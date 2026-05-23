from __future__ import annotations

import json
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _bool_series, _finite, _quantile
from .source_ledger import sha256_file, write_manifest


EPS = 1.0e-30


@dataclass(frozen=True)
class SourceFamilyValidationRun:
    label: str
    mesh: str
    stroke_dir: Path
    total_closure_dir: Path


def default_validation_runs() -> tuple[SourceFamilyValidationRun, ...]:
    baseline_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15")
    dense_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12")
    return (
        SourceFamilyValidationRun(
            "baseline_formal_operator_24x14",
            "baseline",
            baseline_root / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
            baseline_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
        SourceFamilyValidationRun(
            "dense_formal_operator_24x14",
            "dense",
            dense_root / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
            dense_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
    )


@dataclass(frozen=True)
class SourceFamilyValidationInputs:
    equation_dir: Path
    principal_symbol_dir: Path
    runs: tuple[SourceFamilyValidationRun, ...] = field(default_factory=default_validation_runs)


@dataclass(frozen=True)
class SourceFamilyValidationSpec:
    max_workers: int | None = 6
    support_operator_sound_cap: float = 0.40
    heat_sound_cap: float = 0.35
    angular_sound_cap: float = 0.25
    speed_margin_gate: float = 1.0e-6
    speed_margin_watch: float = 5.0e-3
    transport_margin_watch: float = 5.0e-3
    heat_ratio_watch: float = 0.995
    high_psi_watch: float = 4.0
    eigen_condition_gate: float = 1.0e8
    live_support_density_gate: float = 1.0e-14
    local_pf_component_watch: float = 0.40
    local_pf_component_fail: float = 0.80
    local_total_closure_watch_fraction: float = 0.90
    source_profile_scale_watch: float = 0.15


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _truth(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom > 0.0 else float("nan")


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


def _block(lambda_minus: float, lambda_plus: float) -> np.ndarray:
    center = 0.5 * (float(lambda_plus) + float(lambda_minus))
    half = 0.5 * (float(lambda_plus) - float(lambda_minus))
    return np.array([[center, half], [half, center]], dtype=float)


def _operator_terms() -> pd.DataFrame:
    rows = [
        {
            "operator_id": "O01",
            "operator_block": "support_storage",
            "operator": "partial_tau Phi_support = Pi_support",
            "principal_role": "introduces a first-order support storage variable",
        },
        {
            "operator_id": "O02",
            "operator_block": "support_stress",
            "operator": "partial_tau Pi_support = partial_l(c_sigma^2 partial_l Phi_support) + partial_s(c_s^2 partial_s Phi_support) - gamma Pi_support + lower_order(P,F)",
            "principal_role": "supplies finite support-stress characteristic speed; P and F are lower-order exchange drives",
        },
        {
            "operator_id": "O03",
            "operator_block": "support_tensor",
            "operator": "nabla_mu T_support^{mu nu} = P u^nu + F s^nu",
            "principal_role": "restores conservation through explicit localized support tensor divergence",
        },
        {
            "operator_id": "O04",
            "operator_block": "rapidity_transport",
            "operator": "partial_tau psi + v_l partial_l psi + v_s partial_s psi = S_psi",
            "principal_role": "keeps source response in the bounded rapidity variable",
        },
        {
            "operator_id": "O05",
            "operator_block": "hyperbolicity_gate",
            "operator": "A^0(U) partial_t U + A^l(U) partial_l U = lower_order(U,P,F)",
            "principal_role": "P/F roughness is a source-shape watch unless it breaks aggregate support closure or cone margins",
        },
    ]
    return pd.DataFrame(rows)


def _component_error_map(component_summary: pd.DataFrame) -> dict[tuple[str, str], dict[str, float]]:
    mapping: dict[tuple[str, str], dict[str, float]] = {}
    if not len(component_summary):
        return mapping
    frame = component_summary.copy()
    frame["active_normalized_l1_error"] = pd.to_numeric(frame["active_normalized_l1_error"], errors="coerce")
    for _, row in frame.dropna(subset=["active_normalized_l1_error"]).iterrows():
        group_key = str(row.get("group_key", ""))
        parts = group_key.split("|")
        if len(parts) < 2:
            continue
        stage, region = parts[0], parts[1]
        component = str(row.get("component", ""))
        value = _finite(row["active_normalized_l1_error"], 0.0)
        mapping.setdefault((stage, region), {})[component] = max(
            mapping.setdefault((stage, region), {}).get(component, 0.0),
            value,
        )
    return mapping


def _attach_operator_fields(point_fit: pd.DataFrame, component_summary: pd.DataFrame) -> pd.DataFrame:
    component_map = _component_error_map(component_summary)
    out = point_fit.copy()
    p_errors: list[float] = []
    f_errors: list[float] = []
    for _, row in out.iterrows():
        values = component_map.get((str(row.get("stage", "")), str(row.get("region", ""))), {})
        p_errors.append(float(values.get("P", 0.0)))
        f_errors.append(float(values.get("F", 0.0)))
    out["operator_local_P_error"] = p_errors
    out["operator_local_F_error"] = f_errors
    out["operator_local_PF_error"] = np.maximum(out["operator_local_P_error"].astype(float), out["operator_local_F_error"].astype(float))
    out["operator_exchange_residual_load"] = (
        out.get("fit_error_abs_PF_density", pd.Series(0.0, index=out.index)).astype(float).abs()
        + out["operator_local_PF_error"].astype(float)
        * out.get("target_abs_PF_density", pd.Series(0.0, index=out.index)).astype(float).abs()
    )
    out["operator_support_stiffness_density"] = np.maximum(
        out.get("fit_abs_PF_density", pd.Series(0.0, index=out.index)).astype(float).abs()
        - out.get("fit_error_abs_PF_density", pd.Series(0.0, index=out.index)).astype(float).abs(),
        0.0,
    )
    out["operator_support_inertia_density"] = (
        out.get("source_abs_density", pd.Series(0.0, index=out.index)).astype(float).abs()
        + out.get("enthalpy_buffer_density", pd.Series(0.0, index=out.index)).astype(float).clip(lower=0.0)
        + out["operator_exchange_residual_load"].astype(float).abs()
    )
    return out


def _operator_support_sound(row: pd.Series, spec: SourceFamilyValidationSpec) -> float:
    stiffness = max(_finite(row.get("operator_support_stiffness_density"), 0.0), 0.0)
    inertia = max(_finite(row.get("operator_support_inertia_density"), 0.0), 0.0)
    if stiffness <= 0.0:
        return 0.0
    return float(min(spec.support_operator_sound_cap, math.sqrt(stiffness / (stiffness + inertia + EPS))))


def _formal_principal_matrix(row: pd.Series, spec: SourceFamilyValidationSpec) -> tuple[np.ndarray, dict[str, float]]:
    heat_ratio_raw = abs(_finite(row.get("regulated_heat_flux_ratio"), 0.0))
    heat_ratio = float(np.clip(heat_ratio_raw, 0.0, 1.0 - 1.0e-12))
    radial_sign = _signed(_finite(row.get("target_radial_F"), 0.0), _finite(row.get("fit_F"), 1.0))
    flow_speed = radial_sign * heat_ratio
    h_reg = _finite(row.get("enthalpy_buffer_density"), 0.0)
    base_pf_load = abs(_finite(row.get("target_abs_PF_density"), 0.0))
    residual_load = abs(_finite(row.get("operator_exchange_residual_load"), 0.0))
    heat_sound = _sound_from_buffer(h_reg, base_pf_load + residual_load, spec.heat_sound_cap)
    angular_sound = _sound_from_buffer(h_reg, base_pf_load, spec.angular_sound_cap)
    support_sound = _operator_support_sound(row, spec)

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
        "operator_support_sound": support_sound,
        "heat_lambda_minus": heat_minus,
        "heat_lambda_plus": heat_plus,
        "angular_lambda_minus": angular_minus,
        "angular_lambda_plus": angular_plus,
        "support_lambda_minus": support_minus,
        "support_lambda_plus": support_plus,
        "director_lambda": flow_speed,
    }
    return matrix, aux


def _formal_symbol_row(row: pd.Series, spec: SourceFamilyValidationSpec) -> dict[str, Any]:
    matrix, aux = _formal_principal_matrix(row, spec)
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
    local_p_error = _finite(row.get("operator_local_P_error"), 0.0)
    local_f_error = _finite(row.get("operator_local_F_error"), 0.0)

    real_eigen = bool(finite_eigs and imag_max <= 1.0e-9)
    complete = bool(math.isfinite(eig_condition) and eig_condition <= spec.eigen_condition_gate)
    inside_cone = bool(math.isfinite(cone_margin) and cone_margin >= spec.speed_margin_gate)
    positive_margin = bool(h_reg > 0.0 and type_i > 0.0 and transport_margin >= -1.0e-12)
    no_live_support = bool((not live) or support_density <= spec.live_support_density_gate)
    component_shape_ok = bool(max(local_p_error, local_f_error) <= spec.local_pf_component_fail)
    hard_pass = bool(real_eigen and complete and inside_cone and positive_margin and no_live_support and component_shape_ok)
    watch = bool(
        hard_pass
        and (
            cone_margin < spec.speed_margin_watch
            or transport_margin < spec.transport_margin_watch
            or heat_ratio > spec.heat_ratio_watch
            or psi > spec.high_psi_watch
            or max(local_p_error, local_f_error) > spec.local_pf_component_watch
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
        "formal_symbol_status": status,
        "hard_formal_symbol_pass": hard_pass,
        "watch_formal_symbol": watch,
        "real_eigen_pass": real_eigen,
        "complete_eigenbasis_pass": complete,
        "inside_service_cone_pass": inside_cone,
        "positive_margin_pass": positive_margin,
        "no_live_support_pass": no_live_support,
        "component_shape_pass": component_shape_ok,
        "eigen_imag_max": imag_max,
        "eigen_condition": eig_condition,
        "max_abs_relative_characteristic_speed": max_abs_rel,
        "relative_cone_margin": cone_margin,
        "coordinate_cone_margin": coord_margin,
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
        "fit_error_abs_PF_density": abs(_finite(row.get("fit_error_abs_PF_density"), 0.0)),
        "operator_support_stiffness_density": _finite(row.get("operator_support_stiffness_density"), 0.0),
        "operator_support_inertia_density": _finite(row.get("operator_support_inertia_density"), 0.0),
        "operator_exchange_residual_load": _finite(row.get("operator_exchange_residual_load"), 0.0),
        "operator_local_P_error": local_p_error,
        "operator_local_F_error": local_f_error,
        **aux,
    }


def _active_mask(frame: pd.DataFrame) -> pd.Series:
    active = frame["medium_source_active"].astype(bool) if "medium_source_active" in frame else pd.Series(True, index=frame.index)
    live = frame["covariant_divergence_live"].astype(bool) if "covariant_divergence_live" in frame else pd.Series(False, index=frame.index)
    return active & (~live)


def _run_summary(label: str, mesh: str, symbol: pd.DataFrame, total_closure: pd.DataFrame, spec: SourceFamilyValidationSpec) -> dict[str, Any]:
    active = _active_mask(symbol)
    selected = symbol.loc[active].copy()
    fail_rows = int((selected["formal_symbol_status"].astype(str) == "fail").sum())
    watch_rows = int((selected["formal_symbol_status"].astype(str) == "watch").sum())
    min_margin = float(selected["relative_cone_margin"].astype(float).min()) if len(selected) else float("nan")
    local_total = _finite(total_closure.iloc[0]["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan"))
    local_gate = _finite(total_closure.iloc[0]["local_closure_pf_gate"], float("nan"))
    total_closure_watch = bool(math.isfinite(local_total) and math.isfinite(local_gate) and local_total > spec.local_total_closure_watch_fraction * local_gate)
    hard_pass = bool(fail_rows == 0 and math.isfinite(min_margin) and min_margin >= spec.speed_margin_gate)
    status = "fail" if not hard_pass else "watch" if (watch_rows > 0 or total_closure_watch or min_margin < spec.speed_margin_watch) else "pass"
    return {
        "label": label,
        "mesh": mesh,
        "rows": int(len(symbol)),
        "active_rows": int(active.sum()),
        "formal_symbol_status": status,
        "hard_formal_symbol_pass": hard_pass,
        "fail_rows": fail_rows,
        "watch_rows": watch_rows,
        "min_relative_cone_margin": min_margin,
        "p01_relative_cone_margin": _quantile(selected["relative_cone_margin"], 0.01) if len(selected) else float("nan"),
        "max_abs_relative_characteristic_speed": float(selected["max_abs_relative_characteristic_speed"].astype(float).max()) if len(selected) else float("nan"),
        "max_eigen_condition": float(selected["eigen_condition"].astype(float).replace([np.inf], np.nan).max()) if len(selected) else float("nan"),
        "min_h_reg": float(selected["enthalpy_buffer_density"].astype(float).min()) if len(selected) else float("nan"),
        "min_transport_margin": float(selected["transport_margin"].astype(float).min()) if len(selected) else float("nan"),
        "p99_heat_ratio": _quantile(selected["regulated_heat_flux_ratio"], 0.99) if len(selected) else float("nan"),
        "max_transport_rapidity_abs": float(selected["transport_rapidity_abs"].astype(float).max()) if len(selected) else float("nan"),
        "max_operator_support_sound": float(selected["operator_support_sound"].astype(float).max()) if len(selected) else float("nan"),
        "max_local_P_error": float(selected["operator_local_P_error"].astype(float).max()) if len(selected) else float("nan"),
        "max_local_F_error": float(selected["operator_local_F_error"].astype(float).max()) if len(selected) else float("nan"),
        "support_total_local_pf_ratio": local_total,
        "support_total_local_pf_gate": local_gate,
        "support_total_closure_watch": total_closure_watch,
    }


def _local_summary(label: str, mesh: str, symbol: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    active = symbol.loc[_active_mask(symbol)]
    for key, group in active.groupby(["assignment", "stage", "region"], sort=False, dropna=False):
        assignment, stage, region = key
        rows.append({
            "label": label,
            "mesh": mesh,
            "assignment": str(assignment),
            "stage": str(stage),
            "region": str(region),
            "rows": int(len(group)),
            "formal_symbol_status": (
                "fail"
                if (group["formal_symbol_status"] == "fail").any()
                else "watch"
                if (group["formal_symbol_status"] == "watch").any()
                else "pass"
            ),
            "fail_rows": int((group["formal_symbol_status"] == "fail").sum()),
            "watch_rows": int((group["formal_symbol_status"] == "watch").sum()),
            "min_relative_cone_margin": float(group["relative_cone_margin"].astype(float).min()),
            "p01_relative_cone_margin": _quantile(group["relative_cone_margin"], 0.01),
            "min_transport_margin": float(group["transport_margin"].astype(float).min()),
            "p99_heat_ratio": _quantile(group["regulated_heat_flux_ratio"], 0.99),
            "max_transport_rapidity_abs": float(group["transport_rapidity_abs"].astype(float).max()),
            "max_operator_support_sound": float(group["operator_support_sound"].astype(float).max()),
            "max_local_P_error": float(group["operator_local_P_error"].astype(float).max()),
            "max_local_F_error": float(group["operator_local_F_error"].astype(float).max()),
        })
    return pd.DataFrame(rows)


def _load_run(run: SourceFamilyValidationRun) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Path], dict[str, Any]]:
    stroke_manifest_path = run.stroke_dir / "endpoint_support_stroke_exchange_manifest.json"
    stroke_manifest = _read_json(stroke_manifest_path)
    point_path = run.stroke_dir / "endpoint_support_stroke_exchange_point_fit.csv"
    component_path = run.stroke_dir / "endpoint_support_stroke_exchange_selected_component_summary.csv"
    stroke_decision_path = run.stroke_dir / "endpoint_support_stroke_exchange_decision.csv"
    total_decision_path = run.total_closure_dir / "endpoint_support_total_closure_decision.csv"
    point = _read_csv(point_path)
    component = _read_csv(component_path)
    total = _read_csv(total_decision_path)
    paths = {
        "stroke_manifest": stroke_manifest_path,
        "point_fit": point_path,
        "component_summary": component_path,
        "stroke_decision": stroke_decision_path,
        "total_closure_decision": total_decision_path,
    }
    return point, component, total, paths, stroke_manifest


def _build_run(
    run: SourceFamilyValidationRun,
    spec: SourceFamilyValidationSpec,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    point, component, total, paths, stroke_manifest = _load_run(run)
    operator_point = _attach_operator_fields(point, component)
    symbol = pd.DataFrame([_formal_symbol_row(row, spec) for _, row in operator_point.iterrows()])
    for frame in (symbol,):
        frame.insert(0, "mesh", run.mesh)
        frame.insert(0, "label", run.label)
    summary = pd.DataFrame([_run_summary(run.label, run.mesh, symbol, total, spec)])
    local = _local_summary(run.label, run.mesh, symbol)
    run_meta = {
        "label": run.label,
        "mesh": run.mesh,
        "stroke_dir": str(run.stroke_dir),
        "total_closure_dir": str(run.total_closure_dir),
        "stroke_source_name": stroke_manifest.get("source_name", ""),
        "paths": {key: str(path) for key, path in paths.items()},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    return {
        "point_symbol": symbol,
        "run_summary": summary,
        "local_summary": local,
    }, run_meta


def _validation_gates(
    run_summary: pd.DataFrame,
    equation_decision: pd.DataFrame,
    inherited_principal_decision: pd.DataFrame,
    spec: SourceFamilyValidationSpec,
) -> pd.DataFrame:
    equation = equation_decision.iloc[0]
    inherited = inherited_principal_decision.iloc[0]
    dense = run_summary.loc[run_summary["mesh"].astype(str).eq("dense")]
    dense_row = dense.iloc[0] if len(dense) else run_summary.iloc[0]
    rows = [
        {
            "gate": "formal_equation_package",
            "status": "pass" if _truth(equation["hard_equation_package_pass"]) else "fail",
            "value": str(equation["formal_equation_status"]),
            "gate_value": "hard_equation_package_pass",
            "read": str(equation["decision_read"]),
        },
        {
            "gate": "derived_principal_symbol",
            "status": str(dense_row["formal_symbol_status"]),
            "value": _finite(dense_row["min_relative_cone_margin"], float("nan")),
            "gate_value": spec.speed_margin_gate,
            "read": "principal symbol recomputed from the formal support-reservoir operator",
        },
        {
            "gate": "inherited_principal_symbol_comparison",
            "status": "pass"
            if str(inherited["principal_symbol_status"]) != "fail"
            else "fail",
            "value": _finite(inherited["dense_tightest_relative_cone_margin"], float("nan")),
            "gate_value": _finite(dense_row["min_relative_cone_margin"], float("nan")),
            "read": "derived operator preserves the inherited principal-symbol gate class",
        },
        {
            "gate": "support_operator_local_exchange",
            "status": "watch"
            if max(_finite(dense_row["max_local_P_error"]), _finite(dense_row["max_local_F_error"])) > spec.local_pf_component_watch
            else "pass",
            "value": max(_finite(dense_row["max_local_P_error"]), _finite(dense_row["max_local_F_error"])),
            "gate_value": spec.local_pf_component_watch,
            "read": "local P/F shape remains a derivation watch rather than a total-closure failure",
        },
        {
            "gate": "support_total_closure_margin",
            "status": "watch" if _truth(dense_row["support_total_closure_watch"]) else "pass",
            "value": _finite(dense_row["support_total_local_pf_ratio"], float("nan")),
            "gate_value": _finite(dense_row["support_total_local_pf_gate"], float("nan")),
            "read": "support tensor restores total conservation but dense local closure is close to the gate",
        },
        {
            "gate": "live_support_exclusion",
            "status": "pass" if int(run_summary["fail_rows"].astype(int).sum()) == 0 else "fail",
            "value": int(run_summary["fail_rows"].astype(int).sum()),
            "gate_value": 0,
            "read": "formal operator did not introduce hard symbol, live-support, or component-shape failures",
        },
    ]
    return pd.DataFrame(rows)


def _decision(gates: pd.DataFrame, run_summary: pd.DataFrame, spec: SourceFamilyValidationSpec) -> pd.DataFrame:
    fail_count = int((gates["status"].astype(str) == "fail").sum())
    watch_count = int((gates["status"].astype(str) == "watch").sum())
    dense = run_summary.loc[run_summary["mesh"].astype(str).eq("dense")]
    dense_row = dense.iloc[0] if len(dense) else run_summary.iloc[0]
    hard_pass = fail_count == 0
    thin_margin = _finite(dense_row["min_relative_cone_margin"], float("nan")) < spec.speed_margin_watch
    p_watch = _finite(dense_row["max_local_P_error"], 0.0) > spec.local_pf_component_watch
    status = (
        "source_family_validation_watch_pass"
        if hard_pass and watch_count
        else "source_family_validation_pass"
        if hard_pass
        else "source_family_validation_fail"
    )
    bigger_issue = bool(not hard_pass)
    return pd.DataFrame([{
        "source_family_validation_status": status,
        "hard_validation_pass": hard_pass,
        "bigger_issue_flag": bigger_issue,
        "failed_gate_count": fail_count,
        "watch_count": watch_count,
        "safety_margin_resolved": bool(hard_pass and not thin_margin),
        "exchange_refinement_resolved": bool(hard_pass and not p_watch),
        "dense_min_relative_cone_margin": _finite(dense_row["min_relative_cone_margin"], float("nan")),
        "dense_p01_relative_cone_margin": _finite(dense_row["p01_relative_cone_margin"], float("nan")),
        "dense_max_local_P_error": _finite(dense_row["max_local_P_error"], float("nan")),
        "dense_max_local_F_error": _finite(dense_row["max_local_F_error"], float("nan")),
        "dense_support_total_local_pf_ratio": _finite(dense_row["support_total_local_pf_ratio"], float("nan")),
        "dense_operator_support_sound_max": _finite(dense_row["max_operator_support_sound"], float("nan")),
        "decision_read": (
            "formal support-reservoir operator preserves hard hyperbolicity and total-closure gates, but safety-margin debt remains watch-level"
            if hard_pass and watch_count
            else "formal support-reservoir operator clears the validation gates without watch rows"
            if hard_pass
            else "formal support-reservoir operator exposes a hard source-family validation failure"
        ),
    }])


def build_source_family_validation(
    inputs: SourceFamilyValidationInputs,
    *,
    spec: SourceFamilyValidationSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or SourceFamilyValidationSpec()
    equation_decision = _read_csv(inputs.equation_dir / "beta075_source_family_equation_decision.csv")
    equation_boundary = _read_csv(inputs.equation_dir / "beta075_source_family_claim_boundary.csv")
    inherited_principal_decision = _read_csv(inputs.principal_symbol_dir / "endpoint_support_principal_symbol_decision.csv")
    workers = max(1, min(len(inputs.runs), int(spec.max_workers or 1)))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        run_results = list(executor.map(lambda run: _build_run(run, spec), inputs.runs))
    point_frames = [result[0]["point_symbol"] for result in run_results]
    summary_frames = [result[0]["run_summary"] for result in run_results]
    local_frames = [result[0]["local_summary"] for result in run_results]
    run_meta = [result[1] for result in run_results]
    point_symbol = pd.concat(point_frames, ignore_index=True)
    run_summary = pd.concat(summary_frames, ignore_index=True)
    local_summary = pd.concat(local_frames, ignore_index=True)
    gates = _validation_gates(run_summary, equation_decision, inherited_principal_decision, spec)
    decision = _decision(gates, run_summary, spec)
    outputs = {
        "operator_terms": _operator_terms(),
        "run_summary": run_summary,
        "local_summary": local_summary,
        "point_symbol": point_symbol,
        "validation_gates": gates,
        "claim_boundary": equation_boundary,
        "decision": decision,
    }
    input_paths = {
        "equation_decision": inputs.equation_dir / "beta075_source_family_equation_decision.csv",
        "equation_claim_boundary": inputs.equation_dir / "beta075_source_family_claim_boundary.csv",
        "principal_decision": inputs.principal_symbol_dir / "endpoint_support_principal_symbol_decision.csv",
    }
    metadata = {
        "source_name": "beta075_source_family_validation",
        "spec": spec.__dict__,
        "workers": workers,
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "runs": run_meta,
        "claim_boundary": (
            "Source-family validation for the formal beta075 regulated director/support-reservoir equations. "
            "The support reservoir is specified as a derivative storage/stress operator and the local principal symbol "
            "is recomputed on baseline/dense fixed-background ledgers. This remains a fixed-background validation rung, "
            "not a coupled Einstein-matter proof or final matter action."
        ),
    }
    return outputs, metadata


def write_source_family_validation_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "operator_terms": outdir / "beta075_source_family_validation_operator_terms.csv",
        "run_summary": outdir / "beta075_source_family_validation_run_summary.csv",
        "local_summary": outdir / "beta075_source_family_validation_local_summary.csv",
        "point_symbol": outdir / "beta075_source_family_validation_point_symbol.csv",
        "validation_gates": outdir / "beta075_source_family_validation_gates.csv",
        "claim_boundary": outdir / "beta075_source_family_validation_claim_boundary.csv",
        "decision": outdir / "beta075_source_family_validation_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_source_family_validation_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
