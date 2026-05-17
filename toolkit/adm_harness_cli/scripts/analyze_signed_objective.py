from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


SCOPE_COLUMNS = {
    "global": "global",
    "catch": "catch",
    "support": "support_shell",
    "catch_support": "catch_support",
    "packet": "packet_live",
    "catch_packet": "catch_packet",
}


def true_mask(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index)


def prepare_baseline(path: Path) -> pd.DataFrame:
    base = pd.read_csv(path)
    required = {"s", "l", "delta_j_l", "delta_rho", "volume", "stage", "packet_live", "support_shell"}
    missing = required - set(base.columns)
    if missing:
        raise SystemExit(f"Baseline point ledger missing columns: {sorted(missing)}")

    out = base[["s", "l", "delta_j_l", "delta_rho", "volume", "stage", "packet_live", "support_shell"]].rename(
        columns={
            "delta_j_l": "base_delta_j_l",
            "delta_rho": "base_delta_rho",
            "volume": "base_volume",
            "stage": "base_stage",
            "packet_live": "base_packet_live",
            "support_shell": "base_support_shell",
        }
    )
    return out


def add_masks(df: pd.DataFrame) -> pd.DataFrame:
    df["packet_live"] = df["packet_live"].astype(bool)
    df["support_shell"] = df["support_shell"].astype(bool)
    df["catch"] = df["stage"].astype(str).eq("catch_rematch")
    df["catch_support"] = df["catch"] & df["support_shell"]
    df["catch_packet"] = df["catch"] & df["packet_live"]
    return df


def scope_mask(df: pd.DataFrame, scope: str) -> pd.Series:
    if scope == "global":
        return true_mask(df)
    return df[SCOPE_COLUMNS[scope]].astype(bool)


def sign_for_run(run_name: str) -> str:
    if "_pos_" in run_name:
        return "pos"
    if "_neg_" in run_name:
        return "neg"
    return "target" if "target" in run_name else "unpaired"


def family_key(run_name: str) -> str:
    return run_name.replace("_pos_", "_SIGN_").replace("_neg_", "_SIGN_")


def channel_metrics(
    df: pd.DataFrame,
    mask: pd.Series,
    run_col: str,
    base_col: str,
    volume: pd.Series,
) -> dict[str, float]:
    run = df.loc[mask, run_col].astype(float)
    base = df.loc[mask, base_col].astype(float)
    vol = volume.loc[mask].astype(float)
    inc = run - base

    base_abs = float((base.abs() * vol).sum())
    run_abs = float((run.abs() * vol).sum())
    inc_abs = float((inc.abs() * vol).sum())
    aligned = float((np.sign(base) * inc * vol).sum())
    opposition_fraction = -aligned / inc_abs if inc_abs else 0.0
    same_sign_fraction = aligned / inc_abs if inc_abs else 0.0

    return {
        "base_abs": base_abs,
        "run_abs": run_abs,
        "abs_change": run_abs - base_abs,
        "relief_positive_better": base_abs - run_abs,
        "increment_abs": inc_abs,
        "baseline_opposition_fraction": opposition_fraction,
        "baseline_same_sign_fraction": same_sign_fraction,
    }


def analyze_run(root: Path, baseline: pd.DataFrame, run_dir: Path) -> dict[str, float | str]:
    ledger_path = run_dir / "point_ledger.csv"
    df = pd.read_csv(ledger_path)
    required = {"s", "l", "delta_j_l", "delta_rho", "volume", "stage", "packet_live", "support_shell"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"{ledger_path} missing columns: {sorted(missing)}")

    merged = df[["s", "l", "delta_j_l", "delta_rho", "volume", "stage", "packet_live", "support_shell"]].merge(
        baseline,
        on=["s", "l"],
        how="left",
        validate="one_to_one",
    )
    if merged["base_delta_j_l"].isna().any():
        raise SystemExit(f"{ledger_path} did not align with baseline grid")
    merged = add_masks(merged)
    volume = merged["volume"].astype(float)

    row: dict[str, float | str] = {
        "run_name": run_dir.name,
        "sign": sign_for_run(run_dir.name),
        "family_key": family_key(run_dir.name),
    }

    for scope in SCOPE_COLUMNS:
        mask = scope_mask(merged, scope)
        j = channel_metrics(merged, mask, "delta_j_l", "base_delta_j_l", volume)
        for key, value in j.items():
            row[f"{scope}_j_{key}"] = value

    for scope in ["global", "catch_support", "packet", "catch_packet"]:
        mask = scope_mask(merged, scope)
        rho = channel_metrics(merged, mask, "delta_rho", "base_delta_rho", volume)
        for key, value in rho.items():
            row[f"{scope}_rho_{key}"] = value

    packet = scope_mask(merged, "packet")
    catch_support = scope_mask(merged, "catch_support")
    row["packet_j_peak_change"] = float(
        merged.loc[packet, "delta_j_l"].abs().max() - merged.loc[packet, "base_delta_j_l"].abs().max()
    )
    row["packet_rho_peak_change"] = float(
        merged.loc[packet, "delta_rho"].abs().max() - merged.loc[packet, "base_delta_rho"].abs().max()
    )
    row["catch_support_j_peak_change"] = float(
        merged.loc[catch_support, "delta_j_l"].abs().max()
        - merged.loc[catch_support, "base_delta_j_l"].abs().max()
    )

    # Lower is better. The score asks whether the run is a source-objective
    # improvement, not merely a clean incremental placement: it penalizes added
    # absolute burden, packet exposure, and packet peak growth.
    row["signed_source_objective_delta_lower_better"] = float(
        row["global_j_abs_change"]
        + 10.0 * row["packet_j_abs_change"]
        + 1.0e6 * row["packet_rho_abs_change"]
        + 0.1 * row["catch_support_j_abs_change"]
        + 1000.0 * max(0.0, row["packet_j_peak_change"])
        + 1.0e6 * max(0.0, row["packet_rho_peak_change"])
    )
    row["signed_relief_score_higher_better"] = -float(row["signed_source_objective_delta_lower_better"])
    return row


def build_pair_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fam, sub in summary.groupby("family_key"):
        if {"pos", "neg"} - set(sub["sign"]):
            continue
        pos = sub[sub["sign"].eq("pos")].iloc[0]
        neg = sub[sub["sign"].eq("neg")].iloc[0]
        gap = float(pos["signed_source_objective_delta_lower_better"] - neg["signed_source_objective_delta_lower_better"])
        denom = max(
            abs(float(pos["signed_source_objective_delta_lower_better"])),
            abs(float(neg["signed_source_objective_delta_lower_better"])),
            1.0e-30,
        )
        rows.append(
            {
                "family_key": fam,
                "pos_run": pos["run_name"],
                "neg_run": neg["run_name"],
                "winner": "pos" if gap < 0 else "neg",
                "objective_gap_pos_minus_neg": gap,
                "relative_objective_gap": abs(gap) / denom,
                "pos_objective_delta": pos["signed_source_objective_delta_lower_better"],
                "neg_objective_delta": neg["signed_source_objective_delta_lower_better"],
                "pos_catch_support_opposition_fraction": pos["catch_support_j_baseline_opposition_fraction"],
                "neg_catch_support_opposition_fraction": neg["catch_support_j_baseline_opposition_fraction"],
                "pos_global_j_abs_change": pos["global_j_abs_change"],
                "neg_global_j_abs_change": neg["global_j_abs_change"],
                "pos_catch_support_j_abs_change": pos["catch_support_j_abs_change"],
                "neg_catch_support_j_abs_change": neg["catch_support_j_abs_change"],
                "pos_packet_j_abs_change": pos["packet_j_abs_change"],
                "neg_packet_j_abs_change": neg["packet_j_abs_change"],
                "pos_packet_rho_abs_change": pos["packet_rho_abs_change"],
                "neg_packet_rho_abs_change": neg["packet_rho_abs_change"],
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("relative_objective_gap", ascending=False)


def write_report(path: Path, summary: pd.DataFrame, pairs: pd.DataFrame, baseline_run: str) -> None:
    cols = [
        "run_name",
        "sign",
        "global_j_abs_change",
        "catch_support_j_abs_change",
        "catch_support_j_baseline_opposition_fraction",
        "packet_j_abs_change",
        "packet_rho_abs_change",
        "packet_j_peak_change",
        "signed_source_objective_delta_lower_better",
    ]
    pair_cols = [
        "family_key",
        "winner",
        "objective_gap_pos_minus_neg",
        "relative_objective_gap",
        "pos_catch_support_opposition_fraction",
        "neg_catch_support_opposition_fraction",
        "pos_global_j_abs_change",
        "neg_global_j_abs_change",
    ]

    winners = pairs["winner"].value_counts().to_dict() if len(pairs) else {}
    max_gap = float(pairs["relative_objective_gap"].max()) if len(pairs) else 0.0
    meaningful = max_gap >= 1.0e-3

    with path.open("w", encoding="utf-8") as f:
        f.write("# Signed Source Objective Analysis\n\n")
        f.write(f"Baseline: `{baseline_run}`. Positive relief means a run reduced baseline absolute burden; negative relief means it added source burden.\n\n")
        f.write("This analysis differs from the routing score by using signed cancellation/alignment against the baseline source demand and absolute-burden changes, not just incremental placement fractions.\n\n")
        f.write(f"Pair winner counts: `{winners}`. Maximum relative pos/neg objective gap: `{max_gap:.6g}`.\n\n")
        if meaningful:
            f.write("Result: sign is decision-relevant under this objective.\n\n")
        else:
            f.write("Result: sign is not decision-grade under this objective at the tested amplitudes.\n\n")
        f.write("## Best Objective Rows\n\n")
        f.write(summary.sort_values("signed_source_objective_delta_lower_better")[cols].head(15).to_markdown(index=False))
        f.write("\n\n## Largest Sign Gaps\n\n")
        if len(pairs):
            f.write(pairs[pair_cols].head(15).to_markdown(index=False))
        else:
            f.write("No sign pairs found.")
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze sign choice under signed source/objective metrics.")
    parser.add_argument("--root", required=True, help="Run root containing one baseline run and paired sign runs")
    parser.add_argument("--baseline-run", default="v10_service_flow_off")
    parser.add_argument("--output-prefix", default="signed_source_objective")
    args = parser.parse_args()

    root = Path(args.root)
    baseline_path = root / args.baseline_run / "point_ledger.csv"
    if not baseline_path.exists():
        raise SystemExit(f"Missing baseline point ledger: {baseline_path}")
    baseline = prepare_baseline(baseline_path)

    rows = []
    for ledger in sorted(root.glob("*/point_ledger.csv")):
        if ledger.parent.name == args.baseline_run or "comparison" in ledger.parts:
            continue
        rows.append(analyze_run(root, baseline, ledger.parent))
    if not rows:
        raise SystemExit(f"No run ledgers found under {root}")

    summary = pd.DataFrame(rows).sort_values("signed_source_objective_delta_lower_better")
    pairs = build_pair_summary(summary)

    summary_path = root / f"{args.output_prefix}_summary.csv"
    pair_path = root / f"{args.output_prefix}_pair_comparison.csv"
    report_path = root / f"{args.output_prefix}_report.md"
    summary.to_csv(summary_path, index=False)
    pairs.to_csv(pair_path, index=False)
    write_report(report_path, summary, pairs, args.baseline_run)

    print(f"Wrote {summary_path}")
    print(f"Wrote {pair_path}")
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
