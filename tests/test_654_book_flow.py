# -*- coding: utf-8 -*-
"""[MW0601 654차] 호가 흐름 분해(체결 / 취소 하한 / 신규 하한) 회귀 가드.

배경
    `docs/미륵이고도화3/호가깊이/주문취소율_수집가능성_조사_MW0601-20261002.md` —
    두꺼운 매도벽이 체결로 소화됐는지 취소로 사라졌는지 구분할 수단이 없었다.
    Cybos 는 MBO 를 주지 않으므로 MBP 스냅샷 쌍 + 체결로 **하한**을 추론한다.

고정하는 것
    · 항등식 ΔQ = 신규 − 취소 − 체결 에서 하한이 맞게 나온다
    · 5단 창 밖으로 밀려난 잔량을 취소로 세지 않는다(조사 문서 §5-4)
    · 건수는 유효할 때만 쓴다 — 0 으로 비어 오면 미계측(계측 4원칙 ②)
    · 체결 귀속 항등식 ask_exec + bid_exec + unmatched == trade (④⑤)
    · 미계측 봉은 NULL, 키 없는 봉은 행 자체를 안 쓴다
    · 소비 0 — 진입·사이징 경로가 읽지 않는다
"""
from __future__ import annotations

import io
import os
import random
import sqlite3
import sys
import tempfile
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from collection.cybos.book_flow import (  # noqa: E402
    BookFlowEstimator, BookSnapshot, counts_valid,
)

ASK = [101.0, 101.02, 101.04, 101.06, 101.08]
BID = [100.98, 100.96, 100.94, 100.92, 100.90]


def _snap(ask_p=ASK, ask_q=(10, 2, 2, 2, 2), bid_p=BID, bid_q=(3, 3, 3, 3, 3),
          ask_n=None, bid_n=None):
    return BookSnapshot(list(ask_p), list(ask_q), list(bid_p), list(bid_q),
                        None if ask_n is None else list(ask_n),
                        None if bid_n is None else list(bid_n))


def _pair(s0, s1, trades=()):
    est = BookFlowEstimator()
    assert est.on_snapshot(s0) is None          # 첫 스냅샷은 쌍이 없다
    for p, q, side in trades:
        est.on_trade(p, q, side)
    return est.on_snapshot(s1)


# ── 순수 분해 ────────────────────────────────────────────────────────────────
def test_pure_execution_is_not_cancel():
    """매도 1호가 10 → 6, 그 사이 매수체결 4 — 전부 체결, 취소 0."""
    out = _pair(_snap(), _snap(ask_q=(6, 2, 2, 2, 2)), [(101.0, 4, "BUY")])
    assert out["ask_exec_qty"] == 4
    assert out["ask_cancel_qty_lb"] == 0 and out["ask_add_qty_lb"] == 0
    assert out["exec_unmatched_qty"] == 0


def test_pure_cancel_without_trades():
    """체결 없이 10 → 4 — 취소 하한 6."""
    out = _pair(_snap(), _snap(ask_q=(4, 2, 2, 2, 2)))
    assert out["ask_cancel_qty_lb"] == 6 and out["ask_exec_qty"] == 0


def test_add_lower_bound():
    """체결 2 가 났는데 잔량은 10 → 11 — 신규 ≥ 3."""
    out = _pair(_snap(), _snap(ask_q=(11, 2, 2, 2, 2)), [(101.0, 2, "BUY")])
    assert out["ask_add_qty_lb"] == 3 and out["ask_cancel_qty_lb"] == 0


def test_wall_vanishing_inside_window_splits_exec_and_cancel():
    """매도벽(101.00, 10계약)이 사라지고 호가가 한 틱 올라감, 그 사이 체결 3.

    101.00 은 새 스냅샷에서도 창 안(최우선보다 안쪽)이라 잔량 0 으로 관측된다 ⇒
    체결 3 + 취소 하한 7. 새로 나타난 101.10 은 이전 창 밖이라 신규로 세지 않는다.
    """
    cur_ask = [101.02, 101.04, 101.06, 101.08, 101.10]
    out = _pair(_snap(), _snap(ask_p=cur_ask, ask_q=(2, 2, 2, 2, 5)),
                [(101.0, 3, "BUY")])
    assert out["ask_exec_qty"] == 3
    assert out["ask_cancel_qty_lb"] == 7
    assert out["ask_add_qty_lb"] == 0           # 101.10 의 5 는 창 밖에서 들어온 것


def test_level_pushed_out_of_window_is_not_cancel():
    """매수 호가가 한 틱 올라 100.90 이 창 밖으로 밀려남 — 취소로 세지 않는다."""
    cur_bid = [101.00, 100.98, 100.96, 100.94, 100.92]
    out = _pair(_snap(ask_p=[101.02, 101.04, 101.06, 101.08, 101.10]),
                _snap(ask_p=[101.02, 101.04, 101.06, 101.08, 101.10],
                      bid_p=cur_bid, bid_q=(4, 3, 3, 3, 3)))
    assert out["bid_cancel_qty_lb"] == 0
    assert out["bid_add_qty_lb"] == 4           # 101.00 신규 매수 (이전 창 안, 잔량 0)


def test_count_based_cancel_lower_bound():
    """건수 5 → 2, 체결 1계약 ⇒ 체결로 지워진 주문 ≤ 1 ⇒ 취소 건수 ≥ 2."""
    s0 = _snap(ask_q=(10, 2, 2, 2, 2), ask_n=(5, 1, 1, 1, 1), bid_n=(1, 1, 1, 1, 1))
    s1 = _snap(ask_q=(9, 2, 2, 2, 2), ask_n=(2, 1, 1, 1, 1), bid_n=(1, 1, 1, 1, 1))
    out = _pair(s0, s1, [(101.0, 1, "BUY")])
    assert out["cnt_ok"] is True
    assert out["ask_cancel_cnt_lb"] == 2
    # 잔량 기준으로는 10→9 가 체결 1로 전부 설명된다 — 건수가 더 많은 것을 본다
    assert out["ask_cancel_qty_lb"] == 0


def test_zero_counts_are_unmeasured_not_zero():
    """원천이 건수를 0 으로 비워 보내면 그 스냅샷 건수는 버린다(계측 4원칙 ②)."""
    assert counts_valid([3, 2], [0, 0]) is False
    assert counts_valid([3, 2], [4, 1]) is False      # 건수 > 잔량은 모순
    assert counts_valid([3, 2], [2, 1]) is True
    s0 = _snap(ask_n=(0, 0, 0, 0, 0), bid_n=(0, 0, 0, 0, 0))
    out = _pair(s0, _snap(ask_q=(4, 2, 2, 2, 2), ask_n=(1, 1, 1, 1, 1),
                          bid_n=(1, 1, 1, 1, 1)))
    assert out["cnt_ok"] is False
    assert out["ask_cancel_qty_lb"] == 6              # 잔량 분해는 계속된다


def test_one_sided_snapshot_breaks_chain_and_drops_trades():
    est = BookFlowEstimator()
    est.on_trade(101.0, 5, "BUY")
    assert est.on_snapshot(_snap()) is None
    assert est.dropped_trade_qty == 5                 # 첫 스냅샷 이전 체결은 귀속 불가
    est.on_trade(101.0, 2, "BUY")
    assert est.on_snapshot(_snap(bid_q=(0, 0, 0, 0, 0))) is None
    assert est.broken_chains == 1 and est.dropped_trade_qty == 7
    assert est.on_snapshot(_snap()) is None           # 끊긴 뒤 첫 스냅샷도 쌍 없음


def test_unknown_side_trade_attributed_by_mid():
    out = _pair(_snap(), _snap(bid_q=(1, 3, 3, 3, 3)), [(100.98, 2, None)])
    assert out["bid_exec_qty"] == 2 and out["bid_cancel_qty_lb"] == 0


def test_identity_fuzz():
    """무작위 쌍에서도 항등식·비음수가 깨지지 않는다."""
    rnd = random.Random(654)
    for _ in range(500):
        sh_a, sh_b = rnd.randint(-2, 2), rnd.randint(-2, 2)
        a0 = [101.0 + 0.02 * i for i in range(5)]
        b0 = [100.98 - 0.02 * i for i in range(5)]
        a1 = [p + 0.02 * sh_a for p in a0]
        b1 = [p + 0.02 * sh_b for p in b0]
        if min(a1) <= max(b1):
            continue
        q = lambda: [rnd.randint(1, 20) for _ in range(5)]
        n0a, n0b, n1a, n1b = q(), q(), q(), q()
        s0 = BookSnapshot(a0, n0a, b0, n0b, [max(1, x // 2) for x in n0a],
                          [max(1, x // 2) for x in n0b])
        s1 = BookSnapshot(a1, n1a, b1, n1b, [max(1, x // 2) for x in n1a],
                          [max(1, x // 2) for x in n1b])
        trades = [(rnd.choice(a0 + b0), rnd.randint(1, 5),
                   rnd.choice(["BUY", "SELL", None])) for _ in range(rnd.randint(0, 6))]
        out = _pair(s0, s1, trades)
        assert out["trade_qty"] == sum(t[1] for t in trades)
        assert (out["ask_exec_qty"] + out["bid_exec_qty"]
                + out["exec_unmatched_qty"]) == out["trade_qty"]
        for k, v in out.items():
            if k != "cnt_ok":
                assert v >= 0, (k, v)


# ── 실시간 핸들러 배선 ─────────────────────────────────────────────────────────
class _FakeJpBid(object):
    """`CpSysDib.FutureJpBid` 헤더 전량(0–35) 흉내 — 확장 필드 포함."""

    def __init__(self, ask_p, ask_q, bid_p, bid_q, ask_n=None, bid_n=None,
                 ask_full=None, bid_full=None):
        v = {}
        for i in range(5):
            v[2 + i], v[7 + i] = ask_p[i], ask_q[i]
            v[19 + i], v[24 + i] = bid_p[i], bid_q[i]
            if ask_n is not None:
                v[13 + i] = ask_n[i]
            if bid_n is not None:
                v[30 + i] = bid_n[i]
        if ask_n is not None:
            v[18] = sum(ask_n) + 50
            v[35] = sum(bid_n) + 50
        v[12] = ask_full if ask_full is not None else sum(ask_q) + 400
        v[29] = bid_full if bid_full is not None else sum(bid_q) + 400
        self._v = v

    def GetHeaderValue(self, idx):
        return self._v.get(idx, 0)


def _make_rt():
    from collection.cybos.book_flow import BookFlowEstimator as _BFE
    from collection.cybos.realtime_data import CybosRealtimeData
    rt = CybosRealtimeData.__new__(CybosRealtimeData)   # __init__ 은 COM 을 탄다
    rt._last_bid1 = rt._last_ask1 = 0.0
    rt._last_bid_qty = rt._last_ask_qty = 0
    rt._book_oneside_count = 0
    rt._last_hoga_snapshot = {"bid_prices": [], "ask_prices": [],
                              "bid_qtys": [], "ask_qtys": []}
    rt._hoga_event_count = 0
    rt._rt_code = "TEST"
    rt._on_hoga = None
    rt._book_flow = _BFE()
    rt._bf_ext_fail_warned = rt._bf_cnt_invalid_warned = False
    rt._bf_cnt_invalid_count = rt._bf_orphan_pairs = 0
    rt._current_bar = {"ts": datetime(2026, 10, 2, 10, 0),
                       "book_bid_tot": None, "book_ask_tot": None,
                       "book_bid_max": None, "book_ask_max": None,
                       "book_snaps": 0, "_book_bid_sum": 0, "_book_ask_sum": 0,
                       "bf_pairs": 0, "bf_cnt_pairs": 0,
                       "bf_full_snaps": 0, "bf_cnt_snaps": 0}
    return rt


def test_handle_hoga_accumulates_flow_on_bar():
    rt = _make_rt()
    n = (2, 1, 1, 1, 1)
    rt._handle_hoga(_FakeJpBid(ASK, [10, 2, 2, 2, 2], BID, [3] * 5, n, (1,) * 5))
    rt._book_flow.on_trade(101.0, 2, "BUY")             # _handle_tick 이 하는 일
    rt._handle_hoga(_FakeJpBid(ASK, [5, 2, 2, 2, 2], BID, [3] * 5, (1, 1, 1, 1, 1), (1,) * 5))
    b = rt._current_bar
    assert b["bf_pairs"] == 1 and b["bf_cnt_pairs"] == 1
    assert b["bf_ask_exec_qty"] == 2 and b["bf_ask_cancel_qty_lb"] == 3
    assert b["bf_trade_qty"] == 2 and b["bf_exec_unmatched_qty"] == 0
    assert b["bf_full_snaps"] == 2 and b["bf_cnt_snaps"] == 2
    assert b["_bf_ask_full_sum"] == (18 + 400) + (13 + 400)


def test_handle_hoga_without_counts_keeps_qty_flow():
    """원천이 건수 헤더를 0 으로 주면 건수 열은 미계측, 잔량 분해는 계속."""
    rt = _make_rt()
    rt._handle_hoga(_FakeJpBid(ASK, [10, 2, 2, 2, 2], BID, [3] * 5))
    rt._handle_hoga(_FakeJpBid(ASK, [4, 2, 2, 2, 2], BID, [3] * 5))
    b = rt._current_bar
    assert b["bf_pairs"] == 1 and b["bf_cnt_pairs"] == 0
    assert b["bf_ask_cancel_qty_lb"] == 6
    assert "bf_ask_cancel_cnt_lb" not in b
    assert b["bf_cnt_snaps"] == 0
    assert rt._bf_cnt_invalid_count == 2 and rt._bf_cnt_invalid_warned


def test_full_depth_rejected_when_less_than_five_level_sum():
    rt = _make_rt()
    rt._handle_hoga(_FakeJpBid(ASK, [10, 2, 2, 2, 2], BID, [3] * 5, ask_full=5))
    assert rt._current_bar["bf_full_snaps"] == 0


def test_header_indices_match_cybos_spec():
    """헤더 번호는 cybosplus.github.io FutureJpBid 명세에서 왔다 — 바뀌면 이 테스트가 깨진다."""
    src = io.open(os.path.join(ROOT, "collection", "cybos", "realtime_data.py"),
                  encoding="utf-8").read()
    for frag in ("GetHeaderValue(12)", "(13, 14, 15, 16, 17)", "GetHeaderValue(18)",
                 "GetHeaderValue(29)", "(30, 31, 32, 33, 34)", "GetHeaderValue(35)"):
        assert frag in src, frag


# ── DB ──────────────────────────────────────────────────────────────────────
def test_book_flow_row_null_rules():
    from utils.db_utils import book_flow_row
    assert book_flow_row({"ts": "x"}) is None                       # 키 없음 → 행 없음
    row = book_flow_row({"bf_pairs": 0, "bf_cnt_pairs": 0,
                         "bf_full_snaps": 0, "bf_cnt_snaps": 0})
    assert row[0] == 0 and all(v is None for v in row[2:12])        # 흐름 값열 NULL
    assert row[12] == 0 and row[13] is None and row[14] is None


def test_session_bar_writes_book_flow_row():
    import utils.db_utils as D
    tmp = tempfile.mkdtemp()
    orig = D.RAW_DATA_DB
    D.RAW_DATA_DB = os.path.join(tmp, "raw_data.db")
    try:
        D.init_raw_data_db()
        bar = {"ts": datetime(2026, 10, 2, 10, 0), "open": 1, "high": 1, "low": 1,
               "close": 1, "volume": 7,
               "bf_pairs": 3, "bf_cnt_pairs": 0, "bf_trade_qty": 5,
               "bf_exec_unmatched_qty": 1, "bf_ask_exec_qty": 4, "bf_bid_exec_qty": 0,
               "bf_ask_cancel_qty_lb": 6, "bf_ask_add_qty_lb": 2,
               "bf_bid_cancel_qty_lb": 0, "bf_bid_add_qty_lb": 1,
               "bf_ask_cancel_cnt_lb": 9,                  # cnt_pairs=0 → NULL 이어야
               "bf_full_snaps": 2, "_bf_ask_full_sum": 900, "_bf_bid_full_sum": 1000,
               "bf_cnt_snaps": 0}
        D.save_session_bar(bar, "REGULAR", "rt")
        D.save_session_bar({"ts": datetime(2026, 10, 2, 10, 1), "open": 1, "high": 1,
                            "low": 1, "close": 1, "volume": 1}, "REGULAR", "chart_backfill")
        con = sqlite3.connect(D.RAW_DATA_DB)
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM book_flow_bars").fetchall()
        con.close()
        assert len(rows) == 1                                       # 키 없는 봉은 행 없음
        r = rows[0]
        assert r["pairs"] == 3 and r["ask_cancel_qty_lb"] == 6
        assert r["ask_exec_qty"] + r["bid_exec_qty"] + r["exec_unmatched_qty"] == r["trade_qty"]
        assert r["ask_cancel_cnt_lb"] is None
        assert r["ask_full_avg"] == 450.0 and r["ask_cnt5_avg"] is None
    finally:
        D.RAW_DATA_DB = orig


def test_book_flow_not_consumed_by_entry_path():
    """소비 0 — 진입·사이징·모델 경로가 흐름 열을 읽지 않는다."""
    hits = []
    for root in ("strategy", "execution", "risk", "model"):
        base = os.path.join(ROOT, root)
        if not os.path.isdir(base):
            continue
        for dp, _dn, fn in os.walk(base):
            if "__pycache__" in dp:
                continue
            for f in fn:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(dp, f)
                with io.open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    src = fh.read()
                for key in ("book_flow", "_cancel_qty_lb", "_cancel_cnt_lb", "bf_pairs"):
                    if key in src:
                        hits.append("%s:%s" % (p, key))
    assert not hits, "섀도 열이 진입 경로에서 소비됨: %s" % hits
