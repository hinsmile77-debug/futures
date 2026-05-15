import unittest

from config.settings import HORIZONS
from model.ensemble_decision import EnsembleDecision


class EnsembleDecisionTests(unittest.TestCase):
    def _base_horizon_proba(self, up: float, down: float, flat: float):
        data = {}
        for h in HORIZONS.keys():
            direction = 1 if up >= down and up >= flat else (-1 if down >= up and down >= flat else 0)
            confidence = max(up, down, flat)
            data[h] = {
                "up": up,
                "down": down,
                "flat": flat,
                "direction": direction,
                "confidence": confidence,
            }
        return data

    def test_compute_returns_up_direction_and_grade_a(self):
        decision = EnsembleDecision()
        horizon_proba = self._base_horizon_proba(up=0.82, down=0.10, flat=0.08)

        result = decision.compute(horizon_proba, regime="NEUTRAL", adaptive_gating=False)

        self.assertEqual(result["direction"], 1)
        self.assertEqual(result["grade"], "A")
        self.assertTrue(result["regime_ok"])
        self.assertGreaterEqual(result["confidence"], 0.70)

    def test_compute_returns_x_when_confidence_below_regime_threshold(self):
        decision = EnsembleDecision()
        horizon_proba = self._base_horizon_proba(up=0.51, down=0.39, flat=0.10)

        result = decision.compute(horizon_proba, regime="NEUTRAL", adaptive_gating=False)

        self.assertEqual(result["grade"], "X")
        self.assertFalse(result["regime_ok"])

    def test_compute_returns_flat_when_flat_score_is_highest(self):
        decision = EnsembleDecision()
        horizon_proba = self._base_horizon_proba(up=0.20, down=0.20, flat=0.60)

        result = decision.compute(horizon_proba, regime="RISK_ON", adaptive_gating=False)

        self.assertEqual(result["direction"], 0)
        self.assertEqual(result["grade"], "X")


if __name__ == "__main__":
    unittest.main()
