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


def correct_hurst_bias(h_raw: float, n: int, deshrink_table: dict) -> float:
    """
    317차 후속: calculate_hurst()의 소표본 하향편향을 선형 de-shrinkage로 보정.

    N/max_lag 재보정(317차)은 편향의 "크기"만 줄였을 뿐 임계값(0.45/0.55)은 그대로라,
    정상운영 구간조차 진짜 랜덤워크(H=0.5)가 평균 0.446으로 찍혀 여전히 구조적으로
    임계값을 못 넘는 문제가 남는다.

    1차 시도(H=0.5 지점만 기준으로 한 상수 이동, H_corrected=H_raw-bias)는 60거래일
    실측 검증에서 FalsePass가 14.4%→30.6%로 급악화해 폐기됨 — 편향이 H_true에 따라
    다르기 때문(H_true=0.3→0.5→0.7로 갈수록 편향이 커짐, 상수 이동은 이미 편향이
    작던 0.3 부근을 과보정해 0.55 위로 밀어올림). 대신 H_true=0.3/0.7 두 기준점으로
    선형모델(H_raw = a + b*H_true)을 적합하고 역산(H_true_est = (H_raw - a) / b)하는
    de-shrinkage로 교체 — 0.3·0.7 양끝은 정확히 복원되고 0.5도 크게 개선된다.

    deshrink_table: {n: (a, b)}. n이 테이블 키 사이 값이면 a·b 각각 선형보간,
    범위 밖이면 최근접 끝값 사용.

    Args:
        h_raw:          calculate_hurst() 원시 반환값
        n:               계산에 실제로 쓰인 표본 크기(버퍼 길이)
        deshrink_table:  config.settings.HURST_DESHRINK_TABLE 등, {n: (a, b)} 딕셔너리

    Returns:
        float: 보정된 Hurst 지수 (0.0~1.0으로 클립)
    """
    keys = sorted(deshrink_table.keys())
    if not keys:
        return h_raw
    if n <= keys[0]:
        a, b = deshrink_table[keys[0]]
    elif n >= keys[-1]:
        a, b = deshrink_table[keys[-1]]
    else:
        a, b = deshrink_table[keys[0]]
        for lo, hi in zip(keys, keys[1:]):
            if lo <= n <= hi:
                t = (n - lo) / float(hi - lo)
                a_lo, b_lo = deshrink_table[lo]
                a_hi, b_hi = deshrink_table[hi]
                a = a_lo * (1 - t) + a_hi * t
                b = b_lo * (1 - t) + b_hi * t
                break
    if abs(b) < 1e-6:
        return h_raw
    return float(np.clip((h_raw - a) / b, 0.0, 1.0))


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
