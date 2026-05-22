from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_current_regulator import (
    build_current_regulator_point_table,
    build_endpoint_current_regulator_tables,
)


class EndpointCurrentRegulatorTests(unittest.TestCase):
    def _row(
        self,
        idx: int,
        *,
        s: float,
        l: float,
        rho: float = 0.1,
        p_l: float = 0.1,
        j_l: float = 0.105,
        p_omega: float = 1.0,
        live: bool = False,
    ) -> dict[str, object]:
        return {
            "label": "toy",
            "case": "toy_case",
            "point_index": idx,
            "s": s,
            "l": l,
            "stage": "toy_stage",
            "region": "support_edge",
            "inside_packet_live": live,
            "inside_packet_geom": False,
            "residual_zone": "toy_zone",
            "volume_weight": 1.0,
            "sector": "J_endpoint_junction_layer",
            "sector_description": "toy",
            "assignment": "support_edge_endpoint_junction",
            "sector_rho": rho,
            "sector_p_l": p_l,
            "sector_j_l": j_l,
            "sector_p_omega": p_omega,
        }

    def _spread_frame(self, *, live_index: int | None = None) -> pd.DataFrame:
        rows = []
        idx = 0
        for s_idx in range(6):
            for l_idx in range(5):
                rows.append(
                    self._row(
                        idx,
                        s=float(s_idx),
                        l=float(l_idx),
                        live=(live_index is not None and idx == live_index),
                    )
                )
                idx += 1
        return pd.DataFrame(rows)

    def test_regulator_adds_minimal_enthalpy_cushion(self):
        frame = pd.DataFrame([
            self._row(0, s=0.0, l=0.0, rho=1.0, p_l=1.0, j_l=0.1),
            self._row(1, s=0.0, l=1.0, rho=0.1, p_l=0.1, j_l=0.2),
        ])

        points = build_current_regulator_point_table(frame)

        self.assertAlmostEqual(float(points.loc[0, "endpoint_current_regulator"]), 0.0)
        self.assertAlmostEqual(float(points.loc[1, "endpoint_current_regulator"]), 0.2)
        self.assertAlmostEqual(float(points.loc[1, "regulator_delta_sector_rho"]), 0.1)
        self.assertAlmostEqual(float(points.loc[1, "regulator_delta_sector_p_l"]), 0.1)
        self.assertEqual(int((points["regulated_stress_algebraic_type"] == "type_iv_flux_dominant").sum()), 0)

    def test_spread_non_live_regulator_passes_first_screen(self):
        outputs = build_endpoint_current_regulator_tables(
            self._spread_frame(),
            source_name="toy",
            regulator_source_ratio_gate=0.06,
        )
        decision = outputs["feasibility_decision"].iloc[0]

        self.assertTrue(bool(decision["passes_screen"]))
        self.assertTrue(bool(decision["zero_live_rows_pass"]))
        self.assertTrue(bool(decision["regulator_budget_pass"]))
        self.assertEqual(int(decision["post_regulator_type_iv_rows"]), 0)

    def test_live_regulator_row_fails_non_live_gate(self):
        outputs = build_endpoint_current_regulator_tables(
            self._spread_frame(live_index=3),
            source_name="toy",
            regulator_source_ratio_gate=0.06,
        )
        decision = outputs["feasibility_decision"].iloc[0]

        self.assertFalse(bool(decision["passes_screen"]))
        self.assertFalse(bool(decision["zero_live_rows_pass"]))
        self.assertGreater(int(decision["regulator_live_rows"]), 0)


if __name__ == "__main__":
    unittest.main()
