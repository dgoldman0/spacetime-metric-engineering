# Stage II Beta075 Collar Local Bracket Checkpoint

Date: 2026-05-22

## Summary

This checkpoint records the first local bracket around the promoted repaired
beta075 lead:

```text
lead: rematch_w6_t1p5
axis 1: beta_rematch_width_multiplier 5.5, 6.0, 6.5 at temporal 1.5
axis 2: beta_rematch_temporal_width_multiplier 1.25, 1.5, 1.75 at width 6.0
```

The bracket is not intended to replace the promotion audit. It asks whether the
remaining support-edge J selected-null watch item is locally tunable without
giving back the live-channel relief that made `rematch_w6_t1p5` attractive.

At this checkpoint, `rematch_w6_t1p25` has landed; `rematch_w6_t1p75` is still
running in the background.

## Completed Bracket Points

All completed local-bracket ledgers are live-clean:

| label | width | temporal | max live packet norm | positive live packet norm |
| --- | ---: | ---: | ---: | ---: |
| `rematch_w5p5_t1p5` | `5.5` | `1.5` | `-9.935403` | `0` |
| `rematch_w6_t1p5` | `6.0` | `1.5` | `-9.935129` | `0` |
| `rematch_w6p5_t1p5` | `6.5` | `1.5` | `-9.934818` | `0` |
| `rematch_w6_t1p25` | `6.0` | `1.25` | `-9.942843` | `0` |

Main live burden comparison:

| label | live `neg_Tkk_radial` | live `abs_p_l` | live `abs_pOmega` | live `abs_j_l` | live `neg_rho_packet` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `w5.5/t1.5` | `12.163340` | `0.620778` | `1.493945` | `0.067831` | `0.0000328` |
| `w6.0/t1.5` | `12.008237` | `0.620064` | `1.484949` | `0.066347` | `0.0004830` |
| `w6.5/t1.5` | `11.867158` | `0.619430` | `1.476976` | `0.065073` | `0.0013495` |
| `w6.0/t1.25` | `12.005182` | `0.620084` | `1.485288` | `0.066288` | `0.0004830` |

Endpoint J support-edge watch:

| label | support-edge J selected-null | reset J selected-null | support-edge J current | support-edge J angular |
| --- | ---: | ---: | ---: | ---: |
| `w5.5/t1.5` | `0.638110` | `3.696026` | `0.114065` | `1.478747` |
| `w6.0/t1.5` | `0.642179` | `3.696084` | `0.115340` | `1.463343` |
| `w6.5/t1.5` | `0.646253` | `3.696135` | `0.116654` | `1.446052` |
| `w6.0/t1.25` | `0.642335` | `3.695933` | `0.115374` | `1.464207` |

## Interpretation

The width axis is behaving monotonically and legibly:

```text
narrower width:
  lowers the support-edge J selected-null watch and tiny packet-density watch,
  but gives back live-channel relief.

wider width:
  improves the main live service channels,
  but increases support-edge J selected-null and live packet-density watch.
```

This is a useful engineering signal. The collar repair is not a one-point
accident; it is a continuous control with a readable cost curve. It also means
`rematch_w6_t1p5` remains a good conservative midpoint rather than being
obviously dominated by either width neighbor.

The short temporal point `w6/t1.25` is essentially neutral relative to the lead.
It slightly deepens packet-norm margin and slightly lowers live radial-null and
current burden, but does not materially reduce the support-edge J watch or the
packet-density watch. It does not create a new design branch.

## Decision

Do not wait on the full bracket before starting the next rung. Let
`rematch_w6_t1p75` finish as supporting local-bracket evidence, but move the
main work to the physical-source feasibility rung.

Current local-design decision:

```text
Keep rematch_w6_t1p5 as the conservative promoted lead.
Treat rematch_w6p5_t1p5 as the stronger-live-relief / higher-watch bracket.
Treat rematch_w5p5_t1p5 as the lower-watch / weaker-live-relief bracket.
Treat rematch_w6_t1p25 as a near-neutral temporal check.
```

The bracket does not alter the broader feasibility conclusion from the
promotion audit. It strengthens it: the repaired collar has a tunable,
interpretable tradeoff. The next unknown is not local collar existence. The next
unknown is whether the non-live endpoint J target can be represented by a
finite-width, conservation-compatible source family without singular support or
extreme effective coupling.

## Next Rung

Start an endpoint J source-family/conservation diagnostic for the promoted lead:

```text
input:
  rematch_w6_t1p5 component, string-cloud, and intermediate S0/J/R artifacts

model target:
  J_support_edge_shoulder
  J_reset_decompression_cap

diagnostics:
  finite-width active volume and concentration
  approximate divergence/conservation residual proxy
  amplitude/effective-coupling scale proxy
  resolution-growth hooks for later dense confirmation
  live-exclusion hard gate
```

Promotion criterion for the next rung:

```text
J admits a finite-width, non-live, approximately conserved source-family target
whose concentration and amplitude proxies do not sharpen pathologically.
```

Failure criterion:

```text
J only closes by becoming singular, resolution-growing, live-leaking, or
requiring an extreme effective coupling/amplitude.
```
