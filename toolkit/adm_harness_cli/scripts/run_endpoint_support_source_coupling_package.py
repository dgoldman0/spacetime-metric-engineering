from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_support_principal_symbol import PrincipalSymbolSpec  # noqa: E402
from adm_harness.endpoint_support_rapidity_budget import RapidityBudgetSpec  # noqa: E402
from adm_harness.endpoint_support_source_coupling_package import (  # noqa: E402
    PackageCouplingSpec,
    build_package_source_coupling,
    write_package_source_coupling_outputs,
)


DENSE_CLOSURE_DIR = Path(
    "toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/"
    "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a full-package reduced 1+1 support-source coupling sweep over active non-live support slices."
    )
    parser.add_argument("--closure-dir", type=Path, default=DENSE_CLOSURE_DIR)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_source_coupling_package"),
    )
    parser.add_argument("--steps", type=int, default=40)
    parser.add_argument("--cfl", type=float, default=0.45)
    parser.add_argument("--observed-heat-ratio-delta", type=float, default=1.0e-4)
    parser.add_argument("--reference-large-heat-ratio-delta", type=float, default=5.0e-4)
    parser.add_argument("--limiter-safety-fraction", type=float, default=0.95)
    parser.add_argument("--source-column", type=str, default="candidate_support_abs_PF_density")
    parser.add_argument("--source-smoothing-passes", type=int, default=0)
    parser.add_argument("--temporal-profile", choices=["raised_cosine", "flat"], default="raised_cosine")
    parser.add_argument("--budget-bisection-steps", type=int, default=48)
    parser.add_argument("--top-row-count", type=int, default=160)
    parser.add_argument("--max-workers", type=int, default=4, help="Process workers for budget and slice sweeps.")
    parser.add_argument("--budget-chunksize", type=int, default=64)
    parser.add_argument("--slice-chunksize", type=int, default=8)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    symbol_spec = PrincipalSymbolSpec()
    coupling_spec = PackageCouplingSpec(
        observed_heat_ratio_delta=float(args.observed_heat_ratio_delta),
        reference_large_heat_ratio_delta=float(args.reference_large_heat_ratio_delta),
        steps=int(args.steps),
        cfl=float(args.cfl),
        limiter_safety_fraction=float(args.limiter_safety_fraction),
        source_column=str(args.source_column),
        source_smoothing_passes=int(args.source_smoothing_passes),
        temporal_profile=str(args.temporal_profile),
        budget_bisection_steps=int(args.budget_bisection_steps),
        top_row_count=int(args.top_row_count),
        max_workers=None if int(args.max_workers) <= 0 else int(args.max_workers),
        budget_chunksize=int(args.budget_chunksize),
        slice_chunksize=int(args.slice_chunksize),
    )
    outputs, metadata = build_package_source_coupling(
        args.closure_dir,
        symbol_spec=symbol_spec,
        budget_spec=RapidityBudgetSpec(
            observed_heat_ratio_delta=float(args.observed_heat_ratio_delta),
            reference_large_heat_ratio_delta=float(args.reference_large_heat_ratio_delta),
            speed_margin_gate=float(symbol_spec.speed_margin_gate),
            bisection_steps=int(args.budget_bisection_steps),
        ),
        coupling_spec=coupling_spec,
    )
    files = write_package_source_coupling_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "decision": outputs["decision"].iloc[0].to_dict(),
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
