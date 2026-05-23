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
from adm_harness.endpoint_support_transport_evolution import (  # noqa: E402
    TransportEvolutionSpec,
    build_transport_evolution,
    write_transport_evolution_outputs,
)


DENSE_STROKE_DIR = Path(
    "toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/"
    "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a local fixed-background transport-margin evolution pilot on dense principal-symbol watch rows."
    )
    parser.add_argument("--stroke-dir", type=Path, default=DENSE_STROKE_DIR)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_transport_evolution"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("supporting_reports/STAGE2_BETA075_REDUCED_TRANSPORT_EVOLUTION_PILOT.md"),
    )
    parser.add_argument("--dt", type=float, default=0.02)
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--include-pass-margin", type=float, default=0.005)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata, report = build_transport_evolution(
        args.stroke_dir,
        symbol_spec=PrincipalSymbolSpec(),
        evolution_spec=TransportEvolutionSpec(
            dt=float(args.dt),
            steps=int(args.steps),
            include_pass_margin=float(args.include_pass_margin),
        ),
    )
    files = write_transport_evolution_outputs(args.outdir, args.report, outputs, metadata, report)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "report": str(args.report),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
