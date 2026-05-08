import json
from typing import Dict

from config.constants import DIRECTION_FLAT


def derive_meta_label(
    *,
    predicted: int,
    actual: int,
    confidence: float,
    target_close: float,
    future_close: float,
    threshold_ratio: float,
) -> Dict:
    """
    Build a simple three-way meta label for execution quality.

    take:
        correct directional call with enough realized follow-through
    reduce:
        correct call but follow-through is weak
    skip:
        wrong call or no directional edge
    """
    realized_move = 0.0
    threshold_move = abs(float(target_close) * float(threshold_ratio))

    if predicted != DIRECTION_FLAT:
        realized_move = (float(future_close) - float(target_close)) * float(predicted)

    if predicted == DIRECTION_FLAT:
        action = "skip"
        score = 0.0
    elif actual != predicted or realized_move <= 0:
        action = "skip"
        score = 0.0
    elif realized_move >= max(threshold_move * 2.0, 0.05) or confidence >= 0.70:
        action = "take"
        score = 1.0
    else:
        action = "reduce"
        score = 0.5

    return {
        "meta_action": action,
        "meta_score": score,
        "realized_move": round(realized_move, 6),
        "threshold_move": round(threshold_move, 6),
    }


def compact_feature_json(features: Dict) -> str:
    if not features:
        return "{}"
    sanitized = {}
    for key, value in features.items():
        try:
            sanitized[key] = round(float(value), 6)
        except (TypeError, ValueError):
            continue
    return json.dumps(sanitized, ensure_ascii=False)
