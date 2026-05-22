from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_j_closure_component import (  # noqa: E402
    build_endpoint_j_closure_component,
    write_endpoint_j_closure_component_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fit a finite support-edge endpoint-J closure component on top of the structured source model."
    )
    parser.add_argument("--intermediate-dir", type=Path, required=True)
    parser.add_argument("--structured-source-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", action="append", default=None)
    parser.add_argument("--mode-count", type=int, action="append", default=None)
    parser.add_argument("--center-count", type=int, action="append", default=None)
    parser.add_argument("--width-multiplier", type=float, action="append", default=None)
    parser.add_argument("--ridge", type=float, action="append", default=None)
    parser.add_argument("--conservation-weight", type=float, action="append", default=None)
    parser.add_argument("--angular-weight", type=float, action="append", default=None)
    parser.add_argument("--overburden-weight", type=float, default=10.0)
    parser.add_argument("--residual-weight", type=float, default=1.0)
    parser.add_argument("--coefficient-weight", type=float, default=0.02)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_endpoint_j_closure_component(
        args.intermediate_dir,
        args.structured_source_dir,
        labels=args.label,
        mode_counts=args.mode_count,
        center_counts=args.center_count,
        width_multipliers=args.width_multiplier,
        ridges=args.ridge,
        conservation_weights=args.conservation_weight,
        angular_weights=args.angular_weight,
        overburden_weight=float(args.overburden_weight),
        residual_weight=float(args.residual_weight),
        coefficient_weight=float(args.coefficient_weight),
    )
    files = write_endpoint_j_closure_component_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
