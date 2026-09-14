# -*- coding: utf-8 -*-
"""[MW0601 565차] 풀타임 수집 Phase 3 — 차트 TR 보충·로그 복구 불변식.

1. 차트 라벨 → ts 매핑: 라벨은 종료 시각(846 = 08:45 봉), `1545` 는 CLOSE_FILL(15:45).
2. 날짜별 근월물 코드: 만기일까지 그 달, 다음날부터 다음 달 (2026-09-10 만기 실측).
3. 보충은 기존 행을 덮지 않는다(INSERT OR IGNORE) — 실시간 봉의 bid/ask 가 우선.
4. 로그 복구 파서: `[BAR-CLOSE][CYBOS]` 줄 → 봉, 중복 ts 는 첫 출현.
5. main 의 차트 보충 훅은 08:41~08:44 창에만 있다(장중 BlockRequest 금지).

실행: conda run -n py37_32 python -m pytest tests/test_565_session_bars_backfill.py -q
"""
import datetime
import os
import sqlite3
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from collection.cybos import chart_backfill as cb  # noqa: E402
from utils import db_utils, time_utils as tu  # noqa: E402


def test_chart_label_is_bar_end_time():
    rows = [
        {"date": 20260911, "time": 846, "open": 1076.06, "high": 1076.1, "low": 1070.3, "close": 1070.5, "volume": 653, "oi": 1},
        {"date": 20260911, "time": 1535, "open": 1085.44, "high": 1085.9, "low": 1085.16, "close": 1085.28, "volume": 125, "oi": 1},
        {"date": 20260911, "time": 1545, "open": 1083.92, "high": 1083.92, "low": 1083.92, "close": 1083.92, "volume": 261, "oi": 1},
        {"date": 20260911, "time": 1510, "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1, "oi": 1},
    ]
    bars = cb.chart_rows_to_bars(rows)
    m = {ts: s for ts, s, _ in bars}
    assert m["2026-09-11 08:45:00"] == tu.SESSION_PRE_MARKET
    assert m["2026-09-11 15:34:00"] == tu.SESSION_POST_FORCE_EXIT
    assert m["2026-09-11 15:45:00"] == tu.SESSION_CLOSE_FILL
    assert m["2026-09-11 15:09:00"] == tu.SESSION_REGULAR
    assert [ts for ts, _, _ in bars] == sorted(ts for ts, _, _ in bars)


def test_mini_code_for_date_rolls_after_expiry():
    assert cb.mini_code_for_date(datetime.date(2026, 8, 3)) == "A0568"    # 8월물(만기 08-13) — 09-14 현재 조회 불가
    assert cb.mini_code_for_date(datetime.date(2026, 8, 14)) == "A0569"
    assert cb.mini_code_for_date(datetime.date(2026, 9, 10)) == "A0569"   # 만기일 당일
    assert cb.mini_code_for_date(datetime.date(2026, 9, 11)) == "A056A"
    assert cb.mini_code_for_date(datetime.date(2026, 12, 15)) == "A0571"


def test_prev_trading_day_skips_weekend():
    assert cb.prev_trading_day(datetime.date(2026, 9, 14)) == datetime.date(2026, 9, 11)


def test_insert_if_missing_never_overwrites_rt(monkeypatch):
    path = os.path.join(tempfile.mkdtemp(), "raw.db")
    monkeypatch.setattr(db_utils, "RAW_DATA_DB", path)
    db_utils.init_raw_data_db()
    rt = {"ts": datetime.datetime(2026, 9, 11, 15, 34), "open": 1085.44, "high": 1085.9, "low": 1085.16,
          "close": 1085.28, "volume": 125, "bid1": 1085.2, "tick_count": 111}
    db_utils.save_session_bar(rt, tu.SESSION_POST_FORCE_EXIT, "rt")
    chart = {"ts": datetime.datetime(2026, 9, 11, 15, 34), "open": 9, "high": 9, "low": 9, "close": 9, "volume": 9}
    assert db_utils.insert_session_bar_if_missing(chart, tu.SESSION_POST_FORCE_EXIT, "chart_backfill") is False
    fill = {"ts": datetime.datetime(2026, 9, 11, 15, 45), "open": 1083.92, "high": 1083.92, "low": 1083.92,
            "close": 1083.92, "volume": 261, "oi": 52941}
    assert db_utils.insert_session_bar_if_missing(fill, tu.SESSION_CLOSE_FILL, "chart_backfill") is True
    con = sqlite3.connect(path)
    rows = con.execute("SELECT ts, source, bid1, close FROM session_bars ORDER BY ts").fetchall()
    con.close()
    assert rows == [("2026-09-11 15:34:00", "rt", 1085.2, 1085.28), ("2026-09-11 15:45:00", "chart_backfill", None, 1083.92)]

    # reconcile: 기존 행과 불일치는 세기만, 없는 행만 삽입
    bars = cb.chart_rows_to_bars([
        {"date": 20260911, "time": 1535, "open": 1085.44, "high": 1085.9, "low": 1085.16, "close": 1085.28, "volume": 125, "oi": 1},
        {"date": 20260911, "time": 1534, "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 3, "oi": 1},
    ])
    st = cb.reconcile_and_insert(bars)
    assert st == {"chart": 2, "existing": 1, "inserted": 1, "mismatch": 0, "mismatch_ts": [], "open_fixed": 0}
    bars2 = cb.chart_rows_to_bars([
        {"date": 20260911, "time": 1535, "open": 1085.44, "high": 1085.9, "low": 1085.16, "close": 1000.0, "volume": 125, "oi": 1},
    ])
    st2 = cb.reconcile_and_insert(bars2)
    assert st2["mismatch"] == 1 and st2["mismatch_ts"][0][1] == ["close"] and st2["inserted"] == 0

    # 08:45 봉만 차트 O/H/L/V 로 보정(close 유지), source='rt_chart_open'. 다른 봉은 보정 안 함.
    db_utils.save_session_bar({"ts": datetime.datetime(2026, 9, 11, 8, 45), "open": 1072.72, "high": 1072.82,
                               "low": 1070.3, "close": 1070.5, "volume": 330, "bid1": 1070.4},
                              tu.SESSION_PRE_MARKET, "rt")
    st3 = cb.reconcile_and_insert(cb.chart_rows_to_bars([
        {"date": 20260911, "time": 846, "open": 1076.06, "high": 1076.1, "low": 1070.3, "close": 1070.5, "volume": 653, "oi": 1},
    ]))
    assert st3["open_fixed"] == 1 and st3["mismatch"] == 0
    con = sqlite3.connect(path)
    row = con.execute("SELECT open, high, volume, close, bid1, source FROM session_bars WHERE ts='2026-09-11 08:45:00'").fetchone()
    con.close()
    assert row == (1076.06, 1076.1, 653, 1070.5, 1070.4, "rt_chart_open")


def test_log_recovery_parser_first_occurrence_wins(tmp_path, monkeypatch):
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import session_bars_from_logs as sl
    lines = [
        "2026-08-04 15:09:50 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=15:08 O=1 H=1 L=1 C=1 V=1\n",
        "2026-08-04 15:14:50 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=15:14 O=995.94 H=997.16 L=995.94 C=996.84 V=178\n",
        "2026-08-04 15:14:55 [WARNING] SYSTEM: [BAR-CLOSE][DUPLICATE] ts=15:14 ...\n",
        "2026-08-04 15:14:56 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=15:14 O=0 H=0 L=0 C=0 V=0\n",
        "2026-08-05 15:15:50 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=15:15 O=2 H=2 L=2 C=2 V=2\n",
    ]
    monkeypatch.setattr(sl, "iter_log_lines", lambda day: iter(lines))
    bars = sl.parse_bars(datetime.date(2026, 8, 4), datetime.time(15, 8))
    assert len(bars) == 1
    ts, session, bar = bars[0]
    assert ts == "2026-08-04 15:14:00" and session == tu.SESSION_POST_FORCE_EXIT
    assert bar["close"] == 996.84 and bar["volume"] == 178


def test_main_chart_backfill_hook_window():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("backfill_day(_prev)")
    block = src[i - 1500:i]
    assert "datetime.time(8, 41) <= now.time() < datetime.time(8, 44)" in block
    assert "self._chart_backfill_done: bool = False" in src
