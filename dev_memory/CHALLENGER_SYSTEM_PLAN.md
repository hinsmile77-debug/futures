# 도전자 시스템 설계 & 추세전환 고도화 방안
**작성일**: 2026-05-12  
**최종 업데이트**: 2026-05-12 (구현 완료 반영)  
**상태**: ✅ Phase C-1 ~ C-8 + 레짐 전문가 확장 전면 구현 완료

---

## PART 1. 추세전환 분기점 분석

### 1-1. 분석 대상 차트 패턴

2026-05-12 기준 실차트에서 확인된 추세전환 분기점:

| 시각 | 패턴 유형 | 가격 움직임 | 비고 |
|------|-----------|-------------|------|
| 10:39~10:40 | 하락 탈진 후 반전 | 연속 음봉 → 첫 반등 | V자 반전 시작 |
| 10:49~10:50 | 2차 지지 확인 | 소폭 재하락 → 반등 유지 | 이중 바닥 확인 |
| 10:58~10:59 | 추세 전환 확정 | 연속 양봉 전환 | 매수 추세 본격화 |

**공통 패턴 (상위 1% 트레이더 해석)**:
```
하락 탈진(Exhaustion) → 대량 지정가 흡수(Absorption) → OFI 급반전 → 가격 반전
```

---

### 1-2. 현재 미륵이의 진입 불가 이유

| 기존 조건 | 분기점에서의 실제 동작 | 결과 |
|----------|----------------------|------|
| Hurst H < 0.45 → 진입 차단 `-0.99` | 급락 직후 H 필연적 하락 | **진입 완전 차단** |
| 체크리스트 #3 VWAP 위치 | 급락 후 가격이 VWAP 아래 | **매수 조건 불충족** |
| 체크리스트 #7 직전 봉 방향 일치 | 반전 직전 음봉 연속 | **매수 체크리스트 실패** |
| 체크리스트 #4 CVD 방향 일치 | 10분 윈도우 CVD 여전히 음수 | **지연 감지 (5~8분 후행)** |
| ADX > 25 → 추세 모드 | 하락 추세 강하다고 판단 | **역방향 신호 강화** |

**핵심 구조 문제**: 현재 시스템은 추세 추종(Trend-Following)에 최적화되어 있어,  
추세 전환 시점에서 오히려 기존 방향으로 진입하거나 진입 자체를 차단함.

---

## PART 2. 상위 1% 트레이더 관점 — 고도화 방안 5종

### 방안 A — CVD 탈진 감지 (CVD Exhaustion)
✅ **구현 완료**: `features/technical/cvd_exhaustion.py`, `challenger/variants/cvd_exhaustion.py`

**포착 원리**: CVD가 신저점을 갱신하되, 낙폭 속도가 급감하는 순간 = 매도 에너지 소진

```
탈진 조건 (3가지 동시 충족):
  ① cvd < cvd_20min_low           (CVD 20분 신저점 갱신)
  ② cvd_accel > 0                 (CVD 2차 미분 양전환 = 낙폭 둔화)
  ③ volume > avg_vol × 1.8        (거래량 급증 = 매도 클라이맥스)
```

---

### 방안 B — OFI 반전 속도 감지 (OFI Reversal Speed)
✅ **구현 완료**: `features/technical/ofi_reversal.py`, `challenger/variants/ofi_reversal.py`

**포착 원리**: OFI 부호 전환만 보는 기존 방식 → 전환 속도(가속도)로 신호 선행화

---

### 방안 C — VWAP 밴드 반전 모드 (VWAP Reversal Mode)
✅ **구현 완료**: `strategy/entry/checklist.py`, `challenger/variants/vwap_reversal.py`

**실제 구현 내용**:
```python
if vwap_position < -1.5 and cvd_exhaustion > 0.0:
    checks["3_vwap"] = True
    entry_mode = "MEAN_REVERSION"
```

---

### 방안 D — 탈진 레짐 추가 (Exhaustion Regime)
✅ **구현 완료**: `collection/macro/micro_regime.py`, `challenger/variants/exhaustion_regime.py`

**실제 구현 상수**: `REGIME_EXHAUSTION = "탈진"` (한글)

발동 조건 (4가지 동시):
```python
exhaustion_conds = (
    atr_ratio >= 1.5          # 변동성 확대
    and cvd_exhaustion > 0    # CVD 탈진
    and abs(ofi_reversal_speed) > 0   # OFI 급반전
    and abs(vwap_position) >= 1.5     # VWAP 밴드 이탈
)
```

---

### 방안 E — 호가 흡수 감지 (Order Absorption Detection)
✅ **구현 완료**: `challenger/variants/absorption.py`

**주의**: Cybos `FutureJpBid` 구독이 선행되어야 실신호 발동.  
미연결 시 `_hoga_active=False` → `direction=0` (관망) 반환.

---

## PART 3. 챔피언-도전자 시스템 설계

### 3-1. 전체 개념
✅ **구현 완료** — 원안에서 **레짐 전문가 시스템**이 추가 설계·구현됨.

```
                  ┌─────────────────────────────────┐
                  │         매분 파이프라인           │
                  │   (TradingSystem.run())          │
                  └──────────┬──────────────────────┘
                             │ STEP 4 피처 빌드 후
                  ┌──────────▼──────────────────────┐
                  │  [§20] RegimeChampGate           │
                  │  챔피언=None 레짐 → 진입 차단     │
                  └──────────┬──────────────────────┘
                             │ STEP 9 이후
                  ┌──────────▼──────────────────────┐
                  │       ChallengerEngine           │
                  │  (Shadow 실행, 실제 주문 없음)    │
                  └──┬──────┬──────┬──────┬──────┬──┘
                     │      │      │      │      │
                   [A]    [B]    [C]    [D]    [E]
                   CVD   OFI   VWAP  탈진   흡수
                   탈진  반전   반전  레짐   감지
                     │      │      │      │      │
                  ┌──▴──────▴──────▴──────▴──────▴──┐
                  │      challenger.db (SQLite)      │
                  │  signals · trades               │
                  │  daily_metrics · regime_metrics │
                  │  regime_rank_history            │
                  │  champion_history               │
                  └──────────────┬──────────────────┘
                                 │ 일별 마감 (15:40)
                  ┌──────────────▼──────────────────┐
                  │  레짐별 순위 계산 + WARNING 발송  │
                  │  (1위 변경 → 대시보드 경보 탭)    │
                  └─────────────────────────────────┘
```

---

### 3-2. 파일 구조 (실제 구현 기준)

```
futures/
├── challenger/
│   ├── __init__.py                  ✅
│   ├── challenger_engine.py         ✅  Shadow 실행 + 레짐 순위 감지 + WARNING
│   ├── challenger_db.py             ✅  SQLite CRUD (6개 테이블)
│   ├── challenger_registry.py       ✅  REGIME_POOLS + 챔피언 포인터
│   ├── promotion_manager.py         ✅  전역 + 레짐 전문가 승격
│   └── variants/
│       ├── __init__.py              ✅
│       ├── base_challenger.py       ✅
│       ├── cvd_exhaustion.py        ✅  방안 A
│       ├── ofi_reversal.py          ✅  방안 B
│       ├── vwap_reversal.py         ✅  방안 C
│       ├── exhaustion_regime.py     ✅  방안 D
│       └── absorption.py            ✅  방안 E (FutureJpBid 대기)
├── features/technical/
│   ├── cvd_exhaustion.py            ✅  feature_builder 통합
│   └── ofi_reversal.py              ✅  feature_builder 통합
├── dashboard/panels/
│   ├── __init__.py                  ✅
│   └── challenger_panel.py          ✅  레짐 전문가 승위표 + 전체 도전자 테이블
└── data/db/
    └── challenger.db                ✅  자동 생성 (스키마 마이그레이션 포함)
```

---

### 3-3. DB 스키마 (실제 구현 — 원안 대비 2개 테이블 추가)

```sql
-- 원안 그대로 구현 (regime 컬럼 추가)
CREATE TABLE challenger_signals (... regime TEXT DEFAULT '혼합');
CREATE TABLE challenger_trades  (... regime TEXT DEFAULT '혼합');
CREATE TABLE challenger_daily_metrics (...);
CREATE TABLE champion_history   (... regime TEXT DEFAULT 'GLOBAL');

-- 신규 추가 (레짐 전문가 시스템)
CREATE TABLE challenger_regime_metrics (
    challenger_id TEXT NOT NULL,
    regime        TEXT NOT NULL,
    trade_count   INTEGER, win_count INTEGER, win_rate REAL,
    total_pnl_pt  REAL, mdd_pt REAL, sharpe REAL, last_updated TEXT,
    PRIMARY KEY (challenger_id, regime)
);

CREATE TABLE regime_rank_history (
    ts TEXT, regime TEXT,
    rank_1_id TEXT, rank_2_id TEXT, rank_3_id TEXT,
    prev_rank_1 TEXT, changed INTEGER
);
```

---

### 3-4. 레짐 전문가 시스템 (원안 확장)

원안에는 없었던 **레짐별 챔피언 분리 관리** 설계가 추가됨.

#### REGIME_POOLS (레짐별 전문가 풀)

| 레짐 | 전문가 풀 | 챔피언 (초기값) | 비고 |
|------|----------|----------------|------|
| 추세장 | `[CHAMPION_BASELINE]` | CHAMPION_BASELINE | 앙상블이 담당 |
| 횡보장 | `[CHAMPION_BASELINE]` | CHAMPION_BASELINE | 앙상블이 담당 |
| 혼합   | `[CHAMPION_BASELINE]` | CHAMPION_BASELINE | 앙상블이 담당 |
| 급변장 | `[]` | None | 진입 금지 |
| 탈진   | `[A_CVD, C_VWAP, D_EXHAUSTION]` | **None** → 수동 승격 필요 |

#### 레짐 전문가 승격 기준

```python
REGIME_SPECIALIST_CRITERIA = {
    "min_regime_trades":     20,   # 달력일 아닌 레짐 내 거래 수
    "win_rate_vs_baseline": +2.0,  # CHAMPION_BASELINE 동일 레짐 승률 대비 +2%
    "sharpe_min":            1.30, # 희소 레짐 고려해 완화 (전역 기준: 1.50)
    "pnl_positive":          True,
}
```

#### Shadow 1위 WARNING 흐름

```
일별 마감 (15:40)
  → _compute_regime_metrics(): 레짐별 누적 집계 갱신
  → _check_regime_rankings(): 레짐별 순위 계산
  → 1위 변경 감지 시:
       registry.update_regime_shadow_rank1() → True 반환
       db.insert_regime_rank() 기록
       _emit_rank_change_warning() →
         logger.warning(msg)
         log_manager.system(msg, "WARNING")  ← 대시보드 경보 탭
```

---

### 3-5. 레짐 판단 구조 (원안 대비 수정됨)

원안에서 `RegimeClassifier.classify_micro()`를 사용하던 것을 `MicroRegimeClassifier`로 교체.

| 계층 | 담당 클래스 | 위치 | 주기 | 출력 |
|------|------------|------|------|------|
| 매크로 | `RegimeClassifier.classify()` | `collection/macro/regime_classifier.py` | 일 1회 (장 전) | RISK_ON / NEUTRAL / RISK_OFF |
| 미시 | `MicroRegimeClassifier.push_1m_candle()` | `collection/macro/micro_regime.py` | **매분** | 추세장 / 횡보장 / 급변장 / 혼합 / **탈진** |

`MicroRegimeClassifier` 입력:
- `high, low, close` → ADX 자체 계산 (이전: `adx_dummy=22.0` 하드코딩)
- `cvd_exhaustion`, `ofi_reversal_speed`, `vwap_position` → 탈진 레짐 판정

---

### 3-6. 진입 파이프라인 통합 (원안 대비 확장)

원안: "2줄만 추가" → 실제: 5개 연결 포인트

| 위치 | 코드 | 역할 |
|------|------|------|
| `main.py __init__()` | `ChallengerEngine` + `PromotionManager` 초기화 | 엔진 생성 |
| `main.py STEP 4 후` | `micro_regime_clf.push_1m_candle()` | 미시 레짐 실계산 |
| `main.py STEP 6 [§20]` | `RegimeChampGate` | 챔피언 없는 레짐 진입 차단 |
| `main.py STEP 9 후` | `challenger_engine.run_shadow()` | Shadow 실행 (5ms 가드) |
| `main.py daily_close()` | `update_daily_metrics()` + `micro_regime_clf.reset_daily()` | 일별 집계 + 리셋 |

#### [§20] RegimeChampGate 동작

```python
_reg_champ = registry.get_regime_champion(current_micro_regime)

if _reg_champ is None:
    direction = 0 / grade = "X"   # 탈진 레짐: 전문가 수동 승격 전까지 진입 차단
elif _reg_champ == CHAMPION_BASELINE_ID:
    pass                           # 앙상블 신호 그대로 사용
else:
    log("[전문가 챔피언 활성]")     # 로그 기록, 신호는 앙상블 유지 (추후 확장)
```

---

### 3-7. strategy_params.py EXHAUSTION 파라미터

```python
("RISK_ON",  "EXHAUSTION"): {"entry_conf_neutral": -0.04, "kelly_max_mult": -0.30,
                              "atr_tp1_mult": -0.50, "atr_stop_mult": -0.25},
("NEUTRAL",  "EXHAUSTION"): {"entry_conf_neutral": -0.02, "kelly_max_mult": -0.30,
                              "atr_tp1_mult": -0.50, "atr_stop_mult": -0.25},
("RISK_OFF", "EXHAUSTION"): {"entry_conf_neutral": 9999.0, "kelly_max_mult": 0.0},
```

---

### 3-8. 대시보드 모니터링

| 위치 | 표시 내용 |
|------|----------|
| 헤더 `lbl_regime` (기존) | 매크로 레짐 — RISK_ON(초록) / NEUTRAL(주황) / RISK_OFF(빨강) |
| 헤더 `lbl_micro_regime` (신규) | 미시 레짐 — 추세(초록) / 횡보(파랑) / 급변(빨강) / 혼합(주황) / **탈진(보라)** |
| 도전자 모니터 탭 상단 | `현재 레짐: 탈진⚡ \| ADX: 28.5 \| ATR비: 1.72 \| 지속: 3분` |
| 도전자 모니터 탭 중단 | 레짐별 전문가 승위표 (Shadow 1위 변경 시 보라 배경 + "🔴 변경!" 배지) |
| 도전자 모니터 탭 하단 | 전체 도전자 성과 테이블 + 전역 승격 관리 |
| 경보 탭 | Shadow 1위 변경 시 WARNING 자동 발송 |

---

### 3-9. 승격 안전 원칙 (CLAUDE.md 동일 적용)

```
자동 승격: 금지 (코드 레벨 보장)

전역 승격 절차:
  1. evaluate_for_promotion() → READY 조건 달성
  2. 패널에 "승격가능" 강조 표시
  3. 사용자 [▶ 전역 승격] 클릭 → 확인 다이얼로그 (6개 조건 전시)
  4. 승인 → promote() → champion_history GLOBAL 기록

레짐 전문가 승격 절차:
  1. evaluate_regime_specialist() → READY 조건 달성
  2. 경보 탭 WARNING + 승위표 1위 배지
  3. 사용자 [▶ 레짐 전문가 승격] 클릭 → 확인 다이얼로그
  4. 승인 → promote_regime_specialist() → champion_history regime 기록
  5. 이후 해당 레짐에서 실거래 담당 (RegimeChampGate 통과)

롤백:
  - 전역: rollback() → champion_history GLOBAL 역참조
  - 레짐: rollback_regime_specialist() → champion_history regime 역참조
```

---

## PART 4. 구현 결과 체크리스트

### Phase C-1: DB 및 기반 클래스
- [x] `challenger/` 디렉토리 생성
- [x] `challenger/variants/` 디렉토리 생성
- [x] `challenger/challenger_db.py` — 6개 테이블 스키마 + 마이그레이션
  - [x] `challenger_signals` (regime 컬럼 포함)
  - [x] `challenger_trades` (regime 컬럼 포함)
  - [x] `challenger_daily_metrics`
  - [x] `challenger_regime_metrics` ← **신규 (레짐 전문가용)**
  - [x] `regime_rank_history` ← **신규 (WARNING 판단용)**
  - [x] `champion_history` (regime 컬럼 포함)
- [x] `challenger/variants/base_challenger.py`
  - [x] `ChallengerSignal`, `ChallengerTrade`, `ExitReason`
  - [x] `BaseChallenger` 추상 클래스 + ATR TP/SL 기본 구현

### Phase C-2: Shadow 엔진 + 레지스트리
- [x] `challenger/challenger_registry.py`
  - [x] `REGIME_POOLS` — 레짐별 전문가 풀 정의
  - [x] `_regime_champions` — 레짐별 실거래 챔피언 포인터
  - [x] `_regime_shadow_rank1` — Shadow 1위 추적 (WARNING 판단)
  - [x] `update_regime_shadow_rank1()` → bool (변경 여부)
  - [x] 하위 호환 API: `get_champion_id()`, `set_champion()`
- [x] `challenger/challenger_engine.py`
  - [x] `run_shadow()` — regime 태깅 포함
  - [x] `update_daily_metrics()` — 전체 + 레짐별 집계 + 순위 감지
  - [x] `_compute_regime_metrics()` — 레짐별 누적 집계
  - [x] `_check_regime_rankings()` — 1위 변경 감지 + WARNING
  - [x] `_emit_rank_change_warning()` — 대시보드 경보 탭 전송
  - [x] 5ms 가드

### Phase C-3: 도전자 5종 구현
- [x] `challenger/variants/cvd_exhaustion.py` — `CvdExhaustionChallenger`
- [x] `challenger/variants/ofi_reversal.py` — `OfiReversalChallenger`
- [x] `challenger/variants/vwap_reversal.py` — `VwapReversalChallenger`
- [x] `challenger/variants/exhaustion_regime.py` — `ExhaustionRegimeChallenger`
- [x] `challenger/variants/absorption.py` — `AbsorptionChallenger` (FutureJpBid 대기)

### Phase C-4: 메인 파이프라인 연결
- [x] `main.py __init__()` — `ChallengerEngine` + `PromotionManager` 초기화
- [x] `main.py` STEP 4 후 — `MicroRegimeClassifier.push_1m_candle()` (ADX 실계산)
- [x] `main.py` STEP 6 [§20] — `RegimeChampGate` (챔피언=None 레짐 진입 차단)
- [x] `main.py` STEP 9 후 — `challenger_engine.run_shadow()`
- [x] `main.py daily_close()` — `update_daily_metrics()` + `micro_regime_clf.reset_daily()`
- [x] `dashboard` — `set_challenger_engine()` 주입

### Phase C-5: 패널 UI
- [x] `dashboard/panels/__init__.py`
- [x] `dashboard/panels/challenger_panel.py`
  - [x] 현재 미시 레짐 상태 바 (ADX·ATR비·지속 시간 표시)
  - [x] 레짐별 전문가 승위표 (Shadow 1위 변경 시 보라 배경 + 배지)
  - [x] 레짐 전문가 승격/롤백 버튼
  - [x] 전체 도전자 성과 테이블
  - [x] 승격 조건 체크 패널 (6개 항목)
  - [x] ASCII 스파크라인 (누적 손익 추세)
  - [x] 전역 승격/롤백 버튼
  - [x] 30초 자동 갱신
- [x] `dashboard/main_dashboard.py` — "⚔ 도전자 모니터" 탭 + `lbl_micro_regime` 헤더 배지

### Phase C-6: 승격 관리자
- [x] `challenger/promotion_manager.py`
  - [x] 전역 승격: `evaluate_for_promotion()`, `promote()`, `rollback()`
  - [x] 레짐 전문가: `evaluate_regime_specialist()`, `promote_regime_specialist()`, `rollback_regime_specialist()`
  - [x] `get_regime_ranking()`

### Phase C-7: 고도화 피처 구현
- [x] `features/technical/cvd_exhaustion.py` — `CvdExhaustionCalculator`
- [x] `features/technical/ofi_reversal.py` — `OfiReversalCalculator`
- [x] `features/feature_builder.py` — 두 계산기 통합, `cvd_exhaustion` / `ofi_reversal_speed` 피처 추가

### Phase C-8: 탈진 레짐 + 체크리스트 분기
- [x] `collection/macro/micro_regime.py`
  - [x] `REGIME_EXHAUSTION = "탈진"` (한글 상수)
  - [x] 탈진 레짐 4가지 조건 판정
  - [x] `REGIME_EXHAUSTION_PARAMS` 딕셔너리
  - [x] `push_1m_candle()` — ADX 자체 계산 + cvd/ofi/vwap 입력
- [x] `strategy/entry/checklist.py`
  - [x] 체크리스트 #3 VWAP 분기 (MEAN_REVERSION 모드)
  - [x] `entry_mode` 필드 반환
- [x] `config/settings.py` — `CHALLENGER_DB`, `PROMOTION_CRITERIA`, `REGIME_EXHAUSTION_PARAMS`
- [x] `config/strategy_params.py` — EXHAUSTION 레짐 오버라이드 3종 추가

---

## PART 5. 잔여 연결 항목 (미완성)

| 항목 | 현재 상태 | 필요 작업 |
|------|----------|----------|
| 탈진 레짐 전문가 신호 오버라이드 | 로그만 출력, 앙상블 신호 유지 | run_shadow() 이전 호출로 이동 + `get_champion_regime_signal()` 구현 |
| `AbsorptionChallenger` FutureJpBid 연결 | `_hoga_active=False` 대기 | `realtime_data.py`에서 `update_hoga()` 훅 연결 |
| 탈진 레짐 피처 실데이터 검증 | 코드 완성, 장 중 발동 미확인 | 장 중 SIGNAL.log에서 `[MicroRegime] 레짐 변경 → 탈진` 확인 |
| ADX 계산 정확성 검증 | Wilder's 단순화 버전 사용 중 | 실데이터 대비 참조 ADX와 비교 |

---

## PART 6. 검증 계획

| 검증 항목 | 방법 | 통과 기준 |
|----------|------|----------|
| Shadow 실행 성능 | 매분 타이밍 측정 | < 5ms |
| DB 무결성 | 1일 시뮬레이션 후 레코드 확인 | 오류 0건 |
| 탈진 레짐 발동 | 장 중 SIGNAL.log 모니터링 | `[MicroRegime] 레짐 변경 → 탈진` 출력 확인 |
| RegimeChampGate 차단 | 탈진 레짐 진입 시도 시 `grade=X` 확인 | 자동 진입 0건 |
| 레짐 WARNING 발송 | 일별 마감 후 경보 탭 확인 | Shadow 1위 변경 시 경보 표시 |
| 롤백 동작 | promote → rollback 순서 테스트 | 이전 챔피언 복구 확인 |
| 미시 레짐 헤더 배지 | 장 시작 후 `lbl_micro_regime` 색상 변화 확인 | 1분마다 갱신 |

---

*최종 업데이트: 2026-05-12 — Phase C-1~C-8 + 레짐 전문가 확장 구현 완료*
