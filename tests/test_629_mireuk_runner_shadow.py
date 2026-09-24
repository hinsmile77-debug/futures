# -*- coding: utf-8 -*-
"""[MW0601 629차] 신동 조건부 러너 섀도 — 사전등록 값 · 조건 · 러너 계산 · 판정 · 배선.

무엇을 고정하나
---------------
A. 사전등록 값이 조용히 바뀌지 않는다(바뀌면 RUNNER_VERSION·사전등록 문서 개정을 강제).
B. 조건 — 흐름 미수집은 「불충족」이 아니라 **미측정**(cond_met NULL). 방향 반대·보류·TP1
   미도달은 실제와 같다(차이 0).
C. 러너 — TP1 레그는 실제 그대로, **TP1 이후** 비-TP1 레그만 교체. 같은 봉 본전·목표 →
   본전(보수적). CREON 요율.
D. 판정 — WAITING / INSUFFICIENT(표본 없음 ≠ 합격) / PASS / FAIL, 상위 3일 제외 조건.
E. 배선 — 장후 마감에서 부르고, 주문·`trades` 쓰기를 하지 않는다(절대원칙 §6).

실행:
    conda run -n py37_32 python -m pytest tests/test_629_mireuk_runner_shadow.py -q
"""
import json
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

from strategy.shindong import engine as E  # noqa: E402
from strategy.shindong import mireuk_runner as R  # noqa: E402


# ── A ────────────────────────────────────────────────────────────────────
def test_preregistered_values():
    """🔴 바꾸려면 사전등록 문서 §5 절차부터 — 이 테스트를 먼저 고치지 말 것."""
    assert R.RUNNER_VERSION == "SDR-2026-09-24-v1"
    assert R.COMMISSION_RATE == 0.000019          # CREON 편도(사용자 지시)
    assert R.SCORING_START == "2026-09-28"
    assert R.JUDGE_AFTER_FLOW_DAYS == 20
    assert R.MIN_APPLIED == 10
    assert R.EXCLUDE_TOP_DAYS == 3
    assert R.WORST_DAY_TOL_RATIO == 0.5
    assert R.WORST_DAY_TOL_MIN_KRW == 100000
    assert R.TIME_EXIT == "15:05"


def test_creon_rate_matches_constants():
    from config.constants import BROKER_CHANNEL_SPECS
    assert R.COMMISSION_RATE == BROKER_CHANNEL_SPECS["CREON"]["one_way_commission_rate"]


# ── 합성 데이터 ───────────────────────────────────────────────────────────
def _levels():
    row = {"struct_up": json.dumps([[110.0, ["x"]]]), "struct_down": json.dumps([[90.0, ["y"]]]),
           "dist_high": 104.0, "dist_low": 96.0, "high80_hi": 112.0, "low80_lo": 88.0}
    return E.prepare_levels({"0850": row})


def _frame(bars):
    """bars: {HH:MM: (o,h,l,c)}"""
    return E.DayFrame(bars, {})


def _leg(entry, exit_px, qty, reason, exit_ts, side=1, ets="2026-10-05 10:00:02"):
    return {"entry_ts": ets, "direction": "LONG" if side > 0 else "SHORT",
            "entry_price": entry, "exit_price": exit_px, "quantity": qty,
            "gross_pnl_krw": side * (exit_px - entry) * 50000 * qty,
            "exit_ts": exit_ts, "exit_reason": reason}


def _pos(legs, side=1, e=100.0):
    return {"entry_ts": legs[0]["entry_ts"], "side": side, "entry_px": e, "legs": legs,
            "open": False}


DEC_UP = {"pm_sp": -80.0, "bias": 1, "r2": "NONE"}


# ── B ────────────────────────────────────────────────────────────────────
def test_flow_unmeasured_is_null_not_false():
    p = _pos([_leg(100, 101, 1, "TP1 부분청산 33%", "2026-10-05 10:01:00"),
              _leg(100, 100, 1, "하드스톱", "2026-10-05 10:03:00")])
    r = R.evaluate_position(p, None, None, {"pm_sp": None, "bias": 0, "r2": None})
    assert r["cond_met"] is None and r["sd_bias"] is None
    assert r["applied"] == 0 and r["diff_krw"] == 0.0
    assert "미측정" in r["skip_reason"]


@pytest.mark.parametrize("dec,why", [
    ({"pm_sp": 80.0, "bias": -1, "r2": None}, "반대"),
    ({"pm_sp": 10.0, "bias": 0, "r2": None}, "보류"),
])
def test_condition_not_met_equals_actual(dec, why):
    p = _pos([_leg(100, 101, 1, "TP1 부분청산 33%", "2026-10-05 10:01:00"),
              _leg(100, 100, 1, "하드스톱", "2026-10-05 10:03:00")])
    r = R.evaluate_position(p, _frame({"10:02": (100, 101, 99.5, 100.5)}), _levels(), dec)
    assert r["applied"] == 0 and r["shadow_net_krw"] == r["act_net_krw"]
    assert why in r["skip_reason"]


def test_no_tp1_equals_actual():
    p = _pos([_leg(100, 98.5, 2, "하드스톱(틱)", "2026-10-05 10:03:00")])
    r = R.evaluate_position(p, _frame({"10:02": (100, 101, 98, 98.5)}), _levels(), DEC_UP)
    assert r["cond_met"] == 1 and r["applied"] == 0 and r["skip_reason"] == "TP1 미도달"


# ── C ────────────────────────────────────────────────────────────────────
def test_runner_hits_t2_and_keeps_tp1_actual():
    # 매수 100, TP1 101 (10:01), 나머지 1계약 실제는 100.4 청산. 신동 T2 = 가장 먼 구조맥점 110 − 0.5
    tp1 = _leg(100, 101, 1, "TP1 부분청산 33%", "2026-10-05 10:01:30")
    rest = _leg(100, 100.4, 1, "TP2(전량)", "2026-10-05 10:04:00")
    bars = {"10:02": (101, 103, 100.5, 102.5), "10:03": (102.5, 109.8, 102, 109.6)}
    r = R.evaluate_position(_pos([tp1, rest]), _frame(bars), _levels(), DEC_UP)
    assert r["applied"] == 1 and r["runner_start"] == "10:02"
    assert r["t2"] == pytest.approx(109.5)
    assert r["runner_reason"] == "TP2" and r["runner_exit_ts"] == "10:03"
    exp_runner = (109.5 - 100) * 50000 - (100 + 109.5) * 50000 * R.COMMISSION_RATE   # 지정가 — 슬리피지 없음
    exp = R.act_leg_net(tp1) + exp_runner
    assert r["shadow_net_krw"] == pytest.approx(exp)
    assert r["diff_krw"] == pytest.approx(exp - r["act_net_krw"])


def test_same_bar_be_and_target_is_be():
    tp1 = _leg(100, 101, 1, "TP1 부분청산 33%", "2026-10-05 10:01:30")
    rest = _leg(100, 101.5, 1, "TP2(전량)", "2026-10-05 10:04:00")
    bars = {"10:02": (101, 111, 99.9, 105)}          # 본전(100)과 목표(109.5) 모두 닿음
    r = R.evaluate_position(_pos([tp1, rest]), _frame(bars), _levels(), DEC_UP)
    assert r["runner_reason"] == "BE" and r["runner_exit_px"] == 100


def test_time_exit_at_1505_and_market_slip():
    tp1 = _leg(100, 101, 1, "TP1 부분청산 33%", "2026-10-05 14:50:30")
    rest = _leg(100, 101, 1, "TP2(전량)", "2026-10-05 14:52:00")
    bars = {"14:51": (101, 102, 100.5, 101.5), "15:05": (101.5, 102, 101, 101.8),
            "15:06": (101.8, 120, 101, 119)}         # 15:05 뒤 봉은 보지 않는다
    r = R.evaluate_position(_pos([tp1, rest]), _frame(bars), _levels(), DEC_UP)
    assert r["runner_reason"] == "TIME" and r["runner_exit_ts"] == "15:05"
    runner = R.sim_leg_net(1, 100, 101.8, 1, True)
    assert runner == pytest.approx(1.8 * 50000 - 201.8 * 50000 * R.COMMISSION_RATE - 0.02 * 50000)


def test_legs_closed_before_tp1_stay_actual():
    early = _leg(100, 99.2, 1, "손절1차 조기축소", "2026-10-05 10:00:40")
    tp1 = _leg(100, 101, 1, "TP1 부분청산 33%", "2026-10-05 10:01:30")
    rest = _leg(100, 100.0, 1, "하드스톱", "2026-10-05 10:05:00")
    bars = {"10:02": (101, 110, 100.5, 109.8)}
    r = R.evaluate_position(_pos([early, tp1, rest]), _frame(bars), _levels(), DEC_UP)
    assert r["runner_qty"] == 1
    exp = R.act_leg_net(early) + R.act_leg_net(tp1) + R.sim_leg_net(1, 100, 109.5, 1, False)
    assert r["shadow_net_krw"] == pytest.approx(exp)


# ── D ────────────────────────────────────────────────────────────────────
def _seed(tmp_path, n_days, rows):
    from strategy.shindong import store
    db = str(tmp_path / "sd.db")
    con = store.connect(db)
    with con:
        for i in range(n_days):
            con.execute("INSERT INTO shindong_day(trade_date,variant,pm_sp,bias,updated_at) "
                        "VALUES(?, 'MAIN', 60, -1, 'x')", ("2026-10-%02d" % (i + 1),))
        con.execute("INSERT INTO shindong_day(trade_date,variant,pm_sp,bias,updated_at) "
                    "VALUES('2026-09-23','MAIN',60,-1,'x')")       # 채점 시작 전 — 제외
    con.close()
    recs = []
    for k, (d, act, sh, ap) in enumerate(rows):
        recs.append({c: None for c in ["sd_pm_sp", "sd_bias", "sd_r2", "cond_met", "skip_reason",
                                       "tp1_exit_ts", "runner_start", "runner_qty", "t2",
                                       "runner_exit_ts", "runner_exit_px", "runner_reason",
                                       "sd_hold_side", "flow_trend", "filt_b_pass",
                                       "filt_b_net_krw"]})
        recs[-1].update(trade_date=d, entry_ts="%s 10:%02d:00" % (d, k % 60), side=1,
                        entry_px=100.0, qty=1, applied=ap, act_net_krw=act,
                        shadow_net_krw=sh, diff_krw=sh - act)
    R.save(db, recs, source="backfill")
    return db


def test_verdict_waiting_before_20_flow_days(tmp_path):
    db = _seed(tmp_path, 19, [("2026-10-01", 0, 100, 1)])
    assert R.verdict(db)["status"] == "WAITING"


def test_verdict_insufficient_is_not_pass(tmp_path):
    rows = [("2026-10-%02d" % (i + 1), 0, 50000, 1) for i in range(5)]
    db = _seed(tmp_path, 20, rows)
    v = R.verdict(db)
    assert v["status"] == "INSUFFICIENT" and v["applied"] == 5


def test_verdict_fail_when_gain_is_only_top3_days(tmp_path):
    # 3일 대박(+100만) + 나머지 12일 −5만씩 → 누적은 양수지만 상위 3일 제외 음수 → FAIL
    rows = [("2026-10-%02d" % (i + 1), 0, 1000000, 1) for i in range(3)]
    rows += [("2026-10-%02d" % (i + 4), 0, -50000, 1) for i in range(12)]
    v = R.verdict(_seed(tmp_path, 20, rows))
    assert v["c1_total_pos"] and not v["c2_ex_top_nonneg"] and v["status"] == "FAIL"


def test_verdict_pass(tmp_path):
    rows = [("2026-10-%02d" % (i + 1), -20000, 10000, 1) for i in range(12)]
    v = R.verdict(_seed(tmp_path, 20, rows))
    assert v["status"] == "PASS", v


def test_verdict_ignores_days_before_scoring_start(tmp_path):
    rows = [("2026-09-23", 0, 9999999, 1)] + [("2026-10-%02d" % (i + 1), 0, 0, 1) for i in range(10)]
    v = R.verdict(_seed(tmp_path, 20, rows))
    assert v["diff_krw"] == 0 and v["positions"] == 10


# ── E ────────────────────────────────────────────────────────────────────
def test_wired_in_daily_close_and_guarded():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("    def daily_close(self):")
    j = src.index("\n    def ", i + 10)
    body = src[i:j]
    assert "mireuk_runner" in body and "SHINDONG_RUNNER_SHADOW_ENABLED" in body
    k = body.index("mireuk_runner")
    assert "except Exception" in body[k:k + 2500]      # 보조 기록이 마감을 깨지 않는다


def test_module_never_writes_trades_or_orders():
    src = open(os.path.join(_ROOT, "strategy", "shindong", "mireuk_runner.py"),
               encoding="utf-8").read()
    assert not re.search(r"(INSERT|UPDATE|DELETE)[^\n]*\btrades\b", src)
    assert "mode=ro" in src                              # trades.db 는 읽기전용으로 연다
    for bad in ("send_order", "SendOrder", "place_order", "order_manager", "cybos"):
        assert bad not in src


def test_settings_flag():
    import config.settings as st
    assert st.SHINDONG_RUNNER_SHADOW_ENABLED is True


# ── 로컬 DB 재현(있을 때만) ─────────────────────────────────────────────
@pytest.mark.skipif(not os.path.exists(os.path.join(_ROOT, "data", "db", "trades.db")),
                    reason="로컬 DB 없음")
def test_local_20260923_reproduces(tmp_path):
    import config.settings as st
    flow = st.WEEKLY_OPTION_FLOW_DB if os.path.isabs(st.WEEKLY_OPTION_FLOW_DB) \
        else os.path.join(_ROOT, st.WEEKLY_OPTION_FLOW_DB)
    if not os.path.exists(flow):
        pytest.skip("흐름 DB 없음")
    res = R.run_for_date("2026-09-23", st.TRADES_DB, st.RAW_DATA_DB, flow,
                         st.PREMARKET_LEVELS_DB, str(tmp_path / "sd.db"), source="backfill")
    if res["n"] != 1:
        pytest.skip("이 PC 의 9/23 포지션 구성이 다름")
    r = res["records"][0]
    assert r["sd_bias"] == -1 and r["applied"] == 1 and r["runner_reason"] == "BE"
    assert round(r["act_net_krw"]) == 23748 and round(r["shadow_net_krw"]) == 22748


# ── F. [629차 후속] 진입 필터 B — 신동 동방향 보유 중일 때만 진입 ────────────
def test_filter_preregistered_values():
    assert R.FILTER_VERSION == "SDF-2026-09-24-v1"
    assert R.FILTER_MIN_EXCLUDED == 10


def test_hold_side_no_lookahead_and_exit_minute_inclusive():
    trs = [{"entry_ts": "09:33", "exit_ts": "14:26", "side": -1}]
    assert R.sd_hold_side_at(trs, "09:33") == 0        # 같은 분 = 신동 진입봉 종가 전 → 모른다
    assert R.sd_hold_side_at(trs, "09:34") == -1
    assert R.sd_hold_side_at(trs, "14:26") == -1       # 청산은 봉 안 — 아직 보유
    assert R.sd_hold_side_at(trs, "14:27") == 0
    assert R.sd_hold_side_at([{"entry_ts": "10:00", "exit_ts": None, "side": 1}], "13:00") == 1


def test_filter_b_pass_and_exclude():
    p = _pos([_leg(100, 99, 1, "하드스톱", "2026-10-05 10:03:00")])
    same = R.evaluate_position(p, None, None, DEC_UP,
                               [{"entry_ts": "09:40", "exit_ts": "11:00", "side": 1}])
    assert same["filt_b_pass"] == 1 and same["filt_b_net_krw"] == same["act_net_krw"]
    opp = R.evaluate_position(p, None, None, DEC_UP,
                              [{"entry_ts": "09:40", "exit_ts": "11:00", "side": -1}])
    assert opp["filt_b_pass"] == 0 and opp["filt_b_net_krw"] == 0.0 and opp["sd_hold_side"] == -1
    flat = R.evaluate_position(p, None, None, DEC_UP, [])
    assert flat["filt_b_pass"] == 0 and flat["sd_hold_side"] == 0      # 무포지션 = 진입 안 함


def test_filter_b_unmeasured_without_flow():
    p = _pos([_leg(100, 99, 1, "하드스톱", "2026-10-05 10:03:00")])
    r = R.evaluate_position(p, None, None, None, None)
    assert r["filt_b_pass"] is None and r["filt_b_net_krw"] is None and r["sd_hold_side"] is None


def _seed_b(tmp_path, n_days, rows):
    """rows: (date, act, pass)"""
    db = _seed(tmp_path, n_days, [(d, a, a, 0) for d, a, _ in rows])
    con = R.connect(db)
    with con:
        for k, (d, a, ps) in enumerate(rows):
            con.execute("UPDATE shindong_mireuk_runner SET filt_b_pass=?, filt_b_net_krw=? "
                        "WHERE entry_ts=?", (ps, a if ps else 0.0, "%s 10:%02d:00" % (d, k % 60)))
    con.close()
    return db


def test_filter_b_insufficient_when_few_excluded(tmp_path):
    rows = [("2026-10-%02d" % (i + 1), -30000, 0) for i in range(5)]
    v = R.verdict_filter_b(_seed_b(tmp_path, 20, rows))
    assert v["status"] == "INSUFFICIENT" and v["excluded"] == 5


def test_filter_b_pass_when_it_drops_losers(tmp_path):
    rows = [("2026-10-%02d" % (i + 1), -30000, 0) for i in range(12)]
    rows += [("2026-10-%02d" % (i + 13), 20000, 1) for i in range(6)]
    v = R.verdict_filter_b(_seed_b(tmp_path, 20, rows))
    assert v["status"] == "PASS", v
    assert v["diff_krw"] == pytest.approx(12 * 30000)


def test_filter_b_fail_when_it_drops_winners(tmp_path):
    rows = [("2026-10-%02d" % (i + 1), 40000, 0) for i in range(12)]
    v = R.verdict_filter_b(_seed_b(tmp_path, 20, rows))
    assert v["status"] == "FAIL" and not v["c1_total_pos"]


def test_migration_adds_filter_columns_to_old_table(tmp_path):
    import sqlite3
    db = str(tmp_path / "old.db")
    con = sqlite3.connect(db)
    old = R._SCHEMA
    for col, _t in R._ADDED_COLS:
        old = re.sub(r"\n\s*%s\s+[A-Z]+,[^\n]*" % col, "", old)
    con.execute(old)
    con.close()
    con = R.connect(db)
    cols = {r[1] for r in con.execute("PRAGMA table_info(shindong_mireuk_runner)")}
    con.close()
    assert {c for c, _ in R._ADDED_COLS} <= cols


@pytest.mark.skipif(not os.path.exists(os.path.join(_ROOT, "data", "db", "trades.db")),
                    reason="로컬 DB 없음")
def test_local_20260922_filter_b(tmp_path):
    import config.settings as st
    flow = st.WEEKLY_OPTION_FLOW_DB if os.path.isabs(st.WEEKLY_OPTION_FLOW_DB) \
        else os.path.join(_ROOT, st.WEEKLY_OPTION_FLOW_DB)
    if not os.path.exists(flow):
        pytest.skip("흐름 DB 없음")
    res = R.run_for_date("2026-09-22", st.TRADES_DB, st.RAW_DATA_DB, flow,
                         st.PREMARKET_LEVELS_DB, str(tmp_path / "sd.db"), source="backfill")
    if res["n"] != 2:
        pytest.skip("이 PC 의 9/22 포지션 구성이 다름")
    got = {r["entry_ts"][11:16]: (r["sd_hold_side"], r["filt_b_pass"]) for r in res["records"]}
    assert got == {"11:02": (-1, 0), "13:16": (-1, 1)}      # 신동 R3 매도 보유 09:33–14:26
