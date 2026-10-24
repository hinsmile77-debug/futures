# -*- coding: utf-8 -*-
"""본전·트레일 스톱의 「달아난 체결」 재확인·재시도 흐름 — BE3A(+첫 FLOW 컷 0.4) 위. 읽기 전용(DB 미기록).

1분봉으로 틱 슬립을 볼 수 없어 근사한다: 스톱이 걸린 봉의 종가가 스톱가보다 band(1pt) 넘게 불리한 쪽에서 끝나면
「달아난 체결」로 본다. 대상은 본전(BE)·트레일(TR) 스톱만 — 재난손절(SL)·역행컷은 즉시 시장가 그대로.

cfg["stopx"]:
  ("mkt", fill)    현행 시장가 — 달아난 봉의 체결가 가정 fill ∈ {"stop"(스톱가) · "mid"(스톱과 종가 중간) · "close"(종가)}
  ("retry", band)  지정가 = 스톱 ∓ band. 달아난 봉에서는 미체결 → 이후 매분: 고(저)가가 지정가에 닿으면 지정가 체결 ·
                   종가가 진입가보다 유리해지면 청산 취소(스톱 재무장) · 재난손절/15:05 는 그대로
  ("close",)       종가 확인형 — 스톱에 닿아도 종가가 스톱 밖일 때만 종가 청산
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim4                                                   # noqa: E402
import sim5                                                   # noqa: E402
from strategy.shindong import engine as E, spec as S, families as F   # noqa: E402

EV = []      # 달아난 체결 사건 기록


def _leg(dd, side, e, t_from, st0, trail, tp, cfg, atr, sig, leg_no, day):
    be_at = 3.0
    tp_px = (e + side * tp) if tp else None
    cat = e - side * 0.6 * atr
    st = cat
    mfe = mae = 0.0
    trail_on = be = False
    pend = None          # 재시도 대기: 지정가
    tries = 0
    mode = cfg.get("stopx", ("mkt", "stop"))
    bars = [k for k in dd.idx if t_from < k <= S.TIME_EXIT and k in dd.h]
    for k in bars:
        h, l, c = dd.h[k], dd.l[k], dd.c[k]
        # [추격 재시도] chase/escalate/mkt1: 매분 현재가 기준으로 다시 낸다 — 반드시 청산
        if pend is not None and mode[0] in ("chase", "escalate", "mkt1"):
            o = dd.o.get(k, c)
            if (l <= cat) if side > 0 else (h >= cat):
                return k, cat, "SL", True, mfe, mae
            if mode[0] == "mkt1":
                EV.append((day, leg_no, "retry_fill", k, 1))
                return k, o, "BE" if be else "TR", True, mfe, mae
            if side * (o - pend) >= 0:                       # 시가가 지정가보다 유리 → 시가 체결
                EV.append((day, leg_no, "retry_fill", k, tries + 1))
                return k, o, "BE" if be else "TR", False, mfe, mae
            if (h >= pend) if side > 0 else (l <= pend):
                EV.append((day, leg_no, "retry_fill", k, tries + 1))
                return k, pend, "BE" if be else "TR", False, mfe, mae
            tries += 1
            if mode[0] == "chase":
                band_k = mode[1]
            else:
                ladder = [1.0, 2.0, 4.0]
                band_k = ladder[tries] if tries < len(ladder) else None
            if band_k is None:                                # 가격제한폭 지정가 = 무조건 체결 → 다음 봉 시가
                pend = c - side * 1e6
            else:
                pend = c - side * band_k
            continue
        # 재시도 대기 중
        if pend is not None:
            if (l <= cat) if side > 0 else (h >= cat):
                return k, cat, "SL", True, mfe, mae
            if (h >= pend) if side > 0 else (l <= pend):
                EV.append((day, leg_no, "retry_fill", k))
                return k, pend, "BE" if be else "TR", False, mfe, mae
            if side * (c - e) > 0 and side * (c - st) > 0:        # 진입가·스톱보다 유리 → 청산 불필요
                EV.append((day, leg_no, "retry_cancel", k))
                pend = None
            else:
                continue
        hit = st is not None and ((l <= st) if side > 0 else (h >= st))
        if hit:
            kind = "TR" if trail_on else ("BE" if be else "SL")
            ran = kind in ("BE", "TR") and side * (st - c) > cfg.get("band", 1.0)
            if kind == "SL" or not ran:
                if mode[0] == "close" and kind in ("BE", "TR") and side * (st - c) <= 0:
                    pass                                          # 종가 확인형: 종가가 스톱 안 → 유지
                else:
                    px = c if (mode[0] == "close" and kind in ("BE", "TR")) else st
                    return k, px, kind, True, mfe, mae
            else:
                EV.append((day, leg_no, "ran", k, round(side * (st - c), 2)))
                if mode[0] == "mkt":
                    fill = {"stop": st, "mid": (st + c) / 2.0, "close": c}[mode[1]]
                    return k, fill, kind, True, mfe, mae
                if mode[0] == "close":
                    return k, c, kind, True, mfe, mae
                pend = st - side * (mode[1] if mode[0] in ("retry", "chase") else 1.0)   # 첫 지정가 = 스톱 ∓ band
                continue
        if tp_px is not None and ((h >= tp_px) if side > 0 else (l <= tp_px)):
            return k, tp_px, "TP", False, mfe, mae
        mfe = max(mfe, (h - e) if side > 0 else (e - l))
        mae = max(mae, (e - l) if side > 0 else (h - e))
        pre = (not be) and (not trail_on) and mfe < be_at
        if pre and leg_no and t_from < "10:00" and mae >= 0.4 * atr:            # 첫 FLOW 컷 0.4
            return k, c, "SL", True, mfe, mae
        if trail is not None and mfe >= trail[0]:
            ns = (e + side * mfe) - side * trail[1]
            if side * (ns - st) > 0:
                st, trail_on = ns, True
        if not trail_on and mfe >= be_at and side * (e - st) > 0:
            st, be = e, True
    tx = dd.last_at_or_before(S.TIME_EXIT)
    return tx, dd.c[tx], "TIME", True, mfe, mae


def make_pos(d, cfg, day):
    cum, _ = F._flow_signal(d, d.sp, S.FLOWC_K, -1)
    atr = cfg["_atr"]

    def pos(dd, side, t0, stop, trail, tp):
        e = dd.c[t0]
        if t0 >= "10:00" and cum is not None and cum(t0) == -side:      # R60 누적일관성
            return sim4._skip(side, t0, t0)
        legs, info = [], []
        for n in (1, 2):
            ts, px, why, mkt, mfe, mae = _leg(dd, side, e, t0, stop, trail, tp, cfg, atr, None, n, day)
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
    out = {}
    sim4.F._run_signal = sim4.rs
    try:
        for day in sim4.sim.days():
            D, L = sim4.sim.frame(day)
            atr = L["0850"].get("atr14") or 33.3
            sim4.F._run_position = make_pos(D, dict(cfg, _atr=atr), day)
            try:
                res = F.run_family_day(D, L, "hybr60")
            finally:
                sim4.F._run_position = sim4.ORIG_RP
            out[day] = [dict(t=t["entry_ts"], x=t["exit_ts"], why=t["_why"], side=t["side"],
                             pt=round(E.trade_net(t) / 2 / S.PT_VALUE_KRW, 2)) for t in res["trades"]]
    finally:
        sim4.F._run_signal = sim4.ORIG_RS
        sim4.F._run_position = sim4.ORIG_RP
    return out
