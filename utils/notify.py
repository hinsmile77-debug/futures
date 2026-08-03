# utils/notify.py — Slack 알림 발송
"""
Slack Bot API (#maitreya 채널) 로 중요 이벤트를 비동기 발송한다.
PC 출처 [MW0601] 가 모든 메시지에 자동 첨부된다.

토큰·채널·PC명은 config/settings.py 또는 환경변수로 관리한다.
"""
import datetime
import logging

from config.settings import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SLACK_PC_NAME
from utils.runtime_mode import is_test_mode
from utils.slack_queue import get_slack_queue

logger = logging.getLogger("SYSTEM")

_PREFIX = f"[{SLACK_PC_NAME}]" if SLACK_PC_NAME else ""

# 슬랙 발송 On/Off 전역 플래그 — 대시보드 체크박스로 제어
_SLACK_ENABLED: bool = True


def set_slack_enabled(enabled: bool) -> None:
    """슬랙 알림 활성화 여부 설정 (대시보드 체크박스 연동)."""
    global _SLACK_ENABLED
    _SLACK_ENABLED = bool(enabled)
    logger.info("[Notify] 슬랙 알림 %s", "활성화" if _SLACK_ENABLED else "비활성화")


def is_slack_enabled() -> bool:
    return _SLACK_ENABLED


# ── 내부 전송 ─────────────────────────────────────────────────

def _send(message: str, channel: str = None) -> None:
    """Slack 큐에 메시지 추가 (비동기, 워커 스레드가 순차 처리)."""
    if not _SLACK_ENABLED:
        return
    # [MW0601 422차] 테스트 실행이 실제 Slack 큐에 적재하지 않도록 차단.
    # 08-03 장전 CB 허위 알림 30건의 세 번째 오염 경로였다
    # (나머지 둘은 utils/logger.py:setup_logging()에서 차단).
    # 명시적 opt-in(MIREUK_TEST_MODE)만 인정 — utils/runtime_mode.py 참조.
    if is_test_mode():
        return
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


# ── 시동 / 장전 / 첫 틱 / 장애 알림 ──────────────────────────────

def notify_startup(code: str, server_label: str) -> None:
    """connect_broker 성공 직후 — 기동 완료 확인."""
    notify(
        f"미륵이 기동 완료\n종목: {code} | 서버: {server_label}\n09:00 장 시작 대기 중",
        "INFO",
    )


def notify_premarket_ready(regime: str, code: str) -> None:
    """08:55 pre_market_setup + 실시간 구독 완료 — 09:00 준비 완료."""
    notify(
        f"장전 준비 완료 ✅\n레짐: {regime} | 종목: {code}\n실시간 구독 활성 — 09:00 첫 틱 대기",
        "INFO",
    )


def notify_first_tick(candle: dict) -> None:
    """09:00 이후 첫 분봉 완성 수신 — 정상 작동 확인."""
    ts  = candle.get("ts")
    ts_str = ts.strftime("%H:%M") if hasattr(ts, "strftime") else str(ts)
    notify(
        f"첫 분봉 수신 ✅ ({ts_str})\n"
        f"O={candle.get('open',0):,.2f}  H={candle.get('high',0):,.2f}  "
        f"L={candle.get('low',0):,.2f}  C={candle.get('close',0):,.2f}  "
        f"V={candle.get('volume',0):,}",
        "INFO",
    )


def notify_broker_sync_blocked(reason: str) -> None:
    """09:00 이후에도 broker sync 미검증 — 신규 진입 차단 지속."""
    notify(
        f"🚨 broker sync 미검증 — 신규 진입 차단 중\n"
        f"사유: {reason}\n"
        f"즉시 대시보드 확인 및 수동 포지션 조회 필요",
        "CRITICAL",
    )


def notify_connection_lost(broker_name: str = "브로커") -> None:
    """API 연결 끊김 — 재연결 시도."""
    notify(
        f"🚨 {broker_name} 연결 끊김 — 재연결 시도 중\n"
        f"포지션 보유 중이면 HTS에서 수동 확인 필요",
        "CRITICAL",
    )


def notify_pipeline_delayed(elapsed_str: str) -> None:
    """파이프라인 90초 이상 미실행 — 분봉 지연 초기 경고."""
    notify(
        f"⚠ 파이프라인 {elapsed_str} 미실행\n"
        f"분봉 수신 지연 가능성 — 지속 시 자동 복구 예정",
        "WARNING",
    )


# ── SHS / EKS 알림 ────────────────────────────────────────────

def notify_shs_alert(shs: float, components: dict) -> None:
    """SHS < 60 최초 진입 또는 5점 이상 추가 하락 시 경고."""
    restart  = components.get("restart_count", 0)
    z_warn   = components.get("z_warn_count", 0)
    core_pct = components.get("core_pass_rate", 1.0) * 100
    s2_ms    = components.get("s2_latency_sec", 0.0) * 1000
    notify(
        f"🩺 시스템 건강 점수 저하\n"
        f"SHS = {shs:.0f}점  (기준 60점 미만 → 진입 차단)\n"
        f"  재시작: {restart}회  |  z경고 피처: {z_warn}개\n"
        f"  CORE 통과율: {core_pct:.0f}%  |  S2 지연: {s2_ms:.0f}ms",
        "WARNING",
    )


def notify_kill_switch_cleared(scaler_age_h: float, conf_hits: int, conf_window: int) -> None:
    """EKS 자동 해제 — 진입 재개."""
    notify(
        f"✅ Early Kill Switch 해제 — 장중 진입 재개\n"
        f"스케일러 age: {scaler_age_h:.1f}h  conf 임계 초과: {conf_hits}/{conf_window}봉\n"
        f"자동매매 정상화",
        "INFO",
    )


def notify_kill_switch(gap_open_conf_max: float, gap_open_bars: int) -> None:
    """Early Kill Switch 발동 — 일시 관망 (자동 회복 평가 중)."""
    notify(
        f"🚫 Early Kill Switch 발동 — 일시 관망\n"
        f"GAP_OPEN 구간({gap_open_bars}봉) 최대 conf: {gap_open_conf_max * 100:.1f}%\n"
        f"CORE 피처 전 구간 탈락 → 신뢰 진입 조건 없음\n"
        f"자동 진입 차단 중 (스케일러·conf 회복 시 09:20부터 30분 간격 자동 재개 / 수동 진입은 대시보드 가능)",
        "CRITICAL",
    )
