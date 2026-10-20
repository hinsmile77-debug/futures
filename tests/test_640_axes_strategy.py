# -*- coding: utf-8 -*-
"""[MW0602 640차 ③] 4축 귀속(합 불변식) · 레슨 축 · AI 전략 레지스트리 S-n · 전략 집계 · 갈린 섀도 상세."""
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


def _ai(entry_t, side, fill, exit_t, exit_px, why, pnl):
    return dict(entry_t=entry_t, side=side, fill=fill, exit_t=exit_t, exit_px=exit_px, why=why, pnl=pnl, open=False)


def _mn(entry_t, side, entry_px, exit_px, net_pt, reason="1차/최종"):
    return dict(entry_t=entry_t, side_ko=side, entry_px=entry_px, exit_px=exit_px, net_pt=net_pt, reason_ko=reason)


def test_1_axes_paired_sum_invariant():
    ai = [_ai("09:30", "매도", 874.8, "09:44", 864.0, "목표 청산", 10.8), _ai("10:30", "매도", 865.0, "11:17", 872.0, "손절", -7.0)]
    mn = [_mn("09:07", "매도", 871.68, 859.68, 11.81), _mn("10:00", "매도", 862.06, 850.25, 11.81)]
    a = LN.attribute_axes(ai, mn, ai_total=3.4, main_total=23.62)
    assert a["mode"] == "짝지음" and a["exit_kind"] == "목표 청산"
    assert a["by"]["진입"] == pytest.approx((871.68 - 874.8) * -1, abs=0.01)     # 매도: AI 가 더 높게 팔았으면 +
    assert a["by"]["청산"] == pytest.approx((864.0 - 859.68) * -1, abs=0.01)     # 매도: AI 가 더 높게 샀으면(덜 내려가 팔았으면) −
    assert a["by"]["횟수"] == pytest.approx(-7.0 - 11.81, abs=0.01)
    assert round(sum(a["by"].values()), 2) == a["diff"] == pytest.approx(3.4 - 23.62, abs=0.01)


def test_2_axes_direction_mismatch_and_participation():
    ai = [_ai("09:30", "매수", 880.5, "09:44", 871.5, "손절", -9.0)]
    mn = [_mn("09:07", "매도", 871.68, 859.68, 11.81)]
    a = LN.attribute_axes(ai, mn, ai_total=-9.2, main_total=11.81)
    assert a["mode"] == "방향차" and a["by"]["방향"] == pytest.approx(-21.01) and a["by"]["진입"] is None
    b = LN.attribute_axes([], mn, ai_total=0.0, main_total=11.81)
    assert b["mode"] == "참여차" and b["by"]["횟수"] == pytest.approx(-11.81) and b["by"]["방향"] == 0.0
    c = LN.attribute_axes(ai, mn, ai_total=None, main_total=11.81)
    assert c["diff"] is None and all(v is None for v in c["by"].values())


def test_3_lesson_axis_add_set_and_render(tmp_path, monkeypatch):
    monkeypatch.setattr(LN, "LEARN_DIR", str(tmp_path))
    l = LN.lesson_add("L90", "t", "r", axis="진입")
    assert l["axis"] == "진입"
    with pytest.raises(SystemExit):
        LN.lesson_add("L91", "t", "r", axis="엉뚱")
    l2 = LN.lesson_set("L90", axis="손절", why="재분류")
    assert l2["axis"] == "손절" and any("축=손절" in h["why"] for h in l2["history"])
    md = open(os.path.join(str(tmp_path), LN.REGISTRY_MD), encoding="utf-8").read()
    assert "| 축 |" in md and "| L90 | 후보 | 손절 |" in md
    assert "[후보·손절]" in LN.lessons_text()


def test_4_strategy_requires_five_axes_and_tallies(tmp_path, monkeypatch):
    monkeypatch.setattr(LN, "LEARN_DIR", str(tmp_path))
    LN.lesson_add("L12", "오프셋", "맥점 안쪽 0.4", axis="진입")
    with pytest.raises(SystemExit):
        LN.strategy_add("S1", "반쪽", {"방향": "현물 외인 부호", "진입": "되돌림"})
    with pytest.raises(SystemExit):
        LN.strategy_add("S1", "t", {a: "x" for a in LN.STRAT_AXES}, lessons=["L99"])          # 없는 레슨
    s = LN.strategy_add("S1", "현물외인 되돌림 숏", {"방향": "현물 외인 누적 부호", "진입": "저항 맥점 −0.4", "손절": "개장폭 1/3",
                                                   "청산": "자석 2회 거부 시 절반", "확률": "AM 외인 선물 0 위면 하락 ≤30%"}, lessons=["L12"])
    assert s["status"] == "후보" and s["lessons"] == ["L12"] and s["beat_main"] == []
    LN.strategy_tally("S1", "2026-10-21", applied=True, hit=True, beat_main=False)
    LN.strategy_tally("S1", "2026-10-22", applied=True, hit=False, beat_main=True)
    LN.strategy_tally("S1", "2026-10-23", applied=True, hit=True, beat_main=True)
    s = LN._sfind(LN.load_strategies(), "S1")
    assert len(s["applied"]) == 3 and s["hit"] == ["2026-10-21", "2026-10-23"] and s["beat_main"] == ["2026-10-22", "2026-10-23"]
    assert "승격 검토" in LN.strategy_suggestion(s)
    s2 = LN.strategy_set("S1", status="적용중", rules={"청산": "자석 2회 거부 시 절반 + 본전 이동"}, why="3회 적중 2")
    assert s2["status"] == "적용중" and "본전 이동" in s2["rules"]["청산"]
    md = open(os.path.join(str(tmp_path), LN.STRAT_MD), encoding="utf-8").read()
    assert "| S1 | 적용중 |" in md and "3/2/1/2" in md
    assert "S1 [적용중]" in LN.strategies_text(active_only=True)


def test_5_record_strategy_and_evaluate_collects_it(tmp_path, monkeypatch):
    monkeypatch.setattr(SL, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(SL, "DOC_DIR", str(tmp_path / "doc"))
    monkeypatch.setattr(LN, "LEARN_DIR", str(tmp_path / "learn"))
    monkeypatch.setattr(RV, "SD_DB", str(tmp_path / "none.db"))
    day = "2026-10-21"
    SL.record(day, "premarket", "plan", "매도", 880.0, 888.0, 870.0, "x", strategy="S1", vs_main="disagree", vs_why="y")
    SL.record(day, "premarket", "plan", "매도", 880.0, 888.0, 870.0, "섀도", variant="legacy", strategy="S1")   # legacy 는 전략 표기 안 함
    log = SL.load_ai_log(day)
    assert log[0]["strategy"] == "S1" and "strategy" not in log[1]
    assert LN.strategies_applied(log) == ["S1"]
    bars = [("%02d:%02d" % (9 + i // 60, i % 60), 885.0, 886.0, 884.0, 885.0) for i in range(0, 120)]
    out = LN.evaluate_day(day, bars=bars, log=log, save=False)
    assert out["strategies_applied"] == ["S1"] and out["rival"]["present"] is False and out["rival"]["axes"] is None if "axes" in out["rival"] else True
    doc = open(SL._doc_path(day), encoding="utf-8").read()
    assert "전략 S1" in doc


def test_6_rival_block_divergent_carries_trades(tmp_path):
    db = str(tmp_path / "sd.db")
    from tests.test_640_rival_scoreboard import _mk_db
    _mk_db(db)
    rv = RV.read_day("2026-10-20", db=db, last_close=850.0)
    live_ai = dict(pnl=-9.0, trades=[dict(entry_t="09:30", side="매수", fill=880.5, exit_t="09:44", exit_px=871.5, why="손절", pnl=-9.0, open=False)])
    b = LN.rival_block("2026-10-20", rv, live_ai, [dict(ts="2026-10-20T08:52:00", variant="live", action="plan", dir="매수")])
    assert b["axes"]["mode"] == "방향차" and b["axes"]["by"]["방향"] == pytest.approx(-9.2 - 10.0)
    d = {x["short"]: x for x in b["divergent"]}
    assert d["BRKC"]["trades"][0]["side"] == "매수" and d["BRKC"]["trades"][0]["reason"] == "손절"
    assert b["main_trades"][0]["rule"] == "FLOW" and b["main_trades"][0]["net_pt"] == 10.0
    txt = LN._render_rival_eval(b)
    assert "4축 귀속" in txt and "갈린 섀도 BRKC" in txt and "MAIN 거래" in txt
