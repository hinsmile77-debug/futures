# collection/kiwoom/latency_sync.py — HFT 타임스탬프 동기화 (v7.0)
"""
키움 API 수신 지연을 측정하고 보정된 타임스탬프를 제공한다.

배경:
  - 키움 API는 체결 시각을 문자열(HHMMSS)로만 제공 → 마이크로초 없음
  - 로컬 클록으로 수신 시각을 기록하되, 네트워크 지연 offset을 추정해 보정
  - Circuit Breaker에서 CB_API_LATENCY_LIMIT(5초) 초과 시 정지 신호 발생

핵심 개념:
  - recv_ns   : perf_counter_ns() 기준 수신 시각 (monotonic, 절대 참조용)
  - latency   : recv_ns - 체결 시각의 이론적 timestamp (ns 단위)
  - offset_ms : 이동평균 지연 (ms), Circuit Breaker 입력값으로 사용
"""

import logging
import time
from collections import deque
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)

# 이동평균 윈도우 크기 (틱 단위)
LATENCY_MA_WINDOW = 60

# 지연 이상치 필터: 이 값 이상은 측정 오류로 간주 (초)
LATENCY_OUTLIER_SEC = 10.0

# 지연 경고 임계치 (초) — 로그 WARNING 발생
LATENCY_WARN_SEC = 2.0


class LatencySync:
    """
    API 수신 지연 측정기.

    사용 예::

        sync = LatencySync()

        # 틱 수신 직후 호출
        recv_ns = time.perf_counter_ns()
        tick_time_str = "091523"  # HHMMSS
        adj_ts = sync.record(recv_ns, tick_time_str)

        # Circuit Breaker 연동
        if sync.offset_ms > CB_API_LATENCY_LIMIT * 1000:
            circuit_breaker.trigger(...)
    """

    def __init__(self):
        self._latencies_ms: deque = deque(maxlen=LATENCY_MA_WINDOW)
        self._offset_ms: float = 0.0       # 현재 이동평균 지연
        self._peak_ms: float = 0.0         # 당일 최대 지연
        self._sample_count: int = 0
        self._start_perf_ns: int = time.perf_counter_ns()
        self._start_wall: datetime = datetime.now()

    # ── 공개 API ──────────────────────────────────────────────

    def record(self, recv_perf_ns: int, tick_time_str: str) -> datetime:
        """
        틱 수신 시 호출. 지연을 측정하고 보정된 타임스탬프 반환.

        Parameters
        ----------
        recv_perf_ns  : time.perf_counter_ns() 로 기록한 수신 시각
        tick_time_str : 키움 체결시각 문자열 (HHMMSS 또는 HHMMSSMMM)

        Returns
        -------
        보정된 체결 datetime (마이크로초까지)
        """
        now_wall = self._perf_to_wall(recv_perf_ns)
        tick_dt  = self._parse_tick_time(tick_time_str, now_wall.date())

        if tick_dt is not None:
            latency_ms = (now_wall - tick_dt).total_seconds() * 1000.0
            self._update(latency_ms)
            # 조정 타임스탬프: 수신 시각에서 이동평균 지연 차감
            adj_ns = recv_perf_ns - int(self._offset_ms * 1_000_000)
            return self._perf_to_wall(adj_ns)

        # 체결시각 파싱 실패 → 보정 없이 수신 시각 반환
        return now_wall

    def reset_daily(self) -> None:
        """매일 장 시작 시 호출 — 피크값 초기화."""
        self._peak_ms = 0.0
        logger.info("[LatencySync] 일일 리셋 완료")

    # ── 속성 ──────────────────────────────────────────────────

    @property
    def offset_ms(self) -> float:
        """이동평균 수신 지연 (ms)."""
        return self._offset_ms

    @property
    def offset_sec(self) -> float:
        """이동평균 수신 지연 (초) — Circuit Breaker 비교용."""
        return self._offset_ms / 1000.0

    @property
    def peak_ms(self) -> float:
        """당일 최대 지연 (ms)."""
        return self._peak_ms

    @property
    def sample_count(self) -> int:
        """누적 측정 횟수."""
        return self._sample_count

    def is_healthy(self, limit_sec: float) -> bool:
        """현재 지연이 limit_sec 이하인지 반환."""
        return self.offset_sec <= limit_sec

    def summary(self) -> dict:
        """상태 요약 dict — 로그·Circuit Breaker 연동용."""
        return {
            "offset_ms":    round(self._offset_ms, 2),
            "peak_ms":      round(self._peak_ms, 2),
            "sample_count": self._sample_count,
            "window_size":  len(self._latencies_ms),
        }

    # ── 내부 ──────────────────────────────────────────────────

    def _update(self, latency_ms: float) -> None:
        # 이상치 필터
        if latency_ms < 0 or latency_ms > LATENCY_OUTLIER_SEC * 1000:
            logger.debug("[LatencySync] 이상치 무시: %.1f ms", latency_ms)
            return

        self._latencies_ms.append(latency_ms)
        self._sample_count += 1
        self._offset_ms = sum(self._latencies_ms) / len(self._latencies_ms)

        if latency_ms > self._peak_ms:
            self._peak_ms = latency_ms

        if latency_ms > LATENCY_WARN_SEC * 1000:
            logger.warning(
                "[LatencySync] 수신 지연 경고: %.1f ms (평균 %.1f ms)",
                latency_ms, self._offset_ms,
            )

    def _perf_to_wall(self, perf_ns: int) -> datetime:
        """
        perf_counter_ns → wall clock datetime 변환.
        start 기준점의 오차가 누적될 수 있으나 단기(수분) 스케일에서는 충분.
        """
        elapsed_us = (perf_ns - self._start_perf_ns) // 1000
        return self._start_wall + __import__("datetime").timedelta(microseconds=elapsed_us)

    @staticmethod
    def _parse_tick_time(time_str: str, today: date) -> Optional[datetime]:
        """
        키움 체결시각 문자열 → datetime.
        지원 형식: "HHMMSS", "HHMMSSMMM" (밀리초 포함)
        """
        s = time_str.strip()
        try:
            if len(s) >= 9:
                # HHMMSSMMM
                hh, mm, ss, ms = int(s[0:2]), int(s[2:4]), int(s[4:6]), int(s[6:9])
                return datetime(today.year, today.month, today.day, hh, mm, ss, ms * 1000)
            elif len(s) == 6:
                hh, mm, ss = int(s[0:2]), int(s[2:4]), int(s[4:6])
                return datetime(today.year, today.month, today.day, hh, mm, ss)
            else:
                return None
        except (ValueError, IndexError):
            return None
