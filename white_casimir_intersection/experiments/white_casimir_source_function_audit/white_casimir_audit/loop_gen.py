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


def generate_loops(n_loops: int, n_points: int, seed: int, method: str = "brownian_bridge") -> np.ndarray:
    if method != "brownian_bridge":
        raise NotImplementedError("Only brownian_bridge proxy loops are implemented in this Stage 2 smoke slice.")
    return generate_brownian_bridge_loops(n_loops, n_points, seed)
