# -*- coding: utf-8 -*-
"""FLOWC(MAIN) 반사실 — A(재진입 제한) · B(신호 소멸 청산). 읽기 전용."""
import sys, os, sqlite3, datetime as dt, json
ROOT = r"C:\Users\pc1\PycharmProjects\futures"
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from strategy.shindong import engine as E, spec as S, families as F, runner as R
from strategy.shindong.calendar import select_flow_product

RAW, FLOW, LV, SD = "data/db/raw_data.db", "data/db/option_flow.db", "data/db/premarket_levels.db", "data/db/shindong.db"


def dv_fn(d):
    sp = d.sp
    if not sp:
        return None
    if S.FLOW_BASE in sp:
        bk = S.FLOW_BASE
    else:
        after = [k for k in sorted(sp) if k > S.FLOW_BASE]
        if not after:
            return None
        bk = after[0]
    base = sp[bk]
    return lambda k: (None if (k not in sp or k < bk) else sp[k] - base)


def run_pos(d, side, t0, stop, trail, tp, dv, b_frac):
    e = d.c[t0]
    tp_px = e + side * tp
    st, mfe, trail_on = stop, 0.0, False
    for k in [k for k in d.idx if t0 < k <= S.TIME_EXIT and k in d.h]:
        h, l = d.h[k], d.l[k]
        if (l <= st) if side > 0 else (h >= st):
            return k, st, ("TR" if trail_on else "SL"), True, e
        if (h >= tp_px) if side > 0 else (l <= tp_px):
            return k, tp_px, "TP", False, e
        mfe = max(mfe, (h - e) if side > 0 else (e - l))
        if mfe >= trail[0]:
            ns = e + side * mfe - side * trail[1]
            if side * (ns - st) > 0:
                st, trail_on = ns, True
        # B: 신호 소멸 — 역방향 신호 강도 = -side*dv (매수면 dv 가 -K 이하였다)
        if b_frac is not None:
            v = dv(k)
            if v is not None and (-side) * v < b_frac * S.FLOWC_K:
                return k, d.c[k], "SD", True, e
    tx = d.last_at_or_before(S.TIME_EXIT)
    return tx, d.c[tx], "TIME", True, e


def run_day(d, L, a_mode=None, a_cool=0, b_frac=None):
    """a_mode: None | 'rearm'(같은 방향은 신호가 한 번 0 으로 돌아온 뒤에만) | 'cool'(a_cool 분 같은 방향 금지)"""
    dv = dv_fn(d)
    if dv is None:
        return None
    sig = lambda k: (0 if dv(k) is None else -1 * (1 if dv(k) >= S.FLOWC_K else (-1 if dv(k) <= -S.FLOWC_K else 0)))
    cat = F._cat_stop_pts(L)
    out, busy, halted = [], None, False
    last_side, last_exit, armed = 0, None, True
    for k in d.idx:
        if k < "09:00" or k not in d.c:
            continue
        s = sig(k)
        if busy is not None and k <= busy:
            continue
        if s == 0:
            armed = True
        if halted or k > S.FLOW_LAST_ENTRY or len(out) >= S.FLOW_MAX_TRADES or not s:
            continue
        if last_side and s == last_side:
            if a_mode == "rearm" and not armed:
                continue
            if a_mode == "cool" and E._plus_min(last_exit, a_cool) > k:
                continue
        stop = (lambda e: e - s * cat)(d.c[k])
        xt, xp, why, mkt, e = run_pos(d, s, k, stop, S.FLOW_TRAIL, S.FLOW_TP, dv, b_frac)
        pts, net = E.leg_net(s, e, xp, mkt)
        out.append(dict(entry=k, side=s, e=e, exit=xt, xp=xp, why=why, pts=pts, net=net))
        busy, last_side, last_exit, armed = xt, s, xt, False
        if why == "SL" and S.FLOW_CAT_STOP_HALT_DAY:
            halted = True
    return out


def dates():
    c = sqlite3.connect(SD)
    return [r[0] for r in c.execute("select distinct trade_date from shindong_day where variant='MAIN' order by 1")]


VARS = [("BASE", dict()),
        ("A_rearm", dict(a_mode="rearm")),
        ("A_cool10", dict(a_mode="cool", a_cool=10)),
        ("A_cool30", dict(a_mode="cool", a_cool=30)),
        ("B_0.5", dict(b_frac=0.5)),
        ("B_0.0", dict(b_frac=0.0)),
        ("B_1.0", dict(b_frac=1.0)),
        ("A_rearm+B_0.5", dict(a_mode="rearm", b_frac=0.5)),
        ("A_cool30+B_0.5", dict(a_mode="cool", a_cool=30, b_frac=0.5))]

if __name__ == "__main__":
    res = {v: {} for v, _ in VARS}
    skipped = []
    for day in dates():
        prod, _x, _n = select_flow_product(dt.date.fromisoformat(day))
        cd, fl, lv = R.load_inputs(day, prod, RAW, FLOW, LV)
        if not cd or "0850" not in lv:
            skipped.append((day, "no candles/levels")); continue
        L = E.prepare_levels(lv)
        d = E.DayFrame(cd, fl)
        for v, kw in VARS:
            t = run_day(d, L, **kw)
            if t is None:
                if v == "BASE": skipped.append((day, "no flow"))
                continue
            res[v][day] = t
    json.dump(res, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
    print("skipped", skipped)
