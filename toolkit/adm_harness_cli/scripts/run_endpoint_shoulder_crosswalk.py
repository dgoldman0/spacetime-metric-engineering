from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_shoulder_crosswalk import (  # noqa: E402
    build_endpoint_shoulder_crosswalk,
    write_endpoint_shoulder_crosswalk_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Cross radial string-cloud residual zones against existing metric/service "
            "design-component activity axes."
        )
    )
    parser.add_argument(
        "--component-dir",
        type=Path,
        required=True,
        help="Directory containing component_source_manifest.json.",
    )
    parser.add_argument(
        "--string-cloud-dir",
        type=Path,
        required=True,
        help="Directory containing radial_string_cloud_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--top-n", type=int, default=80)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_endpoint_shoulder_crosswalk(
        args.component_dir,
        args.string_cloud_dir,
        top_n=args.top_n,
    )
    files = write_endpoint_shoulder_crosswalk_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
