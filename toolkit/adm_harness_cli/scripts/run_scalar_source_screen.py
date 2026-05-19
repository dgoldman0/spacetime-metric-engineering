from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.scalar_source_screen import (  # noqa: E402
    DEFAULT_PHI0_VALUES,
    DEFAULT_PROFILES,
    DEFAULT_XI_VALUES,
    load_ledger_input,
    screen_ledgers,
    write_screen_outputs,
)


def _csv_floats(value: str | None, default: tuple[float, ...]) -> list[float]:
    if value is None:
        return list(default)
    out: list[float] = []
    for item in value.split(","):
        text = item.strip()
        if text:
            out.append(float(text))
    return out


def _csv_strings(value: str | None, default: tuple[str, ...]) -> list[str]:
    if value is None:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a reduced Stage II scalar-source compatibility screen against "
            "one or more Stage I source-ledger directories."
        )
    )
    parser.add_argument(
        "--ledger-dir",
        type=Path,
        action="append",
        required=True,
        help="Stage I source-ledger directory containing source_ledger_manifest.json.",
    )
    parser.add_argument(
        "--label",
        action="append",
        default=None,
        help="Optional label for the corresponding --ledger-dir. Repeat in the same order.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--profiles",
        default=None,
        help=f"Comma-separated scalar profiles. Defaults to {','.join(DEFAULT_PROFILES)}.",
    )
    parser.add_argument(
        "--phi0-values",
        default=None,
        help="Comma-separated scalar amplitude values.",
    )
    parser.add_argument(
        "--xi-values",
        default=None,
        help="Comma-separated nonminimal coupling values.",
    )
    parser.add_argument("--top-n", type=int, default=10)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    labels = args.label or []
    if labels and len(labels) != len(args.ledger_dir):
        raise SystemExit("--label must be repeated exactly once per --ledger-dir when provided")

    ledgers = [
        load_ledger_input(path, label=labels[idx] if labels else None)
        for idx, path in enumerate(args.ledger_dir)
    ]
    candidates = screen_ledgers(
        ledgers,
        phi0_values=_csv_floats(args.phi0_values, DEFAULT_PHI0_VALUES),
        xi_values=_csv_floats(args.xi_values, DEFAULT_XI_VALUES),
        profiles=_csv_strings(args.profiles, DEFAULT_PROFILES),
    )
    files = write_screen_outputs(args.outdir, ledgers, candidates, top_n=args.top_n)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": int(len(candidates)),
        "files": {key: str(value) for key, value in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
