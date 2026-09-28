# -*- coding: utf-8 -*-
"""[MW0601 632차] 신동 섀도 변형 SHADOW_X4NF — R3 1차 목표 X4 + 같은 맥점 flip 금지.

무엇을 고정하나
---------------
A. 사전등록 — 채점 시작(9/29) · 판정 거래일 수가 조용히 바뀌지 않는다.
B. X4 목표 — 1차는 진입 방향의 **가장 가까운** 구조맥점 − TP_BUF, 현행 1차가 더 가까우면 현행.
C. 재생 — MAIN·SHADOW_E2F2 는 그대로(test_626 이 고정), X4NF 는 딥다이브 하네스와 같은 값.
   flip 금지 — 같은 맥점에서 진입 방향이 한 번도 바뀌지 않는다.
D. 채점표 — 9/28(만든 날) X4NF 행은 표본에서 빠지고, 판정은 10거래일 전엔 「대기」.

실행:
    conda run -n py37_32 python -m pytest tests/test_632_shindong_x4nf.py -q
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest  # noqa: E402

from strategy.shindong import engine, spec  # noqa: E402


# ── A ────────────────────────────────────────────────────────────────────
def test_x4nf_preregistration():
    assert "SHADOW_X4NF" in spec.VARIANTS
    assert spec.VARIANTS[0] == "MAIN"
    assert (spec.X4NF_SCORING_START, spec.X4NF_JUDGE_AFTER_DAYS) == ("2026-09-29", 10)
    assert spec.SPEC_VERSION == "SD-2026-09-24-v1"      # MAIN 값 무변경 → 버전 유지


# ── B ────────────────────────────────────────────────────────────────────
def _levels(struct):
    """08:50 만 있는 최소 맥점. 거리맥점 끝은 멀리(±20) 둔다."""
    lv = {"0850": {"struct_up": "[]", "struct_down": "[]",
                   "dist_low": 1080.0, "dist_high": 1120.0,
                   "low80_lo": 1070.0, "high80_hi": 1130.0}}
    L = engine.prepare_levels(lv)
    L["0850"]["S"] = sorted(struct)
    return L


def test_x4_pulls_t1_to_nearest_struct_level():
    L = _levels([1090.0, 1095.0, 1106.0, 1112.0])
    # 매수 1100: 현행 = 거리맥점 끝 1119.5 와 최종(가장 먼 구조 1112) 1111.5 를 맞바꿔 1차 1111.5,
    #            X4 = 위쪽 첫 맥점 1106 − 0.5
    t1, t2 = engine.targets(L, "10:00", 1, 1100.0)
    x1, x2 = engine.targets_x4(L, "10:00", 1, 1100.0)
    assert (t1, t2) == (pytest.approx(1111.5), pytest.approx(1119.5))
    assert x1 == pytest.approx(1105.5)
    assert x2 == pytest.approx(t2)                       # 최종은 현행 그대로
    # 매도 1100: 아래쪽 첫 맥점 1095(5pt ≥ T1_MIN_DIST) → 1095.5
    x1, _ = engine.targets_x4(L, "10:00", -1, 1100.0)
    assert x1 == pytest.approx(1095.5)


def test_x4_skips_levels_closer_than_min_dist():
    L = _levels([1101.0, 1106.0])
    x1, _ = engine.targets_x4(L, "10:00", 1, 1100.0)     # 1101 은 1pt < 2pt → 1106
    assert x1 == pytest.approx(1105.5)


def test_x4_keeps_current_t1_when_nearer():
    L = _levels([1115.0])
    L["0850"]["dist_high"] = 1104.0                      # 현행 1차 1103.5 가 더 가깝다
    x1, _ = engine.targets_x4(L, "10:00", 1, 1100.0)
    assert x1 == pytest.approx(1103.5)


# ── C ────────────────────────────────────────────────────────────────────
_DB_OK = all(os.path.exists(os.path.join(_ROOT, p)) for p in
             ("data/db/raw_data.db", "data/db/option_flow.db", "data/db/premarket_levels.db"))


def _compute(day):
    from strategy.shindong import runner
    return runner.compute(day, os.path.join(_ROOT, "data/db/raw_data.db"),
                          os.path.join(_ROOT, "data/db/option_flow.db"),
                          os.path.join(_ROOT, "data/db/premarket_levels.db"))


@pytest.mark.skipif(not _DB_OK, reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
@pytest.mark.parametrize("day,main,x4nf", [
    # 2026-09-28 딥다이브 하네스(docs/신동거래/r3_딥다이브_20260928/s8.py) R3 값 + R2
    ("2026-09-21", 157978, -43602),
    ("2026-09-22", 1629902, 1629902),
    ("2026-09-23", 1776971, 1776971),
    ("2026-09-28", 330667, 828674),
])
def test_replay_x4nf(day, main, x4nf):
    r = _compute(day)
    if not r["results"]["MAIN"]["trades"] and "봉 없음" in str(r["results"]["MAIN"]["decision"]):
        pytest.skip("그날 봉이 이 PC DB 에 없다")
    got = {v: round(sum(engine.trade_net(t) for t in res["trades"]))
           for v, res in r["results"].items()}
    assert got["MAIN"] == pytest.approx(main, abs=2)
    assert got["SHADOW_X4NF"] == pytest.approx(x4nf, abs=2)
    # R2 는 MAIN 과 같다 — X4NF 는 R3 만 바꾼다
    r2 = lambda v: [(t["entry_ts"], round(engine.trade_net(t))) for t in r["results"][v]["trades"]
                    if t["rule"] == "R2"]
    assert r2("SHADOW_X4NF") == r2("MAIN")


@pytest.mark.skipif(not _DB_OK, reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
def test_x4nf_never_flips_at_same_level_but_main_did():
    r = _compute("2026-09-28")
    if not r["results"]["MAIN"]["trades"]:
        pytest.skip("그날 봉이 이 PC DB 에 없다")

    def sides(v):
        m = {}
        for t in r["results"][v]["trades"]:
            if t["rule"] == "R3":
                m.setdefault(t["touch_level"], set()).add(t["side"])
        return m
    assert any(len(s) > 1 for s in sides("MAIN").values())        # MAIN 은 1090 에서 뒤집었다
    assert all(len(s) == 1 for s in sides("SHADOW_X4NF").values())


# ── D ────────────────────────────────────────────────────────────────────
def test_scorecard_excludes_build_day_and_waits(tmp_path):
    import importlib.util
    sp = importlib.util.spec_from_file_location(
        "shindong_scorecard", os.path.join(_ROOT, "scripts", "shindong_scorecard.py"))
    sc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(sc)
    from strategy.shindong import store
    db = str(tmp_path / "sd.db")
    tr = {"side": -1, "entry_ts": "09:47", "entry_px": 1103.6, "stop_init": 1107.5,
          "t1": 1100.5, "t2": 1092.75, "status": "CLOSED", "exit_ts": "10:19", "stop_now": 1103.6,
          "rule": "R3", "touch_level": 1106.0, "touch_ts": "09:45",
          "legs": [{"leg": 1, "open": False, "ts": "09:55", "px": 1100.5, "reason": "TP1",
                    "pts": 3.1, "net": 100000.0},
                   {"leg": 2, "open": False, "ts": "10:19", "px": 1092.75, "reason": "TP2",
                    "pts": 10.85, "net": 500000.0}]}
    res = {"decision": {"pm_sp": 279.0, "bias": -1, "r2": "CONFIRMED", "r2_ts": "09:03", "notes": []},
           "trades": [tr]}
    for day in ("2026-09-28", "2026-09-29"):
        for v in spec.VARIANTS:
            store.save_day(db, day, v, "wk_mon", "", res, "15:08", spec.SPEC_VERSION, source="backfill")
    txt = sc.build(db, spec.SCORING_START)
    assert "SHADOW_X4NF 채점 시작(2026-09-29) 전 행 **1건** — 표본 제외" in txt
    assert "판정: **대기** — 1/10 거래일" in txt


# ── E. [632차 후속] SHADOW_TR44 — R3 트레일 4/4 (비교 기록용) ──────────────────
def test_tr44_preregistration():
    assert spec.VARIANTS[-1] == "SHADOW_TR44"
    assert (spec.TR44_ACT, spec.TR44_DIST) == (4.0, 4.0)
    assert spec.LATE_SHADOW_START == {"SHADOW_X4NF": "2026-09-29", "SHADOW_TR44": "2026-09-29"}


def _frame(bars):
    """[(HH:MM, o, h, l, c)] → DayFrame(흐름 없음)."""
    return engine.DayFrame({t: (o, h, l, c) for t, o, h, l, c in bars}, {})


def test_trail_ratchets_and_exits_tr():
    # 매수 100 → 고점 106 → 되밀림. 발동 4 · 간격 4: 104 도달 뒤 손절 100, 106 도달 뒤 102
    d = _frame([("10:00", 100, 100, 100, 100), ("10:01", 100, 104, 100.5, 103),
                ("10:02", 103, 106, 103, 105), ("10:03", 105, 105, 101.5, 102)])
    tr = engine.run_trade(d, 1, "10:00", 95.0, 130.0, 140.0, trail=(4.0, 4.0))
    assert [g.get("reason") for g in tr["legs"]] == ["TR", "TR"]
    assert all(g["px"] == pytest.approx(102.0) and g["ts"] == "10:03" for g in tr["legs"])
    assert tr["status"] == "CLOSED"


def test_trail_uses_previous_bar_stop_same_bar_conservative():
    # 한 봉에서 +4 찍고 곧바로 −5 — 그 봉은 이전 손절(95)로만 검사한다(트레일은 다음 봉부터)
    d = _frame([("10:00", 100, 100, 100, 100), ("10:01", 100, 104, 96, 97)])
    tr = engine.run_trade(d, 1, "10:00", 95.0, 130.0, 140.0, trail=(4.0, 4.0))
    assert all(g["open"] for g in tr["legs"])
    assert tr["stop_now"] == pytest.approx(100.0)       # 다음 봉부터 본전


def test_trail_none_is_main_path():
    d = _frame([("10:00", 100, 100, 100, 100), ("10:01", 100, 104, 100, 103),
                ("10:02", 103, 106, 103, 105), ("10:03", 105, 105, 94, 95)])
    a = engine.run_trade(d, 1, "10:00", 95.0, 130.0, 140.0)
    b = engine.run_trade(d, 1, "10:00", 95.0, 130.0, 140.0, trail=None)
    assert a == b
    assert [g.get("reason") for g in a["legs"]] == ["SL", "SL"]


@pytest.mark.skipif(not _DB_OK, reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
@pytest.mark.parametrize("day,tr44", [
    # 트레일 딥다이브(c9.py) R3 −1 / +153 / +44 / −68만 + R2(MAIN 과 같다)
    ("2026-09-21", 157978),
    ("2026-09-22", 1527679),
    ("2026-09-23", 1776971),
    ("2026-09-28", 330667),
])
def test_replay_tr44(day, tr44):
    r = _compute(day)
    if not r["results"]["MAIN"]["trades"] and "봉 없음" in str(r["results"]["MAIN"]["decision"]):
        pytest.skip("그날 봉이 이 PC DB 에 없다")
    got = round(sum(engine.trade_net(t) for t in r["results"]["SHADOW_TR44"]["trades"]))
    assert got == pytest.approx(tr44, abs=2)
    r2 = lambda v: [(t["entry_ts"], round(engine.trade_net(t))) for t in r["results"][v]["trades"]
                    if t["rule"] == "R2"]
    assert r2("SHADOW_TR44") == r2("MAIN")


# ── F. 채점표 R1 방향 적중률 ─────────────────────────────────────────────────
def test_scorecard_r1_hit_rate(tmp_path):
    import importlib.util
    import sqlite3
    sp = importlib.util.spec_from_file_location(
        "shindong_scorecard", os.path.join(_ROOT, "scripts", "shindong_scorecard.py"))
    sc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(sc)
    raw = str(tmp_path / "raw.db")
    con = sqlite3.connect(raw)
    con.execute("CREATE TABLE raw_candles (ts TEXT, open REAL, high REAL, low REAL, close REAL)")
    for day, a, b in (("2026-09-29", 100.0, 90.0),      # 하방 적중
                      ("2026-09-30", 100.0, 105.0),     # 하방 불적중
                      ("2026-10-01", 100.0, None)):     # 15:05 봉 없음 → 미측정
        con.execute("INSERT INTO raw_candles VALUES (?,?,?,?,?)", (day + " 09:00:00", a, a, a, a))
        if b is not None:
            con.execute("INSERT INTO raw_candles VALUES (?,?,?,?,?)", (day + " 15:05:00", b, b, b, b))
    con.commit()
    con.close()
    days = [{"variant": "MAIN", "trade_date": d, "bias": -1} for d in ("2026-09-29", "2026-09-30", "2026-10-01")]
    days.append({"variant": "MAIN", "trade_date": "2026-10-02", "bias": 0})   # 보류 — 대상 아님
    hits = sc._r1_hits(days, raw)
    assert [h[4] for h in hits] == [True, False, None]
    txt = "\n".join(sc._r1_section(hits))
    assert "적중 **1 / 2** = **50%**" in txt
    assert "미측정 1일 제외" in txt
    # 원천 DB 가 없으면 전부 미측정(0 이 아니다)
    assert [h[4] for h in sc._r1_hits(days, str(tmp_path / "none.db"))] == [None, None, None]
