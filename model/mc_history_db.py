# model/mc_history_db.py — 동적 min_conf 변경 이력 DB
"""
mc_history.db: GBM 재학습 / 매일 08:55 워밍업 시 변경된 min_conf 이력 저장.
DynamicMcPanel이 금일 추이 및 이력을 조회한다.

Python 3.7 32-bit 호환
"""
import logging
import os
import sqlite3
from typing import Dict, List, Optional

from config.settings import DB_DIR

logger = logging.getLogger("LEARNING")

MC_HISTORY_DB = os.path.join(DB_DIR, "mc_history.db")

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS mc_history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT    NOT NULL,
    trigger   TEXT    NOT NULL,
    base_mc   REAL    NOT NULL,
    zone      TEXT    NOT NULL,
    old_mc    REAL    NOT NULL,
    new_mc    REAL    NOT NULL,
    conf_avg  REAL,
    conf_p65  REAL,
    n_samples INTEGER
);
CREATE INDEX IF NOT EXISTS idx_mc_ts ON mc_history(ts);
"""


def init_db() -> None:
    with sqlite3.connect(MC_HISTORY_DB, timeout=10) as conn:
        conn.executescript(_CREATE_SQL)


def insert_mc_change(
    ts: str,
    trigger: str,
    base_mc: float,
    zone_changes: Dict[str, tuple],   # {zone: (old_mc, new_mc)}
    conf_avg: Optional[float] = None,
    conf_p65: Optional[float] = None,
    n_samples: Optional[int] = None,
) -> None:
    """
    zone_changes: {"STABLE_TREND": (0.54, 0.67), "OPEN_VOLATILE": (0.60, 0.69), ...}
    """
    try:
        init_db()
        rows = [
            (ts, trigger, base_mc, zone, old, new, conf_avg, conf_p65, n_samples)
            for zone, (old, new) in zone_changes.items()
        ]
        with sqlite3.connect(MC_HISTORY_DB, timeout=10) as conn:
            conn.executemany(
                """INSERT INTO mc_history
                   (ts,trigger,base_mc,zone,old_mc,new_mc,conf_avg,conf_p65,n_samples)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                rows,
            )
        logger.info(
            "[DynMC] mc 변경 기록 trigger=%s base=%.3f zones=%d개",
            trigger, base_mc, len(zone_changes),
        )
    except Exception as exc:
        logger.warning("[DynMC] mc 이력 저장 실패: %s", exc)


def get_today_history(date_str: str) -> List[dict]:
    """금일 mc 변경 이력 반환."""
    try:
        init_db()
        with sqlite3.connect(MC_HISTORY_DB, timeout=10) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM mc_history WHERE ts >= ? AND ts < ? ORDER BY ts",
                (date_str, date_str + "Z"),
            ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_recent_history(limit: int = 100) -> List[dict]:
    """최근 N건 이력 반환 (패널 이력 탭용)."""
    try:
        init_db()
        with sqlite3.connect(MC_HISTORY_DB, timeout=10) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM mc_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
