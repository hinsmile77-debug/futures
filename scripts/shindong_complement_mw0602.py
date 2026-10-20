# -*- coding: utf-8 -*-
"""[MW0601 699차] 신동 보완 판정 — MW0601 신동 MAIN(v3) 이 MW0602 신동 MAIN(v3 HYBR60)을 보완하는가.

사전등록: `strategy/shindong/spec.py` 「MW0602 보완 판정」 절 ·
          `docs/신동거래/신동_개정_v3_TR44승격_MW0601-20261020.md` §4.
🔴 판정 기준은 spec 에서 읽는다 — 여기서 값을 바꾸지 말 것.

무엇을 재나
-----------
같은 거래일의 두 MAIN 일손익(가상 2계약, 원)을 50:50 으로 섞은 B 와 MW0602 MAIN 단독 H 를 비교한다.
    보완 유효 = B 최악일 > H 최악일 **그리고** B 평균/표준편차 ≥ H 평균/표준편차
대조(표시만 — 판정 아님): MW0602 FLOWR60 섀도 · MW0601 SHADOW_X4NFA · MW0601 (MAIN+X4NFA)/2.

원천
----
· MW0601 쪽: `shindong.db` 의 v3 행(라이브 기록). `--mw0601 replay` 면 이 PC 엔진으로 다시 돌린다(v3 이전 날짜 참고용).
· MW0602 쪽: **이 PC 의 DB 로 MW0602 엔진을 재생한 값**이다 — MW0602 의 실제 기록이 아니다.
  `origin/dev` 를 임시 워크트리로 꺼내(`git worktree add --detach`) 그 브랜치의 `strategy/shindong/runner.compute`
  를 자식 프로세스로 돌리고, 끝나면 워크트리를 지운다. 두 PC 의 수집(흐름·맥점·봉)이 다르면 값이 다를 수 있다
  (2026-10-20 실측: MW0602 v3 제안서 수치와 6일 대조 — 일치 3일 · 0.5만원 이내 3일).
  리포트 머리에 dev 커밋 sha 와 「재생」 표기를 남긴다(계측 4원칙 ④ — 폴백·출처 가시화).

🔴 장후 전용 — `raw_data.db` 를 날짜마다 읽는다(456차 `guard_intraday`). 읽기 전용(DB 쓰기 없음).

사용:
    python scripts/shindong_complement_mw0602.py                         # v3 채점 시작 ~ 오늘
    python scripts/shindong_complement_mw0602.py --from 2026-09-21 --mw0601 replay   # v3 이전 참고(판정 아님)
    python scripts/shindong_complement_mw0602.py --out docs/신동거래/보완판정/보완판정_MW0601_YYYYMMDD.md
"""
import argparse
import datetime as _dt
import json
import math
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.shindong import spec  # noqa: E402

MW0602_VARIANTS = ("MAIN", "SHADOW_FLOWR60")
MW0601_VARIANTS = ("MAIN", "SHADOW_X4NFA")


# ── 순수 함수 ────────────────────────────────────────────────────────────
def mean_sd(xs):
    """(평균, 표준편차(표본), 평균/표준편차). n<2 또는 sd=0 이면 비율은 None(미측정 ≠ 0)."""
    xs = list(xs)
    if not xs:
        return None, None, None
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, None, None
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))
    return m, sd, (m / sd if sd > 0 else None)


def mdd(xs):
    c = p = m = 0.0
    for x in xs:
        c += x
        p = max(p, c)
        m = min(m, c - p)
    return m


def corr(a, b):
    if len(a) < 2:
        return None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def judge(h, x, min_days=None):
    """h, x = 같은 날짜 순서의 일손익 목록. → dict(verdict, ...).

    verdict: 대기 · 미측정 · 보완 유효 · 부분 · 보완 무효. 사전등록 기준은 spec 에서만 읽는다.
    """
    min_days = spec.COMPLEMENT_JUDGE_AFTER_DAYS if min_days is None else min_days
    b = [(p + q) / 2.0 for p, q in zip(h, x)]
    _, _, rh = mean_sd(h)
    _, _, rb = mean_sd(b)
    out = dict(n=len(b), blend=b, worst_h=min(h) if h else None, worst_b=min(b) if b else None,
               ratio_h=rh, ratio_b=rb, corr=corr(h, x))
    if len(b) < min_days:
        out["verdict"] = "대기"
        return out
    if rh is None or rb is None:
        out["verdict"] = "미측정"           # 표준편차 0 — 비율을 정의할 수 없다
        return out
    c1 = out["worst_b"] > out["worst_h"]
    c2 = rb >= rh
    out.update(c_worst=c1, c_ratio=c2,
               verdict="보완 유효" if (c1 and c2) else ("부분" if (c1 or c2) else "보완 무효"))
    return out


# ── 원천 ────────────────────────────────────────────────────────────────
def trade_dates(raw_db, since, until):
    con = sqlite3.connect("file:%s?mode=ro" % raw_db.replace("\\", "/"), uri=True)
    try:
        rows = con.execute("SELECT DISTINCT substr(ts,1,10) FROM raw_candles WHERE ts>=? AND ts<?",
                           (since, (_dt.date.fromisoformat(until) + _dt.timedelta(days=1)).isoformat()))
        return sorted(r[0] for r in rows)
    finally:
        con.close()


def mw0601_from_db(sd_db, dates, version=None):
    """→ {variant: {date: net_krw}}. 그날 판정 행(shindong_day)이 없으면 그 날짜는 빠진다(미측정)."""
    version = version or spec.SPEC_VERSION
    out = {v: {} for v in MW0601_VARIANTS}
    if not os.path.exists(sd_db):
        return out
    con = sqlite3.connect("file:%s?mode=ro" % sd_db.replace("\\", "/"), uri=True)
    try:
        for v in MW0601_VARIANTS:
            for (d,) in con.execute("SELECT trade_date FROM shindong_day WHERE variant=? AND spec_version=?",
                                    (v, version)):
                if d in dates:
                    out[v][d] = 0.0
            for d, net in con.execute(
                    "SELECT trade_date, SUM(net_krw) FROM shindong_trades WHERE variant=? AND spec_version=? "
                    "AND status='CLOSED' GROUP BY trade_date", (v, version)):
                if d in out[v]:
                    out[v][d] = float(net or 0.0)
    finally:
        con.close()
    return out


def mw0601_replay(dates, raw_db, flow_db, levels_db):
    from strategy.shindong import engine, runner
    out = {v: {} for v in MW0601_VARIANTS}
    for d in dates:
        r = runner.compute(d, raw_db, flow_db, levels_db, live=False)
        for v in MW0601_VARIANTS:
            out[v][d] = sum(engine.trade_net(t) for t in r["results"][v]["trades"] if t["status"] == "CLOSED")
    return out


_CHILD = r"""
import sys, json
wt, db_dir, dates, variants = sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4].split(",")
sys.path.insert(0, wt)
import os
from strategy.shindong import runner, spec
P = [os.path.join(db_dir, x) for x in ("raw_data.db", "option_flow.db", "premarket_levels.db")]
out = {"spec_version": spec.SPEC_VERSION, "main_family": getattr(spec, "MAIN_FAMILY", None), "nets": {}}
for d in dates:
    r = runner.compute(d, *P, live=False)
    row = {}
    for v in variants:
        res = r["results"].get(v)
        if res is None:
            continue
        row[v] = sum(sum(g.get("net", 0.0) for g in t["legs"] if not g.get("open", True)) for t in res["trades"])
    out["nets"][d] = row
print("@@JSON@@" + json.dumps(out))
"""


def mw0602_replay(dates, db_dir, dev_ref="origin/dev", fetch=False):
    """→ ({variant: {date: net}}, meta). 임시 워크트리는 성공·실패와 무관하게 지운다."""
    if fetch:
        subprocess.run(["git", "-C", ROOT, "fetch", "-q", "origin"], check=False)
    sha = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", dev_ref], capture_output=True,
                         text=True).stdout.strip()
    if not sha:
        raise SystemExit("dev 참조 %s 를 찾을 수 없다 — `git fetch origin` 후 다시" % dev_ref)
    tmp = tempfile.mkdtemp(prefix="sd_mw0602_")
    wt = os.path.join(tmp, "wt")
    try:
        subprocess.run(["git", "-C", ROOT, "worktree", "add", "-q", "--detach", wt, dev_ref], check=True)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, "-I", "-c", _CHILD, wt, db_dir, ",".join(dates),
                            ",".join(MW0602_VARIANTS)], capture_output=True, text=True,
                           encoding="utf-8", env=env, cwd=tmp)
        line = [x for x in (p.stdout or "").splitlines() if x.startswith("@@JSON@@")]
        if p.returncode != 0 or not line:
            raise SystemExit("MW0602 재생 실패(rc=%s):\n%s" % (p.returncode, (p.stderr or "")[-2000:]))
        res = json.loads(line[-1][len("@@JSON@@"):])
    finally:
        subprocess.run(["git", "-C", ROOT, "worktree", "remove", "--force", wt], check=False,
                       capture_output=True)
        subprocess.run(["git", "-C", ROOT, "worktree", "prune"], check=False)
        shutil.rmtree(tmp, ignore_errors=True)
    nets = {v: {} for v in MW0602_VARIANTS}
    for d, row in res["nets"].items():
        for v, x in row.items():
            nets[v][d] = float(x)
    return nets, dict(sha=sha, ref=dev_ref, spec_version=res["spec_version"], main_family=res["main_family"])


# ── 리포트 ──────────────────────────────────────────────────────────────
def _man(x):
    return "—" if x is None else "%+.1f만" % (x / 1e4)


def _r(x):
    return "—" if x is None else "%.2f" % x


def build(h_map, w_map, meta, since, until, src0601, judged=True):
    lines = []
    w = lines.append
    H = h_map["MAIN"]
    dates = sorted(d for d in H if d in w_map["MAIN"])
    miss = sorted(set(H) ^ set(w_map["MAIN"]))
    w("# [MW0601] 신동 보완 판정 — MW0601 MAIN vs MW0602 MAIN(%s)" % (meta.get("main_family") or "?").upper())
    w("")
    w("> 생성 %s · 창 %s–%s · 사전등록 `%s` 「MW0602 보완 판정」 · 판정 %d거래일 뒤" % (
        _dt.datetime.now().strftime("%Y-%m-%d %H:%M"), since, until, spec.SPEC_VERSION,
        spec.COMPLEMENT_JUDGE_AFTER_DAYS))
    w("> MW0601 원천: **%s** · MW0602 원천: **이 PC DB 로 재생**(`%s` @ `%s`, 규격 `%s`) — MW0602 실기록이 아니다." % (
        "shindong.db v3 라이브 기록" if src0601 == "db" else "이 PC 엔진 재생(참고 — 판정 아님)",
        meta.get("ref"), meta.get("sha"), meta.get("spec_version")))
    w("> 손익은 가상 2계약(원). B = (MW0602 MAIN + 대상)/2 — 노출을 같게 맞춘 혼합.")
    if miss:
        w("> ⚠ 한쪽만 측정된 날 **%d일** 제외: %s" % (len(miss), ", ".join(miss)))
    w("")
    hs = [H[d] for d in dates]
    cand = [("MW0601 MAIN(v3) — **판정 대상**", w_map["MAIN"], True),
            ("MW0601 SHADOW_X4NFA (표시)", w_map["SHADOW_X4NFA"], False),
            ("MW0601 (MAIN+X4NFA)/2 (표시)", {d: (w_map["MAIN"][d] + w_map["SHADOW_X4NFA"].get(d, 0.0)) / 2.0
                                              for d in w_map["MAIN"]}, False),
            ("MW0602 SHADOW_FLOWR60 (표시)", h_map.get("SHADOW_FLOWR60", {}), False)]
    w("## 1. 요약 (%d거래일)" % len(dates))
    w("")
    mh, sh, rh = mean_sd(hs)
    w("MW0602 MAIN 단독: 합 %s · 최악일 %s · MDD %s · 평균/표준편차 %s" % (
        _man(sum(hs)), _man(min(hs) if hs else None), _man(mdd(hs)), _r(rh)))
    w("")
    w("| 대상 | 단독 합 | 상관 | MW0602 손실일 합 | B 합 | B 최악일 | B MDD | B 평균/표준편차 | 판정 |")
    w("|---|---|---|---|---|---|---|---|---|")
    main_j = None
    for name, m, is_main in cand:
        if not all(d in m for d in dates):
            w("| %s | 미측정 | — | — | — | — | — | — | — |" % name)
            continue
        xs = [m[d] for d in dates]
        j = judge(hs, xs)
        if is_main:
            main_j = j
        loss = sum(x for x, y in zip(xs, hs) if y < 0)
        b = j["blend"]
        w("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            name, _man(sum(xs)), _r(j["corr"]), _man(loss), _man(sum(b)), _man(j["worst_b"]),
            _man(mdd(b)), _r(j["ratio_b"]),
            ("**%s**" % j["verdict"]) if (is_main and judged) else "표시만"))
    w("")
    if main_j is not None and judged:
        w("- 판정: **%s** — 기준: B 최악일 > MW0602 단독 최악일(%s vs %s) **그리고** "
          "B 평균/표준편차 ≥ 단독(%s vs %s). %d/%d 거래일." % (
              main_j["verdict"], _man(main_j["worst_b"]), _man(main_j["worst_h"]),
              _r(main_j["ratio_b"]), _r(main_j["ratio_h"]), main_j["n"], spec.COMPLEMENT_JUDGE_AFTER_DAYS))
    elif not judged:
        w("- ⚠ **참고 실행** — v3 채점 시작(%s) 이전 날짜 또는 재생 원천이 섞였다. 판정을 내지 않는다." %
          spec.COMPLEMENT_SCORING_START)
    w("- 판정은 관찰이다 — 자동 조치 없음(절대원칙 §6). 규격 변경은 사전등록 개정으로만.")
    w("")
    w("## 2. 일별 (만원)")
    w("")
    w("| 날짜 | MW0602 MAIN | MW0602 FLOWR60 | MW0601 MAIN | MW0601 X4NFA | B(MAIN 50:50) |")
    w("|---|---|---|---|---|---|")
    for d in dates:
        f = h_map.get("SHADOW_FLOWR60", {}).get(d)
        x = w_map["SHADOW_X4NFA"].get(d)
        w("| %s | %s | %s | %s | %s | %s |" % (d, _man(H[d]), _man(f), _man(w_map["MAIN"][d]), _man(x),
                                               _man((H[d] + w_map["MAIN"][d]) / 2.0)))
    return "\n".join(lines), main_j


def main(argv=None):
    from utils.analysis_db import guard_intraday
    guard_intraday("shindong_complement_mw0602")
    from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, SHINDONG_DB, WEEKLY_OPTION_FLOW_DB
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="since", default=spec.COMPLEMENT_SCORING_START)
    ap.add_argument("--to", dest="until", default=_dt.date.today().isoformat())
    ap.add_argument("--mw0601", choices=("db", "replay"), default="db")
    ap.add_argument("--dev-ref", default="origin/dev")
    ap.add_argument("--fetch", action="store_true", help="재생 전에 git fetch origin")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    flow = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
    dates = trade_dates(RAW_DATA_DB, a.since, a.until)
    if not dates:
        print("거래일 없음 — %s–%s 봉이 없다(미측정)" % (a.since, a.until))
        return 0
    if a.mw0601 == "db":
        w_map = mw0601_from_db(SHINDONG_DB, set(dates))
    else:
        w_map = mw0601_replay(dates, RAW_DATA_DB, flow, PREMARKET_LEVELS_DB)
    want = sorted(set(w_map["MAIN"]))
    if not want:
        print("MW0601 v3 기록 없음(%s 이후) — 미측정. 참고 실행은 --mw0601 replay" % a.since)
        return 0
    h_map, meta = mw0602_replay(want, os.path.dirname(RAW_DATA_DB), a.dev_ref, a.fetch)
    judged = a.mw0601 == "db" and a.since >= spec.COMPLEMENT_SCORING_START
    txt, j = build(h_map, w_map, meta, a.since, a.until, a.mw0601, judged=judged)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(txt + "\n")
        print("저장: %s" % a.out)
    else:
        print(txt)
    if j is not None and judged:
        print("[ShindongComplement] 판정 %s · %d/%d일 · MW0602 dev %s" % (
            j["verdict"], j["n"], spec.COMPLEMENT_JUDGE_AFTER_DAYS, meta["sha"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
