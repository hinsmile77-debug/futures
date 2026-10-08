# -*- coding: utf-8 -*-
"""[MW0601 672차] 신동2 학습 사이클 — 단일 계획 평가 · 변형(live/legacy) · 레슨 레지스트리 · 워크포워드 판정 · 스킬 문구.

고정하는 것
-----------
A. simulate_plan — simulate_ai 와 같은 규약(효력 다음 분, 지정가 고저 포함 체결, 같은 봉 손절 우선, 15:10 강제청산), MFE/MAE.
B. 방향 판정 — 종가−시가 ±2pt 보합, 관망은 분모 제외(None), 보합일엔 매수·매도 모두 실패.
C. legacy 섀도 — simulate_ai 가 무시한다(실제 재량 채점 오염 금지), ai_latest 를 덮지 않는다, 장중 phase 에는 못 쓴다.
D. evaluate_day — 변형별 마지막 계획만, 09:00 이후 premarket 기록은 장전계획이 아니다, lessons_applied 는 live 기록에서만.
E. 레슨 레지스트리 — 같은 id 재신설 금지, 적용/적중/실패는 날짜 집합(같은 날 두 번 세지 않는다), 승격 제안 문구.
F. 추이 판정 — 짝지어진 계획 3건 미만이면 「미측정」(딥다이브 아님), 개선−기존 ≤ 0 이면 딥다이브, 방향 적중 <50% 도 딥다이브.
G. 스킬 — 사이클 5단어(예측·실행·평가·레슨·개선)와 하위명령 5개, legacy 변형, --lessons 표기가 적혀 있다.

실행: conda run -n py37_32 python -m pytest tests/test_672_shindong2_learning.py -v
"""
import datetime as dt
import io
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import shindong2_live as M  # noqa: E402
import shindong2_learn as LN  # noqa: E402


def _bars(prices, start="09:00"):
    h, m = map(int, start.split(":"))
    out = []
    for i, (o, hi, lo, c) in enumerate(prices):
        t = h * 60 + m + i
        out.append(["%02d:%02d" % (t // 60, t % 60), o, hi, lo, c])
    return out


def _rec(ts, day="2026-10-07", **kw):
    r = dict(id=ts, ts="%sT%s" % (day, ts), phase="premarket", action="plan", variant="live")
    r.update(kw)
    return r


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    live, doc, learn = tmp_path / "live", tmp_path / "doc", tmp_path / "learn"
    monkeypatch.setattr(M, "LIVE_DIR", str(live))
    monkeypatch.setattr(M, "DOC_DIR", str(doc))
    monkeypatch.setattr(LN, "LEARN_DIR", str(learn))
    return tmp_path


# ── A. simulate_plan ───────────────────────────────────────────────────────
def test_plan_limit_fill_target_and_mfe_mae():
    cs = _bars([(100, 101, 99, 100), (100, 103, 100, 102.5), (102, 104, 101, 101.5), (101, 102, 96, 97)])
    s = LN.simulate_plan(cs, dict(dir="매도", entry=103.0, stop=106.0, target=97.0), eff="09:01")
    assert s["filled"] and s["entry_t"] == "09:01" and s["how"] == "지정가" and s["fill"] == 103.0
    assert s["why"] == "목표 청산" and s["pnl"] == 6.0 and s["exit_t"] == "09:03"
    assert s["mfe"] == 7.0 and s["mae"] == 1.0            # 저 96 → 7pt 유리, 고 104 → 1pt 불리


def test_plan_effective_time_blocks_earlier_bars_and_stop_priority():
    cs = _bars([(100, 101, 99, 100), (100, 106, 94, 100)])
    s = LN.simulate_plan(cs, dict(dir="매수", entry=None, stop=95.0, target=105.0), eff="09:01")
    assert s["entry_t"] == "09:01" and s["how"] == "시장가" and s["why"] == "손절" and s["pnl"] == -5.0


def test_plan_unfilled_and_forced_exit_and_stand():
    cs = _bars([(100, 100.5, 99.5, 100)] * 5, start="15:05")
    s = LN.simulate_plan(cs, dict(dir="매도", entry=120.0, stop=125.0, target=90.0))
    assert not s["filled"] and s["pnl"] == 0.0
    cs2 = _bars([(100, 100.5, 99.5, 100)] * 13, start="14:57")      # 14:57–15:09
    s2 = LN.simulate_plan(cs2, dict(dir="매도", entry=None, stop=125.0, target=90.0))
    assert s2["entry_t"] == "14:57" and s2["why"] == "15:10 강제청산" and s2["exit_t"] == "15:09"
    assert LN.simulate_plan(cs, dict(dir="관망", action="stand"))["kind"] == "관망"
    assert LN.simulate_plan(cs, dict(dir="매도", action="stand", entry=100.0, stop=101.0, target=99.0))["kind"] == "관망"


def test_plan_expires_after_1500():
    cs = _bars([(100, 100.5, 99.5, 100)] * 12, start="14:58")   # 14:58–15:09
    s = LN.simulate_plan(cs, dict(dir="매수", entry=None, stop=90.0, target=110.0), eff="15:01")
    assert not s["filled"]


def test_quality_metrics():
    oh = dict(open=100, high=110, low=90, close=92, range=20)
    sim = dict(kind="계획", side="매도", entry=108.0, stop=112.0, target=95.0, filled=True, fill=108.0, pnl=13.0)
    q = LN.plan_quality(sim, oh)
    assert q["capture"] == 0.65 and q["entry_q"] == 0.9 and q["target_margin"] == 5.0 and q["stop_margin"] == 2.0
    assert q["risk"] == 4.0 and q["rr"] == 3.25
    miss = LN.plan_quality(dict(kind="계획", side="매도", entry=115.0, stop=120.0, target=95.0, filled=False, pnl=0.0), oh)
    assert miss["entry_miss"] == 5.0 and "capture" not in miss


# ── B. 방향 ────────────────────────────────────────────────────────────────
def test_direction_and_hit():
    assert LN.actual_direction(100, 103) == "매수" and LN.actual_direction(100, 97) == "매도" and LN.actual_direction(100, 101.5) == "보합"
    assert LN.dir_hit("관망", "매도") is None and LN.dir_hit(None, "매도") is None
    assert LN.dir_hit("매도", "매도") is True and LN.dir_hit("매수", "보합") is False


# ── C. legacy 섀도 ─────────────────────────────────────────────────────────
def test_legacy_ignored_by_simulate_ai_and_latest(sandbox):
    cs = _bars([(100, 101, 99, 100), (100, 102, 100, 101.5), (101, 104, 100, 103)])
    recs = [_rec("08:00:00", phase="overnight", dir="매수", entry=None, stop=95.0, target=110.0, variant="legacy"),
            _rec("08:01:00", phase="overnight", dir="관망", action="stand", variant="live")]
    r = M.simulate_ai("2026-10-07", cs, recs)
    assert r["trades"] == [] and r["pending"] is None        # legacy 만 매수였고 live 는 관망 → 거래 없음
    now = dt.datetime(2026, 10, 6, 16, 0, 0)
    M.record("2026-10-07", "overnight", "plan", "매도", 100.0, 103.0, 95.0, "live", now=now)
    M.record("2026-10-07", "overnight", "plan", "매도", 100.0, 102.0, 97.0, "legacy", now=now + dt.timedelta(seconds=5), variant="legacy")
    latest = json.load(io.open(os.path.join(M.day_dir("2026-10-07"), "ai_latest.json"), encoding="utf-8"))
    assert latest["variant"] == "live" and latest["stop"] == 103.0
    doc = io.open(M._doc_path("2026-10-07"), encoding="utf-8").read()
    assert "기존방식 섀도" in doc
    with pytest.raises(SystemExit):
        M.record("2026-10-07", "intraday", "plan", "매도", 100.0, 102.0, 97.0, "x", now=now, variant="legacy")


# ── D. evaluate_day ────────────────────────────────────────────────────────
def test_evaluate_day_variants_and_lessons(sandbox):
    cs = _bars([(100, 101, 99, 100), (100, 103, 100, 102.5), (102, 104, 101, 101.5), (101, 102, 96, 97), (97, 98, 95, 96)])
    log = [_rec("20:00:00", day="2026-10-06", phase="overnight", dir="매도", entry=103.0, stop=106.0, target=97.0, lessons=["L3"]),
           _rec("20:00:05", day="2026-10-06", phase="overnight", dir="매도", entry=103.0, stop=103.5, target=99.0, variant="legacy", lessons=["L9"]),
           _rec("08:55:00", phase="premarket", dir="매수", entry=None, stop=98.0, target=110.0),
           _rec("09:30:00", phase="premarket", dir="매도", entry=None, stop=110.0, target=90.0),   # 09:00 이후 — 장전계획 아님
           _rec("09:10:00", phase="intraday", action="note", dir="관망")]
    out = LN.evaluate_day("2026-10-07", bars=cs, log=log, st=dict(prev=dict(close=99.0), sd2=dict(summary=dict(base=1.0))))
    assert out["actual_dir"] == "매도" and out["prev_close"] == 99.0
    on = out["overnight"]
    assert on["live"]["dir_hit"] is True and on["live"]["sim"]["pnl"] == 6.0
    assert on["legacy"]["sim"]["why"] == "손절" and on["legacy"]["sim"]["pnl"] == -0.5   # 09:02 고 104 ≥ 103.5
    assert out["premarket"]["live"]["dir"] == "매수" and out["premarket"]["live"]["dir_hit"] is False
    assert "legacy" not in out["premarket"]
    assert out["lessons_applied"] == ["L3"]                 # legacy 의 L9 는 세지 않는다
    assert out["live_ai"]["n"] == 1 and out["live_ai"]["trades"][0]["side"] == "매수"
    assert os.path.exists(os.path.join(M.day_dir("2026-10-07"), "eval.json"))
    txt = LN.render_eval(out)
    assert "개선 − 기존 = **+6.50 pt**" in txt and "기존(legacy 섀도)" in txt


# ── E. 레슨 레지스트리 ─────────────────────────────────────────────────────
def test_lessons_registry(sandbox):
    now = dt.datetime(2026, 10, 8, 16, 0, 0)
    l = LN.lesson_add("L9", "손절은 넓게", "V반등일 저항 매도 손절 ATR 비례", trigger="고변동", status="후보", evidence=["2026-10-07"], now=now)
    assert l["origin"] == "2026-10-08" and l["history"][0]["status"] == "후보"
    with pytest.raises(SystemExit):
        LN.lesson_add("L9", "중복", "x", now=now)
    with pytest.raises(SystemExit):
        LN.lesson_add("L10", "x", "y", status="이상함", now=now)
    LN.lesson_tally("L9", "2026-10-08", hit=True)
    LN.lesson_tally("L9", "2026-10-08", hit=True)            # 같은 날 두 번 → 한 번
    LN.lesson_tally("L9", "2026-10-09", hit=False, applied=True)
    LN.lesson_tally("L9", "2026-10-10", hit=True, applied=True)
    l = LN._find(LN.load_lessons(), "L9")
    assert l["hit"] == ["2026-10-08", "2026-10-10"] and l["miss"] == ["2026-10-09"] and l["applied"] == ["2026-10-09", "2026-10-10"]
    LN.lesson_tally("L9", "2026-10-11", hit=True, applied=True)
    assert "승격 검토" in LN.lesson_suggestion(LN._find(LN.load_lessons(), "L9"))
    LN.lesson_set("L9", status="적용중", why="3회 적중 우세", now=now)
    assert [x["id"] for x in LN.load_lessons() if x["status"] in LN.ACTIVE] == ["L9"]
    md = io.open(os.path.join(LN.LEARN_DIR, LN.REGISTRY_MD), encoding="utf-8").read()
    assert "| L9 | 적용중 |" in md and "3/3/1" in md
    assert "L9" in LN.lessons_text(active_only=True)


def test_feedback_requires_registered_lesson_and_writes_doc(sandbox, monkeypatch):
    cs = _bars([(100, 101, 99, 100), (100, 103, 100, 102.5), (101, 102, 96, 97)])
    log = [_rec("20:00:00", day="2026-10-06", phase="overnight", dir="매도", entry=None, stop=106.0, target=97.0)]
    orig = LN.evaluate_day
    monkeypatch.setattr(LN, "evaluate_day", lambda day, now=None, **k: orig(day, now, bars=cs, log=log, st={}))
    with pytest.raises(SystemExit):
        LN.feedback("2026-10-07", "본문", applied=["L99"])
    LN.lesson_add("L1", "Δ10 은 그림자", "Δ10 만으로 뒤집지 않는다", status="적용중", now=dt.datetime(2026, 10, 6))
    rec, out, p = LN.feedback("2026-10-07", "잘한 점: 방향. 잘못한 점: 없음.", applied=["L1"], hits=["L1"], now=dt.datetime(2026, 10, 7, 16, 0))
    assert rec["applied"] == ["L1"] and rec["hits"] == ["L1"] and rec["actual_dir"] == "매도"
    assert os.path.basename(p) == "피드백_%s-20261007.md" % LN.PC   # [MW0602 613차] PC 파생(하드코딩 MW0601 제거)
    doc = io.open(p, encoding="utf-8").read()
    assert "기계 평가" in doc and "잘한 점: 방향" in doc
    assert LN._find(LN.load_lessons(), "L1")["hit"] == ["2026-10-07"]
    assert LN.latest_feedback_before("2026-10-08")["date"] == "2026-10-07"


# ── F. 추이 판정 ───────────────────────────────────────────────────────────
def _row(date, live_pnl, legacy_pnl=None, hit=True):
    return dict(date=date, live=False, actual="매도", range=20.0,
                on_live=dict(dir="매도", hit=hit, pnl=live_pnl, filled=True, capture=None),
                on_legacy=(dict(dir="매도", hit=hit, pnl=legacy_pnl, filled=True, capture=None) if legacy_pnl is not None else None),
                pm_live=None, pm_legacy=None, ai_pnl=live_pnl, ai_n=1, rules_base=0.0, rules_p=None, lessons=[], feedback=True,
                fb_hits=[], fb_misses=[])


def test_trend_verdict_unmeasured_then_deepdive_then_ok():
    rows = [_row("2026-10-07", 5.0), _row("2026-10-08", -2.0)]
    v = LN.trend_verdict(rows, LN.trend_windows(rows))
    assert v["flag"] == "unmeasured"
    rows = [_row("2026-10-07", 1.0, 2.0), _row("2026-10-08", -2.0, 0.0), _row("2026-10-12", 0.0, 0.0)]
    v = LN.trend_verdict(rows, LN.trend_windows(rows))
    assert v["flag"] == "deepdive" and v["streak_nonimprove"] == 3
    rows = [_row("2026-10-07", 3.0, 2.0), _row("2026-10-08", 1.0, 0.0), _row("2026-10-12", 2.0, 0.0)]
    v = LN.trend_verdict(rows, LN.trend_windows(rows))
    assert v["flag"] == "ok" and v["messages"][0].startswith("✅")
    rows = [_row("2026-10-07", 3.0, 2.0, hit=False), _row("2026-10-08", 1.0, 0.0, hit=False), _row("2026-10-12", 2.0, 0.0, hit=True)]
    v = LN.trend_verdict(rows, LN.trend_windows(rows))
    assert v["flag"] == "deepdive" and any("방향 적중" in m for m in v["messages"])
    w = LN.trend_windows(rows)[5]
    assert w["improve_on"] == (1.33, 3) and w["on_hit"] == (0.33, 3)


def test_trend_render_marks_unmeasured_as_dash():
    rows = [_row("2026-10-07", 5.0)]
    md = LN.render_trend(rows, LN.trend_windows(rows), LN.trend_verdict(rows, LN.trend_windows(rows)))
    assert "| 2026-10-07 | 매도 | 20.00 | 매도✅ +5.00 | — |" in md


# ── G. 스킬 ────────────────────────────────────────────────────────────────
def test_skill_mentions_learning_cycle():
    p = os.path.join(_ROOT, ".claude", "skills", "shindong2", "SKILL.md")
    s = io.open(p, encoding="utf-8").read()
    for w in ("evaluate", "feedback", "lesson", "trend", "brief", "--variant legacy", "--lessons", "레슨런", "딥다이브", "워크포워드"):
        assert w in s, w
    assert "주문하지 않는다" in s and "사전등록 규칙을 건드리지 않는다" in s
