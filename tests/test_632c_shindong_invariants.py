# -*- coding: utf-8 -*-
"""[MW0601 632차 후속5] 신동 변형 불변식 — **어느 PC 의 DB 로 돌려도** 성립해야 하는 성질.

왜 따로 있나 (MW0602 적용가이드 §10)
----------------------------------
`test_626`·`test_632`·`test_632b` 의 재현 테스트는 **MW0601 DB 로 뽑은 절대 손익**을 대조한다.
두 PC 는 별개 계좌·별개 수집(흐름·맥점·봉)이라 MW0602 에서는 DB 가 있어도 값이 다르다 —
그 테스트들은 이제 `pc_id() == "MW0601"` 일 때만 돈다. 여기 불변식은 그 공백을 메운다:
값이 아니라 **변형 사이의 관계**를 본다.

  I1. R2 는 변형과 무관하다 — 진입(시각·방향·가격)은 네 변형이 같고, E2 를 쓰지 않는
      MAIN · X4NF · TR44 는 손익까지 같다.
  I2. X4NF 는 같은 맥점에서 R3 진입 방향을 뒤집지 않는다.
  I3. X4NF 의 1차 목표는 같은 진입의 MAIN 1차 목표보다 멀지 않다.
  I4. E2F2 의 R3 는 모두 터치 시점의 당일 흐름 방향과 같은 쪽이다(F2).
  I5. TR44 에서 트레일 청산(`TR`)이 한 번도 없었으면 TR44 거래는 MAIN 과 완전히 같다.
  I6. 일일 리포트의 변형별 순손익 = 엔진 재생 순손익.

대상 날짜: 이 PC `option_flow.db` 에 개인 흐름이 있는 거래일 중 최근 8일(없으면 skip).

실행:
    conda run -n py37_32 python -m pytest tests/test_632c_shindong_invariants.py -q
"""
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest  # noqa: E402

from strategy.shindong import engine, spec  # noqa: E402

_DB = {k: os.path.join(_ROOT, "data", "db", v) for k, v in
       (("raw", "raw_data.db"), ("flow", "option_flow.db"), ("lv", "premarket_levels.db"),
        ("sd", "shindong.db"))}
_DB_OK = all(os.path.exists(_DB[k]) for k in ("raw", "flow", "lv"))


def _flow_days():
    if not _DB_OK:
        return []
    con = sqlite3.connect("file:%s?mode=ro" % _DB["flow"].replace("\\", "/"), uri=True)
    try:
        ds = [r[0] for r in con.execute(
            "SELECT DISTINCT trade_date FROM option_investor_flow WHERE investor='individual' "
            "ORDER BY trade_date DESC LIMIT 8")]
    except sqlite3.Error:
        ds = []
    finally:
        con.close()
    return sorted(ds)


_DAYS = _flow_days()
_CACHE = {}


def _day(d):
    if d not in _CACHE:
        from strategy.shindong import daily_report
        _CACHE[d] = daily_report.load_day(d, _DB["raw"], _DB["flow"], _DB["lv"])
    r = _CACHE[d]
    if not r["ok"]:
        pytest.skip("%s — %s" % (d, r["why"]))
    return r


pytestmark = pytest.mark.skipif(not _DAYS, reason="이 PC 에 신동 흐름 DB 가 없다(런타임 산출물)")


def _key(t):
    return (t["entry_ts"], t["side"], round(t["entry_px"], 2))


@pytest.mark.parametrize("d", _DAYS or ["-"])
def test_i1_r2_same_across_variants(d):
    r = _day(d)["results"]
    ent = {v: [_key(t) for t in r[v]["trades"] if t["rule"] == "R2"] for v in spec.VARIANTS}
    assert all(e == ent["MAIN"] for e in ent.values()), ent
    net = {v: [round(engine.trade_net(t)) for t in r[v]["trades"] if t["rule"] == "R2"]
           for v in ("MAIN", "SHADOW_X4NF", "SHADOW_TR44")}
    assert net["SHADOW_X4NF"] == net["MAIN"] == net["SHADOW_TR44"], net


@pytest.mark.parametrize("d", _DAYS or ["-"])
def test_i2_x4nf_never_flips_at_a_level(d):
    sides = {}
    for t in _day(d)["results"]["SHADOW_X4NF"]["trades"]:
        if t["rule"] == "R3":
            sides.setdefault(t["touch_level"], set()).add(t["side"])
    assert all(len(s) == 1 for s in sides.values()), sides


@pytest.mark.parametrize("d", _DAYS or ["-"])
def test_i3_x4nf_first_target_not_farther(d):
    r = _day(d)["results"]
    main = {_key(t): t for t in r["MAIN"]["trades"] if t["rule"] == "R3"}
    for t in r["SHADOW_X4NF"]["trades"]:
        m = main.get(_key(t))
        if t["rule"] != "R3" or m is None or m["t1"] is None:
            continue
        assert t["t1"] is not None
        assert t["side"] * (t["t1"] - t["entry_px"]) <= t["side"] * (m["t1"] - m["entry_px"]) + 1e-9


@pytest.mark.parametrize("d", _DAYS or ["-"])
def test_i4_e2f2_r3_follows_day_flow(d):
    day = _day(d)
    dd = day["d"]
    base = dd.sp.get(spec.CONF_BASE)
    for t in day["results"]["SHADOW_E2F2"]["trades"]:
        if t["rule"] != "R3":
            continue
        assert base is not None and t["touch_ts"] in dd.sp
        trend = -1 if dd.sp[t["touch_ts"]] - base > 0 else 1
        assert t["side"] == trend, (t["entry_ts"], t["side"], trend)


@pytest.mark.parametrize("d", _DAYS or ["-"])
def test_i5_tr44_equals_main_without_trail_exit(d):
    r = _day(d)["results"]
    tr = r["SHADOW_TR44"]["trades"]
    if any(g.get("reason") == "TR" for t in tr for g in t["legs"]):
        pytest.skip("%s — 트레일 청산이 있었던 날(관계 I5 대상 아님)" % d)
    sig = lambda ts: [(_key(t), round(engine.trade_net(t))) for t in ts]
    assert sig(tr) == sig(r["MAIN"]["trades"])


@pytest.mark.parametrize("d", _DAYS or ["-"])
def test_i6_report_sums_equal_engine(d, tmp_path):
    from strategy.shindong import daily_report
    day = _day(d)
    rep = daily_report.build(d, _DB["raw"], _DB["flow"], _DB["lv"], _DB["sd"], out_dir=str(tmp_path), pc="TEST")
    eng = {v: sum(engine.trade_net(t) for t in day["results"][v]["trades"] if t["status"] == "CLOSED")
           for v in spec.VARIANTS}
    assert {v: round(s["net"]) for v, s in rep["sums"].items()} == {v: round(x) for v, x in eng.items()}
