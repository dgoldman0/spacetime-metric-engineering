from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .scalar_source_screen import scalar_proxy_fields_from_phi, score_scalar_candidate
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class ScalarSolveConfig:
    label: str
    xi: float = 1.0
    top_centers: int = 24
    radial_width: float = 0.22
    temporal_width: float = 0.16
    max_abs_phi: float = 1.0
    maxiter: int = 120
    checkpoint_every: int = 5
    live_penalty: float = 2.0
    gradient_penalty: float = 0.10
    amplitude_penalty: float = 0.25
    p_l_penalty: float = 0.15
    angular_current_penalty: float = 0.05
    focus_quantile: float = 0.985


def _finite(values: pd.Series | np.ndarray, default: float = 0.0) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return np.nan_to_num(arr, nan=default, posinf=default, neginf=default)


def _build_basis(points: pd.DataFrame, config: ScalarSolveConfig) -> tuple[np.ndarray, pd.DataFrame]:
    ranked = points.sort_values("volume_burden_neg_Tkk_radial", ascending=False).head(int(config.top_centers)).copy()
    s = _finite(points["s"])
    l = _finite(points["l"])
    basis_columns: list[np.ndarray] = []
    center_rows: list[dict[str, Any]] = []
    for idx, center in enumerate(ranked.itertuples(index=False), start=1):
        s0 = float(center.s)
        l0 = float(center.l)
        ds = (s - s0) / max(float(config.temporal_width), 1.0e-12)
        dl = (l - l0) / max(float(config.radial_width), 1.0e-12)
        bump = np.exp(-0.5 * (ds * ds + dl * dl))
        max_abs = float(np.max(np.abs(bump)))
        if max_abs > 0.0:
            bump = bump / max_abs
        basis_columns.append(bump)
        center_rows.append({
            "basis_index": idx - 1,
            "s": s0,
            "l": l0,
            "stage": center.stage,
            "region": center.region,
            "inside_packet_live": bool(center.inside_packet_live),
            "bad_neg_Tkk_radial": float(center.bad_neg_Tkk_radial),
            "volume_burden_neg_Tkk_radial": float(center.volume_burden_neg_Tkk_radial),
        })
    if not basis_columns:
        raise ValueError("no radial-null centers available for scalar solve")
    # Add broad stage/region aids so the optimizer is not forced into single
    # point spikes. These remain smooth because the Gaussian basis dominates.
    for stage in ["entry_precatch", "catch_rematch"]:
        mask = points["stage"].astype(str).eq(stage).astype(float).to_numpy()
        if np.any(mask):
            support = _finite(points.get("W_raw", points.get("W", np.ones(len(points)))))
            col = mask * support
            if np.max(np.abs(col)) > 0.0:
                basis_columns.append(col / np.max(np.abs(col)))
                center_rows.append({
                    "basis_index": len(basis_columns) - 1,
                    "s": float("nan"),
                    "l": float("nan"),
                    "stage": stage,
                    "region": "broad_stage",
                    "inside_packet_live": False,
                    "bad_neg_Tkk_radial": float("nan"),
                    "volume_burden_neg_Tkk_radial": float("nan"),
                })
    basis = np.column_stack(basis_columns)
    return basis, pd.DataFrame(center_rows)


def _coverage(demand: np.ndarray, supply: np.ndarray, weight: np.ndarray) -> float:
    denom = float(np.sum(weight * np.abs(demand)))
    if denom <= 0.0:
        return float("nan")
    return float(np.sum(weight * np.minimum(np.abs(supply), np.abs(demand))) / denom)


def _relative_l1(demand: np.ndarray, supply: np.ndarray, weight: np.ndarray) -> float:
    denom = float(np.sum(weight * np.abs(demand)))
    if denom <= 0.0:
        return float("nan")
    return float(np.sum(weight * np.abs(demand - supply)) / denom)


class ScalarFieldSolver:
    def __init__(self, points: pd.DataFrame, config: ScalarSolveConfig, outdir: Path):
        self.points = points.reset_index(drop=True)
        self.config = config
        self.outdir = outdir
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.basis, self.centers = _build_basis(self.points, config)
        self.centers.to_csv(self.outdir / "scalar_field_solve_basis_centers.csv", index=False)
        self.iteration = 0
        self.start_time = time.time()
        self.best: dict[str, Any] | None = None
        self.history_rows: list[dict[str, Any]] = []
        self.demand = _finite(self.points["bad_neg_Tkk_radial"])
        self.weight = _finite(self.points.get("volume_weight", np.ones(len(self.points))), default=1.0)
        threshold = float(np.quantile(self.demand, float(config.focus_quantile)))
        self.focus = self.demand >= threshold
        # Always include the explicit basis centers in the focus even if the
        # quantile threshold is flat.
        center_coords = set(
            zip(
                self.centers["s"].dropna().round(12).astype(float),
                self.centers["l"].dropna().round(12).astype(float),
            )
        )
        if center_coords:
            coords = list(zip(self.points["s"].round(12).astype(float), self.points["l"].round(12).astype(float)))
            self.focus |= np.array([coord in center_coords for coord in coords], dtype=bool)
        self.live = self.points["inside_packet_live"].astype(bool).to_numpy()

    def phi_from_coeffs(self, coeffs: np.ndarray) -> np.ndarray:
        raw = self.basis @ np.asarray(coeffs, dtype=float)
        return self.config.max_abs_phi * np.tanh(raw)

    def evaluate(self, coeffs: np.ndarray) -> tuple[float, dict[str, Any], pd.DataFrame]:
        phi = self.phi_from_coeffs(coeffs)
        proxy = scalar_proxy_fields_from_phi(self.points, phi, self.config.xi)
        supply = np.maximum(-_finite(proxy["scalar_Tkk_radial_proxy"]), 0.0)
        focus_weight = self.weight * np.where(self.focus, 1.0, 0.10)
        radial_residual = _relative_l1(self.demand, supply, focus_weight)
        radial_coverage = _coverage(self.demand, supply, focus_weight)
        live_stress = float(np.sum(self.weight[self.live] * _finite(proxy.loc[self.live, "scalar_stress_abs_proxy"])))
        total_stress = float(np.sum(self.weight * _finite(proxy["scalar_stress_abs_proxy"])))
        live_fraction = live_stress / total_stress if total_stress > 0.0 else 0.0
        max_abs_phi = float(np.max(np.abs(phi)))
        max_grad = float(math.sqrt(np.max(_finite(proxy["grad_norm_proxy"]))))
        channel_score = score_scalar_candidate(self.points, proxy)
        effective_margin = float(1.0 - 8.0 * math.pi * self.config.xi * max_abs_phi * max_abs_phi)
        p_l_residual = float(channel_score["abs_p_l_relative_l1_residual"])
        j_residual = float(channel_score["abs_j_l_relative_l1_residual"])
        omega_residual = float(channel_score["abs_pOmega_relative_l1_residual"])
        loss = (
            radial_residual
            + self.config.live_penalty * live_fraction
            + self.config.gradient_penalty * max(0.0, max_grad - 1.0) ** 2
            + self.config.amplitude_penalty * max(0.0, max_abs_phi - 1.0) ** 2
            + self.config.amplitude_penalty * max(0.0, 0.10 - effective_margin) ** 2
            + self.config.p_l_penalty * p_l_residual
            + self.config.angular_current_penalty * (j_residual + omega_residual)
        )
        metrics = {
            "iteration": int(self.iteration),
            "elapsed_s": float(time.time() - self.start_time),
            "loss": float(loss),
            "radial_null_relative_l1_residual": float(radial_residual),
            "radial_null_coverage": float(radial_coverage),
            "scalar_live_stress_fraction": float(live_fraction),
            "max_abs_phi": max_abs_phi,
            "max_grad_phi_proxy": max_grad,
            "effective_coupling_margin_proxy": effective_margin,
            "abs_p_l_relative_l1_residual": p_l_residual,
            "abs_j_l_relative_l1_residual": j_residual,
            "abs_pOmega_relative_l1_residual": omega_residual,
            "mean_coverage": float(channel_score["mean_coverage"]),
            "mean_relative_l1_residual": float(channel_score["mean_relative_l1_residual"]),
        }
        return float(loss), metrics, proxy

    def _write_checkpoint(self, coeffs: np.ndarray, metrics: dict[str, Any], proxy: pd.DataFrame) -> None:
        phi = self.phi_from_coeffs(coeffs)
        np.savez_compressed(
            self.outdir / "scalar_field_solve_latest.npz",
            coeffs=np.asarray(coeffs, dtype=float),
            phi=phi,
        )
        metrics_path = self.outdir / "scalar_field_solve_latest.json"
        write_manifest(metrics_path, {
            **metrics,
            "label": self.config.label,
            "xi": self.config.xi,
            "top_centers": self.config.top_centers,
            "status": "running",
            "heartbeat_unix": time.time(),
        })
        top = self.points[[
            "s",
            "l",
            "stage",
            "region",
            "inside_packet_live",
            "bad_neg_Tkk_radial",
            "volume_burden_neg_Tkk_radial",
        ]].copy()
        top["phi"] = phi
        top["scalar_neg_Tkk_supply"] = np.maximum(-_finite(proxy["scalar_Tkk_radial_proxy"]), 0.0)
        top.sort_values("volume_burden_neg_Tkk_radial", ascending=False).head(40).to_csv(
            self.outdir / "scalar_field_solve_top_demand_tracking.csv",
            index=False,
        )
        pd.DataFrame(self.history_rows).to_csv(self.outdir / "scalar_field_solve_progress.csv", index=False)

    def objective(self, coeffs: np.ndarray) -> float:
        loss, _metrics, _proxy = self.evaluate(coeffs)
        return loss

    def callback(self, coeffs: np.ndarray) -> None:
        self.iteration += 1
        loss, metrics, proxy = self.evaluate(coeffs)
        self.history_rows.append(metrics)
        if self.best is None or loss < float(self.best["loss"]):
            self.best = dict(metrics)
            np.savez_compressed(
                self.outdir / "scalar_field_solve_best.npz",
                coeffs=np.asarray(coeffs, dtype=float),
                phi=self.phi_from_coeffs(coeffs),
            )
            write_manifest(self.outdir / "scalar_field_solve_best.json", {**metrics, "label": self.config.label})
        if self.iteration == 1 or self.iteration % max(1, self.config.checkpoint_every) == 0:
            self._write_checkpoint(coeffs, metrics, proxy)
            print(json.dumps(metrics), flush=True)

    def solve(self) -> dict[str, Any]:
        initial = np.full(self.basis.shape[1], 0.05, dtype=float)
        initial[1::2] *= -0.5
        bounds = [(-2.0, 2.0)] * len(initial)
        result = minimize(
            self.objective,
            initial,
            method="L-BFGS-B",
            bounds=bounds,
            callback=self.callback,
            options={"maxiter": int(self.config.maxiter), "ftol": 1.0e-8, "maxls": 20},
        )
        self.iteration += 1
        loss, metrics, proxy = self.evaluate(result.x)
        metrics.update({
            "status": "completed",
            "optimizer_success": bool(result.success),
            "optimizer_message": str(result.message),
            "optimizer_nit": int(result.nit),
            "optimizer_nfev": int(result.nfev),
        })
        self.history_rows.append(metrics)
        self._write_checkpoint(result.x, metrics, proxy)
        write_manifest(self.outdir / "scalar_field_solve_final.json", metrics)
        pd.DataFrame(self.history_rows).to_csv(self.outdir / "scalar_field_solve_progress.csv", index=False)
        return metrics


def run_scalar_field_solve(
    *,
    point_ledger_path: Path,
    outdir: Path,
    config: ScalarSolveConfig,
) -> dict[str, Any]:
    points = pd.read_csv(point_ledger_path)
    solver = ScalarFieldSolver(points, config, outdir)
    final = solver.solve()
    manifest = {
        "point_ledger": str(point_ledger_path),
        "point_ledger_sha256": sha256_file(point_ledger_path),
        "config": config.__dict__,
        "final": final,
        "files": {
            "progress": str(outdir / "scalar_field_solve_progress.csv"),
            "latest": str(outdir / "scalar_field_solve_latest.json"),
            "best": str(outdir / "scalar_field_solve_best.json"),
            "final": str(outdir / "scalar_field_solve_final.json"),
            "top_demand_tracking": str(outdir / "scalar_field_solve_top_demand_tracking.csv"),
            "basis_centers": str(outdir / "scalar_field_solve_basis_centers.csv"),
        },
        "caveat": "Fixed-metric reduced scalar field solve over a localized basis; not a coupled scalar-tensor backreaction solve.",
    }
    write_manifest(outdir / "scalar_field_solve_manifest.json", manifest)
    return final
