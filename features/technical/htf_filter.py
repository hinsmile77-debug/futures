# features/technical/htf_filter.py — 상위 타임프레임 필터 ⭐v6.5
"""
Higher TimeFrame (HTF) Filter

멀티 타임프레임 분석의 최종 관문.
5분봉·15분봉·일봉의 지지/저항 레벨을 실시간 추적하여
상위 타임프레임 저항에 걸리는 진입을 차단한다.

핵심 기능:
  1. HTF 피봇 지지/저항 계산 (일봉 기준)
  2. 5분봉 VWAP 밴드 필터
  3. 근접 저항 진입 차단 (목표가 < 저항까지 거리 기준)
"""
import numpy as np
from collections import deque
from typing import Optional, List


class HTFFilter:
    """상위 타임프레임 지지·저항 필터"""

    # 저항 근접 차단 기준 (pt 단위, KOSPI200 선물 기준)
    BLOCK_DISTANCE_PT = 1.0   # 저항까지 1pt 이내 진입 차단

    def __init__(self):
        # 일봉 피봇 레벨
        self._pivot   = 0.0
        self._r1 = self._r2 = 0.0   # 저항
        self._s1 = self._s2 = 0.0   # 지지

        # 5분봉 VWAP 트래킹
        self._vwap_5m_buf = deque(maxlen=10)
        self._5m_closes   = deque(maxlen=10)
        self._5m_vols     = deque(maxlen=10)

        # 주요 저항/지지 레벨 목록
        self._resistance_levels: List[float] = []
        self._support_levels:    List[float] = []

    def set_daily_pivot(self, prev_high: float, prev_low: float, prev_close: float):
        """
        일봉 피봇 포인트 설정 (매일 개장 전 1회 호출)

        피봇 = (H + L + C) / 3
        R1 = 2*P - L,  R2 = P + (H - L)
        S1 = 2*P - H,  S2 = P - (H - L)
        """
        p = (prev_high + prev_low + prev_close) / 3.0
        self._pivot = p
        self._r1    = 2 * p - prev_low
        self._r2    = p + (prev_high - prev_low)
        self._s1    = 2 * p - prev_high
        self._s2    = p - (prev_high - prev_low)

        self._resistance_levels = sorted([self._r1, self._r2])
        self._support_levels    = sorted([self._s1, self._s2], reverse=True)

    def push_5m_candle(self, close: float, volume: float):
        """5분봉 데이터 누적"""
        self._5m_closes.append(close)
        self._5m_vols.append(volume)

        # 5분봉 VWAP
        if self._5m_vols:
            vols   = np.array(list(self._5m_vols))
            closes = np.array(list(self._5m_closes))
            vwap   = float(np.sum(closes * vols) / (np.sum(vols) + 1e-9))
            self._vwap_5m_buf.append(vwap)

    def evaluate_entry(
        self,
        current_price: float,
        signal_direction: int,   # +1 매수, -1 매도
        target_price: Optional[float] = None,
    ) -> dict:
        """
        진입 시 HTF 필터 평가

        Args:
            current_price:    현재가
            signal_direction: +1(매수) / -1(매도)
            target_price:     목표가 (없으면 자동 계산 불가)

        Returns:
            {allow, block_reason, nearest_resistance, nearest_support,
             htf_multiplier, vwap_5m}
        """
        allow        = True
        block_reason = ""
        htf_mult     = 1.0

        # 1) 근접 저항 체크 (매수 시)
        nearest_res = self._nearest_resistance(current_price)
        if signal_direction == 1 and nearest_res is not None:
            dist = nearest_res - current_price
            if dist <= self.BLOCK_DISTANCE_PT:
                allow        = False
                block_reason = f"저항 근접 차단: 현재={current_price}, R={nearest_res:.2f} (거리={dist:.2f}pt)"
                htf_mult     = 0.0

        # 2) 근접 지지 체크 (매도 시)
        nearest_sup = self._nearest_support(current_price)
        if signal_direction == -1 and nearest_sup is not None:
            dist = current_price - nearest_sup
            if dist <= self.BLOCK_DISTANCE_PT:
                allow        = False
                block_reason = f"지지 근접 차단: 현재={current_price}, S={nearest_sup:.2f} (거리={dist:.2f}pt)"
                htf_mult     = 0.0

        # 3) 5분봉 VWAP 대비 방향 일치 확인
        vwap_5m = float(np.mean(list(self._vwap_5m_buf))) if self._vwap_5m_buf else 0.0
        if vwap_5m > 0:
            if signal_direction == 1 and current_price < vwap_5m * 0.999:
                htf_mult = min(htf_mult, 0.85)   # 5분봉 VWAP 하회 매수 → 약화
            elif signal_direction == -1 and current_price > vwap_5m * 1.001:
                htf_mult = min(htf_mult, 0.85)

        # 4) 피봇 기준 방향성 보강
        if self._pivot > 0:
            if signal_direction == 1 and current_price > self._pivot:
                htf_mult = min(htf_mult * 1.05, 1.2)   # 피봇 위 매수 → 소폭 강화
            elif signal_direction == -1 and current_price < self._pivot:
                htf_mult = min(htf_mult * 1.05, 1.2)

        return {
            "allow":              allow,
            "block_reason":       block_reason,
            "nearest_resistance": round(nearest_res, 2) if nearest_res else None,
            "nearest_support":    round(nearest_sup, 2) if nearest_sup else None,
            "pivot":              round(self._pivot, 2),
            "vwap_5m":            round(vwap_5m, 2),
            "htf_multiplier":     round(htf_mult, 3),   # 신호 가중치
        }

    def _nearest_resistance(self, price: float) -> Optional[float]:
        levels = [l for l in self._resistance_levels if l > price]
        return min(levels) if levels else None

    def _nearest_support(self, price: float) -> Optional[float]:
        levels = [l for l in self._support_levels if l < price]
        return max(levels) if levels else None

    def reset_daily(self):
        self._vwap_5m_buf.clear()
        self._5m_closes.clear()
        self._5m_vols.clear()


if __name__ == "__main__":
    f = HTFFilter()
    f.set_daily_pivot(prev_high=395.0, prev_low=385.0, prev_close=390.0)
    print(f"Pivot={f._pivot:.2f}, R1={f._r1:.2f}, R2={f._r2:.2f}, S1={f._s1:.2f}, S2={f._s2:.2f}")

    # 저항에 근접한 매수 시나리오
    r = f.evaluate_entry(current_price=394.2, signal_direction=1)
    print(f"진입 허용={r['allow']} | {r['block_reason'] or 'OK'} | HTF mult={r['htf_multiplier']}")

    # 안전 구간 매수
    r = f.evaluate_entry(current_price=390.5, signal_direction=1)
    print(f"진입 허용={r['allow']} | HTF mult={r['htf_multiplier']}")
