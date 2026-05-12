# challenger/challenger_db.py — SQLite CRUD (challenger.db)
"""
챔피언-도전자 전용 SQLite DB.

테이블:
  challenger_signals       — 매분 신호 로그 (regime 포함)
  challenger_trades        — 가상 거래 (regime 포함)
  challenger_daily_metrics — 전체 일별 집계
  challenger_regime_metrics— 레짐별 누적 집계 (핵심 신규)
  regime_rank_history      — 레짐별 1위 변경 이력 (WARNING 판단용)
  champion_history         — 챔피언 교체 이력
"""
import os
import json
import sqlite3
import logging
from typing import Optional, List, Dict, Any

from config.settings import DB_DIR

logger = logging.getLogger("CHALLENGER")

CHALLENGER_DB_PATH = os.path.join(DB_DIR, "challenger.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS challenger_signals (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT    NOT NULL,
    challenger_id TEXT    NOT NULL,
    direction     INTEGER NOT NULL,
    confidence    REAL    NOT NULL,
    grade         TEXT    NOT NULL,
    entry_price   REAL,
    signal_meta   TEXT,
    regime        TEXT    DEFAULT '혼합'
);
CREATE INDEX IF NOT EXISTS idx_cs_ts_id  ON challenger_signals(ts, challenger_id);
CREATE INDEX IF NOT EXISTS idx_cs_regime ON challenger_signals(challenger_id, regime);

CREATE TABLE IF NOT EXISTS challenger_trades (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    challenger_id   TEXT    NOT NULL,
    entry_ts        TEXT    NOT NULL,
    exit_ts         TEXT,
    direction       INTEGER NOT NULL,
    entry_price     REAL    NOT NULL,
    exit_price      REAL,
    pnl_pt          REAL,
    exit_reason     TEXT,
    grade           TEXT,
    regime          TEXT    DEFAULT '혼합'
);
CREATE INDEX IF NOT EXISTS idx_ct_id     ON challenger_trades(challenger_id, entry_ts);
CREATE INDEX IF NOT EXISTS idx_ct_regime ON challenger_trades(challenger_id, regime);

CREATE TABLE IF NOT EXISTS challenger_daily_metrics (
    date            TEXT NOT NULL,
    challenger_id   TEXT NOT NULL,
    signal_count    INTEGER DEFAULT 0,
    trade_count     INTEGER DEFAULT 0,
    win_count       INTEGER DEFAULT 0,
    win_rate        REAL    DEFAULT 0.0,
    total_pnl_pt    REAL    DEFAULT 0.0,
    mdd_pt          REAL    DEFAULT 0.0,
    sharpe          REAL    DEFAULT 0.0,
    cum_pnl_pt      REAL    DEFAULT 0.0,
    cum_mdd_pt      REAL    DEFAULT 0.0,
    PRIMARY KEY (date, challenger_id)
);

CREATE TABLE IF NOT EXISTS challenger_regime_metrics (
    challenger_id   TEXT NOT NULL,
    regime          TEXT NOT NULL,
    trade_count     INTEGER DEFAULT 0,
    win_count       INTEGER DEFAULT 0,
    win_rate        REAL    DEFAULT 0.0,
    total_pnl_pt    REAL    DEFAULT 0.0,
    mdd_pt          REAL    DEFAULT 0.0,
    sharpe          REAL    DEFAULT 0.0,
    last_updated    TEXT,
    PRIMARY KEY (challenger_id, regime)
);

CREATE TABLE IF NOT EXISTS regime_rank_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    regime      TEXT NOT NULL,
    rank_1_id   TEXT,
    rank_2_id   TEXT,
    rank_3_id   TEXT,
    prev_rank_1 TEXT,
    changed     INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_rrh_regime ON regime_rank_history(regime, ts);

CREATE TABLE IF NOT EXISTS champion_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    promoted_ts     TEXT NOT NULL,
    from_champion   TEXT NOT NULL,
    to_champion     TEXT NOT NULL,
    reason          TEXT,
    regime          TEXT DEFAULT 'GLOBAL',
    obs_days        INTEGER,
    win_rate_delta  REAL,
    mdd_delta       REAL
);
"""

# 기존 DB에 컬럼/테이블이 없을 경우 추가하는 마이그레이션
_MIGRATIONS = [
    "ALTER TABLE challenger_signals ADD COLUMN regime TEXT DEFAULT '혼합'",
    "ALTER TABLE challenger_trades  ADD COLUMN regime TEXT DEFAULT '혼합'",
    "ALTER TABLE champion_history   ADD COLUMN regime TEXT DEFAULT 'GLOBAL'",
]


class ChallengerDB(object):
    """SQLite CRUD 래퍼"""

    def __init__(self, db_path=None):
        self._path = db_path or CHALLENGER_DB_PATH
        self._ensure_dir()
        self._init_schema()
        self._migrate()

    def _ensure_dir(self):
        d = os.path.dirname(self._path)
        if d and not os.path.exists(d):
            os.makedirs(d)

    def _conn(self):
        conn = sqlite3.connect(self._path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._conn() as conn:
            conn.executescript(_SCHEMA)

    def _migrate(self):
        """기존 DB에 신규 컬럼/테이블 추가 (이미 있으면 무시)"""
        with self._conn() as conn:
            for sql in _MIGRATIONS:
                try:
                    conn.execute(sql)
                except Exception:
                    pass  # 이미 컬럼 존재 시 무시

    # ── 신호 로그 ─────────────────────────────────────────────────

    def insert_signal(self, sig, regime="혼합"):
        # type: (Any, str) -> None
        sql = """
        INSERT INTO challenger_signals
            (ts, challenger_id, direction, confidence, grade, entry_price, signal_meta, regime)
        VALUES (?,?,?,?,?,?,?,?)
        """
        meta_json = json.dumps(sig.signal_meta, ensure_ascii=False) if sig.signal_meta else None
        with self._conn() as conn:
            conn.execute(sql, (
                sig.ts, sig.challenger_id, sig.direction,
                sig.confidence, sig.grade, sig.entry_price, meta_json, regime,
            ))

    # ── 가상 거래 ─────────────────────────────────────────────────

    def insert_trade(self, trade, regime="혼합"):
        # type: (Any, str) -> int
        sql = """
        INSERT INTO challenger_trades
            (challenger_id, entry_ts, direction, entry_price, grade, regime)
        VALUES (?,?,?,?,?,?)
        """
        with self._conn() as conn:
            cur = conn.execute(sql, (
                trade.challenger_id, trade.entry_ts,
                trade.direction, trade.entry_price, trade.grade, regime,
            ))
            return cur.lastrowid

    def close_trade(self, trade_id, exit_ts, exit_price, pnl_pt, exit_reason):
        sql = """
        UPDATE challenger_trades
        SET exit_ts=?, exit_price=?, pnl_pt=?, exit_reason=?
        WHERE id=?
        """
        with self._conn() as conn:
            conn.execute(sql, (exit_ts, exit_price, pnl_pt, exit_reason, trade_id))

    def get_open_trades(self, challenger_id):
        # type: (str) -> List[sqlite3.Row]
        sql = """
        SELECT * FROM challenger_trades
        WHERE challenger_id=? AND exit_ts IS NULL
        ORDER BY entry_ts
        """
        with self._conn() as conn:
            return conn.execute(sql, (challenger_id,)).fetchall()

    # ── 전체 일별 집계 ───────────────────────────────────────────

    def upsert_daily_metrics(self, metrics):
        # type: (Dict[str, Any]) -> None
        sql = """
        INSERT OR REPLACE INTO challenger_daily_metrics
            (date, challenger_id, signal_count, trade_count, win_count,
             win_rate, total_pnl_pt, mdd_pt, sharpe, cum_pnl_pt, cum_mdd_pt)
        VALUES (:date, :challenger_id, :signal_count, :trade_count, :win_count,
                :win_rate, :total_pnl_pt, :mdd_pt, :sharpe, :cum_pnl_pt, :cum_mdd_pt)
        """
        with self._conn() as conn:
            conn.execute(sql, metrics)

    def get_metrics_summary(self, challenger_id):
        # type: (str) -> Dict[str, Any]
        sql = """
        SELECT
            COUNT(DISTINCT date) AS obs_days,
            SUM(trade_count)     AS trade_count,
            SUM(win_count)       AS win_count,
            MAX(cum_pnl_pt)      AS cum_pnl_pt,
            MIN(cum_mdd_pt)      AS cum_mdd_pt,
            AVG(sharpe)          AS sharpe_avg
        FROM challenger_daily_metrics
        WHERE challenger_id=?
        """
        with self._conn() as conn:
            row = conn.execute(sql, (challenger_id,)).fetchone()

        if row is None or row["trade_count"] is None:
            return {"obs_days": 0, "trade_count": 0, "win_rate": 0.0,
                    "cum_pnl_pt": 0.0, "cum_mdd_pt": 0.0, "sharpe": 0.0}

        tc = row["trade_count"] or 0
        wc = row["win_count"] or 0
        return {
            "obs_days":    row["obs_days"] or 0,
            "trade_count": tc,
            "win_rate":    round(wc / tc * 100, 2) if tc > 0 else 0.0,
            "cum_pnl_pt":  round(row["cum_pnl_pt"] or 0.0, 2),
            "cum_mdd_pt":  round(row["cum_mdd_pt"] or 0.0, 2),
            "sharpe":      round(row["sharpe_avg"] or 0.0, 2),
        }

    def get_daily_metrics_list(self, challenger_id, limit=60):
        # type: (str, int) -> List[sqlite3.Row]
        sql = """
        SELECT * FROM challenger_daily_metrics
        WHERE challenger_id=?
        ORDER BY date DESC LIMIT ?
        """
        with self._conn() as conn:
            rows = conn.execute(sql, (challenger_id, limit)).fetchall()
        return list(reversed(rows))

    # ── 레짐별 누적 집계 ─────────────────────────────────────────

    def upsert_regime_metrics(self, challenger_id, regime, metrics):
        # type: (str, str, Dict[str, Any]) -> None
        """레짐별 누적 집계 갱신 (INSERT OR REPLACE)"""
        from datetime import datetime
        sql = """
        INSERT OR REPLACE INTO challenger_regime_metrics
            (challenger_id, regime, trade_count, win_count, win_rate,
             total_pnl_pt, mdd_pt, sharpe, last_updated)
        VALUES (?,?,?,?,?,?,?,?,?)
        """
        with self._conn() as conn:
            conn.execute(sql, (
                challenger_id, regime,
                metrics.get("trade_count", 0),
                metrics.get("win_count", 0),
                metrics.get("win_rate", 0.0),
                metrics.get("total_pnl_pt", 0.0),
                metrics.get("mdd_pt", 0.0),
                metrics.get("sharpe", 0.0),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))

    def get_regime_metrics(self, challenger_id, regime):
        # type: (str, str) -> Dict[str, Any]
        """레짐별 누적 성과 조회"""
        sql = """
        SELECT * FROM challenger_regime_metrics
        WHERE challenger_id=? AND regime=?
        """
        with self._conn() as conn:
            row = conn.execute(sql, (challenger_id, regime)).fetchone()
        if row is None:
            return {"trade_count": 0, "win_rate": 0.0,
                    "total_pnl_pt": 0.0, "mdd_pt": 0.0, "sharpe": 0.0}
        return dict(row)

    def get_regime_closed_trades(self, challenger_id, regime):
        # type: (str, str) -> List[sqlite3.Row]
        """특정 레짐에서의 종료된 가상 거래 전체"""
        sql = """
        SELECT * FROM challenger_trades
        WHERE challenger_id=? AND regime=? AND exit_ts IS NOT NULL
        ORDER BY entry_ts
        """
        with self._conn() as conn:
            return conn.execute(sql, (challenger_id, regime)).fetchall()

    def get_regime_ranking(self, regime, challenger_ids):
        # type: (str, List[str]) -> List[Dict[str, Any]]
        """
        레짐별 성과 기준 순위 목록 반환.
        정렬 기준: ① 거래 수 충족 여부 ② win_rate 내림차순 ③ sharpe 내림차순
        """
        if not challenger_ids:
            return []
        rows = []
        for cid in challenger_ids:
            m = self.get_regime_metrics(cid, regime)
            rows.append({"challenger_id": cid, **m})
        rows.sort(key=lambda x: (
            -(x.get("trade_count", 0) >= 20),   # 20건 이상이면 우선
            -x.get("win_rate", 0.0),
            -x.get("sharpe", 0.0),
        ))
        return rows

    # ── 레짐 순위 이력 ───────────────────────────────────────────

    def insert_regime_rank(self, ts, regime, rank1, rank2, rank3, prev_rank1, changed):
        # type: (str, str, Optional[str], Optional[str], Optional[str], Optional[str], bool) -> None
        sql = """
        INSERT INTO regime_rank_history
            (ts, regime, rank_1_id, rank_2_id, rank_3_id, prev_rank_1, changed)
        VALUES (?,?,?,?,?,?,?)
        """
        with self._conn() as conn:
            conn.execute(sql, (ts, regime, rank1, rank2, rank3, prev_rank1, int(changed)))

    def get_latest_regime_rank(self, regime):
        # type: (str) -> Optional[sqlite3.Row]
        sql = """
        SELECT * FROM regime_rank_history
        WHERE regime=?
        ORDER BY id DESC LIMIT 1
        """
        with self._conn() as conn:
            return conn.execute(sql, (regime,)).fetchone()

    # ── 오늘 데이터 헬퍼 ─────────────────────────────────────────

    def get_today_signal_count(self, challenger_id, date_str):
        # type: (str, str) -> int
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM challenger_signals "
                "WHERE challenger_id=? AND ts LIKE ?",
                (challenger_id, date_str + "%"),
            ).fetchone()
        return row["cnt"] if row else 0

    def get_today_closed_trades(self, challenger_id, date_str):
        # type: (str, str) -> List[sqlite3.Row]
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM challenger_trades "
                "WHERE challenger_id=? AND entry_ts LIKE ? AND exit_ts IS NOT NULL",
                (challenger_id, date_str + "%"),
            ).fetchall()

    def get_today_closed_trades_by_regime(self, challenger_id, date_str, regime):
        # type: (str, str, str) -> List[sqlite3.Row]
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM challenger_trades "
                "WHERE challenger_id=? AND entry_ts LIKE ? "
                "AND regime=? AND exit_ts IS NOT NULL",
                (challenger_id, date_str + "%", regime),
            ).fetchall()

    # ── 챔피언 교체 이력 ─────────────────────────────────────────

    def insert_champion_history(self, promoted_ts, from_champion, to_champion,
                                reason, obs_days, win_rate_delta, mdd_delta,
                                regime="GLOBAL"):
        sql = """
        INSERT INTO champion_history
            (promoted_ts, from_champion, to_champion, reason,
             regime, obs_days, win_rate_delta, mdd_delta)
        VALUES (?,?,?,?,?,?,?,?)
        """
        with self._conn() as conn:
            conn.execute(sql, (
                promoted_ts, from_champion, to_champion, reason,
                regime, obs_days, win_rate_delta, mdd_delta,
            ))

    def get_last_champion_history(self, regime="GLOBAL"):
        # type: (str) -> Optional[sqlite3.Row]
        sql = """
        SELECT * FROM champion_history
        WHERE regime=?
        ORDER BY id DESC LIMIT 1
        """
        with self._conn() as conn:
            return conn.execute(sql, (regime,)).fetchone()
