from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _finite
from .endpoint_support_rapidity_advection import (
    _apply_budget_limiter,
    _bottleneck_from_budget,
    _build_slice_budget,
    _slice_for_bottleneck,
    _upwind_step,
)
from .endpoint_support_rapidity_budget import (
    RapidityBudgetSpec,
    _budget_row,
    _source_delta_psi_for_heat_delta,
    _symbol_at_delta_psi,
)
from .endpoint_support_symbol_sensitivity import _select_adversarial_rows
from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


@dataclass(frozen=True)
class SupportSourceDynamicsSpec:
    observed_heat_ratio_delta: float = 1.0e-4
    reference_large_heat_ratio_delta: float = 5.0e-4
    include_pass_margin: float = 0.005
    steps: int = 40
    cfl: float = 0.45
    limiter_safety_fraction: float = 0.95
    bottleneck_source_row_index: int | None = None
    source_column: str = "candidate_support_abs_PF_density"
    source_smoothing_passes: int = 0
    temporal_profile: str = "raised_cosine"


@dataclass(frozen=True)
class SupportSourceScenario:
    label: str
    heat_ratio_delta: float
    direction: str
    budget_limiter: bool = False
    source_scale: float = 1.0
    advection: bool = True


def default_scenarios(spec: SupportSourceDynamicsSpec | None = None) -> list[SupportSourceScenario]:
    spec = spec or SupportSourceDynamicsSpec()
    return [
        SupportSourceScenario("observed_source_outward_unlimited", spec.observed_heat_ratio_delta, "outward", False),
        SupportSourceScenario("observed_source_inward_unlimited", spec.observed_heat_ratio_delta, "inward", False),
        SupportSourceScenario("observed_source_outward_budget_limited", spec.observed_heat_ratio_delta, "outward", True),
        SupportSourceScenario("large_source_outward_unlimited", spec.reference_large_heat_ratio_delta, "outward", False),
        SupportSourceScenario("large_source_outward_budget_limited", spec.reference_large_heat_ratio_delta, "outward", True),
    ]


def _load_closure_dir(closure_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = closure_dir / "endpoint_support_total_closure_manifest.json"
    manifest: dict[str, Any] = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    files = manifest.get("files", {})
    point_path = resolve_manifest_path(
        closure_dir,
        files.get("point_closure", "endpoint_support_total_closure_point_closure.csv"),
    )
    return pd.read_csv(point_path), manifest, point_path


def _source_column(frame: pd.DataFrame, preferred: str) -> str:
    candidates = [
        preferred,
        "candidate_support_abs_PF_density",
        "fit_abs_PF_density",
        "target_abs_PF_density",
    ]
    for column in candidates:
        if column in frame:
            return column
    raise ValueError("closure surface does not include a usable support-source density column")


def _temporal_envelope(steps: int, profile: str) -> np.ndarray:
    count = int(steps)
    if count <= 0:
        return np.zeros(0, dtype=float)
    if profile == "flat":
        return np.full(count, 1.0 / count, dtype=float)
    if profile == "raised_cosine":
        x = (np.arange(count, dtype=float) + 0.5) / count
        weights = 0.5 - 0.5 * np.cos(2.0 * math.pi * x)
        total = float(weights.sum())
        return weights / total if total > 0.0 else np.full(count, 1.0 / count, dtype=float)
    raise ValueError(f"unknown temporal profile {profile!r}")


def _smooth_profile(values: np.ndarray, passes: int) -> np.ndarray:
    out = np.asarray(values, dtype=float).copy()
    for _ in range(max(0, int(passes))):
        if len(out) < 2:
            return out
        smooth = out.copy()
        smooth[0] = 0.75 * out[0] + 0.25 * out[1]
        smooth[-1] = 0.75 * out[-1] + 0.25 * out[-2]
        if len(out) > 2:
            smooth[1:-1] = 0.25 * out[:-2] + 0.5 * out[1:-1] + 0.25 * out[2:]
        out = smooth
    return out


def _source_delta_profile(
    slice_frame: pd.DataFrame,
    bottleneck: pd.Series,
    scenario: SupportSourceScenario,
    spec: SupportSourceDynamicsSpec,
) -> tuple[np.ndarray, pd.DataFrame]:
    column = _source_column(slice_frame, spec.source_column)
    raw = np.abs(slice_frame[column].astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy())
    source = _smooth_profile(raw, spec.source_smoothing_passes)
    bottleneck_index = int(bottleneck["source_row_index"])
    match = np.flatnonzero(slice_frame["source_row_index"].astype(int).to_numpy() == bottleneck_index)
    if len(match):
        normalizer_pos = int(match[0])
    else:
        normalizer_pos = int(np.argmax(source)) if len(source) else 0
    normalizer = float(source[normalizer_pos]) if len(source) else 0.0
    if not math.isfinite(normalizer) or normalizer <= 0.0:
        normalizer_pos = int(np.argmax(source)) if len(source) else 0
        normalizer = float(source[normalizer_pos]) if len(source) else 0.0
    if not math.isfinite(normalizer) or normalizer <= 0.0:
        normalized = np.zeros_like(source)
    else:
        normalized = source / normalizer
    bottleneck_ratio = _finite(bottleneck.get("baseline_heat_ratio"), float("nan"))
    if not math.isfinite(bottleneck_ratio) and len(match):
        bottleneck_ratio = _finite(slice_frame.iloc[normalizer_pos].get("regulated_heat_flux_ratio"), 0.0)
    target_delta = _source_delta_psi_for_heat_delta(
        bottleneck_ratio,
        float(scenario.heat_ratio_delta) * float(scenario.source_scale),
    )
    delta_profile = normalized * float(target_delta)
    profile = slice_frame[["source_row_index", "s", "l", "assignment", "stage", "region"]].copy()
    profile["source_column"] = column
    profile["raw_source_density"] = raw
    profile["smoothed_source_density"] = source
    profile["normalized_source_density"] = normalized
    profile["scenario"] = scenario.label
    profile["target_bottleneck_delta_psi"] = float(target_delta)
    profile["source_delta_psi_integral"] = delta_profile
    profile["normalizer_source_row_index"] = int(slice_frame.iloc[normalizer_pos]["source_row_index"]) if len(source) else -1
    profile["normalizer_source_density"] = normalizer
    profile["normalizer_is_bottleneck"] = bool(len(match) and int(match[0]) == normalizer_pos)
    return delta_profile, profile


def _evaluate_state(
    slice_frame: pd.DataFrame,
    slice_budget: pd.DataFrame,
    state: np.ndarray,
    *,
    scenario: SupportSourceScenario,
    step: int,
    source_increment: np.ndarray,
    clipped: np.ndarray,
    symbol_spec: PrincipalSymbolSpec,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    budgets = slice_budget["max_admissible_delta_psi"].astype(float).to_numpy()
    for pos, (_, row) in enumerate(slice_frame.iterrows()):
        delta_psi = float(state[pos])
        symbol = _symbol_at_delta_psi(row, delta_psi, symbol_spec)
        budget = float(budgets[pos])
        fraction = float(delta_psi / budget) if math.isfinite(budget) and budget > 0.0 else float("inf")
        rows.append({
            "scenario": scenario.label,
            "heat_ratio_delta": float(scenario.heat_ratio_delta),
            "direction": scenario.direction,
            "budget_limiter": bool(scenario.budget_limiter),
            "source_scale": float(scenario.source_scale),
            "advection": bool(scenario.advection),
            "step": int(step),
            "source_row_index": int(row["source_row_index"]),
            "s": _finite(row.get("s"), float("nan")),
            "l": _finite(row.get("l"), float("nan")),
            "assignment": str(row.get("assignment", "")),
            "stage": str(row.get("stage", "")),
            "region": str(row.get("region", "")),
            "delta_psi": delta_psi,
            "source_increment_delta_psi": float(source_increment[pos]),
            "budget_delta_psi": budget,
            "budget_fraction": fraction,
            "limiter_clip_delta_psi": float(clipped[pos]),
            "symbol_status": str(symbol.get("symbol_status", "")),
            "hard_symbol_pass": bool(symbol.get("hard_symbol_pass", False)),
            "relative_cone_margin": _finite(symbol.get("relative_cone_margin"), float("nan")),
            "transport_margin": _finite(symbol.get("transport_margin"), float("nan")),
            "regulated_heat_flux_ratio": _finite(symbol.get("regulated_heat_flux_ratio"), float("nan")),
        })
    return pd.DataFrame(rows)


def _run_scenario(
    slice_frame: pd.DataFrame,
    slice_budget: pd.DataFrame,
    bottleneck: pd.Series,
    scenario: SupportSourceScenario,
    *,
    dynamics_spec: SupportSourceDynamicsSpec,
    symbol_spec: PrincipalSymbolSpec,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    envelope = _temporal_envelope(dynamics_spec.steps, dynamics_spec.temporal_profile)
    source_profile, profile_rows = _source_delta_profile(slice_frame, bottleneck, scenario, dynamics_spec)
    state = np.zeros(len(slice_frame), dtype=float)
    frames = [
        _evaluate_state(
            slice_frame,
            slice_budget,
            state,
            scenario=scenario,
            step=0,
            source_increment=np.zeros_like(state),
            clipped=np.zeros_like(state),
            symbol_spec=symbol_spec,
        )
    ]
    budgets = slice_budget["max_admissible_delta_psi"].astype(float).to_numpy()
    for step, weight in enumerate(envelope, start=1):
        source_increment = source_profile * float(weight)
        state = state + source_increment
        if scenario.advection:
            state = _upwind_step(state, cfl=dynamics_spec.cfl, direction=scenario.direction)
        clipped = np.zeros_like(state)
        if scenario.budget_limiter:
            state, clipped = _apply_budget_limiter(
                state,
                budgets,
                safety_fraction=dynamics_spec.limiter_safety_fraction,
            )
        frames.append(
            _evaluate_state(
                slice_frame,
                slice_budget,
                state,
                scenario=scenario,
                step=step,
                source_increment=source_increment,
                clipped=clipped,
                symbol_spec=symbol_spec,
            )
        )
    return pd.concat(frames, ignore_index=True), profile_rows


def _scenario_summary(trajectory: pd.DataFrame, bottleneck_index: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for scenario, group in trajectory.groupby("scenario", sort=False):
        row_fail = group.groupby("source_row_index")["symbol_status"].agg(lambda values: bool((values.astype(str) == "fail").any()))
        over_budget = group.groupby("source_row_index")["budget_fraction"].max() > 1.0
        limiter = group["limiter_clip_delta_psi"].astype(float) > 0.0
        bottleneck = group.loc[group["source_row_index"].astype(int) == int(bottleneck_index)]
        fail_rows = int(row_fail.sum())
        over_rows = int(over_budget.sum())
        limiter_active = bool(limiter.any())
        hard_pass = fail_rows == 0 and over_rows == 0
        rows.append({
            "scenario": str(scenario),
            "heat_ratio_delta": float(group["heat_ratio_delta"].iloc[0]),
            "direction": str(group["direction"].iloc[0]),
            "budget_limiter": bool(group["budget_limiter"].iloc[0]),
            "source_scale": float(group["source_scale"].iloc[0]),
            "status": "fail" if not hard_pass else "limited_pass" if limiter_active else "pass",
            "hard_pass": hard_pass,
            "rows": int(group["source_row_index"].nunique()),
            "fail_rows_any_time": fail_rows,
            "over_budget_rows_any_time": over_rows,
            "max_budget_fraction": float(group["budget_fraction"].astype(float).replace([np.inf], np.nan).max()),
            "bottleneck_max_budget_fraction": float(bottleneck["budget_fraction"].astype(float).max()) if len(bottleneck) else float("nan"),
            "bottleneck_final_delta_psi": float(bottleneck.sort_values("step")["delta_psi"].iloc[-1]) if len(bottleneck) else float("nan"),
            "max_delta_psi": float(group["delta_psi"].astype(float).max()),
            "min_relative_cone_margin": float(group["relative_cone_margin"].astype(float).min()),
            "min_transport_margin": float(group["transport_margin"].astype(float).min()),
            "limiter_active_steps": int(group.loc[limiter, "step"].nunique()),
            "limiter_clipped_rows": int(group.loc[limiter, "source_row_index"].nunique()),
            "max_limiter_clip_delta_psi": float(group["limiter_clip_delta_psi"].astype(float).max()),
        })
    return pd.DataFrame(rows)


def _decision(summary: pd.DataFrame, observed_delta: float) -> pd.DataFrame:
    observed = summary.loc[
        (summary["heat_ratio_delta"].astype(float) <= float(observed_delta) + 1.0e-15)
        & (~summary["budget_limiter"].astype(bool))
    ]
    observed_limited = summary.loc[
        (summary["heat_ratio_delta"].astype(float) <= float(observed_delta) + 1.0e-15)
        & (summary["budget_limiter"].astype(bool))
    ]
    large_unlimited = summary.loc[
        (summary["heat_ratio_delta"].astype(float) > float(observed_delta) + 1.0e-15)
        & (~summary["budget_limiter"].astype(bool))
    ]
    large_limited = summary.loc[
        (summary["heat_ratio_delta"].astype(float) > float(observed_delta) + 1.0e-15)
        & (summary["budget_limiter"].astype(bool))
    ]
    observed_pass = bool(len(observed) and observed["hard_pass"].astype(bool).all())
    observed_limiter_inactive = bool(
        not len(observed_limited)
        or (
            observed_limited["hard_pass"].astype(bool).all()
            and int(observed_limited["limiter_clipped_rows"].astype(int).max()) == 0
        )
    )
    large_unlimited_fails = bool(len(large_unlimited) and (~large_unlimited["hard_pass"].astype(bool)).any())
    large_limited_passes = bool(len(large_limited) and large_limited["hard_pass"].astype(bool).all())
    status = (
        "coupled_support_source_clean"
        if observed_pass and observed_limiter_inactive and large_unlimited_fails and large_limited_passes
        else "coupled_support_source_watch"
        if observed_pass and observed_limiter_inactive
        else "coupled_support_source_fail"
    )
    read = (
        "the observed support-source amplitude stays under every cone/rapidity budget during coupled source-advection evolution, while the larger reference source still trips the guard"
        if status == "coupled_support_source_clean"
        else "the observed support-source amplitude survives coupled evolution, but the large-source limiter contrast is incomplete"
        if status == "coupled_support_source_watch"
        else "the observed support-source amplitude drives at least one row through the local cone/rapidity budget during coupled evolution"
    )
    return pd.DataFrame([{
        "support_source_dynamics_status": status,
        "observed_unlimited_pass": observed_pass,
        "observed_limiter_inactive": observed_limiter_inactive,
        "large_unlimited_fails": large_unlimited_fails,
        "large_limited_passes": large_limited_passes,
        "max_observed_unlimited_budget_fraction": float(observed["max_budget_fraction"].astype(float).max()) if len(observed) else float("nan"),
        "decision_read": read,
    }])


def build_support_source_dynamics(
    closure_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    budget_spec: RapidityBudgetSpec | None = None,
    dynamics_spec: SupportSourceDynamicsSpec | None = None,
    scenarios: list[SupportSourceScenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    dynamics_spec = dynamics_spec or SupportSourceDynamicsSpec()
    budget_spec = budget_spec or RapidityBudgetSpec(
        include_pass_margin=dynamics_spec.include_pass_margin,
        observed_heat_ratio_delta=dynamics_spec.observed_heat_ratio_delta,
        reference_large_heat_ratio_delta=dynamics_spec.reference_large_heat_ratio_delta,
        speed_margin_gate=symbol_spec.speed_margin_gate,
    )
    scenarios = scenarios or default_scenarios(dynamics_spec)
    point_closure, manifest, point_path = _load_closure_dir(closure_dir)
    selected = _select_adversarial_rows(
        point_closure,
        symbol_spec,
        include_pass_margin=dynamics_spec.include_pass_margin,
    )
    budget_rows = pd.DataFrame([
        _budget_row(
            int(row.get("source_row_index", idx)),
            row,
            symbol_spec,
            budget_spec,
        )
        for idx, row in selected.iterrows()
    ]).sort_values(["max_admissible_delta_psi", "observed_budget_fraction"], ascending=[True, False])
    bottleneck = _bottleneck_from_budget(budget_rows, dynamics_spec)
    slice_frame = _slice_for_bottleneck(point_closure, bottleneck)
    slice_budget = _build_slice_budget(slice_frame, symbol_spec=symbol_spec, budget_spec=budget_spec)
    bottleneck_index = int(bottleneck["source_row_index"])
    trajectory_frames: list[pd.DataFrame] = []
    profile_frames: list[pd.DataFrame] = []
    for scenario in scenarios:
        trajectory, profile = _run_scenario(
            slice_frame,
            slice_budget,
            bottleneck,
            scenario,
            dynamics_spec=dynamics_spec,
            symbol_spec=symbol_spec,
        )
        trajectory_frames.append(trajectory)
        profile_frames.append(profile)
    trajectory = pd.concat(trajectory_frames, ignore_index=True) if trajectory_frames else pd.DataFrame()
    source_profile = pd.concat(profile_frames, ignore_index=True) if profile_frames else pd.DataFrame()
    summary = _scenario_summary(trajectory, bottleneck_index)
    decision = _decision(summary, dynamics_spec.observed_heat_ratio_delta)
    outputs = {
        "adversarial_budget": budget_rows,
        "slice_budget": slice_budget,
        "source_profile": source_profile,
        "trajectory": trajectory,
        "scenario_summary": summary,
        "decision": decision,
    }
    metadata = {
        "source_name": "endpoint_support_source_dynamics",
        "closure_dir": str(closure_dir),
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": manifest.get("source_name", ""),
        "stroke_dir": manifest.get("stroke_dir", ""),
        "symbol_spec": symbol_spec.__dict__,
        "budget_spec": budget_spec.__dict__,
        "dynamics_spec": dynamics_spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "bottleneck_source_row_index": bottleneck_index,
        "bottleneck_s": _finite(bottleneck["s"], float("nan")),
        "bottleneck_l": _finite(bottleneck["l"], float("nan")),
        "caveat": (
            "Reduced 1+1 fixed-background support-source dynamics on the l-slice containing the tightest dense adversarial row. "
            "The fitted support-closure source supplies a time-distributed rapidity drive that is advected and checked against local cone budgets; this is not a full Einstein-matter evolution."
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
    summary = outputs["scenario_summary"]
    slice_budget = outputs["slice_budget"]
    profile = outputs["source_profile"]
    bottleneck_index = int(metadata["bottleneck_source_row_index"])
    bottleneck = slice_budget.loc[slice_budget["source_row_index"].astype(int) == bottleneck_index].iloc[0]
    first_profile = profile.loc[profile["scenario"].astype(str) == str(summary["scenario"].iloc[0])] if len(profile) and len(summary) else pd.DataFrame()
    normalizer = first_profile.loc[first_profile["source_row_index"].astype(int) == int(first_profile["normalizer_source_row_index"].iloc[0])].head(1) if len(first_profile) else pd.DataFrame()
    decision_read = str(decision["decision_read"])
    decision_sentence = decision_read[:1].upper() + decision_read[1:]
    large_unlimited = summary.loc[
        (summary["heat_ratio_delta"].astype(float) > float(metadata["dynamics_spec"]["observed_heat_ratio_delta"]) + 1.0e-15)
        & (~summary["budget_limiter"].astype(bool))
    ]
    max_large_fraction = (
        float(large_unlimited["max_budget_fraction"].astype(float).max()) if len(large_unlimited) else float("nan")
    )
    large_guard_text = (
        "The larger-reference rows still serve as a guardrail here: they fail without the limiter and pass only when the budget guard clips the over-large source. That contrast shows the limiter is active as a diagnostic, not as decoration."
        if bool(decision["large_unlimited_fails"])
        else "The distributed larger-reference source does not reproduce the old instant-impulse failure; it stays below the local budget without limiter clipping. That is favorable for the coupled source profile, but it leaves the limiter-contrast guard incomplete and keeps this at watch level."
    )
    lines = [
        "# Stage II Beta075 Coupled Support-Source Dynamics",
        "",
        "## Status",
        "",
        f"Overall status: `{decision['support_source_dynamics_status']}`.",
        "",
        decision_sentence + ".",
        "",
        "This is a reduced `1+1` fixed-background evolution on the bottleneck service-radial slice. The sealed support closure supplies a fitted `P/F` support-source profile, the profile is injected through a normalized time pulse, and the resulting rapidity perturbation is advected while the existing local cone budget remains the hard gate.",
        "",
        "## Bottleneck And Source Normalization",
        "",
        "| row | s | l | stage | region | baseline psi | budget Delta psi | observed source Delta psi | large source Delta psi |",
        "| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |",
        f"| {bottleneck_index} | {_fmt(bottleneck['s'])} | {_fmt(bottleneck['l'])} | {bottleneck['stage']} | {bottleneck['region']} | "
        f"{_fmt(bottleneck['baseline_psi'])} | {_fmt(bottleneck['max_admissible_delta_psi'])} | "
        f"{_fmt(bottleneck['observed_source_delta_psi'])} | {_fmt(bottleneck['large_source_delta_psi'])} |",
        "",
        "| source column | normalizer row | normalizer l | normalizer density | max normalized source |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    if len(first_profile):
        norm = normalizer.iloc[0] if len(normalizer) else first_profile.iloc[0]
        lines.append(
            f"| {first_profile['source_column'].iloc[0]} | {int(norm['source_row_index'])} | {_fmt(norm['l'])} | "
            f"{_fmt(norm['normalizer_source_density'])} | {_fmt(first_profile['normalized_source_density'].astype(float).max())} |"
        )
    lines.extend([
        "",
        "## Scenario Summary",
        "",
        "| scenario | status | limiter | fail rows | over-budget rows | max budget fraction | bottleneck max fraction | final bottleneck Delta psi | min cone margin | clipped rows |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['status']} | {bool(row['budget_limiter'])} | "
            f"{int(row['fail_rows_any_time'])} | {int(row['over_budget_rows_any_time'])} | "
            f"{_fmt(row['max_budget_fraction'])} | {_fmt(row['bottleneck_max_budget_fraction'])} | "
            f"{_fmt(row['bottleneck_final_delta_psi'])} | {_fmt(row['min_relative_cone_margin'])} | "
            f"{int(row['limiter_clipped_rows'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The test upgrades the previous impulse-advection check by making the support source itself the driver. Passing observed rows therefore means the closure-derived support profile can be coupled into the rapidity equation at the measured `O(1e-4)` amplitude without relying on limiter clipping.",
        "",
        large_guard_text + (f" The largest larger-reference budget fraction in this run is `{_fmt(max_large_fraction)}`." if math.isfinite(max_large_fraction) else ""),
        "",
        "## Provenance",
        "",
        f"- point closure: `{metadata['point_closure']}`",
        f"- bottleneck row: `{bottleneck_index}` at `s={_fmt(metadata['bottleneck_s'])}`, `l={_fmt(metadata['bottleneck_l'])}`",
        f"- slice rows: `{len(slice_budget)}`",
    ])
    return "\n".join(lines) + "\n"


def write_support_source_dynamics_outputs(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "adversarial_budget": outdir / "endpoint_support_source_dynamics_adversarial_budget.csv",
        "slice_budget": outdir / "endpoint_support_source_dynamics_slice_budget.csv",
        "source_profile": outdir / "endpoint_support_source_dynamics_source_profile.csv",
        "trajectory": outdir / "endpoint_support_source_dynamics_trajectory.csv",
        "scenario_summary": outdir / "endpoint_support_source_dynamics_scenarios.csv",
        "decision": outdir / "endpoint_support_source_dynamics_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "endpoint_support_source_dynamics_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
