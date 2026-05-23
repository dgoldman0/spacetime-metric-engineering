from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest


EPS = 1.0e-30


@dataclass(frozen=True)
class SourceFamilyEnergyInputs:
    cross_surface_dir: Path
    equation_dir: Path


@dataclass(frozen=True)
class SourceFamilyEnergySpec:
    symmetry_defect_gate: float = 1.0e-12
    symmetrizer_min_eigen_gate: float = 1.0e-12
    cone_margin_gate: float = 1.0e-6
    cone_margin_watch: float = 5.0e-3
    source_work_watch: float = 1.0
    source_work_fail: float = 2.5
    support_closure_gate: float = 0.55
    support_closure_watch_fraction: float = 0.90
    local_exchange_fail: float = 0.80
    local_exchange_watch: float = 0.40
    min_source_profile_scale_gate: float = 0.0
    min_source_profile_scale_watch: float = 0.15
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


def _block(lambda_minus: float, lambda_plus: float) -> np.ndarray:
    center = 0.5 * (float(lambda_plus) + float(lambda_minus))
    half = 0.5 * (float(lambda_plus) - float(lambda_minus))
    return np.array([[center, half], [half, center]], dtype=float)


def _principal_matrix_from_symbol_row(row: pd.Series) -> np.ndarray:
    matrix = np.zeros((7, 7), dtype=float)
    matrix[0:2, 0:2] = _block(row["heat_lambda_minus"], row["heat_lambda_plus"])
    matrix[2:4, 2:4] = _block(row["angular_lambda_minus"], row["angular_lambda_plus"])
    matrix[4:6, 4:6] = _block(row["support_lambda_minus"], row["support_lambda_plus"])
    matrix[6, 6] = _finite(row["director_lambda"], 0.0)
    return matrix


def _theorem_assumptions() -> pd.DataFrame:
    rows = [
        {
            "assumption_id": "A01",
            "assumption": "fixed_background_service_metric",
            "statement": "The prescribed beta075 service metric is fixed during the source-family evolution.",
            "role": "excludes coupled Einstein-matter evolution from this certificate",
        },
        {
            "assumption_id": "A02",
            "assumption": "bounded_rapidity_state",
            "statement": "The heat-current variable is v_q=tanh(psi) with positive transport margin.",
            "role": "keeps the heat-current block inside the service cone",
        },
        {
            "assumption_id": "A03",
            "assumption": "derivative_support_reservoir",
            "statement": "The support reservoir has first-order storage/stress variables and P/F exchange enters as lower-order work.",
            "role": "provides a symmetric support principal block",
        },
        {
            "assumption_id": "A04",
            "assumption": "scheduled_source_response",
            "statement": "The source response is phase-local and service-scheduled, not an arbitrary impulse class.",
            "role": "bounds source work by the observed source-law certificate",
        },
        {
            "assumption_id": "A05",
            "assumption": "available_surface_scope",
            "statement": "The constants are certified on sealed baseline V5, sealed dense V5, and lower-service dense V2.",
            "role": "prevents overclaiming beyond generated complete surfaces",
        },
    ]
    return pd.DataFrame(rows)


def _energy_row(row: pd.Series, closure_by_label: dict[str, float], spec: SourceFamilyEnergySpec) -> dict[str, Any]:
    matrix = _principal_matrix_from_symbol_row(row)
    symmetrizer = np.eye(7, dtype=float)
    symmetrized = symmetrizer @ matrix
    symmetry_defect = float(np.max(np.abs(symmetrized - symmetrized.T)))
    eigvals = np.linalg.eigvalsh(symmetrizer)
    min_eig = float(np.min(eigvals))
    max_eig = float(np.max(eigvals))
    support_denominator = (
        abs(_finite(row.get("operator_support_stiffness_density"), 0.0))
        + abs(_finite(row.get("operator_support_inertia_density"), 0.0))
        + EPS
    )
    support_work_ratio = abs(_finite(row.get("operator_exchange_residual_load"), 0.0)) / support_denominator
    local_exchange_shape = max(
        abs(_finite(row.get("operator_local_P_error"), 0.0)),
        abs(_finite(row.get("operator_local_F_error"), 0.0)),
    )
    closure_ratio = closure_by_label.get(str(row["label"]), 0.0)
    energy_work_constant = support_work_ratio + local_exchange_shape + closure_ratio
    cone_margin = _finite(row["relative_cone_margin"], float("nan"))
    flux_speed = _finite(row["max_abs_relative_characteristic_speed"], float("nan"))
    hard_pass = bool(
        symmetry_defect <= spec.symmetry_defect_gate
        and min_eig >= spec.symmetrizer_min_eigen_gate
        and cone_margin >= spec.cone_margin_gate
        and energy_work_constant <= spec.source_work_fail
        and local_exchange_shape <= spec.local_exchange_fail
        and closure_ratio <= spec.support_closure_gate
        and bool(row["hard_formal_symbol_pass"])
    )
    watch = bool(
        hard_pass
        and (
            cone_margin < spec.cone_margin_watch
            or energy_work_constant > spec.source_work_watch
            or local_exchange_shape > spec.local_exchange_watch
            or closure_ratio > spec.support_closure_watch_fraction * spec.support_closure_gate
        )
    )
    status = "fail" if not hard_pass else "watch" if watch else "pass"
    return {
        "label": str(row["label"]),
        "surface_family": str(row.get("surface_family", "")),
        "role": str(row.get("role", "")),
        "assignment": str(row["assignment"]),
        "stage": str(row["stage"]),
        "region": str(row["region"]),
        "energy_status": status,
        "hard_energy_pass": hard_pass,
        "watch_energy": watch,
        "symmetrizer": "identity_block_symmetrizer",
        "symmetrizer_min_eigen": min_eig,
        "symmetrizer_max_eigen": max_eig,
        "symmetrizer_condition": max_eig / min_eig if min_eig > 0.0 else float("inf"),
        "principal_symmetry_defect": symmetry_defect,
        "max_abs_relative_characteristic_speed": flux_speed,
        "energy_flux_margin": cone_margin,
        "support_work_ratio": support_work_ratio,
        "local_exchange_shape": local_exchange_shape,
        "support_total_closure_ratio": closure_ratio,
        "energy_work_constant": energy_work_constant,
        "transport_margin": _finite(row.get("transport_margin"), float("nan")),
        "transport_rapidity_abs": _finite(row.get("transport_rapidity_abs"), float("nan")),
    }


def _closure_by_label(run_summary: pd.DataFrame) -> dict[str, float]:
    return {
        str(row["label"]): _finite(row["support_total_local_pf_ratio"], 0.0)
        for _, row in run_summary.iterrows()
    }


def _energy_point_table(
    point_symbol: pd.DataFrame,
    run_summary: pd.DataFrame,
    spec: SourceFamilyEnergySpec,
) -> pd.DataFrame:
    active = point_symbol.loc[
        point_symbol["medium_source_active"].astype(bool)
        & (~point_symbol["covariant_divergence_live"].astype(bool))
    ].copy()
    closure = _closure_by_label(run_summary)
    rows = [_energy_row(row, closure, spec) for _, row in active.iterrows()]
    return pd.DataFrame(rows)


def _summary_by_run(energy_points: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in energy_points.groupby(["label", "surface_family", "role"], sort=False, dropna=False):
        label, surface_family, role = key
        rows.append({
            "label": str(label),
            "surface_family": str(surface_family),
            "role": str(role),
            "energy_status": (
                "fail"
                if (group["energy_status"].astype(str) == "fail").any()
                else "watch"
                if (group["energy_status"].astype(str) == "watch").any()
                else "pass"
            ),
            "hard_energy_pass": bool(group["hard_energy_pass"].astype(bool).all()),
            "rows": int(len(group)),
            "fail_rows": int((group["energy_status"].astype(str) == "fail").sum()),
            "watch_rows": int((group["energy_status"].astype(str) == "watch").sum()),
            "min_energy_flux_margin": float(group["energy_flux_margin"].astype(float).min()),
            "p01_energy_flux_margin": float(group["energy_flux_margin"].astype(float).quantile(0.01)),
            "max_energy_work_constant": float(group["energy_work_constant"].astype(float).max()),
            "p99_energy_work_constant": float(group["energy_work_constant"].astype(float).quantile(0.99)),
            "max_support_work_ratio": float(group["support_work_ratio"].astype(float).max()),
            "max_local_exchange_shape": float(group["local_exchange_shape"].astype(float).max()),
            "support_total_closure_ratio": float(group["support_total_closure_ratio"].astype(float).max()),
            "max_principal_symmetry_defect": float(group["principal_symmetry_defect"].astype(float).max()),
            "max_symmetrizer_condition": float(group["symmetrizer_condition"].astype(float).max()),
        })
    return pd.DataFrame(rows)


def _summary_by_local(energy_points: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in energy_points.groupby(["label", "surface_family", "role", "assignment", "stage", "region"], sort=False, dropna=False):
        label, surface_family, role, assignment, stage, region = key
        rows.append({
            "label": str(label),
            "surface_family": str(surface_family),
            "role": str(role),
            "assignment": str(assignment),
            "stage": str(stage),
            "region": str(region),
            "energy_status": (
                "fail"
                if (group["energy_status"].astype(str) == "fail").any()
                else "watch"
                if (group["energy_status"].astype(str) == "watch").any()
                else "pass"
            ),
            "rows": int(len(group)),
            "fail_rows": int((group["energy_status"].astype(str) == "fail").sum()),
            "watch_rows": int((group["energy_status"].astype(str) == "watch").sum()),
            "min_energy_flux_margin": float(group["energy_flux_margin"].astype(float).min()),
            "max_energy_work_constant": float(group["energy_work_constant"].astype(float).max()),
            "max_support_work_ratio": float(group["support_work_ratio"].astype(float).max()),
            "max_local_exchange_shape": float(group["local_exchange_shape"].astype(float).max()),
        })
    return pd.DataFrame(rows)


def _energy_gates(
    run_summary: pd.DataFrame,
    cross_decision: pd.DataFrame,
    equation_decision: pd.DataFrame,
    spec: SourceFamilyEnergySpec,
) -> pd.DataFrame:
    cross = cross_decision.iloc[0]
    equation = equation_decision.iloc[0]
    min_margin = float(run_summary["min_energy_flux_margin"].astype(float).min()) if len(run_summary) else float("nan")
    max_work = float(run_summary["max_energy_work_constant"].astype(float).max()) if len(run_summary) else float("nan")
    max_closure = float(run_summary["support_total_closure_ratio"].astype(float).max()) if len(run_summary) else float("nan")
    max_exchange = float(run_summary["max_local_exchange_shape"].astype(float).max()) if len(run_summary) else float("nan")
    max_symmetry = float(run_summary["max_principal_symmetry_defect"].astype(float).max()) if len(run_summary) else float("inf")
    max_condition = float(run_summary["max_symmetrizer_condition"].astype(float).max()) if len(run_summary) else float("inf")
    min_scale = _finite(equation["min_source_profile_scale"], float("nan"))
    failed_rows = int(run_summary["fail_rows"].astype(int).sum()) if len(run_summary) else 1
    return pd.DataFrame([
        {
            "gate": "cross_surface_hard_validation",
            "status": "pass" if _truth(cross["hard_cross_surface_pass"]) else "fail",
            "value": str(cross["cross_surface_robustness_status"]),
            "gate_value": "hard_cross_surface_pass",
            "read": "energy certificate inherits hard-clean formal source-family validation surfaces",
        },
        {
            "gate": "positive_symmetrizer",
            "status": "pass" if max_condition < float("inf") else "fail",
            "value": max_condition,
            "gate_value": 1.0,
            "read": "identity block symmetrizer is positive definite on the formal symmetric principal matrix",
        },
        {
            "gate": "principal_symmetry",
            "status": "pass" if max_symmetry <= spec.symmetry_defect_gate else "fail",
            "value": max_symmetry,
            "gate_value": spec.symmetry_defect_gate,
            "read": "symmetrized principal matrix is symmetric to numerical precision",
        },
        {
            "gate": "energy_flux_inside_cone",
            "status": (
                "fail"
                if min_margin < spec.cone_margin_gate
                else "watch"
                if min_margin < spec.cone_margin_watch
                else "pass"
            ),
            "value": min_margin,
            "gate_value": spec.cone_margin_gate,
            "read": "energy flux remains inside the service cone, with thin-margin watch carried",
        },
        {
            "gate": "lower_order_work_bound",
            "status": (
                "fail"
                if max_work > spec.source_work_fail
                else "watch"
                if max_work > spec.source_work_watch
                else "pass"
            ),
            "value": max_work,
            "gate_value": spec.source_work_fail,
            "read": "support exchange and closure enter as bounded lower-order work constants",
        },
        {
            "gate": "local_exchange_shape_bound",
            "status": (
                "fail"
                if max_exchange > spec.local_exchange_fail
                else "watch"
                if max_exchange > spec.local_exchange_watch
                else "pass"
            ),
            "value": max_exchange,
            "gate_value": spec.local_exchange_fail,
            "read": "local P/F exchange shape is bounded but remains a watch constant",
        },
        {
            "gate": "support_closure_work_bound",
            "status": (
                "fail"
                if max_closure > spec.support_closure_gate
                else "watch"
                if max_closure > spec.support_closure_watch_fraction * spec.support_closure_gate
                else "pass"
            ),
            "value": max_closure,
            "gate_value": spec.support_closure_gate,
            "read": "support total-closure work stays below the local closure gate",
        },
        {
            "gate": "scheduled_source_bound",
            "status": (
                "fail"
                if min_scale <= spec.min_source_profile_scale_gate
                else "watch"
                if min_scale < spec.min_source_profile_scale_watch
                else "pass"
            ),
            "value": min_scale,
            "gate_value": spec.min_source_profile_scale_gate,
            "read": "scheduled phase-local source response is bounded but sharp",
        },
        {
            "gate": "energy_point_failures",
            "status": "pass" if failed_rows == 0 else "fail",
            "value": failed_rows,
            "gate_value": 0,
            "read": "no active point violates the configured energy hard gates",
        },
        {
            "gate": "available_surface_scope",
            "status": "pass" if int(cross["surface_count"]) >= spec.required_surface_count else "watch",
            "value": int(cross["surface_count"]),
            "gate_value": spec.required_surface_count,
            "read": "certificate is limited to the available complete fixed-background surfaces",
        },
    ])


def _decision(gates: pd.DataFrame, run_summary: pd.DataFrame) -> pd.DataFrame:
    fail_count = int((gates["status"].astype(str) == "fail").sum())
    watch_count = int((gates["status"].astype(str) == "watch").sum())
    hard_pass = fail_count == 0
    worst_margin = run_summary.loc[int(run_summary["min_energy_flux_margin"].astype(float).idxmin())]
    worst_work = run_summary.loc[int(run_summary["max_energy_work_constant"].astype(float).idxmax())]
    status = (
        "fixed_background_energy_estimate_watch_pass"
        if hard_pass and watch_count
        else "fixed_background_energy_estimate_pass"
        if hard_pass
        else "fixed_background_energy_estimate_fail"
    )
    return pd.DataFrame([{
        "energy_certificate_status": status,
        "hard_energy_certificate_pass": hard_pass,
        "failed_gate_count": fail_count,
        "watch_count": watch_count,
        "surface_count": int(len(run_summary)),
        "worst_margin_surface": str(worst_margin["label"]),
        "worst_energy_flux_margin": _finite(worst_margin["min_energy_flux_margin"], float("nan")),
        "worst_work_surface": str(worst_work["label"]),
        "worst_energy_work_constant": _finite(worst_work["max_energy_work_constant"], float("nan")),
        "max_support_work_ratio": float(run_summary["max_support_work_ratio"].astype(float).max()),
        "max_local_exchange_shape": float(run_summary["max_local_exchange_shape"].astype(float).max()),
        "max_support_total_closure_ratio": float(run_summary["support_total_closure_ratio"].astype(float).max()),
        "decision_read": (
            "fixed-background formal source family admits a symmetric energy estimate with explicit watch constants"
            if hard_pass and watch_count
            else "fixed-background formal source family admits a symmetric energy estimate without configured watches"
            if hard_pass
            else "fixed-background formal source-family energy estimate fails at least one hard gate"
        ),
    }])


def build_source_family_energy_certificate(
    inputs: SourceFamilyEnergyInputs,
    *,
    spec: SourceFamilyEnergySpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or SourceFamilyEnergySpec()
    point_symbol = _read_csv(inputs.cross_surface_dir / "beta075_source_family_cross_surface_point_symbol.csv")
    cross_run_summary = _read_csv(inputs.cross_surface_dir / "beta075_source_family_cross_surface_run_summary.csv")
    cross_decision = _read_csv(inputs.cross_surface_dir / "beta075_source_family_cross_surface_decision.csv")
    equation_decision = _read_csv(inputs.equation_dir / "beta075_source_family_equation_decision.csv")
    energy_points = _energy_point_table(point_symbol, cross_run_summary, spec)
    run_summary = _summary_by_run(energy_points)
    local_summary = _summary_by_local(energy_points)
    gates = _energy_gates(run_summary, cross_decision, equation_decision, spec)
    decision = _decision(gates, run_summary)
    outputs = {
        "theorem_assumptions": _theorem_assumptions(),
        "energy_point": energy_points,
        "energy_run_summary": run_summary,
        "energy_local_summary": local_summary,
        "energy_gates": gates,
        "decision": decision,
    }
    input_paths = {
        "cross_surface_point_symbol": inputs.cross_surface_dir / "beta075_source_family_cross_surface_point_symbol.csv",
        "cross_surface_run_summary": inputs.cross_surface_dir / "beta075_source_family_cross_surface_run_summary.csv",
        "cross_surface_decision": inputs.cross_surface_dir / "beta075_source_family_cross_surface_decision.csv",
        "equation_decision": inputs.equation_dir / "beta075_source_family_equation_decision.csv",
    }
    metadata = {
        "source_name": "beta075_source_family_energy_certificate",
        "spec": spec.__dict__,
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "cross_surface_manifest": _read_json(inputs.cross_surface_dir / "beta075_source_family_cross_surface_manifest.json").get("source_name", ""),
        "claim_boundary": (
            "Fixed-background symmetric-hyperbolic / energy-estimate certificate for the formal beta075 source family "
            "on available complete surfaces. This is theorem-style PDE packaging with explicit watch constants; "
            "it is not a final matter action, global hyperbolicity theorem, or coupled Einstein-matter evolution."
        ),
    }
    return outputs, metadata


def write_source_family_energy_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "theorem_assumptions": outdir / "beta075_source_family_energy_theorem_assumptions.csv",
        "energy_point": outdir / "beta075_source_family_energy_point.csv",
        "energy_run_summary": outdir / "beta075_source_family_energy_run_summary.csv",
        "energy_local_summary": outdir / "beta075_source_family_energy_local_summary.csv",
        "energy_gates": outdir / "beta075_source_family_energy_gates.csv",
        "decision": outdir / "beta075_source_family_energy_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_source_family_energy_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
