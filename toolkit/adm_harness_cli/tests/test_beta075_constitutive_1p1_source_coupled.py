from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_constitutive_1p1_source_coupled import (
    _decision,
    _source_law_gate,
    _source_law_summary,
    write_constitutive_1p1_outputs,
)


class Beta075Constitutive1p1SourceCoupledTests(unittest.TestCase):
    def test_source_law_summary_deduplicates_observed_driver_slices(self):
        rows = []
        for scenario in ["a", "b"]:
            rows.append({
                "scenario": scenario,
                "gate_role": "observed_driver",
                "heat_ratio_delta": 1.0e-4,
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
                "slice_s_key": -1.0,
                "rows": 14,
                "source_profile_scale": 0.5,
                "source_profile_budget_cap_applied": True,
                "source_profile_raw_reference_budget_fraction": 2.0,
                "bottleneck_budget_delta_psi": 1.5,
            })

        summary = _source_law_summary(pd.DataFrame(rows), observed_delta=1.0e-4).iloc[0]

        self.assertEqual(int(summary["slices"]), 1)
        self.assertEqual(int(summary["scaled_slices"]), 1)
        self.assertAlmostEqual(float(summary["min_source_profile_scale"]), 0.5)

    def test_source_law_gate_accepts_phase_local_bounded_scales(self):
        summary = pd.DataFrame([
            {
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
                "scaled_slices": 1,
                "min_source_profile_scale": 0.25,
                "max_source_profile_scale": 1.0,
            }
        ])

        gate = _source_law_gate(summary)

        self.assertTrue(gate["source_law_bounded"])
        self.assertTrue(gate["source_law_phase_local"])
        self.assertEqual(gate["scaled_slices"], 1)

    def test_decision_passes_observed_driver_with_limiter_inactive(self):
        scenario = pd.DataFrame([
            {
                "scenario": "observed",
                "heat_ratio_delta": 1.0e-4,
                "budget_limiter": False,
                "hard_pass": True,
                "limiter_clipped_rows": 0,
                "state_amplification_violation": False,
                "max_budget_fraction": 0.7,
                "max_state_sum_to_source_sum": 0.9,
            },
            {
                "scenario": "observed_limited",
                "heat_ratio_delta": 1.0e-4,
                "budget_limiter": True,
                "hard_pass": True,
                "limiter_clipped_rows": 0,
                "state_amplification_violation": False,
                "max_budget_fraction": 0.7,
                "max_state_sum_to_source_sum": 0.9,
            },
            {
                "scenario": "large",
                "heat_ratio_delta": 5.0e-4,
                "budget_limiter": False,
                "hard_pass": False,
                "limiter_clipped_rows": 0,
                "state_amplification_violation": False,
                "max_budget_fraction": 1.2,
                "max_state_sum_to_source_sum": 0.9,
            },
        ])
        domain = pd.DataFrame([{"live_support_exclusion_pass": True}])
        source = pd.DataFrame([
            {
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
                "scaled_slices": 1,
                "min_source_profile_scale": 0.25,
                "max_source_profile_scale": 1.0,
            }
        ])

        decision = _decision(scenario, domain, source, observed_delta=1.0e-4).iloc[0]

        self.assertEqual(
            decision["constitutive_1p1_status"],
            "constitutive_1p1_observed_clean_with_margin_watches",
        )
        self.assertTrue(bool(decision["observed_unlimited_pass"]))
        self.assertFalse(bool(decision["large_unlimited_pass"]))

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "domain_audit": pd.DataFrame([{"live_support_exclusion_pass": True}]),
            "scenario_summary": pd.DataFrame([{"scenario": "observed"}]),
            "source_profile_summary": pd.DataFrame([{"scenario": "source"}]),
            "source_bin_summary": pd.DataFrame([{"step": 0}]),
            "source_law_summary": pd.DataFrame([{"scaled_slices": 1}]),
            "sampled_worst_rows": pd.DataFrame([{"scenario": "worst"}]),
            "decision": pd.DataFrame([{"constitutive_1p1_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_constitutive_1p1_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
