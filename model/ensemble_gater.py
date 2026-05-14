import json
import logging
import math
import os
from typing import Dict, Optional

import numpy as np

from config.constants import DIRECTION_DOWN, DIRECTION_UP

logger = logging.getLogger("SIGNAL")

# 온라인 학습 파라미터
_LEARNING_RATE = 0.005       # 거래당 가중치 이동 폭 (너무 크면 발산)
_WEIGHT_MIN    = 0.02        # 최소 가중치 (0이 되면 영구 소멸 방지)
_WEIGHT_MAX    = 0.60        # 최대 가중치 (과점유 방지)
_SAVE_PATH     = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "ensemble_gater_weights.json",
)

# 초기 KOSPI200 미시구조 분석 기반 기본 가중치
_DEFAULT_WEIGHTS = {
    "micro_bias":      0.28,
    "mlofi_norm":      0.28,
    "queue_signal":    0.16,
    "cancel_add_ratio": 0.10,
    "depth_bias":      0.10,
    "mlofi_slope":     0.08,
}


class AdaptiveEnsembleGater:
    """Microstructure-aware score adjuster with online weight adaptation.

    가중치는 거래 결과 피드백으로 점진적으로 갱신된다.
    각 신호가 방향 예측에 얼마나 기여했는지를 학습률 0.005로 EMA 업데이트.
    """

    def __init__(self):
        self._weights = dict(_DEFAULT_WEIGHTS)
        self._load_weights()          # 이전 세션 가중치 복원 (없으면 기본값 유지)
        self._confirm_threshold = 0.22
        self._reject_threshold = -0.28
        self._boost_max = 0.08
        self._penalty_max = 0.12
        self._outcome_count = 0       # 피드백 수신 누적 건수 (진단용)

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

    # ── 온라인 가중치 학습 ─────────────────────────────────────────

    def record_outcome(
        self,
        *,
        was_correct: bool,
        signals: Dict[str, float],
        direction: int,
    ) -> None:
        """거래 결과 피드백으로 신호 가중치를 점진적으로 갱신.

        Args:
            was_correct: 이 거래가 수익이었으면 True, 손실이었으면 False.
            signals:     apply()가 반환한 "signals" 딕셔너리 (aligned signal 값).
            direction:   진입 방향 (DIRECTION_UP / DIRECTION_DOWN).
        """
        if not signals or direction not in (DIRECTION_UP, DIRECTION_DOWN):
            return

        sign = 1.0 if direction == DIRECTION_UP else -1.0
        # 신호가 방향과 일치했으면 aligned_val > 0, 반대였으면 < 0
        # was_correct=True  → aligned 신호 비중 ↑ (정확히 예측)
        # was_correct=False → aligned 신호 비중 ↓ (잘못 예측)
        feedback = 1.0 if was_correct else -1.0

        updated = False
        for key in self._weights:
            if key not in signals:
                continue
            aligned_val = float(signals[key]) * sign  # apply()에서 sign이 이미 적용됨
            grad = feedback * abs(aligned_val) * _LEARNING_RATE
            self._weights[key] = float(np.clip(
                self._weights[key] + grad,
                _WEIGHT_MIN, _WEIGHT_MAX,
            ))
            updated = True

        if updated:
            # 가중치 합이 1이 되도록 정규화
            total = sum(self._weights.values())
            if total > 0:
                self._weights = {k: v / total for k, v in self._weights.items()}
            self._outcome_count += 1
            # 10건마다 디스크 저장 (매 거래마다 저장하면 I/O 과다)
            if self._outcome_count % 10 == 0:
                self._save_weights()
                logger.debug(
                    "[EnsembleGater] 가중치 갱신 %d건: %s",
                    self._outcome_count,
                    {k: round(v, 4) for k, v in self._weights.items()},
                )

    def _load_weights(self) -> None:
        try:
            if os.path.exists(_SAVE_PATH):
                with open(_SAVE_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                # 저장된 키가 현재 키와 일치하는 것만 복원 (새 피처 추가 시 안전)
                for k in self._weights:
                    if k in saved and isinstance(saved[k], (int, float)):
                        self._weights[k] = float(saved[k])
                # 정규화
                total = sum(self._weights.values())
                if total > 0:
                    self._weights = {k: v / total for k, v in self._weights.items()}
                logger.info("[EnsembleGater] 저장된 가중치 복원: %s", _SAVE_PATH)
        except Exception as _e:
            logger.warning("[EnsembleGater] 가중치 로드 실패 — 기본값 사용: %s", _e)
            self._weights = dict(_DEFAULT_WEIGHTS)

    def _save_weights(self) -> None:
        try:
            os.makedirs(os.path.dirname(_SAVE_PATH), exist_ok=True)
            with open(_SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._weights, f, ensure_ascii=False, indent=2)
        except Exception as _e:
            logger.warning("[EnsembleGater] 가중치 저장 실패: %s", _e)

    def get_weight_summary(self) -> Dict[str, float]:
        """현재 가중치 조회 (대시보드/진단용)."""
        return {k: round(v, 4) for k, v in self._weights.items()}
