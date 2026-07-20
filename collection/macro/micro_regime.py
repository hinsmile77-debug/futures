"""Minute-level micro regime classifier based on ADX and ATR."""

from collections import Counter, deque
import logging
from typing import Dict

import numpy as np

logger = logging.getLogger("SYSTEM")


REGIME_TREND = "추세장"
REGIME_RANGE = "횡보장"
REGIME_VOLATILE = "급변장"
REGIME_MIXED = "혼합"
REGIME_EXHAUSTION = "탈진"

REGIMES = [
    REGIME_TREND,
    REGIME_RANGE,
    REGIME_VOLATILE,
    REGIME_MIXED,
    REGIME_EXHAUSTION,
]

REGIME_EXHAUSTION_PARAMS = {
    "strategy_mode": "mean_reversion",
    "min_confidence": 0.56,
    "size_mult": 0.70,
    "entry_direction": "TOWARD_VWAP",
    "hurst_override": True,
}


class MicroRegimeClassifier:
    """Classify short-term market structure from 1-minute candles."""

    ADX_TREND_THRESHOLD = 25.0
    ADX_RANGE_THRESHOLD = 20.0
    ATR_VOLATILE_MULT = 1.5
    ATR_TREND_MULT = 1.5
    ATR_VOLATILE_ADX_MIN = 30.0
    ATR_EXHAUSTION_MIN = 1.2   # 탈진장 ATR 하한 (상한은 ATR_VOLATILE_MULT)
    VWAP_EXHAUSTION_MIN = 1.5
    MIN_CANDLES_FOR_ATR = 5
    INSTABILITY_WINDOW_MIN = 10   # [359차] 휩쏘 계측 창 — 최근 N분 내 레짐 전환 횟수

    def __init__(self, atr_window: int = 20, adx_window: int = 14):
        self.atr_window = atr_window
        self.adx_window = adx_window

        candle_buf_len = max(
            adx_window + 5,
            self.MIN_CANDLES_FOR_ATR + atr_window,
        )
        self._high_buf = deque(maxlen=candle_buf_len)
        self._low_buf = deque(maxlen=candle_buf_len)
        self._close_buf = deque(maxlen=candle_buf_len)
        self._atr_buf = deque(maxlen=atr_window)

        self._current_regime = REGIME_MIXED
        self._prev_regime = REGIME_MIXED
        self._regime_duration = 0
        self._regime_history = deque(maxlen=60)

    def push_1m_candle(
        self,
        high,
        low,
        close,
        bear_exhaustion=0.0,
        bull_exhaustion=0.0,
        vwap_position=0.0,
        z_warn_count=0,
    ) -> Dict:
        self._high_buf.append(high)
        self._low_buf.append(low)
        self._close_buf.append(close)

        warmup = self.get_warmup_status()
        if len(self._close_buf) < self.MIN_CANDLES_FOR_ATR:
            result = self._empty()
            result["warmup"] = warmup
            return result

        atr = self._compute_atr()
        atr_avg = float(np.mean(list(self._atr_buf))) if len(self._atr_buf) >= 5 else atr
        self._atr_buf.append(atr)
        atr_ratio = atr / (atr_avg + 1e-9)

        adx = self._compute_adx()
        new_regime = self._classify(
            adx,
            atr,
            atr_avg,
            atr_ratio,
            bear_exhaustion,
            bull_exhaustion,
            vwap_position,
            z_warn_count,
        )

        regime_changed = new_regime != self._current_regime
        if regime_changed:
            logger.info(
                "[MicroRegime] %s → %s (ADX=%.1f, ATR=%.3f, ratio=%.2f)",
                self._current_regime,
                new_regime,
                adx,
                atr,
                atr_ratio,
            )
            self._prev_regime = self._current_regime
            self._current_regime = new_regime
            self._regime_duration = 1
        else:
            self._regime_duration += 1

        self._regime_history.append(new_regime)
        trend_strength = float(np.clip((adx - 10.0) / 40.0, 0.0, 1.0))

        # [359차] 레짐 불안정도(휩쏘) 계측 — 최근 N분 내 레짐 라벨 전환 횟수.
        # _regime_history는 매분 1개씩만 쌓이므로 최근 N개 슬라이스의 인접 비교로 충분.
        _window = list(self._regime_history)[-self.INSTABILITY_WINDOW_MIN:]
        instability = sum(
            1 for _i in range(1, len(_window)) if _window[_i] != _window[_i - 1]
        )

        return {
            "regime": new_regime,
            "adx": round(adx, 2),
            "atr": round(atr, 4),
            "atr_avg": round(atr_avg, 4),
            "atr_ratio": round(atr_ratio, 3),
            "regime_duration": self._regime_duration,
            "regime_changed": regime_changed,
            "trend_strength": round(trend_strength, 3),
            "hurst_override": new_regime == REGIME_EXHAUSTION,
            "warmup": self.get_warmup_status(),
            "instability_10m": instability,
        }

    def _classify(
        self,
        adx,
        atr,
        atr_avg,
        atr_ratio,
        bear_exhaustion=0.0,
        bull_exhaustion=0.0,
        vwap_position=0.0,
        z_warn_count=0,
    ) -> str:
        del atr, atr_avg

        volatile = (
            atr_ratio >= self.ATR_VOLATILE_MULT
            or z_warn_count >= 3
            or (atr_ratio >= 1.25 and adx >= self.ATR_VOLATILE_ADX_MIN)
        )
        if volatile:
            return REGIME_VOLATILE

        # 탈진장: 급변장과 겹치지 않는 독립 구간 (ATR_EXHAUSTION_MIN ~ ATR_VOLATILE_MULT)
        # ofi_reversal_speed 조건 제거 — bear/bull_exhaustion이 CVD+OFI 복합 신호를 이미 내포
        exhaustion_conds = (
            self.ATR_EXHAUSTION_MIN <= atr_ratio < self.ATR_VOLATILE_MULT
            and (bear_exhaustion > 0 or bull_exhaustion > 0)
            and abs(vwap_position) >= self.VWAP_EXHAUSTION_MIN
        )
        if exhaustion_conds:
            return REGIME_EXHAUSTION

        if adx >= self.ADX_TREND_THRESHOLD and atr_ratio < self.ATR_TREND_MULT:
            return REGIME_TREND

        if adx < self.ADX_RANGE_THRESHOLD and atr_ratio < 1.3:
            return REGIME_RANGE

        return REGIME_MIXED

    def _compute_atr(self) -> float:
        highs = list(self._high_buf)
        lows = list(self._low_buf)
        closes = list(self._close_buf)

        if len(closes) < 2:
            return 0.0

        tr_list = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
            tr_list.append(tr)

        return float(np.mean(tr_list[-14:])) if tr_list else 0.0

    def _compute_adx(self) -> float:
        closes = np.array(list(self._close_buf))
        if len(closes) < self.adx_window:
            return 15.0

        highs = np.array(list(self._high_buf)[-self.adx_window:])
        lows = np.array(list(self._low_buf)[-self.adx_window:])
        close_slice = list(self._close_buf)[-self.adx_window:]

        if len(highs) < 2:
            return 15.0

        plus_dm = np.maximum(highs[1:] - highs[:-1], 0)
        minus_dm = np.maximum(lows[:-1] - lows[1:], 0)

        for i in range(len(plus_dm)):
            if plus_dm[i] > 0 and minus_dm[i] > 0:
                if plus_dm[i] >= minus_dm[i]:
                    minus_dm[i] = 0
                else:
                    plus_dm[i] = 0

        atrs = []
        for i in range(1, min(len(highs), len(lows), len(close_slice))):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - close_slice[i - 1]),
                abs(lows[i] - close_slice[i - 1]),
            )
            atrs.append(tr)

        atr_sum = sum(atrs) if atrs else 1e-9
        plus_di = 100 * sum(plus_dm) / (atr_sum + 1e-9)
        minus_di = 100 * sum(minus_dm) / (atr_sum + 1e-9)

        di_sum = plus_di + minus_di
        if di_sum < 1e-9:
            return 15.0

        dx = 100 * abs(plus_di - minus_di) / di_sum
        return float(np.clip(dx, 0, 100))

    def _empty(self) -> Dict:
        return {
            "regime": REGIME_MIXED,
            "adx": 15.0,
            "atr": 0.0,
            "atr_avg": 0.0,
            "atr_ratio": 1.0,
            "regime_duration": 0,
            "regime_changed": False,
            "trend_strength": 0.0,
        }

    def get_warmup_status(self) -> Dict:
        close_count = len(self._close_buf)
        atr_samples = len(self._atr_buf)

        adx_progress = int(
            np.clip((close_count / float(self.adx_window or 1)) * 100.0, 0.0, 100.0)
        )
        atr_progress = int(
            np.clip((atr_samples / float(self.atr_window or 1)) * 100.0, 0.0, 100.0)
        )

        adx_ready = close_count >= self.adx_window
        atr_ready = atr_samples >= self.atr_window
        overall_progress = int(round((adx_progress + atr_progress) / 2.0))

        adx_remaining = max(0, self.adx_window - close_count)
        if close_count < self.MIN_CANDLES_FOR_ATR:
            atr_remaining = self.MIN_CANDLES_FOR_ATR + self.atr_window - 1 - close_count
        else:
            atr_remaining = max(0, self.atr_window - atr_samples)
        remaining_bars = max(adx_remaining, atr_remaining)

        if close_count < self.MIN_CANDLES_FOR_ATR:
            level = "L1"
            label = "TR/ATR seed"
        elif not adx_ready:
            level = "L2"
            label = "ADX warmup"
        elif not atr_ready:
            level = "L3"
            label = "ATR avg warmup"
        else:
            level = "READY"
            label = "Micro regime ready"

        return {
            "active": not (adx_ready and atr_ready),
            "level": level,
            "label": label,
            "progress": overall_progress,
            "remaining_bars": remaining_bars,
            "close_count": close_count,
            "atr_samples": atr_samples,
            "adx_progress": adx_progress,
            "atr_progress": atr_progress,
            "adx_ready": adx_ready,
            "atr_ready": atr_ready,
            "min_closes_for_atr": self.MIN_CANDLES_FOR_ATR,
            "adx_target": self.adx_window,
            "atr_target": self.atr_window,
        }

    @property
    def current_regime(self) -> str:
        return self._current_regime

    def get_regime_distribution(self) -> Dict:
        hist = list(self._regime_history)
        if not hist:
            return {}
        cnt = Counter(hist)
        return {regime: round(cnt.get(regime, 0) / len(hist), 3) for regime in REGIMES}

    def reset_daily(self) -> None:
        self._high_buf.clear()
        self._low_buf.clear()
        self._close_buf.clear()
        self._atr_buf.clear()
        self._current_regime = REGIME_MIXED
        self._prev_regime = REGIME_MIXED
        self._regime_duration = 0
        self._regime_history.clear()
