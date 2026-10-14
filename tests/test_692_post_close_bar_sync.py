# -*- coding: utf-8 -*-
"""[MW0601 692차] 장후 봉 정합 — 만기일 경로 · raw_candles 창 안 보충 · 따라잡기 · 부분 봉 교정.

지키려는 것:
  ① raw_candles 는 **08:45–15:08 창 안**만 메운다(범위를 늘리지 않는다 — 533차 「최근 N행」 우려).
     메운 행은 bar_recovered=2, 차트로 보정한 실시간 행은 3. **1 은 쓰지 않는다**(452차 의미).
  ② 실시간 행이 있으면 덮지 않는다 — 단 session_bars 가 차트 보정한 봉(rt_chart_open/fix)만 O/H/L/V 를 맞춘다.
  ③ 부분 봉: 시가만 다르면 그대로(틱 순서), 고·저·거래량이 다르면 rt_chart_fix 로 교정. 종가만 다르면 교정 안 함.
  ④ 따라잡기: 최근 거래일 중 411봉 미만인 날만, 만기일 제외.
  ⑤ 만기일 창(15:22–15:39) · 종료 직전 확정 판정 배선.

Python 3.7.13 32-bit(py37_32)에서 돌아야 한다.
"""

import datetime
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import db_utils
from utils import time_utils as tu
from collection.cybos import chart_backfill as cb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db(monkeypatch):
    path = os.path.join(tempfile.mkdtemp(), "raw692.db")
    monkeypatch.setattr(db_utils, "RAW_DATA_DB", path)
    db_utils.init_raw_data_db()
    return path


def _sb(ts, o, h, l, c, v, session, source, **kw):
    d = dict(ts=ts, open=o, high=h, low=l, close=c, volume=v)
    d.update(kw)
    db_utils.save_session_bar(d, session, source)


def _raw(path, ts, o, h, l, c, v):
    con = sqlite3.connect(path)
    con.execute("INSERT INTO raw_candles (ts, open, high, low, close, volume) VALUES (?,?,?,?,?,?)",
                (ts, o, h, l, c, v))
    con.commit()
    con.close()


def _rows(path, sql):
    con = sqlite3.connect(path)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


# ────────────────────────────────────────────── ① ② raw_candles 창 안 보충

def test_fill_inserts_only_missing_minutes_inside_window(monkeypatch):
    path = _db(monkeypatch)
    D = "2026-10-14"
    _raw(path, D + " 08:52:00", 951.9, 952.0, 951.0, 951.5, 100)       # 실시간 행 — 덮지 않는다
    _sb(D + " 08:45:00", 948.58, 952.0, 948.0, 951.92, 700, tu.SESSION_PRE_MARKET, "chart_backfill")
    _sb(D + " 08:52:00", 1.0, 2.0, 0.5, 1.5, 3, tu.SESSION_PRE_MARKET, "rt")
    _sb(D + " 15:09:00", 935.0, 936.0, 934.0, 935.5, 50, tu.SESSION_REGULAR, "rt")  # 창 밖
    _sb(D + " 15:45:00", 942.26, 942.26, 942.26, 942.26, 80, tu.SESSION_CLOSE_FILL, "chart_backfill")
    out = db_utils.fill_raw_candles_from_session_bars(D)
    assert out["inserted"] == 1 and out["inserted_ts"] == ["08:45"]
    rows = _rows(path, "SELECT ts, open, bar_recovered, buy_vol FROM raw_candles ORDER BY ts")
    assert rows == [(D + " 08:45:00", 948.58, 2, None),                 # buy_vol 0 을 지어내지 않는다
                    (D + " 08:52:00", 951.9, None, 0)]
    # 재실행은 멱등
    assert db_utils.fill_raw_candles_from_session_bars(D)["inserted"] == 0


def test_fill_applies_chart_fix_to_rt_row_with_flag_3(monkeypatch):
    path = _db(monkeypatch)
    D = "2026-10-13"
    _raw(path, D + " 08:45:00", 976.60, 977.0, 975.0, 976.9, 384)
    _sb(D + " 08:45:00", 977.08, 977.5, 975.0, 976.9, 634, tu.SESSION_PRE_MARKET, "rt_chart_open")
    out = db_utils.fill_raw_candles_from_session_bars(D)
    assert out["fixed"] == 1 and out["inserted"] == 0
    assert _rows(path, "SELECT open, high, volume, close, bar_recovered FROM raw_candles") == \
        [(977.08, 977.5, 634, 976.9, 3)]


def test_recovered_flag_never_uses_1():
    assert db_utils.RAW_RECOVERED_FROM_SESSION == 2
    assert db_utils.RAW_RECOVERED_CHART_FIX == 3


# ────────────────────────────────────────────── ③ 부분 봉 교정

def test_partial_bar_classification(monkeypatch):
    path = _db(monkeypatch)
    D = "2026-09-21"
    for hm, o in (("10:00", 1090.0), ("10:01", 1091.0), ("10:02", 1092.0)):
        _sb(D + " %s:00" % hm, o, o + 1, o - 1, o + 0.5, 100, tu.SESSION_REGULAR, "rt")
    rows = [
        # 10:00 시가만 다름 → 그대로
        {"date": 20260921, "time": 1001, "open": 1090.2, "high": 1091.0, "low": 1089.0, "close": 1090.5, "volume": 100, "oi": 1},
        # 10:01 저가·거래량 다름 → 부분 봉 교정
        {"date": 20260921, "time": 1002, "open": 1090.8, "high": 1092.0, "low": 1089.5, "close": 1091.5, "volume": 180, "oi": 1},
        # 10:02 종가만 다름 → 교정 안 함(그 외 미교정)
        {"date": 20260921, "time": 1003, "open": 1092.0, "high": 1093.0, "low": 1091.0, "close": 1000.0, "volume": 100, "oi": 1},
    ]
    st = cb.reconcile_and_insert(cb.chart_rows_to_bars(rows))
    assert st["mismatch_open"] == 1 and st["fixed"] == 1 and st["mismatch_other"] == 1
    assert st["mismatch"] == 2
    got = _rows(path, "SELECT substr(ts,12,5), open, low, volume, close, source FROM session_bars ORDER BY ts")
    assert got[0] == ("10:00", 1090.0, 1089.0, 100, 1090.5, "rt")
    assert got[1] == ("10:01", 1090.8, 1089.5, 180, 1091.5, "rt_chart_fix")   # close 유지
    assert got[2][5] == "rt"


# ────────────────────────────────────────────── ④ 따라잡기

def test_catchup_picks_short_days_and_skips_expiry(monkeypatch):
    counts = {"2026-10-14": 411, "2026-10-13": 411, "2026-10-12": 400,
              "2026-10-08": 388, "2026-10-07": 411}
    monkeypatch.setattr(db_utils, "count_session_bars", lambda d: counts.get(d, 0))
    days = cb.catchup_days(datetime.date(2026, 10, 15))
    assert datetime.date(2026, 10, 12) in days
    assert datetime.date(2026, 10, 8) not in days        # 만기일 — 만기 월물 사후 조회 불가
    assert datetime.date(2026, 10, 14) not in days


# ────────────────────────────────────────────── ⑤ main 배선

def _main_src():
    with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as f:
        return f.read()


def test_expiry_window_and_post_close_order():
    src = _main_src()
    assert "(datetime.time(15, 22), datetime.time(15, 39)) if _is_exp_t(now)" in src
    i = src.index("def _post_close_bar_sync")
    fn = src[i:i + 4000]
    a, b, c = fn.index("_bf_day(now.date())"), fn.index("catchup_days("), fn.index("_fill_raw(")
    assert a < b < c, "당일 보충 → 따라잡기 → raw 보충 순서"


def test_confirm_runs_before_shutdown_and_on_expiry():
    src = _main_src()
    i = src.index("def _auto_shutdown")
    blk = src[i:i + 900]
    assert "self._run_bargap_confirm(" in blk
    assert blk.index("self._run_bargap_confirm(") < blk.index("_qt_app.quit()") if "_qt_app.quit()" in blk else True
    assert "datetime.time(15, 22) if _is_exp_c(now) else datetime.time(15, 46)" in src


def test_confirm_runs_once():
    """스케줄러·종료 직전 두 곳에서 불려도 한 번만 남는다 — 플래그를 판정 **전에** 세운다."""
    src = _main_src()
    i = src.index("def _run_bargap_confirm")
    fn = src[i:i + 700]
    assert fn.index("if self._bargap_confirm_done:") < fn.index("self._bargap_confirm_done = True") \
        < fn.index("_bg_conf(")
