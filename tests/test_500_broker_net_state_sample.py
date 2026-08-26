# -*- coding: utf-8 -*-
"""[MW0602 500차] F-5 회귀 — `upsert_broker_net()` 무조건 상태 샘플.

**무엇이 문제였나.** 이 함수는 **무음 `return` 이 둘**이었다. 2026-08-26 EOD 에서
당일 `daily_broker_pnl.broker_net_krw` 행이 한 줄도 생기지 않았는데 로그에는 아무
흔적이 없어, 「브로커 TR 이 빈 값을 줬나 / 비거래일로 걸렀나 / 애초에 호출이 안
됐나」를 사후에 구분할 수 없었다(0826 이상점 `1-7`).

CLAUDE.md 「계측 4원칙 ④ 폴백 가시화」가 정확히 이 형태를 금지한다 — 그리고 470차
`C2'` 는 `[MarginCap]` 에서 **조건부 로그의 함정**까지 못박았다(축소 시에만 찍으면
100% 고착이 구조적으로 보장된다). 그래서 여기서 고정하는 불변식:

① **세 상태가 모두 로그를 남긴다** — `OK` / `SKIP_BLANK_TR` / `SKIP_NON_TRADING`.
   "안 찍히는 상태"가 존재하지 않는다.
② **DB 동작은 무변경** — 스킵 조건도, 기록되는 값도 종전과 같다.
③ **하트비트** — 잔고 폴링 경로라 분당 여러 번 들어와도 같은 샘플은 억제하되,
   억제 건수를 다음 줄에 병기한다(계측 4원칙 ③ 탈락 가시화).
④ **상태·값이 바뀌면 억제하지 않는다** — 전이를 놓치면 계측 자체가 무의미하다.
⑤ **`getattr` 폴백으로 상태를 읽지 않는다**(계측 4원칙 ④) — 모듈 전역 명시 초기화.

실행:
    py37_32\\python.exe tests/test_500_broker_net_state_sample.py
"""
import io
import logging
import os
import sqlite3
import sys
import tempfile
from contextlib import contextmanager

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import utils.db_utils as dbu  # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []

# 실제 거래일 / 비거래일 (2026-08-16 은 일요일 — 0826 리포트 `1-15` 유령 행 사례)
TRADING_DAY = "2026-08-26"
NON_TRADING_DAY = "2026-08-16"

_DDL = """CREATE TABLE daily_broker_pnl (
            date       TEXT PRIMARY KEY,
            pnl_krw    REAL NOT NULL,
            updated_at TEXT NOT NULL,
            commission_krw REAL, pnl_net_krw REAL,
            deposit_cash_krw REAL, next_day_deposit_cash_krw REAL,
            broker_net_krw REAL)"""


class _Capture(logging.Handler):
    """`[BrokerNet]` 줄만 모은다."""

    def __init__(self):
        logging.Handler.__init__(self)
        self.lines = []

    def emit(self, record):
        msg = record.getMessage()
        if "[BrokerNet]" in msg:
            self.lines.append(msg)


@contextmanager
def _sandbox(trading=True):
    """실거래 `trades.db` 를 건드리지 않고 함수를 돌린다.

    ⚠ 격리는 선택이 아니다 — 검증 스크립트가 실거래 상태파일을 오염시킨 사고가
      이 저장소에 이미 있다(진입가 100.0 오염).
    ⚠ `is_krx_trading_date` 도 **명시적으로** 갈아끼운다. `get_conn` 만 바꾸면 그
      함수가 predictions 조회에 실패해 `except: return True` 폴백으로 떨어져
      비거래일 분기를 영영 못 밟는다 — 테스트가 조용히 통과하는 형태다.
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(_DDL)
    conn.commit()

    @contextmanager
    def _fake_get_conn(db_path, timeout=10.0):
        yield conn

    cap = _Capture()
    logger = logging.getLogger("SYSTEM")
    prev_level = logger.level
    logger.setLevel(logging.INFO)
    logger.addHandler(cap)
    real_get_conn = dbu.get_conn
    real_is_trading = dbu.is_krx_trading_date
    dbu.get_conn = _fake_get_conn
    dbu.is_krx_trading_date = lambda _d: bool(trading)
    # 모듈 전역 하트비트 상태 초기화 — 테스트 간 누수 방지.
    dbu._broker_net_log_state.update({"key": None, "ts": 0.0, "suppressed": 0})
    try:
        yield cap, conn
    finally:
        dbu.get_conn = real_get_conn
        dbu.is_krx_trading_date = real_is_trading
        logger.removeHandler(cap)
        logger.setLevel(prev_level)
        conn.close()
        try:
            os.remove(path)
        except OSError:
            pass


def _states(cap):
    out = []
    for line in cap.lines:
        out.append(line.split("state=")[1].split(" ")[0])
    return out


# ── ① 세 상태가 모두 로그를 남긴다 ────────────────────────────────────────────
def test_blank_tr_is_not_silent():
    with _sandbox() as (cap, conn):
        dbu.upsert_broker_net(TRADING_DAY, 0.0, 0.0)
    assert _states(cap) == ["SKIP_BLANK_TR"], cap.lines
    assert "dep=0" in cap.lines[0] and "next=0" in cap.lines[0], cap.lines[0]


def test_non_trading_day_is_not_silent():
    with _sandbox(trading=False) as (cap, conn):
        dbu.upsert_broker_net(NON_TRADING_DAY, 1_000_000.0, 1_050_000.0)
    assert _states(cap) == ["SKIP_NON_TRADING"], cap.lines


def test_success_is_also_a_state():
    with _sandbox() as (cap, conn):
        dbu.upsert_broker_net(TRADING_DAY, 1_000_000.0, 1_430_000.0)
    assert _states(cap) == ["OK"], cap.lines
    # net 을 함께 남긴다 — 나중에 DB 없이 로그만으로 대사할 수 있어야 한다.
    assert "net=430000" in cap.lines[0], cap.lines[0]


# ── ② DB 동작 무변경 ──────────────────────────────────────────────────────────
def test_db_effect_unchanged():
    with _sandbox() as (cap, conn):
        dbu.upsert_broker_net(TRADING_DAY, 1_000_000.0, 1_430_000.0)
        row = conn.execute(
            "SELECT deposit_cash_krw, next_day_deposit_cash_krw, broker_net_krw "
            "  FROM daily_broker_pnl WHERE date = ?", (TRADING_DAY,)).fetchone()
    assert row is not None, "성공 경로가 행을 만들지 않았다"
    assert abs(row["broker_net_krw"] - 430_000.0) < 1e-6, tuple(row)


def test_skips_still_write_nothing():
    with _sandbox(trading=False) as (cap, conn):
        dbu.upsert_broker_net(NON_TRADING_DAY, 1_000_000.0, 1_050_000.0)
        n = conn.execute("SELECT COUNT(*) FROM daily_broker_pnl").fetchone()[0]
    assert n == 0, "비거래일 스킵이 유령 행을 만들었다 (계측 4원칙 ② 위반)"
    with _sandbox(trading=True) as (cap, conn):
        dbu.upsert_broker_net(TRADING_DAY, 0.0, 0.0)
        n = conn.execute("SELECT COUNT(*) FROM daily_broker_pnl").fetchone()[0]
    assert n == 0, "빈 TR 스킵이 유령 행을 만들었다 (계측 4원칙 ② 위반)"


# ── ③ 하트비트 — 동일 샘플은 억제하되 건수를 병기한다 ────────────────────────
def test_identical_samples_are_suppressed_with_count():
    with _sandbox() as (cap, conn):
        for _ in range(5):
            dbu.upsert_broker_net(TRADING_DAY, 1_000_000.0, 1_430_000.0)
        assert len(cap.lines) == 1, "동일 샘플 5회가 5줄로 나갔다 (로그 폭증)"
        # 상태가 바뀌면 직전 억제 건수가 그 줄에 드러나야 한다.
        dbu.upsert_broker_net(TRADING_DAY, 0.0, 0.0)
    assert len(cap.lines) == 2, cap.lines
    assert "동일 샘플 4건 생략" in cap.lines[1], cap.lines[1]


def test_heartbeat_interval_is_bounded():
    """무조건 상태 샘플이라면 억제 창이 유한해야 한다 — 무한 억제는 조건부 로그다."""
    assert 0 < dbu.BROKER_NET_LOG_MIN_INTERVAL_SEC <= 60.0, \
        dbu.BROKER_NET_LOG_MIN_INTERVAL_SEC


# ── ④ 전이·값 변화는 억제하지 않는다 ─────────────────────────────────────────
def test_value_change_is_never_suppressed():
    with _sandbox() as (cap, conn):
        dbu.upsert_broker_net(TRADING_DAY, 1_000_000.0, 1_430_000.0)
        dbu.upsert_broker_net(TRADING_DAY, 1_000_000.0, 1_440_000.0)
        dbu.upsert_broker_net(TRADING_DAY, 1_000_000.0, 1_450_000.0)
    assert len(cap.lines) == 3, cap.lines
    assert _states(cap) == ["OK", "OK", "OK"], cap.lines


def test_state_transition_is_never_suppressed():
    """빈 TR -> 비거래일 -> 성공 세 상태가 연속으로 와도 한 줄도 삼키지 않는다."""
    with _sandbox(trading=False) as (cap, conn):
        dbu.upsert_broker_net(TRADING_DAY, 0.0, 0.0)
        dbu.upsert_broker_net(NON_TRADING_DAY, 1_000_000.0, 1_050_000.0)
    assert _states(cap) == ["SKIP_BLANK_TR", "SKIP_NON_TRADING"], cap.lines
    with _sandbox(trading=True) as (cap2, conn):
        dbu.upsert_broker_net(TRADING_DAY, 0.0, 0.0)
        dbu.upsert_broker_net(TRADING_DAY, 1_000_000.0, 1_430_000.0)
    assert _states(cap2) == ["SKIP_BLANK_TR", "OK"], cap2.lines


def test_real_trading_date_gate_is_still_the_guard():
    """스킵 조건 자체는 무변경 — 진짜 게이트가 `is_krx_trading_date` 인가."""
    with io.open(os.path.join(_ROOT, "utils", "db_utils.py"), encoding="utf-8") as f:
        src = f.read()
    body = src.split("def upsert_broker_net")[1].split("\ndef ")[0]
    assert "if not is_krx_trading_date(date):" in body, body[:400]
    assert "if not date or not deposit_cash or not next_day_deposit_cash:" in body
    # 실 캘린더 판정도 살아 있어야 한다(0826 `1-15` 유령 행 대상일이 False 여야 함).
    assert dbu.is_krx_trading_date("2026-08-16") is False
    assert dbu.is_krx_trading_date("2026-08-26") is True


# ── ⑤ 폴백 가시화 규약 — getattr 로 런타임 상태를 읽지 않는다 ────────────────
def test_no_getattr_fallback_for_heartbeat_state():
    with io.open(os.path.join(_ROOT, "utils", "db_utils.py"), encoding="utf-8") as f:
        src = f.read()
    assert "_broker_net_log_state = {" in src, "모듈 전역 명시 초기화가 없다"
    block = src.split("def log_broker_net_state")[1].split("\ndef ")[0]
    assert "getattr(" not in block, "계측 4원칙 ④ 위반 — getattr 폴백으로 상태를 읽는다"


def test_missing_value_renders_as_NA_not_zero():
    """미측정과 0 을 같은 문자로 찍으면 안 된다(계측 4원칙 ②)."""
    assert dbu._fmt_krw(None) == "NA"
    assert dbu._fmt_krw(0) == "0"


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_blank_tr_is_not_silent,
               test_non_trading_day_is_not_silent,
               test_success_is_also_a_state,
               test_db_effect_unchanged,
               test_skips_still_write_nothing,
               test_identical_samples_are_suppressed_with_count,
               test_heartbeat_interval_is_bounded,
               test_value_change_is_never_suppressed,
               test_state_transition_is_never_suppressed,
               test_real_trading_date_gate_is_still_the_guard,
               test_no_getattr_fallback_for_heartbeat_state,
               test_missing_value_renders_as_NA_not_zero):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
