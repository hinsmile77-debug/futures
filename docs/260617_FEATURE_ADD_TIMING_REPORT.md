# 호라이즌별 미가용 피처 추가 적기 보고서

> 작성일: 2026-06-17 (191차 세션)
> 마지막 업데이트: 2026-06-23 (231차 세션) — threshold_feasibility·queue_directional_depletion 활성화, bull/bear 시그널 삭제
> 기준 데이터: raw_features 76,564행 (2026-06-23 기준), 재학습 데이터 39,859행 × 97열
> 추가 기준: 재학습 데이터의 **10% = 4,000행** 도달 시

---

## 현재 미가용(need_add) 피처 목록 (2026-06-23 기준)

`[FeatureReg] Xm: N개 피처 미가용 (need_add) → 제외` 로그 기준.

| 호라이즌 | 미가용 피처 |
|---|---|
| 1m | `micro_regime_code` |
| 3m | `cvd_monotone_ratio` |
| 5m | `opt_chain_pcr`, `cvd_monotone_ratio` |
| 10m | `opt_atm_put_oi`, `opt_gex_sign`, `cvd_monotone_ratio`, `micro_regime_code` |
| 15m | `opt_gex_bn`, `opt_chain_pcr`, `opt_atm_call_oi`, `opt_atm_put_oi`, `opt_pcr_extreme_bearish` |
| 30m | `opt_gex_bn`, `opt_chain_pcr`, `opt_atm_call_oi`, `opt_atm_pcr`, `opt_pcr_extreme_bearish` |

**활성화 이력:**
- `threshold_feasibility` — 2026-06-23 **활성화** [DONE] (5,101행 달성, 06-18 예정 대비 5일 지연 → 15m·30m `in_pkl` 전환)
- `queue_directional_depletion` — 2026-06-23 **활성화** [DONE] (4,253행 달성, 06-20 예정 대비 3일 지연 → 1m `in_pkl` 전환)

**삭제 이력:**
- `bear_reversal_signal` — 2026-06-17 **삭제** (일평균 10봉/일, 0.2% 희소, 4,000행 도달 390일 소요 → `ff68ac1`)
- `bull_reversal_signal` — 2026-06-23 **삭제** (145행, 0.2% 희소 — bear 버전과 동일 사유 → `d3281c9`)
- `bull_exhaustion_signal` — 2026-06-23 **삭제** (2행, 사실상 미수집 → `d3281c9`)

---

## 피처별 수집 현황 및 도달 예상일 (2026-06-23 기준)

| 피처 | 그룹 | 현재 행 수 | 일평균 봉/일 | 4,000행 도달 예상 | 상태 |
|---|---|---|---|---|---|
| `threshold_feasibility` | 임계값 | ~~3,726~~ → **5,101** | 364 | ~~06-18~~ → **06-23 달성** | ✅ 활성화 |
| `queue_directional_depletion` | 미시구조 | ~~2,889~~ → **4,253** | 361 | ~~06-20~~ → **06-23 달성** | ✅ 활성화 |
| `micro_regime_code` | 미시구조 | **3,253** | 227 | **06-26** | ⏳ 대기 |
| `cvd_monotone_ratio` | 미시구조 | **2,902** | 176 | **06-28~07-05** ※변동 심함 | ⏳ 대기 |
| `opt_pcr_extreme_bearish` | 옵션 체인 | **1,832** | ~335 | **07-01 예상** | ⏳ 대기 |
| `opt_chain_pcr` | 옵션 체인 | **1,897** | 335 | **06-29** | ⏳ 대기 |
| `opt_gex_bn` | 옵션 체인 | **1,897** | 335 | **06-29** | ⏳ 대기 |
| `opt_gex_sign` | 옵션 체인 | **1,897** | 335 | **06-29** | ⏳ 대기 |
| `opt_atm_call_oi` | 옵션 ATM | **1,724** | 269 | **07-02** | ⏳ 대기 |
| `opt_atm_pcr` | 옵션 ATM | **1,738** | 270 | **07-02** | ⏳ 대기 |
| `opt_atm_put_oi` | 옵션 ATM | **1,616** | 210 | **07-09** | ⏳ 대기 |

---

## 피처 특성 분류

### 상시 수집 피처 (매분 생성, 일평균 300~364봉)

| 피처 | 수집 시작 | 성격 | 상태 |
|---|---|---|---|
| `threshold_feasibility` | 2026-06-02 | ATR 기반 진입 임계값 실현가능성 | ✅ 활성화 (06-23) |
| `queue_directional_depletion` | 2026-06-08 | 호가 방향성 고갈 강도 (119차 신규) | ✅ 활성화 (06-23) |
| `opt_chain_pcr`, `opt_gex_bn`, `opt_gex_sign` | 2026-06-16 | 옵션 체인 PCR·GEX (178차 수집 시작) | ⏳ 06-29 예정 |
| `opt_pcr_extreme_bearish` | 2026-06-16 | 극단 약세 PCR | ⏳ 07-01 예상 |

### 조건부 수집 피처 (특정 조건 충족 시만 계산)

| 피처 | 수집 시작 | 일평균 | 비고 | 상태 |
|---|---|---|---|---|
| `micro_regime_code` | 2026-06-02 | 227 | 미시구조 레짐 식별 코드 | ⏳ 06-26 예정 |
| `opt_atm_call_oi`, `opt_atm_pcr` | 2026-06-16 | ~270 | ATM 옵션 체인 완성 시 | ⏳ 07-02 예정 |
| `opt_atm_put_oi` | 2026-06-16 | 210 | ATM Put OI (수집 안정화 중) | ⏳ 07-09 예정 |

### 변동성 높은 피처 (일별 편차 큼)

| 피처 | 일별 범위 | 비고 |
|---|---|---|
| `cvd_monotone_ratio` | 92~329봉/일 | CVD 단조성 비율, 시장 상황 의존 |

---

## 단계별 추가 일정

### 1단계 — [DONE 2026-06-23]

```
threshold_feasibility       → 06-23 활성화 완료 (예정 06-18, 5일 지연)
queue_directional_depletion → 06-23 활성화 완료 (예정 06-20, 3일 지연)
```

**적용 호라이즌:**
- `threshold_feasibility`: 15m, 30m (in_pkl 전환, `d3281c9`)
- `queue_directional_depletion`: 1m (in_pkl 전환, `d3281c9`)

**내일(06-24) EOD 확인 포인트:**
```
1m 피처 슬라이싱: 97 → 13개  (+1 queue_directional_depletion)
15m 피처 슬라이싱: 97 → 16개  (+1 threshold_feasibility)
30m 피처 슬라이싱: 97 → 12개  (+1 threshold_feasibility)
[FeatureReg] 1m: queue_directional_depletion 제외  → 소멸 확인
[FeatureReg] 15m·30m: threshold_feasibility 제외  → 소멸 확인
```

---

### 2단계 — 2~3주 후 (06-26~07-02)

```
micro_regime_code           → 06-26 이후  (현재 3,253행, +747행 필요)
cvd_monotone_ratio          → 06-28~07-05 (현재 2,902행, +1,098행, 변동 감안)
opt_chain_pcr               → 06-29 이후  ┐ (현재 1,897행, +2,103행)
opt_gex_bn                  → 06-29 이후  ├ opt_chain 3종 일괄
opt_gex_sign                → 06-29 이후  ┘
opt_atm_call_oi             → 07-02 이후  ┐ (현재 1,724행, +2,276행)
opt_atm_pcr                 → 07-02 이후  ┘ opt_atm 2종
opt_pcr_extreme_bearish     → 07-01 예상   (현재 1,832행, +2,168행)
```

**적용 호라이즌:**
- `micro_regime_code`: 1m, 10m
- `cvd_monotone_ratio`: 3m, 5m, 10m
- opt_chain 3종 + opt_pcr_extreme_bearish: 5m, 10m, 15m, 30m
- opt_atm_call_oi·opt_atm_pcr: 10m, 15m, 30m

**활성화 기준 쿼리:**
```sql
SELECT COUNT(*) FROM raw_features
WHERE json_extract(features,'$.opt_chain_pcr') IS NOT NULL
  AND json_extract(features,'$.opt_chain_pcr') != 0
-- > 4,000행 달성 시 활성화 (현재 1,897행)
```

---

### 3단계 — 4주 후 (07-09)

```
opt_atm_put_oi              → 07-09 이후  (현재 1,616행, +2,384행)
```

**적용 호라이즌:** 10m, 15m

---

## 삭제 처리 내역

| 피처 | 삭제 사유 | 날짜 | 커밋 |
|---|---|---|---|
| `bear_reversal_signal` | 일평균 10봉/일, DB 0.2%, 4,000행 도달 390일 소요 | 2026-06-17 (191차) | `ff68ac1` |
| `bull_reversal_signal` | 145행 (0.2%) — bear 버전과 동일 사유 | 2026-06-23 (231차) | `d3281c9` |
| `bull_exhaustion_signal` | 2행 (0.0%) — 사실상 미수집 | 2026-06-23 (231차) | `d3281c9` |

---

## 참고: 피처 추가 후 확인 사항

1. EOD 재학습 로그에서 해당 피처 `[FeatureReg] Xm: {feature} 제외` 소멸 확인
2. 추가된 호라이즌 재학습 acc 변화 모니터링 (단기 소폭 변동 예상)
3. `피처 슬라이싱: 97 → N개`에서 N이 예상대로 증가하는지 확인

---

## 전체 완료 예상 시점

| 시점 | 누적 활성화 | 완료 피처 | 비고 |
|---|---|---|---|
| ~~2026-06-20~~ **2026-06-23** | +2개 | threshold_feasibility, queue_directional_depletion | [DONE] |
| 2026-06-26 | +1개 추가 | micro_regime_code | |
| 2026-06-29 | +3개 추가 | opt_chain_pcr, opt_gex_bn, opt_gex_sign | 일괄 |
| 2026-07-01 예상 | +1개 추가 | opt_pcr_extreme_bearish | |
| 2026-07-02 | +2개 추가 | opt_atm_call_oi, opt_atm_pcr | |
| 2026-07-05 예상 | +1개 추가 | cvd_monotone_ratio | 변동 감안 |
| 2026-07-09 | +1개 추가 | opt_atm_put_oi | |
| **2026-07-09** | **전체 11개 완료** | need_add 피처 전부 active 전환 | opt_pcr_extreme_bearish 포함 |
