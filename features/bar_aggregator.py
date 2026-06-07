# features/bar_aggregator.py — 1분봉 → N분봉 완성봉 집계
"""
BarAggregator: Phase 2 핵심 컴포넌트.

1분봉을 누적하여 각 호라이즌별 완성봉을 생성한다.
단기(1m) 모델과 장기(30m) 모델이 각자의 시간 규모에 맞는 입력 데이터를 갖게 함.
"""


class BarAggregator(object):
    """1분봉 → N분봉 완성 감지 및 집계"""

    HORIZONS = [1, 3, 5, 10, 15, 30]

    def __init__(self):
        self._bufs = {h: [] for h in self.HORIZONS if h > 1}
        self._last = {h: None for h in self.HORIZONS}

    def push(self, bar_1m):
        # type: (dict) -> dict
        """
        1m 분봉을 입력받아 완성된 N분봉 dict 반환.

        반환값: {1: bar_1m, 3: agg_bar or None, 5: ..., 10: ..., 15: ..., 30: ...}
        None = 해당 봉 미완성 (직전 완성봉 계속 사용)
        """
        result = {1: bar_1m}
        self._last[1] = bar_1m
        for h in [3, 5, 10, 15, 30]:
            self._bufs[h].append(bar_1m)
            if len(self._bufs[h]) >= h:
                agg = self._aggregate(self._bufs[h])
                self._last[h] = agg
                self._bufs[h] = []
                result[h] = agg
            else:
                result[h] = None
        return result

    def get_last(self, h):
        # type: (int) -> dict
        """마지막 완성봉 반환 (아직 완성된 적 없으면 None)."""
        return self._last.get(h)

    def _aggregate(self, bars):
        # type: (list) -> dict
        b0 = bars[0]
        return {
            "ts":       bars[-1]["ts"],
            "open":     b0["open"],
            "high":     max(b["high"] for b in bars),
            "low":      min(b["low"] for b in bars),
            "close":    bars[-1]["close"],
            "volume":   sum(b.get("volume", 0) for b in bars),
            "buy_vol":  sum(b.get("buy_vol", 0) for b in bars),
            "sell_vol": sum(b.get("sell_vol", 0) for b in bars),
            "bid1":     float(bars[-1].get("bid1") or 0.0),
            "ask1":     float(bars[-1].get("ask1") or 0.0),
        }

    def reset_daily(self):
        """일일 리셋 — 당일 누적 봉 버퍼 초기화."""
        for h in [3, 5, 10, 15, 30]:
            self._bufs[h] = []
            self._last[h] = None
        self._last[1] = None
