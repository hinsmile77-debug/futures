# -*- coding: utf-8 -*-
"""자본 3,400만 · 한 거래 최대손실 X% · 증거금 연동 — 일별 실주문 수량과 손익 재생. 읽기 전용.
수량 = min(최대허용 3, 증거금 가능수량, X% 수량).
  X% 수량 = floor(자본 × X ÷ (0.6 × ATR14 × 5만))  (0 이면 진입 안 함 — 최소 1을 강제하지 않는 안과 강제 안을 함께 본다)
  증거금 가능수량 = floor(예탁금 ÷ 계약당 증거금), 계약당 증거금 ≈ 시가 × 5만 × 증거금률
  증거금률 = 10/23 로그 실측(계약당 ≈877만, 08:45 장시작 기준가) 에서 역산 — ⚠ 추정(거래소가 바꿀 수 있다)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim4, sim                                                        # noqa: E402
from strategy.shindong import families as F, engine as E, spec as S     # noqa: E402
PTV, MAXQ = 50_000, 3
DEP = 34_000_000
d23, _ = sim.frame("2026-10-23")
REF = d23.o[min(k for k in d23.idx if k >= "08:45" and k in d23.o)]     # 10/23 장시작 기준가
RATE = 8_770_000 / (REF * PTV)


def day_px(d):
    k = min(k for k in d.idx if k >= "08:45" and k in d.o)
    return d.o[k]


rules = {"v3 현행": None, "BE3·상한제외": {}, "BE3+누적일관성": {"agree": True}}
res = {}
for lab, cfg in rules.items():
    if cfg is None:
        o = {}
        for day in sim.days():
            Dd, L = sim.frame(day)
            r = F.run_family_day(Dd, L, "hybr60")
            o[day] = [dict(pt=E.trade_net(t) / 2 / S.PT_VALUE_KRW) for t in r["trades"]]
        res[lab] = o
    else:
        res[lab] = sim4.run(cfg)

print("증거금률 추정 %.1f%% (10/23 기준가 %.1f · 계약당 877만)" % (RATE * 100, REF))
print("\n| 날짜 | 시가 | ATR14 | 계약당 증거금(추정) | 증거금 수량 | X15% 수량(3,400만) | X15% 수량(1,500만) | **실주문(3,400만·X15)** |")
print("|---|---|---|---|---|---|---|---|")
plan = {}
for day in sim.days():
    Dd, L = sim.frame(day)
    atr = L["0850"].get("atr14") or 33.3
    px = day_px(Dd)
    mg = px * PTV * RATE
    q_m = int(DEP // mg)
    q_x34 = int(DEP * 0.15 // (0.6 * atr * PTV))
    q_x15 = int(15_000_000 * 0.15 // (0.6 * atr * PTV))
    q = min(MAXQ, q_m, q_x34)
    plan[day] = dict(m=q_m, x34=q_x34, x15=q_x15, q=q, atr=atr)
    print("| %s | %.1f | %.1f | %.0f만 | %d | %d | %d | **%d** |" % (day[5:], px, atr, mg / 1e4, q_m, q_x34, q_x15, q))
from collections import Counter
print("\n실주문 수량 분포(3,400만·X15·증거금):", dict(Counter(p["q"] for p in plan.values())))
print("증거금만(현재 규칙):", dict(Counter(min(MAXQ, p["m"]) for p in plan.values())))

print("\n| 규칙 | 수량안 | 21일 합계 | 자본 3,400만 대비 | 10/19~ | 최악일 | 최악 거래 |")
print("|---|---|---|---|---|---|---|")
schemes = {"현재(증거금·최대3)": lambda p: min(MAXQ, p["m"]),
           "증거금 + X15%(3,400만)": lambda p: min(MAXQ, p["m"], p["x34"]),
           "증거금 + X15%(1,500만 위험자본)": lambda p: max(1, min(MAXQ, p["m"], p["x15"])),
           "고정 2": lambda p: 2}
for lab, o in res.items():
    for sn, f in schemes.items():
        day, wt = {}, 0.0
        for d, v in o.items():
            q = f(plan[d])
            for t in v:
                k = t["pt"] * q * PTV
                day[d] = day.get(d, 0) + k; wt = min(wt, k)
            day.setdefault(d, 0.0)
        m = lambda x: format(x / 1e4, "+,.0f") + "만"
        print("| %s | %s | %s | %+.1f%% | %s | %s | %s |" % (lab, sn, m(sum(day.values())), sum(day.values()) / DEP * 100,
              m(sum(x for d, x in day.items() if d >= "2026-10-19")), m(min(day.values())), m(wt)))
