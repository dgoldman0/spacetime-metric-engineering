from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_support_source_law_feasibility import (
    SourceLawFeasibilitySpec,
    _decision,
    _scale_jump_summary,
)


class EndpointSupportSourceLawFeasibilityTests(unittest.TestCase):
    def test_decision_keeps_local_severe_cap_as_candidate_with_watches(self):
        spec = SourceLawFeasibilitySpec(severe_scale_watch=0.25, adjacent_scale_jump_watch=0.50)
        audit = pd.DataFrame([
            {
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
                "s": -1.0,
                "source_profile_scale": 1.0,
                "scale_deficit": 0.0,
                "scale_below_one": False,
                "scaled_outside_expected_scope": False,
            },
            {
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
                "s": -0.9,
                "source_profile_scale": 0.1,
                "scale_deficit": 0.9,
                "scale_below_one": True,
                "scaled_outside_expected_scope": False,
            },
        ])
        phase = pd.DataFrame([{"scaled_slices": 1}])
        jumps = _scale_jump_summary(audit, spec)
        margin = pd.DataFrame([{
            "observed_unlimited_pass": True,
            "observed_limiter_clipped_rows": 0,
            "large_unlimited_fails": True,
            "max_observed_unlimited_budget_fraction": 0.4,
            "min_observed_relative_cone_margin": 1.0e-4,
            "min_observed_transport_margin": 1.0e-4,
            "max_large_unlimited_budget_fraction": 1.2,
        }])

        decision = _decision(audit, phase, jumps, margin, spec).iloc[0]

        self.assertEqual(
            decision["source_law_feasibility_status"],
            "phase_local_source_law_candidate_with_watches",
        )
        self.assertTrue(bool(decision["severe_scale_watch"]))
        self.assertTrue(bool(decision["smoothness_watch"]))

    def test_decision_fails_scaled_slice_outside_expected_scope(self):
        spec = SourceLawFeasibilitySpec()
        audit = pd.DataFrame([
            {
                "assignment": "reset_decompression_endpoint_junction",
                "stage": "reset_decompression",
                "region": "core_throat",
                "s": 0.0,
                "source_profile_scale": 0.8,
                "scale_deficit": 0.2,
                "scale_below_one": True,
                "scaled_outside_expected_scope": True,
            }
        ])
        phase = pd.DataFrame([{"scaled_slices": 1}])
        jumps = pd.DataFrame([{"max_adjacent_scale_jump": 0.0}])
        margin = pd.DataFrame([{
            "observed_unlimited_pass": True,
            "observed_limiter_clipped_rows": 0,
            "large_unlimited_fails": False,
            "max_observed_unlimited_budget_fraction": 0.4,
            "min_observed_relative_cone_margin": 1.0e-4,
            "min_observed_transport_margin": 1.0e-4,
            "max_large_unlimited_budget_fraction": 0.7,
        }])

        decision = _decision(audit, phase, jumps, margin, spec).iloc[0]

        self.assertEqual(decision["source_law_feasibility_status"], "source_law_feasibility_fail")
        self.assertEqual(int(decision["scaled_outside_expected_scope_slices"]), 1)


if __name__ == "__main__":
    unittest.main()
