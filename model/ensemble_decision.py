# model/ensemble_decision.py — 앙상블 가중합 + 진입 등급 판정
"""
6개 호라이즌 예측을 가중합하여 최종 방향·신뢰도·진입 등급을 결정합니다.

앙상블 가중치 (설계 명세 4-3):
  1분 10% / 3분 15% / 5분 20% / 10분 20% / 15분 20% / 30분 15%
"""
import logging
from typing import Dict, Tuple

from config.settings import (
    ENSEMBLE_WEIGHTS, REGIME_MIN_CONFIDENCE, ENTRY_GRADE,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

logger = logging.getLogger("SIGNAL")


class EnsembleDecision:
    """앙상블 신호 생성 + 진입 등급 판정"""

    def compute(
        self,
        horizon_proba: Dict[str, Dict],
        regime: str = "NEUTRAL",
    ) -> Dict:
        """
        Args:
            horizon_proba: MultiHorizonModel.predict_proba() 결과
            regime:        현재 매크로 레짐

        Returns:
            {direction, confidence, up_score, down_score,
             grade, auto_entry, regime_ok, detail}
        """
        # ── 가중합 ────────────────────────────────────────────
        up_score   = 0.0
        down_score = 0.0
        total_w    = 0.0

        detail = {}
        for h, w in ENSEMBLE_WEIGHTS.items():
            res = horizon_proba.get(h, {})
            if not res:
                continue
            up_score   += res.get("up",   0.0) * w
            down_score += res.get("down", 0.0) * w
            total_w    += w
            detail[h]  = {
                "direction":  res.get("direction"),
                "confidence": res.get("confidence"),
                "weight":     w,
            }

        if total_w > 0:
            up_score   /= total_w
            down_score /= total_w

        flat_score = max(0.0, 1.0 - up_score - down_score)

        # ── 최종 방향·신뢰도 ─────────────────────────────────
        if up_score >= down_score and up_score >= flat_score:
            direction  = DIRECTION_UP
            confidence = up_score
        elif down_score > up_score and down_score >= flat_score:
            direction  = DIRECTION_DOWN
            confidence = down_score
        else:
            direction  = DIRECTION_FLAT
            confidence = flat_score

        # ── 레짐별 최소 신뢰도 기준 ──────────────────────────
        min_conf  = REGIME_MIN_CONFIDENCE.get(regime, 0.58)
        regime_ok = (confidence >= min_conf) and (direction != DIRECTION_FLAT)

        # ── 진입 등급 (체크리스트 통과 수는 entry_manager에서 계산) ──
        # 여기선 신뢰도 기반 사전 등급만 판정
        if not regime_ok:
            grade = "X"
        elif confidence >= 0.70:
            grade = "A"
        elif confidence >= 0.60:
            grade = "B"
        elif confidence >= min_conf:
            grade = "C"
        else:
            grade = "X"

        auto_entry = ENTRY_GRADE.get(grade, {}).get("auto", False) and regime_ok

        result = {
            "direction":  direction,
            "confidence": round(confidence, 4),
            "up_score":   round(up_score, 4),
            "down_score": round(down_score, 4),
            "flat_score": round(flat_score, 4),
            "grade":      grade,
            "auto_entry": auto_entry,
            "regime_ok":  regime_ok,
            "min_conf":   min_conf,
            "detail":     detail,
        }

        logger.info(
            f"[Ensemble] dir={direction:+d} conf={confidence:.1%} "
            f"grade={grade} regime={regime}"
        )
        return result
