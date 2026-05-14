# safety/kill_switch.py — 즉시 비상 정지
"""
KillSwitch: 시스템 즉시 중단 (신규 진입 차단 + 비상 청산 트리거)

발동 방법:
  1. 수동: kill_switch.activate("이유")
  2. 키보드 단축키: Ctrl+Alt+K (main.py에서 연결)
  3. 외부 파일: data/KILL_SWITCH 파일 존재 시 자동 감지
"""
import logging
import os
import datetime
from typing import Optional, Callable

from config.settings import DATA_DIR
from utils.notify import notify
from utils.time_utils import now_kst

logger = logging.getLogger("SYSTEM")

KILL_FILE = os.path.join(DATA_DIR, "KILL_SWITCH")


class KillSwitch:
    """
    즉시 비상 정지 스위치.
    활성화 시 모든 신규 진입 차단 + emergency_exit 콜백 호출.
    """

    def __init__(self, emergency_exit_callback: Optional[Callable] = None):
        self._active: bool = False
        self._reason: str = ""
        self._activated_at: Optional[datetime.datetime] = None
        self._emergency_exit = emergency_exit_callback

    # ── 상태 조회 ──────────────────────────────────────────────
    @property
    def is_active(self) -> bool:
        if not self._active:
            self._check_kill_file()
        return self._active

    def _check_kill_file(self):
        """data/KILL_SWITCH 파일 존재 시 자동 활성화."""
        if os.path.exists(KILL_FILE):
            self.activate("KILL_FILE 감지")

    # ── 활성화 ─────────────────────────────────────────────────
    def activate(self, reason: str = "수동 발동") -> None:
        if self._active:
            return
        self._active = True
        self._reason = reason
        self._activated_at = now_kst()

        logger.critical("[KillSwitch] ★★★ 비상 정지 활성화 ★★★ 사유: %s", reason)
        notify(f"KillSwitch 발동!\n사유: {reason}", "CRITICAL")

        # 킬 파일 생성 (다른 프로세스에도 알림)
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(KILL_FILE, "w", encoding="utf-8") as f:
                f.write(f"{self._activated_at.isoformat()} | {reason}\n")
        except OSError:
            logger.warning("[KillSwitch] KILL_FILE 생성 실패")

        # 비상 청산 실행
        if self._emergency_exit:
            try:
                self._emergency_exit()
            except Exception:
                logger.exception("[KillSwitch] 비상 청산 콜백 오류")

    # ── 비활성화 (장 시작 시 수동 리셋) ─────────────────────────
    def deactivate(self) -> None:
        self._active = False
        self._reason = ""
        self._activated_at = None

        # 킬 파일 삭제
        if os.path.exists(KILL_FILE):
            try:
                os.remove(KILL_FILE)
            except OSError:
                pass

        logger.info("[KillSwitch] 비상 정지 해제")

    def status_dict(self) -> dict:
        return {
            "active":       self._active,
            "reason":       self._reason,
            "activated_at": (
                self._activated_at.strftime("%H:%M:%S")
                if self._activated_at else None
            ),
        }
