from __future__ import annotations

import logging
import platform
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


def _require_cybos_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Cybos Plus is only available on Windows. " + CYBOS_RUNTIME_HINT)
    if pythoncom is None or Dispatch is None or WithEvents is None:
        raise RuntimeError("pywin32 is not available. " + CYBOS_RUNTIME_HINT)
    if platform.architecture()[0] != "32bit":
        raise RuntimeError("Cybos Plus COM objects require 32-bit Python. " + CYBOS_RUNTIME_HINT)


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
        owner._handle_subscription_event(self._event_name, self)


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
        if latest and hasattr(self._com_object, "SubscribeLatest"):
            self._com_object.SubscribeLatest()
        else:
            self._com_object.Subscribe()
        self._active = True

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

        self._cp_cybos_event = WithEvents(self._cp_cybos, _CybosConnectionEvent)
        self._cp_cybos_event.set_context(self)

        if not self.is_connected:
            try:
                if hasattr(self._cp_cybos, "CybosPlusConnect"):
                    self._cp_cybos.CybosPlusConnect()
                elif hasattr(self._cp_cybos, "CreonPlusConnect"):
                    self._cp_cybos.CreonPlusConnect()
            except Exception:
                logger.exception("[Cybos] connect request failed")

            deadline = time.time() + 5.0
            while time.time() < deadline and not self.is_connected:
                self._pump_messages()
                time.sleep(0.1)

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
            # main.py currently interprets "1" as Kiwoom mock server.
            # Cybos does not share that contract, so we return a
            # Kiwoom-compatible "real" value to avoid mock-only branches.
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

        obj = Dispatch(CYBOS_FUTURES_BALANCE_PROGID)
        obj.SetInputValue(0, account_no)
        obj.SetInputValue(1, CYBOS_GOODS_CODE_FUTURES)
        obj.SetInputValue(2, "1")
        obj.SetInputValue(3, "")
        obj.SetInputValue(4, 20)

        ret = obj.BlockRequest()
        status = _safe_int(obj.GetDibStatus())
        msg = _safe_str(obj.GetDibMsg1())
        if ret not in (0, None) or status != 0:
            logger.warning("[CybosBalance] request failed ret=%s status=%s msg=%s", ret, status, msg)
            self._emit_msg(
                {
                    "source": "CpTd0723",
                    "status": "ERROR",
                    "status_code": status or ret,
                    "message": msg,
                    "account_no": account_no,
                }
            )
            return None

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

            row = {
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
            }
            rows.append(row)

        summary = self._request_futures_daily_pnl_summary(account_no)

        nonempty_rows = [row for row in rows if _bool_nonblank(list(row.values()))]
        result = {
            "rows": rows,
            "nonempty_rows": nonempty_rows,
            "summary": summary,
            "summary_probe": {
                "dib_status": str(status),
                "dib_msg": msg,
                "count": str(count),
            },
            "record_name": "CpTd0723",
            "prev_next": "",
            "all_blank_rows": bool(rows) and not bool(nonempty_rows),
        }
        logger.info("[CybosBalance] account=%s rows=%d nonempty=%d", account_no, len(rows), len(nonempty_rows))
        return result

    def _request_futures_daily_pnl_summary(self, account_no: str) -> Dict[str, str]:
        today_yyMMdd = time.strftime("%y%m%d")
        try:
            obj = Dispatch(CYBOS_FUTURES_DAILY_PNL_PROGID)
            obj.SetInputValue(0, account_no)
            obj.SetInputValue(1, today_yyMMdd)
            obj.SetInputValue(2, CYBOS_GOODS_CODE_FUTURES)
            obj.SetInputValue(3, 10)

            ret = obj.BlockRequest()
            status = _safe_int(obj.GetDibStatus())
            msg = _safe_str(obj.GetDibMsg1())
            if ret not in (0, None) or status != 0:
                _system_warning(
                    f"[CybosDailyPnl] request failed account={account_no} "
                    f"ret={ret} status={status} msg={msg}"
                )
                return {}

            raw_headers = {idx: _safe_str(obj.GetHeaderValue(idx)) for idx in range(0, 21)}
            deposit_cash = _safe_float(raw_headers.get(DAILY_PNL_HEADER_DEPOSIT_CASH))
            next_day_deposit_cash = _safe_float(raw_headers.get(DAILY_PNL_HEADER_NEXT_DAY_DEPOSIT_CASH))
            prev_day_pnl = _safe_float(raw_headers.get(DAILY_PNL_HEADER_PREV_DAY_PNL))
            today_pnl = _safe_float(raw_headers.get(DAILY_PNL_HEADER_TODAY_PNL))
            liquidation_eval = _safe_float(raw_headers.get(DAILY_PNL_HEADER_LIQUIDATION_EVAL))
            if liquidation_eval <= 0.0 and next_day_deposit_cash > 0.0:
                liquidation_eval = next_day_deposit_cash
            profit_rate = (next_day_deposit_cash / deposit_cash * 100.0) if deposit_cash else 0.0

            header_validation = {
                "deposit_cash_idx": DAILY_PNL_HEADER_DEPOSIT_CASH,
                "next_day_deposit_cash_idx": DAILY_PNL_HEADER_NEXT_DAY_DEPOSIT_CASH,
                "prev_day_pnl_idx": DAILY_PNL_HEADER_PREV_DAY_PNL,
                "today_pnl_idx": DAILY_PNL_HEADER_TODAY_PNL,
                "liquidation_eval_idx": DAILY_PNL_HEADER_LIQUIDATION_EVAL,
                "liquidation_equals_next_day": liquidation_eval == next_day_deposit_cash,
                "prev_day_pnl_zero": prev_day_pnl == 0.0,
            }

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
        except Exception:
            system_logger.exception("[CybosDailyPnl] request failed with exception account=%s", account_no)
            try:
                log_manager.system(f"[CybosDailyPnl] exception account={account_no}", "WARNING")
            except Exception:
                pass
            return {}

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

        obj = Dispatch(CYBOS_FUTURES_ORDER_PROGID)
        obj.SetInputValue(1, account_no)
        obj.SetInputValue(2, _normalize_code(code))
        obj.SetInputValue(3, int(qty))
        obj.SetInputValue(4, 0)
        obj.SetInputValue(5, side_code)
        obj.SetInputValue(6, ORDER_HOGA_MARKET)
        obj.SetInputValue(7, ORDER_CONDITION_DEFAULT)
        obj.SetInputValue(8, CYBOS_GOODS_CODE_FUTURES)

        ret = obj.BlockRequest()
        status = _safe_int(obj.GetDibStatus())
        msg = _safe_str(obj.GetDibMsg1())
        payload = {
            "source": "CpTd6831",
            "status": "OK" if ret in (0, None) and status == 0 else "ERROR",
            "status_code": status if status else _safe_int(ret, 0),
            "message": msg,
            "account_no": account_no,
            "code": _normalize_code(code),
            "side": "매수" if side_code == "2" else "매도",
            "order_gubun": "매수" if side_code == "2" else "매도",
            "trade_gubun": side_code,
            "qty": int(qty),
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
        obj = Dispatch(progid)
        for key, value in sorted(input_values.items()):
            obj.SetInputValue(int(key), value)
        sink = WithEvents(obj, _CybosSubscriptionEvent)
        sink.set_context(owner, event_name, progid)
        subscription = CybosSubscription(obj, sink)
        subscription.subscribe(latest=latest)
        return subscription

    def request_futures_snapshot(self, code: str) -> Dict[str, Any]:
        obj = Dispatch("Dscbo1.FutureMst")
        obj.SetInputValue(0, _normalize_code(code))
        ret = obj.BlockRequest()
        status = _safe_int(obj.GetDibStatus())
        if ret not in (0, None) or status != 0:
            logger.warning(
                "[CybosSnapshot] request failed ret=%s status=%s msg=%s code=%s",
                ret,
                status,
                _safe_str(obj.GetDibMsg1()),
                code,
            )
            return {}

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

    def probe_investor_ticker(self, extra_codes: Optional[List[str]] = None) -> None:
        logger.info("[CybosInvestorProbe] not implemented; extra_codes=%s", extra_codes or [])

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
