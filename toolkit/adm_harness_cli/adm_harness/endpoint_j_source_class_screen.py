from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


EPS = 1.0e-30
FIELD_COLUMNS = ("sector_rho", "sector_p_l", "sector_j_l", "sector_p_omega")


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom > 0.0 else float("nan")


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"1", "true", "yes"})


def _boost_velocity(rho_plus_p: np.ndarray, j_l: np.ndarray, discriminant: np.ndarray) -> np.ndarray:
    out = np.zeros(len(rho_plus_p), dtype=float)
    for idx, (rp, current, disc) in enumerate(zip(rho_plus_p, j_l, discriminant)):
        if abs(current) <= EPS:
            out[idx] = 0.0
            continue
        if disc < 0.0 or not math.isfinite(float(disc)):
            out[idx] = float("nan")
            continue
        root = math.sqrt(max(float(disc), 0.0))
        denom = 2.0 * float(current)
        candidates = [((float(rp) - root) / denom), ((float(rp) + root) / denom)]
        finite = [value for value in candidates if math.isfinite(value)]
        subluminal = [value for value in finite if abs(value) < 1.0 + 1.0e-10]
        pool = subluminal or finite
        out[idx] = min(pool, key=lambda value: abs(value)) if pool else float("nan")
    return out


def classify_endpoint_source_frame(frame: pd.DataFrame, *, type_tolerance: float = 1.0e-12) -> pd.DataFrame:
    out = frame.copy()
    rho = out["sector_rho"].astype(float).to_numpy()
    p_l = out["sector_p_l"].astype(float).to_numpy()
    j_l = out["sector_j_l"].astype(float).to_numpy()
    p_omega = out["sector_p_omega"].astype(float).to_numpy()
    rho_plus_p = rho + p_l
    discriminant = np.square(rho_plus_p) - 4.0 * np.square(j_l)
    sqrt_disc = np.sqrt(np.clip(discriminant, 0.0, np.inf))
    boost_v = _boost_velocity(rho_plus_p, j_l, discriminant)
    rest_energy = 0.5 * (rho - p_l + sqrt_disc)
    rest_radial_pressure = 0.5 * (p_l - rho + sqrt_disc)
    flux_ratio = 2.0 * np.abs(j_l) / np.maximum(np.abs(rho_plus_p), EPS)
    regulator = np.maximum(0.0, 2.0 * np.abs(j_l) - np.abs(rho_plus_p))

    stress_type = np.where(
        discriminant < -abs(float(type_tolerance)),
        "type_iv_flux_dominant",
        np.where(np.abs(discriminant) <= abs(float(type_tolerance)), "type_ii_null_boundary", "type_i_boost_diagonalizable"),
    )

    canonical_scalar = (
        (discriminant >= -abs(float(type_tolerance)))
        & (rho_plus_p >= -abs(float(type_tolerance)))
        & ((p_l - p_omega) >= -abs(float(type_tolerance)))
    )
    phantom_scalar = (
        (rho_plus_p <= abs(float(type_tolerance)))
        & ((p_l - p_omega) <= abs(float(type_tolerance)))
        & (np.abs(rho_plus_p) + abs(float(type_tolerance)) >= 2.0 * np.abs(j_l))
    )
    type_i_heat_flux = (
        (discriminant >= -abs(float(type_tolerance)))
        & (np.isfinite(boost_v))
        & (np.abs(boost_v) < 1.0 + 1.0e-10)
    )

    out["rho_plus_p_l"] = rho_plus_p
    out["radial_block_discriminant"] = discriminant
    out["radial_flux_ratio"] = flux_ratio
    out["stress_algebraic_type"] = stress_type
    out["boost_velocity_to_flux_frame"] = boost_v
    out["rest_frame_energy_density"] = np.where(discriminant >= -abs(float(type_tolerance)), rest_energy, np.nan)
    out["rest_frame_radial_pressure"] = np.where(discriminant >= -abs(float(type_tolerance)), rest_radial_pressure, np.nan)
    out["rest_frame_angular_pressure"] = np.where(discriminant >= -abs(float(type_tolerance)), p_omega, np.nan)
    out["canonical_scalar_compatible"] = canonical_scalar
    out["phantom_scalar_compatible"] = phantom_scalar
    out["type_i_heat_flux_compatible"] = type_i_heat_flux
    out["minimal_type_i_regulator"] = regulator
    out["source_abs_density"] = np.abs(rho) + np.abs(p_l) + np.abs(j_l) + np.abs(p_omega)
    out["pair_abs_density"] = np.abs(rho) + np.abs(p_l)
    out["source_abs_volume"] = out["source_abs_density"] * out["volume_weight"].astype(float)
    out["pair_abs_volume"] = out["pair_abs_density"] * out["volume_weight"].astype(float)
    out["regulator_abs_volume"] = out["minimal_type_i_regulator"] * out["volume_weight"].astype(float)
    return out


def _weighted_fraction(frame: pd.DataFrame, mask: pd.Series | np.ndarray, weight_column: str) -> float:
    if frame.empty or weight_column not in frame:
        return float("nan")
    weights = frame[weight_column].astype(float)
    total = float(weights.sum())
    if total <= 0.0:
        return float("nan")
    return float(weights.loc[pd.Series(mask, index=frame.index).astype(bool)].sum() / total)


def _quantile(series: pd.Series, q: float) -> float:
    values = series.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.quantile(q)) if len(values) else float("nan")


def _summary_row(scope: str, frame: pd.DataFrame) -> dict[str, Any]:
    live = _bool_series(frame["inside_packet_live"]) if "inside_packet_live" in frame else pd.Series(False, index=frame.index)
    type_iv = frame["stress_algebraic_type"].astype(str) == "type_iv_flux_dominant"
    type_ii = frame["stress_algebraic_type"].astype(str) == "type_ii_null_boundary"
    type_i = frame["stress_algebraic_type"].astype(str) == "type_i_boost_diagonalizable"
    source_total = float(frame["source_abs_volume"].sum())
    pair_total = float(frame["pair_abs_volume"].sum())
    regulator_total = float(frame["regulator_abs_volume"].sum())
    return {
        "scope": scope,
        "rows": int(len(frame)),
        "live_rows": int(live.sum()),
        "active_volume": float(frame["volume_weight"].astype(float).sum()),
        "source_abs_volume": source_total,
        "pair_abs_volume": pair_total,
        "type_i_volume_fraction": _weighted_fraction(frame, type_i, "volume_weight"),
        "type_ii_volume_fraction": _weighted_fraction(frame, type_ii, "volume_weight"),
        "type_iv_volume_fraction": _weighted_fraction(frame, type_iv, "volume_weight"),
        "type_iv_source_burden_fraction": _weighted_fraction(frame, type_iv, "source_abs_volume"),
        "canonical_scalar_volume_fraction": _weighted_fraction(frame, frame["canonical_scalar_compatible"], "volume_weight"),
        "phantom_scalar_volume_fraction": _weighted_fraction(frame, frame["phantom_scalar_compatible"], "volume_weight"),
        "type_i_heat_flux_volume_fraction": _weighted_fraction(frame, frame["type_i_heat_flux_compatible"], "volume_weight"),
        "minimal_type_i_regulator_abs_volume": regulator_total,
        "regulator_to_pair_abs_ratio": _safe_ratio(regulator_total, pair_total),
        "regulator_to_source_abs_ratio": _safe_ratio(regulator_total, source_total),
        "peak_minimal_type_i_regulator": float(frame["minimal_type_i_regulator"].astype(float).max()) if len(frame) else float("nan"),
        "p99_minimal_type_i_regulator": _quantile(frame["minimal_type_i_regulator"], 0.99),
        "min_radial_block_discriminant": float(frame["radial_block_discriminant"].astype(float).min()) if len(frame) else float("nan"),
        "p01_radial_block_discriminant": _quantile(frame["radial_block_discriminant"], 0.01),
        "p99_radial_flux_ratio": _quantile(frame["radial_flux_ratio"], 0.99),
        "max_abs_boost_velocity": float(frame["boost_velocity_to_flux_frame"].astype(float).abs().replace([np.inf], np.nan).max())
        if len(frame) else float("nan"),
        "rest_energy_negative_volume_fraction": _weighted_fraction(
            frame,
            frame["rest_frame_energy_density"].astype(float) < 0.0,
            "volume_weight",
        ),
        "angular_nec_violation_volume_fraction": _weighted_fraction(
            frame,
            (frame["rest_frame_energy_density"].astype(float) + frame["rest_frame_angular_pressure"].astype(float)) < 0.0,
            "volume_weight",
        ),
    }


def build_source_class_screen_tables(
    fit_sector_stress: pd.DataFrame,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_source_ratio_gate: float = 0.06,
    type_iv_burden_gate: float = 0.02,
) -> dict[str, pd.DataFrame]:
    classified = classify_endpoint_source_frame(fit_sector_stress)
    summary_rows = [_summary_row("J_total", classified)]
    for assignment, group in classified.groupby("assignment", sort=False):
        summary_rows.append(_summary_row(str(assignment), group))
    assignment_summary = pd.DataFrame(summary_rows)
    total = assignment_summary.loc[assignment_summary["scope"] == "J_total"].iloc[0].to_dict()

    canonical_fraction = _finite(total.get("canonical_scalar_volume_fraction"), float("nan"))
    phantom_fraction = _finite(total.get("phantom_scalar_volume_fraction"), float("nan"))
    type_i_fraction = _finite(total.get("type_i_heat_flux_volume_fraction"), float("nan"))
    type_iv_burden = _finite(total.get("type_iv_source_burden_fraction"), float("nan"))
    regulator_ratio = _finite(total.get("regulator_to_source_abs_ratio"), float("nan"))
    live_rows = int(total.get("live_rows", 0))
    regulator_pass = bool(live_rows == 0 and regulator_ratio <= regulator_source_ratio_gate)
    ordinary_type_i_pass = bool(live_rows == 0 and type_iv_burden <= type_iv_burden_gate and type_i_fraction >= 0.98)

    model_rows = [
        {
            "source_name": source_name,
            "model_class": "single_canonical_scalar",
            "compatible_volume_fraction": canonical_fraction,
            "passes_screen": bool(canonical_fraction >= 0.95),
            "read": "fails_if_fraction_below_0p95; scalar algebra cannot cover mixed radial flux and pOmega demand",
        },
        {
            "source_name": source_name,
            "model_class": "single_phantom_scalar",
            "compatible_volume_fraction": phantom_fraction,
            "passes_screen": bool(phantom_fraction >= 0.95),
            "read": "fails_if_fraction_below_0p95; phantom scalar alone cannot cover mixed-sign endpoint stress",
        },
        {
            "source_name": source_name,
            "model_class": "ordinary_type_i_anisotropic_heat_flux",
            "compatible_volume_fraction": type_i_fraction,
            "type_iv_source_burden_fraction": type_iv_burden,
            "passes_screen": ordinary_type_i_pass,
            "read": "requires almost all burden to be boost-diagonalizable without regulator",
        },
        {
            "source_name": source_name,
            "model_class": "regulated_anisotropic_heat_flux_medium",
            "compatible_volume_fraction": 1.0 if regulator_pass else type_i_fraction,
            "type_iv_source_burden_fraction": type_iv_burden,
            "regulator_to_source_abs_ratio": regulator_ratio,
            "passes_screen": regulator_pass,
            "read": "anisotropic heat/current medium plus finite rho+p current regulator",
        },
        {
            "source_name": source_name,
            "model_class": "multi_field_effective_potential_fallback",
            "compatible_volume_fraction": 1.0,
            "passes_screen": True,
            "read": "fallback class if regulated anisotropic medium fails; not needed if regulator gate passes",
        },
    ]
    recommended = (
        "regulated_anisotropic_heat_flux_medium"
        if regulator_pass
        else "multi_field_effective_potential_fallback"
    )
    decision = pd.DataFrame([{
        "source_name": source_name,
        "recommended_model_class": recommended,
        "ordinary_type_i_passes": ordinary_type_i_pass,
        "regulated_anisotropic_passes": regulator_pass,
        "single_scalar_ruled_out": bool(canonical_fraction < 0.95 and phantom_fraction < 0.95),
        "live_rows": live_rows,
        "type_iv_source_burden_fraction": type_iv_burden,
        "regulator_to_source_abs_ratio": regulator_ratio,
        "regulator_gate": float(regulator_source_ratio_gate),
        "type_iv_burden_gate": float(type_iv_burden_gate),
        "decision_read": (
            "ordinary anisotropic fluid alone is too narrow; finite regulated anisotropic heat/current medium is viable"
            if regulator_pass
            else "requires broader multi-field/effective-potential construction"
        ),
    }])
    return {
        "point_classification": classified,
        "assignment_summary": assignment_summary,
        "model_class_summary": pd.DataFrame(model_rows),
        "feasibility_decision": decision,
    }


def _load_fit_sector_stress(fit_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = fit_dir / "endpoint_j_closure_component_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        value = manifest.get("files", {}).get("fit_sector_stress", "endpoint_j_closure_sector_stress.csv")
        path = resolve_manifest_path(fit_dir, value)
        return pd.read_csv(path), manifest, path
    path = fit_dir / "endpoint_j_closure_sector_stress.csv"
    return pd.read_csv(path), {}, path


def build_endpoint_j_source_class_screen(
    fit_dir: Path,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_source_ratio_gate: float = 0.06,
    type_iv_burden_gate: float = 0.02,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    fit, manifest, fit_path = _load_fit_sector_stress(fit_dir)
    outputs = build_source_class_screen_tables(
        fit,
        source_name=source_name,
        regulator_source_ratio_gate=regulator_source_ratio_gate,
        type_iv_burden_gate=type_iv_burden_gate,
    )
    metadata = {
        "fit_dir": str(fit_dir),
        "fit_sector_stress": str(fit_path),
        "fit_sector_stress_sha256": sha256_file(fit_path),
        "source_name": source_name,
        "input_caveat": manifest.get("caveat", ""),
        "regulator_source_ratio_gate": float(regulator_source_ratio_gate),
        "type_iv_burden_gate": float(type_iv_burden_gate),
        "caveat": (
            "Algebraic physical-source class screen for the frozen endpoint-J effective source. "
            "This classifies local stress blocks and estimates a minimal Type-I regulator; "
            "it is not a field-equation solve or matter-action proof."
        ),
    }
    return outputs, metadata


def write_endpoint_j_source_class_screen_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_classification": outdir / "endpoint_j_source_class_point_classification.csv",
        "assignment_summary": outdir / "endpoint_j_source_class_assignment_summary.csv",
        "model_class_summary": outdir / "endpoint_j_source_class_model_summary.csv",
        "feasibility_decision": outdir / "endpoint_j_source_class_feasibility_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_j_source_class_screen_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
