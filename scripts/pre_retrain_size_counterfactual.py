# -*- coding: utf-8 -*-
"""[MW0602 468차 F-1-v] pre_retrain 배수(×0.6)를 뺐을 때 진입 수량이 바뀌는 건수 — 읽기 전용.

**무엇을 재는가.** `_pre_retrain_done`이 False인 동안 붙는 `[EntryGate] 사이즈 축소 ×0.6`을
품질군 min 합성에서 **제거했을 때** 최종 체결 수량이 달라지는 진입이 몇 건인지 센다.
F-1(전일 EOD 적재로도 제한 해제)이 노출을 얼마나 늘리는지의 **상한 추정**이다.

**왜 필요한가.** 0813 리포트가 사전 규칙을 걸었다 — *"수량이 바뀌는 진입이 10건 이상이면
F-1 단독 적용 금지 → 주간회의 상정(`MAX_CONTRACTS=3`(431차)과 노출 상호작용). 미만이면
즉시 적용 권고."* 그 규칙의 입력을 만드는 스크립트다.

**재구성 규칙** (main.py 431차 품질군 min 합성, `_compose_quality_qty`):

    qty = max(1, round(base × min(품질배수들)))
    품질배수 = {pre_retrain 0.6, meta, tox, exec, hurst 0.5}
    base    = `[Sizer] … → N계약`  (kelly/신뢰도·레짐·안전 배수는 여기 이미 반영돼 있다)

**정직성 규약 — 재구성값이 실제 체결 수량과 다르면 그 건은 세지 않는다.**
로그에 안 찍히는 배수가 있으면(예: `_meta_size_sizing` vs 로그의 `meta=`, 456차 무정보
폴백 중립화) 재구성이 어긋난다. 어긋난 건은 `재구성불가`로 분리 보고하고 카운트에서 뺀다 —
추정치를 실측 옆에 섞지 않는다. 431차(2026-08-05) **이전** 진입은 곱셈 세대라 구조적으로
재구성 불가이며, 그것이 정상이다.

사용:  python scripts/pre_retrain_size_counterfactual.py [--days 20] [--logs logs]
"""
from __future__ import print_function

import argparse
import glob
import io
import os
import re
import sys
from collections import OrderedDict

RE_ENTRY = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.*\[Position\] 진입 (?P<dir>\w+) (?P<qty>\d+)계약")
RE_SIZER = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.*\[Sizer\].*→ (?P<qty>\d+)계약")
RE_MATCH = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.*\[SizerMatch\] sizer=(?P<base>\d+)계약 "
    r"→ actual=(?P<act>\d+)계약.*kelly=(?P<kelly>[\d.]+) meta=(?P<meta>[\d.]+) "
    r"tox=(?P<tox>[\d.]+) exec=(?P<exec>[\d.]+)")
RE_PRE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.*사이즈 축소 ×0\.6")
RE_HURST = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.*\[HurstGate\] 하드차단 대신 사이즈축소.*"
    r"size_mult=(?P<m>[\d.]+)")


def _read(path):
    if not os.path.exists(path):
        return []
    with io.open(path, encoding="utf-8", errors="replace") as f:
        return f.readlines()


def _compose(base, mults):
    """main.py `_compose_quality_qty()`와 같은 식 — 1.0 미만 배수만 min 경쟁."""
    if not base or base <= 0:
        return 0
    ms = [v for v in mults if v is not None and v < 1.0]
    if not ms:
        return base
    return max(1, int(round(base * min(ms))))


def collect(logs_dir, n_days):
    days = sorted({os.path.basename(p)[:8]
                   for p in glob.glob(os.path.join(logs_dir, "*_TRADE.log"))})[-n_days:]
    rows = []
    for d in days:
        trade = _read(os.path.join(logs_dir, "%s_TRADE.log" % d))
        signal = _read(os.path.join(logs_dir, "%s_SIGNAL.log" % d))
        sizer, match, pre, hurst = {}, {}, set(), {}
        for ln in trade:
            m = RE_SIZER.match(ln)
            if m:
                sizer[m.group("ts")] = int(m.group("qty"))
        for ln in signal:
            m = RE_MATCH.match(ln)
            if m:
                match[m.group("ts")] = m.groupdict()
            m = RE_PRE.match(ln)
            if m:
                pre.add(m.group("ts"))
            m = RE_HURST.match(ln)
            if m:
                hurst[m.group("ts")] = float(m.group("m"))
        for ln in trade:
            m = RE_ENTRY.match(ln)
            if not m:
                continue
            ts = m.group("ts")
            mm = match.get(ts)
            rows.append(OrderedDict([
                ("day", d), ("ts", ts), ("actual", int(m.group("qty"))),
                ("base", sizer.get(ts)), ("pre", ts in pre), ("hurst", hurst.get(ts)),
                ("meta", float(mm["meta"]) if mm else None),
                ("tox", float(mm["tox"]) if mm else None),
                ("exec", float(mm["exec"]) if mm else None),
            ]))
    return days, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="pre_retrain ×0.6 제거 카운터팩추얼")
    ap.add_argument("--days", type=int, default=20, help="최근 N거래일 (기본 20)")
    ap.add_argument("--logs", default="logs", help="로그 폴더 (기본 logs)")
    args = ap.parse_args(argv)

    days, rows = collect(args.logs, args.days)
    if not days:
        print("로그 없음: %s" % args.logs)
        return 1

    n_pre = n_ok = n_changed = n_bad = 0
    changed, bad = [], []
    for r in rows:
        if not r["pre"]:
            continue
        n_pre += 1
        others = [r["meta"], r["tox"], r["exec"], r["hurst"]]
        r["recon"] = _compose(r["base"], others + [0.6])
        r["wo_pre"] = _compose(r["base"], others)
        if r["base"] is None or r["recon"] != r["actual"]:
            n_bad += 1
            bad.append(r)
            continue
        n_ok += 1
        if r["wo_pre"] != r["recon"]:
            n_changed += 1
            changed.append(r)

    print("대상 %d거래일: %s ~ %s" % (len(days), days[0], days[-1]))
    print("진입 총 %d건 / ×0.6 적용 %d건" % (len(rows), n_pre))
    print("  재구성 성공(실제 체결과 일치): %d건 · 재구성불가: %d건" % (n_ok, n_bad))
    print("  0.6 제거 시 수량 변화        : %d건" % n_changed)
    if changed:
        print("  총 노출 증가                 : +%d계약"
              % sum(r["wo_pre"] - r["recon"] for r in changed))
        for r in changed:
            print("    %s base=%s meta=%s tox=%s exec=%s hurst=%s : %d → %d계약" % (
                r["ts"], r["base"], r["meta"], r["tox"], r["exec"], r["hurst"],
                r["recon"], r["wo_pre"]))
    if bad:
        print("  재구성불가 상세 (431차 이전 곱셈 세대면 정상):")
        for r in bad[:10]:
            print("    %s actual=%s base=%s recon=%s meta=%s tox=%s exec=%s hurst=%s" % (
                r["ts"], r["actual"], r["base"], r["recon"], r["meta"], r["tox"],
                r["exec"], r["hurst"]))
    print()
    print("판정 기준(0813 리포트 F-1-v): 변화 10건 이상 → 주간회의 상정 / 미만 → 즉시 적용")
    return 0


if __name__ == "__main__":
    sys.exit(main())
