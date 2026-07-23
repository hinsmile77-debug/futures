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
        # [380차] toxicity_score 계측 재설계(features/technical/toxicity.py)에 맞춘
        # 재보정값. 구값(0.78/0.58)은 원 계측이 실측 최댓값 0.393에 묶여 block이 이력상
        # 단 한 번도 발동한 적 없던 죽은 임계값이었음(dev_memory 311차, 07-23 딥다이브로
        # 재확인). 07-14~23 클린 라이브 데이터(n=2690) 백테스트 기준 toxic=0.45→전체의
        # 0.7%(하루 1~7분), warning=0.28→11.8%(하루 20~100분) 발동하도록 선정.
        block_threshold: float = 0.45,
        reduce_threshold: float = 0.28,
        severe_spread_ticks: float = 8.0,
        severe_spread_block_ticks: float = 20.0,
        severe_spread_block_enabled: bool = False,
    ):
        self.block_threshold = block_threshold
        self.reduce_threshold = reduce_threshold
        self.severe_spread_ticks = severe_spread_ticks
        # [311차 후속] 극단 스프레드 block 조건 — config.settings의
        # TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED/_TICKS로 제어. enabled=False여도
        # signals.spread_extreme_shadow는 항상 계산해 섀도우 관찰이 가능하게 한다.
        self.severe_spread_block_ticks = severe_spread_block_ticks
        self.severe_spread_block_enabled = severe_spread_block_enabled

    def evaluate(self, features: Optional[Dict]) -> Dict:
        features = features or {}
        score = float(features.get("toxicity_score", 0.0) or 0.0)
        score_ma = float(features.get("toxicity_score_ma", 0.0) or 0.0)
        spread_ticks = float(features.get("spread_ticks", 0.0) or 0.0)
        cancel_stress = float(features.get("toxicity_cancel_stress", 0.0) or 0.0)
        flow_stress = float(features.get("toxicity_flow_stress", 0.0) or 0.0)
        # [311차 후속] enabled 여부와 무관하게 항상 계산 — 섀도우 로그/대시보드 관찰용
        spread_extreme_shadow = spread_ticks >= self.severe_spread_block_ticks

        spread_block_live = self.severe_spread_block_enabled and spread_extreme_shadow
        if score >= self.block_threshold or score_ma >= (self.block_threshold - 0.05) or spread_block_live:
            return {
                "action": "block",
                "size_multiplier": 0.0,
                "reason": "toxicity_block" if not spread_block_live else "toxicity_block_spread_extreme",
                "score": round(score, 4),
                "score_ma": round(score_ma, 4),
                "signals": {
                    "spread_ticks": round(spread_ticks, 4),
                    "cancel_stress": round(cancel_stress, 4),
                    "flow_stress": round(flow_stress, 4),
                    "spread_extreme_shadow": spread_extreme_shadow,
                },
            }

        if (
            score >= self.reduce_threshold
            or score_ma >= (self.reduce_threshold - 0.03)
            or spread_ticks >= self.severe_spread_ticks
        ):
            return {
                "action": "reduce",
                "size_multiplier": 0.7,
                "reason": "toxicity_reduce",
                "score": round(score, 4),
                "score_ma": round(score_ma, 4),
                "signals": {
                    "spread_ticks": round(spread_ticks, 4),
                    "cancel_stress": round(cancel_stress, 4),
                    "flow_stress": round(flow_stress, 4),
                    "spread_extreme_shadow": spread_extreme_shadow,
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
                "spread_extreme_shadow": spread_extreme_shadow,
            },
        }
