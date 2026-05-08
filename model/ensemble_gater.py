import math
from typing import Dict, Optional

import numpy as np

from config.constants import DIRECTION_DOWN, DIRECTION_UP


class AdaptiveEnsembleGater:
    """Microstructure-aware score adjuster for ensemble outputs."""

    def __init__(self):
        self._weights = {
            "micro_bias": 0.28,
            "mlofi_norm": 0.28,
            "queue_signal": 0.16,
            "cancel_add_ratio": 0.10,
            "depth_bias": 0.10,
            "mlofi_slope": 0.08,
        }
        self._confirm_threshold = 0.22
        self._reject_threshold = -0.28
        self._boost_max = 0.08
        self._penalty_max = 0.12

    def apply(
        self,
        *,
        direction: int,
        up_score: float,
        down_score: float,
        flat_score: float,
        confidence: float,
        features: Optional[Dict[str, float]],
    ) -> Dict[str, object]:
        if direction not in (DIRECTION_UP, DIRECTION_DOWN) or not features:
            return {
                "up_score": up_score,
                "down_score": down_score,
                "flat_score": flat_score,
                "confidence": confidence,
                "gate_strength": 0.0,
                "blocked": False,
                "delta": 0.0,
                "signals": {},
                "reason": "inactive",
            }

        aligned = self._aligned_signals(direction, features)
        gate_strength = float(
            sum(aligned[name] * weight for name, weight in self._weights.items())
        )
        if abs(gate_strength) < 1e-9:
            return {
                "up_score": up_score,
                "down_score": down_score,
                "flat_score": flat_score,
                "confidence": confidence,
                "gate_strength": 0.0,
                "blocked": False,
                "delta": 0.0,
                "signals": {k: round(v, 4) for k, v in aligned.items()},
                "reason": "neutral_noop",
            }
        hard_support = sum(1 for v in aligned.values() if v >= 0.6)
        hard_adverse = sum(1 for v in aligned.values() if v <= -0.6)

        blocked = gate_strength <= self._reject_threshold and hard_adverse >= 2
        if blocked:
            delta = -min(self._penalty_max, 0.04 + abs(gate_strength) * 0.18)
            reason = "blocked_by_microstructure"
        elif gate_strength >= self._confirm_threshold and hard_support >= 2:
            delta = min(self._boost_max, gate_strength * 0.12)
            reason = "boosted_by_microstructure"
        else:
            delta = float(np.clip(gate_strength * 0.04, -0.04, 0.04))
            reason = "soft_adjust"
        if abs(delta) < 1e-9:
            return {
                "up_score": up_score,
                "down_score": down_score,
                "flat_score": flat_score,
                "confidence": confidence,
                "gate_strength": round(gate_strength, 6),
                "blocked": False,
                "delta": 0.0,
                "signals": {k: round(v, 4) for k, v in aligned.items()},
                "reason": "neutral_noop",
            }

        new_up, new_down, new_flat = self._rebalance_scores(
            direction=direction,
            up_score=up_score,
            down_score=down_score,
            flat_score=flat_score,
            delta=delta,
            blocked=blocked,
        )
        new_conf = max(new_up, new_down, new_flat)
        return {
            "up_score": round(new_up, 6),
            "down_score": round(new_down, 6),
            "flat_score": round(new_flat, 6),
            "confidence": round(new_conf, 6),
            "gate_strength": round(gate_strength, 6),
            "blocked": blocked,
            "delta": round(delta, 6),
            "signals": {k: round(v, 4) for k, v in aligned.items()},
            "reason": reason,
        }

    def _aligned_signals(self, direction: int, features: Dict[str, float]) -> Dict[str, float]:
        sign = 1.0 if direction == DIRECTION_UP else -1.0
        return {
            "micro_bias": self._clip(sign * self._safe(features.get("microprice_bias")) / 0.01),
            "mlofi_norm": self._clip(sign * self._safe(features.get("mlofi_norm")) / 1.5),
            "queue_signal": self._clip(sign * self._safe(features.get("queue_signal")) / 0.10),
            "cancel_add_ratio": self._clip(sign * self._safe(features.get("cancel_add_ratio")) / 0.40),
            "depth_bias": self._clip(sign * self._safe(features.get("microprice_depth_bias")) / 0.20),
            "mlofi_slope": self._clip(sign * self._safe(features.get("mlofi_slope")) / 20.0),
        }

    @staticmethod
    def _rebalance_scores(
        *,
        direction: int,
        up_score: float,
        down_score: float,
        flat_score: float,
        delta: float,
        blocked: bool,
    ):
        target = up_score if direction == DIRECTION_UP else down_score
        other = down_score if direction == DIRECTION_UP else up_score

        if blocked:
            target = max(0.0, target + delta)
            flat_score = min(1.0, flat_score + abs(delta) * 1.10)
            other = max(0.0, other + abs(delta) * 0.10)
        elif delta >= 0:
            target = min(1.0, target + delta)
            flat_score = max(0.0, flat_score - delta * 0.60)
            other = max(0.0, other - delta * 0.40)
        else:
            target = max(0.0, target + delta)
            flat_score = min(1.0, flat_score + abs(delta) * 0.80)
            other = min(1.0, other + abs(delta) * 0.20)

        if direction == DIRECTION_UP:
            up_score, down_score = target, other
        else:
            down_score, up_score = target, other

        total = up_score + down_score + flat_score
        if total <= 0:
            return 1 / 3, 1 / 3, 1 / 3
        return up_score / total, down_score / total, flat_score / total

    @staticmethod
    def _clip(value: float) -> float:
        return float(np.clip(value, -1.0, 1.0))

    @staticmethod
    def _safe(value: Optional[float]) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0
        return value if math.isfinite(value) else 0.0
