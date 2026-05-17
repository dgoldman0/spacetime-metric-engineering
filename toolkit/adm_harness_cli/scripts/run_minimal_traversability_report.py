from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
import sys

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import CHANNELS  # noqa: E402


SUPPORT_PLANT_REGIONS = {"core_throat", "support_edge", "outer_quarantine_shell"}
MAIN_SUPPORT_REGIONS = {"core_throat", "support_edge"}
HARD_CHANNELS = {"neg_Tkk_radial", "neg_rho_euler", "neg_rho_packet"}


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _sum_col(points: pd.DataFrame, col: str, mask: pd.Series | np.ndarray | None = None) -> float:
    if col not in points.columns:
        return 0.0
    values = points[col].astype(float)
    if mask is not None:
        values = values.loc[mask]
    return float(np.nansum(values.to_numpy()))


def _git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PACKAGE_ROOT.parent.parent,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def _load_ledger(path: Path, label: str, shell_threshold: float) -> pd.DataFrame:
    points = pd.read_csv(path)
    required = {
        "s",
        "l",
        "stage",
        "region",
        "inside_packet_live",
        "inside_packet_geom",
        "packet_norm",
        "support_shell_window",
    }
    missing = sorted(required - set(points.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    for channel in CHANNELS:
        missing_channel = [
            col
            for col in [f"bad_{channel}", f"volume_burden_{channel}"]
            if col not in points.columns
        ]
        if missing_channel:
            raise ValueError(f"{path} is missing required channel columns: {missing_channel}")

    points = points.copy()
    points["report_label"] = label
    points["inside_packet_live_bool"] = _bool_series(points["inside_packet_live"])
    points["inside_packet_geom_bool"] = _bool_series(points["inside_packet_geom"])
    points["active_shell_bool"] = points["support_shell_window"].astype(float).abs() > shell_threshold
    points["main_support_bool"] = points["region"].astype(str).isin(MAIN_SUPPORT_REGIONS)
    points["support_plant_bool"] = points["region"].astype(str).isin(SUPPORT_PLANT_REGIONS)
    points["catch_support_edge_bool"] = (
        (points["stage"].astype(str) == "catch_rematch")
        & (points["region"].astype(str) == "support_edge")
    )
    points["nonpacket_infrastructure_bool"] = (
        ~points["inside_packet_live_bool"] & points["support_plant_bool"]
    )
    return points


def _packet_summary(points: pd.DataFrame, label: str) -> dict[str, Any]:
    live = points["inside_packet_live_bool"]
    geom = points["inside_packet_geom_bool"]
    active = points["active_shell_bool"]
    packet_norm_live = points.loc[live, "packet_norm"].astype(float)
    return {
        "label": label,
        "rows": int(len(points)),
        "live_packet_points": int(live.sum()),
        "geometric_packet_points": int(geom.sum()),
        "max_packet_norm_live": float(packet_norm_live.max()) if len(packet_norm_live) else math.nan,
        "min_packet_norm_live": float(packet_norm_live.min()) if len(packet_norm_live) else math.nan,
        "positive_packet_norm_live": int((packet_norm_live > 0.0).sum()) if len(packet_norm_live) else 0,
        "live_packet_core_throat_overlap_points": int((live & (points["region"].astype(str) == "core_throat")).sum()),
        "live_packet_support_edge_overlap_points": int((live & (points["region"].astype(str) == "support_edge")).sum()),
        "live_packet_outer_quarantine_overlap_points": int((live & (points["region"].astype(str) == "outer_quarantine_shell")).sum()),
        "live_packet_packet_in_support_points": int((live & (points["region"].astype(str) == "packet_in_support")).sum()),
        "live_packet_active_shell_points": int((live & active).sum()),
        "geometric_packet_active_shell_points": int((geom & active).sum()),
        "active_shell_points": int(active.sum()),
    }


def _channel_summary(points: pd.DataFrame, label: str, top_n: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    live = points["inside_packet_live_bool"]
    geom = points["inside_packet_geom_bool"]
    main_support = points["main_support_bool"]
    support_plant = points["support_plant_bool"]
    active_shell = points["active_shell_bool"]
    catch_support_edge = points["catch_support_edge_bool"]
    nonpacket_infra = points["nonpacket_infrastructure_bool"]

    summary_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []

    for channel, description in CHANNELS.items():
        burden_col = f"volume_burden_{channel}"
        bad_col = f"bad_{channel}"
        total = _sum_col(points, burden_col)
        live_burden = _sum_col(points, burden_col, live)
        geom_burden = _sum_col(points, burden_col, geom)
        main_support_burden = _sum_col(points, burden_col, main_support)
        support_plant_burden = _sum_col(points, burden_col, support_plant)
        active_shell_burden = _sum_col(points, burden_col, active_shell)
        catch_support_edge_burden = _sum_col(points, burden_col, catch_support_edge)
        nonpacket_infra_burden = _sum_col(points, burden_col, nonpacket_infra)
        outside_live_burden = max(total - live_burden, 0.0)

        ranked = points.sort_values(burden_col, ascending=False).head(top_n).copy()
        top_live_count = int(ranked["inside_packet_live_bool"].sum())
        top_geom_count = int(ranked["inside_packet_geom_bool"].sum())
        top = ranked.iloc[0] if len(ranked) else None

        summary_rows.append({
            "label": label,
            "channel": channel,
            "description": description,
            "total_burden": total,
            "live_packet_burden": live_burden,
            "live_packet_fraction": live_burden / total if total > 0.0 else math.nan,
            "geometric_packet_burden": geom_burden,
            "geometric_packet_fraction": geom_burden / total if total > 0.0 else math.nan,
            "outside_live_packet_burden": outside_live_burden,
            "outside_live_packet_fraction": outside_live_burden / total if total > 0.0 else math.nan,
            "main_support_burden": main_support_burden,
            "main_support_fraction": main_support_burden / total if total > 0.0 else math.nan,
            "support_plant_burden": support_plant_burden,
            "support_plant_fraction": support_plant_burden / total if total > 0.0 else math.nan,
            "active_shell_burden": active_shell_burden,
            "active_shell_fraction": active_shell_burden / total if total > 0.0 else math.nan,
            "catch_support_edge_burden": catch_support_edge_burden,
            "catch_support_edge_fraction": catch_support_edge_burden / total if total > 0.0 else math.nan,
            "nonpacket_infrastructure_burden": nonpacket_infra_burden,
            "nonpacket_infrastructure_fraction": nonpacket_infra_burden / total if total > 0.0 else math.nan,
            "top_bad_point_s": float(top["s"]) if top is not None else math.nan,
            "top_bad_point_l": float(top["l"]) if top is not None else math.nan,
            "top_bad_point_stage": str(top["stage"]) if top is not None else "",
            "top_bad_point_region": str(top["region"]) if top is not None else "",
            "top_bad_point_badness": float(top[bad_col]) if top is not None else math.nan,
            "top_bad_point_volume_burden": float(top[burden_col]) if top is not None else math.nan,
            "top_bad_point_in_live_packet": bool(top["inside_packet_live_bool"]) if top is not None else False,
            "top_bad_point_in_geometric_packet": bool(top["inside_packet_geom_bool"]) if top is not None else False,
            "top_n_bad_points": int(len(ranked)),
            "top_n_bad_points_in_live_packet": top_live_count,
            "top_n_bad_points_in_geometric_packet": top_geom_count,
        })

        for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
            top_rows.append({
                "label": label,
                "channel": channel,
                "rank": rank,
                "s": float(row["s"]),
                "l": float(row["l"]),
                "stage": str(row["stage"]),
                "region": str(row["region"]),
                "inside_packet_live": bool(row["inside_packet_live_bool"]),
                "inside_packet_geom": bool(row["inside_packet_geom_bool"]),
                "support_shell_window": float(row["support_shell_window"]),
                "packet_norm": float(row["packet_norm"]),
                "badness": float(row[bad_col]),
                "volume_burden": float(row[burden_col]),
            })
    return summary_rows, top_rows


def _overlap_summary(points: pd.DataFrame, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    live = points[points["inside_packet_live_bool"]].copy()
    for scope, column in [("live_packet_by_region", "region"), ("live_packet_by_stage", "stage")]:
        for value, group in live.groupby(column, dropna=False):
            rows.append({
                "label": label,
                "scope": scope,
                "name": str(value),
                "points": int(len(group)),
                "fraction_of_live_packet": float(len(group) / len(live)) if len(live) else math.nan,
            })
    active_live = live[live["active_shell_bool"]]
    rows.append({
        "label": label,
        "scope": "live_packet_active_shell",
        "name": "support_shell_window_abs_gt_threshold",
        "points": int(len(active_live)),
        "fraction_of_live_packet": float(len(active_live) / len(live)) if len(live) else math.nan,
    })
    return rows


def _decision_rows(packet_df: pd.DataFrame, channel_df: pd.DataFrame, top_n: int, warning_fraction: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, packet in packet_df.iterrows():
        label = str(packet["label"])
        channels = channel_df[channel_df["label"] == label].copy()
        finite_live = channels["live_packet_fraction"].replace([np.inf, -np.inf], np.nan).dropna()
        max_live_fraction = float(finite_live.max()) if len(finite_live) else math.nan
        max_top_live = int(channels["top_n_bad_points_in_live_packet"].max()) if len(channels) else 0
        hard_top_live = int(
            channels[
                channels["channel"].isin(HARD_CHANNELS)
                & channels["top_bad_point_in_live_packet"].astype(bool)
            ].shape[0]
        )
        support_dominates = bool(
            (
                channels["nonpacket_infrastructure_burden"].astype(float)
                >= channels["live_packet_burden"].astype(float)
            ).all()
        ) if len(channels) else False

        reasons: list[str] = []
        status = "pass"
        if int(packet["positive_packet_norm_live"]) > 0:
            status = "fail"
            reasons.append("positive live packet norm")
        if hard_top_live > 0:
            status = "fail"
            reasons.append("top hard-channel point lies in live packet")
        if math.isfinite(max_live_fraction) and max_live_fraction >= 1.0e-2:
            status = "fail"
            reasons.append("live packet carries percent-level burden")

        if status != "fail":
            if math.isfinite(max_live_fraction) and max_live_fraction > warning_fraction:
                status = "warning"
                reasons.append("live packet fraction above warning threshold")
            if max_top_live > 0:
                status = "warning"
                reasons.append(f"top-{top_n} bad points touch live packet")
            if int(packet["live_packet_active_shell_points"]) > 0:
                status = "warning"
                reasons.append("active shell touches live packet")
            if not support_dominates:
                status = "warning"
                reasons.append("nonpacket infrastructure does not dominate every channel")

        if not reasons:
            reasons.append("packet safe and top burdens remain outside live packet")

        rows.append({
            "label": label,
            "packet_norm_safe": int(packet["positive_packet_norm_live"]) == 0,
            "live_packet_core_throat_overlap_points": int(packet["live_packet_core_throat_overlap_points"]),
            "live_packet_support_edge_overlap_points": int(packet["live_packet_support_edge_overlap_points"]),
            "live_packet_active_shell_points": int(packet["live_packet_active_shell_points"]),
            "max_live_packet_fraction_any_channel": max_live_fraction,
            "max_top_bad_points_in_live_packet": max_top_live,
            "hard_channel_top_bad_points_in_live_packet": hard_top_live,
            "support_burden_dominates_packet_burden": support_dominates,
            "minimal_traversability_status": status,
            "status_reason": "; ".join(reasons),
        })
    return pd.DataFrame(rows)


def _fmt(value: Any, digits: int = 6) -> str:
    number = _finite(value, math.nan)
    if not math.isfinite(number):
        return "n/a"
    if abs(number) >= 1000 or (0 < abs(number) < 1.0e-4):
        return f"{number:.3e}"
    return f"{number:.{digits}f}"


def _markdown_report(
    outdir: Path,
    ledgers: list[tuple[Path, str]],
    packet_df: pd.DataFrame,
    channel_df: pd.DataFrame,
    decision_df: pd.DataFrame,
    shell_threshold: float,
    top_n: int,
) -> str:
    lines: list[str] = []
    lines.append("# Minimal-Traversability Packet-Worldtube Report")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This packet-worldtube report asks whether the active-rail packet behaves like a protected service "
        "worldtube coupled to a support plant, or whether it inherits the main support-source burden of an "
        "ordinary passenger-traversed throat."
    )
    lines.append("")
    lines.append("The report is demanded-source accounting only. It uses the point ledger columns already emitted by the ADM/source-ledger harness and does not construct a matter-source model.")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- active shell threshold: `abs(support_shell_window) > {shell_threshold:g}`")
    lines.append(f"- top bad points per channel: `{top_n}`")
    commit = _git_commit()
    if commit:
        lines.append(f"- repository commit: `{commit}`")
    for path, label in ledgers:
        lines.append(f"- `{label}`: `{path}`")
    lines.append("")
    lines.append("## Decision Sheet")
    lines.append("")
    decision_cols = [
        "label",
        "packet_norm_safe",
        "live_packet_core_throat_overlap_points",
        "live_packet_support_edge_overlap_points",
        "live_packet_active_shell_points",
        "max_live_packet_fraction_any_channel",
        "max_top_bad_points_in_live_packet",
        "support_burden_dominates_packet_burden",
        "minimal_traversability_status",
    ]
    display_decision = decision_df[decision_cols].copy()
    display_decision["max_live_packet_fraction_any_channel"] = display_decision["max_live_packet_fraction_any_channel"].map(_fmt)
    lines.append(display_decision.to_markdown(index=False))
    lines.append("")
    lines.append("## Packet Worldtube")
    lines.append("")
    packet_cols = [
        "label",
        "live_packet_points",
        "max_packet_norm_live",
        "min_packet_norm_live",
        "positive_packet_norm_live",
        "live_packet_packet_in_support_points",
        "live_packet_active_shell_points",
    ]
    display_packet = packet_df[packet_cols].copy()
    for col in ["max_packet_norm_live", "min_packet_norm_live"]:
        display_packet[col] = display_packet[col].map(_fmt)
    lines.append(display_packet.to_markdown(index=False))
    lines.append("")
    lines.append("## Source-Burden Placement")
    lines.append("")
    lines.append(
        "The key distinction is live packet burden versus nonpacket infrastructure/support burden. "
        "Fractions are relative to each channel's total volume-weighted badness."
    )
    lines.append("")
    selected_cols = [
        "label",
        "channel",
        "total_burden",
        "live_packet_fraction",
        "main_support_fraction",
        "nonpacket_infrastructure_fraction",
        "top_bad_point_stage",
        "top_bad_point_region",
        "top_bad_point_in_live_packet",
    ]
    display_channels = channel_df[selected_cols].copy()
    for col in ["total_burden", "live_packet_fraction", "main_support_fraction", "nonpacket_infrastructure_fraction"]:
        display_channels[col] = display_channels[col].map(_fmt)
    lines.append(display_channels.to_markdown(index=False))
    lines.append("")
    lines.append("## Status Rationale")
    lines.append("")
    for _, row in decision_df.iterrows():
        lines.append(
            f"- `{row['label']}`: **{row['minimal_traversability_status']}** - {row['status_reason']}."
        )
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append(
        "A pass here would mean the demanded source is placed away from the live packet worldtube in this ledger. "
        "It would not prove that a physical matter family can realize the support plant. A warning or fail should "
        "be read as an architecture/source-placement issue to inspect before moving to Stage II."
    )
    lines.append("")
    lines.append("## Output Files")
    lines.append("")
    for name in [
        "minimal_traversability_summary.csv",
        "minimal_traversability_packet_summary.csv",
        "minimal_traversability_channel_summary.csv",
        "minimal_traversability_top_bad_points.csv",
        "minimal_traversability_overlap_summary.csv",
    ]:
        lines.append(f"- `{outdir / name}`")
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a packet-worldtube minimal-traversability report from source-ledger point ledgers.")
    parser.add_argument("--point-ledger", type=Path, action="append", required=True, help="Point ledger CSV. Repeat for multiple cases.")
    parser.add_argument("--label", action="append", required=True, help="Label for each --point-ledger, in the same order.")
    parser.add_argument("--compare-point-ledger", type=Path, action="append", default=[], help="Optional comparator point ledger CSV.")
    parser.add_argument("--compare-label", action="append", default=[], help="Label for each --compare-point-ledger.")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--shell-threshold", type=float, default=1.0e-3)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--warning-live-fraction", type=float, default=1.0e-3)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if len(args.point_ledger) != len(args.label):
        raise SystemExit("--point-ledger and --label counts must match")
    if len(args.compare_point_ledger) != len(args.compare_label):
        raise SystemExit("--compare-point-ledger and --compare-label counts must match")
    if args.top_n < 1:
        raise SystemExit("--top-n must be at least 1")

    ledgers = list(zip(args.point_ledger, args.label))
    ledgers.extend(zip(args.compare_point_ledger, args.compare_label))
    args.outdir.mkdir(parents=True, exist_ok=True)

    packet_rows: list[dict[str, Any]] = []
    channel_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []
    overlap_rows: list[dict[str, Any]] = []

    for path, label in ledgers:
        points = _load_ledger(path, label, args.shell_threshold)
        packet_rows.append(_packet_summary(points, label))
        channels, top = _channel_summary(points, label, args.top_n)
        channel_rows.extend(channels)
        top_rows.extend(top)
        overlap_rows.extend(_overlap_summary(points, label))

    packet_df = pd.DataFrame(packet_rows)
    channel_df = pd.DataFrame(channel_rows)
    top_df = pd.DataFrame(top_rows)
    overlap_df = pd.DataFrame(overlap_rows)
    decision_df = _decision_rows(packet_df, channel_df, args.top_n, args.warning_live_fraction)

    decision_path = args.outdir / "minimal_traversability_summary.csv"
    packet_path = args.outdir / "minimal_traversability_packet_summary.csv"
    channel_path = args.outdir / "minimal_traversability_channel_summary.csv"
    top_path = args.outdir / "minimal_traversability_top_bad_points.csv"
    overlap_path = args.outdir / "minimal_traversability_overlap_summary.csv"
    report_path = args.outdir / "minimal_traversability_report.md"
    metadata_path = args.outdir / "minimal_traversability_metadata.json"

    decision_df.to_csv(decision_path, index=False)
    packet_df.to_csv(packet_path, index=False)
    channel_df.to_csv(channel_path, index=False)
    top_df.to_csv(top_path, index=False)
    overlap_df.to_csv(overlap_path, index=False)
    report_path.write_text(
        _markdown_report(args.outdir, ledgers, packet_df, channel_df, decision_df, args.shell_threshold, args.top_n),
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps(
            {
                "point_ledgers": [{"path": str(path), "label": label} for path, label in ledgers],
                "shell_threshold": args.shell_threshold,
                "top_n": args.top_n,
                "warning_live_fraction": args.warning_live_fraction,
                "commit": _git_commit(),
                "files": {
                    "summary": str(decision_path),
                    "packet_summary": str(packet_path),
                    "channel_summary": str(channel_path),
                    "top_bad_points": str(top_path),
                    "overlap_summary": str(overlap_path),
                    "report": str(report_path),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "outdir": str(args.outdir), "cases": len(ledgers)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
