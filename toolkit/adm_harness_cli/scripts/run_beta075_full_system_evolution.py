from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_full_system_evolution import (  # noqa: E402
    FullSystemEvolutionSpec,
    build_full_system_evolution,
    write_full_system_evolution_outputs,
)
from adm_harness.endpoint_support_principal_symbol import PrincipalSymbolSpec  # noqa: E402


DENSE_CLOSURE_DIR = Path(
    "toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/"
    "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5"
)
CAP095_SOURCE_COUPLING_DIR = Path(
    "toolkit/adm_harness_cli/runs/stage2_beta075_support_source_coupling_package_support_edge_cap095"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a full-system fixed-background evolution stress test for the sealed beta075 package."
    )
    parser.add_argument("--closure-dir", type=Path, default=DENSE_CLOSURE_DIR)
    parser.add_argument("--source-coupling-dir", type=Path, default=CAP095_SOURCE_COUPLING_DIR)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_full_system_evolution"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("supporting_reports/STAGE2_BETA075_FULL_SYSTEM_FIXED_BACKGROUND_EVOLUTION.md"),
    )
    parser.add_argument("--steps", type=int, default=48)
    parser.add_argument("--radial-cfl", type=float, default=0.40)
    parser.add_argument("--service-cfl", type=float, default=0.20)
    parser.add_argument("--observed-heat-ratio-delta", type=float, default=1.0e-4)
    parser.add_argument("--reference-large-heat-ratio-delta", type=float, default=5.0e-4)
    parser.add_argument("--limiter-safety-fraction", type=float, default=0.95)
    parser.add_argument("--source-column", type=str, default="candidate_support_abs_PF_density")
    parser.add_argument("--source-smoothing-passes", type=int, default=0)
    parser.add_argument(
        "--source-profile-budget-cap-scope",
        choices=["none", "support_edge_entry_catch", "support_edge_all", "all"],
        default="support_edge_entry_catch",
    )
    parser.add_argument("--source-profile-budget-cap-fraction", type=float, default=0.95)
    parser.add_argument("--source-profile-budget-cap-reference-delta", type=float, default=None)
    parser.add_argument("--temporal-profile", choices=["raised_cosine", "flat"], default="raised_cosine")
    parser.add_argument("--max-workers", type=int, default=4, help="Process workers for independent evolution scenarios.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    symbol_spec = PrincipalSymbolSpec()
    spec = FullSystemEvolutionSpec(
        observed_heat_ratio_delta=float(args.observed_heat_ratio_delta),
        reference_large_heat_ratio_delta=float(args.reference_large_heat_ratio_delta),
        steps=int(args.steps),
        radial_cfl=float(args.radial_cfl),
        service_cfl=float(args.service_cfl),
        limiter_safety_fraction=float(args.limiter_safety_fraction),
        source_column=str(args.source_column),
        source_smoothing_passes=int(args.source_smoothing_passes),
        source_profile_budget_cap_scope=str(args.source_profile_budget_cap_scope),
        source_profile_budget_cap_fraction=float(args.source_profile_budget_cap_fraction),
        source_profile_budget_cap_reference_delta=(
            None
            if args.source_profile_budget_cap_reference_delta is None
            else float(args.source_profile_budget_cap_reference_delta)
        ),
        temporal_profile=str(args.temporal_profile),
        max_workers=None if int(args.max_workers) <= 0 else int(args.max_workers),
    )
    outputs, metadata, report = build_full_system_evolution(
        args.closure_dir,
        args.source_coupling_dir,
        symbol_spec=symbol_spec,
        spec=spec,
    )
    files = write_full_system_evolution_outputs(args.outdir, args.report, outputs, metadata, report)
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
