from __future__ import annotations

import argparse
from pathlib import Path

from .runner import compare_runs, run_from_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="adm-harness", description="ADM ledger harness CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run one ADM harness config")
    run.add_argument("--config", "-c", required=True, help="YAML or JSON config path")
    run.add_argument("--output-dir", "-o", default=None, help="Override output root directory")

    cmp = sub.add_parser("compare", help="Compare completed ADM harness run folders")
    cmp.add_argument("--runs", nargs="+", required=True, help="Run folders containing decision_sheet.csv")
    cmp.add_argument("--output-dir", "-o", required=True, help="Comparison output folder")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        out = run_from_config(args.config, args.output_dir)
        print(f"wrote run: {out}")
        return 0
    if args.command == "compare":
        out = compare_runs(args.runs, args.output_dir)
        print(f"wrote comparison: {out}")
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
