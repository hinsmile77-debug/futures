# -*- coding: utf-8 -*-
"""[MW0601 708차] 손익 추이 패널 — 신동 **실거래** 출처(sdx) 신설 · 재생 라벨 「신동(재생)」.

사건(2026-10-22): 「신동(가상)」 화면이 +2,599,065원(shindong.db MAIN 재생)인데 브로커 실측은
+1,127,174원이었다. 실거래 신동(`entry_source=SHINDONG`, trades.db 9포지션 +1,127,139원)은
출처축에 등록돼 있지 않아 「미측정」으로 떨어지고 있었다(`[출처축] 미분류 entry_source ['SHINDONG']`).

고정하는 것
-----------
1. SHINDONG 진입은 `sdx` — 「미측정」도 미분류 경고도 아니다.
2. sdx 는 **실거래**다 — 실거래 출처를 전부 켜면 그 날 값이 브로커 net 이다.
3. sdx 단독 = 신동 실거래 손익 합(재생 net 이 섞이지 않는다).
4. sdx ↔ sd(재생) 배타, sdx ↔ pt2bf(가상 백필) 배타.

실행:
    conda run -n py37_32 python -m pytest tests/test_708_shindong_live_origin.py -q
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

from config.constants import SHINDONG_ENTRY_SOURCE  # noqa: E402
from dashboard.main_dashboard import PnlHistoryPanel  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)

_DAY = "2026-10-22"
_BROKER = 1_127_174.0
_REAL = ("auto", "manual", "unknown", "pt2", "sdx")


class _Row(dict):
    def keys(self):
        return list(super(_Row, self).keys())


def _trade(pnl_krw, src, ts):
    return _Row({
        "entry_ts": ts, "exit_ts": ts,
        "pnl_pts": pnl_krw / 100_000.0, "pnl_krw": pnl_krw,
        "forward_pnl_pts": pnl_krw / 100_000.0, "forward_pnl_krw": pnl_krw,
        "quantity": 2, "reverse_entry_enabled": 0,
        "gross_pnl_krw": pnl_krw, "commission_krw": 0.0,
        "commission_rate_used": 9.8104e-05,
        "entry_source": src, "exit_reason": "하드스톱(틱)",
        "direction": "SHORT", "grade": "A",
    })


def _sd_replay(net=2_599_065.0):
    return {"trade_date": _DAY, "variant": "MAIN", "rule": "R3", "side": -1,
            "entry_ts": _DAY + " 09:37:00", "entry_px": 882.3, "status": "CLOSED",
            "leg1_exit_ts": _DAY + " 09:45:00", "leg1_pts": 8.2, "leg1_reason": "TP1",
            "leg2_exit_ts": _DAY + " 09:47:00", "leg2_pts": 11.2, "leg2_reason": "TP2",
            "net_krw": net}


def _panel():
    trades = [_trade(-384_351.0, SHINDONG_ENTRY_SOURCE, _DAY + " 09:33:05"),
              _trade(400_730.0, SHINDONG_ENTRY_SOURCE, _DAY + " 13:22:05"),
              _trade(50_000.0, "SYSTEM_AUTO", _DAY + " 14:00:00")]
    p = PnlHistoryPanel(rate_mode="live")
    p.refresh(trades, sd_positions=[_sd_replay()], sd_wired=True)
    p._broker_pnl = {_DAY: _BROKER}
    p._broker_pnl_src = {_DAY: "broker"}
    return p


def _set(p, keys):
    for k, cb in p._cb_origin.items():
        cb.blockSignals(True)
        cb.setChecked(k in keys)
        cb.blockSignals(False)


def _day_krw(p):
    rows = p._daily_bucket(p._active_rows()).get(_DAY, [])
    return p._effective_day_krw(_DAY, rows)


def test_shindong_entry_is_sdx_not_unknown():
    p = _panel()
    origins = {r["origin"] for r in p._rows if r.get("entry_source") == SHINDONG_ENTRY_SOURCE}
    assert origins == {"sdx"}
    assert SHINDONG_ENTRY_SOURCE not in p._unrecognized_sources


def test_labels_say_live_vs_replay():
    assert PnlHistoryPanel._ORIGIN_LABEL["sdx"] == "신동"
    assert PnlHistoryPanel._ORIGIN_LABEL["sd"] == "신동(재생)"
    assert "실거래" in PnlHistoryPanel._ORIGIN_TIP["sdx"]
    tip = PnlHistoryPanel._ORIGIN_TIP["sd"]
    assert "실제 체결이 아니다" in tip and "주문이 나간 적 없다" not in tip


def test_all_real_origins_equal_broker_net():
    p = _panel()
    _set(p, set(_REAL))
    assert _day_krw(p) == pytest.approx(_BROKER)


def test_sdx_only_is_live_shindong_sum_not_replay():
    p = _panel()
    _set(p, {"sdx"})
    assert _day_krw(p) == pytest.approx(-384_351.0 + 400_730.0)


def test_sdx_and_replay_are_exclusive():
    p = _panel()
    _set(p, set(_REAL))
    p._cb_origin["sd"].setChecked(True)
    assert not p._cb_origin["sdx"].isChecked()
    p._cb_origin["sdx"].setChecked(True)
    assert not p._cb_origin["sd"].isChecked()


def test_sdx_excludes_peter2_backfill():
    p = _panel()
    _set(p, {"pt2", "pt2bf"})
    p._cb_origin["sdx"].setChecked(True)
    assert not p._cb_origin["pt2bf"].isChecked()
