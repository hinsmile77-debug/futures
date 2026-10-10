# -*- coding: utf-8 -*-
"""[MW0601 678차] 신동2 사전등록 개정 v2 — 위클리 원천 · 먼스리 만기주 기권 · 옵션 콜−풋 금액 단위.

개정 문서: docs/미륵이고도화3/신동2/신동2_개정_v2_수급단위_위클리원천_MW0601-20261010.md

고정하는 것
-----------
A. 위클리 원천 = 만기 최근접. 9/21–10/8 11거래일 실측 주력 상품(외인 거래량 최대)과 전부 일치한다.
   v1(`wk_mon` 고정)은 4/11, 요일 고정안(금·월 월위클리 / 화–목 목위클리)은 8/11 이었다.
B. 먼스리 만기주에는 위클리 항이 기권한다 — 같은 원천(먼스리)이 O1·O2 두 표를 던지지 않는다.
C. 옵션 콜−풋은 금액(flow_amt)으로 판정하고, 계약수는 `*_q` 로 기록만 한다.
D. 사전등록 값(버전·데드밴드·채점 시작)이 조용히 바뀌지 않는다 — 바꾸면 이 테스트와 개정 문서를 함께 고칠 것.
E. 라이브 스냅샷도 같은 단위(금액)를 읽는다 — 규칙과 다른 값을 해설하지 않도록.

실행: conda run --no-capture-output -n py37_32 python -m pytest tests/test_678_shindong2_v2_flow_unit_weekly.py -v
"""
import datetime as _dt
import os
import sqlite3
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, _ROOT)
import foreign_flow_pit_review as R  # noqa: E402
from strategy.shindong.calendar import select_flow_product  # noqa: E402

# 9/21–10/8 외인 마지막 바 누적 매수+매도(계약) 최대 상품 — option_flow.db 실측(2026-10-10)
DOMINANT = {
    "2026-09-21": "wk_mon", "2026-09-22": "wk_thu", "2026-09-23": "wk_thu", "2026-09-28": "wk_mon",
    "2026-09-29": "wk_thu", "2026-09-30": "wk_thu", "2026-10-01": "wk_thu", "2026-10-02": "wk_mon",
    "2026-10-06": "wk_mon",            # 화요일 — 10/5 개천절 대체공휴일로 월위클리 만기 순연
    "2026-10-07": "mon", "2026-10-08": "mon",   # 먼스리 만기주 — 목위클리 미상장
}


# ── A ────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("day,dom", sorted(DOMINANT.items()))
def test_weekly_source_is_nearest_expiry_and_matches_dominant(day, dom):
    assert select_flow_product(_dt.date.fromisoformat(day))[0] == dom


def test_weekday_rule_would_have_missed_holiday_and_monthly_weeks():
    """요일 고정안이 틀리는 3일을 남겨 둔다 — 그 안으로 되돌아가지 않도록."""
    weekday_rule = lambda d: "wk_mon" if d.weekday() in (0, 4) else "wk_thu"
    miss = [d for d, dom in DOMINANT.items() if weekday_rule(_dt.date.fromisoformat(d)) != dom]
    assert sorted(miss) == ["2026-10-06", "2026-10-07", "2026-10-08"]


def test_observe_no_longer_hardcodes_monday_weekly():
    src = open(os.path.join(_ROOT, "scripts", "foreign_flow_pit_review.py"), encoding="utf-8").read()
    assert 'ocd("wk_mon")' not in src and "select_flow_product" in src


# ── 합성 하루 ──────────────────────────────────────────────────────────────
def _S(wk_prod="wk_thu"):
    cs, flow, amt = [], {}, {}
    for m in range(8 * 60 + 45, 10 * 60):
        t = "%02d:%02d" % (m // 60, m % 60)
        cs.append([t, 1100.0, 1100.5, 1099.5, 1100.0])
        k = m - 525
        # 먼스리: 계약수는 콜−풋 음수(싼 외가격 풋 대량 매수)인데 금액은 양수(비싼 콜 매수) — 부호가 갈린다
        flow.setdefault(("mon_call", "foreign"), []).append((t, 10 * k))
        flow.setdefault(("mon_put", "foreign"), []).append((t, 60 * k))
        amt.setdefault(("mon_call", "foreign"), []).append((t, 50 * k))
        amt.setdefault(("mon_put", "foreign"), []).append((t, 5 * k))
        for p in ("wk_mon", "wk_thu"):
            sg = 1 if p == "wk_thu" else -1
            flow.setdefault((p + "_call", "foreign"), []).append((t, sg * 30 * k))
            flow.setdefault((p + "_put", "foreign"), []).append((t, 0))
            amt.setdefault((p + "_call", "foreign"), []).append((t, sg * 40 * k))
            amt.setdefault((p + "_put", "foreign"), []).append((t, 0))
    return dict(day="2026-09-30", cs=cs, fut=[], flow=flow, flow_amt=amt, wk_prod=wk_prod, wk_exp="2026-10-01",
                wk_why="합성", lv=[], snaps=[], s9842=[], yymmdd="260930")


# ── B ────────────────────────────────────────────────────────────────────
def test_monthly_expiry_week_abstains_weekly_term():
    o = R.observe(_S(wk_prod="mon"), "09:55")
    assert o["wk_src"] == "mon" and o["wk_cp"] is None and o["wk_cp_d"] is None and o.get("wk_skip")
    assert o["mon_cp"] is not None
    b, terms = R.p_bias(o)
    assert terms["O2L"] == 0                                  # 먼스리가 크더라도 위클리 표는 없다
    assert R.decide(o)["terms"]["O2"] == 0


def test_weekly_term_reads_the_selected_product():
    o_thu, o_mon = R.observe(_S("wk_thu"), "09:55"), R.observe(_S("wk_mon"), "09:55")
    assert o_thu["wk_cp"] > 0 > o_mon["wk_cp"]                 # 합성에서 두 상품은 부호가 반대다
    assert o_thu["wk_src"] == "wk_thu"


# ── C ────────────────────────────────────────────────────────────────────
def test_option_cp_uses_amount_and_records_contracts_only():
    o = R.observe(_S(), "09:55")
    assert o["mon_cp"] > 0, "판정은 금액 기준이어야 한다"
    assert o["mon_cp_q"] < 0, "계약수는 기록용으로 남는다"
    assert R.p_bias(o)[1]["O1L"] == (1 if abs(o["mon_cp"]) >= R.P_BIAS["O1L"] else 0)


# ── D ────────────────────────────────────────────────────────────────────
def test_preregistered_v2_values():
    assert R.BASE_VER == "SD2B-2026-10-10-v2" and R.BASE_VER_PREV == "SD2B-2026-10-06-v1"
    assert (R.P_VER, R.P2_VER, R.P3_VER) == ("SD2P-2026-10-10-v2", "SD2P2-2026-10-10-v2", "SD2P3-2026-10-10-v2")
    assert R.SCORING_START_V2 == "2026-10-12" and R.V1_SCORED_DAYS == ("2026-10-07", "2026-10-08")
    assert R.P_BIAS == dict(O1L=1850, F2=300, O2L=750, PX=3.0)
    assert R.DEAD == dict(F1=50, F2=300, O1=130, O2=150, S1=100, P1=1.0)
    assert R.P_BIAS_GO == 2 and R.FLOW_UNIT == "백만원"


def test_real_days_wk_source_and_monthly_skip():
    if not os.path.exists(os.path.join(R.DB, "option_flow.db")):
        pytest.skip("실데이터 DB 없음")
    S = R.load("2026-10-07")
    if not S["cs"]:
        pytest.skip("10/7 봉 없음")
    o = R.observe(S, "09:35")
    assert S["wk_prod"] == "mon" and o["wk_cp"] is None and o["mon_cp"] is not None
    S = R.load("2026-10-06")
    assert S["wk_prod"] == "wk_mon" and R.observe(S, "09:35")["wk_cp"] is not None


# ── E ────────────────────────────────────────────────────────────────────
def test_live_snapshot_reads_amount(tmp_path, monkeypatch):
    import shindong2_live as M
    db = tmp_path / "data" / "db"
    db.mkdir(parents=True)
    con = sqlite3.connect(str(db / "option_flow.db"))
    con.execute("CREATE TABLE option_investor_flow (trade_date TEXT, bar_time TEXT, product TEXT, market_code TEXT,"
                " investor TEXT, sell_qty INTEGER, buy_qty INTEGER, net_qty INTEGER, net_amt INTEGER, collected_at TEXT)")
    for t, q, a in (("09:00", 500, -10), ("09:05", 900, -40)):
        con.execute("INSERT INTO option_investor_flow VALUES ('2026-09-30', ?, 'wk_thu_call', 'x', 'foreign', 0, 0, ?, ?, '')", (t, q, a))
    con.execute("INSERT INTO option_investor_flow VALUES ('2026-09-30', '09:05', 'wk_thu_put', 'x', 'foreign', 0, 0, 7, 3, '')")
    con.commit(); con.close()
    monkeypatch.setattr(M, "ROOT", str(tmp_path))
    assert M._opt_amt("2026-09-30", "wk_thu", "09:04") == (-10, None)       # 풋은 그 시각까지 없음 = 미측정
    assert M._opt_amt("2026-09-30", "wk_thu", "09:05") == (-40, 3)          # 금액(백만원) — 계약수 아님
    assert M._opt_amt("2026-09-30", None, "09:05") == (None, None)
    src = open(os.path.join(_ROOT, "scripts", "shindong2_live.py"), encoding="utf-8").read()
    assert 'get("wk_mon_call")' not in src and 'unit="백만원"' in src


# ── F. [678차 후속] 화면 — 버전·개시일 표시, 옵션 수급 띠 계약수/금액 토글 ──────────
def test_analyze_exposes_version_and_start_for_screen():
    out = R.analyze(_S(), live=False, start="09:05", end="09:15")
    assert out["base_ver"] == R.BASE_VER and out["base_ver_prev"] == R.BASE_VER_PREV
    assert out["scoring_start"] == R.SCORING_START_V2 and out["v1_scored_days"] == list(R.V1_SCORED_DAYS)
    assert out["p"]["ver"] == R.P_VER and out["wk"]["prod"] == "wk_thu" and out["flow_unit"] == "백만원"


def test_ladder_page_has_version_strip_and_unit_toggle():
    html = open(os.path.join(_ROOT, "tools", "maekjeom_ladder", "ladder.html"), encoding="utf-8").read()
    assert 'id="sd2Ver"' in html and "SD.scoring_start" in html and "SD.base_ver" in html
    assert 'id="segUnit"' in html and "seg('segUnit', 'unit'" in html and "D.flow1m_amt" in html
    assert "unit: 'qty'" in html, "기본은 계약수 — 기존 화면과 같게 연다"


def test_ladder_flow1m_returns_amount_series():
    sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
    import ladder_data as L
    if not os.path.exists(os.path.join(R.DB, "option_flow.db")):
        pytest.skip("실데이터 DB 없음")
    mins, qty, last, amt = L.flow1m("2026-10-07")
    a, q = amt["mon_call"]["foreign"], qty["mon_call"]["foreign"]
    if a is None:
        pytest.skip("10/7 먼스리 콜 외인 없음")
    assert len(a) == len(q) == len(mins) and a != q           # 금액은 계약수와 다른 시계열이다
    assert amt["wk_thu_call"]["foreign"] is None               # 먼스리 만기주 — 목위클리 미상장(미측정, 0 아님)


# ── G. [678차 후속2] 사다리 — 시간 창 · 세로 자동 맞춤 · 창 밖 맥점 · 방향 영역 · 미니 개요 ──────────
def _ladder_html():
    return open(os.path.join(_ROOT, "tools", "maekjeom_ladder", "ladder.html"), encoding="utf-8").read()


def test_ladder_time_window_controls_and_overview():
    h = _ladder_html()
    for k in ('id="segWin"', 'id="winPrev"', 'id="winNext"', 'id="winLast"', 'id="segDir"', 'id="winRange"', 'id="ladMini"',
              "function winRange()", "function setWindow(", "function drawMini(", "win: 'all'", "dir: 'on'"):
        assert k in h, k
    assert "['60', '60분'], ['120', '120분'], ['all', '전체']" in h


def test_ladder_wheel_does_not_hijack_page_scroll():
    """그냥 휠은 페이지 스크롤 — Ctrl 일 때만 확대·축소, Shift/가로 휠일 때만 이동(긴 페이지에서 스크롤이 차트에 걸리지 않게)."""
    h = _ladder_html()
    assert "if (ev.ctrlKey) {" in h and "{ passive: false }" in h
    assert "그냥 휠 = 페이지 스크롤" in h


def test_ladder_y_axis_fits_window_and_reports_off_range_levels():
    h = _ladder_html()
    assert "const visC = C.filter(" in h and "baseC = visC.length ? visC : C" in h       # 세로축 = 창 안 캔들
    assert "const offUp = allLv.filter(L => L.price > yMax)" in h and "외 ${rest}개" in h   # 안 보임 ≠ 없음 · 잔여 개수
    assert "clip-path': 'url(#ladClip)'" in h


def test_ladder_direction_area_skips_unmeasured_and_legacy():
    h = _ladder_html()
    assert "function dirSegments()" in h and "const mergeSegs" in h
    assert "let cur = null, why = '', t = DAY0;" in h, "AI 첫 기록 전 구간은 칠하지 않는다(미측정 ≠ 관망)"
    assert "(r.variant || 'live') !== 'legacy'" in h, "기존방식 섀도 기록은 방향에 쓰지 않는다"
    for tok in ("--dir-buy", "--dir-sell", "--dir-flat"):
        assert h.count(tok + ":") == 3, tok                                       # 라이트 · 다크(미디어) · 다크(data-theme)


def test_ladder_ctrl_wheel_zoom_is_gentle_and_proportional():
    """[678차 후속3] Ctrl+휠 — 이벤트당 고정 25% 는 너무 빨랐다. 이동량 비례(한 칸 7%) · 이벤트당 ±12% 상한 · 기준 창은 winRange()."""
    h = _ladder_html()
    assert "const ZOOM_K = Math.log(1.07) / 100;" in h
    assert "Math.min(1.12, Math.max(1 / 1.12, Math.exp(px * ZOOM_K)))" in h
    assert "const [cx0, cx1] = winRange()" in h
    assert "ev.deltaY > 0 ? 1.25 : 0.8" not in h
