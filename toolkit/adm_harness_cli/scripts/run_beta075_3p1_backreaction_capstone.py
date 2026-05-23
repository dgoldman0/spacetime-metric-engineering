from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_3p1_backreaction_capstone import (  # noqa: E402
    BackreactionCapstoneInputs,
    BackreactionCapstoneSpec,
    build_backreaction_capstone,
    write_backreaction_capstone_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the beta075 local-compute Stage II 3+1/backreaction capstone."
    )
    parser.add_argument(
        "--first-order-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_first_order_3p1_coupling"),
    )
    parser.add_argument(
        "--energy-constant-dir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_energy_constant_audit"),
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_external/stage2_beta075_3p1_backreaction_capstone"),
    )
    parser.add_argument("--workers", type=int, default=6)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inputs = BackreactionCapstoneInputs(
        first_order_dir=args.first_order_dir,
        energy_constant_dir=args.energy_constant_dir,
    )
    spec = BackreactionCapstoneSpec(workers=args.workers)
    outputs, metadata = build_backreaction_capstone(inputs, spec=spec)
    files = write_backreaction_capstone_outputs(args.outdir, outputs, metadata)
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
