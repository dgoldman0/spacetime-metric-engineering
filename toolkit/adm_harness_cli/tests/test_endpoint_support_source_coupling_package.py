from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from adm_harness.endpoint_support_source_coupling_package import (
    _decision,
    _package_summary,
    _safe_budget_fraction,
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


if __name__ == "__main__":
    unittest.main()
