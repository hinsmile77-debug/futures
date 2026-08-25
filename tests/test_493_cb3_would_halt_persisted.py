# -*- coding: utf-8 -*-
"""[MW0601 493차 후속5 / F-AB] CB③ 조건성립 계측을 DB에 남긴다.

왜 필요한가 (2026-08-25 실측)
-----------------------------
490차 F-G 가 「CB③ HALT 조건이 실제로 성립한 분」을 세기 시작했지만 **로그로만**
내보냈다. 그 로그 줄이 F-Y 서식 결함으로 이틀 연속 죽으면서 값이 통째로 사라졌고,
오늘 값(69분)은 점검 세션이 `[DBG-CB]` 370행을 손으로 재집계해 복원해야 했다.

🔴 **로그는 사람이 읽고 DB는 시계열이 읽는다.** 전환기준 ⑥(CB③ 기준 호라이즌
교체)을 논의하려면 "차단을 켰다면 무엇을 잃었겠는가"의 시계열이 필요하고,
그것은 로그 파싱으로 매번 복원할 것이 아니다.

고정하는 불변식:
① `scaler_daily` 에 3컬럼이 있다.
② `health` 가 없으면 **NULL(미측정)** — 0으로 위장하지 않는다.
③ `health` 가 있으면 **0도 기록한다** — 「조건이 한 번도 성립하지 않았다」는 정보다.
④ ②와 ③의 구분이 실제로 유지된다(같은 컬럼에서 NULL ≠ 0).
⑤ F-Y 가 살린 `[CB③계측]` 로그 줄은 **그대로 유지**한다(둘 다 있어야 한다).
"""
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import model.scaler_monitor_db as M  # noqa: E402

_COLS = ("cb3_would_halt_minutes", "cb3_would_halt_entries", "cb3_would_halt_pnl_krw")


@pytest.fixture()
def db(tmp_path, monkeypatch):
    """라이브 DB를 건드리지 않는다 — 테스트가 운영 시계열에 행을 남기면 안 된다."""
    path = str(tmp_path / "scaler_monitor.db")
    monkeypatch.setattr(M, "SCALER_MONITOR_DB", path)
    M.init_db()
    return path


def _cols(path):
    con = sqlite3.connect(path)
    try:
        return {r[1] for r in con.execute("PRAGMA table_info(scaler_daily)")}
    finally:
        con.close()


def _row(path, date_str):
    con = sqlite3.connect(path)
    try:
        return con.execute(
            "SELECT %s FROM scaler_daily WHERE date = ?" % ", ".join(_COLS),
            (date_str,)).fetchone()
    finally:
        con.close()


# ── ① 스키마 ────────────────────────────────────────────────────────────────
def test_schema_has_three_columns(db):
    missing = [c for c in _COLS if c not in _cols(db)]
    assert not missing, "scaler_daily에 %s 컬럼이 없다" % missing


def test_columns_have_no_default(db):
    """`ALTER TABLE ... DEFAULT 0` 은 **기존 행에도 0을 채워** 미측정을 위장한다.

    `cb3_ready_minutes` 가 같은 이유로 DEFAULT 없이 추가됐다(482차 G-1).
    """
    for name, typedef in M._HEALTH_COLS:
        if name in _COLS:
            assert "DEFAULT" not in typedef.upper(), (
                "%s 에 DEFAULT 가 붙었다 — 기존 행의 미측정이 0으로 바뀐다" % name)


# ── ②③④ 미측정 vs 0 ────────────────────────────────────────────────────────
def test_no_health_leaves_null(db):
    """`health=None` → NULL(미측정). 0으로 채우면 「조건 0분」으로 읽힌다."""
    M.insert_daily("2026-01-02", {}, health=None)
    assert _row(db, "2026-01-02") == (None, None, None)


def test_health_with_zero_records_zero(db):
    """0은 **기록한다** — 「사건이 없었다」와 「안 쟀다」는 다르다."""
    M.insert_daily("2026-01-03", {}, health={
        "pipeline_minutes": 370, "cb3_ready_minutes": 110,
        "cb3_would_halt_minutes": 0, "cb3_would_halt_entries": 0,
        "cb3_would_halt_pnl_krw": 0.0,
    })
    assert _row(db, "2026-01-03") == (0, 0, 0.0)


def test_null_and_zero_are_distinguishable(db):
    """④ 같은 컬럼에서 NULL 과 0 이 실제로 구분되는가 — ②③의 결합 확인."""
    M.insert_daily("2026-01-04", {}, health=None)
    M.insert_daily("2026-01-05", {}, health={"cb3_would_halt_minutes": 0})
    con = sqlite3.connect(db)
    try:
        n_null = con.execute(
            "SELECT COUNT(*) FROM scaler_daily WHERE cb3_would_halt_minutes IS NULL"
        ).fetchone()[0]
        n_zero = con.execute(
            "SELECT COUNT(*) FROM scaler_daily WHERE cb3_would_halt_minutes = 0"
        ).fetchone()[0]
    finally:
        con.close()
    assert n_null == 1 and n_zero == 1


def test_real_values_round_trip(db):
    """2026-08-25 실측(69분 / 0건 / 0원)이 그대로 들어가고 나온다."""
    M.insert_daily("2026-08-25", {}, health={
        "pipeline_minutes": 370, "cb3_ready_minutes": 110,
        "cb3_would_halt_minutes": 69, "cb3_would_halt_entries": 0,
        "cb3_would_halt_pnl_krw": 0.0,
    })
    assert _row(db, "2026-08-25") == (69, 0, 0.0)


def test_negative_pnl_preserved(db):
    """손익은 음수가 정상이다 — int 로 잘리거나 부호가 죽으면 안 된다."""
    M.insert_daily("2026-01-06", {}, health={
        "cb3_would_halt_minutes": 12, "cb3_would_halt_entries": 3,
        "cb3_would_halt_pnl_krw": -1234567.89,
    })
    row = _row(db, "2026-01-06")
    assert row[1] == 3
    assert row[2] == pytest.approx(-1234567.89)


# ── ⑤ 로그도 유지 ───────────────────────────────────────────────────────────
def test_log_line_is_kept_alongside_db():
    """DB 저장을 붙였다고 로그를 없애지 않았는가.

    F-AB 변경 ④ — 로그는 사람이 읽고 DB는 시계열이 읽는다.
    """
    import io
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = io.open(os.path.join(root, "main.py"), encoding="utf-8").read()
    assert "[CB③계측] 조건성립" in src, "F-AB가 F-Y의 로그 줄을 지웠다"
