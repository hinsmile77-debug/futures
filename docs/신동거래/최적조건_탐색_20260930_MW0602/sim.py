# -*- coding: utf-8 -*-
"""규칙 계열 × 파라미터 격자 시뮬레이터 — 현행 신동 규칙과 무관. 읽기 전용.

체결 가정(엔진과 같은 비용): 미니선물 2계약 · CYBOS 편도 요율 · 진입 1틱 · 시장가 청산 1틱.
- 진입: 신호 봉 **종가**(엔진과 같다). 다음 봉부터 청산 검사.
- 한 봉에서 손절과 익절이 모두 닿으면 **손절**(보수적).
- 트레일: 유리한 극값은 그 봉이 끝난 뒤 반영(다음 봉부터).
- 15:05 시간 청산. 신규 진입은 14:50까지.
"""
from strategy.shindong import engine as E

SESSION_END = "15:05"
LAST_ENTRY = "14:50"


def pos_net(side, e, x, market_exit, n=2):
    return n * E.leg_net(side, e, x, market_exit)[1]


def simulate(d, signal, stop=None, trail=None, tp=None, exit_sig=None, max_trades=99,
             start="09:00", stop_fn=None, cooldown=0):
    """signal(k, st) -> side(+1/-1/0).  stop: 진입가 대비 pt · stop_fn(k, side, e) -> 가격(우선).
    trail=(act, dist) · tp: pt · exit_sig(k, side, st) -> bool (종가 청산).  st: 호출 간 공유 dict."""
    ks = [k for k in d.idx if start <= k <= SESSION_END and k in d.c]
    trades, pos, st = [], None, {}
    last_exit_i = -999
    for i, k in enumerate(ks):
        if pos is not None:
            side, e = pos["side"], pos["e"]
            h, l = d.h[k], d.l[k]
            s = pos["stop"]
            hit_stop = s is not None and ((side > 0 and l <= s) or (side < 0 and h >= s))
            t = pos["tp"]
            hit_tp = t is not None and ((side > 0 and h >= t) or (side < 0 and l <= t))
            x = why = None
            if hit_stop:
                x, why, mk = s, "stop", True
            elif hit_tp:
                x, why, mk = t, "tp", False
            elif exit_sig is not None and exit_sig(k, side, st):
                x, why, mk = d.c[k], "sig", True
            elif k >= SESSION_END:
                x, why, mk = d.c[k], "time", True
            if x is not None:
                trades.append(dict(side=side, et=pos["t"], e=e, xt=k, x=x, why=why,
                                   net=pos_net(side, e, x, mk), mfe=pos["mfe"]))
                pos = None
                last_exit_i = i
                continue
            fav = (h - e) if side > 0 else (e - l)
            pos["mfe"] = max(pos["mfe"], fav)
            if trail is not None and pos["mfe"] >= trail[0]:
                ext = e + side * pos["mfe"]
                ns = ext - side * trail[1]
                if pos["stop"] is None or side * (ns - pos["stop"]) > 0:
                    pos["stop"] = ns
            continue
        if k > LAST_ENTRY or len(trades) >= max_trades or i - last_exit_i <= cooldown:
            signal(k, st)          # 상태는 계속 갱신
            continue
        side = signal(k, st)
        if side:
            e = d.c[k]
            s = stop_fn(k, side, e) if stop_fn else (e - side * stop if stop else None)
            pos = dict(side=side, e=e, t=k, stop=s, tp=(e + side * tp) if tp else None, mfe=0.0)
    if pos is not None:            # 방어 — 정상이면 15:05에서 닫힌다
        k = ks[-1]
        trades.append(dict(side=pos["side"], et=pos["t"], e=pos["e"], xt=k, x=d.c[k], why="time",
                           net=pos_net(pos["side"], pos["e"], d.c[k], True), mfe=pos["mfe"]))
    return trades


def total(trades):
    return sum(t["net"] for t in trades)
