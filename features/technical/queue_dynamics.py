from collections import deque
from typing import Dict, List, Optional

import numpy as np


class QueueDynamicsCalculator:
    """Estimate queue depletion, refill, and imbalance drift from top-of-book updates."""

    def __init__(self, window: int = 20, minute_window: int = 5):
        self.window = window
        self.minute_window = minute_window
        self._prev_bid_qty: Optional[float] = None
        self._prev_ask_qty: Optional[float] = None
        self._tick_stats: List[Dict[str, float]] = []
        self._minute_signal_buf = deque(maxlen=minute_window)
        self._imbalance_hist = deque(maxlen=window)

    def update_hoga(self, bid_qty: int, ask_qty: int) -> Optional[Dict[str, float]]:
        bid = float(max(bid_qty, 0))
        ask = float(max(ask_qty, 0))
        total = bid + ask
        if total <= 0:
            return None

        imbalance = (bid - ask) / total
        self._imbalance_hist.append(imbalance)

        if self._prev_bid_qty is None or self._prev_ask_qty is None:
            self._prev_bid_qty = bid
            self._prev_ask_qty = ask
            return None

        bid_delta = bid - self._prev_bid_qty
        ask_delta = ask - self._prev_ask_qty
        depletion_bid = max(-bid_delta, 0.0)
        depletion_ask = max(-ask_delta, 0.0)
        refill_bid = max(bid_delta, 0.0)
        refill_ask = max(ask_delta, 0.0)

        # Use a signed log-ratio so refill=0 cases do not explode to 1e9+ while
        # preserving the intuition that more depletion than refill is positive pressure.
        bid_cancel_add_ratio = self._stable_cancel_add_ratio(depletion_bid, refill_bid)
        ask_cancel_add_ratio = self._stable_cancel_add_ratio(depletion_ask, refill_ask)
        imbalance_slope = self._calc_slope(list(self._imbalance_hist))

        if depletion_ask > refill_ask and depletion_bid <= refill_bid:
            queue_signal = 1
        elif depletion_bid > refill_bid and depletion_ask <= refill_ask:
            queue_signal = -1
        else:
            queue_signal = 0

        stat = {
            "depletion_bid": depletion_bid,
            "depletion_ask": depletion_ask,
            "refill_bid": refill_bid,
            "refill_ask": refill_ask,
            "bid_cancel_add_ratio": bid_cancel_add_ratio,
            "ask_cancel_add_ratio": ask_cancel_add_ratio,
            "imbalance_slope": imbalance_slope,
            "queue_signal": queue_signal,
        }
        self._tick_stats.append(stat)
        self._prev_bid_qty = bid
        self._prev_ask_qty = ask

        return {k: round(v, 4) if isinstance(v, float) else v for k, v in stat.items()}

    def flush_minute(self) -> Dict[str, float]:
        if not self._tick_stats:
            mean_signal = 0.0
            snapshot = {
                "queue_signal_mean": 0.0,
                "queue_signal_ma": 0.0,
                "queue_momentum": 0.0,
                "queue_depletion_speed": 0.0,
                "queue_refill_rate": 0.0,
                "imbalance_slope": 0.0,
                "cancel_add_ratio": 0.0,
                "direction": 0,
            }
            self._minute_signal_buf.append(mean_signal)
            return snapshot

        mean_signal = float(np.mean([s["queue_signal"] for s in self._tick_stats]))
        self._minute_signal_buf.append(mean_signal)
        signal_ma = float(np.mean(self._minute_signal_buf))
        queue_momentum = self._calc_momentum(list(self._minute_signal_buf))

        depletion_speed = float(np.mean([s["depletion_bid"] + s["depletion_ask"] for s in self._tick_stats]))
        refill_rate = float(np.mean([s["refill_bid"] + s["refill_ask"] for s in self._tick_stats]))
        imbalance_slope = float(np.mean([s["imbalance_slope"] for s in self._tick_stats]))
        cancel_add_ratio = float(np.mean([
            (s["bid_cancel_add_ratio"] + s["ask_cancel_add_ratio"]) / 2.0
            for s in self._tick_stats
        ]))

        direction = 1 if signal_ma > 0.15 else -1 if signal_ma < -0.15 else 0
        result = {
            "queue_signal_mean": round(mean_signal, 4),
            "queue_signal_ma": round(signal_ma, 4),
            "queue_momentum": round(queue_momentum, 4),
            "queue_depletion_speed": round(depletion_speed, 4),
            "queue_refill_rate": round(refill_rate, 4),
            "imbalance_slope": round(imbalance_slope, 6),
            "cancel_add_ratio": round(cancel_add_ratio, 4),
            "direction": direction,
        }

        self._tick_stats.clear()
        return result

    @staticmethod
    def _calc_slope(values: List[float]) -> float:
        if len(values) < 3:
            return 0.0
        arr = np.array(values[-5:], dtype=float)
        reg = np.polyfit(range(len(arr)), arr, 1)
        return float(reg[0])

    @staticmethod
    def _calc_momentum(values: List[float]) -> float:
        if len(values) < 3:
            return 0.0
        return float((values[-1] - values[-3]) / 2.0)

    @staticmethod
    def _stable_cancel_add_ratio(depletion: float, refill: float) -> float:
        depletion = max(float(depletion), 0.0)
        refill = max(float(refill), 0.0)
        return float(np.clip(np.log1p(depletion) - np.log1p(refill), -3.0, 3.0))

    def reset_daily(self) -> None:
        self._prev_bid_qty = None
        self._prev_ask_qty = None
        self._tick_stats.clear()
        self._minute_signal_buf.clear()
        self._imbalance_hist.clear()
