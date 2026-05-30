import json

import pandas as pd

from white_casimir_audit.alcubierre_target import (
    equivalent_speed_parameter,
    target_energy_density_J_m3,
)
from white_casimir_audit.em_proxy import estimate_em_competitors
from white_casimir_audit.linearized_metric import estimate_timing_bound
from white_casimir_audit.tensor_scale_harness import HarnessConfig, run_tensor_scale_harness


def test_alcubierre_scale_increases_with_speed_and_inverts():
    slow = abs(target_energy_density_J_m3(1.0e-9, 1.0))
    fast = abs(target_energy_density_J_m3(1.0e-6, 1.0))
    assert fast > slow
    assert equivalent_speed_parameter(slow, 1.0) > 0.0


def test_material_and_metric_competitors_emit_labeled_rows():
    metric = estimate_timing_bound(1.0e-20, 8.0, coupling_fraction=0.5)
    assert metric["estimate_status"] == "linearized_metric_scale_bound_not_transport_prediction"
    rows = estimate_em_competitors(
        casimir_energy_J=1.0e-20,
        sphere_diameter_um=1.0,
        cylinder_diameter_um=4.0,
        cylinder_length_um=8.0,
        wall_thickness_um=0.2,
    )
    assert rows
    assert rows[0]["open_bore_vs_conductor_distinction"] == "accounting_mask_only_until_modeled_bore_run"


def test_tiny_tensor_scale_harness_writes_progress_and_tables(tmp_path):
    cfg = HarnessConfig(
        preset="test",
        run_id="tiny_test",
        grid_n=7,
        grid_extent_um=2.5,
        loop_blocks=1,
        loops_per_block=4,
        points_per_loop=32,
        workers=1,
        chunk_size=4,
        base_seed=3,
        wall_thicknesses_um=(0.2,),
        scale_windows=("mid_0p75_1p50",),
        calibration_gaps_um=(0.75, 1.0),
        material_factors=(1.0,),
    )
    summary = run_tensor_scale_harness(tmp_path / "stage3", cfg)
    assert summary["run_id"] == "tiny_test"
    assert (tmp_path / "stage3" / "progress.jsonl").exists()
    assert (tmp_path / "stage3" / "latest_status.json").exists()
    assert (tmp_path / "stage3" / "reports" / "second_question_machine_readout.md").exists()
    progress_events = [
        json.loads(line)["event"]
        for line in (tmp_path / "stage3" / "progress.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert "tensor_task_baseline_complete" in progress_events
    assert "tensor_task_parameter_complete" in progress_events
    assert "calibration_block_complete" in progress_events
    assert "tensor_block_complete" in progress_events
    calibration = pd.read_csv(tmp_path / "stage3" / "calibration" / "calibration_summary.csv")
    stress = pd.read_csv(tmp_path / "stage3" / "tensor" / "bootstrap_summary.csv")
    assert not calibration.empty
    assert not stress.empty
