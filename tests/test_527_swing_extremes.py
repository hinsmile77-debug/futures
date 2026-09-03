# -*- coding: utf-8 -*-
"""[MW0602 527차] N봉 스윙 고점·저점 피처 — 계산 규약·폴백 가시화·배선 고정.

고정하는 불변식:
  S1  값 규약 — range_pos/거리/나이가 손계산과 일치, 동률 극점은 **가장 최근** 봉.
  S2  항등식 — range_pos ≡ low_dist/(high_dist+low_dist). 재검증에서 독립 3개로 세지 말 것.
  S3  워밍업 가시화(계측 4원칙 ④) — min_bars 미만은 폴백 + swing_measured=False,
      부분 윈도우는 계산하되 swing{N}_ready=False, 윈도우 충족 시 True.
  S4  ATR 미계산이면 거리 0 이 "극점에 있다"로 읽히지 않도록 ready=False.
  S5  reset_daily 후 전일 봉이 극점으로 남지 않는다(317차 갭 오염 규약).
  S6  warm_start 는 순차 update 와 같은 상태를 만들고, 버퍼가 차 있으면 무동작.
  S7  FeatureBuilder 가 매분 전 키를 내고 STEP9 직렬화(bool→1.0)가 삼키지 않는다.
  S8  등록 — DYNAMIC_FEATURES_POOL 에 값 키 15개가 있고 플래그는 없다.
      settings 윈도우가 (20, 60) 이며 키 이름과 정합한다.
  S9  🔴 게이트 미배선 — checklist·trend_persistence·ensemble_decision 이 swing 키를
      읽지 않는다. 라이브 코호트와 전 분봉 IC 부호가 반대라 어느 방향 게이트든 틀린다
      (소급 실측, docs/…/MW0602-20260904-스윙피처…md). 배선하려면 이 테스트를 함께 고쳐야 한다.
  S10 health report 가 `_ready`/`_measured` 플래그를 상태 플래그로 분류한다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import pytest  # noqa: E402

from features.technical.swing_extremes import SwingExtremeCalculator  # noqa: E402


def _feed(calc, closes, atr=1.0, wick=0.3):
    out = None
    for c in closes:
        out = calc.update(high=c + wick, low=c - wick, close=c, atr=atr)
    return out


# ── S1 값 규약 ───────────────────────────────────────────────────────────────

def test_s1_values_match_hand_computation():
    calc = SwingExtremeCalculator(windows=(5,), min_bars=3)
    #        idx: 0    1    2    3    4    5    6
    closes = [100, 101, 103, 102, 101, 100.5, 101.5]
    out = _feed(calc, closes, atr=2.0, wick=0.5)
    # 마지막 5봉(idx 2..6): highs 103.5,102.5,101.5,101.0,102.0 → max 103.5 @idx2 (age 4)
    #                       lows  102.5,101.5,100.5,100.0,101.0 → min 100.0 @idx5 (age 1)
    assert out["swing5_high_age"] == pytest.approx(4 / 5.0)
    assert out["swing5_low_age"] == pytest.approx(1 / 5.0)
    assert out["swing5_high_dist_atr"] == pytest.approx((103.5 - 101.5) / 2.0)
    assert out["swing5_low_dist_atr"] == pytest.approx((101.5 - 100.0) / 2.0)
    assert out["swing5_range_pos"] == pytest.approx((101.5 - 100.0) / (103.5 - 100.0))
    assert out["swing5_ready"] is True
    assert out["swing_measured"] is True
    # 세션 전체: 고점 103.5@idx2 (age 4/7), 저점 99.5@idx0 (age 6/7)
    assert out["swing_day_high_age"] == pytest.approx(4 / 7.0)
    assert out["swing_day_low_age"] == pytest.approx(6 / 7.0)
    assert out["swing_day_range_pos"] == pytest.approx((101.5 - 99.5) / (103.5 - 99.5))


def test_s1b_tie_picks_most_recent_bar():
    calc = SwingExtremeCalculator(windows=(4,), min_bars=2)
    _feed(calc, [100, 105, 101, 105])          # 고점 105 가 idx1·idx3 동률
    out = _feed(calc, [102])                   # 창: idx1..4 → 고점 idx3 → age 1
    assert out["swing4_high_age"] == pytest.approx(1 / 4.0)


def test_s1c_new_high_this_bar_has_zero_age_and_zero_distance():
    calc = SwingExtremeCalculator(windows=(5,), min_bars=2)
    out = _feed(calc, [100, 101, 102, 103, 104, 106], wick=0.0)
    assert out["swing5_high_age"] == 0.0
    assert out["swing5_high_dist_atr"] == 0.0
    assert out["swing5_range_pos"] == 1.0


# ── S2 항등식 ────────────────────────────────────────────────────────────────

def test_s2_range_pos_identity_with_distances():
    import random
    rnd = random.Random(7)
    calc = SwingExtremeCalculator(windows=(20, 60), min_bars=5)
    px = 400.0
    for _ in range(120):
        px += rnd.uniform(-0.6, 0.6)
        out = calc.update(high=px + rnd.uniform(0, .3), low=px - rnd.uniform(0, .3),
                          close=px, atr=1.7)
        if not out["swing_measured"]:
            continue
        for p in ("swing20_", "swing60_", "swing_day_"):
            hd, ld = out[p + "high_dist_atr"], out[p + "low_dist_atr"]
            if hd + ld > 1e-9:
                assert out[p + "range_pos"] == pytest.approx(ld / (hd + ld), abs=1e-9)


# ── S3/S4 폴백 가시화 ────────────────────────────────────────────────────────

def test_s3_warmup_flags_are_visible():
    calc = SwingExtremeCalculator(windows=(5, 8), min_bars=3)
    out = _feed(calc, [100, 101])
    assert out["swing_measured"] is False
    assert out["swing5_range_pos"] == 0.5 and out["swing5_high_dist_atr"] == 0.0
    out = _feed(calc, [102])                   # 3봉 — 측정은 되지만 창 미충족
    assert out["swing_measured"] is True
    assert out["swing5_ready"] is False and out["swing8_ready"] is False
    assert out["swing_day_ready"] is True      # 세션 창은 경과 봉이 곧 창
    _feed(calc, [103, 104])
    out = _feed(calc, [105])                   # 6봉 — 5창 충족, 8창 미충족
    assert out["swing5_ready"] is True and out["swing8_ready"] is False
    out = _feed(calc, [106, 107])              # 8봉
    assert out["swing8_ready"] is True


def test_s3b_fallback_keys_equal_update_keys():
    calc = SwingExtremeCalculator(windows=(20, 60), min_bars=5)
    fb = calc.fallback()
    assert set(fb) == set(calc.keys())
    out = _feed(calc, [100 + i * 0.1 for i in range(10)])
    assert set(out) == set(calc.keys())


def test_s4_atr_not_ready_lowers_ready_flag_instead_of_faking_zero_distance():
    calc = SwingExtremeCalculator(windows=(3,), min_bars=2)
    out = _feed(calc, [100, 101, 102, 103], atr=0.0, wick=0.0)
    assert out["swing_measured"] is True
    assert out["swing3_high_dist_atr"] == 0.0
    assert out["swing3_ready"] is False
    assert out["swing_day_ready"] is False
    assert out["swing3_range_pos"] == 1.0      # ATR 무관 값은 정상 계산(심지 0 → 종가=고점)


# ── S5 일간 리셋 ─────────────────────────────────────────────────────────────

def test_s5_reset_daily_drops_previous_day_extremes():
    calc = SwingExtremeCalculator(windows=(5,), min_bars=2)
    _feed(calc, [100, 120, 100, 100, 100])     # 전일 고점 120
    calc.reset_daily()
    assert calc.n_bars == 0
    out = _feed(calc, [100, 101, 102])         # 갭 다운 후 당일
    assert out["swing_day_high_dist_atr"] == pytest.approx(0.3)   # 당일 고점 102.3 만 본다
    assert out["swing5_high_age"] == 0.0


# ── S6 재기동 워밍업 ─────────────────────────────────────────────────────────

def test_s6_warm_start_equals_sequential_and_is_noop_when_populated():
    closes = [100 + ((i * 7) % 11) * 0.2 for i in range(30)]
    seq = SwingExtremeCalculator(windows=(20,), min_bars=5)
    _feed(seq, closes)
    ws = SwingExtremeCalculator(windows=(20,), min_bars=5)
    n = ws.warm_start([(c + 0.3, c - 0.3, c) for c in closes])
    assert n == 30
    nxt = 101.0
    a = seq.update(high=nxt + .3, low=nxt - .3, close=nxt, atr=1.0)
    b = ws.update(high=nxt + .3, low=nxt - .3, close=nxt, atr=1.0)
    assert a == b
    assert ws.warm_start([(1, 1, 1)]) == 0     # 이미 차 있으면 무동작


def test_s6b_feature_builder_warm_start_hook():
    from features.feature_builder import FeatureBuilder
    fb = FeatureBuilder()
    n = fb.set_intraday_ohlc_history([(390.3, 389.9, 390.0)] * 25)
    assert n == 25
    assert fb.swing.n_bars == 25
    assert fb.set_intraday_ohlc_history([(1, 1, 1)]) == 0


# ── S7 FeatureBuilder 배선 ───────────────────────────────────────────────────

def test_s7_feature_builder_emits_all_keys_and_step9_serializes():
    from features.feature_builder import FeatureBuilder
    fb = FeatureBuilder()
    out = None
    for i in range(25):
        out = fb.build({"close": 390.0 + i * 0.1, "high": 390.15 + i * 0.1,
                        "low": 389.9 + i * 0.1, "open": 390.0 + i * 0.1,
                        "volume": 100 + i})
    for k in fb.swing.keys():
        assert k in out, k
    assert out["swing_measured"] is True
    assert out["swing20_ready"] is True and out["swing60_ready"] is False
    assert out["swing20_high_age"] == 0.0     # 단조 상승 → 이번 봉이 고점
    # STEP9 `_feat_clean` 관례(bool→1.0) — hurst_ready 와 동일 취급
    clean = {k: round(float(v), 4) for k, v in out.items() if v is not None and v == v}
    assert clean["swing20_ready"] == 1.0 and clean["swing_measured"] == 1.0
    fb.reset_daily()
    assert fb.swing.n_bars == 0


# ── S8 등록 정합 ─────────────────────────────────────────────────────────────

def test_s8_pool_registration_matches_calculator_keys():
    from config.constants import DYNAMIC_FEATURES_POOL
    from config.settings import SWING_EXTREME_WINDOWS, SWING_EXTREME_MIN_BARS
    assert tuple(SWING_EXTREME_WINDOWS) == (20, 60)
    assert SWING_EXTREME_MIN_BARS >= 2
    calc = SwingExtremeCalculator(windows=SWING_EXTREME_WINDOWS, min_bars=SWING_EXTREME_MIN_BARS)
    value_keys = {k for k in calc.keys() if not k.endswith(("_ready", "_measured"))}
    assert len(value_keys) == 15
    pool = set(DYNAMIC_FEATURES_POOL)
    missing = value_keys - pool
    assert not missing, "POOL 미등록: %s" % sorted(missing)
    flags = {k for k in calc.keys() if k.endswith(("_ready", "_measured"))}
    assert not (flags & pool), "상태 플래그가 학습 후보에 들어갔다: %s" % sorted(flags & pool)


# ── S9 게이트 미배선 (의도적 마찰) ───────────────────────────────────────────

def test_s9_swing_keys_are_not_consumed_by_entry_gates():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gate_files = [
        os.path.join(root, "strategy", "entry", "checklist.py"),
        os.path.join(root, "strategy", "entry", "trend_persistence.py"),
        os.path.join(root, "model", "ensemble_decision.py"),
    ]
    for f in gate_files:
        with open(f, encoding="utf-8") as fh:
            src = fh.read()
        assert "swing" not in src.lower(), (
            "%s 가 swing 피처를 참조한다 — 527차 S9: 게이트 배선은 섀도 채널 판정 뒤 "
            "주간회의 승인 경로만" % os.path.basename(f))


# ── S10 health report 분류 ───────────────────────────────────────────────────

def test_s10_health_report_treats_flags_as_benign():
    from scripts.feature_health_report import is_benign_flag
    for k in ("swing20_ready", "swing60_ready", "swing_day_ready", "swing_measured",
              "trend_efficiency_ready", "hurst_ready"):
        assert is_benign_flag(k), k
    assert not is_benign_flag("swing20_range_pos")
