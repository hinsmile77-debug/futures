# utils/db_utils.py — SQLite 공통 유틸리티
import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import List, Tuple, Any, Optional

from config.settings import PREDICTIONS_DB, SHAP_DB, TRADES_DB, DB_DIR

_lock = threading.Lock()


@contextmanager
def get_conn(db_path: str):
    """SQLite 연결 컨텍스트 매니저 (스레드 안전)"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute(db_path: str, sql: str, params: Tuple = ()):
    """단일 실행 (INSERT/UPDATE/DELETE)"""
    with _lock:
        with get_conn(db_path) as conn:
            conn.execute(sql, params)


def executemany(db_path: str, sql: str, param_list: List[Tuple]):
    """다수 행 일괄 실행"""
    with _lock:
        with get_conn(db_path) as conn:
            conn.executemany(sql, param_list)


def fetchall(db_path: str, sql: str, params: Tuple = ()) -> List[sqlite3.Row]:
    """SELECT 다수 행 반환"""
    with get_conn(db_path) as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall()


def fetchone(db_path: str, sql: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
    """SELECT 단일 행 반환"""
    with get_conn(db_path) as conn:
        cur = conn.execute(sql, params)
        return cur.fetchone()


# ── 테이블 초기화 ──────────────────────────────────────────────
def init_predictions_db():
    """예측 로그 테이블 생성"""
    sql = """
    CREATE TABLE IF NOT EXISTS predictions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ts          TEXT NOT NULL,
        horizon     TEXT NOT NULL,
        direction   INTEGER NOT NULL,
        confidence  REAL NOT NULL,
        actual      INTEGER,
        correct     INTEGER,
        features    TEXT,
        created_at  TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """
    execute(PREDICTIONS_DB, sql)

    # 인덱스
    execute(PREDICTIONS_DB,
            "CREATE INDEX IF NOT EXISTS idx_ts ON predictions(ts)")
    execute(PREDICTIONS_DB,
            "CREATE INDEX IF NOT EXISTS idx_horizon ON predictions(horizon)")


def init_trades_db():
    """매매 이력 테이블 생성"""
    sql = """
    CREATE TABLE IF NOT EXISTS trades (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_ts    TEXT NOT NULL,
        exit_ts     TEXT,
        direction   TEXT NOT NULL,
        entry_price REAL NOT NULL,
        exit_price  REAL,
        quantity    INTEGER NOT NULL,
        pnl_pts     REAL,
        pnl_krw     REAL,
        exit_reason TEXT,
        grade       TEXT,
        regime      TEXT,
        created_at  TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """
    execute(TRADES_DB, sql)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_entry_ts ON trades(entry_ts)")


def init_shap_db():
    """SHAP 기여도 누적 테이블 생성"""
    sql = """
    CREATE TABLE IF NOT EXISTS shap_scores (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ts          TEXT NOT NULL,
        feature     TEXT NOT NULL,
        shap_value  REAL NOT NULL,
        horizon     TEXT NOT NULL,
        created_at  TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """
    execute(SHAP_DB, sql)
    execute(SHAP_DB,
            "CREATE INDEX IF NOT EXISTS idx_feature ON shap_scores(feature)")


def init_all_dbs():
    """전체 DB 초기화 (main.py에서 1회 호출)"""
    init_predictions_db()
    init_trades_db()
    init_shap_db()
