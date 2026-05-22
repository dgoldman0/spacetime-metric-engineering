from __future__ import annotations

import math
import unittest

import pandas as pd

from adm_harness.endpoint_support_reservoir_exchange import build_support_reservoir_exchange_tables


class EndpointSupportReservoirExchangeTests(unittest.TestCase):
    def _frames(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        projection_rows = []
        divergence_rows = []
        idx = 0
        for s_idx in range(7):
            for l_idx in range(7):
                s = float(s_idx)
                l = float(l_idx)
                p = 0.04 * math.exp(-0.5 * (((s - 3.0) / 1.3) ** 2 + ((l - 2.5) / 1.1) ** 2))
                f = -0.03 * math.exp(-0.5 * (((s - 2.0) / 1.2) ** 2 + ((l - 4.0) / 1.0) ** 2))
                source_abs_density = abs(p) + abs(f) + 0.01
                common = {
                    "case": "toy_case",
                    "s": s,
                    "l": l,
                    "stage": "toy_stage",
                    "region": "support_edge",
                    "assignment": "support_edge_endpoint_junction",
                    "inside_packet_live": False,
                    "volume_weight": 1.0,
                    "source_abs_density": source_abs_density,
                }
                divergence_rows.append({
                    **common,
                    "alpha": 1.0,
                    "beta": 0.0,
                    "gamma_ll": 1.0,
                    "gamma_omega": 1.0,
                    "medium_source_active": True,
                    "covariant_exchange_allowed_mask": True,
                    "covariant_divergence_live": False,
                    "covariant_divergence_0": p,
                    "covariant_divergence_1": f,
                    "covariant_divergence_2": 0.0,
                    "covariant_divergence_3": 0.0,
                    "covariant_divergence_l2_density": math.sqrt(p * p + f * f),
                })
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

    def test_smooth_two_channel_exchange_can_pass_on_toy_field(self):
        projection, divergence = self._frames()
        outputs = build_support_reservoir_exchange_tables(
            projection,
            divergence,
            fit_scopes=["assignment"],
            s_centers=[6],
            l_centers=[6],
            width_multipliers=[0.70],
            ridges=[1.0e-8],
            pf_l1_gate=0.25,
            coordinate_error_gate=0.25,
            coefficient_gate=0.20,
            effective_coefficient_count_gate=80.0,
        )
        decision = outputs["decision"].iloc[0]
        summary = outputs["fit_scope_summary"].iloc[0]

        self.assertTrue(bool(decision["passes_support_reservoir_exchange_fit"]))
        self.assertLess(float(summary["normalized_abs_PF_l1_error"]), 0.25)
        self.assertEqual(int(summary["live_rows"]), 0)
        self.assertEqual(float(summary["fit_angular_exchange_volume"]), 0.0)


if __name__ == "__main__":
    unittest.main()
