# Ensemble Signal Upgrade Plan

## Effect Validation Checklist

### Daily Check

- `microstructure_ab_report.md`에서 baseline vs enhanced `accuracy`, `win_rate`, `avg pnl`, `total pnl` 변화를 매일 비교하고 기록한다.
- `calibration_report.md`에서 overall `ECE`, `Brier`, `log-loss`가 개선되는지 확인한다.
- `meta_gate_tuning_report.md`에서 `meta_labels` 샘플 수와 `best_grid` 갱신 여부를 본다.
- `rollout_readiness_report.md`에서 `recommended_stage`가 `shadow`에 머무는지, `alert_only`로 격상 가능한지 확인한다.

### Gate Quality Check

- `ensemble_decisions`에서 `gate_reason`, `gate_strength`, `meta_action`, `toxicity_action` 컬럼이 최근 row에 정상 기록되는지 체크한다.
- `toxicity_reduce / toxicity_block`가 정확하게 작동하는지 보고, 정상 장세에서 과도한 차단이 없는지 본다.
- `meta skip / reduce`가 실제 손실 구간을 줄이는지, `take`가 수익에 기여하는지 계속 본다.

### Promotion Criteria

- A/B 개선 지표가 2개 이상 유의하게 좋아졌는지 확인한다.
- calibration 악화가 없는지도 확인한다.
- `meta_labels >= 20` 이상 시 `alert_only` 재평가, `meta_labels >= 100` 이상 시 `small_size` 검토를 시작한다.
- rollout 단계는 `shadow -> alert_only -> small_size -> full` 순서를 지킨다.

## Update Status (2026-05-08)

### 구현 완료

- Sprint 1 완료
  - baseline 저장
  - 5레벨 호가(FID) 확인 및 실시간 로깅 검증
  - `MLOFI / microprice / queue dynamics` 구현
- Sprint 2 완료
  - feature builder 연결
  - baseline vs microstructure-enhanced A/B 백테스트 구현
  - adaptive gating 프로토타입 구현
- Sprint 3 대부분 완료
  - meta-labeling 데이터셋 적재(`meta_labels`)
  - meta gate 연결(`take / reduce / skip`)
  - calibration 리포트 자동 생성
- Sprint 4 부분 완료
  - toxicity proxy 계산
  - toxicity gate(`pass / reduce / block`) 구현
  - rollout readiness 리포트 자동 생성

### 현재 생성된 주요 산출물

- `baseline_ensemble_report.md`
- `baseline_metrics.json`
- `microstructure_ab_report.md`
- `microstructure_ab_metrics.json`
- `calibration_report.md`
- `calibration_metrics.json`
- `meta_gate_tuning_report.md`
- `meta_gate_tuning_metrics.json`
- `rollout_readiness_report.md`
- `rollout_readiness_metrics.json`

### 현재 판단

- 문서 전체 목표 상태가 100% 완료된 것은 아님
- 실전 적용 단계는 아직 `shadow` 유지가 타당
- `alert_only -> small size -> full`로 올리기 전에 추가 검증 필요

## Next Work

### 우선순위 높음

1. `meta_labels` 추가 누적 확인
   - 최소 20건 이상 누적 후 `alert_only` 재평가
   - 가능하면 100건 이상 누적 후 meta gate threshold 재튜닝
2. toxicity gate 실전 검증
   - 실제 장중 `toxicity_reduce` 또는 `toxicity_block` 발생 사례 확보
   - 정상 장세에서 과도 차단 없는지 확인
3. calibration 개선
   - 현재 ECE가 아직 높아 보수적 운영 필요
   - 표본 추가 후 `calibration_report.md` 재생성 및 개선 여부 비교

### 아직 남은 구현

- abstention threshold / confidence-gap 기반 보류 로직 명시적 구현
- reliability dashboard 확장
- toxicity gate 전용 backtest / stress-day 검증
- feature flag 기반 rollout 제어
- `alert_only` 모드 구현
- `small_size live` 모드 구현
- `full rollout` 자동 승격 기준과 운영 자동화

### 다음 점검 포인트

- `ensemble_decisions`에 `meta_*`, `toxicity_*` 컬럼이 장중 신규 row에 정상 저장되는지 확인
- `scripts/summarize_ensemble_gating.py`로 `toxicity pass/reduce/block` 집계 확인
- `scripts/generate_meta_gate_tuning_report.py` 재실행 후 threshold 추천 갱신
- `scripts/generate_rollout_readiness_report.py` 재실행 후 `shadow -> alert_only` 승격 가능 여부 재판정

## 목적

현재 `앙상블 신호 방향`은 6개 호라이즌 확률을 고정 가중치로 합산해 `LONG / SHORT / FLAT`을 결정한다. 이 방식은 단순하고 해석 가능하다는 장점이 있지만, 장중 상태 변화에 둔감하고, 깊은 호가창 정보와 실행 가치 판단이 부족하다.

이 문서의 목표는 현재 구조를 상위 수준의 선물 트레이딩 엔진으로 고도화하기 위한 구현 계획과 TODO를 정리하는 것이다.

관련 현재 코드:

- [model/ensemble_decision.py](C:/Users/82108/PycharmProjects/futures/model/ensemble_decision.py:22)
- [model/multi_horizon_model.py](C:/Users/82108/PycharmProjects/futures/model/multi_horizon_model.py:95)
- [strategy/entry/checklist.py](C:/Users/82108/PycharmProjects/futures/strategy/entry/checklist.py:22)
- [features/technical/ofi.py](C:/Users/82108/PycharmProjects/futures/features/technical/ofi.py:19)
- [collection/kiwoom/realtime_data.py](C:/Users/82108/PycharmProjects/futures/collection/kiwoom/realtime_data.py:348)

## 목표 상태

### 현재 방식

- 6개 호라이즌 확률을 고정 가중치로 합산
- OFI, CVD, VWAP 중심의 체크리스트 필터
- 신뢰도는 있으나 확률 보정과 거부 구간이 약함
- 방향 예측과 실행 가치 판단이 거의 같은 흐름에 묶여 있음

### 목표 방식

- 상태 적응형 앙상블 게이팅
- `MLOFI + microprice + queue dynamics` 기반 미세구조 강화
- `meta-labeling`으로 실행 가치 별도 판정
- 신뢰도 보정과 abstention zone 도입
- toxicity 기반 리스크 차단 게이트 추가

## 기대 효과

아래 수치는 문헌 근거와 현재 구조를 기반으로 한 내부 추정치이며 보장값은 아니다.

### 보수적 기대

- 승률 `+1.5 ~ 3.0%p`
- 순기대수익 `+8 ~ 15%`
- Sharpe `+0.15 ~ 0.30`
- 최대낙폭 `-8 ~ 15%`

### 공격적 기대

- 승률 `+3 ~ 5%p`
- 순기대수익 `+15 ~ 30%`
- Sharpe `+0.30 ~ 0.50`
- 최대낙폭 `-15 ~ 25%`

## 원칙

1. 현재 엔진을 깨지 말고 레이어를 추가하는 방식으로 진화시킨다.
2. 각 단계는 독립적으로 켜고 끌 수 있어야 한다.
3. 지표 추가보다 검증 프레임워크를 먼저 같이 만든다.
4. 개선 여부는 반드시 OOS와 WFA 기준으로 판단한다.
5. 실거래 적용은 `shadow -> alert -> small size -> full` 순서로 진행한다.

## Implementation Plan

## Phase 0. Baseline Freeze

### 목적

현재 성능을 고정 기준선으로 저장해 이후 개선 효과를 비교할 수 있게 한다.

### 작업

- 현재 앙상블 방향 정확도 측정
- 시간대별 승률, 기대값, 손익분포 저장
- 체크리스트 항목별 통과율과 기여도 저장
- confidence calibration baseline 저장

### 산출물

- `baseline_ensemble_report.md`
- `baseline_metrics.json`

### 성공 기준

- 최소 최근 20거래일 기준 baseline 리포트 확보
- 이후 모든 개선안은 같은 평가 파이프라인으로 비교 가능

## Phase 1. Microstructure Upgrade

### 목적

현재 OFI를 다층 구조로 확장해 진입 직전 체결 압력 판단을 정교화한다.

### 구현 범위

- `MLOFI` 추가
- `microprice` 추가
- `imbalance slope`
- `queue depletion speed`
- `refill rate`
- `cancel/add ratio`

### 제안 파일

- `features/technical/mlofi.py`
- `features/technical/microprice.py`
- `features/technical/queue_dynamics.py`
- `features/feature_builder.py`
- `collection/kiwoom/realtime_data.py`

### 핵심 설계

- 최소 3호가, 가능하면 5호가까지 사용
- 1호가 단일 압력 대신 깊이별 가중 압력 벡터 생성
- 분봉 집계용 요약값과 틱 직전 진입용 초단기 상태값 분리

### 성공 기준

- 신규 피처 누락률 1% 미만
- 기존 OFI 대비 다음 1~3분 방향 설명력 개선
- 실시간 대시보드에 계산 상태 노출 가능

## Phase 2. Adaptive Gating Ensemble

### 목적

고정 가중치 앙상블을 상태 적응형 가중치 구조로 바꾼다.

### 구현 범위

- 호라이즌별 기본 예측 유지
- 상위 게이팅 모델이 현재 상태에 따라 각 호라이즌 가중치 조정
- 결과적으로 `up_score`, `down_score`, `flat_score`를 동적으로 계산

### 입력 후보

- 시간대
- macro regime
- micro regime
- ATR / realized vol
- spread
- MLOFI 요약값
- microprice drift
- 외인 흐름 강도
- 최근 3개 봉 방향 일관성

### 제안 파일

- `model/ensemble_gater.py`
- `model/ensemble_decision.py`
- `strategy/entry/time_strategy_router.py`

### 성공 기준

- 고정 가중치 대비 OOS log-loss 개선
- regime shift 구간에서 방향 전환 지연 감소
- 장초반 / 장마감 특수 구간 성능 악화 없음

## Phase 3. Meta-Labeling Gate

### 목적

방향이 맞는지와 실제로 진입할 가치가 있는지를 분리한다.

### 구현 범위

- 1차 모델: 방향 예측 유지
- 2차 모델: `take / skip / reduce size` 판단
- 메타 라벨은 실제 순손익, 목표 선도달, 손절 선도달, 비용 반영 결과로 생성

### 메타 피처 후보

- 1차 confidence
- up/down spread
- MLOFI
- microprice drift
- VWAP distance
- OFI persistence
- 외인 방향 변화율
- 시간대
- 직전 봉 구조
- Hurst / ATR / 변동성 상태

### 제안 파일

- `learning/meta_labeling.py`
- `strategy/entry/meta_gate.py`
- `strategy/entry/entry_manager.py`

### 성공 기준

- 거래 수는 감소해도 기대값과 Sharpe 개선
- false positive 감소
- 자동 진입 대비 수동 검토 구간 분리 가능

## Phase 4. Probability Calibration and Abstention

### 목적

confidence를 진짜 확률에 더 가깝게 만들고 애매한 구간은 진입을 거부한다.

### 구현 범위

- 호라이즌별 calibration
- 최종 앙상블 calibration
- reliability diagram 자동 저장
- abstention zone 도입
- confidence gap 기반 진입 보류

### 제안 파일

- `learning/calibration.py`
- `model/ensemble_decision.py`
- `dashboard/main_dashboard.py`

### 성공 기준

- calibration curve 개선
- Brier / log-loss 개선
- 신뢰도 높은 구간의 실제 적중률 일치도 향상

## Phase 5. Toxicity Risk Gate

### 목적

유동성 독성 급상승 구간에서 신규 진입을 막거나 사이즈를 강하게 줄인다.

### 구현 범위

- VPIN 또는 volume-time toxicity proxy
- spread expansion + MLOFI stress + trade intensity 조합
- circuit-breaker 연동

### 설계 원칙

- 방향 예측 신호로 사용하지 않는다
- 위험 회피 게이트로만 사용한다

### 제안 파일

- `features/technical/toxicity.py`
- `strategy/risk/toxicity_gate.py`
- `strategy/risk/circuit_breaker.py`

### 성공 기준

- tail loss 감소
- 급변장 재진입 손실 감소
- 전체 기대값 훼손 없이 MDD 개선

## 검증 계획

## 실험 순서

1. Baseline 저장
2. Phase 1 단독 실험
3. Phase 1 + 2 결합
4. Phase 1 + 2 + 3 결합
5. Calibration 추가
6. Toxicity gate 추가

## 평가 지표

- 방향 정확도
- precision / recall
- Brier score
- log-loss
- calibration error
- 평균 손익
- profit factor
- Sharpe
- max drawdown
- 거래당 기대값
- 시간대별 성능
- regime별 성능

## 검증 규칙

- 동일한 기간 분할 사용
- 최소 walk-forward 기준 유지
- 거래 비용 포함
- 슬리피지 포함
- 실거래 shadow 로그로 사후 검증

## 리스크와 대응

### 1. 과최적화

- 대응: 피처 수를 단계적으로 늘리고 WFA 고정

### 2. 데이터 품질 문제

- 대응: 호가 데이터 누락률 모니터링과 fallback 정의

### 3. 지연시간 증가

- 대응: 실시간 계산과 학습용 계산을 분리

### 4. 설명 가능성 저하

- 대응: 최종 의사결정에 기여한 상위 피처 로그 저장

### 5. 시스템 복잡도 증가

- 대응: feature flag 기반 단계별 롤아웃

## TODO List

## A. Baseline

- [ ] 최근 20거래일 기준 현재 앙상블 성능 리포트 생성
- [ ] confidence reliability table 저장
- [ ] 시간대별 / 레짐별 승률 표 저장
- [ ] 체크리스트 9개 항목 통과율 집계

## B. Data and Feature Plumbing

- [ ] 실시간 호가 3~5레벨 수집 가능 여부 확인
- [ ] 누락 FID 및 저장 구조 점검
- [ ] feature builder에 다층 호가 피처 추가 슬롯 확보
- [ ] 성능 병목 측정

## C. MLOFI / Microprice

- [ ] `mlofi.py` 생성
- [ ] `microprice.py` 생성
- [ ] `queue_dynamics.py` 생성
- [ ] 분봉 집계 로직 연결
- [ ] 디버그 로그 추가
- [ ] 대시보드 상태 표시 추가

## D. Adaptive Ensemble

- [ ] 게이팅 입력 스키마 정의
- [ ] baseline 고정 가중치와 병렬 계산
- [ ] `ensemble_gater.py` 프로토타입 구현
- [ ] 동적 가중치 로그 기록
- [ ] A/B 비교 리포트 생성

## E. Meta-Labeling

- [ ] 메타 라벨 정의 확정
- [ ] 학습 데이터셋 생성 파이프라인 작성
- [ ] `meta_gate.py` 구현
- [ ] `entry_manager.py` 연결
- [ ] `take / skip / reduce` 정책 정의

## F. Calibration

- [ ] 호라이즌별 calibration 적용 여부 점검
- [ ] 최종 앙상블 calibration 레이어 구현
- [ ] abstention threshold 실험
- [ ] reliability dashboard 확장

## G. Toxicity Gate

- [ ] toxicity proxy 정의
- [ ] volume-time 집계 방식 설계
- [ ] circuit breaker 연동
- [ ] 급변 구간 backtest 검증

## H. Rollout

- [ ] feature flag 추가
- [ ] shadow mode 배포
- [ ] alert only mode 배포
- [ ] reduced size live 테스트
- [ ] full rollout 기준 정의

## 구현 우선순위

### 즉시 시작

1. Baseline freeze
2. MLOFI + microprice
3. Adaptive gating prototype

### 그 다음

1. Meta-labeling
2. Calibration + abstention

### 마지막

1. Toxicity gate
2. Full rollout automation

## 추천 실행 순서

### Sprint 1

- Baseline 저장
- 다층 호가 데이터 확인
- MLOFI / microprice 구현

### Sprint 2

- feature builder 연결
- A/B 백테스트
- adaptive gating 프로토타입

### Sprint 3

- meta-labeling 데이터셋 구축
- meta gate 연결
- calibration 실험

### Sprint 4

- toxicity gate
- shadow 운영
- rollout 기준 확정

## 참고 문헌

- MLOFI: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3479741
- Order book signals: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2668277
- Deep order flow imbalance: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3900141
- Meta-labeling: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4032018
- VPIN 원저자 측: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1695596
- VPIN 비판 및 후속 검증: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2292602
- VPIN 추가 검토: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2584346

## 최종 한줄 정리

가장 먼저 할 일은 `baseline 고정 -> MLOFI/microprice 추가 -> adaptive gating -> meta-labeling` 순으로 현재 앙상블을 "방향 예측기"에서 "실행 가치까지 판단하는 상위 레벨 진입 엔진"으로 진화시키는 것이다.
