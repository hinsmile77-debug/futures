# -*- coding: utf-8 -*-
"""[MW0601 705차 후속 / 장후 자동조치] 2026-10-22 장후 리포트 F-27 · G-1 · G-2.

F-27 (전제 반박 → 대사 쪽 수정)
  리포트는 10:13:05 포지션의 최종 레그 `TRAIL_AFTER_TP1` 을 오분류로 보고 신동 부분청산
  사유를 TP1 비보호로 돌리자고 했다. 그러나 신동은 1차 목표 익절(`신동1차`) 뒤 손절을
  본전으로 올린다(`strategy/shindong/live_legs.py:after_leg1`) — 그 뒤 스톱은 라벨 정의상
  TP1 보호 트레일이 맞다(실측 +7.31pt · 10-21 +1.12pt). 라벨을 `INITIAL_STOP` 으로 바꾸면
  이익 청산이 손절로 세여 490차가 막으려던 오염의 **거울상**이 된다.
  틀린 것은 자기대사(`recon_exit_stage_labels`)의 대응 축이 엔진 TP만 본 것이다.

G-1  꺼진 차단 게이트가 화이트리스트에만 없고 근거는 DECISION_LOG·커밋에 있으면
     「근거 미기록(P0 후보)」이 아니라 「목록 등재만 누락」으로 표기한다.
G-2  `retrain_intraday_20260624_102256.log` 처럼 다른 날짜를 명시한 파일이 짧은 토큰
     (`1022`)으로 오늘 파일에 걸리는 것을 가른다.
"""
from __future__ import annotations

import os
import runpy
import sqlite3
import sys
from datetime import date

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import utils.db_utils as dbu                     # noqa: E402

COLLECTOR = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                         "scripts", "collect_evidence.py")

# ── 2026-10-22 `trades` 실측 (entry_ts, exit_stage, exit_reason, qty, net) ──
LEGS_1022 = [
    ("2026-10-22 10:13:05", "OTHER",           "신동1차",      1, 379_824),
    ("2026-10-22 10:13:05", "TRAIL_AFTER_TP1", "하드스톱(틱)", 1, 363_824),
    ("2026-10-22 12:34:05", "OTHER",           "신동1차",      1, 180_000),
    ("2026-10-22 12:34:05", "OTHER",           "신동최종",     1, 210_000),
    ("2026-10-22 13:08:05", "INITIAL_STOP",    "하드스톱(틱)", 2, -170_000),
]


def _db(tmp_path, legs):
    db = str(tmp_path / "trades.db")
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE trades (
        entry_ts TEXT, exit_price REAL, exit_reason TEXT, exit_stage TEXT,
        quantity INTEGER, pnl_krw REAL, net_pnl_krw REAL)""")
    con.executemany("INSERT INTO trades VALUES (?, 1000.0, ?, ?, ?, ?, ?)",
                    [(ts, reason, stage, qty, net, net) for ts, stage, reason, qty, net in legs])
    con.commit()
    con.close()
    return db


def test_f27_shindong_target1_counts_as_external_correspondence(tmp_path, monkeypatch):
    """10-22 10:13:05 는 미대응이 아니라 「신동 1차익절 대응」이다."""
    monkeypatch.setattr(dbu, "TRADES_DB", _db(tmp_path, LEGS_1022))
    r = dbu.recon_exit_stage_labels("2026-10-22")
    assert r["trail_positions"] == 1
    assert r["external_target"] == 1
    assert r["suspect"] == 0
    assert r["corresponded"] == 0       # 엔진 TP 와 섞지 않는다 — 출처를 가른다


def test_f27_no_target1_still_suspect(tmp_path, monkeypatch):
    """신동 1차익절 없이 TRAIL 이 붙으면 여전히 미대응이다(가드가 무뎌지지 않았다)."""
    legs = [("2026-10-22 10:00:00", "OTHER", "피터2미러(청산)", 1, 10_000),
            ("2026-10-22 10:00:00", "TRAIL_AFTER_TP1", "하드스톱(틱)", 1, -50_000)]
    monkeypatch.setattr(dbu, "TRADES_DB", _db(tmp_path, legs))
    r = dbu.recon_exit_stage_labels("2026-10-22")
    assert r["suspect"] == 1
    assert r["external_target"] == 0


def test_f27_trail_after_shindong_target1_keeps_protect_label():
    """신동1차 뒤 하드스톱은 TRAIL_AFTER_TP1 그대로 — 외부 익절 라벨은 비보호 목록에 넣지 않는다."""
    from strategy.position.position_tracker import PositionTracker as PT
    assert PT.classify_exit_stage("하드스톱(틱)", True) == "TRAIL_AFTER_TP1"
    for s in ("OTHER", "EXT_TARGET1", "EXT_TARGET2", "EXT_INSTRUCTED"):
        assert s not in PT._TP1_NON_PROTECT_STAGES


def test_705c_external_principal_reasons_labelled():
    """[705차 후속5] 신동·피터2 자체 청산 사유가 OTHER 로 새지 않는다."""
    from strategy.position.position_tracker import PositionTracker as PT
    C = PT.classify_exit_stage
    assert C("신동1차", False) == "EXT_TARGET1"
    assert C("신동1차·최종", False) == "EXT_TARGET1"
    assert C("신동최종", True) == "EXT_TARGET2"
    assert C("피터2미러(청산)", False) == "EXT_INSTRUCTED"
    assert C("피터2미러(체결)", False) == "EXT_INSTRUCTED"
    assert C("피터2미러(손절)", False) == "INITIAL_STOP"      # 손절은 스톱 계열
    assert C("신동시간청산", False) == "TIME_EXIT"            # 기존 분기 우선 — 무변경
    assert C("가상:신동1차", False) == "EXT_TARGET1"


def test_705c_shindong_partial_then_stop_still_trail():
    """라벨 축 회귀 — 신동1차(1계약) 뒤 남은 계약 하드스톱은 TRAIL_AFTER_TP1 (10-22 10:13:05 재현)."""
    from strategy.position.position_tracker import PositionTracker as PT
    pt = PT.__new__(PT)
    pt.tp1_protect_armed = False
    pt.partial_1_done = pt.partial_2_done = pt.partial_3_done = False
    pt.get_stage_targets = lambda: (1, 0, 0)
    pt.get_closed_quantity = lambda: 1
    pt._sync_partial_progress("신동1차")
    assert pt.tp1_protect_armed is True
    assert pt.classify_exit_stage("하드스톱(틱)", pt._tp1_armed()) == "TRAIL_AFTER_TP1"


def test_f27_main_log_shows_external_bucket_and_stays_shadow():
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    start = src.index("recon_exit_stage_labels as _g5_recon")
    block = src[start:src.index("except Exception as _g5_e", start)]
    assert "external_target" in block
    for forbidden in ("send_market_order", "block_new_entries", "cancel_order",
                      "circuit_breaker", "UPDATE ", "INSERT "):
        assert forbidden not in block


@pytest.fixture(scope="module")
def ce():
    return runpy.run_path(COLLECTOR, run_name="collect_evidence_under_test")


def test_g2_foreign_date_detected(ce):
    toks = ce["date_tokens"](date(2026, 10, 22))
    f = ce["foreign_date_in_name"]
    assert f("retrain_intraday_20260624_102256.log", toks) == "20260624"
    assert f("retrain_intraday_20261015_102200.log", toks) == "20261015"
    assert f("retrain_intraday_20261022_102200.log", toks) is None   # 오늘 파일
    assert f("20261022_SYSTEM.log", toks) is None
    assert f("crash_1022.log", toks) is None                         # 날짜 명시 없음 — 판단 불가, 그대로 둔다
    assert f("x_20261399_1022.log", toks) is None                    # 무효 날짜는 날짜가 아니다


def test_g2_discover_marks_foreign(ce, tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "retrain_intraday_20260624_102256.log").write_text("x")
    (logs / "20261022_SYSTEM.log").write_text("y")
    cfg = {"scan_dirs": ["logs"], "scan_depth": 2, "exclude_patterns": []}
    found = {e["name"]: e for e in ce["discover_files"](str(tmp_path), cfg, date(2026, 10, 22))}
    assert found["retrain_intraday_20260624_102256.log"]["foreign_date"] == "20260624"
    assert found["20261022_SYSTEM.log"]["foreign_date"] is None


def test_g1_rationale_trace(ce, tmp_path):
    dm = tmp_path / "dev_memory"
    dm.mkdir()
    (dm / "DECISION_LOG.md").write_text("703차: FOO_BLOCK_ENABLED = False 사유 …", encoding="utf-8")
    ce["_RATIONALE_CACHE"].clear()
    try:
        assert "DECISION_LOG" in ce["rationale_trace"](str(tmp_path), "FOO_BLOCK_ENABLED")
        assert ce["rationale_trace"](str(tmp_path), "BAR_BLOCK_ENABLED") == []
    finally:
        ce["_RATIONALE_CACHE"].clear()
