# -*- coding: utf-8 -*-
"""월 1,000만원 목표 X — 자본 3,400만 · BE3A(BE3 + R60 누적일관성) · 수량 = min(3, 증거금, X%). 읽기 전용.
21거래일(9/21~10/23) ≈ 한 달. 슬립 = 본전·잠금 청산 1건당 계약당 추가 미끄러짐(pt)."""
import os, sys, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import qty_sim as Q                                             # noqa: E402
import sim4                                                         # noqa: E402
from collections import Counter
DEP, PTV, MAXQ, TARGET = 34_000_000, 50_000, 3, 10_000_000
o = sim4.run({"agree": True})


def run(X, force_min, slip=0.0, scale=1.0):
    day, wt, qd = {}, 0.0, {}
    for d, p in Q.plan.items():
        qx = int(DEP * X // (0.6 * p["atr"] * PTV))
        q = min(MAXQ, p["m"], qx)
        if force_min:
            q = max(1, q)
        qd[d] = q
        for t in o[d]:
            pt = t["pt"] - (slip if "BE" in t["why"] else 0.0)
            pt = pt * scale if pt > 0 else pt          # 할인: 이익만 깎는다(손실은 그대로 — 보수적)
            k = pt * q * PTV
            day[d] = day.get(d, 0) + k; wt = min(wt, k)
        day.setdefault(d, 0.0)
    return sum(day.values()), min(day.values()), wt, qd, day


XS = [x / 100 for x in (0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15)]
for force in (False, True):
    print("\n## %s" % ("최소 1계약 강제(X 수량 0 이어도 1계약)" if force else "X 수량 0 이면 그날 진입 안 함"))
    print("| X | 한도 | 수량 분포 | 21일 합계 | 최악일 | 최악 거래 | 목표 1,000만 |")
    print("|---|---|---|---|---|---|---|")
    for X in XS:
        tot, wd, wt, qd, _ = run(X, force)
        print("| %.1f%% | %.0f만 | %s | %+.0f만 | %+.0f만 | %+.0f만 | %s |" % (
            X * 100, DEP * X / 1e4, dict(sorted(Counter(qd.values()).items())), tot / 1e4, wd / 1e4, wt / 1e4,
            "✅" if tot >= TARGET else "—"))

print("\n## 할인·슬리피지 시나리오별 — 목표 달성에 필요한 최소 X (최소 1계약 강제 · 증거금 상한 함께)")
print("| 시나리오 | 필요 최소 X | 그때 21일 합계 | 수량 분포 | 최악 거래 |")
print("|---|---|---|---|---|")
for lab, slip, scale in (("표본 그대로", 0.0, 1.0), ("본전 슬립 1pt", 1.0, 1.0), ("이익 ×0.7", 0.0, 0.7),
                         ("이익 ×0.5", 0.0, 0.5), ("이익 ×0.5 + 슬립 1pt", 1.0, 0.5), ("이익 ×0.4 + 슬립 1pt", 1.0, 0.4)):
    hit = None
    for X in [x / 1000 for x in range(1, 201)]:
        tot, wd, wt, qd, _ = run(X, True, slip, scale)
        if tot >= TARGET:
            hit = (X, tot, qd, wt); break
    if hit:
        print("| %s | **%.1f%%** (%.0f만) | %+.0f만 | %s | %+.0f만 |" % (lab, hit[0] * 100, DEP * hit[0] / 1e4, hit[1] / 1e4,
              dict(sorted(Counter(hit[2].values()).items())), hit[3] / 1e4))
    else:
        tot, wd, wt, qd, _ = run(0.20, True, slip, scale)
        print("| %s | 증거금 최대(3계약)로도 미달 | %+.0f만 | %s | %+.0f만 |" % (lab, tot / 1e4, dict(sorted(Counter(qd.values()).items())), wt / 1e4))

print("\n## 참고 — 표본 밖(v3 라이브 10/19~10/23, 5일) 몫")
for X in (0.03, 0.05, 0.10, 0.15):
    tot, wd, wt, qd, day = run(X, True)
    print("  X=%.0f%%: 5일 %+.0f만 (일평균 %+.0f만 → 21일 환산 %+.0f만)" % (X * 100, sum(v for d, v in day.items() if d >= "2026-10-19") / 1e4,
          sum(v for d, v in day.items() if d >= "2026-10-19") / 5 / 1e4, sum(v for d, v in day.items() if d >= "2026-10-19") / 5 * 21 / 1e4))
