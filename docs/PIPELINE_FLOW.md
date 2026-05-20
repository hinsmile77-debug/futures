# 미륵이 매분 파이프라인 전체 흐름

> 최종 업데이트: 2026-05-19  
> 기준 커밋: 6순위 안전장치 구현 완료 (Mid-Conf·Brier·루프브레이커·DNA·CoreHealth·ShadowSession·ContrarianMode)

---

## 시스템 기동 (08:45)

```
08:45  TradingSystem.__init__()
       ├─ CircuitBreaker 초기화
       │     Mid-Conf Blind Spot Tracker  (_mid_conf_wrong_streak)
            애매하게 자신있다 라고 판단한 구간에서 계속 틀리는지 추적
            횡보 가짜 돌파 옵션 만기일 뉴스 혼조

       │     Brier Score 버퍼 확률 예측이 얼마나 정확했는지 측정하는 점수저장
             (_brier_buf, _brier_penalty_active)최근 확률 예측 품질이 나빠서 페널티 모드인지 여부
            
       │     재시작 루프 브레이커          (_daily_halt_count)
            하루 동안 시스템이 몇 번 위험정지 되었는지 추적

       ├─ MarketDNA 초기화       [4순위]  safety/market_dna.py
            현재 시장의 “성격” 분석기 
            추세장/눌림목매매유리, 횡보장/mean reversion 유리, 패닉장/손절우선, 옵션변동성장세/fake move 많음

       ├─ CoreHealthScore 초기화  [5순위]  features/core_health.py
            현재 시스템 상태 점수 계산기
            데이터품질, 예측안정성,latency, 슬리피지,종합
            이 점수가 낮으면:포지션 축소, 신규 진입 금지,안전모드 전환

       ├─ ShadowSessionTracker 초기화  [6순위]  safety/shadow_session.py
            실제 주문 없이 “가상 거래”를 추적
            전략 검증,새 모델 테스트,regime 변화 감지

       └─ ContrarianModeTracker 초기화  [6순위]  safety/contrarian_mode.py
            시장 반대로 움직이는 전략 감시


08:55  매크로 수집 → 레짐 확정 (NEUTRAL / RISK_ON / RISK_OFF)
       실시간 구독 사전 시작 (FutureCurOnly tick / FutureJpBid hoga)

09:00  장 시작 — 매분 파이프라인 루프 진입
```

---

## STEP 1 — 과거 예측 검증

**파일**: `main.py:2168`

```
pred_buffer.verify_and_update(ts, close)
현재 시점의 실제 종가(close)를 이용해서,
과거에 저장해둔 예측값이 맞았는지 검증하고,
결과를 버퍼 상태에 반영하라
  ↓
필터: 30m 호라이즌 AND conf > 0.38 AND 이번 세션 예측(_session_start_ts)
이번 장(세션)에서 생성된
30분 방향 예측 중에서
신뢰도 0.38 이상인 것만 사용한다

  ↓
circuit_breaker.record_accuracy(correct, confidence)
모델 예측이 계속 틀릴 때 자동으로 매매를 줄이거나 멈추는 안전장치

  │
  ├─ [2순위] Brier Score 누적/자신 있게 맞히면 점수 낮음, 자신 있게 틀리면 점수 높음
  │     brier_i = (conf - actual)²
  │     이동평균 (최근 10건) > 0.35  → WARNING 로그
  │     이동평균 > 0.45              → brier_penalty_active = True
  │                                      → STEP 7에서 사이즈 ×0.5
  │
  ├─ [1순위] Mid-Conf Blind Spot Tracker
      이 구간은 애매하지만 꽤 자신 있다고 판단한 예측입니다.
      문제는 이 구간에서 계속 틀리면 모델이 특정 상황을 잘못 보고 있다는 뜻

  │     0.60 ≤ conf < 0.85 AND 오답 → mid_conf_wrong_streak +1
  │     7연속                        → CB③ strict 모드 (임계값 35% → 50%)
        원래는 정확도 35%만 넘어도 허용했지만, 이제는 50% 이상 맞혀야 계속 매매 가능

  │     기타 경우                    → 리셋
  │
  ├─ 고신뢰(conf ≥ 0.85) 오답 연속   → high_conf_wrong_streak
      이건 더 위험, 모델이 거의 확신했는데 틀린 경우
  │     5연속                        → CB③ strict 모드 (임계값 35% → 50%)
  │
  └─ acc30m 계산 (20샘플 이상)
      30분 예측 정확도를 계산합니다.단, 최소 20샘플 이상 있어야 의미 있게 판단

        effective_min = 0.50  (high_conf or mid_conf streak ≥ 임계값)
        위험 징후 있음

        effective_min = 0.35  (정상)

        acc < effective_min → cb3_warn_count +1
          1회: CB③ 경고 (슬랙)
          2회: _trigger_halt()
                [3순위] daily_halt_count +1
                1회: restart_size_mult = 1.0  (정상)
                2회: restart_size_mult = 0.5  (50% 축소)
                3회: restart_size_mult = 0.0  (완전 관망)

          1차 위험:    경고
          2차 위험:    halt 발동
          재시작:    restart_size_mult 적용
                      1회 halt → 정상 크기
                      2회 halt → 50%
                      3회 halt → 완전 관망

        acc ≥ effective_min → cb3_warn_count 리셋

horizon_calibrator.record
(horizon/예측 시간 구간, conf/모델 confidence (확신도), correct실제 정답 여부)
실제로 얼마나 믿을 만한가 평가

daily_consolidator.record(zone, correct)  # 5m 호라이즌만
하루 동안의 예측 성능을 “구간(zone)” 별로 누적 기록하는 함수
강한 상승장UP_STRONG,횡보장CHOP,패닉장PANIC,저변동장LOW_VOL
왜 5m만 기록할까
(1) 기준 호라이즌 통일
여러 horizon을 섞으면:정확도를 직접 비교하기 어려움 대표 기준 horizon 하나만 사용
(2) 노이즈 감소
1m는 너무 시끄럽고(random noise 많음)30m는 너무 느립니다.
5m는:단타,스캘핑,선물 방향성에서 균형이 좋은 경우가 많습니다.
(3) 레짐 학습 안정화
zone별 성능 분석은:샘플 수 일관성 안정성이 중요합니다. 5m가 보통 가장 안정적입니다.

이 데이터의 활용
이 누적 결과는 나중에:
특정 zone 거래 금지
position size 축소
confidence penalty
regime filter 강화
champion/challenger 평가등에 사용

---

## STEP 2 — SGD 온라인 자가학습
“방금 전 예측이 맞았나? 틀렸나?”를 보고 SGD 모델의 영향력을 조금씩 키우거나 줄이는 단계

**파일**: `main.py:2193`, `learning/online_learner.py`

```
검증된 예측 → online_learner.learn(horizon, x, actual, predicted)
  버킷: short (1m/3m/5m) / long (10m/15m/30m) 독립 학습
short = 1m / 3m / 5m
long  = 10m / 15m / 30m
short	초단기 움직임. 잡음이 많고 빠르게 변함
long	조금 더 긴 흐름. 추세와 레짐 영향이 큼


SGD 비중은 최종 예측에서 SGD 모델 의견을 얼마나 믿을지 정하는 값
  accuracy > 62% → SGD 비중 +2% (최대 50%)
  accuracy < 48% → SGD 비중 -2% (최소 10%)

stuck 발생 분봉 (비정상 체결) → 학습 스킵 (레이블 오염 방지)
```
SGD = Stochastic Gradient Descent 틀린 만큼 아주 조금씩 수정
시장 데이터 수집/ 체결강도 거래량 OFI 호가 imbalance PCR GEX 선물 흐름  외국인 수급 변동성
    ↓
feature vector 생성 x = [    0.82,    -0.14,    1.33,    ...]
    ↓
예측 수행
    ↓
예측 저장
    ↓
미래 실제값 확인
    ↓
예측 검증
    ↓
SGD partial_fit
    ↓
정확도 평가
    ↓
SGD 영향력 자동 조절
    ↓
실시간 시장 적응

SGD 영향력(weight)은 개별 horizon 성능 평가→ bucket 평가→ 최종 종합 예측 반영




---

## STEP 3 — GBM 배치 재학습
실시간으로 조금씩 배우는 SGD와 다르게, 일정 기간 쌓인 데이터를 모아서 GBM 모델을 다시 학습시키는 작업
SGD는 수업 중 바로바로 오답노트 수정
GBM 배치 재학습은 주말이나 월말에 전체 시험지를 다시 보고 새 참고서를 만드는 작업

**파일**: `main.py:2239`, `learning/batch_retrainer.py`

```
트리거: 주간/월간 스케줄 OR 
세션 재시작 직후 (_warmup_retrain_pending)재시작 후 아직 GBM 재학습을 해야 하는 상태
즉, 프로그램이 켜졌는데 지난번에 재학습을 못 했거나, 시작 직후 한 번 모델을 최신 상태로 맞춰야 하면 이 플래그가 켜집니다.

daemon thread 분리 → 메인 스레드 블로킹 없음/재학습은 뒤에서 돌림

완료 시 QTimer.singleShot(0, _on_gbm_retrain_done) — UI 스레드 안전 로드
PyQt에서는 UI를 아무 스레드에서나 직접 건드리면 위험 QTimer을 사용해서 UI 메인 스레드에서 안전하게 후처리 0의 의미는:가능한 한 빨리, 하지만 UI 이벤트 루프 안에서 실행

_on_gbm_retrain_done
재학습이 끝난 뒤 실행되는 함수
새 GBM 모델 파일 로드 모델 상태 표시 업데이트 로그 출력 재학습 실행 플래그 해제
즉, 재학습 thread가 만든 결과물을 메인 시스템에 반영하는 단계

_gbm_retrain_running 플래그로 중복 실행 차단
이 플래그는 현재 GBM 재학습이 돌고 있는지 표시
```
전체 흐름
STEP 3 — GBM 배치 재학습

1. 주간/월간 스케줄 또는 재시작 직후 조건 확인
2. _gbm_retrain_running 확인
3. 실행 중이 아니면 True로 변경
4. daemon thread에서 batch_retrainer 실행
5. 재학습 완료
6. QTimer.singleShot(0, _on_gbm_retrain_done)
7. UI 스레드에서 새 모델 안전 로드
8. _gbm_retrain_running = False
---

GBM Gradient Boosting Machine
틀린 문제를 계속 복습하면서,
점점 더 똑똑한 여러 개의 작은 결정트리(Tree)를 연결해
최종 예측을 만드는 방식

GBM 구조
입력 데이터
   ↓
특징(Feature) 생성
   ↓
첫 번째 결정트리 학습
   ↓
오차 계산
   ↓
오차를 줄이는 다음 트리 학습
   ↓
반복
   ↓
모든 트리 결과 합산
   ↓
최종 예측

결정트리(Tree)란
거래량 증가율 > 15% ?
   ├─ YES
   │    외국인 순매수 > 100억 ?
   │        ├─ YES → 상승확률 높음
   │        └─ NO  → 보통
   │
   └─ NO
        변동성 증가 ?
             ├─ YES → 하락 위험
             └─ NO  → 횡보

GBM의 핵심은:“이전 트리가 틀린 부분만 집중 보완”




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
