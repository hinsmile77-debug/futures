# 미륵이 전략 파라미터 운용 가이드 및 수익률 극대화 제안

---

## 목적

미륵이(KOSPI 200 선물 1분봉 자동매매) 수익률을 극대화하기 위한 **백테스트 인자, WFA(Walk-Forward Analysis), 시뮬레이션, 실전 반영 절차**에 사용되는 전략 파라미터를 정의한다.  
선정된 파라미터는 **주기적으로 교체**되며, 교체 결과와 성과 변화를 **모니터링**하는 목적으로 관리된다.

> 관련 코드
> - [config/strategy_params.py](config/strategy_params.py) — 파라미터 명세·탐색 공간·이력 관리
> - [backtest/param_optimizer.py](backtest/param_optimizer.py) — 그리드서치 → WFA → 적용 프레임워크
> - [strategy/entry/entry_manager.py](strategy/entry/entry_manager.py) — 실전 진입 흐름
> - [strategy/entry/staged_entry.py](strategy/entry/staged_entry.py) — 등급별 분할 진입
> - [backtest/slippage_simulator.py](backtest/slippage_simulator.py) — 슬리피지 반영 백테스트

> 참고
> - 운영 표는 가독성을 위해 41행으로 요약했다.
> - 실제 코드 기준 세부 파라미터는 47개다.
> - `J` 그룹은 `threshold_1m` ~ `threshold_30m` 6개, `K` 그룹은 `wfa_train_weeks`, `wfa_test_weeks` 2개로 구성된다.

> 신규 구현 코드 (v2026-05-07)
> - [config/strategy_registry.py](config/strategy_registry.py) — 전략 버전 레지스트리 (SQLite 영속, 단계별 성과·롤백 이력)
> - [strategy/param_drift_detector.py](strategy/param_drift_detector.py) — CUSUM 기반 성과 드리프트 조기 경보
> - [dashboard/strategy_dashboard_tab.py](dashboard/strategy_dashboard_tab.py) — 🧭 전략 운용현황 탭 (PyQt5)

---

## 핵심 제안

- `A + E + I`를 월간 최우선 최적화 축으로 고정한다. 진입 질, 손익비, 사이징이 수익률과 Sharpe에 가장 직접적이다.
- 승률만 올라가고 기대값이 떨어지는 조정은 기각한다. `atr_tp2_mult`, `partial_exit_ratio_*`, `account_base_risk`는 반드시 기대손익 기준으로 평가한다.
- 백테스트 대비 실전 성과가 약하면 파라미터보다 `슬리피지`, `지연(latency)`, `분할 진입`부터 점검한다.
- 레짐이 좋은 구간에만 크게 베팅한다. `RISK_ON × 추세장`은 공격적으로, `RISK_OFF × 급변장`은 신규 진입 금지 또는 강제 청산을 우선한다.
- 신규 파라미터 셋은 `WFA 통과 -> 2주 shadow/live 모니터링 -> 정식 반영` 순서로 승격한다.

---

## 추천 내용

### 1. 파라미터 구조 (11개 그룹, 운영 표 41행 / 실제 47개 파라미터)

| 그룹 | 이름 | 핵심 파라미터 | 현재값 | 탐색 범위 | 검토 주기 | 수익 영향도 |
|:----:|------|-------------|:------:|---------|:-------:|:---------:|
| **A** | 진입 신뢰도 | `entry_conf_neutral` | 0.58 | 0.54 ~ 0.66 (step 0.02) | 월 | ★★★★★ |
| **A** | 진입 신뢰도 | `entry_conf_risk_on` | 0.52 | 0.50 ~ 0.60 | 월 | ★★★★★ |
| **A** | 진입 신뢰도 | `entry_conf_risk_off` | 0.65 | 0.60 ~ 0.72 | 월 | ★★★★★ |
| **A** | 시간대 신뢰도 | `entry_conf_open_volatile` | 0.63 | 0.60 ~ 0.70 | 월 | ★★★★ |
| **A** | 시간대 신뢰도 | `entry_conf_stable_trend` | 0.58 | 0.55 ~ 0.65 | 월 | ★★★★ |
| **A** | 시간대 신뢰도 | `entry_conf_lunch_recovery` | 0.60 | 0.57 ~ 0.66 | 월 | ★★★★ |
| **A** | 시간대 신뢰도 | `entry_conf_close_volatile` | 0.62 | 0.59 ~ 0.68 | 월 | ★★★★ |
| **B** | 진입 등급 | `grade_a_min_pass` | 6 | 5 ~ 7 | 분기 | ★★★ |
| **B** | 진입 등급 | `grade_b_min_pass` | 4 | 3 ~ 5 | 분기 | ★★★ |
| **B** | 진입 등급 | `grade_c_min_pass` | 2 | 1 ~ 3 | 분기 | ★★ |
| **C** | 앙상블 가중치 | `ensemble_w_1m` | 0.10 | 0.05 ~ 0.20 | 분기 | ★★★ |
| **C** | 앙상블 가중치 | `ensemble_w_3m` | 0.15 | 0.10 ~ 0.25 | 분기 | ★★★ |
| **C** | 앙상블 가중치 | `ensemble_w_5m` | 0.20 | 0.10 ~ 0.30 | 분기 | ★★★ |
| **C** | 앙상블 가중치 | `ensemble_w_10m` | 0.20 | 0.10 ~ 0.30 | 분기 | ★★★ |
| **C** | 앙상블 가중치 | `ensemble_w_15m` | 0.20 | 0.10 ~ 0.30 | 분기 | ★★★ |
| **C** | 앙상블 가중치 | `ensemble_w_30m` | 0.15 | 0.05 ~ 0.25 | 분기 | ★★★ |
| **D** | 모델 블렌딩 | `gbm_weight_default` | 0.70 | 0.50 ~ 0.85 | 격주 | ★★★ |
| **D** | 모델 블렌딩 | `sgd_boost_threshold` | 0.62 | 0.58 ~ 0.68 | 격주 | ★★★ |
| **D** | 모델 블렌딩 | `sgd_cut_threshold` | 0.48 | 0.43 ~ 0.53 | 격주 | ★★★ |
| **E** | 청산 구조 | `atr_stop_mult` | 1.5 | 1.0 ~ 2.5 (step 0.25) | 주 | ★★★★★ |
| **E** | 청산 구조 | `atr_tp1_mult` | 1.0 | 0.5 ~ 2.0 | 주 | ★★★★★ |
| **E** | 청산 구조 | `atr_tp2_mult` | 1.5 | 1.0 ~ 3.0 | 주 | ★★★★ |
| **E** | 청산 구조 | `partial_exit_ratio_1` | 0.33 | 0.25 ~ 0.50 | 월 | ★★★ |
| **E** | 청산 구조 | `partial_exit_ratio_2` | 0.33 | 0.25 ~ 0.50 | 월 | ★★★ |
| **F** | 포지션 사이징 | `account_base_risk` | 1.0% | 0.5 ~ 2.0% | 월 | ★★★★ |
| **F** | 포지션 사이징 | `max_contracts` | 10 | 3 ~ 15 | 월 | ★★★ |
| **F** | 포지션 사이징 | `daily_loss_limit_pct` | 2.0% | 1.0 ~ 3.0% | 월 | ★★★ |
| **G** | Circuit Breaker | `cb_signal_flip_limit` | 5 | 3 ~ 8 | 격주 | ★★★ |
| **G** | Circuit Breaker | `cb_signal_flip_pause_min` | 15 | 10 ~ 30 | 격주 | ★★ |
| **G** | Circuit Breaker | `cb_consec_stop_limit` | 3 | 2 ~ 5 | 격주 | ★★★ |
| **G** | Circuit Breaker | `cb_accuracy_min_30m` | 0.35 | 0.28 ~ 0.45 | 격주 | ★★★ |
| **G** | Circuit Breaker | `cb_atr_mult_limit` | 3.0 | 2.0 ~ 4.5 | 격주 | ★★ |
| **H** | Hurst Exponent | `hurst_trend_threshold` | 0.55 | 0.50 ~ 0.65 | 분기 | ★★★★ |
| **H** | Hurst Exponent | `hurst_range_threshold` | 0.45 | 0.35 ~ 0.50 | 분기 | ★★★★ |
| **H** | Hurst Exponent | `hurst_max_lag` | 20 | 10 ~ 40 | 분기 | ★★★ |
| **I** | 적응형 켈리 | `kelly_lookback` | 20 | 10 ~ 40 | 월 | ★★★★ |
| **I** | 적응형 켈리 | `kelly_half_factor` | 0.50 | 0.30 ~ 0.70 | 월 | ★★★★ |
| **I** | 적응형 켈리 | `kelly_max_mult` | 1.50 | 1.00 ~ 2.00 | 월 | ★★★ |
| **I** | 적응형 켈리 | `kelly_min_mult` | 0.10 | 0.05 ~ 0.25 | 월 | ★★★ |
| **J** | 타겟 임계값 | `threshold_1m ~ 30m` | 0.0002 ~ 0.0012 | 호라이즌별 2 ~ 4배 범위 | 분기 | ★★ |
| **K** | WFA 설정 | `wfa_train_weeks`, `wfa_test_weeks` | 8, 1 | 4 ~ 16, 1 ~ 2 | 분기 | ★ |

세부 파라미터 메모:
- `J` 그룹 현재값: `threshold_1m=0.0002`, `threshold_3m=0.0003`, `threshold_5m=0.0004`, `threshold_10m=0.0006`, `threshold_15m=0.0008`, `threshold_30m=0.0012`
- `K` 그룹 현재값: `wfa_train_weeks=8`, `wfa_test_weeks=1`

---

### 2. 결합 최적화 그룹 (Coupled Groups)

동시에 최적화해야 효과가 있는 파라미터 묶음이다.  
`param_optimizer.py`에서 `--group` 옵션으로 호출한다.

| 그룹명 | 포함 파라미터 | 설명 |
|--------|-------------|------|
| `entry_quality` | entry_conf_neutral, entry_conf_risk_on/off, grade_a/b_min_pass | 진입 퀄리티 전체 구조 |
| `time_zone_conf` | 4개 시간대별 신뢰도 | 장 전체 시간대 균형 |
| `exit_structure` | atr_stop_mult, atr_tp1/tp2_mult, partial_exit_ratio_1/2 | 손익비 구조 |
| `hurst_bounds` | hurst_trend/range_threshold, hurst_max_lag | gap ≥ 0.05 제약 |
| `ensemble` | 6개 호라이즌 가중치 | 합계 = 1.0 제약 |
| `circuit_breaker` | 5개 CB 파라미터 | 시스템 안정성 |
| `sizing` | account_base_risk, max_contracts, kelly 4개 | 자금 관리 통합 |

권장 탐색 순서:
- 월간: `entry_quality -> exit_structure -> sizing`
- 분기: `hurst_bounds -> ensemble -> time_zone_conf`
- 실전 괴리 발생 시: 파라미터 재탐색보다 `slippage`와 `latency`부터 확인

---

### 3. 최적화 목적함수

```
1순위 (최대화): Sharpe Ratio

하드 제약 (모두 충족해야 파라미터 후보 인정):
  ├─ MDD        ≤ 15%
  ├─ 승률       ≥ 53%
  └─ Sharpe     ≥ 1.5

소프트 제약 (위반 시 복합 점수 차감):
  ├─ Profit Factor  ≥ 1.3
  ├─ Calmar         ≥ 1.0
  └─ WFA 창당 거래  ≥ 20회

복합 점수 가중치:
  Sharpe(50%) + 승률(20%) + Profit Factor(15%) + Calmar(15%)

WFA 통과 기준 (Phase 2 실전 진입 기준):
  평균 Sharpe ≥ 1.5 / 평균 MDD ≤ 15% / 평균 승률 ≥ 53% / 최소 10개 창
```

운영 원칙:
- 승률 상승만 있고 `Profit Factor`와 `Calmar`가 악화되면 승격하지 않는다.
- 월간 재최적화의 목적은 거래수 증가가 아니라 **기대값 개선**이다.

---

### 4. 파라미터 유효성 제약 (자동 검사 6개 + 탐색공간 제약)

`validate_params()` 함수에서 아래 6개 조건을 자동으로 검사한다.  
위반 시 해당 파라미터 조합은 그리드서치에서 자동 탈락된다.

| 제약 | 조건 | 위반 예시 |
|------|------|---------|
| 앙상블 가중치 합 | = 1.0 (±0.05) | 합계 0.95 → 탈락 |
| Hurst 경계 gap | trend − range ≥ 0.05 | 0.55 − 0.52 = 0.03 → 탈락 |
| 부분청산 비율 합 | ratio1 + ratio2 ≤ 1.0 | 0.60 + 0.50 = 1.10 → 탈락 |
| 1차 손익비 | tp1 / stop ≥ 0.5 | 0.50 / 2.00 = 0.25 → 탈락 |
| SGD 임계값 gap | boost − cut ≥ 0.08 | 0.62 − 0.58 = 0.04 → 탈락 |
| 등급 임계값 순서 | A > B > C | A=5, B=5 → 탈락 |

추가 메모:
- `partial_exit_ratio_1`, `partial_exit_ratio_2`의 개별 범위 0.25 ~ 0.50은 `PARAM_SPACE` 탐색 범위로 이미 제한된다.
- `threshold_*`와 `wfa_*`는 값 자체보다 **상대 구조**가 중요하므로 분기 단위 WFA로 검증한다.

---

### 5. 주기별 검토 및 교체 스케줄

```
매일 15:40   적응형 켈리 자동 누적 (코드 자동 — 개입 불필요)
             adaptive_kelly.record() → 매거래 결과 자동 반영

매주 금요일  청산 파라미터 (E 그룹) 손익비 점검
             트리거: 주간 승률 < 50% 또는 Profit Factor < 1.1

격주 월요일  모델 블렌딩(D) + Circuit Breaker(G) 검토
             트리거: CB 발동 일수 > 3일/주 또는 SGD 비중 고착

매월 1일     신뢰도(A/B) + 사이징(F/I) 그리드서치 + WFA
             명령어: python -m backtest.param_optimizer --group entry_quality --top-n 20
                     python -m backtest.param_optimizer --group sizing --top-n 20
             트리거: 월간 수익률 < 0% 또는 Sharpe < 1.5

분기 초      구조 파라미터 전체 WFA 재최적화
             명령어: python -m backtest.param_optimizer --group ensemble
                     python -m backtest.param_optimizer --group hurst_bounds
                     python -m backtest.param_optimizer --group exit_structure
             트리거: 분기 Sharpe < 1.5 또는 MDD > 12% 또는 승률 < 53%
```

---

### 6. 파라미터 교체 절차

```
STEP 1  param_optimizer.py 그리드서치 실행 (coupled_group 단위)
STEP 2  상위 20개 후보 → WFA 26주 교차검증
STEP 3  OPT_OBJECTIVES 하드 제약 전체 통과 확인
STEP 4  기준선 대비 복합 점수 개선량 확인 (Sharpe delta, MDD delta, PF delta)
STEP 5  통과 시 → optimizer.apply_best() 호출
          config/strategy_params.py PARAM_CURRENT 업데이트
          PARAM_HISTORY에 버전·변경 이력·WFA 결과 append
STEP 6  settings.py 반영 후 2주 shadow/live 모니터링
STEP 7  Slack #maitreya 채널에 변경 이력, 기대효과, 롤백 기준 보고
```

롤백 기준:
- 반영 후 2주 누적 Sharpe < 0.8
- 반영 후 2주 MDD가 직전 버전 대비 20% 이상 악화
- 실전 슬리피지가 백테스트 가정보다 25% 이상 나빠짐

---

### 7. 파라미터 선정 근거 (그룹별 우선순위)

#### A 그룹 — 진입 신뢰도 (최우선 최적화 대상)

`entry_conf_neutral`은 전체 거래의 **60 ~ 70%를 차지하는 NEUTRAL 레짐**에서 적용되는 기준선이다.  
0.02 단위 변화가 거래수·승률·Sharpe 모두에 가장 큰 영향을 준다.

- 현재값 0.58은 보수적 기준선
- 백테스트에서 **0.60 ~ 0.62 구간**이 Sharpe 최적점으로 나타나는 경향
- 시간대별 신뢰도는 레짐 신뢰도와 병렬 적용되므로 세트로 최적화가 필수

#### E 그룹 — 청산 구조 (손익비 핵심)

KOSPI200 선물 1분봉 시스템에서 **손익비(RR)가 수익률의 55 ~ 65%를 결정**한다.

- `atr_stop_mult` 1.5는 실전에서 **1.25 ~ 1.75 범위**가 유력 후보
- `atr_tp1_mult`가 stop보다 너무 작으면 승률은 유지돼도 기대값이 급격히 나빠질 수 있음
- 권장 손익비 기준: `TP1/Stop ≥ 0.7`, `TP2/Stop ≥ 1.0`
- 수익률 극대화 관점에서는 `partial_exit_ratio_1`을 과도하게 높이지 않는 편이 유리함

#### H 그룹 — Hurst Exponent (MDD 킬러)

횡보장(H < 0.45) 진입 차단만으로 **MDD 25 ~ 40% 감소** 효과가 기대된다.

- `hurst_range_threshold` 상향(0.45 → 0.47 ~ 0.48)이 MDD 개선에 즉각 효과
- 너무 높이면 진입 기회 과소화로 Sharpe가 떨어질 수 있음
- **최적 데드존 폭**은 `0.45 ~ 0.55` 유지가 기본

#### I 그룹 — 적응형 켈리 (슬럼프 방어 + 좋은 구간 확대)

- `kelly_half_factor=0.5`는 이론 켈리의 50%로 실전 적정선
- `kelly_lookback=20`은 민감도와 안정성의 균형점
- `kelly_min_mult=0.10`은 완전 거래 정지보다 계좌 회복 속도 측면에서 유리
- 좋은 구간에서는 `kelly_max_mult`가 수익률 상방을, 나쁜 구간에서는 `kelly_min_mult`가 생존성을 담당

#### C 그룹 — 앙상블 가중치 (장세별 방향성 확대)

현재 5·10·15분 호라이즌 중심 구조는 1분봉 시스템에 적합하나,  
실전 누적 데이터가 충분해질수록 **레짐별 호라이즌 기대값 재배분**이 중요해진다.

- 추세장: `15m`, `30m` 비중 상향이 유리할 가능성
- 급변장: `1m`, `3m` 비중 상향보다 **신규 진입 축소**가 우선
- 분기 최적화 시 `time_zone_conf + ensemble` 결합 검토 권장

---

### 8. 추가할 내용과 수익률 극대화 실행안

#### 8-1. 코드 기준 활용 가능한 레버 점검

| 레버 | 현재 상태 | 기대 효과 | 권장 조치 |
|------|-----------|----------|-----------|
| `StagedEntryManager` | 진입 매니저 연동 | B/C급 진입 슬리피지 완화 | 2차 진입 성사율·취소율 로깅 강화 |
| `SlippageSimulator` | 백테스트 측 구현 | 백테스트-실전 괴리 축소 | 최적화 결과를 슬리피지 반영 기준으로만 승인 |
| `RegimeStrategyMapper` | 코드 존재, 메인 미연결 | 좋은 장에서만 크게 베팅 | macro × micro 레짐별 PnL 검증 후 연결 검토 |
| `VolatilityTargeter` | 코드 존재, 메인 미연결 | 저변동 구간 사이즈 확대, 고변동 구간 축소 | `target_vol_daily=2%` 기준 shadow test |
| `DynamicSizer` | 코드 존재, 메인 미연결 | 켈리·변동성·레짐 통합 사이징 | 기존 `position_sizer`와 A/B 비교 검증 |

#### 8-2. 쌈박한 수익률 극대화 방안

| 상황 | 1차 조정 | 2차 조정 | 기대 효과 |
|------|---------|---------|----------|
| 승률은 유지되는데 수익률이 둔화 | `atr_tp2_mult` 상향 검토 | `partial_exit_ratio_1` 0.25 ~ 0.30 테스트 | 큰 추세 수익 포착 확대 |
| 거래수는 많은데 Profit Factor가 낮음 | `entry_conf_neutral`, `entry_conf_open_volatile` 상향 | `grade_b_min_pass` 상향 | 헛진입 제거 |
| 추세장에서 수익이 약함 | `ensemble_w_15m`, `ensemble_w_30m` 상향 | `entry_conf_risk_on` 완화 테스트 | 추세 추종 강화 |
| 실전만 성과가 약함 | `staged_entry` 유지, B급 2차 진입 품질 점검 | `latency > 300ms` 신규 진입 제한 검토 | 슬리피지 누수 축소 |
| MDD만 높고 기대값은 유지 | `hurst_range_threshold` 0.47 ~ 0.48 테스트 | `daily_loss_limit_pct`, `cb_consec_stop_limit` 보수화 | 꼬리위험 축소 |
| 저변동일에 수익 기회 상실 | `VolatilityTargeter` shadow test | `RISK_ON/NEUTRAL + 추세장`에서만 size up | Sharpe 상향 |

#### 8-3. 레짐 기반 공격/방어 운영안

`collection/macro/regime_strategy_map.py` 기준 권장 해석:

| 레짐 조합 | 권장 스탠스 | 해석 |
|-----------|------------|------|
| `RISK_ON × 추세장` | 공격적 추세추종 | 진입 기준 완화 + 사이즈 확대 후보 |
| `NEUTRAL × 추세장` | 표준 추세추종 | 기본 수익 구간 |
| `RISK_ON × 횡보장` | 약한 역추세 또는 소형 진입 | 과도한 홀딩 금지 |
| `NEUTRAL × 급변장` | 신규 진입 중단 | 수익보다 생존 우선 |
| `RISK_OFF × 급변장` | 강제 청산/관망 | 계좌 방어 최우선 |

핵심은 **나쁜 장에서 덜 잃는 것보다, 좋은 장에서 더 크게 먹는 구조를 만들되 나쁜 장에서는 아예 쉬는 것**이다.

---

### 9. 모니터링 지표 (파라미터 교체 후 추적 항목)

| 지표 | 목표 | 경보 임계값 | 확인 주기 |
|------|------|-----------|---------|
| Sharpe Ratio | ≥ 1.5 | < 1.0 | 주 |
| MDD | ≤ 15% | > 20% | 일 |
| 승률 | ≥ 53% | < 48% | 주 |
| Profit Factor | ≥ 1.3 | < 1.0 | 주 |
| CB 발동 횟수 | ≤ 1회/주 | > 3회/주 | 일 |
| 30분 이동 정확도 | ≥ 55% | < 40% | 분 (실시간) |
| 적응형 켈리 배율 | 0.5 ~ 1.2 | < 0.2 또는 = MAX | 일 |
| SGD 비중 | 10 ~ 40% | = min(10%) 또는 = max(50%) | 일 |

추가 권장 지표:
- `live_slippage_pts`: 실전 체결 슬리피지와 백테스트 가정치 차이
- `regime_expectancy`: macro × micro 레짐별 거래당 기대손익
- `stage2_fill_rate`: B급 2차 진입 성사율
- `time_slot_expectancy`: 시간대별 기대손익과 MDD

---

### 10. 전략 파라미터 운용현황 대시보드 제안

#### 10-1. 대시보드 목적

전략 파라미터 운용현황 대시보드는 단순 모니터링 화면이 아니라,  
**"어떤 전략 버전이 언제 어떤 검증을 통과했고, 왜 현재 실전에 올라와 있으며, 이전 버전 대비 실제 성과가 기대값을 상회/중간/하회하는지"**를 한눈에 보여주는 **전략 운용 관제판**이어야 한다.

판단해야 할 질문은 아래 5개다.

- 지금 실전에 올라간 전략은 무엇인가
- 이 전략은 백테스트, WFA, 시뮬, shadow/live 검증을 언제 통과했는가
- 직전 운용 전략 대비 무엇이 바뀌었는가
- 기대 성과 대비 현재 실전 성과는 초과/중간/하회 중 어디인가
- 지금 유지, 감시 강화, 교체, 롤백 중 어떤 액션이 맞는가

#### 10-2. 권장 UI 컨셉

권장 컨셉은 **"전략 연구실 + 실전 운용 관제실"** 혼합형이다.

- 상단은 현재 전략의 상태를 즉시 판단하는 `관제형 헤더`
- 중단은 전략 간 비교와 기대값 괴리를 읽는 `의사결정 차트`
- 하단은 변경 이력과 근거를 확인하는 `리서치 로그`

시각 방향:
- 배경은 기존 대시보드 톤을 유지하되, 전략 운용 탭은 `청록 + 주황 + 라임` 중심으로 초과/중립/경보를 명확히 분리
- 숫자보다 상태 해석이 먼저 보이도록 `초과`, `중간`, `하회`, `감시`, `교체 후보`, `롤백 검토` 배지를 전면 배치
- 트레이더가 3초 안에 읽도록 `현재 전략`, `기대값 대비 상태`, `이전 대비 차이`, `추세 변화`를 첫 화면에 고정

#### 10-3. 추천 탭 구조

기존 대시보드에는 이미 `🧠 자가학습`, `🎯 학습 효과 검증기`, `📈 학습 성장 추이`, `📊 손익 추이`가 있으므로,  
신규로 아래 탭을 추가하는 것이 가장 자연스럽다.

**추천 탭명**
- `🧭 전략 운용현황`

**탭 역할**
- 현재 실전 전략 상태판
- 이전 전략 대비 성과 비교
- 전략 승격/교체/롤백 히스토리
- 파라미터 변경의 효과 추적

#### 10-4. 한 화면 레이아웃 제안

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 현재 운용 전략 | v1.3 | 2026-05-07 승격 | 상태: 기대값 상회 | 롤백경보 없음 │
├───────────────┬───────────────────────────────┬─────────────────────────┤
│ 전략 카드      │ 기대값 대비 실전 성과 차트       │ 승격/교체 타임라인       │
│ 현재/이전 비교 │ Backtest / WFA / Sim / Live    │ 버전별 교체 히스토리     │
├───────────────┼───────────────────────────────┼─────────────────────────┤
│ 파라미터 변경  │ 성과 추이 멀티차트              │ 레짐·시간대 기대값 매트릭스 │
│ heatmap        │ Sharpe / MDD / PF / WR / PnL  │ 어디서 먹고 잃는지        │
├───────────────┴───────────────────────────────┴─────────────────────────┤
│ 전략 평가 로그 / 변경 사유 / 승인자 / 롤백 기준 / WFA 요약 / 시뮬 코멘트  │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 10-5. 핵심 카드 1: 현재 운용 전략 카드

화면 좌상단에 가장 크게 보여야 할 카드다.

표시 항목:
- `현재 운용 전략명`
- `전략 버전`
- `활성화 일시`
- `직전 전략 버전`
- `최근 평가 단계`
- `현재 상태`: 기대값 상회 / 기대값 부합 / 기대값 하회
- `최근 2주 판정`: 유지 / 감시 강화 / 교체 후보 / 롤백 검토

예시 문구:

```text
현재 전략: NEUTRAL_Trend_v1.3
승격: 2026-05-07 08:55
직전 전략: v1.2
평가 단계: WFA 통과 → 시뮬 통과 → 실전 8일차
현재 판정: 기대값 상회 (+Sharpe 0.22, MDD -1.8%p)
```

#### 10-6. 핵심 카드 2: 기대값 대비 실전 성과 매트릭스

이 카드가 이 대시보드의 핵심이다.  
트레이더는 전략의 절대 성과보다 **"예상한 만큼 나오고 있는가"**를 먼저 봐야 한다.

표 구조:

| 단계 | Sharpe | MDD | 승률 | PF | 기대값 상태 |
|------|--------|-----|------|----|-------------|
| Backtest | 1.88 | 11.2% | 55.8% | 1.42 | 기준선 |
| WFA | 1.63 | 12.5% | 54.1% | 1.31 | 통과 |
| Simulation | 1.57 | 13.0% | 53.6% | 1.28 | 근접 |
| Live 2주 | 1.81 | 10.9% | 56.3% | 1.39 | 상회 |

상태 규칙:
- `상회`: Live Sharpe/PF가 WFA 기준보다 유의미하게 좋고 MDD가 낮음
- `중간`: WFA/시뮬 범위 내
- `하회`: Live Sharpe 또는 PF가 기준 하회, 혹은 MDD 경보

#### 10-7. 핵심 카드 3: 이전 전략 대비 비교 카드

현재 전략과 직전 전략을 같은 축에서 나란히 놓아야 한다.

표시 항목:
- `Sharpe delta`
- `MDD delta`
- `승률 delta`
- `PF delta`
- `평균 보유시간 delta`
- `거래수 delta`
- `레짐별 기대값 delta`

표현 방식:
- 좌측 `이전 전략`
- 우측 `현재 전략`
- 중앙 `▲ +0.24`, `▼ -1.8%p` 같은 변화값

트레이더 관점에서 가장 중요한 문구:
- `수익률은 늘었지만 MDD도 늘었는가`
- `승률은 줄었지만 기대값은 좋아졌는가`
- `좋아진 것이 특정 레짐에만 국한되는가`

#### 10-8. 핵심 차트 1: 전략 버전별 성과 추이 차트

사용자 요청 2번에 해당하는 핵심 차트다.

반드시 넣을 차트:
- `버전별 누적 PnL 추이`
- `버전별 Sharpe / MDD / 승률 멀티라인 차트`
- `전략 교체 시점 세로 마커`

추천 표현:
- X축: 날짜
- Y축 1: 누적 PnL
- Y축 2: 선택 지표(Sharpe 또는 PF)
- 세로선: `v1.0 -> v1.1`, `v1.1 -> v1.2`
- 배경 band: `상회`, `중간`, `하회` 상태 구간

읽는 포인트:
- 전략 교체 직후 성과가 개선되는지
- 개선이 일시적인지 지속적인지
- 성과 상승이 거래수 증가 때문인지 기대값 개선 때문인지

#### 10-9. 핵심 차트 2: 파라미터 변경 영향 Heatmap

이 차트는 트레이더 인사이트를 가장 많이 올려준다.

세로축:
- 버전

가로축:
- `A`, `C`, `D`, `E`, `F`, `H`, `I` 핵심 파라미터

셀 표현:
- 초록: 상향 조정
- 빨강: 하향 조정
- 회색: 변화 없음
- 셀 우측 작은 숫자: 변화량

오른쪽 보조 컬럼:
- `Sharpe delta`
- `MDD delta`
- `PF delta`

이 Heatmap으로 바로 읽히는 질문:
- 어떤 파라미터 교체가 성과 개선에 자주 연결되는가
- `entry_conf_neutral` 조정이 실제로 먹히는가
- `atr_tp2_mult` 확대가 PF를 올리는가
- `hurst_range_threshold` 상향이 MDD를 얼마나 줄였는가

#### 10-10. 핵심 차트 3: 레짐·시간대 기대값 매트릭스

전략이 어디서 돈을 벌고 잃는지 보여주는 실전형 차트다.

행:
- `RISK_ON`, `NEUTRAL`, `RISK_OFF`

열:
- `OPEN_VOLATILE`, `STABLE_TREND`, `LUNCH_RECOVERY`, `CLOSE_VOLATILE`

셀 값:
- 거래수
- 승률
- 평균 PnL
- 기대값 등급

색상:
- 진한 초록: 기대값 우수
- 연두: 양호
- 주황: 중립
- 빨강: 손실 구간

이 차트는 전략이 잘 먹히는 구간과 죽는 구간을 직관적으로 보여주므로,  
단순 전체 Sharpe보다 실전 의사결정 가치가 높다.

#### 10-11. 하단 로그 패널: 전략 평가 이력

하단에는 숫자가 아닌 **판단의 근거**가 남아야 한다.

로그 항목:
- 평가 일시
- 평가 단계: Backtest / WFA / Simulation / Live Review
- 승격/보류/반려/롤백 결정
- 변경 파라미터 요약
- 변경 사유
- 승인 메모
- 리스크 메모

예시:

```text
2026-05-07 08:55 | v1.3 승격
- entry_conf_neutral 0.58 -> 0.60
- atr_tp2_mult 1.5 -> 2.0
- WFA Sharpe 1.63 / MDD 12.5% / 승률 54.1%
- 시뮬 10일 PF 1.34 확인
- 결정: 실전 반영 / 2주 shadow 모니터링
```

#### 10-12. 기존 대시보드와의 연결 방식

현재 코드 기준으로는 기존 패널을 버릴 필요가 없다.  
오히려 아래처럼 역할을 나누는 것이 좋다.

| 기존 패널 | 유지 역할 | 신규 탭과 관계 |
|-----------|----------|----------------|
| `🧠 자가학습 모니터` | SGD/GBM 학습 상태 | 모델 건강상태 참조 |
| `🎯 학습 효과 검증기` | 캘리브레이션, 등급별 성과 | 전략 평가의 보조 근거 |
| `📈 학습 성장 추이` | 일/주/월 성과 추이 | 전략 버전 추이 차트의 입력 재료 |
| `📊 손익 추이` | 거래 손익 히스토리 | 전략 교체 마커와 결합 가능 |
| `🧭 전략 운용현황` | 전략 버전, 평가, 교체, 기대값 대비 상태 | 신규 핵심 탭 |

즉, 신규 탭은 기존 패널의 상위 관제 레이어다.

#### 10-13. 최소 구현 데이터 구조 제안

이 대시보드를 제대로 만들려면 전략 버전 단위의 이력이 필요하다.

권장 저장 구조:

```python
strategy_registry = {
    "strategy_id": "NEUTRAL_Trend_v1.3",
    "version": "v1.3",
    "activated_at": "2026-05-07 08:55",
    "previous_version": "v1.2",
    "stage": "LIVE",
    "stage_history": [
        {"stage": "BACKTEST", "evaluated_at": "...", "sharpe": 1.88, "mdd_pct": 0.112},
        {"stage": "WFA", "evaluated_at": "...", "sharpe": 1.63, "mdd_pct": 0.125},
        {"stage": "SIM", "evaluated_at": "...", "sharpe": 1.57, "mdd_pct": 0.130},
    ],
    "live_metrics": {"sharpe": 1.81, "mdd_pct": 0.109, "win_rate": 0.563, "pf": 1.39},
    "changed_params": {
        "entry_conf_neutral": {"from": 0.58, "to": 0.60},
        "atr_tp2_mult": {"from": 1.5, "to": 2.0},
    },
    "expected_band": {"sharpe_low": 1.45, "sharpe_high": 1.75},
    "verdict": "OUTPERFORM",
}
```

추가 저장 테이블 제안:
- `strategy_versions`
- `strategy_stage_results`
- `strategy_param_changes`
- `strategy_live_snapshots`

#### 10-14. 최소 구현 우선순위

1차 구현:
- 현재 전략 카드
- 이전 전략 비교 카드
- 버전별 성과 추이 차트
- 전략 평가 로그

2차 구현:
- 파라미터 변경 Heatmap
- 레짐·시간대 기대값 매트릭스
- 기대값 대비 상태 자동 판정

3차 구현:
- 롤백 추천 엔진
- "다음 교체 후보 전략" 추천 카드
- 전략별 SHAP/레짐 기여도 연결

#### 10-15. 가장 쌈박한 한 줄 제안

**"지금 돌아가는 전략이 왜 돌아가고 있는지, 직전 전략보다 진짜 나아졌는지, 이 성과가 기대 범위 안인지"를 3초 안에 판단하게 만드는 관제형 탭**으로 설계하는 것이 가장 좋다.

추천 명칭:
- `Strategy Ops`
- 한글 탭명: `🧭 전략 운용현황`

---

### 11. Implementation Plan / TODO

#### 11-1. 구현 목표

이 가이드의 구현 목표는 아래 4가지를 실제 코드와 데이터 흐름으로 연결하는 것이다.

- 전략 버전의 평가 이력을 일관된 형식으로 저장
- 현재 실전 전략과 직전 전략의 성과 차이를 자동 계산
- 기대값 대비 현재 상태를 `상회 / 중간 / 하회`로 판정
- 기존 대시보드 위에 `🧭 전략 운용현황` 탭을 추가하여 한눈에 보여주기

구현 원칙:
- 기존 `dashboard/main_dashboard.py`를 확장하고 재작성하지 않는다
- `strategy version registry`를 단일 진실 공급원으로 사용한다
- 백테스트/WFA/시뮬/실전 성과는 같은 키 체계로 저장한다
- 자동 승격은 하더라도 자동 실전 반영은 하지 않고, 최종 승인 단계를 둔다

#### 11-2. 권장 구현 순서

가장 안전한 순서는 아래와 같다.

1. 저장 구조 정의
2. 전략 버전 이력 자동 적재
3. 기대값 대비 판정 엔진 구현
4. 대시보드용 조회 API 작성
5. `🧭 전략 운용현황` 탭 UI 구현
6. 경보·롤백 자동화

#### 11-3. Phase별 Implementation Plan

| Phase | 목표 | 주요 작업 | 산출물 | 권장 기간 |
|------|------|----------|--------|----------|
| Phase 0 | 설계 고정 | 전략 버전/평가 단계/판정 규칙 확정 | DB 스키마, 버전 규칙, 상태 규칙 | 0.5 ~ 1일 |
| Phase 1 | 데이터 저장 | 전략 버전·평가 결과·파라미터 변경 이력 저장 | 신규 테이블 + CRUD 유틸 | 1 ~ 2일 |
| Phase 2 | 평가 파이프라인 | Backtest/WFA/Sim/Live 결과를 공통 구조로 적재 | registry service + verdict engine | 1 ~ 2일 |
| Phase 3 | 대시보드 백엔드 | 현재 전략 요약, 이전 전략 비교, 추세/heatmap 데이터 조회 | dashboard query API | 1일 |
| Phase 4 | UI 구현 | `🧭 전략 운용현황` 탭과 핵심 카드/차트 구현 | StrategyOpsPanel | 2 ~ 3일 |
| Phase 5 | 검증 및 롤아웃 | 과거 이력 적재, QA, 경보/롤백 점검 | 운영 가이드 + QA 체크리스트 | 1일 |

#### 11-4. Phase 0: 설계 확정

결정해야 할 항목:

- 전략 ID 규칙: 예) `NEUTRAL_Trend_v1.3`
- 평가 단계 enum: `BACKTEST`, `WFA`, `SIM`, `SHADOW`, `LIVE`
- 현재 상태 enum: `OUTPERFORM`, `IN_RANGE`, `UNDERPERFORM`
- 운영 액션 enum: `KEEP`, `WATCH`, `REPLACE_CANDIDATE`, `ROLLBACK_REVIEW`
- 기대값 band 계산 규칙: `WFA ± tolerance`, 또는 `Sim median ± range`

완료 기준:
- 전략 버전 네이밍 규칙 문서화 완료
- Live 상태 판정 규칙 합의
- 직전 전략 대비 delta 산식 확정

#### 11-5. Phase 1: 데이터 저장 구조 구현

권장 위치:
- 기존 `trades.db`를 확장하거나, 별도 `strategy_registry.db`를 추가
- 구현 난이도를 낮추려면 우선 `trades.db` 확장이 현실적

권장 테이블:

| 테이블 | 용도 | 핵심 컬럼 |
|--------|------|----------|
| `strategy_versions` | 전략 마스터 | `strategy_id`, `version`, `activated_at`, `previous_version`, `stage`, `verdict` |
| `strategy_stage_results` | 평가 단계별 결과 | `strategy_id`, `stage`, `evaluated_at`, `sharpe`, `mdd_pct`, `win_rate`, `pf` |
| `strategy_param_changes` | 파라미터 변경 이력 | `strategy_id`, `param_name`, `old_value`, `new_value`, `changed_at` |
| `strategy_live_snapshots` | 실전 추적 스냅샷 | `strategy_id`, `snapshot_at`, `sharpe`, `mdd_pct`, `win_rate`, `pf`, `pnl_krw` |
| `strategy_events` | 운영 로그 | `strategy_id`, `event_type`, `event_at`, `message`, `note` |

관련 파일:
- `utils/db_utils.py`
- `backtest/param_optimizer.py`
- 신규 `strategy/ops/registry.py`

#### 11-6. Phase 2: 평가 파이프라인 구현

핵심 아이디어:
- Backtest/WFA/Simulation/Live 결과를 따로 보관하지 말고, 모두 `strategy_stage_results`로 적재
- `strategy_versions`에는 현재 활성 전략과 직전 전략 포인터만 유지

구현 포인트:
- `param_optimizer.apply_best()`에서 `PARAM_HISTORY` append와 함께 전략 버전 레코드 생성
- WFA 결과는 즉시 `strategy_stage_results`에 저장
- 시뮬 결과는 별도 저장 함수로 stage=`SIM` 레코드 생성
- 실전은 일별 또는 주별 snapshot job으로 적재
- snapshot 적재 시 기대값 band와 비교하여 `OUTPERFORM / IN_RANGE / UNDERPERFORM` 계산

권장 신규 모듈:
- `strategy/ops/registry.py`
- `strategy/ops/verdict_engine.py`
- `strategy/ops/snapshot_collector.py`

#### 11-7. Phase 3: 대시보드 백엔드 조회 API

신규 탭이 필요로 하는 조회 함수:

- `fetch_current_strategy_summary()`
- `fetch_previous_strategy_summary()`
- `fetch_strategy_stage_results(strategy_id)`
- `fetch_strategy_version_trend(limit=20)`
- `fetch_strategy_param_heatmap(limit=20)`
- `fetch_strategy_regime_timeslot_matrix(strategy_id)`
- `fetch_strategy_event_log(strategy_id, limit=100)`

권장 구현 위치:
- `utils/db_utils.py` 확장
- 또는 신규 `dashboard/strategy_ops_queries.py`

완료 기준:
- UI 없이도 dict/json 형태로 탭 전체 데이터가 조회됨
- `main.py`에서 1회 호출로 필요한 모든 블록 데이터 조립 가능

#### 11-8. Phase 4: UI 구현 계획

신규 패널명:
- `StrategyOpsPanel`

권장 파일:
- 신규 `dashboard/strategy_ops_panel.py`
- `dashboard/main_dashboard.py`에 탭 등록 + adapter 메서드 추가

필수 위젯:
- 현재 전략 카드
- 기대값 대비 실전 성과 매트릭스
- 이전 전략 대비 비교 카드
- 버전별 성과 추이 차트
- 파라미터 변경 Heatmap
- 레짐·시간대 기대값 매트릭스
- 전략 평가 로그 테이블

권장 adapter 메서드:

```python
def update_strategy_ops(self, data: dict):
    """
    data keys:
      current_strategy
      previous_strategy
      stage_results
      version_trend
      param_heatmap
      regime_timeslot_matrix
      event_log
    """
```

#### 11-9. Phase 5: 검증 및 운영 적용

검증 절차:

- 과거 `PARAM_HISTORY`로 더미 전략 버전 데이터 생성
- 최근 4 ~ 8주 실전 손익으로 live snapshot 적재
- 수동으로 3개 이상 전략 버전 시나리오 입력
- `상회 / 중간 / 하회` 판정이 기대대로 나오는지 확인
- 교체 직후, 교체 실패, 롤백 후보 케이스를 각각 QA

운영 전 체크:
- 현재 전략이 항상 1개만 active 상태인지
- 직전 전략 링크가 끊기지 않는지
- stage 결과가 누락되어도 UI가 깨지지 않는지
- 과거 데이터가 적을 때도 graceful fallback 되는지

#### 11-10. 파일별 작업 분담

| 파일 | 작업 내용 |
|------|----------|
| `config/strategy_params.py` | 전략 파라미터 메타 정보 유지, 버전 규칙 문서 반영 |
| `backtest/param_optimizer.py` | 파라미터 교체 시 전략 버전/평가 결과 저장 훅 추가 |
| `utils/db_utils.py` | 전략 버전/단계 결과/heatmap 조회 함수 추가 |
| `main.py` | 신규 탭 데이터 수집, 주기적 refresh, snapshot 적재 호출 |
| `dashboard/main_dashboard.py` | 신규 탭 등록, adapter 메서드 연결 |
| `dashboard/strategy_ops_panel.py` | 핵심 카드/차트/로그 UI 구현 |
| `strategy/ops/registry.py` | 전략 버전 CRUD |
| `strategy/ops/verdict_engine.py` | 기대값 대비 판정 계산 |
| `strategy/ops/snapshot_collector.py` | 실전 snapshot 적재 |

#### 11-11. TODO 리스트

**P0. 설계 / 스키마**
- [ ] 전략 ID 규칙 확정
- [ ] stage enum 확정
- [ ] verdict enum 확정
- [ ] 기대값 band 계산식 확정
- [ ] `strategy_versions` 테이블 스키마 정의
- [ ] `strategy_stage_results` 테이블 스키마 정의
- [ ] `strategy_param_changes` 테이블 스키마 정의
- [ ] `strategy_live_snapshots` 테이블 스키마 정의

**P1. 초격차 수익 극대화 파이프라인 연동**
- [ ] `strategy/shadow_evaluator.py` 통합 (가상 체결 미러링 연동)
- [ ] `REGIME_PARAM_OVERRIDES`에 `kelly_max_mult` 폭주 제한 해제 연동
- [ ] WFA 결과 분포도를 이용한 Plateau(고원) / Overfitting 판별 모듈 구현
- [ ] `strategy_events` 테이블 스키마 정의

**P1. 저장 / 파이프라인**
- [ ] DB migration 또는 init 코드 작성
- [ ] 전략 버전 CRUD 유틸 작성
- [ ] stage 결과 저장 함수 작성
- [ ] param change 저장 함수 작성
- [ ] live snapshot 저장 함수 작성
- [ ] `param_optimizer.apply_best()`에 registry 저장 연결
- [ ] simulation 결과 저장 훅 정의
- [ ] daily/weekly live snapshot 적재 루틴 작성

**P2. 판정 엔진**
- [ ] 현재 전략 vs 직전 전략 delta 계산 함수 작성
- [ ] 기대값 band 계산 함수 작성
- [ ] `OUTPERFORM / IN_RANGE / UNDERPERFORM` 판정 함수 작성
- [ ] `KEEP / WATCH / REPLACE_CANDIDATE / ROLLBACK_REVIEW` 액션 매핑 작성
- [ ] 롤백 경보 조건 구현

**P3. 대시보드 백엔드**
- [ ] 현재 전략 요약 조회 API 작성
- [ ] 이전 전략 요약 조회 API 작성
- [ ] version trend 조회 API 작성
- [ ] param heatmap 조회 API 작성
- [ ] regime × timeslot matrix 조회 API 작성
- [ ] event log 조회 API 작성
- [ ] 대시보드용 종합 payload assembler 작성

**P4. UI**
- [ ] `StrategyOpsPanel` 클래스 생성
- [ ] 현재 전략 카드 UI 구현
- [ ] 기대값 대비 실전 성과 매트릭스 UI 구현
- [ ] 이전 전략 비교 카드 UI 구현
- [ ] 버전별 성과 추이 차트 UI 구현
- [ ] 파라미터 변경 Heatmap UI 구현
- [ ] 레짐·시간대 매트릭스 UI 구현
- [ ] 전략 평가 로그 테이블 UI 구현
- [ ] 상태 배지 컬러 시스템 정의
- [ ] 모바일/창 축소 대응 레이아웃 점검

**P5. 운영 자동화**
- [ ] 교체 직후 2주 shadow/live 모니터링 배너 구현
- [ ] 기대값 하회 시 경보 알림 구현
- [ ] 롤백 추천 메시지 구현
- [ ] 일일/주간 전략 상태 요약 export 구현
- [ ] Slack 보고 메시지 포맷 추가

#### 11-12. v1 최소 구현 범위

가장 먼저 끝내야 하는 v1 범위는 아래 6개다.

- [ ] 전략 버전 저장 구조
- [ ] WFA / Simulation / Live 결과 적재
- [ ] 현재 전략 카드
- [ ] 이전 전략 대비 비교 카드
- [ ] 버전별 성과 추이 차트
- [ ] 전략 평가 로그

이 6개만 구현돼도 "현재 운용 전략이 왜 올라와 있고, 이전보다 좋아졌는지"는 충분히 판단할 수 있다.

#### 11-13. Definition of Done

아래 조건을 만족하면 구현 완료로 본다.

- 대시보드에서 현재 active 전략 1개가 명확히 표시된다
- 직전 전략과 delta 비교가 숫자와 배지로 동시에 보인다
- Backtest/WFA/Sim/Live 4단계 결과가 한 표에 정리된다
- 전략 교체 시점이 손익 추이 차트에 마커로 표시된다
- 파라미터 변경 이력과 성과 변화가 연결돼 보인다
- 현재 전략이 기대값 상회/중간/하회인지 자동 판정된다
- 하회 시 감시 또는 롤백 검토 상태가 경보로 노출된다

---

### 12. CUSUM 성과 드리프트 조기경보 시스템

#### 12-1. 문제 정의

기존 롤백 기준(2주 Sharpe < 0.8)은 **이미 성과가 망가진 뒤 반응**한다.  
목표는 롤백 경보가 뜨기 **2~4일 전**에 "이 전략 이상하다"를 감지하는 것이다.

#### 12-2. CUSUM 원리

```
S_n = max(0, S_{n-1} - z_n - k)

여기서:
  z_n   = (오늘 PnL - WFA기준 기대PnL) / WFA기준 PnL표준편차
  k     = 0.5   (작은 일시적 하락은 무시 — 슬랙 계수)
  S_n   = 하방 누적합산 (커질수록 위험)
```

정상 전략에서 z_n ≈ 0이면 S_n도 0 근처를 유지한다.  
성과 저하 시 z_n이 음(음수 PnL)으로 쏠리면 S_n이 단조 증가 → 경보 발동.

#### 12-3. 경보 수준 정의

| S_n 범위 | 수준 | 색상 | 권장 조치 |
|---------|------|------|----------|
| < 2.0 | CLEAR | 초록 | 정상 운용 |
| 2.0 ~ 4.0 | WATCHLIST | 노랑 | 파라미터 재점검 예약 (최우선 E/A 그룹) |
| 4.0 ~ 6.0 | ALARM | 주황 | param_optimizer 즉시 실행 + 사이즈 80%로 임시 축소 |
| ≥ 6.0 | CRITICAL | 빨강 | 롤백 검토 / 사이즈 50% 축소 / 슬랙 경보 발송 |

#### 12-4. 구현 파일

```
strategy/param_drift_detector.py
  └── DriftDetector        (단일 지표 CUSUM)
  └── MultiMetricDriftDetector (PnL + 승률 + PF 종합)
  └── get_drift_detector() (전역 싱글턴)
```

#### 12-5. 연동 절차

```python
# main.py 15:40 일일 마감 후 호출
from strategy.param_drift_detector import get_drift_detector
det = get_drift_detector()
level, composite_msg = det.update(
    daily_pnl  = today_pnl_krw,
    daily_wr   = today_win_rate,
    daily_pf   = today_profit_factor,
)
if level >= 1:  # WATCHLIST 이상
    notify_slack(composite_msg)
```

#### 12-6. 버전 교체 시 CUSUM 리셋

전략 버전 교체 시 반드시 CUSUM을 리셋하고 기준값을 신규 WFA 결과로 갱신한다.

```python
det.reset_all(
    pnl_ref = (new_wfa_daily_mean, new_wfa_daily_std),
    wr_ref  = (new_wfa_wr_mean,    new_wfa_wr_std),
    pf_ref  = (new_wfa_pf_mean,    new_wfa_pf_std),
)
```

---

### 13. Anchored Walk-Forward (AWFA) — 데이터 효율 극대화

#### 13-1. 기존 WFA의 한계

기존 Rolling WFA (슬라이딩 윈도우):
```
[────8주────][1주]
       [────8주────][1주]
              [────8주────][1주]
```
- 각 창이 독립적이어서 **초기 데이터가 버려짐**
- 데이터가 26주 미만일 때 창 수가 너무 적어 신뢰도 낮음

#### 13-2. AWFA 개념

```
[──────────────────────][1주]  ← 고정 시작점 + 확장 윈도우
[────────────────────────────][1주]
[──────────────────────────────────][1주]
```
- **시작점 고정** + 학습 창을 점점 확장
- 초기 데이터를 **누적해서 모두 활용**
- 데이터 부족 초기 단계에 특히 유리

#### 13-3. 두 방식 결합 전략

| 데이터 보유 기간 | 권장 WFA 방식 |
|----------------|-------------|
| < 16주 | AWFA 우선 (데이터 부족) |
| 16 ~ 26주 | AWFA + Rolling 병행, 두 결과의 평균 Sharpe |
| ≥ 26주 | Rolling WFA 기본 + AWFA 보완 |

#### 13-4. 구현 위치

`backtest/walk_forward.py` 에 `AnchoredWalkForwardValidator` 클래스 추가 권장.

```python
class AnchoredWalkForwardValidator:
    """
    고정 시작점 확장 윈도우 WFA.
    args:
      test_weeks: 각 창의 검증 기간 (기본 1)
      min_train_weeks: 최소 학습 창 길이 (기본 4)
    """
```

---

### 14. 레짐-파라미터 매핑 테이블 (Regime-Param Lookup)

#### 14-1. 개념

단일 파라미터 셋으로 모든 레짐을 운용하는 것은 **RISK_ON 추세장에서 너무 보수적**이 되거나  
**RISK_OFF 급변장에서 너무 공격적**이 되는 문제가 있다.

해결책: **레짐별 경량 파라미터 오버라이드 테이블**.  
기본 파라미터를 base로 두고, 레짐 감지 즉시 해당 오버라이드를 덮어씌운다.

#### 14-2. 레짐-파라미터 매핑 예시

| 레짐 조합 | `entry_conf` 오버라이드 | `atr_stop_mult` 오버라이드 | `kelly_max_mult` 오버라이드 | 비고 |
|-----------|----------------------|--------------------------|--------------------------|------|
| `RISK_ON × 추세장` | -0.02 (완화) | 1.75 (스톱 약간 넓힘) | 1.8 (사이즈 확대) | 공격적 추세추종 |
| `NEUTRAL × 추세장` | 기본값 | 1.5 | 1.5 | 표준 |
| `RISK_ON × 횡보장` | +0.02 (강화) | 1.25 (빠른 손절) | 1.0 | 역추세 소형 진입 |
| `NEUTRAL × 횡보장` | +0.03 (강화) | 1.25 | 0.8 | 보수적 |
| `NEUTRAL × 급변장` | 진입 금지 | — | 0.0 | 관망 |
| `RISK_OFF × 급변장` | 강제 청산 | — | 0.0 | 계좌 방어 |

#### 14-3. 구현 원칙

- 오버라이드 값은 WFA로 **레짐별 독립 검증** 필요 (하지만 데이터 부족 시 경험값으로 시작)
- 오버라이드는 PARAM_CURRENT 기준값에 **delta 방식**으로 적용 (절댓값 덮어쓰기 금지)
- 레짐이 변경되는 즉시 (매분 파이프라인 STEP 4) 오버라이드 적용
- 오버라이드 이력을 `strategy_regime_matrix` 에 기록

#### 14-4. 구현 위치

`config/strategy_params.py` 하단에 `REGIME_PARAM_OVERRIDES` 딕셔너리 추가:

```python
REGIME_PARAM_OVERRIDES = {
    ("RISK_ON",  "TREND"):     {"entry_conf_neutral": -0.02, "kelly_max_mult": +0.30},
    ("NEUTRAL",  "TREND"):     {},   # 기본값 그대로
    ("RISK_ON",  "RANGE"):     {"entry_conf_neutral": +0.02, "atr_stop_mult": -0.25},
    ("NEUTRAL",  "RANGE"):     {"entry_conf_neutral": +0.03, "kelly_max_mult": -0.50},
    ("NEUTRAL",  "VOLATILE"):  {"entry_conf_neutral": 9999},  # 진입 금지
    ("RISK_OFF", "VOLATILE"):  {"entry_conf_neutral": 9999},  # 강제 청산
}
```

---

### 15. 실전 운용 체크리스트 (코드 연동 기준)

#### 15-1. 파라미터 교체 전 체크 (STEP 5 전)

```
[ ] WFA 26주 통과 확인 (avg_sharpe ≥ 1.5, avg_mdd ≤ 15%, avg_wr ≥ 53%)
[ ] 기존 파라미터 대비 복합 점수 delta > 0 확인
[ ] validate_params() 6개 제약 전체 통과
[ ] strategy_registry.register_version() 로 이력 저장
[ ] param_drift_detector.reset_all() 로 CUSUM 리셋
[ ] 대시보드 🧭 탭에서 승격 확인
```

#### 15-2. 파라미터 교체 후 2주 모니터링 체크

```
[ ] 매일 15:40 drift_detector.update() 호출 여부 확인
[ ] WATCHLIST 이상 경보 발생 여부 확인
[ ] 롤백 기준: Sharpe < 0.8 OR MDD 이전 대비 +20% 이상 악화
[ ] 2주 경과 후 verdict 재계산 및 Slack 보고
```

#### 15-3. 대시보드 🧭 탭 운용 절차

```
장 시작 전:
  → 현재 전략 카드 상태 배지 확인 (CLEAR / WATCHLIST / ALARM)
  → 레짐×시간대 매트릭스에서 오늘 예상 취약 구간 파악

장 중:
  → CUSUM 드리프트 배지 실시간 확인 (ALARM 이상 시 사이즈 축소 검토)

장 마감 후 15:40:
  → live_snapshot 저장 (strategy_registry.record_live_snapshot())
  → drift_detector 업데이트
  → Slack 일일 요약 발송

주간 금요일:
  → 버전 성과 추이 확인 (WFA 기준 대비 Live 괴리)
  → WATCHLIST 이상이면 다음 주 param_optimizer 스케줄 잡기
```

---

### 16. 파라미터 버전 이력

| 버전 | 날짜 | 주요 변경 | WFA Sharpe | WFA MDD | WFA 승률 | 비고 |
|------|------|---------|-----------|--------|---------|------|
| v1.0 | 2026-05-07 | 초기 기준값 (설계 명세) | — | — | — | Phase 2 검증 전 |

> 파라미터 교체 시 `PARAM_HISTORY` (config/strategy_params.py) 에 자동 append 됨

---

*최종 업데이트: 2026-05-07 | 미륵이 v7.0 기준*

---

## 17. 실전 수익률 초격차(Alpha Generation)를 위한 추가 제안 (v2026-05)

미륵이 전략의 수익 극대화를 위해 기존 프레임워크에 추가 적용할 수 있는 **"쌈박하고 놀라운 제안"** 3가지.  
모두 코드로 연결 가능한 실전 우선순위 항목이다.

### 17-1. Shadow Strategy Evaluator (섀도우 트레이딩 및 Hot-Swap)

**핵심 개념:**  
파라미터 변경 통과 후 2주 모니터링 구간에서 "실제로는 체결시키지 않지만, 현재 Live 틱 데이터 흐름 속에서 어떤 신호가 몇 시에 발생했고 예상 PnL이 얼마인지"를 백그라운드로 계산한다 (`Shadow Trading`).

- **효과:** 시뮬레이션 환경(슬리피지 가정)과 실전(진짜 호가 공백) 간 괴리를 원천 차단.  
  Live와 Shadow의 2주 수익이 동기화(`Sync Score ≥ 0.70`)될 때에만 **Hot-Swap**(무중단 전략 교체)을 실시.
- **구현 현황:**
  1. `strategy/shadow_evaluator.py` — `ShadowEvaluator.process_tick()` 구현 완료
  2. `sync_score()` — Live/Shadow 일별 PnL 피어슨 상관계수 계산
  3. `is_hotswap_ready()` — 3가지 조건 자동 판정

관련 코드: `strategy/shadow_evaluator.py`

### 17-2. 레짐 인식형 Kelly 사이징 2.0 (Regime-Adjusted Dynamic Kelly)

**핵심 개념:**  
단순 20일 승률/손익 기반 Kelly가 아니라, **"오늘 장세(Regime)와 CUSUM 배지 조합"**에 따라 Kelly 상한선을 순간적으로 확대·축소하는 기능.

- **효과:** `RISK_ON × 추세장 × CUSUM==CLEAR` 삼중 조합에서만 비중을 집중 → 수익 극대화.
- **구현 현황:**
  - `config/strategy_params.py`의 `REGIME_PARAM_OVERRIDES` — `kelly_max_mult` delta 포함 완료
  - `apply_regime_overrides()` 함수 — 매분 파이프라인 STEP 6에서 호출

관련 코드: `config/strategy_params.py`, `REGIME_PARAM_OVERRIDES`

### 17-3. 파라미터 민감도 고원(Plateau) 히트맵 (대시보드 확장)

**핵심 개념:**  
Parameter Optimizer 결과를 2D 히트맵으로 시각화하여, 선택된 파라미터가 '우연히 솟아오른 핀스냅(Overfitting)'인지 '안정적인 고원(Plateau)' 한가운데 있는지 한눈에 판단.

- **효과:** WFA 성과가 좋더라도 주변 파라미터가 모두 적자 구간이면 과최적화로 간주.  
  §18의 `stability_score` 지표와 연동하면 과최적화 제로(Zero-Overfit) 선정 가능.
- **구현 방향:** `dashboard/strategy_dashboard_tab.py` 히트맵 패널 추가 (Phase 4 우선순위)

---

## 18. 파레토 최적 파라미터 선정 (Pareto-Front Selection)

### 18-1. 왜 단일 Sharpe 최적화는 위험한가

그리드서치에서 Sharpe만 최대화하면 다음 문제가 발생한다.

- Sharpe는 높지만 MDD가 극단적으로 크거나
- Sharpe는 높지만 거래수가 적어 통계적 신뢰도 낮거나
- Sharpe는 높지만 주변 파라미터가 모두 적자 → "핀스냅(Pin-snap) 과최적화"

해결책: **다목적 최적화(Multi-Objective)로 Pareto 전선을 찾고, 그 중 가장 안정적인 "고원 중심점"을 선택.**

### 18-2. Pareto Front 개념 및 선정 기준

두 목적함수 f1(Sharpe), f2(−MDD)를 동시에 최대화하는 파라미터 집합을 찾는다.

```
Sharpe
  ↑
4 │          *  ← Pareto 전선
  │        *
3 │      * ← 고원 중심 (최종 선택)
  │    *
2 │  *
  └──────────────→ −MDD (MDD 낮을수록 좋음)
```

**고원 중심점 선정 기준:**  
주변 파라미터(±1 step)의 Sharpe 표준편차가 가장 작은 Pareto-optimal 점 선택.

```
stability_score = 1 / std(Sharpe of ±1-step neighborhood)
```

값이 클수록 과최적화 위험이 낮다. `stability_score < 2.0`이면 핀스냅으로 간주·탈락.

### 18-3. WFA 통과 기준 확장

```
기존: avg_Sharpe ≥ 1.5

추가: avg_Sharpe ≥ 1.5  AND  stability_score ≥ 2.0
```

### 18-4. 구현 방향

`backtest/param_optimizer.py`에 `run_pareto()` 메서드 추가:

```python
def run_pareto(self, coupled_group: str, top_n: int = 10) -> dict:
    """
    Pareto 전선 파라미터 선정.
    1. 전체 그리드에서 (Sharpe, -MDD) Pareto-optimal 집합 추출
    2. 각 후보의 neighborhood stability_score 계산
    3. stability_score 최대 파라미터 반환
    """
```

추가 구현 파일 제안: `backtest/pareto_selector.py`

---

## 19. 피처 분포 드리프트 감지 (Regime Fingerprint)

### 19-1. 개념 — CUSUM보다 2~5일 빠른 시장 구조 변화 감지

CUSUM은 **결과(PnL)**로 이상을 감지한다 → 손실이 이미 발생한 후 반응.

피처 분포 드리프트는 **원인(시장 구조)**의 변화를 선행 감지한다:
> "모델이 학습한 시장과 지금 시장이 얼마나 다른가?"

WFA 학습 데이터의 핵심 피처 분포를 저장하고, Live 데이터와 비교.  
분포가 크게 달라지면 CUSUM보다 **2~5일 빨리** "이 전략의 근거가 흔들렸다"를 감지.

### 19-2. 감지 방법 — PSI (Population Stability Index)

핵심 피처 3개 (CVD·VWAP·OFI)의 분포를 PSI로 비교:

```
PSI = Σ (A_i - B_i) × ln(A_i / B_i)

  여기서:
    A_i = WFA 학습 데이터의 구간별 비율
    B_i = 최근 20일 Live 데이터의 구간별 비율

경보 기준:
  PSI < 0.10 : 안정 (CLEAR)
  PSI 0.10~0.20: 경미한 변화 (WATCHLIST) — 월간 재최적화 2주 앞당김
  PSI > 0.20 : 구조 변화 (ALARM)    — 즉시 param_optimizer 실행
  PSI > 0.30 : 심각한 변화 (CRITICAL) — 해당 구간 신규 진입 중단
```

### 19-3. 구현 방향

```python
# strategy/regime_fingerprint.py (신규)
class RegimeFingerprint:
    def save_training_fingerprint(self, wfa_features: list) -> None:
        """WFA 학습 피처 분포 저장 (버전 교체 시 갱신)."""

    def update_live(self, features: dict) -> float:
        """PSI 계산 후 반환 (매분 STEP 4 후 호출)."""

    def get_level(self) -> int:
        """현재 경보 수준 (DriftLevel 호환)."""
```

### 19-4. 연동 절차

```python
# main.py — STEP 4 직후 매분 호출
psi = fingerprint.update_live(features)
if psi > 0.20:
    notify_slack(f"[RegimeFingerprint] PSI={psi:.3f} — 시장 구조 변화 감지, param_optimizer 예약")
```

**CUSUM과의 역할 분리:**

| 감지기 | 대상 | 반응 시점 | 권장 조치 |
|--------|------|----------|---------|
| CUSUM | 성과(PnL) 저하 | 손실 발생 후 1~3일 | 파라미터 교체 |
| RegimeFingerprint | 시장 구조 변화 | 손실 발생 전 2~5일 | 재최적화 예약 |

두 감지기를 **동시에 운용**하면 대응 속도가 대폭 빨라진다.

---

## 20. Live-Shadow 동기화 점수 (Hot-Swap 품질 지표)

### 20-1. 개념

섀도우 전략이 2주 동안 좋은 성과를 보여도,  
Live 전략과 **PnL 타이밍이 일치하지 않으면** Hot-Swap은 위험하다.

"섀도우가 정말 구조적으로 나은가, 아니면 이번 2주 시장이 우연히 맞아떨어진 것인가?"를  
정량적으로 분리하는 기준이 바로 **Sync Score**다.

### 20-2. Sync Score 계산 및 Hot-Swap 조건

```
Sync Score = Pearson r(live_daily_pnl, shadow_daily_pnl)
              최근 10거래일 기준

Hot-Swap 승인 3가지 조건 (모두 충족 필요):
  ① Shadow 2주 누적 PnL > Live 2주 누적 PnL × 1.10  (10% 이상 우세)
  ② Sync Score ≥ 0.70  (같은 날 같이 이기고 짐 — 구조적 우위)
  ③ Shadow WFA Sharpe ≥ 현재 버전 WFA Sharpe

조건 미충족 시: Hot-Swap 보류, 1주 추가 관찰 후 재판단
```

### 20-3. Sync Score 해석

| Sync Score | 해석 | Hot-Swap 판정 |
|-----------|------|--------------|
| ≥ 0.70 | 섀도우가 Live를 구조적으로 개선 | **승인** |
| 0.50~0.70 | 일부 구간에서만 우세 (우연 가능성) | 보류 |
| < 0.50 | 다른 시장 구조에서 성과 (불일치) | 거부 |
| 음수 | 섀도우가 Live와 역행 | 즉시 종료 |

### 20-4. 구현 현황

`strategy/shadow_evaluator.py`에 `sync_score()`, `is_hotswap_ready()` 구현 완료:

```python
evaluator = get_shadow_evaluator("v1.4-candidate", candidate_params)
score = evaluator.sync_score(live_daily_pnls=last_10_days_pnl)
ready, reason = evaluator.is_hotswap_ready(live_daily_pnls, live_wfa_sharpe=1.63)

if ready:
    registry.register_version("v1.4", ...)  # Hot-Swap 실행
else:
    notify_slack(f"[HotSwap 보류] {reason}")
```

### 20-5. 전략 교체 게이트 통합

```
WFA 통과
  → Shadow 가동 (2주)
    → Sync Score ≥ 0.70 AND 수익 10% 우세 AND WFA Sharpe 유지
      → Hot-Swap 승인
        → registry.register_version() + drift_detector.reset_all()
```

이 게이트 없이 진행하면 "백테스트에서 좋아 보이는 전략"이 실전에서 예상과 다르게 작동할 때  
발견이 너무 늦어진다.

---

*최종 업데이트: 2026-05-07 | 미륵이 v7.0 기준 | §18~20 신규 추가*
