"""V-loop spatial-discrimination runner for the sphere-cylinder proxy."""

from __future__ import annotations

import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np

from .geometry import SphereInCylinder, make_xy_grid
from .loop_gen import generate_loops
from .worldline_scalar import estimate_density_proxy

DEFAULT_SCALE_WINDOWS = {
    "low_0p25_0p75": (0.25, 0.75, 8),
    "mid_0p75_1p50": (0.75, 1.50, 8),
    "upper_1p50_2p75": (1.50, 2.75, 8),
    "broad_0p25_5p00": (0.25, 5.00, 20),
}

AGGREGATE_FIELDS = (
    "negative_fraction",
    "near_shell_mag_fraction",
    "near_shell_enrichment",
    "top_decile_near_shell_fraction",
    "boundary_mag_fraction",
    "far_mag_fraction",
    "readout_mag_fraction",
    "min_radius_from_sphere_um",
    "peak_radial_bin_mid_um",
)


def _scale_window_values(name: str) -> np.ndarray:
    start, stop, count = DEFAULT_SCALE_WINDOWS[name]
    return np.linspace(start, stop, int(count))


def _positive_top_mask(negative_magnitude: np.ndarray, percentile: float = 90.0) -> np.ndarray:
    positive = negative_magnitude[negative_magnitude > 0.0]
    if positive.size == 0:
        return np.zeros_like(negative_magnitude, dtype=bool)
    threshold = float(np.percentile(positive, percentile))
    return negative_magnitude >= threshold


def _fraction(part: float, whole: float) -> float:
    return float(part / whole) if whole > 0.0 else 0.0


def _mean_masked(values: np.ndarray, mask: np.ndarray) -> float:
    return float(np.mean(values[mask])) if np.any(mask) else 0.0


def _field_metrics(
    grid: dict[str, np.ndarray],
    geometry: SphereInCylinder,
    field: np.ndarray,
) -> dict[str, Any]:
    finite = np.asarray(field, dtype=float)
    negative_magnitude = np.maximum(-finite, 0.0)
    total_negative = float(np.sum(negative_magnitude))
    top_mask = _positive_top_mask(negative_magnitude)
    top_count = int(np.count_nonzero(top_mask))

    x = grid["x"]
    y = grid["y"]
    z = grid["z"]
    ox, oy, oz = geometry.sphere_offset_um
    sphere_radius = geometry.sphere_radius_um
    cylinder_radius = geometry.cylinder_radius_um
    sphere_r = np.sqrt((x - ox) ** 2 + (y - oy) ** 2 + (z - oz) ** 2)
    transverse = np.hypot(y, z)

    roles = geometry.role_regions(grid)
    source_role = roles["source_shell_candidate"]
    boundary_role = roles["boundary_infrastructure"]
    far_role = roles["far_field_control"]
    readout_role = roles["transit_readout_channel"]

    near_shell = (
        (sphere_r > sphere_radius)
        & (sphere_r <= sphere_radius + 0.75)
        & (transverse < cylinder_radius - 0.10)
    )
    mid_gap = (
        (sphere_r > sphere_radius + 0.75)
        & (sphere_r <= sphere_radius + 1.25)
        & (transverse < cylinder_radius - 0.10)
    )
    wall_band = (transverse >= cylinder_radius - 0.25) & (transverse <= cylinder_radius + 0.25)
    central_axis = transverse <= 0.15

    min_index = np.unravel_index(int(np.nanargmin(finite)), finite.shape)
    radial_bins = np.asarray([0.0, 0.5, 0.75, 1.0, 1.25, 1.50, 1.75, 2.0, 2.25, 2.5, 3.0])
    radial_profile: list[dict[str, float]] = []
    for lo, hi in zip(radial_bins[:-1], radial_bins[1:], strict=True):
        mask = (sphere_r >= lo) & (sphere_r < hi)
        radial_profile.append(
            {
                "r_min_um": float(lo),
                "r_max_um": float(hi),
                "mean_negative_magnitude": _mean_masked(negative_magnitude, mask),
                "negative_mag_fraction": _fraction(float(np.sum(negative_magnitude[mask])), total_negative),
                "area_fraction": _fraction(float(np.count_nonzero(mask)), float(mask.size)),
            }
        )
    peak_bin = max(radial_profile, key=lambda row: row["mean_negative_magnitude"])
    peak_radial_mid = 0.5 * (peak_bin["r_min_um"] + peak_bin["r_max_um"])

    def mag_fraction(mask: np.ndarray) -> float:
        return _fraction(float(np.sum(negative_magnitude[mask])), total_negative)

    def top_fraction(mask: np.ndarray) -> float:
        return _fraction(float(np.count_nonzero(top_mask & mask)), float(top_count))

    near_shell_mean = _mean_masked(negative_magnitude, near_shell)
    non_shell_mean = _mean_masked(negative_magnitude, ~near_shell)
    source_mean = _mean_masked(negative_magnitude, source_role)
    non_source_mean = _mean_masked(negative_magnitude, ~source_role)

    return {
        "min": float(np.nanmin(finite)),
        "mean": float(np.nanmean(finite)),
        "negative_fraction": _fraction(float(np.count_nonzero(finite < 0.0)), float(finite.size)),
        "contrast_abs_min_to_abs_mean": float(abs(np.nanmin(finite)) / max(abs(np.nanmean(finite)), 1.0e-12)),
        "min_x_um": float(x[min_index]),
        "min_section_um": float(y[min_index]),
        "min_radius_from_sphere_um": float(sphere_r[min_index]),
        "source_role_area_fraction": _fraction(float(np.count_nonzero(source_role)), float(source_role.size)),
        "source_role_mag_fraction": mag_fraction(source_role),
        "source_role_enrichment": float(source_mean / max(non_source_mean, 1.0e-12)),
        "near_shell_area_fraction": _fraction(float(np.count_nonzero(near_shell)), float(near_shell.size)),
        "near_shell_mag_fraction": mag_fraction(near_shell),
        "near_shell_enrichment": float(near_shell_mean / max(non_shell_mean, 1.0e-12)),
        "mid_gap_mag_fraction": mag_fraction(mid_gap),
        "wall_band_mag_fraction": mag_fraction(wall_band),
        "boundary_mag_fraction": mag_fraction(boundary_role),
        "far_mag_fraction": mag_fraction(far_role),
        "readout_mag_fraction": mag_fraction(readout_role),
        "central_axis_mag_fraction": mag_fraction(central_axis),
        "top_decile_near_shell_fraction": top_fraction(near_shell),
        "top_decile_source_role_fraction": top_fraction(source_role),
        "top_decile_boundary_fraction": top_fraction(boundary_role),
        "top_decile_far_fraction": top_fraction(far_role),
        "top_decile_count": top_count,
        "peak_radial_bin_mid_um": float(peak_radial_mid),
        "radial_profile": radial_profile,
    }


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    seed = int(case["seed"])
    wall_thickness_um = float(case["wall_thickness_um"])
    scale_window = str(case["scale_window"])
    n_loops = int(case["n_loops"])
    n_points = int(case["n_points_per_loop"])
    grid_n = int(case["grid_n"])
    grid_extent_um = float(case["grid_extent_um"])

    grid = make_xy_grid(-grid_extent_um, grid_extent_um, -grid_extent_um, grid_extent_um, grid_n, grid_n)
    geometry = SphereInCylinder(
        sphere_diameter_um=1.0,
        cylinder_diameter_um=4.0,
        cylinder_length_um=8.0,
        bore_radius_um=0.05,
        wall_thickness_um=wall_thickness_um,
    )
    loops = generate_loops(n_loops, n_points, seed, method="v_loop")
    scales = _scale_window_values(scale_window)
    result = estimate_density_proxy(
        geometry,
        grid,
        loops,
        scales,
        loop_method="v_loop",
        random_seed=seed,
    )
    return {
        "seed": seed,
        "wall_thickness_um": wall_thickness_um,
        "scale_window": scale_window,
        "n_loops": n_loops,
        "n_points_per_loop": n_points,
        "grid_n": grid_n,
        "grid_extent_um": grid_extent_um,
        "n_scales": int(len(scales)),
        "scale_min_um": float(scales[0]),
        "scale_max_um": float(scales[-1]),
        "elapsed_s": float(result["metadata"]["elapsed_s"]),
        **_field_metrics(grid, geometry, result["density_proxy"]),
    }


def _aggregate_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, float], list[dict[str, Any]]] = {}
    for row in cases:
        grouped.setdefault((str(row["scale_window"]), float(row["wall_thickness_um"])), []).append(row)

    aggregates: list[dict[str, Any]] = []
    for (scale_window, wall_thickness_um), rows in sorted(grouped.items()):
        summary: dict[str, Any] = {
            "scale_window": scale_window,
            "wall_thickness_um": wall_thickness_um,
            "n_cases": len(rows),
            "seeds": [int(row["seed"]) for row in rows],
        }
        for field in AGGREGATE_FIELDS:
            values = np.asarray([float(row[field]) for row in rows], dtype=float)
            summary[f"{field}_mean"] = float(np.mean(values))
            summary[f"{field}_std"] = float(np.std(values))
            summary[f"{field}_min"] = float(np.min(values))
            summary[f"{field}_max"] = float(np.max(values))
        aggregates.append(summary)
    return aggregates


def _write_cases_csv(path: Path, cases: list[dict[str, Any]]) -> None:
    scalar_keys = [
        key
        for key, value in cases[0].items()
        if not isinstance(value, (list, dict))
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=scalar_keys)
        writer.writeheader()
        for row in cases:
            writer.writerow({key: row[key] for key in scalar_keys})


def run_spatial_discrimination(
    base_dir: Path,
    seeds: tuple[int, ...] = (1, 7, 17),
    wall_thicknesses_um: tuple[float, ...] = (0.2, 0.4),
    scale_windows: tuple[str, ...] = tuple(DEFAULT_SCALE_WINDOWS),
    n_loops: int = 128,
    n_points_per_loop: int = 200,
    grid_n: int = 41,
    grid_extent_um: float = 2.5,
    workers: int = 4,
) -> dict[str, Any]:
    outputs_dir = base_dir / "outputs" / "spatial_discrimination"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    requested_cases = [
        {
            "seed": seed,
            "wall_thickness_um": wall,
            "scale_window": scale_window,
            "n_loops": n_loops,
            "n_points_per_loop": n_points_per_loop,
            "grid_n": grid_n,
            "grid_extent_um": grid_extent_um,
        }
        for seed in seeds
        for wall in wall_thicknesses_um
        for scale_window in scale_windows
    ]

    cases: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_case, case) for case in requested_cases]
        for future in as_completed(futures):
            cases.append(future.result())
    cases.sort(key=lambda row: (row["scale_window"], row["wall_thickness_um"], row["seed"]))

    aggregate = _aggregate_cases(cases)
    summary = {
        "stage": "stage2_vloop_spatial_discrimination",
        "proxy_status": "paper_style_v_loop_morphology_proxy_not_si_normalized",
        "parameters": {
            "seeds": list(seeds),
            "wall_thicknesses_um": list(wall_thicknesses_um),
            "scale_windows": {
                name: {
                    "start_um": DEFAULT_SCALE_WINDOWS[name][0],
                    "stop_um": DEFAULT_SCALE_WINDOWS[name][1],
                    "count": DEFAULT_SCALE_WINDOWS[name][2],
                }
                for name in scale_windows
            },
            "n_loops": n_loops,
            "n_points_per_loop": n_points_per_loop,
            "grid_n": grid_n,
            "grid_extent_um": grid_extent_um,
            "workers": workers,
        },
        "cases": cases,
        "aggregate_by_window_wall": aggregate,
        "control_note": "Single-body sphere-only and cylinder-only controls are identically zero under this multi-body scalar contact proxy.",
    }
    (outputs_dir / "stage2_vloop_spatial_discrimination_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_cases_csv(outputs_dir / "stage2_vloop_spatial_discrimination_cases.csv", cases)
    return summary


def _parse_args() -> argparse.Namespace:
    default_base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Run v-loop spatial-discrimination sweeps.")
    parser.add_argument("--base-dir", type=Path, default=default_base)
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 7, 17])
    parser.add_argument("--wall-thicknesses-um", type=float, nargs="+", default=[0.2, 0.4])
    parser.add_argument("--scale-windows", choices=tuple(DEFAULT_SCALE_WINDOWS), nargs="+", default=list(DEFAULT_SCALE_WINDOWS))
    parser.add_argument("--n-loops", type=int, default=128)
    parser.add_argument("--n-points-per-loop", type=int, default=200)
    parser.add_argument("--grid-n", type=int, default=41)
    parser.add_argument("--grid-extent-um", type=float, default=2.5)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    summary = run_spatial_discrimination(
        base_dir=args.base_dir.resolve(),
        seeds=tuple(args.seeds),
        wall_thicknesses_um=tuple(args.wall_thicknesses_um),
        scale_windows=tuple(args.scale_windows),
        n_loops=args.n_loops,
        n_points_per_loop=args.n_points_per_loop,
        grid_n=args.grid_n,
        grid_extent_um=args.grid_extent_um,
        workers=args.workers,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
