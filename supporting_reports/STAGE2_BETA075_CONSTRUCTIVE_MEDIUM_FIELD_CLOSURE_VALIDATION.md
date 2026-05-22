# Stage 2 beta075 constructive medium field-closure validation

Status: closed. Promote the constrained regulated anisotropic heat/current
medium as the beta075 endpoint physical-source candidate at finite-difference
field-closure level.

Verification: `PYTHONPATH=toolkit/adm_harness_cli python -m unittest discover -s toolkit/adm_harness_cli/tests`
passed 60 tests.

## Question

The necessary-condition audit found no hard radial heat/current obstruction, but
it left a non-live angular-pressure watch. The open question was whether that
watch required a new angular-capacity, conservation-closure, collar, packet, or
live regulator component, or whether it could be carried as an internal response
of the same regulated anisotropic heat/current medium.

## Constraint

The test keeps the branch narrow:

```text
same regulated anisotropic medium
same frozen reset-cap body
same frozen support-edge closure
endpoint current regulator only as the unfrozen source degree
internal anisotropic angular response allowed as a constitutive response
no new angular-capacity, conservation-closure, collar, packet, or live regulator component
```

The validation attaches the angular response to explicit medium variables and
checks radial heat/current closure, angular response residuals, conservation
compatibility, finite-propagation margins, boundary-gradient cost, and hidden
component leakage on the baseline and dense meshes.

## New Code

```text
toolkit/adm_harness_cli/adm_harness/endpoint_medium_field_closure.py
toolkit/adm_harness_cli/scripts/run_endpoint_medium_field_closure_validation.py
toolkit/adm_harness_cli/tests/test_endpoint_medium_field_closure.py
```

Outputs:

```text
baseline:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/
  endpoint_medium_field_closure_validation_freeze_rematch_w6_t1p5/

dense:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/
  endpoint_medium_field_closure_validation_freeze_rematch_w6_t1p5/
```

## Decision Metrics

Both meshes pass the constrained field-closure gates.

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| field-closure status | pass | pass |
| worst normalized angular L1 error | `0.002977` | `0.009524` |
| worst angular-watch L1 error | `0.003062` | `0.010758` |
| max response coefficient | `0.608980` | `0.376013` |
| max angular residual/source ratio | `0.001996` | `0.006415` |
| regulator/source ratio | `0.041495` | `0.042933` |
| regulator boundary-gradient/source ratio | `0.012888` | `0.007239` |
| p99 heat-flux ratio | `0.974975` | `0.975555` |
| p01 transport margin | `0.025025` | `0.024445` |
| max boost speed | `0.978182` | `0.987443` |
| live rows | `0` | `0` |
| regulator-live rows | `0` | `0` |
| superluminal/undefined boost rows | `0` | `0` |
| max conservation-burden delta vs regulated target | `0.000000000192` | `0.000020` |

Scope read:

| scope | metric | baseline `189x121` | dense `377x241` |
| --- | --- | ---: | ---: |
| `J_total` | normalized angular L1 error | `0.000923` | `0.002794` |
| `J_total` | angular residual/source ratio | `0.000454` | `0.001370` |
| support edge | normalized angular L1 error | `0.002977` | `0.009524` |
| support edge | angular-watch L1 error | `0.003062` | `0.010758` |
| support edge | angular residual/source ratio | `0.001996` | `0.006415` |
| reset cap | normalized angular L1 error | `0.0000002` | `0.0000001` |
| reset cap | angular-watch L1 error | `0.0000001` | `0.0000000` |

The dense mesh has a larger support-edge angular residual than the baseline, but
it remains below the `0.02` angular-watch gate and below the `0.01` residual to
source gate. The response coefficient decreases from `0.608980` to `0.376013`
under refinement, so the watch does not look like an unbounded capacity demand.

## Closure And Conservation

The fitted medium uses explicit variables:

```text
energy density:             regulated rest-frame energy density
radial pressure:            regulated rest-frame radial pressure
angular pressure:           fitted internal angular response pressure
radial heat/current ratio:  regulated heat-flux ratio
transport margin:           1 - regulated heat-flux ratio
regulator density:          endpoint current regulator density
```

The radial heat/current residual and transport-margin deficit are zero on both
meshes. The fitted angular response also adds no current layer:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| radial heat/current residual volume | `0` | `0` |
| transport-margin deficit volume | `0` | `0` |
| delta-current volume | `0` | `0` |
| boost superluminal/undefined rows | `0` | `0` |

Conservation proxy read:

| mesh | source | `J_total` burden residual | support-edge burden residual | reset-cap burden residual |
| --- | --- | ---: | ---: | ---: |
| baseline | regulated target | `0.022463` | `0.072857` | `0.011832` |
| baseline | fitted internal response | `0.022438` | `0.072716` | `0.011832` |
| dense | regulated target | `0.012381` | `0.044270` | `0.006120` |
| dense | fitted internal response | `0.012384` | `0.044290` | `0.006120` |

All rows keep the `finite_spread_proxy_not_conservation_proof` diagnostic. The
fitted response does not create a hidden conservation source; its conservation
burden remains essentially identical to the regulated target and improves under
dense refinement in the support-edge burden residual.

Gradient read:

| scope | metric | baseline `189x121` | dense `377x241` |
| --- | --- | ---: | ---: |
| `J_total` | internal angular-response gradient/source | `0.142040` | `0.073584` |
| support edge | internal angular-response gradient/source | `0.518973` | `0.284567` |
| reset cap | internal angular-response gradient/source | `0.031062` | `0.016288` |
| `J_total` | angular residual-gradient/source | `0.000391` | `0.000647` |
| support edge | angular residual-gradient/source | `0.001721` | `0.003030` |

The internal response has a finite gradient cost that decreases under
refinement. The residual-gradient cost rises mildly on the dense support edge,
but remains small compared with source burden and does not trip a closure gate.

## Decision

Do not add a new component. The non-live angular-pressure watch is explainable
inside the same regulated anisotropic heat/current medium as a finite internal
anisotropic response. The candidate preserves the current-regulator budget,
keeps transport subluminal with positive margin, has zero live leakage, adds no
current layer, and does not degrade the conservation proxy.

Promote the constrained medium as the beta075 endpoint physical-source
candidate for the technical disclosure. The claim remains bounded: this is a
constructive prescribed-metric/effective-source validation with finite-difference
closure diagnostics, not a covariant matter-action theorem, global horizon
theorem, semiclassical/RSET proof, or broad beta/V robustness claim.
