# -*- coding: utf-8 -*-
"""구멍 가드 추가 변형 — 컷을 손절로 취급(방향 금지·재진입 억제) · 규칙별(첫 FLOW / R60) 분리 · 승자 사전 역행 분포."""
import os, sys, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim5                                                   # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    import run_hole as R                                      # noqa: E402  (기준선·met·show 재사용)
print("| 가드 | 합계 Δ | 전반Δ | 후반Δ | 10/19~Δ | 최악거래 | 최악일 | 구멍(건·pt) | 승자 합 Δ | 거래 | 스트레스 BE@4: 최악거래 · 구멍 · 합계Δ |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
R.show("기준 BE3A", {})
for m in (0.4, 0.5):
    R.show("역행컷 %.1f×ATR 양다리 · 컷=손절(방향금지)" % m, {"mae_cut": (m, False), "cut_as_sl": True})
    R.show("역행컷 %.1f×ATR · 첫 FLOW 거래만" % m, {"mae_cut": (m, False), "cut_rule": "FLOW"})
    R.show("역행컷 %.1f×ATR · 첫 FLOW 만 · 컷=손절" % m, {"mae_cut": (m, False), "cut_rule": "FLOW", "cut_as_sl": True})
    R.show("역행컷 %.1f×ATR · R60 만" % m, {"mae_cut": (m, False), "cut_rule": "R60"})
    R.show("역행컷 %.1f×ATR · R60 만 · 컷=손절" % m, {"mae_cut": (m, False), "cut_rule": "R60", "cut_as_sl": True})
R.show("본전 전 0.4×ATR · 첫 FLOW 만(=컷 0.4 FLOW 컷=손절)", {"mae_cut": (0.4, False), "cut_rule": "FLOW", "cut_as_sl": True})

# 승자(트레일·익절)가 6pt 유리에 닿기 전 겪은 최대 역행 — 규칙별 분포 (가드가 왜 지는지)
tr = [(d, t) for d, v in R.B.items() for t in v]
import statistics as st
for rule in ("FLOW", "R60"):
    w = [t for d, t in tr if t["rule"] == rule and ("TR" in t["why"] or "TP" in t["why"])]
    l = [t for d, t in tr if t["rule"] == rule and t["pt"] < 0 and t["mfe"] < 3]
    mae_w = sorted(t["mae"] / t["atr"] for t in w)
    print("\n%s 승자 %d건: 사전 최대역행/ATR 중앙 %.2f · p75 %.2f · p90 %.2f · 최대 %.2f | 구멍 %d건 역행/ATR %s" % (
        rule, len(w), st.median(mae_w), mae_w[int(.75 * (len(mae_w) - 1))], mae_w[int(.9 * (len(mae_w) - 1))], max(mae_w),
        len(l), [round(t["mae"] / t["atr"], 2) for t in l]))
    for thr in (0.3, 0.4, 0.5):
        print("   역행 ≥ %.1f×ATR 를 겪은 승자: %d/%d (합 %+.1fpt)" % (thr, sum(x >= thr for x in mae_w), len(w), sum(t["pt"] for t in w if t["mae"] / t["atr"] >= thr)))
