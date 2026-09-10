# -*- coding: utf-8 -*-
"""[MW0601 555차] GP 가상 청산 → 손익 추이 패널 갱신 트리거의 불변식.

🔴 이 결함의 지문은 「차트는 맞는데 패널만 낡았다」다
----------------------------------------------------
2026-09-10 실측:

    09:22 → 10:52  GP_LONG_GB90 청산  −17.1364pt
    11:09 → 12:39  GP_LONG_GB90 청산   +8.1841pt
    12:47 →  —     GP_LONG_GB90 보유 중

    12:18:02  마지막 **실거래** 청산 → `_refresh_pnl_history()` (마지막 갱신)
              이후 FLAT → 잔고 폴링 SLEEP → 브로커 푸시 경로의 갱신도 멈춤
    13:17     패널: 「GP 1건 · −856,820원」 / 차트: 「GP 3건 (보유 1)」

DB 에는 2건이 다 있었고 패널 조회 조건(`exit_ts NOT NULL AND pnl_pt NOT NULL`)으로도
2건이 잡혔다. 즉 **데이터 결손이 아니라 표시 지연**이었다. 원인은 하나다 —
`run_shadow()` 가 `None` 을 돌려줘 **가상 청산에 소비자가 붙을 수 없었다.**

FP-CRITICAL 죽은 게이트(2개월 PSI=0.0)·TOX 죽은 섀도(한 달 무소비)와 같은 계열이며,
GP 배너가 "GP 섀도 N건이 합산돼 있다"고 **개수까지 단언**하는 만큼 계측 4원칙 ④
(폴백/낡은 값이 정상값처럼 보인다)에 정확히 해당한다.

이 파일이 고정하는 것:
  ① `run_shadow()` 는 **이번 봉에 DB 기입된 청산의 도전자 id 목록**을 돌려준다
  ② DB 기입 실패는 그 목록에 들어가지 않는다(실패를 「청산됨」으로 세지 않는다)
  ③ 청산이 없는 봉은 빈 목록 — 소비자가 매분 90일 조회를 돌지 않는다
  ④ `main.py` 의 소비자 배선이 살아 있다(`_gp_shadow_ids` 명시 초기화 + 호출)

실행:
    conda run -n py37_32 python -m pytest tests/test_555_gp_panel_refresh_trigger.py -v
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

from challenger.challenger_engine import ChallengerEngine  # noqa: E402
from challenger.variants.base_challenger import (  # noqa: E402
    ChallengerTrade, ExitReason,
)
from config.settings import VALIDATION_CAMPAIGN  # noqa: E402

_GP_IDS = set(VALIDATION_CAMPAIGN["gp_rule_challenger_ids"].values())
_TS = "2026-09-10 12:39:00"


class _StubDB(object):
    """청산 기입만 흉내내는 최소 스텁. `fail=True` 면 close_trade 가 던진다."""

    def __init__(self, fail=False):
        self.fail = fail
        self.closed = []
        self.signals = []

    def close_trade(self, trade_id, exit_ts, exit_price, pnl_pt, exit_reason,
                    cost_ctx=None):
        if self.fail:
            raise RuntimeError("disk I/O error (의도된 실패)")
        self.closed.append(trade_id)

    def insert_signals_bulk(self, signals, regime=None):
        self.signals.extend(signals or [])

    def count_entries_on(self, cid, day):
        return 0


class _StubChallenger(object):
    """`should_exit()` 가 항상 청산을 내는 도전자. 진입은 하지 않는다."""

    GRADE_NA = True
    MAX_PER_DAY = None
    FORCE_EXIT_TIME = "15:05"

    def __init__(self, cid, exit_now=True):
        self.challenger_id = cid
        self.name_kr = cid
        self._exit_now = exit_now

    def observe(self, features, context):
        pass

    def should_exit(self, trade, current_price, current_ts, atr=None):
        return ExitReason.TIME if self._exit_now else None

    def generate_signal(self, features, context):
        class _Sig(object):
            direction = 0
            grade = "X"
            challenger_id = self.challenger_id
        return _Sig()


class _StubRegistry(object):
    def __init__(self, challengers):
        self._c = list(challengers)

    def active_challengers(self):
        return self._c

    def ids(self):
        return [c.challenger_id for c in self._c]

    def register(self, inst):
        pass

    def get_regime_champion(self, regime):
        return None


def _engine(challengers, fail=False):
    db = _StubDB(fail=fail)
    eng = ChallengerEngine(db=db, registry=_StubRegistry(challengers), recover=False)
    for c in challengers:
        eng._open_trades[c.challenger_id] = ChallengerTrade(
            trade_id=1, challenger_id=c.challenger_id,
            entry_ts="2026-09-10 11:09:00", direction=1, entry_price=1096.36,
            grade="A", atr_at_entry=1.0,
        )
    return eng, db


def _run(eng):
    return eng.run_shadow(
        {"atr": 1.0},
        {"close": 1104.8},
        {"ts": _TS, "atr": 1.0, "regime": "혼합", "candle": {"close": 1104.8}},
    )


# ── ① 청산이 난 봉은 그 도전자 id 를 돌려준다 ────────────────────────────────
def test_run_shadow_returns_closed_challenger_ids():
    cid = sorted(_GP_IDS)[0]
    eng, db = _engine([_StubChallenger(cid)])
    assert _run(eng) == [cid]
    assert db.closed == [1], "DB 기입이 실제로 일어나야 한다"


# ── ② DB 기입 실패는 「청산됨」으로 세지 않는다 ──────────────────────────────
def test_failed_db_write_is_not_reported_as_closed():
    """실패를 돌려주면 소비자가 「갱신했는데 값이 안 변한다」를 겪는다(계측 4원칙 ②)."""
    cid = sorted(_GP_IDS)[0]
    eng, db = _engine([_StubChallenger(cid)], fail=True)
    assert _run(eng) == []
    assert db.closed == []
    # 포지션은 닫힌 것으로 처리된다 — 반환값만 보수적이다.
    assert eng._open_trades[cid] is None


# ── ③ 청산이 없는 봉은 빈 목록 ──────────────────────────────────────────────
def test_no_exit_bar_returns_empty():
    """빈 목록이어야 소비자가 매분 90일 조회를 돌지 않는다."""
    cid = sorted(_GP_IDS)[0]
    eng, _db = _engine([_StubChallenger(cid, exit_now=False)])
    assert _run(eng) == []


# ── ④ 예외가 나도 죽지 않고 목록을 돌려준다 ─────────────────────────────────
def test_run_shadow_swallows_exception_and_returns_list():
    class _Boom(_StubChallenger):
        def should_exit(self, *a, **k):
            raise RuntimeError("boom")

    eng, _db = _engine([_Boom(sorted(_GP_IDS)[0])])
    out = _run(eng)
    assert isinstance(out, list), "예외 경로에서도 반환 타입은 목록이다"


# ── ⑤ main.py 소비자 배선이 살아 있는가 ─────────────────────────────────────
#
# 🔴 이 프로젝트가 반복해서 당한 것은 「계산은 하는데 아무도 안 본다」이다.
#   ①~④ 가 다 통과해도 호출부가 반환값을 버리면 결함은 그대로 재발한다.
def test_main_consumes_run_shadow_return():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()

    assert re.search(r"=\s*self\.challenger_engine\.run_shadow\(", src), (
        "main.py 가 run_shadow() 반환값을 받지 않는다 — 갱신 트리거가 죽는다")
    assert "self._gp_shadow_ids = frozenset(" in src, (
        "_gp_shadow_ids 는 __init__ 에서 명시 초기화해야 한다"
        " — getattr 폴백 금지(계측 4원칙 ④)")
    assert re.search(
        r"self\._gp_shadow_ids\.intersection\(_shadow_closed\)[\s\S]{0,400}?"
        r"self\._refresh_pnl_history\(\)", src), (
        "GP 청산 시 _refresh_pnl_history() 를 부르는 배선이 없다")
    assert "".join(["getattr(self, ", '"_gp_shadow_ids"']) not in src, (
        "런타임 상태를 기본값 폴백으로 읽지 말 것(계측 4원칙 ④)."
        " ⚠ 이 리터럴을 소스에 그대로 적으면 test_457 스캐너가 오탐하므로 조립해서 쓴다")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
