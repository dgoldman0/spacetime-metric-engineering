from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_source_family_cross_surface_robustness import (
    CrossSurfaceRobustnessSpec,
    _cross_surface_gates,
    _decision,
    _surface_delta,
    write_cross_surface_robustness_outputs,
)


def _run_summary() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "label": "sealed_dense_v5",
            "surface_family": "sealed_beta075_v5",
            "role": "reference_dense",
            "hard_formal_symbol_pass": True,
            "fail_rows": 0,
            "min_relative_cone_margin": 7.8e-5,
            "max_local_P_error": 0.61,
            "max_local_F_error": 0.47,
            "support_total_local_pf_ratio": 0.544,
            "support_total_local_pf_gate": 0.55,
        },
        {
            "label": "lower_service_dense_v2",
            "surface_family": "lower_service_beta075_v2",
            "role": "adjacent_service_surface",
            "hard_formal_symbol_pass": True,
            "fail_rows": 0,
            "min_relative_cone_margin": 8.0e-5,
            "max_local_P_error": 0.612,
            "max_local_F_error": 0.475,
            "support_total_local_pf_ratio": 0.545,
            "support_total_local_pf_gate": 0.55,
        },
    ])


class Beta075SourceFamilyCrossSurfaceRobustnessTests(unittest.TestCase):
    def test_surface_delta_compares_to_reference_dense(self):
        delta = _surface_delta(_run_summary())
        v2 = delta.loc[delta["label"].eq("lower_service_dense_v2")].iloc[0]

        self.assertEqual(v2["reference_label"], "sealed_dense_v5")
        self.assertAlmostEqual(v2["max_local_P_error_delta_from_reference"], 0.002)
        self.assertAlmostEqual(v2["support_total_local_pf_delta_from_reference"], 0.001)

    def test_gates_watch_not_fail_for_margin_debt(self):
        summary = _run_summary()
        delta = _surface_delta(summary)
        gates = _cross_surface_gates(summary, delta, CrossSurfaceRobustnessSpec())

        self.assertEqual(gates.loc[gates["gate"].eq("all_surfaces_hard_symbol"), "status"].iloc[0], "pass")
        self.assertEqual(gates.loc[gates["gate"].eq("cross_surface_cone_margin"), "status"].iloc[0], "watch")
        self.assertEqual(gates.loc[gates["gate"].eq("cross_surface_local_exchange_shape"), "status"].iloc[0], "watch")
        self.assertEqual(gates.loc[gates["gate"].eq("cross_surface_total_support_closure"), "status"].iloc[0], "watch")
        self.assertEqual(gates.loc[gates["gate"].eq("cross_surface_drift"), "status"].iloc[0], "pass")

    def test_decision_promotes_watch_pass_without_failures(self):
        summary = _run_summary()
        delta = _surface_delta(summary)
        gates = _cross_surface_gates(summary, delta, CrossSurfaceRobustnessSpec())
        decision = _decision(gates, summary).iloc[0]

        self.assertEqual(
            decision["cross_surface_robustness_status"],
            "cross_surface_source_family_robustness_watch_pass",
        )
        self.assertTrue(bool(decision["hard_cross_surface_pass"]))
        self.assertEqual(decision["failed_gate_count"], 0)

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "surface_inputs": pd.DataFrame([{"label": "a"}]),
            "operator_terms": pd.DataFrame([{"operator_id": "O"}]),
            "run_summary": pd.DataFrame([{"label": "r"}]),
            "local_summary": pd.DataFrame([{"label": "l"}]),
            "point_symbol": pd.DataFrame([{"label": "p"}]),
            "surface_delta": pd.DataFrame([{"label": "d"}]),
            "cross_surface_gates": pd.DataFrame([{"gate": "g"}]),
            "claim_boundary": pd.DataFrame([{"claim": "c"}]),
            "decision": pd.DataFrame([{"cross_surface_robustness_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_cross_surface_robustness_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
