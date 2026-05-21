# Stage II Negative-L Receiver Beta100 Retiming and Locality Screen

Date: 2026-05-21

## Scope

This report records a bounded beta100 follow-up to the negative-l beta-memory
receiver stress result. The prior beta100 `p003_mid` run was live-safe but not
transfer-clean: it kept zero positive live packet-norm samples and a clean
intermediate live gate, but selected and angular endpoint accounting no longer
closed the way it did at beta075.

The purpose here is not to change the source family. It is a small
receiver-side flexibility screen:

```text
1. Retiming: shorten receiver post-release persistence.
2. Strength: reduce receiver memory gain.
3. Locality: move the receiver mask inward or outward.
```

The beta075 promoted mechanism remains `p003_mid`: negative-l angular receiver,
receiver angular gain `0.03`, inner/outer multipliers `0.50 / 1.025`, and
`outer_power = 0.5`.

New spec:

```text
toolkit/adm_harness_cli/specs/endpoint_beta_memory_receiver_p003_mid_beta100_retiming_locality_small.json
```

New outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_p003_mid_beta100_retiming_locality_small_61x83/
```

The run reuses the prior beta100 stress seed and grid:

```text
source seed: toolkit/adm_harness_cli/runs/stage2_external/stage2_entry_sector_closure_candidate_ledger_151x225/wide4_start_m1p40
grid:        61 x 83
s range:     -1.5 to 2.4
l range:     -4.2 to 4.2
h_s, h_l:    0.0025, 0.0025
```

## Variant Set

The screen adds five beta100 variants to the prior beta100 baseline and prior
beta100 `p003_mid` result:

| label | change from beta100 `p003_mid` |
| --- | --- |
| `receiver_neg_beta100_p003_mid_post1p0` | post-release persistence `2.0 -> 1.0` |
| `receiver_neg_beta100_p003_mid_post1p5` | post-release persistence `2.0 -> 1.5` |
| `receiver_neg_beta100_p003_mid_gain1p0` | memory gain `2.0 -> 1.0` |
| `receiver_neg_beta100_p003_inner` | inner mask, multipliers `0.35 / 0.85`, `outer_power = 0.0` |
| `receiver_neg_beta100_p003_outer` | default outer receiver mask |

All variants preserve beta100 release timing:

```text
release_beta_width_multiplier = 1.0
release_choreography_mode     = matched_hold
release_matched_hold_widths   = 0.25
release_beta_profile          = minimum_jerk
```

## Stage II Ledgers

All beta100 cases in the combined comparison were live-clean:

| label | elapsed s | rows | positive live packet-norm samples |
| --- | ---: | ---: | ---: |
| `receiver_neg_beta100_baseline` | `331.006` | `5063` | `0` |
| `receiver_neg_beta100_p003_mid` | `381.199` | `5063` | `0` |
| `receiver_neg_beta100_p003_mid_post1p0` | `364.610` | `5063` | `0` |
| `receiver_neg_beta100_p003_mid_post1p5` | `371.189` | `5063` | `0` |
| `receiver_neg_beta100_p003_mid_gain1p0` | `372.293` | `5063` | `0` |
| `receiver_neg_beta100_p003_inner` | `371.692` | `5063` | `0` |
| `receiver_neg_beta100_p003_outer` | `373.110` | `5063` | `0` |

Interpretation: the beta100 issue remains a robustness/timing-margin issue, not
a live-safety issue. None of the retiming or locality probes contaminated the
packet corridor.

## Endpoint Coupling

Endpoint J selected-null and support-edge burdens:

| label | J selected-null | reset cap | support edge | support-edge current | support-edge angular |
| --- | ---: | ---: | ---: | ---: | ---: |
| `receiver_neg_beta100_baseline` | `0.944764` | `0.371175` | `0.573589` | `0.133567` | `2.093173` |
| `receiver_neg_beta100_p003_mid` | `0.964451` | `0.393963` | `0.570488` | `0.130470` | `2.096189` |
| `receiver_neg_beta100_p003_mid_post1p0` | `0.958979` | `0.392233` | `0.566746` | `0.131705` | `2.095779` |
| `receiver_neg_beta100_p003_mid_post1p5` | `0.949286` | `0.378798` | `0.570488` | `0.130470` | `2.096189` |
| `receiver_neg_beta100_p003_mid_gain1p0` | `0.934785` | `0.365917` | `0.568868` | `0.131373` | `2.094149` |
| `receiver_neg_beta100_p003_inner` | `0.962606` | `0.397611` | `0.564995` | `0.128881` | `2.094128` |
| `receiver_neg_beta100_p003_outer` | `0.959005` | `0.381607` | `0.577398` | `0.139486` | `2.098105` |

The coupling read is mixed:

```text
post1p5 improves the old beta100 p003_mid J selected-null from 0.964451 to
0.949286, but remains slightly above the beta100 baseline at 0.944764.

gain1p0 is the only probe that beats the beta100 baseline in raw J selected
null, lowering it to 0.934785, but its angular transfer accounting remains
slightly negative.

outer is clearly too costly at beta100: support-edge current and angular both
rise, and raw J remains worse than baseline.
```

## Transfer Accounting

Transfer accounting compares each variant to the beta100 baseline. Positive
net J relief means reset relief exceeds support-edge transfer for that target.

| label | target | reset relief | support transfer | support / reset | net J relief |
| --- | --- | ---: | ---: | ---: | ---: |
| `receiver_neg_beta100_p003_mid` | selected | `0.012766` | `0.013100` | `1.026202` | `-0.000334` |
| `receiver_neg_beta100_p003_mid` | current | `0.004862` | `0.002807` | `0.577438` | `0.002054` |
| `receiver_neg_beta100_p003_mid` | angular | `0.002225` | `0.009043` | `4.064618` | `-0.006818` |
| `receiver_neg_beta100_p003_mid_post1p0` | selected | `0.000873` | `0.015173` | `17.373487` | `-0.014299` |
| `receiver_neg_beta100_p003_mid_post1p0` | current | `0.002180` | `0.004459` | `2.045994` | `-0.002280` |
| `receiver_neg_beta100_p003_mid_post1p0` | angular | `0.000025` | `0.008547` | `344.889105` | `-0.008523` |
| `receiver_neg_beta100_p003_mid_post1p5` | selected | `0.020613` | `0.013100` | `0.635519` | `0.007513` |
| `receiver_neg_beta100_p003_mid_post1p5` | current | `0.003385` | `0.002807` | `0.829298` | `0.000578` |
| `receiver_neg_beta100_p003_mid_post1p5` | angular | `0.021867` | `0.009043` | `0.413541` | `0.012824` |
| `receiver_neg_beta100_p003_mid_gain1p0` | selected | `0.023035` | `0.007826` | `0.339747` | `0.015209` |
| `receiver_neg_beta100_p003_mid_gain1p0` | current | `0.002539` | `0.002061` | `0.811448` | `0.000479` |
| `receiver_neg_beta100_p003_mid_gain1p0` | angular | `0.005160` | `0.005714` | `1.107502` | `-0.000555` |
| `receiver_neg_beta100_p003_inner` | selected | `0.011551` | `0.002914` | `0.252256` | `0.008638` |
| `receiver_neg_beta100_p003_inner` | current | `0.004364` | `0.000228` | `0.052307` | `0.004135` |
| `receiver_neg_beta100_p003_inner` | angular | `0.002319` | `0.004406` | `1.900450` | `-0.002088` |
| `receiver_neg_beta100_p003_outer` | selected | `0.012660` | `0.025560` | `2.018909` | `-0.012899` |
| `receiver_neg_beta100_p003_outer` | current | `0.005208` | `0.007692` | `1.476893` | `-0.002484` |
| `receiver_neg_beta100_p003_outer` | angular | `0.000037` | `0.009472` | `253.157114` | `-0.009434` |

Transfer interpretation:

```text
post1p5 is the cleanest beta100 repair by endpoint accounting. It is the only
screened variant with positive selected, current, and angular net J relief.

gain1p0 is the best raw-J candidate and has strong selected relief, but angular
net relief remains slightly negative (-0.000555). It is promising but not as
clean as post1p5 under the transfer criterion.

inner improves selected and current transfer but still over-transfers angular.

post1p0 and outer fail the accounting badly. The receiver tail cannot simply
be shortened aggressively, and the default outer band is too broad/costly for
beta100.
```

## Intermediate Source Checks

The combined component/source package passed the intermediate live gate:

| sector | points | live rows | live pair fraction | live selected-null fraction | passes live gate |
| --- | ---: | ---: | ---: | ---: | --- |
| `J_endpoint_junction_layer` | `1172` | `0` | `0.0` | `0.0` | `True` |
| `S0_constant_flux_string_cloud` | `2119` | `0` | `0.0` | blank | `True` |
| `core_body_residual_leakage` | `947` | `0` | `0.0` | `0.0` | `True` |

Reconstruction closure:

```text
points:                                      14833
model rows:                                  29666
weighted total abs reconstruction error:     6.383625e-12
weighted total abs error per pair norm:      5.821142e-15
max abs rho error:                           1.040834e-16
max abs p_l error:                           1.110223e-16
max abs j_l error:                           0.0
max abs p_omega error:                       0.0
live model pair burden:                      0.0
live model selected-null deficit:            0.0
```

Interpretation: the retiming/locality screen does not introduce a
reconstruction or intermediate live-gate issue. The effective source package
continues to reconstruct the demanded component package to numerical
precision, and all modeled sector burden remains non-live.

## SNEC Companion

A light residual-inclusive intermediate SNEC companion was run on the combined
beta100 package:

```text
total mode:    intermediate_plus_residual
tau:           0.5, 1.0, 2.0
center stride: 2
windows:       105798
```

Summary by label:

| label | benchmark violations | worst margin to floor | worst smeared Tkk | minimum scoreable windows |
| --- | ---: | ---: | ---: | ---: |
| `receiver_neg_beta100_baseline` | `0` | `0.059410` | `-0.028167` | `676` |
| `receiver_neg_beta100_p003_mid` | `0` | `0.059410` | `-0.028167` | `676` |
| `receiver_neg_beta100_p003_mid_post1p0` | `0` | `0.059410` | `-0.028167` | `676` |
| `receiver_neg_beta100_p003_mid_post1p5` | `0` | `0.059410` | `-0.028167` | `676` |
| `receiver_neg_beta100_p003_mid_gain1p0` | `0` | `0.059410` | `-0.028167` | `676` |
| `receiver_neg_beta100_p003_inner` | `0` | `0.059410` | `-0.028167` | `676` |
| `receiver_neg_beta100_p003_outer` | `0` | `0.059410` | `-0.028167` | `676` |

Interpretation: the SNEC companion does not distinguish the beta100 receiver
variants at this coarse stress scale. All remain above the benchmark floor
with zero scoreable violations. The beta100 question is therefore endpoint
transfer timing, not SNEC safety.

## Decision Read

The beta100 stress result should be reclassified:

```text
old read: beta100 p003_mid is live-safe but transfer-failed.
new read: beta100 p003_mid is live-safe and retimable; unretimed p003_mid is
          transfer-failed, but post1p5 repairs transfer accounting.
```

This does not change the main promotion target. Beta075 `p003_mid` remains the
promotion-worthy design regime. Beta100 should still not be claimed as already
robust under the beta075 geometry. But beta100 is no longer evidence that the
mechanism has no nearby timing flexibility.

Recommended language:

```text
Beta075 p003_mid is the promoted receiver mechanism.
Beta100 is a live-safe stress boundary for the unchanged beta075 receiver.
A beta100-specific retiming with receiver_post_release_widths = 1.5 gives
positive selected/current/angular transfer accounting on the 61 x 83 stress
grid and passes the same live/intermediate/SNEC companions used here.
```

## Physical Interpretation

The result points to a narrow phase-match rather than a failed source model.
At beta100, the wider beta fade changes when the reset burden is relieved and
when support-edge memory is active. The unchanged beta075 receiver tail
overlaps the wrong part of that transfer: selected net relief is near zero and
angular is over-transferred. Shortening the tail mildly to `1.5` restores a
three-channel transfer story. Shortening it too far to `1.0` destroys reset
relief and produces severe over-transfer.

The mechanism therefore looks credible but timing-sensitive:

```text
live safety:          robust across tested beta100 variants
intermediate closure: robust
SNEC companion:       robust at this coarse tau set
endpoint accounting:  finite operating window; beta100 needs retiming
```

This is useful future-design information. If later designs carry more
workload or use wider beta-release fades, the receiver should not be scaled by
geometry alone. It should carry a phase/tail knob, with `post1p5` as the first
documented beta100 retiming anchor and `gain1p0` as a secondary raw-J anchor.

## Artifacts

Primary spec:

```text
toolkit/adm_harness_cli/specs/endpoint_beta_memory_receiver_p003_mid_beta100_retiming_locality_small.json
```

Primary run root:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_p003_mid_beta100_retiming_locality_small_61x83/
```

Key generated files:

```text
ledgers/stage2_candidate_ledgers_index.csv
component_all/component_source_manifest.json
string_all/radial_string_cloud_manifest.json
intermediate_all/intermediate_source_model_manifest.json
coupling_diagnostic/endpoint_coupling_diagnostic_summary.csv
receiver_basis_beta100_small/beta_support_receiver_transfer_summary.csv
intermediate_snec_plus_residual_tau050_100_200/intermediate_source_snec_summary.csv
```

Note: `toolkit/adm_harness_cli/runs/` is intentionally git-ignored as generated
output. This report and the JSON spec are the tracked durable record for the
screen.
