from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from typing import Callable, Deque, Dict, List, Optional

from collection.cybos.api_connector import CybosAPI, _safe_float, _safe_int, _safe_str

logger = logging.getLogger(__name__)
sys_log = logging.getLogger("SYSTEM")

MAX_CANDLES = 500

FUTURE_CUR_ONLY_PROGID = "Dscbo1.FutureCurOnly"
FUTURE_JP_BID_PROGID = "CpSysDib.FutureJpBid"


class CybosRealtimeData:
    def __init__(
        self,
        api: CybosAPI,
        code: str,
        screen_no: str = "3000",
        on_candle_closed: Optional[Callable] = None,
        on_tick: Optional[Callable] = None,
        on_hoga: Optional[Callable] = None,
        realtime_code: Optional[str] = None,
        is_mock_server: bool = False,
    ):
        del screen_no, is_mock_server

        self.api = api
        self.code = code
        self._rt_code = realtime_code or code
        self._on_candle_closed = on_candle_closed
        self._on_tick = on_tick
        self._on_hoga = on_hoga

        self._candles = deque(maxlen=MAX_CANDLES)
        self._current_bar = None
        self._current_min = None
        self._running = False

        self._tick_subscription = None
        self._hoga_subscription = None

        self._last_price = 0.0
        self._last_cum_volume = 0
        self._last_bid1 = 0.0
        self._last_ask1 = 0.0
        self._last_bid_qty = 0
        self._last_ask_qty = 0
        self._last_hoga_snapshot = {
            "bid_prices": [],
            "ask_prices": [],
            "bid_qtys": [],
            "ask_qtys": [],
        }
        self._tick_event_count = 0
        self._hoga_event_count = 0

    @property
    def candles(self) -> Deque[Dict]:
        return self._candles

    @property
    def latest_closed(self) -> Optional[Dict]:
        return self._candles[-1] if self._candles else None

    @property
    def current_bar(self) -> Optional[Dict]:
        return self._current_bar

    def get_last_n(self, n: int) -> List[Dict]:
        candles = list(self._candles)
        return candles[-n:] if len(candles) >= n else candles

    def start(self, load_history: bool = True) -> None:
        del load_history

        if self._running:
            return

        self._prime_from_snapshot()
        self._tick_subscription = self.api.create_subscription(
            progid=FUTURE_CUR_ONLY_PROGID,
            input_values={0: self._rt_code},
            owner=self,
            event_name="tick",
            latest=True,
        )
        self._hoga_subscription = self.api.create_subscription(
            progid=FUTURE_JP_BID_PROGID,
            input_values={0: self._rt_code},
            owner=self,
            event_name="hoga",
            latest=True,
        )
        self._running = True
        logger.info("[CybosRT] start code=%s", self._rt_code)

    def stop(self) -> None:
        if not self._running:
            return
        if self._tick_subscription is not None:
            self._tick_subscription.unsubscribe()
            self._tick_subscription = None
        if self._hoga_subscription is not None:
            self._hoga_subscription.unsubscribe()
            self._hoga_subscription = None
        self._running = False
        logger.info("[CybosRT] stop code=%s", self._rt_code)

    def _handle_subscription_event(self, event_name: str, sink) -> None:
        if event_name == "tick" and self._tick_subscription is not None:
            self._handle_tick(self._tick_subscription.com_object)
        elif event_name == "hoga" and self._hoga_subscription is not None:
            self._handle_hoga(self._hoga_subscription.com_object)

    def _prime_from_snapshot(self) -> None:
        snapshot = self.api.request_futures_snapshot(self._rt_code)
        if not snapshot:
            return
        self._last_price = _safe_float(snapshot.get("price"))
        self._last_cum_volume = _safe_int(snapshot.get("cum_volume"))
        self._last_bid1 = _safe_float(snapshot.get("bid1"))
        self._last_ask1 = _safe_float(snapshot.get("ask1"))
        self._last_bid_qty = _safe_int(snapshot.get("bid_qty1"))
        self._last_ask_qty = _safe_int(snapshot.get("ask_qty1"))

    def _handle_tick(self, obj) -> None:
        price = _safe_float(obj.GetHeaderValue(1))
        cum_volume = _safe_int(obj.GetHeaderValue(13))
        oi = _safe_int(obj.GetHeaderValue(14))
        raw_tick_time = _safe_str(obj.GetHeaderValue(15))
        tick_time = self._parse_tick_time(raw_tick_time)
        ask1 = _safe_float(obj.GetHeaderValue(18))
        bid1 = _safe_float(obj.GetHeaderValue(19))
        ask_qty1 = _safe_int(obj.GetHeaderValue(20))
        bid_qty1 = _safe_int(obj.GetHeaderValue(21))
        buy_sell_flag = _safe_str(obj.GetHeaderValue(24))

        volume = max(0, cum_volume - self._last_cum_volume) if self._last_cum_volume else 0
        self._last_cum_volume = cum_volume

        if bid1 > 0:
            self._last_bid1 = bid1
        if ask1 > 0:
            self._last_ask1 = ask1
        if bid_qty1 > 0:
            self._last_bid_qty = bid_qty1
        if ask_qty1 > 0:
            self._last_ask_qty = ask_qty1

        is_buy_tick = True
        if buy_sell_flag == "2":
            is_buy_tick = False
        elif buy_sell_flag not in ("1", "2"):
            is_buy_tick = price >= self._last_price if self._last_price else True

        self._last_price = price
        bar_ts = tick_time.replace(second=0, microsecond=0)
        bar_min = bar_ts.hour * 60 + bar_ts.minute
        self._tick_event_count += 1
        if self._tick_event_count <= 5 or self._tick_event_count % 100 == 0:
            sys_log.info(
                "[CybosRT-TICK] #%d code=%s raw_time=%s parsed=%s price=%.2f vol=%d bid1=%.2f ask1=%.2f flag=%s",
                self._tick_event_count,
                self._rt_code,
                raw_tick_time,
                tick_time.strftime("%H:%M:%S"),
                price,
                volume,
                self._last_bid1,
                self._last_ask1,
                buy_sell_flag,
            )

        self._update_bar(
            bar_ts=bar_ts,
            bar_min=bar_min,
            price=price,
            volume=volume,
            bid1=self._last_bid1,
            ask1=self._last_ask1,
            bid_q=self._last_bid_qty,
            ask_q=self._last_ask_qty,
            oi=oi,
            is_buy_tick=is_buy_tick,
        )

    def _handle_hoga(self, obj) -> None:
        ask_prices = [_safe_float(obj.GetHeaderValue(idx)) for idx in (2, 3, 4, 5, 6)]
        ask_qtys = [_safe_int(obj.GetHeaderValue(idx)) for idx in (7, 8, 9, 10, 11)]
        bid_prices = [_safe_float(obj.GetHeaderValue(idx)) for idx in (19, 20, 21, 22, 23)]
        bid_qtys = [_safe_int(obj.GetHeaderValue(idx)) for idx in (24, 25, 26, 27, 28)]

        bid1 = bid_prices[0] if bid_prices else 0.0
        ask1 = ask_prices[0] if ask_prices else 0.0
        bid_q = bid_qtys[0] if bid_qtys else 0
        ask_q = ask_qtys[0] if ask_qtys else 0

        if bid1 > 0:
            self._last_bid1 = bid1
        if ask1 > 0:
            self._last_ask1 = ask1
        if bid_q > 0:
            self._last_bid_qty = bid_q
        if ask_q > 0:
            self._last_ask_qty = ask_q

        self._last_hoga_snapshot = {
            "bid_prices": bid_prices,
            "ask_prices": ask_prices,
            "bid_qtys": bid_qtys,
            "ask_qtys": ask_qtys,
        }
        self._hoga_event_count += 1
        if self._hoga_event_count <= 5 or self._hoga_event_count % 200 == 0:
            sys_log.info(
                "[CybosRT-HOGA] #%d code=%s bid1=%.2f/%d ask1=%.2f/%d",
                self._hoga_event_count,
                self._rt_code,
                self._last_bid1,
                self._last_bid_qty,
                self._last_ask1,
                self._last_ask_qty,
            )

        if self._current_bar is not None:
            self._current_bar["bid1"] = self._last_bid1
            self._current_bar["ask1"] = self._last_ask1
            self._current_bar["bid_qty"] = self._last_bid_qty
            self._current_bar["ask_qty"] = self._last_ask_qty
            self._current_bar["hoga_levels"] = dict(self._last_hoga_snapshot)

        if self._on_hoga is not None:
            try:
                self._on_hoga(
                    self._last_bid1,
                    self._last_ask1,
                    self._last_bid_qty,
                    self._last_ask_qty,
                    dict(self._last_hoga_snapshot),
                )
            except TypeError:
                self._on_hoga(
                    self._last_bid1,
                    self._last_ask1,
                    self._last_bid_qty,
                    self._last_ask_qty,
                )

    def _update_bar(
        self,
        *,
        bar_ts: datetime,
        bar_min: int,
        price: float,
        volume: int,
        bid1: float,
        ask1: float,
        bid_q: int,
        ask_q: int,
        oi: int,
        is_buy_tick: bool,
    ) -> None:
        if self._current_min is not None and bar_min != self._current_min:
            sys_log.info(
                "[CybosRT-ROLLOVER] code=%s from=%s to=%s",
                self._rt_code,
                self._current_bar["ts"].strftime("%H:%M") if self._current_bar else "?",
                bar_ts.strftime("%H:%M"),
            )
            self._close_current_bar()

        buy_v = volume if is_buy_tick else 0
        sell_v = 0 if is_buy_tick else volume

        if self._current_bar is None:
            self._current_bar = {
                "ts": bar_ts,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": volume,
                "buy_vol": buy_v,
                "sell_vol": sell_v,
                "bid1": bid1,
                "ask1": ask1,
                "bid_qty": bid_q,
                "ask_qty": ask_q,
                "hoga_levels": dict(self._last_hoga_snapshot),
                "oi": oi,
            }
            self._current_min = bar_min
        else:
            bar = self._current_bar
            bar["high"] = max(bar["high"], price)
            bar["low"] = min(bar["low"], price)
            bar["close"] = price
            bar["volume"] += volume
            bar["buy_vol"] = bar.get("buy_vol", 0) + buy_v
            bar["sell_vol"] = bar.get("sell_vol", 0) + sell_v
            bar["bid1"] = bid1
            bar["ask1"] = ask1
            bar["bid_qty"] = bid_q
            bar["ask_qty"] = ask_q
            bar["hoga_levels"] = dict(self._last_hoga_snapshot)
            bar["oi"] = oi

        if self._on_tick is not None:
            self._on_tick(dict(self._current_bar))

    def _close_current_bar(self) -> None:
        if self._current_bar is None:
            return
        closed = dict(self._current_bar)
        # Clear rollover state before invoking callbacks because the minute
        # pipeline can re-enter the Qt event loop and trigger nested ticks.
        self._current_bar = None
        self._current_min = None
        self._candles.append(closed)
        sys_log.info(
            "[BAR-CLOSE][CYBOS] ts=%s O=%.2f H=%.2f L=%.2f C=%.2f V=%d",
            closed["ts"].strftime("%H:%M"),
            closed["open"],
            closed["high"],
            closed["low"],
            closed["close"],
            closed["volume"],
        )
        if self._on_candle_closed is not None:
            try:
                self._on_candle_closed(closed)
            except Exception:
                sys_log.exception("[BAR-CLOSE][CYBOS] on_candle_closed callback failed")

    @staticmethod
    def _parse_tick_time(raw_time: str) -> datetime:
        now = datetime.now()
        digits = "".join(ch for ch in _safe_str(raw_time) if ch.isdigit())
        if len(digits) in (5, 6):
            digits = digits.zfill(6)
        if len(digits) >= 6:
            try:
                hh = int(digits[0:2])
                mm = int(digits[2:4])
                ss = int(digits[4:6])
                return now.replace(hour=hh, minute=mm, second=ss, microsecond=0)
            except Exception:
                return now
        return now
