# -*- coding: utf-8 -*-
"""[MW0601 552차] 호가 5단 총잔량 적재 + GP range/dir 피처 회귀 가드.

배경
    JPG 차트 3일 분석에서 「(호가)총 순매수 잔량 비율」이 가장 유망해 보였으나
    211거래일 실데이터 검증에서 **DB 에 원천이 없어 확인 자체가 불가능**했다.
    호가 5단은 `_handle_hoga` 가 이미 파싱해 두고 1단만 봉에 실어 왔다 —
    나머지 4단은 debug 로그로 흘러가 버려졌다. 552차는 그 4단을 적재한다.

    같은 검증에서 `gp_range`(=n봉 종가 레인지)는 중첩·다중검정 보정 후
    **유일하게 생존한 축**이었다(비중첩 t=-3.55). 그래서 함께 노출한다.

규약
    · 미계측은 NULL 이다. `book_snaps=0` 인 봉의 book_* 4열은 전부 NULL
      (452차 앵커 4열 · 451차 program_* 유령 피처 재발 방지).
    · 소비 0 — 진입·사이징 경로에 붙이지 않는다(540차 GP 교차와 동일).
"""
from __future__ import annotations

import os
import sqlite3
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── GP range / dir ───────────────────────────────────────────────────────────
def test_gp_range_dir_matches_spec_formula():
    """구현명세 산식과 일치: GB=(C−min)/C×200, GS=(max−C)/C×200, range=합, dir=차."""
    from features.feature_builder import compute_gp_cross_features
    closes = [1000.0 + i * 0.5 for i in range(20)] + [1005.0]
    out = compute_gp_cross_features(closes, atr=1.0, period=20)
    c, lo, hi = closes[-1], min(closes[-20:]), max(closes[-20:])
    exp_b, exp_s = (c - lo) / c * 200.0, (hi - c) / c * 200.0
    assert abs(out["gp_buy_20"] - exp_b) < 1e-9
    assert abs(out["gp_sell_20"] - exp_s) < 1e-9
    assert abs(out["gp_range_20"] - (exp_b + exp_s)) < 1e-9
    assert abs(out["gp_dir_20"] - (exp_b - exp_s)) < 1e-9


def test_gp_range_identity_and_nonnegative():
    """항등식 gp_range == gp_buy + gp_sell 이고 항상 0 이상."""
    import random
    from features.feature_builder import compute_gp_cross_features
    random.seed(552)
    for _ in range(200):
        cs = [1000.0 + random.uniform(-5, 5) for _ in range(25)]
        o = compute_gp_cross_features(cs, atr=1.0, period=20)
        assert abs(o["gp_range_20"] - (o["gp_buy_20"] + o["gp_sell_20"])) < 1e-9
        assert o["gp_range_20"] >= -1e-12


def test_gp_warmup_does_not_fake_values():
    """워밍업 구간은 0 + ready=False — 0 으로 위장하지 않는다(계측 4원칙 ②)."""
    from features.feature_builder import compute_gp_cross_features
    w = compute_gp_cross_features([1000.0] * 5, atr=1.0, period=20)
    assert w["gp_ready_20"] is False
    assert w["gp_range_20"] == 0.0 and w["gp_dir_20"] == 0.0


# ── 호가 5단 총잔량 ───────────────────────────────────────────────────────────
class _FakeHoga(object):
    """`CpSysDib.FutureJpBid` 헤더 배치를 흉내낸다 (2~11 매도, 19~28 매수)."""

    def __init__(self, ask_p, ask_q, bid_p, bid_q):
        self._v = {}
        for i, idx in enumerate((2, 3, 4, 5, 6)):
            self._v[idx] = ask_p[i]
        for i, idx in enumerate((7, 8, 9, 10, 11)):
            self._v[idx] = ask_q[i]
        for i, idx in enumerate((19, 20, 21, 22, 23)):
            self._v[idx] = bid_p[i]
        for i, idx in enumerate((24, 25, 26, 27, 28)):
            self._v[idx] = bid_q[i]

    def GetHeaderValue(self, idx):
        return self._v.get(idx, 0)


def _make_rt():
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
    rt._current_bar = {"book_bid_tot": None, "book_ask_tot": None,
                       "book_snaps": 0, "_book_bid_sum": 0, "_book_ask_sum": 0}
    return rt


def test_handle_hoga_sums_five_levels():
    """5단 합계가 봉에 누적되고 스냅샷 수가 세어진다."""
    rt = _make_rt()
    rt._handle_hoga(_FakeHoga([101, 102, 103, 104, 105], [10, 20, 30, 40, 50],
                              [100, 99, 98, 97, 96], [11, 21, 31, 41, 51]))
    b = rt._current_bar
    assert b["book_ask_tot"] == 150 and b["book_bid_tot"] == 155
    assert b["book_snaps"] == 1
    rt._handle_hoga(_FakeHoga([101, 102, 103, 104, 105], [1, 2, 3, 4, 5],
                              [100, 99, 98, 97, 96], [5, 4, 3, 2, 1]))
    assert b["book_ask_tot"] == 15 and b["book_bid_tot"] == 15   # 마지막 스냅샷
    assert b["book_snaps"] == 2
    assert b["_book_bid_sum"] == 170 and b["_book_ask_sum"] == 165


def test_book_depth_cols_null_when_never_received():
    """호가를 한 번도 못 받은 봉은 4열 NULL · snaps=0 — 0 으로 위장하지 않는다."""
    from utils.db_utils import _book_depth_cols
    assert _book_depth_cols({"book_snaps": 0}) == (None, None, None, None, 0)
    assert _book_depth_cols({}) == (None, None, None, None, 0)


def test_book_depth_cols_average():
    """평균 = 봉내 합계 ÷ 스냅샷 수."""
    from utils.db_utils import _book_depth_cols
    got = _book_depth_cols({"book_bid_tot": 120, "book_ask_tot": 80,
                            "_book_bid_sum": 300, "_book_ask_sum": 200,
                            "book_snaps": 3})
    assert got[0] == 120 and got[1] == 80
    assert abs(got[2] - 100.0) < 1e-9 and abs(got[3] - (200 / 3.0)) < 1e-9
    assert got[4] == 3


def test_schema_has_book_columns_and_roundtrip():
    """두 테이블 모두 5열을 갖고, 저장→조회 왕복에서 NULL 규약이 유지된다."""
    import utils.db_utils as D
    tmp = tempfile.mkdtemp()
    orig = D.RAW_DATA_DB
    D.RAW_DATA_DB = os.path.join(tmp, "raw_data.db")
    try:
        D.init_raw_data_db()
        base = dict(ts="2026-09-10 09:00:00", open=100.0, high=101.0,
                    low=99.0, close=100.5, volume=10)
        hit = dict(base, book_bid_tot=120, book_ask_tot=80,
                   _book_bid_sum=300, _book_ask_sum=200, book_snaps=3)
        miss = dict(base, ts="2026-09-10 09:01:00", book_snaps=0)
        D.save_candle(hit); D.save_candle(miss)
        D.save_session_bar(hit, "REGULAR", "rt")
        D.save_session_bar(miss, "REGULAR", "rt")
        con = sqlite3.connect(D.RAW_DATA_DB)
        for t in ("raw_candles", "session_bars"):
            cols = [r[1] for r in con.execute("PRAGMA table_info(%s)" % t)]
            for c in ("book_bid_tot", "book_ask_tot", "book_bid_avg",
                      "book_ask_avg", "book_snaps"):
                assert c in cols, "%s 에 %s 없음" % (t, c)
            q = ("SELECT book_bid_tot,book_ask_tot,book_bid_avg,book_ask_avg,"
                 "book_snaps FROM %s WHERE ts=?" % t)
            assert con.execute(q, (hit["ts"],)).fetchone() == (120, 80, 100.0, 200 / 3.0, 3)
            assert con.execute(q, (miss["ts"],)).fetchone() == (None, None, None, None, 0)
        con.close()
    finally:
        D.RAW_DATA_DB = orig


def test_handle_hoga_ignores_one_sided_snapshot():
    """[552차 후속 / 결함3] 한쪽 호가만 온 스냅샷은 세지 않는다.

    막으려는 것: 종전 구현은 `_bid_tot > 0 or _ask_tot > 0` 으로 통과시키고
    양변 모두에 **직전값 캐시**를 실었다. 세션 첫 스냅샷이 한쪽만 오면 반대쪽에
    초기값 0 이 실려 "잔량 0" 과 "미수신" 이 다시 같아진다 — 이 파일이 막으려던
    바로 그 혼동이다. 그리고 평균 누적에 stale 값이 섞인다.
    """
    rt = _make_rt()
    # 매수만 유효 (매도 5단 전부 0) → 스냅샷으로 세지 않는다
    rt._handle_hoga(_FakeHoga([0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                              [100, 99, 98, 97, 96], [11, 21, 31, 41, 51]))
    b = rt._current_bar
    assert b["book_snaps"] == 0
    assert b["book_bid_tot"] is None and b["book_ask_tot"] is None,         "한쪽만 온 스냅샷이 반대편에 0(또는 stale)을 실었다"
    assert rt._book_oneside_count == 1, "탈락 개수를 세지 않으면 조용히 사라진다"

    # 양변 유효 스냅샷이 오면 그때부터 정상 계수
    rt._handle_hoga(_FakeHoga([101, 102, 103, 104, 105], [10, 20, 30, 40, 50],
                              [100, 99, 98, 97, 96], [11, 21, 31, 41, 51]))
    assert b["book_snaps"] == 1
    assert b["book_bid_tot"] == 155 and b["book_ask_tot"] == 150
    assert b["_book_bid_sum"] == 155 and b["_book_ask_sum"] == 150,         "stale 값이 평균 누적에 섞였다"


def test_production_write_path_persists_book_depth():
    """[552차 후속 / 결함1] 프로덕션 경로 `save_candle_and_features` 가 5열을 싣는다.

    🔴 `save_candle()` 은 **프로덕션에서 호출되지 않는다** — main.py 의 raw_candles
    쓰기 3곳(DB 워커·프리마켓·매분 파이프라인)이 전부
    `save_candle_and_features()` 다. 초판은 `save_candle()` 만 패치해서
    `raw_candles.book_*` 가 영구 NULL 이었다. TOX `spread_extreme_shadow`·
    FP-CRITICAL PSI 와 같은 「계산은 하는데 아무도 안 받는」 죽은 계측이다.
    """
    import utils.db_utils as D
    tmp = tempfile.mkdtemp()
    orig = D.RAW_DATA_DB
    D.RAW_DATA_DB = os.path.join(tmp, "raw_data.db")
    try:
        D.init_raw_data_db()
        bar = dict(ts="2026-09-10 09:00:00", open=100.0, high=101.0, low=99.0,
                   close=100.5, volume=10, book_bid_tot=155, book_ask_tot=150,
                   _book_bid_sum=310, _book_ask_sum=300, book_snaps=2)
        miss = dict(bar, ts="2026-09-10 09:01:00", book_snaps=0,
                    book_bid_tot=None, book_ask_tot=None,
                    _book_bid_sum=0, _book_ask_sum=0)
        D.save_candle_and_features(bar, bar["ts"], {"x": 1.0})
        D.save_candle_and_features(miss, miss["ts"], {"x": 1.0})
        con = sqlite3.connect(D.RAW_DATA_DB)
        q = ("SELECT book_bid_tot,book_ask_tot,book_bid_avg,book_ask_avg,book_snaps"
             " FROM raw_candles WHERE ts=?")
        assert con.execute(q, (bar["ts"],)).fetchone() == (155, 150, 155.0, 150.0, 2)
        assert con.execute(q, (miss["ts"],)).fetchone() == (None, None, None, None, 0)
        con.close()
    finally:
        D.RAW_DATA_DB = orig


def test_every_raw_candles_writer_includes_book_columns():
    """[552차 후속 / 결함1] `raw_candles` 로 가는 **모든** INSERT 가 5열을 싣는다.

    이 테스트가 막는 것은 오타가 아니라 **경로 추가**다. 초판의 실패는 쓰기
    함수가 둘인데 하나만 고친 것이었다. 세 번째가 생겨도 여기서 걸린다.
    """
    import io as _io
    import re
    src = _io.open(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "utils", "db_utils.py"),
        encoding="utf-8").read()
    stmts = re.findall(r"INSERT(?:\s+OR\s+REPLACE)?\s+INTO\s+raw_candles(.{0,700}?)VALUES",
                       src, re.S)
    assert stmts, "raw_candles INSERT 문을 찾지 못했다 — 이 가드가 무력화됐다"
    for i, body in enumerate(stmts):
        for col in ("book_bid_tot", "book_ask_tot", "book_bid_avg",
                    "book_ask_avg", "book_snaps"):
            assert col in body, "raw_candles INSERT #%d 에 %s 누락" % (i + 1, col)


def test_recovered_bar_roundtrip_preserves_avg():
    """[552차 후속 / 결함4] DB 행에서 되살린 봉을 재저장해도 평균이 사라지지 않는다.

    `main.py:_bar_from_raw_candle_row` 는 `row.keys()` 자동 승계라 **공개 컬럼만**
    들고 온다(사설 누적키 `_book_bid_sum` 은 없다). 사설키만 보면 그 봉이
    `book_snaps=N` 인데 `book_bid_avg=NULL` 인 모순 행으로 덮인다 — 452차가
    `INSERT OR REPLACE` 로 55봉을 잃은 것과 같은 자리다.
    """
    from utils.db_utils import _book_depth_cols
    recovered = {"book_bid_tot": 155, "book_ask_tot": 150,
                 "book_bid_avg": 155.0, "book_ask_avg": 150.0, "book_snaps": 2}
    assert _book_depth_cols(recovered) == (155, 150, 155.0, 150.0, 2)
    # 사설키가 있으면 그쪽이 우선(라이브 봉)
    live = dict(recovered, _book_bid_sum=400, _book_ask_sum=300)
    assert _book_depth_cols(live)[2] == 200.0


def test_book_depth_not_consumed_by_entry_path():
    """소비 0 규약 — 진입·사이징 경로가 book_* / gp_range 를 읽지 않는다."""
    import io
    roots = ("strategy", "execution", "risk")
    hits = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dp, _dn, fn in os.walk(root):
            if "__pycache__" in dp:
                continue
            for f in fn:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(dp, f)
                with io.open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    src = fh.read()
                for key in ("book_bid_tot", "book_ask_tot", "book_bid_avg",
                            "book_ask_avg", "gp_range_", "gp_dir_"):
                    if key in src:
                        hits.append("%s:%s" % (p, key))
    assert not hits, "적재 전용 열이 진입 경로에서 소비됨: %s" % hits


def test_migration_on_pre552_schema_db():
    """552차 이전 스키마 DB 에 ALTER 가 정상 적용되고 기존 행은 NULL 로 남는다.

    라이브 `raw_data.db`(563MB · 96,903행)가 다음 기동 때 통과할 경로다.
    기존 행이 0 으로 채워지면 "그때 잔량이 0이었다"는 거짓말이 96,903건 생긴다.
    """
    import utils.db_utils as D
    tmp = tempfile.mkdtemp()
    db = os.path.join(tmp, "old.db")
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, open REAL NOT NULL,
      high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL, volume INTEGER NOT NULL,
      bid1 REAL, ask1 REAL, oi INTEGER, buy_vol INTEGER DEFAULT 0, sell_vol INTEGER DEFAULT 0,
      anchor_buy INTEGER, anchor_sell INTEGER, buy_vol_flag INTEGER, sell_vol_flag INTEGER,
      bar_recovered INTEGER, created_at TEXT)""")
    con.execute("""CREATE TABLE session_bars (ts TEXT PRIMARY KEY, session TEXT NOT NULL,
      open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL,
      volume INTEGER NOT NULL, buy_vol INTEGER, sell_vol INTEGER, anchor_buy INTEGER,
      anchor_sell INTEGER, bid1 REAL, ask1 REAL, bid_qty INTEGER, ask_qty INTEGER,
      oi INTEGER, tick_count INTEGER, auction_code INTEGER, auction_ticks INTEGER,
      source TEXT NOT NULL, created_at TEXT)""")
    con.execute("INSERT INTO raw_candles(ts,open,high,low,close,volume)"
                " VALUES('2026-09-01 09:00:00',1,2,0,1,5)")
    con.execute("INSERT INTO session_bars(ts,session,open,high,low,close,volume,source)"
                " VALUES('2026-09-01 09:00:00','REGULAR',1,2,0,1,5,'rt')")
    con.commit()
    con.close()
    orig = D.RAW_DATA_DB
    D.RAW_DATA_DB = db
    try:
        D.init_raw_data_db()
        con = sqlite3.connect(db)
        need = ["book_bid_tot", "book_ask_tot", "book_bid_avg", "book_ask_avg", "book_snaps"]
        for t in ("raw_candles", "session_bars"):
            cols = [r[1] for r in con.execute("PRAGMA table_info(%s)" % t)]
            for c in need:
                assert c in cols, "%s 에 %s 미추가" % (t, c)
            got = con.execute("SELECT %s FROM %s" % (",".join(need), t)).fetchone()
            assert got == (None,) * 5, "기존 행이 NULL 이 아니다: %s %s" % (t, got)
        con.close()
    finally:
        D.RAW_DATA_DB = orig
