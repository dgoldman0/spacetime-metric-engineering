# Evidence review data (2026-09-26)

Supporting data for
[EVIDENCE_REVIEW_AND_IDENTITY_VERIFICATION.md](../../EVIDENCE_REVIEW_AND_IDENTITY_VERIFICATION.md).
The review was assembled in a session that planned a textbook on spacetime
engineering. It checked the physics this repository states, surveyed the
literature around it, and read the project's own record for lessons. Every
file here is kept as written, including drafts and superseded revisions.

## Contents

### `verification/`

Four independent symbolic verifications, each written from scratch in sympy
and mpmath without the repository's code.

| Files | Class | Checks |
|---|---|---|
| `v1_flat_slice_class.*` | Flat slices with lapse and shift (class C0) | 134 |
| `v2_spherical_class.*` | Spherical warped products | 170 |
| `v3_moving_patterns.*` | Stationary pattern frames, horizons, overtaken light | 75 |
| `v4_source_physics.*` | Quantum inequalities, Casimir, anomaly, source laws | 192 |

Each `.md` gives, for every identity: its statement with hypotheses, the
method, the result and a derivation sketch. Each `.py` reproduces its checks,
and the logs record the runs.

Further material in this folder:
- `v1_dev/`, `v4_dev/` and `_proto_engine.py` hold development files. The
  ones in `v1_dev/` and `_proto_engine.py` were deleted by their agents
  during a cleanup step and restored from the agents' transcripts; the
  `RESTORED_FROM_TRANSCRIPT.md` notes say how.
- `runs_written_outside_folder/` holds two v4 run logs that were written
  outside the folder.

Reproduction: `python3 verification/v1_flat_slice_class.py`, and likewise
for v2–v4. The four runs take between a few seconds and a few minutes each.

### `inventories/`

Evidence inventories, with every literature citation pinned to a version:

| File | Contents |
|---|---|
| `incidents_may_june.md`, `incidents_september.md` | Events in the project record where a check, result or finding changed a decision, with counterfactuals, lessons and counter-evidence |
| `knobs_one_space.md`, `knobs_throat_era.md` | Part-and-knob response maps: what each design element and parameter moves physically, and whether an identity or a single measurement backs it |
| `lit_foundations.md` | Energy conditions, quantum inequalities, ANEC, semiclassical gravity, causality and topology, 3+1 texts, NEC-violating field theories |
| `lit_design_strategy.md` | Warp, wormhole and shell literature, read for how design choices move the physics |
| `lit_engineering_methods.md` | Verification and validation, transformation optics, design decomposition, readiness scales |
| `coverage_map.md` | The inventories mapped onto a planned textbook structure |

- `drafts/` and `coverage_work/` hold the agents' working drafts and extracts.
- Each inventory with corrections found later carries an errata block at its
  top.

### `synthesis/`

- `02_SYNTHESIS.md`: the corrected synthesis of the inventories. Revision 1
  is kept beside it.
- `audit_synthesis.md`: a claim-by-claim audit of that synthesis and of the
  project findings.
- `04_PROJECT_FINDINGS.md`: the findings for this repository, with the
  earlier version kept as `_rev0`.
- `vetting/`: a full vetting record of one engineering practice.
- `00_`–`05_`: the textbook planning documents.

### `bibliography/`

- `references.bib`: 381 entries, validated with biber. Each carries a
  verification status: 127 read in full, 179 checked at abstract level, 63
  with metadata only, 12 unverified.
- `citation_index.tsv` and `BIB_NOTES.md`: the key index, version hazards
  and corrections.
- `build/`: the scripts and summaries that assembled it.

### `tools/`

Small scripts used during planning.

### `local_archive/` (not in git)

Downloaded paper texts, PDFs and OCR output, raw metadata caches, test builds,
and the superseded LaTeX scaffold. They stay on the Project Space drive and
are excluded from the public repository.
