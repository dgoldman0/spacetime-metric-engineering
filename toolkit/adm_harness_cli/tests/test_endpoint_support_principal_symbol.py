from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_support_principal_symbol import (
    PrincipalSymbolSpec,
    build_principal_symbol_tables,
)


class EndpointSupportPrincipalSymbolTests(unittest.TestCase):
    def _point(self, *, heat_ratio: float = 0.80, h_reg: float = 0.05, live: bool = False) -> pd.DataFrame:
        return pd.DataFrame([{
            "case": "toy",
            "s": 0.0,
            "l": 0.0,
            "assignment": "support_edge_endpoint_junction",
            "stage": "release_shift_fade",
            "region": "support_edge",
            "alpha": 1.0,
            "beta": 0.0,
            "gamma_ll": 1.0,
            "medium_source_active": True,
            "covariant_divergence_live": live,
            "regulated_heat_flux_ratio": heat_ratio,
            "transport_margin": 1.0 - heat_ratio,
            "transport_rapidity_abs": 1.0,
            "enthalpy_buffer_density": h_reg,
            "regulated_type_i_margin": h_reg,
            "source_abs_density": 0.20,
            "target_abs_PF_density": 0.10,
            "target_radial_F": 0.03,
            "fit_F": 0.03,
            "fit_abs_PF_density": 0.08,
            "fit_error_abs_PF_density": 0.01,
        }])

    def test_symbol_passes_for_buffered_subluminal_toy_medium(self):
        outputs = build_principal_symbol_tables(
            self._point(),
            label="toy",
            mesh="toy",
            kind="reference_24x14",
            spec=PrincipalSymbolSpec(speed_margin_watch=0.001),
        )

        decision = outputs["run_summary"].iloc[0]
        point = outputs["point_symbol"].iloc[0]

        self.assertEqual(str(decision["symbol_status"]), "pass")
        self.assertTrue(bool(point["real_eigen_pass"]))
        self.assertTrue(bool(point["complete_eigenbasis_pass"]))
        self.assertTrue(bool(point["inside_service_cone_pass"]))

    def test_near_luminal_heat_current_is_watch_not_fail(self):
        outputs = build_principal_symbol_tables(
            self._point(heat_ratio=0.998, h_reg=0.01),
            label="toy",
            mesh="toy",
            kind="reference_24x14",
        )

        decision = outputs["run_summary"].iloc[0]
        point = outputs["point_symbol"].iloc[0]

        self.assertEqual(str(decision["symbol_status"]), "watch")
        self.assertTrue(bool(point["hard_symbol_pass"]))
        self.assertLess(float(point["relative_cone_margin"]), 0.005)

    def test_negative_regulator_margin_fails(self):
        outputs = build_principal_symbol_tables(
            self._point(heat_ratio=0.80, h_reg=-0.01),
            label="toy",
            mesh="toy",
            kind="reference_24x14",
        )

        decision = outputs["run_summary"].iloc[0]
        point = outputs["point_symbol"].iloc[0]

        self.assertEqual(str(decision["symbol_status"]), "fail")
        self.assertFalse(bool(point["positive_margin_pass"]))


if __name__ == "__main__":
    unittest.main()
