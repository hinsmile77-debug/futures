# 미륵이 (futures) 현재 개발 상태

> 마지막 업데이트: 2026-05-22 (86차) — **P0 구현 + EOD 스케일러 초기화**
> 이 파일이 가장 먼저 읽혀야 한다.

---

## 2026-05-22 (86차) — 5/22 진입 0 P0 구현 + EOD 스케일러 초기화

### 배경

Deep·Codex 5/22 진입 0 원인 분석 리뷰 기반 P0 5종 구현. signal() TypeError 재발 차단, SHS/EKS 시스템 건강 감시, Warm Scaler Canary, CORE 진단 로그. EOD 스케일러 초기화 3종 추가 수정.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **SHS + EKS**: `safety/system_health.py` 신규 | **완료** |
| **SHS Slack 알림**: `notify_shs_alert()`, `notify_kill_switch()` | **완료** — utils/notify.py |
| **SHS UI 배지**: `lbl_shs` 상단 헤더 + `update_shs_badge()` | **완료** — dashboard/main_dashboard.py |
| **Warm Scaler Canary**: `canary_stale_age_hours()`, `canary_z_warn_count()` | **완료** — model/multi_horizon_model.py |
| **`_load_all()` mtime 동기화**: `_scaler_fitted_at[h]` = pkl mtime | **완료** — model/multi_horizon_model.py |
| **main.py Canary·SHS·EKS 연동**: 08:55 검사·GAP_OPEN·EKS 판정 | **완료** — main.py |
| **log_manager `**_kwargs`**: signal/system/trade TypeError 방어 | **완료** — logging_system/log_manager.py |
| **CORE 진단 로그**: VWAP/CVD/OFI raw값 탈락 시 출력 | **완료** — strategy/entry/checklist.py |
| **EOD `_load_all()` 무조건 호출**: retrain 실패에도 최신 pkl 적용 | **완료** — main.py daily_close() |
| **`system_health.reset_daily()`**: EKS·GAP_OPEN 일일 초기화 | **완료** — safety/system_health.py + main.py |
| **재시작 방지 락**: BrokerSync→connect_broker() 재호출 차단 | **❌ 미구현** — 잔여 P0 최우선 |
| **Scaler Auto Re-fit**: 기동 시 최근 5일 데이터로 scaler 재학습 | **❌ 미구현** — Canary 감지만 |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 |

### 수정 파일 (86차)

| 파일 | 변경 내용 |
|---|---|
| `safety/system_health.py` | **신규** — SHS 계산 + EKS 상태 머신 + `reset_daily()` |
| `utils/notify.py` | `notify_shs_alert()`, `notify_kill_switch()` 추가 |
| `dashboard/main_dashboard.py` | `lbl_shs` 배지 + `update_shs_badge()` |
| `model/multi_horizon_model.py` | Canary 2메서드 + `_load_all()` mtime 동기화 |
| `logging_system/log_manager.py` | signal/system/trade `**_kwargs` 방어 가드 |
| `strategy/entry/checklist.py` | CORE 탈락 raw값 진단 로그 |
| `main.py` | Canary·SHS·EKS 연동 + EOD `_load_all()` + `system_health.reset_daily()` |

### 86차 실세션 확인 사항 (2026-05-23)

1. **SHS 배지**: 상단 헤더 `♥ SHS 100` (정상) 또는 `⚠ SHS N` (경고) 표시
2. **Canary**: `[Canary] scaler 노후=Xh z경고피처=N개` 로그 (08:55)
3. **EKS 판정**: `[SHS-EKS] EKS 미발동. conf_max=XX.X% core_pass=N/5봉` 로그 (09:05 직후)
4. **CORE 진단**: `[Checklist] CORE 피처 ✗ ... | VWAP pos=±X.XXX need >0` 형식 확인
5. **EOD**: 15:40 `daily_close()` 후 `[Model] X 로드 성공` 6개 호라이즌 재로드 확인

---

## 2026-05-22 (85차) — 모의투자 세션 이상점 7·8 deep dive + 구조적 수정 4종

### 배경

14:53~15:09 모의투자 세션 로그에서 이상점 7·8 발견. 1m/5m FL 편향 87%/100%(이상점 7), 10m conf 50~55% 과도 압축(이상점 8)을 deep dive 분석 후 5개 파일에 걸쳐 수정 4종 구현. 커밋 `67f974e`.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **이상점 7-A**: `_CW_1M={FL:0.60}`, `_CW_5M={FL:0.58}` 명시적 FL 완화 | **완료** — multi_horizon_model.py, batch_retrainer.py |
| **이상점 7-D**: CLOSE_VOLATILE 단기(1m/3m/5m) 0.6× 가중치 축소 + time_zone 파라미터 | **완료** — ensemble_decision.py, main.py |
| **이상점 8-B**: `WINDOW=200`(500→), 재보정 주기 `%20`(50→) | **완료** — calibration.py |
| **이상점 8-C**: 10m/15m Platt 하한 `raw_conf×0.85` | **완료** — main.py `_apply_horizon_calibration()` |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 확인 필요 |

### 수정 파일 (85차)

| 파일 | 변경 내용 |
|---|---|
| `model/multi_horizon_model.py` | `_CW_1M={FL:0.60, UP:1.20, DN:1.20}`, `_CW_5M={FL:0.58, UP:1.21, DN:1.21}` 추가 |
| `learning/batch_retrainer.py` | `_CW_1M`, `_CW_5M` 동일하게 추가 (학습기 일관성) |
| `learning/calibration.py` | `WINDOW=200`, 재보정 `% 20` |
| `model/ensemble_decision.py` | `time_zone` 파라미터 추가, CLOSE_VOLATILE 단기 0.6× 재정규화 |
| `main.py` | 10m/15m Platt 하한, `ensemble.compute()` `time_zone` 전달 |

### 85차 실세션 확인 사항 (2026-05-23)

1. **이상점 7 개선**: 1m/5m FL 비율 감소 확인 — `[Bias]` 로그에서 FL 편향 75% 미만 달성 여부
2. **이상점 7-D**: `[Ensemble] CLOSE_VOLATILE 단기 0.6×` 로그 14:00~15:00 구간 발생 확인
3. **이상점 8-B**: 다음 GBM 재학습 후 Platt 200건 윈도우로 현재 구간 반영 속도 향상
4. **이상점 8-C**: 10m conf가 `raw_conf × 0.85` 이하로 압축되지 않는지 확인 — 로그 `[Calib] 10m Platt 하한` 발화 빈도

---

## 2026-05-22 (84차) — 모의투자 세션 이상점 3~6 deep dive + 구조적 수정 4종

### 배경

12:11~12:48 모의투자 세션 로그에서 이상점 3~6을 발견. 30m 예측 7연속 실패(이상점 3), 50분 정확도 급락(이상점 4), Bias 통계 의미 없음(이상점 5), conf 전체 구간 60% 미달(이상점 6)을 deep dive 분석 후 5개 파일에 걸쳐 수정 구현.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **이상점 3**: `_CW_30M = {FL:0.65, UP:1.18, DN:1.18}` FL 다운웨이팅 완화 | **완료** — multi_horizon_model.py, batch_retrainer.py |
| **이상점 4**: `ACCURACY_WINDOW=150`, `_ADJUST_EVERY=3` 분봉 단위 조정 | **완료** — online_learner.py |
| **이상점 5**: 30건 롤링 Bias 버퍼, UP/DN/FL 추적, 15건+ 시 75% 편향 감지 | **완료** — main.py |
| **이상점 6-A**: SGD 초기(< 30건) GBM 전용 모드 `w_gbm=0.95` | **완료** — online_learner.py |
| **이상점 6-B**: 앙상블 전용 `PredictionCalibrator` 분리. 1m 검증으로 학습 | **완료** — ensemble_decision.py, main.py |
| **이상점 6-C**: 6호라이즌 ≤2 합의 시 conf×0.92 패널티 (보너스 미포함) | **완료** — ensemble_decision.py |
| **이상점 6-D**: `ENSEMBLE_WEIGHTS_CORR_ADJ` 30m 0.20→0.15 | **완료** — config/settings.py |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 확인 필요 |

### 수정 파일 (84차)

| 파일 | 변경 내용 |
|---|---|
| `model/multi_horizon_model.py` | `_CW_30M = {FL:0.65, UP:1.18, DN:1.18}` |
| `learning/batch_retrainer.py` | `_CW_30M` 동일하게 수정 (학습기 일관성) |
| `learning/online_learner.py` | `ACCURACY_WINDOW=150`, `_ADJUST_EVERY=3`, `_bucket_learn_count`, `blend_with_gbm()` 초기 GBM 전용 모드 |
| `model/ensemble_decision.py` | `ensemble_calibrator` 추가, 합의도 패널티, Platt 보정 로직 개선, `record_ensemble_outcome()` |
| `config/settings.py` | `ENSEMBLE_WEIGHTS_CORR_ADJ` 30m 0.20→0.15 재배분 |
| `main.py` | `_bias_buf` 롤링 버퍼, `_ensemble_conf_cache`, STEP 1 Bias 통계 재작성, 앙상블 보정기 학습 연결 |

### 84차 실세션 확인 사항 (2026-05-23)

1. **이상점 3 개선**: 30m 예측에서 FL 상황 DN 오분류 발생 빈도 감소 확인
2. **이상점 4 개선**: 50분 정확도 급락 추이 완화 (연속 실패에도 SGD 비중 점진적 감소)
3. **이상점 5 개선**: `[Bias⚠] 30m 적중=?%(N건) DN편향! 75%+` 형식 로그 발생 확인
4. **이상점 6 개선**: conf ≥ 60% 도달하는 분봉 비율이 이전 대비 증가하는지 SIGNAL 로그 확인
5. **앙상블 보정기**: 1m 검증 시 `ensemble_calibrator.record()` 호출. 100건 누적 후 `is_fitted=True` 전환 확인

---

## 2026-05-22 (83차) — 탈진장 ATR ratio 문턱 재설계

### 배경

`MicroRegimeClassifier._classify()`에서 탈진장(`REGIME_EXHAUSTION`)과 급변장(`REGIME_VOLATILE`)이 동일한 ATR 문턱(`1.5`)을 공유. 급변장 판정이 먼저 실행되므로 탈진장은 사실상 dead code — 장중 한 번도 발동 불가. `ofi_reversal_speed` 조건도 `bear_exhaustion`이 이미 내포한 정보라 불필요한 추가 차단 역할.

### 현재 상태

| 항목 | 상태 |
|---|---|
| `ATR_EXHAUSTION_MULT = 1.5` → `ATR_EXHAUSTION_MIN = 1.2` (독립 하한) | **완료** |
| exhaustion 구간: `1.2 ≤ atr_ratio < 1.5` (급변장과 겹침 없음) | **완료** |
| 양방향 대칭: `bull_exhaustion` 파라미터 추가 (SHORT MR 탈진 포착) | **완료** |
| `ofi_reversal_speed` 파라미터·조건 제거 (중복 필터) | **완료** |
| `main.py` 호출부 동기화 (`bull_exhaustion` 추가, `ofi_reversal_speed` 제거) | **완료** |
| 실세션 확인 | **미완료** — 2026-05-23 탈진장 로그 첫 발화 확인 필요 |

### 수정 파일 (83차)

| 파일 | 변경 내용 |
|---|---|
| `collection/macro/micro_regime.py` | `ATR_EXHAUSTION_MIN=1.2`, `push_1m_candle`·`_classify` 파라미터 재설계, exhaustion_conds 독립 구간 + 양방향 |
| `main.py` | `push_1m_candle()` 호출부: `bull_exhaustion` 추가, `ofi_reversal_speed` 제거 |

---

## 2026-05-22 (82차) — Layer 2 인트라데이 게이트 UI 패널 + L2 토글 영속성 및 즉시 적용

### 배경

Layer 2 IntradayTacticalRegime이 코드로 구현·통합(78차)되었으나, 대시보드에서 레짐 상태나 7개 지표 발동 여부를 확인할 방법이 없었음. L2 ON/OFF 토글도 재시작 시 초기화되고 장중 적용이 안 되는 문제 존재.

### 현재 상태

| 항목 | 상태 |
|---|---|
| 진입 관리 탭 Pre-flight 패널 좌우 양분 (5:6) | **완료** |
| Layer 2 상태 카드 (ON/OFF 버튼 + 레짐 색상 + 전환 레이블) | **완료** |
| Layer 2 7개 지표 표시 (발동 항목 빨간색 강조) | **완료** |
| Layer 2 조건 체크 로그 (진입허용·신뢰도강화·사이즈축소·복귀체크) | **완료** |
| L2 게이트 설정 영속성 (ui_prefs.json `layer2_gate_enabled`) | **완료** |
| L2 토글 장중 즉시 적용 — 3개 게이팅 포인트 `_l2_gate_on` 분기 | **완료** |
| `update_layer2(status_dict)` → main.py 파이프라인 연결 | **미완료** — STEP 6 또는 STEP 9에서 호출 코드 추가 필요 |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 확인 필요 |

### 수정 파일 (82차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | Layer 2 패널 3단 UI, `is_layer2_gate_enabled()`, `update_layer2()`, 영속성 메서드, `sig_layer2_gate_toggled` |
| `main.py` | `_l2_gate_on` 분기 (3개 게이팅 포인트), `_on_layer2_gate_ui_toggled` 핸들러, 시그널 연결 |

---

## 2026-05-22 (81차) — Platt 보정 기동 사전 fit + 앙상블 2차 압축

### 배경

GBM 과신 출력(99.9% 확신 → 실제 40%)의 근본 원인: `horizon_calibrator`가 매 기동마다 0샘플 fresh 상태로 시작. DB에 24,626건의 검증 예측이 있어도 로드 코드가 없어 첫 ~100 tick 동안 보정이 비활성. 제안된 코드에는 4가지 추가 버그도 있었음.

### 현재 상태

| 항목 | 상태 |
|---|---|
| `_preload_horizon_calibration()` 신규 메서드 | **완료** — 기동 시 DB 18,000건 로드 + `fit_all()` |
| `ensemble.calibrator` 주입 | **완료** — `main.py __init__` 에서 `self.ensemble.calibrator = self.horizon_calibrator` |
| `EnsembleDecision.__init__` `self.calibrator = None` | **완료** |
| Platt 보정 블록 위치 수정 | **완료** — stuck-breaker 후, **grade 계산 전** 삽입 |
| `confidence_raw` 필드 추가 | **완료** — `result` dict에 보정 전 원본 보존 |
| `transform()` → `calibrate()` 버그 수정 | **완료** |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 확인 필요 |

### 수정 파일 (81차)

| 파일 | 변경 내용 |
|---|---|
| `model/ensemble_decision.py` | `self.calibrator = None`, Platt 보정 블록 (grade 전), `confidence_raw` |
| `main.py` | `_preload_horizon_calibration()` 신규, `ensemble.calibrator` 주입 |

---

## 2026-05-21 (76~80차) — TrendPersistenceGate 대칭 구현 + Layer 2 통합 + 대시보드

### 배경

72차에서 방향 비대칭 편향 6종 수정 완료 후, 원웨이 추세장(상승/하락 한 방향으로 쭉 가는 날) 진입 부재 문제를 해결하기 위해 TrendPersistenceGate를 설계·구현·통합함.

### 76차 — CVD 단조성 비율 피처 추가

| 항목 | 상태 |
|---|---|
| `cvd_monotone_ratio` 피처 | **완료** — CVD 최근 20개 값 중 상승 이동 비율 (0~1) |
| `_cvd_history: deque(maxlen=21)` | **완료** — feature_builder 초기화에 추가 |
| GBM 피처 입력 | **완료** — 추세장 명시적 신호로 GBM 학습 지원 |

### 77차 — TrendPersistenceGate UP-only 최초 통합

| 항목 | 상태 |
|---|---|
| `TrendPersistenceGate` import | **완료** — `main.py` line ~104 |
| `self.trend_gate` 초기화 | **완료** — `__init__` line ~190 |
| STEP 6 TrendGate 블록 | **완료** — UP streak 활성 시 해당 방향 actual_min_conf 완화 |
| `reset_daily()` | **완료** — 일일 마감 라인 ~4182 |

### 78차 — Layer 2 IntradayTacticalRegime 완전 통합

| 항목 | 상태 |
|---|---|
| `min_conf_adjust()` 적용 | **완료** — DAY_RISK_OFF +5%p, CRASH +12%p (TrendGate 이후 적용) |
| `size_mult()` 적용 | **완료** — DAY_RISK_OFF ×0.5, CRASH ×0.3 (Toxicity gate 이후) |
| CRASH A등급 숏 예외 | **완료** — `allow_crash_grade_a_short()` + A등급 조건 조합 |

### 79차 — TrendPersistenceGate DOWN 대칭 구현

| 항목 | 상태 |
|---|---|
| UP/DN 듀얼 streak | **완료** — `_up_streak` / `_dn_streak` 독립 카운터 |
| DOWN 조건 | **완료** — `above_vwap=0 AND cvd_direction=-1` |
| hard_break 비대칭 | **완료** — UP=-300, DN=+200 (숏스퀴즈가 더 빠르고 파괴적) |
| return dict 변경 | **완료** — `up_active/up_streak/dn_active/dn_streak/min_conf_override` |

### 80차 — 대시보드 등급카드 깜빡임 UI

| 항목 | 상태 |
|---|---|
| `_trend_blink_timer` (600ms) | **완료** — `EntryPanel.__init__` |
| `_ens_grade_frame` / `_chk_grade_frame` 저장 | **완료** — `_build()` 루프 내 |
| `_on_trend_blink_tick()` | **완료** — UP=녹색(#3FB950), DN=오렌지(#D29922) 깜빡임 |
| `set_trend_gate_mode(mode)` | **완료** — EntryPanel + MainDashboard 위임 |
| main.py `set_trend_gate_mode()` 호출 | **완료** — STEP 6 TrendGate 블록 후 |

### 실세션 확인 사항 (2026-05-22)

1. UP streak 발동: `[TrendGate] UP 추세 지속 모드 ON (streak=10)` 로그 확인
2. DN streak 발동: `[TrendGate] DN 추세 지속 모드 ON (streak=10)` 로그 확인
3. 등급 카드 깜빡임: UP 활성→녹색, DN 활성→오렌지, 비활성→기본색 복원
4. Layer 2 min_conf_adjust: `[IntradayRegime] DAY_RISK_OFF — min_conf +5%p → 0.55` 형식 로그
5. Layer 2 size_mult: `[IntradayRegime] DAY_RISK_OFF 사이즈 축소 ×0.5 → N계약` 로그
6. CRASH A등급 숏 예외: `[IntradayRegime] CRASH — A등급 숏 추세추종 예외 허용` 로그

### 수정 파일 (76~80차)

| 파일 | 변경 내용 |
|---|---|
| `features/feature_builder.py` | `cvd_monotone_ratio` 피처 추가 |
| `strategy/entry/trend_persistence.py` | UP-only → UP+DN 듀얼 streak 전면 재작성 |
| `main.py` | TrendGate import·초기화·STEP6·reset_daily, Layer2 min_conf_adjust·size_mult·CRASH예외 |
| `dashboard/main_dashboard.py` | 등급 카드 깜빡임 (UP=녹, DN=오) + set_trend_gate_mode |

---

## 2026-05-21 (73차) — 레짐 확정 08:58 2단계 분리

### 배경

매일 08:55 첫 macro fetch에서 `MacroFetcher._first_fetch_done` 메커니즘에 의해
SP500·KRW chg가 항상 0.0으로 나옴. 그 직후 레짐을 확정하면 VIX 단독 결정 구조가 됨.
2회차 fetch(08:58~)에서 실제 값이 나오지만 레짐은 이미 고정된 상태였음.

### 현재 상태

| 항목 | 상태 |
|---|---|
| `pre_market_setup()` 1단계화 | **완료** — seed fetch + PreRetrain만, 레짐 확정 제거 |
| `_pre_market_stage2()` 신규 | **완료** — 08:58 2회차 fetch + 레짐 확정 + 대시보드 + 알림 |
| `_heartbeat` 2단계 분리 | **완료** — stage1(08:55) / stage2(08:58~09:05) 조건 분리 |
| 실세션 검증 | **미완료** — 2026-05-22 장중 확인 필요 |

### 수정 파일 (73차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `pre_market_setup()`: 레짐 확정 로직 제거, seed fetch + PreRetrain만 |
| `main.py` | `_pre_market_stage2()` 신규 — 2회차 fetch + 레짐 확정 |
| `main.py` | `_heartbeat`: `_pre_market_stage1_done` 플래그 추가, 08:58 stage2 조건 삽입 |
| `main.py` | `connect_broker()` + 일일 마감: `_pre_market_stage1_done = False` 리셋 추가 |

### 변경 전후 타임라인

```
[변경 전]
08:55  pre_market_setup()
         → seed fetch (SP500=0%, KRW=0%)
         → 레짐 확정 (VIX만 반영) ← 문제
         → PreRetrain 시작
         → realtime 구독 시작

[변경 후]
08:55  pre_market_setup() [1단계]
         → seed fetch (SP500=0%, KRW=0%)
         → PreRetrain 시작
         → realtime 구독 시작

08:58  _pre_market_stage2() [2단계]
         → manual_fetch() 강제 2회차
         → 레짐 확정 (SP500·KRW 실수치 반영) ← 개선
         → 대시보드 업데이트
         → notify_premarket_ready()
```

### 실세션 확인 사항

1. `08:55:XX [System] 매크로 seed fetch 완료 — 레짐 확정은 08:58 2단계로 연기` 로그 확인
2. `08:58:XX [System] 매크로 수집 완료 | VIX=XX SP500=%+.2f%% KRW=%+.2f%%` — 실수치 확인 (SP500≠0.00%)
3. `08:58:XX [System] 레짐 확정: XXX | ...` 로그 확인
4. GAP_OPEN 구간(09:00~09:05) 진입 전에 레짐이 정상 확정됐는지 확인

---

## 2026-05-21 (72차) — 방향 비대칭 편향 6종 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| OFI 역전 신호 양방향화 | **완료** — `bull_reversal_signal` + `bear_reversal_signal` 분리, 구 `ofi_reversal_signal` deprecated |
| CVD 탈진 양방향화 | **완료** — `bear_exhaustion` + `bull_exhaustion` 분리, 구 `cvd_exhaustion`/`exhaustion` deprecated |
| prev_bar_direction 3-state | **완료** — `prev_bar_bullish: bool` → `prev_bar_direction: int`(+1/0/-1), 도지 양쪽 불통과 |
| PCR 극단값 양방향화 | **완료** — `pcr_extreme_bearish` + `pcr_extreme_bullish`(≤0.67) + `pcr_extreme_signed`(연속값) 추가 |
| S&P500 레짐 임계값 대칭화 | **완료** — `< -1.0` → `< -0.5` (상승 +0.5%와 대칭) |
| RL HOLD 페널티 제거 | **완료** — `hold_penalty = 0.0` (CB·체크리스트 외부 제어와 중복 제거) |
| 실세션 검증 | **미완료** — 2026-05-22 장중 새 신호 동작 확인 필요 |
| deprecated 피처 제거 | **보류** — 모델 재훈련 후 구 피처 수렴 확인 뒤 제거 예정 |

### 수정 파일 (72차)

| 파일 | 변경 내용 |
|---|---|
| `features/technical/cvd_exhaustion.py` | `bear_exhaustion` + `bull_exhaustion` 양방향 탈진 계산 추가, 구 alias 유지 |
| `features/technical/ofi_reversal.py` | `bull_reversal_signal` + `bear_reversal_signal` 분리, 구 `signal` deprecated |
| `features/feature_builder.py` | 신규 6개 피처 등록 + 구 deprecated 피처 alias 유지 |
| `strategy/entry/checklist.py` | 파라미터 `bear_exhaustion` + `bull_exhaustion` 분리, `prev_bar_direction` int 3-state |
| `main.py` | 체크리스트 호출 파라미터 갱신, `prev_bar_direction` 계산 인라인 추가 |
| `collection/macro/micro_regime.py` | `cvd_exhaustion` → `bear_exhaustion` 파라미터 변경 |
| `challenger/variants/vwap_reversal.py` | `cvd_exhaustion` → `bear_exhaustion` (하락 압력 소진 의미 명확화) |
| `challenger/variants/exhaustion_regime.py` | `cvd_exhaustion` → `bear_exhaustion` 피처 조회 변경 |
| `collection/options/pcr_store.py` | `PCR_EXTREME_BULLISH_THRESHOLD=0.67` 신규, `pcr_extreme_bearish/bullish/signed` 추가 |
| `features/options/option_features.py` | 신규 3개 PCR 극단 피처 pass-through, `empty()` 갱신 |
| `collection/macro/regime_classifier.py` | SP500 하락 임계값 `< -1.0` → `< -0.5` |
| `learning/rl/reward_design.py` | HOLD 페널티 `0.001` → `0.0` 제거 |

### SHORT MR 핵심 수정 (의미론 오류)

```python
# 수정 전 (버그): SHORT MR에 하락 압력 소진 조건 → 의미 역전
if vwap_position > 1.5 and bear_exhaustion > 0.0:
    entry_mode = "MEAN_REVERSION"

# 수정 후: SHORT MR에 상승 압력 소진 조건 → 의미 정확
if vwap_position > 1.5 and bull_exhaustion > 0.0:
    entry_mode = "MEAN_REVERSION"
```

---

## 2026-05-21 (71차) — 자동진입관리 UI 카드 구조 개편

### 현재 상태

| 항목 | 상태 |
|---|---|
| 자동진입관리 패널 카드 구조 | **완료** — 앙상블 등급·체크리스트 등급·최종진입 3카드 분리 |
| 레이아웃 빈 공간 | **해소** — QGridLayout → VBox+HBox 재구성 |
| 최종진입 깜박임 | **구현** — 600ms QTimer, 진입 조건 시 녹색 테두리 blink |
| 수량 카드 균등 폭 | **완료** — stretch=1 균등 분배 |

### 수정 파일 (71차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | EntryPanel: 신뢰도→앙상블등급 카드, 진입등급→체크리스트등급 라벨, 최종진입 카드 신규, 레이아웃 재구성, blink 타이머 추가 |
| `main.py` | `update_entry()` 호출에 `ensemble_grade`, `checklist_grade`, `final_entry` 파라미터 추가 |

### 카드별 데이터 소스

| 카드 | 소스 |
|---|---|
| 앙상블 등급 | `decision["grade"]` (EnsembleDecision, 게이트 적용 전) |
| 체크리스트 등급 | `_cr["grade"]` (EntryChecklist, 게이트 적용 전 순수 체크리스트 결과) |
| 최종진입 | `direction!=0 AND _final_grade in ("A","B")` (모든 게이트 적용 후) |

---

## 2026-05-20 (69차) — signal() TypeError ERR-FATAL 수정 + traceback 로깅 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| 68차 개선 3항목 실세션 검증 (11:46:31~) | **완료** — ERR-FATAL 소멸·신뢰도 미달 로그 정상·watchdog 거짓 경보 없음 |
| `signal() takes 2 positional arguments but 3 were given` | **수정 완료** — 3개 파일 수정 |
| ERR-FATAL 발생 시 traceback 가시성 | **개선** — RECOVERABLE·DEGRADED·FATAL 모두 traceback.format_exc() 추가 |
| 69차 수정 실세션 재검증 | **미완료** — 2026-05-21 장중 확인 필요 |

### 수정 파일 (69차)

| 파일 | 변경 내용 |
|---|---|
| `utils/error_policy.py` | `import traceback` 추가. RECOVERABLE·DEGRADED·FATAL 3케이스 모두 `\n%s, traceback.format_exc()` 로깅 |
| `scripts/validate_health_policy_hotreload.py` | `_Collector.signal(self, msg)` → `_Collector.signal(self, msg, level="INFO")` — monkey-patch 중 TypeError 방지 |
| `main.py` | `_hc_block`·IntradayRegime 롱차단·숏차단 3곳 `log_manager.signal(msg, "WARNING")` → `log_manager.signal(msg, level="WARNING")` keyword 인수 변경 |

### 버그 핵심 구조 (수정 전)

```
validate_health_policy_hotreload.py 실행 중:
  log_manager.signal = collector.signal   # monkey-patch
  collector.signal(self, msg)             # level 파라미터 없음

main.py pipeline:
  IntradayRegime CRASH + direction=LONG →
    log_manager.signal(msg, "WARNING")   # positional 3번째 인수
    → TypeError: takes 2 positional arguments but 3 were given
    → ERR-FATAL minute_pipeline 매분 크래시
```

### 운영 메모

- traceback 추가로 다음 ERR-FATAL 시 WARN.log에 파일명·라인 번호 포함 → 디버깅 속도 대폭 향상
- `validate_health_policy_hotreload.py`는 개발 스크립트. 장중 실행 시 monkey-patch 기간이 pipeline 실행과 겹치지 않도록 주의

---

## 2026-05-20 (68차) — minute_pipeline ERR-FATAL 실제 근본 원인 최종 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| 11:04 재시작 자체 | **정상** — tick/hoga/realtime 구독 완료, 데이터 유입 확인 |
| `minute_pipeline` 치명 예외 원인 | **최종 규명 완료** — `checklist.py:95` `entry_mode` 할당 전 참조 (UnboundLocalError) |
| 1차 수정 81e0784 (`main.py`) | **오진단** — UI 모드 변수(auto/hybrid/manual)를 수정했으나 실제 버그는 별개 파일 |
| watchdog 90초/150초 경보 | **원인 규명 완료** — 파이프라인 예외로 `notify_pipeline_ran()` 미도달 → 허위 지연 경보 |
| `checklist.py` 최종 수정 | **완료** — `entry_mode = "TREND_FOLLOW"` 초기화를 `checks = {}` 바로 다음으로 이동 |
| 실세션 재검증 | **미완료** — 2026-05-21 장중 grade=X 분봉에서 ERR-FATAL 소멸 확인 필요 |

### 수정 파일 (68차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` (81e0784, 오진단) | `entry_mode="manual"` 기본값 추가 — UI 진입모드 변수 수정 (실제 버그와 무관) |
| `strategy/entry/checklist.py` | `entry_mode = "TREND_FOLLOW"` 초기화를 `checks = {}` 바로 뒤(line 77)로 이동 — 신뢰도 미달 조기 반환(line 89~96)보다 선행 할당 보장 |

### 버그 핵심 구조 (수정 전)

```
checklist.py evaluate():
  checks = {}
  if not checks["2_confidence"]:   # conf=43.4% < 58% → 항상 True
    return {"entry_mode": entry_mode}  # line 95: 미할당 참조 → UnboundLocalError
  entry_mode = "TREND_FOLLOW"      # line 100: 할당이 여기 있어 로컬 변수로 지정됨
```

### 운영 메모

- `conf < min_conf` 인 분봉(X등급) 전체에서 100% 재현. 장 중 신뢰도 낮은 구간에서 파이프라인이 매분 예외 종료.
- watchdog "분봉 수신 지연 의심" 문구는 분봉 미수신이 아닌 예외 중단 케이스에서도 발생. 추후 분리 표기 개선 검토.

---

## 2026-05-20 (67차) — 장중 로그 분석 + 이상점 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| online_learner scaler partial_fit 버그 수정 | **완료** — 매 샘플마다 `partial_fit()` 호출로 변경 |
| SYSTEM 로그 CB③30m 명확화 | **완료** — `정확도=X%` → `CB③30m=X%(N건)` / `집계중` 표시 |
| horizon별 [Bias] 편향 진단 로그 추가 | **완료** — STEP 1 직후 호라이즌별 UP/FL편향 자동 감지 |
| conf 클립 DEBUG 로그 추가 | **완료** — `[Calib] clipped` DEBUG 로그 |
| SYSTEM 정확도=0.0% 원인 규명 | **완료** — 세션 초반 30분 필터 공백(정상) + 30m 실제 정확도 낮음 |
| 5m bullish bias / 30m flat bias 근본 수정 | **미완료** — [Bias] 로그로 관찰 후 calibration 재보정 필요 |
| 6분 주기 처리시간 스파이크 원인 | **미완료** — GBM 재학습 연관 추정, 단계별 타이머 관찰 필요 |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (67차)

| 파일 | 변경 내용 |
|---|---|
| `learning/online_learner.py` | scaler `partial_fit()` 매 샘플마다 호출 (조건 제거) |
| `dashboard/main_dashboard.py` | `update_system_status()` `cb3_samples` 파라미터 추가. SYSTEM 로그 `CB③30m=X%(N건)` 형식 |
| `main.py` | `update_system_status(cb3_samples=...)` 전달 추가. `[Bias]` horizon 편향 진단 로그 (STEP 1 직후). conf 클립 시 `[Calib] clipped` DEBUG 로그 |

---

## 2026-05-20 (66차) — SHAP 중요도·파라미터 상관계수 이상점 점검 및 4종 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| RESTORED값 LIVE 오인 버그 (임계값 30 vs 100 불일치) | **완료** — `update()` bool 반환 + `_refresh_shap_state()` 임계값 `SHAP_MIN_DATA_POINTS`로 통일 |
| 구버전 `_update_shap_dashboard()` 중복 메서드 제거 | **완료** — 데드코드 + 인코딩 깨진 문자열 포함 블록 삭제 |
| `_shap_feature_window` 재시작 후 미복원 (30분 공백) | **완료** — `_restore_analysis_buffers()`에 DB 복원 추가 |
| `_build_param_corr_string()` `short_names` 인코딩 깨짐 | **완료** — 정상 UTF-8 한글로 교체 |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (66차)

| 파일 | 변경 내용 |
|---|---|
| `learning/shap/shap_tracker.py` | `update()` 반환형 → `bool` (실계산 True, 데이터 부족·실패 False) |
| `main.py` | `SHAP_MIN_DATA_POINTS` import 추가 |
| `main.py` | `_refresh_shap_state()`: 임계값 30→`SHAP_MIN_DATA_POINTS`(100), `update()` 반환값으로 `_live_shap_ready` 제어 |
| `main.py` | 구버전 `_update_shap_dashboard()` (line 820~861) 제거 (데드코드) |
| `main.py` | `_restore_analysis_buffers()`: `_shap_feature_window` DB 데이터로 복원 추가 |
| `main.py` | `_build_param_corr_string()`: `short_names` 키 인코딩 깨짐 → 정상 한글 교체 |

### 핵심 버그 흐름 (수정 전)

```
재시작 후 30개 live 분봉 쌓임
  → _refresh_shap_state(): len(window)=30 >= 30 → update() 호출
  → shap_tracker.update(): len(X)=30 < 100 → return (계산 안 함)
  → get_current_ranking() → 복원값 반환
  → _live_shap_ready = True  ← 버그: 실계산 없이 True
  → 대시보드: 복원값이 "LIVE" 표시
  → save_shap_scores(): 복원값을 LIVE로 DB 저장
```

### 66차 실세션 확인 사항 (2026-05-21)

1. DB에 100건 이상 raw_features가 있으면 기동 직후 SHAP live 계산 성공하는지 확인
2. 100건 미만 구간에서 대시보드에 LIVE 표시 안 나타나는지 확인
3. 파라미터 상관계수 레이블 정상 한글 표시(CVD, VWAP, 외인콜 등) 확인

---

## 2026-05-20 (65차) — 신뢰도·VWAP 흐름 분석 + 진입 체크리스트 7종 개선

### 현재 상태

| 항목 | 상태 |
|---|---|
| 신뢰도 강제 X 게이트 | **완료** — `2_confidence` 실패 시 CORE와 동일하게 즉시 X 반환 |
| min_conf 단일 출처 통일 | **완료** — `actual_min_conf = max(레짐 기준, 시간대 기준)`. 체크리스트·대시보드 전 구간 적용 |
| VWAP 역추세 예외 분기 활성화 | **완료** — `checklist.evaluate()` 호출에 `cvd_exhaustion`·`micro_regime` 추가. MEAN_REVERSION 분기 실제 작동 |
| UI 신뢰도 레이블 동적화 | **완료** — `_conf_chk_name_label` 저장 → 매분 `"신뢰도 ≥ {min_conf:.0%}"` 갱신 |
| CVD·OFI 중립(0) 차단 | **완료** — `>= 0` → `> 0` (중립 신호가 CORE 통과하던 허점 제거) |
| 외인 방향 AND 강화 | **완료** — `or` → `and`. 콜/풋 양수 AND 상대우위 모두 필요 |
| 손실률 분모 동적화 | **완료** — `50_000_000` → `max(_ts_current_sizer_balance(self), 50_000_000)` |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (65차)

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/checklist.py` | 신뢰도 강제 X 반환 블록 추가 + CVD·OFI `> 0`/`< 0` 수정 + 외인 방향 `and` |
| `strategy/entry/time_strategy_router.py` | `get_zone_min_confidence(zone)` 헬퍼 추가 |
| `main.py` | `get_zone_min_confidence` import + `actual_min_conf` 계산 (decision 직후) + `checklist.evaluate()` cvd_exhaustion·micro_regime 추가 + 손실률 분모 동적화 |
| `dashboard/main_dashboard.py` | `_conf_chk_name_label` 저장 + `update_data()` 레이블 동적 갱신 |

### min_conf 흐름 (65차 이후)

```
ensemble_decision.py
  → decision["min_conf"] = REGIME_MIN_CONFIDENCE[레짐]
    (RISK_ON=0.52, NEUTRAL=0.58, RISK_OFF=0.65)

main.py (decision 직후)
  → actual_min_conf = max(decision["min_conf"], get_zone_min_confidence(time_zone))
    (OPEN_VOLATILE=0.63, GAP_OPEN=0.67, STABLE_TREND=0.58, ...)

checklist.evaluate(min_confidence=actual_min_conf)
  → 신뢰도 미달 시 즉시 X 반환

dashboard.update_data(min_conf=actual_min_conf)
  → 신뢰도 색상 + 레이블 모두 actual_min_conf 기준
```

---

## 2026-05-20 (64차) — 09:34 재시작 점검 + 3종 이상점 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| 장중 재시작 warmup 재학습 CB⑤ | **완료** — `connect_broker()` 장중(09:00~15:10) 완료 시 즉시 GBM 재학습 시작. 첫 파이프라인 STEP 3 skip 보장 |
| `_gbm_retrain_running` 초기화 | **완료** — `__init__`에 `False` 명시적 초기화. `getattr` 방어 패턴 불필요 |
| `_last_close` 초기화 | **완료** — `__init__`에 `0.0` 추가. `_poll_option_chain` QTimer 콜백에서 사용 |
| OptionChain BlockRequest 루프 파이프라인 분리 | **완료** — STEP 4 `refresh()` → `get_features()` 캐시 읽기만. QTimer 300s 별도 폴링 |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (64차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `connect_broker()`: 장중 재시작 즉시 GBM warmup 재학습 스레드 시작 블록 추가 |
| `main.py` | `__init__`: `_gbm_retrain_running: bool = False`, `_last_close: float = 0.0` 초기화 |
| `main.py` | `run_minute_pipeline()` STEP 4: `refresh()` 제거, `self._last_close = close` 추가 |
| `main.py` | `_poll_option_chain()` QTimer 콜백 신규 추가 |
| `main.py` | `daily_close()`: `_option_chain_timer.stop()` 추가 |
| `strategy/runtime/broker_runtime_service.py` | `_option_chain_timer` QTimer 생성 + `ensure_market_open_runtime_started()`에서 `start(300_000)` |

### OptionChain QTimer 분리 구조 (64차 신규)

```
장 시작(09:00) → ensure_market_open_runtime_started()
  → _option_chain_timer.start(300_000)   # 5분마다 메인 스레드 QTimer

STEP 4 (매분):
  → option_chain_snap.get_features()     # 캐시 읽기, 0ms

_poll_option_chain() (매 5분, QTimer 콜백):
  → option_chain_snap.refresh(spot=_last_close)  # BlockRequest 루프 (파이프라인 외부)
  → dashboard.update_option_chain()
```

---

## 2026-05-20 (63차) — 파이프라인 크래시 버그 4종 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| log_manager.signal() TypeError 크래시 | **완료** — `level="INFO"` 기본값 추가. 09:14 이후 매분 파이프라인 재귀 실패 해소 |
| GBM 재학습 08:55 분리 | **완료** — `pre_market_setup()` 끝에서 PreRetrain 블록. 09:00 첫 파이프라인 CB⑤ 충돌 방지 |
| PCR 장초반 극단값 — PCRStore 방어 | **완료** — `PCR_MIN_CALL_ABS=1000` skip, `PCR_MAX=4.0` cap. opt_pcr_slope_norm=-5.87 매분 반복 해소 |
| quality_investor_age_sec z=+45 방어 | **완료** — `min(..., 300.0)` cap. 09:00 첫 파이프라인 z-score 폭발 방지 |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (63차)

| 파일 | 변경 내용 |
|---|---|
| `logging_system/log_manager.py` | `signal(msg, level="INFO")` — level 기본값 추가. `log_manager.signal(msg, "WARNING")` 3곳 호출 복구 |
| `main.py` | `pre_market_setup()` 끝에 `[PreRetrain]` 블록 추가. 08:55 GBM 재학습 트리거 |
| `collection/options/pcr_store.py` | `PCR_MIN_CALL_ABS=1000`, `PCR_MAX=4.0` 추가. `update()` call_abs 최소값 방어 + PCR 상한 적용 |
| `features/feature_builder.py` | `quality_investor_age_sec = min(..., 300.0)` cap 추가 |

### 63차 실세션 확인 사항 (2026-05-21)

1. **[PreRetrain]** SYSTEM 로그: `08:55:XX [PreRetrain] 08:55 GBM 사전 재학습 시작` 로그 발생
2. **CB⑤ 없음**: 09:00 첫 파이프라인 처리시간 < 5000ms (PreRetrain 이미 진행 중 → STEP 3 skip)
3. **opt_pcr_slope_norm 정상화**: 09:02부터 `-5.87` 반복 사라짐 (또는 pcr_available=0으로 중립)
4. **파이프라인 무크래시**: `[복구 실패]` 로그 없음. 09:14 이후에도 정상 흐름
5. **IntradayRegime=CRASH 차단 로그**: 이제 TypeError 없이 `[IntradayRegime] CRASH — 신규 롱 금지` 정상 출력
6. **quality_investor_age_sec**: 09:00 첫 파이프라인 z-score < +15 (min(840, 300) = 300 → z 정상화)

### 오늘(5/20) 확인된 잠재 버그 (미수정)

| 버그 | 증상 | 우선순위 |
|---|---|---|
| 잔고 TR 파싱 `rows=0` | `[BrokerSync] 잔고 rows=0` — 포지션 미인식 가능성 | 실전 전환 전 필수 수정 |
| 프로그램 매매 TR | 사용 TR 미확인 상태 | 실전 전환 전 필수 확인 |

---

## 2026-05-19 (62차) — 매크로 레짐 종합 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| IntradayTacticalRegime (Layer 2) | **완료** — `intraday_tactical_regime.py` 신규. NORMAL/DAY_RISK_OFF/CRASH |
| main.py Layer 2 파이프라인 통합 | **완료** — 매분 update + 진입 차단 + reset_daily |
| micro_regime ATR 둔감 수정 | **완료** — 2.0→1.5 + z_warn≥3 복합 조건 |
| macro_fetcher 첫 fetch=0 버그 | **완료** — `_first_fetch_done` 분기로 NEUTRAL 편향 제거 |
| RegimePanel 레짐 모니터 위젯 | **완료** — Layer1/2/Micro 3배지 + 진입정책 + 이력 로그 |
| "🌐 레짐" 대시보드 탭 | **완료** — `mid_tabs` 탭 추가, Layer1·Micro 업데이트 훅 연결 |
| 실세션 동작 확인 | **미완료** — 다음 장 기동 필요 |

### 신규 파일 (62차)

| 파일 | 내용 |
|---|---|
| `collection/macro/intraday_tactical_regime.py` | IntradayTacticalRegime: DAY_RISK_OFF/CRASH 진입정책 분류기 |
| `dashboard/panels/regime_panel.py` | RegimePanel: 3계층 레짐 실시간 모니터 위젯 |

### 수정 파일 (62차)

| 파일 | 변경 내용 |
|---|---|
| `collection/macro/macro_fetcher.py` | `_first_fetch_done` 플래그. 초회 시딩 전용 경로 |
| `collection/macro/micro_regime.py` | ATR_VOLATILE_MULT 2.0→1.5, z_warn_count 파라미터, 복합 급변 조건 |
| `main.py` | IntradayTacticalRegime import·인스턴스·파이프라인·차단·reset |
| `dashboard/main_dashboard.py` | "🌐 레짐" 탭, `update_layer1/micro()` 훅 |

### Layer 2 정책 요약

| 레짐 | 롱 | 숏 | 사이즈 | 신뢰도보정 |
|---|---|---|---|---|
| NORMAL | 허용 | 허용 | ×1.0 | +0%p |
| DAY_RISK_OFF | **금지** | 허용 | ×0.5 | +5%p |
| CRASH | **금지** | **금지** | ×0.3 | +12%p |

### 62차 실세션 확인 사항

1. **"🌐 레짐" 탭**: Layer1/Layer2/Micro 3배지 정상 표시
2. **Layer 2 전환 로그**: `[IntradayRegime] NORMAL → DAY_RISK_OFF` (하락장 시)
3. **진입 차단 로그**: `[IntradayRegime] DAY_RISK_OFF — 신규 롱 금지`
4. **micro 급변장**: 장중 ATR 확대 구간에서 `급변장` 판정 확인
5. **macro_fetcher**: 2회차 fetch chg 실수치 (≠ 0.0) 로그 확인

---

## 2026-05-19 (61차) — CB HALT 분석 + 지표 버그 수정 + CB⑤ 재설계

### 현재 상태

| 항목 | 상태 |
|---|---|
| CB HALT 분석 (11:11~12:19) | **완료** — 50분정확도 26%→21% 하락, 15m/10m 역추세 고확신 연속 오답 패턴 |
| 예측 로그 direction 추가 | **완료** — `main.py` 실패 시 `예측=DN 실제=UP` 방향 정보 추가 |
| 정확도=0.0% 버그 수정 | **완료** — `update_system_status()` `accuracy=_acc30m` 전달 추가 |
| API지연=0ms 버그 수정 + CB⑤ 재설계 | **완료** — `record_pipe_latency()` 신규. 1초 경고·5초 PAUSE |
| 모델 AI 카드 하드코딩 버그 수정 | **완료** — `_model_vals` 참조 저장 + `update_model_cards()` 신규 + 매분 갱신 |
| 헬스 카드 "처리시간" 전환 | **완료** — HealthPanel·LogPanel 양쪽 레이블·툴팁·스파크라인 모두 |
| CB⑤ 테스트 추가 | **완료** — `tests/test_circuit_breaker.py` 2케이스 추가 |
| 실세션 동작 확인 | **미완료** — 다음 장 기동 필요 |

### 수정 파일 (61차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | `CB_PIPE_WARN_MS=1000`, `CB_PIPE_PAUSE_MS=5000` 추가. `HEALTH_LATENCY_WARN_MS` 2500→1000 |
| `safety/circuit_breaker.py` | `record_pipe_latency()` 신규. `CB_PIPE_WARN_MS·PAUSE_MS` import 추가 |
| `main.py` | `_pipe_t0` 타이머, `_pipe_ms` 계산, `record_pipe_latency` 연결. `record_api_latency` 제거. 예측 로그 direction 추가. `update_model_cards` 매분 호출. `accuracy=_acc30m` 전달 |
| `dashboard/main_dashboard.py` | `HealthPanel`: "처리시간" 전환·툴팁·내부 임계값(500→1000, 1000→5000). `LogPanel`: 동일. `update_model_cards()` 신규 (LogPanel + MireukDashboard). `_model_vals` 참조 저장 |
| `tests/test_circuit_breaker.py` | `record_pipe_latency` 경고·정지 2케이스 추가 |

### 61차 실세션 확인 사항

1. **처리시간 카드**: 6 운영 헬스 탭 "처리시간" 표시 + 툴팁 확인 (호버 시 임계값 안내)
2. **SYSTEM 로그**: `CB=NORMAL | 처리시간=Xms | 정확도=YY.Y%` 형식 확인
3. **모델 AI 카드**: 매분 `정확도(50분)·SGD비중·자가학습` 실시간 갱신 확인
4. **예측 로그**: `✗ 15m 예측 실패 (conf=73.9% 예측=DN 실제=UP)` 형식 확인
5. **CB⑤**: 파이프라인 1초 초과 시 `[CB⑤] 파이프라인 Xms 경고` 로그 발생 여부

---

## 2026-05-19 (60차) — 5/19 CB③ 심층분석 기반 안전장치 6종 + Shadow/Contrarian 구현

### 현재 상태

| 항목 | 상태 |
|---|---|
| 1순위: Mid-Conf Blind Spot Tracker | **완료** — `circuit_breaker.py` 60~85% 구간 7연속 오답 → strict 모드 발동 |
| 2순위: Brier Score 실시간 추적 | **완료** — `circuit_breaker.py` 이동평균(10건). >0.35 경고, >0.45 사이즈 50% 패널티 |
| 3순위: 재시작 루프 브레이커 | **완료** — `circuit_breaker.py` _daily_halt_count 2회→50%, 3회→완전관망 |
| 4순위: 장 시작 5분 DNA 진단 | **완료** — `safety/market_dna.py` 신규. 4항목 3/4 이상 이상 → dna_mult=0.25 |
| 5순위: CORE Health Score → Sizer 연동 | **완료** — `features/core_health.py` 신규. 4개 안전 배수 position_sizer 연결 |
| 6순위: Shadow Session 상태 머신 | **완료** — `safety/shadow_session.py` 신규. SHADOW→LIVE/BLOCKED 게이트 |
| 6순위: Contrarian Mode 상태 머신 | **완료** — `safety/contrarian_mode.py` 신규. 3조건 WATCHING→ARMED→ACTIVE |
| 6순위: 실험 게이트 대시보드 탭 | **완료** — `experiment_gate_panel.py` 신규 + main_dashboard "🧪 실험 게이트" 탭 |
| 파이프라인 전체 문서화 | **완료** — `docs/PIPELINE_FLOW.md` 신규. STEP 1~9 전체 흐름 |
| 실세션 동작 확인 | **미완료** — 다음 장 중 첫 기동 필요 |

### 수정 파일 (60차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | CB 신규 상수 9개 (Mid-Conf 3, Brier 3, HALT 2 + 기존) |
| `safety/circuit_breaker.py` | Mid-Conf·Brier·재시작루프 3종 추가. status/state_dict/reset 전체 반영 |
| `safety/market_dna.py` | **신규** — 장 시작 5분 DNA 진단기 |
| `safety/shadow_session.py` | **신규** — Shadow Session 상태 머신 (SHADOW/LIVE/BLOCKED) |
| `safety/contrarian_mode.py` | **신규** — Contrarian Mode 상태 머신 (WATCHING/ARMED/ACTIVE/CLEARED) |
| `features/core_health.py` | **신규** — CORE 피처 건강 점수 0~100 계산기 |
| `model/multi_horizon_model.py` | `last_z_warn_count` 노출, 예측 결과에 `extreme_count` 포함 |
| `strategy/entry/position_sizer.py` | 안전 배수 4종 파라미터 추가 (core_health/brier/restart/dna) |
| `dashboard/panels/experiment_gate_panel.py` | **신규** — Shadow + Contrarian 모니터 UI |
| `dashboard/main_dashboard.py` | "🧪 실험 게이트" 탭 mid_tabs 마지막에 추가 |
| `main.py` | MarketDNA·CoreHealth·Shadow·Contrarian 초기화·매분업데이트·Sizer연결·reset_daily |
| `docs/PIPELINE_FLOW.md` | **신규** — 매분 파이프라인 전체 흐름 문서 |

### 안전 배수 조합 (5/19 재현 시 예상값)

```
core_health_mult × brier_mult × restart_mult × dna_mult
= 0.5 × 0.5 × 0.5 × 0.25 = 0.031 → 사실상 0계약
```

### 다음 기동 확인 사항

1. **Mid-Conf 추적**: 60~85% 구간 오답 연속 시 `[CB] mid_conf_wrong_streak=N` 로그
2. **Brier Score**: 10건 이동평균 >0.35 → `[CB] Brier 경고`, >0.45 → `brier_size_mult=0.5`
3. **재시작 루프 브레이커**: 일별 halt 2회 차 → 사이즈 50%, 3회 차 → 완전관망
4. **MarketDNA**: 09:05에 `[DNA] score=N/4 → dna_mult=X` 로그
5. **CoreHealth**: 매분 `[CoreHealth] score=N → size_mult=X` 로그
6. **ShadowSession**: 09:40 이전 게이트 통과 → `[Shadow] → LIVE` 또는 `BLOCKED`
7. **ContrarianMode**: acc30m<25% 발생 시 `[Contrarian] ARMED` 상태 전환
8. **실험 게이트 탭**: mid_tabs 마지막 탭 정상 표시, 30초 주기 자동 갱신

---

## 2026-05-18 (58차) — 안전장치 6종 구현

### 현재 상태

| 항목 | 상태 |
|---|---|
| P0: PG+CB 상태 영속화 | **완료** — `to/from_state_dict()` 구현, `session_state.json`에 저장/복원 |
| P0: "상태유지" 체크박스 | **완료** — 모의투자/실서버 동일 행 우측. `ui_prefs.json` 연동 |
| P1-a: Restart Armistice | **완료** — 재시작 후 90초 + 브로커 sync ≥2회 clean 전까지 진입 차단 |
| P1-b: Position Integrity Checksum | **완료** — engine/broker/pending 삼각 검증, 불일치 2회 경보, 3회 진입 차단 |
| P2-b: Setup Expectancy Ledger | **완료** — trades.db 5컬럼 추가, 진입 컨텍스트 저장, INSERT 확장 |
| P2-b: 셋업 기대값 패널 | **완료** — `setup_expectancy_panel.py` 신규, mid_tabs "📊 셋업 기대값" 탭 추가 |
| P3-a: OnlineLearner 오염 학습 보호 | **완료** — stuck 분봉 SGD 학습 전체 스킵 |
| P3-b: Reverse Entry Clamp | **완료** — 청산 후 180초 반대 방향 진입 차단 |
| 5/19 실세션 동작 확인 | **미완료** — 최초 기동 필요 |

### 수정 파일 (58차)

| 파일 | 변경 내용 |
|---|---|
| `safety/circuit_breaker.py` | `to_state_dict()` / `from_state_dict()` |
| `strategy/profit_guard.py` | `to_state_dict()` / `from_state_dict()` |
| `strategy/runtime/session_recovery_service.py` | PG+CB 상태 복원 블록 |
| `utils/db_utils.py` | 셋업 태그 5컬럼 마이그레이션 |
| `main.py` | 안전장치 6종 전체 |
| `dashboard/main_dashboard.py` | `chk_state_persist` + `setup_expectancy_panel` 탭 |
| `dashboard/panels/setup_expectancy_panel.py` | 신규 생성 |

### 5/19 기동 확인 사항

1. **상태유지**: ProfitGuard/CB가 HALT 상태인 채로 재시작 → 상태 유지 확인 (`[Restore] ProfitGuard 상태 복원` / `[CB] 상태 복원` 로그)
2. **상태유지 Off**: 체크박스 해제 후 재시작 → PG/CB 초기화 확인
3. **Armistice**: 재시작 직후 signal 발생해도 진입 없음. 90초 경과 + sync 2회 후 진입 허용
4. **Integrity**: FLAT 진입 전 `[Integrity]` 로그 — mismatch=0, integrity_fail=0 확인
5. **Reverse Clamp**: 청산 직후 반대 신호 시 `[ReverseClamp] 진입 차단` 로그
6. **셋업 기대값 탭**: mid_tabs 마지막 탭 표시, 거래 데이터 없으면 빈 테이블 표시
7. **SGD stuck 가드**: ENTRY/EXIT stuck 분봉 STEP 2 로그에 `[SGD] stuck 발생 분봉 — N건 학습 스킵`

---

## 2026-05-18 (57차) — UI 체크박스 설정 유지 버그 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| B120 Fix: 체크박스 재시작 시 True 초기화 | **완료** — `_restore_ui_prefs` 내 `_on_symbol_changed` → `_update_symbol_label` 교체 |
| chk_slack 중복 시그널 제거 | **완료** — `main.py` L4128~4130 `stateChanged` → `_save_ui_prefs` 연결 제거 |
| 5/19 실세션 동작 확인 | **미완료** — 체크박스 해제 후 재시작 시 복원 여부 확인 |

### 수정 파일 (57차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `_restore_ui_prefs()` L7814: `_on_symbol_changed` → `_update_symbol_label` |
| `main.py` | L4128~4130: `chk_slack.stateChanged` → `_save_ui_prefs` 중복 연결 제거 |

### 5/19 확인 사항

1. 중패널_Auto·우패널_Auto 체크 해제 후 재시작 → 해제 상태로 복원되는지 확인
2. `ui_prefs.json`에 `mid_auto_enabled: false, right_auto_enabled: false` 유지되는지 확인

---

## 2026-05-18 (56차) — 상단 배지 5종 점검·수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| FLAT 배지 (`lbl_pos`) | **완료** — `update_position()`에서 LONG/SHORT/FLAT 색상 갱신 |
| 위클리 배지 (`lbl_cycle`) | **완료** — `_calc_cycle_badge()` 월/목 양방향, `[월]위클리`/`[목]위클리`/`[목]월간` 형식 |
| 감마스퀴즈 배지 (`lbl_gamma`) | **완료** — `_update_gamma_badge()` 추가, GEX 기반 3상태 판정, 초기값 "감마 —" |
| NEUTRAL 배지 (`lbl_regime`) | **완료** — 툴팁 "매분 갱신" 오류 수정 + `usd_krw` 인수 누락 수정 |
| L2 배지 (`lbl_l2_halt`) | **완료** — dead code 제거 + 툴팁 400만원 기준 명시 |
| 배지 실세션 동작 확인 | **미완료** — 5/19 장중 첫 확인 예정 |

### 수정 파일 (56차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `update_position()`: `lbl_pos` 갱신 추가 |
| `dashboard/main_dashboard.py` | `_calc_cycle_badge()`: 월/목 양방향 만기 계산 |
| `dashboard/main_dashboard.py` | `update_option_chain()` + `_update_gamma_badge()` 신규, 초기값 "감마 —" |
| `dashboard/main_dashboard.py` | `lbl_regime` 툴팁 "08:55 1회 수집 당일 고정" 수정 |
| `dashboard/main_dashboard.py` | `lbl_l2_halt` 툴팁 Tier4 400만원 명시 |
| `main.py` | `update_supply_macro()` 호출에 `usd_krw` 인수 추가 |
| `strategy/profit_guard.py` | `_tier.check()` dead code `if max_qty == 0:` 제거 |

### 5/19 기동 확인 사항

1. FLAT → LONG 진입 시 배지 색상 전환 (녹색=LONG, 빨강=SHORT, 회색=FLAT)
2. 위클리 배지: 오늘이 월요일(만기일) → `● [월]위클리 만기일` 표시
3. 09:05 이후 감마스퀴즈 배지: "감마 —" → "감마스퀴즈"/"감마플립"/"중립" 전환
4. 시스템 로그에서 `[Regime] ... | USD/KRW=±X.XX` (0.00이 아닌 실수치)

---

## 2026-05-18 (55차) — 옵션 체인 스냅샷 파이프라인 완성 + B115 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| OptionChainSnapshot 클래스 구현 | **완료** — `collection/options/option_chain_snapshot.py` |
| main.py STEP 4 통합 | **완료** — refresh·get_features·dashboard 업데이트 연결 |
| 대시보드 옵션 섹션 UI | **완료** — freshness bar + PCR/GEX 카드 5개 |
| B115 Fix: front month 만기 계산 | **완료** — `_filter_front_month` 2번째 목요일 기준 만기 달 skip |
| 옵션 체인 실데이터 검증 | **미완료** — 5/19 장중 첫 검증 예정 |

### 수정 파일 (55차)

| 파일 | 변경 내용 |
|---|---|
| `collection/options/option_chain_snapshot.py` | 신규 — OptionChainSnapshot 클래스 (5분 폴링 PCR/ATM OI/GEX) + B115 _filter_front_month 만기 계산 |
| `main.py` | import 추가, `__init__` 초기화, `connect_broker` initialize(), STEP4 refresh/get_features/dashboard update, `reset_daily()` |
| `dashboard/main_dashboard.py` | DivergencePanel 옵션 섹션 + freshness bar + update_option_chain() + MainDashboard 위임 메서드 |

### 5/19 기동 확인 사항

1. `[OptionChain] COM 초기화 완료` — connect_broker() 완료 직후 로그
2. `[OptionChain] front month=2606 (만기=2026-06-11)` — B115 수정 동작 확인
3. 09:05 이후 `[OptionChain] 갱신 ... avail=True` — 실데이터 수집 확인
4. 대시보드 하단 옵션 섹션 실수치 표시 (PCR≠1.000, GEX≠0.0B)

---

## 2026-05-18 (54차) — B112/B114 개선

### 현재 상태

| 항목 | 상태 |
|---|---|
| B112 Fix: stale broker_sync_reason 클리어 | **완료** — FLAT 전환 시 `_broker_sync_last_error = "flat after exit"` |
| B114 진단: IntrabarTPSchedule 로그 추가 | **완료** — QTimer 스케줄 시 price/pos/p1p2p3 WARN 출력 |
| B114 진단: IntrabarTPCheck 가드 로그 추가 | **완료** — pending 존재/FLAT/price=0 각 케이스 WARN 출력 |
| B114 근본 원인 수정 | **미완료** — 5/19 세션 로그 확인 후 원인 특정 필요 |
| B113: ProfitGuard 재시작 소멸 | **유지** — 시험가동 중, 모의투자 완료 후 수정 예정 |

### 수정 파일 (54차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` (L4803~4807) | `_ts_on_chejan_event`: 청산 완전 체결 후 FLAT이면 `_broker_sync_last_error = "flat after exit"` |
| `main.py` (L930~943) | `_clear_pending_order`: QTimer 스케줄 시 `[IntrabarTPSchedule]` WARN 로그 추가 |
| `main.py` (L4029~4041) | `_ts_intrabar_tp_check`: 가드 실패 케이스별 WARN 로그 추가 |

### 5/19 기동 확인 사항

1. **B112**: 청산 후 EntryAttempt 로그에서 `broker_sync_reason='flat after exit'` 확인
2. **B114**: TP1 체결 직후 `[IntrabarTPSchedule]` 로그 출력 여부 확인
3. **B114**: `[IntrabarTPCheck]` 또는 `[IntrabarTPCheck] skip:` 로그로 근본 원인 특정
4. **53차 Fix**: `[IntrabarTPCheck]` 정상 발동 + TP1 완료 후 TP2 즉시 점검 확인 (5/18 세션 미적용, 5/19 첫 검증)

---

## 2026-05-18 (53차) — 2차 목표 도달 후 미청산 버그 2종 수정

### 배경

실세션 중 2차 목표(TP2)가 "도달"로 표시됐음에도 청산이 실행되지 않는 현상 제보. 코드 분석으로 두 가지 독립 버그 확인 및 수정 완료.

### 근본 원인 요약

| 버그 | 원인 |
|---|---|
| TP2·TP3 "도달" 오표시 | `pending_stage` 무시 — TP1 주문중임에도 상위 TP에 초록 "도달" 표시 → 운영자 혼동 |
| Pending 해소 후 TP 1분 지연 | `_clear_pending_order()` 이후 다음 분봉 파이프라인까지 대기 → TP3 위 가격이어도 최대 1분 청산 불가 |

### 현재 상태

| 항목 | 상태 |
|---|---|
| Fix 1: `_ts_intrabar_tp_check` 신규 함수 | **완료** — EXIT_PARTIAL 해소 즉시 300ms QTimer로 TP 재점검 |
| Fix 2: `_clear_pending_order` 수정 | **완료** — `_cleared_kind` 캡처 후 EXIT_PARTIAL·EXIT_MANUAL_PARTIAL 시 intrabar check 스케줄 |
| Fix 3: 대시보드 pending 표시 개선 | **완료** — `pending_stage` 기반 해당 TP 행에 "주문중", 미발동 상위 TP는 "대기" |
| 5/19 실세션 동작 확인 | **미완료** — `[IntrabarTPCheck]` 로그 + 대시보드 상태 확인 필요 |

### 수정 파일 (53차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `_clear_pending_order()`: `_cleared_kind` 캡처 + EXIT_PARTIAL 해소 시 300ms 후 `_ts_intrabar_tp_check` QTimer 스케줄 |
| `main.py` | `_ts_intrabar_tp_check()` 신규 함수 — pending 없음 확인 후 TP1→TP2→TP3 순차 재점검 |
| `main.py` | `TradingSystem._intrabar_tp_check = _ts_intrabar_tp_check` 등록 |
| `dashboard/main_dashboard.py` | 청산 트리거 배지 — `pending_stage` 기반으로 주문중 TP 행 강조 + 상위 미발동 TP "대기" 교체 |

### 5/19 기동 확인 사항

1. **`[IntrabarTPCheck]` 로그**: TP1 체결 완료(pending 클리어) 직후 300ms 내 로그 출력 확인
2. **대시보드 상태**: TP1 주문중(pending_stage=1) 시 TP2·TP3 행이 "도달"(초록) 아닌 "대기"로 표시되는지
3. **TP2 즉시 발동**: TP1 완료 후 다음 분봉까지 기다리지 않고 TP2가 바로 발동하는지

---

## 2026-05-18 (52차) — 손익 패널 4종 불일치 수정

### 배경

실세션 중 실시간 잔고(3,006,750원) / 손익 PnL 탭(2,261,018원) / 손익 추이 탭(3,555,000원) / HTS(2,877,000원) 네 패널이 모두 다른 값을 표시. 원인 분석 후 수정 완료.

### 현재 상태

| 항목 | 상태 |
|---|---|
| B109 Fix: `broker_daily_pnl` 포지션 보유 중 오염 차단 | **완료** — `position.status=="FLAT"` 조건 추가 |
| 손익 추이 탭 즉시 갱신 (`_refresh_pnl_history`) | **완료** — FLAT 확인 후 저장 직후 호출 |
| 5/19 실세션 동작 확인 | **미완료** — 다음 장 확인 필요 |

### 수정 파일 (52차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` (L5101~5116) | `upsert_daily_broker_pnl(_today_str, ...)` — `FLAT` 시에만 저장 + 저장 직후 `_refresh_pnl_history()` 호출 |

### 패널별 데이터 소스 정리

| 패널 | 소스 | 특이사항 |
|---|---|---|
| 실시간 잔고 금일손익 | Cybos `CpTd6197` header[6] `today_pnl` | 포지션 보유 중 미실현 포함 가능 |
| 손익 PnL 탭 일일누적 | `position_tracker._daily_pnl_pts × pt_value - commission` | 엔진 메모리, 가장 신뢰 |
| 손익 추이 탭 P/L 원 | `broker_daily_pnl` 테이블 우선, 없으면 `trades.db net_pnl_krw` 합산 | 52차 수정으로 FLAT 시에만 갱신 |
| HTS 금일손익 | Cybos HTS 자체 TR | 수수료 처리 기준 다름 |

---

## 2026-05-18 (51차) — 부분청산 Race Condition 버그 3종 수정

### 배경

실거래 로그에서 `[PNL] 체결진입`만 반복되고 부분청산 로그가 나오지 않는 현상 발생. 코드 분석으로 TP 부분청산 흐름에서 Cybos BlockRequest Race Condition 등 버그 3종 확인 및 수정.

### 현재 상태

| 항목 | 상태 |
|---|---|
| B106 Fix: `_ts_execute_partial_exit()` Race Condition | **완료** — pending 선등록 → 주문 → 실패 시 롤백으로 수정 |
| B107 Fix: `apply_entry_fill()` partial_done 불필요 리셋 | **완료** — 신규 포지션(FLAT→진입)일 때만 리셋, 분할체결·증량 시 보존 |
| B108 Fix: Chejan order_no="" 오탐 매칭 | **완료** — ENTRY/EXIT 방향 교차 검증 추가 |
| 실로그 검증 (10:00 TP1, 10:01 TP2) | **완료** — `[PendingOrder] set` → BlockRequest 중 Chejan 정상 매칭 확인 |

### 수정 파일 (51차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `_ts_execute_partial_exit()`: pending 선등록 후 주문, ret≠0 시 `_clear_pending_order()` 롤백 |
| `main.py` | `_ts_on_chejan_event_cybos_safe()`: order_no="" 매칭 시 direction 교차 검증 (_dir_ok 조건) |
| `strategy/position/position_tracker.py` | `apply_entry_fill()`: `_is_new_position` 플래그 추가, 증량 체결 시 partial_done 보존 |

### 검증 결과 (2026-05-18 실세션)

- 09:59 LONG 4계약 분할체결(1+1+1+1) 진입
- 10:00 **TP1 부분청산 정상 실행** — 1계약 @ 1156.92, +5.43pt ✅
- 10:01 **TP2 부분청산 정상 실행** — 1계약 @ 1160.18, +8.69pt ✅
- 10:04 하드스톱 전량청산 — 2계약 @ 1154.91(평균) ✅
- `[PendingOrder] set`이 `[ChejanFlow] 접수` 보다 먼저 기록됨으로 Race Condition 해소 확인

---

## 2026-05-17 (50차) — 5/15 거래 검토 기반 전략 핵심 수정 6종

### 배경

5/15 거래 리뷰(Deep 분석)에서 이상점 5종·개선안 7종이 도출됨. 5/16~5/17 커밋(40~49차)은 대시보드·Cybos 연동 위주였고 전략 핵심 파일은 미수정. 50차에서 우선순위 순으로 일괄 구현.

### 현재 상태

| 항목 | 상태 |
|---|---|
| CVD/VWAP/OFI 하드게이트 (checklist.py) | **완료** — CORE 3개 중 하나라도 ✗ → Grade X 강제 |
| EXIT 부분체결 즉시 긴급청산 (main.py) | **완료** — stuck 감지 30초→10초 + 반대 포지션 force_exit |
| Hurst 실계산 연결 (feature_builder.py) | **완료** — 60봉 버퍼, ATR 블록 뒤 삽입 (09:40부터 실값) |
| MIN_TRAIN_BARS 3000 한시적 하향 (batch_retrainer.py) | **완료** — 복원 목표 2026-05-26 |
| CB② 2회 강화 (settings.py) | **완료** — CB_CONSEC_STOP_LIMIT 3→2 |
| SizerMatch 로그 (main.py) | **완료** — Sizer 원본 vs 실제 진입 gap 기록 |
| 5/19 모의투자 실검증 | **미완료** — 다음 장 확인 필요 |
| MIN_TRAIN_BARS 5000 복원 | **미완료** — 2026-05-26 이후 |
| CB② 2회 기준 과잉 발동 모니터링 | **미완료** — 2주 관찰 |

### 수정 파일 (50차)

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/checklist.py` | CORE 3개 하드게이트 — pass_count 후 즉시 X등급 반환 |
| `main.py` | EXIT stuck 타임아웃 30s→10s + 반대 포지션 force_exit |
| `main.py` | [SizerMatch] 로그 — `_qty_sizer_raw` 저장 후 진입 직전 gap 출력 |
| `features/feature_builder.py` | `calculate_hurst` import + `_close_history` deque(60) + Hurst 블록 |
| `learning/batch_retrainer.py` | `MIN_TRAIN_BARS` 5000→3000 (주석에 복원 목표일 명시) |
| `config/settings.py` | `CB_CONSEC_STOP_LIMIT` 3→2 |

### raw_data.db 현황 (GBM 학습 소스)

| 항목 | 값 |
|---|---|
| raw_candles | 3,432행 (2026-04-28 ~ 2026-05-15) |
| raw_features | 3,432행 |
| MIN_TRAIN_BARS | **3,000** (한시적, 원래 5,000) |
| 5/19 이후 재학습 | 가능 (3,432 ≥ 3,000) |
| 5,000행 달성 예상 | 2026-05-26경 |

### 주의 — 5/19 기동 확인 필요 사항

1. **Hurst 실값 확인**: 09:40 이후 `hurst=0.5xx` (0.5 이외 값) 로그 확인
2. **GBM 재학습 성공**: `[Retrain] 완료 | N초 | 성공=M/6 호라이즌` 로그 확인
3. **CB② 과잉 발동 여부**: 정상 트레이드 중 2회 손절로 CB 발동 시 파라미터 재검토
4. **[SizerMatch] 로그**: Sizer 제안 vs 실제 진입 gap 원인 추적

---

## 2026-05-16 (43차) — 손익 추이 패널 UI 개선

### 현재 상태

| 항목 | 상태 |
|---|---|
| 소스 선택 체크박스 (순방향/역방향) | **완료** — 탭바 우측 코너 배치 |
| 헤더 `(실행/순)` 표기 제거 | **완료** — 일별·주별·월별 모두 |
| 셀 "실행 xxx / 순 yyy" → 단일 값 | **완료** — `_fmt_val` / `_fmt_single` |
| MDD·샤프·누적 체크박스 연동 | **완료** — `_mdd_sel`, `_sharpe_sel` |
| 요약 카드 (총 손익·MDD) 연동 | **완료** |
| 실 UI 검증 | **미완료** — 다음 기동 시 확인 필요 |

### 수정 파일 (43차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `PnlHistoryPanel`: 체크박스 추가, 헤더 정리, 셀 단일값 표시, 신규 헬퍼 7개 |

---

## 2026-05-16 (42차) — Cybos 잔고 Chejan 버그 수정 4종

### 발견된 버그 근본 원인

```
[발동 체인]
진입 → 잔고 Chejan(gubun=1) 도착
  → sync_from_broker(grade="BROKER") — grade·TP 플래그 덮어씀 [B102, B103]
  → _clear_pending_order() — EXIT pending 파괴 [B101]
  → TP1 체결 Chejan → pending=None → _ts_handle_external_fill
  → remaining_fill > 0 → 반대 방향 MANUAL 포지션 생성
  → 즉시 하드스탑 → record_stop_loss() → CB② 발동 [B100 연관]
  → EmergencyExit.execute() → pending 미등록 → 3건 외부체결 [B104]
```

### 현재 상태

| 항목 | 상태 |
|---|---|
| Fix 1: EXIT pending 보호 (`_ts_sync_from_balance_payload`) | **완료** — main.py |
| Fix 2: TP 플래그 보존 (`sync_from_broker`) | **완료** — position_tracker.py |
| Fix 3: grade 보존 (`sync_from_broker`) | **완료** — position_tracker.py |
| Fix 4: EmergencyExit pending 선등록 | **완료** — emergency_exit.py + main.py |
| 가격 포맷 버그 (`session_recovery_service.py`) | **완료** — `{entry_p:.2f}` / `{exit_p:.2f}` |
| 4종 수정 모의투자 실검증 | **미완료** — 다음 장(2026-05-19) 확인 필요 |

### 수정 파일 (42차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `_ts_sync_from_balance_payload`: EXIT pending 진행 중이면 `_clear_pending_order()` 생략 |
| `main.py` | `EmergencyExit` 초기화: `pending_registrar=self._set_pending_order` 전달 |
| `strategy/position/position_tracker.py` | `sync_from_broker`: 동방향 sync 시 TP 플래그 보존 + grade 보존 |
| `safety/emergency_exit.py` | `pending_registrar` 파라미터 추가 + 발주 전 EXIT_FULL pending 등록 |
| `strategy/runtime/session_recovery_service.py` | 복원 로그 가격 포맷 `{entry_p:.2f}` / `{exit_p:.2f}` 3곳 |

### Fix별 동작 요약

| Fix | 문제 | 해결 |
|---|---|---|
| Fix 1 | 잔고 Chejan이 EXIT pending을 즉시 파괴 | EXIT 계열 pending이면 clear 생략, 로그만 남김 |
| Fix 2 | 동방향 sync가 TP1/2/3_done 플래그 초기화 | `same_side_sync`이면 TP 플래그 유지 |
| Fix 3 | 동방향 sync가 grade=A를 BROKER로 덮어씀 | `same_side_sync`이면 기존 grade 보존 |
| Fix 4 | EmergencyExit 발주 전 pending 미등록 → 비상청산 체결이 외부체결로 분류 | 발주 전 `EXIT_FULL` pending 등록 |

---

## 2026-05-16 (41차) — CB③ 분석 + HORIZON_THRESHOLDS 재보정 + 모니터링·툴팁

### 현재 상태

| 항목 | 상태 |
|---|---|
| HORIZON_THRESHOLDS 재보정 | **완료** — 1200pt 시장 기준 전체 약 1.6× 상향 (FLAT 29~37% 목표) |
| `_log_threshold_monitor()` | **완료** — GBM 재학습 완료 시 + 30분 주기 호출 |
| `_threshold_monitor_tick` | **완료** — main.py line 286 |
| `_CB_TIP` 슬랙 알림 섹션 | **완료** — 5개 트리거 대응표 + 다크박스 포함 |
| `param_title` 피처 윈도우 툴팁 | **완료** — CORE/선택/외부 3색 분류 테이블 |
| `_HZ_TIP` + `hz_title` 연결 | **완료** — 6섹션 툴팁 (호라이즌 개념·threshold·acc·모니터링) |
| GBM 재학습 적용 | **미완료** — 다음날 08:45 기동 시 warmup retrain 자동 발동 예정 |
| ATR 동적 방식 전환 | **미완료** — 정적 재보정 안정화 확인 후 전환 검토 |

### HORIZON_THRESHOLDS 현재값 (2026-05-16 재보정)

| 호라이즌 | 구값 | 신값 | 1200pt 기준 pt |
|---|---|---|---|
| 1m  | 0.0002 | **0.0005** | 0.60pt (12틱) |
| 3m  | 0.0003 | **0.0008** | 0.96pt (19틱) |
| 5m  | 0.0004 | **0.0011** | 1.32pt (26틱) |
| 10m | 0.0006 | **0.0016** | 1.92pt (38틱) |
| 15m | 0.0008 | **0.0022** | 2.64pt (53틱) |
| 30m | 0.0012 | **0.0032** | 3.84pt (77틱) |

> σ_1min≈1.47pt 기준, threshold≈0.4~0.5σ → FLAT 29~37% (3택 랜덤 33% 근접)

### 수정 파일 (41차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | HORIZON_THRESHOLDS 전체 재보정 |
| `main.py` | `_threshold_monitor_tick`, `_log_threshold_monitor()`, GBM 콜백·파이프라인 30분 주기 호출 |
| `dashboard/main_dashboard.py` | `_CB_TIP` 슬랙 섹션, `param_title` 피처 윈도우 테이블, `_HZ_TIP` + `hz_title` 연결 |

### threshold 전파 구조

```
config/settings.py (HORIZON_THRESHOLDS)
  ├── learning/batch_retrainer.py     (학습 라벨 생성)
  ├── learning/prediction_buffer.py   (검증 채점)
  └── learning/target_builder.py      (단독 타겟 계산)
→ settings.py 1곳 수정으로 전파 완료. GBM 재학습 필수.
```

---

## 2026-05-16 (40차) — 장전 시동 흐름 + 슬랙 알림 + 대시보드 체크박스

### 현재 상태

| 항목 | 상태 |
|---|---|
| `pre_market_setup` 타이밍 | **완료** — 08:55 단일 블록 (기존 08:45+08:55 이중 블록 통합) |
| 스냅샷 워밍업 (`_prime_from_snapshot`) | **완료** — `pre_market_setup()` 끝에 선워밍, `start()` 진입 시 skip 로직 |
| GBM 재학습 데몬 스레드 | **완료** — `threading.Thread(daemon=True)` + `QTimer.singleShot(0, _on_gbm_retrain_done)` |
| 08:58 broker sync 선실행 | **완료** — `_pre_sync_attempted` 플래그로 중복 방지 |
| `start_mireuk.bat` 세션 이중 확인 | **완료** — preflight → 3s 대기 → 재확인 |
| 슬랙 알림 (`utils/notify.py`) | **완료** — `_SLACK_ENABLED`, 6개 단계별 함수 추가 |
| `main.py` 슬랙 연동 | **완료** — 기동·장전·첫틱·sync 미검증·연결끊김·90s 지연 |
| 대시보드 `chk_slack` 체크박스 | **완료** — `res_box` 왼쪽 정렬, `ui_prefs.json` 저장·복원 |
| CLAUDE.md 08:55 교정 | **완료** |
| 40차 수정 실검증 | **미완료** — 다음 기동 시 슬랙 알림 수신 + 첫 틱 슬랙 확인 필요 |

### 수정 파일 (40차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | 08:55 통합 블록, 스냅샷 워밍업, GBM 데몬 스레드, 08:58 broker sync, 슬랙 연동 전체, `chk_slack` 연결 |
| `collection/cybos/realtime_data.py` | `start()` — `_last_price > 0`이면 `_prime_from_snapshot` skip |
| `utils/notify.py` | `_SLACK_ENABLED` 플래그 + 제어 함수 + 6개 단계별 알림 함수 |
| `dashboard/main_dashboard.py` | `chk_slack` QCheckBox 추가, `res_box` 왼쪽 정렬, `_save_ui_prefs`·`_restore_ui_prefs` slack 저장/복원 |
| `start_mireuk.bat` | preflight 후 3s + Cybos 세션 재확인 구간 추가 |
| `CLAUDE.md` | 파이프라인 08:45 → 08:55 교정 |

---

## 2026-05-15 (39차) — 선물 롤오버 자동화 전면 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| `_MARKET_SYMBOLS` 동적 생성 | **완료** — `_build_market_symbols()` 기동 날짜 기준 자동 계산, 하드코딩 제거 |
| `set_selected_symbol()` | **완료** — 프로브 후 대시보드 콤보 즉시 동기화 |
| 일반선물(A01xxx) FutureMst 프로브 | **완료** — `get_nearest_normal_futures_code()` 추가 |
| `_resolve_trade_code()` 일반선물 지원 | **완료** — 미니선물과 동일 방식으로 근월물 프로브 + UI 동기화 |
| `check_rollover()` 장중 감시 | **완료** — 60 tick(30분)마다 근월물 재확인, WARNING + UI 갱신 |
| `_rollover_detected` 반복 알림 억제 | **완료** — 감지 후 재탐지 억제, 장 시작 시 초기화 |
| 38차 수정 실검증 | **미완료** — `[NormalProbe/MiniProbe]`, `[CodeRoll]`, `verified=True`, tick #1 확인 필요 |

### 수정 파일 (39차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `_build_market_symbols()`, `_nth_thursday()`, `_next_valid_contracts()`, `_futures_code8()` 추가. `set_selected_symbol()` MireukDashboard + DashboardAdapter |
| `collection/cybos/api_connector.py` | `get_nearest_normal_futures_code()` 추가 (A01xxx FutureMst 프로브) |
| `strategy/runtime/broker_runtime_service.py` | `_resolve_trade_code()` 일반선물 프로브 추가 + UI 동기화. `check_rollover()` 신설 |
| `main.py` | `_scheduler_tick()` 60 tick(30분) 롤오버 감시 + `_rollover_detected` 플래그 |

### 중요 운영 규칙 (39차 추가)

- **심볼 목록은 기동 시 자동 갱신**: `_MARKET_SYMBOLS`는 `_build_market_symbols()` 반환값 → 소스코드 수정 없이 매월/분기 롤오버 반영
- **일반선물도 FutureMst 프로브**: A01xxx(분기물)도 `price > 0` 검증 → UI 저장값 만기 시 자동 교체
- **UI 콤보는 항상 실제 거래 코드**: `_resolve_trade_code()` 확정 후 `set_selected_symbol()` 호출로 UI = 실제 거래 코드

---

## 2026-05-15 (38차) — BlockRequest 데드락 + 롤오버 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| `_run_block_request` COM STA 데드락 | **수정 완료** — `done.wait(0.01)` + `PumpWaitingMessages()` 루프로 교체 |
| `CpTd0723` / `FutureMst` 30초 타임아웃 | **수정 완료** — 메시지 펌핑 후 ~1초 내 완료 예상 |
| 미니선물 만기 롤오버 미처리 | **수정 완료** — `_resolve_trade_code`가 항상 프로브, A0565→A0566 자동 전환 |
| `get_nearest_mini_futures_code` 만기 skip | **수정 완료** — `price > 0` 조건, 만기 코드 자동 건너뜀 |
| broker sync 장중 재시도 | **추가 완료** — startup 실패 시 3분 간격 자동 재시도 |

### 중요 운영 규칙 (Cybos COM)

- **BlockRequest는 메인 스레드 메시지 펌프 필요**: 백그라운드 스레드에서 단독 호출 시 항상 타임아웃. `_run_block_request`가 메인 스레드에서 10ms 간격 펌핑으로 해결.
- **미니선물 코드는 항상 프로브**: 미니선물(A05xxx)은 월물 만기(2차 목요일) 다음날부터 근월물이 바뀐다. UI 저장값을 신뢰하지 않는다.

---

## 2026-05-15 (37차) — 운영 헬스 중앙 패널 추가

### 현재 상태

| 항목 | 상태 |
|---|---|
| 중앙 패널 운영 헬스 | **완료** — `mid_tabs`에 `⚕️ 운영 헬스` 탭 추가 |
| 로그 패널 운영 헬스 | **유지** — 하단 `6 운영 헬스`는 텔레메트리 로그용으로 계속 사용 |
| 중앙 헬스 동기화 | **완료** — `update_runtime_health()`가 로그 패널과 중앙 패널을 동시 갱신 |
| 중앙 헬스 스파크라인 | **완료** — Health Score / 지연 / 품질 3라인 표시 |
| Health Score 계산 | **주의** — 현재는 임시값을 넣고 있어 추후 실제 산식 연결 필요 |

### 운영 판단 포인트

- 이제 헬스 뷰는 로그 창에만 있는 것이 아니라 중앙 패널에서도 즉시 확인 가능하다
- 운영자가 보는 요약 뷰와 로그성 뷰를 분리해 가독성을 확보했다
- 다음 보완점은 중앙 헬스의 `Health Score`를 실제 런타임 계산값으로 바꾸는 것이다

## 2026-05-15 (36차) — Cybos 자동 로그인 버그 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| 모의투자 선택 창 탐지 (`candidates=[]` 버그) | **수정 완료** — `EnumChildWindows` 4차 탐색 추가, 자식 창 생성 케이스 대응 |
| min_wait 중 즉시 감지 | **수정 완료** — 20초 맹목적 대기 → 매초 탐지/즉시 클릭 |
| 공지사항 팝업 처리 | **신설 완료** — `_dismiss_notice_popups(timeout=10)` 모의투자 접속 직후 호출 |
| 로그인 흐름 문서화 | **완료** — `docs/CYBOS_AUTOLOGIN_FLOW.md` 작성 |
| 4차 탐색 실 동작 확인 | **미완료** — 다음 로그인 실행 시 `[INFO] 4차 탐지:` 로그 출력 여부 확인 필요 |
| 공지사항 팝업 제목 패턴 확인 | **미완료** — 실제 팝업 제목이 "공지사항" 외 다른 패턴이면 `NOTICE_KEYWORDS` 확장 필요 |

### 핵심 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `scripts/cybos_autologin.py` | `_find_mock_dialog_hwnd`, `_click_mock_access_in_window`, `_close_dialog_window`, `_dismiss_notice_popups` 신설. min_wait 매초 탐지 적용. |
| `docs/CYBOS_AUTOLOGIN_FLOW.md` | 전체 로그인 흐름 다이어그램 + 단계별 상세 문서 |

---

## 2026-05-15 (35차) — 운영 헬스 고도화 + 하루 운용 검증 준비

### 현재 상태

| 항목 | 상태 |
|---|---|
| Degraded auto/manual 차단 정책 분리 | **완료** — auto/manual 각각 독립 옵션으로 동작 |
| 헬스 설정 핫리로드 | **완료** — `settings.py` 변경 시 재시작 없이 반영 |
| 헬스 스파크라인 확장 | **완료** — Health Score + 지연 + 품질 3라인 표시 |
| 핫리로드/차단 하네스 검증 | **완료** — `validate_health_policy_hotreload.py` 결과 PASS |
| 감사문서 ##10 하루 운용 체크리스트 | **완료** — 항목 추가 및 07:38 사전점검 반영 |
| 브로커 startup sync 상태 | **주의** — `verified=False`, `block_new_entries=True` (07:38 기준) |
| 헬스 탭 수동 UI 진입 확인 | **미완료** — 운영자 화면 확인 필요 |

### 운영 판단 포인트

- 지금 상태에서 자동진입은 브로커 sync 미검증 조건으로 차단되어 있음
- Day10-2/Day11 장중 검증(10.2~10.5)은 sync 정상화 이후 판정하는 것이 유효함
- 핫리로드 정책 검증은 하네스 기준으로는 정상이나, 장중 실제 로그 동작 확인이 추가 필요

## 2026-05-14 (34차) — 진입관리 탭 시간대 가이드 UI 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| 진입관리 설명줄 | **완료** — 현재 zone, 시간 범위, `conf≥`, `size×`, 진입 허용 여부를 실시간 표시 |
| 시간대 버튼 칩 | **완료** — `GAP_OPEN`~`EXIT_ONLY` 6구간을 색상 칩으로 시각화, 현재 구간 강조 |
| A/B/C 등급 버튼 권장 표시 | **완료** — 현재 zone의 `size_mult` 기준으로 권장 등급을 자동 강조 |
| 수동 선택 구분 | **완료** — 권장(`권장`)과 사용자 선택(`선택`)을 동시에 구분 표시 |
| 만기일/FOMC 오버라이드 배지 | **완료** — UI 설명줄에 `만기일 적용중` / `만기 전일 적용중` / `FOMC 적용중` 배지 노출 |
| 실제 UI 런타임 확인 | **미완료** — PyQt 화면에서 시인성과 배지 위치 확인 필요 |

### 구현 메모

- 표시값 소스는 정적 상수가 아니라 `TimeStrategyRouter.route()` + `apply_expiry_override()` + `apply_fomc_override()` 체인이다
- 권장 등급은 `ENTRY_GRADE`의 `size_mult`와 현재 zone `size_mult`의 최근접 매핑으로 계산한다
- 자동 생성 런타임 상태 파일 `data/session_state.json`은 변경되었지만 세션 카운터 증가 성격이라 코드 변경 사항과 분리 관리한다

## 2026-05-14 (33차) — Cybos 장외 startup crash 완화

### 현재 상태

| 항목 | 상태 |
|---|---|
| 장외 Cybos startup crash | **1차 완화 적용 완료** — 장외에는 `RealtimeData.start()`와 수급 `QTimer`를 시작하지 않도록 가드 추가 |
| MacroFetcher startup noise | **완화 완료** — yfinance 실패 콘솔 노이즈 억제, 15분 cooldown, fallback key 정렬 |
| 잔고 `QTableWidget` stylesheet warning | **부분 완화** — 문제 구간 stylesheet 단순화. 재실행으로 완전 해소 여부 확인 필요 |
| 장외 launcher 재검증 | **미완료** — 최신 패치 후 `start_mireuk.bat` 야간 재실행 확인 필요 |

### 로그 기준 결론

- 장중 재기동(`2026-05-14 14:09:23`)은 `startup sync -> realtime start -> tick/hoga 수신`까지 정상 진행
- 야간 재기동(`2026-05-14 20:18:19`, `20:20:15`, `20:26:13`)은 공통적으로 `CpTd0723`와 `FutureMst` timeout 뒤 `-1073741819` 종료
- 따라서 현재 판단은 **장외 timeout 상태에서 실시간 구독까지 강행하던 경로가 가장 위험한 지점**이라는 것

### 남은 리스크

- `CpTd0723` / `FutureMst` timeout 자체의 근본 원인은 아직 미해결
- 장외 guard로 crash는 막을 가능성이 높지만, 장중 reconnect나 pre-open 구간에서 같은 패턴이 재현되는지는 아직 미검증
- `QTableWidget` parse warning이 다른 테이블 stylesheet에서 계속 날 수 있음

---

## 2026-05-14 (32차) — 2차 감사 P3 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/dynamic_sizing.py` | M5: `MIN_COMBINED_FRACTION=0.12` — 7팩터 곱 0.12 미만 시 `_blocked()` 반환 |
| `config/settings.py` | M6: `TIME_ZONES`에 `GAP_OPEN("09:00","09:05")` 추가 (v6.6) |
| `utils/time_utils.py` | M6: `get_time_zone()` GAP_OPEN 분기 추가 / 만기일: `get_monthly_expiry_date()` · `days_to_monthly_expiry()` · `is_expiry_day()` · FOMC 목록 · `is_fomc_day()` 추가 |
| `strategy/entry/time_strategy_router.py` | M6: `GAP_OPEN` 파라미터 추가 / 만기일: `apply_expiry_override()` · `apply_fomc_override()` 추가 |
| `model/multi_horizon_model.py` | M7: `_scaler_fitted_at` 기록 + `predict_proba()` 내 90분 경과 경고 + |z|>4 극단 피처 경고 |

### P3 완료 현황 (2차 감사 기준)

| 항목 | 상태 |
|---|---|
| M5 Dynamic Sizing 0 수렴 | ✅ 완료 — MIN_COMBINED_FRACTION=0.12 차단 |
| M6 09:00-09:05 미분류 | ✅ 완료 — GAP_OPEN 구간 신설 (min_conf=0.67, size×0.5) |
| M7 StandardScaler 노후화 | ✅ 완료 — 90분 경과 WARNING + 극단 z-score 경고 |
| 만기일/FOMC 대응 부재 | ✅ 완료 — 월물 만기일 함수 + FOMC 목록 + TimeRouter 오버라이드 |

---

## 2026-05-14 (31차) — 2차 감사 P1 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `utils/time_utils.py` | C3: `KST` 타임존 상수 + `now_kst()` 헬퍼 추가, 모든 내부 `datetime.now()` 교체 |
| `safety/circuit_breaker.py` | C3: `now_kst()` 사용 |
| `strategy/exit/time_exit.py` | C3: `now_kst()` — 15:10 강제청산 KST 보장 |
| `safety/kill_switch.py` | C3: `now_kst()` |
| `strategy/entry/meta_gate.py` | C3: `now_kst()` |
| `strategy/profit_guard.py` | C3: `now_kst()` |
| `strategy/entry/time_strategy_router.py` | C3: `now_kst()` |
| `strategy/exit/exit_manager.py` | C3: `now_kst()` |
| `strategy/position/position_tracker.py` | C3: `now_kst()` (20곳) |
| `strategy/entry/staged_entry.py` | C3: `now_kst()` |
| `config/settings.py` | M1: `GBM_MIN_SAMPLES_LEAF = 10` 상수 추가 |
| `model/multi_horizon_model.py` | M1: `GBM_MIN_SAMPLES_LEAF` 임포트 → 파라미터 통일 |
| `learning/batch_retrainer.py` | M1: `GBM_MIN_SAMPLES_LEAF` 임포트 → 10으로 통일 (기존 20 → 10) |
| `main.py` | H1: silent except 8곳 → logger.debug/warning 추가 |
| `main.py` | H4: `_last_gate_signals`, `_last_gate_direction` 저장 + `_on_core_feature_fail` 메서드 |
| `main.py` | H4: `_post_exit()` → EnsembleGater 피드백 연결 |
| `features/feature_builder.py` | H2: CVD/VWAP/OFI 연속 실패 카운터 + 3회 시 ERROR 경보 + `_on_core_fail` 콜백 |
| `model/ensemble_gater.py` | H4: `record_outcome()` + `_load_weights()` + `_save_weights()` — 온라인 학습 |
| `model/ensemble_decision.py` | H4: `record_trade_outcome()` 위임 메서드 추가 |

### P1 완료 현황 (2차 감사 기준)

| 우선순위 | 항목 | 상태 |
|---|---|---|
| P1 (C3) | KST 타임존 전체 적용 | ✅ 완료 — 10개 핵심 모듈 `now_kst()` 교체 |
| P1 (H1) | `except Exception: pass` 장애 은폐 제거 | ✅ 완료 — 8곳 logger 추가 |
| P1 (H2) | CORE 피처 0 폴백 → ERROR 경보 | ✅ 완료 — 3회 연속 실패 시 ERROR + Slack |
| P1 (M1) | GBM 파라미터 불일치 | ✅ 완료 — `GBM_MIN_SAMPLES_LEAF=10` 공유 상수 |
| P1 (H4) | EnsembleGater 고정 가중치 | ✅ 완료 — 거래 결과 기반 온라인 학습 (lr=0.005) |

---

## 2026-05-14 (30차) — 감사 기반 전체 버그 수정 + 스텁 모듈 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/checklist.py` | P0: FLAT 방향 조기 반환 (X등급, auto_entry=False) — FLAT→AUTO SHORT 잠재 버그 차단 |
| `features/feature_builder.py` | P1: safe bar.get() + 9개 계산 블록 try/except + 기본값 fallback |
| `features/technical/ofi.py` | P1: `flush_minute()` 말미 `_prev_*=None` 리셋 — stale delta 방지 |
| `safety/circuit_breaker.py` | P1: ATR 버퍼 중앙값 기반 지속 급등 감지 추가 (`import statistics`) |
| `main.py` | P2: 더미 매크로→실 API 연동, `_send_kiwoom_*`→`_send_broker_*` rename 13개소, Dead Code 제거, 스텁 5개 연결 |
| `collection/broker/kiwoom_broker.py` | P2: InvestorData에 api 주입 |
| `strategy/position/position_tracker.py` | P2: 인코딩 깨짐 4개소 수정 |
| `features/technical/cvd.py` | P3: 보합 틱 delta=0 (Long 바이어스 제거) |

### 신규 생성 파일

| 파일 | 내용 |
|---|---|
| `features/macro/macro_feature_transformer.py` | VIX·SP500 등 9개 정규화 피처 |
| `learning/self_learning/daily_consolidator.py` | 시간대별 정확도 → confidence 패널티 |
| `learning/self_learning/drift_adjuster.py` | SGD alpha 동적 조정 (드리프트 감지) |
| `collection/options/pcr_store.py` | 외인 PCR 20분 롤링 저장소 |
| `features/options/option_features.py` | PCR → 6개 ML 피처 |

### 삭제된 파일

| 파일 | 이유 |
|---|---|
| `strategy/entry/entry_manager.py` | Dead Code — main.py에서 한 번도 인스턴스화 안 됨. Kiwoom 전용 API 서명으로 Cybos 미호환. |

### 현재 피처 파이프라인 (STEP 4 갱신 후)

```
investor_data.get_features()  → supply_feats
pcr_store.update(supply_feats)
macro_fetcher.get_features()  → macro_transformer.transform() → _macro_feats
option_feat_calc.transform(pcr_store.get_features()) → _option_feats
feature_builder.build(bar, supply_demand=supply_feats, macro_data=_macro_feats, option_data=_option_feats)
```

### 현재 일일 마감 (15:40) 파이프라인 갱신 후

```
daily_consolidator.consolidate()          ← 시간대별 패널티 계산
drift_adjuster.record_accuracy(acc)       ← SGD alpha 갱신
online_learner.set_alpha(new_alpha)       ← 즉시 반영
pcr_store.reset_daily()                   ← 신규 추가
```

---

## 2026-05-14 (29차) — CB HALT 사후 조사 + 모델 신뢰도 개선

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `main.py` | B84: EXIT pending stuck Chejan 유실 대응 (`expected_remaining` 비교) |
| `main.py` | B86: CB HALT 중 수동 청산 불가 수정 (pending 강제 소멸 분기) |
| `main.py` | C10: `record_accuracy(confidence=_conf)` 전달 |
| `main.py` | C11: `_warmup_retrain_pending` 플래그 + STEP 3 `force=True` 재학습 트리거 |
| `safety/circuit_breaker.py` | B85: `_trigger_halt()` → `emergency_exit` 콜백 호출 추가 |
| `safety/circuit_breaker.py` | C10: `_high_conf_wrong_streak` 카운터 + 동적 임계값 (0.35→0.50) |
| `model/multi_horizon_model.py` | C09: `CONF_CLIP = 0.92` 극단 확률 클리핑 |
| `config/settings.py` | C10 상수 3개: `CB_HIGH_CONF_WRONG_LIMIT`, `CB_HIGH_CONF_THRESHOLD`, `CB_ACCURACY_MIN_30M_STRICT` |

### 현재 안전장치 상태

| 항목 | 상태 |
|---|---|
| CB② 연속 손절 → emergency_exit | ✅ 정상 (이번 회차 B85 수정) |
| CB③ 정확도 저하 → emergency_exit | ✅ 정상 (이번 회차 B85 수정) |
| CB③ 과신 오류 동적 임계값 | ✅ 신규 구현 (C10) |
| GBM 극단 확률 클리핑 (0.92) | ✅ 신규 구현 (C09) |
| 세션 재시작 후 GBM 즉시 재학습 | ✅ 신규 구현 (C11) |
| EXIT pending stuck 자동 복구 | ✅ 정상 (이번 회차 B84 수정) |

### 주요 설계 변경

- **CB HALT 발동 범위 확대**: CB⑤(API 지연)만 emergency_exit 호출하던 것을 CB②/③ 발동 시에도 즉시 청산 (B85)
- **세션 재시작 보호**: 재시작 직후 구식 GBM으로 인한 방향 고착 방지. `_broker_sync_block_new_entries=True` 유지 중에 재학습 수행 → 완료 후 진입 허용 (C11)
- **conf 상한선**: GBM이 학습 분포 외 입력에서 conf=1.000 반환하는 현상 → 0.92로 클리핑, 초과분 나머지 클래스 균등 분배 (C09)

---

## 2026-05-14 (28차) — L2 배지 UI + 모드 필터

### 신규 구현

| 파일 | 내용 |
|---|---|
| `strategy/profit_guard.py` | `_TierGate.halt_threshold`, `_TierGate.halt_tier` 프로퍼티 + `ProfitGuard.get_l2_halt_info()` 메서드 |
| `dashboard/main_dashboard.py` | `self.lbl_l2_halt` 배지 + `update_l2_halt_badge()` 메서드 |
| `main.py` | STEP 9 후 L2 halt 매분 동기화 + STEP 7 모드필터 2순위 추가 |

### 진입 로직 우선순위 (최종 정의)

```
신호 발생 (STEP 6)
    ↓
[1순위] L2 ProfitGuard 체크 ← 수익 보존 (시스템)
    ├─ 1-1: Trail Stop (L1)
    ├─ 1-2: Tier Gate (L2) ← L2 halt latch
    ├─ 1-3: Afternoon Mode (L3)
    └─ 1-4: Profit CB (L4)
    ↓
    통과했다면 ↓
[2순위] 모드 필터 체크 ← 신호 강도 (사용자)
    ├─ "auto": A급만
    ├─ "hybrid": A, B급 (기본값)
    └─ "manual": A, B, C급
    ↓
    둘 다 통과 → 진입 ✅
    L2 차단 → 진입 불가 (원인: [차단] L2 ...)
    모드필터 차단 → 진입 불가 (원인: [모드필터] ... 불일치)
```

### 현재 진입관리 탭 상태

| UI 요소 | 구현 상태 | 기능 |
|---|---|---|
| Auto ON/OFF | ✅ 완벽 | 자동/수동 진입 전환, 로그 기록 |
| A/B/C 등급진입 버튼 | ✅ 이번 회차 완성 | 모드별 등급 필터링 (L2 다음) |
| 역방향 진입 | ✅ 완벽 | 신호 반대로 진입 |

### L2 Tier Gate 최종 설정 이해

```
금일 수익 < 50만원
  → L2 적용 안 함 (기본 min_mult 미정)
  → 진입관리 탭 모드 필터만 작용

금일 수익 50~100만원
  → L2: min_mult=0.6 (C급 이상)
  → 진입관리 탭: 모드 필터 적용
  → 예: C급+B모드 → L2 통과 → 모드 차단 ❌

금일 수익 100~200만원
  → L2: min_mult=1.0 (A급만)
  → 진입관리 탭: 모드 필터 적용
  → 예: B급+B모드 → L2 차단 ❌

금일 수익 ≥ 200만원
  → L2: max_qty=0 (거래 완전 중단)
  → 대시보드: 🔒 L2 중단 (N.NM원) 배지 표시
  → 진입 불가능 (L1~L4 모두)
```

### 배지 표시 규칙

| 배지 | 위치 | 조건 | 표시 내용 |
|---|---|---|---|
| CB 배지 | 상단 중앙 | CB 상태 | "CB NORMAL" / "⛔ CB HALT" / "⏸ CB PAUSE" |
| **L2 배지** | **CB 오른쪽** | **L2 halt 활성** | **🔒 L2 중단 (N.NM원)** |
| L2 배지 | CB 오른쪽 | L2 halt 비활성 | (숨김) |

---

## 2026-05-14 (27차) — Cybos 옵션 지표 수집

### 신규 파일

| 파일 | 내용 |
|---|---|
| `scripts/probe_cp_option_code.py` | CpOptionCode 체인 조회 (4,624종목) |
| `scripts/probe_cp_calc_opt_greeks.py` | CpCalcOptGreeks 그릭스 계산 (속성 할당 + Calculate 방식) |
| `scripts/probe_cp_option_mo.py` | OptionMo 실시간 OI 구독 (장중 필요) |
| `scripts/verify_option_mst_fieldmap.py` | OptionMst HeaderValue 필드맵 교차 검증 |
| `scripts/collect_option_metrics.py` | PCR/GEX/ATM OI 통합 수집 (48종목 2.9초) |
| `AGENTS.md` | 한글판 에이전트 가이드 |

### 핵심 결과 (2026-05-13 장후, 2606월물)

| 지표 | 값 | 해석 |
|---|---|---|
| PCR (OI) | 0.54 | 콜 우위, 강세 |
| ATM PCR | 1.04 | 중립 |
| Total GEX | +35.3B원 | 감마 롱 |

### 확정 필드맵

HV(6)=행사가, HV(13)=잔존일수, HV(93)=현재가, HV(97)=체결량, HV(99)=OI, HV(37)=전일OI, HV(109)=Delta, HV(110)=Gamma, HV(111)=Theta, HV(113)=Rho. HV(17)≠spot(날짜), HV(15)≠ATM(콜/풋코드).

### 다음

1. OptionMo 장중 검증 (4단계)
2. collection/options/ + features/options/ 신설 → Mireuk 피처 통합
3. PCR/GEX 시계열 안정성 검증
4. OptionMst 폴링 최적화

---

## 2026-05-13 (26차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dev_memory/SESSION_LOG.md` | 작업스케줄러 순서의존 로그인 충돌(B83) 원인/개선안 기록 |
| `dev_memory/CURRENT_STATE.md` | 26차 상태 반영 |
| `dev_memory/NEXT_TODO.md` | 외부 키움 리포지토리 구현/검증 TODO 추가 |
| `dev_memory/DECISION_LOG.md` | D58/B83 설계결정/버그 기록 |

### 핵심 운영 상태

- `futures` 리포지토리 내부 코드는 이번 턴에서 변경하지 않았고, 개선안은 외부 키움 프로젝트 적용 항목으로 정리했다.
- 실행순서 충돌의 실질 해법은 절대좌표/클립보드 매크로 제거 및 창 객체 기반 자동화 전환이다.
- 보안상 키움 계정정보는 스크립트 하드코딩 금지, 환경변수/보안 저장소 주입 방식으로 관리해야 한다.

---

## 2026-05-13 (25차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `strategy/position/position_tracker.py` | TP3/3단계 부분청산, `initial_quantity`, `partial_3_done`, stage plan/target helpers, `trailing_anchor_price`, `peek_saved_entry_time()` 추가 |
| `strategy/position/position_tracker.py` (`sync_from_broker`) | same-side broker sync 시 `entry_time`, `stop_price`, `trailing_anchor_price`, 원진입 수량 보존 |
| `strategy/position/position_tracker.py` (`update_trailing_stop`) | 2ATR 구간 trailing stop을 `current_price`가 아니라 `trailing_anchor_price` 기준으로 추적 |
| `dashboard/main_dashboard.py` | 청산관리 패널 `트레일링 기준`/`현재 실행 스톱` 분리, 3차 목표 34% 및 원진입 수량 기준 stage 게이지 반영 |
| `dashboard/main_dashboard.py` (`sync_active_trade`) | 진입마커 sync 시 기존 `entry_ts` 보존, 새 진입/방향전환 때만 신규 마커 생성 |
| `main.py` | 청산관리 패널 payload에 `trail_basis`, `stage_plan`, `pt_value` 전달 |
| `main.py` | stuck exit timeout 시 브로커 잔고 우선 재검증 후 pending 유지/해제 |
| `main.py` | 외부진입 동기화 직후 `250ms / 1200ms` 잔고 재조회 트리거 추가 |

### 설계/운영 규칙

- same-side broker sync는 trailing stop을 되돌리지 않는다.
- 청산관리 패널의 `트레일링 기준`은 `현재 실행 스톱` 복제값이 아니라 별도 기준값이다.
- 진입마커는 진입시각 고정이다. active position sync나 startup restore가 들어와도 기존 `entry_ts`를 우선 보존한다.
- 외부체결은 Chejan만 신뢰하지 않고, 다계약 외부진입/청산 뒤에는 브로커 잔고 재조회로 최종 수량을 보정한다.

### 현재 운영 상태

- 청산관리 탭은 `TP1/TP2/TP3 = 33/33/34`를 원진입 수량 기준으로 유지하며, 수동 부분청산 후에도 stage 완료 상태를 유지한다.
- `PositionTracker.stop_price`는 trailing update로 유리한 방향으로만 이동해야 하며, same-side broker sync 시 초기 하드스톱으로 되돌아가지 않도록 보강돼 있다.
- 분봉차트 active trade는 진입 분봉에 마커가 고정되고, 점선 span만 현재 분봉까지 연장되는 모델을 사용한다.
- 외부체결(HTS/수동) 다계약 사례는 로컬 체결 누락 가능성이 있어, 후속 잔고 refresh 로그로 브로커 수량 일치 여부를 확인해야 한다.

## 2026-05-13 (24차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_marker`) | 청산 아이콘 배지 중심 렌더링에서 텍스트 중심 렌더링으로 단순화 |
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_stamp` 신설) | 청산봉 위치 식별용 소형 스탬프(T/S/P) 마커 추가 |
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_marker`) | TP/SL/PX 색상 팔레트 재정의 + 텍스트 오프셋 조정 |

### 핵심 안전 규칙 (24차 추가)

- **청산 시각정보 우선순위**: 봉 위치 식별(스탬프) + 텍스트 정보(태그/손익/시각)를 함께 제공한다.
- **색상 의미 고정**: TP는 녹색 계열, SL은 적색 계열, PARTIAL/PX는 중성 회색 계열로 고정한다.

---

## 2026-05-13 (23차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` (`run_minute_pipeline`) | 청산 패널 payload 확장: `pending_*`, `time_exit_countdown_sec` 전달 |
| `main.py` (`_ts_push_exit_panel_now` 신설) | Chejan 체결 직후 청산 패널 즉시 갱신 (매분 갱신 대기 제거) |
| `main.py` (`_clear_pending_order`, `_ts_on_chejan_event_cybos_safe`) | pending 소멸/체결 처리 직후 즉시 패널 갱신 호출 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | 배지 enum 기반 상태 렌더링 + 시간청산 카운트다운 표시 + pending EXIT `주문중 n/m` 표시 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | ENTRY pending 시 1/2/3차 목표 배지 `산정중` 강제, 목표 도달 판정 잠금 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | tp1/tp2/tp3 비정상값(<=0) 방어 정규화 |
| `main.py` (`connect_broker`) | 브로커 동기화 직후 포지션 상태 기반 탭 모드 즉시 정렬 |
| `dashboard/main_dashboard.py` (`UiAutoTabController`) | 수동 탭 전환 유휴 판정에 `hasFocus`/`focusWidget` 반영 |

### 핵심 안전 규칙 (23차 추가)

- **청산 패널 실시간성**: Chejan 체결 이벤트 후 상태 배지는 즉시 갱신한다. 분봉 주기 갱신만으로 주문상태를 표현하지 않는다.
- **ENTRY pending 목표 배지 정책**: ENTRY pending 동안 1/2/3차 목표 배지는 `산정중`만 허용. `도달/완료` 표시는 금지.
- **탭 모드 정렬**: 브로커 동기화 직후 포지션 상태와 탭 모드(청산/진입)는 즉시 일치시킨다.

---

## 2026-05-13 (22차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` (Cybos/Kiwoom 핸들러) | `or unfilled_qty == 0` 제거 — 부분체결 pending 조기 소멸 방지 (B75) |
| `main.py` (`_set_pending_order` 후) | `optimistic_opened`/`partial_fill_count` 플래그 추가 — 낙관적 오픈 분할체결 VWAP 보정 (B76) |
| `main.py` (`_ts_handle_exit_fill`) | `_ts_agg_exit_fill` / `_ts_build_agg_exit_result` 헬퍼 + `is_last_fill` 분기 — EXIT 분할체결 CB/Kelly 단1회 기록 (B77) |
| `main.py` (`_on_manual_exit_requested`) | `_set_pending_order`를 `_send_kiwoom_exit_order` 전으로 이동, 실패 시 `_clear_pending_order` 롤백 (B78-race) |
| `main.py` (`_ts_on_chejan_event_cybos_safe`) | `is_final_fill` 폴백: `status=""` + `fill_qty>0` + `fill_price>0` → 체결로 간주 (B78-status) |
| `main.py` (`_ts_handle_external_fill`) | 최종 청산 후 `_ts_force_balance_flat_ui` + `QTimer(250ms, 1200ms)` 추가 (B78-external) |
| `main.py` (`_ts_push_balance_to_dashboard`) | pending EXIT 존재 시 합성 1계약 행 생성 억제 (B78-synthetic) |
| `dashboard/main_dashboard.py` | `WindowStaysOnTopHint` 제거 — 미륵이 창 최상위 고정 해제 |

### 핵심 안전 규칙 (22차 추가)

- **pending 등록 순서**: 청산 주문 `_set_pending_order` → `_send_order` 순서 (역전 금지). 실패 시 즉시 `_clear_pending_order`
- **Cybos unfilled_qty**: 항상 0 반환 → `or unfilled_qty == 0` 조건 사용 금지. `filled_qty >= qty`만으로 완결 판정
- **EXIT 분할체결 통계**: `is_last_fill`에서만 CB/Kelly 기록. 중간 체결은 로그만

---

## 2026-05-13 (21차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py:1776` | `candle` → `bar` NameError 수정 (B72) |
| `main.py:connect_broker()` | `_futures_code` 확정 후 `position._loaded_futures_code`와 비교 — 불일치 시 강제 FLAT + CRITICAL 로그 (B73) |
| `main.py:_ts_on_chejan_event_cybos_safe` | 체결 이벤트 code ≠ `_futures_code` 시 WARNING + 포지션 반영 거부 (B73) |
| `strategy/position/position_tracker.py` | `_futures_code`/`_loaded_futures_code` 필드, `set_futures_code()`, `force_flat()` 추가. `_save_state()`에 `futures_code` 저장, `load_state()`에서 복원 (B73/D50) |
| `collection/cybos/realtime_data.py` | 캔들 dict에 `"code": self.code` 추가 (B74) |
| `dashboard/main_dashboard.py` | `MinuteChartCanvas._instrument_code` 추가. `on_candle_closed()` — 코드 전환 시 차트 초기화. `_trim_to_last_price_group()` + `reload_today()` 필터 (B74/D51) |

### 핵심 안전 규칙 (21차 추가)

- **재시작 시 코드 불일치 → 강제 FLAT**: `connect_broker()` 완료 후 저장 포지션 코드와 `_futures_code` 비교. 불일치면 포지션 CRITICAL 초기화. HTS에서 해당 종목 수동 확인 필수
- **체결 코드 이중 검증**: `_ts_on_chejan_event_cybos_safe`에서 payload code ≠ `_futures_code` 시 포지션 반영 거부
- **봉차트 코드 전환 감지**: 실시간 캔들에 `code` 포함. `on_candle_closed()`에서 코드 변경 감지 시 기존 캔들 초기화

### 현재 운영 상태

- 오늘 발생한 A0666/A0565 불일치 사고: HTS에서 두 포지션 수동 처리 필요 (모의투자)
  - A0666 SHORT @ 1922.80 — 미청산 상태
  - A0565 LONG @ 1177.3 — 실수로 생성됨
- 미니선물(A0565) 선택 후 재시작 → `[PositionCodeMismatch]` 로그 + 강제 FLAT으로 추가 사고 방지
- 봉차트: 다음 정상 세션부터 단일 종목 캔들만 표시됨

---

## 2026-05-13 (20차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` | 8자리 UI 코드 정규화 (`A0565000→A0565`, 끝 "000" 제거). 미니선물 fallback을 `get_nearest_mini_futures_code()`(FutureMst 프로브)로 교체 |
| `collection/cybos/api_connector.py` | `CpUtil.CpKFutureCode` 사용 완전 제거. `get_nearest_mini_futures_code()` FutureMst 프로브 방식으로 재구현 |
| `collection/broker/cybos_broker.py` | `get_nearest_mini_futures_code()` 위임 메서드 추가 |
| `scripts/check_cybos_realtime.py` | `--mini` 플래그를 FutureMst 프로브 방식으로 교체. FutureMst name 표시 추가 |
| `dashboard/main_dashboard.py` | `WindowStaysOnTopHint` 추가 — 미륵이 UI를 항상 최상위 창으로 유지 |
| `scripts/cybos_autologin.py` | "공지사항" 다이얼로그 자동 닫기 추가. `_handle_mock_select_dialog()` 레거시 함수 제거 |

### 핵심 지식 (Cybos COM 코드 체계 — 2026-05-13 실증)

- `CpUtil.CpFutureCode`: KOSPI200 **일반선물(A01xxx)** 만 열거
- `CpUtil.CpKFutureCode`: **코스닥150 선물(A06xxx)** 만 열거 — 절대 미니선물 탐색에 사용 금지
- **KOSPI200 미니선물(A05xxx)**: 열거 COM 없음. `Dscbo1.FutureMst` 프로브만 가능
- 코드 규칙: `A05 + 연도끝자리 + 월(hex)` — 2026-05=A0565, 2026-06=A0566, 2026-12=A056C
- Cybos COM 실시간 구독(FutureCurOnly)은 **5자리 코드만 수락**. 8자리 코드(A0565000)는 무음 실패

### 현재 운영 상태 (20차 시점 기록)

- 미니선물 실시간 구독: `A0565` 5자리 코드로 정상 구독
- 봇 재시작 후 `[DBG CK-3] 근월물 코드=A0565 is_mini=True` 확인 필수

---

## 2026-05-12 버그 수정 (19차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dashboard/panels/profit_guard_panel.py` | 수익보존 탭 Apply 설정을 `data/profit_guard_prefs.json`에 저장/복원하도록 영속화 추가 |

### 핵심 변경

- `Apply` 시 `ProfitGuardConfig`를 JSON으로 즉시 저장
- 패널 생성 시 저장값을 UI에 먼저 반영
- `set_profit_guard()` 호출 시 저장값이 있으면 guard 기본값 대신 저장 config를 우선 주입
- 저장 파일이 없거나 파싱 실패 시 기본 config로 안전 폴백

### 현재 운영 상태

- 수익보존 탭의 L1/L2/L3/L4 하단 설정값은 재시작 후에도 유지된다.
- 영속 파일 경로: `data/profit_guard_prefs.json`

---

## 2026-05-12 버그 수정 (18차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `scripts/cybos_autologin.py` | `_handle_mock_select_dialog()` 내 `sys.exit(0)` → `return True` — STEP 5 연결 대기 루프 실행되도록 수정 |
| `start_mireuk.bat` | 자동 로그인 성공 후에도 에러 출력되는 `%ERRORLEVEL%` 지연 확장 버그 → `!ERRORLEVEL!` 로 수정 |
| `dashboard/main_dashboard.py` | 종목코드·시장구분 선택값을 `data/ui_prefs.json` 에 저장/복원 (`_save_ui_prefs`, `_restore_ui_prefs`) |
| `config/constants.py` | `get_contract_spec()` 추가 — 일반선물/미니선물 계약 스펙(`pt_value`, `tick_size`, `tick_value`) 반환 |
| `main.py` | UI 선택 종목코드 기준으로 계약 스펙 확정 후 `_pt_value` 를 런타임 전역에 전파 |
| `strategy/position/position_tracker.py` | 인스턴스별 `pt_value` 기반 손익/수수료 계산 |
| `strategy/entry/position_sizer.py` | `pt_value` 기반 리스크 계산 + 미니선물 최소 3계약 규칙 |
| `strategy/entry/entry_manager.py` | 주문 코드 하드코딩 제거, 현재 선택 종목코드 사용 |
| `strategy/exit/exit_manager.py` | 청산 주문 코드/손익 KRW 계산을 현재 계약 스펙 기준으로 통일 |
| `collection/kiwoom/investor_data.py` | 수급 TR 조회 종목코드를 현재 선택 코드와 동기화 |
| `collection/cybos/investor_data.py` | 브로커 인터페이스 호환용 `set_futures_code()` 추가 |
| `dashboard/panels/profit_guard_panel.py` | `sqlite3.Row.get()` Python 3.7 미지원 → `_rows_to_dicts()` 변환 + `_run_simulation_inner()` 분리 + try/except 래핑 |

### 주요 패턴 (재사용 가능)

- **`sqlite3.Row` → `dict` 변환**: Python 3.7에서 `row.get()` 미지원. `dict(row)` 로 변환 후 사용. `_rows_to_dicts()` helper 참고.
- **Windows CMD 지연 확장**: 중첩 `IF` 블록 내 `%ERRORLEVEL%` 는 파싱 시점 고정. 반드시 `!ERRORLEVEL!` 사용 (`SETLOCAL EnableDelayedExpansion` 전제).
- **Qt blockSignals**: 콤보 복원 중 save-during-restore 피드백 루프 방지에 필수.
- **계약 스펙 단일 소스**: 일반/미니선물 구분은 브로커 기본 근월물이 아니라 최종 UI 선택 종목코드에서 한 번만 결정해야 함.

### 현재 운영 상태

- `data/ui_prefs.json` 은 `version`, `market`, `symbol_code`, `symbol_text` 구조로 저장된다.
- 시작 직후 기본 콤보값이 저장 파일을 덮어쓰던 버그는 `_update_symbol_label()` 분리로 해결됐다.
- 현재 저장 파일 기준 마지막 선택값은 `KOSPI200 미니선물 / A0565000` 이다.
- 미니선물 선택 시 손익/사이징/주문 코드/수급 조회 코드가 모두 동일 선택 코드 기준으로 동기화된다.

---

## 2026-05-12 수익 보존 가드 시스템 (ProfitGuard 4-Layer)

### 신규 파일

| 파일 | 역할 |
|---|---|
| `strategy/profit_guard.py` | 4-Layer 수익 보존 핵심 로직 |
| `dashboard/panels/profit_guard_panel.py` | "💰 수익 보존" 대시보드 탭 |

### 4-Layer 설계

| 레이어 | 클래스 | 발동 조건 | 파라미터 기본값 |
|---|---|---|---|
| L1 | `_TrailingGuard` | peak ≥ trail_activation_krw(200만) + 현재 < peak × (1-trail_ratio(35%)) | trail_activation=2_000_000, trail_ratio=0.35 |
| L2 | `_TierGate` | 구간별 최소 size_mult 미달 시 차단, 400만+ = max_qty=0 (완전 정지) | tiers: 0/100/200/300/400만 |
| L3 | `_AfternoonMode` | 오후 기준 시간 이후 + 수익 발생 + 진입 횟수 초과 | cutoff_hour=13, max_trades=3 |
| L4 | `_ProfitCB` | 수익 중 N연속 손실 | profit_cb_consec_loss=2, trigger_threshold=150만 |

### main.py 연결 포인트

| 위치 | 동작 |
|---|---|
| `__init__()` | `self.profit_guard = ProfitGuard()` 초기화 |
| STEP 7 진입 전 | `is_entry_allowed(daily_pnl, size_mult)` → grade=X 강제 적용 |
| `_post_exit()` | `on_trade_close(pnl_krw, daily_pnl)` → L4 CB 갱신 |
| `_execute_entry()` | `on_entry()` → L3 오후 카운터 갱신 |
| `daily_close()` | `reset_daily()` → 전체 상태 초기화 |
| `_refresh_pnl_history()` | `dashboard.refresh_profit_guard(pnl, trades)` |

### 대시보드 탭 구성 ("💰 수익 보존")

- **상태 섹션**: L1~L4 레이어 배지 + 핵심 지표 5개 + PnL DNA 시각화 (pyqtSignal 연동)
- **설정 섹션**: QSlider(trail_ratio) + QSpinBox(임계값·기준) + Apply/Reset 버튼
- **비교 섹션**: 챔피언 vs 챌린저 6행 테이블 + 차단 거래 목록
- **제안 섹션**: 3-variant 챌린저 제안표 + 황금 시간대 막대 차트 + 차단 로그

### simulate() 활용

`ProfitGuard.simulate(trades, cfg)` 정적 메서드로 과거 거래 리스트를 대입해 챔피언(가드 없음) vs 챌린저(가드 적용) 총손익·MDD·차단수를 비교할 수 있다.

---

## 2026-05-12 챔피언-도전자 시스템 (Phase C-1 ~ C-8 + 레짐 전문가 확장)

### 신규 파일 목록

| 파일 | 역할 |
|---|---|
| `challenger/__init__.py` | 패키지 init |
| `challenger/variants/__init__.py` | 패키지 init |
| `challenger/variants/base_challenger.py` | 추상 기저: `ChallengerSignal`, `ChallengerTrade`, `BaseChallenger` |
| `challenger/challenger_db.py` | SQLite CRUD (`challenger.db`) — 6개 테이블 |
| `challenger/challenger_registry.py` | 도전자 풀 + 레짐별 챔피언 포인터 관리 |
| `challenger/challenger_engine.py` | Shadow 실행 오케스트레이터 (매분 훅, <5ms 목표) |
| `challenger/promotion_manager.py` | 전역 승격 + 레짐 전문가 승격 (수동 승인 필수) |
| `challenger/variants/cvd_exhaustion.py` | CVD 탈진 도전자 (A) |
| `challenger/variants/ofi_reversal.py` | OFI 반전 도전자 (B) |
| `challenger/variants/vwap_reversal.py` | VWAP 반전 도전자 (C) |
| `challenger/variants/exhaustion_regime.py` | 탈진 레짐 특화 도전자 (D) |
| `challenger/variants/absorption.py` | 흡수 감지 도전자 (E, FutureJpBid 필요) |
| `features/technical/cvd_exhaustion.py` | CVD 탈진 피처 계산기 |
| `features/technical/ofi_reversal.py` | OFI 반전 피처 계산기 |
| `dashboard/panels/__init__.py` | 패키지 init |
| `dashboard/panels/challenger_panel.py` | 도전자 모니터 패널 (레짐 전문가 승위표 + 전체 성과) |

### 핵심 설계 결정

- **레짐 전문가 풀**: `탈진 → [A_CVD, C_VWAP, D_EXHAUSTION]` / `추세·횡보·혼합 → CHAMPION_BASELINE` / `급변장 → []`
- **승격 기준**: 레짐 내 거래 수 기반 (`min_regime_trades: 20`) — 달력일 무관
- **자동 승격 금지**: Shadow 1위 변경 시 대시보드 WARNING만 발송, 실거래 전환은 수동 승인
- **레짐 챔피언 게이트** (`main.py [§20]`): `탈진` 레짐에서 챔피언=None이면 진입 차단

### DB 스키마 (`challenger.db`)

```
challenger_signals       — 매분 신호 (regime 컬럼 포함)
challenger_trades        — 가상 거래 (regime 컬럼 포함)
challenger_daily_metrics — 전체 일별 집계
challenger_regime_metrics— 레짐별 누적 집계 (trade_count 기반 승격 판단)
regime_rank_history      — 레짐별 1위 변경 이력
champion_history         — 챔피언 교체 이력
```

### main.py 연결 포인트

| 위치 | 동작 |
|---|---|
| `__init__()` | `ChallengerEngine` + `PromotionManager` 초기화 (실패 시 None) |
| STEP 9 이후 | `challenger_engine.run_shadow()` — 5ms 가드 포함 |
| STEP 6 [§20] | 레짐 챔피언 게이트 — 챔피언=None 레짐 진입 차단 |
| `daily_close()` | `update_daily_metrics()` — 레짐별 순위 계산 + WARNING 발송 |
| `DashboardAdapter` | `set_challenger_engine()` — 패널에 엔진 주입 |

### 잔여 연결 작업

- `탈진` 레짐 챔피언이 특정 도전자로 승격됐을 때, 해당 도전자의 신호를 앙상블 `direction`으로 오버라이드하는 로직 (현재: 앙상블 신호 유지 + 로그만)
- `AbsorptionChallenger` — `FutureJpBid` 호가 구독 연결 (`update_hoga()` 훅)
- `탈진` 레짐 피처 (`cvd_exhaustion`, `ofi_reversal_speed`) feature_builder 실데이터 검증

---

## 2026-05-11 Cybos Plus 리팩토링 완료 (브로커 전환 마일스톤)

미륵이의 데이터 수집·자동매매 백엔드가 **키움 OpenAPI+ → Cybos Plus(대신증권)** 으로 전면 리팩토링됐다.

| 구분 | 이전 (키움) | 현재 (Cybos Plus) |
|---|---|---|
| 실시간 틱 | `OPT50029` SetRealReg | `Dscbo1.FutureCurOnly` Subscribe |
| 호가 | `FID` 기반 실시간 | `CpSysDib.FutureJpBid` Subscribe |
| 잔고 | `OPW20006` TR | `CpTrade.CpTd0723` BlockRequest |
| 일일손익 | `OPW20003/7/8` TR | `CpTrade.CpTd6197` BlockRequest |
| 주문 | `SendOrderFO` | `CpTrade.CpTd6831` BlockRequest |
| 체결 이벤트 | `OnReceiveChejanData` | `Dscbo1.CpFConclusion` Subscribe |
| 투자자 수급 | `opt10059`, `opt50008` | **`CpSysDib.CpSvrNew7212` (idx0=1) 확정** — 선물/콜/풋 투자자별 순매수 제공 |
| 선물 스냅샷 | `OPT10001` | `Dscbo1.FutureMst` BlockRequest |
| 브로커 팩토리 | `KiwoomBroker` 하드코딩 | `create_broker()` → 기본 `cybos` |

### 11차 세션에서 추가된 것 (2026-05-11)

- `collection/cybos/api_connector.py`: `_probe_investor_tr()` 헬퍼 + `request_investor_futures()` / `request_program_investor()` 다중 후보 실구현
- `collection/cybos/investor_data.py`: `_open_interest`, `program_arb`, `program_nonarb` 필드 추가 및 `get_panel_data()` 확장
- `collection/cybos/realtime_data.py`: `_last_oi` — `FutureCurOnly` 헤더 14번 미결제약정 실시간 저장
- `dashboard/main_dashboard.py`: `DivergencePanel`에 **선물 투자자 수급** 섹션 추가 (외인/개인/기관 순매수 + 프로그램 차익/비차익 + 미결제약정 2×3 그리드)
- `main.py`: `_fetch_investor_data()`에서 `realtime_data._last_oi` → `investor_data._open_interest` 동기화

### 12차 세션에서 추가된 것 (2026-05-11)

- `collection/cybos/api_connector.py`:
  - `_FUTURES_INVESTOR_NAME_MAP` 추가 (한글 투자자명 → INVESTOR_KEYS)
  - `request_investor_futures()` candidates 1순위: `CpSysDib.CpSvrNew7212 [(0,1)]`
  - New7212 전용 파싱 분기: row[3]=선물, row[6]=콜, row[9]=풋 순매수
  - `request_program_investor()` candidates: `Dscbo1.CpSvr8119`, `Dscbo1.CpSvrNew8119` 추가. 전체 0 시 skip.
- `collection/cybos/investor_data.py`:
  - `fetch_futures_investor()`: call_nets/put_nets → `_call/_put` 반영, `option_flow_supported` 자동 활성화
  - `get_panel_data()`: rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias **하드코딩 0 → 실제값** [B54 수정]
  - 상태 텍스트: option_flow_supported 시 자동 갱신
- `dashboard/main_dashboard.py`: 역발상 신호 색상 반전 (`'매수'`→빨간색, `'매도'`→초록색) [D33]
- `config/constants.py`: `CORE_FEATURES` `"ofi_imbalance"` → `"ofi_norm"` [B55 수정]
- 신규 스크립트: `scripts/run_cybos_investor_discovery.py`, `scripts/_probe_7212_dates.py`, `scripts/_probe_8119_fields.py`

### 잔여 검증 항목

- `_probe_8119_fields.py` 장 중(09:00~15:30) 실행 → `Dscbo1.CpSvr8119` h[0~5] 레이아웃 확인
- 실제 파이프라인 매분 업데이트 시 투자자 수급 데이터 흐름 확인 ("대기" → 실수치 전환)
- 장중 `FutureCurOnly` 분봉 timestamp 진행 확인
- `CpTd6831` 모의 주문 체결 end-to-end 검증
- `CybosInvestorRaw 후보 없음` 09:00~10:44 갭 원인 조사 (7건 거래가 모두 이 구간에서 발생)

---

## 2026-05-12 버그 수정 현황

| 버그 | 파일 | 상태 |
|---|---|---|
| MetaConf `loss="log_loss"` (sklearn 1.0.2 호환성) | `learning/meta_confidence.py` | ✅ 수정 완료 |
| 계좌번호 Kiwoom 잔여값 `7034809431` | `config/secrets.py` | ✅ 수정 완료 (gitignore, 미커밋) |
| ExitCooldown 중복 로그 (2회/청산) | `main.py` | ✅ 수정 완료 |
| CB HALTED 이후 Sizer 계속 실행 | `main.py` | ✅ 수정 완료 |
| TRADE.log 한글 깨짐 3곳 | `strategy/position/position_tracker.py` | ✅ 수정 완료 |
| `liquidation_eval=0` 대체 시 경고 없음 | `collection/cybos/api_connector.py` | ✅ 수정 완료 |
| `CybosInvestorRaw 후보 없음` 분당 WARNING 폭주 | `collection/cybos/api_connector.py` | ✅ 수정 완료 (레이트리밋 INFO, 10분 간격) |
| `profit_rate 이상값` 반복 WARNING 폭주 | `collection/cybos/api_connector.py` | ✅ 수정 완료 (`>200%`만 WARNING, 나머지 레이트리밋 INFO) |
| `BalanceUI/BalanceRefresh` 진단 로그 WARNING 과다 | `main.py` | ✅ 수정 완료 (반복성 로그 레이트리밋 INFO) |

### 2026-05-12 경고 재분류 운영 원칙

- 반복성 진단 로그는 INFO(레이트리밋)로 유지하고, 장애성/조치 필요 이벤트만 WARNING 이상으로 유지한다.
- 현재 적용 범위:
  - `CybosInvestorRaw ... 후보 없음`
  - `CybosDailyPnl profit_rate 이상값`
  - `BalanceUI/BalanceRefresh`의 주기성 상태 로그
- WARNING 유지 항목 예시:
  - 브로커 요청 실패(`request returned None`)
  - 필수 입력 누락(`empty account number`)
  - CB/주문 불일치/강제 리스크 이벤트

### MetaConf 오류 인과관계 (2026-05-12 장 중 확인)

```
MetaConf loss="log_loss" 미지원 오류 (sklearn 1.0.2)
→ 6개 호라이즌 × 모든 분봉 학습 실패
→ SGD 온라인학습 미동작 (weight 44%→10%→30% 진동)
→ 메타 신뢰도 보정 없는 앙상블
→ 30분 정확도 19% (CB 임계 35% 미달)
→ CB ③ 10:20:59 당일 정지
```

---

## 2026-05-11 Cybos balance / daily pnl / exit UI state

| Item | Current status |
|---|---|
| Meta confidence training | invalid/ragged feature vectors are filtered before fit/buffer; repeated `MetaConf` shape error is no longer observed in restart logs |
| Position sizing balance source | `PositionSizer` now consumes the latest broker balance summary instead of relying on the old fixed `100,000,000` KRW fallback |
| Cybos daily pnl summary | `CpTd6197` is wired into broker balance flow and logs validation details into `SYSTEM.log` |
| Source of truth for Cybos summary mapping | raw `SYSTEM.log` / `CpTd6197` headers are authoritative; HTS is reference-only |
| Current validated Cybos header mapping | `1=예탁현금`, `2=익일가예탁현금`, `5=전일손익`, `6=금일손익`, `9=청산후총평가금액` |
| Current mock-environment observation | `header 2 == header 9`, `header 5 == 0` |
| Dashboard balance refresh UX | account panel now uses `잔고 새로고침` and `F5` for balance-only refresh |
| Final exit UI sync | on confirmed final exit to `FLAT`, dashboard balance rows are now cleared immediately before broker refresh retries |

### Current operational interpretation

- If HTS and Cybos raw summary look different, trust the logged `CpTd6197` payload first.
- A stale balance row after exit is treated as a UI sync defect, not as proof that the position is still open.
- Broker refresh after final exit is intentionally retried because Cybos COM timing can lag immediately after fill confirmation.

## 2026-05-10 Cybos Plus status update

| Item | Current status |
|---|---|
| Broker abstraction | `main.py` now runs through `create_broker()` and can launch either Kiwoom or Cybos broker backends |
| Cybos connection | `CybosAPI` can connect successfully on 32-bit Python + pywin32 with active CybosPlus SignOn |
| Cybos balance sync | `CpTd0723` startup sync works; empty mock balance is interpreted as `FLAT` |
| Cybos snapshot | `FutureMst` field mapping has been corrected against live snapshot output |
| Cybos realtime wiring | `FutureCurOnly` and `FutureJpBid` subscription wrappers are implemented and startup successfully |
| Cybos order/fill wiring | `CpTd6831` order path and `CpFConclusion` fill event path are implemented, but full live mock validation is still pending |
| Cybos account selection | runtime now falls back to the currently signed-on Cybos account if `config/secrets.py` contains an account not present in the active broker session |
| Investor flow on Cybos | still placeholder / zero-data implementation |
| Test launcher | `start_mireuk_cybos_test.bat` available for safe Cybos-only trial runs without changing default Kiwoom startup |
| Session checker | `scripts/check_cybos_session.py` available for connection/balance/snapshot/realtime/order smoke tests |

### Cybos-specific known gaps

- Live market verification is still incomplete because the latest trial run was performed on `2026-05-10`, a Sunday, with market state `99`.
- Dashboard stylesheet parsing warnings are still present during startup and should be separated from broker/runtime debugging.
- Server label compatibility currently returns a Kiwoom-compatible `"0"` into main flow to avoid false mock-only branches; this should be replaced with a Cybos-native label strategy later.

## 2026-05-08 최신 반영 - 장마감 자동종료/봉차트 UX 보강
| 항목 | 현재 상태 |
|---|---|
| 당일 자동종료 재실행 방지 | 같은 날짜에 자동종료가 이미 끝난 뒤 수동 재시작해도 `daily_close()`와 `_auto_shutdown()`이 다시 실행되지 않도록 복구/가드 이중 방어 적용 |
| 자동종료 상태 복원 | `data/session_state.json`의 `auto_shutdown_done_date`가 오늘이고 장마감 이후면 `_daily_close_done = True`까지 함께 복원 |
| 차트 우측 여백 | 봉차트/분차트 마지막 봉 오른쪽에 10봉 크기 패딩을 줘서 마커와 라벨이 가장자리에 붙지 않음 |
| 진입 마커 시인성 | LONG/SHORT 진입 마커를 더 큰 배지형 스타일로 변경하고, 겹침 회피 로직 추가 |
| LONG/SL 라벨 분리 | `LONG` 라벨은 항상 위쪽, `SL` 라벨칩은 항상 아래쪽으로 더 강하게 분리 |
| 봉차트 단축키 | 단축키 재입력 시 봉차트 윈도우가 닫히는 토글 방식으로 변경 |

### 현재 운영 해석

- 장마감 자동종료는 이제 "당일 1회성 작업"으로 더 강하게 고정되어, 수동 재시작이 후속 종료를 다시 트리거하지 않도록 설계됐다.
- 봉차트는 단순 조회창이 아니라 진입/손절 맥락을 빠르게 읽는 운영 도구로 방향을 더 분명히 잡았다.
- 특히 `LONG` 진입과 `SL` 마커가 같은 봉에 붙는 상황에서 위/아래 레이어를 강제로 분리해 장중 판독 부담을 줄였다.

### 아직 운영 확인 필요한 항목

- 같은 날짜 `15:40` 이후 수동 재시작 시 자동 종료 알림/프로그램 종료가 재실행되지 않는지 확인 필요
- 실제 장중 데이터에서 진입/손절 마커가 여러 개 겹칠 때 현재 충돌 회피 강도가 충분한지 확인 필요
- 봉차트 단축키 토글이 포커스 상태와 무관하게 일관되게 동작하는지 확인 필요

---

## 2026-05-08 최신 반영 - 청산관리 고도화

| 항목 | 현재 상태 |
|---|---|
| 1계약 TP1 처리 | 더 이상 `TP1(전량)`으로 바로 끝나지 않음. `본절보호 / 본절+alpha / ATR 기반 보호이익` 중 선택한 보호전환 모드가 적용됨 |
| TP1 보호전환 UI | 청산관리 탭에서 클릭형 버튼 3개로 선택 가능. 각 버튼에 설명 툴팁 부착 완료 |
| 보호전환 설정 저장 | `data/session_state.json`의 `tp1_single_contract_mode`로 저장/복원 |
| 수동청산 버튼 | 청산관리 탭 `33% / 50% / 전량 청산` 버튼이 실제 주문으로 연결됨 |
| 1계약 수동청산 예외 | 1계약에서 `33%` 또는 `50%` 클릭 시 자동으로 `전량청산`으로 승격 |
| 수동 부분청산 후처리 | `EXIT_MANUAL_PARTIAL` pending kind로 분리되어 자동 TP1/TP2 단계 처리와 충돌하지 않음 |
| 한글 표시 안정화 | 신규 청산관리 탭 문자열은 유니코드 이스케이프 기반으로 넣어 인코딩 깨짐 재발 가능성을 낮춤 |

### 현재 운영 해석

- 청산관리 탭은 이제 상태 표시만 하는 패널이 아니라, TP1 보호전환 설정과 수동청산 실행까지 담당하는 운영 패널이다.
- 1계약 기대값 악화의 핵심이던 `TP1 전량청산` 구조는 제거되었고, 같은 1계약이라도 보호방식을 장중에 바꿔 비교할 수 있다.
- 수동청산은 시장가 기준이므로, 사용 목적은 "전략 청산 대체"보다는 "운영 개입용 안전장치"에 가깝다.

### 아직 남은 확인 사항

- 실제 장중에 TP1 보호전환 3모드가 각각 의도한 스톱 위치로 이동하는지 검증 필요
- `33% / 50% / 전량 청산` 버튼 클릭 후 Kiwoom 체결과 dashboard PnL 갱신이 일관되게 들어오는지 검증 필요
- 1계약 상태에서 `33% / 50%` 클릭 시 WARN/TRADE 로그에 전량승격 의도가 충분히 드러나는지 추가 확인 필요

---

## 2026-05-08 최신 반영 - 역방향진입 실행 오버레이 / 순방향 학습 방화벽

| 항목 | 현재 상태 |
|---|---|
| 역방향진입 토글 | 진입관리 패널 상단에 `역방향 진입` 토글 추가 완료. 자동진입 판단에만 적용되고 수동진입 버튼에는 적용되지 않음 |
| 원신호/실행신호 표시 | 진입관리 패널에 `원신호`, `실행신호` 동시 표시 완료 |
| 로그 반영 | `TRADE`, `SIGNAL` 로그에 `원신호`, `실행신호`, `역방향진입=ON/OFF` 기록 완료 |
| 세션 유지 | `data/session_state.json`에 `reverse_entry_enabled` 저장/복원 완료 |
| 손익 PnL 카드 | `실행 / 순방향` 손익을 동시에 표시하도록 확장 완료 |
| 손익 추이 탭 | 일별/주별/월별 표와 요약 카드에 `실행 / 순` 병기 완료 |
| trades 저장 구조 | `raw_direction`, `executed_direction`, `reverse_entry_enabled`, `forward_*` 컬럼 저장 완료 |
| 학습/통계 방화벽 | 등급 통계, 레짐 통계, 추이 통계, daily PF, daily close snapshot이 순방향 손익 기준으로 동작하도록 수정 완료 |

### 현재 운영 해석

- 순방향 시그널은 전략 본체다.
- 역방향진입은 전략 변경이 아니라 `최종 실행 오버레이 + PnL 비교 수단`이다.
- 따라서 수집/학습/통계/효과검증은 순방향 기준을 유지하고, UI와 주문 실행에서만 역방향 결과를 분리해 본다.

### 남아 있는 확인 포인트

- 실제 UI에서 `역방향진입` ON/OFF 후 진입관리 패널 문구가 기대대로 바뀌는지 확인 필요
- 실제 청산 1회 이상 후 손익 PnL 카드와 손익 추이 탭의 `실행 / 순방향` 값이 모두 채워지는지 확인 필요
- 효과검증 패널 수치가 역방향 실행 손익에 오염되지 않는지 다음 세션 실거래/모의 로그로 최종 검증 필요

## 운영 환경

| 항목 | 값 |
|---|---|
| Python | 3.7 32-bit (`py37_32`) |
| 선물 분봉 TR | OPT50029 (수정 완료 — 구: OPT10080) |
| 모드 | 모의투자 (실전 미전환) |

---

## Phase 완료 현황

| Phase | 코드 | 검증 상태 |
|---|---|---|
| Phase 0 — 설계·인프라 | ✅ | ✅ 완료 |
| Phase 1 — 핵심 시스템 | ✅ | ⏳ 모의계좌 실시간 동작 확인 필요 |
| Phase 2 — 안전장치·백테스트 | ✅ | ⏳ CB 5종 테스트 + 26주 WF 데이터 필요 |
| Phase 3 — 알파 강화 | ✅ | ⏳ 실데이터 정확도 검증 필요 |
| Phase 4 — 차별화 (RL·베이지안·뉴스) | ✅ | ⏳ 실거래 데이터 검증 필요 |
| Phase 5 — 실전 운영 | — | 미진입 |
| Phase 6 — 알파 리서치 봇 | ✅ (유전자 진화 완료) | ⏳ main.py 연결 미완 |

---

## 2026-05-08 세션 주요 수정 (6차) — PnL 승수 수정 + CB③ 개선 + 진입 게이트 보강

### 핵심 변경 사항

**버그 수정 2건 (수익률 직결)**

| 버그 | 원인 | 수정 파일 |
|---|---|---|
| **[B64] PnL 2× 과대 계산** | `FUTURES_MULTIPLIER = 500_000` — KOSPI200 선물 승수는 250,000원/pt | `config/constants.py` FUTURES_MULTIPLIER·FUTURES_TICK_VALUE 수정, `FUTURES_PT_VALUE` 신설. `main.py` 전수 교체 |
| **[B65] 수수료 미반영** | `close_position()` / `partial_close()` / `apply_exit_fill()`에서 pnl_krw 계산 시 수수료(왕복 ~79,500원/계약) 미차감 | `position_tracker.py` — `_calc_commission()` 추가, 3개 청산 경로 모두 적용. `FUTURES_COMMISSION_RATE = 0.000015` settings.py에 추가 |

**CB③ 개선 2건**

| 항목 | 수정 |
|---|---|
| **30m 전용 정확도 피드** | `main.py` STEP 1 `record_accuracy()` 호출에 `v["horizon"] == "30m"` 필터 추가. 기존: 6개 호라이즌 혼합 → 3샘플에서 HALT 발동 |
| **2회 연속 미달 시 HALT** | `circuit_breaker.py` — 1회 미달: WARNING+Slack만, 2회 연속 미달: HALT. 최소 20샘플 확보 후 발동 |

**진입 게이트 보강 3건 (20260508 WARN.log 분석 결과)**

| 조건 | 설명 | 효과 |
|---|---|---|
| **Hurst < 0.45 차단** | `main.py` STEP 7에 `features.get("hurst") >= HURST_RANGE_THRESHOLD` 추가. settings.py에 이미 있던 상수가 실제 게이트에 미연결이었음 | 횡보 레짐 진입 차단 |
| **청산 후 쿨다운** | `_post_exit()` — TP청산 후 2분, 손절청산 후 3분 재진입 금지 (`_exit_cooldown_until`) | 10:13 TP→10:14 즉시재진입, 10:24 스톱→10:25 재진입 패턴 차단 |
| **ATR < 1.0pt 차단** | `ATR_MIN_ENTRY = 1.0` settings.py 추가, STEP 7에 `atr >= ATR_MIN_ENTRY` 조건 추가 | 변동성 부족 구간(ATR=1.37pt) 진입으로 인한 휩쏘 손절 방지 |

### 20260508 WARN.log 분석 요약

| 시각 | 이벤트 | 수정 전 | 수정 후 |
|---|---|---|---|
| 09:34 | CB③ HALT (3샘플, 전 호라이즌 혼합) | 시스템 정지 → 오전 기회 손실 | **방어됨** — 30m 필터 + 20샘플 최소 |
| 10:14 | TP1(10:13) 후 1분 재진입 | 진입 실행 | **차단** — ExitCooldown 2분 |
| 10:24 | 스톱 후 10:25 즉시 재진입 | 진입 실행 → CB② 2/3 도달 | **차단** — ExitCooldown 3분 |

---

## 2026-05-08 세션 주요 수정 (8차) — PnL 기준 통일 + trades.db 정규화 + 잔고/손익 추이 일치화

### 핵심 변경 사항

**PnL 정규화 4건**

| 항목 | 원인 | 수정 |
|---|---|---|
| **`trades.db` 혼합 손익 정규화** | 같은 날짜 거래 안에 `500,000원/pt` 구식 값과 `250,000원/pt - 수수료` 신규 값이 혼재 | `utils/db_utils.py` migration 추가. 기존 `trades.pnl_krw`를 현재 공식으로 일괄 재계산 |
| **정규화 컬럼 추가** | `pnl_krw` 단일 컬럼만으로는 계산 버전/수수료 분리 불가 | `gross_pnl_krw`, `commission_krw`, `net_pnl_krw`, `formula_version` 추가 |
| **거래 저장 경로 통일** | 일부 경로는 구식 저장값을 그대로 INSERT할 위험 | `main.py` 3개 `INSERT INTO trades` 경로 모두 `normalize_trade_pnl()` 사용 |
| **손익 추이 날짜 기준 수정** | 실현손익인데 `entry_ts` 기준 일자 집계 사용 | `fetch_today_trades()`, `fetch_pnl_history()`, `PnlHistoryPanel.refresh()`를 `exit_ts` 기준으로 보정 |

**잔고 패널 안정화 3건**

| 항목 | 수정 |
|---|---|
| **실현손익 fallback 우선순위 보정** | `오늘 정규화 거래합계 -> 마지막 정상 브로커 실현손익 캐시 -> PositionTracker.daily_stats()` 순으로 적용 |
| **TR blank 시 0 덮어쓰기 완화** | `OPW20006` summary blank일 때 직전 정상 브로커 `실현손익`을 당일 캐시로 유지 |
| **재시작 복원 중복 누적 방지** | `_restore_daily_state()`에서 `restore_daily_stats()` 호출 전에 `self.position.reset_daily()` 실행 |

**일일 통계 보정 1건**

| 항목 | 수정 |
|---|---|
| **수수료 리셋 누락** | `PositionTracker.reset_daily()`에 `_daily_commission = 0.0` 추가 |

### 현재 운영 기준

- `손익 추이`의 오늘 값은 이제 `trades.db`의 `net_pnl_krw` 합계와 일치해야 한다.
- 잔고 패널 `실현손익` fallback도 같은 정규화 기준을 사용하므로, 브로커 원문 공란 시 내부 UI끼리 값이 갈라지지 않아야 한다.
- `trades` 테이블의 손익 계산 기준 버전은 `formula_version = 2` 이다.

### 세션 검증 결과

- `fetch_today_trades('2026-05-08')` 합계: `-1,618,766원`
- `trades` 오늘 27건 전체 `formula_version = 2` 정규화 완료
- 정규화 샘플:
  - `pnl_pts=+1.50`
  - `gross_pnl_krw=375,000`
  - `commission_krw=8,645`
  - `net_pnl_krw=366,355`

---

## 2026-05-07 세션 주요 수정 (5차) — Phase 5 QA + strategy_events + shadow IPC

### 핵심 변경 사항

**Phase 5 컴포넌트 구조 (STRATEGY_PARAMS_GUIDE §1~§20 93% 구현 완료)**

| 컴포넌트 | 파일 | 상태 |
|---|---|---|
| StrategyRegistry + strategy_events 테이블 | `config/strategy_registry.py` | ✅ 완료 |
| Shadow candidate IPC (JSON 파일) | `data/shadow_candidate.json` | ✅ 완료 |
| ShadowEvaluator 초기화 (`start_shadow_mode`) | `main.py` | ✅ 완료 |
| HotSwapGate 이벤트 기록 | `strategy/ops/hotswap_gate.py` | ✅ 완료 |
| 전략 대시보드 이벤트 로그 표시 | `dashboard/strategy_dashboard_tab.py` | ✅ 완료 |

**Shadow candidate 흐름**:
```
param_optimizer.propose_for_shadow()
  → data/shadow_candidate.json 기록 (live 파라미터 변경 없음)
    → daily_close() → _load_shadow_candidate()
      → start_shadow_mode() → ShadowEvaluator 인스턴스화
        → (2주 후) HotSwapGate.attempt()
          → 통과: _execute_hotswap() → PARAM_CURRENT 업데이트 + JSON 삭제
          → 거부: log_event("HOTSWAP_DENIED") + 1주 추가 관찰
```

**QA 버그 3종 수정**:
- `%+,.0f` → `%+.0f` (Python 3.7 `%` 포매팅 comma 미지원)
- `det.get_level()` → `max(det.get_levels().values())` (`MultiMetricDriftDetector` API)
- QA 세더 cp949 콘솔 UnicodeEncodeError fallback 추가

---

## 2026-05-07 세션 주요 수정 (4차) — B60~B63 잔고 패널 수치 수정 + 모의서버 포지션 복원 버튼

### 오늘 세션 요약

**계기**: HTS 실시간 잔고와 미륵이 대시보드 잔고 패널 수치 불일치 (총매매 576,500원 vs HTS 288,250,000원).
재시작 후 대시보드 전체 0.00 표시 문제도 동시에 진단.

| 버그 | 원인 | 수정 |
|---|---|---|
| **[B60] 합성 잔고행 PnL 배수 오류** | `_eval_krw = entry × qty × 500_000/1000 = 500원/pt`  KOSPI200 승수=250,000원/pt | `× 250_000` 직접 계산. `_pnl_krw`도 동일 수정 |
| **[B61] 총평가손익 blank (pnl=0 시)** | guard `if pnl_sum or not rows`가 pnl=0+rows=비어있지않음 → False → 미설정 | `if not str(summary.get(...) or "").strip():` — 조건 단순화 |
| **[B61-2] 청산가능 컬럼 blank** | 합성행 key `"청산가능"` ≠ dashboard col-3 key `"주문가능수량"` | key → `"주문가능수량": str(_qty)` |
| **[B62] 모의서버 startup sync FLAT 오염** | 재시작 시 OPW20006 blank rows → FLAT 강제 기록 → position_state.json 덮어씀 → 다음 재시작 FLAT 시작 | `GetServerGubun=="1"` 판정 추가. 모의+blank+비FLAT → FLAT 결정 skip |
| **[B63] 포지션 수동 복원 버튼 설계** | 재시작 후 모의서버 blank로 포지션 정보 소실 시 복구 수단 없음 | `PositionRestoreDialog` + `AccountInfoPanel.btn_position_restore` 신설 |

### 핵심 확인 사항 (오늘 세션)

- **KOSPI200 선물 계약 승수 = 250,000원/pt** (2017년 이후). 기존 코드가 `500_000/1000=500`으로 500배 틀렸음.
- **모의투자 서버 OPW20006 응답 = 항상 blank**. row 구조는 있지만 모든 필드가 빈 문자열. 정상 동작.
- **15:10 강제청산 정상 작동 확인**: `position_state.json` `last_update_reason="apply_exit_fill_final:15:10 강제청산"` 2026-05-07 15:25:59 기록.

### 수정 후 잔고 패널 동작 흐름

```
startup sync → OPW20006 blank rows
  → GetServerGubun == "1" (모의서버) AND position != FLAT
    → FLAT 결정 skip → 저장 포지션 유지 [B62]
  → _ts_push_balance_to_dashboard():
      _has_real_row = False → 합성 잔고행 생성 [B60]
      _eval_krw = entry × qty × 250_000 (pt→KRW)
      _pnl_krw = pnl_pts × 250_000
      "주문가능수량": str(_qty)  [B61-2]
  → summary guard: str(v or "").strip() 체크 [B61]
  → 대시보드 잔고 패널 갱신

수동 복원 버튼 [B63]:
  "포지션 복원" 버튼 클릭 → PositionRestoreDialog (방향/가격/수량/ATR)
  → sig_position_restore.emit() → _manual_position_restore()
  → position.sync_from_broker() → _recalculate_levels(atr)
  → QTimer.singleShot(300ms) → _ts_refresh_dashboard_balance()
```

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` | `_ts_push_balance_to_dashboard`: B60/B61 수정. `_ts_sync_position_from_broker`: B62 모의서버 분기. `_ts_manual_position_restore`: B63 신설. monkey-patch 추가 |
| `dashboard/main_dashboard.py` | `PositionRestoreDialog` 신설. `AccountInfoPanel`: `sig_position_restore` signal + `btn_position_restore` + tooltip. `DashboardFacade`: signal 노출 |

---

## 2026-05-07 세션 주요 수정 (3) — B56: ENTRY 재진입 루프 쿨다운 중앙화

### 오늘 세션 요약 (오후)

**발생 현상**: 09:56~10:07 구간에서 ENTRY 주문이 2분마다 8회 반복 발생.
B52·B53(쿨다운 설정) 코드가 이미 있었지만 `_entry_cooldown_until`이 실제로 설정되지 않는 케이스가 존재했음:
1. B52 쿨다운이 `_optimistic==True` 조건에만 종속 → `_optimistic=False`이면 쿨다운 미설정
2. `_ts_on_order_message` 거부 경로에서 `_clear_pending_order()` 호출 시 쿨다운 없음
3. balance Chejan FLAT 경로(`_ts_sync_from_balance_payload`)도 쿨다운 없음

**근본 수정 [B56]**: 쿨다운 설정 로직을 `_clear_pending_order()`에 중앙화.
ENTRY 미체결(`filled_qty=0`) 소멸이면 **어떤 경로든** 2분 쿨다운 자동 설정.

| 항목 | 수정 내용 |
|---|---|
| **[B56] `_clear_pending_order()` 중앙화** | `kind=="ENTRY" and filled_qty==0`이면 `_entry_cooldown_until = now+2min`. B52/order_reject/balance_FLAT 등 모든 경로 커버 |
| **[B52] `_optimistic` 의존 분리** | `_reset_position()`은 여전히 `_optimistic==True` 조건. 쿨다운은 무조건 설정 (B56 중앙화로 이중 설정이지만 무해) |
| **[B56] balance Chejan FLAT 경로 주석 추가** | `_ts_sync_from_balance_payload` qty<=0 분기에 B56 자동 적용 설명 추가 |

### 수정 후 `_clear_pending_order()` 흐름

```python
def _clear_pending_order(self) -> None:
    if self._pending_order is not None:
        logger.warning("[PendingOrder] clear %s", self._pending_order)
        # [B56] ENTRY 미체결 소멸 → 어떤 경로든 2분 재진입 금지
        if (self._pending_order.get("kind") == "ENTRY"
                and self._pending_order.get("filled_qty", 0) == 0):
            self._entry_cooldown_until = now + 2min
            logger.warning("[EntryCooldown] ... until HH:MM:SS")
    self._pending_order = None
```

### 추가 확인 사항

- **[V42] SHORT 진입 Chejan 수신 확인**: CB③ 발동으로 이번 세션에서 SHORT 미발생. 다음 세션 확인
- **[V39] ENTRY 타임아웃 복원 로그**: `[FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원` 대시보드 SYSTEM 탭 확인
- **[BalanceChejanFlow] 조사 완료**: 09:56~10:09 구간에 gubun='1' 잔고 Chejan 이벤트 없음 확인 → 비이슈 종료

---

## 2026-05-07 세션 주요 수정 (B52·B49·B50 — EXIT 루프 근본 원인 수정)

### 오늘 세션 요약

**발생 현상**: ENTRY 주문(09:01, trade_type=1) 접수만 되고 체결 없음 (모의투자 서버 09:00 고변동성 구간).
낙관적 오픈으로 로컬 position=LONG → 60s ENTRY 타임아웃 → pending 해제만 되고 position 유지 →
하드스톱 반복 발동 → EXIT trade_type=4 → Kiwoom 측 포지션 없으므로 Chejan 무응답 → 2분 루프.

| 항목 | 수정 내용 |
|---|---|
| **[B49] EXIT 진단 로그 추가** | `_ts_check_exit_triggers()` — 하드스톱/시간청산 `[ExitAttempt]` + `[ExitSendOrderResult]` |
| **[B50] price_hint float 오차** | `price_hint=round(exit_price, 2)` 적용 |
| **[B52] ENTRY 타임아웃 포지션 복원** | 60s 타임아웃 + `_optimistic==True` → `_reset_position()` + `[FixB]` 경보 |
| **[B53] 타임아웃 후 2분 쿨다운** | `_entry_cooldown_until = now+2min` → STEP 7 진입 차단 |
| **[B54] SendOrderFO 파라미터 통일** | `lOrdKind=1(신규매매) + sSlbyTp` 방향 명시. trade_type=2(SHORT)가 new convention에서 "정정"으로 해석되어 서버 거부되던 문제 수정. 진입/청산/긴급청산 모두 적용 |
| **[B55] accepted vs filled 타임아웃 분리** | `order_no==""` → 60s (미접수), `order_no!=""` → 300s (접수 대기). `pending["accepted_at"]` 타임스탬프 기록 추가 |
| **BrokerSync CRITICAL→WARNING** | position_state.json 잔여 FLAT 처리는 정상 동작이므로 WARNING으로 완화 |
| **[EntrySendResult]** | `log_manager.system()` 추가 → dashboard에서 ret 즉시 확인 가능 |

### 수정 후 ENTRY 타임아웃 흐름

```
낙관적 오픈 → position=LONG, _optimistic=True
ENTRY 60s 타임아웃 체크
→ kind=="ENTRY" AND _optimistic==True:
    [FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원 (WARN)
    position._reset_position()  ← position=FLAT, entry_price=0
    _clear_pending_order()
→ 이후 하드스톱 발동 안 됨 (position=FLAT)
```

### 추가 확인 사항 (미해결)

- **[V41] B54 SHORT 진입 + EXIT Chejan 수신 확인**: 재시작 후 SHORT 진입 Chejan 수신 여부, LONG 진입 후 EXIT Chejan 수신 여부 확인
- **ENTRY 미체결 원인**: 모의투자 서버 장 초반(09:00~10:10) 고변동성 구간 + 틱 간헐적 수신 문제. 실서버 전환 시 재확인
- **HTS 미처리 주문**: 30907(LONG, 미체결)는 HTS에서 수동 취소 필요 (재시작 전)

---

## 2026-05-06 세션 주요 수정 (Fix B + OPW20006 enc 분석)

| 항목 | 수정 내용 |
|---|---|
| **[B45] OPW20006 레코드명 오타 수정** | `api_connector.py` `_MULTI_RECORD = "선옵잔고상세현황"` (現況·황). 기존 `현활`(活) 오타로 모든 GetCommData 반환값이 blank였음. enc 파일 직접 분석으로 확정 |
| **OPW20006 필드 목록 수정** | `보유수량` 삭제 (OPW20006에 없음), `잔고수량` 유지 (enc offset 66 확인). CS "잔고수량 없음" 오답으로 제거했던 것을 복원. `조회건수` 교차검증 추가 |
| **Fix B — 낙관적 포지션 오픈** | `position_tracker.py`에 `_optimistic` 플래그 + `apply_entry_fill()` 보정 경로 추가. `main.py` line 2660(production)에 `position.open_position()` + `_optimistic=True` 삽입. 모의투자 이중진입 방지 |
| **TR 조사 절차 수립** | `dev_memory/kiwoom_api_tr_investigation.md` 신설. enc 파일(ZIP+CP949) 읽기 절차, GetRepeatCnt/GetCommData 패턴, OPW20006 함정 표 포함 |

### [B46] SendOrderFO 전환 (추가 수정)

| 항목 | 내용 |
|---|---|
| **증상** | `[RC4109] 모의투자 종목코드가 존재하지 않습니다` — `KOA_NORMAL_SELL_KP_ORD` 발생 |
| **원인** | `SendOrder`는 주식 전용. 선물은 `SendOrderFO` 사용 필수 |
| **Fix** | `api_connector.py` `send_order_fo()` 신설. main.py 진입/청산/긴급청산 헬퍼 전환 |
| **`send_order_fo` 파라미터** | `hoga_gb="3"` (선물시장가) / `trade_type` 1=매수, 2=매도 |

**Fix B 진단 로그**: `[FixB] 낙관적 오픈 완료 direction=LONG status=LONG qty=1 optimistic=True` — 2026-05-06 WARN.log에서 정상 확인됨.

### [B47] SendOrderFO trade_type 청산 오류 수정 (2026-05-06 추가)

| 항목 | 내용 |
|---|---|
| **증상** | 14:28 LONG 진입 후 TP1/하드스톱/15:10 강제청산 주문이 60분간 체결 안 됨. EXIT pending 60초마다 set/clear 반복 |
| **원인** | `_send_kiwoom_exit_order`에서 `trade_type=2`(매도 개시=신규 SHORT) 사용. 선물 LONG 청산은 `trade_type=4`(매도 청산) 필수. 모의투자 서버에서 신규매도로 해석 → 체결 처리 안 됨 |
| **Fix** | `trade_type = 4 if LONG else 3` (매도청산/매수청산). `_KiwoomOrderAdapter.send_market_order()`도 동일하게 수정 |

### [B48] gubun='4' 노이즈 이벤트 차단 (2026-05-06 추가)

| 항목 | 내용 |
|---|---|
| **증상** | 매 주문마다 `gubun='4'`, `order_no=''`, `fill_qty=0`, `status=''` 이벤트 추가 도착. ChejanFlow/ChejanMatch 로그 오염 |
| **Fix** | `_ts_on_chejan_event` 진입부에 `if _gubun not in ("0", "1"): return` 추가 |

### 현재 주문 흐름 (B46·B47·Fix B 모두 적용 후)

```
_execute_entry()
→ SendOrderFO COM API, trade_type=1(LONG)/2(SHORT)   ← [B46] 선물 주문 함수
→ _set_pending_order(ENTRY)
→ position.open_position(direction, price, qty)        ← 낙관적 오픈 (Fix B)
→ position._optimistic = True

_send_kiwoom_exit_order()
→ SendOrderFO COM API, trade_type=4(LONG청산)/3(SHORT청산)   ← [B47] 청산 타입 수정

OnReceiveChejanData 콜백
→ gubun='4' → early return (노이즈 차단) [B48]
→ gubun='0' fill_qty=0 → 접수 이벤트 (pending 유지)
→ gubun='0' fill_qty>0 → 체결 이벤트 → apply_entry_fill()/apply_exit_fill()

[Chejan 진입 체결 시]
→ apply_entry_fill() → _optimistic=True + 방향 일치 → 가격 보정만 (수량 불변)

[Chejan 미수신(모의투자 일부)]
→ 낙관적 포지션 그대로 유지 → 이중진입 없음
```

### OPW20006 교훈

```
enc 파일: C:\OpenAPI\data\opw20006.enc (ZIP → OPW20006.dat CP949)
올바른 레코드명: 선옵잔고상세현황 / 선옵잔고상세현황합계
확인된 필드: 종목코드, 종목명, 매매일자, 매매구분("매수"=LONG/"매도"=SHORT),
             잔고수량(offset 66), 매입단가, 매매금액, 현재가, 평가손익, 손익율, 평가금액
키움 CS 오답: "잔고수량 없음" → enc 파일로 반증. CS 답변 맹신 금지.
```

---

## 2026-05-04 세션 주요 수정 (야간 2세션 — Kiwoom API 주문 연결 + 부분 청산 완성)

| 항목 | 수정 내용 |
|---|---|
| **[B42] Kiwoom 주문 전달 누락 수정** | `api_connector.py` `send_order()` 신설. `entry_manager.py`/`exit_manager.py` `acc_no=""` → `_secrets.ACCOUNT_NO`. main.py에 `_send_kiwoom_entry_order()` / `_send_kiwoom_exit_order()` 헬퍼 추가 → 진입/청산 모든 경로에서 실 API 호출 |
| **부분 청산 완성 (TP1/TP2)** | `PositionTracker.partial_close(exit_price, qty, reason)` 신설. `_execute_partial_exit(price, stage)` + `_post_partial_exit(result, stage)` — PARTIAL_EXIT_RATIOS 기반 API→DB→대시보드 전체 연결 |
| **`_KiwoomOrderAdapter` 신설** | main.py 모듈레벨 어댑터 클래스. `EmergencyExit.set_order_manager()` 에 주입 — CB/KillSwitch 긴급청산도 실 API로 연결 |
| **주문/체결 탭 실데이터 메트릭** | LatencySync.summary() → `update_order_metrics(trades, avg_lat_ms, peak_lat_ms, samples)` 매분 갱신. 하드코딩 더미값 제거 |
| **로그 좌측 정렬** | `QTextCursor` + `QTextBlockFormat.setAlignment(Qt.AlignLeft)` 기반 `_insert_html_left()` / `_insert_html_center()` static 메서드. append()/append_restore()/append_separator() 전부 교체 |

### 수정 후 주문 흐름

```
run_minute_pipeline()
→ STEP 7 진입: _send_kiwoom_entry_order(direction, qty) → SendOrder COM API
→                position.open_position(...)
→ STEP 8 청산:
    손절/15:10/트레일: _send_kiwoom_exit_order(qty) → SendOrder COM API
                       position.close_position(...)
    TP1/TP2:           _execute_partial_exit(price, stage)
                       → _send_kiwoom_exit_order(partial_qty) → SendOrder COM API
                       → position.partial_close(...)
                       → _post_partial_exit(result, stage)
CB/KillSwitch:     _KiwoomOrderAdapter.send_market_order() → SendOrder COM API
```

### OnReceiveChejanData 콜백 현황

- ✅ **구현 완료**: `_ts_on_chejan_event()` — gubun='0'(주문/체결) 처리. fill_qty>0 체결 이벤트로 포지션 보정
- ✅ **B47 수정**: trade_type 청산 타입 오류 수정 → EXIT 체결 정상화 (다음 장중 [V35] 확인 필요)
- ✅ **B48 수정**: gubun='4' 노이즈 이벤트 early return 차단
- ⏳ **미확인**: trade_type=4 수정 후 EXIT 체결 Chejan 즉시 수신 → [V35] 다음 장중 확인

---

## 2026-05-04 세션 주요 수정 (야간 — FID 탐색·PROBE 진단·수급 TR 수정)

| 항목 | 수정 내용 |
|---|---|
| **[B40] FID_OI = 291 → 195 수정** | `config/constants.py` + `option_data.py` 하드코딩 2곳. FID 291 = 예상체결가(선물호가잔량), FID 195 = 미결제약정(선물시세). PROBE 스캔으로 확정 |
| **신규 FID 상수 5개 추가** | `FID_EXPECTED_PRICE=291`, `FID_KOSPI200_IDX=197`, `FID_BASIS=183`, `FID_UPPER_LIMIT=305`, `FID_LOWER_LIMIT=306` |
| **TR_INVESTOR_OPTIONS 수정** | opt50014(선물가격대별비중차트요청·잘못 사용) → opt50008(투자자별매도수금액요청) |
| **PROBE 진단 인프라** | LAYER_PROBE 추가, PROBE-ALLRT 전수 FID 스캔, probe_investor_ticker(). 스캔 범위 1~99로 확장 |
| **투자자ticker 모의투자 미지원 확인** | 8가지 코드/타입 조합 전부 ret=0이나 데이터 수신 없음 → 실서버 전환 시 재테스트 필요 |

### 확정된 FID 매핑 (선물시세 기준)

| FID | 값 | 의미 |
|---|---|---|
| 10 | +1049.65 | 현재가 |
| 15 | 거래량 | 거래량 |
| 41 | 매도1호가 | (선물호가잔량에서 수신) |
| 51 | 매수1호가 | (선물호가잔량에서 수신) |
| 195 | 207357 | **미결제약정** (진짜 OI) |
| 197 | +1049.66 | KOSPI200 지수 현재가 |
| 183 | +1.04 | 시장베이시스 |
| 291 | +1020.60 | 예상체결가 (OI 아님! — 선물호가잔량 기준) |
| 305 | +1078.35 | 선물 당일 상한가 |
| 306 | -918.65 | 선물 당일 하한가 |

---

## 2026-05-04 세션 주요 수정 (저녁 — 다이버전스 패널 수급 데이터 흐름)

| 항목 | 수정 내용 |
|---|---|
| **수급 TR 수집 구조 전환** | `investor_data.fetch_all()` → COM 콜백 체인(run_minute_pipeline) 외부로 이동. `_investor_timer` QTimer 60s 신설. STEP4에서 직접 호출 시 0xC0000409 스택 오버런 위험 해소 |
| **investor_data.fetch_*() 수정** | `self._api.set_input_value()`+`comm_rq_data()` (존재하지 않는 메서드) → `self._api.request_tr()` 전환. TR 응답 rows를 인라인으로 직접 파싱 |
| **api_connector._parse_tr_row 확장** | OPT50029만 지원 → opt10059(`순매수`), opt50014(`콜순매수`/`풋순매수`), opt10060(`차익순매수`/`비차익순매수`) 필드 추가 |
| **logger.py DATA 레이어 추가** | `LAYER_DATA="DATA"` 신설. investor_data 오류가 파일 핸들러 없이 사라지던 문제 해결 |
| **투자자 포지션 매트릭스 개선** | `rt_strd`/`fi_strangle` 하드코딩 0 → 실제 `abs(콜)+abs(풋)` 총합 표시 |
| **옵션 구간별 거래량 UI 연결** | `DivergencePanel.update_data()` oz_* 위젯 갱신 구현. `get_zone_data()` 신설 — ATM=현재 전체 수집 데이터 기반 투자자별 %, ITM/OTM=0 (추후 개선) |
| **_fill_dummy_options 기관 추가** | `institution` 더미 추가 → zone % 합계 정상화 |

### 수정 후 수급 데이터 흐름

```
[QTimer 60s]
→ _fetch_investor_data()
→ investor_data.fetch_all()
→   fetch_futures(): request_tr(opt10059) → rows 파싱 → _futures 캐시 갱신
→   fetch_options(): request_tr(opt50014) → rows 파싱 → _call/_put 캐시 갱신
→   fetch_program(): request_tr(opt10060) → rows 파싱 → _program_* 캐시 갱신
→ DATA.log 기록

[run_minute_pipeline - COM 콜백 체인 내]
STEP4: get_features() → 캐시 읽기만 (TR 호출 없음)
       get_zone_data() → 캐시 기반 zone % 계산
→ update_divergence({..., "zones": {...}})
→ DivergencePanel.update_data() → 바이어스 바 + 포지션 카드 + oz_* zone 바 갱신
```

### 남은 한계
- ITM/OTM 구간: opt50014는 전체 합산만 제공 → ATM에 전체 표시, ITM/OTM=0
  - 정확한 구분은 행사가별 개별 TR 조회(여러 번) 필요 (추후 구현)

---

## 2026-05-04 세션 주요 수정 (오후 — 부트스트랩·SGD·UI)

| 항목 | 수정 내용 |
|---|---|
| **[B37] SGD log_loss → log** | `online_learner.py` `loss="log_loss"` → `"log"`. sklearn 1.0.2 호환. 매분 ValueError 크래시 해결 |
| **부트스트랩 치킨에그 해결** | STEP 5 early return 제거 → 미학습 시 1/3 균등 예측 → STEP 9 DB 저장 → SGD 학습 활성화 |
| **watchdog 임계값** | 60/120/180s → 90/150/240s (1분봉 30s 버퍼) |
| **`_last_recovery_ts` 중복 복구 방지** | 동일 ts 반복 복구 스킵 + `run_minute_pipeline` 진입 시 초기화 |
| **Guard-C1/C2 `notify_pipeline_ran()`** | 비정상 분봉 차단 return 경로에 watchdog 카운터 리셋 추가 |
| **`_dir_ko` NameError 수정** | STEP 7 진입 시 변수 정의 추가 |
| **파라미터 중요도·상관계수 툴팁** | SHAP 개념·업데이트 조건 툴팁 추가 |
| **대시보드 섹션 간격** | 섹션 구분선 앞 16px·뒤 12px로 시인성 향상 |

### SGD 학습 파이프라인 현황 (2026-05-04 13:44 확인)

```
[OnlineLearner] 1m/3m/5m/15m 초기 학습 완료 ← log_loss 수정 + 부트스트랩 정상화
10m·30m: 이전 세션 미실행 구간 ts 없음 → 장 진행 중 자동 채워짐
```

---

## 2026-05-04 세션 주요 수정 (B14 OFI 수정 — 선물호가잔량 콜백)

| 항목 | 수정 내용 |
|---|---|
| **B14 OFI 영구 0 수정** | `선물호가잔량` 콜백 `_on_hoga_data()` 신설. bid/ask를 `_last_bid1/ask1`에 저장, `_current_bar` 동기화, `on_hoga` 콜백으로 OFI 누적 |
| **`sopt_type` 파라미터 추가** | `api_connector.register_realtime()` — `"1"` 전달 시 기존 등록 유지하고 추가 등록 (선물호가잔량 등록에 사용) |
| **OFI 경로 분리** | `_on_tick_price_update`에서 OFI 제거 → `_on_hoga_update()` 전담. 선물시세 틱이 아닌 실제 호가 이벤트마다 OFI 누적 |

### 수정 후 데이터 흐름

```
선물시세    → _on_real_data()  → price/vol 조립 → bar 업데이트
선물호가잔량 → _on_hoga_data() → bid/ask 읽기  → _last_bid1/ask1 저장
                                              → _current_bar bid/ask 동기화
                                              → _on_hoga_update() → ofi.update_hoga()
```

---

## 2026-05-04 세션 주요 수정 (모의투자 SetRealReg + WARN 로그 분리 + 파이프라인 watchdog 수정)

| 항목 | 수정 내용 |
|---|---|
| **WARN 로그 분리** | `utils/logger.py` — `_MaxLevelFilter(WARNING)` 추가. SYSTEM 파일핸들러는 INFO만 기록. `YYYYMMDD_WARN.log` 별도 핸들러 추가. 대시보드 경보탭만 WARN+ 표시 |
| **OPT50029 → SetRealReg 전환** | 모의투자 서버에서 OPT50029 rows=0 — 실시간 데이터 미제공. `is_mock_server=False` + `realtime_code=A0166000`으로 SetRealReg 활성화 |
| **SetRealReg 코드 수정 (B33)** | 기존 `rt_code=101W06` → `realtime_code=A0166000`. 콜백 필터 code 불일치 해결 |
| **파이프라인 watchdog 수정 (B35)** | `run_minute_pipeline()` 모델 미학습 early return 전에 `notify_pipeline_ran()` 추가. 기존: line 426 return → line 667 미도달 → watchdog 영구 발동 |
| **진단 로깅 추가** | `[RT-CB]` `[RT-DATA]` `[RT-RAW]` `[RT-BAR]` `[BAR-CLOSE]` SYSTEM.log 기록. 실시간 분봉 수신 경로 end-to-end 확인 가능 |

### 모의투자 실시간 분봉 수신 확인 결과 (2026-05-04 로그)

```
[RT-CB] code='A0166000' type='선물시세' 등록키=[('A0166000', '선물시세')]
[RT-RAW] raw_price='+1038.55' raw_vol='+1'
[BAR-CLOSE] ts=11:22 O=1038.55 H=1038.80 L=1038.45 C=1038.80 V=25  ✅ 매 분 정상
```

---

## 2026-04-30 세션 주요 수정 (SIMULATION 제거 + 자동 종료 + 성장 추이 대시보드)

| 항목 | 수정 내용 |
|---|---|
| **SIMULATION 코드 전면 제거** | `--mode` argparse / `self.mode` / 더미 모델 주입 / `_sim_timer` / `force_ready_for_test()` / `TRADE_MODE` 상수 제거. 단일 실전 경로만 유지 |
| **일일 마감 자동 종료** | `daily_close()` 완료 → 슬랙 종료 알림(거래수·승률·PnL·재학습·다음시작) → 15초 후 `_qt_app.quit()`. `_auto_shutdown()` 신설 |
| **패널 이전 데이터 지속** | `_restore_panels_from_history()` — 시작 500ms 후 DB 이력으로 자가학습·효과검증·추이 패널 선조회. 파이프라인 첫 실행 전 빈값 방지 |
| **daily_stats 스냅샷 저장** | `daily_close()` 내 `save_daily_stats()` — SGD정확도·검증건수·PnL을 `daily_stats` 테이블에 영속 |
| **📈 성장 추이 탭 신설** | `TrendPanel` — 일별(30일)/주별(12주)/월별(12개월)/연간 4탭. 스파크라인(PnL·승률·SGD정확도) + 스크롤 테이블. 탭 순서: …자가학습/효과검증/**성장추이**/알파봇 |
| **DB 집계 쿼리 4종** | `fetch_trend_daily/weekly/monthly/yearly()` + `daily_stats` 테이블 + `save_daily_stats()` |

---

## 현재 대시보드 탭 구조

### 중앙 탭 (mid_tabs) — 8개
| 번호 | 탭 이름 | 클래스 |
|---|---|---|
| 1 | 다이버전스 + 포지션 | `DivergencePanel` |
| 2 | 동적 피처 (SHAP) | `FeaturePanel` |
| 3 | 청산 관리 | `ExitPanel` |
| 4 | 진입 관리 | `EntryPanel` |
| 5 | 🧠 자가학습 | `LearningPanel` |
| 6 | 🎯 효과 검증 | `EfficacyPanel` |
| **7** | **📈 성장 추이** | **`TrendPanel`** (신규) |
| 8 | 알파 리서치 봇 | `AlphaPanel` |

### 우측 5층 로그 탭 — 6개
| 탭 | 내용 |
|---|---|
| 1 시스템/경보 | SYSTEM/WARNING 레벨 통합 (2 경보탭 공유) |
| 2 경보 | WARN/ERROR/CRITICAL 전용 |
| 3 주문/체결 | TRADE 레이어 + FILL/PENDING 태그 |
| 4 손익 | PnL 로그 + 미실현·일일·VaR 수치 |
| 5 모델 AI | LEARNING/MODEL 레이어 |
| 6 📊 손익 추이 | 일별·주별·월별 누적 P&L 테이블 (기존 PnlHistoryPanel) |

---

## 2026-04-30 세션 주요 수정 (파이프라인 감시 경보 버그 2종 수정 + 분봉 툴팁)

| 항목 | 수정 내용 |
|---|---|
| **경보 누락 버그 1** | `_tick_header()` — `_watchdog_alerted.add(threshold)` 가 콜백 체크 **이전**에 실행되어, 콜백 미등록 시 임계값을 소비하고 나중에 콜백 등록 후에도 영구 누락. **수정**: 콜백 실행 후에만 소비(`add` 위치 교체) |
| **경보 누락 버그 2** | `append_sys_log_tagged()` — `level="WARNING"` 체크 조건이 `("WARN", "ERROR", "CRITICAL")` 이라 `"WARNING"` 이 불일치 → SYSTEM 태그로 처리되어 경보 탭 미표시. **수정**: `{"WARNING": "WARN"}.get(level, level)` 정규화 추가 |
| **분봉 라벨 툴팁** | `_PIPE_HEALTH_TIP` 상수 추가 — 파이프라인 심박 막대 기능 + 3단계 자동 조치(60/120/180초) + 긴급복구 루틴 + 원인 목록. 분봉 라벨·진행 바·경과 라벨 3개 위젯 연결 |

### 버그 발생 경위 (실제 시퀀스)

```
1. __init__: _header_timer 시작 → _pipe_elapsed_s 증가 시작
2. connect_kiwoom() 진행 중 (수십 초 소요)
   → 60/120초 도달 시 threshold 소비되나 callback=None → 알림 없음
3. set_pipeline_watchdog_cb() 호출 → callback 등록
4. pipeline 정상 실행 → notify_pipeline_ran() → _watchdog_alerted.clear()
5. pipeline 재정지 → 60초 후 threshold 60 재진입
   → 이때 callback 존재해야 발동되는데...
   → _pipe_elapsed_s += 1 로직에서 threshold 60을 콜백 없이 소비했다면 영구 누락!
```

---

## 2026-04-30 세션 주요 수정 (비정상 분봉 가드 + 진입 신뢰성 강화)

| 항목 | 수정 내용 |
|---|---|
| **Guard-C1 가격 0 차단** | `run_minute_pipeline()` 앞단 — close/high/low ≤ 0 이면 경보 로그 후 즉시 return. ATR 음수·손절가 오작동 원천 차단 |
| **Guard-C2 고가<저가 차단** | high < low 역전 분봉 경보 후 즉시 return. 음의 TR → ATR 오염 방지 |
| **Guard-C3 volume=0 진입 차단** | volume=0 경보 로그 + `_bar_volume_zero` 플래그 설정. STEP 7 진입 조건에 `and not _bar_volume_zero` 추가. 청산은 차단 안 함(가격 기반) |
| **Guard-F1 CORE 피처 NaN/Inf 교정** | STEP 4 후 vwap_position / cvd_direction / ofi_pressure 에 NaN·Inf 검출 시 0으로 교정 + 경보 로그 |
| **daily_loss_pct 계산 수정** | 기존: `abs(pnl_pts) / 1_000` (실질적으로 항상 통과) → 수정: `max(-pnl_krw, 0) / 50_000_000` (5천만원 기준 실손실률). 체크리스트 9번 리스크 한도 실질화 |
| **`import math` 추가** | main.py 최상단 — Guard-F1 NaN/Inf 검사용 |

### 가드 점검 결과 요약 (조사 기반)

| 구간 | 수정 전 | 수정 후 |
|---|---|---|
| 분봉 수신 (realtime_data) | abs() 변환만 | 변경 없음 (수신 레이어는 OK) |
| 파이프라인 앞단 (main.py) | **없음** | **C1/C2/C3 가드 추가** |
| CORE 피처 (STEP 4 후) | **없음** | **F1 NaN/Inf 교정** |
| 진입 조건 (STEP 7) | CB+시간+등급+수량 | **volume=0 차단 추가** |
| 청산 조건 (STEP 8) | 완전 (변경 없음) | 변경 없음 |
| 리스크 한도 (체크리스트 9) | **pts/1000 — 항상 통과** | **KRW/5천만 — 실질 2% 한도** |
| Circuit Breaker | 완전 (변경 없음) | 변경 없음 |

### 남은 한계 (개선 불가·저우선)

- OFI/CVD 극단값 제한 없음 — signal_strength 과대 가능 (CB④ ATR 3배 트리거로 간접 방어)
- account_balance 하드코딩(5천만) — 실제 잔고 연동 시 개선 필요
- ATR floor(0.5pt)로 비정상 소ATR 방어는 유지

---

## 2026-04-30 세션 주요 수정 (파이프라인 생존 감시 + 자동 복구)

| 항목 | 수정 내용 |
|---|---|
| **파이프라인 감시 콜백** | `main_dashboard.py` — `MireukDashboard._watchdog_alerted` (set) + `_pipeline_recovery_cb` 추가. `_tick_header()`에서 60/120/180초 임계값 초과 시 1회만 콜백 발동. `notify_pipeline_ran()` 시 플래그 초기화 |
| **`set_pipeline_watchdog_cb()`** | `DashboardAdapter`에 추가 — main.py → dashboard 역방향 콜백 등록 인터페이스 |
| **`_on_pipeline_watchdog()`** | `main.py` — 60s: 경보 로그(WARNING), 120s: 경보 + 슬랙, 180s: 경보 + 슬랙 + 강제 복구 |
| **`_try_pipeline_recovery()`** | `main.py` — `raw_candles` DB 최신 분봉(10분 이내) 읽어 `run_minute_pipeline()` 강제 재실행. 포지션 보유 중 장기 정지 시 추가 경보 |
| **`log_manager.warn` 오류 수정** | `warn()` 메서드 없음 → 전체 `log_manager.system(msg, "WARNING")` 으로 교체. SYSTEM layer + WARNING level → `append_sys_log_tagged` → 1 시스템·2 경보 탭 동시 기록 |

### 파이프라인 감시 3단계 동작

| 경과 | 동작 |
|---|---|
| **60초** | 경보 탭 경고 — 분봉 수신 지연, 장 시간 확인 안내 |
| **120초** | 경보 탭 경고 + 슬랙 알림 — 60초 내 미복구 시 자동 조치 예고 |
| **180초** | 경보 탭 + 슬랙 + `_try_pipeline_recovery()` 자동 실행 |

### 복구 루틴 조건 분기

- `raw_candles` 없음 → 경보 로그 후 종료 (포지션 있으면 추가 경보)
- 최신 분봉 > 10분 전 → 복구 포기 (장외 시간 판단)
- 최신 분봉 ≤ 10분 → `run_minute_pipeline(bar)` 강제 실행 → `notify_pipeline_ran()` 자동 호출 → 감시 플래그 리셋

---

## 2026-04-30 세션 주요 수정 (PnL 재시작 복원 수정 + 분봉 모니터 툴팁)

| 항목 | 수정 내용 |
|---|---|
| **PnL 재시작 복원 [B30]** | `main.py` `_restore_daily_state()` — `restore_daily_stats()` 호출 후 `dashboard.update_pnl_metrics(0.0, daily_pnl_krw, 0.0)` 추가. 재시작 후 미실현손익·일일누적·VaR 패널이 "——원" 로 리셋되던 버그 수정 |
| **분봉 모니터 툴팁** | `dashboard/main_dashboard.py` — `_CANDLE_MONITOR_TIP` 상수 추가. "다음 분봉 ▷" 라벨·진행 바·초 라벨, "↑ 마지막 갱신" 라벨·경과 라벨 5개 위젯에 동일 툴팁 연결. 라벨에 점선 밑줄(cursor:help) 표시 |

### PnL 복원 버그 근본 원인 (B30)
- `_restore_daily_state()`에서 `position.restore_daily_stats(rows)` 로 내부 통계(`_daily_pnl_pts` 등)는 정상 복원
- 그러나 UI 패널에 `dashboard.update_pnl_metrics()` 호출이 없어 화면은 초기값 "——원" 유지
- 수정: `daily_stats()` 로 복원된 값을 읽어 즉시 패널 반영. 미실현/VaR는 0 (첫 분봉 수신 후 갱신됨)

---

## 2026-04-30 세션 주요 수정 (CB 중복발동 수정 + 슬랙 타임스탬프)

| 항목 | 수정 내용 |
|---|---|
| **CB 중복 슬랙 발동 수정** | `_trigger_halt()` — HALTED 상태 조기 반환 체크 추가 (기존: 체크 없음 → 정확도 35% 미만 지속 시 매분 슬랙 재전송) |
| **CB `_trigger_pause()` 방어** | PAUSED 상태에서도 재발동 방지. 기존엔 `HALTED`만 막음 → `PAUSED·HALTED` 모두 차단 |
| **CB 트리거⑤ API지연 방어** | `record_api_latency()` — PAUSED·HALTED 상태에서 슬랙·청산 콜백 중복 호출 방지 조건 추가 |
| **CB → UI 로그 연결** | `circuit_breaker.py`가 `logger.getLogger("SYSTEM")`만 사용해 UI 미출력. `log_manager` import 추가 + `_trigger_pause/halt`, `_check_pause_expiry`, `reset_daily` 전부 `log_manager.system()` 호출 추가 → 대시보드 SYSTEM/경보 탭 표시 |
| **슬랙 타임스탬프** | `utils/notify.py` — `notify()` 내 `[HH:MM:SS]` 자동 첨부. 모든 알림에 전송 시각 표시 |
| **슬랙 주문·체결 함수 추가** | `notify_order()`, `notify_execution()` 함수 신설 (방향·수량·가격·손익 포함) |

### CB 중복 발동 원인 (근본 원인 분석)
- **트리거③ 정확도**: 30분 정확도 < 35% 동안 매분 `record_accuracy()` → `_trigger_halt()` 호출. 기존엔 HALTED 체크 없어 매분 슬랙 재전송
- **트리거④ ATR**: ATR 3배 초과 지속 시 매분 `_trigger_pause()` 호출. 기존엔 PAUSED 상태에서도 재발동 + `_pause_until` 갱신 + 슬랙 재전송
- **UI 미출력**: `circuit_breaker.py`의 `logger`는 파일/콘솔 전용 (`logging.getLogger`). 대시보드 `log_manager`와 별개 시스템이라 UI에 아무것도 안 보임

---

## 2026-04-30 세션 주요 수정 (자가학습 연결)

| 항목 | 수정 내용 |
|---|---|
| **STEP 2 SGD 연결** | `main.py` STEP 2 — STEP 1 검증 결과(verified)의 피처 dict로 `OnlineLearner.learn()` 호출. 매 검증건마다 즉시 `partial_fit` |
| **STEP 3 GBM 연결** | `main.py` STEP 3 — `should_retrain_weekly()` / `should_retrain_monthly()` 조건 충족 시 `batch_retrainer.retrain_now()` 호출 후 `model._load_all()`로 즉시 반영 |
| **SGD 블렌딩 적용** | `main.py` STEP 5 — GBM `predict_proba()` 직후 호라이즌별 `online_learner.blend_with_gbm()` 적용. SGD 미학습(fitted=False) 시엔 GBM 단독 사용 |
| **features 전체 저장** | `main.py` STEP 9 — `list(features.items())[:20]` → 전체 피처 저장 (SGD 학습 입력 완전성 확보) |
| **daily_close 재학습** | `main.py` 15:40 마감 시 `batch_retrainer.retrain_now(weeks_back=8)` 호출 후 모델 reload |
| **BatchRetrainer 초기화** | `main.py __init__` — `self.batch_retrainer = BatchRetrainer()` 추가 |
| **_load_from_db 재작성** | `batch_retrainer.py` — pandas 의존 제거, `raw_features`/`raw_candles` 테이블 직접 읽기. numpy 기반 X 행렬 + `build_single_target()` 라벨 생성 |
| **prediction_buffer features** | `prediction_buffer.py` `verify_and_update()` — SELECT에 `features` 컬럼 추가, 반환 dict에 JSON 파싱된 `features` 포함 |

---

## 🎯 학습 효과 검증기 패널 (신규 — 2026-04-30)

| 항목 | 내용 |
|---|---|
| **위치** | 중앙 탭 6번째 "🎯 효과 검증" (🧠자가학습 탭 오른쪽) |
| **EfficacyPanel** | `dashboard/main_dashboard.py` `class EfficacyPanel` |
| **update_efficacy()** | `DashboardAdapter.update_efficacy(data)` → `efficacy_panel.update_data(data)` |
| **_gather_efficacy_stats()** | `main.py` — DB 쿼리 후 5분마다 호출 (`_efficacy_tick % 5 == 1`) |
| **DB 쿼리 4종** | `utils/db_utils.py` — `fetch_calibration_bins` / `fetch_grade_stats` / `fetch_regime_stats` / `fetch_accuracy_history` |

### 패널 4-Section 구성
1. **신뢰도 캘리브레이션** — confidence 구간별 실제 적중률 테이블 (✓ 우수 / ▲ 과소신뢰 / ▼ 과신)
2. **등급별 매매 성과** — A/B/C/X/? 등급별 건수·승률·평균pts·합계pts
3. **학습 성장 곡선** — `▁▂▃▄▅▆▇█` 스파크라인 + 초기 50회 vs 최근 50회 Δ
4. **레짐별 성과** — RISK_ON/NEUTRAL/RISK_OFF 승률 게이지 바 + 평균pts

### KPI 상단 배지 4개
- 전체 승률 / A등급 승률 / 캘리브레이션 점수 / 학습 효과 Δ

### 종합 평가 배너 기준
- A등급 승률 ≥60% + 전체 ≥53% → ✅ 학습 효과 확인
- 전체 ≥50% → ⚡ 개선 중
- 전체 <50% → ⚠️ 모델 재점검 권장

---

## 🧠 자가학습 모니터 패널 (신규)

| 항목 | 내용 |
|---|---|
| **위치** | 중앙 탭 5번째 "🧠 자가학습" |
| **LearningPanel** | `dashboard/main_dashboard.py` `class LearningPanel` |
| **update_learning()** | `DashboardAdapter.update_learning(data)` → `learn_panel.update_data(data)` |
| **_gather_learning_stats()** | `main.py` — SGD/GBM/버퍼 통계 수집 후 매분 호출 |
| **_verified_today** | 당일 검증 건수 누적 카운터 (15:40 리셋) |
| **_horizon_counts** | `OnlineLearner._horizon_counts` — 호라이즌별 학습 건수 |

### 패널 구성
1. **요약 카드 4개** — 오늘 검증 건수 / SGD 50분 정확도(색상) / GBM 마지막 재학습 / 데이터 축적%
2. **SGD 섹션** — GBM↔SGD 블렌딩 그라데이션 바 + 6개 호라이즌 카드(정확도/학습건수/배지)
3. **GBM 섹션** — 마지막 재학습 / 재학습 횟수 / 다음 스케줄 + 5000행 축적 진행 바
4. **예측 버퍼 테이블** — 6 호라이즌 × (정확도 / 게이지 / 추세▲▼━)

### 정확도 색상 기준
- ≥62%: 초록 (SGD 비중 증가 중)
- 55~62%: 청록
- 48~55%: 주황
- <48%: 빨강 (SGD 비중 감소 중)

---

## 자가학습 파이프라인 현재 상태

| 항목 | 상태 |
|---|---|
| SGD 온라인 학습 (STEP 2) | ✅ **연결 완료** |
| GBM 배치 재학습 (STEP 3) | ✅ **연결 완료** (주간/월간 + 일일 마감) |
| SGD 블렌딩 (STEP 5) | ✅ **연결 완료** |
| features 전체 저장 (STEP 9) | ✅ **수정 완료** |
| BatchRetrainer DB 로드 | ✅ **raw_features 연동 완료** |
| 실제 학습 가동 조건 | ⏳ raw_candles 5000행 축적 필요 (2026-04-28 시작, 약 2.5주) |

---

## 2026-04-28 세션 주요 수정 (오전)

| 항목 | 수정 내용 |
|---|---|
| PredictionPanel dict reset 재발 수정 | `__init__` 277~279 줄의 reset이 `_build()` 호출 후에 위치해 항상 빈 dict → 선언을 `_build()` 앞으로 이동, `_build()` 내 중복 초기화 제거 |
| 시뮬레이션 타이머 조건부 시작 | `kiwoom=None`일 때만 `_start_sim_timer()` 호출. `update_price()` 첫 수신 시 `_stop_sim_timer()` 자동 호출 |
| sim timer 참조 저장 | `self._sim_timer`로 저장 (`stop()` 호출 가능하도록) |
| force_ready_for_test() 추가 | SIMULATION 모드 파이프라인 통과 검증용 더미 GBM 모델 주입 (`.pkl` 저장 없음) |
| 파이프라인 전체 검증 완료 [V3] | tick→분봉→pipeline→LONG 1계약 @ 1008.2 / 12:29 확인 |
| predictions.db 저장 확인 [V5] | 12:29·12:30 각 6 호라이즌 = 30행 확인 |
| trades.db 저장 누락 수정 | `_post_exit()`에 trades.db INSERT 추가. `position_tracker.close_position()` result에 `entry_ts`·`grade` 추가 |
| 대시보드 가격 동기화 | `run_minute_pipeline()` 진입 시 `dashboard.update_price(bar['close'])` 호출 추가 (기존엔 시뮬 타이머 ~388만 표시됨) |

## 2026-04-30 세션 주요 수정 (저녁)

| 항목 | 수정 내용 |
|---|---|
| 손익 추이 패널 신설 | 5층 로그 6번째 탭 "📊 손익 추이". 일별(60일)·주별(13주)·월별 `QTableWidget` 누적 P&L 테이블 + 요약 카드 6개 |
| 수익/손실 행 배경 | 수익일 연한 초록 / 손실일 연한 빨강 / 당일 황색 볼드 강조 |
| 월별 샤프 지수 | 월 내 일별 PnL 기반 연율화 샤프(√252), 색상 조건부(초록/노랑/빨강) |
| 주별 MDD | 주간 내 순차 누적 기준 최대 낙폭(원) 표시 |
| `fetch_pnl_history()` | db_utils.py 추가 — 체결 완료 거래 최근 90일 SELECT |
| `_refresh_pnl_history()` | main.py 추가 — _post_exit / daily_close / _restore_daily_state 3곳 자동 갱신 |

## 2026-04-30 세션 주요 수정 (오후)

| 항목 | 수정 내용 |
|---|---|
| PnL 탭 즉시 갱신 [B27/B28] | `_post_exit()` / `_execute_entry()` 내 `update_pnl_metrics()` + `append_pnl_log()` 직접 호출 추가 |
| ScreenScale 전면 재작성 | `fit_scale=min(sw/1680,sh/1000)` + `dpi_bonus=(dpr-1)×0.10`. 3840×2160@150%→1.45× 자동 적용 |
| 폰트 시인성 개선 | QTextEdit/배지/버튼 전 하드코딩 px → `S.f()` 교체, 5층 로그 12px 기준 |
| 재시작 연속성 [B29] | `trades.db` 당일 거래 → 주문/체결·손익 탭 `[복원]` 이탤릭 재표시, 세션 카운터(`session_state.json`), `restore_daily_stats()` 통계 재적산 |

## 2026-04-30 세션 주요 수정 (오전)

| 항목 | 수정 내용 |
|---|---|
| FILL 이상가격 이상점 진단 | 대시보드 `_sim_tick()` 시뮬 타이머가 키움 연결 전 창1 주문/체결 탭에 `FILL 매도 5계약 @388.48` 가짜 로그를 출력하는 것으로 확인 — 실제 거래 무관 |
| 시뮬 모드 완전 분리 [B26] | `MireukDashboard.__init__(sim_mode=True)` 파라미터 추가. `live` 모드(`sim_mode=False`)면 시뮬 타이머 자체 미생성. `DashboardAdapter` / `create_dashboard()` 동일하게 `sim_mode` 전파 |
| main.py 모드 연동 | `create_dashboard(sim_mode=(self.mode == "SIMULATION"))` 전달. `stop_sim_timer()` 호출을 `if self.mode == "SIMULATION":` 조건 내부로 이동 (live 모드에서 불필요한 호출 제거) |
| [SIM] 태그 추가 | `_sim_tick()` FILL/PENDING 로그 앞에 `[SIM]` 접두사 추가 — 시뮬 로그와 실거래 로그 육안 구분 가능 |

## 2026-04-29 세션 주요 수정 (오후 추가)

| 항목 | 수정 내용 |
|---|---|
| 멀티 호라이즌 `_preds_ui` 확률 오류 수정 | `main.py` STEP 5→UI 변환 시 `1-confidence` 근사 → `r["up"]`/`r["down"]`/`r["flat"]` 직접 참조로 교체. 3클래스 합≠1 오류 제거 |
| 시뮬레이션 호라이즌 다양성 수정 | `main_dashboard.py` `_sim_tick`: 단일 trend 기반 → 호라이즌별 σ `[0.06~0.20]` 독립 노이즈 적용 (장기일수록 불확실성 증가). `hold` 키 → `flat`으로 실거래 경로와 통일 |

## 2026-04-29 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| 주문/체결 탭 툴팁 | `dashboard/main_dashboard.py`: `_ORDER_TAB_TIP` 상수 추가 + `QToolTip` CSS + `setTabToolTip()` — 진입 흐름(①~⑤) + 청산 흐름(P1~P6) HTML 툴팁 |
| 외인 데이터 "-" 수정 [B16] | `InvestorData` 미임포트·미인스턴스화 확인 → `main.py` import 추가, `__init__`에 인스턴스화, STEP 4에 `fetch_all()` + `supply_demand=supply_feats` 전달 |
| 다이버전스 패널 배선 [B17] | `dashboard.update_divergence()` 미호출 → STEP 4 직후 rt_bias/fi_bias/contrarian/div_score 계산 후 매분 호출 |
| 외인 카드 업데이트 누락 [B18] | `DivergencePanel.update_data()`: fi_call/fi_put/fi_strangle 카드 setText 3줄 추가 |
| investor_data api 주입 | `connect_kiwoom()` 내 `self.investor_data._api = self.kiwoom` 추가 (실거래 시 TR 폴링 활성화) |
| investor_data 일일 리셋 | `daily_close()`에 `self.investor_data.reset_daily()` 추가 |
| 체크리스트 전부 X 버그 [B19] | 체크리스트 평가를 CB·시간 조건 블록 밖으로 분리 → FLAT+방향 있으면 항상 평가, 대시보드 항상 갱신 |
| 체크 미평가 시 X 표시 [B20] | `update_data()`: `checks.get(attr, None)` → None이면 회색 "—" 표시 (기존: False → 빨간 X) |
| 산출 수량 —— [B21] | `update_entry(qty=0)` 파라미터 추가 + `e_qty` 라벨 갱신 로직 추가 |
| 당일 진입 통계 고정 [B22] | `EntryPanel.update_stats()` + `DashboardAdapter.update_entry_stats()` 추가, STEP 9 후 매분 `position.daily_stats()` 기반 갱신 |
| 청산 패널 데이터 배선 [B23] | `main.py` STEP 8 직후 `update_position()` 추가 — PositionTracker 실제 값(`stop_price`, `tp1_price`, `tp2_price`, `entry_time`, `partial_1/2_done`) 전달 |
| ExitPanel.update_data() 재작성 [B24] | FLAT 상태 → `_reset_display()` "——" 표시 / LONG·SHORT: 실제 스톱·목표가 사용, 보유 시간 계산, PnL KRW 방향 반영, 부분청산 바 갱신 |
| 시뮬 루프 청산 패널 수정 [B25] | `status='LONG'` + `stop`/`tp1`/`tp2` 구조화, `partial1`/`partial2` 틱 기반 시뮬 |

## 2026-04-28 세션 주요 수정 (오후)

| 항목 | 수정 내용 |
|---|---|
| Path B DB 인프라 구축 | `utils/db_utils.py`에 `raw_candles`/`raw_features` 테이블 + save/get 함수 4개 추가. `config/settings.py`에 `RAW_DATA_DB` 경로 추가. STEP 4에서 매분 분봉·피처 저장 시작 — 13거래일 후 실제 모델 학습 가능 |
| CVD 틱 방향 수정 [B13] | FC0 FID10 부호(전일대비 방향)를 틱 방향으로 오해 → tick test(prev_price 비교, Lee-Ready 근사)로 교체. `realtime_data.py`에 `_prev_tick_price` 추가, bar dict에 `buy_vol`/`sell_vol` 누적 |
| 손절 exit price 보정 [B15] | `_check_exit_triggers(bar=)`에 bar 파라미터 추가. LONG 손절 시 `exit_price = max(stop_price, bar_low)` — close가가 아닌 손절가 기준 |
| 디버그 로그 8포인트 추가 | [DBG-F4] ATR+핵심피처 / [DBG-F6] 호라이즌예측 / [DBG-CB] CB상태 / [DBG-F7] 진입조건 / [DBG-F7a] 체크리스트 / [DBG-F7b] 사이저 / [DBG-F8] 포지션PnL / [DBG-STOP] 하드스톱 |
| DEBUG 레이어 레벨 수정 | `utils/logger.py`: LOG_LEVEL=INFO여서 DEBUG 레이어도 INFO → debug() 차단. `logging.DEBUG` 고정으로 수정 |
| 대시보드 신뢰도 갱신 | `PredictionPanel.update_data(conf=)` 파라미터 추가 → `lbl_conf` "신뢰도 76.8%" 표시 |
| 대시보드 호라이즌/체크리스트 갱신 | `run_minute_pipeline`에서 `update_prediction()` + `update_entry()` 매분 호출 추가 |
| 대시보드 5층 로그 배선 | `main.py __init__`에서 `log_manager.subscribe()` SYSTEM/TRADE/LEARNING 콜백 등록 |
| 대시보드 PnL 실시간 갱신 | `LogPanel.update_pnl_metrics()` 추가 + `_pnl_vals`/`_pnl_bars` dict 저장 (이전엔 로컬 변수 → 업데이트 불가) |
| 실거래 검증 결과 | LONG @1008.40 stop=1007.65, ATR floor stop_dist=0.75pt 확인 [V6 DONE], 체크리스트 8/9 통과 |

## 2026-04-27 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| 근월물 코드 | `GetFutureCodeByIndex(0)` 0순위 추가 → `A0166000` 확정 (구: 날짜계산 fallback `101W06`) |
| 실시간 타입명 | `RT_FUTURES="FC0"` → `"선물시세"`, `RT_FUTURES_HOGA="FH0"` → `"선물호가잔량"` |
| GetRepeatCnt | `or rq_name` fallback 제거 → `""` 빈 문자열 그대로 전달 |
| EmergencyExit | `get_position()` 없음 → 속성 직접 읽기 + `set_futures_code()` 추가 |
| run_minute_pipeline | candle `ts`(datetime) → `strftime` 문자열 변환 |
| 대시보드 | PredictionPanel `_build()` 맨 앞에서 dict 초기화 (IDE 순서 복구 방지) |
| 대시보드 | `mk_val_label` `align` 파라미터 추가 |
| 대시보드 | 헤더 우측 커밋 해시 표시 (해상도 아래) |

## 2026-04-26 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| TR 코드 | OPT10080 → **OPT50029** (`config/constants.py`) |
| COM 콜백 | 메타데이터만 저장 + QEventLoop.quit(), 실제 API 호출은 exec_() 복귀 후 |
| GetRepeatCnt | 2번째 파라미터: rq_name → **record_name** |
| 근월물 조회 | GetFutureList() 우선 → GetMasterCodeList("10") → 날짜 계산 fallback |
| GetCommDataEx | → **GetCommData** (서명 오류 수정) |
| 대시보드 | `create_dashboard()` 시작 시 show(), 5분마다 대기 상태 로그 |

---

## 현재 차단 이슈

| 이슈 | 원인 | 상태 |
|---|---|---|
| OFI 영구 0 (B14) | 선물호가잔량 콜백 신설 + `sopt_type="1"` 추가 등록으로 해결 | ✅ 해결 |
| CVD tick test 효과 | 다음 실행에서 buy_vol/sell_vol이 실제 분리되는지 [V8] 확인 필요 | ⏳ 검증 대기 |
| OPT50029 초기 분봉 rows=0 | 모의투자 서버에서 OPT50029 미지원 확인. SetRealReg(A0166000)으로 전환 완료 | ✅ 해결 |
| [DBG] 출력문 정리 | 디버그 print 잔존 | 🔧 안정화 후 제거 |
| Walk-Forward 26주 | 실거래 데이터 미확보 | ⏳ 장기 과제 |
| Path B 모델 학습 | 13거래일 raw_candles 축적 후 가능 (2026-04-28 축적 시작) | ⏳ 약 2.5주 후 |

---

## 성능 목표

| 버전 | 정확도 | Sharpe | MDD |
|---|---|---|---|
| v6 (기준) | 75~80% | 2.5~3.0 | — |
| v6.5 (현재) | 80~85% | 3.0~3.5 | — |
| v7.0 (목표) | 82~88% | 3.5~4.0 | -30% |

---

## 형제 프로젝트 참조

- 한량이(주식 자동매매): `auto_trader_kiwoom/dev_memory/CURRENT_STATE.md`
## 2026-05-06 최신 반영

| 항목 | 상태 |
|---|---|
| 체결 소스 오브 트루스 | `OnReceiveChejanData` + pending order 매칭 경로를 기준으로 추적하도록 보강됨 |
| startup broker sync | `OPW20006` blank placeholder row-only 응답을 hard mismatch가 아니라 FLAT 후보로 해석하도록 보정됨 |
| futures balance 진단 | `OPW20006-REQ`, `OPW20006-RESP`, `OPW20006-DIAG` 추가 |
| 주문 경로 진단 | `EntryAttempt`, `EntrySendOrderResult`, `PendingOrder`, `EntryPendingCreated`, `OrderMsgDiag` 추가 |
| Chejan/잔고 진단 | `ChejanDiag`, `ChejanFlow`, `ChejanMatch`, `ChejanDedup`, `EntryFillFlow`, `ExitFillFlow`, `BalanceChejanFlow`, `BrokerSyncFlatPlaceholder` 추가 |
| 포지션 복원 메타 | `position_state.json`에 `last_update_reason`, `last_update_ts` 저장 및 `PositionDiag` 복원 로그 추가 |
| 오늘 확인된 유력 원인 | startup sync 차단은 blank placeholder row 오판 가능성이 가장 높음 |
| 잔여 리스크 | `2026-05-06 10:48:19` 불일치의 정확한 과거 원인은 다음 실행 로그로 최종 증명 필요 |
| 운영 리스크 | CB 저정확도 halt 및 strategy gate 정책은 별도 검토 필요 |
# 2026-05-06 추가 업데이트 (실시간 잔고 패널 연결/보정)

| 항목 | 현재 상태 |
|---|---|
| 좌측 상단 UI | `계좌번호` / `전략명` 콤보와 저장 버튼이 헤더 하단에 정렬되어 있음 |
| 좌측 컬럼 구조 | 상단 `실시간 잔고`, 하단 `멀티 호라이즌 예측 + 파라미터 분석` 2단 분할 완료 |
| 실시간 잔고 패널 | 라이브 게이지 + 합계 6개 + 종목별 잔고 테이블 UI 추가 완료 |
| 잔고 데이터 연결 | `OPW20006` 결과가 startup sync 직후와 잔고 Chejan 이후 대시보드로 전파되도록 연결 완료 |
| 공란 응답 보정 | `OPW20006` summary가 전부 blank일 때 잔고행 합산 + `daily_stats()` 기반 fallback 표시 적용 |
| 진단 로그 | `[OPW20006-SUMMARY-BLANK]`, `[BalanceUIFallback]` 추가 |
| 현재 한계 | `OPW20006` 단독으로는 합계 6개가 항상 채워지지 않음. 장후/무포지션에서 `rows=0`, summary blank 케이스 존재 |

### 최신 확인 로그

- `2026-05-06 18:51:29 [BalanceUIFallback] summary blank from OPW20006 ... applied={'총매매': '0', '총평가손익': '0', '실현손익': '0', '총평가': '0', '총평가수익률': '0.00', '추정자산': '0'}`
- 현재 상단 패널은 더 이상 빈 대괄호를 표시하지 않고, 값이 없으면 공란/0 fallback으로 유지됨.
## 2026-05-08 최신 반영 - Ensemble Upgrade / Effect Validation

| 항목 | 현재 상태 |
|---|---|
| Sprint 1 | 완료. baseline 저장, 5레벨 호가 수신 검증, `MLOFI / microprice / queue dynamics` 구현 및 실시간 로그 검증 완료 |
| Sprint 2 | 완료. `FeatureBuilder` 연결, `adaptive gating` 프로토타입 반영, baseline vs enhanced A/B 백테스트 스크립트/리포트 생성 완료 |
| Sprint 3 | 대부분 완료. `meta_labels`, `meta gate`, calibration 리포트 자동 생성, `ensemble_decisions` 저장 강화 완료 |
| Sprint 4 | 부분 완료. `toxicity gate`, rollout readiness 리포트, shadow 운영 기준 추가 완료 |
| 원확률 저장 | `predictions` 테이블에 `up_prob/down_prob/flat_prob` 저장 경로 및 migration 완료. 재시작 이후 신규 예측은 원확률 저장 확인 |
| 효과 검증 UI | 대시보드 중간 패널에 `A/B / Calibration / Meta Gate / Rollout` 탭 추가 완료 |
| 자동 리포트 주기 실행 | `main.py`에서 `Calibration/Meta/Rollout=15분`, `A/B=30분` 주기로 리포트 자동 재생성 및 스냅샷 누적 |
| 이력 저장 | `effect_monitor_history.json` 에 효과 검증 추이 스냅샷 누적 시작 |
| 탭 툴팁 | `EfficacyPanel` 탭바에 직접 툴팁 부착하도록 수정 완료. 초기 오배선 버그 수정됨 |
| 현재 운영 판단 | rollout 추천 단계는 아직 `shadow` |

### 현재 관측 지표 (2026-05-08 세션 마감 기준)

- `A/B pnl delta`: `-3.60pt`
- `A/B accuracy delta`: `-0.10%p`
- `Calibration ECE`: `0.399783`
- `Meta labels`: `34`
- `Meta best match rate`: `41.18%`
- `Rollout stage`: `shadow`

### 현재 판단

- 기능 구현/배선 자체는 큰 축에서 완료됨
- 다만 실전 승격 관점에서는 `Calibration` 과 `A/B delta` 가 아직 약점
- 다음 우선순위는 `temperature scaling 기반 calibration 개선`, `changed sample 53건 분석`, `meta label 추가 축적 후 rollout 재평가`

---

## 2026-05-11 Cybos 자동 로그인 확정

| 항목 | 값 |
|---|---|
| 스크립트 | `scripts/cybos_autologin.py` |
| 실행 파일 | `C:\DAISHIN\STARTER\ncStarter.exe /prj:cp` |
| 비밀번호 | `PASSWORD_OVERRIDE = "amazin16"` (하드코딩) |
| 비밀번호 입력 좌표 | `(971, 695)` |
| 모의투자 접속 버튼 | `(1416, 645)` |
| 팝업 최소 대기 | 10초 |
| Enter 후 처리 | 3초 후 `sys.exit(0)` (창 탐지 → 버튼 클릭 → 소멸 시 즉시 종료) |
| **상태** | ✅ 정상 동작 확인 (2026-05-11) |

---

---

## 2026-05-16 업데이트 (41차)

### Threshold 재보정

| 항목 | 이전값 | 변경값 | 비고 |
|---|---|---|---|
| 1m threshold | 0.0002 (0.02%) | 0.0005 (0.05%) | 12틱 |
| 3m threshold | 0.0003 (0.03%) | 0.0008 (0.08%) | 19틱 |
| 5m threshold | 0.0004 (0.04%) | 0.0011 (0.11%) | 26틱 |
| 10m threshold | 0.0006 (0.06%) | 0.0016 (0.16%) | 38틱 |
| 15m threshold | 0.0008 (0.08%) | 0.0022 (0.22%) | 53틱 |
| 30m threshold | 0.0012 (0.12%) | 0.0032 (0.32%) | 77틱 |

근거: 5월 초 일중 고저폭 ~96pt 기준 σ_1min≈1.47pt → 각 threshold ≈ 0.4~0.5σ (FLAT 비율 29~37% 목표)

### Dashboard 상태

| 항목 | 현재 상태 |
|---|---|
| PnlHistoryPanel 체크박스 | 순방향/역방향 토글 체크박스 추가 (탭바 우측 코너) |
| PredictionPanel 툴팁 | HTML 리치 포맷 전환 (SHAP 윈도우 테이블, HZ 설명 전체 재작성) |
| CB 툴팁 | 슬랙 알림 내용 ③항목 추가 |
| `DashboardAdapter.chk_slack` | ✅ 노출 수정 완료 (B51 핫픽스) |

### Threshold Monitor

- `_log_threshold_monitor()` 추가 — GBM 재학습 완료 시 + 30분 주기로 ATR 동적 threshold vs Static 비교 기록
- 모델 AI탭에 `✅ 안정` / `⚠ 초과` 판정 자동 기록

### EmergencyExit pending_registrar

- CB/KillSwitch 비상청산 주문 시 `pending_registrar` 콜백으로 `EXIT_FULL` pending 선등록
- Chejan 체결이 "외부체결(HTS/수동)"로 오분류되지 않도록 방지

### PositionTracker same-side sync 보강

- same-side broker sync 시 기존 신호 등급(A/B/C) 보존 — BROKER로 덮어쓰기 방지
- 이미 실행된 TP 플래그(partial_1/2/3_done) 보존 — Chejan이 와도 재발동 방지

### 현재 기동 상태

| 항목 | 상태 |
|---|---|
| 자동 로그인 | ✅ 정상 (`start_mireuk.bat`) |
| Cybos 연결 | ✅ 성공 (ServerType=1 모의투자) |
| B51 크래시 | ✅ 수정 완료 |
| Qt 이벤트 루프 | 재기동 후 확인 필요 |

---

## 2026-05-16 업데이트 (46차)

### PnlHistoryPanel 버그 4종 수정

| 항목 | 이전 | 이후 |
|---|---|---|
| 역방향 체크박스 | forward_pnl 전체 표시 (의미론 오류) | reverse_entry_enabled=1 행만 필터링 |
| 순+역 모두 체크 | exec+fwd 합산 (2배) | 전체 행의 pnl_krw (정상) |
| 총 손익 | broker P&L × 거래 수 중복합산 | 고유 날짜 단위 1회 합산 |
| 체크박스 재시작 | _save_ui_prefs()가 pnl_cb_* 키 삭제 | 읽고-병합-쓰기로 키 보존 |
| P/L 원 별표 | "6,267,000원 ★" | "6,267,000원" |

### 미니선물 pt_value 버그 수정 (B53)

| 항목 | 변경 |
|---|---|
| TRADE_PNL_FORMULA_VERSION | 3 → 4 (기존 레코드 재마이그레이션 강제) |
| normalize_trade_pnl | pt_value 파라미터 추가 (기본값 250,000) |
| _get_pt_value_from_prefs() | ui_prefs.json → symbol_code → get_contract_spec()["pt_value"] |
| _migrate_trades_db | _get_pt_value_from_prefs()로 pt_value 결정 |
| main._trade_metrics_pair | self._pt_value 전달 |

재시작 시 v4 마이그레이션 자동 실행 → 5/14 기준 14.5M→2.9M (5배 정상화).

### 잔여 이슈

- 5/14 2.9M vs 실제 ~1.5M: qty 과다 기록 문제 별도 분석 필요

---

## 2026-05-17 업데이트 (47~48차 + DB 초기화)

### trades.db 초기화

| 항목 | 내용 |
|---|---|
| 초기화 일시 | 2026-05-17 |
| 백업 파일 | data/db/trades_backup_20260517.db (92KB) |
| 초기화 내용 | trades 191건, daily_stats 10행, daily_broker_pnl 2행 전체 삭제 |
| 목적 | 2026-05-19(월)부터 오염 없는 DB로 손익추이 유효성 검증 |
| 검증 포인트 | 신규 체결 거래가 pt_value=50k 기준으로 정확히 기록되는지, qty 과다 기록 없는지 |

### 손익추이 주별/월별 탭 설계 확정

| 탭 | P/L 원 소스 | MDD |
|---|---|---|
| 일별 | broker 정산 우선, 없으면 DB | 일별 DB (broker 있는 날 broker 적용) |
| 주별 | DB pnl_krw 일관 | 일별 DB 집계 (trade 진동 제거) |
| 월별 | DB pnl_krw 일관 | Sharpe만 표시 |
| 요약 헤더 | broker 정산 고유 날짜 합산 | 전체 MDD (_mdd) |

### 현재 기동 상태

| 항목 | 상태 |
|---|---|
| trades.db | 초기화 완료 (0건) |
| 백업 | data/db/trades_backup_20260517.db |
| 다음 첫 거래 | 2026-05-19(월) 시작 예정 |
| 검증 모드 | 오염 없는 DB로 손익추이 유효성 평가 |
## 2026-05-18 상태 업데이트 (GBM/SHAP 운영 패치)

### 1. GBM 재학습 산출물/런타임 정합성
- `learning/batch_retrainer.py`가 이제 `gbm_*.pkl`, `scaler_*.pkl`, `feature_names.pkl`를 함께 저장한다.
- `MultiHorizonModel._load_all()`과 배치 재학습 산출물 포맷이 일치하도록 맞춰져, warmup/manual retrain 후 런타임 reload 경로가 정상화됐다.

### 2. 좌하단 멀티 호라이즌 예측 패널
- `파라미터 상관계수`는 importance 요약 문자열이 아니라 최근 feature history 기반 실제 상관계수 문자열(`rho`)을 사용한다.
- `파라미터 중요도`는 SHAP cache가 있으면 SHAP 기준으로 덮어쓰도록 배선됐다.
- 단, 현재 운영 모델의 `feature_names.pkl`에 따라 일부 피처(`foreign_call_net`, `foreign_retail_divergence`, `program_non_arb_net`)가 SHAP 대상에서 빠질 수 있으므로 다음 managed-set 재학습 검증이 필요하다.

### 3. 재시작 직후 restored/live 분리
- 재시작 시 `raw_features` 기반 복원값과 당일 live 버퍼를 분리하는 로직이 들어갔다.
- 상관계수와 SHAP는 저장 데이터로 즉시 복원 가능하며, 이후 live buffer가 쌓이면 실시간 계산으로 전환된다.

### 4. 중패널 `동적 피처 (SHAP)` 상태
- CORE 3개/동적 TOP3/전체 피처 순위/쿨다운/교체 이력 패널이 실제 `ShapTracker` 데이터와 연결됐다.
- 운영 플로우 카드 추가:
  - `추천 1 적용 + 재학습`
  - `현재 세트 재학습`
  - `세트 원복`
- managed feature set은 `data/db/shap_feature_registry.json`으로 관리하며, retrain 시 batch retrainer가 이를 읽어 active feature set 기준으로 학습한다.

### 5. 오늘 확인된 startup 이슈와 현재 최종 블로커
- 수정 완료:
  - `DB_DIR` import 누락 `NameError`
  - `shap_tracker_history.json` 과 현재 feature length 불일치로 인한 `IndexError`
- 현재 최종 블로커:
  - SHAP/UI 패치가 아니라 `U-CYBOS/CYBOS Plus is not connected` 브로커 세션 미연결
  - 앱은 SHAP 패치 구간을 통과한 뒤 broker connect 단계에서 종료된다.
## 2026-05-22 (82차) — Micro Regime Warmup UI

### 배경

10:03:43 헤더 `횡보장` 표시를 추적한 결과, 실제로는 `10:03:00` 1분봉 갱신 시점의 미시 레짐이 유지된 것이었고, 당시 `ADX=15.0` 은 실측이 아니라 버퍼 부족 fallback 값이었다. 장중 재시작/초기 분봉 구간에 미시 레짐 해석 신뢰도가 낮다는 점을 UI에서 드러낼 필요가 확인되었다.

### 현재 상태

| 항목 | 상태 |
|---|---|
| `MicroRegimeClassifier` 워밍업 메타 | **완료** — `L1 TR/ATR seed` / `L2 ADX warmup` / `L3 ATR avg warmup` / `READY` 계산 |
| 헤더 워밍업 표시 | **완료** — `lbl_micro_regime` 아래 상태 문구 + progress bar 추가 |
| 남은 시간 표시 | **완료** — `remaining_bars` 기준 `N분 남음` 노출 |
| 장중 재시작 초기 해석 보조 | **완료** — 워밍업 중에는 상단에서 레짐 과신 방지 |
| ATR avg 준비용 버퍼 길이 수정 | **완료** — close/high/low buffer 상한 확장 |
| 실 UI 런처 검증 | **미완료** — 다음 기동 시 헤더 배치와 가독성 확인 필요 |

### 구현 파일 (82차)

| 파일 | 변경 내용 |
|---|---|
| `collection/macro/micro_regime.py` | 워밍업 상태 계산 + 버퍼 길이 수정 + 파일 정리 |
| `main.py` | `dashboard.update_micro_regime_warmup(_mr.get("warmup"))` 호출 |
| `dashboard/main_dashboard.py` | 미시 레짐 배지 아래 워밍업 상태 라벨 / progress bar 추가 |

### 다음 확인 사항

1. `start_mireuk.bat` 재기동 후 헤더에서 워밍업 바가 정상 위치/색상으로 보이는지 확인
2. 장중 재시작 직후 `L1 → L2 → L3 → READY` 전환이 실제 시간 흐름과 맞는지 SYSTEM/UI 로그 대조
3. 워밍업 완료 전 `횡보장/추세장` 텍스트는 유지되더라도 사용자 해석이 충분히 보정되는지 판단

---
