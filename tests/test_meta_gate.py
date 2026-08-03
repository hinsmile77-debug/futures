import os
import sys

# [423차] 422차 conftest와 동등한 2줄 중 sys.path 쪽이 빠져 있었다 — pytest 없이
# `python tests/test_meta_gate.py`로 직접 실행하면 `config` import가 깨진다.
# MW0602에는 pytest가 없어 이 줄이 없으면 아예 돌릴 수 없다.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단 (utils/runtime_mode.py)

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
