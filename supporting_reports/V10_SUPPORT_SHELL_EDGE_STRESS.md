# V10 Support-Shell Target Edge Stress

## Scope

This run promotes the preferred V5 support-shell-bearing ansatz to the V = 10 edge case:

- service field: `carrying_flow`
- law: `windowed_adjustment`
- scope: `catch_rematch_support_shell`
- catch lead: `0.75`
- temporal width: `0.5`
- target amplitude: `1.0e-7`

The run uses the actual V10 exact fields and V10 substrate subtraction fields extracted from the tracked source bundles:

- `toolkit/adm_harness_cli/data/sample_v5/exact_builder_adm_v5/adm_exact_fields_V10p0.npz`
- `toolkit/adm_harness_cli/data/sample_v5/substrate_subtraction_fields_v10.npz`

This matters because setting `velocity: 10.0` alone is not sufficient in the harness: the runner filters the point ledger by velocity, but field channels are taken from the configured NPZ field file.

## Method

The reusable harness entry point is:

`toolkit/adm_harness_cli/run_v10_support_shell_edge.sh`

It runs:

1. `v10_service_flow_off` as the V10 edge baseline.
2. `v10_support_shell_window_target` as the promoted target.
3. A focused stress family around the target:
   - amplitude: `5e-8` through `2.5e-6`
   - catch lead: `0.0` through `1.25`
   - temporal width: `0.25` through `1.0`
   - both signs, because the prior V5 direct-window result was sign-symmetric at tiny amplitude.

The scoring compares each run pointwise against `v10_service_flow_off` before aggregating incremental burdens. The preferred score rewards incremental `delta_j_l` landing in catch/rematch support-shell infrastructure and penalizes packet-live momentum, packet `delta_rho`, and excessive added global burden.

## Main Result

The support-shell target survives the V10 edge stress.

The promoted target row:

| run | global abs incremental `delta_j_l` | catch-support fraction | packet `delta_j_l` fraction | packet abs incremental `delta_rho` | fraction of baseline V10 global `delta_j_l` |
|---|---:|---:|---:|---:|---:|
| `v10_support_shell_window_target` | `1.230138e-07` | `0.992775` | `1.431529e-07` | `5.605264e-17` | `3.21306e-06` |

The V10 baseline itself has global abs `delta_j_l` burden `3.82855863634e-02`. The target therefore adds only a tiny controlled support-shell perturbation, not a full redistribution of the V10 handoff burden.

Baseline and target both pass the configured packet gates:

| run | max packet `delta_rho` | max packet `delta_j_l` | catch localization |
|---|---:|---:|---:|
| `v10_service_flow_off` | `2.731433e-07` | `5.126346e-05` | `0.924414` |
| `v10_support_shell_window_target` | `2.731433e-07` | `5.126346e-05` | `0.924415` |

## Best Stress Variants

The best ranked stress rows are narrower or slightly later than the promoted target, but the differences are small and all preserve the same qualitative pattern:

| rank | run | global abs incremental `delta_j_l` | catch-support fraction | packet `delta_j_l` fraction | packet abs incremental `delta_rho` |
|---:|---|---:|---:|---:|---:|
| 1 | `tw_neg_0p25` | `4.319332e-08` | `0.992809` | `4.076969e-07` | `5.605264e-17` |
| 2 | `tw_pos_0p25` | `4.319332e-08` | `0.992809` | `4.076969e-07` | `5.605264e-17` |
| 3 | `amp_neg_5em08` | `6.150701e-08` | `0.992773` | `2.863053e-07` | `5.605264e-17` |
| 4 | `amp_pos_5em08` | `6.150701e-08` | `0.992773` | `2.863053e-07` | `5.605264e-17` |
| 5 | `lead_neg_1p25` | `7.623138e-08` | `0.992867` | `2.310044e-07` | `5.605264e-17` |
| 6 | `lead_pos_1p25` | `7.623138e-08` | `0.992867` | `2.310044e-07` | `5.605264e-17` |

The sign symmetry persists at V10. Positive and negative twins have indistinguishable burden routing at the tested amplitudes.

## Interpretation

The answer to the V10 survival question is yes in the support-placement sense: a direct support-shell window can be applied at the V10 edge while keeping packet `delta_rho` quiet and routing more than 99.27% of its incremental `delta_j_l` into the catch/rematch support-shell infrastructure.

The answer is not yet yes in the stronger load-bearing sense. At amplitude `1e-7`, the target is only about `3.21e-6` of the V10 baseline global `delta_j_l` burden. This is a stable, controllable support-shell channel, not a complete rerouting of the hard V10 handoff load.

The best next design move is to keep the direct support-shell window as the target ansatz, but split the next test into two branches:

- a conservative branch near `amplitude = 5e-8` to `1e-7`, `temporal_width = 0.25` to `0.5`, `catch_lead = 0.75` to `1.25`, for clean edge-rated control placement;
- a load-bearing branch that ramps amplitude beyond the current tiny-control range and asks where packet gates, field validation, or support-shell score first degrade.

## Files

- Result bundle: `toolkit/adm_harness_cli/v10_support_shell_edge_results.zip`
- Routing summary: `toolkit/adm_harness_cli/runs/v10_support_shell_edge/v10_support_shell_edge_summary.csv`
- Run report: `toolkit/adm_harness_cli/runs/v10_support_shell_edge/v10_support_shell_edge_report.md`
