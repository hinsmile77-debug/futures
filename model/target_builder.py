# model/target_builder.py — 타겟 라벨 생성
"""
멀티 호라이즌 타겟 라벨 생성.

타겟: +1(상승) / -1(하락) / 0(횡보)
기준: 미래 N분 후 종가 변화율이 threshold 이상인지
"""
import numpy as np
import pandas as pd
from typing import Dict, List

from config.settings import HORIZONS, HORIZON_THRESHOLDS
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
