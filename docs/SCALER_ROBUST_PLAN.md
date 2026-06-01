# 스케일러 운영 강건화 계획

**작성일**: 2026-06-01  
**배경**: 2026-06-01 진입 0건 — 스케일러 65시간 노후화 → grade=X 지속 → CB③ 당일 정지  
**범위**: GBM 스케일러 운영 정책 + 피처별 Robust 전처리 도입

---

## 1. 진단 요약

| 시각 | 이벤트 | 원인 |
|---|---|---|
| 09:00 | ATR z=+5.04, avg_volume z=+4.22 | 스케일러 3919분(65h) 미갱신 |
| 09:00~09:55 | 전 분봉 grade=X | conf 60% 미달 — 스케일러 왜곡으로 예측 불량 |
| 09:55 | CB③ 당일 정지 | 30분 정확도 0.0% + 중간신뢰도 오류 7연속 2회 |
| 10:12 | spread_ticks z=+6.45 지속 | clip 없는 피처, 장중 변동성 급등 미보호 |

**근본 원인**: 장 시작 전 스케일러 워밍업 루틴 부재. 주말 포함 금요일 마감 이후 재적합 없이 월요일 장 진입.

---

## 2. 스케일러 운영 정책

### 2-1. 경로별 방침

| 경로 | 방침 | 이유 |
|---|---|---|
| **SGD** (OnlineLearner) | **현행 유지** — `partial_fit` 매 샘플 갱신 | 온라인 적응이 핵심 강점. RobustScaler는 partial_fit 미지원 |
| **GBM** (MultiHorizonModel) | **정책 변경** — 스케일러 단독 정기 refit | GBM은 스케일 불변(트리). 스케일러만 독립 refit 가능 |

### 2-2. GBM 스케일러 재적합 트리거 4종

```
[A] 장 시작 전 워밍업     08:55 고정 실행 (근본 원인 차단)
[B] 장초 단축 주기         09:00~09:30 → 15분마다
[C] 정기 주기              장중 60분마다
[D] 강제 트리거            극단 z-score 조건 충족 시 즉시
```

**트리거 D 상세 조건** (OR):
- 동일 피처에서 `|z| > EXTREME_ZSCORE_THRESHOLD` 연속 **3분** 발생
- 같은 피처명이 극단 z-score top에 **2분 이내 2회** 반복

**쿨다운**: 강제 refit 후 5분간 재트리거 억제

### 2-3. 워밍업 refit 데이터 전략

장초 데이터 부족 문제를 방지하기 위해 **전일 tail + 당일 누적** 혼합:

```
08:55 워밍업   → 최근 SCALER_WARMUP_LOOKBACK_BARS 봉 (전일 포함)
15분 단축 refit → 전일 tail 200봉 + 당일 누적봉 혼합
60분 정기 refit → 당일 누적봉 (충분히 쌓인 이후)
```

---

## 3. Config 추가 상수

`config/settings.py` 에 추가:

```python
# ── 스케일러 운영 정책 ──────────────────────────────────────────
# GBM은 트리 기반(스케일 불변) → 스케일러만 독립 refit, 모델 재학습과 분리
# SGD 경로는 partial_fit 현행 유지

# [A] 장 시작 전 워밍업 (08:55)
SCALER_WARMUP_LOOKBACK_BARS: int = 500       # 최근 500봉 (~2거래일)

# [B] 장초 단축 주기
SCALER_OPEN_REFRESH_INTERVAL_MIN: int = 15   # 09:00~09:30 구간
SCALER_OPEN_END_MINUTE: int = 30             # 이후 기본 주기로 복귀

# [C] 정기 주기
SCALER_GBM_REFRESH_INTERVAL_MIN: int = 60   # 장중 60분마다

# [D] 강제 트리거
SCALER_FORCE_EXTREME_CONSEC: int = 3         # 동일 피처 극단 z 연속 N분
SCALER_FORCE_FEATURE_REPEAT: int = 2         # 같은 피처 N회 반복 시
SCALER_FORCE_REFRESH_COOLDOWN_MIN: int = 5   # refit 후 최소 대기

# [경고 임계] 현행값 클래스 상수 → settings 이전
SCALER_WARN_MINUTES: int = 90                # multi_horizon_model.SCALER_WARN_MINUTES 대체
```

---

## 4. Robust 전처리 도입

### 4-1. 적용 원칙

- **적용 범위**: GBM `predict()` 직전 입력 전처리만. 피처 생성 로직(CVD/OFI/VWAP 등) 일체 변경 금지
- **SGD 경로 미적용**: partial_fit 온라인 구조 유지
- **재학습 일관성**: GBM 배치 재학습 시에도 동일 전처리 적용 필수

### 4-2. 피처별 우선순위

#### 1순위 — clip/log1p 없음, 오늘 실제 폭발 확인

| 피처 | 오늘 극단값 | 현재 보호 | 권장 처리 |
|---|---|---|---|
| `atr` | z=+5.04 (09:00) | 없음 | `log1p(x)` → StandardScaler |
| `avg_volume` | z=+4.22 (09:00) | 없음 | `log1p(x)` → StandardScaler |
| `spread_ticks` | z=+6.45 (10:12, 지속) | **없음** | `clip(0, 20.0)` → StandardScaler |
| `mlofi_slope` | 분포 -722 ~ +1127 | 없음 | `clip(-500, 500)` → StandardScaler |

#### 2순위 — clip 있으나 스케일러 노후화 시 간접 영향

| 피처 | 현재 보호 | 비고 |
|---|---|---|
| `ofi_norm` | `clip(-3, 3)` | 스케일러 워밍업 [A] 우선 적용 후 재평가 |
| `mlofi_norm` | `clip(-3, 3)` | 동일 |
| `ofi_imbalance` | `clip(-3, 3)` 간접 | 동일 |

#### 유지 권장 — 이미 보호됨

| 피처 | 이유 |
|---|---|
| `cancel_add_ratio` | tick 단위에서 `_stable_cancel_add_ratio` (log1p + clip(-3,3)) 이미 적용 중 |
| `toxicity_*` | 대부분 0~1 bounded |
| `quality_*`, `macro_*` 플래그 | bounded 또는 코드상 상한 처리 중 |

> **cancel_add_ratio DB 이상치**: 과거 raw DB에 749M 이상치가 남아있는 건 구버전 데이터 문제. 현재 코드 버그가 아니며 학습 데이터 클린업으로 별도 처리.

### 4-3. 전처리 상수 (settings.py 추가)

```python
# ── Robust 전처리 — GBM 입력 직전 적용 (SGD 경로 미적용) ─────────
# 재학습 시에도 반드시 동일 전처리 통과

# log1p 적용 피처 (양수값 long-tail 분포)
SCALER_LOG1P_FEATURES: tuple = ("atr", "avg_volume")

# clip 상한/하한 피처 {피처명: (하한, 상한)}
SCALER_CLIP_FEATURES: dict = {
    "spread_ticks": (0.0, 20.0),    # 틱 단위 스프레드 상한 cap
    "mlofi_slope":  (-500.0, 500.0), # slope 범위 제한
}
```

### 4-4. 구현 위치

```
model/multi_horizon_model.py
  └── predict() → scaler.transform() 직전
        └── _preprocess_robust(x2d) 추가
              ├── log1p 피처 인덱스 조회 → 변환
              └── clip 피처 인덱스 조회 → clip
```

---

## 5. 구현 TODO

### Phase A — 스케일러 워밍업 (최우선, 오늘 문제 직접 차단) ✅ 2026-06-01 구현

- [x] `config/settings.py` — `SCALER_WARMUP_LOOKBACK_BARS=500`, `SCALER_WARN_MINUTES=90` 추가
- [x] `model/multi_horizon_model.py` — `refit_scalers_only(X, feature_names)` 구현
  - 호라이즌별 `StandardScaler().fit(X)` → pkl 저장 → `_scaler_fitted_at` 갱신
  - GBM 모델 불변 (트리 스케일 불변성 활용)
- [x] `learning/batch_retrainer.py` — `load_features_for_warmup(lookback_bars)` 구현
  - `raw_data.db` 최근 N봉 X 행렬 로드 (라벨 계산 없음)
  - managed feature set 적용 (shap_feature_registry 참조)
- [x] `main.py` — `pre_market_setup()` 에서 `_scaler_warmup_worker` daemon thread 시작
  - GBM PreRetrain 예약(`_warmup_retrain_pending=True`) 시 스킵 (재학습이 스케일러 포함)
  - 로그 태그: `[ScalerWarmup]`
- [ ] 검증: 다음 장 08:55 SYSTEM 로그에서 `[ScalerWarmup] 완료` 확인
  - `canary_stale_age_hours()` < 1h 이어야 함

### Phase B — 정기 + 강제 refresh 로직

- [ ] `model/multi_horizon_model.py` — `refresh_scalers_if_needed(bar_count, recent_bars)` 구현
  - 장초 구간 판단 (`SCALER_OPEN_END_MINUTE`)
  - 구간별 주기 비교 (15분 or 60분)
  - 강제 트리거 조건 검사 (`SCALER_FORCE_EXTREME_CONSEC`, `SCALER_FORCE_FEATURE_REPEAT`)
  - 쿨다운 체크 (`SCALER_FORCE_REFRESH_COOLDOWN_MIN`)
- [ ] 매분 파이프라인 STEP 5 (`predict`) 직전 또는 STEP 4 직후 호출
- [ ] WARN 로그: refresh 사유·경과 시간 기록

### Phase C — Robust 전처리 (1순위 피처) ✅ 2026-06-01 구현

- [x] `config/settings.py` — `SCALER_LOG1P_FEATURES=("atr","avg_volume")`, `SCALER_CLIP_FEATURES={"spread_ticks":(0,20),"mlofi_slope":(-500,500)}` 추가
- [x] `model/multi_horizon_model.py` — 모듈 수준 함수 `apply_robust_preprocess(X, feature_names)` 구현
  - 피처명 → 인덱스 dict 매핑, 복사본 반환 (원본 불변)
  - log1p: `np.log1p(max(x, 0))` — 음수 방어 포함
  - clip: `np.clip(x, lo, hi)`
- [x] `predict_proba()` — `scaler.transform()` 직전 `x2d_proc` 생성 후 전달
- [x] `fit()` — 학습 X에도 동일 전처리 적용 (`X_proc`)
- [x] `refit_scalers_only()` — 워밍업 X에도 동일 전처리 적용 (`X_proc`)
- [x] `learning/batch_retrainer.py` — `retrain_now()` 데이터 로드 직후 `apply_robust_preprocess(X, feature_names)` 호출
  - **학습·예측·워밍업 3경로 모두 동일 전처리 통과 — 일관성 보장**

### Phase D — cancel_add_ratio DB 클린업 (독립 작업)

- [ ] DB `features` 테이블에서 `cancel_add_ratio` 이상치 조회
  - `SELECT COUNT(*) WHERE ABS(cancel_add_ratio) > 10` 확인
- [ ] 구버전 raw 데이터 행 삭제 또는 재계산 (current `_stable_cancel_add_ratio` 기준)
- [ ] `MIN_TRAIN_BARS` 복원(5000) 후 재학습 시 오염 여부 확인

### Phase E — 2순위 피처 재평가 (Phase A 완료 후)

- [ ] Phase A 운영 1주 후 `ofi_norm`, `mlofi_norm`, `ofi_imbalance` 극단 z 발생 빈도 재측정
- [ ] 스케일러 워밍업 후에도 빈번하면 clip 보강 검토
- [ ] `SCALER_WARN_MINUTES` 상수를 클래스 내부에서 `settings.py`로 이전

---

## 6. 우선순위 요약

```
[즉시] Phase A  — 08:55 워밍업: 오늘 문제 원천 차단
[즉시] Phase C  — 1순위 Robust: spread_ticks·atr·avg_volume·mlofi_slope clip/log1p
[다음] Phase B  — 정기/강제 refresh: 워밍업 실패 시 자동 복구 레이어
[병행] Phase D  — DB 클린업: 학습 데이터 오염 방지
[추후] Phase E  — 2순위 재평가: 실데이터 관찰 후 결정
```

---

## 7. 제약 사항

- `features/technical/ofi.py`, `cvd.py`, `vwap.py` — **피처 계산 로직 변경 금지** (CORE 3종)
- 전처리 변환은 반드시 GBM 학습·예측 양쪽에 동일하게 적용 (단방향 적용 시 분포 불일치)
- SGD 경로(`learning/online_learner.py`) — **이 계획 적용 외**

---

## 8. 스케일러 상태 로그 / DB 설계

### 8-1. DB 파일

```
data/db/scaler_monitor.db
```

기존 패턴(`threshold_monitor.db` 등)과 동일하게 `DB_DIR` 하위에 독립 파일로 관리.

### 8-2. 테이블 스키마

#### `scaler_events` — 분봉 단위 실시간 이벤트

```sql
CREATE TABLE IF NOT EXISTS scaler_events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT NOT NULL,          -- 'YYYY-MM-DD HH:MM:SS' (분봉 시각)
    date          TEXT NOT NULL,          -- 'YYYY-MM-DD' (일별 집계 키)
    horizon       TEXT NOT NULL,          -- '1m','3m','5m','10m','15m','30m'
    fitted_at     TEXT,                   -- 스케일러 마지막 재적합 시각
    age_minutes   REAL,                   -- fitted_at 기준 경과 분
    max_z         REAL,                   -- 해당 분봉 최대 |z-score|
    max_z_feature TEXT,                   -- max_z를 기록한 피처명
    extreme_count INTEGER DEFAULT 0,      -- |z| > EXTREME_ZSCORE_THRESHOLD 피처 수
    refresh_type  TEXT,                   -- NULL or 'A_WARMUP','B_OPEN','C_PERIODIC','D_FORCE'
    refresh_reason TEXT                   -- 강제 트리거 시 사유 (피처명·연속횟수 등)
);
CREATE INDEX IF NOT EXISTS idx_se_date ON scaler_events(date, ts);
```

#### `scaler_daily` — 일별 집계 (장마감 후 EOD 기록)

```sql
CREATE TABLE IF NOT EXISTS scaler_daily (
    date              TEXT PRIMARY KEY,   -- 'YYYY-MM-DD'
    max_age_minutes   REAL,               -- 당일 최대 스케일러 노후 시간(분)
    total_extreme     INTEGER,            -- 당일 누적 extreme z 발생 건수
    top_extreme_feat  TEXT,               -- 가장 많이 폭발한 피처명
    refresh_count     INTEGER,            -- 당일 refresh 발생 횟수
    refresh_types     TEXT,               -- JSON 배열 ['A_WARMUP','D_FORCE',...]
    grade_x_minutes   INTEGER,            -- grade=X 지속 분 수
    cb3_triggered     INTEGER DEFAULT 0,  -- CB③ 당일 정지 여부 (0/1)
    note              TEXT                -- 수동 메모
);
```

### 8-3. 기록 위치 및 타이밍

| 기록 주체 | 위치 | 타이밍 |
|---|---|---|
| 분봉 이벤트 INSERT | `model/multi_horizon_model.py` — `predict()` 내부 | 매분 예측 직후 |
| refresh 이벤트 UPDATE | `model/multi_horizon_model.py` — `refresh_scalers_if_needed()` | refresh 직후 해당 분봉 행 갱신 |
| 일별 집계 INSERT | `main.py` — `daily_close()` | 15:40 EOD 루틴 |

### 8-4. SIGNAL 로그 강화

기존 WARNING 수준 로그에 구조화 필드를 추가해 grep 가능하게:

```
[ScalerMonitor] ts=09:00 horizon=1m age=3919m max_z=+5.04(atr) extreme=1 refresh=None
[ScalerRefresh] ts=08:55 trigger=A_WARMUP lookback=500 elapsed=0.82s
[ScalerRefresh] ts=09:18 trigger=D_FORCE feat=atr consec=3 elapsed=0.14s
```

---

## 9. ScalerMonitorPanel UI 설계

### 9-1. 파일 위치 및 구조

```
dashboard/panels/scaler_monitor_panel.py   ← 신규
```

기존 `threshold_monitor_panel.py`와 동일한 패턴:
- 독립 파일, `scaler_monitor.db` 직접 조회
- `QTimer` 60초 주기 자동 갱신 (실시간 뷰)
- 다크 팔레트 `_COL` 공통 적용

`main_dashboard.py` 통합: 기존 탭 목록에 **"스케일러"** 탭 추가.

### 9-2. 레이아웃

```
┌─────────────────────────────────────────────────────────────┐
│  스케일러 상태 모니터                          갱신: 14:23:01 │
├──────────────────────────┬──────────────────────────────────┤
│  [실시간 — 호라이즌별]    │  [오늘 누적 extreme 피처 Top5]   │
│                           │                                  │
│  horizon │ 노후(분) │ 상태 │  피처명         │ count │ max_z  │
│  1m      │   12    │  ●  │  spread_ticks   │  43   │ +6.45  │
│  3m      │   12    │  ●  │  atr            │  31   │ +5.04  │
│  5m      │   12    │  ●  │  avg_volume     │  18   │ +4.22  │
│  10m     │   12    │  ●  │  mlofi_slope    │   7   │ +3.91  │
│  15m     │   12    │  ●  │  ofi_norm       │   3   │ +4.10  │
│  30m     │   12    │  ●  │                 │       │        │
│           │          │    ├──────────────────────────────────┤
│  마지막refresh: 08:55    │  [오늘 refresh 이벤트]           │
│  트리거: A_WARMUP        │                                  │
│                           │  08:55 A_WARMUP  lookback=500   │
│                           │  09:18 D_FORCE   feat=atr×3회   │
│                           │  10:15 C_PERIODIC 60min         │
├──────────────────────────┴──────────────────────────────────┤
│  [일별 이력 — 최근 20거래일]                                  │
│                                                             │
│  날짜   │ 최대노후(분) │ extreme건 │ 폭발피처  │ refresh수 │CB③│
│  06-01  │    3919    │    287   │ spread_t  │     3     │ ✗ │
│  05-29  │     62     │     14   │ atr       │     8     │   │
│  05-28  │     58     │      9   │ atr       │     9     │   │
└─────────────────────────────────────────────────────────────┘
```

### 9-3. 상태 색상 규칙

| 조건 | 색상 | 의미 |
|---|---|---|
| 노후 < 30분 | `#3fb950` (초록) | 정상 |
| 노후 30~90분 | `#e3b341` (노랑) | 주의 |
| 노후 > 90분 | `#f85149` (빨강) | 경보 (`SCALER_WARN_MINUTES` 초과) |
| extreme_count > 0 | `#d29922` (주황) 강조 | 극단 z 발생 중 |
| refresh_type = D_FORCE | `#58a6ff` (파랑) 굵게 | 강제 트리거 발생 |
| CB③ 당일 정지 | `#f85149` 셀 배경 | 과거 이력 경보 |

### 9-4. 구현 TODO

#### DB / 수집 레이어

- [ ] `data/db/scaler_monitor.db` 스키마 초기화 함수 구현
  - `model/multi_horizon_model.py` 또는 `utils/db_utils.py` 에 `init_scaler_monitor_db()` 추가
- [ ] `predict()` 내부: 매분 호라이즌별 `scaler_events` INSERT
  - `fitted_at`, `age_minutes`, `max_z`, `max_z_feature`, `extreme_count` 기록
- [ ] `refresh_scalers_if_needed()`: refresh 발생 시 해당 행 `refresh_type`, `refresh_reason` UPDATE
- [ ] `daily_close()`: EOD `scaler_daily` 집계 INSERT
  - 당일 `scaler_events` 집계: max_age, total_extreme, top_feat, refresh_count, refresh_types, grade_x_minutes

#### 패널 구현

- [ ] `dashboard/panels/scaler_monitor_panel.py` 신규 생성
  - `ScalerMonitorPanel(QWidget)` 클래스
  - 실시간 섹션: 호라이즌별 노후 테이블 + 색상 규칙 적용
  - 누적 섹션: 오늘 extreme 피처 Top5 테이블
  - refresh 이벤트 리스트 (스크롤 가능)
  - 일별 이력 테이블 (최근 20거래일)
  - `QTimer` 60초 자동 갱신

- [ ] `main_dashboard.py` 통합
  - `ScalerMonitorPanel` import 추가
  - 탭 위젯에 **"스케일러"** 탭 삽입

#### 연동 검증

- [ ] 장 중 `predict()` 호출 시 DB 기록 확인 (`_check_db.py` 활용)
- [ ] 강제 트리거 발생 시 refresh_type 컬럼 정상 기록 확인
- [ ] 패널 열었을 때 오늘 데이터 즉시 표시 확인
- [ ] 일별 이력 20행 이상 누적 후 스크롤 동작 확인
