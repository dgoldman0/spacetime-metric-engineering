# Stage 2 beta075 regulated-medium admissibility audit

Status: necessary-condition audit completed before constructive field-equation validation.

Verification: 58 unit tests passed.

## Purpose

This rung tests whether the regulated anisotropic heat/current medium is already
blocked by necessary physical-medium conditions before attempting a constructive
field-equation solve.

The audit keeps the frozen endpoint-source design fixed:

```text
reset-cap body: frozen bounded anisotropic body
support-edge closure: frozen finite closure component
unfrozen source degree: endpoint current regulator only
```

The point is to avoid a field-equation fit that succeeds only because it hides
new freedom. The audit asks whether the frozen endpoint source plus the minimal
current regulator is at least admissible as a target for a later physical medium.

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
toolkit/adm_harness_cli/adm_harness/endpoint_medium_admissibility.py
toolkit/adm_harness_cli/scripts/run_endpoint_medium_admissibility_audit.py
toolkit/adm_harness_cli/tests/test_endpoint_medium_admissibility.py
```

Outputs:

```text
baseline:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/
  endpoint_medium_admissibility_audit_freeze_rematch_w6_t1p5

dense:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/
  endpoint_medium_admissibility_audit_freeze_rematch_w6_t1p5
```

## Audit Conditions

The audit scans regulator safety factors:

```text
1.00, 1.05, 1.10, 1.25
```

Decision safety factor:

```text
1.10
```

Necessary-condition gates:

- no live regulator rows,
- no post-regulator Type-IV radial blocks,
- no superluminal or undefined flux-frame boost,
- regulator/source burden below `0.06`,
- regulator boundary-gradient cost below `0.06` of frozen source burden,
- finite support rather than grid-scale concentration,
- regulated total conservation remains finite-spread,
- regulator layer has finite burden-weighted conservation spread,
- no added current, angular, collar, packet, or extra conservation-closure component.

## Decision Result

At the `1.10` regulator safety factor, both meshes show no hard obstruction.

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| audit status | no hard obstruction | no hard obstruction |
| regulator/source burden ratio | `0.041495` | `0.042933` |
| boundary-gradient/source ratio | `0.012888` | `0.007239` |
| p99 heat-flux ratio | `0.974975` | `0.975555` |
| p01 transport margin | `0.025025` | `0.024445` |
| max boost speed | `0.978182` | `0.987443` |
| live regulator rows | `0` | `0` |
| post-regulator Type-IV rows | `0` | `0` |
| superluminal/undefined boost rows | `0` | `0` |
| regulated-total conservation read | finite-spread proxy | finite-spread proxy |

Interpretation: the minimal regulator itself was exactly luminal at safety
factor `1.00`, as expected. A small `1.05` pad already removes the luminal
boundary rows, and the `1.10` decision pad keeps the regulator burden and
boundary-gradient cost comfortably below the `0.06` budget.

## Safety-Factor Scan

J-total scan:

| safety factor | baseline regulator/source | dense regulator/source | baseline p99 heat ratio | dense p99 heat ratio | baseline boundary/source | dense boundary/source | baseline hard pass | dense hard pass |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `1.00` | `0.037723` | `0.039030` | `1.000000` | `1.000000` | `0.011716` | `0.006581` | false | false |
| `1.05` | `0.039609` | `0.040981` | `0.986977` | `0.987081` | `0.012302` | `0.006910` | true | true |
| `1.10` | `0.041495` | `0.042933` | `0.974975` | `0.975555` | `0.012888` | `0.007239` | true | true |
| `1.25` | `0.047153` | `0.048787` | `0.946521` | `0.946803` | `0.014646` | `0.008226` | true | true |

This is the key engineering result: the first safety margin that removes the
luminal boundary does not spend the regulator budget. Even `1.25` remains below
the `0.06` budget on both meshes.

## Assignment Read At 1.10

| assignment | metric | baseline `189x121` | dense `377x241` |
| --- | --- | ---: | ---: |
| support edge | regulator/source ratio | `0.023509` | `0.028036` |
| support edge | boundary-gradient/source ratio | `0.026724` | `0.016817` |
| support edge | p99 heat-flux ratio | `0.990244` | `0.992394` |
| support edge | p01 transport margin | `0.009756` | `0.007606` |
| reset cap | regulator/source ratio | `0.046790` | `0.046978` |
| reset cap | boundary-gradient/source ratio | `0.008814` | `0.004638` |
| reset cap | p99 heat-flux ratio | `0.969431` | `0.968870` |
| reset cap | p01 transport margin | `0.030569` | `0.031130` |

The support edge is the thinner transport-margin assignment, but it still stays
inside the necessary-condition gates. The reset cap carries more of the regulator
burden but has a wider transport margin and smaller boundary-gradient cost.

## Watch Item

The audit flags negative angular-inertia rows:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| J-total angular-inertia negative rows | `1,958` | `7,531` |
| support-edge angular-inertia negative rows | `264` | `981` |
| reset-cap angular-inertia negative rows | `1,694` | `6,550` |
| live rows among angular-inertia negatives | `0` | `0` |
| radial-inertia negative rows | `0` | `0` |

This is a real watch, but not a hard obstruction in this audit. It is not a
radial heat/current transport failure, not live leakage, and not a forced new
component. It reflects the already-known angular pressure burden in the frozen
endpoint source. The later constructive medium must explain this angular stress
instead of hiding it.

## Technical-Disclosure Language

The useful disclosure-level statement is:

```text
Before solving a full matter model, the frozen endpoint source plus the minimal
current regulator was checked against necessary admissibility conditions for a
regulated anisotropic heat/current medium. A small 1.10 regulator safety margin
removes the luminal radial-block boundary while keeping regulator burden,
boundary-gradient cost, live leakage, and conservation-spread diagnostics inside
the existing endpoint-source budgets. The remaining watch is angular pressure
admissibility, not radial current closure.
```

## Decision

The regulated anisotropic heat/current medium is not killed by the necessary
conditions tested here. The project can now move to constructive field-equation
validation with a sharper target and a cleaner failure contract:

```text
constructive model may fit:
  regulated radial pair / current medium variables
constructive model may not add:
  angular-capacity component
  extra conservation-closure component
  collar or packet component
  live regulator support
must explain:
  non-live angular pressure burden flagged by the admissibility audit
```
