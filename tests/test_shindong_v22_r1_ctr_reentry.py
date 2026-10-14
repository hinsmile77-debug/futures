# -*- coding: utf-8 -*-
"""[MW0602 2026-10-15 · SD-2026-10-15-v2.2] MAIN(FLOWC) R1 반대 방향 재진입 금지 — 회귀 테스트.

고정하는 불변식:
  ① R1 방향일, R1 반대 FLOWC 진입은 **그날 첫 1건만** — 이후 같은 쪽 신호는 진입하지 않는다.
  ② 막힌 신호는 decision.notes 에 남는다(첫 시각 · 분 수 — 계측 4원칙 ③).
  ③ R1 방향 재진입 · R1 보류일 · 섀도(FLOWR60·FLOWF·BRKC 보류일)는 **무변경**.
근거: docs/신동거래_V2/R1역방향_손실방어_MW0602-20261015.md (10/07 · 10/14 패턴).
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tests"))

from strategy.shindong import engine, families, spec  # noqa: E402
from test_604_shindong_v2 import _flat, _flow, _levels  # noqa: E402

# 09:05 콜−풋 −300 → FLOWC 매수(역방향) 1100 · 09:20 고가 1112 → 익절 12pt → 신호는 계속 켜져 있다
_PATH = {"09:20": (1112.0, 1100.0, 1110.0)}


def _day(pre):
    flow = _flow(lambda k: -300.0 if k >= "09:05" else 0.0, pre=pre)
    return engine.DayFrame(_flat(path=_PATH), flow)


def test_counter_r1_reentry_is_blocked_and_noted():
    r = families.run_family_day(_day(pre=+400.0), _levels(), "flowc")   # R1: 콜−풋 +400 → 하방(−1)
    assert r["decision"]["bias"] == -1
    assert [(t["entry_ts"], t["side"]) for t in r["trades"]] == [("09:05", 1)], "R1 반대 첫 1건만"
    assert r["trades"][0]["legs"][0]["reason"] == "TP1"
    note = [n for n in r["decision"]["notes"] if n.startswith("[v2.2] R1 반대 재진입 차단")]
    assert len(note) == 1 and "첫 09:21" in note[0] and "R1 하방" in note[0]


def test_hold_day_is_unchanged():
    r = families.run_family_day(_day(pre=0.0), _levels(), "flowc")      # R1 보류
    assert r["decision"]["bias"] == 0
    assert [t["entry_ts"] for t in r["trades"]][:2] == ["09:05", "09:21"], "보류일은 종전처럼 재진입"
    assert not [n for n in r["decision"]["notes"] if "v2.2" in n]


def test_r1_aligned_reentry_is_unchanged():
    r = families.run_family_day(_day(pre=-400.0), _levels(), "flowc")   # R1 상방(+1) — 매수가 R1 방향
    assert r["decision"]["bias"] == 1
    assert [t["entry_ts"] for t in r["trades"]][:2] == ["09:05", "09:21"]


def test_guard_off_reproduces_v21():
    old = spec.FLOW_R1_CTR_REENTRY_BLOCK
    try:
        spec.FLOW_R1_CTR_REENTRY_BLOCK = False
        r = families.run_family_day(_day(pre=+400.0), _levels(), "flowc")
        assert [t["entry_ts"] for t in r["trades"]][:2] == ["09:05", "09:21"], "가드를 끄면 v2.1 과 같다"
    finally:
        spec.FLOW_R1_CTR_REENTRY_BLOCK = old


def test_guard_is_main_only():
    """섀도는 무변경 — MAIN 의 family("flowc") 경로만 가드를 켠다."""
    import inspect
    src = inspect.getsource(families.run_family_day)
    assert src.count("r1_guard=S.FLOW_R1_CTR_REENTRY_BLOCK") == 1
    assert 'trades = flowc()' in src, "BRKC 보류일 대체는 가드 없이 부른다"
    for fam in ("flowr60", "flowf"):
        blk = src[src.index('family == "%s"' % fam):][:600]
        assert "ctr_max" not in blk and "r1_bias" not in blk
