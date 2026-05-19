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


BASE_SPECS = [
    ("base", 0.0, 0.0, "live_only", "live_only", 1.0, 1.4, 1.5, 2.0),
    ("core_m002", -0.02, 0.0, "entry_catch_release", "live_only", 1.1, 1.8, 1.5, 2.0),
    ("core_m005", -0.05, 0.0, "entry_catch_release", "live_only", 1.1, 1.8, 1.5, 2.0),
    ("core_p002", 0.02, 0.0, "entry_catch_release", "live_only", 1.1, 1.8, 1.5, 2.0),
    ("core_p005", 0.05, 0.0, "entry_catch_release", "live_only", 1.1, 1.8, 1.5, 2.0),
    ("shoulder_m002", 0.0, -0.02, "live_only", "entry_catch_release", 1.0, 1.4, 1.7, 2.6),
    ("shoulder_p002", 0.0, 0.02, "live_only", "entry_catch_release", 1.0, 1.4, 1.7, 2.6),
    ("shoulder_p005", 0.0, 0.05, "live_only", "entry_catch_release", 1.0, 1.4, 1.7, 2.6),
    ("ring_p005_catch", 0.0, 0.05, "live_only", "catch_only", 1.3, 1.8, 2.2, 2.8),
    ("ring_p008_catch", 0.0, 0.08, "live_only", "catch_only", 1.3, 1.8, 2.2, 2.8),
    ("ring_p005_entry", 0.0, 0.05, "live_only", "entry_catch_release", 1.3, 1.8, 2.2, 2.8),
    ("core_p003_catch", 0.03, 0.0, "catch_only", "live_only", 1.1, 1.8, 1.5, 2.0),
    ("core_p005_catch", 0.05, 0.0, "catch_only", "live_only", 1.1, 1.8, 1.5, 2.0),
    ("core_p003_ring_p003_catch", 0.03, 0.03, "catch_only", "catch_only", 1.2, 1.8, 2.2, 2.8),
    ("core_p003_entry", 0.03, 0.0, "entry_catch_release", "live_only", 1.1, 1.8, 1.5, 2.0),
    ("core_p005_ring_p005_catch", 0.05, 0.05, "entry_catch_release", "catch_only", 1.3, 1.8, 2.2, 2.8),
    ("core_p005_ring_p008_catch", 0.05, 0.08, "entry_catch_release", "catch_only", 1.3, 1.8, 2.2, 2.8),
    ("core_p004_ring_p010_catch", 0.04, 0.10, "entry_catch_release", "catch_only", 1.3, 1.8, 2.2, 2.8),
    ("core_p005_ring_p012_catch", 0.05, 0.12, "entry_catch_release", "catch_only", 1.3, 1.8, 2.2, 2.8),
    ("core_p006_ring_p012_catch", 0.06, 0.12, "entry_catch_release", "catch_only", 1.3, 1.8, 2.2, 2.8),
    ("core_m002_shoulder_p002", -0.02, 0.02, "entry_catch_release", "entry_catch_release", 1.1, 1.8, 1.7, 2.6),
    ("core_p002_shoulder_p002", 0.02, 0.02, "entry_catch_release", "entry_catch_release", 1.1, 1.8, 1.7, 2.6),
    ("core_p005_shoulder_p002", 0.05, 0.02, "entry_catch_release", "entry_catch_release", 1.1, 1.8, 1.7, 2.6),
]


def _tuple_spec_to_dict(spec: tuple[Any, ...]) -> dict[str, Any]:
    label, core_gain, shoulder_gain, core_schedule, shoulder_schedule, core_r, core_w, shoulder_r, shoulder_w = spec
    return {
        "label": label,
        "core_gain": core_gain,
        "shoulder_gain": shoulder_gain,
        "core_schedule": core_schedule,
        "shoulder_schedule": shoulder_schedule,
        "core_radius_multiplier": core_r,
        "core_width_multiplier": core_w,
        "shoulder_radius_multiplier": shoulder_r,
        "shoulder_width_multiplier": shoulder_w,
        "skirt_gain": 0.0,
        "skirt_mode": "annular",
        "skirt_inner_radius_multiplier": 2.4,
        "skirt_radius_multiplier": 2.6,
        "skirt_width_multiplier": 3.6,
        "skirt_schedule": "live_only",
    }


def _default_specs() -> list[dict[str, Any]]:
    return [_tuple_spec_to_dict(spec) for spec in BASE_SPECS]


def _radial_values(spec: dict[str, Any]) -> dict[str, Any]:
    core_schedule = str(spec.get("core_schedule", "live_only"))
    shoulder_schedule = str(spec.get("shoulder_schedule", "live_only"))
    skirt_schedule = str(spec.get("skirt_schedule", "live_only"))
    return {
        "core_gain": float(spec.get("core_gain", 0.0)),
        "shoulder_gain": float(spec.get("shoulder_gain", 0.0)),
        "core_schedule": core_schedule,
        "shoulder_schedule": shoulder_schedule,
        "core_radius_multiplier": float(spec.get("core_radius_multiplier", 1.0)),
        "core_width_multiplier": float(spec.get("core_width_multiplier", 1.0)),
        "shoulder_radius_multiplier": float(spec.get("shoulder_radius_multiplier", 1.5)),
        "shoulder_width_multiplier": float(spec.get("shoulder_width_multiplier", 2.0)),
        "skirt_gain": float(spec.get("skirt_gain", 0.0)),
        "skirt_mode": str(spec.get("skirt_mode", "annular")),
        "skirt_inner_radius_multiplier": float(spec.get("skirt_inner_radius_multiplier", 2.4)),
        "skirt_radius_multiplier": float(spec.get("skirt_radius_multiplier", 2.6)),
        "skirt_width_multiplier": float(spec.get("skirt_width_multiplier", 3.6)),
        "skirt_schedule": skirt_schedule,
        "core_temporal_profile": str(spec.get("core_temporal_profile") or default_packet_profile(core_schedule)),
        "shoulder_temporal_profile": str(
            spec.get("shoulder_temporal_profile") or default_packet_profile(shoulder_schedule)
        ),
        "skirt_temporal_profile": str(spec.get("skirt_temporal_profile") or default_packet_profile(skirt_schedule)),
    }


def _case_for_spec(label: str, spec: dict[str, Any], params: SourceParams) -> SourceCase:
    values = _radial_values(spec)
    case_params = replace(
        params,
        standing_support_packet_radial_log_gain=values["core_gain"],
        standing_support_packet_radial_radius_multiplier=values["core_radius_multiplier"],
        standing_support_packet_radial_width_multiplier=values["core_width_multiplier"],
        standing_support_packet_radial_schedule=values["core_schedule"],
        standing_support_packet_radial_temporal_profile=values["core_temporal_profile"],
        standing_support_packet_radial_shoulder_log_gain=values["shoulder_gain"],
        standing_support_packet_radial_shoulder_mode="annular",
        standing_support_packet_radial_shoulder_radius_multiplier=values["shoulder_radius_multiplier"],
        standing_support_packet_radial_shoulder_width_multiplier=values["shoulder_width_multiplier"],
        standing_support_packet_radial_shoulder_schedule=values["shoulder_schedule"],
        standing_support_packet_radial_shoulder_temporal_profile=values["shoulder_temporal_profile"],
        standing_support_packet_radial_skirt_log_gain=values["skirt_gain"],
        standing_support_packet_radial_skirt_mode=values["skirt_mode"],
        standing_support_packet_radial_skirt_inner_radius_multiplier=values["skirt_inner_radius_multiplier"],
        standing_support_packet_radial_skirt_radius_multiplier=values["skirt_radius_multiplier"],
        standing_support_packet_radial_skirt_width_multiplier=values["skirt_width_multiplier"],
        standing_support_packet_radial_skirt_schedule=values["skirt_schedule"],
        standing_support_packet_radial_skirt_temporal_profile=values["skirt_temporal_profile"],
    )
    return SourceCase(f"{service_factor_label(params)}_radial_{label}", case_params, "radial support law screen")


def _row_for_spec(label: str, spec: dict[str, Any], case: SourceCase, points: Any) -> dict[str, Any]:
    values = _radial_values(spec)
    return {
        "label": label,
        **values,
        **source_channel_metrics(case, points),
        "radial_factor_min": float(points["standing_support_packet_radial_factor"].min()),
        "radial_factor_max": float(points["standing_support_packet_radial_factor"].max()),
        "max_radial_window_slope": float(points["standing_support_packet_radial_window_slope_abs"].max()),
        "max_radial_skirt_window_slope": float(
            points["standing_support_packet_radial_skirt_window_slope_abs"].max()
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a small packet-local radial gamma_ll support screen.")
    parser.add_argument("--source-ledger-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--ns", type=int, default=31)
    parser.add_argument("--nl", type=int, default=55)
    parser.add_argument("--s-min", type=float, default=-0.35)
    parser.add_argument("--s-max", type=float, default=1.65)
    parser.add_argument("--l-min", type=float, default=-2.80)
    parser.add_argument("--l-max", type=float, default=2.80)
    parser.add_argument("--h-s", type=float, default=2.5e-3)
    parser.add_argument("--h-l", type=float, default=2.5e-3)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--only-labels", nargs="+", default=None)
    parser.add_argument(
        "--spec-file",
        type=Path,
        default=None,
        help="Optional JSON list of radial support specs. Overrides the built-in spec list.",
    )
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
    specs = select_specs(load_spec_list(args.spec_file, _default_specs(), "radial support"), args.only_labels, args.limit)
    run_source_screen(
        context=context,
        specs=specs,
        outdir=args.outdir,
        summary_filename="radial_support_screen_summary.csv",
        top_filename="radial_support_screen_top_bad_points.csv",
        manifest_filename="radial_support_screen_manifest.json",
        case_builder=_case_for_spec,
        row_builder=_row_for_spec,
        top_label_column="screen_case",
        top_label_value=lambda _label, case: case.name,
        top_limit=8,
        spec_file=args.spec_file,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
