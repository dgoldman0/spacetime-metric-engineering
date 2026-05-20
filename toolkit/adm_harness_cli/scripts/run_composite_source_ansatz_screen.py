from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.composite_source_ansatz import (  # noqa: E402
    build_composite_source_ansatz_screen,
    write_composite_source_ansatz_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Screen a reduced composite anisotropic source ansatz against component-source assignments."
    )
    parser.add_argument(
        "--component-dir",
        type=Path,
        required=True,
        help="Directory containing component_source_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--promote-h",
        action="store_true",
        help="Promote the unassigned non-live current residual into the H current-relaxation sector.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_composite_source_ansatz_screen(args.component_dir, promote_h=args.promote_h)
    files = write_composite_source_ansatz_outputs(args.outdir, args.component_dir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
