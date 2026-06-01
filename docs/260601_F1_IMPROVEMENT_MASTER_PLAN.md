# 호라이즌별 Precision / Recall / F1 고도화 마스터 플랜

> **최초 작성**: 2026-06-01  
> **최종 업데이트**: 2026-06-01 (P1~P6c, 개선 1~7 전체 반영)  
> **목표**: 호라이즌별 평균 F1 0.30~0.35 → **0.55 이상**  
> **전략**: 구조적 원인 우선 제거 → 피처 고도화 → 모델 아키텍처 개선

---

## 0. 현황 스냅샷 (기준: 2026-06-01 이전 14거래일)

### 0-1. 시간대 × 호라이즌 F1 실측값 (개선 전)

| 호라이즌 | OPEN_VOLATILE (09:00~09:30) | STABLE_TREND | LUNCH_RECOVERY | CLOSE_VOLATILE |
|---|---|---|---|---|
| 1m | ~0.35 | ~0.40 | ~0.42 | ~0.44 |
| 3m | **0.3079** | ~0.38 | ~0.40 | **0.4143** |
| 5m | ~0.32 | ~0.39 | ~0.38 | ~0.41 |
| 10m | ~0.34 | ~0.37 | ~0.36 | ~0.39 |
| 15m | **0.2476** | ~0.33 | ~0.36 | ~0.37 |
| 30m | **0.2316** | ~0.35 | **0.3874** | **0.4084** |

**핵심 관찰**:
- 개장 구간 F1이 전 구간 대비 평균 **0.10~0.15 낮음**
- 30m·15m는 전 시간대 평균 F1이 가장 낮음 (장기 예측의 구조적 한계)
- 마감 구간에서 상대적으로 높음 — 추세 지속성 효과

### 0-2. 근본 원인 5가지 진단

```
근본 원인                        진단                              현재 상태
────────────────────────────────────────────────────────────────────────────
① 학습 데이터 절대 부족    22거래일(7,286봉) → 오버피팅          [DONE] 190일(71,144봉)
② 방향성 피처 빈약         ATR이 SHAP 1위(0.1476), 방향 신호 없음 [DONE] 피처 17개 추가
③ 레이블 드리프트          학습 σ × 실전 σ 불일치               [DONE] 고정 임계값 분리
④ 캘리브레이션 미스        conf 0.69 선언 → 실 정확도 37~42%     [DONE] Platt Scaling
⑤ 3클래스 동시 예측 한계   UP/DN 경계 모호, 반대 예측 39~41%     [진행중] P8 장기 과제
```

---

## 1. 완료된 개선 (2026-06-01 기준)

### ✅ 1-1. 학습 데이터 22일 → 190일 소급 생성 + MIN_TRAIN_BARS 상향

**문제**: raw_features가 미륵이 최초 기동일(2026-04-28)부터만 존재.  
GBM이 실질적으로 22거래일(7,286봉)로 학습되었고, `MIN_TRAIN_BARS=5000`(13거래일)도 너무 낮았음.

**해결**:

| 항목 | 이전 | 이후 |
|---|---|---|
| raw_features 행 수 | 7,286 | **71,144** |
| 학습 가능 거래일 | 22일 | **190일 (2025-08-19~)** |
| MIN_TRAIN_BARS | 5,000 (13거래일) | **15,000 (40거래일)** |

**소급 데이터 특성** (`feature_quality_score=0.3` 마커):
- 정확 계산: `atr`, `atr_ratio`, `vwap`, `vwap_position`, `above_vwap`
- OHLCV 근사: `cvd_direction`, `cvd_slope`, `avg_volume`, `hurst`
- 0.0 채움: `ofi_*`, `microprice_*`, `mlofi_*`, 수급·매크로·옵션

**관련 파일**: `scripts/backfill_features.py`, `learning/batch_retrainer.py`

---

### ✅ 1-2. 방향성 피처 17개 추가 (P2 + 개선 3)

**문제**: ATR이 SHAP 1위(0.1476) — 변동성 지표가 방향 판단을 지배.

**1차 추가 (P2, 14개 피처)**:

| 피처 | 계산 기반 | 내용 |
|---|---|---|
| `time_sin`, `time_cos` | ts | 시장 내 분 위치 사인/코사인 |
| `is_open_volatile` | ts | 09:05~09:30 여부 |
| `is_close_volatile` | ts | 14:30 이후 여부 |
| `ret_1m`, `ret_5m`, `ret_15m` | close | 가격 모멘텀 |
| `ema_cross` | close | EMA5 > EMA20 여부 (+1/-1) |
| `bb_position` | close | 볼린저 밴드 내 위치 (0~1) |
| `cvd_delta_norm` | OHLCV | Bull/Bear Volume 분해 CVD |
| `poc_distance` | OHLCV | 현재가 대비 POC 거리 |
| `in_value_area` | OHLCV | Value Area 내부 여부 |
| `va_bandwidth` | OHLCV | Value Area 폭 (집중도) |
| `poc_above` | OHLCV | 현재가 > POC 여부 |

**2차 추가 (개선 3, 3개 피처)**:

| 피처 | 내용 |
|---|---|
| `volume_acceleration` | 직전 3봉 거래량 대비 현재 3봉 거래량 변화율 |
| `vwap_momentum` | 최근 5봉 동안 현재가가 VWAP 기준으로 이동한 속도 |
| `prev_day_same_hour_ret` | 전일 동시간대 1분 수익률 (시간대 패턴) |

**신규 파일**: `features/technical/volume_profile.py` (POC/VA 계산기)  
**소급 반영**: `--update-features` 190일 전체 2회 갱신 완료

---

### ✅ 1-3. Rolling σ 레이블 안정화 (91/92차)

**문제**: 정적 임계값으로 FLAT 비율이 날별 14%p 흔들림 → 진입 0일 발생.

**해결**: `SIGMA_K=0.41`, `SIGMA_W=20` rolling σ×k 임계값 도입

| 방법 | FLAT 평균 | FLAT std | 진입 0 재발 |
|---|---|---|---|
| 정적 임계값 | 37.3% | 14.4%p | 높음 |
| **Rolling σ×k** | **32.5%** | **3.2%p** | **낮음** |

---

### ✅ 1-4. 학습 레이블 고정화 (개선 4 — USE_FIXED_LABEL_THRESHOLD)

**문제**: 배치 재학습 시 rolling sigma 레이블 vs. 실전 rolling sigma 레이블의 sigma_buf가 달라 레이블 드리프트 재발 가능.

**해결**: `config/settings.py`에 `USE_FIXED_LABEL_THRESHOLD=True` 추가

```
학습:  HORIZON_THRESHOLDS 고정값으로 레이블 생성 → 분포 일관성 보장
실전:  rolling sigma × k로 실시간 임계값 계산 → 유지
검증:  sigma_at_t(예측 당시 sigma) 저장값으로 재현 → 일관성 보장
```

**관련 파일**: `config/settings.py`, `learning/batch_retrainer.py`, `learning/prediction_buffer.py`

---

### ✅ 1-5. 호라이즌별 최적 σ_k 탐색 및 적용 (P5)

**문제**: k=0.41 전 호라이즌 공통 적용 → 장기 호라이즌 UP/DOWN 불균형.

**해결**: `scripts/optimize_sigma_k.py` 실행 (71,144봉 기준)

| 호라이즌 | 최적 k | 최적 시 FLAT | UP/DN 불균형 |
|---|---|---|---|
| 1m | **0.41** | 33.1% | 0.5%p |
| 3m | **0.41** | 33.4% | 1.5%p |
| 5m | **0.41** | 33.6% | 1.8%p |
| 10m | **0.38** | 32.4% | 3.2%p |
| 15m | **0.38** | 33.8% | 4.2%p |
| 30m | **0.33** | 33.3% | 5.7%p |

**적용**: `SIGMA_K_PER_HORIZON` 딕셔너리 추가, `batch_retrainer`에서 호라이즌별 k 사용

---

### ✅ 1-6. 시간대 × 호라이즌 min_conf 2D 표 적용 (P4)

**문제**: 단일 시간대별 min_conf → F1이 낮은 호라이즌(특히 OPEN_VOLATILE의 15m/30m)도 동일 기준 적용.

**해결**: `MIN_CONF_TABLE` 2D 딕셔너리 추가, STEP 6 앙상블 직전에 conf 미달 호라이즌 제외

```python
# config/settings.py
MIN_CONF_TABLE = {
    "OPEN_VOLATILE":  {"1m": 0.62, "3m": 0.65, "5m": 0.63, "10m": 0.63, "15m": 0.68, "30m": 0.70},
    "STABLE_TREND":   {"1m": 0.57, "3m": 0.58, "5m": 0.57, "10m": 0.57, "15m": 0.60, "30m": 0.62},
    "LUNCH_RECOVERY": {"1m": 0.57, "3m": 0.57, "5m": 0.57, "10m": 0.57, "15m": 0.58, "30m": 0.58},
    "CLOSE_VOLATILE": {"1m": 0.55, "3m": 0.55, "5m": 0.56, "10m": 0.57, "15m": 0.58, "30m": 0.58},
}
```

**관련 파일**: `config/settings.py`, `strategy/entry/time_strategy_router.py`, `main.py`

---

### ✅ 1-7. 호라이즌 방향 코히어런스 게이트 (P3b)

**문제**: 1m UP + 30m DOWN 같은 모순 신호가 앙상블에 그대로 입력 → 노이즈 진입의 주원인.

**해결**: `COHERENCE_GATE_MIN=0.67` — active_horizons 중 4개 이상 동방향 미달 시 grade=X

```python
# model/ensemble_decision.py
if _coherence_score < COHERENCE_GATE_MIN:
    grade = "X"   # 최우선 차단
```

**기대 효과**: OPEN_VOLATILE 진입 -30~40%, Precision +0.06~0.10

---

### ✅ 1-8. 호라이즌 F1 적응형 가중치 (P3)

**문제**: 앙상블 가중치가 상관계수 역수로만 고정 — F1 낮은 호라이즌도 동등 취급.

**해결**: `HorizonF1AdaptiveWeight` 클래스 구현 (EMA decay=0.95, f1_floor=0.30)

```
F1이 낮은 호라이즌 → f1² 비례로 가중치 급감
STEP 1 검증 결과 전 호라이즌 자동 누적 → main.py에서 매분 업데이트
```

**관련 파일**: `model/ensemble_decision.py`, `main.py`

---

### ✅ 1-9. 경로 조건부 레이블 (P6b)

**문제**: T분 후 UP이지만 중간에 역행 발생 → stop-loss 후 손절 케이스가 UP 레이블로 학습됨. 레이블 오염 15~25%.

**해결**: `_path_conditioned_label()` 함수 — 중간 경로 역행폭 > threshold×0.45이면 FLAT 처리

```python
# 예시: 30m UP 후보, 중간에 -0.3% 역행 발생
# threshold=0.0196%, path_ratio=0.45 → 0.0196×0.45=0.0088%
# abs(max_dd)=0.3% >> 0.0088% → FLAT 처리 (레이블 정정)
```

**관련 파일**: `learning/batch_retrainer.py`

---

### ✅ 1-10. RF 이종 앙상블 (P6c)

**문제**: GBM+SGD는 동일 피처 공간 — 동일 노이즈에 동시 실패 가능.

**해결**: `model/rf_horizon_model.py` 신규 생성

```
RandomForest(n_estimators=150, max_depth=10, balanced, n_jobs=1, oob_score=True)
GBM 재학습 완료 시 RF도 자동 학습·저장
앙상블: GBM+SGD 0.70 × RF 0.30
```

**특성**:
- 소급 데이터(OFI=0) 자동 희석 — 개별 트리가 일부 피처 무시
- Python 3.7 32-bit 완전 호환 (scikit-learn 기존 의존)
- OOB score로 재학습 없이 정확도 모니터링

---

### ✅ 1-11. GBM 파라미터 재조정 (개선 6)

**이전**: 데이터 22일 기준 n_estimators=200, learning_rate=0.05  
**이후**: 190일(71,144봉) 기반 강화

```python
GBM_PARAMS = {
    "n_estimators":     300,   # 200 → 300
    "learning_rate":    0.04,  # 0.05 → 0.04 (estimators 증가 보상)
    "max_depth":        5,
    "subsample":        0.8,
    "min_samples_leaf": 10,
}
```

---

### ✅ 1-12. 호라이즌별 Platt Scaling Calibrator (개선 5 / P6)

**이미 구현되어 있음 (81차)**:
- `MultiHorizonCalibrator` — 6개 호라이즌 독립 Platt Scaling
- `_preload_horizon_calibration()` — 기동 시 DB 18,000건 사전 fit
- `_apply_horizon_calibration()` — STEP 5 이후 매분 보정 적용
- STEP 1 검증 시 실시간 누적 + 20건 주기 재fit

---

### ✅ 1-13. 스케일러 강건화 (94/95차)

| 트리거 | 방식 | 시점 |
|---|---|---|
| A: 워밍업 | 500봉 refit | 08:55 고정 |
| B: 장초 단축 | 15분마다 | 09:00~09:30 |
| C: 정기 | 60분마다 | 장중 |
| D: 강제 | 극단 z 3분 연속 | 즉시 |

Robust 전처리: `atr`/`avg_volume` log1p, `spread_ticks` clip(0,20), `mlofi_slope` clip(±500)

---

### ✅ 1-14. 임계값 재보정 + class_weight 재조정 (90차)

| 호라이즌 | 재보정 후 임계값 |
|---|---|
| 1m | 0.0041% |
| 5m | 0.0092% |
| 15m | 0.0155% |
| 30m | 0.0196% |

```python
_CW_1M  = {FLAT: 0.85, UP: 1.08, DOWN: 1.08}
_CW_3M  = {FLAT: 0.75, UP: 1.12, DOWN: 1.12}
_CW_5M  = {FLAT: 0.85, UP: 1.08, DOWN: 1.08}
_CW_30M = {FLAT: 1.00, UP: 1.00, DOWN: 1.00}
```

---

## 2. 미구현 — 장기 과제

### 🔴 [P8] 2단계 예측 구조 (Stage1/2) — 실시간 90일 이상 후

**이유**: Stage 2(UP vs DN) 전용 학습 데이터가 별도로 필요하고, 현재 실시간 데이터가 충분하지 않아 A/B 테스트 불가.

```
Stage 1: Binary (DIRECTIONAL vs FLAT)
  → Precision 중심: 방향성 없는데 신호 내면 손실
  → F1 기준: 기대 +15~20%

Stage 2: Binary (UP vs DOWN) [Stage 1 = DIRECTIONAL만]
  → Recall 중심: 방향 맞추면 수익
  → UP/DN 반대 예측 39~41% 구조적 해결

최종 confidence = P(DIRECTIONAL) × P(UP|DIRECTIONAL)
```

**구현 복잡도**: 높음 (모델 2개 × 6호라이즌 = 12모델)

---

### 🟡 [P7] 소급/실시간 분리 앙상블 — 실시간 90일 이상 후

```
GBM_OHLCV  — atr/vwap/cvd 피처만 사용 (190일 전 구간)
GBM_FULL   — 전체 피처 사용 (실시간 구간)
alpha = max(0, 1 - live_days / 90)  # 실시간 축적 시 GBM_FULL 비중 증가
```

---

### 🟢 [P10] 레짐 조건부 GBM 분기 — 실시간 90일 이상 후

```python
# model/regime_split_model.py (미구현)
# TREND (Hurst>0.55) / MEAN_REV (Hurst<0.45) / VOLATILE (ATR_ratio≥1.8)
# 레짐별 전문화 GBM → 레짐별 F1 +0.05~0.10 기대
```

레짐별 학습 데이터 (190일 기준): TREND ~35,000봉, MEAN_REV ~21,000봉, VOLATILE ~14,000봉 — 이미 충분.  
**미구현 이유**: 실시간 데이터와의 검증이 먼저 필요.

---

## 3. 고도화 방안 설계 (참조)

### 3-1 ~ 3-5 (구현 완료)

| 방안 | 구현 상태 | 관련 섹션 |
|---|---|---|
| 3-1. 소급 CVD 고도화 + 방향 피처 | ✅ 완료 | 1-2 |
| 3-2. 호라이즌 특화 피처 가중치 | ✅ 완료 (HorizonF1AdaptiveWeight로 자동화) | 1-8 |
| 3-3. WFA 기반 σ_k 최적화 | ✅ 완료 | 1-5 |
| 3-4. 앙상블 F1 피드백 루프 | ✅ 완료 | 1-8 |
| 3-5. 시간대 × 호라이즌 min_conf 표 | ✅ 완료 | 1-6 |

### 3-6 ~ 3-10 (일부 완료)

| 방안 | 구현 상태 |
|---|---|
| 3-6. 코히어런스 게이트 | ✅ 완료 (1-7) |
| 3-7. 경로 조건부 레이블링 | ✅ 완료 (1-9) |
| 3-8. 거래량 프로파일 (POC/VA) | ✅ 완료 (1-2 poc_distance 등 4개) |
| 3-9. 레짐 조건부 GBM 분기 | ❌ 미구현 (P10) |
| 3-10. RF 이종 앙상블 | ✅ 완료 (1-10) |

---

## 4. 로드맵 — 구현 순서

```
완료 ──────────────────────────────────────────────────────────
[2026-06-01] ✅ 소급 데이터 190일(71,144봉) 생성
[2026-06-01] ✅ P1  sigma_at_t 저장 (96차)
[2026-06-01] ✅ P2  피처 14개 확장 (volume_profile.py 신규)
[2026-06-01] ✅ P3  HorizonF1AdaptiveWeight
[2026-06-01] ✅ P3b 코히어런스 게이트 (COHERENCE_GATE_MIN=0.67)
[2026-06-01] ✅ P3c 소급 190일 피처 갱신 완료 (71,155봉 UPDATE)
[2026-06-01] ✅ P4  시간대 × 호라이즌 min_conf 2D 표
[2026-06-01] ✅ P5  호라이즌별 최적 σ_k (10m/15m=0.38, 30m=0.33)
[2026-06-01] ✅ P6  Platt Scaling 호라이즌별 calibrator (이미 구현됨 확인)
[2026-06-01] ✅ P6b 경로 조건부 레이블 (path_ratio=0.45)
[2026-06-01] ✅ P6c RF 이종 앙상블 (n=150, balanced, OOB)
[2026-06-01] ✅ 개선1 MIN_TRAIN_BARS 5000→15000
[2026-06-01] ✅ 개선3 volume_acceleration, vwap_momentum, prev_day_same_hour_ret
[2026-06-01] ✅ 개선4 USE_FIXED_LABEL_THRESHOLD=True
[2026-06-01] ✅ 개선6 n_estimators=300, learning_rate=0.04

장기 (실시간 데이터 90일 이상 확보 후)
──────────────────────────────────────────────────────────────
[P7]  소급/실시간 분리 앙상블 (GBM_OHLCV + GBM_FULL)
[P8]  2단계 분류 구조 (DIRECTIONAL/FLAT → UP/DOWN) A/B 테스트  ← 미구현 유일한 핵심
[P10] 레짐 조건부 GBM 분기 (TREND/MEAN_REV/VOLATILE 전문화)
```

---

## 5. 목표 F1 달성 시나리오

```
개선 전 상태:  평균 F1 ≈ 0.32  (시간대별 0.23~0.41 분포)
                                          ↓
[2026-06-01] 구현 완료 효과:
  소급 190일 + MIN_TRAIN_BARS×3    +0.05~0.08  (과적합 → 일반화)
  레이블 고정화 + σ_k 최적화       +0.02~0.04  (레이블 드리프트 제거)
  피처 17개 추가 (방향성 신호)     +0.04~0.07  (ATR 지배 구조 해소)
  코히어런스 게이트                +0.04~0.07  (모순 신호 차단)
  경로 조건부 레이블               +0.03~0.05  (레이블 순도 향상)
  RF 이종 앙상블                   +0.02~0.04  (앙상블 다양성)
  F1 적응형 가중치                 +0.02~0.03  (나쁜 호라이즌 자동 억제)
  min_conf 2D 표 + GBM 파라미터    +0.02~0.04  (품질 진입 + 모델 강화)
                                          ↓
단기 목표 (다음 GBM 재학습 후):  평균 F1 ≈ 0.46~0.55

장기 (P7 / P8 / P10 완료 후):
  2단계 분류 구조                  +0.03~0.06  (FLAT 분리 전용 학습)
  레짐 조건부 GBM 분기             +0.05~0.10  (추세/횡보/고변동 전문화)
  소급/실시간 분리 앙상블          +0.02~0.04
                                          ↓
장기 목표:  평균 F1 ≈ 0.58~0.72
```

---

## 6. 주의 사항 및 제약

### 6-1. 소급 데이터 OFI 불완전성
- 168거래일(소급)의 `ofi_*` = 0.0 → GBM이 "OFI 없음 = 특정 패턴"으로 학습할 수 있음
- `feature_quality_score=0.3` 피처가 GBM에 소급분 마커로 입력됨
- 실시간 데이터가 60일 이상 쌓이면 소급분 비중 자동 희석

### 6-2. USE_FIXED_LABEL_THRESHOLD 운영 주의
- `True`: 학습은 `HORIZON_THRESHOLDS` 고정값, 실전은 rolling sigma 유지
- `False`로 되돌리면 레이블 드리프트 재발 가능 — 변경 전 영향 분석 필수
- sigma_at_t(검증 일관성)와 별개 개념 — 둘 다 필요

### 6-3. 경로 조건부 레이블 (path_ratio=0.45) 영향
- FLAT 비율 +5~12%p 증가 예상 → 학습 후 진입 빈도 소폭 감소 가능
- 진입이 과도하게 줄면 path_ratio=0.50으로 완화 검토

### 6-4. RF 가중치 조정 조건
- RF OOB score < 35% 지속 시 → RF 가중치 0.30 → 0.15로 축소
- `rf_model.get_oob_scores()` 매 재학습 후 로그 확인 필수

### 6-5. 절대 원칙 (CLAUDE.md)
- CVD, VWAP, OFI 코어 피처 교체 불가
- 오버나이트 금지(15:10 강제 청산), Circuit Breaker 5종 조건 유지

### 6-6. Python 3.7 32-bit 제약
- scipy >= 1.7 사용 불가 (32-bit DLL 충돌)
- `from __future__ import annotations` 불가
- `Optional[X]`, `Dict[K,V]` 형식 사용 (PEP 604 `X | Y` 불가)
- RF `n_jobs=1` 필수 (멀티코어 불안정)

---

## 7. 관련 파일 인덱스

| 파일 | 역할 | 상태 |
|---|---|---|
| `scripts/backfill_features.py` | 소급 피처 생성/갱신 (`--update-features`) | ✅ |
| `scripts/optimize_sigma_k.py` | 호라이즌별 최적 σ_k 탐색 | ✅ |
| `features/technical/volume_profile.py` | POC/Value Area 계산기 | ✅ 신규 |
| `features/feature_builder.py` | 실시간 피처 빌더 (17개 추가) | ✅ |
| `model/rf_horizon_model.py` | RF 이종 앙상블 모델 | ✅ 신규 |
| `model/ensemble_decision.py` | 코히어런스 게이트 + F1 적응형 가중치 | ✅ |
| `learning/batch_retrainer.py` | GBM 재학습 (경로 조건부 레이블, RF 연동) | ✅ |
| `learning/calibration.py` | Platt Scaling Calibrator | ✅ (기존) |
| `config/settings.py` | MIN_CONF_TABLE, SIGMA_K_PER_HORIZON, COHERENCE_GATE_MIN, USE_FIXED_LABEL_THRESHOLD | ✅ |
| `strategy/entry/time_strategy_router.py` | `get_horizon_min_confs()` 추가 | ✅ |
| `main.py` | P4 호라이즌 필터 + RF blend + F1 누적 + 피처 갱신 | ✅ |
| `docs/ROLLING_SIGMA_IMPL_PLAN.md` | Phase 0~3 rolling σ 구현 상세 | 참조 |
| `docs/THRESHOLD_WFA_MONITOR.md` | WFA 3단계 전환 계획 | 참조 |
| `dev_memory/NEXT_TODO.md` | 잔여 운영 확인 항목 | 참조 |
