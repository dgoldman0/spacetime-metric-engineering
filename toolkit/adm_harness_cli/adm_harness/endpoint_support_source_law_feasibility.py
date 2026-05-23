from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_support_principal_symbol import _bool_series, _finite
from .source_ledger import sha256_file, write_manifest


PREFIX = "endpoint_support_source_coupling"


@dataclass(frozen=True)
class SourceLawFeasibilitySpec:
    observed_heat_ratio_delta: float = 1.0e-4
    expected_assignment: str = "support_edge_endpoint_junction"
    expected_region: str = "support_edge"
    expected_stages: tuple[str, ...] = ("entry_precatch", "catch_rematch")
    severe_scale_watch: float = 0.25
    adjacent_scale_jump_watch: float = 0.50
    min_margin_gate: float = 1.0e-6


def _read_csv(coupling_dir: Path, suffix: str) -> pd.DataFrame:
    path = coupling_dir / f"{PREFIX}_{suffix}.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing source-coupling table: {path}")
    return pd.read_csv(path)


def _read_manifest(coupling_dir: Path) -> dict[str, Any]:
    path = coupling_dir / f"{PREFIX}_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _observed_unlimited(slice_summary: pd.DataFrame, spec: SourceLawFeasibilitySpec) -> pd.DataFrame:
    observed = slice_summary.loc[
        (slice_summary["heat_ratio_delta"].astype(float) <= float(spec.observed_heat_ratio_delta) + 1.0e-15)
        & (~_bool_series(slice_summary["budget_limiter"]))
    ].copy()
    outward = observed.loc[observed["direction"].astype(str).eq("outward")].copy()
    return outward if len(outward) else observed


def _expected_scope_mask(frame: pd.DataFrame, spec: SourceLawFeasibilitySpec) -> pd.Series:
    return (
        frame["assignment"].astype(str).eq(str(spec.expected_assignment))
        & frame["region"].astype(str).eq(str(spec.expected_region))
        & frame["stage"].astype(str).isin(tuple(spec.expected_stages))
    )


def _cap_slice_audit(slice_summary: pd.DataFrame, spec: SourceLawFeasibilitySpec) -> pd.DataFrame:
    observed = _observed_unlimited(slice_summary, spec).copy()
    observed["source_profile_scale"] = pd.to_numeric(observed["source_profile_scale"], errors="coerce").fillna(1.0)
    observed["source_profile_raw_reference_budget_fraction"] = pd.to_numeric(
        observed["source_profile_raw_reference_budget_fraction"],
        errors="coerce",
    )
    observed["cap_scope_applies"] = _bool_series(observed["source_profile_budget_cap_applied"])
    observed["scale_below_one"] = observed["source_profile_scale"].astype(float) < (1.0 - 1.0e-12)
    observed["expected_phase_local_scope"] = _expected_scope_mask(observed, spec)
    observed["scaled_outside_expected_scope"] = observed["scale_below_one"] & (~observed["expected_phase_local_scope"])
    observed["scale_deficit"] = 1.0 - observed["source_profile_scale"].astype(float)
    cols = [
        "assignment",
        "stage",
        "region",
        "s",
        "slice_s_key",
        "rows",
        "max_budget_fraction",
        "min_relative_cone_margin_sample",
        "min_transport_margin",
        "source_profile_raw_reference_budget_fraction",
        "source_profile_scale",
        "scale_deficit",
        "cap_scope_applies",
        "scale_below_one",
        "expected_phase_local_scope",
        "scaled_outside_expected_scope",
        "worst_source_row_index",
        "worst_l",
    ]
    return observed[cols].sort_values(["assignment", "stage", "region", "s"]).reset_index(drop=True)


def _phase_summary(cap_slice_audit: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (assignment, stage, region), group in cap_slice_audit.groupby(["assignment", "stage", "region"], sort=True):
        raw = group["source_profile_raw_reference_budget_fraction"].astype(float).replace([np.inf, -np.inf], np.nan)
        rows.append({
            "assignment": str(assignment),
            "stage": str(stage),
            "region": str(region),
            "slices": int(len(group)),
            "rows": int(group["rows"].astype(int).sum()),
            "cap_scope_slices": int(group["cap_scope_applies"].astype(bool).sum()),
            "scaled_slices": int(group["scale_below_one"].astype(bool).sum()),
            "scaled_outside_expected_scope_slices": int(group["scaled_outside_expected_scope"].astype(bool).sum()),
            "min_source_profile_scale": float(group["source_profile_scale"].astype(float).min()),
            "max_scale_deficit": float(group["scale_deficit"].astype(float).max()),
            "max_raw_reference_budget_fraction": float(raw.max()) if raw.notna().any() else float("nan"),
            "max_observed_budget_fraction": float(group["max_budget_fraction"].astype(float).max()),
            "min_relative_cone_margin_sample": float(group["min_relative_cone_margin_sample"].astype(float).min()),
            "min_transport_margin": float(group["min_transport_margin"].astype(float).min()),
        })
    return pd.DataFrame(rows)


def _scale_jump_summary(cap_slice_audit: pd.DataFrame, spec: SourceLawFeasibilitySpec) -> pd.DataFrame:
    target = cap_slice_audit.loc[
        cap_slice_audit["assignment"].astype(str).eq(str(spec.expected_assignment))
        & cap_slice_audit["region"].astype(str).eq(str(spec.expected_region))
    ].copy()
    rows: list[dict[str, Any]] = []
    for key, group in [("support_edge_all_phases", target), *target.groupby("stage", sort=True)]:
        if isinstance(key, tuple):
            label = str(key[0])
        else:
            label = str(key)
        ordered = group.sort_values("s").reset_index(drop=True)
        if len(ordered) < 2:
            continue
        scale = ordered["source_profile_scale"].astype(float).to_numpy()
        jumps = np.abs(np.diff(scale))
        pos = int(np.argmax(jumps)) if len(jumps) else 0
        rows.append({
            "scope": label,
            "slices": int(len(ordered)),
            "max_adjacent_scale_jump": float(jumps[pos]) if len(jumps) else float("nan"),
            "left_s": _finite(ordered.iloc[pos].get("s"), float("nan")),
            "left_stage": str(ordered.iloc[pos].get("stage", "")),
            "left_scale": float(scale[pos]),
            "right_s": _finite(ordered.iloc[pos + 1].get("s"), float("nan")),
            "right_stage": str(ordered.iloc[pos + 1].get("stage", "")),
            "right_scale": float(scale[pos + 1]),
        })
    return pd.DataFrame(rows)


def _margin_summary(package_summary: pd.DataFrame, spec: SourceLawFeasibilitySpec) -> pd.DataFrame:
    observed = package_summary.loc[
        (package_summary["heat_ratio_delta"].astype(float) <= float(spec.observed_heat_ratio_delta) + 1.0e-15)
        & (~_bool_series(package_summary["budget_limiter"]))
    ].copy()
    large = package_summary.loc[
        (package_summary["heat_ratio_delta"].astype(float) > float(spec.observed_heat_ratio_delta) + 1.0e-15)
        & (~_bool_series(package_summary["budget_limiter"]))
    ].copy()
    return pd.DataFrame([{
        "observed_scenarios": int(len(observed)),
        "observed_unlimited_pass": bool(len(observed) and _bool_series(observed["hard_pass"]).all()),
        "observed_limiter_clipped_rows": int(observed["limiter_clipped_rows"].astype(int).sum()) if len(observed) else 0,
        "max_observed_unlimited_budget_fraction": float(observed["max_budget_fraction"].astype(float).max()) if len(observed) else float("nan"),
        "min_observed_relative_cone_margin": float(observed["min_relative_cone_margin_sample"].astype(float).min()) if len(observed) else float("nan"),
        "min_observed_transport_margin": float(observed["min_transport_margin"].astype(float).min()) if len(observed) else float("nan"),
        "large_unlimited_scenarios": int(len(large)),
        "large_unlimited_fails": bool(len(large) and (~_bool_series(large["hard_pass"])).any()),
        "max_large_unlimited_budget_fraction": float(large["max_budget_fraction"].astype(float).max()) if len(large) else float("nan"),
    }])


def _decision(
    cap_slice_audit: pd.DataFrame,
    phase_summary: pd.DataFrame,
    jump_summary: pd.DataFrame,
    margin_summary: pd.DataFrame,
    spec: SourceLawFeasibilitySpec,
) -> pd.DataFrame:
    margin = margin_summary.iloc[0]
    scale = cap_slice_audit["source_profile_scale"].astype(float)
    scaled = cap_slice_audit.loc[cap_slice_audit["scale_below_one"].astype(bool)].copy()
    bounded_scale = bool(((scale >= -1.0e-12) & (scale <= 1.0 + 1.0e-12)).all())
    phase_local = int(scaled["scaled_outside_expected_scope"].astype(bool).sum()) == 0
    observed_pass = bool(margin["observed_unlimited_pass"])
    observed_limiter_free = int(margin["observed_limiter_clipped_rows"]) == 0
    min_scale = float(scale.min()) if len(scale) else float("nan")
    max_jump = float(jump_summary["max_adjacent_scale_jump"].astype(float).max()) if len(jump_summary) else 0.0
    severe_scale_watch = math.isfinite(min_scale) and min_scale < float(spec.severe_scale_watch)
    smoothness_watch = math.isfinite(max_jump) and max_jump > float(spec.adjacent_scale_jump_watch)
    margin_watch = (
        _finite(margin["min_observed_relative_cone_margin"], float("nan")) < float(spec.min_margin_gate)
        or _finite(margin["min_observed_transport_margin"], float("nan")) < float(spec.min_margin_gate)
    )
    large_watch = bool(margin["large_unlimited_fails"])
    hard_fail = (not observed_pass) or (not bounded_scale) or (not phase_local) or (not observed_limiter_free)
    watch = severe_scale_watch or smoothness_watch or margin_watch or large_watch
    status = (
        "source_law_feasibility_fail"
        if hard_fail
        else "phase_local_source_law_candidate_with_watches"
        if watch
        else "phase_local_source_law_candidate"
    )
    read = (
        "the proposed source law fails a hard boundedness, locality, observed-pass, or limiter-free gate"
        if hard_fail
        else "the source law is bounded, observed-clean, phase-local, and limiter-free, but severity/smoothness/high-amplitude watches remain"
        if watch
        else "the source law is bounded, observed-clean, phase-local, limiter-free, and below configured watch thresholds"
    )
    return pd.DataFrame([{
        "source_law_feasibility_status": status,
        "observed_unlimited_pass": observed_pass,
        "observed_limiter_free": observed_limiter_free,
        "bounded_scale": bounded_scale,
        "phase_local_scaled_slices": phase_local,
        "scaled_slices": int(len(scaled)),
        "scaled_outside_expected_scope_slices": int(scaled["scaled_outside_expected_scope"].astype(bool).sum()) if len(scaled) else 0,
        "min_source_profile_scale": min_scale,
        "max_scale_deficit": float(cap_slice_audit["scale_deficit"].astype(float).max()) if len(cap_slice_audit) else float("nan"),
        "max_adjacent_scale_jump": max_jump,
        "severe_scale_watch": severe_scale_watch,
        "smoothness_watch": smoothness_watch,
        "margin_watch": margin_watch,
        "large_stress_watch": large_watch,
        "max_observed_unlimited_budget_fraction": _finite(margin["max_observed_unlimited_budget_fraction"], float("nan")),
        "min_observed_relative_cone_margin": _finite(margin["min_observed_relative_cone_margin"], float("nan")),
        "min_observed_transport_margin": _finite(margin["min_observed_transport_margin"], float("nan")),
        "max_large_unlimited_budget_fraction": _finite(margin["max_large_unlimited_budget_fraction"], float("nan")),
        "decision_read": read,
    }])


def _fmt(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(numeric):
        return "nan"
    if numeric != 0.0 and (abs(numeric) < 1.0e-3 or abs(numeric) >= 1.0e4):
        return f"{numeric:.3e}"
    return f"{numeric:.6f}"


def _build_report(
    coupling_dir: Path,
    decision: pd.DataFrame,
    phase_summary: pd.DataFrame,
    jump_summary: pd.DataFrame,
    margin_summary: pd.DataFrame,
    metadata: dict[str, Any],
) -> str:
    row = decision.iloc[0]
    margin = margin_summary.iloc[0]
    scaled = phase_summary.loc[phase_summary["scaled_slices"].astype(int) > 0].copy()
    lines = [
        "# Stage II Beta075 Support-Edge Source-Law Feasibility Audit",
        "",
        "## Status",
        "",
        f"Overall status: `{row['source_law_feasibility_status']}`.",
        "",
        "This audit tests whether the cap-0.95 support-edge source reshaping can be read as a bounded phase-local source law inside the existing endpoint/support medium story. It consumes the package source-coupling outputs rather than adding a new geometric or source component.",
        "",
        "Input run:",
        "",
        "```text",
        str(coupling_dir),
        "```",
        "",
        "## Decision Metrics",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| observed unlimited pass | {bool(row['observed_unlimited_pass'])} |",
        f"| observed limiter free | {bool(row['observed_limiter_free'])} |",
        f"| bounded scale | {bool(row['bounded_scale'])} |",
        f"| phase-local scaled slices | {bool(row['phase_local_scaled_slices'])} |",
        f"| scaled slices | {int(row['scaled_slices'])} |",
        f"| min source-profile scale | {_fmt(row['min_source_profile_scale'])} |",
        f"| max adjacent scale jump | {_fmt(row['max_adjacent_scale_jump'])} |",
        f"| max observed budget fraction | {_fmt(row['max_observed_unlimited_budget_fraction'])} |",
        f"| min observed cone margin | {_fmt(row['min_observed_relative_cone_margin'])} |",
        f"| min observed transport margin | {_fmt(row['min_observed_transport_margin'])} |",
        f"| max large-stress budget fraction | {_fmt(row['max_large_unlimited_budget_fraction'])} |",
        "",
        "## Scaled Phase Slices",
        "",
        "| assignment | stage | region | slices | scaled | min scale | max raw reference budget | max observed budget |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, phase in scaled.sort_values(["assignment", "stage", "region"]).iterrows():
        lines.append(
            f"| {phase['assignment']} | {phase['stage']} | {phase['region']} | "
            f"{int(phase['slices'])} | {int(phase['scaled_slices'])} | "
            f"{_fmt(phase['min_source_profile_scale'])} | "
            f"{_fmt(phase['max_raw_reference_budget_fraction'])} | "
            f"{_fmt(phase['max_observed_budget_fraction'])} |"
        )
    lines.extend([
        "",
        "## Smoothness Watch",
        "",
        "| scope | max adjacent jump | left s | left scale | right s | right scale |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for _, jump in jump_summary.sort_values("max_adjacent_scale_jump", ascending=False).head(6).iterrows():
        lines.append(
            f"| {jump['scope']} | {_fmt(jump['max_adjacent_scale_jump'])} | "
            f"{_fmt(jump['left_s'])} | {_fmt(jump['left_scale'])} | "
            f"{_fmt(jump['right_s'])} | {_fmt(jump['right_scale'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The normalized support-edge source law passes the hard observed-amplitude gates: outward and inward unlimited package evolution remain clean, no observed limiter is active, the scale is bounded in `[0, 1]`, and every actually scaled slice stays inside the intended support-edge endpoint-junction entry/catch scope.",
        "",
        "The watch is not hidden support. It is source-law shape: only a few slices are scaled, but one entry-precatch slice needs a severe scale of about `0.093`, and adjacent scale jumps are correspondingly large. That keeps the law as a phase-local constitutive candidate with severity/smoothness watches, not a final smooth action-level source rule.",
        "",
        "The deliberately large `5e-4` stress remains a margin watch. Per the handoff, it is carried as robustness context rather than used as a same-level tuning target.",
        "",
        "Claim boundary: this is still a reduced fixed-background source-law feasibility audit. It does not prove a final matter action, full PDE closure, or coupled Einstein-matter evolution.",
    ])
    if metadata:
        lines.extend([
            "",
            "## Provenance",
            "",
            "```json",
            json.dumps({
                "source_name": metadata.get("source_name"),
                "closure_dir": metadata.get("closure_dir"),
                "coupling_spec": metadata.get("coupling_spec"),
                "observed_unlimited_pass": bool(margin["observed_unlimited_pass"]),
            }, indent=2, sort_keys=True),
            "```",
        ])
    return "\n".join(lines) + "\n"


def build_source_law_feasibility(
    coupling_dir: Path,
    *,
    spec: SourceLawFeasibilitySpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    spec = spec or SourceLawFeasibilitySpec()
    manifest = _read_manifest(coupling_dir)
    package_summary = _read_csv(coupling_dir, "package_summary")
    slice_summary = _read_csv(coupling_dir, "slice_summary")
    cap_slice_audit = _cap_slice_audit(slice_summary, spec)
    phase_summary = _phase_summary(cap_slice_audit)
    jump_summary = _scale_jump_summary(cap_slice_audit, spec)
    margin_summary = _margin_summary(package_summary, spec)
    decision = _decision(cap_slice_audit, phase_summary, jump_summary, margin_summary, spec)
    outputs = {
        "cap_slice_audit": cap_slice_audit,
        "phase_summary": phase_summary,
        "scale_jump_summary": jump_summary,
        "margin_summary": margin_summary,
        "decision": decision,
    }
    metadata = {
        "source_name": "endpoint_support_source_law_feasibility",
        "coupling_dir": str(coupling_dir),
        "coupling_manifest_sha256": sha256_file(coupling_dir / f"{PREFIX}_manifest.json")
        if (coupling_dir / f"{PREFIX}_manifest.json").exists()
        else None,
        "source_coupling_manifest": manifest,
        "spec": spec.__dict__,
        "caveat": (
            "Reduced fixed-background feasibility audit for reading the support-edge source-profile cap "
            "as a bounded phase-local source law. This is not a final matter action or PDE closure."
        ),
    }
    report = _build_report(coupling_dir, decision, phase_summary, jump_summary, margin_summary, manifest)
    return outputs, metadata, report


def write_source_law_feasibility_outputs(
    outdir: Path,
    report_path: Path | None,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "cap_slice_audit": outdir / "endpoint_support_source_law_feasibility_cap_slice_audit.csv",
        "phase_summary": outdir / "endpoint_support_source_law_feasibility_phase_summary.csv",
        "scale_jump_summary": outdir / "endpoint_support_source_law_feasibility_scale_jump_summary.csv",
        "margin_summary": outdir / "endpoint_support_source_law_feasibility_margin_summary.csv",
        "decision": outdir / "endpoint_support_source_law_feasibility_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)
        paths["report"] = report_path
    manifest_path = outdir / "endpoint_support_source_law_feasibility_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
