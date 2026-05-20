# Stage II Endpoint Reset/Release Ladder

## Summary

The reset/release ladder found the first materially useful endpoint refinement
axis after the endpoint-thickness closeout. Simple endpoint width, catch width,
edge softening, current guard blending, and temporal broadening did not relieve
the coupled endpoint layer. In contrast, widening the release beta fade directly
reduced the stubborn reset/decompression cap while keeping the live packet gate
clean.

This is not yet a complete source model. The reset relief is paid for by moving
burden into the support-edge shoulder. But it is a real mechanical signal:

```text
release beta width is load-bearing for endpoint source closure
reset-current burden is not invariant under true release choreography
support-edge shoulder capacity must be co-designed with the release law
```

## Inputs

Prior closeout:

```text
supporting_reports/STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md
```

Reset/release ladder spec:

```text
toolkit/adm_harness_cli/specs/endpoint_reset_release_ladder_smoke.json
```

Run outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_reset_release_ladder_smoke_61x83/ledgers/
toolkit/adm_harness_cli/runs/endpoint_reset_release_ladder_smoke_61x83/component_all/
toolkit/adm_harness_cli/runs/endpoint_reset_release_ladder_smoke_61x83/string_all/
toolkit/adm_harness_cli/runs/endpoint_reset_release_ladder_smoke_61x83/intermediate_all/
toolkit/adm_harness_cli/runs/endpoint_reset_release_ladder_smoke_61x83/coupling_diagnostic/
```

Tooling updates:

```text
toolkit/adm_harness_cli/scripts/run_smooth_split_screen.py
toolkit/adm_harness_cli/scripts/run_endpoint_coupling_diagnostic.py
```

The smooth-split replay path now exposes the release-choreography controls:

```text
release_choreography_mode
release_matched_hold_widths
release_beta_profile
release_beta_width_multiplier
release_lapse_lag_widths
release_carve_lag_widths
```

The endpoint coupling diagnostic now records these release controls in its
summary and contrast tables.

All results below are demanded-source and intermediate-source diagnostics. They
are not a continuum conservation proof, quantum RSET calculation, matter-model
solve, or no-go theorem.

## Ladder Cases

The baseline matches the current endpoint source-model settings on a coarser
`61 x 83` smoke grid:

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

The tested variants:

| label | change |
| --- | --- |
| `reset_release_base` | baseline |
| `reset_release_hold_short010` | matched hold `0.25 -> 0.10` |
| `reset_release_hold_wide050` | matched hold `0.25 -> 0.50` |
| `reset_release_beta_wide050` | beta release width `0.25 -> 0.50` |
| `reset_release_beta_wide075` | beta release width `0.25 -> 0.75` |
| `reset_release_lapse_lag025` | lapse lag `0.00 -> 0.25` |
| `reset_release_carve_lag025` | carve lag `0.00 -> 0.25` |
| `reset_release_lag_pair025` | lapse and carve lag `0.00 -> 0.25` |

All eight cases remained live-clean:

| label | elapsed s | positive live packet-norm samples |
| --- | ---: | ---: |
| `reset_release_base` | `328.479` | `0` |
| `reset_release_hold_short010` | `329.309` | `0` |
| `reset_release_hold_wide050` | `331.598` | `0` |
| `reset_release_beta_wide050` | `333.412` | `0` |
| `reset_release_beta_wide075` | `334.505` | `0` |
| `reset_release_lapse_lag025` | `322.011` | `0` |
| `reset_release_carve_lag025` | `324.317` | `0` |
| `reset_release_lag_pair025` | `322.793` | `0` |

## Baseline Endpoint Split

On this `61 x 83` smoke grid, the baseline endpoint split is:

| scope | selected-null deficit | current-selected deficit | abs current | abs pOmega |
| --- | ---: | ---: | ---: | ---: |
| `J_total` | `0.986686` | `0.583173` | `0.379582` | `4.029659` |
| `reset_cap` | `0.582542` | `0.466001` | `0.318861` | `2.523036` |
| `support_edge` | `0.404144` | `0.117172` | `0.060721` | `1.506623` |

This is consistent with the prior dense and `81 x 121` reads: the reset cap is
the larger and more current-selected part of the coupled endpoint layer.

## Main Result

The beta release width ladder is monotonic and live-clean:

| label | beta width | J selected deficit | reset selected deficit | reset current | support-edge selected deficit |
| --- | ---: | ---: | ---: | ---: | ---: |
| `reset_release_base` | `0.25` | `0.986686` | `0.582542` | `0.318861` | `0.404144` |
| `reset_release_beta_wide050` | `0.50` | `0.977887` | `0.511289` | `0.286200` | `0.466597` |
| `reset_release_beta_wide075` | `0.75` | `0.964417` | `0.442605` | `0.240184` | `0.521812` |

Relative to baseline, `reset_release_beta_wide075` gives:

```text
J total selected-null deficit:       -2.26%
reset selected-null deficit:        -24.02%
reset abs current:                  -24.68%
reset current-selected deficit:     -23.73%
support-edge selected-null deficit: +29.11%
positive live packet-norm samples:   0
```

This crosses the rough threshold for a model-worthy signal: reset selected-null
deficit falls below `0.45` without introducing a live packet-norm defect.

The cost is not small. Support-edge burden increases substantially. The result
therefore points to a coupled endpoint plant rather than a free release-law
solution: beta release can unload the reset terminator, but the support-edge
shoulder and angular jacket must absorb or reshape the transferred load.

## Secondary Results

Matched hold width is weaker but directionally consistent:

| label | hold width | J selected deficit | reset selected deficit | reset current | support-edge selected deficit |
| --- | ---: | ---: | ---: | ---: | ---: |
| `reset_release_hold_short010` | `0.10` | `0.986741` | `0.582835` | `0.319314` | `0.403906` |
| `reset_release_base` | `0.25` | `0.986686` | `0.582542` | `0.318861` | `0.404144` |
| `reset_release_hold_wide050` | `0.50` | `0.983927` | `0.559395` | `0.309580` | `0.424532` |

Shortening the hold is slightly worse. Widening the hold gives modest reset
relief, again with support-edge transfer.

The lag controls tested here were no-ops on the endpoint split:

```text
release_lapse_lag_widths = 0.25
release_carve_lag_widths = 0.25
both lapse and carve lag = 0.25
```

All three reproduce the baseline J split exactly at this precision. This says
the current relief is not coming from simply delaying lapse or carve response.
It is specifically tied to the beta release fade width.

## Coupling Diagnostic

Endpoint coupling contrast:

| label | change | live defects | J selected deficit | J delta vs base | diagnostic read |
| --- | --- | ---: | ---: | ---: | --- |
| `reset_release_base` | baseline | `0` | `0.986686` | `0` | `endpoint_invariant_no_relief` |
| `reset_release_hold_short010` | hold `0.25 -> 0.10` | `0` | `0.986741` | `0.000055` | `endpoint_invariant_no_relief` |
| `reset_release_hold_wide050` | hold `0.25 -> 0.50` | `0` | `0.983927` | `-0.002758` | `small_mixed_change` |
| `reset_release_beta_wide050` | beta width `0.25 -> 0.50` | `0` | `0.977887` | `-0.008799` | `small_mixed_change` |
| `reset_release_beta_wide075` | beta width `0.25 -> 0.75` | `0` | `0.964417` | `-0.022269` | `possible_endpoint_relief` |
| `reset_release_lapse_lag025` | lapse lag `0 -> 0.25` | `0` | `0.986686` | `0` | `endpoint_invariant_no_relief` |
| `reset_release_carve_lag025` | carve lag `0 -> 0.25` | `0` | `0.986686` | `0` | `endpoint_invariant_no_relief` |
| `reset_release_lag_pair025` | paired lag `0 -> 0.25` | `0` | `0.986686` | `0` | `endpoint_invariant_no_relief` |

`reset_release_beta_wide075` is the only case classified as
`possible_endpoint_relief`.

The reset cap also broadens in concentration as beta width increases:

| label | reset effective volume fraction | reset rows for 50% burden | reset rows for 80% burden |
| --- | ---: | ---: | ---: |
| `reset_release_base` | `0.285776` | `0.235023` | `0.460829` |
| `reset_release_beta_wide050` | `0.418775` | `0.253188` | `0.489982` |
| `reset_release_beta_wide075` | `0.587938` | `0.278027` | `0.531390` |

That is an important improvement over the previous endpoint-thickness ladder.
The reset burden is not merely smaller; it is more distributed within the reset
cap. The transfer into support-edge remains the main cost.

## Source-Model Interpretation

The result aligns with the locked design's architecture. Stage I already had a
protected live packet corridor coupled to a support plant. This ladder says the
release beta fade is part of the endpoint source machinery, not just a
background choreography detail.

Mechanically, the endpoint obligation now looks like:

```text
J0: support-edge shoulder / radial scaffold
J1: beta-release reset-current terminator
J2: angular jacket coupled to the shoulder and terminator
```

The missing source grammar is therefore not "add another generic shell." It is
an explicit beta-release/reset-current terminator coupled to support-edge
capacity. The release law can unload J1, but J0/J2 must be retuned so the load
does not simply accumulate at the shoulder.

## Next Step

The next round should be a targeted beta-release/support-edge co-design screen,
not a broad endpoint ladder:

```text
primary axis:
  release_beta_width_multiplier = 0.50, 0.75, maybe 1.00

companion axes:
  support-edge shoulder width/radius
  angular jacket gain or width
  current guard coupled to the widened beta release, not standalone
```

Win condition:

```text
reset selected-null deficit stays near or below 0.45
reset current remains reduced by about 20-30%
support-edge transfer is reduced from the beta_wide075 cost
positive live packet-norm samples remain 0
J total does not increase
```

Before report-grade conclusions, the beta-width result needs confirmation on a
denser grid and then an endpoint-local SNEC companion. But the smoke result is
strong enough to change the model-refinement direction.
