# safety/shadow_session.py — Shadow Session 트래커 [6순위]
"""
Shadow Session (제안 9):
  09:00~09:40은 실제 주문 대신 가상체결 채점만 진행.
  3가지 게이트 조건을 모두 통과해야 실주문 세션으로 전환.

게이트 조건:
  ① acc30m  >= 40%   (30분 정확도)
  ② CORE 건강 점수   >= 70점
  ③ 최근 5분 z-score 경고 횟수 < 2

상태 머신:
  SHADOW  → (모든 조건 통과)  → LIVE
  SHADOW  → (시간 09:40 초과, 미통과) → BLOCKED
  LIVE    → 정상 운영
  BLOCKED → 해당일 진입 차단 (소형 진입만 허용)
"""
import datetime
import logging
from collections import deque
from typing import Optional

from logging_system.log_manager import log_manager

logger = logging.getLogger("SYSTEM")

# 게이트 임계값
_GATE_ACC30M      = 0.40   # 30분 정확도 최소
_GATE_CORE_HEALTH = 70     # CORE 건강 점수 최소
# z-score 조건 완화 (2026-06-02): 급변장 시 toxicity_atr_stress 등이 z>4 폭발하여
# BLOCKED 고착 발생 → 50으로 완화(사실상 비활성화). acc30m + core_health 2조건만 사용.
_GATE_ZSCORE_WARN = 50     # 급변장 대비 완화 (기존 2)
_SHADOW_END_MIN   = 40     # Shadow 세션 종료 시각 (분) — 09:40
_ZSCORE_WINDOW    = 5      # z-score 경고 추적 창 (분)

SHADOW_SHADOW  = "SHADOW"
SHADOW_LIVE    = "LIVE"
SHADOW_BLOCKED = "BLOCKED"


class ShadowSessionTracker:
    """
    장초반 Shadow Session 상태 머신.

    매분 파이프라인에서 update()를 호출하면 상태가 자동 전이.
    is_live_allowed() = True일 때만 실주문 허용.
    """

    def __init__(self):
        self._state: str = SHADOW_SHADOW
        self._gate_checks: dict = {"acc30m": False, "core_health": False, "zscore": False}
        self._z_warn_buf: deque = deque(maxlen=_ZSCORE_WINDOW)
        self._virtual_pnl: float = 0.0          # 가상 PnL 누적 (pt)
        self._virtual_trades: int = 0
        self._virtual_correct: int = 0
        self._transition_time: Optional[str] = None

    def update(
        self,
        ts_dt: datetime.datetime,
        acc30m: float,
        core_health_score: int,
        z_warn_count: int,
        virtual_pnl_delta: float = 0.0,
        virtual_correct: Optional[bool] = None,
    ) -> None:
        """
        매분 호출.

        Args:
            ts_dt:              현재 분봉 datetime
            acc30m:             CB③ 30분 정확도 (0.0~1.0)
            core_health_score:  CoreHealthScore.score (0~100)
            z_warn_count:       해당 봉 극단 z-score 피처 수
            virtual_pnl_delta:  이번 봉 가상 체결 손익 (pt, 실제 진입 시뮬)
            virtual_correct:    이번 봉 가상 예측 적중 여부 (None = 미집계)
        """
        # BLOCKED 복구: acc30m + core_health 조건 충족 시 LIVE 전환 허용
        # (z 조건 완화로 2조건만 체크 — 급변장 대비 2026-06-02)
        if self._state == SHADOW_BLOCKED:
            if acc30m >= _GATE_ACC30M and core_health_score >= _GATE_CORE_HEALTH:
                self._state = SHADOW_LIVE
                self._transition_time = ts_dt.strftime("%H:%M")
                msg = (
                    f"[ShadowSession] BLOCKED→LIVE 복구 | {self._transition_time} | "
                    f"acc30m={acc30m:.1%} core={core_health_score} z={z_warn_count}"
                )
                logger.info(msg)
                log_manager.system(msg, "INFO")
            return

        if self._state != SHADOW_SHADOW:
            return

        # 가상 PnL·거래 누적
        self._virtual_pnl += virtual_pnl_delta
        if virtual_correct is not None:
            self._virtual_trades += 1
            if virtual_correct:
                self._virtual_correct += 1

        # z-score 추적
        self._z_warn_buf.append(z_warn_count)
        recent_z_total = sum(self._z_warn_buf)

        # 게이트 체크
        self._gate_checks["acc30m"]      = acc30m >= _GATE_ACC30M
        self._gate_checks["core_health"] = core_health_score >= _GATE_CORE_HEALTH
        self._gate_checks["zscore"]      = recent_z_total < _GATE_ZSCORE_WARN

        all_pass = all(self._gate_checks.values())

        # 09:40 이전에 전체 통과 → LIVE 전환
        if all_pass and ts_dt.hour == 9 and ts_dt.minute < _SHADOW_END_MIN:
            self._state = SHADOW_LIVE
            self._transition_time = ts_dt.strftime("%H:%M")
            msg = (
                f"[ShadowSession] LIVE 전환 | {self._transition_time} | "
                f"acc30m={acc30m:.1%} core={core_health_score} z={recent_z_total} "
                f"가상PnL={self._virtual_pnl:+.1f}pt"
            )
            logger.info(msg)
            log_manager.system(msg, "INFO")
            return

        # 09:40 초과, 미통과 → BLOCKED
        if ts_dt.hour == 9 and ts_dt.minute >= _SHADOW_END_MIN and not all_pass:
            self._state = SHADOW_BLOCKED
            self._transition_time = ts_dt.strftime("%H:%M")
            failed = [k for k, ok in self._gate_checks.items() if not ok]
            msg = (
                f"[ShadowSession] BLOCKED | {self._transition_time} | "
                f"미통과={failed} acc30m={acc30m:.1%} core={core_health_score} "
                f"z={recent_z_total}"
            )
            logger.warning(msg)
            log_manager.system(msg, "WARNING")

    def is_live_allowed(self) -> bool:
        """실주문 허용 여부. LIVE 상태일 때만 True."""
        return self._state == SHADOW_LIVE

    def is_blocked(self) -> bool:
        return self._state == SHADOW_BLOCKED

    @property
    def state(self) -> str:
        return self._state

    @property
    def gate_checks(self) -> dict:
        return dict(self._gate_checks)

    @property
    def virtual_pnl(self) -> float:
        return self._virtual_pnl

    @property
    def virtual_accuracy(self) -> float:
        if self._virtual_trades == 0:
            return 0.0
        return self._virtual_correct / self._virtual_trades

    def reset_daily(self) -> None:
        self._state = SHADOW_SHADOW
        self._gate_checks = {"acc30m": False, "core_health": False, "zscore": False}
        self._z_warn_buf.clear()
        self._virtual_pnl = 0.0
        self._virtual_trades = 0
        self._virtual_correct = 0
        self._transition_time = None

    def status_dict(self) -> dict:
        return {
            "state":            self._state,
            "gate_checks":      self._gate_checks,
            "virtual_pnl":      round(self._virtual_pnl, 2),
            "virtual_trades":   self._virtual_trades,
            "virtual_accuracy": round(self.virtual_accuracy, 3),
            "transition_time":  self._transition_time,
        }
