from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.beta075_service_aligned_schedule import (
    _aligned_temporal_weights,
    _decision,
    write_service_aligned_schedule_outputs,
)


class Beta075ServiceAlignedScheduleTests(unittest.TestCase):
    def test_aligned_weights_are_normalized_per_row(self):
        s_values = np.array([-1.0, 0.0, 1.0], dtype=float)

        weights = _aligned_temporal_weights(s_values, steps=5, width_steps=3, service_direction="forward")

        np.testing.assert_allclose(weights.sum(axis=0), np.ones(3))
        self.assertEqual(int(np.argmax(weights[:, 0])), 0)
        self.assertEqual(int(np.argmax(weights[:, 2])), 4)

    def test_backward_alignment_reverses_service_order(self):
        s_values = np.array([-1.0, 0.0, 1.0], dtype=float)

        weights = _aligned_temporal_weights(s_values, steps=5, width_steps=1, service_direction="backward")

        self.assertEqual(int(np.argmax(weights[:, 0])), 4)
        self.assertEqual(int(np.argmax(weights[:, 2])), 0)

    def test_decision_marks_all_widths_pass(self):
        summary = pd.DataFrame([
            {
                "width_steps": 1,
                "hard_pass": True,
                "max_budget_fraction": 0.7,
                "scenario": "a",
                "worst_source_row_index": 10,
                "max_state_sum_to_source_sum": 0.9,
            },
            {
                "width_steps": 3,
                "hard_pass": True,
                "max_budget_fraction": 0.5,
                "scenario": "a",
                "worst_source_row_index": 11,
                "max_state_sum_to_source_sum": 0.8,
            },
        ])
        domain = pd.DataFrame([{"live_support_exclusion_pass": True}])

        decision = _decision(summary, domain).iloc[0]

        self.assertEqual(decision["service_aligned_schedule_status"], "service_aligned_schedule_pass_all_widths")
        self.assertEqual(int(decision["narrowest_pass_width_steps"]), 1)

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "domain_audit": pd.DataFrame([{"live_support_exclusion_pass": True}]),
            "aligned_summary": pd.DataFrame([{"scenario": "aligned"}]),
            "sampled_worst_rows": pd.DataFrame([{"scenario": "worst"}]),
            "decision": pd.DataFrame([{"service_aligned_schedule_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_service_aligned_schedule_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
