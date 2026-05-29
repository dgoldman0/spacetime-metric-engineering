"""Final sphere-cylinder fidelity probe for the White Casimir audit."""

from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np

from .geometry import SphereInCylinder, make_xy_grid
from .loop_gen import generate_loops
from .spatial_discrimination import _field_metrics

FIDELITY_SCALE_WINDOWS = {
    "mid_0p75_1p50": (0.75, 1.50, 8),
    "upper_1p50_2p75": (1.50, 2.75, 8),
    "broad_0p25_5p00": (0.25, 5.00, 20),
}

GEOMETRY_VARIANTS = {
    "baseline": {"sphere_diameter_um": 1.0, "cylinder_diameter_um": 4.0},
    "sphere_0p9": {"sphere_diameter_um": 0.9, "cylinder_diameter_um": 4.0},
    "sphere_1p1": {"sphere_diameter_um": 1.1, "cylinder_diameter_um": 4.0},
    "cylinder_3p8": {"sphere_diameter_um": 1.0, "cylinder_diameter_um": 3.8},
    "cylinder_4p2": {"sphere_diameter_um": 1.0, "cylinder_diameter_um": 4.2},
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


def _window_values(name: str) -> np.ndarray:
    start, stop, count = FIDELITY_SCALE_WINDOWS[name]
    return np.linspace(start, stop, int(count))


def _loop_segments(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 3 or arr.shape[-1] != 3:
        raise ValueError("points must have shape (n_loops, n_points, 3)")
    return arr, np.roll(arr, -1, axis=1)


def loop_hits_sphere_surface(
    points: np.ndarray,
    radius_um: float,
    center_um: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> np.ndarray:
    """Return per-loop exact segment/sphere-surface crossing flags."""

    p0, p1 = _loop_segments(points)
    center = np.asarray(center_um, dtype=float)
    d = p1 - p0
    f = p0 - center[None, None, :]
    a = np.sum(d * d, axis=-1)
    b = 2.0 * np.sum(f * d, axis=-1)
    c = np.sum(f * f, axis=-1) - float(radius_um) ** 2
    disc = b * b - 4.0 * a * c
    valid = (a > 1.0e-15) & (disc >= 0.0)
    sqrt_disc = np.sqrt(np.maximum(disc, 0.0))
    denom = 2.0 * np.where(a > 1.0e-15, a, 1.0)
    t0 = (-b - sqrt_disc) / denom
    t1 = (-b + sqrt_disc) / denom
    segment_hit = valid & (((t0 >= 0.0) & (t0 <= 1.0)) | ((t1 >= 0.0) & (t1 <= 1.0)))
    return np.any(segment_hit, axis=1)


def loop_hits_cylinder_surface(
    points: np.ndarray,
    radius_um: float,
    half_length_um: float,
) -> np.ndarray:
    """Return per-loop exact segment/cylindrical-surface crossing flags."""

    p0, p1 = _loop_segments(points)
    d = p1 - p0
    y0 = p0[..., 1]
    z0 = p0[..., 2]
    dy = d[..., 1]
    dz = d[..., 2]
    a = dy * dy + dz * dz
    b = 2.0 * (y0 * dy + z0 * dz)
    c = y0 * y0 + z0 * z0 - float(radius_um) ** 2
    disc = b * b - 4.0 * a * c
    valid = (a > 1.0e-15) & (disc >= 0.0)
    sqrt_disc = np.sqrt(np.maximum(disc, 0.0))
    denom = 2.0 * np.where(a > 1.0e-15, a, 1.0)
    t0 = (-b - sqrt_disc) / denom
    t1 = (-b + sqrt_disc) / denom

    def root_valid(t: np.ndarray) -> np.ndarray:
        x_at_t = p0[..., 0] + t * d[..., 0]
        return (t >= 0.0) & (t <= 1.0) & (np.abs(x_at_t) <= half_length_um)

    segment_hit = valid & (root_valid(t0) | root_valid(t1))
    return np.any(segment_hit, axis=1)


def _chunk_pair_counts(
    centers: np.ndarray,
    loops: np.ndarray,
    scales: np.ndarray,
    sphere_radius_um: float,
    sphere_center_um: tuple[float, float, float],
    cylinder_inner_radius_um: float,
    cylinder_half_length_um: float,
    chunk_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    values = np.zeros(len(centers), dtype=float)
    touch_counts = np.zeros(len(centers), dtype=np.int32)
    loop_starts = loops
    loop_ends = np.roll(loops, -1, axis=1)
    segment_delta = loop_ends - loop_starts
    sphere_center = np.asarray(sphere_center_um, dtype=float)

    for start in range(0, len(centers), chunk_size):
        stop = min(start + chunk_size, len(centers))
        center_chunk = centers[start:stop]
        chunk_score = np.zeros(stop - start, dtype=float)
        chunk_touches = np.zeros(stop - start, dtype=np.int32)

        for scale in scales:
            p0 = center_chunk[:, None, None, :] + scale * loop_starts[None, :, :, :]
            d = scale * segment_delta[None, :, :, :]

            sphere_hits = _batched_sphere_hits(p0, d, sphere_radius_um, sphere_center)
            cylinder_hits = _batched_cylinder_hits(p0, d, cylinder_inner_radius_um, cylinder_half_length_um)
            pair_hits = sphere_hits & cylinder_hits
            counts = np.count_nonzero(pair_hits, axis=1)
            chunk_touches += counts.astype(np.int32)
            chunk_score -= counts.astype(float) / float(scale**4)

            del p0, d, sphere_hits, cylinder_hits, pair_hits

        values[start:stop] = chunk_score / max(loops.shape[0], 1)
        touch_counts[start:stop] = chunk_touches
    return values, touch_counts


def _batched_sphere_hits(
    p0: np.ndarray,
    d: np.ndarray,
    radius_um: float,
    center: np.ndarray,
) -> np.ndarray:
    f = p0 - center[None, None, None, :]
    a = np.sum(d * d, axis=-1)
    b = 2.0 * np.sum(f * d, axis=-1)
    c = np.sum(f * f, axis=-1) - float(radius_um) ** 2
    disc = b * b - 4.0 * a * c
    valid = (a > 1.0e-15) & (disc >= 0.0)
    sqrt_disc = np.sqrt(np.maximum(disc, 0.0))
    denom = 2.0 * np.where(a > 1.0e-15, a, 1.0)
    t0 = (-b - sqrt_disc) / denom
    t1 = (-b + sqrt_disc) / denom
    segment_hit = valid & (((t0 >= 0.0) & (t0 <= 1.0)) | ((t1 >= 0.0) & (t1 <= 1.0)))
    return np.any(segment_hit, axis=2)


def _batched_cylinder_hits(
    p0: np.ndarray,
    d: np.ndarray,
    radius_um: float,
    half_length_um: float,
) -> np.ndarray:
    y0 = p0[..., 1]
    z0 = p0[..., 2]
    dy = d[..., 1]
    dz = d[..., 2]
    a = dy * dy + dz * dz
    b = 2.0 * (y0 * dy + z0 * dz)
    c = y0 * y0 + z0 * z0 - float(radius_um) ** 2
    disc = b * b - 4.0 * a * c
    valid = (a > 1.0e-15) & (disc >= 0.0)
    sqrt_disc = np.sqrt(np.maximum(disc, 0.0))
    denom = 2.0 * np.where(a > 1.0e-15, a, 1.0)
    t0 = (-b - sqrt_disc) / denom
    t1 = (-b + sqrt_disc) / denom

    x0 = p0[..., 0]
    dx = d[..., 0]
    x_at_t0 = x0 + t0 * dx
    x_at_t1 = x0 + t1 * dx
    root0 = (t0 >= 0.0) & (t0 <= 1.0) & (np.abs(x_at_t0) <= half_length_um)
    root1 = (t1 >= 0.0) & (t1 <= 1.0) & (np.abs(x_at_t1) <= half_length_um)
    segment_hit = valid & (root0 | root1)
    return np.any(segment_hit, axis=2)


def estimate_pair_surface_field(
    geometry: SphereInCylinder,
    grid: dict[str, np.ndarray],
    loops: np.ndarray,
    scale_grid: np.ndarray,
    chunk_size: int = 32,
) -> dict[str, Any]:
    centers = np.stack([grid["x"], grid["y"], grid["z"]], axis=-1).reshape(-1, 3)
    scales = np.asarray(scale_grid, dtype=float)
    cylinder_inner_radius = geometry.cylinder_radius_um - 0.5 * geometry.wall_thickness_um
    if cylinder_inner_radius <= geometry.sphere_radius_um:
        raise ValueError("cylinder inner radius must exceed sphere radius")

    start = time.perf_counter()
    values, touch_counts = _chunk_pair_counts(
        centers=centers,
        loops=np.asarray(loops, dtype=float),
        scales=scales,
        sphere_radius_um=geometry.sphere_radius_um,
        sphere_center_um=geometry.sphere_offset_um,
        cylinder_inner_radius_um=cylinder_inner_radius,
        cylinder_half_length_um=0.5 * geometry.cylinder_length_um,
        chunk_size=chunk_size,
    )
    elapsed_s = time.perf_counter() - start
    shape = grid["x"].shape
    loop_scale_tests = int(len(centers) * len(scales) * loops.shape[0])
    return {
        "density_proxy": values.reshape(shape),
        "touch_count": touch_counts.reshape(shape),
        "metadata": {
            "kernel": "pair_resolved_segment_surface_sphere_inner_cylinder",
            "loop_method": "v_loop",
            "normalization": "normalized_morphology_proxy_not_si_normalized",
            "sphere_radius_um": float(geometry.sphere_radius_um),
            "cylinder_inner_radius_um": float(cylinder_inner_radius),
            "cylinder_half_length_um": float(0.5 * geometry.cylinder_length_um),
            "scale_grid": [float(value) for value in scales],
            "elapsed_s": float(elapsed_s),
            "grid_points": int(len(centers)),
            "loop_scale_tests": loop_scale_tests,
            "loop_scale_tests_per_s": float(loop_scale_tests / max(elapsed_s, 1.0e-12)),
        },
    }


def _case_set(
    baseline_seeds: tuple[int, ...],
    perturbation_seed: int,
    wall_thicknesses_um: tuple[float, ...],
    baseline_windows: tuple[str, ...],
    perturbation_windows: tuple[str, ...],
    n_loops: int,
    n_points_per_loop: int,
    grid_n: int,
    grid_extent_um: float,
    chunk_size: int,
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for seed in baseline_seeds:
        for wall in wall_thicknesses_um:
            for window in baseline_windows:
                cases.append(
                    {
                        "geometry_label": "baseline",
                        "seed": seed,
                        "wall_thickness_um": wall,
                        "scale_window": window,
                    }
                )
    for label in GEOMETRY_VARIANTS:
        if label == "baseline":
            continue
        for wall in wall_thicknesses_um:
            for window in perturbation_windows:
                cases.append(
                    {
                        "geometry_label": label,
                        "seed": perturbation_seed,
                        "wall_thickness_um": wall,
                        "scale_window": window,
                    }
                )
    for case in cases:
        case.update(
            {
                "n_loops": n_loops,
                "n_points_per_loop": n_points_per_loop,
                "grid_n": grid_n,
                "grid_extent_um": grid_extent_um,
                "chunk_size": chunk_size,
            }
        )
    return cases


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    label = str(case["geometry_label"])
    variant = GEOMETRY_VARIANTS[label]
    seed = int(case["seed"])
    wall = float(case["wall_thickness_um"])
    window = str(case["scale_window"])
    n_loops = int(case["n_loops"])
    n_points = int(case["n_points_per_loop"])
    grid_n = int(case["grid_n"])
    extent = float(case["grid_extent_um"])
    chunk_size = int(case["chunk_size"])

    geometry = SphereInCylinder(
        sphere_diameter_um=float(variant["sphere_diameter_um"]),
        cylinder_diameter_um=float(variant["cylinder_diameter_um"]),
        cylinder_length_um=8.0,
        bore_radius_um=0.05,
        wall_thickness_um=wall,
    )
    grid = make_xy_grid(-extent, extent, -extent, extent, grid_n, grid_n)
    loops = generate_loops(n_loops, n_points, seed, method="v_loop")
    scales = _window_values(window)
    result = estimate_pair_surface_field(geometry, grid, loops, scales, chunk_size=chunk_size)
    field = result["density_proxy"]
    metrics = _field_metrics(grid, geometry, field)
    scalar = {
        "geometry_label": label,
        "sphere_diameter_um": float(variant["sphere_diameter_um"]),
        "cylinder_diameter_um": float(variant["cylinder_diameter_um"]),
        "seed": seed,
        "wall_thickness_um": wall,
        "scale_window": window,
        "n_loops": n_loops,
        "n_points_per_loop": n_points,
        "grid_n": grid_n,
        "grid_extent_um": extent,
        "n_scales": int(len(scales)),
        "scale_min_um": float(scales[0]),
        "scale_max_um": float(scales[-1]),
        "elapsed_s": float(result["metadata"]["elapsed_s"]),
        "loop_scale_tests_per_s": float(result["metadata"]["loop_scale_tests_per_s"]),
        **metrics,
    }
    return {"case": scalar, "field": field}


def _aggregate_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, float, str], list[dict[str, Any]]] = {}
    for row in cases:
        grouped.setdefault(
            (str(row["geometry_label"]), float(row["wall_thickness_um"]), str(row["scale_window"])),
            [],
        ).append(row)

    aggregates: list[dict[str, Any]] = []
    for (label, wall, window), rows in sorted(grouped.items()):
        summary: dict[str, Any] = {
            "geometry_label": label,
            "wall_thickness_um": wall,
            "scale_window": window,
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


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    scalar_keys = [key for key, value in rows[0].items() if not isinstance(value, (list, dict))]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=scalar_keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in scalar_keys})


def _write_field_csv(path: Path, grid: dict[str, np.ndarray], field: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x_um", "section_um", "density_proxy"])
        for x, y, value in zip(grid["x"].ravel(), grid["y"].ravel(), field.ravel(), strict=True):
            writer.writerow([float(x), float(y), float(value)])


def _write_mean_fields(
    output_dir: Path,
    case_results: list[dict[str, Any]],
    grid_n: int,
    grid_extent_um: float,
) -> list[str]:
    fields_dir = output_dir / "fields"
    fields_dir.mkdir(parents=True, exist_ok=True)
    grid = make_xy_grid(-grid_extent_um, grid_extent_um, -grid_extent_um, grid_extent_um, grid_n, grid_n)
    grouped: dict[tuple[str, float, str], list[np.ndarray]] = {}
    for row in case_results:
        case = row["case"]
        grouped.setdefault(
            (str(case["geometry_label"]), float(case["wall_thickness_um"]), str(case["scale_window"])),
            [],
        ).append(np.asarray(row["field"], dtype=float))

    written: list[str] = []
    for (label, wall, window), fields in sorted(grouped.items()):
        mean_field = np.mean(np.stack(fields, axis=0), axis=0)
        stem = f"{label}_wall{str(wall).replace('.', 'p')}_{window}_mean"
        npy_path = fields_dir / f"{stem}.npy"
        csv_path = fields_dir / f"{stem}.csv"
        np.save(npy_path, mean_field)
        _write_field_csv(csv_path, grid, mean_field)
        written.extend([str(npy_path.relative_to(output_dir)), str(csv_path.relative_to(output_dir))])
    return written


def run_fidelity_probe(
    base_dir: Path,
    baseline_seeds: tuple[int, ...] = (1, 7, 17),
    perturbation_seed: int = 1,
    wall_thicknesses_um: tuple[float, ...] = (0.2, 0.4),
    baseline_windows: tuple[str, ...] = ("mid_0p75_1p50", "upper_1p50_2p75", "broad_0p25_5p00"),
    perturbation_windows: tuple[str, ...] = ("mid_0p75_1p50", "upper_1p50_2p75"),
    n_loops: int = 96,
    n_points_per_loop: int = 192,
    grid_n: int = 37,
    grid_extent_um: float = 2.5,
    workers: int = 4,
    chunk_size: int = 24,
) -> dict[str, Any]:
    output_dir = base_dir / "outputs" / "fidelity_probe"
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = _case_set(
        baseline_seeds=baseline_seeds,
        perturbation_seed=perturbation_seed,
        wall_thicknesses_um=wall_thicknesses_um,
        baseline_windows=baseline_windows,
        perturbation_windows=perturbation_windows,
        n_loops=n_loops,
        n_points_per_loop=n_points_per_loop,
        grid_n=grid_n,
        grid_extent_um=grid_extent_um,
        chunk_size=chunk_size,
    )

    case_results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_case, case) for case in cases]
        for future in as_completed(futures):
            case_results.append(future.result())
    case_results.sort(
        key=lambda row: (
            row["case"]["geometry_label"],
            row["case"]["wall_thickness_um"],
            row["case"]["scale_window"],
            row["case"]["seed"],
        )
    )
    scalar_cases = [row["case"] for row in case_results]
    aggregates = _aggregate_cases(scalar_cases)
    field_files = _write_mean_fields(output_dir, case_results, grid_n, grid_extent_um)

    summary = {
        "stage": "stage2_final_vloop_pair_surface_fidelity_probe",
        "proxy_status": "pair_resolved_segment_surface_morphology_proxy_not_si_normalized",
        "parameters": {
            "baseline_seeds": list(baseline_seeds),
            "perturbation_seed": perturbation_seed,
            "wall_thicknesses_um": list(wall_thicknesses_um),
            "baseline_windows": list(baseline_windows),
            "perturbation_windows": list(perturbation_windows),
            "scale_windows": {
                name: {
                    "start_um": FIDELITY_SCALE_WINDOWS[name][0],
                    "stop_um": FIDELITY_SCALE_WINDOWS[name][1],
                    "count": FIDELITY_SCALE_WINDOWS[name][2],
                }
                for name in sorted(set(baseline_windows + perturbation_windows))
            },
            "geometry_variants": GEOMETRY_VARIANTS,
            "n_loops": n_loops,
            "n_points_per_loop": n_points_per_loop,
            "grid_n": grid_n,
            "grid_extent_um": grid_extent_um,
            "workers": workers,
            "chunk_size": chunk_size,
        },
        "cases": scalar_cases,
        "aggregate_by_geometry_wall_window": aggregates,
        "mean_field_files": field_files,
        "interpretation_note": "This is the final local scalar morphology probe: it tests sphere-inner-wall pair crossings, not stress tensor or metric-source closure.",
    }
    (output_dir / "stage2_final_fidelity_probe_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_csv(output_dir / "stage2_final_fidelity_probe_cases.csv", scalar_cases)
    return summary


def _parse_args() -> argparse.Namespace:
    default_base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Run the final v-loop pair-surface fidelity probe.")
    parser.add_argument("--base-dir", type=Path, default=default_base)
    parser.add_argument("--baseline-seeds", type=int, nargs="+", default=[1, 7, 17])
    parser.add_argument("--perturbation-seed", type=int, default=1)
    parser.add_argument("--wall-thicknesses-um", type=float, nargs="+", default=[0.2, 0.4])
    parser.add_argument("--baseline-windows", choices=tuple(FIDELITY_SCALE_WINDOWS), nargs="+", default=["mid_0p75_1p50", "upper_1p50_2p75", "broad_0p25_5p00"])
    parser.add_argument("--perturbation-windows", choices=tuple(FIDELITY_SCALE_WINDOWS), nargs="+", default=["mid_0p75_1p50", "upper_1p50_2p75"])
    parser.add_argument("--n-loops", type=int, default=96)
    parser.add_argument("--n-points-per-loop", type=int, default=192)
    parser.add_argument("--grid-n", type=int, default=37)
    parser.add_argument("--grid-extent-um", type=float, default=2.5)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--chunk-size", type=int, default=24)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    summary = run_fidelity_probe(
        base_dir=args.base_dir.resolve(),
        baseline_seeds=tuple(args.baseline_seeds),
        perturbation_seed=args.perturbation_seed,
        wall_thicknesses_um=tuple(args.wall_thicknesses_um),
        baseline_windows=tuple(args.baseline_windows),
        perturbation_windows=tuple(args.perturbation_windows),
        n_loops=args.n_loops,
        n_points_per_loop=args.n_points_per_loop,
        grid_n=args.grid_n,
        grid_extent_um=args.grid_extent_um,
        workers=args.workers,
        chunk_size=args.chunk_size,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
