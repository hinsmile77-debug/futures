# -*- coding: utf-8 -*-
"""[MW0601 590차] 1분봉 차트 하단 이동바 + 그것이 드러낸 시야 결함 2건.

배경
----
휠 줌·드래그 패닝은 590차 이전에도 있었다. 없던 것은 **「지금 하루 중 어디를
보고 있는가」** 였다(411봉 중 40봉을 봐도 위치 표시가 하나도 없었다).

이동바를 달려고 코드를 읽다가 독립 결함 2건이 드러났다. 둘 다 이동바가
만든 문제가 아니라, 이동바가 **보이게 만든** 문제다:

  A) `_view_offset` 은 「오른쪽 끝에서 몇 봉을 숨겼나」다. 새 봉이 와서 total 이
     늘면 같은 offset 이 가리키는 **절대 구간이 앞으로 밀린다** — 과거를 확대해
     보고 있으면 1분마다 화면이 미끄러졌다.
  B) `reset_session()` 이 리로드마다 줌을 전체보기로 되돌렸다. 리로드 트리거에는
     589차가 넣은 **15:46 마감구간 보충 후 자동 리로드**가 포함되므로, 확대해서
     보고 있으면 하루에 한 번 확대가 말없이 풀렸다.

정책(사용자 결정 2026-09-16): **과거를 보는 중이면 고정, 맨 오른쪽이면 따라간다.**

실행: conda run -n py37_32 python -m pytest tests/test_590_chart_nav_bar.py
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"
# ⚠ QApplication import/생성보다 **먼저** — 순서가 바뀌면 실제 창을 띄우려다 죽는다.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication  # noqa: E402

_APP = None


def _app():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


def _canvas():
    _app()
    from dashboard.main_dashboard import MinuteChartCanvas
    return MinuteChartCanvas()


def _bars(n, day="2026-09-16", start=(9, 0)):
    t0 = datetime.datetime(int(day[:4]), int(day[5:7]), int(day[8:10]), *start)
    out = []
    for i in range(n):
        t = t0 + datetime.timedelta(minutes=i)
        out.append({"ts": t.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": 1000.0, "high": 1001.0, "low": 999.0,
                    "close": 1000.5, "volume": 10})
    return out


def _window(c):
    """현재 화면에 보이는 절대 구간 (start_idx, end_idx) — paintEvent 와 같은 식."""
    total = c._view_total()
    visible = c._view_visible(total)
    end = total - c._view_offset
    return max(0, end - visible), end


# ── A. 새 봉이 와도 보던 구간이 안 밀린다 ───────────────────────────────────

def test_anchors_when_looking_at_history():
    c = _canvas()
    c.reset_session(_bars(200), [])
    c._visible_count = 40
    c._view_offset = 100                     # 과거를 보는 중
    before = _window(c)
    assert before == (60, 100)

    c.on_candle_closed({"ts": "2026-09-16 12:20:00", "open": 1000.0, "high": 1001.0,
                        "low": 999.0, "close": 1000.5, "volume": 10})

    assert _window(c) == before, "과거를 보는 중인데 새 봉 때문에 구간이 밀렸다"
    assert c._view_offset == 101, "total 이 1 늘었으면 offset 도 1 늘어야 절대 구간이 고정된다"


def test_follows_latest_when_at_right_edge():
    c = _canvas()
    c.reset_session(_bars(200), [])
    c._visible_count = 40
    c._view_offset = 0                       # 맨 오른쪽 — 실시간 감시
    c.on_candle_closed({"ts": "2026-09-16 12:20:00", "open": 1000.0, "high": 1001.0,
                        "low": 999.0, "close": 1000.5, "volume": 10})
    assert c._view_offset == 0, "맨 오른쪽에서는 최신 봉을 따라가야 한다"
    assert _window(c)[1] == c._view_total(), "오른쪽 끝이 최신 봉이어야 한다"


def test_live_candle_creation_also_anchors():
    """진행 중 봉이 새로 생길 때도 total 이 는다 — 확정 봉만 막으면 반쪽이다."""
    c = _canvas()
    c.reset_session(_bars(200), [])
    c._visible_count = 40
    c._view_offset = 100
    before = _window(c)
    c.update_tick(1000.5, "2026-09-16 12:20:30")     # 새 진행 중 봉
    assert c._live_candle is not None
    assert _window(c) == before, "진행 중 봉이 생기면서 구간이 밀렸다"


def test_tick_on_existing_bar_does_not_shift():
    """같은 분에 틱이 더 와도 total 은 안 는다 — offset 을 건드리면 안 된다."""
    c = _canvas()
    c.reset_session(_bars(200), [])
    c._visible_count = 40
    c._view_offset = 100
    c.update_tick(1000.5, "2026-09-16 12:20:30")
    off1 = c._view_offset
    for _ in range(5):
        c.update_tick(1000.9, "2026-09-16 12:20:45")
    assert c._view_offset == off1, "같은 봉 틱마다 offset 이 늘면 화면이 뒤로 달아난다"


# ── B. 같은 날짜 리로드는 줌을 보존한다 ──────────────────────────────────────

def test_same_day_reload_preserves_zoom():
    c = _canvas()
    c.reset_session(_bars(200), [])
    c._visible_count = 40
    c._view_offset = 100
    c.reset_session(_bars(201), [])           # 15:46 보충 후 자동 리로드와 같은 모양
    assert c._visible_count == 40, "같은 날짜 리로드인데 줌이 풀렸다"
    assert c._view_offset == 100


def test_other_day_reload_resets_zoom():
    c = _canvas()
    c.reset_session(_bars(200), [])
    c._visible_count = 40
    c._view_offset = 100
    c.reset_session(_bars(180, day="2026-09-15"), [])
    assert c._view_offset == 0, "날짜가 바뀌면 초기화해야 한다 — 남의 날 위치를 물려받으면 안 된다"
    # 🔴 [598차] **의미로 묻는다 — 인코딩으로 묻지 않는다.**
    #   종전에는 `_visible_count == 180` 이었다. 그 단언은 「전부 보임」을 **그 순간의
    #   봉 수로 굳히는 것**을 요구하는 셈이었고, 그렇게 굳으면 다음 봉이 붙는 순간
    #   창 모드로 오판돼 「하루 전체」가 저절로 풀렸다(598차 원인).
    #   이제 「전부 보임」은 센티넬 0 이다. 검사해야 할 것은 저장 형태가 아니라
    #   **다 보이는가**이므로 그렇게 묻는다 — 어느 인코딩이든 통과한다.
    assert c._view_visible() == 180, "날짜가 바뀌었으면 전부 보여야 한다"
    assert c._view_is_full(), "전부 보이는 상태여야 한다(줌·패닝 아님)"


def test_preserved_offset_is_clamped_when_day_shrinks():
    """같은 날인데 봉이 줄어들 수도 있다(재조회 실패 등). 범위를 벗어나면 안 된다."""
    c = _canvas()
    c.reset_session(_bars(200), [])
    c._visible_count = 40
    c._view_offset = 150
    c.reset_session(_bars(60), [])
    assert 0 <= c._view_offset <= max(0, 60 - c._view_visible())


# ── C. 이동바 좌우 매핑 ──────────────────────────────────────────────────────

def test_nav_mapping_is_an_involution():
    """offset(오른쪽 기준) ↔ value(왼쪽 기준). 한쪽만 고치면 좌우가 뒤집힌다."""
    from dashboard.main_dashboard import MinuteChartDialog as D

    for total, visible in ((411, 40), (200, 200), (100, 20), (21, 20)):
        for offset in range(0, max(1, total - visible) + 1, 7):
            v = D.nav_value_from_offset(total, visible, offset)
            assert 0 <= v <= total - visible
            assert D.nav_offset_from_value(total, visible, v) == offset


def test_nav_edges_point_the_right_way():
    from dashboard.main_dashboard import MinuteChartDialog as D

    total, visible = 411, 40
    # 맨 오른쪽(최신, offset=0) → 이동바도 맨 오른쪽
    assert D.nav_value_from_offset(total, visible, 0) == total - visible
    # 맨 왼쪽(가장 오래된 구간) → 이동바 0
    assert D.nav_value_from_offset(total, visible, total - visible) == 0


def test_nav_hidden_when_everything_fits():
    """움직일 수 없는 손잡이는 「고장」으로 읽힌다 — 다 보이면 숨어야 한다."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "dashboard", "main_dashboard.py"), encoding="utf-8").read()
    i = src.index("def _on_chart_view_changed")
    blk = src[i:i + 1200]
    assert "if total <= visible:" in blk
    assert "_nav.hide()" in blk
    assert "blockSignals(True)" in blk, "왕복 갱신을 끊지 않으면 손잡이가 떨린다"
