# Stage II Beta075 Rapidity-Budget Diagnostic

## Status

Overall status: `large_kick_limiter_watch`.

The observed O(1e-4) rapidity source kick fits every row, but the larger O(5e-4) reference kick exceeds tight local budgets.

This diagnostic budgets each dense adversarial row in the bounded transport-rapidity variable. The budget is the largest positive `Delta psi` that keeps the local reduced principal symbol above the `1e-6` relative cone-margin gate.

## Budget Summary

| rows | min admissible Delta psi | max observed fraction | observed over-budget rows | large-kick over-budget rows | min observed residual |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 56 | 2.183566 | 0.286844 | 0 | 1 | 1.557223 |

## Recommendation Counts

| recommendation | rows |
| --- | ---: |
| large_kick_limiter_watch | 1 |
| pde_advection_proof_target | 55 |

## Per-Row Rapidity Budgets

| row | s | l | assignment | stage | region | baseline psi | baseline margin | max Delta psi | observed Delta psi | observed fraction | large fraction | recommendation |
| ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 4605 | 2.537234 | 2.000000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 5.064348 | 7.983e-05 | 2.183566 | 0.626342 | 0.286844 | 1.434219 | large_kick_limiter_watch |
| 5114 | 2.800532 | 1.350000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 4.554896 | 0.000221 | 2.669752 | 0.226135 | 0.084703 | 0.423513 | pde_advection_proof_target |
| 5113 | 2.800532 | 1.300000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 4.409537 | 0.000296 | 2.816957 | 0.169100 | 0.060029 | 0.300147 | pde_advection_proof_target |
| 2318 | 0.913564 | 1.350000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 4.344490 | 0.000337 | 2.886428 | 0.148478 | 0.051440 | 0.257200 | pde_advection_proof_target |
| 2478 | 1.089096 | 1.550000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 4.192918 | 0.000456 | 3.024563 | 0.109663 | 0.036258 | 0.181288 | pde_advection_proof_target |
| 5136 | 2.844415 | -1.900000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 4.171301 | 0.000476 | 3.062174 | 0.105025 | 0.034298 | 0.171488 | pde_advection_proof_target |
| 4892 | 2.712766 | -1.050000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 4.153016 | 0.000494 | 3.080033 | 0.101255 | 0.032875 | 0.164374 | pde_advection_proof_target |
| 2603 | 1.264628 | -1.950000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 4.036079 | 0.000624 | 3.196331 | 0.080150 | 0.025076 | 0.125379 | pde_advection_proof_target |
| 2015 | 0.606383 | 1.300000 | support_edge_endpoint_junction | catch_rematch | support_edge | 3.936598 | 0.000761 | 3.238544 | 0.065699 | 0.020286 | 0.101432 | pde_advection_proof_target |
| 2571 | 1.220745 | -1.800000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 3.746872 | 0.001112 | 3.457137 | 0.044969 | 0.013008 | 0.065038 | pde_advection_proof_target |
| 215 | -1.236702 | 1.550000 | support_edge_endpoint_junction | entry_precatch | support_edge | 3.738546 | 0.001131 | 3.482556 | 0.044227 | 0.012700 | 0.063498 | pde_advection_proof_target |
| 4491 | 2.493351 | 0.650000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 3.665687 | 0.001308 | 3.553849 | 0.038237 | 0.010759 | 0.053797 | pde_advection_proof_target |
| 2464 | 1.089096 | -1.600000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 3.491993 | 0.001851 | 3.593583 | 0.027030 | 0.007522 | 0.037609 | pde_advection_proof_target |
| 4313 | 2.405585 | 0.350000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 3.541259 | 0.001678 | 3.677212 | 0.029824 | 0.008111 | 0.040553 | pde_advection_proof_target |
| 4860 | 2.668883 | 1.700000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.519846 | 0.001751 | 3.694100 | 0.028576 | 0.007736 | 0.038678 | pde_advection_proof_target |
| 4775 | 2.625000 | 1.800000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.512753 | 0.001776 | 3.706586 | 0.028174 | 0.007601 | 0.038005 | pde_advection_proof_target |
| 5057 | 2.800532 | -1.500000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.428059 | 0.002104 | 3.781818 | 0.023792 | 0.006291 | 0.031456 | pde_advection_proof_target |
| 4382 | 2.449468 | -0.500000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 3.408717 | 0.002187 | 3.798583 | 0.022891 | 0.006026 | 0.030131 | pde_advection_proof_target |
| 4690 | 2.581117 | 1.900000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.419581 | 0.002140 | 3.800845 | 0.023393 | 0.006155 | 0.030773 | pde_advection_proof_target |
| 5023 | 2.756649 | 1.150000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.360934 | 0.002406 | 3.826950 | 0.020809 | 0.005438 | 0.027188 | pde_advection_proof_target |
| 5133 | 2.844415 | -2.050000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.368278 | 0.002371 | 3.840527 | 0.021116 | 0.005498 | 0.027492 | pde_advection_proof_target |
| 2537 | 1.176862 | -1.700000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 3.243840 | 0.003040 | 3.866405 | 0.016475 | 0.004261 | 0.021305 | pde_advection_proof_target |
| 699 | -0.710106 | 1.500000 | support_edge_endpoint_junction | entry_precatch | support_edge | 3.362069 | 0.002400 | 3.873300 | 0.020856 | 0.005385 | 0.026923 | pde_advection_proof_target |
| 1709 | 0.299202 | 1.400000 | support_edge_endpoint_junction | catch_rematch | support_edge | 3.296935 | 0.002734 | 3.875108 | 0.018315 | 0.004726 | 0.023632 | pde_advection_proof_target |
| 5052 | 2.800532 | -1.750000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.320654 | 0.002607 | 3.878045 | 0.019202 | 0.004952 | 0.024758 | pde_advection_proof_target |
| 4945 | 2.712766 | 1.600000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.281991 | 0.002817 | 3.915783 | 0.017777 | 0.004540 | 0.022699 | pde_advection_proof_target |
| 5062 | 2.800532 | -1.250000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.275471 | 0.002853 | 3.924713 | 0.017548 | 0.004471 | 0.022355 | pde_advection_proof_target |
| 5030 | 2.756649 | 1.500000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.258948 | 0.002949 | 3.929474 | 0.016979 | 0.004321 | 0.021604 | pde_advection_proof_target |
| 4433 | 2.449468 | 2.050000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.305607 | 0.002687 | 3.931525 | 0.018635 | 0.004740 | 0.023699 | pde_advection_proof_target |
| 4846 | 2.668883 | 1.000000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 3.246508 | 0.003023 | 3.942400 | 0.016563 | 0.004201 | 0.021006 | pde_advection_proof_target |
| 1313 | -0.095745 | 1.400000 | support_edge_endpoint_junction | catch_rematch | support_edge | 3.211308 | 0.003244 | 3.958005 | 0.015440 | 0.003901 | 0.019505 | pde_advection_proof_target |
| 5051 | 2.800532 | -1.800000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.225569 | 0.003152 | 3.975288 | 0.015886 | 0.003996 | 0.019980 | pde_advection_proof_target |
| 2365 | 0.957447 | 1.700000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 3.003440 | 0.004911 | 3.995476 | 0.010205 | 0.002554 | 0.012771 | pde_advection_proof_target |
| 2056 | 0.650266 | 1.150000 | support_edge_endpoint_junction | held_carry | support_edge | 3.024277 | 0.004711 | 4.007362 | 0.010638 | 0.002655 | 0.013273 | pde_advection_proof_target |
| 2057 | 0.650266 | 1.200000 | support_edge_endpoint_junction | held_carry | support_edge | 3.148398 | 0.003678 | 4.055450 | 0.013621 | 0.003359 | 0.016793 | pde_advection_proof_target |
| 5135 | 2.844415 | -1.950000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.148248 | 0.003679 | 4.055925 | 0.013617 | 0.003357 | 0.016786 | pde_advection_proof_target |
| 2501 | 1.132979 | -1.650000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 2.933263 | 0.005649 | 4.065652 | 0.008876 | 0.002183 | 0.010915 | pde_advection_proof_target |
| 4604 | 2.537234 | 1.950000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.123800 | 0.003863 | 4.089107 | 0.012969 | 0.003172 | 0.015858 | pde_advection_proof_target |
| 4518 | 2.493351 | 2.000000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.096124 | 0.004082 | 4.117406 | 0.012274 | 0.002981 | 0.014905 | pde_advection_proof_target |
| 314 | -1.105053 | -1.500000 | support_edge_endpoint_junction | entry_precatch | support_edge | 3.003930 | 0.004907 | 4.143878 | 0.010215 | 0.002465 | 0.012326 | pde_advection_proof_target |
| 2659 | 1.308511 | 1.850000 | support_edge_endpoint_junction | post_release_buffer | support_edge | 3.015185 | 0.004798 | 4.144300 | 0.010447 | 0.002521 | 0.012604 | pde_advection_proof_target |
| 2604 | 1.264628 | -1.900000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 3.040354 | 0.004563 | 4.150729 | 0.010984 | 0.002646 | 0.013231 | pde_advection_proof_target |
| 4669 | 2.581117 | 0.850000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 3.028051 | 0.004676 | 4.151907 | 0.010718 | 0.002581 | 0.012907 | pde_advection_proof_target |
| 4806 | 2.668883 | -1.000000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 3.038123 | 0.004583 | 4.153398 | 0.010935 | 0.002633 | 0.013164 | pde_advection_proof_target |
| 2016 | 0.606383 | 1.350000 | support_edge_endpoint_junction | catch_rematch | support_edge | 2.766646 | 0.007875 | 4.155621 | 0.006374 | 0.001534 | 0.007670 | pde_advection_proof_target |
| 5134 | 2.844415 | -2.000000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.037154 | 0.004592 | 4.158829 | 0.010914 | 0.002624 | 0.013121 | pde_advection_proof_target |
| 2977 | 1.659574 | 0.150000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 3.030492 | 0.004653 | 4.179887 | 0.010770 | 0.002577 | 0.012883 | pde_advection_proof_target |
| 5058 | 2.800532 | -1.450000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.006662 | 0.004880 | 4.185337 | 0.010271 | 0.002454 | 0.012270 | pde_advection_proof_target |
| 4549 | 2.537234 | -0.800000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 2.993981 | 0.005005 | 4.195127 | 0.010015 | 0.002387 | 0.011937 | pde_advection_proof_target |
| 2283 | 0.869681 | 1.650000 | support_edge_endpoint_junction | release_shift_fade | support_edge | 2.869696 | 0.006413 | 4.195989 | 0.007822 | 0.001864 | 0.009321 | pde_advection_proof_target |
| 4689 | 2.581117 | 1.850000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 3.002324 | 0.004922 | 4.201324 | 0.010183 | 0.002424 | 0.012119 | pde_advection_proof_target |
| 4464 | 2.493351 | -0.700000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 2.967231 | 0.005279 | 4.218777 | 0.009496 | 0.002251 | 0.011254 | pde_advection_proof_target |
| 2104 | 0.694149 | 1.350000 | support_edge_endpoint_junction | held_carry | support_edge | 2.767599 | 0.007860 | 4.231317 | 0.006387 | 0.001509 | 0.007547 | pde_advection_proof_target |
| 4774 | 2.625000 | 1.750000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 2.962218 | 0.005332 | 4.234469 | 0.009402 | 0.002220 | 0.011101 | pde_advection_proof_target |
| 4402 | 2.449468 | 0.500000 | reset_decompression_endpoint_junction | reset_decompression | core_throat | 2.938994 | 0.005585 | 4.247664 | 0.008977 | 0.002113 | 0.010567 | pde_advection_proof_target |
| 5045 | 2.800532 | -2.100000 | reset_decompression_endpoint_junction | reset_decompression | support_edge | 2.965105 | 0.005302 | 4.252260 | 0.009456 | 0.002224 | 0.011119 | pde_advection_proof_target |

## Interpretation

The full `O(1e-4)` bounded-rapidity source kick fits inside every local cone budget in this adversarial set. That argues against an immediate endpoint/support-edge design repair at this rung. The same rows do not have unlimited headroom: the `O(5e-4)` reference kick exceeds the tight reset-decompression/support-edge budgets, matching the reduced transport pilot's large-kick failure.

So the next spatial model should not simply prove abstract hyperbolicity. It should show that advection and support-source coupling never concentrate a larger effective rapidity kick into the tightest edge rows, or else add an explicit local limiter/smoothing term for the support source.

## Provenance

- point fit: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5/endpoint_support_stroke_exchange_point_fit.csv`
- selected rows: `56` dense watch/near-watch rows
- full table: `endpoint_support_rapidity_budget_rows.csv` in the run output directory
