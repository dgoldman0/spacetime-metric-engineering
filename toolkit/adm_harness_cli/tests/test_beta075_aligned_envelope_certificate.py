from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.beta075_aligned_envelope_certificate import (
    _basis_source_bins,
    _decision,
    write_aligned_envelope_outputs,
)


class Beta075AlignedEnvelopeCertificateTests(unittest.TestCase):
    def test_basis_bins_follow_service_direction(self):
        active = pd.DataFrame({"s": [-1.0, 0.0, 1.0]})

        forward = _basis_source_bins(active, steps=5, service_direction="forward")
        backward = _basis_source_bins(active, steps=5, service_direction="backward")

        np.testing.assert_array_equal(forward, np.array([0, 2, 4]))
        np.testing.assert_array_equal(backward, np.array([4, 2, 0]))

    def test_decision_passes_when_all_convex_kernel_bounds_pass(self):
        basis = pd.DataFrame([
            {
                "convex_kernel_bound_pass": True,
                "state_amplification_violation": False,
                "convex_kernel_bound_budget_fraction": 0.7,
                "scenario": "a",
                "worst_source_row_index": 12,
                "max_state_sum_to_source_sum": 0.9,
            }
        ])
        domain = pd.DataFrame([{"live_support_exclusion_pass": True}])

        decision = _decision(basis, domain).iloc[0]

        self.assertEqual(decision["aligned_envelope_status"], "aligned_envelope_pass_convex_kernel_bound")
        self.assertTrue(bool(decision["convex_kernel_bound_pass"]))

    def test_decision_fails_when_bound_fails(self):
        basis = pd.DataFrame([
            {
                "convex_kernel_bound_pass": False,
                "state_amplification_violation": False,
                "convex_kernel_bound_budget_fraction": 1.1,
                "scenario": "a",
                "worst_source_row_index": 12,
                "max_state_sum_to_source_sum": 0.9,
            }
        ])
        domain = pd.DataFrame([{"live_support_exclusion_pass": True}])

        decision = _decision(basis, domain).iloc[0]

        self.assertEqual(decision["aligned_envelope_status"], "aligned_envelope_fail_convex_kernel_bound")
        self.assertFalse(bool(decision["convex_kernel_bound_pass"]))

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "domain_audit": pd.DataFrame([{"live_support_exclusion_pass": True}]),
            "basis_summary": pd.DataFrame([{"scenario": "basis"}]),
            "service_bin_summary": pd.DataFrame([{"step": 0}]),
            "sampled_worst_rows": pd.DataFrame([{"scenario": "worst"}]),
            "decision": pd.DataFrame([{"aligned_envelope_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_aligned_envelope_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
