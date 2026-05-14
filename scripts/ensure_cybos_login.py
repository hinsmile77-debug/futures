from __future__ import annotations

import time
from typing import Optional


def _safe_import_win32():
    try:
        import win32com.client  # type: ignore
    except Exception:
        return None
    return win32com.client


def is_cybos_connected() -> bool:
    win32com_client = _safe_import_win32()
    if win32com_client is None:
        return False
    try:
        cp = win32com_client.Dispatch("CpUtil.CpCybos")
        return bool(cp.IsConnect)
    except Exception:
        return False


def ensure_cybos_login(
    require_trade_init: bool = False,
    settle_wait_sec: float = 1.0,
) -> bool:
    if is_cybos_connected():
        if require_trade_init:
            _ensure_trade_init()
        return True

    import cybos_autologin

    try:
        ok = bool(cybos_autologin.autologin())
    except SystemExit:
        ok = False

    if not ok:
        return False

    if settle_wait_sec > 0:
        time.sleep(float(settle_wait_sec))

    if not is_cybos_connected():
        return False

    if require_trade_init:
        _ensure_trade_init()
    return True


def _ensure_trade_init() -> Optional[int]:
    win32com_client = _safe_import_win32()
    if win32com_client is None:
        raise RuntimeError("pywin32 import failed")
    trade = win32com_client.Dispatch("CpTrade.CpTdUtil")
    ret = trade.TradeInit(0)
    if ret not in (0, None):
        raise RuntimeError(f"TradeInit failed with ret={ret}")
    return ret

