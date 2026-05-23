from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.beta075_timing_jitter_certificate import (
    _decision,
    _jittered_source_bins,
    _radius_summary,
    write_timing_jitter_outputs,
)


class Beta075TimingJitterCertificateTests(unittest.TestCase):
    def test_jittered_bins_shift_and_clip_common_offset(self):
        active = pd.DataFrame({"s": [-1.0, 0.0, 1.0]})

        forward_late = _jittered_source_bins(active, steps=5, service_direction="forward", offset_steps=2)
        backward_early = _jittered_source_bins(active, steps=5, service_direction="backward", offset_steps=-2)

        np.testing.assert_array_equal(forward_late, np.array([2, 4, 4]))
        np.testing.assert_array_equal(backward_early, np.array([2, 0, 0]))

    def test_radius_summary_marks_worst_offset_and_pass(self):
        offset = pd.DataFrame([
            {
                "jitter_radius_steps": 1,
                "offset_response_pass": True,
                "state_amplification_violation": False,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.4,
                "scenario": "a",
                "offset_steps": -1,
                "worst_source_row_index": 4,
                "worst_assignment": "x",
                "worst_stage": "y",
                "worst_region": "z",
                "worst_s": 0.0,
                "worst_l": 1.0,
                "max_state_sum_to_source_sum": 0.9,
                "max_step_source_fraction": 0.2,
            },
            {
                "jitter_radius_steps": 1,
                "offset_response_pass": True,
                "state_amplification_violation": False,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.6,
                "scenario": "b",
                "offset_steps": 1,
                "worst_source_row_index": 9,
                "worst_assignment": "x",
                "worst_stage": "y",
                "worst_region": "z",
                "worst_s": 2.0,
                "worst_l": 3.0,
                "max_state_sum_to_source_sum": 0.95,
                "max_step_source_fraction": 0.3,
            },
        ])

        summary = _radius_summary(offset).iloc[0]

        self.assertTrue(bool(summary["radius_response_pass"]))
        self.assertEqual(int(summary["worst_offset_steps"]), 1)
        self.assertEqual(int(summary["worst_source_row_index"]), 9)

    def test_decision_reports_partial_radius_limit(self):
        radius = pd.DataFrame([
            {
                "jitter_radius_steps": 1,
                "radius_response_pass": True,
                "max_budget_fraction": 0.8,
                "worst_offset_steps": 0,
                "worst_scenario": "a",
                "worst_source_row_index": 1,
            },
            {
                "jitter_radius_steps": 2,
                "radius_response_pass": False,
                "max_budget_fraction": 1.1,
                "worst_offset_steps": 2,
                "worst_scenario": "b",
                "worst_source_row_index": 2,
            },
        ])
        offset = pd.DataFrame([
            {"state_amplification_violation": False, "limiter_clipped_rows": 0},
            {"state_amplification_violation": False, "limiter_clipped_rows": 0},
        ])
        domain = pd.DataFrame([{"live_support_exclusion_pass": True}])

        decision = _decision(radius, offset, domain).iloc[0]

        self.assertEqual(decision["timing_jitter_status"], "timing_jitter_pass_with_radius_limit")
        self.assertEqual(int(decision["largest_passing_jitter_radius_steps"]), 1)
        self.assertFalse(bool(decision["timing_jitter_pass"]))

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "domain_audit": pd.DataFrame([{"live_support_exclusion_pass": True}]),
            "offset_summary": pd.DataFrame([{"scenario": "offset"}]),
            "radius_summary": pd.DataFrame([{"jitter_radius_steps": 0}]),
            "jitter_bin_summary": pd.DataFrame([{"step": 0}]),
            "source_profile_summary": pd.DataFrame([{"scenario": "source"}]),
            "sampled_worst_rows": pd.DataFrame([{"scenario": "worst"}]),
            "decision": pd.DataFrame([{"timing_jitter_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_timing_jitter_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
