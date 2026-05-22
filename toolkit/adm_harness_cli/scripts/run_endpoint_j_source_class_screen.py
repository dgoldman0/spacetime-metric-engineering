from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_j_source_class_screen import (  # noqa: E402
    build_endpoint_j_source_class_screen,
    write_endpoint_j_source_class_screen_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify frozen endpoint-J source stress and screen first physical source classes."
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
    parser.add_argument("--type-iv-burden-gate", type=float, default=0.02)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_endpoint_j_source_class_screen(
        args.fit_dir,
        source_name=args.source_name,
        regulator_source_ratio_gate=float(args.regulator_source_ratio_gate),
        type_iv_burden_gate=float(args.type_iv_burden_gate),
    )
    files = write_endpoint_j_source_class_screen_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
