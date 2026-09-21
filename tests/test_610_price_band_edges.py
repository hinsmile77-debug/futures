# -*- coding: utf-8 -*-
"""[MW0601 610차] 색으로만 나뉘던 경계에 선을 긋는다 — 가격모델 50%·80% 띠.

증상 (사용자 지적 2026-09-21)
-----------------------------
「라인으로 표시한 값들은 각 라인이 있어 구분이 잘된다. 하지만 **색으로 구분한
값들의 경계는 시인성이 부족하다.**」

가격모델 50%·80% 띠는 채움 알파가 26·14 라 이웃 띠·배경과의 휘도차가 한 자리수다.
실측(2026-09-21 실 DB, 오프스크린 1400x800): 경계 10곳의 돌출이 평균 **+4.58**,
「눈에 띈다(≥10)」가 **1/10**. 어디서 끝나는지 눈이 못 잡는다.

조치
----
채움은 그대로 두고 **위·아래 변에 1px 선**을 얹는다. 결과 평균 **+43.69 · 10/10**.

그 과정에서 두 가지를 더 잡았다 — 둘 다 「고쳤는데 안 보인다」의 원인이다:
  ① **면의 농도 규칙을 선에 그대로 먹이면 안 된다.** 면은 겹치면 탁해져서 이전
     스테이지를 0.45 로 낮추지만, 선은 겹치지 않는다 — 같은 비율을 먹이면 그냥
     안 보이게만 된다(초판 실측: 08:50 변 돌출 3~4).
  ② **1px 가로선은 번지면 손해만 본다**(581차와 같은 교훈). 안티에일리어싱을 끄고
     픽셀 격자에 앉히지 않으면 같은 잉크가 두 줄로 나뉘어 봉우리가 절반이 된다.

⚠ 측정도 두 번 헛돌았다 — 픽셀 스냅으로 선이 1px 옮겨졌는데 표본 행이 고정이었고,
  점선은 x 평균이 절반으로 깎여 「안 그려졌다」처럼 보였다. 그래서 이 테스트는
  y±2 를 훑고 **행 평균과 행 최댓값을 함께** 본다.

실행: conda run -n py37_32 python -m pytest tests/test_610_price_band_edges.py
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"
# ⚠ QApplication import/생성보다 **먼저** — 순서가 바뀌면 실제 창을 띄우려다 죽는다.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QSize            # noqa: E402
from PyQt5.QtGui import QImage, QPainter  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

_APP = None

_DASH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "dashboard", "main_dashboard.py")

_W, _H = 1400, 800


def _app():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


def _canvas():
    _app()
    from dashboard.main_dashboard import MinuteChartCanvas
    return MinuteChartCanvas()


def _src():
    return open(_DASH, encoding="utf-8").read()


def _bars(n, px=1050.0, day="2026-09-21"):
    t0 = datetime.datetime(int(day[:4]), int(day[5:7]), int(day[8:10]), 9, 0)
    return [{"ts": (t0 + datetime.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
             "open": px, "high": px + 1.0, "low": px - 1.0, "close": px + 0.3,
             "volume": 10} for i in range(n)]


def _stage(stage, **kw):
    d = {"stage": stage, "dist_high": 1060.0, "dist_low": 1040.0,
         "struct_up": [], "struct_down": [], "warnings": []}
    d.update(kw)
    return d


def _render(stages):
    c = _canvas()
    c.resize(_W, _H)
    c._ov["price"] = True
    c._ov["struct"] = False        # 띠만 본다 — 구조선이 섞이면 못 잰다
    c.reset_session(_bars(60), [])
    c.set_full_session_x(True)
    c.set_premarket_levels(stages[-1], stages)
    img = QImage(QSize(_W, _H), QImage.Format_RGB32)
    p = QPainter(img)
    c.render(p)
    p.end()
    return c, img


def _lum(px):
    return (0.2126 * ((px >> 16) & 0xFF) + 0.7152 * ((px >> 8) & 0xFF)
            + 0.0722 * (px & 0xFF))


def _row(img, xs, y):
    v = [_lum(img.pixel(x, int(y))) for x in xs]
    return sum(v) / len(v), max(v)


def _edge_pop(c, img, price):
    """경계 가격의 **변 돌출** — (행 평균 돌출, 행 최대 돌출).

    바탕은 경계에서 4px 떨어진 양쪽(띠 안·밖), 변은 y±2 중 가장 밝은 행이다.
    """
    R = c._last_plot_rect
    xs = list(range(int(R.left() + R.width() * 0.45), int(R.right()) - 3, 2))
    y = c._price_to_y(price, R, c._axis_lo, c._axis_hi)
    b = [_row(img, xs, y - 4), _row(img, xs, y + 4)]
    base_m = sum(t[0] for t in b) / 2.0
    base_x = sum(t[1] for t in b) / 2.0
    cand = [_row(img, xs, y + d) for d in (-2, -1, 0, 1, 2)]
    return max(t[0] for t in cand) - base_m, max(t[1] for t in cand) - base_x


# 50% 는 80% 안에 들어간다 — 실제 데이터의 중첩 구조를 그대로 흉내낸다.
#
# ⚠ `dist_*` 를 띠보다 **넓게** 잡는다. 띠는 **의도적으로 축 계산에서 빠지므로**
#   (591차: 「80% 밴드는 축에 넣지 않는다」) 좁게 잡으면 80% 바깥 변이 축 밖으로
#   나가 축밖 가드에 걸린다 — 초판이 그래서 「변이 안 보인다」로 헛돌았다.
#   코드가 아니라 표본이 틀린 경우다.
_AXIS = {"dist_high": 1070.0, "dist_low": 1030.0}
_BANDS = {"high80_lo": 1056.0, "high80_hi": 1064.0,
          "high50_lo": 1058.0, "high50_hi": 1062.0,
          "low80_lo": 1036.0, "low80_hi": 1044.0,
          "low50_lo": 1038.0, "low50_hi": 1042.0}

_EDGE_PRICES = (1056.0, 1064.0, 1058.0, 1062.0, 1036.0, 1044.0, 1038.0, 1042.0)


# ── A. 경계가 실제로 보인다 ───────────────────────────────────────────────

def test_every_band_edge_is_visible():
    """면만으로는 경계가 안 읽힌다 — 변마다 선이 있어야 한다."""
    c, img = _render([_stage("0930", **dict(_AXIS, **_BANDS))])
    for pv in _EDGE_PRICES:
        assert not c._is_off_axis(pv), "표본이 축 밖이다 — 가드가 아니라 표본 문제다"
    weak = []
    for pv in _EDGE_PRICES:
        m, x = _edge_pop(c, img, pv)
        if x < 10.0:
            weak.append((pv, round(m, 2), round(x, 2)))
    assert not weak, "경계가 안 보이는 변: %r" % weak


def test_older_stage_edges_are_visible_too():
    """🔴 이전 스테이지 변에 면의 농도(0.45)를 그대로 먹이면 **안 보이게만** 된다.

    초판이 실제로 그랬다 — 08:50 변 돌출이 3~4 로 배경과 구분되지 않았다.
    """
    c, img = _render([_stage("0850", **dict(_AXIS, **_BANDS)),
                      _stage("0930", **_AXIS)])
    for pv in _EDGE_PRICES:
        assert not c._is_off_axis(pv), "표본이 축 밖이다 — 가드가 아니라 표본 문제다"
    weak = []
    for pv in _EDGE_PRICES:
        m, x = _edge_pop(c, img, pv)
        if x < 10.0:
            weak.append((pv, round(m, 2), round(x, 2)))
    assert not weak, "08:50 경계가 안 보인다: %r" % weak


def test_edges_beat_the_fill_step():
    """변이 채움 단차보다 뚜렷해야 「선을 넣은」 것이다."""
    from dashboard.main_dashboard import MinuteChartCanvas as MC
    assert MC.PRICE_BAND_EDGE_ALPHA["50"] > 26, "50% 채움(26)보다 진해야 한다"
    assert MC.PRICE_BAND_EDGE_ALPHA["80"] > 14, "80% 채움(14)보다 진해야 한다"
    # 점추정(255 · 실선)보다는 **뚜렷이 낮게** — 같으면 띠 경계가 값으로 읽힌다
    assert max(MC.PRICE_BAND_EDGE_ALPHA.values()) < 180, \
        "변이 점추정만큼 밝으면 「또 하나의 값」으로 읽힌다"


# ── B. 고쳤는데 안 보이게 만드는 두 함정 ──────────────────────────────────

def test_edge_dim_is_milder_than_fill_dim():
    """면은 겹치면 탁해지지만 **선은 겹치지 않는다** — 같은 비율로 낮추면 안 된다."""
    from dashboard.main_dashboard import MinuteChartCanvas as MC
    assert MC.PRE_STAGE_EDGE_DIM > MC.PRE_STAGE_DIM, \
        "변에 면의 농도 규칙을 그대로 먹이면 08:50 이 안 보인다"
    assert MC.PRE_STAGE_EDGE_DIM <= 1.0, "그래도 최신보다 진하면 안 된다"


def test_one_pixel_lines_are_snapped_and_not_antialiased():
    """1px 가로선은 번지면 잉크가 두 줄로 나뉘어 봉우리가 절반이 된다(581차)."""
    src = _src()
    i = src.index("def _draw_price_model")
    blk = src[i:i + 4500]
    assert "setRenderHint(QPainter.Antialiasing, False)" in blk
    assert "float(int(_yv)) + 0.5" in blk, "픽셀 격자에 앉히지 않으면 번진다"
    assert "painter.setRenderHint(QPainter.Antialiasing, _aa_on)" in blk, \
        "끈 채로 두면 이후 레이어가 전부 각진다"


def test_fills_are_all_drawn_before_edges():
    """50% 띠는 80% 띠 **안**에 들어간다 — 섞어 그리면 나중 채움이 앞 변을 덮는다."""
    src = _src()
    i = src.index("def _draw_price_model")
    blk = src[i:i + 4500]
    assert "_bands.append(" in blk, "채움 단계에서 변 좌표를 모아둬야 한다"
    assert blk.index("_bands.append(") < blk.index("for _k, _pt, y0, _pb, y1 in _bands:"), \
        "채움을 다 깐 뒤에 변을 그어야 한다"


# ── C. 축 밖에는 변을 긋지 않는다 ─────────────────────────────────────────

def test_no_edge_line_at_the_clamped_plot_border():
    """🔴 `_price_to_y` 는 축 밖 가격을 가장자리로 **클램프**한다.

    거기에 선을 그으면 **없는 경계를 있는 것처럼** 만든다 — 면은 잘려도
    「더 간다」로 읽히지만 선은 그 가격에 경계가 있다고 주장한다(계측 4원칙 ④).
    """
    far = {"high80_lo": 5000.0, "high80_hi": 5100.0,
           "high50_lo": 5020.0, "high50_hi": 5080.0}
    c, img = _render([_stage("0930", **far)])
    R = c._last_plot_rect
    xs = list(range(int(R.left() + R.width() * 0.45), int(R.right()) - 3, 2))
    top = max(_row(img, xs, R.top() + d)[1] for d in (1, 2, 3))
    deep = _row(img, xs, R.top() + 40)[1]
    # 변을 그었다면 알파 95~130 짜리 선이라 40 이상 튄다. 채움(≤26)만이면 한 자리수다.
    assert top - deep < 20.0, \
        "축 밖 띠인데 가장자리에 변이 그어졌다 (top=%.2f deep=%.2f)" % (top, deep)
    src = _src()
    i = src.index("for _pv, _yv in ((_pt, y0), (_pb, y1)):")
    assert "if self._is_off_axis(_pv):" in src[i:i + 300], "축 밖 가드가 없다"


# ── D. 무엇을 그은 선인지 화면이 말한다 ───────────────────────────────────

def test_legend_names_the_edges():
    """경계선을 새 레벨로 오독하지 않으려면 범례가 그것을 말해야 한다."""
    src = _src()
    i = src.index("_LEGEND_SPEC = (")
    blk = src[i:i + 900]
    assert "50%" in blk and "80%" in blk, "범례가 띠의 변을 설명하지 않는다"
