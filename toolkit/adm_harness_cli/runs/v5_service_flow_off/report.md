# ADM harness report v5_service_flow_off

## Decision sheet
| run_name            |   velocity | control_law_mode   | service_modifier_mode   | substrate_mode    |   max_abs_delta_rho_packet |   max_abs_delta_j_packet |   max_abs_delta_j_catch |   delta_j_catch_abs_burden |   delta_j_global_abs_burden |   support_shell_load_fraction |   catch_rematch_localization_fraction |   packet_exposure_score | passes_packet_rho_gate   | passes_packet_j_gate   | passes_catch_j_gate   | passes_support_shell_gate   | recommended_next_step   |
|:--------------------|-----------:|:-------------------|:------------------------|:------------------|---------------------------:|-------------------------:|------------------------:|---------------------------:|----------------------------:|------------------------------:|--------------------------------------:|------------------------:|:-------------------------|:-----------------------|:----------------------|:----------------------------|:------------------------|
| v5_service_flow_off |          5 | none               | none                    | carrying_flow_off |                2.01274e-07 |              2.58064e-05 |             2.58064e-05 |                  0.0187594 |                   0.0214467 |                     0.0043832 |                                0.8747 |             2.95467e-06 | True                     | True                   | True                  | True                        | promote_or_compare      |

## Peak locations
| channel   |    peak_abs |   signed_value |         s |        l | stage               | region                 | inside_packet_live   | packet_edge   | support_shell   |
|:----------|------------:|---------------:|----------:|---------:|:--------------------|:-----------------------|:---------------------|:--------------|:----------------|
| rho       | 0.0124429   |   -0.0124429   | -0.35     | -2.59    | catch_rematch       | outer_quarantine_shell | False                | False         | False           |
| j_l       | 0.0204849   |    0.0204849   |  1.65     |  1.51667 | reset_decompression | packet_in_support      | False                | False         | True            |
| delta_rho | 2.01274e-07 |   -2.01274e-07 |  0.866667 |  1.12    | release_shift_fade  | packet_in_support      | True                 | True          | False           |
| delta_j_l | 2.58064e-05 |    2.58064e-05 | -0.35     | -0.35    | catch_rematch       | packet_in_support      | True                 | False         | False           |

## Packet exposure
| channel   | scope             |   points |   abs_burden |   signed_burden |   neg_burden |   pos_burden |    peak_abs |   peak_signed |   min_signed |   fraction_of_global_abs |
|:----------|:------------------|---------:|-------------:|----------------:|-------------:|-------------:|------------:|--------------:|-------------:|-------------------------:|
| rho       | packet_live       |     2552 | 13.5106      |    13.5106      |  0           | 13.5106      | 0.00953223  |   0.00953223  |  0.00622013  |                0.270602  |
| rho       | packet_core       |     1818 |  9.68034     |     9.68034     |  0           |  9.68034     | 0.00952842  |   0.00952842  |  0.00658223  |                0.193886  |
| rho       | packet_edge       |     1277 |  6.6963      |     6.6963      |  0           |  6.6963      | 0.00953223  |   0.00953223  |  0.00622013  |                0.134119  |
| rho       | packet_edge_strip |      734 |  3.83029     |     3.83029     |  0           |  3.83029     | 0.00953223  |   0.00953223  |  0.00622013  |                0.0767163 |
| j_l       | packet_live       |     2552 |  0.171264    |     0.170955    |  0.000154402 |  0.17111     | 0.00377891  |   0.00377891  | -9.61766e-06 |                0.0784954 |
| j_l       | packet_core       |     1818 |  0.124174    |     0.124174    |  0           |  0.124174    | 0.00317268  |   0.00317268  |  2.7793e-06  |                0.0569127 |
| j_l       | packet_edge       |     1277 |  0.0836902   |     0.0833814   |  0.000154402 |  0.0835358   | 0.00377891  |   0.00377891  | -9.61766e-06 |                0.0383577 |
| j_l       | packet_edge_strip |      734 |  0.04709     |     0.0467812   |  0.000154402 |  0.0469356   | 0.00377891  |   0.00377891  | -9.61766e-06 |                0.0215827 |
| delta_rho | packet_live       |     2552 |  3.99195e-05 |    -3.85627e-05 |  3.92411e-05 |  6.7843e-07  | 2.01274e-07 |   4.82653e-09 | -2.01274e-07 |                0.861292  |
| delta_rho | packet_core       |     1818 |  2.78186e-05 |    -2.66551e-05 |  2.72368e-05 |  5.81772e-07 | 2.0126e-07  |   4.33863e-09 | -2.0126e-07  |                0.600206  |
| delta_rho | packet_edge       |     1277 |  2.04801e-05 |    -1.98802e-05 |  2.01802e-05 |  2.99967e-07 | 2.01274e-07 |   4.82653e-09 | -2.01274e-07 |                0.441873  |
| delta_rho | packet_edge_strip |      734 |  1.21009e-05 |    -1.19076e-05 |  1.20043e-05 |  9.66587e-08 | 2.01274e-07 |   4.82653e-09 | -2.01274e-07 |                0.261086  |
| delta_j_l | packet_live       |     2552 |  0.0201281   |     0.0201281   |  0           |  0.0201281   | 2.58064e-05 |   2.58064e-05 |  8.1104e-07  |                0.938516  |
| delta_j_l | packet_core       |     1818 |  0.0153049   |     0.0153049   |  0           |  0.0153049   | 2.58064e-05 |   2.58064e-05 |  1.1647e-06  |                0.713623  |
| delta_j_l | packet_edge       |     1277 |  0.00929335  |     0.00929335  |  0           |  0.00929335  | 2.51265e-05 |   2.51265e-05 |  8.1104e-07  |                0.433323  |
| delta_j_l | packet_edge_strip |      734 |  0.0048232   |     0.0048232   |  0           |  0.0048232   | 2.35735e-05 |   2.35735e-05 |  8.1104e-07  |                0.224892  |

## Support shell load
| channel   |   points |   abs_burden |   signed_burden |   neg_burden |   pos_burden |    peak_abs |   peak_signed |   min_signed |   global_abs_burden |   support_shell_load_fraction |
|:----------|---------:|-------------:|----------------:|-------------:|-------------:|------------:|--------------:|-------------:|--------------------:|------------------------------:|
| rho       |    10164 |  8.65374     |     8.64119     |  0.00627632  |  8.64746     | 0.00884973  |   0.00884973  | -0.00475752  |        49.928       |                     0.173324  |
| j_l       |    10164 |  1.15927     |     9.40052e-05 |  0.579589    |  0.579683    | 0.0204849   |   0.0204849   | -0.0204848   |         2.18184     |                     0.531328  |
| delta_rho |    10164 |  3.32752e-06 |    -3.29336e-06 |  3.31044e-06 |  1.70786e-08 | 2.01199e-07 |   1.35715e-08 | -2.01199e-07 |         4.63484e-05 |                     0.0717935 |
| delta_j_l |    10164 |  9.40052e-05 |     9.40052e-05 |  4.25344e-19 |  9.40052e-05 | 8.87766e-06 |   8.87766e-06 | -3.46945e-18 |         0.0214467   |                     0.0043832 |

## Catch/rematch localization
| channel   |   catch_abs_burden |   catch_points |   catch_fraction_of_global_abs |   catch_packet_abs_burden |   catch_packet_fraction_of_global_abs |   catch_support_abs_burden |   catch_support_fraction_of_global_abs |   peak_abs_in_catch |
|:----------|-------------------:|---------------:|-------------------------------:|--------------------------:|--------------------------------------:|---------------------------:|---------------------------------------:|--------------------:|
| rho       |       36.1857      |          10122 |                       0.724758 |              10.3941      |                             0.208181  |                5.98635     |                            0.1199      |         0.0124429   |
| j_l       |        0.233066    |          10122 |                       0.106821 |               0.025386    |                             0.0116352 |                0.125723    |                            0.0576224   |         0.00275304  |
| delta_rho |        1.08192e-05 |          10122 |                       0.233432 |               8.91153e-06 |                             0.192273  |                0           |                            0           |         6.92083e-08 |
| delta_j_l |        0.0187594   |          10122 |                       0.8747   |               0.0176448   |                             0.822728  |                7.56539e-15 |                            3.52753e-13 |         2.58064e-05 |

## Status
```json
{
  "caveats": [],
  "control_law_mode": "none",
  "exact_fields": "/home/kir/Downloads/active_rail_final_refreeze_source_track_record_bundle/active-rail-refined-design-base/toolkit/adm_harness_cli/data/sample_v5/exact_builder_adm_v5/adm_exact_fields_V5p0.npz",
  "exact_point_ledger": "/home/kir/Downloads/active_rail_final_refreeze_source_track_record_bundle/active-rail-refined-design-base/toolkit/adm_harness_cli/data/sample_v5/exact_builder_adm_v5/adm_exact_point_ledger_v5_v10.csv",
  "outputs": [
    "catch_rematch_localization.csv",
    "decision_sheet.csv",
    "packet_exposure.csv",
    "peak_locations.csv",
    "point_ledger.csv",
    "scope_burden.csv",
    "stage_region_burden.csv",
    "support_shell_load.csv"
  ],
  "rows": 29161,
  "run_name": "v5_service_flow_off",
  "service_modifier_mode": "none",
  "service_modifiers": [],
  "substrate_fields": "/home/kir/Downloads/active_rail_final_refreeze_source_track_record_bundle/active-rail-refined-design-base/toolkit/adm_harness_cli/data/sample_v5/substrate_subtraction_fields_v5.npz",
  "substrate_mode": "carrying_flow_off",
  "synthesis_enabled": false,
  "velocity": 5.0
}
```

## Notes
Whole-service synthesis is active when `synthesis.enabled` is true. Catch/rematch control laws are treated as service modifiers; sidecar-only control metrics are only used when synthesis is disabled.
