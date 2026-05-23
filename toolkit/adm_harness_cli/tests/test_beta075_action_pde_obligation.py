from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_action_pde_obligation import (
    _decision,
    write_action_pde_obligation_outputs,
)


class Beta075ActionPDEObligationTests(unittest.TestCase):
    def test_decision_marks_temporal_regularization_gap(self):
        domain = pd.DataFrame([{"live_support_exclusion_pass": True}])
        scheduled = pd.DataFrame([
            {
                "hard_pass": True,
                "state_amplification_violation": False,
                "max_budget_fraction": 0.2,
            }
        ])
        impulse = pd.DataFrame([
            {
                "impulse_bound_pass": False,
                "state_amplification_violation": False,
                "max_impulse_budget_fraction": 1.2,
                "max_initial_source_budget_fraction": 1.2,
            }
        ])
        edge = pd.DataFrame([
            {
                "expansive_edge_rows": 3,
                "max_normalized_row_sum_bound": 1.1,
            }
        ])

        decision = _decision(domain, scheduled, impulse, edge).iloc[0]

        self.assertEqual(
            decision["action_pde_obligation_status"],
            "action_pde_obligation_gap_temporal_regularization_required",
        )
        self.assertTrue(bool(decision["observed_schedule_pass"]))
        self.assertFalse(bool(decision["impulse_bound_pass"]))

    def test_decision_fails_observed_schedule_failure(self):
        domain = pd.DataFrame([{"live_support_exclusion_pass": True}])
        scheduled = pd.DataFrame([
            {
                "hard_pass": False,
                "state_amplification_violation": False,
                "max_budget_fraction": 1.2,
            }
        ])
        impulse = pd.DataFrame([
            {
                "impulse_bound_pass": False,
                "state_amplification_violation": False,
                "max_impulse_budget_fraction": 1.2,
                "max_initial_source_budget_fraction": 1.2,
            }
        ])
        edge = pd.DataFrame([
            {
                "expansive_edge_rows": 0,
                "max_normalized_row_sum_bound": 0.9,
            }
        ])

        decision = _decision(domain, scheduled, impulse, edge).iloc[0]

        self.assertEqual(decision["action_pde_obligation_status"], "action_pde_obligation_fail_observed_schedule")

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "domain_audit": pd.DataFrame([{"live_support_exclusion_pass": True}]),
            "scheduled_summary": pd.DataFrame([{"scenario": "scheduled"}]),
            "impulse_summary": pd.DataFrame([{"scenario": "impulse"}]),
            "transport_edge_summary": pd.DataFrame([{"edge_rows": 1}]),
            "transport_edge_rows": pd.DataFrame([{"axis": "radial"}]),
            "source_profile_summary": pd.DataFrame([{"scenario": "source"}]),
            "sampled_worst_rows": pd.DataFrame([{"scenario": "worst"}]),
            "decision": pd.DataFrame([{"action_pde_obligation_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_action_pde_obligation_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
