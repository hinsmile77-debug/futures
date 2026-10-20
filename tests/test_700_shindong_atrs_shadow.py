# -*- coding: utf-8 -*-
"""[MW0601 700차] 신동 섀도 SHADOW_ATRS — v3 MAIN + R3 초기 손절 진입가 ∓ 0.25×ATR14(넓힐 때만).

고정하는 것
  A. 사전등록: k=0.25 · 채점 시작 2026-10-21 · VARIANTS 끝 · MAIN 값·SPEC_VERSION 무변경.
  B. 엔진: R3 손절만 넓어진다(현행보다 좁히지 않음) · R2 무변경 · ATR14 없으면 현행 손절 + notes 폴백 기록 ·
     MAIN 과 같은 트레일(4/4)을 쓴다.
  C. 리포트 라벨.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest  # noqa: E402

from strategy.shindong import engine, spec  # noqa: E402


def test_preregistered():
    assert spec.R3_ATR_STOP_K == 0.25
    assert spec.VARIANTS[-1] == "SHADOW_ATRS"
    assert spec.LATE_SHADOW_START["SHADOW_ATRS"] == "2026-10-21"
    assert spec.SPEC_VERSION == "SD-2026-10-21-v3"            # MAIN 값 무변경 → 버전 유지
    assert spec.MAIN_TRAIL == (4.0, 4.0)


def _day(atr14):
    """09:31 맥점 1100 아래 꼬리 → 09:32 매수 진입(1101) → 1099 까지 되밀림 → 1109 까지 상승.

    현행 R3 손절 = min(1100 − 1.5, 터치 저점 1099.5 − 0.5) = 1098.5 → 09:33 저점 1098.0 에 손절.
    ATRS(k=0.25 × ATR 20 = 5pt): 손절 1096.0 → 버틴다.
    """
    bars = {"09:00": (1103, 1103, 1103, 1103)}
    flow = {"08:59": (100.0, 400.0), "09:00": (100.0, 400.0)}
    for m in range(1, 30):
        t = "09:%02d" % m
        bars[t] = (1103, 1103.5, 1102.5, 1103)
        flow[t] = (100.0, 400.0)
    bars["09:30"] = (1103, 1103, 1102, 1102)
    flow["09:30"] = (100.0, 400.0)
    bars["09:31"] = (1102, 1102, 1099.5, 1100.6)
    flow["09:31"] = (100.0, 400.0)
    bars["09:32"] = (1100.6, 1101, 1100.4, 1101)
    flow["09:32"] = (100.0, 460.0)
    for t, o, h, l, c in (("09:33", 1101, 1101.2, 1098.0, 1098.4), ("09:34", 1098.4, 1103, 1098.3, 1102.8),
                          ("09:35", 1102.8, 1109, 1102.7, 1108.5)):
        bars[t] = (o, h, l, c)
        flow[t] = (100.0, 460.0)
    row = {"struct_up": json.dumps([[1100.0, ["구조"]]]), "struct_down": "[]",
           "dist_low": 1080.0, "dist_high": 1120.0, "low80_lo": 1070.0, "high80_hi": 1140.0}
    if atr14 is not None:
        row["atr14"] = atr14
    return engine.DayFrame(bars, flow), engine.prepare_levels({"0850": row})


def _r3(res):
    return [t for t in res["trades"] if t["rule"] == "R3"]


def test_r3_stop_widened_and_survives():
    d, L = _day(20.0)
    m = _r3(engine.run_day(d, L, "MAIN"))[0]
    a = _r3(engine.run_day(d, L, "SHADOW_ATRS"))[0]
    assert m["entry_ts"] == a["entry_ts"] == "09:32" and m["entry_px"] == a["entry_px"] == 1101
    assert m["stop_init"] == pytest.approx(1098.5)
    assert a["stop_init"] == pytest.approx(1101 - 0.25 * 20.0)       # 1096.0
    assert {g["reason"] for g in m["legs"]} == {"SL"}                   # 현행은 노이즈에 손절
    assert all(g["reason"] != "SL" for g in a["legs"] if not g["open"])  # ATRS 는 버틴다


def test_never_tighter_than_current():
    d, L = _day(4.0)                                                    # 0.25×4 = 1pt → 1100 — 현행 1098.5 보다 좁다
    m = _r3(engine.run_day(d, L, "MAIN"))[0]
    a = _r3(engine.run_day(d, L, "SHADOW_ATRS"))[0]
    assert a["stop_init"] == m["stop_init"] == pytest.approx(1098.5)


def test_fallback_without_atr_is_recorded():
    d, L = _day(None)
    res = engine.run_day(d, L, "SHADOW_ATRS")
    assert _r3(res)[0]["stop_init"] == pytest.approx(1098.5)
    assert "ATR14 없음 — R3 손절 폴백(현행 맥점 손절)" in res["decision"]["notes"]
    assert "ATR14 없음" not in " ".join(engine.run_day(d, L, "MAIN")["decision"]["notes"])   # MAIN 무관


def test_r2_and_trail_same_as_main():
    src = open(os.path.join(ROOT, "strategy", "shindong", "engine.py"), encoding="utf-8").read()
    assert 'elif variant in ("MAIN", "SHADOW_ATRS"):' in src             # 같은 트레일
    a = src.index("# [700차] SHADOW_ATRS — R3 초기 손절")
    assert src.index("# R3\n") < a < src.index('tr.update(rule="R3"')   # R3 경로 안에서만 손절을 바꾼다


def test_report_label():
    from strategy.shindong import daily_report
    assert daily_report.VLABEL["SHADOW_ATRS"].startswith("ATRS")
