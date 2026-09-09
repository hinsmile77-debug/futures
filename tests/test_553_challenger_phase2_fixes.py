# -*- coding: utf-8 -*-
"""[MW0601 553차 / Phase 2] challenger 엔진 선결 결함 5건의 회귀 가드.

왜 이 5건인가
-------------
GP 규칙 섀도(Phase 3)는 기존 `challenger/` 프레임워크 위에 올라간다. 그 프레임워크가
들고 있던 결함을 그대로 상속하면 **GP 손익 기록을 처음부터 못 믿는다.**

  ⓐ 🔴 **미청산 누수** — 실측 28건 중 **3건(10.7%)** 이 `exit_ts=NULL` 영구 미청산.
       원인 ① 엔진 안전망 `FORCE_EXIT_TIME="15:10"` 이 **도달 불가**(파이프라인이
       15:10 이후 봉을 안 준다. 마지막 처리 봉 15:08)
       원인 ② `_open_trades` 가 **인메모리** — 재시작이 지운다
              (552-10 `_broker_dep_base_today` · 552-11 `entry_source` 와 같은 계열)
       그리고 `_compute_and_save_daily()` 가 청산분만 세므로 그 거래는 집계에서
       **조용히 사라진다**(계측 4원칙 ②). GP 롱은 노출 61.9%라 치명적이다.
  ⓑ **수수료가 키움 잔재** `1.5e-05` — CYBOS 실제의 1/6.54 (493차와 같은 사건)
  ⓒ **슬리피지 축 없음** (계측 4원칙 ⑤)
  ⓓ 강제청산 시각이 모듈 상수 — 도전자별(GP 15:05) 지정 불가
  ⓔ 진입 게이트가 `grade in ("A","B")` 고정 — 등급 없는 규칙은 **등급을 위장**하게 된다

실행:
    conda run -n py37_32 python -m pytest tests/test_553_challenger_phase2_fixes.py -v
"""
import ast
import io
import os
import sqlite3
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

from challenger import challenger_cost as CC  # noqa: E402
from challenger.challenger_db import ChallengerDB  # noqa: E402
from challenger.challenger_engine import ChallengerEngine  # noqa: E402
from challenger.variants.base_challenger import (  # noqa: E402
    BaseChallenger, ChallengerSignal, ChallengerTrade, ExitReason,
)
from config.constants import BROKER_CHANNEL_SPECS, MINI_FUTURES_TICK_SIZE  # noqa: E402

_CH_DIR = os.path.join(_ROOT, "challenger")


def _read(p):
    with io.open(p, encoding="utf-8") as fh:
        return fh.read()


def _py_files(root):
    out = []
    for dirpath, _d, files in os.walk(root):
        if "__pycache__" in dirpath:
            continue
        out += [os.path.join(dirpath, f) for f in files if f.endswith(".py")]
    return out


# ── ⓑⓒ 비용 모델 ────────────────────────────────────────────────────────────

def test_no_legacy_kiwoom_rate_left_in_challenger_package():
    """🔴 `0.000015` 는 키움 잔재다. 정의(LEGACY_KIWOOM_RATE)를 빼면 어디에도 없어야 한다.

    ⚠ 문자열 검색으로는 안 된다 — 「이 값은 키움 잔재다」라고 **설명하는 주석**까지
      잡힌다(초판이 그렇게 깨졌다. `test_pure_function_has_no_numpy` 와 같은 실수).
      **AST 로 실제 숫자 리터럴만** 본다.
    """
    hits = []
    for p in _py_files(_CH_DIR):
        if os.path.basename(p) == "challenger_cost.py":
            continue          # 그 파일만 「교체 대상」으로 값을 보관한다
        try:
            tree = ast.parse(_read(p))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Num) and isinstance(node.n, float):
                if abs(node.n - CC.LEGACY_KIWOOM_RATE) < 1e-12:
                    hits.append("%s:%d" % (os.path.relpath(p, _ROOT), node.lineno))
    assert not hits, "키움 잔재 요율 리터럴이 남아 있다: %s" % hits


def test_cost_is_derived_from_settings_not_pinned():
    """핀값 금지(493차) — 채널이 바뀌면 값도 따라와야 한다."""
    from config.settings import BROKER_CHANNEL, FUTURES_COMMISSION_RATE
    ctx = CC.cost_context()
    assert ctx["broker_channel"] == BROKER_CHANNEL
    assert ctx["one_way_rate"] == FUTURES_COMMISSION_RATE
    assert ctx["broker_channel"] in BROKER_CHANNEL_SPECS, (
        "채널명이 스펙에 없는 값이다 — 감지가 폴백으로 빠졌을 수 있다"
        "(초판이 detect_broker_channel() 의 튜플 반환을 놓쳐 UNKNOWN 을 찍었다).")


def test_roundtrip_cost_includes_slippage():
    """수수료만 빼면 왕복비용이 낙관 쪽으로 틀린다(계측 4원칙 ⑤)."""
    ctx = CC.cost_context()
    zero_slip = dict(ctx, slip_ticks_per_side=0.0)
    with_slip = CC.roundtrip_cost_pt(1050.0, 1050.0, ctx)
    without = CC.roundtrip_cost_pt(1050.0, 1050.0, zero_slip)
    assert with_slip > without
    assert with_slip - without == pytest.approx(
        2 * ctx["slip_ticks_per_side"] * MINI_FUTURES_TICK_SIZE)


@pytest.mark.parametrize("channel,expect_pt", [("CYBOS", 0.246018), ("CREON", 0.079900)])
def test_channel_split_reference_values(channel, expect_pt):
    """CYBOS·CREON 왕복비용은 **3.08배** 차이다 — 합치면 판정이 뒤집힌다."""
    rate = BROKER_CHANNEL_SPECS[channel]["one_way_commission_rate"]
    ctx = {"one_way_rate": rate, "tick_size": MINI_FUTURES_TICK_SIZE,
           "slip_ticks_per_side": 1.0, "broker_channel": channel}
    assert CC.roundtrip_cost_pt(1050.0, 1050.0, ctx) == pytest.approx(expect_pt, abs=1e-6)


def test_cost_is_much_higher_than_the_legacy_model():
    """구 모델 대비 배수를 고정 — 값이 조용히 되돌아가면 깨진다."""
    ctx = CC.cost_context()
    new = CC.roundtrip_cost_pt(1050.0, 1050.0, ctx)
    old = 2 * 1050.0 * CC.LEGACY_KIWOOM_RATE
    assert new / old > 5.0


def test_fallback_picks_the_expensive_side():
    """감지 실패 시 싼 쪽으로 폴백하면 가상손익이 조용히 부푼다."""
    src = _read(os.path.join(_CH_DIR, "challenger_cost.py"))
    assert "max(float(v[\"one_way_commission_rate\"])" in src


# ── 공식 일원화 ─────────────────────────────────────────────────────────────

def test_single_pnl_formula():
    """같은 공식이 두 벌 있었고 둘 다 틀렸다 — 한 벌로 모았는지 고정."""
    eng_src = _read(os.path.join(_CH_DIR, "challenger_engine.py"))
    assert "def _calc_pnl" not in eng_src, "엔진에 사본 공식이 되살아났다"
    base_src = _read(os.path.join(_CH_DIR, "variants", "base_challenger.py"))
    assert "COMMISSION_RATE" not in base_src, "Base 에 요율 상수가 되살아났다"
    assert "calc_pnl_pt" in base_src, "Base 가 공용 비용 모듈에 위임해야 한다"


def test_base_calc_pnl_matches_shared_module():
    t = ChallengerTrade(None, "X", "2026-09-09 10:00:00", 1, 1050.0, "A", 3.0)

    class _Stub(BaseChallenger):
        challenger_id = "X"

        def generate_signal(self, features, context):
            return None

    assert _Stub().calc_pnl(t, 1051.0) == CC.calc_pnl_pt(1, 1050.0, 1051.0)


# ── ⓓ 도전자별 강제청산 시각 ────────────────────────────────────────────────

def test_force_exit_time_is_per_challenger():
    assert BaseChallenger.FORCE_EXIT_TIME == "15:10", "기본값은 절대원칙 §1 그대로"
    assert ChallengerEngine._is_force_exit_time("2026-09-09 15:06:00", "15:05") is True
    assert ChallengerEngine._is_force_exit_time("2026-09-09 15:06:00", "15:10") is False
    # 인자를 안 주면 종전과 같은 동작
    assert ChallengerEngine._is_force_exit_time("2026-09-09 15:11:00") is True


def test_engine_reads_challenger_attribute_not_getattr_fallback():
    """계측 4원칙 ④ — Base 가 항상 정의하므로 getattr 폴백을 쓰지 않는다."""
    src = _read(os.path.join(_CH_DIR, "challenger_engine.py"))
    assert "challenger.FORCE_EXIT_TIME" in src
    assert 'getattr(challenger, "FORCE_EXIT_TIME"' not in src


# ── ⓔ 등급 위장 방지 ────────────────────────────────────────────────────────

def test_grade_na_declaration_exists_and_defaults_false():
    assert BaseChallenger.GRADE_NA is False


def test_engine_gate_honours_grade_na():
    src = _read(os.path.join(_CH_DIR, "challenger_engine.py"))
    assert "challenger.GRADE_NA or signal.grade in" in src, (
        "등급 없는 도전자가 grade='A' 를 지어내야 통과하는 구조가 남아 있다")


# ── ⓐ 미청산 누수 — 실제 동작 ──────────────────────────────────────────────

class _StubChallenger(BaseChallenger):
    challenger_id = "T_STUB"
    name_kr = "테스트 스텁"
    GRADE_NA = True
    FORCE_EXIT_TIME = "15:05"

    def __init__(self, direction=1):
        super(_StubChallenger, self).__init__()
        self._dir = direction

    def generate_signal(self, features, context):
        return ChallengerSignal(
            ts=context.get("ts", ""), challenger_id=self.challenger_id,
            direction=self._dir, confidence=0.0, grade="-",
            entry_price=None, signal_meta={"rule": "stub", "grade_na": True})

    def should_exit(self, trade, current_price, current_ts, atr=None):
        return None          # 스스로는 절대 청산하지 않는다 — 누수를 만들어 본다


@pytest.fixture
def tmp_engine():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = ChallengerDB(db_path=path)
    eng = ChallengerEngine(db=db, recover=False)
    stub = _StubChallenger()
    eng.registry.register(stub)
    eng._open_trades[stub.challenger_id] = None
    yield eng, db, path, stub
    try:
        os.remove(path)
    except OSError:
        pass


def _bar(ts, close):
    return ({}, {"close": close}, {"ts": ts, "atr": 3.0, "regime": "혼합"})


def test_open_trade_is_force_closed_at_daily_close(tmp_engine):
    """🔴 마감에 남은 포지션이 닫혀야 한다 — 안 닫히면 집계에서 사라진다."""
    eng, db, path, stub = tmp_engine
    f, c, ctx = _bar("2026-09-09 10:00:00", 1050.0)
    eng.run_shadow(f, c, ctx)
    assert eng._open_trades[stub.challenger_id] is not None, "가상 진입이 안 됐다"
    f, c, ctx = _bar("2026-09-09 14:00:00", 1055.0)
    eng.run_shadow(f, c, ctx)

    eng.update_daily_metrics("2026-09-09")

    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM challenger_trades WHERE challenger_id=?",
                      (stub.challenger_id,)).fetchone()
    assert row["exit_ts"] is not None, "미청산이 남았다"
    assert row["exit_reason"] == ExitReason.EOD_FORCE
    assert row["exit_price"] == pytest.approx(1055.0), "그날 마지막 종가로 닫아야 한다"
    assert row["commission_rate_used"] is not None, "비용 세대가 행에 안 남았다"
    con.close()


def test_force_close_runs_before_aggregation(tmp_engine):
    """집계보다 **먼저** 닫혀야 그 거래가 일별 집계에 들어간다."""
    eng, db, path, stub = tmp_engine
    f, c, ctx = _bar("2026-09-09 10:00:00", 1050.0)
    eng.run_shadow(f, c, ctx)
    eng.update_daily_metrics("2026-09-09")
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    m = con.execute("SELECT * FROM challenger_daily_metrics WHERE challenger_id=?",
                    (stub.challenger_id,)).fetchone()
    con.close()
    assert m is not None and m["trade_count"] == 1, (
        "강제마감이 집계 뒤에 돌면 그 거래가 통계에서 사라진다")


def test_no_close_price_does_not_invent_a_value(tmp_engine):
    """마지막 종가가 없으면 **지어내지 않는다** — 다음 기동 복구가 처리한다."""
    eng, db, path, stub = tmp_engine
    trade = ChallengerTrade(None, stub.challenger_id, "2026-09-09 10:00:00",
                            1, 1050.0, "-", 3.0)
    trade.trade_id = db.insert_trade(trade)
    eng._open_trades[stub.challenger_id] = trade
    eng._last_close = None                      # 봉을 한 번도 못 봤다
    eng.update_daily_metrics("2026-09-09")
    con = sqlite3.connect(path)
    row = con.execute("SELECT exit_ts FROM challenger_trades").fetchone()
    con.close()
    assert row[0] is None, "종가를 모르는데 값을 지어내 닫았다"


def test_restart_adopts_todays_open_trade(tmp_engine):
    """재기동 승계 — 오늘 것은 인메모리로 되살린다(552-10 계열 차단)."""
    eng, db, path, stub = tmp_engine
    from datetime import datetime as _dt
    today = _dt.now().strftime("%Y-%m-%d")
    trade = ChallengerTrade(None, "B_OFI_REVERSAL", today + " 10:00:00",
                            1, 1050.0, "A", 3.0)
    trade.trade_id = db.insert_trade(trade)

    eng2 = ChallengerEngine(db=db)               # recover=True 기본
    adopted = eng2._open_trades.get("B_OFI_REVERSAL")
    assert adopted is not None, "오늘 미청산 행을 승계하지 않았다"
    assert adopted.trade_id == trade.trade_id
    assert adopted.entry_price == pytest.approx(1050.0)


def test_stale_open_trade_is_reconstructed_and_marked(tmp_engine):
    """이전 날짜 미청산은 재구성 청산하되 **관측값이 아님을 사유로 남긴다**."""
    eng, db, path, stub = tmp_engine
    trade = ChallengerTrade(None, "B_OFI_REVERSAL", "2026-09-08 10:00:00",
                            1, 1050.0, "A", 3.0)
    trade.trade_id = db.insert_trade(trade)

    ChallengerEngine(db=db)

    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM challenger_trades WHERE id=?",
                      (trade.trade_id,)).fetchone()
    con.close()
    if row["exit_ts"] is None:
        pytest.skip("raw_candles 에 2026-09-08 정규장 봉이 없다(신규 클론)")
    assert row["exit_reason"] == ExitReason.EOD_FORCE_RECON, (
        "재구성 청산가를 관측값과 같은 사유로 적으면 안 된다(계측 4원칙 ④)")
    assert row["commission_rate_used"] is not None


def test_duplicate_open_trades_for_one_challenger_are_collapsed(tmp_engine):
    """엔진 불변식은 도전자당 1포지션이다 — 2건이면 최신만 남긴다."""
    eng, db, path, stub = tmp_engine
    from datetime import datetime as _dt
    today = _dt.now().strftime("%Y-%m-%d")
    for hh in ("10:00:00", "11:00:00"):
        t = ChallengerTrade(None, "B_OFI_REVERSAL", today + " " + hh, 1, 1050.0, "A", 3.0)
        t.trade_id = db.insert_trade(t)

    eng2 = ChallengerEngine(db=db)
    adopted = eng2._open_trades.get("B_OFI_REVERSAL")
    assert adopted is not None
    assert adopted.entry_ts.endswith("11:00:00"), "최신 1건만 승계해야 한다"


def test_recovery_is_skippable_for_tests():
    """`recover=False` 가 있어야 테스트가 실 DB 를 건드리지 않는다."""
    import inspect
    sig = inspect.signature(ChallengerEngine.__init__)
    assert "recover" in sig.parameters


# ── 통합 불변식 ─────────────────────────────────────────────────────────────

def test_live_db_has_no_orphan_open_trades():
    """실 DB 회귀 — 553차 Phase 2 정규화 이후 미청산 0건이어야 한다."""
    from config.settings import CHALLENGER_DB
    if not os.path.exists(CHALLENGER_DB):
        pytest.skip("challenger.db 없음")
    con = sqlite3.connect("file:%s?mode=ro" % CHALLENGER_DB, uri=True)
    n_open = con.execute(
        "SELECT COUNT(*) FROM challenger_trades WHERE exit_ts IS NULL").fetchone()[0]
    n_legacy = con.execute(
        "SELECT COUNT(*) FROM challenger_trades "
        "WHERE exit_ts IS NOT NULL AND commission_rate_used IS NULL").fetchone()[0]
    con.close()
    assert n_open == 0, "미청산 %d건 — 마감/복구 경로가 새고 있다" % n_open
    assert n_legacy == 0, (
        "비용 세대 미표기 %d건 — scripts/challenger_cost_normalize.py --apply 필요" % n_legacy)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
