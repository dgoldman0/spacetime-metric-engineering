# Active-Rail Validation Ladder Results

## Scope

This report records the current validation-ladder results for the active-rail support-shell branch at `V = 5` and `V = 10`.

Here `V` is the active-rail service factor: a dimensionless carried-shift operating-load parameter. In the reduced metric it controls the magnitude of the support-contained radial shift field during the carried-service portion, i.e. the nominal effective transport factor imposed on the metric service. In the field builder this enters through `U_beta = v_exit + (V - v_exit) C_beta` and `U_packet = v_exit + (V - v_exit) C_packet`; `U_beta` sets the radial shift carrier `beta`, while `U_packet/B + beta` is the combination checked in the packet norm. It is not the ordinary physical velocity of the passenger packet. The harness schema still stores it under `service.velocity`, but report prose should read that as service factor / carried-shift load.

The tested support-shell ansatz is the promoted positive carrying-flow component:

- service field: `carrying_flow`
- law: `windowed_adjustment`
- scope: `catch_rematch_support_shell`
- allocation: `support_shell`
- target amplitude: `+1e-7`
- catch lead: `0.75`
- temporal width: `0.5`

The ladder separates two questions:

1. Does the selected target pass the validation gates?
2. How far can the same ansatz be ramped before it becomes warning-level or unsafe?

This separation matters. A high-amplitude ramp failure should not be counted as a failure of the selected `+1e-7` target.

## Ladder Components

The current ladder runs:

- a flow-off baseline;
- the promoted positive support-shell target;
- a generated negative counterpart for sign comparison;
- a packet-safety overlay on the tuned high-resolution branch;
- a richer multi-channel source objective over `rho`, `j_l`, `delta_rho`, and `delta_j_l`;
- signed source/objective comparison;
- reduced partition-closure bookkeeping;
- a positive-amplitude load-bearing ramp.

The packet overlay recomputes:

```text
packet_norm_new = -alpha^2 + gamma_ll * (U_packet/B + beta + delta_beta)^2
```

using the tuned high-resolution branch for the corresponding `V`.

## Target-Gate Results

Both `V = 5` and `V = 10` pass the selected-target gates.

| quantity | `V = 5` | `V = 10` |
|---|---:|---:|
| target required gates | pass | pass |
| catch-support incremental `delta_j_l` fraction | `0.9927751519845942` | `0.9927751489693433` |
| packet incremental `delta_j_l` fraction | `1.3823230658422633e-07` | `1.4315292180112814e-07` |
| packet abs incremental `delta_rho` | `5.44206011079721e-16` | `5.605263879731586e-17` |
| target live packet-norm violations | `0` | `0` |
| nominal overlay variants safe | `true` | `true` |
| rich packet increment, all channels | `3.4175798635531146e-14` | `3.511240127512317e-14` |
| reduced partition closure error | `2.6469779601696886e-23` | `2.6469779601696886e-23` |

The immediate interpretation is that the support-shell service component survives the `V = 10` service-factor check at the selected amplitude. The target still routes the added burden into catch/rematch support-shell infrastructure, keeps packet exposure tiny, and preserves live packet-norm safety.

## Rich Source Objective

The richer objective does not change the target selection story. It confirms that the support-shell increment is infrastructure-localized across the ADM channels the harness recomputes.

| quantity | `V = 5` | `V = 10` |
|---|---:|---:|
| global increment abs, all channels | `2.463130027755651e-07` | `2.463130025803608e-07` |
| catch-support increment abs, all channels | `2.4453149986890966e-07` | `2.4453149987473015e-07` |
| packet increment abs, all channels | `3.4175798635531146e-14` | `3.511240127512317e-14` |
| packet fraction, all channels | `1.3874947018802483e-07` | `1.4255195993426122e-07` |
| rich source objective, lower better | `3.097057256034496e-07` | `3.092143323731234e-07` |

This objective is still a reduced ADM diagnostic, not a matter-source proof. Its value is that it keeps the packet-exposure accounting from being narrowly tied to `delta_j_l` alone.

## Sign Result

The positive sign remains the preferred convention, but only weakly.

| quantity | `V = 5` | `V = 10` |
|---|---:|---:|
| sign-pair winner | positive | positive |
| relative objective gap | `2.89036e-06` | `5.55542e-06` |
| positive catch-support opposition fraction | `0.009978089120591012` | `0.010306990439262547` |

The sign result is consistent across `V = 5` and `V = 10`, but it is not decision-grade physics. Positive sign is the right default for the harness branch because it slightly opposes the existing signed catch-support demand. It should not yet be promoted as a physical source-family conclusion.

## Packet-Safety Overlay

At the selected target amplitude, packet safety is preserved in both cases.

| quantity | `V = 5` | `V = 10` |
|---|---:|---:|
| target amplitude | `1e-7` | `1e-7` |
| max live packet norm after overlay | about `-251.331` | about `-198.923` |
| target max live packet-norm change | about `0.00350909` | about `0.00699736` |
| live packet-norm violations | `0` | `0` |

The `V = 10` carried-shift load case has a smaller live packet safety margin and a larger target packet-norm response than `V = 5`, but the target amplitude remains very far from violation.

## Load-Bearing Ramp

The ramp is where the higher `V = 10` carried-shift load case becomes meaningfully more restrictive.

| quantity | `V = 5` | `V = 10` |
|---|---:|---:|
| last no-warning pass amplitude | `5e-4` | `2.5e-4` |
| first warning amplitude | `1e-3` | `5e-4` |
| last hard-pass amplitude | `1e-2` | `7.5e-3` |
| first hard failure amplitude | none in tested range | `1e-2` |

The warning criterion is based on packet-norm change relative to the baseline safety scale. It is not always the same thing as the worst live packet norm approaching zero. At `V = 5`, the ramp enters warning territory because some live packet-norm changes become large relative to the baseline margin scale, but no hard packet violation appears through `1e-2`. At `V = 10`, the same ramp eventually drives the maximum live packet norm positive at `1e-2`, with max live packet norm about `48.3828`.

The support-shell routing itself remains excellent throughout the ramp. The failure mode is packet-safety margin consumption, not loss of support-shell localization.

## Current Interpretation

The validation ladder strengthens the active-rail conclusion:

1. The selected support-shell target is stable at `V = 5`.
2. The same selected target survives the `V = 10` service-factor check.
3. The extra support-shell demand remains infrastructure-localized under the richer multi-channel objective.
4. Packet exposure remains tiny at the selected target amplitude.
5. Load-bearing amplitude is not unlimited; the `V = 10` carried-shift load case exposes the first hard packet-safety failure at the top of the tested ramp.

In short: the branch is credible as a controllable support-shell service component, not just a tuned metric artifact. It is still not a source-feasibility proof.

## Harness Lessons Before Hardening

The current work also exposed a harness-design lesson: target validation and ramp-envelope exploration must be separate result classes. The target can pass while the ramp intentionally discovers a failure. Treating every ramp amplitude as part of the target gate creates false negatives.

The next hardening stage should therefore:

- rename the ladder command so it is not `V5`-specific;
- make `V` a first-class service-factor input where the relevant data products exist;
- preserve target pass/fail, warning envelope, and hard ramp failure as distinct outcomes;
- add tests for sign-pair naming, target/ramp separation, nominal overlay filtering, ramp status classification, rich-objective accounting, and partition closure;
- write explicit provenance into every ladder output, including `V`, configs, exact fields, substrate fields, packet member, thresholds, ramp amplitudes, and git commit when available.

## Local Artifacts

Current generated artifacts are intentionally local run outputs:

- `toolkit/adm_harness_cli/runs/v5_validation_ladder/validation_ladder_report.md`
- `toolkit/adm_harness_cli/runs/v5_validation_ladder/validation_ladder_amplitude_ramp_report.md`
- `toolkit/adm_harness_cli/runs/v10_validation_ladder/validation_ladder_report.md`
- `toolkit/adm_harness_cli/runs/v10_validation_ladder/validation_ladder_amplitude_ramp_report.md`
