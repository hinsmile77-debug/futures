# features/technical/atr.py — ATR 변동성 레짐
"""
ATR (Average True Range)

변동성 레짐 분류 + 손절/목표가 계산에 사용.
미시 레짐(v6.5) 분류와 연동됩니다.
"""
import numpy as np
from collections import deque


class ATRCalculator:
    """실시간 ATR 계산기"""

    def __init__(self, period: int = 14):
        self.period = period
        self._tr_buf  = deque(maxlen=period * 3)
        self._atr_buf = deque(maxlen=period * 3)
        self._prev_close: float = None

    def update(self, high: float, low: float, close: float) -> dict:
        """
        1분봉 업데이트

        Returns:
            {atr, atr_avg, atr_ratio, regime}
        """
        if self._prev_close is None:
            self._prev_close = close
            tr = high - low
        else:
            tr = max(
                high - low,
                abs(high - self._prev_close),
                abs(low  - self._prev_close),
            )

        self._tr_buf.append(tr)
        self._prev_close = close

        # Wilder's ATR (EMA 방식)
        if len(self._tr_buf) >= self.period:
            atr = float(np.mean(list(self._tr_buf)[-self.period:]))
        else:
            atr = float(np.mean(list(self._tr_buf)))

        self._atr_buf.append(atr)

        # 평균 ATR (최근 period*2 기간)
        atr_avg = float(np.mean(list(self._atr_buf))) if self._atr_buf else atr

        # ATR 비율 (현재 / 평균)
        atr_ratio = atr / (atr_avg + 1e-9)

        regime = self._classify(atr_ratio)

        return {
            "atr":       round(atr, 4),
            "atr_avg":   round(atr_avg, 4),
            "atr_ratio": round(atr_ratio, 3),
            "regime":    regime,
            "tr":        round(tr, 4),
        }

    def _classify(self, ratio: float) -> str:
        """ATR 비율 기반 레짐 분류"""
        if ratio > 2.0:
            return "급변장"
        elif ratio > 1.5:
            return "고변동"
        elif ratio < 0.7:
            return "저변동"
        else:
            return "표준"

    def get_stop_distance(self, atr: float = None, mult: float = 1.5) -> float:
        """손절 거리 계산 (ATR × mult)"""
        if atr is None:
            atr = self._atr_buf[-1] if self._atr_buf else 0
        return atr * mult

    def reset_daily(self):
        self._tr_buf.clear()
        self._atr_buf.clear()
        self._prev_close = None
