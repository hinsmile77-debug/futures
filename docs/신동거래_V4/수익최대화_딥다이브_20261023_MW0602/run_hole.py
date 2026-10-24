# -*- coding: utf-8 -*-
"""구멍(MFE<3 → 재난손절) 가드 격자 — 기준선 BE3A. 평가 축: 구멍 손실 · 승자 훼손 · 전/후반 · 스트레스(BE 문턱 4)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim5                                                   # noqa: E402

A_END, B_START, OOS = "2026-10-08", "2026-10-12", "2026-10-19"
BASE_CFG = {"agree": True}


def daily(o):
    return {d: sum(t["pt"] for t in v) for d, v in o.items()}


def met(o, be_at=3.0):
    tr = [t for v in o.values() for t in v]
    hole = [t for t in tr if t["mfe"] < be_at and t["pt"] < 0]
    win = [t for t in tr if ("TR" in t["why"] or "TP" in t["why"])]
    od = daily(o)
    return dict(tot=sum(od.values()), a=sum(v for d, v in od.items() if d <= A_END), b=sum(v for d, v in od.items() if d >= B_START),
                oos=sum(v for d, v in od.items() if d >= OOS), worst_d=min(od.values()), worst_t=min(t["pt"] for t in tr),
                hole_n=len(hole), hole=sum(t["pt"] for t in hole), win_n=len(win), win=sum(t["pt"] for t in win),
                n=len(tr), be=sum(1 for t in tr if "BE" in t["why"]))


B = sim5.run(BASE_CFG); BM = met(B)
S4 = sim5.run(dict(BASE_CFG, be_at=4.0)); SM = met(S4, 4.0)
print("기준선 BE3A: 합계 %+.1f · 구멍 %d건 %+.1f · 승자 %d건 %+.1f · 최악거래 %.1f" % (BM["tot"], BM["hole_n"], BM["hole"], BM["win_n"], BM["win"], BM["worst_t"]))
print("스트레스(BE@4): 합계 %+.1f · 구멍 %d건 %+.1f · 최악거래 %.1f · 최악일 %.1f" % (SM["tot"], SM["hole_n"], SM["hole"], SM["worst_t"], SM["worst_d"]))
print("\n[기준선 구멍 거래]", [(t["day"][5:] if "day" in t else d[5:], t["t"], t["rule"], t["why"], t["mfe"], t["mae"], t["pt"]) for d, v in B.items() for t in v if t["mfe"] < 3 and t["pt"] < 0])
print("[스트레스 구멍 거래]", [(d[5:], t["t"], t["rule"], t["why"], t["mfe"], t["mae"], t["pt"]) for d, v in S4.items() for t in v if t["mfe"] < 4 and t["pt"] < 0])

print("\n| 가드 | 합계 Δ | 전반Δ | 후반Δ | 10/19~Δ | 최악거래 | 최악일 | 구멍(건·pt) | 승자 합 Δ | 거래 | 스트레스 BE@4: 최악거래 · 구멍 · 합계Δ |")
print("|---|---|---|---|---|---|---|---|---|---|---|")


def show(lab, cfg):
    o = sim5.run(dict(BASE_CFG, **cfg)); m = met(o)
    s = met(sim5.run(dict(BASE_CFG, be_at=4.0, **{k: v for k, v in cfg.items() if k not in ("be_at", "be_atr", "be_floor")})), 4.0)
    print("| %s | %+.1f | %+.1f | %+.1f | %+.1f | %.1f | %.1f | %d · %+.1f | %+.1f | %d | %.1f · %+.1f · %+.1f |" % (
        lab, m["tot"] - BM["tot"], m["a"] - BM["a"], m["b"] - BM["b"], m["oos"] - BM["oos"], m["worst_t"], m["worst_d"],
        m["hole_n"], m["hole"], m["win"] - BM["win"], m["n"], s["worst_t"], s["hole"], s["tot"] - SM["tot"]))
    return o


show("기준 BE3A", {})
for m in (0.6, 0.5, 0.4, 0.3):
    if m != 0.6:
        show("본전 전 재난손절 %.1f×ATR" % m, {"cat_mult": m})
for be in (2.0, 2.5):
    show("BE 문턱 %.1f" % be, {"be_at": be})
for r in (0.07, 0.08, 0.10):
    show("BE 문턱 %.2f×ATR(최소 2)" % r, {"be_atr": r, "be_floor": 2.0})
for m in (0.3, 0.4, 0.5):
    show("역행컷 %.1f×ATR 양다리" % m, {"mae_cut": (m, False)})
    show("역행컷 %.1f×ATR 1다리" % m, {"mae_cut": (m, True)})
for mn in (30, 60, 90):
    for mult in (0.3, 0.4):
        show("시간단계 %d분→%.1f×ATR" % (mn, mult), {"tstep": [(mn, mult)]})
show("시간단계 30→0.5 · 60→0.4 · 90→0.3", {"tstep": [(30, 0.5), (60, 0.4), (90, 0.3)]})
for mult in (0.0, 0.3, 0.4):
    for g in (0, 10, 20):
        show("신호소멸 %s · 유예%d분" % ("즉시청산" if mult == 0 else "손절→%.1f×ATR" % mult, g), {"fade": (mult, g)})
show("조합: 신호소멸→0.4 유예10 + 시간 60→0.4", {"fade": (0.4, 10), "tstep": [(60, 0.4)]})
show("조합: 신호소멸→0.3 유예20 + 시간 90→0.3", {"fade": (0.3, 20), "tstep": [(90, 0.3)]})
