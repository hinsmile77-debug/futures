# Rolling σ 임계값 구현 계획

> 작성일: 2026-05-30  
> 전제: 방법3(rolling sigma × k=0.41) 단독 채택  
> 분석 근거: `docs/THRESHOLD_WFA_MONITOR.md`, 이 세션 진입 0 원인 분석

---

## 배경 요약

| 문제 | 원인 | 해결책 |
|---|---|---|
| 5/19~5/29 진입 0 | 저변동성 장세 → 구 threshold로 FLAT 50~70% → confidence 붕괴 | 방법3: rolling σ로 FLAT 33% 안정 |
| 날별 FLAT 편차 14%p | 정적 threshold가 변동성 변화 미반영 | rolling σ가 자동 적응 → std 3.2%p |
| SGD 레이블 불일치 | verify 시점과 예측 시점의 threshold 불일치 | 방안B: 예측 시점 sigma 저장 후 사용 |

**방법별 1m FLAT 안정성 비교 (21 거래일):**

| 방법 | 평균 FLAT | std(FLAT) | 진입 0 재발 위험 |
|---|---|---|---|
| 방법1 (현재 정적) | 37.3% | 14.4%p | 높음 |
| 방법2 (σ_1min×√t) | 37.1% | 14.3%p | 높음 (방법1과 동일) |
| **방법3 (rolling×k)** | **32.5%** | **3.2%p** | **낮음** |

---

## 전체 변경 파일 목록

| 파일 | Phase | 핵심 변경 내용 |
|---|---|---|
| `config/settings.py` | P0 | SIGMA_K, USE_ROLLING_SIGMA_THRESHOLD 추가 |
| `main.py` | P0 | sigma_buf·sigma_20·sigma_ready 추가, STEP 파이프라인 연결, 진입 게이트 |
| `learning/batch_retrainer.py` | P0 | _load_from_db() 봉별 rolling sigma 레이블 생성 (방법B 핵심) |
| `learning/prediction_buffer.py` | P1 | save_prediction에 sigma_at_t 추가, verify 시 저장값 사용 |
| `dashboard/panels/threshold_monitor_panel.py` | 완료 | Phase A k값 모니터 패널 (이미 구현) |
| `dashboard/main_dashboard.py` | 완료 | "📐 임계값 모니터" 탭 추가 (이미 구현) |

---

## Phase 0 — 기구현 (90차 완료)

- [x] `HORIZON_THRESHOLDS` 데이터 기반 재보정 (1m→0.041%, 15m→0.155%, 30m→0.196%)
- [x] `HORIZON_THRESHOLDS_RESEARCH` 비대칭 딕셔너리 신규
- [x] `SGD_FULL_RESET_PENDING` 플래그 + `_on_gbm_retrain_done` 1회 리셋 처리
- [x] `build_targets_asymmetric()` 연구용 비대칭 레이블 생성 함수
- [x] `OnlineLearner.reset_full()` SGD 완전 초기화 메서드
- [x] `ThresholdRecalibrator` Phase A 롤링 재보정 모니터
- [x] `ThresholdMonitorPanel` 대시보드 UI 패널
- [x] class_weight 재조정 (1m/5m FL 0.85, 30m FL 1.00)

---

## Phase 1 (P0) — 방법3 핵심 구현

> **3개 파일, 약 100줄 추가/변경**  
> 이 Phase 완료 후 진입 0 재발 방지 효과 발현

### 1-1. `config/settings.py` — 플래그 추가

```python
# rolling σ 임계값 설정
SIGMA_K: float = 0.41            # FLAT 목표 34% 달성 계수 (실측 기반)
SIGMA_W: int   = 20              # rolling window 크기 (봉 수)
SIGMA_W_MIN: int = 5             # 최소 유효 봉 수 (미달 시 전날 EOD 사용)

# ATR 동적 threshold 점진 제거 플래그
# True: rolling σ 사용 / False: 기존 ATR 방식 (전환 기간 안전망)
USE_ROLLING_SIGMA_THRESHOLD: bool = True
```

**변경 위치:** `HORIZON_THRESHOLDS_RESEARCH` 블록 아래 추가

---

### 1-2. `main.py` — sigma 버퍼 + 파이프라인 연결 + 진입 게이트

#### (a) `__init__` 초기화 추가

```python
# rolling σ 임계값 (방법3)
self._sigma_buf: deque = deque(maxlen=20)    # 1분봉 수익률 rolling 버퍼
self._sigma_20:  float = 0.0                 # 현재 rolling σ (%)
self._sigma_ready: bool = False              # 20봉 달성 플래그
self._last_sigma_20: float = 0.0            # 전날 EOD sigma (장 초반 초기값)

# GBM 첫 재학습 전 사이즈 제어
self._pre_retrain_done: bool = False         # 첫 재학습 완료 여부
```

**변경 위치:** `self._threshold_monitor_tick` 선언 근처 (~line 342)

#### (b) 매분 파이프라인 sigma 갱신 (STEP 1 직전)

```python
# ── rolling σ 갱신 ─────────────────────────────────────
if self._last_pipeline_price and close and self._last_pipeline_price > 0:
    _ret_1m = (close - self._last_pipeline_price) / self._last_pipeline_price * 100
    self._sigma_buf.append(_ret_1m)

_n_sigma = len(self._sigma_buf)
if _n_sigma >= runtime_settings.SIGMA_W_MIN:
    _v = list(self._sigma_buf)
    _m = sum(_v) / _n_sigma
    self._sigma_20 = math.sqrt(sum((x - _m) ** 2 for x in _v) / (_n_sigma - 1))
    self._sigma_ready = (_n_sigma >= runtime_settings.SIGMA_W)
    # HORIZON_THRESHOLDS 매분 갱신 (rolling σ 기반)
    if runtime_settings.USE_ROLLING_SIGMA_THRESHOLD and self._sigma_20 > 0:
        import math as _math
        from config import settings as _cfg
        K = _cfg.SIGMA_K
        _cfg.HORIZON_THRESHOLDS.update({
            "1m":  self._sigma_20 / 100 * K * _math.sqrt(1),
            "3m":  self._sigma_20 / 100 * K * _math.sqrt(3),
            "5m":  self._sigma_20 / 100 * K * _math.sqrt(5),
            "10m": self._sigma_20 / 100 * K * _math.sqrt(10),
            "15m": self._sigma_20 / 100 * K * _math.sqrt(15),
            "30m": self._sigma_20 / 100 * K * _math.sqrt(30),
        })
elif self._last_sigma_20 > 0:
    # 20봉 미수집: 전날 EOD sigma로 대체
    self._sigma_20 = self._last_sigma_20
```

**변경 위치:** STEP 1 직전, `_st.append(("S1", ...))` 위

#### (c) STEP 6 진입 게이트 추가

```python
# ── 최적 진입 시점 게이트 ───────────────────────────────
_now_hm = datetime.datetime.now().strftime("%H%M")

# 09:00~09:19: 진입 금지 (sigma_20봉 미수집 + GAP_OPEN 위험)
if _now_hm < "0920":
    _gate_block_sigma = True
    log_manager.signal("[EntryGate] sigma_20봉 미수집 — 진입 대기 (09:20 해제)")
    # grade 강제 X 처리 (기존 흐름 유지)
    _final_grade = "X"

# 09:20~09:29: 조건부 소규모 진입 (grade A만, size×0.5, min_conf 0.60)
elif _now_hm < "0930":
    actual_min_conf = max(actual_min_conf, 0.60)
    if _final_grade in ("B", "C"):
        _final_grade = "X"   # A 등급만 허용
    _pre_retrain_size_mult_local = 0.5
    log_manager.signal("[EntryGate] 조건부 진입 구간 (A등급·size×0.5)")

# 09:30~: 표준 진입
# GBM 첫 재학습 전 사이즈 제어
if not self._pre_retrain_done:
    _pre_retrain_size_mult_local = min(
        getattr(self, "_pre_retrain_size_mult_local", 1.0), 0.6
    )
```

**변경 위치:** STEP 6 진입 판단 직후

#### (d) `_on_gbm_retrain_done` 첫 재학습 완료 처리

```python
# 기존 SGD_FULL_RESET_PENDING 처리 블록 아래에 추가
if not self._pre_retrain_done:
    self._pre_retrain_done = True
    log_manager.system("[EntryGate] GBM 첫 재학습 완료 — 사이즈 제한 해제")
```

#### (e) `daily_close` — EOD sigma 저장

```python
# 일일 리셋 직전에 추가
if self._sigma_20 > 0:
    self._last_sigma_20 = self._sigma_20
    log_manager.learning(f"[Sigma] EOD sigma_20={self._sigma_20:.5f}%% 저장 (다음날 초기값)")
self._sigma_buf.clear()
self._sigma_ready = False
self._pre_retrain_done = False   # 다음날 재학습 완료 전까지 제어 재활성
```

---

### 1-3. `learning/batch_retrainer.py` — 방법B 봉별 rolling sigma 레이블 (핵심)

**변경 위치:** `_load_from_db()` 내 y 라벨 생성 루프 (~line 392)

**현재 코드:**
```python
for hz, h_min in HORIZONS.items():
    threshold = HORIZON_THRESHOLDS.get(hz, 0.0003)  # 재학습 시점 단일값 균일 적용
    y = []
    for ts, _ in records:
        ...
        label = build_single_target(curr_close, future_close, threshold)
        y.append(label)
```

**변경 후:**
```python
from collections import deque as _deque
import math as _math
from config.settings import SIGMA_K, SIGMA_W, SIGMA_W_MIN

for hz, h_min in HORIZONS.items():
    y = []
    # 방법B: 각 봉의 시점별 rolling sigma로 threshold 계산
    _sigma_buf_rt = _deque(maxlen=SIGMA_W)

    for ts, feat_dict in records:
        # 1m 수익률로 rolling sigma 업데이트
        _c0 = close_map.get(ts)
        _t_prev = (datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                   - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
        _c_prev = close_map.get(_t_prev)
        if _c0 and _c_prev and _c_prev > 0:
            _sigma_buf_rt.append((_c0 - _c_prev) / _c_prev * 100)

        # threshold 결정
        _n = len(_sigma_buf_rt)
        if _n >= SIGMA_W_MIN and _n > 1:
            _v = list(_sigma_buf_rt)
            _m = sum(_v) / _n
            _sigma = _math.sqrt(sum((x - _m) ** 2 for x in _v) / (_n - 1))
            threshold = _sigma / 100 * SIGMA_K * _math.sqrt(h_min)
        else:
            # 초기 봉 부족: BASE threshold 사용
            threshold = HORIZON_THRESHOLDS.get(hz, 0.0003)

        future_ts = (
            datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            + datetime.timedelta(minutes=h_min)
        ).strftime("%Y-%m-%d %H:%M:%S")
        curr_close   = close_map.get(ts)
        future_close = close_map.get(future_ts)
        if curr_close and future_close:
            label = build_single_target(curr_close, future_close, threshold)
        else:
            label = 0
        y.append(label)
    y_dict[hz] = np.array(y, dtype=int)
```

**효과:** 방법B 적용 시 전체 FLAT=32.8% (방법A 균일=28.1% 대비), 날별 편차 26~39%p 안정

---

## Phase 2 (P1) — SGD 방안B + GBM 사이즈 제어 정밀화

> **2개 파일, 약 50줄 추가/변경**

### 2-1. `learning/prediction_buffer.py` — 방안B: 예측 시점 sigma 저장

**목표:** verify 시 현재 HORIZON_THRESHOLDS 대신 예측 저장 시점의 sigma × k 사용

#### save_prediction 시그니처 확장

```python
def save_prediction(
    self,
    ts: str,
    horizon: str,
    direction: int,
    confidence: float,
    up_prob=None,
    down_prob=None,
    flat_prob=None,
    features=None,
    sigma_at_t: float = 0.0,    # ← 추가: 예측 시점의 sigma_20 (%)
):
```

**DB 저장:** `predictions` 테이블에 `sigma_at_t` 컬럼 추가 (마이그레이션 필요)

```sql
ALTER TABLE predictions ADD COLUMN sigma_at_t REAL DEFAULT 0.0;
```

#### verify_and_update에서 저장값 사용

```python
# 현재
threshold = HORIZON_THRESHOLDS.get(horizon, 0.0003)

# 변경 후
sigma_saved = row.get("sigma_at_t", 0.0) or 0.0
if sigma_saved > 0 and SIGMA_K > 0:
    import math as _math
    from config.settings import SIGMA_K, HORIZONS as _HZ
    h_min = _HZ.get(horizon, 1)
    threshold = sigma_saved / 100 * SIGMA_K * _math.sqrt(h_min)
else:
    threshold = HORIZON_THRESHOLDS.get(horizon, 0.0003)
```

#### main.py save_prediction 호출부에 sigma_at_t 전달

```python
self.pred_buffer.save_prediction(
    ...,
    sigma_at_t=self._sigma_20,    # ← 추가
)
```

**변경 위치:** main.py STEP 5 예측 저장 부분

---

### 2-2. GBM 재학습 전 사이즈 제어 — settings.py 상수화

```python
# GBM 첫 재학습 완료 전 진입 사이즈 배율
PRE_RETRAIN_SIZE_MULT: float = 0.6   # 40% 축소
```

---

## Phase 3 (P2) — ATR 점진 제거

> **1개 파일, 약 20줄 변경**  
> Phase 1 안정 확인 후 (2~4주) 실행

### 3-1. `main.py` — `_log_threshold_monitor` 비활성화

```python
def _log_threshold_monitor(self, atr: float, price: float) -> None:
    from config import settings as _cfg
    # rolling σ 사용 중이면 ATR 동적 갱신 건너뜀
    if _cfg.USE_ROLLING_SIGMA_THRESHOLD:
        return
    # 기존 ATR 로직 유지 (안전망)
    ...
```

### 3-2. `config/settings.py` — ATR 관련 상수 deprecated 표시

```python
# DEPRECATED: USE_ROLLING_SIGMA_THRESHOLD=True 시 미사용
# Phase 1 안정 2~4주 후 제거 예정
HORIZON_THRESHOLD_MULT = {...}       # deprecated
HORIZON_THRESHOLD_OPEN_MULT = 1.5   # deprecated
```

### 3-3. 완전 제거 시점 (Phase 3 완료 후)

제거 대상:
- `_log_threshold_monitor()` 함수 전체
- `_threshold_monitor_tick` 카운터
- `HORIZON_THRESHOLD_MULT`, `HORIZON_THRESHOLD_OPEN_MULT` 설정값
- `settings.py` line 93-99 ATR multiplier 블록

---

## 구현 순서 및 의존성

```
[P0-a] settings.py SIGMA_K/W/USE_ROLLING 추가
    ↓
[P0-b] batch_retrainer.py 방법B 레이블 생성 ← 가장 임팩트 큰 변경
    ↓
[P0-c] main.py sigma_buf + HORIZON_THRESHOLDS 매분 갱신
    ↓
[P0-d] main.py 진입 게이트 (09:20/09:30)
    ↓
[P0-e] main.py GBM 재학습 전 size_mult 제어
    ↓ (P0 완료 후 1~2주 실세션 검증)
[P1-a] prediction_buffer.py DB 마이그레이션 + sigma_at_t 저장
[P1-b] prediction_buffer.py verify 시 저장값 사용
    ↓ (P1 완료 후 2~4주 안정 확인)
[P2]   ATR 점진 제거
```

---

## Todo List

### P0 — 방법3 핵심 (최우선)

- [ ] **[P0-a]** `config/settings.py` — `SIGMA_K=0.41`, `SIGMA_W=20`, `SIGMA_W_MIN=5`, `USE_ROLLING_SIGMA_THRESHOLD=True`, `PRE_RETRAIN_SIZE_MULT=0.6` 추가
- [ ] **[P0-b]** `learning/batch_retrainer.py` — `_load_from_db()` 봉별 rolling sigma 레이블 생성 (방법B 핵심)
  - 기존 `threshold = HORIZON_THRESHOLDS.get(hz, 0.0003)` 균일 적용 교체
  - 각 레코드의 rolling 20봉 sigma × K × √h_min으로 봉별 threshold 계산
  - 초기 5봉 미만: BASE threshold 폴백
- [ ] **[P0-c]** `main.py __init__` — `_sigma_buf`, `_sigma_20`, `_sigma_ready`, `_last_sigma_20`, `_pre_retrain_done` 초기화
- [ ] **[P0-d]** `main.py` 매분 파이프라인 — STEP 1 직전 sigma 갱신 블록 추가
  - `USE_ROLLING_SIGMA_THRESHOLD=True`이면 `HORIZON_THRESHOLDS` 매분 갱신
  - 20봉 미만이면 `_last_sigma_20` 폴백
- [ ] **[P0-e]** `main.py` STEP 6 — 진입 시점 게이트 추가
  - 09:00~09:19: 진입 금지 (`grade="X"`)
  - 09:20~09:29: grade A만, `min_conf=0.60`, `size_mult=0.5`
  - 09:30~: 표준 진입
- [ ] **[P0-f]** `main.py _on_gbm_retrain_done` — `_pre_retrain_done=True` 처리 + 사이즈 복원 로그
- [ ] **[P0-g]** `main.py daily_close` — `_last_sigma_20` 저장 + `_sigma_buf` 초기화 + `_pre_retrain_done=False` 리셋

### P1 — SGD 방안B (P0 완료 후)

- [ ] **[P1-a]** `learning/prediction_buffer.py` — `predictions` 테이블 `sigma_at_t REAL` 컬럼 마이그레이션
- [ ] **[P1-b]** `learning/prediction_buffer.py` — `save_prediction()` 시그니처에 `sigma_at_t` 추가 + DB 저장
- [ ] **[P1-c]** `learning/prediction_buffer.py` — `verify_and_update()` 에서 저장된 `sigma_at_t` 기반 threshold 사용 (방안B)
- [ ] **[P1-d]** `main.py` — 예측 저장 시 `sigma_at_t=self._sigma_20` 전달 (STEP 5)

### P2 — ATR 점진 제거 (P1 완료 후 2~4주)

- [ ] **[P2-a]** `main.py _log_threshold_monitor()` — `USE_ROLLING_SIGMA_THRESHOLD=True`이면 조기 return
- [ ] **[P2-b]** `config/settings.py` — `HORIZON_THRESHOLD_MULT`, `HORIZON_THRESHOLD_OPEN_MULT` deprecated 주석 추가
- [ ] **[P2-c]** `main.py` — `_log_threshold_monitor` 완전 제거 + `_threshold_monitor_tick` 제거
- [ ] **[P2-d]** `config/settings.py` — ATR multiplier 블록 완전 제거

### 검증 (각 Phase 후)

- [ ] **[V-P0]** P0 완료 후: 다음 기동 시 `[EntryGate]` 로그 확인, 09:30 이후 진입 신호 발생 확인, `[Sigma]` EOD 저장 로그 확인
- [ ] **[V-P0]** `[Bias] 1m FL=XX%` 로그에서 FL 35% 이하 확인 (이전 87~100% 대비)
- [ ] **[V-P1]** `meta_labels.threshold_move` 값이 sigma_at_t × K × √h 값과 일치하는지 확인
- [ ] **[V-P2]** ATR 제거 후 `[Threshold]` 로그 소멸 확인, HORIZON_THRESHOLDS 매분 rolling σ 기반 갱신 확인

---

## 기대 효과

| 항목 | 변경 전 | P0 완료 후 |
|---|---|---|
| 저변동성 날 FLAT | 46~67% | **29~37%** |
| FLAT std(일별) | 14.4%p | **3.2%p** |
| 5/19~5/29형 진입 0 재발 | 가능 | **방지** |
| 장 초반 비정상 진입 | 제한 없음 | 09:30 이후 정상화 |
| GBM 첫 재학습 전 | 전체 사이즈 | size×0.6 보수 진입 |
| ATR 동적 | 5~15% 발동 (거의 정적) | **매분 rolling σ 완전 대체** |

---

## 주의사항

1. **3m threshold**: 방법3 도입 후에도 현행 BASE(0.0006) 우선. Phase A 모니터에서 6~8주 추가 누적 후 재검토.
2. **k=0.41 재산출 시점**: Phase A FLAT ±6%p 경보 발생 시만. 시장 구조 변화(레짐 전환) 감지 없으면 유지.
3. **30m Qualification**: 10:30에야 달성. Phase 3 앙상블 필터링 구현 전까지 현행 유지(낮은 가중치 참여).
4. **P0-b 변경 시**: class_weight도 이미 재조정됨(90차). GBM 재학습 완료 후 `[Bias]` 로그로 FL 비율 변화 반드시 확인.
5. **방안B 미완료 구간**: P1 완료 전까지 verify는 현재 HORIZON_THRESHOLDS(매분 갱신된 rolling σ) 사용. 예측과 verify 시점의 sigma 차이는 1m 봉에서는 무시 가능, 30m는 최대 0.1% 오차.
