from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_source_family_equations import (
    SourceFamilyEquationInputs,
    SourceFamilyEquationSpec,
    _decision,
    _exchange_channel_audit,
    _source_family_equations,
    build_source_family_equation_package,
    write_source_family_equation_outputs,
)


def _stroke_decision() -> pd.DataFrame:
    return pd.DataFrame([{
        "passes_support_stroke_exchange_fit": True,
        "best_normalized_active_abs_PF_l1_error": 0.44,
        "active_pf_l1_gate": 0.50,
        "decision_read": "phase-aware support exchange closes",
    }])


def _total_closure() -> pd.DataFrame:
    return pd.DataFrame([{
        "passes_support_total_closure": True,
        "local_max_closure_residual_to_target_abs_PF_ratio": 0.52,
        "local_closure_pf_gate": 0.55,
        "active_closure_residual_to_target_abs_PF_ratio": 0.44,
        "active_closure_pf_gate": 0.50,
        "angular_support_pass": True,
        "full_total_closure_residual_angular_volume": 0.0,
        "angular_support_gate": 1.0e-14,
        "localization_pass": True,
        "outside_support_tail_fraction": 1.0e-5,
        "support_tail_fraction_gate": 1.0e-3,
        "live_support_tail_fraction": 0.0,
        "live_support_fraction_gate": 1.0e-4,
        "decision_read": "support tensor restores total conservation",
    }])


class Beta075SourceFamilyEquationsTests(unittest.TestCase):
    def test_equations_cover_required_blocks_and_claim_boundary(self):
        equations = _source_family_equations()
        blocks = set(equations["equation_block"])

        for block in SourceFamilyEquationSpec().required_blocks:
            self.assertIn(block, blocks)
        self.assertIn("open_endpoint_balance", set(equations["equation_name"]))
        self.assertIn("fixed_background_effective_action_skeleton", set(equations["equation_name"]))
        action = equations.loc[equations["equation_name"].eq("fixed_background_effective_action_skeleton")].iloc[0]
        self.assertIn("not a final closed matter theorem", action["role"])

    def test_exchange_channel_audit_keeps_tight_channel_as_watch(self):
        component_summary = pd.DataFrame([
            {"component": "P", "active_normalized_l1_error": 0.48, "group_key": "held|support", "fit_scope": "phase_region"},
            {"component": "F", "active_normalized_l1_error": 0.31, "group_key": "entry|support", "fit_scope": "phase_region"},
        ])

        audit = _exchange_channel_audit(
            component_summary=component_summary,
            stroke_exchange=_stroke_decision(),
            total_closure=_total_closure(),
            spec=SourceFamilyEquationSpec(),
        )

        self.assertEqual(audit.loc[audit["channel"].eq("power_P"), "status"].iloc[0], "watch")
        self.assertEqual(audit.loc[audit["channel"].eq("radial_force_F"), "status"].iloc[0], "pass")
        self.assertEqual(audit.loc[audit["channel"].eq("angular_exchange_absence"), "status"].iloc[0], "pass")

    def test_decision_promotes_candidate_with_watches(self):
        constraints = pd.DataFrame([
            {"gate": "source_law_definition", "status": "watch", "value": "candidate"},
            {"gate": "reduced_principal_symbol", "status": "watch", "value": 7.0e-5},
            {"gate": "phase_local_source_response", "status": "watch", "value": 0.09},
            {"gate": "support_total_conservation", "status": "pass", "value": 0.50},
        ])
        exchange = pd.DataFrame([
            {"channel": "power_P", "status": "watch", "value": 0.48},
            {"channel": "radial_force_F", "status": "pass", "value": 0.31},
        ])

        decision = _decision(
            equations=_source_family_equations(),
            constraint_audit=constraints,
            exchange_audit=exchange,
            spec=SourceFamilyEquationSpec(),
        ).iloc[0]

        self.assertTrue(bool(decision["hard_equation_package_pass"]))
        self.assertEqual(
            decision["formal_equation_status"],
            "formal_source_family_equations_candidate_with_hyperbolicity_and_exchange_watches",
        )

    def test_build_package_from_minimal_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_law = root / "source_law"
            principal = root / "principal"
            field = root / "field"
            stroke = root / "stroke"
            total = root / "total"
            robust = root / "robust"
            for path in (source_law, principal, field, stroke, total, robust):
                path.mkdir()

            pd.DataFrame([{
                "source_law_definition_status": "source_law_definition_candidate_with_hyperbolicity_watches",
                "watch_count": 4,
            }]).to_csv(source_law / "beta075_source_law_definition_decision.csv", index=False)
            pd.DataFrame([
                {"evidence": "covariant_tensor_identity", "status": "pass", "primary_value": 1.0e-16, "watch": False, "read": "identity"},
                {"evidence": "phase_local_source_law", "status": "phase_local_source_law_candidate_with_watches", "primary_value": 0.09, "watch": True, "read": "sharp"},
            ]).to_csv(source_law / "beta075_source_law_evidence_summary.csv", index=False)
            pd.DataFrame([
                {"family": "single_scalar", "status": "ruled_out_as_primary", "compatibility_value": 0.4, "reason": "too small"},
                {"family": "regulated_anisotropic_heat_current_medium", "status": "core_endpoint_medium", "compatibility_value": 1.0, "reason": "lead"},
            ]).to_csv(source_law / "beta075_source_law_family_compatibility.csv", index=False)
            pd.DataFrame([{
                "principal_symbol_status": "watch",
                "dense_tightest_relative_cone_margin": 7.0e-5,
                "decision_read": "thin margin",
            }]).to_csv(principal / "endpoint_support_principal_symbol_decision.csv", index=False)
            pd.DataFrame([{
                "label": "dense_24x14",
                "kind": "reference_24x14",
                "symbol_status": "watch",
                "min_relative_cone_margin": 7.0e-5,
            }]).to_csv(principal / "endpoint_support_principal_symbol_run_summary.csv", index=False)
            pd.DataFrame([{
                "passes_constrained_field_closure": True,
                "worst_normalized_l1_error": 0.01,
                "decision_read": "field closure",
            }]).to_csv(field / "endpoint_medium_field_closure_decision.csv", index=False)
            _stroke_decision().to_csv(stroke / "endpoint_support_stroke_exchange_decision.csv", index=False)
            pd.DataFrame([
                {"component": "P", "active_normalized_l1_error": 0.48, "group_key": "held|support", "fit_scope": "phase_region"},
                {"component": "F", "active_normalized_l1_error": 0.31, "group_key": "entry|support", "fit_scope": "phase_region"},
            ]).to_csv(stroke / "endpoint_support_stroke_exchange_selected_component_summary.csv", index=False)
            _total_closure().to_csv(total / "endpoint_support_total_closure_decision.csv", index=False)
            pd.DataFrame([{
                "discretization_robustness_status": "discretization_robustness_pass_with_smooth_variation",
                "drift_watch": False,
                "max_budget_fraction": 0.89,
            }]).to_csv(robust / "beta075_constitutive_1p1_discretization_decision.csv", index=False)

            outputs, _metadata = build_source_family_equation_package(
                SourceFamilyEquationInputs(source_law, principal, field, stroke, total, robust)
            )

            self.assertEqual(
                outputs["decision"]["formal_equation_status"].iloc[0],
                "formal_source_family_equations_candidate_with_hyperbolicity_and_exchange_watches",
            )
            self.assertEqual(outputs["exchange_channel_audit"].loc[0, "status"], "watch")

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "equations": pd.DataFrame([{"equation_id": "E"}]),
            "constraint_audit": pd.DataFrame([{"gate": "g"}]),
            "exchange_channel_audit": pd.DataFrame([{"channel": "c"}]),
            "inherited_gate_summary": pd.DataFrame([{"item": "i"}]),
            "claim_boundary": pd.DataFrame([{"claim": "c"}]),
            "decision": pd.DataFrame([{"formal_equation_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_source_family_equation_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
