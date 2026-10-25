# -*- coding: utf-8 -*-
"""[MW0601 713차 후속] Ctrl+Shift+X 1분봉 차트 — 신동 주체 전환에 맞춘 레이어 정리.

사용자 지시(2026-10-25):
  1. 미륵 휴면이면 「거래미륵」 비활성
  2. 거래신동 거래내역을 거래미륵처럼 **면·칩**으로
  3. 「하루 전체」 기본 켜짐
  4. 「거래신동」 단추를 거래미륵·거래피터 **사이**로(상단 바에서 이동)

🔴 2번의 숨은 결함: 종전에는 trades.db 실거래가 출처와 무관하게 전부 「거래미륵」이었다.
  1번만 하면 **신동 실거래까지 같이 사라진다.** 그래서 `entry_source` 로 레이어를 가른다.

실행:
    conda run -n py37_32 python -m pytest tests/test_713_chart_shindong_layer.py -v
"""
import os
import sys
from datetime import datetime, timedelta

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt5.QtWidgets import QApplication, QHBoxLayout  # noqa: E402

import config.settings as _settings  # noqa: E402
import dashboard.main_dashboard as md  # noqa: E402
from dashboard.main_dashboard import MinuteChartCanvas, MinuteChartDialog  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)
_T0 = datetime(2026, 10, 23, 9, 0)


def _ts(m):
    return _T0 + timedelta(minutes=m)


@pytest.fixture
def dialog(monkeypatch):
    made = []

    def _make(engine="off"):
        monkeypatch.setattr(_settings, "MIREUK_ENGINE", engine, raising=False)
        d = MinuteChartDialog()
        made.append(d)
        return d

    yield _make
    for d in made:
        d.deleteLater()


def _row_of(d, widget):
    """widget 이 들어 있는 QHBoxLayout 의 위젯 순서."""
    stack = [d.layout()]
    while stack:
        lay = stack.pop()
        ws = [lay.itemAt(i).widget() for i in range(lay.count())]
        if widget in ws and isinstance(lay, QHBoxLayout):
            return [w for w in ws if w is not None]
        stack.extend(lay.itemAt(i).layout() for i in range(lay.count())
                     if lay.itemAt(i).layout() is not None)
    return None


# ── 1. 미륵 휴면 → 거래미륵 비활성 ───────────────────────────────
def test_1_mireuk_toggle_disabled_when_dormant(dialog):
    d = dialog("off")
    b = d._ov_btn["trade_mireuk"]
    assert not b.isEnabled() and not b.isChecked()
    assert d._chart._ov["trade_mireuk"] is False, "단추만 끄고 캔버스는 그대로 그린다"


def test_1b_mireuk_toggle_kept_when_engine_on(dialog):
    d = dialog("full")
    b = d._ov_btn["trade_mireuk"]
    assert b.isEnabled() and b.isChecked()
    assert d._chart._ov["trade_mireuk"] is True


# ── 3. 하루 전체 기본 켜짐(연결 뒤 setChecked → 축·레이어까지 반영) ──
def test_3_full_session_default_on(dialog):
    d = dialog("off")
    assert d._btn_fullx.isChecked()
    assert d._chart._full_session_x is True, "단추만 켜지고 캔버스 축은 꺼진 채"
    for k in MinuteChartDialog._FULL_SESSION_LAYERS:
        assert d._ov_btn[k].isChecked() and d._chart._ov[k] is True


# ── 4. 거래신동 단추 위치 ────────────────────────────────────────
def test_4_shindong_button_between_mireuk_and_peter(dialog):
    d = dialog("off")
    sd = d._ov_btn[MinuteChartDialog._SD_OV_KEY]
    row = _row_of(d, sd)
    assert row is not None
    i_m, i_s, i_p = (row.index(d._ov_btn["trade_mireuk"]), row.index(sd),
                     row.index(d._ov_btn["trade_peter"]))
    assert i_m + 1 == i_s and i_s + 1 == i_p, "거래미륵 · 거래신동 · 거래피터 순서여야 한다"
    assert sd.isChecked(), "실시간 표시가 요구사항 — 켜고 시작(626차)"
    # 상단 바(날짜 줄)에 남아 있지 않다
    assert d._layer_lbl not in row


# ── 2. 실거래 주체 분기 ──────────────────────────────────────────
def _canvas():
    c = MinuteChartCanvas()
    c._ov.update({"trade_mireuk": False, "trade_peter": False, "trade_shindong": True})
    return c


def test_2_owner_routing():
    c = _canvas()
    assert c._trade_owner({"source": "SHINDONG"}) == "sd"
    assert c._trade_owner({"source": "PETER2"}) == "pt"
    assert c._trade_owner({"source": "SYSTEM_AUTO"}) == "mr"
    assert c._trade_owner({"source": None}) == "mr", "NULL(미측정)은 종전대로 미륵 레이어"
    assert c._trade_shown({"source": "SHINDONG"})
    assert not c._trade_shown({"source": "SYSTEM_AUTO"})
    assert not c._trade_shown({"source": "PETER2"})
    c._ov["trade_peter"] = True
    assert c._trade_shown({"source": "PETER2"})
    c._ov["trade_shindong"] = False
    assert not c._trade_shown({"source": "SHINDONG"})
    c.deleteLater()


def test_2b_shindong_chip_uses_leg_sum():
    """신동 2계약 — 최종 다리 0.00p(본전)만 보면 1차 익절이 사라진다."""
    c = _canvas()
    c._exit_markers = [
        {"finalize": False, "source": "SHINDONG", "entry_ts": _ts(20), "pnl_pts": 1.5},
        {"finalize": False, "source": "SHINDONG", "entry_ts": _ts(90), "pnl_pts": 9.0},   # 다른 진입
        {"finalize": False, "source": "SYSTEM_AUTO", "entry_ts": _ts(20), "pnl_pts": 7.0},  # 다른 주체
    ]
    assert c._sd_partial_pts({"entry_ts": _ts(20), "pnl_pts": 0.0}) == pytest.approx(1.5)
    c.deleteLater()


def test_2c_replay_suppressed_when_real_exists():
    c = _canvas()
    assert not c._has_real_shindong()
    c._completed_trades = [{"source": "SYSTEM_AUTO"}]
    assert not c._has_real_shindong()
    c._completed_trades.append({"source": "SHINDONG"})
    assert c._has_real_shindong()
    c.deleteLater()


def test_2d_live_entry_exit_carry_source():
    c = _canvas()
    c.record_entry("LONG", 1050.0, ts=_ts(10), source="SHINDONG")
    assert c._active_trade["source"] == "SHINDONG"
    # 같은 방향 재동기(출처 모름)는 기존 출처를 지킨다
    c.sync_active_trade("LONG", 1050.5, ts=_ts(11))
    assert c._active_trade["source"] == "SHINDONG"
    c.record_exit(1051.5, ts=_ts(15), finalize=False, pnl_pts=1.5, reason="1차익절")
    assert c._exit_markers[-1]["source"] == "SHINDONG"
    assert c._exit_markers[-1]["entry_ts"] == _ts(10)
    c.record_exit(1050.0, ts=_ts(30), finalize=True, pnl_pts=0.0, reason="본전")
    assert c._completed_trades[-1]["source"] == "SHINDONG"
    assert c._sd_partial_pts(c._completed_trades[-1]) == pytest.approx(1.5)
    c.deleteLater()


def test_2e_window_live_source_mapping():
    class _W:
        pass
    w = _W()
    for principal, want in (("SHINDONG", "SHINDONG"), ("PETER", "PETER2"),
                            ("MIREUK", "SYSTEM_AUTO"), (None, None)):
        w._principal = principal
        assert md.MireukDashboard._live_trade_source(w) == want


def test_2f_reload_today_tags_entry_source():
    """재적재 경로가 trades.db `entry_source` 를 싣는다 — 실시간 태그는 다음 재적재가 바로잡는다."""
    src = open(os.path.join(_ROOT, "dashboard", "main_dashboard.py"), encoding="utf-8").read()
    body = src.split("    def reload_today(", 1)[1].split("\n    def ", 1)[0]
    assert body.count('"source": row["entry_source"]') == 2, "부분청산·최종 두 경로 모두"


def test_2g_render_smoke_both_paths():
    """실거래 있는 날 · 재생만 있는 날 둘 다 예외 없이 그린다."""
    c = _canvas()
    candles = [{"ts": _ts(i).strftime("%Y-%m-%d %H:%M:%S"), "open": 1050 + i * 0.1,
                "high": 1050.5 + i * 0.1, "low": 1049.5 + i * 0.1, "close": 1050 + i * 0.1,
                "volume": 10} for i in range(60)]
    sd = [{"entry_ts": _ts(30), "entry_price": 1053.0, "direction": "LONG", "status": "CLOSED",
           "t1": 1054.0, "t2": 1055.0, "stop_init": 1052.0,
           "legs": [{"exit_ts": _ts(35), "exit_price": 1053.5, "reason": "TP1", "pts": 0.5},
                    {"exit_ts": _ts(40), "exit_price": 1054.0, "reason": "TP2", "pts": 1.0}]},
          {"entry_ts": _ts(55), "entry_price": 1055.5, "direction": "SHORT", "status": "OPEN",
           "t1": 1054.5, "t2": 1053.5, "stop_now": 1056.5, "legs": []}]
    real = [{"direction": "LONG", "entry_price": 1051.0, "exit_price": 1052.0,
             "entry_ts": _ts(10), "exit_ts": _ts(20), "exit_reason": "본전", "pnl_pts": 0.0,
             "outcome": "EXIT", "source": "SHINDONG"}]
    for comp in (real, []):
        c.resize(1200, 700)
        c.reset_session(candles, comp, exit_markers=[], sd_trades=sd, sd_wired=True)
        img = c.grab().toImage()
        assert img.width() > 0
    c.deleteLater()
