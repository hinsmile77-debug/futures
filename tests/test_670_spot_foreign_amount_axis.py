# -*- coding: utf-8 -*-
"""[MW0602 670차 후속3 · F3] 현물 외인 방향 = 금액(백만원) — 주식 수(net_qty)는 참고.

계기: 원천 경고가 「금액 열 오류 의심 · 수량 부호만 쓸 것」이라 **거꾸로** 안내했다. 금액이 정규장 보도와 일치하고
(10-13 −4.53조 · 10-19 −365억), 수량은 주식 수라 종목 구성에 따라 부호가 갈린다(9/21–10/28 외인 장중 32%).
10-28 은 주식 수 −2,618 인 13:00 에 금액 +7,221억 매수였다 — 신동AI 가 하루 종일 「현물 매도」로 읽었다.

고정하는 것
-----------
A. PIT 기본 규칙 v3 — S1 이 flow_amt 를 읽고(주식 수는 spot_q 기록), 문턱 9,350백만 · 버전·개시일.
B. 신동2 snapshot — 현물 누계·플래그가 금액 부호 · 경고 문구가 「금액 기준」(「수량 부호만」 금지).
C. I3 v2 — net_amt · 데드존 · 판정 표본은 2026-10-29 부터(verify 가 since 를 지킨다).
D. 스킬 규약 — 현물도 금액.

실행: base anaconda `python -m pytest tests/test_670_spot_foreign_amount_axis.py -v`
"""
import os
import sqlite3
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import foreign_flow_pit_review as R   # noqa: E402
import shindong2_live as M            # noqa: E402
from strategy.shindong2_ai.indicators import i3_spot_foreign_persist as I3   # noqa: E402


def _S(spot_q, spot_a):
    """09:00–09:59 합성 하루. 현물 외인 주식 수는 spot_q(k), 금액은 spot_a(k) 로 움직인다(k = 경과 분)."""
    cs, flow, amt = [], {}, {}
    for m in range(9 * 60, 10 * 60):
        t = "%02d:%02d" % (m // 60, m % 60)
        cs.append([t, 1100.0, 1100.5, 1099.5, 1100.0])
        k = m - 540
        flow.setdefault(("kospi_spot", "foreign"), []).append((t, spot_q(k)))
        amt.setdefault(("kospi_spot", "foreign"), []).append((t, spot_a(k)))
    return dict(day="2026-10-28", cs=cs, fut=[], flow=flow, flow_amt=amt, wk_prod="wk_thu", wk_exp="2026-10-29",
                wk_why="합성", lv=[], snaps=[], s9842=[], yymmdd="261028")


# ── A. PIT 기본 v3 ────────────────────────────────────────────────────────
def test_s1_reads_amount_not_shares():
    # 10-28 지문: 주식 수는 줄고(매도처럼 보임) 금액은 분당 +1,500백만씩 는다(매수)
    S = _S(lambda k: -30 * k, lambda k: 1500 * k)
    o = R.observe(S, "09:40")
    assert o["spot_d"] == 15000 and o["spot_q"] < 0
    assert R.decide(o)["terms"]["S1"] == +1, "S1 은 금액 부호를 따라야 한다"


def test_s1_dead_zone_is_9350_million():
    S = _S(lambda k: 500 * k, lambda k: 900 * k)            # Δ10 = 9,000백만 < 9,350 → 기권
    assert R.decide(R.observe(S, "09:40"))["terms"]["S1"] == 0
    S = _S(lambda k: 500 * k, lambda k: 950 * k)            # Δ10 = 9,500백만 ≥ 9,350 → 표
    assert R.decide(R.observe(S, "09:40"))["terms"]["S1"] == +1


def test_v3_prereg_and_screen_keys():
    assert R.BASE_VER == "SD2B-2026-10-28-v3" and R.BASE_VER_PREV == "SD2B-2026-10-10-v2"
    assert R.SCORING_START_V3 == "2026-10-29" and R.SCORING_START_V2 == "2026-10-12"   # P 계열 창은 이어진다
    assert R.DEAD["S1"] == 9350
    out = R.analyze(_S(lambda k: 0, lambda k: 0), live=False, start="09:05", end="09:15")
    assert out["base_scoring_start"] == R.SCORING_START_V3 and out["base_ver_v1"] == R.BASE_VER_V1
    assert out["scoring_start"] == R.SCORING_START_V2
    html = open(os.path.join(_ROOT, "tools", "maekjeom_ladder", "ladder.html"), encoding="utf-8").read()
    assert "SD.base_scoring_start" in html and "SD.base_ver_v1" in html and "현물외인 백만원" in html


# ── B. snapshot · 플래그 · 경고 ──────────────────────────────────────────
@pytest.fixture
def flow_db(tmp_path, monkeypatch):
    db = tmp_path / "data" / "db"
    db.mkdir(parents=True)
    con = sqlite3.connect(str(db / "option_flow.db"))
    con.execute("CREATE TABLE option_investor_flow (trade_date TEXT, bar_time TEXT, product TEXT, market_code TEXT,"
                " investor TEXT, sell_qty INTEGER, buy_qty INTEGER, net_qty INTEGER, net_amt INTEGER, collected_at TEXT)")
    rows = [("13:00", "foreign", -2618, 722100), ("13:00", "institution", 2808, 914389)]
    for t, inv, q, a in rows:
        con.execute("INSERT INTO option_investor_flow VALUES ('2026-10-28', ?, 'kospi_spot', 'B', ?, 0, 0, ?, ?, '')", (t, inv, q, a))
    con.commit()
    con.close()
    monkeypatch.setattr(M, "ROOT", str(tmp_path))
    return tmp_path


def test_spot_foreign_summary_is_amount(flow_db):
    assert M._spot_foreign("2026-10-28", "13:05") == 722100
    assert M._eok(722100) == "+7,221억" and M._eok(-36460) == "−365억"


def test_flags_follow_amount_sign(flow_db):
    # 플래그는 선물 경로(7221 DB)가 있어야 계산된다 — 여기서는 입력(현물 금액·주식 수 갈림)과 판정 축(소스)을 고정한다
    sf = M._foreign_profile("2026-10-28", "13:05")["kospi_spot_foreign"]
    assert sf["qty"] < 0 < sf["amt"]
    src = open(os.path.join(_ROOT, "scripts", "shindong2_live.py"), encoding="utf-8").read()
    assert 'ff > 0 > sf["amt"]' in src and 'ff > 0 > sf["qty"]' not in src     # 현선 교체 플래그는 금액 부호
    assert "abs(sf[\"amt\"]) >= SPOT_AMT_DEAD" in src and M.SPOT_AMT_DEAD == R.DEAD["S1"]


def test_warning_says_amount_is_direction(flow_db):
    st = dict(date="2026-10-28", prev=dict(date="2026-10-27"), foreign=dict(kospi_spot_foreign=dict(t="13:00", qty=-2618, amt=722100)))
    w = [x for x in M.source_warnings(st) if "현물" in x]
    assert len(w) == 1 and "방향은 **금액** 기준" in w[0] and "+7,221억" in w[0]
    src = open(os.path.join(_ROOT, "scripts", "shindong2_live.py"), encoding="utf-8").read()
    assert 'W.append("현물 외인 수량' not in src                         # 거꾸로 된 종전 경고가 되살아나지 않는다


def test_render_shows_amount_first(flow_db):
    fp = M._foreign_profile("2026-10-28", "13:05")
    txt = "\n".join(M._render_foreign(fp))
    assert "현물 외인 **금액 +7,221억** (주식 수 -2618 · 참고)" in txt


# ── C. I3 v2 ─────────────────────────────────────────────────────────────
def test_i3_reads_amount_with_dead_zone(flow_db):
    db = str(flow_db / "data" / "db" / "option_flow.db")
    con = sqlite3.connect(db)
    for m in range(9 * 60, 9 * 60 + 30):
        t = "%02d:%02d" % (m // 60, m % 60)
        con.execute("INSERT INTO option_investor_flow VALUES ('2026-10-29', ?, 'kospi_spot', 'B', 'foreign', 0, 0, ?, ?, '')",
                    (t, -10 * (m - 539), 2000 * (m - 539)))          # 주식 수는 계속 음수, 금액은 계속 양수
    con.commit()
    con.close()
    ser = I3.series("2026-10-29", "09:29", db=db)
    assert ser[-1][1] == 60000                                      # 금액
    v = I3.compute_from(ser, "09:29", dead=I3.DEAD_AMT)
    assert v > 0, "금액 부호(매수)를 따라야 한다"
    assert 0 < v < 1                                                # 개장 직후 |누계| < 9,350 인 분은 분자에서 빠진다


def test_i3_prereg_since_excludes_exploration_days():
    assert I3.META["prereg"]["since"] == "2026-10-29" and "금액" in I3.META["version"]
    assert I3.DEAD_AMT == R.DEAD["S1"]
    src = open(os.path.join(_ROOT, "scripts", "shindong2_research.py"), encoding="utf-8").read()
    assert 'prereg.get("since")' in src and 'd >= prereg["since"]' in src


# ── D. 스킬 ──────────────────────────────────────────────────────────────
def test_skill_says_spot_is_amount():
    s = open(os.path.join(_ROOT, ".claude", "skills", "shindong2", "SKILL.md"), encoding="utf-8").read()
    assert "현물도 금액" in s and "주식 수는 참고" in s
