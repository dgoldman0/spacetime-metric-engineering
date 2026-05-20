from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.hard_affine_snec import (  # noqa: E402
    SECTOR_ORDER,
    build_hard_affine_snec_screen,
    write_hard_affine_snec_outputs,
)


def _sector_scales(values: list[str] | None) -> dict[str, float]:
    scales: dict[str, float] = {}
    for value in values or []:
        if "=" not in value:
            raise SystemExit(f"--sector-scale must use SECTOR=SCALE, got {value!r}")
        sector, raw_scale = value.split("=", 1)
        sector = sector.strip()
        if sector not in SECTOR_ORDER:
            allowed = ", ".join(SECTOR_ORDER)
            raise SystemExit(f"unknown sector {sector!r}; allowed sectors: {allowed}")
        scales[sector] = float(raw_scale)
    return scales


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a sector-resolved affine radial-null SNEC screen from a component-source assignment."
    )
    parser.add_argument(
        "--component-dir",
        type=Path,
        required=True,
        help="Directory containing component_source_manifest.json.",
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
        "--sector-scale",
        action="append",
        default=None,
        help="Scale a sector contribution as SECTOR=SCALE. Repeat for ablations.",
    )
    parser.add_argument(
        "--total-mode",
        choices=["geometric", "sector_sum"],
        default="geometric",
        help="Use the geometric demanded total or the scaled sector-sum total.",
    )
    parser.add_argument("--top-limit", type=int, default=120)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_hard_affine_snec_screen(
        args.component_dir,
        smear_widths=args.smear_width or (0.25, 0.50, 1.00),
        benchmark_b=float(args.benchmark_b),
        center_stride=int(args.center_stride),
        top_limit=int(args.top_limit),
        min_support_coverage=float(args.min_support_coverage),
        min_kernel_coverage=float(args.min_kernel_coverage),
        sector_scales=_sector_scales(args.sector_scale),
        total_mode=str(args.total_mode),
    )
    files = write_hard_affine_snec_outputs(args.outdir, args.component_dir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
