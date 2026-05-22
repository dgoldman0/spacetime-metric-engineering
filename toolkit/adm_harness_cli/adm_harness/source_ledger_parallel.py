from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
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
