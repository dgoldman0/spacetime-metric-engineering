from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_support_stroke_exchange import (  # noqa: E402
    build_support_stroke_exchange_fit,
    write_support_stroke_exchange_outputs,
)


def _csv_ints(value: str) -> list[int]:
    return [int(part) for part in value.split(",") if part.strip()]


def _csv_floats(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def _csv_strings(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fit phase-aware support stroke/stress exchange fields with full-grid tail auditing."
    )
    parser.add_argument(
        "--covariant-dir",
        type=Path,
        required=True,
        help="Directory containing endpoint_medium_covariant_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--source-name", default="endpoint_support_stroke_exchange")
    parser.add_argument("--fit-scopes", type=_csv_strings, default=None)
    parser.add_argument("--fit-domains", type=_csv_strings, default=None)
    parser.add_argument("--active-pf-l1-gate", type=float, default=0.50)
    parser.add_argument("--allowed-pf-l1-gate", type=float, default=0.50)
    parser.add_argument("--coordinate-error-gate", type=float, default=0.55)
    parser.add_argument("--coefficient-gate", type=float, default=4.0)
    parser.add_argument("--effective-coefficient-count-gate", type=float, default=18000.0)
    parser.add_argument("--outside-tail-fraction-gate", type=float, default=0.001)
    parser.add_argument("--live-tail-fraction-gate", type=float, default=0.0001)
    parser.add_argument("--high-psi-source-fraction-gate", type=float, default=0.005)
    parser.add_argument("--coefficient-weight", type=float, default=0.02)
    parser.add_argument("--effective-count-weight", type=float, default=0.000002)
    parser.add_argument("--s-centers", type=_csv_ints, default=None)
    parser.add_argument("--l-centers", type=_csv_ints, default=None)
    parser.add_argument("--width-multipliers", type=_csv_floats, default=None)
    parser.add_argument("--ridges", type=_csv_floats, default=None)
    parser.add_argument("--no-laplacian", action="store_true", help="Disable stress-potential Laplacian basis modes.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_support_stroke_exchange_fit(
        args.covariant_dir,
        source_name=args.source_name,
        fit_scopes=args.fit_scopes,
        fit_domains=args.fit_domains,
        active_pf_l1_gate=float(args.active_pf_l1_gate),
        allowed_pf_l1_gate=float(args.allowed_pf_l1_gate),
        coordinate_error_gate=float(args.coordinate_error_gate),
        coefficient_gate=float(args.coefficient_gate),
        effective_coefficient_count_gate=float(args.effective_coefficient_count_gate),
        outside_tail_fraction_gate=float(args.outside_tail_fraction_gate),
        live_tail_fraction_gate=float(args.live_tail_fraction_gate),
        high_psi_source_fraction_gate=float(args.high_psi_source_fraction_gate),
        coefficient_weight=float(args.coefficient_weight),
        effective_count_weight=float(args.effective_count_weight),
        s_centers=args.s_centers,
        l_centers=args.l_centers,
        width_multipliers=args.width_multipliers,
        ridges=args.ridges,
        include_laplacian=not bool(args.no_laplacian),
    )
    files = write_support_stroke_exchange_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
