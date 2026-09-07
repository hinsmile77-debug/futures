# -*- coding: utf-8 -*-
"""[MW0601 538차] 날짜 전환 계측(G-1 + F-1 보강) 회귀 고정.

2026-09-07 장후 리포트 이상점 1-4가 지적한 것은 코드 버그가 아니라 **판정 근거의
정합성**이었다 — 532차가 F-1의 확인 수단으로 사전등록한 `[SessionStateDrop]` 로그가
3거래일 연속 안 나왔는데도 재현 횟수만으로 "확정"이 선언됐다.

그래서 이 세션이 넣은 것은 원인 수정이 아니라 **전환 순간을 직접 재는 계측**이다.
이 파일이 고정하는 불변식은 두 축이다:

  ① 계측이 실제로 나온다 — 전환 시 `[SessionRollover]`, 마커가 버려지면 `[SessionStateDrop]`
  ② **라이브 반영 0** — 계측을 넣기 전과 쓰는 값이 한 글자도 다르지 않다
     (버려지던 키는 지금도 그대로 버려진다. F-1 본체는 사용자 승인 대기다)
"""
from __future__ import annotations

import datetime
import io
import logging
import os
import re

import pytest

from strategy.runtime.session_recovery_service import SessionRecoveryService

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(
    REPO_ROOT, "strategy", "runtime", "session_recovery_service.py"
)

TODAY = datetime.date.today().isoformat()
YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


class _FakeSystem(object):
    """increment_session이 만지는 최소 표면만 흉내낸다."""

    def __init__(self, state):
        self._state = dict(state)
        self.written = None
        self._reverse_entry_enabled = False
        self._tp1_protect_mode = "atr_profit"

    def _read_session_state(self):
        return dict(self._state)

    def _write_session_state(self, data):
        self.written = dict(data)


class _Capture(logging.Handler):
    """`SYSTEM` 로거는 log_manager가 propagate=False로 잡아 caplog에 안 잡힌다 —
    루트를 거치지 않고 그 로거에 직접 핸들러를 단다."""

    def __init__(self):
        logging.Handler.__init__(self, level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture
def caplog_system():
    lg = logging.getLogger("SYSTEM")
    handler = _Capture()
    prev_level, prev_disabled = lg.level, lg.disabled
    lg.addHandler(handler)
    lg.setLevel(logging.DEBUG)
    lg.disabled = False
    try:
        yield handler
    finally:
        lg.removeHandler(handler)
        lg.setLevel(prev_level)
        lg.disabled = prev_disabled


def _rollover_state():
    """전날 EOD가 완료 마커까지 써 둔 상태."""
    return {
        "date": YESTERDAY,
        "count": 3,
        "reverse_entry_enabled": True,
        "tp1_single_contract_mode": "atr_profit",
        "auto_shutdown_done_date": YESTERDAY,
        "p8_last_success_date": YESTERDAY,
        "eod_retrain_ok_date": YESTERDAY,
    }


# ── ① 계측이 나온다 ──────────────────────────────────────────────────────────

def test_rollover_logs_carried_and_dropped_keys(caplog_system):
    svc = SessionRecoveryService()
    system = _FakeSystem(_rollover_state())

    svc.increment_session(system)

    lines = [r.getMessage() for r in caplog_system.records]
    roll = [m for m in lines if "[SessionRollover]" in m]
    assert len(roll) == 1, lines
    msg = roll[0]
    # 이어받은 축과 버려진 축을 **양쪽 다** 남긴다(계측 4원칙 ⑤)
    assert "이어받은 키" in msg and "새로 초기화된 키" in msg
    assert YESTERDAY in msg and TODAY in msg
    assert "p8_last_success_date" in msg
    assert "eod_retrain_ok_date" in msg


def test_marker_loss_emits_sessionstatedrop_warning(caplog_system):
    svc = SessionRecoveryService()
    system = _FakeSystem(_rollover_state())

    svc.increment_session(system)

    drops = [
        r for r in caplog_system.records if "[SessionStateDrop]" in r.getMessage()
    ]
    assert len(drops) == 1
    assert drops[0].levelno == logging.WARNING
    msg = drops[0].getMessage()
    assert "p8_last_success_date" in msg and "eod_retrain_ok_date" in msg
    # 호출부가 특정돼야 "여기서 지워진다"가 로그만으로 갈린다
    assert "session_recovery_service.py:increment_session" in msg


def test_no_marker_no_drop_warning(caplog_system):
    """마커가 애초에 없었으면 소실 경고를 내지 않는다 — 미측정≠0의 반대편."""
    state = _rollover_state()
    state.pop("p8_last_success_date")
    state.pop("eod_retrain_ok_date")
    svc = SessionRecoveryService()

    svc.increment_session(_FakeSystem(state))

    assert not [
        r for r in caplog_system.records if "[SessionStateDrop]" in r.getMessage()
    ]
    assert [r for r in caplog_system.records if "[SessionRollover]" in r.getMessage()]


def test_same_day_does_not_log_rollover(caplog_system):
    """같은 날 재기동은 전환이 아니다 — 로그가 나오면 오탐이다."""
    state = _rollover_state()
    state["date"] = TODAY
    svc = SessionRecoveryService()

    svc.increment_session(_FakeSystem(state))

    assert not [
        r for r in caplog_system.records if "[SessionRollover]" in r.getMessage()
    ]


def test_instrumentation_never_raises(caplog_system):
    """계측이 깨져도 기동을 막지 않는다."""
    svc = SessionRecoveryService()

    class _Exploding(dict):
        def keys(self):
            raise RuntimeError("boom")

    # prev.keys()가 터져도 increment_session은 정상 반환해야 한다
    svc._log_session_rollover(_Exploding({"date": YESTERDAY}), {"date": TODAY})


# ── ② 라이브 반영 0 — 쓰는 값이 계측 도입 전과 동일하다 ──────────────────────

def test_written_state_is_unchanged_by_instrumentation():
    """F-1 본체는 미적용이다 — 마커는 지금도 그대로 버려져야 한다."""
    svc = SessionRecoveryService()
    system = _FakeSystem(_rollover_state())

    count = svc.increment_session(system)

    assert count == 1  # 날짜 전환이면 count는 0에서 다시 센다
    assert system.written == {
        "date": TODAY,
        "count": 1,
        "reverse_entry_enabled": False,   # system._reverse_entry_enabled 반영
        "tp1_single_contract_mode": "atr_profit",
        "auto_shutdown_done_date": "",
    }
    # 🔴 이 두 줄이 깨지면 F-1이 승인 없이 배포된 것이다
    assert "p8_last_success_date" not in system.written
    assert "eod_retrain_ok_date" not in system.written


def test_same_day_write_is_unchanged():
    state = _rollover_state()
    state["date"] = TODAY
    svc = SessionRecoveryService()
    system = _FakeSystem(state)

    count = svc.increment_session(system)

    assert count == 4
    # 같은 날 경로는 원본 dict를 이어 쓰므로 마커가 살아 있어야 한다
    assert system.written["p8_last_success_date"] == YESTERDAY
    assert system.written["eod_retrain_ok_date"] == YESTERDAY


# ── ③ 소스 규약 ──────────────────────────────────────────────────────────────

def test_marker_keys_match_main_py():
    """마커 키 정의가 main.py와 갈리면 계측이 조용히 빗나간다."""
    main_src = io.open(
        os.path.join(REPO_ROOT, "main.py"), encoding="utf-8"
    ).read()
    m = re.search(
        r"_SESSION_STATE_MARKER_KEYS\s*=\s*\(([^)]*)\)", main_src
    )
    assert m, "main.py에서 _SESSION_STATE_MARKER_KEYS를 찾지 못했다"
    main_keys = tuple(
        k.strip().strip("\"'") for k in m.group(1).split(",") if k.strip()
    )
    assert SessionRecoveryService._MARKER_KEYS == main_keys


def test_rollover_logger_does_not_use_log_manager():
    """log_manager로 WARNING을 내면 exceptions_10m에 합산돼 헬스 degraded 자체 유발(F-17)."""
    src = io.open(SRC_PATH, encoding="utf-8").read()
    start = src.index("def _log_session_rollover")
    tail = src[start + 1:]
    end = start + 1 + tail.index("\n    def ") if "\n    def " in tail else len(src)
    body = src[start:end]
    # 주석·독스트링의 언급이 아니라 **실제 호출**만 잡는다
    assert not re.search(r"log_manager\s*\.\s*\w+\s*\(", body)
