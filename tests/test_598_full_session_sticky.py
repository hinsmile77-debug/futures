# -*- coding: utf-8 -*-
"""[MW0601 598차] 「하루 전체」가 저절로 풀리던 결함 + Y 축 조망 우선.

증상
----
사용자가 「하루 전체」를 켰는데 **줌을 한 적이 없는데도** 일정 봉만 보이는
모드로 되돌아왔다. 버튼은 계속 ON 이고, 꺼진 것은 x 축 격자였다.

원인 — 「줌 중인가」를 파생 조건으로 물었다
------------------------------------------
`_compute_padded_count(candles, total_count)` 의 가드가
`len(candles) < total_count` 였는데, 호출부에서 `candles` 는 **이미 보이는
구간으로 잘려** 넘어온다. 그래서 그 조건의 실제 뜻은 「창이 좁은가」다.

그리고 그 창은 저절로 좁아졌다 — `reset_session` 이 `_visible_count` 를
**그 순간의 봉 수로 굳혔기** 때문이다(2026-05-08 `0af5939` 이래). 봉이 하나만
더 붙으면 `보이는 봉 < 전체 봉` 이 성립한다. 실측: 120 → 121 에서 격자 411 → 130.

🔴 회귀가 아니라 **태생**이다. 589차가 가드를 지을 때 그 전제는 이미 거짓이었다
   — 474차 CORE 그룹 도달불가 · 471차 15:10 1차 경로와 같은 계열이다.

Y 축 (사용자 결정 2026-09-17)
-----------------------------
「하루 전체」는 **조망**이 목적이다. 591차의 점유율 가드는 점유율이 하한 미달이면
확장을 **취소**했는데, 그건 「봉이 아직 안 간 곳은 안 보여준다」와 같은 말이라
버튼의 목적과 어긋난다. 거부권을 떼고 **표기만** 남긴다. 모델 최대/최소 바깥으로
마진도 준다.

실행: conda run -n py37_32 python -m pytest tests/test_598_full_session_sticky.py
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

_DASH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "dashboard", "main_dashboard.py")


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


def _bars(n, day="2026-09-17", start=(8, 50)):
    t0 = datetime.datetime(int(day[:4]), int(day[5:7]), int(day[8:10]), *start)
    return [{"ts": (t0 + datetime.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
             "open": 1000.0, "high": 1001.0, "low": 999.0, "close": 1000.5,
             "volume": 10} for i in range(n)]


def _padded(c):
    """paintEvent 와 **같은 순서**로 잘라서 격자 슬롯 수를 구한다.

    🔴 `candles` 를 자른 **뒤에** 넘기는 것이 이 결함의 핵심이므로 그대로 흉내낸다.
      여기서 자르지 않으면 테스트가 헛돈다.
    """
    cds = list(c._closed_candles) + ([dict(c._live_candle)] if c._live_candle else [])
    total = len(cds)
    visible = min(max(c._visible_count or total, c._min_visible_count), total)
    # paintEvent 는 클램프한 offset 을 **되쓴다**(9609). 안 되쓰면 이 헬퍼가
    # 실제로 일어날 수 없는 상태를 만들어 테스트가 헛돈다.
    c._view_offset = c._clamp_view_offset(c._view_offset, total, visible)
    end = total - c._view_offset
    return c._compute_padded_count(cds[max(0, end - visible):end], total)


class _Wheel(object):
    """QWheelEvent 대신 — `wheelEvent` 가 쓰는 것은 `angleDelta().y()` 뿐이다."""

    class _D(object):
        def __init__(self, v):
            self._v = v

        def y(self):
            return self._v

    def __init__(self, dy):
        self._dy = dy

    def angleDelta(self):
        return _Wheel._D(self._dy)

    def ignore(self):
        pass

    def accept(self):
        pass


class _Dbl(object):
    def button(self):
        from PyQt5.QtCore import Qt
        return Qt.LeftButton

    def accept(self):
        pass


# ── A. 봉이 늘어도 「하루 전체」는 유지된다 ────────────────────────────────

def test_live_candle_does_not_cancel_full_session():
    """**진행 중(미확정) 봉 하나만 생겨도** 종전에는 풀렸다.

    `total_count` 는 확정봉+진행봉인데 `_visible_count` 는 확정봉 수만 담고
    있었다. 장중이면 1분도 못 버틴다.
    """
    c = _canvas()
    c.reset_session(_bars(30), [])
    c.set_full_session_x(True)
    assert _padded(c) >= c._full_session_slots(), "켠 직후부터 전일정 격자여야 한다"

    c._live_candle = _bars(1, start=(9, 20))[0]
    assert _padded(c) >= c._full_session_slots(), "진행 중 봉 하나에 전일정 격자가 풀렸다"


def test_closed_candles_do_not_cancel_full_session():
    c = _canvas()
    c.reset_session(_bars(30), [])
    c.set_full_session_x(True)
    for i in range(12):
        c.on_candle_closed(_bars(1, start=(9, 20 + i))[0])
    assert _padded(c) >= c._full_session_slots(), "봉이 12개 늘자 전일정 격자가 풀렸다"


def test_reload_keeps_full_view_as_sentinel():
    """리로드가 「전부 보임」을 **숫자로 굳히면** 다음 봉에서 풀린다.

    15:46 마감구간 보충 리로드가 매일 이 경로를 탄다.
    """
    c = _canvas()
    c.reset_session(_bars(30), [])
    assert c._visible_count == 0, "「전부 보임」은 센티넬 0 으로 남아야 한다"

    c.reset_session(_bars(31), [])                      # 같은 날 리로드
    assert c._visible_count == 0, "같은 날 리로드가 전체보기를 숫자로 굳혔다"

    c.reset_session(_bars(20, day="2026-09-16"), [])    # 다른 날
    assert c._visible_count == 0
    assert c._view_is_full()


# ── B. 진짜 줌·패닝일 때는 여전히 해제된다 (가드가 헛돌지 않는가) ──────────

def test_real_zoom_still_cancels_full_session():
    """가드를 떼어버린 게 아니다 — **진짜** 줌에는 여전히 걸려야 한다."""
    c = _canvas()
    c.reset_session(_bars(120), [])
    c.set_full_session_x(True)
    assert _padded(c) >= c._full_session_slots()

    c._visible_count = 40                               # 휠 줌과 같은 상태
    assert _padded(c) < c._full_session_slots(), \
        "줌 중인데 격자가 411 로 고정되면 확대가 무력화된다"


def test_real_pan_still_cancels_full_session():
    """패닝은 **줌 다음에만** 온다 — 다 보이는 상태에서는 밀 곳이 없다.

    ⚠ `_view_offset` 만 넣고 재면 안 된다. 다 보이는 상태면 `_clamp_view_offset`
      이 그 값을 0 으로 깎으므로(`max_offset = total - visible = 0`) **도달할 수
      없는 상태를 재는 셈**이 된다. 589차 가드가 바로 그런 조건 위에 서 있다가
      틀렸다 — 같은 실수를 테스트에서 되풀이하지 않는다.
    """
    c = _canvas()
    c.reset_session(_bars(120), [])
    c.set_full_session_x(True)

    c._visible_count = 40                               # 줌
    c._view_offset = 20                                 # 그 다음 과거로 패닝
    assert not c._view_is_full()
    assert _padded(c) < c._full_session_slots(), "패닝 중에는 전일정 격자를 적용하지 않는다"
    assert c._view_offset == 20, "밀 수 있는 범위인데 깎였다"

    # 오른쪽 끝으로 돌아와도 **줌은 그대로**라 여전히 해제다
    c._view_offset = 0
    assert _padded(c) < c._full_session_slots()


def test_zoom_out_to_everything_returns_to_sentinel():
    """다 보이게 줌아웃했는데 숫자로 남으면 다음 봉에서 또 풀린다."""
    c = _canvas()
    c.reset_session(_bars(120), [])
    c.set_full_session_x(True)
    c._visible_count = 40
    for _ in range(20):                                 # 충분히 줌아웃
        c.wheelEvent(_Wheel(-120))
    assert c._visible_count == 0, "전부 보이는데 숫자로 남았다"

    c.on_candle_closed(_bars(1, start=(11, 0))[0])
    assert _padded(c) >= c._full_session_slots(), "줌아웃 복귀 뒤 봉이 붙자 또 풀렸다"


def test_double_click_returns_to_sentinel():
    c = _canvas()
    c.reset_session(_bars(120), [])
    c.set_full_session_x(True)
    c._visible_count = 40
    c._view_offset = 30
    c.mouseDoubleClickEvent(_Dbl())
    assert c._visible_count == 0 and c._view_offset == 0

    c.on_candle_closed(_bars(1, start=(11, 0))[0])
    assert _padded(c) >= c._full_session_slots(), "더블클릭 전체보기 뒤 봉이 붙자 또 풀렸다"


# ── C. 가드는 파생 조건이 아니라 상태를 묻는다 ────────────────────────────

def test_guard_asks_state_not_derived_length():
    """`len(candles) < total_count` 로 되돌아가면 이 결함이 그대로 재발한다."""
    src = _src()
    i = src.index("def _compute_padded_count")
    blk = src[i:i + 1600]
    assert "if not self._view_is_full():" in blk, "상태를 직접 물어야 한다"
    assert "if len(candles) < total_count:" not in blk, "파생 조건으로 되돌아갔다"
    assert "def _view_is_full" in src


def test_view_is_full_answers_by_meaning():
    """숫자로 굳은 값이 어디선가 들어와도 **뜻이 같으면 같게** 판정해야 한다."""
    c = _canvas()
    c.reset_session(_bars(50), [])
    assert c._view_is_full()

    c._visible_count = 50                               # 굳은 값이지만 뜻은 「전부」
    assert c._view_is_full()

    c._visible_count = 49
    assert not c._view_is_full()

    c._visible_count = 0
    c._view_offset = 1
    assert not c._view_is_full(), "패닝 중이면 전부가 아니다"


def test_x_hold_reason_is_visible():
    """조용히 풀리면 「버튼이 저절로 꺼졌다」로 읽힌다(계측 4원칙 ④).

    Y 쪽은 591차부터 사유를 적고 있었는데 x 는 말이 없었다 — 그 비대칭이
    사용자를 두 번 헤매게 했다.
    """
    src = _src()
    assert "self._full_x_note = None" in src, "명시 초기화 필요"
    assert "def _draw_full_x_note" in src
    assert "self._draw_full_x_note(painter, plot)" in src, "그리기 호출이 배선돼야 한다"
    # [621차 후속11] paintEvent 본문이 Qt 진입점 가드(단일 try)로 한 단 들여써졌다 —
    #   들여쓰기 폭이 아니라 「초기화 바로 다음 줄이 조건」이라는 순서만 본다.
    import re
    m = re.search(r"self\._full_x_note = None\r?\n[ ]+if self\._full_session_x", src)
    assert m, "보류 사유 초기화 → 조건 순서가 깨졌다"
    i = m.start()
    assert "self._full_x_note = (" in src[i:i + 500], "보류했으면 사유를 남겨야 한다"


# ── D. Y 축 — 봉이 도달하지 않아도 모델까지 넓히고 마진을 준다 ────────────

def test_y_expands_even_when_bars_have_not_reached():
    """591차 점유율 가드는 **거부권을 잃었다**(사용자 결정 2026-09-17).

    「하루 전체」는 조망이다 — 모델이 가리키는 데까지 미리 열어두지 않으면
    하루가 어디로 갈 수 있는지가 화면에 없다.
    """
    src = _src()
    i = src.index("if _occ >= self.FULL_Y_MIN_OCCUPANCY:")
    blk = src[i:i + 700]
    assert "lo, hi = _ulo, _uhi" not in blk, "점유율이 확장을 취소하면 안 된다(거부권 제거)"
    assert "self._full_y_note = (" in blk, "눌린 정도는 계속 화면이 말해야 한다"


def test_y_model_margin_exists_and_is_not_double_applied():
    from dashboard.main_dashboard import MinuteChartCanvas as MC
    assert 0.0 < MC.FULL_Y_MODEL_MARGIN < 0.5, "마진이 없거나 과하면 조망이 안 된다"
    assert "if not _y_model_padded:" in _src(), \
        "모델 마진과 일반 여백을 둘 다 걸면 두 번 밀려 캔들만 눌린다"


def test_y_margin_leaves_room_beyond_model_extremes():
    """모델 선이 테두리에 딱 붙으면 **더 갈 수 있다는 사실이 안 읽힌다.**"""
    from dashboard.main_dashboard import MinuteChartCanvas as MC
    c = _canvas()
    c.reset_session(_bars(30), [])
    c.set_full_session_x(True)
    c._pre_levels = {"dist_high": 1067.0, "dist_low": 1039.0,
                     "struct_up": [1063.0], "struct_down": [1046.0]}
    lv = c._model_axis_levels()
    assert lv, "모델 레벨이 비면 이 시험이 헛돈다"
    ulo, uhi = min(lv), max(lv)
    m = max((uhi - ulo) * MC.FULL_Y_MODEL_MARGIN, 0.5)
    assert m > 0
    assert ulo - m < ulo and uhi + m > uhi
