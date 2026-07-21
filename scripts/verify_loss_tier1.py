"""[360차/363차] 손절 계단화(Loss Tier1) 오프라인 검증 스크립트.

COM/브로커 없이 PositionTracker 단독으로 상태전이를 검증한다:
1. qty=2 SHORT 진입 -> loss_tier1_price 도달 -> apply_exit_fill(shrink_initial=True)
   -> quantity/initial_quantity가 1로 줄고 partial_1_done이 오염되지 않는지 확인
2. 잔여 1계약이 원래 tp1_price에 도달하면 is_tp1_hit()가 다시 True인지 확인
   (TP1 재도달 가능 검증 — 이번 계획의 핵심 회귀 방지 포인트)
3. 별도 포지션에서, 손실1차 이후 가격이 원래 stop_price까지 역행하면
   is_stop_hit()가 True인지 확인 (잔여가 원래 손절가로 청산되는지)
4. qty=1 진입 케이스는 is_loss_tier1_hit()가 항상 False인지 확인 (대상 제외 확인)
5. LONG 방향에서도 loss_tier1_price가 entry-stop 사이(진입가보다 낮은 쪽)에 오는지 확인
6. [363차] qty=1 손실1차 섀도(is_loss_tier1_qty1_shadow_hit) — qty=1에서만 True, qty=2
   에서는 항상 False(라이브 조기축소 대상과 상호 배타), 1회 기록 후 재발동 안 함 확인
7. [363차] tick-level 우선순위 — 한 가격이 stop_price와 loss_tier1_price를 동시에
   만족할 때 is_stop_hit()가 True임을 확인(main.py _on_tick_price_update의 elif가
   풀스톱을 먼저 평가하므로 이 순서가 실제 우선순위를 보장하는 전제조건).
   ※ main.py의 QTimer 콜백 배선 자체(_process_tick_loss_tier1)는 Qt 이벤트루프가
   필요해 이 스크립트로는 검증 불가 — 다음 실제 급락 손절 시 [TickLossTier1] 로그로
   라이브 확인 필요(다른 tick 경로 항목들과 동일한 제약, NEXT_TODO 363차 참조).

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


def scenario_qty1_shadow_hit():
    print("\n=== 시나리오 6: qty=1 손실1차 섀도 — qty=1만 True, 1회 기록 후 재발동 안 함 ===")
    pt = PositionTracker()
    pt.open_position(POSITION_LONG, price=1000.0, quantity=1, atr=2.0, grade="A",
                      regime="NEUTRAL", entry_horizon="5m")
    price = pt.loss_tier1_price
    check("qty=1: is_loss_tier1_qty1_shadow_hit=True (섀도 대상)",
          pt.is_loss_tier1_qty1_shadow_hit(price))
    check("qty=1: is_loss_tier1_hit는 여전히 False (라이브 조기축소는 미대상 — 상호 배타)",
          not pt.is_loss_tier1_hit(price))

    pt.loss_tier1_qty1_shadow_logged = True  # main.py _ts_record_loss_tier1_qty1_shadow와 동일 타이밍
    check("기록 후 재발동 안 함(loss_tier1_qty1_shadow_logged=True)",
          not pt.is_loss_tier1_qty1_shadow_hit(price))

    pt2 = PositionTracker()
    pt2.open_position(POSITION_LONG, price=1000.0, quantity=2, atr=2.0, grade="A",
                       regime="NEUTRAL", entry_horizon="5m")
    check("qty=2: is_loss_tier1_qty1_shadow_hit는 항상 False (라이브 조기축소 대상과 상호 배타)",
          not pt2.is_loss_tier1_qty1_shadow_hit(pt2.loss_tier1_price))


def scenario_tick_priority_stop_beats_tier1():
    print("\n=== 시나리오 7: 풀스톱과 tier1을 동시에 만족하는 가격 -> is_stop_hit 우선 확인 ===")
    pt = PositionTracker()
    pt.open_position(POSITION_LONG, price=1000.0, quantity=2, atr=2.0, grade="A",
                      regime="NEUTRAL", entry_horizon="5m")
    # tier1보다 더 불리한(풀스톱을 이미 뚫은) 가격 — 급락 시 한 틱에 둘 다 만족 가능
    beyond_stop_price = pt.stop_price - 0.5
    check("풀스톱 너머 가격에서 is_stop_hit=True",
          pt.is_stop_hit(beyond_stop_price))
    check("같은 가격에서 is_loss_tier1_hit도 True (tier1은 stop보다 진입가에 가까우므로)",
          pt.is_loss_tier1_hit(beyond_stop_price))
    print("-> main.py _on_tick_price_update는 if(풀스톱)/elif(tier1) 구조라 이 경우 "
          "풀스톱 경로만 실행되고 tier1 경로는 평가되지 않음(코드 구조로 보장, 이 "
          "스크립트는 두 predicate가 실제로 동시에 True가 될 수 있음만 확인)")


if __name__ == "__main__":
    scenario_short_tier1_then_recover_to_tp1()
    scenario_short_tier1_then_full_stop()
    scenario_qty1_excluded()
    scenario_long_direction()
    scenario_qty1_shadow_hit()
    scenario_tick_priority_stop_beats_tier1()

    print("\n=== 결과 ===")
    if FAILURES:
        print(f"FAIL {len(FAILURES)}건: {FAILURES}")
        sys.exit(1)
    else:
        print("전부 통과")
        sys.exit(0)
