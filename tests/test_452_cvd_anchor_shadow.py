"""[MW0601 452차 / QDQ Phase 0] 앵커 계측 + 체결구분 섀도 분류 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
무엇을 지키는 테스트인가
────────────────────────────────────────────────────────────────────────────
Phase 0의 계약은 **"손실 위험 없이 사실을 확보한다"** 이다. 따라서 지켜야 할 것이
두 종류다.

  (A) 새로 적는 값이 맞는가        → T1·T2·T3
  (B) 기존 값이 하나도 안 바뀌었는가 → T7  ← 이게 깨지면 Phase 0이 아니다

(B)가 특히 중요하다. `buy_vol`/`sell_vol`은 지금 라이브 모델의 학습 입력이라,
여기서 조금이라도 값이 달라지면 CORE 피처에 train/serve skew가 생긴다.
"버그를 그대로 둔 채 옆에 정답을 적는다"가 Phase 0의 전부다.

────────────────────────────────────────────────────────────────────────────
왜 스텁 COM으로 되는가
────────────────────────────────────────────────────────────────────────────
`_handle_tick(obj)`는 `obj.GetHeaderValue(i)`만 호출한다. 그래서 그 메서드 하나만
가진 객체를 넘기면 실제 Cybos COM 없이 전 경로(증분 산출 → 봉 누적 → 마감)가 돈다.
`__init__`은 `api`를 저장만 하므로 스텁으로 충분하다.

────────────────────────────────────────────────────────────────────────────
검증 불변식
────────────────────────────────────────────────────────────────────────────
  T1 decode_trade_side 매핑 (49/50/'1'/'2'/1/2 → BUY/SELL, 그 외 → None)
  T2 정상 흐름: anchor_buy+anchor_sell == volume, 섀도 합 == volume
  T3 발견 A 재현: 보합틱이 있으면 현행 buy_vol > 섀도 buy_vol_flag
  T4 원천이 22/23 미제공 → 앵커 2열 NULL, 섀도는 정상
  T5 원천이 24 미제공   → 섀도 2열 NULL, 앵커는 정상 (0으로 채우지 않음)
  T6 누적값 역행 → 증분 폐기 + 기준선 재설정, 이후 틱 정상
  T7 기존 동작 불변 (volume/buy_vol/sell_vol/OHLC)
  T8 DB 왕복 — 4열 마이그레이션, NULL 보존, 기존 행 NULL 유지
"""

import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from collection.cybos.realtime_data import (  # noqa: E402
    CybosRealtimeData,
    decode_trade_side,
)


# ── 스텁 ────────────────────────────────────────────────────────────────────

class _StubTick(object):
    """`Dscbo1.FutureCurOnly` 실시간 객체의 GetHeaderValue만 흉내낸다.

    필드 번호는 대신 공식 캡처본(`FutureCurOnly(SbPb).xls`) 기준:
      1=현재가 13=누적거래량 14=미결제 15=시각
      18~21=최우선 매도/매수 호가·잔량
      22=누적체결매도 23=누적체결매수 24=체결구분
    """

    def __init__(self, price, cum_volume, cum_sell, cum_buy, flag, hhmmss="100000"):
        self._v = {
            1: price, 13: cum_volume, 14: 1000, 15: hhmmss,
            18: price + 0.05, 19: price - 0.05, 20: 3, 21: 4,
            22: cum_sell, 23: cum_buy, 24: flag,
        }

    def GetHeaderValue(self, idx):  # noqa: N802  (COM 인터페이스 이름)
        return self._v.get(idx, 0)


def _make_feed():
    """실 COM 없이 구동 가능한 CybosRealtimeData 인스턴스."""
    return CybosRealtimeData(api=object(), code="101D3", realtime_code="101D3")


def _drive(ticks):
    """틱 목록을 흘려보내고 마감된 봉 목록을 돌려준다.

    마지막 봉은 다음 분 틱이 없으면 닫히지 않으므로, 강제로 한 번 닫는다.
    """
    feed = _make_feed()
    closed = []
    feed._on_candle_closed = closed.append
    for t in ticks:
        feed._handle_tick(t)
    feed._close_current_bar()
    return feed, closed


# ── T1 ──────────────────────────────────────────────────────────────────────

def test_t1_decode_trade_side():
    # 실제로 오는 값 — 문자 '1'/'2'의 코드값
    assert decode_trade_side(49) == "BUY"
    assert decode_trade_side(50) == "SELL"
    assert decode_trade_side(49.0) == "BUY"
    assert decode_trade_side("50") == "SELL"
    # 원천이 문자로 바뀌어도 견딘다
    assert decode_trade_side("1") == "BUY"
    assert decode_trade_side("2") == "SELL"
    assert decode_trade_side(1) == "BUY"
    assert decode_trade_side(2) == "SELL"
    # 🔴 판정 불가는 반드시 None — 매수로 폴백하면 63% 편향이 재발한다
    for bad in (None, "", 0, "0", 9, "9", "buy", [], {}, True, False):
        assert decode_trade_side(bad) is None, bad


# ── T2 · T3 · T7 ────────────────────────────────────────────────────────────

def _normal_session():
    """매수 2틱 · 매도 2틱 · **보합 1틱(매도)** 의 한 봉.

    보합틱을 매도(flag=50)로 둔 것이 핵심이다. 현행 폴백(`price >= 직전가`)은
    이 틱을 매수로 흡수하지만, 서버 정답지와 올바른 파싱은 매도로 센다 —
    이 괴리가 발견 A의 본체다.

    ⚠ 누적값 기준선을 **0이 아닌 값**으로 잡는다. 첫 틱은 세 계열(거래량·앵커)
    모두 기준선만 세우고 증분을 버리는데, `volume` 산출이
    `... if self._last_cum_volume else 0`이라 기준선이 0이면 그 다음 틱까지
    증분이 0으로 죽는다. 실제 장중에는 구독 시작 시점의 누적값이 0이 아니므로,
    픽스처를 현실에 맞춘다(수집 로직은 손대지 않는다 — Phase 0 비목표).
    """
    return [
        #        price  cumvol  cumsell cumbuy flag
        _StubTick(100.0, 1000,    400,    600,  49),   # 기준선 (증분 버림)
        _StubTick(100.1, 1010,    400,    610,  49),   # 매수 10
        _StubTick(100.2, 1025,    400,    625,  49),   # 매수 15
        _StubTick(100.1, 1035,    410,    625,  50),   # 매도 10
        _StubTick(100.1, 1055,    430,    625,  50),   # 보합 + 매도 20
        _StubTick(100.0, 1060,    435,    625,  50),   # 매도 5
    ]


def test_t2_anchor_and_shadow_identity():
    _, closed = _drive(_normal_session())
    assert len(closed) == 1
    bar = closed[0]

    # 서버 정답지 항등식: 봉내 증분 합 == 봉 거래량
    assert bar["anchor_buy"] + bar["anchor_sell"] == bar["volume"]
    assert bar["anchor_buy"] == 25   # 10 + 15
    assert bar["anchor_sell"] == 35  # 10 + 20 + 5

    # 섀도(올바른 체결구분 파싱)도 같은 항등식을 만족해야 한다
    assert bar["buy_vol_flag"] + bar["sell_vol_flag"] == bar["volume"]
    assert bar["buy_vol_flag"] == 25
    assert bar["sell_vol_flag"] == 35

    # 서버 정답지와 우리 분류가 일치 — 이게 정상 상태다
    assert bar["buy_vol_flag"] == bar["anchor_buy"]
    assert bar["sell_vol_flag"] == bar["anchor_sell"]


def test_t3_reproduces_finding_a_bias():
    """현행 경로가 보합틱을 매수로 흡수하는 것을 실제로 보인다."""
    _, closed = _drive(_normal_session())
    bar = closed[0]

    # 현행: 체결구분이 "49"/"50"이라 `== "2"`가 안 맞고, 폴백 틱룰이 보합(>=)을
    # 매수로 넣는다 → 매도 20이 매수로 넘어간다.
    assert bar["buy_vol"] == 45      # 25(진짜 매수) + 20(보합틱 오분류)
    assert bar["sell_vol"] == 15

    # 🔴 발견 A: 현행이 정답지보다 매수를 20계약 부풀린다
    assert bar["buy_vol"] > bar["anchor_buy"]
    assert bar["buy_vol"] - bar["anchor_buy"] == 20
    assert bar["buy_vol"] - bar["buy_vol_flag"] == 20


def test_t7_legacy_fields_unchanged():
    """Phase 0의 핵심 계약 — 기존 열이 계측 배선 전과 정확히 같아야 한다.

    기대값은 계측 코드와 무관하게 손으로 계산했다(수집 로직을 그대로 옮겨 적으면
    같이 틀려도 통과하므로 의미가 없다).
    """
    _, closed = _drive(_normal_session())
    bar = closed[0]
    assert bar["volume"] == 60
    assert bar["buy_vol"] + bar["sell_vol"] == bar["volume"]
    assert bar["buy_vol"] == 45 and bar["sell_vol"] == 15
    assert bar["open"] == 100.0
    assert bar["high"] == 100.2
    assert bar["low"] == 100.0
    assert bar["close"] == 100.0
    assert bar["tick_count"] == 6


# ── T4 · T5 — 미제공은 NULL이지 0이 아니다 ─────────────────────────────────

def test_t4_anchor_unavailable_stays_null():
    """22/23을 원천이 주지 않으면(항상 0) 앵커 2열은 None으로 남는다."""
    ticks = [
        _StubTick(100.0, 1000, 0, 0, 49),
        _StubTick(100.1, 1010, 0, 0, 49),
        _StubTick(100.0, 1020, 0, 0, 50),
    ]
    feed, closed = _drive(ticks)
    bar = closed[0]

    assert bar["anchor_buy"] is None, "미제공을 0으로 채우면 '매수 0건'으로 위장된다"
    assert bar["anchor_sell"] is None
    assert feed._anchor_available is False

    # 섀도는 독립적으로 정상 동작해야 한다
    assert bar["buy_vol_flag"] == 10
    assert bar["sell_vol_flag"] == 10


def test_t5_flag_unavailable_stays_null():
    """24를 원천이 주지 않으면 섀도 2열은 None. 앵커는 영향 없음."""
    ticks = [
        _StubTick(100.0, 1000, 400, 600, ""),
        _StubTick(100.1, 1010, 400, 610, ""),
        _StubTick(100.0, 1020, 410, 610, ""),
    ]
    feed, closed = _drive(ticks)
    bar = closed[0]

    assert bar["buy_vol_flag"] is None
    assert bar["sell_vol_flag"] is None
    assert feed._flag_unknown_ticks == 3
    assert feed._flag_decoded_ticks == 0

    # 앵커는 정상
    assert bar["anchor_buy"] == 10
    assert bar["anchor_sell"] == 10


# ── T6 — 누적값 역행 ────────────────────────────────────────────────────────

def test_t6_anchor_reset_discards_increment():
    """재접속·세션리셋·월물교체로 누적값이 역행하면 증분을 버리고 재기준한다."""
    ticks = [
        _StubTick(100.0, 1000, 400, 600, 49),   # 기준선
        _StubTick(100.1, 1010, 400, 610, 49),   # +10 매수
        _StubTick(100.2, 1020, 400, 603, 49),   # 역행(610 → 603) — 폐기
        _StubTick(100.3, 1030, 400, 608, 49),   # 재기준 후 +5 매수
    ]
    feed, closed = _drive(ticks)
    bar = closed[0]

    assert feed._anchor_reset_count == 1
    # 역행 틱의 증분은 합산되지 않는다 (10 + 5, 중간의 -7은 버림)
    assert bar["anchor_buy"] == 15
    assert bar["anchor_sell"] == 0

    # 역행 이후에도 기준선이 정상 추적된다
    assert feed._last_cum_buy == 608


def test_t6b_no_ticks_no_columns():
    """앵커를 한 번도 못 쓴 봉은 두 열 모두 None (부분 합산 금지)."""
    ticks = [_StubTick(100.0, 1000, 400, 600, 49)]   # 기준선 틱 하나뿐
    _, closed = _drive(ticks)
    assert closed[0]["anchor_buy"] is None
    assert closed[0]["anchor_sell"] is None


# ── T8 — DB 왕복 ────────────────────────────────────────────────────────────

def test_t8_db_roundtrip_and_null_semantics():
    """마이그레이션 · NULL 저장 · 기존 행 NULL 유지."""
    import utils.db_utils as dbu

    tmpdir = tempfile.mkdtemp(prefix="qdq_p0_")
    db_path = os.path.join(tmpdir, "raw_data.db")

    # 452차 이전 스키마(4열 없음)로 만든 뒤 기존 행을 하나 넣는다
    con = sqlite3.connect(db_path)
    con.execute("""
        CREATE TABLE raw_candles (
            ts TEXT PRIMARY KEY, open REAL NOT NULL, high REAL NOT NULL,
            low REAL NOT NULL, close REAL NOT NULL, volume INTEGER NOT NULL,
            bid1 REAL, ask1 REAL, oi INTEGER,
            buy_vol INTEGER DEFAULT 0, sell_vol INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )""")
    con.execute("INSERT INTO raw_candles (ts, open, high, low, close, volume, "
                "buy_vol, sell_vol) VALUES ('2026-08-07 09:00:00',1,2,0,1,5,3,2)")
    con.commit()
    con.close()

    _orig = dbu.RAW_DATA_DB
    try:
        dbu.RAW_DATA_DB = db_path
        dbu.init_raw_data_db()          # 마이그레이션

        cols = {r[1] for r in sqlite3.connect(db_path)
                .execute("PRAGMA table_info(raw_candles)")}
        for c in ("anchor_buy", "anchor_sell", "buy_vol_flag", "sell_vol_flag"):
            assert c in cols, c

        # 기존 행은 NULL이어야 한다 (DEFAULT 0이 붙으면 여기서 걸린다)
        row = sqlite3.connect(db_path).execute(
            "SELECT anchor_buy, buy_vol_flag FROM raw_candles "
            "WHERE ts='2026-08-07 09:00:00'").fetchone()
        assert row == (None, None), row

        # 계측된 봉 저장 → 그대로 읽힌다
        dbu.save_candle({
            "ts": "2026-08-07 09:01:00", "open": 1, "high": 2, "low": 0,
            "close": 1, "volume": 60, "buy_vol": 45, "sell_vol": 15,
            "anchor_buy": 25, "anchor_sell": 35,
            "buy_vol_flag": 25, "sell_vol_flag": 35,
        })
        # 미계측 봉 저장 → 키가 없으면 NULL (0으로 채워지면 안 된다)
        dbu.save_candle({
            "ts": "2026-08-07 09:02:00", "open": 1, "high": 2, "low": 0,
            "close": 1, "volume": 7, "buy_vol": 4, "sell_vol": 3,
        })

        con = sqlite3.connect(db_path)
        got = con.execute(
            "SELECT ts, buy_vol, anchor_buy, anchor_sell, buy_vol_flag, sell_vol_flag "
            "FROM raw_candles WHERE ts >= '2026-08-07 09:01:00' ORDER BY ts").fetchall()
        con.close()
        assert got[0] == ("2026-08-07 09:01:00", 45, 25, 35, 25, 35), got[0]
        assert got[1] == ("2026-08-07 09:02:00", 4, None, None, None, None), got[1]
    finally:
        dbu.RAW_DATA_DB = _orig


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
