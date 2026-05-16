from __future__ import annotations

import logging
import platform
import threading
import time
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
ORDER_CONDITION_DEFAULT = "0"

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
        try:
            system_logger.info(
                "[CybosEvent] recv begin progid=%s event=%s owner=%s",
                getattr(self, "_progid", ""),
                getattr(self, "_event_name", ""),
                type(owner).__name__,
            )
        except Exception:
            pass
        owner._handle_subscription_event(self._event_name, self)
        try:
            system_logger.info(
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
        if not account_no:
            return None
        self._ensure_trade_init()

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
        profit_rate = (next_day_deposit_cash / deposit_cash * 100.0) if deposit_cash else 0.0

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
            logger.critical(
                "[CybosOrder] %s account=%s code=%s side=%s qty=%s",
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
        logger.info("[CybosOrder] ret=%s status=%s msg=%s payload=%s", ret, status, msg, payload)
        if ret not in (0, None):
            return _safe_int(ret, -1)
        if status != 0:
            return status or -1
        return 0

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
        logger.info("[CybosInvestorProbe] not implemented; extra_codes=%s", extra_codes or [])

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

    # CpSysDib.CpSvrNew7212 한글 투자자명 → INVESTOR_KEYS 매핑
    # (레지스트리 검증 2026-05-11: row[0]=투자자명, row[3]=선물순매수,
    #  row[6]=콜순매수, row[9]=풋순매수)
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

    def _probe_investor_tr(
        self,
        progid: str,
        inputs: List[tuple],
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
            if ret not in (0, None) or status != 0:
                logger.debug(
                    "[CybosProbe] %s blocked ret=%s status=%s msg=%s",
                    progid, ret, status, _safe_str(obj.GetDibMsg1()),
                )
                return None
            headers: Dict[int, str] = {}
            for i in range(24):
                try:
                    headers[i] = _safe_str(obj.GetHeaderValue(i))
                except Exception:
                    break
            rows: List[Dict[int, str]] = []
            for ri in range(20):
                row: Dict[int, str] = {}
                any_val = False
                for fi in range(10):
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
            logger.info(
                "[CybosProbe] %s ok status=%s nonempty_headers=%d rows=%d",
                progid, status,
                sum(1 for v in headers.values() if v),
                len(rows),
            )
            return {"progid": progid, "headers": headers, "rows": rows}
        except Exception as exc:
            logger.debug("[CybosProbe] %s dispatch/request failed: %s", progid, exc)
            return None

    def request_investor_futures(self) -> Dict[str, Any]:
        """
        선물/콜/풋 투자자별 순매수를 반환한다.

        CpSysDib.CpSvrNew7212 (레지스트리 검증 2026-05-11):
          입력 없음, row[0]=투자자명(한글), row[3]=선물순매수,
          row[6]=콜순매수, row[9]=풋순매수.
          단위는 백만원(MKR) 추정 — 방향(부호)이 핵심.
        """
        code = self.get_nearest_futures_code()
        candidates = [
            # P0: 레지스트리 검증 완료 — 선물+콜+풋 투자자별 누적 매매통계
            # idx0=1 → 최근 1개월(30거래일) 누적, 단기 방향 신호에 적합
            # (idx0=0→빈값, 기본값→YTD 누적, idx0=N→N개월 누적)
            ("CpSysDib.CpSvrNew7212", [(0, 1)]),
            # fallback: 기존 추측 후보 (실제로는 미등록, 탐색용 유지)
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

            if progid == "CpSysDib.CpSvrNew7212":
                # 한글 투자자명 기반 파싱
                # row[0]=투자자명, row[3]=선물순매수, row[6]=콜순매수, row[9]=풋순매수
                for row in probe["rows"]:
                    name = _safe_str(row.get(0, "")).strip()
                    key = self._FUTURES_INVESTOR_NAME_MAP.get(name)
                    if not key:
                        continue
                    nets[key]      = _safe_int(row.get(3, 0))
                    call_nets[key] = _safe_int(row.get(6, 0))
                    put_nets[key]  = _safe_int(row.get(9, 0))
                supported = bool(nets)
            else:
                # 숫자 투자자코드 기반 파싱 (기존 로직)
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

    def request_program_investor(self) -> Dict[str, Any]:
        """
        프로그램 매매(차익/비차익) 순매수 데이터를 반환한다.
        Cybos Plus 후보 ProgID를 순서대로 시도한다.

        Dscbo1.CpSvr8119 (레지스트리 검증 2026-05-11):
          입력 없음, pgm.bid 응답, 장 중 누적 프로그램 매매 동향.
          헤더 레이아웃 추정 (장 중 _probe_8119_fields.py로 확인 요망):
            h[0]=차익매수, h[1]=차익매도, h[2]=차익순매수,
            h[3]=비차익매수, h[4]=비차익매도, h[5]=비차익순매수,
            h[6]=전체매수, h[7]=전체매도, h[8]=전체순매수 (단위: 백만원 추정)
        """
        candidates = [
            # P0: 레지스트리 검증 완료 — 장 중 누적 프로그램 매매 동향
            ("Dscbo1.CpSvr8119",         []),
            ("Dscbo1.CpSvrNew8119",      []),
            # fallback: 미등록 확인, 탐색용 유지
            ("CpSysDib.ProgramTrade",    []),
            ("Dscbo1.ProgramTrade",       []),
        ]
        for progid, inputs in candidates:
            probe = self._probe_investor_tr(progid, inputs)
            if probe is None:
                continue
            h = probe["headers"]
            # 헤더 레이아웃 추정: h[0~2]=차익(매수/매도/순), h[3~5]=비차익, h[6~8]=전체
            arb_buy    = _safe_int(h.get(0, "0"))
            arb_sell   = _safe_int(h.get(1, "0"))
            arb_net    = _safe_int(h.get(2, "0")) or (arb_buy - arb_sell)
            nonarb_buy  = _safe_int(h.get(3, "0"))
            nonarb_sell = _safe_int(h.get(4, "0"))
            nonarb_net  = _safe_int(h.get(5, "0")) or (nonarb_buy - nonarb_sell)

            # 헤더가 모두 0인 경우 (장 마감 후 or 미입력) → 데이터 없음으로 처리
            if arb_net == 0 and nonarb_net == 0 and arb_buy == 0 and nonarb_buy == 0:
                logger.debug(
                    "[CybosInvestorRaw] %s all-zero headers — market closed or no data", progid
                )
                continue

            _system_info(
                f"[CybosInvestorRaw] program via {progid} "
                f"arb={arb_net:+d} nonarb={nonarb_net:+d}"
            )
            return {
                "supported": True,
                "source": progid,
                "reason": f"probe ok via {progid}",
                "nets": {"foreign": arb_net + nonarb_net},
                "raw": {"arb_net": arb_net, "nonarb_net": nonarb_net},
            }

        _system_info_throttled(
            "[CybosInvestorRaw] program investor TR 후보 없음",
            key="cybos_investor_raw_program_missing",
            min_interval_sec=600.0,
        )
        return {
            "supported": False,
            "source": "mapping_pending",
            "reason": "Cybos 프로그램 매매 TR 미발견",
            "nets": {},
            "raw": {"arb_net": 0, "nonarb_net": 0},
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
            self._emit_fill(self._extract_fill_payload(self._fill_subscription.com_object))

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
