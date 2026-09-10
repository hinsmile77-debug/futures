# -*- coding: utf-8 -*-
"""[MW0601 555차 후속2] 출처축(P0) · 차트 Y축(P1) · 라벨 레지스트리(P2) · 진입↔청산 연결선.

🔴 이 셋은 **같은 사고의 세 얼굴**이다
--------------------------------------
2026-09-10, 554차 유령 포지션(`trades` id=572,573 · 허구 +6,921,594원 / +138.84pt)이
소비처마다 다르게 흘렀다:

  계좌 「금일손익」        +463,281원        ← 브로커 원천이라 구조적으로 안전
  당일 진입 통계          +148.54pt         ← **93.5%가 허구** (필터 없음)
  1분봉 차트 Y축          1033.69~1125.23   ← 마커 하나가 축을 벌려 봉이 33.1%만 차지
  손익 추이 탭            블랙리스트라 auto 로 편입 (555차 후속에서 해소)

554차가 DB 라벨을 `SYSTEM_AUTO` → `PHANTOM_STATE_ARTIFACT` 로 정정했지만
**그 라벨을 아는 코드가 0곳**이었다. 소비처마다 「시스템 거래」를 따로 정의한 탓이다.

이 파일이 고정하는 것:
  P2  분류 정본이 하나이고, 모르는 라벨의 기본값은 `unknown`(= system 아님)
  P0  `daily_stats()` 가 시스템 축과 제외분을 **함께** 낸다(기존 키는 무변경)
  P1  Y축은 봉 범위가 정하고, 축 밖 마커는 축을 늘리지 않는다
  요청2 진입점 ↔ 청산점을 직접 잇는다(종전엔 진입가 수평선)

실행:
    conda run -n py37_32 python -m pytest tests/test_555_origin_axis_and_chart.py -v
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from config.constants import (  # noqa: E402
    ENTRY_SOURCE_REGISTRY, SYSTEM_ENTRY_SOURCES, MANUAL_ENTRY_SOURCES,
    ARTIFACT_ENTRY_SOURCES, classify_entry_source, entry_source_is_system,
)


# ══════════════════════════════════════════════════════════════════════
# P2 — 라벨 레지스트리
# ══════════════════════════════════════════════════════════════════════
def test_phantom_label_is_registered_as_artifact():
    """554차 라벨이 등록돼 있고 「거래 아님」으로 분류된다."""
    assert ENTRY_SOURCE_REGISTRY["PHANTOM_STATE_ARTIFACT"] == "artifact"
    assert not entry_source_is_system("PHANTOM_STATE_ARTIFACT")


@pytest.mark.parametrize("src", ["", None, "SOME_NEW_LABEL", "  ", "system_auto"])
def test_unknown_labels_are_not_system(src):
    """🔴 모르는 라벨의 기본값은 `unknown` 이지 `system` 이 아니다.

    소문자 `system_auto` 도 포함한다 — 레지스트리는 **정확 일치**만 인정한다.
    """
    assert classify_entry_source(src) == "unknown"
    assert not entry_source_is_system(src)


def test_registry_is_the_single_source_of_truth():
    """설정·패널이 리터럴 사본을 두지 않고 레지스트리에서 파생하는가."""
    from config.settings import PROFIT_GUARD_SYSTEM_SOURCES
    from dashboard.main_dashboard import PnlHistoryPanel
    assert tuple(PROFIT_GUARD_SYSTEM_SOURCES) == tuple(SYSTEM_ENTRY_SOURCES)
    assert tuple(PnlHistoryPanel._MANUAL_SOURCES) == tuple(MANUAL_ENTRY_SOURCES)
    assert PnlHistoryPanel._AUTO_SOURCES == frozenset(SYSTEM_ENTRY_SOURCES)


def test_every_entry_source_literal_in_code_is_classified():
    """🔴 새 라벨을 배선하고 등록을 잊으면 여기서 깨진다.

    소스에서 `entry_source` 근처의 대문자 리터럴을 긁어 전부 분류돼 있는지 본다.
    (P2 의 목적 자체 — "분류 미지정이면 테스트가 깨지게")
    """
    import re
    known = set(ENTRY_SOURCE_REGISTRY)
    pat = re.compile(r'entry_source[^\n]{0,80}?"([A-Z][A-Z0-9_]{3,})"')
    found = set()
    for base, _dirs, files in os.walk(_ROOT):
        if any(p in base for p in (".git", "__pycache__", "tests", "docs", "logs")):
            continue
        for fn in files:
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(base, fn), encoding="utf-8", errors="ignore") as fh:
                found |= set(pat.findall(fh.read()))
    # 분류축 이름 자체(TEXT 등 SQL 조각)는 대상이 아니다.
    found -= {"TEXT", "NULL", "REAL", "INTEGER"}
    missing = sorted(found - known)
    assert not missing, (
        "ENTRY_SOURCE_REGISTRY 에 없는 entry_source 라벨: %s\n"
        "  → config/constants.py 에 분류(system/manual/artifact)를 등록할 것.\n"
        "  등록 전까지 그 거래는 「미측정」으로 집계된다." % missing)


# ══════════════════════════════════════════════════════════════════════
# P0 — daily_stats() 출처축
# ══════════════════════════════════════════════════════════════════════
class _Row(dict):
    def keys(self):
        return list(super(_Row, self).keys())


def _leg(src, pnl_pts, ets, xts=None, qty=1, comm=10_000.0):
    return _Row({
        "entry_ts": ets, "exit_ts": xts or ets, "exit_price": 1100.0,
        "entry_price": 1100.0, "quantity": qty, "pnl_pts": pnl_pts,
        "forward_pnl_pts": pnl_pts, "commission_krw": comm,
        "entry_source": src,
    })


def _tracker():
    from strategy.position.position_tracker import PositionTracker
    t = PositionTracker()
    t.reset_daily()
    return t


#: 2026-09-10 실측 그대로 — 유령 2레그 + 실거래 2레그.
_REAL_DAY = [
    _leg("PHANTOM_STATE_ARTIFACT", 69.60, "2026-09-10 08:02:01", "2026-09-10 08:45:22"),
    _leg("PHANTOM_STATE_ARTIFACT", 69.24, "2026-09-10 08:02:01", "2026-09-10 08:45:22"),
    _leg("BROKER_SYNC_RECOVERY",    4.78, "2026-09-10 12:17:52", "2026-09-10 12:17:53"),
    _leg("BROKER_SYNC_RECOVERY",    4.92, "2026-09-10 12:17:52", "2026-09-10 12:18:00"),
]


def test_restore_splits_phantom_out_of_system_axis():
    """🔴 이 사고의 지문 — 전체 축은 +148.54pt 인데 시스템 축은 0 이어야 한다."""
    t = _tracker()
    t.restore_daily_stats(_REAL_DAY)
    s = t.daily_stats()

    # 기존 축은 **무변경**이다(소비처 18곳 — 여기가 바뀌면 조용한 재정의가 된다).
    assert s["trades"] == 2
    assert s["wins"] == 2
    assert round(s["pnl_pts"], 2) == 148.54

    # 새 축: 오늘 시스템 자동매매는 0건이다.
    assert s["sys_trades"] == 0
    assert s["sys_wins"] == 0
    assert round(s["sys_pnl_pts"], 2) == 0.0

    # 제외분은 버리지 않는다 — 얼마가 왜 빠졌는지 남는다(계측 4원칙 ③).
    assert s["excluded_trades"] == 2
    assert round(s["excluded_pnl_pts"], 2) == 148.54
    assert set(s["excluded_sources"]) == {"PHANTOM_STATE_ARTIFACT",
                                          "BROKER_SYNC_RECOVERY"}


def test_system_entries_land_in_system_axis():
    t = _tracker()
    t.restore_daily_stats([
        _leg("SYSTEM_AUTO", +3.0, "2026-09-11 10:00:00", "2026-09-11 10:05:00"),
        _leg("SYSTEM_AUTO", -1.0, "2026-09-11 11:00:00", "2026-09-11 11:05:00"),
    ])
    s = t.daily_stats()
    assert (s["sys_trades"], s["sys_wins"], s["sys_losses"]) == (2, 1, 1)
    assert round(s["sys_pnl_pts"], 2) == 2.0
    assert s["excluded_trades"] == 0
    assert s["excluded_sources"] == []


def test_missing_entry_source_is_excluded_not_system():
    """311차 이전 미기록 구간 — **미측정이지 시스템진입이 아니다**(계측 4원칙 ②)."""
    t = _tracker()
    t.restore_daily_stats([_leg(None, +5.0, "2026-09-11 10:00:00", "2026-09-11 10:05:00")])
    s = t.daily_stats()
    assert s["sys_trades"] == 0
    assert s["excluded_trades"] == 1
    assert s["excluded_sources"] == ["(미기록)"]


def test_mixed_source_position_is_excluded_conservatively():
    """한 포지션의 레그 출처가 갈리면 **비시스템**으로 본다 — 성과를 부풀리지 않는 방향."""
    t = _tracker()
    ets = "2026-09-11 10:00:00"
    t.restore_daily_stats([
        _leg("SYSTEM_AUTO", +2.0, ets, "2026-09-11 10:03:00"),
        _leg("GHOST_PENDING_MISS", +2.0, ets, "2026-09-11 10:05:00"),
    ])
    s = t.daily_stats()
    assert s["sys_trades"] == 0
    assert s["excluded_trades"] == 1


def test_reset_daily_clears_origin_axis():
    """리셋 누락은 전날 유령을 오늘 제외분으로 남긴다(계측 4원칙 ④)."""
    t = _tracker()
    t.restore_daily_stats(_REAL_DAY)
    assert t.daily_stats()["excluded_trades"] == 2
    t.reset_daily()
    s = t.daily_stats()
    assert (s["sys_trades"], s["excluded_trades"], s["excluded_sources"]) == (0, 0, [])


def test_live_close_position_feeds_origin_axis():
    """복원 경로만 고치면 **당일 라이브 집계**가 여전히 오염된다."""
    t = _tracker()
    t.open_position("LONG", 1100.0, 1, 1.5, grade="A")
    t.entry_source = "SYSTEM_AUTO"
    t.close_position(1105.0, "TP2(전량)")
    s = t.daily_stats()
    assert s["sys_trades"] == 1 and s["sys_wins"] == 1
    assert s["excluded_trades"] == 0


def test_live_close_position_excludes_non_system():
    t = _tracker()
    t.open_position("LONG", 1100.0, 1, 1.5, grade="A")
    t.entry_source = "OPERATOR_MANUAL"
    t.close_position(1105.0, "TP2(전량)")
    s = t.daily_stats()
    assert s["trades"] == 1, "전체 축은 종전대로 센다"
    assert s["sys_trades"] == 0
    assert s["excluded_sources"] == ["OPERATOR_MANUAL"]


# ══════════════════════════════════════════════════════════════════════
# P1 + 요청2 — 차트
# ══════════════════════════════════════════════════════════════════════
def _canvas_with(trades, candles):
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QPixmap, QPainter
    from dashboard.main_dashboard import MinuteChartCanvas
    _app = QApplication.instance() or QApplication(sys.argv)
    c = MinuteChartCanvas()
    c.resize(800, 400)
    c._closed_candles = list(candles)
    c._completed_trades = list(trades)
    pm = QPixmap(800, 400)
    p = QPainter(pm)
    try:
        c.render(p)
    finally:
        p.end()
    return c


def _candles(n=60, base=1100.0, span=30.0):
    out = []
    for i in range(n):
        px = base + (span * (i % 10) / 10.0)
        out.append({"ts": "2026-09-10 %02d:%02d:00" % (9 + i // 60, i % 60),
                    "open": px, "high": px + 0.5, "low": px - 0.5,
                    "close": px, "volume": 10})
    return out


def test_axis_is_set_from_candles_only():
    """🔴 축 밖 마커(유령 진입가 1040)가 Y축을 늘리면 안 된다.

    실측: 봉 1088.58~1118.92 인데 축이 1033.69~1125.23 으로 벌어져
    봉이 세로의 33.1%만 차지했다.
    """
    cs = _candles()
    lo_px = min(c["low"] for c in cs)
    hi_px = max(c["high"] for c in cs)
    phantom = {"entry_ts": cs[0]["ts"], "exit_ts": cs[5]["ts"],
               "entry_price": 1040.0, "exit_price": hi_px, "pnl_pts": 60.0}
    c = _canvas_with([phantom], cs)

    assert c._axis_lo is not None, "축 범위가 기록되지 않았다"
    # 축 하단이 유령 진입가(1040)까지 내려가지 않아야 한다.
    assert c._axis_lo > 1040.0
    # 봉이 축의 대부분을 차지한다.
    used = (hi_px - lo_px) / (c._axis_hi - c._axis_lo)
    assert used > 0.7, "봉이 세로의 %.1f%% 밖에 안 된다 — 축이 마커에 끌려갔다" % (used * 100)


def test_off_axis_price_is_flagged():
    cs = _candles()
    c = _canvas_with([], cs)
    assert c._is_off_axis(1040.0) is True
    assert c._is_off_axis((c._axis_lo + c._axis_hi) / 2.0) is False


def test_off_axis_undecidable_before_first_paint():
    """축 범위를 모르면 「축 안」이라 단정하지 않는다(계측 4원칙 ②)."""
    from PyQt5.QtWidgets import QApplication
    from dashboard.main_dashboard import MinuteChartCanvas
    _app = QApplication.instance() or QApplication(sys.argv)
    c = MinuteChartCanvas()
    assert c._axis_lo is None and c._axis_hi is None
    assert c._is_off_axis(1040.0) is False   # 캐럿을 안 그릴 뿐, 판정하지 않는다


def test_trade_span_connects_entry_to_exit():
    """[요청2] 진입점 → 청산점을 직접 잇는다 — 진입가 수평선이 아니다."""
    import inspect
    from dashboard.main_dashboard import MinuteChartCanvas
    src = inspect.getsource(MinuteChartCanvas._draw_trade_spans)
    assert "_draw_link_line" in src
    # 청산가로 두 번째 y 를 만든다.
    assert "exit_price" in src and "y2" in src
    gp = inspect.getsource(MinuteChartCanvas._draw_gp_layer)
    assert "_draw_link_line" in gp, "GP 섀도도 같은 방식이어야 한다"


def test_link_line_endpoints_differ_for_winning_trade():
    """수평선이면 두 끝점의 y 가 같다 — 대각선이어야 한다."""
    from PyQt5.QtCore import QRectF
    from PyQt5.QtWidgets import QApplication
    from dashboard.main_dashboard import MinuteChartCanvas
    _app = QApplication.instance() or QApplication(sys.argv)
    c = MinuteChartCanvas()
    plot = QRectF(0, 0, 100, 200)
    y_in = c._price_to_y(1100.0, plot, 1090.0, 1120.0)
    y_out = c._price_to_y(1115.0, plot, 1090.0, 1120.0)
    assert abs(y_in - y_out) > 1.0, "진입가와 청산가의 y 가 같으면 대각선이 아니다"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))


# ══════════════════════════════════════════════════════════════════════
# GP 마커 시각 언어 [555차 후속2 / 사용자 지시]
#   GB 진입 = 청색 상방 화살표 · GS 진입 = 적색 하방 화살표
#   청산    = 밝은 테두리 위에 검은 X
# ══════════════════════════════════════════════════════════════════════
def test_gp_entry_colors_are_blue_and_red():
    from dashboard.main_dashboard import MinuteChartCanvas as M
    from PyQt5.QtGui import QColor
    gb, gs = QColor(M.GP_LONG_COLOR), QColor(M.GP_SHORT_COLOR)
    assert gb.blue() > gb.red() and gb.blue() > gb.green(), "GB 는 청색이어야 한다"
    assert gs.red() > gs.blue() and gs.red() > gs.green(), "GS 는 적색이어야 한다"


def test_gp_entry_glyph_is_gb_gs_not_gp():
    """어느 규칙이 낸 신호인지 화면에서 바로 읽혀야 한다."""
    import inspect
    from dashboard.main_dashboard import MinuteChartCanvas as M
    src = inspect.getsource(M._draw_gp_entry_marker)
    assert '"GB" if up else "GS"' in src
    assert '"GP")' not in src, "글리프가 아직 GP 다"


def test_gp_exit_is_black_x_on_bright_rim():
    """🔴 X 는 **언제나 검정**이다 — 손익 색으로 칠하면 실측과 섞인다."""
    import inspect
    from dashboard.main_dashboard import MinuteChartCanvas as M
    from PyQt5.QtGui import QColor
    src = inspect.getsource(M._draw_gp_exit_marker)
    assert "GP_EXIT_RIM" in src and "GP_EXIT_X" in src
    assert src.count("drawLine") >= 2, "X 는 선 2개다"
    rim, xcol = QColor(M.GP_EXIT_RIM), QColor(M.GP_EXIT_X)
    assert rim.lightness() > 200, "테두리 바탕이 밝지 않다"
    assert xcol.lightness() < 40, "X 가 검지 않다"


def test_gp_visual_language_still_differs_from_real_markers():
    """색이 같아져도 **형태·선종**으로 가상/실측이 갈려야 한다(553차 취지 보존)."""
    import inspect
    from dashboard.main_dashboard import MinuteChartCanvas as M
    gp = inspect.getsource(M._draw_gp_layer)
    real = inspect.getsource(M._draw_trade_spans)
    assert "Qt.DotLine" in gp, "GP 연결선은 점선이어야 한다"
    assert "Qt.DotLine" not in real, "실측 연결선은 파선(기본)이어야 한다"
    entry = inspect.getsource(M._draw_entry_marker)
    assert "drawRoundedRect" in entry, "실측 진입은 배지(둥근 사각) 형태다"
    assert "drawRoundedRect" not in inspect.getsource(M._draw_gp_entry_marker)


# ══════════════════════════════════════════════════════════════════════
# 순환 import 함정 — 레지스트리를 파일 끝에 두면 CORE 정의 통합이 조용히 깨진다
# ══════════════════════════════════════════════════════════════════════
def test_registry_defined_before_lazy_settings_import():
    """🔴 구현 중 실제로 밟은 함정이다 — 재발 방지.

    `config/constants.py` 는 모듈 실행 중 `CORE_FEATURES = _derive_core_features()`
    로 **settings 를 지연 import** 한다. 그런데 settings 는 이 레지스트리를 import
    하므로, 레지스트리가 그 줄보다 **뒤에** 정의돼 있으면:

        constants 실행 → _derive_core_features() → settings import
            → `from config.constants import SYSTEM_ENTRY_SOURCES`
            → constants 는 아직 그 줄에 도달하지 않았다 → ImportError
            → `except Exception` 이 삼키고 **CORE 하드코딩 폴백** + WARNING

    폴백값이 마침 파생값과 같아 **숫자로는 아무 일도 안 일어난 것처럼 보인다** —
    500차가 통합한 「CORE 정의는 한 곳」이 조용히 풀리는 것이다(계측 4원칙 ④).
    """
    path = os.path.join(_ROOT, "config", "constants.py")
    src = open(path, encoding="utf-8").read()
    i_reg = src.index("SYSTEM_ENTRY_SOURCES = tuple(")
    i_lazy = src.index("CORE_FEATURES = _derive_core_features()")
    assert i_reg < i_lazy, (
        "ENTRY_SOURCE_REGISTRY 파생부가 `CORE_FEATURES = _derive_core_features()`"
        " 보다 뒤에 있다 — settings 지연 import 시점에 아직 정의되지 않아"
        " CORE 가 폴백으로 떨어진다")


def test_both_import_orders_are_clean():
    """어느 쪽을 먼저 import 해도 CORE 폴백 경고가 나오면 안 된다."""
    import subprocess
    for first, second in (("config.constants", "config.settings"),
                          ("config.settings", "config.constants")):
        r = subprocess.run(
            [sys.executable, "-c",
             "import %s, %s" % (first, second)],
            cwd=_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = r.stdout.decode("utf-8", "ignore")
        assert r.returncode == 0, "%s → %s import 실패:\n%s" % (first, second, out)
        assert "CORE_FEATURES_BY_GROUP 조회 실패" not in out, (
            "%s 를 먼저 import 하면 CORE 가 폴백으로 떨어진다:\n%s" % (first, out))
