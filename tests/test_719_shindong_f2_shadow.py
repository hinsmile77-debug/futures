# -*- coding: utf-8 -*-
"""[MW0601 719차] 신동 섀도 SHADOW_F2 — SHADOW_V2(트레일 없음) + R3 F2 만(E2 없음). 분석명 「V2+F2」.

고정하는 것
  A. 사전등록: VARIANTS 끝 · 채점 시작 2026-10-27 · MAIN 값·SPEC_VERSION 무변경.
  B. 엔진: F2 는 R3 에만 걸린다 — 흐름 Δ>0 이면 매도 R3 만, 아니면 매수 R3 만. 트레일·E2 없음.
  C. 재생: 분석 f2_final(①SHADOW_F2)과 원 단위로 같다(MW0601 DB).
  D. 리포트 라벨 · 귀인 문구.
"""
import datetime as _dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest  # noqa: E402

from strategy.shindong import engine, spec  # noqa: E402


# ── A ─────────────────────────────────────────────────────────────────
def test_preregistered():
    assert spec.VARIANTS[-1] == "SHADOW_F2"
    assert spec.LATE_SHADOW_START["SHADOW_F2"] == spec.SCORING_START == "2026-10-27"
    assert spec.SPEC_VERSION == "SD-2026-10-27-v4"               # MAIN 값 무변경 → 버전 유지
    assert spec.CONF_BASE == "09:00"                             # F2 기준 분(E2F2 와 같다)


def test_engine_flags():
    src = open(os.path.join(ROOT, "strategy", "shindong", "engine.py"), encoding="utf-8").read()
    assert 'e2 = variant == "SHADOW_E2F2"' in src                # E2 는 E2F2 만
    assert 'f2 = variant in ("SHADOW_E2F2", "SHADOW_F2")' in src
    # 트레일 목록에 없다 → tr44 None(= SHADOW_V2)
    assert 'elif variant in ("MAIN", "SHADOW_V3", "SHADOW_ATRS", "SHADOW_R2D7"):' in src


# ── B ─────────────────────────────────────────────────────────────────
def _day(sp_after):
    """09:30 저점 맥점(1090) 터치 → 반전 확인 → 매수 R3 후보. 흐름(콜−풋) 09:00 대비 sp_after 로 둔다."""
    bars, flow = {}, {"08:59": (100.0, 100.0), "09:00": (100.0, 100.0)}
    for m in range(0, 60):
        t = "09:%02d" % m
        px = 1095.0
        lo = px - 0.5
        if t == "09:31":
            px, lo = 1091.0, 1089.5                               # 1090 맥점 터치 뒤 위 마감
        bars[t] = (px, px + 0.5, lo, px)
        if m >= 1:
            call = 100.0 + sp_after
            put = 100.0 + (60.0 if m >= 33 else 0.0)              # 09:33 풋 +60 → 콜−풋 −60 반전(매수 확인)
            flow[t] = (call, put)
    row = {"struct_up": json.dumps([[1120.0, ["구조"]]]), "struct_down": json.dumps([[1090.0, ["구조"]]]),
           "dist_low": 1070.0, "dist_high": 1110.0, "low80_lo": 1060.0, "high80_hi": 1130.0}
    return engine.DayFrame(bars, flow), engine.prepare_levels({"0850": row})


def _r3(res):
    return [t for t in res["trades"] if t["rule"] == "R3"]


def test_buy_r3_passes_when_flow_not_up():
    d, L = _day(sp_after=0.0)                                     # Δ=0 → 매수 쪽(중립 폭 없음)
    v2 = _r3(engine.run_day(d, L, "SHADOW_V2"))
    f2 = _r3(engine.run_day(d, L, "SHADOW_F2"))
    assert v2 and v2[0]["side"] == 1
    assert [(t["entry_ts"], t["side"]) for t in f2] == [(t["entry_ts"], t["side"]) for t in v2]


def test_buy_r3_blocked_when_flow_up():
    d, L = _day(sp_after=200.0)                                   # Δ>0 → 매도만
    assert _r3(engine.run_day(d, L, "SHADOW_V2"))                 # V2 는 받는다
    assert not [t for t in _r3(engine.run_day(d, L, "SHADOW_F2")) if t["side"] == 1]


# ── C ─────────────────────────────────────────────────────────────────
_DBS = [os.path.join(ROOT, "data", "db", p) for p in ("raw_data.db", "option_flow.db", "premarket_levels.db")]
try:
    from utils.db_utils import pc_id as _pc_id
    _SRC_OK = all(os.path.exists(p) for p in _DBS) and _pc_id() == "MW0601"
except Exception:                         # noqa: BLE001
    _SRC_OK = False


@pytest.mark.skipif(not _SRC_OK, reason="기대값은 MW0601 DB 산출")
@pytest.mark.parametrize("day,net", [
    # 분석 f2_final ①SHADOW_F2(V2+F2) — 22일 합 +7,967,315
    ("2026-09-29", -2567403),
    ("2026-10-15", 1939529),
    ("2026-10-21", -817323),
    ("2026-10-22", 2064965),
    ("2026-10-23", -1091976),
    ("2026-10-26", 240801),
])
def test_replay_matches_analysis(day, net):
    from strategy.shindong import runner
    from strategy.shindong.calendar import select_flow_product
    c, f, l = runner.load_inputs(day, select_flow_product(_dt.date.fromisoformat(day))[0], *_DBS)
    d, L = engine.DayFrame(c, f), engine.prepare_levels(l)
    res = engine.run_day(d, L, "SHADOW_F2")
    assert round(sum(engine.trade_net(t) for t in res["trades"] if t["status"] == "CLOSED")) == \
        pytest.approx(net, abs=2)
    assert not any(g.get("reason") == "TR" for t in res["trades"] for g in t["legs"])   # 트레일 없음


# ── D ─────────────────────────────────────────────────────────────────
def test_report_label_and_attribution():
    from strategy.shindong import daily_report
    assert daily_report.VLABEL["SHADOW_F2"].startswith("F2")
    src = open(os.path.join(ROOT, "strategy", "shindong", "daily_report.py"), encoding="utf-8").read()
    assert 'variant in ("SHADOW_E2F2", "SHADOW_F2")' in src     # 「F2 차단(당일 흐름 역방향)」 귀인 공유


# ── E [719차 후속] GAPSW 합성 줄 ─────────────────────────────────────────
def test_gapsw_preregistered():
    assert (spec.GAPSW_DOWN_PCT, spec.GAPSW_DOWN_VARIANT, spec.GAPSW_ELSE_VARIANT, spec.GAPSW_GAP_CODE) == \
        (-0.5, "SHADOW_F2", "MAIN", "10100")
    assert spec.GAPSW_SCORING_START == spec.SCORING_START == "2026-10-27"
    assert {spec.GAPSW_DOWN_VARIANT, spec.GAPSW_ELSE_VARIANT} <= set(spec.VARIANTS)   # 기록되는 변형끼리만 고른다


def _gapsw_dbs(tmp_path, gaps, main_net, f2_net):
    import sqlite3
    from strategy.shindong import store
    sd, reg = str(tmp_path / "sd.db"), str(tmp_path / "reg.db")
    days = sorted(gaps)
    con = store.connect(sd)
    with con:
        for i, day in enumerate(days):
            for v, n in (("MAIN", main_net[i]), ("SHADOW_F2", f2_net[i])):
                con.execute("INSERT INTO shindong_day(trade_date,variant,bias,spec_version,updated_at) VALUES(?,?,?,?,?)",
                            (day, v, -1, spec.SPEC_VERSION, "x"))
                con.execute("""INSERT INTO shindong_trades(trade_date,variant,trade_key,rule,side,entry_ts,entry_px,status,
                               net_krw,spec_version,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                            (day, v, "R3|10:00|-1", "R3", -1, day + " 10:00:00", 900.0, "CLOSED", float(n),
                             spec.SPEC_VERSION, "x"))
    con.close()
    rc = sqlite3.connect(reg)
    rc.execute("CREATE TABLE regular_candles(code TEXT, ts TEXT, trade_date TEXT, open REAL, high REAL, low REAL, close REAL)")
    rc.execute("INSERT INTO regular_candles VALUES('10100','2026-10-26 15:44:00','2026-10-26',1000,1000,1000,1000)")
    px = 1000.0
    for day in days:
        g = gaps[day]
        if g is None:
            continue                                          # 미수집일
        o = px * (1 + g / 100.0)
        rc.execute("INSERT INTO regular_candles VALUES('10100',?,?,?,?,?,?)", (day + " 08:45:00", day, o, o, o, o))
        rc.execute("INSERT INTO regular_candles VALUES('10100',?,?,?,?,?,?)", (day + " 15:44:00", day, o, o, o, o))
        px = o
    rc.commit(); rc.close()
    return sd, reg


_D10 = ["2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30", "2026-11-02",
        "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06", "2026-11-09"]


def test_gapsw_picks_by_gap_and_judges(tmp_path):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import shindong_scorecard as SC
    gaps = dict(zip(_D10, [-1.0, 0.3, -0.5, 1.2, -0.49, -2.0, 0.0, 0.8, -0.7, 0.1]))
    main = [-100, 50, -80, 60, 10, -150, 20, 30, -40, 10]
    f2 = [120, -90, 40, -50, -60, 200, -30, -20, 70, -10]
    sd, reg = _gapsw_dbs(tmp_path, gaps, main, f2)
    txt = SC.build(sd, spec.SCORING_START, raw_db=None, reg_db=reg)
    sec = txt[txt.index("GAPSW 합성 줄 판정"):]
    # 갭 ≤ −0.5% 인 날(10-27 · 10-29 · 11-03 · 11-06)만 F2, 경계 −0.49 는 MAIN
    exp = sum(f if gaps[d] <= -0.5 else m for d, m, f in zip(_D10, main, f2))
    assert exp == 120 + 50 + 40 + 60 + 10 + 200 + 20 + 30 + 70 + 10
    assert "| **GAPSW** | 10 | %s |" % format(float(exp), "+,.0f") in sec
    assert "| 2026-11-02 | -0.49% | MAIN |" in sec and "| 2026-10-29 | -0.50% | SHADOW_F2 |" in sec
    assert "판정: **채택 후보" in sec                       # 순손익 +610 > −250 그리고 최악 +10 > −150


def test_gapsw_missing_gap_is_unmeasured(tmp_path):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import shindong_scorecard as SC
    gaps = dict(zip(_D10, [-1.0, None, 0.3] + [0.1] * 7))
    sd, reg = _gapsw_dbs(tmp_path, gaps, [10] * 10, [20] * 10)
    sec = SC.build(sd, spec.SCORING_START, raw_db=None, reg_db=reg)
    sec = sec[sec.index("GAPSW 합성 줄 판정"):]
    assert "갭 미측정 1일(2026-10-28)" in sec
    assert "판정: **대기** — 9/10 측정일" in sec               # 미측정일은 판정 일수에 넣지 않는다
