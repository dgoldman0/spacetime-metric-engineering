from __future__ import annotations

import math
import unittest

import pandas as pd

from adm_harness.endpoint_medium_field_closure import build_endpoint_medium_field_closure_tables


class EndpointMediumFieldClosureTests(unittest.TestCase):
    def _frame(self) -> pd.DataFrame:
        rows = []
        idx = 0
        for s_idx in range(7):
            for l_idx in range(7):
                s = float(s_idx)
                l = float(l_idx)
                rows.append({
                    "label": "toy",
                    "case": "toy_case",
                    "point_index": idx,
                    "s": s,
                    "l": l,
                    "stage": "toy_stage",
                    "region": "support_edge",
                    "inside_packet_live": False,
                    "inside_packet_geom": False,
                    "residual_zone": "toy_zone",
                    "volume_weight": 1.0,
                    "sector": "J_endpoint_junction_layer",
                    "sector_description": "toy",
                    "assignment": "support_edge_endpoint_junction",
                    "sector_rho": 0.1,
                    "sector_p_l": 0.1,
                    "sector_j_l": 0.05,
                    "sector_p_omega": 0.04 * math.exp(-0.5 * (((s - 3.0) / 1.2) ** 2 + ((l - 3.0) / 1.0) ** 2)),
                })
                idx += 1
        return pd.DataFrame(rows)

    def test_smooth_internal_response_closes_toy_medium(self):
        outputs = build_endpoint_medium_field_closure_tables(
            self._frame(),
            source_name="toy",
            regulator_safety_factor=1.10,
            s_centers=[5],
            l_centers=[5],
            width_multipliers=[0.75],
            ridges=[1.0e-8],
            normalized_l1_gate=0.20,
            angular_watch_l1_gate=0.20,
            angular_residual_source_gate=0.02,
            coefficient_gate=0.25,
        )
        decision = outputs["feasibility_decision"].iloc[0]
        total = outputs["scope_summary"].loc[outputs["scope_summary"]["scope"] == "J_total"].iloc[0]

        self.assertTrue(bool(decision["passes_constrained_field_closure"]))
        self.assertTrue(bool(total["conservation_pass"]))
        self.assertLess(float(total["angular_closure_residual_to_source_ratio"]), 0.02)


if __name__ == "__main__":
    unittest.main()
