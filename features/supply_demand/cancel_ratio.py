# features/supply_demand/cancel_ratio.py — 호가 취소 속도 (스푸핑 감지) ⭐v7.0
"""
Cancel Ratio = 취소 주문 수 / 체결 주문 수

취소 비율이 높으면 시장 조성자나 스푸퍼가 허수 주문으로 시장을 교란 중.
  > 3.0 → 스푸핑 의심 → 반대 방향 가중치 반영
  > 5.0 → 강한 스푸핑 → 진입 신중

OFI·LOBID (정적 스냅샷) + Cancel Ratio (동적 취소 흐름) 보완 관계.
취소가 매수호가에서 집중 → 실제 매수 의향 없음 → 하락 가능성↑
취소가 매도호가에서 집중 → 실제 매도 의향 없음 → 상승 가능성↑

기대 효과: 스푸핑 회피 +3%
"""
import numpy as np
from collections import deque
from typing import Optional


class CancelRatioCalculator:
    """호가 취소 비율 실시간 계산기"""

    # 스푸핑 판단 임계값
    SPOOF_THRESHOLD_MODERATE = 3.0
    SPOOF_THRESHOLD_STRONG   = 5.0

    def __init__(self, window: int = 10):
        """
        Args:
            window: 분봉 이동평균 창 (10분)
        """
        self.window = window

        # 분 내 틱 카운터
        self._cancel_bid   = 0   # 매수호가 취소
        self._cancel_ask   = 0   # 매도호가 취소
        self._fill_bid     = 0   # 매수 체결
        self._fill_ask     = 0   # 매도 체결
        self._cancel_total = 0
        self._fill_total   = 0

        # 분봉 버퍼
        self._ratio_buf      = deque(maxlen=window)
        self._ratio_bid_buf  = deque(maxlen=window)
        self._ratio_ask_buf  = deque(maxlen=window)

    def on_cancel(self, side: str):
        """
        주문 취소 이벤트

        Args:
            side: 'bid' (매수호가 취소) or 'ask' (매도호가 취소)
        """
        self._cancel_total += 1
        if side == 'bid':
            self._cancel_bid += 1
        else:
            self._cancel_ask += 1

    def on_fill(self, side: str):
        """
        주문 체결 이벤트

        Args:
            side: 'bid' or 'ask'
        """
        self._fill_total += 1
        if side == 'bid':
            self._fill_bid += 1
        else:
            self._fill_ask += 1

    def flush_minute(self) -> dict:
        """
        1분봉 마감 — Cancel Ratio 집계

        Returns:
            {cancel_ratio, cancel_ratio_bid, cancel_ratio_ask,
             cancel_ratio_ma, spoof_detected, spoof_direction,
             signal_modifier, reason}
        """
        # 전체 취소 비율
        cr = self._cancel_total / max(self._fill_total, 1)

        # 매수호가 취소 비율 (독립 계산)
        cr_bid = self._cancel_bid / max(self._fill_bid, 1)

        # 매도호가 취소 비율
        cr_ask = self._cancel_ask / max(self._fill_ask, 1)

        self._ratio_buf.append(cr)
        self._ratio_bid_buf.append(cr_bid)
        self._ratio_ask_buf.append(cr_ask)

        cr_ma     = float(np.mean(list(self._ratio_buf)))
        cr_bid_ma = float(np.mean(list(self._ratio_bid_buf)))
        cr_ask_ma = float(np.mean(list(self._ratio_ask_buf)))

        # 스푸핑 감지 및 방향 추정
        spoof_detected = False
        spoof_direction = 0   # +1 (실제 매수 우위), -1 (실제 매도 우위)
        signal_modifier = 1.0
        reason = "정상"

        if cr_ma >= self.SPOOF_THRESHOLD_STRONG:
            spoof_detected = True
            # 매수호가 취소 > 매도호가 취소 → 매수 허수 → 실제 하락 가능
            if cr_bid_ma > cr_ask_ma * 1.5:
                spoof_direction = -1
                reason = f"강한 스푸핑: 매수호가 취소 집중 (bid_cr={cr_bid_ma:.1f}) → 하락 의심"
                signal_modifier = 0.6
            elif cr_ask_ma > cr_bid_ma * 1.5:
                spoof_direction = 1
                reason = f"강한 스푸핑: 매도호가 취소 집중 (ask_cr={cr_ask_ma:.1f}) → 상승 의심"
                signal_modifier = 0.6
            else:
                reason = f"강한 스푸핑: 방향 불명 (cr={cr_ma:.1f}) → 신중 진입"
                signal_modifier = 0.7

        elif cr_ma >= self.SPOOF_THRESHOLD_MODERATE:
            spoof_detected = True
            if cr_bid_ma > cr_ask_ma * 1.3:
                spoof_direction = -1
                reason = f"스푸핑 의심: 매수호가 취소 (bid_cr={cr_bid_ma:.1f})"
                signal_modifier = 0.8
            elif cr_ask_ma > cr_bid_ma * 1.3:
                spoof_direction = 1
                reason = f"스푸핑 의심: 매도호가 취소 (ask_cr={cr_ask_ma:.1f})"
                signal_modifier = 0.8
            else:
                reason = f"스푸핑 의심: cr={cr_ma:.1f}"
                signal_modifier = 0.85

        # 분 초기화
        self._cancel_bid   = 0
        self._cancel_ask   = 0
        self._fill_bid     = 0
        self._fill_ask     = 0
        self._cancel_total = 0
        self._fill_total   = 0

        return {
            "cancel_ratio":     round(cr, 3),          # CORE 피처값
            "cancel_ratio_bid": round(cr_bid, 3),
            "cancel_ratio_ask": round(cr_ask, 3),
            "cancel_ratio_ma":  round(cr_ma, 3),       # CORE 피처값
            "spoof_detected":   spoof_detected,
            "spoof_direction":  spoof_direction,
            "signal_modifier":  round(signal_modifier, 3),
            "reason":           reason,
        }

    def reset_daily(self):
        self._cancel_bid   = 0
        self._cancel_ask   = 0
        self._fill_bid     = 0
        self._fill_ask     = 0
        self._cancel_total = 0
        self._fill_total   = 0
        self._ratio_buf.clear()
        self._ratio_bid_buf.clear()
        self._ratio_ask_buf.clear()


if __name__ == "__main__":
    calc = CancelRatioCalculator(window=10)

    # 스푸핑 시나리오: 매수호가 취소 폭증
    for _ in range(10):
        calc.on_fill('bid')
        calc.on_fill('ask')
    for _ in range(40):
        calc.on_cancel('bid')   # 매수 취소 집중
    for _ in range(5):
        calc.on_cancel('ask')

    for i in range(3):
        r = calc.flush_minute()
        print(f"[분 {i+1}] cr={r['cancel_ratio']:.2f}, cr_ma={r['cancel_ratio_ma']:.2f}, "
              f"spoof={r['spoof_detected']}, dir={r['spoof_direction']:+d}, mod={r['signal_modifier']}")
        print(f"        {r['reason']}")
        # 다음 분: 정상적으로 채우기
        for _ in range(10):
            calc.on_fill('bid')
            calc.on_fill('ask')
