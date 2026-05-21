# Stage II Negative-L Receiver Promotion Gate

Date: 2026-05-21

## Scope

This report records the first two promotion-gate tests for the beta075
negative-l receiver branch:

```text
1. Dense `81 x 121` confirmation for baseline, p003_mid, and p003_outer.
2. Intermediate endpoint/source SNEC companion at affine widths 0.5, 1.0, 2.0.
```

The candidate mechanism is `p003_mid`: a negative-l angular receiver with
inner/outer multipliers `0.50 / 1.025` and `outer_power = 0.5`. The comparison
benchmark is `p003_outer`, the stronger raw-J performer from the locality
screen.

Dense spec:

```text
toolkit/adm_harness_cli/specs/endpoint_beta_memory_receiver_negative_l_promotion_dense.json
```

Dense outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_negative_l_promotion_dense_81x121/
```

## Gate 1: Dense Confirmation

All three dense source ledgers were live-clean:

| label | elapsed s | rows | positive live packet-norm samples |
| --- | ---: | ---: | ---: |
| `receiver_neg_promotion_baseline_beta075` | `637.885` | `9801` | `0` |
| `receiver_neg_promotion_p003_mid_beta075` | `695.011` | `9801` | `0` |
| `receiver_neg_promotion_p003_outer_beta075` | `686.423` | `9801` | `0` |

Dense coupling results:

| label | J selected-null | reset cap | support edge |
| --- | ---: | ---: | ---: |
| baseline | `0.970928` | `0.446198` | `0.524730` |
| p003_mid | `0.958663` | `0.438846` | `0.519817` |
| p003_outer | `0.939090` | `0.427592` | `0.511498` |

Current and angular burden:

| label | support-edge current | support-edge angular |
| --- | ---: | ---: |
| baseline | `0.105652` | `1.776316` |
| p003_mid | `0.103295` | `1.776302` |
| p003_outer | `0.108702` | `1.774882` |

Transfer accounting:

| label | target | reset relief | support transfer | net J relief |
| --- | --- | ---: | ---: | ---: |
| p003_mid | selected | `0.026155` | `0.007963` | `0.018193` |
| p003_mid | current | `0.003100` | `0.002012` | `0.001089` |
| p003_mid | angular | `0.006451` | `0.004490` | `0.001961` |
| p003_outer | selected | `0.030785` | `0.016836` | `0.013949` |
| p003_outer | current | `0.004204` | `0.005619` | `-0.001415` |
| p003_outer | angular | `0.004731` | `0.007575` | `-0.002844` |

Dense interpretation: `p003_mid` keeps the mechanism narrative intact under
grid refinement. It gives smaller raw J relief than `p003_outer`, but it lowers
support-edge current versus baseline and has positive net relief in selected,
current, and angular transfer. `p003_outer` is the raw endpoint-performance
benchmark, but its current/angular transfer turns negative.

## Gate 2: SNEC Companion

Two intermediate source SNEC companion screens were run on the dense component
and intermediate outputs:

```text
intermediate_sector_sum, tau = 0.5, 1.0, 2.0, center_stride = 2
intermediate_plus_residual, tau = 0.5, 1.0, 2.0, center_stride = 2
```

Each screen scanned `87,912` affine windows across the three labels. Both
screens found:

```text
all benchmark-floor violations: 0
scoreable benchmark-floor violations: 0
```

For the sector-sum screen, the worst scoreable margins for `p003_mid` were:

| branch | tau | worst margin to floor | worst smeared Tkk |
| --- | ---: | ---: | ---: |
| minus | `0.5` | `0.990249` | `-0.009751` |
| plus | `0.5` | `0.989155` | `-0.010845` |
| minus | `1.0` | `0.246629` | `-0.003371` |
| plus | `1.0` | `0.245067` | `-0.004933` |
| minus | `2.0` | `0.061568` | `-0.000932` |
| plus | `2.0` | `0.061055` | `-0.001445` |

For the residual-inclusive screen, the worst scoreable margins for `p003_mid`
were:

| branch | tau | worst margin to floor | worst smeared Tkk |
| --- | ---: | ---: | ---: |
| minus | `0.5` | `0.982886` | `-0.017114` |
| plus | `0.5` | `0.976813` | `-0.023187` |
| minus | `1.0` | `0.240432` | `-0.009568` |
| plus | `1.0` | `0.240432` | `-0.009568` |
| minus | `2.0` | `0.060292` | `-0.002208` |
| plus | `2.0` | `0.059821` | `-0.002679` |

The limiting sectors remain endpoint/residual dominated, not live-packet
dominated. In the sector-sum screen, the dominant negative sector is generally
`J_endpoint_junction_layer`. In the residual-inclusive screen it is generally
`intermediate_unmodeled_residual`, which is expected because that mode carries
the residual explicitly.

Closure/live summaries remain clean:

```text
weighted total abs reconstruction error:        0.0
weighted total abs error per pair norm:         0.0
live model pair burden:                         0.0
live model selected-null deficit:               0.0
J_endpoint_junction_layer live rows:            0
S0_constant_flux_string_cloud live rows:        0
core_body_residual_leakage live rows:           0
```

## Promotion Read

The first two promotion gates pass. The negative-l receiver branch survives
dense sampling and the endpoint/intermediate SNEC companion without live packet
contamination or benchmark-floor violations.

Recommended promotion:

```text
Promote p003_mid as the mechanism candidate.
Keep p003_outer as the performance benchmark.
Do not promote p003_outer as the primary physical candidate yet, because its
raw J relief is stronger but its current/angular transfer accounting is worse.
```

Narrative update: the branch now has a credible physical-feasibility shape. It
is not merely a smoke-grid metric trick. The promoted mechanism is a persistent
beta-memory, negative-l, mid-localized endpoint receiver that reduces dense
endpoint J burden, preserves the live gate, improves or preserves current and
angular transfer, and passes the first endpoint/intermediate SNEC companion.

Remaining before report-grade physical-source claims:

```text
1. Commit promotion materials and align the handoff plan.
2. Run a denser or full-stride SNEC pass if needed for final certification.
3. Stress p003_mid at beta100 only after the beta075 promotion is accepted.
4. Replace the effective receiver grammar with a constrained source-family or
   conservation-closed matter-model candidate.
```

