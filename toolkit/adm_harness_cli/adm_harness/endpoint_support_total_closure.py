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


def _load_stroke_dir(stroke_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Path]]:
    manifest_path = stroke_dir / "endpoint_support_stroke_exchange_manifest.json"
    manifest: dict[str, Any] = json.loads(manifest_path.read_text())
    files = manifest.get("files", {})
    point_fit_path = resolve_manifest_path(stroke_dir, files.get("point_fit", "endpoint_support_stroke_exchange_point_fit.csv"))
    decision_path = resolve_manifest_path(stroke_dir, files.get("decision", "endpoint_support_stroke_exchange_decision.csv"))
    return pd.read_csv(point_fit_path), pd.read_csv(decision_path), manifest, {
        "manifest": manifest_path,
        "point_fit": point_fit_path,
        "decision": decision_path,
    }


def _mask(frame: pd.DataFrame, name: str) -> pd.Series:
    live = _bool_series(frame["covariant_divergence_live"]) if "covariant_divergence_live" in frame else pd.Series(False, index=frame.index)
    active = _bool_series(frame["medium_source_active"]) if "medium_source_active" in frame else pd.Series(True, index=frame.index)
    allowed = _bool_series(frame["covariant_exchange_allowed_mask"]) if "covariant_exchange_allowed_mask" in frame else pd.Series(True, index=frame.index)
    if name == "full_grid":
        return pd.Series(True, index=frame.index)
    if name == "active":
        return active & (~live)
    if name == "allowed":
        return allowed & (~live)
    if name == "outside_allowed":
        return (~allowed) & (~live)
    if name == "live":
        return live
    raise ValueError(f"unknown closure mask {name!r}")


def _top_share(values: np.ndarray, row_fraction: float) -> float:
    total = float(np.sum(values))
    if len(values) == 0 or total <= 0.0:
        return float("nan")
    count = max(1, int(math.ceil(float(row_fraction) * len(values))))
    return float(np.sort(values)[::-1][:count].sum() / total)


def _add_total_closure_columns(point_fit: pd.DataFrame) -> pd.DataFrame:
    out = point_fit.copy()
    endpoint = np.column_stack([out[f"covariant_divergence_{nu}"].astype(float).to_numpy() for nu in range(4)])
    support = -np.column_stack([out[f"fit_J_{nu}"].astype(float).to_numpy() for nu in range(4)])
    residual = endpoint + support
    for nu in range(4):
        out[f"candidate_support_current_{nu}"] = support[:, nu]
        out[f"total_closure_residual_{nu}"] = residual[:, nu]
    out["endpoint_exchange_l2_density"] = np.sqrt(np.sum(np.square(endpoint), axis=1))
    out["candidate_support_l2_density"] = np.sqrt(np.sum(np.square(support), axis=1))
    out["total_closure_residual_l2_density"] = np.sqrt(np.sum(np.square(residual), axis=1))
    out["candidate_support_abs_PF_density"] = out["fit_abs_PF_density"].astype(float)
    out["total_closure_residual_abs_PF_density"] = out["fit_error_abs_PF_density"].astype(float)
    out["candidate_support_angular_abs_density"] = (
        out["candidate_support_current_2"].abs() + out["candidate_support_current_3"].abs()
    )
    out["total_closure_residual_angular_abs_density"] = (
        out["total_closure_residual_2"].abs() + out["total_closure_residual_3"].abs()
    )
    volume = out["volume_weight"].astype(float)
    for column in [
        "endpoint_exchange_l2_density",
        "candidate_support_l2_density",
        "total_closure_residual_l2_density",
        "candidate_support_abs_PF_density",
        "total_closure_residual_abs_PF_density",
        "candidate_support_angular_abs_density",
        "total_closure_residual_angular_abs_density",
        "target_abs_PF_density",
    ]:
        out[f"{column}_volume"] = out[column].astype(float) * volume
    return out


def _scope_summary(scope: str, frame: pd.DataFrame, mask: pd.Series) -> dict[str, Any]:
    selected = frame.loc[mask].copy()
    endpoint_l2 = float(selected["endpoint_exchange_l2_density_volume"].astype(float).sum()) if len(selected) else 0.0
    support_l2 = float(selected["candidate_support_l2_density_volume"].astype(float).sum()) if len(selected) else 0.0
    residual_l2 = float(selected["total_closure_residual_l2_density_volume"].astype(float).sum()) if len(selected) else 0.0
    target_pf = float(selected["target_abs_PF_density_volume"].astype(float).sum()) if len(selected) else 0.0
    support_pf = float(selected["candidate_support_abs_PF_density_volume"].astype(float).sum()) if len(selected) else 0.0
    residual_pf = float(selected["total_closure_residual_abs_PF_density_volume"].astype(float).sum()) if len(selected) else 0.0
    residual_angular = float(selected["total_closure_residual_angular_abs_density_volume"].astype(float).sum()) if len(selected) else 0.0
    support_angular = float(selected["candidate_support_angular_abs_density_volume"].astype(float).sum()) if len(selected) else 0.0
    return {
        "scope": scope,
        "rows": int(len(selected)),
        "endpoint_exchange_l2_volume": endpoint_l2,
        "candidate_support_l2_volume": support_l2,
        "total_closure_residual_l2_volume": residual_l2,
        "closure_residual_to_endpoint_l2_ratio": _safe_ratio(residual_l2, endpoint_l2),
        "target_abs_PF_volume": target_pf,
        "candidate_support_abs_PF_volume": support_pf,
        "total_closure_residual_abs_PF_volume": residual_pf,
        "closure_residual_to_target_abs_PF_ratio": _safe_ratio(residual_pf, target_pf),
        "support_to_endpoint_l2_ratio": _safe_ratio(support_l2, endpoint_l2),
        "support_to_target_abs_PF_ratio": _safe_ratio(support_pf, target_pf),
        "candidate_support_angular_volume": support_angular,
        "total_closure_residual_angular_volume": residual_angular,
        "peak_residual_l2_density": float(selected["total_closure_residual_l2_density"].astype(float).max()) if len(selected) else float("nan"),
        "top_1pct_residual_burden_share": _top_share(
            selected["total_closure_residual_l2_density_volume"].astype(float).to_numpy(),
            0.01,
        )
        if len(selected)
        else float("nan"),
    }


def _build_scope_summary(point_closure: pd.DataFrame) -> pd.DataFrame:
    rows = [_scope_summary(scope, point_closure, _mask(point_closure, scope)) for scope in (
        "full_grid",
        "active",
        "allowed",
        "outside_allowed",
        "live",
    )]
    for key, group in point_closure.loc[_mask(point_closure, "active")].groupby(["assignment", "stage", "region"], sort=False, dropna=False):
        assignment, stage, region = key
        label = f"active::{assignment}|{stage}|{region}"
        rows.append(_scope_summary(label, point_closure, point_closure.index.to_series().isin(group.index)))
    return pd.DataFrame(rows)


def _row(summary: pd.DataFrame, scope: str) -> pd.Series:
    selected = summary.loc[summary["scope"].astype(str) == scope]
    if selected.empty:
        raise ValueError(f"missing closure summary scope {scope!r}")
    return selected.iloc[0]


def _decision(
    scope_summary: pd.DataFrame,
    stroke_decision: pd.DataFrame,
    *,
    active_closure_l2_gate: float,
    allowed_closure_l2_gate: float,
    local_closure_l2_gate: float,
    active_closure_pf_gate: float,
    allowed_closure_pf_gate: float,
    local_closure_pf_gate: float,
    outside_residual_fraction_gate: float,
    live_residual_fraction_gate: float,
    support_tail_fraction_gate: float,
    live_support_fraction_gate: float,
    angular_support_gate: float,
) -> pd.DataFrame:
    active = _row(scope_summary, "active")
    allowed = _row(scope_summary, "allowed")
    outside = _row(scope_summary, "outside_allowed")
    live = _row(scope_summary, "live")
    full = _row(scope_summary, "full_grid")
    local = scope_summary.loc[scope_summary["scope"].astype(str).str.startswith("active::")]
    local_max_l2 = float(local["closure_residual_to_endpoint_l2_ratio"].astype(float).max()) if len(local) else float("nan")
    local_max_pf = float(local["closure_residual_to_target_abs_PF_ratio"].astype(float).max()) if len(local) else float("nan")
    full_endpoint = _finite(full["endpoint_exchange_l2_volume"], 0.0)
    full_support = _finite(full["candidate_support_l2_volume"], 0.0)
    outside_residual_fraction = _safe_ratio(_finite(outside["total_closure_residual_l2_volume"], 0.0), full_endpoint)
    live_residual_fraction = _safe_ratio(_finite(live["total_closure_residual_l2_volume"], 0.0), full_endpoint)
    outside_support_fraction = _safe_ratio(_finite(outside["candidate_support_l2_volume"], 0.0), full_support)
    live_support_fraction = _safe_ratio(_finite(live["candidate_support_l2_volume"], 0.0), full_support)
    active_pass = bool(
        _finite(active["closure_residual_to_endpoint_l2_ratio"], float("inf")) <= float(active_closure_l2_gate)
        and _finite(active["closure_residual_to_target_abs_PF_ratio"], float("inf")) <= float(active_closure_pf_gate)
    )
    allowed_pass = bool(
        _finite(allowed["closure_residual_to_endpoint_l2_ratio"], float("inf")) <= float(allowed_closure_l2_gate)
        and _finite(allowed["closure_residual_to_target_abs_PF_ratio"], float("inf")) <= float(allowed_closure_pf_gate)
    )
    local_pass = bool(
        _finite(local_max_l2, float("inf")) <= float(local_closure_l2_gate)
        and _finite(local_max_pf, float("inf")) <= float(local_closure_pf_gate)
    )
    localization_pass = bool(
        outside_residual_fraction <= float(outside_residual_fraction_gate)
        and live_residual_fraction <= float(live_residual_fraction_gate)
        and outside_support_fraction <= float(support_tail_fraction_gate)
        and live_support_fraction <= float(live_support_fraction_gate)
    )
    angular_pass = bool(
        _finite(full["candidate_support_angular_volume"], float("inf")) <= float(angular_support_gate)
        and _finite(full["total_closure_residual_angular_volume"], 0.0) <= float(angular_support_gate)
    )
    stroke_pass = bool(stroke_decision["passes_support_stroke_exchange_fit"].astype(bool).iloc[0]) if len(stroke_decision) else False
    hard_pass = bool(stroke_pass and active_pass and allowed_pass and local_pass and localization_pass and angular_pass)
    return pd.DataFrame([{
        "support_total_closure_status": "support_total_exchange_closure_pass" if hard_pass else "support_total_exchange_closure_watch",
        "passes_support_total_closure": hard_pass,
        "stroke_exchange_fit_pass": stroke_pass,
        "active_closure_pass": active_pass,
        "allowed_closure_pass": allowed_pass,
        "local_active_closure_pass": local_pass,
        "localization_pass": localization_pass,
        "angular_support_pass": angular_pass,
        "active_closure_residual_to_endpoint_l2_ratio": _finite(active["closure_residual_to_endpoint_l2_ratio"], float("nan")),
        "allowed_closure_residual_to_endpoint_l2_ratio": _finite(allowed["closure_residual_to_endpoint_l2_ratio"], float("nan")),
        "local_max_closure_residual_to_endpoint_l2_ratio": local_max_l2,
        "active_closure_residual_to_target_abs_PF_ratio": _finite(active["closure_residual_to_target_abs_PF_ratio"], float("nan")),
        "allowed_closure_residual_to_target_abs_PF_ratio": _finite(allowed["closure_residual_to_target_abs_PF_ratio"], float("nan")),
        "local_max_closure_residual_to_target_abs_PF_ratio": local_max_pf,
        "outside_residual_fraction_of_full_endpoint": outside_residual_fraction,
        "live_residual_fraction_of_full_endpoint": live_residual_fraction,
        "outside_support_tail_fraction": outside_support_fraction,
        "live_support_tail_fraction": live_support_fraction,
        "full_candidate_support_angular_volume": _finite(full["candidate_support_angular_volume"], float("nan")),
        "full_total_closure_residual_angular_volume": _finite(full["total_closure_residual_angular_volume"], float("nan")),
        "active_closure_l2_gate": float(active_closure_l2_gate),
        "allowed_closure_l2_gate": float(allowed_closure_l2_gate),
        "local_closure_l2_gate": float(local_closure_l2_gate),
        "active_closure_pf_gate": float(active_closure_pf_gate),
        "allowed_closure_pf_gate": float(allowed_closure_pf_gate),
        "local_closure_pf_gate": float(local_closure_pf_gate),
        "outside_residual_fraction_gate": float(outside_residual_fraction_gate),
        "live_residual_fraction_gate": float(live_residual_fraction_gate),
        "support_tail_fraction_gate": float(support_tail_fraction_gate),
        "live_support_fraction_gate": float(live_support_fraction_gate),
        "angular_support_gate": float(angular_support_gate),
        "decision_read": (
            "candidate support exchange current cancels the endpoint divergence within closure gates while preserving localization and angular/live exclusions"
            if hard_pass
            else "candidate support exchange current leaves one or more total-closure, localization, angular, or inherited stroke gates on watch"
        ),
    }])


def build_support_total_closure_tables(
    stroke_point_fit: pd.DataFrame,
    stroke_decision: pd.DataFrame,
    *,
    active_closure_l2_gate: float = 0.55,
    allowed_closure_l2_gate: float = 0.55,
    local_closure_l2_gate: float = 0.55,
    active_closure_pf_gate: float = 0.50,
    allowed_closure_pf_gate: float = 0.50,
    local_closure_pf_gate: float = 0.55,
    outside_residual_fraction_gate: float = 0.006,
    live_residual_fraction_gate: float = 0.005,
    support_tail_fraction_gate: float = 0.001,
    live_support_fraction_gate: float = 0.0001,
    angular_support_gate: float = 1.0e-14,
) -> dict[str, pd.DataFrame]:
    point_closure = _add_total_closure_columns(stroke_point_fit)
    scope_summary = _build_scope_summary(point_closure)
    decision = _decision(
        scope_summary,
        stroke_decision,
        active_closure_l2_gate=active_closure_l2_gate,
        allowed_closure_l2_gate=allowed_closure_l2_gate,
        local_closure_l2_gate=local_closure_l2_gate,
        active_closure_pf_gate=active_closure_pf_gate,
        allowed_closure_pf_gate=allowed_closure_pf_gate,
        local_closure_pf_gate=local_closure_pf_gate,
        outside_residual_fraction_gate=outside_residual_fraction_gate,
        live_residual_fraction_gate=live_residual_fraction_gate,
        support_tail_fraction_gate=support_tail_fraction_gate,
        live_support_fraction_gate=live_support_fraction_gate,
        angular_support_gate=angular_support_gate,
    )
    top_residual = point_closure.sort_values("total_closure_residual_l2_density_volume", ascending=False).head(80)
    keep = [
        "case",
        "s",
        "l",
        "assignment",
        "stage",
        "region",
        "medium_source_active",
        "covariant_exchange_allowed_mask",
        "covariant_divergence_live",
        "endpoint_exchange_l2_density",
        "candidate_support_l2_density",
        "total_closure_residual_l2_density",
        "total_closure_residual_l2_density_volume",
        "target_abs_PF_density",
        "candidate_support_abs_PF_density",
        "total_closure_residual_abs_PF_density",
    ]
    return {
        "point_closure": point_closure,
        "scope_summary": scope_summary,
        "top_residual": top_residual[[col for col in keep if col in top_residual.columns]].reset_index(drop=True),
        "decision": decision,
    }


def build_support_total_closure(
    stroke_dir: Path,
    *,
    source_name: str = "endpoint_support_total_closure",
    active_closure_l2_gate: float = 0.55,
    allowed_closure_l2_gate: float = 0.55,
    local_closure_l2_gate: float = 0.55,
    active_closure_pf_gate: float = 0.50,
    allowed_closure_pf_gate: float = 0.50,
    local_closure_pf_gate: float = 0.55,
    outside_residual_fraction_gate: float = 0.006,
    live_residual_fraction_gate: float = 0.005,
    support_tail_fraction_gate: float = 0.001,
    live_support_fraction_gate: float = 0.0001,
    angular_support_gate: float = 1.0e-14,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    point_fit, stroke_decision, stroke_manifest, paths = _load_stroke_dir(stroke_dir)
    outputs = build_support_total_closure_tables(
        point_fit,
        stroke_decision,
        active_closure_l2_gate=active_closure_l2_gate,
        allowed_closure_l2_gate=allowed_closure_l2_gate,
        local_closure_l2_gate=local_closure_l2_gate,
        active_closure_pf_gate=active_closure_pf_gate,
        allowed_closure_pf_gate=allowed_closure_pf_gate,
        local_closure_pf_gate=local_closure_pf_gate,
        outside_residual_fraction_gate=outside_residual_fraction_gate,
        live_residual_fraction_gate=live_residual_fraction_gate,
        support_tail_fraction_gate=support_tail_fraction_gate,
        live_support_fraction_gate=live_support_fraction_gate,
        angular_support_gate=angular_support_gate,
    )
    metadata = {
        "stroke_dir": str(stroke_dir),
        "stroke_manifest": str(paths["manifest"]),
        "stroke_point_fit": str(paths["point_fit"]),
        "stroke_point_fit_sha256": sha256_file(paths["point_fit"]),
        "stroke_decision": str(paths["decision"]),
        "stroke_decision_sha256": sha256_file(paths["decision"]),
        "source_name": source_name,
        "stroke_source_name": stroke_manifest.get("source_name", ""),
        "stroke_caveat": stroke_manifest.get("caveat", ""),
        "active_closure_l2_gate": float(active_closure_l2_gate),
        "allowed_closure_l2_gate": float(allowed_closure_l2_gate),
        "local_closure_l2_gate": float(local_closure_l2_gate),
        "active_closure_pf_gate": float(active_closure_pf_gate),
        "allowed_closure_pf_gate": float(allowed_closure_pf_gate),
        "local_closure_pf_gate": float(local_closure_pf_gate),
        "outside_residual_fraction_gate": float(outside_residual_fraction_gate),
        "live_residual_fraction_gate": float(live_residual_fraction_gate),
        "support_tail_fraction_gate": float(support_tail_fraction_gate),
        "live_support_fraction_gate": float(live_support_fraction_gate),
        "angular_support_gate": float(angular_support_gate),
        "caveat": (
            "Total support-exchange closure guard. This treats the fitted stroke exchange "
            "as a candidate divergence of T_support, J_support^nu = -J_fit^nu, and checks "
            "whether J_endpoint^nu + J_support^nu is small and localized on the full "
            "covariant audit surface. It is a finite-difference closure diagnostic, not a final support action."
        ),
    }
    return outputs, metadata


def write_support_total_closure_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_closure": outdir / "endpoint_support_total_closure_point_closure.csv",
        "scope_summary": outdir / "endpoint_support_total_closure_scope_summary.csv",
        "top_residual": outdir / "endpoint_support_total_closure_top_residual.csv",
        "decision": outdir / "endpoint_support_total_closure_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_support_total_closure_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
