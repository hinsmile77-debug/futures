# 미륵이2 (일반선물 전용) 마이그레이션 계획

> 작성일: 2026-06-24  
> 배경: 235차 TICK_SIZE 버그 수정 및 종목 전환 안전성 분석 결과

---

## 1. 결정 사항

### 미륵이 운영 원칙 (확정)

| 인스턴스 | 종목 | 상태 |
|---|---|---|
| **미륵이** | KOSPI200 미니선물 (`A05xxxx`) 전용 | 현재 운영 중 |
| **미륵이2** | KOSPI200 일반선물 (`A01xxxx`) 전용 | 신규 구축 예정 |

**결정 근거**

- 현재 미륵이는 8개월+ 미니선물 데이터로 GBM·SGD 학습 완료
- 스케일러(StandardScaler)가 미니선물 피처 분포로 fit됨
- CORE 피처(OFI·CVD·spread_ticks)가 미니선물 틱 특성 기준으로 캘리브레이션됨
- 미니선물(0.02pt) vs 일반선물(0.05pt) 틱 사이즈 차이 → 혼재 시 spread_ticks 2.5배 왜곡
- raw_candles DB에 종목코드 없어 혼재 시 GBM 학습 데이터 오염

### 아키텍처 결정: 코드 분기(Fork) 금지 — 설정 주도 단일 코드베이스

코드를 복사해 미륵이2를 만들면 버그 수정·개선이 양쪽에 중복 적용돼야 해서 유지보수 비용이 2배가 된다.  
**코드는 동일, 설정(secrets.py)과 DB 경로만 다른 두 인스턴스로 운영한다.**

```
미륵이   ─── 동일 코드베이스 ───  미륵이2
  │                                  │
FUTURES_CODE=A0567             FUTURES_CODE=A0169
RAW_DATA_DB=raw_A0567.db       RAW_DATA_DB=raw_A0169.db
PC-A / Cybos계정-A              PC-B / Cybos계정-B
```

---

## 2. 현재 상태 분석 (미그레이션 전 체크)

### 종목코드 의존 버그 (235차에서 수정 완료)

| 항목 | 상태 |
|---|---|
| `TICK_SIZE` 하드코딩 (0.05) | **수정 완료** — `feature_builder.set_tick_size()` 동적 주입 |
| `spread_ticks` 미니선물 2.5배 과소계산 | **수정 완료** |
| 재시작 배지 + 포지션FLAT 조건 확인 | **구현 완료** (234차) |

### raw_candles DB 현황 (마이그레이션 필요)

```sql
-- 현재 스키마 (code 컬럼 없음)
CREATE TABLE raw_candles (
    ts         TEXT PRIMARY KEY,
    open, high, low, close, volume,
    bid1, ask1, oi, buy_vol, sell_vol
)
-- raw_features, raw_features_horizon 도 동일하게 code 없음
```

현재 DB에는 미니선물 데이터가 모두 code 구분 없이 저장돼 있음.

---

## 3. 마이그레이션 구현 계획

### Phase A — 설정 파라미터화 (미륵이 단독, 미륵이2 준비 전)

**목표**: 종목코드를 코드에 하드코딩하지 않고 `secrets.py` 하나로 제어

#### A-1. `config/secrets.py`에 `FUTURES_CODE` 추가

```python
# 미니선물 인스턴스
FUTURES_CODE = "A0567"   # 기동 시 이 코드로 _resolve_trade_code 검증

# 일반선물 인스턴스 (미륵이2)
# FUTURES_CODE = "A0169"
```

#### A-2. `config/settings.py` — DB 경로 파라미터화

```python
from config import secrets as _sec

_CODE = getattr(_sec, "FUTURES_CODE", "")
_CODE_SUFFIX = _CODE if _CODE else "default"

RAW_DATA_DB  = os.path.join(DATA_DIR, f"raw_{_CODE_SUFFIX}.db")
TRADES_DB    = os.path.join(DATA_DIR, f"trades_{_CODE_SUFFIX}.db")
LOG_DIR      = os.path.join(BASE_DIR, f"logs_{_CODE_SUFFIX}")
HORIZON_DIR  = os.path.join(MODEL_DIR, f"horizons_{_CODE_SUFFIX}")
SCALER_DIR   = os.path.join(MODEL_DIR, f"scaler_{_CODE_SUFFIX}")
```

> **현재 미륵이**: `FUTURES_CODE=A0567` → 기존 파일명과 동일 (`raw_A0567.db`)  
> 기존 DB 파일을 `raw_A0567.db`로 rename하면 무중단 전환 가능.

#### A-3. `_resolve_trade_code()` — FUTURES_CODE 검증 추가

```python
# strategy/runtime/broker_runtime_service.py
from config import secrets as _sec
_allowed = getattr(_sec, "FUTURES_CODE", "")
if _allowed and code != _allowed:
    logger.critical(
        "[CodeGuard] 프로브 종목(%s)이 허용 종목(%s)과 불일치 — 기동 중단",
        code, _allowed,
    )
    return None   # connect_broker 실패 처리
```

이렇게 하면 실수로 잘못된 종목 설정 시 기동 자체가 차단된다.

---

### Phase B — raw_candles 스키마 마이그레이션

**목표**: 테이블에 `code` 컬럼 추가 → 종목별 쿼리 분리

#### B-1. 스키마 변경 (마이그레이션 스크립트)

```sql
-- raw_candles
ALTER TABLE raw_candles ADD COLUMN code TEXT DEFAULT '';
UPDATE raw_candles SET code = 'A0567' WHERE code = '' OR code IS NULL;
CREATE INDEX IF NOT EXISTS idx_rc_code ON raw_candles(code, ts);

-- raw_features
ALTER TABLE raw_features ADD COLUMN code TEXT DEFAULT '';
UPDATE raw_features SET code = 'A0567' WHERE code = '' OR code IS NULL;

-- raw_features_horizon
ALTER TABLE raw_features_horizon ADD COLUMN code TEXT DEFAULT '';
UPDATE raw_features_horizon SET code = 'A0567' WHERE code = '' OR code IS NULL;
-- PK 재설계: (code, ts, horizon) — SQLite는 PK 변경 불가, 테이블 재생성 필요
CREATE TABLE raw_features_horizon_new (
    code     TEXT NOT NULL DEFAULT '',
    ts       TEXT NOT NULL,
    horizon  TEXT NOT NULL,
    features TEXT NOT NULL,
    PRIMARY KEY (code, ts, horizon)
);
INSERT INTO raw_features_horizon_new SELECT 'A0567', ts, horizon, features FROM raw_features_horizon;
DROP TABLE raw_features_horizon;
ALTER TABLE raw_features_horizon_new RENAME TO raw_features_horizon;
CREATE INDEX IF NOT EXISTS idx_rfh_code_horizon ON raw_features_horizon(code, horizon, ts);
```

#### B-2. `utils/db_utils.py` 수정

- `save_candle(candle, code)` — `code` 파라미터 추가
- `save_features(ts, features, code)` — `code` 파라미터 추가
- 학습 데이터 로드 쿼리: `WHERE code = ?`

#### B-3. `learning/batch_retrainer.py` 수정

```python
# load_features_for_warmup, _load_training_data 등
cursor.execute(
    "SELECT ... FROM raw_candles WHERE code = ? AND ts >= ? ORDER BY ts",
    (self._futures_code, cutoff_ts),
)
```

#### B-4. 영향 받는 쿼리 위치 목록

| 파일 | 위치 | 변경 내용 |
|---|---|---|
| `utils/db_utils.py` | `save_candle()` | `code` 파라미터 추가 |
| `utils/db_utils.py` | `save_features()` | `code` 파라미터 추가 |
| `utils/db_utils.py` | `fetch_recent_raw_candles()` | `WHERE code=?` 추가 |
| `learning/batch_retrainer.py` | `_load_training_data()` | `WHERE code=?` 추가 |
| `learning/batch_retrainer.py` | `load_features_for_warmup()` | `WHERE code=?` 추가 |
| `learning/batch_retrainer.py` | `prune_raw_data_db()` | `WHERE code=?` 추가 |
| `dashboard/main_dashboard.py` | 차트 캔들 쿼리 | `WHERE code=?` 추가 |
| `main.py` | `daily_close()` 내 종가 버퍼 쿼리 | `WHERE code=?` 추가 |

---

### Phase C — 미륵이2 인스턴스 구축

**목표**: 일반선물 전용 미륵이2를 별도 환경에서 기동

#### C-1. 인스턴스 구분 설정

```python
# 미륵이2 전용 config/secrets.py
FUTURES_CODE = "A0169"   # 현재 KOSPI200 일반선물 근월물 (분기별 교체)
ACCOUNT_NO   = "333042073"  # 별도 계정 또는 동일 계정 다른 계약
```

#### C-2. 초기 데이터 수집 기간

- 미륵이2 최초 기동 → 일반선물 데이터 수집 시작
- GBM 첫 재학습: 최소 500봉 (약 8시간 장 운영) 후
- SGD 안정화: 약 1~2주
- Walk-Forward 검증: 4~6주 후 모의투자 결과 평가

#### C-3. 모델 초기화 방침

- **GBM**: 미니선물 학습 모델 재사용 불가 → 빈 상태에서 시작
- **SGD**: 리셋 후 일반선물 온라인 학습 시작
- **스케일러**: 일반선물 첫 WarmupRetrain에서 초기 fit

---

## 4. TODO 리스트

### Phase A — 설정 파라미터화

- [ ] **A-1** `config/secrets.py`에 `FUTURES_CODE = "A0567"` 추가 (명시적 고정)
- [ ] **A-2** `config/settings.py` DB/LOG/MODEL 경로를 `FUTURES_CODE` 기반 자동 파생으로 변경
- [ ] **A-3** 기존 DB 파일을 `raw_A0567.db` 등으로 rename (무중단 전환)
- [ ] **A-4** `_resolve_trade_code()` — `FUTURES_CODE` 불일치 시 기동 중단 로직 추가
- [ ] **A-5** UI `cmb_market` / `cmb_symbol`에서 `FUTURES_CODE` 이외 종목 선택 시 경고 표시

### Phase B — DB 스키마 마이그레이션

- [ ] **B-1** `utils/db_utils.py` `init_db()`: `raw_candles` / `raw_features` `code` 컬럼 추가 마이그레이션
- [ ] **B-2** `raw_features_horizon` 테이블 재생성 (PK에 `code` 포함)
- [ ] **B-3** 기존 데이터 backfill: `UPDATE ... SET code = 'A0567'`
- [ ] **B-4** `save_candle()` / `save_features()` — `code` 파라미터 추가
- [ ] **B-5** `batch_retrainer._load_training_data()` — `WHERE code=?` 추가
- [ ] **B-6** `batch_retrainer.load_features_for_warmup()` — `WHERE code=?` 추가
- [ ] **B-7** `batch_retrainer.prune_raw_data_db()` — `WHERE code=?` 추가
- [ ] **B-8** `dashboard` 차트 캔들 쿼리 — `WHERE code=?` 추가
- [ ] **B-9** `daily_close()` 종가 버퍼 쿼리 — `WHERE code=?` 추가
- [ ] **B-10** `retrain_eod.py` 학습 데이터 쿼리 — `WHERE code=?` 추가
- [ ] **B-11** 마이그레이션 스크립트 작성 (EOD 후 1회 실행용 `scripts/migrate_add_code_col.py`)
- [ ] **B-12** 마이그레이션 후 회귀 테스트 (봉 수 동일 여부, 피처 로드 정상 여부 확인)

### Phase C — 미륵이2 구축

- [ ] **C-1** 별도 PC 또는 별도 Cybos 계정 환경 준비
- [ ] **C-2** `config/secrets.py`에 `FUTURES_CODE = "A0169"` 설정
- [ ] **C-3** 빈 DB로 최초 기동 → 일반선물 데이터 수집 시작
- [ ] **C-4** 500봉 이상 누적 후 GBM 첫 재학습 완료 확인
- [ ] **C-5** 모의투자 4주 통산 수익률 양수 → Phase 5 진입 조건 달성 확인
- [ ] **C-6** 미륵이(미니선물) Walk-Forward 기준 동일하게 검증

---

## 5. 실행 우선순위 및 시점

| 단계 | 선행 조건 | 권장 시점 |
|---|---|---|
| Phase A | 없음 | 미륵이 Phase 5 진입 직전 |
| Phase B | Phase A 완료 | Phase A 완료 후 장 마감 시 1회 실행 |
| Phase C | Phase B 완료 + 별도 환경 준비 | Phase 5 실전 전환 안정화 후 |

---

## 6. 주의사항

1. **Phase B 실행은 반드시 장 마감 후(15:10 이후)** — 운영 중 스키마 변경 절대 금지
2. **backfill 전 DB 백업 필수** — 마이그레이션 실패 시 복구용
3. **미륵이2는 미륵이와 동시 실행 금지** — 동일 PC에서 동일 Cybos 계정으로 두 인스턴스 실행 시 COM 경합
4. **일반선물 모델이 안정화되기 전(최소 4주) 실투자 금지** — CORE 피처 캘리브레이션 미완료 상태
5. **롤오버 주기 차이 주의** — 미니선물(월물) vs 일반선물(분기물) 만기 주기 다름, `_resolve_trade_code()` 롤오버 감지 동작 확인 필요

---

*이 문서는 2026-06-24 장중 미륵이 로그 분석 및 종목 전환 안전성 딥다이브 논의를 바탕으로 작성됨.*
