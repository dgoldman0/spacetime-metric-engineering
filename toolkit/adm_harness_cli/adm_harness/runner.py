from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pandas as pd

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
    summarize_absorber,
    support_shell_load,
)
from .plots import plot_fields
from .report import write_run_report, write_comparison_report


def run_from_config(config_path: str | Path, output_dir: str | Path | None = None) -> Path:
    cfg = load_config(config_path)
    run_name = cfg["run_name"]
    velocity = cfg.get("velocity")
    outputs = cfg.get("outputs", {})
    table_format = outputs.get("format", "csv")
    out_root = Path(output_dir or outputs.get("root", "runs"))
    out_dir = out_root / run_name
    if outputs.get("overwrite", True) and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    exact_fields_path = require_path(cfg, "inputs", "exact_fields")
    exact_fields = load_npz(exact_fields_path)
    point_ledger_path = cfg.get("inputs", {}).get("exact_point_ledger")
    if point_ledger_path and not Path(point_ledger_path).exists():
        raise FileNotFoundError(f"exact_point_ledger path not found: {point_ledger_path}")

    substrate_cfg = cfg.get("substrate", {})
    substrate_mode = substrate_cfg.get("mode", "none")
    substrate_fields = None
    substrate_fields_path = cfg.get("inputs", {}).get("substrate_fields")
    if substrate_fields_path:
        if not Path(substrate_fields_path).exists():
            raise FileNotFoundError(f"substrate_fields path not found: {substrate_fields_path}")
        substrate_fields = load_npz(substrate_fields_path)

    ledger = build_point_ledger(
        exact_fields=exact_fields,
        velocity=velocity,
        point_ledger_path=point_ledger_path,
        substrate_fields=substrate_fields,
        substrate_mode=substrate_mode,
    )

    # Derived ledgers.
    channels = ["rho", "j_l", "delta_rho", "delta_j_l"]
    stage_region = stage_region_burdens(ledger, channels)
    scopes = scope_burdens(ledger, channels)
    packet = packet_exposure(ledger)
    support = support_shell_load(ledger)
    catch = catch_rematch_localization(ledger)
    peaks = peak_locations(ledger, channels)
    absorber_summary = summarize_absorber(cfg.get("absorber", {}))
    decision = decision_sheet(
        ledger,
        run_name=run_name,
        velocity=velocity,
        absorber_mode=cfg.get("absorber", {}).get("mode", "none"),
        substrate_mode=substrate_mode,
        thresholds=GateThresholds.from_config(cfg.get("thresholds", {})),
        absorber_summary=absorber_summary,
    )

    # Write products.
    write_table(ledger, out_dir / "point_ledger", table_format)
    write_table(stage_region, out_dir / "stage_region_burden", "csv")
    write_table(scopes, out_dir / "scope_burden", "csv")
    write_table(packet, out_dir / "packet_exposure", "csv")
    write_table(support, out_dir / "support_shell_load", "csv")
    write_table(catch, out_dir / "catch_rematch_localization", "csv")
    write_table(peaks, out_dir / "peak_locations", "csv")
    write_table(decision, out_dir / "decision_sheet", "csv")

    status: dict[str, Any] = {
        "run_name": run_name,
        "velocity": velocity,
        "exact_fields": str(exact_fields_path),
        "exact_point_ledger": str(point_ledger_path) if point_ledger_path else None,
        "substrate_fields": str(substrate_fields_path) if substrate_fields_path else None,
        "substrate_mode": substrate_mode,
        "absorber_mode": cfg.get("absorber", {}).get("mode", "none"),
        "rows": int(len(ledger)),
        "outputs": sorted(p.name for p in out_dir.iterdir() if p.is_file()),
        "caveats": [],
    }
    if cfg.get("absorber", {}).get("mode", "none") != "none":
        status["caveats"].append(
            "Absorber metrics are sidecar diagnostics in this CLI version unless coupled field inputs are supplied."
        )
    write_json(out_dir / "run_metadata.json", cfg)
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
    return out_dir


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
