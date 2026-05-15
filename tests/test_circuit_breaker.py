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


if __name__ == "__main__":
    unittest.main()
