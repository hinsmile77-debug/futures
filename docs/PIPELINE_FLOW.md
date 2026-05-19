# 미륵이 매분 파이프라인 전체 흐름

> 최종 업데이트: 2026-05-19  
> 기준 커밋: 6순위 안전장치 구현 완료 (Mid-Conf·Brier·루프브레이커·DNA·CoreHealth·ShadowSession·ContrarianMode)

---

## 시스템 기동 (08:45)

```
08:45  TradingSystem.__init__()
       ├─ CircuitBreaker 초기화
       │     Mid-Conf Blind Spot Tracker  (_mid_conf_wrong_streak)
       │     Brier Score 버퍼             (_brier_buf, _brier_penalty_active)
       │     재시작 루프 브레이커          (_daily_halt_count)
       ├─ MarketDNA 초기화       [4순위]  safety/market_dna.py
       ├─ CoreHealthScore 초기화  [5순위]  features/core_health.py
       ├─ ShadowSessionTracker 초기화  [6순위]  safety/shadow_session.py
       └─ ContrarianModeTracker 초기화  [6순위]  safety/contrarian_mode.py

08:55  매크로 수집 → 레짐 확정 (NEUTRAL / RISK_ON / RISK_OFF)
       실시간 구독 사전 시작 (FutureCurOnly tick / FutureJpBid hoga)

09:00  장 시작 — 매분 파이프라인 루프 진입
```

---

## STEP 1 — 과거 예측 검증

**파일**: `main.py:2168`

```
pred_buffer.verify_and_update(ts, close)
  ↓
필터: 30m 호라이즌 AND conf > 0.38 AND 이번 세션 예측(_session_start_ts)
  ↓
circuit_breaker.record_accuracy(correct, confidence)
  │
  ├─ [2순위] Brier Score 누적
  │     brier_i = (conf - actual)²
  │     이동평균 (최근 10건) > 0.35  → WARNING 로그
  │     이동평균 > 0.45              → brier_penalty_active = True
  │                                      → STEP 7에서 사이즈 ×0.5
  │
  ├─ [1순위] Mid-Conf Blind Spot Tracker
  │     0.60 ≤ conf < 0.85 AND 오답 → mid_conf_wrong_streak +1
  │     7연속                        → CB③ strict 모드 (임계값 35% → 50%)
  │     기타 경우                    → 리셋
  │
  ├─ 고신뢰(conf ≥ 0.85) 오답 연속   → high_conf_wrong_streak
  │     5연속                        → CB③ strict 모드 (임계값 35% → 50%)
  │
  └─ acc30m 계산 (20샘플 이상)
        effective_min = 0.50  (high_conf or mid_conf streak ≥ 임계값)
        effective_min = 0.35  (정상)
        acc < effective_min → cb3_warn_count +1
          1회: CB③ 경고 (슬랙)
          2회: _trigger_halt()
                [3순위] daily_halt_count +1
                1회: restart_size_mult = 1.0  (정상)
                2회: restart_size_mult = 0.5  (50% 축소)
                3회: restart_size_mult = 0.0  (완전 관망)
        acc ≥ effective_min → cb3_warn_count 리셋

horizon_calibrator.record(horizon, conf, correct)
daily_consolidator.record(zone, correct)  # 5m 호라이즌만
```

---

## STEP 2 — SGD 온라인 자가학습

**파일**: `main.py:2193`, `learning/online_learner.py`

```
검증된 예측 → online_learner.learn(horizon, x, actual, predicted)
  버킷: short (1m/3m/5m) / long (10m/15m/30m) 독립 학습
  accuracy > 62% → SGD 비중 +2% (최대 50%)
  accuracy < 48% → SGD 비중 -2% (최소 10%)

stuck 발생 분봉 (비정상 체결) → 학습 스킵 (레이블 오염 방지)
```

---

## STEP 3 — GBM 배치 재학습

**파일**: `main.py:2239`, `learning/batch_retrainer.py`

```
트리거: 주간/월간 스케줄 OR 세션 재시작 직후 (_warmup_retrain_pending)
daemon thread 분리 → 메인 스레드 블로킹 없음
완료 시 QTimer.singleShot(0, _on_gbm_retrain_done) — UI 스레드 안전 로드
_gbm_retrain_running 플래그로 중복 실행 차단
```

---

## STEP 4 — 피처 생성

**파일**: `main.py:2268`, `features/feature_builder.py`

```
FeatureBuilder.build(bar, supply_demand, macro, option)
  ├─ CORE 3종
  │     CVD 다이버전스   features/technical/cvd.py
  │     VWAP 위치        features/technical/vwap.py
  │     OFI 불균형       features/technical/ofi.py
  │     실패 시 _core_fail_streak[피처] +1
  │     3회 연속 → ERROR 로그 + CB 경보 콜백
  ├─ 수급 피처 (투자자별 매매동향)
  ├─ 옵션 피처 (PCR / GEX / ATM OI)
  ├─ 매크로 피처 (VIX / SP500 / KRW)
  └─ 기술 피처 (ATR / Hurst / microstructure)

NaN/Inf 가드: vwap_position, cvd_direction, ofi_pressure → 0 교정
분봉·피처 DB 저장 (save_candle / save_features)

── STEP 4 직후 ─────────────────────────────────────────────────────

[5순위] CoreHealthScore.update()                    features/core_health.py
  입력: cvd_streak, vwap_streak, ofi_streak, z_warn_count
  점수 계산 (0~100):
    ① streak=0인 CORE 피처당 25점 (3종 × 25 = 75점 기본)
    ② z-score 경고 0개  → +10점
    ③ 최근 5분 실패율 0% → +15점
    streak 1회당 -5점 페널티
  판정:
    score < 70  → size_mult = 0.0  (A/B 등급도 진입 금지)
    70~85       → size_mult = 0.5
    ≥ 85        → size_mult = 1.0

[4순위] MarketDNA.add_bar()                          safety/market_dna.py
  적용 구간: 09:00~09:04 (5봉 수집 중에만)
  입력: direction, volume, z_score_warn_count, core_ok_count
  5봉 완성 후 diagnose():
    ① 첫 3봉 방향 일치율 < 2/3         → 이상
    ② 첫 1분봉 거래량 > 20일 평균 150% → 이상
    ③ 5봉 합산 z-score 경고 ≥ 2        → 이상
    ④ CORE 평균 정상 수 < 2             → 이상
    이상 ≥ 3개 → "조심의 날" dna_mult = 0.25
    이상 < 3개 → dna_mult = 1.0

PSI 기반 RegimeFingerprint 드리프트 감지
미시 레짐 업데이트 (MicroRegimeClassifier: ADX/ATR)
circuit_breaker.record_atr(atr_ratio)

[6순위] ShadowSessionTracker.update()                safety/shadow_session.py
  입력: ts_dt, acc30m, core_health_score, z_warn_count
  게이트 조건:
    ① acc30m ≥ 40%
    ② core_health_score ≥ 70
    ③ 최근 5분 z-score 경고 합계 < 2
  전이:
    SHADOW → (09:40 이전, 3/3 통과) → LIVE
    SHADOW → (09:40 초과, 미통과)   → BLOCKED

[6순위] ContrarianModeTracker.update()               safety/contrarian_mode.py
  입력: acc30m, signal_direction, regime
  발동 조건:
    ① acc30m < 25%
    ② 동방향 연속 ≥ 10회
    ③ NEUTRAL 레짐
  전이:
    WATCHING → (2/3 충족) → ARMED
    ARMED    → (3/3 충족) → ACTIVE  (역베팅 가상 PnL 집계 시작)
    ACTIVE   → (acc30m ≥ 40% 또는 방향 전환) → CLEARED → WATCHING

dashboard.experiment_gate_panel 갱신 (30초 주기)
```

---

## STEP 5 — 멀티 호라이즌 예측

**파일**: `main.py:2441`, `model/multi_horizon_model.py`

```
GBM predict_proba() → 6개 호라이즌 (1m/3m/5m/10m/15m/30m)
  극단 z-score 감지 (|z| > 임계값) → model.last_z_warn_count 저장
  결과에 extreme_count 포함

SGD blend:
  blended = online_learner.blend_with_gbm(gbm_proba, sgd_proba, horizon)
  GBM 미학습 → SGD-only 또는 1/3 bootstrap

self._last_ensemble_direction = direction   ← Contrarian 동방향 추적용
```

---

## STEP 6 — 앙상블 진입 판단

**파일**: `main.py:2515`, `model/ensemble_decision.py`

```
horizon_calibrator 보정 (호라이즌별 정확도 반영)
EnsembleDecision.evaluate(horizon_proba)
  가중치: 1m(10) / 3m(15) / 5m(20) / 10m(20) / 15m(20) / 30m(15)
  HorizonDecorrelator: 상관계수 역수 기반 동적 가중치 조정 (30분 롤링)
  → direction / confidence / grade

MetaGate.evaluate() → action (take/reduce/skip)

EntryChecklist.evaluate()
  9항목 채점 → grade (A/B/C/X)
    A: 6개 이상 → size_mult 1.5
    B: 4~5개    → size_mult 1.0
    C: 2~3개    → size_mult 0.6
    X: 1개 이하 → 진입 금지

레짐-파라미터 오버라이드 적용 (§14)
ExecutionGovernor 사전 평가
circuit_breaker.record_signal(direction)
```

---

## STEP 7 — 진입 실행

**파일**: `main.py:2700`

```
grade ≠ X AND circuit_breaker.is_entry_allowed()
  │
  ├─ [5순위] CoreHealth 차단 체크
  │     core_health.score < 70 → grade = X (진입 차단, 로그)
  │
  └─ PositionSizer.compute()                strategy/entry/position_sizer.py
        confidence / atr / regime / grade_mult / adaptive_kelly_mult
        ──────────────────────────────────────────────────────────
        core_health_mult = CoreHealth.size_mult     [5순위]
        brier_mult       = CB.brier_size_mult       [2순위]  0.5 or 1.0
        restart_mult     = CB.restart_size_mult     [3순위]  0.0/0.5/1.0
        dna_mult         = MarketDNA.size_mult      [4순위]  0.25 or 1.0
        ──────────────────────────────────────────────────────────
        safety_total = core_health × brier × restart × dna
        raw_qty = (base_risk × conf_mult × regime_mult × grade_mult
                   × kelly_mult × safety_total) / stop_risk
        quantity = clamp(raw_qty, min_qty, MAX_CONTRACTS)
        ※ core_health=0.0 또는 restart=0.0 → 즉시 0계약 반환

ProfitGuard 수익 보존 체크 (진입 직전)
ShadowSession.is_blocked() → True이면 진입 추가 차단 검토
브로커 주문 실행 (모의투자 / 실전)
```

### 안전 배수 조합 예시 (2026-05-19 재현)

| 배수 | 사유 | 값 |
|------|------|----|
| core_health_mult | VWAP+OFI 탈락 (score 50점) | 0.5 |
| brier_mult | 09:40 전후 과신 패널티 발동 | 0.5 |
| restart_mult | 2회차 재시작 | 0.5 |
| dna_mult | 조심의 날 (이상 3/4) | 0.25 |
| **합계** | **0.5 × 0.5 × 0.5 × 0.25** | **0.031 → 사실상 0계약** |

---

## STEP 8 — 청산 트리거 감시

**파일**: `main.py:3104`

```
P1 강제청산      15:10 오버나이트 금지
P2 TP1/TP2 도달  1차·2차 목표가
P3 Trail Stop    고점/저점 대비 추적
P4 Time Exit     TimeExitManager (장중 시간 기반)
P5 ProfitGuard   일일 수익 보존 한도
P6 CB 긴급청산   CB⑤ API 지연 또는 CB② 손절 연속
```

---

## STEP 9 — 예측 DB 저장

**파일**: `main.py:3173`

```
pred_buffer.add(ts, horizon_proba, features)
  → 다음 분봉 STEP 1에서 verify_and_update()로 검증됨

Champion-Challenger Shadow 실행 (STEP 9 이후 훅)
  각 도전자 전략에 현재 신호 피드 → 가상 체결 집계
```

---

## 15:10 — 강제 청산

```
오버나이트 절대 금지 — 수익/손실 무관 전량 청산
```

---

## 15:40 — 일일 마감 및 리셋

```
online_learner 일일 마감
SHAP 피처 심사 (daily_consolidator.consolidate)
reset_daily():
  circuit_breaker      ← Mid-Conf·Brier·HALT 카운터 포함
  market_dna
  core_health
  shadow_session
  contrarian_mode
  _last_ensemble_direction = 0
  feature_builder / micro_regime_clf / investor_data
  pcr_store / option_chain_snap / position / profit_guard
  online_learner / latency_sync
```

---

## 신규 모듈 위치 참조

| 순위 | 모듈 | 파일 |
|------|------|------|
| 1순위 | Mid-Conf Blind Spot Tracker | `safety/circuit_breaker.py` |
| 2순위 | Brier Score 실시간 추적 | `safety/circuit_breaker.py` |
| 3순위 | 재시작 루프 브레이커 | `safety/circuit_breaker.py` |
| 4순위 | 장 시작 5분 DNA 진단 | `safety/market_dna.py` |
| 5순위 | CORE Health Score | `features/core_health.py` |
| 5순위 | Sizer 안전 배수 연동 | `strategy/entry/position_sizer.py` |
| 6순위 | Shadow Session 트래커 | `safety/shadow_session.py` |
| 6순위 | Contrarian Mode 트래커 | `safety/contrarian_mode.py` |
| 6순위 | 실험 게이트 대시보드 | `dashboard/panels/experiment_gate_panel.py` |

---

## CB 상태 조합 매트릭스

| daily_halt_count | restart_size_mult | 운영 모드 |
|-----------------|-------------------|-----------|
| 0 | 1.0 | 정상 |
| 1 | 1.0 | 정상 (1회 HALT 후 재진입) |
| 2 | 0.5 | 50% 축소 모드 |
| ≥ 3 | 0.0 | 완전 관망 (진입 차단) |

| brier_avg | brier_size_mult | 상태 |
|-----------|----------------|------|
| < 0.35 | 1.0 | 정상 |
| 0.35~0.45 | 1.0 | 경고 (로그만) |
| ≥ 0.45 | 0.5 | 패널티 발동 |

| core_health.score | size_mult | 진입 가능 |
|-------------------|-----------|-----------|
| ≥ 85 | 1.0 | 가능 |
| 70~84 | 0.5 | 가능 (절반) |
| < 70 | 0.0 | 불가 |

| MarketDNA 이상 수 | dna_mult | 모드 |
|------------------|---------|------|
| 0~2개 | 1.0 | 정상 |
| ≥ 3개 | 0.25 | 조심의 날 |
