"""Stage 2 scalar worldline proxy smoke runner."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from .geometry import ParallelPlates, SphereInCylinder, make_xy_grid
from .loop_gen import generate_loops
from .report import generate_phase0_phase1
from .worldline_scalar import estimate_density_proxy, proxy_status_for_loop_method


def _write_csv(path: Path, grid: dict[str, np.ndarray], field: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x_um", "section_um", "density_proxy"])
        for x, y, value in zip(grid["x"].ravel(), grid["y"].ravel(), field.ravel(), strict=True):
            writer.writerow([float(x), float(y), float(value)])


def _plot_density(path: Path, title: str, grid: dict[str, np.ndarray], field: np.ndarray) -> None:
    extent = [
        float(grid["x_values"][0]),
        float(grid["x_values"][-1]),
        float(grid["y_values"][0]),
        float(grid["y_values"][-1]),
    ]
    fig, ax = plt.subplots(figsize=(6.0, 4.8), constrained_layout=True)
    image = ax.imshow(field, origin="lower", extent=extent, interpolation="nearest", aspect="equal", cmap="magma")
    ax.set_title(title)
    ax.set_xlabel("x [um]")
    ax.set_ylabel("section coordinate [um]")
    fig.colorbar(image, ax=ax, label="normalized morphology proxy")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _symmetry_error(field: np.ndarray) -> float:
    mirrored = np.flip(field, axis=0)
    numerator = float(np.linalg.norm(field - mirrored))
    denominator = float(np.linalg.norm(field) + 1.0e-12)
    return numerator / denominator


def _estimate_full_run_seconds(metadata: dict[str, Any], full_grid_points: int = 10_000) -> float:
    smoke_rate = float(metadata["loop_scale_tests_per_s"])
    n_points = int(metadata["n_points_per_loop"])
    n_scales = len(metadata["scale_grid"])
    full_loop_scale_tests = full_grid_points * n_scales * 2_000
    point_factor = 1_000 / max(n_points, 1)
    return full_loop_scale_tests / max(smoke_rate, 1.0e-12) * point_factor


def _field_metrics(grid: dict[str, np.ndarray], field: np.ndarray) -> dict[str, Any]:
    finite = np.asarray(field, dtype=float)
    min_index = np.unravel_index(int(np.nanargmin(finite)), finite.shape)
    negative = finite[finite < 0.0]
    return {
        "min": float(np.nanmin(finite)),
        "mean": float(np.nanmean(finite)),
        "std": float(np.nanstd(finite)),
        "negative_pixels": int(np.count_nonzero(finite < 0.0)),
        "total_pixels": int(finite.size),
        "negative_fraction": float(np.count_nonzero(finite < 0.0) / finite.size),
        "contrast_abs_min_to_abs_mean": float(abs(np.nanmin(finite)) / max(abs(np.nanmean(finite)), 1.0e-12)),
        "min_x_um": float(grid["x"][min_index]),
        "min_section_um": float(grid["y"][min_index]),
        "p05": float(np.nanpercentile(finite, 5)),
        "p50": float(np.nanpercentile(finite, 50)),
        "p95": float(np.nanpercentile(finite, 95)),
        "negative_p05": float(np.nanpercentile(negative, 5)) if negative.size else 0.0,
        "negative_p50": float(np.nanpercentile(negative, 50)) if negative.size else 0.0,
    }


def _method_suffix(loop_method: str) -> str:
    return "" if loop_method == "brownian_bridge" else f"_{loop_method}"


def _method_note(loop_method: str) -> str:
    if loop_method == "v_loop":
        return "Paper-style v-loop generator following White et al. Eq. 7-9 summary."
    return "Brownian-bridge proxy loops with thickened smoke-test boundary surfaces."


def run_stage2_smoke(base_dir: Path, loop_method: str = "brownian_bridge") -> dict[str, Any]:
    generate_phase0_phase1(base_dir)
    outputs_dir = base_dir / "outputs"
    reports_dir = base_dir / "reports"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    smoke_cfg = yaml.safe_load((base_dir / "configs" / "smoke.yaml").read_text(encoding="utf-8"))
    n_loops = int(smoke_cfg["loops"]["n_loops"])
    n_points = int(smoke_cfg["loops"]["n_points_per_loop"])
    seed = int(smoke_cfg["seeds"][0])
    loops = generate_loops(n_loops, n_points, seed, method=loop_method)
    scale_grid = np.linspace(0.5, 8.0, 20)
    suffix = _method_suffix(loop_method)

    plate_grid = make_xy_grid(-2.0, 2.0, -1.8, 1.8, smoke_cfg["grid"]["nx"], smoke_cfg["grid"]["ny"])
    plate = ParallelPlates(gap_um=4.0, width_um=20.0, height_um=20.0, thickness_um=0.4)
    plate_result = estimate_density_proxy(
        plate,
        plate_grid,
        loops,
        scale_grid,
        loop_method=loop_method,
        random_seed=seed,
    )
    plate_field = plate_result["density_proxy"]
    plate_symmetry_error = _symmetry_error(plate_field)
    plate_validation = {
        "proxy_negative_somewhere": bool(np.nanmin(plate_field) < 0.0),
        "proxy_mean_negative": bool(np.nanmean(plate_field) < 0.0),
        "midplane_symmetry_relative_error": plate_symmetry_error,
        "symmetry_smoke_pass": bool(plate_symmetry_error < 0.8),
        "boundary_thickness_um": 0.4,
        "method_note": _method_note(loop_method),
    }

    gap_scaling: list[dict[str, Any]] = []
    for gap_um in (2.0, 4.0, 8.0):
        gap_grid = make_xy_grid(-1.0, 1.0, -0.4 * gap_um, 0.4 * gap_um, 9, 9)
        gap_result = estimate_density_proxy(
            ParallelPlates(gap_um=gap_um, width_um=20.0, height_um=20.0, thickness_um=0.4),
            gap_grid,
            loops,
            scale_grid,
            loop_method=loop_method,
            random_seed=seed,
        )
        gap_scaling.append(
            {
                "gap_um": gap_um,
                "mean_negative_magnitude": float(-np.nanmean(gap_result["density_proxy"])),
            }
        )
    gap_values = [row["mean_negative_magnitude"] for row in gap_scaling]
    gap_scaling_pass = bool(gap_values[0] > gap_values[1] > gap_values[2])

    np.save(outputs_dir / f"plate_validation_density_proxy{suffix}.npy", plate_field)
    _write_csv(outputs_dir / f"plate_validation_density_proxy{suffix}.csv", plate_grid, plate_field)
    (outputs_dir / f"plate_validation_metadata{suffix}.json").write_text(
        json.dumps({**plate_result["metadata"], "validation": plate_validation, "gap_scaling": gap_scaling}, indent=2) + "\n",
        encoding="utf-8",
    )
    _plot_density(reports_dir / f"fig_plate_validation_density_proxy{suffix}.png", f"Plate Validation Density Proxy ({loop_method})", plate_grid, plate_field)

    sphere_grid = make_xy_grid(-3.0, 3.0, -3.0, 3.0, smoke_cfg["grid"]["nx"], smoke_cfg["grid"]["ny"])
    sphere = SphereInCylinder(
        sphere_diameter_um=1.0,
        cylinder_diameter_um=4.0,
        cylinder_length_um=8.0,
        bore_radius_um=0.05,
        wall_thickness_um=0.4,
    )
    sphere_result = estimate_density_proxy(
        sphere,
        sphere_grid,
        loops,
        np.linspace(0.25, 5.0, 20),
        loop_method=loop_method,
        random_seed=seed,
    )
    sphere_field = sphere_result["density_proxy"]
    np.save(outputs_dir / f"sphere_cylinder_density_proxy_smoke{suffix}.npy", sphere_field)
    _write_csv(outputs_dir / f"sphere_cylinder_density_proxy_smoke{suffix}.csv", sphere_grid, sphere_field)
    (outputs_dir / f"sphere_cylinder_metadata_smoke{suffix}.json").write_text(
        json.dumps(sphere_result["metadata"], indent=2) + "\n",
        encoding="utf-8",
    )
    _plot_density(reports_dir / f"fig_sphere_cylinder_density_proxy_smoke{suffix}.png", f"Sphere-Cylinder Density Proxy Smoke ({loop_method})", sphere_grid, sphere_field)

    full_estimate_s = _estimate_full_run_seconds(sphere_result["metadata"])
    summary = {
        "stage": "stage2_scalar_worldline_proxy_smoke",
        "loop_method": loop_method,
        "proxy_status": proxy_status_for_loop_method(loop_method),
        "n_loops": n_loops,
        "n_points_per_loop": n_points,
        "plate_validation": plate_validation,
        "gap_scaling": gap_scaling,
        "gap_scaling_pass": gap_scaling_pass,
        "sphere_field_metrics": _field_metrics(sphere_grid, sphere_field),
        "sphere_smoke_metadata": sphere_result["metadata"],
        "estimated_full_100x100_2000x1000_seconds": float(full_estimate_s),
        "estimated_full_100x100_2000x1000_hours": float(full_estimate_s / 3600.0),
        "full_run_guidance": "Use this estimate only for the Python proxy. Exact v-loop/C++ kernels require a separate benchmark.",
    }
    (outputs_dir / f"stage2_smoke_summary{suffix}.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    report_text = "\n".join(
        [
            "# Stage 2 Scalar Worldline Proxy Smoke",
            "",
            f"Status: `{'pass' if plate_validation['proxy_mean_negative'] and gap_scaling_pass else 'watch'}`.",
            "",
            f"Loop method: `{loop_method}`.",
            "",
            _method_note(loop_method),
            "",
            f"- plate mean is negative: `{plate_validation['proxy_mean_negative']}`",
            f"- plate symmetry relative error: `{plate_symmetry_error:.6g}`",
            f"- gap scaling pass: `{gap_scaling_pass}`",
            f"- sphere negative proxy pixels: `{summary['sphere_field_metrics']['negative_pixels']}`",
            f"- sphere contrast |min|/|mean|: `{summary['sphere_field_metrics']['contrast_abs_min_to_abs_mean']:.6g}`",
            f"- sphere minimum coordinate: `({summary['sphere_field_metrics']['min_x_um']:.6g}, {summary['sphere_field_metrics']['min_section_um']:.6g}) um`",
            f"- estimated full Python-proxy runtime: `{summary['estimated_full_100x100_2000x1000_hours']:.3g}` hours",
            "",
            "Generated artifacts:",
            "",
            f"- `outputs/plate_validation_density_proxy{suffix}.npy`",
            f"- `outputs/plate_validation_density_proxy{suffix}.csv`",
            f"- `outputs/sphere_cylinder_density_proxy_smoke{suffix}.npy`",
            f"- `outputs/sphere_cylinder_density_proxy_smoke{suffix}.csv`",
            f"- `reports/fig_plate_validation_density_proxy{suffix}.png`",
            f"- `reports/fig_sphere_cylinder_density_proxy_smoke{suffix}.png`",
        ]
    )
    (reports_dir / f"stage2_smoke_validation{suffix}.md").write_text(report_text + "\n", encoding="utf-8")
    return summary


def main() -> None:
    default_base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Run Stage 2 scalar worldline proxy smoke.")
    parser.add_argument("--base-dir", type=Path, default=default_base)
    parser.add_argument("--loop-method", choices=["brownian_bridge", "v_loop"], default="brownian_bridge")
    args = parser.parse_args()
    print(json.dumps(run_stage2_smoke(args.base_dir.resolve(), loop_method=args.loop_method), indent=2))


if __name__ == "__main__":
    main()
