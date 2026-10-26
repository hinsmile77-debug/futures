# -*- coding: utf-8 -*-
"""[MW0601 699차] 신동 규격 v3 — MAIN = v2 + R3 트레일 4/4(구 SHADOW_TR44 승격) · SHADOW_V2 = 구 MAIN.

고정하는 것
  A. 규격: 버전·변형 목록·트레일 값·채점 재시작·보완 판정 사전등록 상수.
  B. 엔진: MAIN ≡ 종료된 이름 SHADOW_TR44 · SHADOW_V2 ≡ 트레일 없는 경로 · R2 는 트레일 없음.
  C. 실집행: 트레일로 움직인 재생 `stop_now` 를 `live_legs.sync` 가 한 방향으로 따라 조인다 ·
     1차 뒤 본전 이동이 이미 트레일로 올라간 손절을 되돌리지 않는다.
  D. 동결: 조건부 러너 섀도는 SHADOW_V2 로 고정(RUNNER_VERSION 별도 사전등록) · 신동2 상대 사전등록 재등록.
  E. 보완 판정(`scripts/shindong_complement_mw0602.py`)의 순수 판정 함수.
"""
import datetime
import importlib.util
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest  # noqa: E402

from strategy.shindong import engine, live_legs as LL, spec  # noqa: E402


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


# ── A. 규격 ─────────────────────────────────────────────────────────────
def test_spec_v3_registered():
    # [718차] v4 개정 뒤 — v3 는 사료(V3_SPEC_VERSION · V3_SCORING_START). 트레일 값·TR44 종료는 그대로
    assert spec.V3_SPEC_VERSION == spec.SPEC_VERSION_PREV == "SD-2026-10-21-v3"
    assert spec.V2_SPEC_VERSION == "SD-2026-09-29-v2"
    assert spec.VARIANTS[:6] == ("MAIN", "SHADOW_V3", "SHADOW_V2", "SHADOW_E2F2", "SHADOW_X4NF", "SHADOW_X4NFA")
    assert spec.MAIN_TRAIL == (spec.TR44_ACT, spec.TR44_DIST) == (4.0, 4.0)     # 632차 사전등록값 그대로
    assert "SHADOW_TR44" in spec.RETIRED_SHADOWS and "SHADOW_TR44" not in spec.VARIANTS
    assert spec.V3_SCORING_START == "2026-10-21" and spec.V2_SCORING_START == "2026-09-30"
    assert {"SHADOW_V3", "SHADOW_V2", "SHADOW_X4NF", "SHADOW_X4NFA"} <= set(spec.LATE_SHADOW_START)
    # [718차] v4 — 전 섀도가 v4 첫날(10-27)부터 다시 센다(v3 창: 10-21 · R2D7 10-26)
    assert all(v == spec.SCORING_START == "2026-10-27" for v in spec.LATE_SHADOW_START.values())
    assert (spec.COMPLEMENT_SCORING_START, spec.COMPLEMENT_JUDGE_AFTER_DAYS) == ("2026-10-27", 20)


def test_amendment_documented():
    doc = os.path.join(ROOT, "docs", "신동거래", "신동_개정_v3_TR44승격_MW0601-20261020.md")
    assert os.path.exists(doc)
    pre = _src("docs/신동거래/신동_사전등록_20260924.md")
    assert "SD-2026-10-21-v3" in pre                       # §6-1 개정 이력에 올라갔다


# ── B. 엔진 ─────────────────────────────────────────────────────────────
def _levels(struct, dist_low=1080.0, dist_high=1120.0):
    import json
    up = [[x, ["구조"]] for x in struct]
    return engine.prepare_levels({"0850": {"struct_up": json.dumps(up), "struct_down": "[]",
                                           "dist_low": dist_low, "dist_high": dist_high,
                                           "low80_lo": 1070.0, "high80_hi": 1140.0}})


def _day_r3_long_runs_then_reverses():
    """09:31 맥점 1100 아래 꼬리 → 콜−풋 반전으로 매수 진입 → +6pt 달린 뒤 되밀림.

    v2(트레일 없음): 1차(1119.5) 못 닿고 원 손절로 진다. v3: +4pt 뒤 손절이 올라가 이익으로 끝난다.
    """
    bars = {"09:00": (1103, 1103, 1103, 1103)}
    flow = {"08:59": (100.0, 400.0), "09:00": (100.0, 400.0)}      # 콜−풋 −300 → 상방 편향(R2 는 미확정)
    for i, m in enumerate(range(1, 30)):
        t = "09:%02d" % m
        bars[t] = (1103, 1103.5, 1102.5, 1103)
        flow[t] = (100.0, 400.0)
    bars["09:30"] = (1103, 1103, 1102, 1102)
    flow["09:30"] = (100.0, 400.0)
    bars["09:31"] = (1102, 1102, 1099.5, 1100.6)       # 맥점 1100 터치(아래 꼬리) · 위에서 마감 → 매수 후보
    flow["09:31"] = (100.0, 400.0)
    bars["09:32"] = (1100.6, 1101, 1100.4, 1101)       # 콜−풋 −300 → −360(최고점 대비 60 하락) → 매수 진입
    flow["09:32"] = (100.0, 460.0)
    seq = [("09:33", 1101, 1104, 1100.9, 1103.5), ("09:34", 1103.5, 1107, 1103.4, 1106.5),
           ("09:35", 1106.5, 1106.6, 1103.0, 1103.2), ("09:36", 1103.2, 1103.3, 1097.0, 1097.5)]
    for t, o, h, l, c in seq:
        bars[t] = (o, h, l, c)
        flow[t] = (100.0, 460.0)
    return engine.DayFrame(bars, flow), _levels([1100.0])


def test_main_trails_r3_and_v2_does_not():
    d, L = _day_r3_long_runs_then_reverses()
    main = [t for t in engine.run_day(d, L, "MAIN")["trades"] if t["rule"] == "R3"]
    v2 = [t for t in engine.run_day(d, L, "SHADOW_V2")["trades"] if t["rule"] == "R3"]
    assert main and v2 and main[0]["entry_ts"] == v2[0]["entry_ts"] == "09:32"
    assert {g["reason"] for g in main[0]["legs"]} == {"TR"}          # +4 뒤 트레일 손절(극값 1107 − 4 = 1103)
    assert all(g["px"] == pytest.approx(1103.0) for g in main[0]["legs"])
    assert {g["reason"] for g in v2[0]["legs"]} == {"SL"}            # v2 는 원 손절
    assert engine.trade_net(main[0]) > 0 > engine.trade_net(v2[0])


def test_main_equals_retired_tr44_name_and_v2_equals_untrailed_path():
    d, L = _day_r3_long_runs_then_reverses()
    sig = lambda r: [(t["rule"], t["entry_ts"], round(engine.trade_net(t))) for t in r["trades"]]
    assert sig(engine.run_day(d, L, "MAIN")) == sig(engine.run_day(d, L, "SHADOW_TR44"))
    # SHADOW_V2 = 트레일 없음 — run_trade(trail=None) 경로와 같다
    v2 = engine.run_day(d, L, "SHADOW_V2")["trades"][0]
    again = engine.run_trade(d, v2["side"], v2["entry_ts"], v2["stop_init"], v2["t1"], v2["t2"])
    assert [g["net"] for g in again["legs"]] == [g["net"] for g in v2["legs"]]


def test_r2_has_no_trail_in_v3():
    """트레일은 R3 에만 — R2 는 v2 와 같다(엔진 R2 경로는 trail 인자를 넘기지 않는다)."""
    src = _src("strategy/shindong/engine.py")
    assert "tr = run_trade(d, bias, conf, ex, t1, t2, e2=e2)\n" in src
    assert "tr = run_trade(d, side, ent, stop, t1, t2, e2=e2, trail=tr44)" in src


# ── C. 실집행 ───────────────────────────────────────────────────────────
def _tr(stop_now, **kw):
    d = {"trade_key": "R3|09:32|+1", "rule": "R3", "side": 1, "entry_px": 1101.0,
         "stop_init": 1098.0, "stop_now": stop_now, "t1": 1119.5, "t2": 1139.5, "status": "OPEN",
         "source": "live", "leg1_reason": None, "leg2_reason": None}
    d.update(kw)
    return d


def test_sync_follows_trailed_stop_one_way():
    rec = LL.make_rec(_tr(1098.0))
    now = datetime.datetime(2026, 10, 21, 9, 36)
    assert LL.sync(rec, _tr(1098.0), now) == []
    acts = LL.sync(rec, _tr(1103.0), now)                 # 트레일로 올라간 재생 손절
    assert acts == [("set_stop", 1103.0)]
    rec["stop"] = 1103.0
    assert LL.sync(rec, _tr(1101.5), now) == []            # 불리한 쪽으로는 따라가지 않는다
    closed = _tr(1103.0, status="CLOSED", leg1_reason="TR", leg2_reason="TR")
    assert LL.sync(rec, closed, now) == [("exit_all", "신동미러:TR")]


def test_after_leg1_keeps_trailed_stop():
    rec = LL.make_rec(_tr(1098.0))
    rec["stop"] = 1104.0                                   # 1차 전에 이미 트레일로 본전(1101) 위
    assert LL.after_leg1(rec) is None and rec["stop"] == 1104.0


# ── D. 동결 · 재등록 ─────────────────────────────────────────────────────
def test_mireuk_runner_frozen_to_v2_main():
    src = _src("strategy/shindong/mireuk_runner.py")
    assert 'E.run_day(d, L, "SHADOW_V2")' in src and 'E.run_day(d, L, "MAIN")' not in src


def test_shindong2_rival_reregistered_before_open():
    src = _src("scripts/shindong2_rival.py")
    # [718차] v4 로 MAIN 이 바뀌어 v3 재등록(SD2AI-MW0601-2026-10-27-v3) — v2 는 이력으로 남는다(test_718 이 현행을 고정)
    assert '"MW0601": dict(version="SD2AI-MW0601-2026-10-27-v3", scoring_start="2026-10-27")' in src
    doc = _src("docs/맥점x옵션사다리개선/02_사전등록_AI대MAIN_판정_MW0601-20261020.md")
    assert "SD2AI-MW0601-2026-10-21-v2" in doc and "SD-2026-10-21-v3" in doc


def test_report_labels_cover_variants():
    from strategy.shindong import daily_report
    assert all(v in daily_report.VLABEL for v in spec.VARIANTS)


# ── E. 보완 판정 ─────────────────────────────────────────────────────────
def _cm():
    sp = importlib.util.spec_from_file_location(
        "shindong_complement_mw0602", os.path.join(ROOT, "scripts", "shindong_complement_mw0602.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def test_judge_waits_until_registered_days():
    cm = _cm()
    j = cm.judge([1.0, -2.0, 3.0], [2.0, 1.0, -1.0])
    assert j["verdict"] == "대기" and j["n"] == 3


def test_judge_valid_partial_invalid():
    cm = _cm()
    h = [100.0, -150.0, 120.0, 90.0]
    hedge = [20.0, 80.0, 10.0, 30.0]                       # H 손실일에 이익 → 최악일·효율 둘 다 개선
    j = cm.judge(h, hedge, min_days=4)
    assert j["verdict"] == "보완 유효" and j["c_worst"] and j["c_ratio"]
    same_bad = [100.0, -300.0, 120.0, 90.0]                # 같은 날 더 크게 진다
    assert cm.judge(h, same_bad, min_days=4)["verdict"] == "보완 무효"
    low = [0.0, -100.0, 0.0, 0.0]                          # 최악일은 개선(−125 > −150) · 효율은 악화
    jl = cm.judge(h, low, min_days=4)
    assert jl["c_worst"] and not jl["c_ratio"] and jl["verdict"] == "부분"


def test_judge_unmeasured_when_flat():
    cm = _cm()
    assert cm.judge([5.0, 5.0], [5.0, 5.0], min_days=2)["verdict"] == "미측정"   # 표준편차 0 ≠ 효율 0


def test_complement_script_guards_intraday_and_never_writes_db():
    src = _src("scripts/shindong_complement_mw0602.py")
    assert 'guard_intraday("shindong_complement_mw0602")' in src
    assert "mode=ro" in src and "INSERT" not in src and "UPDATE " not in src
    assert '"worktree", "remove", "--force"' in src                         # 임시 워크트리는 항상 지운다
