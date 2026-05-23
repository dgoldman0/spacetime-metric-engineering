from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import PI8, sha256_file, write_manifest


EPS = 1.0e-30


@dataclass(frozen=True)
class FirstOrder3P1RunSpec:
    label: str
    mesh: str
    surface_family: str
    role: str
    covariant_dir: Path
    total_closure_dir: Path


def default_first_order_3p1_runs() -> tuple[FirstOrder3P1RunSpec, ...]:
    baseline_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15")
    dense_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12")
    v2_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_v2_dense377x241")
    return (
        FirstOrder3P1RunSpec(
            "sealed_baseline_v5",
            "baseline",
            "sealed_beta075_v5",
            "reference_baseline",
            baseline_root / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5",
            baseline_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
        FirstOrder3P1RunSpec(
            "sealed_dense_v5",
            "dense",
            "sealed_beta075_v5",
            "reference_dense",
            dense_root / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5",
            dense_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
        FirstOrder3P1RunSpec(
            "lower_service_dense_v2",
            "dense_v2",
            "lower_service_beta075_v2",
            "adjacent_service_surface",
            v2_root / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5",
            v2_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
    )


@dataclass(frozen=True)
class FirstOrder3P1Inputs:
    equation_dir: Path
    energy_constant_dir: Path
    runs: tuple[FirstOrder3P1RunSpec, ...] = field(default_factory=default_first_order_3p1_runs)


@dataclass(frozen=True)
class FirstOrder3P1Spec:
    required_surface_count: int = 3
    local_closure_watch_fraction: float = 0.90
    boost_watch: float = 0.98
    active_constraint_driver_watch: float = 0.90
    adjacent_surface_drift_gate: float = 0.03
    adjacent_boost_drift_gate: float = 0.01


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _truth(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"1", "true", "yes"})


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom > 0.0 else float("nan")


def _volume(frame: pd.DataFrame) -> pd.Series:
    if "volume_weight" in frame:
        return frame["volume_weight"].astype(float)
    return pd.Series(1.0, index=frame.index, dtype=float)


def _source_abs_volume(frame: pd.DataFrame, mask: pd.Series) -> float:
    selected = frame.loc[mask]
    if not len(selected):
        return 0.0
    if "source_abs_volume" in selected:
        return float(selected["source_abs_volume"].fillna(0.0).astype(float).sum())
    return float((selected["source_abs_density"].fillna(0.0).astype(float) * _volume(selected)).sum())


def _component_abs_volume(frame: pd.DataFrame, mask: pd.Series, column: str) -> float:
    selected = frame.loc[mask]
    if not len(selected) or column not in selected:
        return 0.0
    return float((selected[column].fillna(0.0).astype(float).abs() * _volume(selected)).sum())


def _sum_column(frame: pd.DataFrame, mask: pd.Series, column: str) -> float:
    selected = frame.loc[mask]
    if not len(selected) or column not in selected:
        return 0.0
    return float(selected[column].fillna(0.0).astype(float).sum())


def _driver_summary(label: str, point_closure: pd.DataFrame) -> dict[str, Any]:
    live = _bool_series(point_closure["covariant_divergence_live"]) if "covariant_divergence_live" in point_closure else pd.Series(False, index=point_closure.index)
    active = _bool_series(point_closure["medium_source_active"]) if "medium_source_active" in point_closure else pd.Series(True, index=point_closure.index)
    allowed = _bool_series(point_closure["covariant_exchange_allowed_mask"]) if "covariant_exchange_allowed_mask" in point_closure else pd.Series(True, index=point_closure.index)
    active_nonlive = active & (~live)
    allowed_nonlive = allowed & (~live)
    outside_nonlive = (~allowed) & (~live)

    endpoint_active = _sum_column(point_closure, active_nonlive, "endpoint_exchange_l2_density_volume")
    residual_active = _sum_column(point_closure, active_nonlive, "total_closure_residual_l2_density_volume")
    residual_allowed = _sum_column(point_closure, allowed_nonlive, "total_closure_residual_l2_density_volume")
    residual_outside = _sum_column(point_closure, outside_nonlive, "total_closure_residual_l2_density_volume")
    residual_live = _sum_column(point_closure, live, "total_closure_residual_l2_density_volume")
    source_volume = _source_abs_volume(point_closure, active_nonlive)
    normal_residual = _component_abs_volume(point_closure, active_nonlive, "total_closure_residual_0")
    radial_residual = _component_abs_volume(point_closure, active_nonlive, "total_closure_residual_1")
    angular_residual = (
        _component_abs_volume(point_closure, active_nonlive, "total_closure_residual_2")
        + _component_abs_volume(point_closure, active_nonlive, "total_closure_residual_3")
    )
    peak_residual = (
        float(point_closure.loc[active_nonlive, "total_closure_residual_l2_density"].astype(float).max())
        if len(point_closure.loc[active_nonlive]) and "total_closure_residual_l2_density" in point_closure
        else float("nan")
    )
    peak_source = (
        float(point_closure.loc[active_nonlive, "source_abs_density"].astype(float).max())
        if len(point_closure.loc[active_nonlive]) and "source_abs_density" in point_closure
        else float("nan")
    )
    return {
        "label": label,
        "active_source_abs_volume": source_volume,
        "active_endpoint_exchange_l2_volume": endpoint_active,
        "active_bianchi_driver_l2_volume": residual_active,
        "allowed_bianchi_driver_l2_volume": residual_allowed,
        "outside_bianchi_driver_l2_volume": residual_outside,
        "live_bianchi_driver_l2_volume": residual_live,
        "active_bianchi_driver_to_endpoint_ratio": _safe_ratio(residual_active, endpoint_active),
        "active_bianchi_driver_to_source_abs_ratio": _safe_ratio(residual_active, source_volume),
        "outside_driver_fraction_of_active_endpoint": _safe_ratio(residual_outside, endpoint_active),
        "live_driver_fraction_of_active_endpoint": _safe_ratio(residual_live, endpoint_active),
        "normal_driver_abs_volume": normal_residual,
        "radial_driver_abs_volume": radial_residual,
        "angular_driver_abs_volume": angular_residual,
        "hamiltonian_constraint_driver_proxy": 2.0 * PI8 * normal_residual,
        "momentum_constraint_driver_proxy": PI8 * radial_residual,
        "angular_momentum_driver_proxy": PI8 * angular_residual,
        "peak_active_bianchi_driver_density": peak_residual,
        "peak_active_source_abs_density": peak_source,
        "active_rows": int(active_nonlive.sum()),
        "allowed_rows": int(allowed_nonlive.sum()),
        "outside_rows": int(outside_nonlive.sum()),
        "live_rows": int(live.sum()),
    }


def _surface_summary(
    run: FirstOrder3P1RunSpec,
    *,
    covariant_decision: pd.DataFrame,
    closure_decision: pd.DataFrame,
    point_closure: pd.DataFrame,
) -> dict[str, Any]:
    cov = covariant_decision.iloc[0]
    closure = closure_decision.iloc[0]
    driver = _driver_summary(run.label, point_closure)
    return {
        **driver,
        "mesh": run.mesh,
        "surface_family": run.surface_family,
        "role": run.role,
        "covariant_identity_pass": _truth(cov["passes_covariant_identity_audit"]),
        "projection_reconstruction_pass": _truth(cov["projection_reconstruction_pass"]),
        "boost_subluminal_pass": _truth(cov["boost_subluminal_pass"]),
        "mixed_eigen_real_pass": _truth(cov["mixed_eigen_real_pass"]),
        "exchange_localization_pass": _truth(cov["exchange_localization_pass"]),
        "max_abs_boost_velocity": _finite(cov["max_abs_boost_velocity"], float("nan")),
        "outside_allowed_divergence_fraction": _finite(cov["outside_allowed_divergence_fraction"], float("nan")),
        "live_divergence_fraction": _finite(cov["live_divergence_fraction"], float("nan")),
        "peak_active_divergence_norm": _finite(cov["peak_active_divergence_norm"], float("nan")),
        "support_total_closure_pass": _truth(closure["passes_support_total_closure"]),
        "active_closure_residual_to_endpoint_l2_ratio": _finite(closure["active_closure_residual_to_endpoint_l2_ratio"], float("nan")),
        "allowed_closure_residual_to_endpoint_l2_ratio": _finite(closure["allowed_closure_residual_to_endpoint_l2_ratio"], float("nan")),
        "local_max_closure_residual_to_endpoint_l2_ratio": _finite(closure["local_max_closure_residual_to_endpoint_l2_ratio"], float("nan")),
        "active_closure_residual_to_target_abs_PF_ratio": _finite(closure["active_closure_residual_to_target_abs_PF_ratio"], float("nan")),
        "allowed_closure_residual_to_target_abs_PF_ratio": _finite(closure["allowed_closure_residual_to_target_abs_PF_ratio"], float("nan")),
        "local_max_closure_residual_to_target_abs_PF_ratio": _finite(closure["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan")),
        "outside_residual_fraction_of_full_endpoint": _finite(closure["outside_residual_fraction_of_full_endpoint"], float("nan")),
        "live_residual_fraction_of_full_endpoint": _finite(closure["live_residual_fraction_of_full_endpoint"], float("nan")),
        "outside_support_tail_fraction": _finite(closure["outside_support_tail_fraction"], float("nan")),
        "live_support_tail_fraction": _finite(closure["live_support_tail_fraction"], float("nan")),
        "full_total_closure_residual_angular_volume": _finite(closure["full_total_closure_residual_angular_volume"], float("nan")),
        "active_closure_l2_gate": _finite(closure["active_closure_l2_gate"], 0.55),
        "local_closure_l2_gate": _finite(closure["local_closure_l2_gate"], 0.55),
        "active_closure_pf_gate": _finite(closure["active_closure_pf_gate"], 0.50),
        "local_closure_pf_gate": _finite(closure["local_closure_pf_gate"], 0.55),
        "outside_residual_fraction_gate": _finite(closure["outside_residual_fraction_gate"], 0.006),
        "live_residual_fraction_gate": _finite(closure["live_residual_fraction_gate"], 0.005),
        "support_tail_fraction_gate": _finite(closure["support_tail_fraction_gate"], 0.001),
        "live_support_fraction_gate": _finite(closure["live_support_fraction_gate"], 0.0001),
        "angular_support_gate": _finite(closure["angular_support_gate"], 1.0e-14),
    }


def _surface_stability(surface_summary: pd.DataFrame) -> pd.DataFrame:
    reference = surface_summary.loc[surface_summary["role"].astype(str).eq("reference_dense")]
    if not len(reference):
        reference = surface_summary.head(1)
    ref = reference.iloc[0]
    rows: list[dict[str, Any]] = []
    for _, row in surface_summary.iterrows():
        rows.append({
            "label": str(row["label"]),
            "surface_family": str(row["surface_family"]),
            "role": str(row["role"]),
            "reference_label": str(ref["label"]),
            "active_driver_ratio_delta_from_reference": _finite(row["active_bianchi_driver_to_endpoint_ratio"], float("nan"))
            - _finite(ref["active_bianchi_driver_to_endpoint_ratio"], float("nan")),
            "local_pf_delta_from_reference": _finite(row["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan"))
            - _finite(ref["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan")),
            "live_residual_fraction_delta_from_reference": _finite(row["live_residual_fraction_of_full_endpoint"], float("nan"))
            - _finite(ref["live_residual_fraction_of_full_endpoint"], float("nan")),
            "outside_residual_fraction_delta_from_reference": _finite(row["outside_residual_fraction_of_full_endpoint"], float("nan"))
            - _finite(ref["outside_residual_fraction_of_full_endpoint"], float("nan")),
            "boost_delta_from_reference": _finite(row["max_abs_boost_velocity"], float("nan"))
            - _finite(ref["max_abs_boost_velocity"], float("nan")),
        })
    return pd.DataFrame(rows)


def _top_constraint_drivers(run: FirstOrder3P1RunSpec, point_closure: pd.DataFrame, *, top_n: int = 80) -> pd.DataFrame:
    frame = point_closure.copy()
    frame["label"] = run.label
    frame["surface_family"] = run.surface_family
    frame["role"] = run.role
    ordered = frame.sort_values("total_closure_residual_l2_density_volume", ascending=False).head(int(top_n))
    keep = [
        "label",
        "surface_family",
        "role",
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
        "total_closure_residual_0",
        "total_closure_residual_1",
        "total_closure_residual_2",
        "total_closure_residual_3",
        "source_abs_density",
    ]
    return ordered[[col for col in keep if col in ordered.columns]].reset_index(drop=True)


def _gate_row(gate: str, status: str, value: Any, gate_value: Any, read: str) -> dict[str, Any]:
    return {
        "gate": gate,
        "status": status,
        "value": value,
        "gate_value": gate_value,
        "read": read,
    }


def _coupling_gates(
    surface_summary: pd.DataFrame,
    surface_stability: pd.DataFrame,
    equation_decision: pd.DataFrame,
    energy_decision: pd.DataFrame,
    spec: FirstOrder3P1Spec,
) -> pd.DataFrame:
    eq = equation_decision.iloc[0]
    energy = energy_decision.iloc[0]
    max_active = float(surface_summary["active_closure_residual_to_endpoint_l2_ratio"].astype(float).max())
    max_active_gate = float(surface_summary["active_closure_l2_gate"].astype(float).min())
    max_local_pf = float(surface_summary["local_max_closure_residual_to_target_abs_PF_ratio"].astype(float).max())
    max_local_pf_gate = float(surface_summary["local_closure_pf_gate"].astype(float).min())
    max_outside = float(surface_summary["outside_residual_fraction_of_full_endpoint"].astype(float).max())
    max_outside_gate = float(surface_summary["outside_residual_fraction_gate"].astype(float).min())
    max_live = float(surface_summary["live_residual_fraction_of_full_endpoint"].astype(float).max())
    max_live_gate = float(surface_summary["live_residual_fraction_gate"].astype(float).min())
    max_support_tail = float(surface_summary["outside_support_tail_fraction"].astype(float).max())
    max_support_tail_gate = float(surface_summary["support_tail_fraction_gate"].astype(float).min())
    max_live_tail = float(surface_summary["live_support_tail_fraction"].astype(float).max())
    max_live_tail_gate = float(surface_summary["live_support_fraction_gate"].astype(float).min())
    max_angular = float(surface_summary["full_total_closure_residual_angular_volume"].astype(float).max())
    max_angular_gate = float(surface_summary["angular_support_gate"].astype(float).min())
    max_boost = float(surface_summary["max_abs_boost_velocity"].astype(float).max())
    adjacent = surface_stability.loc[surface_stability["role"].astype(str).eq("adjacent_service_surface")]
    adjacent_row = adjacent.iloc[0] if len(adjacent) else surface_stability.iloc[0]
    adjacent_stable = bool(
        abs(_finite(adjacent_row["active_driver_ratio_delta_from_reference"], float("nan"))) <= spec.adjacent_surface_drift_gate
        and abs(_finite(adjacent_row["local_pf_delta_from_reference"], float("nan"))) <= spec.adjacent_surface_drift_gate
        and abs(_finite(adjacent_row["boost_delta_from_reference"], float("nan"))) <= spec.adjacent_boost_drift_gate
    )
    covariant_hard = bool(
        surface_summary["covariant_identity_pass"].astype(bool).all()
        and surface_summary["projection_reconstruction_pass"].astype(bool).all()
        and surface_summary["boost_subluminal_pass"].astype(bool).all()
        and surface_summary["mixed_eigen_real_pass"].astype(bool).all()
    )
    closure_hard = bool(surface_summary["support_total_closure_pass"].astype(bool).all())
    return pd.DataFrame([
        _gate_row(
            "formal_source_family_equations",
            "pass" if _truth(eq["hard_equation_package_pass"]) else "fail",
            str(eq["formal_equation_status"]),
            "hard_equation_package_pass",
            "formal equations are present before entering the 3+1 coupling diagnostic",
        ),
        _gate_row(
            "covariant_endpoint_tensor_identity",
            "watch" if covariant_hard and max_boost > spec.boost_watch else "pass" if covariant_hard else "fail",
            max_boost,
            spec.boost_watch,
            "endpoint tensor identity, real eigenstructure, and subluminal boost carry into the coupled source handoff",
        ),
        _gate_row(
            "total_endpoint_support_bianchi_closure",
            "watch"
            if closure_hard and max_active > spec.active_constraint_driver_watch * max_active_gate
            else "pass"
            if closure_hard and max_active <= max_active_gate
            else "fail",
            max_active,
            max_active_gate,
            "endpoint plus support residual is the first-order Bianchi/constraint driver and stays below active closure gate",
        ),
        _gate_row(
            "local_constraint_driver_pf_closure",
            "watch"
            if max_local_pf <= max_local_pf_gate and max_local_pf > spec.local_closure_watch_fraction * max_local_pf_gate
            else "pass"
            if max_local_pf <= max_local_pf_gate
            else "fail",
            max_local_pf,
            max_local_pf_gate,
            "local P/F closure remains below hard gate but carries the reset-decompression margin watch",
        ),
        _gate_row(
            "offmask_and_live_constraint_driver_localization",
            "pass"
            if max_outside <= max_outside_gate
            and max_live <= max_live_gate
            and max_support_tail <= max_support_tail_gate
            and max_live_tail <= max_live_tail_gate
            else "fail",
            f"outside={max_outside:.12g}; live={max_live:.12g}; support_tail={max_support_tail:.12g}; live_tail={max_live_tail:.12g}",
            f"outside<={max_outside_gate}; live<={max_live_gate}; support_tail<={max_support_tail_gate}; live_tail<={max_live_tail_gate}",
            "constraint driver and support completion stay localized away from off-mask and live support leakage",
        ),
        _gate_row(
            "angular_constraint_driver_absence",
            "pass" if max_angular <= max_angular_gate else "fail",
            max_angular,
            max_angular_gate,
            "first-order handoff does not introduce angular support-exchange residue",
        ),
        _gate_row(
            "energy_constant_buffer_requirement",
            "watch"
            if _truth(energy["hard_constant_audit_pass"]) and _truth(energy["protective_buffer_watch"])
            else "pass"
            if _truth(energy["hard_constant_audit_pass"]) and not _truth(energy["protective_buffer_required_now"])
            else "fail",
            _finite(energy["work_utilization"], float("nan")),
            "protective_buffer_required_now=false",
            "energy constant is carried as safety-margin debt, not as an immediate buffer requirement",
        ),
        _gate_row(
            "adjacent_dense_surface_stability",
            "pass" if adjacent_stable else "fail",
            abs(_finite(adjacent_row["active_driver_ratio_delta_from_reference"], float("nan"))),
            spec.adjacent_surface_drift_gate,
            "lower-service dense surface does not amplify the first-order constraint-driver ratios",
        ),
        _gate_row(
            "available_3p1_entry_surface_scope",
            "pass" if len(surface_summary) >= spec.required_surface_count else "watch",
            int(len(surface_summary)),
            spec.required_surface_count,
            "entry diagnostic is scoped to the available complete surfaces",
        ),
    ])


def _decision(gates: pd.DataFrame, surface_summary: pd.DataFrame) -> pd.DataFrame:
    fail_count = int((gates["status"].astype(str) == "fail").sum())
    watch_count = int((gates["status"].astype(str) == "watch").sum())
    hard_pass = fail_count == 0
    worst_local = surface_summary.loc[int(surface_summary["local_max_closure_residual_to_target_abs_PF_ratio"].astype(float).idxmax())]
    worst_active = surface_summary.loc[int(surface_summary["active_closure_residual_to_endpoint_l2_ratio"].astype(float).idxmax())]
    status = (
        "first_order_3p1_entry_watch_pass"
        if hard_pass and watch_count
        else "first_order_3p1_entry_pass"
        if hard_pass
        else "first_order_3p1_entry_fail"
    )
    return pd.DataFrame([{
        "first_order_3p1_status": status,
        "hard_first_order_3p1_pass": hard_pass,
        "failed_gate_count": fail_count,
        "watch_count": watch_count,
        "surface_count": int(len(surface_summary)),
        "worst_local_pf_surface": str(worst_local["label"]),
        "worst_local_pf_ratio": _finite(worst_local["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan")),
        "worst_local_pf_gate": _finite(worst_local["local_closure_pf_gate"], float("nan")),
        "worst_active_driver_surface": str(worst_active["label"]),
        "worst_active_driver_ratio": _finite(worst_active["active_closure_residual_to_endpoint_l2_ratio"], float("nan")),
        "worst_active_driver_gate": _finite(worst_active["active_closure_l2_gate"], float("nan")),
        "max_live_driver_fraction": float(surface_summary["live_residual_fraction_of_full_endpoint"].astype(float).max()),
        "max_outside_driver_fraction": float(surface_summary["outside_residual_fraction_of_full_endpoint"].astype(float).max()),
        "max_abs_boost_velocity": float(surface_summary["max_abs_boost_velocity"].astype(float).max()),
        "decision_read": (
            "sealed beta075 source family has a hard-clean first-order 3+1 entry handoff; watches are margin constants, not constraint-accounting failures"
            if hard_pass and watch_count
            else "sealed beta075 source family has a hard-clean first-order 3+1 entry handoff without configured watches"
            if hard_pass
            else "sealed beta075 source family fails at least one first-order 3+1 entry handoff gate"
        ),
    }])


def build_first_order_3p1_coupling(
    inputs: FirstOrder3P1Inputs,
    *,
    spec: FirstOrder3P1Spec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or FirstOrder3P1Spec()
    equation_decision = _read_csv(inputs.equation_dir / "beta075_source_family_equation_decision.csv")
    energy_decision = _read_csv(inputs.energy_constant_dir / "beta075_source_family_energy_constant_decision.csv")
    surface_rows: list[dict[str, Any]] = []
    top_tables: list[pd.DataFrame] = []
    input_paths: dict[str, Path] = {
        "equation_decision": inputs.equation_dir / "beta075_source_family_equation_decision.csv",
        "energy_constant_decision": inputs.energy_constant_dir / "beta075_source_family_energy_constant_decision.csv",
    }
    run_manifest_rows: list[dict[str, Any]] = []
    for run in inputs.runs:
        cov_decision_path = run.covariant_dir / "endpoint_medium_covariant_decision.csv"
        closure_decision_path = run.total_closure_dir / "endpoint_support_total_closure_decision.csv"
        closure_point_path = run.total_closure_dir / "endpoint_support_total_closure_point_closure.csv"
        cov_manifest_path = run.covariant_dir / "endpoint_medium_covariant_manifest.json"
        closure_manifest_path = run.total_closure_dir / "endpoint_support_total_closure_manifest.json"
        covariant_decision = _read_csv(cov_decision_path)
        closure_decision = _read_csv(closure_decision_path)
        point_closure = _read_csv(closure_point_path)
        surface_rows.append(
            _surface_summary(
                run,
                covariant_decision=covariant_decision,
                closure_decision=closure_decision,
                point_closure=point_closure,
            )
        )
        top_tables.append(_top_constraint_drivers(run, point_closure))
        input_paths[f"{run.label}_covariant_decision"] = cov_decision_path
        input_paths[f"{run.label}_total_closure_decision"] = closure_decision_path
        input_paths[f"{run.label}_total_closure_point_closure"] = closure_point_path
        run_manifest_rows.append({
            "label": run.label,
            "mesh": run.mesh,
            "surface_family": run.surface_family,
            "role": run.role,
            "covariant_source_name": _read_json(cov_manifest_path).get("source_name", ""),
            "total_closure_source_name": _read_json(closure_manifest_path).get("source_name", ""),
            "covariant_dir": str(run.covariant_dir),
            "total_closure_dir": str(run.total_closure_dir),
        })

    surface_summary = pd.DataFrame(surface_rows)
    stability = _surface_stability(surface_summary)
    gates = _coupling_gates(surface_summary, stability, equation_decision, energy_decision, spec)
    decision = _decision(gates, surface_summary)
    top_drivers = pd.concat(top_tables, ignore_index=True) if top_tables else pd.DataFrame()
    outputs = {
        "run_manifest": pd.DataFrame(run_manifest_rows),
        "surface_summary": surface_summary,
        "surface_stability": stability,
        "classification_gates": gates,
        "top_constraint_drivers": top_drivers,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_first_order_3p1_coupling",
        "spec": spec.__dict__,
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "claim_boundary": (
            "First-order 3+1/backreaction entry diagnostic. The total endpoint-plus-support divergence "
            "is treated as the perturbative Bianchi/constraint driver. This is not a full dynamical "
            "metric evolution or off-axis 3+1 solve."
        ),
    }
    return outputs, metadata


def write_first_order_3p1_coupling_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "run_manifest": outdir / "beta075_first_order_3p1_run_manifest.csv",
        "surface_summary": outdir / "beta075_first_order_3p1_surface_summary.csv",
        "surface_stability": outdir / "beta075_first_order_3p1_surface_stability.csv",
        "classification_gates": outdir / "beta075_first_order_3p1_classification_gates.csv",
        "top_constraint_drivers": outdir / "beta075_first_order_3p1_top_constraint_drivers.csv",
        "decision": outdir / "beta075_first_order_3p1_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_first_order_3p1_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
