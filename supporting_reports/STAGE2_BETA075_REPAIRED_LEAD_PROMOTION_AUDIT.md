# Stage II Beta075 Repaired Lead Promotion Audit

Date: 2026-05-22

## Summary

The repaired beta075 lead `rematch_w6_t1p5` now has a full promotion-audit
companion package. The audit supports promoting it as the conservative repaired
beta075 test article:

```text
mechanism: beta075 p003_mid negative-l receiver
repair:    rematch_w6_t1p5 trailing-edge beta-collar generator candidate
bracket:   rematch_w8_t2p0, retained as wider optical-relief evidence
```

The result is favorable at the effective-source/prescribed-metric level. The
candidate preserves packet timelikeness, clears the dense finite-bundle
caustic-like classification, lowers the main live source burdens, and passes
full-stride affine-reparameterized SNEC companions in both component-sector and
intermediate S0/J/R modes.

This is still not a physical matter construction, conservation proof,
semiclassical RSET result, or global horizon theorem.

## Artifacts

Generated source ledgers:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/ledgers/rematch_w6_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/ledgers/rematch_w8_t2p0/
```

New audit outputs for `rematch_w6_t1p5`:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/component_rematch_w6_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/string_rematch_w6_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/intermediate_rematch_w6_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/affine_snec_rematch_w6_t1p5_full_tau050_100_200/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/intermediate_snec_rematch_w6_t1p5_full_tau050_100_200/
```

Baseline comparison artifacts:

```text
toolkit/adm_harness_cli/runs/scheduled_adm_confidence_beta075_s15_189x121/ledgers/horizon_escape_beta075_p003_mid/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/component_baseline_s15_beta075_p003_mid/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/string_baseline_s15_beta075_p003_mid/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/intermediate_baseline_s15_beta075_p003_mid/
```

Existing optical/causal companion artifacts:

```text
toolkit/adm_harness_cli/runs/trace_expansion_beta_collar_generator_rematch_w6_t1p5_s15/
toolkit/adm_harness_cli/runs/dense_congruence_beta_collar_generator_rematch_w6_t1p5_s15/
```

## Packet Safety

The regenerated `rematch_w6_t1p5` source ledger is live-clean:

```text
live points:                238
positive live packet norm:  0
max live packet norm:      -9.93512860272052
min live packet norm:    -821.017062555306
```

The wider bracket `rematch_w8_t2p0` is also live-clean, but has a shallower
packet-norm margin and a larger small live negative-packet-density watch item
in the generator report. Keep `rematch_w6_t1p5` as the conservative lead.

## Source Accounting

Relative to the s15 beta075 baseline, `rematch_w6_t1p5` lowers the main total
source-accounting channels except radial pressure, which is essentially flat:

| channel | baseline total | repaired total | repaired / baseline |
| --- | ---: | ---: | ---: |
| `neg_Tkk_radial` | `499.312005` | `482.454247` | `0.966238` |
| `abs_p_l` | `83.148737` | `83.156015` | `1.000088` |
| `abs_pOmega` | `14.560511` | `13.561421` | `0.931384` |
| `abs_j_l` | `0.750255` | `0.726867` | `0.968826` |

The live-channel movement is more clearly favorable:

| channel | baseline live | repaired live | repaired / baseline |
| --- | ---: | ---: | ---: |
| `neg_Tkk_radial` | `14.086144` | `12.008237` | `0.852486` |
| `abs_p_l` | `0.631810` | `0.620064` | `0.981409` |
| `abs_pOmega` | `1.650024` | `1.484949` | `0.899956` |
| `abs_j_l` | `0.092355` | `0.066347` | `0.718394` |

Interpretation: the collar repair is not merely an optical postprocessor
victory. It reduces the dangerous live handoff channels and also lowers the
dominant radial-null infrastructure burden.

## Endpoint J Accounting

The S0/J/R intermediate model remains exactly in the desired live-gate class:

```text
J_endpoint_junction_layer live rows:            0
S0_constant_flux_string_cloud live rows:        0
core_body_residual_leakage live rows:           0
live selected-null deficit in modeled sectors:  0
```

The J-layer movement is mixed but not blocking:

| J assignment | baseline selected-null | repaired selected-null | read |
| --- | ---: | ---: | --- |
| `reset_decompression_endpoint_junction` | `3.695554` | `3.696084` | essentially flat |
| `support_edge_endpoint_junction` | `0.615485` | `0.642179` | small adverse shoulder transfer |

The support-edge shoulder selected-null increase is the main watch item. It is
not accompanied by live leakage, and it comes with a large support-edge angular
drop:

```text
support-edge angular burden: 1.976812 -> 1.463343
support-edge current burden: 0.109295 -> 0.115340
support-edge pair L1:        0.455282 -> 0.449438
```

Interpretation: the repair redistributes endpoint burden inside J rather than
simply hiding cost in the live packet. The next robustness bracket should track
support-edge selected-null explicitly.

## Full-Stride Affine SNEC

The component-sector affine-reparameterized SNEC companion scanned:

```text
windows:        137,064
widths:         0.5, 1.0, 2.0
center stride:  1
mode:           sector_sum
parameter:      affine
```

It found:

```text
all-window benchmark-floor violations: 0
scoreable benchmark-floor violations:  0
```

Worst scoreable margins:

| branch | width | worst margin | worst center | region | live? | dominant negative sector |
| --- | ---: | ---: | --- | --- | --- | --- |
| minus | `0.5` | `0.975807` | `s=3.414894, l=0.0` | `reset_decompression / core_throat` | false | `sector_closure_residual` |
| plus | `0.5` | `0.971258` | `s=1.659574, l=2.3` | `reset_decompression / outer_quarantine_shell` | false | `sector_closure_residual` |
| minus | `1.0` | `0.231756` | `s=4.380319, l=0.0` | `reset_decompression / core_throat` | false | `sector_closure_residual` |
| plus | `1.0` | `0.227503` | `s=1.747340, l=2.4` | `reset_decompression / outer_quarantine_shell` | false | `sector_closure_residual` |
| minus | `2.0` | `0.053635` | `s=4.380319, l=-0.7` | `reset_decompression / core_throat` | false | `sector_closure_residual` |
| plus | `2.0` | `0.051880` | `s=4.204787, l=0.2` | `reset_decompression / core_throat` | false | `sector_closure_residual` |

The intermediate S0/J/R residual-inclusive companion scanned the same `137,064`
windows at the same widths and also found:

```text
all-window benchmark-floor violations: 0
scoreable benchmark-floor violations:  0
```

Its tightest margin is the same `0.051880` tau-2 plus result, with
`J_endpoint_junction_layer` dominant in the tight broad-window cases. The
limiting windows remain non-live reset/decompression rows, not packet rows.

## Trace And Dense-Bundle Companions

The existing trace expansion companion remains favorable for the repaired lead.
All branch-band radial, off-axis, and congruence probes escape, and no
branch-band trace remains both-shrinking to the end.

The dense congruence audit is the major repair result:

```text
dense rays:                         136
radial escapes:                     136 / 136
recovered from both-shrinking:      136 / 136
sustained both-shrinking to end:    0
caustic-like bundles:               0 / 8
worst all-both l-width ratio:       0.275792
worst all-both areal-width ratio:   0.170374
```

This changes the finite-bundle classification from adverse caustic-like
compression with later escape to favorable dense-bundle transient focusing.

## Decision

Promote `rematch_w6_t1p5` as the conservative repaired beta075 lead for the next
higher-rung feasibility work.

The result supports the following current claim:

```text
The beta075 p003_mid mechanism with the rematch_w6_t1p5 generator-level
beta-collar repair remains live-clean, clears the dense finite-bundle
caustic-like collapse diagnostic, improves the main live source-accounting
channels, and passes full-stride affine-reparameterized SNEC companions in both
component-sector and intermediate S0/J/R residual-inclusive modes.
```

Avoid:

```text
The physical source is realized.
The endpoint/junction layer is conserved.
The global horizon question is solved.
The result is robust across beta100 or higher-V operation.
```

## Next Rung

Do not broaden to beta100 or V-headroom yet. The next work should be a small
local collar robustness bracket around the conservative lead:

```text
primary controls:
  beta_rematch_width_multiplier near 6.0
  beta_rematch_temporal_width_multiplier near 1.5

track:
  dense-bundle width floor
  positive live packet-norm samples
  live source-accounting channels
  support-edge J selected-null
  live negative packet-density watch item
  full or smoke affine SNEC margins depending on rung cost
```

If nearby variants keep the dense-bundle repair while reducing the support-edge
selected-null transfer, promote the best local bracket. If the bracket shows
the support-edge transfer is unavoidable, keep `rematch_w6_t1p5` and move the
concern into the physical-source family target for J.
