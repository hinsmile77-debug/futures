from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from typing import Callable, Deque, Dict, List, Optional

from collection.cybos.api_connector import CybosAPI, _safe_float, _safe_int, _safe_str

logger = logging.getLogger(__name__)
sys_log = logging.getLogger("SYSTEM")
hoga_log = logging.getLogger("HOGA")

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
        self._last_closed_min: Optional[int] = None  # 중복 BAR-CLOSE 감지용

        self._tick_subscription = None
        self._hoga_subscription = None

        self._last_price = 0.0
        self._last_cum_volume = 0
        self._last_bid1 = 0.0
        self._last_ask1 = 0.0
        self._last_bid_qty = 0
        self._last_ask_qty = 0
        self._last_oi = 0
        self._last_hoga_snapshot = {
            "bid_prices": [],
            "ask_prices": [],
            "bid_qtys": [],
            "ask_qtys": [],
        }
        self._tick_event_count = 0
        self._hoga_event_count = 0
        # [404차 후속6] 당일 상한가/하한가 (FutureMst 스냅샷에서 1회 확보, 0.0=미확보)
        self._upper_limit: float = 0.0
        self._lower_limit: float = 0.0

    @property
    def daily_limits(self) -> Dict[str, float]:
        """[404차 후속6] 당일 상한가/하한가. 미확보 시 0.0.

        `_prime_from_snapshot()`이 FutureMst 스냅샷에서 채운다. 인덱스
        (`CYBOS_FUTUREMST_*_LIMIT_IDX`)가 실측 전이면 0.0이 유지되고, 소비처는
        "상한가 정보 없음"으로 처리해 기존 동작을 그대로 유지한다.

        하루 중 바뀌지 않는 값이라 기동 시 1회 조회로 충분하다(가격제한폭 단계
        확대가 일어나면 달라지지만, 그 경우도 재기동 전까지는 보수적으로 좁은
        값을 유지하므로 과잉 차단이 아니라 과소 차단 방향이라 안전하다).
        """
        return {"upper": self._upper_limit, "lower": self._lower_limit}

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

        # pre_market_setup()에서 이미 _prime_from_snapshot()을 실행한 경우 재호출 스킵.
        # 09:00 정각 BlockRequest 병목을 방지한다 (이상점 2 수정).
        if self._last_price > 0.0:
            sys_log.info(
                "[CybosRT-START] snapshot skipped (pre-warmed) code=%s price=%.2f bid1=%.2f ask1=%.2f",
                self._rt_code,
                self._last_price,
                self._last_bid1,
                self._last_ask1,
            )
        else:
            sys_log.info("[CybosRT-START] snapshot begin code=%s", self._rt_code)
            self._prime_from_snapshot()
            sys_log.info(
                "[CybosRT-START] snapshot end code=%s price=%.2f oi=%d bid1=%.2f ask1=%.2f",
                self._rt_code,
                self._last_price,
                self._last_oi,
                self._last_bid1,
                self._last_ask1,
            )
        sys_log.info("[CybosRT-START] tick subscribe begin code=%s", self._rt_code)
        self._tick_subscription = self.api.create_subscription(
            progid=FUTURE_CUR_ONLY_PROGID,
            input_values={0: self._rt_code},
            owner=self,
            event_name="tick",
            latest=False,
        )
        sys_log.info("[CybosRT-START] tick subscribe end code=%s", self._rt_code)
        sys_log.info("[CybosRT-START] hoga subscribe begin code=%s", self._rt_code)
        self._hoga_subscription = self.api.create_subscription(
            progid=FUTURE_JP_BID_PROGID,
            input_values={0: self._rt_code},
            owner=self,
            event_name="hoga",
            latest=False,
        )
        sys_log.info("[CybosRT-START] hoga subscribe end code=%s", self._rt_code)
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
        sys_log.debug("[CybosRT-EVENT] dispatch event=%s code=%s", event_name, self._rt_code)
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
        oi_init = _safe_int(snapshot.get("open_interest", 0))
        if oi_init > 0:
            self._last_oi = oi_init
        # [404차 후속6] 당일 상한가/하한가. 값이 서로 모순되면(상한<=하한, 또는 현재가가
        # 밖에 있음) 잘못된 인덱스를 읽은 것이므로 채택하지 않는다 — 2026-05-10 B51처럼
        # 인덱스 오매핑이 조용히 흘러드는 것을 막는 방어선이다.
        _up = _safe_float(snapshot.get("upper_limit", 0.0))
        _dn = _safe_float(snapshot.get("lower_limit", 0.0))
        _px = _safe_float(snapshot.get("price", 0.0))
        if _up > 0 and _dn > 0 and _up > _dn and (not _px or _dn <= _px <= _up):
            self._upper_limit, self._lower_limit = _up, _dn
            logger.info("[DailyLimit] 상한가=%.2f 하한가=%.2f (현재가=%.2f)", _up, _dn, _px)
        elif _up or _dn:
            logger.warning(
                "[DailyLimit] 값 모순으로 미채택 — upper=%.2f lower=%.2f price=%.2f. "
                "CYBOS_FUTUREMST_*_LIMIT_IDX 인덱스를 재확인할 것"
                "(scripts/probe_cybos_limit_price.py)", _up, _dn, _px)

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
        if oi > 0:
            self._last_oi = oi

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

        # 버퍼 재생 틱 감지: 체결 시각이 현재보다 90초 이상 오래됐으면 실제 시각 사용.
        # Cybos 재구독 시 버퍼된 과거 틱들이 느린 속도로 재생되면 봉 전환이 영구 차단됨.
        _now = datetime.now()
        _stale_sec = (_now - tick_time).total_seconds()
        if _stale_sec > 90:
            _actual_bar_ts = _now.replace(second=0, microsecond=0)
            _actual_bar_min = _actual_bar_ts.hour * 60 + _actual_bar_ts.minute
            # [stale oscillation 근본 수정 — _last_closed_min 기준 단조증가]
            #
            # 이전 수정(_current_min 기준)의 버그:
            #   _close_current_bar()가 _current_min = None 으로 리셋하므로
            #   봉 전환 직후 다음 stale 틱에서 보정 조건이 항상 False → 역행 봉 재생성.
            #
            # 올바른 기준: _last_closed_min (닫힌 봉의 분 인덱스, None으로 리셋 안 됨).
            #   stale actual_bar_min <= _last_closed_min 이면 이미 닫힌 구간 →
            #   _last_closed_min + 1(현재 진행 중인 봉)으로 교정하여 역행 봉 생성 방지.
            _ref = self._last_closed_min
            if _ref is not None and _actual_bar_min <= _ref:
                _actual_bar_min = _ref + 1
                _actual_bar_ts = _actual_bar_ts.replace(
                    hour=_actual_bar_min // 60,
                    minute=_actual_bar_min % 60,
                )
            sys_log.warning(
                "[CybosRT-STALE] code=%s stale=%.0fs raw_time=%s → actual=%s",
                self._rt_code, _stale_sec,
                tick_time.strftime("%H:%M:%S"),
                _actual_bar_ts.strftime("%H:%M"),
            )
            bar_ts = _actual_bar_ts
            bar_min = _actual_bar_min

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

        active = sum(
            1 for i in range(5) if bid_prices[i] > 0 and ask_prices[i] > 0
        )
        level_parts = " ".join(
            "L%d: bid=%.2f/%d ask=%.2f/%d" % (
                i + 1,
                bid_prices[i], bid_qtys[i],
                ask_prices[i], ask_qtys[i],
            )
            for i in range(5)
        )
        hoga_log.debug(
            "[HOGA] code=%s active_levels=%d/5 %s",
            self._rt_code, active, level_parts,
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
                "code": self.code,
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
                # [349차] 분당 틱수 급변장 사전 가드용 — 이 봉에서 수신한 틱 메시지 수
                # (체결량과 별개로, 주문흐름 자체의 폭주 여부를 보는 지표).
                "tick_count": 1,
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
            bar["tick_count"] = bar.get("tick_count", 0) + 1

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
        _closed_min = closed["ts"].hour * 60 + closed["ts"].minute
        # 중복 BAR-CLOSE 감지: 같은 분봉이 두 번 이상 닫히면 경고
        if self._last_closed_min is not None and _closed_min <= self._last_closed_min:
            sys_log.warning(
                "[BAR-CLOSE][DUPLICATE] ts=%s 이미 닫힌 봉 재발화 "
                "(last_closed=%02d:%02d, cur=%02d:%02d) — stale oscillation 가능성",
                closed["ts"].strftime("%H:%M"),
                self._last_closed_min // 60, self._last_closed_min % 60,
                _closed_min // 60, _closed_min % 60,
            )
        self._last_closed_min = _closed_min
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
