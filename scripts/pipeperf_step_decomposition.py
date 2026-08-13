# -*- coding: utf-8 -*-
"""[MW0602 468차 G-4] 파이프라인 지연 상승의 STEP 단위 분해 — 읽기 전용.

**무엇을 재는가.** `[PipePerf][DBG] total=NNNms | S0=..ms S1=..ms … S8=..ms`를 파싱해
**시간대별로 단조 증가하는 STEP을 지목**한다. "오늘 느려졌다"는 총량 관측을
"어느 단계가 느려졌다"로 좁히는 것이 목적이다.

**왜 필요한가.** 0812·0813 이틀 연속 세션 기준선 대비 장중 최대 지연이 3배 가까이
올랐다(184→536ms / 191→568ms). 2일 연속이라 "그날 우연"은 배제됐는데 원인 STEP이
미규명이다. NEXT_TODO의 기존 의심("`pred_select` 5~12초 병목(S1) — predictions DB
풀스캔")과 교차 확인할 원자료가 매분 로그에 이미 있다.

**라벨 규약** (main.py 9210-9214 주석과 동일):
    마커는 각 STEP **시작** 지점에 찍힌다. 따라서 구간 `S[i-1]→S[i]`의 소요시간은
    `S[i-1]`에 적힌 STEP의 **본문**이다. `S0`은 STEP1 진입 전 준비 구간.
        S0 준비 · S1 과거예측검증 · S2 SGD온라인 · S3 GBM배치재학습 · S4 피처생성
        S5 멀티호라이즌예측 · S6 앙상블판단 · S7 진입실행 · S8 청산감시

**판정 규약 — 상관 하나로 결론내지 않는다.** 버킷 수가 13개 안팎이라 Spearman 하나로는
약하다. `rho`(단조성) **와** `증가폭`(첫→끝 버킷 중앙값 차) **와** `기여율`(그 STEP이
total 증가분에서 차지하는 몫)을 함께 본다. 셋이 같은 방향을 가리킬 때만 "원인 후보"다.

사용:
    python scripts/pipeperf_step_decomposition.py                 # 최근 3거래일
    python scripts/pipeperf_step_decomposition.py --days 5
    python scripts/pipeperf_step_decomposition.py --date 2026-08-13 --bucket 30
"""
from __future__ import print_function

import argparse
import glob
import io
import math
import os
import re
import sys
from collections import OrderedDict

STEP_LABEL = {
    "S0": "준비(STEP1 진입 전)",
    "S1": "과거예측검증",
    "S2": "SGD온라인학습",
    "S3": "GBM배치재학습",
    "S4": "피처생성",
    "S5": "멀티호라이즌예측",
    "S6": "앙상블진입판단",
    "S7": "진입실행",
    "S8": "청산트리거감시",
}

RE_LINE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} (?P<hh>\d{2}):(?P<mm>\d{2})):\d{2}.*"
    r"\[PipePerf\]\[DBG\](?P<tags>[^|]*?)\s*total=(?P<total>\d+)ms\s*\|\s*(?P<steps>.+?)\s*$")
RE_STEP = re.compile(r"(S\d)=(\d+)ms")

# [273차] S6 세부 구간 — "S6가 원인"에서 "S6의 어느 구간이 원인"까지 좁힌다.
# 매분 INFO로 이미 찍히고 있어(main.py 7021) 추가 계측이 필요 없다.
RE_S6 = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} (?P<hh>\d{2}):(?P<mm>\d{2})):\d{2}.*\[S6Detail\]\s*(?P<steps>.+?)\s*$")
RE_S6_SEG = re.compile(r"([A-Za-z_]+)=(\d+)ms")

S6_LABEL = {
    "ensemble":      "앙상블 합성",
    "checklist_pre": "체크리스트 사전평가",
    "meta_gate":     "MetaGate",
    "gates":         "게이트 체인(Tox·Hurst 등)",
    "imp":           "중요도 갱신",
    "shap":          "SHAP 심사",
    "corr":          "파라미터 상관 스냅샷",
    "dash_ui":       "대시보드 갱신",
    "tail":          "잔여",
}


def _median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return float(s[n // 2]) if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def _ranks(xs):
    """동점은 평균 순위 — 동점을 무시하면 상관이 부풀려진다(460차 선례)."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs, ys):
    """(rho, p근사). 표본이 작으면 p는 참고치일 뿐이다."""
    n = len(xs)
    if n < 4:
        return None, None
    rx, ry = _ranks(xs), _ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    if den == 0:
        return None, None
    rho = num / den
    if abs(rho) >= 1.0:
        return rho, 0.0
    t = rho * math.sqrt((n - 2) / (1 - rho * rho))
    # t분포 양측 p 근사 (정규 근사 — 버킷 수가 10~20이라 보수적으로 참고만)
    p = math.erfc(abs(t) / math.sqrt(2.0))
    return rho, p


def read_day(logs_dir, ymd, bucket_min, keep_retrain, kind="pipe"):
    """하루치 PipePerf(또는 S6Detail) → {bucket: {step: [ms,…]}}, 총건수, 제외건수"""
    line_re, seg_re = (RE_LINE, RE_STEP) if kind == "pipe" else (RE_S6, RE_S6_SEG)
    rows, skipped = [], 0
    for path in sorted(glob.glob(os.path.join(logs_dir, "%s_*.log" % ymd))):
        base = os.path.basename(path).lower()
        if "_system" not in base and "_warn" not in base:
            continue
        try:
            with io.open(path, encoding="utf-8", errors="replace") as f:
                for ln in f:
                    m = line_re.match(ln)
                    if not m:
                        continue
                    tags = m.groupdict().get("tags") or ""
                    if not keep_retrain and ("재학습" in tags or "모델교체" in tags):
                        skipped += 1
                        continue
                    steps = dict((k, int(v)) for k, v in seg_re.findall(m.group("steps")))
                    if not steps:
                        continue
                    minute = int(m.group("hh")) * 60 + int(m.group("mm"))
                    total = int(m.groupdict().get("total") or sum(steps.values()))
                    rows.append((minute, total, steps))
        except (IOError, OSError):
            continue
    buckets = OrderedDict()
    for minute, total, steps in rows:
        b = minute // bucket_min
        d = buckets.setdefault(b, {"total": [], "steps": {}})
        d["total"].append(total)
        for k, v in steps.items():
            d["steps"].setdefault(k, []).append(v)
    return buckets, len(rows), skipped


def analyze_day(ymd, buckets, n_rows, skipped, bucket_min, out,
                labels=None, tag="PipePerf"):
    A = out.append
    labels = labels if labels is not None else STEP_LABEL
    if not buckets:
        A("### %s — %s 로그 없음" % (ymd, tag))
        A("")
        return None
    idx = sorted(buckets)
    tot_med = [_median(buckets[b]["total"]) for b in idx]
    steps = sorted({k for b in idx for k in buckets[b]["steps"]})

    A("### %s — %d사이클 · %d분 버킷 %d개%s" % (
        ymd, n_rows, bucket_min, len(idx),
        (" · 재학습/모델교체 사이클 %d건 제외" % skipped) if skipped else ""))
    A("")
    A("총 지연 중앙값: 첫 버킷 %s → 끝 버킷 %s ms (최대 %s)" % (
        tot_med[0], tot_med[-1], max(x for x in tot_med if x is not None)))
    A("")
    A("| STEP | 설명 | 첫 버킷 | 끝 버킷 | 증가 | 최대 | rho(단조성) | p근사 | 증가 기여율 |")
    A("|---|---|---|---|---|---|---|---|---|")

    tot_delta = (tot_med[-1] or 0) - (tot_med[0] or 0)
    results = []
    for s in steps:
        med = []
        bi = []
        for i, b in enumerate(idx):
            v = _median(buckets[b]["steps"].get(s, []))
            if v is not None:
                med.append(v)
                bi.append(i)
        if len(med) < 4:
            continue
        rho, p = spearman(bi, med)
        delta = med[-1] - med[0]
        share = (delta / tot_delta * 100.0) if tot_delta > 0 else 0.0
        results.append({"step": s, "delta": delta, "rho": rho, "p": p,
                        "first": med[0], "last": med[-1], "max": max(med), "share": share})
    for r in sorted(results, key=lambda r: -r["delta"]):
        A("| `%s` | %s | %.0f | %.0f | %+.0f | %.0f | %s | %s | %s |" % (
            r["step"], labels.get(r["step"], "?"), r["first"], r["last"],
            r["delta"], r["max"],
            ("%+.2f" % r["rho"]) if r["rho"] is not None else "—",
            ("%.3f" % r["p"]) if r["p"] is not None else "—",
            ("%.0f%%" % r["share"]) if tot_delta > 0 else "—"))
    A("")
    return {"ymd": ymd, "tot_delta": tot_delta, "results": results,
            "buckets": buckets, "idx": idx}


def print_series(per_day, cands, out, bucket_min, labels):
    """원인 후보의 **버킷별 원값**을 그대로 보인다.

    **왜 필요한가.** rho는 계단(step)과 폭주(runaway)를 구분하지 못한다 — 하루 중간에
    한 번 뛰고 평평해지는 값도 rho가 +0.9를 넘는다. 실제로 SHAP 심사가 그렇다
    (라벨 100건이 차는 시점에 0→166ms 계단, 이후 버퍼 상한 240에서 포화).
    처방이 갈리므로(계단=구조적 정상 / 폭주=누수) 숫자를 직접 보여준다.
    """
    if not cands:
        return
    A = out.append
    A("### 원인 후보 버킷별 원값 (계단 vs 폭주 구분)")
    A("")
    for s in sorted(cands):
        A("**`%s` %s**" % (s, labels.get(s, "")))
        A("")
        for d in per_day:
            vals = []
            for b in d["idx"]:
                v = _median(d["buckets"][b]["steps"].get(s, []))
                vals.append("%s@%02d:%02d" % (
                    ("%.0f" % v) if v is not None else "—",
                    b * bucket_min // 60, b * bucket_min % 60))
            A("- `%s` %s" % (d["ymd"], " · ".join(vals)))
        A("")
    A("*계단이면 그 시점에 켜지는 조건(버퍼 충족·스케줄)을 찾고, 끝까지 우상향이면 누수를 의심한다.*")
    A("")


def summarize(per_day, out, labels, title):
    """여러 날에서 **반복해서** 증가하는 구간만 원인 후보로 올린다. 반환: 후보 이름 집합."""
    out.append("## %s" % title)
    out.append("")
    if len(per_day) < 2:
        out.append("관측일이 1일뿐이라 '그날 우연'을 배제할 수 없다. `--days 3` 이상으로 다시 볼 것.")
        out.append("")
        return set()
    agg = {}
    for d in per_day:
        for r in d["results"]:
            a = agg.setdefault(r["step"], {"days": 0, "up_days": 0, "delta": [], "rho": []})
            a["days"] += 1
            a["delta"].append(r["delta"])
            if r["rho"] is not None:
                a["rho"].append(r["rho"])
            if r["delta"] > 0:
                a["up_days"] += 1
    out.append("| 구간 | 설명 | 증가한 날 | 평균 증가 | 평균 rho | 판정 |")
    out.append("|---|---|---|---|---|---|")
    cands = set()
    for s in sorted(agg, key=lambda s: -(sum(agg[s]["delta"]) / max(1, len(agg[s]["delta"])))):
        a = agg[s]
        avg_d = sum(a["delta"]) / len(a["delta"])
        avg_r = (sum(a["rho"]) / len(a["rho"])) if a["rho"] else None
        # 세 축(모든 날 증가 · 평균 증가>0 · 단조성)이 같은 방향일 때만 후보로 올린다 —
        # 상관 하나로 결론내지 않는다.
        cand = (a["up_days"] == a["days"] and avg_d > 0 and avg_r is not None and avg_r >= 0.5)
        if cand:
            cands.add(s)
        out.append("| `%s` | %s | %d/%d | %+.0fms | %s | %s |" % (
            s, labels.get(s, "?"), a["up_days"], a["days"], avg_d,
            ("%+.2f" % avg_r) if avg_r is not None else "—",
            "**원인 후보**" if cand else "—"))
    out.append("")
    out.append("*판정: 관측한 모든 날에서 증가 + 평균 rho ≥ +0.50 인 구간만 후보로 올린다.*")
    out.append("")
    return cands


def main(argv=None):
    ap = argparse.ArgumentParser(description="PipePerf STEP 단위 분해")
    ap.add_argument("--logs", default="logs")
    ap.add_argument("--days", type=int, default=3, help="최근 N거래일 (기본 3)")
    ap.add_argument("--date", default=None, help="특정일만 (YYYY-MM-DD 또는 YYYYMMDD)")
    ap.add_argument("--bucket", type=int, default=30, help="버킷 크기(분, 기본 30)")
    ap.add_argument("--keep-retrain", action="store_true",
                    help="재학습/모델교체 태그가 붙은 사이클도 포함(기본 제외)")
    args = ap.parse_args(argv)

    if args.date:
        days = [args.date.replace("-", "")]
    else:
        days = sorted({os.path.basename(p)[:8]
                       for p in glob.glob(os.path.join(args.logs, "*_SYSTEM.log"))})[-args.days:]
    if not days:
        print("PipePerf 로그를 찾지 못했다: %s" % args.logs)
        return 1

    out = []
    out.append("# PipePerf STEP 분해 — %s" % ", ".join(days))
    out.append("")
    out.append("> 라벨 규약: 마커는 STEP **시작**에 찍힌다 → `Sn` = STEP n **본문** 소요시간, "
               "`S0` = STEP1 진입 전 준비. (main.py 9210-9214)")
    out.append("")
    per_day = []
    for ymd in days:
        buckets, n_rows, skipped = read_day(args.logs, ymd, args.bucket, args.keep_retrain)
        r = analyze_day(ymd, buckets, n_rows, skipped, args.bucket, out)
        if r:
            per_day.append(r)

    cands = summarize(per_day, out, STEP_LABEL, "종합 — 원인 후보 (STEP 단위)")
    print_series(per_day, cands, out, args.bucket, STEP_LABEL)

    # ── S6가 후보로 잡히면 273차 `[S6Detail]`로 한 단계 더 좁힌다 ──────────────
    # "S6가 원인"까지는 처방을 못 고른다. 어느 하위 구간인지까지 가야
    # 인덱스/캐시/호출빈도 중 무엇을 손댈지 결정할 수 있다.
    if "S6" in cands:
        out.append("## S6 세부 분해 (273차 `[S6Detail]`)")
        out.append("")
        s6_days = []
        for ymd in days:
            b6, n6, sk6 = read_day(args.logs, ymd, args.bucket, True, kind="s6")
            r6 = analyze_day(ymd, b6, n6, sk6, args.bucket, out,
                             labels=S6_LABEL, tag="S6Detail")
            if r6:
                s6_days.append(r6)
        c6 = summarize(s6_days, out, S6_LABEL, "종합 — S6 내부 원인 후보")
        print_series(s6_days, c6, out, args.bucket, S6_LABEL)

    # 교차 확인용 — NEXT_TODO의 기존 의심(S1 = predictions DB 풀스캔)
    for name in ("predictions.db", "trades.db", "raw_data.db"):
        p = os.path.join("data", "db", name)
        if os.path.exists(p):
            out.append("- `%s` %.0fMB" % (p, os.path.getsize(p) / 1024.0 / 1024.0))
    out.append("")
    out.append("> S1(과거예측검증)이 후보로 잡히면 `predictions.db` 인덱스/아카이빙을 먼저 본다 — "
               "NEXT_TODO 기존 항목 \"`pred_select` 5~12초 병목(S1) — 풀스캔 의심\"과 같은 지점이다.")

    text = "\n".join(out)
    if sys.version_info[0] >= 3:
        sys.stdout.write(text + "\n")
    else:
        sys.stdout.write(text.encode("utf-8") + b"\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
