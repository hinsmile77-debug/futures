# utils/db_utils.py — SQLite 공통 유틸리티
import sqlite3
import logging
import os
import sys
import threading
from contextlib import contextmanager
from typing import List, Tuple, Any, Optional, Dict

import json
from config.constants import FUTURES_PT_VALUE, get_contract_spec
from config.settings import PREDICTIONS_DB, SHAP_DB, TRADES_DB, RAW_DATA_DB, DB_DIR, DATA_DIR
from config.settings import FUTURES_COMMISSION_RATE

_lock = threading.Lock()
TRADE_PNL_FORMULA_VERSION = 4  # v4: pt_value 종목코드 연동 (미니선물 50k, 일반선물 250k)
# [459차 F1] daily_stats.wins 집계 단위. v1=레그(청산 행) 단위 — 부분청산 포지션의
# 승패를 **마지막 레그**의 pnl_pts로 판정해 순손실 포지션이 승으로 기록됐다.
# v2=포지션 단위(레그 누적 총합). 과거 행은 소급 수정하지 않으므로 컬럼이 NULL인
# 날짜가 v1 구간이다(2026-08-10 전환 — dev_memory/DECISION_LOG.md 459차).
WIN_COUNT_FORMULA_VERSION = 2
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

    # ── [MW0601 453차 D3] 멱등 쓰기 — UNIQUE 인덱스 + 기존 중복 정리 ──────────
    # 왜: predictions는 plain INSERT + UNIQUE 제약 없음이라 복구 재실행·장중 재시작이
    # (ts,horizon) 중복을 만들었다(실측 423그룹, 영구 미채점 고아 800행 — 채점기가
    # fetchone으로 한 행만 채점하고 나머지는 actual NULL로 방치된다). 쓰기 계층이
    # `INSERT OR IGNORE`로 바뀌었으므로(prediction_buffer.py) 제약이 반드시 필요하다
    # — OR IGNORE는 **제약이 있어야만** 동작한다.
    # 패턴: 인덱스 생성 시도 → 실패(중복 잔존) 시 정리 후 재시도. IF NOT EXISTS라
    # 이미 있으면 no-op — 매 기동마다 무거운 검사를 하지 않는다.
    # ⚠ revert 시 이 인덱스를 DROP하지 않으면 plain INSERT가 IntegrityError로 죽는다.
    for _ux_sql, _dedupe_fn in [
        ("CREATE UNIQUE INDEX IF NOT EXISTS ux_pred_ts_hz ON predictions(ts, horizon)",
         _dedupe_predictions_for_unique_index),
        ("CREATE UNIQUE INDEX IF NOT EXISTS ux_ens_ts ON ensemble_decisions(ts)",
         _dedupe_ensemble_for_unique_index),
    ]:
        try:
            execute(PREDICTIONS_DB, _ux_sql)
        except Exception:
            try:
                _dedupe_fn()
                execute(PREDICTIONS_DB, _ux_sql)
            except Exception as _ux_e:
                # init_all_dbs를 죽이면 안 된다 — 인덱스 없으면 OR IGNORE가 무제약
                # plain INSERT처럼 동작할 뿐(종전과 동일), 시스템은 계속 돈다.
                logging.getLogger("SYSTEM").error(
                    "[D3] UNIQUE 인덱스 생성 실패 — 중복 차단 미가동(종전 동작 유지): %s",
                    _ux_e)

    # WAL 파일이 하루종일 비대해지는 것을 방지 (기본 1000 → 100페이지)
    execute(PREDICTIONS_DB, "PRAGMA wal_autocheckpoint=100")


def _dedupe_predictions_for_unique_index():
    """[MW0601 453차 D3] (ts,horizon) 중복 정리 — UNIQUE 인덱스 생성 전 1회.

    남길 행: 그룹당 1행 — **채점된 행(actual NOT NULL) 우선**, 동급이면 최소 id.
    (STEP 1 채점기가 fetchone=최소 id를 채점하므로 대개 일치한다. 라벨 보존이 목적.)
    삭제 대상은 지우기 전에 `predictions_dup_archive`로 옮긴다 — 860MB DB 파일
    복사 대신 행 단위 아카이브(`_purge_extreme_conf.py`의 predictions_archive 선례).
    """
    with _lock:
        with get_conn(PREDICTIONS_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS predictions_dup_archive AS "
                "SELECT * FROM predictions WHERE 0")
            # victim 판정: 같은 (ts,horizon)에 나보다 우선하는 행이 존재하면 나는 victim.
            # 우선순위 — ① 채점행 > 미채점행 ② 같은 급이면 작은 id.
            conn.execute("""
                CREATE TEMP TABLE _dup_victims AS
                SELECT p.id AS id FROM predictions p
                WHERE EXISTS (
                  SELECT 1 FROM predictions q
                  WHERE q.ts = p.ts AND q.horizon = p.horizon AND q.id != p.id
                    AND (
                      (q.actual IS NOT NULL AND p.actual IS NULL)
                      OR ((q.actual IS NULL) = (p.actual IS NULL) AND q.id < p.id)
                    )
                )""")
            n = conn.execute("SELECT COUNT(*) FROM _dup_victims").fetchone()[0]
            conn.execute("INSERT INTO predictions_dup_archive "
                         "SELECT * FROM predictions "
                         "WHERE id IN (SELECT id FROM _dup_victims)")
            conn.execute("DELETE FROM predictions "
                         "WHERE id IN (SELECT id FROM _dup_victims)")
            conn.execute("DROP TABLE _dup_victims")
            logging.getLogger("SYSTEM").warning(
                "[D3] predictions 중복 정리: %d행 → predictions_dup_archive 이동", n)


def _dedupe_ensemble_for_unique_index():
    """[MW0601 453차 D3] ensemble_decisions ts 중복 정리 — 최소 id만 남긴다."""
    with _lock:
        with get_conn(PREDICTIONS_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS ensemble_dup_archive AS "
                "SELECT * FROM ensemble_decisions WHERE 0")
            conn.execute("""
                CREATE TEMP TABLE _dup_victims AS
                SELECT e.id AS id FROM ensemble_decisions e
                WHERE EXISTS (
                  SELECT 1 FROM ensemble_decisions f
                  WHERE f.ts = e.ts AND f.id < e.id
                )""")
            n = conn.execute("SELECT COUNT(*) FROM _dup_victims").fetchone()[0]
            conn.execute("INSERT INTO ensemble_dup_archive "
                         "SELECT * FROM ensemble_decisions "
                         "WHERE id IN (SELECT id FROM _dup_victims)")
            conn.execute("DELETE FROM ensemble_decisions "
                         "WHERE id IN (SELECT id FROM _dup_victims)")
            conn.execute("DROP TABLE _dup_victims")
            logging.getLogger("SYSTEM").warning(
                "[D3] ensemble_decisions 중복 정리: %d행 → ensemble_dup_archive 이동", n)


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
                # [MW0601 471차 F-4] 동시 성립 차단 축 전량(세미콜론 구분 안정 키).
                # `entry_block_reason`은 STEP7 elif 체인의 **1등 사유 하나**뿐이라
                # 같은 분봉에 두 축이 동시에 성립하면 하나가 통째로 사라진다 —
                # 2026-08-14 09:39·11:24에 로그는 `Degraded 선제차단`, DB는 `등급X`로
                # 갈렸다. 기존 컬럼을 목록으로 바꾸지 않은 이유는 그 컬럼을 읽는
                # 부분문자열 분류기 3곳(_categorize_block_reason·
                # generate_gate_blocking_report·캠페인 LIKE)의 집계가 조용히
                # 재정의돼 과거 시계열과 불연속이 생기기 때문(461차 mdd_pct 유형).
                "entry_block_axes": "TEXT",
                # [MW0601 471차 후속6 / G-1] 사이징 계보 구조체(JSON).
                # 수량 계보(사이저원본→안전군→표시→최종) + 품질군 배수 전량 +
                # argmin(binding_gate) + 상한 2종. `[SizerMatch]` 로그 문자열을
                # 파싱하던 판정을 구조화 질의로 대체한다 — 게이트가 하나 늘 때마다
                # 파서를 고쳐야 하는 구조를 끝낸다(2026-08-14 P1-2 오귀속의 근본원인).
                # ⚠ 사이저가 돌지 않은 분(무신호·포지션 보유중)은 NULL = 미측정.
                "sizing_trace": "TEXT",
                # [MW0601 471차 후속4 / F-9] `entry_mode`가 폴백값인가(0/1).
                # `manual`은 A·B·C 전 등급을 허용하는 **가장 넓은 모드**인데 정상
                # 설정값도 `manual`이라(실측 manual 11,590행 / hybrid 35행) 이 플래그
                # 없이는 "대시보드 예외로 넓어진 행"을 사후에 가려낼 수 없다.
                # 471차 이전 행은 NULL = 미측정(계측 4원칙 ②·④).
                "entry_mode_fallback": "INTEGER",
                # 같은 건의 짝 — Degraded 선제차단 lookahead가 그 분에 발화했는가.
                # "진입이 막혔는가"와 다른 사실이다(막지 않아도 발화한다).
                # 471차 이전 행은 NULL = **미측정**이며 0(미발화)이 아니다(계측 4원칙 ②).
                "health_preblock": "INTEGER",
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
                # [conf(ema) 딥다이브, 2026-07-28, 개선안2] 지금까지 ensemble_decision.py가
                # 계산은 하지만 DB에 저장되지 않아 코드 추적으로만 재구성 가능했던 두 값을
                # 실제 저장 — 근본원인 재확인 시 쿼리 한 번으로 확인 가능하게 한다.
                "confidence_raw": "REAL",       # 캘리브레이션 이전 원본 confidence
                "confidence_smoothed": "REAL",  # P4 display용 EMA(span=20)
                # [MW0601 422차 후속 / 채널 [34]] MetaGate가 클램프·폴백을 적용하기
                # **전**의 원 사이즈 배수(learning/meta_confidence.py:_make_result()).
                # meta_size_mult(적용 후)만으로는 "모델이 0을 냈는데 클램프가 올린 것"과
                # "모델이 그 값을 낸 것"을 구분할 수 없다 — 두 경로 모두 정보를 지운다:
                #   reduce: `learned["size_multiplier"] or 0.5`      → 0.0이 falsy → 0.5
                #   take:   `max(0.9, min(1.25, size_multiplier))`   → 0.0 → **0.9**
                # take 쪽 왜곡(0.0→0.9)이 reduce(0.0→0.5)보다 큰데 419·420차는 reduce의
                # `or 0.5`만 계측했다. 진입한 신호의 raw는 지금까지 어디에도 남지 않아
                # (joint_gate_shadow는 **차단된** 신호 전용) take 밴드는 판정 자체가
                # 불가능했다. 캠페인 실측: take&0.900 버킷 26진입 -903,986원인데 그중
                # raw==0 비율을 알 수 없다.
                # NULL 허용 — MetaGate FLAT early-return 경로는 이 키를 반환하지 않는다
                # (action='skip'이라 [34] 모집단 밖이므로 NULL이 정직하다).
                # 소급 백필 없음: 결정 시점에만 알 수 있는 값이라 복원 불가(420차와 동일).
                "meta_size_raw": "REAL",
                # [conf(ema) 딥다이브, 개선안1] 실질 가중합 0 붕괴(WeightCollapse) 발동 여부.
                # 콜드스타트 좁은 활성창에서 유일 활성 호라이즌이 그 분에 배포되지 않아
                # 안전망(flat_score=1.0)이 발동한 케이스 표시 — 발생 빈도 계량용.
                "weight_collapsed": "INTEGER",
                # ── [MW0601 473차 / F-8] 극단 스프레드 섀도 계측 ──────────────
                # ToxicityGate가 매분 계산하던 `signals.spread_extreme_shadow`가
                # **어디에서도 소비되지 않았다** — 2026-07-12 도입 이래 한 달 넘게
                # 죽은 섀도였고, 그래서 실전 전환 기준 ⑨의 복원 판단 근거를 만들
                # 수 없었다(FP-CRITICAL이 "저장 함수가 호출된 적 없어 2개월간
                # PSI=0.0"이던 것과 같은 결함 패턴).
                #
                # 🔵 단, `spread_ticks` **원값은 이미 남아 있었다** — `features`
                #   JSON(141키) 안에. 2026-08-17 전수 파싱: 24,113행 보유,
                #   max 104.9988, >=20틱 911행(3.8%). 그래서 이 두 컬럼은
                #   "없던 데이터를 새로 만드는 것"이 아니라 **질의 가능하게 꺼내는
                #   것**이다. 141키 JSON 파싱은 매주 리포트가 감당할 비용이 아니다.
                #
                # ⚠ 473차 이전 행은 NULL = **미측정**이지 "스프레드 0"이 아니다.
                #   대조 시 `features` JSON에서 복원할 수 있으나(sizing_trace와
                #   다른 점), 소급 백필은 하지 않았다 — 원본이 살아 있으므로
                #   백필로 사본을 만들 이유가 없고, 백필하면 "언제부터 컬럼이
                #   실제로 채워졌는가"를 잃는다.
                # ⚠ `spread_ticks = 0.0`은 호가 결측 폴백일 수 있다
                #   (`features/feature_builder.py:516`). 판독기가 반드시 가른다.
                "spread_ticks": "REAL",
                "spread_extreme_shadow": "INTEGER",
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
    # [327차] JointGateBlock(MetaGate×ToxicityGate 결합) counterfactual 섀도우 —
    # hurst_gate_shadow와 동일 패턴. meta_size/tox_size/joint_mult을 함께 저장해
    # "차단이 손실을 막았는지"뿐 아니라 "차단 여부가 joint_mult 값과 실제로
    # 상관있는지"(tox_size가 상수 0.7이라 사실상 meta_size 단일 임계와 동치라는
    # 구조적 의문, 07-14 실측 분석 참조)까지 사후 분석할 수 있게 한다.
    # 리포트 전용 계측 테이블 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS joint_gate_shadow (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        ts            TEXT NOT NULL,           -- 차단 시각 (분봉)
        direction     TEXT NOT NULL,           -- LONG/SHORT (차단된 가상 방향)
        grade         TEXT,                    -- 차단 당시 진입 등급 (A/B/C)
        meta_size     REAL,                    -- 차단 당시 MetaGate size_multiplier
        tox_size      REAL,                    -- 차단 당시 ToxicityGate size_multiplier
        joint_mult    REAL,                    -- meta_size × tox_size
        conf          REAL,                    -- 차단 당시 confidence
        entry_price   REAL NOT NULL,           -- 가상 진입가 (분봉 종가)
        stop_price    REAL,                    -- 가상 하드스톱
        tp1_price     REAL,                    -- 가상 TP1
        resolved      INTEGER DEFAULT 0,       -- 1=counterfactual 판정 완료
        cf_outcome    TEXT,                    -- STOP / TP1 / NEITHER
        cf_exit_price REAL,                    -- counterfactual 청산가
        hyp_pnl_pts   REAL,                    -- (+)=차단 안 했으면 이득, (-)=차단이 손실 회피
        -- [404차 후속9 / P1-D] 30분 창 최대 유리폭·불리폭. hyp_pnl_pts가 현행 TP1
        -- (ATR×0.3~0.5) 청산을 가정해 추세일 차단 비용을 과소평가하는 문제를 계측한다
        -- (0731 리포트 §2-E). resolve 시점에 채워지며, 기존 DB는 리포트 스크립트의
        -- _ensure_shadow_mfe_columns()가 ALTER로 보강한다(CREATE IF NOT EXISTS는
        -- 이미 있는 테이블을 갱신하지 않으므로 이 정의만으로는 부족하다).
        mfe_30m       REAL,
        mae_30m       REAL,
        -- ── [MW0601 420차] 419차 반영 계측 보강 ──────────────────────────
        -- 세 가지를 사후 분리할 수 있게 한다. 기존 DB는 리포트 스크립트의
        -- _ensure_joint_gate_columns()가 ALTER로 보강한다(mfe_30m과 동일 사정).
        --
        -- (1) meta축 — 419차 발견 ④의 "meta_size 73/116이 정확히 0.500"이
        --     학습값인지 falsy 폴백인지 구분한다. learning/meta_confidence.py의
        --     _make_result()는 conf<0.5에서 size_mult=0.0을 내는데
        --     strategy/entry/meta_gate.py의 `learned["size_multiplier"] or 0.5`가
        --     그 0.0을 falsy로 잡아 0.5로 **승격**시킨다(약한 신호를 키우는 방향).
        --     게다가 meta_conf는 그 뒤 <0.20이면 0.45로 floor되는데
        --     size_multiplier는 floor 전 raw로 이미 확정돼 있어 두 축이 어긋난다.
        --     → raw/보정 두 값을 모두 남겨야 어느 쪽이 원인인지 사후에 갈린다.
        meta_conf          REAL,    -- MetaGate 보정 후 meta_conf (blended 산출에 실제 사용)
        meta_conf_raw      REAL,    -- predict_confidence 원값 (size_multiplier 산출 근거)
        meta_size_raw      REAL,    -- 클램프·폴백 전 learned["size_multiplier"] (0.0 포함)
        meta_size_fallback INTEGER,  -- 1 = `or 0.5` 폴백이 발동 (raw가 falsy)
        -- (2) tox축 체제 — 419차 P0이 TOXICITY_CANCEL_CHURN_CEILING을 0.08→0.42로
        --     재보정해 tox 밴드 분포가 이동했다(block 23.3→8.6% / reduce 76.4→73.7%
        --     / pass 0.27→17.7%). JointGateBlock 발동 전제가 tox_action=="reduce"라
        --     이 채널의 **모집단 자체**가 2026-08-03부터 바뀐다. 날짜 상수로만 가르면
        --     ceiling이 또 바뀔 때 침묵하므로 발동 시점 값을 행에 새겨 자기기술적으로
        --     만든다(리포트가 config 날짜 경계와 이 값의 정합성을 교차확인한다).
        tox_score          REAL,    -- 차단 당시 toxicity_score
        tox_score_ma       REAL,    -- 차단 당시 toxicity_score_ma
        tox_ceiling        REAL,    -- 차단 당시 TOXICITY_CANCEL_CHURN_CEILING (체제 태그)
        -- (3) 419차 P1의 사각지대 = **차단 축**. [31] toxicity_reduce_mult_shadow는
        --     실제로 체결된 reduce 밴드 진입만 본다 — JointGateBlock으로 차단된
        --     신호는 그 채널에 아예 들어가지 않는다. 그런데 연속 배수가 실적용되면
        --     joint_mult이 바뀌어 **차단 여부 자체가 뒤집힐 수 있다**
        --     (예: meta 0.714 × tox_shadow 0.90 = 0.643 ≥ 0.50 → 차단 해제).
        --     여기서 그 반사실을 기록해야 P1 실적용 판단에 차단 축 근거가 생긴다.
        tox_size_shadow    REAL,    -- 419차 P1 연속 배수 (섀도, 실사이징 미관여)
        joint_mult_shadow  REAL,    -- meta_size × tox_size_shadow
        would_block_shadow INTEGER,  -- 1 = 연속 배수였어도 차단됐을 것 (<0.50)
        -- (4) [MW0602 456차] **무정보 폴백 축**. 위 (1)의 meta_size_fallback은 폴백
        --     발동 여부만 남길 뿐, "폴백을 중립(1.0)으로 봤다면 이 차단이 풀렸는가"는
        --     기록하지 않았다. 431차가 사이징 경로만 중립화하고 차단 경로는 캠페인 [7]
        --     PASS 판정 때문에 의도적으로 남겨뒀는데, 그 결정을 재검토하려면 바로 이
        --     반사실 표본이 있어야 한다(2026-08-10 실측: 폴백이 MetaGate 발동의 25.9%).
        --     `JOINT_GATE_META_FALLBACK_NEUTRAL` 플래그와 **무관하게** 항상 적재한다 —
        --     OFF인 동안 표본을 모으는 것이 이 컬럼의 존재 이유다.
        meta_neutral_pass  INTEGER,  -- 1 = 폴백 중립화였다면 차단이 풀렸을 신호
        created_at    TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_jgs_ts ON joint_gate_shadow(ts)")
    # [MW0601 420차] 위 CREATE는 **이미 존재하는 테이블을 갱신하지 않는다**. 두 PC가
    # 각자 로컬 trades.db를 갖고 있어 기존 DB에는 420차 컬럼이 없고, main.py의
    # INSERT는 컬럼명을 명시하므로 그대로 두면 매 차단마다 조용히 실패한다
    # (예외를 삼키고 warning만 남기는 경로라 표본이 통째로 유실된다).
    # → 기동 시 멱등 ALTER. 리포트 스크립트에도 같은 보강이 있으나 그쪽은 주간
    #   실행이라 라이브 기록을 지켜주지 못한다. 여기가 1차 방어선이다.
    _jgs_migrate = [
        ("meta_conf", "REAL"), ("meta_conf_raw", "REAL"),
        ("meta_size_raw", "REAL"), ("meta_size_fallback", "INTEGER"),
        ("tox_score", "REAL"), ("tox_score_ma", "REAL"), ("tox_ceiling", "REAL"),
        ("tox_size_shadow", "REAL"), ("joint_mult_shadow", "REAL"),
        ("would_block_shadow", "INTEGER"),
        ("meta_neutral_pass", "INTEGER"),   # [MW0602 456차]
    ]
    try:
        _jgs_have = {r[1] for r in fetchall(
            TRADES_DB, "PRAGMA table_info(joint_gate_shadow)")}
        for _c, _t in _jgs_migrate:
            if _c not in _jgs_have:
                execute(TRADES_DB,
                        "ALTER TABLE joint_gate_shadow ADD COLUMN %s %s" % (_c, _t))
    except Exception as _jgs_mig_e:
        # 이 모듈에는 logger가 없다(설계상 순수 유틸). 조용히 넘기면 라이브 기록이
        # 통째로 유실되므로 stderr로는 반드시 남긴다 — EOD 로그에서 보인다.
        print("[DB][WARN] joint_gate_shadow 컬럼 마이그레이션 실패: %s" % _jgs_mig_e,
              file=sys.stderr)
    # [354차] OPEN_VOLATILE 시가이격 필터(§14, ATR×5) counterfactual 섀도우 —
    # hurst_gate_shadow·joint_gate_shadow와 완전히 동일한 패턴. 이 필터는 09:05~10:30
    # 구간에서 세션 시가(고정 기준점) 대비 gap이 ATR×5를 넘는 TREND_FOLLOW 신호를
    # 차단하는데, 기준점이 고정이고 임계 자체도 장중 ATR 압축으로 좁아지는 구조적
    # 결함이 있다고 판단됐으나(2026-07-16 정기점검 P2-d) 실측 피해 사례가 아직 없어
    # 재설계는 보류하고 이 채널로 "차단이 실제로 손실을 회피했는지"를 자동 관찰한다.
    # 리포트 전용 계측 테이블 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS open_gap_shadow (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        ts            TEXT NOT NULL,           -- 차단 시각 (분봉)
        direction     TEXT NOT NULL,           -- LONG/SHORT (차단된 가상 방향)
        grade         TEXT,                    -- 차단 당시 진입 등급 (A/B/C, gap 미차단 가정)
        gap_pt        REAL,                    -- 차단 당시 방향이탈(gap_in_dir) pt
        atr_at_block  REAL,                    -- 차단 당시 ATR
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
            "CREATE INDEX IF NOT EXISTS idx_ogs_ts ON open_gap_shadow(ts)")
    # [신설] ToxicityGate(strategy/risk/toxicity_gate.py) action="block" counterfactual
    # 섀도우 — open_gap_shadow와 완전히 동일한 패턴(발동 시점 가상 진입가·스톱·TP1
    # 기록 → resolve_and_eval_toxicity_block()이 주간 사후 판정). 380차가 toxicity_score
    # 계측 자체는 재설계·재보정했지만 "block이 실제로 옳은 차단이었는지"는 아직
    # 검증 수단이 없었다(근사치 방향적중률뿐) — 이 채널로 TP1/STOP 시뮬레이션 기반
    # 정식 계측을 추가한다. action="reduce"는 사이즈만 축소될 뿐 실제 체결이 그대로
    # 발생해 trades 테이블에 실거래로 남으므로 별도 섀도우 불필요(action="block"만 대상).
    # 리포트 전용 계측 테이블 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS toxicity_block_shadow (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        ts             TEXT NOT NULL,           -- 차단 시각 (분봉)
        direction      TEXT NOT NULL,           -- LONG/SHORT (차단된 가상 방향)
        grade          TEXT,                    -- 차단 당시 진입 등급 (A/B/C, toxicity 미차단 가정)
        toxicity_score REAL,                    -- 차단 당시 toxicity_score
        toxicity_score_ma REAL,                 -- 차단 당시 toxicity_score_ma
        conf           REAL,                    -- 차단 당시 confidence
        entry_price    REAL NOT NULL,           -- 가상 진입가 (분봉 종가)
        stop_price     REAL,                    -- 가상 하드스톱
        tp1_price      REAL,                    -- 가상 TP1
        resolved       INTEGER DEFAULT 0,       -- 1=counterfactual 판정 완료
        cf_outcome     TEXT,                    -- STOP / TP1 / NEITHER
        cf_exit_price  REAL,                    -- counterfactual 청산가
        hyp_pnl_pts    REAL,                    -- (+)=차단 안 했으면 이득, (-)=차단이 손실 회피
        created_at     TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_tbs_ts ON toxicity_block_shadow(ts)")
    # [MW0601 419차 / P1] ToxicityGate reduce 밴드 **연속 배수** 섀도우 —
    # exec_1m_shadow와 동일 계열(실제로 체결된 진입에 진단 태그를 붙이는 방식)이라
    # counterfactual 가격 시뮬레이션이 불필요하다. ts로 trades.entry_ts와 조인해
    # 실현 pnl을 그대로 가져다 쓴다.
    #
    # 계기: reduce 밴드가 밴드 전체를 상수 size_multiplier=0.7 하나로 매핑하는데
    # (joint_gate_shadow 116건 전수에서 tox_size가 예외 없이 정확히 0.7), 밴드
    # **내부**에서 toxicity_score는 실제로 단조 등급성을 갖는다 — 라이브
    # 2026-07-24~07-31 reduce 밴드(n=1,614) 5분위에서 향후 15m 평균스프레드
    # 2.8→3.8틱, 15m 실현레인지 9.52→13.70pt, Spearman rho=+0.319/+0.260
    # (t=13.48/10.81). 상수 0.7이 유의한 정보를 폐기하고 있다는 뜻이다.
    #
    # ⚠ qty_after_* 두 컬럼은 **tox 스테이지 국소 결과**다 — main.py의 사이징 체인은
    # tox 뒤로도 L2·Hurst·Degraded·MAX_CONTRACTS 상한이 각각 max(1, round())로
    # 이어지는데 그 하류를 재시뮬레이션하지 않는다. 따라서 "실제 진입 수량이 이만큼
    # 달라졌을 것"이 아니라 "이 스테이지에서 달라질 여지가 있었는가"의 1차 지표다.
    # 두 값이 같으면 하류가 무엇이든 최종 수량도 같다(입력이 동일하므로) — 즉
    # **차이 0건이면 연속화의 실효가 0임이 확정**되고, 차이가 있을 때만 후속 판단거리가
    # 생긴다. 실제 최종 체결 수량은 qty_entered에 따로 기록한다.
    # 리포트 전용 계측 테이블 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS toxicity_reduce_shadow (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        ts                TEXT NOT NULL,         -- 진입 분봉 (trades.entry_ts 조인키)
        direction         TEXT NOT NULL,         -- LONG/SHORT (실제 체결 방향)
        grade             TEXT,                  -- 진입 등급 (A/B/C)
        toxicity_score    REAL,                  -- 진입 당시 toxicity_score
        toxicity_score_ma REAL,                  -- 진입 당시 toxicity_score_ma
        spread_ticks      REAL,                  -- 진입 당시 스프레드 (밴드 진입 경로 판별용)
        tox_action        TEXT,                  -- pass / reduce / block
        tox_size_applied  REAL,                  -- 실제 적용된 배수 (reduce면 상수 0.7)
        tox_size_shadow   REAL,                  -- 연속 배수(섀도) — 적용되지 않음
        qty_before_tox    REAL,                  -- tox 스테이지 진입 시점 수량
        qty_after_applied REAL,                  -- max(1, round(qty_before × applied))
        qty_after_shadow  REAL,                  -- max(1, round(qty_before × shadow))
        qty_entered       REAL,                  -- 하류 스테이지까지 거친 최종 체결 수량
        created_at        TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_trs_ts ON toxicity_reduce_shadow(ts)")
    # ── [MW0601 431차 / Phase 2-1, 2026-08-05] 신뢰도 배수 재매핑 섀도우 ───────────
    #
    # 계기: `PositionSizer.CONFIDENCE_MULT_TABLE`의 임계(0.58/0.60/0.65/0.70)가 라이브
    # 신뢰도 분포와 **정의역이 어긋나** 상위 4단이 도달 불가다. 실측(2026-07-16~08-04):
    #   · 방향 있는 사이클 n=2,540 — p50=0.346 / p90=0.402 / p95=0.425 / **max=0.628**
    #   · conf >= 0.58 비율 **0.20%**, >= 0.65 **0.00%**
    #   · 그래서 `[Sizer]` 로그의 신뢰도배수가 652건 중 **649건(99.5%)이 최하단 0.6 고정**
    # 즉 사이저의 "신뢰도" 축은 상수나 다름없고, 계약수 변동은 사실상 ATR·등급만 만든다.
    # 417차가 잡은 `trades.quantity` 단위 불일치와 같은 계열(정의역 불일치)의 계측 결함.
    #
    # **왜 바로 안 고치고 섀도인가**: 임계를 실측 분위수로 옮기는 것은 배수 값 자체는
    # 그대로 두더라도 사후 데이터로 사이징을 바꾸는 행위다(313차). 라이브 적용 전에
    # "실제로 얼마나 갈리는가"를 먼저 누적한다. `shadow_*`는 **어떤 사이징 경로도 읽지
    # 않는다** — 기록 전용이며, 승격은 표본 축적 후 주간회의 수동 결정이다.
    #
    # 판독법: `qty_live == qty_shadow`인 행만 쌓이면 재매핑의 실효가 0이다(승격 무의미).
    # 차이가 나는 행이 충분히 모이면 그때 손익과 대조한다. `qty_*`는 **사이저 단계
    # 국소값**이며 하류 게이트 체인(품질군 min 합성·안전군 곱셈·상한)을 재시뮬레이션하지
    # 않는다 — toxicity_reduce_shadow와 동일한 해석 한계.
    # 리포트 전용 계측 테이블 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS conf_mult_shadow (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        ts             TEXT NOT NULL,   -- 진입 분봉 (trades.entry_ts 조인키)
        direction      TEXT NOT NULL,   -- LONG/SHORT (실제 체결 방향)
        grade          TEXT,            -- 진입 등급 (A/B/C)
        confidence     REAL,            -- 사이저에 들어간 앙상블 신뢰도 (재매핑 입력)
        conf_mult_live REAL,            -- 현행 표 배수 (실측상 거의 항상 0.6)
        conf_mult_shad REAL,            -- 재매핑 표 배수 (섀도, 미적용)
        regime_mult    REAL,            -- 동일 사이클 레짐 배수 (교란 분리용)
        grade_mult     REAL,            -- 동일 사이클 등급 배수 (교란 분리용)
        atr            REAL,            -- 동일 사이클 ATR (분모 — 계약수 변동의 실제 주역)
        qty_live       REAL,            -- 사이저가 실제로 낸 수량
        qty_shadow     REAL,            -- 재매핑이었다면 사이저가 냈을 수량
        qty_entered    REAL,            -- 게이트 체인까지 거친 최종 체결 수량
        created_at     TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_cms_ts ON conf_mult_shadow(ts)")
    # [331차 후속2, 2026-07-14] 1m 앙상블 방향투표 퇴역(역스킬 확정) 이후 "1m 활용방안 A"
    # (집행/타이밍 필터) 후보 검증용 섀도우 계측 — hurst_gate_shadow와 달리 차단된
    # 가상 진입이 아니라 **실제로 체결된** 진입에 진단 태그를 붙이는 것이라 counterfactual
    # 가격 시뮬레이션(resolved/cf_outcome)이 불필요함 — entry_ts로 trades 테이블과 조인해
    # 실제 pnl을 그대로 가져다 쓸 수 있음. 목적: 1m GBM 자체 예측(방향·신뢰도)이나 1m
    # 마이크로구조 피처(spread_ticks·toxicity_score)가 실제 체결 품질/승패와 상관이
    # 있는지 라이브 개입 없이 누적 관찰 — 상관이 확인되면 그때 실제 게이트로 승격 검토.
    # 리포트 전용 계측 테이블 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS exec_1m_shadow (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        ts               TEXT NOT NULL,           -- 진입 시각 (분봉, trades.entry_ts와 조인)
        direction        TEXT NOT NULL,           -- LONG/SHORT (실제 진입 방향)
        grade            TEXT,                    -- 진입 등급 (A/B/C)
        spread_ticks     REAL,                    -- 진입 시점 1m 스프레드(틱)
        toxicity_score   REAL,                    -- 진입 시점 1m 독성 점수
        cancel_add_ratio REAL,                    -- 진입 시점 1m 취소/추가 비율
        tox_gate_action  TEXT,                    -- ToxicityGate 판정(block/reduce/pass) 참고용
        tox_gate_score   REAL,                    -- ToxicityGate 산출 score
        hz1m_direction   INTEGER,                 -- 1m GBM 자체 예측 방향 (-1/0/+1)
        hz1m_confidence  REAL,                    -- 1m GBM 자체 confidence
        hz1m_agrees      INTEGER,                 -- 1=1m 예측이 실제 진입방향과 동일, 0=반대/FLAT
        created_at       TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_e1s_ts ON exec_1m_shadow(ts)")
    # ── [MW0601 457차 / G7] 진입 호라이즌 라우터 × 모델 건강도 — 섀도 전용 ──────
    #
    # 계기: `select_entry_horizon()`은 **ATR 밴드 단독 함수**다(모델 품질과 무관).
    #   2026-08-11 실측으로 3m을 **82%** 선택했는데, 하필 그 3m이 하루 6회
    #   ConstOut(상수 출력)으로 앙상블에서 퇴출·복귀를 반복했고 EOD 교체는 7거래일
    #   막혀 있었다. **가장 많은 물량이 가장 관리가 안 되는 모델로 흘러간다.**
    #
    # ⚠ **정책을 바꾸지 않는다 — 이 테이블은 기록만 한다.**
    #   같은 날 대조에서 ConstOut 활성 구간과 진입 시도 시각의 **교집합이 0건**이었다
    #   (진입 10:02/10:04/10:08/10:49/13:24 vs ConstOut 구간 6개 — 13:24는 13:23:01
    #   해소 59초 뒤). 즉 "ConstOut 호라이즌을 라우터에서 빼자"는 조치가 **그날은
    #   아무것도 바꾸지 않았을 것**이다. 효과가 미확인인 상태로 진입 분포를 바꾸는 것은
    #   313차 원칙 위반이라, 얼마나 자주 실제로 물리는지부터 센다.
    #
    # 사전등록: config/settings.py:VALIDATION_CAMPAIGN["router_health_shadow"]
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS router_health_shadow (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        ts             TEXT NOT NULL,        -- 분봉 시각
        chosen_hz      TEXT,                 -- 라우터가 고른 호라이즌 (None=저변동 차단)
        tf             REAL,                 -- threshold_feasibility (라우터 입력)
        const_out_hz   TEXT,                 -- 그 시각 ConstOut 활성 호라이즌 (JSON 배열)
        chosen_degraded INTEGER DEFAULT 0,   -- 1 = 고른 호라이즌이 ConstOut 활성 ← 핵심
        chosen_cv_null INTEGER DEFAULT 0,    -- 1 = 그 호라이즌 배포본이 CV 미검증(F6 사이드카)
        direction      INTEGER,              -- 앙상블 방향 (-1/0/+1)
        grade          TEXT,                 -- 앙상블 등급
        entry_executed INTEGER DEFAULT 0,    -- 1 = 실제 진입까지 갔다
        created_at     TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_rhs_ts ON router_health_shadow(ts)")
    # [339차 후속, 2026-07-16] 1계약 TP1 회계적 분할청산(synthetic partial) 기록 —
    # Cybos 최소 체결단위가 1계약이라 물리적으로 못 쪼개는 포지션이 TP1에 도달했을 때
    # "PARTIAL_EXIT_RATIOS[0](33%)를 그 가격에서 확정했다"고 회계상으로만 남긴다.
    # exec_1m_shadow와 같은 이유로 counterfactual 시뮬레이션(resolved/cf_outcome)이
    # 불필요함 — 차단된 가상 시나리오가 아니라 실제로 TP1에 도달한 사실 그 자체이므로,
    # entry_ts로 trades 테이블과 조인해 최종 실현 pnl과 나란히 비교하면 된다.
    # 리포트 전용 계측 테이블 — 실거래 의사결정(CB/Kelly/사이징)에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS synthetic_partial_exits (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        ts                 TEXT NOT NULL,           -- 발동 시각 (분봉)
        entry_ts           TEXT,                    -- 포지션 진입 시각 (trades.entry_ts 조인 키)
        direction          TEXT NOT NULL,           -- LONG/SHORT
        entry_price        REAL NOT NULL,
        synthetic_price    REAL NOT NULL,           -- TP1 도달 시점 가격(회계상 확정가)
        synthetic_fraction REAL NOT NULL,           -- 회계상 확정 비중 (PARTIAL_EXIT_RATIOS[0])
        synthetic_pnl_pts  REAL NOT NULL,           -- (synthetic_price - entry_price) * mult
        protect_mode       TEXT,                    -- atr_profit 등 (참고용)
        stop_after         REAL,                    -- arm 이후 실제 스탑가(물리적 리스크 관리는 그대로 유지)
        created_at         TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_spe_ts ON synthetic_partial_exits(ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_spe_entry_ts ON synthetic_partial_exits(entry_ts)")
    # [MW0601 406차 / B] atr·protect_offset_pts 영속화 — [25] tp1_protect_offset_shadow가
    # ATR을 `|stop_after - entry| / 0.25`로 **역산**하고 있었는데, 그 역산은 두 경우에 깨진다:
    #   (1) breakeven 모드는 offset=0이라 ATR이 0으로 나와 행 전체가 버려진다
    #       (MW0601 29건 중 25건이 여기 해당 — [25] n=0의 진짜 원인).
    #   (2) position_tracker:749-751의 `if mult*(prev_stop - protected_stop) > 0:
    #       protected_stop = prev_stop` 때문에, 기존 트레일링 스톱이 더 유리하면
    #       stop_after가 "모드가 의도한 offset"이 아니라 트레일링 스톱이 된다.
    #       이 값을 /0.25 하면 ATR과 무관한 숫자가 조용히 나온다. 실측 4/29(13.8%).
    #       **이 함정은 모드와 무관하므로 atr_profit 행에도 걸린다** — MW0602의 [25]도
    #       해당 행에서 오염된 ATR 위에 6개 변형을 쌓고 있을 수 있다(미확인).
    # 두 값 모두 arm_tp1_single_contract_with_mode 호출부에 이미 존재한다 — 새로 계산할
    # 것이 없고 버리고 있었을 뿐이다. protect_offset_pts와 |stop_after-entry|가 다르면
    # 그 행이 (2)에 해당한다는 뜻이라 식별자 역할도 겸한다.
    # 소급 불가 — 기존 행은 NULL이며 [25]가 폴백 경로로 처리한다.
    # [MW0602 436차] arm_ts — 초 해상도 보호전환 시각.
    # 결함: main.py의 INSERT가 `strftime("%Y-%m-%d %H:%M:00")`으로 **초를 리터럴 "00"**
    # 으로 박아 넣어 `ts`가 분 단위로 절삭돼 있었다. `entry_ts`는 초 해상도라
    # (arm - entry) 지연이 최대 ±60초 양자화되고, **67행 중 10행이 물리적으로 불가능한
    # 음수**(-3 ~ -52초)를 갖는다(진입과 같은 분에 arm → 분 시작으로 절삭).
    #
    # 피해는 "부정확"이 아니라 **정보 부재**다. 진입은 매분 파이프라인 끝(초 53~58)에
    # 일어나므로, 같은 분 안의 arm은 기록지연이 `60 - 진입초` = 3~7초로 **항상** 나온다.
    # 즉 그 값은 arm 속도가 아니라 다음 분 경계까지의 잔여시간이며, 분 이하 해상도가
    # 애초에 존재하지 않는다(0806 점검 §6에서 원자료로 실증).
    #
    # ⚠ **`ts`를 초 해상도로 고치면 안 된다** — scripts/tp1_protect_offset_shadow.py:240이
    #   `idx.get(ts)`로 `ts`를 **raw_candles 분봉 인덱스의 키로 직접** 쓴다. 분 절삭이
    #   그 조인의 전제라 그대로 고치면 [25]·[25-B]의 표본이 조용히 0이 된다.
    #   → `ts`는 분 키로 보존하고 초 해상도는 **새 컬럼**으로 분리한다.
    #
    # 왜 필요한가: 0806 점검 §5-1이 "틱 TP1이 보호전환을 앞당겨 러너를 죽였나"를 물었는데,
    # PRE/POST 시간 비교는 `827bd04`가 틱 TP1과 conf passthrough를 **동시 배포**해
    # 영구히 판정 불가다. 남은 유일한 경로는 같은 코드 세대 안에서 **arm 지연 ↔ TP2
    # 완주 상관**을 보는 것인데(캠페인 [50]), 그 측정 수단이 바로 이 컬럼이다.
    # 소급 불가 — 기존 67행은 NULL이며 [50]이 `data_start`로 걸러낸다.
    with get_conn(TRADES_DB) as _spe_conn:
        _spe_cols = {r[1] for r in _spe_conn.execute(
            "PRAGMA table_info(synthetic_partial_exits)").fetchall()}
        for _c in ("atr", "protect_offset_pts"):
            if _c not in _spe_cols:
                _spe_conn.execute(
                    "ALTER TABLE synthetic_partial_exits ADD COLUMN %s REAL" % _c)
        if "arm_ts" not in _spe_cols:
            _spe_conn.execute(
                "ALTER TABLE synthetic_partial_exits ADD COLUMN arm_ts TEXT")
    # [361차] TP2 홀드 A/B 섀도우 — 0720 정기점검 "TP3 도달 0건" 딥다이브 결과, 트레일링
    # 폭이 아니라 qty=2 스테이지 배분(get_stage_plan()이 (1,1,0) 하드코딩, TP2에서 잔량
    # 100% 종료)이 원인으로 확인됨. TP2가 실제로 전량 종료되는 순간 "이 계약을 홀드해서
    # TP3/트레일링까지 갔다면 어땠을까"를 hurst_gate_shadow와 동일한 패턴(발동 시점 상태
    # 기록 → 주간 리포트가 이후 분봉으로 사후 판정)으로 계측한다. 실제 청산 수량/시점은
    # 전혀 바꾸지 않는 순수 부가 기록 — 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS tp2_hold_shadow (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        ts                 TEXT NOT NULL,           -- TP2 발동(실제 전량청산) 시각
        direction          TEXT NOT NULL,           -- LONG/SHORT
        entry_price        REAL NOT NULL,
        tp2_price          REAL NOT NULL,           -- 실제 TP2 청산가 (baseline)
        tp3_price          REAL NOT NULL,           -- 당시 TP3 목표가
        stop_price_at_hook REAL NOT NULL,           -- 당시(TP1 이후) 트레일링 스톱
        atr_at_hook        REAL NOT NULL,           -- 시뮬레이션에 쓸 고정 ATR(단순화)
        grade              TEXT,
        entry_horizon      TEXT,
        resolved           INTEGER DEFAULT 0,       -- 1=counterfactual 판정 완료
        cf_outcome         TEXT,                    -- TP3 / TRAIL_STOP / FORCE_EXIT
        cf_exit_price      REAL,
        cf_hold_minutes    INTEGER,
        hyp_pnl_pts        REAL,                    -- (+)=홀드가 이득, (-)=TP2 조기청산이 나았음
        created_at         TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_t2h_ts ON tp2_hold_shadow(ts)")
    # [363차] qty=1 손실1차(Loss Tier1) 조기청산 섀도 — 0721 정기점검 딥다이브. hurst_gate_
    # shadow/open_gap_shadow와 동일한 "발동 시점 상태 기록 → 주간 리포트가 사후 판정" 패턴.
    # tp2_hold_shadow와 달리 실제 포지션이 계속 진행되므로 별도 캔들 시뮬레이션이 필요
    # 없다 — resolver가 entry_ts로 trades 테이블과 조인해 실현 pnl_pts를 그대로 대조한다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS loss_tier1_qty1_shadow (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        ts                 TEXT NOT NULL,           -- tier1 터치(기록) 시각
        entry_ts           TEXT NOT NULL,           -- trades.entry_ts 조인 키
        direction          TEXT NOT NULL,           -- LONG/SHORT
        entry_price        REAL NOT NULL,
        loss_tier1_price   REAL NOT NULL,           -- entry~stop 50% 지점 (조기청산 가정가)
        stop_price         REAL NOT NULL,           -- 당시 최종 손절가
        grade              TEXT,
        entry_horizon      TEXT,
        resolved           INTEGER DEFAULT 0,       -- 1=실거래 결과와 대조 완료
        cf_outcome         TEXT,                    -- 'EARLY_CUT' 고정(항상 tier1가에서 자름)
        cf_exit_price      REAL,                    -- = loss_tier1_price
        actual_pnl_pts     REAL,                    -- 실거래(trades.pnl_pts) 실현치
        hyp_pnl_pts        REAL,                    -- (+)=조기청산이 유리, (-)=현행(무조치) 유지가 나았음
        quantile_expected_pt    REAL,                -- [363차 후속] 진입 시점 분위 기대엣지(pt)
        quantile_uncertainty_pt REAL,                -- [363차 후속] 진입 시점 분위 불확실성(pt)
        -- ── [MW0602 425차] 두 컬럼 다 판정 품질을 지키기 위한 것이다 ──────────────
        -- live_active: LOSS_TIER1_QTY1_ENABLED가 켜진 뒤의 기록. 그때는 실제로 tier1
        --   에서 잘랐으므로 "잘랐다면"이라는 반사실이 **실제와 같아져** hyp≈0으로
        --   수렴한다. 섞으면 판정이 0 쪽으로 희석되므로 리포트가 이 행을 제외한다.
        -- from_tier1_remainder: qty=2가 tier1으로 1계약을 자른 **잔여 1계약**에서
        --   찍힌 기록. 이 채널의 모집단은 "계단화가 원천 배제된 진짜 qty=1"인데,
        --   잔여계약은 이미 한 번 보호받은 다른 모집단이다(그쪽은 [14]가 맡는다).
        --   실측으로 실제 혼입이 있었다 — 08-04 12:21(entry_qty=2)이 12:22:18 tier1
        --   체결로 qty 2→1이 된 뒤 12:22:5x 파이프라인에서 이 표에 들어왔다.
        live_active        INTEGER DEFAULT 0,
        from_tier1_remainder INTEGER DEFAULT 0,
        created_at         TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    # [363차 후속] 위 CREATE TABLE에 없던 컬럼을 나중에 추가할 때의 관례
    # (ensemble_decisions ALTER 패턴과 동일) — 이미 옛 스키마로 생성된 PC/DB에서도
    # 안전하게 따라잡는다. 신규 설치는 위 CREATE TABLE에 이미 포함돼 있어 no-op.
    with get_conn(TRADES_DB) as _lt1q1_conn:
        _lt1q1_cols = {r[1] for r in _lt1q1_conn.execute(
            "PRAGMA table_info(loss_tier1_qty1_shadow)").fetchall()}
        for _col, _dtype in (
            ("quantile_expected_pt", "REAL"),
            ("quantile_uncertainty_pt", "REAL"),
            # [MW0602 425차] 기존 DB는 DEFAULT 0으로 따라잡는다 — 과거 행은 전부
            # 전환 이전(live_active=0)이 맞고, 잔여계약 혼입 판별은 리포트가
            # trades의 '손절1차 조기축소' 레그 유무로 소급 보정한다.
            ("live_active", "INTEGER DEFAULT 0"),
            ("from_tier1_remainder", "INTEGER DEFAULT 0"),
            # [MW0601 458차 / P3] 진입 후 경과 초. 2026-08-12 조기축소 3건이 전부
            # 진입 후 **11~47초**에 발동했고 그중 2건은 잔여 레그가 곧 반등해 TP2까지
            # 갔다(#3은 30초 뒤 반등) — "진입 직후의 일시적 역행을 손절 신호로
            # 오독하는가"라는 질문이 생겼는데, 그것을 검정할 축이 테이블에 없었다.
            # ⚠ 기존 행은 NULL이다(DEFAULT 0 금지) — 0초 발동과 미측정은 다르다
            #   (계측 4원칙 ②). 리포트는 NULL 행을 이 축의 집계에서 제외해야 한다.
            ("elapsed_sec", "REAL"),
        ):
            if _col not in _lt1q1_cols:
                _lt1q1_conn.execute(
                    f"ALTER TABLE loss_tier1_qty1_shadow ADD COLUMN {_col} {_dtype}")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_lt1q1_ts ON loss_tier1_qty1_shadow(ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_lt1q1_entry_ts ON loss_tier1_qty1_shadow(entry_ts)")
    # [367차] Tier1 발동 후 잔여계약 2단계 조기청산 섀도 — loss_tier1_qty1_shadow와
    # 동일한 "발동 시점 상태 기록 → 주간 리포트가 사후 판정" 패턴. Tier1이 qty=2 중
    # 1계약만 잘라내고 남은 1계약은 원래 stop_price까지 그대로 노출되는 사각지대
    # (0722 정기점검 딥다이브, 07-22 10:26 사례)를 계측한다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS loss_tier2_remainder_shadow (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        ts                 TEXT NOT NULL,           -- tier2 터치(기록) 시각
        entry_ts           TEXT NOT NULL,           -- trades.entry_ts 조인 키(원 포지션)
        direction          TEXT NOT NULL,           -- LONG/SHORT
        entry_price        REAL NOT NULL,           -- 원 포지션 진입가
        loss_tier2_price   REAL NOT NULL,           -- tier1 체결가~stop 50% 지점(조기청산 가정가)
        stop_price         REAL NOT NULL,           -- 당시 최종 손절가 (잔여계약 기준)
        remaining_qty      INTEGER NOT NULL,        -- tier1 이후 잔여 계약수
        grade              TEXT,
        entry_horizon      TEXT,
        resolved           INTEGER DEFAULT 0,       -- 1=실거래 결과와 대조 완료
        cf_outcome         TEXT,                    -- 'EARLY_CUT' 고정(항상 tier2가에서 자름)
        cf_exit_price      REAL,                    -- = loss_tier2_price
        actual_pnl_pts     REAL,                    -- 실거래(trades.pnl_pts, 잔여계약분) 실현치
        hyp_pnl_pts        REAL,                    -- (+)=조기청산이 유리, (-)=현행(무조치) 유지가 나았음
        created_at         TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    # [MW0601 458차 / P3] tier2에도 같은 축을 단다 — tier1과 짝을 이뤄야
    # "1차는 너무 일렀나 / 2차는 늦었나"를 같은 단위로 비교할 수 있다. 기존 행 NULL.
    with get_conn(TRADES_DB) as _lt2_conn:
        _lt2_cols = {r[1] for r in _lt2_conn.execute(
            "PRAGMA table_info(loss_tier2_remainder_shadow)").fetchall()}
        if "elapsed_sec" not in _lt2_cols:
            _lt2_conn.execute(
                "ALTER TABLE loss_tier2_remainder_shadow ADD COLUMN elapsed_sec REAL")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_lt2_ts ON loss_tier2_remainder_shadow(ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_lt2_entry_ts ON loss_tier2_remainder_shadow(entry_ts)")
    # [363차 후속] qty=1 TP1 이후 트레일 폭 섀도 — 0721 정기점검 딥다이브 제안4 편입,
    # 361차 tp2_hold_shadow와 동일한 "발동 시점 상태 기록 → 주간 리포트가 사후
    # 시뮬레이션 판정" 패턴. qty=1은 TP1 이후 update_trailing_stop() 4단계 트레일링
    # 대신 static ATR-lock 1회 보호전환(arm_tp1_single_contract_with_mode)만 받는데,
    # 그게 이후 되돌림에 너무 타이트한지를 "그때부터 qty=2와 동일한 4단계 트레일링을
    # 계속 적용했다면"과 실현치를 대조해 계측한다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS tp1_trail_shadow (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        ts                   TEXT NOT NULL,      -- TP1 보호전환(실제 static lock) 발동 시각
        entry_ts             TEXT NOT NULL,      -- trades.entry_ts 조인 키
        direction            TEXT NOT NULL,      -- LONG/SHORT
        entry_price          REAL NOT NULL,
        tp1_price            REAL NOT NULL,      -- TP1 도달가(훅 시점 current_price)
        protect_stop_at_hook REAL NOT NULL,      -- 실제 적용된 static lock 손절가
        atr_at_hook          REAL NOT NULL,
        protect_mode         TEXT,               -- 'atr_profit' 등
        grade                TEXT,
        entry_horizon        TEXT,
        resolved             INTEGER DEFAULT 0,  -- 1=사후 시뮬레이션+실거래 대조 완료
        cf_outcome           TEXT,               -- TRAIL_STOP / FORCE_EXIT
        cf_exit_price        REAL,
        cf_hold_minutes      INTEGER,
        actual_pnl_pts       REAL,               -- 실거래(trades.pnl_pts) 실현치
        hyp_pnl_pts          REAL,               -- (+)=4단계 트레일링 지속이 유리, (-)=현행 정적락 유지가 나았음
        created_at           TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_t1t_ts ON tp1_trail_shadow(ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_t1t_entry_ts ON tp1_trail_shadow(entry_ts)")
    # [369차, 0723 정기점검 딥다이브] 청산 주문 체결 슬리피지 계측 — 검증캠페인
    # §17 exit_fill_slippage_watch. 0723 유일 거래(TP1 ATR보호전환 후 하드스톱(틱))
    # 실측: 주문 전송가(price_hint) 1122.49 vs 실체결가 1122.12 — 0.37pt(≈18틱)
    # 불리한 슬리피지가 확정 순이익(+0.35pt 예정)을 순손실(-0.02pt)로 뒤집음.
    # VALIDATION_CAMPAIGN 모든 채널의 왕복비용 계산이 가정하는
    # slippage_ticks_per_side=1.0(0.02pt)이 실측과 맞는지 검증할 근거 데이터가
    # 없었다 — 이 테이블이 그 실측치를 쌓는다. 모든 청산 유형(하드스톱/TP1~3/
    # 손절1차/강제청산 등)의 체결마다 기록하며, 정책에는 관여하지 않는다(§9).
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS exit_fill_slippage (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        ts            TEXT NOT NULL,      -- 체결 확인 시각
        entry_ts      TEXT,               -- trades.entry_ts 조인 키(가능한 경우)
        direction     TEXT NOT NULL,      -- LONG/SHORT (청산 대상 포지션 방향)
        reason        TEXT,               -- 청산 사유 (하드스톱(틱)/TP1/TP2(전량)/15:10 강제청산 등)
        price_hint    REAL NOT NULL,      -- 주문 전송 시점 의도가(손절가/목표가)
        fill_price    REAL NOT NULL,      -- 실제 체결가
        slippage_pts  REAL NOT NULL,      -- 방향보정 후 (+)=불리, (-)=유리 (pt)
        hint_source   TEXT,               -- [423차] 'normal' | 'phantom' (아래 참조)
        created_at    TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_efs_ts ON exit_fill_slippage(ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_efs_entry_ts ON exit_fill_slippage(entry_ts)")
    # [MW0602 423차] hint_source 멱등 ALTER — 420차 joint_gate_shadow와 같은 이유.
    # 왜 필요한가: 이 채널(§17)은 왕복비용 가정(slippage_ticks_per_side=1.0 ≈ 0.02pt)을
    # 실측으로 검증하려고 만들었는데, "유령 하드스톱" 건의 price_hint는 **실제로 닿은
    # 적 없는 스톱가**라 fill과의 차이가 집행 슬리피지가 아니다.
    # 2026-08-03 실측: 비틱 `하드스톱` 8건 평균 -1.371pt vs 틱 13건 평균 +0.085pt.
    # 전자를 그대로 쓰면 왕복비용을 60배 이상 과대추정한다 — 섞어 놓으면 채널이
    # 재려던 값을 못 잰다. 그래서 분리 태깅만 하고 기존 행/판정은 건드리지 않는다.
    try:
        _efs_have = {r[1] for r in fetchall(
            TRADES_DB, "PRAGMA table_info(exit_fill_slippage)")}
        if "hint_source" not in _efs_have:
            execute(TRADES_DB,
                    "ALTER TABLE exit_fill_slippage ADD COLUMN hint_source TEXT")
    except Exception as _efs_mig_e:
        print("[DB][WARN] exit_fill_slippage 컬럼 마이그레이션 실패: %s" % _efs_mig_e,
              file=sys.stderr)
    # ── [MW0602 424차 신설] 유령 하드스톱 섀도 — 계측 전용, 청산 동작 무관여 ──────
    # 무엇을 재는가: 봉중(intrabar) 하드스톱 판정이 날 때마다 한 행을 남기고,
    # "조이기 경로를 **전부** 덮은 가드였다면 이 판정을 억제했을까"를 함께 기록한다.
    #
    # 왜 억제하지 않고 재기만 하는가 — 손익 부호가 예상과 반대이기 때문이다.
    #   08-03  비틱 하드스톱  8건  +1.42pt (423차 실측, 5건 유리/3건 불리)
    #   08-04  qty>=2 유령    3건  +8.76pt (+433,609원 = 당일 순익 +752,561원의 57.6%)
    #   반사실(정상 가드 시 손익분기 스톱 유지)은 3건 모두 **0pt** — 되돌림 뒤
    #   12:00·12:24·12:34에 BE스톱이 재히트된다.
    # 유령 판정은 "봉 고가가 스톱을 스쳤으나 현재가는 유리하게 되돌아왔다"에서만
    # 터져 시장가가 스톱보다 좋은 국면만 고른다. 결함(정확성)인 동시에 미발견
    # 청산 알파일 수 있다 — 2거래일 11건으로 확정하는 것은 313차 위반이다.
    #
    # 판정 후: 유리 확정이면 "스파이크가 스톱을 스쳤으나 현재가가 유리하면 시장가
    # 익절"을 **명시적 청산 정책**으로 승격시킬 것. 불리 확정이면 그때 가드를
    # qty>=2까지 켠다(main.py `mark_stop_tightened_shadow` → `_mark_stop_tightened`).
    # 캠페인 채널 등록(`phantom_stop_edge`)은 4-2 후속 — min_samples=20/min_days=5.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS phantom_stop_shadow (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        ts               TEXT NOT NULL,   -- 판정 시각
        entry_ts         TEXT,            -- trades.entry_ts 조인 키
        direction        TEXT NOT NULL,   -- LONG/SHORT
        quantity         INTEGER,         -- 판정 시점 잔여 계약수 (qty>=2 경로 식별용)
        entry_price      REAL,
        stop_eval        REAL,            -- 봉중 판정에 실제로 쓰인 스톱(_prev_stop_price)
        stop_current     REAL,            -- 판정 시점 최신 스톱
        bar_start        TEXT,            -- 평가 대상 분봉 시작시각
        bar_high         REAL,
        bar_low          REAL,
        cur_price        REAL,            -- 판정 시점 현재가 (스톱보다 유리하면 유령 징후)
        close_hit        INTEGER,         -- 1=종가 기준으로도 히트 (유령 아님)
        live_suppressed  INTEGER,         -- 1=423차 라이브 가드가 실제로 억제함
        would_suppress   INTEGER,         -- 1=전 경로 계측 가드였다면 억제했을 것
        tighten_path     TEXT,            -- entry/trailing/arm_tp1_qty1*/tp1_breakeven_qty2
        stop_updated_at  TEXT,            -- 라이브 가드가 본 조이기 시각
        shadow_tightened_at TEXT,         -- 섀도가 본 조이기 시각 (전 경로)
        exited           INTEGER,         -- 1=이 판정이 청산으로 이어짐(주문 전송 시도)
        created_at       TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_pss_ts ON phantom_stop_shadow(ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_pss_entry_ts ON phantom_stop_shadow(entry_ts)")

    # [379차 신설] RegimeExhaustionGate(§18) counterfactual 섀도우 — hurst_gate_shadow·
    # open_gap_shadow와 동일 패턴. "hurst<0.45(평균회귀) + 60분 느린 연장폭 임계 초과 +
    # 10_chase/11_countertrend 소프트 실패" 동시성립 시점의 가상 진입가·스톱·TP1을
    # 기록해 사후 판정(resolve_and_eval_regime_exhaustion())한다. 0723 정기점검
    # 딥다이브 3항(진입 직후 반전 패턴) 후속 제안 — 리포트 전용 계측 테이블,
    # 실거래 의사결정에 관여하지 않는다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS regime_exhaustion_shadow (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        ts                TEXT NOT NULL,           -- 발동 시각 (분봉)
        direction         TEXT NOT NULL,           -- LONG/SHORT (가상 방향, 연장 방향과 동일=추격)
        grade             TEXT,                    -- 발동 당시 진입 등급 (A/B/C)
        hurst             REAL,                    -- 발동 당시 Hurst 값
        ext_atr_60m       REAL,                    -- 발동 당시 60분 느린 연장폭 (signed, ATR 배수)
        chase_failed      INTEGER,                 -- 10_chase 소프트 실패 여부 (0/1)
        countertrend_failed INTEGER,                -- 11_countertrend 소프트 실패 여부 (0/1)
        conf              REAL,                    -- 발동 당시 confidence
        entry_price       REAL NOT NULL,           -- 가상 진입가 (분봉 종가)
        stop_price        REAL,                    -- 가상 하드스톱
        tp1_price         REAL,                    -- 가상 TP1
        resolved          INTEGER DEFAULT 0,       -- 1=counterfactual 판정 완료
        cf_outcome        TEXT,                    -- STOP / TP1 / NEITHER
        cf_exit_price     REAL,                    -- counterfactual 청산가
        hyp_pnl_pts       REAL,                    -- (+)=신호 방향이 맞았음, (-)=탈진 반전 가설 지지(스톱)
        created_at        TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_res_ts ON regime_exhaustion_shadow(ts)")
    # [384차 신설] 검증캠페인 [1] Triple-Barrier 채널 판정 이력 — 383차가 규명한
    # "평가창이 매주 재학습으로 리셋돼 5m~30m이 min_samples_hz(800) 영구 미달"
    # 구조결함의 해법(제안 (a): 재학습 주기와 평가창 분리). 호라이즌별로 실제
    # OOS n이 800에 도달한 주에만 판정을 내려 여기 기록하고, 그 아래 주는 이
    # 로그의 "최근 판정"을 그대로 유지(carry-forward)해 채널 집계에 반영한다.
    # 재학습 실행부(batch_retrainer.retrain_shadow_triple_barrier)도 이 로그에서
    # "오늘 판정된 호라이즌"만 골라 재학습하고 나머지는 모델 파일을 건드리지 않아
    # OOS 누적이 끊기지 않게 한다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS tb_verdict_log (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        horizon       TEXT NOT NULL,           -- 1m/3m/5m/10m/15m/30m
        judged_at     TEXT NOT NULL,           -- 판정(리포트 생성) 시각
        eval_start    TEXT,                    -- 이번 판정 OOS 구간 시작 (= 판정 당시 모델 mtime)
        model_mtime   TEXT,                    -- 판정에 쓰인 모델 파일 mtime
        n_samples     INTEGER,                 -- 판정 시점 OOS 표본 수 (>= min_samples_hz)
        ic_tb         REAL,
        ic_3class     REAL,
        verdict       TEXT NOT NULL,           -- PASS / FAIL
        created_at    TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_tvl_horizon_judged "
            "ON tb_verdict_log(horizon, judged_at)")

    # [404차, P0-4 후속] EOD 모델가드 GuardShadow 영속화 — old_acc(acc.txt, 판정에
    # 실제 쓰는 값)와 old_acc_live(동일폴드 재측정값)가 서로 다른 시점 데이터로 채점된
    # 값이라 acc.txt vs new(cv) 비교는 불공정하다(learning/batch_retrainer.py
    # _measure_incumbent_acc 주석 참조). old_acc_live vs new(cv)만 동일폴드라 공정
    # 비교 자격이 있다. 07-31 최초 라이브 관측에서 이 로그 한 줄로만 존재하던 값이라
    # 사후 추적이 불가능했음 — DB 영속화로 generate_validation_campaign_report.py가
    # "acc.txt 기준 실제 판정이 공정비교와 얼마나 자주 어긋나는지" 누적 판정할 수 있게 한다.
    execute(TRADES_DB, """
    CREATE TABLE IF NOT EXISTS guard_shadow_log (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ts              TEXT NOT NULL,           -- 재학습 실행 시각
        horizon         TEXT NOT NULL,           -- 1m/3m/5m/10m/15m/30m
        source          TEXT NOT NULL DEFAULT 'eod',  -- eod/intraday — 404차 후속
        acc_txt         REAL NOT NULL,           -- 판정에 실제 사용된 old_acc(acc.txt)
        old_acc_live    REAL,                    -- 동일폴드 재측정값 (측정 불가 시 NULL)
        new_cv          REAL NOT NULL,           -- 이번 재학습 3폴드 평균 CV 정확도
        live_note       TEXT,                    -- "ok" 또는 재측정 실패 사유
        distortion      REAL,                    -- acc_txt - old_acc_live (NULL 가능)
        actual_verdict  TEXT NOT NULL,           -- REPLACE/HOLD — 실제 적용된 결정
        fair_verdict    TEXT,                    -- REPLACE/HOLD — old_acc_live 기준 공정 판정 (NULL 가능)
        n_samples       INTEGER,                 -- 이번 재학습 학습표본 수(len(X))
        pc              TEXT,                    -- MW0601/MW0602 — 405차, PC별 분리 판정용
        -- [405차 P1-1] 공정 홀드아웃 섀도: 최신 fair_hold_bars행을 학습에서 완전히
        -- 제외한 도전자 vs 현행 pkl을 같은 구간으로 채점한 값. 판정 무영향.
        fair_new        REAL,
        fair_old        REAL,
        fair_hold_bars  INTEGER,
        fair_note       TEXT,
        -- [MW0602 457차] 위 fair_* 비교가 **성립하는 행인가**. 405차 docstring이
        -- 스스로 밝힌 한계 — "현행 pkl은 intraday 재학습이 매일 덮어쓰므로 홀드아웃
        -- 구간을 이미 학습했을 수 있다" — 를 사이드카 메타(gbm_{h}_meta.json)의
        -- train_end_ts로 직접 판정한다. 0이면 격차가 성능차가 아니라 in-sample
        -- 프리미엄이라 **판정에 쓰면 안 된다**. 457차 이전 42행은 전부 NULL이며
        -- 그 구간 실측이 36행 중 35행 도전자 열위(평균 -0.1161)였다.
        fair_valid      INTEGER,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    # [404차 후속] source 컬럼 — 기존 설치(위 CREATE TABLE 이전 스키마)에서도 안전하게
    # 따라잡는다(loss_tier1_qty1_shadow와 동일 관례). 신규 설치는 위에 이미 포함돼 no-op.
    #
    # [MW0601 405차 / P0-5] pc 컬럼 — [23] missed_upgrade_rate가 두 PC에서 정반대로
    # 나온다(MW0601 0% : 6개 호라이즌 전부 공정비교로도 HOLD / MW0602 50% : 3개는
    # 신모델 우세). 합산하면 상반된 신호가 상쇄돼 무의미한 값이 되므로 PC별로 나눠
    # 판정해야 한다. [23-B] tp1_x2(+32.78 vs -19.04)에 이은 두 번째 PC간 부호 역전이며
    # 313차 원칙상 두 PC를 한 표본으로 합칠 수 없다.
    # 근거: docs/정기점검/금요일점검/0801_MW0601xMW0602_교차검토_및_미결개선계획.md §2-4.
    with get_conn(TRADES_DB) as _gsl_conn:
        _gsl_cols = {r[1] for r in _gsl_conn.execute(
            "PRAGMA table_info(guard_shadow_log)").fetchall()}
        if "source" not in _gsl_cols:
            _gsl_conn.execute(
                "ALTER TABLE guard_shadow_log ADD COLUMN source TEXT NOT NULL DEFAULT 'eod'")
        if "pc" not in _gsl_cols:
            _gsl_conn.execute("ALTER TABLE guard_shadow_log ADD COLUMN pc TEXT")
        # [456차 / F6] fair_contaminated_bars: 홀드아웃 중 현행 모델이 이미 학습한 봉 수.
        #   0  = 깨끗 (판정 유효)  /  >0 = 오염 봉수  /  -1 = 미상(=오염 취급)
        # incumbent_source/cutoff_ts: 배포 pkl이 eod인지 intraday인지, 학습 마지막 봉 ts.
        # [456차 Wave 4 / G2-B] 청산 레그 수량 — 417차 "계약수 x 슬리피지" 가설용.
        # 종전엔 trades 조인으로만 얻었고 그 조인은 exit_ts ±3초 매칭이라 깨지기 쉽다.
        _efs_cols = {r[1] for r in _gsl_conn.execute(
            "PRAGMA table_info(exit_fill_slippage)").fetchall()}
        if _efs_cols and "quantity" not in _efs_cols:
            _gsl_conn.execute("ALTER TABLE exit_fill_slippage ADD COLUMN quantity INTEGER")
        # [MW0601 458차 / P1-A] clean_*: 홀드아웃 중 **현행 cutoff 이후** 구간(=현행도
        #   도전자도 학습하지 않은 봉)만의 매치드 대조. 456차 전환조건 ①("오염 0봉
        #   5거래일 연속")이 원리적 달성 불가임이 458차에 확인돼(장중 재학습이 매일
        #   cutoff를 밀어올려 홀드아웃 91%가 항상 오염), 오염일에도 살아남는 유일한
        #   공정 표본이다. 하루치는 얇으므로(실측 159봉) **롤링 누적으로만** 판정한다.
        # [MW0601 458차 / P1-B] live_*: 그날 배포본이 실제 라이브에서 낸 성적
        #   (predictions.db 당일 채점). EOD 가드가 지키는 구간은 다음날 08:55~09:37의
        #   42분뿐이고 나머지는 무가드 장중 모델이므로, 몸통을 보는 관측치다.
        for _c, _t in (("fair_new", "REAL"), ("fair_old", "REAL"),
                       ("fair_hold_bars", "INTEGER"), ("fair_note", "TEXT"),
                       ("fair_contaminated_bars", "INTEGER"),
                       ("incumbent_source", "TEXT"),
                       ("incumbent_cutoff_ts", "TEXT"),
                       ("verdict_source", "TEXT"),
                       ("clean_new", "REAL"), ("clean_old", "REAL"),
                       ("clean_n", "INTEGER"), ("clean_note", "TEXT"),
                       ("live_acc", "REAL"), ("live_n", "INTEGER"),
                       ("fair_valid", "INTEGER")):   # [MW0602 457차]
            if _c not in _gsl_cols:
                _gsl_conn.execute(
                    "ALTER TABLE guard_shadow_log ADD COLUMN %s %s" % (_c, _t))
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_gsl_horizon_ts ON guard_shadow_log(horizon, ts)")
    execute(TRADES_DB,
            "CREATE INDEX IF NOT EXISTS idx_gsl_source_ts ON guard_shadow_log(source, ts)")

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
                # [311차 후속] 진입 출처 태그 — SYSTEM_AUTO/OPERATOR_MANUAL/
                # BROKER_SYNC_RECOVERY/OPERATOR_RESTORE/GHOST_PENDING_MISS.
                # 기존 grade='MANUAL'이 유령 pending_miss 체결과 정상 수동매매를
                # 구분 못 해 실전 전환 기준① 등 성과 집계가 오염된 문제(306차 유령
                # 포지션 사후분석) 대응. NULL=구버전 레코드(출처 미상).
                "entry_source":       "TEXT",
                # [342차] 켈리가 "자본 대비 1계약도 부적절"이라 판단했는데
                # min_qty로 강제 진입된 경우 1. 실거래 의사결정에는 미관여 —
                # VALIDATION_CAMPAIGN["kelly_skip"] 주간 리포트 전용 계측
                # (signal_decay와 동일한 shadow-first 패턴). NULL=구버전 레코드.
                "kelly_advised_skip": "INTEGER DEFAULT 0",
                # [401차, 372차 제안 반영] 체크리스트 등급(grade, pass_count 기준)과
                # 별개로 진입 시점 원시 확신도 등급(EnsembleDecision.compute()의
                # confidence 임계 기준)을 함께 저장 — "체크리스트 A / 확신도 C" 같은
                # 괴리(0721·372차 지목, 366차 grade_ev_inversion 캠페인의 A등급
                # 순EV 역전과도 연결되는 후보 원인)를 사후분석에서 구분할 수 있게
                # 한다. 진입 판정에는 영향 없는 순수 관측 컬럼. NULL=구버전 레코드.
                "raw_grade": "TEXT",
                # [456차 Wave 4 / F10-B] 진입 시점 체크리스트 통과 항목 수.
                # 승격 경로([36])는 raw_grade->grade로 이미 재지만 "C->A 승격에
                # 정렬강도 하한이 필요한가"는 pass_count 없이는 답할 수 없다.
                # 진입 판정 무관 순수 관측. NULL=구버전 레코드.
                "checklist_pass_count": "INTEGER",
                # [MW0601 417차 / ②] 진입 시점 계약수.
                #
                # **왜 필요한가.** `quantity`는 **청산 행별 계약수**다 — 부분청산
                # 포지션은 같은 entry_ts로 여러 행에 나뉘고 각 행에 그 레그 수량이
                # 들어간다. 그래서 `quantity`만으로는 "이 포지션이 몇 계약으로
                # 들어갔나"를 알 수 없고, 분석하는 쪽이 매번 entry_ts로 묶어
                # 합산해야 한다. 그 합산을 빠뜨리면 편향이 **한 방향으로만** 생긴다:
                # 이익 포지션은 TP1/TP2/TP3로 쪼개져 작은 수량 여러 행이 되고,
                # 손실 포지션은 하드스톱 전량청산이라 큰 수량 한 행이 된다
                # → "계약수가 클수록 진다"가 인과 없이 만들어진다.
                #
                # 실제로 같은 사고가 네 번 반복됐다:
                #   311차 후속(07-12) 인지만 등록 → 402차 후속5(07-29) 진입 27건이
                #   87행으로 승률 65.5% 과대 → 405차(08-01) 병합 헬퍼 도입하며
                #   수량은 max 채택 → 409차(08-02) max 반증·[13]만 sum 수정.
                # 분석 측 관례로는 재발을 못 막으므로 기록 측에 값을 남긴다.
                #
                # 값의 출처는 `PositionTracker.initial_quantity`(진입 시 확정,
                # 추가진입 시 갱신, 360차 shrink_initial 시 축소). NULL=구버전 레코드
                # 이며 소비 측은 entry_ts 레그 합으로 폴백해야 한다.
                "entry_qty": "INTEGER",
            }
            for name, dtype in additions.items():
                if name not in cols:
                    conn.execute(f"ALTER TABLE trades ADD COLUMN {name} {dtype}")

            # [MW0601 417차 / ②] entry_qty 백필 — 구버전 레코드는 같은
            # (entry_ts, direction) 레그들의 quantity **단순 합**이 곧 진입 계약수다.
            # 부분청산이 진입 수량을 남김없이 분할하므로 합이 정확히 원 수량이 된다.
            # 이미 값이 있는 행은 건드리지 않는다(재실행 안전).
            #
            # **중복 제거를 하지 않는 이유 — 실측으로 반증됐다.** 처음에는
            # `stuck_exit_flat`/`stuck_exit_remainder`가 같은 청산을 두 번 기록한
            # 것으로 의심해 (exit_ts, quantity, net_pnl_krw) 중복을 접으려 했으나,
            # TRADE 로그의 `[Position] 진입 N계약`과 대조하니 단순 합이 맞았다:
            #   2026-06-26 11:01:58 로그 6계약 = 2+2+1+1 (중복제거하면 5 — 틀림)
            #   2026-07-01 13:00:01 로그 6계약 = 5+1
            #   2026-07-03 13:20:01 로그 8계약 = 1×8 (중복제거하면 7 — 틀림)
            # flat/remainder는 진짜 별개 레그이고, 1계약씩 같은 가격에 나가면
            # quantity·net_pnl_krw가 우연히 같아질 뿐이다. 07-03의 8분할처럼
            # **정상 레그가 동일값을 갖는 경우가 실재**하므로 값 기반 중복 제거는
            # 안전하지 않다.
            if "entry_qty" not in cols:
                conn.execute(
                    """UPDATE trades SET entry_qty = (
                           SELECT SUM(t2.quantity) FROM trades t2
                           WHERE t2.entry_ts = trades.entry_ts
                             AND t2.direction = trades.direction
                       )
                       WHERE entry_qty IS NULL AND entry_ts IS NOT NULL"""
                )

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
    # [331차 후속2] 1m 활용방안 C(신규 알파 카나리아 호라이즌) — DYNAMIC_FEATURES_POOL
    # 후보 피처들의 IC를 1m 레이블 기준으로 주기 계산해 누적한다. 진짜 알파가 있다면
    # 다중 호라이즌 감쇠 곡선상 가장 먼저(가장 강하게) 1m에서 신호가 보일 것이므로,
    # 신규 피처 후보의 "테스트 우선순위"를 정하는 진단 자료 — 게이트·학습 어디에도
    # 이 결과를 소비하는 코드 없음(scripts/compute_canary_1m_ic.py가 주기 실행해 적재).
    execute(SHAP_DB, """
    CREATE TABLE IF NOT EXISTS canary_1m_ic_scores (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date    TEXT NOT NULL,      -- 계산 실행일 (YYYY-MM-DD)
        feature     TEXT NOT NULL,      -- DYNAMIC_FEATURES_POOL 후보 피처명
        ic          REAL,               -- Spearman IC (1m 전방수익률 기준)
        p_value     REAL,
        n_samples   INTEGER,
        coverage    REAL,               -- 표본 내 non-null 비율
        created_at  TEXT DEFAULT (datetime('now', 'localtime'))
    )
    """)
    execute(SHAP_DB,
            "CREATE INDEX IF NOT EXISTS idx_canary_feature ON canary_1m_ic_scores(feature)")
    execute(SHAP_DB,
            "CREATE INDEX IF NOT EXISTS idx_canary_run_date ON canary_1m_ic_scores(run_date)")


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
            -- ── [MW0601 452차 / QDQ Phase 0] 앵커 계측 4열 (소비 0, 적재 전용) ──
            -- 🔴 DEFAULT를 두지 않는다. 미계측은 반드시 NULL이어야 한다 —
            --    "0이었다"와 "못 받았다"가 같아 보이면 감시가 무의미해진다
            --    (451차 program_* 유령 피처가 정확히 그 방식으로 2개월간 숨었다).
            anchor_buy    INTEGER,   -- 서버 23_누적체결매수 봉내 증분 (정답지)
            anchor_sell   INTEGER,   -- 서버 22_누적체결매도 봉내 증분 (정답지)
            buy_vol_flag  INTEGER,   -- 24_체결구분 올바른 파싱 기준 매수량 (섀도)
            sell_vol_flag INTEGER,   -- 〃 매도량 (섀도)
            -- [MW0601 452차 / QDQ Phase 1] 봉의 내력. NULL=452차 이전 / 0=정상 실시간
            -- 경로 / 1=파이프라인 복구 재처리본(bid_qty·hoga 등 미복원 열화 상태).
            -- 측정값이 아니라 **기록자가 항상 아는 플래그**라 0을 쓰는 것이 위 NULL
            -- 원칙과 충돌하지 않는다.
            bar_recovered INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    # Phase 2 마이그레이션: 기존 DB에 buy_vol/sell_vol 컬럼 추가 (없으면 추가, 있으면 무시)
    # [452차] 앵커 4열도 같은 방식으로 추가 — 기존 88,558행은 NULL이 된다(정상).
    for _col, _type in [("buy_vol", "INTEGER DEFAULT 0"), ("sell_vol", "INTEGER DEFAULT 0"),
                        ("anchor_buy", "INTEGER"), ("anchor_sell", "INTEGER"),
                        ("buy_vol_flag", "INTEGER"), ("sell_vol_flag", "INTEGER"),
                        ("bar_recovered", "INTEGER")]:
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
    # [MW0601 451차 Phase 1-1] 프로그램매매 원천 보존 — `Dscbo1.CpSvr8111` 56필드 전량.
    #
    # 왜 별도 테이블인가:
    #   `raw_features`는 **피처** 테이블이다. 원천 TR 응답을 거기 섞으면 스케일러·모델·
    #   피처 건강도 리포트가 전부 영향을 받는다. 원천은 원천끼리 둔다.
    #
    # 왜 지금 만드는가 (451차가 실증한 대가):
    #   8111은 56필드를 주는데 우리는 `idx19`·`idx37` 2개만 뽑아 쓰고 나머지 54개를
    #   버려 왔다. 그런데 `_probe_investor_tr`는 **이미 매 호출 `GetHeaderValue(0..63)`을
    #   전부 읽고 있다** — 못 받은 게 아니라 저장하지 않았을 뿐이다. 그 결과 지금
    #   gross·위탁/자기 파생을 만들려 해도 **과거 데이터가 없어** 검증을 처음부터
    #   시작해야 한다. 원시를 보존하면 파생은 언제든 오프라인에서 만들 수 있고 과거
    #   구간에 소급도 되지만, 반대는 불가능하다.
    #
    # 왜 JSON인가:
    #   `raw_features.features`와 같은 관례다. 56개를 컬럼으로 펼치면 TR 필드가 바뀔 때
    #   또 스키마 마이그레이션이 필요하고, 그때 담지 못한 필드는 또 영영 사라진다.
    #
    # 용량: 약 370행/일 × 250일 × ~600B ≈ 55MB/년.
    # 필드 의미: `docs/CyBos ref/CYBOS_프로그램매매_투자자별_TR_명세.md` §1-1.
    #   ⚠ `idx17`(차익순매수 위탁금액)은 서버측 결함으로 `idx19`를 중복 반환한다(7일 실측).
    #     쓰려면 `idx19 − idx18` 또는 `idx11 − idx5`로 우회할 것.
    #   ⚠ `idx1`(시간)은 실측상 항상 0이다 — 시계열 용도로 쓰지 말 것. 시각은 `ts` 컬럼이다.
    #   ⚠ 값은 **일중 누계**다(09:02 → 15:34 사이 부호까지 바뀐다). 흐름이 필요하면 차분할 것.
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS raw_program_trade (
            ts         TEXT NOT NULL,
            market     TEXT NOT NULL,
            fields     TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            PRIMARY KEY (ts, market)
        )
    """)

    # v9 처방 P1 (mireuki_v9_최종설계안_2026-07-03.md §2-2): 트리플 배리어 라벨 저장.
    # 기존 학습 라벨(_path_conditioned_label)과 병렬 비교/검증용 — scripts/build_triple_barrier_labels.py
    execute(RAW_DATA_DB, """
        CREATE TABLE IF NOT EXISTS triple_barrier_labels (
            ts            TEXT NOT NULL,
            horizon       TEXT NOT NULL,
            label         INTEGER NOT NULL,
            touch_type    TEXT NOT NULL,
            touch_minute  INTEGER NOT NULL,
            realized_ret  REAL NOT NULL,
            atr_at_t      REAL NOT NULL,
            stop_mult     REAL NOT NULL,
            profit_mult   REAL NOT NULL,
            created_at    TEXT DEFAULT (datetime('now', 'localtime')),
            PRIMARY KEY (ts, horizon)
        )
    """)


def save_triple_barrier_labels(horizon: str, labels: list, stop_mult: float, profit_mult: float) -> None:
    """트리플 배리어 라벨 일괄 저장 (scripts/build_triple_barrier_labels.py 전용)."""
    if not labels:
        return
    rows = [
        (
            lbl["ts"], horizon, int(lbl["label"]), lbl["touch_type"],
            int(lbl["touch_minute"]), float(lbl["realized_ret"]), float(lbl["atr_at_t"]),
            float(stop_mult), float(profit_mult),
        )
        for lbl in labels
    ]
    with _lock:
        with get_conn(RAW_DATA_DB) as conn:
            conn.executemany(
                """INSERT OR REPLACE INTO triple_barrier_labels
                   (ts, horizon, label, touch_type, touch_minute, realized_ret,
                    atr_at_t, stop_mult, profit_mult)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows,
            )


def save_candle(candle: dict) -> None:
    """분봉 확정 시 raw_candles에 저장."""
    ts_raw = candle.get("ts")
    ts = ts_raw.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts_raw, "strftime") else str(ts_raw)
    execute(
        RAW_DATA_DB,
        """INSERT OR REPLACE INTO raw_candles
           (ts, open, high, low, close, volume, bid1, ask1, oi, buy_vol, sell_vol,
            anchor_buy, anchor_sell, buy_vol_flag, sell_vol_flag, bar_recovered)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
            # [452차 Phase 1] 기본값 0 제거 — 키가 없으면 NULL이 맞다.
            # 종전 `.get("buy_vol", 0)`은 복구 경로가 키를 빠뜨렸을 때
            # "매수 0계약이었다"는 **거짓말**을 DB에 남겼다(실측 55봉).
            candle.get("buy_vol"),
            candle.get("sell_vol"),
            # [452차 Phase 0] 기본값 없이 읽는다 — 키가 없으면 None → NULL.
            # `.get(key, 0)`을 쓰면 미계측이 "매수 0건"으로 위장된다.
            candle.get("anchor_buy"),
            candle.get("anchor_sell"),
            candle.get("buy_vol_flag"),
            candle.get("sell_vol_flag"),
            # [452차 Phase 1] 내력 플래그 — 기록자가 항상 아는 값이라 0/1로 확정한다.
            1 if candle.get("bar_recovered") else 0,
        ),
    )


def save_features(ts: str, features: dict) -> None:
    """피처 벡터를 raw_features에 저장."""
    execute(
        RAW_DATA_DB,
        "INSERT OR REPLACE INTO raw_features (ts, features) VALUES (?, ?)",
        (ts, json.dumps(features, ensure_ascii=False)),
    )


def save_program_trade_raw(ts: str, market: str, fields: Dict[str, int]) -> bool:
    """[451차 Phase 1-1] `CpSvr8111` 원천 필드를 `raw_program_trade`에 보존.

    ts     — 'YYYY-MM-DD HH:MM:SS' (분 단위로 내림한 값. 호출부 책임)
    market — '1'=거래소, '2'=코스닥
    fields — {"0": 20260807, "1": 0, ..., "55": 109980}  (문자열 키, 정수 값)

    반환: 저장했으면 True, 입력이 비어 건너뛰었으면 False.

    🔴 **빈 dict는 저장하지 않는다.** 451차의 유령 피처는 "원천이 안 준 것을 0으로 채워
    저장한" 사고였다. 여기서 빈 응답을 빈 JSON으로 남기면 나중에 읽는 사람이 "그 시각엔
    프로그램매매가 0이었다"로 오독한다 — **행이 없는 것과 0인 것은 다르다.**
    """
    if not fields:
        return False
    execute(
        RAW_DATA_DB,
        "INSERT OR REPLACE INTO raw_program_trade (ts, market, fields) VALUES (?, ?, ?)",
        (ts, str(market), json.dumps(fields, ensure_ascii=False, sort_keys=True)),
    )
    return True


def save_candle_and_features(candle: dict, ts: str, features: dict) -> None:
    """분봉 + 피처를 1연결 트랜잭션으로 저장 (save_candle+save_features 2회 연결 → 1회)."""
    ts_raw = candle.get("ts")
    candle_ts = ts_raw.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts_raw, "strftime") else str(ts_raw)
    feat_json = json.dumps(features, ensure_ascii=False)
    with _lock:
        with get_conn(RAW_DATA_DB) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO raw_candles
                   (ts, open, high, low, close, volume, bid1, ask1, oi, buy_vol, sell_vol,
                    anchor_buy, anchor_sell, buy_vol_flag, sell_vol_flag, bar_recovered)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                    # [452차] 기본값 없이 읽는다 (save_candle과 동일 규약)
                    candle.get("buy_vol"),
                    candle.get("sell_vol"),
                    candle.get("anchor_buy"),
                    candle.get("anchor_sell"),
                    candle.get("buy_vol_flag"),
                    candle.get("sell_vol_flag"),
                    1 if candle.get("bar_recovered") else 0,
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


def fetch_ev_by_grade(days_back: int = 30, system_only: bool = False) -> List[sqlite3.Row]:
    """등급별 순EV(수수료 차감 후 실집행 기준) — grade, cnt, win_rate, avg_net_pnl_krw, total_net_pnl_krw.
    [260704 감사 P0] "방향 적중률" 대신 "거래당 순기대값"을 보는 관점 — fetch_grade_stats()(pnl_pts 방향)와 병행 참고.

    Args:
        system_only: True면 `entry_source='SYSTEM_AUTO'` 행만 집계한다.

    [MW0602 423차] `system_only`를 신설한 이유 — **등급의 신호 품질을 판정하려면
    시스템이 스스로 낸 진입만 봐야 한다.** 기본값은 False라 기존 호출부
    (`daily_exporter`의 손익 리포트)는 무변경이다. 손익 리포트는 "실제로 얼마
    벌었나"를 보여야 하므로 수동·구경로 진입을 빼면 오히려 틀린다.

    2026-08-03 실측 — 왜 이 구분이 결론을 뒤집는가:
        A급 30일 전체     n=64  합계 -485,306원  평균  -7,583원  ← 가드가 보던 값
          └ entry_source NULL  n= 6  합계 -1,069,701원 (07-09~10, qty=2 시절)
          └ SYSTEM_AUTO        n=58  합계  +584,395원  평균 +10,076원
    `entry_source` 컬럼이 채워지기 전 구간의 6건이 부호를 통째로 뒤집고 있었다.
    같은 기간 pt 단위로는 A(+0.358)와 C(+0.239)가 통계적으로 구분되지 않는다
    (Mann-Whitney p=0.80) — 원 단위 차이는 계약수 효과였다(417차 교훈과 동형).

    ⚠ 이 필터는 `VALIDATION_CAMPAIGN_DECISIONS["grade_ev_inversion"]`의
      "부결 — GradeEVGuard 활성화하지 않음"(2026-08-01) 결정을 **뒤집지 않는다**.
      그 결정의 근거(급행 풀스톱 11건 오조준)와 **서로소인 두 번째 근거**를 더할
      뿐이다. 가드는 여전히 섀도(GRADE_EV_GUARD_ENABLED=False)로 남는다.
    """
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days_back)).isoformat()
    _src_clause = " AND entry_source = 'SYSTEM_AUTO'" if system_only else ""
    return fetchall(
        TRADES_DB,
        """SELECT COALESCE(NULLIF(grade, ''), '?') AS grade,
                  COUNT(*) AS cnt,
                  ROUND(AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
                  ROUND(AVG(COALESCE(net_pnl_krw, pnl_krw)), 0) AS avg_net_pnl_krw,
                  ROUND(SUM(COALESCE(net_pnl_krw, pnl_krw)), 0) AS total_net_pnl_krw
           FROM trades
           WHERE exit_ts IS NOT NULL AND exit_ts >= ?""" + _src_clause + """
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
                 AND COALESCE(entry_source, '') != 'GHOST_PENDING_MISS'
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
# [305차] JointGateBlock/Hurst미계산/증거금부족은 체크리스트(final_ok) 통과 *이후*
# 2차 실행단계에서 걸리는 차단이라 "Hurst" 등 일반 needle보다 먼저 와야 오분류 방지.
_BLOCK_REASON_CATEGORIES = [
    ("JointGateBlock",  "JointGateBlock"),
    ("Hurst 미계산",      "Hurst미계산(워밍업)"),
    ("증거금 부족",        "증거금부족"),
    # [402차] 아래 5종 신설 — 401차까지 등급X 사유가 전부 `_qty_display <= 0` 분기에
    # 가로채여 "사이저 산출 수량 0"으로 저장됐는데, 그 문구는 이 표에 항목이 없어
    # "기타(사이저 산출 수량 0 — 리스크…)"로 빠졌다(2026-07-29 실측 50건, 그중 23건은
    # 실제 ToxicityGate block). 위 305차 주석과 같은 이유로 일반 needle보다 먼저 둔다 —
    # 게이트 강등 문구에 "Degraded"·"IntradayRegime" 등이 포함될 수 있어서다.
    ("게이트 강등 X — ToxicityGate",      "게이트강등(Toxicity)"),
    ("게이트 강등 X — MetaGate",          "게이트강등(Meta)"),
    ("게이트 강등 X — ExecutionGovernor", "게이트강등(Exec)"),
    ("게이트 강등 X",                     "게이트강등(기타)"),
    ("사이저 산출 수량 0",                 "사이저수량0"),
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
    # [402차] 기존 needle "15:00 이후"는 NEW_ENTRY_CUTOFF가 14:50으로 바뀐 뒤 한 건도
    # 매칭되지 않아 통째로 "기타(...)"로 빠지고 있었다(2026-07-29 10건 실측). 시각을
    # 문자열로 박아두면 컷오프 변경 때마다 재발하므로 시각 비의존 needle로 교체.
    ("신규 진입 금지",       "마감시간(신규진입금지)"),
    ("Degraded",        "Degraded신뢰도"),
    ("점심 휴식",          "시간대차단"),
    ("진입 금지 시간대",     "시간대차단"),
    ("등급X",            "체크리스트항목미달"),
    # [402차] 347차가 신설한 두 문구도 표에 없어 "기타(...)"로 빠지고 있었다
    # (conf_floor 미달은 2026-07-20~29 4건 실측).
    ("conf_floor 미달",  "conf_floor미달(자동진입OFF)"),
    ("자동진입 비활성화",     "자동진입토글OFF"),
    # [402차] 401차 신설 [정보] 문구 — 차단이 아니라 평가 생략이므로 별도 라벨.
    ("포지션 보유중",       "포지션보유중(평가생략)"),
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

    [461차, F-5] **최종 상태(entry_final_ok/entry_executed)를 grade보다 먼저 본다.**
    위 docstring이 스스로 밝히듯 grade는 "앙상블 단계 등급"인데, 285차-P5가
    "A/B등급 자동진입은 CoherenceGate와 무관하게 허용"을 결정한 뒤로는 앙상블
    grade='X'인 채 체크리스트 상향으로 최종관문까지 가는 행이 합법적으로 존재한다.
    등급으로 먼저 분기하고 continue 하면 그 행이 coherence_blocked/conf미달로
    잘못 계상되고 entered/candidate에서 사라진다 — 전기간(2026-06-17~08-13) 실측
    entry_executed=1의 25건(13.2%), entry_final_ok=1&미체결의 17건이 그렇게 은닉돼
    2026-08-03 진입 20 vs 실제 24, 08-13 JointGateBlock 6 vs 실제 7이 됐다.
    은닉량은 grade_override로 노출한다(계측 4원칙 ③ 탈락 가시화).

    반환: {"date", "total", "flat", "conf_fail", "coherence_blocked",
           "ensemble_pass", "gate_blocked", "gate_breakdown": {label: n},
           "exec_fail", "exec_fail_breakdown": {label: n}, "candidate", "entered",
           "grade_override"}

    grade_override: [461차] 앙상블 grade='X'(또는 direction=0)인데 체크리스트 상향으로
    최종관문까지 간 건수. 0이 정상이 아니라 285차-P5 경로가 살아있다는 뜻이다.
    이 값이 0보다 크면 그만큼 구 집계는 entered/candidate를 적게 말했다.

    exec_fail_breakdown: [305차] entry_final_ok=True인데 entry_executed=False인 건
    (체크리스트 통과 후 2차 실행단계 차단 — JointGateBlock/Hurst미계산/증거금부족/
    Degraded신뢰도 등)을 gate_breakdown과 동일한 방식으로 원인별 집계한다. 기존에는
    "체결실패(게이트 통과 후 미체결)" 건수만 보여 실제 원인(대부분 JointGateBlock)이
    가려졌다 — 원인 미표기 시 마치 주문 체결 자체가 실패한 것처럼 오해하기 쉬움.
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
        "exec_fail": 0, "exec_fail_breakdown": {}, "candidate": 0, "entered": 0,
        "grade_override": 0,
    }
    for r in rows:
        direction = int(r["direction"] or 0)
        grade = str(r["grade"] or "")
        final_ok = bool(r["entry_final_ok"])
        executed = bool(r["entry_executed"])

        # [461차, F-5] 최종 상태 우선 — grade/direction 분기보다 앞에 둔다.
        # 이 순서라야 entered == SUM(entry_executed)가 무조건 성립한다.
        # grade가 C/B인 정상 경로는 아래 분기에 걸릴 일이 없으므로 동작이 같다
        # (구 코드의 executed/final_ok 처리를 그대로 흡수한 것).
        if executed or final_ok:
            if grade == "X" or direction == 0:
                out["grade_override"] += 1
            out["ensemble_pass"] += 1
            out["candidate"] += 1
            if executed:
                out["entered"] += 1
            else:
                out["exec_fail"] += 1
                label = _categorize_block_reason(r["entry_block_reason"], r["checklist_reason"])
                out["exec_fail_breakdown"][label] = out["exec_fail_breakdown"].get(label, 0) + 1
            continue

        if direction == 0:
            out["flat"] += 1
            continue
        if grade == "X":
            if bool(r["coherence_blocked"]):
                out["coherence_blocked"] += 1
            else:
                out["conf_fail"] += 1
            continue

        out["ensemble_pass"] += 1
        out["gate_blocked"] += 1
        label = _categorize_block_reason(r["entry_block_reason"], r["checklist_reason"])
        out["gate_breakdown"][label] = out["gate_breakdown"].get(label, 0) + 1
    return out


#: [461차, G-4] `joint_gate_shadow` 채널 개시일(첫 행 2026-07-15 10:24). 이전 날짜는
#: 표가 비어 있는 것이 정상이므로 검산 ③을 건너뛴다 — 미계측 ≠ 불일치.
_JOINT_SHADOW_SINCE = "2026-07-15"


def verify_daily_entry_funnel(funnel: Dict, date_str: Optional[str] = None) -> List[str]:
    """[461차, G-4] 진입 퍼널 자기검증 — 항등식이 깨지면 사유 문자열을 돌려준다.

    F-5가 고친 결함(퍼널 `entered`가 실제 진입의 13.2%를 누락)은 **6주 넘게 아무
    경보 없이** 지나갔다. 문제의 본질은 버그 하나가 아니라 **검산이 없다는 것**이다.
    같은 사실을 서로 다른 경로로 두 번 세서 어긋나면 그날 즉시 잡는다.

    검사 3종 — 모두 항등식이라 정상이면 오탐이 날 수 없다:

      ① 칸 합계 == total
         (flat + conf_fail + coherence_blocked + gate_blocked + candidate)
      ② entered == SUM(entry_executed)            ← 같은 테이블, 다른 집계 경로
      ③ 퍼널 JointGateBlock 건수 == joint_gate_shadow 당일 행수
         ← **다른 DB**(trades.db)에 다른 코드가 쓴 독립 기록. 2026-08-13에 퍼널이
           6, 실제가 7이었던 바로 그 불일치를 잡는 축이다.

    ③의 모집단 주의 — **두 breakdown을 합쳐야 한다.**
    JointGateBlock으로 차단된 행은 `entry_final_ok` 값에 따라 퍼널에서 갈린다:
    1이면 `exec_fail_breakdown`, 0이면 `gate_breakdown`. 한쪽만 세면 상시 어긋난다
    (실측: 2026-07-20 exec_fail 9 + gate_blocked 2 = shadow 11).

    ③은 `_JOINT_SHADOW_SINCE` 이전 날짜에는 건너뛴다 — 그 채널이 2026-07-15에
    개시돼 이전 날짜는 항상 0이다. **미계측을 불일치로 보고하지 않는다**(계측 4원칙 ②).

    반환: 실패 사유 리스트(빈 리스트 = 전부 통과). 예외는 삼키고 사유로 바꾼다 —
    검산이 EOD 리포트 생성을 깨뜨리면 안 된다.
    """
    import datetime as _dt
    d = date_str or funnel.get("date") or _dt.date.today().isoformat()
    fails = []

    # ① 칸 합계
    parts = (int(funnel.get("flat", 0)) + int(funnel.get("conf_fail", 0))
             + int(funnel.get("coherence_blocked", 0))
             + int(funnel.get("gate_blocked", 0)) + int(funnel.get("candidate", 0)))
    total = int(funnel.get("total", 0))
    if parts != total:
        fails.append("칸합계 기대=%d 실측=%d" % (total, parts))

    # ② entered vs SUM(entry_executed)
    try:
        rows = fetchall(
            PREDICTIONS_DB,
            "SELECT COUNT(*) AS n FROM ensemble_decisions "
            "WHERE substr(ts, 1, 10) = ? AND entry_executed = 1",
            (d,),
        )
        db_exec = int(rows[0]["n"]) if rows else 0
        if int(funnel.get("entered", 0)) != db_exec:
            fails.append("진입 기대=%d 실측(entry_executed)=%d" % (db_exec, funnel.get("entered", 0)))
    except Exception as e:
        fails.append("진입 대조 실패(%s)" % e)

    # ③ JointGateBlock vs joint_gate_shadow (다른 DB의 독립 기록)
    if d >= _JOINT_SHADOW_SINCE:
        try:
            rows = fetchall(
                TRADES_DB,
                "SELECT COUNT(*) AS n FROM joint_gate_shadow WHERE substr(ts, 1, 10) = ?",
                (d,),
            )
            shadow_n = int(rows[0]["n"]) if rows else 0
            funnel_n = (int((funnel.get("exec_fail_breakdown") or {}).get("JointGateBlock", 0))
                        + int((funnel.get("gate_breakdown") or {}).get("JointGateBlock", 0)))
            if funnel_n != shadow_n:
                fails.append("JointGateBlock 퍼널=%d joint_gate_shadow=%d" % (funnel_n, shadow_n))
        except Exception as e:
            fails.append("JointGateBlock 대조 실패(%s)" % e)

    return fails


def fetch_daily_joint_gate_fallback(date_str: Optional[str] = None,
                                    min_samples: int = 20) -> Dict:
    """[461차, G-6] JointGateBlock 중 MetaGate 무정보 폴백 비율 일일 집계.

    460차 F-1이 "매일 사람이 눈으로 세고 있다"고 지적한 값을 자동화한다.
    판정 조건은 *"폴백 비율이 3거래일 연속 80% 초과면 게이트 쪽 원인"* 인데,
    그 입력을 손으로 만들고 있었다.

    ⚠ **폴백 여부를 meta 값으로 추정하지 않는다.** `meta_size == 0.50`으로 세면
    "학습값이 우연히 0.50인 행"과 구분이 안 된다. 420차가 신설한
    `joint_gate_shadow.meta_size_fallback`(1 = `learned["size_multiplier"] or 0.5`
    폴백 발동)을 그대로 읽는다 — 2026-08-13 실측 7건 중 6건(85.7%)으로 수동 집계와 일치.

    420차 이전 행은 그 컬럼이 NULL이다 → **미계측으로 따로 센다**(계측 4원칙 ②).
    NULL을 0(=학습값)으로 뭉개면 폴백 건이 학습값처럼 보인다.

    반환: {"n", "fallback", "learned", "unmeasured", "pct", "remain_to_min",
           "min_samples", "verdict_ready"}
    `verdict_ready=False`면 **판정문을 출력하지 말 것**(313차 원칙 — 소표본 확정 금지).
    """
    import datetime as _dt
    d = date_str or _dt.date.today().isoformat()
    out = {"n": 0, "fallback": 0, "learned": 0, "unmeasured": 0, "pct": None,
           "min_samples": min_samples, "remain_to_min": min_samples,
           "verdict_ready": False}
    rows = fetchall(
        TRADES_DB,
        "SELECT meta_size_fallback FROM joint_gate_shadow WHERE substr(ts, 1, 10) = ?",
        (d,),
    )
    out["n"] = len(rows)
    for r in rows:
        v = r["meta_size_fallback"]
        if v is None:
            out["unmeasured"] += 1
        elif int(v) == 1:
            out["fallback"] += 1
        else:
            out["learned"] += 1

    known = out["fallback"] + out["learned"]
    if known > 0:
        out["pct"] = round(100.0 * out["fallback"] / known, 1)
    out["remain_to_min"] = max(min_samples - known, 0)
    out["verdict_ready"] = known >= min_samples
    return out


def fetch_realized_volatility_context(date_str: Optional[str] = None, lookback_days: int = 5) -> Dict:
    """[369차, 0723 정기점검] mc-conf 괴리 경보(진입후보 하한 미달)가 뜰 때,
    원인이 "모델 이상"인지 "그날 시장 자체가 조용했음"인지 즉시 구분하기 위한
    실측 변동성 컨텍스트. raw_candles(1분봉 close)로 당일 레인지·평균 1분 변동폭을
    계산해 직전 lookback_days 영업일 평균과 대조한다.

    딥다이브를 위해 매번 수동으로 raw_candles를 조회해야 했던 절차
    (0723 정기점검에서 실제로 이 계산을 손으로 반복함)를 리포트에 상시 포함시켜
    자동화한다 — 정책 판단에는 관여하지 않는 순수 진단 보조 지표.

    반환: {"today_range": float, "today_mean_abs_move": float,
           "avg_range": float, "avg_mean_abs_move": float, "n_days": int}
    실패/데이터부족 시 빈 dict.
    """
    import datetime as _dt
    d = date_str or _dt.date.today().isoformat()

    def _day_stats(day: str) -> Optional[tuple]:
        rows = fetchall(
            RAW_DATA_DB,
            "SELECT close FROM raw_candles WHERE substr(ts, 1, 10) = ? ORDER BY ts",
            (day,),
        )
        closes = [r["close"] for r in rows if r["close"] is not None]
        if len(closes) < 5:
            return None
        moves = [abs(closes[i] - closes[i - 1]) for i in range(1, len(closes))]
        return (max(closes) - min(closes), sum(moves) / len(moves))

    today_stats = _day_stats(d)
    if today_stats is None:
        return {}

    prior_ranges, prior_moves = [], []
    cursor = _dt.date.fromisoformat(d)
    scanned = 0
    while len(prior_ranges) < lookback_days and scanned < lookback_days * 3:
        cursor -= _dt.timedelta(days=1)
        scanned += 1
        stat = _day_stats(cursor.isoformat())
        if stat is not None:
            prior_ranges.append(stat[0])
            prior_moves.append(stat[1])

    if not prior_ranges:
        return {}

    return {
        "today_range": today_stats[0],
        "today_mean_abs_move": today_stats[1],
        "avg_range": sum(prior_ranges) / len(prior_ranges),
        "avg_mean_abs_move": sum(prior_moves) / len(prior_moves),
        "n_days": len(prior_ranges),
    }


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
    # [459차 F1] 승패 집계 단위 전환 표식. 과거 행은 **소급 수정하지 않는다**
    # (fetch_trend_daily 등 추이 지표에 불연속이 생긴다) — NULL로 남는 날은
    # v1(레그 단위), 값이 있는 날은 v2(포지션 단위)라는 뜻이다.
    cols = {
        row["name"]
        for row in fetchall(TRADES_DB, "PRAGMA table_info(daily_stats)")
    }
    if "win_formula_version" not in cols:
        execute(TRADES_DB,
                "ALTER TABLE daily_stats ADD COLUMN win_formula_version INTEGER")


def save_daily_stats(date_str: str, stats: dict) -> None:
    """일일 마감 통계 저장 — daily_close() 에서 호출."""
    execute(TRADES_DB, """
        INSERT OR REPLACE INTO daily_stats
            (date, trades, wins, pnl_pts, pnl_krw, sgd_accuracy, verified_count,
             win_formula_version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date_str,
        int(stats.get("trades",        0)),
        int(stats.get("wins",          0)),
        float(stats.get("pnl_pts",     0.0)),
        float(stats.get("pnl_krw",     0.0)),
        float(stats.get("sgd_accuracy",0.5)),
        int(stats.get("verified_count",0)),
        WIN_COUNT_FORMULA_VERSION,
    ))


def _trend_sql(bucket_expr: str, alias: str, extra_where: str, limit) -> str:
    """[456차 / F1] 추이 집계 SQL — **포지션 단위**로 승패를 센다.

    `trades` 테이블은 **청산 레그마다 한 행**이다. 종전 쿼리는 `COUNT(*)`로 행을 세고
    레그별 `pnl_pts > 0`으로 승패를 판정해, 다레그 포지션이 여러 건으로 계상되고
    부분청산으로 손실을 턴 포지션이 "승"이 됐다.

    2026-08-10 실측: 13레그 = 10포지션, 레그 기준 승률과 포지션 기준(7승3패)이 불일치.
    같은 결함을 `PositionTracker`(daily_stats·restore_daily_stats) 쪽에서 고쳤으므로
    여기도 맞추지 않으면 "오늘 마감"과 "추이 차트의 오늘"이 서로 다른 값을 낸다.

    승패 기준은 **계약가중 pt 합**이다 — 레그 수량이 다르면 비가중 합은 부호까지
    뒤집힐 수 있다(예: -1.0pt×3 + 2.0pt×1 = -1.0 인데 비가중은 +1.0).

    ⚠ 네 개 추이 함수가 같은 SQL을 복사해 쓰다 한쪽만 고쳐지는 것을 막으려고
    한 곳에서 만든다(333차 후속4가 `campaign_steps`에서 겪은 동기화 드리프트).
    """
    return """
        WITH pos AS (
            SELECT {bucket} AS {alias},
                   SUM(COALESCE(forward_pnl_pts, pnl_pts) * COALESCE(quantity, 1)) AS pos_pts,
                   SUM(COALESCE(forward_net_pnl_krw, forward_pnl_krw,
                                net_pnl_krw, pnl_krw)) AS pos_krw
            FROM trades
            WHERE exit_ts IS NOT NULL
                  AND COALESCE(entry_source, '') != 'GHOST_PENDING_MISS'
                  {extra}
            GROUP BY entry_ts
        )
        SELECT {alias},
               COUNT(*) AS trades,
               SUM(CASE WHEN pos_pts > 0 THEN 1 ELSE 0 END) AS wins,
               COUNT(*) - SUM(CASE WHEN pos_pts > 0 THEN 1 ELSE 0 END) AS losses,
               ROUND(AVG(CASE WHEN pos_pts > 0 THEN 1.0 ELSE 0.0 END), 4) AS win_rate,
               ROUND(SUM(pos_krw), 0) AS pnl_krw
        FROM pos
        GROUP BY {alias}
        ORDER BY {alias} DESC
        {limit}
    """.format(bucket=bucket_expr, alias=alias, extra=extra_where,
               limit=("LIMIT %d" % limit) if limit else "")


def fetch_trend_daily(days_back: int = 30) -> List[dict]:
    """일별 집계 (최대 30일). trades.db 체결 + daily_stats 정확도 병합."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days_back)).isoformat()
    rows = fetchall(
        TRADES_DB,
        _trend_sql("date(entry_ts)", "date", "AND entry_ts >= ?", 30),
        (cutoff,))
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
    """주별 집계 (최대 12주). 승패 단위는 `_trend_sql` 참조."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(weeks=weeks_back)).isoformat()
    return [dict(r) for r in fetchall(
        TRADES_DB,
        _trend_sql("strftime('%Y-W%W', entry_ts)", "week", "AND entry_ts >= ?", 12),
        (cutoff,))]


def fetch_trend_monthly(months_back: int = 12) -> List[dict]:
    """월별 집계 (최대 12개월). 승패 단위는 `_trend_sql` 참조."""
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=months_back * 31)).isoformat()
    return [dict(r) for r in fetchall(
        TRADES_DB,
        _trend_sql("strftime('%Y-%m', entry_ts)", "month", "AND entry_ts >= ?", 12),
        (cutoff,))]


def fetch_trend_yearly() -> List[dict]:
    """연간 집계 (전체). 승패 단위는 `_trend_sql` 참조."""
    return [dict(r) for r in fetchall(
        TRADES_DB,
        _trend_sql("strftime('%Y', entry_ts)", "year", "", None))]


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


def save_tb_verdict(
    horizon: str, judged_at: str, eval_start: str, model_mtime: str,
    n_samples: int, ic_tb: Optional[float], ic_3class: Optional[float], verdict: str,
) -> None:
    """[384차] 검증캠페인 [1] 채널 — 호라이즌이 이번 판정에서 OOS n>=min_samples_hz에
    도달했을 때만 호출. 이 로그의 "해당 호라이즌 최신 행"이 다음 판정(재도달) 전까지
    캠페인 집계에 쓰이는 유효 판정(carry-forward)이 된다."""
    execute(
        TRADES_DB,
        """INSERT INTO tb_verdict_log
           (horizon, judged_at, eval_start, model_mtime, n_samples, ic_tb, ic_3class, verdict)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (horizon, judged_at, eval_start, model_mtime, n_samples, ic_tb, ic_3class, verdict),
    )


def pc_id() -> str:
    """[MW0601 405차 / P0-5] 이 PC의 식별자 — 호스트명에서 `MW####`를 추출.

    두 운영 머신의 호스트명이 `DeskTop-MW0601` / `DeskTop-MW0602` 형태라 정규식
    한 줄로 뽑힌다. 매칭 실패 시 호스트명 원문(최대 32자)을 그대로 쓰고, 그마저
    실패하면 "UNKNOWN". config 상수로 두지 않는 이유는 PC별로 다른 값을 git에
    커밋할 수 없기 때문이다(멀티 PC pull 호환성 — feedback_git_commit_scope).
    """
    try:
        import platform as _pf
        import re as _re
        host = _pf.node() or ""
        m = _re.search(r"(MW\d{4})", host, _re.IGNORECASE)
        if m:
            return m.group(1).upper()
        return host[:32] if host else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def save_guard_shadow(
    ts: str, horizon: str, acc_txt: float, old_acc_live: Optional[float],
    new_cv: float, live_note: str, actual_verdict: str, n_samples: int,
    source: str = "eod",
    fair_new: Optional[float] = None, fair_old: Optional[float] = None,
    fair_hold_bars: Optional[int] = None, fair_note: Optional[str] = None,
    fair_contaminated_bars: Optional[int] = None,
    incumbent_source: Optional[str] = None,
    incumbent_cutoff_ts: Optional[str] = None,
    verdict_source: Optional[str] = None,
    clean_new: Optional[float] = None, clean_old: Optional[float] = None,
    clean_n: Optional[int] = None, clean_note: Optional[str] = None,
    live_acc: Optional[float] = None, live_n: Optional[int] = None,
    fair_valid: Optional[int] = None,
) -> None:
    """[404차, P0-4 후속] EOD/intraday 모델가드 GuardShadow 1행 저장.

    fair_verdict/distortion은 old_acc_live가 있을 때만 계산한다(측정 불가 시
    "검증 폴드 없음"·"피처셋 변경" 등으로 None) — acc.txt vs new(cv)는 서로 다른
    시점 데이터로 채점돼 비교 자격이 없으므로 fair_verdict을 그 값으로 대체하지
    않는다(learning/batch_retrainer.py:_measure_incumbent_acc 한계 참조).

    [404차 후속] source="intraday"는 계측 전용이다 — intraday는 가드 자체가
    없어 actual_verdict은 항상 "REPLACE"로 기록되며(실제로 항상 무조건 교체됨을
    그대로 반영), fair_verdict은 "만약 EOD처럼 가드를 걸었다면 통과했을지"를
    보여주는 참고값일 뿐 어떤 결정에도 관여하지 않는다.

    [MW0602 457차] `fair_valid` — fair_new/fair_old 비교가 **성립하는 행인지**.
    0이면 현행 모델이 홀드아웃 구간을 이미 학습한 상태라 격차가 성능차가 아니라
    in-sample 프리미엄이다. 457차 이전 42행은 전부 NULL이며, 그 구간 실측은
    36행 중 35행 도전자 열위(평균 -0.1161)였다 — **그 표본으로 GuardFair를
    판정하면 안 된다.** 값은 무효여도 기록한다(무효율 자체가 지표다)."""
    distortion = (acc_txt - old_acc_live) if old_acc_live is not None else None
    fair_verdict = (
        ("REPLACE" if new_cv > old_acc_live else "HOLD")
        if old_acc_live is not None else None
    )
    execute(
        TRADES_DB,
        """INSERT INTO guard_shadow_log
           (ts, horizon, source, acc_txt, old_acc_live, new_cv, live_note,
            distortion, actual_verdict, fair_verdict, n_samples, pc,
            fair_new, fair_old, fair_hold_bars, fair_note,
            fair_contaminated_bars, incumbent_source, incumbent_cutoff_ts,
            verdict_source, clean_new, clean_old, clean_n, clean_note,
            live_acc, live_n, fair_valid)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                   ?, ?, ?, ?, ?, ?, ?)""",
        (ts, horizon, source, acc_txt, old_acc_live, new_cv, live_note,
         distortion, actual_verdict, fair_verdict, n_samples, pc_id(),
         fair_new, fair_old, fair_hold_bars, fair_note,
         fair_contaminated_bars, incumbent_source, incumbent_cutoff_ts,
         verdict_source, clean_new, clean_old, clean_n, clean_note,
         live_acc, live_n, fair_valid),
    )


def fetch_live_frequential_acc(horizon: str, date_str: str):
    """[MW0601 458차 / P1-B] 그날 배포본이 **라이브에서 실제로** 낸 적중률.

    EOD 가드가 지키는 구간은 다음날 08:55~09:37의 42분뿐이다 — 09:37 첫 장중
    재학습이 EOD 모델을 덮어쓰고 이후 마감까지는 무가드 장중 모델이 복무한다
    (404차가 재현 분산 8.83%p를 근거로 장중 게이트를 걸지 않기로 한 의도적 결정).
    그러므로 품질 리스크의 몸통은 장중 모델에 있는데, 지금까지 그것을 EOD 시점에
    돌아보는 계측이 없었다.

    predictions 테이블은 매분 STEP1에서 이미 채점되므로(correct 컬럼) 추가 계산이
    없다 — 읽기 1회다. 관찰 전용이며 어떤 판정에도 쓰지 않는다.

    Returns: (acc, n) — 표본 없으면 (None, 0).
    ⚠ "표본 없음"과 "적중률 0.0"을 같은 값으로 돌려주지 않는다(계측 4원칙 ②).
    """
    rows = fetchall(
        PREDICTIONS_DB,
        """SELECT AVG(correct) AS acc, COUNT(correct) AS n
           FROM predictions
           WHERE horizon = ? AND date(ts) = ? AND correct IS NOT NULL""",
        (horizon, date_str),
    )
    if not rows or not rows[0]["n"]:
        return None, 0
    return float(rows[0]["acc"]), int(rows[0]["n"])


def fetch_latest_tb_verdicts() -> Dict[str, sqlite3.Row]:
    """[384차] 호라이즌별 가장 최근 tb_verdict_log 행 (carry-forward 조회용)."""
    rows = fetchall(
        TRADES_DB,
        """SELECT t.* FROM tb_verdict_log t
           INNER JOIN (
               SELECT horizon, MAX(judged_at) AS max_judged_at
               FROM tb_verdict_log GROUP BY horizon
           ) m ON t.horizon = m.horizon AND t.judged_at = m.max_judged_at""",
    )
    return {r["horizon"]: r for r in rows}


def fetch_tb_verdicts_judged_on(date_str: str) -> List[str]:
    """[384차] 해당 날짜(YYYY-MM-DD)에 새로 판정된 호라이즌 목록 — 섀도우 TB
    재학습(batch_retrainer.retrain_shadow_triple_barrier)이 이 목록에 있는
    호라이즌만 재학습하고 나머지는 모델 파일을 건드리지 않아 OOS 누적을 보존한다."""
    rows = fetchall(
        TRADES_DB,
        "SELECT DISTINCT horizon FROM tb_verdict_log WHERE judged_at LIKE ?",
        (date_str + "%",),
    )
    return [r["horizon"] for r in rows]


def init_all_dbs():
    """전체 DB 초기화 (main.py에서 1회 호출)"""
    init_predictions_db()
    init_trades_db()
    init_daily_stats_db()
    init_shap_db()
    init_raw_data_db()
    init_daily_broker_pnl_db()
