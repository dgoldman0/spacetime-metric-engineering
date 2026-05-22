# Stage 2 beta075 endpoint current-regulator screen

Status: first endpoint current-regulator constitutive screen completed.

Verification: 55 unit tests passed.

## Purpose

This rung follows the endpoint source-class screen. The source-class result said
the frozen endpoint-J stress is not a single scalar and not an ordinary Type-I
anisotropic fluid everywhere, but it needs only a small finite `rho+p_l`
regulator to make the radial heat/current block boost-diagonalizable.

This screen tests that design implication directly: keep the frozen reset-cap
body and support-edge closure fixed, introduce only the endpoint current
regulator as a constitutive accounting layer, and check whether it stays
non-live, finite-support, below budget, and conservation-spread friendly.

## Inputs

```text
baseline freeze:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/
  endpoint_j_freeze_source_model_rematch_w6_t1p5

dense freeze:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/
  endpoint_j_freeze_source_model_rematch_w6_t1p5
```

New code:

```text
toolkit/adm_harness_cli/adm_harness/endpoint_current_regulator.py
toolkit/adm_harness_cli/scripts/run_endpoint_current_regulator_screen.py
toolkit/adm_harness_cli/tests/test_endpoint_current_regulator.py
```

Outputs:

```text
baseline:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/
  endpoint_current_regulator_screen_freeze_rematch_w6_t1p5

dense:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/
  endpoint_current_regulator_screen_freeze_rematch_w6_t1p5
```

## Method

For each frozen endpoint-J source row, reuse the source-class regulator density:

```text
minimal regulator = max(0, 2 |j_l| - |rho + p_l|)
```

The constitutive layer is sign-preserving in `rho+p_l` and splits the regulator
evenly into the radial pair:

```text
delta rho = 0.5 sign(rho+p_l) regulator
delta p_l = 0.5 sign(rho+p_l) regulator
delta j_l = 0
delta pOmega = 0
```

This is deliberately narrow. It does not add a new current component, angular
component, optical collar, packet component, or conservation-closure component.
It asks whether the regulator alone is enough to close the radial block within
the regulated anisotropic heat/current medium.

## Gate Result

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| screen decision | pass | pass |
| regulator rows | `525` | `2,103` |
| regulator live rows | `0` | `0` |
| regulator/source burden ratio | `0.037723` | `0.039030` |
| budget gate | `0.060000` | `0.060000` |
| peak regulator density | `0.022435` | `0.023392` |
| p99 regulator density | `0.016790` | `0.017314` |
| effective regulator volume fraction | `0.110140` | `0.090494` |
| top 1pct regulator burden share | `0.053417` | `0.048966` |
| post-regulator Type-IV rows | `0` | `0` |
| post-regulator unresolved rows | `0` | `0` |

Read: the regulator stays at the source-class scale, remains under the `0.06`
budget, touches no live rows, and algebraically closes the flux-dominant radial
block on both meshes.

## Assignment Split

| assignment | metric | baseline `189x121` | dense `377x241` |
| --- | --- | ---: | ---: |
| support edge | regulator rows | `95` | `433` |
| support edge | regulator/source ratio | `0.021372` | `0.025487` |
| support edge | peak regulator density | `0.008559` | `0.008777` |
| support edge | effective volume fraction | `0.066824` | `0.056517` |
| reset cap | regulator rows | `430` | `1,670` |
| reset cap | regulator/source ratio | `0.042536` | `0.042708` |
| reset cap | peak regulator density | `0.022435` | `0.023392` |
| reset cap | effective volume fraction | `0.766158` | `0.770745` |

The larger regulator burden is in the reset cap, not the support edge. The
support-edge regulator remains smaller than the total endpoint value and does
not introduce live leakage.

## Conservation Read

The regulated total remains finite-spread under the existing endpoint-J
conservation proxy:

| model | metric | baseline `189x121` | dense `377x241` |
| --- | --- | ---: | ---: |
| frozen endpoint source | J-total burden-weighted residual norm | `0.020207` | `0.011084` |
| regulated endpoint medium | J-total burden-weighted residual norm | `0.022144` | `0.012190` |
| frozen endpoint source | J-total peak residual norm | `2.026101` | `2.837687` |
| regulated endpoint medium | J-total peak residual norm | `2.032744` | `2.837687` |
| regulator layer only | burden-weighted residual norm | `0.255807` | `0.152476` |
| regulator layer only | peak residual burden share | `0.000000` | `0.000000` |

The standalone regulator layer reports a large volume-normalized residual watch
because zero-layer rows create a bad normalization denominator. That is not the
decision gate here. The relevant checks are that the regulator burden-weighted
spread is finite and that the regulated total source keeps the same finite-spread
read as the frozen endpoint source.

## Interpretation

The endpoint current regulator passes the first constitutive feasibility screen.
It is small, non-live, finite-support, dense-stable, and sufficient to remove the
local Type-IV radial-block classification without adding current, angular, collar,
packet, or extra closure degrees of freedom.

This does not prove a matter action or a full covariant field-equation solution.
It justifies the next physical-source rung, but the next rung should be a
necessary-condition / admissibility audit before a constructive field-equation
solve. The endpoint current regulator remains the only unfrozen source-realization
component.

## Next Work

The next rung should keep the same boundary:

```text
frozen:
  reset-cap bounded anisotropic body
  finite support-edge closure
unfrozen:
  endpoint current regulator only
```

Useful follow-up is a compact admissibility audit: test flux-frame admissibility,
finite transport sanity, boundary-layer cost, conservation spread, and whether
any hidden angular-capacity, current, collar, packet, or extra closure component
is forced. A constructive field-equation solve should come after that audit.
