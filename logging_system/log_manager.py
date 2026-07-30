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

# [304차 후속] 백그라운드 스레드(DailyClose, GBM 재학습, DB 라이터 등)에서 log()를
# 호출하면 구독 콜백(대시보드 append_*_log — QTextEdit 직접 조작)이 GUI 스레드 밖에서
# 실행된다. PyQt는 GUI 위젯을 GUI 스레드 밖에서 조작하면 정의되지 않은 동작(access
# violation)이 될 수 있음 — 0707·0708 daily_close 크래시 딥다이브에서 실측된 근본
# 원인 중 하나(_warn_cross_thread 계측이 302차부터 지목해왔으나 계측만 하고 실제
# 배선은 하지 않았던 부분). QueuedConnection으로 메인 스레드에 위임해 근본 해결한다.
try:
    from PyQt5.QtCore import QObject, pyqtSignal, Qt
    _HAS_QT = True
except Exception:
    _HAS_QT = False


if _HAS_QT:
    class _LogDispatchBridge(QObject):
        dispatch = pyqtSignal(str, object)

    _bridge = _LogDispatchBridge()
else:
    _bridge = None

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

# 대시보드 레이어 → 파일 로거 레이어 매핑
# [402차 후속7 P1-6] HEALTH → 전용 파일(YYYYMMDD_HEALTH.log)로 분리.
# 종전 "HEALTH → SYSTEM" 합류는 SYSTEM 로거의 _MaxLevelFilter를 타면서 헬스
# 타임라인을 SYSTEM.log(INFO)와 WARN.log(WARNING+) 두 파일로 쪼갰고, SYSTEM.log
# 쪽은 TickUI 55만 줄에 파묻혀 사후 추적이 사실상 불가능했다(2026-07-30 딥다이브).
# WARNING 이상은 utils/logger에서 WARN.log에도 계속 합류하므로 경보 가시성은 유지된다.
_FILE_LOGGER_LAYER = {
    "SYSTEM":   "SYSTEM",
    "SIGNAL":   "SIGNAL",
    "TRADE":    "TRADE",
    "LEARNING": "LEARNING",
    "DEBUG":    "DEBUG",
    "HEALTH":   "HEALTH",
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
        self._write_to_file(layer, message, level)
        if not self._callbacks[layer]:
            return
        if _bridge is not None and threading.current_thread() is not threading.main_thread():
            # [304차 후속] 대시보드 콜백은 GUI 위젯을 직접 건드리므로 메인 스레드로 위임
            self._warn_cross_thread(layer)
            _bridge.dispatch.emit(layer, entry)
        else:
            for cb in self._callbacks[layer]:
                cb(entry)

    def _dispatch_to_callbacks(self, layer: str, entry: "LogEntry") -> None:
        """[304차 후속] _bridge.dispatch(QueuedConnection)가 메인 스레드에서 호출하는 슬롯."""
        for cb in self._callbacks.get(layer, []):
            try:
                cb(entry)
            except Exception:
                pass

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

    def get_level_counts(
        self,
        since_sec: int = 600,
        layer: Optional[str] = None,
        exclude_prefixes: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """최근 구간 레벨 카운트 집계 (기본 10분).

        exclude_prefixes: 이 접두사로 시작하는 메시지(정책성 상태 통지 태그 등)는
        실제 예외가 아니므로 집계에서 제외한다.
        """
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=max(0, int(since_sec)))
        counts = {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
        prefixes = tuple(exclude_prefixes) if exclude_prefixes else ()

        layers = [layer] if layer in self._buffers else list(self._buffers.keys())
        for lay in layers:
            for entry in self._buffers.get(lay, []):
                if getattr(entry, "created_at", cutoff) < cutoff:
                    continue
                if prefixes and str(getattr(entry, "message", "")).startswith(prefixes):
                    continue
                lv = str(getattr(entry, "level", "INFO") or "INFO").upper()
                if lv == "WARN":
                    lv = "WARNING"
                if lv in counts:
                    counts[lv] += 1
        return counts


# 전역 싱글톤
log_manager = LogManager()

if _bridge is not None:
    # 모듈 최초 import(메인 스레드)에서 연결 — QueuedConnection이므로 emit()이 어느
    # 스레드에서 호출되든 슬롯은 반드시 메인 이벤트 루프에서 실행된다.
    _bridge.dispatch.connect(log_manager._dispatch_to_callbacks, Qt.QueuedConnection)
