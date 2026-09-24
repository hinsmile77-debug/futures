# -*- coding: utf-8 -*-
"""[MW0601 626차] 신동(神童) 가상거래 — 규격 · 상품 선택 · 엔진 · 차트 · 수급 토글.

무엇을 고정하나
---------------
A. **사전등록 규격이 조용히 바뀌지 않는다** — 값이 바뀌면 이 테스트가 깨져
   `SPEC_VERSION` 갱신과 사전등록 문서 개정을 강제한다.
B. 상품 선택 — 최근접 만기 위클리, **먼스리 만기주에는 먼스리**(사용자 지시 5번).
C. 엔진 — 미래 참조 없음(horizon 뒤를 안 본다), 재생 결과가 분석 원본과 같다
   (9/21–9/23 실측 재현 · 로컬 DB 가 있을 때만).
D. 차트 — [dev 이식판] 제외(dev 는 차트·패널에 신동을 그리지 않는다 — v9-dev 에만 있다).
E. 옵션 수급 차트 — 계약수/금액 토글이 옵션 행만 바꾸고, 금액 없는 행을 계약수로 섞지 않는다.

실행:
    conda run -n py37_32 python -m pytest tests/test_626_shindong.py -q
"""
import datetime as dt
import os
import sys
from datetime import datetime, timedelta

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from strategy.shindong import engine, spec  # noqa: E402
from strategy.shindong.calendar import select_flow_product  # noqa: E402


# ── A. 규격 고정 ──────────────────────────────────────────────────────────
def test_spec_is_preregistered_values():
    """🔴 값이 바뀌면 검증 시계가 초기화된다 — 이 테스트를 고치기 전에 사전등록 문서부터."""
    assert spec.SPEC_VERSION == "SD-2026-09-24-v1"
    assert (spec.BIAS_MIN, spec.CONF_MIN, spec.CONF_END, spec.REV_MIN, spec.REV_WIN_MIN) == \
        (50, 50, "09:10", 50, 10)
    assert (spec.TOUCH_NEAR, spec.TOUCH_FAR, spec.LV_STOP_BUF, spec.EXT_STOP_BUF) == \
        (1.0, 1.5, 1.5, 0.5)
    assert (spec.T1_MIN_DIST, spec.TP_BUF, spec.OR_STOP_BUF) == (2.0, 0.5, 1.0)
    assert (spec.R3_START, spec.NEW_ENTRY_END, spec.TIME_EXIT) == ("09:30", "14:30", "15:05")
    assert spec.VARIANTS == ("MAIN", "SHADOW_E2F2")
    assert (spec.SCORING_START, spec.R3_KILL_AFTER_DAYS, spec.R3_KILL_NET_MAX,
            spec.R3_KILL_WINRATE_MAX) == ("2026-09-28", 10, 0, 0.35)


# ── B. 상품 선택 ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("day,expect", [
    ("2026-09-21", "wk_mon"),   # 월위클리 만기일
    ("2026-09-22", "wk_thu"),
    ("2026-09-23", "wk_thu"),   # 9/24 추석 → 목위클리 만기가 9/23 으로 당겨짐
    ("2026-09-28", "wk_mon"),   # 🔴 정상 거래일(대체공휴일 아님) — 월위클리 만기 당일
    ("2026-09-29", "wk_thu"),   # 다음 만기는 10/1(목) 목위클리
    ("2026-09-30", "wk_thu"),
    ("2026-10-06", "wk_mon"),   # 10/5 개천절 대체공휴일 → 월위클리 만기 10/6 으로 순연(확정 규칙)
    ("2026-10-07", "mon"),      # 🔴 먼스리 만기주(10/8) — 목위클리 대신 먼스리
    ("2026-10-08", "mon"),
    ("2026-11-10", "mon"),      # 11/12 먼스리 만기주
    ("2026-11-12", "mon"),
    ("2026-11-17", "wk_thu"),   # 다음 주는 다시 목위클리
])
def test_product_selection(day, expect):
    prod, _exp, note = select_flow_product(dt.date.fromisoformat(day))
    assert prod == expect, note


def test_monthly_week_note_says_so():
    _p, _e, note = select_flow_product(dt.date(2026, 10, 7))
    assert "먼스리 만기주" in note


# ── C. 엔진 ──────────────────────────────────────────────────────────────
def _levels():
    rows = {"0850": {
        "dist_high": 1110.0, "dist_low": 1090.0,
        "high80_hi": 1120.0, "low80_lo": 1080.0,
        "struct_up": "[[1108, [\"전일고1108\"]]]",
        "struct_down": "[[1095, [\"매물대1095\"]], [1085, [\"전일VWAP1085\"]]]"}}
    return engine.prepare_levels(rows)


def _synthetic_day():
    """장전 콜 우세(+120) → 09:01 콜 증가·풋 감소로 하방 확정 → 1090 아래로 흘러내린다."""
    candles, flow = {}, {}
    px = 1100.0
    t = datetime(2026, 1, 5, 8, 45)
    for i in range(0, 380):
        k = t.strftime("%H:%M")
        if k >= "09:02":
            px -= 0.08
        candles[k] = (px + 0.05, px + 0.2, px - 0.2, px)
        # i=15 가 09:00 — 09:01 에 콜 +40 · 풋 −20 → 콜−풋 +60 (확정 문턱 50 초과)
        call = 100.0 if k < "09:01" else 100.0 + (i - 15) * 40
        put = -20.0 if k < "09:01" else -20.0 - (i - 15) * 20
        if k >= "08:46":
            flow[k] = (call, put)
        t += timedelta(minutes=1)
    return candles, flow


def test_engine_r2_short_on_synthetic_day():
    candles, flow = _synthetic_day()
    d = engine.DayFrame(candles, flow)
    res = engine.run_day(d, _levels(), "MAIN")
    dec = res["decision"]
    assert dec["bias"] == -1 and dec["r2"] == "CONFIRMED" and dec["r2_ts"] == "09:01"
    r2 = [t for t in res["trades"] if t["rule"] == "R2"][0]
    assert r2["side"] == -1
    # 1차 = 거리맥점 1090 +0.5 / 최종 = 가장 먼 구조맥점 1085 +0.5
    assert r2["t1"] == pytest.approx(1090.5) and r2["t2"] == pytest.approx(1085.5)


def test_engine_never_reads_past_horizon():
    """horizon 까지만 준 재생의 **닫힌 다리**는 하루 전체 재생과 같아야 한다(미래 참조 없음)."""
    candles, flow = _synthetic_day()
    full = engine.run_day(engine.DayFrame(candles, flow), _levels(), "MAIN")
    for h in ("09:05", "09:40", "11:00", "13:30"):
        part = engine.run_day(engine.DayFrame(candles, flow, horizon=h), _levels(), "MAIN")
        for tp in part["trades"]:
            tf = [x for x in full["trades"] if x["entry_ts"] == tp["entry_ts"]][0]
            for gp, gf in zip(tp["legs"], tf["legs"]):
                if not gp["open"]:
                    assert (gp["ts"], gp["px"]) == (gf["ts"], gf["px"])


def test_time_exit_waits_for_1505_bar():
    """15:05 봉이 오기 전에는 시간 청산을 확정하지 않는다 — 보유 중(OPEN)이다."""
    candles, flow = _synthetic_day()
    part = engine.run_day(engine.DayFrame(candles, flow, horizon="09:03"), _levels(), "MAIN")
    assert all(t["status"] == "OPEN" for t in part["trades"])


def test_leg_net_matches_cost_model():
    pts, net = engine.leg_net(-1, 1130.50, 1110.50, False)
    assert pts == pytest.approx(20.0)
    assert net == pytest.approx(988007, abs=1)     # 9/23 R2 최종 다리(분석값)


# 로컬 DB 가 있을 때만 — 9/21–9/23 분석 원본 재현
_DB_OK = all(os.path.exists(os.path.join(_ROOT, p)) for p in
             ("data/db/raw_data.db", "data/db/option_flow.db", "data/db/premarket_levels.db"))


@pytest.mark.skipif(not _DB_OK, reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
@pytest.mark.parametrize("day,main,shadow", [
    ("2026-09-21", 157978, 431416),
    ("2026-09-22", 1629902, 1629902),
    ("2026-09-23", 1776971, 1338845),
])
def test_replay_reproduces_preregistration_analysis(day, main, shadow):
    from strategy.shindong import runner
    r = runner.compute(day, os.path.join(_ROOT, "data/db/raw_data.db"),
                       os.path.join(_ROOT, "data/db/option_flow.db"),
                       os.path.join(_ROOT, "data/db/premarket_levels.db"))
    if not r["results"]["MAIN"]["trades"] and "봉 없음" in str(r["results"]["MAIN"]["decision"]):
        pytest.skip("그날 봉이 이 PC DB 에 없다")
    got = {v: round(sum(engine.trade_net(t) for t in res["trades"]))
           for v, res in r["results"].items()}
    assert got["MAIN"] == pytest.approx(main, abs=2)
    assert got["SHADOW_E2F2"] == pytest.approx(shadow, abs=2)


# ── D. 차트 — [dev 이식판] 제외 ─────────────────────────────────────────
# dev(MW0602)는 1분봉 차트·손익 패널에 신동을 그리지 않는다(이식 범위 「계산·기록 + 수급 차트」,
# 2026-09-24 사용자 결정 — MW0602 자체 GP 표시 유지). 차트 레이어 테스트는 v9-dev 에만 있다.
from PyQt5.QtWidgets import QApplication  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)


# ── E. 옵션 수급 차트 — 계약수/금액 토글 ─────────────────────────────────
def test_flow_chart_amount_toggle_swaps_option_rows_only():
    from dashboard.panels.option_flow_delta_chart import OptionFlowDeltaChart
    ch = OptionFlowDeltaChart()
    ch._payload = {"trade_date": "1999-01-01", "products": {
        "wk_thu_call": {"label": "(목)위클리 콜", "unit": "계약", "baseline": 10,
                        "value": 30, "delta": 20, "series": [("09:00", 0), ("09:01", 20)],
                        "unit_amt": "백만원", "baseline_amt": 5, "value_amt": 105,
                        "delta_amt": 100, "series_amt": [("09:00", 0), ("09:01", 100)]},
        # 금액이 없는 행 — 금액 모드에서 계약수로 섞이면 안 된다
        "mon_put": {"label": "먼스리 풋", "unit": "계약", "baseline": 0, "value": 3,
                    "delta": 3, "series": [("09:00", 0), ("09:01", 3)]},
    }}
    ch._fut_payload = {"products": {"fut_x": {"label": "외인", "unit": "계약",
                                              "series": [("09:00", 0)]}}}
    qty = ch._merged()
    assert qty["wk_thu_call"]["unit"] == "계약" and "mon_put" in qty
    ch._btn_unit.setChecked(True)
    amt = ch._merged()
    assert amt["wk_thu_call"]["unit"] == "백만원"
    assert amt["wk_thu_call"]["series"][-1] == ("09:01", 100)
    assert "mon_put" not in amt, "금액 없는 행을 계약수로 남기면 단위가 섞인다"
    assert amt["fut_x"]["unit"] == "계약", "선물 행은 토글 대상이 아니다"


# ── main.py 배선 ─────────────────────────────────────────────────────────
def test_main_wires_shindong_after_flow_fetch():
    import re
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    # ast.get_source_segment 는 3.8+ — 런타임은 3.7 이다
    a = src.index("    def _fetch_weekly_option_flow(")
    b = re.compile(r"\n    def ").search(src, a + 10).start()
    body = src[a:b]
    assert "self._run_shindong(now)" in body
    assert body.index("flow.fetch_and_store()") < body.index("self._run_shindong(now)")
    assert "self._sd_seen = {}" in src and "self._sd_warned = False" in src


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
