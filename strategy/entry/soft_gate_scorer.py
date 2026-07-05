# strategy/entry/soft_gate_scorer.py — L3 소프트게이트 점수화 (섀도우 전용)
"""
qty_ok/mode_filter_ok 병목의 실제 원인(`docs/미륵이고도화/qty_ok_mode_filter_근본원인_2026-07-04.md`
정정본)은 9항목 체크리스트 + Degraded Mode·ExecutionGovernor·MetaGate·ToxicityGate 4종
오버라이드가 하나라도 실패하면 즉시 X로 강등되는 **직렬 AND 구조**다. 30일 실측: A/B등급 0건.

이 모듈은 그 직렬 AND를 **가중 점수 합산**으로 대체했다면 어땠을지를 계산한다.
실거래 판정(`_final_grade`/`_qty_display`)에는 전혀 관여하지 않는 순수 섀도우 스코어러 —
main.py 쪽 호출부는 결과를 로그·entry_gate_json에만 기록한다(진입/수량 로직 미개입).

가중치·등급 컷오프는 잠정값이다 — 표본 축적 후
`scripts/generate_soft_gate_shadow_report.py`의 실측 결과로 재보정 대상
(dev의 VALIDATION_CAMPAIGN 사전등록 원칙과 동일하게, 승격 합격선은 이 파일이 아니라
별도 세션에서 데이터 기반으로 확정한다).
"""
from typing import Dict, Optional

# 가중치 — 체크리스트(신호 품질)를 가장 크게, 나머지 4종 오버라이드(리스크/집행 방어)를
# 균등 분배. 근거: qty_ok_mode_filter_근본원인 문서가 지목한 5개 요소를 전부 반영하되,
# 체크리스트가 방향성 신호의 1차 판정이므로 비중을 더 둠.
_WEIGHTS = {
    "checklist": 0.40,
    "degraded":  0.15,
    "execution": 0.15,
    "meta":      0.15,
    "toxicity":  0.15,
}

# soft_score(0~1) → soft_grade 컷오프. 기존 체크리스트 pass_count 컷오프(6/9, 4/9, 2/9)를
# 비율로 환산한 값(0.667, 0.444, 0.222)에서 상하 여유를 둔 잠정치.
_GRADE_CUTOFFS = (
    ("A", 0.65),
    ("B", 0.50),
    ("C", 0.35),
)


class SoftGateScorer:
    """9항목 체크리스트 + 4종 오버라이드를 직렬 AND 대신 가중 점수 합산으로 재해석한다."""

    def score(
        self,
        *,
        checklist_result: Optional[Dict],
        degraded_active: bool,
        confidence: float,
        degraded_min_conf: float,
        execution_result: Optional[Dict],
        meta_result: Optional[Dict],
        toxicity_result: Optional[Dict],
    ) -> Dict:
        checklist_result = checklist_result or {}
        execution_result = execution_result or {}
        meta_result = meta_result or {}
        toxicity_result = toxicity_result or {}

        pass_count = float(checklist_result.get("pass_count", 0) or 0)
        checklist_component = max(0.0, min(1.0, pass_count / 9.0))

        # Degraded Mode: 비활성이면 만점, 활성이면 conf/threshold 비율(0~1)로 연속화.
        # 기존 로직(main.py _health_degraded_mode 분기)은 conf<threshold면 즉시 X —
        # 여기서는 그 경계를 딱딱한 0/1이 아니라 완만한 비율로 대체한다.
        if not degraded_active:
            degraded_component = 1.0
        else:
            degraded_component = max(
                0.0, min(1.0, float(confidence) / max(float(degraded_min_conf), 1e-6))
            )

        execution_component = float(execution_result.get("tradability_score", 1.0))
        execution_component = max(0.0, min(1.0, execution_component))

        # meta_confidence는 이미 0~1 연속값(blended_conf) — action=skip이어도 값 자체는 보존됨
        meta_component = float(meta_result.get("meta_confidence", 0.5) if meta_result else 0.5)
        meta_component = max(0.0, min(1.0, meta_component))

        # toxicity_score는 "나쁨"이 1에 가까움 — 1에서 빼서 "좋음" 방향으로 통일
        toxicity_score = float(toxicity_result.get("score", 0.0) if toxicity_result else 0.0)
        toxicity_component = max(0.0, min(1.0, 1.0 - toxicity_score))

        soft_score = (
            _WEIGHTS["checklist"] * checklist_component
            + _WEIGHTS["degraded"] * degraded_component
            + _WEIGHTS["execution"] * execution_component
            + _WEIGHTS["meta"] * meta_component
            + _WEIGHTS["toxicity"] * toxicity_component
        )

        soft_grade = "X"
        for grade, cutoff in _GRADE_CUTOFFS:
            if soft_score >= cutoff:
                soft_grade = grade
                break

        # A=1.25배까지, X=0 — 기존 ENTRY_GRADE size_mult(1.5/1.0/0.6/0) 스케일과 정합되도록
        # 완만한 연속 곡선(soft_score를 그대로 배수로 사용, 상한 1.25)으로 근사
        soft_size_mult = 0.0 if soft_grade == "X" else round(min(1.25, soft_score * 1.5), 4)

        return {
            "soft_score":       round(soft_score, 4),
            "soft_grade":       soft_grade,
            "soft_size_mult":   soft_size_mult,
            "components": {
                "checklist": round(checklist_component, 4),
                "degraded":  round(degraded_component, 4),
                "execution": round(execution_component, 4),
                "meta":      round(meta_component, 4),
                "toxicity":  round(toxicity_component, 4),
            },
        }
