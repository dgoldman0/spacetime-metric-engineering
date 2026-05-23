from __future__ import annotations

import math
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .composite_source_ansatz import build_composite_source_ansatz_screen
from .hard_affine_snec import (
    BRANCH_SIGNS,
    SECTOR_ORDER,
    LabelGrid,
    _build_label_grids,
    _fit_coefficients,
    _interpolate_trace,
    _lambda_cell_weights,
    _load_component_detail,
    _load_point_ledgers,
    _pivot_arrays,
    _sector_assignment_points,
    _trace_branch,
)
from .source_ledger import sha256_file, write_manifest


ZONE_MASKS = {
    "endpoint_support": ("endpoint", "support_edge", "reset"),
    "core_throat": ("core_throat",),
    "live_packet": ("packet", "live"),
}


def _finite_values(values: np.ndarray) -> np.ndarray:
    return values[np.isfinite(values)]


def _integral_parts(
    values: np.ndarray,
    lambdas: np.ndarray,
    mask: np.ndarray | None = None,
) -> dict[str, float]:
    finite = np.isfinite(values) & np.isfinite(lambdas)
    if mask is not None:
        finite = finite & np.isfinite(mask)
    if int(finite.sum()) < 2:
        return {
            "integral": float("nan"),
            "positive_part": float("nan"),
            "negative_part": float("nan"),
            "measure": 0.0,
            "mean": float("nan"),
        }
    vals = values[finite]
    lam = lambdas[finite]
    weights = _lambda_cell_weights(lam)
    if mask is not None:
        weights = weights * np.clip(mask[finite], 0.0, 1.0)
    measure = float(np.sum(weights))
    if measure <= 0.0:
        return {
            "integral": float("nan"),
            "positive_part": float("nan"),
            "negative_part": float("nan"),
            "measure": 0.0,
            "mean": float("nan"),
        }
    integral = float(np.sum(vals * weights))
    positive = float(np.sum(np.maximum(vals, 0.0) * weights))
    negative = float(np.sum(np.maximum(-vals, 0.0) * weights))
    return {
        "integral": integral,
        "positive_part": positive,
        "negative_part": negative,
        "measure": measure,
        "mean": integral / measure,
    }


def _mask_column(points: pd.DataFrame, tokens: tuple[str, ...], *, include_live_flag: bool = False) -> pd.Series:
    stage = points.get("stage", pd.Series("", index=points.index)).astype(str).str.lower()
    region = points.get("region", pd.Series("", index=points.index)).astype(str).str.lower()
    text = stage + " " + region
    mask = pd.Series(False, index=points.index)
    for token in tokens:
        mask = mask | text.str.contains(token, regex=False)
    if include_live_flag and "inside_packet_live" in points.columns:
        mask = mask | points["inside_packet_live"].astype(bool)
    return mask.astype(float)


def _add_zone_masks(grid: LabelGrid, centers: pd.DataFrame) -> None:
    mask_points = centers[["label", "case", "s", "l"]].copy()
    for name, tokens in ZONE_MASKS.items():
        mask_points[f"zone::{name}"] = _mask_column(
            centers,
            tokens,
            include_live_flag=(name == "live_packet"),
        )
    mask_grid = _pivot_arrays(mask_points, [f"zone::{name}" for name in ZONE_MASKS])
    grid.arrays.update(mask_grid.arrays)


def _append_seed(
    seeds: dict[tuple[str, int, str], set[str]],
    row: pd.Series,
    branch: str,
    source: str,
) -> None:
    seeds.setdefault((str(row["label"]), int(row["point_index"]), str(branch)), set()).add(source)


def _select_seeds(
    centers: pd.DataFrame,
    *,
    seed_stride: int,
    top_per_branch: int,
    snec_top_windows: pd.DataFrame | None = None,
) -> pd.DataFrame:
    ordered = centers.sort_values(["s", "l"]).reset_index(drop=True)
    seeds: dict[tuple[str, int, str], set[str]] = {}

    for _, row in ordered.iloc[:: max(int(seed_stride), 1)].iterrows():
        for branch in BRANCH_SIGNS:
            _append_seed(seeds, row, branch, "uniform_stride")

    for branch in BRANCH_SIGNS:
        total_col = f"total::{branch}"
        if total_col in ordered.columns:
            for _, row in ordered.sort_values(total_col, ascending=True).head(int(top_per_branch)).iterrows():
                _append_seed(seeds, row, branch, "top_negative_total")

        stage = ordered.get("stage", pd.Series("", index=ordered.index)).astype(str).str.lower()
        region = ordered.get("region", pd.Series("", index=ordered.index)).astype(str).str.lower()
        text = stage + " " + region
        endpoint_mask = text.str.contains("endpoint", regex=False) | text.str.contains("support_edge", regex=False) | text.str.contains("reset", regex=False)
        endpoint = ordered.loc[endpoint_mask]
        if total_col in endpoint.columns and not endpoint.empty:
            for _, row in endpoint.sort_values(total_col, ascending=True).head(int(top_per_branch)).iterrows():
                _append_seed(seeds, row, branch, "endpoint_support_adversarial")

        live_mask = ordered.get("inside_packet_live", pd.Series(False, index=ordered.index)).astype(bool) | text.str.contains("packet", regex=False)
        live = ordered.loc[live_mask]
        if total_col in live.columns and not live.empty:
            for _, row in live.sort_values(total_col, ascending=True).head(int(top_per_branch)).iterrows():
                _append_seed(seeds, row, branch, "live_packet_adversarial")

    if snec_top_windows is not None and not snec_top_windows.empty:
        keep = ["label", "center_point_index", "branch"]
        if set(keep).issubset(snec_top_windows.columns):
            indexed = ordered.set_index(["label", "point_index"], drop=False)
            for _, snec_row in snec_top_windows.iterrows():
                key = (str(snec_row["label"]), int(snec_row["center_point_index"]))
                if key not in indexed.index:
                    continue
                center = indexed.loc[key]
                if isinstance(center, pd.DataFrame):
                    center = center.iloc[0]
                _append_seed(seeds, center, str(snec_row["branch"]), "worst_snec_window")

    rows: list[dict[str, Any]] = []
    indexed = centers.set_index(["label", "point_index"], drop=False)
    for (label, point_index, branch), sources in sorted(seeds.items()):
        center = indexed.loc[(label, point_index)]
        if isinstance(center, pd.DataFrame):
            center = center.iloc[0]
        rows.append({
            "label": label,
            "point_index": int(point_index),
            "branch": branch,
            "seed_sources": "|".join(sorted(sources)),
            "seed_source_count": int(len(sources)),
            "s": float(center["s"]),
            "l": float(center["l"]),
            "stage": center.get("stage", ""),
            "region": center.get("region", ""),
            "inside_packet_live": bool(center.get("inside_packet_live", False)),
        })
    return pd.DataFrame(rows)


def _touch_fraction(grid: LabelGrid, s_values: np.ndarray, l_values: np.ndarray) -> dict[str, bool]:
    if len(s_values) == 0:
        return {
            "touches_s_lower": False,
            "touches_s_upper": False,
            "touches_l_lower": False,
            "touches_l_upper": False,
        }
    s_tol = max(grid.step_s, 1.0e-6)
    l_tol = max(grid.step_l, 1.0e-6)
    return {
        "touches_s_lower": bool(np.nanmin(s_values) <= float(grid.s_axis[0]) + s_tol),
        "touches_s_upper": bool(np.nanmax(s_values) >= float(grid.s_axis[-1]) - s_tol),
        "touches_l_lower": bool(np.nanmin(l_values) <= float(grid.l_axis[0]) + l_tol),
        "touches_l_upper": bool(np.nanmax(l_values) >= float(grid.l_axis[-1]) - l_tol),
    }


def _trace_anec_record(
    grid: LabelGrid,
    seed: pd.Series,
    *,
    parameterization: str,
    lambda_extent: float,
) -> dict[str, Any] | None:
    branch = str(seed["branch"])
    step_s = max(grid.step_s / 2.0, 1.0e-6)
    lambdas, s_values, l_values, diagnostics = _trace_branch(
        grid,
        float(seed["s"]),
        float(seed["l"]),
        branch,
        lambda_extent=float(lambda_extent),
        step_s=step_s,
        parameterization=parameterization,
        return_diagnostics=True,
    )
    if len(lambdas) < 3:
        return None

    names = [f"total::{branch}", *[f"sector::{sector}::{branch}" for sector in SECTOR_ORDER]]
    names.extend([f"zone::{name}" for name in ZONE_MASKS])
    trace_values = _interpolate_trace(grid, names, s_values, l_values)
    total = trace_values[f"total::{branch}"]
    total_parts = _integral_parts(total, lambdas)
    finite_kappa = _finite_values(diagnostics["non_affinity_kappa"])
    finite_residual = _finite_values(diagnostics["radial_geodesic_residual"])
    finite_scale = _finite_values(diagnostics["dlambda_dsigma"])

    record: dict[str, Any] = {
        "label": grid.label,
        "case": grid.case,
        "branch": branch,
        "trace_parameterization": parameterization,
        "seed_point_index": int(seed["point_index"]),
        "seed_sources": seed["seed_sources"],
        "seed_source_count": int(seed["seed_source_count"]),
        "center_s": float(seed["s"]),
        "center_l": float(seed["l"]),
        "center_stage": seed.get("stage", ""),
        "center_region": seed.get("region", ""),
        "center_inside_packet_live": bool(seed.get("inside_packet_live", False)),
        "trace_samples": int(len(lambdas)),
        "trace_lambda_min": float(np.nanmin(lambdas)),
        "trace_lambda_max": float(np.nanmax(lambdas)),
        "trace_lambda_span": float(np.nanmax(lambdas) - np.nanmin(lambdas)),
        "left_affine_extent": float(abs(np.nanmin(lambdas))),
        "right_affine_extent": float(abs(np.nanmax(lambdas))),
        "trace_s_min": float(np.nanmin(s_values)),
        "trace_s_max": float(np.nanmax(s_values)),
        "trace_l_min": float(np.nanmin(l_values)),
        "trace_l_max": float(np.nanmax(l_values)),
        "max_abs_non_affinity_kappa": float(np.max(np.abs(finite_kappa))) if len(finite_kappa) else float("nan"),
        "mean_abs_non_affinity_kappa": float(np.mean(np.abs(finite_kappa))) if len(finite_kappa) else float("nan"),
        "max_abs_radial_geodesic_residual": float(np.max(np.abs(finite_residual))) if len(finite_residual) else float("nan"),
        "min_dlambda_dsigma": float(np.min(finite_scale)) if len(finite_scale) else float("nan"),
        "max_dlambda_dsigma": float(np.max(finite_scale)) if len(finite_scale) else float("nan"),
        "anec_total_integral": total_parts["integral"],
        "anec_positive_part": total_parts["positive_part"],
        "anec_negative_part": total_parts["negative_part"],
        "anec_measure": total_parts["measure"],
        "anec_mean_Tkk": total_parts["mean"],
        "finite_domain_anec_pass": bool(total_parts["integral"] >= 0.0)
        if math.isfinite(total_parts["integral"]) else False,
        **_touch_fraction(grid, s_values, l_values),
    }

    for name in ZONE_MASKS:
        parts = _integral_parts(total, lambdas, trace_values[f"zone::{name}"])
        record[f"zone::{name}::integral"] = parts["integral"]
        record[f"zone::{name}::positive_part"] = parts["positive_part"]
        record[f"zone::{name}::negative_part"] = parts["negative_part"]
        record[f"zone::{name}::measure"] = parts["measure"]

    sector_values: dict[str, float] = {}
    for sector in SECTOR_ORDER:
        values = trace_values[f"sector::{sector}::{branch}"]
        parts = _integral_parts(values, lambdas)
        sector_values[sector] = parts["integral"]
        record[f"sector::{sector}::integral"] = parts["integral"]
        record[f"sector::{sector}::positive_part"] = parts["positive_part"]
        record[f"sector::{sector}::negative_part"] = parts["negative_part"]

    finite_sectors = {sector: value for sector, value in sector_values.items() if math.isfinite(value)}
    record["dominant_negative_sector"] = (
        min(finite_sectors.items(), key=lambda item: item[1])[0] if finite_sectors else ""
    )
    return record


def _chunk_frame(frame: pd.DataFrame, chunks: int) -> list[pd.DataFrame]:
    if frame.empty:
        return []
    chunk_count = max(1, min(int(chunks), len(frame)))
    indices = np.array_split(np.arange(len(frame)), chunk_count)
    return [frame.iloc[index].reset_index(drop=True) for index in indices if len(index)]


def _worker_count(max_workers: int | None) -> int:
    if max_workers is not None and int(max_workers) > 0:
        return int(max_workers)
    return max(1, int(os.cpu_count() or 1))


def _trace_seed_chunk(
    grid: LabelGrid,
    seeds: pd.DataFrame,
    parameterization: str,
    lambda_extent: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, seed in seeds.iterrows():
        record = _trace_anec_record(
            grid,
            seed,
            parameterization=parameterization,
            lambda_extent=float(lambda_extent),
        )
        if record is not None:
            rows.append(record)
    return rows


def _summary_table(traces: pd.DataFrame) -> pd.DataFrame:
    if traces.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for (label, branch), group in traces.groupby(["label", "branch"], sort=False):
        worst_idx = group["anec_total_integral"].astype(float).idxmin()
        worst = group.loc[worst_idx]
        rows.append({
            "label": label,
            "branch": branch,
            "traces_scanned": int(len(group)),
            "finite_domain_negative_count": int((group["anec_total_integral"].astype(float) < 0.0).sum()),
            "finite_domain_anec_pass": bool((group["anec_total_integral"].astype(float) >= 0.0).all()),
            "worst_anec_total_integral": float(worst["anec_total_integral"]),
            "p01_anec_total_integral": float(group["anec_total_integral"].astype(float).quantile(0.01)),
            "median_anec_total_integral": float(group["anec_total_integral"].astype(float).median()),
            "worst_negative_part": float(worst["anec_negative_part"]),
            "worst_positive_part": float(worst["anec_positive_part"]),
            "worst_center_s": float(worst["center_s"]),
            "worst_center_l": float(worst["center_l"]),
            "worst_center_stage": worst["center_stage"],
            "worst_center_region": worst["center_region"],
            "worst_seed_sources": worst["seed_sources"],
            "worst_inside_packet_live": bool(worst["center_inside_packet_live"]),
            "worst_dominant_negative_sector": worst["dominant_negative_sector"],
            "min_left_affine_extent": float(group["left_affine_extent"].astype(float).min()),
            "min_right_affine_extent": float(group["right_affine_extent"].astype(float).min()),
            "median_lambda_span": float(group["trace_lambda_span"].astype(float).median()),
        })
    return pd.DataFrame(rows).sort_values(["label", "branch"])


def _sector_summary_table(traces: pd.DataFrame) -> pd.DataFrame:
    if traces.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for (label, branch), group in traces.groupby(["label", "branch"], sort=False):
        for sector in SECTOR_ORDER:
            col = f"sector::{sector}::integral"
            neg_col = f"sector::{sector}::negative_part"
            if col not in group:
                continue
            values = group[col].astype(float)
            worst_idx = values.idxmin()
            worst = group.loc[worst_idx]
            rows.append({
                "label": label,
                "branch": branch,
                "sector": sector,
                "min_sector_integral": float(values.min()),
                "median_sector_integral": float(values.median()),
                "max_sector_negative_part": float(group[neg_col].astype(float).max()),
                "worst_sector_center_s": float(worst["center_s"]),
                "worst_sector_center_l": float(worst["center_l"]),
                "worst_sector_stage": worst["center_stage"],
                "worst_sector_region": worst["center_region"],
            })
    return pd.DataFrame(rows).sort_values(["label", "branch", "min_sector_integral"])


def build_finite_domain_anec_screen(
    component_dir: Path,
    *,
    seed_stride: int = 16,
    top_per_branch: int = 120,
    top_limit: int = 120,
    snec_top_windows_path: Path | None = None,
    sector_scales: dict[str, float] | None = None,
    total_mode: str = "geometric",
    parameterization: str = "affine",
    lambda_extent: float = 1.0e6,
    max_workers: int | None = 1,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    if parameterization not in {"affine", "lapse"}:
        raise ValueError(f"unknown finite-domain ANEC parameterization: {parameterization!r}")
    detail, metadata = _load_component_detail(component_dir)
    point_ledgers = _load_point_ledgers(component_dir, metadata["manifest"])
    ansatz_outputs, ansatz_metadata = build_composite_source_ansatz_screen(component_dir, promote_h=True)
    coeffs = _fit_coefficients(ansatz_outputs["sector_fits"])
    sector_points = _sector_assignment_points(detail)
    grids, center_tables = _build_label_grids(
        point_ledgers,
        sector_points,
        coeffs,
        sector_scales=sector_scales,
        total_mode=total_mode,
    )

    snec_top_windows = None
    if snec_top_windows_path is not None and Path(snec_top_windows_path).exists():
        snec_top_windows = pd.read_csv(snec_top_windows_path).head(int(top_limit) * 4)

    trace_rows: list[dict[str, Any]] = []
    seed_tables: list[pd.DataFrame] = []
    workers = max(1, _worker_count(max_workers))
    for label, grid in grids.items():
        centers = center_tables[label]
        _add_zone_masks(grid, centers)
        label_snec = None
        if snec_top_windows is not None and "label" in snec_top_windows:
            label_snec = snec_top_windows.loc[snec_top_windows["label"].astype(str).eq(label)]
        seeds = _select_seeds(
            centers,
            seed_stride=int(seed_stride),
            top_per_branch=int(top_per_branch),
            snec_top_windows=label_snec,
        )
        seed_tables.append(seeds)
        label_workers = min(workers, max(1, len(seeds)))
        seed_chunks = _chunk_frame(seeds, label_workers * 3)
        if label_workers <= 1 or len(seed_chunks) <= 1:
            for chunk in seed_chunks:
                trace_rows.extend(_trace_seed_chunk(grid, chunk, parameterization, float(lambda_extent)))
        else:
            with ProcessPoolExecutor(max_workers=label_workers) as pool:
                futures = [
                    pool.submit(_trace_seed_chunk, grid, chunk, parameterization, float(lambda_extent))
                    for chunk in seed_chunks
                ]
                for future in as_completed(futures):
                    trace_rows.extend(future.result())

    traces = pd.DataFrame(trace_rows)
    seeds = pd.concat(seed_tables, ignore_index=True) if seed_tables else pd.DataFrame()
    summary = _summary_table(traces)
    sector_summary = _sector_summary_table(traces)
    top_negative = (
        traces.sort_values(["label", "anec_total_integral"], ascending=[True, True])
        .groupby("label", sort=False)
        .head(int(top_limit))
        .reset_index(drop=True)
        if not traces.empty else pd.DataFrame()
    )
    outputs = {
        "seeds": seeds,
        "traces": traces,
        "summary": summary,
        "sector_summary": sector_summary,
        "top_negative": top_negative,
    }
    metadata.update({
        "ansatz_metadata": ansatz_metadata,
        "seed_stride": int(seed_stride),
        "top_per_branch": int(top_per_branch),
        "top_limit": int(top_limit),
        "snec_top_windows_path": str(snec_top_windows_path) if snec_top_windows_path is not None else "",
        "sector_scales": {sector: float((sector_scales or {}).get(sector, 1.0)) for sector in SECTOR_ORDER},
        "total_mode": str(total_mode),
        "parameterization": str(parameterization),
        "lambda_extent": float(lambda_extent),
        "max_workers": int(workers),
        "storage": "trace-level output is parquet; small seed, summary, sector, and top-negative outputs are csv/json",
    })
    return outputs, metadata


def write_finite_domain_anec_outputs(
    outdir: Path,
    component_dir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "seeds": outdir / "finite_domain_anec_seeds.csv",
        "traces": outdir / "finite_domain_anec_traces.parquet",
        "summary": outdir / "finite_domain_anec_summary.csv",
        "sector_summary": outdir / "finite_domain_anec_sector_summary.csv",
        "top_negative": outdir / "finite_domain_anec_top_negative.csv",
    }
    for key, path in paths.items():
        frame = outputs.get(key, pd.DataFrame())
        if path.suffix == ".parquet":
            frame.to_parquet(path, index=False, compression="zstd")
        else:
            frame.to_csv(path, index=False)
    manifest_path = outdir / "finite_domain_anec_manifest.json"
    manifest = {
        "caveat": (
            "Finite-domain radial ANEC diagnostic on demanded-source/component-sector ledgers. "
            "This reuses the radial null affine reparameterization from the SNEC harness and "
            "integrates Tkk over the longest available in-domain radial traces. It is not a "
            "complete-null-geodesic ANEC theorem, quantum RSET calculation, conservation proof, "
            "or physical matter-model solve."
        ),
        "component_source_dir": str(component_dir),
        "component_source_manifest": str(metadata["manifest_path"]),
        "component_detail": str(metadata["detail_path"]),
        "component_detail_sha256": sha256_file(metadata["detail_path"]),
        "ansatz": "composite_anisotropic_support_with_H",
        "seed_stride": int(metadata["seed_stride"]),
        "top_per_branch": int(metadata["top_per_branch"]),
        "top_limit": int(metadata["top_limit"]),
        "snec_top_windows_path": metadata["snec_top_windows_path"],
        "sector_scales": metadata["sector_scales"],
        "total_mode": metadata["total_mode"],
        "parameterization": metadata["parameterization"],
        "lambda_extent": float(metadata["lambda_extent"]),
        "max_workers": int(metadata["max_workers"]),
        "storage": metadata["storage"],
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
