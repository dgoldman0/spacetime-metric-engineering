from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_j_family_fit import (  # noqa: E402
    build_endpoint_j_family_fit,
    write_endpoint_j_family_fit_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fit finite smooth endpoint-J basis families to the demanded intermediate J target."
    )
    parser.add_argument(
        "--intermediate-dir",
        type=Path,
        required=True,
        help="Directory containing intermediate_source_model_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", action="append", default=None, help="Optional label filter; repeat to include many.")
    parser.add_argument("--s-centers", type=int, default=8)
    parser.add_argument("--l-centers", type=int, default=6)
    parser.add_argument("--width-multiplier", type=float, default=1.25)
    parser.add_argument("--ridge", type=float, default=1.0e-8)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_endpoint_j_family_fit(
        args.intermediate_dir,
        labels=args.label,
        s_centers=int(args.s_centers),
        l_centers=int(args.l_centers),
        width_multiplier=float(args.width_multiplier),
        ridge=float(args.ridge),
    )
    files = write_endpoint_j_family_fit_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
