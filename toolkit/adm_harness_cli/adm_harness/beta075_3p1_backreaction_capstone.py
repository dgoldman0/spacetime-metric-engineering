from __future__ import annotations

import json
import math
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .beta075_first_order_3p1_coupling import FirstOrder3P1RunSpec, default_first_order_3p1_runs
from .source_ledger import PI8, sha256_file, write_manifest


EPS = 1.0e-30


@dataclass(frozen=True)
class BackreactionScenarioSpec:
    scenario_id: str
    angular_mode: int
    offaxis_fraction: float
    metric_feedback_gain: float
    boost_margin_fraction: float
    read: str


def default_backreaction_scenarios() -> tuple[BackreactionScenarioSpec, ...]:
    return (
        BackreactionScenarioSpec(
            "axisymmetric_reference",
            0,
            0.0,
            0.0,
            0.0,
            "base first-order handoff with no off-axis or metric-feedback stress",
        ),
        BackreactionScenarioSpec(
            "m1_tilt_response",
            1,
            0.025,
            0.025,
            0.08,
            "dipole-like off-axis tilt with mild geometric feedback",
        ),
        BackreactionScenarioSpec(
            "m2_shear_response",
            2,
            0.035,
            0.035,
            0.12,
            "quadrupole-like shear response against the support reservoir",
        ),
        BackreactionScenarioSpec(
            "reset_sector_feedback",
            0,
            0.0,
            0.055,
            0.16,
            "axisymmetric geometric-feedback stress focused on the reset-sector margin",
        ),
        BackreactionScenarioSpec(
            "combined_offaxis_feedback",
            2,
            0.045,
            0.055,
            0.18,
            "combined off-axis and metric-feedback capstone stress",
        ),
    )


@dataclass(frozen=True)
class BackreactionCapstoneInputs:
    first_order_dir: Path
    energy_constant_dir: Path
    runs: tuple[FirstOrder3P1RunSpec, ...] = field(default_factory=default_first_order_3p1_runs)
    scenarios: tuple[BackreactionScenarioSpec, ...] = field(default_factory=default_backreaction_scenarios)


@dataclass(frozen=True)
class BackreactionCapstoneSpec:
    active_driver_gate: float = 0.55
    local_pf_gate: float = 0.55
    live_driver_fraction_gate: float = 0.005
    outside_driver_fraction_gate: float = 0.006
    support_tail_fraction_gate: float = 0.001
    live_support_tail_fraction_gate: float = 0.0001
    angular_driver_fraction_gate: float = 0.12
    cone_margin_gate: float = 0.0
    cone_margin_watch: float = 0.02
    adjacent_driver_drift_gate: float = 0.03
    required_surface_count: int = 3
    top_rows_per_surface_scenario: int = 80
    workers: int = 6


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


def _scenario_catalog(scenarios: tuple[BackreactionScenarioSpec, ...]) -> pd.DataFrame:
    return pd.DataFrame([scenario.__dict__ for scenario in scenarios])


def _base_masks(point: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    live = _bool_series(point["covariant_divergence_live"]) if "covariant_divergence_live" in point else pd.Series(False, index=point.index)
    active = _bool_series(point["medium_source_active"]) if "medium_source_active" in point else pd.Series(True, index=point.index)
    allowed = _bool_series(point["covariant_exchange_allowed_mask"]) if "covariant_exchange_allowed_mask" in point else pd.Series(True, index=point.index)
    return active & (~live), allowed & (~live), (~allowed) & (~live), live


def _sum(frame: pd.DataFrame, mask: pd.Series, column: str) -> float:
    if column not in frame:
        return 0.0
    return float(frame.loc[mask, column].fillna(0.0).astype(float).sum())


def _scenario_factor(scenario: BackreactionScenarioSpec, energy_utilization: float) -> float:
    return float(1.0 + scenario.offaxis_fraction + scenario.metric_feedback_gain * energy_utilization)


def _build_surface_scenarios(
    run: FirstOrder3P1RunSpec,
    scenarios: tuple[BackreactionScenarioSpec, ...],
    energy_utilization: float,
    top_rows_per_surface_scenario: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, str]]:
    point_path = run.total_closure_dir / "endpoint_support_total_closure_point_closure.csv"
    closure_decision_path = run.total_closure_dir / "endpoint_support_total_closure_decision.csv"
    covariant_decision_path = run.covariant_dir / "endpoint_medium_covariant_decision.csv"
    point = _read_csv(point_path)
    closure = _read_csv(closure_decision_path).iloc[0]
    covariant = _read_csv(covariant_decision_path).iloc[0]
    active, allowed, outside, live = _base_masks(point)

    base_keep = [
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
        "endpoint_exchange_l2_density_volume",
        "candidate_support_l2_density",
        "total_closure_residual_l2_density",
        "total_closure_residual_l2_density_volume",
        "total_closure_residual_0",
        "total_closure_residual_1",
        "total_closure_residual_2",
        "total_closure_residual_3",
        "source_abs_density",
        "medium_frame_abs_boost_velocity",
    ]
    base = point[[col for col in base_keep if col in point.columns]].copy()
    if "medium_frame_abs_boost_velocity" not in base:
        base["medium_frame_abs_boost_velocity"] = _finite(covariant["max_abs_boost_velocity"], 0.0)

    response_tables: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    top_tables: list[pd.DataFrame] = []
    endpoint_active = _sum(point, active, "endpoint_exchange_l2_density_volume")
    source_active = _sum(point, active, "source_abs_volume")
    if source_active <= 0.0 and "source_abs_density" in point:
        source_active = float((point.loc[active, "source_abs_density"].fillna(0.0).astype(float) * point.loc[active, "volume_weight"].fillna(1.0).astype(float)).sum()) if "volume_weight" in point else float(point.loc[active, "source_abs_density"].fillna(0.0).astype(float).sum())

    for scenario in scenarios:
        factor = _scenario_factor(scenario, energy_utilization)
        response = base.copy()
        response["label"] = run.label
        response["mesh"] = run.mesh
        response["surface_family"] = run.surface_family
        response["role"] = run.role
        response["scenario_id"] = scenario.scenario_id
        response["angular_mode"] = scenario.angular_mode
        response["response_factor"] = factor
        response["scenario_driver_l2_density"] = response["total_closure_residual_l2_density"].fillna(0.0).astype(float) * factor
        response["scenario_driver_l2_volume"] = response["total_closure_residual_l2_density_volume"].fillna(0.0).astype(float) * factor
        response["scenario_normal_driver_volume"] = response["total_closure_residual_0"].fillna(0.0).astype(float).abs()
        response["scenario_radial_driver_volume"] = response["total_closure_residual_1"].fillna(0.0).astype(float).abs()
        response["scenario_offaxis_angular_driver_volume"] = (
            response["scenario_driver_l2_volume"].astype(float) * scenario.offaxis_fraction
        )
        boost = response["medium_frame_abs_boost_velocity"].fillna(0.0).astype(float)
        response["scenario_boost_velocity_proxy"] = boost + scenario.boost_margin_fraction * (1.0 - boost)
        response["scenario_cone_margin_proxy"] = 1.0 - response["scenario_boost_velocity_proxy"].astype(float)

        active_driver = _sum(response, active, "scenario_driver_l2_volume")
        allowed_driver = _sum(response, allowed, "scenario_driver_l2_volume")
        outside_driver = _sum(response, outside, "scenario_driver_l2_volume")
        live_driver = _sum(response, live, "scenario_driver_l2_volume")
        full_endpoint = _sum(response, pd.Series(True, index=response.index), "endpoint_exchange_l2_density_volume")
        angular_driver = _sum(response, active, "scenario_offaxis_angular_driver_volume")
        summary_rows.append({
            "label": run.label,
            "mesh": run.mesh,
            "surface_family": run.surface_family,
            "role": run.role,
            "scenario_id": scenario.scenario_id,
            "angular_mode": scenario.angular_mode,
            "response_factor": factor,
            "active_driver_l2_volume": active_driver,
            "allowed_driver_l2_volume": allowed_driver,
            "outside_driver_l2_volume": outside_driver,
            "live_driver_l2_volume": live_driver,
            "active_endpoint_exchange_l2_volume": endpoint_active,
            "active_source_abs_volume": source_active,
            "active_driver_to_endpoint_ratio": active_driver / (endpoint_active + EPS),
            "active_driver_to_source_abs_ratio": active_driver / (source_active + EPS),
            "full_endpoint_exchange_l2_volume": full_endpoint,
            "outside_driver_fraction_of_full_endpoint": outside_driver / (full_endpoint + EPS),
            "live_driver_fraction_of_full_endpoint": live_driver / (full_endpoint + EPS),
            "offaxis_angular_driver_fraction": angular_driver / (active_driver + EPS),
            "max_scenario_boost_velocity": float(response["scenario_boost_velocity_proxy"].astype(float).max()),
            "min_scenario_cone_margin": float(response["scenario_cone_margin_proxy"].astype(float).min()),
            "peak_scenario_driver_density": float(response.loc[active, "scenario_driver_l2_density"].astype(float).max()) if int(active.sum()) else float("nan"),
            "hamiltonian_constraint_proxy_volume": 2.0 * PI8 * float(response.loc[active, "total_closure_residual_0"].fillna(0.0).astype(float).abs().sum()),
            "momentum_constraint_proxy_volume": PI8 * float(response.loc[active, "total_closure_residual_1"].fillna(0.0).astype(float).abs().sum()),
            "inherited_local_pf_ratio": _finite(closure["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan")),
            "inherited_active_closure_ratio": _finite(closure["active_closure_residual_to_endpoint_l2_ratio"], float("nan")),
            "inherited_live_support_tail_fraction": _finite(closure["live_support_tail_fraction"], float("nan")),
            "inherited_outside_support_tail_fraction": _finite(closure["outside_support_tail_fraction"], float("nan")),
            "inherited_max_boost_velocity": _finite(covariant["max_abs_boost_velocity"], float("nan")),
        })
        top = response.sort_values("scenario_driver_l2_volume", ascending=False).head(int(top_rows_per_surface_scenario))
        top_tables.append(top.reset_index(drop=True))
        response_tables.append(response.reset_index(drop=True))

    paths = {
        "point_closure": str(point_path),
        "closure_decision": str(closure_decision_path),
        "covariant_decision": str(covariant_decision_path),
    }
    return (
        pd.concat(response_tables, ignore_index=True),
        pd.DataFrame(summary_rows),
        pd.concat(top_tables, ignore_index=True),
        paths,
    )


def _surface_worker(args: tuple[FirstOrder3P1RunSpec, tuple[BackreactionScenarioSpec, ...], float, int]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, str]]:
    return _build_surface_scenarios(*args)


def _stability(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for scenario_id, group in summary.groupby("scenario_id", sort=False):
        ref = group.loc[group["role"].astype(str).eq("reference_dense")]
        if not len(ref):
            ref = group.head(1)
        ref_row = ref.iloc[0]
        for _, row in group.iterrows():
            rows.append({
                "scenario_id": str(scenario_id),
                "label": str(row["label"]),
                "surface_family": str(row["surface_family"]),
                "role": str(row["role"]),
                "reference_label": str(ref_row["label"]),
                "active_driver_ratio_delta_from_reference": _finite(row["active_driver_to_endpoint_ratio"], float("nan"))
                - _finite(ref_row["active_driver_to_endpoint_ratio"], float("nan")),
                "cone_margin_delta_from_reference": _finite(row["min_scenario_cone_margin"], float("nan"))
                - _finite(ref_row["min_scenario_cone_margin"], float("nan")),
                "boost_delta_from_reference": _finite(row["max_scenario_boost_velocity"], float("nan"))
                - _finite(ref_row["max_scenario_boost_velocity"], float("nan")),
            })
    return pd.DataFrame(rows)


def _gates(
    summary: pd.DataFrame,
    stability: pd.DataFrame,
    first_order_decision: pd.DataFrame,
    energy_decision: pd.DataFrame,
    spec: BackreactionCapstoneSpec,
) -> pd.DataFrame:
    first = first_order_decision.iloc[0]
    energy = energy_decision.iloc[0]
    max_active = float(summary["active_driver_to_endpoint_ratio"].astype(float).max())
    max_local_pf = float(summary["inherited_local_pf_ratio"].astype(float).max())
    max_live = float(summary["live_driver_fraction_of_full_endpoint"].astype(float).max())
    max_outside = float(summary["outside_driver_fraction_of_full_endpoint"].astype(float).max())
    max_support_tail = float(summary["inherited_outside_support_tail_fraction"].astype(float).max())
    max_live_tail = float(summary["inherited_live_support_tail_fraction"].astype(float).max())
    max_angular_fraction = float(summary["offaxis_angular_driver_fraction"].astype(float).max())
    min_cone_margin = float(summary["min_scenario_cone_margin"].astype(float).min())
    adjacent = stability.loc[stability["role"].astype(str).eq("adjacent_service_surface")]
    max_adjacent_drift = float(adjacent["active_driver_ratio_delta_from_reference"].astype(float).abs().max()) if len(adjacent) else float("inf")
    rows = [
        {
            "gate": "first_order_3p1_handoff",
            "status": "pass" if _truth(first["hard_first_order_3p1_pass"]) else "fail",
            "value": str(first["first_order_3p1_status"]),
            "gate_value": "hard_first_order_3p1_pass",
            "read": "capstone inherits a hard-clean first-order Bianchi/constraint handoff",
        },
        {
            "gate": "scenario_active_driver_bound",
            "status": "watch" if max_active <= spec.active_driver_gate and max_active > 0.90 * spec.active_driver_gate else "pass" if max_active <= spec.active_driver_gate else "fail",
            "value": max_active,
            "gate_value": spec.active_driver_gate,
            "read": "off-axis and metric-feedback scenarios keep the active constraint driver below gate",
        },
        {
            "gate": "scenario_cone_margin_proxy",
            "status": "watch" if min_cone_margin > spec.cone_margin_gate and min_cone_margin < spec.cone_margin_watch else "pass" if min_cone_margin > spec.cone_margin_gate else "fail",
            "value": min_cone_margin,
            "gate_value": spec.cone_margin_gate,
            "read": "metric-response boost proxy remains subluminal but carries thin margin",
        },
        {
            "gate": "offaxis_angular_driver_bound",
            "status": "pass" if max_angular_fraction <= spec.angular_driver_fraction_gate else "fail",
            "value": max_angular_fraction,
            "gate_value": spec.angular_driver_fraction_gate,
            "read": "synthetic off-axis angular driver remains a small fraction of active driver",
        },
        {
            "gate": "live_and_offmask_driver_localization",
            "status": "pass"
            if max_live <= spec.live_driver_fraction_gate
            and max_outside <= spec.outside_driver_fraction_gate
            and max_support_tail <= spec.support_tail_fraction_gate
            and max_live_tail <= spec.live_support_tail_fraction_gate
            else "fail",
            "value": f"live={max_live:.12g}; outside={max_outside:.12g}; support_tail={max_support_tail:.12g}; live_tail={max_live_tail:.12g}",
            "gate_value": f"live<={spec.live_driver_fraction_gate}; outside<={spec.outside_driver_fraction_gate}; support_tail<={spec.support_tail_fraction_gate}; live_tail<={spec.live_support_tail_fraction_gate}",
            "read": "backreaction stress does not buy margin through live or off-mask support leakage",
        },
        {
            "gate": "inherited_reset_sector_pf_margin",
            "status": "watch" if max_local_pf <= spec.local_pf_gate and max_local_pf > 0.90 * spec.local_pf_gate else "pass" if max_local_pf <= spec.local_pf_gate else "fail",
            "value": max_local_pf,
            "gate_value": spec.local_pf_gate,
            "read": "reset-sector P/F closure remains the tight inherited local watch",
        },
        {
            "gate": "adjacent_dense_surface_stability",
            "status": "pass" if max_adjacent_drift <= spec.adjacent_driver_drift_gate else "fail",
            "value": max_adjacent_drift,
            "gate_value": spec.adjacent_driver_drift_gate,
            "read": "lower-service dense surface does not materially amplify capstone drivers",
        },
        {
            "gate": "energy_constant_buffer_requirement",
            "status": "watch" if _truth(energy["hard_constant_audit_pass"]) and _truth(energy["protective_buffer_watch"]) else "pass" if _truth(energy["hard_constant_audit_pass"]) else "fail",
            "value": _finite(energy["work_utilization"], float("nan")),
            "gate_value": "protective_buffer_required_now=false",
            "read": "energy theorem constant remains a watch, not a required protective buffer",
        },
        {
            "gate": "capstone_surface_scope",
            "status": "pass" if int(summary["label"].nunique()) >= spec.required_surface_count else "watch",
            "value": int(summary["label"].nunique()),
            "gate_value": spec.required_surface_count,
            "read": "capstone covers the available complete baseline/dense/lower-service surfaces",
        },
    ]
    return pd.DataFrame(rows)


def _decision(gates: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    fail_count = int((gates["status"].astype(str) == "fail").sum())
    watch_count = int((gates["status"].astype(str) == "watch").sum())
    hard_pass = fail_count == 0
    worst_active = summary.loc[int(summary["active_driver_to_endpoint_ratio"].astype(float).idxmax())]
    worst_cone = summary.loc[int(summary["min_scenario_cone_margin"].astype(float).idxmin())]
    status = (
        "stage2_3p1_backreaction_capstone_watch_pass"
        if hard_pass and watch_count
        else "stage2_3p1_backreaction_capstone_pass"
        if hard_pass
        else "stage2_3p1_backreaction_capstone_fail"
    )
    return pd.DataFrame([{
        "capstone_status": status,
        "hard_capstone_pass": hard_pass,
        "failed_gate_count": fail_count,
        "watch_count": watch_count,
        "surface_count": int(summary["label"].nunique()),
        "scenario_count": int(summary["scenario_id"].nunique()),
        "worst_active_driver_surface": str(worst_active["label"]),
        "worst_active_driver_scenario": str(worst_active["scenario_id"]),
        "worst_active_driver_ratio": _finite(worst_active["active_driver_to_endpoint_ratio"], float("nan")),
        "worst_cone_surface": str(worst_cone["label"]),
        "worst_cone_scenario": str(worst_cone["scenario_id"]),
        "min_cone_margin_proxy": _finite(worst_cone["min_scenario_cone_margin"], float("nan")),
        "max_offaxis_angular_driver_fraction": float(summary["offaxis_angular_driver_fraction"].astype(float).max()),
        "decision_read": (
            "local-compute 3+1/backreaction capstone is hard-clean with inherited margin watches"
            if hard_pass and watch_count
            else "local-compute 3+1/backreaction capstone is hard-clean without configured watches"
            if hard_pass
            else "local-compute 3+1/backreaction capstone finds at least one hard obstruction"
        ),
    }])


def build_backreaction_capstone(
    inputs: BackreactionCapstoneInputs,
    *,
    spec: BackreactionCapstoneSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or BackreactionCapstoneSpec()
    first_order_decision = _read_csv(inputs.first_order_dir / "beta075_first_order_3p1_decision.csv")
    energy_decision = _read_csv(inputs.energy_constant_dir / "beta075_source_family_energy_constant_decision.csv")
    energy_utilization = _finite(energy_decision.iloc[0]["work_utilization"], 0.0)
    tasks = [
        (run, inputs.scenarios, energy_utilization, spec.top_rows_per_surface_scenario)
        for run in inputs.runs
    ]
    workers = max(1, min(int(spec.workers), len(tasks)))
    if workers == 1:
        results = [_surface_worker(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_surface_worker, tasks))

    point_response = pd.concat([item[0] for item in results], ignore_index=True)
    scenario_summary = pd.concat([item[1] for item in results], ignore_index=True)
    top_drivers = pd.concat([item[2] for item in results], ignore_index=True)
    input_paths: dict[str, Path] = {
        "first_order_decision": inputs.first_order_dir / "beta075_first_order_3p1_decision.csv",
        "energy_constant_decision": inputs.energy_constant_dir / "beta075_source_family_energy_constant_decision.csv",
    }
    for _point_response, _summary, _top, paths in results:
        for key, value in paths.items():
            input_paths[value] = Path(value)
    stability = _stability(scenario_summary)
    gates = _gates(scenario_summary, stability, first_order_decision, energy_decision, spec)
    decision = _decision(gates, scenario_summary)
    outputs = {
        "scenario_catalog": _scenario_catalog(inputs.scenarios),
        "scenario_summary": scenario_summary,
        "surface_stability": stability,
        "classification_gates": gates,
        "point_response": point_response,
        "top_constraint_drivers": top_drivers,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_3p1_backreaction_capstone",
        "spec": spec.__dict__,
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "storage": "heavy point/scenario outputs are parquet; summary and decision outputs are csv/json",
        "claim_boundary": (
            "Local-compute Stage II 3+1/backreaction capstone. This is an off-axis and metric-feedback "
            "stress diagnostic over existing complete surfaces, not a full dynamical Einstein-matter solve."
        ),
    }
    return outputs, metadata


def write_backreaction_capstone_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    csv_paths = {
        "scenario_catalog": outdir / "beta075_3p1_backreaction_scenario_catalog.csv",
        "scenario_summary": outdir / "beta075_3p1_backreaction_scenario_summary.csv",
        "surface_stability": outdir / "beta075_3p1_backreaction_surface_stability.csv",
        "classification_gates": outdir / "beta075_3p1_backreaction_classification_gates.csv",
        "decision": outdir / "beta075_3p1_backreaction_decision.csv",
    }
    parquet_paths = {
        "point_response": outdir / "beta075_3p1_backreaction_point_response.parquet",
        "top_constraint_drivers": outdir / "beta075_3p1_backreaction_top_constraint_drivers.parquet",
    }
    for key, path in csv_paths.items():
        outputs[key].to_csv(path, index=False)
    for key, path in parquet_paths.items():
        outputs[key].to_parquet(path, index=False, compression="zstd")
    paths = {**csv_paths, **parquet_paths}
    manifest_path = outdir / "beta075_3p1_backreaction_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
