# 피처 절대값 → 상대값 정규화 구현 계획

> **진행 현황(정리 시점 확인)**: 묶음 1·2(Task 2-A~D, 3-A~B)는 2026-06-05~06-08 사이 완료 확인.
> **묶음 3 — Task 2-E(`quality_investor_age_sec`/`quality_macro_age_sec` 제거)는 아직 미착수** —
> 다음 세션에서 `dev_memory/NEXT_TODO.md`로 진행 여부 확인 후 처리 필요.

> 작성일: 2026-06-05  
> 배경: Extreme 피처 Top5 분석 → 91개 피처 전수 조사 결과  
> 문제: 절대가격/절대값 피처 16개가 상대값 변환 없이 StandardScaler에 직접 투입됨  
>       → 갭하락/갭상승 시 z-score 폭발 (max|z| 6~8), GBM conf 오염

---

## 현황 요약

| 분류 | 개수 | 상태 |
|---|---|---|
| 절대값 (변환 없음) | **14개** | 문제 |
| ofi_raw | 1개 | ✅ 이미 제거됨 (feature_builder.py:219) |
| log1p 변환 | 2개 | 정상 (`atr`, `avg_volume`) |
| clip 처리 | 8개 | 정상 |
| 상대값/정규화 | 59개 | 정상 |

### 절대값 피처 14개 목록

| 피처 | 단위 | 문제 |
|---|---|---|
| `microprice` | KOSPI200 포인트 (~1297) | 갭 시 z폭발, 파생 피처로 완전 대체 가능 |
| `vwap` | KOSPI200 포인트 (~1321) | 동일 |
| `cvd` | 체결량 누적 (-50000~+80000) | 시장 레짐·유동성 수준에 비례 |
| `cvd_slope` | 체결량 차분 (-5000~+8000) | 동일 |
| `queue_depletion_speed` | 잔량 단위 (0~500) | 유동성 수준에 따라 동일 압박도 값이 10배 차이 |
| `queue_refill_rate` | 잔량 단위 (0~500) | 동일 |
| `foreign_futures_net` | 계약수 | 미결제약정 대비 정규화 없음 |
| `foreign_call_net` | 계약수 | 동일 |
| `foreign_put_net` | 계약수 | 동일 |
| `retail_futures_net` | 계약수 | 동일 |
| `institution_futures_net` | 계약수 | 동일 |
| `program_arb_net` | 계약수 | 동일 |
| `program_non_arb_net` | 계약수 | 동일 |
| `foreign_retail_divergence` | 계약수 | 동일 |
| `program_foreign_net_krw` | 원화 (백만원) | 계약수 피처와 단위 불일치로 10배 스케일 차이 |
| `program_institution_net_krw` | 원화 | 동일 |
| `program_individual_net_krw` | 원화 | 동일 |
| `macro_vix_abs` | VIX 원본값 (10~50) | `macro_vix`(정규화)와 완전 중복 |
| `quality_investor_age_sec` | 초 (0~300+) | σ=11, 100초 도달 시 z>7 폭발 |
| `quality_macro_age_sec` | 초 (0~3600+) | σ 좁음, 장 초반 z폭발 |
| `feature_recoverable_errors` | 정수 (0~5) | σ≈0, 값 1만 돼도 z폭발, `feature_degraded`로 대체 가능 |

---

## 구현 계획

---

### Phase 1 — 즉시 clip 추가 (재훈련 없음, 당일 적용)

**목표:** z폭발을 수치적으로 cap. 근본 해결이 아니므로 Phase 2~3과 병행.

#### Task 1-1: SCALER_CLIP_FEATURES 확장

- **파일:** `config/settings.py`
- **위치:** `SCALER_CLIP_FEATURES` dict (line ~248)

```python
# 신규 추가
"microprice":               (1150.0, 1500.0),   # KOSPI200 선물 현실 범위
"vwap":                     (1150.0, 1500.0),   # 동일
"toxicity_cancel_stress":   (0.0, 0.5),         # [0,1] bounded이나 σ=0.002로 취약
"quality_investor_age_sec": (0.0, 180.0),       # is_stale threshold와 일치
"quality_macro_age_sec":    (0.0, 3600.0),      # 매크로 수집 주기 최대값
"macro_vix_abs":            (10.0, 60.0),       # VIX 현실 범위
"feature_recoverable_errors": (0.0, 3.0),       # 최대 3 이상은 동일 취급
# mlofi_slope 범위 강화
"mlofi_slope":              (-300.0, 300.0),    # 기존 ±500 → ±300 (σ=57 기준 3σ≈174)
```

- **검증:** 스케일러 모니터 extreme 발생 수 당일 비교

---

### Phase 2 — 중복/불필요 절대값 피처 제거 (재훈련 필요)

> 파생 피처가 이미 동일 정보를 상대값으로 담고 있는 경우. 정보 손실 없음.

#### Task 2-1: `microprice` 절대값 제거

- **파일:** `features/feature_builder.py` (line ~266), `docs/GBM_FEATURES.md`, `data/db/shap_feature_registry.json`
- **근거:** `microprice_bias`, `microprice_slope`, `microprice_depth_bias`가 완전 대체
- **작업:**
  - feature_builder.py: `features["microprice"]` 저장 라인 제거 또는 주석 처리
  - GBM_FEATURES.md A-2 섹션에서 `microprice` 제거
  - shap_feature_registry.json `active_features`에서 `microprice` 제거
  - GBM 재훈련

#### Task 2-2: `vwap` 절대값 제거

- **파일:** `features/feature_builder.py` (line ~203), `docs/GBM_FEATURES.md`, `data/db/shap_feature_registry.json`
- **근거:** `vwap_position` ([-2,2]), `above_vwap` (0/1)이 완전 대체
- **작업:**
  - feature_builder.py: `features["vwap"]` 저장 제거 (단, `self._vwap_history.append(_vwap_cur)` 등 내부 계산용 사용처는 유지)
  - GBM_FEATURES.md A-1 섹션에서 `vwap` 제거
  - shap_feature_registry.json `active_features`에서 `vwap` 제거
  - GBM 재훈련

#### Task 2-3: `macro_vix_abs` 제거

- **파일:** `features/macro/macro_feature_transformer.py` (line ~80), feature_builder.py, GBM_FEATURES.md
- **근거:** `macro_vix` (정규화 0~1)와 완전 중복. VIX 레짐 판단은 `macro_risk_on/off`로 이미 처리됨
- **작업:**
  - macro_feature_transformer.py: `"macro_vix_abs"` 반환값 제거
  - active_features에서 제거
  - GBM 재훈련

#### Task 2-4: `*_age_sec` 2개 제거 (clip 적용 후 단계적)

> Phase 1 clip 적용 → 최소 1주일 안정 확인 → 제거 진행

- **대상:** `quality_investor_age_sec`, `quality_macro_age_sec`
- **근거:** `quality_investor_stale` (0/1), `quality_macro_stale` (0/1) 플래그로 충분
- **작업:**
  - feature_builder.py: 해당 features[] 저장 라인 제거
  - active_features에서 제거
  - GBM 재훈련

#### Task 2-5: `feature_recoverable_errors` 제거

- **근거:** `feature_degraded` (0/1 플래그)로 충분. 오류 수 자체는 GBM 방향 예측에 의미 없음
- **작업:**
  - feature_builder.py line 395 제거
  - active_features에서 제거
  - GBM 재훈련

---

### Phase 3 — 상대화 변환 (설계 + 재훈련)

> 정보는 유지하되 스케일러 의존성을 제거하는 변환 적용.

#### Task 3-1: `cvd`, `cvd_slope` 일중 정규화

- **파일:** `features/technical/cvd.py`, `features/feature_builder.py`
- **현황:** `cvd` = 일중 누적 체결 델타 (장 시작 0에서 축적). 레벨이 "추세 강도"를 담음
- **변환안:**
  ```python
  # cvd.py flush_minute 추가
  cvd_daily_max = max(abs(x) for x in self._cvd_buf) or 1.0
  cvd_norm = cvd / cvd_daily_max        # [-1, +1] 일중 최대 대비 비율
  cvd_slope_norm = cvd_slope / (cvd_daily_max + 1e-9)
  ```
- **이득:** 거래량이 많은 날/적은 날 동일 시장 구조가 동일 값을 가짐
- **작업:** cvd.py flush_minute에 `cvd_norm`, `cvd_slope_norm` 추가 → active_features에서 `cvd` → `cvd_norm`으로 교체 → GBM 재훈련

#### Task 3-2: `queue_depletion_speed`, `queue_refill_rate` 비율화

- **파일:** `features/technical/queue_dynamics.py`
- **현황:** 거래량 단위 절대값. 장 초반(저유동성)과 점심(중유동성)에서 같은 압박도라도 값이 다름
- **변환안:**
  ```python
  total = depletion_speed + refill_rate + 1e-9
  depletion_ratio = depletion_speed / total   # [0, 1] 비율
  refill_ratio    = refill_rate    / total    # [0, 1] 비율
  ```
- **이득:** 유동성 레벨 독립, 분포 [0,1]로 안정
- **작업:** queue_dynamics.py flush_minute 수정 → active_features 교체 → GBM 재훈련

#### Task 3-3: B축 수급 11개 정규화 방식 검토

- **현황:** 계약수(외국인/기관/개인) + 원화(프로그램) 혼재. 시장 전체 미결제약정 규모 대비 정규화 없음
- **변환안 (2가지 검토):**

  **A안 — 20일 이동평균 대비 편차**
  ```python
  foreign_norm = (foreign_futures_net - rolling_mean) / (rolling_std + 1e-9)
  ```
  - 이득: 분포 안정, 최근 수급 흐름 대비 상대적 강도 표현
  - 단점: 과거 데이터 필요, 스케일러와 역할 중복 가능

  **B안 — 현행 유지 + OI(미결제약정) 도입 후 비율 추가 피처 병행**
  ```python
  foreign_oi_ratio = foreign_futures_net / (open_interest + 1)  # 신규 추가
  ```
  - 이득: 기존 계약수 피처 유지하면서 상대적 강도 정보 보완
  - 단점: OI 데이터 Cybos에서 별도 수집 필요

- **권장:** B안 우선 검토 (기존 피처 유지 + 보완 추가). OI는 Cybos FutureMst에서 이미 부분 수집 중 (`investor_data.py` line 126).

---

### Phase 4 — Gap Offset 구조적 방어 (Stage 2)

> Phase 2 피처 제거 완료 전까지 갭 방어의 중간 단계.

#### Task 4-1: 장 시작 Gap Offset 주입

- **파일:** `model/multi_horizon_model.py`, `model/multi_horizon_model.py:apply_robust_preprocess`
- **개념:** 장 시작 시 `today_open - scaler.mean_[microprice_idx]`를 오프셋으로 기록. 예측 시 절대가격 피처에서 차감 → 스케일러가 실질적으로 "당일 시가 대비 편차"를 z-score로 변환
- **적용 대상:** `microprice`, `vwap` (Phase 2 제거 전까지)
- **주입 시점:** `main.py` 09:00 장 시작 타이머에서 `model.set_daily_gap_offset(today_open)` 호출
- **제거 조건:** Task 2-1, 2-2 완료 후 자동 불필요

---

## 작업 우선순위 및 의존성

```
[즉시]
  Task 1-1 ── SCALER_CLIP_FEATURES 확장 ─→ 재훈련 없이 당일 배포

[단기, 재훈련 1회 묶음]
  Task 2-3 (macro_vix_abs 제거)
  Task 2-5 (feature_recoverable_errors 제거)
  Task 4-1 (Gap Offset) ← Task 2-1, 2-2 완료 전까지 병행

[중기, 재훈련 1회 묶음]
  Task 2-1 (microprice 절대값 제거)
  Task 2-2 (vwap 절대값 제거)
  Task 3-1 (cvd/cvd_slope 정규화)
  Task 3-2 (queue 비율화)

[장기, Phase 1 clip 안정화 확인 후]
  Task 2-4 (*_age_sec 제거)
  Task 3-3 (B축 수급 OI 비율화)
```

---

## 재훈련 체크리스트

각 재훈련 전 확인:
- [ ] `data/db/shap_feature_registry.json` active_features 업데이트
- [ ] `docs/GBM_FEATURES.md` 피처 목록 동기화
- [ ] `docs/SGD_FEATURE_VECTOR.md` SGD 피처 벡터 확인 (SGD는 별도 경로)
- [ ] `scripts/backfill_features.py` 새 피처 백필 실행
- [ ] 6개 호라이즌 모두 재학습 완료 확인
- [ ] 스케일러 모니터 extreme count 전일 대비 감소 확인

---

## 예상 효과

| 작업 | 예상 extreme 감소 |
|---|---|
| Task 1-1 (clip 추가) | microprice 156건 → ~0, vwap 6건 → ~0 (z cap) |
| Task 2-1~2 (가격 피처 제거) | 구조적 폭발 원천 제거 |
| Task 2-3~5 (중복 피처 제거) | macro_vix_abs, age_sec extreme 제거 |
| Task 3-1~2 (상대화 변환) | cvd, queue 피처 장 초반 extreme 감소 |
| Task 4-1 (Gap Offset) | 갭 당일 장 시작 초반 microprice/vwap z 안정화 |

---

## GBM 재훈련 방법

### 자동 재훈련 (평소 운용)

| 시점 | 트리거 | 비고 |
|---|---|---|
| 장 마감 후 15:40 | EOD 마감 루틴 자동 호출 | `weeks_back=8` |
| 매주 월요일 08:50~09:00 | `should_retrain_weekly()` 감지 | `force=True` |
| 매월 1일 07:00 | `should_retrain_monthly()` 감지 | `force=True` |
| 장 중 extreme 반복 | D_FORCE 트리거 | 스케일러만 refit, 모델 교체 없음 |

---

### 피처 변경 후 수동 재훈련 절차

#### Step 1 — 코드 수정

피처 제거: `features/feature_builder.py`에서 해당 `features["xxx"] = ...` 라인 제거  
피처 추가: 계산 코드 추가 후 `features["new_feat"] = value` 저장

#### Step 2 — `shap_feature_registry.json` 업데이트

**경로:** `data/db/shap_feature_registry.json`

GBM 학습 피처 목록은 코드가 아닌 이 파일의 `active_features`가 결정한다.  
제거할 피처는 목록에서 삭제, 추가할 피처는 목록에 append.

```json
{
  "active_features": [
    "cvd_divergence",
    "cvd_direction",
    ...
    // 제거 피처 삭제 / 신규 피처 추가
  ]
}
```

**편집 방법:**
- 텍스트 에디터 직접 편집
- 대시보드 → SHAP 피처 관리 패널 GUI

#### Step 3 — 수동 재훈련 실행

**방법 A: 대시보드 버튼 (미륵이 실행 중)**

대시보드 → "강제 재훈련" 버튼  
→ `retrain_now(force=True)` 백그라운드 스레드 실행  
→ 완료 시 새 pkl 자동 로드

**방법 B: 스크립트 직접 실행 (미륵이 종료 상태)**

```
conda activate py37_32
cd C:\Users\82108\PycharmProjects\futures
```

```python
from learning.batch_retrainer import BatchRetrainer

retrainer = BatchRetrainer()
result = retrainer.retrain_now(weeks_back=8, force=True)

print(f"완료: {result['ok']}")
print(f"소요: {result.get('elapsed_sec')}초")
print(f"데이터: {result.get('data_size')}봉")
for h, r in result.get('horizons', {}).items():
    print(f"  {h}: cv_acc={r.get('cv_acc'):.4f}  replaced={r.get('replaced')}")
```

#### Step 4 — 재훈련 성공 확인

pkl 수정 시간 갱신 확인:

```
model/horizons/gbm_1m.pkl   model/scaler/scaler_1m.pkl
model/horizons/gbm_3m.pkl   model/scaler/scaler_3m.pkl
model/horizons/gbm_5m.pkl   model/scaler/scaler_5m.pkl
model/horizons/gbm_10m.pkl  model/scaler/scaler_10m.pkl
model/horizons/gbm_15m.pkl  model/scaler/scaler_15m.pkl
model/horizons/gbm_30m.pkl  model/scaler/scaler_30m.pkl
```

로그 확인:
```
[Retrain] 1m 교체 (acc 0.4521→0.4589)
[Retrain] 완료 | 47.3초 | 성공=6/6 호라이즌
```

#### Step 5 — 재훈련 후 확인 사항

- [ ] 스케일러 extreme Top5 패널 — 발생수 감소 확인
- [ ] 호라이즌별 cv_acc — 이전 대비 크게 떨어지면 피처 제거 롤백 검토
- [ ] SGD 피처벡터 동기화 — 피처 제거 시 `docs/SGD_FEATURE_VECTOR.md` 확인 후 SGD 리셋 여부 결정

---

### 재훈련 묶음 전략

재훈련 비용을 줄이려면 여러 변경을 한 번에 묶어서 실행한다.

```
묶음 1 — 당일 15:40 EOD 자동 적용
  Task 2-A: macro_vix_abs 코드 제거
  Task 2-B: feature_recoverable_errors 코드 제거
  → active_features에서 두 피처 제거 후 저장

묶음 2 — 다음 월요일 주간 재훈련 자동 적용
  Task 2-C: microprice 절대값 제거
  Task 2-D: vwap 절대값 제거
  Task 3-A: cvd_norm / cvd_slope_norm 추가 (cvd / cvd_slope 교체)
  Task 3-B: queue 비율화 피처 교체
  → active_features 교체 후 저장

묶음 3 — Phase 1 clip 1주일 안정 확인 후
  Task 2-E: quality_investor_age_sec / quality_macro_age_sec 제거
```
