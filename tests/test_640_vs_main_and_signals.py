# -*- coding: utf-8 -*-
"""[MW0602 640차 ②] 상대의 수 블록 — 신호원 값(DayFrame) · `--vs-main` 기록(미기재 → 기권 + 플래그) · 신호등 HTML."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import shindong2_live as SL  # noqa: E402
import shindong2_learn as LN  # noqa: E402
import shindong2_rival as RV  # noqa: E402
from strategy.shindong import engine, spec  # noqa: E402

family_only = pytest.mark.skipif(RV.RULESET != "family", reason="v3 family 규격 전용(FLOWC·FLOWR60·FX) — v1 은 test_7")


def _minutes(a, b):
    out, h, m = [], int(a[:2]), int(a[3:])
    while "%02d:%02d" % (h, m) <= b:
        out.append("%02d:%02d" % (h, m))
        m += 1
        if m == 60:
            h, m = h + 1, 0
    return out


def _frame(cp_by_min, fx_by_min=None, px=1000.0):
    mins = _minutes("08:55", "11:05")
    candles = {k: (px, px + 1, px - 1, px) for k in mins if k >= "09:00"}
    flow = {k: (cp_by_min(k), 0.0) for k in mins}          # call=콜−풋, put=0
    return engine.DayFrame(candles, flow, fx=fx_by_min)


@family_only
def test_1_flowc_and_flowr60_signals_follow_spec_sign_convention():
    # 09:00 기준 0 → 10:00 에 +400(콜 우위 ↑ → 역추종 매도) → 11:00 에 +400 유지(60분 변화 0)
    cp = lambda k: 0.0 if k < "10:00" else 400.0
    d = _frame(cp)
    s10 = RV.signal_from_frame(d, "10:00")
    assert s10["present"] and s10["flowc"]["dv"] == 400.0 and s10["flowc"]["side"] == "매도" and s10["flowc"]["k"] == spec.FLOWC_K
    assert s10["flowr60"]["dv"] == 400.0 and s10["flowr60"]["side"] == "매도"      # 09:00→10:00 변화
    s11 = RV.signal_from_frame(d, "11:00")
    assert s11["flowr60"]["dv"] == 0.0 and s11["flowr60"]["side"] is None and s11["flowr60"]["dist"] == spec.FLOWR_K
    s09 = RV.signal_from_frame(d, "09:30")
    assert s09["flowr60"] is None and s09["flowc"]["side"] is None and s09["flowc"]["dist"] == spec.FLOWC_K   # 10:00 전엔 60분 창 없음


@family_only
def test_2_signal_no_future_reference_and_fx_axis():
    cp = lambda k: 0.0 if k < "10:30" else -900.0            # 10:30 에 급락(매수 신호) — 10:00 시점에선 보이면 안 된다
    fx = {k: (0.0 if k < "10:00" else 500.0) for k in _minutes("09:00", "11:05")}
    d = _frame(cp, fx)
    s = RV.signal_from_frame(d, "10:00")
    assert s["flowc"]["dv"] == 0.0 and s["flowc"]["side"] is None
    assert s["fx60"]["dv"] == 500.0 and s["fx60"]["side"] == "매수"            # 순추종, K=LEAD_K_FX(400)
    s2 = RV.signal_from_frame(d, "10:35")
    assert s2["flowc"]["side"] == "매수"
    assert RV.signal_lines(s2)[0].startswith("상대의 눈") and any("매수" in l for l in RV.signal_lines(s2))


@family_only
def test_3_r1_bias_from_premarket_flow():
    cp = lambda k: 120.0                                   # 08:59 콜−풋 +120 ≥ BIAS_MIN → 하방 편향(매도)
    s = RV.signal_from_frame(_frame(cp), "09:10")
    assert s["r1"]["pm_sp"] == 120.0 and s["r1"]["bias"] == -1 and s["r1"]["side"] == "매도"


def test_4_parse_vs_main_line():
    assert SL.parse_vs_main_line("결론\n상대판단: 반대 | 현물 외인이 더 강하다\n") == ("disagree", "현물 외인이 더 강하다")
    assert SL.parse_vs_main_line("상대판단: 동의") == ("agree", None)
    assert SL.parse_vs_main_line("상대판단: abstain | 상대 없음") == ("abstain", "상대 없음")
    assert SL.parse_vs_main_line("아무 줄") == (None, None)


def test_5_record_stores_vs_main_or_flags_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(SL, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(SL, "DOC_DIR", str(tmp_path / "doc"))
    day = "2026-10-21"
    r1 = SL.record(day, "premarket", "plan", "매수", 880.5, 871.5, 892.5, "장전 계획", scenarios=None)
    assert r1["vs_main"] == "abstain" and r1.get("vs_main_missing") is True
    r2 = SL.record(day, "intraday", "plan", "매도", 874.8, 881.0, 862.0, "결론\n상대판단: 반대 | FLOWC 는 매도인데 현물 외인 매수 전환")
    assert r2["vs_main"] == "disagree" and r2["vs_why"] == "FLOWC 는 매도인데 현물 외인 매수 전환" and "vs_main_missing" not in r2
    r3 = SL.record(day, "intraday", "note", "관망", None, None, None, "유지", vs_main="agree", vs_why="같은 방향")
    assert r3["vs_main"] == "agree" and r3["vs_why"] == "같은 방향"
    r4 = SL.record(day, "overnight", "plan", "매도", 880.0, 888.0, 870.0, "익일 계획")        # 상대가 아직 없다 — 요구하지 않는다
    assert "vs_main" not in r4
    r5 = SL.record(day, "premarket", "plan", "매도", 880.0, 888.0, 870.0, "섀도", variant="legacy")
    assert "vs_main" not in r5
    with pytest.raises(SystemExit):
        SL.record(day, "intraday", "note", "관망", None, None, None, "x", vs_main="maybe")
    doc = open(SL._doc_path(day), encoding="utf-8").read()
    assert "상대 판단 **기권**(미기재 → 기권)" in doc and "상대 판단 **반대** — FLOWC" in doc
    # 평가 — 명시 기록이 미기재 기권보다 우선한다
    log = SL.load_ai_log(day)
    assert LN.vs_main_recorded(log) == ("agree", "recorded", "같은 방향")
    only_missing = [r for r in log if r.get("vs_main_missing")]
    assert LN.vs_main_recorded(only_missing) == ("abstain", "missing", None)


def test_6_ladder_html_has_signal_light():
    p = os.path.join(ROOT, "tools", "maekjeom_ladder", "ladder.html")
    h = open(p, encoding="utf-8").read()
    assert "vslight" in h and "vs-dis" in h and "vs_main_missing" in h and "기계 — 판단 미기록" in h


def test_7_v1_ruleset_signals_for_mw0601_port(monkeypatch):
    """[640차 이식] v9-dev(MW0601) 규격 = R1/R2/R3. 같은 파일이 RULESET 자동 감지로 그 경로를 탄다 — dev 에서도 엔진 v1 함수로 시험된다."""
    from strategy.shindong import engine as E
    monkeypatch.setattr(RV, "RULESET", "v1")
    mins = _minutes("08:55", "10:05")
    candles = {k: (1000.0, 1001.0, 999.0, 1000.0) for k in mins if k >= "09:00"}
    # 08:59 콜−풋 +120(콜 우위 → 하방 편향) · 09:03 에 콜 +80 · 풋 −10 (콜−풋 +90 ≥ CONF_MIN) → R2 확정(매도)
    flow = {k: ((120.0, 0.0) if k < "09:03" else (200.0, -10.0)) for k in mins}
    d = E.DayFrame(candles, flow)
    s = RV.signal_from_frame(d, "09:20", L=None)
    assert s["ruleset"] == "v1" and s["r1"]["side"] == "매도" and s["r1"]["pm_sp"] == 120.0
    assert s["r2"]["status"] == "맥점 없음" and s["r3"]["above"] is None and s["r3"]["active"] is False
    lines = RV.signal_lines(dict(s, product="wk_thu"))
    assert lines[0].endswith("규격 R1/R2/R3):") and any("R1 08:59" in l and "매도" in l for l in lines)
    assert RV.LABEL["MAIN"].startswith("MAIN(")
