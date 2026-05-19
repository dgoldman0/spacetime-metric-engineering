from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.component_source_ledger import (  # noqa: E402
    ComponentConfig,
    assign_component_sources,
    combine_component_outputs,
    load_component_ledger_input,
    write_component_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a toy Stage II component-source assignment ledger from demanded-source ledgers."
    )
    parser.add_argument("--ledger-dir", type=Path, action="append", required=True)
    parser.add_argument("--label", action="append", default=None)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--no-reset-current-sink",
        action="store_true",
        help="Do not assign the optional reset/support-edge current sink component D.",
    )
    parser.add_argument(
        "--no-live-radial-null-trim",
        action="store_true",
        help="Do not assign the live packet-in-support radial-null trim component E.",
    )
    parser.add_argument(
        "--no-live-radial-pressure-trim",
        action="store_true",
        help="Do not assign the live packet-in-support radial-pressure trim component F.",
    )
    parser.add_argument(
        "--no-infrastructure-angular-capacity",
        action="store_true",
        help="Do not assign the non-live support-plant angular-capacity component G.",
    )
    parser.add_argument(
        "--min-volume-burden",
        type=float,
        default=0.0,
        help="Drop point-channel rows at or below this volume burden.",
    )
    parser.add_argument("--top-unassigned", type=int, default=80)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    labels = args.label or []
    if labels and len(labels) != len(args.ledger_dir):
        raise SystemExit("--label must be repeated exactly once per --ledger-dir when provided")

    ledgers = [
        load_component_ledger_input(path, label=labels[idx] if labels else None)
        for idx, path in enumerate(args.ledger_dir)
    ]
    config = ComponentConfig(
        include_reset_current_sink=not args.no_reset_current_sink,
        include_live_radial_null_trim=not args.no_live_radial_null_trim,
        include_live_radial_pressure_trim=not args.no_live_radial_pressure_trim,
        include_infrastructure_angular_capacity=not args.no_infrastructure_angular_capacity,
        min_volume_burden=float(args.min_volume_burden),
        top_unassigned=int(args.top_unassigned),
    )
    outputs = combine_component_outputs(
        assign_component_sources(ledger, config=config)
        for ledger in ledgers
    )
    files = write_component_outputs(args.outdir, ledgers, outputs, config=config)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
