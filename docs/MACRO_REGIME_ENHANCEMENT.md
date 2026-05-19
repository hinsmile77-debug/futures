# 매크로 레짐 종합 강화 제안
> 작성일: 2026-05-19 | 관점: 선물 일수익 1% 트레이더

---

## 1. 진단 — 3가지 구조적 결함

### 결함 1: 장전 1회 고정, 장중 붕괴 미반영
`main.py:1980` 에서 `classify()` 로 한 번 정하고, 이후 장중에는 `main.py:2420` 의 미시 레짐만 갱신된다.  
2026-05-19 08:55 기준 VIX=17.8, SP500=+0.00%, USD/KRW=+0.00% → **NEUTRAL 확정** 후 하루 종일 고정.  
68pt 폭락 같은 당일 충격은 매크로 레짐에 전혀 반영되지 않는다.

### 결함 2: macro_fetcher 첫 fetch 변화율 구조적 0
`macro_fetcher.py:106~110` 에서 이전값 `self._prev` 가 없으면 `*_chg = 0.0` 으로 세팅한다.  
첫 fetch 시점의 SP500·USD/KRW 변화율이 항상 0으로 시작 → `regime_classifier.py:43~78` 기준 VIX 점수(+1)만 반영되어 **구조적 NEUTRAL 편향** 발생.

### 결함 3: 미시 레짐 급변장 기준 과도하게 둔감
`micro_regime.py:53, 148` 에서 `ATR ratio >= 2.0` 이어야 급변장 판정.  
오늘 로그상 MicroRegime 최대 ratio = **1.33**, 급변장 전환 = **0회**.  
폭락일인데도 내내 추세장/횡보장/혼합 안에서만 움직였다.

---

## 2. 설계 원칙 — 2계층 분리

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Overnight Macro Regime                │
│  08:55 1회 판정, 글로벌 환경 (VIX·SP500·환율)     │
│  RISK_ON / NEUTRAL / RISK_OFF                   │
└─────────────────┬───────────────────────────────┘
                  │ 장중 overlay (우선 적용)
┌─────────────────▼───────────────────────────────┐
│  Layer 2: Intraday Tactical Regime (신설)        │
│  매분 갱신, 당일 선물 수익률 기반                  │
│  NORMAL / DAY_RISK_OFF / CRASH                  │
└─────────────────────────────────────────────────┘

최종 적용 레짐 = Layer 2가 NORMAL  → Layer 1 사용
               Layer 2가 DAY_RISK_OFF / CRASH → Layer 2 우선
```

---

## 3. 버그 수정 (1순위 — 즉시 적용)

### macro_fetcher.py 첫 fetch 0 문제

```python
# 현재 (문제)
if self._prev is None:
    sp500_chg = 0.0   # 항상 0 → NEUTRAL 편향

# 수정안 A: 첫 fetch는 레짐 판정 스킵, 2회차부터 반영
if self._prev is None:
    self._prev = current
    return None  # 호출부에서 None이면 이전 레짐 유지

# 수정안 B: 전날 종가를 별도 소스에서 초기화 (더 정확)
# macro_fetcher 초기화 시 전일 종가 fetch → self._prev 사전 세팅
```

이 버그만 수정해도 SP500 전일 등락이 있던 날 NEUTRAL 편향이 사라진다.

---

## 4. Layer 2: Intraday Tactical Regime 발동 규칙

### DAY_RISK_OFF 발동 (둘 중 하나)

| 조건 | 수식 |
|------|------|
| A | 선물 당일 수익률 ≤ −1.0% |
| B | 시가 대비 낙폭 ≤ −0.8% **AND** 직전 15분 수익률 ≤ −0.5% |

> 오늘 기준: 09:30경 조건 B 달성 → 이 시점부터 롱 금지·숏 허용으로 전환 가능했음

### CRASH 발동 (셋 중 하나)

| 조건 | 수식 |
|------|------|
| A | 선물 당일 수익률 ≤ −1.8% |
| B | 30분 수익률 ≤ −1.0% **AND** ATR ratio ≥ 1.25 |
| C | z-score extreme (\|z\| > 4) 가 **3개 이상 horizon에서 동시 발생** |

> 오늘 09:00~09:05: 6개 horizon 전부 z-score 경고 → 조건 C 즉시 달성  
> z-score는 이미 SIGNAL 로그에서 매분 집계 중 — 연결만 하면 됨

### RECOVERY_NEUTRAL 복귀 (셋 모두 충족)

| 조건 | 수식 |
|------|------|
| 1 | 당일 저점 대비 반등률 ≥ +0.5% |
| 2 | OFI 15분 이동평균 > 0 (매수 우세 회복) |
| 3 | ATR ratio < 1.2 (변동성 정상화) |

셋 모두 충족해야 복귀. 하나라도 미달이면 DAY_RISK_OFF 유지.

---

## 5. 레짐별 진입 정책

| 상태 | 신규 롱 | 신규 숏 | 최소 신뢰도 보정 | 사이즈 배율 |
|------|--------|--------|----------------|-----------|
| RISK_ON | 허용 | 허용 | −2%p | ×1.1 |
| NEUTRAL | 허용 | 허용 | 기본 | ×1.0 |
| DAY_RISK_OFF | **금지** | 허용 | +5%p | ×0.5 이하 |
| CRASH | **금지** | A등급 숏 추세추종만 | +12%p | ×0.3 |

> 1% 수익 관점: DAY_RISK_OFF·CRASH 날 롱 차단만으로 최악의 손실 구조 제거 가능.  
> 오늘처럼 모델이 상승 예측해도 레짐이 롱 금지하면 CB③ 4회 반복 발동 자체가 없었을 것.

---

## 6. Contrarian ACTIVE → 레짐 자동 승격 (핵심 연동)

오늘 로그 (`20260519_WARN.log:78`): `14:01 Contrarian ACTIVE | acc30m=0.0% streak=10 regime=NEUTRAL`

Contrarian ACTIVE 조건(acc30m < 25% + 동방향 10연속)은 그 자체로 CRASH 신호다.  
"레짐은 정상인데 내부 안전장치는 이미 비정상" 상태를 레짐 승격 트리거로 활용한다.

```python
# contrarian 발동 시 자동 레짐 승격
if contrarian_mode.should_contra_enter():
    if intraday_regime == "NORMAL":
        intraday_regime = "DAY_RISK_OFF"   # 최소 승격
    # CRASH 조건 추가 충족 시 CRASH까지 승격
```

Contrarian이 NEUTRAL 레짐 속에서 고립 작동하는 비효율이 사라진다.

---

## 7. 미시 레짐 급변장 기준 개선

기존 단일 조건 `ATR ratio >= 2.0` → 아래로 교체:

```python
# 급변장 판정 (셋 중 하나)
급변장 = (
    atr_ratio >= 1.5                           # 기존 2.0 → 1.5 완화
    or abs(z_score_extreme_count) >= 3          # 이미 수집 중, 연결만 필요
    or (atr_ratio >= 1.25 and adx > 30)        # 강한 추세 + 높은 변동성
)
```

급변장 진입 정책은 현행 유지 (`allow_new_entry=False`).

---

## 8. 구현 로드맵

| 순위 | 항목 | 효과 | 난이도 |
|------|------|------|--------|
| **1** | macro_fetcher 첫 fetch 0 버그 수정 | 높음 | 낮음 |
| **2** | Intraday Tactical Regime 클래스 신설 | 매우 높음 | 중간 |
| **2** | 선물 당일 수익률 기반 DAY_RISK_OFF / CRASH 발동 | 매우 높음 | 중간 |
| **2** | 미시 레짐 급변장 기준 1.5로 완화 + z-score 연동 | 높음 | 낮음 |
| **3** | Contrarian ACTIVE → 레짐 승격 연동 | 높음 | 낮음 |
| **3** | RECOVERY_NEUTRAL 복귀 조건 구현 | 중간 | 중간 |
| **3** | 레짐별 롱 금지 / 숏 허용 분리 정책 적용 | 높음 | 낮음 |
| **4** | 외국인 선물 순매수 방향 실시간 수집 (Cybos TR) | 매우 높음 | 높음 |
| **4** | Layer 2 레짐 대시보드 상단 배지 노출 | 중간 | 낮음 |

---

## 9. 오늘(2026-05-19) 시뮬레이션

| 시각 | 실제 결과 | 개선 후 예상 |
|------|-----------|------------|
| 09:00~09:05 | NEUTRAL, 롱 시도 | z-score 6개 → CRASH 발동, 신규 롱 금지 |
| 09:30 | NEUTRAL, CB③ 발동 전 | 시가 −1.2% → DAY_RISK_OFF, 숏만 허용 |
| 09:50 | CB③ HALT #1 | 이미 CRASH라 신규 진입 없음 → CB③ 미발동 |
| 11:15 | 반등 시작 | RECOVERY 조건 미충족 → DAY_RISK_OFF 유지 |
| 14:01 | Contrarian ACTIVE·NEUTRAL 고립 | DAY_RISK_OFF 자동 승격 |

> CB③이 4번 반복 발동하지 않았을 것이며, 11:15 반등 이후 숏 추세추종 A등급 조건 충족 시 1건 이상 거래 성립 가능.

---

## 10. 한 줄 요약

> **지금 시스템은 "글로벌 장전 분위기"는 보지만 "국내 선물 당일 붕괴"를 레짐으로 승격시키지 못한다.  
> 1% 일수익 관점에서는 장전 매크로보다 장중 선물 수익률 기반 전술 레짐이 훨씬 중요하다.**
