from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from adm_harness.beta075_full_system_evolution import (
    FullSystemEvolutionSpec,
    _advect_groups,
    _decision,
    _domain_audit,
)


class Beta075FullSystemEvolutionTests(unittest.TestCase):
    def test_group_advection_does_not_create_state(self):
        state = np.array([0.0, 1.0, 0.0, 2.0], dtype=float)
        groups = [np.array([0, 1, 2]), np.array([3])]

        evolved = _advect_groups(state, groups, cfl=0.5, direction="outward")

        self.assertLessEqual(float(evolved.sum()), float(state.sum()))
        self.assertGreaterEqual(float(evolved.min()), 0.0)

    def test_domain_audit_rejects_live_evolved_rows(self):
        point = pd.DataFrame({"x": [1, 2]})
        active = pd.DataFrame({
            "covariant_divergence_live": [False, True],
            "inside_packet_live": [False, False],
            "assignment": ["a", "a"],
            "region": ["support_edge", "support_edge"],
        })

        audit = _domain_audit(point, active).iloc[0]

        self.assertFalse(bool(audit["live_support_exclusion_pass"]))
        self.assertEqual(int(audit["active_live_rows"]), 1)

    def test_decision_marks_observed_clean_with_large_watch_as_pass_with_watches(self):
        summary = pd.DataFrame([
            {
                "heat_ratio_delta": 1.0e-4,
                "budget_limiter": False,
                "hard_pass": True,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.4,
                "max_state_sum_to_source_sum": 0.9,
                "state_amplification_violation": False,
            },
            {
                "heat_ratio_delta": 1.0e-4,
                "budget_limiter": True,
                "hard_pass": True,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 0.4,
                "max_state_sum_to_source_sum": 0.9,
                "state_amplification_violation": False,
            },
            {
                "heat_ratio_delta": 5.0e-4,
                "budget_limiter": False,
                "hard_pass": False,
                "limiter_clipped_rows": 0,
                "max_budget_fraction": 1.2,
                "max_state_sum_to_source_sum": 0.9,
                "state_amplification_violation": False,
            },
            {
                "heat_ratio_delta": 5.0e-4,
                "budget_limiter": True,
                "hard_pass": True,
                "limiter_clipped_rows": 2,
                "max_budget_fraction": 0.95,
                "max_state_sum_to_source_sum": 0.9,
                "state_amplification_violation": False,
            },
        ])
        audit = pd.DataFrame([{"live_support_exclusion_pass": True}])

        decision = _decision(summary, audit, FullSystemEvolutionSpec().observed_heat_ratio_delta).iloc[0]

        self.assertEqual(decision["full_system_evolution_status"], "full_system_evolution_pass_with_watches")
        self.assertTrue(bool(decision["observed_unlimited_pass"]))
        self.assertTrue(bool(decision["large_unlimited_fails"]))


if __name__ == "__main__":
    unittest.main()
