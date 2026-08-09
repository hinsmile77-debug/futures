"""[MW0601 452차 / QDQ Phase 1] 복구 재처리가 DB 원본을 파괴하지 않음을 잠근다.

────────────────────────────────────────────────────────────────────────────
무엇이 고장나 있었나
────────────────────────────────────────────────────────────────────────────
`main.py:_try_pipeline_recovery()`는 파이프라인이 멎으면 `raw_candles`의 마지막 봉을
읽어 재처리한다. 그런데 bar dict를 손으로 조립하면서

    "buy_vol": 0, "sell_vol": 0      # 하드코딩
    # bid1 / ask1 / oi 는 키 자체가 없음

로 만들었고, 그 bar가 `save_candle_and_features()`의 `INSERT OR REPLACE`에 도달하며
**방금 읽어온 그 행을 열등한 값으로 덮어썼다.**

    읽기 전: volume=308 buy_vol=193 sell_vol=115 bid1=969.82 oi=93197
    쓰기 후: volume=308 buy_vol=0   sell_vol=0   bid1=NULL   oi=NULL

실측 피해 55봉(2026-06-08 이후). 06-25 16봉 · 07-31 13봉 · 08-04 15봉 —
**파이프라인이 멎을 만큼 험했던 날에 집중**. 원본 소실로 복구 불가.

────────────────────────────────────────────────────────────────────────────
이 테스트가 잠그는 것 — 특히 P1
────────────────────────────────────────────────────────────────────────────
P1(스키마 자동 추종)이 이 파일의 핵심이다. 같은 안티패턴이 **세 번** 재발했고
(451차 program_*, aggregate_and_backfill, 이번 복구 경로), 세 번 다 원인은
"열 목록을 손으로 적었다"였다. 452차 Phase 0이 방금 4열을 추가했고 Phase 4가 더
추가할 예정이라, 목록 방식이면 **네 번째 재발이 예약**돼 있다.
P1은 미래에 추가될 열까지 자동으로 실리는지를 확인한다.

  P1 행의 모든 열이 자동 승계된다 (하드코딩 목록 없음 — 미지의 신규 열도 실린다)
  P2 NULL 열은 키 자체가 만들어지지 않는다 (None을 실으면 bar_aggregator가 죽는다)
  P3 ts → datetime 파싱 · created_at 제외
  P4 bar_recovered 표식
  P5 🔴 왕복 멱등성 — 재저장 후 행이 한 열도 바뀌지 않는다 (발견 C 직접 회귀)
  P6 buy_vol 키 없는 bar → 0이 아니라 NULL
  P7 bar_recovered 3상태 (NULL=452차 이전 / 0=정상 / 1=복구)
  P8 derive_bar_flow — 실측 우선, 없으면 기하 프록시, 합 == volume
"""

import datetime
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()


def _row(sql_table_extra="", values_extra=(), cols_extra=""):
    """임시 DB에 raw_candles 1행을 넣고 sqlite3.Row로 돌려준다."""
    tmp = tempfile.mkdtemp(prefix="qdq_p1_")
    path = os.path.join(tmp, "r.db")
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("""
        CREATE TABLE raw_candles (
            ts TEXT PRIMARY KEY, open REAL, high REAL, low REAL, close REAL,
            volume INTEGER, bid1 REAL, ask1 REAL, oi INTEGER,
            buy_vol INTEGER, sell_vol INTEGER,
            anchor_buy INTEGER, anchor_sell INTEGER,
            buy_vol_flag INTEGER, sell_vol_flag INTEGER,
            bar_recovered INTEGER, created_at TEXT %s
        )""" % sql_table_extra)
    con.execute(
        "INSERT INTO raw_candles (ts, open, high, low, close, volume, bid1, ask1, oi,"
        " buy_vol, sell_vol, anchor_buy, anchor_sell, buy_vol_flag, sell_vol_flag,"
        " bar_recovered, created_at%s) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?%s)"
        % (cols_extra, "," + ",".join("?" * len(values_extra)) if values_extra else ""),
        ("2026-08-04 14:04:00", 967.72, 970.28, 967.72, 969.24, 308,
         969.82, 969.98, 93197, 193, 115, 190, 118, 191, 117,
         0, "2026-08-04 14:04:50") + tuple(values_extra),
    )
    con.commit()
    row = con.execute("SELECT * FROM raw_candles").fetchone()
    con.close()
    return row


# ── P1 · P2 · P3 · P4 ──────────────────────────────────────────────────────

def test_p1_carries_every_column_including_unknown_future_ones():
    """열 목록을 하드코딩하지 않았음을 '미래의 열'로 증명한다."""
    import main

    row = _row(sql_table_extra=", future_col_x INTEGER",
               cols_extra=", future_col_x", values_extra=(4242,))
    bar = main._bar_from_raw_candle_row(row)

    # Phase 0이 추가한 열
    assert bar["anchor_buy"] == 190 and bar["anchor_sell"] == 118
    assert bar["buy_vol_flag"] == 191 and bar["sell_vol_flag"] == 117
    # 실측 피해의 직접 대상이던 열
    assert bar["buy_vol"] == 193 and bar["sell_vol"] == 115
    assert bar["bid1"] == 969.82 and bar["ask1"] == 969.98 and bar["oi"] == 93197
    # 🔴 이 함수가 전혀 모르는 열도 실려야 한다 (미래 스키마 추가 대비)
    assert bar["future_col_x"] == 4242, "열 목록을 하드코딩하면 여기서 걸린다"


def test_p2_null_columns_do_not_create_keys():
    """None을 실으면 bar_aggregator의 sum()이 TypeError로 죽는다."""
    import main
    from features.bar_aggregator import BarAggregator

    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE raw_candles (ts TEXT, open REAL, high REAL, low REAL,"
                " close REAL, volume INTEGER, buy_vol INTEGER, bid1 REAL)")
    con.execute("INSERT INTO raw_candles VALUES ('2026-08-04 14:04:00',1,2,0,1,308,"
                " NULL, NULL)")
    row = con.execute("SELECT * FROM raw_candles").fetchone()
    bar = main._bar_from_raw_candle_row(row)

    assert "buy_vol" not in bar, "NULL은 키를 만들지 않는다"
    assert "bid1" not in bar
    assert bar["volume"] == 308

    # 키가 없어야 하류 두 소비처가 모두 안전하다
    assert bar.get("buy_vol", 0) == 0          # bar_aggregator 경로
    assert bar.get("buy_vol") is None          # feature_builder 프록시 분기 경로
    BarAggregator().push(dict(bar, ts=bar["ts"]))   # sum()이 죽지 않는다


def test_p3_ts_parsed_and_created_at_dropped():
    import main
    bar = main._bar_from_raw_candle_row(_row())
    assert isinstance(bar["ts"], datetime.datetime)
    assert bar["ts"] == datetime.datetime(2026, 8, 4, 14, 4, 0)
    assert "created_at" not in bar, "DB 자동생성 열을 실어보내면 안 된다"


def test_p4_marks_bar_recovered():
    import main
    assert main._bar_from_raw_candle_row(_row())["bar_recovered"] is True


# ── P5 🔴 핵심 회귀 ─────────────────────────────────────────────────────────

def test_p5_recovery_roundtrip_is_idempotent():
    """복구 재저장 후 행이 **한 열도** 바뀌지 않아야 한다 (발견 C 직접 회귀)."""
    import main
    import utils.db_utils as dbu

    tmp = tempfile.mkdtemp(prefix="qdq_p1_rt_")
    path = os.path.join(tmp, "raw_data.db")
    _orig = dbu.RAW_DATA_DB
    try:
        dbu.RAW_DATA_DB = path
        dbu.init_raw_data_db()

        original = {
            "ts": "2026-08-04 14:04:00", "open": 967.72, "high": 970.28,
            "low": 967.72, "close": 969.24, "volume": 308,
            "bid1": 969.82, "ask1": 969.98, "oi": 93197,
            "buy_vol": 193, "sell_vol": 115,
            "anchor_buy": 190, "anchor_sell": 118,
            "buy_vol_flag": 191, "sell_vol_flag": 117,
        }
        dbu.save_candle(original)

        def _snapshot():
            con = sqlite3.connect(path)
            con.row_factory = sqlite3.Row
            r = con.execute("SELECT * FROM raw_candles").fetchone()
            con.close()
            # created_at은 매 write마다 갱신되고, bar_recovered는 0→1이 **의도된 변화**다
            return {k: r[k] for k in r.keys()
                    if k not in ("created_at", "bar_recovered")}

        before = _snapshot()

        # 복구 경로가 하는 일을 그대로 재현: 행을 읽어 bar를 만들고 다시 저장
        row = dbu.fetchone(path, "SELECT * FROM raw_candles ORDER BY ts DESC LIMIT 1")
        dbu.save_candle(main._bar_from_raw_candle_row(row))

        after = _snapshot()
        assert after == before, (
            "복구 재처리가 원본을 바꿨다 — 발견 C 재발\n before=%s\n after =%s"
            % (before, after))

        # 표식은 남아야 한다
        con = sqlite3.connect(path)
        assert con.execute("SELECT bar_recovered FROM raw_candles").fetchone()[0] == 1
        con.close()
    finally:
        dbu.RAW_DATA_DB = _orig


# ── P6 · P7 ────────────────────────────────────────────────────────────────

def test_p6_missing_flow_writes_null_not_zero():
    """buy_vol 키가 없으면 '매수 0계약'이 아니라 '모른다(NULL)'가 남아야 한다."""
    import utils.db_utils as dbu

    tmp = tempfile.mkdtemp(prefix="qdq_p1_null_")
    path = os.path.join(tmp, "raw_data.db")
    _orig = dbu.RAW_DATA_DB
    try:
        dbu.RAW_DATA_DB = path
        dbu.init_raw_data_db()
        dbu.save_candle({"ts": "2026-08-04 14:04:00", "open": 1, "high": 2,
                         "low": 0, "close": 1, "volume": 308})
        con = sqlite3.connect(path)
        got = con.execute("SELECT buy_vol, sell_vol, volume FROM raw_candles").fetchone()
        con.close()
        assert got == (None, None, 308), got
    finally:
        dbu.RAW_DATA_DB = _orig


def test_p7_bar_recovered_three_states():
    import utils.db_utils as dbu

    tmp = tempfile.mkdtemp(prefix="qdq_p1_flag_")
    path = os.path.join(tmp, "raw_data.db")
    _orig = dbu.RAW_DATA_DB
    try:
        dbu.RAW_DATA_DB = path
        # 452차 이전 스키마로 만든 뒤 행 1개 → 마이그레이션 후 NULL이어야 한다
        con = sqlite3.connect(path)
        con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, open REAL NOT NULL,"
                    " high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL,"
                    " volume INTEGER NOT NULL, bid1 REAL, ask1 REAL, oi INTEGER,"
                    " buy_vol INTEGER, sell_vol INTEGER, created_at TEXT)")
        con.execute("INSERT INTO raw_candles (ts,open,high,low,close,volume)"
                    " VALUES ('2026-08-01 09:00:00',1,2,0,1,5)")
        con.commit(); con.close()

        dbu.init_raw_data_db()
        base = {"open": 1, "high": 2, "low": 0, "close": 1, "volume": 5}
        dbu.save_candle(dict(base, ts="2026-08-04 09:01:00"))                    # 정상
        dbu.save_candle(dict(base, ts="2026-08-04 09:02:00", bar_recovered=True))  # 복구

        con = sqlite3.connect(path)
        got = dict(con.execute(
            "SELECT ts, bar_recovered FROM raw_candles ORDER BY ts").fetchall())
        con.close()
        assert got["2026-08-01 09:00:00"] is None, "452차 이전 행 = NULL"
        assert got["2026-08-04 09:01:00"] == 0, "정상 실시간 경로 = 0"
        assert got["2026-08-04 09:02:00"] == 1, "복구 재처리 = 1"
    finally:
        dbu.RAW_DATA_DB = _orig


# ── P8 ─────────────────────────────────────────────────────────────────────

def test_p8_derive_bar_flow():
    from scripts.aggregate_and_backfill import derive_bar_flow

    # 실측이 있으면 그대로
    buy, sell, proxy = derive_bar_flow(308, 970.28, 967.72, 969.24,
                                       buy_vol=193, sell_vol=115)
    assert (buy, sell, proxy) == (193.0, 115.0, False)

    # 없으면 기하 프록시 — 합은 반드시 volume과 일치
    buy, sell, proxy = derive_bar_flow(308, 970.28, 967.72, 969.24)
    assert proxy is True
    assert abs((buy + sell) - 308) < 1e-9, "합이 거래량과 어긋나면 항등식이 깨진다"
    assert buy > 0 and sell > 0

    # 종가=고가면 전량 매수 귀속
    buy, sell, _ = derive_bar_flow(100, 10.0, 9.0, 10.0)
    assert abs(buy - 100) < 1e-9 and abs(sell) < 1e-9

    # high==low(플랫 바)에서도 죽지 않는다
    buy, sell, _ = derive_bar_flow(100, 10.0, 10.0, 10.0)
    assert abs((buy + sell) - 100) < 1e-9

    # 한쪽만 있으면 실측으로 치지 않는다
    _, _, proxy = derive_bar_flow(100, 10.0, 9.0, 9.5, buy_vol=50, sell_vol=None)
    assert proxy is True


if __name__ == "__main__":
    _fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    _fail = 0
    for fn in _fns:
        try:
            fn()
            print("OK   %s" % fn.__name__)
        except Exception as e:
            _fail += 1
            print("FAIL %s: %r" % (fn.__name__, e))
    print("-" * 60)
    print("%d/%d 통과" % (len(_fns) - _fail, len(_fns)))
    sys.exit(1 if _fail else 0)
