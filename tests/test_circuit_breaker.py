import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단 — 아래 주석 참조

import unittest
from unittest.mock import patch

from config.constants import CB_STATE_HALTED, CB_STATE_PAUSED
from safety.circuit_breaker import CircuitBreaker

# [MW0601 422차] 맨 위 2줄은 **프로젝트 import보다 먼저** 와야 한다.
#
# 이 테스트는 실제 CircuitBreaker를 구동하므로 CB의 알림·로그 경로가 그대로
# 실행된다. 2026-08-03 장전에 이 파일이 5회 실행되며 프로덕션 로그에 CRITICAL
# CB 알림 30건(`연속 손절 3회`, `API 지연 6.0초` 등)을 남겼다 — 장중 실제 CB
# 발동은 0건이었는데도. 진짜 CB 발동이 그 노이즈에 묻히는 것이 위험이다.
#
# `MIREUK_TEST_MODE`는 utils/logger.py:setup_logging()(로그 파일 핸들러 생성의
# 유일한 지점)과 utils/notify.py:_send()(Slack 큐)를 무력화한다. CB 상태 전이
# 로직 자체는 그대로 실행되므로 아래 단언은 영향받지 않는다.
# pytest로 돌리면 tests/conftest.py가 같은 일을 하지만, `python tests/
# test_circuit_breaker.py` 직접 실행은 conftest를 로드하지 않아 여기서 막는다.
# 상세: utils/runtime_mode.py


class CircuitBreakerTests(unittest.TestCase):
    def test_halts_after_three_consecutive_stop_losses(self):
        # [260704 감사 P0] CB_CONSEC_STOP_LIMIT는 모의투자 한정 예외로 9999로 완화됨
        # (CLAUDE.md 절대원칙②, config/settings.py:CB_CONSEC_STOP_LIMIT 참조).
        # 이 테스트는 "예외 해제 후 실투 기준(3회)"에서 CB② 메커니즘 자체가 정상
        # 작동하는지 검증하는 것이 목적이므로, 현재 완화된 운영값과 무관하게
        # 모듈 상수를 3으로 패치해 로직만 독립적으로 확인한다.
        with patch("safety.circuit_breaker.CB_CONSEC_STOP_LIMIT", 3):
            cb = CircuitBreaker()

            cb.record_stop_loss()
            cb.record_stop_loss()
            cb.record_stop_loss()

            self.assertEqual(cb.state, CB_STATE_HALTED)

    def test_pauses_on_signal_flips(self):
        cb = CircuitBreaker()

        # alternate signals quickly inside the 1-minute window
        for d in [1, -1, 1, -1, 1, -1]:
            cb.record_signal(d)

        self.assertEqual(cb.state, CB_STATE_PAUSED)

    def test_pauses_on_api_latency_spike(self):
        cb = CircuitBreaker()

        cb.record_api_latency(6.0)

        self.assertEqual(cb.state, CB_STATE_PAUSED)

    def test_warns_on_pipe_latency_over_warn(self):
        cb = CircuitBreaker()

        cb.record_pipe_latency(1500)  # > CB_PIPE_WARN_MS(1000), < CB_PIPE_PAUSE_MS(5000)

        self.assertEqual(cb.state, "NORMAL")  # 경고만, PAUSE 아님

    def test_pauses_on_pipe_latency_over_pause(self):
        cb = CircuitBreaker()

        cb.record_pipe_latency(6000)  # > CB_PIPE_PAUSE_MS(5000)

        self.assertEqual(cb.state, CB_STATE_PAUSED)


if __name__ == "__main__":
    unittest.main()
