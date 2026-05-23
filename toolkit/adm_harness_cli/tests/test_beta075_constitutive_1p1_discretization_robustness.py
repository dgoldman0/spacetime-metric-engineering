from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_constitutive_1p1_discretization_robustness import (
    DiscretizationRobustnessSpec,
    DiscretizationVariant,
    _proof_spec_for_variant,
    _robustness_decision,
    default_discretization_variants,
    write_discretization_robustness_outputs,
)


class Beta075Constitutive1p1DiscretizationRobustnessTests(unittest.TestCase):
    def test_default_variants_include_refinement_tail_and_cfl_roles(self):
        roles = {variant.role for variant in default_discretization_variants()}

        self.assertIn("baseline", roles)
        self.assertIn("service_step_refinement", roles)
        self.assertIn("tail_window_sensitivity", roles)
        self.assertIn("cfl_sensitivity", roles)

    def test_proof_spec_for_variant_carries_resolution_and_source_settings(self):
        base = DiscretizationRobustnessSpec(source_profile_budget_cap_fraction=0.91, max_workers=5)
        variant = DiscretizationVariant("v", 72, 96, 12, 0.3, 0.15, "test")

        proof = _proof_spec_for_variant(base, variant)

        self.assertEqual(proof.steps, 72)
        self.assertEqual(proof.tail_steps, 96)
        self.assertEqual(proof.jitter_radius_steps, 12)
        self.assertAlmostEqual(proof.source_profile_budget_cap_fraction, 0.91)
        self.assertEqual(proof.max_workers, 5)

    def test_robustness_decision_passes_smooth_variation(self):
        summary = pd.DataFrame([
            {
                "variant": "baseline",
                "role": "baseline",
                "proof_obligations_pass": True,
                "max_budget_fraction": 0.7,
                "max_state_sum_to_source_sum": 0.9,
                "negative_source_rows": 0,
                "scaled_outside_expected_scope_slices": 0,
                "worst_source_row_index": 1,
                "worst_offset_steps": 0,
                "min_source_profile_scale": 0.25,
            },
            {
                "variant": "refined",
                "role": "service_step_refinement",
                "proof_obligations_pass": True,
                "max_budget_fraction": 0.72,
                "max_state_sum_to_source_sum": 0.91,
                "negative_source_rows": 0,
                "scaled_outside_expected_scope_slices": 0,
                "worst_source_row_index": 1,
                "worst_offset_steps": 0,
                "min_source_profile_scale": 0.25,
            },
        ])

        decision = _robustness_decision(summary, DiscretizationRobustnessSpec()).iloc[0]

        self.assertEqual(
            decision["discretization_robustness_status"],
            "discretization_robustness_pass_with_smooth_variation",
        )
        self.assertTrue(bool(decision["robustness_pass"]))

    def test_robustness_decision_marks_drift_watch(self):
        summary = pd.DataFrame([
            {
                "variant": "baseline",
                "role": "baseline",
                "proof_obligations_pass": True,
                "max_budget_fraction": 0.5,
                "max_state_sum_to_source_sum": 0.9,
                "negative_source_rows": 0,
                "scaled_outside_expected_scope_slices": 0,
                "worst_source_row_index": 1,
                "worst_offset_steps": 0,
                "min_source_profile_scale": 0.25,
            },
            {
                "variant": "refined",
                "role": "service_step_refinement",
                "proof_obligations_pass": True,
                "max_budget_fraction": 0.8,
                "max_state_sum_to_source_sum": 0.91,
                "negative_source_rows": 0,
                "scaled_outside_expected_scope_slices": 0,
                "worst_source_row_index": 2,
                "worst_offset_steps": 1,
                "min_source_profile_scale": 0.25,
            },
        ])

        decision = _robustness_decision(summary, DiscretizationRobustnessSpec()).iloc[0]

        self.assertEqual(
            decision["discretization_robustness_status"],
            "discretization_robustness_pass_with_drift_watch",
        )
        self.assertTrue(bool(decision["drift_watch"]))

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "variant_summary": pd.DataFrame([{"variant": "baseline"}]),
            "scenario_summary": pd.DataFrame([{"scenario": "s"}]),
            "radius_summary": pd.DataFrame([{"timing_radius_steps": 0}]),
            "transport_semigroup": pd.DataFrame([{"axis": "radial"}]),
            "source_law_summary": pd.DataFrame([{"scaled_slices": 1}]),
            "obligation_summary": pd.DataFrame([{"obligation": "o"}]),
            "sampled_worst_rows": pd.DataFrame([{"scenario": "worst"}]),
            "decision": pd.DataFrame([{"discretization_robustness_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_discretization_robustness_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
