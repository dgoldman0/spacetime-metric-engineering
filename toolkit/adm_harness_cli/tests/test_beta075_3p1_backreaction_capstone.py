from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_3p1_backreaction_capstone import (
    BackreactionCapstoneSpec,
    BackreactionScenarioSpec,
    _decision,
    _gates,
    _scenario_factor,
    _stability,
    write_backreaction_capstone_outputs,
)


class Beta0753P1BackreactionCapstoneTests(unittest.TestCase):
    def test_scenario_factor_combines_offaxis_and_feedback(self):
        scenario = BackreactionScenarioSpec("s", 2, 0.04, 0.05, 0.1, "read")

        self.assertAlmostEqual(_scenario_factor(scenario, 0.8), 1.08)

    def test_stability_uses_reference_dense_per_scenario(self):
        summary = pd.DataFrame([
            {
                "scenario_id": "axis",
                "label": "sealed_dense_v5",
                "surface_family": "sealed",
                "role": "reference_dense",
                "active_driver_to_endpoint_ratio": 0.45,
                "min_scenario_cone_margin": 0.01,
                "max_scenario_boost_velocity": 0.99,
            },
            {
                "scenario_id": "axis",
                "label": "lower_service_dense_v2",
                "surface_family": "lower",
                "role": "adjacent_service_surface",
                "active_driver_to_endpoint_ratio": 0.451,
                "min_scenario_cone_margin": 0.0101,
                "max_scenario_boost_velocity": 0.9899,
            },
        ])

        stability = _stability(summary)
        adjacent = stability.loc[stability["role"].eq("adjacent_service_surface")].iloc[0]

        self.assertAlmostEqual(float(adjacent["active_driver_ratio_delta_from_reference"]), 0.001)
        self.assertAlmostEqual(float(adjacent["boost_delta_from_reference"]), -0.0001)

    def test_gates_and_decision_watch_pass_for_margin_debt(self):
        summary = pd.DataFrame([
            {
                "label": "sealed_dense_v5",
                "scenario_id": "combined",
                "role": "reference_dense",
                "active_driver_to_endpoint_ratio": 0.50,
                "min_scenario_cone_margin": 0.012,
                "offaxis_angular_driver_fraction": 0.045,
                "live_driver_fraction_of_full_endpoint": 0.003,
                "outside_driver_fraction_of_full_endpoint": 0.001,
                "inherited_outside_support_tail_fraction": 0.0,
                "inherited_live_support_tail_fraction": 0.0,
                "inherited_local_pf_ratio": 0.544,
            },
            {
                "label": "lower_service_dense_v2",
                "scenario_id": "combined",
                "role": "adjacent_service_surface",
                "active_driver_to_endpoint_ratio": 0.501,
                "min_scenario_cone_margin": 0.012,
                "offaxis_angular_driver_fraction": 0.045,
                "live_driver_fraction_of_full_endpoint": 0.003,
                "outside_driver_fraction_of_full_endpoint": 0.001,
                "inherited_outside_support_tail_fraction": 0.0,
                "inherited_live_support_tail_fraction": 0.0,
                "inherited_local_pf_ratio": 0.544,
            },
        ])
        stability = _stability(summary.assign(surface_family="x", max_scenario_boost_velocity=0.988))
        first = pd.DataFrame([{"hard_first_order_3p1_pass": True, "first_order_3p1_status": "first_order_3p1_entry_watch_pass"}])
        energy = pd.DataFrame([{"hard_constant_audit_pass": True, "protective_buffer_watch": True, "work_utilization": 0.82}])

        gates = _gates(summary, stability, first, energy, BackreactionCapstoneSpec())
        decision = _decision(gates, summary).iloc[0]

        self.assertEqual(decision["capstone_status"], "stage2_3p1_backreaction_capstone_watch_pass")
        self.assertEqual(int(decision["failed_gate_count"]), 0)

    def test_output_writer_uses_parquet_for_heavy_tables(self):
        outputs = {
            "scenario_catalog": pd.DataFrame([{"scenario_id": "s"}]),
            "scenario_summary": pd.DataFrame([{"label": "l"}]),
            "surface_stability": pd.DataFrame([{"label": "d"}]),
            "classification_gates": pd.DataFrame([{"gate": "g"}]),
            "point_response": pd.DataFrame([{"label": "p", "value": 1.0}]),
            "top_constraint_drivers": pd.DataFrame([{"label": "t", "value": 2.0}]),
            "decision": pd.DataFrame([{"capstone_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_backreaction_capstone_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertEqual(paths["point_response"].suffix, ".parquet")
            self.assertEqual(paths["top_constraint_drivers"].suffix, ".parquet")
            self.assertNotIn("report", manifest["files"])
            self.assertEqual(len(pd.read_parquet(paths["point_response"])), 1)


if __name__ == "__main__":
    unittest.main()
