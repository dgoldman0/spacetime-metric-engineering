from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_decomposition import decompose_ledger, write_decomposition_outputs  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a Stage II source-decomposition map from demanded-source ledgers."
    )
    parser.add_argument("--ledger-dir", type=Path, action="append", required=True)
    parser.add_argument("--label", action="append", default=None)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--channels",
        nargs="+",
        default=["neg_Tkk_radial", "abs_p_l", "abs_j_l", "abs_pOmega"],
    )
    parser.add_argument("--limit-per-channel", type=int, default=40)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    labels = args.label or []
    if labels and len(labels) != len(args.ledger_dir):
        raise SystemExit("--label must be repeated exactly once per --ledger-dir when provided")
    decompositions = []
    for idx, ledger_dir in enumerate(args.ledger_dir):
        label = labels[idx] if labels else None
        decompositions.append(
            decompose_ledger(
                ledger_dir,
                label=label,
                channels=args.channels,
                limit_per_channel=args.limit_per_channel,
            )
        )
    files = write_decomposition_outputs(args.outdir, decompositions)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "files": {key: str(path) for key, path in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
