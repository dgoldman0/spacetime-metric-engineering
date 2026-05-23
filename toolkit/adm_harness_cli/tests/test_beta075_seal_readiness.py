from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.beta075_seal_readiness import classify_bounded_seal_status


class Beta075SealReadinessTests(unittest.TestCase):
    def test_watch_without_blocker_is_bounded_ready(self):
        matrix = pd.DataFrame([
            {"status": "pass", "hard_required": True, "blocks_bounded_seal": False},
            {"status": "watch", "hard_required": True, "blocks_bounded_seal": False},
            {"status": "watch", "hard_required": False, "blocks_bounded_seal": False},
        ])

        decision = classify_bounded_seal_status(matrix).iloc[0]

        self.assertEqual(decision["beta075_seal_readiness_status"], "bounded_seal_ready_with_watches")
        self.assertTrue(bool(decision["bounded_seal_ready"]))
        self.assertEqual(int(decision["hard_blocker_count"]), 0)
        self.assertEqual(int(decision["watch_count"]), 2)

    def test_required_failure_blocks_bounded_seal(self):
        matrix = pd.DataFrame([
            {"status": "fail", "hard_required": True, "blocks_bounded_seal": True},
            {"status": "watch", "hard_required": False, "blocks_bounded_seal": False},
        ])

        decision = classify_bounded_seal_status(matrix).iloc[0]

        self.assertEqual(decision["beta075_seal_readiness_status"], "not_ready")
        self.assertFalse(bool(decision["bounded_seal_ready"]))
        self.assertEqual(int(decision["hard_blocker_count"]), 1)


if __name__ == "__main__":
    unittest.main()
