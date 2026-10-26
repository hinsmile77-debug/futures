# -*- coding: utf-8 -*-
"""신동 규칙 엔진 — 순수 함수. DB·Qt 를 모른다.

입력은 그날의 분 단위 표(`DayFrame`)와 장전 맥점(`levels`), 출력은 판정 기록과
가상거래 목록이다. **매분 하루치를 처음부터 다시 계산(재생)한다.**

왜 재생인가
-----------
증분 상태를 들고 다니면 재기동이 그 상태를 지운다 — 552-10(`_broker_dep_base_today`)과
552-11(`entry_source` 오귀속)이 같은 계열이다. 재생은 같은 입력이면 같은 답을 내므로
재기동 전후가 갈라지지 않는다.

미래 참조 금지
--------------
`horizon`(= 봉·흐름이 **둘 다** 도착한 마지막 분) 뒤의 값은 보지 않는다.
09:30 산출 맥점은 09:31 부터만 쓴다(analysis 와 동일).

⚠ 이 파일의 판정 순서는 사전등록 당시 분석 스크립트(`common.py` · `var.py`,
  2026-09-24 세션)와 **한 줄씩 같다.** 겉보기에 이상한 순서(예: 같은 봉에서 1차 익절
  직후 본전 손절 검사)도 규격의 일부이므로 "정리"하지 말 것 —
  `tests/test_626_shindong.py` 가 9/21–9/23 재현값으로 고정한다.
"""
import datetime as _dt
import json
from typing import Any, Dict, List, Optional, Tuple

from strategy.shindong import spec as S


# ── 분 단위 표 ──────────────────────────────────────────────────────────
class DayFrame:
    """분(HH:MM) → OHLC · 콜 · 풋 · 콜−풋. 결측은 직전 값으로 잇는다(분석과 동일).

    candles: {HH:MM: (o,h,l,c)}   flow: {HH:MM: (call_amt, put_amt)}
    """

    def __init__(self, candles: Dict[str, Tuple[float, float, float, float]],
                 flow: Dict[str, Tuple[Optional[float], Optional[float]]],
                 horizon: Optional[str] = None, last_minute: str = "15:08"):
        keys = sorted(set(candles) | set(flow))
        keys = [k for k in keys if k <= last_minute]
        if horizon is not None:
            keys = [k for k in keys if k <= horizon]
        self.idx: List[str] = keys
        self.o, self.h, self.l, self.c = {}, {}, {}, {}
        self.call, self.put, self.sp = {}, {}, {}
        last_bar = None
        lc = lp = None          # 콜·풋은 **각자** 잇는다(pandas ffill 과 같다)
        for k in keys:
            if k in candles:
                last_bar = candles[k]
            if last_bar is not None:
                self.o[k], self.h[k], self.l[k], self.c[k] = last_bar
            if k in flow:
                if flow[k][0] is not None:
                    lc = flow[k][0]
                if flow[k][1] is not None:
                    lp = flow[k][1]
            if lc is not None and lp is not None:
                self.call[k], self.put[k] = lc, lp
                self.sp[k] = lc - lp

    def between(self, a: str, b: str) -> List[str]:
        return [k for k in self.idx if a <= k <= b]

    def last_at_or_before(self, t: str) -> Optional[str]:
        xs = [k for k in self.idx if k <= t]
        return xs[-1] if xs else None


def _plus_min(hhmm: str, n: int) -> str:
    t = _dt.datetime.strptime(hhmm, "%H:%M") + _dt.timedelta(minutes=n)
    return t.strftime("%H:%M")


# ── 맥점 ────────────────────────────────────────────────────────────────
def prepare_levels(rows: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """premarket_levels 행(stage→dict)에 구조맥점 가격 목록 `S` 와 파싱된 목록을 붙인다."""
    out = {}
    for st, r in rows.items():
        r = dict(r)
        up = json.loads(r.get("struct_up") or "[]")
        dn = json.loads(r.get("struct_down") or "[]")
        r["_up"], r["_dn"] = up, dn
        r["S"] = sorted(set(x[0] for x in up + dn))
        out[st] = r
    return out


def levels_at(L, t):
    st = "0930" if (t >= "09:31" and "0930" in L) else "0850"
    lv = sorted(set(L["0850"]["S"] + (L["0930"]["S"] if st == "0930" else [])))
    return L[st], lv


def targets(L, t, side, e):
    """[v2 · 2026-09-29 개정] 1차·최종 목표. 두 목표 모두 진입가에서 `T1_MIN_DIST` 이상 떨어진 맥점만 쓴다.

    v1(`targets_v1`)은 최종 목표 후보(가장 먼 구조맥점)를 **버퍼 −0.5 를 빼기 전에** 「진입 방향에
    있는가」로만 걸렀다. 맥점이 진입가 바로 너머(0.5pt 이내)면 버퍼 뒤 목표가 진입가 **뒤**로
    넘어가고, 1차·최종 맞바꿈이 그 값을 1차 자리에 넣어 1차 최소거리(2pt)도 우회했다.
    2026-09-29 MAIN R3 매수 4건(10:37·10:43·10:59·11:19)이 1차 1091.50 에 진입가 1091.04–1091.90
    — 1차 익절이 곧 본전(또는 손실)이었다. 개정 문서 `docs/신동거래/신동_개정_v2_1차목표역전_20260929.md`.
    """
    cur, _ = levels_at(L, t)
    z = L["0850"]
    t1c = [cur["dist_low"] if side < 0 else cur["dist_high"]]
    if t >= "09:31" and "0930" in L:
        for x in L["0930"]["_up"] + L["0930"]["_dn"]:
            if any((("OR저" in s) if side < 0 else ("OR고" in s)) for s in x[1]):
                t1c.append(x[0])
    t1c = [x for x in t1c if x is not None and side * (x - e) >= S.T1_MIN_DIST]
    t1 = (max(t1c) if side < 0 else min(t1c)) if t1c else None
    # v2: 최종 후보도 1차와 같은 최소거리로 거른다 — 없으면 80% 거리맥점 끝, 그것도 가까우면 없음
    far = [x for x in z["S"] if side * (x - e) >= S.T1_MIN_DIST]
    t2 = (min(far) if side < 0 else max(far)) if far else (z["low80_lo"] if side < 0 else z["high80_hi"])
    if t2 is not None and side * (t2 - e) < S.T1_MIN_DIST:
        t2 = None
    t1 = t1 - side * S.TP_BUF if t1 else None
    t2 = t2 - side * S.TP_BUF if t2 else None
    if t1 and t2 and side * (t2 - t1) < 0:
        t1, t2 = t2, t1
    if t1 is None:
        t1 = t2
    return t1, t2


def targets_v1(L, t, side, e):
    """🔒 `SD-2026-09-24-v1` 목표 — 동결. 조건부 러너 섀도(`mireuk_runner`, `RUNNER_VERSION` 별도
    사전등록)가 이 함수를 쓴다. 신동 v2 개정이 그 섀도를 조용히 바꾸지 않게 남겨 둔다 — 고치지 말 것."""
    cur, _ = levels_at(L, t)
    z = L["0850"]
    t1c = [cur["dist_low"] if side < 0 else cur["dist_high"]]
    if t >= "09:31" and "0930" in L:
        for x in L["0930"]["_up"] + L["0930"]["_dn"]:
            if any((("OR저" in s) if side < 0 else ("OR고" in s)) for s in x[1]):
                t1c.append(x[0])
    t1c = [x for x in t1c if x is not None and side * (x - e) >= S.T1_MIN_DIST]
    t1 = (max(t1c) if side < 0 else min(t1c)) if t1c else None
    far = [x for x in z["S"] if side * (x - e) > 0]
    t2 = (min(far) if side < 0 else max(far)) if far else (z["low80_lo"] if side < 0 else z["high80_hi"])
    if t2 is not None and side * (t2 - e) <= 0:
        t2 = None
    t1 = t1 - side * S.TP_BUF if t1 else None
    t2 = t2 - side * S.TP_BUF if t2 else None
    if t1 and t2 and side * (t2 - t1) < 0:
        t1, t2 = t2, t1
    if t1 is None:
        t1 = t2
    return t1, t2


def targets_x4(L, t, side, e):
    """[632차] SHADOW_X4NF 청산 — 1차 목표를 **진입 방향의 가장 가까운 구조맥점 −0.5** 로 당긴다.

    현행 1차(거리맥점 끝·OR 끝)가 12pt 넘게 멀어 본전 이동이 안 걸리던 것을 겨냥한다
    (R3 딥다이브 2026-09-28 §4-2 X4). 후보는 현행과 같은 `T1_MIN_DIST` 이상 떨어진 맥점뿐이고,
    현행 1차가 더 가까우면 그대로 둔다. 최종은 현행(없으면 1차).
    """
    t1, t2 = targets(L, t, side, e)
    _, lv = levels_at(L, t)
    near = [x for x in lv if side * (x - e) >= S.T1_MIN_DIST]
    if near:
        n = (min(near) if side > 0 else max(near)) - side * S.TP_BUF
        if t1 is None or side * (t1 - n) > 0:
            t1 = n
    if t2 is None:
        t2 = t1
    if t1 is not None and side * (t2 - t1) < 0:
        t2 = t1
    return t1, t2


# ── 손익 ────────────────────────────────────────────────────────────────
def leg_net(side, e, x, market_exit):
    pts = side * (x - e)
    net = (pts * S.PT_VALUE_KRW - (e + x) * S.PT_VALUE_KRW * S.COMMISSION_RATE
           - S.SLIP_TICK * S.PT_VALUE_KRW
           - (S.SLIP_TICK * S.PT_VALUE_KRW if market_exit else 0))
    return pts, net


# ── 거래 진행 ───────────────────────────────────────────────────────────
def run_trade(d: DayFrame, side, t0, stop, t1, t2, e2=False,
              trail: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
    """두 다리(1차·최종)를 봉마다 진행한다. horizon 에서 멈추면 status=OPEN.

    e2=False : MAIN — 1차 익절 즉시 공통 손절을 본전으로(같은 봉의 최종 다리도 그 손절로 검사)
    e2=True  : SHADOW E2 — 최종 다리 손절은 1차–최종 중간 지점 도달 뒤에야 본전
    trail=(act, dist) : [632차 후속] SHADOW_TR44 — 진입가 대비 유리한 극값이 act pt 이상이면
               공통 손절 = 극값 − dist(단조). 그 봉 극값은 **다음 봉부터** 반영한다(봉 내부 경로를
               모르므로 보수적). 1차 익절 때는 손절이 본전보다 불리할 때만 본전으로 올린다.
               None 이면 이 경로는 한 줄도 타지 않는다(MAIN 과 같다).
    """
    e = d.c[t0]
    legs = [{"leg": 1, "tp": t1, "open": True}, {"leg": 2, "tp": t2, "open": True}]
    st = stop            # MAIN 공통 손절
    st2 = stop           # SHADOW 최종 다리 손절
    half = None
    best = e             # 트레일용 유리한 극값
    bars = [k for k in d.idx if t0 < k <= S.TIME_EXIT]
    for t in bars:
        h, l = d.h[t], d.l[t]
        for g in legs:
            if not g["open"]:
                continue
            cur = st if not e2 else (stop if g["leg"] == 1 else st2)
            if (h >= cur) if side < 0 else (l <= cur):
                g.update(open=False, ts=t, px=cur, mkt=True,
                         reason=("BE" if cur == e else
                                 ("TR" if trail is not None and side * (cur - stop) > 0 else "SL")))
                continue
            if g["tp"] is not None and ((l <= g["tp"]) if side < 0 else (h >= g["tp"])):
                g.update(open=False, ts=t, px=g["tp"], mkt=False,
                         reason=("TP1" if g["leg"] == 1 else "TP2"))
                if not e2:
                    if trail is None or side * (e - st) > 0:
                        st = e
                elif g["leg"] == 1:
                    if t2 is not None:
                        half = t1 + (t2 - t1) / 2.0
                    else:
                        st2 = e
        if e2 and half is not None and ((l <= half) if side < 0 else (h >= half)):
            st2 = e
            half = None
        if not any(g["open"] for g in legs):
            break
        if trail is not None:
            best = max(best, h) if side > 0 else min(best, l)
            if side * (best - e) >= trail[0]:
                cand = best - side * trail[1]
                if side * (cand - st) > 0:
                    st = cand
    horizon = d.idx[-1] if d.idx else None
    # 시간 청산은 15:05 봉이 **도착한 뒤**에만 확정한다 — 그 전은 보유 중(OPEN)이다.
    if any(g["open"] for g in legs) and horizon is not None and horizon >= S.TIME_EXIT:
        tx = d.last_at_or_before(S.TIME_EXIT)
        for g in legs:
            if g["open"]:
                g.update(open=False, ts=tx, px=d.c[tx], mkt=True, reason="TIME")
    for g in legs:
        if not g["open"]:
            g["pts"], g["net"] = leg_net(side, e, g["px"], g["mkt"])
    closed = [g for g in legs if not g["open"]]
    # 지금 살아 있는 손절선 — 차트가 보유 중 손절선을 그릴 때 쓴다
    stop_now = st if not e2 else (st2 if not legs[0]["open"] else stop)
    return {
        "side": side, "entry_ts": t0, "entry_px": e, "stop_init": stop,
        "t1": t1, "t2": t2, "legs": legs,
        "status": "OPEN" if any(g["open"] for g in legs) else "CLOSED",
        "exit_ts": max(g["ts"] for g in closed) if len(closed) == len(legs) else None,
        "stop_now": stop_now,
    }


# ── 하루 ────────────────────────────────────────────────────────────────
def run_day(d: DayFrame, L, variant: str = "MAIN") -> Dict[str, Any]:
    """하루 판정. 반환: {"decision": {...}, "trades": [...]}."""
    e2 = variant == "SHADOW_E2F2"
    # [719차] SHADOW_F2 = SHADOW_V2(트레일 없음) + R3 F2 만(E2 없음) — 분석명 「V2+F2」. F2 판정은 E2F2 와 같은 줄을 쓴다.
    f2 = variant in ("SHADOW_E2F2", "SHADOW_F2")
    # [632차] SHADOW_X4NF — R3 만 바꾼다: 1차 목표 X4 + 같은 맥점 방향 뒤집기(flip) 금지. R2 는 MAIN 과 같다.
    # [MW0602 598차] SHADOW_X4NFA — X4NF 전부 + 깨진 맥점 진입 금지(A). R2 는 MAIN 과 같다.
    broken_guard = variant == "SHADOW_X4NFA"
    x4nf = variant == "SHADOW_X4NF" or broken_guard
    # [632차 후속] SHADOW_TR44 — MAIN 과 같은 진입·목표에 R3 만 트레일(+4pt 발동 · 4pt 간격). 비교 기록용.
    # [v3 · 699차] MAIN 이 그 규칙을 승계했다(spec.MAIN_TRAIL). SHADOW_V2 = 트레일 없는 구 MAIN(되돌림 기준).
    #   SHADOW_TR44 이름은 종료됐지만 재현 테스트·과거 행 복기용으로 계속 알아듣는다(= v3 MAIN · v4 SHADOW_V3 와 같다).
    # [v4 · 718차] MAIN = v3 MAIN(트레일 4/4) + R3 F2X 방향 필터(구 분석명 ②SHADOW_F2X). SHADOW_V3 = 필터 없는 v3 MAIN
    #   (되돌림 기준). ATRS · R2D7 은 등록 정의(「v3 MAIN 그대로 + …」)대로 F2X 를 쓰지 않는다.
    f2x = variant == "MAIN"
    if variant == "SHADOW_TR44":
        tr44 = (S.TR44_ACT, S.TR44_DIST)
    elif variant in ("MAIN", "SHADOW_V3", "SHADOW_ATRS", "SHADOW_R2D7"):
        tr44 = S.MAIN_TRAIL
    else:
        tr44 = None
    # [700차] SHADOW_ATRS = v3 MAIN 그대로 + R3 초기 손절만 k×ATR14(08:50 산출) 로 넓힘(R2 무변경)
    atrs = variant == "SHADOW_ATRS"
    atr14 = None
    if atrs:
        _a = (L.get("0850") or {}).get("atr14")
        atr14 = float(_a) if isinstance(_a, (int, float)) and _a > 0 else None
    lvl_side: Dict[float, int] = {}     # 맥점 → 그 맥점에서 마지막으로 **진입한** 방향
    dec: Dict[str, Any] = {"pm_sp": None, "bias": None, "r2": None, "r2_ts": None,
                           "notes": []}
    trades: List[Dict[str, Any]] = []
    if "0850" not in L:
        dec["notes"].append("08:50 맥점 없음 — 판정 불가")
        return {"decision": dec, "trades": trades}

    # R1
    pm = [k for k in d.idx if k <= S.PREMARKET_LAST and k in d.sp]
    if not pm:
        dec["bias"] = 0
        dec["notes"].append("장전 흐름 미수집 — 방향 보류")
    else:
        s = d.sp[pm[-1]]
        dec["pm_sp"] = s
        dec["bias"] = 0 if abs(s) < S.BIAS_MIN else (-1 if s > 0 else 1)
    bias = dec["bias"]
    # [714차] SHADOW_R2D7 — R2 확정 창만 늦춘다(기준·시작·끝). R1·R3·청산은 MAIN 과 같다.
    conf_base, conf_start, conf_end = ((S.R2D7_CONF_BASE, S.R2D7_CONF_START, S.R2D7_CONF_END)
                                       if variant == "SHADOW_R2D7"
                                       else (S.CONF_BASE, S.CONF_START, S.CONF_END))
    busy = conf_base            # 이 분까지는 신규 진입 없음(보유 중이면 청산 시각)

    # R2
    if bias:
        if conf_base not in d.sp:
            dec["r2"] = "PENDING" if (not d.idx or d.idx[-1] < conf_base) else "NO_BASE"
        else:
            bc, bp, bs = d.call[conf_base], d.put[conf_base], d.sp[conf_base]
            conf = None
            for t in d.between(conf_start, conf_end):
                if t not in d.sp or t not in d.c:    # [598차] 봉 없는 분엔 진입가가 없다
                    continue
                dc, dp, ds = d.call[t] - bc, d.put[t] - bp, d.sp[t] - bs
                if bias < 0 and dc > 0 and dp <= 0 and ds >= S.CONF_MIN:
                    conf = t
                    break
                if bias > 0 and dc < 0 and dp >= 0 and ds <= -S.CONF_MIN:
                    conf = t
                    break
            if conf:
                dec["r2"], dec["r2_ts"] = "CONFIRMED", conf
                # [MW0602 598차] 봉이 없는 분(예: 09:00 1분봉 결손 — 2026-09-29 실측)은 흐름만 있고
                #   h/l 가 없다. 예전엔 KeyError 로 그날 재생 전체가 죽었다(첫 실패만 WARNING, 이후 억제).
                #   봉이 있는 분만 쓴다 — 정상일(봉 전부 있음)은 결과가 한 원도 바뀌지 않는다.
                seg = [k for k in d.between(conf_base, conf) if k in d.h]
                ex = (max(d.h[k] for k in seg) + S.OR_STOP_BUF if bias < 0
                      else min(d.l[k] for k in seg) - S.OR_STOP_BUF)
                e = d.c[conf]
                t1, t2 = targets(L, conf, bias, e)
                tr = run_trade(d, bias, conf, ex, t1, t2, e2=e2)
                tr.update(rule="R2", touch_level=None)
                trades.append(tr)
                busy = tr["exit_ts"] or "99:99"
            else:
                dec["r2"] = "PENDING" if (d.idx and d.idx[-1] < conf_end) else "NONE"

    # R3 — [v4 · 718차] 인과 선택: **확인(진입) 분이 가장 이른 신호**가 자리를 갖는다(동률이면 먼저 터치한 것).
    #   v3 까지는 터치 시각 순으로 훑어, 먼저 터치·나중 확인된 신호가 그사이 확인·진입한 다른 신호의 자리를
    #   **소급 점유**했다 → 라이브에서 이미 진입한 거래가 다음 분 재생에서 사라짐(RETRACTED, v3 4일 14건 전부).
    #   후보 계산(터치 → 반전 확인 → 손절)은 v3 와 한 줄도 다르지 않다 — 고른 순서만 바뀐다.
    #   근거 `docs/미륵이고도화3/신동2/신동2_철회신호_메커니즘·개선대책_MW0601-20261026.md`.
    #   후보는 busy 와 무관하므로 분마다 한 번만 계산한다(X4NF flip 금지만 선택 시점의 lvl_side 로 본다).
    f2x_dir = f2x_direction(d) if f2x else None
    pos = {k: i for i, k in enumerate(d.idx)}
    cands = []
    for t in [k for k in d.idx if S.R3_START <= k <= S.NEW_ENTRY_END]:
        if t not in d.c:
            continue
        _, lv = levels_at(L, t)
        h, l, c = d.h[t], d.l[t], d.c[t]
        sig = None
        for L0 in lv:
            if L0 - S.TOUCH_NEAR <= h <= L0 + S.TOUCH_FAR and c < L0:
                sig = (-1, L0)
                break
            if L0 - S.TOUCH_FAR <= l <= L0 + S.TOUCH_NEAR and c > L0:
                sig = (1, L0)
                break
        if not sig:
            continue
        side, L0 = sig
        if f2:
            if t not in d.sp:
                continue
            base = d.sp.get(S.CONF_BASE)
            trend = -1 if (base is not None and d.sp[t] - base > 0) else 1
            if side != trend:
                continue
        if f2x_dir is not None:
            # [v4 · 718차] MAIN F2X — 수급(F2 ±F2X_SP_BAND)과 가격 추세(EMA 빠름−느림)가 **일치할 때만** 그 방향만.
            #   불일치·판정 불가(0)면 필터 없이 통과한다.
            v = f2x_dir.get(t, 0)
            if v != 0 and side != v:
                continue
        endw = min(S.NEW_ENTRY_END, _plus_min(t, S.REV_WIN_MIN))
        ent = None
        # [v4] 모든 분의 후보를 계산하므로 색인 조각 + 누적 극값으로 훑는다(v3 의 between() 반복 스캔과 같은 값).
        i0 = pos[t]
        lo = hi = None
        for j in range(i0, len(d.idx)):
            u = d.idx[j]
            if u > endw:
                break
            if u not in d.sp:
                continue
            x = d.sp[u]
            lo = x if lo is None else min(lo, x)
            hi = x if hi is None else max(hi, x)
            if side < 0 and x - lo >= S.REV_MIN:
                ent, j_ent = u, j
                break
            if side > 0 and hi - x >= S.REV_MIN:
                ent, j_ent = u, j
                break
        if not ent:
            continue
        e = d.c[ent]
        if broken_guard and side * (e - L0) <= 0:
            continue                    # 반전 대기 중 가격이 맥점을 다시 넘어감 — 되밀림 신호 무효
        span = d.idx[i0:j_ent + 1]
        stop = (max(L0 + S.LV_STOP_BUF, max(d.h[k] for k in span) + S.EXT_STOP_BUF) if side < 0
                else min(L0 - S.LV_STOP_BUF, min(d.l[k] for k in span) - S.EXT_STOP_BUF))
        if side * (e - stop) <= 0:
            continue
        if atrs:
            # [700차] SHADOW_ATRS — R3 초기 손절을 진입가 ∓ k×ATR14 로 넓힌다(현행보다 좁히지 않는다).
            #   ATR14 가 없으면 현행 손절 그대로 — 폴백 사실을 notes 에 한 번 남긴다(계측 4원칙 ④).
            if atr14 is not None:
                wide = e - side * S.R3_ATR_STOP_K * atr14
                if side * (stop - wide) > 0:
                    stop = wide
            elif "ATR14 없음 — R3 손절 폴백(현행 맥점 손절)" not in dec["notes"]:
                dec["notes"].append("ATR14 없음 — R3 손절 폴백(현행 맥점 손절)")
        cands.append((ent, t, side, L0, e, stop))
    cands.sort(key=lambda x: (x[0], x[1]))
    while True:
        pick = None
        for x in cands:
            ent, t, side, L0 = x[0], x[1], x[2], x[3]
            if t <= busy:
                continue
            if x4nf and lvl_side.get(L0, side) != side:
                continue                # 같은 맥점에서 방향 뒤집기 — 박스권 양쪽 잡기 방지
            pick = x
            break
        if pick is None:
            break
        ent, t, side, L0, e, stop = pick
        t1, t2 = (targets_x4 if x4nf else targets)(L, ent, side, e)
        tr = run_trade(d, side, ent, stop, t1, t2, e2=e2, trail=tr44)
        tr.update(rule="R3", touch_level=L0, touch_ts=t)
        trades.append(tr)
        lvl_side[L0] = side
        busy = tr["exit_ts"] or "99:99"
    return {"decision": dec, "trades": trades}


def _ema(series: Dict[str, float], keys: List[str], n: int) -> Dict[str, float]:
    """분 순서 EMA(α = 2/(n+1)). 값이 없는 분은 직전 EMA 를 잇는다 — t 까지의 값만 쓴다(인과)."""
    a = 2.0 / (n + 1)
    out, v = {}, None
    for k in keys:
        if k in series:
            v = series[k] if v is None else v + a * (series[k] - v)
        if v is not None:
            out[k] = v
    return out


def f2x_direction(d: DayFrame) -> Dict[str, int]:
    """[v4 · 718차] F2X 방향(분 → −1 매도 · +1 매수 · 0 판정 불가).

    수급: 09:00 대비 콜−풋 변화 Δ — |Δ| ≤ F2X_SP_BAND 이면 0, Δ>0 이면 −1(개인 콜 매수 쏠림 역추종).
    가격: 종가 EMA(F2X_EMA_FAST) − EMA(F2X_EMA_SLOW) 의 부호(0 이면 0).
    둘이 같고 0 이 아닐 때만 그 방향, 아니면 0. 분석 `f2_filters.build` 「조합: F2±50 ∧ 가격 EMA20−60」과 같다.
    """
    base = d.sp.get(S.CONF_BASE)
    fast = _ema(d.c, d.idx, S.F2X_EMA_FAST)
    slow = _ema(d.c, d.idx, S.F2X_EMA_SLOW)
    out: Dict[str, int] = {}
    for k in d.idx:
        a = 0
        if base is not None and k in d.sp:
            x = d.sp[k] - base
            a = 0 if abs(x) <= S.F2X_SP_BAND else (-1 if x > 0 else 1)
        b = 0
        if k in fast and k in slow:
            y = fast[k] - slow[k]
            b = 0 if y == 0 else (1 if y > 0 else -1)
        out[k] = a if (a == b and a != 0) else 0
    return out


def trade_net(tr) -> float:
    return sum(g.get("net", 0.0) for g in tr["legs"] if not g["open"])
