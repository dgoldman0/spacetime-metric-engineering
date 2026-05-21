# Stage II Negative-L Receiver Full-Stride and Beta100 Update

Date: 2026-05-21

## Scope

This report records the next promotion checks after the beta075 negative-l
receiver promotion gate:

```text
1. Full-stride intermediate SNEC confirmation on the dense beta075 package.
2. Beta100 stress screen for the p003_mid mechanism candidate.
```

The beta075 mechanism candidate remains `p003_mid`: a persistent beta-memory,
negative-l, mid-localized endpoint receiver with angular gain `0.03`,
inner/outer multipliers `0.50 / 1.025`, and `outer_power = 0.5`.

Beta100 stress spec:

```text
toolkit/adm_harness_cli/specs/endpoint_beta_memory_receiver_p003_mid_beta100_stress.json
```

Beta100 stress outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_p003_mid_beta100_stress_61x83/
```

## Full-Stride Beta075 SNEC

The dense beta075 component/intermediate package was rescanned at full center
stride:

```text
intermediate_sector_sum, tau = 0.5, 1.0, 2.0, center_stride = 1
intermediate_plus_residual, tau = 0.5, 1.0, 2.0, center_stride = 1
```

Each full-stride screen scanned `175,851` affine windows across baseline,
`p003_mid`, and `p003_outer`. Both screens found:

```text
all benchmark-floor violations: 0
scoreable benchmark-floor violations: 0
```

For `p003_mid`, the sector-sum full-stride margins were:

| branch | tau | worst margin to floor | worst smeared Tkk |
| --- | ---: | ---: | ---: |
| minus | `0.5` | `0.990249` | `-0.009751` |
| plus | `0.5` | `0.988862` | `-0.011138` |
| minus | `1.0` | `0.246605` | `-0.003395` |
| plus | `1.0` | `0.245067` | `-0.004933` |
| minus | `2.0` | `0.061556` | `-0.000944` |
| plus | `2.0` | `0.061055` | `-0.001445` |

For `p003_mid`, the residual-inclusive full-stride margins were:

| branch | tau | worst margin to floor | worst smeared Tkk |
| --- | ---: | ---: | ---: |
| minus | `0.5` | `0.982814` | `-0.017186` |
| plus | `0.5` | `0.976813` | `-0.023187` |
| minus | `1.0` | `0.240432` | `-0.009568` |
| plus | `1.0` | `0.240432` | `-0.009568` |
| minus | `2.0` | `0.060200` | `-0.002300` |
| plus | `2.0` | `0.059695` | `-0.002805` |

Interpretation: the beta075 `p003_mid` candidate passes the tougher SNEC
confirmation. The result is not merely a stride-2 artifact. The limiting
windows remain endpoint/residual dominated and stay far above the benchmark
floor.

## Beta100 Stress

The beta100 stress screen compared a beta100 baseline against beta100
`p003_mid` on the `61 x 83` grid.

Both cases were live-clean:

| label | elapsed s | rows | positive live packet-norm samples |
| --- | ---: | ---: | ---: |
| `receiver_neg_beta100_baseline` | `331.006` | `5063` | `0` |
| `receiver_neg_beta100_p003_mid` | `381.199` | `5063` | `0` |

Endpoint coupling:

| label | J selected-null | reset cap | support edge |
| --- | ---: | ---: | ---: |
| beta100 baseline | `0.944764` | `0.371175` | `0.573589` |
| beta100 p003_mid | `0.964451` | `0.393963` | `0.570488` |

Current and angular burden:

| label | support-edge current | support-edge angular |
| --- | ---: | ---: |
| beta100 baseline | `0.133567` | `2.093173` |
| beta100 p003_mid | `0.130470` | `2.096189` |

Transfer accounting:

| target | reset relief | support transfer | net J relief |
| --- | ---: | ---: | ---: |
| selected | `0.012766` | `0.013100` | `-0.000334` |
| current | `0.004862` | `0.002807` | `0.002054` |
| angular | `0.002225` | `0.009043` | `-0.006818` |

The intermediate model remains clean:

```text
weighted total abs reconstruction error: 0.0
live model pair burden:                  0.0
live model selected-null deficit:        0.0
```

## Interpretation

The beta075 promotion is strengthened. `p003_mid` now has dense live-clean
confirmation, clean transfer accounting, stride-2 SNEC companion pass, and
full-stride SNEC pass in both sector-sum and residual-inclusive modes.

The beta100 stress is a timing-sensitivity warning, not a live-safety kill.
The beta100 `p003_mid` case remains live-clean and slightly improves current,
but it worsens J selected-null from `0.944764` to `0.964451` and transfers too
much angular burden into support-edge rows. The selected channel no longer has
positive net J relief, and angular net relief is negative.

Narrative update:

```text
beta075 p003_mid: promotion-grade effective receiver mechanism.
beta100 p003_mid: live-safe but not transfer-clean; do not promote unchanged.
```

This says the negative-l receiver is real but beta-timing sensitive. The
mechanism is strong enough to promote at beta075, but beta100 should not be
treated as already solved by the same geometry. Before any report-grade
physical-source claim, the next discussion should decide whether beta100 is an
acceptable stress boundary or whether a beta100-specific memory/locality
retuning is required.

