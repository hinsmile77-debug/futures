# -*- coding: utf-8 -*-
"""거래 단위 트레일링 — engine.run_trade 와 같은 봉 판정 순서에 트레일을 얹는다.

act  : 진입가 대비 유리한 극값(MFE)이 이 pt 이상이 되면 트레일 시작
dist : 트레일 손절 = 극값 − dist (단조, 기존 손절보다 불리하면 무시)
mode : 'keep'  = 1차·최종 목표 유지 + 트레일
       'no2'   = 1차 목표 유지, 최종 목표 없음(트레일로만 청산)
보수적 규칙: 한 봉 안에서는 **이전 봉까지의 트레일 손절**로 먼저 검사하고, 그 봉 극값은 다음 봉부터 반영.
"""
import sys
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
from strategy.shindong import engine as E, spec as S


def make(act, dist, mode="keep"):
    def run(d, side, t0, stop, t1, t2, e2=False):
        e = d.c[t0]
        legs = [{"leg": 1, "tp": t1, "open": True},
                {"leg": 2, "tp": (None if mode == "no2" else t2), "open": True}]
        st = stop
        best = e
        for t in [k for k in d.idx if t0 < k <= S.TIME_EXIT]:
            h, l = d.h[t], d.l[t]
            for g in legs:
                if not g["open"]:
                    continue
                if (h >= st) if side < 0 else (l <= st):
                    g.update(open=False, ts=t, px=st, mkt=True,
                             reason=("BE" if st == e else ("TR" if side * (st - stop) > 0 and st != e else "SL")))
                    continue
                if g["tp"] is not None and ((l <= g["tp"]) if side < 0 else (h >= g["tp"])):
                    g.update(open=False, ts=t, px=g["tp"], mkt=False, reason="TP%d" % g["leg"])
                    if side * (e - st) > 0:
                        st = e                  # 1차 체결 → 본전(현행과 같음)
            if not any(g["open"] for g in legs):
                break
            best = max(best, h) if side > 0 else min(best, l)
            if side * (best - e) >= act:
                cand = best - side * dist
                if side * (cand - st) > 0:
                    st = cand
        if any(g["open"] for g in legs) and d.idx and d.idx[-1] >= S.TIME_EXIT:
            tx = d.last_at_or_before(S.TIME_EXIT)
            for g in legs:
                if g["open"]:
                    g.update(open=False, ts=tx, px=d.c[tx], mkt=True, reason="TIME")
        for g in legs:
            if not g["open"]:
                g["pts"], g["net"] = E.leg_net(side, e, g["px"], g["mkt"])
        closed = [g for g in legs if not g["open"]]
        return {"side": side, "entry_ts": t0, "entry_px": e, "stop_init": stop, "t1": t1, "t2": t2,
                "legs": legs, "status": "OPEN" if any(g["open"] for g in legs) else "CLOSED",
                "exit_ts": max(g["ts"] for g in closed) if len(closed) == len(legs) else None,
                "stop_now": st}
    return run
