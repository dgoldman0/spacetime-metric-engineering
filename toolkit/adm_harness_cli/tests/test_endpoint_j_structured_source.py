from __future__ import annotations

import math
import unittest

import pandas as pd

from adm_harness.endpoint_j_conservation import J_SECTOR, SUPPORT_ASSIGNMENT
from adm_harness.endpoint_j_structured_source import build_structured_endpoint_j_source_tables


class EndpointJStructuredSourceTests(unittest.TestCase):
    def _row(self, point_index: int, s: float, l: float) -> dict[str, object]:
        envelope = math.exp(-0.5 * (((s - 1.0) / 0.8) ** 2 + ((l - 0.5) / 0.7) ** 2))
        vector = (-0.9, -0.7, 0.16, -0.35)
        rho, p_l, j_l, p_omega = [envelope * item for item in vector]
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
            "inside_packet_live": False,
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

    def _target(self) -> pd.DataFrame:
        rows = []
        point_index = 0
        for s in [0.0, 0.5, 1.0, 1.5, 2.0]:
            for l in [-0.5, 0.0, 0.5, 1.0, 1.5]:
                rows.append(self._row(point_index, s, l))
                point_index += 1
        return pd.DataFrame(rows)

    def test_structured_fit_recovers_single_stress_vector_target(self):
        outputs = build_structured_endpoint_j_source_tables(
            self._target(),
            s_centers=5,
            l_centers=5,
            mode_counts=[1],
            width_multipliers=[1.0],
            ridges=[1.0e-12],
            edge_tail_counts=[0],
            overburden_weight=1.0,
        )
        component = outputs["component_summary"]
        assignment = outputs["assignment_summary"].iloc[0]
        conservation = outputs["fit_conservation_summary"].loc[
            outputs["fit_conservation_summary"]["scope"] == "support_edge"
        ].iloc[0]

        self.assertTrue((component["normalized_l1_error"].astype(float) < 0.02).all())
        self.assertLess(float(assignment["fit_selected_ratio"]), 1.05)
        self.assertLess(float(assignment["fit_current_ratio"]), 1.05)
        self.assertLess(float(assignment["fit_pomega_ratio"]), 1.05)
        self.assertEqual(int(conservation["live_rows"]), 0)


if __name__ == "__main__":
    unittest.main()
