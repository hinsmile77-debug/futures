# 호라이즌별 미가용 피처 추가 적기 보고서

> 작성일: 2026-06-17 (191차 세션)
> 기준 데이터: raw_features 75,189행, 재학습 데이터 40,080행 × 97열
> 추가 기준: 재학습 데이터의 **10% = 4,000행** 도달 시

---

## 현재 미가용(need_add) 피처 목록

`[FeatureReg] Xm: N개 피처 미가용 (need_add) → 제외` 로그 기준.

| 호라이즌 | 미가용 피처 |
|---|---|
| 1m | `queue_directional_depletion`, `micro_regime_code` |
| 3m | `cvd_monotone_ratio` |
| 5m | `opt_chain_pcr`, `cvd_monotone_ratio` |
| 10m | `opt_atm_put_oi`, `opt_gex_sign`, `cvd_monotone_ratio`, `micro_regime_code` |
| 15m | `opt_gex_bn`, `opt_chain_pcr`, `opt_atm_call_oi`, `opt_atm_put_oi`, `threshold_feasibility` |
| 30m | `opt_gex_bn`, `opt_chain_pcr`, `opt_atm_call_oi`, `opt_atm_pcr`, `threshold_feasibility` |

※ `bear_reversal_signal` — 동일 세션(191차)에 **삭제 처리** (일평균 10봉/일, 0.2% 희소, 390일 소요 → `ff68ac1`)

---

## 피처별 수집 현황 및 도달 예상일

> 측정 기준: 2026-06-17 장 마감 시점

| 피처 | 그룹 | 현재 행 수 | 일평균 봉/일 | 4,000행 도달 예상 |
|---|---|---|---|---|
| `threshold_feasibility` | 임계값 | 3,726 | 364 | **06-18 (내일)** |
| `queue_directional_depletion` | 미시구조 | 2,889 | 361 | **06-20** |
| `micro_regime_code` | 미시구조 | 2,330 | 227 | **06-26** |
| `cvd_monotone_ratio` | 미시구조 | 2,350 | 176 | **06-28~07-05** ※변동 심함 |
| `opt_chain_pcr` | 옵션 체인 | 670 | 335 | **06-29** |
| `opt_gex_bn` | 옵션 체인 | 670 | 335 | **06-29** |
| `opt_gex_sign` | 옵션 체인 | 670 | 335 | **06-29** |
| `opt_atm_call_oi` | 옵션 ATM | 538 | 269 | **07-02** |
| `opt_atm_pcr` | 옵션 ATM | 541 | 270 | **07-02** |
| `opt_atm_put_oi` | 옵션 ATM | 419 | 210 | **07-09** |

---

## 피처 특성 분류

### 상시 수집 피처 (매분 생성, 일평균 300~364봉)

| 피처 | 수집 시작 | 성격 |
|---|---|---|
| `threshold_feasibility` | 2026-06-02 | ATR 기반 진입 임계값 실현가능성 |
| `queue_directional_depletion` | 2026-06-08 | 호가 방향성 고갈 강도 (119차 신규) |
| `opt_chain_pcr`, `opt_gex_bn`, `opt_gex_sign` | 2026-06-16 | 옵션 체인 PCR·GEX (178차 수집 시작) |

### 조건부 수집 피처 (특정 조건 충족 시만 계산)

| 피처 | 수집 시작 | 일평균 | 비고 |
|---|---|---|---|
| `micro_regime_code` | 2026-06-02 | 227 | 미시구조 레짐 식별 코드 |
| `opt_atm_call_oi`, `opt_atm_pcr` | 2026-06-16 | ~270 | ATM 옵션 체인 완성 시 |
| `opt_atm_put_oi` | 2026-06-16 | 210 | ATM Put OI (수집 안정화 중) |

### 변동성 높은 피처 (일별 편차 큼)

| 피처 | 일별 범위 | 비고 |
|---|---|---|
| `cvd_monotone_ratio` | 92~329봉/일 | CVD 단조성 비율, 시장 상황 의존 |

---

## 단계별 추가 일정

### 1단계 — 이번 주 (06-18~06-20)

```
threshold_feasibility      → 06-18 이후 active 전환
queue_directional_depletion → 06-20 이후 active 전환
```

**적용 호라이즌:**
- `threshold_feasibility`: 15m, 30m 피처셋 보완
- `queue_directional_depletion`: 1m 피처셋 보완

**전환 방법:**
```python
# featureset by horizon/horizon_feature_sets.json
# _feature_status_summary.need_add_features 에서 제거
# 해당 호라이즌 피처 배열에 추가

# shap_feature_registry.json — 이미 active_features에 없으면 추가
# 또는 다음 EOD 재학습 후 FeatureReg 로그에서 자동 활성화 확인
```

### 2단계 — 2~3주 후 (06-26~07-02)

```
micro_regime_code           → 06-26 이후
cvd_monotone_ratio          → 06-28~07-05 (변동 감안)
opt_chain_pcr               → 06-29 이후  ┐
opt_gex_bn                  → 06-29 이후  ├ opt_chain 3종 일괄
opt_gex_sign                → 06-29 이후  ┘
opt_atm_call_oi             → 07-02 이후  ┐
opt_atm_pcr                 → 07-02 이후  ┘ opt_atm 2종
```

**적용 호라이즌:**
- `micro_regime_code`: 1m, 10m
- `cvd_monotone_ratio`: 3m, 5m, 10m
- opt_chain 3종: 5m, 10m, 15m, 30m
- opt_atm 2종: 10m, 15m, 30m

**기존 NEXT_TODO 조건 (179차):**
```sql
SELECT COUNT(*) FROM raw_features
WHERE features LIKE '%opt_chain_pcr%'
  AND CAST(json_extract(features,'$.opt_chain_pcr') AS REAL) != 0
-- > 3,000행 → 현재 670행, 약 7일 후 달성
```

### 3단계 — 4주 후 (07-09)

```
opt_atm_put_oi              → 07-09 이후
```

**적용 호라이즌:** 10m, 15m

---

## 삭제 처리 내역

| 피처 | 삭제 사유 | 커밋 |
|---|---|---|
| `bear_reversal_signal` | 일평균 10봉/일, DB 0.2%, 4,000행 도달 390일 → 재학습 기여 없음 | `ff68ac1` |

---

## 참고: 피처 추가 후 확인 사항

1. EOD 재학습 로그에서 `[FeatureReg] Xm: bear_reversal_signal 제외` 소멸 확인
2. 추가된 호라이즌 재학습 acc 변화 모니터링 (단기 소폭 변동 예상)
3. `피처 슬라이싱: 97 → N개`에서 N이 증가하는지 확인

---

## 전체 완료 예상 시점

| 시점 | 완료 피처 수 | 비고 |
|---|---|---|
| 2026-06-20 | +2개 | threshold_feasibility, queue_directional_depletion |
| 2026-07-02 | +7개 추가 | micro_regime_code, cvd_monotone_ratio, opt_chain 3종, opt_atm 2종 |
| 2026-07-09 | +1개 추가 | opt_atm_put_oi |
| **2026-07-09** | **전체 10개 완료** | need_add 피처 전부 active 전환 |
