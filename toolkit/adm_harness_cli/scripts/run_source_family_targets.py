from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_family_targets import (  # noqa: E402
    build_source_family_targets,
    write_source_family_target_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract explicit source-family fit targets from source-sector closure outputs."
    )
    parser.add_argument(
        "--component-dir",
        type=Path,
        required=True,
        help="Directory containing component_source_manifest.json.",
    )
    parser.add_argument(
        "--ansatz-dir",
        type=Path,
        default=None,
        help="Optional directory containing composite_source_ansatz_manifest.json.",
    )
    parser.add_argument(
        "--snec-dir",
        type=Path,
        default=None,
        help="Optional directory containing hard_affine_snec_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_source_family_targets(
        args.component_dir,
        ansatz_dir=args.ansatz_dir,
        snec_dir=args.snec_dir,
    )
    files = write_source_family_target_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
