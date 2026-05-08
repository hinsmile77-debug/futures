from collections import deque
from typing import Dict, List, Optional

import numpy as np


class MLOFICalculator:
    """Multi-level order flow imbalance over 3~5 levels."""

    def __init__(self, levels: int = 5, window: int = 5):
        self.levels = levels
        self.window = window
        self._prev_bid_prices: Optional[List[float]] = None
        self._prev_bid_qtys: Optional[List[float]] = None
        self._prev_ask_prices: Optional[List[float]] = None
        self._prev_ask_qtys: Optional[List[float]] = None
        self._minute_mlofi = 0.0
        self._minute_depth = 0.0
        self._mlofi_buf = deque(maxlen=window)
        self._depth_buf = deque(maxlen=window)
        self._weights = np.array([1.0 / (i + 1) for i in range(levels)], dtype=float)

    def update_hoga(
        self,
        bid_prices: List[float],
        bid_qtys: List[int],
        ask_prices: List[float],
        ask_qtys: List[int],
    ) -> Optional[float]:
        n = min(len(bid_prices), len(bid_qtys), len(ask_prices), len(ask_qtys), self.levels)
        if n <= 0:
            return None

        bid_prices = [float(v or 0.0) for v in bid_prices[:n]]
        bid_qtys = [float(v or 0.0) for v in bid_qtys[:n]]
        ask_prices = [float(v or 0.0) for v in ask_prices[:n]]
        ask_qtys = [float(v or 0.0) for v in ask_qtys[:n]]

        if self._prev_bid_prices is None:
            self._prev_bid_prices = bid_prices
            self._prev_bid_qtys = bid_qtys
            self._prev_ask_prices = ask_prices
            self._prev_ask_qtys = ask_qtys
            return None

        mlofi_tick = 0.0
        weighted_depth = 0.0
        for i in range(n):
            weight = float(self._weights[i])
            weighted_depth += weight * (bid_qtys[i] + ask_qtys[i])
            mlofi_tick += weight * self._level_contribution(
                bid_prices[i],
                bid_qtys[i],
                self._prev_bid_prices[i],
                self._prev_bid_qtys[i],
                side="bid",
            )
            mlofi_tick += weight * self._level_contribution(
                ask_prices[i],
                ask_qtys[i],
                self._prev_ask_prices[i],
                self._prev_ask_qtys[i],
                side="ask",
            )

        self._minute_mlofi += mlofi_tick
        self._minute_depth += weighted_depth
        self._prev_bid_prices = bid_prices
        self._prev_bid_qtys = bid_qtys
        self._prev_ask_prices = ask_prices
        self._prev_ask_qtys = ask_qtys
        return mlofi_tick

    def flush_minute(self) -> Dict[str, float]:
        self._mlofi_buf.append(self._minute_mlofi)
        self._depth_buf.append(max(self._minute_depth, 1.0))

        mlofi_raw = self._mlofi_buf[-1] if self._mlofi_buf else 0.0
        avg_depth = float(np.mean(self._depth_buf)) if self._depth_buf else 1.0
        mlofi_norm = float(np.clip(mlofi_raw / (avg_depth + 1e-9), -3.0, 3.0))
        mlofi_ma = float(np.mean(self._mlofi_buf)) if self._mlofi_buf else 0.0
        mlofi_slope = self._calc_slope(list(self._mlofi_buf))
        pressure = 1 if mlofi_norm > 0 else -1 if mlofi_norm < 0 else 0

        self._minute_mlofi = 0.0
        self._minute_depth = 0.0
        return {
            "mlofi_raw": round(mlofi_raw, 4),
            "mlofi_norm": round(mlofi_norm, 6),
            "mlofi_ma": round(mlofi_ma, 4),
            "mlofi_slope": round(mlofi_slope, 6),
            "mlofi_pressure": pressure,
        }

    @staticmethod
    def _level_contribution(
        price: float,
        qty: float,
        prev_price: float,
        prev_qty: float,
        *,
        side: str,
    ) -> float:
        if side == "bid":
            if price > prev_price:
                return qty
            if price == prev_price:
                return qty - prev_qty
            return -prev_qty

        if price < prev_price:
            return -qty
        if price == prev_price:
            return -(qty - prev_qty)
        return prev_qty

    @staticmethod
    def _calc_slope(values: List[float]) -> float:
        if len(values) < 3:
            return 0.0
        arr = np.array(values[-5:], dtype=float)
        reg = np.polyfit(range(len(arr)), arr, 1)
        return float(reg[0])

    def reset_daily(self) -> None:
        self._prev_bid_prices = None
        self._prev_bid_qtys = None
        self._prev_ask_prices = None
        self._prev_ask_qtys = None
        self._minute_mlofi = 0.0
        self._minute_depth = 0.0
        self._mlofi_buf.clear()
        self._depth_buf.clear()
