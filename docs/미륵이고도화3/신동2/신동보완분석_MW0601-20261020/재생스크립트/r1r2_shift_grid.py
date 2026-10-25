# -*- coding: utf-8 -*-
"""신동 v3 R1 판단 시각 × R2 확정 창 시프트 그리드 — 읽기 전용 반사실.

R1 T ∈ 08:59–09:05 (1분) · R2 시작 S ∈ 09:01/03/05/07 (기준 = S−1분, 창 10분)
미래 참조 방지: R2 확정은 R1 결정 뒤 분(≥ T+1)부터만.
엔진은 v3 MAIN(engine.run_day) 그대로, spec 상수만 바꿔 돌린다.
"""
import sys, os, json, sqlite3, datetime as dt
ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, ROOT)
from utils.analysis_db import guard_intraday
guard_intraday("r1r2_shift")
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import engine as E, spec as S, runner as R
from strategy.shindong.calendar import select_flow_product

FLOW_DB = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
OUT = sys.argv[1]
DAYS = sys.argv[2].split(",")

def plus(h, n): return E._plus_min(h, n)

T_LIST = ["08:59"] + [plus("09:00", i) for i in range(0, 6)]
S_LIST = ["09:01", "09:03", "09:05", "09:07"]
ORIG = {k: getattr(S, k) for k in ("PREMARKET_LAST", "CONF_BASE", "CONF_START", "CONF_END")}

frames = {}
for day in DAYS:
    prod, _e, _n = select_flow_product(dt.date.fromisoformat(day))
    c, f, lv = R.load_inputs(day, prod, RAW_DATA_DB, FLOW_DB, PREMARKET_LEVELS_DB)
    if not c or "0850" not in lv:
        print("skip", day, "candles" if not c else "levels"); continue
    frames[day] = (E.DayFrame(c, f), E.prepare_levels(lv))

rows = []
for T in T_LIST:
    for Sx in S_LIST:
        S.PREMARKET_LAST = T
        S.CONF_BASE = plus(Sx, -1)
        S.CONF_START = max(Sx, plus(T, 1))
        S.CONF_END = plus(Sx, 9)
        for day, (d, L) in frames.items():
            res = E.run_day(d, L, "MAIN")
            dec = res["decision"]
            k0 = d.last_at_or_before("09:00"); kT = d.last_at_or_before(max(T, "09:00"))
            kx = d.last_at_or_before("15:05")
            mv_fix = (d.c[kx] - d.c[k0]) if (k0 in d.c and kx in d.c) else None
            mv_dec = (d.c[kx] - d.c[kT]) if (kT in d.c and kx in d.c) else None
            r2 = [t for t in res["trades"] if t.get("rule") == "R2"]
            r3 = [t for t in res["trades"] if t.get("rule") == "R3"]
            rows.append(dict(T=T, S=Sx, day=day, bias=dec.get("bias"), pm_sp=dec.get("pm_sp"),
                             r2=dec.get("r2"), r2_ts=dec.get("r2_ts"),
                             mv_fix=mv_fix, mv_dec=mv_dec,
                             r2_net=sum(E.trade_net(t) for t in r2),
                             r2_n=len(r2), r2_entry=(r2[0]["entry_px"] if r2 else None),
                             r2_leg=[g.get("reason") for g in r2[0]["legs"]] if r2 else None,
                             r3_net=sum(E.trade_net(t) for t in r3), r3_n=len(r3)))
for k, v in ORIG.items():
    setattr(S, k, v)
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("days", len(frames), "rows", len(rows))
