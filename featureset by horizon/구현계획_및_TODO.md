# 호라이즌별 최적 피처셋 구현 계획 및 TODO List
> 기획안 v1.0 기반 | 작성일: 2026-06-15

---

## 현황 진단 (코드 분석 결과)

### 핵심 문제 3가지

| # | 문제 | 위치 | 심각도 |
|---|---|---|---|
| P1 | **단일 feature_names.pkl** — 6개 호라이즌이 동일한 pkl 공유 | `batch_retrainer._save_feature_names()` L573 | 🔴 최고 |
| P2 | **macro yfinance 실패** — macro_sp500_chg 등 분산=0 | `collection/macro/macro_fetcher.py` L26 | 🔴 최고 |
| P3 | **feature_decay가 선택이 아닌 스케일링만** — 가중치를 곱할 뿐, 피처 열 자체를 제거하지 않음 | `features/feature_decay.py` L47 | 🟡 중간 |

### 현재 구조 정리

```
[현재]
build_for_horizon(bar, horizon_min)  →  get_horizon_features(feats, "Nm")
  └─ N분봉 bar 값 덮어쓰기 (O)             └─ 11개 피처 가중치 스케일링만 (X)

batch_retrainer.retrain()
  └─ 6개 호라이즌 모두 동일한 X (67피처) 로 GBM 학습
  └─ 공유 feature_names.pkl 1개 저장

[목표]
각 호라이즌별 독립 X (13~21개 피처) → 독립 feature_names_Nm.pkl
batch_retrainer → horizon별로 X 슬라이싱 후 학습
inference(main.py STEP5) → 호라이즌별 독립 피처벡터 구성
```

---

## 단계별 구현 계획

### PHASE A — 즉시 (1~2일): macro_fetcher 수집 복구

**목표**: vix_chg / sp500_chg / us10y_chg / krw_chg 실데이터 활성화

#### A-1. 장애 원인 확인
- `logs/` 최신 로그에서 `grep "Macro" | grep -E "fallback|cooldown|yfinance"` 실행
- `macro_quality_fallback_used` 컬럼 DB 확인 (1.0이면 수집 실패 중)

#### A-2. yfinance 대체 수집처 추가
- **VIX**: Cboe CDN `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`
- **S&P500**: Yahoo Finance API 직접 또는 `requests` + HTML 파싱 (yfinance 모듈 우회)
- **US10Y**: US Treasury XML `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml`
- **KRW**: 한국은행 Open API (ECOS) `https://ecos.bok.or.kr/api/` 또는 네이버금융 파싱

#### A-3. fallback 체계 개선
```python
# macro_fetcher.py 수집 우선순위
1순위: Cboe CDN (VIX) / Treasury XML (US10Y) / ECOS (KRW)
2순위: yfinance (현재)
3순위: 전날 성공값 캐시 (_last_good_vix 방식 확장)
4순위: 장기 평균 dummy fallback
```

#### A-4. macro_daily.csv 백필 적재
- 외부 수집한 일별 데이터를 `data/macro_daily.csv`에 저장
- `macro_fetcher.py`에 CSV 로드 fallback 경로 추가

---

### PHASE B — 1주: 호라이즌별 피처셋 명세 JSON 확정

**목표**: 기획안 3절의 피처셋을 코드에서 사용할 JSON으로 정의

#### B-1. `featureset by horizon/horizon_feature_sets.json` 생성
```json
{
  "1m": {
    "include": ["ofi_norm", "mlofi_slope", "queue_directional_depletion",
                "microprice_bias", "cvd_direction", "toxicity_score",
                "cancel_add_ratio", "spread_ticks", "micro_regime_code",
                "ret_1m", "vwap_position", "time_sin", "time_cos",
                "is_open_volatile"],
    "exclude": ["macro_vix", "macro_sp500_chg", "hurst",
                "opt_chain_pcr", "opt_gex_bn", "investor_net",
                "ret_15m", "bb_position", "ema_cross"]
  },
  "3m": { ... },
  ...
}
```

#### B-2. 현재 DB feature_names 조회로 실존 피처명 교차검증
```python
# _check_feat_keys.py 활용
SELECT DISTINCT feature_name FROM shap_tracker ...
```

#### B-3. SHAP vs 상관 불일치 피처 처리 결정
- SHAP↑/상관↓: `bb_position`, `ema_cross`, `ret_5m`, `vwap_momentum` → Walk-Forward 후 결정
- 상관↑/SHAP↓: `opt_chain_pcr`, `opt_gex_bn` → 피처 스케일/인코딩 점검 필요
- **보수적 처리**: 불확실 피처는 일단 포함, 다음 주기 갱신 시 제거

---

### PHASE C — 2~3주: 호라이즌별 독립 feature_names 구조 구현

**목표**: 가장 큰 구조 변경. 기존 단일 pkl → 6개 pkl 분리

#### C-1. `features/horizon_feature_registry.py` 신규 생성

```python
# horizon_feature_registry.py
import json, os

_JSON_PATH = os.path.join(os.path.dirname(__file__),
    "../featureset by horizon/horizon_feature_sets.json")

def get_feature_set(horizon: str) -> list:
    """horizon="1m" → 해당 호라이즌 include 피처 리스트 반환."""
    ...

def filter_for_horizon(X, all_feature_names, horizon):
    """X (N×F) 에서 horizon 전용 컬럼만 추출. 없는 피처는 0 패딩."""
    ...
```

#### C-2. `learning/batch_retrainer.py` 수정

변경 포인트:
- `_save_feature_names()` → `_save_feature_names(horizon_key, feature_names)` — 파일명 `feature_names_1m.pkl` 등
- `retrain()` 루프 내: 공통 X에서 호라이즌별 컬럼 슬라이싱 후 `_train_horizon()` 호출
- `_load_feature_names(horizon_key)` 추가 — 없으면 기존 공유 pkl로 fallback
- 기존 `feature_names.pkl` 호환 유지 (fallback)

```python
# 변경 전
self._save_feature_names(feature_names)  # 공유 pkl 1개

# 변경 후
for horizon_key in HORIZONS:
    h_feat_names = _filter_by_horizon(feature_names, horizon_key)
    X_h = _slice_columns(X, feature_names, h_feat_names)
    result = self._train_horizon(horizon_key, X_h, y_dict[horizon_key],
                                  feature_names=h_feat_names)
    self._save_feature_names(horizon_key, h_feat_names)
```

#### C-3. `model/multi_horizon_model.py` 수정

변경 포인트:
- `save()` / `load()`: `feature_names.pkl` → `feature_names_Nm.pkl` (호라이즌별)
- `predict_proba()` 경로: 호라이즌 key로 해당 feature_names 로드 후 컬럼 선택
- `_validate_feature_alignment()`: 호라이즌별 scaler 차원 검증
- 기존 단일 pkl 로드 fallback 유지 (이전 모델 호환)

#### C-4. `main.py` STEP 4~5 추론 경로 수정

```python
# STEP 4: build_for_horizon() 결과 전체 피처 dict 유지

# STEP 5: 각 호라이즌 예측 시 해당 피처셋만 추출
for horizon_key, h_min in [("1m", 1), ("3m", 3), ...]:
    h_feat_names = horizon_feature_registry.get_feature_set(horizon_key)
    h_vec = feature_builder.get_feature_vector_from_dict(feats, h_feat_names)
    prob = model.predict_proba(h_vec, horizon_key)
```

#### C-5. `features/feature_decay.py` 역할 재정의

현재: 11개 피처 가중치 곱셈 (스케일링)
변경: `get_horizon_features()` 는 `horizon_feature_registry` 호출로 대체
→ 기존 함수는 호환 레이어로 남기되 내부 로직은 hard selection으로 변경

---

### PHASE D — 3~4주: 호라이즌별 GBM 재학습 및 Walk-Forward 검증

**목표**: 새 피처셋으로 실제 성능 개선 확인

**⚠️ 2026-06-15 검증 결과 — 전략 수정**

검증 결과: `featureset by horizon/validation_results.md` 참조

| 전략 | 10m | 15m | 30m | 판정 |
|---|---|---|---|---|
| 공유 97개 (현재) | 0.4104 | 0.3957 | 0.3911 | 베이스라인 |
| Registry strict 선택 | 0.4073 (-0.003) | 0.3909 (-0.005) | **0.3538 (-0.037)** | **REGRESS** |
| Additive +신규 피처 | 0.4104 (0.000) | 0.3957 (0.000) | 0.3911 (0.000) | 변화없음 |

**REGRESS 원인**:
1. opt_gex_bn(ρ=0.290), opt_chain_pcr(ρ=0.245) 등 핵심 신호가 Cybos 수집 미안정으로 DB 미존재
2. registry 제거 목록(mlofi/microprice/ofi)이 현재 GBM에서 실제로 쓰는 정보를 담고 있음
3. 보상 신호(opt 시리즈) 없이 기존 신호를 제거하면 정보 손실

**수정된 전략**:
- **즉시**: 현재 97개 공유 피처셋 유지 (레그레션 방지)
- **단기**: opt_chain_snapshot 수집 상태 확인 + opt_gex_bn/chain_pcr/atm_* 수집 안정화
- **opt 4주 축적 후**: Phase D 재검증 (공유 97 vs 레지스트리 with opt 피처)

#### D-1. EOD 재학습 (`eod_retrain.py`) 수정
- `batch_retrainer.retrain()` 호출 시 `use_horizon_features=True` 기본값 전환
- 호라이즌별 `feature_names_Nm.pkl` 존재 여부 확인 후 분기
- **현재**: opt 피처 미수집 상태에서는 registry 미적용 (shared 97 유지)

#### D-2. Walk-Forward 검증 (opt 수집 안정화 후 재실행)
- 검증 순서: **10m → 15m → 30m** (기대 개선폭 큰 순서)
- 기준: 공유 베이스 대비 +2%p, Precision 개선, Recall 개선
- 재실행 조건: opt_gex_bn/chain_pcr/atm_* 4주 이상 DB 축적 확인

#### D-3. 결과 기록
- 검증 기록: `featureset by horizon/validation_results.md` (2026-06-15 완료)
- opt 수집 안정화 후 재실행 예정

---

### PHASE E — 4~6주: SHAP Tracker 6 호라이즌 확장

**목표**: 호라이즌별 독립 SHAP 추적으로 자동 피처 갱신 기반 마련

#### E-1. `learning/shap/shap_tracker.py` 수정
- `ShapTracker` 생성자에 `horizon: str` 파라미터 추가
- DB 저장 시 `horizon` 컬럼 포함 (기존 스키마 마이그레이션 필요)
- `get_top_features(horizon)` 메서드 추가
- `main.py`에서 호라이즌별 ShapTracker 인스턴스 6개 운용

#### E-2. 자동 피처셋 갱신 로직 설계
```python
# 주 1회 (EOD 재학습 시) 실행
for horizon in HORIZONS:
    shap_top = shap_tracker[horizon].get_top_features(n=30)
    corr_top = spearman_analyzer.get_significant_features(horizon, p_cutoff=0.05)
    new_set = intersect_and_validate(shap_top, corr_top, horizon)
    horizon_feature_registry.update(horizon, new_set)
```

---

### PHASE F — 지속: 레짐 조건부 피처셋 스위칭 (기발한 아이디어)

**목표**: micro_regime_code에 따라 1m 피처셋 동적 분기

#### F-1. `features/horizon_feature_registry.py` 확장
```python
REGIME_FEATURE_SETS = {
    "1m": {
        "trending": ["ofi_norm", "cvd_direction", "mlofi_slope", ...],   # 추세장
        "ranging":  ["ofi_norm", "microprice_bias", "ret_1m", ...],      # 횡보장
        "volatile": ["queue_directional_depletion", "toxicity_score", ...]  # 급변장
    }
}

def get_regime_feature_set(horizon, micro_regime_code):
    ...
```

#### F-2. main.py STEP 5 분기
```python
if horizon_key == "1m":
    regime = feats.get("micro_regime_code", 0)
    h_feat_names = registry.get_regime_feature_set("1m", regime)
```

---

## TODO List (우선순위 순)

### 🔴 즉시 (이번 주)

- [ ] **A-1** `logs/` 최신 로그에서 macro yfinance 실패 패턴 확인
- [ ] **A-2** `macro_fetcher.py`에 Cboe CDN VIX 수집 추가 (`_fetch_cboe_vix()`)
- [ ] **A-2** `macro_fetcher.py`에 US Treasury XML US10Y 수집 추가
- [ ] **A-3** `macro_fetcher.py` fallback 우선순위: Cboe/Treasury → yfinance → 캐시 → dummy
- [ ] **A-4** `data/macro_daily.csv` 백필 적재 (2026-05-11 이후 외부 수집 데이터)

### 🟠 1주 내

- [ ] **B-1** `featureset by horizon/horizon_feature_sets.json` 작성 (6개 호라이즌 × include/exclude)
- [ ] **B-2** 현재 DB에서 실존 피처명 목록 조회 → JSON과 교차검증
- [ ] **B-3** SHAP↑/상관↓ 피처 처리 방침 결정 (일단 포함 또는 별도 검증셋 분리)
- [ ] **B-4** `_analyze_corr.py` 또는 새 스크립트로 Spearman 상관 재확인 (최신 DB 기준)

### 🟡 2~3주 내

- [x] **C-1** `features/horizon_feature_registry.py` 신규 작성 ✅ 2026-06-15
  - `get_feature_set(horizon)` — JSON 로드
  - `get_available_feature_set(horizon, all_names)` — 컬럼 슬라이싱 + 미존재 피처 자동 제외
- [x] **C-2** `learning/batch_retrainer.py` 수정 ✅ 2026-06-15
  - `_save_feature_names(horizon_key, names)` — `feature_names_1m.pkl` 등
  - `_load_feature_names(horizon_key)` — fallback 포함
  - `retrain()` 루프: 호라이즌별 X 슬라이싱 후 학습
- [x] **C-3** `model/multi_horizon_model.py` 수정 ✅ 2026-06-15
  - `horizon_feature_names` dict + `_hz_feat_indices` 사전계산 추가
  - `predict_proba()`: 호라이즌별 numpy 슬라이싱 (O(1) 접근)
  - `validate_and_resync()`: 호라이즌별 scaler 차원 검증
- [x] **C-4** `main.py` STEP 5 주석 추가 ✅ 2026-06-15 (실질 변경 없음 — 모델 내부 슬라이싱)
- [ ] **C-5** `features/feature_decay.py` → `horizon_feature_registry` 위임 (opt 수집 후 진행)
- [x] **C-6** 단위 테스트: backward compat predict_proba OK ✅ 2026-06-15

### 🟢 3~4주 내

- [ ] **D-0** ⚠️ opt_chain_snapshot 수집 상태 확인 — opt_gex_bn/chain_pcr/atm_* DB 수집 여부
- [x] **D-2** Walk-Forward 검증 실행: 10m → 15m → 30m ✅ 2026-06-15 (결과: REGRESS)
- [x] **D-3** Before/After 정확도 기록 → `featureset by horizon/validation_results.md` ✅ 2026-06-15
- [x] **D-4** 판정: opt 미수집으로 registry strict 선택 보류 → 현재 97개 공유셋 유지 ✅
- [ ] **D-5** opt 4주 수집 후 Phase D 재검증 (재검증 조건 달성 시 실행)
- [ ] **D-1** `eod_retrain.py` 수정: `use_horizon_features=True` 기본값 전환 (D-5 후 진행)

### 🔵 4~6주 내

- [ ] **E-1** `shap_tracker.py` 수정: `horizon` 파라미터 + DB 컬럼 추가
- [ ] **E-2** `shap_tracker.db` 스키마 마이그레이션 (ALTER TABLE horizon TEXT)
- [ ] **E-3** `main.py` 호라이즌별 ShapTracker 인스턴스 6개 운용
- [ ] **E-4** 자동 피처셋 갱신 로직 설계 및 스케줄 등록

### ⚪ 지속 (Phase F)

- [ ] **F-1** `horizon_feature_registry.py` 레짐별 피처셋 분기 구조 추가
- [ ] **F-2** `main.py` STEP 5 → 1m 호라이즌 레짐 조건부 피처셋 스위칭
- [ ] **F-3** 횡보/추세/급변 레짐별 성능 A/B 비교

---

## 구현 시 주의사항

### 1. 하위 호환성 필수 유지
- 기존 `feature_names.pkl` (공유) → 신규 `feature_names_1m.pkl` 등 공존 기간 운영
- 신규 pkl 없으면 구 pkl fallback (Phase C 완료 전 장 운영 중단 없이 전환 가능)

### 2. CORE 피처 3개 절대 제거 불가
- `cvd_direction` / `vwap_position` / `ofi_norm` — 어느 호라이즌에도 include 유지
- 단, 30m에서 `ofi_norm` 제거는 기획안에 명시되어 있으므로 **예외 허용** (CORE.md와 기획안 충돌 → 30m 한정 제거 결정 필요)

### 3. 매크로 피처는 수집 복구 후 추가
- Phase A 완료 전까지 `macro_*` 피처는 include 목록에 있어도 GBM은 0 입력 수신
- 복구 후 재학습 없이는 모델이 0값을 정상값으로 학습했을 수 있음 → **복구 후 반드시 재학습**

### 4. COM 콜백 규칙 변경 없음
- 추론 경로가 바뀌어도 콜백 내 dynamicCall/emit 금지 규칙은 유지

### 5. 검증 순서 준수
- 10m → 15m → 30m 순 검증 후 1m → 3m → 5m 검증
- 전 호라이즌 동시 변경 금지 (롤백 시 혼란)

---

## 기대 성능 목표

| 호라이즌 | 현재 acc | 목표 acc | 주요 변화 |
|---|---|---|---|
| 1m | 38.5% | 40~42% | LOB 노이즈 피처 제거 → 과적합 감소 |
| 3m | 35.2% | 37~39% | bear_reversal 강화 + VIX/US10Y 추가 |
| 5m | 35.9% | 38~40% | opt_chain_pcr 활성화 |
| 10m | 34.3% | **38~41%** | OFI 잡음 제거 + ATM OI 풀 활성 (최대 개선 기대) |
| 15m | 33.1% | 36~39% | FLAT 편향 완화 + 매크로 복구 |
| 30m | 35.4% | 38~41% | 틱 노이즈 제거 + vix_chg 최강 신호 |

> Walk-Forward 20거래일 기준 +2%p 이상 확인 후 배포
