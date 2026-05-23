from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_source_family_energy_constant_audit import (
    EnergyConstantAuditSpec,
    _classification_gates,
    _constant_decomposition,
    _decision,
    _surface_stability,
    write_energy_constant_audit_outputs,
)


def _run_summary() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "label": "sealed_dense_v5",
            "surface_family": "sealed_beta075_v5",
            "role": "reference_dense",
            "energy_status": "watch",
            "hard_energy_pass": True,
            "rows": 10,
            "fail_rows": 0,
            "watch_rows": 10,
            "min_energy_flux_margin": 7.88e-5,
            "max_energy_work_constant": 2.04905,
            "max_support_work_ratio": 0.89893,
            "max_local_exchange_shape": 0.60903,
            "support_total_closure_ratio": 0.54457,
        },
        {
            "label": "lower_service_dense_v2",
            "surface_family": "lower_service_beta075_v2",
            "role": "adjacent_service_surface",
            "energy_status": "watch",
            "hard_energy_pass": True,
            "rows": 10,
            "fail_rows": 0,
            "watch_rows": 10,
            "min_energy_flux_margin": 7.89e-5,
            "max_energy_work_constant": 2.04904,
            "max_support_work_ratio": 0.89892,
            "max_local_exchange_shape": 0.60902,
            "support_total_closure_ratio": 0.54456,
        },
    ])


class Beta075SourceFamilyEnergyConstantAuditTests(unittest.TestCase):
    def test_decomposition_recovers_headroom_and_utilization(self):
        decomposed = _constant_decomposition(_run_summary(), EnergyConstantAuditSpec())
        dense = decomposed.loc[decomposed["label"].eq("sealed_dense_v5")].iloc[0]

        self.assertAlmostEqual(float(dense["work_headroom_to_fail"]), 2.5 - 2.04905)
        self.assertAlmostEqual(float(dense["work_utilization"]), 2.04905 / 2.5)
        self.assertTrue(bool(dense["constant_watch"]))

    def test_adjacent_dense_surface_is_stable_against_reference(self):
        decomposed = _constant_decomposition(_run_summary(), EnergyConstantAuditSpec())
        decomposed["min_energy_flux_margin"] = _run_summary()["min_energy_flux_margin"]
        decomposed["fail_rows"] = _run_summary()["fail_rows"]
        stability = _surface_stability(decomposed)
        adjacent = stability.loc[stability["label"].eq("lower_service_dense_v2")].iloc[0]

        self.assertLess(abs(float(adjacent["work_delta_from_reference"])), 0.03)
        self.assertLessEqual(float(adjacent["energy_flux_relative_drop_from_reference"]), 0.0)

    def test_classification_reads_constant_as_theorem_watch_not_required_buffer(self):
        spec = EnergyConstantAuditSpec()
        run_summary = _run_summary()
        decomposed = _constant_decomposition(run_summary, spec)
        decomposed["min_energy_flux_margin"] = run_summary["min_energy_flux_margin"]
        decomposed["fail_rows"] = run_summary["fail_rows"]
        stability = _surface_stability(decomposed)
        energy_decision = pd.DataFrame([{
            "hard_energy_certificate_pass": True,
            "failed_gate_count": 0,
        }])
        energy_gates = pd.DataFrame([
            {"gate": "lower_order_work_bound", "status": "watch"},
            {"gate": "energy_point_failures", "status": "pass"},
        ])

        gates = _classification_gates(decomposed, stability, energy_decision, energy_gates, spec)
        decision = _decision(gates, decomposed, stability, spec).iloc[0]

        self.assertEqual(
            decision["energy_constant_audit_status"],
            "stable_limiting_theorem_constant_with_buffer_watch",
        )
        self.assertFalse(bool(decision["protective_buffer_required_now"]))
        self.assertTrue(bool(decision["protective_buffer_watch"]))
        self.assertTrue(bool(decision["hard_constant_audit_pass"]))

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "constant_decomposition": pd.DataFrame([{"label": "d"}]),
            "local_constant_decomposition": pd.DataFrame([{"label": "l"}]),
            "surface_stability": pd.DataFrame([{"label": "s"}]),
            "classification_gates": pd.DataFrame([{"gate": "g"}]),
            "decision": pd.DataFrame([{"energy_constant_audit_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_energy_constant_audit_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
