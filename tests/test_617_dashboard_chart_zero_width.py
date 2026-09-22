# -*- coding: utf-8 -*-
"""[MW0601 617차] 표시 위젯이 **매매 엔진을 죽이지 못하게** 하는 불변식.

무엇이 일어났나 (2026-09-22 09:41:56)
-------------------------------------
미륵이가 장중에 즉사했다. 런처가 10초 뒤 재기동해 09:43:16 에 복구됐지만
**다운 31초 · 분봉 2개(ts=09:41·09:42) 파이프라인 결손**이 남았다.
실손해가 0이었던 것은 그날 09:30:01 `JointGateBlock` 차단으로 **우연히
FLAT 이었기 때문**이다 — 480차(08-19 동결)와 같은 계열이다.

    File "dashboard/panels/direction_indicator_dialog.py", line 490, in _draw_chart
      ...matplotlib/transforms.py:1890 in inverted
    numpy.linalg.LinAlgError: Singular matrix

인과
----
1. `transData = transScale + (transLimits + transAxes)` 의 역행렬은
   `transAxes = BboxTransformTo(ax.bbox)` 부터 깐다. **`ax.bbox` 폭이 0이면
   그 행렬은 특이(singular)** 다.
2. 캔버스에는 `setMinimumHeight(180)` **만** 있었다 — 최소 폭이 없었다.
   좌측 컬럼이 든 `main_split` 은 `setChildrenCollapsible(False)` 를 부른 적이
   없어(기본 True) 핸들을 끝까지 끌면 폭 0 이 된다.
3. 폭 0 일 때 같은 함수의 `axvline` 은 통과하고 `axhline` 만 터진다(실측).
   `axhline` 은 `direction != 0` 일 때만 그려서 희소했다.
4. `_refresh` 는 QTimer 슬롯이다. **PyQt5(5.15.10)는 슬롯 안의 미처리 예외에서
   `qFatal()` 로 프로세스를 abort** 한다. `sys.excepthook` 로는 못 막는다.

이 파일이 고정하는 것 — 세 겹 전부
-----------------------------------
A. 슬롯(`_refresh`·`_flash_tick`)과 `_draw_chart` 가 **예외를 밖으로 내지 않는다**
B. 캔버스 최소 폭 · 스플리터 접힘 금지 (원인 제거)
C. 폭/높이가 0 이면 그리기를 건너뛴다 (A·B 가 뚫려도 서는 마지막 문)

⚠ **"차트가 안 그려지는 것"은 이 테스트의 관심사가 아니다.** 여기서 재는 것은
오직 **엔진이 사는가**다. 표시가 비는 것은 허용되고, 죽는 것은 허용되지 않는다.

실행:
    conda run -n py37_32 python -m pytest tests/test_617_dashboard_chart_zero_width.py -q
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

pytest.importorskip("PyQt5")
pytest.importorskip("matplotlib")


@pytest.fixture(scope="module")
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _candles(n=57, base=1135.0):
    return [
        {
            "ts":    "2026-09-22 09:%02d:00" % (i % 60),
            "open":  base + i * 0.01,
            "high":  base + i * 0.01 + 0.3,
            "low":   base + i * 0.01 - 0.3,
            "close": base + i * 0.01 + 0.1,
        }
        for i in range(n)
    ]


def _widget(app):
    from dashboard.panels.direction_indicator_dialog import DirectionIndicatorWidget
    w = DirectionIndicatorWidget()
    w.resize(290, 600)
    w.show()
    app.processEvents()
    return w


# ── A. 폭 0 에서도 죽지 않는다 (사고 재현 경로) ────────────────────────────

@pytest.mark.parametrize("direction", [1, -1, 0])
def test_draw_chart_survives_zero_width(app, direction):
    """사고 당시와 같은 상태 — 캔버스 폭 0 + 방향 표시.

    617차 이전에는 `direction != 0` 에서 `LinAlgError` 가 **밖으로 나가** 프로세스가
    죽었다. 지금은 조용히 건너뛰어야 한다.
    """
    w = _widget(app)
    w._canvas.resize(0, 600)          # 좌측 컬럼 접힘과 같은 상태
    app.processEvents()
    w._draw_chart(_candles(), direction, "#3fb950")   # 예외가 나오면 실패


@pytest.mark.parametrize("size", [(0, 0), (0, 600), (290, 0), (1, 1)])
def test_draw_chart_survives_degenerate_sizes(app, size):
    w = _widget(app)
    w._canvas.resize(*size)
    app.processEvents()
    w._draw_chart(_candles(), 1, "#3fb950")


def test_refresh_slot_never_raises(app, monkeypatch):
    """QTimer 슬롯은 무슨 일이 있어도 예외를 밖으로 내지 않는다.

    DB·그리기 어느 쪽이 터지든 마찬가지다 — PyQt5 는 슬롯에서 새어나온 예외를
    `qFatal()` 로 처리하므로 **예외 종류를 가릴 여지가 없다.**
    """
    w = _widget(app)

    def boom(*_a, **_k):
        raise RuntimeError("의도적 폭발 — 슬롯 밖으로 새면 안 된다")

    monkeypatch.setattr(w, "_fetch_candles", boom)
    w._refresh()

    monkeypatch.undo()
    monkeypatch.setattr(w, "_draw_chart_impl", boom)
    w._refresh()


def test_flash_tick_slot_never_raises(app, monkeypatch):
    w = _widget(app)
    monkeypatch.setattr(w, "_set_lamp_style",
                        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")))
    w._flash_count = 3
    w._flash_tick()


def test_failure_is_logged_not_swallowed_silently(app, caplog, monkeypatch):
    """삼키되 숨기지 않는다 — 계측 4원칙 ④(폴백 가시화).

    10초 폴링이라 매번 찍으면 로그가 잠긴다. 첫 1회는 반드시 남아야 한다.
    """
    import logging
    w = _widget(app)
    monkeypatch.setattr(w, "_draw_chart_impl",
                        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")))
    w._draw_fail_n = 0
    with caplog.at_level(logging.WARNING,
                         logger="dashboard.panels.direction_indicator_dialog"):
        w._draw_chart(_candles(), 1, "#3fb950")
    assert any("DirIndicator" in r.getMessage() for r in caplog.records), \
        "실패가 로그에 남지 않으면 죽은 게이트와 구분되지 않는다"


# ── B. 원인 제거 — 최소 폭 · 접힘 금지 ─────────────────────────────────────

def test_canvas_has_minimum_width(app):
    """높이만 막혀 있었던 것이 사고의 절반이다."""
    w = _widget(app)
    assert w._canvas.minimumWidth() > 0, \
        "캔버스 최소 폭이 0이면 스플리터가 폭 0 으로 접을 수 있다"
    assert w._canvas.minimumHeight() > 0


def test_splitters_are_not_collapsible():
    """`main_split`·`left_split` 은 접힘 금지여야 한다.

    대시보드 전체를 import 하면 무거우므로 소스에서 확인한다 —
    그 두 스플리터가 사고 경로에 있던 바로 그 객체다.
    """
    src = open(os.path.join(ROOT, "dashboard", "main_dashboard.py"),
               encoding="utf-8").read()
    for name in ("main_split", "left_split"):
        assert "%s.setChildrenCollapsible(False)" % name in src, (
            "%s 가 접힘 허용 상태다 — 컬럼을 폭 0 으로 접으면 "
            "matplotlib 캔버스가 특이행렬을 만든다" % name
        )


# ── C. 음성 대조 — 가드가 **일하고 있다**는 증거 ───────────────────────────

def test_guard_is_what_saves_us_not_luck(app):
    """가드를 우회하면 **여전히 죽는다** — 살아 있는 것은 운이 아니라 가드다.

    사고를 만든 물리량은 Qt 위젯 폭이 아니라 **matplotlib figure 폭**이다.
    `FigureCanvasQT.resizeEvent` 가 폭 0 을 받으면 `set_size_inches(0, …)` 를
    부르고, 그때 `ax.bbox` 폭이 0 이 되어 `transAxes` 가 특이해진다.
    여기서는 그 호출을 그대로 재현한다.

    `_draw_chart_impl`(가드 우회)이 통과하기 시작하면 matplotlib 쪽이 바뀐
    것이므로 이 파일의 전제를 다시 읽어야 한다.
    """
    import numpy as np
    w = _widget(app)

    w._fig.set_size_inches(0.0, 1.8, forward=False)   # resizeEvent(width=0) 과 동일
    assert w._ax.bbox.width == 0, "전제 재현 실패 — ax.bbox 폭이 0이 아니다"

    with pytest.raises(np.linalg.LinAlgError):         # 가드 우회 — 여전히 죽는다
        w._draw_chart_impl(_candles(), 1, "#3fb950")

    w._draw_chart(_candles(), 1, "#3fb950")            # 가드 경유 — 살아야 한다


def test_splitter_collapse_no_longer_reaches_zero(app):
    """원인 제거(B)가 스플리터 경로를 실제로 막는지 — 접힘을 허용해도 0 이 안 된다."""
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QWidget
    from dashboard.panels.direction_indicator_dialog import (
        _CANVAS_MIN_W, DirectionIndicatorWidget)

    sp = QSplitter(Qt.Horizontal)
    left = QWidget()
    ll = QVBoxLayout(left)
    ll.setContentsMargins(0, 0, 0, 0)
    w = DirectionIndicatorWidget()
    ll.addWidget(w)
    sp.addWidget(left)
    sp.addWidget(QWidget())
    sp.resize(1000, 800)
    sp.show()
    app.processEvents()

    sp.setChildrenCollapsible(True)      # 일부러 사고 당시 설정으로 되돌려도
    sp.setSizes([0, 1000])
    app.processEvents()

    assert w._canvas.width() >= _CANVAS_MIN_W, (
        "캔버스 최소 폭이 스플리터 접힘을 막지 못한다 — 폭 %d"
        % w._canvas.width()
    )
    w._draw_chart(_candles(), 1, "#3fb950")


# ── D. 형제 화면 — 봉차트 팝업도 같은 결함이었다 ───────────────────────────

def test_candle_chart_dialog_survives_zero_width(app):
    """`candle_chart_dialog` 도 높이만 막혀 있었고 슬롯도 무가드였다.

    여기서는 위젯 폭이 아니라 **figure 폭**만 0 이 된 상태를 만든다 — 실제로
    가드가 걸리는 지점은 `ax.bbox` 검사다(위젯 폭은 640 그대로다).
    축이 셋이라 셋 다 봐야 한다.
    """
    from dashboard.panels.candle_chart_dialog import CandleChartDialog
    d = CandleChartDialog(parent=None)
    app.processEvents()

    assert d._canvas.minimumWidth() > 0

    d._fig.set_size_inches(0.0, 2.7, forward=False)
    assert d._ax.bbox.width == 0

    d._draw_chart(_candles(), 1, "#3fb950", {})    # 예외가 나오면 실패
    d._apply(_candles(), None, {}, {})             # 워커 완료 슬롯도 마찬가지

    try:
        if d._worker is not None:
            d._worker.wait(2000)
    except Exception:
        pass
