from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.radial_shell_viability import (  # noqa: E402
    build_radial_shell_viability,
    write_radial_shell_viability_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Decompose A/B/I radial support into string-like scaffold and residual viability targets."
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
    outputs, metadata = build_radial_shell_viability(args.component_dir)
    files = write_radial_shell_viability_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
