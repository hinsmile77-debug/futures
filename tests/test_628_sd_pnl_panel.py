# -*- coding: utf-8 -*-
"""[MW0601 628차] 손익 추이 패널 — 「GP(가상)」 자리를 「신동(가상)」 **단독 표시**로 교체.

사용자 지시(2026-09-24): 신동의 손익을 **별도로 산출해서** 보여준다 — 실거래에 더하고
마커로 표시하는 방식(553차 GP)이 아니라 **신동 자체의 순손익**.

고정하는 것
-----------
1. 신동을 켜면 실거래 출처가 꺼지고(배타), 그 날 값 = **신동 순손익 합**뿐이다.
   브로커 실측 net 이 신동 화면에 새어 들어오지 않는다(실거래 행이 없는 날 포함).
2. 신동을 끄면 종전과 **완전히 같은 값** — 브로커 실측 net 이 살아 있다
   (553차 급소: 가상거래가 완전성 판정 분모에 끼면 모든 날이 「부분」이 된다).
3. 순손익은 신동이 계산한 `net_krw`(2계약 · 수수료+슬리피지 차감) 그대로 — 요율 재환산 없음.
4. 반사실 탭에는 신동이 없다. 기본값은 해제. 배너가 「미배선 · 0건 · n건」을 가른다.

실행:
    conda run -n py37_32 python -m pytest tests/test_628_sd_pnl_panel.py -q
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

from dashboard.main_dashboard import PnlHistoryPanel  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)

_DAY = "2026-09-23"
_SD_ONLY_DAY = "2026-09-22"      # 실거래가 없는 날
_BROKER = 500_000.0


class _Row(dict):
    def keys(self):
        return list(super(_Row, self).keys())


def _trade(pnl_krw=100_000.0, pnl_pts=2.0, ts=_DAY + " 10:00:00"):
    return _Row({
        "entry_ts": ts, "exit_ts": ts,
        "pnl_pts": pnl_pts, "pnl_krw": pnl_krw,
        "forward_pnl_pts": pnl_pts, "forward_pnl_krw": pnl_krw,
        "quantity": 1, "reverse_entry_enabled": 0,
        "gross_pnl_krw": pnl_krw, "commission_krw": 0.0,
        "commission_rate_used": 9.8104e-05,
        "entry_source": "SYSTEM_AUTO", "exit_reason": "TP1",
        "direction": "LONG", "grade": "A",
    })


def _sd(net=1_318_000.0, l1=7.26, l2=20.0, day=_DAY, rule="R2"):
    """shindong_trades 행(청산 완료) — 9/23 R2 분석값 형태."""
    return {"trade_date": day, "variant": "MAIN", "rule": rule, "side": -1,
            "entry_ts": day + " 09:01:00", "entry_px": 1130.5, "status": "CLOSED",
            "leg1_exit_ts": day + " 09:49:00", "leg1_pts": l1, "leg1_reason": "TP1",
            "leg2_exit_ts": day + " 11:33:00", "leg2_pts": l2, "leg2_reason": "TP2",
            "net_krw": net}


def _panel(trades, sd=None, wired=True, broker=True, mode="live"):
    p = PnlHistoryPanel(rate_mode=mode)
    p.refresh(trades, sd_positions=sd, sd_wired=wired)
    if broker:
        p._broker_pnl = {_DAY: _BROKER, _SD_ONLY_DAY: 77_777.0}
        p._broker_pnl_src = {_DAY: "broker", _SD_ONLY_DAY: "broker"}
    return p


def _set(p, keys):
    for k, cb in p._cb_origin.items():
        cb.blockSignals(True)
        cb.setChecked(k in keys)
        cb.blockSignals(False)


def _day_krw(p, day=_DAY):
    rows = p._daily_bucket(p._active_rows()).get(day, [])
    return p._effective_day_krw(day, rows)


# ── 축 ──────────────────────────────────────────────────────────────────
def test_sd_replaces_gp_origin():
    assert PnlHistoryPanel._ORIGIN_KEYS == ("auto", "manual", "unknown", "sd")
    assert PnlHistoryPanel._ORIGIN_LABEL["sd"] == "신동(가상)"
    assert "gp" not in PnlHistoryPanel._ORIGIN_LABEL
    tip = PnlHistoryPanel._ORIGIN_TIP["sd"]
    assert "가상" in tip and "전환기준" in tip and "단독" in tip


# ── 1. 신동 단독 — 실거래에 더하지 않는다 ─────────────────────────────────
def test_sd_view_is_sd_net_only_not_added_to_broker():
    p = _panel([_trade()], [_sd(net=1_318_000.0)])
    _set(p, {"sd"})
    assert _day_krw(p) == pytest.approx(1_318_000.0), "신동 화면에 실거래·브로커 net 이 섞였다"


def test_broker_net_does_not_leak_into_sd_only_day():
    """실거래 행이 없는 날은 `_day_is_whole` 이 참이다 — 브로커 net 이 새면 안 된다."""
    p = _panel([_trade()], [_sd(net=-250_000.0, l1=-3.0, l2=-3.0, day=_SD_ONLY_DAY)])
    _set(p, {"sd"})
    assert _day_krw(p, _SD_ONLY_DAY) == pytest.approx(-250_000.0)


def test_mixed_origins_collapse_to_sd_only():
    """저장된 설정·짝 패널 전파로 섞여 들어와도 신동만 남는다."""
    p = _panel([_trade()], [_sd()])
    _set(p, {"auto", "manual", "unknown", "sd"})
    assert p._active_origins() == {"sd"}
    assert all(r.get("is_sd") for r in p._active_rows())


def test_checking_sd_unchecks_real_and_vice_versa():
    p = _panel([_trade()], [_sd()])
    _set(p, {"auto", "manual", "unknown"})
    p._cb_origin["sd"].setChecked(True)          # 사용자가 신동을 켠다
    assert not any(p._cb_origin[k].isChecked() for k in ("auto", "manual", "unknown"))
    p._cb_origin["auto"].setChecked(True)        # 사용자가 자동을 켠다
    assert not p._cb_origin["sd"].isChecked()


def test_sd_stats_count_trades_and_points():
    p = _panel([_trade()], [_sd(l1=7.26, l2=20.0), _sd(net=-50_000.0, l1=-1.0, l2=-1.0,
                                                       rule="R3")])
    _set(p, {"sd"})
    n, wins, losses, ppts, _k = p._stats(p._active_rows())
    assert (n, wins, losses) == (2, 1, 1)
    assert ppts == pytest.approx(7.26 + 20.0 - 2.0), "pt 합계 = 두 다리 pt 합(계약당 × 2)"


# ── 2. 신동을 끄면 종전과 같다 ─────────────────────────────────────────────
def test_broker_net_survives_when_sd_unchecked():
    p = _panel([_trade()], [_sd()])
    _set(p, {"auto", "manual", "unknown"})
    assert _day_krw(p) == pytest.approx(_BROKER)


def test_day_total_legs_excludes_sd():
    p = _panel([_trade(), _trade(ts=_DAY + " 10:05:00")], [_sd(), _sd()])
    assert p._day_total_legs[_DAY] == 2


def test_unchecked_sd_matches_no_sd_at_all():
    a = _panel([_trade()], [_sd()])
    _set(a, {"auto", "manual", "unknown"})
    b = _panel([_trade()], None)
    _set(b, {"auto", "manual", "unknown"})
    assert _day_krw(a) == _day_krw(b)


# ── 3. 순손익 원천 ──────────────────────────────────────────────────────
def test_sd_net_is_used_as_is_not_renormalized():
    p = _panel([], [_sd(net=123_456.0)])
    r = [x for x in p._rows if x.get("is_sd")][0]
    assert p._engine_net(r) == pytest.approx(123_456.0)
    assert r["quantity"] == 2


def test_open_or_incomplete_sd_rows_are_skipped():
    bad = dict(_sd())
    bad["leg2_pts"] = None
    p = _panel([], [bad])
    assert not [x for x in p._rows if x.get("is_sd")], "청산 미완 거래를 0 으로 넣었다"


# ── 4. 반사실 · 기본값 · 배너 ───────────────────────────────────────────
def test_counterfactual_tab_hides_and_clears_sd():
    p = PnlHistoryPanel(rate_mode="creon")
    assert p._cb_origin["sd"].isChecked() is False
    assert p._cb_origin["sd"].isVisible() is False


def test_refresh_pnl_history_does_not_pass_sd_to_cf():
    import inspect
    from dashboard.main_dashboard import LogPanel
    src = inspect.getsource(LogPanel.refresh_pnl_history)
    assert "self.pnl_history_cf.refresh(rows)" in src


def test_sd_defaults_off_when_unset():
    import inspect
    src = inspect.getsource(PnlHistoryPanel._load_origin_prefs)
    assert "k != self._SD_ORIGIN" in src
    p = PnlHistoryPanel()                        # 참조를 잡아 둔다(즉시 수거 방지)
    assert p._cb_origin["sd"].isChecked() is False


@pytest.mark.parametrize("sd,wired,expect", [
    ([], False, "미배선"),
    ([], True, "0건"),
    ([_sd()], True, "청산 1건"),
])
def test_banner_separates_unwired_from_zero(sd, wired, expect):
    p = _panel([_trade()], sd, wired=wired)
    _set(p, {"sd"})
    p._refresh_sd_banner()
    assert p._sd_banner.isVisibleTo(p)
    assert expect in p._sd_banner.text()


def test_banner_hidden_when_sd_unchecked():
    p = _panel([_trade()], [_sd()])
    _set(p, {"auto"})
    p._refresh_sd_banner()
    assert not p._sd_banner.isVisibleTo(p)


def test_no_gp_marker_left_in_daily_table():
    import inspect
    src = inspect.getsource(PnlHistoryPanel._build_daily)
    assert "🟣" not in src and "_day_has_gp" not in src


def test_main_passes_sd_not_gp():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    a = src.index("    def _refresh_pnl_history(self)")
    body = src[a:a + 3000]
    assert "sd_positions=" in body and "gp_positions" not in body
    assert "load_closed_for_pnl" in body


def test_verdict_source_does_not_read_shindong_db():
    """전환기준 ① 판정 원천은 가상거래를 보지 않는다."""
    import inspect
    from utils.db_utils import fetch_daily_net_for_verdict
    src = inspect.getsource(fetch_daily_net_for_verdict)
    assert "shindong" not in src.lower()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
