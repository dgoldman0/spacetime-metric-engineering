# Stage I Release-Choreography Boundary Memo

## Purpose

This memo records the shaped beta-sleeve probe and the design conclusion it forced.

The immediate question was whether the residual V2 radial-null floor and point peaks were caused by a blunt packet-local beta rematch. The tested refinement was a nonuniform packet-edge sleeve:

```text
weak or inactive in the packet center
strongest near 0.85-1.10 Rpass
biased toward the trailing / inner side
active mainly around catch/rematch through release
```

The deeper question was whether the current family of simple release choreography knobs can be pushed into a strict packet/source-separation pass.

## Harness Change

The source ledger now exposes shaped packet beta-rematch windows:

```text
standing_support_packet_beta_rematch_shape = core | shoulder | annular | edge_soften | trailing_edge
standing_support_packet_beta_rematch_inner_radius_multiplier
standing_support_packet_beta_rematch_outer_radius_multiplier
standing_support_packet_beta_rematch_edge_softness
standing_support_packet_beta_rematch_temporal_width_multiplier
standing_support_packet_beta_rematch_center_floor
```

It also adds a `catch_release` temporal schedule:

```text
active mainly from catch/rematch through release
skips most entry/precatch exposure
```

The focused ledger and overlay sweep CLIs expose singular/plural versions of these controls. Long sweep case slugs are now shortened with a hash suffix so broad shaped-window screens do not exceed filesystem filename limits.

The old `core` shape preserves the previous filled packet-local beta rematch. The new shaped windows test shoulder, annular, edge-softened, and trailing-edge sleeves.

## Runs

Exploratory and focused runs:

```text
toolkit/adm_harness_cli/runs/stage1_v2_trailing_edge_sanity/
toolkit/adm_harness_cli/runs/stage1_v2_trailing_edge_sanity_gain_ladder/
toolkit/adm_harness_cli/runs/stage1_v2_annular_edge_sleeve_sanity/
toolkit/adm_harness_cli/runs/stage1_v2_trailing_edge_live_timing_check/
toolkit/adm_harness_cli/runs/stage1_v2_shaped_sleeve_floor_ladder/
toolkit/adm_harness_cli/runs/stage1_v2_peakcontrolled_sleeve_floor_ladder/
toolkit/adm_harness_cli/runs/stage1_v2_shaped_sleeve_selected_check/
toolkit/adm_harness_cli/runs/stage1_v5_shaped_sleeve_selected_cap_check/
```

One early broad run hit the original filename-length limit and was not used as evidence:

```text
toolkit/adm_harness_cli/runs/stage1_v2_trailing_edge_rematch_screen/
```

## Main Results

Pure trailing-edge, annular, and edge-softened beta sleeves did not restore packet safety. They reduced or reshaped the residual in the expected packet-edge zone, but left packet-norm failures.

The best low-resolution shaped-sleeve cases required a weak filled center floor. The best aggressive near-pass low-resolution row was:

| shape | beta gain | inner radius | center floor | packet failures | live Tkk fraction | live p_l fraction | max point peak ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| annular | 1.20 | 0.75 | 0.45 | 0 | 0.014418 | 0.005416 | 10.459 |

The report-grid selected check improved V2 radial-null slightly compared with the previous aggressive near-pass branch, but with much worse point peaks:

| V | branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | prior aggressive near-pass | 0 | 0 | 0.012860 | 0.005288 | n/a | 11.849591 |
| 2 | shaped annular sleeve, floor 0.45 | 0 | 0 | 0.012323 | 0.005264 | 1.753689 | 25.075342 |

The same shaped branch failed the V5 cap:

| V | branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|---:|
| 5 | shaped annular sleeve, floor 0.45 | 47 | 1 | 0.020311 | 0.005569 | 1.918818 | 22.874898 |

The peak-controlled geometry kept point peaks under control, but did not improve the strict V2 target:

| branch | packet failures | live Tkk fraction | live p_l fraction | max point peak ratio |
|---|---:|---:|---:|---:|
| peak-controlled shaped sleeve best row | 0 | about 0.0275 | about 0.0265 | 4.66 |

## Interpretation

The shaped-sleeve probe supports the packet-edge diagnosis, but not the hoped-for simple fix.

Current readout:

```text
The residual radial-null floor and point peaks really do live near the packet edge / release handoff.
Pure beta sleeves are too local and too amplitude-like to solve the derivative handoff.
Adding a center floor restores packet safety, but turns the sleeve back toward the filled-window family and raises point peaks.
The V5 cap failure shows that the V2 near-pass improvement is not a robust release architecture.
```

This likely marks the end of the naive release-choreography family:

```text
simple window timing
local carve/lapse/beta amplitudes
filled or annular packet sleeves
gain ladders around the same release window
```

It does not mark the end of release choreography as an idea. The current results make quick optimism weaker, but they make the next design target clearer.

## Next Design Target

The next choreography should be built around smoothing the handoff derivatives, not around stronger beta correction.

A more mature release law should include:

```text
catch/rematch the packet
hold the matched state briefly while the trailing edge settles
fade beta with a minimum-jerk or higher-smoothness profile
keep lapse support until beta derivatives are small
relax carve/support only after the packet edge is no longer carrying the mismatch
make first and second derivatives vanish at packet-edge or phase boundaries where practical
```

In control-law terms, the release should become a coordinated phase program:

```text
catch/rematch phase
matched-hold phase
derivative-limited beta fade phase
lapse-supported beta-settling phase
carve/support relaxation phase
```

The next harness should therefore test choreography knobs such as:

```text
matched_hold_duration
beta_release_profile = smoothstep5 | minimum_jerk | smoothstep7
beta_release_width_multiplier
lapse_release_lag
carve_release_lag
coordinated_release_mode
```

The purpose is not to add more independent amplitude knobs. The purpose is to stop asking one abrupt release window to simultaneously carry beta matching, lapse margin, carve relaxation, and packet-edge derivative cleanup.

## Recommendation

Do not treat the shaped beta sleeve as a selected architecture.

Use it as evidence that the next stage should mature release choreography:

```text
Keep the packet-edge/trailing-edge diagnosis.
Stop optimizing stronger local beta sleeves as the primary lever.
Build an explicit matched-hold and derivative-limited release law.
Then rerun V2/V5 and report whether the stricter choreography reduces the radial-null floor without packet failures or point-peak inflation.
```

Stage II should remain paused. The demanded-source target is not yet clean enough to justify selecting a matter-source realization.
