from __future__ import annotations

import math
import unittest

import pandas as pd

from adm_harness.endpoint_medium_covariant_audit import build_endpoint_medium_covariant_audit_tables


class EndpointMediumCovariantAuditTests(unittest.TestCase):
    def _frames(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        ledger_rows = []
        validation_rows = []
        rest_rho = 0.20
        rest_p_l = 0.05
        p_omega = 0.03
        v = 0.20
        gamma = 1.0 / math.sqrt(1.0 - v * v)
        rho_h = gamma * gamma * (rest_rho + rest_p_l * v * v)
        j_l = gamma * gamma * v * (rest_rho + rest_p_l)
        p_l = gamma * gamma * (rest_p_l + rest_rho * v * v)
        idx = 0
        for s_idx in range(5):
            for l_idx in range(5):
                s = float(s_idx)
                l = float(l_idx)
                base = {
                    "case": "toy_case",
                    "s": s,
                    "l": l,
                    "stage": "reset_decompression",
                    "region": "support_edge",
                    "inside_packet_live": False,
                    "inside_packet_geom": False,
                    "alpha": 1.0,
                    "beta": 0.0,
                    "gamma_ll": 1.0,
                    "gamma_omega": 1.0,
                    "volume_weight": 1.0,
                    "support_shell_window": 0.0,
                    "support_edge_receiver_radial_cap_window": 1.0,
                    "support_edge_receiver_angular_flange_window": 1.0,
                }
                ledger_rows.append(base)
                validation_rows.append({
                    **{key: base[key] for key in ["case", "s", "l", "stage", "region", "inside_packet_live", "volume_weight"]},
                    "label": "toy",
                    "point_index": idx,
                    "residual_zone": "reset_cap",
                    "sector": "J_endpoint_junction_layer",
                    "assignment": "reset_decompression_endpoint_junction",
                    "regulated_sector_rho": rho_h,
                    "regulated_sector_j_l": j_l,
                    "regulated_sector_p_l": p_l,
                    "regulated_sector_p_omega": p_omega,
                    "medium_energy_density": rest_rho,
                    "medium_radial_pressure": rest_p_l,
                    "medium_angular_pressure": p_omega,
                    "medium_boost_velocity_to_flux_frame": v,
                    "source_abs_density": abs(rho_h) + abs(p_l) + abs(j_l) + abs(p_omega),
                })
                idx += 1
        return pd.DataFrame(validation_rows), pd.DataFrame(ledger_rows)

    def test_covariant_lift_reprojects_constant_toy_medium(self):
        validation, ledger = self._frames()
        outputs = build_endpoint_medium_covariant_audit_tables(
            validation,
            ledger,
            projection_error_gate=1.0e-12,
            outside_exchange_gate=0.0,
            live_exchange_gate=0.0,
            top_limit=5,
        )
        decision = outputs["decision"].iloc[0]
        scope = outputs["scope_summary"].loc[outputs["scope_summary"]["scope"] == "J_total"].iloc[0]
        divergence = outputs["divergence_summary"].loc[
            outputs["divergence_summary"]["scope"] == "full_grid_exchange"
        ].iloc[0]

        self.assertTrue(bool(decision["projection_reconstruction_pass"]))
        self.assertTrue(bool(decision["boost_subluminal_pass"]))
        self.assertTrue(bool(decision["mixed_eigen_real_pass"]))
        self.assertLess(float(scope["max_projection_linf_error"]), 1.0e-12)
        self.assertLess(float(divergence["scoreable_divergence_volume"]), 1.0e-10)


if __name__ == "__main__":
    unittest.main()
