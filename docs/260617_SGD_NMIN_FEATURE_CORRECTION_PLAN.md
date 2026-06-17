# SGD 학습 피처 N분봉 교정 — 검토 및 일정

> 작성일: 2026-06-17
> 배경: 189차 세션 분석 — SGD 예측(N분봉)과 학습(1분봉) 피처 불일치 확인

---

## 1. 검토 목적

GBM은 배치 재학습(Phase 2) 시 N분봉 재계산 피처로 학습하고, 예측 시에도
`_hz_feat_cache`(N분봉 완성봉 기반)를 사용한다. SGD 온라인 학습기는 예측 시
동일하게 N분봉 피처(`_hz_feat_vecs`)를 사용하지만, **학습(learn()) 시에는
DB에 저장된 1분봉 피처(`_dv.get("features")`)를 사용한다.**

이 불일치가 SGD 정확도 저하, 단방향 붕괴(collapse), conf 고착의 구조적
원인이 될 수 있음을 확인하고, 교정 방안과 적정 구현 일정을 검토한다.

---

## 2. 현재 경로 구조

```
[GBM 학습]  batch_retrainer → raw_features_horizon (N분봉 재계산값) ✅
[GBM 예측]  _hz_feat_cache[h] → N분봉 피처                          ✅

[SGD 예측]  _hz_feat_vecs[h] = _hz_feat_cache[h]  → N분봉 피처      ✅
[SGD 학습]  _dv.get("features")                   → 1분봉 피처       ❌

피처 이름(NAME)은 horizon_feature_sets.json으로 호라이즌별 고정.
불일치는 이름이 아닌 값(VALUE)의 출처 문제.
```

---

## 3. 방안 정의

### A안 — STEP 9 DB 저장 시 hz_feat_vecs 함께 저장 (정확)

예측 생성 시점(T)에 각 호라이즌별 N분봉 피처 벡터를 함께 DB에 저장한다.
검증 시점(T+N)에 해당 저장값을 꺼내 SGD learn()에 사용한다.

```
T=09:50  30m 예측 생성
         DB 저장: features(1m), hz_features_30m(30m봉 피처)
T=10:20  30m 검증
         SGD 학습 입력: hz_features_30m (T 시점의 30m봉 값) ← 시간 일치
```

### B안 — 학습 시 현재 _hz_feat_cache 사용 (근사)

검증 시점(T+N)에 현재 `_hz_feat_cache[h]`(가장 최근 완성 N분봉 값)를
SGD 학습 입력으로 사용한다. DB 구조 변경 없음.

```
T=09:50  30m 예측 생성 (피처: 09:30봉 기준)
T=10:20  30m 검증
         SGD 학습 입력: _hz_feat_cache["30m"] = 10:00봉 기준 피처 ← 30분 불일치
```

---

## 4. 이득과 손실 비교

### 4-1. A안

| 항목 | 내용 |
|---|---|
| **이득: 시간 완전 일치** | 예측에 쓴 N분봉 피처 = 학습 입력. "T의 시장상황 → T+N 결과" 인과관계 정확 |
| **이득: 피처 분포 일치** | StandardScaler가 N분봉 분포로 일관 적합 → 스케일러 왜곡 없음 |
| **이득: SGD collapse 완화** | 예측·학습 피처 공간 통일 → 단방향 과적합 감소 |
| **손실: DB 저장량 증가** | 전체 피처(97개) × 6호라이즌 = 최대 582 float32 추가/분봉. 슬라이싱 저장 시 약 76개 추가 |
| **손실: STEP 9 지연** | 매분 DB 저장 데이터량 증가 → 파이프라인 크리티컬 경로 영향 가능 |
| **손실: DB 마이그레이션** | predictions 테이블 구조 변경 + 학습 조회 경로 변경 |
| **손실: 초기 구간 처리** | 09:00~09:29 `_hz_feat_cache["30m"]` 없음 → 반감기 fallback값 저장 또는 NULL 처리 예외 경로 필요 |

### 4-2. B안

| 항목 | 내용 |
|---|---|
| **이득: 피처 공간 일치** | 예측·학습 모두 N분봉 분포 → 스케일러 일관성 |
| **이득: 구현 단순** | DB 변경 없음. `_dv.get("features")` → `_hz_feat_cache[h]` 교체만 |
| **이득: 저장 비용 없음** | STEP 9, DB 무변경 |
| **손실: 시간 불일치** | T의 예측을 T+N의 N분봉 피처로 학습 |
| **손실: 미래 데이터 오염 (핵심)** | 검증 시점 N분봉이 예측 결과 기간의 가격 움직임을 이미 반영 → "결과 후 피처 + 결과 레이블" 학습 위험 |

**B안 호라이즌별 미래 오염 위험도:**

| 호라이즌 | 검증 후 N분봉 경과 | 오염 위험 |
|---|---|---|
| 1m | T+1 → 1분봉 항상 최신 | 낮음 |
| 3m | 최대 5분 차이 | 낮음 |
| 5m | 최대 9분 차이 | 보통 |
| 10m | 최대 19분 차이 | 높음 |
| 15m | 최대 29분 차이 | 높음 |
| **30m** | **최대 59분 차이** | **매우 높음** |

### 4-3. 종합

| 항목 | 현재(1분봉) | A안 | B안 |
|---|---|---|---|
| 예측-학습 피처 분포 일치 | ❌ | ✅ | ✅ |
| 시간 정확성 | ✅ | ✅ | ❌ |
| 미래 데이터 오염 | 없음 | 없음 | 30m에서 심각 |
| DB 변경 | 없음 | 필요 | 없음 |
| 구현 복잡도 | — | 높음 | 낮음 |

---

## 5. 호라이즌별 피처셋과 tick 민감도

피처를 두 군으로 분류한다:

- **A군**: 봉 크기 무관 — 1m값 ≈ Nm값 (옵션 체인, 일봉 매크로, 일간 VWAP/POC/VA)
- **B군**: 봉 크기 의존 — 1m값 ≠ Nm값 (ATR, 거래량, MLOFI, hurst, 독성MA 등)

### 5-1. 10m 피처셋 (15개) — 심각도 높음

| 피처 | 군 | 1m봉 학습 시 문제 |
|---|---|---|
| `hurst` | B군 | 1m 20봉 허스트 ≠ 10m 20봉 허스트. 프랙탈 시간척도 완전히 다름 |
| `mlofi_slope` | B군 | 1m MLOFI 기울기 ≈ 틱 잡음. 10m MLOFI는 수급 방향성 신호 |
| `vwap_momentum` | B군 | 5분 VWAP 이동속도 → 1m봉 기준값은 noise에 가까움 |
| `cvd_monotone_ratio` | B군 | 1m 20분 롤링 vs 10m 200분 롤링 — 완전히 다른 단조성 |
| `micro_regime_code` | B군 | 1분봉 기반 레짐 코드. 10m 레이블과 시간척도 불일치 |
| 나머지 10개 | A군 | 옵션·매크로·POC → 봉 무관 ✅ |

**15개 중 5개 오염**

### 5-2. 15m 피처셋 (21개) — 심각도 중

| 피처 | 군 | 1m봉 학습 시 문제 |
|---|---|---|
| `volume_acceleration` | B군 | 1m 거래량 가속도 vs 15m 거래량 가속도 — 절대값 15배 차이 |
| `avg_volume` | B군 | 동일, 스케일 불일치 |
| `atr_ratio` | B군 | 1m ATR/평균ATR vs 15m ATR/평균ATR — 변동성 척도 상이 |
| `toxicity_atr_stress` | B군 | ATR 기반 파생, 동일 문제 |
| 나머지 17개 | A군 | 옵션·수급·매크로·VA → 봉 무관 ✅ |

**21개 중 4개 오염**

### 5-3. 30m 피처셋 (18개) — 심각도 중, 설계 안전장치 있음

30m exclude 목록에 OFI/MLOFI/microprice/cancel_add 등 tick-최민감 피처가
이미 제거되어 있음. 다만 아래 B군은 여전히 존재한다.

| 피처 | 군 | 1m봉 학습 시 문제 |
|---|---|---|
| `atr_ratio` | B군 | 1m ATR vs 30m ATR — 스케일 30배 |
| `toxicity_score_ma` | B군 | 1m 틱 독성 이동평균 vs 30m 단위 독성 |
| `queue_signal_ma` | B군 | 1m 큐신호 MA vs 30m 단위 큐신호 |
| `toxicity_atr_stress` | B군 | ATR 파생 |
| `threshold_feasibility` | B군 | ATR 기반 변동성 실현 가능성 |
| `opt_pcr_slope_norm` | B군 | PCR 기울기 롤링 윈도우 — 1m롤링 ≠ 30m롤링 |
| `micro_regime_code` | B군 | 1분봉 레짐 코드 |
| 나머지 11개 | A군 | 옵션 4종·매크로 2종·VWAP·VA → 봉 무관 ✅ |

**18개 중 7개 오염**

### 5-4. 단기 호라이즌 (1m·3m·5m) — 상대적으로 무해

1m·3m 피처셋은 tick 기반 신호(OFI, MLOFI, CVD, microprice)가 주력이며
이 피처들은 1분봉 기준으로 계산되는 것이 원래 의도다.
B안(단기만 _hz_feat_cache 사용)으로도 1m·3m는 bar_age가 0~2분으로
매우 짧아 실질 차이가 없고, 미래 오염 위험도 낮다.

---

## 6. 즉시 적용 가능한 중간 단계

A안 전체 구현 전, B군 피처만 선별 교체하는 방식으로 핵심 오염을 제거한다.

```python
# SGD 학습 시 B군 피처 인덱스를 _hz_feat_cache 값으로 교체
B_FEAT_NAMES = {
    "10m": ["hurst", "mlofi_slope", "vwap_momentum", "cvd_monotone_ratio"],
    "15m": ["volume_acceleration", "avg_volume", "atr_ratio", "toxicity_atr_stress"],
    "30m": ["atr_ratio", "toxicity_score_ma", "queue_signal_ma",
            "toxicity_atr_stress", "threshold_feasibility"],
}
# 해당 피처 인덱스만 _hz_feat_cache[h]에서 꺼내 덮어쓰기
# 나머지는 기존 _dv.get("features") 유지
```

DB 구조 변경 없이 핵심 B군 오염 피처를 교정. 미래 오염 위험도 없음
(B군 피처 자체가 N분봉 기반 안정 신호라 오염 민감도 낮음).

---

## 7. A안 전체 구현 선행 조건

| 조건 | 현재 상태 | 충족 기준 |
|---|---|---|
| GBM 피처셋 안정화 | ❌ need_add 14개 미포함 | Phase C 재학습 완료 + pkl 고정 |
| DB 스키마 안정 | ❌ 잦은 컬럼 추가 | 스키마 변경 없이 4주 이상 안정 |
| SGD 기여도 실증 | ❌ acc 42%, P2-D 89% 차단 | SGD acc 48% 이상 4주 평균 유지 |
| 모의투자 검증 | ❌ 진행 중 | 모의투자 4주 양수 수익률 |

---

## 8. 권고 및 일정

| 시기 | 작업 | 근거 |
|---|---|---|
| **즉시 (189차~)** | 중간 단계: B군 피처 선별 교정 | DB 변경 없이 핵심 오염 제거 가능 |
| **Phase C 재학습 완료 후** (2026-07 예상) | A안 DB 스키마 설계 확정 | 피처셋 고정 후 저장 구조 결정 의미 있음 |
| **모의투자 4주 완료 후** (2026-07~08 예상) | A안 구현 판단 | SGD acc 실증 + DB 안정 + 피처 고정 3조건 충족 시 구현 |
| **Phase 5 진입 직전** | A안 구현 필수 | 실전에서 SGD 오염 학습은 직접 손실로 연결 |

> **지금 A안 전체를 구현하면 손해다.**
> 피처셋이 아직 유동적이고, SGD 기여도가 불확실하며,
> 중간 단계(B군 선별 교정)로 핵심 오염은 지금 제거 가능하다.

---

## 9. 참고 — 관련 파일

| 파일 | 역할 |
|---|---|
| `featureset by horizon/horizon_feature_sets.json` | 호라이즌별 피처 include/exclude 정의 |
| `features/bar_aggregator.py` | 1분봉 → N분봉 완성봉 집계 |
| `features/feature_decay.py` | 반감기 fallback 가중치 |
| `main.py:3879~3927` | _hz_feat_cache 관리 + BAR_CACHE_DECAY 적용 |
| `main.py:5641~5675` | SGD 학습 경로 (교정 대상) |
| `learning/online_learner.py` | SGD learn() / predict_proba() |
