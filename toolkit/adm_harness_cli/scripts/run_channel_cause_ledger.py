from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
import sys

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import (  # noqa: E402
    CHANNELS,
    SourceParams,
    channel_cause_ledger,
    sha256_file,
    write_manifest,
)


def _resolve_path(base: Path, value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    for candidate in (path, PACKAGE_ROOT / path, base / path, base / path.name):
        if candidate.exists():
            return candidate
    return base / path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a focused channel-cause ledger from an existing source-ledger output directory."
    )
    parser.add_argument(
        "--ledger-dir",
        type=Path,
        required=True,
        help="Directory produced by run_source_ledger.py.",
    )
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--point-ledger", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--limit-per-channel", type=int, default=20)
    parser.add_argument("--channels", choices=list(CHANNELS), nargs="+", default=list(CHANNELS))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ledger_dir = args.ledger_dir
    manifest_path = args.manifest or ledger_dir / "source_ledger_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    point_ledger_path = args.point_ledger
    if point_ledger_path is None:
        point_ledger_path = _resolve_path(ledger_dir, manifest["files"]["point_ledger"])
    out_path = args.out or ledger_dir / "source_ledger_channel_cause.csv"

    params = SourceParams(**manifest["params"])
    grid = manifest["grid"]
    points = pd.read_csv(point_ledger_path)
    cause = channel_cause_ledger(
        points,
        params,
        h_s=float(grid["h_s"]),
        h_l=float(grid["h_l"]),
        limit_per_channel=int(args.limit_per_channel),
        channels=args.channels,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cause.to_csv(out_path, index=False)

    cause_manifest = {
        "source_manifest": str(manifest_path),
        "point_ledger": str(point_ledger_path),
        "output": str(out_path),
        "rows": int(len(cause)),
        "limit_per_channel": int(args.limit_per_channel),
        "channels": args.channels,
        "source_point_ledger_sha256": sha256_file(point_ledger_path),
        "channel_cause_sha256": sha256_file(out_path),
        "case": manifest.get("case"),
        "grid": grid,
    }
    write_manifest(out_path.with_suffix(".manifest.json"), cause_manifest)
    print(json.dumps({
        "ok": True,
        "out": str(out_path),
        "rows": int(len(cause)),
        "manifest": str(out_path.with_suffix(".manifest.json")),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
