# -*- coding: utf-8 -*-
"""[MW0601 714차] 신동 섀도 SHADOW_R2D7 — v3 MAIN + R2 확정 창만 기준 09:06 · 확정 09:07–09:16.

고정하는 것
  A. 사전등록: 창 값 · 채점 시작 2026-10-26 · VARIANTS 끝 · MAIN 값·SPEC_VERSION 무변경.
  B. 엔진: R2 만 늦게 확정 · 기준은 09:06 콜/풋 · OR 손절은 기준 분–확정 분 고점 + 1 · 창 밖 변화는 무시.
     창 값을 MAIN 과 같게 두면 MAIN 과 한 원도 다르지 않다(바뀌는 것은 창뿐).
  C. 리포트 라벨 · 귀인 문구.
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
    assert (spec.R2D7_CONF_BASE, spec.R2D7_CONF_START, spec.R2D7_CONF_END) == ("09:06", "09:07", "09:16")
    assert "SHADOW_R2D7" in spec.VARIANTS                                # [719차] 뒤에 SHADOW_F2 가 붙었다
    assert spec.LATE_SHADOW_START["SHADOW_R2D7"] == "2026-10-27"         # [718차] v4 재시작(714차 등록 10-26)
    assert spec.SPEC_VERSION == "SD-2026-10-27-v4"                       # [718차] v4 — R2D7 정의(v3 MAIN 그대로 + R2 창)는 무변경
    assert (spec.PREMARKET_LAST, spec.CONF_BASE, spec.CONF_START, spec.CONF_END) == \
        ("08:59", "09:00", "09:01", "09:10")                              # MAIN 창은 그대로


def _day(late_jump="09:08"):
    """장전 콜−풋 +400 → 하방. 09:01 콜 +60(풋 그대로) → MAIN 09:01 확정.
    그 뒤 09:06 까지 흐름 정지 → late_jump 분에 콜 +60 → R2D7 확정."""
    bars, flow = {}, {"08:59": (500.0, 100.0)}
    call = 500.0
    for m in range(0, 31):
        t = "09:%02d" % m
        if t == "09:01" or t == late_jump:
            call += 60.0
        flow[t] = (call, 100.0)
        px = 1110.0 - 0.1 * m
        bars[t] = (px, px + (2.0 if t == "09:07" else 0.5), px - 0.5, px)
    row = {"struct_up": json.dumps([[1130.0, ["구조"]]]), "struct_down": json.dumps([[1090.0, ["구조"]]]),
           "dist_low": 1080.0, "dist_high": 1140.0, "low80_lo": 1070.0, "high80_hi": 1150.0}
    return engine.DayFrame(bars, flow), engine.prepare_levels({"0850": row})


def _r2(res):
    return [t for t in res["trades"] if t["rule"] == "R2"]


def test_main_confirms_0901_r2d7_confirms_late():
    d, L = _day()
    m = engine.run_day(d, L, "MAIN")
    x = engine.run_day(d, L, "SHADOW_R2D7")
    assert m["decision"]["bias"] == x["decision"]["bias"] == -1          # R1 은 같다(08:59)
    assert m["decision"]["r2_ts"] == "09:01" and x["decision"]["r2_ts"] == "09:08"
    t = _r2(x)[0]
    assert t["side"] == -1 and t["entry_px"] == pytest.approx(d.c["09:08"])
    hi = max(d.h[k] for k in d.between("09:06", "09:08"))                 # 09:07 고점 포함
    assert t["stop_init"] == pytest.approx(hi + spec.OR_STOP_BUF)


def test_change_outside_window_is_ignored():
    d, L = _day(late_jump="09:17")                                        # 창(09:07–09:16) 밖
    x = engine.run_day(d, L, "SHADOW_R2D7")
    assert x["decision"]["r2"] == "NONE" and _r2(x) == []
    d2, L2 = _day(late_jump="09:05")                                      # 기준(09:06) 전 변화 — 기준에 흡수
    assert engine.run_day(d2, L2, "SHADOW_R2D7")["decision"]["r2"] == "NONE"


def test_same_window_equals_main(monkeypatch):
    d, L = _day()
    monkeypatch.setattr(spec, "R2D7_CONF_BASE", spec.CONF_BASE)
    monkeypatch.setattr(spec, "R2D7_CONF_START", spec.CONF_START)
    monkeypatch.setattr(spec, "R2D7_CONF_END", spec.CONF_END)
    m = engine.run_day(d, L, "MAIN")
    x = engine.run_day(d, L, "SHADOW_R2D7")
    assert m["decision"] == x["decision"]
    assert [engine.trade_net(t) for t in m["trades"]] == [engine.trade_net(t) for t in x["trades"]]


def test_report_label_and_attribution():
    from strategy.shindong import daily_report
    assert daily_report.VLABEL["SHADOW_R2D7"].startswith("R2D7")
    src = open(os.path.join(ROOT, "strategy", "shindong", "daily_report.py"), encoding="utf-8").read()
    assert "R2 확정 창 이동(09:07–09:16)" in src
