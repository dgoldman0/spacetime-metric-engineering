from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_support_principal_symbol import (
    PrincipalSymbolSpec,
    _active_mask,
    _finite,
    _quantile,
    _symbol_row,
    build_principal_symbol_tables,
)
from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


@dataclass(frozen=True)
class SensitivityScenario:
    label: str
    heat_ratio_delta: float = 0.0
    regulator_scale: float = 1.0
    heat_sound_cap: float | None = None
    angular_sound_cap: float | None = None
    support_sound_cap: float | None = None


DEFAULT_SCENARIOS = [
    SensitivityScenario("nominal"),
    SensitivityScenario("heat_relief_m5e4", heat_ratio_delta=-5.0e-4),
    SensitivityScenario("heat_stress_p2p5e5", heat_ratio_delta=2.5e-5),
    SensitivityScenario("heat_stress_p5e5", heat_ratio_delta=5.0e-5),
    SensitivityScenario("heat_stress_p7p5e5", heat_ratio_delta=7.5e-5),
    SensitivityScenario("heat_stress_p1e4", heat_ratio_delta=1.0e-4),
    SensitivityScenario("heat_stress_p2p5e4", heat_ratio_delta=2.5e-4),
    SensitivityScenario("heat_stress_p5e4", heat_ratio_delta=5.0e-4),
    SensitivityScenario("regulator_half", regulator_scale=0.5),
    SensitivityScenario("regulator_tenth", regulator_scale=0.1),
    SensitivityScenario("regulator_one_percent", regulator_scale=0.01),
    SensitivityScenario("regulator_zero", regulator_scale=0.0),
    SensitivityScenario("heat_sound_cap_0p50", heat_sound_cap=0.50),
    SensitivityScenario("heat_sound_cap_0p70", heat_sound_cap=0.70),
    SensitivityScenario("support_sound_cap_0p65", support_sound_cap=0.65),
    SensitivityScenario("combined_heat_p5e5_cap0p50", heat_ratio_delta=5.0e-5, heat_sound_cap=0.50),
]


def _load_point_fit(stroke_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = stroke_dir / "endpoint_support_stroke_exchange_manifest.json"
    manifest: dict[str, Any] = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    files = manifest.get("files", {})
    point_path = resolve_manifest_path(stroke_dir, files.get("point_fit", "endpoint_support_stroke_exchange_point_fit.csv"))
    return pd.read_csv(point_path), manifest, point_path


def _spec_for_scenario(base: PrincipalSymbolSpec, scenario: SensitivityScenario) -> PrincipalSymbolSpec:
    return PrincipalSymbolSpec(
        heat_sound_cap=float(base.heat_sound_cap if scenario.heat_sound_cap is None else scenario.heat_sound_cap),
        angular_sound_cap=float(base.angular_sound_cap if scenario.angular_sound_cap is None else scenario.angular_sound_cap),
        support_sound_cap=float(base.support_sound_cap if scenario.support_sound_cap is None else scenario.support_sound_cap),
        speed_margin_gate=base.speed_margin_gate,
        speed_margin_watch=base.speed_margin_watch,
        transport_margin_watch=base.transport_margin_watch,
        heat_ratio_watch=base.heat_ratio_watch,
        high_psi_watch=base.high_psi_watch,
        eigen_condition_gate=base.eigen_condition_gate,
        live_support_density_gate=base.live_support_density_gate,
    )


def _perturb_frame(frame: pd.DataFrame, scenario: SensitivityScenario) -> pd.DataFrame:
    out = frame.copy()
    if "regulated_heat_flux_ratio" in out:
        ratio = out["regulated_heat_flux_ratio"].astype(float) + float(scenario.heat_ratio_delta)
        out["regulated_heat_flux_ratio"] = ratio
        out["transport_margin"] = 1.0 - ratio
        clipped = ratio.clip(lower=0.0, upper=1.0 - 1.0e-15)
        psi = np.arctanh(clipped)
        psi = psi.where(ratio < 1.0, np.inf)
        out["transport_rapidity_abs"] = psi
    for column in ["enthalpy_buffer_density", "regulated_type_i_margin"]:
        if column in out:
            out[column] = out[column].astype(float) * float(scenario.regulator_scale)
    return out


def _evaluate_frame(frame: pd.DataFrame, spec: PrincipalSymbolSpec) -> pd.DataFrame:
    rows = []
    for idx, row in frame.iterrows():
        out = _symbol_row(row, spec)
        out["source_row_index"] = int(idx)
        rows.append(out)
    return pd.DataFrame(rows)


def _select_adversarial_rows(point_fit: pd.DataFrame, spec: PrincipalSymbolSpec, *, include_pass_margin: float) -> pd.DataFrame:
    nominal = build_principal_symbol_tables(
        point_fit,
        label="nominal",
        mesh="dense",
        kind="reference_24x14",
        spec=spec,
    )["point_symbol"]
    active = _active_mask(point_fit)
    candidate = nominal.loc[active.to_numpy()].copy()
    watch = candidate["symbol_status"].astype(str) != "pass"
    near = candidate["relative_cone_margin"].astype(float) <= float(include_pass_margin)
    selected_indices = candidate.loc[watch | near].index
    selected = point_fit.loc[selected_indices].copy()
    selected["source_row_index"] = selected.index.astype(int)
    return selected


def _scenario_summary(scenario: SensitivityScenario, symbol: pd.DataFrame) -> dict[str, Any]:
    fail_rows = int((symbol["symbol_status"].astype(str) == "fail").sum())
    watch_rows = int((symbol["symbol_status"].astype(str) == "watch").sum())
    hard_pass = fail_rows == 0
    return {
        "scenario": scenario.label,
        "heat_ratio_delta": float(scenario.heat_ratio_delta),
        "regulator_scale": float(scenario.regulator_scale),
        "heat_sound_cap": float("nan") if scenario.heat_sound_cap is None else float(scenario.heat_sound_cap),
        "angular_sound_cap": float("nan") if scenario.angular_sound_cap is None else float(scenario.angular_sound_cap),
        "support_sound_cap": float("nan") if scenario.support_sound_cap is None else float(scenario.support_sound_cap),
        "rows": int(len(symbol)),
        "symbol_status": "fail" if fail_rows else "watch" if watch_rows else "pass",
        "hard_symbol_pass": hard_pass,
        "fail_rows": fail_rows,
        "watch_rows": watch_rows,
        "min_relative_cone_margin": float(symbol["relative_cone_margin"].astype(float).min()) if len(symbol) else float("nan"),
        "p01_relative_cone_margin": _quantile(symbol["relative_cone_margin"], 0.01) if len(symbol) else float("nan"),
        "min_transport_margin": float(symbol["transport_margin"].astype(float).min()) if len(symbol) else float("nan"),
        "p01_transport_margin": _quantile(symbol["transport_margin"], 0.01) if len(symbol) else float("nan"),
        "p99_heat_ratio": _quantile(symbol["regulated_heat_flux_ratio"], 0.99) if len(symbol) else float("nan"),
        "max_transport_rapidity_abs": float(symbol["transport_rapidity_abs"].astype(float).replace([np.inf], np.nan).max()) if len(symbol) else float("nan"),
        "min_h_reg": float(symbol["enthalpy_buffer_density"].astype(float).min()) if len(symbol) else float("nan"),
        "max_abs_relative_characteristic_speed": float(symbol["max_abs_relative_characteristic_speed"].astype(float).max()) if len(symbol) else float("nan"),
    }


def _local_summary(scenario: SensitivityScenario, symbol: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in symbol.groupby(["assignment", "stage", "region"], sort=False, dropna=False):
        assignment, stage, region = key
        fail_rows = int((group["symbol_status"].astype(str) == "fail").sum())
        watch_rows = int((group["symbol_status"].astype(str) == "watch").sum())
        rows.append({
            "scenario": scenario.label,
            "assignment": str(assignment),
            "stage": str(stage),
            "region": str(region),
            "rows": int(len(group)),
            "symbol_status": "fail" if fail_rows else "watch" if watch_rows else "pass",
            "fail_rows": fail_rows,
            "watch_rows": watch_rows,
            "min_relative_cone_margin": float(group["relative_cone_margin"].astype(float).min()),
            "min_transport_margin": float(group["transport_margin"].astype(float).min()),
            "p99_heat_ratio": _quantile(group["regulated_heat_flux_ratio"], 0.99),
            "max_transport_rapidity_abs": float(group["transport_rapidity_abs"].astype(float).replace([np.inf], np.nan).max()),
            "min_h_reg": float(group["enthalpy_buffer_density"].astype(float).min()),
        })
    return pd.DataFrame(rows)


def build_symbol_sensitivity(
    stroke_dir: Path,
    *,
    spec: PrincipalSymbolSpec | None = None,
    scenarios: list[SensitivityScenario] | None = None,
    include_pass_margin: float = 0.005,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    spec = spec or PrincipalSymbolSpec()
    scenarios = scenarios or DEFAULT_SCENARIOS
    point_fit, manifest, point_path = _load_point_fit(stroke_dir)
    selected = _select_adversarial_rows(point_fit, spec, include_pass_margin=include_pass_margin)
    point_frames: list[pd.DataFrame] = []
    local_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_spec = _spec_for_scenario(spec, scenario)
        perturbed = _perturb_frame(selected, scenario)
        symbol = _evaluate_frame(perturbed, scenario_spec)
        symbol.insert(0, "scenario", scenario.label)
        point_frames.append(symbol)
        local_frames.append(_local_summary(scenario, symbol))
        summary_rows.append(_scenario_summary(scenario, symbol))
    point_sensitivity = pd.concat(point_frames, ignore_index=True) if point_frames else pd.DataFrame()
    local_sensitivity = pd.concat(local_frames, ignore_index=True) if local_frames else pd.DataFrame()
    scenario_summary = pd.DataFrame(summary_rows)
    decision = _decision(scenario_summary)
    outputs = {
        "selected_rows": selected,
        "point_sensitivity": point_sensitivity,
        "local_sensitivity": local_sensitivity,
        "scenario_summary": scenario_summary,
        "decision": decision,
    }
    metadata = {
        "source_name": "endpoint_support_symbol_sensitivity",
        "stroke_dir": str(stroke_dir),
        "point_fit": str(point_path),
        "point_fit_sha256": sha256_file(point_path),
        "stroke_source_name": manifest.get("source_name", ""),
        "include_pass_margin": float(include_pass_margin),
        "spec": spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "caveat": (
            "Frozen-coefficient local sensitivity over the nominal dense principal-symbol watch rows. "
            "This does not evolve the medium; it estimates margin fragility before reduced fixed-background evolution."
        ),
    }
    return outputs, metadata, _report(outputs, metadata)


def _decision(scenario_summary: pd.DataFrame) -> pd.DataFrame:
    nominal = scenario_summary.loc[scenario_summary["scenario"].astype(str) == "nominal"]
    heat_stress = scenario_summary.loc[scenario_summary["heat_ratio_delta"].astype(float) > 0.0].sort_values("heat_ratio_delta")
    first_fail = heat_stress.loc[heat_stress["fail_rows"].astype(int) > 0].head(1)
    first_watch = heat_stress.loc[heat_stress["watch_rows"].astype(int) > 0].head(1)
    nominal_pass = bool(len(nominal) and int(nominal["fail_rows"].iloc[0]) == 0)
    first_fail_delta = _finite(first_fail["heat_ratio_delta"].iloc[0], float("nan")) if len(first_fail) else float("nan")
    status = "fail" if not nominal_pass else "fragile_watch" if math.isfinite(first_fail_delta) and first_fail_delta <= 1.0e-4 else "watch"
    return pd.DataFrame([{
        "symbol_sensitivity_status": status,
        "nominal_fail_rows": int(nominal["fail_rows"].iloc[0]) if len(nominal) else -1,
        "nominal_watch_rows": int(nominal["watch_rows"].iloc[0]) if len(nominal) else -1,
        "first_positive_heat_delta_with_failures": first_fail_delta,
        "first_positive_heat_delta_with_watch_rows": _finite(first_watch["heat_ratio_delta"].iloc[0], float("nan")) if len(first_watch) else float("nan"),
        "decision_read": (
            "nominal watch rows pass hard symbol gates, but O(1e-4) heat-current worsening creates hard local failures"
            if status == "fragile_watch"
            else "nominal watch rows fail hard symbol gates before perturbation"
            if status == "fail"
            else "nominal watch rows tolerate the scanned heat-current perturbations without hard symbol failure"
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
    local = outputs["local_sensitivity"]
    decision = outputs["decision"].iloc[0]
    heat_rows = summary.loc[
        summary["scenario"].astype(str).str.startswith("heat_relief")
        | summary["scenario"].astype(str).str.startswith("heat_stress")
    ]
    stress_rows = heat_rows.sort_values("heat_ratio_delta")
    regulator_rows = summary.loc[summary["scenario"].astype(str).str.startswith("regulator")]
    sound_rows = summary.loc[
        summary["scenario"].astype(str).str.contains("cap")
        & (~summary["scenario"].astype(str).str.startswith("combined"))
    ]
    fail_local = local.loc[local["fail_rows"].astype(int) > 0].sort_values(["scenario", "fail_rows"], ascending=[True, False]).head(10)
    lines = [
        "# Stage II Beta075 Principal-Symbol Sensitivity",
        "",
        "## Status",
        "",
        f"Overall status: `{decision['symbol_sensitivity_status']}`.",
        "",
        "This is a frozen-coefficient sensitivity check on the dense principal-symbol watch rows. It perturbs local heat-current ratio, regulator margin, and characteristic-speed caps without refitting the support sector.",
        "",
        "## Scenario Summary",
        "",
        "| scenario | status | fail rows | watch rows | min cone margin | min transport margin | p99 heat ratio | min h_reg |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['symbol_status']} | {int(row['fail_rows'])} | {int(row['watch_rows'])} | "
            f"{_fmt(row['min_relative_cone_margin'])} | {_fmt(row['min_transport_margin'])} | {_fmt(row['p99_heat_ratio'])} | {_fmt(row['min_h_reg'])} |"
        )
    lines.extend([
        "",
        "## Heat-Current Stress Ladder",
        "",
        "| heat delta | status | fail rows | min cone margin | min transport margin |",
        "| ---: | --- | ---: | ---: | ---: |",
    ])
    for _, row in stress_rows.iterrows():
        lines.append(
            f"| {_fmt(row['heat_ratio_delta'])} | {row['symbol_status']} | {int(row['fail_rows'])} | "
            f"{_fmt(row['min_relative_cone_margin'])} | {_fmt(row['min_transport_margin'])} |"
        )
    lines.extend([
        "",
        "## Regulator And Speed-Cap Probes",
        "",
        "Regulator depletion alone keeps the cone speeds real until the regulator is driven exactly to zero, where the positive-margin gate fails. Raising heat/support speed caps mostly changes cone-margin tightness; it does not create the first hard failure before heat-current stress does.",
        "",
        "| scenario | status | fail rows | min cone margin | min h_reg |",
        "| --- | --- | ---: | ---: | ---: |",
    ])
    for _, row in pd.concat([regulator_rows, sound_rows], ignore_index=True).iterrows():
        lines.append(
            f"| {row['scenario']} | {row['symbol_status']} | {int(row['fail_rows'])} | "
            f"{_fmt(row['min_relative_cone_margin'])} | {_fmt(row['min_h_reg'])} |"
        )
    if len(fail_local):
        lines.extend([
            "",
            "## First Local Failures",
            "",
            "| scenario | assignment | stage | region | fail rows | min cone margin | min transport margin |",
            "| --- | --- | --- | --- | ---: | ---: | ---: |",
        ])
        for _, row in fail_local.iterrows():
            lines.append(
                f"| {row['scenario']} | {row['assignment']} | {row['stage']} | {row['region']} | {int(row['fail_rows'])} | "
                f"{_fmt(row['min_relative_cone_margin'])} | {_fmt(row['min_transport_margin'])} |"
            )
    lines.extend([
        "",
        "## Interpretation",
        "",
        str(decision["decision_read"]),
        "",
        "The sensitivity result sharpens the previous watch: the reduced symbol is not algebraically failing at the frozen point, but some dense rows have only an O(1e-4) heat-current buffer before the positive transport/cone-margin gates fail. That argues for a regulator/transport-margin-preserving reduced evolution before any broader PDE claim.",
        "",
        "## Next",
        "",
        "```text",
        "1. Build reduced fixed-background evolution with explicit transport-margin preservation.",
        "2. Use the heat-stress failure rows as boundary/perturbation targets.",
        "3. Do not promote to action-level hyperbolicity until O(1e-4) heat-current fragility is explained or buffered.",
        "```",
        "",
        "## Provenance",
        "",
        f"- point fit: `{metadata['point_fit']}`",
        f"- selected rows: `{len(outputs['selected_rows'])}` nominal watch/near-watch rows",
    ])
    return "\n".join(lines) + "\n"


def write_symbol_sensitivity_outputs(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "selected_rows": outdir / "endpoint_support_symbol_sensitivity_selected_rows.csv",
        "point_sensitivity": outdir / "endpoint_support_symbol_sensitivity_point.csv",
        "local_sensitivity": outdir / "endpoint_support_symbol_sensitivity_local.csv",
        "scenario_summary": outdir / "endpoint_support_symbol_sensitivity_scenarios.csv",
        "decision": outdir / "endpoint_support_symbol_sensitivity_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "endpoint_support_symbol_sensitivity_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
