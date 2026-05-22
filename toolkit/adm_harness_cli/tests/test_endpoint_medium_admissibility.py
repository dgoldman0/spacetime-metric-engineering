from __future__ import annotations

import unittest

import pandas as pd

from adm_harness.endpoint_medium_admissibility import (
    build_admissibility_point_table,
    build_endpoint_medium_admissibility_tables,
)


class EndpointMediumAdmissibilityTests(unittest.TestCase):
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

    def test_safety_factor_opens_transport_margin(self):
        frame = pd.DataFrame([
            self._row(0, s=0.0, l=0.0, rho=0.1, p_l=0.1, j_l=0.2),
            self._row(1, s=0.0, l=1.0, rho=0.1, p_l=0.1, j_l=0.2),
        ])

        minimal = build_admissibility_point_table(frame, regulator_safety_factor=1.0)
        padded = build_admissibility_point_table(frame, regulator_safety_factor=1.10)

        self.assertAlmostEqual(float(minimal["transport_margin"].min()), 0.0)
        self.assertGreater(float(padded["transport_margin"].min()), 0.0)
        self.assertEqual(int(padded["boost_superluminal_or_nan"].sum()), 0)

    def test_spread_non_live_case_has_no_hard_obstruction(self):
        outputs = build_endpoint_medium_admissibility_tables(
            self._spread_frame(),
            source_name="toy",
            regulator_safety_factors=[1.0, 1.25],
            decision_safety_factor=1.25,
        )
        decision = outputs["feasibility_decision"].iloc[0]

        self.assertTrue(bool(decision["hard_admissibility_pass"]))
        self.assertEqual(decision["admissibility_status"], "no_hard_obstruction")

    def test_live_regulator_case_is_a_hard_obstruction(self):
        outputs = build_endpoint_medium_admissibility_tables(
            self._spread_frame(live_index=3),
            source_name="toy",
            regulator_safety_factors=[1.10],
            decision_safety_factor=1.10,
        )
        decision = outputs["feasibility_decision"].iloc[0]

        self.assertFalse(bool(decision["hard_admissibility_pass"]))
        self.assertEqual(decision["admissibility_status"], "necessary_condition_watch")


if __name__ == "__main__":
    unittest.main()
