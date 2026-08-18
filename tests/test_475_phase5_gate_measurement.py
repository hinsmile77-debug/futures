# -*- coding: utf-8 -*-
"""tests/test_475_phase5_gate_measurement.py
    — [MW0602 475차 후속] 실전 전환 게이트 ①·④ 실측 배선 회귀

────────────────────────────────────────────────────────────────────────────
무엇을 지키는가
────────────────────────────────────────────────────────────────────────────
①④는 `checker=None`("trades.db 실측이 필요해 코드가 판정할 수 없다")이었다.
그런데 ①의 판정식은 SQL 한 줄이다. 손으로 적은 수치를 노트에 남기는 방식은 이 repo 에서
이미 실패했다 — 417차의 "379건 중 86건"이 몇 주 동안 재인용됐고 CLAUDE.md 가 그것을
직접 경고한다.

**충족을 자동으로 선언하지는 않는다.** 이 모듈의 규율 그대로다 —
*"자동 판정은 한쪽 방향으로만 확정한다."*

  ① 합이 0 이하 → OPEN(반증 확실) / 양수 → UNMEASURED(롤링 창이라 확정은 사람 몫)
  ④ 합격선이 정의된 적이 없다 → **영구 UNMEASURED**. 임계를 지어내면 코드가
     사전등록 원칙(§9)을 넘는 것이 된다. 대신 재료(평균·표준편차·양수일)를 보여 준다.

불변식:
  (1) DB 를 못 읽으면 UNMEASURED — 미충족으로 떨어뜨리지 않는다(계측 4원칙 ②)
  (2) 통산이 음수면 OPEN (반증은 자동으로 확정한다)
  (3) 통산이 양수여도 MET 이 아니다 (충족은 자동 선언하지 않는다)
  (4) 4주(20거래일) 미달이면 UNMEASURED — 표본 부족을 충족/미충족으로 읽지 않는다
  (5) ④는 어떤 입력에도 MET/OPEN 이 되지 않는다 (합격선 부재)
"""
from __future__ import print_function

import os
import shutil
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MIREUK_TEST_MODE", "1")

from strategy.ops import phase5_gate_status as G                     # noqa: E402

_fails = []


def check(label, cond):
    print("%s %s" % ("[OK]  " if cond else "[FAIL]", label))
    if not cond:
        _fails.append(label)


def _fake_db(root, daily):
    """daily: [(YYYY-MM-DD, net원)] — 하루 1레그로 단순화."""
    p = os.path.join(root, "trades.db")
    con = sqlite3.connect(p)
    con.execute("create table trades (exit_ts text, net_pnl_krw real, entry_source text)")
    con.executemany("insert into trades values (?,?,'SYSTEM_AUTO')",
                    [("%s 15:00:00" % d, v) for d, v in daily])
    con.commit()
    con.close()
    return p


class _patched(object):
    """TRADES_DB 를 임시 DB 로 갈아끼우고 캐시를 비운다."""

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        from config import settings as _s
        self._orig = getattr(_s, "TRADES_DB", None)
        _s.TRADES_DB = self.path
        G._pnl_cache["at"] = None
        return self

    def __exit__(self, *a):
        from config import settings as _s
        _s.TRADES_DB = self._orig
        G._pnl_cache["at"] = None


def _days(vals, start=1):
    return [("2026-08-%02d" % (start + i), v) for i, v in enumerate(vals)]


# ══════════════════════════════════════════════════════════════════
def test_missing_db_is_unmeasured():
    root = tempfile.mkdtemp(prefix="mireuk_p5_")
    try:
        with _patched(os.path.join(root, "nope.db")):
            st, detail = G._chk_paper_profit(None)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    check("(1) DB 부재는 UNMEASURED — 미충족이 아니다 (%s)" % st, st == G.UNMEASURED)
    check("(1) 사유가 미측정을 말한다", "미측정" in detail)


def test_negative_total_is_open():
    root = tempfile.mkdtemp(prefix="mireuk_p5_")
    try:
        with _patched(_fake_db(root, _days([-50000] * 20))):
            st, detail = G._chk_paper_profit(None)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    check("(2) 통산 음수는 OPEN — 반증은 자동 확정 (%s)" % st, st == G.OPEN)
    check("(2) 금액이 사유에 박힌다 — %s" % detail, "-1,000,000" in detail)


def test_positive_total_is_not_met():
    root = tempfile.mkdtemp(prefix="mireuk_p5_")
    try:
        with _patched(_fake_db(root, _days([50000] * 20))):
            st, detail = G._chk_paper_profit(None)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    check("(3) 통산 양수여도 MET 이 아니다 (%s)" % st, st != G.MET)
    check("(3) UNMEASURED 로 사람에게 넘긴다", st == G.UNMEASURED)
    check("(3) 수동 기록이 필요하다고 말한다", "수동 기록" in detail)


def test_short_window_is_unmeasured():
    root = tempfile.mkdtemp(prefix="mireuk_p5_")
    try:
        with _patched(_fake_db(root, _days([-99999] * 5))):
            st, detail = G._chk_paper_profit(None)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    check("(4) 4주 미달이면 음수여도 UNMEASURED (%s)" % st, st == G.UNMEASURED)
    check("(4) 미달 사실을 말한다", "미달" in detail)


def test_volatility_gate_never_decides():
    root = tempfile.mkdtemp(prefix="mireuk_p5_")
    try:
        for vals in ([10000] * 20, [-10000] * 20, [1000000, -900000] * 10):
            with _patched(_fake_db(root, _days(vals))):
                st, detail = G._chk_daily_vol(None)
                os.remove(os.path.join(root, "trades.db"))
            check("(5) 어떤 입력에도 판정하지 않는다 (%s)" % st, st == G.UNMEASURED)
        check("(5) 합격선 부재를 명시한다", "합격선" in detail)
        check("(5) 재료(표준편차)를 보여 준다", "표준편차" in detail)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_gate_specs_wired():
    specs = {n: chk for n, _s, _t, chk in G._GATE_SPECS}
    check("(6) ①에 checker 가 붙었다", specs[1] is not None)
    check("(6) ④에 checker 가 붙었다", specs[4] is not None)
    check("(6) ②③은 여전히 실측필요(자동 판정 대상 아님)",
          specs[2] is None and specs[3] is None)


if __name__ == "__main__":
    for fn in sorted(
        [v for k, v in list(globals().items()) if k.startswith("test_")],
        key=lambda f: f.__code__.co_firstlineno,
    ):
        print("\n── %s" % fn.__name__)
        fn()
    print("\n" + "=" * 60)
    if _fails:
        print("Phase 5 게이트 실측 회귀 실패 %d건" % len(_fails))
        for f in _fails:
            print("  - %s" % f)
        sys.exit(1)
    print("Phase 5 게이트 실측 회귀 전부 통과")
