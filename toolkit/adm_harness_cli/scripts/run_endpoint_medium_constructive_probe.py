from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_medium_constructive_probe import (  # noqa: E402
    build_constructive_medium_probe,
    write_constructive_medium_probe_outputs,
)


def _csv_ints(value: str) -> list[int]:
    return [int(part) for part in value.split(",") if part.strip()]


def _csv_floats(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Probe finite internal angular response for the regulated endpoint medium."
    )
    parser.add_argument(
        "--fit-dir",
        type=Path,
        required=True,
        help="Directory containing endpoint_j_closure_component_manifest.json or endpoint_j_closure_sector_stress.csv.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--source-name", default="endpoint_j_frozen_source")
    parser.add_argument("--regulator-safety-factor", type=float, default=1.10)
    parser.add_argument("--normalized-l1-gate", type=float, default=0.12)
    parser.add_argument("--angular-watch-l1-gate", type=float, default=0.16)
    parser.add_argument("--coefficient-gate", type=float, default=1.0)
    parser.add_argument("--coefficient-weight", type=float, default=0.02)
    parser.add_argument("--s-centers", type=_csv_ints, default=None)
    parser.add_argument("--l-centers", type=_csv_ints, default=None)
    parser.add_argument("--width-multipliers", type=_csv_floats, default=None)
    parser.add_argument("--ridges", type=_csv_floats, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_constructive_medium_probe(
        args.fit_dir,
        source_name=args.source_name,
        regulator_safety_factor=float(args.regulator_safety_factor),
        normalized_l1_gate=float(args.normalized_l1_gate),
        angular_watch_l1_gate=float(args.angular_watch_l1_gate),
        coefficient_gate=float(args.coefficient_gate),
        coefficient_weight=float(args.coefficient_weight),
        s_centers=args.s_centers,
        l_centers=args.l_centers,
        width_multipliers=args.width_multipliers,
        ridges=args.ridges,
    )
    files = write_constructive_medium_probe_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
