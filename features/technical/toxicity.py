from collections import deque
from typing import Dict


class ToxicityCalculator:
    """
    Lightweight microstructure toxicity proxy.

    It is not a strict VPIN implementation. Instead it combines:
    - ATR expansion
    - spread expansion
    - order-flow stress
    - queue depletion / cancel-add stress
    into a bounded toxicity score suitable for runtime blocking.

    [380차 재보정, 근거: 07-23 딥다이브] 원 공식은 다음 세 가지가 겹쳐 score가 사실상
    상수(과거 실측 최댓값 0.393, dev_memory 311차)로 죽어 있었다:
      - atr_stress: ceiling이 atr_ratio=3.0(CB④ 하드정지 임계와 동일)이라 정지 직전까지도
        거의 0.
      - spread_stress: ceiling이 5틱이라 이 시장 평상 스프레드(2026-07-14~23 클린 라이브
        데이터 n=2690, p50=9.0틱)에서 항상 포화(1.0 고정).
      - queue_stress: 실제로 넘어오는 값은 [0,1] 비율(queue_depletion_ratio, 0.5=균형)인데
        무한 속도값 전제의 /3.0을 그대로 적용해 최댓값이 수학적으로 0.333에 영구히 캡되고,
        평시(ratio≈0.5)에도 늘 0.167의 유령 바닥값이 깔림.
    아래 정규화 상수는 전부 2026-07-14~23 클린 라이브 데이터(그 이전 구간은 bid1/ask1
    결측으로 spread_ticks 등이 0으로 죽어있어 제외, raw_data.db raw_features 재현검증)의
    p90~p99 실측 기준으로 재보정했다. 재보정 후 급변장(micro_regime_code=4) 평균 score가
    0.257로 횡보장(0.177)·추세장(0.176)과 뚜렷이 분리됨(구 공식은 급변장 0.254 vs 횡보장
    0.245로 사실상 무구분) — 26주 Walk-Forward 주기(CLAUDE.md "주기적 재검증 항목")에
    편입해 재확인할 것.
    """

    def __init__(self, window: int = 20):
        self.window = window
        self._score_history = deque(maxlen=window)

    def update(
        self,
        *,
        atr_ratio: float,
        spread_ticks: float,
        mlofi_norm: float,
        queue_depletion_ratio: float,
        cancel_churn_ratio: float,
    ) -> Dict[str, float]:
        # floor=1.0(무팽창) · ceiling=2.0 — CB④(3.0배 하드정지)보다 낮게 잡아 정지 전
        # 구간에서부터 점증하게 함(07-14~23 p99=1.606, max=1.859 확인).
        atr_stress = min(max(float(atr_ratio) - 1.0, 0.0), 1.0)
        # floor=1틱 · ceiling=20틱 — 311차 슬리피지 역산(spread_ticks>=20이 1m TP1의 40%를
        # 스프레드 비용만으로 잠식, p90 실측)과 07-14~23 재확인치(p95=19.0)가 일치.
        spread_stress = min(max((float(spread_ticks) - 1.0) / 19.0, 0.0), 1.0)
        # floor=0 · ceiling=0.12 — 07-14~23 |mlofi_norm| p99=0.119.
        flow_stress = min(abs(float(mlofi_norm)) / 0.12, 1.0)
        # queue_depletion_ratio는 [0,1] 비율(0.5=고갈·리필 균형). 0.5 이하(리필 우세)는
        # 무독성으로 0 처리, 0.5 초과(고갈 우세)만 스트레스로 카운트.
        # ceiling=0.05 — 07-14~23 |ratio-0.5| max=0.0513(이 비율 자체의 실측 변동폭이
        # 매우 좁음 — 급변장 평균편차 0.00057이 추세장 0.00104보다도 작아, 재보정 후에도
        # 이 성분의 실제 판별력은 약할 수 있음. queue_dynamics.py 틱단위 계산 자체의
        # 잔여 이슈 가능성은 별도 조사 필요, 이번 수정 범위 밖).
        queue_stress = min(max((float(queue_depletion_ratio) - 0.5) / 0.05, 0.0), 1.0)
        # cancel_churn_ratio: bid/ask 절대값 기반 무방향 취소폭주 지표(QueueDynamicsCalculator
        # 신규 필드) — 기존 cancel_add_ratio(부호 있는 평균, EnsembleGater 등 방향성 신호로
        # 계속 사용)는 반대부호 상쇄로 양방향 취소폭주를 못 잡는 사각지대가 있어 대체.
        # ceiling=0.08은 신규 피처라 과거 데이터로 재현검증 불가한 잠정치 — 라이브 섀도
        # 관찰 몇 주 후 재보정 필요(317차 Hurst·371차 PSI와 동일 절차).
        cancel_stress = min(abs(float(cancel_churn_ratio)) / 0.08, 1.0)

        score = (
            atr_stress * 0.25
            + spread_stress * 0.20
            + flow_stress * 0.20
            + queue_stress * 0.15
            + cancel_stress * 0.20
        )
        score = min(max(score, 0.0), 1.0)
        self._score_history.append(score)
        rolling = sum(self._score_history) / len(self._score_history) if self._score_history else score

        # [380차] 재보정 후 스케일에 맞춘 임계값 — 07-14~23 클린 데이터(n=2690) 백테스트로
        # toxic(0.45)은 전체의 0.7%(하루 1~7분), warning(0.28)은 11.8%(하루 20~100분)
        # 발동하도록 선정(구 공식은 toxic 0회/전체 이력, warning은 spread_ticks>=8 우회
        # 조건이 사실상 전담 — strategy/risk/toxicity_gate.py 동시 수정 참조).
        if score >= 0.45 or rolling >= 0.40:
            regime = "toxic"
        elif score >= 0.28 or rolling >= 0.25:
            regime = "warning"
        else:
            regime = "normal"

        return {
            "toxicity_score": round(score, 6),
            "toxicity_score_ma": round(rolling, 6),
            "toxicity_regime": regime,
            "atr_stress": round(atr_stress, 6),
            "spread_stress": round(spread_stress, 6),
            "flow_stress": round(flow_stress, 6),
            "queue_stress": round(queue_stress, 6),
            "cancel_stress": round(cancel_stress, 6),
        }

    def reset_daily(self) -> None:
        self._score_history.clear()
