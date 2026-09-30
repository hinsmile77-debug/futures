# -*- coding: utf-8 -*-
"""[MW0602 598차] 신동 — SHADOW_X4NFA(깨진 맥점 금지) · 09:00 봉 결손 내성 · 채점표 표시 3종 · RETRACTED 로그.

무엇을 고정하나
---------------
A. 사전등록 — X4NFA 채점 시작 9/30 · MAIN 규격 버전 무변경 · A 필터 비교 기준 변형.
B. 엔진 — 반전 대기 중 가격이 맥점을 다시 넘어가면 X4NFA 만 진입하지 않는다(MAIN·X4NF 는 진입).
   맥점 이쪽 편이면 셋 다 진입한다. 흐름 5일 재생에서 X4NFA 의 깨진 맥점 진입은 0건.
C. 09:00 1분봉 결손일 — 엔진 R2 경로와 일일 리포트가 KeyError 로 죽지 않는다
   (2026-09-29 실측: 장후 리포트·메일이 통째로 빠졌다).
D. 채점표 — 깨진 맥점 판별 · 「보이는 대로」 손익(철회 신호) · R1·R2 경제성 · R3 분리.
E. main.py — 재계산에서 사라진 거래를 `[Shindong] … RETRACTED` 한 줄로 남긴다.

⚠ 로컬 DB 값에 기대지 않는다(합성 데이터) — 두 PC 의 봉·맥점이 달라 같은 코드가
  다른 값을 낸다(`docs/신동거래/신동_흐름정리_레슨런_수익개선안_MW0602-20260929.md` §4-3).

실행:
    python -m pytest tests/test_598_shindong_x4nfa.py -q
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

import pytest  # noqa: E402

from strategy.shindong import engine, spec  # noqa: E402


def _scorecard():
    sp = importlib.util.spec_from_file_location(
        "shindong_scorecard", os.path.join(_ROOT, "scripts", "shindong_scorecard.py"))
    sc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(sc)
    return sc


def _levels(struct, dist_low=1080.0, dist_high=1120.0):
    lv = {"0850": {"struct_up": "[]", "struct_down": "[]",
                   "dist_low": dist_low, "dist_high": dist_high,
                   "low80_lo": 1070.0, "high80_hi": 1130.0}}
    L = engine.prepare_levels(lv)
    L["0850"]["S"] = sorted(struct)
    return L


# ── A ────────────────────────────────────────────────────────────────────
def test_x4nfa_preregistration():
    # [604차] X4NFA 는 2026-09-30 부로 종료(RETIRED) — 엔진 플래그·재현 테스트는 유지된다
    assert spec.VARIANTS[0] == "MAIN" and "SHADOW_X4NFA" in spec.RETIRED_SHADOWS
    assert "SHADOW_X4NFA" not in spec.VARIANTS
    assert spec.X4NFA_BASE_VARIANT == "SHADOW_X4NF"
    assert spec.V1_SPEC_VERSION == "SD-2026-09-24-v1"                  # v1 값 무변경(SHADOW_V1)


# ── B ────────────────────────────────────────────────────────────────────
def _touch_day(close_0931, low_0931):
    """09:30 매수 터치(맥점 1100, 저가 1099.5 · 종가 1100.5) → 09:31 콜−풋 −60(반전) 진입."""
    candles = {"09:30": (1101.0, 1101.5, 1099.5, 1100.5),
               "09:31": (1100.5, 1100.6, low_0931, close_0931)}
    flow = {"09:30": (0.0, 0.0), "09:31": (0.0, 60.0)}           # 콜−풋 0 → −60
    return engine.DayFrame(candles, flow)


def _r3(res):
    return [(t["entry_ts"], t["side"]) for t in res["trades"] if t["rule"] == "R3"]


def test_broken_level_entry_blocked_only_in_x4nfa():
    d = _touch_day(close_0931=1099.0, low_0931=1098.8)            # 진입가 1099.0 < 맥점 1100 — 깨짐
    L = _levels([1100.0])
    assert _r3(engine.run_day(d, L, "MAIN")) == [("09:31", 1)]
    assert _r3(engine.run_day(d, L, "SHADOW_X4NF")) == [("09:31", 1)]
    assert _r3(engine.run_day(d, L, "SHADOW_X4NFA")) == []


def test_intact_level_entry_kept_in_x4nfa():
    d = _touch_day(close_0931=1100.2, low_0931=1099.6)            # 진입가 1100.2 > 맥점 — 정상
    L = _levels([1100.0])
    main = engine.run_day(d, L, "MAIN")
    x4 = engine.run_day(d, L, "SHADOW_X4NF")
    x4a = engine.run_day(d, L, "SHADOW_X4NFA")
    assert _r3(main) == _r3(x4a) == [("09:31", 1)]
    # A 가 막지 않으면 X4NFA 는 X4NF 와 같은 거래다(목표 X4 · 같은 손절)
    ka = ("entry_px", "stop_init", "t1", "t2")
    assert [tuple(t[k] for k in ka) for t in x4a["trades"]] == [tuple(t[k] for k in ka) for t in x4["trades"]]


_DB_OK = all(os.path.exists(os.path.join(_ROOT, p)) for p in
             ("data/db/raw_data.db", "data/db/option_flow.db", "data/db/premarket_levels.db"))


@pytest.mark.skipif(not _DB_OK, reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
@pytest.mark.parametrize("day", ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29"])
def test_replay_x4nfa_never_enters_broken_level_and_keeps_r2(day):
    from strategy.shindong import runner
    r = runner.compute_legacy(day, os.path.join(_ROOT, "data/db/raw_data.db"),      # [604차] v1 이름 재현
                              os.path.join(_ROOT, "data/db/option_flow.db"),
                              os.path.join(_ROOT, "data/db/premarket_levels.db"))["results"]
    if not r["MAIN"]["trades"] and "봉 없음" in str(r["MAIN"]["decision"]):
        pytest.skip("그날 봉이 이 PC DB 에 없다")
    for t in r["SHADOW_X4NFA"]["trades"]:
        if t["rule"] == "R3":
            assert t["side"] * (t["entry_px"] - t["touch_level"]) > 0
    r2 = lambda v: [(t["entry_ts"], round(engine.trade_net(t))) for t in r[v]["trades"] if t["rule"] == "R2"]
    assert r2("SHADOW_X4NFA") == r2("MAIN")


# ── C. 09:00 봉 결손 ───────────────────────────────────────────────────────
def _missing_0900_inputs():
    """09:00 봉 없음 · 08:59 콜−풋 +200(하방) · 09:01 콜 +100 풋 −10 → R2 확정 09:01."""
    candles, flow = {}, {}
    t = dt.datetime(2026, 9, 29, 8, 46)
    i = 0
    while t.strftime("%H:%M") <= "15:08":
        k = t.strftime("%H:%M")
        if k >= "09:01":
            c = 1100.0 - 0.05 * i
            candles[k] = (c + 0.1, c + 0.3, c - 0.3, c)
            i += 1
        flow[k] = (200.0, 0.0) if k < "09:01" else (300.0, -10.0)
        t += dt.timedelta(minutes=1)
    return candles, flow


def test_engine_r2_survives_missing_0900_bar():
    candles, flow = _missing_0900_inputs()
    d = engine.DayFrame(candles, flow)
    assert "09:00" in d.idx and "09:00" not in d.h                  # 흐름만 있고 봉이 없는 분
    res = engine.run_day(d, _levels([1090.0, 1080.0], dist_low=1095.0), "MAIN")
    dec = res["decision"]
    assert (dec["bias"], dec["r2"], dec["r2_ts"]) == (-1, "CONFIRMED", "09:01")
    r2 = [t for t in res["trades"] if t["rule"] == "R2"][0]
    assert r2["stop_init"] == pytest.approx(candles["09:01"][1] + spec.OR_STOP_BUF)


def _write_dbs(tmp_path, candles, flow, day="2026-09-29"):
    raw, fl, lv = (str(tmp_path / n) for n in ("raw.db", "flow.db", "lv.db"))
    con = sqlite3.connect(raw)
    con.execute("CREATE TABLE raw_candles (ts TEXT, open REAL, high REAL, low REAL, close REAL)")
    con.executemany("INSERT INTO raw_candles VALUES (?,?,?,?,?)",
                    [("%s %s:00" % (day, k),) + v for k, v in candles.items()])
    con.commit()
    con.close()
    con = sqlite3.connect(fl)
    con.execute("CREATE TABLE option_investor_flow (trade_date TEXT, bar_time TEXT, product TEXT, "
                "investor TEXT, net_amt REAL)")
    for k, (c, p) in flow.items():
        con.execute("INSERT INTO option_investor_flow VALUES (?,?,?,?,?)", (day, k, "wk_thu_call", "individual", c))
        con.execute("INSERT INTO option_investor_flow VALUES (?,?,?,?,?)", (day, k, "wk_thu_put", "individual", p))
    con.commit()
    con.close()
    con = sqlite3.connect(lv)
    con.execute("CREATE TABLE premarket_levels (date TEXT, stage TEXT, struct_up TEXT, struct_down TEXT, "
                "dist_low REAL, dist_high REAL, low80_lo REAL, high80_hi REAL)")
    con.execute("INSERT INTO premarket_levels VALUES (?,?,?,?,?,?,?,?)",
                (day, "0850", "[]", json.dumps([[1090.0, ["a"]], [1080.0, ["b"]]]), 1095.0, 1110.0, 1070.0, 1130.0))
    con.commit()
    con.close()
    return raw, fl, lv


def test_daily_report_survives_missing_0900_bar(tmp_path):
    from strategy.shindong import daily_report
    candles, flow = _missing_0900_inputs()
    raw, fl, lv = _write_dbs(tmp_path, candles, flow)
    r = daily_report.build("2026-09-29", raw, fl, lv, str(tmp_path / "none.db"),
                           out_dir=str(tmp_path / "out"), pc="TEST")
    assert r["ok"] is True
    md = open(r["md_path"], encoding="utf-8").read()
    assert "09:00봉 결손" in md                                     # 결손을 숨기지 않는다(계측 4원칙 ④)
    assert "V1X4(R2+X4NF)" in md and "MAIN(v2 FLOWC)" in md         # [604차] v2 변형 라벨


# ── D. 채점표 ─────────────────────────────────────────────────────────────
def test_scorecard_is_broken():
    sc = _scorecard()
    assert sc._is_broken({"rule": "R3", "side": 1, "entry_px": 1084.2, "touch_level": 1088.0}) is True
    assert sc._is_broken({"rule": "R3", "side": -1, "entry_px": 1087.8, "touch_level": 1085.0}) is True
    assert sc._is_broken({"rule": "R3", "side": -1, "entry_px": 1086.88, "touch_level": 1088.0}) is False
    assert sc._is_broken({"rule": "R2", "side": -1, "entry_px": 1115.5, "touch_level": None}) is None


def test_scorecard_as_seen_net(tmp_path):
    sc = _scorecard()
    raw = str(tmp_path / "raw.db")
    con = sqlite3.connect(raw)
    con.execute("CREATE TABLE raw_candles (ts TEXT, open REAL, high REAL, low REAL, close REAL)")
    for k, c in (("09:49", 1086.0), ("09:50", 1085.0), ("09:51", 1084.0)):
        con.execute("INSERT INTO raw_candles VALUES (?,?,?,?,?)", ("2026-09-29 %s:00" % k, c, c, c, c))
    con.commit()
    t = {"trade_date": "2026-09-29", "source": "live", "status": "RETRACTED", "side": -1,
         "entry_px": 1086.1, "detect_px": 1086.1, "updated_at": "2026-09-29 09:51:47"}
    got = sc._as_seen_net(t, con)
    # 09:51:47 에 알아챔 → 직전 완성봉 09:50 종가 1085.0 에 두 다리 시장가 청산
    exp = 2 * engine.leg_net(-1, 1086.1, 1085.0, True)[1]
    assert got == pytest.approx(exp)
    # 철회 전 1차가 닫혔으면 그 다리는 기록 청산가를 쓴다
    t1 = dict(t, leg1_exit_ts="2026-09-29 09:50:00", leg1_exit_px=1084.5, leg1_reason="TP1")
    exp1 = engine.leg_net(-1, 1086.1, 1084.5, False)[1] + engine.leg_net(-1, 1086.1, 1085.0, True)[1]
    assert sc._as_seen_net(t1, con) == pytest.approx(exp1)
    # 백필 · 원천 없음 → 미측정(None ≠ 0)
    assert sc._as_seen_net(dict(t, source="backfill"), con) is None
    assert sc._as_seen_net(t, None) is None
    con.close()


def test_scorecard_display_sections():
    sc = _scorecard()
    days = [{"variant": "MAIN", "trade_date": "2026-09-28", "bias": -1, "r2_status": "CONFIRMED"},
            {"variant": "MAIN", "trade_date": "2026-09-29", "bias": 0, "r2_status": None}]
    tr = lambda day, rule, side, e, lv, net: {"variant": "MAIN", "trade_date": day, "rule": rule, "side": side,
                                             "entry_px": e, "touch_level": lv, "net_krw": net, "status": "CLOSED"}
    live = [tr("2026-09-28", "R2", -1, 1115.5, None, 1283379.0),
            tr("2026-09-28", "R3", -1, 1098.36, 1100.0, 682000.0),       # R1 같음 · 정상
            tr("2026-09-28", "R3", 1, 1100.86, 1100.0, -270000.0),       # R1 반대 · 정상
            tr("2026-09-29", "R3", 1, 1084.20, 1088.0, -87267.0)]        # 보류일 · 깨짐
    econ = "\n".join(sc._r2_econ_section(live, days))
    assert "| R1 보류일(콜−풋 절댓값 < 50 또는 미수집) | 1 (50%) |" in econ
    assert "| R2 확정 / 방향일 | 1 / 1 = 100% |" in econ
    split = "\n".join(sc._r3_split_section(live, days))
    assert "| **깨진 맥점 진입** (X4NFA 차단 대상) | 1 | 0 | 0% | -87,267 |" in split
    assert "| R1 방향과 같음 | 1 | 1 | 100% | +682,000 |" in split
    assert "| R1 방향과 반대 | 1 | 0 | 0% | -270,000 |" in split
    assert "| R1 보류일 | 1 | 0 | 0% | -87,267 |" in split


# ── E. main.py 배선 ───────────────────────────────────────────────────────
def test_main_logs_retracted_once():
    import re
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    a = src.index("    def _run_shindong(")
    b = re.compile(r"\n    def ").search(src, a + 10).start()
    body = src[a:b]
    assert "RETRACTED 진입" in body
    assert 'self._sd_seen[_k] = "RETRACTED"' in body                  # 같은 철회를 두 번 적지 않는다
    assert "self._sd_last = {}" in body                               # 날짜가 바뀌면 비운다
    init = src[:a]
    assert "self._sd_last = {}" in init                               # __init__ 명시 초기화(계측 4원칙 ④)
    assert 'getattr(self, "_sd_last"' not in src


def test_main_retracted_behavior(monkeypatch):
    """`_run_shindong` 본문을 떼어 실제로 돌린다 — 신호가 사라지면 RETRACTED 한 줄, 같은 철회는 다시 안 적는다."""
    import logging
    import re
    import textwrap
    import types
    from strategy.shindong import runner as sd_runner
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    a = src.index("    def _run_shindong(")
    b = re.compile(r"\n    def ").search(src, a + 10).start()
    msgs = []

    class _Log(object):
        def info(self, fmt, *args):
            msgs.append(fmt % args)

        def warning(self, fmt, *args, **kw):
            msgs.append("WARN " + (fmt % args))

    ns = {"datetime": dt, "logger": _Log(), "logging": logging,
          "runtime_settings": types.SimpleNamespace(
              SHINDONG_ENABLED=True, RAW_DATA_DB="r", WEEKLY_OPTION_FLOW_DB="f",
              PREMARKET_LEVELS_DB="l", SHINDONG_DB="s")}
    exec(textwrap.dedent(src[a:b]), ns)
    run = ns["_run_shindong"]
    row = {"trade_key": "R3|09:49|-1", "rule": "R3", "side": -1, "status": "OPEN", "entry_px": 1086.1,
           "entry_ts": "2026-09-29 09:49:00", "stop_now": 1089.5, "t1": 1080.5, "t2": 1071.5,
           "leg1_reason": None, "leg2_reason": None, "net_krw": 0.0, "product": "wk_thu",
           "detected_at": "2026-09-29 09:50:47"}
    payloads = [{"trades": [row], "horizon": "09:49", "last_close": 1086.1},
                {"trades": [], "horizon": "09:50", "last_close": 1084.2},
                {"trades": [], "horizon": "09:51", "last_close": 1084.0}]
    monkeypatch.setattr(sd_runner, "run_and_store", lambda *a_, **k: payloads.pop(0))
    me = types.SimpleNamespace(_sd_day=None, _sd_seen={}, _sd_last={}, _sd_warned=False, dashboard=None,
                               _refresh_pnl_history=lambda: None)
    for m in (49, 50, 51):
        run(me, dt.datetime(2026, 9, 29, 9, m, 47))
    assert not [x for x in msgs if x.startswith("WARN")], msgs
    ret = [x for x in msgs if "RETRACTED" in x]
    assert len(ret) == 1                                              # 세 번째 호출에서 다시 적지 않는다
    assert "R3 매도 RETRACTED 진입 1086.10(09:49)" in ret[0] and "현재가 1084.20" in ret[0]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
