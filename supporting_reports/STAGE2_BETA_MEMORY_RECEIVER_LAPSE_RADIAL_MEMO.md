# Stage II Beta-Memory Receiver Lapse/Radial Memo

Date: 2026-05-20

## Scope

This memo records the second `61 x 83` smoke test of the beta-memory
support-edge receiver branch. It keeps the same non-live receiver memory
geometry as the first smoke, but replaces the direct beta-relaxation plus
strong angular flange with a milder lapse/radial stress-channel realization.

Outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_lapse_radial_smoke_61x83/
```

Spec:

```text
toolkit/adm_harness_cli/specs/endpoint_beta_memory_receiver_lapse_radial_smoke.json
```

## Result

All five source-ledger cases were live-clean:

| label | positive live packet-norm samples |
| --- | ---: |
| `receiver_lr_baseline_beta075` | `0` |
| `receiver_lr_lapse_p004_beta075` | `0` |
| `receiver_lr_radial_p004_beta075` | `0` |
| `receiver_lr_lapse_radial_p004_beta075` | `0` |
| `receiver_lr_lapse_radial_p004_ang_p0015_beta075` | `0` |

The lapse/radial channels alone did not improve the endpoint J selected-null
total:

| label | J selected-null deficit |
| --- | ---: |
| `receiver_lr_baseline_beta075` | `0.964417` |
| `receiver_lr_lapse_p004_beta075` | `0.965803` |
| `receiver_lr_radial_p004_beta075` | `0.965790` |
| `receiver_lr_lapse_radial_p004_beta075` | `0.967548` |
| `receiver_lr_lapse_radial_p004_ang_p0015_beta075` | `0.954120` |

The small angular companion recovered selected-null improvement but revived
the current/angular cost:

| label | support-edge current | support-edge angular |
| --- | ---: | ---: |
| `receiver_lr_baseline_beta075` | `0.105033` | `1.912497` |
| `receiver_lr_lapse_p004_beta075` | `0.104954` | `2.537997` |
| `receiver_lr_radial_p004_beta075` | `0.106144` | `1.941453` |
| `receiver_lr_lapse_radial_p004_beta075` | `0.106048` | `2.464310` |
| `receiver_lr_lapse_radial_p004_ang_p0015_beta075` | `0.214547` | `2.566714` |

## Interpretation

The alternate realization confirms that the receiver geometry remains
live-safe, but it does not produce a better absorber.

The lapse-only and radial-only variants mostly preserve current, but they do
not relieve J. The paired lapse/radial variant is worse than baseline in
selected-null burden and still raises angular burden. Adding even a small
positive-l angular term improves selected-null, but it roughly doubles
support-edge current and increases angular burden substantially.

Narrative update:

```text
The branch is not out of options, but simple local metric-channel gains are
being squeezed. The only tested knob that moves selected-null is angular
capacity, and every tested positive-l angular realization has carried a
current/angular penalty.
```

Next search should keep the beta-memory localization but test a different
angular/current structure, such as symmetry-balanced angular support,
current-specific receiver constraints, or an explicit source-family
counterterm, rather than increasing local lapse/radial gains.
