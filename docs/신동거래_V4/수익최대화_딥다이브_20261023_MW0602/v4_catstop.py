# -*- coding: utf-8 -*-
"""V4 에서 재난손절(0.6×ATR14)이 걸리는 경우 — ① 21일 V4 재생의 실제 발동 ② R60 거래 역행 분포 ③ 1분봉 급변(컷 건너뛰기) 빈도. 읽기 전용."""
import os, sys, sqlite3, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim6                                                   # noqa: E402
from strategy.shindong import families as F, spec as S, engine as E   # noqa: E402

# ① V4 재생 — 거래별 사유·MFE·MAE(÷ATR)
o = {}
sim6.sim4.F._run_signal = sim6.sim4.rs
try:
    for day in sim6.sim4.sim.days():
        D, L = sim6.sim4.sim.frame(day); atr = L["0850"].get("atr14") or 33.3
        sim6.sim4.F._run_position = sim6.make_pos(D, {"stopx": ("mkt", "stop"), "_atr": atr}, day)
        try:
            r = F.run_family_day(D, L, "hybr60")
        finally:
            sim6.sim4.F._run_position = sim6.sim4.ORIG_RP
        o[day] = (atr, r["trades"], D)
finally:
    sim6.sim4.F._run_signal = sim6.sim4.ORIG_RS
print("## ① V4 21일 재생 — 손절(SL) 청산 거래")
rows = []
for day, (atr, trs, D) in o.items():
    for t in trs:
        why = t["_why"]; e = t["entry_px"]; side = t["side"]
        ks = [k for k in D.idx if t["entry_ts"] < k <= t["exit_ts"] and k in D.h]
        mae = max((side * (e - (D.l[k] if side > 0 else D.h[k])) for k in ks), default=0)
        rows.append(dict(day=day, t=t["entry_ts"], rule=t["rule"], why=why, mfe=t["_mfe"], mae=mae, atr=atr,
                         pt=E.trade_net(t) / 2 / S.PT_VALUE_KRW, cat=abs(e - (e - side * 0.6 * atr))))
for x in rows:
    if "SL" in x["why"]:
        kind = "재난손절 0.6×ATR" if x["mae"] >= 0.59 * x["atr"] else "첫 FLOW 역행컷 0.4×ATR"
        print("  %s %s %-4s %-18s MFE %4.1f MAE %4.1f (%.2f×ATR) %+6.2fpt" % (x["day"][5:], x["t"], x["rule"], kind, x["mfe"], x["mae"], x["mae"] / x["atr"], x["pt"]))
r60 = [x for x in rows if x["rule"] == "R60"]; fl = [x for x in rows if x["rule"] == "FLOW"]
print("\n## ② 규칙별 — 본전 전(MFE<3) 최대 역행 ÷ ATR")
for lab, xs in (("첫 FLOW", fl), ("R60", r60)):
    pre = [x for x in xs if x["mfe"] < 3]
    vals = sorted(x["mae"] / x["atr"] for x in pre)
    print("  %s %d건 중 MFE<3 %d건 · 역행/ATR %s · ≥0.4 %d건 · ≥0.6 %d건" % (lab, len(xs), len(pre), [round(v, 2) for v in vals],
          sum(v >= 0.4 for v in vals), sum(v >= 0.59 for v in vals)))

# ③ 1분봉 급변 — 한 봉 범위가 0.2×ATR 이상(0.4 컷을 건너뛰어 0.6 에 닿을 수 있는 크기)인 봉 비율 · 6월 이후 전 봉
c = sqlite3.connect("file:data/db/premarket_levels.db?mode=ro", uri=True)
atr = dict(c.execute("select date, atr14 from premarket_levels where stage='0850' and atr14 is not null").fetchall())
rc = sqlite3.connect("file:data/db/raw_data.db?mode=ro", uri=True)
tot = cnt2 = cnt3 = 0; days = set(); big = []
for ts, h, l in rc.execute("select ts, high, low from raw_candles where substr(ts,12,5) between '09:00' and '10:00' order by ts"):
    d = ts[:10]
    if d not in atr: continue
    rng = (h - l) / atr[d]; tot += 1
    if rng >= 0.2: cnt2 += 1; days.add(d); big.append((d, ts[11:16], round(h - l, 1), round(rng, 2)))
    if rng >= 0.3: cnt3 += 1
print("\n## ③ 09:00~10:00(첫 FLOW 거래 시간대) 1분봉 %d개 · ATR 있는 %d일" % (tot, len({t for t in atr})))
print("  한 봉 범위 ≥ 0.2×ATR: %d봉 (%.3f%%) · %d일 · ≥ 0.3×ATR: %d봉" % (cnt2, 100.0 * cnt2 / tot, len(days), cnt3))
print("  사례:", big[:12])
