# safety/emergency_exit.py — 전 포지션 즉시 시장가 청산
"""
EmergencyExit: Circuit Breaker / KillSwitch 발동 시 전 포지션 강제 청산.

처리 순서:
  1. PositionTracker에서 현재 포지션 확인
  2. pending_registrar 콜백으로 EXIT_FULL pending 등록 (Chejan 추적용)
  3. OrderManager를 통해 시장가 청산 주문 전송
  4. 최대 3회 재시도 (10초 간격)
  5. 성공/실패 로그 기록 + 알림 발송
"""
import logging
import time
from typing import Callable, Optional

from utils.notify import notify_force_exit

logger = logging.getLogger("SYSTEM")


class EmergencyExit:
    """전 포지션 즉시 시장가 청산."""

    MAX_RETRY       = 3
    RETRY_INTERVAL  = 10  # 초

    def __init__(self, position_tracker=None, order_manager=None, pending_registrar=None):
        """
        Args:
            position_tracker:  PositionTracker 인스턴스 (포지션 조회)
            order_manager:     OrderManager 인스턴스 (주문 실행)
            pending_registrar: _set_pending_order 콜백 — 비상 청산 주문을 pending에 등록해
                               Chejan 체결이 '외부체결'로 오분류되지 않도록 함
        """
        self._position_tracker  = position_tracker
        self._order_manager     = order_manager
        self._pending_registrar: Optional[Callable] = pending_registrar
        self._executed: bool    = False
        self._futures_code: str = ""

    # ── 공개 인터페이스 ────────────────────────────────────────

    def execute(self) -> bool:
        """
        전 포지션 시장가 청산 실행.

        Returns:
            bool: 청산 성공(또는 포지션 없음) 여부
        """
        if self._executed:
            logger.warning("[EmergencyExit] 이미 실행됨 — 중복 호출 무시")
            return True

        logger.critical("[EmergencyExit] ★★★ 비상 청산 시작 ★★★")

        position = self._get_position()
        if position is None or position.get("qty", 0) == 0:
            logger.info("[EmergencyExit] 청산할 포지션 없음")
            self._executed = True
            return True

        side   = position.get("side", "FLAT")   # "LONG" | "SHORT"
        qty    = abs(int(position.get("qty", 0)))
        code   = position.get("code", "")
        avg_px = float(position.get("avg_price", 0.0))

        order_side = "SELL" if side == "LONG" else "BUY"
        logger.critical(
            "[EmergencyExit] %s %d계약 시장가 %s 청산 (종목: %s)",
            side, qty, order_side, code,
        )

        # Chejan 체결이 '외부체결(HTS/수동)'로 오분류되지 않도록 pending 선등록
        if self._pending_registrar is not None:
            try:
                self._pending_registrar(
                    kind="EXIT_FULL",
                    direction=side,
                    qty=qty,
                    price_hint=avg_px,
                    reason="CB 비상청산",
                )
            except Exception:
                logger.exception("[EmergencyExit] pending 등록 실패 — 계속 진행")

        for attempt in range(1, self.MAX_RETRY + 1):
            success = self._send_market_order(code, order_side, qty)
            if success:
                logger.critical(
                    "[EmergencyExit] 청산 주문 성공 (시도 %d/%d)",
                    attempt, self.MAX_RETRY,
                )
                notify_force_exit("비상 청산", 0.0)
                self._executed = True
                return True

            logger.error(
                "[EmergencyExit] 청산 주문 실패 (시도 %d/%d) — %d초 후 재시도",
                attempt, self.MAX_RETRY, self.RETRY_INTERVAL,
            )
            if attempt < self.MAX_RETRY:
                time.sleep(self.RETRY_INTERVAL)

        logger.critical("[EmergencyExit] ★★★ 비상 청산 %d회 실패 — 수동 청산 필요 ★★★", self.MAX_RETRY)
        return False

    # ── 의존성 설정 (늦은 바인딩) ────────────────────────────────

    def set_position_tracker(self, tracker) -> None:
        self._position_tracker = tracker

    def set_order_manager(self, manager) -> None:
        self._order_manager = manager

    def set_pending_registrar(self, registrar: Callable) -> None:
        """_set_pending_order 콜백 설정 (늦은 바인딩)."""
        self._pending_registrar = registrar

    def set_futures_code(self, code: str) -> None:
        """청산 주문에 사용할 선물 종목 코드 설정."""
        self._futures_code = code

    def reset(self):
        """장 시작 시 일간 리셋."""
        self._executed = False
        logger.info("[EmergencyExit] 리셋 완료")

    @property
    def is_executed(self) -> bool:
        return self._executed

    # ── 내부 헬퍼 ─────────────────────────────────────────────

    def _get_position(self) -> Optional[dict]:
        if self._position_tracker is None:
            logger.warning("[EmergencyExit] PositionTracker 미설정 — 포지션 조회 불가")
            return None
        try:
            pt = self._position_tracker
            return {
                "side":      pt.status,
                "qty":       pt.quantity,
                "avg_price": pt.entry_price,
                "code":      self._futures_code,
            }
        except Exception:
            logger.exception("[EmergencyExit] 포지션 조회 오류")
            return None

    def _send_market_order(self, code: str, order_side: str, qty: int) -> bool:
        if self._order_manager is None:
            # 시뮬레이션 모드: OrderManager 없어도 성공 처리
            logger.info("[EmergencyExit] OrderManager 미설정 — 시뮬레이션 청산")
            return True
        try:
            result = self._order_manager.send_market_order(
                code=code,
                side=order_side,
                qty=qty,
                reason="EMERGENCY_EXIT",
            )
            return result is not None
        except Exception:
            logger.exception("[EmergencyExit] 시장가 주문 전송 오류")
            return False
