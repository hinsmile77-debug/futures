# SGD / GBM 피처 분리 보기

> 기준일: 2026-05-22
> 기준 파일: `main.py`, `learning/online_learner.py`, `learning/batch_retrainer.py`, `features/feature_builder.py`

## 1. 결론 먼저

| 항목 | 내용 |
|---|---|
| GBM 피처 | `data/db/shap_feature_registry.json` 의 `active_features` 91개 |
| SGD 피처 | 운영 중에는 사실상 `self.model.feature_names` 와 동일 |
| 공통점 | 둘 다 `FeatureBuilder.get_feature_vector(feature_names)` 로 같은 순서 벡터 사용 |
| 차이점 | GBM은 레지스트리 91열이 기준이고, SGD는 GBM 미학습 초기에는 `sorted(features.keys())` 로 임시 부트스트랩 가능 |
| 핵심 해석 | 현재 미륵이는 "SGD 전용 피처셋"과 "GBM 전용 피처셋"을 따로 유지하지 않고, 거의 같은 입력 축을 공유함 |

## 2. GBM 피처

### 2-1. 기준

- 기준 원천: `data/db/shap_feature_registry.json` -> `active_features`
- 학습 조립: `learning/batch_retrainer.py::_load_from_db()`
- 행렬 크기: `X[n_samples, 91]`
- 적용 대상: 1m, 3m, 5m, 10m, 15m, 30m 전체 호라이즌 공통

### 2-2. 축 구조

| 축 | 의미 | 개수 |
|---|---|---:|
| A. 장중 내부 상태 축 | 가격, 체결, 호가 미시구조, 변동성, 독성 | 42 |
| B. 수급 포지셔닝 축 | 외국인/기관/개인/프로그램 순매수 방향 | 11 |
| C. 옵션 심리 축 | PCR 기반 옵션 편향 | 5 |
| D. 매크로 레짐 축 | VIX, 미국 지수, 환율, 금리 기반 외부 환경 | 9 |
| E. 데이터 품질 축 | 소스 가용성, stale, fallback, 품질 점수 | 24 |
| 합계 |  | 91 |

### 2-3. 세부 피처

`cvd_divergence`, `cvd_direction`, `cvd`, `cvd_slope`, `cvd_exhaustion`, `cvd_exhaustion_signal`

`vwap_position`, `vwap`, `above_vwap`

`ofi_norm`, `ofi_pressure`, `ofi_imbalance`, `ofi_raw`, `ofi_reversal_speed`, `ofi_reversal_signal`

- 역할: 매수/매도 우위와 추세 지속 가능성 판단
- CORE 3 직접 포함: `cvd_divergence`, `vwap_position`, `ofi_norm`

#### A-2. 호가 미시구조 축 (15)

`avg_volume`

`microprice`, `microprice_bias`, `microprice_slope`, `microprice_depth_bias`

`mlofi_norm`, `mlofi_pressure`, `mlofi_slope`

`queue_signal`, `queue_signal_ma`, `queue_momentum`, `queue_depletion_speed`, `queue_refill_rate`, `imbalance_slope`, `cancel_add_ratio`

- 역할: 체결 이전 단계의 호가 압력과 체결 대기열 변화 반영
- 특징: 초단기 진입 타이밍과 체결 직전 압박 감지에 강함

#### A-3. 변동성 / 독성 레짐 축 (12)

`atr`, `atr_ratio`, `hurst`, `spread_ticks`

`toxicity_score`, `toxicity_score_ma`, `toxicity_atr_stress`, `toxicity_spread_stress`, `toxicity_flow_stress`, `toxicity_queue_stress`, `toxicity_cancel_stress`, `toxicity_regime_code`

- 역할: 지금 구간이 정상 추세장인지, 독성 높은 소음장인지 구분
- 특징: 진입 허용 여부와 confidence 해석의 배경축

### B. 수급 포지셔닝 축 (11)

이 축은 시장 참여자별 방향 베팅을 본다. 가격 자체보다 "누가 어느 쪽으로 누적 포지션을 쌓는가"에 가깝다.

`foreign_futures_net`, `foreign_call_net`, `foreign_put_net`

`retail_futures_net`, `institution_futures_net`

`program_arb_net`, `program_non_arb_net`

`foreign_retail_divergence`

`program_foreign_net_krw`, `program_institution_net_krw`, `program_individual_net_krw`

- 역할: 외국인 선물 주도, 개인 역추세, 프로그램 수급 동행 여부 반영
- 특징: 단기 가격 신호보다 느리지만 방향 conviction 보강에 유용

### C. 옵션 심리 축 (5)

이 축은 옵션시장 심리를 PCR로 압축한 것이다.

`opt_pcr_norm`, `opt_pcr_bearish`, `opt_pcr_bullish`, `opt_pcr_extreme`, `opt_pcr_slope_norm`

- 역할: 옵션시장이 risk-off인지 risk-on인지 요약
- 특징: 추세 추종보다 과열/공포 구간 해석에 도움

### D. 매크로 레짐 축 (9)

이 축은 장중 내부 데이터가 아니라 외부 시장 환경을 본다.

`macro_vix`, `macro_vix_abs`, `macro_sp500_chg`, `macro_nasdaq_chg`, `macro_krw_chg`, `macro_us10y_chg`, `macro_risk_on`, `macro_risk_off`, `macro_event_flag`

- 역할: 글로벌 위험 선호와 한국 장의 개장 레짐 보정
- 특징: 같은 미시구조 신호라도 매크로 축에 따라 해석이 달라질 수 있음

### E. 데이터 품질 축 (24)

이 축은 시장 방향을 직접 예측하기보다 "지금 입력을 얼마나 믿을 수 있는가"를 모델에 같이 알려준다. 미륵이 피처 행렬의 중요한 특징이다.

#### E-1. 수급 품질 (9)

`quality_investor_supported`, `quality_investor_futures_supported`, `quality_investor_program_supported`, `quality_investor_option_supported`, `quality_investor_stale`, `quality_investor_age_sec`, `quality_investor_fetch_count`, `quality_investor_source_code`, `quality_investor_reason_code`

#### E-2. 옵션 품질 (1)

`opt_available`

#### E-3. 매크로 품질 (5)

`macro_quality_available`, `macro_quality_stale`, `macro_quality_age_sec`, `macro_quality_fallback_used`, `macro_quality_source_code`

#### E-4. 전역 품질 (9)

`feature_recoverable_errors`, `feature_degraded`, `feature_quality_score`

`quality_option_available`, `quality_macro_available`, `quality_supply_available`

`quality_macro_stale`, `quality_macro_age_sec`, `quality_macro_fallback_used`

## 3. SGD 피처

### 3-1. 기준

- 운영 기준: `main.py` 에서 `self.model.feature_names` 를 그대로 사용
- 예측/학습 조립: `self.feature_builder.get_feature_vector(self.model.feature_names)`
- 학습기: `learning/online_learner.py`
- 스케일링: 호라이즌별 `StandardScaler.partial_fit()`

### 3-2. 현재 운영상 SGD가 실제로 보는 피처

대부분의 정상 운영 구간에서는 SGD도 GBM과 같은 91개 피처를 본다.

이유는 다음과 같다.

1. `main.py` 가 예측 시 `self.model.feature_names` 순서로 피처 벡터를 만든다.
2. 검증 완료 후 SGD `learn()` 도 같은 순서의 벡터를 받아 `partial_fit()` 한다.
3. `self.model.feature_names` 는 보통 GBM 모델 저장값 또는 `active_features` 기반으로 유지된다.

즉, 현재 미륵이에서 SGD는 별도 레지스트리를 갖기보다 GBM 피처 순서를 공유하는 온라인 보정기 역할에 가깝다.

### 3-3. SGD만의 예외 구간

GBM 미학습 초기에는 다음 예외가 있다.

- `main.py` 에서 `if not self.model.feature_names and features: self.model.set_feature_names(sorted(features.keys()))`
- 이 시점에는 SGD가 `FeatureBuilder.build()` 가 만든 런타임 키 전체를 정렬한 순서로 먼저 부트스트랩될 수 있다.

이 예외 때문에 초기에만 SGD 피처 집합이 GBM 레지스트리와 잠깐 다를 수 있다.

### 3-4. SGD 피처를 따로 볼 때의 해석

현재 시점에서 "SGD 피처"를 따로 본다는 것은 보통 아래 둘 중 하나다.

1. 운영 정상 구간의 SGD 입력
- 사실상 GBM과 같은 91개 열

2. GBM 미학습 부트스트랩 구간의 SGD 입력
- `FeatureBuilder` 런타임 키 기준
- 여기에는 `cvd_monotone_ratio`, `bear_exhaustion`, `bull_exhaustion`, `bull_reversal_signal`, `bear_reversal_signal` 같은 신형 피처가 포함될 수 있음

## 4. 공통 벡터 조립 흐름

```text
GBM
  raw_features DB 적재
    -> batch_retrainer._load_from_db()
    -> active_features 순서 선택
    -> X[n_samples, 91]
    -> horizon별 GBM 학습
```

```text
SGD
  FeatureBuilder.build(...)
    -> self._last_features(dict)
    -> get_feature_vector(self.model.feature_names)
    -> verified outcome 발생 시 online_learner.learn(...)
```

즉, GBM은 레지스트리 중심이고 SGD는 운영 중 GBM의 열 정의를 재사용한다.

## 5. SGD와 GBM을 분리해서 볼 때의 표

| 구분 | GBM | SGD |
|---|---|---|
| 기준 이름 목록 | `active_features` | `self.model.feature_names` |
| 기본 열 수 | 91 | 보통 91 |
| 열 순서 원천 | 레지스트리 | 대체로 GBM과 동일 |
| 입력 생성 시점 | 배치 재학습 / 실시간 추론 | 검증 후 온라인 학습 / 실시간 추론 |
| 스케일링 | 호라이즌별 `StandardScaler.fit` | 호라이즌별 `StandardScaler.partial_fit` |
| 예외 | 없음 | GBM 미학습 초기에는 런타임 키 정렬로 부트스트랩 가능 |

## 6. 현재 차이 나는 런타임 신형 피처

아래 피처들은 런타임 `FeatureBuilder` 에는 있으나 현재 GBM 레지스트리 91열에는 직접 반영되지 않는다.

`cvd_monotone_ratio`

`bear_exhaustion`, `bull_exhaustion`

`bear_exhaustion_signal`, `bull_exhaustion_signal`

`bull_reversal_signal`, `bear_reversal_signal`

반대로 레지스트리에는 아직 아래 구형 피처가 남아 있다.

`ofi_raw`

`ofi_reversal_signal`

이 때문에 "부트스트랩 초기 SGD" 와 "현재 GBM 학습 피처"를 엄밀히 나누면 입력 구성이 달라질 수 있다.

## 7. 실무 해석

- GBM 피처를 보고 싶다면 지금은 `active_features` 91개를 보면 된다.
- SGD 피처를 보고 싶다면 정상 운영 중에는 사실상 같은 91개를 보면 된다.
- 진짜로 분리해서 봐야 하는 부분은 "GBM 레지스트리" 대 "FeatureBuilder 런타임 신형 피처" 차이다.
- 즉, 현재 분리의 본질은 `SGD vs GBM` 자체보다 `레지스트리 기반 학습 피처 vs 런타임 진화 피처` 쪽에 더 가깝다.

## 8. 원하시면 다음 단계

다음 중 하나로 이어서 정리할 수 있다.

1. 문서에 `GBM 91개 목록`과 `초기 SGD 런타임 목록`을 표로 완전히 나눠 적기
2. `active_features` 를 신형 런타임 피처 기준으로 갱신해서 SGD/GBM 입력 차이를 줄이기
3. 아예 `docs/GBM_FEATURES.md` 와 `docs/SGD_FEATURES.md` 두 파일로 분리하기
