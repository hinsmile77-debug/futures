# -*- coding: utf-8 -*-
"""[MW0601 566차 / T-BOOK-1] 호가깊이 **추정량 정리** — 회귀 가드.

무엇을 고정하는가
-----------------
561차가 확인한 사실: `book_*_tot` 은 **봉의 마지막 1스냅샷**이다(봉당 중앙 494건
중 1건). 이름이 「합계」로 읽혀 561차 판정기가 실제로 그것을 「봉의 깊이」로
썼고, 표집 잡음을 「새 정보」로 오판해 **326차가 이미 기각한 축을 통과**시킬
뻔했다. 주석에 경고가 있었는데도 밟았다 — 그러면 다음 사람도 밟는다.

566차가 한 것:

  ① `book_bid_max`/`book_ask_max` 신설 — 「이 봉에서 깊이가 얼마까지 갔나」에
     답하는 열. `_avg` 는 뭉개고 `_tot` 은 임의의 한 장면이라 둘 다 답하지 못한다.
  ② `_tot` 2종을 **폐기 예정**으로 강등(스키마 주석) — 신규 소비 금지.
  ③ 소비처를 `_avg`/`_max` 로 이동.

⚠ **`min` 은 넣지 않는다.** 5단 합의 하한이 5 에 붙어 있어(실측 min=5·중앙 8)
  사실상 상수다. 범위를 넓히면 「쓰지 않는 열」이 하나 더 생길 뿐이다.

⚠ **566차 이전 행의 `_max` 는 NULL 이다 — 0 이 아니다**(계측 4원칙 ②).

이 파일이 깨지면 정리가 되돌려진 것이다. 수치를 고치기 전에
`docs/미륵이고도화3/호가깊이/호가잔량_유효성_딥다이브_MW0601-20260914.md` 를 읽을 것.
"""
from __future__ import print_function

import io
import os
import sqlite3
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _read(rel):
    with io.open(os.path.join(_ROOT, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


# ─────────────────────── ① 누적 의미 ───────────────────────
class _FakeHoga(object):
    def __init__(self, ask_p, ask_q, bid_p, bid_q):
        self._v = {}
        for i in range(5):
            self._v[2 + i] = float(ask_p[i])
            self._v[7 + i] = int(ask_q[i])
            self._v[19 + i] = float(bid_p[i])
            self._v[24 + i] = int(bid_q[i])

    def GetHeaderValue(self, i):
        return self._v[i]


def _rt():
    from collection.cybos.realtime_data import CybosRealtimeData
    r = CybosRealtimeData.__new__(CybosRealtimeData)
    r._last_bid1 = r._last_ask1 = 0.0
    r._last_bid_qty = r._last_ask_qty = 0
    r._book_oneside_count = 0
    r._last_hoga_snapshot = {"bid_prices": [], "ask_prices": [],
                             "bid_qtys": [], "ask_qtys": []}
    r._hoga_event_count = 0
    r._rt_code = "TEST"
    r._on_hoga = None
    r._current_bar = {"book_bid_tot": None, "book_ask_tot": None,
                      "book_bid_max": None, "book_ask_max": None,
                      "book_snaps": 0, "_book_bid_sum": 0, "_book_ask_sum": 0}
    return r


def test_max_is_monotone_and_survives_the_overwrite():
    """`_tot` 이 덮이는 바로 그 자리에서 `_max` 는 살아남는다."""
    r = _rt()
    r._handle_hoga(_FakeHoga([101, 102, 103, 104, 105], [10, 20, 30, 40, 50],
                             [100, 99, 98, 97, 96], [11, 21, 31, 41, 51]))
    r._handle_hoga(_FakeHoga([101, 102, 103, 104, 105], [1, 2, 3, 4, 5],
                             [100, 99, 98, 97, 96], [5, 4, 3, 2, 1]))
    r._handle_hoga(_FakeHoga([101, 102, 103, 104, 105], [2, 2, 2, 2, 2],
                             [100, 99, 98, 97, 96], [40, 40, 40, 40, 40]))
    b = r._current_bar
    assert b["book_bid_tot"] == 200, "`_tot` 은 마지막 장면이어야 한다"
    assert b["book_bid_max"] == 200, "매수 최댓값"
    assert b["book_ask_max"] == 150, "매도 최댓값 — 첫 스냅샷 뒤로 계속 작아졌다"
    assert b["book_ask_tot"] == 10, "`_tot` 이 150 → 10 으로 덮인 그 자리"


def test_bar_invariants_hold():
    """`tot <= max` · `avg <= max` — 인수조건 2·3 을 산술로 고정한다."""
    r = _rt()
    for q in ([10, 20, 30, 40, 50], [1, 2, 3, 4, 5], [8, 8, 8, 8, 8]):
        r._handle_hoga(_FakeHoga([101, 102, 103, 104, 105], q,
                                 [100, 99, 98, 97, 96], q))
    b = r._current_bar
    avg = b["_book_bid_sum"] / float(b["book_snaps"])
    assert b["book_bid_tot"] <= b["book_bid_max"]
    assert avg <= b["book_bid_max"] + 1e-9


def test_min_columns_are_not_introduced():
    """범위 확장 금지 — `min` 은 정보가 거의 없다(실측 하한 5 고착)."""
    for rel in ("utils/db_utils.py", "collection/cybos/realtime_data.py"):
        src = _read(rel)
        assert "book_bid_min" not in src and "book_ask_min" not in src, (
            "%s 에 min 열이 생겼다 — T-BOOK-1 은 범위를 넓히지 않기로 했다" % rel)


# ─────────────────────── ② 스키마·마이그레이션 ───────────────────────
def test_alter_migration_adds_max_to_existing_db():
    """566차 이전 스키마의 DB 에도 열이 붙고, **기존 행은 NULL** 로 남는다."""
    import utils.db_utils as D
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "raw_data.db")
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, open REAL, high REAL,"
                " low REAL, close REAL, volume INTEGER, book_bid_tot INTEGER,"
                " book_bid_avg REAL, book_snaps INTEGER)")
    con.execute("INSERT INTO raw_candles VALUES ('2026-09-12 09:00:00',1,1,1,1,1,9,9.0,3)")
    con.commit(); con.close()
    orig = D.RAW_DATA_DB
    D.RAW_DATA_DB = path
    try:
        D.init_raw_data_db()
        con = sqlite3.connect(path)
        cols = [r[1] for r in con.execute("PRAGMA table_info(raw_candles)")]
        assert "book_bid_max" in cols and "book_ask_max" in cols, "ALTER 가 안 돌았다"
        got = con.execute("SELECT book_bid_max, book_ask_max FROM raw_candles").fetchone()
        assert got == (None, None), "기존 행이 0 으로 채워졌다 — 계측 4원칙 ② 위반"
        con.close()
    finally:
        D.RAW_DATA_DB = orig


def test_session_bars_writer_carries_max():
    """`session_bars` 도 같이 싣는다 — 552차 결함1(writer 하나만 패치)의 재발 방지."""
    import utils.db_utils as D
    tmp = tempfile.mkdtemp()
    orig = D.RAW_DATA_DB
    D.RAW_DATA_DB = os.path.join(tmp, "raw_data.db")
    try:
        D.init_raw_data_db()
        bar = dict(ts="2026-09-15 09:00:00", open=1.0, high=1.0, low=1.0, close=1.0,
                   volume=1, book_bid_tot=120, book_ask_tot=80,
                   book_bid_max=210, book_ask_max=140,
                   _book_bid_sum=300, _book_ask_sum=200, book_snaps=3)
        D.save_session_bar(bar, "REGULAR", "rt")
        con = sqlite3.connect(D.RAW_DATA_DB)
        got = con.execute("SELECT book_bid_max, book_ask_max FROM session_bars"
                          " WHERE ts=?", (bar["ts"],)).fetchone()
        con.close()
        assert got == (210, 140), "session_bars 가 max 를 안 싣는다: %r" % (got,)
    finally:
        D.RAW_DATA_DB = orig


# ─────────────────────── ③ 강등·소비처 ───────────────────────
def test_tot_is_marked_deprecated_in_schema():
    """이름이 오용을 부른다 — 스키마에 **폐기 예정**이 박혀 있어야 한다."""
    src = _read("utils/db_utils.py")
    i = src.find("book_bid_tot  INTEGER,   -- 봉 **마지막 1스냅샷**")
    assert i != -1, "tot 의 점표본 주석이 사라졌다"
    head = src[max(0, i - 700):i]
    assert "폐기 예정" in head, "강등 표기가 없다 — 다음 사람이 또 「합계」로 읽는다"
    assert "T-BOOK-1b" in head


def test_daily_checker_uses_avg_and_checks_invariants():
    """일일 점검기가 `_avg` 로 적재를 보고 `_max` 불변식을 매일 센다."""
    src = _read("scripts/defect3_collection_check.py")
    assert "SUM(book_bid_avg IS NOT NULL)" in src, "적재 센서가 아직 tot 이다"
    assert "불변식 tot<=max" in src and "불변식 avg<=max" in src
    # 566차 이전 날짜를 FAIL 로 찍으면 안 된다
    assert "566차 배포 이전 거래일" in src, "미측정과 실패를 구분하지 않는다"


def test_ratio_check_keeps_tot_on_purpose():
    """「5단 ÷ 1단」만은 `_tot` 이 맞다 — `bid_qty` 와 **같은 스냅샷**이기 때문이다.

    여기까지 기계적으로 `_avg` 로 바꾸면 서로 다른 추정량을 비교하게 돼
    「5단합 ≥ 1단」 불변식 자체가 무의미해진다. 그 판단 근거를 남겨 둔다.
    """
    src = _read("scripts/defect3_collection_check.py")
    assert "의도적으로 `_tot`" in src, "왜 여기만 tot 인지가 안 적혀 있다"
    assert "1.0*book_bid_tot/bid_qty" in src
