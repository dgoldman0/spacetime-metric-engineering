from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from adm_harness.endpoint_support_source_coupling_package import (
    PackageCouplingSpec,
    _decision,
    _package_summary,
    _safe_budget_fraction,
    _source_profile_budget_scale,
)


class EndpointSupportSourceCouplingPackageTests(unittest.TestCase):
    def test_safe_budget_fraction_handles_infinite_budget(self):
        delta = np.array([0.2, 0.5, 0.0, 1.0])
        budget = np.array([1.0, np.inf, 0.0, 0.0])

        fraction = _safe_budget_fraction(delta, budget)

        self.assertAlmostEqual(float(fraction[0]), 0.2)
        self.assertAlmostEqual(float(fraction[1]), 0.0)
        self.assertAlmostEqual(float(fraction[2]), 0.0)
        self.assertTrue(np.isinf(fraction[3]))

    def test_package_summary_rolls_up_slices(self):
        slices = pd.DataFrame([
            {
                "scenario": "observed",
                "heat_ratio_delta": 1.0e-4,
                "direction": "outward",
                "budget_limiter": False,
                "hard_pass": True,
                "rows": 4,
                "fail_rows_any_time": 0,
                "over_budget_rows_any_time": 0,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.2,
                "min_relative_cone_margin_sample": 0.1,
                "min_transport_margin": 0.2,
            },
            {
                "scenario": "observed",
                "heat_ratio_delta": 1.0e-4,
                "direction": "outward",
                "budget_limiter": False,
                "hard_pass": True,
                "rows": 6,
                "fail_rows_any_time": 0,
                "over_budget_rows_any_time": 0,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.5,
                "min_relative_cone_margin_sample": 0.03,
                "min_transport_margin": 0.1,
            },
        ])

        summary = _package_summary(slices).iloc[0]

        self.assertEqual(summary["status"], "pass")
        self.assertEqual(int(summary["slices"]), 2)
        self.assertEqual(int(summary["rows"]), 10)
        self.assertAlmostEqual(float(summary["max_budget_fraction"]), 0.5)

    def test_decision_marks_clean_observed_package_verdict(self):
        package = pd.DataFrame([
            {
                "scenario": "observed_source_outward_unlimited",
                "heat_ratio_delta": 1.0e-4,
                "budget_limiter": False,
                "hard_pass": True,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.2,
            },
            {
                "scenario": "observed_source_outward_budget_limited",
                "heat_ratio_delta": 1.0e-4,
                "budget_limiter": True,
                "hard_pass": True,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.2,
            },
            {
                "scenario": "large_source_outward_unlimited",
                "heat_ratio_delta": 5.0e-4,
                "budget_limiter": False,
                "hard_pass": False,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 1.2,
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

        decision = _decision(package, 1.0e-4).iloc[0]

        self.assertEqual(decision["package_source_coupling_status"], "package_support_source_observed_clean")
        self.assertTrue(bool(decision["large_unlimited_fails"]))

    def test_source_profile_budget_scale_caps_targeted_entry_catch_profile(self):
        group = pd.DataFrame([
            {
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
            },
            {
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
            },
        ])
        budget = pd.DataFrame([
            {"max_admissible_delta_psi": 1.0},
            {"max_admissible_delta_psi": 1.0},
        ])
        normalized = np.array([1.0, 4.0])
        bottleneck = pd.Series({"baseline_heat_ratio": 0.0})
        spec = PackageCouplingSpec(
            observed_heat_ratio_delta=0.5,
            source_profile_budget_cap_scope="support_edge_entry_catch",
            source_profile_budget_cap_fraction=0.5,
        )

        scale, meta = _source_profile_budget_scale(group, budget, normalized, bottleneck, spec)

        self.assertTrue(meta["source_profile_budget_cap_applied"])
        self.assertLess(scale, 1.0)
        self.assertAlmostEqual(
            meta["source_profile_raw_reference_budget_fraction"] * scale,
            0.5,
        )

    def test_source_profile_budget_scale_ignores_untargeted_stage(self):
        group = pd.DataFrame([
            {
                "assignment": "support_edge_endpoint_junction",
                "stage": "release_shift_fade",
                "region": "support_edge",
            },
        ])
        budget = pd.DataFrame([{"max_admissible_delta_psi": 1.0}])
        spec = PackageCouplingSpec(
            observed_heat_ratio_delta=0.5,
            source_profile_budget_cap_scope="support_edge_entry_catch",
            source_profile_budget_cap_fraction=0.5,
        )

        scale, meta = _source_profile_budget_scale(
            group,
            budget,
            np.array([10.0]),
            pd.Series({"baseline_heat_ratio": 0.0}),
            spec,
        )

        self.assertEqual(scale, 1.0)
        self.assertFalse(meta["source_profile_budget_cap_applied"])


if __name__ == "__main__":
    unittest.main()
