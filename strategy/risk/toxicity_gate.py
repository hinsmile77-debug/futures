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
        # [MW0601 419차 / P1 섀도] reduce 밴드 연속 배수 앵커 — config.settings의
        # TOXICITY_REDUCE_MULT_SHADOW_HI/_LO. **섀도 전용**: size_multiplier_shadow
        # 키로 병기만 하고 실제 size_multiplier(상수 0.7)에는 관여하지 않는다.
        # [MW0601 421차] 419차 P0 반영 후 재도출 — 0.90/0.45 → 0.81/0.36.
        # 라이브는 main.py가 config.settings 값을 주입하므로 이 기본값은 폴백이지만,
        # 단위테스트·오프라인 재생이 구값으로 굴러 결론이 갈리지 않도록 동기화한다.
        reduce_mult_shadow_hi: float = 0.81,
        reduce_mult_shadow_lo: float = 0.36,
    ):
        self.block_threshold = block_threshold
        self.reduce_threshold = reduce_threshold
        self.severe_spread_ticks = severe_spread_ticks
        self.reduce_mult_shadow_hi = reduce_mult_shadow_hi
        self.reduce_mult_shadow_lo = reduce_mult_shadow_lo
        # [311차 후속] 극단 스프레드 block 조건 — config.settings의
        # TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED/_TICKS로 제어. enabled=False여도
        # signals.spread_extreme_shadow는 항상 계산해 섀도우 관찰이 가능하게 한다.
        self.severe_spread_block_ticks = severe_spread_block_ticks
        self.severe_spread_block_enabled = severe_spread_block_enabled

    def _reduce_mult_shadow(self, score: float, score_ma: float) -> float:
        """[MW0601 419차 / P1 섀도] reduce 밴드 내 선형 보간 배수 — **읽기 전용**.

        현행 reduce 밴드는 밴드 전체를 상수 0.7 하나로 매핑한다(joint_gate_shadow
        116건 전수에서 tox_size가 예외 없이 정확히 0.7). 그러나 밴드 **내부**에서
        toxicity_score는 실제로 단조 등급성을 갖는다 — 라이브 07-24~07-31 reduce
        밴드(n=1,614) 5분위에서 향후 15m 평균스프레드가 2.8→3.8틱, 15m 실현레인지가
        9.52→13.70pt로 단조 증가하며 Spearman rho=+0.319(t=13.48) / +0.260(t=10.81).
        즉 상수 0.7은 유의한 정보를 전량 폐기하고 있다.

        밴드 내 위치는 score와 score_ma 중 **큰 쪽**으로 잡는다 — evaluate()의
        reduce 진입 조건이 둘의 OR이므로, ma로만 진입한 분봉을 score 기준으로
        보간하면 밴드 하단에 잘못 붙는다.

        앵커는 노출 중립으로 골랐다 — reduce 밴드 평균 배수가 실적용 상수 0.70과
        같아야 한다. 총 노출을 고정해야 나중에 손익이 바뀌었을 때 그것이 등급화
        덕인지 노출 증가 탓인지 분리할 수 있다.

        [MW0601 421차] 419차 P0(cancel ceiling 0.08→0.42)가 밴드 분포를 옮겨
        구 앵커(0.90/0.45)의 평균이 0.7894(+12.8%)로 이탈 → 0.81/0.36으로 재도출.
        span(등급화 강도) 0.45는 고정하고 수준만 옮겼다. 도출 근거와 재실행 방법은
        config/settings.py의 TOXICITY_REDUCE_MULT_SHADOW_HI 주석 참조.
        """
        span = self.block_threshold - self.reduce_threshold
        if span <= 0:
            return self.reduce_mult_shadow_hi
        pos = max(score, score_ma)
        t = (min(max(pos, self.reduce_threshold), self.block_threshold)
             - self.reduce_threshold) / span
        hi, lo = self.reduce_mult_shadow_hi, self.reduce_mult_shadow_lo
        return round(hi + (lo - hi) * t, 4)

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
                # [419차 / P1 섀도] block 밴드는 연속화 대상이 아니다 — 실배수와 동일.
                "size_multiplier_shadow": 0.0,
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
                # ⚠ 상수 0.7 — 419차는 이 값을 **바꾸지 않았다**. 연속 배수는 아래
                # size_multiplier_shadow로 병기만 하며 실거래 사이징에 관여하지 않는다.
                # 실적용 전환은 VALIDATION_CAMPAIGN["toxicity_reduce_mult_shadow"]
                # 표본 축적 후 주간회의 수동 결정(§9 사전등록 원칙).
                "size_multiplier": 0.7,
                "size_multiplier_shadow": self._reduce_mult_shadow(score, score_ma),
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
            # [419차 / P1 섀도] pass 밴드도 연속화 대상이 아니다 — 실배수와 동일.
            "size_multiplier_shadow": 1.0,
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
