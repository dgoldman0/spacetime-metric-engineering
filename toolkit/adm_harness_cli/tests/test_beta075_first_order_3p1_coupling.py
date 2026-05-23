from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_first_order_3p1_coupling import (
    FirstOrder3P1Spec,
    _coupling_gates,
    _decision,
    _driver_summary,
    _surface_stability,
    write_first_order_3p1_coupling_outputs,
)


def _point_closure() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "medium_source_active": True,
            "covariant_divergence_live": False,
            "covariant_exchange_allowed_mask": True,
            "volume_weight": 2.0,
            "source_abs_density": 5.0,
            "endpoint_exchange_l2_density_volume": 10.0,
            "total_closure_residual_l2_density_volume": 4.0,
            "total_closure_residual_l2_density": 2.0,
            "total_closure_residual_0": 0.30,
            "total_closure_residual_1": 0.40,
            "total_closure_residual_2": 0.0,
            "total_closure_residual_3": 0.0,
        },
        {
            "medium_source_active": False,
            "covariant_divergence_live": True,
            "covariant_exchange_allowed_mask": False,
            "volume_weight": 1.0,
            "source_abs_density": 0.0,
            "endpoint_exchange_l2_density_volume": 1.0,
            "total_closure_residual_l2_density_volume": 0.1,
            "total_closure_residual_l2_density": 0.1,
            "total_closure_residual_0": 0.10,
            "total_closure_residual_1": 0.0,
            "total_closure_residual_2": 0.0,
            "total_closure_residual_3": 0.0,
        },
    ])


def _surface_summary() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "label": "sealed_dense_v5",
            "surface_family": "sealed_beta075_v5",
            "role": "reference_dense",
            "covariant_identity_pass": True,
            "projection_reconstruction_pass": True,
            "boost_subluminal_pass": True,
            "mixed_eigen_real_pass": True,
            "max_abs_boost_velocity": 0.987,
            "support_total_closure_pass": True,
            "active_closure_residual_to_endpoint_l2_ratio": 0.451,
            "active_closure_l2_gate": 0.55,
            "local_max_closure_residual_to_target_abs_PF_ratio": 0.544,
            "local_closure_pf_gate": 0.55,
            "outside_residual_fraction_of_full_endpoint": 0.001,
            "outside_residual_fraction_gate": 0.006,
            "live_residual_fraction_of_full_endpoint": 0.003,
            "live_residual_fraction_gate": 0.005,
            "outside_support_tail_fraction": 0.00001,
            "support_tail_fraction_gate": 0.001,
            "live_support_tail_fraction": 0.0,
            "live_support_fraction_gate": 0.0001,
            "full_total_closure_residual_angular_volume": 0.0,
            "angular_support_gate": 1.0e-14,
            "active_bianchi_driver_to_endpoint_ratio": 0.451,
        },
        {
            "label": "lower_service_dense_v2",
            "surface_family": "lower_service_beta075_v2",
            "role": "adjacent_service_surface",
            "covariant_identity_pass": True,
            "projection_reconstruction_pass": True,
            "boost_subluminal_pass": True,
            "mixed_eigen_real_pass": True,
            "max_abs_boost_velocity": 0.9871,
            "support_total_closure_pass": True,
            "active_closure_residual_to_endpoint_l2_ratio": 0.452,
            "active_closure_l2_gate": 0.55,
            "local_max_closure_residual_to_target_abs_PF_ratio": 0.5441,
            "local_closure_pf_gate": 0.55,
            "outside_residual_fraction_of_full_endpoint": 0.001,
            "outside_residual_fraction_gate": 0.006,
            "live_residual_fraction_of_full_endpoint": 0.003,
            "live_residual_fraction_gate": 0.005,
            "outside_support_tail_fraction": 0.00001,
            "support_tail_fraction_gate": 0.001,
            "live_support_tail_fraction": 0.0,
            "live_support_fraction_gate": 0.0001,
            "full_total_closure_residual_angular_volume": 0.0,
            "angular_support_gate": 1.0e-14,
            "active_bianchi_driver_to_endpoint_ratio": 0.452,
        },
    ])


class Beta075FirstOrder3P1CouplingTests(unittest.TestCase):
    def test_driver_summary_projects_bianchi_residual_components(self):
        driver = _driver_summary("toy", _point_closure())

        self.assertAlmostEqual(driver["active_bianchi_driver_to_endpoint_ratio"], 0.4)
        self.assertAlmostEqual(driver["active_bianchi_driver_to_source_abs_ratio"], 0.4)
        self.assertGreater(driver["hamiltonian_constraint_driver_proxy"], 0.0)
        self.assertEqual(driver["live_rows"], 1)

    def test_surface_stability_uses_dense_reference(self):
        stability = _surface_stability(_surface_summary())
        adjacent = stability.loc[stability["label"].eq("lower_service_dense_v2")].iloc[0]

        self.assertAlmostEqual(float(adjacent["active_driver_ratio_delta_from_reference"]), 0.001)
        self.assertLess(abs(float(adjacent["boost_delta_from_reference"])), 0.01)

    def test_coupling_gates_watch_on_margin_without_failure(self):
        surfaces = _surface_summary()
        stability = _surface_stability(surfaces)
        equation_decision = pd.DataFrame([{
            "hard_equation_package_pass": True,
            "formal_equation_status": "formal_source_family_equations_candidate_with_hyperbolicity_and_exchange_watches",
        }])
        energy_decision = pd.DataFrame([{
            "hard_constant_audit_pass": True,
            "protective_buffer_watch": True,
            "protective_buffer_required_now": False,
            "work_utilization": 0.82,
        }])

        gates = _coupling_gates(surfaces, stability, equation_decision, energy_decision, FirstOrder3P1Spec())
        decision = _decision(gates, surfaces).iloc[0]

        self.assertEqual(decision["first_order_3p1_status"], "first_order_3p1_entry_watch_pass")
        self.assertEqual(int(decision["failed_gate_count"]), 0)
        self.assertGreaterEqual(int(decision["watch_count"]), 1)

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "run_manifest": pd.DataFrame([{"label": "r"}]),
            "surface_summary": pd.DataFrame([{"label": "s"}]),
            "surface_stability": pd.DataFrame([{"label": "d"}]),
            "classification_gates": pd.DataFrame([{"gate": "g"}]),
            "top_constraint_drivers": pd.DataFrame([{"label": "t"}]),
            "decision": pd.DataFrame([{"first_order_3p1_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_first_order_3p1_coupling_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
