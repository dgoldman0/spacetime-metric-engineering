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
class TransportEvolutionSpec:
    dt: float = 0.02
    steps: int = 80
    include_pass_margin: float = 0.005
    speed_margin_gate: float = 1.0e-6
    speed_margin_watch: float = 5.0e-3


@dataclass(frozen=True)
class EvolutionScenario:
    label: str
    model: str
    heat_ratio_delta: float
    damping_rate: float


DEFAULT_SCENARIOS = [
    EvolutionScenario("raw_delta_p1e4_k0", "raw_ratio", 1.0e-4, 0.0),
    EvolutionScenario("raw_delta_p1e4_k4", "raw_ratio", 1.0e-4, 4.0),
    EvolutionScenario("rapidity_delta_p1e4_k0", "rapidity", 1.0e-4, 0.0),
    EvolutionScenario("rapidity_delta_p1e4_k1", "rapidity", 1.0e-4, 1.0),
    EvolutionScenario("rapidity_delta_p1e4_k4", "rapidity", 1.0e-4, 4.0),
    EvolutionScenario("rapidity_delta_p2p5e4_k4", "rapidity", 2.5e-4, 4.0),
    EvolutionScenario("rapidity_delta_p5e4_k4", "rapidity", 5.0e-4, 4.0),
    EvolutionScenario("rapidity_relief_m5e4_k1", "rapidity", -5.0e-4, 1.0),
]


def _clip_ratio(values: pd.Series | np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=float), 0.0, 1.0 - 1.0e-15)


def _initial_psi(ratio: np.ndarray) -> np.ndarray:
    return np.arctanh(_clip_ratio(ratio))


def _psi_kick_for_heat_delta(ratio: np.ndarray, heat_delta: float) -> np.ndarray:
    denom = np.maximum(1.0 - np.square(_clip_ratio(ratio)), 1.0e-12)
    return float(heat_delta) / denom


def _evolved_ratio(
    ratio0: np.ndarray,
    scenario: EvolutionScenario,
    time: float,
) -> tuple[np.ndarray, np.ndarray]:
    decay = math.exp(-float(scenario.damping_rate) * float(time))
    if scenario.model == "raw_ratio":
        ratio = ratio0 + float(scenario.heat_ratio_delta) * decay
        psi = np.arctanh(_clip_ratio(ratio))
        psi = np.where(ratio < 1.0, psi, np.inf)
        return ratio, psi
    if scenario.model == "rapidity":
        psi0 = _initial_psi(ratio0)
        psi = psi0 + _psi_kick_for_heat_delta(ratio0, scenario.heat_ratio_delta) * decay
        ratio = np.tanh(psi)
        return ratio, psi
    raise ValueError(f"unknown evolution model {scenario.model!r}")


def _evaluate_step(
    selected: pd.DataFrame,
    scenario: EvolutionScenario,
    time: float,
    symbol_spec: PrincipalSymbolSpec,
) -> pd.DataFrame:
    frame = selected.copy()
    ratio0 = frame["regulated_heat_flux_ratio"].astype(float).to_numpy()
    ratio, psi = _evolved_ratio(ratio0, scenario, time)
    frame["regulated_heat_flux_ratio"] = ratio
    frame["transport_margin"] = 1.0 - ratio
    frame["transport_rapidity_abs"] = psi
    rows: list[dict[str, Any]] = []
    for idx, row in frame.iterrows():
        out = _symbol_row(row, symbol_spec)
        out["source_row_index"] = int(idx)
        out["time"] = float(time)
        rows.append(out)
    return pd.DataFrame(rows)


def _scenario_summary(
    scenario: EvolutionScenario,
    trajectory: pd.DataFrame,
    spec: TransportEvolutionSpec,
) -> dict[str, Any]:
    fail = trajectory["symbol_status"].astype(str) == "fail"
    watch = trajectory["symbol_status"].astype(str) == "watch"
    grouped = trajectory.groupby("source_row_index", sort=False)
    row_min = grouped["relative_cone_margin"].min()
    row_fail = grouped["symbol_status"].agg(lambda values: bool((values.astype(str) == "fail").any()))
    row_watch = grouped["symbol_status"].agg(lambda values: bool((values.astype(str) == "watch").any()))
    min_margin = float(trajectory["relative_cone_margin"].astype(float).min()) if len(trajectory) else float("nan")
    min_transport = float(trajectory["transport_margin"].astype(float).min()) if len(trajectory) else float("nan")
    hard_pass = int(row_fail.sum()) == 0 and min_margin >= spec.speed_margin_gate and min_transport >= 0.0
    status = "fail" if not hard_pass else "watch" if (int(row_watch.sum()) > 0 or min_margin < spec.speed_margin_watch) else "pass"
    return {
        "scenario": scenario.label,
        "model": scenario.model,
        "heat_ratio_delta": float(scenario.heat_ratio_delta),
        "damping_rate": float(scenario.damping_rate),
        "symbol_status": status,
        "hard_symbol_pass": hard_pass,
        "rows": int(grouped.ngroups),
        "time_samples": int(trajectory["time"].nunique()) if len(trajectory) else 0,
        "fail_rows_any_time": int(row_fail.sum()),
        "watch_rows_any_time": int(row_watch.sum()),
        "fail_samples": int(fail.sum()),
        "watch_samples": int(watch.sum()),
        "min_relative_cone_margin": min_margin,
        "p01_row_min_relative_cone_margin": _quantile(row_min, 0.01),
        "min_transport_margin": min_transport,
        "p01_transport_margin": _quantile(trajectory["transport_margin"], 0.01),
        "p99_heat_ratio": _quantile(trajectory["regulated_heat_flux_ratio"], 0.99),
        "max_transport_rapidity_abs": float(trajectory["transport_rapidity_abs"].astype(float).replace([np.inf], np.nan).max()) if len(trajectory) else float("nan"),
    }


def _local_summary(scenario: EvolutionScenario, trajectory: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in trajectory.groupby(["assignment", "stage", "region"], sort=False, dropna=False):
        assignment, stage, region = key
        row_fail = group.groupby("source_row_index")["symbol_status"].agg(lambda values: bool((values.astype(str) == "fail").any()))
        row_watch = group.groupby("source_row_index")["symbol_status"].agg(lambda values: bool((values.astype(str) == "watch").any()))
        rows.append({
            "scenario": scenario.label,
            "model": scenario.model,
            "assignment": str(assignment),
            "stage": str(stage),
            "region": str(region),
            "rows": int(group["source_row_index"].nunique()),
            "symbol_status": "fail" if int(row_fail.sum()) else "watch" if int(row_watch.sum()) else "pass",
            "fail_rows_any_time": int(row_fail.sum()),
            "watch_rows_any_time": int(row_watch.sum()),
            "min_relative_cone_margin": float(group["relative_cone_margin"].astype(float).min()),
            "min_transport_margin": float(group["transport_margin"].astype(float).min()),
            "p99_heat_ratio": _quantile(group["regulated_heat_flux_ratio"], 0.99),
            "max_transport_rapidity_abs": float(group["transport_rapidity_abs"].astype(float).replace([np.inf], np.nan).max()),
        })
    return pd.DataFrame(rows)


def build_transport_evolution(
    stroke_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    evolution_spec: TransportEvolutionSpec | None = None,
    scenarios: list[EvolutionScenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    evolution_spec = evolution_spec or TransportEvolutionSpec()
    scenarios = scenarios or DEFAULT_SCENARIOS
    point_fit, manifest, point_path = _load_point_fit(stroke_dir)
    selected = _select_adversarial_rows(
        point_fit,
        symbol_spec,
        include_pass_margin=evolution_spec.include_pass_margin,
    )
    times = np.arange(int(evolution_spec.steps) + 1, dtype=float) * float(evolution_spec.dt)
    trajectory_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    local_frames: list[pd.DataFrame] = []
    for scenario in scenarios:
        frames = [_evaluate_step(selected, scenario, float(time), symbol_spec) for time in times]
        trajectory = pd.concat(frames, ignore_index=True)
        trajectory.insert(0, "scenario", scenario.label)
        trajectory.insert(1, "model", scenario.model)
        trajectory_frames.append(trajectory)
        summary_rows.append(_scenario_summary(scenario, trajectory, evolution_spec))
        local_frames.append(_local_summary(scenario, trajectory))
    trajectory = pd.concat(trajectory_frames, ignore_index=True) if trajectory_frames else pd.DataFrame()
    scenario_summary = pd.DataFrame(summary_rows)
    local_summary = pd.concat(local_frames, ignore_index=True) if local_frames else pd.DataFrame()
    decision = _decision(scenario_summary)
    outputs = {
        "selected_rows": selected,
        "trajectory": trajectory,
        "scenario_summary": scenario_summary,
        "local_summary": local_summary,
        "decision": decision,
    }
    metadata = {
        "source_name": "endpoint_support_transport_evolution",
        "stroke_dir": str(stroke_dir),
        "point_fit": str(point_path),
        "point_fit_sha256": sha256_file(point_path),
        "stroke_source_name": manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "evolution_spec": evolution_spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "caveat": (
            "Local fixed-background transport-margin evolution pilot over dense principal-symbol watch rows. "
            "This tests bounded rapidity versus raw heat-ratio perturbations; it is not a full spatial PDE evolution."
        ),
    }
    return outputs, metadata, _report(outputs, metadata)


def _decision(scenario_summary: pd.DataFrame) -> pd.DataFrame:
    raw = scenario_summary.loc[
        (scenario_summary["model"].astype(str) == "raw_ratio")
        & (scenario_summary["heat_ratio_delta"].astype(float) == 1.0e-4)
    ]
    bounded = scenario_summary.loc[
        (scenario_summary["model"].astype(str) == "rapidity")
        & (scenario_summary["heat_ratio_delta"].astype(float) == 1.0e-4)
        & (scenario_summary["damping_rate"].astype(float) == 4.0)
    ]
    raw_fails = bool(len(raw) and int(raw["fail_rows_any_time"].max()) > 0)
    bounded_passes = bool(len(bounded) and int(bounded["fail_rows_any_time"].iloc[0]) == 0)
    status = "transport_law_candidate" if raw_fails and bounded_passes else "watch" if bounded_passes else "fail"
    return pd.DataFrame([{
        "transport_evolution_status": status,
        "raw_delta_1e4_fails": raw_fails,
        "bounded_delta_1e4_damped_passes": bounded_passes,
        "bounded_delta_1e4_damped_min_margin": _finite(bounded["min_relative_cone_margin"].iloc[0], float("nan")) if len(bounded) else float("nan"),
        "decision_read": (
            "bounded rapidity transport with damping preserves hard cone/transport gates under the first raw heat-current failure stress"
            if status == "transport_law_candidate"
            else "bounded rapidity transport does not yet protect the first heat-current failure stress"
            if status == "fail"
            else "bounded rapidity transport passes the tested stress but raw failure comparison is incomplete"
        ),
    }])


def _fmt(value: Any) -> str:
    number = _finite(value, float("nan"))
    if not math.isfinite(number):
        return "nan"
    if abs(number) > 0 and (abs(number) < 1.0e-4 or abs(number) >= 1.0e5):
        return f"{number:.3e}"
    return f"{number:.6f}"


def _report(outputs: dict[str, pd.DataFrame], metadata: dict[str, Any]) -> str:
    summary = outputs["scenario_summary"]
    local = outputs["local_summary"]
    decision = outputs["decision"].iloc[0]
    first_fail = local.loc[local["fail_rows_any_time"].astype(int) > 0].head(12)
    lines = [
        "# Stage II Beta075 Reduced Transport Evolution Pilot",
        "",
        "## Status",
        "",
        f"Overall status: `{decision['transport_evolution_status']}`.",
        "",
        "This is a local fixed-background evolution pilot for the heat-current/transport variable on the dense principal-symbol watch rows. It compares a raw heat-ratio perturbation against a bounded rapidity variable with relaxation back to the frozen beta075 state.",
        "",
        "## Scenario Summary",
        "",
        "| scenario | model | status | fail rows | watch rows | min cone margin | min transport margin | p99 heat ratio | max psi |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['model']} | {row['symbol_status']} | {int(row['fail_rows_any_time'])} | "
            f"{int(row['watch_rows_any_time'])} | {_fmt(row['min_relative_cone_margin'])} | "
            f"{_fmt(row['min_transport_margin'])} | {_fmt(row['p99_heat_ratio'])} | {_fmt(row['max_transport_rapidity_abs'])} |"
        )
    if len(first_fail):
        lines.extend([
            "",
            "## Local Failures",
            "",
            "| scenario | assignment | stage | region | fail rows | min cone margin | min transport margin |",
            "| --- | --- | --- | --- | ---: | ---: | ---: |",
        ])
        for _, row in first_fail.iterrows():
            lines.append(
                f"| {row['scenario']} | {row['assignment']} | {row['stage']} | {row['region']} | "
                f"{int(row['fail_rows_any_time'])} | {_fmt(row['min_relative_cone_margin'])} | {_fmt(row['min_transport_margin'])} |"
            )
    lines.extend([
        "",
        "## Interpretation",
        "",
        str(decision["decision_read"]),
        "",
        "The pilot is not a full spatial PDE evolution, but it tests the exact fragility found by the sensitivity rung. A raw `+1e-4` heat-ratio perturbation fails immediately because it crosses the transport boundary. Evolving the same stress as a perturbation of bounded rapidity keeps the ratio below one and allows damping to recover margin. That makes bounded transport rapidity a plausible reduced evolution variable, not just a notation choice.",
        "",
        "## Next",
        "",
        "```text",
        "1. Add spatial coupling on l for the same rapidity variable.",
        "2. Couple the support stroke/stress variables to the rapidity relaxation source.",
        "3. Require the O(1e-4) stress case to preserve cone and transport margins under spatial advection, not just local relaxation.",
        "```",
        "",
        "## Provenance",
        "",
        f"- point fit: `{metadata['point_fit']}`",
        f"- selected rows: `{len(outputs['selected_rows'])}` dense watch/near-watch rows",
    ])
    return "\n".join(lines) + "\n"


def write_transport_evolution_outputs(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "selected_rows": outdir / "endpoint_support_transport_evolution_selected_rows.csv",
        "trajectory": outdir / "endpoint_support_transport_evolution_trajectory.csv",
        "scenario_summary": outdir / "endpoint_support_transport_evolution_scenarios.csv",
        "local_summary": outdir / "endpoint_support_transport_evolution_local.csv",
        "decision": outdir / "endpoint_support_transport_evolution_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "endpoint_support_transport_evolution_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
