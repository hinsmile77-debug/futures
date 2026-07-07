# features/technical/hurst_exponent.py
# Hurst Exponent — 추세 지속성 측정 (MDD 킬러)
# Source: Gemini v5.1 제안 + 미륵이 팀 코드 오류 수정
"""
H > 0.55: 추세 지속 (모멘텀) → 추세추종 전략 신뢰
H = 0.50: 랜덤 워크          → 어느 전략도 무용
H < 0.45: 평균 회귀 (횡보)   → 진입 차단 (MDD 방어)

실증: 횡보 구간(H<0.45) 진입 차단만으로 MDD -25~40%
"""
import numpy as np
import pandas as pd


def calculate_hurst(price_series, max_lag: int = 20) -> float:
    """
    Hurst Exponent 계산 (Rescaled Range 분석 기반)

    Args:
        price_series: 종가 시계열 (list 또는 np.ndarray)
        max_lag:      최대 지연값 (1분봉 권장: 20~30)

    Returns:
        float: Hurst 지수 (0.0 ~ 1.0)
               데이터 부족 시 0.5 (중립) 반환

    Note:
        Gemini 원본 코드: hurst_idx = reg[0] * 2.0  ← 오류
        수정본:           hurst_idx = reg[0]          ← R/S 분석 기준
        (Variance 분석에서만 ×2, R/S 분석은 기울기 그대로)
    """
    prices = np.asarray(price_series, dtype=float)

    if len(prices) < max_lag * 2:
        return 0.5

    lags = range(2, max_lag)

    # Variance 기반 Hurst 추정 (표준 구현)
    # tau[i] = std(price[lag:] - price[:-lag])
    # random walk: std ~ lag^0.5 → log-log 기울기 = H = 0.5
    # ★ 수정: 이전 코드는 sqrt(std)를 사용해 기울기가 H/2로 underestimate됨
    #   (sqrt(lag^H) = lag^(H/2)) — 오늘 0.064~0.070이 나온 원인
    # 1e-10 floor: std=0인 lag에서 log(0)=-inf → polyfit NaN 방지
    tau = [
        max(float(np.std(np.subtract(prices[lag:], prices[:-lag]))), 1e-10)
        for lag in lags
    ]

    # log-log 선형 회귀: log(tau) = H * log(lag) + const
    reg = np.polyfit(np.log(list(lags)), np.log(tau), 1)

    hurst_h = float(reg[0])

    return float(np.clip(hurst_h, 0.0, 1.0))


if __name__ == "__main__":
    # ── 동작 테스트 ───────────────────────────────────────────
    import random
    random.seed(42)

    # 추세 시뮬레이션
    trend_prices = [390 + i * 0.05 + random.gauss(0, 0.1) for i in range(60)]
    h_trend = calculate_hurst(trend_prices)
    print(f"[추세 시뮬] H = {h_trend:.3f}")

    # 횡보 시뮬레이션
    range_prices = [390 + random.gauss(0, 0.3) for _ in range(60)]
    h_range = calculate_hurst(range_prices)
    print(f"[횡보 시뮬] H = {h_range:.3f}")
