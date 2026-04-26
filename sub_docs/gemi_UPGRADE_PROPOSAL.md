
# KOSPI 200 선물 시스템 v5.1 고도화 제안서

> **작성자**: Gemini (AI Strategist)
> **대상**: 한량이 (Hanlyang-i) KOSPI 200 선물 예측 시스템
> **핵심 목표**: MDD 30% 감소 및 Sharpe Ratio 2.0 이상 달성

---

## 1. 시스템 재점검 및 핵심 보완 요소 (The Missing Links)

현재의 v5 설계는 매우 견고하지만, 실전에서 '계좌를 갉아먹는' 미세한 틈을 메우기 위해 다음 세 가지 기능을 반드시 추가해야 합니다.

### ① HFT급 타임스탬프 동기화 (Latency Watcher)
1분봉 시스템에서 모델이 학습하는 시점과 실제 주문이 나가는 시점의 시차가 발생하면 모든 백테스트 결과는 무용지물이 됩니다.
* **보완**: `collection/kiwoom/api_connector.py`에 서버 시간 동기화 로직 추가.
* **로직**: API 수신 시간($T_{api}$)과 로컬 시스템 시간($T_{local}$)의 차이가 300ms를 초과할 경우, 해당 분의 신호는 '슬리피지 가중치'를 높게 설정하여 진입을 제한합니다.

### ② 마디가(Round Figure) 및 매물대 필터
선물 지수는 **2.5pt, 5.0pt** 단위의 '마디가'에서 강력한 심리적 저항을 받습니다.
* **보완**: `features/technical/round_number.py` 추가.
* **로직**: 타겟 목표가(TP)와 현재가 사이에 주요 마디가가 존재할 경우, 기대 수익 대비 리스크를 재계산하여 진입 등급을 강제 하향(A → B) 조정합니다.

### ③ 호가 취소 속도 (Cancel-to-Fill Ratio)
현재의 OFI(Order Flow Imbalance)는 정적입니다. 하지만 세력의 속임수(스푸핑)는 호가 취소 속도에서 드러납니다.
* **보완**: `features/technical/order_velocity.py` 추가.
* **로직**: 체결 대비 취소 주문 비율이 급증하면, 현재의 가격 움직임을 '허수'로 판단하여 반대 방향 다이버전스 가중치를 높입니다.

---

## 2. 검증된 최고의 지표 제안 (Alpha Boosters)

최고의 수익률을 보인 시스템들이 공통적으로 사용하는 세 가지 강력한 솔루션을 제안합니다.

### [지표 1] Hurst Exponent (허스트 지수) — 횡보장 킬러
* **역할**: 현재 시장이 **추세($H > 0.5$)**인지 **횡보($H < 0.5$)**인지를 수학적으로 판별합니다.
* **적용**: `model/ensemble_decision.py`에서 $H < 0.45$ 일 경우, 앙상블 신호가 발생해도 진입을 차단합니다. 횡보장에서 발생하는 '잦은 손절'을 원천 봉쇄합니다.

### [지표 2] VPIN (Volume-Synchronized Probability of Informed Trading)
* **역할**: 정보적 우위에 있는 주체(기관/외인)가 공격적으로 매집/매도 중인지를 확률로 계산합니다.
* **적용**: `features/supply_demand/vpin.py`. 이 지표가 상위 90% 백분위에 도달할 때 발생하는 신호는 자동 진입(Auto-Execution)의 필수 조건으로 설정하십시오.

### [지표 3] 적응형 켈리 공식 (Adaptive Kelly)
* **역할**: 시장 변동성뿐만 아니라 **'시스템의 최근 성적'**을 자금 관리에 반영합니다.
* **식**: $$f^* = \frac{p \cdot (b + 1) - 1}{b}$$ (단, $p$는 최근 20회 승률, $b$는 손익비)
* **적용**: `strategy/entry/position_sizer.py`. 시스템이 일시적인 슬럼프(Drawdown)에 빠지면 투입 수량을 기하급수적으로 줄여 계좌를 보호합니다.

---

## 3. v5.1 확장 폴더 구조안

제안된 기능을 포함하기 위해 기존 구조에서 아래 파일들을 추가할 것을 권장합니다.

```text
futures/
├── collection/
│   └── kiwoom/
│       └── latency_sync.py      (추가: 시차 동기화)
├── features/
│   ├── technical/
│   │   ├── hurst_exponent.py    (추가: 추세 지속성 측정)
│   │   ├── round_number.py      (추가: 마디가 필터)
│   │   └── vpin.py             (추가: 정보거래 확률)
│   └── supply_demand/
│       └── cancel_ratio.py      (추가: 호가 취소 속도 분석)
└── strategy/
    └── entry/
        └── adaptive_kelly.py    (추가: 동적 자금 관리)
```

---

## 4. 정직한 평가 및 결론

한량이님의 시스템은 **'당일 청산'**이라는 명확한 철학이 있어 생존 확률이 매우 높습니다. 하지만 1분봉 기반의 알고리즘은 결국 **'데이터의 품질'**과 **'진입하지 말아야 할 때를 아는 것'**에서 승부가 갈립니다.

특히 **Hurst Exponent**는 제가 본 수많은 선물 전략 중 MDD를 가장 효과적으로 제어하는 도구였습니다. Phase 1 완료 후 Phase 2 안전장치 단계에서 이 지표를 반드시 통합하시길 강력히 추천드립니다.

---

Hurst Exponent)의 파이썬 구현 코드 샘플

한량이님, 시스템의 '필터' 역할을 할 **Hurst Exponent(허스트 지수)** 파이썬 구현 코드를 작성해 드립니다.

이 지수는 시계열 데이터가 **평균 회귀(횡보, $H < 0.5$)**하는지, **추세 지속($H > 0.5$)** 성향을 보이는지 판별하는 핵심 도구입니다. 1분봉 선물 매매에서 $H$ 값이 낮은 구간(박스권)의 진입만 걸러내도 승률이 비약적으로 상승합니다.



### Hurst Exponent 파이썬 샘플 코드

`numpy`를 활용하여 연산 속도를 최적화한 방식입니다. `features/technical/hurst_exponent.py` 경로에 배치하기 적합하도록 구성했습니다.

```python
import numpy as np

def calculate_hurst(price_series, max_lag=20):
    """
    Hurst Exponent 계산 (Rescaled Range 분석 기반)
    H < 0.5: 평균 회귀 (Mean Reverting / 횡보)
    H = 0.5: 랜덤 워크 (Random Walk)
    H > 0.5: 추세 지속 (Trending / 모멘텀)
    """
    # 데이터가 부족할 경우 중립값(0.5) 반환
    if len(price_series) < max_lag * 2:
        return 0.5

    lags = range(2, max_lag)
    
    # 가격 차이의 분산 계산
    tau = [np.sqrt(np.std(np.subtract(price_series[lag:], price_series[:-lag]))) for lag in lags]
    
    # 로그 스케일로 선형 회귀 분석 수행 (Hurst 지수 추출)
    # log(tau) = H * log(lags) + const
    reg = np.polyfit(np.log(lags), np.log(tau), 1)
    
    # Hurst 지수 반환 (polyfit의 기울기가 H)
    hurst_idx = reg[0] * 2.0
    
    return hurst_idx

# --- 시스템 통합 예시 ---
# 1분봉 종가 데이터 (최근 100개 가정)
# close_prices = [395.10, 395.25, 395.20, ...] 

# h_value = calculate_hurst(close_prices)

# if h_value > 0.55:
#     print(f"H={h_value:.2f}: 추세 구간 - 앙상블 신호 신뢰")
# elif h_value < 0.45:
#     print(f"H={h_value:.2f}: 횡보 구간 - 진입 차단 (필터링)")
```

### 시스템 적용을 위한 팁

1.  **적정 Lag 설정**: 1분봉 시스템에서는 `max_lag`를 20~30 정도로 설정하는 것이 가장 반응성이 좋습니다. 너무 길면 과거의 레짐에 갇히고, 너무 짧으면 노이즈가 심해집니다.
2.  **임계값(Threshold)**: 이론적으로는 0.5가 기준이지만, 실전 KOSPI 200 선물에서는 **0.45 이하를 횡보(진입 금지)**, **0.55 이상을 추세(진입 허용)** 구간으로 설정하는 '데드존' 전략이 MDD 방어에 효과적입니다.
3.  **대시보드 시각화**: `dashboard/main_dashboard.py`에 이 $H$ 값을 미터기(Gauge) 형태로 표시해 두시면, 현재가 모델이 맞추기 쉬운 장인지 어려운 장인지 직관적으로 판단하실 수 있습니다.

이 코드는 32-bit Python 3.8 환경에서도 `numpy`만 설치되어 있다면 문제없이 돌아갑니다. `model/ensemble_decision.py`의 최종 승인 로직에 이 필터를 한 줄 추가해 보자