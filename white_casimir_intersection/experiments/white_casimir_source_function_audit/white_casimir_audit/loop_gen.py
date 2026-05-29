"""Closed-loop generators for scalar worldline smoke tests."""

from __future__ import annotations

import numpy as np


def generate_brownian_bridge_loops(
    n_loops: int,
    n_points: int,
    seed: int,
    dimensions: int = 3,
    normalize_rms: bool = True,
) -> np.ndarray:
    """Generate reproducible closed Gaussian loops.

    This is a Brownian-bridge smoke generator, not the exact v-loop method
    described by White et al. Results using it must remain labeled as
    reproduction proxies.
    """

    if n_loops <= 0:
        raise ValueError("n_loops must be positive")
    if n_points < 4:
        raise ValueError("n_points must be at least 4")
    if dimensions <= 0:
        raise ValueError("dimensions must be positive")

    rng = np.random.default_rng(seed)
    increments = rng.normal(0.0, 1.0 / np.sqrt(n_points), size=(n_loops, n_points - 1, dimensions))
    path = np.concatenate(
        [np.zeros((n_loops, 1, dimensions)), np.cumsum(increments, axis=1)],
        axis=1,
    )
    drift = np.linspace(0.0, 1.0, n_points, dtype=float)[None, :, None] * path[:, -1:, :]
    loops = path - drift
    loops = loops - loops.mean(axis=1, keepdims=True)
    if normalize_rms:
        rms = np.sqrt(np.mean(np.sum(loops**2, axis=2), axis=1))
        loops = loops / np.maximum(rms[:, None, None], 1.0e-12)
    return loops.astype(np.float64)


def generate_v_loops(
    n_loops: int,
    n_points: int,
    seed: int,
    dimensions: int = 3,
) -> np.ndarray:
    """Generate unit loops using the v-loop construction quoted by White et al.

    The implementation follows the paper's Eq. 7-9 summary coordinate by
    coordinate. The sampled ``w_i`` use the paper's ``exp(-w_i^2)`` Gaussian
    convention, i.e. a normal distribution with variance ``1/2``.
    """

    if n_loops <= 0:
        raise ValueError("n_loops must be positive")
    if n_points < 4:
        raise ValueError("n_points must be at least 4")
    if dimensions <= 0:
        raise ValueError("dimensions must be positive")

    n = n_points
    rng = np.random.default_rng(seed)
    w = rng.normal(0.0, 1.0 / np.sqrt(2.0), size=(n_loops, n - 1, dimensions))
    vbar = np.zeros_like(w)
    vbar[:, 0, :] = np.sqrt(2.0 / n) * w[:, 0, :]
    for i in range(2, n):
        idx = i - 1
        vbar[:, idx, :] = np.sqrt((2.0 / n) * ((n + 1.0 - i) / (n + 2.0 - i))) * w[:, idx, :]

    v = np.zeros((n_loops, n, dimensions), dtype=float)
    partial = np.zeros((n_loops, dimensions), dtype=float)
    for i in range(2, n):
        idx = i - 1
        v[:, idx, :] = vbar[:, idx, :] - partial / (n + 2.0 - i)
        partial += v[:, idx, :]

    y = np.zeros((n_loops, n, dimensions), dtype=float)
    y[:, 0, :] = (
        vbar[:, 0, :]
        - np.sum(((n - np.arange(2, n)) + 0.5)[None, :, None] * v[:, 1 : n - 1, :], axis=1)
    ) / n
    for i in range(2, n):
        idx = i - 1
        y[:, idx, :] = y[:, idx - 1, :] + v[:, idx, :]
    y[:, n - 1, :] = -np.sum(y[:, : n - 1, :], axis=1)
    return y.astype(np.float64)


def generate_loops(n_loops: int, n_points: int, seed: int, method: str = "brownian_bridge") -> np.ndarray:
    if method == "brownian_bridge":
        return generate_brownian_bridge_loops(n_loops, n_points, seed)
    if method == "v_loop":
        return generate_v_loops(n_loops, n_points, seed)
    raise ValueError(f"unknown loop generation method: {method}")
