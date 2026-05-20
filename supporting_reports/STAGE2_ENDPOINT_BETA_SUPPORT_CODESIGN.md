# Stage II Endpoint Beta/Support Co-Design Screen

## Summary

The beta/support co-design screen confirms that release beta width is a real
endpoint-relief lever, but it does not confirm that the current Stage I
smooth-split support-edge controls are the missing receiver mechanism.

All ten `61 x 83` cases remained live-clean. Increasing
`release_beta_width_multiplier` from `0.25` to `0.75` reproduced the prior
reset-cap relief, and increasing it to `1.00` produced still stronger reset
relief with no positive live packet-norm samples. The cost remains a structured
transfer into the support-edge shoulder.

At fixed `release_beta_width_multiplier = 0.75`, however, the tested
support-edge companions were nearly invariant:

```text
edge width 7.2 -> 9.0 or 11.0
edge carve 0.16 -> 0.12 with edge width 9.0
angular_log_gain 0.00 -> 0.05 or 0.10
edge width 9.0 plus angular_log_gain 0.05
guard blend 0.25 with edge width 9.0
```

These controls changed the coupled endpoint J burden only in the fourth or
fifth decimal and left the reset cap unchanged to practical precision. The
result is therefore not "Stage I edge width needed to be paired with beta." It
is sharper:

```text
beta release is the reset-transfer valve;
the tested smooth-split edge/angle controls are not the receiver;
the next source model needs an explicit support-edge receiver component.
```

All results below are demanded-source and intermediate-source diagnostics. They
are not a continuum conservation proof, quantum RSET calculation, matter-model
solve, or no-go theorem.

## Inputs

Previous reset/release report:

```text
supporting_reports/STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md
```

Co-design screen spec:

```text
toolkit/adm_harness_cli/specs/endpoint_beta_support_codesign_smoke.json
```

Run outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_support_codesign_smoke_61x83/ledgers/
toolkit/adm_harness_cli/runs/endpoint_beta_support_codesign_smoke_61x83/component_all/
toolkit/adm_harness_cli/runs/endpoint_beta_support_codesign_smoke_61x83/string_all/
toolkit/adm_harness_cli/runs/endpoint_beta_support_codesign_smoke_61x83/intermediate_all/
toolkit/adm_harness_cli/runs/endpoint_beta_support_codesign_smoke_61x83/coupling_diagnostic/
```

Tooling update:

```text
toolkit/adm_harness_cli/scripts/run_endpoint_coupling_diagnostic.py
```

The endpoint coupling diagnostic now records:

```text
angular_log_gain
support_radius_Rth
support_width_wth
angular_radius_ROmega
angular_width_wOmega
angular_amplitude_aOmega
```

and names angular/edge-angular control changes in the contrast table.

## Cases

Baseline settings:

```text
live_packet_start = -1.40
entry_carve = 0.75
catch_carve = 0.15
edge_carve = 0.16
entry_width_multiplier = 4.8
catch_width_multiplier = 3.4
edge_width_multiplier = 7.2
temporal_profile = tanh
radial_profile = compact_smoothstep7
composition = additive
null_gain = -0.07

release_choreography_mode = matched_hold
release_matched_hold_widths = 0.25
release_beta_profile = minimum_jerk
release_beta_width_multiplier = 0.25
release_lapse_lag_widths = 0.0
release_carve_lag_widths = 0.0
```

Ledger safety:

| label | elapsed s | positive live packet-norm samples |
| --- | ---: | ---: |
| `codesign_base_beta025` | `337.181` | `0` |
| `codesign_beta075` | `337.195` | `0` |
| `codesign_beta100` | `340.361` | `0` |
| `codesign_beta075_edge_wide9` | `343.741` | `0` |
| `codesign_beta075_edge_wide11` | `341.937` | `0` |
| `codesign_beta075_edge_soft_wide9` | `343.966` | `0` |
| `codesign_beta075_ang_p005` | `380.140` | `0` |
| `codesign_beta075_ang_p010` | `366.138` | `0` |
| `codesign_beta075_edge_wide9_ang_p005` | `376.896` | `0` |
| `codesign_beta075_guard_blend025_wide9` | `492.496` | `0` |

## Beta Monotonic Result

The pure beta axis remains monotonic and live-clean:

| label | beta width | J selected | reset selected | reset abs current | support-edge selected | support-edge abs current | support-edge abs pOmega |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `codesign_base_beta025` | `0.25` | `0.986686` | `0.582542` | `0.318861` | `0.404144` | `0.060721` | `1.506623` |
| `codesign_beta075` | `0.75` | `0.964417` | `0.442605` | `0.240184` | `0.521812` | `0.105033` | `1.912497` |
| `codesign_beta100` | `1.00` | `0.944764` | `0.371175` | `0.177826` | `0.573589` | `0.133567` | `2.093173` |

Relative to baseline:

| label | J selected delta | reset selected delta | reset current delta | support-edge selected delta | support-edge current delta | support-edge pOmega delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `codesign_beta075` | `-2.26%` | `-24.02%` | `-24.67%` | `+29.12%` | `+72.98%` | `+26.94%` |
| `codesign_beta100` | `-4.25%` | `-36.28%` | `-44.23%` | `+41.93%` | `+119.97%` | `+38.93%` |

The concentration read also moves in the expected direction:

| label | reset effective volume fraction | reset rows for 50% burden | reset rows for 80% burden |
| --- | ---: | ---: | ---: |
| `codesign_base_beta025` | `0.285776` | `0.235023` | `0.460829` |
| `codesign_beta075` | `0.587938` | `0.278027` | `0.531390` |
| `codesign_beta100` | `0.780140` | `0.315789` | `0.593567` |

The reset cap is not merely smaller. It is less concentrated under beta
broadening.

## Transfer Accounting

The beta axis is not a free win. Most of the reset relief reappears as
support-edge load:

| label | reset relief | support-edge transfer | transfer / reset relief | net J relief | net J relief / reset relief |
| --- | ---: | ---: | ---: | ---: | ---: |
| `codesign_beta075` | `0.139937` | `0.117668` | `0.840866` | `0.022269` | `0.159134` |
| `codesign_beta100` | `0.211367` | `0.169445` | `0.801663` | `0.041922` | `0.198337` |

This is the strongest conservation-like signal in the screen. Roughly
`80-84%` of the reset relief is paid into the support-edge shoulder, while
`16-20%` becomes net J-layer relief.

That ratio should not be over-interpreted as a conservation law. It is a
coarse-grid effective-coupling diagnostic. But it is specific enough to guide
the next model: the receiver needs to be a load-bearing endpoint component, not
another passive widening of the existing smooth-split support edge.

## Fixed-Beta Co-Design Result

At fixed `release_beta_width_multiplier = 0.75`, the tested support-edge and
angular companions did not materially change the endpoint split:

| label | change | J selected | delta vs `beta075` | reset selected | support-edge selected | support-edge pOmega |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `codesign_beta075` | beta `0.75` | `0.964417` | `0.000000` | `0.442605` | `0.521812` | `1.912497` |
| `codesign_beta075_edge_wide9` | edge width `7.2 -> 9.0` | `0.964409` | `-0.000008` | `0.442605` | `0.521804` | `1.912089` |
| `codesign_beta075_edge_wide11` | edge width `7.2 -> 11.0` | `0.964404` | `-0.000013` | `0.442605` | `0.521799` | `1.912161` |
| `codesign_beta075_edge_soft_wide9` | edge carve `0.16 -> 0.12` | `0.964446` | `+0.000028` | `0.442605` | `0.521840` | `1.912556` |
| `codesign_beta075_ang_p005` | angular gain `0.05` | `0.964435` | `+0.000017` | `0.442605` | `0.521829` | `1.912597` |
| `codesign_beta075_ang_p010` | angular gain `0.10` | `0.964531` | `+0.000114` | `0.442605` | `0.521926` | `1.912697` |
| `codesign_beta075_edge_wide9_ang_p005` | edge width `9.0` plus angular gain `0.05` | `0.964382` | `-0.000035` | `0.442605` | `0.521776` | `1.912175` |
| `codesign_beta075_guard_blend025_wide9` | guard blend `0.25`, edge width `9.0` | `0.964475` | `+0.000058` | `0.442605` | `0.521870` | `1.912921` |

The support-edge controls are live-safe, but in this source grammar they are
not the receiver. They do not pull the transferred load out of support-edge, do
not further unload the reset cap, and do not improve J total by more than
grid-scale noise.

## Diagnostic Contrast

The endpoint coupling contrast classifies every beta-broadened case as
`possible_endpoint_relief`, but that classification is caused by beta width,
not by the companion knobs:

| label | diagnostic read | live defects | J selected | J delta fraction vs base |
| --- | --- | ---: | ---: | ---: |
| `codesign_base_beta025` | `endpoint_invariant_no_relief` | `0` | `0.986686` | `0.000000` |
| `codesign_beta075` | `possible_endpoint_relief` | `0` | `0.964417` | `-0.022569` |
| `codesign_beta100` | `possible_endpoint_relief` | `0` | `0.944764` | `-0.042488` |
| `codesign_beta075_edge_wide9` | `possible_endpoint_relief` | `0` | `0.964409` | `-0.022577` |
| `codesign_beta075_edge_wide11` | `possible_endpoint_relief` | `0` | `0.964404` | `-0.022583` |
| `codesign_beta075_edge_soft_wide9` | `possible_endpoint_relief` | `0` | `0.964446` | `-0.022540` |
| `codesign_beta075_ang_p005` | `possible_endpoint_relief` | `0` | `0.964435` | `-0.022551` |
| `codesign_beta075_ang_p010` | `possible_endpoint_relief` | `0` | `0.964531` | `-0.022454` |
| `codesign_beta075_edge_wide9_ang_p005` | `possible_endpoint_relief` | `0` | `0.964382` | `-0.022605` |
| `codesign_beta075_guard_blend025_wide9` | `possible_endpoint_relief` | `0` | `0.964475` | `-0.022510` |

## Source-Model Interpretation

This screen strengthens the endpoint-plant narrative but revises the next
mechanical target.

The reset/release ladder already showed:

```text
J1 reset terminator is beta-release sensitive.
```

The co-design screen adds:

```text
J0 support-edge shoulder receives most of the relieved reset load.
Existing smooth-split edge width/softening does not act as an active receiver.
Local angular log gain on the same smooth-split edge window does not absorb it.
Guard blending on that edge window does not absorb it.
```

So the missing model is more specific than "support-edge retuning." It should
be an explicit support-edge receiver layer with its own stress role:

```text
non-live endpoint shoulder receiver
localized to support_edge / catch-rematch / post-release interface
coupled to beta release width or beta-release flux
allowed to carry radial-pair trim, angular capacity, and current relaxation
with live packet exclusion preserved as a hard constraint
```

That points toward an anchored endpoint cap or tension-lattice shoulder, not
another smooth geometric smear.

## Next Step

The next source model should introduce a receiver diagnostic before another
large scan:

```text
1. Define a beta-release flux or release-gradient proxy:
   how much reset obligation is being moved out of J1.

2. Define a support-edge receiver amplitude:
   a localized non-live support-edge endpoint layer whose amplitude is tied to
   that release proxy rather than to plain edge width.

3. Split receiver roles:
   radial-pair shoulder trim,
   support-edge angular capacity,
   support-edge current relaxation.

4. Test whether receiver activation reduces the support-edge transfer while
   preserving beta relief:
   reset selected remains <= 0.45,
   support-edge selected drops below the beta075 value 0.521812,
   J total remains <= 0.964417,
   positive live packet-norm samples remain 0.
```

`release_beta_width_multiplier = 1.00` is live-clean and worth retaining as a
stress point, but it should not be promoted alone. It increases support-edge
load too much to count as a complete endpoint solution.

Before report-grade physical claims, this screen still needs denser-grid
confirmation and an endpoint-local SNEC companion. The smoke-grid conclusion is
nevertheless clear enough for model selection: the next branch should be an
explicit support-edge receiver model coupled to beta-release transfer.
