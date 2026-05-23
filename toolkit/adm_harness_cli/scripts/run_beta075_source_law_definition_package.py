from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_source_law_definition_package import (  # noqa: E402
    SourceLawDefinitionInputs,
    build_source_law_definition_package,
    write_source_law_definition_outputs,
)


DENSE_ROOT = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the beta075 observed source-law definition package."
    )
    parser.add_argument(
        "--source-class-dir",
        type=Path,
        default=DENSE_ROOT / "endpoint_j_source_class_screen_freeze_rematch_w6_t1p5",
    )
    parser.add_argument(
        "--covariant-dense-dir",
        type=Path,
        default=DENSE_ROOT / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5",
    )
    parser.add_argument(
        "--principal-symbol-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_principal_symbol"),
    )
    parser.add_argument(
        "--source-law-feasibility-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_source_law_feasibility"),
    )
    parser.add_argument(
        "--proof-obligation-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_constitutive_1p1_proof_obligation"),
    )
    parser.add_argument(
        "--robustness-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_constitutive_1p1_discretization_robustness"),
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_law_definition_package"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inputs = SourceLawDefinitionInputs(
        source_class_dir=args.source_class_dir,
        covariant_dense_dir=args.covariant_dense_dir,
        principal_symbol_dir=args.principal_symbol_dir,
        source_law_feasibility_dir=args.source_law_feasibility_dir,
        proof_obligation_dir=args.proof_obligation_dir,
        robustness_dir=args.robustness_dir,
    )
    outputs, metadata = build_source_law_definition_package(inputs)
    files = write_source_law_definition_outputs(args.outdir, outputs, metadata)
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
