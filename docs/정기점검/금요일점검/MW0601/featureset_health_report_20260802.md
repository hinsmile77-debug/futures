# 호라이즌별 피처셋 주간 건강 리포트 — MW0601 · 2026-08-02

> 생성: `scripts/generate_featureset_health_report.py` (읽기 전용)  
> 근거: `docs/Spec for feature/피처셋_주기점검_자동리포트_구현계획_2026-08-02.md` Phase A  
> **이 리포트는 관측과 권고만 출력한다.** 피처셋 변경은 L3(purged CV) 배터리 → 주간회의 수동 승인 → EOD 재학습 경로로만 이뤄진다 (`CLAUDE.md` §6 자동 통합 금지).

- 건강도 관찰창: **2026-07-03 ~ 2026-07-31** (20거래일, 7,539행)
- 후보 축적 관찰창: 2026-05-06 ~ 2026-07-31 (60거래일)
- 배포 스펙 출처: `model/horizons/feature_names_{hz}.pkl` **직접 로드** — `horizon_feature_sets.json`(계획 문서)·`shap_feature_registry.json`(PC별 런타임 산출물)이 아니다
- 판정 기준: `scripts/feature_health_report.py` 단일 출처 (DEAD=분산0 / CRITICAL=zero·최빈 95%+ / WARN=80%+ / 미계측=표본<200)
- git: `ef3ee59`

## 1. 호라이즌별 요약

| 호라이즌 | 앙상블 | 배포 피처 | OK | WARN | CRITICAL | DEAD | 미계측 | raw부재 | **실이상** | CORE |
|---|---|---|---|---|---|---|---|---|---|---|
| 1m | 퇴역 | 8 | 7 | 1 | 0 | 0 | 0 | 0 | **0** | OK |
| 3m | 0.13 | 12 | 12 | 0 | 0 | 0 | 0 | 0 | **0** | OK |
| 5m | 0.30 | 12 | 10 | 1 | 1 | 0 | 0 | 0 | **0** | OK |
| 10m | 0.29 | 11 | 10 | 1 | 0 | 0 | 0 | 0 | **0** | OK |
| 15m | 0.28 | 13 | 12 | 0 | 1 | 0 | 0 | 0 | **0** | OK |
| 30m | 퇴역 | 11 | 11 | 0 | 0 | 0 | 0 | 0 | **0** | OK |

> **`실이상`만 보면 된다** — DEAD·CRITICAL·raw부재 중 원인 미규명이고 상태플래그도 아닌 것의 수. `is_*`/`quality_*`처럼 "항상 같은 값이 정상"인 플래그는 CRITICAL/WARN 열에 잡혀도 실이상이 아니다(경보 피로 방지 — `feature_health_report.py`의 '신규 이상'과 같은 정의).  
> `앙상블=퇴역`은 `ENSEMBLE_WEIGHTS`가 0.0인 호라이즌(1m 331차 후속2, 30m 296차) — 방향투표에 쓰이지 않으므로 개선 대상이 아니다.  
> `raw부재` = 모델 입력인데 `raw_features`에 기록이 없는 피처. 0이 아니면 계측 자체가 그 피처를 못 보고 있다는 뜻이라 우선 조사 대상이다.  
> `CORE`는 체크리스트 게이트(`CLAUDE.md` §3)라 모델 입력이 아닐 수 있다 — pkl 미포함은 이상이 아니므로 건강도만 본다.

## 2. 호라이즌별 상세 (정상 아닌 것만)

### 1m — 배포 8개 (pkl 2026-07-31 14:05)

| 등급 | 피처 | n | zero% | 최빈비중 | 고유값 | 비고 |
|---|---|---|---|---|---|---|
| WARN | `is_open_volatile` | 7539 | 88.3% | 88.3% | 2 | 상태플래그(상수 정상) |

CORE(short): `cvd_delta_norm`=OK / `vwap_position`=OK / `ofi_pressure`=OK

### 3m — 배포 12개 (pkl 2026-07-31 14:05)

전 피처 OK.

CORE(short): `cvd_delta_norm`=OK / `vwap_position`=OK / `ofi_pressure`=OK

### 5m — 배포 12개 (pkl 2026-07-31 14:05)

| 등급 | 피처 | n | zero% | 최빈비중 | 고유값 | 비고 |
|---|---|---|---|---|---|---|
| CRITICAL | `is_close_volatile` | 7539 | 97.8% | 97.8% | 2 | 상태플래그(상수 정상) |
| WARN | `is_open_volatile` | 7539 | 88.3% | 88.3% | 2 | 상태플래그(상수 정상) |

CORE(short): `cvd_delta_norm`=OK / `vwap_position`=OK / `ofi_pressure`=OK

### 10m — 배포 11개 (pkl 2026-07-31 14:05)

| 등급 | 피처 | n | zero% | 최빈비중 | 고유값 | 비고 |
|---|---|---|---|---|---|---|
| WARN | `opt_pcr_extreme` | 7268 | 84.6% | 84.6% | 2 |  |

CORE(mid): `vwap_position`=OK

### 15m — 배포 13개 (pkl 2026-07-31 14:05)

| 등급 | 피처 | n | zero% | 최빈비중 | 고유값 | 비고 |
|---|---|---|---|---|---|---|
| CRITICAL | `is_close_volatile` | 7539 | 97.8% | 97.8% | 2 | 상태플래그(상수 정상) |

CORE(mid): `vwap_position`=OK

### 30m — 배포 11개 (pkl 2026-07-31 14:05)

전 피처 OK.

CORE(long): `above_vwap`=OK / `opt_chain_pcr`=OK

**배포 피처 신규 이상(원인 미규명·상태플래그 제외)**: 없음

### 2-b. 전체 `raw_features` 신규 이상 (배포·후보 밖 포함)

| 등급 | 피처 | zero% | 최빈비중 | 소재 |
|---|---|---|---|---|
| DEAD | `bear_exhaustion_shadow` | 100.0% | 100.0% | 계측만 (배포·후보 아님) |
| DEAD | `bear_reversal_signal` | 100.0% | 100.0% | 계측만 (배포·후보 아님) |
| CRITICAL | `bull_exhaustion_shadow` | 99.2% | 99.2% | 계측만 (배포·후보 아님) |
| CRITICAL | `bull_reversal_signal` | 98.9% | 98.9% | 계측만 (배포·후보 아님) |
| DEAD | `feature_recoverable_errors` | 100.0% | 100.0% | 계측만 (배포·후보 아님) |
| DEAD | `macro_vix_abs` | 100.0% | 100.0% | 계측만 (배포·후보 아님) |
| DEAD | `microprice` | 100.0% | 100.0% | 계측만 (배포·후보 아님) |
| CRITICAL | `opt_gex_sign` | 0.7% | 96.7% | 후보: POOL, pending:15m |

> `계측만`인 피처가 죽어 있어도 지금 당장 모델을 해치지는 않는다. 다만 **나중에 후보로 승격시킬 때 이미 죽어 있는 상태**라 표준절차 Phase 2에서 반드시 걸린다 — 그때 고치는 것보다 지금 아는 편이 싸다.

## 3. L4 — confidence 층화 검정 요약

⚠ **미배선** — `data/horizon_conf_stratified_latest.json`가 없다. 이 절은 `scripts/horizon_conf_stratified_test.py`(07-30 실행계획 1단계 신설 대상)가 그 경로에 JSON을 쓰면 자동으로 채워진다. **빈칸이 '이상 없음'을 뜻하지 않는다.**

## 4. 후보 파이프라인 현황판

| 후보 | 출처 | 축적(최근 60거래일) | 건강 | 상태 |
|---|---|---|---|---|
| `basis_change_pt` | pending:1m, pending:3m, pending:5m, pending:10m | 13일 | OK | 축적중 13/20일 |
| `basis_pt` | pending:1m, pending:3m, pending:5m, pending:10m | 13일 | OK | 축적중 13/20일 |
| `cancel_ratio` | POOL | 0일 | raw부재 | ⚠ 미배선(축적 0) |
| `cvd_direction` | pending:10m | 60일 | OK | 검증가능 (60일) |
| `foreign_futures_net` | pending:10m | 60일 | OK | 검증가능 (60일) |
| `hurst_ready` | POOL | 25일 | WARN | 검증가능 (25일) |
| `imbalance_slope` | POOL | 60일 | OK | 검증가능 (60일) |
| `is_month_end_rebalance` | pending:1m, pending:3m, pending:5m, pending:10m, pending:15m, pending:30m | 19일 | OK | 축적중 19/20일 |
| `is_monthly_expiry_week` | pending:1m, pending:3m, pending:5m, pending:10m, pending:15m, pending:30m | 19일 | CRITICAL | 축적중 19/20일 |
| `is_monthly_witching` | pending:1m, pending:3m, pending:5m, pending:10m, pending:15m, pending:30m | 19일 | CRITICAL | 축적중 19/20일 |
| `is_weekly_witching` | pending:1m, pending:3m, pending:5m, pending:10m, pending:15m, pending:30m | 19일 | OK | 축적중 19/20일 |
| `kyle_lambda` | POOL | 13일 | OK | 축적중 13/20일 |
| `micro_regime_code` | POOL | 28일 | OK | 검증가능 (28일) |
| `microprice_slope` | POOL | 60일 | OK | 검증가능 (60일) |
| `mlofi_norm` | POOL | 60일 | OK | 검증가능 (60일) |
| `multi_timeframe_15m` | POOL | 13일 | OK | 축적중 13/20일 |
| `multi_timeframe_5m` | POOL | 13일 | OK | 축적중 13/20일 |
| `ofi_reversal_speed` | pending:1m | 60일 | OK | 검증가능 (60일) |
| `opt_atm_call_oi` | pending:15m | 13일 | OK | 축적중 13/20일 |
| `opt_atm_pcr` | POOL, pending:15m | 13일 | OK | 축적중 13/20일 |
| `opt_atm_put_oi` | pending:15m | 13일 | OK | 축적중 13/20일 |
| `opt_chain_pcr` | pending:15m | 13일 | OK | 축적중 13/20일 |
| `opt_gex_bn` | pending:15m | 13일 | OK | 축적중 13/20일 |
| `opt_gex_sign` | POOL, pending:15m | 13일 | CRITICAL | 축적중 13/20일 |
| `program_arb_net` | pending:5m, pending:10m, pending:15m, pending:30m | 60일 | OK | 검증가능 (60일) |
| `program_non_arb_net` | pending:5m, pending:10m, pending:15m, pending:30m | 60일 | OK | 검증가능 (60일) |
| `queue_depletion_speed` | POOL | 60일 | OK | 검증가능 (60일) |
| `queue_directional_depletion` | POOL | 28일 | OK | 검증가능 (28일) |
| `queue_momentum` | POOL | 60일 | OK | 검증가능 (60일) |
| `queue_refill_rate` | POOL | 60일 | OK | 검증가능 (60일) |
| `queue_signal` | POOL | 60일 | OK | 검증가능 (60일) |
| `round_number_distance` | POOL | 13일 | OK | 축적중 13/20일 |
| `rv_iv_spread` | POOL | 12일 | OK | 축적중 12/20일 |
| `threshold_feasibility` | pending:15m | 28일 | OK | 검증가능 (28일) |
| `trend_efficiency` | POOL | 13일 | OK | 축적중 13/20일 |
| `vkospi` | pending:10m, pending:15m, pending:30m | 13일 | OK | 축적중 13/20일 |
| `vpin` | POOL | 13일 | OK | 축적중 13/20일 |

- **살아있는 재고**: 36건 (축적중+검증가능 — `미배선`·`📌결정됨` 제외)
- 재고 충분 — 발굴 세션 권고 없음 (트리거 기준 3건)

> `⚠ 미배선`은 명부에만 있고 계산 모듈이 없거나 배선이 끊겨 `raw_features`에 값이 전혀 쌓이지 않는 후보다 — 표준절차 Phase 1을 밟지 않은 상태이므로 검증 단계로 올라갈 수 없다 (예: `cancel_ratio`는 계좌등급 제한으로 **구현불가 확정**).  
> `검증가능`은 L1' 월간 스크리닝(`ic_probe_pending_features.py`) 표본 요건(20거래일)을 채웠다는 뜻일 뿐, 채택 근거가 아니다.

## 5. 확정 결정 레지스트리 (📌)

(등록된 확정 결정 없음 — `config/settings.py:FEATURE_SET_DECISIONS`)

## ⚠ 생성 경고

- `config/settings.py:FEATURE_SET_DECISIONS` 미정의 — 구현계획 Phase B 미구현 상태다. §5가 비어 있는 것은 '결정이 없다'가 아니라 '레지스트리가 아직 없다'는 뜻이므로, 기각 피처가 §4에 후보로 다시 뜰 수 있다.

---

> 다음 단계: 이 리포트는 L0(건강)·L4(신뢰도) 관측이다. KEEP/DROP/ADD 제안은 월간 리포트(구현계획 Phase C, L1·L2 필요)가 낸다. 어느 쪽도 피처셋을 바꾸지 않는다 — 변경은 L3 purged CV 통과 + 주간회의 승인 + EOD 재학습 반영 후 **pkl 직접 로드로 확인**하는 경로뿐이다.