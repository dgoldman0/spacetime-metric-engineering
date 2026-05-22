from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_j_conservation import (  # noqa: E402
    build_endpoint_j_conservation_diagnostic,
    write_endpoint_j_conservation_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run finite-width and finite-difference conservation proxies for the intermediate endpoint J layer."
    )
    parser.add_argument(
        "--intermediate-dir",
        type=Path,
        required=True,
        help="Directory containing intermediate_source_model_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", action="append", default=None, help="Optional label filter; repeat to include many.")
    parser.add_argument("--top-limit", type=int, default=80, help="Number of highest residual point rows to retain.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_endpoint_j_conservation_diagnostic(
        args.intermediate_dir,
        labels=args.label,
        top_limit=int(args.top_limit),
    )
    files = write_endpoint_j_conservation_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
