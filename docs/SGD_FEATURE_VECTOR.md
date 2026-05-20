# SGD 피처 벡터 구성

> 조사일: 2026-05-20  
> 대상: `learning/online_learner.py` + `features/feature_builder.py`

---

## 1. 개요

| 항목 | 내용 |
|---|---|
| 총 피처 수 | **93개** |
| 피처 정의 파일 | `data/db/shap_feature_registry.json` → `active_features` 배열 |
| 벡터 조립 함수 | `features/feature_builder.py` → `FeatureBuilder.get_feature_vector()` |
| 호라이즌 | 1 · 3 · 5 · 10 · 15 · 30분 (6개, 공통 피처 벡터 사용) |

---

## 2. 카테고리별 피처 목록

### 2-1. 기술적 피처 (Technical) — 약 35개

| 그룹 | 피처명 |
|---|---|
| CVD | cvd_divergence, cvd_direction, cvd, cvd_slope, cvd_exhaustion, cvd_exhaustion_signal |
| VWAP | vwap_position, vwap, above_vwap |
| OFI | ofi_norm, ofi_pressure, ofi_imbalance, ofi_raw, ofi_reversal_speed, ofi_reversal_signal |
| Microprice | microprice, microprice_bias, microprice_slope, microprice_depth_bias |
| MLOFI | mlofi_norm, mlofi_pressure, mlofi_slope |
| Queue Dynamics | queue_signal, queue_signal_ma, queue_momentum, queue_depletion_speed, queue_refill_rate, imbalance_slope, cancel_add_ratio |
| 기타 | avg_volume, atr, atr_ratio, hurst, spread_ticks |

### 2-2. Toxicity (독성) — 8개

| 피처명 |
|---|
| toxicity_score, toxicity_score_ma, toxicity_atr_stress, toxicity_spread_stress |
| toxicity_flow_stress, toxicity_queue_stress, toxicity_cancel_stress, toxicity_regime_code |

### 2-3. 수급 (Supply/Demand) — 13개

| 피처명 |
|---|
| foreign_futures_net, foreign_call_net, foreign_put_net |
| retail_futures_net, institution_futures_net |
| program_arb_net, program_non_arb_net |
| foreign_retail_divergence |
| program_foreign_net_krw, program_institution_net_krw, program_individual_net_krw |
| quality_investor_supported (+ 관련 quality 메타) |

### 2-4. 옵션 (Options) — 6개

| 피처명 |
|---|
| opt_pcr_norm, opt_pcr_bearish, opt_pcr_bullish, opt_pcr_extreme, opt_pcr_slope_norm, opt_available |

### 2-5. 매크로 (Macro) — 9개

| 피처명 |
|---|
| macro_vix, macro_vix_abs, macro_sp500_chg, macro_nasdaq_chg |
| macro_krw_chg, macro_us10y_chg |
| macro_risk_on, macro_risk_off, macro_event_flag |

### 2-6. 품질/메타데이터 (Quality) — 나머지

| 피처명 |
|---|
| feature_recoverable_errors, feature_degraded, feature_quality_score |
| quality_option_available, quality_macro_available, quality_supply_available |
| quality_macro_stale, quality_macro_age_sec, quality_macro_fallback_used |
| macro_quality_available, macro_quality_stale, macro_quality_age_sec, macro_quality_fallback_used |

---

## 3. 벡터 조립 흐름

```
FeatureBuilder.build(bar, supply_demand, option_data, macro_data)
  ├─ 기술 지표 계산 (CVD, VWAP, OFI, Microprice, MLOFI, Queue, ATR, Hurst, Toxicity)
  ├─ 수급 피처 주입:  for k, v in supply_demand.items()
  ├─ 옵션 피처 주입:  for k, v in option_data.items()
  ├─ 매크로 피처 주입: for k, v in macro_data.items()
  └─ 품질 메타 계산
        ↓
  self._last_features (dict)  ← 모든 피처를 키-값으로 보관
        ↓
  get_feature_vector(feature_names: list) → np.ndarray(93,)
    [self._last_features.get(name, 0.0) for name in feature_names]
```

- `feature_names` 순서는 `shap_feature_registry.json`의 `active_features` 배열 순서
- 누락 피처는 `0.0` 으로 대체 (결측 안전 처리)
- 최종 dtype: `float64`

---

## 4. 스케일링

| 항목 | 내용 |
|---|---|
| 방식 | `StandardScaler` (평균 0, 표준편차 1) |
| 스케일러 수 | **6개** — 호라이즌별 독립 (1·3·5·10·15·30분) |
| 초기화 | 첫 샘플에서 `partial_fit()` 으로 초기 통계 추정 |
| 적용 | `learn()` 및 `predict()` 모두 동일 scaler로 `transform()` |

---

## 5. SGD 모델 설정

```python
# learning/online_learner.py
SGDClassifier(
    loss="log",           # 로지스틱 → 확률 출력
    learning_rate="optimal",  # 적응형: 1 / (alpha * t)
    alpha=0.001,          # L2 정규화
    max_iter=1,           # 온라인: 샘플 1개씩 학습
    warm_start=True,      # 가중치 누적 보존
    random_state=42,
    n_jobs=1,
)
```

**클래스:** 3개 — `DOWN(-1)`, `FLAT(0)`, `UP(+1)`

---

## 6. 피처 선택 규칙

### CORE 피처 (절대 교체 불가)

`config/constants.py` → `CORE_FEATURES`

| 피처 | 역할 |
|---|---|
| `cvd_divergence` | 단기 최강 방향 신호 |
| `vwap_position` | 기관 알고리즘 기준선 |
| `ofi_norm` | 1~3분 방향 선행 |

### 동적 피처 교체

| 항목 | 내용 |
|---|---|
| 분석 주기 | 매주 (SHAP TreeExplainer) |
| 분석 파일 | `learning/shap/shap_tracker.py` |
| 교체 후보 | SHAP 순위 하위 5개 중 4주 연속 하락 피처 |
| 후보 풀 | `config/constants.py` → `DYNAMIC_FEATURES_POOL` (31개) |
| 쿨다운 | 교체 후 3일 |
| 일일 한도 | 최대 1개 |
| **자동화 여부** | **수동 승인 필수 — 자동 통합 절대 금지** |

---

## 7. 관련 파일 요약

| 파일 | 역할 |
|---|---|
| `features/feature_builder.py` | 피처 계산 및 벡터 조립 |
| `learning/online_learner.py` | SGD 모델 + 스케일러 관리 |
| `learning/batch_retrainer.py` | feature_names 로드 및 DB 연동 |
| `data/db/shap_feature_registry.json` | active_features 순서 정의 |
| `config/constants.py` | CORE_FEATURES, DYNAMIC_FEATURES_POOL |
| `learning/shap/shap_tracker.py` | 주간 SHAP 분석 + 교체 후보 선정 |
