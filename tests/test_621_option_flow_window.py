# tests/test_621_option_flow_window.py
"""[MW0601 621차] 수급 증감 차트 — 봉별 증감 표시 · 콜↔풋 상대강도 · 독립 창.

사용자 지시(2026-09-23):
  · 가장 중요하게 보는 것은 「전봉 대비 이번 봉이 늘었나 줄었나」 — 강세·약세 판단은 안 한다
  · (월)·(목) 위클리 콜/풋 그룹 아래에 두 멤버 중 어느 쪽이 더 늘었나를 보이는 행
  · 탭 속이라 봉폭이 작다 → 독립 창으로 분리
"""
from __future__ import annotations

import os

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CHART = os.path.join(_ROOT, "dashboard", "panels", "option_flow_delta_chart.py")
_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")


def _src(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


_QAPP = None


def _app():
    global _QAPP
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from PyQt5.QtWidgets import QApplication
    except Exception:                                    # pragma: no cover
        pytest.skip("PyQt5 없음")
    # ⚠ 반환값을 붙들어야 한다 — 버리면 GC 돼 프로세스가 죽는다(613차 실측).
    _QAPP = QApplication.instance() or QApplication([])
    return _QAPP


def _payload(keys_peaks, n=300, last="13:59"):
    prods = {}
    for key, peak in keys_peaks:
        ser = [("%02d:%02d" % (9 + i // 60, i % 60), int(peak * i / float(n)))
               for i in range(n)]
        prods[key] = {"label": key, "baseline": 0, "baseline_time": "09:00",
                      "value": peak, "delta": peak, "last_time": last,
                      "n": len(ser), "series": ser, "unit": "계약"}
    return {"trade_date": "2026-09-21", "last_time": last, "products": prods}


# ── 순수 계산 ────────────────────────────────────────────────────────────

def test_1_bar_state_compares_with_previous_existing_bar():
    """결측 분을 0 으로 채워 비교하면 가짜 「감소→증가」가 생긴다(계측 4원칙 ②)."""
    from dashboard.panels.option_flow_delta_chart import _bar_states

    pts = [(540, 100), (541, 110), (545, 105), (546, 105)]   # 542~544 결측
    st = _bar_states(pts, thr=0.0)
    assert st[0] == (540, 100, None, 0), "첫 봉은 Δ 없음"
    assert st[1][2:] == (10, 1)
    assert st[2][2:] == (-5, -1), "결측을 건너 직전 존재 봉(541)과 비교해야 한다"
    assert st[3][2:] == (0, 0)


def test_2_deadband_marks_small_changes_as_flat():
    from dashboard.panels.option_flow_delta_chart import _bar_states, _deadband

    deltas = [10, -10, 10, -10, 1]
    thr = _deadband(deltas)
    assert thr == pytest.approx(2.0)                   # 0.2 × 중앙값 10
    st = _bar_states([(540, 0), (541, 1), (542, 20)], thr)
    assert st[1][3] == 0, "|Δ|=1 은 변화 없음"
    assert st[2][3] == 1


def test_3_streak_counts_trailing_run():
    from dashboard.panels.option_flow_delta_chart import _streak

    assert _streak([1, -1, 1, 1, 1]) == (1, 3)
    assert _streak([1, 1, -1]) == (-1, 1)
    assert _streak([]) == (0, 0)


def test_4_rs_is_delta_call_minus_delta_put_on_common_minutes():
    """막대 = Δ콜 − Δ풋, 누적 = 콜 − 풋. 한쪽이 빠진 분은 건너뛴다."""
    from dashboard.panels.option_flow_delta_chart import _rs_points

    call = [(540, 0), (541, 10), (542, 12), (543, 20)]
    put = [(540, 0), (541, 3), (543, 30)]               # 542 결측
    r = _rs_points(call, put)
    assert r == [(541, 10 - 3, 7), (543, (20 - 10) - (30 - 3), -10)]


def test_5_put_decrease_counts_toward_call_side():
    """🔴 증감만 본다 — 풋이 줄면 콜이 안 늘어도 콜 쪽 막대다(사용자 지시)."""
    from dashboard.panels.option_flow_delta_chart import _rs_points

    r = _rs_points([(540, 0), (541, 0)], [(540, 0), (541, -50)])
    assert r[0][1] == 50


# ── 배치 ─────────────────────────────────────────────────────────────────

def test_6_rs_rows_sit_right_under_each_weekly_pair():
    from dashboard.panels.option_flow_delta_chart import _LAYOUT

    keys = [k for _kind, k, _l, _g, _w in _LAYOUT]
    assert keys[:3] == ["wk_mon_call", "wk_mon_put", "rs_mon"]
    assert keys[3:6] == ["wk_thu_call", "wk_thu_put", "rs_thu"]
    assert keys[6:9] == ["mon_call", "mon_put", "rs_mm"], "먼스리 콜↔풋 행(후속3)"
    assert all(keys.count(k) == 1 for k in ("rs_mon", "rs_thu", "rs_mm"))
    # 데이터 행 순서는 612·613차 지시 그대로
    assert [k for kind, k, _l, _g, _w in _LAYOUT if kind == "data"] == [
        "wk_mon_call", "wk_mon_put", "wk_thu_call", "wk_thu_put",
        "mon_call", "mon_put", "open_int", "fut_fi", "prog_arb", "prog_nonarb"]


def test_7_increase_is_not_encoded_by_hue():
    """🔴 증가/감소를 초록/빨강으로 칠하면 풋 행(원래 빨강)에서 구분이 안 된다.

    그래서 막대 색은 상품 종류(`_ROW_COLOR`) 하나만 쓰고, 증감은 채움으로 가른다.
    """
    src = _src(_CHART)
    body = src.split("def _draw_data_row", 1)[1].split("def _draw_rs_row", 1)[0]
    assert "col = QColor(_ROW_COLOR.get(key" in body
    assert "p.drawRect(" in body, "감소(속 빈 막대) 표시가 없다"
    assert '_COL["green"]' not in body and '_COL["red"]' not in body, (
        "데이터 행 막대에 증감용 색이 섞였다")


# ── 렌더 ─────────────────────────────────────────────────────────────────

def test_8_zoomed_view_gives_wide_bars():
    """90분 확대에서 봉폭이 채움/속빔을 가를 만큼 넓어야 한다."""
    _app()
    from dashboard.panels.option_flow_delta_chart import _Plot, _RECT_MIN_PPM

    pl = _Plot(minimap=True)
    pl.set_data(_payload([("wk_mon_call", 9000)])["products"], False)
    pl.set_window(90)
    pl.resize(1100, 800)
    v0, v1 = pl.view_range()
    assert v1 - v0 == 90
    assert v1 - 1 == 13 * 60 + 59, "실시간 모드는 최신 봉에서 끝나야 한다"
    ppm = (1100 - _Plot.LABEL_W - _Plot.VALUE_W) / 90.0
    assert ppm >= _RECT_MIN_PPM * 2


def test_9_anchor_and_follow():
    _app()
    from dashboard.panels.option_flow_delta_chart import _Plot

    pl = _Plot(minimap=True)
    pl.set_data(_payload([("wk_mon_call", 100)])["products"], False)
    pl.set_window(60)
    pl.set_anchor(11 * 60)
    assert not pl.is_following()
    assert pl.view_range() == (11 * 60 + 1 - 60, 11 * 60 + 1)
    pl.set_anchor(23 * 60)               # 최신 봉 이후 → 따라가기로 복귀
    assert pl.is_following()


def test_10_window_and_tab_render_without_exception():
    """탭(전체)·독립 창(90분) 둘 다 전 행이 예외 없이 그려져야 한다."""
    _app()
    from PyQt5.QtGui import QPixmap

    from dashboard.panels import option_flow_delta_chart as M

    errs = []
    orig = M._Plot._paint

    def spy(self):
        try:
            orig(self)
        except Exception as exc:                          # pragma: no cover
            errs.append(exc)
            raise
    M._Plot._paint = spy
    try:
        tab = M.OptionFlowDeltaChart()
        win = M.OptionFlowDeltaWindow()                   # prefs_path=None → 저장 안 함
        tab.add_mirror(win.chart)
        tab.update_flow(_payload([("wk_mon_call", 9656), ("wk_mon_put", -12135),
                                  ("wk_thu_call", 198), ("wk_thu_put", 1041),
                                  ("mon_call", -244)]))           # mon_put 미수집
        tab.update_futures_flow(_payload([("open_int", 3000), ("prog_arb", -500)]))
        for w, size in ((tab, (560, 400)), (win, (1100, 860))):
            w.resize(*size)
            w.render(QPixmap(w.size()))
        # 크로스헤어 오버레이도 그려져야 한다
        win.chart._plot._hover_min = 13 * 60 + 30
        win.render(QPixmap(win.size()))
        win.chart._chk_shared.setChecked(True)
        win.render(QPixmap(win.size()))
        assert not errs, "paint 예외: %s" % errs[0]
        assert win.chart._plot._rows_geo, "행 좌표가 기록되지 않았다"
    finally:
        M._Plot._paint = orig


def test_11_mirror_receives_same_payload_and_age():
    """독립 창은 탭 차트가 받은 값을 그대로 받는다 — 스스로 조회하지 않는다."""
    _app()
    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart

    tab = OptionFlowDeltaChart()
    pl = _payload([("wk_mon_call", 10)])
    tab.update_flow(pl)
    tab.set_age_text("수급 3분 00초 전", "warn")
    win = OptionFlowDeltaChart(window_mode=True)
    tab.add_mirror(win)                   # 나중에 붙여도 지금까지의 값을 받는다
    assert win._payload is pl
    assert win._lbl_age.text() == "수급 3분 00초 전"
    fp = _payload([("fut_fi", 5)])
    tab.update_futures_flow(fp)
    assert win._fut_payload is fp


def test_12_mirror_failure_does_not_break_tab_chart():
    _app()
    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart

    class Boom:
        def update_flow(self, _p):
            raise RuntimeError("x")

        def update_futures_flow(self, _p):
            raise RuntimeError("x")

        def set_age_text(self, *_a):
            raise RuntimeError("x")

    tab = OptionFlowDeltaChart()
    tab._mirrors.append(Boom())
    pl = _payload([("wk_mon_call", 10)])
    tab.update_flow(pl)                   # 예외가 밖으로 나오면 안 된다
    assert tab._payload is pl


def test_13_default_windows():
    _app()
    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart

    assert OptionFlowDeltaChart()._plot._window_min is None, "탭은 기본 전체"
    # [후속8] 독립 창 기본 90 → 60분(사용자 지시)
    assert OptionFlowDeltaChart(window_mode=True)._plot._window_min == 60


# ── 부하·배선 ────────────────────────────────────────────────────────────

def test_14_bars_are_cached_and_crosshair_only_overlays():
    """🔴 메인 스레드를 매매 파이프라인과 공유한다 — 마우스 이동마다 전체를 다시 그리지 않는다."""
    src = _src(_CHART)
    pe = src.split("def paintEvent", 1)[1].split("def _group_max", 1)[0]
    assert "self._dirty" in pe and "drawPixmap" in pe
    mv = src.split("def mouseMoveEvent", 1)[1].split("def leaveEvent", 1)[0]
    assert "_invalidate" not in mv and "_dirty" not in mv, "호버가 캐시를 무효화한다"
    assert "_PAINT_SLOW_MS" in src.split("def _paint(self)", 1)[1][:2000]


def test_15_dashboard_wires_window_as_mirror():
    dash = _src(_DASH)
    assert "OptionFlowDeltaWindow(" in dash
    assert "add_mirror(self._option_flow_window.chart)" in dash
    assert "def toggle_option_flow_window" in dash
    assert "popout_requested.connect(self.toggle_option_flow_window)" in dash


def test_16_window_does_not_write_prefs_without_path(tmp_path):
    """테스트·기본 생성은 사용자의 ui_prefs.json 을 건드리면 안 된다."""
    _app()
    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaWindow

    w = OptionFlowDeltaWindow()
    w._save_geometry()                    # 경로 없음 → 아무것도 안 함
    p = tmp_path / "prefs.json"
    p.write_text('{"keep": 1}', encoding="utf-8")
    w2 = OptionFlowDeltaWindow(prefs_path=str(p))
    w2.resize(700, 500)          # offscreen 화면(800×600) 안 — 가용 크기 절단을 피한다
    w2._save_geometry()
    import json
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["keep"] == 1, "다른 키를 덮어썼다"
    assert d[OptionFlowDeltaWindow.PREFS_KEY]["w"] == 700


# ── [621차 후속] 맨 오른쪽 열 동기화 ────────────────────────────────────
# 사용자 보고(2026-09-23 10:56): 「최우측란에 해당 봉이 동시에 올라오지 않는다」.

def test_17_horizon_is_last_completed_minute_and_replay_is_uncut():
    import datetime as dt

    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart as C

    now = dt.datetime(2026, 9, 23, 10, 57, 2)
    assert C._complete_horizon({"trade_date": "2026-09-23"}, now) == 10 * 60 + 56, (
        "10:57:02 에 받은 값은 10:56 까지만 마감이다 — 10:57 은 2초짜리 진행 중 봉")
    assert C._complete_horizon({"trade_date": "2026-09-21"}, now) is None, (
        "복기(과거 날짜)는 자르면 안 된다")


def test_18_new_column_opens_only_when_both_sources_arrived():
    """선물이 먼저 와도 옵션이 오기 전에는 새 열을 열지 않는다(한 틱 안 두 번 push)."""
    _app()
    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart

    ch = OptionFlowDeltaChart()
    ch._horizon = {"opt": 655, "fut": 656}         # 선물만 10:56 까지 도착
    assert ch.display_cutoff() == 655
    ch._horizon["opt"] = 656                        # 옵션 도착 → 함께 연다
    assert ch.display_cutoff() == 656


def test_19_dead_source_does_not_freeze_the_other():
    _app()
    from dashboard.panels.option_flow_delta_chart import (_SYNC_STALE_MIN,
                                                          OptionFlowDeltaChart)

    ch = OptionFlowDeltaChart()
    ch._horizon = {"opt": 600, "fut": 600 + _SYNC_STALE_MIN + 1}
    assert ch.display_cutoff() == 600 + _SYNC_STALE_MIN + 1
    ch._horizon = {"opt": None, "fut": 640}        # 옵션 아직 한 번도 안 옴
    assert ch.display_cutoff() == 640


def test_20_trim_drops_in_progress_bar_and_resyncs_badge():
    _app()
    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart

    ch = OptionFlowDeltaChart()
    ch._payload = {"trade_date": "x", "products": {"mon_put": {
        "baseline": -500, "value": -532, "delta": -32, "last_time": "10:57",
        "series": [("10:55", -25), ("10:56", -31), ("10:57", -32)]}}}
    ch._fut_payload = {"trade_date": "x", "products": {"fut_fi": {
        "baseline": 100, "value": 90, "delta": -10, "last_time": "10:57",
        "series": [("10:56", -8), ("10:57", -10)]}}}
    ch._horizon = {"opt": 656, "fut": 656}
    m = ch._merged()
    assert [t for t, _v in m["mon_put"]["series"]][-1] == "10:56"
    assert m["mon_put"]["delta"] == -31 and m["mon_put"]["value"] == -531, (
        "배지(시초·누계)가 화면 마지막 봉과 어긋난다")
    assert m["fut_fi"]["last_time"] == "10:56"
    # 원본 payload 는 건드리지 않는다(미러가 같은 객체를 받는다)
    assert ch._payload["products"]["mon_put"]["last_time"] == "10:57"


def test_21_missing_minutes_are_marked_not_bridged():
    """행이 없는 분은 0 으로 잇지 않고 「행 없음」 점으로 칸을 채운다."""
    src = _src(_CHART)
    body = src.split("def _draw_data_row", 1)[1].split("def _draw_rs_row", 1)[0]
    assert 'tips[tm] = "행 없음"' in body
    _app()
    from PyQt5.QtGui import QPixmap

    from dashboard.panels.option_flow_delta_chart import _Plot

    pl = _Plot(minimap=True)
    pl.set_data({
        "wk_mon_call": {"series": [("10:50", 1), ("10:52", 3)], "delta": 3, "value": 3},
        "mon_put": {"series": [("10:50", 1), ("10:51", 2), ("10:52", 3), ("10:53", 4)],
                    "delta": 4, "value": 4},
    }, False)
    pl.set_window(60)
    pl.resize(1100, 800)
    pl.render(QPixmap(pl.size()))
    tips = pl._rows_geo[0][1]                       # 첫 행 = wk_mon_call
    assert tips.get(10 * 60 + 51) == "행 없음", "중간 결측 분이 비어 있다"
    assert tips.get(10 * 60 + 53) == "행 없음", "맨 오른쪽 열이 비어 있다"


# ── [621차 후속2] 시간 눈금 위치 · 툴팁 ─────────────────────────────────

def test_22_tooltip_only_on_title():
    """사용자 지시 — 툴팁은 좌상단 타이틀에만. 막대를 볼 때 설명이 가리지 않게."""
    src = _src(_CHART)
    code = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
    assert code.count(".setToolTip(") == 1
    assert "self._lbl_title.setToolTip(_TITLE_TIP)" in code
    _app()
    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart

    ch = OptionFlowDeltaChart(window_mode=True)
    assert ch._plot.toolTip() == "" and ch._chk_shared.toolTip() == ""
    assert "하루 전체" in ch._lbl_title.toolTip()


def test_23_time_axis_sits_above_rows():
    """시간 눈금은 행 **위**에 — 첫 행이 미니맵+눈금 띠 아래에서 시작한다."""
    _app()
    from dashboard.panels.option_flow_delta_chart import _Plot

    pl = _Plot(minimap=True)
    pl.set_window(60)
    pl.resize(1100, 800)
    top, _h = pl.row_spans(pl.row_height())[0]
    assert top == _Plot.PAD_V + _Plot.MINIMAP_H + _Plot.AXIS_H
    # [후속8] 독립 창은 하루 전체 띠와 시간 눈금 **사이**에 상태 줄이 들어간다
    ps = _Plot(minimap=True, status=True)
    ps.set_window(60)
    ps.resize(1100, 800)
    top2, _h = ps.row_spans(ps.row_height())[0]
    assert top2 == _Plot.PAD_V + _Plot.MINIMAP_H + _Plot.STATUS_H + _Plot.AXIS_H
    src = _src(_CHART)
    axis = src.split("def _draw_axis", 1)[1].split("def _draw_minimap", 1)[0]
    assert "top0 - self.AXIS_H" in axis and "QRectF(x - 20, ybase" not in axis


# ── [621차 후속4] 창 단추(최소화 · 최대화/이전 크기) ─────────────────────

def test_24_minute_chart_has_min_max_buttons():
    """당일 1분봉 차트 — 최소화·최대화 단추(사용자 지시 2026-09-23)."""
    dash = _src(_DASH)
    body = dash.split("class MinuteChartDialog", 1)[1].split("def __init__", 1)[1][:1500]
    assert "Qt.WindowMinMaxButtonsHint" in body
    # 플래그는 HWND 생성 전(생성자)에 — 나중에 바꾸면 창이 다시 만들어진다
    assert body.index("setWindowFlags") < body.index("self.resize(")


def test_25_toggle_restores_minimized_instead_of_closing():
    """최소화된 창도 isVisible() 이 True — 단축키가 닫기가 되면 안 된다."""
    dash = _src(_DASH)
    body = dash.split("def toggle_minute_chart_dialog", 1)[1].split("\n    def ", 1)[0]
    assert (body.index("if self._minute_chart_dialog.isMinimized()")
            < body.index("if self._minute_chart_dialog.isVisible()"))
    assert "showNormal()" in body
    # 작업표시줄 단추는 위치 복원 뒤·show() 전에
    i_restore = body.index("restore_saved_geometry()")
    i_force = body.index("force_taskbar_button(")
    i_show = body.index(".show()")
    assert i_restore < i_force < i_show


def test_26_minimize_is_not_a_close():
    """[후속5 갱신] 최소화(OS 가 보내는 spontaneous hide)는 저장 계기가 아니다.

    후속4 는 「최소화 상태면 저장 생략」이었으나 후속5 가 저장을 hideEvent 로 옮기고
    최대화·최소화 중에는 normalGeometry() 를 쓰게 바꿨다 — 불변식은 그대로다.
    """
    dash = _src(_DASH)
    hide = dash.split("class MinuteChartDialog", 1)[1].split("def hideEvent", 1)[1][:600]
    assert "if not event.spontaneous():" in hide


def test_27_taskbar_helper_is_noop_offscreen():
    """offscreen(테스트)에서는 아무것도 하지 않는다 — 가짜 핸들에 Win32 호출 금지."""
    _app()
    from PyQt5.QtWidgets import QDialog

    from dashboard.window_utils import force_taskbar_button

    assert force_taskbar_button(QDialog()) is False


# ── [621차 후속5] 창 크기 복원 ─────────────────────────────────────────
# 사용자 보고(2026-09-23): 「크기조정 후 닫고 다시 열면 이전 크기가 안 온다」.
# 실측 저장값이 정확히 1920×1060(종전 고정 상한)이었다.

class _FakeScreen:
    def __init__(self, dpi, aw, ah):
        self._dpi, self._aw, self._ah = dpi, aw, ah

    def logicalDotsPerInch(self):
        return self._dpi

    def availableGeometry(self):
        from PyQt5.QtCore import QRect
        return QRect(0, 0, self._aw, self._ah)


def test_28_budget_keeps_150pct_limit_and_frees_100pct():
    """150% 모니터 상한은 종전(217차 18MB)과 같고, 100% 모니터에서만 풀린다."""
    from dashboard.window_utils import DIB_BUDGET_BYTES, dib_safe_size

    hi = _FakeScreen(144, 3840, 2160)
    w, h, clipped = dib_safe_size(hi, 2600, 1500)
    assert clipped and w * h * 4 * 1.5 * 1.5 <= DIB_BUDGET_BYTES * 1.001
    assert w * h <= 1920 * 1060 * 1.001, "150% 모니터에서 종전보다 커졌다 — 크래시 위험 증가"
    assert abs(w / float(h) - 2600 / 1500.0) < 0.01, "비율을 유지해 줄여야 한다"
    lo = _FakeScreen(96, 2560, 1400)
    assert dib_safe_size(lo, 2560, 1400) == (2560, 1400, False), "100% 전체화면이 잘렸다"
    assert dib_safe_size(lo, 2300, 1250) == (2300, 1250, False)
    assert dib_safe_size(None, 2300, 1250)[2], "모니터 모름 → 150% 로 보수 가정"


def test_29_minute_chart_saves_on_every_close_path():
    dash = _src(_DASH)
    cls = dash.split("class MinuteChartDialog", 1)[1]
    save = cls.split("def _save_geometry", 1)[1].split("\n    def ", 1)[0]
    assert "normalGeometry()" in save, "최대화로 닫으면 보통 크기를 잃는다"
    assert "dib_safe_size(" in save
    assert "min(geo.width(),  _CHART_MAX_LOGICAL_W)" not in cls, "고정 상한 절단이 남았다"
    hide = cls.split("def hideEvent", 1)[1].split("\n    def ", 1)[0]
    assert '_save_geometry("hide")' in hide and "spontaneous()" in hide, (
        "Esc(reject)는 closeEvent 를 거치지 않는다 — hideEvent 에서 저장해야 한다")
    rest = cls.split("def restore_saved_geometry", 1)[1].split("\n    def ", 1)[0]
    assert "dib_safe_size(target_screen" in rest


# ── [621차 후속6] 1분봉 차트 배경 캐시 ───────────────────────────────────
# 사용자 보고(2026-09-23): 최대화 시 「차트영역과 윈도우 영역이 따로 논다」.
# 원인: 전 레이어 다시 그리기(격리 ~30ms · 라이브 78~140ms)를 호버가 최대 60회/초,
# 틱이 5회/초 요청했다(09-15 이후 하루 약 35,000회 slow paint).

def _canvas_with_live():
    _app()
    import datetime as dt

    from dashboard.main_dashboard import MinuteChartCanvas

    cv = MinuteChartCanvas()
    rows = [{"ts": "2026-09-21 09:%02d:00" % i, "open": 100.0 + i % 5, "high": 102.0 + i % 5,
             "low": 99.0 + i % 5, "close": 101.0 + i % 5, "volume": 10} for i in range(40)]
    cv.reset_session(rows, [])
    cv.resize(900, 520)
    live_t = dt.datetime(2026, 9, 21, 9, 40, 5)
    cv.update_tick(101.0, ts=live_t)
    return cv, live_t


def _render(cv):
    from PyQt5.QtGui import QPixmap
    pm = QPixmap(cv.size())
    cv.render(pm)
    return pm.toImage()


def test_30_hover_and_tick_reuse_cache_and_match_full_render():
    import datetime as dt

    from PyQt5.QtCore import QPoint

    cv, live_t = _canvas_with_live()
    _render(cv)                                            # 전체 그리기 → 캐시
    cv._last_tick_update_ms = 0
    cv.update_tick(101.3, ts=live_t + dt.timedelta(seconds=10))   # 같은 분·범위 안
    cv._hover_pos = QPoint(400, 200)
    n0 = cv._dbg_overlay_count
    a = _render(cv)
    assert cv._dbg_overlay_count == n0 + 1, "틱·호버가 캐시를 재사용하지 않았다"
    cv._base_dirty = True
    b = _render(cv)
    assert a == b, "캐시 경로 화면이 전체 그리기와 다르다"


def test_31_state_change_and_new_bar_invalidate_cache():
    import datetime as dt

    cv, live_t = _canvas_with_live()
    _render(cv)
    n0 = cv._dbg_overlay_count
    cv.set_direction_at("2026-09-21 09:39:00", 1)          # 파이썬 update() → 무효화
    _render(cv)
    assert cv._dbg_overlay_count == n0
    cv._last_tick_update_ms = 0
    cv.update_tick(101.0, ts=live_t + dt.timedelta(minutes=1))    # 새 봉
    _render(cv)
    assert cv._dbg_overlay_count == n0
    cv._last_tick_update_ms = 0
    cv.update_tick(500.0, ts=live_t + dt.timedelta(minutes=1, seconds=5))  # 축 범위 확장
    _render(cv)
    assert cv._dbg_overlay_count == n0


def test_32_live_price_links_are_drawn_in_overlay():
    """[후속7] 보유 중 연결선·GP 미청산 다리는 현재가를 따른다 — 캐시가 아니라 오버레이가 그린다.

    후속6 은 「1초에 한 번 전체 그리기」였으나 재기동 실측에서 GP 미청산 1건 때문에
    전체 그리기가 35회/분에 머물렀다(11:53~11:58). 선을 오버레이로 옮기면 틱마다
    캐시를 쓰면서도 선 끝이 지연 없이 따라온다.
    """
    import datetime as dt

    cv, live_t = _canvas_with_live()
    cv.sync_active_trade("LONG", 100.0, ts=live_t)
    _render(cv)
    # [dev 이식] dev 의 보유 중 표시는 **진입가 수평선**이다(v9-dev 555차 후속2 의 진입→현재가
    #   연결선이 없다) — 현재가를 안 쓰므로 오버레이로 넘길 선도 없다. 요점(보유 중 틱이
    #   캐시를 재사용하고, 그 화면이 전체 그리기와 같다)만 고정한다.
    assert not cv._base_meta["live_dep"]
    cv._last_tick_update_ms = 0
    cv.update_tick(101.8, ts=live_t + dt.timedelta(seconds=20))
    n0 = cv._dbg_overlay_count
    a = _render(cv)
    assert cv._dbg_overlay_count == n0 + 1, "보유 중 틱이 캐시를 재사용하지 않았다"
    cv._base_dirty = True
    b = _render(cv)
    assert a == b, "오버레이 연결선이 전체 그리기와 다르다"


def test_33_cache_path_errors_fall_back_not_abort():
    """🔴 PyQt5 는 paintEvent 안 미처리 예외에서 프로세스를 abort 한다(0xC0000409)."""
    dash = _src(_DASH)
    pe = dash.split("class MinuteChartCanvas", 1)[1].split("    def paintEvent", 1)[1][:3000]
    assert "except Exception as _ce:" in pe and "self._base_cache_error(_ce)" in pe
    assert "QPixmap,   # [621차 후속6]" in dash, "QPixmap import 누락 — paint 에서 NameError → abort"



# ── [621차 후속8] 상태 줄 — LIVE · 브로커 시각 · 다음 분봉 ─────────────────

def test_34_broker_clock_falls_back_to_pc_and_says_so():
    """모르면 PC 시각을 쓰되 **브로커 시각인 척 하지 않는다**(계측 4원칙 ④)."""
    _app()
    from dashboard.panels.option_flow_delta_chart import _Plot

    pl = _Plot(minimap=True, status=True)
    now, is_broker, off = pl.broker_now()
    assert is_broker is False and off is None
    pl.set_clock_provider(lambda: None)
    assert pl.broker_now()[1] is False
    pl.set_clock_provider(lambda: 1.5)
    now2, is_broker2, off2 = pl.broker_now()
    assert is_broker2 and off2 == 1.5
    def boom():
        raise RuntimeError("x")
    pl.set_clock_provider(boom)
    assert pl.broker_now()[1] is False, "공급자 예외가 화면을 죽이면 안 된다"


def test_35_status_strip_renders_and_does_not_invalidate_cache():
    _app()
    from PyQt5.QtGui import QPixmap

    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaWindow

    w = OptionFlowDeltaWindow()
    w.chart.update_flow(_payload([("wk_mon_call", 100), ("wk_mon_put", -50)]))
    w.chart.set_clock_provider(lambda: 0.4)
    w.resize(1100, 860)
    w.render(QPixmap(w.size()))
    pl = w.chart._plot
    assert pl._status_timer is not None and pl._status_timer.interval() == 500
    pl._dirty = False
    pl._on_status_tick()                       # 500ms 틱
    assert pl._dirty is False, "시계 틱이 캐시를 무효화했다 — 막대를 매번 다시 그린다"


def test_36_broker_offset_is_state_only_in_com_callback():
    """🔴 절대원칙 §4 — 틱 콜백 안에서는 상태 저장만. 파싱 실패 폴백(PC 시각)은 표본에서 뺀다."""
    src = _src(os.path.join(_ROOT, "collection", "cybos", "realtime_data.py"))
    blk = src.split("# [MW0601 621차 후속8] 브로커 시계 표본", 1)[1][:900]
    assert "self._broker_offsets.append(" in blk
    assert "len(_digits) >= 5" in blk, "파싱 실패 폴백(오프셋 0)이 실측으로 섞인다"
    assert "abs(_off) <= 30.0" in blk, "버퍼 재생 틱이 시계로 섞인다"
    for bad in ("emit(", "dynamicCall", "dashboard"):
        assert bad not in blk
    from collection.cybos.realtime_data import CybosRealtimeData  # noqa: F401


def test_37_broker_offset_uses_recent_max_and_none_when_stale():
    """체결시각은 초 단위로 잘려 온다 — 최근 60초 표본의 최댓값. 표본이 없으면 None(모름)."""
    import time as _t
    from collections import deque

    from collection.cybos.realtime_data import CybosRealtimeData

    rt = CybosRealtimeData.__new__(CybosRealtimeData)
    rt._broker_offsets = deque(maxlen=240)
    assert rt.broker_clock_offset() is None
    now = _t.monotonic()
    rt._broker_offsets.extend([(now - 200, 9.0), (now - 5, -0.8), (now - 2, 0.3), (now - 1, -0.2)])
    assert rt.broker_clock_offset() == 0.3, "창 밖(200초 전) 표본이 섞였다"
    rt._broker_offsets.clear()
    rt._broker_offsets.append((now - 120, 0.5))
    assert rt.broker_clock_offset() is None



# ── [621차 후속9] 다음 분봉 — 실제 봉 열림 기준 · 차오르는 막대 ──────────────

def _flow(last_min):
    ser = [("%02d:%02d" % divmod(m, 60), m - 540) for m in range(540, last_min + 1)]
    return {"trade_date": "2026-09-21", "last_time": ser[-1][0], "products": {
        "wk_mon_call": {"baseline": 0, "value": 1, "delta": 1, "series": ser}}}


def test_38_bar_clock_starts_on_real_column_open_not_on_first_load():
    _app()
    import time as _t

    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart

    ch = OptionFlowDeltaChart(window_mode=True)
    ch.update_flow(_flow(600))
    assert ch._plot._bar_opened_mono is None, "첫 적재를 봉 열림으로 셌다"
    ch.update_flow(_flow(600))                     # 같은 열 — 갱신 아님
    assert ch._plot._bar_opened_mono is None
    ch.update_flow(_flow(601))                     # 새 열
    t1 = ch._plot._bar_opened_mono
    assert t1 is not None and ch._plot._bar_interval_measured is False
    ch._col_opened_mono = _t.monotonic() - 61.0    # 61초 전에 열렸던 것으로
    ch.update_flow(_flow(602))
    ch._col_opened_mono = _t.monotonic() - 59.0
    ch.update_flow(_flow(603))
    assert ch._plot._bar_interval_measured is True
    assert 55.0 <= ch._plot._bar_interval_s <= 65.0


def test_39_bar_clock_ignores_restart_gaps():
    _app()
    import time as _t

    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart

    ch = OptionFlowDeltaChart(window_mode=True)
    ch.update_flow(_flow(600))
    ch.update_flow(_flow(601))
    ch._col_opened_mono = _t.monotonic() - 900.0   # 15분 공백(재기동)
    ch.update_flow(_flow(602))
    assert ch._col_intervals == [], "재기동 공백을 간격으로 셌다"


def test_40_strip_renders_all_states():
    """대기 · 진행 · 지연 세 상태가 예외 없이 그려진다(paint 예외는 경고로만 남는다)."""
    _app()
    import time as _t

    from PyQt5.QtGui import QPixmap

    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaWindow, _Plot

    w = OptionFlowDeltaWindow()
    w.chart.update_flow(_payload([("wk_mon_call", 100)]))
    w.resize(1100, 860)
    errs = []
    orig = _Plot._draw_status_strip

    def spy(self, p):
        try:
            orig(self, p)
        except Exception as exc:                  # pragma: no cover
            errs.append(exc)
            raise
    _Plot._draw_status_strip = spy
    try:
        pl = w.chart._plot
        for opened in (None, _t.monotonic() - 20, _t.monotonic() - 90):
            pl.set_bar_clock(opened, 60.0, opened is not None)
            w.render(QPixmap(w.size()))
    finally:
        _Plot._draw_status_strip = orig
    assert not errs, errs



def test_41_strip_number_counts_up_from_zero():
    """[후속10] 숫자는 막대와 같은 방향 — 열린 뒤 경과 초(0부터 증가)."""
    src = _src(_CHART)
    body = src.split("def _draw_status_strip", 1)[1].split("def _draw_overlay", 1)[0]
    assert 'text("%d초" % int(el)' in body
    assert "int(rem + 0.999)" not in body, "남은 초(감소) 표기가 남았다"


# ── [621차 후속11] Qt 진입점 가드 — 617차 래칫 원칙을 621차 진입점 전부로 넓힌다 ─────
# 래칫(test_617)은 QTimer 슬롯만 센다. 하지만 PyQt5 는 **어떤** Qt 진입점(슬롯·이벤트
# 처리기)에서 새어나온 예외든 qFatal() 로 프로세스를 죽인다. 621차가 넣거나 고친
# 진입점은 전부 감사기와 같은 형태(본문 == 단일 Try + Exception 포착)로 고정한다.

_GUARDED_621 = {
    _CHART: ["_Plot.showEvent", "_Plot.hideEvent", "_Plot.mouseMoveEvent", "_Plot.leaveEvent",
             "_Plot.mousePressEvent", "_Plot.wheelEvent", "_Plot.paintEvent",
             "_Plot._on_status_tick",
             "OptionFlowDeltaChart._on_toggle", "OptionFlowDeltaChart._on_window",
             "OptionFlowDeltaChart._sync_live_btn", "OptionFlowDeltaChart._on_live_clicked",
             "OptionFlowDeltaWindow.toggle", "OptionFlowDeltaWindow.hideEvent"],
    _DASH: ["MinuteChartCanvas.paintEvent", "MinuteChartCanvas.mouseMoveEvent",
            "MinuteChartCanvas.leaveEvent", "MinuteChartDialog.hideEvent",
            "MireukDashboard.toggle_option_flow_window",
            "MireukDashboard.toggle_minute_chart_dialog"],
}


def _is_single_try_guard(fn):
    import ast
    body = list(fn.body)
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Str)):
        body = body[1:]                                  # docstring 은 밖에 둔다
    if len(body) != 1 or not isinstance(body[0], ast.Try):
        return False
    return any(isinstance(h.type, ast.Name) and h.type.id == "Exception"
               for h in body[0].handlers)


def test_42_all_621_qt_entry_points_are_guarded():
    import ast
    bad = []
    for path, names in _GUARDED_621.items():
        tree = ast.parse(_src(path))
        fns = {}
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for fn in cls.body:
                if isinstance(fn, ast.FunctionDef):
                    fns["%s.%s" % (cls.name, fn.name)] = fn
        for n in names:
            if n not in fns:
                bad.append("없음 " + n)
            elif not _is_single_try_guard(fns[n]):
                bad.append("무가드 " + n)
    assert not bad, "PyQt5 는 여기서 새는 예외에 프로세스를 죽인다: %s" % bad


def test_43_guard_logs_instead_of_swallowing():
    """삼키지 않는다 — 가드는 `_qt_guard_fail` 로 태그와 함께 남긴다(계측 4원칙 ④)."""
    for path in (_CHART, _DASH):
        src = _src(path)
        assert "def _qt_guard_fail(tag, exc):" in src
        assert "exc_info=True" in src.split("def _qt_guard_fail", 1)[1][:600]
    assert "except Exception as _qe:" in _src(_DASH)


def test_44_handler_exception_does_not_escape():
    """처리기 안에서 예외가 나도 밖으로 새지 않는다(= Qt 가 abort 하지 않는다)."""
    _app()
    from dashboard.panels.option_flow_delta_chart import _Plot

    pl = _Plot(minimap=True, status=True)

    class _Bad:
        def pos(self):
            raise RuntimeError("boom")

        def angleDelta(self):
            raise RuntimeError("boom")

        def spontaneous(self):
            raise RuntimeError("boom")

    pl.set_window(60)
    pl.mouseMoveEvent(_Bad())
    pl.mousePressEvent(_Bad())
    pl.wheelEvent(_Bad())
