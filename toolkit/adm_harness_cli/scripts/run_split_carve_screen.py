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
    default_packet_profile,
    load_source_screen_context,
    load_spec_list,
    run_source_screen,
    select_specs,
    service_factor_label,
    source_channel_metrics,
)


BASE_SPECS: list[dict[str, Any]] = [
    {"label": "current"},
    {"label": "entry07", "entry_carve": 0.70},
    {"label": "entry07_catch02", "entry_carve": 0.70, "catch_carve": 0.20},
    {"label": "entry075_catch015", "entry_carve": 0.75, "catch_carve": 0.15},
    {"label": "entry08_catch01", "entry_carve": 0.80, "catch_carve": 0.10},
    {"label": "entry07_catch02_null_m005", "entry_carve": 0.70, "catch_carve": 0.20, "null_gain": -0.05},
    {"label": "entry07_catch02_null_p005", "entry_carve": 0.70, "catch_carve": 0.20, "null_gain": 0.05},
    {
        "label": "entry075_catch015_null_ann_m003",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "null_gain": -0.03,
        "null_mode": "annular",
        "null_inner_radius_multiplier": 1.0,
        "null_radius_multiplier": 1.7,
        "null_width_multiplier": 2.2,
    },
    {
        "label": "entry075_catch015_null_ann_m005",
        "entry_carve": 0.75,
        "catch_carve": 0.15,
        "null_gain": -0.05,
        "null_mode": "annular",
        "null_inner_radius_multiplier": 1.0,
        "null_radius_multiplier": 1.7,
        "null_width_multiplier": 2.2,
    },
    {
        "label": "entry08_catch01_null_ann_m003",
        "entry_carve": 0.80,
        "catch_carve": 0.10,
        "null_gain": -0.03,
        "null_mode": "annular",
        "null_inner_radius_multiplier": 1.0,
        "null_radius_multiplier": 1.7,
        "null_width_multiplier": 2.2,
    },
]


def _split_carve_values(spec: dict[str, Any], params: SourceParams) -> dict[str, Any]:
    entry_schedule = str(spec.get("entry_schedule", params.standing_support_packet_exclusion_schedule))
    catch_schedule = str(spec.get("catch_schedule", params.standing_support_packet_exclusion_catch_schedule))
    null_schedule = str(spec.get("null_schedule", params.standing_support_packet_null_cushion_schedule))
    return {
        "entry_carve": float(spec.get("entry_carve", params.standing_support_packet_exclusion)),
        "catch_carve": float(spec.get("catch_carve", params.standing_support_packet_exclusion_catch)),
        "entry_schedule": entry_schedule,
        "catch_schedule": catch_schedule,
        "catch_radius_multiplier": float(
            spec.get(
                "catch_radius_multiplier",
                params.standing_support_packet_exclusion_catch_radius_multiplier,
            )
        ),
        "catch_width_multiplier": float(
            spec.get(
                "catch_width_multiplier",
                params.standing_support_packet_exclusion_catch_width_multiplier,
            )
        ),
        "null_gain": float(spec.get("null_gain", params.standing_support_packet_null_cushion_log_gain)),
        "null_mode": str(spec.get("null_mode", params.standing_support_packet_null_cushion_mode)),
        "null_schedule": null_schedule,
        "null_inner_radius_multiplier": float(
            spec.get(
                "null_inner_radius_multiplier",
                params.standing_support_packet_null_cushion_inner_radius_multiplier,
            )
        ),
        "null_radius_multiplier": float(
            spec.get(
                "null_radius_multiplier",
                params.standing_support_packet_null_cushion_radius_multiplier,
            )
        ),
        "null_width_multiplier": float(
            spec.get(
                "null_width_multiplier",
                params.standing_support_packet_null_cushion_width_multiplier,
            )
        ),
        "entry_temporal_profile": str(spec.get("entry_temporal_profile") or default_packet_profile(entry_schedule)),
        "catch_temporal_profile": str(spec.get("catch_temporal_profile") or default_packet_profile(catch_schedule)),
        "null_temporal_profile": str(spec.get("null_temporal_profile") or default_packet_profile(null_schedule)),
    }


def _case_for_spec(label: str, spec: dict[str, Any], params: SourceParams) -> SourceCase:
    values = _split_carve_values(spec, params)
    case_params = replace(
        params,
        standing_support_packet_exclusion=values["entry_carve"],
        standing_support_packet_exclusion_schedule=values["entry_schedule"],
        standing_support_packet_exclusion_temporal_profile=values["entry_temporal_profile"],
        standing_support_packet_exclusion_catch=values["catch_carve"],
        standing_support_packet_exclusion_catch_radius_multiplier=values["catch_radius_multiplier"],
        standing_support_packet_exclusion_catch_width_multiplier=values["catch_width_multiplier"],
        standing_support_packet_exclusion_catch_schedule=values["catch_schedule"],
        standing_support_packet_exclusion_catch_temporal_profile=values["catch_temporal_profile"],
        standing_support_packet_null_cushion_log_gain=values["null_gain"],
        standing_support_packet_null_cushion_mode=values["null_mode"],
        standing_support_packet_null_cushion_inner_radius_multiplier=values["null_inner_radius_multiplier"],
        standing_support_packet_null_cushion_radius_multiplier=values["null_radius_multiplier"],
        standing_support_packet_null_cushion_width_multiplier=values["null_width_multiplier"],
        standing_support_packet_null_cushion_schedule=values["null_schedule"],
        standing_support_packet_null_cushion_temporal_profile=values["null_temporal_profile"],
    )
    return SourceCase(f"{service_factor_label(params)}_split_carve_{label}", case_params, "split carve/null cushion screen")


def _row_for_spec(label: str, spec: dict[str, Any], case: SourceCase, points: Any) -> dict[str, Any]:
    values = _split_carve_values(spec, case.params)
    return {
        "label": label,
        "entry_carve": values["entry_carve"],
        "catch_carve": values["catch_carve"],
        "entry_schedule": values["entry_schedule"],
        "catch_schedule": values["catch_schedule"],
        "catch_radius_multiplier": values["catch_radius_multiplier"],
        "catch_width_multiplier": values["catch_width_multiplier"],
        "null_gain": values["null_gain"],
        "null_mode": values["null_mode"],
        "null_schedule": values["null_schedule"],
        "null_inner_radius_multiplier": values["null_inner_radius_multiplier"],
        "null_radius_multiplier": values["null_radius_multiplier"],
        "null_width_multiplier": values["null_width_multiplier"],
        **source_channel_metrics(case, points),
        "max_carve_catch_window_slope": float(points["standing_support_packet_carve_catch_window_slope_abs"].max()),
        "max_null_cushion_window_slope": float(points["standing_support_packet_null_cushion_window_slope_abs"].max()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Screen split packet-carve and local null-cushion controls.")
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
    specs = select_specs(load_spec_list(args.spec_file, BASE_SPECS, "split-carve"), args.only_labels, args.limit)
    run_source_screen(
        context=context,
        specs=specs,
        outdir=args.outdir,
        summary_filename="split_carve_screen_summary.csv",
        top_filename="split_carve_screen_top_bad_points.csv",
        manifest_filename="split_carve_screen_manifest.json",
        case_builder=_case_for_spec,
        row_builder=_row_for_spec,
        spec_file=args.spec_file,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
