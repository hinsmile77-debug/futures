from collections import deque
from typing import Dict


class ToxicityCalculator:
    """
    Lightweight microstructure toxicity proxy.

    It is not a strict VPIN implementation. Instead it combines:
    - ATR expansion
    - spread expansion
    - order-flow stress
    - queue depletion / cancel-add stress
    into a bounded toxicity score suitable for runtime blocking.
    """

    def __init__(self, window: int = 20):
        self.window = window
        self._score_history = deque(maxlen=window)

    def update(
        self,
        *,
        atr_ratio: float,
        spread_ticks: float,
        mlofi_norm: float,
        queue_depletion_speed: float,
        cancel_add_ratio: float,
    ) -> Dict[str, float]:
        atr_stress = min(max((float(atr_ratio) - 1.0) / 2.0, 0.0), 1.0)
        spread_stress = min(max((float(spread_ticks) - 1.0) / 4.0, 0.0), 1.0)
        flow_stress = min(abs(float(mlofi_norm)) * 2.5, 1.0)
        queue_stress = min(abs(float(queue_depletion_speed)) / 3.0, 1.0)
        cancel_stress = min(abs(float(cancel_add_ratio)) / 2.0, 1.0)

        score = (
            atr_stress * 0.25
            + spread_stress * 0.20
            + flow_stress * 0.20
            + queue_stress * 0.15
            + cancel_stress * 0.20
        )
        score = min(max(score, 0.0), 1.0)
        self._score_history.append(score)
        rolling = sum(self._score_history) / len(self._score_history) if self._score_history else score

        if score >= 0.78 or rolling >= 0.72:
            regime = "toxic"
        elif score >= 0.58 or rolling >= 0.55:
            regime = "warning"
        else:
            regime = "normal"

        return {
            "toxicity_score": round(score, 6),
            "toxicity_score_ma": round(rolling, 6),
            "toxicity_regime": regime,
            "atr_stress": round(atr_stress, 6),
            "spread_stress": round(spread_stress, 6),
            "flow_stress": round(flow_stress, 6),
            "queue_stress": round(queue_stress, 6),
            "cancel_stress": round(cancel_stress, 6),
        }

    def reset_daily(self) -> None:
        self._score_history.clear()
