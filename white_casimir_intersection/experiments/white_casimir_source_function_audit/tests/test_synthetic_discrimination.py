import json

import pandas as pd

from white_casimir_audit.synthetic_discrimination import (
    DiscriminationConfig,
    build_template_bundle,
    run_synthetic_discrimination,
)


def test_template_bundle_has_shell_and_nuisance_columns():
    schedule, template_frame, provenance = build_template_bundle()
    assert len(schedule) >= 10
    assert provenance["shell_template_source"] == "default_stage3_focused_summary_values"
    names = set(template_frame["template_name"])
    assert "shell_channel" in names
    assert "patch_potential" in names
    assert "readout_circuit_artifact" in names


def test_tiny_synthetic_discrimination_writes_parquet_and_heartbeat(tmp_path):
    cfg = DiscriminationConfig(
        preset="test",
        run_id="stage4_tiny_test",
        shell_datasets_per_sbr=3,
        em_only_datasets_per_sbr=3,
        sbr_values=(0.1, 0.5),
        noise_sigma=0.05,
        nuisance_sigma=1.0,
        ridge_alpha=1.0e-3,
        shell_detection_z=1.0,
        base_seed=11,
        chunk_size=2,
        source_stage3_dir=None,
    )
    summary = run_synthetic_discrimination(tmp_path / "stage4", cfg)
    assert summary["run_id"] == "stage4_tiny_test"
    assert summary["claim_boundary"] == "synthetic_identifiability_proxy_not_physical_detection_claim"
    assert summary["n_observation_rows"] > summary["n_fit_rows"]

    progress_events = [
        json.loads(line)["event"]
        for line in (tmp_path / "stage4" / "progress.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert "synthetic_chunk_complete" in progress_events
    assert "fit_chunk_complete" in progress_events
    assert "schedule_recommendation_complete" in progress_events

    observations = pd.read_parquet(tmp_path / "stage4" / "synthetic" / "synthetic_observations.parquet")
    recovery = pd.read_parquet(tmp_path / "stage4" / "synthetic" / "recovery_ledger.parquet")
    false_positive = pd.read_parquet(tmp_path / "stage4" / "synthetic" / "false_positive_ledger.parquet")
    recommendation = pd.read_csv(tmp_path / "stage4" / "synthetic" / "schedule_recommendation.csv")
    assert not observations.empty
    assert not recovery.empty
    assert not false_positive.empty
    assert bool(recommendation["recommended"].any())
