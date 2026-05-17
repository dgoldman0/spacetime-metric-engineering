from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from .adm import apply_field_delta, recompute_adm_fields
from .service_modifiers import compute_service_field_delta
from .field_names import normalize_substrate_mode, public_substrate_mode, service_field_name, service_facing_dataframe
from .config import load_config, require_path
from .io import load_npz, write_json, write_table, read_table
from .metrics import (
    build_point_ledger,
    catch_rematch_localization,
    decision_sheet,
    GateThresholds,
    packet_exposure,
    peak_locations,
    scope_burdens,
    stage_region_burdens,
    summarize_control_law,
    support_shell_load,
)
from .plots import plot_fields
from .report import write_run_report, write_comparison_report
from .validation import (
    ValidationReport,
    validate_config_contract,
    validate_field_delta,
    validate_fields,
    validate_substrate,
)


def _write_validation(out_dir: Path, report: ValidationReport) -> None:
    write_json(out_dir / "validation_report.json", report.to_dict())


def _run_identity_self_check(fields: dict, tolerance: float) -> dict[str, Any]:
    recomputed = recompute_adm_fields(fields, recompute_r3=False)
    checks: dict[str, Any] = {"tolerance": tolerance, "passed": True, "channels": {}}
    for key in ["k_l", "k_omega", "K", "rho", "j_l"]:
        if key not in fields:
            continue
        diff = abs(recomputed[key] - fields[key])
        max_abs = float(diff.max())
        checks["channels"][key] = {"max_abs_error": max_abs, "passed": max_abs <= tolerance}
        if max_abs > tolerance:
            checks["passed"] = False
    return checks


def run_from_config(config_path: str | Path, output_dir: str | Path | None = None) -> Path:
    cfg = load_config(config_path)
    run_name = cfg["run_name"]
    velocity = cfg.get("velocity", (cfg.get("service", {}) or {}).get("velocity"))
    outputs = cfg.get("outputs", {})
    table_format = outputs.get("format", "csv")
    out_root = Path(output_dir or outputs.get("root", "runs"))
    out_dir = out_root / run_name
    if outputs.get("overwrite", True) and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    validation = ValidationReport()
    validation.merge(validate_config_contract(cfg), "config")

    exact_fields_path = require_path(cfg, "inputs", "exact_fields")
    exact_fields = load_npz(exact_fields_path)
    validation.merge(validate_fields(exact_fields, require_derived=True), "exact_fields")

    point_ledger_path = cfg.get("inputs", {}).get("exact_point_ledger")
    if point_ledger_path and not Path(point_ledger_path).exists():
        raise FileNotFoundError(f"exact_point_ledger path not found: {point_ledger_path}")

    substrate_cfg = cfg.get("substrate", {})
    substrate_mode_user = substrate_cfg.get("mode", "none")
    substrate_mode = normalize_substrate_mode(substrate_mode_user)
    substrate_fields = None
    substrate_fields_path = cfg.get("inputs", {}).get("substrate_fields")
    if substrate_fields_path:
        if not Path(substrate_fields_path).exists():
            raise FileNotFoundError(f"substrate_fields path not found: {substrate_fields_path}")
        substrate_fields = load_npz(substrate_fields_path)
    validation.merge(validate_substrate(substrate_fields, exact_fields), "substrate")

    synthesis_cfg = cfg.get("synthesis", {}) or {}
    synthesis_enabled = bool(synthesis_cfg.get("enabled", False))
    field_delta_metadata: dict[str, Any] | None = None
    field_delta_summary: pd.DataFrame | None = None
    service_modifier_summary: pd.DataFrame | None = None
    final_fields = exact_fields
    recompute_delta_from_substrate = False

    if synthesis_enabled:
        preliminary_ledger = build_point_ledger(
            exact_fields=exact_fields,
            velocity=velocity,
            point_ledger_path=point_ledger_path,
            substrate_fields=substrate_fields,
            substrate_mode=substrate_mode,
        )
        delta_result = compute_service_field_delta(
            exact_fields,
            preliminary_ledger=preliminary_ledger,
            cfg=cfg,
        )
        validation.merge(validate_field_delta(delta_result.delta, exact_fields), "field_delta")
        validation.raise_if_failed()
        modified_fields = apply_field_delta(exact_fields, delta_result.delta)
        validation.merge(validate_fields(modified_fields, require_derived=False), "modified_base_fields")
        recompute_r3 = any(k in delta_result.delta for k in ("gamma_ll", "gamma_omega"))
        final_fields = recompute_adm_fields(modified_fields, recompute_r3=recompute_r3)
        validation.merge(validate_fields(final_fields, require_derived=True), "modified_adm_fields")
        field_delta_metadata = delta_result.metadata
        rows = []
        for key, arr in delta_result.delta.items():
            rows.append({
                "service_field": service_field_name(key),
                "delta_name": f"delta_{service_field_name(key)}",
                "min": float(arr.min()),
                "max": float(arr.max()),
                "linf": float(abs(arr).max()),
                "l1": float(abs(arr).sum()),
                "nonzero_points": int((abs(arr) > 0).sum()),
            })
        field_delta_summary = pd.DataFrame(rows)
        if delta_result.summaries:
            service_modifier_summary = pd.DataFrame(delta_result.summaries)
        recompute_delta_from_substrate = True

    # Fail before writing scientific products if validation found a hard error.
    validation.raise_if_failed()

    ledger = build_point_ledger(
        exact_fields=final_fields,
        velocity=velocity,
        point_ledger_path=point_ledger_path,
        substrate_fields=substrate_fields,
        substrate_mode=substrate_mode,
        recompute_substrate_delta=recompute_delta_from_substrate,
    )

    # Derived ledgers.
    channels = ["rho", "j_l", "delta_rho", "delta_j_l"]
    stage_region = stage_region_burdens(ledger, channels)
    scopes = scope_burdens(ledger, channels)
    packet = packet_exposure(ledger)
    support = support_shell_load(ledger)
    catch = catch_rematch_localization(ledger)
    peaks = peak_locations(ledger, channels)
    control_cfg = cfg.get("control_law", {}) or cfg.get("absorber", {}) or {}
    control_summary = summarize_control_law(control_cfg)
    service_modifier_mode = "none"
    if field_delta_metadata:
        control_summary.update({f"service_synthesis_{k}": v for k, v in field_delta_metadata.items()})
        laws = sorted({str(m.get("law", "unknown")) for m in field_delta_metadata.get("modifiers", [])})
        if laws:
            service_modifier_mode = "+".join(laws)
    decision = decision_sheet(
        ledger,
        run_name=run_name,
        velocity=velocity,
        control_law_mode=control_cfg.get("mode", control_cfg.get("law", "none")),
        substrate_mode=public_substrate_mode(substrate_mode_user),
        thresholds=GateThresholds.from_config(cfg.get("thresholds", {})),
        service_modifier_mode=service_modifier_mode,
        control_summary=control_summary,
    )

    # Write products.
    write_table(service_facing_dataframe(ledger), out_dir / "point_ledger", table_format)
    write_table(stage_region, out_dir / "stage_region_burden", "csv")
    write_table(scopes, out_dir / "scope_burden", "csv")
    write_table(packet, out_dir / "packet_exposure", "csv")
    write_table(support, out_dir / "support_shell_load", "csv")
    write_table(catch, out_dir / "catch_rematch_localization", "csv")
    write_table(peaks, out_dir / "peak_locations", "csv")
    write_table(decision, out_dir / "decision_sheet", "csv")
    if field_delta_summary is not None:
        write_table(field_delta_summary, out_dir / "field_delta_summary", "csv")
    if service_modifier_summary is not None:
        write_table(service_modifier_summary, out_dir / "service_modifier_summary", "csv")
    if field_delta_metadata is not None:
        write_json(out_dir / "field_delta_metadata.json", field_delta_metadata)

    identity_check = None
    if cfg.get("validation", {}).get("identity_self_check", synthesis_enabled):
        identity_check = _run_identity_self_check(exact_fields, float(cfg.get("validation", {}).get("identity_tolerance", 1e-10)))
        validation.checks["identity_self_check"] = identity_check
        if not identity_check["passed"]:
            validation.errors.append("identity ADM recomputation self-check failed; inspect validation_report.json")

    status: dict[str, Any] = {
        "run_name": run_name,
        "velocity": velocity,
        "exact_fields": str(exact_fields_path),
        "exact_point_ledger": str(point_ledger_path) if point_ledger_path else None,
        "substrate_fields": str(substrate_fields_path) if substrate_fields_path else None,
        "substrate_mode": public_substrate_mode(substrate_mode_user),
        "control_law_mode": control_cfg.get("mode", control_cfg.get("law", "none")),
        "service_modifiers": field_delta_metadata.get("modified_service_fields", []) if field_delta_metadata else [],
        "service_modifier_mode": service_modifier_mode,
        "synthesis_enabled": synthesis_enabled,
        "rows": int(len(ledger)),
        "outputs": sorted(p.name for p in out_dir.iterdir() if p.is_file()),
        "caveats": [],
    }
    if control_cfg.get("mode", control_cfg.get("law", "none")) != "none" and not synthesis_enabled:
        status["caveats"].append(
            "Catch/rematch control metrics are sidecar diagnostics unless synthesis.enabled is true or coupled field inputs are supplied."
        )
    if synthesis_enabled and field_delta_metadata and any(name in {"rail_stretch", "throat_capacity"} for name in field_delta_metadata.get("modified_service_fields", [])):
        status["caveats"].append("Geometry-field synthesis uses a numerical R3 recomputation path.")
    if identity_check is not None:
        status["identity_self_check_passed"] = bool(identity_check["passed"])

    write_json(out_dir / "run_metadata.json", cfg)
    _write_validation(out_dir, validation)
    write_json(out_dir / "status.json", status)

    if outputs.get("figures", True):
        paths = plot_fields(ledger, out_dir / "figures")
        status["figures"] = [str(p.name) for p in paths]
        write_json(out_dir / "status.json", status)

    if outputs.get("report", True):
        write_run_report(
            out_dir / "report.md",
            run_name=run_name,
            decision=decision,
            peaks=peaks,
            packet=packet,
            support=support,
            catch=catch,
            status=status,
        )
    if validation.errors:
        _write_validation(out_dir, validation)
        validation.raise_if_failed()
    return out_dir


def validate_config_file(config_path: str | Path, output_json: str | Path | None = None) -> ValidationReport:
    cfg = load_config(config_path)
    report = ValidationReport()
    report.merge(validate_config_contract(cfg), "config")
    try:
        exact_fields_path = require_path(cfg, "inputs", "exact_fields")
        exact_fields = load_npz(exact_fields_path)
        report.merge(validate_fields(exact_fields, require_derived=True), "exact_fields")
        substrate_fields = None
        substrate_fields_path = cfg.get("inputs", {}).get("substrate_fields")
        if substrate_fields_path:
            if not Path(substrate_fields_path).exists():
                report.errors.append(f"substrate_fields path not found: {substrate_fields_path}")
            else:
                substrate_fields = load_npz(substrate_fields_path)
        if "exact_fields" in locals():
            report.merge(validate_substrate(substrate_fields, exact_fields), "substrate")
    except Exception as exc:
        report.errors.append(str(exc))
    if output_json:
        write_json(output_json, report.to_dict())
    return report


def compare_runs(run_dirs: list[str | Path], output_dir: str | Path) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    decisions = []
    for rd in run_dirs:
        rd = Path(rd)
        p = rd / "decision_sheet.csv"
        if not p.exists():
            raise FileNotFoundError(f"Missing decision sheet: {p}")
        decisions.append(pd.read_csv(p))
    decision = pd.concat(decisions, ignore_index=True)

    metric_cols = [
        "max_abs_delta_rho_packet",
        "max_abs_delta_j_packet",
        "max_abs_delta_j_catch",
        "support_shell_load_fraction",
        "catch_rematch_localization_fraction",
        "packet_exposure_score",
    ]
    rows = []
    for col in metric_cols:
        if col not in decision.columns:
            continue
        vals = decision[["run_name", col]].copy()
        vals = vals.sort_values(col, ascending=(col not in {"support_shell_load_fraction", "catch_rematch_localization_fraction"}))
        for rank, (_, row) in enumerate(vals.iterrows(), start=1):
            rows.append({"metric": col, "rank": rank, "run_name": row["run_name"], "value": row[col]})
    rankings = pd.DataFrame(rows)
    decision.to_csv(out / "comparison_decision_sheet.csv", index=False)
    rankings.to_csv(out / "delta_metric_rankings.csv", index=False)
    write_comparison_report(out / "comparison_report.md", decision, rankings)
    return out
