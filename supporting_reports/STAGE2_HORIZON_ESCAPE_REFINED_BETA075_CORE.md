# Stage II Refined Beta075 Horizon Escape Core Test

Date: 2026-05-21

## Purpose

This run narrows the horizon/physics-wall question to the promoted mechanism:
beta075 `p003_mid`. Instead of testing more beta100/design variants, it refines
the long-tail beta075 domain, increases seed coverage for the live packet and
carrier masks, and asks whether the live branch-band escape result survives
closer sampling of the local GZ-like branch region.

The intent is deliberately modest and sharp:

```text
If the promoted beta075 mechanism fails refined live-service escape, then the
local GZ-like behavior may be a real physics wall.

If it survives, beta100 can wait for a robustness section.
```

## Inputs

Refined beta075 ledger:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/ledgers/horizon_escape_beta075_p003_mid/
```

Grid:

```text
s: -1.5 .. 9.0
l: -6.0 .. 6.0
grid: 121 x 121
rows: 14641
```

Escape output:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/escape_ladder_core_masks_seed30/
```

Refined local GZ screen:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/gz_obstruction/
```

## Branch Band Target

The previous long-tail beta075 pilot put the live branch band roughly in:

```text
s: -1.125 .. 0.125
l: -0.878 .. 0.293
region: packet_in_support
```

The refined ledger samples the live band more sharply. The refined live packet
has:

```text
live rows: 237
positive live packet-norm samples: 0
live extent:
  s: -1.325 .. 1.5625
  l: -1.6 .. 1.9
```

The refined live branch-band q20 subset has:

```text
branch-band rows: 48
q20 margin cutoff: 0.709174
branch-band extent:
  s: -1.325 .. 0.1625
  l: -1.0 .. 0.3
stages:
  catch_rematch: 39
  entry_precatch: 9
min branch margin: 0.002402
median branch margin: 0.330271
max branch margin: 0.706465
```

So this refinement did not move away from the dangerous local channel. It found
an even tighter sampled branch margin than the earlier long-tail pilot.

## Refined Local GZ Screen

The local GZ obstruction decision still fails:

```text
status: fail
reason: live packet branch-zero crossing edge; active interpolation branch-zero
crossing edge; top shell/throat-overlap branch-zero crossing edge
```

Key refined GZ numbers:

| scope | rows | min branch abs margin | branch crossing edges | gtt >= 0 points | max GZ overlap |
| --- | ---: | ---: | ---: | ---: | ---: |
| `live_packet` | 237 | 0.002402 | 45 | 98 | 245.010 |
| `active_interpolation` | 8580 | 0.002402 | 64 | 121 | 245.010 |
| `top_gz_overlap_decile` | 1452 | 0.002402 | 64 | 121 | 245.010 |

This preserves the important contrast: the local branch diagnostic remains
adverse. Any favorable escape result is not coming from the branch issue
disappearing under refinement.

## High-Coverage Core Escape Result

The escape ladder was rerun only on the core masks:

```text
packet_live
packet_geom
main_carrier
support_plant
branch_band_live
```

with `30` seeds per mask. Each seed was traced in both radial null branches,
for `300` total traces.

Summary:

```text
radial escapes: 300
s_upper_boundary unresolved traces: 0
invalid/stalled traces: 0
```

Per-mask result:

| seed scope | branch | traces | expected escapes | unresolved |
| --- | --- | ---: | ---: | ---: |
| `packet_live` | plus | 30 | 30 | 0 |
| `packet_live` | minus | 30 | 30 | 0 |
| `packet_geom` | plus | 30 | 30 | 0 |
| `packet_geom` | minus | 30 | 30 | 0 |
| `main_carrier` | plus | 30 | 30 | 0 |
| `main_carrier` | minus | 30 | 30 | 0 |
| `support_plant` | plus | 30 | 30 | 0 |
| `support_plant` | minus | 30 | 30 | 0 |
| `branch_band_live` | plus | 30 | 30 | 0 |
| `branch_band_live` | minus | 30 | 30 | 0 |

The plus traces exited through `l_upper_boundary`. The minus traces exited
through `l_lower_boundary`.

The minimum branch margin encountered along the refined escape traces was
`0.002402`, and the minus families accumulated branch sign changes:

| seed scope | minus branch sign changes | min trace margin |
| --- | ---: | ---: |
| `packet_live` | 26 | 0.002402 |
| `packet_geom` | 27 | 0.002402 |
| `main_carrier` | 25 | 0.002402 |
| `support_plant` | 25 | 0.002402 |
| `branch_band_live` | 26 | 0.002402 |

That is the key physical read: the traces are not merely avoiding the branch
band. The minus branch crosses the branch-sensitive region and still reaches the
lower exterior boundary.

## Interpretation

This is the strongest horizon-ladder result so far. The promoted beta075
`p003_mid` mechanism remains live-clean, still fails the local GZ branch screen,
and nevertheless shows complete radial escape for high-coverage packet,
carrier, support, and live branch-band seeds on the refined long-tail domain.

The evidence now supports:

```text
The local GZ-like branch signature survives refinement, but it does not become
live-service radial trapping in the promoted beta075 p003_mid mechanism.
```

This does not prove full global event-horizon freedom. It does strongly weaken
the immediate "GZ-like no-go wall" concern for the promoted design, because the
core live-service masks escape even when the sampled branch margin tightens to
`0.002402`.

The right next step is not a design-family sweep. It is a local convergence
rung: refine around the live branch band or increase targeted seed density
again, then consider angular/null-expansion diagnostics only after the radial
escape verdict is stable.

## Current Decision

Do not run beta100 stress variants as part of deciding whether beta075 has a
fundamental physics wall. Beta100 can be added later as robustness context. The
core beta075 result is already the relevant promoted-mechanism test, and it is
favorable.
