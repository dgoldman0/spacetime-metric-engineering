from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from adm_harness.service_modifiers import compute_service_field_delta
from adm_harness.validation import validate_field_delta, validate_fields


class ServiceSynthesisValidationTests(unittest.TestCase):
    def _fields(self):
        s = np.linspace(0.0, 1.0, 5)
        l = np.linspace(-1.0, 1.0, 7)
        ss, ll = np.meshgrid(s, l, indexing="ij")
        shape = ss.shape
        return {
            "s_grid": s,
            "l_grid": l,
            "alpha": np.ones(shape),
            "beta": 0.01 * np.sin(np.pi * ss) * np.exp(-ll * ll),
            "gamma_ll": np.ones(shape) * 2.0,
            "gamma_omega": np.ones(shape) * 4.0,
            "rho": np.zeros(shape),
            "j_l": np.zeros(shape),
            "k_l": np.zeros(shape),
            "k_omega": np.zeros(shape),
            "K": np.zeros(shape),
            "R3": np.zeros(shape),
        }

    def _ledger(self, fields):
        s = fields["s_grid"]
        l = fields["l_grid"]
        ss, ll = np.meshgrid(s, l, indexing="ij")
        n = ss.size
        return pd.DataFrame({
            "s": ss.ravel(),
            "l": ll.ravel(),
            "stage": ["catch_rematch"] * n,
            "region": ["test"] * n,
            "packet_live": np.zeros(n, dtype=bool),
            "packet_edge": np.ones(n, dtype=bool),
            "support_shell": np.ones(n, dtype=bool),
            "delta_j_l": np.linspace(-1.0, 1.0, n),
        })

    def test_field_validation_accepts_required_arrays(self):
        report = validate_fields(self._fields(), require_derived=True)
        self.assertTrue(report.ok, report.errors)

    def test_delta_validation_rejects_unknown_service_target_after_mapping(self):
        fields = self._fields()
        bad = {"unknown": np.zeros((5, 7))}
        report = validate_field_delta(bad, fields)
        self.assertFalse(report.ok)

    def test_compact_carrying_flow_law_returns_bounded_delta(self):
        fields = self._fields()
        ledger = self._ledger(fields)
        cfg = {
            "synthesis": {"enabled": True},
            "service": {
                "carrying_flow": {
                    "enabled": True,
                    "law": "compact_momentum_localizer",
                    "scope": "catch_rematch_edge",
                    "signal": "delta_j_l",
                    "amplitude": 0.005,
                    "max_abs_change": 0.005,
                    "smoothness_order": 1,
                }
            },
        }
        result = compute_service_field_delta(fields, ledger, cfg)
        self.assertIn("beta", result.delta)
        self.assertLessEqual(np.max(np.abs(result.delta["beta"])), 0.005 + 1e-15)
        self.assertEqual(result.metadata["modified_service_fields"], ["carrying_flow"])


if __name__ == "__main__":
    unittest.main()
