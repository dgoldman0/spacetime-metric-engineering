from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.intermediate_source_snec import (
    INTERMEDIATE_RESIDUAL_SECTOR,
    _build_intermediate_label_grids,
    _sector_value_points,
    _summary_table,
)


class IntermediateSourceSNECTests(unittest.TestCase):
    def _points(self) -> pd.DataFrame:
        rows = []
        point_index = 0
        for s in [0.0, 1.0]:
            for l in [0.0, 1.0]:
                rows.append({
                    "label": "toy",
                    "case": "toy_case",
                    "point_index": point_index,
                    "s": s,
                    "l": l,
                    "stage": "toy_stage",
                    "region": "toy_region",
                    "inside_packet_live": False,
                    "rho_euler": 1.0 + point_index,
                    "p_l_unit": -0.25,
                    "j_l_unit": 0.10,
                    "alpha": 1.0,
                    "beta": 0.0,
                    "gamma_ll": 1.0,
                })
                point_index += 1
        return pd.DataFrame(rows)

    def _sector_rows(self) -> pd.DataFrame:
        return pd.DataFrame([
            {
                "label": "toy",
                "point_index": 0,
                "sector": "S0_constant_flux_string_cloud",
                "sector_rho": 0.50,
                "sector_p_l": -0.10,
                "sector_j_l": 0.05,
            },
            {
                "label": "toy",
                "point_index": 0,
                "sector": "DH_current_relaxation",
                "sector_rho": 0.25,
                "sector_p_l": -0.05,
                "sector_j_l": -0.02,
            },
            {
                "label": "toy",
                "point_index": 1,
                "sector": "S1_support_edge_shoulder_radial_trim",
                "sector_rho": 0.10,
                "sector_p_l": -0.20,
                "sector_j_l": 0.00,
            },
        ])

    def test_sector_value_points_builds_branch_contractions(self):
        sector_points = _sector_value_points(self._sector_rows())
        row = sector_points.loc[
            (sector_points["point_index"] == 0)
            & (sector_points["sector"] == "S0_constant_flux_string_cloud")
        ].iloc[0]

        self.assertAlmostEqual(float(row["sector_Tkk_plus"]), 0.30)
        self.assertAlmostEqual(float(row["sector_Tkk_minus"]), 0.50)

    def test_label_grid_totals_and_residual_are_reconstructed(self):
        points = self._points()
        sector_points = _sector_value_points(self._sector_rows())
        _grids, center_tables = _build_intermediate_label_grids(
            {"toy": points},
            sector_points,
            total_mode="intermediate_sector_sum",
        )
        table = center_tables["toy"].sort_values("point_index").reset_index(drop=True)

        self.assertAlmostEqual(float(table.loc[0, "intermediate_total::plus"]), 0.54)
        self.assertAlmostEqual(float(table.loc[0, "intermediate_total::minus"]), 0.66)
        self.assertAlmostEqual(float(table.loc[0, "total::plus"]), 0.54)
        geometric_plus = 1.0 - 0.25 - 2.0 * 0.10
        residual_plus = geometric_plus - 0.54
        self.assertAlmostEqual(
            float(table.loc[0, f"sector::{INTERMEDIATE_RESIDUAL_SECTOR}::plus"]),
            residual_plus,
        )

    def test_total_modes_select_expected_package(self):
        points = self._points()
        sector_points = _sector_value_points(self._sector_rows())
        _grids, sector_sum_tables = _build_intermediate_label_grids(
            {"toy": points},
            sector_points,
            total_mode="intermediate_sector_sum",
        )
        _grids, plus_residual_tables = _build_intermediate_label_grids(
            {"toy": points},
            sector_points,
            total_mode="intermediate_plus_residual",
        )
        _grids, geometric_tables = _build_intermediate_label_grids(
            {"toy": points},
            sector_points,
            total_mode="geometric",
        )

        sector_sum = sector_sum_tables["toy"].sort_values("point_index").reset_index(drop=True)
        plus_residual = plus_residual_tables["toy"].sort_values("point_index").reset_index(drop=True)
        geometric = geometric_tables["toy"].sort_values("point_index").reset_index(drop=True)

        self.assertAlmostEqual(float(sector_sum.loc[0, "total::plus"]), 0.54)
        self.assertAlmostEqual(
            float(plus_residual.loc[0, "total::plus"]),
            float(geometric.loc[0, "geometric_total::plus"]),
        )
        self.assertAlmostEqual(
            float(geometric.loc[0, "total::minus"]),
            float(geometric.loc[0, "geometric_total::minus"]),
        )

    def test_summary_table_uses_scoreable_windows_for_pass_fail(self):
        windows = pd.DataFrame([
            {
                "label": "toy",
                "branch": "plus",
                "smear_width_affine": 1.0,
                "scoreable_window": False,
                "violates_benchmark_floor": True,
                "margin_to_benchmark_floor": -1.0,
                "smeared_total_Tkk_hat": -2.0,
                "benchmark_floor": -1.0,
                "critical_B_for_zero_margin": 0.08,
                "benchmark_to_critical_B_ratio": 0.12,
                "center_s": 0.0,
                "center_l": 0.0,
                "center_stage": "edge",
                "center_region": "edge",
                "center_inside_packet_live": False,
                "dominant_negative_sector": "edge_sector",
                "smeared_geometric_total_Tkk_hat": -2.0,
                "smeared_intermediate_total_Tkk_hat": -2.0,
            },
            {
                "label": "toy",
                "branch": "plus",
                "smear_width_affine": 1.0,
                "scoreable_window": True,
                "violates_benchmark_floor": False,
                "margin_to_benchmark_floor": 0.5,
                "smeared_total_Tkk_hat": -0.5,
                "benchmark_floor": -1.0,
                "critical_B_for_zero_margin": 0.02,
                "benchmark_to_critical_B_ratio": 0.50,
                "center_s": 1.0,
                "center_l": 1.0,
                "center_stage": "interior",
                "center_region": "core",
                "center_inside_packet_live": False,
                "dominant_negative_sector": "",
                "smeared_geometric_total_Tkk_hat": -0.5,
                "smeared_intermediate_total_Tkk_hat": -0.5,
            },
        ])

        summary = _summary_table(windows).iloc[0]

        self.assertEqual(int(summary["all_benchmark_violations"]), 1)
        self.assertEqual(int(summary["benchmark_violations"]), 0)
        self.assertTrue(bool(summary["passes_benchmark"]))
        self.assertAlmostEqual(float(summary["worst_margin_to_floor"]), 0.5)


if __name__ == "__main__":
    unittest.main()
