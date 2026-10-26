# -*- coding: utf-8 -*-
"""[MW0601 717차 후속] 창3 「주문/체결」 탭 표시 3건 — 회귀 고정.

2026-10-26 18:11 장외 재기동 화면 실측:
  ① 거래 11건이 복원됐는데 「당일 거래 0건」 — 매분 경로가 분봉이 와야 돌았다.
  ② 지연·수신 칸 「——ms」·「0회」 — LatencySync 는 Cybos 경로에서 record() 호출처가 없다(표본 0).
  ③ 자본 줄 「장전 08:30부터 표시」 — 갱신 창(08:30–15:35)을 말하지 않아 고장처럼 읽혔다.
표시만 바뀐다 — 주문·청산·수량 경로는 무변경.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def panel():
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    import dashboard.main_dashboard as md
    p = md.LogPanel()
    yield md, p
    p.deleteLater()
    app.processEvents()


def test_initial_texts(panel):
    md, p = panel
    assert p._order_vals["trades"].text() == "0건"
    for k in ("avg_lat", "peak_lat", "samples"):
        assert p._order_vals[k].text() == "미측정"
    assert p._capital_lbl.text() == md.CAPITAL_IDLE_TEXT
    assert "08:30–15:35" in md.CAPITAL_IDLE_TEXT and "~" not in md.CAPITAL_IDLE_TEXT


def test_zero_samples_is_unmeasured(panel):
    _, p = panel
    p.update_order_metrics(trades=11, avg_lat_ms=0.0, peak_lat_ms=0.0, samples=0)
    assert p._order_vals["trades"].text() == "11건"
    assert [p._order_vals[k].text() for k in ("avg_lat", "peak_lat", "samples")] == ["미측정"] * 3


def test_measured_values_still_shown(panel):
    _, p = panel
    p.update_order_metrics(trades=2, avg_lat_ms=120.4, peak_lat_ms=0.0, samples=5)
    assert p._order_vals["avg_lat"].text() == "120ms"
    assert p._order_vals["peak_lat"].text() == "0ms"     # 측정된 0 은 0 이다
    assert p._order_vals["samples"].text() == "5회"


def test_update_order_trades_only_touches_trades(panel):
    _, p = panel
    p.update_order_metrics(trades=0, avg_lat_ms=0.0, peak_lat_ms=0.0, samples=0)
    p.update_order_trades(7)
    assert p._order_vals["trades"].text() == "7건"
    assert p._order_vals["samples"].text() == "미측정"


# ── 재기동 복원 경로 ──────────────────────────────────────────────────────────
class _Dash:
    def __init__(self):
        self.order_trades = []

    def update_order_trades(self, n):
        self.order_trades.append(n)

    def __getattr__(self, name):          # 그 밖의 패널 호출은 무시
        return lambda *a, **k: None


class _Pos:
    def __init__(self):
        self.n = 0

    def reset_daily(self):
        self.n = 0

    def restore_daily_stats(self, rows):
        self.n = len(rows)

    def daily_stats(self):
        return {"trades": self.n}


def test_restore_pushes_trade_count(monkeypatch):
    import strategy.runtime.session_recovery_service as srs
    rows = [{"direction": "LONG", "entry_price": 857.86, "exit_price": 854.42, "quantity": 1,
             "pnl_pts": -3.44, "pnl_krw": -173630.0, "forward_pnl_pts": None, "forward_pnl_krw": None,
             "exit_reason": "하드스톱(틱)", "grade": "S", "entry_ts": "2026-10-26 09:45:10",
             "exit_ts": "2026-10-26 09:47:00"}] * 3
    monkeypatch.setattr(srs, "fetch_today_trades", lambda d: rows)

    class _Sys:
        _session_no = 2
        dashboard = _Dash()
        position = _Pos()

    s = _Sys()
    try:
        srs.SessionRecoveryService().restore_daily_state(s)
    except Exception:
        pass   # 뒤따르는 ProfitGuard·CB 복원은 이 가짜 객체로는 끝까지 못 간다 — 앞부분만 본다
    assert s.dashboard.order_trades == [3]


def test_restore_display_failure_is_harmless(monkeypatch):
    """대시보드가 새 메서드를 몰라도 복원은 계속된다(표시 실패 ≠ 복원 실패)."""
    import strategy.runtime.session_recovery_service as srs
    src = open(srs.__file__, encoding="utf-8").read()
    i = src.index("update_order_trades(")
    assert "try:" in src[i - 200:i] and "except Exception" in src[i:i + 300]
