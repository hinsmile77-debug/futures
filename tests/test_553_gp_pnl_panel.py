# -*- coding: utf-8 -*-
"""[MW0601 553차 / Phase 4] 손익 추이 패널 「GP(가상)」 구분의 불변식.

🔴 이 기능의 급소는 **브로커 net 대사 경로**다
--------------------------------------------
`_effective_day_krw()` 는 이 패널의 **단일 관문**이고, 그 안의 `_day_is_whole()` 은
「그 날 실거래 행이 전부 남아 있는가」로 브로커 실측 net 사용 여부를 정한다.
브로커 net 은 예탁금 차액(익일가예탁현금 − 예탁현금)이라 **그 날 전체의 합**이고
거래별로 쪼갤 수 없다.

GP 가상거래를 실거래와 같은 경로로 흘리면 두 방향으로 다 깨진다:

  · GP 해제 시 → `_day_total_legs` 분모에 GP 가 끼어 모든 날이 「부분」이 되고
    **브로커 실측 net 을 통째로 못 쓰게 된다**(전환기준 ① 판정 원천이 죽는다).
  · GP 체크 시 → 브로커 net(실거래 전용)이 **가상 포함 집합의 손익**으로 표시된다.
    493차가 경고한 「조용히 그럴듯한 값」 그 자체다.

그래서 **분리 합성**한다: `실거래분(브로커 or 엔진 net) + GP분(단순 합)`.
이 파일이 그 불변식을 고정한다.

실행:
    conda run -n py37_32 python -m pytest tests/test_553_gp_pnl_panel.py -v
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

from config.constants import MINI_FUTURES_PT_VALUE  # noqa: E402
from dashboard.main_dashboard import PnlHistoryPanel  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)

_DAY = "2026-09-10"
_BROKER = 500_000.0


class _Row(dict):
    """`sqlite3.Row` 처럼 인덱싱되는 최소 스텁 — 패널은 `r["col"]` 로만 읽는다."""

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


def _gp(pnl_pt=3.0, ts=_DAY + " 11:00:00", cid="GP_LONG_GB90"):
    return {"challenger_id": cid, "entry_ts": ts, "exit_ts": ts,
            "direction": 1, "entry_price": 1100.0, "exit_price": 1103.0,
            "pnl_pt": pnl_pt, "exit_reason": "TIME",
            "commission_rate_used": 9.8104e-05, "broker_channel": "CYBOS"}


def _panel(trades, gp_positions=None, gp_wired=True, broker=True, mode="live"):
    p = PnlHistoryPanel(rate_mode=mode)
    p.refresh(trades, gp_positions=gp_positions, gp_wired=gp_wired)
    if broker:
        # 브로커 실측이 있는 날을 만든다 — refresh() 가 덮어쓰므로 뒤에 주입한다.
        p._broker_pnl = {_DAY: _BROKER}
        p._broker_pnl_src = {_DAY: "broker"}
    return p


def _set_origins(p, keys):
    for k, cb in p._cb_origin.items():
        cb.blockSignals(True)
        cb.setChecked(k in keys)
        cb.blockSignals(False)


def _day_krw(p):
    rows = p._daily_bucket(p._active_rows()).get(_DAY, [])
    return p._effective_day_krw(_DAY, rows)


# ── 축 존재 ──────────────────────────────────────────────────────────────────

def test_gp_is_a_fourth_origin_key():
    assert PnlHistoryPanel._ORIGIN_KEYS == ("auto", "manual", "unknown", "gp")
    assert PnlHistoryPanel._ORIGIN_LABEL["gp"] == "GP(가상)"


def test_gp_tooltip_says_it_is_not_real():
    tip = PnlHistoryPanel._ORIGIN_TIP["gp"]
    assert "가상" in tip and "실적이 아니다" in tip
    assert "전환기준" in tip


# ── 🔴 급소 1: GP 해제 시 브로커 실측이 살아 있어야 한다 ────────────────────

def test_broker_net_survives_when_gp_unchecked():
    """GP 를 분모에 넣으면 모든 날이 「부분」이 되어 실측을 못 쓴다."""
    p = _panel([_trade()], [_gp()])
    _set_origins(p, {"auto", "manual", "unknown"})
    assert _day_krw(p) == pytest.approx(_BROKER), (
        "GP 해제인데 브로커 실측 net 이 안 쓰였다 — _day_total_legs 에 GP 가 끼었다")


def test_day_total_legs_excludes_gp():
    p = _panel([_trade(), _trade(ts=_DAY + " 10:05:00")], [_gp(), _gp()])
    assert p._day_total_legs[_DAY] == 2, "완전성 판정 분모에 가상거래가 들어갔다"


def test_unchecked_gp_matches_no_gp_at_all():
    """켜지 않으면 종전과 **완전히 같은 값**이어야 한다."""
    with_gp = _panel([_trade()], [_gp()])
    _set_origins(with_gp, {"auto", "manual", "unknown"})
    without = _panel([_trade()], None)
    _set_origins(without, {"auto", "manual", "unknown"})
    assert _day_krw(with_gp) == _day_krw(without)


# ── 🔴 급소 2: GP 체크 시 분리 합성 ─────────────────────────────────────────

def test_checked_gp_adds_to_broker_net_not_replaces():
    p = _panel([_trade()], [_gp(pnl_pt=3.0)])
    _set_origins(p, {"auto", "manual", "unknown", "gp"})
    expect = _BROKER + 3.0 * MINI_FUTURES_PT_VALUE
    assert _day_krw(p) == pytest.approx(expect), (
        "브로커 실측 net 에 GP 를 **더하는** 분리 합성이어야 한다")


def test_gp_only_view_excludes_real_trades():
    p = _panel([_trade()], [_gp(pnl_pt=3.0)])
    _set_origins(p, {"gp"})
    # 실거래를 전부 걸렀으므로 브로커 net 은 쓰지 못한다 → GP 분만 남는다
    assert _day_krw(p) == pytest.approx(3.0 * MINI_FUTURES_PT_VALUE)


def test_gp_uses_mini_futures_multiplier():
    """🔴 원문서가 250,000원/pt 로 5배 과대계상했던 지점이다."""
    p = _panel([], [_gp(pnl_pt=1.0)], broker=False)
    _set_origins(p, {"gp"})
    assert _day_krw(p) == pytest.approx(MINI_FUTURES_PT_VALUE)
    assert MINI_FUTURES_PT_VALUE == 50_000


def test_gp_rows_are_marked_and_have_unit_quantity():
    p = _panel([_trade()], [_gp()])
    gp_rows = [r for r in p._rows if r.get("is_gp")]
    assert len(gp_rows) == 1
    assert gp_rows[0]["origin"] == "gp"
    assert gp_rows[0]["quantity"] == 1
    assert gp_rows[0]["entry_source"] == "GP_SHADOW"


def test_gp_net_is_not_rate_renormalized():
    """GP net 은 이미 현행 비용 모델이다 — 요율 재환산 대상이 아니다."""
    p = _panel([], [_gp(pnl_pt=2.0)], broker=False)
    row = [r for r in p._rows if r.get("is_gp")][0]
    assert p._engine_net(row) == pytest.approx(2.0 * MINI_FUTURES_PT_VALUE)


# ── 반사실 탭은 가상거래를 다루지 않는다 ────────────────────────────────────

def test_counterfactual_tab_hides_and_clears_gp():
    """반사실 탭은 **실거래의 요율 축**을 묻는 곳이다."""
    p = PnlHistoryPanel(rate_mode="creon")
    assert p._cb_origin["gp"].isChecked() is False
    assert p._cb_origin["gp"].isVisible() is False


def test_refresh_pnl_history_does_not_pass_gp_to_cf():
    import inspect
    from dashboard.main_dashboard import LogPanel
    src = inspect.getsource(LogPanel.refresh_pnl_history)
    assert "self.pnl_history_cf.refresh(rows)" in src, (
        "반사실 패널에 gp_positions 가 넘어가면 요율 반사실이 가상거래를 포함하게 된다")


# ── 미배선 ≠ 0건 (계측 4원칙 ②) ─────────────────────────────────────────────

@pytest.mark.parametrize("gp,wired,expect", [
    ([], False, "미배선"),
    ([], True, "0건"),
    ([_gp()], True, "1건"),
])
def test_banner_separates_unwired_from_zero(gp, wired, expect):
    p = _panel([_trade()], gp, gp_wired=wired)
    _set_origins(p, {"auto", "manual", "unknown", "gp"})
    p._refresh_gp_banner()
    # ⚠ `isVisible()` 은 조상이 show() 되지 않으면 항상 False 다(offscreen 테스트).
    #   위젯 자신의 표시 의도는 `isVisibleTo(부모)` 로 본다.
    assert p._gp_banner.isVisibleTo(p)
    assert expect in p._gp_banner.text()


def test_banner_hidden_when_gp_unchecked():
    p = _panel([_trade()], [_gp()])
    _set_origins(p, {"auto", "manual", "unknown"})
    p._refresh_gp_banner()
    assert not p._gp_banner.isVisibleTo(p)


def test_banner_warns_against_using_it_for_the_gate():
    p = _panel([_trade()], [_gp()])
    _set_origins(p, {"auto", "manual", "unknown", "gp"})
    p._refresh_gp_banner()
    assert "전환기준" in p._gp_banner.text()


# ── 셀 마커 ─────────────────────────────────────────────────────────────────

def test_day_with_gp_is_flagged():
    p = _panel([_trade()], [_gp()])
    _set_origins(p, {"auto", "manual", "unknown", "gp"})
    rows = p._daily_bucket(p._active_rows())[_DAY]
    assert p._day_has_gp(rows) is True
    _set_origins(p, {"auto"})
    rows = p._daily_bucket(p._active_rows()).get(_DAY, [])
    assert p._day_has_gp(rows) is False


# ── 기본값 ──────────────────────────────────────────────────────────────────

def test_gp_defaults_off_when_unset():
    """🔴 기본 해제 — 판정 원천 화면이 기본 상태에서 바뀌면 안 된다.

    ⚠ 다른 키는 검사하지 않는다 — 그건 **사용자가 저장한 실제 설정**이라
      테스트가 강제할 값이 아니다(초판이 그걸 True 로 단정해 깨졌다).
    """
    import inspect
    src = inspect.getsource(PnlHistoryPanel._load_origin_prefs)
    assert "k != self._GP_ORIGIN" in src, (
        "gp 의 기본값이 다른 키와 같아졌다 — 켜진 채로 배포되면 판정 화면이 오염된다")
    p = PnlHistoryPanel()
    assert p._cb_origin["gp"].isChecked() is False
    assert p._load_origin_prefs()["gp"] is False


# ── 판정 함수는 패널과 무관하다 ─────────────────────────────────────────────

def test_verdict_source_does_not_read_challenger_db():
    """전환기준 ① 판정 원천(`fetch_daily_net_for_verdict`)은 GP 를 보지 않는다."""
    import inspect
    from utils.db_utils import fetch_daily_net_for_verdict
    src = inspect.getsource(fetch_daily_net_for_verdict)
    assert "CHALLENGER" not in src.upper()
    assert "challenger_trades" not in src


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
