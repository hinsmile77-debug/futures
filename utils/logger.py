# utils/logger.py — 5층 로그 시스템
"""
5층 로그 구조:
  Layer 1 (SYSTEM)   — 시스템 부팅·종료·Circuit Breaker (INFO 전용)
  Layer 2 (SIGNAL)   — 예측 신호·앙상블 결정
  Layer 3 (TRADE)    — 진입·청산 실행
  Layer 4 (LEARNING) — 자가학습·SHAP 교체
  Layer 5 (DEBUG)    — 피처·모델 상세 디버그
  Layer 6 (WARN)     — WARNING 이상 전용 경보 로그
"""
import logging
import logging.handlers
import os
from datetime import date

from config.settings import BASE_DIR, LOG_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


# ── 로거 이름 상수 ─────────────────────────────────────────────
LAYER_SYSTEM   = "SYSTEM"
LAYER_SIGNAL   = "SIGNAL"
LAYER_TRADE    = "TRADE"
LAYER_LEARNING = "LEARNING"
LAYER_DEBUG    = "DEBUG"
LAYER_WARN     = "WARN"     # WARNING 이상 전용 경보 파일

_initialized = False


class _MaxLevelFilter(logging.Filter):
    """지정 레벨 미만만 통과 — SYSTEM.log에서 WARNING 이상 제외."""
    def __init__(self, max_level: int):
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.max_level


def _log_file(layer: str) -> str:
    today = date.today().strftime("%Y%m%d")
    return os.path.join(LOG_DIR, f"{today}_{layer}.log")


def setup_logging():
    """로그 시스템 초기화 (1회만 호출)"""
    global _initialized
    if _initialized:
        return
    _initialized = True

    os.makedirs(LOG_DIR, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    layers = [LAYER_SYSTEM, LAYER_SIGNAL, LAYER_TRADE, LAYER_LEARNING, LAYER_DEBUG]

    for layer in layers:
        logger = logging.getLogger(layer)
        # DEBUG 레이어는 항상 DEBUG 레벨 — 다른 레이어는 settings.LOG_LEVEL 사용
        logger.setLevel(logging.DEBUG if layer == LAYER_DEBUG else LOG_LEVEL)
        logger.propagate = False

        # 파일 핸들러 (자정에 롤오버)
        fh = logging.handlers.TimedRotatingFileHandler(
            _log_file(layer), when="midnight", backupCount=30, encoding="utf-8"
        )
        fh.setFormatter(formatter)
        if layer == LAYER_SYSTEM:
            # SYSTEM.log는 INFO 이하만 — WARNING 이상은 WARN.log로 분리
            fh.addFilter(_MaxLevelFilter(logging.WARNING))
        logger.addHandler(fh)

    # SYSTEM 로거에 경보 파일 핸들러 추가 (WARNING 이상 → WARN.log)
    warn_fh = logging.handlers.TimedRotatingFileHandler(
        _log_file(LAYER_WARN), when="midnight", backupCount=30, encoding="utf-8"
    )
    warn_fh.setFormatter(formatter)
    warn_fh.setLevel(logging.WARNING)
    logging.getLogger(LAYER_SYSTEM).addHandler(warn_fh)

    # 루트 콘솔 핸들러 (SYSTEM·SIGNAL·TRADE만 콘솔 출력)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    for layer in [LAYER_SYSTEM, LAYER_SIGNAL, LAYER_TRADE]:
        logging.getLogger(layer).addHandler(console)


def get_logger(layer: str = LAYER_DEBUG) -> logging.Logger:
    """레이어 로거 반환"""
    if not _initialized:
        setup_logging()
    return logging.getLogger(layer)


# ── 편의 함수 ──────────────────────────────────────────────────
system   = lambda msg: get_logger(LAYER_SYSTEM).info(msg)
signal   = lambda msg: get_logger(LAYER_SIGNAL).info(msg)
trade    = lambda msg: get_logger(LAYER_TRADE).info(msg)
learning = lambda msg: get_logger(LAYER_LEARNING).info(msg)
debug    = lambda msg: get_logger(LAYER_DEBUG).debug(msg)
warn     = lambda msg: get_logger(LAYER_SYSTEM).warning(msg)
