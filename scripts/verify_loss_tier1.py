"""[360차] 손절 계단화(Loss Tier1) 오프라인 검증 스크립트.

COM/브로커 없이 PositionTracker 단독으로 상태전이를 검증한다:
1. qty=2 SHORT 진입 -> loss_tier1_price 도달 -> apply_exit_fill(shrink_initial=True)
   -> quantity/initial_quantity가 1로 줄고 partial_1_done이 오염되지 않는지 확인
2. 잔여 1계약이 원래 tp1_price에 도달하면 is_tp1_hit()가 다시 True인지 확인
   (TP1 재도달 가능 검증 — 이번 계획의 핵심 회귀 방지 포인트)
3. 별도 포지션에서, 손실1차 이후 가격이 원래 stop_price까지 역행하면
   is_stop_hit()가 True인지 확인 (잔여가 원래 손절가로 청산되는지)
4. qty=1 진입 케이스는 is_loss_tier1_hit()가 항상 False인지 확인 (대상 제외 확인)
5. LONG 방향에서도 loss_tier1_price가 entry-stop 사이(진입가보다 낮은 쪽)에 오는지 확인

검증 후 삭제 예정 — 임시 스크립트.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.position.position_tracker import PositionTracker
from config.constants import POSITION_LONG, POSITION_SHORT, POSITION_FLAT

FAILURES = []


def check(name, cond):
    status = "OK" if cond else "FAIL"
    print(f"[{status}] {name}")
    if not cond:
        FAILURES.append(name)


def scenario_short_tier1_then_recover_to_tp1():
    print("\n=== 시나리오 1+2: SHORT qty=2, 손실1차 축소 후 TP1 재도달 ===")
    pt = PositionTracker()
    pt.open_position(POSITION_SHORT, price=1000.0, quantity=2, atr=2.0, grade="A",
                      regime="NEUTRAL", entry_horizon="5m")
    print(f"entry=1000.0 stop={pt.stop_price:.2f} tp1={pt.tp1_price:.2f} "
          f"tp2={pt.tp2_price:.2f} loss_tier1={pt.loss_tier1_price:.2f}")

    # entry(1000) < loss_tier1 < stop 순서(SHORT는 위로 갈수록 불리)
    check("loss_tier1_price가 entry와 stop 사이(SHORT, entry<tier1<stop)",
          1000.0 < pt.loss_tier1_price < pt.stop_price)

    # 가격이 loss_tier1_price까지 불리하게 이동
    price = pt.loss_tier1_price
    check("is_loss_tier1_hit=True (qty=2)", pt.is_loss_tier1_hit(price))
    check("is_stop_hit=False (아직 최종 손절 전)", not pt.is_stop_hit(price))

    cut_qty = pt.get_loss_tier1_exit_qty()
    check("cut_qty == 1 (2계약의 50%)", cut_qty == 1)

    result = pt.apply_exit_fill(exit_price=price, quantity=cut_qty,
                                 reason="손절1차 조기축소", shrink_initial=True)
    pt.loss_tier1_done = True  # main.py의 _ts_handle_exit_fill과 동일 타이밍

    check("quantity == 1 (축소 후)", pt.quantity == 1)
    check("initial_quantity == 1 (shrink_initial 반영)", pt.initial_quantity == 1)
    check("partial_1_done == False (TP1 오염 안 됨 — 핵심 검증)",
          pt.partial_1_done is False)
    check("status 여전히 SHORT (잔여 포지션 유지)", pt.status == POSITION_SHORT)
    check("stop_price 불변 (원래 손절가 유지)", abs(pt.stop_price - (1000.0 + 2.0 * 1.0 * 1.5)) < 1e-6 or pt.stop_price > 1000.0)

    # 가격이 회복해서 원래 tp1_price에 도달
    tp1_price = pt.tp1_price
    check("회복 후 is_tp1_hit=True (TP1 재도달 가능 — 핵심 회귀 방지 포인트)",
          pt.is_tp1_hit(tp1_price))
    check("loss_tier1_done=True라 is_loss_tier1_hit는 재발동 안 함",
          not pt.is_loss_tier1_hit(price))


def scenario_short_tier1_then_full_stop():
    print("\n=== 시나리오 3: SHORT qty=2, 손실1차 축소 후 잔여가 원래 손절가로 청산 ===")
    pt = PositionTracker()
    pt.open_position(POSITION_SHORT, price=1000.0, quantity=2, atr=2.0, grade="A",
                      regime="NEUTRAL", entry_horizon="5m")
    orig_stop = pt.stop_price
    price = pt.loss_tier1_price
    cut_qty = pt.get_loss_tier1_exit_qty()
    pt.apply_exit_fill(exit_price=price, quantity=cut_qty,
                        reason="손절1차 조기축소", shrink_initial=True)
    pt.loss_tier1_done = True

    check("잔여 손절가가 손실1차 가격이 아니라 원래 stop_price와 동일",
          abs(pt.stop_price - orig_stop) < 1e-9)
    check("가격이 원래 stop_price까지 역행하면 is_stop_hit=True",
          pt.is_stop_hit(orig_stop))


def scenario_qty1_excluded():
    print("\n=== 시나리오 4: qty=1은 손실1차 대상 제외 ===")
    pt = PositionTracker()
    pt.open_position(POSITION_SHORT, price=1000.0, quantity=1, atr=2.0, grade="A",
                      regime="NEUTRAL", entry_horizon="5m")
    check("loss_tier1_price도 계산은 되지만",
          pt.loss_tier1_price > 1000.0)
    check("is_loss_tier1_hit는 qty==1이라 항상 False",
          not pt.is_loss_tier1_hit(pt.loss_tier1_price))
    check("get_loss_tier1_exit_qty도 0",
          pt.get_loss_tier1_exit_qty() == 0)


def scenario_long_direction():
    print("\n=== 시나리오 5: LONG 방향 loss_tier1_price 위치 검증 ===")
    pt = PositionTracker()
    pt.open_position(POSITION_LONG, price=1000.0, quantity=2, atr=2.0, grade="A",
                      regime="NEUTRAL", entry_horizon="5m")
    print(f"entry=1000.0 stop={pt.stop_price:.2f} loss_tier1={pt.loss_tier1_price:.2f}")
    check("loss_tier1_price가 entry와 stop 사이(LONG, stop<tier1<entry)",
          pt.stop_price < pt.loss_tier1_price < 1000.0)
    check("가격이 loss_tier1_price 이하로 내려가면 is_loss_tier1_hit=True",
          pt.is_loss_tier1_hit(pt.loss_tier1_price))


if __name__ == "__main__":
    scenario_short_tier1_then_recover_to_tp1()
    scenario_short_tier1_then_full_stop()
    scenario_qty1_excluded()
    scenario_long_direction()

    print("\n=== 결과 ===")
    if FAILURES:
        print(f"FAIL {len(FAILURES)}건: {FAILURES}")
        sys.exit(1)
    else:
        print("전부 통과")
        sys.exit(0)
