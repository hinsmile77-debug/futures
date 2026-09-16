# -*- coding: utf-8 -*-
"""[MW0601 593차] 「피터맥점」·「거래피터」 토글이 **자기 것만** 지우는가.

무엇이 무너졌었나
-----------------
피터 라벨은 캔들 뒤에 찍어야 해서(584차) 생산자가 큐에 쌓아두고 2차 패스가
소비한다. 생산자(`_draw_peter_orders`/`_draw_peter_trades`)는 `_ov` 를 보는데
소비자(`_draw_peter_order_labels`/`_draw_peter_labels`)는 **보지 않았다**.
레이어를 끄면 생산자는 즉시 빠져나가고 큐에는 **지난 paint 의 라벨이 남아**
소비자가 그걸 계속 찍었다 — 실측 2026-09-16:

  · 「거래피터」 OFF 인데 `+10.00p 피터리` · `LONG 09:00→09:32 · 익절` 이 남음
  · 「피터맥점」 OFF 인데 `⏱09:00 △돌파매수 1035` · `손절 1032` 가 남음

선은 사라지는데 라벨만 남아 화면이 거짓말을 했다.

왜 **연속 렌더**로 잡나
----------------------
이건 상태가 남는 버그다. OFF 만 단독으로 그리면 큐가 애초에 빈 채라 **통과해
버린다.** 반드시 `(ON,ON)` 을 먼저 그린 **직후** 끈 상태를 그려야 재현된다.
1·2번 검사가 이 순서를 고정한다 — 순서를 없애면 검사가 무의미해진다.

왜 색은 `#BC8CFF` 하나만 쓰나
-----------------------------
피터맥점 전용 색이라 다른 레이어에서 샐 수 없다. 거래피터 라벨은 테두리가
손익색(`#3FB950`/`#F85149`)이라 실측 거래·GP 와 겹치므로 **색으로 판정하면
거짓양성이 난다** — 그쪽은 큐 상태로 판정한다(계측 4원칙 ②: 못 재는 걸
재는 척하지 않는다).

실행:
    conda run -n py37_32 python -m pytest tests/test_593_peter_layer_isolation.py -v
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

from PyQt5.QtGui import QColor, QPixmap  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

from dashboard.main_dashboard import MinuteChartCanvas  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)

_BASE = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
_ORDER_COLOR = "#BC8CFF"          # 피터 지시 앵커·칩 테두리 전용색


def _ts(i):
    return (_BASE + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:00")


def _candles(n=40, price=350.0):
    rows = []
    for i in range(n):
        c = price + (i % 5) * 0.1
        rows.append({"ts": _ts(i), "open": c, "high": c + 0.3,
                     "low": c - 0.3, "close": c, "volume": 100})
    return rows


def _peter_order():
    """지시 1건 — 09:00 돌파매수. 값은 캔들 범위 안이어야 화면에 들어온다."""
    return {"raw": "354.5 돌파시 매수 손절가 353.9", "hm": "10:05", "other_day": False,
            "kind": "entry_brk", "side": "L", "entry": 350.5, "entry_raw": 354.5,
            "stop": 349.9, "target": 350.65, "tag": "", "ts": _ts(5)}


def _peter_trade():
    return {"entry_hm": "10:05", "direction": "LONG", "entry_price": 350.2,
            "exit_hm": "10:25", "exit_price": 350.6, "open": False, "why": "익절",
            "entry_ts": _ts(5), "exit_ts": _ts(25)}


def _peter_levels():
    return [{"kind": "entry_brk", "level": 354.5, "level_adj": 350.5, "at": 0},
            {"kind": "stop", "level": 353.9, "level_adj": 349.9, "at": 10},
            {"kind": "target", "level": 354.65, "level_adj": 350.65, "at": 20}]


def _canvas():
    c = MinuteChartCanvas()
    c.resize(900, 500)
    c.reset_session(_candles(), [])
    c.set_peter(_peter_levels(), [_peter_trade()], [_peter_order()])
    return c


def _render(canvas, peter_lv, trade_peter):
    canvas.set_overlay("peter_lv", peter_lv)
    canvas.set_overlay("trade_peter", trade_peter)
    pm = QPixmap(canvas.size())
    canvas.render(pm)
    return pm.toImage()


def _color_present(img, hex_color, tol=26):
    want = QColor(hex_color)
    step = 2                      # 900x500 전수는 느리다 — 격자 샘플링으로 충분하다
    for x in range(0, img.width(), step):
        for y in range(0, img.height(), step):
            px = QColor(img.pixel(x, y))
            if (abs(px.red() - want.red()) <= tol
                    and abs(px.green() - want.green()) <= tol
                    and abs(px.blue() - want.blue()) <= tol):
                return True
    return False


# ── ① 잔상 — 이 버그의 본체. 반드시 연속 렌더로 잡는다 ──────────────────────

def test_order_labels_vanish_right_after_being_drawn():
    """「피터맥점」을 끄면 **직전 paint 의 지시 칩**까지 사라져야 한다."""
    c = _canvas()
    assert _color_present(_render(c, True, True), _ORDER_COLOR), (
        "지시 레이어가 켜졌는데 전용색이 안 나온다 — 검사 전제가 무너졌다.")
    img = _render(c, False, True)          # ← 켠 직후 끈다
    assert not _color_present(img, _ORDER_COLOR), (
        "「피터맥점」을 껐는데 지시 칩이 남았다 — 2차 패스 큐 잔상(593차 재발).")
    assert c._peter_order_labels == [], "지시 라벨 큐가 안 비었다."
    assert c._peter_aux_labels == [], "[594차] 예고 라벨 큐가 안 비었다."


def test_trade_labels_vanish_right_after_being_drawn():
    """「거래피터」를 끄면 **직전 paint 의 손익 칩**까지 사라져야 한다."""
    c = _canvas()
    _render(c, True, True)
    assert c._peter_label_q, "거래 레이어가 켜졌는데 라벨 큐가 비었다 — 전제가 무너졌다."
    _render(c, True, False)                # ← 켠 직후 끈다
    assert c._peter_label_q == [], (
        "「거래피터」를 껐는데 거래 라벨 큐가 남았다 — 잔상이 찍힌다(593차 재발).")


# ── ② 레이어 독립 — 한쪽을 꺼도 다른 쪽은 멀쩡해야 한다 ─────────────────────

def test_each_layer_owns_only_its_own_labels():
    c = _canvas()
    _render(c, True, True)
    _render(c, True, False)                # 피터맥점만
    assert c._peter_order_labels, "피터맥점만 켰는데 지시 라벨이 없다."
    assert c._peter_label_q == [], "피터맥점만 켰는데 거래 라벨이 남았다."
    _render(c, False, True)                # 거래피터만
    assert c._peter_label_q, "거래피터만 켰는데 거래 라벨이 없다."
    assert c._peter_order_labels == [], "거래피터만 켰는데 지시 라벨이 남았다."


def test_both_off_leaves_nothing():
    c = _canvas()
    _render(c, True, True)
    img = _render(c, False, False)
    assert not _color_present(img, _ORDER_COLOR)
    assert c._peter_label_q == [] and c._peter_order_labels == []
    assert c._peter_aux_labels == [], "[594차] 예고 라벨 큐가 안 비었다."


def test_both_on_still_draws_both():
    """반대편 확인 — 고치면서 통째로 꺼버리지 않았는가."""
    c = _canvas()
    img = _render(c, True, True)
    assert _color_present(img, _ORDER_COLOR)
    assert c._peter_label_q and c._peter_order_labels


# ── ③ 날짜를 갈아끼워도 지난 날 라벨을 들고 있지 않는다 ─────────────────────

def test_set_peter_drops_previous_day_labels():
    c = _canvas()
    _render(c, True, True)
    c.set_peter([], [], [])                # 사료 없는 날로 이동
    assert c._peter_label_q == [] and c._peter_order_labels == [], (
        "날짜를 바꿨는데 지난 날 라벨 큐가 남았다.")
    assert not _color_present(_render(c, True, True), _ORDER_COLOR)


# ── ④ 불변식을 코드로 못 박는다 ─────────────────────────────────────────────

def test_label_consumers_check_the_overlay_flag():
    """소비자가 `_ov` 를 보지 않으면 잔상은 언제든 되돌아온다."""
    import inspect
    for fn, key in ((MinuteChartCanvas._draw_peter_labels, "trade_peter"),
                    (MinuteChartCanvas._draw_peter_order_labels, "peter_lv")):
        src = inspect.getsource(fn)
        assert key in src, "%s 가 '%s' 오버레이를 확인하지 않는다." % (fn.__name__, key)


def test_paint_event_clears_queues_before_producers_run():
    """입구에서 비우지 않으면 생산자의 다른 이탈 경로(0건·예외)로 잔상이 샌다."""
    import inspect
    src = inspect.getsource(MinuteChartCanvas.paintEvent)
    assert "self._peter_label_q = []" in src and "self._peter_order_labels = []" in src
    assert "self._peter_aux_labels = []" in src, "[594차] 예고 큐도 입구에서 비워야 한다."
    assert src.index("self._peter_order_labels = []") < src.index("self._draw_peter_orders("), (
        "큐 비우기가 생산자보다 뒤에 있다 — 매 paint 마다 자기 결과를 지운다.")
