from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_medium_covariant_audit import (  # noqa: E402
    build_endpoint_medium_covariant_audit,
    write_endpoint_medium_covariant_audit_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit the regulated endpoint medium as a covariant stress-energy tensor."
    )
    parser.add_argument(
        "--field-closure-dir",
        type=Path,
        required=True,
        help="Directory containing endpoint_medium_field_closure_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--point-ledger",
        type=Path,
        default=None,
        help="Optional source_ledger_point_ledger CSV/Parquet override; inferred from manifests by default.",
    )
    parser.add_argument("--projection-error-gate", type=float, default=1.0e-9)
    parser.add_argument("--outside-exchange-gate", type=float, default=0.05)
    parser.add_argument("--live-exchange-gate", type=float, default=0.005)
    parser.add_argument("--top-limit", type=int, default=80)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_endpoint_medium_covariant_audit(
        args.field_closure_dir,
        point_ledger_path=args.point_ledger,
        projection_error_gate=float(args.projection_error_gate),
        outside_exchange_gate=float(args.outside_exchange_gate),
        live_exchange_gate=float(args.live_exchange_gate),
        top_limit=int(args.top_limit),
    )
    files = write_endpoint_medium_covariant_audit_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
