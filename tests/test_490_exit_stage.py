# -*- coding: utf-8 -*-
"""[MW0601 490차 / F-I · 기등록 P2-I] `trades.exit_stage` — 손절과 TP1-후 트레일을 가른다.

## 왜 필요한가 (2026-08-24 이상점 1-9)

`exit_reason='하드스톱(틱)'` 한 값이 **두 가지 서로 다른 사건**을 담고 있다:

  · 진짜 손절      — 진입 스톱에 그대로 맞았다 (손실)
  · TP1 후 트레일  — 이익을 지키려고 스톱을 진입가 위로 올린 뒤 잘렸다
                     (실현 손익이 **양수**일 수 있다)

2026-08-24 실측: 최종 청산이 하드스톱·손절 계열인 포지션 **10/10건**, 오염률
66.7%. 이 구분 없이는 「손절률」·「손절폭 초과율」 지표가 통째로 오염된다 —
417차가 레그/포지션 단위를 섞어 인과 없는 상관을 만든 것과 같은 계열이다.

## 🔴 무엇을 바꾸지 않았는가

`exit_reason` **문자열 무변경**. 소비처가 많다 — `[ExitCooldown]` · CB② 연속손절
카운터 · 캠페인 채널 다수. 바꾸면 그 판정들이 조용히 재정의되고 과거 시계열과
불연속이 생긴다(461차 `mdd_pct` 유형). **컬럼만 늘렸다.**

`tp1_protect_offset` 조정도 포함하지 않는다 — 캠페인 [25] 2026-08-08 주간회의
확정 결정(미적용 유지)이며 재론은 주간회의 소관이다.
"""
import ast
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from strategy.position.position_tracker import PositionTracker  # noqa: E402

_C = PositionTracker.classify_exit_stage
_MAIN = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()


# ── 분류 규약 ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("reason,armed,want", [
    # 스톱 계열 — 이 fix 의 본체. 같은 문자열이 armed 여부로 갈린다.
    ("하드스톱(틱)", False, "INITIAL_STOP"),
    ("하드스톱(틱)", True,  "TRAIL_AFTER_TP1"),
    ("하드스톱",     False, "INITIAL_STOP"),
    ("하드스톱",     True,  "TRAIL_AFTER_TP1"),
    # 판정 불가 — 조용히 INITIAL_STOP 으로 밀지 않는다(계측 4원칙 ②)
    ("하드스톱(틱)", None,  "STOP_UNKNOWN"),
    # 손절 계단화 1차 — 스톱과 다른 사건이다
    ("손절1차 조기축소",       False, "TIER1_EARLY"),
    ("손절1차 전량청산(qty1)", False, "TIER1_EARLY"),
    # TP 계열 — armed 와 무관하게 사유가 이긴다
    ("TP1 부분청산 33%", True,  "TP1"),
    ("TP2 부분청산 33%", True,  "TP2"),
    ("TP2(전량)",        True,  "TP2"),
    ("TP3(전량)",        True,  "TP3"),
    # 시간 청산 — 절대원칙 §1 집행 경로. 손절률 분모에 들어가면 안 된다.
    ("15:10 강제청산",         True, "TIME_EXIT"),
    ("15:10 FLAT불일치 강제청산", True, "TIME_EXIT"),
    # 시스템 청산 규칙의 표본이 아닌 것들
    ("수동 전량청산",           False, "MANUAL"),
    ("수동 청산 33%→전량",      False, "MANUAL"),
    ("외부체결(HTS/수동)",      False, "MANUAL"),
    ("미추적체결(pending_miss)", False, "RECOVERY"),
    ("stuck_exit_flat",         False, "RECOVERY"),
    ("stuck_exit_remainder",    False, "RECOVERY"),
    # 미분류 — None(미측정)이 아니라 OTHER 다
    ("듣도보도 못한 사유", False, "OTHER"),
    ("", False, "OTHER"),
    (None, False, "OTHER"),
])
def test_분류_규약(reason, armed, want):
    assert _C(reason, armed) == want


def test_TP1_문자열이_스톱보다_먼저_판정된다():
    """`TP1 부분청산 33%` 에는 '청산'이 들어 있다 — 순서가 뒤바뀌면 TP 가 스톱으로 샌다."""
    for armed in (True, False, None):
        assert _C("TP1 부분청산 33%", armed) == "TP1"


def test_미분류와_미측정은_다른_값이다():
    """`OTHER`(재봤는데 안 맞음) vs NULL(안 잼). 뭉개면 451차 program_* 결함이 된다."""
    assert _C("알 수 없는 사유", False) == "OTHER"
    assert _C("알 수 없는 사유", False) is not None


# ── 실 DB 사유 전수 커버리지 ─────────────────────────────────────────────

def test_실DB의_모든_exit_reason이_분류된다():
    """운영 DB 에 실제로 존재하는 사유 문자열이 전부 라벨을 받아야 한다.
    새 사유가 생겼는데 `OTHER` 로 새면 그 사건은 영영 안 보인다."""
    import sqlite3
    from config.settings import TRADES_DB
    if not os.path.exists(TRADES_DB):
        pytest.skip("trades.db 없음 (이 PC 에 운영 이력이 없다)")
    con = sqlite3.connect("file:%s?mode=ro" % TRADES_DB.replace(os.sep, "/"), uri=True)
    try:
        reasons = [r[0] for r in con.execute(
            "SELECT DISTINCT exit_reason FROM trades WHERE exit_reason IS NOT NULL")]
    finally:
        con.close()
    unclassified = [r for r in reasons if _C(r, False) == "OTHER"]
    assert not unclassified, (
        "실 DB 의 청산 사유 중 미분류가 있다 — 분류기에 분기를 추가할 것: %s"
        % unclassified
    )


# ── 배선 ─────────────────────────────────────────────────────────────────

def test_리셋_전에_라벨을_잡는다():
    """`close_position()` 은 마지막에 `_reset_position()` 을 부른다. 그 뒤에 읽으면
    `partial_1_done` 이 False 라 **모든 스톱이 INITIAL_STOP 으로 보인다**
    (483차 P1-A 와 같은 「리셋 뒤에 읽기」 함정)."""
    src = io.open(os.path.join(_ROOT, "strategy", "position", "position_tracker.py"),
                  encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "close_position":
            lines = src.splitlines()
            last = max(getattr(s, "lineno", node.lineno) or node.lineno
                       for s in ast.walk(node))
            seg = chr(10).join(lines[node.lineno - 1:last])
            i_label = seg.index("classify_exit_stage")
            # ⚠ `self.` 를 붙여 찾는다 — 주석 안의 `_reset_position()` 언급을
            #   호출로 오인하면 이 검사가 자기 자신의 주석에 걸린다.
            i_reset = seg.index("self._reset_position()")
            assert i_label < i_reset, (
                "exit_stage 를 _reset_position() 뒤에 잡는다 — 모든 스톱이 "
                "INITIAL_STOP 으로 기록된다 (490차 F-I 회귀)"
            )
            return
    pytest.fail("close_position() 을 못 찾았다")


def test_trades_INSERT가_정합한다():
    import re
    m = re.search(r'"""INSERT INTO trades\s*\((.*?)\)\s*VALUES \((.*?)\)"""', _MAIN, re.S)
    assert m, "trades INSERT 문을 못 찾았다"
    cols = [c.strip() for c in m.group(1).replace(chr(10), " ").split(",") if c.strip()]
    assert "exit_stage" in cols
    assert len(cols) == m.group(2).count("?"), (
        "컬럼 %d개 vs 플레이스홀더 %d개" % (len(cols), m.group(2).count("?"))
    )
    tree = ast.parse(_MAIN)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_record_trade_result":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and getattr(sub.func, "id", "") == "execute":
                    assert len(sub.args[2].elts) == len(cols), (
                        "값 %d개 vs 컬럼 %d개" % (len(sub.args[2].elts), len(cols))
                    )
                    return
    pytest.fail("_record_trade_result 의 execute() 를 못 찾았다")


def test_exit_reason_문자열은_바꾸지_않았다():
    """🔴 소비처가 많다 — 바꾸면 CB② 연속손절 카운터·캠페인 판정이 조용히 재정의된다."""
    for lit in ('reason="하드스톱(틱)"', 'reason="하드스톱"', 'reason="손절1차 조기축소"'):
        assert lit in _MAIN, "%s 가 사라졌다 — exit_reason 문자열 무변경 규약 위반" % lit


def test_결과_dict에_키가_없으면_NULL이다():
    """`.get("exit_stage")` 여야 한다 — `or "OTHER"` 로 승격하면 「분류기가 안 돌았다」가
    「분류했는데 미분류」로 위장한다."""
    assert 'result.get("exit_stage")' in _MAIN
    assert 'result.get("exit_stage", "OTHER")' not in _MAIN
    assert 'result.get("exit_stage") or' not in _MAIN
