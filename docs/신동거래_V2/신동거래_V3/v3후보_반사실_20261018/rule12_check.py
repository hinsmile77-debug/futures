# -*- coding: utf-8 -*-
"""v3 에 ①(주도 지표 선택) · ②(손절 방향 금지의 덮어쓰기 규칙) 반영 여부와 이득.
① v3(FLOWR60 = CP 60분 변화만) vs v3+①(CP·FX 상관 주도 선택 · 0.3 미만 관망)
② 금지 방식: last(마지막 손절 방향만 · 덮어쓰기 = 엔진 same) / sticky(손절 난 방향 누적 — 양방향 손절되면 사실상 당일 중단)"""
import sys, collections
sys.argv = [sys.argv[0]]
import v3_candidates as V
M = V.M
from strategy.shindong import families as F, spec as S, daily_report as DR

def run(d, L, bias, day, after, ban, route="first"):
    fsig, _ = F._flow_signal(d, d.sp, S.FLOWC_K, -1)
    if after == "R60":
        r = F._roll_signal(d.sp, S.FLOWR_WIN_MIN, S.FLOWR_K, -1); asig = lambda k: (r(k), "CP*")
    else:
        mon = M.Monitor(d, 60); asig = lambda k: mon(k)[:2]
    g = day >= M.V22_FROM
    cat = F._cat_stop_pts(L)
    trades, busy, blocked, ctr_n, log = [], None, set(), 0, []
    for k in d.idx:
        if k < "09:00" or k not in d.c or (busy is not None and k <= busy):
            continue
        if k > S.FLOW_LAST_ENTRY or len(trades) >= S.FLOW_MAX_TRADES:
            continue
        if route == "flowc" or not trades:
            side, lead = fsig(k), "FLOWC"
            if side and bias and side == -bias and ctr_n >= 1 and g:
                continue
        else:
            side, lead = asig(k)
        if not side or side in blocked:
            continue
        t = M.trade(d, side, k, cat, lead, lead); trades.append(t); busy = t["x"] or "99:99"
        if bias and side == -bias:
            ctr_n += 1
        if t["why"] == "SL":
            if ban == "last":
                blocked = {side}
            else:
                blocked.add(side)
            log.append((t["x"], side, len(trades)))
    return trades, log

data = {}
for day in M.PRE + M.EVAL:
    o = DR.load_day(day, M.RAW_DATA_DB, M.FLOW, M.PREMARKET_LEVELS_DB)
    if o.get("ok") and o["d"].sp and o["d"].fx:
        data[day] = (o["d"], o["L"], F._r1_bias(o["d"])[1])
cfg = [("v3 (R60·last)", "R60", "last", "first"), ("v3+① (LEAD·last)", "LEAD", "last", "first"),
       ("v3 (R60·sticky)", "R60", "sticky", "first"), ("v3+① (LEAD·sticky)", "LEAD", "sticky", "first"),
       ("V22S (FLOWC·last)", None, "last", "flowc"), ("V22S (FLOWC·sticky)", None, "sticky", "flowc")]
res = {}
for name, after, ban, route in cfg:
    res[name] = {day: run(*data[day], day, after or "R60", ban, route) for day in data}
print("%-22s %8s %8s %8s %6s | 하루 손절≥2회 / 금지 전환 발생 / 3번째 거래 손절" % ("규칙", "평가10일", "사전6일", "16일", "최악일"))
for name, *_ in cfg:
    e = sum(sum(t["net"] for t in res[name][d][0]) for d in M.EVAL)
    p = sum(sum(t["net"] for t in res[name][d][0]) for d in M.PRE if d in data)
    worst = min(sum(t["net"] for t in res[name][d][0]) for d in data)
    two = [d[5:] for d in data if len(res[name][d][1]) >= 2]
    sw = [d[5:] for d in data if any(res[name][d][1][i][1] != res[name][d][1][i - 1][1] for i in range(1, len(res[name][d][1])))]
    third = [d[5:] for d in data if any(x[2] == 3 for x in res[name][d][1])]
    print("%-22s %8.1f %8.1f %8.1f %6.1f | %s / %s / %s" % (name, e / 1e4, p / 1e4, (e + p) / 1e4, worst / 1e4, two or "-", sw or "-", third or "-"))
print("\n[① 차이가 난 날의 거래] v3 vs v3+①")
for day in data:
    a = [(t["t"], t["side"], round(t["net"] / 1e4, 1)) for t in res["v3 (R60·last)"][day][0]]
    b = [(t["t"], t["side"], round(t["net"] / 1e4, 1)) for t in res["v3+① (LEAD·last)"][day][0]]
    if a != b:
        print(" ", day[5:])
        for nm in ("v3 (R60·last)", "v3+① (LEAD·last)"):
            print("    %-18s" % nm, [(t["t"], t["x"], t["side"], t["lead"], t["why"], round(t["net"] / 1e4, 1)) for t in res[nm][day][0]])
# ① 의 관망(상관 <0.3) 이 R60 신호를 막은 분 / 방향을 바꾼 분 — 2·3번째 진입 구간에서
print("\n[① 이 FLOWR60 신호를 바꾼 빈도 — 10:00~14:50 분 단위, 16일]")
cnt = collections.Counter()
for day, (d, L, b) in data.items():
    r = F._roll_signal(d.sp, 60, S.FLOWR_K, -1); mon = M.Monitor(d, 60)
    for k in d.idx:
        if "10:00" <= k <= "14:50" and k in d.c:
            s1 = r(k); s2, lead, _ = mon(k)
            key = ("R60신호" if s1 else "R60무") + "/" + ("LEAD신호" if s2 else "LEAD무")
            if s1 and s2 and s1 != s2:
                key = "방향 반대"
            elif s1 and s2:
                key = "같은 방향(" + lead + ")"
            cnt[key] += 1
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    print("  %-22s %5d분" % (k, v))
