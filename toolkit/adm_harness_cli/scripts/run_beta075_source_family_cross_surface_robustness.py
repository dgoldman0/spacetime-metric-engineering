from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_source_family_cross_surface_robustness import (  # noqa: E402
    CrossSurfaceRobustnessInputs,
    build_cross_surface_robustness,
    default_cross_surface_runs,
    write_cross_surface_robustness_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run cross-surface robustness for the beta075 formal source-family validation."
    )
    parser.add_argument(
        "--equation-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_equations"),
    )
    parser.add_argument(
        "--principal-symbol-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_principal_symbol"),
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_cross_surface_robustness"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inputs = CrossSurfaceRobustnessInputs(
        equation_dir=args.equation_dir,
        principal_symbol_dir=args.principal_symbol_dir,
        runs=default_cross_surface_runs(),
    )
    outputs, metadata = build_cross_surface_robustness(inputs)
    files = write_cross_surface_robustness_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "workers": metadata["workers"],
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "decision": outputs["decision"].iloc[0].to_dict(),
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
