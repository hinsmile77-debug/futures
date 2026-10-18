# -*- coding: utf-8 -*-
"""첫 거래 뒤 감시 · W60 · CP+FX — 거래를 R1 동방향/역방향으로 분해 (현행 MAIN 대조)."""
import sys, collections
sys.argv = [sys.argv[0]]
import lead_reentry_cf as M
from strategy.shindong import families as F, daily_report as DR
rows = {"현행 MAIN": [], "첫거래뒤 W60": []}
for day in M.EVAL:
    o = DR.load_day(day, M.RAW_DATA_DB, M.FLOW, M.PREMARKET_LEVELS_DB)
    d, L = o["d"], o["L"]; bias = F._r1_bias(d)[1]
    for name, mode in (("현행 MAIN", None), ("첫거래뒤 W60", "any")):
        for i, t in enumerate(M.run_main(d, L, bias, day >= M.V22_FROM, mode, 60) or []):
            rel = "보류" if not bias else ("동방향" if t["side"] == bias else "역방향")
            rows[name].append(dict(t, day=day, bias=bias, rel=rel, n=i + 1))
for name, rs in rows.items():
    print("\n=== %s" % name)
    g = collections.defaultdict(list)
    for r in rs:
        g[(r["src"], r["rel"])].append(r); g[("합계", r["rel"])].append(r)
    for k in sorted(g):
        xs = g[k]; net = sum(x["net"] for x in xs)
        print("  %-6s %-4s n%2d 승%2d 패%2d 순손익 %+7.1f만 평균 %+6.1f SL%d" % (k[0], k[1], len(xs), sum(x["net"] > 0 for x in xs),
              sum(x["net"] <= 0 for x in xs), net / 1e4, net / len(xs) / 1e4, sum(x["why"] == "SL" for x in xs)))
    print("  -- 일자별 R1적중 구분")
    hit = {"2026-10-01": False, "2026-10-16": False}
    for lab, f in (("R1 적중일", lambda r: hit.get(r["day"], True)), ("R1 오판일(10/01·10/16)", lambda r: not hit.get(r["day"], True))):
        for rel in ("동방향", "역방향"):
            xs = [r for r in rs if f(r) and r["rel"] == rel]
            if xs:
                print("   %-18s %s n%2d 승%2d 순손익 %+7.1f만" % (lab, rel, len(xs), sum(x["net"] > 0 for x in xs), sum(x["net"] for x in xs) / 1e4))
    print("  -- 거래")
    for r in rs:
        print("   %s #%d %s→%s %-5s %s %-4s %+6.1f만 %s" % (r["day"][5:], r["n"], r["t"], r["x"], r["src"], r["rel"], r["why"], r["net"] / 1e4, r.get("lead") or ""))
