# strategy/position/position_tracker.py — 현재 포지션 상태 추적
"""
실시간 포지션 상태를 관리합니다.
진입 → 보유 → 청산의 전체 생명주기를 추적.
"""
import datetime
import json
import logging
import os
from typing import Optional, Dict, Tuple

from utils.time_utils import now_kst

from config.constants import POSITION_LONG, POSITION_SHORT, POSITION_FLAT, FUTURES_PT_VALUE
from config.settings import ATR_STOP_MULT, ATR_TP1_MULT, ATR_TP2_MULT, ATR_TP3_MULT, FUTURES_COMMISSION_RATE

# 인스턴스별 pt_value를 주입받기 전 module-level fallback 으로만 사용
def _calc_commission(price: float, quantity: int, pt_value: float = FUTURES_PT_VALUE) -> float:
    """편도 수수료 계산 (왕복은 호출부에서 × 2)"""
    return price * quantity * pt_value * FUTURES_COMMISSION_RATE

logger = logging.getLogger("TRADE")

_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "position_state.json",
)


class PositionTracker:
    """단일 포지션 상태 관리"""

    def __init__(self, pt_value: float = FUTURES_PT_VALUE):
        self._pt_value: float = float(pt_value)
        self.status:       str   = POSITION_FLAT
        self.entry_price:  float = 0.0
        self.quantity:     int   = 0
        self.entry_time:   Optional[datetime.datetime] = None
        self.grade:        str   = ""
        self.regime:       str   = ""
        self.signal_direction: str = ""
        self.reverse_entry_enabled: bool = False

        self.stop_price:   float = 0.0
        self.tp1_price:    float = 0.0
        self.tp2_price:    float = 0.0
        self.tp3_price:    float = 0.0
        self.trailing_anchor_price: float = 0.0

        self.partial_1_done: bool = False
        self.partial_2_done: bool = False
        self.partial_3_done: bool = False
        self.initial_quantity: int = 0

        self._optimistic: bool = False  # True = open_position() called speculatively; Chejan will correct price

        self._daily_pnl_pts:   float = 0.0
        self._daily_trades:    int   = 0
        self._daily_wins:      int   = 0
        self._daily_commission: float = 0.0
        self._daily_forward_pnl_pts: float = 0.0
        self._daily_forward_trades: int = 0
        self._daily_forward_wins: int = 0
        self._daily_forward_commission: float = 0.0
        self.last_update_reason: str = "init"
        self.last_update_ts: Optional[datetime.datetime] = None

        self._futures_code: str = ""          # 현재 거래 종목코드 (connect_broker 후 주입)
        self._loaded_futures_code: str = ""   # load_state() 에서 복원된 저장 코드

    def set_pt_value(self, pt_value: float) -> None:
        """계약 종류 변경 시 pt_value 갱신 (FLAT 상태에서만 유효)."""
        self._pt_value = float(pt_value)

    def set_futures_code(self, code: str) -> None:
        """거래 종목코드 주입 — connect_broker() 완료 후 호출."""
        self._futures_code = str(code or "").strip()

    def force_flat(self, reason: str = "forced") -> None:
        """포지션 강제 초기화 — 코드 불일치 등 비정상 상태 복구용."""
        self.status = POSITION_FLAT
        self.entry_price = 0.0
        self.quantity = 0
        self.entry_time = None
        self.stop_price = 0.0
        self.tp1_price = 0.0
        self.tp2_price = 0.0
        self.tp3_price = 0.0
        self.trailing_anchor_price = 0.0
        self.partial_1_done = False
        self.partial_2_done = False
        self.partial_3_done = False
        self.initial_quantity = 0
        self._optimistic = False
        self.last_update_reason = reason
        self.last_update_ts = now_kst()
        self._save_state()

    def open_position(
        self,
        direction: str,
        price: float,
        quantity: int,
        atr: float,
        grade: str = "B",
        regime: str = "NEUTRAL",
        raw_direction: Optional[str] = None,
        reverse_entry_enabled: bool = False,
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
        self.entry_time  = now_kst()
        self.grade       = grade
        self.regime      = regime
        self.signal_direction = raw_direction or direction
        self.reverse_entry_enabled = bool(reverse_entry_enabled)
        self.initial_quantity = quantity
        self.trailing_anchor_price = price

        mult = 1 if direction == POSITION_LONG else -1
        self.stop_price = price - mult * atr * ATR_STOP_MULT
        self.tp1_price  = price + mult * atr * ATR_TP1_MULT
        self.tp2_price  = price + mult * atr * ATR_TP2_MULT

        self.partial_1_done = False
        self.partial_2_done = False
        self.partial_3_done = False
        self.last_update_reason = f"open_position:{direction}"
        self.last_update_ts = now_kst()

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
        commission = _calc_commission(self.entry_price, self.quantity, self._pt_value) * 2  # 왕복
        pnl_krw = pnl_pts * self._pt_value * self.quantity - commission
        forward_direction = self.signal_direction or self.status
        forward_pnl_pts = self._calc_directional_pnl_pts(forward_direction, exit_price)
        forward_commission = _calc_commission(self.entry_price, self.quantity, self._pt_value) * 2
        forward_pnl_krw = forward_pnl_pts * self._pt_value * self.quantity - forward_commission

        self._daily_pnl_pts += pnl_pts * self.quantity
        self._daily_commission += commission
        self._daily_trades  += 1
        if pnl_pts > 0:
            self._daily_wins += 1
        self._daily_forward_pnl_pts += forward_pnl_pts * self.quantity
        self._daily_forward_commission += forward_commission
        self._daily_forward_trades += 1
        if forward_pnl_pts > 0:
            self._daily_forward_wins += 1

        entry_ts_str = (
            self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.entry_time else ""
        )
        result = {
            "direction":    self.status,
            "executed_direction": self.status,
            "raw_direction": forward_direction,
            "entry_price":  self.entry_price,
            "exit_price":   exit_price,
            "quantity":     self.quantity,
            "pnl_pts":      round(pnl_pts, 4),
            "pnl_krw":      round(pnl_krw, 0),
            "forward_pnl_pts": round(forward_pnl_pts, 4),
            "forward_pnl_krw": round(forward_pnl_krw, 0),
            "commission":   round(commission, 0),
            "forward_commission": round(forward_commission, 0),
            "exit_reason":  reason,
            "hold_minutes": self._hold_minutes(),
            "entry_ts":     entry_ts_str,
            "grade":        self.grade,
            "reverse_entry_enabled": self.reverse_entry_enabled,
        }

        logger.info(
            f"[Position] 청산 {self.status} @ {exit_price} "
            f"| PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) 수수료={commission:,.0f}원 | {reason}"
        )

        # 초기화
        self.last_update_reason = f"close_position:{reason}"
        self.last_update_ts = now_kst()
        self._reset_position()
        return result

    def apply_entry_fill(
        self,
        direction: str,
        price: float,
        quantity: int,
        atr: float,
        grade: str = "B",
        regime: str = "NEUTRAL",
        filled_at: Optional[datetime.datetime] = None,
        raw_direction: Optional[str] = None,
        reverse_entry_enabled: bool = False,
    ) -> Dict:
        """Chejan 체결 기준으로 포지션을 오픈하거나 증액한다."""
        assert direction in (POSITION_LONG, POSITION_SHORT), f"Invalid direction: {direction}"
        assert quantity > 0, f"Invalid fill quantity: {quantity}"

        if self._optimistic and self.status == direction:
            # 투기적 오픈(open_position) 후 Chejan이 실제 체결가로 보정
            self.entry_price = price
            if filled_at:
                self.entry_time = filled_at
            self._optimistic = False
            self.signal_direction = raw_direction or self.signal_direction or direction
            self.reverse_entry_enabled = bool(reverse_entry_enabled or self.reverse_entry_enabled)
            self.trailing_anchor_price = price
            self._recalculate_levels(atr)
            self.last_update_reason = f"apply_entry_fill_correction:{direction}"
            self.last_update_ts = filled_at or now_kst()
            self._save_state()
            logger.info(
                f"[Position] 체결보정 {direction} {quantity}계약 @ {price} "
                f"| 평균={self.entry_price:.2f} 보유={self.quantity}계약"
            )
            return {
                "direction": self.status,
                "fill_price": round(price, 4),
                "filled_qty": quantity,
                "avg_entry_price": round(self.entry_price, 4),
                "position_qty": self.quantity,
                "entry_ts": (
                    self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                    if self.entry_time else ""
                ),
                "grade": self.grade,
                "regime": self.regime,
            }

        if self.status == POSITION_FLAT:
            self.status = direction
            self.entry_price = price
            self.quantity = quantity
            self.initial_quantity = quantity
            self.trailing_anchor_price = price
            self.entry_time = filled_at or now_kst()
            self.grade = grade
            self.regime = regime
            self.signal_direction = raw_direction or direction
            self.reverse_entry_enabled = bool(reverse_entry_enabled)
        else:
            assert self.status == direction, (
                f"Opposite fill mismatch: status={self.status} fill={direction}"
            )
            total_qty = self.quantity + quantity
            self.entry_price = (
                (self.entry_price * self.quantity) + (price * quantity)
            ) / total_qty
            self.quantity = total_qty
            self.initial_quantity = max(int(self.initial_quantity or 0), total_qty)
            self.grade = grade or self.grade
            self.regime = regime or self.regime
            self.signal_direction = raw_direction or self.signal_direction or direction
            self.reverse_entry_enabled = bool(reverse_entry_enabled or self.reverse_entry_enabled)
            if self.entry_time is None:
                self.entry_time = filled_at or now_kst()

        self._recalculate_levels(atr)
        self.partial_1_done = False
        self.partial_2_done = False
        self.partial_3_done = False
        self.last_update_reason = f"apply_entry_fill:{direction}"
        self.last_update_ts = filled_at or now_kst()
        self._save_state()

        logger.info(
            f"[Position] 체결진입 {direction} {quantity}계약 @ {price} "
            f"| 평균={self.entry_price:.2f} 보유={self.quantity}계약"
        )
        return {
            "direction": self.status,
            "fill_price": round(price, 4),
            "filled_qty": quantity,
            "avg_entry_price": round(self.entry_price, 4),
            "position_qty": self.quantity,
            "entry_ts": (
                self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                if self.entry_time else ""
            ),
            "grade": self.grade,
            "regime": self.regime,
        }

    def apply_exit_fill(
        self,
        exit_price: float,
        quantity: int,
        reason: str,
        filled_at: Optional[datetime.datetime] = None,
    ) -> Dict:
        """Chejan 체결 기준으로 포지션을 부분/전량 청산한다."""
        assert self.status != POSITION_FLAT, "포지션 없음"
        assert 0 < quantity <= self.quantity, (
            f"Invalid exit fill quantity: fill={quantity} total={self.quantity}"
        )

        mult = 1 if self.status == POSITION_LONG else -1
        pnl_pts = (exit_price - self.entry_price) * mult
        commission = _calc_commission(self.entry_price, quantity, self._pt_value) * 2  # 왕복
        pnl_krw = pnl_pts * self._pt_value * quantity - commission
        forward_direction = self.signal_direction or self.status
        forward_pnl_pts = self._calc_directional_pnl_pts(forward_direction, exit_price)
        forward_commission = _calc_commission(self.entry_price, quantity, self._pt_value) * 2
        forward_pnl_krw = forward_pnl_pts * self._pt_value * quantity - forward_commission
        self._daily_pnl_pts += pnl_pts * quantity
        self._daily_commission += commission
        self._daily_forward_pnl_pts += forward_pnl_pts * quantity
        self._daily_forward_commission += forward_commission

        is_final = quantity == self.quantity
        if is_final:
            self._daily_trades += 1
            if pnl_pts > 0:
                self._daily_wins += 1
            self._daily_forward_trades += 1
            if forward_pnl_pts > 0:
                self._daily_forward_wins += 1

        result = self._build_exit_result(
            exit_price=exit_price,
            quantity=quantity,
            pnl_pts=pnl_pts,
            pnl_krw=pnl_krw,
            reason=reason,
            filled_at=filled_at,
        )
        result["forward_pnl_pts"] = round(forward_pnl_pts, 4)
        result["forward_pnl_krw"] = round(forward_pnl_krw, 0)
        result["forward_commission"] = round(forward_commission, 0)

        if is_final:
            logger.info(
                f"[Position] 체결청산 {self.status} @ {exit_price} "
                f"| PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) | {reason}"
            )
            self.last_update_reason = f"apply_exit_fill_final:{reason}"
            self.last_update_ts = filled_at or now_kst()
            self._reset_position()
        else:
            self.quantity -= quantity
            self._sync_partial_progress()
            self.last_update_reason = f"apply_exit_fill_partial:{reason}"
            self.last_update_ts = filled_at or now_kst()
            self._save_state()
            result["remaining"] = self.quantity
            logger.info(
                f"[Position] 체결부분청산 {quantity}계약 @ {exit_price} "
                f"| 잔여={self.quantity}계약 | PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) | {reason}"
            )

        return result

    def sync_from_broker(
        self,
        direction: str,
        price: float,
        quantity: int,
        atr: float,
        *,
        synced_at: Optional[datetime.datetime] = None,
        grade: str = "BROKER",
        regime: str = "BROKER_SYNC",
    ) -> Dict:
        """브로커 잔고 스냅샷을 기준으로 포지션 상태를 강제 동기화한다."""
        assert direction in (POSITION_LONG, POSITION_SHORT), f"Invalid direction: {direction}"
        assert quantity > 0, f"Invalid broker quantity: {quantity}"

        prev_status = self.status
        prev_initial = max(int(self.initial_quantity or 0), int(self.quantity or 0))
        prev_entry_time = self.entry_time
        prev_stop = float(self.stop_price or 0.0)
        prev_anchor = float(self.trailing_anchor_price or 0.0)
        same_side_sync = prev_status == direction

        self.status = direction
        self.entry_price = price
        self.quantity = quantity
        self.entry_time = prev_entry_time if same_side_sync and prev_entry_time else (synced_at or now_kst())
        self.grade = grade
        self.regime = regime
        self.signal_direction = direction
        self.reverse_entry_enabled = False
        if same_side_sync and prev_initial > 0:
            self.initial_quantity = max(prev_initial, quantity)
        else:
            self.initial_quantity = quantity
        self.partial_1_done = False
        self.partial_2_done = False
        self.partial_3_done = False
        self.last_update_reason = f"sync_from_broker:{direction}"
        self.last_update_ts = synced_at or now_kst()
        self._recalculate_levels(atr)
        if same_side_sync:
            if prev_stop > 0:
                if direction == POSITION_LONG:
                    self.stop_price = max(self.stop_price, prev_stop)
                else:
                    self.stop_price = min(self.stop_price, prev_stop)
            if prev_anchor > 0:
                if direction == POSITION_LONG:
                    self.trailing_anchor_price = max(prev_anchor, price)
                else:
                    self.trailing_anchor_price = min(prev_anchor, price)
            else:
                self.trailing_anchor_price = price
        else:
            self.trailing_anchor_price = price
        self._sync_partial_progress()
        self._save_state()

        logger.warning(
            f"[Position] 브로커 기준 동기화: {direction} {quantity}계약 @ {price} "
            f"| 손절={self.stop_price:.2f}"
        )
        return {
            "direction": self.status,
            "entry_price": round(self.entry_price, 4),
            "quantity": self.quantity,
            "entry_ts": (
                self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                if self.entry_time else ""
            ),
        }

    def sync_flat_from_broker(self) -> None:
        """브로커 기준 무포지션 상태로 강제 동기화한다."""
        self.last_update_reason = "sync_flat_from_broker"
        self.last_update_ts = now_kst()
        self._reset_position()
        logger.warning("[Position] 브로커 기준 동기화: FLAT")

    def partial_close(self, exit_price: float, qty: int, reason: str) -> Dict:
        """부분 청산 — qty 계약만 청산하고 잔여 포지션 유지.

        _daily_trades는 증가시키지 않음 (최종 close_position에서만 카운트).
        """
        assert self.status != POSITION_FLAT, "포지션 없음"
        assert 0 < qty < self.quantity, (
            f"부분청산 수량 오류: qty={qty} total={self.quantity}"
        )

        mult    = 1 if self.status == POSITION_LONG else -1
        pnl_pts = (exit_price - self.entry_price) * mult
        commission = _calc_commission(self.entry_price, qty, self._pt_value) * 2  # 왕복
        pnl_krw = pnl_pts * self._pt_value * qty - commission
        forward_direction = self.signal_direction or self.status
        forward_pnl_pts = self._calc_directional_pnl_pts(forward_direction, exit_price)
        forward_commission = _calc_commission(self.entry_price, qty, self._pt_value) * 2
        forward_pnl_krw = forward_pnl_pts * self._pt_value * qty - forward_commission

        self._daily_pnl_pts += pnl_pts * qty
        self._daily_commission += commission
        self._daily_forward_pnl_pts += forward_pnl_pts * qty
        self._daily_forward_commission += forward_commission
        self.quantity        -= qty
        self._sync_partial_progress()
        self.last_update_reason = f"partial_close:{reason}"
        self.last_update_ts = now_kst()

        entry_ts_str = (
            self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.entry_time else ""
        )
        result = {
            "direction":    self.status,
            "executed_direction": self.status,
            "raw_direction": forward_direction,
            "entry_price":  self.entry_price,
            "exit_price":   exit_price,
            "quantity":     qty,
            "remaining":    self.quantity,
            "pnl_pts":      round(pnl_pts, 4),
            "pnl_krw":      round(pnl_krw, 0),
            "forward_pnl_pts": round(forward_pnl_pts, 4),
            "forward_pnl_krw": round(forward_pnl_krw, 0),
            "exit_reason":  reason,
            "hold_minutes": self._hold_minutes(),
            "entry_ts":     entry_ts_str,
            "grade":        self.grade,
            "forward_commission": round(forward_commission, 0),
            "reverse_entry_enabled": self.reverse_entry_enabled,
        }

        logger.info(
            f"[Position] 부분청산 {qty}계약 @ {exit_price} "
            f"| 잔여={self.quantity}계약 "
            f"| PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) | {reason}"
        )
        self._save_state()
        return result

    def arm_tp1_single_contract(self, current_price: float, atr: float = 0.0) -> Dict:
        """For single-contract positions, convert TP1 into protection instead of full exit."""
        assert self.status != POSITION_FLAT, "포지션 없음"
        assert self.quantity == 1, f"single-contract only: qty={self.quantity}"

        mult = 1 if self.status == POSITION_LONG else -1
        prev_stop = self.stop_price
        protected_stop = self.entry_price
        if mult * (prev_stop - protected_stop) > 0:
            protected_stop = prev_stop

        if mult * (protected_stop - self.stop_price) > 0:
            self.stop_price = protected_stop

        self.partial_1_done = True
        self._sync_partial_progress()
        self.last_update_reason = "arm_tp1_single_contract"
        self.last_update_ts = now_kst()
        self._save_state()

        logger.info(
            f"[Position] 1계약 TP1 암(arm) @ {current_price:.2f} "
            f"| stop {prev_stop:.2f} -> {self.stop_price:.2f}"
        )
        return {
            "direction": self.status,
            "entry_price": round(self.entry_price, 4),
            "current_price": round(current_price, 4),
            "prev_stop_price": round(prev_stop, 4),
            "new_stop_price": round(self.stop_price, 4),
            "tp1_price": round(self.tp1_price, 4),
            "tp2_price": round(self.tp2_price, 4),
            "quantity": self.quantity,
        }

    def arm_tp1_single_contract_with_mode(
        self,
        current_price: float,
        atr: float = 0.0,
        mode: str = "breakeven",
        alpha_pts: float = 0.20,
        atr_lock_mult: float = 0.25,
    ) -> Dict:
        """For single-contract positions, convert TP1 into protection instead of full exit."""
        assert self.status != POSITION_FLAT, "FLAT 상태에서 TP1 암 호출 불가"
        assert self.quantity == 1, f"single-contract only: qty={self.quantity}"

        mult = 1 if self.status == POSITION_LONG else -1
        prev_stop = self.stop_price
        mode = str(mode or "breakeven").strip().lower()

        protect_offset_pts = 0.0
        if mode == "breakeven_plus":
            protect_offset_pts = max(float(alpha_pts or 0.0), 0.0)
        elif mode == "atr_profit":
            protect_offset_pts = max(float(atr or 0.0) * float(atr_lock_mult or 0.0), 0.0)

        protected_stop = self.entry_price + mult * protect_offset_pts
        if mult * (prev_stop - protected_stop) > 0:
            protected_stop = prev_stop

        if mult * (protected_stop - self.stop_price) > 0:
            self.stop_price = protected_stop

        self.partial_1_done = True
        self._sync_partial_progress()
        self.last_update_reason = f"arm_tp1_single_contract:{mode}"
        self.last_update_ts = now_kst()
        self._save_state()

        logger.info(
            f"[Position] 1계약 TP1 보호전환 @ {current_price:.2f} "
            f"| mode={mode} | stop {prev_stop:.2f} -> {self.stop_price:.2f}"
        )
        return {
            "direction": self.status,
            "entry_price": round(self.entry_price, 4),
            "current_price": round(current_price, 4),
            "prev_stop_price": round(prev_stop, 4),
            "new_stop_price": round(self.stop_price, 4),
            "mode": mode,
            "protect_offset_pts": round(protect_offset_pts, 4),
            "tp1_price": round(self.tp1_price, 4),
            "tp2_price": round(self.tp2_price, 4),
            "quantity": self.quantity,
        }

    def update_trailing_stop(self, current_price: float, atr: float):
        """트레일링 스톱 업데이트"""
        if self.status == POSITION_FLAT:
            return

        mult = 1 if self.status == POSITION_LONG else -1
        unrealized_pts = (current_price - self.entry_price) * mult
        if self.trailing_anchor_price <= 0:
            self.trailing_anchor_price = self.entry_price
        if self.status == POSITION_LONG:
            self.trailing_anchor_price = max(self.trailing_anchor_price, current_price)
        else:
            self.trailing_anchor_price = min(self.trailing_anchor_price, current_price)

        if unrealized_pts >= atr * 2.0:
            # 2ATR 이상 수익 → 최고점 추적 (1ATR 간격)
            new_stop = self.trailing_anchor_price - mult * atr
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

    def is_tp3_hit(self, price: float) -> bool:
        if self.status == POSITION_FLAT or self.partial_3_done:
            return False
        if self.status == POSITION_LONG:
            return price >= self.tp3_price
        return price <= self.tp3_price

    def get_stage_plan(self) -> Tuple[int, int, int]:
        total_qty = int(self.initial_quantity or self.quantity or 0)
        if total_qty <= 0:
            return (0, 0, 0)
        if total_qty == 1:
            return (1, 0, 0)
        if total_qty == 2:
            return (1, 1, 0)

        raw = [
            total_qty * 0.33,
            total_qty * 0.33,
            total_qty * 0.34,
        ]
        plan = [int(value) for value in raw]
        remainder = total_qty - sum(plan)
        order = sorted(
            range(3),
            key=lambda idx: (raw[idx] - plan[idx], idx == 2, -idx),
            reverse=True,
        )
        for idx in order:
            if remainder <= 0:
                break
            plan[idx] += 1
            remainder -= 1
        return tuple(plan)

    def get_stage_targets(self) -> Tuple[int, int, int]:
        q1, q2, q3 = self.get_stage_plan()
        return (q1, q1 + q2, q1 + q2 + q3)

    def get_closed_quantity(self) -> int:
        if self.status == POSITION_FLAT and self.initial_quantity <= 0:
            return 0
        current_qty = max(int(self.quantity or 0), 0)
        initial_qty = max(int(self.initial_quantity or 0), current_qty)
        return max(0, initial_qty - current_qty)

    def get_stage_exit_qty(self, stage: int) -> int:
        stage = int(stage or 0)
        if stage < 1 or stage > 3:
            return 0
        targets = self.get_stage_targets()
        closed_qty = self.get_closed_quantity()
        needed = max(0, targets[stage - 1] - closed_qty)
        return min(max(int(self.quantity or 0), 0), needed)

    def resolve_stage_for_exit_qty(self, exit_qty: int, *, full_close: bool = False) -> int:
        exit_qty = max(int(exit_qty or 0), 0)
        if exit_qty <= 0:
            return 0
        if full_close:
            return 3
        targets = self.get_stage_targets()
        closed_after = self.get_closed_quantity() + exit_qty
        if closed_after >= targets[2]:
            return 3
        if closed_after >= targets[1]:
            return 2
        if closed_after >= targets[0]:
            return 1
        return 0

    def unrealized_pnl_pts(self, current_price: float) -> float:
        if self.status == POSITION_FLAT:
            return 0.0
        mult = 1 if self.status == POSITION_LONG else -1
        return (current_price - self.entry_price) * mult * self.quantity

    def unrealized_forward_pnl_pts(self, current_price: float) -> float:
        if self.status == POSITION_FLAT:
            return 0.0
        return self._calc_directional_pnl_pts(
            self.signal_direction or self.status,
            current_price,
        ) * self.quantity

    def _hold_minutes(self) -> int:
        if not self.entry_time:
            return 0
        delta = now_kst() - self.entry_time
        return int(delta.total_seconds() // 60)

    def _recalculate_levels(self, atr: float) -> None:
        mult = 1 if self.status == POSITION_LONG else -1
        self.stop_price = self.entry_price - mult * atr * ATR_STOP_MULT
        self.tp1_price = self.entry_price + mult * atr * ATR_TP1_MULT
        self.tp2_price = self.entry_price + mult * atr * ATR_TP2_MULT
        self.tp3_price = self.entry_price + mult * atr * ATR_TP3_MULT

    def get_trailing_reference_price(self, current_price: float, atr: float) -> float:
        if self.status == POSITION_FLAT:
            return 0.0
        mult = 1 if self.status == POSITION_LONG else -1
        unrealized_pts = (current_price - self.entry_price) * mult
        if unrealized_pts >= atr * 2.0:
            return float(self.trailing_anchor_price or current_price or self.entry_price)
        if unrealized_pts >= atr * 1.5:
            return self.entry_price + mult * atr * 0.5
        if unrealized_pts >= atr * 1.0:
            return self.entry_price
        return self.entry_price - mult * atr * ATR_STOP_MULT

    def _sync_partial_progress(self) -> None:
        target_1, target_2, target_3 = self.get_stage_targets()
        closed_qty = self.get_closed_quantity()
        self.partial_1_done = bool(self.partial_1_done or (target_1 > 0 and closed_qty >= target_1))
        self.partial_2_done = bool(self.partial_2_done or (target_2 > 0 and closed_qty >= target_2))
        self.partial_3_done = bool(self.partial_3_done or (target_3 > 0 and closed_qty >= target_3))

    def _build_exit_result(
        self,
        exit_price: float,
        quantity: int,
        pnl_pts: float,
        pnl_krw: float,
        reason: str,
        filled_at: Optional[datetime.datetime] = None,
    ) -> Dict:
        entry_ts_str = (
            self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.entry_time else ""
        )
        return {
            "direction": self.status,
            "executed_direction": self.status,
            "raw_direction": self.signal_direction or self.status,
            "entry_price": self.entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "pnl_pts": round(pnl_pts, 4),
            "pnl_krw": round(pnl_krw, 0),
            "exit_reason": reason,
            "hold_minutes": self._hold_minutes(),
            "entry_ts": entry_ts_str,
            "exit_ts": (
                (filled_at or now_kst()).strftime("%Y-%m-%d %H:%M:%S")
            ),
            "grade": self.grade,
            "reverse_entry_enabled": self.reverse_entry_enabled,
        }

    def _reset_position(self) -> None:
        self.status = POSITION_FLAT
        self.entry_price = 0.0
        self.quantity = 0
        self.entry_time = None
        self.grade = ""
        self.regime = ""
        self.signal_direction = ""
        self.reverse_entry_enabled = False
        self.stop_price = 0.0
        self.tp1_price = 0.0
        self.tp2_price = 0.0
        self.tp3_price = 0.0
        self.trailing_anchor_price = 0.0
        self.partial_1_done = False
        self.partial_2_done = False
        self.partial_3_done = False
        self.initial_quantity = 0
        self._optimistic = False
        self.last_update_ts = self.last_update_ts or now_kst()
        self._save_state()

    # ── 일일 통계 ──────────────────────────────────────────────
    def daily_stats(self) -> dict:
        gross_krw = round(self._daily_pnl_pts * self._pt_value, 0)
        return {
            "trades":     self._daily_trades,
            "wins":       self._daily_wins,
            "losses":     self._daily_trades - self._daily_wins,
            "win_rate":   self._daily_wins / max(self._daily_trades, 1),
            "pnl_pts":    round(self._daily_pnl_pts, 4),
            "pnl_krw":    round(gross_krw - self._daily_commission, 0),  # 수수료 차감 순손익
            "gross_krw":  gross_krw,
            "commission": round(self._daily_commission, 0),
        }

    def daily_forward_stats(self) -> dict:
        gross_krw = round(self._daily_forward_pnl_pts * self._pt_value, 0)
        return {
            "trades": self._daily_forward_trades,
            "wins": self._daily_forward_wins,
            "losses": self._daily_forward_trades - self._daily_forward_wins,
            "win_rate": self._daily_forward_wins / max(self._daily_forward_trades, 1),
            "pnl_pts": round(self._daily_forward_pnl_pts, 4),
            "pnl_krw": round(gross_krw - self._daily_forward_commission, 0),
            "gross_krw": gross_krw,
            "commission": round(self._daily_forward_commission, 0),
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
            forward_pnl_pts = float(
                row["forward_pnl_pts"]
                if "forward_pnl_pts" in row.keys() and row["forward_pnl_pts"] is not None
                else pnl_pts
            )
            self._daily_forward_pnl_pts += forward_pnl_pts * qty
            self._daily_forward_trades += 1
            if forward_pnl_pts > 0:
                self._daily_forward_wins += 1
            # trades.db에 commission 컬럼이 있으면 복원, 없으면 재계산
            commission = float(row["commission"] if "commission" in row.keys() else 0.0)
            if commission == 0.0 and "entry_price" in row.keys():
                ep = float(row["entry_price"] or 0.0)
                commission = _calc_commission(ep, qty) * 2
            self._daily_commission += commission
            forward_commission = float(
                row["forward_commission_krw"]
                if "forward_commission_krw" in row.keys() and row["forward_commission_krw"] is not None
                else commission
            )
            self._daily_forward_commission += forward_commission

    def reset_daily(self):
        self._daily_pnl_pts = 0.0
        self._daily_trades  = 0
        self._daily_wins    = 0
        self._daily_commission = 0.0
        self._daily_forward_pnl_pts = 0.0
        self._daily_forward_trades = 0
        self._daily_forward_wins = 0
        self._daily_forward_commission = 0.0

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
                "signal_direction": self.signal_direction,
                "reverse_entry_enabled": self.reverse_entry_enabled,
                "stop_price":   self.stop_price,
                "tp1_price":    self.tp1_price,
                "tp2_price":    self.tp2_price,
                "tp3_price":    self.tp3_price,
                "trailing_anchor_price": self.trailing_anchor_price,
                "initial_quantity": self.initial_quantity,
                "partial_1_done": self.partial_1_done,
                "partial_2_done": self.partial_2_done,
                "partial_3_done": self.partial_3_done,
                "last_update_reason": self.last_update_reason,
                "last_update_ts": (
                    self.last_update_ts.isoformat() if self.last_update_ts else None
                ),
                "futures_code": self._futures_code,
                "saved_at":     now_kst().isoformat(),
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

            self._loaded_futures_code = str(state.get("futures_code") or "").strip()
            self.status      = state["status"]
            self.entry_price = float(state["entry_price"])
            self.quantity    = int(state["quantity"])
            self.entry_time  = (datetime.datetime.fromisoformat(state["entry_time"])
                                if state.get("entry_time") else None)
            self.grade        = state.get("grade", "")
            self.regime       = state.get("regime", "")
            self.signal_direction = state.get("signal_direction", self.status)
            self.reverse_entry_enabled = bool(state.get("reverse_entry_enabled", False))
            self.stop_price   = float(state.get("stop_price", 0))
            self.tp1_price    = float(state.get("tp1_price", 0))
            self.tp2_price    = float(state.get("tp2_price", 0))
            self.tp3_price    = float(state.get("tp3_price", 0))
            self.trailing_anchor_price = float(state.get("trailing_anchor_price", self.entry_price))
            self.initial_quantity = int(state.get("initial_quantity", self.quantity))
            self.partial_1_done = bool(state.get("partial_1_done", False))
            self.partial_2_done = bool(state.get("partial_2_done", False))
            self.partial_3_done = bool(state.get("partial_3_done", False))
            if self.tp3_price == 0.0 and self.stop_price and self.tp1_price and self.tp2_price:
                atr = abs(self.entry_price - self.stop_price) / ATR_STOP_MULT if ATR_STOP_MULT else 0.0
                mult = 1 if self.status == POSITION_LONG else -1
                self.tp3_price = self.entry_price + mult * max(atr, 0.0) * ATR_TP3_MULT
            self._sync_partial_progress()
            self.last_update_reason = state.get("last_update_reason", "unknown")
            self.last_update_ts = (
                datetime.datetime.fromisoformat(state["last_update_ts"])
                if state.get("last_update_ts") else None
            )

            logger.warning(
                f"[Position] 이전 포지션 복원: {self.status} {self.quantity}계약 "
                f"@ {self.entry_price} (손절={self.stop_price:.2f})"
            )
            logger.warning(
                "[PositionDiag] restore source=%s saved_at=%s last_update_ts=%s",
                self.last_update_reason,
                state.get("saved_at", ""),
                state.get("last_update_ts", ""),
            )
            return True
        except Exception as e:
            logger.warning(f"[Position] 상태 복원 실패: {e}")
            return False

    def peek_saved_entry_time(self, direction: str = "") -> Optional[datetime.datetime]:
        """같은 날 저장된 상태 파일에서 진입시각 힌트를 읽는다."""
        if not os.path.exists(_STATE_FILE):
            return None
        try:
            with open(_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            saved_at = datetime.datetime.fromisoformat(state.get("saved_at", ""))
            if saved_at.date() != datetime.date.today():
                return None
            status = str(state.get("status") or "").strip().upper()
            if status == POSITION_FLAT:
                return None
            if direction and status != str(direction).strip().upper():
                return None
            entry_time_raw = state.get("entry_time")
            if not entry_time_raw:
                return None
            return datetime.datetime.fromisoformat(str(entry_time_raw))
        except Exception:
            return None

    def _calc_directional_pnl_pts(self, direction: str, exit_price: float) -> float:
        mult = 1 if direction == POSITION_LONG else -1
        return (exit_price - self.entry_price) * mult
