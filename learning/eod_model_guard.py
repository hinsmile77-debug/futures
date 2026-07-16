# learning/eod_model_guard.py — EOD 모델 교체 가드 (346차)
"""
EOD(장 마감 후) GBM/RF 재학습 결과가 구모델보다 유의미하게 나빠졌는데도
`force=True`로 무조건 교체되던 문제(0715진입청산검토.md 딥다이브) 대응.

판정 로직만 분리한 순수 함수 — main.py/batch_retrainer.py처럼 COM·sklearn에
의존하는 무거운 모듈 밖에서 독립적으로 단위 테스트할 수 있다(344차 fq_accuracy_gate.py
와 동일한 설계 이유).
"""
from typing import Dict, Tuple


def evaluate_model_replace(
    horizon: str,
    new_acc: float,
    old_acc: float,
    tolerance_map: Dict[str, float],
    default_tolerance: float = 0.03,
) -> Tuple[bool, str]:
    """새로 학습된 모델(new_acc)로 교체할지, 구모델(old_acc)을 유지할지 판정한다.

    Args:
        horizon:           호라이즌 키 ("1m" 등)
        new_acc:           신규 학습 결과 정확도(GBM cv_acc) 또는 OOB(RF) [0,1]
        old_acc:           구모델의 저장된 정확도/OOB. 0.0 이하면 구모델이 없는
                            콜드스타트로 간주 — 비교 없이 항상 교체 허용.
        tolerance_map:      호라이즌별 허용 하락폭 딕셔너리
        default_tolerance:  tolerance_map에 없는 호라이즌의 기본 허용 하락폭

    Returns:
        (replace: bool, reason: str)
        replace=True  → 교체 진행 (개선·유지·콜드스타트)
        replace=False → 교체 보류, 구모델 유지 (reason에 하락폭/허용치 명시)
    """
    if old_acc <= 0.0:
        return True, "콜드스타트(구모델 없음) — 비교 없이 교체"

    tolerance = tolerance_map.get(horizon, default_tolerance)
    drop = old_acc - new_acc

    if drop > tolerance:
        return False, (
            "acc 하락 %.4f > 허용 %.4f (new=%.4f old=%.4f)"
            % (drop, tolerance, new_acc, old_acc)
        )
    return True, (
        "acc %s (new=%.4f old=%.4f 허용=%.4f)"
        % ("개선" if drop < 0 else "유지", new_acc, old_acc, tolerance)
    )
