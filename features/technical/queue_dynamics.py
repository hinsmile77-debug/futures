# features/technical/queue_dynamics.py — 호가 큐 동역학 (Queue Dynamics)
"""
호가 큐의 소진 속도(queue depletion rate)와 재생 속도(replenishment rate)를 측정.
1분봉 내 단기 방향 전환을 미리 선행 감지.

핵심 아이디어:
  - 매수1호가 수량이 빠르게 줄어들면(소진) → 매수 압력 소진 → 하락 선행
  - 매도1호가 수량이 빠르게 줄어들면(소진) → 매도 물량 소진 → 상승 선행
  - 큐 재생이 소진보다 빠르면 → 해당 방향 유지

지표:
  depletion_bid: 매수1호가 소진율 (qty 감소 속도)
  depletion_ask: 매도1호가 소진율
  queue_signal:  +1(매수 큐 우위) / -1(매도 큐 우위) / 0(중립)
"""
import numpy as np
from collections import deque
from typing import Optional


class QueueDynamicsCalculator:
    """호가 큐 동역학 계산기"""

    def __init__(self, window: int = 10):
        """
        Args:
            window: 큐 변화 추적 틱 수 (짧을수록 민감)
        """
        self.window = window
        self._bid_qty_hist = deque(maxlen=window)
        self._ask_qty_hist = deque(maxlen=window)

        # 분봉 집계
        self._minute_signals = []
        self._minute_buf     = deque(maxlen=5)   # 5분 MA

    def update_hoga(
        self,
        bid_qty: int,
        ask_qty: int,
    ) -> Optional[dict]:
        """
        호가 틱 업데이트

        Args:
            bid_qty: 매수 1호가 수량
            ask_qty: 매도 1호가 수량

        Returns:
            틱 레벨 큐 신호 또는 None (데이터 부족)
        """
        self._bid_qty_hist.append(float(bid_qty))
        self._ask_qty_hist.append(float(ask_qty))

        if len(self._bid_qty_hist) < 3:
            return None

        return self._compute_tick()

    def _compute_tick(self) -> dict:
        """틱 레벨 큐 동역학 계산"""
        bid_arr = np.array(list(self._bid_qty_hist))
        ask_arr = np.array(list(self._ask_qty_hist))

        # 소진율: 최근 수량 변화 (음수 = 소진, 양수 = 재생)
        bid_delta = float(bid_arr[-1] - bid_arr[0])
        ask_delta = float(ask_arr[-1] - ask_arr[0])

        # 소진 속도 정규화 (평균 대비)
        bid_avg = float(np.mean(bid_arr)) + 1e-9
        ask_avg = float(np.mean(ask_arr)) + 1e-9

        depletion_bid = -bid_delta / bid_avg   # 양수 = 매수 큐 소진
        depletion_ask = -ask_delta / ask_avg   # 양수 = 매도 큐 소진

        # 큐 신호: 매도 큐가 소진되면 매수 유리
        if depletion_ask > 0.2 and depletion_bid < 0.1:
            queue_signal = 1
        elif depletion_bid > 0.2 and depletion_ask < 0.1:
            queue_signal = -1
        else:
            queue_signal = 0

        self._minute_signals.append(queue_signal)

        return {
            "depletion_bid": round(depletion_bid, 4),
            "depletion_ask": round(depletion_ask, 4),
            "queue_signal":  queue_signal,
        }

    def flush_minute(self) -> dict:
        """
        1분봉 마감 — 분봉 레벨 큐 집계

        Returns:
            {queue_signal_mean, queue_signal_ma, queue_momentum}
        """
        if self._minute_signals:
            mean_signal = float(np.mean(self._minute_signals))
        else:
            mean_signal = 0.0

        self._minute_buf.append(mean_signal)

        # 5분 이동평균
        signal_ma = float(np.mean(list(self._minute_buf)))

        # 큐 모멘텀: 최근 변화 추세
        momentum = 0.0
        if len(self._minute_buf) >= 3:
            arr = list(self._minute_buf)
            momentum = float(arr[-1] - arr[-3]) / 2.0

        # 최종 방향 판단
        if signal_ma > 0.15:
            direction = 1
        elif signal_ma < -0.15:
            direction = -1
        else:
            direction = 0

        self._minute_signals.clear()

        return {
            "queue_signal_mean": round(mean_signal, 4),   # CORE 피처값
            "queue_signal_ma":   round(signal_ma, 4),     # CORE 피처값
            "queue_momentum":    round(momentum, 4),
            "direction":         direction,
        }

    def reset_daily(self):
        self._bid_qty_hist.clear()
        self._ask_qty_hist.clear()
        self._minute_signals.clear()
        self._minute_buf.clear()


if __name__ == "__main__":
    calc = QueueDynamicsCalculator(window=10)

    # 매도 큐 소진 → 매수 신호 시나리오
    ask_qtys = [300, 250, 200, 150, 100, 80, 60, 50, 40, 30]
    bid_qtys = [200, 210, 205, 215, 210, 220, 215, 225, 220, 230]

    for i in range(10):
        r = calc.update_hoga(bid_qty=bid_qtys[i], ask_qty=ask_qtys[i])
        if r:
            print(f"[틱 {i+1}] dep_bid={r['depletion_bid']:+.3f}, dep_ask={r['depletion_ask']:+.3f}, signal={r['queue_signal']:+d}")

    result = calc.flush_minute()
    print(f"[분봉] signal_mean={result['queue_signal_mean']:+.4f}, dir={result['direction']:+d}")
