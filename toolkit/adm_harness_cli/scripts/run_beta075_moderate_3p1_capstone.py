from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_moderate_3p1_capstone import (  # noqa: E402
    Moderate3P1Inputs,
    Moderate3P1Spec,
    run_moderate_3p1_v5_capstone,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the moderate local beta075 sealed-V5 3+1/backreaction capstone."
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
        default=Path("toolkit/adm_harness_cli/runs/stage2_external/stage2_beta075_moderate_3p1_v5_capstone"),
    )
    parser.add_argument("--n-phi", type=int, default=24)
    parser.add_argument("--n-steps", type=int, default=64)
    parser.add_argument("--time-chunk-steps", type=int, default=4)
    parser.add_argument("--workers", type=int, default=4)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inputs = Moderate3P1Inputs(
        first_order_dir=args.first_order_dir,
        energy_constant_dir=args.energy_constant_dir,
    )
    spec = Moderate3P1Spec(
        n_phi=args.n_phi,
        n_steps=args.n_steps,
        time_chunk_steps=args.time_chunk_steps,
        workers=args.workers,
    )
    files = run_moderate_3p1_v5_capstone(inputs, args.outdir, spec=spec)
    decision = pd.read_csv(files["decision"]).iloc[0].to_dict()
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "decision": decision,
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
