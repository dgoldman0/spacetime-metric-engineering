"""Stage 3 tensor-scale harness for the White Casimir audit.

This harness extends the scalar morphology result with calibrated scale
brackets, finite-difference stress-channel proxies, material/readout competitor
tables, and progress checkpoints. The stress rows remain proxy-level outputs;
they are not a worldline stress-energy tensor reconstruction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .alcubierre_target import build_target_grid
from .constants import (
    C_M_S,
    parallel_plate_em_energy_density_J_m3,
    parallel_plate_scalar_dirichlet_energy_density_J_m3,
)
from .em_proxy import estimate_em_competitors
from .fidelity_probe import estimate_pair_surface_field
from .geometry import CentralReadoutPath, ParallelPlates, SphereInCylinder, make_xy_grid
from .linearized_metric import estimate_timing_bound
from .loop_gen import generate_loops
from .stress_tensor_proxy import field_channel_metrics, finite_difference_rows, summarize_bootstrap

DEFAULT_EXTERNAL_BASE = Path("/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_tensor_scale_probe")

SCALE_WINDOWS = {
    "mid_0p75_1p50": (0.75, 1.50, 8),
    "upper_1p50_2p75": (1.50, 2.75, 8),
}

PRESETS: dict[str, dict[str, Any]] = {
    "smoke": {
        "grid_n": 25,
        "loop_blocks": 4,
        "loops_per_block": 16,
        "points_per_loop": 128,
        "workers": 2,
        "chunk_size": 12,
    },
    "focused": {
        "grid_n": 73,
        "loop_blocks": 12,
        "loops_per_block": 32,
        "points_per_loop": 256,
        "workers": 4,
        "chunk_size": 12,
    },
    "stretch": {
        "grid_n": 121,
        "loop_blocks": 16,
        "loops_per_block": 32,
        "points_per_loop": 256,
        "workers": 4,
        "chunk_size": 8,
    },
}

CALIBRATION_GAPS_UM = (0.75, 1.0, 1.25, 1.5, 2.0, 2.75)
WALL_THICKNESSES_UM = (0.2, 0.4)
MATERIAL_FACTORS = (1.0, 0.5, 0.1, 0.01)


@dataclass(frozen=True)
class HarnessConfig:
    preset: str
    run_id: str
    grid_n: int
    grid_extent_um: float
    loop_blocks: int
    loops_per_block: int
    points_per_loop: int
    workers: int
    chunk_size: int
    base_seed: int
    wall_thicknesses_um: tuple[float, ...]
    scale_windows: tuple[str, ...]
    calibration_gaps_um: tuple[float, ...]
    material_factors: tuple[float, ...]
    sphere_diameter_um: float = 1.0
    cylinder_diameter_um: float = 4.0
    cylinder_length_um: float = 8.0
    readout_radius_um: float = 0.05
    finite_delta_um: float = 0.025
    cylinder_length_delta_um: float = 0.10


class ProgressRecorder:
    """Write heartbeat, latest-status, and machine-readout files."""

    def __init__(self, outdir: Path, total_tasks: int):
        self.outdir = outdir
        self.total_tasks = int(total_tasks)
        self.completed = 0
        self.started = time.time()
        self.progress_path = outdir / "progress.jsonl"
        self.latest_path = outdir / "latest_status.json"
        self.report_path = outdir / "reports" / "second_question_machine_readout.md"
        (outdir / "reports").mkdir(parents=True, exist_ok=True)
        self.progress_path.write_text("", encoding="utf-8")

    def record(self, event: str, payload: Mapping[str, Any]) -> None:
        if event in {"calibration_block_complete", "tensor_block_complete"}:
            self.completed += 1
        elapsed = time.time() - self.started
        rate = self.completed / elapsed if elapsed > 0.0 else 0.0
        remaining = max(self.total_tasks - self.completed, 0)
        eta_s = remaining / rate if rate > 0.0 else None
        row = {
            "utc": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "completed_tasks": self.completed,
            "total_tasks": self.total_tasks,
            "elapsed_s": elapsed,
            "eta_s": eta_s,
            **dict(payload),
        }
        with self.progress_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        self.latest_path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self._write_machine_readout(row)
        print(
            f"[stage3] {event}: {self.completed}/{self.total_tasks} "
            f"elapsed={elapsed:.1f}s eta={(eta_s if eta_s is not None else -1.0):.1f}s "
            f"{payload.get('label', '')}",
            flush=True,
        )

    def _write_machine_readout(self, row: Mapping[str, Any]) -> None:
        eta = row.get("eta_s")
        eta_text = "unknown" if eta is None else f"{float(eta):.1f} s"
        text = (
            "# Stage 3 Machine Readout\n\n"
            "Status: machine-generated progress summary, not interpretive report.\n\n"
            f"- latest event: `{row.get('event')}`\n"
            f"- completed tasks: `{row.get('completed_tasks')}` / `{row.get('total_tasks')}`\n"
            f"- elapsed: `{float(row.get('elapsed_s', 0.0)):.1f} s`\n"
            f"- ETA: `{eta_text}`\n"
            f"- latest label: `{row.get('label', '')}`\n"
            f"- latest output path: `{self.outdir}`\n\n"
            "Progress events are appended to `progress.jsonl`; this file is only a heartbeat dashboard.\n"
        )
        self.report_path.write_text(text, encoding="utf-8")


def _scale_values(name: str) -> np.ndarray:
    start, stop, count = SCALE_WINDOWS[name]
    return np.linspace(start, stop, int(count))


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


def _sha256_array(arr: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(arr, dtype=np.float64).tobytes()).hexdigest()[:16]


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_frame(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        frame.to_parquet(path, index=False, compression="zstd")
    else:
        frame.to_csv(path, index=False)


def _batched_plane_hits(
    p0: np.ndarray,
    d: np.ndarray,
    plane_y: float,
    width_um: float,
    height_um: float,
) -> np.ndarray:
    dy = d[..., 1]
    valid = np.abs(dy) > 1.0e-15
    t = (float(plane_y) - p0[..., 1]) / np.where(valid, dy, 1.0)
    x_at = p0[..., 0] + t * d[..., 0]
    z_at = p0[..., 2] + t * d[..., 2]
    segment_hit = (
        valid
        & (t >= 0.0)
        & (t <= 1.0)
        & (np.abs(x_at) <= 0.5 * float(width_um))
        & (np.abs(z_at) <= 0.5 * float(height_um))
    )
    return np.any(segment_hit, axis=2)


def estimate_plate_pair_surface_field(
    geometry: ParallelPlates,
    grid: Mapping[str, np.ndarray],
    loops: np.ndarray,
    scale_grid: np.ndarray,
    chunk_size: int = 12,
) -> dict[str, Any]:
    """Pair-resolved plane crossing proxy for calibration plates."""

    centers = np.stack([grid["x"], grid["y"], grid["z"]], axis=-1).reshape(-1, 3)
    scales = np.asarray(scale_grid, dtype=float)
    loop_starts = np.asarray(loops, dtype=float)
    loop_ends = np.roll(loop_starts, -1, axis=1)
    segment_delta = loop_ends - loop_starts
    values = np.zeros(len(centers), dtype=float)
    touch_counts = np.zeros(len(centers), dtype=np.int32)
    start = time.perf_counter()
    for begin in range(0, len(centers), chunk_size):
        stop = min(begin + chunk_size, len(centers))
        center_chunk = centers[begin:stop]
        chunk_score = np.zeros(stop - begin, dtype=float)
        chunk_touches = np.zeros(stop - begin, dtype=np.int32)
        for scale in scales:
            p0 = center_chunk[:, None, None, :] + scale * loop_starts[None, :, :, :]
            d = scale * segment_delta[None, :, :, :]
            lower = _batched_plane_hits(
                p0,
                d,
                -0.5 * geometry.gap_um,
                geometry.width_um,
                geometry.height_um,
            )
            upper = _batched_plane_hits(
                p0,
                d,
                0.5 * geometry.gap_um,
                geometry.width_um,
                geometry.height_um,
            )
            pair_hits = lower & upper
            counts = np.count_nonzero(pair_hits, axis=1)
            chunk_touches += counts.astype(np.int32)
            chunk_score -= counts.astype(float) / float(scale**4)
        values[begin:stop] = chunk_score / max(loop_starts.shape[0], 1)
        touch_counts[begin:stop] = chunk_touches
    elapsed_s = time.perf_counter() - start
    shape = grid["x"].shape
    return {
        "density_proxy": values.reshape(shape),
        "touch_count": touch_counts.reshape(shape),
        "metadata": {
            "kernel": "pair_resolved_segment_surface_parallel_plate",
            "loop_method": "v_loop",
            "normalization": "normalized_morphology_proxy_not_si_normalized",
            "gap_um": float(geometry.gap_um),
            "scale_grid": [float(value) for value in scales],
            "elapsed_s": float(elapsed_s),
        },
    }


def _calibration_task(task: Mapping[str, Any]) -> list[dict[str, Any]]:
    cfg = task["config"]
    block_id = int(task["block_id"])
    gap_um = float(task["gap_um"])
    window = str(task["scale_window"])
    seed = int(cfg["base_seed"]) + 10_000 + block_id
    loops = generate_loops(int(cfg["loops_per_block"]), int(cfg["points_per_loop"]), seed, method="v_loop")
    scales = _scale_values(window)
    grid_n = int(cfg["grid_n"])
    geometry = ParallelPlates(gap_um=gap_um, width_um=40.0, height_um=40.0, thickness_um=0.05)
    grid = make_xy_grid(-2.5, 2.5, -0.5 * gap_um, 0.5 * gap_um, grid_n, grid_n)
    result = estimate_plate_pair_surface_field(geometry, grid, loops, scales, chunk_size=int(cfg["chunk_size"]))
    field = result["density_proxy"]
    proxy_mean = float(np.mean(field))
    proxy_integral = float(np.sum(field))
    proxy_peak = float(np.min(field))
    em_energy = parallel_plate_em_energy_density_J_m3(gap_um)
    scalar_energy = parallel_plate_scalar_dirichlet_energy_density_J_m3(gap_um)
    families = {
        "ideal_em": em_energy,
        "scalar_dirichlet": scalar_energy,
    }
    rows: list[dict[str, Any]] = []
    for family, energy_density in families.items():
        pressure = -3.0 * abs(energy_density)
        rows.append(
            {
                "stage": "calibration",
                "block_id": block_id,
                "seed": seed,
                "loop_hash": _sha256_array(loops),
                "gap_um": gap_um,
                "scale_window": window,
                "calibration_family": family,
                "proxy_integral": proxy_integral,
                "proxy_mean": proxy_mean,
                "proxy_peak": proxy_peak,
                "analytic_energy_density_J_m3": float(energy_density),
                "analytic_pressure_Pa": float(pressure),
                "calibration_alpha_energy": float(energy_density / proxy_mean) if proxy_mean != 0.0 else np.nan,
                "calibration_alpha_pressure": float(pressure / proxy_mean) if proxy_mean != 0.0 else np.nan,
                "elapsed_s": float(result["metadata"]["elapsed_s"]),
            }
        )
    return rows


def _sphere_geometry(cfg: Mapping[str, Any], wall: float, **overrides: Any) -> SphereInCylinder:
    sphere_diameter = float(overrides.get("sphere_diameter_um", cfg["sphere_diameter_um"]))
    cylinder_diameter = float(overrides.get("cylinder_diameter_um", cfg["cylinder_diameter_um"]))
    cylinder_length = float(overrides.get("cylinder_length_um", cfg["cylinder_length_um"]))
    sphere_offset = tuple(overrides.get("sphere_offset_um", (0.0, 0.0, 0.0)))
    readout_radius = float(overrides.get("readout_radius_um", cfg["readout_radius_um"]))
    return SphereInCylinder(
        sphere_diameter_um=sphere_diameter,
        cylinder_diameter_um=cylinder_diameter,
        cylinder_length_um=cylinder_length,
        bore_radius_um=readout_radius,
        readout_path=CentralReadoutPath(cylinder_length, readout_radius),
        wall_thickness_um=float(wall),
        sphere_offset_um=sphere_offset,
    )


def _field_for_geometry(
    geometry: SphereInCylinder,
    cfg: Mapping[str, Any],
    loops: np.ndarray,
    scale_window: str,
) -> tuple[dict[str, np.ndarray], np.ndarray, float]:
    extent = float(cfg["grid_extent_um"])
    grid = make_xy_grid(-extent, extent, -extent, extent, int(cfg["grid_n"]), int(cfg["grid_n"]))
    result = estimate_pair_surface_field(
        geometry,
        grid,
        loops,
        _scale_values(scale_window),
        chunk_size=int(cfg["chunk_size"]),
    )
    return grid, result["density_proxy"], float(result["metadata"]["elapsed_s"])


def _tensor_task(task: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    cfg = task["config"]
    block_id = int(task["block_id"])
    wall = float(task["wall_thickness_um"])
    window = str(task["scale_window"])
    seed = int(cfg["base_seed"]) + 20_000 + block_id
    loops = generate_loops(int(cfg["loops_per_block"]), int(cfg["points_per_loop"]), seed, method="v_loop")
    loop_hash = _sha256_array(loops)
    baseline_geometry = _sphere_geometry(cfg, wall)
    grid, baseline_field, baseline_elapsed = _field_for_geometry(baseline_geometry, cfg, loops, window)
    baseline_metrics = field_channel_metrics(grid, baseline_geometry, baseline_field)
    baseline_row = {
        "block_id": block_id,
        "seed": seed,
        "loop_hash": loop_hash,
        "wall_thickness_um": wall,
        "scale_window": window,
        "elapsed_s": baseline_elapsed,
        **baseline_metrics,
    }

    delta = float(cfg["finite_delta_um"])
    length_delta = float(cfg["cylinder_length_delta_um"])
    parameter_specs = [
        (
            "cylinder_inner_radius",
            delta,
            {"cylinder_diameter_um": float(cfg["cylinder_diameter_um"]) + 2.0 * delta},
            {"cylinder_diameter_um": float(cfg["cylinder_diameter_um"]) - 2.0 * delta},
        ),
        ("sphere_axial_offset", delta, {"sphere_offset_um": (delta, 0.0, 0.0)}, {"sphere_offset_um": (-delta, 0.0, 0.0)}),
        ("sphere_radial_offset", delta, {"sphere_offset_um": (0.0, delta, 0.0)}, {"sphere_offset_um": (0.0, -delta, 0.0)}),
        (
            "sphere_diameter",
            delta,
            {"sphere_diameter_um": float(cfg["sphere_diameter_um"]) + delta},
            {"sphere_diameter_um": float(cfg["sphere_diameter_um"]) - delta},
        ),
        (
            "cylinder_length",
            length_delta,
            {"cylinder_length_um": float(cfg["cylinder_length_um"]) + length_delta},
            {"cylinder_length_um": float(cfg["cylinder_length_um"]) - length_delta},
        ),
    ]

    channel_rows: list[dict[str, Any]] = []
    elapsed_total = baseline_elapsed
    for parameter, step, plus_overrides, minus_overrides in parameter_specs:
        plus_geometry = _sphere_geometry(cfg, wall, **plus_overrides)
        minus_geometry = _sphere_geometry(cfg, wall, **minus_overrides)
        _, plus_field, plus_elapsed = _field_for_geometry(plus_geometry, cfg, loops, window)
        _, minus_field, minus_elapsed = _field_for_geometry(minus_geometry, cfg, loops, window)
        elapsed_total += plus_elapsed + minus_elapsed
        plus_metrics = field_channel_metrics(grid, plus_geometry, plus_field)
        minus_metrics = field_channel_metrics(grid, minus_geometry, minus_field)
        channel_rows.extend(
            finite_difference_rows(
                baseline_metrics,
                plus_metrics,
                minus_metrics,
                parameter=parameter,
                delta_um=float(step),
                block_id=block_id,
                wall_thickness_um=wall,
                scale_window=window,
            )
        )

    readout_delta = delta
    plus_readout = _sphere_geometry(cfg, wall, readout_radius_um=float(cfg["readout_radius_um"]) + readout_delta)
    minus_readout = _sphere_geometry(cfg, wall, readout_radius_um=max(float(cfg["readout_radius_um"]) - readout_delta, 1.0e-6))
    plus_readout_metrics = field_channel_metrics(grid, plus_readout, baseline_field)
    minus_readout_metrics = field_channel_metrics(grid, minus_readout, baseline_field)
    channel_rows.extend(
        finite_difference_rows(
            baseline_metrics,
            plus_readout_metrics,
            minus_readout_metrics,
            parameter="readout_accounting_radius",
            delta_um=readout_delta,
            block_id=block_id,
            wall_thickness_um=wall,
            scale_window=window,
        )
    )

    for row in channel_rows:
        row["seed"] = seed
        row["loop_hash"] = loop_hash
    baseline_row["elapsed_s"] = elapsed_total
    return {"baseline_rows": [baseline_row], "channel_rows": channel_rows}


def _summarize_calibration(frame: pd.DataFrame) -> pd.DataFrame:
    def safe_median(series: pd.Series) -> float:
        values = series.astype(float).dropna()
        return float(values.median()) if not values.empty else float("nan")

    def safe_std(series: pd.Series) -> float:
        values = series.astype(float).dropna()
        return float(values.std(ddof=0)) if not values.empty else float("nan")

    grouped = frame.groupby(["gap_um", "scale_window", "calibration_family"], dropna=False)
    rows: list[dict[str, Any]] = []
    for keys, group in grouped:
        rows.append(
            {
                "gap_um": keys[0],
                "scale_window": keys[1],
                "calibration_family": keys[2],
                "n_blocks": int(len(group)),
                "proxy_mean_median": safe_median(group["proxy_mean"]),
                "proxy_mean_std": safe_std(group["proxy_mean"]),
                "proxy_integral_median": safe_median(group["proxy_integral"]),
                "proxy_peak_median": safe_median(group["proxy_peak"]),
                "analytic_energy_density_J_m3": safe_median(group["analytic_energy_density_J_m3"]),
                "analytic_pressure_Pa": safe_median(group["analytic_pressure_Pa"]),
                "calibration_alpha_energy_median": safe_median(group["calibration_alpha_energy"]),
                "calibration_alpha_energy_std": safe_std(group["calibration_alpha_energy"]),
                "calibration_alpha_pressure_median": safe_median(group["calibration_alpha_pressure"]),
                "bootstrap_std": safe_std(group["calibration_alpha_energy"]),
            }
        )
    summary = pd.DataFrame(rows)
    if summary.empty:
        return summary
    summary["gap_ordering_pass"] = False
    for (window, family), idx in summary.groupby(["scale_window", "calibration_family"]).groups.items():
        subset = summary.loc[idx].sort_values("gap_um")
        magnitudes = np.abs(subset["proxy_mean_median"].to_numpy(dtype=float))
        pass_order = bool(np.all(np.diff(magnitudes) <= 1.0e-12))
        summary.loc[idx, "gap_ordering_pass"] = pass_order
    return summary


def _near_shell_volume_m3(sphere_diameter_um: float, shell_thickness_um: float = 0.75) -> float:
    r_inner_m = 0.5 * sphere_diameter_um * 1.0e-6
    r_outer_m = (0.5 * sphere_diameter_um + shell_thickness_um) * 1.0e-6
    return (4.0 / 3.0) * np.pi * (r_outer_m**3 - r_inner_m**3)


def _scale_and_competitor_rows(
    cfg: HarnessConfig,
    calibration_summary: pd.DataFrame,
    baseline_frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    material_rows: list[dict[str, Any]] = []
    readout_rows: list[dict[str, Any]] = []

    shell_volume = _near_shell_volume_m3(cfg.sphere_diameter_um)
    if baseline_frame.empty or calibration_summary.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    for _, cal in calibration_summary.iterrows():
        window = str(cal["scale_window"])
        family = str(cal["calibration_family"])
        alpha_energy = float(cal["calibration_alpha_energy_median"])
        alpha_pressure = float(cal["calibration_alpha_pressure_median"])
        baseline_subset = baseline_frame[baseline_frame["scale_window"] == window]
        if baseline_subset.empty:
            continue
        proxy_mean = float(baseline_subset["source_shell_candidate_signed_mean"].median())
        readout_fraction = float(baseline_subset["transit_readout_channel_negative_magnitude_fraction"].median())
        shell_fraction = float(baseline_subset["source_shell_candidate_negative_magnitude_fraction"].median())
        far_fraction = float(baseline_subset["far_field_leakage_fraction"].median())
        rho_mid = alpha_energy * proxy_mean
        pressure_mid = alpha_pressure * proxy_mean
        for material_factor in cfg.material_factors:
            rho = rho_mid * material_factor
            pressure = pressure_mid * material_factor
            integrated_energy = rho * shell_volume
            readout_energy = integrated_energy * readout_fraction
            source_rows.extend(
                build_target_grid(
                    rho_mid,
                    material_factor=material_factor,
                    calibration_family=f"{family}:{window}:material_{material_factor:g}",
                )
            )
            metric_rows.append(
                {
                    "calibration_family": family,
                    "scale_window": window,
                    "material_factor": material_factor,
                    "energy_density_J_m3_mid": rho,
                    "pressure_Pa_mid": pressure,
                    "shell_volume_m3": shell_volume,
                    "integrated_shell_energy_J": integrated_energy,
                    "readout_path_energy_coupling_J": readout_energy,
                    **estimate_timing_bound(readout_energy, cfg.cylinder_length_um, coupling_fraction=1.0),
                }
            )
            readout_rows.append(
                {
                    "calibration_family": family,
                    "scale_window": window,
                    "material_factor": material_factor,
                    "readout_source_fraction": readout_fraction,
                    "shell_channel_fraction": shell_fraction,
                    "shell_to_readout_channel_ratio": shell_fraction / readout_fraction
                    if readout_fraction > 0.0
                    else float("inf")
                    if shell_fraction > 0.0
                    else 0.0,
                    "readout_channel_nonzero": bool(readout_fraction > 0.0),
                    "far_field_leakage_fraction": far_fraction,
                    "readout_calibrated_energy_coupling_J": readout_energy,
                }
            )
            material_rows.extend(
                {
                    **row,
                    "calibration_family": family,
                    "scale_window": window,
                    "material_factor": material_factor,
                }
                for row in estimate_em_competitors(
                    integrated_energy,
                    sphere_diameter_um=cfg.sphere_diameter_um,
                    cylinder_diameter_um=cfg.cylinder_diameter_um,
                    cylinder_length_um=cfg.cylinder_length_um,
                    wall_thickness_um=float(np.median(cfg.wall_thicknesses_um)),
                    readout_radius_um=cfg.readout_radius_um,
                )
            )
    return pd.DataFrame(source_rows), pd.DataFrame(metric_rows), pd.DataFrame(material_rows), pd.DataFrame(readout_rows)


def _write_manifest(outdir: Path, cfg: HarnessConfig) -> None:
    payload = {
        "run_id": cfg.run_id,
        "stage": "stage3_tensor_scale_probe",
        "proxy_boundary": "finite_difference_stress_channel_proxy_not_worldline_stress_tensor",
        "git_commit": _git_commit(),
        "config": asdict(cfg),
        "output_categories": [
            "normalized_morphology_proxy",
            "calibrated_energy_density_bracket",
            "finite_difference_stress_channel_proxy",
            "source_demand_ratio",
            "linearized_metric_scale_bound",
            "ordinary_em_proxy",
        ],
    }
    _write_json(outdir / "manifest.json", payload)
    _write_json(outdir / "configs" / "run_config.json", asdict(cfg))


def _task_total(cfg: HarnessConfig) -> int:
    return (
        cfg.loop_blocks * len(cfg.calibration_gaps_um) * len(cfg.scale_windows)
        + cfg.loop_blocks * len(cfg.wall_thicknesses_um) * len(cfg.scale_windows)
    )


def run_tensor_scale_harness(outdir: Path, cfg: HarnessConfig) -> dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    for subdir in ("calibration", "tensor", "scale", "material", "readout", "audit", "configs", "reports"):
        (outdir / subdir).mkdir(parents=True, exist_ok=True)
    _write_manifest(outdir, cfg)

    recorder = ProgressRecorder(outdir, _task_total(cfg))
    cfg_payload = asdict(cfg)
    recorder.record("run_start", {"label": cfg.run_id, "preset": cfg.preset})

    calibration_tasks = [
        {"config": cfg_payload, "block_id": block, "gap_um": gap, "scale_window": window}
        for block in range(cfg.loop_blocks)
        for gap in cfg.calibration_gaps_um
        for window in cfg.scale_windows
    ]
    calibration_rows: list[dict[str, Any]] = []
    mp_context = mp.get_context("spawn")
    with ProcessPoolExecutor(max_workers=cfg.workers, mp_context=mp_context) as executor:
        futures = [executor.submit(_calibration_task, task) for task in calibration_tasks]
        for future in as_completed(futures):
            rows = future.result()
            calibration_rows.extend(rows)
            first = rows[0]
            recorder.record(
                "calibration_block_complete",
                {
                    "label": f"gap={first['gap_um']} window={first['scale_window']} block={first['block_id']}",
                    "proxy_mean": first["proxy_mean"],
                },
            )

    calibration_points = pd.DataFrame(calibration_rows)
    calibration_summary = _summarize_calibration(calibration_points)
    _write_frame(outdir / "calibration" / "calibration_points.parquet", calibration_points)
    _write_frame(outdir / "calibration" / "calibration_summary.csv", calibration_summary)
    recorder.record(
        "calibration_stage_summary",
        {
            "label": "calibration summary",
            "gap_ordering_all_pass": bool(calibration_summary["gap_ordering_pass"].all())
            if not calibration_summary.empty
            else False,
        },
    )

    tensor_tasks = [
        {"config": cfg_payload, "block_id": block, "wall_thickness_um": wall, "scale_window": window}
        for block in range(cfg.loop_blocks)
        for wall in cfg.wall_thicknesses_um
        for window in cfg.scale_windows
    ]
    baseline_rows: list[dict[str, Any]] = []
    channel_rows: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=cfg.workers, mp_context=mp_context) as executor:
        futures = [executor.submit(_tensor_task, task) for task in tensor_tasks]
        for future in as_completed(futures):
            result = future.result()
            baseline_rows.extend(result["baseline_rows"])
            channel_rows.extend(result["channel_rows"])
            first = result["baseline_rows"][0]
            recorder.record(
                "tensor_block_complete",
                {
                    "label": f"wall={first['wall_thickness_um']} window={first['scale_window']} block={first['block_id']}",
                    "shell_fraction": first["source_shell_candidate_negative_magnitude_fraction"],
                    "readout_fraction": first["transit_readout_channel_negative_magnitude_fraction"],
                },
            )

    baseline_frame = pd.DataFrame(baseline_rows)
    channel_frame = pd.DataFrame(channel_rows)
    bootstrap_summary = summarize_bootstrap(channel_rows)
    _write_frame(outdir / "tensor" / "stress_channel_points.parquet", channel_frame)
    _write_frame(outdir / "tensor" / "stress_channel_baseline_blocks.parquet", baseline_frame)
    _write_frame(outdir / "tensor" / "bootstrap_summary.csv", bootstrap_summary)
    stress_summary = (
        bootstrap_summary[
            bootstrap_summary["channel"].isin(
                [
                    "signed_integral",
                    "source_shell_candidate_signed_integral",
                    "transit_readout_channel_signed_integral",
                    "far_field_control_signed_integral",
                ]
            )
        ]
        if not bootstrap_summary.empty
        else bootstrap_summary
    )
    _write_frame(outdir / "tensor" / "stress_channel_summary.csv", stress_summary)

    source_frame, metric_frame, material_frame, readout_frame = _scale_and_competitor_rows(
        cfg,
        calibration_summary,
        baseline_frame,
    )
    _write_frame(outdir / "scale" / "source_demand_ratio.csv", source_frame)
    _write_frame(outdir / "scale" / "linearized_metric_bound.csv", metric_frame)
    _write_frame(outdir / "material" / "material_competitor_summary.csv", material_frame)
    _write_frame(outdir / "readout" / "readout_coupling_summary.csv", readout_frame)

    final_summary = {
        "run_id": cfg.run_id,
        "outdir": str(outdir),
        "calibration_gap_ordering_all_pass": bool(calibration_summary["gap_ordering_pass"].all())
        if not calibration_summary.empty
        else False,
        "tensor_blocks": int(len(baseline_frame)),
        "stress_channel_rows": int(len(channel_frame)),
        "source_demand_rows": int(len(source_frame)),
        "material_rows": int(len(material_frame)),
        "proxy_boundary": "finite_difference_stress_channel_proxy_not_worldline_stress_tensor",
    }
    _write_json(outdir / "summary.json", final_summary)
    recorder.record("run_complete", {"label": cfg.run_id, **final_summary})
    return final_summary


def config_from_args(args: argparse.Namespace) -> HarnessConfig:
    preset = PRESETS[args.preset].copy()
    for key in ("grid_n", "loop_blocks", "loops_per_block", "points_per_loop", "workers", "chunk_size"):
        value = getattr(args, key)
        if value is not None:
            preset[key] = value
    run_id = args.run_id or f"stage3_{args.preset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return HarnessConfig(
        preset=args.preset,
        run_id=run_id,
        grid_n=int(preset["grid_n"]),
        grid_extent_um=float(args.grid_extent_um),
        loop_blocks=int(preset["loop_blocks"]),
        loops_per_block=int(preset["loops_per_block"]),
        points_per_loop=int(preset["points_per_loop"]),
        workers=int(preset["workers"]),
        chunk_size=int(preset["chunk_size"]),
        base_seed=int(args.base_seed),
        wall_thicknesses_um=tuple(float(v) for v in args.wall_thicknesses_um),
        scale_windows=tuple(args.scale_windows),
        calibration_gaps_um=tuple(float(v) for v in args.calibration_gaps_um),
        material_factors=tuple(float(v) for v in args.material_factors),
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Stage 3 White tensor-scale proxy harness.")
    parser.add_argument("--preset", choices=tuple(PRESETS), default="smoke")
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--grid-n", type=int, default=None)
    parser.add_argument("--grid-extent-um", type=float, default=2.5)
    parser.add_argument("--loop-blocks", type=int, default=None)
    parser.add_argument("--loops-per-block", type=int, default=None)
    parser.add_argument("--points-per-loop", type=int, default=None)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--base-seed", type=int, default=1)
    parser.add_argument("--wall-thicknesses-um", type=float, nargs="+", default=list(WALL_THICKNESSES_UM))
    parser.add_argument("--scale-windows", choices=tuple(SCALE_WINDOWS), nargs="+", default=list(SCALE_WINDOWS))
    parser.add_argument("--calibration-gaps-um", type=float, nargs="+", default=list(CALIBRATION_GAPS_UM))
    parser.add_argument("--material-factors", type=float, nargs="+", default=list(MATERIAL_FACTORS))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    cfg = config_from_args(args)
    base_outdir = args.outdir
    if base_outdir is None:
        base_outdir = DEFAULT_EXTERNAL_BASE / cfg.run_id
    summary = run_tensor_scale_harness(base_outdir.resolve(), cfg)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
