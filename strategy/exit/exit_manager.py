# strategy/exit/exit_manager.py — 청산 통합 관리자
"""
청산 결정의 최종 관문 — 아래 조건들을 매 분봉 점검

청산 트리거 우선순위:
  P1 (최우선)  — 15:10 강제 청산 (오버나이트 절대 금지)
  P2           — 손절가 도달 (하드 스톱)
  P3           — 1차 목표가 도달 (부분 청산 33%)
  P4           — 2차 목표가 도달 (부분 청산 33%)
  P5           — 트레일링 스톱 업데이트 + 트레일 히트
  P6           — Circuit Breaker 긴급 청산 (외부 호출)

각 트리거는 독립적으로 점검 → 최고 우선순위 트리거 실행
"""
import datetime
import logging
from typing import Optional, Dict, TYPE_CHECKING

from config import secrets as _secrets

from config.constants import (
    POSITION_LONG, POSITION_SHORT, POSITION_FLAT,
    FUTURES_PT_VALUE,
)
FUTURES_MULTIPLIER = FUTURES_PT_VALUE   # 하위 호환 alias
from config.settings import PARTIAL_EXIT_RATIOS

from strategy.exit.time_exit import TimeExitManager

if TYPE_CHECKING:
    from strategy.position.position_tracker import PositionTracker
    from collection.broker.base import BrokerAPI

logger = logging.getLogger("TRADE")


class ExitManager:
    """
    청산 통합 관리자

    main.py의 run_minute_pipeline()에서 매 분봉 호출:
        result = exit_manager.check_and_exit(price, atr, now)
    """

    def __init__(
        self,
        position_tracker,   # PositionTracker
        kiwoom_api=None,    # KiwoomAPI (None = 시뮬레이션)
    ):
        self._tracker   = position_tracker
        self._api       = kiwoom_api
        self._time_exit = TimeExitManager()

        # 부분 청산 상태
        self._partial1_done = False
        self._partial2_done = False

        # 일일 청산 통계
        self._daily_exits: list = []

    # ── 매 분봉 메인 호출 ─────────────────────────────────────────
    def check_and_exit(
        self,
        price: float,
        atr:   float,
        now:   Optional[datetime.datetime] = None,
    ) -> Optional[Dict]:
        """
        청산 조건 점검 — 해당 시 청산 실행 및 결과 반환

        Args:
            price: 현재가 (분봉 종가)
            atr:   현재 ATR
            now:   기준 시각

        Returns:
            청산 결과 딕셔너리 or None (청산 없음)
        """
        if now is None:
            now = datetime.datetime.now()

        if self._tracker.status == POSITION_FLAT:
            return None

        # ─ P1. 15:10 강제 청산 ───────────────────────────────────
        if self._time_exit.should_force_exit(now):
            return self._execute_exit(price, reason="15:10 강제청산", priority=1)

        # ─ P2. 하드 스톱 ─────────────────────────────────────────
        if self._tracker.is_stop_hit(price):
            return self._execute_exit(price, reason="손절", priority=2)

        # ─ P3. 1차 목표가 (부분 청산) ────────────────────────────
        if self._tracker.is_tp1_hit(price):
            return self._execute_partial_exit(price, stage=1)

        # ─ P4. 2차 목표가 (부분 청산) ────────────────────────────
        if self._tracker.is_tp2_hit(price):
            return self._execute_partial_exit(price, stage=2)

        # ─ P5. 트레일링 스톱 업데이트 + 히트 ─────────────────────
        self._tracker.update_trailing_stop(price, atr)
        if self._tracker.is_stop_hit(price):
            return self._execute_exit(price, reason="트레일링스톱", priority=5)

        return None

    # ── P6. 외부 긴급 청산 (CB·KillSwitch 호출용) ────────────────
    def force_exit(self, price: float, reason: str = "긴급청산") -> Optional[Dict]:
        """
        Circuit Breaker / KillSwitch에서 직접 호출
        포지션 없으면 None 반환
        """
        if self._tracker.status == POSITION_FLAT:
            return None
        return self._execute_exit(price, reason=reason, priority=0)

    # ── 전량 청산 실행 ────────────────────────────────────────────
    def _execute_exit(self, price: float, reason: str, priority: int) -> Dict:
        direction = self._tracker.status
        qty       = self._tracker.quantity

        order_result = self._send_close_order(direction, qty, price)
        if not order_result.get("ok"):
            logger.error(f"[Exit] 청산 주문 실패: {order_result.get('error')}")

        result     = self._tracker.close_position(exit_price=price, reason=reason)
        self._partial1_done = False
        self._partial2_done = False

        exit_record = {
            **result,
            "priority":   priority,
            "exit_reason": reason,
        }
        self._daily_exits.append(exit_record)

        logger.info(
            f"[Exit] 🔴 전량청산 | {direction} {qty}계약 @ {price:.2f} "
            f"| {reason} | PnL={result.get('pnl_pts', 0):+.2f}pt"
        )
        return exit_record

    # ── 부분 청산 실행 ────────────────────────────────────────────
    def _execute_partial_exit(self, price: float, stage: int) -> Optional[Dict]:
        """
        1차/2차 목표가 부분 청산 (각 33%)

        남은 33%는 트레일링 스톱으로 관리
        """
        total_qty = self._tracker.quantity
        partial_ratio = PARTIAL_EXIT_RATIOS[stage - 1] if stage <= len(PARTIAL_EXIT_RATIOS) else 0.33
        partial_qty   = max(1, round(total_qty * partial_ratio))

        if stage == 1 and self._partial1_done:
            return None
        if stage == 2 and self._partial2_done:
            return None
        if partial_qty >= total_qty:
            # 전량 청산으로 처리
            return self._execute_exit(price, reason=f"TP{stage}(전량)", priority=3 if stage == 1 else 4)

        direction = self._tracker.status
        order_result = self._send_close_order(direction, partial_qty, price)
        if not order_result.get("ok"):
            return None

        mult = 1 if direction == POSITION_LONG else -1
        pnl_pts = (price - self._tracker.entry_price) * mult * partial_qty

        # 포지션 수량 감소
        self._tracker.quantity -= partial_qty

        if stage == 1:
            self._tracker.partial_1_done = True
            self._partial1_done          = True
        else:
            self._tracker.partial_2_done = True
            self._partial2_done          = True

        result = {
            "action":      f"PARTIAL_EXIT_TP{stage}",
            "direction":   direction,
            "qty":         partial_qty,
            "remaining":   self._tracker.quantity,
            "price":       price,
            "pnl_pts":     round(pnl_pts, 4),
            "pnl_krw":     round(pnl_pts * FUTURES_MULTIPLIER, 0),
            "exit_reason": f"TP{stage} 부분청산 {partial_ratio:.0%}",
        }
        logger.info(
            f"[Exit] 🟡 TP{stage} 부분청산 {partial_qty}계약 @ {price:.2f} "
            f"| 잔여={self._tracker.quantity}계약 | PnL={pnl_pts:+.2f}pt"
        )
        self._daily_exits.append(result)
        return result

    # ── 주문 전송 ─────────────────────────────────────────────────
    def _send_close_order(self, direction: str, qty: int, price: float) -> dict:
        if self._api is None:
            logger.info(f"[Exit] [SIM] 청산주문: {direction} {qty}계약 @ {price:.2f}")
            return {"ok": True, "order_no": "SIM-CLOSE-0000"}

        try:
            order_type = 2 if direction == POSITION_LONG else 1  # 2=매도, 1=매수
            order_no   = self._api.send_order(
                rqname     = "청산",
                screen_no  = "1001",
                acc_no     = _secrets.ACCOUNT_NO,
                order_type = order_type,
                code       = "101Q9000",
                qty        = qty,
                price      = 0,
                hoga_gb    = "03",
                org_order  = "",
            )
            return {"ok": True, "order_no": order_no}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── 일일 리셋 및 통계 ─────────────────────────────────────────
    def reset_daily(self):
        self._partial1_done = False
        self._partial2_done = False
        self._daily_exits.clear()

    def get_daily_stats(self) -> dict:
        pnl_sum = sum(e.get("pnl_pts", 0) for e in self._daily_exits)
        wins    = sum(1 for e in self._daily_exits if e.get("pnl_pts", 0) > 0)
        exits   = len(self._daily_exits)
        return {
            "exit_count": exits,
            "wins":       wins,
            "win_rate":   round(wins / max(exits, 1), 3),
            "total_pnl_pts": round(pnl_sum, 4),
            "total_pnl_krw": round(pnl_sum * FUTURES_MULTIPLIER, 0),
            "exit_reasons": [e.get("exit_reason") for e in self._daily_exits],
        }
