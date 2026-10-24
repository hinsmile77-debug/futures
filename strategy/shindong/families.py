# -*- coding: utf-8 -*-
"""[MW0602 604차] 신동 v2 「계열」 규칙 — FLOWC · FLOWF · BRKC · FLOWR60 · [v3] HYBR60(MAIN) · HYBL · FLOWC_S.

`engine.run_day` 는 v1(R1/R2/R3)의 변형만 안다. v2 규칙은 R2·R3 가 없는 **별개 규칙**이라
같은 함수에 넣으면 분기가 폭발한다 — 그래서 여기 둔다. 반환 형식은 `run_day` 와 같아
`store`·`daily_report`·`scorecard` 가 그대로 받는다.

규칙(사전등록 `docs/신동거래_V2/신동_사전등록_V2_20260930.md`)
  FLOWC : 개인 위클리 콜−풋 누적(09:00 대비)이 +K 이상 → 매도 / −K 이하 → 매수(역방향)
  FLOWF : 외국인 선물 순매수 누적(09:00 이후 첫 수신 대비)이 −K 이하 → 매도 / +K 이상 → 매수(순방향)
  BRKC  : R1 방향일 = 종가가 구조맥점을 R1 방향으로 새로 넘으면 진입(손절 = 깬 맥점 ∓ 2) / 보류일 = FLOWC
  [v3] HYBR60 : 첫 거래 = FLOWC · 2·3번째 = FLOWR60(최근 60분 변화) · 재난 손절 뒤 손절 방향 누적 금지 — v3 MAIN(= v4 의 SHADOW_V3)
  [v3] HYBL   : 첫 거래 = FLOWC · 2·3번째 = 주도 지표(CP·FX 중 가격 추종 상관 높은 쪽) · 손절 방향 누적 금지
  [v3] FLOWC_S: FLOWC(v2.2 R1 가드 포함) · 손절 방향 누적 금지(당일 전면 중단 대신)
  [v4] V4     : HYBR60 + 본전이동@3 · 본전청산 상한 제외 · 첫 FLOW 역행컷 0.4×ATR · R60 누적일관성 · ATR 폴백 — MAIN
  [v4] BE3    : HYBR60 + 본전이동@3 · 본전청산 상한 제외 · ATR 폴백(컷·일관성 없음) — SHADOW_BE3
  [v4] HYBL4  : V4 에서 2·3번째 신호만 주도 지표 — SHADOW_HYBL4
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
RULE_R60 = "R60"                  # [v3] HYBR60 의 2·3번째 진입(FLOWR60 신호)
RULE_LEAD = "LEAD"                # [v3] HYBL 의 2·3번째 진입(주도 지표 신호)


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


def _minus_min(hhmm: str, n: int) -> str:
    return E._plus_min(hhmm, -n)


def _roll_signal(series: Dict[str, float], win_min: int, k_thr: float, sign: int) -> Callable[[str], int]:
    """[605차 SHADOW_FLOWR60] **최근 win_min 분 변화**(지금 값 − win_min 분 전 값)로 방향.
    win_min 분 전 분이 FLOW_BASE(09:00) 이전이거나 그 분 값이 없으면 신호 없음 — 그래서 60분이면 첫 신호는 10:00.
    누적(09:00 대비)과 달리 흐름이 돌아서면 win_min 분 뒤에 잊는다."""
    def sig(k: str) -> int:
        v = series.get(k)
        if v is None:
            return 0
        rk = _minus_min(k, win_min)
        if rk < S.FLOW_BASE:
            return 0
        r = series.get(rk)
        if r is None:
            return 0
        dv = v - r
        return sign * (1 if dv >= k_thr else (-1 if dv <= -k_thr else 0))
    return sig


def _pearson(a: List[float], b: List[float]) -> Optional[float]:
    n = len(a)
    if n < 5:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) ** 0.5


def _lead_signal(d: "E.DayFrame") -> Tuple[Callable[[str], int], Dict[str, Any]]:
    """[v3 SHADOW_HYBL] 「가격이 따라가는 지표」의 최근 LEAD_WIN_MIN 분 변화로 방향.
    정렬 시계열: CP = −개인 콜−풋(역추종) · FX = +외국인 선물 순매수 누적(순추종).
    분 k 에서 k−W ~ k 의 가격 종가와 각 시계열의 피어슨 상관 → 높은 쪽이 주도(둘 다 LEAD_C_MIN 미만이면 0).
    주도 지표의 같은 창 변화 ≥ +K → 매수 / ≤ −K → 매도. k−W 가 09:00 이전이면 0(첫 신호 10:00).
    st["lead"] 에 마지막으로 신호를 낸 주도 지표 이름을 남긴다(기록용). 미래 참조 없음 — k 까지의 값만 쓴다."""
    keys = [k for k in d.idx if k >= S.FLOW_BASE and k in d.c]
    pos = {k: i for i, k in enumerate(keys)}
    ser = {"CP": {k: -d.sp[k] for k in keys if k in d.sp}, "FX": {k: d.fx[k] for k in keys if k in d.fx}}
    kk = {"CP": S.LEAD_K_CP, "FX": S.LEAD_K_FX}
    st: Dict[str, Any] = {"lead": None}
    cache: Dict[str, Tuple[int, Optional[str]]] = {}

    def sig(k: str) -> int:
        if k not in cache:
            out: Tuple[int, Optional[str]] = (0, None)
            i = pos.get(k)
            rk = _minus_min(k, S.LEAD_WIN_MIN)
            if i is not None and rk >= S.FLOW_BASE:
                ks = [x for x in keys[:i + 1] if x >= rk]
                px = [d.c[x] for x in ks]
                cand = []
                for nm, s in ser.items():
                    if all(x in s for x in ks):
                        r = _pearson(px, [s[x] for x in ks])
                        if r is not None and r >= S.LEAD_C_MIN:
                            cand.append((r, nm))
                if cand:
                    _r, lead = max(cand)
                    dv = ser[lead][k] - ser[lead][ks[0]]
                    out = ((1 if dv >= kk[lead] else (-1 if dv <= -kk[lead] else 0)), lead)
            cache[k] = out
        side, lead = cache[k]
        if side:
            st["lead"] = lead
        return side
    return sig, st


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
                  trail: Tuple[float, float], tp: Optional[float],
                  be_at: Optional[float] = None, cut_pts: Optional[float] = None) -> Dict[str, Any]:
    """진입 뒤 청산까지. `run_trade` 와 같은 반환 형식(두 다리 동일).

    [v4] be_at   : MFE 가 이 pt 에 닿으면 손절 = 진입가(트레일 점화 전만). 그 손절에 닿으면 사유 "BE".
         cut_pts : 본전·트레일 전(MFE < be_at) 구간에서 그 봉 고(저)가 기준 역행(MAE) ≥ 이 pt 이면
                   **그 봉 종가로 청산**(사유 "SL" — 손절 취급). 첫 FLOW 역행컷.
    한 봉 판정 순서(반사실 `docs/신동거래_V4/수익최대화_딥다이브_20261023_MW0602/sim6.py` 와 한 줄씩 같다):
      손절가 닿음(TR > BE > SL) → 익절 → MFE·MAE 갱신 → 역행컷 → 트레일 갱신 → 본전 무장.
    둘 다 None 이면 v3 이전과 같다(재현 테스트가 고정)."""
    e = d.c[t0]
    tp_px = (e + side * tp) if tp else None
    st = stop
    mfe = 0.0
    mae = 0.0
    trail_on = False
    be = False                        # [v4] 본전 무장
    cut = False                       # [v4] 첫 FLOW 역행컷 발동
    exit_ts = exit_px = reason = None
    mkt = True
    bars = [k for k in d.idx if t0 < k <= S.TIME_EXIT and k in d.h]
    for k in bars:
        h, l = d.h[k], d.l[k]
        if st is not None and ((l <= st) if side > 0 else (h >= st)):
            exit_ts, exit_px, reason, mkt = k, st, ("TR" if trail_on else ("BE" if be else "SL")), True
            break
        if tp_px is not None and ((h >= tp_px) if side > 0 else (l <= tp_px)):
            exit_ts, exit_px, reason, mkt = k, tp_px, "TP", False
            break
        fav = (h - e) if side > 0 else (e - l)
        mfe = max(mfe, fav)
        mae = max(mae, (e - l) if side > 0 else (h - e))
        if (cut_pts is not None and not be and not trail_on
                and (be_at is None or mfe < be_at) and mae >= cut_pts):
            exit_ts, exit_px, reason, mkt = k, d.c[k], "SL", True
            cut = True
            break
        if trail is not None and mfe >= trail[0]:
            ns = (e + side * mfe) - side * trail[1]
            if st is None or side * (ns - st) > 0:
                st, trail_on = ns, True
        if be_at is not None and not trail_on and mfe >= be_at and (st is None or side * (e - st) > 0):
            st, be = e, True
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
            "stop_now": st, "be_armed": be, "cut": cut}


def _run_signal(d: "E.DayFrame", sig: Callable[[str], int], rule: str, stop_fn, trail, tp, max_trades: int,
                start: str = "09:00", level_of=None, halt_on_sl: bool = False,
                notes: Optional[List[str]] = None, halt_mode: Optional[str] = None,
                r1_bias: int = 0, ctr_max: Optional[int] = None,
                sig_after: Optional[Callable[[str], int]] = None, rule_after: Optional[str] = None,
                be_at: Optional[float] = None, first_cut_pts: Optional[float] = None,
                be_free: bool = False, agree: Optional[Callable[[str], int]] = None
                ) -> List[Dict[str, Any]]:
    """stop_fn(side, entry_px) -> 손절가 또는 None.
    halt_mode: "all"(손절 뒤 당일 전면 중단 — v2.1 규격) · "same"(손절 난 방향만 중단 — [605차] 반사실 계측용,
               마지막 손절 방향으로 덮어쓴다) · "sticky"([v3] 손절 난 방향을 **누적** 금지 — 양방향 손절이면 당일 끝) · None.
    sig_after: [v3] 주어지면 하루 **두 번째 거래부터** 이 신호로 진입한다(첫 거래는 sig). rule 표기는 rule_after.
               sig 는 그 뒤에도 매분 불러 상태(BRK 직전 종가 등)를 잇는다.
    halt_on_sl=True 는 halt_mode="all" 과 같다(호환).
    [v4] be_at        : 모든 거래에 본전이동(`_run_position(be_at=)`).
         first_cut_pts: 하루 **첫 거래**에만 역행컷(`_run_position(cut_pts=)`) — 사유 "SL" 이라 손절 방향 금지·상한 포함.
         be_free      : 본전청산(사유 "BE")은 하루 상한(max_trades)에 세지 않는다. 방향 금지는 원래 "SL" 에만 걸린다.
         agree        : 2번째 거래부터, 그 분의 agree 신호(FLOWC 누적)가 진입 방향과 **반대면** 진입하지 않는다(중립은 진입).
    halt_on_sl=True (v2.1 재난 손절): 손절(SL)이 한 번 발동하면 **그날 신규 진입을 멈춘다** —
    신호가 살아 있어 곧바로 같은 방향으로 재진입하는 것을 끊는다(9/29 실측: 손절 8·12pt 가 재진입으로 손실을 키웠다)."""
    trades: List[Dict[str, Any]] = []
    busy = None
    halted = False
    blocked = 0                       # halt_mode="same": 손절 난 방향만 그날 막는다
    banned = set()                    # [v3] halt_mode="sticky": 손절 난 방향을 누적해 막는다
    ban_hits = 0                      # 금지 방향 신호로 막힌 분(탈락 가시화 — 계측 4원칙 ③)
    mode = halt_mode or ("all" if halt_on_sl else None)
    # [v2.2] R1 반대 방향 재진입 금지 — ctr_max 가 None 이면 꺼짐(섀도·반사실은 종전과 같다)
    ctr_n = 0
    ctr_blocked = []                  # 막힌 분(탈락 가시화 — 계측 4원칙 ③)
    agree_blocked = []                # [v4] 누적일관성으로 막힌 분(탈락 가시화)

    def _counted() -> int:
        # [v4] be_free 면 본전에서 닫힌 거래는 상한에 세지 않는다(열린 거래·다른 사유는 센다)
        if not be_free:
            return len(trades)
        return sum(1 for t in trades
                   if not (t["status"] == "CLOSED" and t["legs"][0].get("reason") == "BE"))
    for k in d.idx:
        if k < start or k not in d.c:
            continue
        if busy is not None and k <= busy:
            sig(k)                    # 상태(직전 종가)는 계속 갱신
            continue
        if halted or k > S.FLOW_LAST_ENTRY or _counted() >= max_trades:
            sig(k)
            continue
        after = sig_after is not None and len(trades) >= 1
        side = sig(k)
        if after:
            side = sig_after(k)
        if not side or side == blocked:
            continue
        if side in banned:
            ban_hits += 1
            continue
        ctr = bool(r1_bias) and side == -r1_bias
        if ctr and ctr_max is not None and ctr_n >= ctr_max:
            ctr_blocked.append(k)
            continue
        if agree is not None and trades and agree(k) == -side:
            agree_blocked.append(k)
            continue
        e = d.c[k]
        stop = stop_fn(side, e) if stop_fn else None
        tr = _run_position(d, side, k, stop, trail, tp, be_at=be_at,
                           cut_pts=(first_cut_pts if not trades else None))
        tr.update(rule=(rule_after or rule) if after else rule,
                  touch_level=(level_of() if level_of else None), touch_ts=None)
        trades.append(tr)
        busy = tr["exit_ts"] or "99:99"
        if ctr:
            ctr_n += 1
        if mode in ("all", "same", "sticky") and tr["status"] == "CLOSED" and tr["legs"][0].get("reason") == "SL":
            if mode == "sticky":
                banned.add(side)
                if len(banned) >= 2:
                    halted = True
                if notes is not None:
                    notes.append("재난 손절 발동(%s) — %s 당일 금지%s" % (
                        tr["exit_ts"], "매수" if side > 0 else "매도",
                        " · 양방향 손절 — 당일 신규 진입 종료" if halted else " · 반대 방향은 진입 가능"))
            elif mode == "all":
                halted = True
                if notes is not None:
                    notes.append("재난 손절 발동(%s) — 당일 신규 진입 중단" % tr["exit_ts"])
            else:
                blocked = side
                if notes is not None:
                    notes.append("재난 손절 발동(%s) — 같은 방향만 당일 중단" % tr["exit_ts"])
    if ban_hits and notes is not None:
        notes.append("[v3] 손절 방향 금지로 막힌 신호 %d분 (금지 %s)" % (
            ban_hits, "·".join("매수" if x > 0 else "매도" for x in sorted(banned))))
    if agree_blocked and notes is not None:
        notes.append("[v4] R60 누적일관성 차단 — 첫 %s · 신호 %d분 (누적 FLOWC 와 반대 방향)"
                     % (agree_blocked[0], len(agree_blocked)))
    if ctr_blocked and notes is not None:
        # 신호가 켜져 있던 분마다 세면 수십 개라 첫 시각·분 수만 남긴다(…외 N 형식 — 계측 4원칙 ③).
        notes.append("[v2.2] R1 반대 재진입 차단 — 첫 %s · 신호 %d분 (R1 %s · 허용 %d건 소진)"
                     % (ctr_blocked[0], len(ctr_blocked), "하방" if r1_bias < 0 else "상방", ctr_max or 0))
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


def _v4_atr(L, notes: Optional[List[str]] = None) -> Optional[float]:
    """[v4] ATR14 — `runner.resolve_atr14_v4` 가 `L["0850"]["atr14_v4"]`(+ `_src`)로 넘긴 값.
    그 키가 없으면(테스트·직접 호출) 08:50 `atr14` 만 쓴다. 고정 pt 폴백은 **없다** — 못 구하면 None(그날 신규 진입 없음).
    08:50 값이 아니면 출처를 notes 에 남긴다(계측 4원칙 ④)."""
    try:
        z = L["0850"]
    except (KeyError, TypeError):
        z = {}
    if "atr14_v4" in z:
        v, src = z.get("atr14_v4"), z.get("atr14_v4_src") or "?"
    else:
        v, src = z.get("atr14"), "0850"
    if isinstance(v, (int, float)) and v > 0:
        if src != "0850" and notes is not None:
            notes.append("[v4] ATR14 폴백 %.2f — %s" % (float(v), src))
        return float(v)
    if notes is not None:
        notes.append("[v4] ATR14 미확보(08:50 · 재계산 · 이월 모두 없음) — 신규 진입 없음(기록만)")
    return None


def _v4_trades(d: "E.DayFrame", L, dec: Dict[str, Any], after: str, cut: bool, agree: bool
               ) -> List[Dict[str, Any]]:
    """[v4] MAIN(v4) · SHADOW_BE3 · SHADOW_HYBL4 공통 골격 — 첫 거래 FLOWC · 2·3번째 after("r60"|"lead") ·
    손절 방향 누적 금지 · 본전이동@V4_BE_AT · 본전청산 상한 제외. cut=첫 FLOW 역행컷 · agree=R60 누적일관성."""
    notes = dec["notes"]
    atr = _v4_atr(L, notes)
    if atr is None:
        return []
    sig, why = _flow_signal(d, d.sp, S.FLOWC_K, -1)
    if sig is None:
        notes.append("FLOWC %s — 거래 없음(미측정)" % why)
        return []
    cat = S.FLOW_CAT_STOP_ATR * atr
    if after == "lead":
        if not d.fx:
            notes.append("HYBL 외국인 선물 원천 없음 — 주도 지표는 CP 만으로 판정(미측정 ≠ 0)")
        sig_after, _lst = _lead_signal(d)
        rule_after = RULE_LEAD
    else:
        sig_after, rule_after = _roll_signal(d.sp, S.FLOWR_WIN_MIN, S.FLOWR_K, -1), RULE_R60
    trades = _run_signal(d, sig, RULE_FLOW, lambda side, e: e - side * cat, S.FLOW_TRAIL, S.FLOW_TP,
                         S.FLOW_MAX_TRADES, notes=notes, halt_mode=S.HYB_SL_HALT_MODE,
                         sig_after=sig_after, rule_after=rule_after,
                         be_at=S.V4_BE_AT, first_cut_pts=(S.V4_FIRST_CUT_ATR * atr) if cut else None,
                         be_free=S.V4_BE_FREE, agree=sig if agree else None)
    n_be = sum(1 for t in trades if t["status"] == "CLOSED" and t["legs"][0].get("reason") == "BE")
    n_cut = sum(1 for t in trades if t.get("cut"))
    if n_be:
        notes.append("[v4] 본전청산 %d건 — 하루 상한·방향 금지 제외" % n_be)
    if n_cut:
        t = next(t for t in trades if t.get("cut"))
        notes.append("[v4] 첫 FLOW 역행컷 발동(%s · 컷 %.2fpt = %.1f×ATR %.2f) — 손절 취급(그 방향 당일 금지)"
                     % (t["exit_ts"], S.V4_FIRST_CUT_ATR * atr, S.V4_FIRST_CUT_ATR, atr))
    return trades


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

    def flowc(r1_guard=False):
        sig, why = _flow_signal(d, d.sp, S.FLOWC_K, -1)
        if sig is None:
            dec["notes"].append("FLOWC %s — 거래 없음(미측정)" % why)
            return []
        return _run_signal(d, sig, RULE_FLOW, cat_stop, S.FLOW_TRAIL, S.FLOW_TP, S.FLOW_MAX_TRADES,
                           halt_on_sl=S.FLOW_CAT_STOP_HALT_DAY, notes=dec["notes"],
                           r1_bias=bias if r1_guard else 0,
                           ctr_max=S.FLOW_R1_CTR_MAX if r1_guard else None)

    if family in ("v4", "be3", "hybl4"):
        # [v4] MAIN = v4 · SHADOW_BE3 = v3 + 본전이동만(컷·일관성 없음) · SHADOW_HYBL4 = v4 + 주도 지표 재진입.
        #   셋 다 ATR14 를 `_v4_atr`(재계산·이월 폴백, 고정 pt 없음)로 쓴다 — `cat` 위 계산(20pt 폴백)은 쓰지 않는다.
        #   위 `_cat_stop_pts` 가 남긴 「ATR14 없음 — 20pt 폴백」 문구는 v4 계열에서 사실이 아니므로 지운다.
        dec["notes"] = [n for n in dec["notes"] if not n.startswith("ATR14 없음 — 재난 손절 폴백")]
        trades = _v4_trades(d, L, dec, after=("lead" if family == "hybl4" else "r60"),
                            cut=(family != "be3"), agree=(family != "be3" and S.V4_R60_AGREE))
    elif family == "flowc":
        # [v2.2] v2.2 MAIN(= v3 의 SHADOW_V22)의 FLOWC 만 R1 반대 재진입 금지를 쓴다. BRKC 보류일 대체(아래)는
        # R1=0 이라 어차피 무영향이지만 규격을 섞지 않으려 명시적으로 끈다.
        trades = flowc(r1_guard=S.FLOW_R1_CTR_REENTRY_BLOCK)
    elif family == "flowc_s":
        # [v3 SHADOW_V22S] v2.2 MAIN 에서 손절 뒤 처리만 「손절 방향 누적 금지」로 바꾼다.
        sig, why = _flow_signal(d, d.sp, S.FLOWC_K, -1)
        if sig is None:
            dec["notes"].append("FLOWC %s — 거래 없음(미측정)" % why)
        else:
            trades = _run_signal(d, sig, RULE_FLOW, cat_stop, S.FLOW_TRAIL, S.FLOW_TP, S.FLOW_MAX_TRADES,
                                 notes=dec["notes"], halt_mode=S.SL_BAN_STICKY,
                                 r1_bias=bias if S.FLOW_R1_CTR_REENTRY_BLOCK else 0,
                                 ctr_max=S.FLOW_R1_CTR_MAX if S.FLOW_R1_CTR_REENTRY_BLOCK else None)
    elif family in ("hybr60", "hybl"):
        # [v3] 첫 거래 = FLOWC · 2·3번째 = FLOWR60(hybr60 = MAIN) / 주도 지표(hybl). 손절 방향 누적 금지.
        #   R1 반대 재진입 금지는 쓰지 않는다 — FLOWC 는 첫 거래만이라 재진입이 없고, 후반 신호에 걸면
        #   R1 오판일의 반대 전환을 막는다(spec 「v3」 절).
        sig, why = _flow_signal(d, d.sp, S.FLOWC_K, -1)
        if sig is None:
            dec["notes"].append("FLOWC %s — 거래 없음(미측정)" % why)
        elif family == "hybr60":
            trades = _run_signal(d, sig, RULE_FLOW, cat_stop, S.FLOW_TRAIL, S.FLOW_TP, S.FLOW_MAX_TRADES,
                                 notes=dec["notes"], halt_mode=S.HYB_SL_HALT_MODE,
                                 sig_after=_roll_signal(d.sp, S.FLOWR_WIN_MIN, S.FLOWR_K, -1), rule_after=RULE_R60)
        else:
            if not d.fx:
                dec["notes"].append("HYBL 외국인 선물 원천 없음 — 주도 지표는 CP 만으로 판정(미측정 ≠ 0)")
            lsig, _lst = _lead_signal(d)
            trades = _run_signal(d, sig, RULE_FLOW, cat_stop, S.FLOW_TRAIL, S.FLOW_TP, S.FLOW_MAX_TRADES,
                                 notes=dec["notes"], halt_mode=S.HYB_SL_HALT_MODE,
                                 sig_after=lsig, rule_after=RULE_LEAD)
    elif family == "flowr60":
        if not d.sp:
            dec["notes"].append("FLOWR60 원천 없음 — 거래 없음(미측정)")
        else:
            trades = _run_signal(d, _roll_signal(d.sp, S.FLOWR_WIN_MIN, S.FLOWR_K, -1), RULE_FLOW, cat_stop,
                                 S.FLOW_TRAIL, S.FLOW_TP, S.FLOW_MAX_TRADES,
                                 halt_on_sl=S.FLOW_CAT_STOP_HALT_DAY, notes=dec["notes"])
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


def flowc_counterfactual(d: "E.DayFrame", L, cat_atr: Optional[float] = None,
                         halt_mode: Optional[str] = "all") -> Optional[List[Dict[str, Any]]]:
    """[605차] MAIN(FLOWC)의 **반사실** 재계산 — 채점표 「재난 손절 발동일」 계측 전용(기록·판정 경로 아님).
    cat_atr=None → 재난 손절 없음(15:05 까지) · halt_mode "all"/"same"/None.
    흐름·맥점이 없으면 None(미측정 ≠ 0)."""
    if L is None or "0850" not in L:
        return None
    sig, _why = _flow_signal(d, d.sp, S.FLOWC_K, -1)
    if sig is None:
        return None
    if cat_atr is None:
        stop_fn = None
    else:
        atr = L["0850"].get("atr14")
        cat = cat_atr * float(atr) if isinstance(atr, (int, float)) and atr > 0 else S.FLOW_CAT_STOP_FALLBACK_PT
        stop_fn = lambda side, e: e - side * cat
    return _run_signal(d, sig, RULE_FLOW, stop_fn, S.FLOW_TRAIL, S.FLOW_TP, S.FLOW_MAX_TRADES, halt_mode=halt_mode)
