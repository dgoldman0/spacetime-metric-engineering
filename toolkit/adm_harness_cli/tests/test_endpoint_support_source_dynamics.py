from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from adm_harness.endpoint_support_source_dynamics import (
    SupportSourceDynamicsSpec,
    SupportSourceScenario,
    _decision,
    _smooth_profile,
    _source_delta_profile,
    _temporal_envelope,
)


class EndpointSupportSourceDynamicsTests(unittest.TestCase):
    def test_temporal_envelope_integrates_to_one(self):
        weights = _temporal_envelope(40, "raised_cosine")

        self.assertEqual(len(weights), 40)
        self.assertGreater(float(weights.max()), float(weights.min()))
        self.assertAlmostEqual(float(weights.sum()), 1.0)

    def test_smoothing_preserves_integrated_source(self):
        values = np.array([0.0, 2.0, 0.0])

        smoothed = _smooth_profile(values, passes=1)

        self.assertAlmostEqual(float(smoothed.sum()), float(values.sum()))
        self.assertLess(float(smoothed.max()), float(values.max()))

    def test_source_profile_normalizes_at_bottleneck(self):
        frame = pd.DataFrame({
            "source_row_index": [10, 11, 12],
            "s": [1.0, 1.0, 1.0],
            "l": [0.0, 1.0, 2.0],
            "assignment": ["a", "a", "a"],
            "stage": ["stage", "stage", "stage"],
            "region": ["edge", "edge", "edge"],
            "candidate_support_abs_PF_density": [1.0, 2.0, 4.0],
        })
        bottleneck = pd.Series({"source_row_index": 11, "baseline_heat_ratio": 0.5})
        scenario = SupportSourceScenario("observed", 1.0e-4, "outward")

        delta, profile = _source_delta_profile(frame, bottleneck, scenario, SupportSourceDynamicsSpec())

        self.assertAlmostEqual(float(profile.loc[1, "normalized_source_density"]), 1.0)
        self.assertAlmostEqual(float(delta[2] / delta[1]), 2.0)
        self.assertTrue(bool(profile.loc[1, "normalizer_is_bottleneck"]))

    def test_decision_requires_observed_pass_without_limiter_activity(self):
        summary = pd.DataFrame([
            {
                "scenario": "observed_source_outward_unlimited",
                "heat_ratio_delta": 1.0e-4,
                "budget_limiter": False,
                "hard_pass": True,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.25,
            },
            {
                "scenario": "observed_source_outward_budget_limited",
                "heat_ratio_delta": 1.0e-4,
                "budget_limiter": True,
                "hard_pass": True,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.25,
            },
            {
                "scenario": "large_source_outward_unlimited",
                "heat_ratio_delta": 5.0e-4,
                "budget_limiter": False,
                "hard_pass": False,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 1.25,
            },
            {
                "scenario": "large_source_outward_budget_limited",
                "heat_ratio_delta": 5.0e-4,
                "budget_limiter": True,
                "hard_pass": True,
                "limiter_clipped_rows": 1,
                "max_budget_fraction": 0.95,
            },
        ])

        decision = _decision(summary, 1.0e-4).iloc[0]

        self.assertEqual(decision["support_source_dynamics_status"], "coupled_support_source_clean")
        self.assertTrue(bool(decision["observed_limiter_inactive"]))


if __name__ == "__main__":
    unittest.main()
