# -*- coding: utf-8 -*-
"""첫 FLOW 거래 전용 역행컷 — 문턱 민감도 · BE 없는 가정(v3+일관성) · 10/23 경로."""
import os, sys, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim5                                                   # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    import run_hole as R                                      # noqa: E402
print("## A. 첫 FLOW 전용 역행컷 — BE3A 기준 / 스트레스 BE@4 / BE 없음(≈v3+일관성)")
print("| 문턱 | BE3A: 합계Δ · 최악거래 · 컷 발동 | BE@4: 합계Δ · 최악거래 · 구멍 | BE 없음: 합계Δ · 최악거래 · 최악일 · 컷 발동 |")
print("|---|---|---|---|")
NB = sim5.run(dict(R.BASE_CFG, be_at=99.0)); NBM = R.met(NB, 99.0)
for m in (0.25, 0.3, 0.35, 0.4, 0.45, 0.5):
    c = {"mae_cut": (m, False), "cut_rule": "FLOW", "cut_as_sl": True}
    o = sim5.run(dict(R.BASE_CFG, **c)); mm = R.met(o)
    s = R.met(sim5.run(dict(R.BASE_CFG, be_at=4.0, **c)), 4.0)
    nb = sim5.run(dict(R.BASE_CFG, be_at=99.0, **c)); nbm = R.met(nb, 99.0)
    fire = lambda oo: sum(1 for v in oo.values() for t in v if t["rule"] == "FLOW" and "SL" in t["why"] and t["mae"] < 0.59 * t["atr"])
    print("| %.2f×ATR | %+.1f · %.1f · %d | %+.1f · %.1f · %+.1f | %+.1f · %.1f · %.1f · %d |" % (
        m, mm["tot"] - R.BM["tot"], mm["worst_t"], fire(o), s["tot"] - R.SM["tot"], s["worst_t"], s["hole"],
        nbm["tot"] - NBM["tot"], nbm["worst_t"], nbm["worst_d"], fire(nb)))
print("BE 없음 기준: 합계 %+.1f · 최악거래 %.1f · 최악일 %.1f" % (NBM["tot"], NBM["worst_t"], NBM["worst_d"]))

print("\n## B. 첫 FLOW 거래 21건 — MFE · MAE/ATR · 결과 (BE3A 기준)")
for d, v in R.B.items():
    t = v[0]
    print("  %s %s %s MFE %4.1f MAE %4.1f (%.2f×ATR) %-6s %+6.2f" % (d[5:], t["t"], "매수" if t["side"] > 0 else "매도", t["mfe"], t["mae"], t["mae"] / t["atr"], t["why"], t["pt"]))

print("\n## C. 10/23 경로 — BE 없음 + FLOW 컷 0.4×ATR (18.3pt)")
from strategy.shindong import engine as E
o = sim5.run(dict(R.BASE_CFG, be_at=99.0, mae_cut=(0.4, False), cut_rule="FLOW", cut_as_sl=True))
print("  ", o["2026-10-23"])
d, L = sim5.sim4.sim.frame("2026-10-23")
e = 826.7
for k in [k for k in d.idx if "09:07" < k <= "10:05" and k in d.h]:
    if d.h[k] - e >= 0.4 * 45.75:
        print("   첫 도달 봉", k, "고가", d.h[k], "종가", d.c[k], "→ 역행", round(d.h[k] - e, 1), "pt"); break
