from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_support_principal_symbol import (  # noqa: E402
    PrincipalSymbolSpec,
    build_principal_symbol_from_runs,
    write_principal_symbol_outputs,
)


BASELINE_ROOT = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15")
DENSE_ROOT = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12")


DEFAULT_RUNS = [
    {
        "label": "baseline_24x14",
        "mesh": "baseline",
        "kind": "reference_24x14",
        "stroke_dir": BASELINE_ROOT / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
    },
    {
        "label": "dense_24x14",
        "mesh": "dense",
        "kind": "reference_24x14",
        "stroke_dir": DENSE_ROOT / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
    },
    {
        "label": "baseline_compact22x13",
        "mesh": "baseline",
        "kind": "compact_22x13",
        "stroke_dir": BASELINE_ROOT / "endpoint_support_stroke_compact22x13_freeze_rematch_w6_t1p5",
    },
    {
        "label": "dense_compact22x13",
        "mesh": "dense",
        "kind": "compact_22x13",
        "stroke_dir": DENSE_ROOT / "endpoint_support_stroke_compact22x13_freeze_rematch_w6_t1p5",
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the reduced fixed-background principal-symbol gate for endpoint/support constitutive variables."
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_principal_symbol"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("supporting_reports/STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md"),
    )
    parser.add_argument("--heat-sound-cap", type=float, default=0.35)
    parser.add_argument("--angular-sound-cap", type=float, default=0.25)
    parser.add_argument("--support-sound-cap", type=float, default=0.40)
    parser.add_argument("--speed-margin-gate", type=float, default=1.0e-6)
    parser.add_argument("--speed-margin-watch", type=float, default=5.0e-3)
    parser.add_argument("--transport-margin-watch", type=float, default=5.0e-3)
    parser.add_argument("--heat-ratio-watch", type=float, default=0.995)
    parser.add_argument("--high-psi-watch", type=float, default=4.0)
    parser.add_argument("--eigen-condition-gate", type=float, default=1.0e8)
    parser.add_argument("--live-support-density-gate", type=float, default=1.0e-14)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    spec = PrincipalSymbolSpec(
        heat_sound_cap=float(args.heat_sound_cap),
        angular_sound_cap=float(args.angular_sound_cap),
        support_sound_cap=float(args.support_sound_cap),
        speed_margin_gate=float(args.speed_margin_gate),
        speed_margin_watch=float(args.speed_margin_watch),
        transport_margin_watch=float(args.transport_margin_watch),
        heat_ratio_watch=float(args.heat_ratio_watch),
        high_psi_watch=float(args.high_psi_watch),
        eigen_condition_gate=float(args.eigen_condition_gate),
        live_support_density_gate=float(args.live_support_density_gate),
    )
    outputs, metadata, report = build_principal_symbol_from_runs(DEFAULT_RUNS, spec=spec)
    files = write_principal_symbol_outputs(args.outdir, args.report, outputs, metadata, report)
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
