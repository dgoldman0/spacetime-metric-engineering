from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_support_total_closure import build_support_total_closure_tables


class EndpointSupportTotalClosureTests(unittest.TestCase):
    def test_candidate_support_current_cancels_endpoint_exchange(self):
        point = pd.DataFrame({
            "case": ["toy"] * 4,
            "s": [0.0, 1.0, 2.0, 3.0],
            "l": [0.0, 0.0, 0.0, 0.0],
            "assignment": ["reset_decompression_endpoint_junction", "reset_decompression_endpoint_junction", "", ""],
            "stage": ["reset_decompression"] * 4,
            "region": ["support_edge"] * 4,
            "volume_weight": [1.0, 1.0, 1.0, 1.0],
            "medium_source_active": [True, True, False, False],
            "covariant_exchange_allowed_mask": [True, True, True, False],
            "covariant_divergence_live": [False, False, False, False],
            "covariant_divergence_0": [0.10, -0.08, 0.02, 0.0],
            "covariant_divergence_1": [0.05, 0.03, -0.01, 0.0],
            "covariant_divergence_2": [0.0, 0.0, 0.0, 0.0],
            "covariant_divergence_3": [0.0, 0.0, 0.0, 0.0],
            "fit_J_0": [0.10, -0.08, 0.02, 0.0],
            "fit_J_1": [0.05, 0.03, -0.01, 0.0],
            "fit_J_2": [0.0, 0.0, 0.0, 0.0],
            "fit_J_3": [0.0, 0.0, 0.0, 0.0],
            "target_abs_PF_density": [0.15, 0.11, 0.03, 0.0],
            "fit_abs_PF_density": [0.15, 0.11, 0.03, 0.0],
            "fit_error_abs_PF_density": [0.0, 0.0, 0.0, 0.0],
        })
        stroke_decision = pd.DataFrame([{"passes_support_stroke_exchange_fit": True}])

        outputs = build_support_total_closure_tables(point, stroke_decision)
        decision = outputs["decision"].iloc[0]
        active = outputs["scope_summary"].loc[outputs["scope_summary"]["scope"] == "active"].iloc[0]

        self.assertTrue(bool(decision["passes_support_total_closure"]))
        self.assertEqual(float(active["total_closure_residual_l2_volume"]), 0.0)
        self.assertEqual(float(decision["outside_support_tail_fraction"]), 0.0)
        self.assertEqual(float(decision["full_candidate_support_angular_volume"]), 0.0)


if __name__ == "__main__":
    unittest.main()
