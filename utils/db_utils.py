# utils/db_utils.py — SQLite 공통 유틸리티
import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import List, Tuple, Any, Optional, Dict

import json
from config.constants import FUTURES_PT_VALUE, get_contract_spec
from config.settings import PREDICTIONS_DB, SHAP_DB, TRADES_DB, RAW_DATA_DB, DB_DIR, DATA_DIR
from config.settings import FUTURES_COMMISSION_RATE

_lock = threading.Lock()
TRADE_PNL_FORMULA_VERSION = 4  # v4: pt_value 종목코드 연동 (미니선물 50k, 일반선물 250k)
MIN_VALID_FUTURES_PRICE = 100.0
MAX_VALID_FUTURES_PRICE = 10000.0
MAX_REASONABLE_TRADE_PNL_PTS = 200.0


@contextmanager
def get_conn(db_path: str, timeout: float = 10.0):
    """SQLite 연결 컨텍스트 매니저 (스레드 안전)

    timeout: busy_timeout(초) — 다른 연결이 DB를 잠그고 있을 때 대기할 최대 시간.
             파이프라인 크리티컬 경로에서 호출하는 경우 짧게(2~3s) 줘서
             장시간 블로킹 대신 빠르게 실패시키는 용도로 사용.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=timeout, check_same_thread=False)
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


def _get_pt_value_from_prefs() -> int:
    """ui_prefs.json의 symbol_code로 pt_value를 결정한다.
    읽기 실패 또는 코드 미설정 시 일반선물 기본값(250,000) 반환.
    """
    try:
        prefs_path = os.path.join(DATA_DIR, "ui_prefs.json")
        with open(prefs_path, "r", encoding="utf-8") as _f:
            prefs = json.load(_f)
        code = prefs.get("symbol_code", "")
        if code:
            return get_contract_spec(code)["pt_value"]
    except Exception:
        pass
    return FUTURES_PT_VALUE


def normalize_trade_pnl(
    entry_price: float,
    quantity: int,
    pnl_pts: float,
    pt_value: int = FUTURES_PT_VALUE,
) -> Dict[str, float]:
    """계약 스펙(pt_value)을 반영해 거래 손익을 정규화한다.
    미니선물=50,000 / 일반선물=250,000 — 반드시 종목코드 기반 pt_value를 전달할 것.
    """
    entry_price_f = float(entry_price or 0.0)
    quantity_i = max(int(quantity or 0), 0)
    pnl_pts_f = float(pnl_pts or 0.0)
    gross_pnl_krw = pnl_pts_f * pt_value * quantity_i
    commission_krw = entry_price_f * quantity_i * pt_value * FUTURES_COMMISSION_RATE * 2
    net_pnl_krw = gross_pnl_krw - commission_krw
    return {
        "gross_pnl_krw": round(gross_pnl_krw, 0),
        "commission_krw": round(commission_krw, 0),
        "net_pnl_krw": round(net_pnl_krw, 0),
        "formula_version": TRADE_PNL_FORMULA_VERSION,
    }


def is_plausible_futures_trade(
    *,
    entry_price: Any,
    exit_price: Any,
    quantity: Any,
    pnl_pts: Any,
) -> bool:
    """Filter obviously corrupted futures trade rows from restore/PnL views."""
    try:
        entry_price_f = float(entry_price or 0.0)
        exit_price_f = float(exit_price or 0.0)
        quantity_i = int(quantity or 0)
        pnl_pts_f = abs(float(pnl_pts or 0.0))
    except Exception:
        return False

    if quantity_i <= 0:
        return False
    if not (MIN_VALID_FUTURES_PRICE <= entry_price_f <= MAX_VALID_FUTURES_PRICE):
        return False
    if not (MIN_VALID_FUTURES_PRICE <= exit_price_f <= MAX_VALID_FUTURES_PRICE):
        return False
    if abs(pnl_pts_f) > MAX_REASONABLE_TRADE_PNL_PTS:
        return False
    return True


def filter_plausible_trade_rows(rows: List[sqlite3.Row]) -> List[sqlite3.Row]:
    return [
        row for row in rows
        if is_plausible_futures_trade(
            entry_price=row["entry_price"] if "entry_price" in row.keys() else 0.0,
            exit_price=row["exit_price"] if "exit_price" in row.keys() else 0.0,
            quantity=row["quantity"] if "quantity" in row.keys() else 0,
            pnl_pts=row["pnl_pts"] if "pnl_pts" in row.keys() else 0.0,
        )
    ]


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
    # 복합 인덱스 — verify_and_update의 WHERE ts=? AND horizon=? AND actual IS NULL 최적화
    execute(PREDICTIONS_DB,
            "CREATE INDEX IF NOT EXISTS idx_ts_hz ON predictions(ts, horizon)")
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
    # WAL 파일이 하루종일 비대해지는 것을 방지 (기본 1000 → 100페이지)
    execute(PREDICTIONS_DB, "PRAGMA wal_autocheckpoint=100")


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
            if "sigma_at_t" not in cols:
                conn.execute(
                    "ALTER TABLE predictions ADD COLUMN sigma_at_t REAL DEFAULT 0.0"
                )
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
                # STEP7 마스터 게이트 — 대시보드 "진입단계 추적" 카드 복원용
                "entry_gate_json": "TEXT",
                "entry_final_ok": "INTEGER",
                "entry_qty": "INTEGER",
                "entry_mode": "TEXT",
                "entry_executed": "INTEGER",
                "entry_block_reason": "TEXT",
                # 차단사유 축약 키 — stage 2/8 표시용
                "checklist_reason": "TEXT",
                # [260704 감사 P1] meta_labels 기반 진입품질 분류기 섀도우 스코어 —
                # 실거래 의사결정 미반영, 예측-손익 상관 분석용 로깅 전용
                "meta_entry_quality_prob": "REAL",
                # [260704 감사 P2] 분위 회귀(q10/q50/q90) 섀도우 스코어 — 실거래 미반영
                "quantile_expected_pt": "REAL",
                "quantile_uncertainty_pt": "REAL",
                # [260705 검증 캠페인] §3-3 커버리지 KPI용 원시 분위값 + 스코어링 호라이즌
                # (expected/uncertainty만으로는 비대칭 분위에서 q10/q90 복원 불가)
                "quantile_q10_pt": "REAL",
                "quantile_q90_pt": "REAL",
                "meta_gate_horizon": "TEXT",
                # [297차, P1-6] CoherenceGate/CascadeCoherence 실제 차단 플래그.
                # grade=='X' AND regime_ok==1 로 역추정하면 conf미달과 동시 발생한
                # 케이스(같은 분에 confidence<mc 이면서 coherence_blocked도 True인
                # 경우 — 실측 존재)를 conf미달로 오분류한다. 진입 퍼널(daily_exporter)
                # 정확도를 위해 원본 플래그를 직접 저장.
                "coherence_blocked": "INTEGER",
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
    # [260705 검증 캠페인] §3-5 신호소멸청산 counterfactual 기록 —
    # 발동 시점의 스톱/TP1 가격을 보존해 두고, 주간 리포트가 이후 분봉으로
    # "청산 안 했으면 어느 배리어에 먼저 닿았나"를 사후 판정(resolve)한다.
    # 리포트 전용 계측 테이블 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS signal_decay_exits (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        ts            TEXT NOT NULL,           -- 발동 시각 (분봉)
        direction     TEXT NOT NULL,           -- LONG/SHORT (청산된 포지션 방향)
        exit_price    REAL NOT NULL,           -- 신호소멸청산 체결가(분봉 종가)
        stop_price    REAL,                    -- 당시 하드스톱 가격
        tp1_price     REAL,                    -- 당시 TP1 가격
        quantity      INTEGER,
        conf          REAL,                    -- 반대신호 confidence
        zone_mc       REAL,                    -- 당시 zone_mc 임계
        resolved      INTEGER DEFAULT 0,       -- 1=counterfactual 판정 완료
        cf_outcome    TEXT,                    -- STOP / TP1 / NEITHER
        cf_exit_price REAL,                    -- counterfactual 청산가
        saved_pts     REAL,                    -- (+)=조기청산으로 아낀 pt, (-)=놓친 pt
        created_at    TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_sde_ts ON signal_decay_exits(ts)")
    # [297차, P1-4] Hurst 게이트 counterfactual 섀도우 — signal_decay_exits와 동일 패턴.
    # 실제로는 차단(미진입)된 분봉이므로 "가상 진입가 대비 stop/tp1 중 무엇에 먼저
    # 닿았나"를 사후 판정해 "차단이 손실을 막았는지, 이익을 놓쳤는지"를 누적한다.
    # 리포트 전용 계측 테이블 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS hurst_gate_shadow (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        ts            TEXT NOT NULL,           -- 차단 시각 (분봉)
        direction     TEXT NOT NULL,           -- LONG/SHORT (차단된 가상 방향)
        grade         TEXT,                    -- 차단 당시 진입 등급 (A/B/C, Hurst 미차단 가정)
        hurst         REAL,                    -- 차단 당시 Hurst 값
        conf          REAL,                    -- 차단 당시 confidence
        entry_price   REAL NOT NULL,           -- 가상 진입가 (분봉 종가)
        stop_price    REAL,                    -- 가상 하드스톱
        tp1_price     REAL,                    -- 가상 TP1
        resolved      INTEGER DEFAULT 0,       -- 1=counterfactual 판정 완료
        cf_outcome    TEXT,                    -- STOP / TP1 / NEITHER
        cf_exit_price REAL,                    -- counterfactual 청산가
        hyp_pnl_pts   REAL,                    -- (+)=차단 안 했으면 이득, (-)=차단이 손실 회피
        created_at    TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_hgs_ts ON hurst_gate_shadow(ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_entry_ts ON trades(entry_ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_exit_ts ON trades(exit_ts)")


def _migrate_trades_db():
    """거래 테이블에 정규화 PnL 컬럼을 보강하고 기존 혼합 데이터를 현재 공식으로 통일.
    v4: ui_prefs.json의 symbol_code로 pt_value를 결정해 미니/일반선물 구분 적용.
    """
    pt_value = _get_pt_value_from_prefs()
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
                "raw_direction": "TEXT",
                "executed_direction": "TEXT",
                "reverse_entry_enabled": "INTEGER",
                "forward_pnl_pts": "REAL",
                "forward_pnl_krw": "REAL",
                "forward_gross_pnl_krw": "REAL",
                "forward_commission_krw": "REAL",
                "forward_net_pnl_krw": "REAL",
                "meta_action":        "TEXT",
                "hurst_bucket":       "TEXT",
                "hour_bucket":        "INTEGER",
                "was_restart_after":  "INTEGER DEFAULT 0",
                "had_partial_fill":   "INTEGER DEFAULT 0",
                "entry_horizon":      "TEXT",
            }
            for name, dtype in additions.items():
                if name not in cols:
                    conn.execute(f"ALTER TABLE trades ADD COLUMN {name} {dtype}")

            rows = conn.execute(
                """SELECT id, entry_price, exit_price, direction,
                          COALESCE(raw_direction, direction) AS raw_direction,
                          quantity, pnl_pts, formula_version
                   FROM trades
                   WHERE pnl_pts IS NOT NULL AND exit_price IS NOT NULL"""
            ).fetchall()
            for row in rows:
                current_version = int(row["formula_version"] or 0)
                if current_version == TRADE_PNL_FORMULA_VERSION:
                    continue
                # v3: pnl_pts를 진입/청산가 기준 per-contract 값으로 재산출한다.
                # 이전 버전에서 분할체결 집계 시 per-contract × fill_count가 저장된 버그를 수정.
                entry_p = float(row["entry_price"] or 0.0)
                exit_p = float(row["exit_price"] or 0.0)
                qty = max(int(row["quantity"] or 1), 1)
                direction = str(row["direction"] or "LONG")
                raw_dir = str(row["raw_direction"] or direction)
                exec_mult = 1 if direction == "LONG" else -1
                fwd_mult = 1 if raw_dir == "LONG" else -1
                corrected_pnl_pts = (exit_p - entry_p) * exec_mult
                corrected_fwd_pts = (exit_p - entry_p) * fwd_mult
                metrics = normalize_trade_pnl(
                    entry_price=entry_p,
                    quantity=qty,
                    pnl_pts=corrected_pnl_pts,
                    pt_value=pt_value,
                )
                fwd_metrics = normalize_trade_pnl(
                    entry_price=entry_p,
                    quantity=qty,
                    pnl_pts=corrected_fwd_pts,
                    pt_value=pt_value,
                )
                conn.execute(
                    """UPDATE trades
                       SET pnl_pts = ?,
                           gross_pnl_krw = ?,
                           commission_krw = ?,
                           net_pnl_krw = ?,
                           pnl_krw = ?,
                           formula_version = ?,
                           raw_direction = COALESCE(raw_direction, direction),
                           executed_direction = COALESCE(executed_direction, direction),
                           reverse_entry_enabled = COALESCE(reverse_entry_enabled, 0),
                           forward_pnl_pts = ?,
                           forward_pnl_krw = ?,
                           forward_gross_pnl_krw = ?,
                           forward_commission_krw = ?,
                           forward_net_pnl_krw = ?
                       WHERE id = ?""",
                    (
                        round(corrected_pnl_pts, 4),
                        metrics["gross_pnl_krw"],
                        metrics["commission_krw"],
                        metrics["net_pnl_krw"],
                        metrics["net_pnl_krw"],
                        metrics["formula_version"],
                        round(corrected_fwd_pts, 4),
                        fwd_metrics["net_pnl_krw"],
                        fwd_metrics["gross_pnl_krw"],
                        fwd_metrics["commission_krw"],
                        fwd_metrics["net_pnl_krw"],
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


def save_shap_scores(ts: str, horizon: str, score_map: Dict[str, float]) -> None:
    """Persist one SHAP snapshot for multiple features."""
    if not ts or not score_map:
        return
    rows = [
        (ts, str(feature), float(value), str(horizon))
        for feature, value in score_map.items()
    ]
    executemany(
        SHAP_DB,
        """
        INSERT INTO shap_scores (ts, feature, shap_value, horizon)
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )


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
            buy_vol    INTEGER DEFAULT 0,
            sell_vol   INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    # Phase 2 마이그레이션: 기존 DB에 buy_vol/sell_vol 컬럼 추가 (없으면 추가, 있으면 무시)
    for _col, _type in [("buy_vol", "INTEGER DEFAULT 0"), ("sell_vol", "INTEGER DEFAULT 0")]:
        try:
            execute(RAW_DATA_DB, "ALTER TABLE raw_candles ADD COLUMN {} {}".format(_col, _type))
        except Exception:
            pass  # 이미 존재하면 무시
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS raw_features (
            ts         TEXT PRIMARY KEY,
            features   TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    # Phase 2: 호라이즌별 피처 테이블 (N분봉 완성 시 저장)
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS raw_features_horizon (
            ts       TEXT NOT NULL,
            horizon  TEXT NOT NULL,
            features TEXT NOT NULL,
            regime   TEXT DEFAULT 'NEUTRAL',
            PRIMARY KEY (ts, horizon)
        )
    """)
    # P2 사전 준비: 기존 DB에 regime 컬럼 추가 (없으면 추가, 있으면 무시)
    try:
        execute(RAW_DATA_DB,
                "ALTER TABLE raw_features_horizon ADD COLUMN regime TEXT DEFAULT 'NEUTRAL'")
    except Exception:
        pass  # 이미 존재하면 무시
    try:
        execute(RAW_DATA_DB,
                "CREATE INDEX IF NOT EXISTS idx_rfh_horizon ON raw_features_horizon(horizon, ts)")
    except Exception:
        pass
    # 173차: 레짐 히스토리 (차트 레짐 바 재시작 복원용)
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS regime_history (
            ts     TEXT PRIMARY KEY,
            regime TEXT NOT NULL
        )
    """)
    # [303차] 거래소 CB(단일가/서킷브레이커) 감지 이력 — EOD 리포트 halt 요약용
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS exchange_cb_halts (
            start_ts TEXT PRIMARY KEY,
            end_ts   TEXT NOT NULL,
            gap_min  INTEGER NOT NULL
        )
    """)
    # Phase 2: N분봉 완성봉 집계 캐시 (backfill 및 검증용)
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS raw_candles_aggregated (
            ts       TEXT NOT NULL,
            horizon  TEXT NOT NULL,
            open     REAL, high  REAL, low REAL, close REAL,
            volume   INTEGER, buy_vol INTEGER, sell_vol INTEGER,
            PRIMARY KEY (ts, horizon)
        )
    """)


def save_candle(candle: dict) -> None:
    """분봉 확정 시 raw_candles에 저장."""
    ts_raw = candle.get("ts")
    ts = ts_raw.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts_raw, "strftime") else str(ts_raw)
    execute(
        RAW_DATA_DB,
        """INSERT OR REPLACE INTO raw_candles
           (ts, open, high, low, close, volume, bid1, ask1, oi, buy_vol, sell_vol)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            ts,
            candle.get("open",     0.0),
            candle.get("high",     0.0),
            candle.get("low",      0.0),
            candle.get("close",    0.0),
            candle.get("volume",   0),
            candle.get("bid1"),
            candle.get("ask1"),
            candle.get("oi"),
            candle.get("buy_vol",  0),
            candle.get("sell_vol", 0),
        ),
    )


def save_features(ts: str, features: dict) -> None:
    """피처 벡터를 raw_features에 저장."""
    execute(
        RAW_DATA_DB,
        "INSERT OR REPLACE INTO raw_features (ts, features) VALUES (?, ?)",
        (ts, json.dumps(features, ensure_ascii=False)),
    )


def save_candle_and_features(candle: dict, ts: str, features: dict) -> None:
    """분봉 + 피처를 1연결 트랜잭션으로 저장 (save_candle+save_features 2회 연결 → 1회)."""
    ts_raw = candle.get("ts")
    candle_ts = ts_raw.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts_raw, "strftime") else str(ts_raw)
    feat_json = json.dumps(features, ensure_ascii=False)
    with _lock:
        with get_conn(RAW_DATA_DB) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO raw_candles
                   (ts, open, high, low, close, volume, bid1, ask1, oi, buy_vol, sell_vol)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    candle_ts,
                    candle.get("open",     0.0),
                    candle.get("high",     0.0),
                    candle.get("low",      0.0),
                    candle.get("close",    0.0),
                    candle.get("volume",   0),
                    candle.get("bid1"),
                    candle.get("ask1"),
                    candle.get("oi"),
                    candle.get("buy_vol",  0),
                    candle.get("sell_vol", 0),
                ),
            )
            conn.execute(
                "INSERT OR REPLACE INTO raw_features (ts, features) VALUES (?, ?)",
                (ts, feat_json),
            )


def save_horizon_features(ts: str, horizon: str, features: dict, regime: str = "NEUTRAL") -> None:
    """N분봉 완성 시 호라이즌별 피처 저장 (Phase 2 전용)."""
    execute(
        RAW_DATA_DB,
        "INSERT OR REPLACE INTO raw_features_horizon (ts, horizon, features, regime) VALUES (?,?,?,?)",
        (ts, horizon, json.dumps(features, ensure_ascii=False), regime or "NEUTRAL"),
    )


def get_candle_close(ts: str) -> Optional[float]:
    """ts 시각의 종가 반환 — actual 라벨 계산용."""
    row = fetchone(RAW_DATA_DB, "SELECT close FROM raw_candles WHERE ts = ?", (ts,))
    return float(row["close"]) if row else None


def count_raw_candles() -> int:
    """누적 분봉 수 반환."""
    row = fetchone(RAW_DATA_DB, "SELECT COUNT(*) AS cnt FROM raw_candles")
    return row["cnt"] if row else 0


def fetch_recent_raw_features(limit: int = 240) -> List[sqlite3.Row]:
    """Return recent raw feature rows ordered oldest -> newest."""
    rows = fetchall(
        RAW_DATA_DB,
        """
        SELECT ts, features
        FROM raw_features
        ORDER BY ts DESC
        LIMIT ?
        """,
        (int(limit),),
    )
    return list(reversed(rows))


def fetch_recent_raw_candles(limit: int = 60) -> List[sqlite3.Row]:
    """Return recent raw candle rows (high/low/close/volume) oldest -> newest.
    VP 버퍼 복원 등 재시작 후 상태 복구 용도.
    """
    rows = fetchall(
        RAW_DATA_DB,
        "SELECT ts, high, low, close, volume FROM raw_candles ORDER BY ts DESC LIMIT ?",
        (int(limit),),
    )
    return list(reversed(rows))


def fetch_pnl_history(limit_days: int = 90) -> List[sqlite3.Row]:
    """최근 N일 체결 완료 거래 전체 반환 — 손익 추이 패널용.
    반환 컬럼: direction, entry_price, exit_price, quantity, pnl_pts, pnl_krw,
               exit_reason, grade, entry_ts, exit_ts
    """
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=limit_days)).isoformat()
    rows = fetchall(
        TRADES_DB,
        """SELECT COALESCE(raw_direction, direction) AS raw_direction,
                  COALESCE(executed_direction, direction) AS executed_direction,
                  direction, entry_price, exit_price, quantity,
                  pnl_pts,
                  COALESCE(net_pnl_krw, pnl_krw) AS pnl_krw,
                  COALESCE(forward_pnl_pts, pnl_pts) AS forward_pnl_pts,
                  COALESCE(forward_net_pnl_krw, forward_pnl_krw, net_pnl_krw, pnl_krw) AS forward_pnl_krw,
                  gross_pnl_krw, commission_krw, formula_version,
                  forward_gross_pnl_krw, forward_commission_krw,
                  reverse_entry_enabled,
                  exit_reason, grade, entry_ts, exit_ts
           FROM trades
           WHERE exit_ts IS NOT NULL AND exit_ts >= ?
           ORDER BY exit_ts ASC""",
        (cutoff + " 00:00:00",),
    )
    return filter_plausible_trade_rows(rows)


def fetch_today_trades(today_str: str = None) -> List[sqlite3.Row]:
    """당일 체결 완료 거래 목록 (entry_ts LIKE today_str%).
    반환 컬럼: direction, entry_price, exit_price, quantity, pnl_pts, pnl_krw,
               exit_reason, grade, entry_ts, exit_ts
    """
    import datetime as _dt
    if today_str is None:
        today_str = _dt.date.today().isoformat()
    rows = fetchall(
        TRADES_DB,
        """SELECT COALESCE(raw_direction, direction) AS raw_direction,
                  COALESCE(executed_direction, direction) AS executed_direction,
                  direction, entry_price, exit_price, quantity,
                  pnl_pts,
                  COALESCE(net_pnl_krw, pnl_krw) AS pnl_krw,
                  COALESCE(forward_pnl_pts, pnl_pts) AS forward_pnl_pts,
                  COALESCE(forward_net_pnl_krw, forward_pnl_krw, net_pnl_krw, pnl_krw) AS forward_pnl_krw,
                  gross_pnl_krw, commission_krw, formula_version,
                  forward_gross_pnl_krw, forward_commission_krw,
                  exit_reason, grade, entry_ts, exit_ts
           FROM trades
           WHERE exit_ts LIKE ?
           ORDER BY exit_ts ASC""",
        (today_str + "%",),
    )
    return filter_plausible_trade_rows(rows)


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
                  ROUND(AVG(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
                  ROUND(AVG(COALESCE(forward_pnl_pts, pnl_pts)), 4) AS avg_pnl,
                  ROUND(SUM(COALESCE(forward_pnl_pts, pnl_pts)), 4) AS total_pnl
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
                  ROUND(AVG(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
                  ROUND(AVG(COALESCE(forward_pnl_pts, pnl_pts)), 4) AS avg_pnl
           FROM trades
           WHERE exit_ts IS NOT NULL
           GROUP BY regime
           ORDER BY regime""",
    )


def fetch_ev_by_grade(days_back: int = 30) -> List[sqlite3.Row]:
    """등급별 순EV(수수료 차감 후 실집행 기준) — grade, cnt, win_rate, avg_net_pnl_krw, total_net_pnl_krw.
    [260704 감사 P0] "방향 적중률" 대신 "거래당 순기대값"을 보는 관점 — fetch_grade_stats()(pnl_pts 방향)와 병행 참고.
    """
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days_back)).isoformat()
    return fetchall(
        TRADES_DB,
        """SELECT COALESCE(NULLIF(grade, ''), '?') AS grade,
                  COUNT(*) AS cnt,
                  ROUND(AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
                  ROUND(AVG(COALESCE(net_pnl_krw, pnl_krw)), 0) AS avg_net_pnl_krw,
                  ROUND(SUM(COALESCE(net_pnl_krw, pnl_krw)), 0) AS total_net_pnl_krw
           FROM trades
           WHERE exit_ts IS NOT NULL AND exit_ts >= ?
           GROUP BY grade
           ORDER BY grade""",
        (cutoff + " 00:00:00",),
    )


def fetch_ev_by_horizon(days_back: int = 30) -> List[sqlite3.Row]:
    """진입 호라이즌별 순EV — entry_horizon, cnt, win_rate, avg_net_pnl_krw, total_net_pnl_krw.
    entry_horizon은 2026-07-05 이후 체결분부터 기록되므로 그 이전 데이터는 '?'(미기록)으로 집계된다.
    """
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days_back)).isoformat()
    return fetchall(
        TRADES_DB,
        """SELECT COALESCE(NULLIF(entry_horizon, ''), '?') AS entry_horizon,
                  COUNT(*) AS cnt,
                  ROUND(AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
                  ROUND(AVG(COALESCE(net_pnl_krw, pnl_krw)), 0) AS avg_net_pnl_krw,
                  ROUND(SUM(COALESCE(net_pnl_krw, pnl_krw)), 0) AS total_net_pnl_krw
           FROM trades
           WHERE exit_ts IS NOT NULL AND exit_ts >= ?
           GROUP BY entry_horizon
           ORDER BY entry_horizon""",
        (cutoff + " 00:00:00",),
    )


def fetch_ev_by_hour(days_back: int = 30) -> List[sqlite3.Row]:
    """시간대(hour_bucket)별 순EV — hour_bucket, cnt, win_rate, avg_net_pnl_krw."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days_back)).isoformat()
    return fetchall(
        TRADES_DB,
        """SELECT COALESCE(hour_bucket, -1) AS hour_bucket,
                  COUNT(*) AS cnt,
                  ROUND(AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
                  ROUND(AVG(COALESCE(net_pnl_krw, pnl_krw)), 0) AS avg_net_pnl_krw
           FROM trades
           WHERE exit_ts IS NOT NULL AND exit_ts >= ?
           GROUP BY hour_bucket
           ORDER BY hour_bucket""",
        (cutoff + " 00:00:00",),
    )


def fetch_recent_ev(n: int = 20) -> Dict:
    """최근 N건 체결 완료 거래의 순EV(수수료 차감 후) 요약 — 대시보드 상시 노출용.
    반환: {"cnt": int, "avg_net_pnl_krw": float, "win_rate": float, "total_net_pnl_krw": float}
    """
    rows = fetchall(
        TRADES_DB,
        """SELECT COALESCE(net_pnl_krw, pnl_krw) AS net_pnl_krw
           FROM trades
           WHERE exit_ts IS NOT NULL
           ORDER BY exit_ts DESC
           LIMIT ?""",
        (n,),
    )
    if not rows:
        return {"cnt": 0, "avg_net_pnl_krw": 0.0, "win_rate": 0.0, "total_net_pnl_krw": 0.0}
    vals = [float(r["net_pnl_krw"] or 0.0) for r in rows]
    wins = sum(1 for v in vals if v > 0)
    return {
        "cnt": len(vals),
        "avg_net_pnl_krw": sum(vals) / len(vals),
        "win_rate": wins / len(vals),
        "total_net_pnl_krw": sum(vals),
    }


def fetch_entry_candidate_gap(lookback_days: int = 5) -> Dict:
    """[297차, P1-5] 최근 N거래일 진입후보(confidence>=min_conf) 분 수 롤링 집계.

    동적 min_conf(zone_mc)는 과거 conf 분포 기반이라, conf 분포가 급락하면
    ensemble_decisions.regime_ok=1(=진입후보) 분 수가 0에 가깝게 붕괴할 수 있다
    (292차 진입0 딥다이브 실측). 자동으로 mc를 조정하지 않고 경보용 수치만 반환한다
    — 판단은 사용자 몫(config.settings.MC_CONF_GAP_ALERT_*).

    반환: {"days": [{"date": str, "n_candidates": int}, ...], "avg": float,
           "today": int, "lookback_days": int}
    거래일 자체가 없으면 avg=0.0, days=[].
    """
    rows = fetchall(
        PREDICTIONS_DB,
        """SELECT substr(ts, 1, 10) AS d,
                  SUM(CASE WHEN regime_ok = 1 THEN 1 ELSE 0 END) AS n_cand
           FROM ensemble_decisions
           GROUP BY d
           ORDER BY d DESC
           LIMIT ?""",
        (lookback_days,),
    )
    if not rows:
        return {"days": [], "avg": 0.0, "today": 0, "lookback_days": lookback_days}
    days = [{"date": r["d"], "n_candidates": int(r["n_cand"] or 0)} for r in rows]
    avg = sum(d["n_candidates"] for d in days) / len(days)
    return {
        "days": days,
        "avg": round(avg, 1),
        "today": days[0]["n_candidates"],
        "lookback_days": lookback_days,
    }


# [297차, P1-6] entry_block_reason(STEP7 elif-chain) 부분문자열 → 표시 라벨.
# 순서 중요 — main.py의 우선순위 그대로 위에서부터 첫 매치를 사용한다.
_BLOCK_REASON_CATEGORIES = [
    ("Hurst",           "Hurst(횡보차단)"),
    ("모드필터",          "모드필터"),
    ("시가이격",          "시가갭(OPEN_VOLATILE)"),
    ("ATR",             "ATR변동성"),
    ("거래소 CB",         "거래소CB관망"),
    ("Circuit Breaker", "CB정지"),
    ("고신뢰 연속오답",     "HC차단"),
    ("브로커 sync",       "브로커동기화"),
    ("Restart Armistice", "재시작유예"),
    ("포지션 무결성",       "무결성"),
    ("쿨다운",            "쿨다운"),
    ("Reverse Clamp",   "역방향클램프"),
    ("IntradayRegime",  "장중레짐"),
    ("15:00 이후",        "마감시간(15:00+)"),
    ("Degraded",        "Degraded신뢰도"),
    ("점심 휴식",          "시간대차단"),
    ("진입 금지 시간대",     "시간대차단"),
    ("등급X",            "체크리스트항목미달"),
]


def _categorize_block_reason(entry_block_reason: Optional[str], checklist_reason: Optional[str]) -> str:
    """entry_block_reason(비어있지 않으면 우선) → 표시용 게이트 라벨."""
    r = entry_block_reason or ""
    if r:
        for needle, label in _BLOCK_REASON_CATEGORIES:
            if needle in r:
                return label
        return "기타(%s)" % r[:24]
    cr = checklist_reason or ""
    if cr:
        # position!=FLAT(포지션 보유 중)이라 STEP7 차단문구가 안 찍힌 경우 등 —
        # checklist_reason(콜드스타트/워밍업 단계 표시)으로 대체 분류
        return "콜드스타트/기타(%s)" % cr
    return "기타(미분류)"


def fetch_daily_entry_funnel(date_str: Optional[str] = None) -> Dict:
    """[297차, P1-6] 진입 퍼널 일일 자동 집계 — "어느 층에서 진입0이 발생했는가".

    ensemble_decisions는 매분 무조건 기록되므로(STEP9, dedup 없음) 로그의
    [ZeroDiag]/entry_block_reason 출력(직전 분과 동일하면 dedup되어 스킵)보다
    더 정확하다. ensemble_decisions.grade 컬럼은 앙상블 단계 등급(체크리스트·
    CB③-P4·STEP7 게이트 반영 전)이라는 점에 근거해 5단 퍼널을 재구성한다:

      FLAT → conf미달 / CoherenceGate(앙상블 X) → 게이트차단(STEP7·체크리스트)
           → 후보(entry_final_ok) → 진입(entry_executed)

    coherence_blocked는 conf미달과 같은 분에 동시 발생할 수 있다(코드상 우선순위:
    ensemble_decision.py가 coherence_blocked를 regime_ok보다 먼저 검사) — 이 함수도
    그 우선순위를 따라 coherence_blocked를 conf미달보다 먼저 판정한다.
    coherence_blocked 컬럼은 297차부터 저장되므로, 그 이전 날짜 데이터는 0으로
    나온다(과소 계상 — 로그 재생 없이는 소급 복원 불가, 알려진 한계).

    반환: {"date", "total", "flat", "conf_fail", "coherence_blocked",
           "ensemble_pass", "gate_blocked", "gate_breakdown": {label: n},
           "exec_fail", "candidate", "entered"}
    """
    import datetime as _dt
    d = date_str or _dt.date.today().isoformat()
    rows = fetchall(
        PREDICTIONS_DB,
        """SELECT direction, regime_ok, grade, entry_final_ok, entry_executed,
                  entry_block_reason, checklist_reason, coherence_blocked
           FROM ensemble_decisions
           WHERE substr(ts, 1, 10) = ?""",
        (d,),
    )
    out = {
        "date": d, "total": len(rows),
        "flat": 0, "conf_fail": 0, "coherence_blocked": 0,
        "ensemble_pass": 0, "gate_blocked": 0, "gate_breakdown": {},
        "exec_fail": 0, "candidate": 0, "entered": 0,
    }
    for r in rows:
        direction = int(r["direction"] or 0)
        if direction == 0:
            out["flat"] += 1
            continue
        grade = str(r["grade"] or "")
        if grade == "X":
            if bool(r["coherence_blocked"]):
                out["coherence_blocked"] += 1
            else:
                out["conf_fail"] += 1
            continue

        out["ensemble_pass"] += 1
        final_ok = bool(r["entry_final_ok"])
        executed = bool(r["entry_executed"])
        if executed:
            out["candidate"] += 1
            out["entered"] += 1
        elif final_ok:
            out["candidate"] += 1
            out["exec_fail"] += 1
        else:
            out["gate_blocked"] += 1
            label = _categorize_block_reason(r["entry_block_reason"], r["checklist_reason"])
            out["gate_breakdown"][label] = out["gate_breakdown"].get(label, 0) + 1
    return out


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
               SUM(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(COALESCE(forward_net_pnl_krw, forward_pnl_krw, net_pnl_krw, pnl_krw)), 0) AS pnl_krw
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
               SUM(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(COALESCE(forward_net_pnl_krw, forward_pnl_krw, net_pnl_krw, pnl_krw)), 0) AS pnl_krw
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
               SUM(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(COALESCE(forward_net_pnl_krw, forward_pnl_krw, net_pnl_krw, pnl_krw)), 0) AS pnl_krw
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
               SUM(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN COALESCE(forward_pnl_pts, pnl_pts) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(COALESCE(forward_net_pnl_krw, forward_pnl_krw, net_pnl_krw, pnl_krw)), 0) AS pnl_krw
        FROM trades
        WHERE exit_ts IS NOT NULL
        GROUP BY strftime('%Y', entry_ts)
        ORDER BY year DESC
    """)]


def init_daily_broker_pnl_db():
    """브로커 일별 실현손익 테이블 생성 (CpTd6197 실제 정산값 보관)"""
    execute(TRADES_DB, """
        CREATE TABLE IF NOT EXISTS daily_broker_pnl (
            date       TEXT PRIMARY KEY,
            pnl_krw    REAL NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)


def upsert_daily_broker_pnl(date: str, pnl_krw: float) -> None:
    """날짜별 브로커 실현손익 저장 (pnl_krw=0 이면 스킵)."""
    if not date or pnl_krw == 0.0:
        return
    import datetime as _dt
    execute(TRADES_DB,
            "INSERT OR REPLACE INTO daily_broker_pnl (date, pnl_krw, updated_at) VALUES (?, ?, ?)",
            (date, float(pnl_krw), _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def fetch_broker_daily_pnl_map(days: int = 90) -> Dict[str, float]:
    """날짜 → 브로커 실현손익(원) 딕셔너리 반환."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days)).isoformat()
    rows = fetchall(TRADES_DB,
                    "SELECT date, pnl_krw FROM daily_broker_pnl WHERE date >= ? ORDER BY date",
                    (cutoff,))
    return {r["date"]: float(r["pnl_krw"]) for r in rows}


def save_regime_at(ts: str, regime: str) -> None:
    """매분 레짐 결과를 regime_history에 저장 (재시작 시 복원용)."""
    if not ts or not regime:
        return
    execute(RAW_DATA_DB, "INSERT OR REPLACE INTO regime_history (ts, regime) VALUES (?, ?)", (ts, regime))


def fetch_regime_today(today_str: str = None) -> dict:
    """오늘 날짜 레짐 히스토리를 {ts: regime} dict로 반환."""
    import datetime as _dt
    if today_str is None:
        today_str = _dt.date.today().isoformat()
    rows = fetchall(RAW_DATA_DB, "SELECT ts, regime FROM regime_history WHERE ts LIKE ?", (today_str + "%",))
    return {row["ts"]: row["regime"] for row in rows}


def fetch_direction_today(today_str: str = None) -> dict:
    """오늘 날짜 앙상블 방향 이력을 {ts: direction_int} dict로 반환 (방향 바 재시작 복원용).

    ensemble_decisions 테이블을 직접 읽으므로 별도 저장 없이 복원 가능.
    """
    import datetime as _dt
    if today_str is None:
        today_str = _dt.date.today().isoformat()
    rows = fetchall(
        PREDICTIONS_DB,
        "SELECT ts, direction FROM ensemble_decisions WHERE ts LIKE ?",
        (today_str + "%",),
    )
    return {row["ts"]: int(row["direction"] or 0) for row in rows}


def purge_old_regime_history(keep_days: int = 30) -> None:
    """keep_days 이전 레짐 히스토리 삭제 (EOD 마감 시 1회 호출)."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=keep_days)).isoformat()
    execute(RAW_DATA_DB, "DELETE FROM regime_history WHERE ts < ?", (cutoff,))


def record_exchange_cb_halt(start_ts: str, end_ts: str, gap_min: int) -> None:
    """[303차] 거래소 CB(단일가/서킷브레이커) 해제 시점에 halt 구간 1건 기록.

    분봉 미수신 + Cybos 연결 정상 조합으로 감지된 구간만 기록되므로(main.py
    ExchangeCB 상태머신), API 지연·연결 끊김으로 인한 공백과는 구분된다.
    """
    if not start_ts or not end_ts:
        return
    execute(
        RAW_DATA_DB,
        "INSERT OR REPLACE INTO exchange_cb_halts (start_ts, end_ts, gap_min) VALUES (?, ?, ?)",
        (start_ts, end_ts, int(gap_min)),
    )


def fetch_daily_exchange_cb_halts(date_str: Optional[str] = None) -> Dict:
    """[303차] 오늘(또는 date_str) 거래소 CB halt 구간 요약 — EOD 리포트용.

    반환: {"date", "count", "total_gap_min", "events": [{"start","end","gap_min"}, ...]}
    """
    import datetime as _dt
    d = date_str or _dt.date.today().isoformat()
    rows = fetchall(
        RAW_DATA_DB,
        "SELECT start_ts, end_ts, gap_min FROM exchange_cb_halts WHERE start_ts LIKE ? ORDER BY start_ts",
        (d + "%",),
    )
    events = [
        {"start": r["start_ts"], "end": r["end_ts"], "gap_min": int(r["gap_min"])}
        for r in rows
    ]
    return {
        "date": d,
        "count": len(events),
        "total_gap_min": sum(e["gap_min"] for e in events),
        "events": events,
    }


def purge_old_exchange_cb_halts(keep_days: int = 30) -> None:
    """keep_days 이전 거래소 CB halt 이력 삭제 (EOD 마감 시 1회 호출)."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=keep_days)).isoformat()
    execute(RAW_DATA_DB, "DELETE FROM exchange_cb_halts WHERE start_ts < ?", (cutoff,))


def init_all_dbs():
    """전체 DB 초기화 (main.py에서 1회 호출)"""
    init_predictions_db()
    init_trades_db()
    init_daily_stats_db()
    init_shap_db()
    init_raw_data_db()
    init_daily_broker_pnl_db()
