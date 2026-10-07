# -*- coding: utf-8 -*-
"""[MW0602 610차] 손익 추이 「피터2」 출처 필터.

피터2(entry_source=PETER2)는 같은 계좌의 실거래라 신동처럼 별도 주체로 떼지 않고 [미륵] 안의
필터로 둔다. 불변식:
  · 셋 다 체크 = 계좌 전체 → 일 손익은 브로커 실측(종전 화면 그대로)
  · 피터2 해제 / 피터2 단독 → 그날 거래 일부만 선택 → 브로커 실측을 쪼갤 수 없어 엔진 net
  · 순방향·역방향은 미륵 거래에만 적용
  · 피터2 0건(shadow)을 「0원」으로 보이지 않는다(계측 4원칙 ②)
ui_prefs.json 은 tmp 로 격리한다 — 실제 사용자 화면 설정을 건드리지 않는다.
"""
import io
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

D1, D2 = "2026-10-08", "2026-10-09"
ROWS = [
    # D1: 미륵 순방향 1 · 미륵 역방향 1 · 피터2 1  → 브로커 실측 -50,000
    dict(entry_ts=D1 + " 09:10:00", exit_ts=D1 + " 09:20:00", pnl_pts=2.0, pnl_krw=100000.0,
         forward_pnl_pts=2.0, forward_pnl_krw=100000.0, quantity=1, reverse_entry_enabled=0,
         entry_source="SYSTEM_AUTO"),
    dict(entry_ts=D1 + " 10:10:00", exit_ts=D1 + " 10:20:00", pnl_pts=-1.0, pnl_krw=-50000.0,
         forward_pnl_pts=1.0, forward_pnl_krw=50000.0, quantity=1, reverse_entry_enabled=1,
         entry_source="SYSTEM_AUTO"),
    dict(entry_ts=D1 + " 11:10:00", exit_ts=D1 + " 11:20:00", pnl_pts=-4.0, pnl_krw=-200000.0,
         forward_pnl_pts=-4.0, forward_pnl_krw=-200000.0, quantity=1, reverse_entry_enabled=0,
         entry_source="PETER2"),
    # D2: 피터2 만 → 그날은 피터2 가 곧 계좌 전체(브로커 실측 +30,000 그대로)
    dict(entry_ts=D2 + " 09:10:00", exit_ts=D2 + " 09:30:00", pnl_pts=0.5, pnl_krw=25000.0,
         forward_pnl_pts=0.5, forward_pnl_krw=25000.0, quantity=1, reverse_entry_enabled=0,
         entry_source="PETER2"),
]
BROKER = {D1: {"net_krw": -50000.0, "source": "broker"},
          D2: {"net_krw": 30000.0, "source": "broker"}}


@pytest.fixture
def panel(tmp_path, monkeypatch):
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    import dashboard.main_dashboard as md
    import utils.db_utils as du
    monkeypatch.setattr(md, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(du, "fetch_daily_net_for_verdict", lambda days=90: dict(BROKER))
    p = md.PnlHistoryPanel()
    monkeypatch.setattr(p, "_load_shindong", lambda: None)
    p.refresh([dict(r) for r in ROWS])
    p._app = app
    return p


def _set(p, fwd, rev, p2):
    for cb, on in ((p._cb_forward, fwd), (p._cb_reverse, rev), (p._cb_peter2, p2)):
        cb.blockSignals(True)
        cb.setChecked(on)
        cb.blockSignals(False)
    p._on_source_changed()


def _day(p, d):
    rows = [r for r in p._active_rows() if r["entry_ts"].startswith(d)]
    return len(rows), p._effective_day_krw(d, rows)


def test_1_default_is_whole_account_broker_net(panel):
    assert panel._cb_peter2.isChecked()            # 기본 켜짐 = 종전 화면
    assert _day(panel, D1) == (3, -50000.0)        # 브로커 실측
    assert _day(panel, D2) == (1, 30000.0)


def test_2_peter2_off_excludes_and_falls_back_to_engine_net(panel):
    _set(panel, True, True, False)
    assert _day(panel, D1) == (2, 50000.0)         # 100,000 − 50,000 (엔진 net)
    assert _day(panel, D2)[0] == 0
    assert "피터2 2건 제외" in panel._mode_banner.text()


def test_3_peter2_only(panel):
    _set(panel, False, False, True)
    assert _day(panel, D1) == (1, -200000.0)       # 미륵 거래가 섞인 날 → 엔진 net
    assert _day(panel, D2) == (1, 30000.0)         # 피터2 만의 날 → 브로커 실측이 곧 피터2
    assert "피터2 단독" in panel._mode_banner.text()
    assert panel.is_peter2_only()


def test_4_direction_filter_does_not_touch_peter2(panel):
    _set(panel, False, True, True)                 # 역방향 + 피터2
    srcs = sorted((r["is_p2"], r["reverse_entry_enabled"]) for r in panel._active_rows())
    assert srcs == [(False, 1), (True, 0), (True, 0)]


def test_5_set_peter2_only_roundtrip_and_pref_saved(panel, tmp_path):
    panel.set_peter2_only(True)
    assert panel.is_peter2_only()
    panel.set_peter2_only(False)
    assert (panel._cb_forward.isChecked(), panel._cb_reverse.isChecked(),
            panel._cb_peter2.isChecked()) == (True, True, True)
    import json
    with io.open(os.path.join(str(tmp_path), "ui_prefs.json"), encoding="utf-8") as f:
        assert json.load(f)["pnl_cb_peter2"] is True


def test_6_zero_peter2_is_not_zero_won(panel, monkeypatch):
    panel.refresh([dict(r) for r in ROWS if r["entry_source"] != "PETER2"])
    _set(panel, False, False, True)
    t = panel._mode_banner.text()
    assert "실거래 0건" in t
    for v in panel._sum.values():
        assert v.text() == "—"                     # 0원·0% 가 아니라 미측정


def test_7_shindong_hides_peter2_checkbox(panel):
    panel._btn_shindong.setChecked(True)
    assert panel._cb_peter2.isHidden()
    panel._btn_mireuk.setChecked(True)
    assert not panel._cb_peter2.isHidden()


def test_8_query_selects_entry_source():
    s = io.open(os.path.join(ROOT, "utils", "db_utils.py"), encoding="utf-8").read()
    body = s[s.index("def fetch_pnl_history"):]
    body = body[:body.index("\ndef ")]
    assert "entry_source" in body.split("FROM trades")[0]


def test_9_logpanel_button_toggles_peter2_only(tmp_path, monkeypatch):
    from PyQt5.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    import dashboard.main_dashboard as md
    import utils.db_utils as du
    monkeypatch.setattr(md, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(du, "fetch_daily_net_for_verdict", lambda days=90: dict(BROKER))
    lp = md.LogPanel()
    lp._on_peter2_btn()
    assert lp.pnl_history.is_peter2_only()
    assert lp.tabs.currentWidget() is lp.pnl_history
    lp._on_peter2_btn()
    assert not lp.pnl_history.is_peter2_only()
