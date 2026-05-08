# utils/db_utils.py — SQLite 공통 유틸리티
import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import List, Tuple, Any, Optional, Dict

import json
from config.constants import FUTURES_PT_VALUE
from config.settings import PREDICTIONS_DB, SHAP_DB, TRADES_DB, RAW_DATA_DB, DB_DIR
from config.settings import FUTURES_COMMISSION_RATE

_lock = threading.Lock()
TRADE_PNL_FORMULA_VERSION = 2


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


def normalize_trade_pnl(entry_price: float, quantity: int, pnl_pts: float) -> Dict[str, float]:
    """현재 기준(250,000원/pt - 왕복 수수료)으로 거래 손익을 정규화한다."""
    entry_price_f = float(entry_price or 0.0)
    quantity_i = max(int(quantity or 0), 0)
    pnl_pts_f = float(pnl_pts or 0.0)
    gross_pnl_krw = pnl_pts_f * FUTURES_PT_VALUE * quantity_i
    commission_krw = entry_price_f * quantity_i * FUTURES_PT_VALUE * FUTURES_COMMISSION_RATE * 2
    net_pnl_krw = gross_pnl_krw - commission_krw
    return {
        "gross_pnl_krw": round(gross_pnl_krw, 0),
        "commission_krw": round(commission_krw, 0),
        "net_pnl_krw": round(net_pnl_krw, 0),
        "formula_version": TRADE_PNL_FORMULA_VERSION,
    }


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
        up_prob     REAL,
        down_prob   REAL,
        flat_prob   REAL,
        actual      INTEGER,
        correct     INTEGER,
        features    TEXT,
        created_at  TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """
    execute(PREDICTIONS_DB, sql)
    _migrate_predictions_db()

    # 인덱스
    execute(PREDICTIONS_DB,
            "CREATE INDEX IF NOT EXISTS idx_ts ON predictions(ts)")
    execute(PREDICTIONS_DB,
            "CREATE INDEX IF NOT EXISTS idx_horizon ON predictions(horizon)")
    execute(
        PREDICTIONS_DB,
        """
        CREATE TABLE IF NOT EXISTS ensemble_decisions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            ts             TEXT NOT NULL,
            regime         TEXT,
            micro_regime   TEXT,
            direction      INTEGER NOT NULL,
            confidence     REAL NOT NULL,
            up_score       REAL,
            down_score     REAL,
            flat_score     REAL,
            grade          TEXT,
            auto_entry     INTEGER,
            regime_ok      INTEGER,
            min_conf       REAL,
            gate_reason    TEXT,
            gate_strength  REAL,
            gate_delta     REAL,
            gate_blocked   INTEGER,
            gate_signals   TEXT,
            detail         TEXT,
            features       TEXT,
            created_at     TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """,
    )
    _migrate_ensemble_decisions_db()
    execute(PREDICTIONS_DB,
            "CREATE INDEX IF NOT EXISTS idx_ensemble_ts ON ensemble_decisions(ts)")
    execute(
        PREDICTIONS_DB,
        """
        CREATE TABLE IF NOT EXISTS meta_labels (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            ts               TEXT NOT NULL,
            horizon          TEXT NOT NULL,
            predicted        INTEGER NOT NULL,
            actual           INTEGER NOT NULL,
            confidence       REAL NOT NULL,
            up_prob          REAL,
            down_prob        REAL,
            flat_prob        REAL,
            target_close     REAL,
            future_close     REAL,
            realized_move    REAL,
            threshold_move   REAL,
            meta_action      TEXT NOT NULL,
            meta_score       REAL NOT NULL,
            features         TEXT,
            created_at       TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """,
    )
    execute(PREDICTIONS_DB,
            "CREATE INDEX IF NOT EXISTS idx_meta_ts ON meta_labels(ts)")
    execute(PREDICTIONS_DB,
            "CREATE INDEX IF NOT EXISTS idx_meta_horizon ON meta_labels(horizon)")


def _migrate_predictions_db():
    """Backfill newly introduced probability columns on existing DBs."""
    with _lock:
        with get_conn(PREDICTIONS_DB) as conn:
            cols = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(predictions)").fetchall()
            }
            for name in ("up_prob", "down_prob", "flat_prob"):
                if name not in cols:
                    conn.execute(f"ALTER TABLE predictions ADD COLUMN {name} REAL")
            conn.execute(
                """
                UPDATE predictions
                SET
                    up_prob = CASE
                        WHEN up_prob IS NOT NULL THEN up_prob
                        WHEN direction = 1 THEN confidence
                        WHEN direction = -1 THEN (1.0 - confidence) / 2.0
                        ELSE (1.0 - confidence) / 2.0
                    END,
                    down_prob = CASE
                        WHEN down_prob IS NOT NULL THEN down_prob
                        WHEN direction = -1 THEN confidence
                        WHEN direction = 1 THEN (1.0 - confidence) / 2.0
                        ELSE (1.0 - confidence) / 2.0
                    END,
                    flat_prob = CASE
                        WHEN flat_prob IS NOT NULL THEN flat_prob
                        WHEN direction = 0 THEN confidence
                        ELSE (1.0 - confidence) / 2.0
                    END
                WHERE up_prob IS NULL OR down_prob IS NULL OR flat_prob IS NULL
                """
            )


def _migrate_ensemble_decisions_db():
    """Ensure adaptive/meta gate telemetry columns exist on older DBs."""
    with _lock:
        with get_conn(PREDICTIONS_DB) as conn:
            cols = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(ensemble_decisions)").fetchall()
            }
            additions = {
                "meta_action": "TEXT",
                "meta_confidence": "REAL",
                "meta_size_mult": "REAL",
                "meta_reason": "TEXT",
                "toxicity_action": "TEXT",
                "toxicity_score": "REAL",
                "toxicity_score_ma": "REAL",
                "toxicity_size_mult": "REAL",
                "toxicity_reason": "TEXT",
            }
            for name, dtype in additions.items():
                if name not in cols:
                    conn.execute(
                        f"ALTER TABLE ensemble_decisions ADD COLUMN {name} {dtype}"
                    )


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
    _migrate_trades_db()
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_entry_ts ON trades(entry_ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_exit_ts ON trades(exit_ts)")


def _migrate_trades_db():
    """거래 테이블에 정규화 PnL 컬럼을 보강하고 기존 혼합 데이터를 현재 공식으로 통일."""
    with _lock:
        with get_conn(TRADES_DB) as conn:
            cols = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(trades)").fetchall()
            }
            additions = {
                "gross_pnl_krw": "REAL",
                "commission_krw": "REAL",
                "net_pnl_krw": "REAL",
                "formula_version": "INTEGER",
            }
            for name, dtype in additions.items():
                if name not in cols:
                    conn.execute(f"ALTER TABLE trades ADD COLUMN {name} {dtype}")

            rows = conn.execute(
                """SELECT id, entry_price, quantity, pnl_pts, formula_version
                   FROM trades
                   WHERE pnl_pts IS NOT NULL"""
            ).fetchall()
            for row in rows:
                metrics = normalize_trade_pnl(
                    entry_price=row["entry_price"],
                    quantity=row["quantity"],
                    pnl_pts=row["pnl_pts"],
                )
                current_version = int(row["formula_version"] or 0)
                if current_version == TRADE_PNL_FORMULA_VERSION:
                    continue
                conn.execute(
                    """UPDATE trades
                       SET gross_pnl_krw = ?,
                           commission_krw = ?,
                           net_pnl_krw = ?,
                           pnl_krw = ?,
                           formula_version = ?
                       WHERE id = ?""",
                    (
                        metrics["gross_pnl_krw"],
                        metrics["commission_krw"],
                        metrics["net_pnl_krw"],
                        metrics["net_pnl_krw"],
                        metrics["formula_version"],
                        row["id"],
                    ),
                )


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
                  pnl_pts,
                  COALESCE(net_pnl_krw, pnl_krw) AS pnl_krw,
                  gross_pnl_krw, commission_krw, formula_version,
                  exit_reason, grade, entry_ts, exit_ts
           FROM trades
           WHERE exit_ts IS NOT NULL AND exit_ts >= ?
           ORDER BY exit_ts ASC""",
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
                  pnl_pts,
                  COALESCE(net_pnl_krw, pnl_krw) AS pnl_krw,
                  gross_pnl_krw, commission_krw, formula_version,
                  exit_reason, grade, entry_ts, exit_ts
           FROM trades
           WHERE exit_ts LIKE ?
           ORDER BY exit_ts ASC""",
        (today_str + "%",),
    )


def fetch_calibration_bins(days_back: int = 30) -> List[sqlite3.Row]:
    """신뢰도 캘리브레이션 — confidence 구간별 실제 적중률.
    반환: conf_bin(5단위), cnt, accuracy
    """
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days_back)).isoformat()
    return fetchall(
        PREDICTIONS_DB,
        """SELECT (CAST(confidence * 20 AS INTEGER) * 5) AS conf_bin,
                  COUNT(*) AS cnt,
                  ROUND(AVG(CAST(correct AS FLOAT)), 4) AS accuracy
           FROM predictions
           WHERE actual IS NOT NULL AND ts >= ?
           GROUP BY conf_bin
           ORDER BY conf_bin""",
        (cutoff + " 00:00:00",),
    )


def fetch_grade_stats() -> List[sqlite3.Row]:
    """등급별 매매 성과 — A/B/C/? 등급 vs 건수/승률/평균PnL/합계PnL.
    반환: grade, cnt, win_rate, avg_pnl, total_pnl
    """
    return fetchall(
        TRADES_DB,
        """SELECT COALESCE(NULLIF(grade, ''), '?') AS grade,
                  COUNT(*) AS cnt,
                  ROUND(AVG(CASE WHEN pnl_pts > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
                  ROUND(AVG(pnl_pts), 4) AS avg_pnl,
                  ROUND(SUM(pnl_pts), 4) AS total_pnl
           FROM trades
           WHERE exit_ts IS NOT NULL
           GROUP BY grade
           ORDER BY grade""",
    )


def fetch_regime_stats() -> List[sqlite3.Row]:
    """레짐별 매매 성과 — RISK_ON/NEUTRAL/RISK_OFF vs 승률/평균PnL.
    반환: regime, cnt, win_rate, avg_pnl
    """
    return fetchall(
        TRADES_DB,
        """SELECT COALESCE(NULLIF(regime, ''), 'NEUTRAL') AS regime,
                  COUNT(*) AS cnt,
                  ROUND(AVG(CASE WHEN pnl_pts > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
                  ROUND(AVG(pnl_pts), 4) AS avg_pnl
           FROM trades
           WHERE exit_ts IS NOT NULL
           GROUP BY regime
           ORDER BY regime""",
    )


def fetch_accuracy_history(limit: int = 100) -> List[sqlite3.Row]:
    """최근 N개 예측의 정확도 이력 — 학습 성장 곡선용.
    반환: ts, correct (0/1)
    """
    return fetchall(
        PREDICTIONS_DB,
        """SELECT ts, correct
           FROM predictions
           WHERE actual IS NOT NULL AND correct IS NOT NULL
           ORDER BY ts DESC
           LIMIT ?""",
        (limit,),
    )


def init_daily_stats_db():
    """일일 스냅샷 테이블 생성 (trades.db 에 함께 저장)"""
    execute(TRADES_DB, """
        CREATE TABLE IF NOT EXISTS daily_stats (
            date           TEXT PRIMARY KEY,
            trades         INTEGER DEFAULT 0,
            wins           INTEGER DEFAULT 0,
            pnl_pts        REAL    DEFAULT 0.0,
            pnl_krw        REAL    DEFAULT 0.0,
            sgd_accuracy   REAL    DEFAULT 0.5,
            verified_count INTEGER DEFAULT 0,
            created_at     TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)


def save_daily_stats(date_str: str, stats: dict) -> None:
    """일일 마감 통계 저장 — daily_close() 에서 호출."""
    execute(TRADES_DB, """
        INSERT OR REPLACE INTO daily_stats
            (date, trades, wins, pnl_pts, pnl_krw, sgd_accuracy, verified_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date_str,
        int(stats.get("trades",        0)),
        int(stats.get("wins",          0)),
        float(stats.get("pnl_pts",     0.0)),
        float(stats.get("pnl_krw",     0.0)),
        float(stats.get("sgd_accuracy",0.5)),
        int(stats.get("verified_count",0)),
    ))


def fetch_trend_daily(days_back: int = 30) -> List[dict]:
    """일별 집계 (최대 30일). trades.db 체결 + daily_stats 정확도 병합."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days_back)).isoformat()
    rows = fetchall(TRADES_DB, """
        SELECT date(entry_ts)  AS date,
               COUNT(*)        AS trades,
               SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN pnl_pts > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(pnl_krw), 0) AS pnl_krw
        FROM trades
        WHERE exit_ts IS NOT NULL AND entry_ts >= ?
        GROUP BY date(entry_ts)
        ORDER BY date(entry_ts) DESC
        LIMIT 30
    """, (cutoff,))
    acc_map = {
        r["date"]: (r["sgd_accuracy"], r["verified_count"])
        for r in fetchall(TRADES_DB,
            "SELECT date, sgd_accuracy, verified_count FROM daily_stats WHERE date >= ?",
            (cutoff,))
    }
    result = []
    for row in rows:
        d = dict(row)
        acc, vc = acc_map.get(d["date"], (None, 0))
        d["sgd_accuracy"]   = acc
        d["verified_count"] = vc
        result.append(d)
    return result


def fetch_trend_weekly(weeks_back: int = 12) -> List[dict]:
    """주별 집계 (최대 12주)."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(weeks=weeks_back)).isoformat()
    return [dict(r) for r in fetchall(TRADES_DB, """
        SELECT strftime('%Y-W%W', entry_ts) AS week,
               COUNT(*)        AS trades,
               SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN pnl_pts > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(pnl_krw), 0) AS pnl_krw
        FROM trades
        WHERE exit_ts IS NOT NULL AND entry_ts >= ?
        GROUP BY strftime('%Y-W%W', entry_ts)
        ORDER BY week DESC
        LIMIT 12
    """, (cutoff,))]


def fetch_trend_monthly(months_back: int = 12) -> List[dict]:
    """월별 집계 (최대 12개월)."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=months_back * 31)).isoformat()
    return [dict(r) for r in fetchall(TRADES_DB, """
        SELECT strftime('%Y-%m', entry_ts) AS month,
               COUNT(*)        AS trades,
               SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN pnl_pts > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(pnl_krw), 0) AS pnl_krw
        FROM trades
        WHERE exit_ts IS NOT NULL AND entry_ts >= ?
        GROUP BY strftime('%Y-%m', entry_ts)
        ORDER BY month DESC
        LIMIT 12
    """, (cutoff,))]


def fetch_trend_yearly() -> List[dict]:
    """연간 집계 (전체)."""
    return [dict(r) for r in fetchall(TRADES_DB, """
        SELECT strftime('%Y', entry_ts) AS year,
               COUNT(*)        AS trades,
               SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN pnl_pts > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(pnl_krw), 0) AS pnl_krw
        FROM trades
        WHERE exit_ts IS NOT NULL
        GROUP BY strftime('%Y', entry_ts)
        ORDER BY year DESC
    """)]


def init_all_dbs():
    """전체 DB 초기화 (main.py에서 1회 호출)"""
    init_predictions_db()
    init_trades_db()
    init_daily_stats_db()
    init_shap_db()
    init_raw_data_db()
