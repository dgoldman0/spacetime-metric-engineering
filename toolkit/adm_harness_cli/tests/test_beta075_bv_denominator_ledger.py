from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_bv_denominator_ledger import (
    BVDenominatorLedgerInputs,
    BVDenominatorLedgerSpec,
    build_bv_denominator_ledger,
    write_bv_denominator_ledger_outputs,
)


class TestBeta075BVDenominatorLedger(unittest.TestCase):
    def _write_medium(self, path: Path, source_name: str) -> None:
        pd.DataFrame([
            {
                "source_name": source_name,
                "point_index": 1,
                "s": 0.1,
                "l": 0.2,
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
                "inside_packet_live": False,
                "regulator_safety_factor": 1.10,
                "regulator_active": True,
                "regulated_heat_flux_ratio": 0.99,
                "transport_margin": 0.01,
                "regulated_abs_boost_velocity": 0.9,
                "regulated_type_i_margin": 1.0e-6,
                "regulator_to_local_source_abs_density": 0.4,
                "rest_frame_angular_inertia_density": -0.1,
                "boost_superluminal_or_nan": False,
                "regulated_stress_algebraic_type": "type_i_boost_diagonalizable",
                "regulator_gradient_cost_density": 0.02,
            },
            {
                "source_name": source_name,
                "point_index": 2,
                "s": 0.3,
                "l": 0.4,
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
                "inside_packet_live": False,
                "regulator_safety_factor": 1.00,
                "regulator_active": False,
                "regulated_heat_flux_ratio": 1.0,
                "transport_margin": 0.0,
                "regulated_abs_boost_velocity": 1.0,
                "regulated_type_i_margin": 0.0,
                "regulator_to_local_source_abs_density": 0.0,
                "rest_frame_angular_inertia_density": 0.1,
                "boost_superluminal_or_nan": False,
                "regulated_stress_algebraic_type": "type_i_boost_diagonalizable",
                "regulator_gradient_cost_density": 0.0,
            },
        ]).to_csv(path, index=False)

    def test_builds_parquet_outputs_and_counts_only_active_symbol_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            baseline = tmp / "baseline_medium.csv"
            dense = tmp / "dense_medium.csv"
            self._write_medium(baseline, "baseline")
            self._write_medium(dense, "dense")

            symbol = tmp / "symbol.csv"
            pd.DataFrame([
                {
                    "label": "sealed_dense_v5",
                    "role": "reference_dense",
                    "assignment": "support_edge_endpoint_junction",
                    "stage": "entry_precatch",
                    "region": "support_edge",
                    "s": 0.1,
                    "l": 0.2,
                    "medium_source_active": True,
                    "hard_formal_symbol_pass": True,
                    "no_live_support_pass": True,
                    "relative_cone_margin": 1.0e-4,
                    "transport_margin": 0.01,
                    "transport_rapidity_abs": 1.2,
                    "operator_local_P_error": 0.6,
                    "operator_local_F_error": 0.4,
                    "operator_support_sound": 0.3,
                },
                {
                    "label": "sealed_dense_v5",
                    "role": "reference_dense",
                    "assignment": "none",
                    "stage": "outer",
                    "region": "far_exterior",
                    "s": 0.0,
                    "l": 0.0,
                    "medium_source_active": False,
                    "hard_formal_symbol_pass": False,
                    "no_live_support_pass": True,
                    "relative_cone_margin": 1.0,
                    "transport_margin": 1.0,
                    "transport_rapidity_abs": 0.0,
                    "operator_local_P_error": 0.0,
                    "operator_local_F_error": 0.0,
                    "operator_support_sound": 0.0,
                },
            ]).to_csv(symbol, index=False)

            energy = tmp / "energy.csv"
            pd.DataFrame([{
                "label": "sealed_dense_v5",
                "role": "reference_dense",
                "assignment": "support_edge_endpoint_junction",
                "stage": "entry_precatch",
                "region": "support_edge",
                "hard_energy_pass": True,
                "energy_flux_margin": 1.0e-4,
                "energy_work_constant": 2.0,
                "support_work_ratio": 0.5,
                "support_total_closure_ratio": 0.54,
                "local_exchange_shape": 0.6,
                "transport_margin": 0.01,
                "transport_rapidity_abs": 1.2,
            }]).to_csv(energy, index=False)

            anec = tmp / "anec.parquet"
            pd.DataFrame([{
                "branch": "plus",
                "center_stage": "entry_precatch",
                "center_region": "support_edge",
                "center_s": 0.1,
                "center_l": 0.2,
                "center_inside_packet_live": False,
                "anec_total_integral": -0.01,
                "anec_positive_part": 0.0,
                "anec_negative_part": 0.01,
                "trace_lambda_span": 10.0,
                "dominant_negative_sector": "sector_closure_residual",
                "sector::sector_closure_residual::negative_part": 0.01,
                "sector::live_handoff_trim::negative_part": 0.0,
                "sector::infrastructure_angular_capacity::negative_part": 0.0,
                "touches_s_lower": False,
                "touches_s_upper": False,
                "touches_l_lower": False,
                "touches_l_upper": False,
            }]).to_parquet(anec, index=False)

            inputs = BVDenominatorLedgerInputs(
                baseline_admissibility=baseline,
                dense_admissibility=dense,
                cross_surface_point_symbol=symbol,
                energy_point=energy,
                geometric_anec_traces=anec,
                residual_trimmed_anec_traces=anec,
            )
            outputs, metadata = build_bv_denominator_ledger(
                inputs,
                spec=BVDenominatorLedgerSpec(max_workers=2, top_rows_per_metric=4),
            )
            self.assertEqual(metadata["workers"], 2)
            symbol_gate = outputs["gate_summary"][
                outputs["gate_summary"]["table"].eq("source_family_point_symbol")
            ].iloc[0]
            self.assertEqual(int(symbol_gate["active_rows"]), 1)
            self.assertEqual(int(symbol_gate["active_hard_symbol_failures"]), 0)

            paths = write_bv_denominator_ledger_outputs(tmp / "out", outputs, metadata)
            for key, path in paths.items():
                if key == "manifest":
                    self.assertEqual(path.suffix, ".json")
                else:
                    self.assertEqual(path.suffix, ".parquet")


if __name__ == "__main__":
    unittest.main()
