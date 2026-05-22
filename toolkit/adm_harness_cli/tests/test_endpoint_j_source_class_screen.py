from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_j_source_class_screen import build_source_class_screen_tables, classify_endpoint_source_frame


class EndpointJSourceClassScreenTests(unittest.TestCase):
    def _row(self, idx: int, *, rho: float, p_l: float, j_l: float, p_omega: float) -> dict[str, object]:
        return {
            "label": "toy",
            "case": "toy_case",
            "point_index": idx,
            "s": float(idx),
            "l": 0.0,
            "inside_packet_live": False,
            "volume_weight": 1.0,
            "sector": "J_endpoint_junction_layer",
            "assignment": "reset_decompression_endpoint_junction",
            "sector_rho": rho,
            "sector_p_l": p_l,
            "sector_j_l": j_l,
            "sector_p_omega": p_omega,
        }

    def test_classifies_type_i_and_type_iv_rows(self):
        frame = pd.DataFrame([
            self._row(0, rho=1.0, p_l=1.0, j_l=0.2, p_omega=0.1),
            self._row(1, rho=0.1, p_l=0.1, j_l=0.2, p_omega=0.1),
        ])

        classified = classify_endpoint_source_frame(frame)

        self.assertEqual(classified.loc[0, "stress_algebraic_type"], "type_i_boost_diagonalizable")
        self.assertEqual(classified.loc[1, "stress_algebraic_type"], "type_iv_flux_dominant")
        self.assertAlmostEqual(float(classified.loc[1, "minimal_type_i_regulator"]), 0.2)

    def test_regulated_anisotropic_medium_is_recommended_for_small_regulator(self):
        frame = pd.DataFrame([
            self._row(0, rho=1.0, p_l=1.0, j_l=0.1, p_omega=0.2),
            self._row(1, rho=0.1, p_l=0.1, j_l=0.105, p_omega=0.2),
        ])

        outputs = build_source_class_screen_tables(
            frame,
            source_name="toy",
            regulator_source_ratio_gate=0.10,
            type_iv_burden_gate=0.02,
        )
        decision = outputs["feasibility_decision"].iloc[0]

        self.assertFalse(bool(decision["ordinary_type_i_passes"]))
        self.assertTrue(bool(decision["regulated_anisotropic_passes"]))
        self.assertEqual(decision["recommended_model_class"], "regulated_anisotropic_heat_flux_medium")


if __name__ == "__main__":
    unittest.main()
