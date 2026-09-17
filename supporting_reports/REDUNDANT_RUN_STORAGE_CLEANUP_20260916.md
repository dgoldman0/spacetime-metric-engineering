# Redundant run storage cleanup

The September 16, 2026 local cleanup released **1,376,235,520 allocated bytes
(1.282 GiB)** from this checkout. The measured reduction comprises
1,366,798,336 bytes of duplicate CSV storage and 9,437,184 bytes of Python and
pytest caches. The operation completed at 2026-09-17 02:37 UTC against Git
revision `7896587d85c2c790dd95341db18d906eb3e0ee04`.

The [machine-readable manifest](data/redundant_run_storage_cleanup_20260916/manifest.json)
records every consolidated path, its retained counterpart, content hash,
original modification time, released allocation, and removed cache directory.
Filesystem allocation fell from 21,427,847,168 to 20,051,611,648 bytes before
adding this small report and manifest. Available filesystem space measured
2,183,737,344 bytes immediately after the cleanup.

## Consolidation scope

The cleanup examined historical `point_ledger.csv` outputs with saved run
configurations, existing inputs, matching run names, and explicit
`outputs.overwrite: true`. Across 36 identical-content groups, 66 redundant
copies became hard links to retained files. All 102 affected paths preserve
their original CSV contents. Run configurations, summaries, reports, input
data, and unique numerical results remain at their existing paths.

The normal harness recreates a run directory before writing its results.
Consequently, regeneration with the recorded overwrite setting creates an
independent replacement for a shared CSV. Specialized source-ledger generators
that write files in place retain separate storage. Tracked scientific files,
Git history, installed dependencies, and build outputs retain their existing
storage as well.

Hard-linked CSVs share an inode, modification time, and contents. Direct
in-place editing through one linked path changes its aliases. Independent
changes use the recorded overwrite-enabled harness or replacement with a
separate file. The manifest preserves the original per-path modification
times; per-run configuration and provenance files remain independent.

## Verification

Six workers computed SHA-256 hashes before and after consolidation. Each
replacement also passed a complete byte comparison immediately before the
atomic link replacement. The complete run-path inventory and logical file
lengths matched their pre-cleanup values, and hashes of all 102 associated run
configurations remained unchanged. The run tree's allocation decreased by
exactly the duplicate-byte total.

A representative `run_from_config` execution started with a hard link to the
historical flow-off ledger in a temporary run directory. Regeneration created
a distinct inode and preserved the original ledger's SHA-256 hash. The
temporary outputs were removed after verification. Cache removal covered
untracked `__pycache__` and `.pytest_cache` directories.

The storage layout belongs to this local checkout. The report and manifest
provide the versioned record of the cleanup and its verification.
