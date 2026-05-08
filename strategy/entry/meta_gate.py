import datetime
import logging
from typing import Dict, Optional

from config.constants import DIRECTION_FLAT
from learning.meta_confidence import MetaConfidenceLearner

logger = logging.getLogger("SIGNAL")


class MetaGate:
    """
    Meta-labeling execution gate.

    The current prototype blends ensemble confidence with a context-aware
    confidence learner and converts that into take / reduce / skip.
    """

    def __init__(self):
        self.learner = MetaConfidenceLearner()

    def evaluate(
        self,
        *,
        direction: int,
        confidence: float,
        regime: str,
        micro_regime: str,
        features: Optional[Dict],
        now: Optional[datetime.datetime] = None,
        recent_accuracy: float = 0.5,
    ) -> Dict:
        if now is None:
            now = datetime.datetime.now()
        features = features or {}

        if direction == DIRECTION_FLAT:
            return {
                "action": "skip",
                "meta_confidence": 0.0,
                "size_multiplier": 0.0,
                "reason": "flat_signal",
                "source": "rule",
            }

        lob_imbalance = float(features.get("mlofi_norm", 0.0) or 0.0)
        vpin_proxy = min(max(abs(float(features.get("cancel_add_ratio", 0.0) or 0.0)) / 3.0, 0.0), 1.0)
        meta_features = self.learner.build_meta_features(
            regime=micro_regime,
            hurst=float(features.get("hurst", 0.5) or 0.5),
            atr_ratio=float(features.get("atr_ratio", 1.0) or 1.0),
            hour_minute=now.hour * 100 + now.minute,
            lob_imbalance=lob_imbalance,
            vpin=vpin_proxy,
            recent_accuracy=float(recent_accuracy),
            signal_strength=float(confidence),
        )
        learned = self.learner.predict_confidence(meta_features)
        meta_conf = float(learned["confidence_score"])
        blended_conf = (float(confidence) * 0.6) + (meta_conf * 0.4)

        if blended_conf >= 0.67:
            action = "take"
            size_mult = max(0.9, min(1.25, learned["size_multiplier"]))
            reason = "meta_take"
        elif blended_conf >= 0.56:
            action = "reduce"
            size_mult = max(0.35, min(0.75, learned["size_multiplier"] or 0.5))
            reason = "meta_reduce"
        else:
            action = "skip"
            size_mult = 0.0
            reason = "meta_skip"

        return {
            "action": action,
            "meta_confidence": round(blended_conf, 4),
            "size_multiplier": round(size_mult, 4),
            "reason": reason,
            "source": learned["model_source"],
            "meta_features": meta_features,
            "raw_meta_confidence": round(meta_conf, 4),
            "regime": regime,
            "micro_regime": micro_regime,
        }

    def record_outcome(self, meta_features, correct: bool) -> None:
        try:
            self.learner.record_outcome(meta_features, correct)
        except Exception as exc:
            logger.debug("[MetaGate] record_outcome fallback: %s", exc)
