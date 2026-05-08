from typing import Dict, Optional


class ToxicityGate:
    """
    Runtime entry gate for toxic microstructure conditions.

    block:
        do not allow new entry
    reduce:
        keep direction but shrink size
    pass:
        no action
    """

    def __init__(
        self,
        block_threshold: float = 0.78,
        reduce_threshold: float = 0.58,
        severe_spread_ticks: float = 4.0,
    ):
        self.block_threshold = block_threshold
        self.reduce_threshold = reduce_threshold
        self.severe_spread_ticks = severe_spread_ticks

    def evaluate(self, features: Optional[Dict]) -> Dict:
        features = features or {}
        score = float(features.get("toxicity_score", 0.0) or 0.0)
        score_ma = float(features.get("toxicity_score_ma", 0.0) or 0.0)
        spread_ticks = float(features.get("spread_ticks", 0.0) or 0.0)
        cancel_stress = float(features.get("toxicity_cancel_stress", 0.0) or 0.0)
        flow_stress = float(features.get("toxicity_flow_stress", 0.0) or 0.0)

        if score >= self.block_threshold or score_ma >= (self.block_threshold - 0.05):
            return {
                "action": "block",
                "size_multiplier": 0.0,
                "reason": "toxicity_block",
                "score": round(score, 4),
                "score_ma": round(score_ma, 4),
                "signals": {
                    "spread_ticks": round(spread_ticks, 4),
                    "cancel_stress": round(cancel_stress, 4),
                    "flow_stress": round(flow_stress, 4),
                },
            }

        if (
            score >= self.reduce_threshold
            or score_ma >= (self.reduce_threshold - 0.03)
            or spread_ticks >= self.severe_spread_ticks
        ):
            return {
                "action": "reduce",
                "size_multiplier": 0.5,
                "reason": "toxicity_reduce",
                "score": round(score, 4),
                "score_ma": round(score_ma, 4),
                "signals": {
                    "spread_ticks": round(spread_ticks, 4),
                    "cancel_stress": round(cancel_stress, 4),
                    "flow_stress": round(flow_stress, 4),
                },
            }

        return {
            "action": "pass",
            "size_multiplier": 1.0,
            "reason": "toxicity_pass",
            "score": round(score, 4),
            "score_ma": round(score_ma, 4),
            "signals": {
                "spread_ticks": round(spread_ticks, 4),
                "cancel_stress": round(cancel_stress, 4),
                "flow_stress": round(flow_stress, 4),
            },
        }
