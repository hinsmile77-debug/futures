# 166차: BiasReset·confstuck·CB타이밍 4종 패치

**작성**: 2026-06-12  
**커밋**: `92691b2`  
**브랜치**: `dev`  
**변경 파일**: `main.py`, `safety/circuit_breaker.py`

---

## 1. 분석 배경

`20260610_LEARNING.log` (165차 배포 이전) 장중 로그를 분석하여 4종 문제를 확인.

---

## 2. 원인별 문제 정리

### 2-1. BiasReset 해제 즉시 재고착 (P0 원인)

| 항목 | 내용 |
|---|---|
| 현상 | 09:39 5m DN편향 93% → fallback 적용. 09:49 DN편향 77%로 내려가자 즉시 해제. 해제 직후 DN=23/30이 그대로 남아 다음 분봉에서 재고착 반복 |
| 근본 원인 | fallback 해제 시 `_bias_buf[h]`를 초기화하지 않아 오염된 과거 이력(DN=23개)이 그대로 남아있음 |
| 영향 | uniform fallback 해제와 적용이 매 분봉마다 반전(flip-flop) → 앙상블 출력 불안정 |

### 2-2. 해제/진입 임계값 동일로 인한 flip-flop (P1 원인)

| 항목 | 내용 |
|---|---|
| 현상 | 진입 조건(≥80%)과 해제 조건(< 80%)이 대칭 → 편향이 77~81% 사이를 오가는 구간에서 매 분봉 발동·해제 반복 |
| 근본 원인 | `if _dir_bias_r >= 0.80: 진입 / else: 해제` — 경계값 동일 |
| 영향 | [BiasReset] 로그가 연속으로 찍히고 앙상블 출력이 분봉마다 uniform ↔ 정상 전환 |

### 2-3. conf 값 장기 고착 (P2 원인)

| 항목 | 내용 |
|---|---|
| 현상 | 1m conf=37.0% 10분 연속 동일값(09:20~09:29), 40.0% 10분(09:30~09:39), 42.0% 12분(09:40~09:51). 3m conf=54.9% 3회 연속 |
| 근본 원인 | 미파악 (진단 로그 부재 — P2에서 추가) |
| 가설 1 | `_hz_feat_cache`에서 N분봉 완성봉 대기 중 동일 피처 벡터 재사용 → GBM 동일 입력 → 동일 conf |
| 가설 2 | GBM 모델 자체가 특정 피처 영역에서 confidence 분포가 평탄화되어 항상 같은 max proba 반환 |
| 영향 | 예측 신호가 시장 변화를 반영하지 못하고 고착 → 거짓 안정 신호 |

### 2-4. CB PAUSED 발동 시 원인 불투명 (P5 원인)

| 항목 | 내용 |
|---|---|
| 현상 | 09:41~09:46 CB=PAUSED + 처리시간 5421~6175ms. 원인 로그 부재로 GBM 재학습 중 GIL 블로킹인지, 다른 병목인지 구분 불가 |
| 근본 원인 | `record_pipe_latency()` PAUSE 발동 메시지에 `_gbm_retrain_active` 상태와 실제 임계값이 누락 |
| 추가 문제 | PipePerf WARN 수준(1~5초)은 100ms+ 단계만 출력 → 단계별 분해값이 일부 누락되어 병목 단계 특정 어려움 |
| 영향 | 운영 중 CB PAUSED 재발 시 원인 파악에 수분 소요 |

---

## 3. 개선 내용

### P0: BiasReset 해제 시 오염 버퍼 초기화

**파일**: `main.py:3128~3137`

```python
# 변경 전
if _h in self._bias_override_horizons:
    self._bias_override_horizons.discard(_h)
    log_manager.learning(...)
self._bias_fl_streak[_h] = 0

# 변경 후
_can_release = _dir_bias_r < 0.60
if _h in self._bias_override_horizons:
    if _can_release:
        self._bias_override_horizons.discard(_h)
        self._bias_buf[_h].clear()      # ← 오염 이력 제거
        self._conf_stuck[_h] = 0
        log_manager.learning(...)
self._bias_fl_streak[_h] = 0
```

**효과**: fallback 해제 직후 빈 버퍼에서 새로 집계 시작 → 즉각 재고착 방지

---

### P1: 진입/해제 임계값 비대칭화 (80% / 60%)

**파일**: `main.py:3126`

```python
# 변경 전: else 블록 — _dir_bias_r < 0.80이면 무조건 해제
# 변경 후: 해제는 _dir_bias_r < 0.60일 때만
_can_release = _dir_bias_r < 0.60
```

| 편향 비율 | 이전 동작 | 이후 동작 |
|---|---|---|
| ≥ 80% | fallback 진입 | fallback 진입 (동일) |
| 60~79% | fallback 해제 | **fallback 유지**, streak만 리셋 |
| < 60% | fallback 해제 | fallback 해제 (+ 버퍼 초기화) |

**효과**: 경계값 flip-flop 제거. 6/10 케이스(77%)는 해제되지 않음

---

### P2: conf 고착 진단 로그 (`[CONF⚠]`)

**파일**: `main.py:470~471` (초기화), `main.py:3620~3638` (감지 로직)

```python
# 신규 상태 변수
self._conf_prev: dict = {}                      # 직전 틱 blended conf
self._conf_stuck: dict = {h: 0 for h in HORIZONS}  # 연속 동일 카운터

# STEP5 블렌딩 후 삽입
_curr_conf = horizon_proba[h_name]["confidence"]
if abs(_curr_conf - self._conf_prev.get(h_name, -1.0)) < 1e-6:
    self._conf_stuck[h_name] += 1
    if self._conf_stuck[h_name] >= 3:
        log_manager.learning(
            f"[CONF⚠] {h_name} conf={_curr_conf:.4f} "
            f"{self._conf_stuck[h_name]}분 고착 | "
            f"gbm_raw={_gbm_raw_conf:.4f} sgd={...} bar_age={...}"
        )
else:
    self._conf_stuck[h_name] = 0
self._conf_prev[h_name] = _curr_conf
```

**로그 예시**:
```
[CONF⚠] 1m conf=0.3700 10분 고착 | gbm_raw=0.3700 sgd=u=0.333/d=0.333/f=0.333 bar_age=0
→ GBM raw와 SGD 모두 동일 → 입력 피처 자체가 고착 의심
```

**효과**: 고착 3분차부터 즉시 감지 + 계층별 분해값으로 GBM/SGD/피처 캐시 중 원인 특정 가능

---

### P5: CB PAUSED 처리시간 진단 강화

**파일**: `safety/circuit_breaker.py:443~461`, `main.py:5142~5166`

#### 5-1. PAUSE 발동 메시지에 완화 맥락 포함

```python
# 변경 전
self._trigger_pause(5, f"파이프라인 {pipe_ms:.0f}ms — 처리 지연")

# 변경 후
_retrain_tag = " [GBM재학습중→임계×2]" if self._gbm_retrain_active else ...
self._trigger_pause(5, f"파이프라인 {pipe_ms:.0f}ms — 처리 지연{_retrain_tag} (임계={_pause_threshold:.0f}ms)")
```

**로그 예시**:
```
# GBM 재학습 중 정상 완화 케이스
[CB] 5분 진입 정지 | 파이프라인 6175ms — 처리 지연 [GBM재학습중→임계×2] (임계=10000ms)
→ 임계 10000ms인데 6175ms → 정상 완화 중이므로 CB 미발동이 맞음

# 실제 이상 케이스  
[CB] 5분 진입 정지 | 파이프라인 5421ms — 처리 지연 (임계=5000ms)
→ GBM 재학습 없이 5421ms → 실제 병목 조사 필요
```

#### 5-2. PipePerf WARN 수준도 전 단계 분해 출력

```python
# 변경 전: WARN 수준은 100ms+ 단계만 출력
# 변경 후: WARN·CB임박 모두 전 단계(S1→S2→…→end) 분해 + SYSTEM 로그 기록
_pipeperf_warn_msg = f"[PipePerf]{_retrain_tag_pipe} total={_pipe_ms:.0f}ms | {_all_steps_str}"
logger.warning(_pipeperf_warn_msg)
log_manager.system(_pipeperf_warn_msg, "WARNING")
```

**효과**: 1초~5초 처리 지연에서도 어느 단계(S1 피처 검증 / S2 SGD / S3 GBM재학습 / S4 피처생성 / S5 예측 / …)가 병목인지 즉시 확인 가능

---

## 4. 검증 포인트

다음 장에서 LEARNING 로그로 확인:

| 항목 | 기대 로그 |
|---|---|
| P0 검증 | fallback 해제 직후 편향 집계가 0건부터 재시작 (`[Bias] 적중=0%(0/1)`) |
| P1 검증 | 편향 60~79% 구간에서 `[BiasReset] fallback 해제` 로그 미출력 |
| P2 검증 | conf 동일 3분차부터 `[CONF⚠]` 출력. `gbm_raw`와 `sgd` 값이 모두 동일이면 입력 피처 고착 확인 |
| P5 검증 | CB PAUSED 발동 시 `[GBM재학습중→임계×2]` 또는 무태그로 원인 즉시 구분 가능 |

---

## 5. 향후 할일

### 즉시 (P2 후속 — conf 고착 원인 해소)

`[CONF⚠]` 로그가 실제로 찍히면 `gbm_raw` vs `sgd` 값으로 분기:

| gbm_raw 고착 | sgd 정상 | → GBM이 동일 피처에서 동일 확률 반환. `_hz_feat_cache` 갱신 주기 점검 |
|---|---|---|
| gbm_raw 고착 | sgd도 고착 | → 피처 입력 자체 고착. `build_for_horizon()` 1m 갱신 경로 점검 |
| gbm_raw 정상 | sgd 고착 | → SGD partial_fit 미발생 또는 SGD가 초기 균등분포 고착 |

**파일 대상**: `features/feature_decay.py`, `main.py:_hz_feat_cache 갱신 로직`

---

### 이번 주 (P3·P4 잔여)

#### P3: GBM 편향 감지 시 SGD 비중 자동 복구

- **파일**: `learning/online_learner.py:_adjust_weights()`
- **내용**: `_bias_override_horizons`에 호라이즌이 있을 때 해당 버킷 SGD 비중을 최소 15%로 일시 상향
- **근거**: SGD가 min floor(10%)에서 GBM 편향 대항 능력 상실. 6/10 09:40 이후 SGD비중=10% 고착 확인

#### P4: 동적 class weight halflife 단축 검토

- **파일**: `learning/batch_retrainer.py:_DYN_HALFLIFE`
- **내용**: 100봉(≈100분) → 60봉(≈60분) 단축 A/B 테스트
- **근거**: 장전 재학습(08:55) → 09:31 첫 정기 재학습 30분 공백 동안 당일 초반 편향 데이터 감쇠 불충분
- **리스크**: 단기 노이즈 과민 반응 가능 → 백테스트 확인 후 적용

#### P4-b: 조기 재학습 트리거 (09:15~09:20)

- **파일**: `learning/batch_retrainer.py` 또는 `main.py:STEP3`
- **내용**: 최초 30건 누적 후 1회 추가 재학습 트리거 (09:15 전후)
- **근거**: 09:10~09:30 UP 추세 전환 시 당일 데이터가 재학습에 반영되기까지 공백 존재

---

### 다음 주 (중기 개선)

#### Triple Barrier 레이블링

- **파일**: `learning/batch_retrainer.py:_path_conditioned_label()` 교체
- **내용**: 고정 임계값 레이블 → 변동성 기반 Triple Barrier (상한/하한/시간 장벽)
- **근거**: 현재 고정 임계값이 변동성 레짐 변화에 무감각 → 레이블 분포 자연 균형화 기대
- **사전 필요**: KOSPI200 선물 1분봉 ATR 실측 (추정 0.10~0.25%)

#### 레짐 조건부 GBM 분리

- **내용**: RISK_ON / NEUTRAL / RISK_OFF 레짐별 독립 GBM 학습
- **근거**: 단일 GBM이 최근 하락 레짐 패턴으로 오염 → 레짐 전환 후에도 이전 편향 잔존
- **참조**: 260611_DIRECTION_BIAS_IMPROVEMENT_PLAN.md § 4.2

---

## 6. 관련 파일

| 파일 | 역할 |
|---|---|
| `main.py` | P0·P1·P2 적용 (BiasReset·conf 고착 감지) |
| `safety/circuit_breaker.py` | P5 적용 (PAUSE 진단 강화) |
| `docs/260611_DIRECTION_BIAS_IMPROVEMENT_PLAN.md` | 방향편향 전체 개선 계획 |
| `learning/batch_retrainer.py` | 165차 P0·P1 (동적 class weight·CUSUM) |
| `strategy/entry/meta_gate.py` | 165차 P3 (MetaGate 편향 감지) |
