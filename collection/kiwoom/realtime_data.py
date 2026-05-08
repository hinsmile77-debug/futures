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

from PyQt5.QtCore import QTimer

from config.constants import (
    FID_FUTURES_PRICE, FID_FUTURES_VOL,
    FID_BID_PRICE, FID_ASK_PRICE,
    FID_BID_QTY, FID_ASK_QTY, FID_OI,
    FUTURES_BID_PRICE_FIDS, FUTURES_ASK_PRICE_FIDS,
    FUTURES_BID_QTY_FIDS, FUTURES_ASK_QTY_FIDS,
    RT_FUTURES, RT_FUTURES_HOGA, TR_FUTURES_1MIN,
)
from collection.kiwoom.api_connector import KiwoomAPI

logger    = logging.getLogger(__name__)
sys_log   = logging.getLogger("SYSTEM")   # 폴링 추적 → SYSTEM.log + WARN.log
hoga_log  = logging.getLogger("HOGA")

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
    api             : KiwoomAPI 인스턴스
    code            : OPT50029 분봉 TR용 코드 (예: "A0166000")
    screen_no       : 실시간 등록 화면 번호
    on_candle_closed : 분봉 완성 시 호출되는 콜백(candle: dict) → None
    on_tick         : 틱 수신마다 호출 (candle: dict — 현재 미완성 bar) → None
    on_hoga         : 호가 변경마다 호출 (bid1, ask1, bid_qty, ask_qty) → None
                      OFI 업데이트용 — 선물호가잔량 이벤트마다 직접 호출됨
    realtime_code   : SetRealReg 실시간 구독용 코드.
                      None이면 code와 동일하게 사용.
    is_mock_server  : True = 모의투자 서버 → OPT50029 30초 폴링으로 분봉 수집.
                      False = SetRealReg 실시간 수신 (모의/실전 모두 사용 가능).
    """

    # 모의투자 폴링 간격 (ms)
    _POLL_INTERVAL_MS = 30_000

    def __init__(
        self,
        api: KiwoomAPI,
        code: str,
        screen_no: str = "3000",
        on_candle_closed: Optional[Callable] = None,
        on_tick: Optional[Callable] = None,
        on_hoga: Optional[Callable] = None,
        realtime_code: Optional[str] = None,
        is_mock_server: bool = False,
    ):
        self.api = api
        self.code = code                              # OPT50029 분봉 TR용
        self._rt_code = realtime_code or code         # SetRealReg 실시간용
        self.screen_no = screen_no
        self._is_mock = is_mock_server

        self._on_candle_closed = on_candle_closed
        self._on_tick = on_tick
        self._on_hoga = on_hoga

        self._candles: Deque[Dict] = deque(maxlen=MAX_CANDLES)
        self._current_bar: Optional[Dict] = None   # 미완성 현재 bar
        self._current_min: Optional[int] = None    # 현재 bar의 분 (0–1439)

        # 틱 수신 시 latency 측정용 (latency_sync 연동)
        self._last_tick_recv_ns: int = 0

        # 틱 방향 판단용 직전 가격 (tick test — FC0 부호는 전일대비 방향, 틱 방향 아님)
        self._prev_tick_price: float = 0.0

        # 최신 호가 (선물호가잔량에서 갱신 — 선물시세에는 bid/ask FID 없음)
        self._last_bid1: float = 0.0
        self._last_ask1: float = 0.0
        self._last_bid_qty: int = 0
        self._last_ask_qty: int = 0
        self._last_hoga_snapshot: Dict[str, List[float]] = {
            "bid_prices": [],
            "ask_prices": [],
            "bid_qtys": [],
            "ask_qtys": [],
        }

        # 모의투자 폴링 상태
        self._poll_timer: Optional[QTimer] = None
        self._last_polled_ts: Optional[datetime] = None  # 마지막으로 처리한 분봉 ts

        self._running: bool = False

    # ── 시작 / 중지 ───────────────────────────────────────────

    def start(self, load_history: bool = True) -> None:
        """실시간 등록 후 초기 분봉 로드."""
        if self._running:
            return

        # 선물시세(체결) 실시간 등록
        print(f"[DBG RD-START] register_realtime 직전 rt_code={self._rt_code!r} tr_code={self.code!r} mock={self._is_mock}", flush=True)
        self.api.register_realtime(
            code=self._rt_code,
            real_type=RT_FUTURES,
            screen_no=self.screen_no,
            callback=self._on_real_data,
            sopt_type="0",
        )
        # 선물호가잔량 실시간 등록 — 기존 선물시세 등록 유지(sopt_type="1")
        # bid/ask FID는 선물시세에 없고 선물호가잔량 전용 → OFI 정상화
        self.api.register_realtime(
            code=self._rt_code,
            real_type=RT_FUTURES_HOGA,
            screen_no=self.screen_no,
            callback=self._on_hoga_data,
            sopt_type="1",
        )
        self._running = True
        self._tick_count = 0
        self._hoga_count = 0
        logger.info("[RealtimeData] 실시간 수신 시작 — TR코드=%s RT코드=%s mock=%s",
                    self.code, self._rt_code, self._is_mock)
        hoga_log.info(
            "[HOGA-CONFIG] code=%s bid_price_fids=%s ask_price_fids=%s bid_qty_fids=%s ask_qty_fids=%s",
            self._rt_code,
            FUTURES_BID_PRICE_FIDS,
            FUTURES_ASK_PRICE_FIDS,
            FUTURES_BID_QTY_FIDS,
            FUTURES_ASK_QTY_FIDS,
        )
        print(f"[DBG RD-START] register_realtime 완료 (선물시세 + 선물호가잔량)", flush=True)

        if load_history:
            self._load_initial_candles()

        # 모의투자: SetRealReg 틱 미지원 → OPT50029 폴링으로 분봉 수집
        if self._is_mock:
            self._start_polling()

    def stop(self) -> None:
        """실시간 등록 해제."""
        if not self._running:
            return
        if self._poll_timer is not None:
            self._poll_timer.stop()
            self._poll_timer = None
        self.api.unregister_realtime(self.code, self.screen_no)
        self._running = False
        logger.info("[RealtimeData] 실시간 수신 중지 — %s", self.code)

    # ── 모의투자 폴링 ──────────────────────────────────────────

    def _start_polling(self) -> None:
        """OPT50029 30초 폴링 타이머 시작 (모의투자 전용)."""
        # 모의투자 서버는 체결시간이 고정값 반환 → wall clock 기준으로 분봉 감지
        # (캔들 deque의 ts를 쓰면 항상 같은 값이어서 비교가 영원히 True가 됨)
        self._last_polled_ts = None
        self._poll_timer = QTimer()
        self._poll_timer.timeout.connect(self._poll_opt50029)
        self._poll_timer.start(self._POLL_INTERVAL_MS)
        sys_log.info("[POLL] 모의투자 OPT50029 폴링 시작 (%ds 간격) code=%s",
                     self._POLL_INTERVAL_MS // 1000, self.code)

    def _poll_opt50029(self) -> None:
        """OPT50029 조회 → wall clock 기준 새 완성 분봉 감지 시 on_candle_closed 호출."""
        from utils.time_utils import is_market_open
        now = datetime.now()
        if not is_market_open(now):
            return

        # 모의투자는 체결시간이 고정값 → wall clock으로 방금 완성된 분봉 시각 계산
        completed_min = now.replace(second=0, microsecond=0) - timedelta(minutes=1)

        sys_log.info("[POLL] tick %s | completed=%s | last=%s",
                     now.strftime("%H:%M:%S"),
                     completed_min.strftime("%H:%M"),
                     self._last_polled_ts.strftime("%H:%M") if self._last_polled_ts else "None")

        if self._last_polled_ts is not None and completed_min <= self._last_polled_ts:
            return  # 이미 처리한 분봉

        # 새 분봉 — OPT50029 TR 조회
        sys_log.info("[POLL] ★ 새 분봉 감지 completed=%s — TR 조회", completed_min.strftime("%H:%M"))
        result = self.api.request_tr(
            tr_code=TR_FUTURES_1MIN,
            rq_name="poll_1min",
            inputs={"종목코드": self.code, "시간단위": "1"},
            screen_no="2002",
        )
        if result is None:
            sys_log.warning("[POLL] OPT50029 결과 None — TR 타임아웃 또는 실패")
            return

        rows = result.get("rows", [])
        sys_log.info("[POLL] TR 수신 rows=%d", len(rows))
        if not rows:
            sys_log.warning("[POLL] rows=0 — 빈 응답")
            return

        # API 응답은 최신순 — rows[0]이 가장 최근 완성 분봉
        latest = self._parse_tr_candle(rows[0])
        if latest is None:
            sys_log.warning("[POLL] rows[0] 파싱 실패: %s", rows[0])
            return

        # ts를 wall clock 기준으로 오버라이드 (mock 서버의 고정 ts 무시)
        latest["ts"] = completed_min
        self._last_polled_ts = completed_min

        sys_log.info("[POLL] ★ 분봉 확정 ts=%s close=%.2f", completed_min, latest.get("close", 0))
        self._candles.append(latest)

        if self._on_candle_closed:
            try:
                self._on_candle_closed(latest)
            except Exception:
                logger.exception("[POLL] on_candle_closed 오류")

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

    @staticmethod
    def _format_hoga_snapshot(snapshot: Dict[str, List[float]]) -> str:
        bid_prices = snapshot.get("bid_prices", [])
        ask_prices = snapshot.get("ask_prices", [])
        bid_qtys = snapshot.get("bid_qtys", [])
        ask_qtys = snapshot.get("ask_qtys", [])
        parts = []
        for idx in range(min(len(bid_prices), len(ask_prices), len(bid_qtys), len(ask_qtys))):
            parts.append(
                f"L{idx + 1}: bid={bid_prices[idx]:.2f}/{bid_qtys[idx]} ask={ask_prices[idx]:.2f}/{ask_qtys[idx]}"
            )
        return " | ".join(parts)

    @staticmethod
    def _detect_active_hoga_levels(snapshot: Dict[str, List[float]]) -> int:
        levels = 0
        for bid_p, ask_p, bid_q, ask_q in zip(
            snapshot.get("bid_prices", []),
            snapshot.get("ask_prices", []),
            snapshot.get("bid_qtys", []),
            snapshot.get("ask_qtys", []),
        ):
            if any(float(v or 0) > 0 for v in (bid_p, ask_p, bid_q, ask_q)):
                levels += 1
        return levels

    # ── 초기 분봉 로드 ────────────────────────────────────────

    def _load_initial_candles(self) -> None:
        """OPT50029 TR로 최근 INIT_CANDLES 개 분봉 로드."""
        logger.info("[RealtimeData] 초기 분봉 로드 중 (%d개)...", INIT_CANDLES)
        result = self.api.request_tr(
            tr_code=TR_FUTURES_1MIN,
            rq_name="init_1min",
            inputs={
                "종목코드": self.code,
                "시간단위": "1",
                "수정주가구분": "0",
            },
            screen_no="2001",
        )
        if result is None:
            logger.warning("[RealtimeData] 초기 분봉 로드 실패")
            return

        rows = result.get("rows", [])[:INIT_CANDLES]
        if not rows:
            logger.warning(
                "[RealtimeData] OPT50029 응답 rows=0 — "
                "장외 시간이거나 시뮬레이션 서버 미지원. "
                "초기 분봉 없이 실시간 틱부터 자동 축적합니다."
            )
            return

        rows.reverse()   # API는 최신순 → 과거→최신으로 정렬

        for row in rows:
            candle = self._parse_tr_candle(row)
            if candle:
                self._candles.append(candle)

        logger.info("[RealtimeData] 초기 분봉 %d개 로드 완료", len(self._candles))

    # ── 실시간 틱 처리 ────────────────────────────────────────

    def _on_real_data(self, code: str, real_type: str, real_data: str) -> None:
        """KiwoomAPI.real_data_event 콜백 — FC0 선물 체결."""
        self._tick_count = getattr(self, "_tick_count", 0) + 1
        # 처음 5틱 + 100틱마다 SYSTEM.log에 기록
        if self._tick_count <= 5 or self._tick_count % 100 == 0:
            sys_log.info("[RT-DATA] #%d code=%r type=%r rt_code=%r RT_FUTURES=%r",
                         self._tick_count, code, real_type, self._rt_code, RT_FUTURES)
        if code.strip() != self._rt_code.strip() or real_type.strip() != RT_FUTURES.strip():
            if self._tick_count <= 5:
                sys_log.warning("[RT-DATA] 필터제외 code=%r rt_code=%r type=%r RT_FUTURES=%r",
                                code, self._rt_code, real_type, RT_FUTURES)
            return

        self._last_tick_recv_ns = time.perf_counter_ns()

        try:
            raw_price = self.api.get_real_data(code, FID_FUTURES_PRICE)
            raw_vol   = self.api.get_real_data(code, FID_FUTURES_VOL)
            # 처음 5틱은 raw 값을 SYSTEM.log에 기록해 파싱 이슈 즉시 확인
            if self._tick_count <= 5:
                sys_log.info("[RT-RAW] #%d raw_price=%r raw_vol=%r",
                             self._tick_count, raw_price, raw_vol)
            price  = abs(float(raw_price.replace("+", "").replace("-", "")))
            is_buy_tick = price >= self._prev_tick_price if self._prev_tick_price else True
            self._prev_tick_price = price
            volume = abs(int(raw_vol)) if raw_vol.strip() else 0
            # bid/ask는 선물시세에 없음 — 선물호가잔량(_on_hoga_data)에서 갱신된 최신값 사용
            bid1  = self._last_bid1
            ask1  = self._last_ask1
            bid_q = self._last_bid_qty
            ask_q = self._last_ask_qty
            oi    = self._safe_int(self.api.get_real_data(code, FID_OI))
        except (ValueError, TypeError) as e:
            sys_log.warning("[RT-PARSE] #%d 틱 파싱 오류: %s | raw_price=%r",
                            self._tick_count, e,
                            locals().get("raw_price", "?"))
            return

        now = datetime.now()
        bar_ts = now.replace(second=0, microsecond=0)
        bar_min = now.hour * 60 + now.minute

        if self._tick_count <= 5:
            sys_log.info("[RT-BAR] #%d price=%.2f vol=%d bar_min=%d cur_min=%s",
                         self._tick_count, price, volume, bar_min, self._current_min)

        self._update_bar(bar_ts, bar_min, price, volume, bid1, ask1, bid_q, ask_q, oi, is_buy_tick)

    def _on_hoga_data(self, code: str, real_type: str, real_data: str) -> None:
        """선물호가잔량 콜백 — 1~5호가 스냅샷 저장 + feature 누적."""
        try:
            bid_prices = [self._safe_float(self.api.get_real_data(code, fid)) for fid in FUTURES_BID_PRICE_FIDS]
            ask_prices = [self._safe_float(self.api.get_real_data(code, fid)) for fid in FUTURES_ASK_PRICE_FIDS]
            bid_qtys = [self._safe_int(self.api.get_real_data(code, fid)) for fid in FUTURES_BID_QTY_FIDS]
            ask_qtys = [self._safe_int(self.api.get_real_data(code, fid)) for fid in FUTURES_ASK_QTY_FIDS]
        except Exception:
            return
        bid1 = bid_prices[0] if bid_prices else 0.0
        ask1 = ask_prices[0] if ask_prices else 0.0
        bid_q = bid_qtys[0] if bid_qtys else 0
        ask_q = ask_qtys[0] if ask_qtys else 0
        if bid1 <= 0 or ask1 <= 0:
            return

        self._last_bid1    = bid1
        self._last_ask1    = ask1
        self._last_bid_qty = bid_q
        self._last_ask_qty = ask_q
        self._last_hoga_snapshot = {
            "bid_prices": bid_prices,
            "ask_prices": ask_prices,
            "bid_qtys": bid_qtys,
            "ask_qtys": ask_qtys,
        }
        self._hoga_count = getattr(self, "_hoga_count", 0) + 1
        active_levels = self._detect_active_hoga_levels(self._last_hoga_snapshot)
        if self._hoga_count <= 20 or self._hoga_count % 100 == 0 or active_levels < len(bid_prices):
            hoga_log.debug(
                "[HOGA] #%d code=%s active_levels=%d/%d %s",
                self._hoga_count,
                code,
                active_levels,
                len(bid_prices),
                self._format_hoga_snapshot(self._last_hoga_snapshot),
            )

        # 현재 진행 중인 bar에도 최신 호가 반영
        if self._current_bar is not None:
            self._current_bar["bid1"]    = bid1
            self._current_bar["ask1"]    = ask1
            self._current_bar["bid_qty"] = bid_q
            self._current_bar["ask_qty"] = ask_q
            self._current_bar["hoga_levels"] = dict(self._last_hoga_snapshot)

        if self._on_hoga is not None:
            try:
                self._on_hoga(bid1, ask1, bid_q, ask_q, dict(self._last_hoga_snapshot))
            except TypeError:
                self._on_hoga(bid1, ask1, bid_q, ask_q)

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
        is_buy_tick: bool = True,
    ) -> None:
        # 분이 바뀌었으면 이전 bar 확정
        if self._current_min is not None and bar_min != self._current_min:
            self._close_current_bar()

        buy_v  = volume if is_buy_tick else 0
        sell_v = 0      if is_buy_tick else volume

        if self._current_bar is None:
            # 새 bar 시작
            self._current_bar = {
                "ts":       bar_ts,
                "open":     price,
                "high":     price,
                "low":      price,
                "close":    price,
                "volume":   volume,
                "buy_vol":  buy_v,
                "sell_vol": sell_v,
                "bid1":     bid1,
                "ask1":     ask1,
                "bid_qty":  bid_q,
                "ask_qty":  ask_q,
                "hoga_levels": dict(self._last_hoga_snapshot),
                "oi":       oi,
            }
            self._current_min = bar_min
        else:
            # 기존 bar 업데이트
            bar = self._current_bar
            bar["high"]     = max(bar["high"], price)
            bar["low"]      = min(bar["low"], price)
            bar["close"]    = price
            bar["volume"]  += volume
            bar["buy_vol"]  = bar.get("buy_vol",  0) + buy_v
            bar["sell_vol"] = bar.get("sell_vol", 0) + sell_v
            bar["bid1"]     = bid1
            bar["ask1"]     = ask1
            bar["bid_qty"]  = bid_q
            bar["ask_qty"]  = ask_q
            bar["hoga_levels"] = dict(self._last_hoga_snapshot)
            bar["oi"]       = oi

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
        sys_log.info("[BAR-CLOSE] ts=%s O=%.2f H=%.2f L=%.2f C=%.2f V=%d",
                     closed["ts"].strftime("%H:%M"),
                     closed["open"], closed["high"], closed["low"],
                     closed["close"], closed["volume"])
        if self._on_candle_closed is not None:
            try:
                self._on_candle_closed(closed)
            except Exception:
                sys_log.exception("[BAR-CLOSE] on_candle_closed 예외")

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
            return abs(float(s.replace("+", ""))) if s else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _safe_int(s: str) -> int:
        try:
            return int(float(s)) if s else 0
        except ValueError:
            return 0
