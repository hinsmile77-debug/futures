# -*- coding: utf-8 -*-
"""[MW0601 533차] 풀타임 세션 봉 적재(Phase 1) 불변식.

무엇을 고정하나
---------------
1. `classify_session` — 봉 ts → 세션 라벨. 만기일 15:20 경계, 체결유형코드 우선.
2. `CybosRealtimeData` — 헤더 28(체결유형코드)을 봉에 누적하되 **미수신은 None**.
3. `save_session_bar` — 스키마·NULL 규약(없는 키는 NULL, 0 아님).
4. `main._on_candle_closed` — 세션 적재 호출이 **모든 분기보다 앞**에 있다.
   15:09 봉이 force-exit 가드에 버려지던 결함의 재발 방지.

실행: pytest tests/test_533_session_bars.py
"""
import datetime
import os
import re
import sqlite3
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from utils import time_utils as tu  # noqa: E402
from utils import db_utils  # noqa: E402
from collection.cybos.realtime_data import CybosRealtimeData  # noqa: E402


# ── 1. classify_session ──────────────────────────────────────────────────────

def _d(h, m, day=(2026, 9, 4)):
    return datetime.datetime(day[0], day[1], day[2], h, m)


def test_classify_session_normal_day():
    # 2026-09-04(금) — 만기일 아님
    assert tu.classify_session(_d(8, 30)) == tu.SESSION_PRE_AUCTION
    assert tu.classify_session(_d(8, 45)) == tu.SESSION_PRE_MARKET
    assert tu.classify_session(_d(8, 59)) == tu.SESSION_PRE_MARKET
    assert tu.classify_session(_d(9, 0)) == tu.SESSION_REGULAR
    assert tu.classify_session(_d(15, 9)) == tu.SESSION_REGULAR      # 15:09 봉은 REGULAR
    assert tu.classify_session(_d(15, 10)) == tu.SESSION_POST_FORCE_EXIT
    assert tu.classify_session(_d(15, 34)) == tu.SESSION_POST_FORCE_EXIT
    assert tu.classify_session(_d(15, 35)) == tu.SESSION_CLOSE_AUCTION
    assert tu.classify_session(_d(15, 44)) == tu.SESSION_CLOSE_AUCTION
    assert tu.classify_session(_d(15, 45)) == tu.SESSION_CLOSE_FILL
    assert tu.classify_session(_d(15, 46)) == tu.SESSION_AFTER


def test_classify_session_expiry_day():
    exp = tu.get_monthly_expiry_date(2026, 9)
    day = (exp.year, exp.month, exp.day)
    assert tu.is_expiry_day(datetime.datetime(*day, 10, 0))
    assert tu.classify_session(_d(15, 15, day)) == tu.SESSION_POST_FORCE_EXIT
    assert tu.classify_session(_d(15, 20, day)) == tu.SESSION_EXPIRY_CLOSE
    assert tu.classify_session(_d(15, 21, day)) == tu.SESSION_AFTER
    assert tu.classify_session(_d(15, 40, day)) == tu.SESSION_AFTER   # 만기일엔 마감 단일가 없음


def test_classify_session_auction_code_overrides_time():
    assert tu.classify_session(_d(11, 0), tu.AUCTION_CODE_INTRADAY) == tu.SESSION_EXCHANGE_CB
    assert tu.classify_session(_d(15, 45), tu.AUCTION_CODE_CLOSE) == tu.SESSION_CLOSE_FILL
    # 시가단일가는 08:45 봉 안에 흡수 — PRE_MARKET 유지
    assert tu.classify_session(_d(8, 45), tu.AUCTION_CODE_OPEN) == tu.SESSION_PRE_MARKET
    # None(미수신)과 0(연속매매)은 둘 다 시각 분류
    assert tu.classify_session(_d(10, 0), None) == tu.SESSION_REGULAR
    assert tu.classify_session(_d(10, 0), 0) == tu.SESSION_REGULAR


def test_classify_session_off_day():
    assert tu.classify_session(datetime.datetime(2026, 9, 6, 10, 0)) == tu.SESSION_OFF  # 일요일


# ── 2. realtime_data 헤더 28 누적 ────────────────────────────────────────────

class _StubTick(object):
    def __init__(self, price, cum_vol, raw_time, auction=0, has_28=True):
        self._v = {1: price, 13: cum_vol, 14: 1000, 15: raw_time, 18: price + 0.02, 19: price,
                   20: 5, 21: 5, 22: 0, 23: 0, 24: "1", 30: "0"}
        if has_28:
            self._v[28] = auction
        self.has_28 = has_28

    def GetHeaderValue(self, idx):
        if idx == 28 and not self.has_28:
            raise Exception("no such header")
        return self._v.get(idx, 0)


class _StubAPI(object):
    pass


def _rt(closed):
    return CybosRealtimeData(api=_StubAPI(), code="A0569", on_candle_closed=closed.append)


def _now_times():
    """stale 판정(90초)에 안 걸리는 raw_time 2분치 — 현재 분과 다음 분."""
    t0 = datetime.datetime.now().replace(second=0, microsecond=0)
    t1 = t0 + datetime.timedelta(minutes=1)
    return t0.strftime("%H%M%S"), (t0 + datetime.timedelta(seconds=1)).strftime("%H%M%S"), \
        (t0 + datetime.timedelta(seconds=2)).strftime("%H%M%S"), t1.strftime("%H%M%S")


def test_auction_code_accumulates_in_bar():
    closed = []
    rt = _rt(closed)
    rt._last_cum_volume = 100
    rt._last_price = 1000.0
    a, b, c, d = _now_times()
    rt._handle_tick(_StubTick(1000.0, 101, a, auction=10))
    rt._handle_tick(_StubTick(1000.5, 102, b, auction=0))
    rt._handle_tick(_StubTick(1000.5, 103, c, auction=10))
    bar = rt.current_bar
    assert bar["auction_code"] == 10
    assert bar["auction_ticks"] == 2
    # 다음 분 → 봉 마감, 새 봉은 연속매매만 → auction_code 0 (받았음), ticks 0
    rt._handle_tick(_StubTick(1001.0, 104, d, auction=0))
    assert closed and closed[-1]["auction_code"] == 10 and closed[-1]["auction_ticks"] == 2
    assert rt.current_bar["auction_code"] == 0
    assert rt.current_bar["auction_ticks"] == 0


def test_auction_code_missing_header_stays_none():
    closed = []
    rt = _rt(closed)
    rt._last_cum_volume = 100
    rt._last_price = 1000.0
    a, b, _c, _d = _now_times()
    rt._handle_tick(_StubTick(1000.0, 101, a, has_28=False))
    rt._handle_tick(_StubTick(1000.0, 102, b, has_28=False))
    assert rt.current_bar["auction_code"] is None      # 미수신 ≠ 0
    assert rt.current_bar["auction_ticks"] is None
    assert rt._auction_field_warned is True            # 경고 1회


# ── 3. save_session_bar 스키마·NULL 규약 ──────────────────────────────────────

def test_save_session_bar_schema_and_nulls(monkeypatch):
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "raw_data_test.db")
    monkeypatch.setattr(db_utils, "RAW_DATA_DB", path)
    db_utils.init_raw_data_db()
    bar = {"ts": datetime.datetime(2026, 9, 4, 15, 45), "open": 1.0, "high": 2.0, "low": 0.5,
           "close": 1.5, "volume": 900, "auction_code": 30, "auction_ticks": 1}
    db_utils.save_session_bar(bar, tu.SESSION_CLOSE_FILL, "rt")
    bar2 = {"ts": "2026-09-04 15:09:00", "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0,
            "volume": 10}
    db_utils.save_session_bar(bar2, tu.SESSION_REGULAR)
    con = sqlite3.connect(path)
    rows = con.execute("SELECT ts, session, volume, auction_code, auction_ticks, buy_vol, source "
                       "FROM session_bars ORDER BY ts").fetchall()
    con.close()
    assert rows[0] == ("2026-09-04 15:09:00", "REGULAR", 10, None, None, None, "rt")
    assert rows[1] == ("2026-09-04 15:45:00", "CLOSE_FILL", 900, 30, 1, None, "rt")


def test_prune_includes_session_bars():
    src = open(os.path.join(_ROOT, "learning", "batch_retrainer.py"), encoding="utf-8").read()
    m = re.search(r"for table in \(([^)]*)\):", src)
    assert m and "session_bars" in m.group(1)


# ── 4. main._on_candle_closed 순서 불변식 ────────────────────────────────────

def test_on_candle_closed_persists_before_any_branch():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    start = src.index("def _on_candle_closed(self, candle: dict)")
    body = src[start:start + 4000]
    i_persist = body.index("self._persist_session_bar(candle)")
    i_pre = body.index("if is_pre_market(now):")
    i_open = body.index("if not is_market_open(now):")
    i_fe = body.index("if is_force_exit_time(now):")
    assert i_persist < i_pre < i_open < i_fe, "세션 적재는 프리장·장외·force-exit 분기보다 앞이어야 한다"
    # DBWriter 에 op 가 있고, daily_close 가 센티널 전에 플래그를 세운다
    assert 'elif op == "session_bar":' in src
    i_flag = src.index("self._db_writer_closed = True")
    i_sentinel = src.index("self._db_write_queue.put(None)  # DBWriter 종료 sentinel")
    assert i_flag < i_sentinel
    assert "self._db_writer_closed: bool = False" in src
