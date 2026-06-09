import datetime
import logging
from typing import Dict, Optional

from utils.time_utils import now_kst

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
        min_conf: float = 0.57,
    ) -> Dict:
        if now is None:
            now = now_kst()
        features = features or {}

        if direction == DIRECTION_FLAT:
            return {
                "action": "skip",
                "meta_confidence": 0.0,
                "size_multiplier": 0.0,
                "reason": "flat_signal",
                "source": "rule",
            }

        # mlofi_norm / cancel_add_ratio 는 EnsembleGater가 이미 처리 → 중복 패널티 방지
        meta_features = self.learner.build_meta_features(
            regime=micro_regime,
            hurst=float(features.get("hurst", 0.5) or 0.5),
            atr_ratio=float(features.get("atr_ratio", 1.0) or 1.0),
            hour_minute=now.hour * 100 + now.minute,
            recent_accuracy=float(recent_accuracy),
            signal_strength=float(confidence),
        )
        learned = self.learner.predict_confidence(meta_features)
        meta_conf = float(learned["confidence_score"])

        # SGD 붕괴 보완: prob[1]≈0 고착 시 rule-based 값으로 하한 보정
        # (극단 z-score → 연속 오예측 → SGD "항상 틀림" 학습 방지)
        if meta_conf < 0.15:
            _rb_conf = self.learner._rule_based_confidence(meta_features)
            if _rb_conf > meta_conf:
                logger.info(
                    "[MetaGate] SGD 붕괴 보완: raw=%.3f → rule=%.3f",
                    meta_conf, _rb_conf,
                )
                meta_conf = _rb_conf
                learned["model_source"] = "규칙기반(붕괴보완)"

        blended_conf = (float(confidence) * 0.6) + (meta_conf * 0.4)

        # min_conf 연동 상대 임계값
        # reduce_thr: offset 없이 min_conf 그대로 사용.
        #   - actual_min_conf(존+FQAdj 반영값)이 MetaGate 의 실질 하한이 됨
        #   - floor 0.38: 극단적 저품질 신호까지 열지 않음
        take_thr   = max(0.52, min(0.70, min_conf + 0.14))
        reduce_thr = max(0.38, min_conf)

        if blended_conf >= take_thr:
            action = "take"
            size_mult = max(0.9, min(1.25, learned["size_multiplier"]))
            reason = "meta_take"
        elif blended_conf >= reduce_thr:
            action = "reduce"
            size_mult = max(0.35, min(0.75, learned["size_multiplier"] or 0.5))
            reason = "meta_reduce"
        else:
            action = "skip"
            size_mult = 0.0
            reason = "meta_skip"
            logger.info(
                "[MetaGate] skip: blended=%.3f reduce_thr=%.3f take_thr=%.3f "
                "(min_conf=%.3f ens=%.3f meta_raw=%.3f)",
                blended_conf, reduce_thr, take_thr, min_conf,
                float(confidence), meta_conf,
            )

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
