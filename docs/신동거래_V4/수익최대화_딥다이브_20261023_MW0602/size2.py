# -*- coding: utf-8 -*-
"""후보별 원화 환산 — 수량안 × 규칙안. X% 규칙: 계약수 = floor(자본×X ÷ (0.6×ATR14×5만)), 1~2. 읽기 전용."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim4                                                   # noqa: E402
CAP, PTV = 15_000_000, 50_000


def qty(atr, mode):
    if mode == "1": return 1
    if mode == "2": return 2
    x = float(mode[1:]) / 100.0
    return max(1, min(2, int(CAP * x // (0.6 * atr * PTV))))


rules = [("v3 현행(라이브)", None), ("BE3·상한제외", {}), ("BE3·상한제외 + 누적일관성", {"agree": True})]
print("| 규칙 | 수량 | 21일 합계 | 수익률(1,500만) | 10/19~ | 최악일 | 최악 거래 | 최대 보유역행 노출 | 2계약 일수 |")
print("|---|---|---|---|---|---|---|---|---|")
import sim                                                    # noqa: E402
for lab, cfg in rules:
    if cfg is None:
        o = {}
        from strategy.shindong import families as F, engine as E, spec as S
        for d in sim.days():
            Dd, L = sim.frame(d)
            r = F.run_family_day(Dd, L, "hybr60")
            atr = L["0850"].get("atr14") or 33.3
            # 보유 역행(MAE) 은 엔진 결과에 없어 노출 칸은 생략
            o[d] = [dict(pt=E.trade_net(t) / 2 / S.PT_VALUE_KRW, atr=atr, mae=None) for t in r["trades"]]
    else:
        o = sim4.run(cfg)
    for mode in ("1", "2", "X12", "X15", "X18"):
        day, wt, risk, two = {}, 0, 0, set()
        for d, v in o.items():
            for t in v:
                q = qty(t["atr"], mode)
                if q == 2: two.add(d)
                k = t["pt"] * q * PTV
                day[d] = day.get(d, 0) + k; wt = min(wt, k)
                if t.get("mae") is not None: risk = max(risk, t["mae"] * q * PTV)
            day.setdefault(d, 0)
        oos = sum(x for d, x in day.items() if d >= "2026-10-19")
        m = lambda x: format(x / 1e4, "+,.0f") + "만"
        print("| %s | %s | %s | %+.1f%% | %s | %s | %s | %s | %d/%d |" % (
            lab, {"1": "고정 1", "2": "고정 2"}.get(mode, "X=" + mode[1:] + "%"), m(sum(day.values())),
            sum(day.values()) / CAP * 100, m(oos), m(min(day.values())), m(wt),
            ("%.0f만 (%.1f%%)" % (risk / 1e4, risk / CAP * 100)) if risk else "-", len(two), len(day)))
