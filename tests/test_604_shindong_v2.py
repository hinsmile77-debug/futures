# -*- coding: utf-8 -*-
"""[MW0602 604차] 신동 v2 — MAIN = FLOWC · 섀도 V1/V1X4/FLOWF/BRKC · 되돌림 판정 · 종료 섀도.

무엇을 고정하나
---------------
A. 사전등록 값(`docs/신동거래_V2/신동_사전등록_V2_20260930.md`) — 바뀌면 v3 다.
B. v1 상수 무변경 — SHADOW_V1 이 v1 그대로여야 되돌림 판정이 뜻을 가진다.
C. families — 합성 데이터 재현값(FLOWC 익절·트레일·시간청산 · FLOWF 순방향 · BRKC 방향일/보류일).
D. runner.compute 분기 · daily_report · scorecard(되돌림 · 레거시 R3 · FLOWC↔FLOWF 대조).
E. 엔진의 v1 시대 이름(SHADOW_X4NF)은 계속 알아듣는다(재현 테스트 보호).

실행:
    python -m pytest tests/test_604_shindong_v2.py -q
"""
import datetime as dt
import importlib.util
import json
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from strategy.shindong import engine, families, runner, spec, store  # noqa: E402

DAY = "2026-10-01"


def _scorecard():
    sp = importlib.util.spec_from_file_location(
        "shindong_scorecard", os.path.join(_ROOT, "scripts", "shindong_scorecard.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ── A. 사전등록 값 ────────────────────────────────────────────────────────
def test_v2_spec_is_preregistered():
    assert spec.SPEC_VERSION == "SD-2026-09-30-v2.1"                 # v2.1 = 재난 손절 사전 정정(채점 전)
    assert (spec.FLOW_CAT_STOP_ATR, spec.FLOW_CAT_STOP_FALLBACK_PT, spec.FLOW_CAT_STOP_HALT_DAY) == (0.6, 20.0, True)
    assert spec.V1_SPEC_VERSION == "SD-2026-09-24-v1"
    assert (spec.SCORING_START, spec.V1_SCORING_START) == ("2026-10-01", "2026-09-28")
    assert (spec.MAIN_KIND, spec.MAIN_FAMILY) == ("family", "flowc")
    assert (spec.FLOW_BASE, spec.FLOWC_K, spec.FLOW_TRAIL, spec.FLOW_TP, spec.FLOW_MAX_TRADES, spec.FLOW_LAST_ENTRY) == \
        ("09:00", 300, (6.0, 4.0), 12.0, 3, "14:50")
    assert spec.FLOWF_K == 800
    assert (spec.BRK_STOP_BUF, spec.BRK_TRAIL, spec.BRK_TP, spec.BRK_MAX_TRADES) == (2.0, (6.0, 3.0), 8.0, 5)
    assert spec.JUDGE_AFTER_DAYS == 20
    assert spec.VARIANTS == ("MAIN", "SHADOW_V1", "SHADOW_V1X4", "SHADOW_FLOWF", "SHADOW_BRKC")
    assert all(v == spec.SCORING_START for v in spec.LATE_SHADOW_START.values())
    assert set(spec.RETIRED_SHADOWS) == {"SHADOW_E2F2", "SHADOW_X4NF", "SHADOW_TR44", "SHADOW_X4NFA"}
    assert not (set(spec.RETIRED_SHADOWS) & set(spec.VARIANTS))
    assert len(spec.VARIANTS) - 1 <= 5                       # 상시 섀도 5개 상한


def test_v1_constants_untouched():
    assert (spec.BIAS_MIN, spec.CONF_MIN, spec.CONF_END, spec.REV_MIN, spec.REV_WIN_MIN) == (50, 50, "09:10", 50, 10)
    assert (spec.TOUCH_NEAR, spec.TOUCH_FAR, spec.LV_STOP_BUF, spec.EXT_STOP_BUF) == (1.0, 1.5, 1.5, 0.5)
    assert (spec.T1_MIN_DIST, spec.TP_BUF, spec.OR_STOP_BUF) == (2.0, 0.5, 1.0)
    assert (spec.R3_START, spec.NEW_ENTRY_END, spec.TIME_EXIT) == ("09:30", "14:30", "15:05")
    assert (spec.R3_KILL_AFTER_DAYS, spec.R3_KILL_NET_MAX, spec.R3_KILL_WINRATE_MAX) == (10, 0, 0.35)


# ── C. families ──────────────────────────────────────────────────────────
def _minutes(a="08:50", b="15:08"):
    t = dt.datetime(2026, 10, 1, int(a[:2]), int(a[3:]))
    out = []
    while t.strftime("%H:%M") <= b:
        out.append(t.strftime("%H:%M"))
        t += dt.timedelta(minutes=1)
    return out


def _flat(px=1100.0, path=None):
    """평평한 봉. path: {HH:MM: (h, l, c)} 로 특정 분만 덮어쓴다."""
    c = {}
    for k in _minutes():
        c[k] = (px, px, px, px)
    for k, (h, l, cl) in (path or {}).items():
        c[k] = (cl, h, l, cl)
    return c


def _levels(struct=(1100.0,)):
    lv = {"0850": {"struct_up": "[]", "struct_down": json.dumps([[x, ["a"]] for x in struct]),
                   "dist_low": 1080.0, "dist_high": 1120.0, "low80_lo": 1070.0, "high80_hi": 1130.0}}
    return engine.prepare_levels(lv)


def _flow(sp_by_min, pre=0.0):
    """콜−풋 = sp (풋 0 고정). 08:59 는 pre."""
    f = {"08:59": (pre, 0.0)}
    for k in _minutes("09:00"):
        f[k] = (sp_by_min(k), 0.0)
    return f


def test_flowc_sell_then_take_profit():
    # 09:05 콜−풋 +300 → 매도 1100 · 09:20 저가 1087 → 익절 1088 (12pt)
    flow = _flow(lambda k: 300.0 if k >= "09:05" else 0.0)
    d = engine.DayFrame(_flat(path={"09:20": (1100.0, 1087.0, 1090.0)}), flow)
    r = families.run_family_day(d, _levels(), "flowc")
    assert [(t["entry_ts"], t["side"], t["exit_ts"], t["legs"][0]["reason"], t["legs"][1]["reason"])
            for t in r["trades"]][0] == ("09:05", -1, "09:20", "TP1", "TP2")
    t = r["trades"][0]
    # [v2.1] 정상 손절은 없지만 재난 손절(폴백 20pt — _levels() 에 atr14 없음)이 stop_init 에 실린다
    assert t["rule"] == "FLOW" and t["stop_init"] == 1100.0 + spec.FLOW_CAT_STOP_FALLBACK_PT and t["t1"] == 1088.0
    assert engine.trade_net(t) == pytest.approx(2 * engine.leg_net(-1, 1100.0, 1088.0, False)[1])


def test_flowc_trail_and_time_exit_and_max_trades():
    # 매도 1100 · 09:10 저가 1093(7pt 유리 → 트레일 손절 1097) · 09:12 고가 1097 → TR 청산 1097
    flow = _flow(lambda k: 300.0 if k >= "09:05" else 0.0)
    # 09:11 은 1094 근처에 머물고(트레일 1097 미접촉) 09:12 고가 1097.5 → TR 청산 1097
    d = engine.DayFrame(_flat(path={"09:10": (1100.0, 1093.0, 1094.0), "09:11": (1095.0, 1093.5, 1094.0),
                                    "09:12": (1097.5, 1094.0, 1095.0)}), flow)
    r = families.run_family_day(d, _levels(), "flowc")
    t = r["trades"][0]
    assert (t["exit_ts"], t["legs"][0]["reason"], t["legs"][0]["px"]) == ("09:12", "TR", 1097.0)
    # 그 다음 분부터 신호가 살아 있으면 재진입 — 평평한 봉이라 두 번째 거래는 15:05 시간 청산까지 간다(3회 상한 안)
    assert [x["entry_ts"] for x in r["trades"]] == ["09:05", "09:13"]
    assert r["trades"][-1]["legs"][0]["reason"] == "TIME" and r["trades"][-1]["exit_ts"] == "15:05"


def test_flowc_no_entry_after_last_entry_minute():
    flow = _flow(lambda k: 300.0 if k >= "14:51" else 0.0)
    d = engine.DayFrame(_flat(), flow)
    assert families.run_family_day(d, _levels(), "flowc")["trades"] == []


def test_flowc_unmeasured_when_no_flow():
    d = engine.DayFrame(_flat(), {})
    r = families.run_family_day(d, _levels(), "flowc")
    assert r["trades"] == [] and any("미측정" in n for n in r["decision"]["notes"])


def test_flowf_follows_foreign_sign_and_is_unmeasured_without_fx():
    fx = {k: (-800.0 if k >= "09:05" else 0.0) for k in _minutes("09:02")}   # 외국인 순매도 −800 → 매도
    d = engine.DayFrame(_flat(path={"09:30": (1100.0, 1087.0, 1090.0)}), _flow(lambda k: 0.0), fx=fx)
    r = families.run_family_day(d, _levels(), "flowf")
    assert [(t["entry_ts"], t["side"]) for t in r["trades"]][0] == ("09:05", -1)   # 익절 뒤 신호가 살아 있어 재진입한다
    d2 = engine.DayFrame(_flat(), _flow(lambda k: 0.0))
    r2 = families.run_family_day(d2, _levels(), "flowf")
    assert r2["trades"] == [] and any("FLOWF" in n for n in r2["decision"]["notes"])


def test_brkc_direction_day_breaks_level_and_hold_day_uses_flowc():
    # 08:59 콜−풋 +200 → 하방. 09:31 종가 1099.5 < 맥점 1100 ≤ 직전 종가 → 매도 1099.5 · 손절 1102 · 09:40 고가 1102.2 → SL
    flow = _flow(lambda k: 0.0, pre=200.0)
    d = engine.DayFrame(_flat(path={"09:31": (1100.4, 1099.3, 1099.5), "09:40": (1102.2, 1099.0, 1100.0)}), flow)
    r = families.run_family_day(d, _levels([1100.0]), "brkc")
    t = r["trades"][0]
    assert (t["rule"], t["entry_ts"], t["side"], t["stop_init"], t["touch_level"]) == ("BRK", "09:31", -1, 1102.0, 1100.0)
    assert (t["exit_ts"], t["legs"][0]["reason"]) == ("09:40", "SL")
    # 보류일(|콜−풋| < 50) → FLOWC 와 같은 거래
    flow_h = _flow(lambda k: 300.0 if k >= "09:05" else 0.0, pre=10.0)
    dh = engine.DayFrame(_flat(path={"09:20": (1100.0, 1087.0, 1090.0)}), flow_h)
    rb = families.run_family_day(dh, _levels(), "brkc")
    rc = families.run_family_day(dh, _levels(), "flowc")
    assert [x["entry_ts"] for x in rb["trades"]] == [x["entry_ts"] for x in rc["trades"]]
    assert rb["trades"][0]["entry_ts"] == "09:05"
    assert rb["trades"][0]["rule"] == "FLOW"


# ── E. 엔진 — v1 시대 이름 호환 ──────────────────────────────────────────────
def test_engine_legacy_names_map_to_v1_flags():
    candles = {"09:30": (1101.0, 1101.5, 1099.5, 1100.5), "09:31": (1100.5, 1100.6, 1099.6, 1100.2)}
    flow = {"09:30": (0.0, 0.0), "09:31": (0.0, 60.0)}
    d = engine.DayFrame(candles, flow)
    L = _levels([1100.0])
    ka = ("entry_ts", "entry_px", "stop_init", "t1", "t2")
    pick = lambda v: [tuple(t[k] for k in ka) for t in engine.run_day(d, L, v)["trades"]]
    assert pick("SHADOW_X4NF") == pick("SHADOW_V1X4") != []
    assert pick("MAIN") == pick("SHADOW_V1")


# ── D. runner · report · scorecard ─────────────────────────────────────────
def _write_dbs(tmp_path, with_fx=True):
    raw, fl, lv = str(tmp_path / "raw.db"), str(tmp_path / "flow.db"), str(tmp_path / "levels.db")
    con = sqlite3.connect(raw)
    con.execute("CREATE TABLE raw_candles (ts TEXT, open REAL, high REAL, low REAL, close REAL)")
    for k, (o, h, l, c) in _flat(path={"09:20": (1100.0, 1087.0, 1090.0)}).items():
        con.execute("INSERT INTO raw_candles VALUES (?,?,?,?,?)", ("%s %s:00" % (DAY, k), o, h, l, c))
    if with_fx:
        con.execute("CREATE TABLE raw_investor_futures (ts TEXT, fields TEXT, src TEXT, created_at TEXT)")
        for k in _minutes("09:02"):
            con.execute("INSERT INTO raw_investor_futures VALUES (?,?,?,?)",
                        ("%s %s:00" % (DAY, k), json.dumps({"foreign_net_qty": -900 if k >= "09:05" else 0}), "live", ""))
    con.commit()
    con.close()
    con = sqlite3.connect(fl)
    con.execute("CREATE TABLE option_investor_flow (trade_date TEXT, bar_time TEXT, product TEXT, investor TEXT, net_amt REAL)")
    for k, (c, p) in _flow(lambda k: 300.0 if k >= "09:05" else 0.0, pre=200.0).items():
        con.execute("INSERT INTO option_investor_flow VALUES (?,?,?,?,?)", (DAY, k, "wk_thu_call", "individual", c))
        con.execute("INSERT INTO option_investor_flow VALUES (?,?,?,?,?)", (DAY, k, "wk_thu_put", "individual", p))
    con.commit()
    con.close()
    con = sqlite3.connect(lv)
    con.execute("CREATE TABLE premarket_levels (date TEXT, stage TEXT, struct_up TEXT, struct_down TEXT, "
                "dist_low REAL, dist_high REAL, low80_lo REAL, high80_hi REAL, atr14 REAL)")
    con.execute("INSERT INTO premarket_levels VALUES (?,?,?,?,?,?,?,?,?)",
                (DAY, "0850", "[]", json.dumps([[1100.0, ["a"]]]), 1080.0, 1120.0, 1070.0, 1130.0, 30.0))
    con.commit()
    con.close()
    return raw, fl, lv


def test_runner_compute_dispatches_by_kind(tmp_path):
    raw, fl, lv = _write_dbs(tmp_path)
    r = runner.compute(DAY, raw, fl, lv)
    assert tuple(r["results"]) == spec.VARIANTS
    main = r["results"]["MAIN"]
    assert main["decision"]["bias"] == -1 and main["decision"]["family"] == "flowc"   # v1 R1 판정을 실어 받는다
    assert {t["rule"] for t in main["trades"]} == {"FLOW"} and main["trades"]
    assert {t["rule"] for t in r["results"]["SHADOW_FLOWF"]["trades"]} == {"FLOW"}
    assert all(t["rule"] in ("R2", "R3") for t in r["results"]["SHADOW_V1"]["trades"])
    # FLOWF 원천 테이블이 없으면 미측정(거래 0 · 노트)
    raw2, fl2, lv2 = _write_dbs(tmp_path / "nofx", with_fx=False) if (tmp_path / "nofx").mkdir() is None else (None,) * 3
    r2 = runner.compute(DAY, raw2, fl2, lv2)
    assert r2["results"]["SHADOW_FLOWF"]["trades"] == []
    assert any("FLOWF" in n for n in r2["results"]["SHADOW_FLOWF"]["decision"]["notes"])


def test_run_and_store_then_report_and_scorecard(tmp_path):
    raw, fl, lv = _write_dbs(tmp_path)
    sd = str(tmp_path / "sd.db")
    runner.run_and_store(DAY, raw, fl, lv, sd, live=False)
    # 저장 행: 변형·규칙·spec_version
    con = sqlite3.connect(sd)
    rows = con.execute("SELECT variant, rule, spec_version, count(*) FROM shindong_trades GROUP BY 1,2,3").fetchall()
    con.close()
    assert any(v == "MAIN" and rule == "FLOW" and sv == spec.SPEC_VERSION and n >= 1 for v, rule, sv, n in rows)
    assert any(v == "SHADOW_V1" and rule in ("R2", "R3") for v, rule, _sv, _n in rows)
    # 일일 리포트
    from strategy.shindong import daily_report
    r = daily_report.build(DAY, raw, fl, lv, sd, out_dir=str(tmp_path / "out"), pc="TEST")
    assert r["ok"] is True
    md = open(r["md_path"], encoding="utf-8").read()
    for sec in ("## 0. 한눈에", "## 1. 차트", "## 2. 거래 흐름 — MAIN", "## 3. 섀도 흐름", "## 4. 누적 채점"):
        assert sec in md
    assert "MAIN(v2 FLOWC)" in md and "V1(현행 R1/R2/R3)" in md and "FLOWF(외국인선물 추종)" in md
    assert "v2 vs V1 되돌림 판정 1/20일" in md
    assert "| FLOW " in md                      # 규칙별 열
    # 채점표
    sc = _scorecard()
    txt = sc.build(sd, spec.SCORING_START, raw, lv)
    assert "## 3. v2 vs V1 되돌림 판정" in txt and "판정: **대기** — 1/20 거래일" in txt
    assert "SHADOW_FLOWF 판정" in txt and "SHADOW_BRKC 판정" in txt
    assert "V1 레거시 — R3 중단 판정" in txt
    assert "FLOWC ↔ FLOWF 대조" in txt and "첫 진입 방향 일치 **1 / 1**" in txt


def test_scorecard_is_v1_helper():
    sc = _scorecard()
    assert sc._is_v1({"variant": "SHADOW_V1"}) is True
    assert sc._is_v1({"variant": "MAIN", "spec_version": spec.V1_SPEC_VERSION}) is True
    assert sc._is_v1({"variant": "MAIN"}) is True                              # 미기록은 v1 로 본다
    assert sc._is_v1({"variant": "MAIN", "spec_version": spec.SPEC_VERSION}) is False
    assert sc._is_v1({"variant": "SHADOW_FLOWF"}) is False


def test_report_dir_is_v2_folder():
    from config import settings
    assert settings.SHINDONG_DAILY_REPORT_DIR.replace("\\", "/").endswith("docs/신동거래_V2/일일")


def test_store_keeps_other_spec_generation_rows(tmp_path):
    """[604차] v2 코드가 v1 시대 날짜를 다시 돌려도 v1 MAIN 행을 RETRACTED 로 만들거나 덮지 않는다(사료 보존)."""
    sd = str(tmp_path / "sd.db")
    tr_v1 = {"side": -1, "entry_ts": "09:47", "entry_px": 1103.6, "stop_init": 1107.5, "t1": 1100.5, "t2": 1092.75,
             "status": "CLOSED", "exit_ts": "10:19", "stop_now": 1103.6, "rule": "R3", "touch_level": 1106.0,
             "touch_ts": "09:45",
             "legs": [{"leg": 1, "open": False, "ts": "09:55", "px": 1100.5, "reason": "TP1", "pts": 3.1, "net": 100000.0},
                      {"leg": 2, "open": False, "ts": "10:19", "px": 1092.75, "reason": "TP2", "pts": 10.85, "net": 500000.0}]}
    res_v1 = {"decision": {"pm_sp": 279.0, "bias": -1, "r2": "CONFIRMED", "r2_ts": "09:03", "notes": []}, "trades": [tr_v1]}
    store.save_day(sd, "2026-09-30", "MAIN", "wk_thu", "", res_v1, "15:08", spec.V1_SPEC_VERSION, source="live")
    tr_v2 = dict(tr_v1, rule="FLOW", touch_level=None, touch_ts=None, entry_ts="09:06", stop_init=None)
    res_v2 = {"decision": {"pm_sp": 279.0, "bias": -1, "r2": None, "r2_ts": None, "notes": []}, "trades": [tr_v2]}
    store.save_day(sd, "2026-09-30", "MAIN", "wk_thu", "", res_v2, "15:08", spec.SPEC_VERSION, source="live")
    con = sqlite3.connect(sd)
    rows = con.execute("SELECT rule, spec_version, status FROM shindong_trades WHERE variant='MAIN' ORDER BY rule").fetchall()
    day = con.execute("SELECT spec_version FROM shindong_day WHERE variant='MAIN'").fetchone()[0]
    con.close()
    assert ("R3", spec.V1_SPEC_VERSION, "CLOSED") in rows         # v1 행 그대로(철회 아님)
    assert ("FLOW", spec.SPEC_VERSION, "CLOSED") in rows
    assert day == spec.V1_SPEC_VERSION                            # 판정 행도 v1 세대를 덮지 않는다


# ── v2.1 재난 손절(채점 전 사전 정정) ─────────────────────────────────────────
def test_catastrophe_stop_uses_atr14_and_halts_the_day():
    L = _levels()
    L["0850"]["atr14"] = 30.0                                  # 재난 손절 = 0.6 × 30 = 18pt
    flow = _flow(lambda k: 300.0 if k >= "09:05" else 0.0)     # 09:05 매도 1100 → 손절 1118
    d = engine.DayFrame(_flat(path={"09:30": (1118.5, 1100.0, 1110.0), "10:00": (1110.0, 1080.0, 1090.0)}), flow)
    r = families.run_family_day(d, L, "flowc")
    t = r["trades"][0]
    assert (t["stop_init"], t["exit_ts"], t["legs"][0]["reason"], t["legs"][0]["px"]) == (1118.0, "09:30", "SL", 1118.0)
    assert len(r["trades"]) == 1                                # 신호가 살아 있어도 그날 재진입 없음(10:00 급락도 못 탄다)
    assert any("재난 손절 발동" in n for n in r["decision"]["notes"])


def test_catastrophe_stop_fallback_without_atr14_is_logged():
    flow = _flow(lambda k: 300.0 if k >= "09:05" else 0.0)
    d = engine.DayFrame(_flat(), flow)
    r = families.run_family_day(d, _levels(), "flowc")         # _levels() 에는 atr14 가 없다
    assert r["trades"][0]["stop_init"] == 1100.0 + spec.FLOW_CAT_STOP_FALLBACK_PT
    assert any("폴백" in n for n in r["decision"]["notes"])


def test_catastrophe_stop_not_hit_in_normal_trade():
    L = _levels(); L["0850"]["atr14"] = 30.0
    flow = _flow(lambda k: 300.0 if k >= "09:05" else 0.0)
    d = engine.DayFrame(_flat(path={"09:20": (1100.0, 1087.0, 1090.0)}), flow)   # 익절 경로 — 손절 1118 은 무관
    t = families.run_family_day(d, L, "flowc")["trades"][0]
    assert (t["stop_init"], t["legs"][0]["reason"]) == (1118.0, "TP1")
