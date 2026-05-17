from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import generate_service_factor_inputs as generator
import run_validation_ladder as ladder
from adm_harness import source_ledger


class ValidationLadderHardeningTests(unittest.TestCase):
    def test_service_factor_is_inferred_from_matching_configs(self):
        args = SimpleNamespace(service_factor=None)
        baseline = {"service": {"velocity": 5.0}}
        target = {"service": {"velocity": 5.0}}

        self.assertEqual(ladder._infer_service_factor(args, baseline, target), 5.0)

    def test_service_factor_mismatch_is_rejected(self):
        args = SimpleNamespace(service_factor=5.0)
        baseline = {"service": {"velocity": 5.0}}
        target = {"service": {"velocity": 10.0}}

        with self.assertRaises(SystemExit):
            ladder._infer_service_factor(args, baseline, target)

    def test_defaults_are_derived_from_service_factor(self):
        args = SimpleNamespace(output_root=None, packet_member=None)

        output_root, output_inferred = ladder._resolve_output_root(args, "v10")
        packet_member, packet_inferred = ladder._resolve_packet_member(args, 10.0)

        self.assertTrue(output_inferred)
        self.assertEqual(output_root, Path("runs/v10_validation_ladder"))
        self.assertTrue(packet_inferred)
        self.assertEqual(packet_member, "highres_41x73/V10_tuned_w0569_eta200.csv")

    def test_ramp_envelope_keeps_warning_and_failure_separate(self):
        ramp = pd.DataFrame(
            [
                {"amplitude": 1e-4, "status_class": "pass", "hard_gate_passed": True, "warning_flag": False},
                {"amplitude": 5e-4, "status_class": "warning", "hard_gate_passed": True, "warning_flag": True},
                {"amplitude": 1e-3, "status_class": "fail", "hard_gate_passed": False, "warning_flag": True},
            ]
        )

        envelope = ladder._ramp_envelope(ramp)

        self.assertTrue(envelope["enabled"])
        self.assertEqual(envelope["last_no_warning_pass_amplitude"], 1e-4)
        self.assertEqual(envelope["last_hard_pass_amplitude"], 5e-4)
        self.assertEqual(envelope["first_warning_amplitude"], 5e-4)
        self.assertEqual(envelope["first_hard_failure_amplitude"], 1e-3)
        self.assertEqual(envelope["status_counts"], {"fail": 1, "pass": 1, "warning": 1})

    def test_service_factor_generator_writes_reusable_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            metadata = generator.generate_products(
                SimpleNamespace(
                    service_factor=6.0,
                    output_dir=base / "data",
                    config_dir=base / "configs",
                    ns=9,
                    nl=13,
                    w_th=0.569,
                    eta_N=2.0,
                    support_radius=1.75,
                )
            )

            for path in metadata["files"].values():
                self.assertTrue(Path(path).exists(), path)
            self.assertEqual(metadata["service_factor_label"], "v6")
            self.assertIn("max_live_packet_norm", metadata["diagnostics"])
            self.assertIn("catch_support_delta_j_l_fraction", metadata["diagnostics"])

    def test_service_factor_generator_rejects_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            args = SimpleNamespace(
                service_factor=0.0,
                output_dir=base / "data",
                config_dir=base / "configs",
                ns=9,
                nl=13,
                w_th=0.569,
                eta_N=2.0,
                support_radius=1.75,
            )

            with self.assertRaises(SystemExit):
                generator.generate_products(args)

    def test_source_ledger_small_grid_has_heavy_channels(self):
        case = source_ledger.branch_case("tuned_w0569_eta200", service_factor=5.0)
        points = source_ledger.compute_case(case, ns=3, nl=3, progress=False)
        summary, compact, stage, safety, decision = source_ledger.summarize(points)

        self.assertEqual(len(points), 9)
        self.assertIn("Tkk_min_radial", points.columns)
        self.assertIn("p_l_unit", points.columns)
        self.assertIn("rho_packet", points.columns)
        self.assertIn("neg_Tkk_radial", set(compact["channel"]))
        self.assertIn("abs_p_l", set(compact["channel"]))
        self.assertEqual(int(safety["positive_packet_norm_live"].iloc[0]), 0)
        self.assertIn("score", decision.columns)
        self.assertFalse(summary.empty)
        self.assertFalse(stage.empty)
        self.assertFalse(source_ledger.top_bad_points(points, limit=2).empty)

    def test_source_ledger_reference_compare_identity(self):
        case = source_ledger.branch_case("conservative_w0565_eta200", service_factor=5.0)
        points = source_ledger.compute_case(case, ns=3, nl=3, progress=False)
        comparison = source_ledger.compare_to_reference(points, points, reference_case=case.name)

        self.assertGreater(len(comparison), 0)
        self.assertEqual(float(comparison["max_abs_error"].max()), 0.0)


if __name__ == "__main__":
    unittest.main()
