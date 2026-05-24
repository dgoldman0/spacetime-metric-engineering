from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_bv_denominator_ledger import (  # noqa: E402
    BVDenominatorLedgerInputs,
    BVDenominatorLedgerSpec,
    build_bv_denominator_ledger,
    default_bv_denominator_inputs,
    write_bv_denominator_ledger_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    defaults = default_bv_denominator_inputs()
    parser = argparse.ArgumentParser(
        description="Build a Parquet boundedness ledger for the beta075 Barcelo--Visser analogue source-family question."
    )
    parser.add_argument("--baseline-admissibility", type=Path, default=defaults.baseline_admissibility)
    parser.add_argument("--dense-admissibility", type=Path, default=defaults.dense_admissibility)
    parser.add_argument("--cross-surface-point-symbol", type=Path, default=defaults.cross_surface_point_symbol)
    parser.add_argument("--energy-point", type=Path, default=defaults.energy_point)
    parser.add_argument("--geometric-anec-traces", type=Path, default=defaults.geometric_anec_traces)
    parser.add_argument("--residual-trimmed-anec-traces", type=Path, default=defaults.residual_trimmed_anec_traces)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_bv_denominator_ledger"),
    )
    parser.add_argument("--max-workers", type=int, default=6)
    parser.add_argument("--top-rows-per-metric", type=int, default=80)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inputs = BVDenominatorLedgerInputs(
        baseline_admissibility=args.baseline_admissibility,
        dense_admissibility=args.dense_admissibility,
        cross_surface_point_symbol=args.cross_surface_point_symbol,
        energy_point=args.energy_point,
        geometric_anec_traces=args.geometric_anec_traces,
        residual_trimmed_anec_traces=args.residual_trimmed_anec_traces,
    )
    spec = BVDenominatorLedgerSpec(
        max_workers=args.max_workers,
        top_rows_per_metric=args.top_rows_per_metric,
    )
    outputs, metadata = build_bv_denominator_ledger(inputs, spec=spec)
    files = write_bv_denominator_ledger_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "workers": metadata["workers"],
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
