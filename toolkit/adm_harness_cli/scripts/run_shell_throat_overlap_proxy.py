from __future__ import annotations

import argparse
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
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from adm_harness.source_ledger import (  # noqa: E402
    CHANNELS,
    compute_case,
    sha256_file,
    shell_throat_overlap_proxy_ledger,
    shell_throat_overlap_summary,
    write_manifest,
)
from adm_harness.source_screening import (  # noqa: E402
    load_source_screen_context,
    load_spec_list,
    select_specs,
    source_channel_metrics,
)
from run_smooth_split_screen import BASE_SPECS, _case_for_spec  # noqa: E402


def _params_for_spec(spec: dict[str, Any], base_params: Any) -> Any:
    updates: dict[str, Any] = {}
    if "support_radius" in spec:
        updates["Rth"] = float(spec["support_radius"])
        updates["ROmega"] = float(spec["support_radius"])
    if "Rth" in spec:
        updates["Rth"] = float(spec["Rth"])
    if "ROmega" in spec:
        updates["ROmega"] = float(spec["ROmega"])
    if "support_width" in spec:
        updates["w_th"] = float(spec["support_width"])
    if "w_th" in spec:
        updates["w_th"] = float(spec["w_th"])
    if "angular_width" in spec:
        updates["wOmega"] = float(spec["angular_width"])
    if "wOmega" in spec:
        updates["wOmega"] = float(spec["wOmega"])
    if "angular_gain" in spec:
        updates["aOmega"] = float(spec["angular_gain"])
    if "aOmega" in spec:
        updates["aOmega"] = float(spec["aOmega"])
    return replace(base_params, **updates) if updates else base_params


def _topology_values(spec: dict[str, Any], params: Any) -> dict[str, float]:
    return {
        "Rth": float(params.Rth),
        "ROmega": float(params.ROmega),
        "w_th": float(params.w_th),
        "wOmega": float(params.wOmega),
        "aOmega": float(params.aOmega),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the shell/throat mixed-derivative overlap proxy on smooth-split source cases."
    )
    parser.add_argument("--source-ledger-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--spec-file", type=Path, default=None)
    parser.add_argument("--ns", type=int, default=61)
    parser.add_argument("--nl", type=int, default=83)
    parser.add_argument("--s-min", type=float, default=None)
    parser.add_argument("--s-max", type=float, default=None)
    parser.add_argument("--l-min", type=float, default=None)
    parser.add_argument("--l-max", type=float, default=None)
    parser.add_argument("--h-s", type=float, default=None)
    parser.add_argument("--h-l", type=float, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--only-labels", nargs="+", default=None)
    parser.add_argument("--limit-per-channel", type=int, default=20)
    parser.add_argument(
        "--channels",
        choices=list(CHANNELS),
        nargs="+",
        default=["neg_Tkk_radial", "abs_p_l", "abs_j_l", "abs_pOmega"],
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
    specs = select_specs(load_spec_list(args.spec_file, BASE_SPECS, "smooth split"), args.only_labels, args.limit)
    args.outdir.mkdir(parents=True, exist_ok=True)
    proxy_rows: list[pd.DataFrame] = []
    summary_rows: list[pd.DataFrame] = []
    metric_rows: list[dict[str, Any]] = []

    for spec in specs:
        label = str(spec["label"])
        base_params = _params_for_spec(spec, context.params)
        case = _case_for_spec(label, spec, base_params)
        points = compute_case(case, progress=False, **context.grid)
        metric_rows.append({
            "label": label,
            **_topology_values(spec, case.params),
            **source_channel_metrics(case, points),
        })
        proxy = shell_throat_overlap_proxy_ledger(
            points,
            case.params,
            h_s=float(context.grid["h_s"]),
            h_l=float(context.grid["h_l"]),
            limit_per_channel=int(args.limit_per_channel),
            channels=args.channels,
        )
        proxy.insert(0, "label", label)
        proxy_rows.append(proxy)
        summary = shell_throat_overlap_summary(proxy)
        summary.insert(0, "label", label)
        summary_rows.append(summary)
        print(json.dumps({
            "label": label,
            "case": case.name,
            "rows": int(len(proxy)),
            "summary_rows": int(len(summary)),
        }), flush=True)

    proxy_out = args.outdir / "shell_throat_overlap_points.csv"
    summary_out = args.outdir / "shell_throat_overlap_summary.csv"
    metrics_out = args.outdir / "shell_throat_case_metrics.csv"
    all_proxy = pd.concat(proxy_rows, ignore_index=True) if proxy_rows else pd.DataFrame()
    all_summary = pd.concat(summary_rows, ignore_index=True) if summary_rows else pd.DataFrame()
    all_proxy.to_csv(proxy_out, index=False)
    all_summary.to_csv(summary_out, index=False)
    pd.DataFrame(metric_rows).to_csv(metrics_out, index=False)

    manifest = {
        "source_manifest": str(context.manifest_path),
        "spec_file": str(args.spec_file) if args.spec_file else None,
        "rows": int(len(all_proxy)),
        "summary_rows": int(len(all_summary)),
        "grid": context.grid,
        "limit_per_channel": int(args.limit_per_channel),
        "channels": args.channels,
        "points": str(proxy_out),
        "summary": str(summary_out),
        "case_metrics": str(metrics_out),
        "points_sha256": sha256_file(proxy_out),
        "summary_sha256": sha256_file(summary_out),
        "case_metrics_sha256": sha256_file(metrics_out),
    }
    if args.spec_file:
        manifest["spec_file_sha256"] = sha256_file(args.spec_file)
    write_manifest(args.outdir / "shell_throat_overlap_manifest.json", manifest)
    print(json.dumps({
        "ok": True,
        "points": str(proxy_out),
        "summary": str(summary_out),
        "rows": int(len(all_proxy)),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
