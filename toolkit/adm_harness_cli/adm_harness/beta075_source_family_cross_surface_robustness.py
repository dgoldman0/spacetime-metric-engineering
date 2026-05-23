from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from .beta075_source_family_validation import (
    SourceFamilyValidationInputs,
    SourceFamilyValidationRun,
    SourceFamilyValidationSpec,
    build_source_family_validation,
)
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class CrossSurfaceRunSpec:
    label: str
    mesh: str
    surface_family: str
    role: str
    stroke_dir: Path
    total_closure_dir: Path


def default_cross_surface_runs() -> tuple[CrossSurfaceRunSpec, ...]:
    baseline_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15")
    dense_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12")
    v2_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_v2_dense377x241")
    return (
        CrossSurfaceRunSpec(
            "sealed_baseline_v5",
            "baseline",
            "sealed_beta075_v5",
            "reference_baseline",
            baseline_root / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
            baseline_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
        CrossSurfaceRunSpec(
            "sealed_dense_v5",
            "dense",
            "sealed_beta075_v5",
            "reference_dense",
            dense_root / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
            dense_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
        CrossSurfaceRunSpec(
            "lower_service_dense_v2",
            "dense_v2",
            "lower_service_beta075_v2",
            "adjacent_service_surface",
            v2_root / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
            v2_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
    )


@dataclass(frozen=True)
class CrossSurfaceRobustnessInputs:
    equation_dir: Path
    principal_symbol_dir: Path
    runs: tuple[CrossSurfaceRunSpec, ...] = field(default_factory=default_cross_surface_runs)


@dataclass(frozen=True)
class CrossSurfaceRobustnessSpec:
    validation_spec: SourceFamilyValidationSpec = field(default_factory=SourceFamilyValidationSpec)
    cone_margin_relative_drift_watch: float = 0.35
    exchange_absolute_drift_watch: float = 0.05
    total_closure_absolute_drift_watch: float = 0.03


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


def _validation_runs(runs: tuple[CrossSurfaceRunSpec, ...]) -> tuple[SourceFamilyValidationRun, ...]:
    return tuple(
        SourceFamilyValidationRun(
            label=run.label,
            mesh=run.mesh,
            stroke_dir=run.stroke_dir,
            total_closure_dir=run.total_closure_dir,
        )
        for run in runs
    )


def _run_role_frame(runs: tuple[CrossSurfaceRunSpec, ...]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "label": run.label,
            "mesh": run.mesh,
            "surface_family": run.surface_family,
            "role": run.role,
            "stroke_dir": str(run.stroke_dir),
            "total_closure_dir": str(run.total_closure_dir),
        }
        for run in runs
    ])


def _augment_run_summary(run_summary: pd.DataFrame, run_roles: pd.DataFrame) -> pd.DataFrame:
    return run_summary.merge(
        run_roles[["label", "surface_family", "role"]],
        on="label",
        how="left",
    )


def _surface_delta(run_summary: pd.DataFrame) -> pd.DataFrame:
    reference = run_summary.loc[run_summary["role"].astype(str).eq("reference_dense")]
    if not len(reference):
        reference = run_summary.head(1)
    ref = reference.iloc[0]
    ref_margin = _finite(ref["min_relative_cone_margin"], float("nan"))
    ref_p = _finite(ref["max_local_P_error"], float("nan"))
    ref_f = _finite(ref["max_local_F_error"], float("nan"))
    ref_total = _finite(ref["support_total_local_pf_ratio"], float("nan"))
    rows: list[dict[str, Any]] = []
    for _, row in run_summary.iterrows():
        margin = _finite(row["min_relative_cone_margin"], float("nan"))
        p_error = _finite(row["max_local_P_error"], float("nan"))
        f_error = _finite(row["max_local_F_error"], float("nan"))
        total = _finite(row["support_total_local_pf_ratio"], float("nan"))
        rows.append({
            "label": str(row["label"]),
            "surface_family": str(row.get("surface_family", "")),
            "role": str(row.get("role", "")),
            "reference_label": str(ref["label"]),
            "min_relative_cone_margin": margin,
            "cone_margin_delta_from_reference": margin - ref_margin,
            "cone_margin_relative_drop_from_reference": (ref_margin - margin) / ref_margin if ref_margin > 0.0 else float("nan"),
            "max_local_P_error": p_error,
            "max_local_P_error_delta_from_reference": p_error - ref_p,
            "max_local_F_error": f_error,
            "max_local_F_error_delta_from_reference": f_error - ref_f,
            "support_total_local_pf_ratio": total,
            "support_total_local_pf_delta_from_reference": total - ref_total,
        })
    return pd.DataFrame(rows)


def _cross_surface_gates(
    run_summary: pd.DataFrame,
    delta: pd.DataFrame,
    spec: CrossSurfaceRobustnessSpec,
) -> pd.DataFrame:
    val_spec = spec.validation_spec
    min_margin = float(run_summary["min_relative_cone_margin"].astype(float).min()) if len(run_summary) else float("nan")
    max_p = float(run_summary["max_local_P_error"].astype(float).max()) if len(run_summary) else float("nan")
    max_f = float(run_summary["max_local_F_error"].astype(float).max()) if len(run_summary) else float("nan")
    max_component = max(max_p, max_f)
    max_total = float(run_summary["support_total_local_pf_ratio"].astype(float).max()) if len(run_summary) else float("nan")
    min_total_gate = float(run_summary["support_total_local_pf_gate"].astype(float).min()) if len(run_summary) else float("nan")
    fail_rows = int(run_summary["fail_rows"].astype(int).sum()) if len(run_summary) else 1
    hard_passes = bool(run_summary["hard_formal_symbol_pass"].astype(bool).all()) if len(run_summary) else False
    margin_drop = float(delta["cone_margin_relative_drop_from_reference"].astype(float).max()) if len(delta) else float("nan")
    p_drift = float(delta["max_local_P_error_delta_from_reference"].astype(float).max()) if len(delta) else float("nan")
    f_drift = float(delta["max_local_F_error_delta_from_reference"].astype(float).max()) if len(delta) else float("nan")
    total_drift = float(delta["support_total_local_pf_delta_from_reference"].astype(float).max()) if len(delta) else float("nan")
    drift_watch = bool(
        (math.isfinite(margin_drop) and margin_drop > spec.cone_margin_relative_drift_watch)
        or (math.isfinite(p_drift) and p_drift > spec.exchange_absolute_drift_watch)
        or (math.isfinite(f_drift) and f_drift > spec.exchange_absolute_drift_watch)
        or (math.isfinite(total_drift) and total_drift > spec.total_closure_absolute_drift_watch)
    )
    component_status = (
        "fail"
        if max_component > val_spec.local_pf_component_fail
        else "watch"
        if max_component > val_spec.local_pf_component_watch
        else "pass"
    )
    total_status = (
        "fail"
        if max_total > min_total_gate
        else "watch"
        if max_total > val_spec.local_total_closure_watch_fraction * min_total_gate
        else "pass"
    )
    margin_status = (
        "fail"
        if min_margin < val_spec.speed_margin_gate
        else "watch"
        if min_margin < val_spec.speed_margin_watch
        else "pass"
    )
    return pd.DataFrame([
        {
            "gate": "all_surfaces_hard_symbol",
            "status": "pass" if hard_passes and fail_rows == 0 else "fail",
            "value": fail_rows,
            "gate_value": 0,
            "read": "every available surface keeps hard formal-symbol gates clean",
        },
        {
            "gate": "cross_surface_cone_margin",
            "status": margin_status,
            "value": min_margin,
            "gate_value": val_spec.speed_margin_gate,
            "read": "minimum cone margin across surfaces remains inside the service cone",
        },
        {
            "gate": "cross_surface_local_exchange_shape",
            "status": component_status,
            "value": max_component,
            "gate_value": val_spec.local_pf_component_fail,
            "read": "local P/F exchange shape remains bounded across surfaces",
        },
        {
            "gate": "cross_surface_total_support_closure",
            "status": total_status,
            "value": max_total,
            "gate_value": min_total_gate,
            "read": "total support tensor closure remains below local gate across surfaces",
        },
        {
            "gate": "cross_surface_drift",
            "status": "watch" if drift_watch else "pass",
            "value": max(
                value
                for value in [margin_drop, p_drift, f_drift, total_drift]
                if math.isfinite(value)
            ),
            "gate_value": max(
                spec.cone_margin_relative_drift_watch,
                spec.exchange_absolute_drift_watch,
                spec.total_closure_absolute_drift_watch,
            ),
            "read": "adjacent surfaces do not introduce a new hard drift in cone, exchange, or support closure",
        },
        {
            "gate": "available_surface_scope",
            "status": "pass" if len(run_summary) >= 3 else "watch",
            "value": int(len(run_summary)),
            "gate_value": 3,
            "read": "scope is sealed baseline/dense plus available lower-service dense surface, not broad beta/V coverage",
        },
    ])


def _decision(gates: pd.DataFrame, run_summary: pd.DataFrame) -> pd.DataFrame:
    fail_count = int((gates["status"].astype(str) == "fail").sum())
    watch_count = int((gates["status"].astype(str) == "watch").sum())
    hard_pass = fail_count == 0
    worst_margin_idx = int(run_summary["min_relative_cone_margin"].astype(float).idxmin())
    worst_exchange_idx = int(
        run_summary[["max_local_P_error", "max_local_F_error"]]
        .astype(float)
        .max(axis=1)
        .idxmax()
    )
    worst_closure_idx = int(run_summary["support_total_local_pf_ratio"].astype(float).idxmax())
    worst_margin = run_summary.loc[worst_margin_idx]
    worst_exchange = run_summary.loc[worst_exchange_idx]
    worst_closure = run_summary.loc[worst_closure_idx]
    status = (
        "cross_surface_source_family_robustness_watch_pass"
        if hard_pass and watch_count
        else "cross_surface_source_family_robustness_pass"
        if hard_pass
        else "cross_surface_source_family_robustness_fail"
    )
    return pd.DataFrame([{
        "cross_surface_robustness_status": status,
        "hard_cross_surface_pass": hard_pass,
        "failed_gate_count": fail_count,
        "watch_count": watch_count,
        "surface_count": int(len(run_summary)),
        "worst_margin_surface": str(worst_margin["label"]),
        "worst_margin_value": _finite(worst_margin["min_relative_cone_margin"], float("nan")),
        "worst_exchange_surface": str(worst_exchange["label"]),
        "worst_exchange_value": max(
            _finite(worst_exchange["max_local_P_error"], float("nan")),
            _finite(worst_exchange["max_local_F_error"], float("nan")),
        ),
        "worst_total_closure_surface": str(worst_closure["label"]),
        "worst_total_closure_value": _finite(worst_closure["support_total_local_pf_ratio"], float("nan")),
        "decision_read": (
            "formal source-family validation survives available cross-surface checks with watch-level margin debt"
            if hard_pass and watch_count
            else "formal source-family validation clears available cross-surface checks without configured watches"
            if hard_pass
            else "formal source-family validation fails on at least one available cross-surface gate"
        ),
    }])


def build_cross_surface_robustness(
    inputs: CrossSurfaceRobustnessInputs,
    *,
    spec: CrossSurfaceRobustnessSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or CrossSurfaceRobustnessSpec()
    validation_inputs = SourceFamilyValidationInputs(
        equation_dir=inputs.equation_dir,
        principal_symbol_dir=inputs.principal_symbol_dir,
        runs=_validation_runs(inputs.runs),
    )
    validation_outputs, validation_metadata = build_source_family_validation(
        validation_inputs,
        spec=spec.validation_spec,
    )
    run_roles = _run_role_frame(inputs.runs)
    run_summary = _augment_run_summary(validation_outputs["run_summary"], run_roles)
    local_summary = _augment_run_summary(validation_outputs["local_summary"], run_roles)
    point_symbol = _augment_run_summary(validation_outputs["point_symbol"], run_roles)
    delta = _surface_delta(run_summary)
    gates = _cross_surface_gates(run_summary, delta, spec)
    decision = _decision(gates, run_summary)
    outputs = {
        "surface_inputs": run_roles,
        "operator_terms": validation_outputs["operator_terms"],
        "run_summary": run_summary,
        "local_summary": local_summary,
        "point_symbol": point_symbol,
        "surface_delta": delta,
        "cross_surface_gates": gates,
        "claim_boundary": validation_outputs["claim_boundary"],
        "decision": decision,
    }
    input_paths = {
        "equation_decision": inputs.equation_dir / "beta075_source_family_equation_decision.csv",
        "principal_decision": inputs.principal_symbol_dir / "endpoint_support_principal_symbol_decision.csv",
    }
    metadata = {
        "source_name": "beta075_source_family_cross_surface_robustness",
        "spec": {
            "validation_spec": spec.validation_spec.__dict__,
            "cone_margin_relative_drift_watch": spec.cone_margin_relative_drift_watch,
            "exchange_absolute_drift_watch": spec.exchange_absolute_drift_watch,
            "total_closure_absolute_drift_watch": spec.total_closure_absolute_drift_watch,
        },
        "workers": validation_metadata["workers"],
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "validation_runs": validation_metadata["runs"],
        "claim_boundary": (
            "Cross-surface robustness for the formal beta075 source-family validation across the available "
            "baseline/dense sealed surfaces and lower-service dense surface. This is not broad beta/V robustness, "
            "not a final matter action, and not coupled Einstein-matter evolution."
        ),
    }
    return outputs, metadata


def write_cross_surface_robustness_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "surface_inputs": outdir / "beta075_source_family_cross_surface_inputs.csv",
        "operator_terms": outdir / "beta075_source_family_cross_surface_operator_terms.csv",
        "run_summary": outdir / "beta075_source_family_cross_surface_run_summary.csv",
        "local_summary": outdir / "beta075_source_family_cross_surface_local_summary.csv",
        "point_symbol": outdir / "beta075_source_family_cross_surface_point_symbol.csv",
        "surface_delta": outdir / "beta075_source_family_cross_surface_delta.csv",
        "cross_surface_gates": outdir / "beta075_source_family_cross_surface_gates.csv",
        "claim_boundary": outdir / "beta075_source_family_cross_surface_claim_boundary.csv",
        "decision": outdir / "beta075_source_family_cross_surface_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_source_family_cross_surface_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
