# -*- coding: utf-8 -*-
"""[MW0601 591차] 「⛶ 하루 전체」 — y축을 맥점 모델 범위까지 넓힌다.

왜 이 모양인가 (실측 근거, 2026-09-16 · 107 스테이지-일)
--------------------------------------------------------
요청은 「y축을 거리모델·구조모델 Min/Max 로」였지만, 실측이 두 가지를 바꿨다.

① **합집합이어야 한다.** 모델 범위'만'으로 잡으면 캔들이 잘린다 —
   실제 봉이 모델 범위를 벗어난 날이 0850 **89%** · 0930 **76%**,
   벗어난 폭 중앙 **13pt**(봉 폭이 보통 20~25pt다).

② **80% 밴드는 넣으면 안 된다.** 캔들 세로 점유율(현행 봉만 = 100%):

       스테이지  점추정만   +구조     +밴드
       0850      82.1%     72.2%    37.6%  (최소 15.1%)
       0930      92.0%     86.5%    42.2%  (최소 16.9%)

   554차 사고(마커 한 건이 캔들을 **33.1%** 로 눌렀다) 때와 같거나 더 나쁘다.
   그래서 축에는 **점추정 + 구조**만 넣는다. 밴드는 면이라 잘려도 읽힌다.

③ 그래도 최악은 37.7%(0930) 이므로 **점유율 하한 가드**를 둔다.
   `FULL_Y_MIN_OCCUPANCY = 0.40` — 107 스테이지-일 중 1일에서 발동한다.
   **죽은 가드가 아니다**, 그리고 발동하면 화면에 사유를 적는다(계측 4원칙 ④).

실행: conda run -n py37_32 python -m pytest tests/test_591_full_session_y_axis.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"
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


def _dash_src():
    return open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "dashboard", "main_dashboard.py"), encoding="utf-8").read()


_LEVELS = {
    "stage": "0930",
    "dist_high": 1056.0,
    "dist_low": 1029.37,
    "struct_up": [[1053.44, ["전일고"]], [1056.0, ["매물대"]]],
    "struct_down": [[1032.0, ["OR저"]]],
    # 밴드 — **축에 들어가면 안 된다**
    "high80_lo": 1040.0, "high80_hi": 1120.0,
    "low80_lo": 960.0, "low80_hi": 1035.0,
    "high50_lo": 1048.0, "high50_hi": 1075.0,
    "low50_lo": 1005.0, "low50_hi": 1033.0,
}


# ── 1. 축에 넣을 레벨 고르기 ────────────────────────────────────────────────

def test_axis_levels_take_points_and_structure_only():
    c = _canvas()
    c.set_premarket_levels(dict(_LEVELS))
    got = sorted(c._model_axis_levels())
    assert got == sorted([1056.0, 1029.37, 1053.44, 1056.0, 1032.0])
    # 밴드 값이 하나라도 섞이면 554차 재현이다
    for band in (1120.0, 960.0, 1040.0, 1035.0, 1005.0, 1075.0, 1048.0, 1033.0):
        assert band not in got, "80%%/50%% 밴드(%s)가 축 계산에 섞였다" % band


def test_axis_levels_empty_means_no_widening():
    """「미조회(None)」와 「그날 산출 없음({})」 둘 다 축을 안 늘린다 — 뜻은 다르다."""
    c = _canvas()
    assert c._model_axis_levels() == []          # 초기값 None
    c.set_premarket_levels({})
    assert c._model_axis_levels() == []


def test_axis_levels_survive_garbage():
    c = _canvas()
    c.set_premarket_levels({"dist_high": None, "dist_low": "x",
                            "struct_up": [["bad"], [], None, [1050.0]],
                            "struct_down": None})
    assert c._model_axis_levels() == [1050.0]


# ── 2. 가드 상수 ────────────────────────────────────────────────────────────

def test_occupancy_guard_is_live_not_dead():
    """554차(33.1%)보다 높고, 실측 최악(37.7%)보다도 높아야 **발동하는** 가드다."""
    from dashboard.main_dashboard import MinuteChartCanvas as MC
    assert MC.FULL_Y_MIN_OCCUPANCY > 0.331, "554차 사고 수준을 허용하면 가드가 아니다"
    assert MC.FULL_Y_MIN_OCCUPANCY > 0.377, "실측 최악에서도 안 울리면 죽은 가드다"
    assert MC.FULL_Y_MIN_OCCUPANCY < 0.722, "실측 중앙(0850 72.2%)에서 울리면 상시 보류다"


def test_guard_fallback_is_visible():
    """조용히 안 늘리면 「버튼이 안 먹는다」로 읽힌다(계측 4원칙 ④)."""
    src = _dash_src()
    assert "self._full_y_note = None" in src, "명시 초기화 필요"
    assert "def _draw_full_y_note" in src
    assert "self._draw_full_y_note(painter, plot)" in src, "그리기 호출이 배선돼야 한다"
    i = src.index("if _occ >= self.FULL_Y_MIN_OCCUPANCY:")
    blk = src[i:i + 700]
    assert "self._full_y_note = (" in blk, "보류했으면 사유를 남겨야 한다"


# ── 3. 배선 ─────────────────────────────────────────────────────────────────

def test_toggle_also_enables_model_layers():
    """축을 늘린 **원인이 화면에 보여야** 한다(사용자 결정 2026-09-16)."""
    src = _dash_src()
    assert '_FULL_SESSION_LAYERS = ("price", "struct")' in src
    i = src.index("def _on_full_session_toggled")
    blk = src[i:i + 800]
    assert "if on:" in blk and "setChecked(True)" in blk
    assert "self._chart.set_full_session_x(on)" in blk
    # 끌 때 되돌리지 않는다 — 사용자가 직접 조정한 레이어를 덮으면 그쪽이 더 놀랍다
    assert "setChecked(False)" not in blk


def test_0930_levels_reach_the_chart_without_reload():
    """09:30 2차가 DB 에 들어가도 리로드가 없으면 차트는 1차를 계속 들고 있었다."""
    src = _dash_src()
    # ⚠ `EntryPanel` 에도 같은 이름·같은 docstring 머리의 메서드가 있다.
    #   어댑터 쪽만 잡으려면 **어댑터 본문 고유의 줄**을 앵커로 쓴다.
    i = src.index("self._win.entry_panel.update_premarket_levels(stages)")
    blk = src[i:i + 1200]
    assert "_apply_premarket_levels()" in blk, "차트 레벨 갱신이 배선되지 않았다"
    assert "_live_mode" in blk, "복기 모드에서는 오늘 레벨로 덮으면 안 된다"


def test_button_label_covers_both_axes():
    """라벨이 x축 전용 표현이면 y까지 고정한다는 사실이 안 읽힌다."""
    src = _dash_src()
    i = src.index("self._btn_fullx = QPushButton(")
    line = src[i:src.index("\n", i)]
    assert "15:45 격자" not in line, "y축까지 바뀌는데 x축 전용 라벨이 남아 있다"
    i2 = src.index("self._btn_fullx.setToolTip(")
    tip = src[i2:i2 + 900]
    assert "y축" in tip and "합집합" in tip, "툴팁이 동작을 설명해야 한다"
