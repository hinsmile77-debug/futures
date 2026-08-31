# -*- coding: utf-8 -*-
"""[MW0601 507차 후속 / F-11] 승패 표기에 축을 박는다 — gross pt vs net 원.

**판정 축은 바꾸지 않는다.** `wins`/`losses`/`win_rate` 는 소비처가 많아 무변경이고
(461차 `mdd_pct` 유형의 조용한 재정의 방지), `wins_net`/`losses_net`/`win_rate_net`
을 **추가만** 한다.

2026-08-31 마감 로그: `승=12 패=8 PnL=-6,389,508원` — 승패는 gross pt 축인데 PnL 은
net 축이라 한 줄에서 단위가 갈렸다. net 축으로 세면 9승 11패, 승률 60% → 45%.
1계약 왕복 수수료 약 10,220원이 손익분기 0.204pt 를 만들기 때문이다.
⚠ 실전 전환 기준 ③의 「승률 ≥ 53%」가 어느 축인지는 문서에 없다 — **주간회의 안건**.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.constants import POSITION_SHORT                      # noqa: E402
from config.constants import MINI_FUTURES_PT_VALUE                # noqa: E402
from strategy.position.position_tracker import PositionTracker    # noqa: E402

# 라이브는 미니선물이다(1pt = 50,000원). 트래커 기본값은 정규선물(250,000)이라
# 그대로 쓰면 손익분기가 5배로 벌어져 이 사고를 재현하지 못한다.
PT = MINI_FUTURES_PT_VALUE


class _Row(dict):
    """`sqlite3.Row` 흉내 — `restore_daily_stats` 가 `keys()`/`[]` 만 쓴다."""

    def keys(self):
        return list(super(_Row, self).keys())


def _leg(entry_ts, pnl_pts, qty, commission):
    return _Row(entry_ts=entry_ts, exit_price=1000.0, entry_price=1000.0,
                pnl_pts=pnl_pts, quantity=qty, commission_krw=commission,
                forward_pnl_pts=pnl_pts, forward_commission_krw=commission)


def test_a_stats_expose_both_axes():
    """ⓐ `daily_stats()` 가 두 축을 동시에 낸다."""
    t = PositionTracker(pt_value=PT)
    s = t.daily_stats()
    for k in ("wins", "losses", "win_rate",
              "wins_net", "losses_net", "win_rate_net"):
        assert k in s, "축 키 누락: %s" % k


def test_b_axes_split_on_breakeven_position():
    """ⓑ **손익분기 근처 이익**은 gross 승 / net 패로 갈린다.

    08-31 CASE-04 계열 재현: gross +0.20pt 인데 왕복 수수료를 빼면 net 음수.
    1계약 왕복 수수료 10,220원 ⇒ 손익분기 0.204pt.
    """
    t = PositionTracker(pt_value=PT)
    t.restore_daily_stats([_leg("2026-08-31 10:46:41", 0.20, 1, 10_220.0)])
    s = t.daily_stats()
    assert s["trades"] == 1
    assert s["wins"] == 1, "gross pt 축은 승이어야 한다(판정 축 무변경)"
    assert s["wins_net"] == 0, "net 축은 패여야 한다 — 수수료가 이익을 넘는다"
    assert s["losses"] == 0 and s["losses_net"] == 1


def test_c_clear_win_counts_on_both_axes():
    """ⓒ 확실한 이익은 두 축 모두 승 — 병기가 값을 왜곡하지 않는다."""
    t = PositionTracker(pt_value=PT)
    t.restore_daily_stats([_leg("2026-08-31 12:16:32", 2.08, 1, 10_220.0)])
    s = t.daily_stats()
    assert (s["wins"], s["wins_net"]) == (1, 1)


def test_d_clear_loss_counts_on_both_axes():
    t = PositionTracker(pt_value=PT)
    t.restore_daily_stats([_leg("2026-08-31 09:28:47", -3.52, 1, 10_220.0)])
    s = t.daily_stats()
    assert (s["wins"], s["wins_net"]) == (0, 0)
    assert (s["losses"], s["losses_net"]) == (1, 1)


def test_e_multileg_position_counted_once_on_both_axes():
    """ⓔ 다레그 포지션은 **포지션 단위 1건**이다(계측 4원칙 ①).

    08-31 14:33:38 재현 — TP1 + TP2 + 트레일 3레그.
    """
    ts = "2026-08-31 14:33:38"
    t = PositionTracker(pt_value=PT)
    t.restore_daily_stats([
        _leg(ts, 1.5667, 1, 10_220.0),
        _leg(ts, 2.3067, 1, 10_220.0),
        _leg(ts, 0.8467, 1, 10_220.0),
    ])
    s = t.daily_stats()
    assert s["trades"] == 1, "레그 3행이 3트레이드로 세어졌다 — 단위 회귀"
    assert s["wins"] == 1 and s["wins_net"] == 1


def test_f_legacy_keys_unchanged_regression():
    """ⓕ 기존 키의 **값**이 net 축 추가로 바뀌지 않는다(회귀)."""
    legs = [_leg("2026-08-31 10:46:41", 0.20, 1, 10_220.0),
            _leg("2026-08-31 09:28:47", -3.52, 1, 10_220.0),
            _leg("2026-08-31 12:16:32", 2.08, 1, 10_220.0)]
    t = PositionTracker(pt_value=PT)
    t.restore_daily_stats(legs)
    s = t.daily_stats()
    assert s["trades"] == 3
    assert s["wins"] == 2                       # gross: +0.20 · +2.08
    assert s["win_rate"] == pytest.approx(2 / 3)
    assert s["wins_net"] == 1                   # net: +2.08 만 살아남는다
    assert s["win_rate_net"] == pytest.approx(1 / 3)


def test_g_reset_clears_net_axis():
    """ⓖ 일일 리셋이 net 축 카운터도 지운다 — 다음 날로 새지 않는다."""
    t = PositionTracker(pt_value=PT)
    t.restore_daily_stats([_leg("2026-08-31 12:16:32", 2.08, 1, 10_220.0)])
    assert t.daily_stats()["wins_net"] == 1
    t.reset_daily()
    s = t.daily_stats()
    assert s["wins_net"] == 0 and s["losses_net"] == 0


def test_h_live_close_path_counts_net_axis():
    """ⓗ 라이브 청산 경로(`close_position`)도 net 축을 센다.

    복원 경로만 고치면 재시작 전후 값이 갈린다.
    """
    # 08-31 10:46:41 재현 — 진입 1047.14 SHORT 1계약, +0.20pt 에서 청산.
    # 그 가격대의 1계약 왕복 수수료가 이익 10,000원을 넘어(손익분기 약 0.205pt)
    # gross 승 / net 패로 갈린다.
    t = PositionTracker(pt_value=PT)
    t.open_position(POSITION_SHORT, 1047.14, 1, atr=3.0)
    t.close_position(1046.94, "TP1 부분청산 33%")
    s = t.daily_stats()
    assert s["trades"] == 1
    assert s["wins"] == 1
    assert s["wins_net"] == 0, "라이브 경로에 net 축이 안 붙었다"


def test_i_daily_close_log_prints_both_axes():
    """ⓘ 마감 로그 문구에 **두 축이 모두** 박혀 있다.

    문자열을 코드에서 직접 확인한다 — 이 표기가 F-11 의 산출물 자체다.
    """
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert "(gross pt 기준)" in src
    assert "net 기준 {stats.get('wins_net', '?')}승" in src
