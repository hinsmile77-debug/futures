# features/bar_aggregator.py — 1분봉 → N분봉 완성봉 집계
"""
BarAggregator: Phase 2 핵심 컴포넌트.

1분봉을 누적하여 각 호라이즌별 완성봉을 생성한다.
단기(1m) 모델과 장기(30m) 모델이 각자의 시간 규모에 맞는 입력 데이터를 갖게 함.
"""
import logging

logger = logging.getLogger("SYSTEM")


class BarAggregator(object):
    """1분봉 → N분봉 완성 감지 및 집계"""

    HORIZONS = [1, 3, 5, 10, 15, 30]

    def __init__(self):
        self._bufs = {h: [] for h in self.HORIZONS if h > 1}
        self._last = {h: None for h in self.HORIZONS}
        self._hz_bar_age = {}   # {"1m": 0, "3m": 2, ...} — 완성봉 이후 경과 1분봉 수
        self._last_push_ts = None   # [453차 D4] 직전 push된 1m 봉 ts — 중복 주입 가드

    def push(self, bar_1m):
        # type: (dict) -> dict
        """
        1m 분봉을 입력받아 완성된 N분봉 dict 반환.

        반환값: {1: bar_1m, 3: agg_bar or None, 5: ..., 10: ..., 15: ..., 30: ...}
        None = 해당 봉 미완성 (직전 완성봉 계속 사용)
        """
        # [MW0601 453차 D4] 동일 ts 중복 주입 가드 — N분봉 격자 보호.
        # 이 클래스는 len(buf) >= h 로 봉 완성을 판정하므로, 중복 1분봉 하나가
        # 들어오면 그 뒤 **모든** N분봉 경계가 1분씩 밀리고 되돌아오지 않는다
        # (~452차 복구 재실행이 실제로 그랬다 — 08-04 완주 7회로 30m 경계 최대
        # 7분 어긋남). 중복이면 버퍼·age를 건드리지 않고 "완성봉 없음"만 낸다.
        _ts = bar_1m.get("ts")
        if _ts is not None and _ts == self._last_push_ts:
            logger.warning(
                "[BarAggregator] 동일 ts 중복 push 무시 ts=%s — N분봉 격자 보호 (453차 D4)",
                _ts)
            return {h: (bar_1m if h == 1 else None) for h in self.HORIZONS}
        self._last_push_ts = _ts

        result = {1: bar_1m}
        self._last[1] = bar_1m
        self._hz_bar_age["1m"] = 0   # 1m: 매분 완성
        for h in [3, 5, 10, 15, 30]:
            self._bufs[h].append(bar_1m)
            h_name = "{}m".format(h)
            if len(self._bufs[h]) >= h:
                agg = self._aggregate(self._bufs[h])
                self._last[h] = agg
                self._bufs[h] = []
                result[h] = agg
                self._hz_bar_age[h_name] = 0
            else:
                result[h] = None
                self._hz_bar_age[h_name] = self._hz_bar_age.get(h_name, 0) + 1
        return result

    def get_bar_age(self, hz):
        # type: (str) -> int
        """N분봉 완성 후 경과 1분봉 수. 완성 직후=0, 미초기화=999"""
        return self._hz_bar_age.get(hz, 999)

    def is_bar_fresh(self, hz, max_age=0):
        # type: (str, int) -> bool
        """max_age 이내면 True"""
        return self.get_bar_age(hz) <= max_age

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
        self._last_push_ts = None   # [453차 D4] 중복 가드 추적 ts도 함께 리셋
        self._last[1] = None
        self._hz_bar_age.clear()
