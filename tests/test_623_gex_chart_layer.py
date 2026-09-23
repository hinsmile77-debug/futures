# -*- coding: utf-8 -*-
"""[MW0601 623차] 1분봉 차트 — 만기북(먼스리·목위클·월위클) 감마월 · GEX 패널 레이어.

    conda run -n py37_32 python -m pytest tests/test_623_gex_chart_layer.py -q
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QSize            # noqa: E402
from PyQt5.QtGui import QImage, QPainter  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

_APP = None


def _canvas():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    from dashboard.main_dashboard import MinuteChartCanvas
    return MinuteChartCanvas()


def _bars(n, day="2026-09-23"):
    t0 = datetime.datetime(2026, 9, 23, 9, 0)
    return [{"ts": (t0 + datetime.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
             "open": 1118.0, "high": 1122.0, "low": 1114.0, "close": 1119.0,
             "volume": 10} for i in range(n)]


def _snap(hm, cw, pw, gex, nv=48, nt=48):
    return {"ts": "2026-09-23 %s:17" % hm, "call_wall": cw, "put_wall": pw,
            "gex_bn": gex, "n_valid": nv, "n_target": nt, "label": "2609W4"}


_BOOKS = {
    "monthly":    [_snap("09:05", 1150.0, 1100.0, 5.0), _snap("09:35", 1150.0, 1100.0, 5.1)],
    "weekly_thu": [_snap("09:05", 1112.5, 1105.0, 41.6), _snap("09:35", 1115.0, 1116.5, 38.0, nv=40)],
    "weekly_mon": [_snap("09:05", None, None, None, nv=0)],     # 미측정 스냅샷
}


def _render(books, toggles=("gw_month", "gw_thu", "gw_mon")):
    c = _canvas()
    c.resize(1200, 700)
    c.reset_session(_bars(60), [])
    for k in toggles:
        c.set_overlay(k, True)
    c.set_option_book(books)
    chips, panels = [], []
    _orig_chip, _orig_panel = c._draw_label_chip, c._draw_gex_panel

    def _spy_chip(painter, x, y, text, fill, stroke, upward):
        chips.append(text)
        return _orig_chip(painter, x, y, text, fill, stroke, upward)

    def _spy_panel(painter, rect, *a):
        panels.append(rect.height())
        return _orig_panel(painter, rect, *a)
    c._draw_label_chip = _spy_chip
    c._draw_gex_panel = _spy_panel
    img = QImage(QSize(1200, 700), QImage.Format_RGB32)
    p = QPainter(img)
    c.render(p)
    p.end()
    return c, img, chips, panels


def _has_color(img, rgb, tol=40):
    r0, g0, b0 = (rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255
    for y in range(0, img.height(), 2):
        for x in range(0, img.width(), 2):
            v = img.pixel(x, y)
            if (abs(((v >> 16) & 255) - r0) < tol and abs(((v >> 8) & 255) - g0) < tol
                    and abs((v & 255) - b0) < tol):
                return True
    return False


def test_walls_draw_latest_chip_per_book():
    c, img, chips, panels = _render(_BOOKS)
    # 마지막 스냅샷 값으로 칩을 단다 (09:35 → 콜월 1115 · 풋월 1116.5)
    assert "목위클 콜월 1115" in chips
    assert "목위클 풋월 1116.5" in chips
    assert not any("월위클" in t for t in chips)       # 미측정 북은 칩이 없다(0 이 아니다)
    assert panels and panels[0] > 0                    # GEX 패널 자리를 뗐다
    assert _has_color(img, 0xFFA657)                   # 목위클 색이 실제로 찍혔다


def test_off_axis_walls_are_marked_not_placed():
    """먼스리 벽(1150/1100)은 봉 범위 밖 — 가장자리 가격인 척 **그 높이에** 칩을 달면 안 된다.
    값은 ▲/▼ 가 붙은 가장자리 칩으로만 알린다(두 개 다 — 아래쪽이 겹쳐 사라지지 않는다)."""
    _, _, chips, _ = _render(_BOOKS, toggles=("gw_month",))
    mon = [t for t in chips if "먼스리" in t]
    assert sorted(mon) == ["▲ 먼스리 콜월 1150", "▼ 먼스리 풋월 1100"]


def test_toggles_off_draw_nothing():
    c, img, chips, panels = _render(_BOOKS, toggles=())
    assert c._gex_panel_height() == 0 and not panels
    assert not any("콜월" in t or "풋월" in t for t in chips)
    assert not _has_color(img, 0xFFA657)


def test_unloaded_or_empty_books_do_not_crash():
    for books in (None, {}, {"weekly_thu": []}):
        c, _, chips, panels = _render(books)
        assert c._gex_panel_height() == 0 and not panels and not chips


def test_spans_are_steps_until_next_snapshot():
    c = _canvas()
    bars = _bars(60)
    idx = {b["ts"]: i for i, b in enumerate(bars)}
    snaps = [_snap("09:05", 1112.5, 1105.0, 1.0), _snap("09:10", 1115.0, 1105.0, 1.0),
             _snap("09:15", 1115.0, 1105.0, 1.0)]
    sp = c._gex_spans(snaps, bars, idx)
    assert [(a, b) for a, b, _ in sp] == [(5, 10), (10, 15), (15, 30)]   # 마지막은 15봉 상한


def test_collection_gap_is_not_bridged():
    """수집 공백(30분)을 한 줄로 잇지 않는다 — 벽이 그대로였던 척하면 안 된다(실측 49분 사례)."""
    c = _canvas()
    bars = _bars(60)
    idx = {b["ts"]: i for i, b in enumerate(bars)}
    sp = c._gex_spans(_BOOKS["weekly_thu"], bars, idx)          # 09:05 → 09:35
    assert [(a, b) for a, b, _ in sp] == [(5, 5 + c.GEX_STALE_BARS), (35, 50)]


def test_dialog_toggle_keys_match_canvas_spec():
    from dashboard.main_dashboard import MinuteChartDialog, _GEX_BOOK_SPEC
    keys = {k for k, _t, _c in MinuteChartDialog._OV_SPEC}
    for _b, k, _n, col in _GEX_BOOK_SPEC:
        assert k in keys
        assert dict((kk, cc) for kk, _t, cc in MinuteChartDialog._OV_SPEC)[k] == col
