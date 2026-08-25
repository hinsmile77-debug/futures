# -*- coding: utf-8 -*-
"""[MW0601 493차 후속5 / F-AA] 청산 결과를 만드는 **모든** 지점이 `exit_stage`를 채운다.

왜 필요한가 (2026-08-25 실측)
-----------------------------
490차 F-I 가 `trades.exit_stage` 컬럼과 `classify_exit_stage()` 를 신설하면서
결과 dict 조립 지점 **2곳**에만 붙였고, `_build_exit_result()` 가 빠졌다.
그 결과 컬럼은 만들어졌는데 **367행 전부 NULL** 이었다 — 컬럼이 있으니 채워지는
줄 알았고, 아무 계측도 "비어 있다"를 말해주지 않았다.

왜 이 값이 필요한가: `exit_reason='하드스톱(틱)'` 한 문자열이 「진짜 손절」과
「TP1 후 트레일(이익 확정)」을 겸한다. 그래서 손절률·손절폭 초과율이 오염된다
(2026-08-24 실측 오염률 **66.7%**). 🔴 `exit_reason` 자체는 못 바꾼다 —
소비처(`[ExitCooldown]`·CB② 연속손절 카운터·캠페인 다수)가 많아 바꾸면 판정이
조용히 재정의된다(461차 `mdd_pct` 유형).

**이 파일은 같은 누락의 재발을 구조적으로 막는다.** 새 조립 지점이 생기면
AST 검사가 깨져 이 문단의 갱신을 강제한다
(474차 `test_473_core_group_reachability.py` · 457차 `test_457_fallback_visibility.py` 관례).
"""
import ast
import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import POSITION_LONG  # noqa: E402
from strategy.position.position_tracker import PositionTracker  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PT_SRC = os.path.join(ROOT, "strategy", "position", "position_tracker.py")


def _str_value(n):
    """py3.7(`ast.Str`) / py3.8+(`ast.Constant`) 양쪽 지원 — 없으면 검사가 공허해진다."""
    if isinstance(n, ast.Str):
        return n.s
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return n.value
    return None


def _dict_keys(node):
    out = set()
    for k in node.keys:
        v = _str_value(k) if k is not None else None
        if v is not None:
            out.add(v)
    return out


def _exit_result_dicts():
    """`exit_reason` 키를 가진 dict 리터럴 = 청산 결과 조립 지점."""
    tree = ast.parse(io.open(PT_SRC, encoding="utf-8").read())
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = _dict_keys(node)
        if "exit_reason" in keys:
            hits.append((node.lineno, keys))
    return hits


def test_every_exit_result_builder_sets_exit_stage():
    """🔴 핵심 불변식 — 청산 결과를 만드는 곳은 전부 `exit_stage`를 채운다.

    새 조립 지점을 추가하고 이 키를 빠뜨리면 여기서 깨진다. 그때 고칠 것은
    테스트가 아니라 **그 조립 지점**이다.
    """
    hits = _exit_result_dicts()
    assert hits, "청산 결과 dict를 하나도 못 찾았다 — 검사기가 죽었다(공허한 통과)"
    missing = [ln for ln, keys in hits if "exit_stage" not in keys]
    assert not missing, (
        "`exit_reason`은 있는데 `exit_stage`가 없는 조립 지점: %s행.\n"
        "  → `self.classify_exit_stage(reason, self._tp1_armed())` 를 추가할 것.\n"
        "  (490차가 2곳만 덮어 `trades.exit_stage` 367행이 전부 NULL이 됐다)"
        % missing)


def test_builder_count_is_what_we_think():
    """조립 지점 수가 바뀌면 알린다 — 위 테스트가 통과해도 설계는 검토 대상이다."""
    hits = _exit_result_dicts()
    assert len(hits) == 3, (
        "청산 결과 조립 지점이 3곳이 아니라 %d곳이다(%s행). "
        "늘었다면 G-3(진입·청산 경로 공통 헬퍼) 논의를 갱신할 것"
        % (len(hits), [ln for ln, _ in hits]))


# ── 실제 값이 채워지는가 ────────────────────────────────────────────────────
def _opened(qty=2, entry=1040.0, atr=1.5):
    pt = PositionTracker(pt_value=50_000)
    pt.open_position(direction=POSITION_LONG, price=entry, quantity=qty,
                     atr=atr, grade="A", regime="NEUTRAL")
    return pt


def test_build_exit_result_value_matches_classifier():
    """반환값이 `classify_exit_stage()` 와 **일치**해야 한다(복붙 드리프트 방지)."""
    pt = _opened()
    res = pt._build_exit_result(exit_price=1038.0, quantity=2,
                                pnl_pts=-2.0, pnl_krw=-200000.0,
                                reason="하드스톱")
    assert "exit_stage" in res
    assert res["exit_stage"] == pt.classify_exit_stage("하드스톱", pt._tp1_armed())


def test_tick_stop_distinguishes_initial_from_trail():
    """같은 `하드스톱(틱)` 이 TP1 전/후로 **다른 단계**가 되는가 — 이 fix의 목적."""
    pt = _opened()
    before = pt._build_exit_result(exit_price=1038.0, quantity=2, pnl_pts=-2.0,
                                   pnl_krw=-200000.0, reason="하드스톱(틱)")["exit_stage"]
    pt.partial_1_done = True                       # TP1 도달 후 트레일 상태
    after = pt._build_exit_result(exit_price=1041.0, quantity=1, pnl_pts=1.0,
                                  pnl_krw=50000.0, reason="하드스톱(틱)")["exit_stage"]
    assert before != after, (
        "TP1 전/후가 같은 단계로 분류된다 — `exit_reason` 오염(66.7%)을 못 가른다")


def test_exit_reason_string_is_unchanged():
    """🚫 `exit_reason` 문자열은 건드리지 않는다.

    소비처가 많아 바꾸면 판정이 조용히 재정의된다(461차 `mdd_pct` 유형).
    F-AA는 **컬럼을 채우는** fix이지 사유를 바꾸는 fix가 아니다.
    """
    pt = _opened()
    res = pt._build_exit_result(exit_price=1038.0, quantity=2, pnl_pts=-2.0,
                                pnl_krw=-200000.0, reason="하드스톱(틱)")
    assert res["exit_reason"] == "하드스톱(틱)"


def test_historical_rows_are_not_backfilled():
    """🚫 과거 NULL 은 **미측정**이며 소급 채우지 않는다(계측 4원칙 ②).

    `partial_1_done` 은 청산 시점에만 알 수 있어 사후 복원이 원리상 불가능하다.
    마이그레이션이 그 컬럼을 채우기 시작했다면 여기서 알린다.
    """
    src = io.open(os.path.join(ROOT, "utils", "db_utils.py"), encoding="utf-8").read()
    assert "UPDATE trades SET exit_stage" not in src, (
        "exit_stage 소급 백필 코드가 생겼다 — 재구성값을 실측으로 위장하면 안 된다. "
        "필요하면 별도 컬럼(exit_stage_reconstructed)에 출처를 표기해 넣을 것")
