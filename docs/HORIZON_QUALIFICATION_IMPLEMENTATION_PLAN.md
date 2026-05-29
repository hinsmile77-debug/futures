# Horizon Qualification Implementation Plan

## 목적

당일 각 호라이즌이 자기 자신으로 `3 cycle`의 만기 검증과 학습 반영을 끝내기 전에는 방향 판단과 신뢰도 판단에 참여하지 않도록 바꾼다.  
자격을 획득한 호라이즌만 앙상블에 참여시키고, 참여 가능한 호라이즌 집합에 따라 비중을 동적으로 재구성한다.  
다른 호라이즌을 빌려 쓰는 confidence fallback은 제거한다.

## 핵심 규칙

- `cycle` = 해당 호라이즌 예측 1건이 만기 검증까지 완료된 1회
- `verified_cycles[h]` = STEP 1 `pred_buffer.verify_and_update()` 에서 해당 호라이즌 검증 완료 건수
- `trained_cycles[h]` = STEP 2 `online_learner.learn(h, ...)` 실제 호출 건수 (`_horizon_counts[h]` 동기화)
  - GBM은 pkl 기반으로 장 시작 전 고정됨 — 장중 SGD 학습만 카운트
  - 장중 재시작 시 복원 규칙: [결정 C] 참조
- `qualified` = 당일 `verified_cycles[h] >= 3` 이고 `trained_cycles[h] >= 3`
- `active` = `qualified=True` 이고 품질 게이트를 통과해 실제 앙상블에 반영되는 상태
- 자격 전 호라이즌은:
  - 방향 판단 미사용
  - confidence 판단 미사용
  - 다른 호라이즌 fallback source로도 미사용

## 자격 획득 시점 예시

- `1m`: 최소 3분 후
- `3m`: 최소 9분 후
- `5m`: 최소 15분 후
- `10m`: 최소 30분 후
- `15m`: 최소 45분 후
- `30m`: 최소 90분 후

## 설계 결정 (사전 확정 — 구현 전 변경 불가)

### [결정 A] HorizonDecorrelator와 비중 조합 방식

**결정: Decorrelator 마스크 후 재정규화**

고정 비중 테이블 사용을 **폐기**한다. 대신:

1. `ensemble_decision.py`의 `compute()` 에서 `cur_weights = decorr.weights` 가져온 후
2. inactive 호라이즌에 weight=0 을 덮어씌우고
3. 남은 active 호라이즌의 가중치를 재정규화한다.

```python
# compute() 내부 (Decorr.push() 후)
for h in list(cur_weights.keys()):
    if h not in active_horizons:
        cur_weights[h] = 0.0
_total = sum(cur_weights.values())
if _total <= 0:
    return _flat_result()          # active 없음 → 안전 처리 (Patch 6)
cur_weights = {h: w / _total for h, w in cur_weights.items()}
```

**이유**:
- 고정 테이블은 실측 호라이즌 간 상관관계를 무시 → HorizonDecorrelator가 30분 이상 쌓이면 실측 기반으로 자동 최적화됨
- 단순 마스크+재정규화가 사실상 "active horizon 내 최선 비중"을 유지하므로 고정 테이블 대비 정보 손실 없음
- `ENSEMBLE_WEIGHTS_CORR_ADJ` 정적 추정치(MIN_SAMPLES < 30 시 사용)에도 동일하게 적용 → 일관된 경로

**고정 비중 테이블(아래 동적 비중 정책 섹션)은 삭제하고 `settings.py`에 추가하지 않는다.**

---

### [결정 B] 합의도 패널티 분모

**결정: active horizon 기준 집계 + 과반 미달 패널티**

```python
# ensemble_decision.py compute() — 합의도 패널티 블록 교체
if direction != DIRECTION_FLAT:
    _n_active = sum(1 for h, w in cur_weights.items() if w > 0)
    _n_agree  = sum(
        1 for h, h_res in horizon_proba.items()
        if cur_weights.get(h, 0.0) > 0 and h_res.get("direction") == direction
    )
    # 과반 미달(active 중 절반 미만 동의) = 노이즈 신호
    if _n_active > 0 and _n_agree < _n_active / 2:
        confidence = round(confidence * 0.92, 6)
        ...
```

**이유**:
- 기존 `n_agree <= 2` 는 6개 기준으로 설계됨. active 3개일 때 n_agree=2(67% 합의)에도 패널티 발동 → 과도 억제
- active 과반이 동의하면 합의 인정. n_active=1이면 n_agree=1 ≥ 0.5 → 패널티 없음 (단일 호라이즌 보호)
- `cur_weights`를 기준으로 집계하므로 inactive 호라이즌 방향이 혼입되지 않음

---

### [결정 C] 장중 재시작 시 verified_cycles 복원

**결정: DB 기반 복원 + trained_cycles는 verified_cycles와 동일 초기화**

`connect_broker()` 장중 재시작 시 아래 절차 추가:

```python
def _restore_qualification_state(self):
    today = datetime.date.today().isoformat()
    for h in HORIZONS:
        n = self.pred_buffer.count_verified_today(h, today)   # 신규 헬퍼
        self._horizon_runtime_state[h]["verified_cycles"] = n
        # GBM pkl 존재 → trained_cycles = verified_cycles 로 동기화
        # (SGD는 재시작 후 0부터 시작하지만 GBM이 있으면 학습된 것으로 간주)
        self._horizon_runtime_state[h]["trained_cycles"]  = n
```

`prediction_buffer.py` 에 헬퍼 추가:

```python
def count_verified_today(self, horizon: str, date_str: str) -> int:
    conn = sqlite3.connect(self._db_path)
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM predictions WHERE horizon=? AND date(ts)=? AND verified=1",
        (horizon, date_str),
    )
    return c.fetchone()[0]
```

**이유**:
- 장중 재시작 후 SGD는 초기화되지만 GBM pkl 은 유지됨
- DB verified 건수가 당일 실질적 자격 획득 여부의 유일한 신뢰 소스
- `trained_cycles`를 0으로 두면 이미 자격을 갖췄던 호라이즌이 재자격 대기에 빠져 진입 공백 발생

---

## 동적 비중 정책

[결정 A]에 의해 고정 비중 테이블은 사용하지 않는다. 대신:

- **inactive 호라이즌 weight=0** → active 호라이즌만 재정규화
- 품질 게이트가 발동하면 해당 호라이즌 weight를 추가로 감산 후 재정규화

아래는 참고용 초기 비중 기댓값(고정 테이블 아님):

| active 집합 | 기대 비중 흐름 |
|---|---|
| `1m` 단독 | decorr 정적 추정치: 1m=0.21 → 재정규화=1.00 |
| `1m+3m` | 1m≈0.55, 3m≈0.45 (정적 추정치 재정규화 결과) |
| `1m+3m+5m` | 1m≈0.40, 3m≈0.33, 5m≈0.27 |
| 전체 6개 | ENSEMBLE_WEIGHTS_CORR_ADJ 그대로 적용 |

품질 저하가 있으면 해당 호라이즌 비중 감산 후 나머지 재정규화를 한 번 더 적용한다.

## 품질 게이트 초안

- 최근 정확도 하한 미달 시 해당 호라이즌 비중 `0` 또는 강한 감산
- 단일 방향 편향 `>= 75%` 시 비중 `50% 감산`
- 상태 구분:
  - `not_qualified`
  - `qualified_active`
  - `qualified_penalized`
  - `qualified_blocked`

## 폴백 제거 원칙

- 호라이즌별 confidence가 아직 자격을 못 얻었으면 그냥 미사용 처리
- 앙상블 calibrator가 충분히 학습되지 않았더라도 다른 호라이즌 calibrator를 빌려오지 않음
- 특히 `3m` fallback 제거

## 영향 범위

- `main.py`
  - 당일 호라이즌 자격 상태 저장 (`_horizon_runtime_state`)
  - cycle 카운트 갱신 (`_horizon_counts[h]` 참조)
  - 품질 통계 축적
  - dashboard 전달 payload 구성
  - `_restore_qualification_state()` 신규 (장중 재시작 복원)
- `model/ensemble_decision.py`
  - `compute()` 에 `active_horizons: set` 파라미터 추가
  - Decorr 마스크+재정규화 ([결정 A])
  - 합의도 패널티 동적화 ([결정 B])
  - fallback 제거
  - `detail[h]`에 `qualified/active/status/weight` 포함
- `learning/prediction_buffer.py`
  - `count_verified_today(h, date_str)` 헬퍼 추가 ([결정 C])
- `learning/calibration.py`
  - 로직 변경 최소화, 호출 정책 변경
- `dashboard/main_dashboard.py`
  - 체크박스 상단 카드 추가
  - 자격/진행도/비중/정확도 상태 표시
- `config/settings.py`
  - `HORIZON_QUALIFY_MIN_CYCLES = 3`
  - 품질 게이트 임계치
  - **동적 비중 테이블 상수 추가 않음** ([결정 A])

## Code Patch Breakdown

### Patch 1. 설정 상수 추가

대상:

- `config/settings.py`

작업:

- `HORIZON_QUALIFY_MIN_CYCLES = 3` 추가
- 품질 게이트 임계치 상수 추가 (`QUALIFY_QUALITY_MIN_SAMPLES = 10` 등)
- **동적 비중 테이블 상수 추가 안 함** — [결정 A]에 의해 Decorr 재정규화로 대체

완료 기준:

- 자격/품질 게이트가 설정 상수로 한 곳에 모임 (비중은 ensemble_decision.py 내부)

### Patch 2. 런타임 상태 구조 도입

대상:

- `main.py`

작업:

- `self._horizon_runtime_state` 신규 도입
- 호라이즌별 아래 필드 관리
  - `verified_cycles`
  - `trained_cycles`
  - `qualified`
  - `active`
  - `status`
  - `weight`
  - `recent_accuracy`
  - `bias_up`
  - `bias_dn`
  - `bias_fl`
- 일간 리셋 시 해당 상태 초기화

완료 기준:

- 장중 언제든 각 호라이즌의 자격 상태를 단일 구조에서 조회 가능

### Patch 3. 검증 완료 기준 cycle 반영

대상:

- `main.py`

작업:

- STEP 1 검증 완료 루프에서 호라이즌별 `verified_cycles += 1`
- 검증 결과를 bias/accuracy 버퍼와 함께 상태 구조에 반영
- 자격 획득 시 1회성 로그 출력

완료 기준:

- 만기 검증 완료 건수가 호라이즌별 정확히 집계됨

### Patch 4. 학습 완료 기준 cycle 반영

대상:

- `main.py`

작업:

- STEP 2 `online_learner.learn(h, ...)` 호출 후 `_horizon_runtime_state[h]["trained_cycles"]`를
  `online_learner._horizon_counts[h]` 와 동기화 (별도 카운터 없이 기존 값 참조)
- `verified_cycles >= 3` and `trained_cycles >= 3` 이면 `qualified=True`
- `qualified` 전에는 active로 승격 금지

완료 기준:

- "검증은 됐지만 아직 학습 반영 전" 상태와 "실제 자격 획득" 상태가 분리됨

주의:

- `_bucket_learn_count`는 short/long 버킷 기준이므로 Qualification 카운터로 사용 불가
- `_horizon_counts[h]`(호라이즌별 누적 learn() 횟수)를 직접 참조한다

### Patch 5. active horizon 집합 계산 함수 추가

대상:

- `main.py`

작업:

- 현재 qualified horizon 집합 계산 (`qualified=True` 호라이즌 set 반환)
- 품질 게이트 적용 후 최종 `active/penalized/blocked` 상태 계산
- `compute()` 호출 시 `active_horizons` set 을 파라미터로 전달
- **비중 계산은 `ensemble_decision.py` 내부** — `compute()` 에서 decorr 마스크+재정규화로 처리 ([결정 A])
- 고정 비중 테이블 lookup 로직 불필요 — 구현하지 않음

완료 기준:

- 장중 특정 시점의 active horizon 집합을 함수 하나로 재현 가능
- `compute()` 가 active_horizons 외 호라이즌을 가중합에 포함하지 않음

### Patch 6. 앙상블 입력 필터링

대상:

- `model/ensemble_decision.py`
- `main.py`

작업:

- `ensemble.compute()` 시그니처에 `active_horizons: set` 파라미터 추가
- `compute()` 내부 ([결정 A]):
  - `cur_weights = decorr.weights` 가져온 후 inactive weight=0, 재정규화
  - `total_w <= 0` → `_flat_result()` 반환
- 합의도 패널티 ([결정 B]):
  - `cur_weights > 0` 인 호라이즌만 n_agree 집계
  - 과반 미달 시 패널티 (기존 `n_agree <= 2` 로직 교체)
- `detail[h]`에 `qualified`, `active`, `status`, `weight` 포함
- active horizon이 없으면 `FLAT/X/conf=0` 처리

완료 기준:

- 앙상블 점수 계산에 자격 없는 호라이즌이 절대 참여하지 않음
- 합의도 패널티가 active 호라이즌 수에 맞게 동적 적용됨

### Patch 7. confidence fallback 제거

대상:

- `model/ensemble_decision.py`
- `main.py`

작업:

- 앙상블 calibrator 미성숙 시 `3m calibrator` fallback 제거
- 호라이즌 자격 전 다른 호라이즌 confidence 차용 제거
- 필요 시 raw confidence 보수 clip만 유지

완료 기준:

- confidence 판단에 다른 호라이즌 데이터가 섞이지 않음

### Patch 8. 품질 게이트 적용

대상:

- `main.py`
- 필요 시 `model/ensemble_decision.py`

작업:

- 최근 적중률과 방향 편향으로 `qualified_active / penalized / blocked` 판정
- `Bias⚠` 로그를 실제 비중 조정과 연결
- 품질 악화 시 비중 감산 또는 0 처리

완료 기준:

- 자격을 얻었더라도 당일 품질이 나쁘면 앙상블 기여도가 자동 축소됨

### Patch 9. Dashboard 카드 추가

대상:

- `dashboard/main_dashboard.py`

작업:

- 체크박스 상단에 horizon qualification 카드 영역 추가
- 카드별 표시:
  - horizon 명
  - cycle 진행도 `n/3`
  - 상태 텍스트
  - 현재 반영 비중
  - 최근 정확도
- 색상 규칙:
  - 회색 `WAIT`
  - 초록 `ACTIVE`
  - 주황 `PENALIZED`
  - 빨강 `BLOCKED`

완료 기준:

- 사용자가 현재 어떤 호라이즌이 신뢰도 판단에 실제 참여 중인지 즉시 인지 가능

### Patch 10. Dashboard 데이터 연결

대상:

- `main.py`
- `dashboard/main_dashboard.py`

작업:

- 런타임 상태를 dashboard update payload에 포함
- 분 단위 갱신마다 qualification 카드 상태 갱신

완료 기준:

- 엔진 상태와 UI 표시가 동일한 기준으로 동작

### Patch 11. 로그/운영 가시성 보강

대상:

- `main.py`
- `model/ensemble_decision.py`

작업:

- 자격 획득 로그 추가
- 비중 변경 로그 추가
- 품질 페널티 로그 추가
- 필요 시 하루 시작 후 active horizon 변천 로그 요약

완료 기준:

- 로그만 봐도 어느 시점에 어떤 호라이즌이 참여했는지 추적 가능

### Patch 12. 일간 리셋 및 복구 경로

대상:

- `main.py`
- `learning/prediction_buffer.py`

작업:

**A. 일간 리셋 (장 시작 전 / `daily_close()` 내)**
- `_horizon_runtime_state` 전체 필드 초기화
- 전일 qualification 상태가 남지 않도록 보장

**B. 장중 재시작 복구 ([결정 C])**
- `connect_broker()` 장중 재시작 분기에 `_restore_qualification_state()` 추가
- DB 당일 verified 건수로 `verified_cycles` 및 `trained_cycles` 복원
- `prediction_buffer.count_verified_today(h, date_str)` 헬퍼 신규 추가

```python
# prediction_buffer.py 추가
def count_verified_today(self, horizon: str, date_str: str) -> int:
    conn = sqlite3.connect(self._db_path)
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM predictions "
        "WHERE horizon=? AND date(ts)=? AND verified=1",
        (horizon, date_str),
    )
    result = c.fetchone()[0]
    conn.close()
    return result
```

완료 기준:

- 당일 기준 qualification 상태 보장
- 장중 재시작 후 이미 earned된 자격이 소실되지 않음

## Implementation Plan

> **핵심 원칙**: Dashboard(dry-run)로 상태 추적을 먼저 눈으로 확인한 뒤 앙상블 실제 변경을 적용한다.  
> Qualification 변경과 품질 게이트를 동일 배포에 넣지 않는다 — 어떤 변경이 어떤 결과를 냈는지 분리 불가능해진다.

### Phase 1. 상태 추적 시작 (앙상블 미변경)

목표:

- `_horizon_runtime_state` 구조 도입 및 cycle 카운터 가동
- 앙상블 동작은 현재와 동일하게 유지
- 로그와 대시보드로 자격 획득 타이밍 검증

패치 범위: Patch 2 · Patch 3 · Patch 4

산출물:

- 매분 로그에 `[Qualify] 1m verified=1/3 trained=1/3` 형식 출력
- 장 초반 자격 공백 시간대가 예상과 일치하는지 확인

리스크:

- 없음 (앙상블 비변경)

---

### Phase 2. Dashboard Dry-run 검증

목표:

- Qualification 카드 UI 추가
- 하루 실세션으로 자격 획득 시점·비중 변화가 예상과 맞는지 눈으로 확인
- 앙상블 동작은 여전히 현재와 동일

패치 범위: Patch 9 · Patch 10

산출물:

- 6개 호라이즌 qualification 카드 (WAIT/ACTIVE/PENALIZED/BLOCKED 색상)
- cycle 진행도 `n/3`, 상태, 현재 비중, 최근 정확도 표시

리스크:

- 기존 대시보드 레이아웃과 충돌 가능 → 레이아웃 확인 후 배포

---

### Phase 3. 앙상블 실제 변경

목표:

- active horizon 기반 앙상블 전환
- fallback 완전 제거
- 장중 재시작 복원 경로 확보

패치 범위: Patch 1 · Patch 5 · Patch 6 · Patch 7 · Patch 12

산출물:

- `ensemble.compute(active_horizons)` 전환
- `3m calibrator fallback` 제거
- `count_verified_today()` 헬퍼 + `_restore_qualification_state()`

리스크:

- 장 초반 active horizon 부족으로 진입 수 감소 → **의도된 변화**
- fallback 제거 후 conf 분포 변화 → Phase 2 dry-run 결과와 비교하며 모니터링

---

### Phase 4. 품질 게이트 + 로그/가시성 보강

목표:

- 자격 획득 후에도 품질 불량 호라이즌 영향 제한
- 운영 가시성 완성

패치 범위: Patch 8 · Patch 11

산출물:

- 정확도 하한·방향 편향 기반 weight penalty/block
- 자격 획득·비중 변경·패널티 로그 (로그만으로 전체 흐름 추적 가능)

리스크:

- 품질 게이트가 과도하면 usable horizon 부족 → 최소 샘플 10건 조건 필수

---

## 30m 호라이즌 운영 주의사항

```
15:10 강제 청산 기준 운영 시간 370분 → 30m 최대 9 cycle/일
품질 게이트 최소 10건 조건 → 매일 장 마감 무렵에야 품질 평가 가능
실질적으로 30m는 heuristic decorative 역할

조치: 1개월 운영 데이터 후 품질 게이트 작동 빈도 기반 삭제 검토
현재 CORR_ADJ 0.15는 유지 (가중치가 낮아 리스크 제한적)
```

## Todo List

### Phase 1 Must — 상태 추적 시작 (앙상블 미변경)

- [ ] `main.py` — `_horizon_runtime_state` dict 구조 도입 (verified/trained/qualified/active/status/weight/recent_accuracy/bias 필드)
- [ ] `main.py` STEP 1 — `verified_cycles[h] += 1` 호라이즌별 누적 (pred_buffer.verify_and_update 루프)
- [ ] `main.py` STEP 2 — `trained_cycles[h]` = `online_learner._horizon_counts[h]` 동기화 (`_bucket_learn_count` 사용 금지)
- [ ] `main.py` — `[Qualify] h verified=N/3 trained=N/3` 형식 DEBUG 로그 추가
- [ ] `main.py` 일간 리셋 — `_horizon_runtime_state` 초기화 (`daily_close()` 내)

### Phase 2 Must — Dashboard Dry-run

- [ ] `dashboard/main_dashboard.py` — qualification 카드 영역 추가 (6개 호라이즌, 색상: 회색 WAIT / 초록 ACTIVE / 주황 PENALIZED / 빨강 BLOCKED)
- [ ] `dashboard/main_dashboard.py` — 카드별 cycle 진행도 `n/3`, 상태 텍스트, 현재 반영 비중, 최근 정확도 표시
- [ ] `main.py` — `_horizon_runtime_state` → dashboard update payload 포함 (분 단위 갱신)

### Phase 3 Must — 앙상블 실제 변경

- [ ] `config/settings.py` — `HORIZON_QUALIFY_MIN_CYCLES=3`, `QUALIFY_QUALITY_MIN_SAMPLES=10` 추가 (동적 비중 테이블 상수 추가 안 함 [결정A])
- [ ] `main.py` — `_get_active_horizons()` 함수 (`verified ≥ 3 AND trained ≥ 3` 판정, set 반환)
- [ ] `main.py` STEP 6 — `ensemble.compute(active_horizons=...)` 호출로 변경
- [ ] `model/ensemble_decision.py` — `compute(active_horizons: set)` 파라미터 추가
- [ ] `model/ensemble_decision.py` — [결정A] decorr 마스크+재정규화 (inactive weight=0 후 재정규화, total_w=0 → `_flat_result()`)
- [ ] `model/ensemble_decision.py` — [결정B] 합의도 패널티 교체 (`n_agree < n_active/2` 과반 미달, `cur_weights > 0` 기준 집계)
- [ ] `model/ensemble_decision.py` — 3m fallback 제거 (`ensemble_calibrator` 미학습 시 raw conf 보수 clip만 유지)
- [ ] `model/ensemble_decision.py` — `detail[h]`에 `qualified/active/status/weight` 필드 추가
- [ ] `main.py` — active horizon 없을 때 `FLAT/X/conf=0` 안전 처리
- [ ] `learning/prediction_buffer.py` — `count_verified_today(h, date_str)` 헬퍼 추가 [결정C]
- [ ] `main.py` — `_restore_qualification_state()` 신규 (`connect_broker()` 장중 재시작 분기에 추가) [결정C]

### Phase 4 Must — 품질 게이트 + 가시성

- [ ] `main.py` — `_compute_qualified_status()` → active/penalized/blocked 분류 함수
- [ ] `main.py` — 최근 정확도 기반 weight penalty (최소 `QUALIFY_QUALITY_MIN_SAMPLES=10`건 미충족 시 게이트 skip)
- [ ] `main.py` — 방향 편향 ≥ 75% 시 비중 50% 감산 (기존 `_bias_buf` 연결)
- [ ] `main.py` — 자격 획득 1회성 로그 `[Qualify] Xm 자격 획득 → active`
- [ ] `main.py` — 비중 변경·패널티 발동 로그 추가
- [ ] `model/ensemble_decision.py` — 품질 패널티 후 재정규화 로그

### Should

- [ ] `main.py` — 하루 active horizon 변화 이력 로그 (자격 취득 시점마다 기록, `daily_close()` 시 요약)
- [ ] `dashboard/main_dashboard.py` — qualification 카드에 최근 적중률·편향 툴팁 추가

### Nice to Have

- [ ] active horizon 조합별 실전 성능 로그 축적 (1개월 후 30m 삭제 검토 근거 데이터)

## 검증 체크리스트

- [ ] 09:00 직후에는 어떤 호라이즌도 자격 없음으로 표시되는지 확인
- [ ] 09:03 이후 `1m`만 자격 획득하는지 확인
- [ ] 09:09 이후 `3m` 자격 획득으로 비중이 `1m+3m` 구조로 바뀌는지 확인
- [ ] 09:30 이전에는 `10m`가 앙상블에 절대 참여하지 않는지 확인
- [ ] 10:30 이전에는 `30m`가 절대 active 되지 않는지 확인
- [ ] fallback 제거 후에도 시스템이 `FLAT/X`로 안전 동작하는지 확인
- [ ] dashboard 카드와 실제 active horizon 로그가 일치하는지 확인

## GBM/SGD 비중과 Qualification 상호작용 분석

### 현재 GBM·SGD 블렌딩 구조

```
MultiHorizonModel(GBM pkl) + OnlineLearner(SGD) → blend_with_gbm() → horizon_proba[h]
                                                                           ↓
EnsembleDecision.compute(active_horizons) → Decorr 마스크+재정규화 → final conf
```

### 핵심 사실

| 항목 | 내용 |
|---|---|
| GBM | 장 시작 전 pkl 로드 고정. 장중 불변 |
| SGD | 매분 STEP 2에서 partial_fit. `_horizon_counts[h]`로 호라이즌별 추적 |
| GBM/SGD 블렌딩 | `blend_with_gbm()` — `_horizon_counts[h] < 30`이면 w_gbm=0.95 |
| 버킷 분리 | short(1/3/5m) / long(10/15/30m) 독립 SGD 가중치 동적 조정 |

### Qualification과의 상호작용 — 문제 없음

- **inactive 호라이즌의 GBM+SGD 블렌딩**: `blend_with_gbm()` 는 여전히 수행됨. 단, `active_horizons`
  필터로 앙상블 가중합에서 배제되므로 최종 신호에 영향 없음. 예측 연산 자체는 6개 호라이즌 모두 유지
  (~5ms 추가, 무시 가능)
- **long 버킷 SGD 가중치 조정**: 10m/15m/30m가 inactive인 장 초반 90분 동안 long 버킷
  `_adjust_weights()` 는 호출되지 않음(검증 건수 없음). 이는 의도된 자연스러운 동작

### `_bucket_learn_count` 사용 금지

`_bucket_learn_count["short"|"long"]` 는 short/long 버킷 기준 집계이므로 **호라이즌별 Qualification 카운터로 사용 불가**.
`_horizon_counts[h]` (호라이즌별 learn() 총 호출 횟수)를 `trained_cycles` 소스로 사용한다.

### 품질 게이트 샘플 수 주의

- 자격 취득 시점(verified=3)의 샘플:
  - `1m` → 3건 (0/33/67/100% 4가지 정확도만 가능)
  - `30m` → 3건 (90분간 데이터)
- **품질 게이트(정확도 하한·편향 판정)는 최소 10건 이상 쌓인 후에만 적용**
  - Patch 8 에서 `if len(acc_samples) < 10: skip` 조건 추가 필수

---

## 메모

- 본 변경은 "당일 자기 데이터로 자격을 획득한 호라이즌만 당일 신뢰도 판단에 사용한다"는 운영 철학을 코드에 강제하는 작업이다.
- 장 초반 진입 수 감소는 의도된 변화일 가능성이 높다.
- 실제 적용 전 시뮬레이션 모드와 로그 검증이 먼저 필요하다.
- **설계 결정 A/B/C 는 구현 도중 임의 변경 금지** — 변경 시 이 문서를 먼저 수정하고 이유를 기록한다.
