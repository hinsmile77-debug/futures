"""[MW0602 459차 F1] 승패 집계 단위 — 레그 → 포지션 회귀 테스트.

지키려는 불변식 — **승패는 포지션당 1회, 레그 누적 Σ(pnl_pts×qty) 총합으로
판정한다.** 종전에는 최종 레그의 pnl_pts만 봐서 (-3.04pt×2, +0.70pt×1)처럼
순손실 포지션이 마지막 레그 이익 때문에 승으로 집계됐다(0808 실측:
-273,410원 포지션이 승).

동률 규약: 총합 0.0은 **패** — 종전 `>0` 판정과 같은 방향(과거 통계 불연속
방지, 변경 금지).

실행: python tests/test_459_position_winloss_unit.py   (COM/브로커 불필요)
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

from config.constants import POSITION_LONG, POSITION_SHORT
from strategy.position.position_tracker import PositionTracker

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _open(qty, direction=POSITION_SHORT, price=990.0, raw_direction=None):
    """상태파일 저장을 건드리지 않고 포지션만 연다."""
    pt = PositionTracker(pt_value=50_000)
    pt._save_state = lambda *a, **k: None
    pt.open_position(
        direction=direction, price=price, quantity=qty,
        atr=2.5, grade="A", regime="NEUTRAL", raw_direction=raw_direction,
    )
    return pt


def test_3leg_net_loss_is_one_loss():
    """제안서 재현 케이스: (-3.04pt×2, +0.70pt×1) → 1패 (종전엔 마지막 레그가 승)."""
    pt = _open(3, POSITION_SHORT, 990.0)
    pt.apply_exit_fill(exit_price=993.04, quantity=2, reason="손절1차 조기축소",
                       shrink_initial=True)
    pt.apply_exit_fill(exit_price=989.30, quantity=1, reason="TP1(잔량)")
    st = pt.daily_stats()
    check("트레이드 1건 (레그 아님)", st["trades"] == 1)
    check("순손실 -5.38pt 포지션은 패 (버그 시 승)", st["wins"] == 0)
    check("pnl_pts 누적은 종전과 동일 (-5.38)", abs(st["pnl_pts"] - (-5.38)) < 1e-9)


def test_net_win_with_losing_final_leg():
    """반대 방향 오류도 수정되는지 — 순이익인데 마지막 레그가 손실인 포지션은 승."""
    pt = _open(3, POSITION_LONG, 1000.0)
    pt.apply_exit_fill(exit_price=1002.0, quantity=1, reason="TP1")   # +2.0
    pt.apply_exit_fill(exit_price=999.5, quantity=2, reason="트레일링스톱")  # -0.5×2
    st = pt.daily_stats()
    check("순이익 +1.0pt 포지션은 승 (버그 시 패)", st["trades"] == 1 and st["wins"] == 1)


def test_zero_total_is_loss():
    """동률(총합 0.0) 규약 — 패 (종전 `>0`과 같은 방향, 변경 금지)."""
    pt = _open(2, POSITION_LONG, 1000.0)
    pt.apply_exit_fill(exit_price=1001.0, quantity=1, reason="TP1")   # +1.0
    pt.apply_exit_fill(exit_price=999.0, quantity=1, reason="스톱")    # -1.0
    st = pt.daily_stats()
    check("동률 0.0은 패", st["trades"] == 1 and st["wins"] == 0)


def test_partial_close_then_close_position_path():
    """비체결(partial_close→close_position) 경로도 같은 판정을 쓰는지."""
    pt = _open(3, POSITION_SHORT, 990.0)
    pt.partial_close(exit_price=993.04, qty=2, reason="손절1차")
    pt.close_position(exit_price=989.30, reason="강제청산")
    st = pt.daily_stats()
    check("partial_close+close_position 순손실 → 1패",
          st["trades"] == 1 and st["wins"] == 0)
    check("close_position 경로 pnl 누적 동일", abs(st["pnl_pts"] - (-5.38)) < 1e-9)


def test_forward_stats_judged_independently():
    """역진입 포지션 — 실행 손익은 패, 순방향(신호 방향) 손익은 승으로 갈려야 한다."""
    pt = _open(3, POSITION_SHORT, 990.0, raw_direction=POSITION_LONG)
    pt.apply_exit_fill(exit_price=993.04, quantity=2, reason="스톱")   # 실행 -3.04×2 / 순방향 +3.04×2
    pt.apply_exit_fill(exit_price=989.30, quantity=1, reason="잔량")   # 실행 +0.70 / 순방향 -0.70
    st, fst = pt.daily_stats(), pt.daily_forward_stats()
    check("실행 통계: 1패", st["trades"] == 1 and st["wins"] == 0)
    check("순방향 통계: 1승 (독립 판정)", fst["trades"] == 1 and fst["wins"] == 1)


def test_single_leg_unchanged():
    """레그 1개짜리 통상 포지션은 종전과 완전 동일해야 한다 (회귀 없음)."""
    pt = _open(1, POSITION_LONG, 1000.0)
    pt.apply_exit_fill(exit_price=1003.0, quantity=1, reason="TP3")
    st = pt.daily_stats()
    check("단일 레그 승 판정 불변", st["trades"] == 1 and st["wins"] == 1)

    pt2 = _open(1, POSITION_LONG, 1000.0)
    pt2.close_position(exit_price=998.0, reason="스톱")
    st2 = pt2.daily_stats()
    check("단일 레그 패 판정 불변", st2["trades"] == 1 and st2["wins"] == 0)


def test_accumulator_resets_between_positions():
    """이전 포지션 누적이 다음 포지션 판정에 새면 안 된다."""
    pt = _open(2, POSITION_LONG, 1000.0)
    pt.apply_exit_fill(exit_price=990.0, quantity=2, reason="스톱")   # -10.0×2 → 패
    pt.open_position(direction=POSITION_LONG, price=1000.0, quantity=1,
                     atr=2.5, grade="A", regime="NEUTRAL")
    pt.apply_exit_fill(exit_price=1000.5, quantity=1, reason="TP1")   # +0.5 → 승
    st = pt.daily_stats()
    check("2포지션 = 2트레이드 1승", st["trades"] == 2 and st["wins"] == 1)


def test_restore_daily_stats_groups_by_entry_ts():
    """재기동 복원 — 레그 행을 entry_ts로 묶어 포지션 단위로 세는지."""
    rows = [
        # 포지션 A: (-3.04×2, +0.70×1) → 1패
        {"entry_ts": "2026-08-10 09:31:00", "exit_price": 993.04,
         "pnl_pts": -3.04, "quantity": 2, "entry_price": 990.0},
        {"entry_ts": "2026-08-10 09:31:00", "exit_price": 989.30,
         "pnl_pts": 0.70, "quantity": 1, "entry_price": 990.0},
        # 포지션 B: 단일 레그 +2.0 → 1승
        {"entry_ts": "2026-08-10 10:00:00", "exit_price": 1002.0,
         "pnl_pts": 2.0, "quantity": 1, "entry_price": 1000.0},
        # entry_ts 없는 레그 — 귀속 불가, 행 단위 폴백 → 1승
        {"entry_ts": "", "exit_price": 1001.0,
         "pnl_pts": 1.0, "quantity": 1, "entry_price": 1000.0},
        # 미청산 행 — 손익·카운트 모두 제외 (종전엔 0pt 1패)
        {"entry_ts": "2026-08-10 11:00:00", "exit_price": None,
         "pnl_pts": None, "quantity": 2, "entry_price": 1000.0},
    ]
    pt = PositionTracker(pt_value=50_000)
    pt._save_state = lambda *a, **k: None
    pt.restore_daily_stats(rows)
    st = pt.daily_stats()
    check("복원: 3트레이드 (A·B·귀속불가, 미청산 제외)", st["trades"] == 3)
    check("복원: 2승 (A는 순손실 패)", st["wins"] == 2)
    check("복원: pnl_pts = -5.38+2.0+1.0 = -2.38",
          abs(st["pnl_pts"] - (-2.38)) < 1e-9)


def test_restore_excludes_open_position_group():
    """보유 중 포지션의 기청산 레그는 손익만 복원하고 승패는 세지 않는다."""
    rows = [
        {"entry_ts": "2026-08-10 09:31:00", "exit_price": 993.04,
         "pnl_pts": -3.04, "quantity": 2, "entry_price": 990.0},
        {"entry_ts": "2026-08-10 10:00:00", "exit_price": 1002.0,
         "pnl_pts": 2.0, "quantity": 1, "entry_price": 1000.0},
    ]
    pt = PositionTracker(pt_value=50_000)
    pt._save_state = lambda *a, **k: None
    # 09:31 진입 포지션이 아직 1계약 보유 중인 상황 (load_state 후 상태 재현)
    pt.status = POSITION_SHORT
    pt.entry_price = 990.0
    pt.quantity = 1
    pt.entry_time = datetime.datetime(2026, 8, 10, 9, 31, 0)
    pt.restore_daily_stats(rows)
    st = pt.daily_stats()
    check("미완결 그룹 제외: 1트레이드(B)만", st["trades"] == 1 and st["wins"] == 1)
    check("미완결 그룹 손익은 누적 (-6.08+2.0)",
          abs(st["pnl_pts"] - (-4.08)) < 1e-9)


def test_accumulator_persists_across_restart():
    """장중 재기동 — 기청산 레그 손익이 상태 JSON으로 살아나 최종 판정에 반영."""
    import json as _json
    import tempfile

    from strategy.position import position_tracker as _mod

    orig = _mod._STATE_FILE
    tmp = os.path.join(tempfile.mkdtemp(), "position_state.json")
    try:
        _mod._STATE_FILE = tmp
        pt = PositionTracker(pt_value=50_000)
        pt.open_position(direction=POSITION_SHORT, price=990.0, quantity=3,
                         atr=2.5, grade="A", regime="NEUTRAL")
        pt.apply_exit_fill(exit_price=993.04, quantity=2, reason="손절1차",
                           shrink_initial=True)   # -3.04×2 누적 후 _save_state

        pt2 = PositionTracker(pt_value=50_000)   # 재기동
        check("재기동 복원 성공", pt2.load_state() is True)
        check("레그 누적기 복원 (-6.08)",
              abs(pt2._pos_acc_pnl_pts - (-6.08)) < 1e-9)
        pt2.apply_exit_fill(exit_price=989.30, quantity=1, reason="잔량")  # +0.70
        st = pt2.daily_stats()
        check("재기동 후 최종 판정도 패 (버그 시 승)", st["wins"] == 0)

        # 구버전 상태파일(누적기 키 없음) 하위호환 — 0.0 폴백
        with open(tmp, "w", encoding="utf-8") as f:
            _json.dump({
                "saved_at": datetime.datetime.now().isoformat(),
                "status": POSITION_SHORT, "entry_price": 990.0,
                "quantity": 1, "initial_quantity": 1, "futures_code": "",
            }, f)
        pt3 = PositionTracker(pt_value=50_000)
        pt3._save_state = lambda *a, **k: None
        check("구버전 상태파일 복원 성공", pt3.load_state() is True)
        check("누적기 키 없으면 0.0 폴백 (종전 동작)",
              pt3._pos_acc_pnl_pts == 0.0)
    finally:
        _mod._STATE_FILE = orig
        if os.path.exists(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    test_3leg_net_loss_is_one_loss()
    test_net_win_with_losing_final_leg()
    test_zero_total_is_loss()
    test_partial_close_then_close_position_path()
    test_forward_stats_judged_independently()
    test_single_leg_unchanged()
    test_accumulator_resets_between_positions()
    test_restore_daily_stats_groups_by_entry_ts()
    test_restore_excludes_open_position_group()
    test_accumulator_persists_across_restart()

    print()
    if FAILURES:
        print("FAILED %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  -", f)
        sys.exit(1)
    print("전부 통과 — 승패 집계 포지션 단위 불변식 유지")
