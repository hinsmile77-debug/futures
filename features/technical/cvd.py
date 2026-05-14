# features/technical/cvd.py — CVD 다이버전스 ★ CORE-1
"""
CVD (Cumulative Volume Delta) 다이버전스

매수 체결량 - 매도 체결량의 누적값.
가격이 상승하는데 CVD가 하락 → 허수 상승 (매도 압력이 더 강함)
→ 단기 최강 방향 신호

계산:
  tick_delta = +qty if 체결가 > 직전가
             = -qty if 체결가 < 직전가
             =   0  if 체결가 == 직전가 (보합 — 중립 처리)
  CVD_t = CVD_{t-1} + tick_delta
  divergence = price_direction != cvd_direction (최근 N분)
"""
import numpy as np
from collections import deque
from typing import Tuple


class CVDCalculator:
    """실시간 CVD 계산기"""

    def __init__(self, window: int = 10):
        """
        Args:
            window: 다이버전스 판단 기간 (기본 10분봉)
        """
        self.window = window
        self._cvd_buf   = deque(maxlen=window)
        self._price_buf = deque(maxlen=window)
        self._cumulative_cvd = 0.0

    def update(self, price: float, qty: int, prev_price: float) -> dict:
        """
        틱 체결 데이터로 CVD 업데이트

        Args:
            price:      현재 체결가
            qty:        체결량
            prev_price: 직전 체결가

        Returns:
            {cvd, delta, divergence, signal_strength}
        """
        # 보합(price == prev_price)을 매수로 분류하면 시스템적 롱 바이어스가 누적된다.
        # 체결가 변화가 없는 틱은 방향 불명이므로 delta=0(중립) 처리한다.
        if price > prev_price:
            delta = qty
        elif price < prev_price:
            delta = -qty
        else:
            delta = 0
        self._cumulative_cvd += delta

        self._cvd_buf.append(self._cumulative_cvd)
        self._price_buf.append(price)

        return self.compute()

    def update_from_bar(self, close: float, buy_vol: float, sell_vol: float) -> dict:
        """
        1분봉 집계 데이터로 CVD 업데이트 (체결강도 방식)

        Args:
            close:    종가
            buy_vol:  매수 체결량
            sell_vol: 매도 체결량
        """
        delta = buy_vol - sell_vol
        self._cumulative_cvd += delta

        self._cvd_buf.append(self._cumulative_cvd)
        self._price_buf.append(close)

        return self.compute()

    def compute(self) -> dict:
        """CVD 다이버전스 계산"""
        n = len(self._cvd_buf)
        if n < 3:
            return {
                "cvd": self._cumulative_cvd,
                "delta": 0.0,
                "divergence": False,
                "signal_strength": 0.0,
                "direction": 0,
            }

        prices = list(self._price_buf)
        cvds   = list(self._cvd_buf)

        price_slope = prices[-1] - prices[0]
        cvd_slope   = cvds[-1]   - cvds[0]

        # 다이버전스: 가격과 CVD 방향이 반대
        divergence = (price_slope > 0 and cvd_slope < 0) or \
                     (price_slope < 0 and cvd_slope > 0)

        # 신호 강도: 0.0 ~ 1.0
        if divergence:
            magnitude = min(abs(cvd_slope) / (abs(price_slope) + 1e-9), 3.0)
            strength  = min(magnitude / 3.0, 1.0)
        else:
            strength = 0.0

        # CVD 방향 (단순)
        direction = 1 if cvd_slope > 0 else (-1 if cvd_slope < 0 else 0)

        return {
            "cvd":              round(self._cumulative_cvd, 2),
            "delta":            round(cvds[-1] - cvds[-2] if n >= 2 else 0, 2),
            "divergence":       divergence,
            "signal_strength":  round(strength, 3),
            "direction":        direction,
            "price_slope":      round(price_slope, 4),
            "cvd_slope":        round(cvd_slope, 2),
        }

    def reset_daily(self):
        """일일 리셋 (장 시작 시 호출)"""
        self._cumulative_cvd = 0.0
        self._cvd_buf.clear()
        self._price_buf.clear()
