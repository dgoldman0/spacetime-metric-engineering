# Active Rail Lifecycle Ledger Report

Mode: `region_phase`
Case: `soft_minjerk_q_t0m04_Tr30`

## Lifecycle accounting

Passenger exposure is counted through the live packet stages and stops before decompression/reset unless `count_reset_as_packet_exposure` is enabled.

```json
{
  "Rpass": 0.35,
  "Rth": 1.75,
  "x_entry": -0.35,
  "x_catch": 0.15,
  "x_beta": 0.7,
  "x_release": 1.06,
  "x_q": 1.25,
  "w_entry": 0.12,
  "w_catch": 0.16,
  "w_beta": 0.18,
  "w_release": 0.16,
  "w_q": 0.18,
  "include_entry_as_live": true,
  "include_release_as_live": true,
  "count_reset_as_packet_exposure": false,
  "packet_center_mode": "diagonal"
}
```

## Lifecycle rollup

| stage               | packet_live_accounting   |   packet_neg_rho_peak_badness |   all_neg_rho_peak_badness |   support_shell_neg_rho_peak_badness |   packet_neg_rho_pkt_peak_badness |   all_neg_rho_pkt_peak_badness |   support_shell_neg_rho_pkt_peak_badness |   packet_neg_Tkk_peak_badness |   all_neg_Tkk_peak_badness |   support_shell_neg_Tkk_peak_badness |   packet_abs_p_l_peak_badness |   all_abs_p_l_peak_badness |   support_shell_abs_p_l_peak_badness |   packet_abs_pOmega_peak_badness |   all_abs_pOmega_peak_badness |   support_shell_abs_pOmega_peak_badness |   packet_abs_j_l_peak_badness |   all_abs_j_l_peak_badness |   support_shell_abs_j_l_peak_badness |
|:--------------------|:-------------------------|------------------------------:|---------------------------:|-------------------------------------:|----------------------------------:|-------------------------------:|-----------------------------------------:|------------------------------:|---------------------------:|-------------------------------------:|------------------------------:|---------------------------:|-------------------------------------:|---------------------------------:|------------------------------:|----------------------------------------:|------------------------------:|---------------------------:|-------------------------------------:|
| entry_pre_catch     | True                     |                      0        |                   0.027982 |                             0.027982 |                          0        |                       0        |                               nan        |                      0.201942 |                   0.290399 |                             0.290399 |                      0.014    |                   0.032267 |                             0.032267 |                         1.4e-05  |                      1.30866  |                                1.30866  |                      9.4e-05  |                   0.000627 |                             0.000627 |
| catch_rematch       | True                     |                      0        |                   0.027977 |                             0.027977 |                          0        |                       0.098056 |                                 0.098056 |                      0.190617 |                   0.283621 |                             0.283621 |                      0.014015 |                   0.032149 |                             0.032149 |                         1.4e-05  |                      1.30582  |                                1.30582  |                      0.000113 |                   0.000975 |                             0.000975 |
| held_transport      | True                     |                      0        |                   0.027797 |                             0.027797 |                          0        |                      16.9513   |                                16.9513   |                      0.089217 |                   0.25211  |                             0.25211  |                      0.014013 |                   0.031558 |                             0.031558 |                         3.7e-05  |                      1.27961  |                                1.27961  |                      0.000469 |                   0.001227 |                             0.001227 |
| shift_fade_release  | True                     |                      0.026295 |                   0.026939 |                             0.026939 |                          0.041223 |                       0.043282 |                                 0.043282 |                      0.162207 |                   0.199801 |                             0.199801 |                      0.029283 |                   0.031056 |                             0.031056 |                         1.05431  |                      1.2065   |                                1.2065   |                      0.005207 |                   0.005584 |                             0.003972 |
| decompression_reset | False                    |                      0.026054 |                   0.026054 |                             0.026054 |                          0.041288 |                       0.049995 |                                 0.046327 |                      0.135279 |                   0.135281 |                             0.135281 |                      0.027219 |                   0.048666 |                             0.027219 |                         0.957389 |                      0.957389 |                                0.957389 |                      0.014105 |                   0.044449 |                             0.037607 |
| reset_tail          | False                    |                      0.002388 |                   0.025828 |                             0.00694  |                          0.004836 |                       0.049802 |                                 0.016879 |                      0.00581  |                   0.071871 |                             0.033476 |                      0.001889 |                   0.045969 |                             0.022292 |                         0.001727 |                      0.023356 |                                0.0059   |                      0.000767 |                   0.006006 |                             0.006006 |

## Live packet vs reset-removed peak comparison

| channel     |   live_packet_peak |   reset_removed_peak |   geometric_packet_peak |   live_over_geometric_peak |   reset_removed_over_geometric_peak |
|:------------|-------------------:|---------------------:|------------------------:|---------------------------:|------------------------------------:|
| neg_rho     |           0.026295 |             0.026054 |                0.026295 |                   1        |                            0.990838 |
| neg_rho_pkt |           0.041223 |             0.041288 |                0.041288 |                   0.998431 |                            1        |
| neg_Tkk     |           0.201942 |             0.135279 |                0.201942 |                   1        |                            0.669889 |
| abs_p_l     |           0.029283 |             0.027219 |                0.029283 |                   1        |                            0.929505 |
| abs_pOmega  |           1.05431  |             0.957389 |                1.05431  |                   1        |                            0.908072 |
| abs_j_l     |           0.005207 |             0.014105 |                0.014105 |                   0.369189 |                            1        |

## Candidate tradeoff readthrough

| candidate         |   max_score_lower_better |   max_live_Tkk_fraction |   Tkk_fraction_cut_vs_freeze |   max_live_radial_pressure_fraction |   radial_pressure_fraction_cut_vs_freeze |   mean_total_Tkk_burden |   Tkk_burden_ratio_vs_freeze |   mean_total_pOmega_burden |   worst_packet_norm |
|:------------------|-------------------------:|------------------------:|-----------------------------:|------------------------------------:|-----------------------------------------:|------------------------:|-----------------------------:|---------------------------:|--------------------:|
| R2p0_quarantine   |                  1.11379 |                0.229202 |                     0.17938  |                            0.212971 |                                 0.089249 |                162707   |                      1.77214 |                    2804.16 |         -1129.07    |
| R1p75_quarantine  |                  1.31419 |                0.272578 |                     0.136005 |                            0.24928  |                                 0.05294  |                131774   |                      1.43523 |                    2094.75 |          -726.991   |
| broad_packet_edge |                  1.78972 |                0.3711   |                     0.037482 |                            0.337905 |                                -0.035685 |                 92853.4 |                      1.01132 |                    1327.02 |           -18.0044  |
| freeze            |                  1.80214 |                0.408582 |                     0        |                            0.30222  |                                 0        |                 91813.9 |                      1       |                    1699.49 |            -8.55547 |

## Caveat

This run used region/phase peaks, not the missing point-level tensor ledger. Treat it as a lifecycle-resolved peak diagnostic, not a volume-integrated exposure proof.