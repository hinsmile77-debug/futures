# -*- coding: utf-8 -*-
"""[MW0601 662차 후속] 신동2 · 신동2-P — 미래 참조 차단과 사전등록 불변식.

고정하는 것
-----------
A. observe(S, T) 는 T 이후 데이터를 아무리 바꿔도 결과가 같다(미래 참조 0).
B. 신동2-P 손절은 진입 시 거리 그대로 — 보유 중 넓히지 않는다(피터 손절 확대일이 손실일).
C. 재진입은 같은 방향뿐 — 방향이 바뀌면 그 앞에 「세팅 변경」 로그가 있어야 한다.
D. 하루 진입 ≤ 3, 손절 3회 또는 −12pt 에서 종료.
E. 피터 거래 줄 파서.

실행: conda run -n py37_32 python -m pytest tests/test_662b_shindong2_pit.py -v
"""
import copy
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, _ROOT)
import foreign_flow_pit_review as R  # noqa: E402


def _synthetic():
    cs, fut, flow = [], [], {}
    px = 1100.0
    for m in range(8 * 60 + 45, 15 * 60 + 46):
        t = "%02d:%02d" % (m // 60, m % 60)
        px += -0.3 if m < 11 * 60 else 0.1
        cs.append([t, px, px + 0.5, px - 0.5, px])
        if m >= 9 * 60 + 2:
            fut.append((t, -(m - 540) * 10, (m - 540) * 10, 0))
        for prod, sgn in (("mon_call", -1), ("mon_put", 1), ("wk_mon_call", -1), ("wk_mon_put", 1), ("kospi_spot", -1)):
            flow.setdefault((prod, "foreign"), []).append((t, sgn * (m - 525) * 20))
    lv = [dict(stage="0850", start="08:51", kind="구조", price=p, label="x", side="up") for p in (1090.0, 1080.0, 1070.0)]
    return dict(cs=cs, fut=fut, flow=flow, lv=lv, snaps=[], s9842=[], yymmdd="261006")


# ── A. 미래 참조 0 ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("T", ["08:55", "09:05", "09:35", "13:00"])
def test_observe_ignores_everything_at_or_after_T(T):
    S = _synthetic()
    a = R.observe(S, T)
    S2 = copy.deepcopy(S)
    lim = R._hm(T)
    for c in S2["cs"]:
        if R._hm(c[0]) >= lim:
            c[1:] = [9999.0, 9999.5, 9998.5, 9999.0]
    S2["fut"] = [(t, (99999 if R._hm(t) >= lim else f), i, r) for t, f, i, r in S2["fut"]]
    for k in S2["flow"]:
        S2["flow"][k] = [(t, (99999 if R._hm(t) >= lim else v)) for t, v in S2["flow"][k]]
    S2["lv"].append(dict(stage="0930", start=T, kind="구조", price=5000.0, label="미래", side="up"))
    S2["lv"][-1]["start"] = R._fmt(lim + 1)               # T 이후에 생기는 맥점
    assert R.observe(S2, T) == a


def test_bias_uses_levels_not_deltas():
    """신동2-P 세팅 점수에 Δ10 항이 없다 — 피터 「외인 수급으로 상방 하방 예측 못한다」."""
    o = dict(px=1100.0, open=1110.0, mon_cp=-1500, fut_for=-500, wk_cp=0,
             mon_cp_d=+9999, fut_for_d=+9999, wk_cp_d=+9999, spot_d=+9999, dpx=+50)
    b, terms = R.p_bias(o)
    assert b == -3 and set(terms) == {"O1L", "F2", "O2L", "PX"}


# ── B·C·D. 신동2-P 불변식 (합성 하루 + 실데이터 날짜) ──────────────────────
def _check_invariants(P):
    assert len(P["trades"]) <= R.P_MAX_ENTRIES
    stops = 0
    for x in P["trades"]:
        for pnl, why, _ in x["legs"]:
            if why == "손절":
                assert pnl >= -R.P_STOP_MAX - 1e-6, "손절 폭이 상한을 넘었다 — 넓힌 흔적"
            if why == "본전 손절":
                assert abs(pnl) < 1e-6
        if all(w == "손절" for _, w, _ in x["legs"]):
            stops += 1
    assert stops <= R.P_DAY_STOP_N
    sides = [x["side"] for x in P["trades"]]
    if len(set(sides)) > 1:
        assert any("세팅 변경" in l for l in P["log"]), "세팅 변경 없이 방향이 바뀌었다"


def test_p_invariants_on_synthetic_day():
    P = R.run_p(_synthetic())
    _check_invariants(P)
    assert P["side"] == "매도"                    # 합성 하락일 — 수준 점수가 매도 세팅


def test_p_invariants_on_real_days():
    dbs = [os.path.join(R.DB, n) for n in ("regular_candles.db", "raw_data.db", "option_flow.db")]
    if not all(os.path.exists(p) for p in dbs):
        pytest.skip("실데이터 DB 없음")
    for day in ("2026-09-17", "2026-10-01", "2026-10-02", "2026-10-06"):
        S = R.load(day)
        if not S["cs"]:
            continue
        _check_invariants(R.run_p(S))


# ── E. 피터 파서 ───────────────────────────────────────────────────────────
def test_peter_line_parser(tmp_path, monkeypatch):
    import sqlite3
    db = tmp_path / "peter_levels.db"
    con = sqlite3.connect(str(db))
    con.execute("CREATE TABLE peter_paste (date TEXT, offset REAL, raw_lv TEXT, raw_tr TEXT, saved_at TEXT)")
    con.execute("INSERT INTO peter_paste VALUES ('2026-10-06', -5.51, '', ?, '')",
                ("09:23 S 1116 / 13:49 X 1095 수익\n9:39 L 1050 / 10:17 X 1047 손절\n",))
    con.commit(); con.close()
    monkeypatch.setattr(R, "DB", str(tmp_path))
    pt = R.peter_trades("2026-10-06")
    assert [x["pnl"] for x in pt["trades"]] == [21.0, -3.0]
    assert pt["trades"][0]["entry_mini"] == 1110.49 and pt["trades"][1]["entry_t"] == "09:39"
    assert R.peter_trades("2026-10-07") is not None and R.peter_trades("2026-10-07")["measured"] is False


# ── F. 사다리 표시 — 장중에는 미래 시점·강제청산이 없다 ─────────────────────
def test_analyze_live_has_no_future_points_or_forced_exit():
    S = _synthetic()
    S["cs"] = [c for c in S["cs"] if c[0] <= "09:40"]          # 09:40 까지 완결 봉
    out = R.analyze(S, live=True)
    assert [p["obs"]["T"] for p in out["points"]] == ["08:55", "09:05", "09:15", "09:25", "09:35"]
    for p in out["points"]:
        assert p["grade"].get("result") != "15:10 강제청산"
        assert p["grade"].get("dir_hit") is None                  # 장중엔 방향 적중을 확정하지 않는다
    for t in out["p"]["trades"]:
        assert t.get("why") != "15:10 강제청산"


def test_ladder_page_and_data_wire_shindong2():
    root = os.path.join(_ROOT, "tools", "maekjeom_ladder")
    html = open(os.path.join(root, "ladder.html"), encoding="utf-8").read()
    data = open(os.path.join(root, "ladder_data.py"), encoding="utf-8").read()
    assert "D.shindong2" in html and "drawSD2Table" in html and "segSd2" in html
    assert "shindong2=sd2" in data
    assert "cs[:-1] if live" in data, "장중에는 덜 찬 마지막 봉을 넘기면 안 된다"
