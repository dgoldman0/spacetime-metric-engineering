# V5 Support-Shell Final Freeze

This report freezes the reduced ADM support-shell control target before moving to the heavier tests. The design object is the support-shell-bearing control ansatz on the selected V5 shaped-catch/radial-soft/lapse-cushion branch, not a new geometry family and not a source-feasibility claim.

## Frozen Target

```text
law: windowed_adjustment
scope: catch_rematch_support_shell
allocation_mode: support_shell
target_service_field: carrying_flow
amplitude: +1e-7
max_abs_change: 1e-7
catch_lead: 1.0
temporal_width: 0.35
smoothness_order: 1
packet_exclusion: 1.0
support_shell_gain: 0.0
edge_bias: 0.0
```

This freezes an interior representative of the passing plateau. The final sweep's lowest score was the smallest tested amplitude at the tighter/earlier edge of the box (`5e-8`, `lead=1.15`, `temporal_width=0.30`). That is a minimal-intervention preference induced by the score's total-burden penalty, not a separate architectural discovery. The frozen target keeps the previous nominal amplitude, moves to the stronger local timing found by refinement, and uses the positive sign as the standing tie-breaker from the signed objective diagnostics.

## Final Confirmation Sweep

Run directory:

```text
toolkit/adm_harness_cli/runs/v5_support_shell_final_sweep
```

Sweep box:

```text
abs_amplitude: 5e-8, 1e-7, 2.5e-7
catch_lead: 0.85, 1.0, 1.15
temporal_width: 0.30, 0.35, 0.40
sign: positive, negative
smoothness_order: 1
```

All 54 variants passed the reduced hard gates:

| readout | result |
|---|---:|
| variants tested | 54 |
| hard-gate failures | 0 |
| packet-unsafe variants | 0 |
| minimum catch/support fraction | `0.992802` |
| maximum packet `delta_j_l` fraction | `9.613541e-7` |
| maximum packet abs incremental `delta_rho` | `5.442060e-16` |

At the frozen nominal amplitude slice (`1e-7`), the best timing rows were:

| catch lead | temporal width | catch/support fraction | packet `delta_j_l` fraction | global abs incremental `delta_j_l` | score |
|---:|---:|---:|---:|---:|---:|
| `1.15` | `0.30` | `0.992808` | `4.806802e-7` | `3.537587e-8` | `0.007451` |
| `1.00` | `0.30` | `0.992822` | `4.114204e-7` | `4.133116e-8` | `0.007479` |
| `1.15` | `0.35` | `0.992837` | `3.716353e-7` | `4.575582e-8` | `0.007494` |
| `1.00` | `0.35` | `0.992842` | `3.190142e-7` | `5.330321e-8` | `0.007542` |

The frozen row is not the absolute minimum score in the box. It is the central robust row that preserves the highest local catch/support fraction while keeping packet contamination and packet density quiet.

## Prior Screen And Ladder Context

The broad V5 support-shell ansatz screen showed that the direct support-shell window is the correct family. Compact and mixed momentum-following variants routed only about `0.714` to `0.737` of incremental `delta_j_l` into catch/support. The direct window routed about `0.9926` to `0.9928`, with packet `delta_j_l` leakage far below the gate and packet density essentially silent.

The integrated V5 validation ladder passed on the selected branch. For the previous nominal row (`lead=0.75`, `temporal_width=0.50`) it measured:

| gate | value | threshold |
|---|---:|---:|
| catch/support incremental fraction | `0.992775` | `>= 0.99` |
| packet incremental `delta_j_l` fraction | `1.382323e-7` | `<= 1e-4` |
| packet abs incremental `delta_rho` | `5.442060e-16` | `<= 1e-12` |
| rich packet increment | `3.417580e-14` | `<= 1e-10` |

The amplitude ramp showed no hard failure through `0.01`; warning status began at `0.001` from packet-norm-change fraction, not from packet-norm violation.

After the config freeze, the V5 validation ladder was rerun at:

```text
toolkit/adm_harness_cli/runs/v5_validation_ladder_frozen
```

The frozen target passed all required gates:

| gate | frozen value | threshold | margin |
|---|---:|---:|---:|
| catch/support incremental fraction | `0.9928425` | `>= 0.99` | `+0.00284246` |
| packet incremental `delta_j_l` fraction | `3.190142e-7` | `<= 1e-4` | `+9.968099e-5` |
| packet abs incremental `delta_rho` | `5.442060e-16` | `<= 1e-12` | `+9.994558e-13` |
| rich packet increment | `3.417580e-14` | `<= 1e-10` | `+9.996582e-11` |
| partition closure error | `1.323489e-23` | `<= 1e-18` | `+9.999868e-19` |

The frozen signed-objective diagnostic again chose the positive sign, with relative sign-pair gap `6.26498e-6`. This remains a tie-breaker, not a strong sign-selection effect.

## Freeze Decision

The support-shell control design is frozen for reduced-harness purposes. Further broad tuning is no longer the best use of effort. The branch has a stable burden-routing mechanism, robust packet quietness in the local neighborhood, no sign-critical behavior at tested amplitudes, and no hard-gate failure in the final confirmation box.

The next step is hardcore validation: express this support-shell component as a continuous metric modification, run regenerated 4D demanded-source ledgers at V5, check convergence and off-axis/null exposure, then use V10 as an edge stress after V5 remains the reference truth.
