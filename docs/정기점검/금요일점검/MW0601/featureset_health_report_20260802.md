# 호라이즌별 피처셋 주간 건강 리포트 — MW0601 · 2026-08-02

> 생성: `scripts/generate_featureset_health_report.py` (읽기 전용)  
> 근거: `docs/Spec for feature/피처셋_주기점검_자동리포트_구현계획_2026-08-02.md` Phase A  
> **이 리포트는 관측과 권고만 출력한다.** 피처셋 변경은 L3(purged CV) 배터리 → 주간회의 수동 승인 → EOD 재학습 경로로만 이뤄진다 (`CLAUDE.md` §6 자동 통합 금지).

- 건강도 관찰창: **2026-07-03 ~ 2026-07-31** (20거래일, 7,539행)
- 후보 축적 관찰창: 2026-05-06 ~ 2026-07-31 (60거래일)
- 배포 스펙 출처: `model/horizons/feature_names_{hz}.pkl` **직접 로드** — `horizon_feature_sets.json`(계획 문서)·`shap_feature_registry.json`(PC별 런타임 산출물)이 아니다
- 판정 기준: `scripts/feature_health_report.py` 단일 출처 (DEAD=분산0 / CRITICAL=zero·최빈 95%+ / WARN=80%+ / 미계측=표본<200)
- git: `f173a90`

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
| `basis_change_pt` | pending:1m, pending:3m, pending:5m, pending:10m | 13일 | OK | 📌 승격 보류 — basis_pt와 동일 검정에서 함께 재현 실패 |
| `basis_pt` | pending:1m, pending:3m, pending:5m, pending:10m | 13일 | OK | 📌 승격 보류 — 표본 확대 후 신호 소멸(재현 실패) |
| `cancel_ratio` | POOL | 0일 | raw부재 | 📌 구현불가 확정 — 데이터 원천 없음 (완전 사장) |
| `cvd_direction` | pending:10m | 60일 | OK | 📌 교체 완료 — cvd_delta_norm이 대체 (후보 목록의 잔존 항목) |
| `foreign_futures_net` | pending:10m | 60일 | OK | 검증가능 (60일) |
| `hurst_ready` | POOL | 25일 | WARN | 검증가능 (25일) |
| `imbalance_slope` | POOL | 60일 | OK | 검증가능 (60일) |
| `is_month_end_rebalance` | pending:1m, pending:3m, pending:5m, pending:10m, pending:15m, pending:30m | 19일 | OK | 축적중 19/20일 |
| `is_monthly_expiry_week` | pending:1m, pending:3m, pending:5m, pending:10m, pending:15m, pending:30m | 19일 | CRITICAL | 축적중 19/20일 |
| `is_monthly_witching` | pending:1m, pending:3m, pending:5m, pending:10m, pending:15m, pending:30m | 19일 | CRITICAL | 축적중 19/20일 |
| `is_weekly_witching` | pending:1m, pending:3m, pending:5m, pending:10m, pending:15m, pending:30m | 19일 | OK | 축적중 19/20일 |
| `kyle_lambda` | POOL | 13일 | OK | 축적중 13/20일 |
| `micro_regime_code` | POOL | 28일 | OK | 검증가능 (28일) · 📌 1m 편입만 하지 않음 — 타 호라이즌 후보 자격은 유지 |
| `microprice_slope` | POOL | 60일 | OK | 검증가능 (60일) |
| `mlofi_norm` | POOL | 60일 | OK | 검증가능 (60일) |
| `multi_timeframe_15m` | POOL | 13일 | OK | 축적중 13/20일 |
| `multi_timeframe_5m` | POOL | 13일 | OK | 축적중 13/20일 |
| `ofi_reversal_speed` | pending:1m | 60일 | OK | 검증가능 (60일) |
| `opt_atm_call_oi` | pending:15m | 13일 | OK | 축적중 13/20일 · 📌 강등(include → pending) — magnitude 계열 재현 실패 |
| `opt_atm_pcr` | POOL, pending:15m | 13일 | OK | 축적중 13/20일 |
| `opt_atm_put_oi` | pending:15m | 13일 | OK | 축적중 13/20일 · 📌 강등(include → pending) — magnitude 계열 재현 실패 |
| `opt_chain_pcr` | pending:15m | 13일 | OK | 축적중 13/20일 · 📌 ⚠ CORE — 15m 승격만 보류. 30m CORE 지위는 그대로 유지 |
| `opt_gex_bn` | pending:15m | 13일 | OK | 축적중 13/20일 · 📌 강등(include → pending) — magnitude 계열 재현 실패, sign 계열로 대체 |
| `opt_gex_sign` | POOL, pending:15m | 13일 | CRITICAL | 축적중 13/20일 |
| `program_arb_net` | pending:5m, pending:10m, pending:15m, pending:30m | 60일 | OK | 검증가능 (60일) |
| `program_non_arb_net` | pending:5m, pending:10m, pending:15m, pending:30m | 60일 | OK | 검증가능 (60일) |
| `queue_depletion_speed` | POOL | 60일 | OK | 검증가능 (60일) |
| `queue_directional_depletion` | POOL | 28일 | OK | 📌 1m 편입 종결 — 개선 대상 아님 (후보 재고에서 제외) |
| `queue_momentum` | POOL | 60일 | OK | 검증가능 (60일) |
| `queue_refill_rate` | POOL | 60일 | OK | 검증가능 (60일) |
| `queue_signal` | POOL | 60일 | OK | 검증가능 (60일) |
| `round_number_distance` | POOL | 13일 | OK | 축적중 13/20일 |
| `rv_iv_spread` | POOL | 12일 | OK | 축적중 12/20일 |
| `threshold_feasibility` | pending:15m | 28일 | OK | 📌 기각 — F4 재검증에서 부호 반전 (재현 실패) |
| `trend_efficiency` | POOL | 13일 | OK | 축적중 13/20일 |
| `vkospi` | pending:10m, pending:15m, pending:30m | 13일 | OK | 축적중 13/20일 |
| `vpin` | POOL | 13일 | OK | 축적중 13/20일 |

- **살아있는 재고**: 31건 (축적중+검증가능 — `⚠ 미배선`과 §5에서 `재고=제외`로 확정된 것은 뺀다)
- 재고 충분 — 발굴 세션 권고 없음 (트리거 기준 3건)

> `⚠ 미배선`은 명부에만 있고 계산 모듈이 없거나 배선이 끊겨 `raw_features`에 값이 전혀 쌓이지 않는 후보다 — 표준절차 Phase 1을 밟지 않은 상태이므로 검증 단계로 올라갈 수 없다 (예: `cancel_ratio`는 계좌등급 제한으로 **구현불가 확정**).  
> `검증가능`은 L1' 월간 스크리닝(`ic_probe_pending_features.py`) 표본 요건(20거래일)을 채웠다는 뜻일 뿐, 채택 근거가 아니다.

## 5. 확정 결정 레지스트리 (📌)

출처: `config/settings.py:FEATURE_SET_DECISIONS` (16건)

| 피처 | 결정 | 일자 | 재고 | 재검토 |
|---|---|---|---|---|
| `basis_change_pt` | 승격 보류 — basis_pt와 동일 검정에서 함께 재현 실패 | 2026-07-26 | 제외 | basis_pt와 동시에만 재론. |
| `basis_pt` | 승격 보류 — 표본 확대 후 신호 소멸(재현 실패) | 2026-07-26 | 제외 | 표본이 386차 시점(2,953행)의 4배 이상으로 늘고 다른 근거가 새로 생겼을 때만 1회 재검정. 그 전에는 재론 금지. |
| `bear_exhaustion` | 조건부채택(섀도 유지) — 라이브 소비 미개방 | 2026-07-27 | 유지 | 섀도 20거래일 이상 관측 후 ⓐⓑⓒ 전부 충족 시 live 전환 재론. |
| `bear_exhaustion_signal` | 조건부채택(섀도 유지) — 라이브 소비 미개방 | 2026-07-27 | 유지 | bear_exhaustion과 동시 판단. |
| `bull_exhaustion` | 조건부채택(섀도 유지) — 라이브 소비 미개방 | 2026-07-27 | 유지 | 섀도 20거래일 이상 관측 후 ⓐⓑⓒ 전부 충족 시 live 전환 재론. |
| `bull_exhaustion_signal` | 조건부채택(섀도 유지) — 라이브 소비 미개방 | 2026-07-27 | 유지 | bull_exhaustion과 동시 판단. |
| `cancel_ratio` | 구현불가 확정 — 데이터 원천 없음 (완전 사장) | 2026-07-14 | 제외 | 재검정 금지 |
| `cvd_direction` | 교체 완료 — cvd_delta_norm이 대체 (후보 목록의 잔존 항목) | 2026-06-25 | 제외 | Cybos buy_vol 편향 자체가 해소되면(원천 데이터 변경) 재론 가능. |
| `micro_regime_code` | 1m 편입만 하지 않음 — 타 호라이즌 후보 자격은 유지 | 2026-08-02 | 유지 | 월간 L1' 스크리닝에서 3m 이상 호라이즌 IC를 계속 관찰. 1m 편입만 재론 금지. |
| `opt_atm_call_oi` | 강등(include → pending) — magnitude 계열 재현 실패 | 2026-07-14 | 유지 | opt_gex_bn과 동시 관찰. |
| `opt_atm_put_oi` | 강등(include → pending) — magnitude 계열 재현 실패 | 2026-07-14 | 유지 | opt_gex_bn과 동시 관찰. |
| `opt_chain_pcr` | ⚠ CORE — 15m 승격만 보류. 30m CORE 지위는 그대로 유지 | 2026-07-14 | 유지 | 15m 승격은 월간 L1'에서 IC가 회복될 때 재론. |
| `opt_gex_bn` | 강등(include → pending) — magnitude 계열 재현 실패, sign 계열로 대체 | 2026-07-14 | 유지 | 월간 L1' 스크리닝에서 magnitude 계열 IC가 회복되는지 계속 관찰. |
| `queue_directional_depletion` | 1m 편입 종결 — 개선 대상 아님 (후보 재고에서 제외) | 2026-08-02 | 제외 | 1m이 앙상블 가중치를 되찾는 경우에만 재론(현재 계획 없음). |
| `threshold_feasibility` | 기각 — F4 재검증에서 부호 반전 (재현 실패) | 2026-07-26 | 제외 | 재검정 금지 |
| `vwap_position` | ⚠ CORE 유지 — 단, 단독 신호로는 비용차감 후 손실 확정 | 2026-07-27 | 유지 | 해당 없음 — CORE 지위 변경은 사용자 승인 사안이라 이 레지스트리에서 재론하지 않는다(정보성 기록). |

- **`basis_change_pt`** — IC -0.0119~+0.0001 (p 0.51~1.00)으로 전 호라이즌 비유의. basis_pt보다 오히려 더 확실하게 0에 붙어 있다. 재론 조건은 basis_pt와 동일.  
  근거: dev_memory/DECISION_LOG.md 2026-07-26(386차) §3
- **`basis_pt`** — 07-13 보고서가 1m/3m/15m IC +0.048~+0.099(전부 명목 유의, 호라이즌 단조 증가)로 유망 후보라 판단했으나, 그 표본은 07-14 **하루치**(커버리지 17.3%)였다. 07-14~07-24로 2,953행(약 8거래일)까지 확대해 재검증하자 전 호라이즌 비유의(p 0.11~0.94)로 소멸했다. 386차 결론: '추가 축적으로도 신호가 나타날 근거 약함(방향 전환 없이 계속 0에 수렴 중)'. ⚠ 원문 표현은 **'승격 보류'**이지 '기각'이 아니다 — 표준절차 Phase 6의 기각(반증) 요건은 충족하나 그렇게 종결 선언된 적은 없으므로 그대로 옮긴다.  
  근거: dev_memory/DECISION_LOG.md 2026-07-26(386차) §3, featureset by horizon/horizon_feature_sets.json _meta
- **`bear_exhaustion`, `bull_exhaustion`** — 394차 계측결함 교정 완료 후에도 `EXHAUSTION_RESTORE_MODE='shadow'`로 유지 중 — 라이브 소비를 열지 않고 값만 기록한다(표준절차 Phase 6 '조건부채택(섀도 유지)'의 대표 사례). live 전환 조건이 이미 사전등록돼 있다: ⓐ 발화 시점 사후수익률이 기대방향 기준 일자단위로 유의하게 양(+) ⓑ 교정값 포함 EOD 재학습 1회 이상 완료 ⓒ 탈진 레짐 발생률 확인(RegimeChampGate가 그 구간 진입을 막으므로 챔피언 승격 여부를 함께 결정). 현재 미충족 사유는 알파 미검증 — 교정 후 발화 시점 사후 10분 수익률 평균 −1.72pt(n=89, t=−1.35)로 음도 양도 아니다. 별칭 `cvd_exhaustion`·`cvd_exhaustion_signal`도 같은 결정에 묶인다.  
  근거: config/settings.py EXHAUSTION_RESTORE_MODE 주석, docs/미륵이고도화2/Phase1_소진복구_2026-07-27.md
- **`bear_exhaustion_signal`, `bull_exhaustion_signal`** — 394차 계측결함 교정 완료 후에도 `EXHAUSTION_RESTORE_MODE='shadow'`로 유지 중 — 라이브 소비를 열지 않고 값만 기록한다(표준절차 Phase 6 '조건부채택(섀도 유지)'의 대표 사례). live 전환 조건이 이미 사전등록돼 있다: ⓐ 발화 시점 사후수익률이 기대방향 기준 일자단위로 유의하게 양(+) ⓑ 교정값 포함 EOD 재학습 1회 이상 완료 ⓒ 탈진 레짐 발생률 확인(RegimeChampGate가 그 구간 진입을 막으므로 챔피언 승격 여부를 함께 결정). 현재 미충족 사유는 알파 미검증 — 교정 후 발화 시점 사후 10분 수익률 평균 −1.72pt(n=89, t=−1.35)로 음도 양도 아니다. 별칭 `cvd_exhaustion`·`cvd_exhaustion_signal`도 같은 결정에 묶인다.  
  근거: config/settings.py EXHAUSTION_RESTORE_MODE 주석
- **`cancel_ratio`** — Cybos Plus 취소/정정 TR(CpTd6832/6833 등)은 전부 '내 계좌' 전용이라 **시장 전체 취소 이벤트라는 데이터 자체가 없다**(Level-3 주문흐름 미제공). 대안으로 검토한 Dscbo1.FutOptRest는 2026-07-14 실계정 BlockRequest 실측에서 '고객님의 계좌등급으로는 FutOptRest 시세데이터를 받는 데 제한이 있습니다' (파라미터 무관 항상 발생)로 조회 자체가 불가. 표준절차 Phase 1의 '이론상 가능 ≠ 실측 가능' 대표 사례 — 계좌등급이 바뀌지 않는 한 재론 불가.  
  근거: config/constants.py DYNAMIC_FEATURES_POOL 주석, docs/미륵이고도화2/cancel_ratio_Cybos_데이터가용성_재조사_2026-07-14.md
- **`cvd_direction`** — Cybos buy_vol의 시스템 편향(buy>sell 98.6%)으로 10일 이상 +0.5에 고착해 **상수 피처로 전락**했고, 2026-06-25 project-wide로 CORE에서 cvd_delta_norm(price-action 기반, 편향 없음)으로 교체됐다. 1m·3m feature_names pkl에 cvd_delta_norm만 있고 cvd_direction은 없음을 386차가 직접 로드로 확인했다. 10m `include_pending_validation`에 남아 있는 항목은 395차가 '교체 이후에도 후보 목록에 남아있던 **폐기 대상 잔존 항목**'으로 판정하고 '항목 자체 제거 검토 권고'를 메모해 둔 것이다 — json 편집은 사용자 승인 사안이라 그때 삭제하지 않았다. 여기 등록은 그 판정의 기록이며, **json에서 실제로 지우는 것은 여전히 사용자 승인이 필요하다.**  
  근거: dev_memory/DECISION_LOG.md 2026-07-27(395차) §2, config/settings.py CORE_FEATURES_BY_GROUP 주석(2026-06-25)
- **`micro_regime_code`** — 위 `queue_directional_depletion`과 같은 1m 갭이지만 **결정을 달리한다.** 1m 편입을 하지 않는 이유는 동일하다(1m 영구 퇴역). 그러나 이 피처는 직전 1분 미시 레짐 코드(0=횡보 1=혼합 2=추세 3=탈진 4=급변, features/feature_builder.py:624)로 **1분 lag를 허용하는 레짐 변수**여서 초단기 전용 신호가 아니고, 실제로 10m·30m include 명세에도 같은 이름이 올라 있다(셋 다 미배포). 타 호라이즌 유효성은 검증된 적이 없으므로 `suppress=False`로 두어 **월간 L1' 스크리닝이 계속 평가**하게 한다. 1m 하나 때문에 전 호라이즌 후보 자격까지 닫는 것은 과잉이다.  
  근거: docs/미륵이고도화3/호라이즌_방향예측_개선_실행계획_2026-07-30.md 항목 F, featureset by horizon/horizon_feature_sets.json(1m·10m·30m include), features/feature_builder.py:624
- **`opt_atm_call_oi`, `opt_atm_put_oi`** — opt_gex_bn과 동일 F4 판정. 비율 계열 opt_atm_pcr이 대체 후보로 승격됐다.  
  근거: docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md F4
- **`opt_chain_pcr`** — **이 항목을 '기각'으로 읽지 말 것.** opt_chain_pcr은 CLAUDE.md 절대원칙 §3의 장기(30m) 그룹 CORE 피처이고 체크리스트 게이트로 소비된다. 보류 대상은 '15m 모델 입력으로 승격하는 것'뿐이며, 그 근거는 설계 rho=0.184 → 최신구간 IC=0.002 재현 실패다. CORE 교체는 사용자 승인 사안이라 이 레지스트리의 권한 밖이다.  
  근거: CLAUDE.md 절대원칙 §3, docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md F4
- **`opt_gex_bn`** — 설계 rho=0.198 → 최신구간 실측 IC=0.013으로 재현 실패. 다만 **개념 전체가 죽은 게 아니다** — 같은 F4 재실측에서 sign/ratio 계열(opt_gex_sign IC=0.035 p=0.006, opt_atm_pcr IC=0.051 p<1e-4)은 부분 생존했고, '재현될 때까지 sign/ratio 계열로 대체' 원칙에 따라 그 둘만 POOL로 승격했다. 표준절차 Phase 4-4(표현형 다양성)의 실례이므로 재고에 남긴다.  
  근거: config/constants.py DYNAMIC_FEATURES_POOL 주석(331차), docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md F4
- **`queue_directional_depletion`** — 07-30 실행계획 항목 F의 '명시적 제외' 권고를 사용자가 확정한 건이다. 근거 셋: ① **1m은 331차 후속2로 영구 퇴역**한 호라이즌이라 `ENSEMBLE_WEIGHTS['1m']=0.0` — 방향투표에 한 표도 넣지 않으므로 그 피처셋을 고쳐도 거래 결과가 바뀌지 않는다(퇴역 근거는 conf-층화 검정 방향적중률 47.75%, z=-2.82). ② **타 호라이즌 승격 여지가 없다** — `features/feature_decay.py`의 감쇠곡선이 (1.0, 0.8, 0.5, 0.1, 0.0, 0.0)로 1m에서 최대, 10m 이후 0으로 사전 정의돼 있다(호가 큐 방향별 고갈 강도라 성격상 초단기 전용). ③ **실제 배포된 적은 2026-06-29~30 이틀뿐**이고 그마저 `active_features`가 일시적으로 121개였던 기간의 부수효과였다(413차 로그 분해). 덧붙여 현재는 `active_features`(97)에 없어 batch_retrainer의 `get_available_feature_set()` 교집합에서 탈락하므로, json 명세만으로는 **구조적으로 편입 자체가 불가능**한 상태다. ⚠ 412차가 근거로 적었던 '395차의 07-27 배포 확인 + SHAP 0.0069'은 413차 로그·DB 분해에서 **사실이 아님이 확정**됐다(아래 source의 413차 항목).  
  근거: docs/미륵이고도화3/호라이즌_방향예측_개선_실행계획_2026-07-30.md 항목 F, config/settings.py ENSEMBLE_WEIGHTS(331차 후속2), features/feature_decay.py, dev_memory/DECISION_LOG.md 395차
- **`threshold_feasibility`** — 설계 시점 rho=+0.086이 최신 구간 재실측에서 IC=-0.024로 **부호가 뒤집혔다**. 386차가 1m 레지스트리 갭 2종을 DYNAMIC_FEATURES_POOL에 등록할 때 이 피처는 'F4 재현실패 케이스라 등록하지 않음(opt_gex_bn류와 동일 취급, 331차 선례 그대로)'으로 **명시적으로 제외**했다. 15m include_pending_validation에 남아 있는 것은 강등 시점의 잔존 표기다.  
  근거: dev_memory/DECISION_LOG.md 2026-07-26(386차) §2
- **`vwap_position`** — **제거 결정이 아니다.** 단·중기 CORE(CLAUDE.md §3)이자 미통과 시 강제 X등급인 게이트이며 현행 배포 피처셋에도 들어 있다. 기록하는 이유는 반대 방향의 오독을 막기 위해서다 — IC가 압도적(t=-14.7)이라 나중에 누군가 '이걸 단독 방향신호로 쓰자'고 재발굴할 여지가 크지만, 394차 거래성 검정에서 왕복비용 차감 후 **양방향 모두 손실**로 확정됐다. 게이트로 쓸 때도 ±2.0 클리핑에 51.6%가 몰려 해상도가 낮다는 별도 한계가 있다.  
  근거: docs/Spec for feature/피처_발굴_표준절차.md Phase 4-3(394차 거래성 하네스)

> `재고=제외`(suppress)만 §4 살아있는 재고에서 빠진다. `유지`는 마커만 붙고 재고에 그대로 남는다 — 보류·조건부채택처럼 **진행 중인 상태**를 재고에서 빼면 추적이 끊기기 때문이다.  
> **판정(매주 재계산)과 결정(사람이 확정)은 별개다** — 리포트가 같은 수치를 다시 찍는 것은 미조치가 아니다(`CLAUDE.md` 검증 캠페인 운영 모드).

---

> 다음 단계: 이 리포트는 L0(건강)·L4(신뢰도) 관측이다. KEEP/DROP/ADD 제안은 월간 리포트(구현계획 Phase C, L1·L2 필요)가 낸다. 어느 쪽도 피처셋을 바꾸지 않는다 — 변경은 L3 purged CV 통과 + 주간회의 승인 + EOD 재학습 반영 후 **pkl 직접 로드로 확인**하는 경로뿐이다.