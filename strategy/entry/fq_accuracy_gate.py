# strategy/entry/fq_accuracy_gate.py — FQAdj 실측 정확도 게이트 (344차)
"""
FQAdj(feature_quality_score 기반 min_conf 조정)는 데이터 "품질"만 보고 완화/강화를
결정했는데, 데이터가 깨끗한 것과 모델이 실제로 잘 맞히는 것은 다른 질문이다.
7/15 진입0 딥다이브: 당일 실측 정확도가 랜덤 수준(~0.31~0.35)이었는데도
feature_quality_score=1.00으로 min_conf가 0.35→0.32로 완화된 사례 확인 — 방향이
반대였다(가장 못 맞히는 날에 더 쉽게 진입하게 만듦).

이 모듈은 그 결정 로직만 분리한 순수 함수로, main.py의 거대한 파이프라인 밖에서
독립적으로(COM 의존 없이) 단위 테스트할 수 있다.
"""
from typing import Optional, Tuple


def compute_fq_adjusted_min_conf(
    fq_score: float,
    zone_mc: float,
    short_horizon_acc: Optional[float],
    mc_floor: float,
    mc_ceil: float,
    relax_delta: float = 0.03,
    tighten_delta: float = 0.05,
    fq_relax_min: float = 0.9,
    fq_tighten_max: float = 0.6,
    acc_freeze_min: float = 0.45,
    acc_strengthen_min: float = 0.40,
) -> Tuple[float, str, str]:
    """fq_score와 실측 단기 정확도(short_horizon_acc)를 함께 반영해 zone_mc를 조정한다.

    Args:
        fq_score:            feature_quality_score [0,1]
        zone_mc:              조정 전 min_conf(시간대 기준값)
        short_horizon_acc:    1m/3m/5m 합산 실측 정확도 [0,1], 표본 부족 시 None
                               (None이면 정확도 게이트 자체를 건너뛰고 fq만으로 판단
                               — 표본이 없다고 완화를 막아버리면 세션 초반 정상 완화가
                               막히므로, "모른다"는 "나쁘다"와 다르게 취급한다)
        mc_floor, mc_ceil:    min_conf 절대 하한/상한
        relax_delta:          fq 높음 + acc 정상 시 완화폭
        tighten_delta:        fq 낮음 또는 acc 매우 낮음 시 강화폭
        fq_relax_min:         이 값 이상이면 "완화 후보"
        fq_tighten_max:       이 값 미만이면 "강화"
        acc_freeze_min:       완화 후보인데 이 값 미만이면 완화를 동결(zone_mc 유지)
        acc_strengthen_min:   이 값 미만이면 fq와 무관하게 강화로 전환

    Returns:
        (new_zone_mc, action, reason)
        action: "relax" | "tighten" | "freeze" | "none"
        reason: 사람이 읽을 로그 문구 (action=="none"이면 빈 문자열)
    """
    acc_known = short_horizon_acc is not None
    acc_strengthen_triggered = acc_known and short_horizon_acc < acc_strengthen_min
    acc_freeze_triggered = acc_known and short_horizon_acc < acc_freeze_min

    # 강화가 완화보다 우선 — fq가 낮거나(데이터 품질 자체 불량) 실측 정확도가
    # 심각하게 낮으면(랜덤 수준) fq 값과 무관하게 강화한다.
    if fq_score < fq_tighten_max or acc_strengthen_triggered:
        new_mc = min(zone_mc + tighten_delta, mc_ceil)
        if new_mc > zone_mc:
            reason = (
                f"fq={fq_score:.2f} 낮음" if fq_score < fq_tighten_max
                else f"실측acc={short_horizon_acc:.1%} 낮음"
            )
            return new_mc, "tighten", reason
        return zone_mc, "none", ""

    if fq_score >= fq_relax_min:
        if acc_freeze_triggered:
            return (
                zone_mc, "freeze",
                f"fq={fq_score:.2f} 높음이나 실측acc={short_horizon_acc:.1%} 미달",
            )
        new_mc = max(zone_mc - relax_delta, mc_floor)
        if new_mc < zone_mc:
            return new_mc, "relax", f"fq={fq_score:.2f}"
        return zone_mc, "none", ""

    return zone_mc, "none", ""
