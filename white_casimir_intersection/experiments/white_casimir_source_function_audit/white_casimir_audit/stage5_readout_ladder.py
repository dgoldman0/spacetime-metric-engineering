"""Stage 5 readout-transduction ladder for the White Casimir audit."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .readout_transduction import (
    DEFAULT_STAGE3_DIR,
    DEFAULT_STAGE4_DIR,
    DEFAULT_STAGE5_BASE,
    Stage5Config,
    Stage5ProgressRecorder,
    dataclass_frame,
    git_commit,
    write_frame,
    write_json,
)
from .stage5_gates import build_gate_ledgers
from .stage5_models import (
    SCENARIO_FACTORS,
    default_readout_candidates,
    evaluate_candidate_transduction,
    load_stage5_input_context,
    select_candidates,
)
from .synthetic_discrimination import NUISANCE_NAMES, build_template_bundle


PRESETS: dict[str, dict[str, Any]] = {
    "smoke": {
        "shell_datasets_per_candidate": 12,
        "em_only_datasets_per_candidate": 12,
        "chunk_size": 12,
        "candidate_ids": (),
    },
    "focused": {
        "shell_datasets_per_candidate": 200,
        "em_only_datasets_per_candidate": 200,
        "chunk_size": 100,
        "candidate_ids": (),
    },
}


def _normalize(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(arr))
    if norm <= 0.0:
        return np.zeros_like(arr, dtype=float)
    return arr / norm


def _rms(values: np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr))) if arr.size else 0.0


def _load_stage4_templates(stage4_dir: Path, stage3_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    schedule_path = stage4_dir / "synthetic" / "schedule_matrix.parquet"
    template_path = stage4_dir / "synthetic" / "template_matrix.parquet"
    if schedule_path.exists() and template_path.exists():
        schedule = pd.read_parquet(schedule_path).sort_values("schedule_order").reset_index(drop=True)
        template_frame = pd.read_parquet(template_path)
        provenance = {"template_source": str(template_path), "schedule_source": str(schedule_path)}
    else:
        schedule, template_frame, provenance = build_template_bundle(str(stage3_dir), nuisance_model="geometry")

    pivot = template_frame.pivot(index="schedule_order", columns="template_name", values="template_value").sort_index()
    if "shell_channel" not in pivot:
        raise ValueError("Stage 5 requires a shell_channel template from Stage 4 or the fallback builder.")
    templates = {"shell_channel": _normalize(pivot["shell_channel"].to_numpy(dtype=float))}
    for nuisance_name in NUISANCE_NAMES:
        if nuisance_name in pivot:
            templates[nuisance_name] = _normalize(pivot[nuisance_name].to_numpy(dtype=float))
    return schedule, pd.DataFrame([provenance]), templates


def _mix_template(parts: tuple[tuple[float, np.ndarray], ...]) -> np.ndarray:
    values = np.zeros_like(parts[0][1], dtype=float)
    for weight, vector in parts:
        values = values + float(weight) * np.asarray(vector, dtype=float)
    return _normalize(values)


def _candidate_shell_templates(templates: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
    shell = templates["shell_channel"]

    def nuisance(name: str) -> np.ndarray:
        return templates.get(name, np.zeros_like(shell, dtype=float))

    return {
        "central_timing_reference": _mix_template(
            ((0.35, shell), (0.45, nuisance("readout_circuit_artifact")), (0.20, nuisance("waveguide_dispersion")))
        ),
        "force_gradient_mems": _mix_template(((0.86, shell), (0.10, nuisance("patch_potential")), (0.04, nuisance("vibration_alignment")))),
        "differential_pressure_cell": _mix_template(
            ((0.82, shell), (0.10, nuisance("thermal_drift")), (0.08, nuisance("vibration_alignment")))
        ),
        "high_q_cavity_shift": _mix_template(
            ((0.74, shell), (0.16, nuisance("waveguide_dispersion")), (0.10, nuisance("capacitance_shift")))
        ),
        "superconducting_resonator_shift": _mix_template(
            ((0.68, shell), (0.18, nuisance("material_response")), (0.14, nuisance("thermal_drift")))
        ),
        "material_impedance_control": _mix_template(
            ((0.50, nuisance("material_response")), (0.30, nuisance("patch_potential")), (0.20, nuisance("capacitance_shift")))
        ),
    }


def _candidate_observable_template_frame(
    schedule: pd.DataFrame,
    candidate_templates: Mapping[str, np.ndarray],
    transduction: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = transduction.groupby(["candidate_id", "scenario"], sort=True)
    for (candidate_id, scenario), group in grouped:
        values = candidate_templates[str(candidate_id)]
        for order, value in enumerate(values):
            step = str(schedule.loc[order, "schedule_step"])
            observed = group[group["schedule_order"] == order]
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "scenario": scenario,
                    "schedule_order": int(order),
                    "schedule_step": step,
                    "template_name": "candidate_shell_observable",
                    "template_value": float(value),
                    "shell_observable": float(observed["shell_observable"].iloc[0]) if not observed.empty else 0.0,
                    "shell_observable_unit": str(observed["shell_observable_unit"].iloc[0]) if not observed.empty else "",
                }
            )
    return pd.DataFrame(rows)


def _nuisance_template_frame(
    schedule: pd.DataFrame,
    candidates: list[Any],
    templates: Mapping[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        for scenario in SCENARIO_FACTORS:
            for nuisance_name in NUISANCE_NAMES:
                values = templates.get(nuisance_name)
                if values is None:
                    continue
                for order, value in enumerate(values):
                    rows.append(
                        {
                            "candidate_id": candidate.candidate_id,
                            "scenario": scenario,
                            "schedule_order": int(order),
                            "schedule_step": str(schedule.loc[order, "schedule_step"]),
                            "template_name": nuisance_name,
                            "template_role": "nuisance",
                            "template_value": float(value),
                        }
                    )
    return pd.DataFrame(rows)


def _candidate_nuisance_weights(candidate_id: str) -> dict[str, float]:
    weights = {name: 1.0 for name in NUISANCE_NAMES}
    if candidate_id == "central_timing_reference":
        weights.update({"readout_circuit_artifact": 2.5, "waveguide_dispersion": 2.0, "capacitance_shift": 1.8})
    elif candidate_id == "force_gradient_mems":
        weights.update({"patch_potential": 3.0, "vibration_alignment": 1.8, "thermal_drift": 1.4})
    elif candidate_id == "differential_pressure_cell":
        weights.update({"patch_potential": 2.5, "thermal_drift": 2.0, "vibration_alignment": 1.6})
    elif candidate_id == "high_q_cavity_shift":
        weights.update({"waveguide_dispersion": 2.5, "thermal_drift": 2.2, "capacitance_shift": 1.8})
    elif candidate_id == "superconducting_resonator_shift":
        weights.update({"material_response": 3.0, "thermal_drift": 2.4, "readout_circuit_artifact": 1.8})
    elif candidate_id == "material_impedance_control":
        weights.update({"material_response": 3.0, "patch_potential": 2.8, "capacitance_shift": 2.2, "contact_loading": 1.8})
    return weights


def _x_matrix(candidate_template: np.ndarray, nuisance_templates: Mapping[str, np.ndarray]) -> tuple[np.ndarray, list[str]]:
    names = ["candidate_shell_observable", *[name for name in NUISANCE_NAMES if name in nuisance_templates]]
    columns = [_normalize(candidate_template)]
    columns.extend(_normalize(nuisance_templates[name]) for name in names[1:])
    return np.column_stack(columns), names


def _fit_dataset(group: pd.DataFrame, x_matrix: np.ndarray, template_names: list[str], cfg: Stage5Config) -> dict[str, Any]:
    ordered = group.sort_values("schedule_order")
    y = ordered["observed_value"].to_numpy(dtype=float)
    xtx = x_matrix.T @ x_matrix
    penalty = cfg.ridge_alpha * np.eye(xtx.shape[0])
    inv = np.linalg.pinv(xtx + penalty)
    coeff = inv @ x_matrix.T @ y
    residual = y - x_matrix @ coeff
    dof = max(len(y) - len(coeff), 1)
    sigma2 = float(np.sum(residual * residual) / dof)
    shell_se = float(np.sqrt(max(inv[0, 0] * sigma2, 1.0e-300)))
    shell_z = float(coeff[0] / shell_se)
    true_shell = float(ordered["true_shell_coefficient"].iloc[0])
    family = str(ordered["simulation_family"].iloc[0])
    shell_fraction = float(coeff[0] / true_shell) if abs(true_shell) > 0.0 else 0.0
    detected = bool(coeff[0] > 0.0 and shell_z >= cfg.shell_detection_z)
    row: dict[str, Any] = {
        "candidate_id": str(ordered["candidate_id"].iloc[0]),
        "scenario": str(ordered["scenario"].iloc[0]),
        "dataset_id": int(ordered["dataset_id"].iloc[0]),
        "simulation_family": family,
        "predicted_sbr": float(ordered["predicted_sbr"].iloc[0]),
        "true_shell_coefficient": true_shell,
        "shell_coefficient": float(coeff[0]),
        "shell_standard_error": shell_se,
        "shell_z_score": shell_z,
        "shell_fraction_recovered": shell_fraction,
        "shell_recovered": bool(family == "shell_plus_background" and detected),
        "false_positive": bool(family == "em_only" and detected),
        "residual_rms": _rms(residual),
        "template_condition_number": float(np.linalg.cond(xtx + penalty)),
    }
    for index, name in enumerate(template_names):
        row[f"fit_{name}"] = float(coeff[index])
    return row


def _generate_synthetic_rows(
    candidate_id: str,
    scenario: str,
    dataset_id: int,
    family: str,
    rng: np.random.Generator,
    schedule: pd.DataFrame,
    x_matrix: np.ndarray,
    template_names: list[str],
    predicted_sbr: float,
    background_rms: float,
    cfg: Stage5Config,
) -> list[dict[str, Any]]:
    shell_template = _normalize(x_matrix[:, 0])
    nuisance_matrix = x_matrix[:, 1:]
    weights = _candidate_nuisance_weights(candidate_id)
    coefficient_scales = np.array(
        [cfg.nuisance_sigma * weights.get(name, 1.0) for name in template_names[1:]],
        dtype=float,
    )
    coefficients = rng.normal(0.0, coefficient_scales, nuisance_matrix.shape[1])
    nuisance_total = nuisance_matrix @ coefficients
    nuisance_rms = _rms(nuisance_total)
    nuisance_scale = 1.0
    if nuisance_rms > 0.0:
        nuisance_scale = max(background_rms, 1.0e-300) / nuisance_rms
        nuisance_total = nuisance_total * nuisance_scale
    shell_coefficient = float(predicted_sbr * max(background_rms, 1.0e-300)) if family == "shell_plus_background" else 0.0
    shell_component = shell_coefficient * shell_template
    noise = rng.normal(0.0, cfg.noise_sigma * max(background_rms, 1.0e-300), len(schedule))
    observed = shell_component + nuisance_total + noise

    rows: list[dict[str, Any]] = []
    for order, step in enumerate(schedule["schedule_step"].astype(str).tolist()):
        row: dict[str, Any] = {
            "candidate_id": candidate_id,
            "scenario": scenario,
            "dataset_id": int(dataset_id),
            "simulation_family": family,
            "schedule_order": int(order),
            "schedule_step": step,
            "predicted_sbr": float(predicted_sbr),
            "observed_value": float(observed[order]),
            "shell_component": float(shell_component[order]),
            "noise_component": float(noise[order]),
            "background_rms": float(background_rms),
            "true_shell_coefficient": shell_coefficient,
        }
        for nuisance_index, nuisance_name in enumerate(template_names[1:]):
            row[f"{nuisance_name}_component"] = float(
                (nuisance_matrix * coefficients[None, :] * nuisance_scale)[order, nuisance_index]
            )
        rows.append(row)
    return rows


def _template_metrics_frame(
    candidates: list[Any],
    candidate_templates: Mapping[str, np.ndarray],
    nuisance_templates: Mapping[str, np.ndarray],
    cfg: Stage5Config,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        for scenario in SCENARIO_FACTORS:
            x_matrix, names = _x_matrix(candidate_templates[candidate.candidate_id], nuisance_templates)
            shell = _normalize(x_matrix[:, 0])
            corr_values = [abs(float(shell @ _normalize(x_matrix[:, index]))) for index in range(1, x_matrix.shape[1])]
            xtx = x_matrix.T @ x_matrix + cfg.ridge_alpha * np.eye(len(names))
            rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "scenario": scenario,
                    "template_count": int(len(names)),
                    "max_abs_shell_nuisance_correlation": max(corr_values) if corr_values else 0.0,
                    "template_condition_number": float(np.linalg.cond(xtx)),
                }
            )
    return pd.DataFrame(rows)


def _run_candidate_synthetic_gate(
    candidates: list[Any],
    schedule: pd.DataFrame,
    candidate_templates: Mapping[str, np.ndarray],
    nuisance_templates: Mapping[str, np.ndarray],
    transduction: pd.DataFrame,
    cfg: Stage5Config,
    recorder: Stage5ProgressRecorder,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(cfg.base_seed)
    observation_rows: list[dict[str, Any]] = []
    fit_rows: list[dict[str, Any]] = []
    dataset_id = 0
    completed = 0
    total_groups = len(candidates) * len(SCENARIO_FACTORS)

    for candidate in candidates:
        for scenario in SCENARIO_FACTORS:
            recorder.record("candidate_started", {"label": f"{candidate.candidate_id}:{scenario}"})
            x_matrix, names = _x_matrix(candidate_templates[candidate.candidate_id], nuisance_templates)
            group = transduction[
                (transduction["candidate_id"] == candidate.candidate_id) & (transduction["scenario"] == scenario)
            ]
            predicted_sbr = float(group["predicted_sbr"].iloc[0])
            background_rms = float(group["background_observable_rms"].iloc[0])
            local_dataset_ids: list[int] = []
            generated_since_heartbeat = 0
            for family, count in (
                ("shell_plus_background", cfg.shell_datasets_per_candidate),
                ("em_only", cfg.em_only_datasets_per_candidate),
            ):
                for _ in range(count):
                    observation_rows.extend(
                        _generate_synthetic_rows(
                            candidate.candidate_id,
                            scenario,
                            dataset_id,
                            family,
                            rng,
                            schedule,
                            x_matrix,
                            names,
                            predicted_sbr,
                            background_rms,
                            cfg,
                        )
                    )
                    local_dataset_ids.append(dataset_id)
                    dataset_id += 1
                    generated_since_heartbeat += 1
                    if generated_since_heartbeat >= cfg.chunk_size:
                        recorder.record(
                            "synthetic_chunk_complete",
                            {
                                "label": f"{candidate.candidate_id}:{scenario}:{dataset_id}",
                                "datasets_generated": dataset_id,
                            },
                        )
                        generated_since_heartbeat = 0
            if generated_since_heartbeat:
                recorder.record(
                    "synthetic_chunk_complete",
                    {"label": f"{candidate.candidate_id}:{scenario}:{dataset_id}", "datasets_generated": dataset_id},
                )

            local_observations = pd.DataFrame([row for row in observation_rows if row["dataset_id"] in local_dataset_ids])
            for _, group_rows in local_observations.groupby("dataset_id", sort=True):
                fit_rows.append(_fit_dataset(group_rows, x_matrix, names, cfg))
            completed += 1
            recorder.record(
                "candidate_model_complete",
                {"label": f"{candidate.candidate_id}:{scenario}", "completed_candidate_scenarios": completed, "total": total_groups},
            )

    return pd.DataFrame(observation_rows), pd.DataFrame(fit_rows)


def _write_manifest(outdir: Path, cfg: Stage5Config, context: Any, template_provenance: pd.DataFrame) -> None:
    payload = {
        "run_id": cfg.run_id,
        "stage": "stage5_readout_transduction_ladder",
        "claim_boundary": "candidate_readout_transduction_gate_not_warp_detection_claim",
        "git_commit": git_commit(),
        "config": asdict(cfg),
        "stage5_input_context": asdict(context),
        "template_provenance": template_provenance.to_dict(orient="records"),
        "output_categories": [
            "readout_candidate_ledger",
            "stage3_shell_template",
            "candidate_observable_templates",
            "nuisance_templates",
            "synthetic_observation_ledger",
            "recovery_fit_ledger",
            "em_only_false_positive_ledger",
            "gate_ledger",
            "required_gain_ledger",
        ],
    }
    write_json(outdir / "manifest.json", payload)
    write_json(outdir / "configs" / "run_config.json", asdict(cfg))


def _schedule_recommendation(stage4_dir: Path, gate_ledger: pd.DataFrame) -> pd.DataFrame:
    source = stage4_dir / "synthetic" / "schedule_recommendation.csv"
    if source.exists():
        frame = pd.read_csv(source)
        frame.insert(0, "recommendation_source", "stage4_schedule_basis")
        return frame
    if gate_ledger.empty:
        return pd.DataFrame([{"recommendation_source": "stage5_gate_basis", "recommended": False}])
    best = gate_ledger.sort_values(["predicted_sbr", "em_only_false_positive_rate"], ascending=[False, True]).iloc[0]
    return pd.DataFrame(
        [
            {
                "recommendation_source": "stage5_gate_basis",
                "recommended": True,
                "candidate_id": best["candidate_id"],
                "scenario": best["scenario"],
                "gate_status": best["gate_status"],
                "predicted_sbr": best["predicted_sbr"],
            }
        ]
    )


def run_stage5_readout_ladder(outdir: Path, cfg: Stage5Config) -> dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    for subdir in ("configs", "candidates", "templates", "synthetic", "gates", "schedules", "reports"):
        (outdir / subdir).mkdir(parents=True, exist_ok=True)

    recorder = Stage5ProgressRecorder(outdir)
    recorder.record("run_start", {"label": cfg.run_id, "preset": cfg.preset})

    context = load_stage5_input_context(cfg.source_stage3_dir, cfg.source_stage4_dir)
    schedule, template_provenance, templates = _load_stage4_templates(Path(cfg.source_stage4_dir), Path(cfg.source_stage3_dir))
    nuisance_templates = {name: value for name, value in templates.items() if name != "shell_channel"}
    candidates = select_candidates(cfg.candidate_ids)
    candidate_templates = _candidate_shell_templates(templates)
    candidate_templates = {candidate.candidate_id: candidate_templates[candidate.candidate_id] for candidate in candidates}
    _write_manifest(outdir, cfg, context, template_provenance)
    recorder.record(
        "inputs_loaded",
        {
            "label": "stage3_stage4",
            "candidate_count": len(candidates),
            "stage4_required_sbr": context.stage4_required_sbr,
        },
    )

    write_frame(outdir / "candidates" / "readout_candidates.parquet", dataclass_frame(candidates))
    write_frame(outdir / "candidates" / "readout_candidates.csv", dataclass_frame(candidates))
    write_frame(outdir / "schedules" / "schedule_matrix.parquet", schedule)
    write_frame(
        outdir / "templates" / "stage3_shell_template.parquet",
        pd.DataFrame(
            {
                "schedule_order": schedule["schedule_order"],
                "schedule_step": schedule["schedule_step"],
                "template_name": "stage3_shell_channel",
                "template_value": templates["shell_channel"],
            }
        ),
    )
    write_json(
        outdir / "templates" / "stage4_recovery_gate.json",
        {
            "source_stage4_dir": cfg.source_stage4_dir,
            "required_signal_to_background_ratio": context.stage4_required_sbr,
            "false_positive_rate": context.stage4_false_positive_rate,
            "max_abs_shell_nuisance_correlation": context.stage4_max_shell_nuisance_correlation,
            "recovery_fraction_at_max_sbr": context.stage4_recovery_fraction_at_max_sbr,
        },
    )

    transduction_rows = []
    for candidate in candidates:
        transduction_rows.extend(evaluate_candidate_transduction(candidate, context, schedule, candidate_templates))
    transduction = dataclass_frame(transduction_rows)
    recorder.record("candidate_model_complete", {"label": "analytic_transduction", "rows": len(transduction)})
    template_metrics = _template_metrics_frame(candidates, candidate_templates, nuisance_templates, cfg)
    candidate_template_frame = _candidate_observable_template_frame(schedule, candidate_templates, transduction)
    nuisance_template_rows = _nuisance_template_frame(schedule, candidates, nuisance_templates)
    write_frame(outdir / "templates" / "candidate_observable_templates.parquet", candidate_template_frame)
    write_frame(outdir / "templates" / "nuisance_templates.parquet", nuisance_template_rows)
    write_frame(outdir / "templates" / "candidate_template_metrics.csv", template_metrics)

    observations, recovery = _run_candidate_synthetic_gate(
        candidates,
        schedule,
        candidate_templates,
        nuisance_templates,
        transduction,
        cfg,
        recorder,
    )
    false_positive = recovery[recovery["simulation_family"] == "em_only"].copy()
    write_frame(outdir / "synthetic" / "synthetic_observations.parquet", observations)
    write_frame(outdir / "synthetic" / "recovery_ledger.parquet", recovery)
    write_frame(outdir / "synthetic" / "false_positive_ledger.parquet", false_positive)

    gate_ledger, required_gain_ledger = build_gate_ledgers(candidates, transduction, recovery, template_metrics, context, cfg)
    write_frame(outdir / "gates" / "gate_ledger.parquet", gate_ledger)
    write_frame(outdir / "gates" / "gate_summary.csv", gate_ledger)
    write_frame(outdir / "gates" / "required_gain_ledger.parquet", required_gain_ledger)
    schedule_recommendation = _schedule_recommendation(Path(cfg.source_stage4_dir), gate_ledger)
    write_frame(outdir / "schedules" / "schedule_recommendation.csv", schedule_recommendation)
    recorder.record("candidate_gate_complete", {"label": "gate_ledger", "rows": len(gate_ledger)})

    status_counts = gate_ledger["gate_status"].value_counts().to_dict() if not gate_ledger.empty else {}
    summary = {
        "run_id": cfg.run_id,
        "outdir": str(outdir),
        "stage": "stage5_readout_transduction_ladder",
        "claim_boundary": "candidate_readout_transduction_gate_not_warp_detection_claim",
        "source_stage3_dir": cfg.source_stage3_dir,
        "source_stage4_dir": cfg.source_stage4_dir,
        "candidate_count": int(len(candidates)),
        "candidate_scenario_count": int(len(gate_ledger)),
        "stage4_required_sbr": context.stage4_required_sbr,
        "n_observation_rows": int(len(observations)),
        "n_fit_rows": int(len(recovery)),
        "gate_status_counts": {str(key): int(value) for key, value in status_counts.items()},
        "max_predicted_sbr": float(gate_ledger["predicted_sbr"].max()) if not gate_ledger.empty else 0.0,
        "min_required_gain_to_stage4_gate": float(gate_ledger["required_gain_to_stage4_gate"].min())
        if not gate_ledger.empty
        else None,
    }
    write_json(outdir / "summary.json", summary)
    recorder.record("run_complete", {"label": cfg.run_id, **summary})
    return summary


def config_from_args(args: argparse.Namespace) -> Stage5Config:
    preset_name = args.preset_flag or args.preset or "smoke"
    preset = PRESETS[preset_name].copy()
    if args.shell_datasets_per_candidate is not None:
        preset["shell_datasets_per_candidate"] = args.shell_datasets_per_candidate
    if args.em_only_datasets_per_candidate is not None:
        preset["em_only_datasets_per_candidate"] = args.em_only_datasets_per_candidate
    if args.chunk_size is not None:
        preset["chunk_size"] = args.chunk_size
    candidate_ids = tuple(args.candidate_id) if args.candidate_id else tuple(preset["candidate_ids"])
    run_id = args.run_id or f"stage5_{preset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    outdir = args.outdir or (DEFAULT_STAGE5_BASE / run_id)
    return Stage5Config(
        preset=preset_name,
        run_id=run_id,
        source_stage3_dir=str(args.source_stage3_dir),
        source_stage4_dir=str(args.source_stage4_dir),
        outdir=str(outdir),
        base_seed=int(args.base_seed),
        shell_datasets_per_candidate=int(preset["shell_datasets_per_candidate"]),
        em_only_datasets_per_candidate=int(preset["em_only_datasets_per_candidate"]),
        chunk_size=int(preset["chunk_size"]),
        heartbeat_interval_s=float(args.heartbeat_interval_s),
        noise_sigma=float(args.noise_sigma),
        nuisance_sigma=float(args.nuisance_sigma),
        ridge_alpha=float(args.ridge_alpha),
        shell_detection_z=float(args.shell_detection_z),
        recovery_threshold=float(args.recovery_threshold),
        false_positive_threshold=float(args.false_positive_threshold),
        preferred_correlation_threshold=float(args.preferred_correlation_threshold),
        candidate_ids=candidate_ids,
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Stage 5 White Casimir readout-transduction ladder.")
    parser.add_argument("preset", nargs="?", choices=tuple(PRESETS), default=None)
    parser.add_argument("--preset", dest="preset_flag", choices=tuple(PRESETS), default=None)
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--source-stage3-dir", type=Path, default=DEFAULT_STAGE3_DIR)
    parser.add_argument("--source-stage4-dir", type=Path, default=DEFAULT_STAGE4_DIR)
    parser.add_argument("--candidate-id", action="append", default=None)
    parser.add_argument("--shell-datasets-per-candidate", type=int, default=None)
    parser.add_argument("--em-only-datasets-per-candidate", type=int, default=None)
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--base-seed", type=int, default=51)
    parser.add_argument("--heartbeat-interval-s", type=float, default=10.0)
    parser.add_argument("--noise-sigma", type=float, default=0.05)
    parser.add_argument("--nuisance-sigma", type=float, default=1.0)
    parser.add_argument("--ridge-alpha", type=float, default=1.0e-3)
    parser.add_argument("--shell-detection-z", type=float, default=2.0)
    parser.add_argument("--recovery-threshold", type=float, default=0.80)
    parser.add_argument("--false-positive-threshold", type=float, default=0.05)
    parser.add_argument("--preferred-correlation-threshold", type=float, default=0.85)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    cfg = config_from_args(args)
    summary = run_stage5_readout_ladder(Path(cfg.outdir).resolve(), cfg)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
