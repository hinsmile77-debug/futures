from __future__ import annotations

from typing import Dict, Optional


class ExecutionGovernor:
    """Runtime tradability gate using confidence, quality, latency, and toxicity."""

    def __init__(
        self,
        pass_threshold: float = 0.65,
        reduce_threshold: float = 0.45,
        latency_warn_sec: float = 1.5,
        latency_block_sec: float = 5.0,
    ):
        self.pass_threshold = pass_threshold
        self.reduce_threshold = reduce_threshold
        self.latency_warn_sec = latency_warn_sec
        self.latency_block_sec = latency_block_sec

    def evaluate(
        self,
        *,
        confidence: float,
        quality_score: float,
        latency_sec: float,
        toxicity_score: float,
        context: Optional[Dict] = None,
    ) -> Dict:
        confidence = float(max(0.0, min(1.0, confidence)))
        quality_score = float(max(0.0, min(1.0, quality_score)))
        latency_sec = float(max(0.0, latency_sec))
        toxicity_score = float(max(0.0, min(1.0, toxicity_score)))

        latency_score = self._latency_to_score(latency_sec)
        toxicity_passability = 1.0 - toxicity_score

        # 1차 버전 고정 가중치
        tradability = (
            confidence * 0.35
            + quality_score * 0.30
            + latency_score * 0.20
            + toxicity_passability * 0.15
        )

        # Hard block rule: API 지연 급증은 점수와 무관하게 차단
        if latency_sec >= self.latency_block_sec:
            return {
                "action": "block",
                "size_multiplier": 0.0,
                "tradability_score": round(tradability, 4),
                "reason": "latency_hard_block",
                "components": {
                    "confidence": round(confidence, 4),
                    "quality": round(quality_score, 4),
                    "latency_score": round(latency_score, 4),
                    "toxicity_passability": round(toxicity_passability, 4),
                    "latency_sec": round(latency_sec, 4),
                    "toxicity_score": round(toxicity_score, 4),
                },
                "context": context or {},
            }

        if tradability >= self.pass_threshold:
            action = "pass"
            size_multiplier = 1.0
            reason = "tradability_pass"
        elif tradability >= self.reduce_threshold:
            action = "reduce"
            size_multiplier = 0.6
            reason = "tradability_reduce"
        else:
            action = "block"
            size_multiplier = 0.0
            reason = "tradability_block"

        if latency_sec >= self.latency_warn_sec and action == "pass":
            action = "reduce"
            size_multiplier = min(size_multiplier, 0.7)
            reason = "latency_warn_reduce"

        return {
            "action": action,
            "size_multiplier": float(size_multiplier),
            "tradability_score": round(tradability, 4),
            "reason": reason,
            "components": {
                "confidence": round(confidence, 4),
                "quality": round(quality_score, 4),
                "latency_score": round(latency_score, 4),
                "toxicity_passability": round(toxicity_passability, 4),
                "latency_sec": round(latency_sec, 4),
                "toxicity_score": round(toxicity_score, 4),
            },
            "context": context or {},
        }

    def _latency_to_score(self, latency_sec: float) -> float:
        if latency_sec <= 0.3:
            return 1.0
        if latency_sec <= 1.0:
            return 0.8
        if latency_sec <= self.latency_warn_sec:
            return 0.6
        if latency_sec <= 3.0:
            return 0.35
        if latency_sec <= self.latency_block_sec:
            return 0.1
        return 0.0
