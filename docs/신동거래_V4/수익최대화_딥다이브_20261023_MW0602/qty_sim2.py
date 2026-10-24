# -*- coding: utf-8 -*-
"""자본 3,400만 기준 X% 를 낮췄을 때 — 수량 분포와 손익(최소 1계약 강제). 읽기 전용."""
import os, sys, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import qty_sim as Q                                             # noqa: E402  (재생 결과·일별 계획 재사용)
from collections import Counter
DEP, PTV = Q.DEP, Q.PTV
print("| 규칙 | X(3,400만) | 2계약 허용 ATR / 3계약 허용 ATR | 수량 분포 | 21일 합계 | 10/19~ | 최악일 | 최악 거래 |")
print("|---|---|---|---|---|---|---|---|")
for lab in ("v3 현행", "BE3·상한제외"):
    o = Q.res[lab]
    for X in (0.15, 0.12, 0.10, 0.08, 0.06):
        lim = DEP * X
        qd = {d: max(1, min(Q.MAXQ, p["m"], int(lim // (0.6 * p["atr"] * PTV)))) for d, p in Q.plan.items()}
        day, wt = {}, 0.0
        for d, v in o.items():
            for t in v:
                k = t["pt"] * qd[d] * PTV
                day[d] = day.get(d, 0) + k; wt = min(wt, k)
            day.setdefault(d, 0.0)
        m = lambda x: format(x / 1e4, "+,.0f") + "만"
        a2, a3 = lim / (2 * 0.6 * PTV), lim / (3 * 0.6 * PTV)
        print("| %s | %d%% (%s) | ≤%.1f / ≤%.1f | %s | %s | %s | %s | %s |" % (
            lab, X * 100, m(lim).lstrip("+"), a2, a3, dict(sorted(Counter(qd.values()).items())),
            m(sum(day.values())), m(sum(x for d, x in day.items() if d >= "2026-10-19")), m(min(day.values())), m(wt)))
