# features/technical/trend_efficiency.py — Trend Efficiency Ratio (Kaufman 1995) ⭐320차
"""
Kaufman Efficiency Ratio — 직선거리(순변화) / 총이동거리(누적 절대변화).

  ER = |close[t] - close[t-N]| / Σ|close[i] - close[i-1]|   (i = t-N+1..t)

0(잡음·횡보 — 왔다갔다한 거리가 순변화보다 훨씬 큼) ~ 1(완벽한 추세 — 한 방향으로만 이동).
Hurst 지수와 취지(추세 지속성)는 겹치지만 계산 방식이 전혀 다름(경로 비율 vs
variance-scaling 회귀) — 상관이 1이 아닐 것으로 기대되는 보완 신호.
"""
from typing import List

import numpy as np


def calculate_trend_efficiency(closes: List[float], window: int = 10) -> float:
    """
    Args:
        closes: 종가 리스트 (시간 오름차순), 최소 window+1개 필요
        window: 효율성 측정 구간 (분봉 수)

    Returns:
        0.0~1.0 (표본 부족 시 중립값 0.5, 총이동거리가 0에 가까우면 0.0)
    """
    n = len(closes)
    if n < window + 1:
        return 0.5

    recent = closes[-(window + 1):]
    net_change = abs(recent[-1] - recent[0])
    path_sum = sum(abs(recent[i] - recent[i - 1]) for i in range(1, len(recent)))

    if path_sum < 1e-9:
        return 0.0

    return float(np.clip(net_change / path_sum, 0.0, 1.0))


if __name__ == "__main__":
    # 완벽한 추세 (직선 상승)
    trend = [390.0 + i * 0.1 for i in range(15)]
    print(f"완벽한 추세: ER={calculate_trend_efficiency(trend, window=10):.4f} (기대: 1.0 근처)")

    # 순수 잡음 (왕복)
    import random
    random.seed(0)
    noise = [390.0]
    for _ in range(14):
        noise.append(noise[-1] + random.choice([-0.5, 0.5]))
    print(f"순수 잡음(왕복): ER={calculate_trend_efficiency(noise, window=10):.4f} (기대: 0에 가까움)")
