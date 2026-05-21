from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .composite_source_ansatz import build_composite_source_ansatz_screen
from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


COMPONENT_TO_SECTOR = {
    "A_infrastructure_radial_null_support": "infrastructure_radial_support",
    "B_core_radial_pressure_balance": "infrastructure_radial_support",
    "I_support_edge_radial_pressure_balance": "infrastructure_radial_support",
    "G_infrastructure_angular_capacity": "infrastructure_angular_capacity",
    "C_live_handoff_angular_current": "live_handoff_trim",
    "E_live_handoff_radial_null_trim": "live_handoff_trim",
    "F_live_handoff_radial_pressure_trim": "live_handoff_trim",
    "D_reset_support_edge_current_sink": "reset_current_sink",
}

H_SECTOR = "distributed_current_relaxation_H"
RESIDUAL_SECTOR = "sector_closure_residual"

SECTOR_ORDER = [
    "infrastructure_radial_support",
    "infrastructure_angular_capacity",
    "live_handoff_trim",
    "reset_current_sink",
    H_SECTOR,
    RESIDUAL_SECTOR,
]

BRANCH_SIGNS = {
    "plus": -1.0,
    "minus": 1.0,
}


@dataclass(frozen=True)
class LabelGrid:
    label: str
    case: str
    s_axis: np.ndarray
    l_axis: np.ndarray
    arrays: dict[str, np.ndarray]

    @property
    def step_s(self) -> float:
        diffs = np.diff(self.s_axis)
        return float(np.nanmin(np.abs(diffs))) if len(diffs) else 1.0

    @property
    def step_l(self) -> float:
        diffs = np.diff(self.l_axis)
        return float(np.nanmin(np.abs(diffs))) if len(diffs) else 1.0

    def in_bounds(self, s: float, l: float) -> bool:
        return (
            float(self.s_axis[0]) <= s <= float(self.s_axis[-1])
            and float(self.l_axis[0]) <= l <= float(self.l_axis[-1])
        )

    def interp(self, name: str, s: float, l: float) -> float:
        if name not in self.arrays or not self.in_bounds(s, l):
            return float("nan")
        return _bilinear(self.s_axis, self.l_axis, self.arrays[name], s, l)


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def _bilinear(x_axis: np.ndarray, y_axis: np.ndarray, values: np.ndarray, x: float, y: float) -> float:
    if x < x_axis[0] or x > x_axis[-1] or y < y_axis[0] or y > y_axis[-1]:
        return float("nan")
    ix = int(np.searchsorted(x_axis, x, side="right") - 1)
    iy = int(np.searchsorted(y_axis, y, side="right") - 1)
    ix = min(max(ix, 0), len(x_axis) - 2)
    iy = min(max(iy, 0), len(y_axis) - 2)
    x0 = float(x_axis[ix])
    x1 = float(x_axis[ix + 1])
    y0 = float(y_axis[iy])
    y1 = float(y_axis[iy + 1])
    tx = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
    ty = 0.0 if y1 == y0 else (y - y0) / (y1 - y0)
    v00 = values[ix, iy]
    v10 = values[ix + 1, iy]
    v01 = values[ix, iy + 1]
    v11 = values[ix + 1, iy + 1]
    if not np.isfinite([v00, v10, v01, v11]).all():
        return float("nan")
    return float(
        (1.0 - tx) * (1.0 - ty) * v00
        + tx * (1.0 - ty) * v10
        + (1.0 - tx) * ty * v01
        + tx * ty * v11
    )


def _null_speed(grid: LabelGrid, s: float, l: float, branch: str) -> float:
    branch_factor = 1.0 if branch == "plus" else -1.0
    alpha = grid.interp("alpha", s, l)
    beta = grid.interp("beta", s, l)
    gamma_ll = grid.interp("gamma_ll", s, l)
    if not all(math.isfinite(v) for v in [alpha, beta, gamma_ll]) or gamma_ll <= 0.0:
        return float("nan")
    return float(-beta + branch_factor * alpha / math.sqrt(gamma_ll))


def _metric_components(grid: LabelGrid, s: float, l: float) -> np.ndarray:
    alpha = grid.interp("alpha", s, l)
    beta = grid.interp("beta", s, l)
    gamma_ll = grid.interp("gamma_ll", s, l)
    if not all(math.isfinite(v) for v in [alpha, beta, gamma_ll]):
        return np.full((2, 2), float("nan"), dtype=float)
    return np.array(
        [
            [-alpha * alpha + gamma_ll * beta * beta, gamma_ll * beta],
            [gamma_ll * beta, gamma_ll],
        ],
        dtype=float,
    )


def _partial_metric(grid: LabelGrid, s: float, l: float, axis: int) -> np.ndarray:
    if axis == 0:
        h = max(grid.step_s * 0.5, 1.0e-6)
        lo = s - h
        hi = s + h
        fixed = l
        lower_bound = float(grid.s_axis[0])
        upper_bound = float(grid.s_axis[-1])
    elif axis == 1:
        h = max(grid.step_l * 0.5, 1.0e-6)
        lo = l - h
        hi = l + h
        fixed = s
        lower_bound = float(grid.l_axis[0])
        upper_bound = float(grid.l_axis[-1])
    else:
        raise ValueError(f"unknown metric derivative axis {axis!r}")

    if lo >= lower_bound and hi <= upper_bound:
        if axis == 0:
            left = _metric_components(grid, lo, fixed)
            right = _metric_components(grid, hi, fixed)
        else:
            left = _metric_components(grid, fixed, lo)
            right = _metric_components(grid, fixed, hi)
        return (right - left) / (2.0 * h)
    if hi <= upper_bound:
        if axis == 0:
            base = _metric_components(grid, s, fixed)
            right = _metric_components(grid, hi, fixed)
        else:
            base = _metric_components(grid, fixed, l)
            right = _metric_components(grid, fixed, hi)
        return (right - base) / h
    if lo >= lower_bound:
        if axis == 0:
            left = _metric_components(grid, lo, fixed)
            base = _metric_components(grid, s, fixed)
        else:
            left = _metric_components(grid, fixed, lo)
            base = _metric_components(grid, fixed, l)
        return (base - left) / h
    return np.full((2, 2), float("nan"), dtype=float)


def _speed_partial(grid: LabelGrid, s: float, l: float, branch: str, axis: int) -> float:
    if axis == 0:
        h = max(grid.step_s * 0.5, 1.0e-6)
        lo = s - h
        hi = s + h
        lower_bound = float(grid.s_axis[0])
        upper_bound = float(grid.s_axis[-1])
        if lo >= lower_bound and hi <= upper_bound:
            return (_null_speed(grid, hi, l, branch) - _null_speed(grid, lo, l, branch)) / (2.0 * h)
        if hi <= upper_bound:
            return (_null_speed(grid, hi, l, branch) - _null_speed(grid, s, l, branch)) / h
        if lo >= lower_bound:
            return (_null_speed(grid, s, l, branch) - _null_speed(grid, lo, l, branch)) / h
    elif axis == 1:
        h = max(grid.step_l * 0.5, 1.0e-6)
        lo = l - h
        hi = l + h
        lower_bound = float(grid.l_axis[0])
        upper_bound = float(grid.l_axis[-1])
        if lo >= lower_bound and hi <= upper_bound:
            return (_null_speed(grid, s, hi, branch) - _null_speed(grid, s, lo, branch)) / (2.0 * h)
        if hi <= upper_bound:
            return (_null_speed(grid, s, hi, branch) - _null_speed(grid, s, l, branch)) / h
        if lo >= lower_bound:
            return (_null_speed(grid, s, l, branch) - _null_speed(grid, s, lo, branch)) / h
    else:
        raise ValueError(f"unknown speed derivative axis {axis!r}")
    return float("nan")


def _non_affinity(grid: LabelGrid, s: float, l: float, branch: str) -> tuple[float, float]:
    """Return kappa and the radial geodesic residual for K=(1, dl/ds).

    The coordinate-time null tangent K is generally non-affine:
    K^nu nabla_nu K^mu = kappa K^mu.  The residual reports the mismatch in the
    radial component after using the time component to infer kappa.
    """
    metric = _metric_components(grid, s, l)
    if not np.isfinite(metric).all():
        return float("nan"), float("nan")
    try:
        inverse = np.linalg.inv(metric)
    except np.linalg.LinAlgError:
        return float("nan"), float("nan")
    derivs = [_partial_metric(grid, s, l, 0), _partial_metric(grid, s, l, 1)]
    if not all(np.isfinite(deriv).all() for deriv in derivs):
        return float("nan"), float("nan")
    gamma = np.zeros((2, 2, 2), dtype=float)
    for mu in range(2):
        for nu in range(2):
            for rho in range(2):
                total = 0.0
                for lam in range(2):
                    total += inverse[mu, lam] * (
                        derivs[nu][rho, lam]
                        + derivs[rho][nu, lam]
                        - derivs[lam][nu, rho]
                    )
                gamma[mu, nu, rho] = 0.5 * total

    speed = _null_speed(grid, s, l, branch)
    speed_s = _speed_partial(grid, s, l, branch, 0)
    speed_l = _speed_partial(grid, s, l, branch, 1)
    if not all(math.isfinite(v) for v in [speed, speed_s, speed_l]):
        return float("nan"), float("nan")
    tangent = np.array([1.0, speed], dtype=float)
    acceleration = np.zeros(2, dtype=float)
    acceleration[1] = speed_s + speed * speed_l
    for mu in range(2):
        connection = 0.0
        for nu in range(2):
            for rho in range(2):
                connection += gamma[mu, nu, rho] * tangent[nu] * tangent[rho]
        acceleration[mu] += connection
    kappa = float(acceleration[0])
    radial_residual = float(acceleration[1] - kappa * speed)
    return kappa, radial_residual


def _load_component_detail(component_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    manifest_path = component_dir / "component_source_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    detail_value = manifest.get("files", {}).get("detail", "component_source_assignment_detail.csv")
    detail_path = resolve_manifest_path(component_dir, detail_value)
    detail = pd.read_csv(detail_path)
    return detail, {"manifest_path": manifest_path, "manifest": manifest, "detail_path": detail_path}


def _load_point_ledgers(component_dir: Path, component_manifest: dict[str, Any]) -> dict[str, pd.DataFrame]:
    ledgers: dict[str, pd.DataFrame] = {}
    for ledger in component_manifest.get("ledgers", []):
        label = str(ledger["label"])
        ledger_dir = Path(str(ledger["ledger_dir"]))
        point_path = resolve_manifest_path(component_dir, ledger.get("point_ledger", "source_ledger_point_ledger.csv"))
        if not point_path.exists() and ledger_dir.exists():
            point_path = resolve_manifest_path(ledger_dir, ledger.get("point_ledger", "source_ledger_point_ledger.csv"))
        points = pd.read_csv(point_path).reset_index(names="point_index")
        points["label"] = label
        ledgers[label] = points
    return ledgers


def _fit_coefficients(sector_fits: pd.DataFrame) -> dict[tuple[str, str], dict[str, float | str]]:
    coeffs: dict[tuple[str, str], dict[str, float | str]] = {}
    for _, row in sector_fits.iterrows():
        label = str(row["label"])
        sector = str(row["sector"])
        amp_col = str(row["amplitude_variable"])
        item: dict[str, float | str] = {"amplitude_variable": amp_col}
        for target in ["rho_euler", "p_l_unit", "j_l_unit", "p_omega_unit"]:
            key = f"{target}_per_{amp_col}"
            item[target] = _finite(row.get(key), 0.0)
        coeffs[(label, sector)] = item
    return coeffs


def _sector_assignment_points(detail: pd.DataFrame) -> pd.DataFrame:
    assigned = detail.loc[detail["assigned"].map(_bool)].copy()
    assigned["sector"] = assigned["component"].map(COMPONENT_TO_SECTOR)
    assigned = assigned.loc[assigned["sector"].notna()].copy()

    h_rows = detail.loc[(~detail["assigned"].map(_bool)) & detail["channel"].astype(str).eq("abs_j_l")].copy()
    if not h_rows.empty:
        h_rows["sector"] = H_SECTOR
        assigned = pd.concat([assigned, h_rows], ignore_index=True)

    if assigned.empty:
        return pd.DataFrame()
    grouped = (
        assigned.groupby(["label", "point_index", "sector"], dropna=False)
        .agg(
            case=("case", "first"),
            s=("s", "first"),
            l=("l", "first"),
            stage=("stage", "first"),
            region=("region", "first"),
            inside_packet_live=("inside_packet_live", "max"),
            demand_volume_burden=("demand_volume_burden", "sum"),
            rho_euler=("rho_euler", "first"),
            p_l_unit=("p_l_unit", "first"),
            j_l_unit=("j_l_unit", "first"),
            p_omega_unit=("p_omega_unit", "first"),
        )
        .reset_index()
    )
    return grouped


def _sector_values_for_points(
    points: pd.DataFrame,
    sector_points: pd.DataFrame,
    coeffs: dict[tuple[str, str], dict[str, float | str]],
    label: str,
) -> pd.DataFrame:
    out = points[["point_index", "label", "case", "s", "l"]].copy()
    sector_sum = {branch: np.zeros(len(out), dtype=float) for branch in BRANCH_SIGNS}
    indexed_positions = {int(point): idx for idx, point in enumerate(out["point_index"].astype(int))}

    for sector in SECTOR_ORDER:
        if sector == RESIDUAL_SECTOR:
            continue
        for branch in BRANCH_SIGNS:
            out[f"sector::{sector}::{branch}"] = 0.0

    label_sector_points = sector_points.loc[sector_points["label"].astype(str).eq(label)]
    for _, row in label_sector_points.iterrows():
        sector = str(row["sector"])
        fit = coeffs.get((label, sector))
        if not fit:
            continue
        pos = indexed_positions.get(int(row["point_index"]))
        if pos is None:
            continue
        amp_col = str(fit["amplitude_variable"])
        amp = _finite(row.get(amp_col), 0.0)
        rho = amp * float(fit.get("rho_euler", 0.0))
        p_l = amp * float(fit.get("p_l_unit", 0.0))
        j_l = amp * float(fit.get("j_l_unit", 0.0))
        for branch, branch_sign in BRANCH_SIGNS.items():
            value = rho + p_l + branch_sign * 2.0 * j_l
            out.iat[pos, out.columns.get_loc(f"sector::{sector}::{branch}")] += value
            sector_sum[branch][pos] += value

    for branch, branch_sign in BRANCH_SIGNS.items():
        total = (
            out.merge(
                points[["point_index", "rho_euler", "p_l_unit", "j_l_unit"]],
                on="point_index",
                how="left",
            )
        )
        total_hat = (
            total["rho_euler"].astype(float)
            + total["p_l_unit"].astype(float)
            + branch_sign * 2.0 * total["j_l_unit"].astype(float)
        ).to_numpy()
        out[f"sector::{RESIDUAL_SECTOR}::{branch}"] = total_hat - sector_sum[branch]
    return out


def _pivot_arrays(points: pd.DataFrame, value_columns: Iterable[str]) -> LabelGrid:
    s_axis = np.array(sorted(points["s"].astype(float).unique()), dtype=float)
    l_axis = np.array(sorted(points["l"].astype(float).unique()), dtype=float)
    arrays: dict[str, np.ndarray] = {}
    for column in value_columns:
        pivot = points.pivot_table(index="s", columns="l", values=column, aggfunc="first")
        pivot = pivot.reindex(index=s_axis, columns=l_axis)
        arrays[column] = pivot.to_numpy(dtype=float)
    return LabelGrid(
        label=str(points["label"].iloc[0]),
        case=str(points["case"].iloc[0]),
        s_axis=s_axis,
        l_axis=l_axis,
        arrays=arrays,
    )


def _build_label_grids(
    point_ledgers: dict[str, pd.DataFrame],
    sector_points: pd.DataFrame,
    coeffs: dict[tuple[str, str], dict[str, float | str]],
    *,
    sector_scales: dict[str, float] | None = None,
    total_mode: str = "geometric",
) -> tuple[dict[str, LabelGrid], dict[str, pd.DataFrame]]:
    scales = {sector: float((sector_scales or {}).get(sector, 1.0)) for sector in SECTOR_ORDER}
    grids: dict[str, LabelGrid] = {}
    center_tables: dict[str, pd.DataFrame] = {}
    for label, points in point_ledgers.items():
        points = points.copy()
        for column in ["rho_euler", "p_l_unit", "j_l_unit", "alpha", "beta", "gamma_ll"]:
            points[column] = points[column].astype(float)
        for branch, branch_sign in BRANCH_SIGNS.items():
            points[f"total::{branch}"] = (
                points["rho_euler"] + points["p_l_unit"] + branch_sign * 2.0 * points["j_l_unit"]
            )
        sectors = _sector_values_for_points(points, sector_points, coeffs, label)
        sector_cols = [col for col in sectors.columns if col.startswith("sector::")]
        points = points.merge(sectors[["point_index", *sector_cols]], on="point_index", how="left")
        points[sector_cols] = points[sector_cols].fillna(0.0)
        for sector in SECTOR_ORDER:
            for branch in BRANCH_SIGNS:
                col = f"sector::{sector}::{branch}"
                if col in points.columns:
                    points[col] = points[col].astype(float) * scales[sector]
        if total_mode == "sector_sum":
            for branch in BRANCH_SIGNS:
                branch_cols = [f"sector::{sector}::{branch}" for sector in SECTOR_ORDER]
                points[f"total::{branch}"] = points[branch_cols].sum(axis=1)
        elif total_mode != "geometric":
            raise ValueError(f"unknown hard affine SNEC total mode: {total_mode}")
        value_cols = ["alpha", "beta", "gamma_ll", "total::plus", "total::minus", *sector_cols]
        grids[label] = _pivot_arrays(points, value_cols)
        center_tables[label] = points
    return grids, center_tables


def _trace_branch(
    grid: LabelGrid,
    center_s: float,
    center_l: float,
    branch: str,
    *,
    lambda_extent: float,
    step_s: float,
    parameterization: str = "affine",
    return_diagnostics: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    if parameterization not in {"affine", "lapse"}:
        raise ValueError(f"unknown SNEC trace parameterization {parameterization!r}")
    alpha_center = grid.interp("alpha", center_s, center_l)
    if not math.isfinite(alpha_center) or alpha_center <= 0.0:
        alpha_center = 1.0

    def step(direction: float) -> list[tuple[float, float, float, float, float, float]]:
        samples: list[tuple[float, float, float, float, float, float]] = []
        s = float(center_s)
        l = float(center_l)
        lam = 0.0
        kappa_integral = 0.0
        while abs(lam) < lambda_extent:
            speed = _null_speed(grid, s, l, branch)
            if not math.isfinite(speed):
                break
            ds = direction * step_s
            next_s = s + ds
            if next_s < grid.s_axis[0] or next_s > grid.s_axis[-1]:
                break
            next_l = l + speed * ds
            mid_s = s + 0.5 * ds
            mid_l = l + 0.5 * speed * ds
            if not grid.in_bounds(next_s, next_l) or not grid.in_bounds(mid_s, mid_l):
                break
            mid_speed = _null_speed(grid, mid_s, mid_l, branch)
            if math.isfinite(mid_speed):
                next_l = l + mid_speed * ds
                if not grid.in_bounds(next_s, next_l):
                    break
            kappa_mid, residual_mid = _non_affinity(grid, mid_s, mid_l, branch)
            if parameterization == "affine":
                if not math.isfinite(kappa_mid):
                    break
                next_kappa_integral = kappa_integral + kappa_mid * ds
                scale_mid = alpha_center * math.exp(0.5 * (kappa_integral + next_kappa_integral))
                dlam = scale_mid * ds
                kappa_integral = next_kappa_integral
            else:
                alpha_mid = grid.interp("alpha", mid_s, mid_l)
                if not math.isfinite(alpha_mid):
                    break
                scale_mid = alpha_mid
                dlam = scale_mid * ds
                if not math.isfinite(kappa_mid):
                    kappa_mid = float("nan")
                if not math.isfinite(residual_mid):
                    residual_mid = float("nan")
            lam += dlam
            samples.append((lam, next_s, next_l, kappa_mid, residual_mid, scale_mid))
            s = next_s
            l = next_l
        return samples

    backward = step(-1.0)
    forward = step(1.0)
    center_kappa, center_residual = _non_affinity(grid, center_s, center_l, branch)
    center_sample = (0.0, float(center_s), float(center_l), center_kappa, center_residual, alpha_center)
    all_samples = list(reversed(backward)) + [center_sample] + forward
    lambdas = np.array([item[0] for item in all_samples], dtype=float)
    s_values = np.array([item[1] for item in all_samples], dtype=float)
    l_values = np.array([item[2] for item in all_samples], dtype=float)
    diagnostics = {
        "non_affinity_kappa": np.array([item[3] for item in all_samples], dtype=float),
        "radial_geodesic_residual": np.array([item[4] for item in all_samples], dtype=float),
        "dlambda_dsigma": np.array([item[5] for item in all_samples], dtype=float),
    }
    if return_diagnostics:
        return lambdas, s_values, l_values, diagnostics
    return lambdas, s_values, l_values


def _lambda_cell_weights(lambdas: np.ndarray) -> np.ndarray:
    if len(lambdas) == 1:
        return np.ones(1, dtype=float)
    weights = np.zeros(len(lambdas), dtype=float)
    weights[0] = 0.5 * abs(lambdas[1] - lambdas[0])
    weights[-1] = 0.5 * abs(lambdas[-1] - lambdas[-2])
    if len(lambdas) > 2:
        weights[1:-1] = 0.5 * np.abs(lambdas[2:] - lambdas[:-2])
    return weights


def _smeared_average(values: np.ndarray, lambdas: np.ndarray, width: float) -> tuple[float, float, float]:
    finite = np.isfinite(values) & np.isfinite(lambdas)
    if int(finite.sum()) == 0:
        return float("nan"), float("nan"), 0.0
    vals = values[finite]
    lam = lambdas[finite]
    measure = _lambda_cell_weights(lam)
    kernel = np.exp(-0.5 * (lam / float(width)) ** 2)
    weights = measure * kernel
    norm = float(np.sum(weights))
    if norm <= 0.0:
        return float("nan"), float("nan"), 0.0
    average = float(np.sum(weights * vals) / norm)
    neg_average = float(np.sum(weights * np.maximum(-vals, 0.0)) / norm)
    return average, neg_average, norm


def _coverage_record(
    lambdas: np.ndarray,
    width: float,
    norm: float,
    *,
    min_support_coverage: float,
    min_kernel_coverage: float,
) -> dict[str, Any]:
    requested = 4.0 * float(width)
    lambda_min = float(np.nanmin(lambdas))
    lambda_max = float(np.nanmax(lambdas))
    left = min(abs(lambda_min), requested)
    right = min(abs(lambda_max), requested)
    support_coverage = (left + right) / (2.0 * requested) if requested > 0.0 else 0.0
    ideal_norm = math.sqrt(2.0 * math.pi) * float(width) * math.erf(4.0 / math.sqrt(2.0))
    kernel_coverage = norm / ideal_norm if ideal_norm > 0.0 else 0.0
    return {
        "requested_lambda_extent": requested,
        "left_support_coverage": left / requested if requested > 0.0 else 0.0,
        "right_support_coverage": right / requested if requested > 0.0 else 0.0,
        "support_coverage_fraction": support_coverage,
        "kernel_weight_coverage_fraction": kernel_coverage,
        "scoreable_window": bool(
            support_coverage >= float(min_support_coverage)
            and kernel_coverage >= float(min_kernel_coverage)
        ),
    }


def _interpolate_trace(grid: LabelGrid, names: list[str], s_values: np.ndarray, l_values: np.ndarray) -> dict[str, np.ndarray]:
    out: dict[str, list[float]] = {name: [] for name in names}
    for s, l in zip(s_values, l_values):
        for name in names:
            out[name].append(grid.interp(name, float(s), float(l)))
    return {name: np.array(values, dtype=float) for name, values in out.items()}


def _dominant_negative_sector(record: dict[str, Any], branch: str) -> str:
    sector_values = {
        sector: _finite(record.get(f"smeared_sector::{sector}::{branch}"), float("nan"))
        for sector in SECTOR_ORDER
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
    parameterization: str,
    progress: bool = False,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    max_width = max(smear_widths)
    step_s = max(grid.step_s / 2.0, 1.0e-6)
    trace_names_by_branch = {
        branch: [f"total::{branch}", *[f"sector::{sector}::{branch}" for sector in SECTOR_ORDER]]
        for branch in BRANCH_SIGNS
    }
    selected_centers = centers.sort_values(["s", "l"]).iloc[:: max(int(center_stride), 1)]
    total_centers = int(len(selected_centers))
    for center_index, (_, center) in enumerate(selected_centers.iterrows(), start=1):
        center_s = float(center["s"])
        center_l = float(center["l"])
        for branch in BRANCH_SIGNS:
            lambdas, s_values, l_values, trace_diagnostics = _trace_branch(
                grid,
                center_s,
                center_l,
                branch,
                lambda_extent=4.0 * max_width,
                step_s=step_s,
                parameterization=parameterization,
                return_diagnostics=True,
            )
            if len(lambdas) < 3:
                continue
            kappa_values = trace_diagnostics["non_affinity_kappa"]
            residual_values = trace_diagnostics["radial_geodesic_residual"]
            scale_values = trace_diagnostics["dlambda_dsigma"]
            finite_kappa = kappa_values[np.isfinite(kappa_values)]
            finite_residual = residual_values[np.isfinite(residual_values)]
            finite_scale = scale_values[np.isfinite(scale_values)]
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
                    "trace_parameterization": parameterization,
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
                    "max_abs_non_affinity_kappa": float(np.max(np.abs(finite_kappa))) if len(finite_kappa) else float("nan"),
                    "mean_abs_non_affinity_kappa": float(np.mean(np.abs(finite_kappa))) if len(finite_kappa) else float("nan"),
                    "max_abs_radial_geodesic_residual": float(np.max(np.abs(finite_residual))) if len(finite_residual) else float("nan"),
                    "min_dlambda_dsigma": float(np.min(finite_scale)) if len(finite_scale) else float("nan"),
                    "max_dlambda_dsigma": float(np.max(finite_scale)) if len(finite_scale) else float("nan"),
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
                for sector in SECTOR_ORDER:
                    sector_avg, sector_neg, _norm = _smeared_average(
                        trace_values[f"sector::{sector}::{branch}"],
                        lambdas,
                        width,
                    )
                    record[f"smeared_sector::{sector}::{branch}"] = sector_avg
                    record[f"smeared_sector_neg::{sector}::{branch}"] = sector_neg
                record["dominant_negative_sector"] = _dominant_negative_sector(record, branch)
                rows.append(record)
        if progress and (center_index == total_centers or center_index % max(1, total_centers // 5) == 0):
            print(f"{grid.label}: SNEC center {center_index}/{total_centers}", flush=True)
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
            "worst_support_coverage_fraction": float(worst.get("support_coverage_fraction", float("nan"))),
            "worst_kernel_weight_coverage_fraction": float(worst.get("kernel_weight_coverage_fraction", float("nan"))),
            "worst_center_s": float(worst["center_s"]),
            "worst_center_l": float(worst["center_l"]),
            "worst_center_stage": worst["center_stage"],
            "worst_center_region": worst["center_region"],
            "worst_center_inside_packet_live": bool(worst["center_inside_packet_live"]),
            "dominant_negative_sector": worst["dominant_negative_sector"],
        })
    return pd.DataFrame(rows).sort_values(["label", "smear_width_affine", "branch"])


def _sector_summary_table(windows: pd.DataFrame) -> pd.DataFrame:
    if windows.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for (label, branch, width), group in windows.groupby(["label", "branch", "smear_width_affine"], sort=False):
        scoreable = group.loc[group["scoreable_window"].astype(bool)] if "scoreable_window" in group else group
        sector_group = scoreable if not scoreable.empty else group
        for sector in SECTOR_ORDER:
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


def build_hard_affine_snec_screen(
    component_dir: Path,
    *,
    smear_widths: Iterable[float] = (0.25, 0.50, 1.00),
    benchmark_b: float = 1.0 / (32.0 * math.pi),
    center_stride: int = 1,
    top_limit: int = 120,
    min_support_coverage: float = 0.80,
    min_kernel_coverage: float = 0.80,
    sector_scales: dict[str, float] | None = None,
    total_mode: str = "geometric",
    parameterization: str = "affine",
    progress: bool = False,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    if parameterization not in {"affine", "lapse"}:
        raise ValueError(f"unknown hard affine SNEC parameterization: {parameterization!r}")
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
                parameterization=str(parameterization),
                progress=bool(progress),
            )
            for label, grid in grids.items()
        ],
        ignore_index=True,
    )
    summary = _summary_table(windows)
    sector_summary = _sector_summary_table(windows)
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
    metadata.update({
        "ansatz_metadata": ansatz_metadata,
        "smear_widths": widths,
        "benchmark_b": float(benchmark_b),
        "center_stride": int(center_stride),
        "top_limit": int(top_limit),
        "min_support_coverage": float(min_support_coverage),
        "min_kernel_coverage": float(min_kernel_coverage),
        "sector_scales": {sector: float((sector_scales or {}).get(sector, 1.0)) for sector in SECTOR_ORDER},
        "total_mode": str(total_mode),
        "parameterization": str(parameterization),
        "progress": bool(progress),
    })
    return outputs, metadata


def write_hard_affine_snec_outputs(
    outdir: Path,
    component_dir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "windows": outdir / "hard_affine_snec_windows.csv",
        "summary": outdir / "hard_affine_snec_summary.csv",
        "sector_summary": outdir / "hard_affine_snec_sector_summary.csv",
        "top_windows": outdir / "hard_affine_snec_top_windows.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "hard_affine_snec_manifest.json"
    manifest = {
        "caveat": (
            "Harder radial-null SNEC screen on sampled branches. With parameterization='affine' "
            "the trace integrates the radial-null non-affinity and uses a center-normalized affine "
            "parameter while reporting the remaining radial geodesic residual; with "
            "parameterization='lapse' it is a lapse-parametrized comparison screen. This uses the "
            "demanded stress ledger and the H-promoted sector ansatz; it is still not a quantum "
            "RSET calculation, conservation proof, or physical matter-model solve."
        ),
        "component_source_dir": str(component_dir),
        "component_source_manifest": str(metadata["manifest_path"]),
        "component_detail": str(metadata["detail_path"]),
        "component_detail_sha256": sha256_file(metadata["detail_path"]),
        "ansatz": "composite_anisotropic_support_with_H",
        "smear_widths_affine": list(metadata["smear_widths"]),
        "benchmark_B": float(metadata["benchmark_b"]),
        "center_stride": int(metadata["center_stride"]),
        "min_support_coverage": float(metadata["min_support_coverage"]),
        "min_kernel_coverage": float(metadata["min_kernel_coverage"]),
        "sector_scales": metadata["sector_scales"],
        "total_mode": metadata["total_mode"],
        "parameterization": metadata["parameterization"],
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
