# ADM harness report v5_service_carrying_flow_localizer

## Decision sheet
| run_name                           |   velocity | control_law_mode   | service_modifier_mode      | substrate_mode    |   max_abs_delta_rho_packet |   max_abs_delta_j_packet |   max_abs_delta_j_catch |   delta_j_catch_abs_burden |   delta_j_global_abs_burden |   support_shell_load_fraction |   catch_rematch_localization_fraction |   packet_exposure_score | passes_packet_rho_gate   | passes_packet_j_gate   | passes_catch_j_gate   | passes_support_shell_gate   | recommended_next_step   |   service_synthesis_enabled_modifiers | service_synthesis_modified_service_fields   | service_synthesis_modifiers                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|:-----------------------------------|-----------:|:-------------------|:---------------------------|:------------------|---------------------------:|-------------------------:|------------------------:|---------------------------:|----------------------------:|------------------------------:|--------------------------------------:|------------------------:|:-------------------------|:-----------------------|:----------------------|:----------------------------|:------------------------|--------------------------------------:|:--------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v5_service_carrying_flow_localizer |          5 | none               | compact_momentum_localizer | carrying_flow_off |                2.01274e-07 |              2.58064e-05 |             2.58064e-05 |                  0.0187953 |                   0.0214826 |                    0.00437588 |                              0.874908 |             2.95775e-06 | True                     | True                   | True                  | True                        | promote_or_compare      |                                     1 | ['carrying_flow']                           | [{'block': 'carrying_flow', 'service_field': 'carrying_flow', 'delta_name': 'delta_carrying_flow', 'law': 'compact_momentum_localizer', 'requested_law': 'compact_momentum_localizer', 'scope': 'catch_rematch_edge_support_mix', 'amplitude': 0.002, 'gain': 1.0, 'max_abs_change': 0.002, 'window_abs_sum': 3809.610206604004, 'window_max': 1.0, 'window_total_abs': 3809.610206604004, 'window_packet_edge_abs': 272.1868076324463, 'window_support_shell_abs': 3500.3147583007812, 'window_packet_live_abs': 277.48216438293457, 'window_packet_edge_fraction': 0.07144741663086876, 'window_support_shell_fraction': 0.9188117861068685, 'window_packet_live_fraction': 0.07283741625374585, 'min': -0.002, 'max': 4.448812716890929e-18, 'linf': 0.002, 'l1': 0.6502113510051645, 'nonzero_points': 1150}] |

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
| j_l       | packet_live       |     2552 |  0.171296    |     0.17099     |  0.000153009 |  0.171143    | 0.00377891  |   0.00377891  | -9.59647e-06 |                0.0785089 |
| j_l       | packet_core       |     1818 |  0.124191    |     0.124191    |  0           |  0.124191    | 0.00317268  |   0.00317268  |  2.84655e-06 |                0.0569196 |
| j_l       | packet_edge       |     1277 |  0.0837201   |     0.0834141   |  0.000153009 |  0.0835671   | 0.00377891  |   0.00377891  | -9.59647e-06 |                0.0383708 |
| j_l       | packet_edge_strip |      734 |  0.0471052   |     0.0467992   |  0.000153009 |  0.0469522   | 0.00377891  |   0.00377891  | -9.59647e-06 |                0.0215894 |
| delta_rho | packet_live       |     2552 |  3.9961e-05  |    -3.85887e-05 |  3.92748e-05 |  6.86168e-07 | 2.01274e-07 |   4.86907e-09 | -2.01274e-07 |                0.86131   |
| delta_rho | packet_core       |     1818 |  2.78088e-05 |    -2.66297e-05 |  2.72193e-05 |  5.89559e-07 | 2.0126e-07  |   4.52113e-09 | -2.0126e-07  |                0.599385  |
| delta_rho | packet_edge       |     1277 |  2.05271e-05 |    -1.9917e-05  |  2.0222e-05  |  3.05056e-07 | 2.01274e-07 |   4.86907e-09 | -2.01274e-07 |                0.442436  |
| delta_rho | packet_edge_strip |      734 |  1.21522e-05 |    -1.19589e-05 |  1.20556e-05 |  9.66089e-08 | 2.01274e-07 |   4.86907e-09 | -2.01274e-07 |                0.261925  |
| delta_j_l | packet_live       |     2552 |  0.0201629   |     0.0201629   |  0           |  0.0201629   | 2.58064e-05 |   2.58064e-05 |  8.1104e-07  |                0.938569  |
| delta_j_l | packet_core       |     1818 |  0.0153217   |     0.0153217   |  0           |  0.0153217   | 2.58064e-05 |   2.58064e-05 |  1.1647e-06  |                0.713216  |
| delta_j_l | packet_edge       |     1277 |  0.00932606  |     0.00932606  |  0           |  0.00932606  | 2.51792e-05 |   2.51792e-05 |  8.1104e-07  |                0.434122  |
| delta_j_l | packet_edge_strip |      734 |  0.00484116  |     0.00484116  |  0           |  0.00484116  | 2.36741e-05 |   2.36741e-05 |  8.1104e-07  |                0.225353  |

## Support shell load
| channel   |   points |   abs_burden |   signed_burden |   neg_burden |   pos_burden |    peak_abs |   peak_signed |   min_signed |   global_abs_burden |   support_shell_load_fraction |
|:----------|---------:|-------------:|----------------:|-------------:|-------------:|------------:|--------------:|-------------:|--------------------:|------------------------------:|
| rho       |    10164 |  8.65374     |     8.64119     |  0.00627632  |  8.64746     | 0.00884973  |   0.00884973  | -0.00475752  |        49.928       |                    0.173324   |
| j_l       |    10164 |  1.15927     |     9.40052e-05 |  0.579589    |  0.579683    | 0.0204849   |   0.0204849   | -0.0204848   |         2.18187     |                    0.53132    |
| delta_rho |    10164 |  3.32752e-06 |    -3.29336e-06 |  3.31044e-06 |  1.70786e-08 | 2.01199e-07 |   1.35715e-08 | -2.01199e-07 |         4.63956e-05 |                    0.0717205  |
| delta_j_l |    10164 |  9.40052e-05 |     9.40052e-05 |  3.51841e-14 |  9.40052e-05 | 8.87766e-06 |   8.87766e-06 | -1.32533e-14 |         0.0214826   |                    0.00437588 |

## Catch/rematch localization
| channel   |   catch_abs_burden |   catch_points |   catch_fraction_of_global_abs |   catch_packet_abs_burden |   catch_packet_fraction_of_global_abs |   catch_support_abs_burden |   catch_support_fraction_of_global_abs |   peak_abs_in_catch |
|:----------|-------------------:|---------------:|-------------------------------:|--------------------------:|--------------------------------------:|---------------------------:|---------------------------------------:|--------------------:|
| rho       |       36.1857      |          10122 |                       0.724758 |              10.3941      |                             0.208181  |                5.98635     |                            0.1199      |         0.0124429   |
| j_l       |        0.233099    |          10122 |                       0.106834 |               0.025418    |                             0.0116497 |                0.125723    |                            0.0576216   |         0.00275304  |
| delta_rho |        1.08663e-05 |          10122 |                       0.23421  |               8.95294e-06 |                             0.19297   |                3.58357e-16 |                            7.72393e-12 |         7.00203e-08 |
| delta_j_l |        0.0187953   |          10122 |                       0.874908 |               0.0176796   |                             0.822973  |                3.77871e-14 |                            1.75897e-12 |         2.58064e-05 |

## Status
```json
{
  "caveats": [],
  "control_law_mode": "none",
  "exact_fields": "/home/kir/Downloads/active_rail_final_refreeze_source_track_record_bundle/active-rail-refined-design-base/toolkit/adm_harness_cli/data/sample_v5/exact_builder_adm_v5/adm_exact_fields_V5p0.npz",
  "exact_point_ledger": "/home/kir/Downloads/active_rail_final_refreeze_source_track_record_bundle/active-rail-refined-design-base/toolkit/adm_harness_cli/data/sample_v5/exact_builder_adm_v5/adm_exact_point_ledger_v5_v10.csv",
  "identity_self_check_passed": true,
  "outputs": [
    "catch_rematch_localization.csv",
    "decision_sheet.csv",
    "field_delta_metadata.json",
    "field_delta_summary.csv",
    "packet_exposure.csv",
    "peak_locations.csv",
    "point_ledger.csv",
    "scope_burden.csv",
    "service_modifier_summary.csv",
    "stage_region_burden.csv",
    "support_shell_load.csv"
  ],
  "rows": 29161,
  "run_name": "v5_service_carrying_flow_localizer",
  "service_modifier_mode": "compact_momentum_localizer",
  "service_modifiers": [
    "carrying_flow"
  ],
  "substrate_fields": "/home/kir/Downloads/active_rail_final_refreeze_source_track_record_bundle/active-rail-refined-design-base/toolkit/adm_harness_cli/data/sample_v5/substrate_subtraction_fields_v5.npz",
  "substrate_mode": "carrying_flow_off",
  "synthesis_enabled": true,
  "velocity": 5.0
}
```

## Notes
Whole-service synthesis is active when `synthesis.enabled` is true. Catch/rematch control laws are treated as service modifiers; sidecar-only control metrics are only used when synthesis is disabled.
