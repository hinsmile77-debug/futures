# 임계값 개선을 위한 WFA 모니터 방안

> 작성일: 2026-05-30  
> 데이터 기준: 2026-04-28 ~ 2026-05-29 (21 거래일, 4.4주)  
> 관련 파일: `config/settings.py`, `model/target_builder.py`, `backtest/walk_forward.py`, `strategy/param_drift_detector.py`

---

## 1. 배경 및 문제 정의

### 1-1. 임계값이란

`HORIZON_THRESHOLDS`는 미래 N분 후 수익률이 임계값을 초과하면 UP/DOWN, 미만이면 FLAT으로 레이블링하는 기준값이다.

```python
# model/target_builder.py
ret = (price[i+h] - price[i]) / price[i]
if   ret >  thresh: label = UP    (+1)
elif ret < -thresh: label = DOWN  (-1)
else:               label = FLAT  ( 0)
```

### 1-2. 현재 설정값의 문제

2026-05-30 기준 데이터 분석 결과, 현재 `HORIZON_THRESHOLDS_BASE`와 데이터 기반 최적값 사이에 다음 괴리가 확인됐다.

| 호라이즌 | 현재 BASE | 데이터 기반 최적값 | 괴리 | 영향 |
|---|---|---|---|---|
| 1m  | 0.0500% | 0.041% | +22% 과다 | FLAT 과다 |
| 3m  | 0.0600% | 0.060% | 동일 | — |
| 5m  | 0.1100% | 0.092% | +20% 과다 | FLAT 과다 |
| 10m | 0.1600% | 0.148% | +8% 과다 | 소폭 |
| 15m | 0.2200% | 0.155% | **+42% 과다** | FLAT 심각 과다 |
| 30m | 0.3200% | 0.196% | **+63% 과다** | FLAT 심각 과다 |

### 1-3. 임계값이 시간에 따라 변하는 이유

임계값은 시장 변동폭의 함수다. 아래 시나리오에서 고정 임계값은 즉시 부적절해진다.

| 시나리오 | 변동폭 변화 | 고정 임계값 영향 |
|---|---|---|
| 장세 전환 (상승→횡보) | 변동폭 축소 | FLAT 과소 → UP/DOWN 남발 |
| 외인 이벤트 쇼크 | 변동폭 확대 | FLAT 과다 → 신호 실종 |
| 야간 갭 정상화 | 구조적 변화 | 비대칭 편향 소멸 |
| 현재 상승 추세 소멸 | 방향성 감소 | 단기 임계값 과대 추정 |

현재 산출된 임계값은 **KOSPI200 선물 1200pt 전후, 상승 추세 구간의 스냅샷**이다. 시장 구조가 바뀌면 임계값도 재보정이 필요하다.

---

## 2. WFA 모니터 구조 — 3단계 전환 설계

현재 데이터(4.4주)로는 전통 WFA(최소 26주)를 즉시 적용할 수 없다. 데이터 누적량에 따라 3단계로 전환한다.

```
Phase A (현재 ~ +6주)  : 롤링 재보정 모니터      ← 지금 구축
Phase B (+6주 ~ +26주) : 슬라이딩 품질 모니터
Phase C (+26주 이후)   : 전통 WFA 통합
```

> **임계값 WFA의 목적**은 수익률(Sharpe/MDD) 최적화가 아니라  
> **레이블 분포 33/34/33 유지 + 시장 레짐 변화 반영**이다.

---

## 3. Phase A — 롤링 재보정 모니터 (즉시 구축)

### 3-1. 실행 시점

매주 금요일 15:40 자가학습 일일 마감 직후 (`main.py` EOD 훅).

### 3-2. 계산 로직

```python
# 전체 raw_candles로 호라이즌별 수익률 분포 재산출
# target_builder.build_targets() 재활용

for horizon in HORIZONS:
    rets = compute_returns(raw_candles, horizon)
    n = len(rets)
    sorted_rets = sorted(rets)

    # 33/34/33 분위수
    thresh_down = sorted_rets[int(n * 0.33)]
    thresh_up   = sorted_rets[int(n * 0.67)]
    new_thresh  = (abs(thresh_down) + thresh_up) / 2  # 대칭화

    # 현재 BASE로 FLAT 비율 계산
    flat_actual = sum(1 for r in rets if -current_base <= r <= current_base) / n * 100
```

### 3-3. 경보 트리거 (둘 중 하나 해당 시 업데이트)

| 조건 | 기준 | 경보 레벨 |
|---|---|---|
| FLAT 비율 이탈 | 실제 FLAT이 목표(34%)에서 ±6%p 이상 | WATCHLIST |
| 임계값 변화율 | 현재 대비 재산출값이 ±15% 이상 | UPDATE |

```
FLAT 비율 28% 미만  or  40% 초과  → WATCHLIST
임계값 변화 ±15% 초과             → settings.py 업데이트 + 재학습 트리거
임계값 변화 ±15% 이내             → 유지 (노이즈로 판단)
```

### 3-4. 모니터링 지표 3개

```
1. FLAT drift        : 실제 FLAT 비율 vs 목표 34%  (±6%p 경보)
2. Threshold δ       : 현재 임계값 대비 재산출값 변화율  (±15% 경보)
3. ATR-Threshold ratio: threshold / ATR_p50  (정상 범위: 0.05 ~ 0.15)
```

**ATR-Threshold ratio 해석:**

```
현재 ATR p50 = 1.896pt (1300pt 시장 기준 0.146%)

ratio = threshold / ATR_p50
  < 0.05 : 임계값이 ATR 대비 너무 낮음 → FLAT 너무 적음
  0.05~0.15 : 정상
  > 0.15 : 임계값이 ATR 대비 너무 높음 → FLAT 너무 많음
```

---

## 4. Phase B — 슬라이딩 품질 모니터 (+6주부터)

### 4-1. 롤링 윈도우

```
window = 최근 4주 (20 거래일)
주간 갱신: 매주 금요일
```

### 4-2. 품질 지표

| 지표 | 계산 방식 | 경보 기준 |
|---|---|---|
| Brier Score 7일 MA | 호라이즌별 BS 7일 이동평균 | 2주 연속 상승 시 WATCHLIST |
| 불일치 구간 PnL | A=UD→B=FLAT 구간 진입 시 평균 손익 | 양전환 시 재산출 검토 |
| 고신뢰 정확도 | confidence 0.65+ 구간 실제 정확도 | 3%p 이상 하락 시 즉시 재산출 |
| ECE (캘리브레이션 오차) | 신뢰도 구간별 실제 정확도 편차 | 0.05 초과 시 경보 |

### 4-3. DriftDetector 재활용

기존 `strategy/param_drift_detector.py`의 CUSUM 로직을 임계값 품질 모니터로 재활용한다. 수익률 대신 Brier Score를 입력값으로 사용한다.

```python
# 기존 코드 재활용 (신규 개발 없음)
from strategy.param_drift_detector import DriftDetector

threshold_monitor = {
    h: DriftDetector(
        ref_daily_pnl_mean = brier_baseline[h],   # Phase A 산출 기준값
        ref_daily_pnl_std  = brier_baseline_std[h],
    )
    for h in HORIZONS
}

# 매일 업데이트
level, cusum, msg = threshold_monitor["30m"].update(today_brier_30m)
if level >= DriftLevel.ALARM:
    trigger_threshold_recalibration("30m")
```

**경보 수준 (기존 DriftLevel 그대로 사용):**

```
CLEAR     (CUSUM < 2.0) : 정상
WATCHLIST (CUSUM ≥ 2.0) : 모니터링 강화 — 다음 주 재산출 예고
ALARM     (CUSUM ≥ 4.0) : 즉시 임계값 재산출 검토
CRITICAL  (CUSUM ≥ 6.0) : 즉시 재산출 + GBM/SGD 재학습
```

---

## 5. Phase C — 전통 WFA 통합 (+26주부터)

### 5-1. PARAM_SPACE에 임계값 추가

26주가 쌓이면 `config/strategy_params.py`의 PARAM_SPACE에 임계값을 파라미터로 추가하여 기존 `param_optimizer.py`와 통합한다.

```python
# config/strategy_params.py에 추가 예정
"threshold_1m":  {"min": 0.00030, "max": 0.00060, "step": 0.00005},
"threshold_5m":  {"min": 0.00070, "max": 0.00120, "step": 0.00010},
"threshold_10m": {"min": 0.00100, "max": 0.00200, "step": 0.00010},
"threshold_15m": {"min": 0.00110, "max": 0.00220, "step": 0.00010},
"threshold_30m": {"min": 0.00140, "max": 0.00280, "step": 0.00020},
```

### 5-2. WFA 검증 기준 — 레이블 품질 기준 추가

기존 Sharpe/MDD/승률 기준에 임계값 전용 기준을 추가한다.

```
기존 기준 (유지):
  Sharpe ≥ 1.5
  MDD ≤ 15%
  승률 ≥ 53%

임계값 추가 기준:
  Brier Score 평균 ≤ 0.88 (1m 기준)
  FLAT 비율 편차 ≤ 5%p   (목표 34%에서 ±5%p 이내)
```

### 5-3. 실행 명령

```bash
# 임계값 그룹만 최적화
python -m backtest.param_optimizer --groups THRESHOLD --full-wfa

# 전체 파라미터 + 임계값 통합 최적화
python -m backtest.param_optimizer --groups ALL --full-wfa
```

---

## 6. 운영/연구 병렬 구조와의 연동

Phase A~C 전체에서 **운영(대칭)과 연구(비대칭) 임계값을 분리 모니터링**한다.

```
settings.py
├── HORIZON_THRESHOLDS         (운영: 대칭, ATR 동적 갱신 대상)
│     └── WFA 모니터 Phase A~C 적용
└── HORIZON_THRESHOLDS_RESEARCH (연구: 비대칭, 고정)
      └── WFA 모니터 Phase B부터 Brier Score 비교

[주간 금요일 15:40]
  운영 임계값 재보정 → Phase A 트리거 평가
  연구 임계값 성과 비교 → Phase B 시작 시 챔피언-도전자 판정
```

**ATR 동적 threshold와의 일관성 유지:**

```python
# _log_threshold_monitor() — 운영 임계값만 갱신 (변경 불필요)
_cfg.HORIZON_THRESHOLDS.update(new_thresholds)
# HORIZON_THRESHOLDS_RESEARCH는 갱신하지 않음 (고정 유지)
```

Phase A에서 운영 BASE가 변경되면 ATR 동적 threshold 발동 빈도가 함께 바뀐다.
새 BASE 기준 발동 ATR 기준값 (가격 1300pt):

| 호라이즌 | 새 BASE | 발동 ATR | 현재 분포 |
|---|---|---|---|
| 1m  | 0.041% | ATR > 4.4pt | p95 = 4.9pt |
| 5m  | 0.092% | ATR > 4.3pt | p95 = 4.9pt |
| 10m | 0.148% | ATR > 4.8pt | p99 = 6.6pt |
| 15m | 0.155% | ATR > 3.9pt | p90 = 3.9pt |
| 30m | 0.196% | ATR > 3.6pt | p90 = 3.9pt |

---

## 7. 구현 위치 및 작업 목록

### 7-1. 기존 코드 연결점

| 구성요소 | 파일 | 방식 |
|---|---|---|
| 수익률 분포 재산출 | `model/target_builder.py` | `build_targets()` 재활용 |
| FLAT 비율 모니터 | `strategy/param_drift_detector.py` | `DriftDetector` 재활용 |
| 주간 스케줄 | `main.py` 15:40 EOD 훅 | 기존 훅에 함수 1개 추가 |
| 연구용 비대칭 | `model/target_builder.py` | `build_targets_asymmetric()` 신규 |
| 결과 저장 | `data/db/threshold_monitor.db` | 신규 테이블 |

### 7-2. 우선순위별 작업 목록

| 우선순위 | 작업 | Phase | 난이도 | 효과 |
|---|---|---|---|---|
| **P0** | 매주 금요일 FLAT 비율 체크 + 로그 저장 | A | 낮음 | 즉각 |
| **P0** | threshold δ 경보 (±15% 트리거) | A | 낮음 | 즉각 |
| **P1** | DriftDetector로 Brier Score 추이 감시 | B | 낮음 | +4주 |
| **P1** | 운영/연구 분리 Brier Score 주간 비교 | B | 낮음 | +4주 |
| **P2** | PARAM_SPACE threshold 추가 | C | 중간 | +26주 |
| **P2** | WFA 레이블 품질 기준 추가 | C | 낮음 | +26주 |

### 7-3. threshold_monitor.db 스키마

```sql
CREATE TABLE threshold_log (
    date         TEXT,          -- YYYY-MM-DD
    horizon      TEXT,          -- 1m/3m/5m/10m/15m/30m
    current_base REAL,          -- 현재 BASE 임계값
    recalc_sym   REAL,          -- 재산출 대칭값
    recalc_down  REAL,          -- 재산출 비대칭 하단
    recalc_up    REAL,          -- 재산출 비대칭 상단
    flat_actual  REAL,          -- 실제 FLAT 비율 (%)
    flat_target  REAL DEFAULT 34.0,
    threshold_delta REAL,       -- 변화율 (%)
    atr_ratio    REAL,          -- threshold / ATR_p50
    alert_level  TEXT,          -- CLEAR/WATCHLIST/UPDATE
    updated      INTEGER DEFAULT 0,  -- 실제 업데이트 여부
    PRIMARY KEY (date, horizon)
);

CREATE TABLE brier_log (
    date         TEXT,
    horizon      TEXT,
    brier_ops    REAL,   -- 운영 임계값 기준
    brier_res    REAL,   -- 연구 임계값 기준
    cusum        REAL,
    drift_level  TEXT,
    PRIMARY KEY (date, horizon)
);
```

---

## 8. 요약

```
현재 (4.4주)    → Phase A: 롤링 재보정 모니터 (P0 즉시)
+6주 (10주)     → Phase B: Brier Score + DriftDetector (P1)
+22주 (26주)    → Phase C: PARAM_SPACE 통합 WFA (P2)

핵심 지표 3개:
  FLAT drift       (±6%p 경보)
  Threshold δ      (±15% 트리거)
  ATR-Threshold ratio (0.05~0.15 정상)

3m 임계값은 Phase C까지 현행(0.0006) 유지 — 데이터 불충분
비대칭 임계값은 26주 이후 상승 추세 편향 검증 후 Phase C에서 재검토
```
