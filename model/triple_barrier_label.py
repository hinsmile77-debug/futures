# model/triple_barrier_label.py — 트리플 배리어 라벨링 (v9 처방 P1)
"""
Lopez de Prado, *Advances in Financial Machine Learning* ch.3 — Triple-Barrier Labeling.

기존 `learning/batch_retrainer.py::_path_conditioned_label()`은 "h분 뒤 종가 수익률
방향 + 중간 경로 최대 역행폭 재분류" 방식이다. 배리어 폭이 고정 threshold(횟수 기반)이고,
손절/익절 중 무엇이 먼저 닿는지(first-touch)가 아니라 h분 뒤 시점의 종가만으로 최종
방향을 정한 뒤 사후적으로 FLAT 재분류만 한다 — 즉 "라벨이 실제 거래 손익 구조(손절/익절)를
반영하지 않는다"는 갭이 있다 (mireuki_v9_최종설계안_2026-07-03.md §2-1 G3, 처방 P1).

이 모듈은 ATR 연동 손절(하단)/익절(상단) 배리어 중 먼저 닿는 쪽으로 라벨링해,
학습 목표를 실제 거래의 손익비 구조에 정렬시킨다. 어느 배리어도 안 닿으면 시간 배리어
(호라이즌 종료)에서 종가 수익률 부호로 판정한다.

기존 라벨링 로직·운영 파이프라인은 변경하지 않는다 — 이 모듈은 병렬 비교/검증용
(scripts/build_triple_barrier_labels.py)이며, W2~3 오프라인 walk-forward 비교를 통과한
뒤에만 batch_retrainer 학습 경로에 편입한다.
"""
import datetime
from typing import Dict, List, Optional

from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

TOUCH_UPPER = "upper"
TOUCH_LOWER = "lower"
TOUCH_TIME = "time"

# 처방 P1 기본값: ATR_STOP_MULT(1.5, config/settings.py)를 손절 배리어로,
# 손익비 목표 2.0(mireuki_v9 §6 검증기준)을 그대로 익절 배리어 배수에 반영.
DEFAULT_STOP_MULT = 1.5
DEFAULT_PROFIT_MULT = DEFAULT_STOP_MULT * 2.0  # = 3.0


def _minute_ts(ts: str, offset: int) -> str:
    return (
        datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        + datetime.timedelta(minutes=offset)
    ).strftime("%Y-%m-%d %H:%M:%S")


def build_triple_barrier_label(
    bar_map: Dict[str, dict],
    ts: str,
    h_min: int,
    atr_at_t: float,
    stop_mult: float = DEFAULT_STOP_MULT,
    profit_mult: float = DEFAULT_PROFIT_MULT,
    flat_ret_threshold: float = 0.0,
) -> Optional[dict]:
    """단일 (ts, horizon) 트리플 배리어 라벨 산출.

    Args:
        bar_map: {ts: {"high":.., "low":.., "close":..}} 분봉 딕셔너리 (raw_candles 기반)
        ts:      진입 시점 (분봉 타임스탬프, "%Y-%m-%d %H:%M:%S")
        h_min:   호라이즌 (분) — 시간 배리어
        atr_at_t: 진입 시점 ATR (pt) — 손절/익절 배리어 폭 산출 기준
        stop_mult / profit_mult: ATR 대비 손절/익절 배수

    Returns:
        {"label", "touch_type", "touch_minute", "realized_ret"} 또는
        데이터 부족 시 None. 기존 target_builder 관례(라벨 없음도 FLAT으로 침묵 처리)와
        달리, 라벨 없음과 FLAT 라벨을 구분해 집계 왜곡을 피한다.
    """
    c0 = bar_map.get(ts, {}).get("close")
    if not c0 or atr_at_t is None or atr_at_t <= 0:
        return None

    upper = c0 + profit_mult * atr_at_t
    lower = c0 - stop_mult * atr_at_t

    for m in range(1, h_min + 1):
        bar = bar_map.get(_minute_ts(ts, m))
        if bar is None:
            continue
        hi, lo = bar.get("high"), bar.get("low")
        if hi is None or lo is None:
            continue
        # 동일 봉 내 상하단 동시 터치 — 보수적으로 손절(하단) 우선 판정
        if lo <= lower and hi >= upper:
            return {"label": DIRECTION_DOWN, "touch_type": TOUCH_LOWER,
                    "touch_minute": m, "realized_ret": (lower - c0) / c0}
        if hi >= upper:
            return {"label": DIRECTION_UP, "touch_type": TOUCH_UPPER,
                    "touch_minute": m, "realized_ret": (upper - c0) / c0}
        if lo <= lower:
            return {"label": DIRECTION_DOWN, "touch_type": TOUCH_LOWER,
                    "touch_minute": m, "realized_ret": (lower - c0) / c0}

    # 시간 배리어 — h_min까지 어느 쪽도 안 닿음 → 종가 수익률 부호로 판정
    final_bar = bar_map.get(_minute_ts(ts, h_min))
    if final_bar is None:
        return None
    ret = (final_bar["close"] - c0) / c0
    if ret > flat_ret_threshold:
        label = DIRECTION_UP
    elif ret < -flat_ret_threshold:
        label = DIRECTION_DOWN
    else:
        label = DIRECTION_FLAT
    return {"label": label, "touch_type": TOUCH_TIME,
            "touch_minute": h_min, "realized_ret": ret}


def build_triple_barrier_labels_for_horizon(
    candles: List[dict],
    h_min: int,
    atr_period: int = 14,
    stop_mult: float = DEFAULT_STOP_MULT,
    profit_mult: float = DEFAULT_PROFIT_MULT,
) -> List[dict]:
    """분봉 시퀀스 전체에 대해 ATR 스트리밍 계산 + 매 시점 트리플 배리어 라벨 산출.

    Args:
        candles: 시간순 정렬된 [{"ts","high","low","close"}, ...] (raw_candles 조회 결과)

    Returns:
        [{"ts","label","touch_type","touch_minute","realized_ret","atr_at_t"}, ...]
        (마지막 h_min분 및 ATR 워밍업 구간은 라벨 없음으로 제외)
    """
    from features.technical.atr import ATRCalculator

    calc = ATRCalculator(period=atr_period)
    bar_map = {c["ts"]: c for c in candles}
    results: List[dict] = []
    for c in candles:
        atr_res = calc.update(c["high"], c["low"], c["close"])
        lbl = build_triple_barrier_label(
            bar_map, c["ts"], h_min, atr_res["atr"],
            stop_mult=stop_mult, profit_mult=profit_mult,
        )
        if lbl is not None:
            lbl["ts"] = c["ts"]
            lbl["atr_at_t"] = atr_res["atr"]
            results.append(lbl)
    return results
