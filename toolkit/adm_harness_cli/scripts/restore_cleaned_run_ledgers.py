"""Rebuild archived point ledgers from the cleanup manifest and verify their hashes."""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = "supporting_reports/data/rebuildable_run_cleanup_20260917/manifest.json"
RUN_PREFIX = "toolkit/adm_harness_cli/runs/"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_path(relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Expected a repository-relative path: {relative}")
    result = REPO_ROOT / path
    result.resolve().relative_to(REPO_ROOT)
    return result


def rebuild_case(case: dict, verify_only: bool) -> dict:
    started = time.monotonic()
    relative = case["path"]
    if not relative.startswith(RUN_PREFIX) or Path(relative).name != "point_ledger.csv":
        raise ValueError(f"Unexpected ledger destination: {relative}")
    destination = repository_path(relative)
    expected = case["sha256"]
    if destination.is_symlink():
        raise ValueError(f"Destination is a symbolic link: {relative}")
    if destination.exists():
        if sha256(destination) != expected:
            raise ValueError(f"Existing ledger has different contents: {relative}")
        if not verify_only:
            return {"path": relative, "status": "already_present", "sha256": expected}

    with tempfile.TemporaryDirectory(prefix="active-rail-ledger-rebuild-") as scratch:
        scratch = Path(scratch)
        os.environ["MPLCONFIGDIR"] = str(scratch / "matplotlib")
        os.environ["MPLBACKEND"] = "Agg"
        sys.dont_write_bytecode = True
        package_root = str(REPO_ROOT / "toolkit/adm_harness_cli")
        if package_root not in sys.path:
            sys.path.insert(0, package_root)
        from adm_harness.runner import run_from_config

        config = copy.deepcopy(case["config"])
        if config["run_name"] != destination.parent.name:
            raise ValueError(f"Configuration run name differs from destination: {relative}")
        config["inputs"] = {
            key: str(repository_path(value)) for key, value in config["inputs"].items()
        }
        config.setdefault("outputs", {}).update(
            root=str(scratch / "runs"), overwrite=True, format="csv", report=False, figures=False
        )
        config_path = scratch / "config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        output = run_from_config(config_path, output_dir=scratch / "runs") / "point_ledger.csv"
        actual = sha256(output)
        if actual != expected:
            raise ValueError(
                f"Rebuild differs from the recorded ledger: {relative}; "
                "use the runtime revision and dependency versions recorded in the manifest"
            )
        if not verify_only:
            destination.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix=".restoring-ledger-", dir=destination.parent)
            try:
                with os.fdopen(fd, "wb") as target, output.open("rb") as source:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
                    target.flush()
                    os.fsync(target.fileno())
                os.chmod(temporary, case.get("mode", 0o644))
                # An exclusive link preserves any file concurrently created at the destination.
                os.link(temporary, destination)
            finally:
                Path(temporary).unlink(missing_ok=True)
        return {
            "path": relative,
            "status": "verified" if verify_only else "restored",
            "sha256": actual,
            "seconds": round(time.monotonic() - started, 6),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--workers", type=int, choices=range(1, 7), default=4)
    parser.add_argument("--case", action="append", default=[], help="Run-relative path prefix; repeat to select several")
    parser.add_argument("--verify-only", action="store_true", help="Rebuild and check in temporary storage without installing CSVs")
    parser.add_argument("--receipt", type=Path, help="Optional JSON verification or restoration receipt")
    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = REPO_ROOT / manifest_path
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = manifest["cases"]
    if args.case:
        cases = [
            case for case in cases
            if any(case["path"][len(RUN_PREFIX):].startswith(prefix) for prefix in args.case)
        ]
    if not cases:
        parser.error("No manifest cases match the selection")
    if len({case["path"] for case in cases}) != len(cases):
        raise ValueError("Manifest contains duplicate destination paths")
    inputs = {value for case in cases for value in case["config"]["inputs"].values()}
    for relative in sorted(inputs):
        if sha256(repository_path(relative)) != manifest["inputs"][relative]["sha256"]:
            raise ValueError(f"Input differs from the recorded version: {relative}")

    started = time.monotonic()
    results, errors = [], []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(rebuild_case, case, args.verify_only): case["path"] for case in cases}
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append({"path": futures[future], "error": str(exc)})
            finished = len(results) + len(errors)
            if finished % 25 == 0 or finished == len(cases):
                print(json.dumps({"completed": finished, "total": len(cases), "errors": len(errors)}), flush=True)
    receipt = {
        "manifest": str(manifest_path.relative_to(REPO_ROOT)),
        "manifest_sha256": sha256(manifest_path),
        "mode": "verify_only" if args.verify_only else "restore",
        "workers": args.workers,
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "results": sorted(results, key=lambda item: item["path"]),
        "errors": sorted(errors, key=lambda item: item["path"]),
    }
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"successful": len(results), "failed": len(errors), "elapsed_seconds": receipt["elapsed_seconds"]}))
    if errors:
        for error in errors:
            print(json.dumps(error), file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
