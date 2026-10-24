# -*- coding: utf-8 -*-
"""「MFE<3 → 재난손절」 구멍 가드 딥다이브 — BE3A 기준선 위. 읽기 전용(DB 미기록).

sim4 의 위치 시뮬레이터를 본전 전(pre-BE) 구간 가드로 확장한다. cfg 추가 키:
  be_at      본전이동 MFE 문턱(기본 3.0) · be_atr  → be_at = max(floor, be_atr×ATR)
  cat_mult   본전 전 재난손절 폭 ATR 배수(기본 0.6 = 현행)
  mae_cut    (m, half)  MAE ≥ m×ATR 이고 MFE<be_at 이면 청산. half=True 면 1다리만
  tstep      [(min, mult), ...] 진입 뒤 min 분이 지나도 MFE<be_at 이면 손절 = 진입가 ∓ mult×ATR 로 당긴다
  fade       (mult, grace)  진입 신호(첫 거래 = FLOWC 누적 · 이후 = R60)가 중립으로 돌아오고 grace 분 지나도
             MFE<be_at 이면 손절 = 진입가 ∓ mult×ATR (mult=0 이면 즉시 종가 청산)
  agree      sim4 와 같다(기준선 BE3A)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim4                                                   # noqa: E402
from strategy.shindong import engine as E, spec as S, families as F   # noqa: E402

ORIG_MAKE_POS = sim4.make_pos


def _leg(dd, side, e, t_from, st0, trail, tp, cfg, atr, sig, leg_no):
    be_at = cfg.get("be_at", 3.0)
    if cfg.get("be_atr"):
        be_at = max(cfg.get("be_floor", 0.0), cfg["be_atr"] * atr)
    tp_px = (e + side * tp) if tp else None
    st = e - side * cfg.get("cat_mult", 0.6) * atr if st0 is not None else None
    mfe = mae = 0.0
    trail_on = be = False
    fade_t = None
    bars = [k for k in dd.idx if t_from < k <= S.TIME_EXIT and k in dd.h]
    t0m = int(t_from[:2]) * 60 + int(t_from[3:])
    for k in bars:
        h, l = dd.h[k], dd.l[k]
        if st is not None and ((l <= st) if side > 0 else (h >= st)):
            return k, st, ("TR" if trail_on else ("BE" if be else "SL")), True, mfe, mae
        if tp_px is not None and ((h >= tp_px) if side > 0 else (l <= tp_px)):
            return k, tp_px, "TP", False, mfe, mae
        mfe = max(mfe, (h - e) if side > 0 else (e - l))
        mae = max(mae, (e - l) if side > 0 else (h - e))
        pre = (not be) and (not trail_on) and mfe < be_at
        if pre and cfg.get("mae_cut") and (cfg.get("cut_rule") is None or cfg["cut_rule"] == ("FLOW" if t_from < "10:00" else "R60")):
            m, half = cfg["mae_cut"]
            if mae >= m * atr and (not half or leg_no == 1):
                return k, dd.c[k], ("SL" if cfg.get("cut_as_sl") else "CUT"), True, mfe, mae
        if pre and cfg.get("tstep"):
            held = int(k[:2]) * 60 + int(k[3:]) - t0m
            for mn, mult in cfg["tstep"]:
                if held >= mn:
                    ns = e - side * mult * atr
                    if st is None or side * (ns - st) > 0:
                        st = ns
        if pre and cfg.get("fade") and sig is not None:
            mult, grace = cfg["fade"]
            if sig(k) == 0 and fade_t is None:
                fade_t = int(k[:2]) * 60 + int(k[3:])
            if fade_t is not None and int(k[:2]) * 60 + int(k[3:]) - fade_t >= grace:
                if mult <= 0:
                    return k, dd.c[k], "FADE", True, mfe, mae
                ns = e - side * mult * atr
                if side * (ns - st) > 0:
                    st = ns
        if trail is not None and mfe >= trail[0]:
            ns = (e + side * mfe) - side * trail[1]
            if st is None or side * (ns - st) > 0:
                st, trail_on = ns, True
        if not trail_on and mfe >= be_at and side * (e - st) > 0:
            st, be = e, True
    tx = dd.last_at_or_before(S.TIME_EXIT)
    return tx, dd.c[tx], "TIME", True, mfe, mae


def make_pos(d, cfg):
    cum, _ = F._flow_signal(d, d.sp, S.FLOWC_K, -1)
    r60 = F._roll_signal(d.sp, S.FLOWR_WIN_MIN, S.FLOWR_K, -1)
    atr = cfg["_atr"]

    def pos(dd, side, t0, stop, trail, tp):
        e = dd.c[t0]
        if cfg.get("agree") and t0 >= "10:00" and cum is not None and cum(t0) == -side:
            return sim4._skip(side, t0, t0)
        sig = cum if t0 < "10:00" else r60
        legs, info = [], []
        for n in (1, 2):
            ts, px, why, mkt, mfe, mae = _leg(dd, side, e, t0, stop, trail, tp, cfg, atr, sig, n)
            pts, net = E.leg_net(side, e, px, mkt)
            legs.append(dict(leg=n, tp=(e + side * tp) if tp else None, open=False, ts=ts, px=px, mkt=mkt, pts=pts,
                             net=net, reason=(("TP1" if n == 1 else "TP2") if why == "TP" else why)))
            info.append((ts, why, mfe, mae))
        whys = [i[1] for i in info]
        return dict(side=side, entry_ts=t0, entry_px=e, stop_init=stop, t1=legs[0]["tp"], t2=legs[1]["tp"], legs=legs,
                    status="CLOSED", exit_ts=max(i[0] for i in info), stop_now=None,
                    _be=all(w == "BE" for w in whys), _why="/".join(sorted(set(whys))),
                    _mfe=max(i[2] for i in info), _mae=max(i[3] for i in info))
    return pos


def run(cfg):
    """sim4.run 을 빌려 쓰되 make_pos 만 바꾼다. ATR 은 날마다 cfg['_atr'] 로 넣는다."""
    out = {}
    sim4.F._run_signal = sim4.rs
    try:
        for day in sim4.sim.days():
            D, L = sim4.sim.frame(day)
            atr = L["0850"].get("atr14") or 33.3
            c = dict(cfg, _atr=atr)
            sim4.F._run_position = make_pos(D, c)
            try:
                res = F.run_family_day(D, L, "hybr60")
            finally:
                sim4.F._run_position = sim4.ORIG_RP
            out[day] = [dict(rule=t["rule"], side=t["side"], t=t["entry_ts"], x=t["exit_ts"], why=t["_why"],
                             mfe=round(t["_mfe"], 1), mae=round(t["_mae"], 1), atr=round(atr, 1),
                             pt=round(E.trade_net(t) / 2 / S.PT_VALUE_KRW, 2)) for t in res["trades"]]
    finally:
        sim4.F._run_signal = sim4.ORIG_RS
        sim4.F._run_position = sim4.ORIG_RP
    return out
