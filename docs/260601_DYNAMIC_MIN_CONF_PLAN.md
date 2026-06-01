# 동적 min_conf 설계 및 구현 계획

> **작성일**: 2026-06-01  
> **배경**: 재학습 전후 conf 분포 급변으로 인한 진입0 문제 → mc 동적화 필요  
> **데이터 근거**: 재학습 전 avg=0.406 → 재학습 후 avg=0.698 (conf 분포 완전 교체)

---

## 1. 현재 mc 결정 구조

```
[고정 기반값] time_strategy_router.py _ZONE_PARAMS
  GAP_OPEN:       0.67
  OPEN_VOLATILE:  0.60
  STABLE_TREND:   0.54
  LUNCH_RECOVERY: 0.57
  CLOSE_VOLATILE: 0.62
        ↓
[레짐 오버라이드] apply_regime_override()
  RISK_OFF: +0.05  /  RISK_ON: -0.02
        ↓
[Layer 2 조정] intraday_regime.min_conf_adjust()
  DAY_RISK_OFF / CRASH → +N%p
        ↓
[TrendGate 완화] TrendPersistenceGate
  추세 10분+ 지속 → min_conf 일시 하향 (~0.44)
        ↓
final actual_min_conf (main.py에서 결정)
```

**문제**: 기반값(고정)이 GBM conf 분포와 동기화되지 않음.  
모델이 재학습되거나 시장 변동성 레짐이 바뀌면 conf 분포가 수십%p 변하는데  
mc는 그대로 고정 → 수일간 진입0 지속.

### 실측 데이터 (2026-05-26 ~ 2026-06-01)

| 날짜 | conf 평균 | conf p70 | X율 | mc(0.57) 통과율 |
|---|---|---|---|---|
| 05-26 | 0.420 | 0.468 | 89% | 0% |
| 05-27 | 0.390 | 0.409 | 100% | 0% |
| 05-28 | 0.397 | 0.427 | 100% | 0% |
| 05-29 | 0.432 | 0.483 | 96% | 0% |
| 06-01 (재학습 전) | 0.406 | 0.433 | 100% | 0% |
| **06-01 재학습 후** | **0.698** | **~0.72** | **-** | **10.8%** |

---

## 2. 진입0 진단 요약

```
근본 원인 체인:
  GBM conf 분포 (0.35~0.58)
        vs
  고정 mc (0.57~0.67)
  → 모든 봉 grade=X → 진입 0건

mc 기준 자체는 논리적으로 맞음.
하지만 "어느 수준의 conf를 신뢰할 것인가"는
모델 상태와 시장에 따라 달라져야 함.
```

---

## 3. 동적 mc 설계안 — 2가지 주기

### 주기 1: GBM 재학습 완료 즉시 (이벤트 기반)

```
트리거: _on_gbm_retrain_done() 콜백
방법:
  predictions DB에서 직전 5거래일 conf 분포 측정
  → new_mc = max(conf_p65, MC_ABS_FLOOR)
  → 시간대별 mc = new_mc × 시간대 배율 테이블
  → _ZONE_PARAMS 런타임 업데이트
  → mc_history.db에 변경 이력 저장
```

**오늘 적용 예시**:  
재학습 전 p65 ≈ 0.45 → floor=0.50 → mc=0.50  
재학습 후 p65 ≈ 0.67 → mc=0.67 (STABLE_TREND 기준)

### 주기 2: 매일 08:55 스케일러 워밍업 완료 후 (일간 재보정)

```
트리거: pre_market_setup() 스케일러 워밍업 완료 직후
방법:
  최근 10거래일 conf 분포 EMA(alpha=0.2) 기반
  → ema_p65 = 0.8×이전값 + 0.2×오늘_p65
  → 급격한 변화 방지 (전날 대비 ±0.05 clamp)
```

---

## 4. mc 결정 규칙 (시간대 배율)

| 시간대 | 배율 | 이유 |
|---|---|---|
| GAP_OPEN | base × 1.05 | 시초가 급변 리스크 |
| OPEN_VOLATILE | base × 1.02 | 개장 변동성 |
| STABLE_TREND | base × 1.00 | 기준 구간 |
| LUNCH_RECOVERY | base × 0.99 | 외인 재진입 감지 |
| CLOSE_VOLATILE | base × 1.01 | 마감 리스크 |

`base_mc = max(conf_p65, MC_ABS_FLOOR=0.50)`  
시간대 mc = `clip(base × 배율, MC_ABS_FLOOR, MC_ABS_CEIL=0.75)`

---

## 5. 추천 구현 (채택)

**주기 1 + 주기 2 동시 적용. 주기 3(일중 실시간) 미채택.**

주기 3 미채택 이유: 일중 mc가 분봉마다 변하면 진입 판단이 불안정해지고  
"오늘 오전에 진입 안 됐는데 오후에 됐다"는 불확실성이 생김.  
일관된 기준을 하루 단위로 유지하는 것이 더 예측 가능.

### 변경 이력 저장 (mc_history.db)

```sql
CREATE TABLE mc_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,           -- 변경 시각
    trigger     TEXT NOT NULL,           -- 'RETRAIN' | 'DAILY_WARMUP'
    base_mc     REAL NOT NULL,           -- 기반 mc (p65 기준)
    zone        TEXT NOT NULL,           -- 시간대 코드
    old_mc      REAL NOT NULL,           -- 변경 전 mc
    new_mc      REAL NOT NULL,           -- 변경 후 mc
    conf_avg    REAL,                    -- 측정 기간 conf 평균
    conf_p65    REAL,                    -- 측정 기간 conf 65th percentile
    n_samples   INTEGER                  -- 측정 표본 수
);
```

---

## 6. 기대 효과

```
이전:  mc 고정 → conf 분포 변해도 mc 불변 → 수일간 진입0
이후:
  재학습 완료 즉시 → mc 자동 재보정 → 당일 신호 통과
  매일 08:55      → 시장 변화 점진 반영 → 중기 안정성

06-01 시뮬:
  재학습 후 mc=0.67 자동 설정 → 22건 진입, 승률 77%, +1,056만원
  (기존 고정 mc=0.57 기준에서도 42건 55% 수준으로 개선)
```

---

## 7. 관련 파일

| 파일 | 역할 |
|---|---|
| `config/settings.py` | MC_PERCENTILE=0.65, MC_ABS_FLOOR=0.50, MC_ABS_CEIL=0.75 |
| `strategy/entry/time_strategy_router.py` | `update_dynamic_mc()`, `_ZONE_MC_MULT` |
| `main.py` | `_on_gbm_retrain_done`, `pre_market_setup` 연결 |
| `data/db/mc_history.db` | 변경 이력 저장 |
| `dashboard/panels/dynamic_mc_panel.py` | UI 패널 (금일 추이 + 이력) |
