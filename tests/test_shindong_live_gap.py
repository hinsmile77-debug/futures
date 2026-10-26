# -*- coding: utf-8 -*-
"""[MW0602 2026-10-26] 신동 가상 ↔ 실거래 체결 차 대조(`display.live_gap`).

손익 추이 「신동」·「신동실」 배너가 이 값을 쓴다. 고정하는 것:
  A. 같은 날·같은 방향·tol 분 이내만, 가장 가까운 것끼리 1:1 로 짝짓는다
  B. 같은 진입의 여러 레그는 한 포지션(수량 가중 pt) — 계측 4원칙 ①
  C. 짝 0건은 gap_avg_pt=None(미측정) — 0.0 이 아니다(계측 4원칙 ②)
  D. 짝 없는 실거래는 n_unmatched 로 남는다(계측 4원칙 ③)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.shindong.display import live_gap


def _sd(ts, side, pts, status="CLOSED"):
    return {"entry_ts": ts, "side": side, "status": status, "entry_px": 800.0,
            "leg1_exit_ts": ts, "leg1_exit_px": 800.0, "leg1_pts": pts, "leg1_net": 0.0,
            "leg2_exit_ts": ts, "leg2_exit_px": 800.0, "leg2_pts": pts, "leg2_net": 0.0}


def _lv(ts, d, pts, q=1):
    return {"entry_ts": ts, "direction": d, "pnl_pts": pts, "quantity": q}


def test_a_matches_nearest_same_day_same_side():
    sd = [_sd("2026-10-26 09:08:00", 1, -11.36),
          _sd("2026-10-26 09:20:00", -1, 5.0),
          _sd("2026-10-27 09:08:00", 1, 3.0)]
    g = live_gap(sd, [_lv("2026-10-26 09:09:33", "LONG", -12.18)])
    assert g["n_matched"] == 1
    p = g["pairs"][0]
    assert abs(p["gap"] - (-0.82)) < 1e-9
    assert abs(p["lag_min"] - 1.55) < 1e-9


def test_a_outside_tolerance_or_wrong_side_is_unmatched():
    sd = [_sd("2026-10-26 09:00:00", 1, 1.0)]
    g = live_gap(sd, [_lv("2026-10-26 09:06:00", "LONG", 1.0),
                      _lv("2026-10-26 09:01:00", "SHORT", 1.0)])
    assert g["n_matched"] == 0 and g["n_unmatched"] == 2


def test_b_legs_of_one_entry_are_one_position():
    sd = [_sd("2026-10-26 10:00:00", -1, 12.0)]
    g = live_gap(sd, [_lv("2026-10-26 10:01:00", "SHORT", 12.0, 1),
                      _lv("2026-10-26 10:01:00", "SHORT", 9.0, 2)])
    assert g["n_live"] == 1 and g["n_matched"] == 1
    assert abs(g["pairs"][0]["live_pt"] - 10.0) < 1e-9      # (12×1 + 9×2) / 3


def test_c_no_pair_is_unmeasured_not_zero():
    g = live_gap([], [])
    assert g["gap_avg_pt"] is None and g["lag_avg_min"] is None
    g = live_gap([_sd("2026-10-26 09:00:00", 1, 1.0, status="OPEN")],
                 [_lv("2026-10-26 09:01:00", "LONG", 1.0)])
    assert g["gap_avg_pt"] is None and g["n_unmatched"] == 1


def test_d_one_virtual_is_not_reused():
    sd = [_sd("2026-10-26 09:00:00", 1, 1.0)]
    g = live_gap(sd, [_lv("2026-10-26 09:01:00", "LONG", 1.0),
                      _lv("2026-10-26 09:02:00", "LONG", 1.0)])
    assert g["n_matched"] == 1 and g["n_unmatched"] == 1
