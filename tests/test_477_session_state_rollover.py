# -*- coding: utf-8 -*-
"""[MW0602 477차 F-1] session_state 날짜 롤오버 키 보존 불변식.

무엇을 지키는가
---------------
`SessionRecoveryService.increment_session()`이 날짜 롤오버 시
**당일 종속 키만 리셋하고 나머지 키는 전부 보존**한다.

왜 필요한가 (실제 사고, 2026-08-20 원인 규명)
---------------------------------------------
구 구현은 롤오버 시 dict를 화이트리스트 5키로 **전량 재구성**했다. 이 함수가
만들어진 뒤에 추가된 키들이 화이트리스트에 반영되지 않아, retrain_eod.py가
15:47에 기록한 `p8_last_success_date`·`eod_retrain_ok_date`와 대시보드 누적
카운터 `gbm_last_retrain`·`gbm_total_retrain_count`가 **매 거래일 아침에
삭제**됐다. 그 결과:

  - 08:55 PreRetrain 1차 경로가 매일 죽고 마커파일 폴백으로만 살았다
    (마커파일 단일 장애점).
  - EKS 원인 태깅(main.py:7643)이 `p8_last_success_date`를 항상 빈 값으로
    읽어 스케일러 노후를 `휴장/중단갭`으로 상시 오분류했다.
  - 누적 재학습 카운터가 매 거래일 0으로 리셋됐다(계측 4원칙 ② 위반).

동시에 지키는 반대 방향 불변식: **CB/ProfitGuard 상태는 날짜를 넘어 살아남으면
안 된다.** 전량 보존(dict(data))으로 반전하면서 `circuit_breaker_state`·
`profit_guard_state`가 전일치로 잔존하면, restore_daily_state()의
`date == today` 가드를 통과해 전일 CB 상태가 복원된다(절대원칙 §2 판정 오염).
main.py `_write_session_state()`의 재직렬화가 예외로 실패하는 경우가 실경로다.

이 파일이 깨지면 둘 중 하나다 — 롤오버가 다시 키를 버리기 시작했거나(사고
재발), CB/PG가 날짜를 넘기 시작했거나(더 나쁜 회귀).

실행:
    pytest tests/test_477_session_state_rollover.py
"""
import datetime
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

from strategy.runtime.session_recovery_service import SessionRecoveryService  # noqa: E402

_TODAY = datetime.date.today().isoformat()
_YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


class _FakeSystem(object):
    """increment_session()이 요구하는 최소 표면 — 파일 대신 메모리에 저장."""

    def __init__(self, state):
        self._state = dict(state)
        self._reverse_entry_enabled = False
        self._tp1_protect_mode = "atr_profit"

    def _read_session_state(self):
        return dict(self._state)

    def _write_session_state(self, data):
        self._state = dict(data)


def _yesterday_state():
    """어제 EOD(retrain_eod.py P8)까지 끝난 시점의 실제 파일 모양."""
    return {
        "date": _YESTERDAY,
        "count": 3,
        "reverse_entry_enabled": False,
        "tp1_single_contract_mode": "atr_profit",
        "auto_shutdown_done_date": _YESTERDAY,
        "today_open": 1050.5,
        # 롤오버에서 살아남아야 하는 키들 (사고에서 소실됐던 4종)
        "p8_last_success_date": _YESTERDAY,
        "eod_retrain_ok_date": _YESTERDAY,
        "gbm_last_retrain": _YESTERDAY + " 15:47",
        "gbm_total_retrain_count": 42,
        # 롤오버에서 죽어야 하는 키들
        "profit_guard_state": {"stale": True},
        "circuit_breaker_state": {"stale": True},
    }


def _rollover():
    system = _FakeSystem(_yesterday_state())
    count = SessionRecoveryService().increment_session(system)
    return system._state, count


def test_eod_marker_keys_survive_rollover():
    """불변식 ① — PreRetrain 1차 경로·EKS 태깅의 입력이 살아남는가."""
    state, _ = _rollover()
    assert state.get("p8_last_success_date") == _YESTERDAY, (
        "p8_last_success_date가 롤오버에서 소실 — EKS 원인 태깅(main.py:7643)이 "
        "다시 상시 오분류로 돌아간다"
    )
    assert state.get("eod_retrain_ok_date") == _YESTERDAY, (
        "eod_retrain_ok_date가 롤오버에서 소실 — 08:55 PreRetrain 1차 경로가 "
        "다시 죽고 마커파일 폴백이 단일 장애점이 된다"
    )


def test_gbm_counters_survive_rollover():
    """불변식 ② — 대시보드 누적 재학습 카운터가 살아남는가."""
    state, _ = _rollover()
    assert state.get("gbm_last_retrain") == _YESTERDAY + " 15:47"
    assert state.get("gbm_total_retrain_count") == 42, (
        "gbm_total_retrain_count가 리셋 — '미측정을 0으로 읽지 말 것' "
        "(계측 4원칙 ②) 위반 재발"
    )


def test_daily_keys_are_reset():
    """불변식 ③ — 당일 종속 키는 리셋되는가 (보존 반전의 부작용 방지)."""
    state, count = _rollover()
    assert state.get("date") == _TODAY
    assert count == 1, "롤오버 후 첫 세션 카운트는 1이어야 한다 (0 리셋 + 즉시 +1)"
    assert state.get("count") == 1
    assert state.get("auto_shutdown_done_date") == "", (
        "auto_shutdown_done_date가 전일치로 잔존 — 자동종료 판정 오염"
    )
    assert "today_open" not in state, (
        "today_open(당일 갭 오프셋)이 날짜를 넘었다 — 전일 시가가 잔존"
    )


def test_cb_and_profit_guard_do_not_cross_dates():
    """불변식 ④ — CB/ProfitGuard 상태가 날짜를 넘지 않는가 (회귀 위험 최대 지점).

    _FakeSystem._write_session_state는 main.py와 달리 CB/PG를 재직렬화하지
    않는다 — 재직렬화가 예외로 실패한 날의 경로를 그대로 재현한 것이다.
    그 경로에서도 전일 상태가 남지 않아야 한다.
    """
    state, _ = _rollover()
    assert "circuit_breaker_state" not in state, (
        "전일 circuit_breaker_state가 date=today와 함께 잔존 — "
        "restore_daily_state()의 date==today 가드를 통과해 전일 CB 상태가 "
        "복원된다(절대원칙 §2 판정 오염)"
    )
    assert "profit_guard_state" not in state


def test_same_day_restart_loses_nothing():
    """같은 날 재시작(롤오버 아님)은 종전과 동일 — 키 무손실 + 카운트 증가."""
    same_day = _yesterday_state()
    same_day["date"] = _TODAY
    system = _FakeSystem(same_day)
    count = SessionRecoveryService().increment_session(system)
    state = system._state
    assert count == 4 and state.get("count") == 4
    # 같은 날에는 CB/PG·today_open도 그대로 있어야 한다 (재시작 복원용)
    assert state.get("circuit_breaker_state") == {"stale": True}
    assert state.get("profit_guard_state") == {"stale": True}
    assert state.get("today_open") == 1050.5
    assert state.get("p8_last_success_date") == _YESTERDAY
    assert state.get("gbm_total_retrain_count") == 42
