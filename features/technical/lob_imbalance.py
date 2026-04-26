# features/technical/lob_imbalance.py — LOB Imbalance (호가창 불균형)
"""
Limit Order Book Imbalance — 10호가 전체의 매수/매도 압력 비교

단순 1호가 OFI보다 시장 깊이(depth)를 반영하여 더 강력한 선행 지표.
기대 효과: 정확도 +5~8%

계산:
  bid_volume = Σ(bid_qty_i * weight_i)  i=1..10
  ask_volume = Σ(ask_qty_i * weight_i)  i=1..10
  weight_i = 1/i  (1호가 비중 최대, 거리 멀수록 감소)

  LOB_imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol)
  범위: -1.0 (완전 매도 우위) ~ +1.0 (완전 매수 우위)
"""
import numpy as np
from collections import deque
from typing import List, Optional


class LOBImbalanceCalculator:
    """10호가 기반 LOB Imbalance 계산기"""

    MAX_LEVELS = 10   # 최대 호가 단계 수

    def __init__(self, window: int = 5):
        self.window = window
        self._imb_buf = deque(maxlen=window)

        # 호가 가중치: 1호가=1.0, 2호가=0.5, ..., 10호가=0.1
        self._weights = np.array([1.0 / (i + 1) for i in range(self.MAX_LEVELS)])

    def compute(
        self,
        bid_prices: List[float], bid_qtys: List[int],
        ask_prices: List[float], ask_qtys: List[int],
    ) -> dict:
        """
        호가창 스냅샷으로 즉시 계산 (틱마다 또는 분마다 호출 가능)

        Args:
            bid_prices: 매수 1~10호가 리스트
            bid_qtys:   매수 1~10호가 수량
            ask_prices: 매도 1~10호가 리스트
            ask_qtys:   매도 1~10호가 수량

        Returns:
            {lob_imbalance, bid_vol, ask_vol, depth_ratio, pressure}
        """
        n = min(len(bid_qtys), len(ask_qtys), self.MAX_LEVELS)
        if n == 0:
            return self._empty()

        w = self._weights[:n]
        bid_vol = float(np.dot(np.array(bid_qtys[:n], dtype=float), w))
        ask_vol = float(np.dot(np.array(ask_qtys[:n], dtype=float), w))

        total = bid_vol + ask_vol
        if total < 1e-9:
            return self._empty()

        imbalance = (bid_vol - ask_vol) / total   # -1 ~ +1

        # 분봉 이동평균용 버퍼 누적
        self._imb_buf.append(imbalance)
        imb_ma = float(np.mean(list(self._imb_buf)))

        # 호가 스프레드 (매도1 - 매수1)
        spread = (ask_prices[0] - bid_prices[0]) if (ask_prices and bid_prices) else 0.0

        # 깊이 비율 (총 유동성 크기)
        depth_ratio = bid_vol / (ask_vol + 1e-9)

        # 압력 방향
        if imbalance > 0.15:
            pressure = 1
        elif imbalance < -0.15:
            pressure = -1
        else:
            pressure = 0

        return {
            "lob_imbalance": round(imbalance, 4),   # CORE 피처값
            "lob_imb_ma":    round(imb_ma, 4),       # CORE 피처값
            "bid_vol":       round(bid_vol, 1),
            "ask_vol":       round(ask_vol, 1),
            "spread":        round(spread, 2),
            "depth_ratio":   round(depth_ratio, 3),
            "pressure":      pressure,
        }

    def _empty(self) -> dict:
        return {
            "lob_imbalance": 0.0,
            "lob_imb_ma":    0.0,
            "bid_vol":       0.0,
            "ask_vol":       0.0,
            "spread":        0.0,
            "depth_ratio":   1.0,
            "pressure":      0,
        }

    def reset_daily(self):
        self._imb_buf.clear()


if __name__ == "__main__":
    calc = LOBImbalanceCalculator(window=5)

    # 매수 우위 시나리오
    bid_p = [390.0, 389.75, 389.5, 389.25, 389.0, 388.75, 388.5, 388.25, 388.0, 387.75]
    bid_q = [500, 300, 200, 150, 100, 80, 60, 50, 40, 30]
    ask_p = [390.25, 390.5, 390.75, 391.0, 391.25, 391.5, 391.75, 392.0, 392.25, 392.5]
    ask_q = [100,  80,  60,  50,  40,  30,  25,  20,  15,  10]

    for i in range(3):
        r = calc.compute(bid_p, bid_q, ask_p, ask_q)
        print(f"[{i+1}] imbalance={r['lob_imbalance']:+.4f}, pressure={r['pressure']:+d}, spread={r['spread']}")
