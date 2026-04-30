# utils/notify.py — Slack 알림 발송
"""
Slack Bot API (#maitreya 채널) 로 중요 이벤트를 비동기 발송한다.
PC 출처 [MW0601] 가 모든 메시지에 자동 첨부된다.

토큰·채널·PC명은 config/settings.py 또는 환경변수로 관리한다.
"""
import datetime
import logging

from config.settings import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SLACK_PC_NAME
from utils.slack_queue import get_slack_queue

logger = logging.getLogger("SYSTEM")

_PREFIX = f"[{SLACK_PC_NAME}]" if SLACK_PC_NAME else ""


# ── 내부 전송 ─────────────────────────────────────────────────

def _send(message: str, channel: str = None) -> None:
    """Slack 큐에 메시지 추가 (비동기, 워커 스레드가 순차 처리)."""
    try:
        q = get_slack_queue(token=SLACK_BOT_TOKEN, default_channel=SLACK_CHANNEL_ID)
        full = f"{_PREFIX} {message}" if _PREFIX else message
        q.enqueue(full, channel=channel)
    except Exception as e:
        logger.warning("[Notify] Slack 큐 추가 실패: %s", e)


# ── 공개 API ──────────────────────────────────────────────────

def notify(message: str, level: str = "INFO") -> None:
    """
    이벤트 알림 발송.

    Parameters
    ----------
    message : 알림 본문
    level   : "INFO" | "WARNING" | "CRITICAL"
    """
    ts       = datetime.datetime.now().strftime("%H:%M:%S")
    icon     = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}.get(level, "")
    full_msg = f"{icon} [{ts}] [미륵이] {message}"
    logger.info("[Notify] %s", full_msg)
    _send(full_msg)


def notify_circuit_breaker(trigger: str, action: str) -> None:
    notify(
        f"Circuit Breaker 발동!\n트리거: {trigger}\n조치: {action}",
        "CRITICAL",
    )


def notify_order(side: str, quantity: int, price: float, order_id: str = "") -> None:
    """주문 제출 알림"""
    oid = f" (주문번호: {order_id})" if order_id else ""
    notify(
        f"주문{oid}\n방향: {side}  수량: {quantity}계약  가격: {price:,.2f}",
        "INFO",
    )


def notify_execution(side: str, quantity: int, price: float, pnl_krw: float = None) -> None:
    """체결 알림"""
    pnl_str = f"\n손익: {pnl_krw:+,.0f}원" if pnl_krw is not None else ""
    notify(
        f"체결\n방향: {side}  수량: {quantity}계약  가격: {price:,.2f}{pnl_str}",
        "INFO",
    )


def notify_force_exit(reason: str, pnl_krw: float) -> None:
    sign = "+" if pnl_krw >= 0 else ""
    notify(
        f"강제 청산 실행\n사유: {reason}\n손익: {sign}{pnl_krw:,.0f}원",
        "WARNING",
    )


def notify_daily_summary(win: int, lose: int, total_pnl: float) -> None:
    notify(
        f"일일 마감 리포트\n승: {win}회 / 패: {lose}회\n총 손익: {total_pnl:+,.0f}원",
        "INFO",
    )
