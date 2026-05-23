from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .source_ledger import CHANNELS, sha256_file, write_manifest
from .source_screening import resolve_manifest_path
from .table_io import read_table


DEMAND_CHANNELS = ("neg_Tkk_radial", "abs_p_l", "abs_j_l", "abs_pOmega")
UNASSIGNED_COMPONENT = "unassigned"


@dataclass(frozen=True)
class ComponentLedgerInput:
    label: str
    ledger_dir: Path
    manifest_path: Path
    point_ledger_path: Path
    manifest: dict[str, Any]


@dataclass(frozen=True)
class ComponentConfig:
    include_reset_current_sink: bool = True
    include_live_radial_null_trim: bool = True
    include_live_radial_pressure_trim: bool = True
    include_support_edge_radial_pressure_balance: bool = True
    include_infrastructure_angular_capacity: bool = True
    min_volume_burden: float = 0.0
    top_unassigned: int = 80


def load_component_ledger_input(ledger_dir: Path, label: str | None = None) -> ComponentLedgerInput:
    manifest_path = ledger_dir / "source_ledger_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    files = manifest.get("files", {})
    point_value = files.get("point_ledger", "source_ledger_point_ledger.csv")
    point_ledger_path = resolve_manifest_path(ledger_dir, point_value)
    return ComponentLedgerInput(
        label=label or str(manifest.get("label") or manifest.get("case") or ledger_dir.name),
        ledger_dir=ledger_dir,
        manifest_path=manifest_path,
        point_ledger_path=point_ledger_path,
        manifest=manifest,
    )


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def _demand(row: pd.Series, channel: str) -> float:
    bad_col = f"bad_{channel}"
    if bad_col in row.index:
        return max(_finite(row.get(bad_col)), 0.0)
    if channel == "neg_Tkk_radial":
        return max(-_finite(row.get("Tkk_min_radial")), 0.0)
    if channel == "abs_p_l":
        return abs(_finite(row.get("p_l_unit")))
    if channel == "abs_j_l":
        return abs(_finite(row.get("j_l_unit")))
    if channel == "abs_pOmega":
        return abs(_finite(row.get("p_omega_unit")))
    return 0.0


def _volume_burden(row: pd.Series, channel: str, demand: float) -> float:
    burden_col = f"volume_burden_{channel}"
    if burden_col in row.index:
        return max(_finite(row.get(burden_col)), 0.0)
    return demand * max(_finite(row.get("volume_weight"), 1.0), 0.0)


def _component_for(
    row: pd.Series,
    channel: str,
    *,
    include_reset_current_sink: bool,
    include_live_radial_null_trim: bool,
    include_live_radial_pressure_trim: bool,
    include_support_edge_radial_pressure_balance: bool,
    include_infrastructure_angular_capacity: bool,
) -> tuple[str, str]:
    live = _bool(row.get("inside_packet_live", False))
    stage = str(row.get("stage", ""))
    region = str(row.get("region", ""))
    if channel == "neg_Tkk_radial" and not live and region in {"core_throat", "support_edge"}:
        return "A_infrastructure_radial_null_support", "non_live_core_or_support_edge_radial_null"
    if channel == "abs_p_l" and not live and region == "core_throat":
        return "B_core_radial_pressure_balance", "non_live_core_throat_radial_pressure"
    if (
        include_support_edge_radial_pressure_balance
        and channel == "abs_p_l"
        and not live
        and region == "support_edge"
    ):
        return "I_support_edge_radial_pressure_balance", "non_live_support_edge_radial_pressure"
    if channel in {"abs_j_l", "abs_pOmega"} and live and region == "packet_in_support":
        return "C_live_handoff_angular_current", "live_packet_in_support_angular_or_current"
    if (
        include_live_radial_null_trim
        and channel == "neg_Tkk_radial"
        and live
        and region == "packet_in_support"
    ):
        return "E_live_handoff_radial_null_trim", "live_packet_in_support_radial_null_trim"
    if (
        include_live_radial_pressure_trim
        and channel == "abs_p_l"
        and live
        and region == "packet_in_support"
    ):
        return "F_live_handoff_radial_pressure_trim", "live_packet_in_support_radial_pressure_trim"
    if (
        include_infrastructure_angular_capacity
        and channel == "abs_pOmega"
        and not live
        and region in {"support_edge", "outer_quarantine_shell", "core_throat"}
    ):
        return "G_infrastructure_angular_capacity", "non_live_support_plant_angular_capacity"
    if (
        include_reset_current_sink
        and channel == "abs_j_l"
        and not live
        and stage == "reset_decompression"
        and region == "support_edge"
    ):
        return "D_reset_support_edge_current_sink", "non_live_reset_support_edge_current"
    return UNASSIGNED_COMPONENT, "outside_toy_component_roles"


def _component_description(component: str) -> str:
    return {
        "A_infrastructure_radial_null_support": "Infrastructure exotic radial-null support for non-live core/support-edge rows.",
        "B_core_radial_pressure_balance": "Core throat radial-pressure balance for non-live rows.",
        "C_live_handoff_angular_current": "Live handoff angular/current handling inside packet_in_support rows.",
        "D_reset_support_edge_current_sink": "Optional reset/support-edge current sink for non-live shift-sector rows.",
        "E_live_handoff_radial_null_trim": "Live packet-in-support radial-null trim for packet-side residual burden.",
        "F_live_handoff_radial_pressure_trim": "Live packet-in-support radial-pressure trim for packet-side residual burden.",
        "G_infrastructure_angular_capacity": "Infrastructure angular/throat-capacity support for non-live support-plant rows.",
        "I_support_edge_radial_pressure_balance": "Support-edge radial-pressure balance for non-live infrastructure rows.",
        UNASSIGNED_COMPONENT: "Demand outside the first toy component-source role set.",
    }.get(component, "")


def assign_component_sources(
    ledger: ComponentLedgerInput,
    *,
    config: ComponentConfig = ComponentConfig(),
) -> dict[str, pd.DataFrame]:
    points = read_table(ledger.point_ledger_path)
    rows: list[dict[str, Any]] = []
    for point_index, row in points.iterrows():
        for channel in DEMAND_CHANNELS:
            demand = _demand(row, channel)
            volume_burden = _volume_burden(row, channel, demand)
            if volume_burden <= config.min_volume_burden:
                continue
            component, reason = _component_for(
                row,
                channel,
                include_reset_current_sink=config.include_reset_current_sink,
                include_live_radial_null_trim=config.include_live_radial_null_trim,
                include_live_radial_pressure_trim=config.include_live_radial_pressure_trim,
                include_support_edge_radial_pressure_balance=config.include_support_edge_radial_pressure_balance,
                include_infrastructure_angular_capacity=config.include_infrastructure_angular_capacity,
            )
            inside_live = _bool(row.get("inside_packet_live", False))
            inside_geom = _bool(row.get("inside_packet_geom", False))
            rows.append({
                "label": ledger.label,
                "case": ledger.manifest.get("case", ledger.label),
                "point_index": int(point_index),
                "s": _finite(row.get("s")),
                "l": _finite(row.get("l")),
                "stage": row.get("stage", ""),
                "region": row.get("region", ""),
                "inside_packet_live": inside_live,
                "inside_packet_geom": inside_geom,
                "packet_norm": _finite(row.get("packet_norm")),
                "channel": channel,
                "channel_description": CHANNELS.get(channel, ""),
                "component": component,
                "component_description": _component_description(component),
                "assignment_reason": reason,
                "assigned": component != UNASSIGNED_COMPONENT,
                "intended_live_component": component
                in {
                    "C_live_handoff_angular_current",
                    "E_live_handoff_radial_null_trim",
                    "F_live_handoff_radial_pressure_trim",
                },
                "demand": demand,
                "volume_weight": _finite(row.get("volume_weight"), 1.0),
                "demand_volume_burden": volume_burden,
                "assigned_volume_burden": volume_burden if component != UNASSIGNED_COMPONENT else 0.0,
                "unassigned_volume_burden": volume_burden if component == UNASSIGNED_COMPONENT else 0.0,
                "rho_euler": _finite(row.get("rho_euler")),
                "p_l_unit": _finite(row.get("p_l_unit")),
                "j_l_unit": _finite(row.get("j_l_unit")),
                "p_omega_unit": _finite(row.get("p_omega_unit")),
                "Tkk_min_radial": _finite(row.get("Tkk_min_radial")),
            })
    detail = pd.DataFrame(rows)
    if detail.empty:
        return {
            "detail": detail,
            "component_summary": pd.DataFrame(),
            "channel_summary": pd.DataFrame(),
            "overlap_summary": pd.DataFrame(),
            "packet_residual_summary": pd.DataFrame(),
            "top_unassigned": pd.DataFrame(),
        }
    component_summary = _summarize_components(detail)
    channel_summary = _summarize_channels(detail)
    overlap_summary = _summarize_overlap(detail)
    packet_residual_summary = _summarize_packet_residuals(detail)
    top_unassigned = (
        detail.loc[~detail["assigned"]]
        .sort_values(["label", "unassigned_volume_burden"], ascending=[True, False])
        .groupby("label", sort=False)
        .head(int(config.top_unassigned))
        .reset_index(drop=True)
    )
    return {
        "detail": detail,
        "component_summary": component_summary,
        "channel_summary": channel_summary,
        "overlap_summary": overlap_summary,
        "packet_residual_summary": packet_residual_summary,
        "top_unassigned": top_unassigned,
    }


def _summarize_components(detail: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        detail.groupby(["label", "component", "channel", "inside_packet_live"], dropna=False)
        .agg(
            rows=("component", "count"),
            total_demand_burden=("demand_volume_burden", "sum"),
            assigned_burden=("assigned_volume_burden", "sum"),
            unassigned_burden=("unassigned_volume_burden", "sum"),
            mean_demand=("demand", "mean"),
            max_demand=("demand", "max"),
        )
        .reset_index()
    )
    totals = grouped.groupby(["label", "component", "channel"])["total_demand_burden"].transform("sum")
    grouped["live_component_fraction"] = np.where(
        totals > 0.0,
        np.where(grouped["inside_packet_live"], grouped["total_demand_burden"], 0.0) / totals,
        np.nan,
    )
    return grouped.sort_values(["label", "component", "channel", "inside_packet_live"])


def _summarize_channels(detail: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        detail.groupby(["label", "channel"], dropna=False)
        .agg(
            rows=("channel", "count"),
            total_demand_burden=("demand_volume_burden", "sum"),
            assigned_burden=("assigned_volume_burden", "sum"),
            unassigned_burden=("unassigned_volume_burden", "sum"),
            assigned_rows=("assigned", "sum"),
        )
        .reset_index()
    )
    grouped["coverage_fraction"] = np.where(
        grouped["total_demand_burden"] > 0.0,
        grouped["assigned_burden"] / grouped["total_demand_burden"],
        np.nan,
    )
    grouped["residual_fraction"] = np.where(
        grouped["total_demand_burden"] > 0.0,
        grouped["unassigned_burden"] / grouped["total_demand_burden"],
        np.nan,
    )
    return grouped.sort_values(["label", "channel"])


def _summarize_overlap(detail: pd.DataFrame) -> pd.DataFrame:
    assigned = detail.loc[detail["assigned"]].copy()
    if assigned.empty:
        return pd.DataFrame()
    point_component = (
        assigned.groupby(["label", "point_index"], dropna=False)
        .agg(
            components=("component", "nunique"),
            channels=("channel", "nunique"),
            total_assigned_burden=("assigned_volume_burden", "sum"),
            inside_packet_live=("inside_packet_live", "max"),
        )
        .reset_index()
    )
    rows: list[dict[str, Any]] = []
    for label, group in point_component.groupby("label", sort=False):
        total = float(group["total_assigned_burden"].sum())
        overlap = group.loc[group["components"] > 1]
        live_overlap = overlap.loc[overlap["inside_packet_live"].astype(bool)]
        hard_components = assigned.loc[
            (assigned["label"] == label)
            & assigned["component"].isin(
                [
                    "A_infrastructure_radial_null_support",
                    "B_core_radial_pressure_balance",
                    "I_support_edge_radial_pressure_balance",
                    "D_reset_support_edge_current_sink",
                ]
            )
        ]
        hard_total = float(hard_components["assigned_volume_burden"].sum())
        hard_live = float(
            hard_components.loc[hard_components["inside_packet_live"], "assigned_volume_burden"].sum()
        )
        rows.append({
            "label": label,
            "assigned_points": int(len(group)),
            "multi_component_points": int(len(overlap)),
            "total_assigned_burden": total,
            "multi_component_burden": float(overlap["total_assigned_burden"].sum()),
            "multi_component_fraction": float(overlap["total_assigned_burden"].sum()) / total if total > 0.0 else np.nan,
            "live_multi_component_burden": float(live_overlap["total_assigned_burden"].sum()),
            "hard_component_live_contamination_burden": hard_live,
            "hard_component_live_contamination_fraction": hard_live / hard_total if hard_total > 0.0 else np.nan,
        })
    return pd.DataFrame(rows)


def _summarize_packet_residuals(detail: pd.DataFrame) -> pd.DataFrame:
    packet = detail.loc[detail["inside_packet_live"].astype(bool)].copy()
    if packet.empty:
        return pd.DataFrame()
    grouped = (
        packet.groupby(["label", "channel"], dropna=False)
        .agg(
            live_rows=("channel", "count"),
            live_total_burden=("demand_volume_burden", "sum"),
            live_assigned_burden=("assigned_volume_burden", "sum"),
            live_unassigned_burden=("unassigned_volume_burden", "sum"),
            max_live_demand=("demand", "max"),
        )
        .reset_index()
    )
    grouped["live_coverage_fraction"] = np.where(
        grouped["live_total_burden"] > 0.0,
        grouped["live_assigned_burden"] / grouped["live_total_burden"],
        np.nan,
    )
    grouped["live_residual_fraction"] = np.where(
        grouped["live_total_burden"] > 0.0,
        grouped["live_unassigned_burden"] / grouped["live_total_burden"],
        np.nan,
    )
    return grouped.sort_values(["label", "channel"])


def combine_component_outputs(outputs: Iterable[dict[str, pd.DataFrame]]) -> dict[str, pd.DataFrame]:
    items = list(outputs)
    combined: dict[str, pd.DataFrame] = {}
    for key in [
        "detail",
        "component_summary",
        "channel_summary",
        "overlap_summary",
        "packet_residual_summary",
        "top_unassigned",
    ]:
        frames = [item[key] for item in items if key in item and not item[key].empty]
        combined[key] = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return combined


def write_component_outputs(
    outdir: Path,
    ledgers: list[ComponentLedgerInput],
    outputs: dict[str, pd.DataFrame],
    *,
    config: ComponentConfig = ComponentConfig(),
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "detail": outdir / "component_source_assignment_detail.csv",
        "component_summary": outdir / "component_source_component_summary.csv",
        "channel_summary": outdir / "component_source_channel_summary.csv",
        "overlap_summary": outdir / "component_source_overlap_summary.csv",
        "packet_residual_summary": outdir / "component_source_packet_residual_summary.csv",
        "top_unassigned": outdir / "component_source_top_unassigned.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "component_source_manifest.json"
    manifest = {
        "caveat": (
            "Toy component-source assignment ledger. Component supplies are oracle "
            "partitions of demanded-source burden by channel, region, stage, and live-packet "
            "status; this is not a physical matter-model solve."
        ),
        "config": {
            "channels": list(DEMAND_CHANNELS),
            "include_reset_current_sink": bool(config.include_reset_current_sink),
            "include_live_radial_null_trim": bool(config.include_live_radial_null_trim),
            "include_live_radial_pressure_trim": bool(config.include_live_radial_pressure_trim),
            "include_support_edge_radial_pressure_balance": bool(config.include_support_edge_radial_pressure_balance),
            "include_infrastructure_angular_capacity": bool(config.include_infrastructure_angular_capacity),
            "min_volume_burden": float(config.min_volume_burden),
            "top_unassigned": int(config.top_unassigned),
        },
        "ledgers": [
            {
                "label": ledger.label,
                "ledger_dir": str(ledger.ledger_dir),
                "manifest": str(ledger.manifest_path),
                "point_ledger": str(ledger.point_ledger_path),
                "point_ledger_sha256": sha256_file(ledger.point_ledger_path),
                "case": ledger.manifest.get("case"),
            }
            for ledger in ledgers
        ],
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
