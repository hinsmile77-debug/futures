# -*- coding: utf-8 -*-
"""ATR14 결측 시 폴백 최적성 — ① 결측 빈도 ② 후보별 오차(실제 ATR 대비) ③ 21일 전부 결측 가정 스트레스 손익. 읽기 전용."""
import os, sys, sqlite3, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim5                                                   # noqa: E402
from strategy.shindong import families as F, engine as E, spec as S   # noqa: E402
c = sqlite3.connect("file:data/db/premarket_levels.db?mode=ro", uri=True)
rows = c.execute("select date, atr14 from premarket_levels where stage='0850' order by date").fetchall()
miss = [d for d, a in rows if a is None]
print("08:50 맥점 행 %d일 (%s ~ %s) · ATR14 결측 %d일: %s" % (len(rows), rows[0][0], rows[-1][0], len(miss), miss))
hist = [(d, a) for d, a in rows if a is not None]
# ② 후보 — 그날 ATR 이 비었다고 치고 그 전 데이터로만 만든 값
cand = {"고정 20pt": lambda i: 20.0, "고정 30pt": lambda i: 30.0, "직전 ATR14 이월": lambda i: hist[i - 1][1],
        "직전 20일 ATR14 중앙": lambda i: st.median(a for _, a in hist[max(0, i - 20):i]),
        "직전 60일 ATR14 최대": lambda i: max(a for _, a in hist[max(0, i - 60):i])}
print("\n| 폴백 후보 | 평균 |오차| pt | 과소(폴백<실제) 비율 | 최대 과소 pt | 재난손절 폭 오차 0.6× 평균 |")
print("|---|---|---|---|---|")
for nm, f in cand.items():
    errs = [(f(i) - hist[i][1]) for i in range(5, len(hist))]
    print("| %s | %.2f | %.0f%% | %.1f | %.2f |" % (nm, st.mean(abs(e) for e in errs), 100 * sum(e < 0 for e in errs) / len(errs),
          -min(errs), 0.6 * st.mean(abs(e) for e in errs)))
print("실제 ATR14 범위(%d일): 최소 %.1f · 중앙 %.1f · 최대 %.1f" % (len(hist), min(a for _, a in hist), st.median(a for _, a in hist), max(a for _, a in hist)))

# ③ 스트레스 — 21일 전부 ATR14 결측이라 치고 폴백 값을 손절·컷에 쓴다(BE3A + 첫 FLOW 컷 0.4)
ORIG_RUN = sim5.run
idx = {d: i for i, (d, _) in enumerate(hist)}
def run_fb(cfg, fb):
    out = {}
    sim5.sim4.F._run_signal = sim5.sim4.rs
    try:
        for day in sim5.sim4.sim.days():
            D, L = sim5.sim4.sim.frame(day)
            atr = fb(idx[day]) if fb else (L["0850"].get("atr14") or 33.3)
            sim5.sim4.F._run_position = sim5.make_pos(D, dict(cfg, _atr=atr))
            try:
                res = F.run_family_day(D, L, "hybr60")
            finally:
                sim5.sim4.F._run_position = sim5.sim4.ORIG_RP
            out[day] = [E.trade_net(t) / 2 / S.PT_VALUE_KRW for t in res["trades"]]
    finally:
        sim5.sim4.F._run_signal = sim5.sim4.ORIG_RS
    return out
CFG = {"agree": True, "mae_cut": (0.4, False), "cut_rule": "FLOW", "cut_as_sl": True}
print("\n| 21일 전부 폴백 가정 | 합계 pt | 최악 거래 | 최악일 |")
print("|---|---|---|---|")
for nm, f in [("실제 ATR14(기준)", None)] + list(cand.items()):
    o = run_fb(CFG, f)
    print("| %s | %+.1f | %.1f | %.1f |" % (nm, sum(sum(v) for v in o.values()), min(x for v in o.values() for x in v), min(sum(v) for v in o.values())))
