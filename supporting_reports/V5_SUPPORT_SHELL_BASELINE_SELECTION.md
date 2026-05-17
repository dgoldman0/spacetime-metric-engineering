# V5 Support-Shell Baseline Selection

## Scope

This is the V5 baseline counterpart to the V10 support-shell edge stress report. V5 is the primary target-selection case; V10 is only the edge-survival check.

The screen asks which support-shell-bearing ansatz should be promoted from the V5 baseline:

- baseline: `v5_service_flow_off`
- preferred family: direct `windowed_adjustment`
- service field: `carrying_flow`
- scope: `catch_rematch_support_shell`
- default target: `window_pos_a1em07_lead0p75`

This report is intentionally narrower than `V5_SUPPORT_SHELL_ANSATZ_SCREEN.md`: it records the selected target in the same compact style as the V10 edge report.

## Method

The V5 support-shell screen was run by:

`toolkit/adm_harness_cli/run_v5_support_shell_screen.sh`

It compares each variant pointwise against `v5_service_flow_off` before aggregating incremental burden. The preferred routing objective rewards incremental `delta_j_l` in catch/rematch support-shell infrastructure and penalizes packet-live momentum, packet `delta_rho`, and excess global added burden.

## Main Result

The direct support-shell window is the V5 baseline selection.

The selected target:

| run | global abs incremental `delta_j_l` | catch-support fraction | support fraction | packet `delta_j_l` fraction | packet abs incremental `delta_rho` |
|---|---:|---:|---:|---:|---:|
| `window_pos_a1em07_lead0p75` | `1.230138e-07` | `0.992775` | `0.992811` | `1.382323e-07` | `5.442060e-16` |

The V5 flow-off baseline and selected target both pass the configured packet gates:

| run | max packet `delta_rho` | max packet `delta_j_l` | catch localization | support-shell fraction |
|---|---:|---:|---:|---:|
| `v5_service_flow_off` | `2.012739e-07` | `2.580641e-05` | `0.874700` | `0.004383` |
| `window_pos_a1em07_lead0p75` | `2.012739e-07` | `2.580641e-05` | `0.874701` | `0.004389` |

The target adds only a tiny controlled support-shell perturbation relative to the baseline global `delta_j_l` burden of `2.14466987967e-02`. The point is not to claim full load-bearing reroute yet; it is to select the support-shell control placement that is stable, packet quiet, and cleanly localized.

## Top Routing Rows

The top rows are all direct support-shell windows. Positive and negative signs are effectively tied by the absolute routing score:

| rank | run | global abs incremental `delta_j_l` | catch-support fraction | support fraction | packet `delta_j_l` fraction | packet abs incremental `delta_rho` |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `window_neg_a1em07_lead0p75` | `1.230138e-07` | `0.992775` | `0.992811` | `1.382323e-07` | `5.442060e-16` |
| 2 | `window_pos_a1em07_lead0p75` | `1.230138e-07` | `0.992775` | `0.992811` | `1.382323e-07` | `5.442060e-16` |
| 3 | `window_neg_a1em07_lead0p5` | `1.660666e-07` | `0.992578` | `0.992680` | `1.023955e-07` | `5.442060e-16` |
| 4 | `window_pos_a1em07_lead0p5` | `1.660666e-07` | `0.992578` | `0.992680` | `1.023955e-07` | `5.442060e-16` |
| 5 | `window_neg_a2p5em07_lead0p75` | `3.075341e-07` | `0.992776` | `0.992812` | `5.529298e-08` | `5.442060e-16` |
| 6 | `window_pos_a2p5em07_lead0p75` | `3.075341e-07` | `0.992776` | `0.992812` | `5.529298e-08` | `5.442060e-16` |

## Interpretation

V5 selects the direct support-shell window as the preferred ansatz. The current best target is:

```text
law: windowed_adjustment
target_service_field: carrying_flow
scope: catch_rematch_support_shell
amplitude: +1e-7
catch_lead: 0.75
temporal_width: 0.5
```

The `+1e-7` sign is not selected by the absolute routing objective; it is selected only as a signed-objective tie-breaker. The routing result itself says the support-shell placement is robust and packet quiet, while sign remains nearly symmetric at this amplitude.

## Output Files

- `toolkit/adm_harness_cli/runs/v5_support_shell_screen/support_shell_routing_summary.csv`
- `toolkit/adm_harness_cli/runs/v5_support_shell_screen/support_shell_routing_report.md`
- `toolkit/adm_harness_cli/v5_support_shell_results.zip`
