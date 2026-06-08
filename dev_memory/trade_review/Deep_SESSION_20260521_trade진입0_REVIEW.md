# 2026-05-21 미륵이 진입 0건 + CB3 정지 종합 분석

> 분석일시: 2026-05-21 16:00 (장 종료 후)
> 분석 도구: openCode (Deep)
> 로그 소스: 20260521_SIGNAL.log, SYSTEM.log, WARN.log, TRADE.log, LEARNING.log
> 핵심 이벤트: 전일 진입 0건, 5회 재시작, CB3 13:22 당일 정지

---

## 1. 요약 결론

- 5/21 미륵이는 **1건의 진입도 없는 완전 관망일**이었다 (TRADE.log 9줄, 모두 시스템 초기화 로그).
- 근본 원인: **앙상블 confidence가 전일 최대 57.1%로, 모든 시간대의 min_conf threshold(58~67%)에 단 한 번도 도달하지 못함**.
- Contrarian Mode가 **09:13에 ACTIVE**(acc30m=0.0%, streak=10) — 장 시작 13분만에 모델이 완전히 틀렸음이 수학적으로 입증됨.
- 11:24에 STABLE_TREND 구간에서 57.1%를 기록했으나 min_conf=58%에 **0.9%p 차이로 유일하게 근접하고 실패**.
- CB3은 13:22 정상 발동했지만, 진입 0건은 CB3 이전 4시간+ 구간에서도 동일 — CB3와 무관하게 **모델 자체의 신뢰도 부족이 원인**.

---

## 2. 진입 0건의 결정적 원인: 시간대별 min_conf 미달

| 시간대 | min_conf | 앙상블 conf 범위 | 최대 conf | 격차 (최대 기준) |
|--------|:-------:|:----------------:|:---------:|:----------------:|
| GAP_OPEN (09:00~09:05) | **67.0%** | 44.6% ~ 50.8% | 50.8% | -16.2%p |
| OPEN_VOLATILE (09:05~10:30) | **63.0%** | 35.2% ~ 51.3% | 51.3% | -11.7%p |
| STABLE_TREND (10:30~11:50) | **58.0%** | 37.0% ~ **57.1%** | **57.1%** | **-0.9%p** |
| OTHER (11:50~15:10) | **65.0%** | 35.7% ~ 56.6% | 56.6% | -8.4%p |

> **핵심 발견**: STABLE_TREND 구간 11:24에 57.1%로 min_conf=58%에 0.9%p 차이로 **유일하게 근접**. 나머지 전 구간은 10%p 이상의 큰 격차. 모델이 낼 수 있는 신뢰도 상한 자체가 min_conf에 미달한 것.

---

## 3. 정량 분석 요약

| 항목 | 수치 |
|---|---|
| 전일 거래 | **0건 진입, 0건 청산** (TRADE.log 9줄) |
| 시스템 재시작 | **5회** (07:54 → 07:59 → 08:45 → 08:51 → 08:54) |
| Contrarian 첫 ACTIVE | **09:13** (acc30m=0.0%, streak=10, 역베팅=LONG) |
| Contrarian 재ACTIVE | **09:40** (acc30m=18.2%, streak=10) |
| Brier 과신 패널티 (0.45↑) | **5회** (09:42, 11:39, 12:39, 13:32, 14:50) |
| Brier 과신 경고 (0.35↑) | **30회+** (전일 거의 지속) |
| Mid-Conf Blind Spot (7연속) | **6회** (11:38, 12:36, 12:50, 13:33, 14:48, 15:27) |
| CB5 파이프라인 경고 (>1s) | **20회+** (최대 10,658ms @ 10:35, 5분 정지) |
| z-score 극단 경고 | 전 호라이즌 반복 (ofi_raw=+92.0, ofi_reversal_speed=-15.0, microprice_depth_bias=-17.3, queue_depletion_speed=+22.2) |
| 앙상블 방향 | SHORT 편향 지속 → 09:13 Contrarian ACTIVE (LONG)으로 역베팅 검증 |
| 레짐 | NEUTRAL 전일 지속 (VIX=17.4, SP500=+0.00%, USD/KRW=+0.00%) |

---

## 4. 시간대별 세부 분석

### A. 장전: 5회 재시작 → 세션 불안정 + scaler 미적응

```
07:54:39 기동 → 07:59:18 기동 → 08:45:16 기동 → 08:51:02 기동 → 08:54:22 기동
```

- 5회 연속 재시작은 비정상. `autologin` 또는 Cybos COM 초기화 문제로 추정.
- 매 재시작마다 `_accuracy_buf`, `_signal_history`, 온라인 학습 상태 초기화.
- `BrokerSync` 에러 반복: `rows=0 | 모의투자 데이터가 없습니다` → 잔고 TR 안정화 실패.
- 08:55 매크로 수집 결과: VIX=17.4(저공포), SP500 0%, KRW 0% → **NEUTRAL 레짐 확정**.

### B. 09:00~09:13: Contrarian ACTIVE — 장 시작 13분만에 모델 완전 오판

```
09:00  [Ensemble] dir=-1 conf=44.6% grade=X
09:01  [Ensemble] dir=+1 conf=46.7% grade=X
09:02  [Ensemble] dir=-1 conf=47.3% grade=X
09:03  [Ensemble] dir=-1 conf=46.6% grade=X
...
09:13  [Contrarian] ACTIVE | acc30m=0.0% streak=10 regime=NEUTRAL 역베팅방향=LONG
```

**acc30m=0.0%의 의미**: 직전 10개+ 30m 예측이 100% 오답. 모델은 SHORT를 고집했으나 실제 시장은 (Contrarian이 LONG을 제안할 만큼) 상승세.

> **이 시점에서 이미 "오늘 모델은 이 시장을 이해하지 못한다"는 사실이 통계적으로 증명되었다.** 이후 4시간 동안 진입 0건도 이 연장선.

### C. 09:13~10:30: OPEN_VOLATILE — Brier 0.476 급등

```
09:39  [Brier] 과신 경고 | 이동평균=0.393 > 0.35
09:40  [Brier] 과신 경고 | 이동평균=0.416 > 0.35
09:40  [Contrarian] ACTIVE | acc30m=18.2% streak=10
09:41  [Brier] 과신 경고 | 이동평균=0.446 > 0.35
09:42  [Brier] 과신 패널티 발동 | 이동평균=0.476 > 0.45 — 사이징 50% 강제 축소
```

- Brier Score가 09:39~09:42 사이 0.393 → 0.476으로 단 3분 만에 급등.
- Brier 0.476은 완벽 랜덤(0.22)의 2배 이상. 모델이 "확신하는데 완전히 틀리는" 과신 상태 확정.

### D. 10:35: CB5 파이프라인 10,658ms — S2(OnlineLearner) 10.3초

```
10:35  [PipePerf] total=10658ms | S2=10316ms S7=229ms
10:35  [CB] 5분 진입 정지 | 파이프라인 10658ms — 처리 지연
```

- STEP 2(SGD 온라인 학습)에서 10.3초 소요. `partial_fit`이 50건+ 샘플을 한 번에 처리하는 중으로 추정.
- 5분 진입 정지 → 10:35~10:40 진입 불가.
- S2가 지속적으로 1~3초 소요 중 (정상은 <100ms). online_learner scaler `partial_fit`이 매 샘플마다 전체 데이터에 대해 연산 중일 가능성.

### E. 11:14~11:24: STABLE_TREND — 유일한 진입 근접 순간

```
11:14  dir=-1 conf=54.5% < 58.0% → X (-3.5%p)
11:22  dir=-1 conf=54.3% < 58.0% → X (-3.7%p)
11:24  dir=-1 conf=57.1% < 58.0% → X (-0.9%p) ← 최근접!
```

- STABLE_TREND의 min_conf=58%는 레짐별 최저값. 여기서도 통과하지 못했다는 것은 **모델 자체의 신뢰도 상한이 57%에 묶여있다**는 의미.
- 57.1%를 낼 수 있었다면 min_conf를 57%로 낮췄어도 최소 1회 진입은 가능했을 것.

### F. 11:38: Mid-Conf Blind Spot 첫 발동

```
11:38  [Mid-Conf Blind Spot] 7연속 오답 (conf 60%~85%) — CB3 strict 모드 진입
```

- 60~85% 중간 신뢰도 구간에서 7회 연속 오답 → CB3 임계값이 35%→42%로 상향.
- 그러나 acc30m이 이미 20%대라 큰 영향 없음. **이 시점에서 strict 모드로도 진입 상황을 바꾸지 못함**.

### G. 11:50~13:22: OTHER → CB3 HALT

```
11:50  시간대 전환 → OTHER: 기타 구간 — 진입 금지 (min_conf=65%)
```

- OTHER 구간에서도 conf는 35~57% → 65% min_conf에 대폭 미달.

### H. 13:22: CB3 당일 정지 + Contrarian 재ACTIVE

```
13:21  [CB3 경고 1/2] 30분 정확도 16.0% < 35% (strict: 42%)
13:22  [CB] 당일 시스템 정지 | 30분 정확도 15.4%
13:25  [Contrarian] ACTIVE | acc30m=13.8% streak=10 regime=NEUTRAL 역베팅방향=LONG
```

### I. 13:22~15:30: CB3 HALT 상태에서 파이프라인만 지속

- 진입은 차단되었으나 파이프라인은 계속 작동.
- Brier 경고·패널티 지속 → 14:48 Mid-Conf Blind Spot 5차 발동.
- 15:20~15:29 CB5 2565ms 경고. 마지막까지 conf 미달 상태 유지.


---

## 5. 근본 원인 분석

### 원인 1. [모델 구조] 앙상블 신뢰도 상한이 57%로 고정

가장 심각한 문제. 모델이 GAP_OPEN(67%), OPEN_VOLATILE(63%), STABLE_TREND(58%), OTHER(65%) 어떤 시간대에서도 요구 신뢰도에 도달하지 못했다. 이는:
- GBM/SGD가 현재 시장 국면(5/21 NEUTRAL)에서 UP/DOWN을 확신 있게 구분하지 못함
- 6개 호라이즌의 예측이 서로 상쇄되어 confidence가 낮게 유지됨
- 방향은 SHORT로 편향되었지만 확신도는 57%를 넘지 못함

### 원인 2. [데이터 품질] GBM Scaler 완전 노후화

```
ofi_raw=+92.0 (z-score) —   정상 범위 ±4의 23배
microprice_depth_bias=-17.3 — 정상 범위 ±4의 4.3배
queue_depletion_speed=+22.2 — 정상 범위 ±4의 5.5배
```

- `raw_data.db` 마지막 학습 데이터: 5/15. 5/16~5/21 6거래일 데이터 미반영.
- 이 기간 사이 시장 분포가 완전히 시프트 → GBM scaler `fit()` 시점과 현재 데이터가 격리.
- SGD scaler는 `partial_fit()`(67차 수정)으로 적응하지만, **GBM scaler는 여전히 고정**.
- GBM이 앙상블 가중치의 70~90%를 차지 → scaler 노후화가 confidence 전체를 끌어내림.

### 원인 3. [학습 오염] 전장전 5회 재시작 → 온라인 상태 초기화

- `_accuracy_buf`, `_signal_history`, SGD partial_fit 상태가 5번 초기화.
- 매 재시작마다 `BrokerSync` TR 실패 (잔고 rows=0).
- Session recovery가 완전히 이루어지지 않은 상태에서 첫 파이프라인 투입.

### 원인 4. [설계] min_conf가 모델 역량을 초과

NEUTRAL 레짐에서 모델이 HISTORICALLY 낼 수 있는 최대 신뢰도를 반영하지 않고, 고정된 threshold만 적용. 모델이 57%가 한계인데 58~67%를 요구 → 수학적으로 진입이 불가능한 상태.

### 원인 5. [파이프라인] S2(OnlineLearner) 처리량 폭증

```
09:00 S2=2119ms, 09:14 S2=2214ms, 10:35 S2=10316ms, 12:34 S2=2385ms
```

- S2(STEP 2: SGD 온라인 학습)가 지속적으로 2~10초 소모.
- `partial_fit()`이 매 샘플마다 전체 scaler 데이터로 연산 중일 가능성 (67차 수정 부작용).
- 전체 파이프라인이 2~3초로 지연 → 시장 데이터 처리 지연 악순환.

---

## 6. 재발 패턴 분석: 5/19 vs 5/21 vs 5/18

| 항목 | 5/18 | 5/19 | 5/21 |
|------|:---:|:---:|:---:|
| 거래 건수 | 13건 | 0건 (CB3 정지) | **0건 (전일)** |
| CB3 HALT | 없음 | 09:50 | 13:22 |
| acc30m at HALT | -- | 19.0% | 15.4% |
| 레짐 | RISK_ON→NEUTRAL | NEUTRAL | NEUTRAL |
| conf 최대 | 92% | 83% | **57.1%** |
| Contrarian ACTIVE | 없음 | 없음 | 09:13, 09:40 |
| Brier 과신 | 없음 | 없음 | 전일 0.35~0.48 지속 |
| z-score 경고 | some | 반복 | **극심** (ofi+92) |
| 재시작 | 0회 | 3회 (장중) | **5회 (장전)** |
| scaler 상태 | 정상 | 약간 노후 | **심각하게 노후** |

**악화 추세**:
```
5/18: conf 최대 92%, 13건 진입, 승률 84.6% → 정상 운영
5/19: conf 최대 83%, 0건 진입, acc30m 19% 붕괴 → CB3 정지
5/21: conf 최대 57%, 0건 진입, acc30m 15% 붕괴, Contrarian 09:13 ACTIVE → 완전 관망
```

> **5/21이 가장 심각**: conf 상한 자체가 57%로 하락. scaler 노후화와 학습 데이터 격리가 5/18→5/21 사이 급격히 진행된 것으로 추정.

---

## 7. 재발 원인 3종 (깃 히스토리 추적)

| # | 재발 원인 | 히스토리 | 5/21 발현 | 해결안 |
|---|----------|---------|:---:|------|
| 1 | **모델 신뢰도 < min_conf** | 29차(57ed809)→41차(6701e81)→65차(30b8295)에서 지속 개선 시도했으나 **모델 자체의 conf 상한을 올리지 못함** | Y (결정적) | A2: 동적 min_conf + A1: 가중치 재분배 |
| 2 | **Scaler 노후화** | 63차(d0f8255) 극단값 방어는 했으나 **GBM scaler 재적응은 미구현**. 67차(755186e) SGD scaler만 수정 | Y (GBM scaler 6일 미갱신) | B1: GBM scaler partial_fit |
| 3 | **중간 신뢰도 과신** | 60차(db189d3) Mid-Conf Tracker 구현됐으나 **감지만, 교정 없음** | Y (6회 발동, 효과 없음) | A3: Calibration 강제 적용 |

---

## 8. 종합 개선 방안

### Phase A: 즉시 적용 (P0, 3~4시간) — 5/22 장중 적용 목표

#### A1. 앙상블 HorizonDecorrelator 강제 가중치 재분배
**파일**: `model/ensemble_decision.py`

```python
# HorizonDecorrelator.push() 끝에 추가
def push(self, horizon_proba, regime="NEUTRAL"):
    directions = [horizon_proba[h].get("direction", 0) for h in self._horizons]
    if regime == "NEUTRAL" and len(set(directions)) == 1:
        self._direction_streak += 1
        if self._direction_streak >= 8:
            for h in self._horizons:
                if horizon_proba[h]["direction"] == directions[0]:
                    self._weights[h] *= 0.7
                else:
                    self._weights[h] *= 1.3
            self._weights = _renormalize(self._weights)
    else:
        self._direction_streak = 0
```

**효과**: NEUTRAL 고착 시 horizon weights 강제 재분배 → confidence가 35~57%에서 50~65%로 상승 기대.

#### A2. 동적 min_conf threshold (분포 75분위수 기준)
**파일**: `config/settings.py` + `strategy/entry/time_strategy_router.py`

```python
def get_dynamic_min_conf(regime: str, recent_confidences: list) -> float:
    static_base = REGIME_MIN_CONFIDENCE.get(regime, 0.58)
    if len(recent_confidences) < 30:
        return static_base
    p75 = float(np.percentile(recent_confidences, 75))
    return max(0.52, min(p75, static_base))
```

**효과**: 모델이 57%까지만 낼 수 있다면 min_conf도 57%로 자동 하향 → 11:24에 진입 가능했을 것.

#### A3. MultiHorizonCalibrator → 앙상블 강제 연결
**파일**: `main.py` STEP 5~6 사이

```python
calibrated_proba = {}
for h, proba in horizon_proba.items():
    cal_up = self.calibrator.calibrate(h, proba["up"])
    cal_down = self.calibrator.calibrate(h, proba["down"])
    cal_flat = self.calibrator.calibrate(h, proba["flat"])
    total = cal_up + cal_down + cal_flat
    calibrated_proba[h] = {
        "up": cal_up / total, "down": cal_down / total, "flat": cal_flat / total,
        "direction": proba["direction"], "confidence": proba["confidence"],
    }
```

**효과**: Brier 0.476 → 0.25 이하 목표. Platt Scaling이 과신을 줄이고 정직한 확률로 변환.

#### A4. Contrarian ACTIVE → SHADOW 모드 진환 (진입 게이트화)
**파일**: `safety/contrarian_mode.py`

- ACTIVE 상태가 되면 `cb.block_new_entries = True` 연동 (파이프라인은 유지).
- 가상 역베팅 PnL만 집계하고 실진입 차단 → "오늘은 모델이 시장을 이해하지 못한다"는 신호로 활용.

### Phase B: 피처 품질 근본 개선 (P1, 1~2일)

#### B1. GBM Scaler 적응적 partial_fit
**파일**: `model/multi_horizon_model.py`

```python
def predict_proba(self, x: np.ndarray, adapt_scaler: bool = False):
    if adapt_scaler and self._should_adapt(horizon):
        scaler.partial_fit(x2d)
        self._scaler_fitted_at[horizon] = datetime.datetime.now()
```

**효과**: ofi_raw=+92 → 0에 가깝게 정규화. z-score 경고 90%+ 감소.

#### B2. OFI/CVD extreme winsorization
**파일**: `features/technical/ofi.py`, `cvd.py`

```python
P1, P99 = np.percentile(running_values, [1, 99])
return {"ofi_raw": float(np.clip(ofi_raw, P1, P99)),
        "ofi_norm": float(np.clip(ofi_norm, -3.0, 3.0))}
```

**효과**: z>10 경보 소멸. scaler 부담 경감.

#### B3. Microprice depth_bias NaN 가드
**파일**: `features/technical/microprice.py`

```python
if bid_depth <= 0 or ask_depth <= 0:
    return {"microprice_depth_bias": 0.0}
```

**효과**: depth_bias=-17.3 z-score 소멸.

### Phase C: 학술적 방법론 (P2, R&D 검증)

#### C1. Beta-Binomial Bayesian Calibration (Zadrozny & Elkan, 2002)
- Platt Scaling(100샘플 필요) 대체 → 20샘플만 쌓여도 수렴.
- Brier 초기 급등(09:39: 0.393→0.476) 방지.
- 신규: `learning/bayesian_calibrator.py`

#### C2. Regime-Conditional Dynamic Thresholding (Kritzman et al., 2012)
- NEUTRAL 레짐 min_conf = `max(0.52, P75(최근50분conf))`
- `config/settings.py` 확장.

#### C3. SPRT Sequential Probability Ratio Test (Wald, 1945)
- 우도비 누적 검정 → "충분한 증거" 있을 때만 진입.
- 신규: `model/sprt_gate.py` (alpha=0.05, beta=0.10).

#### C4. GBM Scaler Rolling Window Re-fit (매 90분)
- 90분마다 최근 N개 샘플로 scaler 재학습 (partial_fit 아님).
- `learning/batch_retrainer.py` 확장.

---

## 9. 실행 우선순위

### 🔴 P0 — 5/22 장중 적용 목표 (오늘 오후~밤 구현)

| # | 항목 | 파일 | 예상 시간 | 기대 효과 |
|---|------|------|:---:|------|
| P0-1 | 캘리브레이션 강제 연결 | `main.py` STEP 5~6 | 30분 | Brier 0.47→0.25, conf 정직화 |
| P0-2 | 동적 min_conf | `settings.py` + `time_strategy_router.py` | 1시간 | 진입 가능성 회복 (57%→57% 통과) |
| P0-3 | 방향 고착 Horizon 브레이커 | `ensemble_decision.py` | 1시간 | NEUTRAL 고착 해제, conf 상승 |
| P0-4 | GBM scaler 부분 적응 | `multi_horizon_model.py` | 1시간 | z-score 경고 90% 감소 |

### 🟡 P1 — 금주 내

| # | 항목 | 파일 |
|---|------|------|
| P1-1 | OFI/CVD winsorization | `ofi.py`, `cvd.py` |
| P1-2 | Microprice NaN 가드 | `microprice.py` |
| P1-3 | S2 OnlineLearner 처리량 최적화 | `online_learner.py` |
| P1-4 | 전장전 multi-restart 방지 로직 | `main.py` + `cybos_autologin.py` |

### 🟢 P2 — WFA 검증 병행

| # | 항목 | 신규 파일 |
|---|------|------|
| P2-1 | Beta-Binomial 캘리브레이션 | `learning/bayesian_calibrator.py` |
| P2-2 | SPRT 진입 게이트 | `model/sprt_gate.py` |
| P2-3 | GBM scaler rolling window | `learning/batch_retrainer.py` 확장 |

---

## 10. 최종 판단

### 핵심 교훈

1. **min_conf는 모델이 낼 수 있는 신뢰도보다 높으면 진입이 수학적으로 불가능** → 동적 threshold 필수.
2. **GBM scaler는 5거래일 이상 재학습 없으면 노후화가 치명적** → partial_fit 또는 rolling re-fit 필요.
3. **Contrarian 09:13 ACTIVE는 "오늘은 관망하라"는 가장 강력한 신호** — 이를 진입 게이트로 활용해야 함.
4. **캘리브레이션은 기록만 하고 적용하지 않으면 무의미** — Brier 0.47이 증명.

### 한 줄 요약

> **"고정된 min_conf가 57%인 모델에게 58%를 요구했고, 캘리브레이션은 기록만 하고 적용되지 않았으며, scaler는 6일째 얼어붙은 상태였다. P0-1~4로 이 세 가지를 동시에 해결해야 5/22에 진입이 재개된다."**

---

## 11. Contrarian Mode 실전 연결 검토

### 현재 상태
- 09:13 첫 ACTIVE, 09:40 재ACTIVE, 13:25 재ACTIVE
- 가상모드 (`enable_real_order=False`) → 모의투자 PnL 집계 중

### 실전 연결 조건 제안
1. 모의투자 누적 30건 이상
2. 가상 승률 >= 65%
3. 1일 최대 2회, 1회 1계약으로 제한
4. 당일 Contrarian 실주문 손실 누적 >= 3pt 시 그날 Contrarian 중지

**5/21 가상 역베팅(LONG) 결과**: Contrarian이 LONG을 제안했고, CB3 HALT 시 역베팅방향=LONG (모델은 SHORT). 실제 시장 상승세라면 Contrarian 가상 PnL은 (+)일 가능성.

---
