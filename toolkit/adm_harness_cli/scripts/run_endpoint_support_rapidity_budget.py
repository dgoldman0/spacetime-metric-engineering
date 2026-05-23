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
from adm_harness.endpoint_support_rapidity_budget import (  # noqa: E402
    RapidityBudgetSpec,
    build_rapidity_budget,
    write_rapidity_budget_outputs,
)


DENSE_STROKE_DIR = Path(
    "toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/"
    "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a per-row rapidity budget for dense endpoint/support principal-symbol adversarial rows."
    )
    parser.add_argument("--stroke-dir", type=Path, default=DENSE_STROKE_DIR)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_rapidity_budget"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("supporting_reports/STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md"),
    )
    parser.add_argument("--include-pass-margin", type=float, default=0.005)
    parser.add_argument("--observed-heat-ratio-delta", type=float, default=1.0e-4)
    parser.add_argument("--reference-large-heat-ratio-delta", type=float, default=5.0e-4)
    parser.add_argument("--budget-fraction-watch", type=float, default=0.75)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    symbol_spec = PrincipalSymbolSpec()
    outputs, metadata, report = build_rapidity_budget(
        args.stroke_dir,
        symbol_spec=symbol_spec,
        budget_spec=RapidityBudgetSpec(
            include_pass_margin=float(args.include_pass_margin),
            observed_heat_ratio_delta=float(args.observed_heat_ratio_delta),
            reference_large_heat_ratio_delta=float(args.reference_large_heat_ratio_delta),
            speed_margin_gate=float(symbol_spec.speed_margin_gate),
            budget_fraction_watch=float(args.budget_fraction_watch),
        ),
    )
    files = write_rapidity_budget_outputs(args.outdir, args.report, outputs, metadata, report)
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
