from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_support_reservoir_exchange import (  # noqa: E402
    build_support_reservoir_exchange_fit,
    write_support_reservoir_exchange_outputs,
)


def _csv_ints(value: str) -> list[int]:
    return [int(part) for part in value.split(",") if part.strip()]


def _csv_floats(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def _csv_strings(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fit localized support-reservoir P/F exchange fields for the entrained-director endpoint skeleton."
    )
    parser.add_argument(
        "--covariant-dir",
        type=Path,
        required=True,
        help="Directory containing endpoint_medium_covariant_manifest.json.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--source-name", default="endpoint_support_reservoir_exchange")
    parser.add_argument("--fit-scopes", type=_csv_strings, default=None)
    parser.add_argument("--pf-l1-gate", type=float, default=0.50)
    parser.add_argument("--coordinate-error-gate", type=float, default=0.50)
    parser.add_argument("--coefficient-gate", type=float, default=1.0)
    parser.add_argument("--effective-coefficient-count-gate", type=float, default=120.0)
    parser.add_argument("--high-psi-source-fraction-gate", type=float, default=0.005)
    parser.add_argument("--coefficient-weight", type=float, default=0.02)
    parser.add_argument("--effective-count-weight", type=float, default=0.0005)
    parser.add_argument("--s-centers", type=_csv_ints, default=None)
    parser.add_argument("--l-centers", type=_csv_ints, default=None)
    parser.add_argument("--width-multipliers", type=_csv_floats, default=None)
    parser.add_argument("--ridges", type=_csv_floats, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata = build_support_reservoir_exchange_fit(
        args.covariant_dir,
        source_name=args.source_name,
        fit_scopes=args.fit_scopes,
        pf_l1_gate=float(args.pf_l1_gate),
        coordinate_error_gate=float(args.coordinate_error_gate),
        coefficient_gate=float(args.coefficient_gate),
        effective_coefficient_count_gate=float(args.effective_coefficient_count_gate),
        high_psi_source_fraction_gate=float(args.high_psi_source_fraction_gate),
        coefficient_weight=float(args.coefficient_weight),
        effective_count_weight=float(args.effective_count_weight),
        s_centers=args.s_centers,
        l_centers=args.l_centers,
        width_multipliers=args.width_multipliers,
        ridges=args.ridges,
    )
    files = write_support_reservoir_exchange_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
