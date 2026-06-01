# features/technical/volume_profile.py — 거래량 프로파일 기반 지지/저항 피처
"""
최근 N봉의 가격-거래량 분포에서 POC(Point of Control)와 Value Area를 계산.
OHLCV만 사용 → 소급 데이터에도 적용 가능.
Python 3.7 32-bit 호환 (numpy 의존).

피처 4개:
  poc_distance:  현재가 대비 POC 거리 비율 (양수=POC 위, 음수=POC 아래)
  in_value_area: 현재가가 Value Area 내부 여부 (1.0/0.0)
  va_bandwidth:  Value Area 폭 (POC 기준 정규화)
  poc_above:     현재가 > POC 여부 (1.0/0.0)
"""
from collections import deque
from typing import Dict

import numpy as np


class VolumeProfileCalculator:
    """
    최근 N봉 거래량 프로파일 계산기.

    Args:
        n:        롤링 창 봉 수 (기본 60)
        bins:     가격 구간 수 (기본 20)
        va_ratio: Value Area 포함 비율 (기본 0.70 = 70%)
    """

    def __init__(self, n=60, bins=20, va_ratio=0.70):
        self._n        = n
        self._bins     = bins
        self._va_ratio = va_ratio
        self._high_buf  = deque(maxlen=n)
        self._low_buf   = deque(maxlen=n)
        self._vol_buf   = deque(maxlen=n)

    def update(self, high: float, low: float, close: float, volume: float) -> Dict[str, float]:
        self._high_buf.append(float(high))
        self._low_buf.append(float(low))
        self._vol_buf.append(float(volume))

        if len(self._vol_buf) < 10:
            return {"poc_distance": 0.0, "in_value_area": 0.5,
                    "va_bandwidth": 0.0, "poc_above": 0.5}

        return self._compute(float(close))

    def _compute(self, cur: float) -> Dict[str, float]:
        highs = np.array(self._high_buf, dtype=np.float64)
        lows  = np.array(self._low_buf,  dtype=np.float64)
        vols  = np.array(self._vol_buf,  dtype=np.float64)

        price_min = float(lows.min())
        price_max = float(highs.max())
        if price_max <= price_min:
            return {"poc_distance": 0.0, "in_value_area": 0.5,
                    "va_bandwidth": 0.0, "poc_above": 0.5}

        edges = np.linspace(price_min, price_max, self._bins + 1)
        mid   = (edges[:-1] + edges[1:]) / 2.0

        # 각 봉의 고저 범위 중 겹치는 구간만큼 거래량 분배
        vol_profile = np.zeros(self._bins, dtype=np.float64)
        for i in range(len(vols)):
            lo, hi, vi = lows[i], highs[i], vols[i]
            overlap = np.minimum(hi, edges[1:]) - np.maximum(lo, edges[:-1])
            np.maximum(overlap, 0.0, out=overlap)
            rng = hi - lo + 1e-9
            vol_profile += vi * (overlap / rng)

        total_vol = float(vol_profile.sum()) + 1e-9
        poc_idx   = int(vol_profile.argmax())
        poc_price = float(mid[poc_idx])

        # Value Area: 거래량 많은 구간부터 누적 → va_ratio 충족 시 stop
        sorted_idx = list(np.argsort(vol_profile)[::-1])
        cum_vol = 0.0
        va_idx  = []
        for si in sorted_idx:
            va_idx.append(int(si))
            cum_vol += float(vol_profile[si])
            if cum_vol >= self._va_ratio * total_vol:
                break

        vah = float(mid[max(va_idx)])
        val = float(mid[min(va_idx)])

        poc_dist = (cur - poc_price) / (poc_price + 1e-9)
        in_va    = 1.0 if val <= cur <= vah else 0.0
        va_bw    = (vah - val) / (poc_price + 1e-9)
        poc_ab   = 1.0 if cur > poc_price else 0.0

        return {
            "poc_distance":  round(float(poc_dist), 6),
            "in_value_area": in_va,
            "va_bandwidth":  round(float(va_bw), 6),
            "poc_above":     poc_ab,
        }

    def reset_daily(self):
        """일중 연속성이 중요하므로 reset 없음 — 인터페이스 통일용"""
        pass
