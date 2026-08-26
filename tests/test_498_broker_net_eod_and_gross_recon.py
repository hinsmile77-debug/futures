# -*- coding: utf-8 -*-
"""[MW0601 498차 / F-8·F-9] 브로커 net 축 EOD 보정 + gross 대사 자기참조 분리.

왜 필요한가 (2026-08-26 실측 — 이상점 1-9·1-10)
------------------------------------------------
**F-8.** 실전 전환 기준 ①의 판정 원천인 `daily_broker_pnl.broker_net_krw` 가
그날 하루만 NULL 이었다(직전 20거래일은 전부 존재). 값이 안 온 것이 아니라
**저장 경로가 안 탔다** — net 축 저장이 「FLAT 상태의 잔고 TR 푸시」라는 기회
의존적 사건에 묶여 있는데, 마지막 푸시(12:19:01)가 최종 청산 처리 도중이라
`position.status` 가 아직 FLAT 이 아니었고 그 뒤 푸시가 오지 않았다.

**F-9.** 같은 날 `[BrokerPnl] … (broker gross 대사 일치)` 는 **자기 자신과
대사**하고 있었다. `update_daily_broker_pnl_net()` 이 행이 없으면 엔진 gross 로
행을 만드는데, 그 **직후** 같은 행을 되읽어 "브로커 gross" 로 썼다. 그래서
`_f4_broker` 는 절대 None 이 될 수 없었고 else 분기는 도달 불가 코드였다
(471차 F-1·474차와 같은 계열 — 계측 4원칙 ⑤).

고정하는 불변식
---------------
① EOD 스냅샷 보정은 **NULL 일 때만** 쓴다 — 실측(live) 기입을 덮지 않는다
② 보정으로 쓴 값에는 **출처와 관측 시각**이 같은 행에 남는다(계측 4원칙 ②·④)
③ 15:10 이전 스냅샷은 `stale_snapshot` 으로 구분된다 — live 와 같은 값이 아니다
④ gross 대사는 **쓰기 전 상태**를 본다 — 행이 없으면 `origin="none"`
⑤ gross 0 인 행을 "브로커가 0원이라고 했다"로 읽지 않는다(`origin="net_only"`)
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


def _mark_trading_day(pdb, date_str):
    con = sqlite3.connect(pdb)
    con.execute("INSERT INTO predictions (ts) VALUES (?)", (date_str + " 09:01:00",))
    con.commit(); con.close()


def _row(tdb, date_str):
    con = sqlite3.connect(tdb)
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM daily_broker_pnl WHERE date = ?",
                    (date_str,)).fetchone()
    con.close()
    return r


D = "2026-08-26"


# ── F-8 ① 실측 기입을 덮지 않는다 ───────────────────────────────────────────
def test_eod_snapshot_does_not_overwrite_live(tmp_dbs):
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, D)
    assert du.upsert_broker_net(D, 49_349_062.0, 49_538_950.0, source="live") is True
    # EOD 보정 시도 — 이미 실측이 있으므로 아무것도 하지 않아야 한다.
    wrote = du.upsert_broker_net(D, 1.0, 2.0, source="eod_snapshot",
                                 snapshot_ts="2026-08-26 15:40:22",
                                 only_if_missing=True)
    assert wrote is False, "EOD 스냅샷이 실측 기입을 덮었다"
    r = _row(tdb, D)
    assert r["broker_net_krw"] == pytest.approx(189_888.0)
    assert r["broker_net_source"] == "live"


# ── F-8 ② NULL 인 날은 보정이 채운다 ────────────────────────────────────────
def test_eod_snapshot_fills_when_missing(tmp_dbs):
    """2026-08-26 재현 — FLAT 푸시가 한 번도 안 온 날."""
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, D)
    du.update_daily_broker_pnl_net(D, 232_000.0, 42_098.0, 189_902.0)
    assert _row(tdb, D)["broker_net_krw"] is None      # 결손 상태 재현
    wrote = du.upsert_broker_net(D, 49_349_062.0, 49_538_950.0,
                                 source="stale_snapshot",
                                 snapshot_ts="2026-08-26 12:19:01",
                                 only_if_missing=True)
    assert wrote is True
    r = _row(tdb, D)
    assert r["broker_net_krw"] is not None, \
        "잔고 푸시가 FLAT 으로 한 번도 안 온 날에도 net 축이 비면 안 된다"
    assert r["broker_net_krw"] == pytest.approx(189_888.0)
    # gross 는 보존된다 — 보정이 다른 축을 건드리지 않는다.
    assert r["pnl_krw"] == pytest.approx(232_000.0)


# ── F-8 ③ 폴백 가시화 — 출처·시각이 같은 행에 남는다 ────────────────────────
def test_fallback_source_and_snapshot_ts_recorded(tmp_dbs):
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, D)
    du.upsert_broker_net(D, 49_349_062.0, 49_538_950.0,
                         source="stale_snapshot",
                         snapshot_ts="2026-08-26 12:19:01", only_if_missing=True)
    r = _row(tdb, D)
    assert r["broker_net_source"] == "stale_snapshot"
    assert r["deposit_snapshot_ts"] == "2026-08-26 12:19:01"
    # 기입 시각(updated_at)과 관측 시각(deposit_snapshot_ts)은 다르다 —
    # 그 차이 자체가 판정 재료다(계측 4원칙 ④).
    assert r["updated_at"] != r["deposit_snapshot_ts"]


def test_source_flows_into_recon_and_verdict(tmp_dbs):
    """대사·판정 조회가 출처를 그대로 실어 보낸다 — 로그가 축을 말할 수 있어야 한다."""
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, D)
    du.update_daily_broker_pnl_net(D, 232_000.0, 42_098.0, 189_902.0)
    du.upsert_broker_net(D, 49_349_062.0, 49_538_950.0,
                         source="stale_snapshot",
                         snapshot_ts="2026-08-26 12:19:01", only_if_missing=True)
    rec = du.reconcile_daily_net(D, 232_000.0, 42_098.0, 189_902.0)
    assert rec["status"] == "OK"           # 실측 잔차 14원
    assert rec["broker_net_source"] == "stale_snapshot"
    assert rec["deposit_snapshot_ts"] == "2026-08-26 12:19:01"
    v = du.fetch_daily_net_for_verdict(days=3650)
    assert v[D]["source"] == "broker"
    assert v[D]["broker_net_source"] == "stale_snapshot"


def test_legacy_rows_report_none_source_not_live(tmp_dbs):
    """498차 이전 행은 출처가 **미측정(None)** 이다 — "live 아님"이 아니다."""
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, "2026-08-25")
    con = sqlite3.connect(tdb)
    con.execute("""INSERT INTO daily_broker_pnl
                       (date, pnl_krw, updated_at, deposit_cash_krw,
                        next_day_deposit_cash_krw, broker_net_krw)
                   VALUES ('2026-08-25', 39000.0, 'x', 49350842.0, 49349060.0, -1782.0)""")
    con.commit(); con.close()
    b = du.fetch_broker_net("2026-08-25")
    assert b["net_source"] is None
    assert b["deposit_snapshot_ts"] is None


def test_zero_guard_still_holds(tmp_dbs):
    """0/결측 가드는 그대로 — 빈 TR 응답이 실측을 0으로 덮지 않는다."""
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, D)
    assert du.upsert_broker_net(D, 0.0, 0.0, source="live") is False
    assert _row(tdb, D) is None


# ── F-9 ④⑤ gross 대사 자기참조 분리 ────────────────────────────────────────
def test_gross_origin_none_before_any_write(tmp_dbs):
    tdb, pdb = tmp_dbs
    assert du.fetch_broker_gross_origin(D)["origin"] == "none"


def test_eod_write_reports_created_flag(tmp_dbs):
    """🔴 도달 불가 분기의 존재 증명 — 행이 없으면 만들었다고 **알린다**."""
    tdb, pdb = tmp_dbs
    created = du.update_daily_broker_pnl_net(D, 232_000.0, 42_098.0, 189_902.0)
    assert created is True, "행 생성 사실을 호출자가 알 수 없으면 자기참조 대사가 된다"
    # 같은 날 두 번째 호출은 UPDATE 라 created=False
    assert du.update_daily_broker_pnl_net(D, 232_000.0, 42_098.0, 189_902.0) is False


def test_self_reference_is_broken(tmp_dbs):
    """쓰기 **전** 상태를 읽으면 「브로커 gross 미수신」이 실제로 나타난다.

    종전 순서(쓰고 나서 읽기)로는 이 단언이 성립할 수 없었다.
    """
    tdb, pdb = tmp_dbs
    origin_before = du.fetch_broker_gross_origin(D)
    du.update_daily_broker_pnl_net(D, 232_000.0, 42_098.0, 189_902.0)
    origin_after = du.fetch_broker_gross_origin(D)
    assert origin_before["origin"] == "none"
    assert origin_after["origin"] == "broker", \
        "쓰기 후에는 엔진 gross 가 '브로커 gross' 처럼 보인다 — 이것이 자기참조다"


def test_broker_origin_when_tr_received(tmp_dbs):
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, D)
    du.upsert_daily_broker_pnl(D, 232_000.0)
    o = du.fetch_broker_gross_origin(D)
    assert o["origin"] == "broker"
    assert o["gross_krw"] == pytest.approx(232_000.0)
    assert o["updated_at"]          # 로그에 박을 TR 수신 시각


def test_net_only_row_is_not_broker_gross(tmp_dbs):
    """net 축만 선기입된 행의 gross 0 을 브로커 실측으로 읽지 않는다(계측 4원칙 ②)."""
    tdb, pdb = tmp_dbs
    _mark_trading_day(pdb, D)
    du.upsert_broker_net(D, 49_349_062.0, 49_538_950.0, source="live")
    assert _row(tdb, D)["pnl_krw"] == 0.0
    assert du.fetch_broker_gross_origin(D)["origin"] == "net_only"


def test_schema_migration_adds_text_columns(tmp_path, monkeypatch):
    """구버전 테이블도 init 에서 출처·스냅샷시각 컬럼을 따라잡는다."""
    tdb = str(tmp_path / "trades_legacy.db")
    con = sqlite3.connect(tdb)
    con.execute("""CREATE TABLE daily_broker_pnl (
        date TEXT PRIMARY KEY, pnl_krw REAL NOT NULL, updated_at TEXT NOT NULL)""")
    con.commit(); con.close()
    monkeypatch.setattr(du, "TRADES_DB", tdb)
    du.init_daily_broker_pnl_db()
    con = sqlite3.connect(tdb)
    cols = {r[1] for r in con.execute("PRAGMA table_info(daily_broker_pnl)")}
    con.close()
    assert {"broker_net_source", "deposit_snapshot_ts",
            "broker_net_krw", "deposit_cash_krw"} <= cols
