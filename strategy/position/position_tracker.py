# strategy/position/position_tracker.py — 현재 포지션 상태 추적
"""
실시간 포지션 상태를 관리합니다.
진입 → 보유 → 청산의 전체 생명주기를 추적.
"""
import datetime
import logging
from typing import Optional, Dict

from config.constants import POSITION_LONG, POSITION_SHORT, POSITION_FLAT
from config.settings import ATR_STOP_MULT, ATR_TP1_MULT, ATR_TP2_MULT

logger = logging.getLogger("TRADE")


class PositionTracker:
    """단일 포지션 상태 관리"""

    def __init__(self):
        self.status:       str   = POSITION_FLAT
        self.entry_price:  float = 0.0
        self.quantity:     int   = 0
        self.entry_time:   Optional[datetime.datetime] = None
        self.grade:        str   = ""
        self.regime:       str   = ""

        self.stop_price:   float = 0.0
        self.tp1_price:    float = 0.0
        self.tp2_price:    float = 0.0

        self.partial_1_done: bool = False
        self.partial_2_done: bool = False

        self._daily_pnl_pts: float = 0.0
        self._daily_trades:  int   = 0
        self._daily_wins:    int   = 0

    def open_position(
        self,
        direction: str,
        price: float,
        quantity: int,
        atr: float,
        grade: str = "B",
        regime: str = "NEUTRAL",
    ):
        """
        포지션 진입

        Args:
            direction: LONG | SHORT
            price:     진입가
            quantity:  계약 수
            atr:       현재 ATR (손절/목표 계산)
            grade:     진입 등급 (A/B/C)
            regime:    매크로 레짐
        """
        assert direction in (POSITION_LONG, POSITION_SHORT), f"Invalid direction: {direction}"
        assert self.status == POSITION_FLAT, "이미 포지션 보유 중"

        self.status      = direction
        self.entry_price = price
        self.quantity    = quantity
        self.entry_time  = datetime.datetime.now()
        self.grade       = grade
        self.regime      = regime

        mult = 1 if direction == POSITION_LONG else -1
        self.stop_price = price - mult * atr * ATR_STOP_MULT
        self.tp1_price  = price + mult * atr * ATR_TP1_MULT
        self.tp2_price  = price + mult * atr * ATR_TP2_MULT

        self.partial_1_done = False
        self.partial_2_done = False

        logger.info(
            f"[Position] 진입 {direction} {quantity}계약 @ {price} "
            f"| 손절={self.stop_price:.2f} 1차={self.tp1_price:.2f} 2차={self.tp2_price:.2f}"
        )

    def close_position(self, exit_price: float, reason: str) -> Dict:
        """포지션 청산 후 손익 반환"""
        assert self.status != POSITION_FLAT, "포지션 없음"

        mult = 1 if self.status == POSITION_LONG else -1
        pnl_pts = (exit_price - self.entry_price) * mult
        pnl_krw = pnl_pts * 500_000 * self.quantity   # 선물 1pt = 500,000원

        self._daily_pnl_pts += pnl_pts * self.quantity
        self._daily_trades  += 1
        if pnl_pts > 0:
            self._daily_wins += 1

        result = {
            "direction":   self.status,
            "entry_price": self.entry_price,
            "exit_price":  exit_price,
            "quantity":    self.quantity,
            "pnl_pts":     round(pnl_pts, 4),
            "pnl_krw":     round(pnl_krw, 0),
            "exit_reason": reason,
            "hold_minutes": self._hold_minutes(),
        }

        logger.info(
            f"[Position] 청산 {self.status} @ {exit_price} "
            f"| PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) | {reason}"
        )

        # 초기화
        self.status      = POSITION_FLAT
        self.entry_price = 0.0
        self.quantity    = 0
        self.entry_time  = None
        return result

    def update_trailing_stop(self, current_price: float, atr: float):
        """트레일링 스톱 업데이트"""
        if self.status == POSITION_FLAT:
            return

        mult = 1 if self.status == POSITION_LONG else -1
        unrealized_pts = (current_price - self.entry_price) * mult

        if unrealized_pts >= atr * 2.0:
            # 2ATR 이상 수익 → 최고점 추적 (1ATR 간격)
            new_stop = current_price - mult * atr
            if mult * (new_stop - self.stop_price) > 0:
                self.stop_price = new_stop
        elif unrealized_pts >= atr * 1.5:
            # 1.5ATR 이상 → +0.5ATR 보장
            new_stop = self.entry_price + mult * atr * 0.5
            if mult * (new_stop - self.stop_price) > 0:
                self.stop_price = new_stop
        elif unrealized_pts >= atr * 1.0:
            # 1ATR 이상 → 본전 손절
            new_stop = self.entry_price
            if mult * (new_stop - self.stop_price) > 0:
                self.stop_price = new_stop

    def is_stop_hit(self, price: float) -> bool:
        if self.status == POSITION_FLAT:
            return False
        if self.status == POSITION_LONG:
            return price <= self.stop_price
        return price >= self.stop_price

    def is_tp1_hit(self, price: float) -> bool:
        if self.status == POSITION_FLAT or self.partial_1_done:
            return False
        if self.status == POSITION_LONG:
            return price >= self.tp1_price
        return price <= self.tp1_price

    def is_tp2_hit(self, price: float) -> bool:
        if self.status == POSITION_FLAT or self.partial_2_done:
            return False
        if self.status == POSITION_LONG:
            return price >= self.tp2_price
        return price <= self.tp2_price

    def unrealized_pnl_pts(self, current_price: float) -> float:
        if self.status == POSITION_FLAT:
            return 0.0
        mult = 1 if self.status == POSITION_LONG else -1
        return (current_price - self.entry_price) * mult * self.quantity

    def _hold_minutes(self) -> int:
        if not self.entry_time:
            return 0
        delta = datetime.datetime.now() - self.entry_time
        return int(delta.total_seconds() // 60)

    # ── 일일 통계 ──────────────────────────────────────────────
    def daily_stats(self) -> dict:
        return {
            "trades":   self._daily_trades,
            "wins":     self._daily_wins,
            "losses":   self._daily_trades - self._daily_wins,
            "win_rate": self._daily_wins / max(self._daily_trades, 1),
            "pnl_pts":  round(self._daily_pnl_pts, 4),
            "pnl_krw":  round(self._daily_pnl_pts * 500_000, 0),
        }

    def reset_daily(self):
        self._daily_pnl_pts = 0.0
        self._daily_trades  = 0
        self._daily_wins    = 0
