# -*- coding: utf-8 -*-
"""FLOWC 손절·익절 비대칭 딥다이브 — 읽기 전용 반사실 격자."""
import sys, os, json, itertools, datetime as dt
ROOT = r"C:\Users\pc1\PycharmProjects\futures"
sys.path.insert(0, ROOT); os.chdir(ROOT)
from strategy.shindong import engine as E, spec as S, runner as R
from strategy.shindong.calendar import select_flow_product
import sqlite3

RAW, FLOW, LV, SD = "data/db/raw_data.db", "data/db/option_flow.db", "data/db/premarket_levels.db", "data/db/shindong.db"
IS_END = "2026-09-30"          # v2 설계(6일 격자) 구간 끝 — 이후는 설계 뒤 표본(OOS)


def dv_fn(d):
    sp = d.sp
    bk = S.FLOW_BASE if S.FLOW_BASE in sp else ([k for k in sorted(sp) if k > S.FLOW_BASE] or [None])[0]
    if bk is None:
        return None
    base = sp[bk]
    return lambda k: (None if (k not in sp or k < bk) else sp[k] - base)


def run_pos(d, side, t0, stop, tp, trail, be, tstop):
    """be=(trigger, lock): MFE≥trigger 면 손절 = 진입가 + side*lock.  tstop=(분, mfe임계): 그 분 수 경과 시 MFE<임계면 종가 청산."""
    e = d.c[t0]
    tp_px = (e + side * tp) if tp else None
    st = stop
    mfe, mae, trail_on, n = 0.0, 0.0, False, 0
    be_on = False
    t_mfe = t0
    for k in [k for k in d.idx if t0 < k <= S.TIME_EXIT and k in d.h]:
        n += 1
        h, l = d.h[k], d.l[k]
        if st is not None and ((l <= st) if side > 0 else (h >= st)):
            mae = max(mae, (e - l) if side > 0 else (h - e))
            # 본전 이동으로 올라간 손절은 'BE' — 재난 손절(SL)이 아니므로 당일 중단을 걸지 않는다
            why = "TR" if trail_on else ("BE" if be_on else "SL")
            return dict(exit=k, xp=st, why=why, mkt=True, e=e, mfe=mfe, mae=mae, t_mfe=t_mfe)
        if tp_px is not None and ((h >= tp_px) if side > 0 else (l <= tp_px)):
            return dict(exit=k, xp=tp_px, why="TP", mkt=False, e=e, mfe=max(mfe, tp), mae=mae, t_mfe=k)
        fav = (h - e) if side > 0 else (e - l)
        if fav > mfe:
            mfe, t_mfe = fav, k
        mae = max(mae, (e - l) if side > 0 else (h - e))
        if trail and mfe >= trail[0]:
            ns = e + side * mfe - side * trail[1]
            if st is None or side * (ns - st) > 0:
                st, trail_on = ns, True
        if be and mfe >= be[0]:
            ns = e + side * be[1]
            if st is None or side * (ns - st) > 0:
                st = ns
                be_on = True
        if tstop and n >= tstop[0] and mfe < tstop[1]:
            return dict(exit=k, xp=d.c[k], why="TS", mkt=True, e=e, mfe=mfe, mae=mae, t_mfe=t_mfe)
    tx = d.last_at_or_before(S.TIME_EXIT)
    return dict(exit=tx, xp=d.c[tx], why="TIME", mkt=True, e=e, mfe=mfe, mae=mae, t_mfe=t_mfe)


def run_day(d, atr, stop_atr=0.6, stop_pt=None, tp=12.0, trail=(6.0, 4.0), be=None, tstop=None, halt=True):
    dv = dv_fn(d)
    if dv is None:
        return None
    if stop_pt is not None:
        cat = stop_pt
    elif stop_atr is not None:
        cat = stop_atr * atr if atr else S.FLOW_CAT_STOP_FALLBACK_PT
    else:
        cat = None
    out, busy, halted = [], None, False
    for k in d.idx:
        if k < "09:00" or k not in d.c:
            continue
        if busy is not None and k <= busy:
            continue
        v = dv(k)
        s = 0 if v is None else -1 * (1 if v >= S.FLOWC_K else (-1 if v <= -S.FLOWC_K else 0))
        if halted or k > S.FLOW_LAST_ENTRY or len(out) >= S.FLOW_MAX_TRADES or not s:
            continue
        e = d.c[k]
        r = run_pos(d, s, k, (e - s * cat) if cat else None, tp, trail, be, tstop)
        r["pts"], r["net"] = E.leg_net(s, e, r["xp"], r["mkt"])
        r.update(entry=k, side=s, cat=cat)
        out.append(r)
        busy = r["exit"]
        if halt and r["why"] == "SL":
            halted = True
    return out


def load_days():
    c = sqlite3.connect(SD)
    days = [r[0] for r in c.execute("select distinct trade_date from shindong_day where variant='MAIN' order by 1")]
    out = []
    for day in days:
        prod, _x, _n = select_flow_product(dt.date.fromisoformat(day))
        cd, fl, lv = R.load_inputs(day, prod, RAW, FLOW, LV)
        L = E.prepare_levels(lv)
        atr = L["0850"].get("atr14")
        out.append((day, E.DayFrame(cd, fl), atr))
    return out


def summarize(days, kw):
    tr_all, daynet = [], {}
    for day, d, atr in days:
        t = run_day(d, atr, **kw) or []
        for x in t:
            x["day"] = day
        tr_all += t
        daynet[day] = sum(x["net"] for x in t)
    is_ = sum(v for k, v in daynet.items() if k <= IS_END)
    oos = sum(v for k, v in daynet.items() if k > IS_END)
    worst_tr = min((x["net"] for x in tr_all), default=0)
    return dict(n=len(tr_all), tot=sum(daynet.values()), is_=is_, oos=oos,
                worst_day=min(daynet.values()), worst_tr=worst_tr,
                drop_best=sum(daynet.values()) - max(daynet.values()),
                win=sum(1 for x in tr_all if x["net"] > 0) / max(1, len(tr_all)),
                sl=sum(1 for x in tr_all if x["why"] == "SL"),
                neg_days=sum(1 for v in daynet.values() if v < 0), daynet=daynet, trades=tr_all)


if __name__ == "__main__":
    days = load_days()
    outp = sys.argv[1]
    print("ATR14", [(d, round(a, 2) if a else a) for d, _, a in days])
    # 1) BASE 거래 MAE/MFE
    base = summarize(days, {})
    print("\n[1] BASE 거래별 MAE/MFE")
    print("day        entry side  e        exit  why   pts    MFE    MAE  t_mfe  cat")
    for x in base["trades"]:
        print("%s %s %+d %8.2f %s %-4s %6.2f %6.2f %6.2f %s %5.1f" % (
            x["day"], x["entry"], x["side"], x["e"], x["exit"], x["why"], x["pts"], x["mfe"], x["mae"], x["t_mfe"], x["cat"]))
    # 2) 격자
    grid = []
    stops = [("atr", a) for a in (None, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8)] + [("pt", p) for p in (5, 8, 10, 12, 15)]
    tps = [8.0, 10.0, 12.0, 15.0, 20.0, None]
    trails = [(6.0, 4.0), (4.0, 3.0), (5.0, 3.0), (4.0, 2.0), (3.0, 2.0), (8.0, 4.0), (6.0, 3.0), (8.0, 6.0)]
    for (sk, sv), tp, tr in itertools.product(stops, tps, trails):
        kw = dict(tp=tp, trail=tr)
        if sk == "atr":
            kw["stop_atr"] = sv
        else:
            kw["stop_pt"] = sv
        s = summarize(days, kw)
        grid.append(dict(stop="%s%s" % (sk, sv), tp=tp, trail=tr, **{k: v for k, v in s.items() if k not in ("trades",)}))
    # 3) 본전 이동 · 시간 손절 (현행 손절·익절·트레일 유지)
    extra = []
    for be in [(2.0, 0.0), (3.0, 0.0), (4.0, 0.0), (3.0, 1.0), (4.0, 1.0), (5.0, 1.0)]:
        s = summarize(days, dict(be=be)); extra.append(dict(name="BE%s" % (be,), **{k: v for k, v in s.items() if k != "trades"}))
    for ts in [(20, 2.0), (30, 2.0), (30, 3.0), (45, 3.0), (60, 3.0), (60, 4.0), (90, 4.0)]:
        s = summarize(days, dict(tstop=ts)); extra.append(dict(name="TS%s" % (ts,), **{k: v for k, v in s.items() if k != "trades"}))
    for be, ts in [((3.0, 0.0), (60, 3.0)), ((4.0, 1.0), (45, 3.0)), ((3.0, 0.0), (30, 2.0))]:
        s = summarize(days, dict(be=be, tstop=ts)); extra.append(dict(name="BE%s+TS%s" % (be, ts), **{k: v for k, v in s.items() if k != "trades"}))
    json.dump(dict(base={k: v for k, v in base.items()}, grid=grid, extra=extra), open(outp, "w", encoding="utf-8"),
              ensure_ascii=False, default=str)
    print("grid", len(grid))
