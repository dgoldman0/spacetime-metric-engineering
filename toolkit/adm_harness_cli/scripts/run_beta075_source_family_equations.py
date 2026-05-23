from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_source_family_equations import (  # noqa: E402
    SourceFamilyEquationInputs,
    build_source_family_equation_package,
    write_source_family_equation_outputs,
)


DENSE_ROOT = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the beta075 formal source-family equation package."
    )
    parser.add_argument(
        "--source-law-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_law_definition_package"),
    )
    parser.add_argument(
        "--principal-symbol-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_principal_symbol"),
    )
    parser.add_argument(
        "--field-closure-dir",
        type=Path,
        default=DENSE_ROOT / "endpoint_medium_field_closure_validation_freeze_rematch_w6_t1p5",
    )
    parser.add_argument(
        "--stroke-exchange-dir",
        type=Path,
        default=DENSE_ROOT / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
    )
    parser.add_argument(
        "--total-closure-dir",
        type=Path,
        default=DENSE_ROOT / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
    )
    parser.add_argument(
        "--robustness-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_constitutive_1p1_discretization_robustness"),
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_equations"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inputs = SourceFamilyEquationInputs(
        source_law_dir=args.source_law_dir,
        principal_symbol_dir=args.principal_symbol_dir,
        field_closure_dir=args.field_closure_dir,
        stroke_exchange_dir=args.stroke_exchange_dir,
        total_closure_dir=args.total_closure_dir,
        robustness_dir=args.robustness_dir,
    )
    outputs, metadata = build_source_family_equation_package(inputs)
    files = write_source_family_equation_outputs(args.outdir, outputs, metadata)
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
