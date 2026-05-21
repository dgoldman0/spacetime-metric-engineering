# Stage II Negative-L Receiver Ladder Closeout

Date: 2026-05-20

## Scope

This report records the promoted beta075 negative-l receiver
dose/localization ladder. The goal was to test whether the orientation-smoke
lead was a real receiver channel or a single favorable point.

Outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_negative_l_ladder_smoke_61x83/
```

Spec:

```text
toolkit/adm_harness_cli/specs/endpoint_beta_memory_receiver_negative_l_ladder_smoke.json
```

## Result

All eight `61 x 83` source-ledger cases were live-clean:

| label | elapsed s | rows | positive live packet-norm samples |
| --- | ---: | ---: | ---: |
| `receiver_neg_ladder_baseline_beta075` | `330.944` | `5063` | `0` |
| `receiver_neg_ladder_neg_p00075_outer_beta075` | `363.005` | `5063` | `0` |
| `receiver_neg_ladder_neg_p0015_outer_beta075` | `360.144` | `5063` | `0` |
| `receiver_neg_ladder_neg_p00225_outer_beta075` | `359.193` | `5063` | `0` |
| `receiver_neg_ladder_neg_p003_outer_beta075` | `360.184` | `5063` | `0` |
| `receiver_neg_ladder_neg_p0015_inner_beta075` | `362.748` | `5063` | `0` |
| `receiver_neg_ladder_neg_p0015_narrow_outer_beta075` | `355.622` | `5063` | `0` |
| `receiver_neg_ladder_neg_p0015_short_memory_beta075` | `352.488` | `5063` | `0` |

The default outer negative-l dose ladder gives a coherent selected-null
response:

| label | J selected-null | reset cap | support edge |
| --- | ---: | ---: | ---: |
| baseline | `0.964417` | `0.442605` | `0.521812` |
| negative-l p00075 outer | `0.959711` | `0.438012` | `0.521699` |
| negative-l p0015 outer | `0.954948` | `0.433382` | `0.521566` |
| negative-l p00225 outer | `0.950129` | `0.428714` | `0.521415` |
| negative-l p003 outer | `0.946962` | `0.425718` | `0.521244` |

The cost remains small compared with the positive-l branch. Support-edge
current only moves from `0.105033` at baseline to `0.109344` at p003, while
support-edge angular stays essentially flat:

| label | support-edge current | support-edge angular |
| --- | ---: | ---: |
| baseline | `0.105033` | `1.912497` |
| negative-l p00075 outer | `0.106104` | `1.912376` |
| negative-l p0015 outer | `0.107180` | `1.912350` |
| negative-l p00225 outer | `0.108260` | `1.912494` |
| negative-l p003 outer | `0.109344` | `1.912649` |

The p0015 localization variants separate endpoint performance from transfer
cleanliness:

| label | J selected-null | support-edge selected | support-edge current | support-edge angular |
| --- | ---: | ---: | ---: | ---: |
| p0015 outer | `0.954948` | `0.521566` | `0.107180` | `1.912350` |
| p0015 inner | `0.956318` | `0.518648` | `0.103522` | `1.912389` |
| p0015 narrow outer | `0.953195` | `0.510651` | `0.106905` | `1.909454` |
| p0015 short memory | `0.956984` | `0.509929` | `0.106190` | `1.908480` |

## Transfer Read

The default outer dose ladder has stable transfer ratios. For p00075 through
p00225, selected support transfer is about `0.578` per unit reset relief, so
about `42%` of the selected reset relief remains as net J relief. At p003 the
selected transfer ratio rises to `0.613`, but net J relief still increases.
Current and angular transfer remain nearly neutral in absolute terms:

```text
p003 outer:
  selected reset relief:     0.027857
  selected support transfer: 0.017080
  selected net J relief:     0.010777
  current net J relief:     -0.001524
  angular net J relief:     -0.000174
```

The inner p0015 localization has the cleanest transfer accounting:

```text
p0015 inner:
  selected reset relief:     0.013562
  selected support transfer: 0.000767
  selected net J relief:     0.012795
  current net J relief:      0.001127
  angular net J relief:      0.002295
```

However, the endpoint coupling table gives better total J for p0015
narrow-outer than p0015 inner. Narrow-outer appears to improve endpoint totals
by reshaping support-edge burden more aggressively, while inner gives a
cleaner reset-to-support exchange.

## Interpretation

The negative-l branch is no longer a single-point anomaly. It is a live-clean,
orientation-specific receiver channel with coherent dose response. This is the
first tested local receiver realization that reduces endpoint J selected-null
while keeping support-edge current and angular burden close to the beta075
baseline.

The physical-feasibility narrative improves, but remains pre-certification.
The result supports a persistent beta-memory endpoint receiver rather than a
generic metric smear. The short-memory case underperforms the main outer dose
ladder, which argues that the post-release memory tail is doing real work.
The branch still needs denser-grid confirmation, endpoint-local SNEC, and
eventual conservation/source-family closure before report-grade matter-model
claims.

Recommended next branch:

```text
Use p003 outer as the performance anchor.
Use p0015 inner as the transfer-cleanliness anchor.
Run a focused locality refinement around p00225/p003:
  inner-to-outer interpolation,
  narrow outer with longer memory,
  default outer with slightly reduced support transfer,
  optional p003 inner/narrow companions.
Only after this geometry decision, run a denser-grid promotion or beta100
stress case.
```

