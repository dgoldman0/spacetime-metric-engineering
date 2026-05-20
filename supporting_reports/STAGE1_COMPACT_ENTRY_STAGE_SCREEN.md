# Stage I Compact Entry-Stage Screen

## Purpose

The extended-domain hard-affine SNEC adjudication showed that the compact
wide4 target's broad-window SNEC issue was a boundary artifact, but it exposed
two positive live packet-norm points at the newly included early-entry edge.
This screen tests whether that is evidence for a missing live-entry service
stage rather than another catch/rematch or `p_l` tuning problem.

## Harness Update

The source-ledger parameters now include an optional default-off live packet
entry gate:

```text
live_packet_start
```

When unset, historical ledgers keep their old semantics. When set, points with
`s < live_packet_start` are classified as:

```text
pre_entry_setup
```

and are excluded from live packet accounting. This lets extended-domain screens
separate prepared entry infrastructure from live passenger exposure.

The generic source-screen runner also now emits a per-candidate heartbeat:

```text
{"event": "screen_case_start", ...}
```

and appends `elapsed_s` to each completed row.

## Runs

Extended high-resolution confirmation, stopped after the baseline and first
entry-start case:

```text
toolkit/adm_harness_cli/runs/stage1_v5_compact_entry_stage_screen_extended_101x151/
```

Coarse extended-domain discriminator:

```text
toolkit/adm_harness_cli/runs/stage1_v5_compact_entry_stage_screen_extended_41x61/
toolkit/adm_harness_cli/runs/stage1_v5_compact_entry_stage_screen_extended_41x61_remainder/
toolkit/adm_harness_cli/runs/stage1_v5_compact_entry_stage_screen_extended_41x61_pressure_tail/
```

Spec file:

```text
toolkit/adm_harness_cli/specs/compact_entry_stage_screen.json
```

## High-Resolution Confirmation

At `101 x 151` on the extended domain `s in [-1.50, 2.40]`,
`l in [-4.20, 4.20]`:

| case | live start | positive live packet norm | max live packet norm | live Tkk | live p_l | live j_l | live pOmega |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `wide4_no_start` | unset | 2 | 1.6255 | 15.9390 | 0.6830 | 0.1023 | 2.1339 |
| `wide4_start_m1p40` | -1.40 | 0 | -1.2424 | 13.9779 | 0.6244 | 0.0885 | 1.6853 |

This is the main result. The early-entry packet-norm positives disappear when
the service model distinguishes pre-entry setup from live passenger exposure.
The live burden also drops because the newly exposed boundary cells are no
longer charged to the passenger worldtube.

## Coarse Discriminator

At `41 x 61` on the same extended domain:

| case | live start | entry carve | entry width | live Tkk | live p_l | live j_l | live pOmega | Tkk peak | pOmega peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `wide4_no_start` | unset | 0.75 | 4.8 | 16.4289 | 0.6904 | 0.1052 | 2.5194 | 0.9393 | 0.8880 |
| `wide4_start_m1p40` | -1.40 | 0.75 | 4.8 | 13.2838 | 0.6016 | 0.0832 | 1.5827 | 0.9393 | 0.8880 |
| `wide4_start_m1p36` | -1.36 | 0.75 | 4.8 | 13.2838 | 0.6016 | 0.0832 | 1.5827 | 0.9393 | 0.8880 |
| `wide4_start_m1p32` | -1.32 | 0.75 | 4.8 | 13.2838 | 0.6016 | 0.0832 | 1.5827 | 0.9393 | 0.8880 |
| `wide4_start_m1p28` | -1.28 | 0.75 | 4.8 | 11.7766 | 0.5543 | 0.0751 | 1.5030 | 0.9393 | 0.8880 |
| `wide4_start_m1p36_w42` | -1.36 | 0.75 | 4.2 | 13.0635 | 0.5479 | 0.0995 | 1.9594 | 1.0942 | 0.9948 |
| `wide4_start_m1p40_e080` | -1.40 | 0.80 | 4.8 | 12.3689 | 0.4992 | 0.1285 | 2.2289 | 1.4022 | 1.1816 |
| `wide4_start_m1p36_e080_w54` | -1.36 | 0.80 | 5.4 | 12.4810 | 0.5366 | 0.1054 | 1.8327 | 1.2391 | 1.0723 |

All entry-start cases had zero positive live packet-norm points on this coarse
extended screen.

## Interpretation

The cleanest move is not stronger entry pressure-hold. It is an explicit
service-stage separation:

```text
pre-entry setup / pressure preparation
-> live packet entry
-> compact catch/rematch handoff
```

Narrower or stronger entry controls do reduce live `p_l`, but they immediately
charge the same channels the compact wide4 handoff was protecting:

```text
entry width 4.2: lower p_l, higher j_l/pOmega, higher Tkk/pOmega peaks
entry carve 0.80: lower p_l, much higher j_l/pOmega and point peaks
```

So the pressure-hold idea is real, but the naive version is too blunt. The
entry stage should first be represented as service choreography/accounting and
then, if needed, as a derivative-limited pressure-preparation component that
does not disturb the compact handoff.

## Next Step

Carry `live_packet_start = -1.40` as the first explicit-entry comparator and
rerun the compact source/component/SNEC chain on that accounting. If a geometry
change is still needed after that, do not simply increase entry carve; build a
separate pressure-preparation profile with its own derivative cap and reject it
unless it preserves the wide4 `j_l`, `pOmega`, and point-peak gains.
