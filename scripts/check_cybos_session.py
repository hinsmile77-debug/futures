from __future__ import annotations

import argparse
import sys
import time


def build_parser():
    parser = argparse.ArgumentParser(
        description="Check Cybos Plus API session, balance, realtime, and optional order flow."
    )
    parser.add_argument("--account-no", required=True, help="Cybos futures/options account number")
    parser.add_argument("--listen-sec", type=int, default=10, help="Realtime listen duration in seconds")
    parser.add_argument("--send-order", action="store_true", help="Send a test futures market order")
    parser.add_argument("--side", choices=["BUY", "SELL"], default="BUY", help="Order side for --send-order")
    parser.add_argument("--qty", type=int, default=1, help="Order quantity for --send-order")
    return parser


def safe_str(value):
    if value is None:
        return ""
    return str(value).strip()


def safe_int(value, default=0):
    try:
        text = safe_str(value).replace(",", "")
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def safe_float(value, default=0.0):
    try:
        text = safe_str(value).replace(",", "")
        if not text:
            return default
        return float(text)
    except Exception:
        return default


class EventCounter(object):
    def __init__(self):
        self.tick_count = 0
        self.hoga_count = 0
        self.fill_count = 0
        self.last_tick = {}
        self.last_hoga = {}
        self.last_fill = {}


class FutureCurOnlyEvent(object):
    def set_context(self, parent, counter):
        self.parent = parent
        self.counter = counter

    def OnReceived(self):
        obj = self.parent
        self.counter.tick_count += 1
        self.counter.last_tick = {
            "code": safe_str(obj.GetHeaderValue(0)),
            "price": safe_float(obj.GetHeaderValue(1)),
            "cum_volume": safe_int(obj.GetHeaderValue(13)),
            "open_interest": safe_int(obj.GetHeaderValue(14)),
            "time": safe_str(obj.GetHeaderValue(15)),
            "ask1": safe_float(obj.GetHeaderValue(18)),
            "bid1": safe_float(obj.GetHeaderValue(19)),
            "ask_qty1": safe_int(obj.GetHeaderValue(20)),
            "bid_qty1": safe_int(obj.GetHeaderValue(21)),
            "trade_flag": safe_str(obj.GetHeaderValue(24)),
        }


class FutureJpBidEvent(object):
    def set_context(self, parent, counter):
        self.parent = parent
        self.counter = counter

    def OnReceived(self):
        obj = self.parent
        self.counter.hoga_count += 1
        self.counter.last_hoga = {
            "code": safe_str(obj.GetHeaderValue(0)),
            "ask1": safe_float(obj.GetHeaderValue(2)),
            "ask_qty1": safe_int(obj.GetHeaderValue(7)),
            "bid1": safe_float(obj.GetHeaderValue(19)),
            "bid_qty1": safe_int(obj.GetHeaderValue(24)),
            "market_state": safe_str(obj.GetHeaderValue(36)),
        }


class FillEvent(object):
    def set_context(self, parent, counter):
        self.parent = parent
        self.counter = counter

    def OnReceived(self):
        obj = self.parent
        self.counter.fill_count += 1
        self.counter.last_fill = {
            "account_no": safe_str(obj.GetHeaderValue(7)),
            "code": safe_str(obj.GetHeaderValue(9)),
            "filled_qty": safe_int(obj.GetHeaderValue(3)),
            "fill_price": safe_float(obj.GetHeaderValue(4)),
            "order_no": safe_str(obj.GetHeaderValue(5)),
            "original_order_no": safe_str(obj.GetHeaderValue(6)),
            "side_code": safe_str(obj.GetHeaderValue(12)),
            "status_code": safe_str(obj.GetHeaderValue(44)),
            "position_side_code": safe_str(obj.GetHeaderValue(45)),
            "position_qty": safe_int(obj.GetHeaderValue(46)),
            "closable_qty": safe_int(obj.GetHeaderValue(47)),
        }


def main():
    args = build_parser().parse_args()

    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        print("[FAIL] pywin32 import error:", exc)
        return 2

    pythoncom.CoInitialize()

    cp = win32com.client.Dispatch("CpUtil.CpCybos")
    print("[CHECK] IsConnect =", cp.IsConnect)
    print("[CHECK] ServerType =", cp.ServerType)
    if cp.IsConnect != 1:
        print("[FAIL] Cybos Plus API is not connected.")
        return 3

    trade = win32com.client.Dispatch("CpTrade.CpTdUtil")
    trade_init = trade.TradeInit(0)
    print("[CHECK] TradeInit =", trade_init)
    if trade_init not in (0, None):
        print("[FAIL] TradeInit failed.")
        return 4

    accounts = list(trade.AccountNumber)
    print("[CHECK] Accounts =", accounts)
    if args.account_no not in accounts:
        print("[FAIL] Account not available in this session:", args.account_no)
        return 5

    try:
        goods = list(trade.GoodsList(args.account_no, 2))
    except Exception as exc:
        goods = []
        print("[WARN] GoodsList failed:", exc)
    print("[CHECK] GoodsList(futures/options) =", goods)

    future_code = win32com.client.Dispatch("CpUtil.CpFutureCode")
    future_count = safe_int(future_code.GetCount())
    nearest_code = ""
    nearest_name = ""
    for idx in range(future_count):
        code = safe_str(future_code.GetData(0, idx))
        name = safe_str(future_code.GetData(1, idx))
        if code.startswith("A") and "F" in name:
            nearest_code = code
            nearest_name = name
            break
    if not nearest_code and future_count > 0:
        nearest_code = safe_str(future_code.GetData(0, 0))
        nearest_name = safe_str(future_code.GetData(1, 0))
    print("[CHECK] Nearest future =", nearest_code, nearest_name)

    balance = win32com.client.Dispatch("CpTrade.CpTd0723")
    balance.SetInputValue(0, args.account_no)
    balance.SetInputValue(1, "50")
    balance.SetInputValue(2, "1")
    balance.SetInputValue(3, "")
    balance.SetInputValue(4, 20)
    balance.BlockRequest()
    print("[BALANCE] DibStatus =", balance.GetDibStatus())
    print("[BALANCE] DibMsg1 =", safe_str(balance.GetDibMsg1()))
    balance_count = safe_int(balance.GetHeaderValue(2))
    print("[BALANCE] Count =", balance_count)
    for idx in range(balance_count):
        row = {
            "code": safe_str(balance.GetDataValue(0, idx)),
            "name": safe_str(balance.GetDataValue(1, idx)),
            "side_code": safe_str(balance.GetDataValue(2, idx)),
            "qty": safe_int(balance.GetDataValue(3, idx)),
            "avg_price": safe_float(balance.GetDataValue(5, idx)),
            "closable_qty": safe_int(balance.GetDataValue(9, idx)),
            "trade_qty": safe_int(balance.GetDataValue(10, idx)),
        }
        print("[BALANCE] Row", idx, row)

    snapshot = win32com.client.Dispatch("Dscbo1.FutureMst")
    snapshot.SetInputValue(0, nearest_code)
    snapshot.BlockRequest()
    print("[SNAPSHOT] DibStatus =", snapshot.GetDibStatus())
    print("[SNAPSHOT] DibMsg1 =", safe_str(snapshot.GetDibMsg1()))
    print(
        "[SNAPSHOT] price/open/high/low/oi =",
        safe_float(snapshot.GetHeaderValue(71)),
        safe_float(snapshot.GetHeaderValue(72)),
        safe_float(snapshot.GetHeaderValue(73)),
        safe_float(snapshot.GetHeaderValue(74)),
        safe_int(snapshot.GetHeaderValue(80)),
    )
    print(
        "[SNAPSHOT] ask1/bid1/ask_qty1/bid_qty1/state =",
        safe_float(snapshot.GetHeaderValue(37)),
        safe_float(snapshot.GetHeaderValue(54)),
        safe_int(snapshot.GetHeaderValue(42)),
        safe_int(snapshot.GetHeaderValue(59)),
        safe_int(snapshot.GetHeaderValue(115)),
    )

    counter = EventCounter()
    cur_obj = win32com.client.Dispatch("Dscbo1.FutureCurOnly")
    cur_obj.SetInputValue(0, nearest_code)
    cur_evt = win32com.client.WithEvents(cur_obj, FutureCurOnlyEvent)
    cur_evt.set_context(cur_obj, counter)

    hoga_obj = win32com.client.Dispatch("CpSysDib.FutureJpBid")
    hoga_obj.SetInputValue(0, nearest_code)
    hoga_evt = win32com.client.WithEvents(hoga_obj, FutureJpBidEvent)
    hoga_evt.set_context(hoga_obj, counter)

    fill_obj = win32com.client.Dispatch("Dscbo1.CpFConclusion")
    fill_evt = win32com.client.WithEvents(fill_obj, FillEvent)
    fill_evt.set_context(fill_obj, counter)

    fill_obj.Subscribe()
    cur_obj.SubscribeLatest()
    hoga_obj.SubscribeLatest()

    print("[REALTIME] Listening for", args.listen_sec, "seconds...")
    started = time.time()
    while time.time() - started < args.listen_sec:
        pythoncom.PumpWaitingMessages()
        time.sleep(0.1)

    print("[REALTIME] Tick count =", counter.tick_count)
    print("[REALTIME] Last tick =", counter.last_tick)
    print("[REALTIME] Hoga count =", counter.hoga_count)
    print("[REALTIME] Last hoga =", counter.last_hoga)
    print("[REALTIME] Fill count =", counter.fill_count)
    print("[REALTIME] Last fill =", counter.last_fill)
    if counter.tick_count == 0 and counter.hoga_count == 0:
        print("[REALTIME] No realtime events captured. This is expected outside market hours.")

    if args.send_order:
        side_code = "2" if args.side == "BUY" else "1"
        order = win32com.client.Dispatch("CpTrade.CpTd6831")
        order.SetInputValue(1, args.account_no)
        order.SetInputValue(2, nearest_code)
        order.SetInputValue(3, int(args.qty))
        order.SetInputValue(4, 0)
        order.SetInputValue(5, side_code)
        order.SetInputValue(6, "2")
        order.SetInputValue(7, "0")
        order.SetInputValue(8, "50")
        ret = order.BlockRequest()
        print("[ORDER] BlockRequest ret =", ret)
        print("[ORDER] DibStatus =", order.GetDibStatus())
        print("[ORDER] DibMsg1 =", safe_str(order.GetDibMsg1()))

        print("[ORDER] Waiting for fill events...")
        started = time.time()
        base_fill_count = counter.fill_count
        while time.time() - started < 10:
            pythoncom.PumpWaitingMessages()
            if counter.fill_count > base_fill_count:
                break
            time.sleep(0.1)
        print("[ORDER] Fill count =", counter.fill_count)
        print("[ORDER] Last fill =", counter.last_fill)

    try:
        cur_obj.Unsubscribe()
    except Exception:
        pass
    try:
        hoga_obj.Unsubscribe()
    except Exception:
        pass
    try:
        fill_obj.Unsubscribe()
    except Exception:
        pass

    print("[DONE] Session check finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
