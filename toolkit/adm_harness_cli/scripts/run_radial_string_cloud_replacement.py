from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.radial_string_cloud import (  # noqa: E402
    build_radial_string_cloud_replacement,
    write_radial_string_cloud_replacement_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Subtract a constant-areal-flux radial string-cloud target from A/B/I "
            "and summarize the body/cap residuals."
        )
    )
    parser.add_argument(
        "--component-dir",
        type=Path,
        required=True,
        help="Directory containing component_source_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_radial_string_cloud_replacement(args.component_dir)
    files = write_radial_string_cloud_replacement_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
