from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_support_symbol_sensitivity import (
    SensitivityScenario,
    _perturb_frame,
)


class EndpointSupportSymbolSensitivityTests(unittest.TestCase):
    def test_heat_ratio_perturbation_updates_transport_margin_and_rapidity(self):
        frame = pd.DataFrame([{
            "regulated_heat_flux_ratio": 0.90,
            "transport_margin": 0.10,
            "transport_rapidity_abs": 1.0,
            "enthalpy_buffer_density": 0.02,
            "regulated_type_i_margin": 0.03,
        }])

        out = _perturb_frame(frame, SensitivityScenario("stress", heat_ratio_delta=0.05))

        self.assertAlmostEqual(float(out["regulated_heat_flux_ratio"].iloc[0]), 0.95)
        self.assertAlmostEqual(float(out["transport_margin"].iloc[0]), 0.05)
        self.assertGreater(float(out["transport_rapidity_abs"].iloc[0]), 1.0)

    def test_regulator_scale_updates_h_reg_and_type_i_together(self):
        frame = pd.DataFrame([{
            "regulated_heat_flux_ratio": 0.90,
            "transport_margin": 0.10,
            "transport_rapidity_abs": 1.0,
            "enthalpy_buffer_density": 0.02,
            "regulated_type_i_margin": 0.03,
        }])

        out = _perturb_frame(frame, SensitivityScenario("scale", regulator_scale=0.1))

        self.assertAlmostEqual(float(out["enthalpy_buffer_density"].iloc[0]), 0.002)
        self.assertAlmostEqual(float(out["regulated_type_i_margin"].iloc[0]), 0.003)


if __name__ == "__main__":
    unittest.main()
