from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import SourceCase, SourceParams  # noqa: E402
from adm_harness.source_screening import (  # noqa: E402
    load_source_screen_context,
    load_spec_list,
    run_source_screen,
    select_specs,
    service_factor_label,
    source_channel_metrics,
)


BASE_SPECS: list[dict[str, Any]] = [
    {"label": "current", "mode": "current"},
    {
        "label": "split_ref",
        "mode": "split_piecewise",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "null_gain": -0.05,
    },
    {
        "label": "coupled_carve_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.0,
        "radial_gain": 0.0,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "coupled_edge_rad005_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.12,
        "radial_gain": 0.0,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "coupled_edgecarve018_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.18,
        "radial_gain": 0.0,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "coupled_edgecarve024_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.24,
        "radial_gain": 0.0,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "pressure_edge018_rebate025_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.18,
        "rebate_fraction": 0.25,
        "radial_gain": 0.0,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "pressure_edge024_rebate025_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.24,
        "rebate_fraction": 0.25,
        "radial_gain": 0.0,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "pressure_edge024_rebate050_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.24,
        "rebate_fraction": 0.50,
        "radial_gain": 0.0,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "pressure_edge018_rebate050_rad005_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.18,
        "rebate_fraction": 0.50,
        "radial_gain": 0.05,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "coupled_edgecarve012_rad005_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.12,
        "radial_gain": 0.05,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "coupled_edge_rad010_keep_radial",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.12,
        "radial_gain": 0.10,
        "null_gain": -0.05,
        "replace_radial": False,
    },
    {
        "label": "coupled_edge_rad010_replace",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.12,
        "radial_gain": 0.10,
        "null_gain": -0.05,
        "replace_radial": True,
    },
    {
        "label": "coupled_edge_rad015_replace",
        "mode": "coupled",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.18,
        "radial_gain": 0.15,
        "null_gain": -0.05,
        "replace_radial": True,
    },
]


def _values(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": str(spec.get("mode", "coupled")),
        "entry_carve": float(spec.get("entry_carve", 0.75)),
        "catch_carve": float(spec.get("catch_carve", 0.15)),
        "edge_carve": float(spec.get("edge_carve", 0.0)),
        "radius_multiplier": float(spec.get("radius_multiplier", 1.0)),
        "width_multiplier": float(spec.get("width_multiplier", 1.6)),
        "entry_schedule": str(spec.get("entry_schedule", "live_only")),
        "catch_schedule": str(spec.get("catch_schedule", "catch_only")),
        "temporal_profile": str(spec.get("temporal_profile", "minimum_jerk")),
        "edge_inner_radius_multiplier": float(spec.get("edge_inner_radius_multiplier", 1.0)),
        "edge_outer_radius_multiplier": float(spec.get("edge_outer_radius_multiplier", 1.7)),
        "edge_width_multiplier": float(spec.get("edge_width_multiplier", 2.2)),
        "rebate_fraction": float(spec.get("rebate_fraction", 0.0)),
        "radial_gain": float(spec.get("radial_gain", 0.0)),
        "null_gain": float(spec.get("null_gain", 0.0)),
        "replace_carve": bool(spec.get("replace_carve", True)),
        "replace_radial": bool(spec.get("replace_radial", False)),
        "replace_null": bool(spec.get("replace_null", True)),
    }


def _zero_carve(params: dict[str, Any]) -> None:
    params.update(
        standing_support_packet_exclusion=0.0,
        standing_support_packet_exclusion_catch=0.0,
        standing_support_packet_exclusion_shoulder=0.0,
    )


def _zero_radial(params: dict[str, Any]) -> None:
    params.update(
        standing_support_packet_radial_log_gain=0.0,
        standing_support_packet_radial_shoulder_log_gain=0.0,
        standing_support_packet_radial_skirt_log_gain=0.0,
    )


def _zero_null(params: dict[str, Any]) -> None:
    params.update(standing_support_packet_null_cushion_log_gain=0.0)


def _case_for_spec(label: str, spec: dict[str, Any], params: SourceParams) -> SourceCase:
    values = _values(spec)
    updates: dict[str, Any] = {}
    if values["mode"] == "current":
        return SourceCase(f"{service_factor_label(params)}_coupled_profile_{label}", params, "coupled profile screen")
    if values["mode"] == "split_piecewise":
        updates.update(
            standing_support_packet_exclusion=values["entry_carve"],
            standing_support_packet_exclusion_schedule=values["entry_schedule"],
            standing_support_packet_exclusion_temporal_profile=values["temporal_profile"],
            standing_support_packet_exclusion_catch=values["catch_carve"],
            standing_support_packet_exclusion_catch_schedule=values["catch_schedule"],
            standing_support_packet_exclusion_catch_temporal_profile=values["temporal_profile"],
            standing_support_packet_null_cushion_log_gain=values["null_gain"],
            standing_support_packet_null_cushion_mode="annular",
            standing_support_packet_null_cushion_inner_radius_multiplier=values["edge_inner_radius_multiplier"],
            standing_support_packet_null_cushion_radius_multiplier=values["edge_outer_radius_multiplier"],
            standing_support_packet_null_cushion_width_multiplier=values["edge_width_multiplier"],
            standing_support_packet_null_cushion_schedule=values["catch_schedule"],
            standing_support_packet_null_cushion_temporal_profile=values["temporal_profile"],
        )
    else:
        if values["replace_carve"]:
            _zero_carve(updates)
        if values["replace_radial"]:
            _zero_radial(updates)
        if values["replace_null"]:
            _zero_null(updates)
        updates.update(
            standing_support_packet_coupled_profile_enabled=True,
            standing_support_packet_coupled_entry_carve=values["entry_carve"],
            standing_support_packet_coupled_catch_carve=values["catch_carve"],
            standing_support_packet_coupled_edge_carve=values["edge_carve"],
            standing_support_packet_coupled_radius_multiplier=values["radius_multiplier"],
            standing_support_packet_coupled_width_multiplier=values["width_multiplier"],
            standing_support_packet_coupled_entry_schedule=values["entry_schedule"],
            standing_support_packet_coupled_catch_schedule=values["catch_schedule"],
            standing_support_packet_coupled_temporal_profile=values["temporal_profile"],
            standing_support_packet_coupled_edge_inner_radius_multiplier=values["edge_inner_radius_multiplier"],
            standing_support_packet_coupled_edge_outer_radius_multiplier=values["edge_outer_radius_multiplier"],
            standing_support_packet_coupled_edge_width_multiplier=values["edge_width_multiplier"],
            standing_support_packet_coupled_rebate_fraction=values["rebate_fraction"],
            standing_support_packet_coupled_radial_log_gain=values["radial_gain"],
            standing_support_packet_coupled_null_cushion_log_gain=values["null_gain"],
        )
    return SourceCase(
        f"{service_factor_label(params)}_coupled_profile_{label}",
        replace(params, **updates),
        "coupled profile screen",
    )


def _row_for_spec(label: str, spec: dict[str, Any], case: SourceCase, points: Any) -> dict[str, Any]:
    values = _values(spec)
    return {
        "label": label,
        **values,
        **source_channel_metrics(case, points),
        "max_coupled_containment_slope": float(
            points["standing_support_packet_coupled_containment_window_slope_abs"].max()
        ),
        "max_coupled_edge_slope": float(points["standing_support_packet_coupled_edge_window_slope_abs"].max()),
        "max_coupled_rebate_slope": float(points["standing_support_packet_coupled_rebate_window_slope_abs"].max()),
        "max_coupled_null_slope": float(
            points["standing_support_packet_coupled_null_cushion_window_slope_abs"].max()
        ),
        "coupled_containment_peak": float(points["standing_support_packet_coupled_containment_window"].max()),
        "coupled_rebate_peak": float(points["standing_support_packet_coupled_rebate_contribution"].max()),
        "coupled_radial_window_peak": float(points["standing_support_packet_coupled_radial_window"].max()),
        "coupled_null_window_peak": float(points["standing_support_packet_coupled_null_cushion_window"].max()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Screen coupled packet containment/support profile families.")
    parser.add_argument("--source-ledger-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--spec-file", type=Path, default=None)
    parser.add_argument("--ns", type=int, default=31)
    parser.add_argument("--nl", type=int, default=55)
    parser.add_argument("--s-min", type=float, default=None)
    parser.add_argument("--s-max", type=float, default=None)
    parser.add_argument("--l-min", type=float, default=None)
    parser.add_argument("--l-max", type=float, default=None)
    parser.add_argument("--h-s", type=float, default=None)
    parser.add_argument("--h-l", type=float, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--only-labels", nargs="+", default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    context = load_source_screen_context(
        args.source_ledger_dir,
        ns=args.ns,
        nl=args.nl,
        s_min=args.s_min,
        s_max=args.s_max,
        l_min=args.l_min,
        l_max=args.l_max,
        h_s=args.h_s,
        h_l=args.h_l,
    )
    specs = select_specs(load_spec_list(args.spec_file, BASE_SPECS, "coupled profile"), args.only_labels, args.limit)
    run_source_screen(
        context=context,
        specs=specs,
        outdir=args.outdir,
        summary_filename="coupled_profile_screen_summary.csv",
        top_filename="coupled_profile_screen_top_bad_points.csv",
        manifest_filename="coupled_profile_screen_manifest.json",
        case_builder=_case_for_spec,
        row_builder=_row_for_spec,
        spec_file=args.spec_file,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
