# Stage II Scheduled ADM Confidence Run

Date: 2026-05-21

## Purpose

This report records the staged confidence run after the beta075 branch-band
convergence check and the first scheduled ADM probe pilot. The goal was to make
the remaining release/wake red tag interpretable, not to run another design
variant sweep.

The fixed target is the promoted beta075 `p003_mid` negative-l receiver. The
question is:

```text
If the future domain is extended, do reset-decompression packet-geometry
minus-tail probes clear, remain exterior, re-enter live service, or form a new
obstruction pattern?
```

## Ledgers

All runs keep the same mechanism and `l = +/-6.0` radial domain.

| label | grid | s domain | rows | ledger build time | positive live packet norm |
| --- | --- | --- | ---: | ---: | ---: |
| refined core | `121 x 121` | `-1.5 .. 9.0` | 14641 | 1135.375 s | 0 |
| s12 confidence | `155 x 121` | `-1.5 .. 12.0` | 18755 | 1462.952 s | 0 |
| s15 confidence | `189 x 121` | `-1.5 .. 15.0` | 22869 | 1833.512 s | 0 |

The extended ledgers are:

```text
toolkit/adm_harness_cli/runs/scheduled_adm_confidence_beta075_s12_155x121/
toolkit/adm_harness_cli/runs/scheduled_adm_confidence_beta075_s15_189x121/
```

## Branch Diagnostic

The local GZ-style branch diagnostic remains adverse on the extended ledgers.

| rung | status | live rows | min live branch margin | live branch-crossing edges | active interpolation branch-crossing edges |
| --- | --- | ---: | ---: | ---: | ---: |
| s9 | fail | 237 | 0.002402 | 45 | 64 |
| s12 | fail | 238 | 0.003845 | 43 | 64 |
| s15 | fail | 238 | 0.004569 | 45 | 64 |

This preserves the important separation: the favorable escape results are not
coming from disappearance of the branch-crossing channel.

## Core Radial Escape

The seed120 core-mask radial escape rung improved from the original `s=9`
ambiguity to clean escape on the extended domains.

| rung | total traces | radial escapes | future-boundary unresolved | packet_geom minus unresolved |
| --- | ---: | ---: | ---: | ---: |
| s9 seed120 | 1056 | 1012 | 44 | 44 |
| s12 seed120 | 1056 | 1056 | 0 | 0 |
| s15 seed120 | 1056 | 1056 | 0 | 0 |

At both `s12` and `s15`, `packet_live`, `packet_geom`, `main_carrier`,
`support_plant`, and `branch_band_live` all escape on both radial branches.
The branch-band minus family still crosses the branch-sensitive region and
escapes lower.

## Scheduled ADM Probe Audit

The stricter scheduled ADM audit also improves monotonically. It prescribes
the beta075 `p003_mid` metric fields and evolves packet centerline, packet
tube-edge, branch-band radial null, off-axis null, congruence, and explicit
reset-tail red-tag probes.

| rung | branch-band radial/off-axis/congruence | packet centerline | packet tube edge | red-tag lower escapes | red-tag future-boundary unresolved | live re-entry in red tag |
| --- | --- | --- | --- | ---: | ---: | ---: |
| s9 | clean | `0/24` radial, `24/24` future | `13/24` radial, `11/24` future | 0 / 41 | 41 / 41 | 0 |
| s12 | clean | `2/24` radial, `22/24` future | `24/24` radial | 13 / 41 | 28 / 41 | 0 |
| s15 | clean | `24/24` radial | `24/24` radial | 30 / 41 | 11 / 41 | 0 |

The remaining `s15` red-tag unresolved traces are all:

```text
trace_outcome: s_upper_boundary
final_region: far_exterior
entered_live_packet: false
seed_region: packet_outer
final s: 15.0
final l: -5.868617 .. -3.490957
min branch margin along trace: 1.0
min packet norm along trace: -0.75
```

This is a strong trend toward wake-tail domain closure. It is not complete
closure yet, because 11 of 41 red-tag traces remain future-boundary unresolved
at `s_max = 15.0`.

## Current Interpretation

The confidence state has moved materially:

```text
Live-service radial trapping is not observed.
Branch crossing persists locally.
Core packet/carrier/branch-band null families escape on the extended domains.
Scheduled branch-band radial, off-axis, and congruence probes escape.
The red-tag reset tail is clearing with future-domain extension and remains
outside live service, but 11 exterior tail probes are still unresolved at s15.
```

This supports high confidence in the prescribed-ADM statement:

```text
The promoted beta075 p003_mid service program does not show live-service
radial trapping under the tested prescribed-metric probes.
```

It does not yet support a proof-level global horizon or trapped-surface claim.
The remaining open item is late exterior wake-tail closure, not branch-band
live-service obstruction.

## Next Decision

An `s18` closure rung is justified only if the immediate goal is to close the
last 11 exterior reset-tail probes outright. The staged trend suggests they may
clear with additional future time, but the present result is already enough to
change direction toward:

```text
1. dedicated null-expansion/trapped-surface proxy around packet/carrier/sheath,
2. source-closure/conservation audit for the prescribed service program,
3. optional s18 wake-tail closure if a report-grade tail-closure sentence is
   needed before those higher-tier diagnostics.
```

The recommendation is to stop broad future-domain extension unless a clean
tail-closure sentence is required. If it is required, run one more `s18` rung
and then stop extending unless the remaining probes reverse trend or re-enter
the live packet.
