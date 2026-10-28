# -*- coding: utf-8 -*-
"""[MW0602 670차 후속] 신동AI 봉 신선도 — 3단계 등급(ok/lag/moved) · 레벨 관통 · 기록 직전 `delta` · 기록 시점 보정(P1–P3).

계기: 2026-10-28 「위반 13/18」 — 7건은 고·저가 그대로인 지연뿐이고(무해) 6건은 고가 갱신(그중 plan 2건)이었다.
두 종류가 한 수치에 묶여 있었고(계측 4원칙 ③), 경고는 기록이 끝난 뒤에만 떠서 그 기록을 고칠 수 없었다.

고정하는 것
-----------
A. 등급 — 지연만 = lag(🟡) · 고·저 갱신 또는 레벨 관통 = moved(🔴) · 1봉 = ok(줄 없음) · 조회 실패 = unmeasured(⚪, 위장 금지).
B. 레벨 관통 — 기준 이후 봉 범위가 이 기록의 진입·손절·청산·시나리오 레벨을 건드리면 moved. 기준 이전에 지난 레벨은 세지 않는다.
C. 소급 — 등급 도입 전 행(10-27·28)은 저장된 극값으로 분류된다(stale 정의는 그대로 남는다).
D. delta — 기준을 앞으로 당긴다(fresh_seen.json). 바로 이어 record 하면 ok. 새 snapshot 이 더 늦으면 snapshot 이 기준.
E. record — moved 면 문서에 「⏱ 기록 시점 보정」 줄이 붙는다. 기록은 막지 않는다.
F. 장후 집계 — moved/lag 를 따로 센다 · 패널이 moved 를 보인다 · 스킬에 delta 절차가 있다.

실행: conda run -n py37_32 python -m pytest tests/test_670_shindong2_freshness_delta.py -v
"""
import datetime as dt
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
import shindong2_pmethod as PM  # noqa: E402
import shindong2_live as M      # noqa: E402
import ladder_data as L         # noqa: E402

DAY = "2026-10-28"


def _bars(rows, start="09:00"):
    h, m = map(int, start.split(":"))
    return [["%02d:%02d" % ((h * 60 + m + i) // 60, (h * 60 + m + i) % 60)] + list(r) for i, r in enumerate(rows)]


@pytest.fixture
def feed(monkeypatch):
    """봉 공급 — 마지막 봉은 장중이라 덜 찬 봉으로 빠진다(freshness 와 같은 규칙)."""
    box = {}

    def set_bars(rows, start="09:00"):
        box["bars"] = _bars(rows, start) + [["99:99", 0, 0, 0, 0]]
    monkeypatch.setattr(L, "is_live", lambda day, now=None: True)
    monkeypatch.setattr(L, "candles", lambda day, live: (box["bars"], "test"))
    return set_bars


# 09:00–09:05 고 905 저 899(09:01–09:05 는 900–904), 09:06–09:08 은 902–904 안에서만 논다(극값 갱신 없음)
FLAT = [(900, 905, 899, 902)] + [(902, 904, 900, 903)] * 5 + [(903, 904, 902, 903)] * 3


# ── A. 등급 ───────────────────────────────────────────────────────────────
def test_lag_only_is_yellow_not_red(feed):
    feed(FLAT)
    fr = PM.freshness(DAY, dict(last_bar="09:05", hi=905, lo=899))
    assert fr["rec_bar"] == "09:08" and fr["lag_bars"] == 3
    assert fr["grade"] == "lag" and fr["stale"] is True             # stale(종전 정의)은 유지된다
    line = PM.freshness_line(fr)
    assert line.startswith("🟡") and "갱신·레벨 관통 없음" in line
    assert PM.correction_line(fr) is None                           # lag 에는 보정 줄을 붙이지 않는다


def test_new_high_is_moved(feed):
    feed(FLAT[:7] + [(903, 907.5, 902, 907)] * 2)
    fr = PM.freshness(DAY, dict(last_bar="09:05", hi=905, lo=899))
    assert fr["grade"] == "moved" and fr["new_hi"] == 907.5
    assert PM.freshness_line(fr).startswith("🔴") and "고 907.50 갱신" in PM.freshness_line(fr)
    assert PM.correction_line(fr).startswith("⏱ 기록 시점 보정: 완결 봉 09:08 · 현재가 907")


def test_one_bar_is_ok_and_silent(feed):
    feed(FLAT)
    fr = PM.freshness(DAY, dict(last_bar="09:07", hi=905, lo=899))
    assert fr["grade"] == "ok" and fr["stale"] is False and PM.freshness_line(fr) is None


def test_unmeasured_not_disguised(monkeypatch):
    monkeypatch.setattr(L, "is_live", lambda day, now=None: True)

    def boom(day, live):
        raise IOError("db")
    monkeypatch.setattr(L, "candles", boom)
    fr = PM.freshness(DAY, dict(last_bar="09:03", hi=1, lo=0))
    assert fr["grade"] == "unmeasured" and PM.freshness_line(fr).startswith("⚪")


# ── B. 레벨 관통 ──────────────────────────────────────────────────────────
def test_level_hit_without_new_extreme_is_moved(feed):
    feed(FLAT)                                                      # 기준(09:05) 뒤 범위 902–904
    fr = PM.freshness(DAY, dict(last_bar="09:05", hi=905, lo=899), [("진입", 903.0), ("청산", 910.0)])
    assert fr["level_hit"] == ["진입 903"] and fr["grade"] == "moved"
    assert "레벨 관통 진입 903" in PM.freshness_line(fr)


def test_level_passed_before_base_is_not_counted(feed):
    feed(FLAT)
    # 899 는 09:00 봉에서 지나갔다 — 기준(09:05) 뒤 범위 902–904 밖이므로 관통 아님
    fr = PM.freshness(DAY, dict(last_bar="09:05", hi=905, lo=899), [("손절", 899.0)])
    assert fr["level_hit"] == [] and fr["grade"] == "lag"


def test_record_levels_include_scenarios():
    items = [dict(key="A", target=920.0, invalid=899.0, then=None), dict(key="B", target=890.3, invalid=906.0, then=None)]
    lv = M.record_levels(899.5, 896.5, None, items)
    assert ("진입", 899.5) in lv and ("손절", 896.5) in lv and ("A목표", 920.0) in lv and ("B무효", 906.0) in lv
    assert all(n != "청산" for n, _ in lv)                          # None 레벨은 빠진다


# ── C. 소급 ───────────────────────────────────────────────────────────────
def test_legacy_rows_are_graded_from_stored_extremes():
    assert PM.fresh_grade(dict(rec_bar="09:19", stale=True, new_hi=914.18, new_lo=None)) == "moved"
    assert PM.fresh_grade(dict(rec_bar="09:08", stale=True, new_hi=None, new_lo=None)) == "lag"
    assert PM.fresh_grade(dict(rec_bar="09:36", stale=False)) == "ok"
    assert PM.fresh_grade(dict(rec_bar=None, why="x")) == "unmeasured"
    assert PM.fresh_grade(None) is None


# ── D. delta ──────────────────────────────────────────────────────────────
@pytest.fixture
def live_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(M, "DOC_DIR", str(tmp_path / "doc"))
    d = M.day_dir(DAY)
    with open(os.path.join(d, "state.json"), "w", encoding="utf-8") as f:
        json.dump(dict(date=DAY, last_bar="09:05", hi=905, lo=899, px=903), f)
    return d


def test_delta_moves_base_then_record_is_ok(feed, live_dirs):
    feed(FLAT[:7] + [(903, 907.5, 902, 907)] * 2)
    fr, levels = M.cmd_delta(DAY, entry=906.0, stop=903.0, target=912.0)
    assert fr["grade"] == "moved" and "진입 906" in fr["level_hit"]
    out = "\n".join(PM.delta_lines(fr, levels))
    assert "🔴 움직였다" in out and "새 기준" in out
    seen = json.load(open(os.path.join(live_dirs, "fresh_seen.json"), encoding="utf-8"))
    assert seen["last_bar"] == "09:08" and seen["hi"] == 907.5 and seen["lo"] == 899 and seen["base"] == "delta"
    rec = M.record(DAY, "intraday", "plan", "매수", 906.0, 903.0, 912.0, "본문",
                   now=dt.datetime(2026, 10, 28, 9, 9, 10), scenarios="A|상승|60|912|903 ; B|하락|40|900|907.6")
    assert rec["fresh"]["grade"] == "ok" and rec["fresh"]["base"] == "delta"


def test_newer_snapshot_overrides_delta(live_dirs):
    with open(os.path.join(live_dirs, "fresh_seen.json"), "w", encoding="utf-8") as f:
        json.dump(dict(base="delta", last_bar="09:04", hi=905, lo=899), f)
    assert M.fresh_base(DAY)["last_bar"] == "09:05" and (M.fresh_base(DAY).get("base") or "snapshot") == "snapshot"
    with open(os.path.join(live_dirs, "fresh_seen.json"), "w", encoding="utf-8") as f:
        json.dump(dict(base="delta", last_bar="09:07", hi=905, lo=899), f)
    assert M.fresh_base(DAY)["base"] == "delta"


def test_delta_compares_previous_plan_levels(feed, live_dirs):
    feed(FLAT)
    M.record(DAY, "intraday", "plan", "매수", 903.0, 897.0, 915.0, "본문",
             now=dt.datetime(2026, 10, 28, 9, 5, 30), scenarios="A|상승|60|915|897 ; B|하락|40|895|906")
    with open(os.path.join(live_dirs, "state.json"), "w", encoding="utf-8") as f:   # 기록 뒤 기준은 09:05 그대로
        json.dump(dict(date=DAY, last_bar="09:05", hi=905, lo=899), f)
    fr, levels = M.cmd_delta(DAY)
    assert ("직전진입", 903.0) in levels and "직전진입 903" in fr["level_hit"]


# ── E. record — 보정 줄 · 막지 않는다 ─────────────────────────────────────
def test_record_appends_correction_line_and_still_records(feed, live_dirs):
    feed(FLAT[:7] + [(903, 907.5, 902, 907)] * 2)
    rec = M.record(DAY, "intraday", "note", "매수", None, None, None, "본문 첫 줄",
                   now=dt.datetime(2026, 10, 28, 9, 9, 10), scenarios="A|상승|60|912|903 ; B|하락|40|900|908")
    assert rec["fresh"]["grade"] == "moved"
    doc = open(M._doc_path(DAY), encoding="utf-8").read()
    assert "> 🔴 봉 신선도" in doc and "> ⏱ 기록 시점 보정: 완결 봉 09:08" in doc
    assert len(M.load_ai_log(DAY)) == 1                            # 기록은 남는다(벽시계 원칙)


# ── F. 집계 · 패널 · 스킬 ─────────────────────────────────────────────────
def test_trend_renders_moved_lag_and_legacy_rows():
    cfg = dict(id="PM-test", box=dict(T=[]))
    rows = [dict(date="2026-10-28", fresh=dict(n=18, stale=13, unmeasured=0)),          # 3단계 도입 전 행
            dict(date="2026-10-29", fresh=dict(n=10, stale=4, moved=1, lag=3, delta_base=6, unmeasured=0))]
    md = PM.render_trend(rows, cfg)
    assert "🔴moved 1 · 🟡lag 3 / 측정 28" in md and "delta 기준 6" in md
    assert "| 위반 13/18 |" in md and "| 1/3/10 |" in md


def test_panel_shows_moved_note():
    latest = dict(ts="2026-10-28T09:52:22", dir="매수", entry=920.0, stop=917.5, target=923.1, comment="결론",
                  fresh=dict(grade="moved", snap_bar="09:48", rec_bar="09:50", new_hi=923.14, level_hit=[]))
    out = L.plain_lines(DAY, [], False, None, latest, None)
    assert "⏱ 이 판단은 09:48 봉을 보고 썼다" in out["ai"] and "고 923.14" in out["ai"]
    latest["fresh"] = dict(grade="lag", snap_bar="09:48", rec_bar="09:50")
    assert "⏱" not in L.plain_lines(DAY, [], False, None, latest, None)["ai"]


def test_skill_requires_delta_before_record():
    s = open(os.path.join(_ROOT, ".claude", "skills", "shindong2", "SKILL.md"), encoding="utf-8").read()
    assert "shindong2_live.py delta" in s
    assert "`record` 바로 앞에 `delta` 를 부른다" in s
    assert "moved" in s and "lag" in s
