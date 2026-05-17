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
        self.assertIn("beta", result.delta)  # internal bundle key for the public carrying_flow field
        self.assertLessEqual(np.max(np.abs(result.delta["beta"])), 0.005 + 1e-15)
        self.assertEqual(result.metadata["modified_service_fields"], ["carrying_flow"])

    def test_config_validation_rejects_unknown_service_law(self):
        from adm_harness.validation import validate_config_contract

        cfg = {
            "inputs": {"exact_fields": "dummy.npz"},
            "synthesis": {"enabled": True},
            "service": {"carrying_flow": {"enabled": True, "law": "bogus_law"}},
        }
        report = validate_config_contract(cfg)
        self.assertFalse(report.ok)
        self.assertTrue(any("Unknown service modifier law" in e for e in report.errors))

    def test_config_validation_rejects_compact_law_on_wrong_service_field(self):
        from adm_harness.validation import validate_config_contract

        cfg = {
            "inputs": {"exact_fields": "dummy.npz"},
            "synthesis": {"enabled": True},
            "service": {"clock_lapse": {"enabled": True, "law": "compact_momentum_localizer"}},
        }
        report = validate_config_contract(cfg)
        self.assertFalse(report.ok)
        self.assertTrue(any("can only target carrying_flow" in e for e in report.errors))

    def test_mixed_catch_window_preserves_support_allocation(self):
        from adm_harness.service_modifiers import build_service_window, summarize_window_allocation

        fields = self._fields()
        ledger = self._ledger(fields).copy()
        # Split the toy ledger so the old packet-edge-only scope and the
        # support-shell component occupy different points.
        n = len(ledger)
        ledger["packet_edge"] = False
        ledger.loc[: n // 2 - 1, "packet_edge"] = True
        ledger["packet_live"] = ledger["packet_edge"]
        ledger["support_shell"] = False
        ledger.loc[n // 2 :, "support_shell"] = True
        mixed = {
            "scope": "catch_rematch_edge_support_mix",
            "allocation_mode": "edge_support_mix",
            "packet_exclusion": 0.8,
            "support_shell_gain": 2.0,
            "edge_bias": 0.0,
            "smoothness_order": 0,
        }
        old = {
            "scope": "catch_rematch_edge",
            "packet_exclusion": 0.8,
            "support_shell_gain": 2.0,
            "edge_bias": 0.0,
            "smoothness_order": 0,
        }
        mixed_window = build_service_window(fields, ledger, mixed)
        old_window = build_service_window(fields, ledger, old)
        mixed_summary = summarize_window_allocation(ledger, mixed_window)
        old_summary = summarize_window_allocation(ledger, old_window)
        self.assertGreater(mixed_summary["window_support_shell_fraction"], 0.0)
        self.assertGreater(mixed_summary["window_support_shell_fraction"], old_summary["window_support_shell_fraction"])
        self.assertLess(mixed_summary["window_packet_edge_fraction"], old_summary["window_packet_edge_fraction"])

    def test_temporal_width_without_center_shapes_window(self):
        from adm_harness.service_modifiers import build_service_window

        fields = self._fields()
        ledger = self._ledger(fields)
        narrow = build_service_window(fields, ledger, {
            "scope": "catch_rematch_edge",
            "temporal_width": 0.1,
            "smoothness_order": 0,
        })
        wide = build_service_window(fields, ledger, {
            "scope": "catch_rematch_edge",
            "temporal_width": 10.0,
            "smoothness_order": 0,
        })
        self.assertFalse(np.allclose(narrow, wide))
        self.assertLess(float(narrow.sum()), float(wide.sum()))

    def test_radial_width_without_center_shapes_window(self):
        from adm_harness.service_modifiers import build_service_window

        fields = self._fields()
        ledger = self._ledger(fields)
        narrow = build_service_window(fields, ledger, {
            "scope": "catch_rematch_edge",
            "radial_width": 0.2,
            "smoothness_order": 0,
        })
        wide = build_service_window(fields, ledger, {
            "scope": "catch_rematch_edge",
            "radial_width": 10.0,
            "smoothness_order": 0,
        })
        self.assertFalse(np.allclose(narrow, wide))
        self.assertLess(float(narrow.sum()), float(wide.sum()))

    def test_catch_lead_shifts_temporal_window(self):
        from adm_harness.service_modifiers import build_service_window

        fields = self._fields()
        ledger = self._ledger(fields)
        earlier = build_service_window(fields, ledger, {
            "scope": "catch_rematch_edge",
            "catch_lead": 0.25,
            "smoothness_order": 0,
        })
        later = build_service_window(fields, ledger, {
            "scope": "catch_rematch_edge",
            "catch_lead": -0.25,
            "smoothness_order": 0,
        })
        s = fields["s_grid"]
        earlier_center = float((earlier.sum(axis=1) @ s) / earlier.sum())
        later_center = float((later.sum(axis=1) @ s) / later.sum())
        self.assertLess(earlier_center, later_center)

    def test_config_validation_rejects_non_numeric_catch_lead(self):
        from adm_harness.validation import validate_config_contract

        cfg = {
            "inputs": {"exact_fields": "dummy.npz"},
            "synthesis": {"enabled": True},
            "service": {"carrying_flow": {"enabled": True, "law": "compact_momentum_localizer", "catch_lead": "early"}},
        }
        report = validate_config_contract(cfg)
        self.assertFalse(report.ok)
        self.assertTrue(any("catch_lead must be numeric" in e for e in report.errors))


if __name__ == "__main__":
    unittest.main()
