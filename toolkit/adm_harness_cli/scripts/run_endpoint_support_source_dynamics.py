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
from adm_harness.endpoint_support_source_dynamics import (  # noqa: E402
    SupportSourceDynamicsSpec,
    build_support_source_dynamics,
    write_support_source_dynamics_outputs,
)


DENSE_CLOSURE_DIR = Path(
    "toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/"
    "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a reduced coupled support-source rapidity dynamics check on the bottleneck support-edge slice."
    )
    parser.add_argument("--closure-dir", type=Path, default=DENSE_CLOSURE_DIR)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_source_dynamics"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("supporting_reports/STAGE2_BETA075_SUPPORT_SOURCE_DYNAMICS.md"),
    )
    parser.add_argument("--steps", type=int, default=40)
    parser.add_argument("--cfl", type=float, default=0.45)
    parser.add_argument("--observed-heat-ratio-delta", type=float, default=1.0e-4)
    parser.add_argument("--reference-large-heat-ratio-delta", type=float, default=5.0e-4)
    parser.add_argument("--limiter-safety-fraction", type=float, default=0.95)
    parser.add_argument("--include-pass-margin", type=float, default=0.005)
    parser.add_argument("--bottleneck-source-row-index", type=int, default=None)
    parser.add_argument("--source-column", type=str, default="candidate_support_abs_PF_density")
    parser.add_argument("--source-smoothing-passes", type=int, default=0)
    parser.add_argument("--temporal-profile", choices=["raised_cosine", "flat"], default="raised_cosine")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    symbol_spec = PrincipalSymbolSpec()
    dynamics_spec = SupportSourceDynamicsSpec(
        observed_heat_ratio_delta=float(args.observed_heat_ratio_delta),
        reference_large_heat_ratio_delta=float(args.reference_large_heat_ratio_delta),
        include_pass_margin=float(args.include_pass_margin),
        steps=int(args.steps),
        cfl=float(args.cfl),
        limiter_safety_fraction=float(args.limiter_safety_fraction),
        bottleneck_source_row_index=args.bottleneck_source_row_index,
        source_column=str(args.source_column),
        source_smoothing_passes=int(args.source_smoothing_passes),
        temporal_profile=str(args.temporal_profile),
    )
    outputs, metadata, report = build_support_source_dynamics(
        args.closure_dir,
        symbol_spec=symbol_spec,
        budget_spec=RapidityBudgetSpec(
            include_pass_margin=float(args.include_pass_margin),
            observed_heat_ratio_delta=float(args.observed_heat_ratio_delta),
            reference_large_heat_ratio_delta=float(args.reference_large_heat_ratio_delta),
            speed_margin_gate=float(symbol_spec.speed_margin_gate),
        ),
        dynamics_spec=dynamics_spec,
    )
    files = write_support_source_dynamics_outputs(args.outdir, args.report, outputs, metadata, report)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "report": str(args.report),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "decision": outputs["decision"].iloc[0].to_dict(),
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
