# Stage I Mature Release-Choreography Probe

## Purpose

The release-choreography boundary memo concluded that simple window timing plus local amplitude sleeves had likely reached its limit. This probe added a first explicit mature release law:

```text
hold the packet matched briefly
fade beta with a finite smooth profile
allow lapse/carve schedules to relax on the coordinated release clock
test whether this reduces packet-edge derivative cost without relying only on stronger beta correction
```

This is still a demanded-source harness probe, not a selected matter-source model.

## Harness Change

New release controls:

```text
release_choreography_mode = legacy | matched_hold
release_matched_hold_widths
release_beta_profile = tanh | minimum_jerk | smoothstep5 | smoothstep7
release_beta_width_multiplier
release_lapse_lag_widths
release_carve_lag_widths
```

`legacy` preserves the previous beta release. `matched_hold` delays the start of beta fade by `release_matched_hold_widths * w_beta`, then fades over:

```text
4 * w_beta * release_beta_width_multiplier
```

The finite smooth profiles give explicit endpoint control. `minimum_jerk` / `smoothstep5` and `smoothstep7` have vanishing endpoint derivatives, which is the key distinction from just increasing beta-rematch gain.

Packet-local schedules also gained:

```text
coordinated_release
```

That schedule is available for carve, shoulder, lapse, and beta-rematch windows. In practice, the first smoke showed that using a catch-onset coordinated window for carve/lapse can uncover large live pre-catch burden because the current live-packet mask includes the pre-catch packet corridor. The useful selected checks therefore kept carve/shoulder active on `live_only`, used `entry_catch_release` lapse, and applied the mature law to the beta release envelope itself.

## Runs

Smoke and selected checks:

```text
toolkit/adm_harness_cli/runs/stage1_v2_mature_release_smoke/
toolkit/adm_harness_cli/runs/stage1_v2_mature_release_smoke2/
toolkit/adm_harness_cli/runs/stage1_v2_mature_beta_release_only_smoke/
toolkit/adm_harness_cli/runs/stage1_v2_mature_short_release_smoke/
toolkit/adm_harness_cli/runs/stage1_v2_mature_short_release_beta_floor_smoke/
toolkit/adm_harness_cli/runs/stage1_v5_mature_short_release_beta_floor_cap_smoke/
toolkit/adm_harness_cli/runs/stage1_v5_mature_short_release_cap_margin_ladder/
toolkit/adm_harness_cli/runs/stage1_v2_mature_short_release_cap_safe_check/
toolkit/adm_harness_cli/runs/stage1_v2_mature_release_selected_check/
toolkit/adm_harness_cli/runs/stage1_v5_mature_release_selected_cap_check/
toolkit/adm_harness_cli/runs/stage1_v2_mature_release_lowgain_selected_check/
```

The main family used the aggressive near-pass geometry:

```text
standing_support_packet_exclusion = 0.90
standing_support_packet_exclusion_width_multiplier = 1.4
standing_support_packet_exclusion_shoulder = 0.18
standing_support_packet_exclusion_shoulder_mode = annular
standing_support_packet_exclusion_shoulder_radius_multiplier = 1.5
standing_support_packet_exclusion_shoulder_width_multiplier = 2.0
standing_support_packet_lapse_log_gain = 1.0
standing_support_packet_lapse_radius_multiplier = 1.7
standing_support_packet_lapse_width_multiplier = 2.0
release_choreography_mode = matched_hold
release_matched_hold_widths = 0.25
release_beta_profile = minimum_jerk
release_beta_width_multiplier = 0.25
```

## Low-Resolution Signal

The first useful low-resolution result came from short finite beta release plus a shaped beta floor:

| V | beta shape | beta gain | center floor | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | trailing_edge | 1.2 | 0.45 | 0 | 0 | 0.012047 | 0.005056 | 14.153 |
| 2 | annular | 1.2 | 0.45 | 0 | 0 | 0.010821 | 0.005050 | 14.153 |

This was promising relative to the previous shaped-sleeve-only report-grid check:

| V | branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|
| 2 | shaped sleeve only | 0 | 0 | 0.012323 | 0.005264 | 25.075 |
| 2 | mature release smoke, trailing edge | 0 | 0 | 0.012047 | 0.005056 | 14.153 |

The V5 low-resolution cap required more margin:

| V | beta shape | beta gain | center floor | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5 | annular | 1.5 | 0.60 | 0 | 0 | 0.029933 | 0.006267 | 11.619 |

So at smoke resolution, the mature choreography looked like a real improvement in packet safety and point-peak control, though V5 radial-null cleanliness was not good.

## Report-Grid Check

Report-grid checks were less favorable.

Lower-gain V2 report-grid check:

| V | beta shape | beta gain | center floor | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | trailing_edge | 1.2 | 0.45 | 0 | 0 | 0.013807 | 0.005175 | 25.137 |
| 2 | annular | 1.2 | 0.45 | 0 | 0 | 0.012898 | 0.005195 | 25.075 |

At report grid this lower-gain branch no longer improved point peaks; it mostly returned to the shaped-sleeve-only behavior.

Cap-safe report-grid selected check:

| V | beta shape | beta gain | center floor | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | annular | 1.5 | 0.60 | 0 | 1 | 0.013896 | 0.005353 | 18.574 |
| 5 | annular | 1.5 | 0.60 | 0 | 1 | 0.032248 | 0.006421 | 43.520 |

This branch is packet-safe at V5, which is progress over the previous shaped-sleeve V5 cap failure:

| V | branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|
| 5 | shaped sleeve only | 47 | 1 | 0.020311 | 0.005569 | 22.875 |
| 5 | mature release cap-safe | 0 | 1 | 0.032248 | 0.006421 | 43.520 |

But this is not a selected architecture: V5 survives by spending radial-null cleanliness and point-peak margin.

## Interpretation

The mature release law is useful, but this first implementation does not solve the strict gate.

Current readout:

```text
Short finite beta release can lower the smoke-grid peak cost.
Without rematch margin it opens packet-norm failures.
With a shaped beta floor it restores V2 safety and can restore V5 packet safety.
At report grid, the V2 peak improvement mostly disappears for the lower-gain branch.
The V5-safe branch has no packet failures, but it has a top hard live point, worse Tkk, and a large point peak.
```

This means the conceptual direction is still alive, but the first control law is too crude. It coordinates the beta release clock, but it does not yet regularize the actual packet-edge derivative stack finely enough.

The important practical lesson is:

```text
Mature release choreography can trade packet-norm safety back into the V5 cap.
It has not yet reduced the strict radial-null floor and point peaks together at report resolution.
```

## Next Steps

Do not select this branch as the Stage I architecture.

Next refinements should be more derivative-aware:

```text
1. Add explicit release-derivative diagnostics for beta, packet rematch window, lapse window, and carve window.
2. Shape the beta-rematch floor by derivative demand instead of a fixed center floor.
3. Test a phase-aware live mask or report slice that distinguishes pre-catch live packet exposure from release handoff exposure.
4. Add a smoother coordinated-release onset for carve/lapse that does not uncover the pre-catch packet corridor.
5. Retest the V2/V5 cap only after the high-resolution point peak is controlled below the shaped-sleeve baseline.
```

Stage II should remain paused. The mature choreography probe produced a useful harness direction and a V5-safe diagnostic branch, but not a clean demanded-source target.
