from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class EnergyConstantAuditInputs:
    energy_dir: Path


@dataclass(frozen=True)
class EnergyConstantAuditSpec:
    source_work_fail: float = 2.5
    work_utilization_watch: float = 0.75
    dense_work_delta_gate: float = 0.03
    dense_support_delta_gate: float = 0.02
    dense_exchange_delta_gate: float = 0.02
    dense_closure_delta_gate: float = 0.01
    dense_flux_drop_gate: float = 0.35
    support_closure_fail: float = 0.55
    local_exchange_fail: float = 0.80
    required_surface_count: int = 3


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


def _constant_decomposition(run_summary: pd.DataFrame, spec: EnergyConstantAuditSpec) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in run_summary.iterrows():
        support = _finite(row["max_support_work_ratio"], float("nan"))
        exchange = _finite(row["max_local_exchange_shape"], float("nan"))
        closure = _finite(row["support_total_closure_ratio"], float("nan"))
        work = _finite(row["max_energy_work_constant"], float("nan"))
        max_component_upper_sum = support + exchange + closure
        headroom = spec.source_work_fail - work
        utilization = work / spec.source_work_fail if spec.source_work_fail > 0.0 else float("nan")
        rows.append({
            "label": str(row["label"]),
            "surface_family": str(row.get("surface_family", "")),
            "role": str(row.get("role", "")),
            "energy_status": str(row.get("energy_status", "")),
            "hard_energy_pass": _truth(row.get("hard_energy_pass", False)),
            "max_energy_work_constant": work,
            "support_work_ratio": support,
            "local_exchange_shape": exchange,
            "support_total_closure_ratio": closure,
            "max_component_upper_sum": max_component_upper_sum,
            "component_upper_slack": max_component_upper_sum - work,
            "work_headroom_to_fail": headroom,
            "work_headroom_fraction": headroom / spec.source_work_fail if spec.source_work_fail > 0.0 else float("nan"),
            "work_utilization": utilization,
            "support_work_share": support / work if work > 0.0 else float("nan"),
            "local_exchange_share": exchange / work if work > 0.0 else float("nan"),
            "closure_share": closure / work if work > 0.0 else float("nan"),
            "constant_watch": bool(utilization > spec.work_utilization_watch),
            "read": (
                "bounded high-utilization work constant"
                if utilization > spec.work_utilization_watch
                else "bounded lower-utilization work constant"
            ),
        })
    return pd.DataFrame(rows)


def _local_constant_decomposition(
    local_summary: pd.DataFrame,
    run_decomposition: pd.DataFrame,
    spec: EnergyConstantAuditSpec,
) -> pd.DataFrame:
    closure_by_label = {
        str(row["label"]): _finite(row["support_total_closure_ratio"], 0.0)
        for _, row in run_decomposition.iterrows()
    }
    rows: list[dict[str, Any]] = []
    for _, row in local_summary.iterrows():
        label = str(row["label"])
        support = _finite(row["max_support_work_ratio"], float("nan"))
        exchange = _finite(row["max_local_exchange_shape"], float("nan"))
        closure = closure_by_label.get(label, float("nan"))
        work = _finite(row["max_energy_work_constant"], float("nan"))
        reconstructed = support + exchange + closure
        rows.append({
            "label": label,
            "surface_family": str(row.get("surface_family", "")),
            "role": str(row.get("role", "")),
            "assignment": str(row["assignment"]),
            "stage": str(row["stage"]),
            "region": str(row["region"]),
            "energy_status": str(row.get("energy_status", "")),
            "rows": int(row.get("rows", 0)),
            "fail_rows": int(row.get("fail_rows", 0)),
            "watch_rows": int(row.get("watch_rows", 0)),
            "min_energy_flux_margin": _finite(row["min_energy_flux_margin"], float("nan")),
            "max_energy_work_constant": work,
            "support_work_ratio": support,
            "local_exchange_shape": exchange,
            "surface_closure_constant": closure,
            "reconstructed_local_upper_constant": reconstructed,
            "work_headroom_to_fail": spec.source_work_fail - work,
            "work_utilization": work / spec.source_work_fail if spec.source_work_fail > 0.0 else float("nan"),
            "dominant_local_term": _dominant_term(support, exchange, closure),
        })
    return pd.DataFrame(rows)


def _dominant_term(support: float, exchange: float, closure: float) -> str:
    terms = {
        "support_work": support,
        "local_exchange": exchange,
        "surface_closure": closure,
    }
    return max(terms, key=lambda key: _finite(terms[key], float("-inf")))


def _surface_stability(run_decomposition: pd.DataFrame) -> pd.DataFrame:
    reference = run_decomposition.loc[run_decomposition["role"].astype(str).eq("reference_dense")]
    if not len(reference):
        reference = run_decomposition.head(1)
    ref = reference.iloc[0]
    ref_margin = _finite(ref.get("min_energy_flux_margin"), float("nan"))
    rows: list[dict[str, Any]] = []
    for _, row in run_decomposition.iterrows():
        margin = _finite(row.get("min_energy_flux_margin"), float("nan"))
        rows.append({
            "label": str(row["label"]),
            "surface_family": str(row.get("surface_family", "")),
            "role": str(row.get("role", "")),
            "reference_label": str(ref["label"]),
            "work_delta_from_reference": _finite(row["max_energy_work_constant"], float("nan"))
            - _finite(ref["max_energy_work_constant"], float("nan")),
            "support_work_delta_from_reference": _finite(row["support_work_ratio"], float("nan"))
            - _finite(ref["support_work_ratio"], float("nan")),
            "local_exchange_delta_from_reference": _finite(row["local_exchange_shape"], float("nan"))
            - _finite(ref["local_exchange_shape"], float("nan")),
            "closure_delta_from_reference": _finite(row["support_total_closure_ratio"], float("nan"))
            - _finite(ref["support_total_closure_ratio"], float("nan")),
            "energy_flux_margin": margin,
            "energy_flux_margin_delta_from_reference": margin - ref_margin,
            "energy_flux_relative_drop_from_reference": (
                (ref_margin - margin) / ref_margin if ref_margin > 0.0 else float("nan")
            ),
        })
    return pd.DataFrame(rows)


def _augment_run_decomposition(run_decomposition: pd.DataFrame, run_summary: pd.DataFrame) -> pd.DataFrame:
    margins = run_summary[["label", "min_energy_flux_margin", "fail_rows"]].copy()
    return run_decomposition.merge(margins, on="label", how="left")


def _classification_gates(
    run_decomposition: pd.DataFrame,
    surface_stability: pd.DataFrame,
    energy_decision: pd.DataFrame,
    energy_gates: pd.DataFrame,
    spec: EnergyConstantAuditSpec,
) -> pd.DataFrame:
    decision = energy_decision.iloc[0]
    worst = run_decomposition.loc[int(run_decomposition["max_energy_work_constant"].astype(float).idxmax())]
    adjacent = surface_stability.loc[
        surface_stability["role"].astype(str).eq("adjacent_service_surface")
    ]
    if len(adjacent):
        adjacent_row = adjacent.iloc[0]
    else:
        adjacent_row = surface_stability.loc[
            surface_stability["role"].astype(str).ne("reference_dense")
        ].head(1).iloc[0]
    energy_gate_lookup = {
        str(row["gate"]): str(row["status"])
        for _, row in energy_gates.iterrows()
    }
    max_work = _finite(worst["max_energy_work_constant"], float("nan"))
    max_exchange = float(run_decomposition["local_exchange_shape"].astype(float).max())
    max_closure = float(run_decomposition["support_total_closure_ratio"].astype(float).max())
    utilization = max_work / spec.source_work_fail if spec.source_work_fail > 0.0 else float("nan")
    headroom = spec.source_work_fail - max_work
    stable_adjacent = bool(
        abs(_finite(adjacent_row["work_delta_from_reference"], float("nan"))) <= spec.dense_work_delta_gate
        and abs(_finite(adjacent_row["support_work_delta_from_reference"], float("nan"))) <= spec.dense_support_delta_gate
        and abs(_finite(adjacent_row["local_exchange_delta_from_reference"], float("nan"))) <= spec.dense_exchange_delta_gate
        and abs(_finite(adjacent_row["closure_delta_from_reference"], float("nan"))) <= spec.dense_closure_delta_gate
        and _finite(adjacent_row["energy_flux_relative_drop_from_reference"], 0.0) <= spec.dense_flux_drop_gate
    )
    hard_clean = bool(
        _truth(decision["hard_energy_certificate_pass"])
        and int(decision["failed_gate_count"]) == 0
        and int(run_decomposition["fail_rows"].astype(int).sum()) == 0
    )
    direct_buffer_required = bool(
        max_work >= spec.source_work_fail
        or max_exchange >= spec.local_exchange_fail
        or max_closure >= spec.support_closure_fail
        or not stable_adjacent
        or not hard_clean
    )
    buffer_watch = bool(not direct_buffer_required and utilization > spec.work_utilization_watch)
    return pd.DataFrame([
        {
            "gate": "inherited_energy_hard_certificate",
            "status": "pass" if hard_clean else "fail",
            "value": int(decision["failed_gate_count"]),
            "gate_value": 0,
            "read": "energy certificate has no hard failures or point failures",
        },
        {
            "gate": "lower_order_work_failure_headroom",
            "status": "pass" if headroom > 0.0 else "fail",
            "value": headroom,
            "gate_value": 0.0,
            "read": "work constant remains below the configured hard theorem bound",
        },
        {
            "gate": "lower_order_work_utilization",
            "status": "watch" if buffer_watch else "pass" if not direct_buffer_required else "fail",
            "value": utilization,
            "gate_value": spec.work_utilization_watch,
            "read": "high utilization creates safety-margin debt but not an immediate redesign requirement",
        },
        {
            "gate": "adjacent_surface_recurrence_stability",
            "status": "pass" if stable_adjacent else "fail",
            "value": abs(_finite(adjacent_row["work_delta_from_reference"], float("nan"))),
            "gate_value": spec.dense_work_delta_gate,
            "read": "adjacent dense V2 reproduces the dense V5 constant instead of amplifying it",
        },
        {
            "gate": "local_exchange_and_closure_below_hard_gates",
            "status": "pass" if max_exchange < spec.local_exchange_fail and max_closure < spec.support_closure_fail else "fail",
            "value": f"exchange={max_exchange:.12g}; closure={max_closure:.12g}",
            "gate_value": f"exchange<{spec.local_exchange_fail}; closure<{spec.support_closure_fail}",
            "read": "sharp P/F exchange and closure constants remain below their hard energy bounds",
        },
        {
            "gate": "energy_certificate_watch_consistency",
            "status": "pass"
            if energy_gate_lookup.get("lower_order_work_bound") == "watch"
            and energy_gate_lookup.get("energy_point_failures") == "pass"
            else "watch",
            "value": energy_gate_lookup.get("lower_order_work_bound", ""),
            "gate_value": "watch",
            "read": "the recurring constant is already represented as explicit theorem watch debt",
        },
        {
            "gate": "protective_buffer_required_now",
            "status": "fail" if direct_buffer_required else "pass",
            "value": direct_buffer_required,
            "gate_value": False,
            "read": "no explicit protective buffer is required before the next rung unless a later coupled test activates this debt",
        },
    ])


def _decision(
    gates: pd.DataFrame,
    run_decomposition: pd.DataFrame,
    surface_stability: pd.DataFrame,
    spec: EnergyConstantAuditSpec,
) -> pd.DataFrame:
    fail_count = int((gates["status"].astype(str) == "fail").sum())
    watch_count = int((gates["status"].astype(str) == "watch").sum())
    worst = run_decomposition.loc[int(run_decomposition["max_energy_work_constant"].astype(float).idxmax())]
    adjacent = surface_stability.loc[
        surface_stability["role"].astype(str).eq("adjacent_service_surface")
    ]
    adjacent_row = adjacent.iloc[0] if len(adjacent) else surface_stability.iloc[0]
    utilization = _finite(worst["work_utilization"], float("nan"))
    buffer_required = bool(
        gates.loc[gates["gate"].astype(str).eq("protective_buffer_required_now"), "status"].iloc[0] == "fail"
    )
    buffer_watch = bool(not buffer_required and utilization > spec.work_utilization_watch)
    status = (
        "energy_constant_audit_fail_buffer_required"
        if buffer_required
        else "stable_limiting_theorem_constant_with_buffer_watch"
        if buffer_watch
        else "stable_limiting_theorem_constant"
    )
    return pd.DataFrame([{
        "energy_constant_audit_status": status,
        "hard_constant_audit_pass": fail_count == 0,
        "failed_gate_count": fail_count,
        "watch_count": watch_count,
        "protective_buffer_required_now": buffer_required,
        "protective_buffer_watch": buffer_watch,
        "theorem_constant_classification": (
            "limiting_theorem_constant_with_safety_margin_debt"
            if not buffer_required
            else "insufficient_margin_requires_buffer_or_refinement"
        ),
        "worst_surface": str(worst["label"]),
        "worst_work_constant": _finite(worst["max_energy_work_constant"], float("nan")),
        "work_fail_bound": spec.source_work_fail,
        "work_headroom_to_fail": _finite(worst["work_headroom_to_fail"], float("nan")),
        "work_headroom_fraction": _finite(worst["work_headroom_fraction"], float("nan")),
        "work_utilization": utilization,
        "dense_adjacent_work_delta": _finite(adjacent_row["work_delta_from_reference"], float("nan")),
        "dense_adjacent_exchange_delta": _finite(adjacent_row["local_exchange_delta_from_reference"], float("nan")),
        "dense_adjacent_closure_delta": _finite(adjacent_row["closure_delta_from_reference"], float("nan")),
        "dense_adjacent_flux_relative_drop": _finite(adjacent_row["energy_flux_relative_drop_from_reference"], float("nan")),
        "decision_read": (
            "recurring energy work constant is stable across available dense surfaces and remains below hard bound; "
            "read it as a limiting theorem constant with a protective-buffer watch, not a current source-family redesign"
            if not buffer_required and buffer_watch
            else "recurring energy work constant is stable and below watch utilization"
            if not buffer_required
            else "recurring energy work constant fails a hard audit condition and needs buffer or source-family refinement"
        ),
    }])


def build_energy_constant_audit(
    inputs: EnergyConstantAuditInputs,
    *,
    spec: EnergyConstantAuditSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or EnergyConstantAuditSpec()
    run_summary = _read_csv(inputs.energy_dir / "beta075_source_family_energy_run_summary.csv")
    local_summary = _read_csv(inputs.energy_dir / "beta075_source_family_energy_local_summary.csv")
    energy_decision = _read_csv(inputs.energy_dir / "beta075_source_family_energy_decision.csv")
    energy_gates = _read_csv(inputs.energy_dir / "beta075_source_family_energy_gates.csv")
    run_decomposition = _constant_decomposition(run_summary, spec)
    run_decomposition = _augment_run_decomposition(run_decomposition, run_summary)
    local_decomposition = _local_constant_decomposition(local_summary, run_decomposition, spec)
    stability = _surface_stability(run_decomposition)
    gates = _classification_gates(run_decomposition, stability, energy_decision, energy_gates, spec)
    decision = _decision(gates, run_decomposition, stability, spec)
    outputs = {
        "constant_decomposition": run_decomposition,
        "local_constant_decomposition": local_decomposition,
        "surface_stability": stability,
        "classification_gates": gates,
        "decision": decision,
    }
    input_paths = {
        "energy_run_summary": inputs.energy_dir / "beta075_source_family_energy_run_summary.csv",
        "energy_local_summary": inputs.energy_dir / "beta075_source_family_energy_local_summary.csv",
        "energy_decision": inputs.energy_dir / "beta075_source_family_energy_decision.csv",
        "energy_gates": inputs.energy_dir / "beta075_source_family_energy_gates.csv",
    }
    metadata = {
        "source_name": "beta075_source_family_energy_constant_audit",
        "spec": spec.__dict__,
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "energy_manifest": _read_json(inputs.energy_dir / "beta075_source_family_energy_manifest.json").get("source_name", ""),
        "claim_boundary": (
            "Classification audit for the recurring fixed-background energy work constant. "
            "This uses existing energy-certificate outputs only; it does not retune a component or generate report prose."
        ),
    }
    return outputs, metadata


def write_energy_constant_audit_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "constant_decomposition": outdir / "beta075_source_family_energy_constant_decomposition.csv",
        "local_constant_decomposition": outdir / "beta075_source_family_energy_constant_local_decomposition.csv",
        "surface_stability": outdir / "beta075_source_family_energy_constant_surface_stability.csv",
        "classification_gates": outdir / "beta075_source_family_energy_constant_classification_gates.csv",
        "decision": outdir / "beta075_source_family_energy_constant_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_source_family_energy_constant_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
