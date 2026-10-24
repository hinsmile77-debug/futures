# -*- coding: utf-8 -*-
"""[MW0602 657차 · SD-2026-10-26-v4] 신동 V4 — MAIN = v3 + 본전이동 · 본전청산 상한 제외 · 첫 FLOW 역행컷 ·
R60 누적일관성 · ATR14 폴백 · 실주문 X% 수량 · 섀도 리뉴얼(V3 · BE3 · HYBL4 · FLOWR60 · BRKC).

고정하는 불변식:
  ① 규격: 새로 고른 수치가 없다 — 본전 3.0 = 트레일 발동 6.0/2 · 컷 0.4 = 재난손절 0.6 × 2/3. 나머지 v3 값 그대로.
  ② 본전이동: MFE ≥ 3 → 손절 = 진입가 · 그 손절에 닿으면 사유 "BE" · OPEN 이면 stop_now = 진입가(실집행이 이것을 따른다).
  ③ 본전청산은 하루 상한에 세지 않고 방향 금지도 걸지 않는다(같은 방향 재진입).
  ④ 첫 FLOW 역행컷: 첫 거래만 · 본전 전 · MAE ≥ 0.4×ATR → 그 봉 종가 청산 · 사유 SL(그 방향 당일 금지 · 상한 포함).
  ⑤ R60 누적일관성: 2번째 거래부터 누적 FLOWC 와 반대 방향 진입 차단(중립은 진입) · 막힌 분을 남긴다.
  ⑥ ATR14: 08:50 → 재계산 → 이월 → 미확보 = 진입 없음. 고정 pt 폴백 없음.
  ⑦ 실주문 수량: floor(3,000만 × 7% ÷ (0.6 × ATR × 5만)), 최소 1 · 증거금 수량과 min.
  ⑧ 실데이터: 21일(9/21~10/23) 공식 엔진 = 반사실 `v4_compare.json`(거래 단위 · 반올림 폭).
근거: docs/신동거래_V4/신동_V4_구현계획_및_섀도리뉴얼_MW0602-20261024.md · 신동_사전등록_V4_20261024.md
"""
import datetime as dt
import json
import os
import re
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tests"))

import pytest  # noqa: E402

from strategy.shindong import engine, exec_recon, families, live_exec, runner, spec  # noqa: E402
from test_604_shindong_v2 import _flat, _flow, _levels  # noqa: E402


def _L(atr=30.0, **extra):
    L = _levels()
    if atr is not None:
        L["0850"]["atr14"] = atr
    L["0850"].update(extra)
    return L


# ── ① 규격 ────────────────────────────────────────────────────────────────
def test_v4_spec_is_preregistered():
    from config.krx_holidays import is_krx_holiday
    assert spec.SPEC_VERSION == "SD-2026-10-26-v4" and spec.SPEC_TAG == "v4"
    assert spec.SCORING_START == "2026-10-26"
    d0 = dt.date.fromisoformat(spec.SCORING_START)
    assert d0.weekday() < 5 and not is_krx_holiday(d0)
    assert (spec.MAIN_KIND, spec.MAIN_FAMILY) == ("family", "v4")
    # 새로 고른 수치 없음 — 기존 값에서 파생
    assert spec.V4_BE_AT == spec.FLOW_TRAIL[0] / 2.0 == 3.0
    assert spec.V4_FIRST_CUT_ATR == 0.4 and spec.V4_FIRST_CUT_ATR == pytest.approx(spec.FLOW_CAT_STOP_ATR * 2 / 3)
    assert (spec.V4_BE_FREE, spec.V4_R60_AGREE) == (True, True)
    assert (spec.V4_ATR_RECOMPUTE_MIN, spec.V4_ATR_RECOMPUTE_STALE_DAYS, spec.V4_ATR_CARRY_MAX_DAYS) == (5, 10, 5)
    assert (spec.V4_BE_SLIP_REVIEW_PT, spec.V4_BE_SLIP_MIN_N) == (0.8, 20)
    # v3 에서 그대로인 값
    assert (spec.FLOWC_K, spec.FLOWR_WIN_MIN, spec.FLOWR_K) == (300, 60, 150)
    assert (spec.FLOW_CAT_STOP_ATR, spec.FLOW_TRAIL, spec.FLOW_TP, spec.FLOW_MAX_TRADES, spec.FLOW_LAST_ENTRY,
            spec.TIME_EXIT) == (0.6, (6.0, 4.0), 12.0, 3, "14:50", "15:05")
    assert spec.HYB_SL_HALT_MODE == "sticky"
    # 섀도 리뉴얼
    assert spec.VARIANTS == ("MAIN", "SHADOW_V3", "SHADOW_BE3", "SHADOW_HYBL4", "SHADOW_FLOWR60", "SHADOW_BRKC")
    fam = {k: m["family"] for k, m in spec.SHADOW_META}
    assert fam == {"SHADOW_V3": "hybr60", "SHADOW_BE3": "be3", "SHADOW_HYBL4": "hybl4",
                   "SHADOW_FLOWR60": "flowr60", "SHADOW_BRKC": "brkc"}
    assert spec.ROLLBACK_VARIANT == "SHADOW_V3" and spec.ROLLBACK_TO == "v3"
    assert {"SHADOW_V22", "SHADOW_V22S", "SHADOW_HYBL"} <= set(spec.RETIRED_SHADOWS)
    assert not (set(spec.RETIRED_SHADOWS) & set(spec.VARIANTS))
    assert all(v == "2026-10-26" for v in spec.LATE_SHADOW_START.values())
    assert len(spec.VARIANTS) - 1 <= 5


def test_retired_families_still_replay():
    """종료 섀도의 규칙은 family 이름으로 계속 재현된다(사료·재현 테스트)."""
    d = engine.DayFrame(_flat(path={"09:20": (1100.0, 1087.0, 1090.0)}),
                        _flow(lambda k: 300.0 if k >= "09:05" else 0.0))
    for f in ("flowc", "flowc_s", "hybl", "hybr60"):
        assert families.run_family_day(d, _L(), f)["decision"]["family"] == f


# ── ② 본전이동 ─────────────────────────────────────────────────────────────
def _be_day(horizon=None):
    # 09:05 콜−풋 +300 → 매도 1100. 09:10 저가 1096.5(MFE 3.5 → 본전 무장) · 09:11 진입가 아래 머묾 ·
    # 09:12 고가 1100.5 → 본전 청산 1100 (평평한 봉 1100 은 본전가에 닿으므로 09:11 을 아래로 둔다)
    flow = _flow(lambda k: 300.0 if k >= "09:05" else 0.0)
    c = _flat(path={"09:10": (1100.0, 1096.5, 1098.0), "09:11": (1099.0, 1097.5, 1098.5),
                    "09:12": (1100.5, 1098.0, 1100.0)})
    return engine.DayFrame(c, flow, horizon=horizon)


def test_breakeven_exit_at_entry():
    r = families.run_family_day(_be_day(), _L(), "v4")
    t = r["trades"][0]
    assert (t["rule"], t["entry_ts"], t["side"]) == ("FLOW", "09:05", -1)
    assert (t["exit_ts"], t["legs"][0]["reason"], t["legs"][0]["px"], t["legs"][1]["reason"]) == ("09:12", "BE", 1100.0, "BE")
    assert t["be_armed"] and not t["cut"]
    assert t["stop_init"] == pytest.approx(1100.0 + 0.6 * 30.0)
    assert any("본전청산 1건" in n for n in r["decision"]["notes"])


def test_open_trade_stop_moves_to_entry_and_live_follows():
    """라이브 재생(horizon 09:11): 본전 무장 뒤 OPEN 거래의 stop_now = 진입가 → live_exec 가 손절을 진입가로 조인다."""
    r = families.run_family_day(_be_day(horizon="09:11"), _L(), "v4")
    t = r["trades"][0]
    assert t["status"] == "OPEN" and t["stop_now"] == 1100.0
    rec = {"side": -1, "stop": 1118.0}
    acts = live_exec.manage(rec, dict(t, status="OPEN"), dt.datetime(2026, 10, 26, 9, 12))
    assert acts == [("set_stop", 1100.0)]


def test_v3_has_no_breakeven():
    t = families.run_family_day(_be_day(), _L(), "hybr60")["trades"][0]
    assert t["exit_ts"] != "09:12" and t["legs"][0]["reason"] != "BE"


# ── ③ 본전청산 상한 제외 · 방향 금지 없음 ─────────────────────────────────────
def _be_cycles():
    """09:01 부터 3분 주기로 4번: 진입(1100) → 저가 1097(MFE 3) → 고가 1100.5(본전 청산). 이후 평평."""
    path = {}
    for i in range(4):
        m1 = (dt.datetime(2026, 10, 26, 9, 1) + dt.timedelta(minutes=3 * i + 1)).strftime("%H:%M")
        m2 = (dt.datetime(2026, 10, 26, 9, 1) + dt.timedelta(minutes=3 * i + 2)).strftime("%H:%M")
        path[m1] = (1100.0, 1097.0, 1099.0)
        path[m2] = (1100.5, 1099.0, 1100.0)
    return engine.DayFrame(_flat(path=path), {})


def _run_cycles(be_free):
    return families._run_signal(_be_cycles(), lambda k: -1 if k >= "09:01" else 0, "FLOW",
                                lambda side, e: e - side * 18.0, spec.FLOW_TRAIL, None, 3,
                                halt_mode="sticky", be_at=3.0, be_free=be_free)


def test_breakeven_not_counted_and_same_direction_reentry():
    tr = _run_cycles(be_free=True)
    assert [t["entry_ts"] for t in tr] == ["09:01", "09:04", "09:07", "09:10", "09:13"]
    assert [t["legs"][0]["reason"] for t in tr] == ["BE"] * 4 + ["TIME"]
    assert all(t["side"] == -1 for t in tr)                     # 본전 뒤 같은 방향 재진입(방향 금지 없음)
    tr2 = _run_cycles(be_free=False)
    assert [t["entry_ts"] for t in tr2] == ["09:01", "09:04", "09:07"]   # 끄면 종전처럼 3건에서 멈춘다


# ── ④ 첫 FLOW 역행컷 ───────────────────────────────────────────────────────
def _cut_day():
    # 매도 1100(09:05) · 09:07 고가 1113(MAE 13 ≥ 0.4×30=12) 종가 1111 → 컷. 재난손절 1118 은 안 닿는다.
    flow = _flow(lambda k: 300.0 if k >= "09:05" else 0.0)
    return engine.DayFrame(_flat(path={"09:07": (1113.0, 1100.0, 1111.0)}), flow)


def test_first_flow_cut_closes_at_bar_close_and_bans_direction():
    r = families.run_family_day(_cut_day(), _L(), "v4")
    t = r["trades"][0]
    assert (t["exit_ts"], t["legs"][0]["reason"], t["legs"][0]["px"], t["cut"]) == ("09:07", "SL", 1111.0, True)
    assert len(r["trades"]) == 1, "컷 = 손절 취급 → 매도 당일 금지(10:00 R60 매도 신호도 막힌다)"
    notes = r["decision"]["notes"]
    assert any("첫 FLOW 역행컷 발동(09:07" in n for n in notes)
    assert any("매도 당일 금지" in n for n in notes) and any("손절 방향 금지로 막힌 신호" in n for n in notes)


def test_cut_absent_in_v3_and_be3():
    for f in ("hybr60", "be3"):
        t = families.run_family_day(_cut_day(), _L(), f)["trades"][0]
        assert t["exit_ts"] != "09:07" and not t.get("cut"), f


def test_cut_only_first_trade_and_only_before_breakeven():
    path = {"09:02": (1100.0, 1087.0, 1090.0),                  # 첫 거래 익절(12pt)
            "09:12": (1113.0, 1100.0, 1111.0)}                  # 둘째 거래 MAE 13 — 컷 대상 아님
    d = engine.DayFrame(_flat(path=path), {})
    sig = {"09:01": -1}
    sig2 = {"09:10": -1}
    tr = families._run_signal(d, lambda k: sig.get(k, 0), "FLOW", lambda side, e: e - side * 18.0,
                              spec.FLOW_TRAIL, 12.0, 3, halt_mode="sticky",
                              sig_after=lambda k: sig2.get(k, 0), rule_after="R60",
                              be_at=3.0, first_cut_pts=12.0, be_free=True)
    assert [(t["entry_ts"], t["rule"]) for t in tr] == [("09:01", "FLOW"), ("09:10", "R60")]
    assert tr[0]["legs"][0]["reason"] == "TP1"
    assert tr[1]["exit_ts"] != "09:12" and not tr[1]["cut"]
    # 본전 무장(MFE ≥ 3) 뒤에는 역행이 커도 컷이 아니라 본전 손절이다
    d2 = engine.DayFrame(_flat(path={"09:02": (1100.0, 1096.0, 1098.0), "09:03": (1099.0, 1097.0, 1098.0),
                                     "09:04": (1113.0, 1100.0, 1111.0)}), {})
    t = families._run_signal(d2, lambda k: -1 if k == "09:01" else 0, "FLOW", lambda side, e: e - side * 18.0,
                             spec.FLOW_TRAIL, None, 3, be_at=3.0, first_cut_pts=12.0)[0]
    assert (t["exit_ts"], t["legs"][0]["reason"], t["legs"][0]["px"], t["cut"]) == ("09:04", "BE", 1100.0, False)


# ── ⑤ R60 누적일관성 ───────────────────────────────────────────────────────
def test_agree_filter_blocks_opposite_and_allows_neutral():
    d = engine.DayFrame(_flat(path={"09:02": (1100.0, 1087.0, 1090.0)}), {})
    sig = {"09:01": -1}
    after = {"09:10": 1, "09:20": 1}
    cum = {"09:10": -1, "09:20": 0}                             # 09:10 누적 매도(반대) · 09:20 중립
    notes = []
    tr = families._run_signal(d, lambda k: sig.get(k, 0), "FLOW", lambda side, e: e - side * 18.0,
                              spec.FLOW_TRAIL, 12.0, 3, notes=notes, halt_mode="sticky",
                              sig_after=lambda k: after.get(k, 0), rule_after="R60",
                              be_at=3.0, be_free=True, agree=lambda k: cum.get(k, 0))
    assert [(t["entry_ts"], t["side"]) for t in tr] == [("09:01", -1), ("09:20", 1)]
    assert any("누적일관성 차단 — 첫 09:10 · 신호 1분" in n for n in notes)


def test_agree_filter_never_blocks_first_trade():
    d = engine.DayFrame(_flat(), {})
    tr = families._run_signal(d, lambda k: -1 if k == "09:01" else 0, "FLOW", None, None, None, 3,
                              agree=lambda k: 1)
    assert [t["entry_ts"] for t in tr] == ["09:01"]


# ── ⑥ ATR14 ───────────────────────────────────────────────────────────────
def test_v4_no_entry_without_atr_and_no_fixed_fallback():
    d = _be_day()
    r = families.run_family_day(d, _L(atr=None, atr14_v4=None, atr14_v4_src="미확보"), "v4")
    assert r["trades"] == []
    assert any("ATR14 미확보" in n for n in r["decision"]["notes"])
    assert not any("20pt" in n for n in r["decision"]["notes"])           # v4 계열은 20pt 폴백 문구를 남기지 않는다
    # v3(SHADOW_V3)는 규격대로 20pt 폴백으로 거래한다
    r3 = families.run_family_day(d, _L(atr=None), "hybr60")
    assert r3["trades"] and r3["trades"][0]["stop_init"] == 1100.0 + spec.FLOW_CAT_STOP_FALLBACK_PT


def test_v4_fallback_atr_is_used_and_noted():
    r = families.run_family_day(_be_day(), _L(atr=None, atr14_v4=40.0, atr14_v4_src="직전 기록일 2026-10-23 이월"), "v4")
    assert r["trades"][0]["stop_init"] == pytest.approx(1100.0 + 0.6 * 40.0)
    assert any("ATR14 폴백 40.00 — 직전 기록일 2026-10-23 이월" in n for n in r["decision"]["notes"])


def _levels_db(tmp_path, rows):
    p = str(tmp_path / "lv.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE premarket_levels (date TEXT, stage TEXT, atr14 REAL)")
    con.executemany("INSERT INTO premarket_levels VALUES (?,?,?)", rows)
    con.commit()
    con.close()
    return p


def _history(tmp_path, last_day, n=15, name="hist.json"):
    from features.levels import premarket_levels as PL
    d = dt.date.fromisoformat(last_day)
    ss = []
    while len(ss) < n:
        if d.weekday() < 5:
            k = len(ss)
            ss.append(PL.SessionSummary(d=d.isoformat(), o=1000.0, h=1010.0 + k, l=990.0 - k, c=1000.0 + k))
        d -= dt.timedelta(days=1)
    ss.reverse()
    p = str(tmp_path / name)
    json.dump({"summaries": [PL.summary_to_dict(s) for s in ss]}, open(p, "w", encoding="utf-8"))
    return p, ss


def test_resolve_atr14_order(tmp_path, monkeypatch):
    from features.levels import premarket_levels as PL
    monkeypatch.setattr(runner, "_ATR_V4_CACHE", {})
    lv = _levels_db(tmp_path, [("2026-10-22", "0850", 44.6), ("2026-10-23", "0850", 45.7)])
    # ① 08:50
    assert runner.resolve_atr14_v4("2026-10-26", {"0850": {"atr14": 41.0}}, lv) == (41.0, "0850")
    # ② 재계산 — 08:50 산출과 같은 공식(atr_of)
    hp, ss = _history(tmp_path, "2026-10-23")
    v, src = runner.resolve_atr14_v4("2026-10-26", {"0850": {"atr14": None}}, lv, cache_path=hp)
    assert v == pytest.approx(PL.atr_of(ss, len(ss))) and src.startswith("재계산")
    # ③ 이월 — 이력이 낡았으면(마지막 세션이 10일 넘게 전) 재계산하지 않는다
    hp2, _ = _history(tmp_path, "2026-09-30", name="hist_stale.json")
    v, src = runner.resolve_atr14_v4("2026-10-26", {"0850": {"atr14": None}}, lv, cache_path=hp2)
    assert v == 45.7 and src.startswith("직전 기록일 2026-10-23 이월") and "낡음" in src
    # ④ 미확보 — 이력·이월 모두 없음
    lv0 = _levels_db(tmp_path / "x" if (tmp_path / "x").mkdir() is None else tmp_path, [("2026-10-23", "0850", None)])
    v, src = runner.resolve_atr14_v4("2026-10-26", {"0850": {"atr14": None}}, lv0,
                                     cache_path=str(tmp_path / "없음.json"))
    assert v is None and src.startswith("미확보")


def test_attach_atr_feeds_v4_family(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "_ATR_V4_CACHE", {})
    lv = _levels_db(tmp_path, [("2026-10-23", "0850", 40.0)])
    L = _L(atr=None)
    v, src = runner.attach_atr14_v4(L, "2026-10-26", {"0850": {"atr14": None}}, lv)
    assert L["0850"]["atr14_v4"] == v
    if v is not None:
        r = families.run_family_day(_be_day(), L, "v4")
        assert r["trades"][0]["stop_init"] == pytest.approx(1100.0 + 0.6 * v)


# ── ⑦ 실주문 수량 ─────────────────────────────────────────────────────────
def test_risk_qty_rule():
    from config import capital as C
    from config import settings as ST
    assert (ST.SHINDONG_RISK_QTY_ENABLED, ST.SHINDONG_RISK_CAPITAL_KRW, ST.SHINDONG_TRADE_RISK_PCT) == (True, 30_000_000, 0.07)
    assert C.SHINDONG_PT_VALUE_KRW == spec.PT_VALUE_KRW
    q = C.shindong_risk_qty
    assert [q(a) for a in (23.0, 23.3, 23.4, 34.2, 35.0, 35.1, 38.6, 45.7, 120.0)] == [3, 3, 2, 2, 2, 1, 1, 1, 1]
    assert q(None) is None and q(0) is None
    # 계획 수량 = min(최대허용, 장시작 가능, X%) · 증거금 0 은 0 그대로(기각)
    assert C.shindong_planned_qty(3, 3, 2, 1) == 1
    assert C.shindong_planned_qty(3, 3, 2, None) == 3
    assert C.shindong_planned_qty(3, 0, 2, 1) == 0
    st = C.capital_state(policy_krw=15e6, deposit_krw=30e6, price=1050.0, pt_value=50_000, margin_qty=3,
                         configured_qty=2, ui_max_qty=3, day_start_margin_qty=3, risk_qty=1, risk_atr=45.7,
                         risk_atr_src="0850")
    assert (st["planned_qty"], st["effective_qty"], st["risk_qty"]) == (1, 1, 1)
    assert "X%위험 1계약(ATR 45.7)" in st["reasons"]
    assert "장시작 증거금 기준 확대 2→3" in st["reasons"]          # 증거금 몫은 X% 와 따로 말한다


def test_risk_qty_disabled(monkeypatch):
    from config import capital as C
    monkeypatch.setattr(C, "SHINDONG_RISK_QTY_ENABLED", False)
    assert C.shindong_risk_qty(30.0) is None


def test_main_wires_risk_qty_and_atr_state():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    init = src[src.index("self._sd_day = None"):src.index("self._sd_day = None") + 600]
    assert "self._sd_atr_v4 = (None, None)" in init                      # 계측 4원칙 ④ — __init__ 명시 초기화
    body = src[src.index("def _shindong_live_qty(self)"):src.index("def _principal_live_qty")]
    assert "_capital_sd_risk_qty(self._sd_atr_v4[0])" in body
    run = src[src.index("def _run_shindong(self"):src.index("def _sd_exec_load")]
    assert run.index('payload.get("atr14_v4")') < run.index("self._shindong_exec_step(payload, now)")
    assert "risk_qty=_capital_sd_risk_qty(self._sd_atr_v4[0])" in src


# ── 섀도 계열 ─────────────────────────────────────────────────────────────
def test_hybl4_uses_lead_signal_with_v4_exits():
    flow = _flow(lambda k: (300.0 + 5 * ((int(k[:2]) - 9) * 60 + int(k[3:]) - 5)) if k >= "09:05" else 0.0)
    d = engine.DayFrame(_flat(path={"09:20": (1100.0, 1087.0, 1090.0)}), flow)
    r = families.run_family_day(d, _L(), "hybl4")
    assert r["trades"][0]["rule"] == "FLOW" and all(t["rule"] == "LEAD" for t in r["trades"][1:])
    assert any("HYBL 외국인 선물 원천 없음" in n for n in r["decision"]["notes"])
    rb = families.run_family_day(_be_day(), _L(), "hybl4")
    assert rb["trades"][0]["legs"][0]["reason"] == "BE"                  # 청산은 V4


def test_be_exit_slips():
    rc = {"items": [
        {"kind": "MATCH", "key": "R60|10:00|-1", "real": {"legs": [("10:05", 1100.3, "신동미러:BE")]},
         "replay": {"side": -1, "entry_px": 1100.0, "legs": [("10:05", 1100.0, "BE"), ("10:05", 1100.0, "BE")]}},
        {"kind": "MATCH", "key": "FLOW|09:05|-1", "real": {"legs": [("09:20", 1088.0, "x")]},
         "replay": {"side": -1, "entry_px": 1100.0, "legs": [("09:20", 1088.0, "TP1")]}},
        {"kind": "REPLAY_ONLY", "key": "z", "real": None, "replay": {"side": 1, "entry_px": 1.0, "legs": [("", 1.0, "BE")]}},
    ]}
    sl = exec_recon.be_exit_slips(rc)
    assert len(sl) == 1 and sl[0]["slip_pt"] == pytest.approx(0.3)      # 매도 본전 1100 → 실청산 1100.3 = 0.3 불리
    assert exec_recon.be_exit_slips(None) is None


# ── ⑧ 실데이터 재현 ───────────────────────────────────────────────────────
_DBS = [os.path.join(_ROOT, "data", "db", p) for p in ("raw_data.db", "option_flow.db", "premarket_levels.db")]
_REF = os.path.join(_ROOT, "docs", "신동거래_V4", "V22_V3_반사실_20261024", "v4_compare.json")


@pytest.mark.skipif(not (all(os.path.exists(p) for p in _DBS) and os.path.exists(_REF)),
                    reason="로컬 DB·반사실 없음(이 PC 의 런타임 산출물)")
def test_v4_engine_reproduces_counterfactual_21days():
    from strategy.shindong.calendar import select_flow_product
    ref = json.load(open(_REF, encoding="utf-8"))
    db = os.path.join(_ROOT, "data", "db") + os.sep
    tot = {"V3": 0.0, "V4": 0.0}
    for day in sorted(ref["V4"]):
        prod, _, _ = select_flow_product(dt.date.fromisoformat(day))
        cd, fl, lr = runner.load_inputs(day, prod, db + "raw_data.db", db + "option_flow.db", db + "premarket_levels.db")
        if not cd or "0850" not in lr:
            pytest.skip("%s 봉·맥점 없음 — 이 PC DB 범위 밖" % day)
        d, L = engine.DayFrame(cd, fl, fx=runner.load_fx(day, db + "raw_data.db")), engine.prepare_levels(lr)
        for lab, fam, tol in (("V3", "hybr60", 1e-6), ("V4", "v4", 0.005 + 1e-9)):
            got = [engine.trade_net(t) / 2 / spec.PT_VALUE_KRW for t in families.run_family_day(d, L, fam)["trades"]
                   if t["status"] == "CLOSED"]
            want = ref[lab][day]
            assert len(got) == len(want) and all(abs(a - b) <= tol for a, b in zip(got, want)), (day, lab, got, want)
            tot[lab] += sum(engine.trade_net(t) for t in families.run_family_day(d, L, fam)["trades"]
                            if t["status"] == "CLOSED")
    # MW0602 DB 실측(2026-10-24). 반사실 v4_compare: V3 +2,242.6만 · V4 +2,671.0만(가상 2계약)
    assert round(tot["V3"]) == pytest.approx(22425662, abs=2)
    assert round(tot["V4"]) == pytest.approx(26711348, abs=2)
