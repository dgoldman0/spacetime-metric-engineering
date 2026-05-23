# Stage II Beta075 Coupled Support-Source Dynamics

## Status

Overall status: `coupled_support_source_watch`.

The observed support-source amplitude survives coupled evolution, but the large-source limiter contrast is incomplete.

This is a reduced `1+1` fixed-background evolution on the bottleneck service-radial slice. The sealed support closure supplies a fitted `P/F` support-source profile, the profile is injected through a normalized time pulse, and the resulting rapidity perturbation is advected while the existing local cone budget remains the hard gate.

## Bottleneck And Source Normalization

| row | s | l | stage | region | baseline psi | budget Delta psi | observed source Delta psi | large source Delta psi |
| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| 4605 | 2.537234 | 2.000000 | reset_decompression | support_edge | 5.064348 | 2.183566 | 0.626342 | 3.131712 |

| source column | normalizer row | normalizer l | normalizer density | max normalized source |
| --- | ---: | ---: | ---: | ---: |
| candidate_support_abs_PF_density | 4605 | 2.000000 | 0.040284 | 3.207034 |

## Scenario Summary

| scenario | status | limiter | fail rows | over-budget rows | max budget fraction | bottleneck max fraction | final bottleneck Delta psi | min cone margin | clipped rows |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| observed_source_outward_unlimited | pass | False | 0 | 0 | 0.170065 | 0.170065 | 0.371349 | 3.750e-05 | 0 |
| observed_source_inward_unlimited | pass | False | 0 | 0 | 0.128254 | 0.128254 | 0.044486 | 4.502e-05 | 0 |
| observed_source_outward_budget_limited | pass | True | 0 | 0 | 0.170065 | 0.170065 | 0.371349 | 3.750e-05 | 0 |
| large_source_outward_unlimited | pass | False | 0 | 0 | 0.850326 | 0.850326 | 1.856743 | 1.923e-06 | 0 |
| large_source_outward_budget_limited | pass | True | 0 | 0 | 0.850326 | 0.850326 | 1.856743 | 1.923e-06 | 0 |

## Interpretation

The test upgrades the previous impulse-advection check by making the support source itself the driver. Passing observed rows therefore means the closure-derived support profile can be coupled into the rapidity equation at the measured `O(1e-4)` amplitude without relying on limiter clipping.

The distributed larger-reference source does not reproduce the old instant-impulse failure; it stays below the local budget without limiter clipping. That is favorable for the coupled source profile, but it leaves the limiter-contrast guard incomplete and keeps this at watch level. The largest larger-reference budget fraction in this run is `0.850326`.

## Provenance

- point closure: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5/endpoint_support_total_closure_point_closure.csv`
- bottleneck row: `4605` at `s=2.537234`, `l=2.000000`
- slice rows: `85`
