from __future__ import annotations

from typing import Dict, Optional


class ExecutionGovernor:
    """Runtime tradability gate: confidence + data quality + API latency.

    toxicity는 ToxicityGate가 전담하므로 여기서 제외 (이중 차감 방지).

    [311차 후속 결정] 이 게이트는 "저신뢰도 시 사이즈 축소"가 아니라 **인프라 장애
    전용 비상정지**로 운영하기로 확정됨. 실측(06-15~07-10) 근거:
      - feature_quality_score는 정상 운영 중 95.9%가 0.94 이상(데이터원 정상이면
        페널티 0, feature_builder.py의 quality_penalty 참조)이라 quality×0.35 항이
        거의 항상 최대치.
      - latency_score도 정상 틱 수신 지연(<0.3초)이면 항상 1.0이라 latency×0.25도
        거의 항상 최대치.
      - 즉 quality+latency만으로 tradability 기본값이 ~0.60이고, pass_threshold
        (0.65)를 넘기려면 confidence×0.40이 0.05만 넘으면 되는데(confidence≥0.125)
        실측 confidence는 항상 이보다 훨씬 높아 **confidence 항은 사실상 판정에
        관여하지 못함**(같은 기간 실측 tradability 최솟값 0.671 > 0.65, pass 100%).
      - 이 기간 실제 데이터 결손·지연 급증이 없어 발동 0건이었을 뿐이며, docstring
        문구("confidence + quality + latency"가 대등하게 반영된다는 인상)와 실제
        동작(quality/latency 급락 시에만 사실상 발동) 사이의 괴리를 인지한 상태로
        현 구조를 유지하기로 결정 — 재설계하지 않음.
    """

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
        toxicity_score: float = 0.0,   # 하위 호환 — 내부에서 사용 안 함
        context: Optional[Dict] = None,
    ) -> Dict:
        confidence = float(max(0.0, min(1.0, confidence)))
        quality_score = float(max(0.0, min(1.0, quality_score)))
        latency_sec = float(max(0.0, latency_sec))

        latency_score = self._latency_to_score(latency_sec)

        # toxicity는 ToxicityGate 전담 → 여기서 제외, 가중치 재분배
        tradability = (
            confidence    * 0.40
            + quality_score * 0.35
            + latency_score * 0.25
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
                    "latency_sec": round(latency_sec, 4),
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
                "latency_sec": round(latency_sec, 4),
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
