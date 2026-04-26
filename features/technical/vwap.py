# features/technical/vwap.py — VWAP + 밴드 ★ CORE-2
"""
VWAP (Volume-Weighted Average Price)

기관 알고리즘의 기준선. 현재가 vs VWAP 위치가
단기 방향의 핵심 판단 근거.

계산:
  VWAP = Σ(Price × Volume) / Σ(Volume)  — 일중 누적
  Upper Band = VWAP + k × σ
  Lower Band = VWAP - k × σ
  (σ: 가격의 VWAP 대비 편차 표준편차)
"""
import numpy as np
from collections import deque


class VWAPCalculator:
    """일중 VWAP + 밴드 실시간 계산기"""

    BAND_K = 2.0        # 밴드 승수 (2σ)
    STD_WINDOW = 20     # 표준편차 계산 기간

    def __init__(self):
        self._cum_pv  = 0.0   # Σ(price × volume)
        self._cum_vol = 0.0   # Σ(volume)
        self._price_dev_buf = deque(maxlen=self.STD_WINDOW)

    def update(self, high: float, low: float, close: float, volume: float) -> dict:
        """
        1분봉 업데이트

        Args:
            high, low, close: 봉 가격
            volume:           봉 거래량

        Returns:
            {vwap, upper_band, lower_band, position, band_width_pct}
        """
        if volume <= 0:
            return self._empty_result(close)

        typical_price = (high + low + close) / 3.0
        self._cum_pv  += typical_price * volume
        self._cum_vol += volume

        vwap = self._cum_pv / self._cum_vol

        # 편차 버퍼
        self._price_dev_buf.append(close - vwap)

        # 표준편차
        if len(self._price_dev_buf) >= 5:
            std = float(np.std(list(self._price_dev_buf)))
        else:
            std = abs(close - vwap) if close != vwap else 1.0

        upper = vwap + self.BAND_K * std
        lower = vwap - self.BAND_K * std

        # 위치: -1(하단밴드 하) ~ 0(VWAP) ~ +1(상단밴드 상)
        band_range = upper - lower
        position = (close - vwap) / (band_range / 2 + 1e-9)
        position = float(np.clip(position, -2.0, 2.0))

        return {
            "vwap":           round(vwap, 2),
            "upper_band":     round(upper, 2),
            "lower_band":     round(lower, 2),
            "position":       round(position, 3),    # CORE 피처값
            "above_vwap":     close > vwap,
            "std":            round(std, 4),
            "band_width_pct": round(band_range / vwap * 100, 3) if vwap else 0,
        }

    def _empty_result(self, close: float) -> dict:
        vwap = self._cum_pv / self._cum_vol if self._cum_vol > 0 else close
        return {
            "vwap":           round(vwap, 2),
            "upper_band":     round(vwap, 2),
            "lower_band":     round(vwap, 2),
            "position":       0.0,
            "above_vwap":     close > vwap,
            "std":            0.0,
            "band_width_pct": 0.0,
        }

    def get_vwap(self) -> float:
        if self._cum_vol <= 0:
            return 0.0
        return self._cum_pv / self._cum_vol

    def reset_daily(self):
        """장 시작 시 호출"""
        self._cum_pv  = 0.0
        self._cum_vol = 0.0
        self._price_dev_buf.clear()
