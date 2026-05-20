# -*- coding: utf-8 -*-
"""
Cybos Plus session preflight.

Exit codes:
    0 = all checks passed
    1 = COM connection failed
    2 = TradeInit failed
    3 = exception while dispatching COM
"""
import datetime
import struct
import sys

if struct.calcsize("P") != 4:
    print("[ERROR] 32-bit Python is required, current=%d-bit" % (struct.calcsize("P") * 8))
    sys.exit(3)

import win32com.client


def main():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[%s] Cybos Plus Preflight Check start" % ts)

    try:
        cp = win32com.client.Dispatch("CpUtil.CpCybos")
        is_connect = cp.IsConnect
        server_type = cp.ServerType
    except Exception as exc:
        print("[CHECK 1/3] COM Dispatch failed: %s" % exc)
        sys.exit(3)

    print("[CHECK 1/3] IsConnect=%d  %s" % (
        is_connect, "connected" if is_connect == 1 else "disconnected"))
    if is_connect != 1:
        print("[ERROR] Cybos Plus COM is not connected.")
        sys.exit(1)

    print("[CHECK 2/3] ServerType=%s" % server_type)

    trade_init_param = 0
    try:
        is_mock = int(server_type) == 2
    except (TypeError, ValueError):
        is_mock = server_type is not None and u"모의" in str(server_type)
    if is_mock:
        trade_init_param = 1
        print("[CHECK 3/3] Mock server detected -- TradeInit(1)")
    else:
        print("[CHECK 3/3] Real server detected -- TradeInit(0)")

    try:
        trade = win32com.client.Dispatch("CpTrade.CpTdUtil")
        ret = trade.TradeInit(trade_init_param)
    except Exception as exc:
        print("[CHECK 3/3] TradeInit exception: %s" % exc)
        sys.exit(2)

    print("[CHECK 3/3] TradeInit(%d)=%s  %s" % (
        trade_init_param, ret, "success" if ret in (0, None) else "failed"))
    if ret not in (0, None):
        print("[ERROR] TradeInit failed with ret=%s" % ret)
        sys.exit(2)

    print("[PASS] All preflight checks passed (%s)" % (
        datetime.datetime.now().strftime("%H:%M:%S")))
    sys.exit(0)


if __name__ == "__main__":
    main()
