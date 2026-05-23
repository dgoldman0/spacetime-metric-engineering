# Stage II Beta075 Rapidity Advection Non-Concentration

## Status

Overall status: `advection_nonconcentration_with_limiter_guard`.

Observed O(1e-4) rapidity impulses do not concentrate over budget under the tested radial advection, and the budget limiter catches the known larger-kick failure.

This is a reduced `1+1` fixed-background rapidity-impulse advection check on the service-radial `l` slice containing the tightest dense adversarial row. It asks whether monotone radial advection concentrates the admissible `O(1e-4)` rapidity kick into an over-budget edge row, and whether a local budget limiter catches the known larger-kick failure.

## Bottleneck Row

| row | s | l | stage | region | baseline psi | baseline transport margin | budget Delta psi | observed Delta psi | large Delta psi |
| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 4605 | 2.537234 | 2.000000 | reset_decompression | support_edge | 5.064348 | 7.983e-05 | 2.183566 | 0.626342 | 3.131712 |

## Scenario Summary

| scenario | status | limiter | fail rows | over-budget rows | max budget fraction | bottleneck max fraction | min cone margin | clipped rows | max clip |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| observed_outward_unlimited | pass | False | 0 | 0 | 0.286844 | 0.286844 | 2.252e-05 | 0 | 0.000000 |
| observed_inward_unlimited | pass | False | 0 | 0 | 0.286844 | 0.286844 | 2.252e-05 | 0 | 0.000000 |
| observed_outward_budget_limited | pass | True | 0 | 0 | 0.286844 | 0.286844 | 2.252e-05 | 0 | 0.000000 |
| large_outward_unlimited | fail | False | 1 | 1 | 1.434219 | 1.434219 | 1.501e-07 | 0 | 0.000000 |
| large_outward_budget_limited | limited_pass | True | 0 | 0 | 0.950000 | 0.950000 | 1.244e-06 | 1 | 1.057324 |

## Interpretation

The observed `O(1e-4)` rapidity impulse stays below every local budget under both outward and inward monotone radial advection on the bottleneck slice. The budget limiter is inactive on the observed case, so it is not hiding a marginal pass.

The larger `O(5e-4)` reference impulse fails without the limiter and passes with the limiter active. That makes the next reduced PDE target sharper: keep the limiter as a guard for over-budget support-source concentration, but first try to prove or numerically demonstrate that the physical support-source/advection law stays in the observed-kick regime.

## Provenance

- point fit: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5/endpoint_support_stroke_exchange_point_fit.csv`
- bottleneck row: `4605` at `s=2.537234`, `l=2.000000`
- slice rows: `85`
