# logging_system/log_manager.py — 5층 로그 시스템 관리자
"""
대시보드의 5개 로그 창과 연동되는 이벤트 버퍼.

Layer 1 (SYSTEM)   — 시스템 부팅·종료·Circuit Breaker
Layer 2 (SIGNAL)   — 예측 신호·앙상블 결정
Layer 3 (TRADE)    — 진입·청산 실행
Layer 4 (LEARNING) — 자가학습·SHAP 교체
Layer 5 (DEBUG)    — 피처·모델 상세 디버그
"""
import datetime
import logging
import os
import threading
import traceback
from collections import deque
from typing import Dict, List, Callable, Optional

from utils.logger import get_logger

# [302차] 크로스스레드 GUI 콜백 진단 전용 로거 — log_manager를 거치지 않고
# 별도 파일 핸들러로만 기록해 무한 재귀·동일 크래시 경로 재사용을 피한다.
# 배경: 0707 15:40:27 daily_close() 크래시 딥다이브 중 crash_fault.log
# (faulthandler dump_traceback_later)에서 크래시 순간 main 스레드가 아니라
# _run_daily_close 백그라운드 스레드가 circuit_breaker.reset_daily() →
# log_manager.system() → 대시보드 콜백(QTextCursor 직접 조작) 경로를 실행
# 중이었음을 확인 — PyQt는 GUI 위젯을 GUI 스레드 밖에서 조작하면 정의되지
# 않은 동작(드물게 크래시)이 될 수 있다. 아래 계측은 그 자체로 수정이 아니라
# "재발 시 어느 스레드·어느 호출 경로가 원인인지 즉시 특정"하기 위한
# 진단 전용 장치 — 실행 경로·성능에 영향 없음(경고만 별도 파일에 기록).
_cross_thread_logger: Optional[logging.Logger] = None


def _get_cross_thread_logger() -> logging.Logger:
    global _cross_thread_logger
    if _cross_thread_logger is None:
        logger = logging.getLogger("CrossThreadGUI")
        logger.setLevel(logging.WARNING)
        os.makedirs("logs", exist_ok=True)
        handler = logging.FileHandler(
            os.path.join("logs", "cross_thread_gui.log"), encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
        _cross_thread_logger = logger
    return _cross_thread_logger

# 대시보드 레이어 → 파일 로거 레이어 매핑 (HEALTH는 전용 파일이 없어 SYSTEM으로 합류)
_FILE_LOGGER_LAYER = {
    "SYSTEM":   "SYSTEM",
    "SIGNAL":   "SIGNAL",
    "TRADE":    "TRADE",
    "LEARNING": "LEARNING",
    "DEBUG":    "DEBUG",
    "HEALTH":   "SYSTEM",
}


class LogEntry:
    __slots__ = ("ts", "layer", "level", "message", "created_at")

    def __init__(self, layer: str, level: str, message: str):
        now = datetime.datetime.now()
        self.ts      = now.strftime("%H:%M:%S")
        self.layer   = layer
        self.level   = level
        self.message = message
        self.created_at = now

    def __str__(self):
        return f"[{self.ts}] [{self.layer}] {self.message}"


class LogManager:
    """5층 로그 이벤트 버퍼 (대시보드 연동용)"""

    LAYERS = ["SYSTEM", "SIGNAL", "TRADE", "LEARNING", "DEBUG", "HEALTH"]
    MAX_ENTRIES = 200   # 레이어당 최대 보관

    def __init__(self):
        self._buffers: Dict[str, deque] = {
            layer: deque(maxlen=self.MAX_ENTRIES)
            for layer in self.LAYERS
        }
        self._callbacks: Dict[str, List[Callable]] = {
            layer: [] for layer in self.LAYERS
        }
        self._cross_thread_warned_at: Dict[str, float] = {}   # [302차] 스레드별 경고 쿨다운

    def log(self, layer: str, message: str, level: str = "INFO"):
        if layer not in self._buffers:
            return
        entry = LogEntry(layer, level, message)
        self._buffers[layer].append(entry)
        if self._callbacks[layer] and threading.current_thread() is not threading.main_thread():
            self._warn_cross_thread(layer)
        for cb in self._callbacks[layer]:
            cb(entry)
        self._write_to_file(layer, message, level)

    def _warn_cross_thread(self, layer: str) -> None:
        """[302차] 대시보드 콜백이 GUI(main) 스레드가 아닌 곳에서 실행되는
        경우를 기록 — 같은 스레드는 5초 쿨다운으로 스팸 방지."""
        try:
            th = threading.current_thread()
            now = datetime.datetime.now().timestamp()
            last = self._cross_thread_warned_at.get(th.name, 0.0)
            if now - last < 5.0:
                return
            self._cross_thread_warned_at[th.name] = now
            stack = "".join(traceback.format_stack(limit=15))
            _get_cross_thread_logger().warning(
                "GUI 콜백이 non-main 스레드에서 실행됨 — layer=%s thread=%s(daemon=%s)\n%s",
                layer, th.name, th.daemon, stack,
            )
        except Exception:
            pass

    def _write_to_file(self, layer: str, message: str, level: str) -> None:
        """대시보드 버퍼 전용이던 메시지를 파일 로거로도 남긴다 — 차단사유 등
        사후 추적이 필요한 신호가 .log 파일 grep으로도 확인되도록 한다."""
        file_layer = _FILE_LOGGER_LAYER.get(layer)
        if not file_layer:
            return
        try:
            lvl = getattr(logging, str(level or "INFO").upper(), logging.INFO)
            get_logger(file_layer).log(lvl, message)
        except Exception:
            pass

    # ── 편의 메서드 ────────────────────────────────────────────
    def system(self, msg: str, level: str = "INFO", **_kwargs):
        self.log("SYSTEM", msg, level)

    def signal(self, msg: str, level: str = "INFO", **_kwargs):
        # **_kwargs: 인자 추가 시 TypeError 방지 가드 (5/22 재발 방지)
        self.log("SIGNAL", msg, level)

    def trade(self, msg: str, level: str = "INFO", **_kwargs):
        self.log("TRADE", msg, level)

    def learning(self, msg: str):
        self.log("LEARNING", msg)

    def debug(self, msg: str):
        self.log("DEBUG", msg)

    def health(self, msg: str, level: str = "INFO"):
        self.log("HEALTH", msg, level)

    # ── 콜백 등록 (대시보드에서 사용) ─────────────────────────
    def subscribe(self, layer: str, callback: Callable):
        if layer in self._callbacks:
            self._callbacks[layer].append(callback)

    def get_recent(self, layer: str, n: int = 50) -> List[LogEntry]:
        buf = self._buffers.get(layer, deque())
        entries = list(buf)
        return entries[-n:]

    def get_all_recent(self, n: int = 20) -> List[LogEntry]:
        """전체 레이어 최근 N개 (시간순 정렬)"""
        all_entries = []
        for layer in self.LAYERS:
            all_entries.extend(list(self._buffers[layer]))
        all_entries.sort(key=lambda e: e.ts)
        return all_entries[-n:]

    def get_level_counts(self, since_sec: int = 600, layer: Optional[str] = None) -> Dict[str, int]:
        """최근 구간 레벨 카운트 집계 (기본 10분)."""
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=max(0, int(since_sec)))
        counts = {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}

        layers = [layer] if layer in self._buffers else list(self._buffers.keys())
        for lay in layers:
            for entry in self._buffers.get(lay, []):
                if getattr(entry, "created_at", cutoff) < cutoff:
                    continue
                lv = str(getattr(entry, "level", "INFO") or "INFO").upper()
                if lv == "WARN":
                    lv = "WARNING"
                if lv in counts:
                    counts[lv] += 1
        return counts


# 전역 싱글톤
log_manager = LogManager()
