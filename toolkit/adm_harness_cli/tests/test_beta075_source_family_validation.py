from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_source_family_validation import (
    SourceFamilyValidationSpec,
    _attach_operator_fields,
    _component_error_map,
    _decision,
    _operator_terms,
    _validation_gates,
    write_source_family_validation_outputs,
)


class Beta075SourceFamilyValidationTests(unittest.TestCase):
    def test_operator_terms_specify_derivative_support_reservoir(self):
        terms = _operator_terms()

        self.assertIn("support_stress", set(terms["operator_block"]))
        stress = terms.loc[terms["operator_block"].eq("support_stress"), "operator"].iloc[0]
        self.assertIn("partial_l", stress)
        self.assertIn("lower_order(P,F)", stress)

    def test_component_error_map_attaches_local_p_and_f_errors(self):
        component = pd.DataFrame([
            {"group_key": "reset_decompression|core_throat", "component": "P", "active_normalized_l1_error": 0.61},
            {"group_key": "reset_decompression|support_edge", "component": "F", "active_normalized_l1_error": 0.47},
        ])
        point = pd.DataFrame([
            {
                "stage": "reset_decompression",
                "region": "core_throat",
                "fit_error_abs_PF_density": 0.2,
                "target_abs_PF_density": 2.0,
                "fit_abs_PF_density": 1.8,
                "source_abs_density": 0.1,
                "enthalpy_buffer_density": 0.05,
            },
            {
                "stage": "held_carry",
                "region": "support_edge",
                "fit_error_abs_PF_density": 0.0,
                "target_abs_PF_density": 1.0,
                "fit_abs_PF_density": 1.0,
                "source_abs_density": 0.1,
                "enthalpy_buffer_density": 0.05,
            },
        ])

        mapping = _component_error_map(component)
        attached = _attach_operator_fields(point, component)

        self.assertEqual(mapping[("reset_decompression", "core_throat")]["P"], 0.61)
        self.assertAlmostEqual(attached.loc[0, "operator_local_P_error"], 0.61)
        self.assertAlmostEqual(attached.loc[0, "operator_exchange_residual_load"], 1.42)
        self.assertAlmostEqual(attached.loc[1, "operator_local_P_error"], 0.0)

    def test_validation_gates_keep_margin_and_exchange_as_watches(self):
        run_summary = pd.DataFrame([
            {
                "mesh": "dense",
                "formal_symbol_status": "watch",
                "min_relative_cone_margin": 7.0e-5,
                "max_local_P_error": 0.61,
                "max_local_F_error": 0.47,
                "support_total_closure_watch": True,
                "support_total_local_pf_ratio": 0.544,
                "support_total_local_pf_gate": 0.55,
                "fail_rows": 0,
            }
        ])
        equation_decision = pd.DataFrame([{
            "hard_equation_package_pass": True,
            "formal_equation_status": "formal_source_family_equations_candidate_with_hyperbolicity_and_exchange_watches",
            "decision_read": "equations close",
        }])
        inherited = pd.DataFrame([{
            "principal_symbol_status": "watch",
            "dense_tightest_relative_cone_margin": 7.0e-5,
        }])

        gates = _validation_gates(run_summary, equation_decision, inherited, SourceFamilyValidationSpec())

        self.assertEqual(gates.loc[gates["gate"].eq("derived_principal_symbol"), "status"].iloc[0], "watch")
        self.assertEqual(gates.loc[gates["gate"].eq("support_operator_local_exchange"), "status"].iloc[0], "watch")
        self.assertEqual(gates.loc[gates["gate"].eq("live_support_exclusion"), "status"].iloc[0], "pass")

    def test_decision_watch_pass_not_bigger_issue_without_failures(self):
        gates = pd.DataFrame([
            {"gate": "a", "status": "pass"},
            {"gate": "b", "status": "watch"},
        ])
        run_summary = pd.DataFrame([
            {
                "mesh": "dense",
                "min_relative_cone_margin": 7.0e-5,
                "p01_relative_cone_margin": 0.01,
                "max_local_P_error": 0.61,
                "max_local_F_error": 0.47,
                "support_total_local_pf_ratio": 0.544,
                "max_operator_support_sound": 0.4,
            }
        ])

        decision = _decision(gates, run_summary, SourceFamilyValidationSpec()).iloc[0]

        self.assertEqual(decision["source_family_validation_status"], "source_family_validation_watch_pass")
        self.assertTrue(bool(decision["hard_validation_pass"]))
        self.assertFalse(bool(decision["bigger_issue_flag"]))
        self.assertFalse(bool(decision["safety_margin_resolved"]))

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "operator_terms": pd.DataFrame([{"operator_id": "O"}]),
            "run_summary": pd.DataFrame([{"label": "r"}]),
            "local_summary": pd.DataFrame([{"label": "l"}]),
            "point_symbol": pd.DataFrame([{"label": "p"}]),
            "validation_gates": pd.DataFrame([{"gate": "g"}]),
            "claim_boundary": pd.DataFrame([{"claim": "c"}]),
            "decision": pd.DataFrame([{"source_family_validation_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_source_family_validation_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
