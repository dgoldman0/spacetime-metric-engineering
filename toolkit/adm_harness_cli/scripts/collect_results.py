from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


def main() -> int:
    parser = argparse.ArgumentParser(description="Zip ADM harness local run results for review.")
    parser.add_argument("--runs", default="runs", help="Run directory to collect")
    parser.add_argument("--output", default="local_test_results.zip", help="Output ZIP path")
    args = parser.parse_args()
    root = Path(args.runs)
    output = Path(args.output)
    if not root.exists():
        raise SystemExit(f"Run directory does not exist: {root}")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(root.parent))
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
