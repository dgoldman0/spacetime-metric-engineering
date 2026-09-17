# Rebuildable run and build artifact cleanup

The September 17, 2026 cleanup released **5,917,335,552 allocated bytes
(5.511 GiB)**. All 337 selected historical CSVs were rebuilt in temporary
storage and matched their original SHA-256 hashes before removal. Six workers
completed that verification in 189.734 seconds. Their saved configurations,
summaries, reports, and five tracked input datasets remain available.

| Removed artifact | Allocated bytes released |
| --- | ---: |
| 337 sweep and validation `point_ledger.csv` paths | 5,716,488,192 |
| Quiz application `node_modules/` | 196,345,856 |
| Quiz application `dist/` | 3,321,856 |
| Root LaTeX `build/` | 700,416 |
| White Casimir LaTeX `build/` | 479,232 |
| Total | 5,917,335,552 |

The CSVs occupied 274 distinct inodes after the preceding duplicate-storage
cleanup. Two shared datasets retain links outside the selected directories.
The measured allocation reduction accounts for those surviving links and the
earlier deduplication. Immediately after this pass, the checkout occupied
14,135,468,032 bytes and the filesystem reported 6,581,817,344 available bytes,
before the final documentation and Git commit.

## Retained reconstruction material

The [manifest](data/rebuildable_run_cleanup_20260917/manifest.json) stores a
portable configuration and expected content hash for each removed CSV. It also
records input hashes, Python and package versions, and the source revision
`dae3dfa31789ab1cd00f9dcbfa29f4bd777173a4`. The
[verification receipt](data/rebuildable_run_cleanup_20260917/verification.json)
records a successful exact reconstruction for every case.

The selected families are `v5_screen`, `v5_support_shell_screen`,
`v5_direct_window_refine2`, `v5_support_shell_final_sweep`,
`v10_support_shell_edge`, `v5_validation_ladder`,
`v5_validation_ladder_current`, `v5_validation_ladder_frozen`, and
`v10_validation_ladder`. Removal preserved the complete inventory and file
signatures of the other run files. The original configuration hashes for all
337 cases remained unchanged.

## Restore a ledger family

From the repository root:

```bash
python3 -B toolkit/adm_harness_cli/scripts/restore_cleaned_run_ledgers.py \
  --case v5_screen --workers 4
```

The `--case` option selects a prefix beneath `toolkit/adm_harness_cli/runs/` and
can select a single `point_ledger.csv` path. Omitting it restores the complete
set. The default four workers can be adjusted from one through six.

Each case is rebuilt in an isolated temporary directory. Its SHA-256 must match
the saved value before the CSV is installed at its original path. Existing
matching CSVs are reused, and a conflicting existing file produces an error.
The installation preserves run metadata, reports, and summaries. Input hashes
are checked before reconstruction. The `--verify-only` option performs the
same reconstruction and checksum comparison in temporary storage.

Full restoration creates independent files totaling approximately 6.58 GiB,
plus temporary working space. Selecting a run family bounds both the retained
output size and the reconstruction work. The recorded runtime revision and
dependency versions provide the reconstruction baseline as the main code
continues to evolve.

After removal, the restoration command recreated one V=5 and one V=10 ledger
at their original paths with exact hashes and preserved their metadata. Those
two verification outputs were then removed again. The
[restoration receipt](data/rebuildable_run_cleanup_20260917/restoration_verification.json)
records that check.

## Restore dependencies and compiled documents

The quiz application's `package.json` and lockfile remain tracked. From
`toolkit/active_rail_quiz_system/`, `npm ci` restores dependencies and
`npm run build` restores `dist/`. A fresh isolated installation using
`npm ci --offline --ignore-scripts --no-audit --no-fund` succeeded from a
temporary copy of the existing npm cache, and the application built with those
fresh dependencies. The original npm cache remains available. The
[dependency verification](data/rebuildable_run_cleanup_20260917/dependency_verification.json)
records the lockfile hash and successful installation and build.

The three LaTeX documents represented in the removed build directories also
compiled successfully into temporary directories. Their sources and PDFs
outside `build/` remain in place. To recreate a build directory, create
`build/` beside the source and run
`pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build FILE.tex`
from that source directory. The
[build verification](data/rebuildable_run_cleanup_20260917/build_verification.json)
lists the compiled source documents.

The [cleanup measurements](data/rebuildable_run_cleanup_20260917/cleanup.json)
record the removed paths, allocation changes, and preservation checks. Dense
simulation products, supporting scientific datasets, archived input bundles,
and Git history remain available. This commit preserves the recovery tooling
and evidence for the local storage cleanup.
