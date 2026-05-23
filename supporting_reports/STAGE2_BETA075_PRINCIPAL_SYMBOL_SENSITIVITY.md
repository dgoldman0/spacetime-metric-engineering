# Stage II Beta075 Principal-Symbol Sensitivity

## Status

Overall status: `fragile_watch`.

This is a frozen-coefficient sensitivity check on the dense principal-symbol watch rows. It perturbs local heat-current ratio, regulator margin, and characteristic-speed caps without refitting the support sector.

## Scenario Summary

| scenario | status | fail rows | watch rows | min cone margin | min transport margin | p99 heat ratio | min h_reg |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nominal | watch | 0 | 56 | 7.881e-05 | 7.983e-05 | 0.999842 | 4.036e-09 |
| heat_relief_m5e4 | watch | 0 | 51 | 0.000572 | 0.000580 | 0.999342 | 4.036e-09 |
| heat_stress_p2p5e5 | watch | 0 | 56 | 5.413e-05 | 5.483e-05 | 0.999867 | 4.036e-09 |
| heat_stress_p5e5 | watch | 0 | 56 | 2.945e-05 | 2.983e-05 | 0.999892 | 4.036e-09 |
| heat_stress_p7p5e5 | watch | 0 | 56 | 4.770e-06 | 4.832e-06 | 0.999917 | 4.036e-09 |
| heat_stress_p1e4 | fail | 1 | 55 | 9.872e-13 | -2.017e-05 | 0.999942 | 4.036e-09 |
| heat_stress_p2p5e4 | fail | 2 | 54 | 9.424e-13 | -0.000170 | 1.000092 | 4.036e-09 |
| heat_stress_p5e4 | fail | 7 | 49 | 9.290e-13 | -0.000420 | 1.000342 | 4.036e-09 |
| regulator_half | watch | 0 | 53 | 7.911e-05 | 7.983e-05 | 0.999842 | 2.018e-09 |
| regulator_tenth | watch | 0 | 49 | 7.951e-05 | 7.983e-05 | 0.999842 | 4.036e-10 |
| regulator_one_percent | watch | 0 | 48 | 7.973e-05 | 7.983e-05 | 0.999842 | 4.036e-11 |
| regulator_zero | fail | 56 | 0 | 7.983e-05 | 7.983e-05 | 0.999842 | 0.000000 |
| heat_sound_cap_0p50 | watch | 0 | 56 | 7.881e-05 | 7.983e-05 | 0.999842 | 4.036e-09 |
| heat_sound_cap_0p70 | watch | 0 | 56 | 7.881e-05 | 7.983e-05 | 0.999842 | 4.036e-09 |
| support_sound_cap_0p65 | watch | 0 | 56 | 7.881e-05 | 7.983e-05 | 0.999842 | 4.036e-09 |
| combined_heat_p5e5_cap0p50 | watch | 0 | 56 | 2.945e-05 | 2.983e-05 | 0.999892 | 4.036e-09 |

## Heat-Current Stress Ladder

| heat delta | status | fail rows | min cone margin | min transport margin |
| ---: | --- | ---: | ---: | ---: |
| -0.000500 | watch | 0 | 0.000572 | 0.000580 |
| 2.500e-05 | watch | 0 | 5.413e-05 | 5.483e-05 |
| 5.000e-05 | watch | 0 | 2.945e-05 | 2.983e-05 |
| 7.500e-05 | watch | 0 | 4.770e-06 | 4.832e-06 |
| 0.000100 | fail | 1 | 9.872e-13 | -2.017e-05 |
| 0.000250 | fail | 2 | 9.424e-13 | -0.000170 |
| 0.000500 | fail | 7 | 9.290e-13 | -0.000420 |

## Regulator And Speed-Cap Probes

Regulator depletion alone keeps the cone speeds real until the regulator is driven exactly to zero, where the positive-margin gate fails. Raising heat/support speed caps mostly changes cone-margin tightness; it does not create the first hard failure before heat-current stress does.

| scenario | status | fail rows | min cone margin | min h_reg |
| --- | --- | ---: | ---: | ---: |
| regulator_half | watch | 0 | 7.911e-05 | 2.018e-09 |
| regulator_tenth | watch | 0 | 7.951e-05 | 4.036e-10 |
| regulator_one_percent | watch | 0 | 7.973e-05 | 4.036e-11 |
| regulator_zero | fail | 56 | 7.983e-05 | 0.000000 |
| heat_sound_cap_0p50 | watch | 0 | 7.881e-05 | 4.036e-09 |
| heat_sound_cap_0p70 | watch | 0 | 7.881e-05 | 4.036e-09 |
| support_sound_cap_0p65 | watch | 0 | 7.881e-05 | 4.036e-09 |

## First Local Failures

| scenario | assignment | stage | region | fail rows | min cone margin | min transport margin |
| --- | --- | --- | --- | ---: | ---: | ---: |
| heat_stress_p1e4 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 1 | 9.872e-13 | -2.017e-05 |
| heat_stress_p2p5e4 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 2 | 9.424e-13 | -0.000170 |
| heat_stress_p5e4 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 4 | 9.424e-13 | -0.000420 |
| heat_stress_p5e4 | support_edge_endpoint_junction | release_shift_fade | support_edge | 2 | 9.290e-13 | -0.000163 |
| heat_stress_p5e4 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 1 | 9.583e-13 | -6.077e-06 |
| regulator_zero | reset_decompression_endpoint_junction | reset_decompression | support_edge | 24 | 7.983e-05 | 7.983e-05 |
| regulator_zero | reset_decompression_endpoint_junction | reset_decompression | core_throat | 11 | 0.000494 | 0.000494 |
| regulator_zero | support_edge_endpoint_junction | release_shift_fade | support_edge | 10 | 0.000337 | 0.000337 |
| regulator_zero | support_edge_endpoint_junction | catch_rematch | support_edge | 4 | 0.000761 | 0.000761 |
| regulator_zero | support_edge_endpoint_junction | entry_precatch | support_edge | 3 | 0.001131 | 0.001131 |

## Interpretation

nominal watch rows pass hard symbol gates, but O(1e-4) heat-current worsening creates hard local failures

The sensitivity result sharpens the previous watch: the reduced symbol is not algebraically failing at the frozen point, but some dense rows have only an O(1e-4) heat-current buffer before the positive transport/cone-margin gates fail. That argues for a regulator/transport-margin-preserving reduced evolution before any broader PDE claim.

## Next

```text
1. Build reduced fixed-background evolution with explicit transport-margin preservation.
2. Use the heat-stress failure rows as boundary/perturbation targets.
3. Do not promote to action-level hyperbolicity until O(1e-4) heat-current fragility is explained or buffered.
```

## Provenance

- point fit: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5/endpoint_support_stroke_exchange_point_fit.csv`
- selected rows: `56` nominal watch/near-watch rows
