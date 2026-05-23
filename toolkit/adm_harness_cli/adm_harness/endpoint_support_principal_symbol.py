from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


EPS = 1.0e-30


@dataclass(frozen=True)
class PrincipalSymbolSpec:
    heat_sound_cap: float = 0.35
    angular_sound_cap: float = 0.25
    support_sound_cap: float = 0.40
    speed_margin_gate: float = 1.0e-6
    speed_margin_watch: float = 5.0e-3
    transport_margin_watch: float = 5.0e-3
    heat_ratio_watch: float = 0.995
    high_psi_watch: float = 4.0
    eigen_condition_gate: float = 1.0e8
    live_support_density_gate: float = 1.0e-14


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


def _quantile(series: pd.Series, q: float) -> float:
    values = series.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.quantile(q)) if len(values) else float("nan")


def _signed(value: float, fallback: float = 1.0) -> float:
    if value > 0.0:
        return 1.0
    if value < 0.0:
        return -1.0
    return 1.0 if fallback >= 0.0 else -1.0


def _relativistic_add(v: float, c: float) -> float:
    denom = 1.0 + float(v) * float(c)
    if abs(denom) <= EPS:
        return math.copysign(float("inf"), float(v) + float(c))
    return float((float(v) + float(c)) / denom)


def _sound_from_buffer(buffer: float, load: float, cap: float) -> float:
    h = max(_finite(buffer, 0.0), 0.0)
    demand = max(_finite(load, 0.0), 0.0)
    if h <= 0.0:
        return 0.0
    return float(min(float(cap), math.sqrt(h / (h + demand + EPS))))


def _support_sound(row: pd.Series, spec: PrincipalSymbolSpec) -> float:
    support = abs(_finite(row.get("fit_abs_PF_density"), 0.0))
    source = abs(_finite(row.get("source_abs_density"), 0.0))
    h = max(_finite(row.get("enthalpy_buffer_density"), 0.0), 0.0)
    if support <= 0.0:
        return 0.0
    return float(min(spec.support_sound_cap, math.sqrt(support / (support + source + h + EPS))))


def _block(lambda_minus: float, lambda_plus: float) -> np.ndarray:
    center = 0.5 * (float(lambda_plus) + float(lambda_minus))
    half = 0.5 * (float(lambda_plus) - float(lambda_minus))
    return np.array([[center, half], [half, center]], dtype=float)


def _principal_matrix(row: pd.Series, spec: PrincipalSymbolSpec) -> tuple[np.ndarray, dict[str, float]]:
    heat_ratio_raw = abs(_finite(row.get("regulated_heat_flux_ratio"), 0.0))
    heat_ratio = float(np.clip(heat_ratio_raw, 0.0, 1.0 - 1.0e-12))
    radial_sign = _signed(_finite(row.get("target_radial_F"), 0.0), _finite(row.get("fit_F"), 1.0))
    flow_speed = radial_sign * heat_ratio
    h_reg = _finite(row.get("enthalpy_buffer_density"), 0.0)
    pf_load = abs(_finite(row.get("target_abs_PF_density"), 0.0)) + abs(_finite(row.get("fit_error_abs_PF_density"), 0.0))
    heat_sound = _sound_from_buffer(h_reg, pf_load, spec.heat_sound_cap)
    angular_sound = _sound_from_buffer(h_reg, abs(_finite(row.get("target_abs_PF_density"), 0.0)), spec.angular_sound_cap)
    support_sound = _support_sound(row, spec)

    heat_minus = _relativistic_add(flow_speed, -heat_sound)
    heat_plus = _relativistic_add(flow_speed, heat_sound)
    angular_minus = _relativistic_add(flow_speed, -angular_sound)
    angular_plus = _relativistic_add(flow_speed, angular_sound)
    support_minus = -support_sound
    support_plus = support_sound

    matrix = np.zeros((7, 7), dtype=float)
    matrix[0:2, 0:2] = _block(heat_minus, heat_plus)
    matrix[2:4, 2:4] = _block(angular_minus, angular_plus)
    matrix[4:6, 4:6] = _block(support_minus, support_plus)
    matrix[6, 6] = flow_speed
    aux = {
        "flow_speed": flow_speed,
        "heat_sound": heat_sound,
        "angular_sound": angular_sound,
        "support_sound": support_sound,
        "heat_lambda_minus": heat_minus,
        "heat_lambda_plus": heat_plus,
        "angular_lambda_minus": angular_minus,
        "angular_lambda_plus": angular_plus,
        "support_lambda_minus": support_minus,
        "support_lambda_plus": support_plus,
        "director_lambda": flow_speed,
    }
    return matrix, aux


def _symbol_row(row: pd.Series, spec: PrincipalSymbolSpec) -> dict[str, Any]:
    matrix, aux = _principal_matrix(row, spec)
    eigvals, eigvecs = np.linalg.eig(matrix)
    imag_max = float(np.max(np.abs(np.imag(eigvals)))) if len(eigvals) else float("nan")
    real = np.real(eigvals)
    finite_eigs = bool(np.all(np.isfinite(real)) and np.isfinite(imag_max))
    try:
        eig_condition = float(np.linalg.cond(eigvecs))
    except Exception:
        eig_condition = float("inf")
    alpha = _finite(row.get("alpha"), float("nan"))
    beta = _finite(row.get("beta"), float("nan"))
    gamma_ll = _finite(row.get("gamma_ll"), float("nan"))
    radial_light_scale = alpha / math.sqrt(gamma_ll) if alpha > 0.0 and gamma_ll > 0.0 else float("nan")
    coord_speeds = -beta + real * radial_light_scale if math.isfinite(radial_light_scale) else np.full_like(real, np.nan)
    light_minus = -beta - radial_light_scale if math.isfinite(radial_light_scale) else float("nan")
    light_plus = -beta + radial_light_scale if math.isfinite(radial_light_scale) else float("nan")
    max_abs_rel = float(np.max(np.abs(real))) if len(real) else float("nan")
    cone_margin = float(1.0 - max_abs_rel) if math.isfinite(max_abs_rel) else float("nan")
    coord_margin = float(np.min(np.minimum(light_plus - coord_speeds, coord_speeds - light_minus))) if len(coord_speeds) else float("nan")
    active = bool(_finite(row.get("medium_source_active"), 1.0) != 0.0)
    live = str(row.get("covariant_divergence_live", False)).lower() in {"true", "1", "yes"}
    support_density = abs(_finite(row.get("fit_abs_PF_density"), 0.0))
    transport_margin = _finite(row.get("transport_margin"), float("nan"))
    heat_ratio = _finite(row.get("regulated_heat_flux_ratio"), float("nan"))
    h_reg = _finite(row.get("enthalpy_buffer_density"), float("nan"))
    type_i = _finite(row.get("regulated_type_i_margin"), float("nan"))
    psi = _finite(row.get("transport_rapidity_abs"), float("nan"))

    real_eigen = bool(finite_eigs and imag_max <= 1.0e-9)
    complete = bool(math.isfinite(eig_condition) and eig_condition <= spec.eigen_condition_gate)
    inside_cone = bool(math.isfinite(cone_margin) and cone_margin >= spec.speed_margin_gate)
    positive_margin = bool(h_reg > 0.0 and type_i > 0.0 and transport_margin >= -1.0e-12)
    no_live_support = bool((not live) or support_density <= spec.live_support_density_gate)
    hard_pass = bool(real_eigen and complete and inside_cone and positive_margin and no_live_support)
    watch = bool(
        hard_pass
        and (
            cone_margin < spec.speed_margin_watch
            or transport_margin < spec.transport_margin_watch
            or heat_ratio > spec.heat_ratio_watch
            or psi > spec.high_psi_watch
        )
    )
    status = "fail" if not hard_pass else "watch" if watch else "pass"
    return {
        "case": row.get("case", ""),
        "s": _finite(row.get("s"), float("nan")),
        "l": _finite(row.get("l"), float("nan")),
        "assignment": str(row.get("assignment", "")),
        "stage": str(row.get("stage", "")),
        "region": str(row.get("region", "")),
        "medium_source_active": active,
        "covariant_divergence_live": live,
        "symbol_status": status,
        "hard_symbol_pass": hard_pass,
        "watch_symbol": watch,
        "real_eigen_pass": real_eigen,
        "complete_eigenbasis_pass": complete,
        "inside_service_cone_pass": inside_cone,
        "positive_margin_pass": positive_margin,
        "no_live_support_pass": no_live_support,
        "eigen_imag_max": imag_max,
        "eigen_condition": eig_condition,
        "max_abs_relative_characteristic_speed": max_abs_rel,
        "relative_cone_margin": cone_margin,
        "coordinate_cone_margin": coord_margin,
        "radial_light_speed_coordinate": radial_light_scale,
        "coordinate_light_minus": light_minus,
        "coordinate_light_plus": light_plus,
        "min_coordinate_characteristic_speed": float(np.nanmin(coord_speeds)) if len(coord_speeds) else float("nan"),
        "max_coordinate_characteristic_speed": float(np.nanmax(coord_speeds)) if len(coord_speeds) else float("nan"),
        "enthalpy_buffer_density": h_reg,
        "regulated_type_i_margin": type_i,
        "transport_margin": transport_margin,
        "regulated_heat_flux_ratio": heat_ratio,
        "transport_rapidity_abs": psi,
        "fit_abs_PF_density": support_density,
        **aux,
    }


def _active_mask(frame: pd.DataFrame) -> pd.Series:
    active = _bool_series(frame["medium_source_active"]) if "medium_source_active" in frame else pd.Series(True, index=frame.index)
    live = _bool_series(frame["covariant_divergence_live"]) if "covariant_divergence_live" in frame else pd.Series(False, index=frame.index)
    return active & (~live)


def _summary_row(label: str, mesh: str, kind: str, point: pd.DataFrame, symbol: pd.DataFrame, spec: PrincipalSymbolSpec) -> dict[str, Any]:
    active = _active_mask(point)
    live = _bool_series(point["covariant_divergence_live"]) if "covariant_divergence_live" in point else pd.Series(False, index=point.index)
    support_density = point["fit_abs_PF_density"].astype(float).abs() if "fit_abs_PF_density" in point else pd.Series(0.0, index=point.index)
    selected = symbol.loc[active].copy()
    live_support_rows = int(((live) & (support_density > spec.live_support_density_gate)).sum())
    fail_rows = int((selected["symbol_status"].astype(str) == "fail").sum())
    watch_rows = int((selected["symbol_status"].astype(str) == "watch").sum())
    min_margin = float(selected["relative_cone_margin"].astype(float).min()) if len(selected) else float("nan")
    hard_pass = bool(fail_rows == 0 and live_support_rows == 0 and math.isfinite(min_margin) and min_margin >= spec.speed_margin_gate)
    status = "fail" if not hard_pass else "watch" if (watch_rows > 0 or min_margin < spec.speed_margin_watch) else "pass"
    return {
        "label": label,
        "mesh": mesh,
        "kind": kind,
        "rows": int(len(symbol)),
        "active_rows": int(active.sum()),
        "live_rows": int(live.sum()),
        "live_support_rows": live_support_rows,
        "symbol_status": status,
        "hard_symbol_pass": hard_pass,
        "fail_rows": fail_rows,
        "watch_rows": watch_rows,
        "min_relative_cone_margin": min_margin,
        "p01_relative_cone_margin": _quantile(selected["relative_cone_margin"], 0.01) if len(selected) else float("nan"),
        "max_abs_relative_characteristic_speed": float(selected["max_abs_relative_characteristic_speed"].astype(float).max()) if len(selected) else float("nan"),
        "max_eigen_condition": float(selected["eigen_condition"].astype(float).replace([np.inf], np.nan).max()) if len(selected) else float("nan"),
        "min_h_reg": float(selected["enthalpy_buffer_density"].astype(float).min()) if len(selected) else float("nan"),
        "min_transport_margin": float(selected["transport_margin"].astype(float).min()) if len(selected) else float("nan"),
        "p01_transport_margin": _quantile(selected["transport_margin"], 0.01) if len(selected) else float("nan"),
        "p99_heat_ratio": _quantile(selected["regulated_heat_flux_ratio"], 0.99) if len(selected) else float("nan"),
        "max_transport_rapidity_abs": float(selected["transport_rapidity_abs"].astype(float).max()) if len(selected) else float("nan"),
        "max_heat_sound": float(selected["heat_sound"].astype(float).max()) if len(selected) else float("nan"),
        "max_support_sound": float(selected["support_sound"].astype(float).max()) if len(selected) else float("nan"),
    }


def _local_summary(label: str, mesh: str, kind: str, symbol: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    active = symbol.loc[symbol["medium_source_active"].astype(bool) & (~symbol["covariant_divergence_live"].astype(bool))]
    for key, group in active.groupby(["assignment", "stage", "region"], sort=False, dropna=False):
        assignment, stage, region = key
        rows.append({
            "label": label,
            "mesh": mesh,
            "kind": kind,
            "assignment": str(assignment),
            "stage": str(stage),
            "region": str(region),
            "rows": int(len(group)),
            "symbol_status": "fail" if (group["symbol_status"] == "fail").any() else "watch" if (group["symbol_status"] == "watch").any() else "pass",
            "fail_rows": int((group["symbol_status"] == "fail").sum()),
            "watch_rows": int((group["symbol_status"] == "watch").sum()),
            "min_relative_cone_margin": float(group["relative_cone_margin"].astype(float).min()),
            "p01_relative_cone_margin": _quantile(group["relative_cone_margin"], 0.01),
            "max_abs_relative_characteristic_speed": float(group["max_abs_relative_characteristic_speed"].astype(float).max()),
            "min_transport_margin": float(group["transport_margin"].astype(float).min()),
            "p01_transport_margin": _quantile(group["transport_margin"], 0.01),
            "p99_heat_ratio": _quantile(group["regulated_heat_flux_ratio"], 0.99),
            "max_transport_rapidity_abs": float(group["transport_rapidity_abs"].astype(float).max()),
            "min_h_reg": float(group["enthalpy_buffer_density"].astype(float).min()),
            "max_heat_sound": float(group["heat_sound"].astype(float).max()),
            "max_support_sound": float(group["support_sound"].astype(float).max()),
        })
    return pd.DataFrame(rows)


def build_principal_symbol_tables(
    point_fit: pd.DataFrame,
    *,
    label: str,
    mesh: str,
    kind: str,
    spec: PrincipalSymbolSpec | None = None,
) -> dict[str, pd.DataFrame]:
    spec = spec or PrincipalSymbolSpec()
    symbol_rows = [_symbol_row(row, spec) for _, row in point_fit.iterrows()]
    point_symbol = pd.DataFrame(symbol_rows)
    summary = pd.DataFrame([_summary_row(label, mesh, kind, point_fit, point_symbol, spec)])
    local = _local_summary(label, mesh, kind, point_symbol)
    return {
        "point_symbol": point_symbol,
        "run_summary": summary,
        "local_summary": local,
    }


def _load_stroke_dir(stroke_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Path]]:
    manifest_path = stroke_dir / "endpoint_support_stroke_exchange_manifest.json"
    manifest: dict[str, Any] = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    files = manifest.get("files", {})
    point_path = resolve_manifest_path(stroke_dir, files.get("point_fit", "endpoint_support_stroke_exchange_point_fit.csv"))
    return pd.read_csv(point_path), manifest, {
        "manifest": manifest_path,
        "point_fit": point_path,
    }


def build_principal_symbol_from_runs(
    runs: list[dict[str, str | Path]],
    *,
    spec: PrincipalSymbolSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    spec = spec or PrincipalSymbolSpec()
    point_frames: list[pd.DataFrame] = []
    summary_frames: list[pd.DataFrame] = []
    local_frames: list[pd.DataFrame] = []
    run_meta: list[dict[str, Any]] = []
    for run in runs:
        label = str(run["label"])
        mesh = str(run["mesh"])
        kind = str(run["kind"])
        stroke_dir = Path(run["stroke_dir"])
        point_fit, manifest, paths = _load_stroke_dir(stroke_dir)
        outputs = build_principal_symbol_tables(point_fit, label=label, mesh=mesh, kind=kind, spec=spec)
        for frame in outputs.values():
            if "kind" not in frame:
                frame.insert(0, "kind", kind)
            if "mesh" not in frame:
                frame.insert(0, "mesh", mesh)
            if "label" not in frame:
                frame.insert(0, "label", label)
        point_frames.append(outputs["point_symbol"])
        summary_frames.append(outputs["run_summary"])
        local_frames.append(outputs["local_summary"])
        run_meta.append({
            "label": label,
            "mesh": mesh,
            "kind": kind,
            "stroke_dir": str(stroke_dir),
            "point_fit": str(paths["point_fit"]),
            "point_fit_sha256": sha256_file(paths["point_fit"]),
            "stroke_source_name": manifest.get("source_name", ""),
        })
    point_symbol = pd.concat(point_frames, ignore_index=True) if point_frames else pd.DataFrame()
    run_summary = pd.concat(summary_frames, ignore_index=True) if summary_frames else pd.DataFrame()
    local_summary = pd.concat(local_frames, ignore_index=True) if local_frames else pd.DataFrame()
    decision = _decision(run_summary, local_summary)
    outputs = {
        "point_symbol": point_symbol,
        "run_summary": run_summary,
        "local_summary": local_summary,
        "decision": decision,
    }
    metadata = {
        "source_name": "endpoint_support_principal_symbol",
        "runs": run_meta,
        "spec": spec.__dict__,
        "caveat": (
            "Reduced fixed-background local principal-symbol harness. It checks a "
            "constitutive endpoint/support sector on the prescribed service metric; "
            "it is not a full matter action, fixed-background evolution, or coupled Einstein-matter system."
        ),
    }
    return outputs, metadata, _report(outputs, metadata)


def _decision(run_summary: pd.DataFrame, local_summary: pd.DataFrame) -> pd.DataFrame:
    promoted = run_summary.loc[run_summary["kind"].astype(str) == "reference_24x14"]
    hard_fail = bool((promoted["symbol_status"].astype(str) == "fail").any()) if len(promoted) else True
    watch = bool((promoted["symbol_status"].astype(str) == "watch").any()) if len(promoted) else False
    dense_local = local_summary.loc[
        (local_summary["kind"].astype(str) == "reference_24x14")
        & (local_summary["mesh"].astype(str) == "dense")
    ]
    tightest = dense_local.sort_values("min_relative_cone_margin").head(1)
    status = "fail" if hard_fail else "watch" if watch else "pass"
    return pd.DataFrame([{
        "principal_symbol_status": status,
        "passes_reduced_principal_symbol_gate": bool(status != "fail"),
        "promoted_runs": int(len(promoted)),
        "promoted_fail_runs": int((promoted["symbol_status"].astype(str) == "fail").sum()) if len(promoted) else 0,
        "promoted_watch_runs": int((promoted["symbol_status"].astype(str) == "watch").sum()) if len(promoted) else 0,
        "dense_tightest_assignment": str(tightest["assignment"].iloc[0]) if len(tightest) else "",
        "dense_tightest_stage": str(tightest["stage"].iloc[0]) if len(tightest) else "",
        "dense_tightest_region": str(tightest["region"].iloc[0]) if len(tightest) else "",
        "dense_tightest_relative_cone_margin": _finite(tightest["min_relative_cone_margin"].iloc[0], float("nan")) if len(tightest) else float("nan"),
        "decision_read": (
            "reduced endpoint/support principal symbol has real complete in-cone characteristics on promoted runs, with watch rows requiring action-level follow-up"
            if status == "watch"
            else "reduced endpoint/support principal symbol clears promoted baseline/dense runs without watch rows"
            if status == "pass"
            else "reduced endpoint/support principal symbol fails a promoted necessary hyperbolicity gate"
        ),
    }])


def _fmt(value: Any) -> str:
    number = _finite(value, float("nan"))
    if not math.isfinite(number):
        return "nan"
    if abs(number) > 0.0 and (abs(number) < 1.0e-4 or abs(number) >= 1.0e5):
        return f"{number:.3e}"
    return f"{number:.6f}"


def _report(outputs: dict[str, pd.DataFrame], metadata: dict[str, Any]) -> str:
    run_summary = outputs["run_summary"]
    local_summary = outputs["local_summary"]
    decision = outputs["decision"].iloc[0]
    dense_local = (
        local_summary.loc[
            (local_summary["kind"].astype(str) == "reference_24x14")
            & (local_summary["mesh"].astype(str) == "dense")
        ]
        .sort_values("min_relative_cone_margin")
        .head(8)
    )
    lines = [
        "# Stage II Beta075 Reduced Principal-Symbol Hyperbolicity Gate",
        "",
        "## Status",
        "",
        f"Overall status: `{decision['principal_symbol_status']}`.",
        "",
        "This is a fixed-background local principal-symbol harness for the promoted endpoint/support constitutive sector. It uses the prescribed beta075 service metric and the support-stroke point-fit ledgers; it does not evolve the metric or claim a complete matter action.",
        "",
        "## Reduced Model",
        "",
        "The local radial-frame principal symbol uses seven primitive perturbations:",
        "",
        "```text",
        "U = (h, psi, chi_Omega, pi_Omega, Phi_support, Pi_support, n_l)",
        "```",
        "",
        "It checks block principal speeds for heat/enthalpy, angular internal response, support stroke/stress, and director advection. Rest-frame characteristic speeds are mapped through the ADM service cone `dl/dsigma = -beta +/- alpha/sqrt(gamma_ll)`.",
        "",
        "Gate conditions:",
        "",
        "```text",
        "real finite characteristic speeds",
        "complete eigenbasis",
        "relative speeds inside the service cone",
        "positive h_reg / Type-I / transport margin",
        "zero live support exchange",
        "watch if cone margin, heat ratio, transport margin, or rapidity gets too close to boundary",
        "```",
        "",
        "## Run Summary",
        "",
        "| label | status | active rows | fail rows | watch rows | min cone margin | p01 cone margin | p99 heat ratio | max psi |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in run_summary.iterrows():
        lines.append(
            f"| {row['label']} | {row['symbol_status']} | {int(row['active_rows'])} | {int(row['fail_rows'])} | {int(row['watch_rows'])} | "
            f"{_fmt(row['min_relative_cone_margin'])} | {_fmt(row['p01_relative_cone_margin'])} | {_fmt(row['p99_heat_ratio'])} | {_fmt(row['max_transport_rapidity_abs'])} |"
        )
    lines.extend([
        "",
        "## Dense Adversarial Rows",
        "",
        "| assignment | stage | region | status | min cone margin | p01 cone margin | min transport margin | p99 heat ratio | max psi |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for _, row in dense_local.iterrows():
        lines.append(
            f"| {row['assignment']} | {row['stage']} | {row['region']} | {row['symbol_status']} | "
            f"{_fmt(row['min_relative_cone_margin'])} | {_fmt(row['p01_relative_cone_margin'])} | "
            f"{_fmt(row['min_transport_margin'])} | {_fmt(row['p99_heat_ratio'])} | {_fmt(row['max_transport_rapidity_abs'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        str(decision["decision_read"]),
        "",
        "The result should be read as a necessary local hyperbolicity check. A pass/watch result means the reduced constitutive sector has a real in-cone local principal symbol on the tested rows, but the boundary-near rows still need a real evolution or action-level closure. A fail would have killed the current support-sector PDE direction before evolution.",
        "",
        "## Next",
        "",
        "```text",
        "1. Aim any reduced evolution model at the dense local watch rows first.",
        "2. Freeze support-sector coefficients before cross-mesh evolution tests.",
        "3. Do not treat this as a coupled Einstein-matter result.",
        "```",
        "",
        "## Provenance",
        "",
    ])
    for run in metadata["runs"]:
        lines.append(f"- `{run['label']}`: `{run['point_fit']}`")
    return "\n".join(lines) + "\n"


def write_principal_symbol_outputs(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_symbol": outdir / "endpoint_support_principal_symbol_point.csv",
        "run_summary": outdir / "endpoint_support_principal_symbol_run_summary.csv",
        "local_summary": outdir / "endpoint_support_principal_symbol_local_summary.csv",
        "decision": outdir / "endpoint_support_principal_symbol_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "endpoint_support_principal_symbol_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
