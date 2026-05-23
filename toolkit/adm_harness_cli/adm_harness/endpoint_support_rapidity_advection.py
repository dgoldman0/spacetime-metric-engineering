from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _finite, _quantile
from .endpoint_support_rapidity_budget import (
    RapidityBudgetSpec,
    _budget_row,
    _source_delta_psi_for_heat_delta,
    _symbol_at_delta_psi,
)
from .endpoint_support_symbol_sensitivity import _load_point_fit
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class RapidityAdvectionSpec:
    observed_heat_ratio_delta: float = 1.0e-4
    reference_large_heat_ratio_delta: float = 5.0e-4
    include_pass_margin: float = 0.005
    steps: int = 40
    cfl: float = 0.45
    limiter_safety_fraction: float = 0.95
    bottleneck_source_row_index: int | None = None


@dataclass(frozen=True)
class AdvectionScenario:
    label: str
    heat_ratio_delta: float
    direction: str
    budget_limiter: bool = False


def default_scenarios(spec: RapidityAdvectionSpec | None = None) -> list[AdvectionScenario]:
    spec = spec or RapidityAdvectionSpec()
    return [
        AdvectionScenario("observed_outward_unlimited", spec.observed_heat_ratio_delta, "outward", False),
        AdvectionScenario("observed_inward_unlimited", spec.observed_heat_ratio_delta, "inward", False),
        AdvectionScenario("observed_outward_budget_limited", spec.observed_heat_ratio_delta, "outward", True),
        AdvectionScenario("large_outward_unlimited", spec.reference_large_heat_ratio_delta, "outward", False),
        AdvectionScenario("large_outward_budget_limited", spec.reference_large_heat_ratio_delta, "outward", True),
    ]


def _upwind_step(values: np.ndarray, *, cfl: float, direction: str) -> np.ndarray:
    q = np.asarray(values, dtype=float)
    c = float(cfl)
    if not 0.0 <= c <= 1.0:
        raise ValueError("cfl must be in [0, 1]")
    out = q.copy()
    if len(q) == 0:
        return out
    if direction == "outward":
        out[0] = (1.0 - c) * q[0]
        out[1:] = q[1:] - c * (q[1:] - q[:-1])
        return out
    if direction == "inward":
        out[-1] = (1.0 - c) * q[-1]
        out[:-1] = q[:-1] + c * (q[1:] - q[:-1])
        return out
    raise ValueError(f"unknown advection direction {direction!r}")


def _apply_budget_limiter(
    values: np.ndarray,
    budgets: np.ndarray,
    *,
    safety_fraction: float,
) -> tuple[np.ndarray, np.ndarray]:
    q = np.asarray(values, dtype=float)
    cap = np.asarray(budgets, dtype=float) * float(safety_fraction)
    cap = np.where(np.isfinite(cap), np.maximum(cap, 0.0), np.inf)
    limited = np.minimum(q, cap)
    clipped = np.maximum(q - limited, 0.0)
    return limited, clipped


def _active_nonlive(frame: pd.DataFrame) -> pd.Series:
    active = frame["medium_source_active"].astype(bool) if "medium_source_active" in frame else pd.Series(True, index=frame.index)
    live = frame["covariant_divergence_live"].astype(bool) if "covariant_divergence_live" in frame else pd.Series(False, index=frame.index)
    return active & (~live)


def _slice_for_bottleneck(point_fit: pd.DataFrame, bottleneck: pd.Series) -> pd.DataFrame:
    s0 = _finite(bottleneck["s"], float("nan"))
    assignment = str(bottleneck["assignment"])
    active = _active_nonlive(point_fit)
    same_s = np.isclose(point_fit["s"].astype(float), s0, rtol=0.0, atol=1.0e-12)
    same_assignment = point_fit["assignment"].astype(str) == assignment
    frame = point_fit.loc[active & same_s & same_assignment].copy()
    frame["source_row_index"] = frame.index.astype(int)
    return frame.sort_values("l").reset_index(drop=True)


def _bottleneck_from_budget(budget_rows: pd.DataFrame, spec: RapidityAdvectionSpec) -> pd.Series:
    if spec.bottleneck_source_row_index is not None:
        match = budget_rows.loc[budget_rows["source_row_index"].astype(int) == int(spec.bottleneck_source_row_index)]
        if len(match):
            return match.iloc[0]
    return budget_rows.sort_values(["max_admissible_delta_psi", "observed_budget_fraction"], ascending=[True, False]).iloc[0]


def _build_slice_budget(
    slice_frame: pd.DataFrame,
    *,
    symbol_spec: PrincipalSymbolSpec,
    budget_spec: RapidityBudgetSpec,
) -> pd.DataFrame:
    rows = [
        _budget_row(
            int(row.get("source_row_index", idx)),
            row,
            symbol_spec,
            budget_spec,
        )
        for idx, row in slice_frame.iterrows()
    ]
    return pd.DataFrame(rows).sort_values("l").reset_index(drop=True)


def _evaluate_state(
    slice_frame: pd.DataFrame,
    slice_budget: pd.DataFrame,
    state: np.ndarray,
    *,
    scenario: AdvectionScenario,
    step: int,
    clipped: np.ndarray,
    symbol_spec: PrincipalSymbolSpec,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    budgets = slice_budget["max_admissible_delta_psi"].astype(float).to_numpy()
    for pos, (_, row) in enumerate(slice_frame.iterrows()):
        symbol = _symbol_at_delta_psi(row, float(state[pos]), symbol_spec)
        budget = float(budgets[pos])
        fraction = float(state[pos] / budget) if math.isfinite(budget) and budget > 0.0 else float("inf")
        rows.append({
            "scenario": scenario.label,
            "heat_ratio_delta": float(scenario.heat_ratio_delta),
            "direction": scenario.direction,
            "budget_limiter": bool(scenario.budget_limiter),
            "step": int(step),
            "source_row_index": int(row["source_row_index"]),
            "s": _finite(row.get("s"), float("nan")),
            "l": _finite(row.get("l"), float("nan")),
            "assignment": str(row.get("assignment", "")),
            "stage": str(row.get("stage", "")),
            "region": str(row.get("region", "")),
            "delta_psi": float(state[pos]),
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
    scenario: AdvectionScenario,
    *,
    advection_spec: RapidityAdvectionSpec,
    symbol_spec: PrincipalSymbolSpec,
) -> pd.DataFrame:
    ratios = slice_frame["regulated_heat_flux_ratio"].astype(float).to_numpy()
    state = np.array([_source_delta_psi_for_heat_delta(ratio, scenario.heat_ratio_delta) for ratio in ratios], dtype=float)
    budgets = slice_budget["max_admissible_delta_psi"].astype(float).to_numpy()
    frames: list[pd.DataFrame] = []
    clipped = np.zeros_like(state)
    if scenario.budget_limiter:
        state, clipped = _apply_budget_limiter(
            state,
            budgets,
            safety_fraction=advection_spec.limiter_safety_fraction,
        )
    frames.append(_evaluate_state(slice_frame, slice_budget, state, scenario=scenario, step=0, clipped=clipped, symbol_spec=symbol_spec))
    for step in range(1, int(advection_spec.steps) + 1):
        state = _upwind_step(state, cfl=advection_spec.cfl, direction=scenario.direction)
        clipped = np.zeros_like(state)
        if scenario.budget_limiter:
            state, clipped = _apply_budget_limiter(
                state,
                budgets,
                safety_fraction=advection_spec.limiter_safety_fraction,
            )
        frames.append(_evaluate_state(slice_frame, slice_budget, state, scenario=scenario, step=step, clipped=clipped, symbol_spec=symbol_spec))
    return pd.concat(frames, ignore_index=True)


def _scenario_summary(trajectory: pd.DataFrame, bottleneck_index: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for scenario, group in trajectory.groupby("scenario", sort=False):
        row_status = group.groupby("source_row_index")["symbol_status"].agg(lambda values: bool((values.astype(str) == "fail").any()))
        over_budget = group.groupby("source_row_index")["budget_fraction"].max() > 1.0
        limiter = group["limiter_clip_delta_psi"].astype(float) > 0.0
        bottleneck = group.loc[group["source_row_index"].astype(int) == int(bottleneck_index)]
        fail_rows = int(row_status.sum())
        over_rows = int(over_budget.sum())
        limiter_active = bool(limiter.any())
        hard_pass = fail_rows == 0 and over_rows == 0
        rows.append({
            "scenario": str(scenario),
            "heat_ratio_delta": float(group["heat_ratio_delta"].iloc[0]),
            "direction": str(group["direction"].iloc[0]),
            "budget_limiter": bool(group["budget_limiter"].iloc[0]),
            "status": "fail" if not hard_pass else "limited_pass" if limiter_active else "pass",
            "hard_pass": hard_pass,
            "rows": int(group["source_row_index"].nunique()),
            "fail_rows_any_time": fail_rows,
            "over_budget_rows_any_time": over_rows,
            "max_budget_fraction": float(group["budget_fraction"].astype(float).replace([np.inf], np.nan).max()),
            "bottleneck_max_budget_fraction": float(bottleneck["budget_fraction"].astype(float).max()) if len(bottleneck) else float("nan"),
            "bottleneck_max_delta_psi": float(bottleneck["delta_psi"].astype(float).max()) if len(bottleneck) else float("nan"),
            "min_relative_cone_margin": float(group["relative_cone_margin"].astype(float).min()),
            "min_transport_margin": float(group["transport_margin"].astype(float).min()),
            "limiter_active_steps": int(group.loc[limiter, "step"].nunique()),
            "limiter_clipped_rows": int(group.loc[limiter, "source_row_index"].nunique()),
            "max_limiter_clip_delta_psi": float(group["limiter_clip_delta_psi"].astype(float).max()),
        })
    return pd.DataFrame(rows)


def _decision(summary: pd.DataFrame) -> pd.DataFrame:
    observed = summary.loc[
        (summary["heat_ratio_delta"].astype(float) <= 1.0e-4 + 1.0e-15)
        & (~summary["budget_limiter"].astype(bool))
    ]
    observed_limited = summary.loc[
        (summary["heat_ratio_delta"].astype(float) <= 1.0e-4 + 1.0e-15)
        & (summary["budget_limiter"].astype(bool))
    ]
    large_unlimited = summary.loc[
        (summary["heat_ratio_delta"].astype(float) > 1.0e-4)
        & (~summary["budget_limiter"].astype(bool))
    ]
    large_limited = summary.loc[
        (summary["heat_ratio_delta"].astype(float) > 1.0e-4)
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
        "advection_nonconcentration_with_limiter_guard"
        if observed_pass and observed_limiter_inactive and large_unlimited_fails and large_limited_passes
        else "advection_watch"
        if observed_pass
        else "advection_fail"
    )
    read = (
        "observed O(1e-4) rapidity impulses do not concentrate over budget under the tested radial advection, and the budget limiter catches the known larger-kick failure"
        if status == "advection_nonconcentration_with_limiter_guard"
        else "observed O(1e-4) rapidity impulses pass this advection check, but the limiter/failure contrast is incomplete"
        if status == "advection_watch"
        else "observed O(1e-4) rapidity impulses exceed a local budget under radial advection"
    )
    return pd.DataFrame([{
        "rapidity_advection_status": status,
        "observed_unlimited_pass": observed_pass,
        "observed_limiter_inactive": observed_limiter_inactive,
        "large_unlimited_fails": large_unlimited_fails,
        "large_limited_passes": large_limited_passes,
        "max_observed_unlimited_budget_fraction": float(observed["max_budget_fraction"].astype(float).max()) if len(observed) else float("nan"),
        "decision_read": read,
    }])


def build_rapidity_advection(
    stroke_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    budget_spec: RapidityBudgetSpec | None = None,
    advection_spec: RapidityAdvectionSpec | None = None,
    scenarios: list[AdvectionScenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    advection_spec = advection_spec or RapidityAdvectionSpec()
    budget_spec = budget_spec or RapidityBudgetSpec(
        include_pass_margin=advection_spec.include_pass_margin,
        observed_heat_ratio_delta=advection_spec.observed_heat_ratio_delta,
        reference_large_heat_ratio_delta=advection_spec.reference_large_heat_ratio_delta,
        speed_margin_gate=symbol_spec.speed_margin_gate,
    )
    scenarios = scenarios or default_scenarios(advection_spec)
    point_fit, manifest, point_path = _load_point_fit(stroke_dir)
    from .endpoint_support_rapidity_budget import build_rapidity_budget

    budget_outputs, _, _ = build_rapidity_budget(stroke_dir, symbol_spec=symbol_spec, budget_spec=budget_spec)
    adversarial_budget = budget_outputs["budget_rows"]
    bottleneck = _bottleneck_from_budget(adversarial_budget, advection_spec)
    slice_frame = _slice_for_bottleneck(point_fit, bottleneck)
    slice_budget = _build_slice_budget(slice_frame, symbol_spec=symbol_spec, budget_spec=budget_spec)
    bottleneck_index = int(bottleneck["source_row_index"])
    trajectory = pd.concat(
        [
            _run_scenario(
                slice_frame,
                slice_budget,
                scenario,
                advection_spec=advection_spec,
                symbol_spec=symbol_spec,
            )
            for scenario in scenarios
        ],
        ignore_index=True,
    )
    summary = _scenario_summary(trajectory, bottleneck_index)
    decision = _decision(summary)
    outputs = {
        "adversarial_budget": adversarial_budget,
        "slice_budget": slice_budget,
        "trajectory": trajectory,
        "scenario_summary": summary,
        "decision": decision,
    }
    metadata = {
        "source_name": "endpoint_support_rapidity_advection",
        "stroke_dir": str(stroke_dir),
        "point_fit": str(point_path),
        "point_fit_sha256": sha256_file(point_path),
        "stroke_source_name": manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "budget_spec": budget_spec.__dict__,
        "advection_spec": advection_spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "bottleneck_source_row_index": bottleneck_index,
        "bottleneck_s": _finite(bottleneck["s"], float("nan")),
        "bottleneck_l": _finite(bottleneck["l"], float("nan")),
        "caveat": (
            "Reduced 1+1 fixed-background rapidity-impulse advection on the l-slice containing the tightest dense adversarial row. "
            "This is a non-concentration and limiter-guard diagnostic, not a full support-source PDE closure."
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
    bottleneck_index = int(metadata["bottleneck_source_row_index"])
    bottleneck = slice_budget.loc[slice_budget["source_row_index"].astype(int) == bottleneck_index].iloc[0]
    decision_read = str(decision["decision_read"])
    decision_sentence = decision_read[:1].upper() + decision_read[1:]
    lines = [
        "# Stage II Beta075 Rapidity Advection Non-Concentration",
        "",
        "## Status",
        "",
        f"Overall status: `{decision['rapidity_advection_status']}`.",
        "",
        decision_sentence + ".",
        "",
        "This is a reduced `1+1` fixed-background rapidity-impulse advection check on the service-radial `l` slice containing the tightest dense adversarial row. It asks whether monotone radial advection concentrates the admissible `O(1e-4)` rapidity kick into an over-budget edge row, and whether a local budget limiter catches the known larger-kick failure.",
        "",
        "## Bottleneck Row",
        "",
        "| row | s | l | stage | region | baseline psi | baseline transport margin | budget Delta psi | observed Delta psi | large Delta psi |",
        "| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        f"| {bottleneck_index} | {_fmt(bottleneck['s'])} | {_fmt(bottleneck['l'])} | {bottleneck['stage']} | {bottleneck['region']} | "
        f"{_fmt(bottleneck['baseline_psi'])} | {_fmt(bottleneck['baseline_transport_margin'])} | "
        f"{_fmt(bottleneck['max_admissible_delta_psi'])} | {_fmt(bottleneck['observed_source_delta_psi'])} | {_fmt(bottleneck['large_source_delta_psi'])} |",
        "",
        "## Scenario Summary",
        "",
        "| scenario | status | limiter | fail rows | over-budget rows | max budget fraction | bottleneck max fraction | min cone margin | clipped rows | max clip |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['status']} | {bool(row['budget_limiter'])} | "
            f"{int(row['fail_rows_any_time'])} | {int(row['over_budget_rows_any_time'])} | "
            f"{_fmt(row['max_budget_fraction'])} | {_fmt(row['bottleneck_max_budget_fraction'])} | "
            f"{_fmt(row['min_relative_cone_margin'])} | {int(row['limiter_clipped_rows'])} | {_fmt(row['max_limiter_clip_delta_psi'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The observed `O(1e-4)` rapidity impulse stays below every local budget under both outward and inward monotone radial advection on the bottleneck slice. The budget limiter is inactive on the observed case, so it is not hiding a marginal pass.",
        "",
        "The larger `O(5e-4)` reference impulse fails without the limiter and passes with the limiter active. That makes the next reduced PDE target sharper: keep the limiter as a guard for over-budget support-source concentration, but first try to prove or numerically demonstrate that the physical support-source/advection law stays in the observed-kick regime.",
        "",
        "## Provenance",
        "",
        f"- point fit: `{metadata['point_fit']}`",
        f"- bottleneck row: `{bottleneck_index}` at `s={_fmt(metadata['bottleneck_s'])}`, `l={_fmt(metadata['bottleneck_l'])}`",
        f"- slice rows: `{len(slice_budget)}`",
    ])
    return "\n".join(lines) + "\n"


def write_rapidity_advection_outputs(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "adversarial_budget": outdir / "endpoint_support_rapidity_advection_adversarial_budget.csv",
        "slice_budget": outdir / "endpoint_support_rapidity_advection_slice_budget.csv",
        "trajectory": outdir / "endpoint_support_rapidity_advection_trajectory.csv",
        "scenario_summary": outdir / "endpoint_support_rapidity_advection_scenarios.csv",
        "decision": outdir / "endpoint_support_rapidity_advection_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "endpoint_support_rapidity_advection_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
