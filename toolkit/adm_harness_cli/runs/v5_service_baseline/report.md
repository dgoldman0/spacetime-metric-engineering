# ADM harness report v5_service_baseline

## Decision sheet
| run_name            |   velocity | control_law_mode   | service_modifier_mode   | substrate_mode   |   max_abs_delta_rho_packet |   max_abs_delta_j_packet |   max_abs_delta_j_catch |   delta_j_catch_abs_burden |   delta_j_global_abs_burden |   support_shell_load_fraction |   catch_rematch_localization_fraction |   packet_exposure_score | passes_packet_rho_gate   | passes_packet_j_gate   | passes_catch_j_gate   | passes_support_shell_gate   | recommended_next_step   |
|:--------------------|-----------:|:-------------------|:------------------------|:-----------------|---------------------------:|-------------------------:|------------------------:|---------------------------:|----------------------------:|------------------------------:|--------------------------------------:|------------------------:|:-------------------------|:-----------------------|:----------------------|:----------------------------|:------------------------|
| v5_service_baseline |          5 | none               | none                    | none             |                          0 |                        0 |                       0 |                          0 |                           0 |                             0 |                                     0 |                       0 | True                     | True                   | True                  | True                        | promote_or_compare      |

## Peak locations
| channel   |   peak_abs |   signed_value |     s |        l | stage               | region                 | inside_packet_live   | packet_edge   | support_shell   |
|:----------|-----------:|---------------:|------:|---------:|:--------------------|:-----------------------|:---------------------|:--------------|:----------------|
| rho       |  0.0124429 |     -0.0124429 | -0.35 | -2.59    | catch_rematch       | outer_quarantine_shell | False                | False         | False           |
| j_l       |  0.0204849 |      0.0204849 |  1.65 |  1.51667 | reset_decompression | packet_in_support      | False                | False         | False           |
| delta_rho |  0         |      0         | -0.35 | -2.8     | catch_rematch       | outer_quarantine_shell | False                | False         | False           |
| delta_j_l |  0         |      0         | -0.35 | -2.8     | catch_rematch       | outer_quarantine_shell | False                | False         | False           |

## Packet exposure
| channel   | scope             |   points |   abs_burden |   signed_burden |   neg_burden |   pos_burden |   peak_abs |   peak_signed |   min_signed |   fraction_of_global_abs |
|:----------|:------------------|---------:|-------------:|----------------:|-------------:|-------------:|-----------:|--------------:|-------------:|-------------------------:|
| rho       | packet_live       |     2552 |    13.5106   |      13.5106    |  0           |   13.5106    | 0.00953223 |    0.00953223 |  0.00622013  |                0.270602  |
| rho       | packet_core       |     1818 |     9.68034  |       9.68034   |  0           |    9.68034   | 0.00952842 |    0.00952842 |  0.00658223  |                0.193886  |
| rho       | packet_edge       |      734 |     3.83029  |       3.83029   |  0           |    3.83029   | 0.00953223 |    0.00953223 |  0.00622013  |                0.0767163 |
| rho       | packet_edge_strip |      734 |     3.83029  |       3.83029   |  0           |    3.83029   | 0.00953223 |    0.00953223 |  0.00622013  |                0.0767163 |
| j_l       | packet_live       |     2552 |     0.171264 |       0.170955  |  0.000154402 |    0.17111   | 0.00377891 |    0.00377891 | -9.61766e-06 |                0.0784954 |
| j_l       | packet_core       |     1818 |     0.124174 |       0.124174  |  0           |    0.124174  | 0.00317268 |    0.00317268 |  2.7793e-06  |                0.0569127 |
| j_l       | packet_edge       |      734 |     0.04709  |       0.0467812 |  0.000154402 |    0.0469356 | 0.00377891 |    0.00377891 | -9.61766e-06 |                0.0215827 |
| j_l       | packet_edge_strip |      734 |     0.04709  |       0.0467812 |  0.000154402 |    0.0469356 | 0.00377891 |    0.00377891 | -9.61766e-06 |                0.0215827 |
| delta_rho | packet_live       |     2552 |     0        |       0         |  0           |    0         | 0          |    0          |  0           |                0         |
| delta_rho | packet_core       |     1818 |     0        |       0         |  0           |    0         | 0          |    0          |  0           |                0         |
| delta_rho | packet_edge       |      734 |     0        |       0         |  0           |    0         | 0          |    0          |  0           |                0         |
| delta_rho | packet_edge_strip |      734 |     0        |       0         |  0           |    0         | 0          |    0          |  0           |                0         |
| delta_j_l | packet_live       |     2552 |     0        |       0         |  0           |    0         | 0          |    0          |  0           |                0         |
| delta_j_l | packet_core       |     1818 |     0        |       0         |  0           |    0         | 0          |    0          |  0           |                0         |
| delta_j_l | packet_edge       |      734 |     0        |       0         |  0           |    0         | 0          |    0          |  0           |                0         |
| delta_j_l | packet_edge_strip |      734 |     0        |       0         |  0           |    0         | 0          |    0          |  0           |                0         |

## Support shell load
| channel   |   points |   abs_burden |   signed_burden |   neg_burden |   pos_burden |   peak_abs |   peak_signed |   min_signed |   global_abs_burden |   support_shell_load_fraction |
|:----------|---------:|-------------:|----------------:|-------------:|-------------:|-----------:|--------------:|-------------:|--------------------:|------------------------------:|
| rho       |        0 |            0 |               0 |            0 |            0 |        nan |           nan |          nan |            49.928   |                             0 |
| j_l       |        0 |            0 |               0 |            0 |            0 |        nan |           nan |          nan |             2.18184 |                             0 |
| delta_rho |        0 |            0 |               0 |            0 |            0 |        nan |           nan |          nan |             0       |                             0 |
| delta_j_l |        0 |            0 |               0 |            0 |            0 |        nan |           nan |          nan |             0       |                             0 |

## Catch/rematch localization
| channel   |   catch_abs_burden |   catch_points |   catch_fraction_of_global_abs |   catch_packet_abs_burden |   catch_packet_fraction_of_global_abs |   catch_support_abs_burden |   catch_support_fraction_of_global_abs |   peak_abs_in_catch |
|:----------|-------------------:|---------------:|-------------------------------:|--------------------------:|--------------------------------------:|---------------------------:|---------------------------------------:|--------------------:|
| rho       |          36.1857   |          10122 |                       0.724758 |                 10.3941   |                             0.208181  |                          0 |                                      0 |          0.0124429  |
| j_l       |           0.233066 |          10122 |                       0.106821 |                  0.025386 |                             0.0116352 |                          0 |                                      0 |          0.00275304 |
| delta_rho |           0        |          10122 |                       0        |                  0        |                             0         |                          0 |                                      0 |          0          |
| delta_j_l |           0        |          10122 |                       0        |                  0        |                             0         |                          0 |                                      0 |          0          |

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
  "run_name": "v5_service_baseline",
  "service_modifier_mode": "none",
  "service_modifiers": [],
  "substrate_fields": null,
  "substrate_mode": "none",
  "synthesis_enabled": false,
  "velocity": 5.0
}
```

## Notes
Whole-service synthesis is active when `synthesis.enabled` is true. Catch/rematch control laws are treated as service modifiers; sidecar-only control metrics are only used when synthesis is disabled.
