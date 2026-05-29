# 상위 방향 엔진 + 하위 실행 엔진 고도화 방안

## 목적

기존 멀티 호라이즌 예측 구조를 유지하면서도,  
상위 방향성 판단과 하위 실행 타이밍 판단의 역할을 분리해 실전 대응력을 높인다.

핵심 아이디어는 다음과 같다.

- 상위 방향 엔진:
  - `1m, 3m, 5m, 10m, 15m, 30m`의 기존 호라이즌 예측을 사용
  - 방향성, 신뢰도 승인, 보유 논리를 담당
- 하위 실행 엔진:
  - 최근 호라이즌 window 기반 `1m 예측`을 사용
  - 진입 타이밍, 재진입, 감산, 청산 가속을 담당

---

## 1. 두 방식의 설명과 장단점

### 1-1. 기존 호라이즌 예측

설명:

- 현재 시점의 피처를 기반으로 `N분 후 방향`을 예측하는 방식
- 예:
  - `1m`: 1분 후 방향
  - `3m`: 3분 후 방향
  - `5m`: 5분 후 방향
  - `10m`: 10분 후 방향
  - `15m`: 15분 후 방향
  - `30m`: 30분 후 방향
- 평가 방식은 원칙적으로 각 호라이즌별 anchor 또는 비중복 사건 기반이 가장 적합

장점:

- 예측 목표가 분명하다
- 포지션 보유 시간과 직접 연결된다
- 멀티타임프레임 방향 판단이 가능하다
- 상위 레짐과 하위 레짐을 동시에 반영하기 쉽다
- 앙상블 구조를 설계하기 좋다

단점:

- 긴 호라이즌은 샘플 축적이 느리다
- 장 초반에는 긴 호라이즌 판단 신뢰도가 약하다
- 1분 롤링 집계를 쓰면 중복 표본 문제가 커진다
- 실전 진입 타이밍 대응은 둔할 수 있다

실전 이득:

- 큰 방향을 거스르는 진입을 줄인다
- 보유 가치가 있는 신호인지 판단하기 쉽다
- ShadowSession, CB, 방향 승인 레이어에 적합하다

### 1-2. 최근 호라이즌 window 기반 1m 예측

설명:

- 최근 `N분`의 맥락을 입력 창으로 사용하되, 예측 대상은 항상 `다음 1분`인 방식
- 예:
  - 최근 5분 데이터를 보고 1분 후 방향 예측
  - 최근 30분 데이터를 보고 1분 후 방향 예측
- 즉 입력 윈도우는 길고, 타깃은 짧다

장점:

- 1분마다 갱신되어 반응이 빠르다
- 장중 실행 타이밍에 강하다
- 최근 시장 컨텍스트를 실시간으로 반영한다
- 검증과 학습 피드백이 빠르다
- 추격 진입, 재진입, 감산 판단에 유리하다

단점:

- 노이즈에 취약하다
- 과민반응과 과매매 위험이 있다
- 상위 방향성 판단에는 부적합할 수 있다
- 기존 1m 모델과 역할 중복 가능성이 있다
- "30분 후 방향"을 직접 맞히는 구조는 아니다

실전 이득:

- 좋은 방향 신호가 있어도 나쁜 진입 타이밍을 피할 수 있다
- 급변 직전/직후의 마이크로 구조 변화를 반영할 수 있다
- 체결 실행 품질과 리스크 절감에 도움이 된다

### 1-3. 비교 요약

- 기존 호라이즌 예측:
  - 질문: `N분 후 어디로 갈까`
  - 역할: 방향성과 보유 논리
- 최근 window 기반 1m 예측:
  - 질문: `최근 N분 맥락에서 다음 1분은 어떨까`
  - 역할: 타이밍과 실행 논리

정리:

- 1번만 쓰면 방향성은 좋지만 둔할 수 있다
- 2번만 쓰면 반응은 빠르지만 시끄러울 수 있다
- 둘을 분리 결합하는 것이 가장 실전적이다

---

## 2. 현재 미륵이 시스템의 방식 정리

### 2-1. 현재 코어 예측 구조

현재 미륵이는 본질적으로 **기존 호라이즌 예측 구조**를 사용하고 있다.

근거:

- `config/settings.py`의 `HORIZONS` 기준으로 `1m, 3m, 5m, 10m, 15m, 30m` 운용
- `model/target_builder.py`에서 각 호라이즌별 `future N분 가격`을 기준으로 타깃 생성
- `model/multi_horizon_model.py`에서 호라이즌별 개별 모델과 개별 scaler 운용
- `main.py`에서 매분 각 호라이즌 예측을 생성하고 앙상블 수행

즉 현재 구조는:

- 입력:
  - 현재 시점 feature vector
- 출력:
  - 각 호라이즌의 `N분 후 방향 확률`
- 최종:
  - multi-horizon ensemble

### 2-2. 현재 평가와 운영의 특징

현재 시스템은 예측 정의는 호라이즌 기반이지만,  
검증과 운영은 **매분 롤링 평가** 성격이 강하다.

예:

- 예측은 매분 저장
- 현재 시각에서 `T-h` 시점 예측을 매분 검증
- `30m accuracy`도 최근 롤링 검증 버퍼 기반으로 집계

이 의미는:

- 예측 철학은 1번
- 운영 집계 철학은 anchor형보다 더 롤링형

### 2-3. 현재 구조의 장점

- 이미 멀티타임프레임 방향 엔진이 존재한다
- 상위 방향과 하위 방향을 함께 본다
- 호라이즌별 confidence를 앙상블할 수 있다
- feature infra, calibration, online learning이 이미 붙어 있다

### 2-4. 현재 구조의 한계

- 긴 호라이즌의 정확도 평가가 중복 표본에 민감하다
- 상위 방향 판단과 하위 실행 타이밍이 한 엔진 안에 섞여 있다
- 1분 실행 타이밍 최적화 엔진이 독립 계층으로 존재하지 않는다
- 좋은 방향을 봐도 진입 타이밍이 나쁘면 실전 성과가 훼손될 수 있다

정리하면:

- 현재 미륵이는 **상위 방향 엔진은 이미 상당 부분 구현**
- 하지만 **하위 실행 엔진은 독립 설계가 부족**

---

## 3. 개편안 제안 정리

### 3-1. 목표 구조

구조를 아래 2계층으로 분리한다.

1. 상위 방향 엔진
- 기존 멀티 호라이즌 예측 유지
- 방향 승인, 신뢰도 승인, 보유시간 논리 담당

2. 하위 실행 엔진
- 최근 horizon window 기반 1m 예측 신규 추가
- 실제 진입 타이밍, 감산, 재진입, 청산 가속 담당

### 3-2. 상위 방향 엔진의 역할

- 오늘 이 구간에서 어느 방향이 우세한가
- 지금 진입을 고려할 자격이 있는가
- 1m 노이즈보다 5m/10m/15m/30m 기준으로 보유 가치가 있는가
- ShadowSession, CB, 방향 승인, qualification gating에 활용

### 3-3. 하위 실행 엔진의 역할

- 상위 방향 엔진이 승인한 방향 안에서 지금 바로 들어가도 되는가
- 직전 1~3분 미세 반전/급변/체결 불리 구간은 아닌가
- 추격 진입을 늦춰야 하는가
- 분할 진입/감산/청산 속도를 조절해야 하는가

### 3-4. 결합 방식 제안

기본 원칙:

- 상위 방향 엔진이 먼저 `direction bias`를 결정
- 하위 실행 엔진이 `execute / delay / reduce / block`을 결정

예시:

- 상위 엔진: `UP 승인`
- 하위 엔진:
  - `execute_now`
  - `delay_1m`
  - `half_size`
  - `block_entry`

### 3-5. 기대 효과

- 방향은 맞는데 진입이 나빠서 손실나는 케이스 감소
- 장 초반/급변 구간 과매수, 과매도 추격 감소
- 롤링 1m 노이즈를 상위 방향 엔진이 완충
- 상위 방향성 없는 무의미한 초단기 진입 억제

---

## 4. 구현 개요

### 4-1. 상위 방향 엔진

유지 또는 개선 대상:

- 기존 `MultiHorizonModel`
- horizon qualification gating
- horizon confidence calibration
- ensemble decision
- anchor 또는 비중복 사건 기반 성능 집계

핵심 개선:

- 긴 호라이즌 평가를 더 정직하게 정리
- 자격 획득 전 호라이즌 배제
- active horizon 기반 동적 비중 적용

### 4-2. 하위 실행 엔진 — rule-based ExecutionGate

**설계 결정: 신규 ML 모델 구현 안 함**

현재 모의투자 단계에서 ExecutionWindowModel(새 ML)을 훈련시키려면 실행 결과 레이블(go/delay/block이 옳았는지)이 필요하며 이 레이블은 실전 거래 데이터에서만 나온다. feature_builder에 이미 microprice, OFI, MLOFI, queue_dynamics, toxicity가 모두 존재한다. 즉시 투입 가능한 rule-based gate가 실용적이며, 추후 ML로 업그레이드 가능하다.

**ExecutionGate 신규 모듈**: `strategy/entry/execution_gate.py`

실행 신호 4종 정의:

| 신호 | 피처 소스 | 조건 | 액션 |
|---|---|---|---|
| E1. 독성 흐름 | `toxicity_score` | > `EXEC_TOXICITY_BLOCK`(0.7) | block |
| E2. OFI 역전 임박 | `bear/bull_reversal_signal` | 진입 방향 반대 reversal > 0.5 | delay |
| E3. 호가 스프레드 확대 | `spread_ticks` | > `EXEC_SPREAD_MAX`(3.0틱) | reduce |
| E4. Queue 도주 | `queue_imbalance` | ask/bid side 물량 급감 | reduce |

우선순위: block > delay > reduce > go

출력 스키마:

```python
{"action": "go"|"delay"|"reduce"|"block", "reasons": [...], "toxicity": float}
```

**Shadow mode 필수**: `EXEC_GATE_SHADOW=True` 동안 차단 없이 로그만 출력. 1주 운영 후 action 통계(block/delay 비율 10~25% 범위)가 정상이면 실제 게이트 활성화.

### 4-3. 매분 파이프라인 의사결정 흐름 (확정)

```
STEP 4  FeatureBuilder → feat_vec
STEP 5  MultiHorizonModel + SGD blend → horizon_proba (6개 전부 계산)
STEP 6
  ┌─ [계층 1: 상위 방향 엔진] ──────────────────────────────────────┐
  │  _get_active_horizons()  →  active_horizons set                │
  │  EnsembleDecision.compute(active_horizons)                     │
  │     decorr 마스크+재정규화 [결정A]                              │
  │     합의도 패널티 동적화 [결정B]                                 │
  │     Platt 보정 / 품질 게이트 / stuck 감쇠                       │
  │  출력: direction, confidence, grade, active_set                │
  └────────────────────────────────────────────────────────────────┘
        ↓ direction ≠ FLAT AND grade ≠ X 일 때만
  ┌─ [계층 2: 하위 실행 엔진 (rule-based)] ─────────────────────────┐
  │  ExecutionGate.evaluate(feat_vec, direction)                   │
  │     E1 toxicity / E2 OFI reversal / E3 spread / E4 queue      │
  │  출력: action = go | delay | reduce | block                    │
  └────────────────────────────────────────────────────────────────┘
        ↓
  ┌─ [최종 결합] ────────────────────────────────────────────────────┐
  │  grade=A/B AND action=go   → 정상 진입                          │
  │  grade=A/B AND action=reduce → size_mult × 0.5                 │
  │  grade=A/B AND action=delay  → _exec_delay_remaining=1 (다음 분) │
  │  action=block 또는 grade=X  → 진입 차단                         │
  └────────────────────────────────────────────────────────────────┘
```

---

## 5. Implementation Plan

> **두 트랙 병렬 진행**: Track A(상위 방향 엔진)와 Track B(하위 실행 엔진)는 독립 배포 가능하다.  
> 단, Track B는 Track A Phase 3(앙상블 실제 변경) 완료 후 투입한다. 두 변경을 동시에 활성화하면 원인 분리 불가.

---

### Track A — 상위 방향 엔진 (Qualification 기반) [1~1.5주]

상세 구현 계획은 `HORIZON_QUALIFICATION_IMPLEMENTATION_PLAN.md` 기준.  
4단계 순서: **상태 추적 → Dashboard dry-run → 앙상블 변경 → 품질 게이트**

| 단계 | 패치 | 핵심 내용 | 앙상블 변경 |
|---|---|---|---|
| A-1 | Patch 2/3/4 | `_horizon_runtime_state` + cycle 카운터 | ❌ |
| A-2 | Patch 9/10 | Dashboard qualification 카드 (dry-run) | ❌ |
| A-3 | Patch 1/5/6/7/12 | `compute(active_horizons)` 전환 + fallback 제거 | ✅ |
| A-4 | Patch 8/11 | 품질 게이트 + 가시성 보강 | 경미 |

---

### Track B — 하위 실행 엔진 (ExecutionGate) [Track A-3 완료 후, 1주]

| 단계 | 작업 | 핵심 내용 | 실제 차단 |
|---|---|---|---|
| B-1 | ExecutionGate 구현 | E1~E4 룰 + shadow mode | ❌ (로그만) |
| B-2 | Shadow 1주 운영 | block/delay 비율 10~25% 확인 | ❌ |
| B-3 | Gate 활성화 | `EXEC_GATE_SHADOW=False` | ✅ |
| B-4 | size_mult 연결 | action=reduce → ×0.5 반영 | ✅ |

---

### Track C — Anchor 평가 체계 [별도 일정, 낮은 우선순위]

목표: 긴 호라이즌(10m/15m/30m) 성능 평가를 비중복 사건 기반으로 개선

- `prediction_buffer.anchor_accuracy(h)` 헬퍼 (rolling 대비 편향 없는 독립 집계)
- CB③ rolling vs anchor 지표 역할 분리
- ShadowSession 평가 기준 anchor 전환 검토

---

### Track D — 대시보드 통합 [Track A-2 완료 후]

목표: 두 엔진 상태를 한 화면에서 분리 표시

- Qualification 카드 (계층 1 상태)
- ExecutionGate 상태 카드 (계층 2 action + reasons)
- 최종 진입 verdict 카드 (grade + action → 결과)

---

## 6. Code Patch Breakdown

### Patch A. 상위 방향 엔진 — Qualification 기반 전환

대상: `main.py` · `model/ensemble_decision.py` · `config/settings.py` · `learning/prediction_buffer.py`

상세 내용: `HORIZON_QUALIFICATION_IMPLEMENTATION_PLAN.md` Patch 1~12 참조.  
핵심 변경:

- `_horizon_runtime_state` 구조 도입 + cycle 카운터
- `compute(active_horizons)` 파라미터 추가 + decorr 마스크 [결정A]
- 합의도 패널티 동적화 [결정B]
- 3m fallback 제거
- `count_verified_today()` + `_restore_qualification_state()` [결정C]

---

### Patch B. ExecutionGate — 하위 실행 엔진 신규 구현

대상: `strategy/entry/execution_gate.py` (신규) · `config/settings.py` · `main.py`

작업:

```python
# strategy/entry/execution_gate.py
class ExecutionGate:
    def evaluate(self, feat: dict, direction: int) -> dict:
        action = "go"
        reasons = []
        # E1: 독성 흐름 차단
        if feat.get("toxicity_score", 0.0) > EXEC_TOXICITY_BLOCK:
            return {"action": "block", "reasons": ["toxicity"], ...}
        # E2: OFI 역전 임박
        if direction == DIRECTION_UP and feat.get("bear_reversal_signal", 0) > 0.5:
            action, reasons = "delay", ["ofi_reversal_imminent"]
        elif direction == DIRECTION_DOWN and feat.get("bull_reversal_signal", 0) > 0.5:
            action, reasons = "delay", ["ofi_reversal_imminent"]
        # E3: 스프레드 확대
        elif feat.get("spread_ticks", 0.0) > EXEC_SPREAD_MAX:
            action, reasons = "reduce", ["wide_spread"]
        # E4: Queue 도주
        ...
        return {"action": action, "reasons": reasons, ...}
```

`config/settings.py` 추가:
```python
EXEC_TOXICITY_BLOCK = 0.70   # E1 독성 차단 임계값
EXEC_SPREAD_MAX     = 3.0    # E3 스프레드 최대 허용 (틱)
EXEC_QUEUE_RUN      = 0.75   # E4 queue imbalance 도주 임계값
EXEC_GATE_SHADOW    = True   # Shadow mode: 로그만, 실제 차단 없음
```

`main.py` STEP 6 연결:
- 상위 엔진 grade ≠ X 후 `execution_gate.evaluate()` 호출
- action=block → 진입 차단
- action=delay → `_exec_delay_remaining=1` (다음 분봉 재평가)
- action=reduce → size_mult × 0.5

---

### Patch C. 30m Anchor 평가 (Track C, 별도 일정)

대상: `learning/prediction_buffer.py` · `safety/circuit_breaker.py`

작업:

- `anchor_accuracy(h, date_str)` — 비중복 사건 기반 정확도 (h분 간격 독립 예측만 집계)
- CB③ 지표에 rolling/anchor 구분 표시
- ShadowSession 평가 기준 anchor 전환 검토

---

### Patch D. 대시보드 2계층 통합 표시

대상: `dashboard/main_dashboard.py`

작업:

- Qualification 카드 (Track A-2 기준, 6개 호라이즌 상태)
- ExecutionGate 상태 카드 (action + reasons + shadow mode 여부 표시)
- 최종 진입 verdict 카드 (계층1 grade + 계층2 action → 결과 레이블)

---

## 7. 종합 Todo List

> Track A = 상위 방향 엔진, Track B = 하위 실행 엔진, C = Anchor 평가, D = 대시보드

---

### Track A — Must (상위 방향 엔진, 순서 엄수)

**A-1: 상태 추적 시작 (앙상블 미변경)**

- [ ] `main.py` — `_horizon_runtime_state` dict 구조 도입
- [ ] `main.py` STEP 1 — `verified_cycles[h] += 1` 누적
- [ ] `main.py` STEP 2 — `trained_cycles[h]` = `online_learner._horizon_counts[h]` 동기화 (`_bucket_learn_count` 사용 금지)
- [ ] `main.py` — `[Qualify] h verified=N/3 trained=N/3` DEBUG 로그
- [ ] `main.py` `daily_close()` — `_horizon_runtime_state` 일간 초기화

**A-2: Dashboard Dry-run (실세션 1일 검증 후 A-3 진행)**

- [ ] `dashboard/main_dashboard.py` — qualification 카드 6개 (WAIT/ACTIVE/PENALIZED/BLOCKED 색상)
- [ ] `dashboard/main_dashboard.py` — cycle 진행도 `n/3`, 상태, 비중, 정확도 표시
- [ ] `main.py` — `_horizon_runtime_state` → dashboard payload 연결 (분 단위)

**A-3: 앙상블 실제 변경 (A-2 검증 완료 후)**

- [ ] `config/settings.py` — `HORIZON_QUALIFY_MIN_CYCLES=3`, `QUALIFY_QUALITY_MIN_SAMPLES=10`
- [ ] `main.py` — `_get_active_horizons()` 함수 구현
- [ ] `main.py` STEP 6 — `ensemble.compute(active_horizons=...)` 호출 변경
- [ ] `model/ensemble_decision.py` — `compute(active_horizons: set)` 파라미터 추가
- [ ] `model/ensemble_decision.py` — [결정A] decorr 마스크+재정규화 (inactive=0, total_w=0 → flat_result)
- [ ] `model/ensemble_decision.py` — [결정B] 합의도 패널티 교체 (`n_agree < n_active/2`)
- [ ] `model/ensemble_decision.py` — 3m fallback 제거
- [ ] `model/ensemble_decision.py` — `detail[h]`에 `qualified/active/status/weight` 포함
- [ ] `main.py` — active horizon 없을 때 `FLAT/X/conf=0` 안전 처리
- [ ] `learning/prediction_buffer.py` — `count_verified_today(h, date_str)` 헬퍼
- [ ] `main.py` — `_restore_qualification_state()` (`connect_broker()` 장중 재시작 분기)

**A-4: 품질 게이트 + 가시성 (A-3 3일 이상 모의투자 후)**

- [ ] `main.py` — `_compute_qualified_status()` → active/penalized/blocked 분류
- [ ] `main.py` — 정확도 기반 weight penalty (최소 샘플 10건 미충족 시 skip)
- [ ] `main.py` — 방향 편향 ≥ 75% 시 비중 50% 감산 (`_bias_buf` 연결)
- [ ] `main.py` + `model/ensemble_decision.py` — 자격 획득·비중 변경·패널티 로그

---

### Track B — Must (하위 실행 엔진, Track A-3 완료 후)

**B-1: ExecutionGate Shadow 구현**

- [ ] `strategy/entry/execution_gate.py` — `ExecutionGate` 클래스 신규 구현 (E1~E4 룰)
- [ ] `config/settings.py` — `EXEC_TOXICITY_BLOCK=0.70`, `EXEC_SPREAD_MAX=3.0`, `EXEC_QUEUE_RUN=0.75`, `EXEC_GATE_SHADOW=True`
- [ ] `main.py` STEP 6 — 상위 엔진 grade ≠ X 후 `execution_gate.evaluate()` 호출
- [ ] `main.py` — shadow mode: 로그만, 실제 차단 없음
- [ ] `main.py` — `[ExecGate] action=X reasons=[Y]` 로그 (매 분봉)

**B-2: Shadow 1주 검증 → 활성화**

- [ ] action 통계 확인: block+delay 비율 10~25% 범위인지 확인
- [ ] `config/settings.py` — `EXEC_GATE_SHADOW=False` 전환 (검증 통과 후)
- [ ] `main.py` — action=block → 진입 차단
- [ ] `main.py` — action=delay → `_exec_delay_remaining=1` (다음 분봉 재평가)
- [ ] `main.py` — action=reduce → size_mult × 0.5

---

### Track C — Should (Anchor 평가, 별도 일정)

- [ ] `learning/prediction_buffer.py` — `anchor_accuracy(h, date_str)` (비중복 사건 기반 독립 집계)
- [ ] `safety/circuit_breaker.py` — CB③ rolling / anchor 지표 분리 표시
- [ ] ShadowSession 평가 기준 anchor 전환 검토

---

### Track D — Should (대시보드 통합)

- [ ] `dashboard/main_dashboard.py` — ExecutionGate 상태 카드 (action + reasons + shadow 여부)
- [ ] `dashboard/main_dashboard.py` — 최종 진입 verdict 카드 (계층1 grade + 계층2 action → 결과)
- [ ] `dashboard/main_dashboard.py` — 두 엔진 상태 대비 표시 (상위/하위 나란히)

---

### Nice to Have

- [ ] `strategy/entry/execution_gate.py` — 실행 결과 레이블 누적 시작 (ML 전환 준비)
- [ ] 상위 엔진 승인 + 하위 엔진 실행 결과의 PnL attribution 로그 (1개월 후)
- [ ] 30m 호라이즌 삭제 검토 — 품질 게이트 작동 빈도 기반, 1개월 운영 후

---

## 8. 결론 — 1% 트레이더 관점 종합

### 현재 시스템 진단

| 항목 | 상태 | 비고 |
|---|---|---|
| 멀티 호라이즌 방향 엔진 | ✅ 존재 | Qualification으로 고도화 필요 |
| 장 초반 자격 없는 호라이즌 참여 | ❌ 구조적 오류 | Track A로 해결 |
| 3m fallback 오염 | ❌ 신뢰도 왜곡 | Track A로 제거 |
| 실행 타이밍 독립 계층 | ❌ 미분리 | Track B(rule-based)로 신규 |
| 30m 실효성 | ⚠️ decorative | 1개월 후 삭제 검토 |

### 1% 트레이더의 핵심 판단

**"방향은 맞는데 진입이 나빠서 손실나는 케이스"를 줄이는 게 목표다.**

- 방향 오류: Qualification이 장 초반 미검증 호라이즌을 막는다
- 타이밍 오류: ExecutionGate가 독성 흐름·스프레드 확대·OFI 역전 임박에서 진입을 막는다
- 오버트레이딩: 장 초반 3분 공백 + ExecutionGate reduce/delay가 추격 진입을 억제한다

### 구현 우선순위 한 줄 원칙

```
구조적 오류(잘못된 신호 입력) 제거 먼저 → 실행 품질 개선 나중
Qualification 완성 → ExecutionGate Shadow → ExecutionGate 활성화
절대 금지: 두 변경 동시 활성화
```

### 관계 문서

- 상위 방향 엔진 상세: `HORIZON_QUALIFICATION_IMPLEMENTATION_PLAN.md`
- 본 문서: 두 엔진 통합 아키텍처 + 하위 실행 엔진 설계 + 종합 Todo

