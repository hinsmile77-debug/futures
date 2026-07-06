# 호라이즌별 미가용 피처 추가 적기 보고서

> 작성일: 2026-06-17 (191차 세션)
> 마지막 업데이트: 2026-06-25 — 30m 피처 미탑재 영향 섹션 추가 / horizon_feature_sets.json `in_pkl` 오표기 2건 정정 (threshold_feasibility·queue_directional_depletion)
> 기준 데이터: raw_features 76,889행 (2026-06-24 기준), 재학습 데이터 39,859행 × 97열
> 추가 기준: 재학습 데이터의 **10% = 4,000행** 도달 시

---

## 현재 미가용(need_add) 피처 목록 (2026-06-24 기준)

`[FeatureReg] Xm: N개 피처 미가용 (need_add) → 제외` 로그 기준.

| 호라이즌 | 미가용 피처 |
|---|---|
| 1m | `queue_directional_depletion`, `micro_regime_code` |
| 3m | `cvd_monotone_ratio` |
| 5m | `opt_chain_pcr`, `cvd_monotone_ratio` |
| 10m | `opt_atm_put_oi`, `opt_gex_sign`, `cvd_monotone_ratio`, `micro_regime_code` |
| 15m | `opt_gex_bn`, `opt_chain_pcr`, `opt_atm_call_oi`, `opt_atm_put_oi`, `threshold_feasibility`, `opt_pcr_extreme_bearish` |
| 30m | `opt_gex_bn`, `opt_chain_pcr`, `opt_atm_call_oi`, `opt_atm_pcr`, `threshold_feasibility`, `opt_pcr_extreme_bearish`, `micro_regime_code` |

**활성화 이력:**
- `threshold_feasibility` — 2026-06-23 `in_pkl` 전환 시도 → **2026-06-25 재확인 결과 실제 pkl 미포함** → `need_add` 재정정 (15m·30m)
- `queue_directional_depletion` — 2026-06-23 `in_pkl` 전환 시도 → **2026-06-25 재확인 결과 실제 pkl 미포함** → `need_add` 재정정 (1m)

**삭제 이력:**
- `bear_reversal_signal` — 2026-06-17 **삭제** (일평균 10봉/일, 0.2% 희소, 4,000행 도달 390일 소요 → `ff68ac1`)
- `bull_reversal_signal` — 2026-06-23 **삭제** (145행, 0.2% 희소 — bear 버전과 동일 사유 → `d3281c9`)
- `bull_exhaustion_signal` — 2026-06-23 **삭제** (2행, 0.0% — 사실상 미수집 → `d3281c9`)

---

## 피처별 수집 현황 및 도달 예상일 (2026-06-24 실측)

| 피처 | 그룹 | 현재 행 수 | 일평균 봉/일 | 4,000행 도달 예상 | 상태 |
|---|---|---|---|---|---|
| `threshold_feasibility` | 임계값 | **5,101+** | 364 | **06-23 달성** | ✅ 활성화 |
| `queue_directional_depletion` | 미시구조 | **4,253+** | 361 | **06-23 달성** | ✅ 활성화 |
| `micro_regime_code` | 미시구조 | **3,493** | 240 | **06-29** | ⏳ 대기 |
| `cvd_monotone_ratio` | 미시구조 | **2,979** | 176 | **07-02~07-09** ※변동 심함 | ⏳ 대기 |
| `opt_chain_pcr` | 옵션 체인 | **2,202** | 314 | **07-02** | ⏳ 대기 |
| `opt_gex_bn` | 옵션 체인 | **2,202** | 314 | **07-02** | ⏳ 대기 |
| `opt_gex_sign` | 옵션 체인 | **2,202** | 314 | **07-02** | ⏳ 대기 |
| `opt_pcr_extreme_bearish` | 옵션 체인 | **2,114** | 302 | **07-03** | ⏳ 대기 |
| `opt_atm_call_oi` | 옵션 ATM | **2,029** | 290 | **07-03** | ⏳ 대기 |
| `opt_atm_pcr` | 옵션 ATM | **2,043** | 292 | **07-03** | ⏳ 대기 |
| `opt_atm_put_oi` | 옵션 ATM | **1,921** | 274 | **07-07** | ⏳ 대기 |

> **일평균 계산 기준**: opt 계열은 수집 개시(2026-06-16) 이후 7거래일 누적 기준.

---

## [NEW 2026-06-24] opt_chain_snapshot 수집흐름 조사 결과

### 수집 파이프라인 (정상 확인)

```
[QTimer 300s — 메인 스레드 COM 안전]
_poll_option_chain()
  └─ OptionChainSnapshot.refresh(spot)
       └─ Dscbo1.OptionMst.BlockRequest()  (5분마다 실폴링)
            ├─ CpUtil.CpOptionCode: 체인 종목 목록 (캐시: data/option_chain.json)
            └─ ATM ±30pt 종목별 OI / Gamma 수집
                 → opt_chain_pcr / opt_gex_bn / opt_atm_call_oi / opt_atm_put_oi / opt_gex_sign

[매분 파이프라인 STEP 4]
option_chain_snap.get_features()  ← 캐시 읽기만 (블로킹 없음)
_option_combined = {**option_feats, **chain_feats}
feature_builder.build(option_data=_option_combined)
  └─ raw_features JSON blob에 opt_chain_pcr 등 포함 저장  ✅
```

### 일자별 수집률 (2026-06-16 수집 개시 이후)

| 날짜 | opt_chain_available > 0 | 전체 봉 | 수집률 |
|---|---|---|---|
| 2026-06-16 | 317 | 360 | **88%** |
| 2026-06-17 | 353 | 369 | **96%** |
| 2026-06-18 | 229 | 302 | **76%** |
| 2026-06-19 | 343 | 368 | **93%** |
| 2026-06-22 | 331 | 352 | **94%** |
| 2026-06-23 | 324 | 353 | **92%** |
| 2026-06-24 | 305 | 325 | **94%** |
| **합계** | **2,202** | **2,429** | **91%** |

### 실측값 샘플 (2026-06-24 장 마감)

```
opt_chain_pcr = 1.357~1.395  (풋 우세 — 정상 범위)
opt_gex_bn    = -80.992      (딜러 감마숏 — 변동성 확대 구간)
opt_atm_call_oi = 22~42
opt_atm_put_oi  = 11~67
```

→ **수집 자체는 정상 작동, 실데이터 값 유효**

---

## [CRITICAL] shap_feature_registry 게이트 이슈

opt 계열 피처는 **두 가지 소스**로 분리되어 있으며, feature_names.pkl 포함 여부가 다름:

| 소스 | 피처 | feature_names.pkl(97개) | shap_feature_registry.json |
|---|---|---|---|
| **PCRStore** (투자자 순매수 기반) | `opt_pcr_norm`, `opt_pcr_bearish`, `opt_pcr_slope_norm` 등 | ✅ 포함 | ✅ active |
| **OptionChainSnapshot** (Dscbo1.OptionMst 폴링) | `opt_chain_pcr`, `opt_gex_bn`, `opt_gex_sign`, `opt_atm_call_oi`, `opt_atm_pcr`, `opt_atm_put_oi` | ❌ 미포함 | ❌ 미포함 |

**결론**: raw_features JSON blob에는 opt_chain_pcr 등이 이미 저장되고 있지만, 재학습 시 `shap_feature_registry.json`의 `active_features`가 게이트 역할을 하여 자동 제외됨.

**활성화 시 필요한 작업 2단계:**
1. `horizon_feature_sets.json`에서 해당 피처 pkl 상태: `"need_add"` → `"in_pkl"` 전환
2. `shap_feature_registry.json`의 `active_features` 목록에 해당 피처 추가

4,000행 도달만으로는 부족하며, 위 두 파일 수동 업데이트 후 EOD 재학습 필요.

---

## 피처 특성 분류

### 상시 수집 피처 (매분 생성, 일평균 240~364봉)

| 피처 | 수집 시작 | 성격 | 상태 |
|---|---|---|---|
| `threshold_feasibility` | 2026-06-02 | ATR 기반 진입 임계값 실현가능성 | ✅ 활성화 (06-23) |
| `queue_directional_depletion` | 2026-06-08 | 호가 방향성 고갈 강도 (119차 신규) | ✅ 활성화 (06-23) |
| `opt_chain_pcr`, `opt_gex_bn`, `opt_gex_sign` | 2026-06-16 | 옵션 체인 PCR·GEX (178차 수집 시작) | ⏳ 07-02 예정 |
| `opt_pcr_extreme_bearish` | 2026-06-16 | 극단 약세 PCR | ⏳ 07-03 예상 |

### 조건부 수집 피처 (특정 조건 충족 시만 계산)

| 피처 | 수집 시작 | 일평균 | 비고 | 상태 |
|---|---|---|---|---|
| `micro_regime_code` | 2026-06-02 | 240 | 미시구조 레짐 식별 코드 | ⏳ 06-29 예정 |
| `opt_atm_call_oi`, `opt_atm_pcr` | 2026-06-16 | ~290 | ATM 옵션 체인 완성 시 | ⏳ 07-03 예정 |
| `opt_atm_put_oi` | 2026-06-16 | 274 | ATM Put OI | ⏳ 07-07 예정 |

### 변동성 높은 피처 (일별 편차 큼)

| 피처 | 일별 범위 | 비고 |
|---|---|---|
| `cvd_monotone_ratio` | 77~329봉/일 | CVD 단조성 비율, 시장 상황 의존 |

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

---

### 2단계 — 2026-06-29 ~ 07-03

```
micro_regime_code           → 06-29 이후  (현재 3,493행, +507행 필요)
cvd_monotone_ratio          → 07-02~07-09 (현재 2,979행, +1,021행, 변동 감안)
opt_chain_pcr               → 07-02 이후  ┐ (현재 2,202행, +1,798행)
opt_gex_bn                  → 07-02 이후  ├ opt_chain 3종 일괄
opt_gex_sign                → 07-02 이후  ┘
opt_atm_call_oi             → 07-03 이후  ┐ (현재 2,029행, +1,971행)
opt_atm_pcr                 → 07-03 이후  ┘ opt_atm 2종
opt_pcr_extreme_bearish     → 07-03 예상   (현재 2,114행, +1,886행)
```

**적용 호라이즌:**
- `micro_regime_code`: 1m, 10m
- `cvd_monotone_ratio`: 3m, 5m, 10m
- opt_chain 3종 + opt_pcr_extreme_bearish: 5m, 10m, 15m, 30m
- opt_atm_call_oi·opt_atm_pcr: 10m, 15m, 30m

**활성화 기준 쿼리:**
```sql
-- opt_chain_pcr 행 수 확인
SELECT COUNT(*) FROM raw_features
WHERE json_extract(features,'$.opt_chain_pcr') IS NOT NULL
  AND json_extract(features,'$.opt_chain_pcr') != 0
-- > 4,000행 달성 시 활성화 (현재 2,202행)

-- micro_regime_code 행 수 확인
SELECT COUNT(*) FROM raw_features
WHERE json_extract(features,'$.micro_regime_code') IS NOT NULL
  AND json_extract(features,'$.micro_regime_code') != 0
-- > 4,000행 달성 시 활성화 (현재 3,493행)
```

**⚠️ 활성화 시 shap_feature_registry.json 업데이트 필수** (게이트 이슈 섹션 참조)

---

### 3단계 — 2026-07-07

```
opt_atm_put_oi              → 07-07 이후  (현재 1,921행, +2,079행)
```

**적용 호라이즌:** 10m, 15m

---

## Phase D 재검증 타임라인

| 항목 | 날짜 | 비고 |
|---|---|---|
| opt 수집 개시 | 2026-06-16 | Dscbo1.OptionMst 수집 안정화 확인 |
| 현재 수집량 | 2,202행 (06-24) | 91% 수집률 (7거래일) |
| need_add 피처 전환 완료 예상 | **2026-07-07** | opt_atm_put_oi 기준 |
| **Phase D 재검증 실행 가능** | **2026-07-14 이후** | 전환 완료 후 1주 안정화 |

> 재검증 기준: opt_gex_bn(ρ=0.290), opt_chain_pcr(ρ=0.245) 핵심 신호 4주 이상 DB 축적 확인 후 공유 97개 vs. registry strict 선택 Walk-Forward 재실행 (10m → 15m → 30m 순).

---

## [UPDATE 2026-07-06, 296차] 30m 퇴역 최종 확정

재활성화 조건 ①(opt_gex_bn·opt_chain_pcr 등 8개 4,000행 달성)·③(registry 반영)은
292차(2026-07-06)에서 충족됐으나, 조건 ②(30m EOD CV acc ≥ 0.33)는 같은 날 15:46
EOD full_cv 재학습(26주·40,011행·105피처 완전 반영) 결과 **acc=0.3052로 여전히 미달**
(3클래스 랜덤 0.333보다도 낮음). 아래 각주("조건 ①만 달성하고 acc≥0.33 미달 시 필터
비활성 유지")에 따라 재활성화를 철회하고 **영구 퇴역으로 최종 결정**.

- `model/ensemble_decision.py`: CascadeCoherence·CoherenceGate에서도 30m 제외(기존
  가중합 제외에 추가) — 구조적 저성능 호라이즌의 노이즈 방향이 다른 게이트를 통해
  간접적으로 진입을 막는 경로까지 차단.
- `config/settings.py`: `ENSEMBLE_WEIGHTS`/`ENSEMBLE_WEIGHTS_CORR_ADJ`의 30m을
  0.0으로 명시(런타임은 이미 강제 0이었으나 설정값도 실제와 일치시킴), 나머지
  5개 호라이즌에 +0.03씩 재분배.
- predict_proba·GBM/RF 학습·CB③ P4 stage 모니터링은 연구/재평가용으로 계속 유지.
- 아래 "재활성화 조건" 섹션은 역사적 기록으로 유지하되, 현재 상태는 위 결정으로 대체됨.

---

## [NEW 2026-06-25] 30m 피처 미탑재 영향 및 임시 비활성화 조치 (296차에서 퇴역 확정으로 대체됨)

### 30m 영향 요약

2026-06-25 ERR-FATAL(09:00:59) 및 EOD 재학습 결과 분석에서 확인된 사항.

| 항목 | 상태 |
|---|---|
| EOD CV acc (30m) | **0.2796** — 3클래스 랜덤(0.333) 이하 |
| 원인 | need_add 피처 7개 미탑재 (opt_gex_bn·opt_chain_pcr·opt_atm_call_oi·opt_atm_pcr·opt_pcr_extreme_bearish·threshold_feasibility 등) |
| 앙상블 기여 | filter_only 정책 — 가중합 **완전 제외** (가중치 0 강제) |
| 역방향 필터 | acc 0.2796 상태에서 앙상블 반대 방향 판정 시 **정상 진입 차단** → 역효과 |
| CB③ acc30m | 구조적 acc 저하로 **오발동 위험** — 모델 완성도 문제지 전략 실패 아님 |

**30m 모델이 앙상블 점수에 기여하지 않으면서도 역방향 필터로 진입을 막는 구조적 문제.** opt_gex_bn(ρ=0.290)·opt_chain_pcr(ρ=0.245) 등 핵심 피처가 없는 상태에서 30m 방향 예측은 신뢰할 수 없음.

---

### 비활성화 내용 (2026-06-25 적용)

#### ① 30m 역방향 필터 비활성화
**파일:** `model/ensemble_decision.py` (Q3 블록)

변경 전:
```python
if _dir_30m != DIRECTION_FLAT and _dir_30m != direction:
    _30m_filter_blocked = True
    grade = "X"        # 진입 차단
    auto_entry = False
```

변경 후:
```python
# 비활성화 — 플래그 기록만 유지, grade 격하 없음
if _dir_30m != DIRECTION_FLAT and _dir_30m != direction:
    _30m_filter_blocked = True   # 대시보드 표시·재활성화 판단용
    logger.debug(...)            # WARN → DEBUG 다운그레이드
```

`_30m_filter_blocked` 플래그 및 cascade coherence 계산은 유지됨.

#### ② CB③ acc30m HALT 트리거 비활성화
**파일:** `safety/circuit_breaker.py` (`record_accuracy` 메서드)

변경 전:
```python
if acc < effective_min:
    self._cb3_warn_count += 1
    if self._cb3_warn_count >= 2:
        self._trigger_halt(...)    # 당일 시스템 정지
    else:
        logger.warning(...)        # 경고 + Slack 발송
```

변경 후:
```python
if acc < effective_min:
    logger.debug("[CB③ 비활성] acc30m=...% (30m 피처 미탑재 기간 중 발동 억제)")
    # HALT·경고·Slack 없음
```

유지되는 기능:
- `_accuracy_buf` 누적 (DriftRetrain 조건A/B 판단에 사용)
- P4 stage 추적 NORMAL/WATCH/RESTRICTED (정보성 대시보드 표시)
- warn_count 리셋 로직 (재활성화 즉시 동작 가능한 상태 보존)

---

### 재활성화 조건

다음 **두 조건 모두** 충족 시 두 블록의 주석 해제 후 EOD 재학습 확인.

| 조건 | 기준 | 예상 시점 |
|---|---|---|
| ① opt_gex_bn / opt_chain_pcr 행 수 | **각 4,000행 달성** | 2026-07-02 |
| ② 30m EOD CV acc | **≥ 0.33** (랜덤 이상) | 피처 탑재 후 첫 full_cv 재학습 |
| ③ shap_feature_registry 업데이트 | `active_features`에 opt 7개 추가 | ①과 동시 |

재활성화 순서:
1. `shap_feature_registry.json` + `horizon_feature_sets.json` 업데이트 (need_add → in_pkl)
2. EOD 재학습 실행 (full_cv=True) → 30m CV acc 확인
3. acc ≥ 0.33 확인 후 `ensemble_decision.py` Q3 블록 재활성화
4. `circuit_breaker.py` CB③ HALT 재활성화
5. 다음 장 로그에서 `[Ensemble] 30m 역방향 필터 작동` 정상 발동 확인

> 조건 ①만 달성하고 acc ≥ 0.33 미달 시 필터 비활성 유지. 역방향 필터가 acc < 0.33인 모델에 의존하면 정상 진입을 막는 역효과가 반복됨.

---

## 삭제 처리 내역

| 피처 | 삭제 사유 | 날짜 | 커밋 |
|---|---|---|---|
| `bear_reversal_signal` | 일평균 10봉/일, DB 0.2%, 4,000행 도달 390일 소요 | 2026-06-17 (191차) | `ff68ac1` |
| `bull_reversal_signal` | 145행 (0.2%) — bear 버전과 동일 사유 | 2026-06-23 (231차) | `d3281c9` |
| `bull_exhaustion_signal` | 2행 (0.0%) — 사실상 미수집 | 2026-06-23 (231차) | `d3281c9` |

---

## 참고: 피처 추가 후 확인 사항

1. `shap_feature_registry.json`의 `active_features`에 해당 피처 추가 (게이트 이슈 해소)
2. `horizon_feature_sets.json`에서 해당 피처 pkl 상태 `"need_add"` → `"in_pkl"` 전환
3. EOD 재학습 로그에서 `[FeatureReg] Xm: {feature} 제외` 소멸 확인
4. 추가된 호라이즌 재학습 acc 변화 모니터링 (단기 소폭 변동 예상)
5. `피처 슬라이싱: 97 → N개`에서 N이 예상대로 증가하는지 확인

---

## 전체 완료 예상 시점

| 시점 | 누적 활성화 | 완료 피처 | 비고 |
|---|---|---|---|
| ~~2026-06-20~~ **2026-06-23** | +2개 | threshold_feasibility, queue_directional_depletion | [DONE] |
| **2026-06-29** | +1개 추가 | micro_regime_code | |
| **2026-07-02** | +3개 추가 | opt_chain_pcr, opt_gex_bn, opt_gex_sign | 일괄 |
| **2026-07-02~09 예상** | +1개 추가 | cvd_monotone_ratio | 변동 심함 |
| **2026-07-03** | +3개 추가 | opt_pcr_extreme_bearish, opt_atm_call_oi, opt_atm_pcr | |
| **2026-07-07** | +1개 추가 | opt_atm_put_oi | |
| **2026-07-07** | **전체 11개 완료** | need_add 피처 전부 active 전환 | |
| **2026-07-14 이후** | — | Phase D 재검증 실행 | opt 4주 기준 달성 |

추가검토사항 7/1
P2	옵션체인 피처 확보 (opt_gex_bn 등 4종)	07-02 이후 4000행 달성	30m 피처 다양성 확보
P3	30m 피처 목록에 빠른-변화 피처 추가	피처 엔지니어링	ConstOut 자체 발생 빈도 감소


