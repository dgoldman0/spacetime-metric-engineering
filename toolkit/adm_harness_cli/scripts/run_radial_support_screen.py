from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import (  # noqa: E402
    SourceCase,
    SourceParams,
    compute_case,
    sha256_file,
    summarize,
    top_bad_points,
    write_manifest,
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


def _load_specs(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return [_tuple_spec_to_dict(spec) for spec in BASE_SPECS]
    raw = json.loads(path.read_text())
    if not isinstance(raw, list):
        raise ValueError("spec file must contain a JSON list of radial support specs")
    specs: list[dict[str, Any]] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"spec {idx} must be a JSON object")
        spec = {
            "label": item["label"],
            "core_gain": item.get("core_gain", 0.0),
            "shoulder_gain": item.get("shoulder_gain", 0.0),
            "core_schedule": item.get("core_schedule", "live_only"),
            "shoulder_schedule": item.get("shoulder_schedule", "live_only"),
            "core_radius_multiplier": item.get("core_radius_multiplier", 1.0),
            "core_width_multiplier": item.get("core_width_multiplier", 1.0),
            "shoulder_radius_multiplier": item.get("shoulder_radius_multiplier", 1.5),
            "shoulder_width_multiplier": item.get("shoulder_width_multiplier", 2.0),
            "skirt_gain": item.get("skirt_gain", 0.0),
            "skirt_mode": item.get("skirt_mode", "annular"),
            "skirt_inner_radius_multiplier": item.get("skirt_inner_radius_multiplier", 2.4),
            "skirt_radius_multiplier": item.get("skirt_radius_multiplier", 2.6),
            "skirt_width_multiplier": item.get("skirt_width_multiplier", 3.6),
            "skirt_schedule": item.get("skirt_schedule", "live_only"),
            "core_temporal_profile": item.get("core_temporal_profile"),
            "shoulder_temporal_profile": item.get("shoulder_temporal_profile"),
            "skirt_temporal_profile": item.get("skirt_temporal_profile"),
        }
        specs.append(spec)
    return specs


def _default_profile(schedule: str) -> str:
    return "minimum_jerk" if schedule != "live_only" else "tanh"


def _resolve_path(base: Path, value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    for candidate in (path, PACKAGE_ROOT / path, base / path, base / path.name):
        if candidate.exists():
            return candidate
    return base / path


def _row_for_case(case: SourceCase, points: pd.DataFrame) -> dict[str, float | int | str]:
    _summary, compact, _stage, safety, _decision = summarize(points)
    channels = compact.set_index("channel")
    return {
        "case": case.name,
        "positive_packet_norm_live": int(safety["positive_packet_norm_live"].iloc[0]),
        "max_packet_norm_live": float(safety["max_packet_norm_live"].iloc[0]),
        "live_Tkk_fraction": float(channels.loc["neg_Tkk_radial", "live_packet_fraction"]),
        "live_p_l_fraction": float(channels.loc["abs_p_l", "live_packet_fraction"]),
        "live_j_l_fraction": float(channels.loc["abs_j_l", "live_packet_fraction"]),
        "live_pOmega_fraction": float(channels.loc["abs_pOmega", "live_packet_fraction"]),
        "Tkk_point_peak": float(channels.loc["neg_Tkk_radial", "point_peak"]),
        "p_l_point_peak": float(channels.loc["abs_p_l", "point_peak"]),
        "j_l_point_peak": float(channels.loc["abs_j_l", "point_peak"]),
        "pOmega_point_peak": float(channels.loc["abs_pOmega", "point_peak"]),
        "max_any_point_peak": float(channels["point_peak"].max()),
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
    manifest_path = args.source_ledger_dir / "source_ledger_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    params = SourceParams(**manifest["params"])

    args.outdir.mkdir(parents=True, exist_ok=True)
    summary_path = args.outdir / "radial_support_screen_summary.csv"
    top_path = args.outdir / "radial_support_screen_top_bad_points.csv"
    specs = _load_specs(args.spec_file)
    if args.only_labels:
        labels = set(args.only_labels)
        specs = [spec for spec in specs if spec["label"] in labels]
    if args.limit is not None:
        specs = specs[: args.limit]

    rows: list[dict[str, float | int | str]] = []
    top_rows: list[pd.DataFrame] = []
    fieldnames: list[str] | None = None
    with summary_path.open("w", newline="") as handle:
        writer: csv.DictWriter | None = None
        for spec in specs:
            label = str(spec["label"])
            core_gain = float(spec["core_gain"])
            shoulder_gain = float(spec["shoulder_gain"])
            core_schedule = str(spec["core_schedule"])
            shoulder_schedule = str(spec["shoulder_schedule"])
            core_r = float(spec["core_radius_multiplier"])
            core_w = float(spec["core_width_multiplier"])
            shoulder_r = float(spec["shoulder_radius_multiplier"])
            shoulder_w = float(spec["shoulder_width_multiplier"])
            skirt_gain = float(spec["skirt_gain"])
            skirt_mode = str(spec["skirt_mode"])
            skirt_inner_r = float(spec["skirt_inner_radius_multiplier"])
            skirt_r = float(spec["skirt_radius_multiplier"])
            skirt_w = float(spec["skirt_width_multiplier"])
            skirt_schedule = str(spec["skirt_schedule"])
            core_profile = str(spec.get("core_temporal_profile") or _default_profile(core_schedule))
            shoulder_profile = str(spec.get("shoulder_temporal_profile") or _default_profile(shoulder_schedule))
            skirt_profile = str(spec.get("skirt_temporal_profile") or _default_profile(skirt_schedule))
            case_params = replace(
                params,
                standing_support_packet_radial_log_gain=core_gain,
                standing_support_packet_radial_radius_multiplier=core_r,
                standing_support_packet_radial_width_multiplier=core_w,
                standing_support_packet_radial_schedule=core_schedule,
                standing_support_packet_radial_temporal_profile=core_profile,
                standing_support_packet_radial_shoulder_log_gain=shoulder_gain,
                standing_support_packet_radial_shoulder_mode="annular",
                standing_support_packet_radial_shoulder_radius_multiplier=shoulder_r,
                standing_support_packet_radial_shoulder_width_multiplier=shoulder_w,
                standing_support_packet_radial_shoulder_schedule=shoulder_schedule,
                standing_support_packet_radial_shoulder_temporal_profile=shoulder_profile,
                standing_support_packet_radial_skirt_log_gain=skirt_gain,
                standing_support_packet_radial_skirt_mode=skirt_mode,
                standing_support_packet_radial_skirt_inner_radius_multiplier=skirt_inner_r,
                standing_support_packet_radial_skirt_radius_multiplier=skirt_r,
                standing_support_packet_radial_skirt_width_multiplier=skirt_w,
                standing_support_packet_radial_skirt_schedule=skirt_schedule,
                standing_support_packet_radial_skirt_temporal_profile=skirt_profile,
            )
            case = SourceCase(f"V5_radial_{label}", case_params, "radial support law screen")
            points = compute_case(
                case,
                ns=args.ns,
                nl=args.nl,
                s_min=args.s_min,
                s_max=args.s_max,
                l_min=args.l_min,
                l_max=args.l_max,
                h_s=args.h_s,
                h_l=args.h_l,
                progress=False,
            )
            row = {
                "label": label,
                "core_gain": core_gain,
                "shoulder_gain": shoulder_gain,
                "core_schedule": core_schedule,
                "shoulder_schedule": shoulder_schedule,
                "skirt_gain": skirt_gain,
                "skirt_mode": skirt_mode,
                "skirt_schedule": skirt_schedule,
                "core_radius_multiplier": core_r,
                "core_width_multiplier": core_w,
                "shoulder_radius_multiplier": shoulder_r,
                "shoulder_width_multiplier": shoulder_w,
                "skirt_inner_radius_multiplier": skirt_inner_r,
                "skirt_radius_multiplier": skirt_r,
                "skirt_width_multiplier": skirt_w,
                "core_temporal_profile": core_profile,
                "shoulder_temporal_profile": shoulder_profile,
                "skirt_temporal_profile": skirt_profile,
                **_row_for_case(case, points),
            }
            rows.append(row)
            if writer is None:
                fieldnames = list(row)
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
            writer.writerow(row)
            handle.flush()
            print(json.dumps(row), flush=True)
            top = top_bad_points(points, limit=8)
            top.insert(0, "screen_case", case.name)
            top_rows.append(top)

    if top_rows:
        pd.concat(top_rows, ignore_index=True).to_csv(top_path, index=False)

    write_manifest(
        args.outdir / "radial_support_screen_manifest.json",
        {
            "source_manifest": str(manifest_path),
            "source_point_ledger": str(_resolve_path(args.source_ledger_dir, manifest["files"]["point_ledger"])),
            "source_point_ledger_sha256": sha256_file(_resolve_path(args.source_ledger_dir, manifest["files"]["point_ledger"])),
            "summary": str(summary_path),
            "top_bad_points": str(top_path),
            "rows": len(rows),
            "summary_sha256": sha256_file(summary_path),
            "spec_file": str(args.spec_file) if args.spec_file else None,
            "grid": {
                "ns": args.ns,
                "nl": args.nl,
                "s_min": args.s_min,
                "s_max": args.s_max,
                "l_min": args.l_min,
                "l_max": args.l_max,
                "h_s": args.h_s,
                "h_l": args.h_l,
            },
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
