from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.intermediate_source_model import (
    _closure_summary,
    _live_gate_summary,
    build_point_sector_stress,
)


class IntermediateSourceModelTests(unittest.TestCase):
    def _points(self) -> pd.DataFrame:
        rows = [
            {
                "label": "toy",
                "case": "toy_case",
                "point_index": 0,
                "s": 0.0,
                "l": 0.0,
                "stage": "catch_rematch",
                "region": "core_throat",
                "inside_packet_live": False,
                "inside_packet_geom": False,
                "residual_zone": "core_cloud_body",
                "volume_weight": 2.0,
                "string_cloud_rho": 0.5,
                "string_cloud_p_l": -0.5,
                "residual_rho": 0.01,
                "residual_p_l": -0.02,
                "residual_j_l": 0.03,
                "residual_p_omega": 0.04,
            },
            {
                "label": "toy",
                "case": "toy_case",
                "point_index": 1,
                "s": 0.0,
                "l": 1.0,
                "stage": "entry_precatch",
                "region": "support_edge",
                "inside_packet_live": False,
                "inside_packet_geom": False,
                "residual_zone": "support_edge_shoulder",
                "volume_weight": 3.0,
                "string_cloud_rho": 0.25,
                "string_cloud_p_l": -0.25,
                "residual_rho": -0.02,
                "residual_p_l": -0.01,
                "residual_j_l": -0.05,
                "residual_p_omega": 0.06,
            },
            {
                "label": "toy",
                "case": "toy_case",
                "point_index": 2,
                "s": 1.0,
                "l": 1.0,
                "stage": "reset_decompression",
                "region": "support_edge",
                "inside_packet_live": False,
                "inside_packet_geom": False,
                "residual_zone": "reset_cap",
                "volume_weight": 5.0,
                "string_cloud_rho": 0.125,
                "string_cloud_p_l": -0.125,
                "residual_rho": -0.03,
                "residual_p_l": -0.04,
                "residual_j_l": 0.07,
                "residual_p_omega": -0.08,
            },
        ]
        points = pd.DataFrame(rows)
        points["rho_euler"] = points["string_cloud_rho"] + points["residual_rho"]
        points["p_l_unit"] = points["string_cloud_p_l"] + points["residual_p_l"]
        points["j_l_unit"] = points["residual_j_l"]
        points["p_omega_unit"] = points["residual_p_omega"]
        return points

    def test_sector_rows_reconstruct_point_stress(self):
        points = self._points()
        sectors = build_point_sector_stress(points)
        closure = _closure_summary(points, sectors).iloc[0]

        self.assertEqual(int(closure["points"]), 3)
        self.assertEqual(int(closure["model_rows"]), 10)
        self.assertAlmostEqual(float(closure["weighted_total_abs_error"]), 0.0)
        self.assertAlmostEqual(float(closure["max_abs_rho_error"]), 0.0)
        self.assertAlmostEqual(float(closure["max_abs_p_l_error"]), 0.0)
        self.assertAlmostEqual(float(closure["max_abs_j_l_error"]), 0.0)
        self.assertAlmostEqual(float(closure["max_abs_p_omega_error"]), 0.0)

    def test_string_cloud_sector_has_zero_radial_null_contraction(self):
        sectors = build_point_sector_stress(self._points())
        cloud = sectors.loc[sectors["sector"] == "S0_constant_flux_string_cloud"]

        self.assertEqual(len(cloud), 3)
        self.assertTrue((cloud["sector_Tkk_plus"].abs() < 1.0e-15).all())
        self.assertTrue((cloud["sector_Tkk_minus"].abs() < 1.0e-15).all())
        self.assertTrue((cloud["sector_abs_current_density"] == 0.0).all())
        self.assertTrue((cloud["sector_abs_pomega_density"] == 0.0).all())

    def test_zone_specific_sectors_are_assigned(self):
        sectors = build_point_sector_stress(self._points())
        by_point = sectors.groupby("point_index")["sector"].agg(set).to_dict()

        self.assertIn("core_body_residual_leakage", by_point[0])
        self.assertIn("S1_support_edge_shoulder_radial_trim", by_point[1])
        self.assertIn("S2_reset_endpoint_radial_cap", by_point[2])
        self.assertIn("DH_current_relaxation", by_point[1])
        self.assertIn("DH_current_relaxation", by_point[2])
        self.assertIn("G_angular_endpoint_capacity", by_point[1])
        self.assertIn("G_angular_endpoint_capacity", by_point[2])

    def test_live_gate_summary_passes_for_non_live_model(self):
        sectors = build_point_sector_stress(self._points())
        live = _live_gate_summary(sectors)

        self.assertFalse(live.empty)
        self.assertTrue(live["passes_live_gate"].astype(bool).all())
        self.assertEqual(float(live["live_pair_l1"].sum()), 0.0)
        self.assertEqual(float(live["live_selected_null_deficit"].sum()), 0.0)


if __name__ == "__main__":
    unittest.main()
