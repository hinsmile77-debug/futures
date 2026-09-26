# -*- coding: utf-8 -*-
"""[MW0601 631차] 기동 DB 초기화 지연 — F-1a(부분 인덱스) · F-2([DBInit]) · F-5([BOOT]).

2026-09-26 부팅 직후 기동이 `_migrate_predictions_db` 의 역채움 UPDATE 에서 ≥210초
멈췄다. 세 확률 열이 ALTER 로 `features` 뒤에 붙어 NULL 판정에도 행 전체를 읽는
구조였다. 부분 인덱스로 UPDATE 가 인덱스만 훑게 한다 — 역채움 안전망은 유지.
"""
import io
import os
import sqlite3

import utils.db_utils as D

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _legacy_db(path):
    """운영 DB 와 같은 열 순서 — 확률 열이 features 뒤에 ALTER 로 붙은 구세대."""
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, horizon TEXT NOT NULL,
        direction INTEGER, confidence REAL, actual INTEGER, correct INTEGER,
        features TEXT, created_at TEXT)""")
    con.executemany(
        "INSERT INTO predictions (ts, horizon, direction, confidence, features) "
        "VALUES (?,?,?,?,?)",
        [("2026-09-26 09:%02d" % i, "1m", (i % 3) - 1, 0.6, "x" * 3000) for i in range(30)])
    con.commit()
    con.close()


def test_partial_index_created_and_backfill_still_works(tmp_path, monkeypatch):
    db = str(tmp_path / "p.db")
    _legacy_db(db)
    monkeypatch.setattr(D, "PREDICTIONS_DB", db)

    D._migrate_predictions_db()

    con = sqlite3.connect(db)
    idx = con.execute("SELECT sql FROM sqlite_master WHERE name='idx_pred_prob_null'").fetchone()
    assert idx and "WHERE" in idx[0].upper(), "부분 인덱스가 없으면 매 기동 전수 스캔으로 돌아간다"
    # 역채움 안전망 — 구세대 NULL 행이 모두 채워져야 한다
    assert con.execute("SELECT COUNT(*) FROM predictions WHERE up_prob IS NULL "
                       "OR down_prob IS NULL OR flat_prob IS NULL").fetchone()[0] == 0
    # 방향=1, conf=0.6 → up=0.6
    assert con.execute("SELECT up_prob FROM predictions WHERE direction=1 LIMIT 1").fetchone()[0] == 0.6
    plan = " ".join(str(r) for r in con.execute(
        "EXPLAIN QUERY PLAN UPDATE predictions SET up_prob=up_prob WHERE "
        "up_prob IS NULL OR down_prob IS NULL OR flat_prob IS NULL").fetchall())
    assert "idx_pred_prob_null" in plan, "UPDATE 가 부분 인덱스를 타지 않는다: %s" % plan
    con.close()


def test_migrate_idempotent(tmp_path, monkeypatch):
    db = str(tmp_path / "p.db")
    _legacy_db(db)
    monkeypatch.setattr(D, "PREDICTIONS_DB", db)
    D._migrate_predictions_db()
    D._migrate_predictions_db()   # 두 번째 기동 — 예외 없이 통과해야 한다


def test_init_all_dbs_reports_every_step():
    src = io.open(os.path.join(_ROOT, "utils", "db_utils.py"), encoding="utf-8").read()
    block = src[src.index("def init_all_dbs():"):]
    block = block[:block.index("return timings")]
    for fn in ("init_predictions_db", "init_trades_db", "init_daily_stats_db", "init_shap_db",
               "init_raw_data_db", "init_daily_broker_pnl_db", "init_broker_sync_recon_db",
               "init_premarket_levels_db"):
        assert fn in block, "%s 가 init_all_dbs 에서 빠졌다" % fn
    assert "[DBInit]" in block


def test_main_boot_progress_wired():
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("init_all_dbs()\n    finally:")
    seg = src[i - 1500:i + 400]
    assert "[BOOT] DB 초기화 중" in seg
    assert "_boot_done.set()" in seg, "진행 표시 스레드가 멈추지 않으면 콘솔에 영원히 찍힌다"
    assert "daemon=True" in seg
