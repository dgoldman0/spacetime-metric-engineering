from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_source_family_energy_certificate import (  # noqa: E402
    SourceFamilyEnergyInputs,
    build_source_family_energy_certificate,
    write_source_family_energy_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the beta075 fixed-background source-family energy-estimate certificate."
    )
    parser.add_argument(
        "--cross-surface-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_cross_surface_robustness"),
    )
    parser.add_argument(
        "--equation-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_equations"),
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_energy_certificate"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inputs = SourceFamilyEnergyInputs(
        cross_surface_dir=args.cross_surface_dir,
        equation_dir=args.equation_dir,
    )
    outputs, metadata = build_source_family_energy_certificate(inputs)
    files = write_source_family_energy_outputs(args.outdir, outputs, metadata)
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
