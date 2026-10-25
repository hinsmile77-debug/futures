# -*- coding: utf-8 -*-
"""[MW0601 713차 / 신동 주체 전환 P1] 미륵 파이프라인 속 신동 부품 — 공유 메서드 추출 회귀.

P1 은 **동작 무변경** 추출이다. 파이프라인과 (P2 의) 경량 분봉 패스가 같은 메서드를 불러야
한쪽만 고쳐지는 「두 벌」이 생기지 않는다(MW0602 Sindong-V4 c3281a9 와 같은 원칙).
계획: docs/신동거래/신동주체전환_구현계획_미륵휴면_MW0601-20261025.md §2-3.
"""
import ast
import io
import os
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "main.py")


def _methods():
    tree = ast.parse(io.open(MAIN, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "TradingSystem":
            return {n.name: n for n in node.body if isinstance(n, ast.FunctionDef)}
    raise AssertionError("TradingSystem 없음")


def _calls(fn):
    out = []
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name) and n.func.value.id == "self"):
            out.append((n.lineno, n.func.attr))
    return [a for _, a in sorted(out)]     # 소스 순서(ast.walk 는 너비 우선이라 순서가 아니다)


SHARED = ("_maybe_compute_levels_0930", "_bar_price_guard",
          "_check_pending_order_timeout", "_push_position_panels")


def test_shared_methods_exist():
    m = _methods()
    for name in SHARED + ("_maybe_compute_levels_0850",):
        assert name in m, name


def test_pipeline_calls_shared_parts_in_order():
    """파이프라인 순서(맥점 → 틱스톱 → 가드 → 대기주문 … → 화면)가 추출 전과 같다."""
    calls = _calls(_methods()["run_minute_pipeline"])
    for name in SHARED + ("_process_tick_stop",):
        assert calls.count(name) == 1, (name, calls.count(name))
    idx = [calls.index(n) for n in ("_maybe_compute_levels_0930", "_process_tick_stop",
                                    "_bar_price_guard", "_check_pending_order_timeout",
                                    "_check_exit_triggers", "_push_position_panels")]
    assert idx == sorted(idx), idx


def test_premarket_calls_0850():
    assert "_maybe_compute_levels_0850" in _calls(_methods()["_on_pre_market_bar"])


def test_blocks_left_pipeline():
    """옮긴 블록이 파이프라인에 남아 있지 않다(두 벌 금지)."""
    text = io.open(MAIN, encoding="utf-8").read()
    m = _methods()
    fn = m["run_minute_pipeline"]
    # py3.7 에는 end_lineno 가 없다 — 다음 메서드의 시작 줄을 끝으로 쓴다
    nxt = min(n.lineno for n in m.values() if n.lineno > fn.lineno)
    body = "\n".join(text.splitlines()[fn.lineno - 1: nxt - 1])
    assert "def run_minute_pipeline" in body and len(body.splitlines()) > 1000
    for frag in ("[Guard-C1] 비정상 가격 분봉 차단", "[PendingOrder] 타임아웃",
                 "09:30 훅 실패", "self.dashboard.update_order_metrics("):
        assert frag not in body, frag


# ── _bar_price_guard 행위 ────────────────────────────────────────────
class _Dash:
    def __init__(self):
        self.ran = 0

    def notify_pipeline_ran(self):
        self.ran += 1


@pytest.fixture()
def guard(monkeypatch):
    import main
    logs = []
    monkeypatch.setattr(main.log_manager, "system", lambda msg, lvl="INFO": logs.append((msg, lvl)))
    obj = types.SimpleNamespace(dashboard=_Dash())
    fn = main.TradingSystem._bar_price_guard
    return (lambda bar, notify=True: fn(obj, bar, "2026-10-26 09:00:00", notify)), obj, logs


def test_guard_pass(guard):
    g, obj, logs = guard
    assert g({"close": 900.5, "high": 901, "low": 899, "volume": 12}) == (900.5, 901.0, 899.0, 12)
    assert obj.dashboard.ran == 0 and logs == []


@pytest.mark.parametrize("bar,tag", [
    ({"close": "x", "high": 1, "low": 1, "volume": 1}, "Guard-C0"),
    ({"close": 0, "high": 1, "low": 1, "volume": 1}, "Guard-C1"),
    ({"close": 900, "high": 899, "low": 901, "volume": 1}, "Guard-C2"),
])
def test_guard_block_notifies(guard, bar, tag):
    g, obj, logs = guard
    assert g(bar) is None
    assert obj.dashboard.ran == 1 and tag in logs[0][0]


def test_guard_block_silent_when_notify_false(guard):
    g, obj, logs = guard
    assert g({"close": 0, "high": 1, "low": 1, "volume": 1}, notify=False) is None
    assert obj.dashboard.ran == 0 and logs == []
