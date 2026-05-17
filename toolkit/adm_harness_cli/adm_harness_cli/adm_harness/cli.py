from __future__ import annotations

import argparse
from pathlib import Path

from .runner import compare_runs, run_from_config, validate_config_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="adm-harness", description="ADM ledger harness CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run one ADM harness config")
    run.add_argument("--config", "-c", required=True, help="YAML or JSON config path")
    run.add_argument("--output-dir", "-o", default=None, help="Override output root directory")

    val = sub.add_parser("validate", help="Validate one config and its field/substrate inputs")
    val.add_argument("--config", "-c", required=True, help="YAML or JSON config path")
    val.add_argument("--output-json", default=None, help="Optional validation report JSON path")

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
    if args.command == "validate":
        report = validate_config_file(args.config, args.output_json)
        print("validation: ok" if report.ok else "validation: failed")
        if report.errors:
            for error in report.errors:
                print(f"ERROR: {error}")
        if report.warnings:
            for warning in report.warnings:
                print(f"WARNING: {warning}")
        return 0 if report.ok else 1
    if args.command == "compare":
        out = compare_runs(args.runs, args.output_dir)
        print(f"wrote comparison: {out}")
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
