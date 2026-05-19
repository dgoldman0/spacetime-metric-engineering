from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.scalar_field_solve import ScalarSolveConfig, run_scalar_field_solve  # noqa: E402
from adm_harness.scalar_source_screen import load_ledger_input  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a fixed-metric localized scalar field solve against a Stage I demanded-source ledger. "
            "Writes heartbeat/progress files so long runs are inspectable."
        )
    )
    parser.add_argument("--ledger-dir", type=Path, required=True)
    parser.add_argument("--label", default=None)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--xi", type=float, default=1.0)
    parser.add_argument("--top-centers", type=int, default=24)
    parser.add_argument("--radial-width", type=float, default=0.22)
    parser.add_argument("--temporal-width", type=float, default=0.16)
    parser.add_argument("--max-abs-phi", type=float, default=1.0)
    parser.add_argument("--maxiter", type=int, default=120)
    parser.add_argument("--checkpoint-every", type=int, default=5)
    parser.add_argument("--live-penalty", type=float, default=2.0)
    parser.add_argument("--gradient-penalty", type=float, default=0.10)
    parser.add_argument("--amplitude-penalty", type=float, default=0.25)
    parser.add_argument("--p-l-penalty", type=float, default=0.15)
    parser.add_argument("--angular-current-penalty", type=float, default=0.05)
    parser.add_argument("--focus-quantile", type=float, default=0.985)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ledger = load_ledger_input(args.ledger_dir, label=args.label)
    config = ScalarSolveConfig(
        label=ledger.label,
        xi=float(args.xi),
        top_centers=int(args.top_centers),
        radial_width=float(args.radial_width),
        temporal_width=float(args.temporal_width),
        max_abs_phi=float(args.max_abs_phi),
        maxiter=int(args.maxiter),
        checkpoint_every=int(args.checkpoint_every),
        live_penalty=float(args.live_penalty),
        gradient_penalty=float(args.gradient_penalty),
        amplitude_penalty=float(args.amplitude_penalty),
        p_l_penalty=float(args.p_l_penalty),
        angular_current_penalty=float(args.angular_current_penalty),
        focus_quantile=float(args.focus_quantile),
    )
    final = run_scalar_field_solve(
        point_ledger_path=ledger.point_ledger_path,
        outdir=args.outdir,
        config=config,
    )
    print(json.dumps({
        "ok": True,
        "label": ledger.label,
        "outdir": str(args.outdir),
        "final": final,
        "inspect": {
            "heartbeat": str(args.outdir / "scalar_field_solve_latest.json"),
            "progress": str(args.outdir / "scalar_field_solve_progress.csv"),
            "top_demand_tracking": str(args.outdir / "scalar_field_solve_top_demand_tracking.csv"),
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
