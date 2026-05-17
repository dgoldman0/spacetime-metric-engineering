from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_validation_ladder as ladder


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


if __name__ == "__main__":
    unittest.main()
