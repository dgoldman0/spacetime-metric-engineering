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
    return baseline[["s", "l", "delta_j_l", "delta_rho"]].rename(
        columns={"delta_j_l": "baseline_delta_j_l", "delta_rho": "baseline_delta_rho"}
    )


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
    overlay_args = SimpleNamespace(
        input=str(args.packet_input),
        member=args.packet_member,
        output_dir=str(root / "packet_safety_overlay"),
        support_radius=args.support_radius,
        support_multiplier=args.support_multiplier,
        catch_lead=args.catch_lead,
        temporal_width=args.temporal_width,
        smoothing_passes=args.smoothing_passes,
        amplitudes=args.amplitudes,
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


def _decision_sheet(
    *,
    root: Path,
    target_run: str,
    routing: pd.DataFrame,
    packet_summary: pd.DataFrame,
    signed_summary: pd.DataFrame,
    sign_pairs: pd.DataFrame,
    balance: pd.DataFrame,
    target_amplitude: float,
    args: argparse.Namespace,
) -> pd.DataFrame:
    target_routing = routing[routing["run_name"].eq(target_run)].iloc[0]
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
            "check": "all_tested_overlay_variants_safe",
            "value": float(packet_summary["packet_safe"].astype(bool).all()),
            "threshold": "true",
            "required": True,
            "passed": bool(packet_summary["packet_safe"].astype(bool).all()),
            "note": "the default sign/amplitude ladder should remain packet-safe",
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
    baseline_run: str,
    target_run: str,
    negative_run: str,
    target_amplitude: float,
    decision: pd.DataFrame,
    routing: pd.DataFrame,
    packet_summary: pd.DataFrame,
    signed_summary: pd.DataFrame,
    sign_pairs: pd.DataFrame,
    balance: pd.DataFrame,
) -> None:
    required = decision[decision["required"].astype(bool)]
    passed = bool(required["passed"].astype(bool).all())
    target_routing = routing[routing["run_name"].eq(target_run)]
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
        f.write("# V5 Validation Ladder\n\n")
        f.write(f"Baseline run: `{baseline_run}`. Target run: `{target_run}`. Negative counterpart: `{negative_run}`.\n\n")
        f.write(f"Required-gate result: `{'PASS' if passed else 'FAIL'}`.\n\n")
        f.write("## Decision Sheet\n\n")
        f.write(decision.to_markdown(index=False))
        f.write("\n\n## Routing Gate\n\n")
        f.write(target_routing[routing_cols].to_markdown(index=False))
        f.write("\n\n## Packet-Safety Overlay\n\n")
        f.write(target_packet[packet_cols].to_markdown(index=False))
        f.write("\n\nAll tested overlay variants packet-safe: ")
        f.write(f"`{bool(packet_summary['packet_safe'].astype(bool).all())}`.\n\n")
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
        f.write("\n\n## Files\n\n")
        f.write("- `validation_ladder_decision_sheet.csv`\n")
        f.write("- `validation_ladder_routing_summary.csv`\n")
        f.write("- `validation_ladder_signed_objective_summary.csv`\n")
        f.write("- `validation_ladder_signed_objective_pair_comparison.csv`\n")
        f.write("- `validation_ladder_balance_summary.csv`\n")
        f.write("- `packet_safety_overlay/support_shell_packet_safety_summary.csv`\n")


def run_ladder(args: argparse.Namespace) -> Path:
    root = Path(args.output_root)
    root.mkdir(parents=True, exist_ok=True)

    baseline_config = Path(args.baseline_config)
    target_config = Path(args.target_config)
    target_cfg = load_config(target_config)
    target_run = str(target_cfg["run_name"])
    baseline_run = str(load_config(baseline_config)["run_name"])
    target_amplitude = float(target_cfg.get("service", {}).get("carrying_flow", {}).get("amplitude", 0.0))
    negative_config = _negative_counterpart_config(target_config, root)
    negative_run = str(load_config(negative_config)["run_name"])

    baseline_dir = _run_validated_config(baseline_config, root, "baseline")
    target_dir = _run_validated_config(target_config, root, "target")
    negative_dir = _run_validated_config(negative_config, root, "negative_counterpart")

    routing = _routing_summary(root, baseline_dir.name, [target_dir.name, negative_dir.name])
    packet_summary = _packet_overlay(args, root)
    signed_summary, sign_pairs = _signed_objective(root, baseline_run)
    balance = _balance_summary(root, baseline_run, [target_run, negative_run])
    decision = _decision_sheet(
        root=root,
        target_run=target_run,
        routing=routing,
        packet_summary=packet_summary,
        signed_summary=signed_summary,
        sign_pairs=sign_pairs,
        balance=balance,
        target_amplitude=target_amplitude,
        args=args,
    )
    _write_ladder_report(
        root=root,
        baseline_run=baseline_run,
        target_run=target_run,
        negative_run=negative_run,
        target_amplitude=target_amplitude,
        decision=decision,
        routing=routing,
        packet_summary=packet_summary,
        signed_summary=signed_summary,
        sign_pairs=sign_pairs,
        balance=balance,
    )

    required = decision[decision["required"].astype(bool)]
    metadata = {
        "baseline_config": str(baseline_config),
        "target_config": str(target_config),
        "negative_counterpart_config": str(negative_config),
        "baseline_run": baseline_run,
        "target_run": target_run,
        "negative_run": negative_run,
        "packet_input": str(args.packet_input),
        "packet_member": args.packet_member,
        "required_gate_passed": bool(required["passed"].astype(bool).all()),
    }
    _write_json(root / "validation_ladder_metadata.json", metadata)
    return root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the V5 active-rail validation ladder for the support-shell target.")
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
    parser.add_argument("--min-catch-support-fraction", type=float, default=0.99)
    parser.add_argument("--max-packet-j-fraction", type=float, default=1e-4)
    parser.add_argument("--max-packet-abs-delta-rho", type=float, default=1e-12)
    parser.add_argument("--max-partition-closure-error", type=float, default=1e-18)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = run_ladder(args)
    metadata = json.loads((root / "validation_ladder_metadata.json").read_text(encoding="utf-8"))
    print(f"Wrote V5 validation ladder: {root}")
    print("required gates: pass" if metadata["required_gate_passed"] else "required gates: fail")
    return 0 if metadata["required_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
