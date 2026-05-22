from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_medium_admissibility import (  # noqa: E402
    build_endpoint_medium_admissibility_audit,
    write_endpoint_medium_admissibility_outputs,
)


def _csv_floats(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run necessary-condition admissibility audit for the regulated endpoint heat/current medium."
    )
    parser.add_argument(
        "--fit-dir",
        type=Path,
        required=True,
        help="Directory containing endpoint_j_closure_component_manifest.json or endpoint_j_closure_sector_stress.csv.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--source-name", default="endpoint_j_frozen_source")
    parser.add_argument("--regulator-safety-factors", type=_csv_floats, default=[1.0, 1.05, 1.10, 1.25])
    parser.add_argument("--decision-safety-factor", type=float, default=1.10)
    parser.add_argument("--regulator-source-ratio-gate", type=float, default=0.06)
    parser.add_argument("--boundary-gradient-ratio-gate", type=float, default=0.06)
    parser.add_argument("--transport-p99-gate", type=float, default=0.995)
    parser.add_argument("--regulator-density-floor", type=float, default=1.0e-14)
    parser.add_argument("--type-tolerance", type=float, default=1.0e-12)
    parser.add_argument("--top-limit", type=int, default=80)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_endpoint_medium_admissibility_audit(
        args.fit_dir,
        source_name=args.source_name,
        regulator_safety_factors=args.regulator_safety_factors,
        decision_safety_factor=float(args.decision_safety_factor),
        regulator_source_ratio_gate=float(args.regulator_source_ratio_gate),
        boundary_gradient_ratio_gate=float(args.boundary_gradient_ratio_gate),
        transport_p99_gate=float(args.transport_p99_gate),
        regulator_density_floor=float(args.regulator_density_floor),
        type_tolerance=float(args.type_tolerance),
        top_limit=int(args.top_limit),
    )
    files = write_endpoint_medium_admissibility_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
