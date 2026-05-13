from __future__ import annotations

import argparse
import sys
import time


def build_parser():
    parser = argparse.ArgumentParser(
        description="Listen to Cybos futures realtime only and report tick/hoga flow."
    )
    parser.add_argument(
        "--listen-sec",
        type=int,
        default=20,
        help="Realtime listen duration in seconds",
    )
    parser.add_argument(
        "--progress-sec",
        type=int,
        default=5,
        help="Progress print interval in seconds",
    )
    parser.add_argument(
        "--code",
        default="",
        help="Explicit futures realtime code (default: nearest futures code from CpFutureCode)",
    )
    parser.add_argument(
        "--mini",
        action="store_true",
        help="Use CpUtil.CpKFutureCode to resolve mini futures code instead of regular futures",
    )
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


class RealtimeCounter(object):
    def __init__(self):
        self.tick_count = 0
        self.hoga_count = 0
        self.last_tick = {}
        self.last_hoga = {}


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


def resolve_nearest_code(future_code):
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
    return nearest_code, nearest_name


def probe_mini_futures_code(win32com_client):
    """FutureMst BlockRequest로 후보 코드를 프로브해 KOSPI200 미니선물 근월물 반환.

    Cybos COM 열거 객체(CpFutureCode, CpKFutureCode) 어디에도 A05xxx가 없다.
    (CpFutureCode=KOSPI200 일반선물 A01xxx, CpKFutureCode=코스닥150 A06xxx — 2026-05-13 실증)
    코드 규칙: A05 + 연도끝자리 + 월(hex uppercase) — 예) 2026년5월=A0565, 6월=A0566, 12월=A056C
    """
    import datetime
    today = datetime.date.today()
    candidates = []
    for delta in range(7):
        month = today.month + delta
        year = today.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        year_digit = str(year)[-1]
        month_hex = format(month, "X")
        candidates.append("A05{0}{1}".format(year_digit, month_hex))

    print("[MINI] Probing FutureMst for mini futures codes:", candidates)
    snapshot = win32com_client.Dispatch("Dscbo1.FutureMst")
    for code in candidates:
        snapshot.SetInputValue(0, code)
        snapshot.BlockRequest()
        status = safe_int(snapshot.GetDibStatus())
        price = safe_float(snapshot.GetHeaderValue(71))
        name = safe_str(snapshot.GetHeaderValue(1)) if status == 0 else ""
        print("[MINI]   probe code={0!r} DibStatus={1} price={2} name={3!r}".format(
            code, status, price, name))
        if status == 0 and price > 0:
            return code, name or code
    return "", ""


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

    if args.mini:
        # CpFutureCode/CpKFutureCode 모두 A05xxx를 포함하지 않으므로 FutureMst 프로브 사용
        nearest_code, nearest_name = probe_mini_futures_code(win32com.client)
    else:
        future_code = win32com.client.Dispatch("CpUtil.CpFutureCode")
        nearest_code, nearest_name = resolve_nearest_code(future_code)

    code = safe_str(args.code) or nearest_code
    if not code:
        print("[FAIL] Could not resolve a futures code.")
        return 5

    print("[CHECK] Realtime code =", code, nearest_name,
          "(미니선물)" if args.mini else "(일반선물)")

    snapshot = win32com.client.Dispatch("Dscbo1.FutureMst")
    snapshot.SetInputValue(0, code)
    snapshot.BlockRequest()
    print("[SNAPSHOT] DibStatus =", snapshot.GetDibStatus())
    print("[SNAPSHOT] DibMsg1 =", safe_str(snapshot.GetDibMsg1()))
    print(
        "[SNAPSHOT] price/open/high/low =",
        safe_float(snapshot.GetHeaderValue(71)),
        safe_float(snapshot.GetHeaderValue(72)),
        safe_float(snapshot.GetHeaderValue(73)),
        safe_float(snapshot.GetHeaderValue(74)),
    )
    print(
        "[SNAPSHOT] ask1/bid1/ask_qty1/bid_qty1/state =",
        safe_float(snapshot.GetHeaderValue(37)),
        safe_float(snapshot.GetHeaderValue(54)),
        safe_int(snapshot.GetHeaderValue(42)),
        safe_int(snapshot.GetHeaderValue(59)),
        safe_int(snapshot.GetHeaderValue(115)),
    )

    counter = RealtimeCounter()
    cur_obj = win32com.client.Dispatch("Dscbo1.FutureCurOnly")
    cur_obj.SetInputValue(0, code)
    cur_evt = win32com.client.WithEvents(cur_obj, FutureCurOnlyEvent)
    cur_evt.set_context(cur_obj, counter)

    hoga_obj = win32com.client.Dispatch("CpSysDib.FutureJpBid")
    hoga_obj.SetInputValue(0, code)
    hoga_evt = win32com.client.WithEvents(hoga_obj, FutureJpBidEvent)
    hoga_evt.set_context(hoga_obj, counter)

    cur_obj.SubscribeLatest()
    hoga_obj.SubscribeLatest()

    print("[REALTIME] Listening for", args.listen_sec, "seconds...")
    started = time.time()
    next_progress = started + max(1, args.progress_sec)

    while time.time() - started < args.listen_sec:
        pythoncom.PumpWaitingMessages()
        if time.time() >= next_progress:
            print(
                "[PROGRESS] tick_count={0} hoga_count={1} last_tick_time={2} last_price={3} last_hoga_bidask={4}/{5}".format(
                    counter.tick_count,
                    counter.hoga_count,
                    counter.last_tick.get("time", ""),
                    counter.last_tick.get("price", 0.0),
                    counter.last_hoga.get("bid1", 0.0),
                    counter.last_hoga.get("ask1", 0.0),
                )
            )
            next_progress += max(1, args.progress_sec)
        time.sleep(0.05)

    print("[RESULT] Tick count =", counter.tick_count)
    print("[RESULT] Last tick =", counter.last_tick)
    print("[RESULT] Hoga count =", counter.hoga_count)
    print("[RESULT] Last hoga =", counter.last_hoga)

    try:
        cur_obj.Unsubscribe()
    except Exception:
        pass
    try:
        hoga_obj.Unsubscribe()
    except Exception:
        pass

    if counter.tick_count > 0 and counter.hoga_count > 0:
        print("[PASS] Tick and hoga events were both captured.")
        return 0
    if counter.tick_count > 0 or counter.hoga_count > 0:
        print("[WARN] Only one realtime stream was captured. Inspect partial wiring/logging.")
        return 10

    print("[FAIL] No realtime events were captured during listen window.")
    return 11


if __name__ == "__main__":
    sys.exit(main())
