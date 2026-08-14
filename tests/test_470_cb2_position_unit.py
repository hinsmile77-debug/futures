# -*- coding: utf-8 -*-
"""tests/test_470_cb2_position_unit.py — [MW0602 470차 C1] CB② 포지션 단위 집계 회귀

────────────────────────────────────────────────────────────────────────────
무엇을 지키는가
────────────────────────────────────────────────────────────────────────────
2026-08-14 라이브: 실제 손실 **포지션 2건**에 CB 연속손절 카운터가 **3**까지 갔다.

    13:07:27 체결부분청산 `손절1차 조기축소` → [CB] 연속 손절 1회   ← 레그
    13:07:31 체결청산     `하드스톱(틱)`     → [CB] 연속 손절 2회   ← 같은 포지션
    14:41:43                                → [CB] 연속 손절 3회

지금은 `CB_CONSEC_STOP_LIMIT=9999` 라 무해하지만 **복원 시점이 위험하다.**
임계 2로 되돌리면 그날 13:07:31에 HALT + emergency_exit 가 걸린다 —
실제 손실 포지션이 1건뿐인데도.

불변식:
    (1) 부분청산 손실 레그는 카운터를 **올리지 않는다**
    (2) 부분청산 이익 레그는 카운터를 **리셋하지 않는다** (반대 방향 비대칭 방지)
    (3) 최종 청산은 종전대로 올린다/리셋한다
    (4) 인자 없는 호출은 **종전 동작 그대로** (기존 테스트 2개가 그렇게 부른다)
    (5) 0814 시나리오 재현 — 임계 2에서도 HALT 가 걸리지 않는다
"""
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MIREUK_TEST_MODE", "1")   # 로그·Slack 부작용 차단 (422차)

from unittest.mock import patch                                    # noqa: E402

from config.constants import CB_STATE_HALTED, CB_STATE_NORMAL      # noqa: E402
from safety.circuit_breaker import CircuitBreaker                  # noqa: E402

_fails = []


def check(label, cond):
    print("%s %s" % ("[OK]  " if cond else "[FAIL]", label))
    if not cond:
        _fails.append(label)


def test_partial_leg_does_not_increment():
    cb = CircuitBreaker()
    cb.record_stop_loss(is_partial_leg=True)
    cb.record_stop_loss(is_partial_leg=True)
    check("(1) 부분청산 손실 레그는 카운터를 올리지 않는다",
          cb.status_dict()["consec_stops"] == 0)
    check("(1) 대신 관측 카운터에는 쌓인다",
          getattr(cb, "_partial_loss_legs", 0) == 2)


def test_partial_win_does_not_reset():
    cb = CircuitBreaker()
    cb.record_stop_loss()                      # 최종 손절 1회
    cb.record_win(is_partial_leg=True)         # TP1 부분익절 — 리셋하면 안 된다
    check("(2) 부분청산 이익 레그는 카운터를 리셋하지 않는다",
          cb.status_dict()["consec_stops"] == 1)


def test_final_exit_unchanged():
    cb = CircuitBreaker()
    cb.record_stop_loss()
    cb.record_stop_loss()
    check("(3) 최종 청산은 종전대로 올린다", cb.status_dict()["consec_stops"] == 2)
    cb.record_win()
    check("(3) 최종 이익은 종전대로 리셋한다", cb.status_dict()["consec_stops"] == 0)


def test_default_args_backward_compatible():
    """기존 test_circuit_breaker.py / test_log_isolation.py 가 인자 없이 부른다."""
    with patch("safety.circuit_breaker.CB_CONSEC_STOP_LIMIT", 3):
        cb = CircuitBreaker()
        cb.record_stop_loss()
        cb.record_stop_loss()
        cb.record_stop_loss()
        check("(4) 인자 없는 호출 3회 → 종전대로 HALT", cb.state == CB_STATE_HALTED)


def test_0814_scenario():
    """0814 재현 — 손실 포지션 2건이 임계 2에서 HALT 를 만들면 안 된다.

    포지션A: 손절1차 조기축소(부분) → 하드스톱(최종)   = 손실 포지션 1
    포지션B: 하드스톱(최종)                           = 손실 포지션 2
    종전 코드에서는 레그가 3회로 잡혀 임계 2에서 두 번째 레그(같은 포지션)에 HALT 였다.
    """
    with patch("safety.circuit_breaker.CB_CONSEC_STOP_LIMIT", 2):
        cb = CircuitBreaker()
        cb.record_stop_loss(is_partial_leg=True)     # 13:07:27 손절1차 조기축소
        check("(5) 포지션A 부분 레그 직후 HALT 아님", cb.state == CB_STATE_NORMAL)
        cb.record_stop_loss()                        # 13:07:31 하드스톱 = 손실 포지션 1
        check("(5) 포지션A 최종 청산 후 연속=1", cb.status_dict()["consec_stops"] == 1)
        check("(5) 아직 HALT 아님 — 종전 코드는 여기서 HALT 였다",
              cb.state == CB_STATE_NORMAL)
        cb.record_stop_loss()                        # 14:41:43 = 손실 포지션 2
        check("(5) 손실 포지션 2건째에 비로소 연속=2",
              cb.status_dict()["consec_stops"] == 2)
        check("(5) 임계 2 도달 → 이제 HALT (설계대로)", cb.state == CB_STATE_HALTED)


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 470차 C1] CB② 포지션 단위 집계 회귀 테스트")
    print("=" * 72)
    for fn in (test_partial_leg_does_not_increment,
               test_partial_win_does_not_reset,
               test_final_exit_unchanged,
               test_default_args_backward_compatible,
               test_0814_scenario):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if _fails:
        print("실패 %d건:" % len(_fails))
        for f in _fails:
            print("  - %s" % f)
        sys.exit(1)
    print("470차 C1 CB② 포지션 단위 집계 회귀 테스트 전부 통과")
