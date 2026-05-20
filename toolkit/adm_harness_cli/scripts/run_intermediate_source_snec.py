from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.intermediate_source_snec import (  # noqa: E402
    build_intermediate_source_snec_screen,
    write_intermediate_source_snec_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an affine radial-null SNEC screen for the intermediate source sector package."
    )
    parser.add_argument(
        "--component-dir",
        type=Path,
        required=True,
        help="Directory containing component_source_manifest.json.",
    )
    parser.add_argument(
        "--intermediate-dir",
        type=Path,
        required=True,
        help="Directory containing intermediate_source_model_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--smear-width",
        type=float,
        action="append",
        default=None,
        help="Affine Gaussian smear width. Repeat to scan multiple widths.",
    )
    parser.add_argument(
        "--benchmark-b",
        type=float,
        default=1.0 / (32.0 * math.pi),
        help="Benchmark B in the geometric SNEC floor -8*pi*B/tau^2.",
    )
    parser.add_argument(
        "--center-stride",
        type=int,
        default=1,
        help="Scan every Nth grid center after sorting by s,l.",
    )
    parser.add_argument(
        "--min-support-coverage",
        type=float,
        default=0.80,
        help="Minimum two-sided +/-4 tau affine support coverage for scoreable windows.",
    )
    parser.add_argument(
        "--min-kernel-coverage",
        type=float,
        default=0.80,
        help="Minimum Gaussian kernel integral coverage for scoreable windows.",
    )
    parser.add_argument(
        "--total-mode",
        choices=["intermediate_sector_sum", "geometric", "intermediate_plus_residual"],
        default="intermediate_sector_sum",
        help="Which pointwise total to smear as the tested Tkk package.",
    )
    parser.add_argument("--top-limit", type=int, default=120)
    parser.add_argument(
        "--progress",
        dest="progress",
        action="store_true",
        default=True,
        help="Print center-scan progress while building uncached SNEC windows.",
    )
    parser.add_argument(
        "--no-progress",
        dest="progress",
        action="store_false",
        help="Suppress center-scan progress for quiet batch runs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    smear_widths = args.smear_width or (0.25, 0.50, 1.00)
    started_at = time.perf_counter()
    print(json.dumps({
        "event": "intermediate_source_snec_compute_start",
        "component_dir": str(args.component_dir),
        "intermediate_dir": str(args.intermediate_dir),
        "outdir": str(args.outdir),
        "smear_widths": [float(width) for width in smear_widths],
        "center_stride": int(args.center_stride),
        "total_mode": str(args.total_mode),
    }), flush=True)
    outputs, metadata = build_intermediate_source_snec_screen(
        args.component_dir,
        args.intermediate_dir,
        smear_widths=smear_widths,
        benchmark_b=float(args.benchmark_b),
        center_stride=int(args.center_stride),
        top_limit=int(args.top_limit),
        min_support_coverage=float(args.min_support_coverage),
        min_kernel_coverage=float(args.min_kernel_coverage),
        total_mode=str(args.total_mode),
        progress=bool(args.progress),
    )
    files = write_intermediate_source_snec_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "elapsed_s": round(time.perf_counter() - started_at, 3),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
