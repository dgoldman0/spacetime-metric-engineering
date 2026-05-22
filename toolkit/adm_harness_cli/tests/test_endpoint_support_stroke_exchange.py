from __future__ import annotations

import math
import unittest

import pandas as pd

from adm_harness.endpoint_support_stroke_exchange import build_support_stroke_exchange_tables


class EndpointSupportStrokeExchangeTests(unittest.TestCase):
    def _frames(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        projection_rows = []
        divergence_rows = []
        idx = 0
        for s_idx in range(7):
            for l_idx in range(7):
                s = float(s_idx)
                l = float(l_idx)
                body = math.exp(-0.5 * (((s - 3.0) / 1.4) ** 2 + ((l - 3.0) / 1.2) ** 2))
                edge = (s - 3.0) * math.exp(-0.5 * (((s - 3.0) / 1.2) ** 2 + ((l - 2.5) / 1.0) ** 2))
                p = 0.025 * body - 0.018 * edge
                f = -0.020 * body + 0.014 * (l - 3.0) * body
                source_abs_density = abs(p) + abs(f) + 0.01
                active = 1 <= s_idx <= 5 and 1 <= l_idx <= 5
                allowed = active or (s_idx in {0, 6} and 1 <= l_idx <= 5)
                common = {
                    "case": "toy_case",
                    "s": s,
                    "l": l,
                    "stage": "reset_decompression",
                    "region": "support_edge",
                    "assignment": "reset_decompression_endpoint_junction" if active else "",
                    "inside_packet_live": False,
                    "volume_weight": 1.0,
                    "source_abs_density": source_abs_density if active else 0.0,
                }
                divergence_rows.append({
                    **common,
                    "alpha": 1.0,
                    "beta": 0.0,
                    "gamma_ll": 1.0,
                    "gamma_omega": 1.0,
                    "medium_source_active": active,
                    "covariant_exchange_allowed_mask": allowed,
                    "covariant_divergence_live": False,
                    "covariant_divergence_0": p if allowed else 0.0,
                    "covariant_divergence_1": f if allowed else 0.0,
                    "covariant_divergence_2": 0.0,
                    "covariant_divergence_3": 0.0,
                    "covariant_divergence_l2_density": math.sqrt(p * p + f * f) if allowed else 0.0,
                    "h_ref": 1.0,
                })
                if active:
                    projection_rows.append({
                        **common,
                        "point_index": idx,
                        "enthalpy_buffer_density": 0.25,
                        "transport_margin": 0.40,
                        "regulated_heat_flux_ratio": 0.60,
                        "regulated_type_i_margin": 0.20,
                        "source_abs_volume": source_abs_density,
                    })
                    idx += 1
        return pd.DataFrame(projection_rows), pd.DataFrame(divergence_rows)

    def test_stroke_exchange_fits_toy_field_and_scores_tails(self):
        projection, divergence = self._frames()
        outputs = build_support_stroke_exchange_tables(
            projection,
            divergence,
            fit_scopes=["phase_region"],
            fit_domains=["allowed"],
            s_centers=[6],
            l_centers=[6],
            width_multipliers=[0.70],
            ridges=[1.0e-8],
            active_pf_l1_gate=0.25,
            allowed_pf_l1_gate=0.25,
            coordinate_error_gate=0.30,
            coefficient_gate=0.50,
            effective_coefficient_count_gate=200.0,
            outside_tail_fraction_gate=0.15,
        )
        decision = outputs["decision"].iloc[0]
        summary = outputs["fit_scope_summary"].iloc[0]

        self.assertTrue(bool(decision["passes_support_stroke_exchange_fit"]))
        self.assertLess(float(summary["normalized_active_abs_PF_l1_error"]), 0.25)
        self.assertLess(float(summary["normalized_allowed_abs_PF_l1_error"]), 0.25)
        self.assertLess(float(summary["outside_tail_fraction"]), 0.15)
        self.assertEqual(float(summary["fit_angular_exchange_volume"]), 0.0)


if __name__ == "__main__":
    unittest.main()
