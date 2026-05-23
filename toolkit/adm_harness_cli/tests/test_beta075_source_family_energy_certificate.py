from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_source_family_energy_certificate import (
    SourceFamilyEnergySpec,
    _decision,
    _energy_gates,
    _energy_point_table,
    _principal_matrix_from_symbol_row,
    _theorem_assumptions,
    write_source_family_energy_outputs,
)


def _point_symbol() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "label": "sealed_dense_v5",
            "surface_family": "sealed_beta075_v5",
            "role": "reference_dense",
            "assignment": "a",
            "stage": "reset_decompression",
            "region": "core_throat",
            "medium_source_active": True,
            "covariant_divergence_live": False,
            "hard_formal_symbol_pass": True,
            "relative_cone_margin": 7.0e-5,
            "max_abs_relative_characteristic_speed": 0.99993,
            "operator_exchange_residual_load": 0.2,
            "operator_support_stiffness_density": 0.4,
            "operator_support_inertia_density": 0.3,
            "operator_local_P_error": 0.61,
            "operator_local_F_error": 0.47,
            "transport_margin": 7.0e-5,
            "transport_rapidity_abs": 5.0,
            "heat_lambda_minus": -0.2,
            "heat_lambda_plus": 0.3,
            "angular_lambda_minus": -0.1,
            "angular_lambda_plus": 0.2,
            "support_lambda_minus": -0.4,
            "support_lambda_plus": 0.4,
            "director_lambda": 0.1,
        }
    ])


class Beta075SourceFamilyEnergyCertificateTests(unittest.TestCase):
    def test_theorem_assumptions_include_scope_and_scheduled_source(self):
        assumptions = _theorem_assumptions()

        self.assertIn("fixed_background_service_metric", set(assumptions["assumption"]))
        self.assertIn("scheduled_source_response", set(assumptions["assumption"]))
        self.assertIn("available_surface_scope", set(assumptions["assumption"]))

    def test_principal_matrix_is_symmetric_for_formal_blocks(self):
        matrix = _principal_matrix_from_symbol_row(_point_symbol().iloc[0])

        self.assertEqual(matrix.shape, (7, 7))
        self.assertAlmostEqual(float(abs(matrix - matrix.T).max()), 0.0)

    def test_energy_point_table_promotes_watch_without_hard_failure(self):
        run_summary = pd.DataFrame([{
            "label": "sealed_dense_v5",
            "support_total_local_pf_ratio": 0.544,
        }])

        energy = _energy_point_table(_point_symbol(), run_summary, SourceFamilyEnergySpec()).iloc[0]

        self.assertEqual(energy["energy_status"], "watch")
        self.assertTrue(bool(energy["hard_energy_pass"]))
        self.assertGreater(energy["energy_work_constant"], 1.0)

    def test_energy_gates_report_expected_watches(self):
        run_summary = pd.DataFrame([{
            "label": "sealed_dense_v5",
            "energy_status": "watch",
            "hard_energy_pass": True,
            "fail_rows": 0,
            "min_energy_flux_margin": 7.0e-5,
            "max_energy_work_constant": 1.42,
            "max_local_exchange_shape": 0.61,
            "support_total_closure_ratio": 0.544,
            "max_principal_symmetry_defect": 0.0,
            "max_symmetrizer_condition": 1.0,
        }])
        cross = pd.DataFrame([{
            "hard_cross_surface_pass": True,
            "cross_surface_robustness_status": "cross_surface_source_family_robustness_watch_pass",
            "surface_count": 3,
        }])
        equation = pd.DataFrame([{
            "min_source_profile_scale": 0.0926,
        }])

        gates = _energy_gates(run_summary, cross, equation, SourceFamilyEnergySpec())

        self.assertEqual(gates.loc[gates["gate"].eq("energy_flux_inside_cone"), "status"].iloc[0], "watch")
        self.assertEqual(gates.loc[gates["gate"].eq("lower_order_work_bound"), "status"].iloc[0], "watch")
        self.assertEqual(gates.loc[gates["gate"].eq("scheduled_source_bound"), "status"].iloc[0], "watch")
        self.assertEqual(gates.loc[gates["gate"].eq("principal_symmetry"), "status"].iloc[0], "pass")

    def test_decision_watch_pass_when_no_failures(self):
        gates = pd.DataFrame([
            {"gate": "a", "status": "pass"},
            {"gate": "b", "status": "watch"},
        ])
        run_summary = pd.DataFrame([{
            "label": "sealed_dense_v5",
            "min_energy_flux_margin": 7.0e-5,
            "max_energy_work_constant": 1.42,
            "max_support_work_ratio": 0.3,
            "max_local_exchange_shape": 0.61,
            "support_total_closure_ratio": 0.544,
        }])

        decision = _decision(gates, run_summary).iloc[0]

        self.assertEqual(decision["energy_certificate_status"], "fixed_background_energy_estimate_watch_pass")
        self.assertTrue(bool(decision["hard_energy_certificate_pass"]))
        self.assertEqual(decision["failed_gate_count"], 0)

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "theorem_assumptions": pd.DataFrame([{"assumption": "a"}]),
            "energy_point": pd.DataFrame([{"label": "p"}]),
            "energy_run_summary": pd.DataFrame([{"label": "r"}]),
            "energy_local_summary": pd.DataFrame([{"label": "l"}]),
            "energy_gates": pd.DataFrame([{"gate": "g"}]),
            "decision": pd.DataFrame([{"energy_certificate_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_source_family_energy_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
