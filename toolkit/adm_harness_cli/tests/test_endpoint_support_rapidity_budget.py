from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_support_principal_symbol import PrincipalSymbolSpec
from adm_harness.endpoint_support_rapidity_budget import (
    RapidityBudgetSpec,
    _max_admissible_delta_psi,
    _source_delta_psi_for_heat_delta,
    _symbol_at_delta_psi,
)


def _sample_row(ratio: float = 0.92) -> pd.Series:
    return pd.Series({
        "case": "unit",
        "s": 0.0,
        "l": 0.0,
        "assignment": "unit",
        "stage": "unit",
        "region": "unit",
        "medium_source_active": True,
        "covariant_divergence_live": False,
        "alpha": 1.0,
        "beta": 0.0,
        "gamma_ll": 1.0,
        "target_radial_F": 1.0,
        "fit_F": 1.0,
        "fit_abs_PF_density": 0.0,
        "source_abs_density": 0.0,
        "target_abs_PF_density": 0.01,
        "fit_error_abs_PF_density": 0.0,
        "enthalpy_buffer_density": 0.1,
        "regulated_type_i_margin": 0.1,
        "regulated_heat_flux_ratio": ratio,
        "transport_margin": 1.0 - ratio,
        "transport_rapidity_abs": 0.0,
    })


class EndpointSupportRapidityBudgetTests(unittest.TestCase):
    def test_source_delta_psi_grows_near_transport_boundary(self):
        loose = _source_delta_psi_for_heat_delta(0.5, 1.0e-4)
        tight = _source_delta_psi_for_heat_delta(0.999, 1.0e-4)

        self.assertGreater(tight, loose)

    def test_max_delta_psi_reaches_cone_gate(self):
        symbol_spec = PrincipalSymbolSpec(heat_sound_cap=0.0, angular_sound_cap=0.0, support_sound_cap=0.0)
        budget_spec = RapidityBudgetSpec(speed_margin_gate=symbol_spec.speed_margin_gate)
        row = _sample_row(0.92)

        budget, gate_symbol = _max_admissible_delta_psi(row, symbol_spec, budget_spec)
        after_symbol = _symbol_at_delta_psi(row, budget + 1.0e-5, symbol_spec)

        self.assertGreater(budget, 0.0)
        self.assertGreaterEqual(float(gate_symbol["relative_cone_margin"]), symbol_spec.speed_margin_gate)
        self.assertLess(float(after_symbol["relative_cone_margin"]), 2.0e-5)


if __name__ == "__main__":
    unittest.main()
