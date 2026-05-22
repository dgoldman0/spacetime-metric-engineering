from __future__ import annotations

import math
import unittest

import pandas as pd

from adm_harness.endpoint_j_closure_component import build_endpoint_j_closure_component_tables
from adm_harness.endpoint_j_conservation import J_SECTOR, SUPPORT_ASSIGNMENT
from adm_harness.endpoint_j_structured_source import _derive_sector_columns


class EndpointJClosureComponentTests(unittest.TestCase):
    def _target_row(self, point_index: int, s: float, l: float) -> dict[str, object]:
        envelope = math.exp(-0.5 * (((s - 1.0) / 0.55) ** 2 + ((l - 0.5) / 0.45) ** 2))
        rho = -0.5 * envelope
        p_l = -0.4 * envelope
        j_l = 0.12 * envelope
        p_omega = -0.25 * envelope
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
            "volume_weight": 1.0,
            "sector": J_SECTOR,
            "sector_description": "",
            "assignment": SUPPORT_ASSIGNMENT,
            "sector_rho": rho,
            "sector_p_l": p_l,
            "sector_j_l": j_l,
            "sector_p_omega": p_omega,
        }

    def _target(self) -> pd.DataFrame:
        rows = []
        point_index = 0
        for s in [0.0, 0.5, 1.0, 1.5, 2.0]:
            for l in [-0.5, 0.0, 0.5, 1.0, 1.5]:
                rows.append(self._target_row(point_index, s, l))
                point_index += 1
        return _derive_sector_columns(pd.DataFrame(rows))

    def _base(self, target: pd.DataFrame) -> pd.DataFrame:
        out = target.copy()
        for column in ["sector_rho", "sector_p_l", "sector_j_l", "sector_p_omega"]:
            out[column] = 0.0
        return _derive_sector_columns(out)

    def test_closure_component_reduces_missing_support_component(self):
        target = self._target()
        outputs = build_endpoint_j_closure_component_tables(
            target,
            self._base(target),
            mode_counts=[1],
            center_counts=[4],
            width_multipliers=[0.9],
            ridges=[1.0e-12],
            conservation_weights=[0.0],
            angular_weights=[0.0],
            overburden_weight=1.0,
        )

        component = outputs["component_summary"]
        base_error = component.loc[component["model"] == "base", "normalized_l1_error"].mean()
        fit_error = component.loc[component["model"] == "fit", "normalized_l1_error"].mean()
        summary = outputs["assignment_summary"].iloc[0]

        self.assertLess(float(fit_error), float(base_error) * 0.25)
        self.assertLess(float(summary["fit_selected_ratio"]), 1.10)
        self.assertEqual(int(summary["fit_live_rows"]), 0)


if __name__ == "__main__":
    unittest.main()
