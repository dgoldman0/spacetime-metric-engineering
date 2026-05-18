# Stage I Release-Choreography Refreeze

## Purpose

This report refreezes the release-choreography direction with the intended target hierarchy restored:

```text
V5 is the primary engineering target.
V2 is a diagnostic microscope for mechanism and margin.
V10 remains an edge target, but not the current optimization driver.
```

The previous mature-release probe showed that a short finite beta release plus shaped beta floor could restore V5 packet safety at smoke resolution, but report-grid checks still found point-peak and live hard-point problems. This pass refined the law around two hypotheses:

```text
1. The beta floor must remain active through the live packet corridor; moving it later causes V5 packet-norm failure.
2. The floor/sleeve join is a derivative-sensitive place, so the harness should expose derivative diagnostics and test smoother floor unions.
```

## Harness Refinements

The harness now records derivative diagnostics in point ledgers:

```text
release_profile_slope_abs
standing_support_packet_carve_window_slope_abs
standing_support_packet_lapse_window_slope_abs
standing_support_packet_beta_rematch_window_slope_abs
```

The shaped beta rematch floor gained an explicit union mode:

```text
standing_support_packet_beta_rematch_floor_mode = max | blend | add
```

Meanings:

```text
max    old hard union, max(shaped_sleeve, center_floor)
blend  smooth union, shaped_sleeve + center_floor * (1 - shaped_sleeve)
add    clipped additive union
```

The `blend` option was intended to remove a potential derivative kink at the floor/sleeve join while preserving center causal margin.

## Runs

Main runs:

```text
toolkit/adm_harness_cli/runs/stage1_v5_mature_release_beta_timing_ladder/
toolkit/adm_harness_cli/runs/stage1_v5_mature_release_floor_mode_ladder/
toolkit/adm_harness_cli/runs/stage1_v5_mature_release_trailing_selected_check/
toolkit/adm_harness_cli/runs/stage1_v2_mature_release_trailing_selected_check/
toolkit/adm_harness_cli/runs/stage1_v10_mature_release_trailing_edge_smoke/
toolkit/adm_harness_cli/runs/stage1_v5_mature_release_trailing_selected_ledger/
```

Selected refreeze branch:

```text
service shell amplitude = 0.5
catch lead = 1.55
temporal width = 0.30
clock lapse ratio = 0.375

release_choreography_mode = matched_hold
release_matched_hold_widths = 0.25
release_beta_profile = minimum_jerk
release_beta_width_multiplier = 0.25

standing_support_packet_exclusion = 0.90
standing_support_packet_exclusion_width_multiplier = 1.4
standing_support_packet_exclusion_schedule = live_only
standing_support_packet_exclusion_shoulder = 0.18
standing_support_packet_exclusion_shoulder_mode = annular
standing_support_packet_exclusion_shoulder_radius_multiplier = 1.5
standing_support_packet_exclusion_shoulder_width_multiplier = 2.0
standing_support_packet_exclusion_shoulder_schedule = live_only

standing_support_packet_lapse_log_gain = 1.0
standing_support_packet_lapse_radius_multiplier = 1.7
standing_support_packet_lapse_width_multiplier = 2.0
standing_support_packet_lapse_schedule = entry_catch_release

standing_support_packet_beta_rematch_shape = trailing_edge
standing_support_packet_beta_rematch_gain = 1.8
standing_support_packet_beta_rematch_inner_radius_multiplier = 0.75
standing_support_packet_beta_rematch_outer_radius_multiplier = 1.10
standing_support_packet_beta_rematch_center_floor = 0.60
standing_support_packet_beta_rematch_floor_mode = max
standing_support_packet_beta_rematch_schedule = live_only
```

## Timing-Ladder Result

Moving beta rematch from `live_only` to `catch_release` or `coordinated_release` was not viable at V5. It removed the pre-catch support the packet still needs:

| beta schedule | safe rows | min packet failures | best live Tkk fraction | min max point peak ratio |
|---|---:|---:|---:|---:|
| `catch_release` | 0 | 35 | 0.014882 | 8.498 |
| `coordinated_release` | 0 | 35 | 0.015675 | 11.315 |

This is an important correction to the conceptual model. The beta floor is not merely a release cleanup term. At V5 it is also preserving live packet causal margin before catch/rematch.

## Floor-Mode Result

The smoother `blend` floor union did not refreeze cleanly. It reduced some raw peak rows, but introduced live hard-channel exposure:

| branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---|---:|---:|---:|---:|---:|
| annular, gain 1.2, floor 0.60, `blend` | 0 | 2 | 0.025911 | 0.006022 | 9.651 |
| annular, gain 1.5, floor 0.60, `max` | 0 | 0 | 0.030301 | 0.006371 | 11.619 |

So the old hard union remains the better V5 safety choice for now. The price is that the derivative/point-peak problem is not solved by floor smoothing alone.

## Selected V5 Refreeze

The selected trailing-edge V5 report-grid check:

| V | packet failures | top hard live points | max packet norm | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0 | 0 | -5.236716 | 0.028567 | 0.006986 | 2.228077 | 43.889793 |

Compared with the previous annular cap-safe report-grid branch:

| V | branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|
| 5 | annular cap-safe | 0 | 1 | 0.032248 | 0.006421 | 43.520 |
| 5 | trailing-edge refreeze | 0 | 0 | 0.028567 | 0.006986 | 43.890 |

Compared with shaped-sleeve-only V5:

| V | branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|
| 5 | shaped sleeve only | 47 | 1 | 0.020311 | 0.005569 | 22.875 |
| 5 | trailing-edge refreeze | 0 | 0 | 0.028567 | 0.006986 | 43.890 |

The refreeze is therefore a V5 packet-safety improvement, not a source-cleanliness victory.

## V2 Diagnostic Check

The same selected branch at V2:

| V | packet failures | top hard live points | max packet norm | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 0 | 0 | -5.559247 | 0.013895 | 0.005367 | 1.897165 | 13.002831 |

V2 remains useful as a diagnostic: the branch is cleanly packet-safe there and does not show the V5 point-peak explosion. But V2 is not the target; it only tells us the mechanism is not nonsense.

## V10 Edge Check

A cheap V10 smoke check of the selected branch fails:

| V | packet failures | top hard live points | max packet norm | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 3 | 3 | 276.340802 | 0.058684 | 0.015423 | 4.037603 | 98.357128 |

This should not be overinterpreted as a final V10 impossibility. It says the current refrozen V5 law is not V10-ready, and V10 should remain an edge target for a later service-aware law.

## Point-Ledger Diagnostics

The focused V5 point ledger for the selected branch shows the top bad points are not live-packet points:

```text
top radial-null points: core_throat / support_edge
top stages: catch_rematch and entry_precatch
inside_packet_live: false for the top listed points
```

Maximum derivative diagnostic locations:

| diagnostic | max value | stage | region | live packet |
|---|---:|---|---|---|
| `release_profile_slope_abs` | 10.054 | release_shift_fade | outer_quarantine_shell | false |
| `standing_support_packet_carve_window_slope_abs` | 6.034 | catch_rematch | core_throat | false |
| `standing_support_packet_lapse_window_slope_abs` | 5.558 | catch_rematch | core_throat | false |
| `standing_support_packet_beta_rematch_window_slope_abs` | 8.140 | catch_rematch | core_throat | false |

This supports the current interpretation:

```text
The packet corridor can be protected at V5.
The support plant is still paying through sharp infrastructure-side derivative structure.
```

## Implications

The V5 target has not been abandoned. This refreeze gives a V5 packet-safe release choreography with no top hard-channel points in the live packet. That is meaningful progress over the shaped-sleeve-only V5 cap.

But the branch is not a final Stage I source target because:

```text
V5 max point peak is still too high.
V5 live Tkk is worse than the shaped-sleeve-only cap, though packet safety is fixed.
V10 fails even at smoke resolution.
The worst derivative and source peaks remain in support infrastructure near catch/rematch.
```

Recommended next move:

```text
Keep this branch as the V5 release-choreography refreeze.
Stop trying to improve V5 by moving beta rematch later; that breaks packet safety.
Target infrastructure derivative smoothing around catch/rematch and core/support-edge transitions.
Use V2 only for mechanism checks.
Use V10 only as an edge check after the V5 infrastructure peak is controlled.
```

Stage II should remain paused. The demanded-source target is better structured, but not yet clean enough for matter-source selection.
