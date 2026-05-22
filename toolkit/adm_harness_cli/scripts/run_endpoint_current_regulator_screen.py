from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_current_regulator import (  # noqa: E402
    build_endpoint_current_regulator_screen,
    write_endpoint_current_regulator_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Screen the endpoint current regulator for the regulated anisotropic heat/current medium."
    )
    parser.add_argument(
        "--fit-dir",
        type=Path,
        required=True,
        help="Directory containing endpoint_j_closure_component_manifest.json or endpoint_j_closure_sector_stress.csv.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--source-name", default="endpoint_j_frozen_source")
    parser.add_argument("--regulator-source-ratio-gate", type=float, default=0.06)
    parser.add_argument("--support-effective-volume-fraction-gate", type=float, default=0.01)
    parser.add_argument("--top-1pct-burden-share-gate", type=float, default=0.50)
    parser.add_argument("--regulator-safety-factor", type=float, default=1.0)
    parser.add_argument("--regulator-density-floor", type=float, default=1.0e-14)
    parser.add_argument("--type-tolerance", type=float, default=1.0e-12)
    parser.add_argument("--top-limit", type=int, default=80)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_endpoint_current_regulator_screen(
        args.fit_dir,
        source_name=args.source_name,
        regulator_source_ratio_gate=float(args.regulator_source_ratio_gate),
        support_effective_volume_fraction_gate=float(args.support_effective_volume_fraction_gate),
        top_1pct_burden_share_gate=float(args.top_1pct_burden_share_gate),
        regulator_safety_factor=float(args.regulator_safety_factor),
        regulator_density_floor=float(args.regulator_density_floor),
        type_tolerance=float(args.type_tolerance),
        top_limit=int(args.top_limit),
    )
    files = write_endpoint_current_regulator_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
