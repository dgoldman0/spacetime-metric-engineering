from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_j_conservation import (
    J_SECTOR,
    SUPPORT_ASSIGNMENT,
    build_endpoint_j_conservation_tables,
)


class EndpointJConservationTests(unittest.TestCase):
    def _row(self, point_index: int, s: float, l: float, *, live: bool = False) -> dict[str, object]:
        rho = -s
        p_l = -1.0
        j_l = l
        p_omega = 0.5 * l
        selected_margin = rho + p_l - 2.0 * abs(j_l)
        selected_deficit = max(-selected_margin, 0.0)
        volume = 1.0
        return {
            "label": "toy",
            "case": "toy_case",
            "point_index": point_index,
            "s": s,
            "l": l,
            "stage": "toy_stage",
            "region": "support_edge",
            "inside_packet_live": live,
            "inside_packet_geom": False,
            "residual_zone": "support_edge_shoulder",
            "volume_weight": volume,
            "sector": J_SECTOR,
            "sector_description": "",
            "assignment": SUPPORT_ASSIGNMENT,
            "sector_rho": rho,
            "sector_p_l": p_l,
            "sector_j_l": j_l,
            "sector_p_omega": p_omega,
            "sector_Tkk_plus": rho + p_l - 2.0 * j_l,
            "sector_Tkk_minus": rho + p_l + 2.0 * j_l,
            "sector_selected_null_margin": selected_margin,
            "sector_selected_null_deficit_density": selected_deficit,
            "sector_pair_l1_density": abs(rho) + abs(p_l),
            "sector_abs_current_density": abs(j_l),
            "sector_abs_pomega_density": abs(p_omega),
            "sector_selected_null_deficit_density_volume": selected_deficit * volume,
            "sector_pair_l1_density_volume": (abs(rho) + abs(p_l)) * volume,
            "sector_abs_current_density_volume": abs(j_l) * volume,
            "sector_abs_pomega_density_volume": abs(p_omega) * volume,
        }

    def _linear_conserved_grid(self, *, live_point: int | None = None) -> pd.DataFrame:
        rows = []
        point_index = 0
        for s in [0.0, 1.0, 2.0]:
            for l in [0.0, 1.0, 2.0]:
                rows.append(self._row(point_index, s, l, live=point_index == live_point))
                point_index += 1
        return pd.DataFrame(rows)

    def test_assignment_local_linear_grid_has_zero_conservation_proxy(self):
        outputs = build_endpoint_j_conservation_tables(self._linear_conserved_grid(), source_name="toy_source")
        support = outputs["summary"].loc[outputs["summary"]["scope"] == "support_edge"].iloc[0]

        self.assertEqual(int(support["rows"]), 9)
        self.assertEqual(int(support["scoreable_derivative_rows"]), 9)
        self.assertAlmostEqual(float(support["weighted_mean_continuity_abs_density"]), 0.0)
        self.assertAlmostEqual(float(support["weighted_mean_radial_momentum_abs_density"]), 0.0)
        self.assertAlmostEqual(float(support["weighted_mean_conservation_residual_norm"]), 0.0)
        self.assertEqual(support["diagnostic_read"], "finite_spread_proxy_not_conservation_proof")

    def test_live_endpoint_rows_fail_non_live_gate(self):
        outputs = build_endpoint_j_conservation_tables(self._linear_conserved_grid(live_point=4), source_name="toy_source")
        total = outputs["summary"].loc[outputs["summary"]["scope"] == "J_total"].iloc[0]

        self.assertEqual(int(total["live_rows"]), 1)
        self.assertEqual(total["diagnostic_read"], "fails_non_live_endpoint_gate")


if __name__ == "__main__":
    unittest.main()
