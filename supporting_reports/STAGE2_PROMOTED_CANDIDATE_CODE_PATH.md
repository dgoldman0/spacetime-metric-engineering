# Stage II Promoted Candidate Code Path

## Purpose

This note records the code path for turning the compact wide4 Stage I result into the first provisional Stage II source-family screen.

The promoted Stage II pair is:

```text
compact7_wide4_edge160
wide4_radius205
```

The first is the compact handoff target. The second is the radius-broadened comparator that checks whether the source family prefers broader support geometry.

## Disk Placement

The root filesystem is tight enough that report-grade Stage II runs should not default to the repo-local `runs/` directory for heavy sweeps:

```text
/dev/nvme0n1p7 mounted on /: about 19G available
```

The large mounted volume is:

```text
/media/kir/9CDCBD3EDCBD140C
/dev/nvme1n1p1: about 123G available
```

Recommended run root:

```text
/media/kir/9CDCBD3EDCBD140C/Research/active_rail_stage2_runs
```

The scripts accept absolute `--outdir` paths, so no symlink is required. A symlink from `toolkit/adm_harness_cli/runs/stage2_*` to the mounted volume can be added later if desired.

## New Code

The Stage II path adds:

```text
toolkit/adm_harness_cli/adm_harness/scalar_source_screen.py
toolkit/adm_harness_cli/scripts/run_scalar_source_screen.py
toolkit/adm_harness_cli/scripts/run_stage2_candidate_ledgers.py
toolkit/adm_harness_cli/specs/stage2_promoted_candidates.json
```

`run_stage2_candidate_ledgers.py` replays selected smooth-split specs into full `source_ledger_*` directories. This is needed because the compact handoff Stage I screens wrote summaries and top bad points, but not full per-candidate point ledgers.

`run_scalar_source_screen.py` consumes one or more full source-ledger directories and runs a reduced Barceló-Visser-like scalar compatibility screen. It scans simple scalar profiles, amplitudes, and nonminimal coupling values, then reports:

```text
channel residual proxies
coverage proxies
live packet scalar-stress contamination
max |phi|
gradient and second-derivative proxies
effective-coupling-margin warning proxy
```

This is not a scalar-tensor proof or a full matter solve. It is the first source-family compatibility discriminator.

## Report-Grade Commands

Create a run root on the large volume:

```bash
mkdir -p /media/kir/9CDCBD3EDCBD140C/Research/active_rail_stage2_runs
```

Generate full Stage II candidate ledgers:

```bash
python toolkit/adm_harness_cli/scripts/run_stage2_candidate_ledgers.py \
  --source-ledger-dir toolkit/adm_harness_cli/runs/stage1_v5_two_feature_radial_current_ledger \
  --spec-file toolkit/adm_harness_cli/specs/stage2_promoted_candidates.json \
  --outdir /media/kir/9CDCBD3EDCBD140C/Research/active_rail_stage2_runs/stage2_promoted_candidate_ledgers_61x83 \
  --ns 61 \
  --nl 83 \
  --s-min -0.96 \
  --s-max 1.65 \
  --l-min -2.80 \
  --l-max 2.80 \
  --force
```

Run the first reduced scalar-source screen:

```bash
python toolkit/adm_harness_cli/scripts/run_scalar_source_screen.py \
  --ledger-dir /media/kir/9CDCBD3EDCBD140C/Research/active_rail_stage2_runs/stage2_promoted_candidate_ledgers_61x83/compact7_wide4_edge160 \
  --label compact7_wide4_edge160 \
  --ledger-dir /media/kir/9CDCBD3EDCBD140C/Research/active_rail_stage2_runs/stage2_promoted_candidate_ledgers_61x83/wide4_radius205 \
  --label wide4_radius205 \
  --outdir /media/kir/9CDCBD3EDCBD140C/Research/active_rail_stage2_runs/stage2_scalar_source_screen_61x83 \
  --profiles standing_support,carved_support,compact_handoff,core_throat,support_edge,catch_support,packet_exclusion \
  --phi0-values 0.025,0.05,0.1,0.2,0.5,1,2 \
  --xi-values 0,0.0833333333,0.1666666667,0.3333333333,0.5,1,2 \
  --top-n 12
```

Outputs:

```text
scalar_source_screen_candidates.csv
scalar_source_screen_summary.csv
scalar_source_screen_top_candidates.csv
scalar_source_screen_manifest.json
```

## Interpretation

A useful first pass is not a low residual by itself. It should have:

```text
low or moderate mean residual;
nontrivial coverage of neg_Tkk_radial, abs_j_l, abs_pOmega, and abs_p_l proxies;
low scalar live-stress fraction;
no |phi| > 1 warning for the best low-residual rows;
no effective-coupling-margin collapse.
```

If the compact target wins with acceptable warnings, Stage II should refine that scalar ansatz around compact support. If `wide4_radius205` wins, the source family is probably asking for broader support even though Stage I preferred compact live-channel behavior.
