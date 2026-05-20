from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .hard_affine_snec import (
    BRANCH_SIGNS,
    LabelGrid,
    _coverage_record,
    _interpolate_trace,
    _load_point_ledgers,
    _pivot_arrays,
    _smeared_average,
    _trace_branch,
)
from .intermediate_source_model import SECTOR_ORDER
from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


INTERMEDIATE_RESIDUAL_SECTOR = "intermediate_unmodeled_residual"
ALL_SECTORS = [*SECTOR_ORDER, INTERMEDIATE_RESIDUAL_SECTOR]


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _load_intermediate_manifest(intermediate_dir: Path) -> tuple[dict[str, Any], Path]:
    manifest_path = intermediate_dir / "intermediate_source_model_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    point_value = manifest.get("files", {}).get("point_sector_stress", "intermediate_source_point_sector_stress.csv")
    point_path = resolve_manifest_path(intermediate_dir, point_value)
    return manifest, point_path


def _sector_value_points(point_sector_stress: pd.DataFrame) -> pd.DataFrame:
    if point_sector_stress.empty:
        return pd.DataFrame()
    frame = point_sector_stress.copy()
    for branch in BRANCH_SIGNS:
        value_col = f"sector_Tkk_{branch}"
        if value_col not in frame.columns:
            sign = BRANCH_SIGNS[branch]
            frame[value_col] = (
                frame["sector_rho"].astype(float)
                + frame["sector_p_l"].astype(float)
                + sign * 2.0 * frame["sector_j_l"].astype(float)
            )
    grouped = (
        frame.groupby(["label", "point_index", "sector"], dropna=False)
        .agg(
            sector_Tkk_plus=("sector_Tkk_plus", "sum"),
            sector_Tkk_minus=("sector_Tkk_minus", "sum"),
        )
        .reset_index()
    )
    return grouped


def _model_sector_order(manifest: dict[str, Any], sector_points: pd.DataFrame) -> list[str]:
    ordered: list[str] = []
    for sector in manifest.get("sectors", SECTOR_ORDER):
        sector_name = str(sector)
        if sector_name and sector_name != INTERMEDIATE_RESIDUAL_SECTOR and sector_name not in ordered:
            ordered.append(sector_name)
    if "sector" in sector_points.columns:
        for sector in sector_points["sector"].dropna().astype(str).unique():
            if sector and sector != INTERMEDIATE_RESIDUAL_SECTOR and sector not in ordered:
                ordered.append(sector)
    return ordered


def _build_intermediate_label_grids(
    point_ledgers: dict[str, pd.DataFrame],
    sector_points: pd.DataFrame,
    *,
    sectors: Iterable[str] | None = None,
    total_mode: str = "intermediate_sector_sum",
) -> tuple[dict[str, LabelGrid], dict[str, pd.DataFrame]]:
    model_sectors = list(sectors or SECTOR_ORDER)
    scan_sectors = [*model_sectors, INTERMEDIATE_RESIDUAL_SECTOR]
    grids: dict[str, LabelGrid] = {}
    center_tables: dict[str, pd.DataFrame] = {}
    for label, points in point_ledgers.items():
        points = points.copy()
        for column in ["rho_euler", "p_l_unit", "j_l_unit", "alpha", "beta", "gamma_ll"]:
            points[column] = points[column].astype(float)
        for branch, branch_sign in BRANCH_SIGNS.items():
            points[f"geometric_total::{branch}"] = (
                points["rho_euler"] + points["p_l_unit"] + branch_sign * 2.0 * points["j_l_unit"]
            )
            points[f"intermediate_total::{branch}"] = 0.0
            for sector in scan_sectors:
                points[f"sector::{sector}::{branch}"] = 0.0

        indexed_positions = {int(point): idx for idx, point in enumerate(points["point_index"].astype(int))}
        label_sectors = sector_points.loc[sector_points["label"].astype(str).eq(str(label))]
        for _, row in label_sectors.iterrows():
            pos = indexed_positions.get(int(row["point_index"]))
            if pos is None:
                continue
            sector = str(row["sector"])
            if sector not in model_sectors:
                continue
            for branch in BRANCH_SIGNS:
                value = _finite(row.get(f"sector_Tkk_{branch}"))
                points.iat[pos, points.columns.get_loc(f"sector::{sector}::{branch}")] += value
                points.iat[pos, points.columns.get_loc(f"intermediate_total::{branch}")] += value

        for branch in BRANCH_SIGNS:
            points[f"sector::{INTERMEDIATE_RESIDUAL_SECTOR}::{branch}"] = (
                points[f"geometric_total::{branch}"] - points[f"intermediate_total::{branch}"]
            )
            if total_mode == "intermediate_sector_sum":
                points[f"total::{branch}"] = points[f"intermediate_total::{branch}"]
            elif total_mode == "geometric":
                points[f"total::{branch}"] = points[f"geometric_total::{branch}"]
            elif total_mode == "intermediate_plus_residual":
                points[f"total::{branch}"] = (
                    points[f"intermediate_total::{branch}"]
                    + points[f"sector::{INTERMEDIATE_RESIDUAL_SECTOR}::{branch}"]
                )
            else:
                raise ValueError(f"unknown intermediate SNEC total mode: {total_mode}")

        value_cols = [
            "alpha",
            "beta",
            "gamma_ll",
            "total::plus",
            "total::minus",
            "geometric_total::plus",
            "geometric_total::minus",
            "intermediate_total::plus",
            "intermediate_total::minus",
            *[
                f"sector::{sector}::{branch}"
                for sector in scan_sectors
                for branch in BRANCH_SIGNS
            ],
        ]
        grids[label] = _pivot_arrays(points, value_cols)
        center_tables[label] = points
    return grids, center_tables


def _dominant_negative_sector(record: dict[str, Any], branch: str, sectors: Iterable[str]) -> str:
    sector_values = {
        sector: _finite(record.get(f"smeared_sector::{sector}::{branch}"), float("nan"))
        for sector in sectors
    }
    finite = {key: value for key, value in sector_values.items() if math.isfinite(value)}
    if not finite:
        return ""
    sector, value = min(finite.items(), key=lambda item: item[1])
    return sector if value < 0.0 else ""


def _scan_label(
    grid: LabelGrid,
    centers: pd.DataFrame,
    *,
    smear_widths: list[float],
    benchmark_b: float,
    center_stride: int,
    min_support_coverage: float,
    min_kernel_coverage: float,
    sectors: Iterable[str] | None = None,
    progress: bool = False,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    scan_sectors = list(sectors or ALL_SECTORS)
    max_width = max(smear_widths)
    step_s = max(grid.step_s / 2.0, 1.0e-6)
    trace_names_by_branch = {
        branch: [
            f"total::{branch}",
            f"geometric_total::{branch}",
            f"intermediate_total::{branch}",
            *[f"sector::{sector}::{branch}" for sector in scan_sectors],
        ]
        for branch in BRANCH_SIGNS
    }
    selected_centers = centers.sort_values(["s", "l"]).iloc[:: max(int(center_stride), 1)]
    total_centers = int(len(selected_centers))
    for center_index, (_, center) in enumerate(selected_centers.iterrows(), start=1):
        center_s = float(center["s"])
        center_l = float(center["l"])
        for branch in BRANCH_SIGNS:
            lambdas, s_values, l_values = _trace_branch(
                grid,
                center_s,
                center_l,
                branch,
                lambda_extent=4.0 * max_width,
                step_s=step_s,
            )
            if len(lambdas) < 3:
                continue
            trace_values = _interpolate_trace(grid, trace_names_by_branch[branch], s_values, l_values)
            total_values = trace_values[f"total::{branch}"]
            for width in smear_widths:
                total_avg, neg_avg, norm = _smeared_average(total_values, lambdas, width)
                if not math.isfinite(total_avg):
                    continue
                coverage = _coverage_record(
                    lambdas,
                    width,
                    norm,
                    min_support_coverage=min_support_coverage,
                    min_kernel_coverage=min_kernel_coverage,
                )
                floor = -8.0 * math.pi * float(benchmark_b) / (float(width) * float(width))
                critical_b = max(-total_avg, 0.0) * float(width) * float(width) / (8.0 * math.pi)
                record: dict[str, Any] = {
                    "label": grid.label,
                    "case": grid.case,
                    "branch": branch,
                    "smear_width_affine": float(width),
                    "center_point_index": int(center["point_index"]),
                    "center_s": center_s,
                    "center_l": center_l,
                    "center_stage": center.get("stage", ""),
                    "center_region": center.get("region", ""),
                    "center_inside_packet_live": bool(center.get("inside_packet_live", False)),
                    "trace_samples": int(len(lambdas)),
                    "trace_lambda_min": float(np.nanmin(lambdas)),
                    "trace_lambda_max": float(np.nanmax(lambdas)),
                    "window_weight_norm": norm,
                    **coverage,
                    "smeared_total_Tkk_hat": total_avg,
                    "smeared_total_neg_part": neg_avg,
                    "benchmark_B": float(benchmark_b),
                    "benchmark_floor": floor,
                    "critical_B_for_zero_margin": critical_b,
                    "benchmark_to_critical_B_ratio": float(benchmark_b) / critical_b
                    if critical_b > 0.0 else float("inf"),
                    "margin_to_benchmark_floor": float(total_avg - floor),
                    "violates_benchmark_floor": bool(total_avg < floor),
                }
                for name in ["geometric_total", "intermediate_total"]:
                    avg, neg, _norm = _smeared_average(trace_values[f"{name}::{branch}"], lambdas, width)
                    record[f"smeared_{name}_Tkk_hat"] = avg
                    record[f"smeared_{name}_neg_part"] = neg
                for sector in scan_sectors:
                    sector_avg, sector_neg, _norm = _smeared_average(
                        trace_values[f"sector::{sector}::{branch}"],
                        lambdas,
                        width,
                    )
                    record[f"smeared_sector::{sector}::{branch}"] = sector_avg
                    record[f"smeared_sector_neg::{sector}::{branch}"] = sector_neg
                record["dominant_negative_sector"] = _dominant_negative_sector(record, branch, scan_sectors)
                rows.append(record)
        if progress and (center_index == total_centers or center_index % max(1, total_centers // 5) == 0):
            print(f"{grid.label}: intermediate SNEC center {center_index}/{total_centers}", flush=True)
    return pd.DataFrame(rows)


def _summary_table(windows: pd.DataFrame) -> pd.DataFrame:
    if windows.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for keys, group in windows.groupby(["label", "branch", "smear_width_affine"], sort=False):
        scoreable = group.loc[group["scoreable_window"].astype(bool)] if "scoreable_window" in group else group
        summary_group = scoreable if not scoreable.empty else group
        worst = summary_group.sort_values("margin_to_benchmark_floor", ascending=True).iloc[0]
        rows.append({
            "label": keys[0],
            "branch": keys[1],
            "smear_width_affine": keys[2],
            "windows_scanned": int(len(group)),
            "scoreable_windows": int(len(scoreable)),
            "coverage_rejected_windows": int(len(group) - len(scoreable)),
            "all_benchmark_violations": int(group["violates_benchmark_floor"].astype(bool).sum()),
            "benchmark_violations": int(summary_group["violates_benchmark_floor"].astype(bool).sum()),
            "passes_benchmark": bool(not summary_group["violates_benchmark_floor"].astype(bool).any()),
            "summary_uses_scoreable_filter": bool(not scoreable.empty),
            "worst_margin_to_floor": float(worst["margin_to_benchmark_floor"]),
            "worst_smeared_total_Tkk_hat": float(worst["smeared_total_Tkk_hat"]),
            "benchmark_floor": float(worst["benchmark_floor"]),
            "critical_B_for_zero_margin": float(worst["critical_B_for_zero_margin"]),
            "benchmark_to_critical_B_ratio": float(worst["benchmark_to_critical_B_ratio"]),
            "worst_center_s": float(worst["center_s"]),
            "worst_center_l": float(worst["center_l"]),
            "worst_center_stage": worst["center_stage"],
            "worst_center_region": worst["center_region"],
            "worst_center_inside_packet_live": bool(worst["center_inside_packet_live"]),
            "dominant_negative_sector": worst["dominant_negative_sector"],
            "worst_smeared_geometric_total_Tkk_hat": float(worst["smeared_geometric_total_Tkk_hat"]),
            "worst_smeared_intermediate_total_Tkk_hat": float(worst["smeared_intermediate_total_Tkk_hat"]),
        })
    return pd.DataFrame(rows).sort_values(["label", "smear_width_affine", "branch"])


def _sector_summary_table(windows: pd.DataFrame, sectors: Iterable[str] | None = None) -> pd.DataFrame:
    if windows.empty:
        return pd.DataFrame()
    scan_sectors = list(sectors or ALL_SECTORS)
    rows: list[dict[str, Any]] = []
    for (label, branch, width), group in windows.groupby(["label", "branch", "smear_width_affine"], sort=False):
        scoreable = group.loc[group["scoreable_window"].astype(bool)] if "scoreable_window" in group else group
        sector_group = scoreable if not scoreable.empty else group
        for sector in scan_sectors:
            col = f"smeared_sector::{sector}::{branch}"
            neg_col = f"smeared_sector_neg::{sector}::{branch}"
            values = sector_group[col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
            neg_values = sector_group[neg_col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
            if values.empty:
                continue
            worst_idx = values.idxmin()
            rows.append({
                "label": label,
                "branch": branch,
                "smear_width_affine": float(width),
                "sector": sector,
                "min_smeared_sector_Tkk_hat": float(values.min()),
                "mean_smeared_sector_Tkk_hat": float(values.mean()),
                "max_smeared_sector_neg_part": float(neg_values.max()) if not neg_values.empty else float("nan"),
                "worst_sector_center_s": float(sector_group.loc[worst_idx, "center_s"]),
                "worst_sector_center_l": float(sector_group.loc[worst_idx, "center_l"]),
                "worst_sector_center_stage": sector_group.loc[worst_idx, "center_stage"],
                "worst_sector_center_region": sector_group.loc[worst_idx, "center_region"],
            })
    return pd.DataFrame(rows).sort_values(["label", "smear_width_affine", "branch", "sector"])


def build_intermediate_source_snec_screen(
    component_dir: Path,
    intermediate_dir: Path,
    *,
    smear_widths: Iterable[float] = (0.25, 0.50, 1.00),
    benchmark_b: float = 1.0 / (32.0 * math.pi),
    center_stride: int = 1,
    top_limit: int = 120,
    min_support_coverage: float = 0.80,
    min_kernel_coverage: float = 0.80,
    total_mode: str = "intermediate_sector_sum",
    progress: bool = False,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    component_manifest_path = component_dir / "component_source_manifest.json"
    component_manifest = json.loads(component_manifest_path.read_text())
    point_ledgers = _load_point_ledgers(component_dir, component_manifest)
    intermediate_manifest, point_sector_path = _load_intermediate_manifest(intermediate_dir)
    point_sector_stress = pd.read_csv(point_sector_path)
    sector_points = _sector_value_points(point_sector_stress)
    model_sectors = _model_sector_order(intermediate_manifest, sector_points)
    scan_sectors = [*model_sectors, INTERMEDIATE_RESIDUAL_SECTOR]
    grids, center_tables = _build_intermediate_label_grids(
        point_ledgers,
        sector_points,
        sectors=model_sectors,
        total_mode=total_mode,
    )
    widths = [float(width) for width in smear_widths]
    windows = pd.concat(
        [
            _scan_label(
                grid,
                center_tables[label],
                smear_widths=widths,
                benchmark_b=float(benchmark_b),
                center_stride=int(center_stride),
                min_support_coverage=float(min_support_coverage),
                min_kernel_coverage=float(min_kernel_coverage),
                sectors=scan_sectors,
                progress=bool(progress),
            )
            for label, grid in grids.items()
        ],
        ignore_index=True,
    )
    summary = _summary_table(windows)
    sector_summary = _sector_summary_table(windows, scan_sectors)
    top_source = windows.loc[windows["scoreable_window"].astype(bool)] if not windows.empty else windows
    if top_source.empty:
        top_source = windows
    top_windows = (
        top_source.sort_values(["label", "margin_to_benchmark_floor"], ascending=[True, True])
        .groupby("label", sort=False)
        .head(int(top_limit))
        .reset_index(drop=True)
    )
    outputs = {
        "windows": windows,
        "summary": summary,
        "sector_summary": sector_summary,
        "top_windows": top_windows,
    }
    metadata = {
        "component_dir": component_dir,
        "component_manifest_path": component_manifest_path,
        "component_manifest": component_manifest,
        "intermediate_dir": intermediate_dir,
        "intermediate_manifest": intermediate_manifest,
        "point_sector_stress_path": point_sector_path,
        "model_sectors": model_sectors,
        "scan_sectors": scan_sectors,
        "smear_widths": widths,
        "benchmark_b": float(benchmark_b),
        "center_stride": int(center_stride),
        "top_limit": int(top_limit),
        "min_support_coverage": float(min_support_coverage),
        "min_kernel_coverage": float(min_kernel_coverage),
        "total_mode": str(total_mode),
        "progress": bool(progress),
    }
    return outputs, metadata


def write_intermediate_source_snec_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "windows": outdir / "intermediate_source_snec_windows.csv",
        "summary": outdir / "intermediate_source_snec_summary.csv",
        "sector_summary": outdir / "intermediate_source_snec_sector_summary.csv",
        "top_windows": outdir / "intermediate_source_snec_top_windows.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "intermediate_source_snec_manifest.json"
    manifest = {
        "caveat": (
            "Light hard-affine SNEC-style screen for the intermediate sector package. "
            "The intermediate sector-sum total tests the replacement package, not a complete physical matter model."
        ),
        "component_source_dir": str(metadata["component_dir"]),
        "intermediate_source_dir": str(metadata["intermediate_dir"]),
        "point_sector_stress": str(metadata["point_sector_stress_path"]),
        "point_sector_stress_sha256": sha256_file(Path(metadata["point_sector_stress_path"])),
        "sectors": list(metadata["scan_sectors"]),
        "smear_widths_affine": list(metadata["smear_widths"]),
        "benchmark_B": float(metadata["benchmark_b"]),
        "center_stride": int(metadata["center_stride"]),
        "min_support_coverage": float(metadata["min_support_coverage"]),
        "min_kernel_coverage": float(metadata["min_kernel_coverage"]),
        "total_mode": metadata["total_mode"],
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
