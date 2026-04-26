# safety/circuit_breaker.py — 5종 트리거 비상 정지
"""
Circuit Breaker (설계 명세 A2):

발동 조건 5종:
  ① 1분 내 신호 5번 이상 반전      → 15분 진입 정지
  ② 5분 내 손절 3번 연속           → 당일 시스템 정지
  ③ 30분 정확도 이동평균 < 35%     → 당일 시스템 정지
  ④ 변동성 ATR 평균의 3배 초과     → 5분 진입 정지
  ⑤ API 응답 지연 5초 초과        → 전 포지션 즉시 청산

2010 Flash Crash 이후 모든 헤지펀드 의무 도입.
"""
import datetime
import logging
from collections import deque
from typing import Callable, Optional

from config.settings import (
    CB_SIGNAL_FLIP_LIMIT, CB_SIGNAL_FLIP_PAUSE,
    CB_CONSEC_STOP_LIMIT, CB_ACCURACY_MIN_30M,
    CB_ATR_MULT_LIMIT, CB_API_LATENCY_LIMIT, CB_API_LATENCY_PAUSE,
)
from config.constants import CB_STATE_NORMAL, CB_STATE_PAUSED, CB_STATE_HALTED
from utils.notify import notify_circuit_breaker

logger = logging.getLogger("SYSTEM")


class CircuitBreaker:
    """5종 트리거 Circuit Breaker"""

    def __init__(self, emergency_exit_callback: Optional[Callable] = None):
        """
        Args:
            emergency_exit_callback: 즉시 청산이 필요할 때 호출할 함수
        """
        self._state: str = CB_STATE_NORMAL
        self._pause_until: Optional[datetime.datetime] = None
        self._emergency_exit = emergency_exit_callback

        # 트리거 ① 신호 반전 추적 (1분 창)
        self._signal_history: deque = deque()   # (timestamp, direction)
        self._flip_window_sec = 60

        # 트리거 ② 연속 손절 카운터
        self._consec_stops: int = 0

        # 트리거 ③ 30분 정확도 버퍼
        self._accuracy_buf: deque = deque(maxlen=30)  # 매분 정확도

        # 트리거 ④ ATR 비율
        self._atr_buf: deque = deque(maxlen=30)

        # 트리거 ⑤ 최근 API 지연
        self._last_latency: float = 0.0

    # ── 상태 조회 ──────────────────────────────────────────────
    @property
    def state(self) -> str:
        self._check_pause_expiry()
        return self._state

    def is_entry_allowed(self) -> bool:
        return self.state == CB_STATE_NORMAL

    def _check_pause_expiry(self):
        if self._state == CB_STATE_PAUSED and self._pause_until:
            if datetime.datetime.now() >= self._pause_until:
                self._state = CB_STATE_NORMAL
                self._pause_until = None
                logger.info("[CB] 일시 정지 해제 — 정상 복귀")

    # ── 트리거 ① 신호 반전 ────────────────────────────────────
    def record_signal(self, direction: int):
        now = datetime.datetime.now()
        self._signal_history.append((now, direction))

        # 1분 이전 제거
        cutoff = now - datetime.timedelta(seconds=self._flip_window_sec)
        while self._signal_history and self._signal_history[0][0] < cutoff:
            self._signal_history.popleft()

        # 반전 횟수 계산
        signals = [d for _, d in self._signal_history]
        flips = sum(1 for i in range(1, len(signals)) if signals[i] != signals[i-1])

        if flips >= CB_SIGNAL_FLIP_LIMIT:
            self._trigger_pause(
                CB_SIGNAL_FLIP_PAUSE,
                f"신호 반전 {flips}회/분",
            )

    # ── 트리거 ② 연속 손절 ────────────────────────────────────
    def record_stop_loss(self):
        self._consec_stops += 1
        logger.warning(f"[CB] 연속 손절 {self._consec_stops}회")
        if self._consec_stops >= CB_CONSEC_STOP_LIMIT:
            self._trigger_halt(f"연속 손절 {self._consec_stops}회 — 당일 정지")

    def record_win(self):
        self._consec_stops = 0   # 수익 시 카운터 초기화

    # ── 트리거 ③ 정확도 저하 ──────────────────────────────────
    def record_accuracy(self, correct: bool):
        self._accuracy_buf.append(1.0 if correct else 0.0)
        if len(self._accuracy_buf) >= 30:
            acc = sum(self._accuracy_buf) / len(self._accuracy_buf)
            if acc < CB_ACCURACY_MIN_30M:
                self._trigger_halt(f"30분 정확도 {acc:.1%} < {CB_ACCURACY_MIN_30M:.0%}")

    # ── 트리거 ④ ATR 급등 ─────────────────────────────────────
    def record_atr(self, atr_ratio: float):
        self._atr_buf.append(atr_ratio)
        if atr_ratio >= CB_ATR_MULT_LIMIT:
            self._trigger_pause(5, f"ATR {atr_ratio:.1f}배 급등")

    # ── 트리거 ⑤ API 지연 ─────────────────────────────────────
    def record_api_latency(self, latency_sec: float):
        self._last_latency = latency_sec
        if latency_sec >= CB_API_LATENCY_LIMIT:
            logger.critical(f"[CB] API 지연 {latency_sec:.1f}초 — 즉시 청산")
            notify_circuit_breaker(
                f"API 지연 {latency_sec:.1f}초",
                "전 포지션 즉시 청산",
            )
            if self._emergency_exit:
                self._emergency_exit()
            self._trigger_pause(
                CB_API_LATENCY_PAUSE // 60,
                f"API 지연 {latency_sec:.1f}초",
            )

    # ── 내부 트리거 ────────────────────────────────────────────
    def _trigger_pause(self, minutes: int, reason: str):
        if self._state == CB_STATE_HALTED:
            return
        self._state = CB_STATE_PAUSED
        self._pause_until = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        logger.warning(f"[CB] {minutes}분 진입 정지 | {reason}")
        notify_circuit_breaker(reason, f"{minutes}분 진입 정지")

    def _trigger_halt(self, reason: str):
        self._state = CB_STATE_HALTED
        self._pause_until = None
        logger.critical(f"[CB] 당일 시스템 정지 | {reason}")
        notify_circuit_breaker(reason, "당일 시스템 정지")

    def reset_daily(self):
        """장 시작 시 일간 리셋"""
        self._state = CB_STATE_NORMAL
        self._pause_until = None
        self._signal_history.clear()
        self._consec_stops = 0
        self._accuracy_buf.clear()
        self._atr_buf.clear()
        logger.info("[CB] 일간 리셋 완료")

    def status_dict(self) -> dict:
        return {
            "state":          self.state,
            "pause_until":    self._pause_until.strftime("%H:%M:%S") if self._pause_until else None,
            "consec_stops":   self._consec_stops,
            "last_latency":   self._last_latency,
            "accuracy_30m":   round(sum(self._accuracy_buf) / max(len(self._accuracy_buf), 1), 3),
        }
