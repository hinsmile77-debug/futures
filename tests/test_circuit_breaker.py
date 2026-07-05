import unittest
from unittest.mock import patch

from config.constants import CB_STATE_HALTED, CB_STATE_PAUSED
from safety.circuit_breaker import CircuitBreaker


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
