# model/scaler_monitor_db.py
# 섹션 8: 스케일러 상태 모니터 DB — scaler_monitor.db
#
# 테이블:
#   scaler_events — 분봉 단위 호라이즌별 실시간 이벤트
#   scaler_daily  — 일별 EOD 집계
import json
import os
import sqlite3
import logging
from typing import List, Optional

from config.settings import SCALER_MONITOR_DB

logger = logging.getLogger("SIGNAL")

_DDL = """
CREATE TABLE IF NOT EXISTS scaler_events (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    ts             TEXT NOT NULL,
    date           TEXT NOT NULL,
    horizon        TEXT NOT NULL,
    fitted_at      TEXT,
    age_minutes    REAL,
    max_z          REAL,
    max_z_feature  TEXT,
    extreme_count  INTEGER DEFAULT 0,
    raw_value      REAL,
    pre_value      REAL,
    scaler_mean    REAL,
    scaler_std     REAL,
    refresh_type   TEXT,
    refresh_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_se_date ON scaler_events(date, ts);

CREATE TABLE IF NOT EXISTS scaler_daily (
    date             TEXT PRIMARY KEY,
    max_age_minutes  REAL,
    total_extreme    INTEGER,
    top_extreme_feat TEXT,
    refresh_count    INTEGER,
    refresh_types    TEXT,
    grade_x_minutes  INTEGER,
    cb3_triggered    INTEGER DEFAULT 0,
    note             TEXT
);
"""


def init_db() -> None:
    """DB 파일 생성 + 스키마 초기화 (멱등). 기존 DB에 신규 컬럼 자동 마이그레이션."""
    os.makedirs(os.path.dirname(SCALER_MONITOR_DB), exist_ok=True)
    with sqlite3.connect(SCALER_MONITOR_DB, timeout=10) as c:
        c.executescript(_DDL)
        existing = {r[1] for r in c.execute("PRAGMA table_info(scaler_events)").fetchall()}
        for col, typedef in [
            ("raw_value",   "REAL"),
            ("pre_value",   "REAL"),
            ("scaler_mean", "REAL"),
            ("scaler_std",  "REAL"),
        ]:
            if col not in existing:
                c.execute("ALTER TABLE scaler_events ADD COLUMN %s %s" % (col, typedef))
        c.commit()


def insert_events_batch(rows: List[dict]) -> None:
    """호라이즌별 분봉 이벤트 일괄 INSERT.

    rows: list of dicts — keys:
        ts, date, horizon, fitted_at, age_minutes,
        max_z, max_z_feature, extreme_count,
        raw_value, pre_value, scaler_mean, scaler_std
    """
    if not rows:
        return
    try:
        with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
            c.executemany(
                """INSERT INTO scaler_events
                   (ts, date, horizon, fitted_at, age_minutes,
                    max_z, max_z_feature, extreme_count,
                    raw_value, pre_value, scaler_mean, scaler_std)
                   VALUES
                   (:ts, :date, :horizon, :fitted_at, :age_minutes,
                    :max_z, :max_z_feature, :extreme_count,
                    :raw_value, :pre_value, :scaler_mean, :scaler_std)""",
                rows,
            )
            c.commit()
    except Exception as _e:
        logger.debug("[ScalerMonitorDB] insert_events_batch 실패: %s", _e)


def update_event_refresh(ts: str, refresh_type: str, refresh_reason: str) -> None:
    """해당 ts 의 모든 호라이즌 행에 refresh 정보 UPDATE.

    Phase B 트리거 스레드가 refit 완료 후 호출.
    """
    try:
        with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
            c.execute(
                "UPDATE scaler_events SET refresh_type=?, refresh_reason=? WHERE ts=?",
                (refresh_type, refresh_reason, ts),
            )
            c.commit()
    except Exception as _e:
        logger.debug("[ScalerMonitorDB] update_event_refresh 실패: %s", _e)


def aggregate_daily(date_str: str) -> dict:
    """date_str 의 scaler_events 집계 → scaler_daily INSERT 용 dict 반환.

    Returns:
        max_age_minutes, total_extreme, top_extreme_feat,
        refresh_count, refresh_types (JSON list)
    """
    try:
        with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
            max_age = c.execute(
                "SELECT MAX(age_minutes) FROM scaler_events WHERE date=?",
                (date_str,),
            ).fetchone()[0] or 0.0

            total_extreme = c.execute(
                "SELECT COALESCE(SUM(extreme_count),0) FROM scaler_events WHERE date=?",
                (date_str,),
            ).fetchone()[0]

            top_row = c.execute(
                """SELECT max_z_feature, COUNT(*) AS cnt
                   FROM scaler_events
                   WHERE date=? AND extreme_count > 0
                   GROUP BY max_z_feature
                   ORDER BY cnt DESC LIMIT 1""",
                (date_str,),
            ).fetchone()
            top_feat = top_row[0] if top_row else ""

            refresh_rows = c.execute(
                """SELECT DISTINCT ts, refresh_type
                   FROM scaler_events
                   WHERE date=? AND refresh_type IS NOT NULL""",
                (date_str,),
            ).fetchall()
    except Exception as _e:
        logger.debug("[ScalerMonitorDB] aggregate_daily 실패: %s", _e)
        return {}

    refresh_ts_set = set(r[0] for r in refresh_rows)
    refresh_types  = sorted(set(r[1] for r in refresh_rows if r[1]))
    return {
        "max_age_minutes":  round(float(max_age), 1),
        "total_extreme":    int(total_extreme),
        "top_extreme_feat": top_feat,
        "refresh_count":    len(refresh_ts_set),
        "refresh_types":    json.dumps(refresh_types),
    }


def insert_daily(
    date_str: str,
    stats: dict,
    grade_x_minutes: int = 0,
    cb3_triggered: int = 0,
    note: str = "",
) -> None:
    """scaler_daily 일별 집계 INSERT OR REPLACE."""
    try:
        with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
            c.execute(
                """INSERT OR REPLACE INTO scaler_daily
                   (date, max_age_minutes, total_extreme, top_extreme_feat,
                    refresh_count, refresh_types, grade_x_minutes, cb3_triggered, note)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    date_str,
                    stats.get("max_age_minutes", 0.0),
                    stats.get("total_extreme", 0),
                    stats.get("top_extreme_feat", ""),
                    stats.get("refresh_count", 0),
                    stats.get("refresh_types", "[]"),
                    grade_x_minutes,
                    cb3_triggered,
                    note,
                ),
            )
            c.commit()
        logger.info(
            "[ScalerMonitor] EOD 일별 집계 저장 | date=%s age=%.0fm extreme=%d refresh=%d grade_x=%d cb3=%d",
            date_str,
            stats.get("max_age_minutes", 0.0),
            stats.get("total_extreme", 0),
            stats.get("refresh_count", 0),
            grade_x_minutes,
            cb3_triggered,
        )
    except Exception as _e:
        logger.debug("[ScalerMonitorDB] insert_daily 실패: %s", _e)
