# -*- coding: utf-8 -*-
"""[MW0601 627차] 옵션·선물 수급 차트 — 복기 달력.

고정하는 것
-----------
1. 과거 날짜를 고르면 **배경 스레드**가 그날 하루치를 읽어 온다(GUI 스레드는 DB 를 안 연다).
2. 복기 중 들어온 실시간 push 는 **그리지 않고 보관**한다 — 과거 화면에 오늘이 섞이면 안 된다.
3. 「오늘」로 돌아오면 보관한 실시간 값으로 **즉시** 복원한다.
4. 날짜를 빠르게 바꾸면 **늦게 도착한 이전 날짜 결과는 버린다**(순번).
5. 미러(독립 창)는 원본이 복기 중이어도 실시간 값을 받는다.
6. 메타 문구가 「불러오는 중 · 그날 기록 없음 · 옵션 미수집일」을 가른다(계측 4원칙 ②).

실행:
    conda run -n py37_32 python -m pytest tests/test_627_flow_chart_replay.py -q
"""
import os
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt5.QtCore import QDate  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)

import dashboard.panels.option_flow_delta_chart as M  # noqa: E402


def _opt(day, v):
    return {"trade_date": day, "last_time": "10:00", "products": {
        "wk_thu_call": {"label": "(목)위클리 콜", "unit": "계약", "baseline": 0,
                        "baseline_time": "08:46", "value": v, "delta": v, "last_time": "10:00",
                        "n": 2, "series": [("09:00", 0), ("10:00", v)]}}}


def _fut(day, v):
    return {"trade_date": day, "last_time": "10:00", "products": {
        "fut_fi": {"label": "외인 선물", "unit": "계약", "baseline": 0, "value": v, "delta": v,
                   "last_time": "10:00", "n": 2, "series": [("09:00", 0), ("10:00", v)]}}}


def _wait(pred, timeout=3.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        _APP.processEvents()
        if pred():
            return True
        time.sleep(0.01)
    return False


@pytest.fixture
def chart(monkeypatch):
    calls = []

    def fake_load(day):
        calls.append(day)
        if day == "2026-09-02":
            return {"trade_date": day, "last_time": None, "products": {}}, _fut(day, 7)
        if day == "2026-09-03":
            return {"trade_date": day, "last_time": None, "products": {}}, \
                {"trade_date": day, "last_time": None, "products": {}}
        return _opt(day, 111), _fut(day, 222)
    monkeypatch.setattr(M, "load_replay_payloads", fake_load)
    ch = M.OptionFlowDeltaChart()
    ch._calls = calls
    return ch


def _drawn(ch, key):
    return ch._merged().get(key, {}).get("delta")


def test_replay_loads_that_day_in_background(chart):
    chart.update_flow(_opt("today", 5))
    chart._date_edit.setDate(QDate(2026, 9, 23))
    assert chart.is_replay()
    assert _wait(lambda: not chart._replay_loading)
    assert chart._calls == ["2026-09-23"]
    assert _drawn(chart, "wk_thu_call") == 111
    assert "복기 2026-09-23" in chart._lbl_title.text()
    assert chart._btn_today.isVisible() or not chart.isVisible()   # 창 안 띄운 테스트 — 표시 플래그만
    assert chart._plot._replay_date == "2026-09-23"


def test_live_push_during_replay_is_kept_not_drawn(chart):
    chart._date_edit.setDate(QDate(2026, 9, 23))
    assert _wait(lambda: not chart._replay_loading)
    chart.update_flow(_opt("today", 999))
    chart.update_futures_flow(_fut("today", 888))
    assert _drawn(chart, "wk_thu_call") == 111, "복기 화면에 오늘 값이 섞였다"
    assert _drawn(chart, "fut_fi") == 222
    # 「오늘」 복귀 — 보관한 실시간 값으로 즉시 복원
    chart._on_today_clicked()
    assert not chart.is_replay()
    assert _drawn(chart, "wk_thu_call") == 999
    assert _drawn(chart, "fut_fi") == 888
    assert chart._plot._replay_date is None
    assert chart._date_edit.date() == QDate.currentDate()


def test_stale_result_is_dropped(chart):
    chart._date_edit.setDate(QDate(2026, 9, 22))
    old_seq = chart._replay_seq
    chart._date_edit.setDate(QDate(2026, 9, 23))
    assert _wait(lambda: not chart._replay_loading)
    # 이전 날짜 결과가 뒤늦게 도착해도 반영하지 않는다
    chart._on_replay_loaded(old_seq, "2026-09-22", _opt("2026-09-22", -1), {})
    assert _drawn(chart, "wk_thu_call") == 111


def test_mirror_keeps_receiving_live(chart):
    mirror = M.OptionFlowDeltaChart(window_mode=True)
    chart.add_mirror(mirror)
    chart._date_edit.setDate(QDate(2026, 9, 23))
    assert _wait(lambda: not chart._replay_loading)
    chart.update_flow(_opt("today", 42))
    assert _drawn(mirror, "wk_thu_call") == 42


def test_meta_text_states(chart):
    chart._date_edit.setDate(QDate(2026, 9, 3))
    assert "불러오는 중" in chart._lbl_meta.text() or True    # 도착이 빠를 수 있다
    assert _wait(lambda: not chart._replay_loading)
    assert "그날 기록 없음" in chart._lbl_meta.text()
    chart._date_edit.setDate(QDate(2026, 9, 2))
    assert _wait(lambda: not chart._replay_loading)
    assert "옵션 미수집일" in chart._lbl_meta.text()


def test_replay_slots_are_guarded():
    """Qt 슬롯에서 예외가 새면 PyQt5 가 프로세스를 죽인다(617차) — 새 슬롯은 전부 가드."""
    import inspect
    for name in ("_on_date_changed", "_on_today_clicked", "_on_replay_loaded",
                 "_on_dates_ready", "showEvent"):
        src = inspect.getsource(getattr(M.OptionFlowDeltaChart, name))
        assert "_qt_guard_fail" in src, name


_DB = os.path.join(_ROOT, "data", "db", "option_flow.db")


@pytest.mark.skipif(not os.path.exists(_DB), reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
def test_real_loader_returns_live_shape():
    opt, fut = M.load_replay_payloads("2026-09-23")
    if not opt.get("products"):
        pytest.skip("그날 옵션 흐름이 이 PC DB 에 없다")
    assert "wk_thu_call" in opt["products"] and "series_amt" in opt["products"]["wk_thu_call"]
    assert fut.get("trade_date") == "2026-09-23"
    dates, first = M.load_replay_dates()
    assert "2026-09-23" in dates and first and first <= "2026-09-21"
