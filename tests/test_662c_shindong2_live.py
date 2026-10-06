# -*- coding: utf-8 -*-
"""[MW0601 662차 후속4] 신동2 라이브 — 재량 기록·채점 · 이벤트 감지 · 사다리 해설 패널 · 스킬.

고정하는 것
-----------
A. 재량 채점 — 효력은 기록 **다음 분 봉부터**, 같은 봉 손절 우선, 15:10 강제청산, 장중 보유는 평가로만.
B. 기록 — plan 은 손절·청산 필수, append-only, 문서에 덧붙인다, 시각은 벽시계(지정 인자 없음).
C. 이벤트 — 같은 키는 한 번만 저장된다.
D. 사다리 — 해설 패널 배선, 기록 폴더가 없으면 None(미기록 ≠ 0).
E. 스킬 파일 — 주문 금지·사전등록 불변·conda 경유가 적혀 있다.

실행: conda run -n py37_32 python -m pytest tests/test_662c_shindong2_live.py -v
"""
import datetime as dt
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import shindong2_live as M  # noqa: E402


def _bars(prices, start="09:00"):
    h, m = map(int, start.split(":"))
    out = []
    for i, (o, hi, lo, c) in enumerate(prices):
        t = h * 60 + m + i
        out.append(["%02d:%02d" % (t // 60, t % 60), o, hi, lo, c])
    return out


def _rec(ts, **kw):
    r = dict(id=ts, ts="2026-10-07T%s" % ts, phase="intraday", action="plan")
    r.update(kw)
    return r


# ── A. 재량 채점 ───────────────────────────────────────────────────────────
def test_effect_starts_next_minute_and_limit_fill():
    # 09:00:30 기록 → 09:01 봉부터. 09:00 봉이 진입가를 지나도 체결 아님
    cs = _bars([(100, 101, 99, 100), (100, 100.5, 99.5, 100), (100, 102, 100, 101.5)])
    r = M.simulate_ai("2026-10-07", cs, [_rec("09:00:30", dir="매수", entry=101.0, stop=98.0, target=110.0)])
    assert r["trades"][0]["entry_t"] == "09:02" and r["trades"][0]["fill"] == 101.0


def test_stop_wins_same_bar_and_target():
    cs = _bars([(100, 100, 100, 100), (100, 106, 94, 100)])
    r = M.simulate_ai("2026-10-07", cs, [_rec("08:59:00", dir="매수", entry=None, stop=95.0, target=105.0)])
    t = r["trades"][0]
    assert t["how"] == "시장가" and t["why"] == "손절" and t["pnl"] == -5.0


def test_forced_exit_and_live_open():
    cs = _bars([(100, 100.5, 99.5, 100)] * 13, start="14:57")    # 14:57–15:09
    recs = [_rec("14:56:10", dir="매도", entry=None, stop=110.0, target=90.0)]
    r = M.simulate_ai("2026-10-07", cs, recs)
    assert r["trades"][0]["entry_t"] == "14:57" and r["trades"][0]["why"] == "15:10 강제청산"
    r2 = M.simulate_ai("2026-10-07", cs[:4], recs, live=True)
    assert r2["trades"][0].get("open") and r2["pnl"] == 0.0         # 장중 평가는 합계에 넣지 않는다
    late = M.simulate_ai("2026-10-07", cs, [_rec("15:03:00", dir="매도", entry=None, stop=110.0, target=90.0)])
    assert late["trades"] == []                                      # 15:00 이후 신규 진입 계획은 체결하지 않는다


def test_manage_exit_stand_and_premarket_record():
    cs = _bars([(100, 100.2, 99.8, 100)] * 6, start="08:45")
    recs = [dict(id="a", ts="2026-10-06T20:00:00", phase="overnight", action="plan", dir="매도", entry=None, stop=105.0, target=90.0),
            _rec("08:47:10", action="manage", stop=101.0),
            _rec("08:48:10", action="exit")]
    r = M.simulate_ai("2026-10-07", cs, recs)
    t = r["trades"][0]
    assert t["entry_t"] == "08:45" and t["why"] == "재량 청산" and t["exit_t"] == "08:49"
    r2 = M.simulate_ai("2026-10-07", cs, [_rec("08:44:00", dir="매수", entry=50.0, stop=40.0, target=60.0),
                                          _rec("08:46:00", action="stand")])
    assert r2["trades"] == [] and r2["pending"] is None


def test_backfill_records_are_ignored():
    cs = _bars([(100, 101, 99, 100)] * 3)
    r = M.simulate_ai("2026-10-07", cs, [_rec("08:59:00", dir="매수", entry=None, stop=90.0, target=110.0, backfill=True)])
    assert r["trades"] == []


# ── B. 기록 ───────────────────────────────────────────────────────────────
def test_record_requires_stop_target_and_appends(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(M, "DOC_DIR", str(tmp_path / "doc"))
    with pytest.raises(SystemExit):
        M.record("2026-10-07", "intraday", "plan", "매수", 100.0, None, 110.0, "x")
    now = dt.datetime(2026, 10, 7, 9, 12, 30)
    M.record("2026-10-07", "intraday", "plan", "매수", 100.0, 96.0, 110.0, "**결론** 매수", now=now)
    M.record("2026-10-07", "intraday", "note", "관망", None, None, None, "유지", now=now + dt.timedelta(minutes=10))
    log = M.load_ai_log("2026-10-07")
    assert [r["action"] for r in log] == ["plan", "note"] and log[0]["ts"] == "2026-10-07T09:12:30"
    doc = open(M._doc_path("2026-10-07"), encoding="utf-8").read()
    assert doc.startswith("# 신동2 해설") and "09:12 장중" in doc and "09:22 장중" in doc
    import inspect
    assert "asof" not in inspect.signature(M.main).parameters and "--asof" not in open(M.__file__, encoding="utf-8").read().split("def main")[1]


# ── C. 이벤트 ─────────────────────────────────────────────────────────────
def test_events_are_saved_once(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path / "live"))
    ev = [dict(key="p:set", t="09:05", kind="세팅", text="x"), dict(key="prev_low_break", t="12:09", kind="구조", text="y")]
    now = dt.datetime(2026, 10, 7, 12, 10)
    assert len(M.save_new_events("2026-10-07", ev, now)) == 2
    assert M.save_new_events("2026-10-07", ev, now) == []


def test_detect_events_gap_text():
    st = dict(last_bar="09:30", open=1120.0, hi=1121.0, lo=1110.0, prev=dict(high=1115.0, low=1100.0, close=1110.0),
              prev_high_break_t="08:45", prev_low_break_t=None, gap="상승",
              sd2=dict(points=[], variants={}))
    ev = M.detect_events(st)
    assert ev[0]["key"] == "prev_high_break" and ev[0]["text"].startswith("갭 상승")


# ── D. 사다리 ─────────────────────────────────────────────────────────────
def test_ladder_wires_ai_panel(tmp_path, monkeypatch):
    html = open(os.path.join(_ROOT, "tools", "maekjeom_ladder", "ladder.html"), encoding="utf-8").read()
    assert "sd2aiSec" in html and "function drawAI" in html and "D.sd2ai" in html and "['ai','AI']" in html
    sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
    import ladder_data as LD
    monkeypatch.setattr(LD._sd2_live_mod(), "LIVE_DIR", str(tmp_path / "none"))
    assert LD.shindong2_ai("2026-10-07", [], False) is None


# ── E. 스킬 ───────────────────────────────────────────────────────────────
def test_skill_file_states_guards():
    s = open(os.path.join(_ROOT, ".claude", "skills", "shindong2", "SKILL.md"), encoding="utf-8").read()
    assert s.startswith("---\nname: shindong2")
    for must in ("주문하지 않는다", "사전등록 규칙을 건드리지 않는다", "conda run --no-capture-output -n py310_64", "456차", "--for-date"):
        assert must in s, must
