from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_support_total_closure import (  # noqa: E402
    build_support_total_closure,
    write_support_total_closure_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check total endpoint-plus-support exchange closure from a support stroke fit."
    )
    parser.add_argument(
        "--stroke-dir",
        type=Path,
        required=True,
        help="Directory containing endpoint_support_stroke_exchange_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--source-name", default="endpoint_support_total_closure")
    parser.add_argument("--active-closure-l2-gate", type=float, default=0.55)
    parser.add_argument("--allowed-closure-l2-gate", type=float, default=0.55)
    parser.add_argument("--local-closure-l2-gate", type=float, default=0.55)
    parser.add_argument("--active-closure-pf-gate", type=float, default=0.50)
    parser.add_argument("--allowed-closure-pf-gate", type=float, default=0.50)
    parser.add_argument("--local-closure-pf-gate", type=float, default=0.55)
    parser.add_argument("--outside-residual-fraction-gate", type=float, default=0.006)
    parser.add_argument("--live-residual-fraction-gate", type=float, default=0.005)
    parser.add_argument("--support-tail-fraction-gate", type=float, default=0.001)
    parser.add_argument("--live-support-fraction-gate", type=float, default=0.0001)
    parser.add_argument("--angular-support-gate", type=float, default=1.0e-14)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_support_total_closure(
        args.stroke_dir,
        source_name=args.source_name,
        active_closure_l2_gate=float(args.active_closure_l2_gate),
        allowed_closure_l2_gate=float(args.allowed_closure_l2_gate),
        local_closure_l2_gate=float(args.local_closure_l2_gate),
        active_closure_pf_gate=float(args.active_closure_pf_gate),
        allowed_closure_pf_gate=float(args.allowed_closure_pf_gate),
        local_closure_pf_gate=float(args.local_closure_pf_gate),
        outside_residual_fraction_gate=float(args.outside_residual_fraction_gate),
        live_residual_fraction_gate=float(args.live_residual_fraction_gate),
        support_tail_fraction_gate=float(args.support_tail_fraction_gate),
        live_support_fraction_gate=float(args.live_support_fraction_gate),
        angular_support_gate=float(args.angular_support_gate),
    )
    files = write_support_total_closure_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
