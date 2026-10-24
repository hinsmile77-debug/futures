# -*- coding: utf-8 -*-
"""유형①·② 수익 최적화 딥다이브 재생기 — 읽기 전용(DB 미기록).

기준선 = 선행 보고서 「새 기준」: v3(hybr60) + 양다리 본전이동@3 + 본전청산 상한 제외(방향 금지 없음).
`../신동v3_꼬리위험_20261023_MW0602/sim3.py` 의 위치 시뮬레이터를 확장한 것이다(cfg={} 이면 같은 값).
엔진 함수(`families._run_signal`·`run_family_day`)를 쓰고 `_run_position` 만 런타임에 감싼다(원본 무수정·복원).

추가 옵션(cfg)
  be_lock    MFE≥3 때 손절 = 진입가 + side×be_lock (기본 0 = 본전)
  ladder     [(mfe, lock), ...] 추가 잠금 단계 — MFE≥mfe 이면 손절 ≥ 진입가 + side×lock
  trail      (발동, 간격) 덮어쓰기 · tp 익절폭 덮어쓰기(None = 익절 없음)
  tp1        1다리만 이 폭에서 익절(나머지 다리는 기본 규칙)
  pull       (k, n) 눌림 지정가 진입: 신호 봉 종가보다 k pt 유리한 지정가, n분 안에 미체결이면 생략
  agree      R60(10:00 이후 2·3번째) 진입이 누적 FLOWC 신호와 반대면 생략
  family     'hybr60'(기본) | 'hybl'(2·3번째 진입 = 주도 지표)
사용: 저장소 루트에서  python <이 폴더>/run4.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "strategy")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(HERE, "..", "신동v3_꼬리위험_20261023_MW0602"))
os.chdir(ROOT)
import sim                                                   # noqa: E402  선행 재생기(프레임 캐시·요약)
from strategy.shindong import engine as E, spec as S, families as F   # noqa: E402

BE_AT = 3.0
ORIG_RS = F._run_signal
ORIG_RP = F._run_position


def _leg(dd, side, e, t_from, st0, trail, tp, cfg):
    """한 다리를 진행 → (ts, px, why, mkt, mfe, mae)."""
    tp_px = (e + side * tp) if tp else None
    st, mfe, mae, trail_on, be = st0, 0.0, 0.0, False, False
    bars = [k for k in dd.idx if t_from < k <= S.TIME_EXIT and k in dd.h]
    for k in bars:
        h, l = dd.h[k], dd.l[k]
        if st is not None and ((l <= st) if side > 0 else (h >= st)):
            return k, st, ("TR" if trail_on else ("BE" if be else "SL")), True, mfe, mae
        if tp_px is not None and ((h >= tp_px) if side > 0 else (l <= tp_px)):
            return k, tp_px, "TP", False, mfe, mae
        mfe = max(mfe, (h - e) if side > 0 else (e - l))
        mae = max(mae, (e - l) if side > 0 else (h - e))
        if trail is not None and mfe >= trail[0]:
            ns = (e + side * mfe) - side * trail[1]
            if st is None or side * (ns - st) > 0:
                st, trail_on = ns, True
        if not trail_on:
            locks = [(BE_AT, cfg.get("be_lock", 0.0))] + list(cfg.get("ladder", []))
            for m, lk in locks:
                if mfe >= m:
                    ns = e + side * lk
                    if side * (ns - st) > 0:
                        st, be = ns, True
    tx = dd.last_at_or_before(S.TIME_EXIT)
    return tx, dd.c[tx], "TIME", True, mfe, mae


def make_pos(d, cfg):
    cum, _ = F._flow_signal(d, d.sp, S.FLOWC_K, -1)

    def pos(dd, side, t0, stop, trail, tp):
        trail = cfg.get("trail", trail)
        tp = cfg.get("tp", tp) if "tp" in cfg else tp
        e, start = dd.c[t0], t0
        # 눌림 지정가 진입
        if cfg.get("pull"):
            k_pt, n = cfg["pull"]
            lim = e - side * k_pt
            fut = [k for k in dd.idx if t0 < k <= E._plus_min(t0, n) and k in dd.h]
            hit = next((k for k in fut if ((dd.l[k] <= lim) if side > 0 else (dd.h[k] >= lim))), None)
            if hit is None:
                end = fut[-1] if fut else t0
                return _skip(side, t0, end)
            e, start = lim, hit
            stop = e - side * abs(dd.c[t0] - stop) if stop is not None else None
        if cfg.get("agree") and t0 >= "10:00" and cum is not None and cum(t0) == -side:
            return _skip(side, t0, t0)
        legs, info = [], []
        for n in (1, 2):
            tpn = cfg["tp1"] if (n == 1 and cfg.get("tp1")) else tp
            ts, px, why, mkt, mfe, mae = _leg(dd, side, e, start, stop, trail, tpn, cfg)
            pts, net = E.leg_net(side, e, px, mkt)
            legs.append(dict(leg=n, tp=(e + side * tpn) if tpn else None, open=False, ts=ts, px=px, mkt=mkt, pts=pts,
                             net=net, reason=(("TP1" if n == 1 else "TP2") if why == "TP" else why)))
            info.append((ts, why, mfe, mae))
        x = max(i[0] for i in info)
        whys = [i[1] for i in info]
        return dict(side=side, entry_ts=t0, entry_px=e, stop_init=stop, t1=legs[0]["tp"], t2=legs[1]["tp"], legs=legs,
                    status="CLOSED", exit_ts=x, stop_now=None, _be=all(w == "BE" for w in whys),
                    _why="/".join(sorted(set(whys))), _mfe=max(i[2] for i in info), _mae=max(i[3] for i in info))
    return pos


def _skip(side, t0, end):
    z = dict(leg=1, tp=None, open=False, ts=end, px=0.0, mkt=False, pts=0.0, net=0.0, reason="SKIP")
    return dict(side=side, entry_ts=t0, entry_px=0.0, stop_init=None, t1=None, t2=None, legs=[z, dict(z, leg=2)],
                status="CLOSED", exit_ts=end, stop_now=None, _be=True, _why="SKIP", _mfe=0.0, _mae=0.0, _skip=True)


def rs(d, sig, rule, stop_fn, trail, tp, max_trades, **kw):
    """본전청산·생략은 하루 상한에 세지 않는다(선행 sim3 와 같은 처리)."""
    out = ORIG_RS(d, sig, rule, stop_fn, trail, tp, max_trades + 20, **kw)
    keep, n = [], 0
    for t in out:
        if n >= max_trades:
            break
        if not t.get("_skip"):
            keep.append(t)
        n += 0 if t.get("_be") else 1
    return keep


def run(cfg, ds=None):
    out = {}
    F._run_signal = rs
    try:
        for day in ds or sim.days():
            D, L = sim.frame(day)
            F._run_position = make_pos(D, cfg)
            try:
                res = F.run_family_day(D, L, cfg.get("family", "hybr60"))
            finally:
                F._run_position = ORIG_RP
            atr = L["0850"].get("atr14") or 33.3
            out[day] = [dict(rule=t["rule"], side=t["side"], t=t["entry_ts"], x=t["exit_ts"], why=t["_why"],
                             mfe=round(t["_mfe"], 1), mae=round(t["_mae"], 1), atr=round(atr, 1),
                             pt=round(E.trade_net(t) / 2 / S.PT_VALUE_KRW, 2)) for t in res["trades"]]
    finally:
        F._run_signal = ORIG_RS
        F._run_position = ORIG_RP
    return out
