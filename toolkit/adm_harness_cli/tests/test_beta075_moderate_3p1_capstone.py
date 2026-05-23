from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_moderate_3p1_capstone import (
    Moderate3P1Inputs,
    Moderate3P1ScenarioSpec,
    Moderate3P1Spec,
    Moderate3P1SurfaceSpec,
    _angular_weights,
    default_moderate_v5_surfaces,
    run_moderate_3p1_v5_capstone,
)
from adm_harness.source_ledger import sha256_file, write_manifest


def _write_fake_surface(root: Path, label: str, service_rating: float) -> Moderate3P1SurfaceSpec:
    total = root / label / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5"
    cov = root / label / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5"
    total.mkdir(parents=True)
    cov.mkdir(parents=True)

    point = pd.DataFrame([
        {
            "case": "a",
            "s": -0.5,
            "l": 1.8,
            "stage": "entry_precatch",
            "region": "support_edge",
            "assignment": "support",
            "volume_weight": 1.0,
            "medium_source_active": True,
            "covariant_divergence_live": False,
            "covariant_exchange_allowed_mask": True,
            "endpoint_exchange_l2_density_volume": 10.0,
            "total_closure_residual_l2_density_volume": 1.0,
            "total_closure_residual_l2_density": 1.0,
            "total_closure_residual_0": 0.1,
            "total_closure_residual_1": 0.2,
            "total_closure_residual_2": 0.0,
            "total_closure_residual_3": 0.0,
            "source_abs_volume": 12.0,
            "source_abs_density": 12.0,
            "medium_frame_abs_boost_velocity": 0.95,
        },
        {
            "case": "a",
            "s": 0.5,
            "l": 1.9,
            "stage": "release_shift_fade",
            "region": "support_edge",
            "assignment": "support",
            "volume_weight": 1.0,
            "medium_source_active": True,
            "covariant_divergence_live": False,
            "covariant_exchange_allowed_mask": True,
            "endpoint_exchange_l2_density_volume": 8.0,
            "total_closure_residual_l2_density_volume": 0.5,
            "total_closure_residual_l2_density": 0.5,
            "total_closure_residual_0": 0.1,
            "total_closure_residual_1": 0.1,
            "total_closure_residual_2": 0.0,
            "total_closure_residual_3": 0.0,
            "source_abs_volume": 9.0,
            "source_abs_density": 9.0,
            "medium_frame_abs_boost_velocity": 0.96,
        },
        {
            "case": "a",
            "s": 0.9,
            "l": 2.0,
            "stage": "reset_decompression",
            "region": "live",
            "assignment": "packet",
            "volume_weight": 1.0,
            "medium_source_active": True,
            "covariant_divergence_live": True,
            "covariant_exchange_allowed_mask": True,
            "endpoint_exchange_l2_density_volume": 1.0,
            "total_closure_residual_l2_density_volume": 0.0,
            "total_closure_residual_l2_density": 0.0,
            "total_closure_residual_0": 0.0,
            "total_closure_residual_1": 0.0,
            "total_closure_residual_2": 0.0,
            "total_closure_residual_3": 0.0,
            "source_abs_volume": 1.0,
            "source_abs_density": 1.0,
            "medium_frame_abs_boost_velocity": 0.94,
        },
    ])
    point_path = total / "endpoint_support_total_closure_point_closure.csv"
    point.to_csv(point_path, index=False)
    closure = pd.DataFrame([{
        "passes_support_total_closure": True,
        "local_max_closure_residual_to_target_abs_PF_ratio": 0.50,
        "outside_support_tail_fraction": 0.0,
        "live_support_tail_fraction": 0.0,
    }])
    closure_path = total / "endpoint_support_total_closure_decision.csv"
    closure.to_csv(closure_path, index=False)
    write_manifest(total / "endpoint_support_total_closure_manifest.json", {
        "files": {"point_closure": str(point_path), "decision": str(closure_path)},
        "sha256": {
            "point_closure": sha256_file(point_path),
            "decision": sha256_file(closure_path),
        },
    })

    covariant = pd.DataFrame([{
        "passes_covariant_identity_audit": True,
        "projection_reconstruction_pass": True,
        "boost_subluminal_pass": True,
        "max_abs_boost_velocity": 0.96,
        "mixed_eigen_real_pass": True,
        "exchange_localization_pass": True,
    }])
    cov_path = cov / "endpoint_medium_covariant_decision.csv"
    covariant.to_csv(cov_path, index=False)
    write_manifest(cov / "endpoint_medium_covariant_manifest.json", {
        "files": {"decision": str(cov_path)},
        "sha256": {"decision": sha256_file(cov_path)},
    })

    return Moderate3P1SurfaceSpec(
        label,
        "test",
        "main_dense" if "dense" in label else "reference_baseline",
        service_rating,
        cov,
        total,
    )


class Beta075Moderate3P1CapstoneTests(unittest.TestCase):
    def test_default_surfaces_are_sealed_v5_only(self):
        surfaces = default_moderate_v5_surfaces()

        self.assertEqual([surface.service_rating for surface in surfaces], [5.0, 5.0])
        self.assertTrue(all("v5" in surface.label for surface in surfaces))

    def test_angular_weights_are_normalized(self):
        scenario = Moderate3P1ScenarioSpec("s", 0.03, 0.04, 0.01, 0.02, 0.1, 1.0, "read")

        _phi, weights = _angular_weights(scenario, 12)

        self.assertAlmostEqual(float(weights.mean()), 1.0)
        self.assertGreater(float(weights.min()), 0.0)

    def test_small_run_writes_parquet_and_does_not_evolve_live_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = _write_fake_surface(root, "sealed_baseline_v5", 5.0)
            dense = _write_fake_surface(root, "sealed_dense_v5", 5.0)
            first_order = root / "first_order"
            energy = root / "energy"
            first_order.mkdir()
            energy.mkdir()
            pd.DataFrame([{
                "hard_first_order_3p1_pass": True,
                "first_order_3p1_status": "first_order_3p1_entry_watch_pass",
            }]).to_csv(first_order / "beta075_first_order_3p1_decision.csv", index=False)
            pd.DataFrame([{
                "hard_constant_audit_pass": True,
                "protective_buffer_watch": True,
                "work_utilization": 0.82,
            }]).to_csv(energy / "beta075_source_family_energy_constant_decision.csv", index=False)
            inputs = Moderate3P1Inputs(
                first_order,
                energy,
                surfaces=(baseline, dense),
                scenarios=(Moderate3P1ScenarioSpec("axis", 0.0, 0.0, 0.0, 0.0, 0.05, 1.0, "read"),),
            )

            paths = run_moderate_3p1_v5_capstone(
                inputs,
                root / "out",
                spec=Moderate3P1Spec(n_phi=4, n_steps=5, time_chunk_steps=2, workers=1),
            )
            decision = pd.read_csv(paths["decision"]).iloc[0]
            summary = pd.read_csv(paths["scenario_summary"])
            gates = pd.read_csv(paths["classification_gates"])
            import json

            manifest = json.loads(paths["manifest"].read_text())

            self.assertEqual(decision["capstone_status"], "stage2_moderate_3p1_v5_capstone_watch_pass")
            self.assertEqual(int(summary["live_rows_evolved"].max()), 0)
            self.assertIn("no_live_row_evolution", set(gates["gate"]))
            self.assertGreater(int(manifest["rows"]["time_response"]), 0)
            self.assertTrue((root / "out" / "time_response").exists())


if __name__ == "__main__":
    unittest.main()
