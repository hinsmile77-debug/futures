# safety/contrarian_mode.py — 역모델 스위치 트래커 [6순위]
"""
Contrarian Mode (아이디어 B):
  모델이 한방향만 찍는데 30분 정확도가 25% 미만이면,
  수학적으로 역베팅이 75%+ 정확도 → 소형 역포지션 허용.

발동 조건 3가지 (모두 충족 시 ARMED → ACTIVE):
  ① acc30m < 25%
  ② 동방향 연속 10회 이상
  ③ NEUTRAL 레짐

상태 머신:
  WATCHING → (조건 2/3 충족) → ARMED
  ARMED    → (조건 3/3 충족) → ACTIVE (역베팅 허용)
  ACTIVE   → (acc30m 회복 >= 40% 또는 방향 전환) → CLEARED
  CLEARED  → WATCHING
"""
import logging
from typing import Optional

from logging_system.log_manager import log_manager

logger = logging.getLogger("SYSTEM")

# 발동 조건 임계값
_ACC30M_TRIGGER       = 0.25   # acc30m 이 이 값 미만이면 조건①
_SAME_DIR_STREAK      = 10     # 동방향 연속 횟수
_RECOVERY_ACC30M      = 0.40   # acc30m 회복 임계값 (ACTIVE → CLEARED)

# 역베팅 사이즈 (모의투자: 가상 1~2계약, 실전 연결 전 차단)
_CONTRA_SIZE          = 1      # 기본 역베팅 계약 수 (모의투자 검증용)

CONTRA_WATCHING  = "WATCHING"
CONTRA_ARMED     = "ARMED"
CONTRA_ACTIVE    = "ACTIVE"
CONTRA_CLEARED   = "CLEARED"


class ContrarianModeTracker:
    """
    역모델 스위치 — 모의투자 검증용 가상 역베팅 트래커.

    실주문은 차단하고 가상 PnL만 집계한다.
    실전 연결 여부는 별도 플래그(enable_real_order)로 제어.
    """

    def __init__(self, enable_real_order: bool = False):
        self._state: str          = CONTRA_WATCHING
        self._enable_real_order   = enable_real_order
        self._same_dir_streak: int = 0
        self._last_direction: Optional[int] = None
        self._virtual_pnl: float  = 0.0
        self._virtual_trades: int = 0
        self._virtual_correct: int = 0
        self._active_direction: Optional[int] = None  # 역베팅 방향
        self._conditions: dict = {
            "acc30m_low":    False,
            "same_dir":      False,
            "neutral_regime": False,
        }

    def update(
        self,
        acc30m: float,
        signal_direction: int,
        regime: str,
        virtual_pnl_delta: float = 0.0,
        signal_correct: Optional[bool] = None,
    ) -> None:
        """
        매분 파이프라인 호출.

        Args:
            acc30m:            CB③ 30분 정확도
            signal_direction:  앙상블 방향 (+1/-1/0)
            regime:            매크로 레짐 문자열
            virtual_pnl_delta: 역베팅 가상 손익 (pt)
            signal_correct:    원래 시그널 적중 여부 (역베팅은 반대)
        """
        # 동방향 연속 카운터 갱신
        if signal_direction != 0:
            if signal_direction == self._last_direction:
                self._same_dir_streak += 1
            else:
                self._same_dir_streak = 1
            self._last_direction = signal_direction

        # 조건 평가
        self._conditions["acc30m_low"]     = acc30m < _ACC30M_TRIGGER
        self._conditions["same_dir"]       = self._same_dir_streak >= _SAME_DIR_STREAK
        self._conditions["neutral_regime"] = (regime == "NEUTRAL")

        cond_count = sum(self._conditions.values())

        # 가상 PnL 집계 (ACTIVE 상태에서만)
        if self._state == CONTRA_ACTIVE:
            self._virtual_pnl += virtual_pnl_delta
            if signal_correct is not None:
                self._virtual_trades += 1
                # 역베팅: 원래 시그널이 틀리면 역베팅은 맞음
                if not signal_correct:
                    self._virtual_correct += 1

        # 상태 전이
        if self._state == CONTRA_WATCHING:
            if cond_count >= 2:
                self._state = CONTRA_ARMED
                logger.info(
                    "[Contrarian] ARMED | 조건 %d/3 | acc30m=%.1%% streak=%d regime=%s",
                    cond_count, acc30m, self._same_dir_streak, regime,
                )

        elif self._state == CONTRA_ARMED:
            if cond_count == 3:
                self._state           = CONTRA_ACTIVE
                self._active_direction = -signal_direction  # 역베팅 = 반대방향
                msg = (
                    f"[Contrarian] ACTIVE | acc30m={acc30m:.1%} "
                    f"streak={self._same_dir_streak} regime={regime} "
                    f"역베팅방향={'LONG' if self._active_direction == 1 else 'SHORT'}"
                )
                logger.warning(msg)
                log_manager.system(msg, "WARNING")

        elif self._state == CONTRA_ACTIVE:
            # 회복 조건: acc30m 40% 이상 회복 OR 방향 반전
            recovered = acc30m >= _RECOVERY_ACC30M
            dir_changed = (self._last_direction != (self._active_direction * -1)
                           if self._last_direction is not None else False)
            if recovered or dir_changed:
                reason = "acc30m 회복" if recovered else "방향 전환"
                self._state = CONTRA_CLEARED
                msg = (
                    f"[Contrarian] CLEARED ({reason}) | "
                    f"가상PnL={self._virtual_pnl:+.1f}pt {self._virtual_trades}건"
                )
                logger.info(msg)
                log_manager.system(msg, "INFO")

        elif self._state == CONTRA_CLEARED:
            self._state = CONTRA_WATCHING

    def should_contra_enter(self) -> bool:
        """역베팅 진입 허용 여부 (모의투자: 가상 집계, 실전: enable_real_order 필요)."""
        return self._state == CONTRA_ACTIVE

    @property
    def contra_direction(self) -> Optional[int]:
        """역베팅 방향. ACTIVE 상태일 때만 유효."""
        return self._active_direction if self._state == CONTRA_ACTIVE else None

    @property
    def contra_size(self) -> int:
        return _CONTRA_SIZE

    @property
    def state(self) -> str:
        return self._state

    @property
    def conditions(self) -> dict:
        return dict(self._conditions)

    @property
    def same_dir_streak(self) -> int:
        return self._same_dir_streak

    @property
    def virtual_pnl(self) -> float:
        return self._virtual_pnl

    @property
    def virtual_win_rate(self) -> float:
        if self._virtual_trades == 0:
            return 0.0
        return self._virtual_correct / self._virtual_trades

    def reset_daily(self) -> None:
        self._state = CONTRA_WATCHING
        self._same_dir_streak = 0
        self._last_direction = None
        self._virtual_pnl = 0.0
        self._virtual_trades = 0
        self._virtual_correct = 0
        self._active_direction = None
        self._conditions = {"acc30m_low": False, "same_dir": False, "neutral_regime": False}

    def status_dict(self) -> dict:
        return {
            "state":            self._state,
            "conditions":       self._conditions,
            "same_dir_streak":  self._same_dir_streak,
            "contra_direction": self._active_direction,
            "virtual_pnl":      round(self._virtual_pnl, 2),
            "virtual_trades":   self._virtual_trades,
            "virtual_win_rate": round(self.virtual_win_rate, 3),
        }
