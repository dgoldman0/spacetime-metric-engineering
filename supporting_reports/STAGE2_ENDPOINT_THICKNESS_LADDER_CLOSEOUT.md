# Stage II Endpoint Thickness Ladder Closeout

## Summary

The endpoint-focused ladder closes the current intermediate endpoint source
model as a useful diagnostic artifact, not as a complete physical source model.
The model still supports the Stage I architecture as a protected live packet
corridor coupled to a non-live support plant, but it does not absorb the
endpoint obligation by finite endpoint thickening, mild edge softening,
current-guard blending, or broader timing.

The key result is invariance. Six live-clean endpoint variants leave the
coupled endpoint/junction layer essentially unchanged. The only variant that
moves the endpoint burden in a noticeable direction is temporal broadening, and
that variant introduces a live packet-norm defect.

Interpretation:

```text
This source model has reached closeout.
It is not a design kill.
It says the next source model must be an explicit endpoint/junction plant,
especially for reset/release current relaxation and conservation closure.
```

## Inputs

Recently committed endpoint theory memo:

```text
supporting_reports/STAGE2_ENDPOINT_THEORY_MEMO.md
```

Ladder specification:

```text
toolkit/adm_harness_cli/specs/endpoint_thickness_ladder_smoke.json
```

Run outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_thickness_ladder_smoke_81x121/ledgers/
toolkit/adm_harness_cli/runs/endpoint_thickness_ladder_smoke_81x121/component_all/
toolkit/adm_harness_cli/runs/endpoint_thickness_ladder_smoke_81x121/string_all/
toolkit/adm_harness_cli/runs/endpoint_thickness_ladder_smoke_81x121/intermediate_all/
toolkit/adm_harness_cli/runs/endpoint_thickness_ladder_smoke_81x121/coupling_diagnostic/
toolkit/adm_harness_cli/runs/endpoint_thickness_ladder_smoke_81x121/snec_all_stride24_tau050_100_200/
```

New diagnostic tooling:

```text
toolkit/adm_harness_cli/scripts/run_endpoint_coupling_diagnostic.py
```

All results below are demanded-source and intermediate-source diagnostics. They
are not a continuum conservation proof, quantum RSET calculation, matter-model
solve, or no-go theorem.

## Ladder Cases

The ladder used the current compact entry-gated endpoint settings as baseline:

```text
live_packet_start = -1.40
entry_carve = 0.75
entry_width_multiplier = 4.8
catch_carve = 0.15
catch_width_multiplier = 3.4
edge_carve = 0.16
edge_width_multiplier = 7.2
temporal_profile = tanh
radial_profile = compact_smoothstep7
composition = additive
null_gain = -0.07
```

The variants tested:

| label | change |
| --- | --- |
| `endpoint_base_wide4_start_m1p40` | baseline |
| `endpoint_edge_wide9` | edge width `7.2 -> 9.0` |
| `endpoint_edge_wide11` | edge width `7.2 -> 11.0` |
| `endpoint_catch_edge_wide` | catch width `3.4 -> 4.2`, edge width `7.2 -> 9.0` |
| `endpoint_edge_soft_wide9` | edge carve `0.16 -> 0.12`, edge width `9.0` |
| `endpoint_guard_blend_wide9` | current guard fraction `0.25`, guard mode `blend` |
| `endpoint_temporal_wide14` | temporal width multiplier `1.0 -> 1.4` |

The ledger pass ran on an `81 x 121` smoke grid over:

```text
s in [-1.50, 2.40]
l in [-4.20, 4.20]
```

## Ledger Result

Six of seven cases remain live-clean:

| label | elapsed s | positive live packet-norm samples |
| --- | ---: | ---: |
| `endpoint_base_wide4_start_m1p40` | `648.952` | `0` |
| `endpoint_edge_wide9` | `647.615` | `0` |
| `endpoint_edge_wide11` | `630.862` | `0` |
| `endpoint_catch_edge_wide` | `639.076` | `0` |
| `endpoint_edge_soft_wide9` | `637.128` | `0` |
| `endpoint_guard_blend_wide9` | `932.735` | `0` |
| `endpoint_temporal_wide14` | `652.269` | `1` |

The temporal-width case has the only direct live safety blemish:

```text
label:       endpoint_temporal_wide14
s:           -0.76875
l:           -0.42
stage:       entry_precatch
region:      packet_in_support
packet_norm: 16.807818
```

This is a concrete live packet overlap, not merely a global aggregate change.

## Endpoint Junction Burden

The coupled endpoint/junction layer `J_endpoint_junction_layer` remains
essentially invariant under the live-clean ladder cases:

| label | J selected-null deficit | delta vs baseline | support-edge deficit | reset-cap deficit | live defect |
| --- | ---: | ---: | ---: | ---: | ---: |
| `endpoint_base_wide4_start_m1p40` | `0.990430395` | `0` | `0.422016728` | `0.568413667` | `0` |
| `endpoint_edge_wide9` | `0.990424465` | `-0.000005930` | `0.422010798` | `0.568413667` | `0` |
| `endpoint_edge_wide11` | `0.990415489` | `-0.000014906` | `0.422001822` | `0.568413667` | `0` |
| `endpoint_catch_edge_wide` | `0.990422641` | `-0.000007754` | `0.422008974` | `0.568413667` | `0` |
| `endpoint_edge_soft_wide9` | `0.990461159` | `0.000030764` | `0.422047492` | `0.568413667` | `0` |
| `endpoint_guard_blend_wide9` | `0.990516490` | `0.000086095` | `0.422103855` | `0.568412635` | `0` |
| `endpoint_temporal_wide14` | `0.991488117` | `0.001057722` | `0.422984407` | `0.568503710` | `1` |

The reset cap is the most stubborn piece. Across the live-clean width and guard
variants, its selected-null deficit stays fixed at approximately `0.568414`.
The support-edge shoulder moves only in the fifth or sixth decimal place.

## Effective-Coupling Diagnostic

The endpoint coupling diagnostic asks whether the J-layer burden dilutes over a
larger active/effective support volume, or whether it behaves like a fixed
localized endpoint cap. It summarizes:

```text
selected-null deficit
static radial deficit
current-selected deficit
active volume
mean and peak selected-deficit density
effective burden volume
rows needed to carry 50% and 80% of burden
current/angular ratios
```

It is a scaling and concentration proxy, not a conservation proof.

Baseline J readout:

| scope | active volume | selected deficit | static deficit | current-selected deficit | current share | effective volume fraction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `J_total` | `2597.71145` | `0.990430395` | `0.405818098` | `0.584612297` | `0.590260860` | `0.023079919` |
| `support_edge` | `2525.74806` | `0.422016728` | `0.295909062` | `0.126107667` | `0.298821488` | `0.037041180` |
| `reset_cap` | `71.96338` | `0.568413667` | `0.109909036` | `0.458504630` | `0.806638998` | `0.310537354` |

The support-edge shoulder is the more radial/throat-like subproblem: mostly
static/radial selected deficit, larger support volume, and stronger peak
concentration. The reset cap is smaller in volume and strongly current-selected:
about `80.7%` of its selected deficit is current-selected.

Diagnostic contrast:

| label | J delta fraction vs baseline | J effective-volume fraction | effective-volume delta | current share | diagnostic read |
| --- | ---: | ---: | ---: | ---: | --- |
| `endpoint_base_wide4_start_m1p40` | `0` | `0.023079919` | `0` | `0.590260860` | `endpoint_invariant_no_relief` |
| `endpoint_edge_wide9` | `-0.000005987` | `0.023114042` | `0.000034122` | `0.590261471` | `endpoint_invariant_no_relief` |
| `endpoint_edge_wide11` | `-0.000015050` | `0.023152852` | `0.000072933` | `0.590257167` | `endpoint_invariant_no_relief` |
| `endpoint_catch_edge_wide` | `-0.000007829` | `0.023114161` | `0.000034242` | `0.590261167` | `endpoint_invariant_no_relief` |
| `endpoint_edge_soft_wide9` | `0.000031061` | `0.023072666` | `-0.000007253` | `0.590227790` | `endpoint_invariant_no_relief` |
| `endpoint_guard_blend_wide9` | `0.000086927` | `0.023179838` | `0.000099918` | `0.590448303` | `endpoint_invariant_no_relief` |
| `endpoint_temporal_wide14` | `0.001067941` | `0.023361688` | `0.000281768` | `0.592293398` | `worsens_live_gate` |

The diagnostic result is therefore not merely "the integral did not move." It
says the endpoint obligation does not dilute over the tested endpoint thickness
or mild coupling knobs. The apparent support volume changes, but the effective
burden fraction and current share stay effectively fixed for the live-clean
variants.

## Concentration Read

The J concentration metrics are also stable:

```text
baseline J rows for 50% burden: 18.56%
baseline J rows for 80% burden: 38.54%
```

These values remain unchanged to practical grid precision for the live-clean
width, softening, and guard variants. The support-edge shoulder remains more
peak-concentrated than the reset cap:

```text
support-edge rows for 50% burden: 14.31%
support-edge rows for 80% burden: 33.43%

reset-cap rows for 50% burden: 23.86%
reset-cap rows for 80% burden: 46.49%
```

This supports a two-piece endpoint interpretation:

```text
support-edge shoulder: radial/throat-like support shoulder
reset cap: current-selected release/decompression terminator
```

## SNEC Companion

A coarse all-label intermediate-source SNEC smoke was run as a companion check:

```text
outdir: toolkit/adm_harness_cli/runs/endpoint_thickness_ladder_smoke_81x121/snec_all_stride24_tau050_100_200/
center stride: 24
tau: 0.5, 1.0, 2.0
windows scanned: 17052
raw benchmark-floor violations: 0
scoreable benchmark-floor violations: 0
```

Worst scoreable margins remain far above the benchmark floor. For the baseline:

| tau | branch | worst total | floor | margin | dominant sector |
| ---: | --- | ---: | ---: | ---: | --- |
| `0.5` | minus | `-0.008833` | `-1.000000` | `0.991167` | `J_endpoint_junction_layer` |
| `0.5` | plus | `-0.008468` | `-1.000000` | `0.991532` | `J_endpoint_junction_layer` |
| `1.0` | minus | `-0.002394` | `-0.250000` | `0.247606` | `J_endpoint_junction_layer` |
| `1.0` | plus | `-0.001269` | `-0.250000` | `0.248731` | `intermediate_unmodeled_residual` |
| `2.0` | minus | `-0.000850` | `-0.062500` | `0.061650` | `J_endpoint_junction_layer` |
| `2.0` | plus | `-0.000576` | `-0.062500` | `0.061924` | `intermediate_unmodeled_residual` |

This keeps the endpoint concern in the physical-source/completion category. It
does not turn the ladder result into an immediate affine smeared-null failure.

## Closeout Interpretation

This intermediate source model has served its purpose. It established that:

```text
1. A constant-flux radial string cloud can represent the broad non-live body.
2. The remaining endpoint layer is coupled, not three independent small trims.
3. The endpoint burden is live-clean in the baseline and most variants.
4. The endpoint burden is not relieved by simple thickness/edge/catch knobs.
5. Temporal broadening is a bad lever because it creates live packet leakage.
```

The result is not surprising in kind, because the model was explicitly
intermediate and incomplete. It is informative in strength: the endpoint
obligation is stubborn enough that the next model should not try to hide it by
another mask smear.

The current design is therefore not ruled out, but its physical feasibility now
depends on whether the endpoint can be represented by a finite, conserved
junction source family. The next source model should target:

```text
J0: radial support shoulder / finite-tension endpoint scaffold
J1: reset-release current relaxation cap
J2: angular capacity jacket coupled to J0/J1
```

The first refinement should vary reset/release choreography rather than only
support-edge thickness:

```text
release matched-hold width
release beta width multiplier
lapse/carve lag through reset
reset cap thickness or taper
current-relaxation width and sign structure
```

The next diagnostic should be a conservation/effective-coupling closure test:

```text
Does reset current-selected deficit scale down with reset/release thickness?
Does the finite-difference momentum/pressure residual remain bounded?
Does angular capacity remain coupled without live packet overlap?
Does any proxy coupling grow like an inverse thickness wall?
```

If the answer is finite and bounded, the endpoint becomes an exotic but
well-posed source-family target. If the answer is invariant, sharpening, or
coupling-divergent under true reset/release thickness changes, then the endpoint
becomes the likely feasibility blocker.
