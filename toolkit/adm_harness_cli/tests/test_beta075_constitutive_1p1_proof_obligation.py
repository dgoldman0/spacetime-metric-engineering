from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_constitutive_1p1_proof_obligation import (
    Constitutive1p1ProofSpec,
    _decision,
    _obligation_rows,
    _transport_semigroup_certificate,
    default_proof_scenarios,
    write_constitutive_1p1_proof_outputs,
)


class Beta075Constitutive1p1ProofObligationTests(unittest.TestCase):
    def test_default_proof_scenarios_cover_common_jitter_offsets(self):
        scenarios = default_proof_scenarios(Constitutive1p1ProofSpec(jitter_radius_steps=2))

        self.assertEqual(len(scenarios), 15)
        self.assertEqual(min(s.timing_offset_steps for s in scenarios), -2)
        self.assertEqual(max(s.timing_offset_steps for s in scenarios), 2)
        self.assertTrue(all(not s.budget_limiter for s in scenarios))

    def test_transport_semigroup_certificate_fails_bad_cfl(self):
        scenarios = default_proof_scenarios(Constitutive1p1ProofSpec(jitter_radius_steps=0))
        cert = _transport_semigroup_certificate(
            radial_group_count=3,
            service_group_count=4,
            spec=Constitutive1p1ProofSpec(radial_cfl=1.2, service_cfl=0.2, jitter_radius_steps=0),
            scenarios=scenarios,
        )

        self.assertFalse(bool(cert["positive_coefficients_pass"].all()))
        self.assertTrue(bool(cert.loc[cert["axis"].eq("service"), "positive_coefficients_pass"].all()))

    def test_obligation_rows_pass_clean_observed_class(self):
        scenario = pd.DataFrame([
            {
                "hard_pass": True,
                "state_amplification_violation": False,
                "negative_source_rows": 0,
                "max_budget_fraction": 0.7,
                "max_state_sum_to_source_sum": 0.9,
            }
        ])
        radius = pd.DataFrame([
            {
                "timing_radius_steps": 0,
                "radius_pass": True,
                "max_budget_fraction": 0.7,
            }
        ])
        transport = pd.DataFrame([
            {
                "cfl": 0.4,
                "positive_coefficients_pass": True,
                "maps_nonnegative_state_to_nonnegative_state": True,
                "l1_nonincrease_for_nonnegative_state": True,
            }
        ])
        domain = pd.DataFrame([
            {
                "live_support_exclusion_pass": True,
                "active_live_rows": 0,
                "active_packet_live_rows": 0,
            }
        ])
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

        obligations = _obligation_rows(
            scenario,
            radius,
            transport,
            domain,
            source,
            Constitutive1p1ProofSpec(limiter_safety_fraction=0.95),
        )

        self.assertTrue(bool(obligations["pass"].all()))

    def test_decision_reports_failed_obligations(self):
        obligations = pd.DataFrame([
            {"obligation": "a", "pass": True},
            {"obligation": "b", "pass": False},
        ])
        scenarios = pd.DataFrame([
            {
                "scenario": "s",
                "timing_offset_steps": 0,
                "worst_source_row_index": 12,
                "max_budget_fraction": 1.1,
                "max_state_sum_to_source_sum": 0.9,
            }
        ])
        radius = pd.DataFrame([{"timing_radius_steps": 0}])

        decision = _decision(obligations, scenarios, radius).iloc[0]

        self.assertEqual(
            decision["constitutive_1p1_proof_status"],
            "constitutive_1p1_observed_class_proof_obligation_fail",
        )
        self.assertEqual(int(decision["failed_obligation_count"]), 1)

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "domain_audit": pd.DataFrame([{"live_support_exclusion_pass": True}]),
            "scenario_summary": pd.DataFrame([{"scenario": "s"}]),
            "radius_summary": pd.DataFrame([{"timing_radius_steps": 0}]),
            "transport_semigroup": pd.DataFrame([{"axis": "radial"}]),
            "source_profile_summary": pd.DataFrame([{"scenario": "source"}]),
            "source_bin_summary": pd.DataFrame([{"step": 0}]),
            "source_law_summary": pd.DataFrame([{"scaled_slices": 1}]),
            "obligation_summary": pd.DataFrame([{"obligation": "o"}]),
            "sampled_worst_rows": pd.DataFrame([{"scenario": "worst"}]),
            "decision": pd.DataFrame([{"constitutive_1p1_proof_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_constitutive_1p1_proof_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
