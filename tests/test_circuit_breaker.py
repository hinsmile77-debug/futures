import unittest

from config.constants import CB_STATE_HALTED, CB_STATE_PAUSED
from safety.circuit_breaker import CircuitBreaker


class CircuitBreakerTests(unittest.TestCase):
    def test_halts_after_three_consecutive_stop_losses(self):
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
