# -*- coding: utf-8 -*-
"""[MW0602 640차] 상대의 수 — 신동 v3 MAIN·섀도 읽기 · 단위 환산 · 사전등록 판정(BEATS/TRAILS/INVALID_COPY/UNMEASURED).

사전등록: docs/맥점x옵션사다리개선/02_사전등록_AI대MAIN_판정_MW0602-20261020.md
"""
import json
import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import shindong2_rival as RV  # noqa: E402
from strategy.shindong import store, spec  # noqa: E402


def _mk_db(path, day="2026-10-20"):
    con = store.connect(path)
    try:
        with con:
            for v in spec.VARIANTS:
                con.execute("INSERT INTO shindong_day(trade_date,variant,bias,notes,spec_version,updated_at) VALUES(?,?,?,?,?,?)",
                            (day, v, -1, "FLOWC 09:07 매도", spec.SPEC_VERSION, "x"))
            # MAIN: 1건 CLOSED(2계약 합 +1,000,000원 = +10pt/계약) + 1건 OPEN
            con.execute("""INSERT INTO shindong_trades(trade_date,variant,trade_key,rule,side,entry_ts,entry_px,stop_init,stop_now,t1,status,
                           leg1_exit_ts,leg1_exit_px,leg1_reason,leg2_exit_ts,leg2_exit_px,leg2_reason,net_krw,spec_version,updated_at)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (day, "MAIN", "FLOW|09:07|-1", "FLOW", -1, day + " 09:07:00", 871.68, 896.78, 864.1, 859.68, "CLOSED",
                         day + " 09:49:00", 859.68, "TP1", day + " 09:49:00", 859.68, "TP2", 1_000_000.0, spec.SPEC_VERSION, "x"))
            con.execute("""INSERT INTO shindong_trades(trade_date,variant,trade_key,rule,side,entry_ts,entry_px,stop_init,status,net_krw,spec_version,updated_at)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (day, "MAIN", "R60|10:16|-1", "R60", -1, day + " 10:16:00", 852.10, 870.0, "OPEN", 0.0, spec.SPEC_VERSION, "x"))
            # 섀도: V22 CLOSED +300,000 (= +3pt) · BRKC CLOSED −900,000 (= −9pt) · 나머지 거래 없음(day 행만)
            con.execute("""INSERT INTO shindong_trades(trade_date,variant,trade_key,rule,side,entry_ts,entry_px,status,
                           leg1_exit_ts,leg1_exit_px,leg1_reason,net_krw,spec_version,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (day, "SHADOW_V22", "FLOW|09:07|-1", "FLOW", -1, day + " 09:07:00", 871.68, "CLOSED",
                         day + " 10:00:00", 868.68, "TR", 300_000.0, spec.SPEC_VERSION, "x"))
            con.execute("""INSERT INTO shindong_trades(trade_date,variant,trade_key,rule,side,entry_ts,entry_px,status,
                           leg1_exit_ts,leg1_exit_px,leg1_reason,net_krw,spec_version,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (day, "SHADOW_BRKC", "BRK|09:20|+1", "BRK", 1, day + " 09:20:00", 875.0, "CLOSED",
                         day + " 09:40:00", 866.0, "SL", -900_000.0, spec.SPEC_VERSION, "x"))
            # RETRACTED 행은 보이면 안 된다
            con.execute("""INSERT INTO shindong_trades(trade_date,variant,trade_key,rule,side,entry_ts,entry_px,status,net_krw,spec_version,updated_at)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                        (day, "SHADOW_HYBL", "LEAD|11:00|+1", "LEAD", 1, day + " 11:00:00", 860.0, "RETRACTED", 0.0, spec.SPEC_VERSION, "x"))
    finally:
        con.close()


def test_1_unit_conversion_pt_per_contract():
    """2계약 일괄 net_krw → pt/계약. 10/19 실측 1,916,683원 = +19.17pt."""
    assert RV.PT_DIV == spec.PT_VALUE_KRW * spec.LEGS == 100_000
    assert RV.to_pt(1_916_683) == 19.17
    assert RV.to_pt(None) is None


def test_2_read_day_variants_open_eval_and_divergence(tmp_path):
    db = str(tmp_path / "sd.db")
    _mk_db(db)
    r = RV.read_day("2026-10-20", db=db, last_close=850.0)
    assert r["present"] and set(r["variants"]) == set(spec.VARIANTS)
    m = r["main"]
    assert m["n"] == 2 and m["n_closed"] == 1 and m["pnl_pt"] == 10.0 and m["first_side"] == "매도"
    assert m["open"]["entry_t"] == "10:16" and m["open"]["eval_pt"] == pytest.approx(2.10, abs=0.01)   # 매도 852.10 → 850.0
    assert m["trades"][0]["reason_ko"] == "1차/최종" and m["trades"][0]["exit_t"] == "09:49"
    assert r["variants"]["SHADOW_V22"]["pnl_pt"] == 3.0
    assert r["variants"]["SHADOW_BRKC"]["pnl_pt"] == -9.0 and r["variants"]["SHADOW_BRKC"]["first_side"] == "매수"
    assert r["variants"]["SHADOW_HYBL"]["n"] == 0 and r["variants"]["SHADOW_HYBL"]["pnl_pt"] == 0.0   # RETRACTED 제외, day 행 있으니 0
    shorts = {d["short"]: d["diff"] for d in r["divergent"]}
    assert shorts["V22"] == -7.0 and shorts["BRKC"] == -19.0 and "HYBL" in shorts and "FLOWR60" in shorts


def test_3_missing_db_is_unmeasured(tmp_path):
    r = RV.read_day("2026-10-20", db=str(tmp_path / "none.db"))
    assert r["present"] is False and "없음" in r["why"] and r["variants"] == {}
    assert RV.summary_lines(r)[1].startswith("미측정")


def test_4_ai_cost_and_agreement():
    sim = dict(pnl=5.0, trades=[dict(open=False), dict(open=False), dict(open=True)])
    assert RV.ai_cost_pt(sim) == pytest.approx(5.0 - 2 * RV.AI_RT_COST_PT)
    assert RV.ai_cost_pt(dict(pnl=0.0, trades=[])) == 0.0        # 미참여 = 0pt(선택이다)
    assert RV.ai_cost_pt(None) is None
    assert RV.agreement("매수", "매수") == "agree" and RV.agreement("매수", "매도") == "disagree"
    assert RV.agreement(None, "매도") is None and RV.agreement("매수", None) is None


def _rows(n, ai, main, ai_dir="매수", main_dir="매도", vs=None, start=21):
    out = []
    for i in range(n):
        d = "2026-10-%02d" % (start + i) if start + i <= 31 else "2026-11-%02d" % (start + i - 31)
        out.append(dict(date=d, ai_pt=ai[i] if isinstance(ai, list) else ai, main_pt=main[i] if isinstance(main, list) else main,
                        ai_dir=ai_dir, main_dir=main_dir, vs_main=vs, vs_src="recorded" if vs else None))
    return out


def test_5_judge_unmeasured_below_min_days():
    j = RV.judge_window(_rows(10, 1.0, 0.5))
    assert j["verdict"] == "UNMEASURED" and j["n_both"] == 10 and "15" in j["why"]
    assert j["cohort"]["verdict"] == "AI_WINS"           # 반대일 n=10 ≥ 5 이면 코호트는 따로 판정된다


def test_6_judge_invalid_copy_when_agreeing():
    j = RV.judge_window(_rows(20, 2.0, 1.0, ai_dir="매도", main_dir="매도"))
    assert j["agree_rate"] == 1.0 and j["verdict"] == "INVALID_COPY" and j["cohort"]["n"] == 0


def test_7_judge_beats_requires_net_and_worst_day():
    ai = [2.0] * 19 + [-3.0]
    main = [1.0] * 19 + [-5.0]
    j = RV.judge_window(_rows(20, ai, main))
    assert j["verdict"] == "BEATS" and j["ai_worst"] == -3.0 and j["main_worst"] == -5.0
    # 순손익은 이겨도 최악일이 더 나쁘면 TRAILS
    j2 = RV.judge_window(_rows(20, [2.0] * 19 + [-9.0], [1.0] * 19 + [-5.0]))
    assert j2["verdict"] == "TRAILS"


def test_8_recorded_vs_main_overrides_mechanical_and_window_is_since_scoring_start():
    # 기계로는 반대(매수 vs 매도)지만 기록은 abstain → 동의율 분모에서 빠진다
    rows = _rows(20, 1.0, 0.5, vs="abstain")
    j = RV.judge_window(rows)
    assert j["n_dir"] == 0 and j["agree_rate"] is None and j["cohort"]["n"] == 0
    assert j["verdict"] == "BEATS"                      # net 20 > 10 · 최악일 1.0 > 0.5 — 기권은 능가 판정 자체를 막지 않는다
    assert "뒷받침하지 않는다" in j["why"]               # 단 반대일 코호트가 비어 「동의일 덕」 경고가 붙는다
    # 개시일 이전 행은 창에서 제외된다
    pre = _rows(5, 100.0, 0.0, start=10)
    j2 = RV.judge_window(pre + _rows(15, 1.0, 0.5))
    assert j2["n_both"] == 15 and j2["first"] == "2026-10-21" and j2["ai_net"] == 15.0


def test_8b_beats_value_check():
    j = RV.judge_window(_rows(20, 1.0, 0.5, vs="abstain"))
    assert j["verdict"] == "BEATS"


def test_9_learn_rival_block_without_db_is_unmeasured(tmp_path, monkeypatch):
    monkeypatch.setenv("SHINDONG2_SD_DB", str(tmp_path / "none.db"))
    import importlib
    importlib.reload(RV)
    import shindong2_learn as LN
    importlib.reload(LN)
    log = [dict(ts="2026-10-20T08:52:00", variant="live", action="plan", dir="매수", phase="premarket")]
    b = LN.rival_block("2026-10-20", None, dict(pnl=3.0, trades=[dict(exit_t="10:00")]), log)
    assert b["present"] is False and b["main_pt"] is None and b["ai_dir"] == "매수" and b["ai_pt_cost"] == pytest.approx(2.8)
    assert b["vs_main"] is None and b["diff"] is None
    monkeypatch.delenv("SHINDONG2_SD_DB")
    importlib.reload(RV)
    importlib.reload(LN)


def test_10_ladder_build_day_carries_rival(monkeypatch):
    sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))
    import ladder_data as L
    monkeypatch.setattr(L, "rival", lambda day, cs, live: (_ for _ in ()).throw(RuntimeError("boom")))
    d = L.build_day("2099-01-01")
    assert d["rival"]["present"] is False and "boom" in d["rival"]["why"]
    assert any("신동 v3 MAIN" in w for w in d["warnings"])


def test_11_ladder_html_has_rival_panel_and_archive():
    p = os.path.join(ROOT, "tools", "maekjeom_ladder", "ladder.html")
    with open(p, encoding="utf-8") as f:
        h = f.read()
    assert 'id="rivalSec"' in h and 'id="rivalTbl"' in h and "function drawRival" in h and "drawRival();" in h
    assert 'id="sd2Archive"' in h and "(사료) 신동2" in h
    assert "['main','MAIN']" in h and "['sh','섀도']" in h and "--sdm:" in h and "--sds:" in h
    assert "D.rival" in h and "k-sdm" in h
