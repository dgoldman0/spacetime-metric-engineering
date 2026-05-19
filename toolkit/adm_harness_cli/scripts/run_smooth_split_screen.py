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
        "label": "coupled_edge024",
        "mode": "coupled_edge",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.24,
        "null_gain": -0.05,
    },
    {
        "label": "smooth_ref_like",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.0,
        "null_gain": -0.05,
    },
    {
        "label": "smooth_ref_tanh",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.0,
        "null_gain": -0.05,
        "temporal_profile": "tanh",
    },
    {
        "label": "smooth_additive_ref",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.0,
        "null_gain": -0.05,
        "composition": "additive",
    },
    {
        "label": "smooth_additive_edge006",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.06,
        "null_gain": -0.05,
        "composition": "additive",
    },
    {
        "label": "smooth_additive_edge002",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.02,
        "null_gain": -0.05,
        "composition": "additive",
    },
    {
        "label": "smooth_additive_edge004",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.04,
        "null_gain": -0.05,
        "composition": "additive",
    },
    {
        "label": "smooth_additive_edge004_null_m003",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.04,
        "null_gain": -0.03,
        "composition": "additive",
    },
    {
        "label": "smooth_additive_edge004_null_m007",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.04,
        "null_gain": -0.07,
        "composition": "additive",
    },
    {
        "label": "smooth_additive_edge002_null_m007",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.02,
        "null_gain": -0.07,
        "composition": "additive",
    },
    {
        "label": "smooth_additive_edge008",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.08,
        "null_gain": -0.05,
        "composition": "additive",
    },
    {
        "label": "smooth_edge006",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.06,
        "null_gain": -0.05,
    },
    {
        "label": "smooth_edge010",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.10,
        "null_gain": -0.05,
    },
    {
        "label": "smooth_entry085_catch020",
        "mode": "smooth_split",
        "entry_carve": 0.85,
        "catch_carve": 0.20,
        "edge_carve": 0.0,
        "null_gain": -0.05,
    },
    {
        "label": "smooth_entry090_catch015",
        "mode": "smooth_split",
        "entry_carve": 0.90,
        "catch_carve": 0.15,
        "edge_carve": 0.0,
        "null_gain": -0.05,
    },
    {
        "label": "smooth_entry090_catch020_edge006",
        "mode": "smooth_split",
        "entry_carve": 0.90,
        "catch_carve": 0.20,
        "edge_carve": 0.06,
        "null_gain": -0.05,
    },
    {
        "label": "smooth_join_wide",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.06,
        "null_gain": -0.05,
        "temporal_width_multiplier": 1.4,
    },
    {
        "label": "smooth_join_wide_tanh",
        "mode": "smooth_split",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "edge_carve": 0.06,
        "null_gain": -0.05,
        "temporal_profile": "tanh",
        "temporal_width_multiplier": 1.4,
    },
]


def _values(spec: dict[str, Any], params: SourceParams) -> dict[str, Any]:
    return {
        "mode": str(spec.get("mode", "smooth_split")),
        "entry_carve": float(spec.get("entry_carve", 0.75)),
        "catch_carve": float(spec.get("catch_carve", 0.15)),
        "edge_carve": float(spec.get("edge_carve", 0.0)),
        "entry_radius_multiplier": float(
            spec.get("entry_radius_multiplier", params.standing_support_packet_exclusion_radius_multiplier)
        ),
        "entry_width_multiplier": float(
            spec.get("entry_width_multiplier", params.standing_support_packet_exclusion_width_multiplier)
        ),
        "catch_radius_multiplier": float(
            spec.get("catch_radius_multiplier", params.standing_support_packet_exclusion_catch_radius_multiplier)
        ),
        "catch_width_multiplier": float(
            spec.get("catch_width_multiplier", params.standing_support_packet_exclusion_catch_width_multiplier)
        ),
        "edge_inner_radius_multiplier": float(spec.get("edge_inner_radius_multiplier", 1.0)),
        "edge_outer_radius_multiplier": float(spec.get("edge_outer_radius_multiplier", 1.7)),
        "edge_width_multiplier": float(spec.get("edge_width_multiplier", 2.2)),
        "entry_schedule": str(spec.get("entry_schedule", params.standing_support_packet_exclusion_schedule)),
        "catch_schedule": str(spec.get("catch_schedule", "catch_only")),
        "edge_schedule": str(spec.get("edge_schedule", "catch_only")),
        "temporal_profile": str(spec.get("temporal_profile", params.standing_support_packet_exclusion_temporal_profile)),
        "temporal_width_multiplier": float(spec.get("temporal_width_multiplier", 1.0)),
        "composition": str(spec.get("composition", "smooth_union")),
        "null_gain": float(spec.get("null_gain", -0.05)),
    }


def _zero_legacy_packet_controls(updates: dict[str, Any]) -> None:
    updates.update(
        standing_support_packet_exclusion=0.0,
        standing_support_packet_exclusion_catch=0.0,
        standing_support_packet_null_cushion_log_gain=0.0,
        standing_support_packet_coupled_profile_enabled=False,
    )


def _case_for_spec(label: str, spec: dict[str, Any], params: SourceParams) -> SourceCase:
    values = _values(spec, params)
    mode = values["mode"]
    if mode == "current":
        return SourceCase(f"{service_factor_label(params)}_smooth_split_{label}", params, "smooth split screen")

    updates: dict[str, Any] = {}
    if mode == "split_piecewise":
        updates.update(
            standing_support_packet_exclusion=values["entry_carve"],
            standing_support_packet_exclusion_schedule=values["entry_schedule"],
            standing_support_packet_exclusion_temporal_profile=values["temporal_profile"],
            standing_support_packet_exclusion_catch=values["catch_carve"],
            standing_support_packet_exclusion_catch_radius_multiplier=values["catch_radius_multiplier"],
            standing_support_packet_exclusion_catch_width_multiplier=values["catch_width_multiplier"],
            standing_support_packet_exclusion_catch_schedule=values["catch_schedule"],
            standing_support_packet_exclusion_catch_temporal_profile=values["temporal_profile"],
            standing_support_packet_null_cushion_log_gain=values["null_gain"],
            standing_support_packet_null_cushion_mode="annular",
            standing_support_packet_null_cushion_inner_radius_multiplier=values["edge_inner_radius_multiplier"],
            standing_support_packet_null_cushion_radius_multiplier=values["edge_outer_radius_multiplier"],
            standing_support_packet_null_cushion_width_multiplier=values["edge_width_multiplier"],
            standing_support_packet_null_cushion_schedule=values["edge_schedule"],
            standing_support_packet_null_cushion_temporal_profile=values["temporal_profile"],
        )
    elif mode == "coupled_edge":
        _zero_legacy_packet_controls(updates)
        updates.update(
            standing_support_packet_coupled_profile_enabled=True,
            standing_support_packet_coupled_entry_carve=values["entry_carve"],
            standing_support_packet_coupled_catch_carve=values["catch_carve"],
            standing_support_packet_coupled_edge_carve=values["edge_carve"],
            standing_support_packet_coupled_entry_schedule=values["entry_schedule"],
            standing_support_packet_coupled_catch_schedule=values["catch_schedule"],
            standing_support_packet_coupled_temporal_profile=values["temporal_profile"],
            standing_support_packet_coupled_edge_inner_radius_multiplier=values["edge_inner_radius_multiplier"],
            standing_support_packet_coupled_edge_outer_radius_multiplier=values["edge_outer_radius_multiplier"],
            standing_support_packet_coupled_edge_width_multiplier=values["edge_width_multiplier"],
            standing_support_packet_coupled_null_cushion_log_gain=values["null_gain"],
        )
    elif mode == "smooth_split":
        _zero_legacy_packet_controls(updates)
        updates.update(
            standing_support_packet_smooth_split_enabled=True,
            standing_support_packet_smooth_split_entry_carve=values["entry_carve"],
            standing_support_packet_smooth_split_catch_carve=values["catch_carve"],
            standing_support_packet_smooth_split_edge_carve=values["edge_carve"],
            standing_support_packet_smooth_split_entry_radius_multiplier=values["entry_radius_multiplier"],
            standing_support_packet_smooth_split_entry_width_multiplier=values["entry_width_multiplier"],
            standing_support_packet_smooth_split_catch_radius_multiplier=values["catch_radius_multiplier"],
            standing_support_packet_smooth_split_catch_width_multiplier=values["catch_width_multiplier"],
            standing_support_packet_smooth_split_edge_inner_radius_multiplier=values["edge_inner_radius_multiplier"],
            standing_support_packet_smooth_split_edge_outer_radius_multiplier=values["edge_outer_radius_multiplier"],
            standing_support_packet_smooth_split_edge_width_multiplier=values["edge_width_multiplier"],
            standing_support_packet_smooth_split_entry_schedule=values["entry_schedule"],
            standing_support_packet_smooth_split_catch_schedule=values["catch_schedule"],
            standing_support_packet_smooth_split_edge_schedule=values["edge_schedule"],
            standing_support_packet_smooth_split_temporal_profile=values["temporal_profile"],
            standing_support_packet_smooth_split_temporal_width_multiplier=values["temporal_width_multiplier"],
            standing_support_packet_smooth_split_composition=values["composition"],
            standing_support_packet_smooth_split_null_cushion_log_gain=values["null_gain"],
        )
    else:
        raise ValueError(f"Unknown smooth split screen mode: {mode}")

    return SourceCase(
        f"{service_factor_label(params)}_smooth_split_{label}",
        replace(params, **updates),
        "smooth split screen",
    )


def _row_for_spec(label: str, spec: dict[str, Any], case: SourceCase, points: Any) -> dict[str, Any]:
    values = _values(spec, case.params)
    return {
        "label": label,
        **values,
        **source_channel_metrics(case, points),
        "max_smooth_split_containment_slope": float(
            points["standing_support_packet_smooth_split_containment_window_slope_abs"].max()
        ),
        "max_smooth_split_edge_slope": float(points["standing_support_packet_smooth_split_edge_window_slope_abs"].max()),
        "max_smooth_split_null_slope": float(
            points["standing_support_packet_smooth_split_null_cushion_window_slope_abs"].max()
        ),
        "smooth_split_containment_peak": float(points["standing_support_packet_smooth_split_containment_window"].max()),
        "smooth_split_edge_peak": float(points["standing_support_packet_smooth_split_edge_window"].max()),
        "smooth_split_null_peak": float(points["standing_support_packet_smooth_split_null_cushion_window"].max()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Screen smoothed split-family packet-support profiles.")
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
    specs = select_specs(load_spec_list(args.spec_file, BASE_SPECS, "smooth split"), args.only_labels, args.limit)
    run_source_screen(
        context=context,
        specs=specs,
        outdir=args.outdir,
        summary_filename="smooth_split_screen_summary.csv",
        top_filename="smooth_split_screen_top_bad_points.csv",
        manifest_filename="smooth_split_screen_manifest.json",
        case_builder=_case_for_spec,
        row_builder=_row_for_spec,
        spec_file=args.spec_file,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
