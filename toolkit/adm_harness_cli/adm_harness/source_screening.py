from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from .source_ledger import (
    SourceCase,
    SourceParams,
    compute_case,
    sha256_file,
    summarize,
    top_bad_points,
    write_manifest,
)


@dataclass(frozen=True)
class SourceScreenContext:
    source_ledger_dir: Path
    manifest_path: Path
    manifest: dict[str, Any]
    params: SourceParams
    grid: dict[str, float | int]


def default_packet_profile(schedule: str) -> str:
    return "minimum_jerk" if schedule != "live_only" else "tanh"


def service_factor_label(params: SourceParams) -> str:
    value = float(params.V)
    text = f"{value:g}".replace("-", "m").replace(".", "p")
    return f"V{text}"


def load_spec_list(path: Path | None, default_specs: list[dict[str, Any]], description: str) -> list[dict[str, Any]]:
    if path is None:
        return [dict(spec) for spec in default_specs]
    raw = json.loads(path.read_text())
    if not isinstance(raw, list):
        raise ValueError(f"{description} spec file must contain a JSON list")
    specs: list[dict[str, Any]] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"{description} spec {idx} must be a JSON object")
        if "label" not in item:
            raise ValueError(f"{description} spec {idx} must include label")
        specs.append(dict(item))
    return specs


def select_specs(
    specs: list[dict[str, Any]],
    only_labels: list[str] | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    selected = specs
    if only_labels:
        labels = set(only_labels)
        selected = [spec for spec in selected if str(spec["label"]) in labels]
    if limit is not None:
        selected = selected[:limit]
    return selected


def source_grid_from_manifest(
    manifest: dict[str, Any],
    *,
    ns: int | None,
    nl: int | None,
    s_min: float | None,
    s_max: float | None,
    l_min: float | None,
    l_max: float | None,
    h_s: float | None,
    h_l: float | None,
) -> dict[str, float | int]:
    source_grid = manifest["grid"]
    return {
        "ns": int(source_grid["ns"] if ns is None else ns),
        "nl": int(source_grid["nl"] if nl is None else nl),
        "s_min": float(source_grid["s_min"] if s_min is None else s_min),
        "s_max": float(source_grid["s_max"] if s_max is None else s_max),
        "l_min": float(source_grid["l_min"] if l_min is None else l_min),
        "l_max": float(source_grid["l_max"] if l_max is None else l_max),
        "h_s": float(source_grid["h_s"] if h_s is None else h_s),
        "h_l": float(source_grid["h_l"] if h_l is None else h_l),
    }


def load_source_screen_context(
    source_ledger_dir: Path,
    *,
    ns: int | None,
    nl: int | None,
    s_min: float | None,
    s_max: float | None,
    l_min: float | None,
    l_max: float | None,
    h_s: float | None,
    h_l: float | None,
) -> SourceScreenContext:
    manifest_path = source_ledger_dir / "source_ledger_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    params = SourceParams(**manifest["params"])
    grid = source_grid_from_manifest(
        manifest,
        ns=ns,
        nl=nl,
        s_min=s_min,
        s_max=s_max,
        l_min=l_min,
        l_max=l_max,
        h_s=h_s,
        h_l=h_l,
    )
    return SourceScreenContext(source_ledger_dir, manifest_path, manifest, params, grid)


def resolve_manifest_path(source_ledger_dir: Path, value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    for candidate in (path, source_ledger_dir / path, source_ledger_dir / path.name):
        if candidate.exists():
            return candidate
    return source_ledger_dir / path


def source_channel_metrics(case: SourceCase, points: pd.DataFrame) -> dict[str, float | int | str]:
    _summary, compact, _stage, safety, _decision = summarize(points)
    channels = compact.set_index("channel")
    return {
        "case": case.name,
        "positive_packet_norm_live": int(safety["positive_packet_norm_live"].iloc[0]),
        "max_packet_norm_live": float(safety["max_packet_norm_live"].iloc[0]),
        "live_Tkk_fraction": float(channels.loc["neg_Tkk_radial", "live_packet_fraction"]),
        "live_p_l_fraction": float(channels.loc["abs_p_l", "live_packet_fraction"]),
        "live_j_l_fraction": float(channels.loc["abs_j_l", "live_packet_fraction"]),
        "live_pOmega_fraction": float(channels.loc["abs_pOmega", "live_packet_fraction"]),
        "live_Tkk_burden": float(channels.loc["neg_Tkk_radial", "live_packet_burden"]),
        "live_p_l_burden": float(channels.loc["abs_p_l", "live_packet_burden"]),
        "live_j_l_burden": float(channels.loc["abs_j_l", "live_packet_burden"]),
        "live_pOmega_burden": float(channels.loc["abs_pOmega", "live_packet_burden"]),
        "Tkk_point_peak": float(channels.loc["neg_Tkk_radial", "point_peak"]),
        "p_l_point_peak": float(channels.loc["abs_p_l", "point_peak"]),
        "j_l_point_peak": float(channels.loc["abs_j_l", "point_peak"]),
        "pOmega_point_peak": float(channels.loc["abs_pOmega", "point_peak"]),
        "rho_packet_live_burden": float(channels.loc["neg_rho_packet", "live_packet_burden"]),
        "rho_packet_live_peak": float(channels.loc["neg_rho_packet", "live_packet_point_peak"]),
        "max_any_point_peak": float(channels["point_peak"].max()),
    }


CaseBuilder = Callable[[str, dict[str, Any], SourceParams], SourceCase]
RowBuilder = Callable[[str, dict[str, Any], SourceCase, pd.DataFrame], dict[str, Any]]
TopLabelValue = Callable[[str, SourceCase], Any]


def run_source_screen(
    *,
    context: SourceScreenContext,
    specs: list[dict[str, Any]],
    outdir: Path,
    summary_filename: str,
    top_filename: str,
    manifest_filename: str,
    case_builder: CaseBuilder,
    row_builder: RowBuilder,
    top_label_column: str = "screen_label",
    top_label_value: TopLabelValue | None = None,
    top_limit: int = 10,
    spec_file: Path | None = None,
) -> list[dict[str, Any]]:
    outdir.mkdir(parents=True, exist_ok=True)
    summary_path = outdir / summary_filename
    top_path = outdir / top_filename
    rows: list[dict[str, Any]] = []
    top_rows: list[pd.DataFrame] = []

    with summary_path.open("w", newline="") as handle:
        writer: csv.DictWriter | None = None
        for spec in specs:
            label = str(spec["label"])
            case = case_builder(label, spec, context.params)
            started_at = time.perf_counter()
            print(
                json.dumps({
                    "event": "screen_case_start",
                    "label": label,
                    "case": case.name,
                    "grid": context.grid,
                }),
                flush=True,
            )
            points = compute_case(case, progress=False, **context.grid)
            row = row_builder(label, spec, case, points)
            row["elapsed_s"] = round(time.perf_counter() - started_at, 3)
            rows.append(row)
            if writer is None:
                writer = csv.DictWriter(handle, fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
            handle.flush()
            print(json.dumps(row), flush=True)
            top = top_bad_points(points, limit=top_limit)
            top.insert(0, top_label_column, top_label_value(label, case) if top_label_value else label)
            top_rows.append(top)

    if top_rows:
        pd.concat(top_rows, ignore_index=True).to_csv(top_path, index=False)
    else:
        pd.DataFrame().to_csv(top_path, index=False)

    manifest_out: dict[str, Any] = {
        "source_manifest": str(context.manifest_path),
        "summary": str(summary_path),
        "top_bad_points": str(top_path),
        "rows": len(rows),
        "grid": context.grid,
        "spec_file": str(spec_file) if spec_file else None,
        "summary_sha256": sha256_file(summary_path),
        "top_bad_points_sha256": sha256_file(top_path),
    }
    files = context.manifest.get("files", {})
    if "point_ledger" in files:
        point_ledger = resolve_manifest_path(context.source_ledger_dir, files["point_ledger"])
        manifest_out["source_point_ledger"] = str(point_ledger)
        manifest_out["source_point_ledger_sha256"] = sha256_file(point_ledger)
    write_manifest(outdir / manifest_filename, manifest_out)
    return rows
