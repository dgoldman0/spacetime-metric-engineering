# Stage II Beta075 Reduced Transport Evolution Pilot

## Status

Overall status: `transport_law_candidate`.

This is a local fixed-background evolution pilot for the heat-current/transport variable on the dense principal-symbol watch rows. It compares a raw heat-ratio perturbation against a bounded rapidity variable with relaxation back to the frozen beta075 state.

## Scenario Summary

| scenario | model | status | fail rows | watch rows | min cone margin | min transport margin | p99 heat ratio | max psi |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_delta_p1e4_k0 | raw_ratio | fail | 1 | 55 | 9.872e-13 | -2.017e-05 | 1.000020 | 4.855862 |
| raw_delta_p1e4_k4 | raw_ratio | fail | 1 | 56 | 9.872e-13 | -2.017e-05 | 0.999923 | 7.176279 |
| rapidity_delta_p1e4_k0 | rapidity | watch | 0 | 56 | 2.252e-05 | 2.281e-05 | 0.999977 | 5.690691 |
| rapidity_delta_p1e4_k1 | rapidity | watch | 0 | 56 | 2.252e-05 | 2.281e-05 | 0.999952 | 5.690691 |
| rapidity_delta_p1e4_k4 | rapidity | watch | 0 | 56 | 2.252e-05 | 2.281e-05 | 0.999923 | 5.690691 |
| rapidity_delta_p2p5e4_k4 | rapidity | watch | 0 | 56 | 3.440e-06 | 3.484e-06 | 0.999927 | 6.630204 |
| rapidity_delta_p5e4_k4 | rapidity | fail | 1 | 56 | 1.501e-07 | 1.521e-07 | 0.999942 | 8.196060 |
| rapidity_relief_m5e4_k1 | rapidity | watch | 0 | 55 | 0.000279 | 0.000283 | 0.999558 | 4.432067 |

## Local Failures

| scenario | assignment | stage | region | fail rows | min cone margin | min transport margin |
| --- | --- | --- | --- | ---: | ---: | ---: |
| raw_delta_p1e4_k0 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 1 | 9.872e-13 | -2.017e-05 |
| raw_delta_p1e4_k4 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 1 | 9.872e-13 | -2.017e-05 |
| rapidity_delta_p5e4_k4 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 1 | 1.501e-07 | 1.521e-07 |

## Interpretation

bounded rapidity transport with damping preserves hard cone/transport gates under the first raw heat-current failure stress

The pilot is not a full spatial PDE evolution, but it tests the exact fragility found by the sensitivity rung. A raw `+1e-4` heat-ratio perturbation fails immediately because it crosses the transport boundary. Evolving the same stress as a perturbation of bounded rapidity keeps the ratio below one and allows damping to recover margin. That makes bounded transport rapidity a plausible reduced evolution variable, not just a notation choice.

## Next

```text
1. Add spatial coupling on l for the same rapidity variable.
2. Couple the support stroke/stress variables to the rapidity relaxation source.
3. Require the O(1e-4) stress case to preserve cone and transport margins under spatial advection, not just local relaxation.
```

## Provenance

- point fit: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5/endpoint_support_stroke_exchange_point_fit.csv`
- selected rows: `56` dense watch/near-watch rows
