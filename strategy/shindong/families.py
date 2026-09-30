# -*- coding: utf-8 -*-
"""[MW0602 604차] 신동 v2 「계열」 규칙 — MAIN(FLOWC) · SHADOW_FLOWF · SHADOW_BRKC.

`engine.run_day` 는 v1(R1/R2/R3)의 변형만 안다. v2 규칙은 R2·R3 가 없는 **별개 규칙**이라
같은 함수에 넣으면 분기가 폭발한다 — 그래서 여기 둔다. 반환 형식은 `run_day` 와 같아
`store`·`daily_report`·`scorecard` 가 그대로 받는다.

규칙(사전등록 `docs/신동거래_V2/신동_사전등록_V2_20260930.md`)
  FLOWC : 개인 위클리 콜−풋 누적(09:00 대비)이 +K 이상 → 매도 / −K 이하 → 매수(역방향)
  FLOWF : 외국인 선물 순매수 누적(09:00 이후 첫 수신 대비)이 −K 이하 → 매도 / +K 이상 → 매수(순방향)
  BRKC  : R1 방향일 = 종가가 구조맥점을 R1 방향으로 새로 넘으면 진입(손절 = 깬 맥점 ∓ 2) / 보류일 = FLOWC
  청산  : 손절(BRK 만) → 트레일(유리 act pt → 극값 ∓ dist, 그 봉 극값은 다음 봉부터) → 익절 지정가 →
          15:05 시간 청산. 한 봉에서 손절·익절이 함께 닿으면 **손절**(보수적). 신규 진입 14:50 까지.
  수량  : 2계약 일괄 — 두 다리가 같은 가격·같은 사유로 닫힌다(legs 형식 유지).

미래 참조 금지 — DayFrame 이 horizon 뒤를 잘라 온다. 진입은 신호 봉 **종가**, 청산 검사는 다음 봉부터.
9/30 격자 시뮬레이터(`docs/신동거래/최적조건_탐색_20260930_MW0602/sim.py`)와 한 줄씩 같다 —
`tests/test_604_shindong_v2.py` 가 합성 재현값으로 고정한다.
"""
from typing import Any, Callable, Dict, List, Optional, Tuple

from strategy.shindong import engine as E
from strategy.shindong import spec as S

RULE_FLOW = "FLOW"
RULE_BRK = "BRK"


def _r1_bias(d: "E.DayFrame") -> Tuple[Optional[float], Optional[int]]:
    """v1 R1 과 같은 판정(장전 마지막 콜−풋). (pm_sp, bias) — 흐름 없으면 (None, 0)."""
    pm = [k for k in d.idx if k <= S.PREMARKET_LAST and k in d.sp]
    if not pm:
        return None, 0
    sp = d.sp[pm[-1]]
    return sp, (0 if abs(sp) < S.BIAS_MIN else (-1 if sp > 0 else 1))


def _flow_signal(d: "E.DayFrame", series: Dict[str, float], k_thr: float, sign: int
                 ) -> Tuple[Optional[Callable[[str], int]], Optional[str]]:
    """누적 시계열의 기준점 대비 변화로 방향. sign=-1 역방향(콜−풋) · +1 순방향(외국인).
    기준점 = FLOW_BASE 값, 없으면 그 이후 첫 값. 시계열이 비면 (None, 사유)."""
    if not series:
        return None, "원천 없음"
    if S.FLOW_BASE in series:
        base_k = S.FLOW_BASE
    else:
        after = [k for k in sorted(series) if k > S.FLOW_BASE]
        if not after:
            return None, "기준점 없음"
        base_k = after[0]
    base = series[base_k]

    def sig(k: str) -> int:
        v = series.get(k)
        if v is None or k < base_k:
            return 0
        dv = v - base
        # dv 의 부호 × sign: 역방향(-1)이면 콜−풋 ↑(+) → 매도(-1), 순방향(+1)이면 외국인 순매수 ↑ → 매수(+1)
        return sign * (1 if dv >= k_thr else (-1 if dv <= -k_thr else 0))
    return sig, base_k


def _brk_signal(d: "E.DayFrame", L, bias: int) -> Tuple[Callable[[str], int], Dict[str, Any]]:
    """종가가 구조맥점을 R1 방향으로 새로 넘으면 그 방향. st["lvl"] 에 깬 맥점을 남긴다."""
    st: Dict[str, Any] = {"prev": None, "lvl": None}

    def sig(k: str) -> int:
        _, lv = E.levels_at(L, k)
        prev, c = st["prev"], d.c[k]
        st["prev"] = c
        if prev is None or not bias:
            return 0
        for x in lv:
            sd = -1 if (prev >= x > c) else (1 if (prev <= x < c) else 0)
            if sd and sd == bias:
                st["lvl"] = x
                return sd
        return 0
    return sig, st


def _run_position(d: "E.DayFrame", side: int, t0: str, stop: Optional[float],
                  trail: Tuple[float, float], tp: Optional[float]) -> Dict[str, Any]:
    """진입 뒤 청산까지. `run_trade` 와 같은 반환 형식(두 다리 동일)."""
    e = d.c[t0]
    tp_px = (e + side * tp) if tp else None
    st = stop
    mfe = 0.0
    trail_on = False
    exit_ts = exit_px = reason = None
    mkt = True
    bars = [k for k in d.idx if t0 < k <= S.TIME_EXIT and k in d.h]
    for k in bars:
        h, l = d.h[k], d.l[k]
        if st is not None and ((l <= st) if side > 0 else (h >= st)):
            exit_ts, exit_px, reason, mkt = k, st, ("TR" if trail_on else "SL"), True
            break
        if tp_px is not None and ((h >= tp_px) if side > 0 else (l <= tp_px)):
            exit_ts, exit_px, reason, mkt = k, tp_px, "TP", False
            break
        fav = (h - e) if side > 0 else (e - l)
        mfe = max(mfe, fav)
        if trail is not None and mfe >= trail[0]:
            ns = (e + side * mfe) - side * trail[1]
            if st is None or side * (ns - st) > 0:
                st, trail_on = ns, True
    horizon = d.idx[-1] if d.idx else None
    if exit_ts is None and horizon is not None and horizon >= S.TIME_EXIT:
        tx = d.last_at_or_before(S.TIME_EXIT)
        exit_ts, exit_px, reason, mkt = tx, d.c[tx], "TIME", True
    legs = []
    for n in (1, 2):
        g = {"leg": n, "tp": tp_px, "open": exit_ts is None}
        if exit_ts is not None:
            pts, net = E.leg_net(side, e, exit_px, mkt)
            g.update(ts=exit_ts, px=exit_px, mkt=mkt, pts=pts, net=net,
                     reason=("TP1" if n == 1 else "TP2") if reason == "TP" else reason)
        legs.append(g)
    return {"side": side, "entry_ts": t0, "entry_px": e, "stop_init": stop, "t1": tp_px, "t2": tp_px,
            "legs": legs, "status": "OPEN" if exit_ts is None else "CLOSED", "exit_ts": exit_ts,
            "stop_now": st}


def _run_signal(d: "E.DayFrame", sig: Callable[[str], int], rule: str, stop_fn, trail, tp, max_trades: int,
                start: str = "09:00", level_of=None, halt_on_sl: bool = False,
                notes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """stop_fn(side, entry_px) -> 손절가 또는 None.
    halt_on_sl=True (v2.1 재난 손절): 손절(SL)이 한 번 발동하면 **그날 신규 진입을 멈춘다** —
    신호가 살아 있어 곧바로 같은 방향으로 재진입하는 것을 끊는다(9/29 실측: 손절 8·12pt 가 재진입으로 손실을 키웠다)."""
    trades: List[Dict[str, Any]] = []
    busy = None
    halted = False
    for k in d.idx:
        if k < start or k not in d.c:
            continue
        if busy is not None and k <= busy:
            sig(k)                    # 상태(직전 종가)는 계속 갱신
            continue
        if halted or k > S.FLOW_LAST_ENTRY or len(trades) >= max_trades:
            sig(k)
            continue
        side = sig(k)
        if not side:
            continue
        e = d.c[k]
        stop = stop_fn(side, e) if stop_fn else None
        tr = _run_position(d, side, k, stop, trail, tp)
        tr.update(rule=rule, touch_level=(level_of() if level_of else None), touch_ts=None)
        trades.append(tr)
        busy = tr["exit_ts"] or "99:99"
        if halt_on_sl and tr["status"] == "CLOSED" and tr["legs"][0].get("reason") == "SL":
            halted = True
            if notes is not None:
                notes.append("재난 손절 발동(%s) — 당일 신규 진입 중단" % tr["exit_ts"])
    return trades


def _cat_stop_pts(L, notes: Optional[List[str]] = None) -> float:
    """[v2.1] 재난 손절 폭(pt) = FLOW_CAT_STOP_ATR × ATR14(08:50 산출). ATR14 가 없으면 고정 폴백 — 폴백 사실을 남긴다(계측 4원칙 ④)."""
    atr = None
    try:
        atr = L["0850"].get("atr14")
    except (KeyError, AttributeError, TypeError):
        atr = None
    if isinstance(atr, (int, float)) and atr > 0:
        return S.FLOW_CAT_STOP_ATR * float(atr)
    if notes is not None:
        notes.append("ATR14 없음 — 재난 손절 폴백 %.0fpt" % S.FLOW_CAT_STOP_FALLBACK_PT)
    return S.FLOW_CAT_STOP_FALLBACK_PT


def run_family_day(d: "E.DayFrame", L, family: str,
                   v1_decision: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """하루 판정 — `engine.run_day` 와 같은 반환. decision 에는 v1 의 R1/R2 판정을 실어 둔다(기록·채점용)."""
    if v1_decision is not None:
        dec = dict(v1_decision)
        dec["notes"] = list(dec.get("notes") or [])
    else:
        pm_sp, bias = _r1_bias(d)
        dec = {"pm_sp": pm_sp, "bias": bias, "r2": None, "r2_ts": None, "notes": []}
    dec["family"] = family
    trades: List[Dict[str, Any]] = []
    if L is None or "0850" not in L:
        dec["notes"].append("08:50 맥점 없음 — 판정 불가")
        return {"decision": dec, "trades": trades}
    bias = int(dec.get("bias") or 0)
    cat = _cat_stop_pts(L, dec["notes"])                     # [v2.1] 재난 손절 폭(pt)
    cat_stop = lambda side, e: e - side * cat               # 진입가 ∓ 재난 손절 폭

    def flowc():
        sig, why = _flow_signal(d, d.sp, S.FLOWC_K, -1)
        if sig is None:
            dec["notes"].append("FLOWC %s — 거래 없음(미측정)" % why)
            return []
        return _run_signal(d, sig, RULE_FLOW, cat_stop, S.FLOW_TRAIL, S.FLOW_TP, S.FLOW_MAX_TRADES,
                           halt_on_sl=S.FLOW_CAT_STOP_HALT_DAY, notes=dec["notes"])

    if family == "flowc":
        trades = flowc()
    elif family == "flowf":
        sig, why = _flow_signal(d, d.fx, S.FLOWF_K, +1)
        if sig is None:
            dec["notes"].append("FLOWF 외국인 선물 %s — 거래 없음(미측정)" % why)
        else:
            trades = _run_signal(d, sig, RULE_FLOW, cat_stop, S.FLOW_TRAIL, S.FLOW_TP, S.FLOW_MAX_TRADES,
                                 halt_on_sl=S.FLOW_CAT_STOP_HALT_DAY, notes=dec["notes"])
    elif family == "brkc":
        if bias:
            sig, st = _brk_signal(d, L, bias)
            trades = _run_signal(d, sig, RULE_BRK,
                                 lambda side, e: st["lvl"] + S.BRK_STOP_BUF if side < 0 else st["lvl"] - S.BRK_STOP_BUF,
                                 S.BRK_TRAIL, S.BRK_TP, S.BRK_MAX_TRADES, level_of=lambda: st["lvl"])
        else:
            dec["notes"].append("R1 보류일 — FLOWC 로 거래")
            trades = flowc()
    else:
        raise ValueError("unknown family %r" % family)
    return {"decision": dec, "trades": trades}
