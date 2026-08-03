"""[MW0601 421차] `entry_qty` 불변식 회귀 테스트.

지키려는 불변식 — **한 포지션의 모든 청산 레그는 같은 `entry_qty`를 갖고,
그 값은 진입 계약수와 같다.**

왜 필요한가: `initial_quantity`와 `entry_quantity`는 진입 시 같은 값으로
출발하지만 수명이 다르다. 360차 `shrink_initial`(손절1차 조기축소)이 전자를
청산분만큼 깎는데 — TP 진행률 매칭(`_sync_partial_progress`)이 잔여 포지션을
"처음부터 이 수량이었던 새 포지션"으로 봐야 하므로 **의도된 동작이다** —
417차가 `entry_qty` 기록을 하필 그 전자에서 가져가면서 충돌했다.

실측 재현(2026-08-03 10:19 SHORT 3계약):
    trades.id=209  quantity=2  entry_qty=2   ← 3이어야 함
    trades.id=210  quantity=1  entry_qty=1   ← 3이어야 함
`db_utils`의 구버전 백필은 `SUM(quantity) GROUP BY entry_ts`라 3을 넣으므로
라이브 경로와 백필 경로가 서로 다른 값을 만들고 있었다.

이 파일이 깨지면 그 버그가 재발한 것이다. `shrink_initial` 블록에서
`entry_quantity`를 함께 줄이고 싶어졌다면 위 설명을 먼저 읽을 것.

실행: python tests/test_entry_qty_invariant.py   (COM/브로커 불필요)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import POSITION_LONG, POSITION_SHORT
from strategy.position.position_tracker import PositionTracker

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _open(qty, direction=POSITION_SHORT, price=990.0):
    """상태파일 저장을 건드리지 않고 포지션만 연다."""
    pt = PositionTracker(pt_value=50_000)
    pt._save_state = lambda *a, **k: None
    pt.open_position(
        direction=direction, price=price, quantity=qty,
        atr=2.5, grade="A", regime="NEUTRAL",
    )
    return pt


def test_loss_tier1_partial_keeps_entry_qty():
    """08-03 10:19 실측 재현 — 3계약 진입 → 손절1차 2계약 → 잔여 1계약 풀스톱."""
    pt = _open(3)
    check("진입 직후 entry_quantity=3", pt.entry_quantity == 3)

    legs = []
    # 손절1차 조기축소는 1계약씩 두 번 체결됐다(10:20:21, 10:20:22).
    for _ in range(2):
        legs.append(pt.apply_exit_fill(
            exit_price=993.5, quantity=1,
            reason="손절1차 조기축소", shrink_initial=True,
        ))
    # 잔여 1계약 하드스톱(전량 청산 → is_final)
    legs.append(pt.apply_exit_fill(
        exit_price=995.4, quantity=1, reason="하드스톱(틱)",
    ))

    check("레그 3건 생성", len(legs) == 3)
    check("모든 레그의 entry_qty가 동일", len({l["entry_qty"] for l in legs}) == 1)
    check("entry_qty == 진입 계약수 3 (버그 시 2·1로 갈림)",
          all(l["entry_qty"] == 3 for l in legs))
    check("레그별 quantity는 실제 청산 수량 그대로",
          [l["quantity"] for l in legs] == [1, 1, 1])


def test_shrink_initial_still_shrinks():
    """360차 동작을 되돌리지 않았는지 — initial_quantity는 여전히 줄어야 한다."""
    pt = _open(3)
    pt.apply_exit_fill(exit_price=993.5, quantity=2,
                       reason="손절1차 조기축소", shrink_initial=True)
    check("initial_quantity는 3→1로 축소(360차 의도 유지)", pt.initial_quantity == 1)
    check("entry_quantity는 3으로 보존(421차 신규)", pt.entry_quantity == 3)


def test_normal_partial_exit_unaffected():
    """TP1/TP2 같은 통상 부분청산(shrink_initial=False)에서도 동일해야 한다."""
    pt = _open(2, direction=POSITION_LONG, price=1000.0)
    a = pt.apply_exit_fill(exit_price=1002.0, quantity=1, reason="TP1")
    b = pt.apply_exit_fill(exit_price=1004.0, quantity=1, reason="TP2(전량)")
    check("통상 부분청산도 entry_qty 동일", a["entry_qty"] == b["entry_qty"] == 2)


def test_add_position_raises_entry_qty():
    """추가진입은 진입 규모가 실제로 커진 것 — 증가는 정상."""
    pt = PositionTracker(pt_value=50_000)
    pt._save_state = lambda *a, **k: None
    pt.apply_entry_fill(direction=POSITION_LONG, price=1000.0, quantity=1,
                        atr=2.5, grade="A", regime="NEUTRAL")
    check("최초 체결 entry_quantity=1", pt.entry_quantity == 1)
    pt.apply_entry_fill(direction=POSITION_LONG, price=1002.0, quantity=2,
                        atr=2.5, grade="A", regime="NEUTRAL")
    check("추가진입 후 entry_quantity=3", pt.entry_quantity == 3)
    leg = pt.apply_exit_fill(exit_price=1005.0, quantity=3, reason="TP3")
    check("청산 레그 entry_qty=3", leg["entry_qty"] == 3)


def test_legacy_state_restore_falls_back():
    """구버전 상태파일(entry_quantity 키 없음)에서 복원 시 종전 동작 보존.

    운영 중인 data/position_state.json은 건드리지 않는다 — 모듈 전역
    `_STATE_FILE`을 임시 경로로 바꿨다가 되돌린다.
    """
    import datetime as _dt
    import json as _json
    import tempfile

    from strategy.position import position_tracker as _mod

    orig = _mod._STATE_FILE
    tmp = os.path.join(tempfile.mkdtemp(), "position_state.json")
    try:
        _mod._STATE_FILE = tmp
        with open(tmp, "w", encoding="utf-8") as f:
            _json.dump({
                "saved_at": _dt.datetime.now().isoformat(),
                "status": POSITION_SHORT, "entry_price": 990.0,
                "quantity": 2, "initial_quantity": 2,   # entry_quantity 키 없음
                "futures_code": "",
            }, f)

        pt = PositionTracker(pt_value=50_000)
        pt._save_state = lambda *a, **k: None
        check("구버전 상태파일 복원 성공", pt.load_state() is True)
        check("entry_quantity가 initial_quantity로 폴백(구버전 호환)",
              pt.entry_quantity == 2)
    finally:
        _mod._STATE_FILE = orig
        if os.path.exists(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    test_loss_tier1_partial_keeps_entry_qty()
    test_shrink_initial_still_shrinks()
    test_normal_partial_exit_unaffected()
    test_add_position_raises_entry_qty()
    test_legacy_state_restore_falls_back()

    print()
    if FAILURES:
        print("FAILED %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  -", f)
        sys.exit(1)
    print("전부 통과 — entry_qty 불변식 유지")
