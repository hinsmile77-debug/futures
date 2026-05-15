import unittest

from config.constants import DIRECTION_FLAT
from strategy.entry.meta_gate import MetaGate


class MetaGateTests(unittest.TestCase):
    def test_evaluate_returns_skip_for_flat_signal(self):
        gate = MetaGate()

        result = gate.evaluate(
            direction=DIRECTION_FLAT,
            confidence=0.8,
            regime="NEUTRAL",
            micro_regime="혼합",
            features={},
        )

        self.assertEqual(result["action"], "skip")
        self.assertEqual(result["meta_confidence"], 0.0)
        self.assertEqual(result["size_multiplier"], 0.0)
        self.assertEqual(result["reason"], "flat_signal")

    def test_evaluate_returns_valid_action_for_directional_signal(self):
        gate = MetaGate()

        result = gate.evaluate(
            direction=1,
            confidence=0.72,
            regime="NEUTRAL",
            micro_regime="추세",
            features={
                "mlofi_norm": 0.3,
                "cancel_add_ratio": 0.2,
                "hurst": 0.56,
                "atr_ratio": 1.1,
            },
            recent_accuracy=0.61,
        )

        self.assertIn(result["action"], {"take", "reduce", "skip"})
        self.assertIn("meta_confidence", result)
        self.assertIn("size_multiplier", result)
        self.assertIn("meta_features", result)


if __name__ == "__main__":
    unittest.main()
