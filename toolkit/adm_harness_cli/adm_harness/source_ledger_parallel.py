from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import (
    CHANNELS,
    SourceCase,
    channel_badness,
    compute_case,
    einstein_tensor_at,
    live_packet_mask,
    projections,
    region_name,
    stage_name,
)


@dataclass(frozen=True)
class SourceLedgerShard:
    index: int
    start_row: int
    end_row: int
    s_values: tuple[float, ...]


def resolve_s_shard_count(ns: int, jobs: int, s_shards: int | None = None) -> int:
    """Return the bounded number of contiguous s-row shards for a source-ledger run."""

    if ns < 3:
        raise ValueError(f"source-ledger grid must be at least 3 x 3, got {ns} s rows")
    if jobs < 1:
        raise ValueError(f"jobs must be positive, got {jobs}")
    if s_shards is not None and s_shards < 1:
        raise ValueError(f"s_shards must be positive when provided, got {s_shards}")
    requested = int(s_shards) if s_shards is not None else max(int(jobs), int(jobs) * 4)
    return min(int(ns), requested)


def build_s_shards(s_grid: np.ndarray, jobs: int, s_shards: int | None = None) -> list[SourceLedgerShard]:
    shard_count = resolve_s_shard_count(len(s_grid), jobs, s_shards)
    chunks = np.array_split(np.arange(len(s_grid)), shard_count)
    shards: list[SourceLedgerShard] = []
    for index, row_indices in enumerate(chunks):
        if len(row_indices) == 0:
            continue
        start_row = int(row_indices[0]) + 1
        end_row = int(row_indices[-1]) + 1
        shards.append(
            SourceLedgerShard(
                index=index,
                start_row=start_row,
                end_row=end_row,
                s_values=tuple(float(s_grid[row_index]) for row_index in row_indices),
            )
        )
    return shards


def _compute_s_shard(
    case: SourceCase,
    shard: SourceLedgerShard,
    l_values: tuple[float, ...],
    ds: float,
    dl: float,
    h_s: float,
    h_l: float,
) -> tuple[int, list[dict[str, Any]]]:
    params = case.params
    rows: list[dict[str, Any]] = []
    for s in shard.s_values:
        for l in l_values:
            base = {
                "case": case.name,
                "s": float(s),
                "l": float(l),
                "stage": stage_name(float(s), params),
                "region": region_name(float(s), float(l), params),
                "inside_packet_geom": abs(float(l) - float(s)) <= params.Rpass,
                "inside_packet_live": live_packet_mask(float(s), float(l), params),
                "cell_area": ds * dl,
            }
            try:
                einstein, diagnostics = einstein_tensor_at(float(s), float(l), params, h_s, h_l)
                projected = projections(float(s), float(l), einstein, params)
                row = {**base, **projected, **diagnostics}
                row["point_weight"] = 1.0
                row["volume_weight"] = float(projected["spatial_volume_density"] * ds * dl)
                for channel in CHANNELS:
                    bad = channel_badness(row, channel)
                    row[f"bad_{channel}"] = bad
                    row[f"point_burden_{channel}"] = bad
                    row[f"volume_burden_{channel}"] = bad * row["volume_weight"]
                rows.append(row)
            except Exception as exc:
                rows.append({**base, "error": repr(exc)})
    return shard.index, rows


def _write_progress(path: Path | None, event: dict[str, Any]) -> None:
    if path is None:
        return
    payload = {"timestamp": time.time(), **event}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _write_shard_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def compute_case_sharded(
    case: SourceCase,
    ns: int,
    nl: int,
    s_min: float = -0.35,
    s_max: float = 1.65,
    l_min: float = -2.80,
    l_max: float = 2.80,
    h_s: float = 2.5e-3,
    h_l: float = 2.5e-3,
    *,
    jobs: int = 1,
    s_shards: int | None = None,
    progress: bool = True,
) -> pd.DataFrame:
    """Compute a source ledger by splitting independent s-row bands across workers."""

    if jobs <= 1:
        return compute_case(case, ns, nl, s_min, s_max, l_min, l_max, h_s, h_l, progress=progress)
    if ns < 3 or nl < 3:
        raise ValueError(f"source-ledger grid must be at least 3 x 3, got {ns} x {nl}")

    s_grid = np.linspace(s_min, s_max, ns)
    l_grid = np.linspace(l_min, l_max, nl)
    ds = float((s_max - s_min) / max(ns - 1, 1))
    dl = float((l_max - l_min) / max(nl - 1, 1))
    shards = build_s_shards(s_grid, jobs, s_shards)
    max_workers = min(int(jobs), len(shards))
    if progress:
        print(
            f"{case.name}: source-ledger sharded compute {ns}x{nl} "
            f"with {max_workers} workers across {len(shards)} s-shards",
            flush=True,
        )

    shard_rows: dict[int, list[dict[str, Any]]] = {}
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_compute_s_shard, case, shard, tuple(float(l) for l in l_grid), ds, dl, h_s, h_l): shard
            for shard in shards
        }
        completed = 0
        for future in as_completed(futures):
            shard = futures[future]
            index, rows = future.result()
            shard_rows[index] = rows
            completed += 1
            if progress:
                print(
                    f"{case.name}: shard {completed}/{len(shards)} "
                    f"(s rows {shard.start_row}-{shard.end_row}/{ns})",
                    flush=True,
                )

    rows: list[dict[str, Any]] = []
    for shard in shards:
        rows.extend(shard_rows[shard.index])
    return pd.DataFrame(rows)


def compute_case_sharded_parquet(
    case: SourceCase,
    ns: int,
    nl: int,
    s_min: float = -0.35,
    s_max: float = 1.65,
    l_min: float = -2.80,
    l_max: float = 2.80,
    h_s: float = 2.5e-3,
    h_l: float = 2.5e-3,
    *,
    jobs: int = 1,
    s_shards: int | None = None,
    shard_dir: Path,
    progress_log: Path | None = None,
    force: bool = False,
    progress: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compute a sharded source ledger while checkpointing each shard as Parquet.

    The returned frame preserves the historical in-memory API for summary table
    generation, but every completed shard is durable before final aggregation.
    A rerun with the same shard directory and ``force=False`` reuses existing
    shard files.
    """

    if jobs <= 1:
        points = compute_case(case, ns, nl, s_min, s_max, l_min, l_max, h_s, h_l, progress=progress)
        return points, {"source_compute": "serial", "jobs": 1, "s_shards": 1}
    if ns < 3 or nl < 3:
        raise ValueError(f"source-ledger grid must be at least 3 x 3, got {ns} x {nl}")

    shard_dir.mkdir(parents=True, exist_ok=True)
    if progress_log is not None:
        progress_log.parent.mkdir(parents=True, exist_ok=True)
        if force and progress_log.exists():
            progress_log.unlink()

    s_grid = np.linspace(s_min, s_max, ns)
    l_grid = np.linspace(l_min, l_max, nl)
    ds = float((s_max - s_min) / max(ns - 1, 1))
    dl = float((l_max - l_min) / max(nl - 1, 1))
    shards = build_s_shards(s_grid, jobs, s_shards)
    max_workers = min(int(jobs), len(shards))
    manifest_path = shard_dir / "source_ledger_shard_manifest.json"
    start_time = time.time()
    shard_records: dict[int, dict[str, Any]] = {}
    if progress:
        print(
            f"{case.name}: source-ledger parquet checkpoint compute {ns}x{nl} "
            f"with {max_workers} workers across {len(shards)} s-shards",
            flush=True,
        )
    _write_progress(
        progress_log,
        {
            "event": "sharded_parquet_start",
            "case": case.name,
            "ns": int(ns),
            "nl": int(nl),
            "jobs": int(max_workers),
            "s_shards": int(len(shards)),
        },
    )

    pending: list[SourceLedgerShard] = []
    for shard in shards:
        shard_path = shard_dir / f"part-{shard.index:04d}_s{shard.start_row:04d}-{shard.end_row:04d}.parquet"
        if shard_path.exists() and not force:
            frame = pd.read_parquet(shard_path)
            shard_records[shard.index] = {
                "index": int(shard.index),
                "start_row": int(shard.start_row),
                "end_row": int(shard.end_row),
                "rows": int(len(frame)),
                "path": str(shard_path),
                "status": "reused",
            }
            _write_progress(
                progress_log,
                {
                    "event": "shard_reused",
                    "case": case.name,
                    "shard": int(shard.index),
                    "start_row": int(shard.start_row),
                    "end_row": int(shard.end_row),
                    "rows": int(len(frame)),
                    "path": str(shard_path),
                },
            )
        else:
            pending.append(shard)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_compute_s_shard, case, shard, tuple(float(l) for l in l_grid), ds, dl, h_s, h_l): shard
            for shard in pending
        }
        completed = len(shard_records)
        for future in as_completed(futures):
            shard = futures[future]
            shard_start = time.time()
            index, rows = future.result()
            frame = pd.DataFrame(rows)
            shard_path = shard_dir / f"part-{index:04d}_s{shard.start_row:04d}-{shard.end_row:04d}.parquet"
            frame.to_parquet(shard_path, index=False, compression="zstd")
            completed += 1
            shard_records[index] = {
                "index": int(index),
                "start_row": int(shard.start_row),
                "end_row": int(shard.end_row),
                "rows": int(len(frame)),
                "path": str(shard_path),
                "status": "computed",
                "write_elapsed_seconds": float(time.time() - shard_start),
            }
            _write_progress(
                progress_log,
                {
                    "event": "shard_written",
                    "case": case.name,
                    "shard": int(index),
                    "completed": int(completed),
                    "total": int(len(shards)),
                    "start_row": int(shard.start_row),
                    "end_row": int(shard.end_row),
                    "rows": int(len(frame)),
                    "path": str(shard_path),
                },
            )
            if progress:
                print(
                    f"{case.name}: shard {completed}/{len(shards)} "
                    f"(s rows {shard.start_row}-{shard.end_row}/{ns}) wrote {len(frame)} rows",
                    flush=True,
                )
            _write_shard_manifest(
                manifest_path,
                {
                    "case": case.name,
                    "grid": {"ns": int(ns), "nl": int(nl), "s_min": s_min, "s_max": s_max, "l_min": l_min, "l_max": l_max},
                    "jobs": int(max_workers),
                    "s_shards": int(len(shards)),
                    "shards": [shard_records[key] for key in sorted(shard_records)],
                    "complete": len(shard_records) == len(shards),
                },
            )

    ordered_frames = [pd.read_parquet(shard_records[shard.index]["path"]) for shard in shards]
    points = pd.concat(ordered_frames, ignore_index=True) if ordered_frames else pd.DataFrame()
    elapsed = float(time.time() - start_time)
    manifest = {
        "case": case.name,
        "grid": {"ns": int(ns), "nl": int(nl), "s_min": s_min, "s_max": s_max, "l_min": l_min, "l_max": l_max},
        "jobs": int(max_workers),
        "s_shards": int(len(shards)),
        "rows": int(len(points)),
        "elapsed_seconds": elapsed,
        "shards": [shard_records[key] for key in sorted(shard_records)],
        "complete": len(shard_records) == len(shards),
    }
    _write_shard_manifest(manifest_path, manifest)
    _write_progress(
        progress_log,
        {
            "event": "sharded_parquet_complete",
            "case": case.name,
            "rows": int(len(points)),
            "elapsed_seconds": elapsed,
            "manifest": str(manifest_path),
        },
    )
    return points, {
        "source_compute": "sharded_parquet_checkpoint",
        "jobs": int(max_workers),
        "s_shards": int(len(shards)),
        "shard_dir": str(shard_dir),
        "shard_manifest": str(manifest_path),
        "progress_log": str(progress_log) if progress_log is not None else "",
        "elapsed_seconds": elapsed,
    }
