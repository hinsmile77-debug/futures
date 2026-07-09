from __future__ import annotations

import logging
import platform
import threading
import time
from collections import deque
from typing import Any, Callable, Dict, List, Optional
from logging_system.log_manager import log_manager

try:
    import pythoncom
    from win32com.client import Dispatch, WithEvents
except ImportError:  # pragma: no cover - runtime dependency on 32-bit pywin32
    pythoncom = None
    Dispatch = None
    WithEvents = None

try:
    from PyQt5.QtCore import QTimer
except ImportError:  # pragma: no cover - GUI/runtime dependency
    QTimer = None

logger = logging.getLogger(__name__)
system_logger = logging.getLogger("SYSTEM")
probe_log = logging.getLogger("PROBE")

# Per-key last emission timestamp for throttled diagnostic logs.
_THROTTLED_INFO_TS: Dict[str, float] = {}


CYBOS_RUNTIME_HINT = (
    "Cybos Plus broker requires 32-bit Windows Python with pywin32, "
    "a running U-CYBOS/CYBOS Plus login session, and enabled futures trading."
)

CYBOS_GOODS_CODE_FUTURES = "50"
CYBOS_CONCLUSION_PROGID = "Dscbo1.CpFConclusion"
CYBOS_FUTURES_BALANCE_PROGID = "CpTrade.CpTd0723"
CYBOS_FUTURES_DAILY_PNL_PROGID = "CpTrade.CpTd6197"
CYBOS_FUTURES_ORDER_PROGID = "CpTrade.CpTd6831"
CYBOS_FUTURES_ORDER_MARGIN_QTY_PROGID = "CpTrade.CpTd6722"  # 선물/옵션 신규주문가능 수량 조회
# [260704 감사 P2] KOSPI200 현물지수 코드 — 사용자가 Cybos Plus 클라이언트
# 종목코드검색으로 직접 확인 (2026-07-05). 선물-현물 베이시스 계산용.
# 주의: 코스피200지수는 문맥에 따라 두 코드가 다르다 (둘 다 같은 지수값, TR 네임스페이스만 다름)
#   - "00800" = 선물차트 코드(예: FutOptChart 등 선물 관련 문맥에서 참조)
#   - "K2G01P" = 주식차트 지수코드(예: StockChart/StockMst 등 일반 시세 조회 문맥)
# dscbo1.StockMst는 일반 시세조회 TR이므로 K2G01P를 사용한다.
KOSPI200_INDEX_CODE = "K2G01P"
# [260704 감사 P2] VKOSPI(코스피200변동성지수) 코드 — 사용자가 Cybos Plus 클라이언트
# 종목코드검색("코스피 200 변동성지수")으로 직접 확인 (2026-07-05).
# 주의: A0567은 이 지수의 "선물"(예: 2607 만기)이라 롤오버가 있음 — 만기 없는
# 현물/지수값이 필요해 O2901P(현물지수)를 사용한다.
VKOSPI_INDEX_CODE = "O2901P"

# CpTd6722 GetHeaderValue 인덱스 (cybosplus.github.io/cptrade_new_rtf_1_/cptd6722_.htm 검증)
MARGIN_QTY_HEADER_SELL_NEW = 19   # 매도(SHORT) 신규주문가능수량
MARGIN_QTY_HEADER_BUY_NEW = 29    # 매수(LONG) 신규주문가능수량

BALANCE_SIDE_MAP = {
    "1": "매도",
    "2": "매수",
}

ORDER_SIDE_MAP = {
    "SELL": "1",
    "BUY": "2",
}

ORDER_STATUS_MAP = {
    "1": "접수",
    "2": "정정확인",
    "3": "취소확인",
    "4": "체결",
    "5": "거부",
}

ORDER_HOGA_MARKET = "2"
ORDER_HOGA_LIMIT = "1"
ORDER_CONDITION_DEFAULT = "0"
CYBOS_FUTURES_CANCEL_PROGID = "CpTrade.CpTd6833"  # 선물/옵션 취소주문
# CpTd6831 신규주문 응답 GetHeaderValue(8) = 주문번호 (정정/취소 시 원주문번호로 사용)
# 근거: docs/CyBos ref/CYBOS_FUTURES_ORDER_TR_MAP.md §4 (공식 TR 테스트 예제 실측 캡처 기반, 2026-07-05 검증)
ORDER_NEW_HEADER_ORDER_NO = 8

# CpTd6197 header mapping is validated against raw Cybos logs in SYSTEM.log.
# HTS is a visual cross-check only and does not override this mapping.
# Current validated mapping from the 2026-05-11 session:
# - 1: deposit cash
# - 2: next-day deposit cash
# - 5: previous-day pnl
# - 6: today's realized pnl
# - 9: liquidation evaluation amount
# In the current mock environment, headers 2 and 9 are identical and header 5
# is returned as zero; both are treated as broker facts, not parser failures.
DAILY_PNL_HEADER_DEPOSIT_CASH = 1
DAILY_PNL_HEADER_NEXT_DAY_DEPOSIT_CASH = 2
DAILY_PNL_HEADER_PREV_DAY_PNL = 5
DAILY_PNL_HEADER_TODAY_PNL = 6
DAILY_PNL_HEADER_LIQUIDATION_EVAL = 9


def _system_info(message: str) -> None:
    system_logger.info(message)
    try:
        log_manager.system(message, "INFO")
    except Exception:
        pass


def _system_warning(message: str) -> None:
    system_logger.warning(message)
    try:
        log_manager.system(message, "WARNING")
    except Exception:
        pass


def _system_info_throttled(message: str, key: str, min_interval_sec: float = 600.0) -> None:
    now = time.time()
    last = _THROTTLED_INFO_TS.get(key, 0.0)
    if (now - last) < float(min_interval_sec):
        return
    _THROTTLED_INFO_TS[key] = now
    _system_info(message)


def _require_cybos_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Cybos Plus is only available on Windows. " + CYBOS_RUNTIME_HINT)
    if pythoncom is None or Dispatch is None or WithEvents is None:
        raise RuntimeError("pywin32 is not available. " + CYBOS_RUNTIME_HINT)
    if platform.architecture()[0] != "32bit":
        raise RuntimeError("Cybos Plus COM objects require 32-bit Python. " + CYBOS_RUNTIME_HINT)


# BlockRequest() 타임아웃 (초). COM 데드락 시 청산 불가를 방지.
BLOCK_REQUEST_TIMEOUT_SEC = 30


def _run_block_request(progid, input_pairs, data_reader=None,
                       timeout_sec=BLOCK_REQUEST_TIMEOUT_SEC):
    """COM BlockRequest를 백그라운드 스레드에서 타임아웃과 함께 실행한다.

    COM STA 규칙: Dispatch + SetInputValue + BlockRequest + 데이터 읽기를 모두
    같은 백그라운드 스레드에서 수행한다. 메인 스레드는 PumpWaitingMessages를
    10ms 간격으로 호출하며 완료를 기다린다 — Cybos BlockRequest가 호출 스레드의
    Windows 메시지 큐로 응답을 보내므로 메시지 펌프가 없으면 데드락이 발생한다.

    Args:
        progid: COM ProgID 문자열
        input_pairs: [(idx, val), ...] — SetInputValue 호출 목록
        data_reader: fn(obj) -> Any — COM obj에서 데이터를 읽는 콜백
                     (스레드 내에서 실행되므로 STA-safe)
        timeout_sec: 타임아웃 초

    Returns:
        (ret, status, msg, data)

    Raises:
        TimeoutError: timeout_sec 초 안에 완료되지 않은 경우
        RuntimeError / COM 예외: 내부 오류
    """
    result = {"ret": None, "status": None, "msg": None, "data": None, "exc": None}
    done = threading.Event()

    def _worker():
        try:
            pythoncom.CoInitialize()
        except Exception as e:  # CoInitialize 실패 시에도 계속 시도
            logger.debug("[BlockReq] CoInitialize warn: %s", e)
        try:
            obj = Dispatch(progid)
            for idx, val in input_pairs:
                obj.SetInputValue(idx, val)
            result["ret"] = obj.BlockRequest()
            result["status"] = _safe_int(obj.GetDibStatus())
            result["msg"] = _safe_str(obj.GetDibMsg1())
            if data_reader is not None:
                result["data"] = data_reader(obj)
        except Exception as exc:
            result["exc"] = exc
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
            done.set()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

    # Cybos Plus의 BlockRequest는 호출 스레드의 Windows 메시지 큐로 응답을 전달한다.
    # done.wait()로 메인 스레드를 블록하면 메시지 펌프가 멈춰 백그라운드 스레드의
    # BlockRequest가 영구 데드락에 빠진다. 10ms 간격으로 PumpWaitingMessages를
    # 호출해 COM 메시지를 처리하면서 완료를 기다린다.
    #
    # [주의] QCoreApplication.processEvents() 를 이 루프에서 호출하면
    # QTimer 이벤트(투자자 데이터 폴링 등)가 발동 → 또 다른 _run_block_request()
    # 호출 → 그 안에서 processEvents() → 재귀 깊이 폭발 + Qt 이벤트 루프 상태 오염.
    # 실증: TickUI 5분 침묵 → 폭발, 차트 응답 없음, 파이프라인 멈춤.
    # processEvents() 는 절대 이 루프에서 호출하지 않는다.
    deadline = time.time() + timeout_sec
    while True:
        if done.wait(timeout=0.01):
            break
        if time.time() >= deadline:
            logger.critical(
                "[BlockReq] TIMEOUT %ss progid=%s — 비상 청산이 필요할 수 있음",
                timeout_sec, progid,
            )
            raise TimeoutError(
                "Cybos BlockRequest timeout ({0}s) progid={1}".format(timeout_sec, progid)
            )
        if pythoncom is not None:
            try:
                pythoncom.PumpWaitingMessages()
            except Exception:
                pass

    if result["exc"] is not None:
        raise result["exc"]

    return result["ret"], result["status"], result["msg"], result["data"]


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).replace(",", "").strip()
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        text = str(value).replace(",", "").strip()
        if not text:
            return default
        return float(text)
    except Exception:
        return default


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _fix_mojibake_kr(value: str) -> str:
    """CP949 한글 바이트가 Latin-1로 오디코딩된 mojibake 복구.

    [302차] `CpSysDib.MarketEye` 등 일부 COM TR이 이 환경에서 한글 종목명을
    Latin-1로 잘못 디코딩해 반환하는 현상 확인(예: "코스피200 변동성" →
    "ÄÚ½ºÇÇ200 º¯µ¿¼º" — VKOSPI 조회가 매분 100% 실패하던 원인).
    정상적으로 디코딩된 한글 문자열은 U+AC00~U+D7A3 범위라 Latin-1(0~255)로
    encode 자체가 실패하므로, 이 경우 원본을 그대로 반환 — 실제로 깨진
    문자열만 복구되는 안전한 왕복 변환.
    """
    if not value:
        return value
    try:
        return value.encode("latin1").decode("cp949")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def _bool_nonblank(values: List[Any]) -> bool:
    return any(_safe_str(v) for v in values)


def _normalize_code(value: str) -> str:
    code = _safe_str(value)
    if code and not code.startswith("A"):
        code = "A" + code
    return code


class _CybosSubscriptionEvent:
    def set_context(self, owner, event_name: str, progid: str) -> None:
        self._owner = owner
        self._event_name = event_name
        self._progid = progid

    def OnReceived(self):  # pragma: no cover - COM event callback
        owner = getattr(self, "_owner", None)
        if owner is None:
            return
        # [308차] fill(체결통보)만 INFO로 승격 — tick/hoga 구독은 초당 다회 발생해
        # DEBUG로 유지. fill은 드물고(하루 수백건 이하) "원시 수신 횟수"를 남겨야
        # main.py의 ChejanFlow(처리 횟수)·ChejanDedup(폐기 횟수)와 3분할 대조가
        # 가능해진다 — 콜백 유실이 (a) 애초에 안 옴 (b) 왔는데 dedup에 폐기됨
        # (c) 왔고 처리도 됐는데 그 이후 로직에서 유실, 셋 중 어디인지 구분하는
        # 유일한 방법이 이 원시 카운터다.
        _is_fill = getattr(self, "_event_name", "") == "fill"
        _log = system_logger.info if _is_fill else system_logger.debug
        try:
            _log(
                "[CybosEvent] recv begin progid=%s event=%s owner=%s",
                getattr(self, "_progid", ""),
                getattr(self, "_event_name", ""),
                type(owner).__name__,
            )
        except Exception:
            pass
        owner._handle_subscription_event(self._event_name, self)
        try:
            _log(
                "[CybosEvent] recv end progid=%s event=%s owner=%s",
                getattr(self, "_progid", ""),
                getattr(self, "_event_name", ""),
                type(owner).__name__,
            )
        except Exception:
            pass


class _CybosConnectionEvent:
    def set_context(self, owner) -> None:
        self._owner = owner

    def OnDisConnect(self):  # pragma: no cover - COM event callback
        owner = getattr(self, "_owner", None)
        if owner is None:
            return
        owner._handle_disconnect()


class CybosSubscription:
    def __init__(self, com_object, sink):
        self._com_object = com_object
        self._sink = sink
        self._active = False

    @property
    def com_object(self):
        return self._com_object

    def subscribe(self, latest: bool = False) -> None:
        method_name = "SubscribeLatest" if latest and hasattr(self._com_object, "SubscribeLatest") else "Subscribe"
        system_logger.info("[CybosSub] subscribe begin method=%s", method_name)
        if latest and hasattr(self._com_object, "SubscribeLatest"):
            self._com_object.SubscribeLatest()
        else:
            self._com_object.Subscribe()
        self._active = True
        system_logger.info("[CybosSub] subscribe end method=%s", method_name)

    def unsubscribe(self) -> None:
        if not self._active:
            return
        try:
            self._com_object.Unsubscribe()
        except Exception:
            logger.debug("[Cybos] unsubscribe failed", exc_info=True)
        self._active = False


class CybosAPI:
    def __init__(self):
        _require_cybos_runtime()
        pythoncom.CoInitialize()

        self._cp_cybos = None
        self._cp_trade_util = None
        self._cp_future_code = None
        self._cp_cybos_event = None
        self._fill_subscription = None
        self._message_pump_timer = None

        self._fill_callbacks = []
        self._msg_callbacks = []
        self._investor_mapping_warned = set()
        self._last_order_error: Optional[Dict[str, Any]] = None
        # [308차 후속] fill 콜백 경량화 — OnReceived(COM 콜백) 안에서는 payload
        # 추출(공유 버퍼가 다음 이벤트로 덮어써지기 전에 반드시 동기로 읽어야 함)
        # 까지만 하고 큐에 적재, 실제 처리(_emit_fill → DB 기록·잔고 TR 등 무거운
        # 동기 작업)는 QTimer.singleShot(0)으로 COM 콜백 스택 밖(다음 이벤트루프
        # tick)에서 실행한다. 절대원칙 §4(콜백 내부는 상태저장만, dynamicCall
        # 금지)와 같은 취지를 Cybos 체결 콜백 경로에도 적용.
        self._fill_queue: "deque[Dict[str, Any]]" = deque()
        self._fill_drain_scheduled = False

    @property
    def is_connected(self) -> bool:
        if self._cp_cybos is None:
            return False
        try:
            return bool(self._cp_cybos.IsConnect)
        except Exception:
            return False

    def connect(self) -> bool:
        self._cp_cybos = Dispatch("CpUtil.CpCybos")
        self._cp_trade_util = Dispatch("CpTrade.CpTdUtil")
        self._cp_future_code = Dispatch("CpUtil.CpFutureCode")
        # CpUtil.CpKFutureCode는 KOSDAQ 150 선물 코드를 반환하므로
        # KOSPI200 미니선물 식별에 사용하지 않는다. (2026-05-13 실증)

        self._cp_cybos_event = WithEvents(self._cp_cybos, _CybosConnectionEvent)
        self._cp_cybos_event.set_context(self)

        if not self.is_connected:
            raise RuntimeError("U-CYBOS/CYBOS Plus is not connected. " + CYBOS_RUNTIME_HINT)

        ret = self._cp_trade_util.TradeInit(0)
        if ret not in (0, None):
            raise RuntimeError(
                "CpTdUtil.TradeInit failed with ret={0}. {1}".format(ret, CYBOS_RUNTIME_HINT)
            )

        self._ensure_message_pump()
        self._subscribe_fill_events()
        logger.info("[Cybos] connect ok server_type=%s accounts=%s", self.get_login_info("GetServerGubun"), self.get_account_list())
        return True

    def get_login_info(self, tag: str) -> str:
        tag = _safe_str(tag).upper()
        if tag == "ACCNO":
            return ";".join(self.get_account_list())
        if tag == "ACCOUNT_CNT":
            return str(len(self.get_account_list()))
        if tag == "GETSERVERGUBUN":
            # Cybos ServerType: 1=simulation, 2=real (same "1"=mock contract as Kiwoom)
            if self._cp_cybos is None:
                return ""
            try:
                server_type = int(self._cp_cybos.ServerType)
                return "1" if server_type == 1 else "0"
            except Exception:
                return "0" if self.is_connected else ""
        return ""

    def get_account_list(self) -> List[str]:
        if self._cp_trade_util is None:
            return []
        try:
            raw = self._cp_trade_util.AccountNumber
        except Exception:
            return []
        return [_safe_str(item) for item in list(raw or []) if _safe_str(item)]

    def get_nearest_futures_code(self) -> str:
        if self._cp_future_code is None:
            return ""

        count = _safe_int(self._cp_future_code.GetCount())
        for idx in range(count):
            code = _safe_str(self._cp_future_code.GetData(0, idx))
            name = _safe_str(self._cp_future_code.GetData(1, idx))
            if code.startswith("A") and "F" in name:
                return code
        return _safe_str(self._cp_future_code.GetData(0, 0)) if count > 0 else ""

    def get_nearest_mini_futures_code(self) -> str:
        """FutureMst BlockRequest 프로브로 KOSPI200 미니선물 근월물 코드(A05xxx) 반환.

        CpFutureCode — KOSPI200 일반선물(A01xxx)만 포함, A05xxx 없음.
        CpKFutureCode — 코스닥150 선물(A06xxx, ~1900pt)만 포함, A05xxx 없음.
        (2026-05-13 실증 확인 — 두 COM 객체 모두 미니선물 열거 불가)

        코드 규칙: A05 + 연도끝자리 + 월(hex uppercase)
        예) 2026-05 = A0565, 2026-06 = A0566, 2026-12 = A056C
        근월물 = 오늘 기준 가장 가까운 유효 만기(DibStatus=0, price>0).
        만기된 코드는 price=0 이므로 자동으로 skip된다.
        """
        import datetime
        if Dispatch is None:
            return ""
        today = datetime.date.today()
        candidates = []
        for delta in range(7):
            month = today.month + delta
            year = today.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            code = "A05{0}{1}".format(str(year)[-1], format(month, "X"))
            candidates.append(code)

        def _read_price(obj):
            return _safe_float(obj.GetHeaderValue(71))

        for code in candidates:
            try:
                ret, status, msg, price = _run_block_request(
                    progid="Dscbo1.FutureMst",
                    input_pairs=[(0, code)],
                    data_reader=_read_price,
                )
                if ret in (0, None) and status == 0 and price and price > 0:
                    logger.info("[MiniProbe] 근월물 확정 code=%s price=%.2f", code, price)
                    return code
                logger.debug("[MiniProbe] skip code=%s ret=%s status=%s price=%s", code, ret, status, price)
            except (TimeoutError, Exception) as exc:
                logger.debug("[MiniProbe] skip code=%s exc=%s", code, exc)
        return ""

    def get_nearest_normal_futures_code(self) -> str:
        """FutureMst BlockRequest 프로브로 KOSPI200 일반선물(A01xxx) 근월물 코드 반환.

        CpFutureCode 결과를 우선 후보로 하되, FutureMst price>0 으로 실거래 여부를 검증한다.
        코드 규칙: A01 + 연도끝자리 + 월(hex uppercase) — 분기만기(3·6·9·12월).
        만기된 코드는 price=0 이므로 자동으로 skip된다.
        """
        import datetime
        if Dispatch is None:
            return ""

        primary = self.get_nearest_futures_code()  # CpFutureCode 우선 후보 (A01xxx)

        today = datetime.date.today()
        quarterly = (3, 6, 9, 12)
        candidates = []
        if primary:
            candidates.append(primary)

        # 분기 후보 — 향후 18개월 스캔 (최대 2개 분기월 이상 커버)
        year, month = today.year, today.month
        for _ in range(18):
            if month in quarterly:
                code = "A01{0}{1}".format(str(year)[-1], format(month, "X"))
                if code not in candidates:
                    candidates.append(code)
            month += 1
            if month > 12:
                month = 1
                year += 1

        def _read_price(obj):
            return _safe_float(obj.GetHeaderValue(71))

        for code in candidates:
            try:
                ret, status, msg, price = _run_block_request(
                    progid="Dscbo1.FutureMst",
                    input_pairs=[(0, code)],
                    data_reader=_read_price,
                )
                if ret in (0, None) and status == 0 and price and price > 0:
                    logger.info("[NormalProbe] 근월물 확정 code=%s price=%.2f", code, price)
                    return code
                logger.debug("[NormalProbe] skip code=%s ret=%s status=%s price=%s", code, ret, status, price)
            except (TimeoutError, Exception) as exc:
                logger.debug("[NormalProbe] skip code=%s exc=%s", code, exc)

        if primary:
            logger.warning("[NormalProbe] FutureMst 프로브 전부 실패 — CpFutureCode 결과 사용: %s", primary)
            return primary
        return ""

    def register_fill_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        if callback not in self._fill_callbacks:
            self._fill_callbacks.append(callback)

    def register_msg_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        if callback not in self._msg_callbacks:
            self._msg_callbacks.append(callback)

    def request_futures_balance(self, account_no: str) -> Optional[Dict[str, Any]]:
        import time as _t, traceback as _tb, logging as _log
        _rfb_t0 = _t.monotonic()
        _rfb_caller = "".join(_tb.format_stack()[-4:-1]).replace("\n", " | ").replace("  ", " ")
        _log.getLogger("SYSTEM").warning(
            "[LiveDBG] request_futures_balance 호출 account=%s | caller=%s",
            account_no, _rfb_caller[-200:],
        )
        if not account_no:
            return None
        self._ensure_trade_init()
        _log.getLogger("SYSTEM").warning(
            "[LiveDBG] request_futures_balance TradeInit 완료 %.0fms",
            (_t.monotonic() - _rfb_t0) * 1000,
        )

        def _read_rows(obj):
            count = _safe_int(obj.GetHeaderValue(2))
            rows = []
            for idx in range(count):
                code = _safe_str(obj.GetDataValue(0, idx))
                name = _safe_str(obj.GetDataValue(1, idx))
                side_code = _safe_str(obj.GetDataValue(2, idx))
                qty = _safe_int(obj.GetDataValue(3, idx))
                avg_price = _safe_float(obj.GetDataValue(5, idx))
                closable_qty = _safe_int(obj.GetDataValue(9, idx))
                traded_qty = _safe_int(obj.GetDataValue(10, idx))
                rows.append({
                    "종목코드": _normalize_code(code),
                    "종목명": name,
                    "구분": BALANCE_SIDE_MAP.get(side_code, side_code),
                    "매매구분": BALANCE_SIDE_MAP.get(side_code, side_code),
                    "잔고수량": str(qty),
                    "청산가능": str(closable_qty),
                    "평균가": str(avg_price),
                    "매입단가": str(avg_price),
                    "현재가": "",
                    "평가손익(원)": "",
                    "수익률(%)": "",
                    "체결수량": str(traded_qty),
                    "side_code": side_code,
                })
            return rows

        try:
            # 잔고 조회는 대시보드 표시용 — 트레이딩 로직 무관.
            # 서버 무응답 시 메인스레드 블로킹을 최소화하기 위해 8초 단축 타임아웃 사용.
            ret, status, msg, rows = _run_block_request(
                progid=CYBOS_FUTURES_BALANCE_PROGID,
                input_pairs=[
                    (0, account_no),
                    (1, CYBOS_GOODS_CODE_FUTURES),
                    (2, "1"),
                    (3, ""),
                    (4, 20),
                ],
                data_reader=_read_rows,
                timeout_sec=8,
            )
        except TimeoutError as exc:
            logger.error("[CybosBalance] %s account=%s", exc, account_no)
            return None

        if ret not in (0, None) or status != 0:
            logger.warning("[CybosBalance] request failed ret=%s status=%s msg=%s", ret, status, msg)
            self._emit_msg({
                "source": "CpTd0723",
                "status": "ERROR",
                "status_code": status or ret,
                "message": msg,
                "account_no": account_no,
            })
            return None

        rows = rows or []
        summary = self._request_futures_daily_pnl_summary(account_no)
        nonempty_rows = [row for row in rows if _bool_nonblank(list(row.values()))]
        result = {
            "rows": rows,
            "nonempty_rows": nonempty_rows,
            "summary": summary,
            "summary_probe": {
                "dib_status": str(status),
                "dib_msg": msg,
                "count": str(len(rows)),
            },
            "record_name": "CpTd0723",
            "prev_next": "",
            "all_blank_rows": bool(rows) and not bool(nonempty_rows),
        }
        logger.info("[CybosBalance] account=%s rows=%d nonempty=%d", account_no, len(rows), len(nonempty_rows))
        import time as _t2, logging as _log2
        _log2.getLogger("SYSTEM").warning(
            "[LiveDBG] request_futures_balance 완료 총 %.0fms account=%s",
            (_t2.monotonic() - _rfb_t0) * 1000, account_no,
        )
        return result

    def _request_futures_daily_pnl_summary(self, account_no: str) -> Dict[str, str]:
        today_yyMMdd = time.strftime("%y%m%d")

        def _read_pnl(obj):
            return {idx: _safe_str(obj.GetHeaderValue(idx)) for idx in range(0, 21)}

        try:
            ret, status, msg, raw_headers = _run_block_request(
                progid=CYBOS_FUTURES_DAILY_PNL_PROGID,
                input_pairs=[
                    (0, account_no),
                    (1, today_yyMMdd),
                    (2, CYBOS_GOODS_CODE_FUTURES),
                    (3, 10),
                ],
                data_reader=_read_pnl,
            )
        except TimeoutError as exc:
            system_logger.error("[CybosDailyPnl] %s account=%s", exc, account_no)
            return {}
        except Exception:
            system_logger.exception("[CybosDailyPnl] request failed with exception account=%s", account_no)
            try:
                log_manager.system(f"[CybosDailyPnl] exception account={account_no}", "WARNING")
            except Exception:
                pass
            return {}

        if ret not in (0, None) or status != 0:
            _system_warning(
                f"[CybosDailyPnl] request failed account={account_no} "
                f"ret={ret} status={status} msg={msg}"
            )
            return {}

        raw_headers = raw_headers or {}
        deposit_cash = _safe_float(raw_headers.get(DAILY_PNL_HEADER_DEPOSIT_CASH))
        next_day_deposit_cash = _safe_float(raw_headers.get(DAILY_PNL_HEADER_NEXT_DAY_DEPOSIT_CASH))
        prev_day_pnl = _safe_float(raw_headers.get(DAILY_PNL_HEADER_PREV_DAY_PNL))
        today_pnl = _safe_float(raw_headers.get(DAILY_PNL_HEADER_TODAY_PNL))
        liquidation_eval_raw = _safe_float(raw_headers.get(DAILY_PNL_HEADER_LIQUIDATION_EVAL))
        liquidation_substituted = liquidation_eval_raw <= 0.0 and next_day_deposit_cash > 0.0
        liquidation_eval = next_day_deposit_cash if liquidation_substituted else liquidation_eval_raw
        profit_rate = ((next_day_deposit_cash - deposit_cash) / deposit_cash * 100.0) if deposit_cash else 0.0

        # profit_rate는 운영 중 반복 관측되는 진단값이라 기본 INFO(레이트리밋),
        # 과도한 이상치만 WARNING으로 올린다.
        profit_rate_msg = (
            f"[CybosDailyPnl] profit_rate 이상값 {profit_rate:.2f}% — "
            f"deposit={deposit_cash:.0f} next_day={next_day_deposit_cash:.0f} "
            f"header_idx_check={{1:{raw_headers.get(1)}, 2:{raw_headers.get(2)}}}"
        )
        if abs(profit_rate) > 200.0:
            _system_warning(profit_rate_msg)
        elif abs(profit_rate) > 50.0:
            _system_info_throttled(
                profit_rate_msg,
                key="cybos_daily_pnl_profit_rate_diag",
                min_interval_sec=600.0,
            )

        if liquidation_substituted:
            _system_warning(
                f"[CybosDailyPnl] 청산평가액=0 → 익일예탁금({next_day_deposit_cash:.0f})으로 대체 "
                f"(장 시작 전 타이밍 또는 미결제약정 없음) account={account_no}"
            )

        header_validation = {
            "deposit_cash_idx": DAILY_PNL_HEADER_DEPOSIT_CASH,
            "next_day_deposit_cash_idx": DAILY_PNL_HEADER_NEXT_DAY_DEPOSIT_CASH,
            "prev_day_pnl_idx": DAILY_PNL_HEADER_PREV_DAY_PNL,
            "today_pnl_idx": DAILY_PNL_HEADER_TODAY_PNL,
            "liquidation_eval_idx": DAILY_PNL_HEADER_LIQUIDATION_EVAL,
            "liquidation_substituted": liquidation_substituted,
            "prev_day_pnl_zero": prev_day_pnl == 0.0,
        }

        # 필드 의미 (대시보드 라벨 기준):
        #   총매매        = 예탁금 (KRW)
        #   총평가손익    = 청산평가손익 (KRW, 포지션 없으면 익일예탁금 대체)
        #   총평가수익률  = 익일가예탁현금 (KRW) — _ts_extract_sizer_balance 잔고 소스
        #   추정자산      = 전일손익 (KRW)
        summary = {
            "총매매": f"{deposit_cash:.0f}",
            "총평가손익": f"{liquidation_eval:.0f}",
            "실현손익": f"{today_pnl:.0f}",
            "총평가": f"{profit_rate:.2f}",
            "총평가수익률": f"{next_day_deposit_cash:.0f}",
            "추정자산": f"{prev_day_pnl:.0f}",
        }
        # 포지션 없을 때 총평가손익=익일예탁금(대체값)이 실제 잔고처럼 보여 감사 오판 방지.
        # 숫자 파싱(_num)은 "총평가손익" 키만 참조하므로 별도 키로 안전하게 추가.
        if liquidation_substituted:
            summary["총평가손익_비고"] = "익일예탁금대체(포지션없음)"
        _system_info(
            f"[CybosDailyPnl] account={account_no} "
            f"validate={header_validation} summary={summary}"
        )
        system_logger.info(
            "[CybosDailyPnlHeaders] account=%s headers=%s",
            account_no,
            raw_headers,
        )
        return summary

    def send_market_order(
        self,
        *,
        account_no: str,
        code: str,
        side: str,
        qty: int,
        rqname: str,
        screen_no: str,
    ) -> int:
        del rqname, screen_no

        if not account_no or not code or qty <= 0:
            return -1

        self._ensure_trade_init()
        side_code = ORDER_SIDE_MAP.get(_safe_str(side).upper())
        if not side_code:
            return -1

        _code = _normalize_code(code)
        _qty = int(qty)

        try:
            ret, status, msg, _ = _run_block_request(
                progid=CYBOS_FUTURES_ORDER_PROGID,
                input_pairs=[
                    (1, account_no),
                    (2, _code),
                    (3, _qty),
                    (4, 0),
                    (5, side_code),
                    (6, ORDER_HOGA_MARKET),
                    (7, ORDER_CONDITION_DEFAULT),
                    (8, CYBOS_GOODS_CODE_FUTURES),
                ],
            )
        except TimeoutError as exc:
            self._last_order_error = {
                "ret": -99, "status": None, "msg": str(exc),
                "account_no": account_no, "code": _code, "side": side_code, "qty": _qty,
            }
            system_logger.critical(
                "[CybosOrder] BlockRequest 타임아웃: %s account=%s code=%s side=%s qty=%s",
                exc, account_no, _code, side_code, _qty,
            )
            self._emit_msg({
                "source": "CpTd6831",
                "status": "TIMEOUT",
                "status_code": -99,
                "message": str(exc),
                "account_no": account_no,
                "code": _code,
                "side": "매수" if side_code == "2" else "매도",
                "order_gubun": "매수" if side_code == "2" else "매도",
                "trade_gubun": side_code,
                "qty": _qty,
            })
            # -99: 타임아웃 전용 오류 코드 — 호출자가 CB 트리거 여부 판단
            return -99

        payload = {
            "source": "CpTd6831",
            "status": "OK" if ret in (0, None) and status == 0 else "ERROR",
            "status_code": status if status else _safe_int(ret, 0),
            "message": msg,
            "account_no": account_no,
            "code": _code,
            "side": "매수" if side_code == "2" else "매도",
            "order_gubun": "매수" if side_code == "2" else "매도",
            "trade_gubun": side_code,
            "qty": _qty,
        }
        self._emit_msg(payload)
        _order_failed = ret not in (0, None) or status != 0
        if _order_failed:
            self._last_order_error = {
                "ret": ret, "status": status, "msg": msg,
                "account_no": account_no, "code": _code, "side": side_code, "qty": _qty,
            }
            # [재발방지] 이전에는 module logger(__name__)로만 기록돼 어떤 로그 파일에도
            # 남지 않았음 — 2026-07-03 10:28:59 LONG 3계약 주문 거부(ret=-1) 시
            # 실제 거부 사유(GetDibMsg1)가 통째로 유실된 사고 재발 방지.
            system_logger.error(
                "[CybosOrder] 주문 실패 ret=%s status=%s msg=%s account=%s code=%s side=%s qty=%s",
                ret, status, msg, account_no, _code,
                "매수" if side_code == "2" else "매도", _qty,
            )
        else:
            self._last_order_error = None
            logger.info("[CybosOrder] ret=%s status=%s msg=%s payload=%s", ret, status, msg, payload)
        if ret not in (0, None):
            return _safe_int(ret, -1)
        if status != 0:
            return status or -1
        return 0

    def send_limit_order(
        self,
        *,
        account_no: str,
        code: str,
        side: str,
        qty: int,
        price: float,
        rqname: str,
        screen_no: str,
    ) -> Dict[str, Any]:
        """지정가 신규주문 (CpTd6831, idx6='1'). send_market_order와 동일 TR — idx4/6만 다름.

        [260704 감사 P1] 지정가 우선 집행용 — 반환값에 order_no를 포함해 미체결 시
        cancel_order()로 취소할 수 있게 한다.

        Returns: {"ret": int, "order_no": str} — ret=0 성공, 그 외 실패(get_last_order_error 참조)
        """
        del rqname, screen_no

        if not account_no or not code or qty <= 0 or price <= 0:
            return {"ret": -1, "order_no": ""}

        self._ensure_trade_init()
        side_code = ORDER_SIDE_MAP.get(_safe_str(side).upper())
        if not side_code:
            return {"ret": -1, "order_no": ""}

        _code = _normalize_code(code)
        _qty = int(qty)

        def _read_order_no(obj):
            return _safe_str(obj.GetHeaderValue(ORDER_NEW_HEADER_ORDER_NO))

        try:
            ret, status, msg, order_no = _run_block_request(
                progid=CYBOS_FUTURES_ORDER_PROGID,
                input_pairs=[
                    (1, account_no),
                    (2, _code),
                    (3, _qty),
                    (4, float(price)),
                    (5, side_code),
                    (6, ORDER_HOGA_LIMIT),
                    (7, ORDER_CONDITION_DEFAULT),
                    (8, CYBOS_GOODS_CODE_FUTURES),
                ],
                data_reader=_read_order_no,
            )
        except TimeoutError as exc:
            self._last_order_error = {
                "ret": -99, "status": None, "msg": str(exc),
                "account_no": account_no, "code": _code, "side": side_code, "qty": _qty,
            }
            system_logger.critical(
                "[CybosLimitOrder] BlockRequest 타임아웃: %s account=%s code=%s side=%s qty=%s price=%s",
                exc, account_no, _code, side_code, _qty, price,
            )
            self._emit_msg({
                "source": "CpTd6831",
                "status": "TIMEOUT",
                "status_code": -99,
                "message": str(exc),
                "account_no": account_no,
                "code": _code,
                "side": "매수" if side_code == "2" else "매도",
                "order_gubun": "매수" if side_code == "2" else "매도",
                "trade_gubun": side_code,
                "qty": _qty,
            })
            return {"ret": -99, "order_no": ""}

        payload = {
            "source": "CpTd6831",
            "status": "OK" if ret in (0, None) and status == 0 else "ERROR",
            "status_code": status if status else _safe_int(ret, 0),
            "message": msg,
            "account_no": account_no,
            "code": _code,
            "side": "매수" if side_code == "2" else "매도",
            "order_gubun": "매수" if side_code == "2" else "매도",
            "trade_gubun": side_code,
            "qty": _qty,
        }
        self._emit_msg(payload)
        _order_failed = ret not in (0, None) or status != 0
        if _order_failed:
            self._last_order_error = {
                "ret": ret, "status": status, "msg": msg,
                "account_no": account_no, "code": _code, "side": side_code, "qty": _qty,
            }
            system_logger.error(
                "[CybosLimitOrder] 지정가 주문 실패 ret=%s status=%s msg=%s account=%s code=%s side=%s qty=%s price=%s",
                ret, status, msg, account_no, _code,
                "매수" if side_code == "2" else "매도", _qty, price,
            )
            _ret_code = _safe_int(ret, -1) if ret not in (0, None) else (status or -1)
            return {"ret": _ret_code, "order_no": ""}

        self._last_order_error = None
        logger.info("[CybosLimitOrder] ret=%s status=%s msg=%s order_no=%s payload=%s",
                    ret, status, msg, order_no, payload)
        return {"ret": 0, "order_no": order_no or ""}

    def cancel_order(
        self,
        *,
        account_no: str,
        order_no: str,
        code: str,
        qty: int,
    ) -> int:
        """선물/옵션 취소주문 (CpTd6833). 반환: 0=성공, 그 외=실패.

        [260704 감사 P1] 지정가 우선 집행 타임아웃 시 미체결 주문 취소용.
        """
        if not account_no or not order_no or not code or qty <= 0:
            return -1

        self._ensure_trade_init()
        _code = _normalize_code(code)

        try:
            ret, status, msg, _ = _run_block_request(
                progid=CYBOS_FUTURES_CANCEL_PROGID,
                input_pairs=[
                    (2, order_no),
                    (3, account_no),
                    (4, _code),
                    (5, int(qty)),
                    (6, CYBOS_GOODS_CODE_FUTURES),
                ],
            )
        except TimeoutError as exc:
            system_logger.critical(
                "[CybosCancel] BlockRequest 타임아웃: %s order_no=%s account=%s code=%s qty=%s",
                exc, order_no, account_no, _code, qty,
            )
            return -99

        _failed = ret not in (0, None) or status != 0
        if _failed:
            system_logger.error(
                "[CybosCancel] 취소 실패 ret=%s status=%s msg=%s order_no=%s account=%s code=%s qty=%s",
                ret, status, msg, order_no, account_no, _code, qty,
            )
            return _safe_int(ret, -1) if ret not in (0, None) else (status or -1)

        system_logger.info(
            "[CybosCancel] 취소 성공 order_no=%s account=%s code=%s qty=%s",
            order_no, account_no, _code, qty,
        )
        return 0

    def get_last_order_error(self) -> Optional[Dict[str, Any]]:
        """가장 최근 실패한 주문의 상세 정보(ret/status/msg). 성공 시 None."""
        return self._last_order_error

    def request_order_available_qty(
        self, account_no: str, code: str, price: float,
    ) -> Optional[Dict[str, int]]:
        """CpTd6722: 선물 신규주문가능수량(증거금 반영) 조회.

        SendOrder가 매번 최종 판정하지만, 증거금 부족으로 인한 주문 거부를
        진입 수량 산출 단계에서 미리 걸러내기 위해 호출한다.
        """
        if not account_no or not code:
            return None
        self._ensure_trade_init()
        _code = _normalize_code(code)

        def _read_qty(obj):
            return {
                "sell_new_qty": _safe_int(obj.GetHeaderValue(MARGIN_QTY_HEADER_SELL_NEW)),
                "buy_new_qty": _safe_int(obj.GetHeaderValue(MARGIN_QTY_HEADER_BUY_NEW)),
            }

        try:
            ret, status, msg, data = _run_block_request(
                progid=CYBOS_FUTURES_ORDER_MARGIN_QTY_PROGID,
                input_pairs=[
                    (0, account_no),
                    (1, _code),
                    (2, float(price or 0.0)),
                    (3, ORDER_HOGA_MARKET),
                    (4, CYBOS_GOODS_CODE_FUTURES),
                    (5, "Y"),
                ],
                data_reader=_read_qty,
                timeout_sec=5,
            )
        except TimeoutError as exc:
            system_logger.warning(
                "[CybosMarginQty] BlockRequest 타임아웃: %s account=%s code=%s",
                exc, account_no, _code,
            )
            return None

        if ret not in (0, None) or status != 0:
            system_logger.warning(
                "[CybosMarginQty] 조회 실패 ret=%s status=%s msg=%s account=%s code=%s",
                ret, status, msg, account_no, _code,
            )
            return None
        return data

    def get_index_price(
        self, code: str = KOSPI200_INDEX_CODE, name_contains: str = "200",
    ) -> Optional[float]:
        """[260704 감사 P2, 294차 TR 교체] 지수 현재가 조회 (CpSysDib.MarketEye).

        기본값은 KOSPI200 현물지수(코드 "K2G01P"). VKOSPI(코드 "O2901P",
        name_contains="변동성")에도 재사용. 선물-현물 베이시스 계산용.

        294차 실증: dscbo1.StockMst는 K2G01P/O2901P는 물론 대신증권 자체
        지수코드 후보(U180)로도 "71103 조회결과가 없습니다"만 반환 — 개별
        종목(주식/ETF) 전용 TR로 확정, 코드가 아니라 TR 자체가 틀렸었음.
        CpSysDib.MarketEye(주식·지수·선물옵션 통합 조회)로 교체 후 동일 코드
        K2G01P/O2901P로 정상 조회 확인(종목명="코스피 200"/"코스피200 변동성",
        관리자 권한 세션 실측). MarketEye는 필드타입 배열 + 종목코드 배열을
        받아 GetDataValue(position, row)로 응답하는 인터페이스라 StockMst의
        GetHeaderValue 단일조회와 다름 — field 0=종목코드, 4=현재가, 17=종목명
        (요청한 필드 순서가 GetDataValue의 position 인자가 된다).

        종목명(idx1)에 name_contains가 없으면 잘못된 코드로 간주해 None 반환 —
        틀린 코드가 조용히 엉뚱한 가격을 흘려보내는 사고를 방지하는 자체 검증.
        """
        if not code:
            return None
        try:
            ret, status, msg, data = _run_block_request(
                progid="CpSysDib.MarketEye",
                input_pairs=[(0, [0, 4, 17]), (1, [code])],
                data_reader=lambda obj: {
                    "name": _fix_mojibake_kr(_safe_str(obj.GetDataValue(2, 0))),
                    "price": _safe_float(obj.GetDataValue(1, 0)),
                },
                timeout_sec=5,
            )
        except TimeoutError as exc:
            system_logger.warning("[CybosIndex] BlockRequest 타임아웃: %s code=%s", exc, code)
            return None
        except Exception as exc:
            # 주기적 폴링(베이시스/VKOSPI 피처 보조용)이라 여기서 예외를 삼켜 호출부(QTimer)를
            # 보호한다 — 주문류(send_market_order 등)와 달리 실패해도 매매에 영향 없음.
            system_logger.warning("[CybosIndex] 조회 예외: %s code=%s", exc, code)
            return None

        if ret not in (0, None) or status != 0:
            system_logger.warning(
                "[CybosIndex] 조회 실패 ret=%s status=%s msg=%s code=%s", ret, status, msg, code,
            )
            return None
        if not data or name_contains not in data.get("name", ""):
            system_logger.error(
                "[CybosIndex] 종목명 검증 실패 — code=%s name=%s (기대 포함어=%s, 값 폐기)",
                code, data.get("name") if data else None, name_contains,
            )
            return None
        return data["price"] if data["price"] > 0 else None

    def create_subscription(
        self,
        *,
        progid: str,
        input_values: Dict[int, Any],
        owner,
        event_name: str,
        latest: bool = False,
    ) -> CybosSubscription:
        system_logger.info(
            "[CybosSub] create begin progid=%s event=%s latest=%s inputs=%s",
            progid,
            event_name,
            latest,
            input_values,
        )
        obj = Dispatch(progid)
        system_logger.info("[CybosSub] dispatch ok progid=%s event=%s", progid, event_name)
        for key, value in sorted(input_values.items()):
            obj.SetInputValue(int(key), value)
        system_logger.info("[CybosSub] input ok progid=%s event=%s", progid, event_name)
        sink = WithEvents(obj, _CybosSubscriptionEvent)
        sink.set_context(owner, event_name, progid)
        system_logger.info("[CybosSub] with-events ok progid=%s event=%s", progid, event_name)
        subscription = CybosSubscription(obj, sink)
        subscription.subscribe(latest=latest)
        system_logger.info("[CybosSub] create end progid=%s event=%s", progid, event_name)
        return subscription

    def request_futures_snapshot(self, code: str) -> Dict[str, Any]:
        _code = _normalize_code(code)

        def _read_snapshot(obj):
            return {
                "code": _safe_str(obj.GetHeaderValue(0)),
                "price": _safe_float(obj.GetHeaderValue(71)),
                "open": _safe_float(obj.GetHeaderValue(72)),
                "high": _safe_float(obj.GetHeaderValue(73)),
                "low": _safe_float(obj.GetHeaderValue(74)),
                "cum_volume": _safe_int(obj.GetHeaderValue(75)),
                "open_interest": _safe_int(obj.GetHeaderValue(80)),
                "ask1": _safe_float(obj.GetHeaderValue(37)),
                "bid1": _safe_float(obj.GetHeaderValue(54)),
                "ask_qty1": _safe_int(obj.GetHeaderValue(42)),
                "bid_qty1": _safe_int(obj.GetHeaderValue(59)),
                "trade_time": _safe_int(obj.GetHeaderValue(82)),
                "process_time": _safe_int(obj.GetHeaderValue(83)),
                "market_state": _safe_int(obj.GetHeaderValue(115)),
            }

        try:
            ret, status, msg, data = _run_block_request(
                progid="Dscbo1.FutureMst",
                input_pairs=[(0, _code)],
                data_reader=_read_snapshot,
            )
        except TimeoutError as exc:
            logger.error("[CybosSnapshot] %s code=%s", exc, code)
            return {}

        if ret not in (0, None) or status != 0:
            logger.warning(
                "[CybosSnapshot] request failed ret=%s status=%s msg=%s code=%s",
                ret, status, msg, code,
            )
            return {}
        return data or {}

    def probe_investor_ticker(self, extra_codes: Optional[List[str]] = None) -> None:
        probe_log.info("[CybosInvestorProbe] not implemented; extra_codes=%s", extra_codes or [])

    # ──────────────────────────────────────────────────────────────
    # 투자자 수급 / 프로그램 매매 데이터 수집
    # QTimer 스레드에서만 호출 (COM 콜백 체인 외부).
    # 각 후보 ProgID를 순서대로 시도하여 응답하는 첫 번째를 사용한다.
    # ──────────────────────────────────────────────────────────────

    # 선물 투자자 구분 코드 → INVESTOR_KEYS 매핑 (Cybos Plus 공통 순서)
    _FUTURES_INVESTOR_TYPE_MAP: Dict[int, str] = {
        0: "individual",
        1: "foreign",
        2: "institution",
        3: "financial",
        4: "insurance",
        5: "trust",
        6: "bank",
        7: "etc_corp",
        8: "pension",
        9: "nation",
    }

    # CpSysDib.CpSvrNew7221 — InvestIndex (행=상품종류, 대신증권 자료실 seq=85 확인)
    # 0=거래소주식, 1=코스닥주식, 2=선물, 3=옵션콜, 4=옵션풋,
    # 5=주식콜, 6=주식풋, 7=스타지수선물, 8=주식선물 ...
    _7221_INVEST_INDEX: Dict[int, str] = {
        0: "거래소주식", 1: "코스닥주식", 2: "선물", 3: "옵션콜", 4: "옵션풋",
        5: "주식콜", 6: "주식풋", 7: "스타지수선물", 8: "주식선물",
    }
    # CpSysDib.CpSvrNew7221 — 열 인덱스 (개인/외인/기관)
    # 2=개인순매수, 5=외인순매수, 8=기관순매수 (대신증권 자료실 seq=85 확인)

    # fallback 후보용: 숫자 투자자코드 → INVESTOR_KEYS (기존 추측 코드, 미확인)
    _FUTURES_INVESTOR_NAME_MAP: Dict[str, str] = {
        "개인":     "individual",
        "외국인":   "foreign",
        "기관계":   "institution",
        "금융투자": "financial",
        "보험":     "insurance",
        "투신":     "trust",
        "은행":     "bank",
        "기타금융": "etc_corp",
        "연기금":   "pension",
        "국가지자체": "nation",
        "기타법인": "etc_corp",
    }

    # 투자자 TR probe 결과를 SYSTEM 로그에 1회만 덤프 (세션당 progid별)
    _probe_dump_done: set = set()

    def _probe_investor_tr(
        self,
        progid: str,
        inputs: List[tuple],
        allow_status_error: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        COM 오브젝트를 Dispatch 하여 BlockRequest 후 헤더/행 데이터를 반환한다.
        실패(연결 불가, status ≠ 0) 시 None 반환.
        """
        try:
            obj = Dispatch(progid)
            for idx, val in inputs:
                obj.SetInputValue(idx, val)
            ret = obj.BlockRequest()
            status = _safe_int(obj.GetDibStatus())
            msg = _safe_str(obj.GetDibMsg1())
            if ret not in (0, None) or (status != 0 and not allow_status_error):
                probe_log.warning(
                    "[CybosProbe] %s blocked ret=%s status=%s msg=%s",
                    progid, ret, status, msg,
                )
                return None
            headers: Dict[int, str] = {}
            # CpSvr8111(프로그램매매)은 idx55까지 사용(2026-07-05 검증) — 여유있게 64까지 읽음
            for i in range(64):
                try:
                    headers[i] = _safe_str(obj.GetHeaderValue(i))
                except Exception:
                    break
            rows: List[Dict[int, str]] = []
            for ri in range(30):
                row: Dict[int, str] = {}
                any_val = False
                for fi in range(15):
                    try:
                        v = _safe_str(obj.GetDataValue(fi, ri))
                        row[fi] = v
                        if v:
                            any_val = True
                    except Exception:
                        pass
                if not any_val and ri > 0:
                    break
                if row:
                    rows.append(row)
            nonempty_h = sum(1 for v in headers.values() if v)
            probe_log.info(
                "[CybosProbe] %s ok status=%s nonempty_headers=%d rows=%d",
                progid, status, nonempty_h, len(rows),
            )
            # 세션당 1회 raw 덤프 — TR 구조 파악용
            if progid not in CybosAPI._probe_dump_done:
                CybosAPI._probe_dump_done.add(progid)
                h_nonempty = {k: v for k, v in headers.items() if v}
                probe_log.info(
                    "[CybosProbe][RAW] %s headers=%s rows_sample=%s",
                    progid, h_nonempty, rows[:5],
                )
            return {
                "progid": progid,
                "ret": ret,
                "status": status,
                "msg": msg,
                "headers": headers,
                "rows": rows,
            }
        except Exception as exc:
            probe_log.warning("[CybosProbe] %s dispatch/request failed: %s", progid, exc)
            return None

    def request_investor_futures(self) -> Dict[str, Any]:
        """
        선물/콜/풋 투자자별 순매수를 반환한다.

        CpSysDib.CpSvrNew7221 (투자자별 매매종합서비스, 대신증권 자료실 seq=85):
          입력: SetInputValue(0, ord('1')) → 옵션금액/선물계약 단위
          행 인덱스(상품 종류):
            0=거래소주식, 1=코스닥주식, 2=선물, 3=옵션콜, 4=옵션풋,
            5=주식콜, 6=주식풋, 7=스타지수선물, 8=주식선물 ...
          열 인덱스(투자자 종류):
            0=개인매도, 1=개인매수, 2=개인순매수
            3=외인매도, 4=외인매수, 5=외인순매수
            6=기관매도, 7=기관매수, 8=기관순매수
        """
        code = self.get_nearest_futures_code()
        candidates = [
            # P0: 대신증권 공식 자료실 확인 TR — 투자자별 매매종합
            # ord('1')=49: 옵션금액/선물계약 단위
            ("CpSysDib.CpSvrNew7221", [(0, ord('1'))]),
            # fallback (미확인 후보, 탐색용 유지)
            ("Dscbo1.FutureTrader",    [(0, code)]),
            ("CpSysDib.FutureTrader",  [(0, code)]),
            ("Dscbo1.FutureTrade",     [(0, code)]),
            ("CpSysDib.FutureTrade",   [(0, code)]),
        ]
        for progid, inputs in candidates:
            probe = self._probe_investor_tr(progid, inputs)
            if probe is None:
                continue

            nets: Dict[str, int] = {}
            call_nets: Dict[str, int] = {}
            put_nets: Dict[str, int] = {}

            if progid == "CpSysDib.CpSvrNew7221":
                # 행=상품종류(ri), 열=투자자(fi)
                # ri 2=선물, ri 3=옵션콜, ri 4=옵션풋
                # fi 2=개인순매수, fi 5=외인순매수, fi 8=기관순매수
                rows = probe["rows"]
                if len(rows) > 2:
                    r = rows[2]  # 선물
                    nets["individual"] = _safe_int(r.get(2, 0))
                    nets["foreign"]    = _safe_int(r.get(5, 0))
                    nets["institution"] = _safe_int(r.get(8, 0))
                if len(rows) > 3:
                    r = rows[3]  # 옵션콜
                    call_nets["individual"] = _safe_int(r.get(2, 0))
                    call_nets["foreign"]    = _safe_int(r.get(5, 0))
                    call_nets["institution"] = _safe_int(r.get(8, 0))
                if len(rows) > 4:
                    r = rows[4]  # 옵션풋
                    put_nets["individual"] = _safe_int(r.get(2, 0))
                    put_nets["foreign"]    = _safe_int(r.get(5, 0))
                    put_nets["institution"] = _safe_int(r.get(8, 0))

                if not nets:
                    system_logger.warning(
                        "[CybosInvestorRaw] 7221 rows=%d — 선물 행(ri=2) 데이터 없음. "
                        "rows_sample=%s",
                        len(rows), rows[:5],
                    )
                supported = bool(nets)
            else:
                # 숫자 투자자코드 기반 파싱 (기존 fallback 로직)
                for ri, row in enumerate(probe["rows"]):
                    try:
                        type_raw  = row.get(0, "")
                        net_raw   = row.get(3, "")
                        type_code = _safe_int(type_raw) if type_raw else ri
                        net_val   = _safe_int(net_raw)
                        key = self._FUTURES_INVESTOR_TYPE_MAP.get(type_code)
                        if key:
                            nets[key] = net_val
                    except Exception:
                        pass
                supported = bool(probe["rows"])

            _system_info(
                f"[CybosInvestorRaw] futures via {progid} supported={supported} "
                f"nets={{{','.join(f'{k}:{v:+d}' for k, v in nets.items() if v != 0)}}}"
            )
            return {
                "supported": supported,
                "source": progid,
                "reason": f"probe ok via {progid}",
                "nets": nets,
                "call_nets": call_nets,
                "put_nets": put_nets,
                "raw": {"open_interest": 0, "row_count": len(probe["rows"])},
            }

        # 모든 후보 실패 → FutureMst 미결제약정 fallback
        snap = self.request_futures_snapshot(code) if code else {}
        oi = _safe_int(snap.get("open_interest", 0)) if snap else 0
        _system_info_throttled(
            f"[CybosInvestorRaw] futures investor TR 후보 없음 "
            f"open_interest={oi} (FutureMst fallback)",
            key="cybos_investor_raw_futures_missing",
            min_interval_sec=600.0,
        )
        return {
            "supported": False,
            "source": "FutureMst_oi",
            "reason": "Cybos 선물 투자자 TR 미발견; 미결제약정만 제공",
            "nets": {},
            "call_nets": {},
            "put_nets": {},
            "raw": {"open_interest": oi},
        }

    def request_program_investor(self, market: str = "1") -> Dict[str, Any]:
        """
        프로그램매매 종합매매현황 (Dscbo1.CpSvr8111).

        [260704 감사 P2] 필드 매핑을 공식 문서(cybosplus.github.io/cpdib_rtf_1_/cpsvr8111.htm)
        기준으로 확정했다(2026-07-05, 사용자가 실제 Creon Plus 연결로 확인) — 이전 코드의
        "guess"(h[0~2]=arb, h[3~5]=nonarb)는 완전히 틀렸었다. 실제 GetHeaderValue 레이아웃:

            idx0=날짜, idx1=시간
            idx2~7   = 차익매도   (위탁/자기/합계 × 수량/금액)
            idx8~13  = 차익매수   (위탁/자기/합계 × 수량/금액)
            idx14~19 = 차익순매수 (idx14=위탁수량,15=자기수량,16=합계수량,
                                    17=위탁금액,18=자기금액,19=합계금액)
            idx20~25 = 비차익매도
            idx26~31 = 비차익매수
            idx32~37 = 비차익순매수 (idx32=위탁수량,33=자기수량,34=합계수량,
                                      35=위탁금액,36=자기금액,37=합계금액)
            idx38~55 = 전체(차익+비차익 합산) 매도/매수/순매수

        입력 idx0 = 거래소/코스닥 구분코드: '1'=거래소(KOSPI), '2'=코스닥.
        KOSPI200 선물 시스템이므로 기본값 '1'.

        실측(2026-07-05, 장중): Dscbo1.CpSvr8111S/8111KS는 BlockRequest 미지원
        ("본 객체에서는 지원하지 않는 함수입니다") — 8111S는 실시간 구독 전용으로 추정,
        조회는 8111(비실시간)만 사용한다. CpSvr8119/CpSvrNew8119는 종목별(입력 없인 전종목
        순회) TR로 이 용도(시장 전체 요약)에 맞지 않아 후보에서 제외했다.
        """
        ARB_NET_AMOUNT_IDX = 19       # 차익순매수체결금액 (총, KRW)
        NONARB_NET_AMOUNT_IDX = 37    # 비차익순매수체결금액 (총, KRW)

        # [260704 P2 재수정] 최초 str(market)="1" 시도가 "해당자료가 없습니다(100)"로 실패 —
        # 같은 코드베이스의 CpSvrNew7221(request_investor_futures)이 이미 ord('1')(아스키 49)
        # 관례를 쓰고 있어 동일하게 맞춤(2026-07-05, 실제 Creon Plus 연결로 확인).
        probe = self._probe_investor_tr("Dscbo1.CpSvr8111", [(0, ord(str(market)))], allow_status_error=True)
        if probe is None:
            _system_info_throttled(
                "[CybosInvestorRaw] CpSvr8111 dispatch/request 실패",
                key="cybos_investor_raw_program_missing",
                min_interval_sec=600.0,
            )
            return {
                "supported": False,
                "source": "Dscbo1.CpSvr8111",
                "reason": "dispatch/request 실패",
                "nets": {},
                "raw": {"arb_net": 0, "nonarb_net": 0},
            }

        if _safe_int(probe.get("status", 0)) != 0:
            system_logger.info(
                "[CybosInvestorRaw] CpSvr8111 reachable but status=%s msg=%s",
                probe.get("status"), probe.get("msg"),
            )
            return {
                "supported": False,
                "source": "Dscbo1.CpSvr8111",
                "reason": f"dib status={probe.get('status')} msg={probe.get('msg')}",
                "nets": {},
                "raw": {"arb_net": 0, "nonarb_net": 0},
            }

        h = probe["headers"]
        arb_net = _safe_int(h.get(ARB_NET_AMOUNT_IDX, "0"))
        nonarb_net = _safe_int(h.get(NONARB_NET_AMOUNT_IDX, "0"))

        _system_info(
            f"[CybosInvestorRaw] program via CpSvr8111(market={market}) "
            f"arb={arb_net:+d} nonarb={nonarb_net:+d}"
        )
        return {
            "supported": True,
            "source": "Dscbo1.CpSvr8111",
            "reason": "verified field mapping (cybosplus docs, 2026-07-05)",
            "nets": {"foreign": arb_net + nonarb_net},
            "raw": {"arb_net": arb_net, "nonarb_net": nonarb_net},
        }

    def _ensure_message_pump(self) -> None:
        if QTimer is None or self._message_pump_timer is not None:
            return
        self._message_pump_timer = QTimer()
        self._message_pump_timer.timeout.connect(self._pump_messages)
        self._message_pump_timer.start(50)

    def _pump_messages(self) -> None:
        if pythoncom is None:
            return
        try:
            pythoncom.PumpWaitingMessages()
        except Exception:
            logger.debug("[Cybos] COM message pump failed", exc_info=True)

    def _ensure_trade_init(self) -> None:
        if self._cp_trade_util is None:
            raise RuntimeError("Cybos API is not connected. Call connect() first.")
        ret = self._cp_trade_util.TradeInit(0)
        if ret not in (0, None):
            raise RuntimeError("CpTdUtil.TradeInit failed with ret={0}".format(ret))

    def _subscribe_fill_events(self) -> None:
        if self._fill_subscription is not None:
            return
        self._fill_subscription = self.create_subscription(
            progid=CYBOS_CONCLUSION_PROGID,
            input_values={},
            owner=self,
            event_name="fill",
        )

    def _handle_disconnect(self) -> None:
        logger.warning("[Cybos] disconnected from U-CYBOS")
        self._emit_msg(
            {
                "source": "CpCybos",
                "status": "DISCONNECT",
                "status_code": -1,
                "message": "U-CYBOS disconnected",
            }
        )

    def _handle_subscription_event(self, event_name: str, sink) -> None:
        com_object = getattr(sink, "_obj_", None)
        if com_object is None:
            com_object = getattr(sink, "_oleobj_", None)
        if event_name == "fill":
            # payload 추출은 반드시 여기서(COM 콜백 스택 안, 동기) 수행한다 —
            # CpFConclusion은 공유 버퍼라 다음 이벤트가 도착하면 값이 덮어써진다.
            # 추출 이후의 처리(_emit_fill → TradingSystem 콜백 체인의 DB 기록·
            # 잔고 TR 등)는 무겁고 때로 동기 BlockRequest를 포함할 수 있어
            # COM 콜백 스택 안에서 실행하면 재진입 위험이 있다 — 큐에 적재만
            # 하고 실제 처리는 _drain_fill_queue로 미룬다.
            payload = self._extract_fill_payload(self._fill_subscription.com_object)
            self._fill_queue.append(payload)
            self._schedule_fill_drain()

    def _schedule_fill_drain(self) -> None:
        if self._fill_drain_scheduled:
            return
        if QTimer is None:
            # QTimer 불가 환경(예외적) — 유실보다 즉시 처리가 안전하므로 폴백.
            self._drain_fill_queue()
            return
        self._fill_drain_scheduled = True
        QTimer.singleShot(0, self._drain_fill_queue)

    def _drain_fill_queue(self) -> None:
        self._fill_drain_scheduled = False
        while self._fill_queue:
            payload = self._fill_queue.popleft()
            self._emit_fill(payload)

    def _extract_fill_payload(self, obj) -> Dict[str, Any]:
        side_code = _safe_str(obj.GetHeaderValue(12))
        balance_side_code = _safe_str(obj.GetHeaderValue(45))
        status_code = _safe_str(obj.GetHeaderValue(44)) or _safe_str(obj.GetHeaderValue(15))

        payload = {
            "gubun": "0",
            "transaction_name": _safe_str(obj.GetHeaderValue(0)),
            "account_name": _safe_str(obj.GetHeaderValue(1)),
            "code_name": _safe_str(obj.GetHeaderValue(2)),
            "filled_qty": _safe_int(obj.GetHeaderValue(3)),
            "fill_price": _safe_float(obj.GetHeaderValue(4)),
            "order_no": _safe_str(obj.GetHeaderValue(5)),
            "original_order_no": _safe_str(obj.GetHeaderValue(6)),
            "account_no": _safe_str(obj.GetHeaderValue(7)),
            "goods_code": _safe_str(obj.GetHeaderValue(8)),
            "code": _normalize_code(_safe_str(obj.GetHeaderValue(9))),
            "side_code": side_code,
            "side": BALANCE_SIDE_MAP.get(side_code, side_code),
            "trade_gubun": side_code,
            "order_gubun": BALANCE_SIDE_MAP.get(side_code, side_code),
            "order_kind_code": _safe_str(obj.GetHeaderValue(20)),
            "order_condition_code": _safe_str(obj.GetHeaderValue(43)),
            "order_status_code": status_code,
            "order_status": ORDER_STATUS_MAP.get(status_code, status_code),
            "receipt_no": _safe_str(obj.GetHeaderValue(16)),
            "sell_balance": _safe_int(obj.GetHeaderValue(13)),
            "buy_balance": _safe_int(obj.GetHeaderValue(18)),
            "sell_avg_price": _safe_float(obj.GetHeaderValue(29)),
            "buy_avg_price": _safe_float(obj.GetHeaderValue(30)),
            "balance_side_code": balance_side_code,
            "position_qty": _safe_int(obj.GetHeaderValue(46)),
            "closable_qty": _safe_int(obj.GetHeaderValue(47)),
            "current_price": _safe_float(obj.GetHeaderValue(4)),
            "unfilled_qty": 0,
            "fill_no": "",
        }
        return payload

    def _emit_fill(self, payload: Dict[str, Any]) -> None:
        for callback in list(self._fill_callbacks):
            try:
                callback(dict(payload))
            except Exception:
                logger.exception("[Cybos] fill callback failed")

    def _emit_msg(self, payload: Dict[str, Any]) -> None:
        for callback in list(self._msg_callbacks):
            try:
                callback(dict(payload))
            except Exception:
                logger.exception("[Cybos] msg callback failed")

    def _warn_investor_mapping_once(self, key: str, message: str) -> None:
        if key in self._investor_mapping_warned:
            return
        self._investor_mapping_warned.add(key)
        _system_warning(message)
