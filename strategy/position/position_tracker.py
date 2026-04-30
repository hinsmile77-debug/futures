# strategy/position/position_tracker.py — 현재 포지션 상태 추적
"""
실시간 포지션 상태를 관리합니다.
진입 → 보유 → 청산의 전체 생명주기를 추적.
"""
import datetime
import json
import logging
import os
from typing import Optional, Dict

from config.constants import POSITION_LONG, POSITION_SHORT, POSITION_FLAT
from config.settings import ATR_STOP_MULT, ATR_TP1_MULT, ATR_TP2_MULT

logger = logging.getLogger("TRADE")

_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "position_state.json",
)


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
        self._save_state()

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

        entry_ts_str = (
            self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.entry_time else ""
        )
        result = {
            "direction":    self.status,
            "entry_price":  self.entry_price,
            "exit_price":   exit_price,
            "quantity":     self.quantity,
            "pnl_pts":      round(pnl_pts, 4),
            "pnl_krw":      round(pnl_krw, 0),
            "exit_reason":  reason,
            "hold_minutes": self._hold_minutes(),
            "entry_ts":     entry_ts_str,
            "grade":        self.grade,
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
        self._save_state()
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

    def restore_daily_stats(self, rows) -> None:
        """재시작 시 trades.db 당일 행으로 일일 통계 복원.

        trades.db 컬럼: pnl_pts(계약당), quantity, pnl_krw(합계)
        close_position()과 동일한 집계 방식 사용.
        """
        for row in rows:
            pnl_pts = float(row["pnl_pts"] or 0.0)
            qty     = int(row["quantity"] or 1)
            self._daily_pnl_pts += pnl_pts * qty
            self._daily_trades  += 1
            if pnl_pts > 0:
                self._daily_wins += 1

    def reset_daily(self):
        self._daily_pnl_pts = 0.0
        self._daily_trades  = 0
        self._daily_wins    = 0

    # ── 포지션 상태 퍼시스턴스 ────────────────────────────────────

    def _save_state(self) -> None:
        """포지션 상태를 JSON 파일에 저장 — 재시작 시 복원용."""
        try:
            state = {
                "status":       self.status,
                "entry_price":  self.entry_price,
                "quantity":     self.quantity,
                "entry_time":   (self.entry_time.isoformat()
                                 if self.entry_time else None),
                "grade":        self.grade,
                "regime":       self.regime,
                "stop_price":   self.stop_price,
                "tp1_price":    self.tp1_price,
                "tp2_price":    self.tp2_price,
                "partial_1_done": self.partial_1_done,
                "partial_2_done": self.partial_2_done,
                "saved_at":     datetime.datetime.now().isoformat(),
            }
            os.makedirs(os.path.dirname(_STATE_FILE), exist_ok=True)
            with open(_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"[Position] 상태 저장 실패: {e}")

    def load_state(self) -> bool:
        """저장된 포지션 상태 복원. 반환값: 복원 성공 여부."""
        if not os.path.exists(_STATE_FILE):
            return False
        try:
            with open(_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)

            # 당일 데이터만 복원 (날짜 다르면 무시)
            saved_at = datetime.datetime.fromisoformat(state.get("saved_at", ""))
            if saved_at.date() != datetime.date.today():
                logger.info("[Position] 저장 상태가 어제 데이터 — 무시")
                return False

            # FLAT이면 복원 불필요
            if state.get("status") == POSITION_FLAT:
                return False

            self.status      = state["status"]
            self.entry_price = float(state["entry_price"])
            self.quantity    = int(state["quantity"])
            self.entry_time  = (datetime.datetime.fromisoformat(state["entry_time"])
                                if state.get("entry_time") else None)
            self.grade        = state.get("grade", "")
            self.regime       = state.get("regime", "")
            self.stop_price   = float(state.get("stop_price", 0))
            self.tp1_price    = float(state.get("tp1_price", 0))
            self.tp2_price    = float(state.get("tp2_price", 0))
            self.partial_1_done = bool(state.get("partial_1_done", False))
            self.partial_2_done = bool(state.get("partial_2_done", False))

            logger.warning(
                f"[Position] 이전 포지션 복원: {self.status} {self.quantity}계약 "
                f"@ {self.entry_price} (손절={self.stop_price:.2f})"
            )
            return True
        except Exception as e:
            logger.warning(f"[Position] 상태 복원 실패: {e}")
            return False
