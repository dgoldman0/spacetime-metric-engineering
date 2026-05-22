# Stage 2 beta075 covariant endpoint-medium audit

Status: first covariant tensor-identity rung completed. Promote the regulated
anisotropic heat/current medium from ADM-component closure to a covariant
stress-energy identity diagnostic for the beta075 endpoint source.

## Question

The field-closure validation showed that the frozen endpoint source, current
regulator, and internal angular response close as an effective medium in ADM
variables. The next question was whether those variables can be assembled into
one spacetime tensor field on the service metric and then projected back to the
same ADM source channels.

## New Code

```text
toolkit/adm_harness_cli/adm_harness/endpoint_medium_covariant_audit.py
toolkit/adm_harness_cli/scripts/run_endpoint_medium_covariant_audit.py
toolkit/adm_harness_cli/tests/test_endpoint_medium_covariant_audit.py
```

Outputs:

```text
baseline:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/
  endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5/

dense:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/
  endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5/
```

## Tensor Lift

The audit constructs

```text
T_mu_nu = rho u_mu u_nu + p_l s_mu s_nu + pOmega Q_mu_nu
          + u_mu q_nu + u_nu q_mu
```

with `u = n_ADM`, `s = e_l`, `q = j_l s`, and
`Q = g + u u - s s`. The stored boost-to-flux-frame remains a diagnostic for
heat/current admissibility and eigenframe behavior; it is not used as a
zero-heat-flux rest-frame lift because that branch does not preserve the signed
ADM endpoint stress.

The tensor is projected back onto the ADM tetrad and compared with the regulated
endpoint source channels:

```text
rho_H, j_l, p_l, pOmega, Tkk_plus, Tkk_minus
```

The audit also computes a full-grid finite-difference
`nabla_mu T^{mu nu}` diagnostic. The component tensor is set to zero off the
endpoint-source support so boundary exchange appears explicitly rather than
being hidden inside the active rows.

## Decision Metrics

Both meshes pass.

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| covariant identity status | pass | pass |
| point rows | `7,188` | `28,359` |
| max ADM projection error | `5.55e-17` | `6.59e-17` |
| projection/source error ratio | `1.16e-16` | `1.13e-16` |
| max boost-to-flux-frame speed | `0.978182` | `0.987443` |
| boost superluminal/undefined rows | `0` | `0` |
| mixed-eigen complex rows | `0` | `0` |
| max mixed-eigen imaginary part | `0` | `0` |
| allowed exchange divergence fraction | `0.995410` | `0.995927` |
| outside-allowed divergence fraction | `0.004590` | `0.004073` |
| live finite-difference halo fraction | `0.003553` | `0.003199` |
| weighted mean active divergence norm | `0.001980` | `0.000947` |
| peak active divergence norm | `0.220714` | `0.207154` |

The dense mesh improves the active divergence norm and slightly reduces the
outside/live divergence fractions. The small live value is a derivative-stencil
halo in non-active packet-adjacent rows, not active medium support: active
source rows remain non-live.

## Scope Read

| scope | rows baseline | rows dense | max projection error baseline | max projection error dense | max boost baseline | max boost dense |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `J_total` | `7,188` | `28,359` | `5.55e-17` | `6.59e-17` | `0.978182` | `0.987443` |
| support edge | `652` | `2,590` | `5.55e-17` | `5.38e-17` | `0.926884` | `0.974376` |
| reset cap | `6,536` | `25,769` | `4.16e-17` | `6.59e-17` | `0.978182` | `0.987443` |

## Interpretation

This closes the first covariant identity check: the regulated endpoint medium
is not merely a loose collection of ADM channel knobs. Its regulated density,
radial pressure, angular response, and radial heat/current assemble into a
single tensor whose ADM projections reproduce the fitted source channels on
baseline and dense meshes.

The covariant-divergence diagnostic is also favorable at this rung. The
exchange burden is localized to endpoint/support masks, with a small
finite-difference halo near packet-adjacent rows. That halo is below the audit
gate and decreases under refinement.

## Boundary

This is still not a matter-action theorem, a dynamical Einstein evolution, a
global horizon theorem, or a semiclassical/RSET proof. It is a tensor
reconstruction, ADM reprojection, eigen/type, and direct finite-difference
covariant-divergence audit for the fixed prescribed metric and endpoint medium.

The next physical-source rung, if pursued, should be an explicit constitutive
field-equation or matter-action construction that produces this tensor and its
localized exchange current rather than simply diagnosing it.
