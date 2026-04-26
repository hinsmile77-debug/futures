# collection/kiwoom/realtime_data.py — 1분봉 실시간 수신 및 조립
"""
키움 FC0(선물 체결) 실시간 틱을 받아 1분봉 OHLCV 캔들을 완성한다.

흐름:
  1. KiwoomAPI.register_realtime() 으로 FC0 등록
  2. 틱 수신마다 _on_tick() 호출
  3. 분(minute)이 바뀌면 이전 분봉을 확정 → on_candle_closed 콜백 호출
  4. 초기 분봉은 OPT50029 TR로 로드 → deque에 prepend

캔들 dict 형식:
  {
    "ts"     : datetime  (bar 시작 시각 — 초·마이크로초 제거)
    "open"   : float
    "high"   : float
    "low"    : float
    "close"  : float
    "volume" : int
    "bid1"   : float
    "ask1"   : float
    "bid_qty": int
    "ask_qty": int
    "oi"     : int       (미결제약정)
  }
"""

import logging
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Callable, Deque, Dict, List, Optional

from config.constants import (
    FID_FUTURES_PRICE, FID_FUTURES_VOL,
    FID_BID_PRICE, FID_ASK_PRICE,
    FID_BID_QTY, FID_ASK_QTY, FID_OI,
    RT_FUTURES, TR_FUTURES_1MIN,
)
from collection.kiwoom.api_connector import KiwoomAPI

logger = logging.getLogger(__name__)

# 보관할 최대 분봉 수 (약 1거래일 + 여유)
MAX_CANDLES = 500

# OPT50029 초기 로드 분봉 수
INIT_CANDLES = 120

# 분봉 확정 후 전달할 때 틱 지연 버퍼 (ms)
CANDLE_EMIT_DELAY_MS = 50


class RealtimeData:
    """
    선물 1분봉 실시간 수집기.

    Parameters
    ----------
    api         : KiwoomAPI 인스턴스
    code        : 선물 종목 코드 (예: "101W06")
    screen_no   : 실시간 등록 화면 번호
    on_candle_closed : 분봉 완성 시 호출되는 콜백(candle: dict) → None
    on_tick     : 틱 수신마다 호출 (candle: dict — 현재 미완성 bar) → None
    """

    def __init__(
        self,
        api: KiwoomAPI,
        code: str,
        screen_no: str = "3000",
        on_candle_closed: Optional[Callable] = None,
        on_tick: Optional[Callable] = None,
    ):
        self.api = api
        self.code = code
        self.screen_no = screen_no

        self._on_candle_closed = on_candle_closed
        self._on_tick = on_tick

        self._candles: Deque[Dict] = deque(maxlen=MAX_CANDLES)
        self._current_bar: Optional[Dict] = None   # 미완성 현재 bar
        self._current_min: Optional[int] = None    # 현재 bar의 분 (0–1439)

        # 틱 수신 시 latency 측정용 (latency_sync 연동)
        self._last_tick_recv_ns: int = 0

        self._running: bool = False

    # ── 시작 / 중지 ───────────────────────────────────────────

    def start(self, load_history: bool = True) -> None:
        """초기 분봉 로드 후 실시간 등록."""
        if self._running:
            return

        if load_history:
            self._load_initial_candles()

        self.api.register_realtime(
            code=self.code,
            real_type=RT_FUTURES,
            screen_no=self.screen_no,
            callback=self._on_real_data,
        )
        self._running = True
        logger.info("[RealtimeData] 실시간 수신 시작 — %s", self.code)

    def stop(self) -> None:
        """실시간 등록 해제."""
        if not self._running:
            return
        self.api.unregister_realtime(self.code, self.screen_no)
        self._running = False
        logger.info("[RealtimeData] 실시간 수신 중지 — %s", self.code)

    # ── 데이터 접근 ───────────────────────────────────────────

    @property
    def candles(self) -> Deque[Dict]:
        """완성된 분봉 deque (오래된 것이 앞)."""
        return self._candles

    @property
    def latest_closed(self) -> Optional[Dict]:
        """가장 최근 완성 분봉."""
        return self._candles[-1] if self._candles else None

    @property
    def current_bar(self) -> Optional[Dict]:
        """현재 진행 중인 미완성 분봉."""
        return self._current_bar

    def get_last_n(self, n: int) -> List[Dict]:
        """최근 n개 완성 분봉 반환 (오래된 → 최신 순)."""
        candles = list(self._candles)
        return candles[-n:] if len(candles) >= n else candles

    # ── 초기 분봉 로드 ────────────────────────────────────────

    def _load_initial_candles(self) -> None:
        """OPT50029 TR로 최근 INIT_CANDLES 개 분봉 로드."""
        logger.info("[RealtimeData] 초기 분봉 로드 중 (%d개)...", INIT_CANDLES)
        result = self.api.request_tr(
            tr_code=TR_FUTURES_1MIN,
            rq_name="init_1min",
            inputs={
                "종목코드": self.code,
                "틱범위": "1",
                "수정주가구분": "0",
            },
            screen_no="2001",
        )
        if result is None:
            logger.warning("[RealtimeData] 초기 분봉 로드 실패")
            return

        rows = result.get("rows", [])[:INIT_CANDLES]
        rows.reverse()   # API는 최신순 → 과거→최신으로 정렬

        for row in rows:
            candle = self._parse_tr_candle(row)
            if candle:
                self._candles.append(candle)

        logger.info("[RealtimeData] 초기 분봉 %d개 로드 완료", len(self._candles))

    # ── 실시간 틱 처리 ────────────────────────────────────────

    def _on_real_data(self, code: str, real_type: str, real_data: str) -> None:
        """KiwoomAPI.real_data_event 콜백 — FC0 선물 체결."""
        if code != self.code or real_type != RT_FUTURES:
            return

        self._last_tick_recv_ns = time.perf_counter_ns()

        try:
            price  = float(self.api.get_real_data(code, FID_FUTURES_PRICE).replace("+", "").replace("-", "-"))
            volume = abs(int(self.api.get_real_data(code, FID_FUTURES_VOL)))
            bid1   = self._safe_float(self.api.get_real_data(code, FID_BID_PRICE))
            ask1   = self._safe_float(self.api.get_real_data(code, FID_ASK_PRICE))
            bid_q  = self._safe_int(self.api.get_real_data(code, FID_BID_QTY))
            ask_q  = self._safe_int(self.api.get_real_data(code, FID_ASK_QTY))
            oi     = self._safe_int(self.api.get_real_data(code, FID_OI))
        except (ValueError, TypeError) as e:
            logger.debug("틱 파싱 오류: %s", e)
            return

        now = datetime.now()
        bar_ts = now.replace(second=0, microsecond=0)
        bar_min = now.hour * 60 + now.minute

        self._update_bar(bar_ts, bar_min, price, volume, bid1, ask1, bid_q, ask_q, oi)

    def _update_bar(
        self,
        bar_ts: datetime,
        bar_min: int,
        price: float,
        volume: int,
        bid1: float,
        ask1: float,
        bid_q: int,
        ask_q: int,
        oi: int,
    ) -> None:
        # 분이 바뀌었으면 이전 bar 확정
        if self._current_min is not None and bar_min != self._current_min:
            self._close_current_bar()

        if self._current_bar is None:
            # 새 bar 시작
            self._current_bar = {
                "ts":      bar_ts,
                "open":    price,
                "high":    price,
                "low":     price,
                "close":   price,
                "volume":  volume,
                "bid1":    bid1,
                "ask1":    ask1,
                "bid_qty": bid_q,
                "ask_qty": ask_q,
                "oi":      oi,
            }
            self._current_min = bar_min
        else:
            # 기존 bar 업데이트
            bar = self._current_bar
            bar["high"]    = max(bar["high"], price)
            bar["low"]     = min(bar["low"], price)
            bar["close"]   = price
            bar["volume"] += volume
            bar["bid1"]    = bid1
            bar["ask1"]    = ask1
            bar["bid_qty"] = bid_q
            bar["ask_qty"] = ask_q
            bar["oi"]      = oi

        if self._on_tick is not None:
            try:
                self._on_tick(dict(self._current_bar))
            except Exception:
                logger.exception("on_tick 콜백 오류")

    def _close_current_bar(self) -> None:
        """현재 bar를 확정하고 deque에 추가, 콜백 호출."""
        if self._current_bar is None:
            return
        closed = dict(self._current_bar)
        self._candles.append(closed)
        logger.debug(
            "분봉 확정: %s  O=%.2f H=%.2f L=%.2f C=%.2f V=%d",
            closed["ts"].strftime("%H:%M"),
            closed["open"], closed["high"], closed["low"], closed["close"], closed["volume"],
        )
        if self._on_candle_closed is not None:
            try:
                self._on_candle_closed(closed)
            except Exception:
                logger.exception("on_candle_closed 콜백 오류")

        self._current_bar = None
        self._current_min = None

    # ── TR 분봉 파싱 ──────────────────────────────────────────

    @staticmethod
    def _parse_tr_candle(row: Dict[str, str]) -> Optional[Dict]:
        """OPT50029 TR 한 행 → 분봉 dict."""
        try:
            ts_str = row.get("체결시간", "")
            if len(ts_str) < 12:
                return None
            # 형식: YYYYMMDDHHMI (12자리) 또는 HHMI (4자리 — 당일만)
            if len(ts_str) == 12:
                ts = datetime.strptime(ts_str, "%Y%m%d%H%M")
            elif len(ts_str) == 8:
                ts = datetime.strptime(ts_str, "%Y%m%d")
            else:
                date_part = ts_str[:8]
                time_part = ts_str[8:12]
                ts = datetime.strptime(date_part + time_part, "%Y%m%d%H%M")

            return {
                "ts":      ts,
                "open":    abs(float(row.get("시가",  "0") or "0")),
                "high":    abs(float(row.get("고가",  "0") or "0")),
                "low":     abs(float(row.get("저가",  "0") or "0")),
                "close":   abs(float(row.get("현재가","0") or "0")),
                "volume":  abs(int(float(row.get("거래량","0") or "0"))),
                "bid1":    0.0,
                "ask1":    0.0,
                "bid_qty": 0,
                "ask_qty": 0,
                "oi":      0,
            }
        except (ValueError, KeyError) as e:
            logger.debug("TR 분봉 파싱 오류: %s | row=%s", e, row)
            return None

    # ── 유틸 ──────────────────────────────────────────────────

    @staticmethod
    def _safe_float(s: str) -> float:
        try:
            return float(s.replace("+", "")) if s else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _safe_int(s: str) -> int:
        try:
            return int(float(s)) if s else 0
        except ValueError:
            return 0
