# -*- coding: utf-8 -*-
"""월 1,000만원 목표 X — 자본(인자, 기본 3,000만) · BE3A · 수량 = min(3, 증거금 가능수량, X%). 읽기 전용.
증거금 가능수량을 그 자본으로 다시 계산한다(qty_sim 의 계약당 증거금 추정 그대로)."""
import os, sys, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import qty_sim as Q                                             # noqa: E402  (재생·계약당 증거금 추정 재사용)
import sim4                                                         # noqa: E402
from collections import Counter
DEP = int(sys.argv[1]) if len(sys.argv) > 1 else 30_000_000
PTV, MAXQ, TARGET = 50_000, 3, 10_000_000
rules = {"BE3A(제안)": sim4.run({"agree": True}), "v3 현행(참고)": Q.res["v3 현행"]}
plan = {}
for d in Q.plan:
    Dd, L = Q.sim.frame(d)
    mg = Q.day_px(Dd) * PTV * Q.RATE
    plan[d] = dict(m=int(DEP // mg), atr=Q.plan[d]["atr"], mg=mg)


def run(o, X, force_min=True, slip=0.0, scale=1.0, xcap=True):
    day, wt, qd = {}, 0.0, {}
    for d, p in plan.items():
        q = min(MAXQ, p["m"])
        if xcap:
            q = min(q, int(DEP * X // (0.6 * p["atr"] * PTV)))
        if force_min:
            q = max(1, q)
        qd[d] = q
        for t in o[d]:
            pt = t["pt"] - (slip if "BE" in t["why"] else 0.0) if "why" in t else t["pt"]
            pt = pt * scale if pt > 0 else pt
            k = pt * q * PTV
            day[d] = day.get(d, 0) + k; wt = min(wt, k)
        day.setdefault(d, 0.0)
    return sum(day.values()), min(day.values()), wt, qd, day


m = lambda x: format(x / 1e4, "+,.0f") + "만"
print("자본 %s원 · 증거금 가능수량 분포(최대 3):" % format(DEP, ","), dict(sorted(Counter(min(MAXQ, p["m"]) for p in plan.values()).items())))
print("\n## X 별 (최소 1계약 강제 · 증거금 상한 함께)")
print("| 규칙 | X | 한도 | 수량 분포 | 21일 합계 | 자본 대비 | 최악일 | 최악 거래 | 목표 |")
print("|---|---|---|---|---|---|---|---|---|")
for lab, o in rules.items():
    for X in (0.02, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15):
        tot, wd, wt, qd, _ = run(o, X)
        print("| %s | %d%% | %.0f만 | %s | %s | %+.1f%% | %s | %s | %s |" % (lab, X * 100, DEP * X / 1e4,
              dict(sorted(Counter(qd.values()).items())), m(tot), tot / DEP * 100, m(wd), m(wt), "✅" if tot >= TARGET else "—"))
    tot, wd, wt, qd, _ = run(o, 0, xcap=False)
    print("| %s | 증거금만(X 없음) | - | %s | %s | %+.1f%% | %s | %s | %s |" % (lab, dict(sorted(Counter(qd.values()).items())), m(tot),
          tot / DEP * 100, m(wd), m(wt), "✅" if tot >= TARGET else "—"))

print("\n## BE3A — 할인·슬리피지 시나리오별 목표 달성 최소 X")
print("| 시나리오 | 필요 최소 X | 그때 21일 합계 | 수량 분포 | 최악 거래 |")
print("|---|---|---|---|---|")
o = rules["BE3A(제안)"]
for lab, slip, scale in (("표본 그대로", 0.0, 1.0), ("본전 슬립 1pt", 1.0, 1.0), ("이익 ×0.7", 0.0, 0.7), ("이익 ×0.6 + 슬립 1pt", 1.0, 0.6),
                         ("이익 ×0.5", 0.0, 0.5), ("이익 ×0.5 + 슬립 1pt", 1.0, 0.5)):
    hit = next(((X, r) for X in [x / 1000 for x in range(1, 301)] for r in [run(o, X, True, slip, scale)] if r[0] >= TARGET), None)
    if hit:
        X, r = hit
        print("| %s | **%.1f%%** (%.0f만) | %s | %s | %s |" % (lab, X * 100, DEP * X / 1e4, m(r[0]), dict(sorted(Counter(r[3].values()).items())), m(r[2])))
    else:
        r = run(o, 0, True, slip, scale, xcap=False)
        print("| %s | 증거금 최대로도 미달 | %s | %s | %s |" % (lab, m(r[0]), dict(sorted(Counter(r[3].values()).items())), m(r[2])))
