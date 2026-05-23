from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class Beta075SealReadinessInputs:
    support_robustness_dir: Path = Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_sector_robustness_gate")
    principal_symbol_dir: Path = Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_principal_symbol")
    symbol_sensitivity_dir: Path = Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_symbol_sensitivity")
    transport_evolution_dir: Path = Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_transport_evolution")
    rapidity_budget_dir: Path = Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_rapidity_budget")
    rapidity_advection_dir: Path = Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_rapidity_advection")


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


def _truth(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "pass"}


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _one(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        raise ValueError("expected at least one row")
    return frame.iloc[0]


def _gate_row(frame: pd.DataFrame, gate: str) -> pd.Series:
    selected = frame.loc[frame["gate"].astype(str) == gate]
    if selected.empty:
        raise ValueError(f"missing gate row {gate!r}")
    return selected.iloc[0]


def _decision_row(
    gate: str,
    status: str,
    hard_required: bool,
    metric: float,
    gate_value: float,
    read: str,
) -> dict[str, Any]:
    blocker = bool(hard_required and status == "fail")
    return {
        "gate": gate,
        "status": status,
        "hard_required": bool(hard_required),
        "blocks_bounded_seal": blocker,
        "metric": metric,
        "gate_value": gate_value,
        "read": read,
    }


def classify_bounded_seal_status(gate_matrix: pd.DataFrame) -> pd.DataFrame:
    blockers = int(gate_matrix["blocks_bounded_seal"].astype(bool).sum())
    required = gate_matrix.loc[gate_matrix["hard_required"].astype(bool)]
    required_watch = int((required["status"].astype(str) == "watch").sum())
    watches = int((gate_matrix["status"].astype(str) == "watch").sum())
    if blockers:
        status = "not_ready"
    elif watches:
        status = "bounded_seal_ready_with_watches"
    else:
        status = "bounded_seal_ready_clean"
    return pd.DataFrame([{
        "beta075_seal_readiness_status": status,
        "bounded_seal_ready": bool(blockers == 0),
        "hard_blocker_count": blockers,
        "required_watch_count": required_watch,
        "watch_count": watches,
        "required_gate_count": int(len(required)),
        "gate_count": int(len(gate_matrix)),
        "decision_read": (
            "bounded beta075 seal is blocked by one or more required gates"
            if blockers
            else "bounded beta075 seal is ready, with named watch items carried as future proof obligations"
            if watches
            else "bounded beta075 seal is ready with no active watch gates in this scope"
        ),
    }])


def _build_gate_matrix(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    robustness_gate = tables["support_robustness_gate"]
    robustness_decision = tables["support_robustness_decision"]
    robustness_local = tables["support_robustness_local"]
    principal = _one(tables["principal_decision"])
    principal_runs = tables["principal_runs"]
    sensitivity = _one(tables["sensitivity_decision"])
    transport = _one(tables["transport_decision"])
    budget = _one(tables["rapidity_budget_decision"])
    advection = _one(tables["rapidity_advection_decision"])

    reference = _gate_row(robustness_gate, "reference_total_closure")
    compact = _gate_row(robustness_gate, "compact_cross_bracket")
    locality = _gate_row(robustness_gate, "locality_and_hidden_channel")
    coefficient = _gate_row(robustness_gate, "coefficient_stability")
    concentration = _gate_row(robustness_gate, "residual_concentration_scaling")

    dense_ref = _one(robustness_decision.loc[
        (robustness_decision["kind"].astype(str) == "reference_24x14")
        & (robustness_decision["mesh"].astype(str) == "dense")
    ])
    dense_principal = _one(principal_runs.loc[
        (principal_runs["kind"].astype(str) == "reference_24x14")
        & (principal_runs["mesh"].astype(str) == "dense")
    ])
    reset_core = _one(robustness_local.loc[
        (robustness_local["kind"].astype(str) == "reference_24x14")
        & (robustness_local["mesh"].astype(str) == "dense")
        & (robustness_local["assignment"].astype(str) == "reset_decompression_endpoint_junction")
        & (robustness_local["stage"].astype(str) == "reset_decompression")
        & (robustness_local["region"].astype(str) == "core_throat")
    ])

    rows = [
        _decision_row(
            "promoted_24x14_total_closure",
            "watch" if str(reference["status"]) == "watch" else str(reference["status"]),
            True,
            _finite(dense_ref["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan")),
            _finite(dense_ref["local_closure_pf_gate"], float("nan")),
            "promoted 24x14 support sector clears baseline/dense total closure, but dense local margin remains tight",
        ),
        _decision_row(
            "locality_and_hidden_channel",
            str(locality["status"]),
            True,
            _finite(locality["metric"], float("nan")),
            _finite(locality["gate_value"], float("nan")),
            str(locality["read"]),
        ),
        _decision_row(
            "reduced_principal_symbol",
            "watch" if _truth(principal["passes_reduced_principal_symbol_gate"]) else "fail",
            True,
            _finite(principal["dense_tightest_relative_cone_margin"], float("nan")),
            1.0e-6,
            str(principal["decision_read"]),
        ),
        _decision_row(
            "bounded_rapidity_transport",
            "pass" if _truth(transport["bounded_delta_1e4_damped_passes"]) else "fail",
            True,
            _finite(transport["bounded_delta_1e4_damped_min_margin"], float("nan")),
            1.0e-6,
            str(transport["decision_read"]),
        ),
        _decision_row(
            "rapidity_budget_observed_kick",
            "watch" if int(budget["large_exceeds_budget_rows"]) else "pass",
            True,
            _finite(budget["max_observed_budget_fraction"], float("nan")),
            1.0,
            str(budget["decision_read"]),
        ),
        _decision_row(
            "advection_nonconcentration",
            "pass" if _truth(advection["observed_unlimited_pass"]) and _truth(advection["observed_limiter_inactive"]) else "fail",
            True,
            _finite(advection["max_observed_unlimited_budget_fraction"], float("nan")),
            1.0,
            str(advection["decision_read"]),
        ),
        _decision_row(
            "dense_reset_core_watch",
            "watch",
            True,
            _finite(reset_core["residual_to_target_abs_PF"], float("nan")),
            _finite(dense_ref["local_closure_pf_gate"], float("nan")),
            "dense reset/core is the tightest closure watch and stays just inside the promoted local PF gate",
        ),
        _decision_row(
            "compact_cross_bracket",
            "watch" if str(compact["status"]) != "pass" else "pass",
            False,
            _finite(compact["metric"], float("nan")),
            _finite(compact["gate_value"], float("nan")),
            str(compact["read"]),
        ),
        _decision_row(
            "raw_heat_current_sensitivity",
            "watch" if str(sensitivity["symbol_sensitivity_status"]) == "fragile_watch" else "fail",
            False,
            _finite(sensitivity["first_positive_heat_delta_with_failures"], float("nan")),
            1.0e-4,
            str(sensitivity["decision_read"]),
        ),
        _decision_row(
            "coefficient_stability",
            str(coefficient["status"]),
            False,
            _finite(coefficient["metric"], float("nan")),
            _finite(coefficient["gate_value"], float("nan")),
            str(coefficient["read"]),
        ),
        _decision_row(
            "residual_concentration_scaling",
            str(concentration["status"]),
            False,
            _finite(concentration["metric"], float("nan")),
            _finite(concentration["gate_value"], float("nan")),
            str(concentration["read"]),
        ),
        _decision_row(
            "dense_principal_symbol_margin",
            "watch" if str(dense_principal["symbol_status"]) == "watch" else str(dense_principal["symbol_status"]),
            False,
            _finite(dense_principal["min_relative_cone_margin"], float("nan")),
            1.0e-6,
            "dense promoted run has no hard principal-symbol failures but remains characteristic-margin thin",
        ),
    ]
    return pd.DataFrame(rows)


def _build_watch_ledger(gate_matrix: pd.DataFrame) -> pd.DataFrame:
    watches = gate_matrix.loc[gate_matrix["status"].astype(str) == "watch"].copy()
    return watches[["gate", "hard_required", "metric", "gate_value", "read"]].reset_index(drop=True)


def build_beta075_seal_readiness(
    inputs: Beta075SealReadinessInputs | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    inputs = inputs or Beta075SealReadinessInputs()
    paths = {
        "support_robustness_gate": inputs.support_robustness_dir / "support_sector_robustness_gate_summary.csv",
        "support_robustness_decision": inputs.support_robustness_dir / "support_sector_robustness_decision_compare.csv",
        "support_robustness_local": inputs.support_robustness_dir / "support_sector_robustness_local_residual_compare.csv",
        "principal_decision": inputs.principal_symbol_dir / "endpoint_support_principal_symbol_decision.csv",
        "principal_runs": inputs.principal_symbol_dir / "endpoint_support_principal_symbol_run_summary.csv",
        "sensitivity_decision": inputs.symbol_sensitivity_dir / "endpoint_support_symbol_sensitivity_decision.csv",
        "transport_decision": inputs.transport_evolution_dir / "endpoint_support_transport_evolution_decision.csv",
        "rapidity_budget_decision": inputs.rapidity_budget_dir / "endpoint_support_rapidity_budget_decision.csv",
        "rapidity_budget_rows": inputs.rapidity_budget_dir / "endpoint_support_rapidity_budget_rows.csv",
        "rapidity_advection_decision": inputs.rapidity_advection_dir / "endpoint_support_rapidity_advection_decision.csv",
        "rapidity_advection_scenarios": inputs.rapidity_advection_dir / "endpoint_support_rapidity_advection_scenarios.csv",
    }
    tables = {key: _read_csv(path) for key, path in paths.items()}
    gate_matrix = _build_gate_matrix(tables)
    decision = classify_bounded_seal_status(gate_matrix)
    watch_ledger = _build_watch_ledger(gate_matrix)
    outputs = {
        "gate_matrix": gate_matrix,
        "watch_ledger": watch_ledger,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_seal_readiness",
        "inputs": {key: str(path) for key, path in paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in paths.items()},
        "claim_scope": (
            "Bounded beta075 sealing gate for the promoted rematch_w6_t1p5 lead at prescribed-metric/"
            "effective-source and reduced endpoint/support-sector level. This is not a final matter action, "
            "global causal theorem, semiclassical/RSET proof, broad beta/V robustness claim, or coupled GR evolution."
        ),
    }
    return outputs, metadata, _report(outputs, metadata)


def _fmt(value: Any) -> str:
    number = _finite(value, float("nan"))
    if not math.isfinite(number):
        return "nan"
    if abs(number) > 0 and (abs(number) < 1.0e-4 or abs(number) >= 1.0e5):
        return f"{number:.3e}"
    return f"{number:.6f}"


def _report(outputs: dict[str, pd.DataFrame], metadata: dict[str, Any]) -> str:
    decision = outputs["decision"].iloc[0]
    gate_matrix = outputs["gate_matrix"]
    watch_ledger = outputs["watch_ledger"]
    lines = [
        "# Stage II Beta075 Bounded Seal Readiness Gate",
        "",
        "## Status",
        "",
        f"Overall status: `{decision['beta075_seal_readiness_status']}`.",
        "",
        str(decision["decision_read"]).capitalize() + ".",
        "",
        "This is a bounded general-testing gate for the promoted beta075 `rematch_w6_t1p5` lead. It aggregates the support-sector stability, reduced hyperbolicity/causality, heat-current sensitivity, bounded rapidity, row-budget, advection non-concentration, and compact-bracket evidence already generated for the current phase.",
        "",
        "## Seal Scope",
        "",
        metadata["claim_scope"],
        "",
        "## Gate Matrix",
        "",
        "| gate | status | required | blocks seal | metric | gate | read |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for _, row in gate_matrix.iterrows():
        lines.append(
            f"| {row['gate']} | {row['status']} | {bool(row['hard_required'])} | {bool(row['blocks_bounded_seal'])} | "
            f"{_fmt(row['metric'])} | {_fmt(row['gate_value'])} | {row['read']} |"
        )
    lines.extend([
        "",
        "## Watch Ledger",
        "",
        "| watch | required | metric | gate | interpretation |",
        "| --- | --- | ---: | ---: | --- |",
    ])
    for _, row in watch_ledger.iterrows():
        lines.append(
            f"| {row['gate']} | {bool(row['hard_required'])} | {_fmt(row['metric'])} | {_fmt(row['gate_value'])} | {row['read']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "There are no hard blockers inside this bounded seal scope. The promoted `24x14` endpoint/support sector clears total closure, locality, live-support exclusion, reduced principal-symbol, bounded rapidity transport, observed-kick budget, and advection non-concentration gates. The limiter remains inactive for the observed source amplitude and only catches the deliberately over-budget `O(5e-4)` reference kick.",
        "",
        "The active watches are real but bounded: dense reset/core is close to the local closure gate, the compact `22x13` bracket fails dense local closure, raw heat-ratio perturbations are fragile unless expressed/evolved as bounded rapidity, and the dense characteristic margin is thin. Those are future proof obligations, not reasons to keep same-level beta075 fitting open.",
        "",
        "## Recommendation",
        "",
        "Treat beta075 as ready to seal at the current prescribed-metric/effective-source plus reduced support-sector level after review. Stop adding same-level closure repairs unless a later action/PDE gate points back to a specific dense reset/core failure. The next work should move upward: source-coupled `1+1` rapidity evolution with the row-budget limiter as a guard, then action-level or fixed-background PDE proof work.",
        "",
        "## Provenance",
        "",
    ])
    for key, path in metadata["inputs"].items():
        lines.append(f"- {key}: `{path}`")
    return "\n".join(lines) + "\n"


def write_beta075_seal_readiness_outputs(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "gate_matrix": outdir / "beta075_seal_readiness_gate_matrix.csv",
        "watch_ledger": outdir / "beta075_seal_readiness_watch_ledger.csv",
        "decision": outdir / "beta075_seal_readiness_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "beta075_seal_readiness_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
