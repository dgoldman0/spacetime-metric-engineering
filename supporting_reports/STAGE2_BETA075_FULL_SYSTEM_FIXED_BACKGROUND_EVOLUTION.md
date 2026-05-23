# Stage II Beta075 Full-System Fixed-Background Evolution Stress Test

## Status

Overall status: `full_system_evolution_pass_with_watches`.

Sealed beta075 passes the observed-amplitude fixed-background full-domain evolution stress test, with large-stress and smoothness watches carried forward.

This is the first full-domain fixed-background evolution rung after the bounded seal gate. It uses the sealed beta075 support package as input, not as an optimization target, and evolves a bounded-rapidity perturbation over the active non-live support-source surface with radial and service-time upwind transport.

## Domain

| point rows | active source rows | live evolved rows | packet-live evolved rows | radial groups | service groups |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 29317 | 28359 | 0 | 0 | 682 | 125 |

Scenario workers: `4`.

## Scenario Summary

| scenario | status | limiter | fail rows | over-budget rows | max budget fraction | min cone margin | min transport margin | max state/source | clipped rows |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| observed_full_outward_forward_unlimited | pass | False | 0 | 0 | 0.120935 | 0.000330 | 6.971e-05 | 0.926360 | 0 |
| observed_full_inward_forward_unlimited | pass | False | 0 | 0 | 0.121201 | 0.000182 | 6.523e-05 | 0.914960 | 0 |
| observed_full_outward_backward_unlimited | pass | False | 0 | 0 | 0.115633 | 0.003412 | 6.773e-05 | 0.924707 | 0 |
| observed_full_outward_forward_budget_limited | pass | True | 0 | 0 | 0.120935 | 0.000330 | 6.971e-05 | 0.926360 | 0 |
| large_full_outward_forward_unlimited | pass | False | 0 | 0 | 0.604677 | 1.538e-05 | 1.701e-05 | 0.926360 | 0 |
| large_full_outward_forward_budget_limited | pass | True | 0 | 0 | 0.604677 | 1.538e-05 | 1.701e-05 | 0.926360 | 0 |

## Result Read

This rung is complete. The observed-amplitude full-domain rows passed without limiter clipping, live-row evolution, packet-live evolution, over-budget rows, or state amplification. Those rows are the seal driver for this test.

The large-amplitude rows are retained only as engineering-margin watches. Because this rung passed, there is no remaining same-level component work required here; the next work should move upward to action-level fixed-background PDE proof obligations or broader full-system validation unless a later gate localizes a failure back to a specific component.

## Provenance

- closure dir: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5`
- source-coupling dir: `toolkit/adm_harness_cli/runs/stage2_beta075_support_source_coupling_package_support_edge_cap095`
- point closure: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5/endpoint_support_total_closure_point_closure.csv`
- caveat: Fixed-background split-step evolution over the active non-live beta075 support-source domain. It evolves the bounded rapidity perturbation on the sealed prescribed metric and checks local cone/transport budgets, live exclusion, source localization, and state amplification. It is not a coupled Einstein-matter evolution or final PDE theorem.
