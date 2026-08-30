# features/technical/trend_efficiency.py — Trend Efficiency Ratio (Kaufman 1995) ⭐320차
"""
Kaufman Efficiency Ratio — 직선거리(순변화) / 총이동거리(누적 절대변화).

  ER = |close[t] - close[t-N]| / Σ|close[i] - close[i-1]|   (i = t-N+1..t)

0(잡음·횡보 — 왔다갔다한 거리가 순변화보다 훨씬 큼) ~ 1(완벽한 추세 — 한 방향으로만 이동).
Hurst 지수와 취지(추세 지속성)는 겹치지만 계산 방식이 전혀 다름(경로 비율 vs
variance-scaling 회귀) — 상관이 1이 아닐 것으로 기대되는 보완 신호.
"""
from typing import List, Tuple, Union

import numpy as np


def calculate_trend_efficiency(
    closes: List[float],
    window: int = 10,
    return_ready: bool = False,
) -> Union[float, Tuple[float, bool]]:
    """
    Args:
        closes: 종가 리스트 (시간 오름차순), 최소 window+1개 필요
        window: 효율성 측정 구간 (분봉 수)
        return_ready: True면 `(value, ready)` 튜플 반환 (MW0602 502차 후속 U-1)

    Returns:
        0.0~1.0 (표본 부족 시 중립값 0.5, 총이동거리가 0에 가까우면 0.0).
        `return_ready=True`면 `(값, ready)` — ready=False는 **표본 부족 폴백**이다.

    [MW0602 502차 후속 U-1 체리픽] ready 플래그를 도입한 이유 — 계측 4원칙
    ④("폴백이 쓰였으면 그 사실을 남긴다"):
      표본 부족 폴백값 **0.5**는 진입 게이트 후보 임계 0.32보다 **크다**. 즉 게이트를
      배선하면 *"아직 계산할 수 없다"* 가 *"효율적인 구간이다"* 로 읽혀 **폴백이 게이트를
      통과한다.** 전 분봉의 0.49%(57/11,739, MW0602 실측)로 빈도는 낮지만 **장 초반에
      몰리고**, 하필 그 구간이 손실 집중 구간이다(501차 딥다이브 §7: 개장 1시간이 일
      손실의 46~74%). FP-CRITICAL(2개월 PSI=0.0)·TOX 죽은 섀도와 같은 계열의 씨앗이다.
      → 소비자는 `ready=False`를 **별도 취급**할 것. 0.5를 그대로 비교하지 말 것.

    ⚠ `path_sum < 1e-9` → **0.0**은 폴백이 아니라 별도의 축퇴(degenerate) 규약이다.
      10분간 가격이 전혀 움직이지 않아 ER = 0/0 이 정의되지 않는 경우이며,
      "최대 비효율"로 관례 부여한다(게이트 관점에서는 스킵 쪽 = 보수적).
      표본 부족 폴백과 달리 **게이트를 통과하지 않으므로** ready=True로 둔다.
    """
    n = len(closes)
    if n < window + 1:
        return (0.5, False) if return_ready else 0.5

    recent = closes[-(window + 1):]
    net_change = abs(recent[-1] - recent[0])
    path_sum = sum(abs(recent[i] - recent[i - 1]) for i in range(1, len(recent)))

    if path_sum < 1e-9:
        return (0.0, True) if return_ready else 0.0

    val = float(np.clip(net_change / path_sum, 0.0, 1.0))
    return (val, True) if return_ready else val


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
