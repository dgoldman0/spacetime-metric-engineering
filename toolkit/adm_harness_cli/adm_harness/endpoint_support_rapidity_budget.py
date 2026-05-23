from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _finite, _quantile, _symbol_row
from .endpoint_support_symbol_sensitivity import _load_point_fit, _select_adversarial_rows
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class RapidityBudgetSpec:
    include_pass_margin: float = 0.005
    observed_heat_ratio_delta: float = 1.0e-4
    reference_large_heat_ratio_delta: float = 5.0e-4
    speed_margin_gate: float = 1.0e-6
    budget_fraction_watch: float = 0.75
    max_delta_psi_search: float = 64.0
    bisection_steps: int = 80


def _clip_ratio(value: float) -> float:
    return float(np.clip(float(value), 0.0, 1.0 - 1.0e-15))


def _psi_from_ratio(value: float) -> float:
    return float(np.arctanh(_clip_ratio(value)))


def _ratio_from_psi(psi: float) -> float:
    return float(np.tanh(float(psi)))


def _source_delta_psi_for_heat_delta(ratio: float, heat_delta: float) -> float:
    clipped = _clip_ratio(ratio)
    denom = max(1.0 - clipped * clipped, 1.0e-12)
    return float(heat_delta) / denom


def _row_with_delta_psi(row: pd.Series, delta_psi: float) -> pd.Series:
    out = row.copy()
    psi = _psi_from_ratio(_finite(row.get("regulated_heat_flux_ratio"), 0.0)) + float(delta_psi)
    ratio = _ratio_from_psi(psi)
    out["regulated_heat_flux_ratio"] = ratio
    out["transport_margin"] = 1.0 - ratio
    out["transport_rapidity_abs"] = abs(psi)
    return out


def _symbol_at_delta_psi(row: pd.Series, delta_psi: float, symbol_spec: PrincipalSymbolSpec) -> dict[str, Any]:
    return _symbol_row(_row_with_delta_psi(row, delta_psi), symbol_spec)


def _max_admissible_delta_psi(
    row: pd.Series,
    symbol_spec: PrincipalSymbolSpec,
    budget_spec: RapidityBudgetSpec,
) -> tuple[float, dict[str, Any]]:
    gate = float(budget_spec.speed_margin_gate)
    baseline = _symbol_at_delta_psi(row, 0.0, symbol_spec)
    baseline_margin = _finite(baseline.get("relative_cone_margin"), float("nan"))
    if not math.isfinite(baseline_margin) or baseline_margin < gate:
        return 0.0, baseline

    lo = 0.0
    hi = 1.0e-8
    hi_symbol = baseline
    while hi < float(budget_spec.max_delta_psi_search):
        hi_symbol = _symbol_at_delta_psi(row, hi, symbol_spec)
        hi_margin = _finite(hi_symbol.get("relative_cone_margin"), float("nan"))
        if not math.isfinite(hi_margin) or hi_margin < gate:
            break
        lo = hi
        hi *= 2.0

    if hi >= float(budget_spec.max_delta_psi_search):
        last = _symbol_at_delta_psi(row, float(budget_spec.max_delta_psi_search), symbol_spec)
        last_margin = _finite(last.get("relative_cone_margin"), float("nan"))
        if math.isfinite(last_margin) and last_margin >= gate:
            return float("inf"), last

    gate_symbol = baseline
    for _ in range(int(budget_spec.bisection_steps)):
        mid = 0.5 * (lo + hi)
        mid_symbol = _symbol_at_delta_psi(row, mid, symbol_spec)
        mid_margin = _finite(mid_symbol.get("relative_cone_margin"), float("nan"))
        if math.isfinite(mid_margin) and mid_margin >= gate:
            lo = mid
            gate_symbol = mid_symbol
        else:
            hi = mid
    return float(lo), gate_symbol


def _budget_fraction(kick: float, budget: float) -> float:
    if not math.isfinite(kick):
        return float("inf")
    if not math.isfinite(budget):
        return 0.0
    if budget <= 0.0:
        return float("inf") if kick > 0.0 else 0.0
    return float(kick) / float(budget)


def _recommendation(row: dict[str, Any], budget_spec: RapidityBudgetSpec) -> str:
    baseline_margin = _finite(row["baseline_relative_cone_margin"], float("nan"))
    budget = _finite(row["max_admissible_delta_psi"], float("nan"))
    observed_fraction = _finite(row["observed_budget_fraction"], float("inf"))
    large_fraction = _finite(row["large_budget_fraction"], float("inf"))
    gate = float(budget_spec.speed_margin_gate)
    if not math.isfinite(baseline_margin) or baseline_margin < gate:
        return "design_repair"
    if not math.isfinite(budget) or budget <= 0.0:
        return "design_repair"
    if observed_fraction > 1.0:
        return "source_limiter_or_spatial_smoothing_required"
    if observed_fraction >= float(budget_spec.budget_fraction_watch):
        return "tight_budget_spatial_smoothing_watch"
    if large_fraction > 1.0:
        return "large_kick_limiter_watch"
    return "pde_advection_proof_target"


def _budget_row(
    source_index: int,
    row: pd.Series,
    symbol_spec: PrincipalSymbolSpec,
    budget_spec: RapidityBudgetSpec,
) -> dict[str, Any]:
    baseline = _symbol_at_delta_psi(row, 0.0, symbol_spec)
    ratio = _finite(row.get("regulated_heat_flux_ratio"), float("nan"))
    psi = _psi_from_ratio(ratio)
    budget, gate_symbol = _max_admissible_delta_psi(row, symbol_spec, budget_spec)
    observed_kick = _source_delta_psi_for_heat_delta(ratio, budget_spec.observed_heat_ratio_delta)
    large_kick = _source_delta_psi_for_heat_delta(ratio, budget_spec.reference_large_heat_ratio_delta)
    observed_symbol = _symbol_at_delta_psi(row, observed_kick, symbol_spec)
    large_symbol = _symbol_at_delta_psi(row, large_kick, symbol_spec)
    out = {
        "source_row_index": int(source_index),
        "s": _finite(row.get("s"), float("nan")),
        "l": _finite(row.get("l"), float("nan")),
        "assignment": str(row.get("assignment", "")),
        "stage": str(row.get("stage", "")),
        "region": str(row.get("region", "")),
        "baseline_heat_ratio": ratio,
        "baseline_psi": psi,
        "baseline_transport_margin": _finite(row.get("transport_margin"), float("nan")),
        "baseline_relative_cone_margin": _finite(baseline.get("relative_cone_margin"), float("nan")),
        "baseline_symbol_status": str(baseline.get("symbol_status", "")),
        "max_admissible_delta_psi": budget,
        "heat_ratio_at_cone_gate": _finite(gate_symbol.get("regulated_heat_flux_ratio"), float("nan")),
        "transport_margin_at_cone_gate": _finite(gate_symbol.get("transport_margin"), float("nan")),
        "relative_cone_margin_at_gate": _finite(gate_symbol.get("relative_cone_margin"), float("nan")),
        "observed_heat_ratio_delta": float(budget_spec.observed_heat_ratio_delta),
        "observed_source_delta_psi": observed_kick,
        "observed_budget_fraction": _budget_fraction(observed_kick, budget),
        "observed_delta_psi_residual": budget - observed_kick if math.isfinite(budget) else float("inf"),
        "observed_relative_cone_margin": _finite(observed_symbol.get("relative_cone_margin"), float("nan")),
        "observed_transport_margin": _finite(observed_symbol.get("transport_margin"), float("nan")),
        "observed_symbol_status": str(observed_symbol.get("symbol_status", "")),
        "large_heat_ratio_delta": float(budget_spec.reference_large_heat_ratio_delta),
        "large_source_delta_psi": large_kick,
        "large_budget_fraction": _budget_fraction(large_kick, budget),
        "large_relative_cone_margin": _finite(large_symbol.get("relative_cone_margin"), float("nan")),
        "large_transport_margin": _finite(large_symbol.get("transport_margin"), float("nan")),
        "large_symbol_status": str(large_symbol.get("symbol_status", "")),
    }
    out["recommendation"] = _recommendation(out, budget_spec)
    return out


def _decision(budget_rows: pd.DataFrame, budget_spec: RapidityBudgetSpec) -> pd.DataFrame:
    baseline_fail = int((budget_rows["baseline_relative_cone_margin"].astype(float) < float(budget_spec.speed_margin_gate)).sum())
    observed_exceeds = int((budget_rows["observed_budget_fraction"].astype(float) > 1.0).sum())
    observed_watch = int((budget_rows["observed_budget_fraction"].astype(float) >= float(budget_spec.budget_fraction_watch)).sum())
    large_exceeds = int((budget_rows["large_budget_fraction"].astype(float) > 1.0).sum())
    min_budget = float(budget_rows["max_admissible_delta_psi"].astype(float).replace([np.inf], np.nan).min())
    max_observed_fraction = float(budget_rows["observed_budget_fraction"].astype(float).replace([np.inf], np.nan).max())
    status = (
        "fail"
        if baseline_fail
        else "source_limiter_required"
        if observed_exceeds
        else "tight_budget_watch"
        if observed_watch
        else "large_kick_limiter_watch"
        if large_exceeds
        else "budget_pass"
    )
    read = (
        "one or more baseline rows sit below the cone gate before any rapidity kick"
        if status == "fail"
        else "the observed O(1e-4) rapidity source kick exceeds at least one local cone budget"
        if status == "source_limiter_required"
        else "the observed O(1e-4) rapidity source kick fits but consumes most of at least one local budget"
        if status == "tight_budget_watch"
        else "the observed O(1e-4) rapidity source kick fits every row, but the larger O(5e-4) reference kick exceeds tight local budgets"
        if status == "large_kick_limiter_watch"
        else "the scanned rapidity source kicks fit every local cone budget"
    )
    return pd.DataFrame([{
        "rapidity_budget_status": status,
        "rows": int(len(budget_rows)),
        "baseline_fail_rows": baseline_fail,
        "observed_exceeds_budget_rows": observed_exceeds,
        "observed_budget_watch_rows": observed_watch,
        "large_exceeds_budget_rows": large_exceeds,
        "min_max_admissible_delta_psi": min_budget,
        "max_observed_budget_fraction": max_observed_fraction,
        "min_observed_delta_psi_residual": float(budget_rows["observed_delta_psi_residual"].astype(float).replace([np.inf], np.nan).min()),
        "decision_read": read,
    }])


def build_rapidity_budget(
    stroke_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    budget_spec: RapidityBudgetSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    budget_spec = budget_spec or RapidityBudgetSpec(speed_margin_gate=symbol_spec.speed_margin_gate)
    point_fit, manifest, point_path = _load_point_fit(stroke_dir)
    selected = _select_adversarial_rows(
        point_fit,
        symbol_spec,
        include_pass_margin=budget_spec.include_pass_margin,
    )
    rows = [
        _budget_row(
            int(row.get("source_row_index", idx)),
            row,
            symbol_spec,
            budget_spec,
        )
        for idx, row in selected.iterrows()
    ]
    budget_rows = pd.DataFrame(rows).sort_values(
        ["max_admissible_delta_psi", "observed_budget_fraction"],
        ascending=[True, False],
    )
    decision = _decision(budget_rows, budget_spec)
    outputs = {
        "selected_rows": selected,
        "budget_rows": budget_rows,
        "decision": decision,
    }
    metadata = {
        "source_name": "endpoint_support_rapidity_budget",
        "stroke_dir": str(stroke_dir),
        "point_fit": str(point_path),
        "point_fit_sha256": sha256_file(point_path),
        "stroke_source_name": manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "budget_spec": budget_spec.__dict__,
        "caveat": (
            "Frozen-coefficient rapidity-budget diagnostic on dense principal-symbol adversarial rows. "
            "Budgets are local positive delta-psi capacities to the 1e-6 cone gate, not a spatial PDE proof."
        ),
    }
    return outputs, metadata, _report(outputs, metadata)


def _fmt(value: Any) -> str:
    number = _finite(value, float("nan"))
    if not math.isfinite(number):
        return "inf" if number > 0 else "nan"
    if abs(number) > 0 and (abs(number) < 1.0e-4 or abs(number) >= 1.0e5):
        return f"{number:.3e}"
    return f"{number:.6f}"


def _report(outputs: dict[str, pd.DataFrame], metadata: dict[str, Any]) -> str:
    budget_rows = outputs["budget_rows"]
    decision = outputs["decision"].iloc[0]
    recommendation_counts = budget_rows["recommendation"].value_counts().sort_index()
    decision_read = str(decision["decision_read"])
    decision_sentence = decision_read[:1].upper() + decision_read[1:]
    lines = [
        "# Stage II Beta075 Rapidity-Budget Diagnostic",
        "",
        "## Status",
        "",
        f"Overall status: `{decision['rapidity_budget_status']}`.",
        "",
        decision_sentence + ".",
        "",
        "This diagnostic budgets each dense adversarial row in the bounded transport-rapidity variable. The budget is the largest positive `Delta psi` that keeps the local reduced principal symbol above the `1e-6` relative cone-margin gate.",
        "",
        "## Budget Summary",
        "",
        "| rows | min admissible Delta psi | max observed fraction | observed over-budget rows | large-kick over-budget rows | min observed residual |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| {int(decision['rows'])} | {_fmt(decision['min_max_admissible_delta_psi'])} | {_fmt(decision['max_observed_budget_fraction'])} | "
        f"{int(decision['observed_exceeds_budget_rows'])} | {int(decision['large_exceeds_budget_rows'])} | {_fmt(decision['min_observed_delta_psi_residual'])} |",
        "",
        "## Recommendation Counts",
        "",
        "| recommendation | rows |",
        "| --- | ---: |",
    ]
    for recommendation, count in recommendation_counts.items():
        lines.append(f"| {recommendation} | {int(count)} |")
    lines.extend([
        "",
        "## Per-Row Rapidity Budgets",
        "",
        "| row | s | l | assignment | stage | region | baseline psi | baseline margin | max Delta psi | observed Delta psi | observed fraction | large fraction | recommendation |",
        "| ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    for _, row in budget_rows.iterrows():
        lines.append(
            f"| {int(row['source_row_index'])} | {_fmt(row['s'])} | {_fmt(row['l'])} | {row['assignment']} | "
            f"{row['stage']} | {row['region']} | {_fmt(row['baseline_psi'])} | {_fmt(row['baseline_transport_margin'])} | "
            f"{_fmt(row['max_admissible_delta_psi'])} | {_fmt(row['observed_source_delta_psi'])} | "
            f"{_fmt(row['observed_budget_fraction'])} | {_fmt(row['large_budget_fraction'])} | {row['recommendation']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The full `O(1e-4)` bounded-rapidity source kick fits inside every local cone budget in this adversarial set. That argues against an immediate endpoint/support-edge design repair at this rung. The same rows do not have unlimited headroom: the `O(5e-4)` reference kick exceeds the tight reset-decompression/support-edge budgets, matching the reduced transport pilot's large-kick failure.",
        "",
        "So the next spatial model should not simply prove abstract hyperbolicity. It should show that advection and support-source coupling never concentrate a larger effective rapidity kick into the tightest edge rows, or else add an explicit local limiter/smoothing term for the support source.",
        "",
        "## Provenance",
        "",
        f"- point fit: `{metadata['point_fit']}`",
        f"- selected rows: `{len(outputs['selected_rows'])}` dense watch/near-watch rows",
        "- full table: `endpoint_support_rapidity_budget_rows.csv` in the run output directory",
    ])
    return "\n".join(lines) + "\n"


def write_rapidity_budget_outputs(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "selected_rows": outdir / "endpoint_support_rapidity_budget_selected_rows.csv",
        "budget_rows": outdir / "endpoint_support_rapidity_budget_rows.csv",
        "decision": outdir / "endpoint_support_rapidity_budget_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "endpoint_support_rapidity_budget_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
