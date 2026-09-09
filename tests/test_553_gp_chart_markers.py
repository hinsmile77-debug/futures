# -*- coding: utf-8 -*-
"""[MW0601 553차 / Phase 0] Ctrl+Shift+X 차트의 **GP 규칙 섀도 마커**가 실제로 그려지는가.

왜 렌더링까지 검사하나
----------------------
이 프로젝트가 반복해서 당한 사고는 **「배선했는데 아무도 소비하지 않는 것」** 이다:
FP-CRITICAL 은 학습분포 저장 함수가 호출된 적이 없어 2개월간 PSI=0.0 이었고,
TOX-SEVERE-SPREAD 는 `spread_extreme_shadow` 를 매분 계산하고도 한 달 넘게
아무 데도 남기지 않았다. GP 마커도 **Phase 3 이전에는 데이터가 0건**이라
"안 그려지는 것"과 "못 그리는 것"이 구분되지 않는다.

그래서 합성 GP 거래를 넣고 **픽셀이 실제로 찍히는지** 확인한다.

무엇을 고정하나
---------------
1. 합성 GP 거래를 주면 GP 색이 캔버스에 실제로 나타난다.
2. GP 를 안 주면 그 색이 **나타나지 않는다**(색이 다른 데서 새어 나오지 않는지 대조).
3. 실측(`_completed_trades`)과 **색이 겹치지 않는다** — 가상·실측 구분이 시각 언어다.
4. 「미배선」 · 「0건」 · 「n건」이 서로 다른 문구로 나온다(계측 4원칙 ②).
5. 청산 미기록 거래(보유 중)를 줘도 죽지 않고, 진입만 그린다.

실행:
    conda run -n py37_32 python -m pytest tests/test_553_gp_chart_markers.py -v
"""
import os
import sys
from datetime import datetime, timedelta

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
# ⚠ QApplication 생성보다 **먼저** offscreen 을 세운다(493차 관례).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt5.QtGui import QColor, QPixmap  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

from dashboard.main_dashboard import MinuteChartCanvas, MinuteChartDialog  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)

_BASE = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)


def _candles(n=40, price=350.0):
    rows = []
    for i in range(n):
        ts = (_BASE + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:00")
        c = price + (i % 5) * 0.1
        rows.append({"ts": ts, "open": c, "high": c + 0.3,
                     "low": c - 0.3, "close": c, "volume": 100})
    return rows


def _gp_trade(direction="LONG", entry_i=5, exit_i=25, pnl=1.25, closed=True):
    return {
        "challenger_id": "GP_LONG_GB90" if direction == "LONG" else "GP_SHORT_SQZ60",
        "entry_ts": (_BASE + timedelta(minutes=entry_i)).strftime("%Y-%m-%d %H:%M:00"),
        "exit_ts": ((_BASE + timedelta(minutes=exit_i)).strftime("%Y-%m-%d %H:%M:00")
                    if closed else None),
        "direction": direction,
        "entry_price": 350.0,
        "exit_price": 351.25 if closed else 0.0,
        "pnl_pt": pnl if closed else None,
        "exit_reason": "TIME_90M" if closed else "",
    }


def _render(canvas):
    canvas.resize(900, 500)
    pm = QPixmap(canvas.size())
    canvas.render(pm)
    return pm.toImage()


def _color_present(img, hex_color, tol=26):
    """해당 색이 이미지에 나타나는가. 안티에일리어싱을 감안해 근사 매칭."""
    want = QColor(hex_color)
    step = 2  # 900x500 전수는 느리다 — 격자 샘플링으로 충분하다
    for x in range(0, img.width(), step):
        for y in range(0, img.height(), step):
            px = QColor(img.pixel(x, y))
            if (abs(px.red() - want.red()) <= tol
                    and abs(px.green() - want.green()) <= tol
                    and abs(px.blue() - want.blue()) <= tol):
                return True
    return False


# ── 렌더링 ───────────────────────────────────────────────────────────────────

def test_gp_long_marker_is_actually_painted():
    canvas = MinuteChartCanvas()
    canvas.reset_session(_candles(), [], gp_trades=[_gp_trade("LONG")], gp_wired=True)
    assert _color_present(_render(canvas), MinuteChartCanvas.GP_LONG_COLOR), (
        "GP 롱 마커가 캔버스에 나타나지 않는다 — 배선만 되고 그려지지 않는 상태다.")


def test_gp_short_marker_is_actually_painted():
    canvas = MinuteChartCanvas()
    canvas.reset_session(_candles(), [], gp_trades=[_gp_trade("SHORT")], gp_wired=True)
    assert _color_present(_render(canvas), MinuteChartCanvas.GP_SHORT_COLOR)


def test_no_gp_color_when_no_gp_trades():
    """대조군 — GP 색이 다른 요소에서 새어 나오면 위 두 검사가 무의미해진다."""
    canvas = MinuteChartCanvas()
    canvas.reset_session(_candles(), [], gp_trades=[], gp_wired=True)
    img = _render(canvas)
    assert not _color_present(img, MinuteChartCanvas.GP_LONG_COLOR)
    assert not _color_present(img, MinuteChartCanvas.GP_SHORT_COLOR)


def test_open_gp_leg_renders_without_exit():
    """청산 미기록 = 보유 중. 죽지 않고 진입만 그린다(손익 0으로 위장하지 않는다)."""
    canvas = MinuteChartCanvas()
    canvas.reset_session(_candles(), [],
                         gp_trades=[_gp_trade("LONG", closed=False)], gp_wired=True)
    assert _color_present(_render(canvas), MinuteChartCanvas.GP_LONG_COLOR)


def test_gp_colors_do_not_collide_with_live_trade_colors():
    """🔴 가상과 실측은 **색 축이 달라야** 한다. 겹치면 화면이 거짓말한다."""
    live = {"#2FBF71", "#FF5D73", "#8B949E"}   # _draw_trade_spans 의 실측 색
    gp = {MinuteChartCanvas.GP_LONG_COLOR.upper(),
          MinuteChartCanvas.GP_SHORT_COLOR.upper()}
    assert not (gp & {c.upper() for c in live})


def test_gp_is_drawn_before_live_markers():
    """겹칠 때 실측이 위로 와야 한다 — paintEvent 호출 순서로 고정한다."""
    import inspect
    src = inspect.getsource(MinuteChartCanvas.paintEvent)
    assert src.index("_draw_gp_layer") < src.index("self._draw_markers("), (
        "GP 레이어가 실측 마커보다 뒤에 그려진다 — 가상이 실측을 덮는다.")


# ── 상태 문구: 미배선 ≠ 0건 ──────────────────────────────────────────────────

@pytest.mark.parametrize("trades,wired,expect", [
    ([], False, "GP 미배선"),
    ([], True, "GP 0건"),
    ([_gp_trade("LONG")], True, "GP 1건"),
])
def test_status_text_separates_unwired_from_zero(trades, wired, expect):
    """계측 4원칙 ② — 「측정 안 함」과 「측정했더니 0」을 같은 문구로 쓰지 않는다."""
    assert MinuteChartDialog._gp_status_text(None, trades, wired) == expect


def test_status_text_shows_open_legs():
    txt = MinuteChartDialog._gp_status_text(
        None, [_gp_trade("LONG"), _gp_trade("SHORT", closed=False)], True)
    assert txt == "GP 2건 (보유 1)"


# ── 로더 계약 ────────────────────────────────────────────────────────────────

def test_loader_uses_challenger_db_not_trades_db():
    """🔴 GP 를 `trades` 에서 읽으면 실거래와 섞인다(검토문서 §5-4)."""
    import inspect
    src = inspect.getsource(MinuteChartDialog._load_gp_trades)
    assert "CHALLENGER_DB" in src
    assert "TRADES_DB" not in src and "FROM trades" not in src


def test_loader_ids_come_from_preregistration():
    """도전자 ID 를 하드코딩하면 사전등록과 갈린다."""
    import inspect
    src = inspect.getsource(MinuteChartDialog._load_gp_trades)
    assert "gp_rule_challenger_ids" in src
    assert "GP_LONG_GB90" not in src, "ID 사본은 드리프트한다 — 사전등록에서 읽을 것"


def test_loader_is_safe_before_phase3():
    """Phase 3 이전(테이블·행 없음)에도 예외 없이 (빈목록, False) 를 준다."""
    trades, wired = MinuteChartDialog._load_gp_trades("1999-01-01")
    assert trades == []
    assert wired is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
