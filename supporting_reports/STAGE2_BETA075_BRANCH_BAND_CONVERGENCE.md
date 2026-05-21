# Stage II Beta075 Branch-Band Convergence Check

Date: 2026-05-21

## Purpose

This report records the narrow convergence rung requested after the refined
beta075 core horizon-escape test. The aim was not to run another broad variant
sweep. It was to keep the promoted beta075 `p003_mid` mechanism fixed, increase
targeted seed density around the live packet/carrier/branch-band masks, and ask
whether the same separation persists:

```text
Local branch crossing remains present, but packet/carrier/branch-band null
families still escape.
```

## Inputs

Promoted refined ledger:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/ledgers/horizon_escape_beta075_p003_mid/source_ledger_point_ledger.csv
```

Fixed grid and mechanism:

```text
mechanism: beta075 p003_mid negative-l receiver
grid: 121 x 121
s: -1.5 .. 9.0
l: -6.0 .. 6.0
```

Seed-density outputs:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/escape_ladder_core_masks_seed30/
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/escape_ladder_core_masks_seed60/
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/escape_ladder_core_masks_seed120/
```

GZ obstruction screen:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/gz_obstruction/
```

The tested core masks were:

```text
packet_live
packet_geom
main_carrier
support_plant
branch_band_live
```

Each selected seed was traced in both radial null branches.

## Branch Crossing Still Exists

The refined GZ obstruction screen remains adverse:

```text
status: fail
reason: live packet branch-zero crossing edge; active interpolation branch-zero
crossing edge; top shell/throat-overlap branch-zero crossing edge
```

The relevant local branch numbers are unchanged in the convergence rung:

| scope | rows | min branch margin | branch-crossing edges | gtt >= 0 points | max GZ overlap |
| --- | ---: | ---: | ---: | ---: | ---: |
| `live_packet` | 237 | 0.002402 | 45 | 98 | 245.010006 |
| `active_interpolation` | 8580 | 0.002402 | 64 | 121 | 245.010006 |
| `top_gz_overlap_decile` | 1452 | 0.002402 | 64 | 121 | 245.010006 |

So the favorable escape results below are not caused by the branch diagnostic
disappearing.

## Seed-Density Results

| rung | scope | traces | expected escapes | s-upper unresolved | branch sign changes | min branch margin |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| seed30 | `packet_live` | 60 | 60 | 0 | 26 | 0.002402 |
| seed30 | `packet_geom` | 60 | 60 | 0 | 27 | 0.002402 |
| seed30 | `main_carrier` | 60 | 60 | 0 | 25 | 0.002402 |
| seed30 | `support_plant` | 60 | 60 | 0 | 25 | 0.002402 |
| seed30 | `branch_band_live` | 60 | 60 | 0 | 26 | 0.002402 |
| seed60 | `packet_live` | 120 | 120 | 0 | 46 | 0.002402 |
| seed60 | `packet_geom` | 120 | 114 | 6 | 42 | 0.002402 |
| seed60 | `main_carrier` | 120 | 120 | 0 | 42 | 0.002402 |
| seed60 | `support_plant` | 120 | 120 | 0 | 42 | 0.002402 |
| seed60 | `branch_band_live` | 96 | 96 | 0 | 38 | 0.002402 |
| seed120 | `packet_live` | 240 | 240 | 0 | 91 | 0.002402 |
| seed120 | `packet_geom` | 240 | 196 | 44 | 58 | 0.002402 |
| seed120 | `main_carrier` | 240 | 240 | 0 | 48 | 0.002402 |
| seed120 | `support_plant` | 240 | 240 | 0 | 48 | 0.002402 |
| seed120 | `branch_band_live` | 96 | 96 | 0 | 38 | 0.002402 |

`branch_band_live` saturates at seed60/seed120 because the refined branch-band
mask contains only 48 unique seed rows. Both null branches were traced for all
available branch-band seeds.

## Reset-Decompression Tail

The only unresolved traces introduced by the denser rungs are in `packet_geom`
minus-branch seeds. At seed120, all 44 unresolved traces are:

```text
scope: packet_geom
branch: minus
stage: reset_decompression
inside_packet_live: false
inside_packet_geom: true
regions: packet_in_support (12), packet_outer (32)
```

They start at:

```text
s: 1.65 .. 2.2625
l: 1.3 .. 2.4
```

and terminate at the future domain boundary with:

```text
final s: 9.0
final l: -5.942194 .. -4.509300
branch sign changes: 0
```

This is not a live branch-band reversal. It is a finite-domain
reset-decompression/wake-tail ambiguity in the geometric packet mask.

## Decision

The narrow convergence rung passes for the intended branch-band question:

```text
The local branch-crossing channel persists, but live packet, main carrier,
support plant, and live branch-band null families still escape under increased
targeted seed density.
```

The result supports moving to a scheduled ADM evolution audit with prescribed
metric fields, not to full dynamical Einstein evolution. The red tag that must
carry forward is:

```text
Release/wake tail closure remains open. Monitor reset-decompression packet_geom
minus-branch tails explicitly in the scheduled ADM probe evolution.
```

The next audit tier should prescribe the metric fields
`alpha(sigma,l)`, `beta(sigma,l)`, `gamma_ll(sigma,l)`, and
`gamma_Omega(sigma,l)` from the promoted beta075 service program, then evolve
probe families through that scheduled geometry: packet centerlines, tube edges,
radial null rays, off-axis null samples, and a small congruence bundle. The
required monitors are packet norm, causal reachability, null-expansion proxies,
source-channel changes, and the reset-decompression wake-tail channel above.
