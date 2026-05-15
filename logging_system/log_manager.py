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
from collections import deque
from typing import Dict, List, Callable, Optional


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

    def log(self, layer: str, message: str, level: str = "INFO"):
        if layer not in self._buffers:
            return
        entry = LogEntry(layer, level, message)
        self._buffers[layer].append(entry)
        for cb in self._callbacks[layer]:
            cb(entry)

    # ── 편의 메서드 ────────────────────────────────────────────
    def system(self, msg: str, level: str = "INFO"):
        self.log("SYSTEM", msg, level)

    def signal(self, msg: str):
        self.log("SIGNAL", msg)

    def trade(self, msg: str, level: str = "INFO"):
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
