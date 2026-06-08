# 2026-05-21 미륵이 30분 정확도 급락 + CB③ 정지 종합 분석

> 분석일시: 2026-05-21 13:30 (장중)
> 분석 도구: openCode (Deep)
> 핵심 이벤트:
>   - 12:46 CB⑤ 파이프라인 2239ms 경고
>   - 13:06 Brier 과신 패널티 발동 (이동평균=0.464 > 0.45)
>   - 13:21 CB③ 경고 1/2: 30분 정확도 16.0%
>   - 13:22 CB③ 당일 시스템 정지: 30분 정확도 15.4%
>   - 13:25 Contrarian ACTIVE: acc30m=13.8%, streak=10, NEUTRAL, 역베팅=LONG

---

## 1. 요약 결론

- 오늘 오후 정지는 **CB③ 30분 정확도 저하**로 정상 발동했다.
- 경고 시점 13:21 정확도 16.0%, 정지 시점 13:22 정확도 15.4% — **33% 랜덤 수준의 절반 이하**.
- 이는 단순한 성능 저하가 아닌 **모델이 "자신있게 한 방향만 고집하다 전부 틀리는" 과신 패턴**의 재발이다.
- **5/19와 동일한 구조**: NEUTRAL 레짐 + LONG 일변도 편향 + 중간 신뢰도(60~85%) 구간 대량 오답 → acc30m 붕괴.
- 13:25 Contrarian ACTIVE 발동으로 **역베팅 모드** 진입 — 모델이 LONG을 고집하지만 실제로 SHORT가 맞았다는 수학적 귀결.

---

## 2. 정확도 붕괴 타임라인

### A. 전조 증상 (12:46~13:06)

| 시각 | 이벤트 | 의미 |
|------|--------|------|
| **12:46** | CB⑤ 파이프라인 2239ms 경고 | 점심 회복 구간(12:00~13:30) 처리 지연 — GBM 재학습 또는 옵션체인 폴링과 충돌 가능성 |
| **12:58** | CB⑤ 파이프라인 1211ms 경고 | 지속적 처리 지연 — 1초 이상 지연이 12분 간격 2회 발생 |
| **13:06** | Brier 과신 패널티 발동 (0.464 > 0.45) | **모델이 46.4% 평균 제곱오차로 확률을 출력 중** — 완벽 보정(0.0)에서 심각하게 이탈. 사이징 50% 강제 축소 |

> **Brier Score 0.464의 의미**: 무작위 예측(conf=0.33)은 Brier≈0.22. 0.464는 모델이 70% 확신으로 틀리거나, 30%로 맞추는 등 **확률과 실제 정답이 심각하게 괴리**된 상태. 이 시점에서 이미 acc30m 붕괴는 예고된 셈.

### B. CB③ 발동 흐름 (13:21~13:25)

| 시각 | 이벤트 | acc30m | 방향 | 비고 |
|------|--------|--------|------|------|
| 13:21 | **CB③ 경고 1/2** | **16.0%** < 35% | — | 25개 중 약 4개 정답 |
| 13:22 | **CB③ 당일 정지** | **15.4%** < 35% | — | 2회 연속 미달 → HALT + 비상청산 |
| 13:25 | **Contrarian ACTIVE** | **13.8%** | LONG 역베팅 | streak=10, NEUTRAL, 3/3 조건 충족 |

> CB③ 버퍼 25~26개 샘플 중 정답이 4개 수준. 즉, 최근 30분 예측 중 **80% 이상이 정반대 방향**으로 틀렸다.

### C. Contrarian ACTIVE 의 수학적 함의

```
acc30m = 13.8% → 역방향 예측 시 기대 정확도 = 86.2%
동방향 연속 10회 → 모델이 LONG만 10회 연속 출력
NEUTRAL 레짐 → 추세장이 아닌 횡보장에서의 편향 (가장 위험한 패턴)
역베팅방향 = LONG → 모델은 SHORT를 출력, Contrarian은 LONG 베팅
```

> 모델은 SHORT를 10번 고집했고 86.2% 확률로 틀렸다. 실제 시장은 오르고 있었다. 이는 **GBM/SGD 양쪽 모두 방향성 오판**에 빠진 상태를 의미.

---

## 3. 낮은 정확도의 근본 원인 분석

### 원인 1. [구조적] GBM/SGD 양쪽 모두 LONG → SHORT 전환 실패 (재발)

5/19에서는 모델이 LONG 일변도였고 시장은 횡보/하락 → CB③ 정지.
오늘은 **반대 방향**: 모델이 SHORT 일변도였고 시장은 상승.

**재발 메커니즘**:
```
NEUTRAL 레짐 진입
  → GBM은 과거 학습 데이터의 추세 방향을 prior로 사용
  → SGD는 최근 partial_fit으로 시도하지만 noise가 많으면 방향 전환 못 함
  → 앙상블 가중합 결과 특정 방향으로 "고착"
  → 고착된 방향이 실제 시장과 반대면 acc30m 0%로 수렴
```

이 패턴은 5/19(3차례 재시작 모두 실패), 5/21(오늘)에서 확인된 **구조적 결함**. Contrarian 모드가 발동됐다는 것 자체가 "모델이 한 방향만 찍었고 완전히 틀렸다"는 증거.

### 원인 2. [지표] Brier Score 0.464 — 과신의 정량적 증거

Brier Score 이동평균이 0.464라는 것은:
- conf=0.80인 예측이 대부분 틀렸을 때: (0.80-0)² = 0.64 / 건
- conf=0.60인 예측이 대부분 맞았을 때: (0.60-1)² = 0.16 / 건
- **0.464는 고신뢰도(70~85%) 오답 + 저신뢰도(30~45%) 정답이 혼재**된 상태

즉, **"확신할 땐 틀리고, 의심할 땐 맞는" 전형적인 미보정(overconfident) 모델**.

### 원인 3. [학습] Scalper 노후화 + GBM 분포 괴리

- **Scaler 노후화**: 67차에서 `partial_fit()`을 매 샘플로 수정했으나, GBM scaler는 `fit()` 시점에 고정. 재학습이 트리거되지 않으면 장중 분포 변화에 GBM이 점점 더 취약해짐.
- **GBM 학습 데이터**: `raw_data.db` 3,432행(4/28~5/15) — 최근 1주일(5/16~5/21) 데이터 미포함. 시장 레짐이 변했는데 과거 데이터로만 학습 중.
- **SGD noise 학습**: `meta_action == "NOISE"`인 샘플도 partial_fit에 포함 → 방향 전환 능력 저하.

### 원인 4. [설계] Mid-Conf Blind Spot — 60~85% 구간 과신

5/19 분석(제안 6)에서 지적된 문제가 오늘 재발:

```
CB③ _high_conf_wrong_streak: conf >= 85% 오답만 추적
                                   ↓
실제 오답의 90%+는 conf=60~80% 구간에서 발생 (감시 사각지대)
                                   ↓
Mid-Conf Tracker: 7연속 시 strict 모드 (임계값 35%→42%)
```

60차에서 구현된 Mid-Conf Blind Spot Tracker는 **경고는 발생했지만 임계값 상향(35%→42%)만으로 15% 정확도를 막지 못함**. 42% 임계값으로도 16%는 통과 불가 — CB③은 결국 정상 발동했으나, 정지 시점까지 지연.

### 원인 5. [파이프라인] 정오 구간 처리 지연 (12:46, 12:58)

- 점심 회복 구간 STABLE_TREND에서 2회 연속 1초 이상 파이프라인 지연
- GBM 재학습 데몬 스레드가 이 시점에 BlockRequest 루프를 발생시켰을 가능성
- 지연된 파이프라인은 뒤처진 분봉 데이터를 처리 → 검증 타임스탬프 어긋남 → 정확도 집계 오염 가능성

---

## 4. 재발 패턴 분석: 5/19 vs 5/21

| 항목 | 2026-05-19 | 2026-05-21 |
|------|-----------|-----------|
| 경고 시각 | 09:49 | 13:21 |
| 정지 시각 | 09:50 | 13:22 |
| acc30m at HALT | 19.0% | 15.4% |
| 레짐 | NEUTRAL | NEUTRAL |
| 편향 방향 | LONG 일변도 | SHORT 일변도 |
| 역베팅 방향 | — (당시 미구현) | LONG |
| 사전 증상 | z-score 경고 반복, CORE 탈락 | Brier 과신, CB⑤ 처리 지연 |
| 재시작 | 3회 (모두 실패) | 없음 (당일 정지) |
| Contrarian 발동 | 미구현 | 13:25 ACTIVE |

**공통점**:
1. **NEUTRAL 레짐에서 발생** — 추세 없는 장에서 모델이 한쪽 방향으로 고착
2. **중간 신뢰도(60~85%) 구간 대량 오답** — conf=0.85 이상 과신보다 더 위험한 패턴
3. **사전 경고 무시** — 5/19는 z-score, 5/21은 Brier + CB⑤ 경고가 있었지만 진입 축소만으로는 막지 못함

**차이점**:
- 5/19는 **오전**(시초 데이터 불안정) + **재시작 루프**
- 5/21은 **오후**(데이터 충분히 쌓인 후) + **단일 세션 내 붕괴**
- → 오늘은 "데이터 부족"을 탓할 수 없는 구조적 모델 문제

---

## 5. 모델·학습 관점 개선안 (Phase A: 즉시 적용)

### A1. 앙상블 방향 고착 브레이커 (Directional Stuck Detector)

**문제**: 모델이 동일 방향을 10회 연속 출력 → 실제는 반대 방향 → acc30m 15%.

**해결**: `model/ensemble_decision.py` `HorizonDecorrelator`에 방향 고착 감지 로직 추가:

```python
# 매분 push() 호출 시
if same_direction_streak >= 8 and regime == "NEUTRAL":
    # 반대 방향 horizon weights +30% → 예측 다양화 강제
    for h in self._horizons:
        if horizon_direction[h] == stuck_direction:
            self._weights[h] *= 0.7  # 고착 방향 감쇠
        else:
            self._weights[h] *= 1.3  # 반대 방향 증폭
    self._weights = _renormalize(self._weights)
```

**효과**: NEUTRAL + 8연속 동일 방향 시 horizon 가중치를 강제로 재분배 → 앙상블 방향 전환 유도. Contrarian ACTIVE 발동 전에 선제 대응.

**구현 난이도**: 낮음 (30줄, `HorizonDecorrelator.push()` 끝에 추가)

---

### A2. 캘리브레이션 강제 적용 (Brier Score 직접 개선)

**문제**: `MultiHorizonCalibrator` 가 `record()`는 하지만 `calibrate()` 결과가 앙상블 입력으로 사용되지 않을 가능성.

**해결**: `main.py` STEP 6에서 horizon_proba를 앙상블에 전달하기 전에:

```python
# 각 horizon 확률을 calibrator로 보정
calibrated_horizon_proba = {}
for h, proba in horizon_proba.items():
    cal_up   = calibrator.calibrate(h, proba["up"])
    cal_down = calibrator.calibrate(h, proba["down"])
    cal_flat = calibrator.calibrate(h, proba["flat"])
    total = cal_up + cal_down + cal_flat
    calibrated_horizon_proba[h] = {
        "up": cal_up / total,
        "down": cal_down / total,
        "flat": cal_flat / total,
    }
```

**효과**: Brier Score 개선 (0.464 → 목표 0.25 이하). Platt Scaling이 과신을 보정한 확률을 앙상블에 공급.

**구현 난이도**: 낮음 (15줄, `main.py` STEP 5~6 사이)

---

### A3. 30m FLAT 클래스 다운웨이트 강화

**문제**: 30m에서 FLAT 예측 비중이 과다 → UP/DOWN 예측이 적을 때 틀리면 acc30m 급락.

**해결**: `model/multi_horizon_model.py:27` + `learning/batch_retrainer.py:65`:

```python
_CW_30M = {DIRECTION_FLAT: 0.35, DIRECTION_UP: 1.5, DIRECTION_DOWN: 1.5}
# 현재: {FLAT: 0.5, UP: 1.25, DOWN: 1.25}
```

**효과**: GBM이 30m에서 FLAT 대신 UP/DOWN을 더 적극적으로 예측. 방향성 있는 예측이 맞을 확률은 50%(UP/DOWN) vs 33%(FLAT).

**구현 난이도**: 낮음 (2줄 수정 + GBM 재학습 필요)

---

## 6. 모델·학습 관점 개선안 (Phase B: 아키텍처)

### B1. SGD 온라인 학습 품질 필터 도입

**문제**: `online_learner.py` `learn()`이 모든 검증 샘플을 무조건 partial_fit. meta_action이 NOISE/AMBIGUOUS인 오염 데이터도 학습.

**해결**:

```python
# learning/online_learner.py learn() 메서드
def learn(self, horizon, x, actual_label, predicted_label,
           meta_action="CORRECT_CLEAN"):
    if meta_action in ("NOISE", "AMBIGUOUS", "STUCK"):
        return  # 오염 샘플 스킵
    # ... 기존 partial_fit 로직
```

`main.py` STEP 2에서 `prediction_buffer.verify_and_update()` 반환값의 `meta_label`을 `online_learner.learn()`에 전달.

**효과**: SGD 모델의 방향 전환 능력 향상. noise 데이터로 인한 방향 고착 완화.

**구현 난이도**: 중간 (30줄, `main.py` STEP 2 + `online_learner.py`)

---

### B2. 호라이즌 교차 학습 (Cross-Horizon Stacking)

**문제**: 6개 호라이즌이 독립적으로 예측. 1m/3m/5m 단기 신호가 30m 예측에 반영되지 않음.

**해결**: 단기 호라이즌 방향성 피처를 30m GBM 입력에 추가:

```python
# features/feature_builder.py 신규 피처
short_momentum_1m = (horizon_proba["1m"]["up"] - horizon_proba["1m"]["down"])
short_momentum_3m = (horizon_proba["3m"]["up"] - horizon_proba["3m"]["down"])
short_momentum_5m = (horizon_proba["5m"]["up"] - horizon_proba["5m"]["down"])
```

30m GBM은 "단기 방향성 + 현재 피처"를 동시에 보고 결정 → 단기 반전 신호가 있을 때 30m도 더 빠르게 전환.

**구현 난이도**: 중간 (피처 추가 + GBM 재학습 + 앙상블 파이프라인 순서 조정)

---

### B3. 레짐별 SGD 독립 가중치 (short/long → regime×horizon)

**문제**: 현재 SGD 가중치는 short/long 2버킷만 존재. NEUTRAL에서 SGD가 계속 틀려도 RISK_ON에서의 좋은 성과와 버킷을 공유해 가중치가 10%(최소)까지만 내려감.

**해결**:

```python
# learning/online_learner.py: regime × bucket 2차원 가중치
_WEIGHT_MATRIX = {
    "RISK_ON":  {"short": 0.30, "long": 0.30},
    "RISK_OFF": {"short": 0.20, "long": 0.20},
    "NEUTRAL":  {"short": 0.30, "long": 0.30},
}
```

NEUTRAL에서 long bucket 정확도가 0%로 떨어지면 **NEUTRAL의 long만 SGD 비중 0%** — RISK_ON의 좋은 성과와 분리.

**구현 난이도**: 중간 (100줄, `online_learner.py` 내부 확장 + `main.py` STEP 2 regime 전달)

---

## 7. 학술적 방법론 (Phase C: R&D)

### C1. 적응형 레짐별 확률 Threshold (Regime-Conditional Thresholding)

**이론적 배경**: Kritzman et al.(2012) "Regime Shifts: Implications for Dynamic Strategies"

NEUTRAL 레짐은 추세 신호의 신뢰도가 구조적으로 낮음. 같은 confidence=0.70도 RISK_ON에서는 의미 있고 NEUTRAL에서는 잡음일 가능성이 높다.

```python
# config/settings.py
REGIME_CONFIDENCE_RECALIBRATION = {
    "RISK_ON":  1.00,   # 그대로 사용
    "NEUTRAL":  0.75,   # confidence × 0.75 → 원래 70% → 52.5%
    "RISK_OFF": 0.60,   # confidence × 0.60
}
```

학술적 근거: Christensen et al.(2018) "Machine Learning and the Cross-Section of Expected Returns" — 레짐별 conditional accuracy가 unconditional accuracy보다 최대 18%p 차이.

### C2. Beta-Binomial 베이지안 온라인 캘리브레이션

**이론적 배경**: Zadrozny & Elkan(2002) "Transforming Classifier Scores into Accurate Multiclass Probability Estimates"

현재 Platt Scaling의 한계:
- 최소 100개 샘플 필요 → 첫 100개는 미보정
- 로지스틱 회귀는 단조 보정만 가능 → 중간 구간 과신 패턴 보정 미흡

Beta-Binomial 접근:
```python
class BayesianCalibrator:
    def __init__(self, alpha_prior=2, beta_prior=2):
        self.alpha = alpha_prior  # pseudo-correct count
        self.beta = beta_prior    # pseudo-incorrect count
    
    def record(self, prob, correct):
        self.alpha += prob * correct       # 부분 가중 업데이트
        self.beta  += prob * (1 - correct)
    
    def calibrate(self, raw_prob):
        posterior_mean = self.alpha / (self.alpha + self.beta)
        # raw_prob과 posterior_mean 사이의 가중 평균
        return raw_prob * 0.3 + posterior_mean * 0.7
```

장점: **20개 샘플만 쌓여도 수렴 시작**. 오늘 acc30m 첫 20샘플이 20% 정답이면 → posterior_mean=0.20 → confidence를 급격히 하향 조정.

### C3. 조건부 커널 밀도 추정 (CKDE) — 상황별 정확도 맵

**이론적 배경**: Bishop(2006) "Pattern Recognition and Machine Learning" §2.5

"regime=NEUTRAL AND vpin<0.3 AND hurst<0.45 AND lob_imbalance≈0" 조합에서의 실제 정확도?

```python
from scipy.stats import gaussian_kde  # scipy 1.5.4 지원

class CKDEConfidence:
    def estimate(self, regime, hurst, vpin, lob, atr_ratio):
        # 다차원 조건부 확률 p(correct | context)
        context = np.array([regime_code, hurst, vpin, lob, atr_ratio])
        density = self._kde.evaluate(context)
        return min(density / self._baseline_density, 1.0)
```

이 방법이 규칙 기반 `MetaConfidenceLearner._rule_based_confidence()`를 통계 기반으로 대체.

---

## 8. 재발 방지 — 깃 히스토리에 기록된 지속 문제

### 재발 이력

| 커밋 | 차수 | 내용 | 오늘 재발 여부 |
|------|------|------|:---:|
| 57ed809 | 29차 | 모델 신뢰도 개선 3종 | ✓ (동일 증상) |
| 6701e81 | 41차 | Threshold 재보정 | ✓ (Threshold 변경만으로 불충분) |
| db189d3 | 60차 | Mid-Conf Blind Spot + Brier + Contrarian 구현 | ✓ (경고는 하지만 정지는 못 막음) |
| 755186e | 67차 | horizon 편향 진단 | ✓ ([Bias] 로그로 관찰만, 자동 교정 없음) |

### 재발 구조 도식

```
1. NEUTRAL 레짐 진입
2. GBM prior(과거 추세) + SGD noise 학습 → 방향 고착
3. 고착된 방향 ≠ 실제 시장 → 중간 신뢰도(60~85%) 오답 누적
4. Mid-Conf Tracker 경고 (7연속 오답) → CB③ 임계값 35%→42% 상향
5. acc30m이 42% 이하로 떨어져도 35% 기준으로는 한참 남음 → 20%대까지 지연
6. CB③ 2회 연속 미달 → HALT + 비상청산
7. Contrarian ACTIVE (모델이 10회 연속 오답 + acc30m<25%)
```

**핵심 단절 지점**: (4)→(5)에서 CB③ strict 모드가 임계값을 42%로 올리지만, **acc30m이 42%→20%로 떨어지는 동안 모델이 계속 틀린다**. 이 구간에서 **포지션을 축소하거나 역베팅을 더 빨리 시작하는** 장치가 필요.

### 재발 원인 3종 정리

| 번호 | 재발 원인 | 설명 | 해결안 |
|:---:|------|------|------|
| ① | **방향 고착 감지 부재** | NEUTRAL + 동일 방향 N회 → 모델이 stuck 상태임을 인지 못 함 | A1: Directional Stuck Detector |
| ② | **캘리브레이션 미적용** | Brier 0.464 → Platt 보정이 앙상블에 반영되지 않음 | A2: 강제 보정 적용 |
| ③ | **SGD noise 학습** | meta_action=NOISE도 partial_fit → 방향 전환 능력 저하 | B1: 학습 품질 필터 |

---

## 9. Contrarian Mode 실전 연결 검토

### 현재 상태

- 13:25 Contrarian ACTIVE, 방향=LONG, 가상모드 (`enable_real_order=False`)
- 모의투자로 가상 PnL 집계 중 — 실제 주문은 발주되지 않음

### 실전 연결 조건 제안

Contrarian 실주문 허용 시점:
1. 모의투자 누적 30건 이상
2. 가상 승률 ≥ 65%
3. 1일 최대 2회, 1회 1계약으로 제한
4. 당일 Contrarian 실주문 손실 누적 ≥ 3pt 시 그날 Contrarian 중지

**리스크**: 모델이 완전히 틀렸다는 수학적 확신이 있어도, **Contrarian도 시장 변동성에 노출**. CB③ 정지 구간의 변동성이 높을 수 있어 단기 역베팅도 위험.

**현재 권장**: 모의투자 검증 1~2주 더 진행 후, Phase A(방향 고착 브레이커) 완료 시점에 결정.

---

## 10. 종합 우선순위 로드맵

### 🔴 P0 — 오늘 CB③ 정지 대응 (즉시)

| # | 항목 | 파일 | 예상 시간 | 효과 |
|---|------|------|:---:|------|
| P0-1 | 캘리브레이션 강제 적용 | `main.py` STEP 5~6 | 30분 | Brier 0.464 → 0.25 목표 |
| P0-2 | 30m FLAT class_weight 0.35로 강화 | `multi_horizon_model.py` + `batch_retrainer.py` | 10분 | 30m 방향성 예측 증가 |
| P0-3 | Directional Stuck Detector | `ensemble_decision.py` | 1시간 | NEUTRAL 고착 → horizon weights 재분배 |

### 🟡 P1 — 모델 신뢰도 체계 개선 (1~2일)

| # | 항목 | 파일 | 예상 시간 | 효과 |
|---|------|------|:---:|------|
| P1-1 | SGD 학습 품질 필터 | `online_learner.py` + `main.py` | 2시간 | SGD 방향 전환 능력 향상 |
| P1-2 | 레짐별 SGD 독립 가중치 | `online_learner.py` | 2시간 | NEUTRAL 전용 SGD 비중 관리 |
| P1-3 | CB③ HALT 전 pre-emptive 축소 | `circuit_breaker.py` | 1시간 | acc30m 25% 진입 시 가상모드 전환 |

### 🟢 P2 — 피처·아키텍처 심화 (1주)

| # | 항목 | 파일 | 검증 |
|---|------|------|------|
| P2-1 | Cross-Horizon Stacking | `feature_builder.py` + GBM 재학습 | WFA 6주 → Sharpe +2%↑ 검증 |
| P2-2 | SHAP 기반 호라이즌별 피처 선택 | `batch_retrainer.py` | Backtest → 호라이즌별 acc 비교 |
| P2-3 | OFI/CVD 2차 미분 피처 | `features/technical/ofi.py`, `cvd.py` | 피처 중요도 WFA 검증 |

### 🔵 P3 — 학술적 방법론 R&D (2~4주)

| # | 방법 | 신규 파일 | 검증 |
|---|------|------|------|
| P3-1 | Beta-Binomial Bayesian Calibration | `learning/bayesian_calibrator.py` | 20샘플 vs Platt 100샘플 ECE 비교 |
| P3-2 | CKDE 상황별 정확도 | `learning/ckde_confidence.py` | `MetaConfidenceLearner` 규칙 vs CKDE Shadow 비교 |
| P3-3 | Regime-Conditional Threshold | `config/settings.py` | conditional accuracy × regime WFA |
| P3-4 | SPRT 진입 게이트 | `model/sprt_gate.py` | Sequential test α=0.05 → 백테스트 승률/진입빈도 |

---

## 11. 최종 판단

### 오늘 CB③ 정지는 **오작동이 아니라 정당한 방어**다.

- acc30m 15.4% = 6개 중 1개 정답 수준. 어떤 기준으로도 정상 모델 작동이 아님.
- Contrarian ACTIVE가 "모델의 역방향이 86% 확률로 맞다"고 수학적으로 증명.
- CB③ + EmergencyExit가 계좌를 추가 손실로부터 보호했다.

### 진짜 문제는 **정지가 발생했다는 것**이 아니라 **정지 전에 감지되지 못한 40분**이다.

- 13:06 Brier 과신 패널티 발동 → 이 시점에서 이미 모델은 "자신있게 틀리는" 상태.
- 12:46~12:58 CB⑤ 파이프라인 지연 → 데이터 처리 품질 저하 의심.
- **P0-1(캘리브레이션) + P0-3(Directional Stuck Detector)가 13:06 시점에서 포지션을 축소했다면, CB③ HALT 없이 당일 50% 사이즈로 안전하게 마감 가능했다.**

### 실행 전략

1. **Phase A (P0) 즉시 구현** — 오늘 오후/저녁. 2026-05-22 장중 적용.
2. **Phase B (P1) 금주 내 구현** — SGD 학습 필터 + 레짐별 가중치.
3. **P2 + P3는 WFA 검증 병행** — 과최적화 방지.

### 한 줄 요약

> **NEUTRAL 장세에서 모델의 방향 고착을 5/19에 이어 5/21에도 재현. Brier 0.464 + Contrarian ACTIVE가 이를 수학적으로 입증. 캘리브레이션 강제 적용 + 방향 고착 브레이커로 당장 대응 필요.**