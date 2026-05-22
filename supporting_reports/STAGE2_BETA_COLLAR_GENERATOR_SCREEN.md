# Stage II Beta-Collar Generator Screen

Date: 2026-05-21

## Purpose

This report records the first tensor-consistent follow-up to the finite
minus-branch carrier-focus collar mitigation screen. The previous screen showed
that prescribed-metric beta-collar softening could relieve adverse
caustic-like compression with later escape, but its saved candidate ledgers
were observation artifacts rather than regenerated demanded-source ledgers.

This rung regenerates the source ledger from the metric generator after
retuning the existing packet beta-rematch family. The Einstein-tensor/source
columns therefore see the modified beta geometry directly.

## Diagnostic

New manifest-driven runner:

```text
toolkit/adm_harness_cli/scripts/run_beta_collar_generator_screen.py
```

Input baseline:

```text
toolkit/adm_harness_cli/runs/scheduled_adm_confidence_beta075_s15_189x121/ledgers/horizon_escape_beta075_p003_mid/source_ledger_manifest.json
```

First generated candidate:

```text
label: rematch_w6_t1p5
shape: trailing_edge
gain: 1.8
width multiplier: 6.0
temporal width multiplier: 1.5
center floor: 0.6
grid: s15, 189 x 121
```

Second bracket candidate:

```text
label: rematch_w8_t2p0
shape: trailing_edge
gain: 1.8
width multiplier: 8.0
temporal width multiplier: 2.0
center floor: 0.6
grid: s15, 189 x 121
```

Output ledgers and audits:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/ledgers/rematch_w6_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/ledgers/rematch_w8_t2p0/
toolkit/adm_harness_cli/runs/trace_expansion_beta_collar_generator_rematch_w6_t1p5_s15/
toolkit/adm_harness_cli/runs/trace_expansion_beta_collar_generator_rematch_w8_t2p0_s15/
toolkit/adm_harness_cli/runs/dense_congruence_beta_collar_generator_rematch_w6_t1p5_s15/
toolkit/adm_harness_cli/runs/dense_congruence_beta_collar_generator_rematch_w8_t2p0_s15/
```

## Result

The first tensor-consistent beta-collar candidates clear the dense finite-bundle
gate that blocked promotion of the previous design.

Packet safety in the regenerated source ledger:

```text
rematch_w6_t1p5:
  rows: 22,869
  live points: 238
  positive live packet-norm rows: 0
  max live packet norm: -9.935129
  min live packet norm: -821.017063

rematch_w8_t2p0:
  rows: 22,869
  live points: 238
  positive live packet-norm rows: 0
  max live packet norm: -6.577702
```

Scheduled trace-expansion audit:

```text
decision: favorable_transient_branch_band_focusing
traces: 235
branch-band traces entering both-shrinking: recover
sustained-to-end both-shrinking traces: 0
```

Dense congruence audit:

```text
rematch_w6_t1p5:
  decision: favorable_dense_bundle_transient_focusing
  dense rays: 136
  dense radial escapes: 136/136
  entered both-shrinking: 136/136
  recovered from both-shrinking: 136/136
  sustained-to-end both-shrinking rays: 0
  caustic-like bundles: 0/8
  worst all-both l-width ratio: 0.275792
  worst all-both areal-width ratio: 0.170374

rematch_w8_t2p0:
  decision: favorable_dense_bundle_transient_focusing
  dense radial escapes: 136/136
  recovered from both-shrinking: 136/136
  sustained-to-end both-shrinking rays: 0
  caustic-like bundles: 0/8
  worst all-both l-width ratio: 0.394689
  worst all-both areal-width ratio: 0.303871
```

Compared with the s15 baseline dense audit, this moves the finite-width result
from adverse caustic-like compression with later escape to favorable dense
bundle transient focusing:

| quantity | baseline s15 | `rematch_w6_t1p5` |
| --- | ---: | ---: |
| dense radial escapes | 136/136 | 136/136 |
| sustained-to-end both-shrinking rays | 0 | 0 |
| caustic-like bundles | 8/8 | 0/8 |
| worst all-both l-width ratio | 0.009603 | 0.275792 |
| worst all-both areal-width ratio | 0.000696 | 0.170374 |
| positive live packet-norm rows | 0 | 0 |

The wider bracket improves the optical width floor further:

| quantity | `rematch_w6_t1p5` | `rematch_w8_t2p0` |
| --- | ---: | ---: |
| caustic-like bundles | 0/8 | 0/8 |
| worst all-both l-width ratio | 0.275792 | 0.394689 |
| worst all-both areal-width ratio | 0.170374 | 0.303871 |
| max live packet norm | -9.935129 | -6.577702 |

The source-accounting movement is not obviously adverse on this first
candidate. Relative to the baseline s15 source ledger, live packet burdens move
as follows:

| channel | live-burden ratio vs baseline | note |
| --- | ---: | --- |
| `neg_Tkk_radial` | 0.852x | lower |
| `abs_p_l` | 0.981x | essentially unchanged/slightly lower |
| `abs_pOmega` | 0.900x | lower |
| `abs_j_l` | 0.718x | lower |
| `neg_rho_euler` | unchanged at zero live burden | clean |
| `neg_rho_packet` | small nonzero live burden, `0.000483` | watch item |

For `rematch_w8_t2p0`, the primary live burden channels improve a little more
than `rematch_w6_t1p5`, but the small live negative packet-density watch item
is larger:

| channel | live-burden ratio vs baseline |
| --- | ---: |
| `neg_Tkk_radial` | 0.819x |
| `abs_p_l` | 0.978x |
| `abs_pOmega` | 0.883x |
| `abs_j_l` | 0.674x |
| `neg_rho_packet` | live burden `0.005930` |

## Interpretation

This is the first report-grade evidence that the finite minus-branch
carrier-focus collar is a tunable rematch feature rather than an invariant
finite-width obstruction. The earlier artifacted beta smoothing was not merely
a postprocessor mirage: generator-level widening of the trailing-edge
beta-rematch collar preserves packet timelikeness, preserves radial escape,
removes the dense caustic-like collapse classification, and does not create an
obvious source-accounting spike in the primary live burden channels.

The bracket has an expected tradeoff. `rematch_w8_t2p0` gives a larger optical
width floor, while `rematch_w6_t1p5` keeps a deeper packet-norm margin and a
smaller negative-packet-density watch item. The conservative lead is therefore
`rematch_w6_t1p5`; the wider bracket is useful evidence that the direction is
robust.

This still does not certify physical viability. It is a prescribed metric and
demanded-source regeneration, not a conservation-closed matter model or a
global horizon theorem. The remaining gates are source-family replacement,
affine SNEC companion checks for the regenerated candidate, robustness across
nearby collar widths/timings, and any full-domain wake/tail follow-up needed
before horizon-freedom wording is strengthened.

## Decision

Promote `rematch_w6_t1p5` as the conservative beta-collar mitigation lead, with
`rematch_w8_t2p0` retained as a wider optical-relief bracket. The next checks
should be companion SNEC/source-accounting audits and a small local robustness
bracket around width and temporal multiplier, not a broad geometry redesign.
