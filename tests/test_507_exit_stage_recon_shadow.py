# -*- coding: utf-8 -*-
"""[MW0601 507차 후속 / G-5] 청산 사유 라벨의 자기대사 — 섀도, 차단 없음.

2026-08-31 이상점 1-19: `exit_stage='TRAIL_AFTER_TP1'`(= TP1 뒤 트레일 = 이익 청산)
라벨 13레그 중 **5포지션이 TP1이 난 적 없는 포지션**이었다. 합계 −6,977,391원이
「진짜 손절」이 아니라 「이익 청산」으로 분류돼 손절률·손절폭 초과율·CB② 후보
산정의 분모와 분자가 오염됐다.

🔴 **여기서 라벨을 고치지 않는다.** 그 수정(F-10)은 `is_tp1_hit` 재발동 가드와
   같은 플래그를 쓰므로 청산 트리거 경로 변경이고, 섀도 10거래일 관찰이 선행조건이다
   (P5-06). 이 계측이 그 관찰을 만든다.

⚠ 단일계약 1레그 포지션은 의심에서 뺀다 — `arm_tp1_single_contract*()` 가 사유를
  명시하고 세우는 설계된 경로다. 안 빼면 08-31 실측이 5건이 아니라 8건으로 부푼다.
"""
from __future__ import annotations

import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import utils.db_utils as dbu                     # noqa: E402

# ── 2026-08-31 `trades` 실측 레그 (entry_ts, exit_stage, exit_reason, qty, net) ──
# 값은 DB 원문 그대로다. 이 표가 이 사고의 지문이다.
LEGS_0831 = [
    ("2026-08-31 00:42:24", "TRAIL_AFTER_TP1", "하드스톱(틱)", 4, -5_461_928),
    ("2026-08-31 09:28:47", "INITIAL_STOP",    "하드스톱(틱)", 1,   -186_273),
    ("2026-08-31 09:35:04", "TP1",             "TP1 부분청산 33%", 1, 100_019),
    ("2026-08-31 09:35:04", "TRAIL_AFTER_TP1", "하드스톱(틱)", 2,    -25_963),
    ("2026-08-31 09:44:09", "TP1",             "TP1 부분청산 33%", 1, 116_374),
    ("2026-08-31 09:44:09", "TRAIL_AFTER_TP1", "하드스톱",     2,    204_748),
    ("2026-08-31 09:50:17", "TRAIL_AFTER_TP1", "하드스톱(틱)", 3,   -509_754),
    ("2026-08-31 09:56:09", "RECOVERY", "복구청산(pending_miss)", 1,  71_740),
    ("2026-08-31 10:30:25", "RECOVERY", "복구청산(pending_miss)", 1,  -1_220),
    ("2026-08-31 10:46:41", "TRAIL_AFTER_TP1", "하드스톱(틱)", 1,       -210),
    ("2026-08-31 10:50:09", "TRAIL_AFTER_TP1", "하드스톱(틱)", 2,   -397_416),
    ("2026-08-31 11:03:28", "TRAIL_AFTER_TP1", "하드스톱(틱)", 2,   -392_469),
    ("2026-08-31 11:22:23", "TP1",             "TP1 부분청산 33%", 1,  69_094),
    ("2026-08-31 11:22:23", "TRAIL_AFTER_TP1", "하드스톱(틱)", 2,    -19_812),
    ("2026-08-31 11:28:25", "TRAIL_AFTER_TP1", "하드스톱(틱)", 1,       -253),
    ("2026-08-31 11:35:09", "INITIAL_STOP",    "하드스톱(틱)", 1,   -138_222),
    ("2026-08-31 12:16:32", "TP2",             "TP2(전량)",    1,     93_658),
    ("2026-08-31 12:27:56", "TRAIL_AFTER_TP1", "하드스톱(틱)", 1,      7_683),
    ("2026-08-31 14:31:19", "TP1",             "TP1 부분청산 33%", 1,  49_200),
    ("2026-08-31 14:31:19", "TRAIL_AFTER_TP1", "하드스톱",     2,    144_399),
    ("2026-08-31 14:33:38", "TP1",             "TP1 부분청산 33%", 1,  67_887),
    ("2026-08-31 14:33:38", "TP2",             "TP2 부분청산 33%", 1, 104_887),
    ("2026-08-31 14:33:38", "TRAIL_AFTER_TP1", "하드스톱(틱)", 1,     31_887),
    ("2026-08-31 14:50:56", "RECOVERY", "복구청산(pending_miss)", 2,   2_451),
    ("2026-08-31 14:50:56", "RECOVERY", "복구청산(pending_miss)", 1,   9_225),
    ("2026-08-31 14:56:44", "INITIAL_STOP",    "하드스톱(틱)", 1,   -113_426),
    ("2026-08-31 15:03:11", "TRAIL_AFTER_TP1", "하드스톱(틱)", 2,   -215_824),
]

# 리포트 §4가 지목한 5포지션 — 이 합계가 재현되어야 한다.
SUSPECT_ENTRIES = ["2026-08-31 00:42:24", "2026-08-31 09:50:17",
                   "2026-08-31 10:50:09", "2026-08-31 11:03:28",
                   "2026-08-31 15:03:11"]
SUSPECT_NET = -6_977_391


@pytest.fixture()
def fake_trades(tmp_path, monkeypatch):
    db = str(tmp_path / "trades.db")
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE trades (
        entry_ts TEXT, exit_price REAL, exit_reason TEXT, exit_stage TEXT,
        quantity INTEGER, pnl_krw REAL, net_pnl_krw REAL)""")
    con.executemany(
        "INSERT INTO trades VALUES (?, 1000.0, ?, ?, ?, ?, ?)",
        [(ts, reason, stage, qty, net, net)
         for ts, stage, reason, qty, net in LEGS_0831])
    con.commit()
    con.close()
    monkeypatch.setattr(dbu, "TRADES_DB", db)
    return db


def test_a_reproduces_0831_suspect_set(fake_trades):
    """ⓐ 08-31 실측이 그대로 재현된다 — 미대응 5포지션 · −6,977,391원."""
    r = dbu.recon_exit_stage_labels("2026-08-31")
    assert r["suspect"] == 5
    assert r["suspect_entries"] == SUSPECT_ENTRIES
    assert r["suspect_net_krw"] == pytest.approx(SUSPECT_NET)


def test_b_trail_totals_match_report(fake_trades):
    """ⓑ TRAIL_AFTER_TP1 13레그 / 대응 5 + 단일계약 3 = 8 / 미대응 5."""
    r = dbu.recon_exit_stage_labels("2026-08-31")
    assert r["trail_legs"] == 13
    assert r["trail_positions"] == 13 - 0   # 포지션마다 트레일 레그는 1건씩이다
    assert r["corresponded"] + r["single_armed"] == 8
    assert r["corresponded"] == 5
    assert r["single_armed"] == 3
    assert r["suspect"] == 5


def test_c_single_contract_arming_is_not_suspect(fake_trades):
    """ⓒ 단일계약 1레그(10:46:41 · 11:28:25 · 12:27:56)는 의심이 아니다.

    `arm_tp1_single_contract*()` 가 세우는 설계된 경로다. 이걸 의심으로 세면
    08-31 실측이 8건으로 부풀어 F-10 판정 표본이 흐려진다.
    """
    r = dbu.recon_exit_stage_labels("2026-08-31")
    for ts in ("2026-08-31 10:46:41", "2026-08-31 11:28:25", "2026-08-31 12:27:56"):
        assert ts not in r["suspect_entries"]


def test_d_position_with_real_tp_leg_is_corresponded(fake_trades):
    """ⓓ TP 레그가 실제로 있는 포지션은 대응으로 센다(오탐 방지)."""
    r = dbu.recon_exit_stage_labels("2026-08-31")
    for ts in ("2026-08-31 09:35:04", "2026-08-31 14:33:38"):
        assert ts not in r["suspect_entries"]


def test_e_null_exit_stage_is_unmeasured_not_clean(tmp_path, monkeypatch):
    """ⓔ `exit_stage` 가 전부 NULL 인 포지션은 **미측정**이다 — 0 이 아니다.

    490차 이전 행이 그렇다. 「판정했더니 문제 없음」과 구분해야 한다(계측 4원칙 ②).
    """
    db = str(tmp_path / "t.db")
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE trades (
        entry_ts TEXT, exit_price REAL, exit_reason TEXT, exit_stage TEXT,
        quantity INTEGER, pnl_krw REAL, net_pnl_krw REAL)""")
    con.execute("INSERT INTO trades VALUES ('2026-06-01 09:10:00', 1000.0, "
                "'하드스톱(틱)', NULL, 2, -100.0, -100.0)")
    con.commit()
    con.close()
    monkeypatch.setattr(dbu, "TRADES_DB", db)
    r = dbu.recon_exit_stage_labels("2026-06-01")
    assert r["unmeasured"] == 1
    assert r["suspect"] == 0
    assert r["trail_positions"] == 0


def test_f_quiet_day_produces_no_suspects(tmp_path, monkeypatch):
    """ⓕ 라벨이 맞는 날에는 아무것도 보고하지 않는다(오탐 0)."""
    db = str(tmp_path / "t.db")
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE trades (
        entry_ts TEXT, exit_price REAL, exit_reason TEXT, exit_stage TEXT,
        quantity INTEGER, pnl_krw REAL, net_pnl_krw REAL)""")
    con.executemany("INSERT INTO trades VALUES (?, 1000.0, ?, ?, ?, ?, ?)", [
        ("2026-06-02 09:10:00", "TP1 부분청산 33%", "TP1", 1, 50_000, 50_000),
        ("2026-06-02 09:10:00", "하드스톱(틱)", "TRAIL_AFTER_TP1", 2, -10_000, -10_000),
        ("2026-06-02 10:10:00", "하드스톱(틱)", "INITIAL_STOP", 3, -90_000, -90_000),
    ])
    con.commit()
    con.close()
    monkeypatch.setattr(dbu, "TRADES_DB", db)
    r = dbu.recon_exit_stage_labels("2026-06-02")
    assert r["suspect"] == 0
    assert r["corresponded"] == 1
    assert r["unmeasured"] == 0


def test_g_is_shadow_only_no_blocking(fake_trades):
    """ⓖ **라이브 반영 0** — 이 함수는 읽기만 하고 아무것도 쓰지 않는다.

    G-5 는 섀도다. 라벨(`exit_stage`)도 손익도 1원도 바뀌지 않는다.
    """
    before = sqlite3.connect(fake_trades).execute(
        "SELECT exit_stage, net_pnl_krw FROM trades ORDER BY rowid").fetchall()
    dbu.recon_exit_stage_labels("2026-08-31")
    after = sqlite3.connect(fake_trades).execute(
        "SELECT exit_stage, net_pnl_krw FROM trades ORDER BY rowid").fetchall()
    assert before == after, "섀도 계측이 DB 를 건드렸다"


def test_h_main_logs_shadow_without_blocking():
    """ⓗ `main.py` 배선이 **보고만** 한다 — 차단·주문 호출이 붙지 않았는지 본다."""
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    start = src.index("recon_exit_stage_labels as _g5_recon")
    end = src.index("except Exception as _g5_e", start)
    block = src[start:end]
    assert "_g5_recon(today_str)" in block
    # 섀도 블록이 하는 일은 읽기와 로그뿐이어야 한다.
    for forbidden in ("send_market_order", "block_new_entries", "cancel_order",
                      "circuit_breaker", "UPDATE ", "INSERT "):
        assert forbidden not in block, "섀도 블록에 %s 가 섞였다" % forbidden
    assert "log_manager.system" in block
