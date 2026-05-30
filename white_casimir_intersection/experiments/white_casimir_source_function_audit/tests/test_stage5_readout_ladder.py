import json
import math

import pandas as pd

from white_casimir_audit.readout_transduction import Stage5Config
from white_casimir_audit.stage5_readout_ladder import run_stage5_readout_ladder


def _tiny_cfg(tmp_path):
    stage3 = tmp_path / "missing_stage3"
    stage4 = tmp_path / "missing_stage4"
    return Stage5Config(
        preset="test",
        run_id="stage5_tiny_test",
        source_stage3_dir=str(stage3),
        source_stage4_dir=str(stage4),
        outdir=str(tmp_path / "stage5"),
        base_seed=7,
        shell_datasets_per_candidate=2,
        em_only_datasets_per_candidate=2,
        chunk_size=4,
        heartbeat_interval_s=1.0,
        shell_detection_z=1.0,
    )


def test_stage5_smoke_writes_required_outputs(tmp_path):
    cfg = _tiny_cfg(tmp_path)
    summary = run_stage5_readout_ladder(tmp_path / "stage5", cfg)
    assert summary["run_id"] == "stage5_tiny_test"
    assert summary["candidate_count"] == 6
    assert summary["candidate_scenario_count"] == 18

    required = [
        "manifest.json",
        "summary.json",
        "progress.jsonl",
        "latest_status.json",
        "configs/run_config.json",
        "candidates/readout_candidates.parquet",
        "candidates/readout_candidates.csv",
        "templates/stage3_shell_template.parquet",
        "templates/stage4_recovery_gate.json",
        "templates/candidate_observable_templates.parquet",
        "templates/nuisance_templates.parquet",
        "synthetic/synthetic_observations.parquet",
        "synthetic/recovery_ledger.parquet",
        "synthetic/false_positive_ledger.parquet",
        "gates/gate_ledger.parquet",
        "gates/gate_summary.csv",
        "gates/required_gain_ledger.parquet",
        "schedules/schedule_matrix.parquet",
        "schedules/schedule_recommendation.csv",
        "reports/stage5_readout_ladder_readout.md",
    ]
    for relative in required:
        assert (tmp_path / "stage5" / relative).exists()

    events = [
        json.loads(line)["event"]
        for line in (tmp_path / "stage5" / "progress.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert "inputs_loaded" in events
    assert "synthetic_chunk_complete" in events
    assert "candidate_gate_complete" in events


def test_stage5_candidate_claim_classes_and_gates_are_preserved(tmp_path):
    cfg = _tiny_cfg(tmp_path)
    run_stage5_readout_ladder(tmp_path / "stage5", cfg)
    candidates = pd.read_parquet(tmp_path / "stage5" / "candidates" / "readout_candidates.parquet")
    gates = pd.read_parquet(tmp_path / "stage5" / "gates" / "gate_ledger.parquet")
    false_positive = pd.read_parquet(tmp_path / "stage5" / "synthetic" / "false_positive_ledger.parquet")

    assert {"metric_proxy", "casimir_boundary", "material_response"}.issubset(set(candidates["claim_class"]))
    assert set(false_positive["candidate_id"]) == set(candidates["candidate_id"])

    central = gates[gates["candidate_id"] == "central_timing_reference"]
    assert not central.empty
    assert set(central["gate_status"]) == {"closed_amplitude"}
    assert central["required_gain_to_stage4_gate"].map(math.isfinite).all()

    material = gates[gates["candidate_id"] == "material_impedance_control"]
    assert not material.empty
    assert set(material["gate_status"]) == {"background_calibration_only"}


def test_stage5_gate_summary_matches_gate_ledger(tmp_path):
    cfg = _tiny_cfg(tmp_path)
    run_stage5_readout_ladder(tmp_path / "stage5", cfg)
    gate_ledger = pd.read_parquet(tmp_path / "stage5" / "gates" / "gate_ledger.parquet")
    gate_summary = pd.read_csv(tmp_path / "stage5" / "gates" / "gate_summary.csv")
    required_gain = pd.read_parquet(tmp_path / "stage5" / "gates" / "required_gain_ledger.parquet")
    assert len(gate_summary) == len(gate_ledger)
    assert len(required_gain) == len(gate_ledger)
    assert "recommended_next_action" in gate_summary


def test_stage5_physical_priority_mode_writes_backend_sweep(tmp_path):
    cfg = _tiny_cfg(tmp_path)
    cfg = Stage5Config(
        **{
            **cfg.__dict__,
            "backend_mode": "physical",
            "candidate_ids": (
                "central_timing_reference",
                "differential_pressure_cell",
                "high_q_cavity_shift",
                "superconducting_resonator_shift",
                "material_impedance_control",
            ),
        }
    )
    summary = run_stage5_readout_ladder(tmp_path / "stage5_physical", cfg)
    assert summary["backend_mode"] == "physical"
    assert summary["candidate_count"] == 5
    assert summary["physical_backend_rows"] == 27

    backend = pd.read_parquet(tmp_path / "stage5_physical" / "backends" / "physical_backend_sweep.parquet")
    gates = pd.read_parquet(tmp_path / "stage5_physical" / "gates" / "gate_ledger.parquet")
    assert set(backend["backend"]) == {
        "differential_pressure_physical",
        "high_q_cavity_physical",
        "superconducting_resonator_physical",
    }
    assert {"closed_physical_scale", "closed_nuisance_degeneracy", "candidate_survives_for_experiment"} & set(
        gates["gate_status"]
    )
