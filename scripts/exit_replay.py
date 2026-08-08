# scripts/exit_replay.py
"""[MW0601 440차, 캠페인 47 해제작업] 청산 사다리 재생기 — 라이브 미러링 단일 소스.

무엇을 고치는가
----------------
기하 A/B 채널들([3-B]/[23-B]/[25]/[25-B]/[46])이 공유하던 재생기는 세 가정을
갖고 있었고, [47] `sim_fidelity_gate`가 그 가정 때문에 **총합 부호까지 뒤집힌다**는
것을 실측해(시뮬 -24.17 vs 실제 +34.89 pt, n=119/16일) 하위 채널 판정을 전부
정지시켰다.

    ① 1분봉 고저가만 본다                    ← 이 모듈도 동일 (틱 데이터가 DB에 없다)
    ② TP1(또는 TP2)에 닿으면 거기서 종료한다  ← **이 모듈이 고친다**
    ③ TP3·4단계 트레일링을 모델링하지 않는다  ← **이 모듈이 고친다**

[47]이 사전등록한 해제 조건이 바로 "재생기에 TP3·트레일링을 편입해 재현이
회복되면 자동 PASS"다. 이 모듈은 그 편입을 수행한다.

무엇을 모델링하나 — `main.py::_ts_check_exit_triggers()` 순서 그대로
--------------------------------------------------------------------
매 분봉마다:

    1. 4단계 트레일링 갱신    compute_trailing_stop_tier()  ← **라이브 함수를 import**
    2. 하드스톱 (전량)        종가 히트 = 갱신 후 스톱 / 봉중 히트 = 갱신 전 스톱
    3. 손절1차 조기축소       LOSS_TIER1 (qty>=2, 50% 축소, 1회)
    4. TP1 / TP2 / TP3        PARTIAL_EXIT_RATIOS 분할. qty=1 TP1은 **보호전환**
    5. 15:10 강제청산

`compute_trailing_stop_tier`는 361차가 이미 "라이브 트레일링과 계측용 시뮬레이션이
복붙으로 갈라져 드리프트하는 것을 막기 위해" 순수함수로 분리해 둔 것이다. 이 모듈은
그 의도를 그대로 따른다 — **트레일링 로직을 다시 쓰지 않는다.**

왜 qty=1 보호전환이 중요한가
-----------------------------
qty=1은 TP1에서 물리적 분할이 불가능해 `arm_tp1_single_contract_with_mode()`가
스톱만 `entry ± ATR×TP1_PROTECT_ATR_LOCK_MULT`로 조인다. 구 재생기는 이 경우
"TP1 가격에 전량 청산"으로 계상했는데, 실제로는 **포지션이 계속 살아 있다** —
그 뒤 되돌리면 lock에서 털리고(오늘 실측 중앙값 수십 초), 더 가면 트레일링이
받는다. 구 재생기는 이 두 결말을 **둘 다** TP1 확정이익으로 계상했다.

⚠ 이 모듈이 **고치지 않는** 것 (정직한 한계)
---------------------------------------------
- **틱 경로**: 라이브는 `TickTP1`·`TickStop-S0C`로 봉 중간에 나간다. DB에 틱이
  없어 재현 불가다. 0807 호가로그(224,812틱)로 별도 확인한 결과, 봉 단위 가정만으로도
  현행 재현이 +62% 어긋났다 — 즉 ①은 여전히 남은 오차원이다.
- **신호소멸청산**: 라이브는 **섀도 전용**이라(main.py 3.5순위 주석: "실제 청산은
  하지 않는다(shadow-only)") 모델링 대상이 아니다. [47] 독스트링이 이것을 미모델
  항목으로 적은 것은 부정확하다 — 라이브에 없는 것은 재생기에도 없어야 맞다.
- **체결가 관례**: 스톱 청산가로 `stop_px`를 쓴다(라이브의 `min(stop, bar_high)`가
  아니다). 432차 후속2가 그 라이브 식을 "체결 불가능한 가격을 체결로 계상"으로
  지목했고 [48] `bar_stop_path_watch`가 따로 보고 있다 — 재생기가 그 결함을
  따라가면 안 된다.
- **봉내 도달순서**: 스톱·TP가 같은 봉에 있으면 **스톱 우선**(캠페인 공통 관례).

[MW0601 441차] TP 체결가를 세대별로 갈랐다 — 편향 1건 제거
--------------------------------------------------------
`tp_trigger="close"` 세대(~2026-08-02)의 TP 체결가를 목표가에서 **트리거 봉의
종가**로 바꿨다. 그 세대의 트리거 조건 자체가 "종가가 목표가를 넘었다"이므로
체결을 목표가로 적는 것은 자기모순이었고, 넘어선 만큼(이익 방향 오버슈트)이
전부 사라져 **시뮬이 구조적으로 이익을 과소계상**했다.

실측 근거(2026-07-05~08-07, TP2 완주 22건): 실제 체결거리가 재생 목표거리를
**전건 초과**했고(합 +18.19pt, 최대 +2.47pt), 큰 초과분(+1.2~2.5pt)은 전부
pre 세대였다. 이 수정으로 [47] 게이트의 재현 격차가 **+21.56pt 회복**된다.

⚠ **스톱에는 같은 수정을 하지 않는다.** pre 세대에도 `하드스톱(틱)` 레그가
실존하므로(틱 스톱 경로는 원래 있었다) 스톱까지 종가 체결로 바꾸면 −23.40pt가
반대 방향으로 얹혀 재현이 오히려 나빠진다 — 441차가 실측으로 확인했다.
⚠ 이 수정은 **자유 파라미터를 도입하지 않는다.** 종가는 데이터이지 튜닝값이
아니며, 어느 세대에 적용할지는 이미 사전등록된 `replay_regime`이 정한다.

⚠ 사전등록 정직성
------------------
이 모듈은 [47]을 **PASS로 만들기 위해** 쓰였다. 그러므로 자유 파라미터를 두지
않는다 — 모든 배수·비율은 `config/settings.py`와 라이브 함수에서 읽는다. 이 파일이
새로 도입하는 수치 상수는 **하나도 없다**. 재현이 회복되지 않으면 그대로 SUSPEND가
유지되며, 그것이 정상 동작이다.
"""
from __future__ import annotations

import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.constants import POSITION_LONG, POSITION_SHORT  # noqa: E402
from config.settings import (  # noqa: E402
    ATR_STOP_MULT, ATR_TP1_MULT, ATR_TP2_MULT, ATR_TP3_MULT,
    ATR_HORIZON_TP1_MULT,
    HURST_REGIME_ATR_MULT, HURST_REGIME_ATR_MULT_ENABLED,
    LOSS_TIER1_ENABLED, LOSS_TIER1_STOP_FRACTION, LOSS_TIER1_CUT_RATIO,
    PARTIAL_EXIT_RATIOS,
    TP1_PROTECT_ATR_LOCK_MULT, TP1_PROTECT_PLUS_ALPHA_PTS,
    VALIDATION_CAMPAIGN,
)
# 361차가 "복붙 금지"를 위해 순수함수로 뽑아 둔 라이브 트레일링 — 재구현하지 않는다.
from strategy.position.position_tracker import compute_trailing_stop_tier  # noqa: E402

_TS_FMT = "%Y-%m-%d %H:%M:%S"
_FORCE_HHMM = "15:10"       # 절대원칙 §1 — 오버나이트 금지
_MAX_HOLD_MIN = 360         # 재생 상한(분). 정상적으로는 15:10 컷이 먼저 걸린다


# ──────────────────────────────────────────────────────────────────────────
# 기하 — 라이브 `PositionTracker._recalculate_levels()`와 같은 산식
# ──────────────────────────────────────────────────────────────────────────
def geometry(horizon, hurst_bucket, atr, *,
             stop_mult=None, tp1_mult=None, tp2_mult=None, tp3_mult=None):
    """(stop_pts, tp1_pts, tp2_pts, tp3_pts) — 전부 진입가로부터의 **절대 거리**.

    override가 주어지면 그 ATR 배수로 대체한다(A/B 변형용). hurst 레짐 배수는
    라이브와 동일하게 stop/tp1/tp2에만 곱한다 — TP3에는 곱하지 않는다
    (`_recalculate_levels()`가 tp3만 `ATR_TP3_MULT` 단독으로 쓴다).
    """
    m = (HURST_REGIME_ATR_MULT.get(hurst_bucket or "", {})
         if HURST_REGIME_ATR_MULT_ENABLED else {})
    _stop = ATR_STOP_MULT if stop_mult is None else stop_mult
    _tp1_base = ATR_HORIZON_TP1_MULT.get(horizon, ATR_TP1_MULT)
    _tp1 = _tp1_base if tp1_mult is None else tp1_mult
    _tp2 = ATR_TP2_MULT if tp2_mult is None else tp2_mult
    _tp3 = ATR_TP3_MULT if tp3_mult is None else tp3_mult
    return (
        atr * _stop * m.get("stop", 1.0),
        atr * _tp1 * m.get("tp1", 1.0),
        atr * _tp2 * m.get("tp2", 1.0),
        atr * _tp3,
    )


_REGIME = (VALIDATION_CAMPAIGN.get("sim_fidelity_gate", {}) or {}).get(
    "replay_regime") or (VALIDATION_CAMPAIGN.get("replay_regime") or {})


def regime_for(entry_ts):
    """진입 시각 → 그 날의 코드 세대 규칙 {"tp_trigger", "protect_mode"}.

    경계는 `config/settings.py VALIDATION_CAMPAIGN["replay_regime"]`에 사전등록돼
    있다(MW0601 TRADE 로그 전수 집계로 확정). 상세 근거는 그쪽 주석 참조.
    """
    start = str(_REGIME.get("tick_era_start") or "2026-08-03")
    pre = dict(_REGIME.get("pre") or {"tp_trigger": "close", "protect_mode": "breakeven"})
    post = dict(_REGIME.get("post") or {"tp_trigger": "envelope", "protect_mode": "atr_profit"})
    return post if str(entry_ts)[:10] >= start else pre


def _protect_offset(mode, atr):
    """qty=1 TP1 보호전환 offset(pt) — 라이브
    `arm_tp1_single_contract_with_mode()`와 같은 분기."""
    m = str(mode or "atr_profit").strip().lower()
    if m == "breakeven":
        return 0.0
    if m == "breakeven_plus":
        return max(float(TP1_PROTECT_PLUS_ALPHA_PTS), 0.0)
    return max(float(atr) * float(TP1_PROTECT_ATR_LOCK_MULT), 0.0)


def stage_plan(total_qty):
    """라이브 `PositionTracker.get_stage_plan()`과 동일한 33/33/34 배분."""
    total_qty = int(total_qty or 0)
    if total_qty <= 0:
        return (0, 0, 0)
    if total_qty == 1:
        return (1, 0, 0)
    if total_qty == 2:
        return (1, 1, 0)
    raw = [total_qty * r for r in PARTIAL_EXIT_RATIOS]
    plan = [int(v) for v in raw]
    rem = total_qty - sum(plan)
    order = sorted(range(3), key=lambda i: (raw[i] - plan[i], i == 2, -i), reverse=True)
    for i in order:
        if rem <= 0:
            break
        plan[i] += 1
        rem -= 1
    return tuple(plan)


# ──────────────────────────────────────────────────────────────────────────
# 본체
# ──────────────────────────────────────────────────────────────────────────
def replay(bars_by_ts, entry_ts, direction, entry_px, qty, atr,
           horizon=None, hurst_bucket=None, *,
           stop_mult=None, tp1_mult=None, tp2_mult=None, tp3_mult=None,
           lock_offset_pts=None, max_hold_min=_MAX_HOLD_MIN,
           tp_trigger="envelope", protect_mode="atr_profit"):
    """청산 사다리를 분봉으로 재생한다.

    Args:
        bars_by_ts: {ts_str: (high, low, close)} — 1분봉
        direction : "LONG" / "SHORT"
        qty       : 진입 계약수 (분할 스케줄이 여기서 갈린다)
        lock_offset_pts: qty=1 TP1 보호전환 offset(pt). None이면 `protect_mode`가
                         정한 라이브 현행값. [25] 채널이 이 축을 A/B한다.
        tp_trigger: TP 도달 판정 기준 — **코드 세대에 따라 다르다**(아래 참조)
                    "envelope" = 봉 고저가 (틱 TP 경로가 있는 세대)
                    "close"    = 봉 종가만 (분당 파이프라인만 있던 세대)
        protect_mode: qty=1 TP1 보호전환 모드 — "atr_profit" / "breakeven" /
                    "breakeven_plus". 역시 코드 세대에 따라 다르다.

    ⚠ **체제(코드 세대)를 섞지 말 것** — 440차 실측
    ------------------------------------------------
    두 인자를 고정값으로 두면 과거를 **다른 시스템의 규칙으로** 재생하게 된다.
    MW0601 TRADE 로그 전수 집계상 경계는 **2026-08-03**으로 깨끗하다:

        ~2026-07-31 : TickTP1 0건 / protect_mode=breakeven 전량
        2026-08-03~ : TickTP1 상시 / protect_mode=atr_profit

    실제 사고 사례(2026-07-21 09:30 LONG qty=1): 그날은 종가 트리거·breakeven이라
    라이브가 09:36 종가 1040.00에서 본전 스톱을 걸고 TP2까지 완주해 **+8.82pt**를
    냈다. 그런데 envelope+atr_profit으로 재생하면 09:32 봉고가(1039.64)에서 조기
    arm → 09:33 저가가 lock(1037.76)을 때려 **+1.24pt STOP**으로 끝난다. 격차 한
    건이 -7.64pt다. [25]가 이미 `mw0601_sample_start: "2026-08-03"`으로 같은
    경계를 등록해 두고 있다 — 이 인자들은 그 등록과 같은 사실을 가리킨다.

    Returns:
        {"pts": 계약가중 총 손익(pt·계약), "qty": 진입수량,
         "pts_per_contract": pts/qty, "outcome": 최종 결말 라벨,
         "events": [(ts, kind, qty, price, pts)], "hold_min": 보유 분,
         "reached": {"tp1": bool, "tp2": bool, "tp3": bool, "trail": bool}}
        재생 불가(봉 없음)면 None.
    """
    is_long = str(direction).upper() == "LONG"
    sgn = 1 if is_long else -1
    pos_dir = POSITION_LONG if is_long else POSITION_SHORT
    qty = int(qty or 1)
    if qty <= 0 or not atr or atr <= 0:
        return None

    stop_pts, tp1_pts, tp2_pts, tp3_pts = geometry(
        horizon, hurst_bucket, float(atr),
        stop_mult=stop_mult, tp1_mult=tp1_mult,
        tp2_mult=tp2_mult, tp3_mult=tp3_mult)

    stop_px = entry_px - sgn * stop_pts
    tp_px = (entry_px + sgn * tp1_pts,
             entry_px + sgn * tp2_pts,
             entry_px + sgn * tp3_pts)
    # 손절1차 — entry~stop 거리의 LOSS_TIER1_STOP_FRACTION 지점
    lt1_px = entry_px - sgn * stop_pts * LOSS_TIER1_STOP_FRACTION

    plan = stage_plan(qty)
    targets = (plan[0], plan[0] + plan[1], plan[0] + plan[1] + plan[2])

    remaining = qty
    closed = 0
    realized = 0.0                     # pt·계약 누계
    anchor = 0.0                       # 트레일링 앵커 (0이면 미개시)
    stage_done = [False, False, False]
    lt1_done = False
    tp1_armed = False                  # qty=1 보호전환 여부
    events = []
    reached = {"tp1": False, "tp2": False, "tp3": False, "trail": False}

    base = datetime.datetime.strptime(entry_ts, _TS_FMT).replace(second=0)
    outcome = None
    last_close = entry_px
    hold_min = 0

    for k in range(1, int(max_hold_min) + 1):
        cur = base + datetime.timedelta(minutes=k)
        key = cur.strftime(_TS_FMT)
        bar = bars_by_ts.get(key)
        if bar is None:
            # 결손봉은 건너뛴다. 날짜가 바뀌면 중단(오버나이트 없음).
            if cur.date() != base.date():
                break
            continue
        hi, lo, cl = bar
        last_close = cl
        hold_min = k

        # 15:10 강제청산 — 절대원칙 §1. 이 봉을 평가하기 **전에** 끊는다.
        if cur.strftime("%H:%M") >= _FORCE_HHMM:
            realized += sgn * (cl - entry_px) * remaining
            events.append((key, "FORCED", remaining, cl, sgn * (cl - entry_px)))
            remaining = 0
            outcome = "FORCED"
            break

        # ── 1. 4단계 트레일링 (라이브 함수) ─────────────────────────────
        prev_stop = stop_px
        anchor, stop_px = compute_trailing_stop_tier(
            entry_px, pos_dir, float(atr), cl, anchor, stop_px)
        if abs(stop_px - prev_stop) > 1e-9:
            reached["trail"] = True
        # 유령 하드스톱 가드(423차) — 이 봉 안에서 스톱이 조여졌으면 봉중 판정을
        # 억제하고 종가 기준만 본다. 라이브 `is_stop_hit_intrabar(bar_start=...)`.
        tightened_this_bar = abs(stop_px - prev_stop) > 1e-9

        # ── 2. 하드스톱 (전량) ─────────────────────────────────────────
        # 종가 히트는 갱신 후 스톱, 봉중 히트는 갱신 전 스톱 — 라이브와 동일.
        close_hit = (cl <= stop_px) if is_long else (cl >= stop_px)
        intrabar_hit = ((lo <= prev_stop) if is_long else (hi >= prev_stop))
        if tightened_this_bar:
            intrabar_hit = False
        if close_hit or intrabar_hit:
            eff = stop_px if close_hit else prev_stop
            realized += sgn * (eff - entry_px) * remaining
            events.append((key, "STOP", remaining, eff, sgn * (eff - entry_px)))
            remaining = 0
            outcome = "STOP"
            break

        # ── 3. 손절1차 조기축소 (qty>=2, 1회) ──────────────────────────
        if (LOSS_TIER1_ENABLED and not lt1_done and remaining > 1):
            lt1_hit = (lo <= lt1_px) if is_long else (hi >= lt1_px)
            if lt1_hit:
                cut = max(1, int(round(remaining * LOSS_TIER1_CUT_RATIO)))
                cut = min(cut, remaining - 1)      # 전량청산 금지
                if cut > 0:
                    realized += sgn * (lt1_px - entry_px) * cut
                    events.append((key, "LOSS_TIER1", cut, lt1_px,
                                   sgn * (lt1_px - entry_px)))
                    remaining -= cut
                    closed += cut
                lt1_done = True
                # 라이브는 발동한 틱에 pending이 걸려 아래 TP 체크를 건너뛴다.
                continue

        # ── 4. TP1 / TP2 / TP3 ────────────────────────────────────────
        for stage in (1, 2, 3):
            if stage_done[stage - 1] or remaining <= 0:
                continue
            px = tp_px[stage - 1]
            # 코드 세대에 따라 TP 트리거 기준이 다르다 — 독스트링 ⚠ 참조.
            if tp_trigger == "close":
                hit = (cl >= px) if is_long else (cl <= px)
            else:
                hit = (hi >= px) if is_long else (lo <= px)
            if not hit:
                continue
            reached["tp%d" % stage] = True
            # 체결가 — `close` 세대는 **종가로 체결된다**(441차 수정).
            # 그 세대의 트리거 조건 자체가 "종가가 목표가를 넘었다"이므로 체결을
            # 목표가로 적으면 넘어선 만큼(이익 방향 오버슈트)이 통째로 사라진다.
            # `envelope` 세대는 틱이 목표가를 스치는 즉시 나가므로 목표가가 맞다.
            fill = cl if tp_trigger == "close" else px

            # qty=1 TP1 → 물리적 청산이 아니라 **보호전환**
            if stage == 1 and qty == 1:
                off = (_protect_offset(protect_mode, float(atr))
                       if lock_offset_pts is None else float(lock_offset_pts))
                protected = entry_px + sgn * max(off, 0.0)
                # 라이브: 기존 스톱보다 불리해지면 채택하지 않는다
                if sgn * (protected - stop_px) > 0:
                    stop_px = protected
                    tightened_this_bar = True
                tp1_armed = True
                stage_done[0] = True
                events.append((key, "TP1_ARM", 0, fill, 0.0))
                continue

            need = max(0, targets[stage - 1] - closed)
            exit_qty = min(remaining, need)
            is_full = (exit_qty >= remaining) or stage >= 3
            send = remaining if is_full else exit_qty
            if send <= 0:
                stage_done[stage - 1] = True
                continue
            realized += sgn * (fill - entry_px) * send
            events.append((key, "TP%d" % stage, send, fill, sgn * (fill - entry_px)))
            remaining -= send
            closed += send
            stage_done[stage - 1] = True
            if remaining <= 0:
                outcome = "TP%d" % stage
                break
        if remaining <= 0:
            break

    if remaining > 0:
        # 상한 도달 / 봉 소진 — 마지막 종가로 마감
        realized += sgn * (last_close - entry_px) * remaining
        events.append(("", "TIMEOUT", remaining, last_close,
                       sgn * (last_close - entry_px)))
        outcome = outcome or "TIMEOUT"

    if outcome is None:
        outcome = "TIMEOUT"
    if tp1_armed and outcome == "STOP":
        outcome = "TP1_ARM_STOP"     # 보호전환 뒤 되돌림 — [24]가 세는 바로 그 결말

    return {
        "pts": realized,
        "qty": qty,
        "pts_per_contract": realized / qty if qty else 0.0,
        "outcome": outcome,
        "events": events,
        "hold_min": hold_min,
        "reached": reached,
    }
