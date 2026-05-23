from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.beta075_full_system_evolution import (
    FullSystemEvolutionSpec,
    _advect_groups,
    _decision,
    _domain_audit,
    write_full_system_evolution_outputs,
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

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "domain_audit": pd.DataFrame([{"live_support_exclusion_pass": True}]),
            "scenario_summary": pd.DataFrame([{"scenario": "observed", "hard_pass": True}]),
            "source_profile_summary": pd.DataFrame([{"scenario": "observed", "rows": 1}]),
            "sampled_worst_rows": pd.DataFrame([{"scenario": "observed", "max_budget_fraction": 0.1}]),
            "decision": pd.DataFrame([{"full_system_evolution_status": "full_system_evolution_pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_full_system_evolution_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
