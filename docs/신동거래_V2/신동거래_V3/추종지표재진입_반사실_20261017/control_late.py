# -*- coding: utf-8 -*-
"""대조군 — 감시 없이 「첫 거래 뒤 재진입은 T 이후」만 둔 FLOWC. 이득이 시간 효과인지 분리한다."""
import sys
sys.argv = [sys.argv[0]]
import lead_reentry_cf as M
from strategy.shindong import families as F, spec as S, daily_report as DR

def run_late(d, L, bias, guard, t_min, halt=True, sig_kind="flowc"):
    fsig, _ = F._flow_signal(d, d.sp, S.FLOWC_K, -1)
    if fsig is None:
        return None
    cat = F._cat_stop_pts(L)
    trades, busy, halted, ctr_n = [], None, False, 0
    for k in d.idx:
        if k < "09:00" or k not in d.c or (busy is not None and k <= busy):
            continue
        if halted or k > S.FLOW_LAST_ENTRY or len(trades) >= S.FLOW_MAX_TRADES:
            continue
        if trades and k < t_min:
            continue
        side = fsig(k)
        if not side:
            continue
        if guard and bias and side == -bias and ctr_n >= S.FLOW_R1_CTR_MAX:
            continue
        t = M.trade(d, side, k, cat, "FLOWC")
        trades.append(t); busy = t["x"] or "99:99"
        if bias and side == -bias:
            ctr_n += 1
        if t["why"] == "SL" and halt:
            halted = True
    return trades

data = {}
for day in M.PRE + M.EVAL:
    o = DR.load_day(day, M.RAW_DATA_DB, M.FLOW, M.PREMARKET_LEVELS_DB)
    if o.get("ok") and o["d"].sp:
        data[day] = (o["d"], o["L"], F._r1_bias(o["d"])[1])
print("FLOWC 재진입 시각 하한 · 손절 시 당일 중단 유지/해제 — 평가 10일 | 사전 6일 | 일별(평가)")
for t_min in ("09:00", "09:30", "10:00", "10:30"):
    for halt in (True, False):
        ev = {d: sum(x["net"] for x in run_late(*data[d][:3], d >= M.V22_FROM, t_min, halt)) for d in M.EVAL}
        pr = {d: sum(x["net"] for x in run_late(*data[d][:3], False, t_min, halt)) for d in M.PRE if d in data}
        print("  %s %-6s %7.1f만 최악일 %7.1f | %7.1f만 | %s" % (t_min, "중단" if halt else "중단해제", sum(ev.values()) / 1e4,
              min(ev.values()) / 1e4, sum(pr.values()) / 1e4, " ".join("%.0f" % (v / 1e4) for v in ev.values())))
