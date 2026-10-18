# -*- coding: utf-8 -*-
"""[MW0602 2026-10-18 · SD-2026-10-19-v3] 신동 v3 — MAIN = HYBR60 · 섀도 재구성 회귀 테스트.

고정하는 불변식:
  ① 규격: v3 는 **새 값이 없다** — K·창·손절·트레일·익절·상한이 v2 사전등록값 그대로. 바뀐 것은 라우팅·손절 뒤 처리뿐.
  ② HYBR60: 하루 첫 거래 = FLOWC 신호(rule FLOW) · 2·3번째 = FLOWR60 신호(rule R60, 첫 신호 10:00).
  ③ 손절 방향 **누적** 금지(sticky): 손절 난 방향은 그날 막고 반대 방향은 연다 · 두 방향 모두 손절이면 당일 끝.
     덮어쓰기(same, 605차 반사실)와 갈리는 유일한 경우 = 「매도 손절 → 매수 손절 → 매도 신호」.
  ④ 섀도: V22(v2.2 그대로 · 되돌림 기준) · V22S · HYBL · FLOWR60 · BRKC. V1·V1X4·FLOWF 종료.
  ⑤ 실데이터 재현: 공식 경로 16일(9/21~10/16) 합계 = 반사실(`docs/신동거래_V2/신동거래_V3/v3후보_반사실_20261018/`).
근거: docs/신동거래_V2/신동거래_V3/신동_v3_규칙제안_섀도재구성_MW0602_20261018.md
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tests"))

import pytest  # noqa: E402

from strategy.shindong import engine, families, spec  # noqa: E402
from test_604_shindong_v2 import _flat, _flow, _levels  # noqa: E402


# ── ① 규격 ────────────────────────────────────────────────────────────────
def test_v3_spec_is_preregistered():
    assert spec.SPEC_VERSION == "SD-2026-10-19-v3"
    assert (spec.SCORING_START, spec.V22_SPEC_VERSION, spec.V22_SCORING_START) == \
        ("2026-10-19", "SD-2026-10-15-v2.2", "2026-10-15")
    assert (spec.MAIN_KIND, spec.MAIN_FAMILY) == ("family", "hybr60")
    assert spec.HYB_SL_HALT_MODE == spec.SL_BAN_STICKY == "sticky"
    # 새 값 없음 — v2 사전등록값 그대로
    assert (spec.FLOWC_K, spec.FLOWR_WIN_MIN, spec.FLOWR_K) == (300, 60, 150)
    assert (spec.FLOW_CAT_STOP_ATR, spec.FLOW_TRAIL, spec.FLOW_TP, spec.FLOW_MAX_TRADES, spec.FLOW_LAST_ENTRY) == \
        (0.6, (6.0, 4.0), 12.0, 3, "14:50")
    assert (spec.LEAD_WIN_MIN, spec.LEAD_C_MIN, spec.LEAD_K_CP, spec.LEAD_K_FX) == (60, 0.3, 150.0, 400.0)
    assert spec.VARIANTS == ("MAIN", "SHADOW_V22", "SHADOW_V22S", "SHADOW_HYBL", "SHADOW_FLOWR60", "SHADOW_BRKC")
    assert spec.ROLLBACK_VARIANT == "SHADOW_V22" and spec.SHADOW_META_D["SHADOW_V22"]["family"] == "flowc"
    assert {"SHADOW_V1", "SHADOW_V1X4", "SHADOW_FLOWF"} <= set(spec.RETIRED_SHADOWS)
    assert not (set(spec.RETIRED_SHADOWS) & set(spec.VARIANTS))
    assert all(v == "2026-10-19" for v in spec.LATE_SHADOW_START.values())
    assert len(spec.VARIANTS) - 1 <= 5


# ── ② HYBR60 라우팅 ───────────────────────────────────────────────────────
def _hyb_day():
    # 09:05 콜−풋 +300 → FLOWC 매도 1100 · 09:20 저가 1087 → 익절 12pt.
    # 콜−풋은 이후에도 분당 +5 씩 오른다 → FLOWC 신호는 09:21 부터 켜져 있고, 60분 변화(≥150)는 10:00 에 처음 성립.
    flow = _flow(lambda k: (300.0 + 5 * ((int(k[:2]) - 9) * 60 + int(k[3:]) - 5)) if k >= "09:05" else 0.0)
    return engine.DayFrame(_flat(path={"09:20": (1100.0, 1087.0, 1090.0)}), flow)


def test_hybr60_first_flowc_then_r60_from_1000():
    r = families.run_family_day(_hyb_day(), _levels(), "hybr60")
    tr = [(t["entry_ts"], t["side"], t["rule"]) for t in r["trades"]]
    assert tr[0] == ("09:05", -1, "FLOW") and r["trades"][0]["legs"][0]["reason"] == "TP1"
    assert tr[1] == ("10:00", -1, "R60"), "2번째 진입은 FLOWR60 — FLOWC 가 켜져 있던 09:21 이 아니다"
    assert len(tr) <= spec.FLOW_MAX_TRADES


def test_v22_shadow_reenters_with_flowc_unchanged():
    r = families.run_family_day(_hyb_day(), _levels(), "flowc")       # SHADOW_V22 = v2.2 MAIN
    assert [(t["entry_ts"], t["rule"]) for t in r["trades"]][:2] == [("09:05", "FLOW"), ("09:21", "FLOW")]


def test_main_dispatch_uses_hybr60():
    from strategy.shindong import runner
    d = _hyb_day()
    m = runner.run_variant(d, _levels(), "MAIN")
    assert m["decision"]["family"] == "hybr60"
    v22 = runner.run_variant(d, _levels(), "SHADOW_V22")
    assert v22["decision"]["family"] == "flowc"


# ── ③ 손절 방향 누적 금지 ─────────────────────────────────────────────────
def _ladder():
    """09:01 매도 1100 → 09:02 고가 1106 손절(1105) → 09:03 매수 1106 → 09:04 저가 1100 손절(1101) → 09:05 매도 신호."""
    c = _flat()
    c["09:02"] = (1106.0, 1106.0, 1100.0, 1106.0)
    c["09:03"] = (1106.0, 1106.0, 1106.0, 1106.0)
    c["09:04"] = (1100.0, 1106.0, 1100.0, 1100.0)
    for k in [x for x in c if x >= "09:05"]:
        c[k] = (1100.0, 1100.0, 1100.0, 1100.0)
    d = engine.DayFrame(c, {})
    want = {"09:01": -1, "09:03": 1, "09:05": -1}
    return d, (lambda k: want.get(k, 0))


def _ladder_run(mode, notes=None):
    d, sig = _ladder()
    return families._run_signal(d, sig, "FLOW", lambda side, e: e - side * 5.0, None, None, 3,
                                halt_mode=mode, notes=notes)


def test_sticky_blocks_third_after_both_sides_stopped():
    notes = []
    tr = _ladder_run("sticky", notes)
    assert [(t["entry_ts"], t["side"], t["legs"][0]["reason"]) for t in tr] == [("09:01", -1, "SL"), ("09:03", 1, "SL")]
    assert any("양방향 손절 — 당일 신규 진입 종료" in n for n in notes)


def test_same_overwrites_and_reopens_first_side():
    tr = _ladder_run("same")
    assert [(t["entry_ts"], t["side"]) for t in tr] == [("09:01", -1), ("09:03", 1), ("09:05", -1)]


def test_sticky_allows_opposite_after_one_stop_and_logs_blocked():
    c = _flat()
    c["09:02"] = (1106.0, 1106.0, 1100.0, 1106.0)
    d = engine.DayFrame(c, {})
    want = {"09:01": -1, "09:03": -1, "09:04": -1, "09:06": 1}
    notes = []
    tr = families._run_signal(d, lambda k: want.get(k, 0), "FLOW", lambda side, e: e - side * 5.0, None, None, 3,
                              halt_mode="sticky", notes=notes)
    assert [(t["entry_ts"], t["side"]) for t in tr] == [("09:01", -1), ("09:06", 1)]
    assert any("손절 방향 금지로 막힌 신호 2분" in n for n in notes)
    assert any("매도 당일 금지 · 반대 방향은 진입 가능" in n for n in notes)


def test_existing_modes_unchanged():
    tr = _ladder_run("all")
    assert [t["entry_ts"] for t in tr] == ["09:01"]
    assert [t["entry_ts"] for t in _ladder_run(None)] == ["09:01", "09:03", "09:05"]


# ── ④ HYBL ────────────────────────────────────────────────────────────────
def test_hybl_routes_and_notes_missing_fx():
    r = families.run_family_day(_hyb_day(), _levels(), "hybl")
    assert r["trades"][0]["rule"] == "FLOW"
    assert all(t["rule"] == "LEAD" for t in r["trades"][1:])
    assert any("HYBL 외국인 선물 원천 없음" in n for n in r["decision"]["notes"])


def test_lead_signal_no_future_and_starts_1000():
    d = _hyb_day()
    sig, _st = families._lead_signal(d)
    assert all(sig(k) == 0 for k in d.idx if k < "10:00")
    # k 이후 값을 바꿔도 k 의 판정이 같다(미래 참조 없음)
    k = "10:30"
    a = sig(k)
    d.sp["11:00"] = -9e9
    sig2, _ = families._lead_signal(d)
    assert sig2(k) == a


# ── ⑤ 실데이터 재현 ───────────────────────────────────────────────────────
_DBS = [os.path.join(_ROOT, "data", "db", p) for p in ("raw_data.db", "option_flow.db", "premarket_levels.db")]
_DAYS = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01",
         "2026-10-02", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-12", "2026-10-13", "2026-10-14",
         "2026-10-15", "2026-10-16"]


@pytest.mark.skipif(not all(os.path.exists(p) for p in _DBS), reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
def test_official_path_reproduces_counterfactual_16days():
    from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
    from strategy.shindong import daily_report as DR
    flow = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(_ROOT, WEEKLY_OPTION_FLOW_DB)
    tot = {v: 0.0 for v in spec.VARIANTS}
    for day in _DAYS:
        o = DR.load_day(day, RAW_DATA_DB, flow, PREMARKET_LEVELS_DB)
        if not o.get("ok"):
            pytest.skip("%s 봉 없음 — 이 PC DB 범위 밖" % day)
        for v in spec.VARIANTS:
            tot[v] += sum(engine.trade_net(t) for t in o["results"][v]["trades"] if t["status"] == "CLOSED")
    # MW0602 DB 실측(2026-10-18). 반사실 v3_candidates.py(가드 전 기간) · rule12_check.py 와 같다.
    assert {v: round(x) for v, x in tot.items()} == pytest.approx(
        {"MAIN": 17268164, "SHADOW_V22": 17727850, "SHADOW_V22S": 18342777, "SHADOW_HYBL": 17574291,
         "SHADOW_FLOWR60": 13404620, "SHADOW_BRKC": 9230154}, abs=2)
