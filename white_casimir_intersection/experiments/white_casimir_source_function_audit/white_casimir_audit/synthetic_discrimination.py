"""Synthetic EM-background discrimination harness for the White Casimir audit.

This Stage 4 harness treats the Stage 3 geometry derivatives as a shell-channel
template and asks whether that template can be recovered from synthetic readout
data after ordinary EM/material/readout nuisance templates are mixed in. The
output is an identifiability and schedule-design proxy, not a physical detection
claim.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd


DEFAULT_EXTERNAL_BASE = Path("/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_synthetic_discrimination")

SCHEDULE_VARIABLES = (
    "cylinder_inner_radius",
    "sphere_diameter",
    "sphere_radial_offset",
    "sphere_axial_offset",
    "cylinder_length",
    "readout_accounting_radius",
    "wall_thickness",
)

NUISANCE_NAMES = (
    "capacitance_shift",
    "patch_potential",
    "contact_loading",
    "material_response",
    "thermal_drift",
    "vibration_alignment",
    "waveguide_dispersion",
    "readout_circuit_artifact",
)

DEFAULT_SCHEDULE_ROWS: tuple[tuple[str, Mapping[str, float]], ...] = (
    ("cylinder_radius", {"cylinder_inner_radius": 1.0}),
    ("sphere_diameter", {"sphere_diameter": 1.0}),
    ("radial_offset", {"sphere_radial_offset": 1.0}),
    ("axial_offset", {"sphere_axial_offset": 1.0}),
    ("cylinder_length", {"cylinder_length": 1.0}),
    ("readout_radius", {"readout_accounting_radius": 1.0}),
    ("wall_thickness", {"wall_thickness": 1.0}),
    ("shell_gap_contrast", {"cylinder_inner_radius": 1.0, "sphere_diameter": -0.70}),
    ("shell_size_contrast", {"cylinder_inner_radius": 0.45, "sphere_diameter": -1.0, "wall_thickness": 0.25}),
    ("readout_isolation", {"readout_accounting_radius": 1.0, "cylinder_length": 0.55}),
    ("offset_balance", {"sphere_radial_offset": 1.0, "sphere_axial_offset": -1.0}),
    ("material_wall_length", {"wall_thickness": 1.0, "cylinder_length": 0.55}),
)

DEFAULT_SHELL_VECTOR = np.array([541.8, -345.0, 2.6, 2.0, 0.0, 0.0, 140.0], dtype=float)

DEFAULT_NUISANCE_VECTORS: dict[str, np.ndarray] = {
    "capacitance_shift": np.array([0.35, 0.05, 0.00, 0.00, 0.35, 0.85, 0.20], dtype=float),
    "patch_potential": np.array([0.45, 0.30, 0.22, 0.10, 0.05, 0.30, 0.55], dtype=float),
    "contact_loading": np.array([0.10, 0.05, 0.00, 0.00, 0.65, 0.75, 0.25], dtype=float),
    "material_response": np.array([0.50, 0.45, 0.00, 0.00, 0.35, 0.00, 0.60], dtype=float),
    "thermal_drift": np.array([0.40, 0.40, 0.15, 0.15, 0.45, 0.35, 0.45], dtype=float),
    "vibration_alignment": np.array([0.05, 0.05, 0.85, 0.65, 0.20, 0.10, 0.00], dtype=float),
    "waveguide_dispersion": np.array([0.25, 0.00, 0.00, 0.00, 0.65, 0.85, 0.05], dtype=float),
    "readout_circuit_artifact": np.array([0.05, 0.00, 0.00, 0.00, 0.45, 1.00, 0.05], dtype=float),
}

STAGE3_PARAMETER_TO_VARIABLE = {
    "cylinder_inner_radius": "cylinder_inner_radius",
    "sphere_diameter": "sphere_diameter",
    "sphere_radial_offset": "sphere_radial_offset",
    "sphere_axial_offset": "sphere_axial_offset",
    "cylinder_length": "cylinder_length",
    "readout_accounting_radius": "readout_accounting_radius",
}

PRESETS: dict[str, dict[str, Any]] = {
    "smoke": {
        "shell_datasets_per_sbr": 12,
        "em_only_datasets_per_sbr": 12,
        "sbr_values": (0.05, 0.10, 0.25, 0.50, 1.00),
        "chunk_size": 12,
    },
    "focused": {
        "shell_datasets_per_sbr": 200,
        "em_only_datasets_per_sbr": 200,
        "sbr_values": (0.02, 0.05, 0.10, 0.20, 0.50, 1.00, 2.00),
        "chunk_size": 100,
    },
}


@dataclass(frozen=True)
class DiscriminationConfig:
    preset: str
    run_id: str
    shell_datasets_per_sbr: int
    em_only_datasets_per_sbr: int
    sbr_values: tuple[float, ...]
    noise_sigma: float
    nuisance_sigma: float
    ridge_alpha: float
    shell_detection_z: float
    base_seed: int
    chunk_size: int
    source_stage3_dir: str | None = None
    template_mode: str = "block_bootstrap"
    nuisance_model: str = "geometry"


class Stage4ProgressRecorder:
    """Append heartbeat events and maintain a latest-status dashboard."""

    def __init__(self, outdir: Path):
        self.outdir = outdir
        self.started = time.time()
        self.progress_path = outdir / "progress.jsonl"
        self.latest_path = outdir / "latest_status.json"
        self.report_path = outdir / "reports" / "stage4_synthetic_discrimination_readout.md"
        (outdir / "reports").mkdir(parents=True, exist_ok=True)
        self.progress_path.write_text("", encoding="utf-8")

    def record(self, event: str, payload: Mapping[str, Any]) -> None:
        elapsed = time.time() - self.started
        row = {
            "utc": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "elapsed_s": elapsed,
            **dict(payload),
        }
        with self.progress_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        self.latest_path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self._write_machine_readout(row)
        print(f"[stage4] {event}: {payload.get('label', '')} elapsed={elapsed:.1f}s", flush=True)

    def _write_machine_readout(self, row: Mapping[str, Any]) -> None:
        text = (
            "# Stage 4 Synthetic Discrimination Readout\n\n"
            "Status: machine-generated heartbeat, not interpretive report.\n\n"
            f"- latest event: `{row.get('event')}`\n"
            f"- elapsed: `{float(row.get('elapsed_s', 0.0)):.1f} s`\n"
            f"- latest label: `{row.get('label', '')}`\n"
            f"- output path: `{self.outdir}`\n\n"
            "Large ledgers are written under `synthetic/` as parquet files.\n"
        )
        self.report_path.write_text(text, encoding="utf-8")


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip()


def _normalize(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(arr))
    if norm <= 0.0:
        return np.zeros_like(arr, dtype=float)
    return arr / norm


def _rms(values: np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr))) if arr.size else 0.0


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_frame(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        frame.to_parquet(path, index=False, compression="zstd")
    else:
        frame.to_csv(path, index=False)


def _schedule_frame() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for order, (name, weights) in enumerate(DEFAULT_SCHEDULE_ROWS):
        row: dict[str, Any] = {"schedule_order": order, "schedule_step": name}
        for variable in SCHEDULE_VARIABLES:
            row[variable] = float(weights.get(variable, 0.0))
        rows.append(row)
    return pd.DataFrame(rows)


def _geometry_nuisance_vectors(schedule: pd.DataFrame, source_stage3_dir: str | None) -> dict[str, np.ndarray]:
    """Build nuisance templates from schedule geometry controls."""

    values = schedule.loc[:, SCHEDULE_VARIABLES].astype(float)
    cylinder = values["cylinder_inner_radius"].to_numpy()
    sphere = values["sphere_diameter"].to_numpy()
    radial = values["sphere_radial_offset"].to_numpy()
    axial = values["sphere_axial_offset"].to_numpy()
    length = values["cylinder_length"].to_numpy()
    readout = values["readout_accounting_radius"].to_numpy()
    wall = values["wall_thickness"].to_numpy()

    gap = cylinder - 0.55 * sphere
    surface = 0.60 * np.abs(sphere) + 0.55 * np.abs(wall) + 0.25 * np.abs(length)
    alignment = radial + 0.75 * axial
    material_scale = _read_stage3_material_scale(source_stage3_dir)
    patch_ratio = material_scale.get("patch_to_casimir_ratio_median") or 1.0
    material_ratio = material_scale.get("casimir_to_material_rest_energy_ratio_median") or 1.0e-27
    patch_gain = min(3.0, max(1.0, np.log10(float(patch_ratio) + 1.0) / 2.0))
    material_gain = min(3.0, max(1.0, -np.log10(max(float(material_ratio), 1.0e-30)) / 16.0))

    return {
        "capacitance_shift": 0.65 * gap + 1.15 * readout + 0.30 * length + 0.20 * wall,
        "patch_potential": patch_gain * (0.75 * gap + 0.45 * surface + 0.35 * np.abs(alignment) + 0.20 * readout),
        "contact_loading": 1.10 * readout + 0.70 * length + 0.30 * wall + 0.15 * np.abs(radial),
        "material_response": material_gain * (0.80 * wall + 0.45 * length + 0.35 * sphere + 0.30 * cylinder),
        "thermal_drift": 0.55 * length + 0.45 * wall + 0.35 * cylinder + 0.25 * sphere + 0.20 * readout,
        "vibration_alignment": 1.15 * radial + 0.85 * axial + 0.20 * length + 0.10 * readout,
        "waveguide_dispersion": 1.20 * readout - 0.40 * cylinder + 0.65 * length + 0.20 * wall,
        "readout_circuit_artifact": 1.30 * readout + 0.65 * length + 0.35 * gap + 0.10 * wall,
    }


def _read_stage3_material_scale(source_stage3_dir: str | None) -> dict[str, Any]:
    if not source_stage3_dir:
        return {
            "material_scale_source": "default_no_stage3_dir",
            "patch_to_casimir_ratio_median": None,
            "casimir_to_material_rest_energy_ratio_median": None,
        }
    material_path = Path(source_stage3_dir) / "material" / "material_competitor_summary.csv"
    if not material_path.exists():
        return {
            "material_scale_source": f"missing:{material_path}",
            "patch_to_casimir_ratio_median": None,
            "casimir_to_material_rest_energy_ratio_median": None,
        }
    frame = pd.read_csv(material_path)
    return {
        "material_scale_source": str(material_path),
        "patch_to_casimir_ratio_median": float(frame["patch_to_casimir_energy_ratio"].median())
        if "patch_to_casimir_energy_ratio" in frame
        else None,
        "casimir_to_material_rest_energy_ratio_median": float(
            frame["casimir_to_material_rest_energy_ratio"].median()
        )
        if "casimir_to_material_rest_energy_ratio" in frame
        else None,
    }


def _nuisance_weight_map(source_stage3_dir: str | None) -> dict[str, float]:
    weights = {name: 1.0 for name in NUISANCE_NAMES}
    if not source_stage3_dir:
        return weights

    material_path = Path(source_stage3_dir) / "material" / "material_competitor_summary.csv"
    if material_path.exists():
        material = pd.read_csv(material_path)
        if "patch_to_casimir_energy_ratio" in material and not material.empty:
            patch_ratio = max(float(material["patch_to_casimir_energy_ratio"].median()), 1.0)
            weights["patch_potential"] = min(5.0, max(1.0, np.log10(patch_ratio + 1.0)))
        if "contact_loading_warning" in material and bool(material["contact_loading_warning"].any()):
            weights["contact_loading"] = 2.0
        if "waveguide_cutoff_hz" in material:
            weights["waveguide_dispersion"] = 1.5
        if "capacitance_F" in material:
            weights["capacitance_shift"] = 1.5
        if "casimir_to_material_rest_energy_ratio" in material and not material.empty:
            ratio = max(float(material["casimir_to_material_rest_energy_ratio"].median()), 1.0e-30)
            weights["material_response"] = min(5.0, max(1.0, -np.log10(ratio) / 8.0))

    readout_path = Path(source_stage3_dir) / "readout" / "readout_coupling_summary.csv"
    if readout_path.exists():
        readout = pd.read_csv(readout_path)
        if "readout_source_fraction" in readout and not readout.empty:
            fraction = max(float(readout["readout_source_fraction"].median()), 0.0)
            weights["readout_circuit_artifact"] = min(3.0, 1.0 + 25.0 * fraction)
    return weights


def _shell_variable_vector(source_stage3_dir: str | None) -> tuple[np.ndarray, dict[str, Any]]:
    vector = DEFAULT_SHELL_VECTOR.astype(float).copy()
    provenance: dict[str, Any] = {
        "shell_template_source": "default_stage3_focused_summary_values",
        "stage3_rows_used": 0,
    }
    if not source_stage3_dir:
        return vector, provenance

    bootstrap_path = Path(source_stage3_dir) / "tensor" / "bootstrap_summary.csv"
    if not bootstrap_path.exists():
        provenance["shell_template_source"] = f"missing:{bootstrap_path}"
        return vector, provenance

    frame = pd.read_csv(bootstrap_path)
    if frame.empty or "parameter" not in frame or "channel" not in frame:
        provenance["shell_template_source"] = f"unusable:{bootstrap_path}"
        return vector, provenance

    channel_priority = (
        "source_shell_candidate_signed_integral",
        "source_shell_candidate_negative_magnitude_integral",
    )
    selected = pd.DataFrame()
    for channel in channel_priority:
        candidate = frame[frame["channel"] == channel]
        if not candidate.empty:
            selected = candidate
            break
    if selected.empty:
        provenance["shell_template_source"] = f"no_shell_channel:{bootstrap_path}"
        return vector, provenance

    grouped = selected.groupby("parameter", dropna=False)["median_per_um"].median()
    for parameter, value in grouped.items():
        variable = STAGE3_PARAMETER_TO_VARIABLE.get(str(parameter))
        if variable is None:
            continue
        vector[SCHEDULE_VARIABLES.index(variable)] = float(value)
    provenance = {
        "shell_template_source": str(bootstrap_path),
        "stage3_rows_used": int(len(selected)),
        "stage3_channel": str(selected["channel"].iloc[0]),
    }
    return vector, provenance


def _shell_variable_samples(source_stage3_dir: str | None) -> tuple[pd.DataFrame, dict[str, Any]]:
    columns = ["sample_id", "block_id", "wall_thickness_um", "scale_window", *SCHEDULE_VARIABLES]
    if not source_stage3_dir:
        return pd.DataFrame(columns=columns), {"shell_template_sample_source": "none_no_stage3_dir"}

    base = Path(source_stage3_dir)
    points_path = base / "tensor" / "stress_channel_points.parquet"
    baseline_path = base / "tensor" / "stress_channel_baseline_blocks.parquet"
    if not points_path.exists():
        return pd.DataFrame(columns=columns), {"shell_template_sample_source": f"missing:{points_path}"}

    points = pd.read_parquet(points_path)
    channel_priority = (
        "source_shell_candidate_signed_integral",
        "source_shell_candidate_negative_magnitude_integral",
    )
    selected = pd.DataFrame()
    for channel in channel_priority:
        candidate = points[points["channel"] == channel]
        if not candidate.empty:
            selected = candidate
            break
    if selected.empty:
        return pd.DataFrame(columns=columns), {"shell_template_sample_source": f"no_shell_channel:{points_path}"}

    rows: list[dict[str, Any]] = []
    grouped = selected.groupby(["block_id", "wall_thickness_um", "scale_window"], dropna=False)
    sample_id = 0
    for (block_id, wall, window), group in grouped:
        row: dict[str, Any] = {
            "sample_id": sample_id,
            "block_id": int(block_id),
            "wall_thickness_um": float(wall),
            "scale_window": str(window),
        }
        vector = DEFAULT_SHELL_VECTOR.astype(float).copy()
        for _, item in group.iterrows():
            variable = STAGE3_PARAMETER_TO_VARIABLE.get(str(item["parameter"]))
            if variable is not None:
                vector[SCHEDULE_VARIABLES.index(variable)] = float(item["finite_difference_per_um"])
        for index, variable in enumerate(SCHEDULE_VARIABLES):
            row[variable] = float(vector[index])
        rows.append(row)
        sample_id += 1

    samples = pd.DataFrame(rows, columns=columns)
    provenance = {
        "shell_template_sample_source": str(points_path),
        "shell_template_sample_channel": str(selected["channel"].iloc[0]),
        "shell_template_sample_rows": int(len(samples)),
    }

    if baseline_path.exists() and not samples.empty:
        baseline = pd.read_parquet(baseline_path)
        needed = {"block_id", "wall_thickness_um", "scale_window", "source_shell_candidate_signed_integral"}
        if needed.issubset(set(baseline.columns)):
            pivot = baseline.pivot_table(
                index=["block_id", "scale_window"],
                columns="wall_thickness_um",
                values="source_shell_candidate_signed_integral",
                aggfunc="median",
            )
            wall_derivatives: dict[tuple[int, str], float] = {}
            for key, row in pivot.iterrows():
                if 0.2 in row and 0.4 in row and pd.notna(row[0.2]) and pd.notna(row[0.4]):
                    wall_derivatives[(int(key[0]), str(key[1]))] = float((row[0.4] - row[0.2]) / 0.2)
            if wall_derivatives:
                samples["wall_thickness"] = [
                    wall_derivatives.get((int(row.block_id), str(row.scale_window)), row.wall_thickness)
                    for row in samples.itertuples(index=False)
                ]
                provenance["wall_thickness_sample_source"] = str(baseline_path)
                provenance["wall_thickness_sample_rows"] = int(len(wall_derivatives))
    return samples, provenance


def _shell_template_sample_frame(schedule: pd.DataFrame, source_stage3_dir: str | None) -> tuple[pd.DataFrame, dict[str, Any]]:
    samples, provenance = _shell_variable_samples(source_stage3_dir)
    if samples.empty:
        shell_vector, shell_provenance = _shell_variable_vector(source_stage3_dir)
        samples = pd.DataFrame(
            [
                {
                    "sample_id": 0,
                    "block_id": -1,
                    "wall_thickness_um": np.nan,
                    "scale_window": "fallback",
                    **{variable: float(shell_vector[index]) for index, variable in enumerate(SCHEDULE_VARIABLES)},
                }
            ]
        )
        provenance.update(shell_provenance)
        provenance["shell_template_sample_rows"] = 1

    schedule_matrix = schedule.loc[:, SCHEDULE_VARIABLES].to_numpy(dtype=float)
    rows: list[dict[str, Any]] = []
    for sample in samples.itertuples(index=False):
        vector = np.array([float(getattr(sample, variable)) for variable in SCHEDULE_VARIABLES], dtype=float)
        template = _normalize(schedule_matrix @ vector)
        for order, value in enumerate(template):
            rows.append(
                {
                    "sample_id": int(sample.sample_id),
                    "block_id": int(sample.block_id),
                    "wall_thickness_um": float(sample.wall_thickness_um)
                    if pd.notna(sample.wall_thickness_um)
                    else np.nan,
                    "scale_window": str(sample.scale_window),
                    "schedule_order": int(order),
                    "schedule_step": str(schedule.loc[order, "schedule_step"]),
                    "template_value": float(value),
                }
            )
    return pd.DataFrame(rows), provenance


def build_template_bundle(
    source_stage3_dir: str | None = None,
    nuisance_model: str = "geometry",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    schedule = _schedule_frame()
    schedule_matrix = schedule.loc[:, SCHEDULE_VARIABLES].to_numpy(dtype=float)
    shell_vector, provenance = _shell_variable_vector(source_stage3_dir)
    shell_template = _normalize(schedule_matrix @ shell_vector)

    template_columns: dict[str, np.ndarray] = {"shell_channel": shell_template}
    if nuisance_model == "geometry":
        nuisance_vectors = _geometry_nuisance_vectors(schedule, source_stage3_dir)
        provenance["nuisance_template_model"] = "geometry_derived_proxy"
        for nuisance_name in NUISANCE_NAMES:
            template_columns[nuisance_name] = _normalize(np.asarray(nuisance_vectors[nuisance_name], dtype=float))
    else:
        provenance["nuisance_template_model"] = "fixed_abstract_vector"
        for nuisance_name in NUISANCE_NAMES:
            template_columns[nuisance_name] = _normalize(schedule_matrix @ DEFAULT_NUISANCE_VECTORS[nuisance_name])

    template_rows: list[dict[str, Any]] = []
    for template_name, values in template_columns.items():
        role = "shell" if template_name == "shell_channel" else "nuisance"
        for order, value in enumerate(values):
            template_rows.append(
                {
                    "schedule_order": int(order),
                    "schedule_step": str(schedule.loc[order, "schedule_step"]),
                    "template_name": template_name,
                    "template_role": role,
                    "template_value": float(value),
                }
            )
    template_frame = pd.DataFrame(template_rows)

    matrix = np.column_stack([template_columns[name] for name in template_columns])
    names = list(template_columns)
    corr = matrix.T @ matrix
    orthogonality = pd.DataFrame(corr, columns=names)
    orthogonality.insert(0, "template_name", names)
    provenance.update(_read_stage3_material_scale(source_stage3_dir))
    provenance["schedule_steps"] = int(len(schedule))
    provenance["template_count"] = int(len(names))
    return schedule, template_frame, provenance


def _template_matrix(template_frame: pd.DataFrame) -> tuple[np.ndarray, list[str], list[str]]:
    pivot = template_frame.pivot(index="schedule_order", columns="template_name", values="template_value").sort_index()
    names = ["shell_channel", *[name for name in NUISANCE_NAMES if name in pivot.columns]]
    pivot = pivot.loc[:, names]
    schedule_steps = (
        template_frame[["schedule_order", "schedule_step"]]
        .drop_duplicates()
        .sort_values("schedule_order")["schedule_step"]
        .astype(str)
        .tolist()
    )
    return pivot.to_numpy(dtype=float), names, schedule_steps


def _generate_dataset_rows(
    dataset_id: int,
    family: str,
    sbr: float,
    rng: np.random.Generator,
    cfg: DiscriminationConfig,
    x_matrix: np.ndarray,
    data_shell_template: np.ndarray,
    template_sample_id: int,
    template_names: list[str],
    schedule_steps: list[str],
    nuisance_weights: Mapping[str, float],
) -> list[dict[str, Any]]:
    shell_template = _normalize(data_shell_template)
    fit_shell_template = _normalize(x_matrix[:, 0])
    template_correlation = float(shell_template @ fit_shell_template)
    nuisance_matrix = x_matrix[:, 1:]
    coefficient_scales = np.array(
        [cfg.nuisance_sigma * float(nuisance_weights.get(name, 1.0)) for name in template_names[1:]],
        dtype=float,
    )
    nuisance_coefficients = rng.normal(0.0, coefficient_scales, nuisance_matrix.shape[1])
    nuisance_components = nuisance_matrix * nuisance_coefficients[None, :]
    nuisance_total = np.sum(nuisance_components, axis=1)
    background_rms = max(_rms(nuisance_total), 1.0e-12)
    shell_coefficient = float(sbr * background_rms) if family == "shell_plus_em" else 0.0
    shell_component = shell_coefficient * shell_template
    noise_scale = cfg.noise_sigma * max(background_rms, 1.0)
    noise = rng.normal(0.0, noise_scale, len(schedule_steps))
    observed = shell_component + nuisance_total + noise

    rows: list[dict[str, Any]] = []
    for order, step in enumerate(schedule_steps):
        row: dict[str, Any] = {
            "dataset_id": dataset_id,
            "simulation_family": family,
            "sbr": float(sbr),
            "schedule_order": int(order),
            "schedule_step": step,
            "observed_value": float(observed[order]),
            "shell_component": float(shell_component[order]),
            "noise_component": float(noise[order]),
            "true_shell_coefficient": shell_coefficient,
            "background_rms": background_rms,
            "template_sample_id": int(template_sample_id),
            "shell_fit_template_correlation": template_correlation,
        }
        for nuisance_index, nuisance_name in enumerate(template_names[1:]):
            row[f"{nuisance_name}_component"] = float(nuisance_components[order, nuisance_index])
        rows.append(row)
    return rows


def _fit_dataset(
    group: pd.DataFrame,
    x_matrix: np.ndarray,
    template_names: list[str],
    cfg: DiscriminationConfig,
) -> dict[str, Any]:
    ordered = group.sort_values("schedule_order")
    y = ordered["observed_value"].to_numpy(dtype=float)
    xtx = x_matrix.T @ x_matrix
    penalty = cfg.ridge_alpha * np.eye(xtx.shape[0])
    inv = np.linalg.pinv(xtx + penalty)
    coeff = inv @ x_matrix.T @ y
    residual = y - x_matrix @ coeff
    dof = max(len(y) - len(coeff), 1)
    residual_rms = _rms(residual)
    sigma2 = float(np.sum(residual * residual) / dof)
    shell_se = float(np.sqrt(max(inv[0, 0] * sigma2, 1.0e-24)))
    shell_z = float(coeff[0] / shell_se)
    true_shell = float(ordered["true_shell_coefficient"].iloc[0])
    shell_fraction = float(coeff[0] / true_shell) if abs(true_shell) > 0.0 else 0.0
    family = str(ordered["simulation_family"].iloc[0])
    shell_detected = bool(coeff[0] > 0.0 and shell_z >= cfg.shell_detection_z)
    row: dict[str, Any] = {
        "dataset_id": int(ordered["dataset_id"].iloc[0]),
        "simulation_family": family,
        "sbr": float(ordered["sbr"].iloc[0]),
        "template_sample_id": int(ordered["template_sample_id"].iloc[0])
        if "template_sample_id" in ordered
        else -1,
        "shell_fit_template_correlation": float(ordered["shell_fit_template_correlation"].iloc[0])
        if "shell_fit_template_correlation" in ordered
        else 1.0,
        "true_shell_coefficient": true_shell,
        "shell_coefficient": float(coeff[0]),
        "shell_standard_error": shell_se,
        "shell_z_score": shell_z,
        "shell_fraction_recovered": shell_fraction,
        "shell_recovered": bool(family == "shell_plus_em" and shell_detected),
        "false_positive": bool(family == "em_only" and shell_detected),
        "residual_rms": residual_rms,
        "template_condition_number": float(np.linalg.cond(xtx + penalty)),
    }
    for index, name in enumerate(template_names):
        row[f"fit_{name}"] = float(coeff[index])
    return row


def _candidate_schedule_subsets(schedule_steps: list[str]) -> dict[str, list[int]]:
    index = {name: idx for idx, name in enumerate(schedule_steps)}

    def ids(names: tuple[str, ...]) -> list[int]:
        return [index[name] for name in names if name in index]

    return {
        "full_schedule": list(range(len(schedule_steps))),
        "shell_core": ids(
            (
                "cylinder_radius",
                "sphere_diameter",
                "shell_gap_contrast",
                "shell_size_contrast",
                "wall_thickness",
                "material_wall_length",
            )
        ),
        "readout_countermodulated": ids(
            (
                "cylinder_radius",
                "sphere_diameter",
                "readout_radius",
                "readout_isolation",
                "shell_gap_contrast",
                "shell_size_contrast",
                "cylinder_length",
            )
        ),
        "offset_controls": ids(
            (
                "radial_offset",
                "axial_offset",
                "offset_balance",
                "cylinder_radius",
                "sphere_diameter",
                "shell_gap_contrast",
            )
        ),
        "material_controls": ids(
            (
                "wall_thickness",
                "material_wall_length",
                "cylinder_length",
                "readout_radius",
                "readout_isolation",
                "shell_gap_contrast",
            )
        ),
    }


def _max_shell_nuisance_correlation(x_matrix: np.ndarray) -> float:
    shell = _normalize(x_matrix[:, 0])
    values = []
    for idx in range(1, x_matrix.shape[1]):
        nuisance = _normalize(x_matrix[:, idx])
        values.append(abs(float(shell @ nuisance)))
    return max(values) if values else 0.0


def _recommend_schedules(
    x_matrix: np.ndarray,
    template_names: list[str],
    schedule_steps: list[str],
    cfg: DiscriminationConfig,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for name, indices in _candidate_schedule_subsets(schedule_steps).items():
        if not indices:
            continue
        subset = x_matrix[indices, :]
        gram = subset.T @ subset + cfg.ridge_alpha * np.eye(len(template_names))
        condition = float(np.linalg.cond(gram))
        rank = int(np.linalg.matrix_rank(subset))
        max_corr = _max_shell_nuisance_correlation(subset)
        coverage = len(indices) / len(schedule_steps)
        rank_fraction = rank / len(template_names)
        score = rank_fraction + 0.35 * coverage - max_corr - 0.05 * np.log10(max(condition, 1.0))
        rows.append(
            {
                "schedule_name": name,
                "schedule_steps": ",".join(schedule_steps[idx] for idx in indices),
                "n_steps": int(len(indices)),
                "template_rank": rank,
                "template_count": int(len(template_names)),
                "rank_fraction": float(rank_fraction),
                "max_abs_shell_nuisance_correlation": float(max_corr),
                "condition_number": condition,
                "schedule_score": float(score),
            }
        )
    frame = pd.DataFrame(rows).sort_values("schedule_score", ascending=False).reset_index(drop=True)
    frame["recommended"] = False
    if not frame.empty:
        frame.loc[0, "recommended"] = True
    return frame


def _summarize_recovery(recovery: pd.DataFrame, max_corr: float) -> dict[str, Any]:
    if recovery.empty:
        return {
            "recovery_fraction_at_max_sbr": 0.0,
            "false_positive_rate": 0.0,
            "required_signal_to_background_ratio": None,
            "max_abs_shell_nuisance_correlation": max_corr,
        }
    shell = recovery[recovery["simulation_family"] == "shell_plus_em"]
    em_only = recovery[recovery["simulation_family"] == "em_only"]
    recovery_by_sbr = shell.groupby("sbr")["shell_recovered"].mean() if not shell.empty else pd.Series(dtype=float)
    false_by_sbr = em_only.groupby("sbr")["false_positive"].mean() if not em_only.empty else pd.Series(dtype=float)
    required_sbr: float | None = None
    for sbr in sorted(recovery["sbr"].unique()):
        recovered = float(recovery_by_sbr.get(sbr, 0.0))
        false_rate = float(false_by_sbr.get(sbr, 0.0))
        if recovered >= 0.8 and false_rate <= 0.05:
            required_sbr = float(sbr)
            break
    max_sbr = float(max(recovery["sbr"])) if not recovery.empty else 0.0
    return {
        "recovery_fraction_at_max_sbr": float(recovery_by_sbr.get(max_sbr, 0.0)),
        "false_positive_rate": float(em_only["false_positive"].mean()) if not em_only.empty else 0.0,
        "required_signal_to_background_ratio": required_sbr,
        "max_abs_shell_nuisance_correlation": max_corr,
    }


def _write_manifest(outdir: Path, cfg: DiscriminationConfig, provenance: Mapping[str, Any]) -> None:
    payload = {
        "run_id": cfg.run_id,
        "stage": "stage4_synthetic_em_background_discrimination",
        "claim_boundary": "synthetic_identifiability_proxy_not_physical_detection_claim",
        "git_commit": _git_commit(),
        "config": asdict(cfg),
        "provenance": dict(provenance),
        "output_categories": [
            "template_matrix",
            "synthetic_observation_ledger",
            "recovery_fit_ledger",
            "em_only_false_positive_ledger",
            "schedule_recommendation",
        ],
    }
    _write_json(outdir / "manifest.json", payload)
    _write_json(outdir / "configs" / "run_config.json", asdict(cfg))


def run_synthetic_discrimination(outdir: Path, cfg: DiscriminationConfig) -> dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    for subdir in ("configs", "synthetic", "reports"):
        (outdir / subdir).mkdir(parents=True, exist_ok=True)

    recorder = Stage4ProgressRecorder(outdir)
    recorder.record("run_start", {"label": cfg.run_id, "preset": cfg.preset})

    schedule, template_frame, provenance = build_template_bundle(cfg.source_stage3_dir, cfg.nuisance_model)
    nuisance_weights = _nuisance_weight_map(cfg.source_stage3_dir)
    provenance["nuisance_amplitude_weights"] = nuisance_weights
    x_matrix, template_names, schedule_steps = _template_matrix(template_frame)
    shell_samples, shell_sample_provenance = _shell_template_sample_frame(schedule, cfg.source_stage3_dir)
    provenance.update(shell_sample_provenance)
    sample_pivot = shell_samples.pivot(index="sample_id", columns="schedule_order", values="template_value").sort_index()
    sample_ids = sample_pivot.index.astype(int).to_numpy()
    sample_matrix = sample_pivot.to_numpy(dtype=float)
    sample_correlations = sample_matrix @ _normalize(x_matrix[:, 0])
    if cfg.template_mode != "block_bootstrap":
        sample_ids = np.array([0], dtype=int)
        sample_matrix = x_matrix[:, 0][None, :]
        sample_correlations = np.array([1.0], dtype=float)
    orthogonality = pd.DataFrame(x_matrix.T @ x_matrix, columns=template_names)
    orthogonality.insert(0, "template_name", template_names)
    max_corr = _max_shell_nuisance_correlation(x_matrix)
    _write_manifest(outdir, cfg, provenance)
    _write_frame(outdir / "synthetic" / "schedule_matrix.parquet", schedule)
    _write_frame(outdir / "synthetic" / "template_matrix.parquet", template_frame)
    _write_frame(outdir / "synthetic" / "shell_template_samples.parquet", shell_samples)
    _write_frame(outdir / "synthetic" / "template_orthogonality.csv", orthogonality)
    recorder.record(
        "template_stage_complete",
        {
            "label": "templates",
            "max_abs_shell_nuisance_correlation": max_corr,
            **provenance,
        },
    )

    rng = np.random.default_rng(cfg.base_seed)
    observation_rows: list[dict[str, Any]] = []
    dataset_id = 0
    generated_since_heartbeat = 0
    total_datasets = len(cfg.sbr_values) * (cfg.shell_datasets_per_sbr + cfg.em_only_datasets_per_sbr)
    for sbr in cfg.sbr_values:
        for family, count in (
            ("shell_plus_em", cfg.shell_datasets_per_sbr),
            ("em_only", cfg.em_only_datasets_per_sbr),
        ):
            for _ in range(count):
                sample_position = int(rng.integers(0, len(sample_ids)))
                observation_rows.extend(
                    _generate_dataset_rows(
                        dataset_id,
                        family,
                        float(sbr),
                        rng,
                        cfg,
                        x_matrix,
                        sample_matrix[sample_position],
                        int(sample_ids[sample_position]),
                        template_names,
                        schedule_steps,
                        nuisance_weights,
                    )
                )
                dataset_id += 1
                generated_since_heartbeat += 1
                if generated_since_heartbeat >= cfg.chunk_size:
                    recorder.record(
                        "synthetic_chunk_complete",
                        {
                            "label": f"{dataset_id}/{total_datasets}",
                            "datasets_generated": dataset_id,
                            "total_datasets": total_datasets,
                        },
                    )
                    generated_since_heartbeat = 0
    if generated_since_heartbeat:
        recorder.record(
            "synthetic_chunk_complete",
            {
                "label": f"{dataset_id}/{total_datasets}",
                "datasets_generated": dataset_id,
                "total_datasets": total_datasets,
            },
        )

    observations = pd.DataFrame(observation_rows)
    _write_frame(outdir / "synthetic" / "synthetic_observations.parquet", observations)

    fit_rows: list[dict[str, Any]] = []
    fitted = 0
    for _, group in observations.groupby("dataset_id", sort=True):
        fit_rows.append(_fit_dataset(group, x_matrix, template_names, cfg))
        fitted += 1
        if fitted % cfg.chunk_size == 0:
            recorder.record(
                "fit_chunk_complete",
                {"label": f"{fitted}/{total_datasets}", "datasets_fit": fitted, "total_datasets": total_datasets},
            )
    if fitted % cfg.chunk_size:
        recorder.record(
            "fit_chunk_complete",
            {"label": f"{fitted}/{total_datasets}", "datasets_fit": fitted, "total_datasets": total_datasets},
        )

    recovery = pd.DataFrame(fit_rows)
    false_positive = recovery[recovery["simulation_family"] == "em_only"].copy()
    recommendation = _recommend_schedules(x_matrix, template_names, schedule_steps, cfg)
    _write_frame(outdir / "synthetic" / "recovery_ledger.parquet", recovery)
    _write_frame(outdir / "synthetic" / "false_positive_ledger.parquet", false_positive)
    _write_frame(outdir / "synthetic" / "schedule_recommendation.csv", recommendation)
    recorder.record(
        "schedule_recommendation_complete",
        {
            "label": str(recommendation["schedule_name"].iloc[0]) if not recommendation.empty else "none",
            "recommended_score": float(recommendation["schedule_score"].iloc[0]) if not recommendation.empty else 0.0,
        },
    )

    recovery_summary = _summarize_recovery(recovery, max_corr)
    summary = {
        "run_id": cfg.run_id,
        "outdir": str(outdir),
        "stage": "stage4_synthetic_em_background_discrimination",
        "claim_boundary": "synthetic_identifiability_proxy_not_physical_detection_claim",
        "n_schedule_steps": int(len(schedule_steps)),
        "n_templates": int(len(template_names)),
        "n_shell_template_samples": int(len(sample_ids)),
        "shell_template_correlation_median": float(np.median(sample_correlations)) if len(sample_correlations) else 1.0,
        "shell_template_correlation_q16": float(np.quantile(sample_correlations, 0.16))
        if len(sample_correlations)
        else 1.0,
        "shell_template_correlation_q84": float(np.quantile(sample_correlations, 0.84))
        if len(sample_correlations)
        else 1.0,
        "n_observation_rows": int(len(observations)),
        "n_fit_rows": int(len(recovery)),
        "recommended_schedule": str(recommendation["schedule_name"].iloc[0]) if not recommendation.empty else None,
        **recovery_summary,
        **provenance,
    }
    _write_json(outdir / "summary.json", summary)
    recorder.record("run_complete", {"label": cfg.run_id, **summary})
    return summary


def config_from_args(args: argparse.Namespace) -> DiscriminationConfig:
    preset = PRESETS[args.preset].copy()
    shell_datasets = args.shell_datasets_per_sbr
    em_only_datasets = args.em_only_datasets_per_sbr
    chunk_size = args.chunk_size
    if shell_datasets is not None:
        preset["shell_datasets_per_sbr"] = shell_datasets
    if em_only_datasets is not None:
        preset["em_only_datasets_per_sbr"] = em_only_datasets
    if args.sbr_values is not None:
        preset["sbr_values"] = tuple(args.sbr_values)
    if chunk_size is not None:
        preset["chunk_size"] = chunk_size
    run_id = args.run_id or f"stage4_{args.preset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return DiscriminationConfig(
        preset=args.preset,
        run_id=run_id,
        shell_datasets_per_sbr=int(preset["shell_datasets_per_sbr"]),
        em_only_datasets_per_sbr=int(preset["em_only_datasets_per_sbr"]),
        sbr_values=tuple(float(value) for value in preset["sbr_values"]),
        noise_sigma=float(args.noise_sigma),
        nuisance_sigma=float(args.nuisance_sigma),
        ridge_alpha=float(args.ridge_alpha),
        shell_detection_z=float(args.shell_detection_z),
        base_seed=int(args.base_seed),
        chunk_size=int(preset["chunk_size"]),
        source_stage3_dir=str(args.source_stage3_dir) if args.source_stage3_dir is not None else None,
        template_mode=str(args.template_mode),
        nuisance_model=str(args.nuisance_model),
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Stage 4 synthetic White readout-discrimination harness.")
    parser.add_argument("--preset", choices=tuple(PRESETS), default="smoke")
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--source-stage3-dir", type=Path, default=None)
    parser.add_argument("--shell-datasets-per-sbr", type=int, default=None)
    parser.add_argument("--em-only-datasets-per-sbr", type=int, default=None)
    parser.add_argument("--sbr-values", type=float, nargs="+", default=None)
    parser.add_argument("--noise-sigma", type=float, default=0.05)
    parser.add_argument("--nuisance-sigma", type=float, default=1.0)
    parser.add_argument("--ridge-alpha", type=float, default=1.0e-3)
    parser.add_argument("--shell-detection-z", type=float, default=2.0)
    parser.add_argument("--base-seed", type=int, default=41)
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--template-mode", choices=("median", "block_bootstrap"), default="block_bootstrap")
    parser.add_argument("--nuisance-model", choices=("geometry", "fixed"), default="geometry")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    cfg = config_from_args(args)
    outdir = args.outdir
    if outdir is None:
        outdir = DEFAULT_EXTERNAL_BASE / cfg.run_id
    summary = run_synthetic_discrimination(outdir.resolve(), cfg)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
