# features/technical/microprice.py — Microprice (호가 가중 중간가)
"""
Microprice = (Ask * BidQty + Bid * AskQty) / (BidQty + AskQty)

단순 중간가(midprice)보다 실제 체결 방향을 더 정확히 예측.
- Bid qty가 크면 → 매수 압력 → microprice > midprice
- Ask qty가 크면 → 매도 압력 → microprice < midprice

기대 효과: 정확도 +3~5%
참고: Stoikov (2018), "The micro-price: a high-frequency estimator of future prices"
"""
import numpy as np
from collections import deque
from typing import Optional


class MicropriceCalculator:
    """실시간 Microprice 계산기"""

    def __init__(self, window: int = 5):
        self.window = window
        self._mp_buf  = deque(maxlen=window)   # 분봉 microprice
        self._mid_buf = deque(maxlen=window)   # 분봉 midprice

        self._tick_mp  = []   # 분 내 틱 microprice 수집
        self._tick_mid = []

    def update_hoga(
        self,
        bid_price: float, bid_qty: int,
        ask_price: float, ask_qty: int,
    ) -> Optional[float]:
        """
        호가 틱마다 호출 — 분봉 마감 전 실시간 microprice 추적

        Returns:
            현재 틱 microprice (float) or None
        """
        total_qty = bid_qty + ask_qty
        if total_qty == 0:
            return None

        midprice   = (bid_price + ask_price) / 2.0
        microprice = (ask_price * bid_qty + bid_price * ask_qty) / total_qty

        self._tick_mp.append(microprice)
        self._tick_mid.append(midprice)

        return microprice

    def flush_minute(self) -> dict:
        """
        1분봉 마감 시 집계

        Returns:
            {microprice, midprice, mp_bias, mp_ma, mp_slope, direction}
        """
        if self._tick_mp:
            mp  = float(np.mean(self._tick_mp))
            mid = float(np.mean(self._tick_mid))
        else:
            mp  = 0.0
            mid = 0.0

        self._mp_buf.append(mp)
        self._mid_buf.append(mid)

        result = self._compute(mp, mid)

        self._tick_mp.clear()
        self._tick_mid.clear()

        return result

    def _compute(self, mp: float, mid: float) -> dict:
        """현재 분봉 지표 계산"""
        # Microprice bias: 중간가 대비 편향 (양수 = 매수 우위)
        mp_bias = mp - mid

        # 이동평균
        mp_ma = float(np.mean(list(self._mp_buf))) if self._mp_buf else mp

        # 기울기 (추세 선행)
        mp_slope = 0.0
        if len(self._mp_buf) >= 3:
            arr = np.array(list(self._mp_buf)[-5:])
            if len(arr) >= 2:
                reg = np.polyfit(range(len(arr)), arr, 1)
                mp_slope = float(reg[0])

        # 방향: bias와 slope 결합
        direction = 0
        if mp_bias > 0 and mp_slope > 0:
            direction = 1
        elif mp_bias < 0 and mp_slope < 0:
            direction = -1

        return {
            "microprice":  round(mp, 2),
            "midprice":    round(mid, 2),
            "mp_bias":     round(mp_bias, 4),      # CORE 피처값
            "mp_ma":       round(mp_ma, 2),
            "mp_slope":    round(mp_slope, 4),     # CORE 피처값
            "direction":   direction,
        }

    def reset_daily(self):
        self._mp_buf.clear()
        self._mid_buf.clear()
        self._tick_mp.clear()
        self._tick_mid.clear()


if __name__ == "__main__":
    calc = MicropriceCalculator(window=5)

    # 매수 우위 시나리오: bid qty > ask qty → microprice > mid
    for i in range(3):
        for _ in range(10):
            calc.update_hoga(bid_price=390.0, bid_qty=200, ask_price=390.25, ask_qty=50)
        r = calc.flush_minute()
        print(f"[분 {i+1}] microprice={r['microprice']}, bias={r['mp_bias']:+.4f}, dir={r['direction']:+d}")
