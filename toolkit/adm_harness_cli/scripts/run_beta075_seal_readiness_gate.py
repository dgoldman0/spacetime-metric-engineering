from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_seal_readiness import (  # noqa: E402
    Beta075SealReadinessInputs,
    build_beta075_seal_readiness,
    write_beta075_seal_readiness_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate bounded beta075 support-sector/hyperbolicity gates into a seal-readiness decision."
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_seal_readiness_gate"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("supporting_reports/STAGE2_BETA075_BOUNDED_SEAL_READINESS.md"),
    )
    parser.add_argument(
        "--support-robustness-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_sector_robustness_gate"),
    )
    parser.add_argument(
        "--principal-symbol-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_principal_symbol"),
    )
    parser.add_argument(
        "--symbol-sensitivity-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_symbol_sensitivity"),
    )
    parser.add_argument(
        "--transport-evolution-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_transport_evolution"),
    )
    parser.add_argument(
        "--rapidity-budget-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_rapidity_budget"),
    )
    parser.add_argument(
        "--rapidity-advection-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_rapidity_advection"),
    )
    parser.add_argument(
        "--source-coupling-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_source_coupling_package_support_edge_cap095"),
    )
    parser.add_argument(
        "--source-law-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_source_law_feasibility"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata, report = build_beta075_seal_readiness(
        Beta075SealReadinessInputs(
            support_robustness_dir=args.support_robustness_dir,
            principal_symbol_dir=args.principal_symbol_dir,
            symbol_sensitivity_dir=args.symbol_sensitivity_dir,
            transport_evolution_dir=args.transport_evolution_dir,
            rapidity_budget_dir=args.rapidity_budget_dir,
            rapidity_advection_dir=args.rapidity_advection_dir,
            source_coupling_dir=args.source_coupling_dir,
            source_law_dir=args.source_law_dir,
        )
    )
    files = write_beta075_seal_readiness_outputs(args.outdir, args.report, outputs, metadata, report)
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
