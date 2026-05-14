# strategy/exit/time_exit.py — 시간 강제 청산 (15:10 절대원칙)
"""
당일 청산 절대원칙:
  15:10 → 강제 청산 시작
  예외 없음. 수익 중이어도, 손실 중이어도.

이유: 1분봉 시스템은 야간 데이터 없음 + 갭 리스크가 시스템 전체 무력화
"""
import datetime
import logging

from config.settings import FORCE_EXIT_TIME, NEW_ENTRY_CUTOFF
from utils.time_utils import now_kst

logger = logging.getLogger("TRADE")


class TimeExitManager:
    """시간 기반 청산 관리"""

    # 강제 청산: 15:10
    FORCE_EXIT = datetime.time(15, 10)
    # 신규 진입 금지: 15:00
    NO_ENTRY   = datetime.time(15, 0)
    # 최종 마감: 15:18 (슬리피지 감안)
    FINAL_CLOSE = datetime.time(15, 18)

    def should_force_exit(self, dt: datetime.datetime = None) -> bool:
        """강제 청산 시각 도달 여부"""
        if dt is None:
            dt = now_kst()
        result = dt.time() >= self.FORCE_EXIT
        if result:
            logger.warning(f"[TimeExit] 15:10 강제 청산 트리거 @ {dt.strftime('%H:%M:%S')}")
        return result

    def should_block_entry(self, dt: datetime.datetime = None) -> bool:
        """신규 진입 금지 시각 도달 여부"""
        if dt is None:
            dt = now_kst()
        return dt.time() >= self.NO_ENTRY

    def minutes_to_force_exit(self, dt: datetime.datetime = None) -> int:
        """강제 청산까지 남은 분 수"""
        if dt is None:
            dt = now_kst()
        today = dt.date()
        force_dt = datetime.datetime.combine(today, self.FORCE_EXIT)
        delta = force_dt - dt
        return max(0, int(delta.total_seconds() // 60))

    def get_exit_urgency(self, dt: datetime.datetime = None) -> str:
        """
        청산 긴박도 반환
          NORMAL  : 청산 여유 있음
          WARNING : 20분 이내
          URGENT  : 10분 이내
          FORCE   : 강제 청산
        """
        mins = self.minutes_to_force_exit(dt)
        if dt is not None and self.should_force_exit(dt):
            return "FORCE"
        elif mins <= 10:
            return "URGENT"
        elif mins <= 20:
            return "WARNING"
        return "NORMAL"
