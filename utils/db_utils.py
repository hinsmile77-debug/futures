# utils/db_utils.py — SQLite 공통 유틸리티
import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import List, Tuple, Any, Optional

import json
from config.settings import PREDICTIONS_DB, SHAP_DB, TRADES_DB, RAW_DATA_DB, DB_DIR

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


def init_raw_data_db():
    """분봉 원본 + 피처 저장 테이블 — 경로 B 학습 데이터 축적용"""
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS raw_candles (
            ts         TEXT PRIMARY KEY,
            open       REAL NOT NULL,
            high       REAL NOT NULL,
            low        REAL NOT NULL,
            close      REAL NOT NULL,
            volume     INTEGER NOT NULL,
            bid1       REAL,
            ask1       REAL,
            oi         INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS raw_features (
            ts         TEXT PRIMARY KEY,
            features   TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)


def save_candle(candle: dict) -> None:
    """분봉 확정 시 raw_candles에 저장."""
    ts_raw = candle.get("ts")
    ts = ts_raw.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts_raw, "strftime") else str(ts_raw)
    execute(
        RAW_DATA_DB,
        """INSERT OR REPLACE INTO raw_candles
           (ts, open, high, low, close, volume, bid1, ask1, oi)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            ts,
            candle.get("open",   0.0),
            candle.get("high",   0.0),
            candle.get("low",    0.0),
            candle.get("close",  0.0),
            candle.get("volume", 0),
            candle.get("bid1"),
            candle.get("ask1"),
            candle.get("oi"),
        ),
    )


def save_features(ts: str, features: dict) -> None:
    """피처 벡터를 raw_features에 저장."""
    execute(
        RAW_DATA_DB,
        "INSERT OR REPLACE INTO raw_features (ts, features) VALUES (?, ?)",
        (ts, json.dumps(features, ensure_ascii=False)),
    )


def get_candle_close(ts: str) -> Optional[float]:
    """ts 시각의 종가 반환 — actual 라벨 계산용."""
    row = fetchone(RAW_DATA_DB, "SELECT close FROM raw_candles WHERE ts = ?", (ts,))
    return float(row["close"]) if row else None


def count_raw_candles() -> int:
    """누적 분봉 수 반환."""
    row = fetchone(RAW_DATA_DB, "SELECT COUNT(*) AS cnt FROM raw_candles")
    return row["cnt"] if row else 0


def fetch_pnl_history(limit_days: int = 90) -> List[sqlite3.Row]:
    """최근 N일 체결 완료 거래 전체 반환 — 손익 추이 패널용.
    반환 컬럼: direction, entry_price, exit_price, quantity, pnl_pts, pnl_krw,
               exit_reason, grade, entry_ts, exit_ts
    """
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=limit_days)).isoformat()
    return fetchall(
        TRADES_DB,
        """SELECT direction, entry_price, exit_price, quantity,
                  pnl_pts, pnl_krw, exit_reason, grade, entry_ts, exit_ts
           FROM trades
           WHERE exit_ts IS NOT NULL AND entry_ts >= ?
           ORDER BY entry_ts ASC""",
        (cutoff + " 00:00:00",),
    )


def fetch_today_trades(today_str: str) -> List[sqlite3.Row]:
    """당일 체결 완료 거래 목록 (entry_ts LIKE today_str%).
    반환 컬럼: direction, entry_price, exit_price, quantity, pnl_pts, pnl_krw,
               exit_reason, grade, entry_ts, exit_ts
    """
    return fetchall(
        TRADES_DB,
        """SELECT direction, entry_price, exit_price, quantity,
                  pnl_pts, pnl_krw, exit_reason, grade, entry_ts, exit_ts
           FROM trades
           WHERE entry_ts LIKE ?
           ORDER BY entry_ts ASC""",
        (today_str + "%",),
    )


def init_all_dbs():
    """전체 DB 초기화 (main.py에서 1회 호출)"""
    init_predictions_db()
    init_trades_db()
    init_shap_db()
    init_raw_data_db()
