# Stage II Beta075 Full-Package 1+1 Source Coupling

## Status

Overall status: `package_support_source_watch`.

The full-package reduced `1+1` source-coupling sweep does not clear the observed-amplitude source law globally. The failure is narrow and diagnostic rather than architectural: the original row-4605 reset-decompression bottleneck passes, while two support-edge endpoint-junction phase slices overdrive the local rapidity budget.

This report is written from the structured run outputs in:

```text
toolkit/adm_harness_cli/runs/stage2_beta075_support_source_coupling_package/
```

The code wrote CSV and manifest artifacts only. This report is the human interpretation layer.

## Run Scope

The sweep promoted the row-4605 source-coupled rapidity pilot to every active non-live support slice in the sealed dense `24x14` support-closure package. Each slice used the sealed support-source profile as a time-distributed rapidity drive, advected it along the service-radial `l` direction, and checked local cone/transport budgets.

Structured outputs:

```text
endpoint_support_source_coupling_active_budget.csv
endpoint_support_source_coupling_slice_summary.csv
endpoint_support_source_coupling_package_summary.csv
endpoint_support_source_coupling_worst_rows.csv
endpoint_support_source_coupling_decision.csv
endpoint_support_source_coupling_manifest.json
```

## Package Summary

| scenario | status | slices | fail slices | fail rows | max budget fraction | min sampled cone margin | min transport margin |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| observed outward | fail | 682 | 2 | 16 | 2.075621 | 2.247e-11 | 2.655e-11 |
| observed inward | fail | 682 | 2 | 6 | 1.388222 | 7.134e-09 | 1.435e-08 |
| observed outward, budget-audited | limited pass | 682 | 0 | 0 | 0.950000 | 1.654e-06 | 1.514e-06 |
| large outward | fail | 682 | 7 | 85 | 10.378107 | 4.814e-13 | 0.000000 |
| large outward, budget-audited | limited pass | 682 | 0 | 0 | 0.950000 | 1.432e-06 | 1.514e-06 |

The central verdict is the observed outward/inward result. The larger-amplitude and budget-audited rows are retained as stress context and diagnostics, not as the claim driver.

## Observed Failure Localization

| direction | assignment | stage | region | s | rows | fail rows | max budget fraction | worst row | worst l | worst delta psi | min sampled cone margin | min transport margin |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| outward | support_edge_endpoint_junction | entry_precatch | support_edge | -1.236702 | 31 | 14 | 2.075621 | 204 | -1.600000 | 10.327273 | 2.247e-11 | 2.655e-11 |
| inward | support_edge_endpoint_junction | entry_precatch | support_edge | -1.236702 | 31 | 1 | 1.388222 | 194 | -2.100000 | 8.837622 | 7.134e-09 | 1.435e-08 |
| outward | support_edge_endpoint_junction | catch_rematch | support_edge | 0.606383 | 40 | 2 | 1.015163 | 2002 | -1.500000 | 5.363739 | 8.519e-07 | 1.763e-06 |
| inward | support_edge_endpoint_junction | catch_rematch | support_edge | 0.606383 | 40 | 5 | 1.025096 | 2025 | 1.800000 | 6.589253 | 7.242e-07 | 1.504e-06 |

The entry-precatch slice at `s=-1.236702` is the real observed-amplitude failure. The catch-rematch slice at `s=0.606383` is a mild over-budget edge case, just above the local budget in both directions.

## Row-4605 Read

The earlier row-4605 reset-decompression/support-edge bottleneck survives the full-package source-coupled run.

| scenario | status | max budget fraction | worst row | worst l | worst delta psi | min transport margin |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| observed outward | pass | 0.167438 | 4605 | 2.000000 | 0.365613 | 3.8e-05 |
| observed inward | pass | 0.128254 | 4605 | 2.000000 | 0.280051 | 4.6e-05 |
| large outward | pass | 0.837192 | 4605 | 2.000000 | 1.828064 | 2.0e-06 |

This matters because it separates the package failure from the previously identified reset-decompression bottleneck. The distributed support-source profile resolves that specific concern; the new problem is phase-local source overdrive in support-edge endpoint-junction entry/catch slices.

## Interpretation

The result does not point to a missing geometric or closure component. The sealed design components remain coherent at this rung: the full-package run shifts the failure away from reset-decompression row 4605 and into a small number of support-edge endpoint-junction source-realization slices.

The right next move is targeted source design, not architecture redesign. The source law needs phase-aware shaping or normalization for `entry_precatch/support_edge` near `s=-1.236702`, with a smaller catch-rematch cleanup near `s=0.606383`. Candidate repairs should be judged by rerunning the same full-package structured sweep and requiring observed outward/inward source-coupled evolution to clear without hard cone, transport, live-leakage, or over-budget failures.

Claim boundary: this is still a reduced fixed-background source-coupling diagnostic. It does not promote the package to full spacetime evolution, a matter-action proof, or a global hyperbolicity theorem.
