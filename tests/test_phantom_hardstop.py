"""[MW0602 423차] "유령 하드스톱" 회귀 테스트.

지키려는 불변식 — **스톱을 조인 그 분봉의 고저가로는 봉중 스톱 히트를 판정하지
않는다.** 그 고저가는 조이기 이전에 형성된 값이라, 새 스톱을 소급 적용하면
실제로 닿지 않은 스톱에 걸려 청산된다.

왜 필요한가: 기존 가드(`_ts_check_exit_triggers`의 `_prev_stop_price`)는 그 함수
안에서 `update_trailing_stop()`이 조인 것만 되돌린다. 그런데 TP1 보호전환은
COM 틱 핸들러가 **함수 밖에서 비동기로** `stop_price`를 바꾸므로, 다음 파이프라인
호출 시점엔 이미 조여진 값이 `_prev_stop_price`로 들어와 가드가 무력화된다.

실측 재현(2026-08-03, MW0602 — 비틱 `하드스톱` 청산 8건이 **전부** 이 경로):
    13:49:54  진입 SHORT @ 988.88  (손절 991.00)
    13:50:09  틱 TP1 → stop 991.00 → 988.53 으로 조임
    13:50:55  파이프라인이 분봉 13:50(고가 988.94)으로 히트 판정 → 청산
              ↑ 988.94는 13:50:00~13:50:09, **조이기 이전**에 찍힌 값이다.
분봉 13:50 OHLC 실측: 988.88 / 988.94 / 986.74 / 987.10

이 파일이 깨지면 그 버그가 재발한 것이다. `is_stop_hit_intrabar()`에서
`bar_start` 인자를 떼거나 `stop_updated_at` 갱신을 지우고 싶어졌다면 위 설명을
먼저 읽을 것. **종가 기준 `is_stop_hit()`은 그대로 살아 있으므로 진짜 스톱
히트를 놓치지 않는다** — 다음 봉부터 새 스톱으로 정상 판정된다.

실행: python tests/test_phantom_hardstop.py   (COM/브로커 불필요)
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


def _open(qty=1, direction=POSITION_SHORT, price=988.88, atr=2.0):
    pt = PositionTracker(pt_value=50_000)
    pt._save_state = lambda *a, **k: None
    pt.open_position(
        direction=direction, price=price, quantity=qty,
        atr=atr, grade="A", regime="RISK_ON",
    )
    return pt


def test_0803_1349_short_phantom_blocked():
    """08-03 13:49 SHORT 실측 재현 — 조인 봉에서는 봉중 판정 금지."""
    pt = _open()
    # 진입 직후 스톱을 실측값으로 맞춘다(ATR 배수 계산과 무관하게 시나리오 고정).
    pt.stop_price = 991.00
    bar_start = datetime.datetime(2026, 8, 3, 13, 50, 0)

    # 13:50:09 — 틱 TP1 보호전환으로 스톱을 988.53까지 조인다.
    pt.stop_updated_at = bar_start + datetime.timedelta(seconds=9)
    pt.stop_price = 988.53

    BAR_HIGH, BAR_LOW, BAR_CLOSE = 988.94, 986.74, 987.10

    check("가드 없음(구동작): 유령 히트가 발생한다",
          pt.is_stop_hit_intrabar(BAR_LOW, BAR_HIGH) is True)
    check("가드 적용: 조인 봉의 봉중 판정은 차단된다",
          pt.is_stop_hit_intrabar(BAR_LOW, BAR_HIGH, bar_start=bar_start) is False)
    check("종가 기준 판정은 그대로 살아 있다 (987.10 < 988.53 → 미히트)",
          pt.is_stop_hit(BAR_CLOSE) is False)


def test_next_bar_is_evaluated_normally():
    """다음 봉부터는 새 스톱으로 정상 판정 — 진짜 히트를 삼키면 안 된다."""
    pt = _open()
    bar_start = datetime.datetime(2026, 8, 3, 13, 50, 0)
    pt.stop_updated_at = bar_start + datetime.timedelta(seconds=9)
    pt.stop_price = 988.53

    nxt = bar_start + datetime.timedelta(minutes=1)
    check("다음 봉(13:51)에서 고가가 스톱을 넘으면 정상 히트",
          pt.is_stop_hit_intrabar(987.0, 989.20, bar_start=nxt) is True)
    check("다음 봉에서 고가가 스톱 아래면 미히트",
          pt.is_stop_hit_intrabar(985.2, 987.10, bar_start=nxt) is False)


def test_long_side_symmetry():
    """LONG도 대칭으로 막혀야 한다(저가가 조인 스톱을 뚫는 형태)."""
    pt = _open(direction=POSITION_LONG, price=1000.0)
    bar_start = datetime.datetime(2026, 8, 3, 10, 0, 0)
    pt.stop_updated_at = bar_start + datetime.timedelta(seconds=20)
    pt.stop_price = 1001.0          # 이익 보호로 진입가 위까지 조임

    check("LONG 가드 없음: 유령 히트",
          pt.is_stop_hit_intrabar(1000.2, 1003.0) is True)
    check("LONG 가드 적용: 차단",
          pt.is_stop_hit_intrabar(1000.2, 1003.0, bar_start=bar_start) is False)


def test_untightened_bar_still_hits():
    """스톱을 조이지 않은 봉에서는 가드가 아무것도 바꾸지 않아야 한다."""
    pt = _open()
    pt.stop_price = 991.00
    bar_start = datetime.datetime(2026, 8, 3, 13, 55, 0)
    # 스톱은 훨씬 전(13:49)에 마지막으로 갱신됐다.
    pt.stop_updated_at = datetime.datetime(2026, 8, 3, 13, 49, 54)

    check("이전 봉에서 조인 스톱은 이번 봉 봉중 판정에 정상 적용",
          pt.is_stop_hit_intrabar(989.0, 991.50, bar_start=bar_start) is True)


def test_backward_compat_no_bar_start():
    """bar_start를 안 넘기면 종전과 완전히 동일(하위호환)."""
    pt = _open()
    pt.stop_price = 991.00
    pt.stop_updated_at = datetime.datetime(2026, 8, 3, 13, 50, 9)
    check("bar_start 미지정 시 가드 비활성",
          pt.is_stop_hit_intrabar(989.0, 991.50) is True)


def test_tp1_protect_records_timestamp():
    """TP1 보호전환이 실제로 stop_updated_at을 남기는가 (배선 확인)."""
    pt = _open(atr=2.0)
    # ⚠ open_position도 stop_updated_at을 찍는다. Windows 시계 해상도(~15ms)상
    #   두 호출이 같은 값을 반환할 수 있어 "이전 값과 다른가"로는 검증이 안 된다.
    #   None으로 지운 뒤 보호전환이 다시 채우는지를 본다.
    pt.stop_updated_at = None
    pt.arm_tp1_single_contract_with_mode(
        current_price=987.84, atr=2.0, mode="atr_profit", atr_lock_mult=0.25,
    )
    check("보호전환 후 stop_updated_at이 갱신된다",
          pt.stop_updated_at is not None)
    check("보호전환이 스톱을 실제로 조였다",
          pt.stop_price < 991.0)


def test_trailing_only_stamps_on_change():
    """update_trailing_stop은 값이 바뀐 때만 시각을 갱신해야 한다.

    매분 무조건 찍으면 stop_updated_at이 항상 '이번 봉'이 되어 봉중 판정이
    영구 무력화된다 — 그러면 이 가드가 기능을 통째로 죽이는 셈이 된다.
    """
    pt = _open(atr=2.0)
    pt.stop_updated_at = None
    # 진입가 근처에서는 트레일이 움직이지 않는다.
    pt.update_trailing_stop(pt.entry_price, 2.0)
    check("스톱 불변이면 stop_updated_at을 찍지 않는다",
          pt.stop_updated_at is None)


def main():
    for fn in (
        test_0803_1349_short_phantom_blocked,
        test_next_bar_is_evaluated_normally,
        test_long_side_symmetry,
        test_untightened_bar_still_hits,
        test_backward_compat_no_bar_start,
        test_tp1_protect_records_timestamp,
        test_trailing_only_stamps_on_change,
    ):
        print("\n--- %s ---" % fn.__name__)
        fn()
    print("\n%s" % ("=" * 60))
    if FAILURES:
        print("FAILED %d: %s" % (len(FAILURES), FAILURES))
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
