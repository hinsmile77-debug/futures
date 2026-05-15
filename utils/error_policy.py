from __future__ import annotations

import datetime
import logging
from enum import Enum
from typing import Any


class ErrorLevel(str, Enum):
    RECOVERABLE = "recoverable"
    DEGRADED = "degraded"
    FATAL = "fatal"


def classify_exception(exc: Exception, default: ErrorLevel = ErrorLevel.RECOVERABLE) -> ErrorLevel:
    if isinstance(exc, (MemoryError, SystemError, OSError)):
        return ErrorLevel.FATAL
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return ErrorLevel.DEGRADED
    return default


def apply_error_policy(
    *,
    system: Any,
    level: ErrorLevel,
    context: str,
    exc: Exception,
    logger: logging.Logger,
    dashboard_logger: Any = None,
) -> None:
    if level == ErrorLevel.RECOVERABLE:
        logger.warning("[ERR-RECOVERABLE] %s: %s", context, exc)
        if dashboard_logger is not None:
            dashboard_logger(f"[ERR-RECOVERABLE] {context}: {exc}", "WARNING")
        return

    if level == ErrorLevel.DEGRADED:
        logger.warning("[ERR-DEGRADED] %s: %s", context, exc)
        if dashboard_logger is not None:
            dashboard_logger(f"[ERR-DEGRADED] {context}: {exc}", "WARNING")
        return

    # FATAL: 신규 진입을 즉시 차단하고 쿨다운을 건다.
    logger.error("[ERR-FATAL] %s: %s", context, exc)
    try:
        system._auto_entry_enabled = False
        system._entry_cooldown_until = datetime.datetime.now() + datetime.timedelta(minutes=15)
        system._last_block_reason = f"fatal:{context}"
    except Exception:
        pass

    if dashboard_logger is not None:
        dashboard_logger(
            f"[ERR-FATAL] {context}: {exc} | 자동진입 OFF + 15분 쿨다운",
            "CRITICAL",
        )
