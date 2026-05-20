# Stage II Endpoint-Junction Source Milestone

## Summary

The entry-gated `wide4_start_m1p40` source track has reached a useful but
more sobering milestone. The Stage I architecture still holds under the current
source-placement gates:

```text
live packet norm: clean
live packet burden: localized and controlled
constant-flux radial cloud: non-live backbone
broad hard-affine SNEC: clean at tau = 2.0, 3.0, 4.0
```

But the endpoint residual is no longer just a bookkeeping nuisance. The
intermediate source work now says the support-edge shoulder and
reset/decompression cap should be treated as a coupled endpoint/junction source
problem. That is exactly the place where a Barcelo/Visser-style concern can
enter: a construction can protect the desired corridor while forcing the exotic
or trans-Planckian cost to appear somewhere else.

The current diagnostics do not show a failure. They show a sharper gate. The
main unresolved physical question is whether the endpoint/junction layer can be
made into a finite-width, conserved, physically admissible source family, or
whether it is merely the localized place where the hard cost has been hidden.

## Inputs

Representative branch:

```text
label = wide4_start_m1p40
live_packet_start = -1.40
entry_carve = 0.75
entry_width_multiplier = 4.8
catch_carve = 0.15
catch_width_multiplier = 3.4
edge_carve = 0.16
edge_width_multiplier = 7.2
null_cushion_log_gain = -0.07
```

Dense component source closure:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_entry_sector_closure_component_source_151x225_refined_roles/
```

Radial string-cloud replacement:

```text
toolkit/adm_harness_cli/runs/radial_string_cloud_replacement_entry_closure_151x225/
```

Previous split intermediate source model:

```text
toolkit/adm_harness_cli/runs/intermediate_source_model_entry_closure_151x225/
```

Dense split intermediate SNEC screen:

```text
toolkit/adm_harness_cli/runs/intermediate_source_snec_entry_closure_151x225_dense_tau200_300_400/
```

Updated endpoint-junction intermediate model:

```text
toolkit/adm_harness_cli/runs/intermediate_source_model_entry_closure_151x225_junction/
```

Sampled endpoint-junction SNEC screen:

```text
toolkit/adm_harness_cli/runs/intermediate_source_snec_entry_closure_151x225_junction_stride16_tau200_300_400/
```

New/updated tooling:

```text
toolkit/adm_harness_cli/adm_harness/intermediate_source_model.py
toolkit/adm_harness_cli/adm_harness/intermediate_source_snec.py
toolkit/adm_harness_cli/scripts/run_intermediate_source_model.py
toolkit/adm_harness_cli/tests/test_intermediate_source_model.py
toolkit/adm_harness_cli/tests/test_intermediate_source_snec.py
```

These are demanded-source diagnostics. They are not a conservation proof,
quantum RSET calculation, matter model, or SNEC theorem.

## What Held

The previous split intermediate model exactly reconstructed the demanded point
stress after subtracting the radial string-cloud core:

```text
points:                                  14457
model rows:                              47896
weighted total absolute closure error:   9.508886e-13
closure error / pair norm:               6.149764e-15
live model pair burden:                  0.000000
live selected-null deficit:              0.000000
```

Its dense hard-affine SNEC comparison also held:

```text
windows scanned:                         203838
tau:                                     2.0, 3.0, 4.0
raw benchmark-floor violations:          0
scoreable benchmark-floor violations:    0
```

Worst dense split intermediate sector-sum margins:

| tau | branch | worst total | floor | margin | dominant sector |
| ---: | --- | ---: | ---: | ---: | --- |
| `2.0` | minus | `-0.000998` | `-0.062500` | `0.061502` | `intermediate_unmodeled_residual` |
| `2.0` | plus | `-0.001223` | `-0.062500` | `0.061277` | `DH_current_relaxation` |
| `3.0` | minus | `-0.000485` | `-0.027778` | `0.027293` | `DH_current_relaxation` |
| `3.0` | plus | `-0.000619` | `-0.027778` | `0.027159` | `DH_current_relaxation` |
| `4.0` | minus | `-0.000318` | `-0.015625` | `0.015307` | `DH_current_relaxation` |
| `4.0` | plus | `-0.000378` | `-0.015625` | `0.015247` | `DH_current_relaxation` |

This is consistent with the earlier dense Stage II source-sector closure: the
architecture is not failing the broad smeared-null gate, and the limiting
windows are not live-packet conditions.

## Why The Model Changed

The split model was diagnostically useful, but it treated endpoint work as three
separate residual trims:

```text
S1: support-edge shoulder radial trim
S2: reset/decompression endpoint radial cap
G: angular endpoint capacity
D/H: current relaxation
```

That split started to obscure the real physical question. The endpoint does not
look like three independent small repairs. It looks like one localized junction
layer that must carry radial tension/pressure balance, angular capacity, and
current relaxation together.

The updated intermediate model therefore uses:

```text
S0_constant_flux_string_cloud
J_endpoint_junction_layer
core_body_residual_leakage
```

The pointwise demanded stress is unchanged. The update is a source grammar
change, not a new metric or an improved fit by fiat.

## Junction Model Result

The endpoint-junction model exactly reconstructs the same demanded point stress:

```text
points:                                  14457
model rows:                              28914
weighted total absolute closure error:   9.508886e-13
closure error / pair norm:               6.149764e-15
live model pair burden:                  0.000000
live selected-null deficit:              0.000000
```

The row count drops because the support-edge and reset endpoint residuals are no
longer split into radial/current/angular rows. Each endpoint point now has one
coupled junction row.

Junction sector summary:

| assignment | points | pair L1 | selected-null deficit | current | angular |
| --- | ---: | ---: | ---: | ---: | ---: |
| `support_edge_endpoint_junction` | `5222` | `0.337507` | `0.443187` | `0.066263` | `1.499727` |
| `reset_decompression_endpoint_junction` | `4269` | `0.314444` | `0.567268` | `0.315088` | `2.462061` |
| total junction layer | `9491` | `0.651951` | `1.010455` | `0.381351` | `3.961788` |

All junction rows are non-live:

```text
J_endpoint_junction_layer live rows:                 0
J_endpoint_junction_layer live pair burden:          0.000000
J_endpoint_junction_layer live selected-null burden: 0.000000
```

This is the sharpest statement of the current endpoint issue. The endpoint is
not contaminating the live corridor in this ledger, but it is carrying the
non-live radial-null deficit, angular endpoint support, and most of the current
relaxation in one place.

## Junction SNEC Check

A sampled junction-sector SNEC run was performed as a consistency check:

```text
windows scanned:                         12738
center stride:                           16
tau:                                     2.0, 3.0, 4.0
raw benchmark-floor violations:          0
scoreable benchmark-floor violations:    0
```

Worst sampled junction margins:

| tau | branch | worst total | floor | margin | dominant sector |
| ---: | --- | ---: | ---: | ---: | --- |
| `2.0` | minus | `-0.000871` | `-0.062500` | `0.061629` | `J_endpoint_junction_layer` |
| `2.0` | plus | `-0.001009` | `-0.062500` | `0.061491` | `J_endpoint_junction_layer` |
| `3.0` | minus | `-0.000473` | `-0.027778` | `0.027305` | `J_endpoint_junction_layer` |
| `3.0` | plus | `-0.000594` | `-0.027778` | `0.027184` | `J_endpoint_junction_layer` |
| `4.0` | minus | `-0.000273` | `-0.015625` | `0.015352` | `J_endpoint_junction_layer` |
| `4.0` | plus | `-0.000251` | `-0.015625` | `0.015374` | `J_endpoint_junction_layer` |

The total smeared result is expected to stay clean because the pointwise
intermediate sector sum is unchanged. The value of this run is attribution: the
dominant negative sector is now correctly named as the endpoint/junction layer,
not scattered across S1, S2, G, and D/H.

## Comparison To Stage I Concerns

Stage I left a clear warning: several knobs reduced one channel only by moving
burden into live `p_l`, live `j_l`, or live `pOmega`, especially in the
`catch_rematch / packet_in_support` sleeve. The newer full-grid and intermediate
results strengthen the architecture against that specific failure mode:

```text
full-grid live abs_p_l fraction:     0.787%
full-grid live abs_pOmega fraction: 14.706%
full-grid live abs_j_l fraction:    11.976%
positive live packet-norm samples:  0
intermediate model live burden:      0
```

The old high-`p_l` worry does not reappear here as a live-packet pass/fail
problem. The broad SNEC gate also remains clean.

But this does not settle physical admissibility. It moves the hard question. The
architecture now looks like:

```text
protected live packet corridor
  plus
constant-flux radial support scaffold
  plus
localized non-live endpoint/junction layer
```

The endpoint/junction layer is the candidate "somewhere" where the exotic or
trans-Planckian cost might have been localized.

## Current Interpretation

The design has not failed the Stage I/II architecture gates:

```text
live packet corridor: still protected
radial scaffold: compatible with constant-flux string-cloud accounting
broad smeared-null behavior: still clean
endpoint burden: non-live and localized
```

The design also has not passed the physical-source gate:

```text
endpoint conservation: not shown
finite-width junction source: not shown
semiclassical source acceptability: not shown
quantum inequality / ANEC-style endpoint cost: not shown
curvature or trans-Planckian scale control: not shown
```

This distinction matters. The current result should not be summarized as "the
endpoint is solved." It should be summarized as "the endpoint has become the
main physical-admissibility test."

## Decision

Use the coupled endpoint-junction source grammar for the next source-family
analysis:

```text
S0: constant-flux radial string-cloud backbone
J: endpoint/junction layer carrying radial trim, angular capacity, and current relaxation
R: small core-body residual leakage
```

Do not treat this as a matter model. Treat it as a sharper target for physical
replacement.

## Next Work

The next work should test whether `J_endpoint_junction_layer` can be made less
like a hidden throat shell:

```text
1. Endpoint scale/thickness ladder:
   Does widening or distributing J reduce peak/null cost without leaking into the live packet?

2. Conservation diagnostic:
   Does the coupled endpoint stress admit a plausible divergence-balanced source family?

3. Curvature/stress concentration check:
   Is the endpoint load finite and controllable, or does it sharpen as resolution/domain improves?

4. SNEC/ANEC/QI-oriented endpoint accumulation:
   The broad radial SNEC gate is clean, but endpoint-local accumulation needs its own adversarial screen.

5. Source-family ansatz:
   Try a finite-width junction/cap family first; reject any model that works only by hiding singular or trans-Planckian support in J.
```

Promotion criterion:

```text
J can be represented by a finite-width, non-live, conserved or nearly conserved
source-family target without degrading live packet safety or broad SNEC margins.
```

Failure criterion:

```text
J requires singular support, resolution-growing stress, live leakage, or an
unbounded endpoint accumulation even though the corridor gates remain clean.
```
