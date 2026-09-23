# -*- coding: utf-8 -*-
"""[MW0601 625차] Ctrl+Shift+X 1분봉 차트 창이 **어느 PC 화면에도 들어가는가**.

사고 (2026-09-23 MW0601)
------------------------
① 623차가 레이어 줄에 GEX 버튼 3개·GEX 문구를 붙이자 그 줄 최소 폭이 2,461px
   (S=1.40)가 됐다. 줄바꿈 없는 QLabel 은 문구 전체 폭이 곧 최소 폭이라, 창이
   주모니터(2560)에 안 들어가 가로가 화면 밖으로 나가고 줄여지지도 않았다.
② 4K 모니터로 옮겨 키우면 paintEvent 가드(3000×2000)에 걸려 **배경만 칠한 빈
   차트**가 됐다 — 가드는 있는데 그 크기로 커지는 것을 막는 장치가 없었다.

왜 S 단위로 판정하나
--------------------
UI 스케일 S 는 주모니터 크기에서 나온다(가로 기준 S ≤ 가용폭/1680). 그래서 최소 폭을
**S 단위**로 재면 해상도와 무관하다 — MW0601(QHD) 과 MW0602(구성 미기록) 어느 쪽에서
돌려도 같은 판정이 나온다. 사고 당시 그 줄은 약 1,758·S = 주모니터 가로의 105% 였다.
상한 1000·S ≈ 60%.

실행:
    conda run -n py37_32 python -m pytest tests/test_625_chart_dialog_fit.py -v
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt5.QtGui import QColor  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

import dashboard.main_dashboard as md  # noqa: E402
from dashboard.main_dashboard import MinuteChartCanvas, MinuteChartDialog  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)

_SRC = open(os.path.join(_ROOT, "dashboard", "main_dashboard.py"), encoding="utf-8").read()

# 2026-09-23 라이브 실측 문구를 **두 번** 이어 붙인다 — 앞으로 문구가 길어져도 통과해야 한다.
_OV = ("장전레벨 구조 0850 4개 · 0930 6개  (옅은 점선 = 이전 스테이지) · ⚠2"
       "  |  GEX 먼스리 4 · 목위클 4 · 월위클 4  ") * 2
_PETER = ("피터 지시 2 · 예고 1 · 거래 2 · 오프셋 -5.86 · ⚠실측 -4.00(30봉) · ⚠못읽음 3줄"
          " · ⚠레이어 꺼짐(피터맥점 · 거래피터)  ") * 2
_STATUS = ("Ctrl+Shift+X  |  휠 줌  |  드래그 이동  |  더블클릭 전체보기  |  크로스헤어"
           "  |  GP 섀도(가상) ↑GB 청 · ↓GS 적 · 청산 ⊗  |  GP 미배선  ") * 2
_BADGE = ('<span style="color:#A371F7">봉&nbsp;384+27</span>'
          + '<span>&nbsp;&nbsp;|&nbsp;&nbsp;</span>'.join(
              '<span style="color:#8B949E">%s&nbsp;미수집</span>' % n
              for n in ("레짐", "방향", "거래", "GP", "맥점", "피터")))

#: 0.80 = 하한 · 1.04 = FHD 1920×1080 · 1.40 = QHD 2560×1440(MW0601) · 2.16 = 4K 100%
_SCALES = (0.80, 1.04, 1.40, 2.16)


@pytest.fixture
def scaled():
    """S 를 바꿔 대화창을 만든다. 스타일시트가 생성 시점에 S 를 읽으므로 생성 **전에** 바꾼다."""
    made = []
    old = md.S._scale

    def _make(scale, long_text=True):
        md.S._scale = scale
        d = MinuteChartDialog()
        if long_text:
            d._ov_note.setText(_OV)
            d._peter_note.setText(_PETER)
            d._status.setText(_STATUS)
        d._layer_lbl.setText(_BADGE)
        made.append(d)
        return d

    yield _make
    md.S._scale = old
    for d in made:
        d.deleteLater()


@pytest.mark.parametrize("scale", _SCALES)
def test_1_min_width_within_budget(scaled, scale):
    """최소 폭 ≤ 1000·S — 가로 기준 주모니터의 약 60%. 레이어 버튼을 더 붙이면 여기서 깨진다."""
    d = scaled(scale)
    min_w = d.minimumSizeHint().width()
    budget = MinuteChartDialog.MIN_WIDTH_BUDGET_S * scale
    assert min_w <= budget, (
        "S=%.2f 최소 폭 %dpx > 예산 %dpx(1000·S) — 창이 주모니터에 안 들어갈 수 있다. "
        "레이어 줄에 무엇을 붙였는지 확인할 것(623차 사고)." % (scale, min_w, budget))


@pytest.mark.parametrize("scale", (1.04, 1.40))
def test_2_long_notes_do_not_widen_window(scaled, scale):
    """문구 길이가 창 최소 폭을 바꾸지 않는다 — 사고의 기전 자체를 고정한다."""
    short = scaled(scale, long_text=False).minimumSizeHint().width()
    long_ = scaled(scale, long_text=True).minimumSizeHint().width()
    assert long_ == short, "문구가 최소 폭을 %d→%dpx 로 늘렸다" % (short, long_)


def test_3_notes_are_not_on_button_row():
    """두 문구는 버튼 줄이 아니라 별도(줄바꿈) 줄에 있다."""
    body = _SRC.split("def _build_overlay_bar", 1)[1].split("\n    def ", 1)[0]
    assert "bar.addWidget(self._ov_note" not in body
    assert "bar.addWidget(self._peter_note" not in body
    d = MinuteChartDialog()
    for lbl in (d._ov_note, d._peter_note, d._status, d._layer_lbl):
        assert lbl.wordWrap()
        assert lbl.sizePolicy().horizontalPolicy() == md.QSizePolicy.Ignored
    d.deleteLater()


def test_4_max_size_equals_paint_guard():
    """캔버스 최대 크기 = 그리기 가드 — 가드에 걸리는 크기로는 애초에 못 커진다."""
    d = MinuteChartDialog()
    c = d._chart
    assert (c.maximumWidth(), c.maximumHeight()) == (MinuteChartCanvas.MAX_W,
                                                     MinuteChartCanvas.MAX_H)
    m = d.layout().contentsMargins()
    assert d.maximumWidth() == MinuteChartCanvas.MAX_W + m.left() + m.right()
    d.deleteLater()
    # 가드는 상수를 읽는다 — 숫자를 따로 적으면 둘이 어긋난다
    paint = _SRC.split("class MinuteChartCanvas", 1)[1].split("def paintEvent", 1)[1][:2500]
    assert "self.MAX_W" in paint and "self.MAX_H" in paint
    assert "width() > 3000" not in paint


def test_5_oversize_draws_notice_not_blank():
    """가드에 걸리면 빈 배경이 아니라 사유 문구를 그린다(계측 4원칙 ④)."""
    c = MinuteChartCanvas()
    c.setMaximumSize(16777215, 16777215)   # F2 를 일부러 우회 — 창 관리자가 넘긴 상황
    c.resize(MinuteChartCanvas.MAX_W + 200, 600)
    assert "한계 3000×2000" in c.oversize_notice_text()
    img = c.grab().toImage()
    bg = QColor(md.C["bg"]).rgb()
    non_bg = sum(1 for x in range(0, img.width(), 7) for y in range(0, img.height(), 3)
                 if img.pixel(x, y) != bg)
    assert non_bg > 0, "가드가 배경만 칠했다 — 2026-09-23 증상 그대로"
    c.deleteLater()


def test_6_size_verdict_consistent():
    """F4 판정 — MW0602 원격 검증용 한 줄이 필요한 값을 다 담고, 판정이 값과 일치한다."""
    d = MinuteChartDialog()
    v = d.size_fit_verdict()
    for k in ("scale", "min_w", "min_h", "max_w", "avail_w", "avail_h", "screen", "fits"):
        assert k in v
    assert v["fits"] == (v["min_w"] <= v["avail_w"] and v["min_h"] <= v["avail_h"])
    d.deleteLater()


def test_7_after_show_is_guarded_and_wired():
    """after_show 는 Qt 진입점이다 — 예외가 새면 PyQt5 가 프로세스를 죽인다(617차)."""
    body = _SRC.split("    def after_show", 1)[1].split("\n    def ", 1)[0]
    assert "_qt_guard_fail('MinuteChartDialog.after_show'" in body
    assert "restore_saved_geometry()" in body and "_log_size_verdict()" in body
    tog = _SRC.split("def toggle_minute_chart_dialog", 1)[1].split("\n    def ", 1)[0]
    assert "singleShot(0, self._minute_chart_dialog.after_show)" in tog
