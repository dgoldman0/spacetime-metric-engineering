from __future__ import annotations

import math
import unittest

import pandas as pd

from adm_harness.endpoint_medium_constructive_probe import build_constructive_medium_probe_tables


class EndpointMediumConstructiveProbeTests(unittest.TestCase):
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
                    "sector_j_l": 0.105,
                    "sector_p_omega": 0.04 * math.exp(-0.5 * (((s - 3.0) / 1.2) ** 2 + ((l - 3.0) / 1.0) ** 2)),
                })
                idx += 1
        return pd.DataFrame(rows)

    def test_smooth_internal_response_can_pass_on_toy_field(self):
        outputs = build_constructive_medium_probe_tables(
            self._frame(),
            source_name="toy",
            regulator_safety_factor=1.10,
            s_centers=[5],
            l_centers=[5],
            width_multipliers=[0.75],
            ridges=[1.0e-8],
            normalized_l1_gate=0.20,
            angular_watch_l1_gate=0.20,
            coefficient_gate=0.25,
        )
        decision = outputs["feasibility_decision"].iloc[0]

        self.assertTrue(bool(decision["passes_internal_response_probe"]))
        self.assertLess(float(decision["worst_normalized_l1_error"]), 0.20)


if __name__ == "__main__":
    unittest.main()
