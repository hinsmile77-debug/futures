# -*- coding: utf-8 -*-
"""456차 Wave 1 — F1 승패 집계 단위 + F2 SHS CORE 통과율 회귀 테스트.

배경: `docs/정기점검/매일점검/MW0601-20260810-점검리포트.md` §2-1·§3-2,
      `docs/정기점검/매일점검/0810_Fix_고도화_통합구현계획_MW0601.md` Wave 1.
"""
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from strategy.position.position_tracker import PositionTracker   # noqa: E402
from safety.system_health import SystemHealthScore               # noqa: E402


# ── F1: 승패 집계 단위 (레그 → 포지션) ───────────────────────────────────────

@pytest.fixture
def pt(tmp_path, monkeypatch):
    """상태파일이 실제 data/를 건드리지 않도록 격리한 트래커."""
    import strategy.position.position_tracker as m
    monkeypatch.setattr(m, "_STATE_FILE", str(tmp_path / "pos.json"))
    return PositionTracker(pt_value=50_000)


def _open(pt, direction="SHORT", price=980.16, qty=3):
    pt.open_position(direction=direction, price=price, quantity=qty, atr=3.09)


def test_multileg_net_loss_counts_as_loss(pt):
    """2026-08-10 09:58 실측 재현 — 손실을 부분청산으로 털고 잔여가 소폭 이익.

    3계약 진입 → 2계약 -3.04pt 청산 → 잔여 1계약 +0.70pt.
    계약가중 합 = -3.04*2 + 0.70*1 = -5.38pt → **패**.
    구 코드는 최종 레그(+0.70)만 보고 승으로 셌다(순 -273,410원인데 승).
    """
    _open(pt, qty=3)
    pt.apply_exit_fill(exit_price=980.16 + 3.04, quantity=2, reason="손절1차")
    pt.apply_exit_fill(exit_price=980.16 - 0.70, quantity=1, reason="하드스톱")
    s = pt.daily_stats()
    assert s["trades"] == 1, "부분청산은 별도 거래로 세지 않는다"
    assert s["wins"] == 0 and s["losses"] == 1


def test_multileg_net_win_counts_as_win(pt):
    """10:19 실측 재현 — TP1 부분익절 후 잔여도 소폭 이익 → 승."""
    _open(pt, qty=3, price=983.27)
    pt.apply_exit_fill(exit_price=983.27 - 1.39, quantity=1, reason="TP1")
    pt.apply_exit_fill(exit_price=983.27 - 0.07, quantity=2, reason="하드스톱")
    s = pt.daily_stats()
    assert (s["trades"], s["wins"], s["losses"]) == (1, 1, 0)


def test_leg_weighting_matters(pt):
    """계약수 가중이 없으면 부호가 뒤집히는 경우.

    -1.0pt x 3계약 = -3.0  /  +2.0pt x 1계약 = +2.0  → 합 -1.0 (패).
    비가중이면 -1.0 + 2.0 = +1.0 으로 승이 된다.
    """
    _open(pt, direction="LONG", price=1000.0, qty=4)
    pt.apply_exit_fill(exit_price=999.0, quantity=3, reason="부분손절")
    pt.apply_exit_fill(exit_price=1002.0, quantity=1, reason="청산")
    s = pt.daily_stats()
    assert (s["wins"], s["losses"]) == (0, 1)


def test_single_leg_behavior_unchanged(pt):
    """단일 레그 포지션은 종전과 동일해야 한다(회귀)."""
    _open(pt, qty=1, price=980.0)
    pt.apply_exit_fill(exit_price=979.0, quantity=1, reason="TP")   # SHORT 이익
    s = pt.daily_stats()
    assert (s["trades"], s["wins"]) == (1, 1)


def test_accumulator_resets_between_positions(pt):
    """이전 포지션의 실현손익이 다음 포지션 판정에 새지 않는가."""
    _open(pt, qty=1, price=980.0)
    pt.apply_exit_fill(exit_price=990.0, quantity=1, reason="큰손실")   # SHORT -10pt
    assert pt._pos_realized_pnl_pts == 0.0, "청산 후 누적기가 초기화돼야 한다"
    _open(pt, qty=1, price=980.0)
    pt.apply_exit_fill(exit_price=979.0, quantity=1, reason="소폭이익")
    s = pt.daily_stats()
    assert (s["trades"], s["wins"], s["losses"]) == (2, 1, 1)


def test_partial_close_path_also_accumulates(pt):
    """partial_close() 경로(apply_exit_fill과 별개)도 누적하는가."""
    _open(pt, qty=3, price=980.0)
    pt.partial_close(exit_price=985.0, qty=2, reason="부분손절")   # SHORT -5pt x2
    assert pt._pos_realized_pnl_pts == pytest.approx(-10.0)
    pt.apply_exit_fill(exit_price=979.0, quantity=1, reason="청산")  # +1pt
    s = pt.daily_stats()
    assert (s["wins"], s["losses"]) == (0, 1)


def test_accumulator_survives_restart(pt, tmp_path, monkeypatch):
    """장중 재기동 시 부분청산 이력이 유실되면 구 버그가 재발한다."""
    import strategy.position.position_tracker as m
    _open(pt, qty=3, price=980.0)
    pt.partial_close(exit_price=985.0, qty=2, reason="부분손절")   # -10pt 누적

    revived = PositionTracker(pt_value=50_000)
    assert revived.load_state() is True
    assert revived._pos_realized_pnl_pts == pytest.approx(-10.0), \
        "재기동 후 누적 실현손익이 복원돼야 한다"


def test_restore_daily_stats_groups_by_position():
    """trades.db 행(레그)을 포지션으로 묶는가 — 구 코드는 13레그를 13건으로 셌다."""
    rows = [
        {"entry_ts": "A", "pnl_pts": -3.04, "quantity": 2, "entry_price": 980.0},
        {"entry_ts": "A", "pnl_pts": +0.70, "quantity": 1, "entry_price": 980.0},
        {"entry_ts": "B", "pnl_pts": +1.39, "quantity": 1, "entry_price": 983.0},
        {"entry_ts": "B", "pnl_pts": +0.07, "quantity": 2, "entry_price": 983.0},
        {"entry_ts": "C", "pnl_pts": +4.58, "quantity": 1, "entry_price": 985.0},
    ]
    pt = PositionTracker(pt_value=50_000)
    pt.restore_daily_stats([_Row(r) for r in rows])
    s = pt.daily_stats()
    assert s["trades"] == 3, "5레그 → 3포지션"
    assert (s["wins"], s["losses"]) == (2, 1)   # A는 계약가중 -5.38 → 패


def test_restore_daily_stats_legacy_rows_without_entry_ts():
    """entry_ts가 없는 구버전 행은 행=포지션으로 종전 동작 유지."""
    rows = [
        {"pnl_pts": +1.0, "quantity": 1, "entry_price": 980.0},
        {"pnl_pts": -1.0, "quantity": 1, "entry_price": 980.0},
    ]
    pt = PositionTracker(pt_value=50_000)
    pt.restore_daily_stats([_Row(r) for r in rows])
    s = pt.daily_stats()
    assert (s["trades"], s["wins"], s["losses"]) == (2, 1, 1)


class _Row(dict):
    """sqlite3.Row 흉내 — keys() 와 [] 접근."""
    def keys(self):          # noqa: D102
        return list(super().keys())


# ── F1: 대시보드 추이 쿼리도 같은 단위여야 한다 ──────────────────────────────

def test_trend_sql_counts_positions_not_legs(tmp_path, monkeypatch):
    """fetch_trend_* 가 레그가 아니라 포지션을 세는가.

    PositionTracker 쪽만 고치면 "오늘 마감"과 "추이 차트의 오늘"이 어긋난다.
    """
    import sqlite3
    import utils.db_utils as U

    db = tmp_path / "trades.db"
    con = sqlite3.connect(str(db))
    con.execute("""create table trades(
        entry_ts text, exit_ts text, quantity int, pnl_pts real, pnl_krw real,
        net_pnl_krw real, forward_pnl_pts real, forward_pnl_krw real,
        forward_net_pnl_krw real, entry_source text)""")
    # fetch_trend_daily 는 정확도 병합을 위해 daily_stats 도 읽는다
    con.execute("""create table daily_stats(
        date text primary key, sgd_accuracy real, verified_count int)""")
    rows = [
        # A: 3계약 → -3.04×2 + 0.70×1 = -5.38pt → 패 (구 코드는 2건·1승1패로 셌다)
        ("2026-08-10 09:58:00", "2026-08-10 10:01:29", 2, -3.04, -306940),
        ("2026-08-10 09:58:00", "2026-08-10 10:06:54", 1, +0.70, +33530),
        # B: 단일 레그 이익
        ("2026-08-10 10:28:00", "2026-08-10 10:30:59", 1, +4.58, +227523),
    ]
    for ets, xts, q, pts, krw in rows:
        con.execute(
            "insert into trades(entry_ts,exit_ts,quantity,pnl_pts,pnl_krw,"
            "net_pnl_krw,forward_pnl_pts,forward_net_pnl_krw,entry_source)"
            " values (?,?,?,?,?,?,?,?,'SYSTEM_AUTO')",
            (ets, xts, q, pts, krw, krw, pts, krw))
    con.commit()
    con.close()
    monkeypatch.setattr(U, "TRADES_DB", str(db))

    out = {r["date"]: r for r in U.fetch_trend_daily(30)}["2026-08-10"]
    assert out["trades"] == 2, "3레그 → 2포지션"
    assert (out["wins"], out["losses"]) == (1, 1)
    assert out["pnl_krw"] == pytest.approx(-45887)   # 레그 합은 그대로


def test_trend_sql_is_built_in_one_place():
    """네 함수가 SQL을 복사하지 않는가 (한쪽만 고쳐지는 드리프트 방지)."""
    import inspect
    import utils.db_utils as U
    for fn in (U.fetch_trend_daily, U.fetch_trend_weekly,
               U.fetch_trend_monthly, U.fetch_trend_yearly):
        src = inspect.getsource(fn)
        assert "_trend_sql(" in src, "%s 가 공용 빌더를 쓰지 않는다" % fn.__name__
        assert "SUM(CASE WHEN COALESCE(forward_pnl_pts" not in src, \
            "%s 에 레그 단위 SQL이 남아 있다" % fn.__name__


# ── F2: SHS CORE 통과율 ──────────────────────────────────────────────────────

def test_unmeasured_core_pass_is_not_a_penalty():
    """체크리스트 미실행 분이 'CORE 전부 실패'로 계상되지 않는가.

    2026-08-10 실측: FLAT 수렴 189회 + 포지션 보유 구간에 _cr is None 이라
    상시 -25점을 먹었고, 재시작1(-8)+z경고3(-7.5)만 겹쳐도 59.5로 임계 60 아래였다.
    """
    h = SystemHealthScore()
    h.update_restart(1)
    h.update_z_warn(3)
    h.update_core_pass(None)
    assert h.shs == pytest.approx(84.5), "미측정은 감점 대상이 아니다"
    assert h.to_dict()["core_pass_measured"] is False


def test_measured_zero_core_pass_still_penalized():
    """진짜 0%는 그대로 감점 — 가드를 무력화한 게 아니다."""
    h = SystemHealthScore()
    h.update_restart(1)
    h.update_z_warn(3)
    h.update_core_pass(0.0)
    assert h.shs == pytest.approx(59.5)
    assert h.to_dict()["core_pass_measured"] is True


def test_core_pass_partial_scores_proportionally():
    h = SystemHealthScore()
    h.update_core_pass(2.0 / 3.0)
    assert h.shs == pytest.approx(100.0 - (1 - 2 / 3) * 25.0)


def test_shs_alert_text_does_not_claim_blocking(monkeypatch):
    """경보가 하지 않는 일을 한다고 말하지 않는가.

    entry_blocked 는 대시보드 배지에만 쓰인다 — 2026-08-10 경보 8회 중 10건 진입.
    """
    import utils.notify as N
    sent = []
    monkeypatch.setattr(N, "notify", lambda msg, lvl="INFO": sent.append(msg))
    h = SystemHealthScore()
    h.update_core_pass(None)
    N.notify_shs_alert(59.5, h.to_dict())
    msg = sent[0]
    assert "진입 차단" not in msg or "진입 차단 아님" in msg
    assert "미측정" in msg, "미측정 상태가 0%로 표시되면 안 된다"


def test_entry_blocked_is_documented_as_display_only():
    """표시 전용임을 코드가 스스로 밝히는가 (다음 세션 오독 방지)."""
    import inspect
    doc = inspect.getdoc(SystemHealthScore.is_entry_blocked) or ""
    assert "표시 전용" in doc and "막지 않는다" in doc
