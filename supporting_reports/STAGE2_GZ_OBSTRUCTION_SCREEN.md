# Stage II GZ Obstruction Screen

Date: 2026-05-21

## Purpose

This screen tests the Garattini-Zatrimaylov-style horizon/trapping concern as a
separate causal-structure gate. It is not another selected-null, endpoint J, or
live packet-norm leaderboard. The diagnostic checks whether the ADM radial
metric develops null-branch pinch behavior in the live packet or shell/throat
actuation band.

The harness convention is

```text
ds^2 = -alpha^2 dsigma^2 + gamma_ll (dl + beta dsigma)^2 + gamma_omega dOmega^2
```

so the radial coordinate null speeds are

```text
dl/dsigma = -beta +/- alpha / sqrt(gamma_ll)
```

The screen tracks `g_sigma_sigma = -alpha^2 + gamma_ll beta^2`, radial branch
speeds, branch zero-crossing edges, finite-domain null trace smoke tests, metric
condition number, Ricci scalar, and a shell/throat overlap proxy built from
actuation windows, areal-radius throat proxy, and local shape gradients.

## Inputs

Screen output directory:

```text
toolkit/adm_harness_cli/runs/gz_obstruction_screen_receiver_beta075_beta100/
```

Compared ledgers:

| label | point ledger |
| --- | --- |
| `beta075_p003_mid` | `toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_negative_l_promotion_dense_81x121/ledgers/receiver_neg_promotion_p003_mid_beta075/source_ledger_point_ledger.csv` |
| `beta100_baseline` | `toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_p003_mid_beta100_stress_61x83/ledgers/receiver_neg_beta100_baseline/source_ledger_point_ledger.csv` |
| `beta100_p003_mid` | `toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_p003_mid_beta100_stress_61x83/ledgers/receiver_neg_beta100_p003_mid/source_ledger_point_ledger.csv` |
| `beta100_p003_mid_post1p5` | `toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_p003_mid_beta100_retiming_locality_small_61x83/ledgers/receiver_neg_beta100_p003_mid_post1p5/source_ledger_point_ledger.csv` |

Generated files:

| file | role |
| --- | --- |
| `gz_obstruction_report.md` | generated screen report |
| `gz_obstruction_decision.csv` | pass/fail decision sheet |
| `gz_obstruction_summary.csv` | per-label, per-scope causal-margin summary |
| `gz_obstruction_branch_crossing_edges.csv` | localized branch zero-crossing edges |
| `gz_obstruction_top_overlap_points.csv` | highest shell/throat-overlap proxy rows |
| `gz_obstruction_null_trace_summary.csv` | finite-domain null trace smoke results |

## Decision

The gate trips for every compared case.

| label | status | primary trip |
| --- | --- | --- |
| `beta075_p003_mid` | fail | live packet, active interpolation, and top shell/throat-overlap minus-branch zero-crossing edges |
| `beta100_baseline` | fail | live packet, active interpolation, and top shell/throat-overlap minus-branch zero-crossing edges |
| `beta100_p003_mid` | fail | live packet, active interpolation, and top shell/throat-overlap minus-branch zero-crossing edges |
| `beta100_p003_mid_post1p5` | fail | live packet, active interpolation, and top shell/throat-overlap minus-branch zero-crossing edges |

This is not a statement that a global event horizon has been proven. It is a
report-grade statement that the current ledgers do contain the local causal
signature that the GZ concern was asking us to check.

## Main Numbers

| label | scope | branch crossing edges | min endpoint speed | gtt >= 0 points | max GZ overlap score |
| --- | --- | ---: | ---: | ---: | ---: |
| `beta075_p003_mid` | live packet | 71 | 0.004725 | 259 / 620 | 135.276 |
| `beta075_p003_mid` | top overlap decile | 95 | 0.004725 | 196 / 981 | 135.276 |
| `beta100_baseline` | live packet | 53 | 0.008881 | 133 / 342 | 210.710 |
| `beta100_baseline` | top overlap decile | 75 | 0.008881 | 146 / 507 | 210.710 |
| `beta100_p003_mid` | live packet | 53 | 0.008881 | 133 / 342 | 210.624 |
| `beta100_p003_mid` | top overlap decile | 68 | 0.008881 | 97 / 507 | 210.624 |
| `beta100_p003_mid_post1p5` | live packet | 53 | 0.008881 | 133 / 342 | 210.624 |
| `beta100_p003_mid_post1p5` | top overlap decile | 68 | 0.008881 | 97 / 507 | 210.624 |

The sampled grid points do not land exactly on branch zero at the `1e-4`
threshold, but the branch sign changes across neighboring grid edges. In other
words, the zero surface lies between sampled points.

## Interpretation

The failure is not beta100-specific and not receiver-specific. The beta100
baseline already has the causal branch issue, and the beta100 `p003_mid` and
`p003_mid_post1p5` variants mostly inherit the same causal picture. The retimed
receiver can improve endpoint transfer accounting, but it does not clear the GZ
obstruction gate.

The failure is specifically a minus-branch accessibility issue. The plus branch
stays positive in the tested scopes, while the minus branch changes sign. That
means the local cones are tilted enough that one radial null branch loses the
expected coordinate-side access in parts of the live packet and shell/throat
overlap band. This is exactly the kind of channel that live packet norm and SNEC
screens do not measure.

There is no evidence here of a new curvature blow-up caused by the receiver. The
live-packet max `abs(ricci_scalar)` is about `12.70` for beta075 and `9.47` for
the beta100 cases. Whole-grid peaks are larger, about `44.66` for beta075 and
`53.23` for beta100, but this run is not a refinement-scaling proof. The metric
condition number is high in the support/throat plant, reaching about `9.43e4`
globally, while the live-packet maxima are lower, about `690` for beta075 and
`592` for beta100.

The finite-domain null trace smoke test is inconclusive rather than reassuring:
representative traces drift in the expected radial directions, but they hit the
upper sigma boundary before reaching the radial domain boundary. Because the
branch zero-crossing edges already trip, the next version needs longer-domain or
proper null-geodesic tracing rather than treating the smoke trace as a pass.

## Consequence For Current Claims

The beta075 `p003_mid` receiver remains live-clean and endpoint-effective in the
previously measured receiver/source-accounting channels. This screen does not
undo those results.

It does block any claim that the promoted active-rail metric is horizon-free or
GZ-obstruction-free. The correct current language is:

```text
The beta075 p003_mid receiver is live-clean and endpoint-effective in the measured
source-accounting/SNEC channels, but the active-rail metric still trips a local
GZ-style causal branch gate. Horizon/trapping freedom remains unresolved and
currently adverse at the ledger-screen level.
```

## Recommended Next Step

Do not tune the beta100 receiver to solve this; the issue is already present in
the beta100 baseline and in beta075. The next design move should be a
horizon-aware source/metric constraint:

- reduce or redistribute the carrying-flow shift in live packet and high-overlap
  shell/throat regions,
- enforce a local margin such as `abs(beta) < alpha / sqrt(gamma_ll)` in the
  protected packet corridor unless a deliberate one-way causal region is being
  modeled,
- rerun this screen with refinement scaling after any metric/source retiming,
- extend the smoke traces into a proper radial null escape diagnostic.

Until that is done, the GZ concern should stay open and marked as a real
causal-structure blocker for any horizon-free design claim.
