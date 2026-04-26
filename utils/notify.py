# utils/notify.py — 알림 발송 (카카오 알림톡)
"""
카카오 알림톡 API를 통해 중요 이벤트 알림을 발송합니다.
KAKAO_TOKEN이 설정되지 않으면 로그만 기록합니다.
"""
import requests
import logging

from config.settings import KAKAO_TOKEN

logger = logging.getLogger("SYSTEM")

KAKAO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


def _send_kakao(message: str) -> bool:
    if not KAKAO_TOKEN:
        return False
    try:
        payload = {
            "object_type": "text",
            "text": message,
            "link": {"web_url": "", "mobile_web_url": ""},
        }
        resp = requests.post(
            KAKAO_URL,
            headers={"Authorization": f"Bearer {KAKAO_TOKEN}"},
            json={"template_object": payload},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception as e:
        logger.warning(f"[Notify] 카카오 전송 실패: {e}")
        return False


def notify(message: str, level: str = "INFO"):
    """
    알림 발송
    level: INFO | WARNING | CRITICAL
    """
    icon = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}.get(level, "")
    full_msg = f"{icon} [미륵이] {message}"

    logger.info(f"[Notify] {full_msg}")
    _send_kakao(full_msg)


def notify_circuit_breaker(trigger: str, action: str):
    notify(f"Circuit Breaker 발동!\n트리거: {trigger}\n조치: {action}", "CRITICAL")


def notify_force_exit(reason: str, pnl_krw: float):
    sign = "+" if pnl_krw >= 0 else ""
    notify(
        f"강제 청산 실행\n사유: {reason}\n손익: {sign}{pnl_krw:,.0f}원",
        "WARNING",
    )


def notify_daily_summary(win: int, lose: int, total_pnl: float):
    notify(
        f"일일 마감 리포트\n승: {win}회 / 패: {lose}회\n"
        f"총 손익: {total_pnl:+,.0f}원",
        "INFO",
    )
