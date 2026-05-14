# features/technical/multi_timeframe.py — 멀티 타임프레임 분석 ⭐v6.5
"""
1분봉 + 5분봉 + 15분봉 동시 분석
상위 타임프레임 방향과 일치할 때만 신호 강화 / 불일치 시 차단

v6.5 채용 사항:
  5분봉↑ + 15분봉↑ → 1분봉 매수 신호 ×1.3
  5분봉↓ → 1분봉 매수 신호 차단
  5분봉↑ + 15분봉↓ → 1분봉 매수 신호 ×0.8 (약화)

기대 효과: 정확도 +3~5%, 거짓 신호 -30%
"""
import numpy as np
from collections import deque
from typing import Optional


class MultiTimeframeAnalyzer:
    """1분봉 기반 멀티 타임프레임 분석기"""

    def __init__(self):
        # 1분봉 원본 데이터 버퍼 (15분봉 계산용 최소 15개)
        self._close_1m  = deque(maxlen=60)   # 60분 보관
        self._high_1m   = deque(maxlen=60)
        self._low_1m    = deque(maxlen=60)
        self._volume_1m = deque(maxlen=60)

        # 5분봉 / 15분봉 집계 버퍼
        self._buf_5m  = deque(maxlen=5)   # 5개의 5분봉 (25분)
        self._buf_15m = deque(maxlen=4)   # 4개의 15분봉 (60분)

        self._tick_5m  = []   # 1분봉 5개 모아서 5분봉 생성
        self._tick_15m = []   # 1분봉 15개 모아서 15분봉 생성
        self._count_5m  = 0
        self._count_15m = 0

    def push_1m_candle(self, open_: float, high: float, low: float, close: float, volume: float) -> dict:
        """
        1분봉 확정 시 호출 — 5분봉·15분봉 자동 집계

        Returns:
            {trend_1m, trend_5m, trend_15m, multiplier,
             block_long_entry, block_short_entry, reason}

        block_long_entry : 5분봉↓ 시 True — 롱 진입만 차단 (숏은 허용)
        block_short_entry: 5분봉↑ 시 True — 숏 진입만 차단 (롱은 허용)
        """
        self._close_1m.append(close)
        self._high_1m.append(high)
        self._low_1m.append(low)
        self._volume_1m.append(volume)

        # 5분봉 데이터 누적
        self._tick_5m.append({"o": open_, "h": high, "l": low, "c": close, "v": volume})
        self._tick_15m.append({"o": open_, "h": high, "l": low, "c": close, "v": volume})
        self._count_5m  += 1
        self._count_15m += 1

        # 5분봉 완성
        if self._count_5m >= 5:
            candle_5m = self._aggregate_candles(self._tick_5m)
            self._buf_5m.append(candle_5m)
            self._tick_5m.clear()
            self._count_5m = 0

        # 15분봉 완성
        if self._count_15m >= 15:
            candle_15m = self._aggregate_candles(self._tick_15m)
            self._buf_15m.append(candle_15m)
            self._tick_15m.clear()
            self._count_15m = 0

        return self._evaluate()

    def _aggregate_candles(self, ticks: list) -> dict:
        """N개 1분봉 → 상위 봉 집계"""
        return {
            "o": ticks[0]["o"],
            "h": max(t["h"] for t in ticks),
            "l": min(t["l"] for t in ticks),
            "c": ticks[-1]["c"],
            "v": sum(t["v"] for t in ticks),
        }

    def _candle_trend(self, buf: deque, periods: int = 3) -> int:
        """
        최근 N개 봉 기반 추세 판단

        Returns:
            +1 (상승), -1 (하락), 0 (횡보)
        """
        if len(buf) < 2:
            return 0

        closes = [b["c"] for b in list(buf)[-periods:]]
        if len(closes) < 2:
            return 0

        # 단순 선형 기울기
        reg = np.polyfit(range(len(closes)), closes, 1)
        slope = reg[0]
        avg   = np.mean(closes)
        rel   = slope / (avg + 1e-9)

        if rel > 0.0005:    # 0.05% 이상 기울기 = 상승
            return 1
        elif rel < -0.0005:
            return -1
        return 0

    def _evaluate(self) -> dict:
        """
        1분봉 기준 현재 추세 + 상위 타임프레임 필터 평가

        Returns:
            {trend_1m, trend_5m, trend_15m, multiplier,
             block_long_entry, block_short_entry, reason}
        """
        trend_1m  = self._trend_from_closes(list(self._close_1m)[-5:])
        trend_5m  = self._candle_trend(self._buf_5m,  periods=3)
        trend_15m = self._candle_trend(self._buf_15m, periods=2)

        multiplier         = 1.0
        block_long_entry   = False
        block_short_entry  = False
        reason             = ""

        # --- v6.5 규칙 (방향 대칭으로 개선) ---
        if trend_5m == 1 and trend_15m == 1:
            multiplier = 1.3
            reason     = "5분↑+15분↑ 동조 → 신호 ×1.3"

        elif trend_5m == -1 and trend_15m == -1:
            multiplier = 0.7
            reason     = "5분↓+15분↓ 역행 → 신호 ×0.7"

        elif trend_5m == -1:
            # 5분봉 하락 → 롱만 차단 (숏은 5m 추세 동조이므로 허용)
            block_long_entry = True
            multiplier       = 0.0
            reason           = "5분봉↓ → 매수 진입 차단"

        elif trend_5m == 1 and trend_15m == -1:
            # 5분봉 상승이지만 15분봉 하락 불일치 → 숏만 차단, 롱 약화
            block_short_entry = True
            multiplier        = 0.8
            reason            = "5분↑/15분↓ 불일치 → 신호 ×0.8 (숏 차단)"

        elif trend_5m == 1:
            # 5분봉 상승 (15분봉 중립) → 숏 차단
            block_short_entry = True
            multiplier        = 0.0
            reason            = "5분봉↑ → 매도 진입 차단"

        elif trend_5m == 0:
            multiplier = 0.9
            reason     = "5분봉 횡보 → 신호 ×0.9"

        return {
            "trend_1m":          trend_1m,
            "trend_5m":          trend_5m,
            "trend_15m":         trend_15m,
            "multiplier":        round(multiplier, 2),
            "block_long_entry":  block_long_entry,
            "block_short_entry": block_short_entry,
            "reason":            reason,
        }

    @staticmethod
    def _trend_from_closes(closes: list) -> int:
        if len(closes) < 2:
            return 0
        reg = np.polyfit(range(len(closes)), closes, 1)
        slope = reg[0]
        avg   = np.mean(closes)
        rel   = slope / (avg + 1e-9)
        if rel > 0.0005:
            return 1
        elif rel < -0.0005:
            return -1
        return 0

    def reset_daily(self):
        self._close_1m.clear()
        self._high_1m.clear()
        self._low_1m.clear()
        self._volume_1m.clear()
        self._buf_5m.clear()
        self._buf_15m.clear()
        self._tick_5m.clear()
        self._tick_15m.clear()
        self._count_5m  = 0
        self._count_15m = 0


if __name__ == "__main__":
    import random
    random.seed(42)

    mtf = MultiTimeframeAnalyzer()
    price = 390.0

    # 상승 추세 시뮬레이션 (20분)
    for i in range(20):
        price += random.gauss(0.1, 0.2)
        r = mtf.push_1m_candle(price - 0.1, price + 0.1, price - 0.15, price, 1000)
        print(f"[{i+1:02d}분] 1m={r['trend_1m']:+d} 5m={r['trend_5m']:+d} 15m={r['trend_15m']:+d} "
              f"mult={r['multiplier']} blk_L={r['block_long_entry']} blk_S={r['block_short_entry']} | {r['reason']}")
