"""Scalar worldline morphology proxy for the White Casimir audit."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

import numpy as np

from .loop_gen import generate_loops


def _grid_points(grid: Mapping[str, np.ndarray]) -> np.ndarray:
    return np.stack([grid["x"], grid["y"], grid["z"]], axis=-1).reshape(-1, 3)


def _grid_shape(grid: Mapping[str, np.ndarray]) -> tuple[int, int]:
    return tuple(int(v) for v in grid["x"].shape)


def _geometry_config_hash(geometry: object) -> str:
    if is_dataclass(geometry):
        payload: Any = asdict(geometry)
    else:
        payload = repr(geometry)
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def proxy_status_for_loop_method(loop_method: str) -> str:
    if loop_method == "v_loop":
        return "paper_style_v_loop_morphology_proxy_not_si_normalized"
    return "reproduction_proxy_not_exact_white_method"


def _hit_counts_for_scaled_points(geometry: object, points: np.ndarray) -> np.ndarray:
    ids = geometry.body_ids_for_points(points)
    n_loops = ids.shape[0]
    counts = np.zeros(n_loops, dtype=np.int16)
    for body_id in np.unique(ids):
        if body_id > 0:
            counts += np.any(ids == body_id, axis=1)
    return counts


def estimate_density_proxy(
    geometry: object,
    grid: Mapping[str, np.ndarray],
    loops: np.ndarray,
    scale_grid: np.ndarray | list[float],
    loop_method: str = "brownian_bridge",
    random_seed: int | None = None,
) -> dict[str, Any]:
    """Estimate a normalized scalar morphology proxy.

    The proxy marks translated/scaled loops that touch two or more distinct
    bodies and accumulates a negative scale-weighted score. It is not an exact
    White et al. worldline reproduction and carries no SI normalization.
    """

    loop_arr = np.asarray(loops, dtype=float)
    if loop_arr.ndim != 3 or loop_arr.shape[2] != 3:
        raise ValueError("loops must have shape (n_loops, n_points, 3)")
    scales = np.asarray(scale_grid, dtype=float)
    if scales.ndim != 1 or np.any(scales <= 0.0):
        raise ValueError("scale_grid must be a positive 1-D array")

    centers = _grid_points(grid)
    values = np.zeros(len(centers), dtype=float)
    touch_counts = np.zeros(len(centers), dtype=np.int32)
    start = time.perf_counter()
    for center_index, center in enumerate(centers):
        score = 0.0
        touches = 0
        translated = loop_arr + center[None, None, :]
        for scale in scales:
            scaled = center[None, None, :] + scale * loop_arr
            counts = _hit_counts_for_scaled_points(geometry, scaled)
            hit = counts >= 2
            if np.any(hit):
                touches += int(np.count_nonzero(hit))
                score -= float(np.count_nonzero(hit)) / float(scale**4)
        values[center_index] = score / max(loop_arr.shape[0], 1)
        touch_counts[center_index] = touches
    elapsed_s = time.perf_counter() - start

    field = values.reshape(_grid_shape(grid))
    touch_field = touch_counts.reshape(_grid_shape(grid))
    metadata = {
        "loop_method": loop_method,
        "proxy_status": proxy_status_for_loop_method(loop_method),
        "n_loops": int(loop_arr.shape[0]),
        "n_points_per_loop": int(loop_arr.shape[1]),
        "scale_grid": [float(v) for v in scales],
        "random_seed": random_seed,
        "geometry_config_hash": _geometry_config_hash(geometry),
        "normalization": "normalized_morphology_proxy",
        "elapsed_s": elapsed_s,
        "grid_points": int(len(centers)),
        "loop_scale_tests": int(len(centers) * len(scales) * loop_arr.shape[0]),
        "loop_scale_tests_per_s": float(len(centers) * len(scales) * loop_arr.shape[0] / max(elapsed_s, 1.0e-12)),
    }
    return {"density_proxy": field, "touch_count": touch_field, "metadata": metadata}


def generate_and_estimate_density_proxy(
    geometry: object,
    grid: Mapping[str, np.ndarray],
    n_loops: int,
    n_points: int,
    seed: int,
    scale_grid: np.ndarray | list[float],
    loop_method: str = "brownian_bridge",
) -> dict[str, Any]:
    loops = generate_loops(n_loops=n_loops, n_points=n_points, seed=seed, method=loop_method)
    return estimate_density_proxy(
        geometry,
        grid,
        loops,
        scale_grid,
        loop_method=loop_method,
        random_seed=seed,
    )
