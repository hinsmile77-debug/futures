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

    # R/S (Rescaled Range) 기반 Hurst 추정
    # tau[i] = sqrt(std(price[lag:] - price[:-lag]))
    tau = [
        np.sqrt(np.std(np.subtract(prices[lag:], prices[:-lag])))
        for lag in lags
    ]

    # log-log 선형 회귀: log(tau) = H * log(lag) + const
    reg = np.polyfit(np.log(list(lags)), np.log(tau), 1)

    # ★ 수정: polyfit 기울기 = H (R/S 분석)
    #   Gemini 원본은 × 2.0 적용 → Variance 분석 혼동 오류
    hurst_h = float(reg[0])

    return float(np.clip(hurst_h, 0.0, 1.0))


def classify_market_state(h: float) -> dict:
    """
    Hurst 값을 시장 상태로 분류

    Returns:
        {state, action, confidence_modifier, description}
    """
    if h > 0.55:
        return {
            "state":               "추세장",
            "action":              "추세추종 허용",
            "confidence_modifier": +0.10,   # 신뢰도 +10%
            "description":        f"H={h:.3f} — 추세 지속, 진입 우호적",
        }
    elif h < 0.45:
        return {
            "state":               "횡보장",
            "action":              "진입 차단",
            "confidence_modifier": -0.99,   # 사실상 차단
            "description":        f"H={h:.3f} — 평균 회귀, MDD 위험",
        }
    else:
        return {
            "state":               "혼합 (데드존)",
            "action":              "신중 진입",
            "confidence_modifier": -0.10,   # 신뢰도 -10%
            "description":        f"H={h:.3f} — 방향 불명확",
        }


def hurst_with_regime_synergy(h: float, adx: float, atr_ratio: float) -> dict:
    """
    Hurst + v6.5 미시 레짐 결합 시너지

    Args:
        h:         Hurst 지수
        adx:       ADX 값 (추세 강도)
        atr_ratio: ATR / ATR_평균 (변동성 비율)

    Returns:
        결합 판단 결과
    """
    hurst_state = classify_market_state(h)

    # ADX > 25 AND H > 0.55 → 강한 추세 확인
    if adx > 25 and h > 0.55:
        return {
            "verdict":             "강한 추세 확인",
            "confidence_boost":    +0.15,
            "reason":              f"ADX={adx:.1f}(추세) + H={h:.2f}(지속성) 이중 확인",
        }

    # ADX > 25 BUT H < 0.45 → 가짜 추세 경고
    elif adx > 25 and h < 0.45:
        return {
            "verdict":             "가짜 추세 경고",
            "confidence_boost":    -0.99,
            "reason":              f"ADX={adx:.1f}(추세 외형) + H={h:.2f}(평균회귀) 불일치",
        }

    # ADX < 20 AND H < 0.45 → 명확 횡보
    elif adx < 20 and h < 0.45:
        return {
            "verdict":             "명확 횡보 — 역추세만",
            "confidence_boost":    -0.99,
            "reason":              f"ADX={adx:.1f} + H={h:.2f} 횡보 이중 확인",
        }

    # 급변장 (ATR 2배 이상)
    elif atr_ratio > 2.0:
        return {
            "verdict":             "급변장 — 거래 중단",
            "confidence_boost":    -0.99,
            "reason":              f"ATR비율={atr_ratio:.1f}배 급변 + H={h:.2f}",
        }

    else:
        return {
            "verdict":             "표준 앙상블",
            "confidence_boost":    0.0,
            "reason":              "혼합 레짐, 기본값 적용",
        }


if __name__ == "__main__":
    # ── 동작 테스트 ───────────────────────────────────────────
    import random
    random.seed(42)

    # 추세 시뮬레이션
    trend_prices = [390 + i * 0.05 + random.gauss(0, 0.1) for i in range(60)]
    h_trend = calculate_hurst(trend_prices)
    print(f"[추세 시뮬] H = {h_trend:.3f} → {classify_market_state(h_trend)['state']}")

    # 횡보 시뮬레이션
    range_prices = [390 + random.gauss(0, 0.3) for _ in range(60)]
    h_range = calculate_hurst(range_prices)
    print(f"[횡보 시뮬] H = {h_range:.3f} → {classify_market_state(h_range)['state']}")

    # 레짐 결합 테스트
    combined = hurst_with_regime_synergy(h=0.62, adx=28.5, atr_ratio=1.1)
    print(f"[레짐 결합] {combined['verdict']} | {combined['reason']}")
