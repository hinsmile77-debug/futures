# model/target_builder.py — 타겟 라벨 생성
"""
멀티 호라이즌 타겟 라벨 생성.

타겟: +1(상승) / -1(하락) / 0(횡보)
기준: 미래 N분 후 종가 변화율이 threshold 이상인지
"""
import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from config.settings import HORIZONS, HORIZON_THRESHOLDS, HORIZON_THRESHOLDS_RESEARCH
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT


def build_targets(
    closes: List[float],
    horizons: Dict[str, int] = None,
    thresholds: Dict[str, float] = None,
) -> Dict[str, np.ndarray]:
    """
    과거 종가 리스트로 멀티 호라이즌 타겟 배열 생성

    Args:
        closes:     종가 리스트 (시간순)
        horizons:   {"1m": 1, "3m": 3, ...}
        thresholds: {"1m": 0.0002, ...}

    Returns:
        {"1m": np.array([1, -1, 0, ...]), "3m": ...}
        각 배열 길이 = len(closes) - max_horizon (미래 없는 부분은 NaN)
    """
    if horizons is None:
        horizons = HORIZONS
    if thresholds is None:
        thresholds = HORIZON_THRESHOLDS

    prices = np.array(closes, dtype=float)
    n = len(prices)
    targets = {}

    for name, h in horizons.items():
        thresh = thresholds.get(name, 0.0003)
        labels = np.full(n, np.nan)

        for i in range(n - h):
            ret = (prices[i + h] - prices[i]) / prices[i]
            if ret > thresh:
                labels[i] = DIRECTION_UP
            elif ret < -thresh:
                labels[i] = DIRECTION_DOWN
            else:
                labels[i] = DIRECTION_FLAT

        targets[name] = labels

    return targets


# ── [260704 감사 P1] Triple-barrier 레이블 (섀도우 병행 전용) ──────────────
#
# 기존 build_targets*()는 "N분 후 종가 변화율"만 보므로 실제 청산 규칙(하드스톱·
# TP1)과 무관한 레이블을 학습에 사용한다 — 모델이 배우는 것과 시스템이 버는 것이
# 다른 함수가 되는 근본 원인 (docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §1-2).
#
# build_triple_barrier_label()은 진입(롱 가정) 후 {TP 배리어 / SL 배리어 / 시간
# 배리어} 중 무엇이 먼저 닿는가로 레이블을 정한다. 배리어 폭은 실제 청산 배수
# (config.settings.ATR_STOP_MULT, ATR_HORIZON_TP1_MULT)와 동일하게 맞춰야
# "모델 예측 = 시스템 실행"이 성립한다 — 호출부(batch_retrainer)에서 그 값을 그대로 전달할 것.
#
# 롱 가정으로 상단 배리어(TP) 우선 도달 → UP, 하단 배리어(SL) 우선 도달 → DOWN,
# 시간 배리어까지 어느 쪽도 도달 못하면 → FLAT. 방향 자체(시장이 어느 쪽으로
# 먼저 그만큼 움직였는가)를 보는 것이므로 숏 가정을 별도로 볼 필요는 없다
# (숏 관점은 부호만 반대인 대칭 문제).
def build_triple_barrier_label(
    ts: str,
    h_min: int,
    close_map: Dict[str, float],
    high_map: Dict[str, float],
    low_map: Dict[str, float],
    atr: float,
    stop_mult: float,
    tp_mult: float,
) -> int:
    """단일 시점 triple-barrier 레이블.

    Args:
        ts:        기준 시각 ("%Y-%m-%d %H:%M:%S")
        h_min:     시간 배리어 (분) — 호라이즌 길이
        close_map/high_map/low_map: {ts: price} — 분봉 OHLC
        atr:       기준 시각의 ATR (배리어 폭 산정 기준)
        stop_mult: 하단 배리어 배수 (예: ATR_STOP_MULT)
        tp_mult:   상단 배리어 배수 (예: ATR_HORIZON_TP1_MULT[hz])

    Returns:
        DIRECTION_UP / DIRECTION_DOWN / DIRECTION_FLAT
    """
    c0 = close_map.get(ts)
    if not c0 or atr <= 0 or stop_mult <= 0 or tp_mult <= 0:
        return DIRECTION_FLAT

    upper = c0 + atr * tp_mult
    lower = c0 - atr * stop_mult

    base_dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    for m in range(1, h_min + 1):
        mid_ts = (base_dt + datetime.timedelta(minutes=m)).strftime("%Y-%m-%d %H:%M:%S")
        hi = high_map.get(mid_ts)
        lo = low_map.get(mid_ts)
        if hi is None or lo is None:
            continue
        touched_up = hi >= upper
        touched_dn = lo <= lower
        if touched_up and touched_dn:
            # 동일 분봉 내 상/하단 동시 터치 — 봉 내부 체결 순서 불명(분봉 데이터의 한계).
            # 룩어헤드 편향을 피하기 위해 보수적으로 손절(SL) 먼저 닿은 것으로 처리.
            return DIRECTION_DOWN
        if touched_up:
            return DIRECTION_UP
        if touched_dn:
            return DIRECTION_DOWN

    return DIRECTION_FLAT


def build_single_target(
    current_price: float,
    future_price: float,
    threshold: float,
) -> int:
    """단일 샘플 타겟 라벨 생성 (실시간 검증용)"""
    ret = (future_price - current_price) / current_price
    if ret > threshold:
        return DIRECTION_UP
    elif ret < -threshold:
        return DIRECTION_DOWN
    return DIRECTION_FLAT


def build_targets_asymmetric(
    closes: List[float],
    horizons: Dict[str, int] = None,
    thresholds_research: Dict[str, dict] = None,
) -> Dict[str, np.ndarray]:
    """
    연구용 비대칭 임계값으로 멀티 호라이즌 타겟 배열 생성.

    thresholds_research 형식:
        {"1m": {"down": -0.00041, "up": 0.00041}, "30m": {"down": -0.00129, "up": 0.00262}, ...}

    Returns:
        {"1m": np.array([1, -1, 0, ...]), ...}
    """
    if horizons is None:
        horizons = HORIZONS
    if thresholds_research is None:
        thresholds_research = HORIZON_THRESHOLDS_RESEARCH

    prices = np.array(closes, dtype=float)
    n = len(prices)
    targets = {}

    for name, h in horizons.items():
        t = thresholds_research.get(name)
        if t is None:
            continue
        thr_up  = float(t["up"])
        thr_dn  = float(t["down"])
        labels  = np.full(n, np.nan)

        for i in range(n - h):
            ret = (prices[i + h] - prices[i]) / prices[i]
            if ret > thr_up:
                labels[i] = DIRECTION_UP
            elif ret < thr_dn:
                labels[i] = DIRECTION_DOWN
            else:
                labels[i] = DIRECTION_FLAT

        targets[name] = labels

    return targets
