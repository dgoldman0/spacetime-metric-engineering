# Stage II Beta075 Reduced Principal-Symbol Hyperbolicity Gate

## Status

Overall status: `watch`.

This is a fixed-background local principal-symbol harness for the promoted endpoint/support constitutive sector. It uses the prescribed beta075 service metric and the support-stroke point-fit ledgers; it does not evolve the metric or claim a complete matter action.

## Reduced Model

The local radial-frame principal symbol uses seven primitive perturbations:

```text
U = (h, psi, chi_Omega, pi_Omega, Phi_support, Pi_support, n_l)
```

It checks block principal speeds for heat/enthalpy, angular internal response, support stroke/stress, and director advection. Rest-frame characteristic speeds are mapped through the ADM service cone `dl/dsigma = -beta +/- alpha/sqrt(gamma_ll)`.

Gate conditions:

```text
real finite characteristic speeds
complete eigenbasis
relative speeds inside the service cone
positive h_reg / Type-I / transport margin
zero live support exchange
watch if cone margin, heat ratio, transport margin, or rapidity gets too close to boundary
```

## Run Summary

| label | status | active rows | fail rows | watch rows | min cone margin | p01 cone margin | p99 heat ratio | max psi |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_24x14 | watch | 7188 | 0 | 19 | 0.000241 | 0.018308 | 0.974975 | 4.507205 |
| dense_24x14 | watch | 28359 | 0 | 56 | 7.881e-05 | 0.017633 | 0.975555 | 5.064348 |
| baseline_compact22x13 | watch | 7188 | 0 | 19 | 0.000241 | 0.018308 | 0.974975 | 4.507205 |
| dense_compact22x13 | watch | 28359 | 0 | 56 | 7.881e-05 | 0.017597 | 0.975555 | 5.064348 |

## Dense Adversarial Rows

| assignment | stage | region | status | min cone margin | p01 cone margin | min transport margin | p99 heat ratio | max psi |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| reset_decompression_endpoint_junction | reset_decompression | support_edge | watch | 7.881e-05 | 0.019189 | 7.983e-05 | 0.974975 | 5.064348 |
| support_edge_endpoint_junction | release_shift_fade | support_edge | watch | 0.000321 | 0.001503 | 0.000337 | 0.997923 | 4.344490 |
| reset_decompression_endpoint_junction | reset_decompression | core_throat | watch | 0.000473 | 0.027463 | 0.000494 | 0.962544 | 4.153016 |
| support_edge_endpoint_junction | catch_rematch | support_edge | watch | 0.000650 | 0.012336 | 0.000761 | 0.976998 | 3.936598 |
| support_edge_endpoint_junction | entry_precatch | support_edge | watch | 0.001058 | 0.009848 | 0.001131 | 0.984370 | 3.738546 |
| support_edge_endpoint_junction | held_carry | support_edge | watch | 0.003021 | 0.003591 | 0.003678 | 0.994690 | 3.148398 |
| support_edge_endpoint_junction | post_release_buffer | support_edge | watch | 0.003970 | 0.008001 | 0.004798 | 0.990954 | 3.015185 |
| support_edge_endpoint_junction | pre_entry_setup | support_edge | pass | 0.036444 | 0.043177 | 0.060011 | 0.925134 | 1.737951 |

## Interpretation

reduced endpoint/support principal symbol has real complete in-cone characteristics on promoted runs, with watch rows requiring action-level follow-up

The result should be read as a necessary local hyperbolicity check. A pass/watch result means the reduced constitutive sector has a real in-cone local principal symbol on the tested rows, but the boundary-near rows still need a real evolution or action-level closure. A fail would have killed the current support-sector PDE direction before evolution.

## Next

```text
1. Aim any reduced evolution model at the dense local watch rows first.
2. Freeze support-sector coefficients before cross-mesh evolution tests.
3. Do not treat this as a coupled Einstein-matter result.
```

## Provenance

- `baseline_24x14`: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5/endpoint_support_stroke_exchange_point_fit.csv`
- `dense_24x14`: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5/endpoint_support_stroke_exchange_point_fit.csv`
- `baseline_compact22x13`: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_support_stroke_compact22x13_freeze_rematch_w6_t1p5/endpoint_support_stroke_exchange_point_fit.csv`
- `dense_compact22x13`: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_stroke_compact22x13_freeze_rematch_w6_t1p5/endpoint_support_stroke_exchange_point_fit.csv`
