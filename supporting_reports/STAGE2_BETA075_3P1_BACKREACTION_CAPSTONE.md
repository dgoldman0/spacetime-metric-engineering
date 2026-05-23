# Stage II Beta075 Light 3+1 Backreaction Proxy

## Status

Status: `stage2_3p1_backreaction_capstone_watch_pass`.

Scope correction: this report is now classified as a light local
off-axis/backreaction proxy, not the final local-compute Stage II capstone. The
moderate sealed-V5 capstone is recorded separately in
`supporting_reports/STAGE2_BETA075_MODERATE_3P1_V5_CAPSTONE.md`. This proxy
remains useful because it was the first partition-backed Parquet off-axis and
metric-feedback stress, but its computational size and lack of explicit
angular/time evolution are too small for it to carry the capstone claim by
itself.

This light proxy lifts the hard-clean first-order 3+1 handoff into a small
scenario catalog of off-axis
and metric-feedback stresses. It keeps the run disciplined: three complete
surfaces, five stress scenarios, summary-first outputs, and Parquet for the
heavy point-response artifacts.

The result is hard-clean. There are zero hard failures. The watches are the
same inherited margin constants already known before this rung: thin boost /
cone margin, reset-sector P/F closure, and the energy theorem utilization.
The proxy does not create a new source-law, support-reservoir, live-support,
or off-mask failure.

This report is manually written from structured outputs. The harness writes
CSV/JSON summaries plus Parquet point tables; it does not generate narrative
report prose.

## Machine Output

Structured output:

`toolkit/adm_harness_cli/runs/stage2_external/stage2_beta075_3p1_backreaction_capstone/`

Rows:

- scenario catalog: `5`
- scenario summary: `15`
- surface stability: `15`
- classification gates: `9`
- point response: `331505` Parquet rows
- top constraint drivers: `1200` Parquet rows
- decision rows: `1`

Storage:

- heavy point response: `beta075_3p1_backreaction_point_response.parquet`
- top drivers: `beta075_3p1_backreaction_top_constraint_drivers.parquet`
- total capstone artifact size: about `25M`

The run was written through the existing `runs/stage2_external` symlink, so it
remains part of the `runs` provenance tree while living on the external
partition.

## Decision

```text
capstone_status: stage2_3p1_backreaction_capstone_watch_pass
hard_capstone_pass: true
failed_gate_count: 0
watch_count: 3
surface_count: 3
scenario_count: 5
```

Worst capstone case:

```text
worst active driver surface:   lower_service_dense_v2
worst active driver scenario:  combined_offaxis_feedback
worst active driver ratio:     0.492946535 / 0.55
worst cone surface:            sealed_dense_v5
worst cone scenario:           combined_offaxis_feedback
minimum cone-margin proxy:     0.010296510
max off-axis angular fraction: 0.045 / 0.12
```

## Scenario Catalog

The capstone applies five local-compute scenarios:

| scenario | mode | read |
| --- | ---: | --- |
| `axisymmetric_reference` | `0` | base first-order handoff |
| `m1_tilt_response` | `1` | dipole-like off-axis tilt with mild feedback |
| `m2_shear_response` | `2` | quadrupole-like shear response |
| `reset_sector_feedback` | `0` | axisymmetric reset-sector geometric feedback |
| `combined_offaxis_feedback` | `2` | combined off-axis and metric-feedback stress |

These are not a full dynamical Einstein-matter solve. They are the strongest
local-compute stress layer we can reasonably add on this machine before moving
to external compute: perturb the first-order handoff in the directions most
likely to expose source-conservation, cone, angular, live-support, or
reset-sector failures.

## Gate Summary

| gate | status | value |
| --- | --- | ---: |
| first-order 3+1 handoff | pass | inherited watch-pass |
| active driver bound | pass | `0.492946535 / 0.55` |
| cone-margin proxy | watch | `0.010296510` |
| off-axis angular driver | pass | `0.045 / 0.12` |
| live/off-mask localization | pass | live `0.003873`, outside `0.001130` |
| reset-sector P/F margin | watch | `0.544566954 / 0.55` |
| adjacent dense stability | pass | `0.000897381 / 0.03` |
| energy constant buffer | watch | utilization `0.819620378` |
| surface scope | pass | `3` surfaces |

The live/off-mask gate uses the same full-endpoint denominator convention as
the inherited total-closure gate. Under that accounting, the combined scenario
stays below live and off-mask limits with comfortable enough separation for
this rung.

## Surface And Scenario Read

The combined off-axis/feedback scenario is the worst active-driver case:

| surface | active driver / endpoint | driver / source abs | live fraction | outside fraction |
| --- | ---: | ---: | ---: | ---: |
| sealed baseline V5 | `0.267055` | `0.040266` | `0.003873` | `0.001130` |
| sealed dense V5 | `0.492049` | `0.080687` | `0.003487` | `0.000950` |
| lower-service dense V2 | `0.492947` | `0.081939` | `0.003518` | `0.000753` |

The lower-service dense V2 surface remains stable against sealed dense V5. Its
worst active-driver delta is `0.000897381`, far below the `0.03` drift gate.
The cone proxy is essentially identical across dense V5 and dense V2 at the
same scenario.

## Driver Location

The top combined-scenario drivers remain in:

```text
reset_decompression_endpoint_junction / reset_decompression / support_edge
```

The strongest lower-service dense V2 point is at:

```text
s = 1.922872, l = -1.60
scenario_driver_l2_density = 0.209746
scenario_driver_l2_volume  = 0.004972
```

The thinnest cone-margin proxy occurs at:

```text
sealed_dense_v5
combined_offaxis_feedback
s = 2.537234, l = 2.00
reset_decompression / support_edge
cone-margin proxy = 0.010296510
```

That location is exactly the known reset-sector support-edge watch. The stress
does not migrate into packet-live support, does not require angular exchange,
and does not create an unrelated off-mask driver. That is the central physical
read of this light proxy.

## Interpretation

The light local 3+1/backreaction proxy passed. The result does not prove a
final Einstein-matter theorem, and by itself it no longer carries the
local-compute capstone claim. Its role is narrower: it showed that the first
off-axis/metric-feedback stress layer did not point back to a component repair
or create live/off-mask leakage before the project moved to an explicitly
angular/time-evolved capstone.

The moderate sealed-V5 capstone now supplies the stronger local-compute read.
Use that later report for the Stage II closeout interpretation.

## Claim Boundary

Included:

- light local 3+1/backreaction proxy stress;
- off-axis and metric-feedback scenario stress;
- Parquet point-response artifacts;
- cross-surface baseline/dense/lower-service stability;
- live/off-mask/angular/cone/source-conservation gates.

Excluded:

- full dynamical Einstein-matter evolution;
- global 3+1 theorem;
- final matter action;
- broad external-compute parameter sweep;
- final academic proof of physical realization.

## Current Read

This proxy supports the Stage II progression but is not the final local read.
The stronger current claim is made only after the moderate sealed-V5 capstone:

```text
The light off-axis/backreaction proxy did not uncover a component-level
obstruction and justified proceeding to the moderate sealed-V5 3+1 capstone.
```

The capstone-level conclusion is recorded in
`supporting_reports/STAGE2_BETA075_MODERATE_3P1_V5_CAPSTONE.md`.
