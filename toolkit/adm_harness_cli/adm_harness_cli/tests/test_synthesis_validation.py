import unittest
import numpy as np
import pandas as pd

from adm_harness.adm import apply_field_delta, recompute_adm_fields
from adm_harness.absorbers import compute_field_delta
from adm_harness.metrics import build_point_ledger
from adm_harness.validation import validate_field_delta, validate_fields


class SynthesisValidationTests(unittest.TestCase):
    def make_fields(self):
        s = np.linspace(0.0, 1.0, 5)
        l = np.linspace(-1.0, 1.0, 7)
        ss, ll = np.meshgrid(s, l, indexing="ij")
        fields = {
            "s_grid": s,
            "l_grid": l,
            "alpha": np.ones_like(ss) * 1.2,
            "beta": 0.01 * np.sin(np.pi * ss) * np.exp(-ll * ll),
            "gamma_ll": np.ones_like(ss) * 2.0,
            "gamma_omega": 4.0 + ll * ll,
            "packet_norm": np.zeros_like(ss),
            "gtt": np.zeros_like(ss),
            "R3": np.zeros_like(ss),
            "rho": np.zeros_like(ss),
            "j_l": np.zeros_like(ss),
        }
        return recompute_adm_fields(fields, recompute_r3=True)

    def test_identity_recompute_is_stable(self):
        fields = self.make_fields()
        recomputed = recompute_adm_fields(fields, recompute_r3=True)
        self.assertLess(np.max(np.abs(recomputed["rho"] - fields["rho"])), 1e-12)
        self.assertLess(np.max(np.abs(recomputed["j_l"] - fields["j_l"])), 1e-12)

    def test_delta_validation_catches_shape(self):
        fields = self.make_fields()
        bad = {"beta": np.zeros((3, 3))}
        report = validate_field_delta(bad, fields)
        self.assertFalse(report.ok)

    def test_compact_law_returns_bounded_beta_delta(self):
        fields = self.make_fields()
        ledger = build_point_ledger(fields, velocity=5.0)
        ledger["stage"] = "catch_rematch"
        ledger["packet_edge"] = True
        ledger["delta_j_l"] = np.linspace(-1, 1, len(ledger))
        result = compute_field_delta(
            fields,
            preliminary_ledger=ledger,
            substrate_fields=None,
            absorber_cfg={
                "law": "compact_beta_localizer",
                "target_field": "beta",
                "support_mask": "catch_rematch_edge",
                "coefficients": {"amplitude": 0.01, "max_abs_delta": 0.005},
            },
        )
        self.assertIn("beta", result.delta)
        self.assertLessEqual(np.max(np.abs(result.delta["beta"])), 0.005 + 1e-15)
        self.assertTrue(validate_field_delta(result.delta, fields).ok)


if __name__ == "__main__":
    unittest.main()
