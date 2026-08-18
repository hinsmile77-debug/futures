# -*- coding: utf-8 -*-
"""[MW0601 477차 후속3 / 476차 F-3 재설계 + G-1] 훅 경로 분리 + MFE 소급 계측.

고정하는 사실:
① synthetic_partial_exits 마이그레이션이 기존 행을 'qty1_static'/entry_qty=1로
   백필한다 — NULL로 두면 레거시와 신규 qty≥2를 구분할 수 없다.
② [25] _load_hooks()는 qty1_static(+레거시 NULL)만 읽는다 — qty≥2 훅이 들어와도
   사전등록 판정 모집단이 오염되지 않는다(§9-4 합격선 무변경).
   ⚠ [25] v1 경로에는 qty 필터가 없고 report_both_engines=True라 v1도 계산되므로
   이 필터가 유일한 방어선이다.
③ position_mfe_shadow: SHORT/LONG MFE·MAE 방향, 추세일 판정의 룩어헤드 부재,
   표본 미달 시 INSUFFICIENT.
"""
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.db_utils as du
import scripts.position_mfe_shadow as pmf
import scripts.tp1_protect_offset_shadow as tpo


# ── ①② 훅 경로 분리 ───────────────────────────────────────────────


def _legacy_spe_db(path):
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE synthetic_partial_exits (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, entry_ts TEXT,
        direction TEXT NOT NULL, entry_price REAL NOT NULL,
        synthetic_price REAL NOT NULL, synthetic_fraction REAL NOT NULL,
        synthetic_pnl_pts REAL NOT NULL, protect_mode TEXT, stop_after REAL,
        created_at TEXT)""")
    con.execute("""INSERT INTO synthetic_partial_exits
        (ts, entry_ts, direction, entry_price, synthetic_price,
         synthetic_fraction, synthetic_pnl_pts, protect_mode, stop_after)
        VALUES ('2026-08-12 10:00:00','2026-08-12 09:59:00','SHORT',
                350.0, 349.0, 0.33, 1.0, 'atr_profit', 350.3)""")
    con.commit()
    con.close()


def test_migration_backfills_hook_path(tmp_path, monkeypatch):
    p = str(tmp_path / "trades.db")
    _legacy_spe_db(p)
    monkeypatch.setattr(du, "TRADES_DB", p)
    du.init_synthetic_partial_exits_db() if hasattr(
        du, "init_synthetic_partial_exits_db") else du.init_trades_db()
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT hook_path, entry_qty FROM synthetic_partial_exits").fetchone()
    con.close()
    assert r["hook_path"] == "qty1_static"     # 레거시 행은 전부 qty=1 시절이다
    assert r["entry_qty"] == 1


def test_load_hooks_excludes_qty2plus(tmp_path, monkeypatch):
    p = str(tmp_path / "trades2.db")
    _legacy_spe_db(p)
    con = sqlite3.connect(p)
    con.execute("ALTER TABLE synthetic_partial_exits ADD COLUMN hook_path TEXT")
    con.execute("ALTER TABLE synthetic_partial_exits ADD COLUMN entry_qty INTEGER")
    con.execute("UPDATE synthetic_partial_exits SET hook_path='qty1_static', entry_qty=1")
    con.execute("""INSERT INTO synthetic_partial_exits
        (ts, entry_ts, direction, entry_price, synthetic_price, synthetic_fraction,
         synthetic_pnl_pts, protect_mode, stop_after, hook_path, entry_qty)
        VALUES ('2026-08-18 10:21:00','2026-08-18 10:20:59','SHORT',
                350.0, 349.1, 0.33, 0.9, 'partial_exit', 350.5,
                'qty2plus_partial', 2)""")
    con.commit(); con.close()
    monkeypatch.setattr(tpo, "TRADES_DB", p)
    hooks = tpo._load_hooks("2026-06-01")
    assert len(hooks) == 1                       # qty≥2 행은 판정 모집단에서 제외
    assert hooks[0]["ts"].startswith("2026-08-12")


def test_load_hooks_legacy_db_without_column(tmp_path, monkeypatch):
    """컬럼이 아직 없는 DB(코드만 먼저 pull한 PC)에서도 죽지 않는다."""
    p = str(tmp_path / "trades3.db")
    _legacy_spe_db(p)
    monkeypatch.setattr(tpo, "TRADES_DB", p)
    assert len(tpo._load_hooks("2026-06-01")) == 1


# ── ③ position_mfe_shadow ────────────────────────────────────────


def _mfe_dbs(tmp_path, positions, bars):
    tdb = str(tmp_path / "t.db")
    rdb = str(tmp_path / "r.db")
    con = sqlite3.connect(tdb)
    con.execute("""CREATE TABLE trades (
        entry_ts TEXT, exit_ts TEXT, direction TEXT, entry_price REAL,
        entry_qty INTEGER, quantity INTEGER, pnl_pts REAL,
        entry_horizon TEXT, hurst_bucket TEXT)""")
    con.executemany(
        "INSERT INTO trades VALUES (?,?,?,?,?,?,?,?,?)", positions)
    con.commit(); con.close()
    con = sqlite3.connect(rdb)
    con.execute("CREATE TABLE raw_candles (ts TEXT, high REAL, low REAL)")
    con.executemany("INSERT INTO raw_candles VALUES (?,?,?)", bars)
    con.commit(); con.close()
    return tdb, rdb


def test_short_mfe_uses_low_and_mae_uses_high(tmp_path, monkeypatch):
    bars = [("2026-08-18 10:%02d:00" % m, 350.0 + m * 0.1, 348.0 - m * 0.5)
            for m in range(0, 30)]
    pos = [("2026-08-18 10:00:00", "2026-08-18 10:02:00", "SHORT", 350.0,
            2, 1, 2.0, "3m", "trend")]
    tdb, rdb = _mfe_dbs(tmp_path, pos, bars)
    monkeypatch.setattr(pmf, "TRADES_DB", tdb)
    monkeypatch.setattr(pmf, "RAW_DATA_DB", rdb)
    res = pmf.compute("2026-06-01")
    r = res["rows"][0]
    # SHORT: MFE = entry − 최저 low (10봉째 low = 348.0 − 5.0 = 343.0 → 7.0)
    assert r["mfe10"] == pytest.approx(7.0)
    # SHORT: MAE = 최고 high − entry (10봉째 high = 351.0 → 1.0)
    assert r["mae10"] == pytest.approx(1.0)
    # 계약당 실현 = 합 pnl_pts / entry_qty
    assert r["realized_per_ct"] == pytest.approx(1.0)


def test_long_direction_flips_mfe_mae(tmp_path, monkeypatch):
    bars = [("2026-08-18 10:%02d:00" % m, 350.0 + m * 0.5, 349.0 - m * 0.1)
            for m in range(0, 30)]
    pos = [("2026-08-18 10:00:00", "2026-08-18 10:05:00", "LONG", 350.0,
            1, 1, 1.0, "1m", "trend")]
    tdb, rdb = _mfe_dbs(tmp_path, pos, bars)
    monkeypatch.setattr(pmf, "TRADES_DB", tdb)
    monkeypatch.setattr(pmf, "RAW_DATA_DB", rdb)
    r = pmf.compute("2026-06-01")["rows"][0]
    assert r["mfe10"] == pytest.approx(5.0)     # high 355.0 − entry 350.0
    assert r["mae10"] == pytest.approx(2.0)     # entry 350.0 − 최저 low 348.0


def test_trend_day_uses_prior_days_only(tmp_path, monkeypatch):
    """추세일 판정 기준선은 **직전** 거래일 평균 — 당일을 넣으면 룩어헤드다."""
    bars = []
    for d, span in (("2026-08-14", 10.0), ("2026-08-17", 10.0), ("2026-08-18", 40.0)):
        for m in range(0, 30):
            bars.append(("%s 10:%02d:00" % (d, m), 350.0 + span / 2, 350.0 - span / 2))
    pos = [("2026-08-18 10:00:00", "2026-08-18 10:02:00", "SHORT", 350.0,
            1, 1, 1.0, "3m", "trend")]
    tdb, rdb = _mfe_dbs(tmp_path, pos, bars)
    monkeypatch.setattr(pmf, "TRADES_DB", tdb)
    monkeypatch.setattr(pmf, "RAW_DATA_DB", rdb)
    r = pmf.compute("2026-06-01")["rows"][0]
    assert r["day_range_base_pt"] == pytest.approx(10.0)   # 당일 40이 섞이지 않는다
    assert r["is_trend_day"] is True                       # 40 >= 10 × 1.5


def test_insufficient_when_below_min_samples(tmp_path, monkeypatch):
    bars = [("2026-08-18 10:%02d:00" % m, 351.0, 349.0) for m in range(0, 30)]
    pos = [("2026-08-18 10:00:00", "2026-08-18 10:02:00", "SHORT", 350.0,
            1, 1, 1.0, "3m", "trend")]
    tdb, rdb = _mfe_dbs(tmp_path, pos, bars)
    monkeypatch.setattr(pmf, "TRADES_DB", tdb)
    monkeypatch.setattr(pmf, "RAW_DATA_DB", rdb)
    res = pmf.compute("2026-06-01")
    assert res["verdict"] == "INSUFFICIENT"
    assert "판정 보류" in res["reason"]
