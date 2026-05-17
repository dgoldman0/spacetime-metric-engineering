from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pandas as pd
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = PACKAGE_ROOT.parent.parent
for import_root in (PACKAGE_ROOT, SCRIPT_DIR):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from adm_harness.config import load_config
from adm_harness.runner import run_from_config, validate_config_file
from analyze_signed_objective import analyze_run, build_pair_summary, prepare_baseline, write_report as write_signed_report
from test_support_shell_packet_safety import run_overlay


DEFAULT_PACKET_INPUT = REPO_ROOT / "included_bundles" / "active_rail_v_sweep.zip"
DEFAULT_PACKET_MEMBER = "highres_41x73/V5_tuned_w0569_eta200.csv"
SOURCE_CHANNELS = ["rho", "j_l", "delta_rho", "delta_j_l"]
SOURCE_SCOPES = ["global", "catch_support", "support", "packet", "catch_packet", "other"]
RICH_OBJECTIVE_WEIGHTS = {
    "rho": {
        "global_abs_change": 1.0e3,
        "packet_increment_abs": 1.0e6,
        "packet_peak_growth": 1.0e6,
        "catch_support_increment_abs": 1.0e2,
    },
    "j_l": {
        "global_abs_change": 0.25,
        "packet_increment_abs": 2.5,
        "packet_peak_growth": 250.0,
        "catch_support_increment_abs": 0.025,
    },
    "delta_rho": {
        "global_abs_change": 1.0e3,
        "packet_increment_abs": 1.0e6,
        "packet_peak_growth": 1.0e6,
        "catch_support_increment_abs": 1.0e2,
    },
    "delta_j_l": {
        "global_abs_change": 1.0,
        "packet_increment_abs": 10.0,
        "packet_peak_growth": 1000.0,
        "catch_support_increment_abs": 0.1,
    },
}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _run_validated_config(config_path: Path, output_root: Path, label: str) -> Path:
    validation_path = output_root / f"validation_{label}.json"
    validation = validate_config_file(config_path, validation_path)
    if not validation.ok:
        errors = "; ".join(validation.errors) or "unknown validation failure"
        raise SystemExit(f"{config_path} failed validation: {errors}")
    return run_from_config(config_path, output_root)


def _negative_counterpart_config(target_config: Path, output_root: Path) -> Path:
    cfg = load_config(target_config)
    neg_cfg = copy.deepcopy(cfg)
    run_name = str(neg_cfg.get("run_name", target_config.stem))
    if "_pos_" in run_name:
        neg_cfg["run_name"] = run_name.replace("_pos_", "_neg_")
    elif run_name.endswith("_pos"):
        neg_cfg["run_name"] = f"{run_name[:-4]}_neg"
    else:
        neg_cfg["run_name"] = f"{run_name}_neg"

    carrying_flow = neg_cfg.setdefault("service", {}).setdefault("carrying_flow", {})
    amplitude = abs(float(carrying_flow.get("amplitude", 0.0)))
    if amplitude == 0.0:
        raise SystemExit(f"Target config has zero carrying_flow amplitude: {target_config}")
    carrying_flow["amplitude"] = -amplitude
    carrying_flow["max_abs_change"] = abs(float(carrying_flow.get("max_abs_change", amplitude)))

    out_dir = output_root / "_generated_configs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{target_config.stem}_negative_counterpart.yaml"
    out_path.write_text(yaml.safe_dump(neg_cfg, sort_keys=False), encoding="utf-8")
    return out_path


def _read_ledger(run_dir: Path) -> pd.DataFrame:
    path = run_dir / "point_ledger.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing point ledger: {path}")
    return pd.read_csv(path)


def _merge_with_baseline(run_dir: Path, baseline: pd.DataFrame) -> pd.DataFrame:
    required = {"s", "l", "delta_j_l", "delta_rho", "volume", "stage", "packet_live", "support_shell"}
    df = _read_ledger(run_dir)
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"{run_dir / 'point_ledger.csv'} missing columns: {sorted(missing)}")
    merged = df.merge(baseline, on=["s", "l"], how="left", validate="one_to_one")
    if merged["baseline_delta_j_l"].isna().any():
        raise SystemExit(f"{run_dir / 'point_ledger.csv'} did not align with baseline grid")
    return merged


def _baseline_frame(baseline_dir: Path) -> pd.DataFrame:
    baseline = _read_ledger(baseline_dir)
    required = {"s", "l", "delta_j_l", "delta_rho"}
    missing = required - set(baseline.columns)
    if missing:
        raise SystemExit(f"{baseline_dir / 'point_ledger.csv'} missing columns: {sorted(missing)}")
    cols = ["s", "l"] + [channel for channel in SOURCE_CHANNELS if channel in baseline.columns]
    return baseline[cols].rename(columns={channel: f"baseline_{channel}" for channel in SOURCE_CHANNELS})


def _token(value: float) -> str:
    text = f"{value:.10g}"
    return text.replace("-", "m").replace("+", "").replace(".", "p").replace("e", "e")


def _v_label(cfg: dict[str, Any]) -> str:
    v_value = cfg.get("velocity", (cfg.get("service", {}) or {}).get("velocity"))
    try:
        v = float(v_value)
    except (TypeError, ValueError):
        return "v"
    if v.is_integer():
        return f"v{int(v)}"
    return f"v{_token(v)}"


def _has_positive_marker(run_name: str) -> bool:
    return "_pos_" in run_name or run_name.endswith("_pos")


def _positive_target_config(target_config: Path, output_root: Path) -> Path:
    cfg = load_config(target_config)
    run_name = str(cfg.get("run_name", target_config.stem))
    carrying_flow = cfg.get("service", {}).get("carrying_flow", {})
    amplitude = float(carrying_flow.get("amplitude", 0.0))
    if amplitude <= 0.0 or _has_positive_marker(run_name):
        return target_config

    pos_cfg = copy.deepcopy(cfg)
    if run_name.endswith("_target"):
        pos_cfg["run_name"] = run_name.replace("_target", "_pos_target")
    else:
        pos_cfg["run_name"] = f"{run_name}_pos"

    out_dir = output_root / "_generated_configs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{target_config.stem}_positive_counterpart.yaml"
    out_path.write_text(yaml.safe_dump(pos_cfg, sort_keys=False), encoding="utf-8")
    return out_path


def _scope_masks(df: pd.DataFrame) -> dict[str, pd.Series]:
    packet = df["packet_live"].astype(bool)
    support = df["support_shell"].astype(bool)
    catch = df["stage"].astype(str).eq("catch_rematch")
    catch_support = catch & support
    catch_packet = catch & packet
    return {
        "global": pd.Series(True, index=df.index),
        "catch_support": catch_support,
        "support": support,
        "packet": packet,
        "catch_packet": catch_packet,
        "other": ~(catch_support | packet),
    }


def _channel_rich_metrics(df: pd.DataFrame, channel: str, masks: dict[str, pd.Series]) -> dict[str, Any]:
    base_col = f"baseline_{channel}"
    run = df[channel].astype(float)
    base = df[base_col].astype(float)
    vol = df["volume"].astype(float)
    inc = run - base

    row: dict[str, Any] = {
        "channel": channel,
        "global_base_abs_burden": float((base.abs() * vol).sum()),
        "global_run_abs_burden": float((run.abs() * vol).sum()),
        "global_abs_change": float((run.abs() * vol).sum() - (base.abs() * vol).sum()),
        "global_increment_abs": float((inc.abs() * vol).sum()),
        "global_signed_increment": float((inc * vol).sum()),
        "global_peak_abs_change": float(run.abs().max() - base.abs().max()),
    }
    for scope, mask in masks.items():
        scoped_inc = inc[mask]
        scoped_base = base[mask]
        scoped_run = run[mask]
        scoped_vol = vol[mask]
        increment_abs = float((scoped_inc.abs() * scoped_vol).sum())
        aligned = float((np.sign(scoped_base) * scoped_inc * scoped_vol).sum()) if increment_abs else 0.0
        row[f"{scope}_increment_abs"] = increment_abs
        row[f"{scope}_signed_increment"] = float((scoped_inc * scoped_vol).sum())
        row[f"{scope}_abs_change"] = float((scoped_run.abs() * scoped_vol).sum() - (scoped_base.abs() * scoped_vol).sum())
        row[f"{scope}_baseline_opposition_fraction"] = -aligned / increment_abs if increment_abs else 0.0
        row[f"{scope}_peak_abs_change"] = (
            float(scoped_run.abs().max() - scoped_base.abs().max()) if len(scoped_run) else 0.0
        )
    row["packet_fraction_of_increment_abs"] = (
        row["packet_increment_abs"] / row["global_increment_abs"] if row["global_increment_abs"] else 0.0
    )
    row["catch_support_fraction_of_increment_abs"] = (
        row["catch_support_increment_abs"] / row["global_increment_abs"] if row["global_increment_abs"] else 0.0
    )
    return row


def _rich_source_objective_summary(root: Path, baseline_run: str, run_names: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline = _baseline_frame(root / baseline_run)
    channel_rows = []
    aggregate_rows = []
    for run_name in run_names:
        merged = _merge_with_baseline(root / run_name, baseline)
        available = [channel for channel in SOURCE_CHANNELS if channel in merged.columns and f"baseline_{channel}" in merged.columns]
        if not available:
            raise SystemExit(f"No source channels available for richer objective in {run_name}")
        masks = _scope_masks(merged)
        objective = 0.0
        aggregate: dict[str, Any] = {
            "run_name": run_name,
            "channels": ",".join(available),
            "global_increment_abs_all_channels": 0.0,
            "packet_increment_abs_all_channels": 0.0,
            "catch_support_increment_abs_all_channels": 0.0,
            "positive_packet_peak_growth_all_channels": 0.0,
        }
        for channel in available:
            metrics = _channel_rich_metrics(merged, channel, masks)
            metrics["run_name"] = run_name
            channel_rows.append(metrics)
            weights = RICH_OBJECTIVE_WEIGHTS[channel]
            objective += weights["global_abs_change"] * metrics["global_abs_change"]
            objective += weights["packet_increment_abs"] * metrics["packet_increment_abs"]
            objective += weights["catch_support_increment_abs"] * metrics["catch_support_increment_abs"]
            objective += weights["packet_peak_growth"] * max(0.0, metrics["packet_peak_abs_change"])
            aggregate[f"{channel}_global_increment_abs"] = metrics["global_increment_abs"]
            aggregate[f"{channel}_packet_increment_abs"] = metrics["packet_increment_abs"]
            aggregate[f"{channel}_catch_support_increment_abs"] = metrics["catch_support_increment_abs"]
            aggregate[f"{channel}_global_abs_change"] = metrics["global_abs_change"]
            aggregate[f"{channel}_packet_peak_abs_change"] = metrics["packet_peak_abs_change"]
            aggregate[f"{channel}_catch_support_opposition_fraction"] = metrics["catch_support_baseline_opposition_fraction"]
            aggregate["global_increment_abs_all_channels"] += metrics["global_increment_abs"]
            aggregate["packet_increment_abs_all_channels"] += metrics["packet_increment_abs"]
            aggregate["catch_support_increment_abs_all_channels"] += metrics["catch_support_increment_abs"]
            aggregate["positive_packet_peak_growth_all_channels"] += max(0.0, metrics["packet_peak_abs_change"])
        aggregate["packet_fraction_all_channels"] = (
            aggregate["packet_increment_abs_all_channels"] / aggregate["global_increment_abs_all_channels"]
            if aggregate["global_increment_abs_all_channels"]
            else 0.0
        )
        aggregate["catch_support_fraction_all_channels"] = (
            aggregate["catch_support_increment_abs_all_channels"] / aggregate["global_increment_abs_all_channels"]
            if aggregate["global_increment_abs_all_channels"]
            else 0.0
        )
        aggregate["rich_source_objective_lower_better"] = float(objective)
        aggregate["rich_source_relief_score_higher_better"] = -float(objective)
        aggregate_rows.append(aggregate)

    channels = pd.DataFrame(channel_rows)
    summary = pd.DataFrame(aggregate_rows).sort_values("rich_source_objective_lower_better")
    channels.to_csv(root / "validation_ladder_rich_source_objective_channels.csv", index=False)
    summary.to_csv(root / "validation_ladder_rich_source_objective_summary.csv", index=False)
    return summary, channels


def _routing_summary(root: Path, baseline_run: str, run_names: list[str]) -> pd.DataFrame:
    baseline = _baseline_frame(root / baseline_run)
    rows = []
    for run_name in run_names:
        merged = _merge_with_baseline(root / run_name, baseline)
        vol = merged["volume"].astype(float)
        inc_j = merged["delta_j_l"].astype(float) - merged["baseline_delta_j_l"].astype(float)
        inc_rho = merged["delta_rho"].astype(float) - merged["baseline_delta_rho"].astype(float)
        abs_inc_j = inc_j.abs() * vol
        abs_inc_rho = inc_rho.abs() * vol

        packet = merged["packet_live"].astype(bool)
        support = merged["support_shell"].astype(bool)
        catch = merged["stage"].astype(str).eq("catch_rematch")
        catch_support = catch & support

        global_inc_j = float(abs_inc_j.sum())
        catch_support_inc_j = float(abs_inc_j[catch_support].sum())
        support_inc_j = float(abs_inc_j[support].sum())
        packet_inc_j = float(abs_inc_j[packet].sum())
        packet_inc_rho = float(abs_inc_rho[packet].sum())

        catch_support_fraction = catch_support_inc_j / global_inc_j if global_inc_j else 0.0
        packet_j_fraction = packet_inc_j / global_inc_j if global_inc_j else 0.0
        support_fraction = support_inc_j / global_inc_j if global_inc_j else 0.0
        score = (
            (1.0 - catch_support_fraction)
            + 10.0 * packet_j_fraction
            + 1.0e6 * packet_inc_rho
        ) * (1.0 + global_inc_j / 1.0e-6)

        rows.append(
            {
                "run_name": run_name,
                "global_abs_incremental_delta_j_l": global_inc_j,
                "catch_support_abs_incremental_delta_j_l": catch_support_inc_j,
                "support_abs_incremental_delta_j_l": support_inc_j,
                "packet_abs_incremental_delta_j_l": packet_inc_j,
                "packet_abs_incremental_delta_rho": packet_inc_rho,
                "catch_support_incremental_fraction": catch_support_fraction,
                "support_incremental_fraction": support_fraction,
                "packet_incremental_j_fraction": packet_j_fraction,
                "support_routing_score_lower_better": score,
            }
        )
    out = pd.DataFrame(rows).sort_values("support_routing_score_lower_better")
    out.insert(0, "support_routing_rank", range(1, len(out) + 1))
    out.to_csv(root / "validation_ladder_routing_summary.csv", index=False)
    return out


def _signed_objective(root: Path, baseline_run: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline_path = root / baseline_run / "point_ledger.csv"
    baseline = prepare_baseline(baseline_path)
    rows = []
    for ledger in sorted(root.glob("*/point_ledger.csv")):
        if ledger.parent.name == baseline_run or ledger.parent.name.startswith("_"):
            continue
        rows.append(analyze_run(root, baseline, ledger.parent))
    if not rows:
        raise SystemExit(f"No target ledgers found under {root}")

    summary = pd.DataFrame(rows).sort_values("signed_source_objective_delta_lower_better")
    pairs = build_pair_summary(summary)
    prefix = "validation_ladder_signed_objective"
    summary.to_csv(root / f"{prefix}_summary.csv", index=False)
    pairs.to_csv(root / f"{prefix}_pair_comparison.csv", index=False)
    write_signed_report(root / f"{prefix}_report.md", summary, pairs, baseline_run)
    return summary, pairs


def _balance_summary(root: Path, baseline_run: str, run_names: list[str]) -> pd.DataFrame:
    baseline = _baseline_frame(root / baseline_run)
    rows = []
    for run_name in run_names:
        merged = _merge_with_baseline(root / run_name, baseline)
        vol = merged["volume"].astype(float)
        inc_j = (merged["delta_j_l"].astype(float) - merged["baseline_delta_j_l"].astype(float)) * vol
        inc_rho = (merged["delta_rho"].astype(float) - merged["baseline_delta_rho"].astype(float)) * vol

        packet = merged["packet_live"].astype(bool)
        support = merged["support_shell"].astype(bool)
        catch = merged["stage"].astype(str).eq("catch_rematch")
        catch_support = catch & support
        catch_support_only = catch_support & ~packet
        packet_only = packet & ~catch_support
        overlap = catch_support & packet
        other = ~(catch_support | packet)

        row: dict[str, Any] = {"run_name": run_name}
        for label, inc in [("j", inc_j), ("rho", inc_rho)]:
            global_abs = float(inc.abs().sum())
            global_signed = float(inc.sum())
            parts_abs = {
                "catch_support_only": float(inc[catch_support_only].abs().sum()),
                "packet_only": float(inc[packet_only].abs().sum()),
                "catch_support_packet_overlap": float(inc[overlap].abs().sum()),
                "other": float(inc[other].abs().sum()),
            }
            parts_signed = {
                "catch_support_only": float(inc[catch_support_only].sum()),
                "packet_only": float(inc[packet_only].sum()),
                "catch_support_packet_overlap": float(inc[overlap].sum()),
                "other": float(inc[other].sum()),
            }
            abs_closure_error = abs(sum(parts_abs.values()) - global_abs)
            signed_closure_error = abs(sum(parts_signed.values()) - global_signed)

            row[f"global_abs_incremental_delta_{label}"] = global_abs
            row[f"global_signed_incremental_delta_{label}"] = global_signed
            for part, value in parts_abs.items():
                row[f"{part}_abs_incremental_delta_{label}"] = value
            for part, value in parts_signed.items():
                row[f"{part}_signed_incremental_delta_{label}"] = value
            row[f"abs_partition_closure_error_delta_{label}"] = abs_closure_error
            row[f"signed_partition_closure_error_delta_{label}"] = signed_closure_error
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(root / "validation_ladder_balance_summary.csv", index=False)
    return out


def _packet_overlay(args: argparse.Namespace, root: Path) -> pd.DataFrame:
    amplitudes = getattr(args, "overlay_amplitudes", args.amplitudes)
    overlay_args = SimpleNamespace(
        input=str(args.packet_input),
        member=args.packet_member,
        output_dir=str(root / "packet_safety_overlay"),
        support_radius=args.support_radius,
        support_multiplier=args.support_multiplier,
        catch_lead=args.catch_lead,
        temporal_width=args.temporal_width,
        smoothing_passes=args.smoothing_passes,
        amplitudes=amplitudes,
    )
    summary, _ = run_overlay(overlay_args)
    return summary


def _target_packet_row(packet_summary: pd.DataFrame, target_amplitude: float) -> pd.Series:
    sign = "pos" if target_amplitude > 0 else "neg"
    abs_amp = abs(float(target_amplitude))
    mask = packet_summary["sign"].eq(sign) & np.isclose(packet_summary["abs_amplitude"].astype(float), abs_amp)
    if not mask.any():
        raise SystemExit(f"Packet overlay summary does not contain target amplitude {target_amplitude:g}")
    return packet_summary[mask].iloc[0]


def _support_shell_amplitude_config(target_config: Path, output_root: Path, amplitude: float) -> Path:
    cfg = load_config(target_config)
    amp = float(amplitude)
    sign_name = "pos" if amp >= 0.0 else "neg"
    abs_amp = abs(amp)
    run_name = f"{_v_label(cfg)}_support_shell_ramp_{sign_name}_a{_token(abs_amp)}"
    cfg["run_name"] = run_name
    carrying_flow = cfg.setdefault("service", {}).setdefault("carrying_flow", {})
    carrying_flow["amplitude"] = amp
    carrying_flow["max_abs_change"] = abs_amp

    out_dir = output_root / "_generated_configs" / "amplitude_ramp"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{run_name}.yaml"
    out_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return out_path


def _run_amplitude_ramp(args: argparse.Namespace, root: Path, target_config: Path) -> pd.DataFrame:
    rows = []
    if args.skip_amplitude_ramp:
        out = pd.DataFrame(rows)
        out.to_csv(root / "validation_ladder_amplitude_ramp_runs.csv", index=False)
        return out

    for amplitude in args.ramp_amplitudes:
        cfg = _support_shell_amplitude_config(target_config, root, float(amplitude))
        run_name = str(load_config(cfg)["run_name"])
        row: dict[str, Any] = {
            "run_name": run_name,
            "amplitude": float(amplitude),
            "config": str(cfg),
            "run_status": "ok",
            "error": "",
        }
        try:
            _run_validated_config(cfg, root, f"ramp_{_token(float(amplitude))}")
        except (Exception, SystemExit) as exc:
            row["run_status"] = "failed"
            row["error"] = str(exc)
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(root / "validation_ladder_amplitude_ramp_runs.csv", index=False)
    return out


def _packet_row_for_amplitude(packet_summary: pd.DataFrame, amplitude: float) -> pd.Series | None:
    sign = "pos" if amplitude > 0 else "neg"
    abs_amp = abs(float(amplitude))
    mask = packet_summary["sign"].eq(sign) & np.isclose(packet_summary["abs_amplitude"].astype(float), abs_amp)
    if not mask.any():
        return None
    return packet_summary[mask].iloc[0]


def _amplitude_ramp_summary(
    *,
    root: Path,
    ramp_runs: pd.DataFrame,
    routing: pd.DataFrame,
    rich_summary: pd.DataFrame,
    packet_summary: pd.DataFrame,
    args: argparse.Namespace,
) -> pd.DataFrame:
    rows = []
    if ramp_runs.empty:
        out = pd.DataFrame(rows)
        out.to_csv(root / "validation_ladder_amplitude_ramp_summary.csv", index=False)
        return out

    for _, run in ramp_runs.iterrows():
        run_name = str(run["run_name"])
        amplitude = float(run["amplitude"])
        row: dict[str, Any] = {
            "run_name": run_name,
            "amplitude": amplitude,
            "run_status": run["run_status"],
            "error": run["error"],
        }
        if run["run_status"] != "ok":
            row["hard_gate_passed"] = False
            row["warning_flag"] = True
            row["status_class"] = "run_failed"
            rows.append(row)
            continue

        route = routing[routing["run_name"].eq(run_name)]
        rich = rich_summary[rich_summary["run_name"].eq(run_name)]
        packet = _packet_row_for_amplitude(packet_summary, amplitude)
        if route.empty or rich.empty or packet is None:
            row["hard_gate_passed"] = False
            row["warning_flag"] = True
            row["status_class"] = "missing_metrics"
            rows.append(row)
            continue

        route_row = route.iloc[0]
        rich_row = rich.iloc[0]
        max_packet_norm = float(packet["max_packet_norm_live"])
        baseline_margin = -float(packet["baseline_max_packet_norm_live"])
        packet_margin = -max_packet_norm
        max_abs_packet_change = float(packet["max_abs_packet_norm_live_change"])
        packet_change_fraction = max_abs_packet_change / baseline_margin if baseline_margin else float("inf")
        packet_margin_fraction = packet_margin / baseline_margin if baseline_margin else float("-inf")

        routing_passed = (
            float(route_row["catch_support_incremental_fraction"]) >= args.min_catch_support_fraction
            and float(route_row["packet_incremental_j_fraction"]) <= args.max_packet_j_fraction
            and float(route_row["packet_abs_incremental_delta_rho"]) <= args.max_packet_abs_delta_rho
        )
        packet_passed = bool(packet["packet_safe"]) and int(packet["positive_packet_norm_live"]) == 0
        rich_packet_passed = float(rich_row["packet_increment_abs_all_channels"]) <= args.max_rich_packet_increment_abs
        hard_gate_passed = bool(routing_passed and packet_passed and rich_packet_passed)
        warning_flag = bool(
            packet_change_fraction >= args.ramp_warning_fraction
            or packet_margin_fraction <= 1.0 - args.ramp_warning_fraction
            or not hard_gate_passed
        )

        row.update(
            {
                "global_abs_incremental_delta_j_l": float(route_row["global_abs_incremental_delta_j_l"]),
                "catch_support_incremental_fraction": float(route_row["catch_support_incremental_fraction"]),
                "packet_incremental_j_fraction": float(route_row["packet_incremental_j_fraction"]),
                "packet_abs_incremental_delta_rho": float(route_row["packet_abs_incremental_delta_rho"]),
                "rich_source_objective_lower_better": float(rich_row["rich_source_objective_lower_better"]),
                "rich_packet_increment_abs_all_channels": float(rich_row["packet_increment_abs_all_channels"]),
                "rich_packet_fraction_all_channels": float(rich_row["packet_fraction_all_channels"]),
                "max_packet_norm_live": max_packet_norm,
                "packet_margin": packet_margin,
                "packet_margin_fraction_of_baseline": packet_margin_fraction,
                "max_abs_packet_norm_live_change": max_abs_packet_change,
                "packet_norm_change_fraction_of_baseline_margin": packet_change_fraction,
                "packet_safe": bool(packet["packet_safe"]),
                "positive_packet_norm_live": int(packet["positive_packet_norm_live"]),
                "routing_gate_passed": bool(routing_passed),
                "packet_gate_passed": bool(packet_passed),
                "rich_packet_gate_passed": bool(rich_packet_passed),
                "hard_gate_passed": hard_gate_passed,
                "warning_flag": warning_flag,
                "status_class": "pass" if hard_gate_passed and not warning_flag else ("warning" if hard_gate_passed else "fail"),
            }
        )
        rows.append(row)

    out = pd.DataFrame(rows).sort_values("amplitude")
    out.to_csv(root / "validation_ladder_amplitude_ramp_summary.csv", index=False)
    v_label = _v_label(load_config(Path(args.target_config))) if hasattr(args, "target_config") else "v"
    _write_amplitude_ramp_report(root, out, v_label)
    return out


def _write_amplitude_ramp_report(root: Path, ramp_summary: pd.DataFrame, v_label: str) -> None:
    with (root / "validation_ladder_amplitude_ramp_report.md").open("w", encoding="utf-8") as f:
        f.write(f"# {v_label.upper()} Support-Shell Amplitude Ramp\n\n")
        if ramp_summary.empty:
            f.write("Amplitude ramp was skipped.\n")
            return
        ok = ramp_summary[ramp_summary["run_status"].eq("ok")]
        hard_pass = ok[ok["hard_gate_passed"].astype(bool)] if "hard_gate_passed" in ok.columns else pd.DataFrame()
        clean_pass = ok[ok["status_class"].eq("pass")] if "status_class" in ok.columns else pd.DataFrame()
        warnings = ok[ok["warning_flag"].astype(bool)] if "warning_flag" in ok.columns else pd.DataFrame()
        failures = ramp_summary[~ramp_summary["status_class"].isin(["pass", "warning"])] if "status_class" in ramp_summary.columns else pd.DataFrame()
        last_clean_pass = float(clean_pass["amplitude"].max()) if len(clean_pass) else float("nan")
        last_hard_pass = float(hard_pass["amplitude"].max()) if len(hard_pass) else float("nan")
        first_warning = float(warnings["amplitude"].min()) if len(warnings) else float("nan")
        first_failure = float(failures["amplitude"].min()) if len(failures) else float("nan")
        f.write(f"Last no-warning pass amplitude: `{last_clean_pass:.6g}`.\n\n")
        f.write(f"Last hard-pass amplitude: `{last_hard_pass:.6g}`.\n\n")
        f.write(f"First warning amplitude: `{first_warning:.6g}`.\n\n")
        f.write(f"First failure amplitude: `{first_failure:.6g}`.\n\n")
        cols = [
            "amplitude",
            "status_class",
            "hard_gate_passed",
            "catch_support_incremental_fraction",
            "packet_incremental_j_fraction",
            "rich_packet_increment_abs_all_channels",
            "max_packet_norm_live",
            "packet_margin_fraction_of_baseline",
            "packet_norm_change_fraction_of_baseline_margin",
        ]
        present = [col for col in cols if col in ramp_summary.columns]
        f.write("## Ramp Summary\n\n")
        f.write(ramp_summary[present].to_markdown(index=False))
        f.write("\n")


def _decision_sheet(
    *,
    root: Path,
    target_run: str,
    routing: pd.DataFrame,
    rich_summary: pd.DataFrame,
    packet_summary: pd.DataFrame,
    signed_summary: pd.DataFrame,
    sign_pairs: pd.DataFrame,
    balance: pd.DataFrame,
    target_amplitude: float,
    args: argparse.Namespace,
) -> pd.DataFrame:
    target_routing = routing[routing["run_name"].eq(target_run)].iloc[0]
    target_rich = rich_summary[rich_summary["run_name"].eq(target_run)].iloc[0]
    target_packet = _target_packet_row(packet_summary, target_amplitude)
    target_signed = signed_summary[signed_summary["run_name"].eq(target_run)].iloc[0]
    target_balance = balance[balance["run_name"].eq(target_run)].iloc[0]

    pair_winner = "none"
    pair_gap = 0.0
    family_key = target_run.replace("_pos_", "_SIGN_").replace("_neg_", "_SIGN_")
    if len(sign_pairs):
        pair = sign_pairs[sign_pairs["family_key"].eq(family_key)]
        if len(pair):
            pair_winner = str(pair.iloc[0]["winner"])
            pair_gap = float(pair.iloc[0]["relative_objective_gap"])

    closure_error = max(
        float(target_balance["abs_partition_closure_error_delta_j"]),
        float(target_balance["signed_partition_closure_error_delta_j"]),
        float(target_balance["abs_partition_closure_error_delta_rho"]),
        float(target_balance["signed_partition_closure_error_delta_rho"]),
    )
    nominal_overlay = packet_summary[
        packet_summary["abs_amplitude"].astype(float).isin([abs(float(a)) for a in args.amplitudes])
    ]

    rows = [
        {
            "stage": "routing",
            "check": "catch_support_incremental_fraction",
            "value": float(target_routing["catch_support_incremental_fraction"]),
            "threshold": f">= {args.min_catch_support_fraction:g}",
            "required": True,
            "passed": bool(target_routing["catch_support_incremental_fraction"] >= args.min_catch_support_fraction),
            "note": "incremental delta_j_l should land in catch/support infrastructure",
        },
        {
            "stage": "routing",
            "check": "packet_incremental_j_fraction",
            "value": float(target_routing["packet_incremental_j_fraction"]),
            "threshold": f"<= {args.max_packet_j_fraction:g}",
            "required": True,
            "passed": bool(target_routing["packet_incremental_j_fraction"] <= args.max_packet_j_fraction),
            "note": "packet momentum contamination should stay quiet",
        },
        {
            "stage": "routing",
            "check": "packet_abs_incremental_delta_rho",
            "value": float(target_routing["packet_abs_incremental_delta_rho"]),
            "threshold": f"<= {args.max_packet_abs_delta_rho:g}",
            "required": True,
            "passed": bool(target_routing["packet_abs_incremental_delta_rho"] <= args.max_packet_abs_delta_rho),
            "note": "packet density increment should stay quiet",
        },
        {
            "stage": "packet_overlay",
            "check": "target_positive_packet_norm_live",
            "value": float(target_packet["positive_packet_norm_live"]),
            "threshold": "== 0",
            "required": True,
            "passed": bool(int(target_packet["positive_packet_norm_live"]) == 0),
            "note": "target overlay should leave all live packet norms negative",
        },
        {
            "stage": "packet_overlay",
            "check": "nominal_overlay_variants_safe",
            "value": float(nominal_overlay["packet_safe"].astype(bool).all()),
            "threshold": "true",
            "required": True,
            "passed": bool(nominal_overlay["packet_safe"].astype(bool).all()),
            "note": "the nominal sign/amplitude ladder should remain packet-safe; load ramp failures are summarized separately",
        },
        {
            "stage": "rich_source_objective",
            "check": "packet_increment_abs_all_channels",
            "value": float(target_rich["packet_increment_abs_all_channels"]),
            "threshold": f"<= {args.max_rich_packet_increment_abs:g}",
            "required": True,
            "passed": bool(target_rich["packet_increment_abs_all_channels"] <= args.max_rich_packet_increment_abs),
            "note": "rho/j_l/delta_rho/delta_j_l packet exposure should remain quiet as a group",
        },
        {
            "stage": "rich_source_objective",
            "check": "rich_source_objective",
            "value": float(target_rich["rich_source_objective_lower_better"]),
            "threshold": "diagnostic",
            "required": False,
            "passed": True,
            "note": "weighted multi-channel source objective; lower is better",
        },
        {
            "stage": "signed_objective",
            "check": "positive_sign_pair_winner",
            "value": 1.0 if pair_winner == "pos" else 0.0,
            "threshold": "diagnostic",
            "required": False,
            "passed": bool(pair_winner in {"pos", "none"}),
            "note": f"winner={pair_winner}, relative_gap={pair_gap:.6g}; sign remains a tie-breaker unless the gap grows",
        },
        {
            "stage": "signed_objective",
            "check": "target_objective_delta",
            "value": float(target_signed["signed_source_objective_delta_lower_better"]),
            "threshold": "diagnostic",
            "required": False,
            "passed": True,
            "note": "lower is better; used for comparison, not as a hard V5 safety gate",
        },
        {
            "stage": "balance",
            "check": "partition_closure_error",
            "value": closure_error,
            "threshold": f"<= {args.max_partition_closure_error:g}",
            "required": True,
            "passed": bool(closure_error <= args.max_partition_closure_error),
            "note": "reduced ledger bookkeeping should close across disjoint masks",
        },
    ]
    out = pd.DataFrame(rows)
    out.to_csv(root / "validation_ladder_decision_sheet.csv", index=False)
    return out


def _write_ladder_report(
    *,
    root: Path,
    v_label: str,
    baseline_run: str,
    target_run: str,
    negative_run: str,
    target_amplitude: float,
    decision: pd.DataFrame,
    routing: pd.DataFrame,
    rich_summary: pd.DataFrame,
    packet_summary: pd.DataFrame,
    signed_summary: pd.DataFrame,
    sign_pairs: pd.DataFrame,
    balance: pd.DataFrame,
    ramp_summary: pd.DataFrame,
) -> None:
    required = decision[decision["required"].astype(bool)]
    passed = bool(required["passed"].astype(bool).all())
    target_routing = routing[routing["run_name"].eq(target_run)]
    target_rich = rich_summary[rich_summary["run_name"].eq(target_run)]
    target_packet = _target_packet_row(packet_summary, target_amplitude).to_frame().T
    target_signed = signed_summary[signed_summary["run_name"].eq(target_run)]
    target_balance = balance[balance["run_name"].eq(target_run)]

    routing_cols = [
        "run_name",
        "global_abs_incremental_delta_j_l",
        "catch_support_incremental_fraction",
        "support_incremental_fraction",
        "packet_incremental_j_fraction",
        "packet_abs_incremental_delta_rho",
        "support_routing_score_lower_better",
    ]
    packet_cols = [
        "run_name",
        "amplitude",
        "max_packet_norm_live",
        "positive_packet_norm_live",
        "max_packet_norm_live_change",
        "max_abs_packet_norm_live_change",
        "packet_safe",
    ]
    signed_cols = [
        "run_name",
        "sign",
        "global_j_abs_change",
        "catch_support_j_abs_change",
        "catch_support_j_baseline_opposition_fraction",
        "packet_j_abs_change",
        "packet_rho_abs_change",
        "signed_source_objective_delta_lower_better",
    ]
    rich_cols = [
        "run_name",
        "rich_source_objective_lower_better",
        "global_increment_abs_all_channels",
        "catch_support_increment_abs_all_channels",
        "packet_increment_abs_all_channels",
        "packet_fraction_all_channels",
        "delta_j_l_catch_support_opposition_fraction",
    ]
    balance_cols = [
        "run_name",
        "global_abs_incremental_delta_j",
        "global_signed_incremental_delta_j",
        "catch_support_only_abs_incremental_delta_j",
        "packet_only_abs_incremental_delta_j",
        "other_abs_incremental_delta_j",
        "abs_partition_closure_error_delta_j",
    ]

    with (root / "validation_ladder_report.md").open("w", encoding="utf-8") as f:
        f.write(f"# {v_label.upper()} Validation Ladder\n\n")
        f.write(f"Baseline run: `{baseline_run}`. Target run: `{target_run}`. Negative counterpart: `{negative_run}`.\n\n")
        f.write(f"Required-gate result: `{'PASS' if passed else 'FAIL'}`.\n\n")
        f.write("## Decision Sheet\n\n")
        f.write(decision.to_markdown(index=False))
        f.write("\n\n## Routing Gate\n\n")
        f.write(target_routing[routing_cols].to_markdown(index=False))
        f.write("\n\n## Packet-Safety Overlay\n\n")
        f.write(target_packet[packet_cols].to_markdown(index=False))
        nominal_rows = decision[decision["check"].eq("nominal_overlay_variants_safe")]
        nominal_safe = bool(nominal_rows.iloc[0]["passed"]) if len(nominal_rows) else False
        f.write("\n\nNominal overlay variants packet-safe: ")
        f.write(f"`{nominal_safe}`.\n\n")
        f.write("All overlay variants, including load-ramp amplitudes, packet-safe: ")
        f.write(f"`{bool(packet_summary['packet_safe'].astype(bool).all())}`.\n\n")
        f.write("## Rich Source Objective\n\n")
        f.write("This aggregates `rho`, `j_l`, `delta_rho`, and `delta_j_l` over global, catch-support, support, packet, catch-packet, and other masks.\n\n")
        f.write(target_rich[[col for col in rich_cols if col in target_rich.columns]].to_markdown(index=False))
        f.write("\n\n")
        f.write("## Signed Objective\n\n")
        f.write(target_signed[signed_cols].to_markdown(index=False))
        f.write("\n\n")
        if len(sign_pairs):
            f.write(sign_pairs.head(10).to_markdown(index=False))
        else:
            f.write("No sign-pair comparison was available.")
        f.write("\n\n## Conservation-Style Balance\n\n")
        f.write("This is reduced ledger bookkeeping, not a continuum conservation proof.\n\n")
        f.write(target_balance[balance_cols].to_markdown(index=False))
        if not ramp_summary.empty:
            f.write("\n\n## Load-Bearing Amplitude Ramp\n\n")
            ramp_cols = [
                "amplitude",
                "status_class",
                "hard_gate_passed",
                "catch_support_incremental_fraction",
                "packet_incremental_j_fraction",
                "rich_packet_increment_abs_all_channels",
                "max_packet_norm_live",
                "packet_norm_change_fraction_of_baseline_margin",
            ]
            present = [col for col in ramp_cols if col in ramp_summary.columns]
            f.write(ramp_summary[present].to_markdown(index=False))
        f.write("\n\n## Files\n\n")
        f.write("- `validation_ladder_decision_sheet.csv`\n")
        f.write("- `validation_ladder_routing_summary.csv`\n")
        f.write("- `validation_ladder_rich_source_objective_summary.csv`\n")
        f.write("- `validation_ladder_rich_source_objective_channels.csv`\n")
        f.write("- `validation_ladder_signed_objective_summary.csv`\n")
        f.write("- `validation_ladder_signed_objective_pair_comparison.csv`\n")
        f.write("- `validation_ladder_balance_summary.csv`\n")
        f.write("- `validation_ladder_amplitude_ramp_summary.csv`\n")
        f.write("- `packet_safety_overlay/support_shell_packet_safety_summary.csv`\n")


def run_ladder(args: argparse.Namespace) -> Path:
    root = Path(args.output_root)
    root.mkdir(parents=True, exist_ok=True)

    baseline_config = Path(args.baseline_config)
    target_config_input = Path(args.target_config)
    target_config = _positive_target_config(target_config_input, root)
    target_cfg = load_config(target_config)
    v_label = _v_label(target_cfg)
    target_run = str(target_cfg["run_name"])
    baseline_run = str(load_config(baseline_config)["run_name"])
    target_amplitude = float(target_cfg.get("service", {}).get("carrying_flow", {}).get("amplitude", 0.0))
    negative_config = _negative_counterpart_config(target_config, root)
    negative_run = str(load_config(negative_config)["run_name"])
    args.overlay_amplitudes = sorted(
        {
            abs(float(a))
            for a in [
                *args.amplitudes,
                *([] if args.skip_amplitude_ramp else args.ramp_amplitudes),
                abs(target_amplitude),
            ]
        }
    )

    baseline_dir = _run_validated_config(baseline_config, root, "baseline")
    target_dir = _run_validated_config(target_config, root, "target")
    negative_dir = _run_validated_config(negative_config, root, "negative_counterpart")
    ramp_runs = _run_amplitude_ramp(args, root, target_config)
    ramp_ok_names = (
        ramp_runs[ramp_runs["run_status"].eq("ok")]["run_name"].astype(str).tolist()
        if not ramp_runs.empty
        else []
    )
    analyzed_run_names = [target_dir.name, negative_dir.name] + ramp_ok_names

    routing = _routing_summary(root, baseline_dir.name, analyzed_run_names)
    packet_summary = _packet_overlay(args, root)
    signed_summary, sign_pairs = _signed_objective(root, baseline_run)
    rich_summary, _rich_channels = _rich_source_objective_summary(root, baseline_run, analyzed_run_names)
    balance = _balance_summary(root, baseline_run, analyzed_run_names)
    ramp_summary = _amplitude_ramp_summary(
        root=root,
        ramp_runs=ramp_runs,
        routing=routing,
        rich_summary=rich_summary,
        packet_summary=packet_summary,
        args=args,
    )
    decision = _decision_sheet(
        root=root,
        target_run=target_run,
        routing=routing,
        rich_summary=rich_summary,
        packet_summary=packet_summary,
        signed_summary=signed_summary,
        sign_pairs=sign_pairs,
        balance=balance,
        target_amplitude=target_amplitude,
        args=args,
    )
    _write_ladder_report(
        root=root,
        v_label=v_label,
        baseline_run=baseline_run,
        target_run=target_run,
        negative_run=negative_run,
        target_amplitude=target_amplitude,
        decision=decision,
        routing=routing,
        rich_summary=rich_summary,
        packet_summary=packet_summary,
        signed_summary=signed_summary,
        sign_pairs=sign_pairs,
        balance=balance,
        ramp_summary=ramp_summary,
    )

    required = decision[decision["required"].astype(bool)]
    metadata = {
        "baseline_config": str(baseline_config),
        "target_config": str(target_config),
        "input_target_config": str(target_config_input),
        "negative_counterpart_config": str(negative_config),
        "v_label": v_label,
        "baseline_run": baseline_run,
        "target_run": target_run,
        "negative_run": negative_run,
        "packet_input": str(args.packet_input),
        "packet_member": args.packet_member,
        "overlay_amplitudes": args.overlay_amplitudes,
        "ramp_enabled": not args.skip_amplitude_ramp,
        "ramp_amplitudes": [] if args.skip_amplitude_ramp else args.ramp_amplitudes,
        "required_gate_passed": bool(required["passed"].astype(bool).all()),
    }
    _write_json(root / "validation_ladder_metadata.json", metadata)
    return root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the active-rail validation ladder for a support-shell target.")
    parser.add_argument("--baseline-config", default="configs/v5_service_flow_off.yaml")
    parser.add_argument("--target-config", default="configs/v5_service_support_shell_target.yaml")
    parser.add_argument("--output-root", default="runs/v5_validation_ladder")
    parser.add_argument("--packet-input", type=Path, default=DEFAULT_PACKET_INPUT)
    parser.add_argument("--packet-member", default=DEFAULT_PACKET_MEMBER)
    parser.add_argument("--support-radius", type=float, default=1.75)
    parser.add_argument("--support-multiplier", type=float, default=1.2)
    parser.add_argument("--catch-lead", type=float, default=0.75)
    parser.add_argument("--temporal-width", type=float, default=0.5)
    parser.add_argument("--smoothing-passes", type=int, default=1)
    parser.add_argument(
        "--amplitudes",
        type=float,
        nargs="+",
        default=[5e-8, 1e-7, 2.5e-7, 5e-7, 1e-6, 2.5e-6, 5e-6, 1e-5],
    )
    parser.add_argument(
        "--ramp-amplitudes",
        type=float,
        nargs="+",
        default=[1e-7, 2.5e-7, 5e-7, 1e-6, 2.5e-6, 5e-6, 1e-5, 2.5e-5, 5e-5, 1e-4, 2.5e-4, 5e-4, 1e-3, 2.5e-3, 5e-3, 7.5e-3, 1e-2],
        help="Positive support-shell amplitudes to run for the load-bearing envelope.",
    )
    parser.add_argument("--skip-amplitude-ramp", action="store_true", help="Run only the target/negative validation pair.")
    parser.add_argument("--min-catch-support-fraction", type=float, default=0.99)
    parser.add_argument("--max-packet-j-fraction", type=float, default=1e-4)
    parser.add_argument("--max-packet-abs-delta-rho", type=float, default=1e-12)
    parser.add_argument("--max-rich-packet-increment-abs", type=float, default=1e-10)
    parser.add_argument("--ramp-warning-fraction", type=float, default=0.10)
    parser.add_argument("--max-partition-closure-error", type=float, default=1e-18)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = run_ladder(args)
    metadata = json.loads((root / "validation_ladder_metadata.json").read_text(encoding="utf-8"))
    print(f"Wrote {metadata.get('v_label', 'v').upper()} validation ladder: {root}")
    print("required gates: pass" if metadata["required_gate_passed"] else "required gates: fail")
    return 0 if metadata["required_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
