# safety/shadow_session.py — Shadow Session 트래커 [6순위]
"""
Shadow Session (제안 9):
  09:00~09:40은 실제 주문 대신 가상체결 채점만 진행.
  게이트 조건을 통과해야 실주문 세션으로 전환.

게이트 조건 (단일):
  ① CORE 건강 점수 >= 70점
  ② z-score 경고 < 50 (사실상 비활성 — 급변장 대비 완화)

  [2026-06-08] acc30m 게이트 제거:
    스캘퍼 진입 호라이즌(1m/5m)과 30m 채점이 불일치하고,
    장초반 30분 채점 지연으로 SHADOW 구간에서 의미 없음.
    acc30m은 CB③(당일 정지 조건)에서만 관리.

상태 머신:
  SHADOW  → (조건 통과, 09:40 이전) → LIVE
  SHADOW  → (시간 09:40 초과, 미통과) → BLOCKED
  LIVE    → 정상 운영
  BLOCKED → 해당일 진입 차단 / core_health 회복 시 자동 복구
"""
import datetime
import logging
from collections import deque
from typing import Optional

from logging_system.log_manager import log_manager
from utils.notify import notify as _notify

logger = logging.getLogger("SYSTEM")

_BLOCKED_NOTIFY_MIN = 30   # [P6] BLOCKED 지속 시 첫 알림 임계 (분)

# 게이트 임계값
# [2026-06-08] acc30m 게이트 제거 — 스캘퍼 진입 호라이즌(1m/5m)과 불일치,
# 30분 채점 지연으로 장초반에 의미 없음. CB③에서만 관리.
_GATE_CORE_HEALTH = 70     # CORE 건강 점수 최소 (단일 조건)
# z-score 조건 완화 (2026-06-02): 급변장 시 toxicity_atr_stress 등이 z>4 폭발하여
# BLOCKED 고착 발생 → 50으로 완화(사실상 비활성화).
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
        self._gate_checks: dict = {"core_health": False, "zscore": False}
        self._z_warn_buf: deque = deque(maxlen=_ZSCORE_WINDOW)
        self._virtual_pnl: float = 0.0          # 가상 PnL 누적 (pt)
        self._virtual_trades: int = 0
        self._virtual_correct: int = 0
        self._transition_time: Optional[str] = None
        # [P6] BLOCKED 지속 알림
        self._blocked_since: Optional[datetime.datetime] = None
        self._blocked_last_notify: Optional[datetime.datetime] = None
        # 거래소 CB 중 플래그 — BLOCKED 복구 시도 skip 용
        self._exchange_cb_active: bool = False

    def update(
        self,
        ts_dt: datetime.datetime,
        core_health_score: int,
        z_warn_count: int,
        virtual_pnl_delta: float = 0.0,
        virtual_correct: Optional[bool] = None,
    ) -> None:
        """
        매분 호출.

        Args:
            ts_dt:              현재 분봉 datetime
            core_health_score:  CoreHealthScore.score (0~100)
            z_warn_count:       해당 봉 극단 z-score 피처 수
            virtual_pnl_delta:  이번 봉 가상 체결 손익 (pt, 실제 진입 시뮬)
            virtual_correct:    이번 봉 가상 예측 적중 여부 (None = 미집계)
        """
        # BLOCKED 복구: core_health 단일 조건 (acc30m 제거 — 스캘퍼 호라이즌 불일치)
        if self._state == SHADOW_BLOCKED:
            # 거래소 CB 중에는 core_health가 무의미 — 복구 시도 자체를 skip
            if self._exchange_cb_active:
                return
            if core_health_score >= _GATE_CORE_HEALTH:
                self._state = SHADOW_LIVE
                self._transition_time = ts_dt.strftime("%H:%M")
                self._blocked_since = None          # [P6] 타이머 리셋
                self._blocked_last_notify = None
                msg = (
                    f"[ShadowSession] BLOCKED→LIVE 복구 | {self._transition_time} | "
                    f"core={core_health_score} z={z_warn_count}"
                )
                logger.info(msg)
                log_manager.system(msg, "INFO")
            else:
                # [P6] BLOCKED 지속 알림 — 30분마다 반복
                _now = ts_dt
                _elapsed = (
                    (_now - self._blocked_since).total_seconds() / 60.0
                    if self._blocked_since else 0.0
                )
                _since_last = (
                    (_now - self._blocked_last_notify).total_seconds() / 60.0
                    if self._blocked_last_notify else float("inf")
                )
                if _elapsed >= _BLOCKED_NOTIFY_MIN and _since_last >= _BLOCKED_NOTIFY_MIN:
                    _failed = [k for k, ok in self._gate_checks.items() if not ok]
                    _action = (
                        "→ 시스템 로그 확인 (CoreHealth 저하 원인 파악)"
                        if "core_health" in _failed
                        else "→ 자연 회복 대기"
                    )
                    _msg = (
                        f"[ShadowSession] BLOCKED {_elapsed:.0f}분 지속 — 복구 미발동\n"
                        f"미통과: {_failed} | "
                        f"core={core_health_score}(기준 {_GATE_CORE_HEALTH})\n"
                        f"권장 대응: {_action}"
                    )
                    logger.warning(_msg)
                    log_manager.system(_msg, "WARNING")
                    _notify(_msg, "WARNING")
                    self._blocked_last_notify = _now
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

        # 게이트 체크 (acc30m 제거 — CB③에서 별도 관리)
        self._gate_checks["core_health"] = core_health_score >= _GATE_CORE_HEALTH
        self._gate_checks["zscore"]      = recent_z_total < _GATE_ZSCORE_WARN

        all_pass = all(self._gate_checks.values())

        # 09:40 이전에 전체 통과 → LIVE 전환
        if all_pass and ts_dt.hour == 9 and ts_dt.minute < _SHADOW_END_MIN:
            self._state = SHADOW_LIVE
            self._transition_time = ts_dt.strftime("%H:%M")
            msg = (
                f"[ShadowSession] LIVE 전환 | {self._transition_time} | "
                f"core={core_health_score} z={recent_z_total} "
                f"가상PnL={self._virtual_pnl:+.1f}pt"
            )
            logger.info(msg)
            log_manager.system(msg, "INFO")
            return

        # 09:40 초과, 미통과 → BLOCKED
        if ts_dt.hour == 9 and ts_dt.minute >= _SHADOW_END_MIN and not all_pass:
            self._state = SHADOW_BLOCKED
            self._transition_time = ts_dt.strftime("%H:%M")
            self._blocked_since = ts_dt          # [P6] 타이머 시작
            self._blocked_last_notify = None
            failed = [k for k, ok in self._gate_checks.items() if not ok]
            msg = (
                f"[ShadowSession] BLOCKED | {self._transition_time} | "
                f"미통과={failed} core={core_health_score} z={recent_z_total}"
            )
            logger.warning(msg)
            log_manager.system(msg, "WARNING")

    def mark_exchange_cb(self, active: bool) -> None:
        """거래소 서킷브레이커 중임을 마킹.

        active=True  : CB 진입 — BLOCKED 복구 시도를 중단하고 대기.
        active=False : CB 해제 — 복구 시도 재개 (force_live와 함께 호출).
        """
        self._exchange_cb_active = active

    def force_live(self, reason: str = "") -> None:
        """외부 이벤트(거래소 CB 해제)로 강제 LIVE 전환.

        BLOCKED 상태일 때만 동작. core_health 조건 면제.
        """
        if self._state == SHADOW_BLOCKED:
            self._state = SHADOW_LIVE
            self._blocked_since = None
            self._blocked_last_notify = None
            msg = (
                f"[ShadowSession] 거래소 CB 해제 → 강제 LIVE 복구"
                f" | reason={reason}"
            )
            logger.info(msg)
            log_manager.system(msg, "INFO")

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
        self._gate_checks = {"core_health": False, "zscore": False}
        self._z_warn_buf.clear()
        self._virtual_pnl = 0.0
        self._virtual_trades = 0
        self._virtual_correct = 0
        self._transition_time = None
        self._blocked_since = None        # [P6]
        self._blocked_last_notify = None  # [P6]
        self._exchange_cb_active = False  # 거래소 CB 플래그도 초기화

    def status_dict(self) -> dict:
        return {
            "state":            self._state,
            "gate_checks":      self._gate_checks,
            "virtual_pnl":      round(self._virtual_pnl, 2),
            "virtual_trades":   self._virtual_trades,
            "virtual_accuracy": round(self.virtual_accuracy, 3),
            "transition_time":  self._transition_time,
        }
