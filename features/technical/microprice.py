from collections import deque
from typing import Dict, List, Optional

import numpy as np


class MicropriceCalculator:
    """Track best-level and depth-aware microprice statistics."""

    def __init__(self, window: int = 5, max_levels: int = 5):
        self.window = window
        self.max_levels = max_levels
        self._mp_buf = deque(maxlen=window)
        self._mid_buf = deque(maxlen=window)
        self._tick_mp: List[float] = []
        self._tick_mid: List[float] = []
        self._tick_depth_bias: List[float] = []

    def update_hoga(
        self,
        bid_prices: List[float],
        bid_qtys: List[int],
        ask_prices: List[float],
        ask_qtys: List[int],
    ) -> Optional[Dict[str, float]]:
        n = min(len(bid_prices), len(bid_qtys), len(ask_prices), len(ask_qtys), self.max_levels)
        if n <= 0:
            return None

        bid1 = float(bid_prices[0] or 0.0)
        ask1 = float(ask_prices[0] or 0.0)
        bid1_qty = float(bid_qtys[0] or 0.0)
        ask1_qty = float(ask_qtys[0] or 0.0)
        total_top = bid1_qty + ask1_qty
        if bid1 <= 0 or ask1 <= 0 or total_top <= 0:
            return None

        midprice = (bid1 + ask1) / 2.0
        microprice = (ask1 * bid1_qty + bid1 * ask1_qty) / total_top

        weights = np.array([1.0 / (i + 1) for i in range(n)], dtype=float)
        bid_depth = float(np.dot(np.array(bid_qtys[:n], dtype=float), weights))
        ask_depth = float(np.dot(np.array(ask_qtys[:n], dtype=float), weights))
        depth_bias = (bid_depth - ask_depth) / (bid_depth + ask_depth + 1e-9)

        self._tick_mp.append(microprice)
        self._tick_mid.append(midprice)
        self._tick_depth_bias.append(depth_bias)

        return {
            "microprice_tick": round(microprice, 4),
            "midprice_tick": round(midprice, 4),
            "depth_bias_tick": round(depth_bias, 4),
        }

    def flush_minute(self) -> Dict[str, float]:
        mp = float(np.mean(self._tick_mp)) if self._tick_mp else 0.0
        mid = float(np.mean(self._tick_mid)) if self._tick_mid else 0.0
        depth_bias = float(np.mean(self._tick_depth_bias)) if self._tick_depth_bias else 0.0

        self._mp_buf.append(mp)
        self._mid_buf.append(mid)

        mp_bias = mp - mid
        mp_ma = float(np.mean(self._mp_buf)) if self._mp_buf else mp
        mp_slope = self._calc_slope(list(self._mp_buf))
        direction = 1 if mp_bias > 0 and mp_slope >= 0 else -1 if mp_bias < 0 and mp_slope <= 0 else 0

        self._tick_mp.clear()
        self._tick_mid.clear()
        self._tick_depth_bias.clear()

        return {
            "microprice": round(mp, 4),
            "midprice": round(mid, 4),
            "mp_bias": round(mp_bias, 6),
            "mp_ma": round(mp_ma, 4),
            "mp_slope": round(mp_slope, 6),
            "depth_bias": round(depth_bias, 4),
            "direction": direction,
        }

    @staticmethod
    def _calc_slope(values: List[float]) -> float:
        if len(values) < 3:
            return 0.0
        arr = np.array(values[-5:], dtype=float)
        reg = np.polyfit(range(len(arr)), arr, 1)
        return float(reg[0])

    def reset_daily(self) -> None:
        self._mp_buf.clear()
        self._mid_buf.clear()
        self._tick_mp.clear()
        self._tick_mid.clear()
        self._tick_depth_bias.clear()
