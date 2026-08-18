# -*- coding: utf-8 -*-
"""[MW0601 477차 후속2 / 476차 F-4] daily_broker_pnl 단위 명시 + 유령 행 가드.

고정하는 사실:
① 비거래일(predictions·trades 모두 0행)에는 upsert가 행을 만들지 않는다 —
   달력 기준 `_yesterday`가 주말마다 직전 금요일 값을 복제하던 결함(8월 실측
   4행, 전환기준 ① SUM 시 +151만원 이중가산)의 재발 방지.
② upsert(gross 갱신)는 EOD가 기입한 commission/net을 지우지 않는다.
③ update_daily_broker_pnl_net은 브로커 행이 없으면 엔진 gross로 행을 만든다
   (0원 거래일 기록 불가 보완 — 계측 4원칙 ②).
"""
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.db_utils as du


@pytest.fixture
def tmp_dbs(tmp_path, monkeypatch):
    tdb = str(tmp_path / "trades.db")
    pdb = str(tmp_path / "predictions.db")
    con = sqlite3.connect(tdb)
    con.execute("CREATE TABLE trades (entry_ts TEXT)")
    con.commit(); con.close()
    con = sqlite3.connect(pdb)
    con.execute("CREATE TABLE predictions (ts TEXT)")
    con.commit(); con.close()
    monkeypatch.setattr(du, "TRADES_DB", tdb)
    monkeypatch.setattr(du, "PREDICTIONS_DB", pdb)
    du._trading_date_cache.clear()
    du.init_daily_broker_pnl_db()
    return tdb, pdb


def _rows(tdb):
    con = sqlite3.connect(tdb)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT date, pnl_krw, commission_krw, pnl_net_krw FROM daily_broker_pnl ORDER BY date"
    ).fetchall()
    con.close()
    return rows


def _mark_trading_day(pdb, date_str):
    con = sqlite3.connect(pdb)
    con.execute("INSERT INTO predictions (ts) VALUES (?)", (date_str + " 09:01:00",))
    con.commit(); con.close()


def test_non_trading_date_blocked(tmp_dbs):
    tdb, pdb = tmp_dbs
    du.upsert_daily_broker_pnl("2026-08-16", 32000.0)   # 일요일 유령 행 시나리오
    assert _rows(tdb) == []


def test_trading_date_allowed_and_zero_skipped(tmp_dbs):
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, "2026-08-18")
    du.upsert_daily_broker_pnl("2026-08-18", 0.0)       # 빈 TR 폴백 — 스킵 유지
    assert _rows(tdb) == []
    du.upsert_daily_broker_pnl("2026-08-18", 685000.0)
    rows = _rows(tdb)
    assert len(rows) == 1 and rows[0]["pnl_krw"] == 685000.0
    assert rows[0]["commission_krw"] is None            # NULL = EOD 미기입(미측정)


def test_upsert_preserves_eod_columns(tmp_dbs):
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, "2026-08-18")
    du.upsert_daily_broker_pnl("2026-08-18", 600000.0)
    du.update_daily_broker_pnl_net("2026-08-18", 685000.0, 23332.0, 661668.0)
    du.upsert_daily_broker_pnl("2026-08-18", 685000.0)  # 이후 gross 재갱신
    r = _rows(tdb)[0]
    assert r["pnl_krw"] == 685000.0
    assert r["commission_krw"] == pytest.approx(23332.0)   # 지워지지 않는다
    assert r["pnl_net_krw"] == pytest.approx(661668.0)


def test_eod_update_creates_row_when_broker_missing(tmp_dbs):
    tdb, pdb = tmp_dbs
    du.update_daily_broker_pnl_net("2026-08-19", 0.0, 3300.0, -3300.0)  # 0원 gross 거래일
    r = _rows(tdb)[0]
    assert r["pnl_krw"] == 0.0                       # 엔진 gross로 생성
    assert r["pnl_net_krw"] == pytest.approx(-3300.0)


def test_trading_date_cache_and_trades_fallback(tmp_dbs):
    tdb, pdb = tmp_dbs
    # predictions 없음 + trades 있음 → 거래일 (예: predictions DB 유실 복구 시)
    con = sqlite3.connect(tdb)
    con.execute("INSERT INTO trades (entry_ts) VALUES ('2026-08-20 10:00:00')")
    con.commit(); con.close()
    assert du.is_krx_trading_date("2026-08-20") is True
    assert du._trading_date_cache["2026-08-20"] is True


def test_legacy_schema_migrated(tmp_path, monkeypatch):
    """구버전 3컬럼 테이블도 init에서 commission/net 컬럼을 따라잡는다."""
    tdb = str(tmp_path / "trades_legacy.db")
    con = sqlite3.connect(tdb)
    con.execute("""CREATE TABLE daily_broker_pnl (
        date TEXT PRIMARY KEY, pnl_krw REAL NOT NULL, updated_at TEXT NOT NULL)""")
    con.execute("INSERT INTO daily_broker_pnl VALUES ('2026-08-14', 32000.0, 'x')")
    con.commit(); con.close()
    monkeypatch.setattr(du, "TRADES_DB", tdb)
    du.init_daily_broker_pnl_db()
    con = sqlite3.connect(tdb)
    cols = {r[1] for r in con.execute("PRAGMA table_info(daily_broker_pnl)")}
    con.close()
    assert {"commission_krw", "pnl_net_krw"} <= cols
