from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.finite_domain_anec import (  # noqa: E402
    build_finite_domain_anec_screen,
    write_finite_domain_anec_outputs,
)
from adm_harness.hard_affine_snec import SECTOR_ORDER  # noqa: E402


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
        description="Run a finite-domain radial ANEC diagnostic from a component-source assignment."
    )
    parser.add_argument(
        "--component-dir",
        type=Path,
        required=True,
        help="Directory containing component_source_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--seed-stride",
        type=int,
        default=16,
        help="Use every Nth grid point as a uniform radial-null seed.",
    )
    parser.add_argument(
        "--top-per-branch",
        type=int,
        default=120,
        help="Add this many branch-specific adversarial seeds per source family.",
    )
    parser.add_argument(
        "--snec-top-windows",
        type=Path,
        default=None,
        help="Optional hard_affine_snec_top_windows.csv to seed from worst SNEC centers.",
    )
    parser.add_argument("--top-limit", type=int, default=120)
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
    parser.add_argument(
        "--parameterization",
        choices=["affine", "lapse"],
        default="affine",
        help="Use affine reparameterization from radial-null non-affinity diagnostics, or legacy lapse parameter.",
    )
    parser.add_argument(
        "--lambda-extent",
        type=float,
        default=1.0e6,
        help="Large affine extent cap; traces normally stop at ledger-domain boundaries first.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Process workers for independent seed-trace chunks. Use 1 for serial.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    started_at = time.perf_counter()
    print(json.dumps({
        "event": "finite_domain_anec_compute_start",
        "component_dir": str(args.component_dir),
        "outdir": str(args.outdir),
        "seed_stride": int(args.seed_stride),
        "top_per_branch": int(args.top_per_branch),
        "snec_top_windows": str(args.snec_top_windows) if args.snec_top_windows else "",
        "total_mode": str(args.total_mode),
        "parameterization": str(args.parameterization),
        "max_workers": int(args.max_workers),
    }), flush=True)
    outputs, metadata = build_finite_domain_anec_screen(
        args.component_dir,
        seed_stride=int(args.seed_stride),
        top_per_branch=int(args.top_per_branch),
        top_limit=int(args.top_limit),
        snec_top_windows_path=args.snec_top_windows,
        sector_scales=_sector_scales(args.sector_scale),
        total_mode=str(args.total_mode),
        parameterization=str(args.parameterization),
        lambda_extent=float(args.lambda_extent),
        max_workers=None if int(args.max_workers) <= 0 else int(args.max_workers),
    )
    files = write_finite_domain_anec_outputs(args.outdir, args.component_dir, outputs, metadata)
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
