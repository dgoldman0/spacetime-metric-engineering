from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_source_family_energy_constant_audit import (  # noqa: E402
    EnergyConstantAuditInputs,
    build_energy_constant_audit,
    write_energy_constant_audit_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify the recurring beta075 source-family energy work constant."
    )
    parser.add_argument(
        "--energy-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_energy_certificate"),
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_energy_constant_audit"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inputs = EnergyConstantAuditInputs(energy_dir=args.energy_dir)
    outputs, metadata = build_energy_constant_audit(inputs)
    files = write_energy_constant_audit_outputs(args.outdir, outputs, metadata)
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
