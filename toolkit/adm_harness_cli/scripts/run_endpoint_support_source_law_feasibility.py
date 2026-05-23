from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.endpoint_support_source_law_feasibility import (  # noqa: E402
    SourceLawFeasibilitySpec,
    build_source_law_feasibility,
    write_source_law_feasibility_outputs,
)


CAP095_COUPLING_DIR = Path(
    "toolkit/adm_harness_cli/runs/stage2_beta075_support_source_coupling_package_support_edge_cap095"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit whether the support-edge source-profile cap behaves as a bounded phase-local source law."
    )
    parser.add_argument("--coupling-dir", type=Path, default=CAP095_COUPLING_DIR)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_source_law_feasibility"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional standalone report path. By default the audit writes only structured artifacts.",
    )
    parser.add_argument("--observed-heat-ratio-delta", type=float, default=1.0e-4)
    parser.add_argument("--severe-scale-watch", type=float, default=0.25)
    parser.add_argument("--adjacent-scale-jump-watch", type=float, default=0.50)
    parser.add_argument("--min-margin-gate", type=float, default=1.0e-6)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata, report = build_source_law_feasibility(
        args.coupling_dir,
        spec=SourceLawFeasibilitySpec(
            observed_heat_ratio_delta=float(args.observed_heat_ratio_delta),
            severe_scale_watch=float(args.severe_scale_watch),
            adjacent_scale_jump_watch=float(args.adjacent_scale_jump_watch),
            min_margin_gate=float(args.min_margin_gate),
        ),
    )
    files = write_source_law_feasibility_outputs(args.outdir, args.report, outputs, metadata, report)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "report": None if args.report is None else str(args.report),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "decision": outputs["decision"].iloc[0].to_dict(),
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
