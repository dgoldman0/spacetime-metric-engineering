# Stage I Release-Choreography Artifact Check

## Purpose

This pass tested whether the V5 release-choreography refreeze was a real mechanism or an artifact of a sharp floor/sleeve seam.

Target hierarchy for this pass:

```text
V5 is the active engineering target.
V2 remains a secondary diagnostic scale, not a goal.
V10 remains an edge smoke test, not the current optimization driver.
```

The decisive question was:

```text
Does V5 packet safety survive smoother floor unions, softer/wider trailing-edge joins, and higher grid resolution?
```

## Runs

Main runs:

```text
toolkit/adm_harness_cli/runs/stage1_v5_release_artifact_smoothing_screen/
toolkit/adm_harness_cli/runs/stage1_v5_release_artifact_highres_check/
toolkit/adm_harness_cli/runs/stage1_v5_release_artifact_best_smooth_ledger/
toolkit/adm_harness_cli/runs/stage1_v10_release_artifact_best_smooth_smoke/
```

The smoothing screen kept the refrozen release choreography fixed and varied only:

```text
standing_support_packet_beta_rematch_floor_mode = max | blend | add
standing_support_packet_beta_rematch_width_multiplier = 1.0 | 1.3 | 1.6
standing_support_packet_beta_rematch_edge_softness = 1.0 | 1.5 | 2.0
standing_support_packet_beta_rematch_center_floor = 0.55 | 0.60 | 0.65
```

Fixed branch:

```text
V = 5
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
standing_support_packet_beta_rematch_schedule = live_only
```

## V5 Smoothing Screen

The 81-case V5 screen was run at the report grid, `53 x 73`.

```text
total cases: 81
zero packet-norm failures: 37
zero top hard-channel live packet points: 77
both gates simultaneously: 37
```

The exact prior hard-union refreeze point reproduced the old peak problem:

| floor mode | beta width | edge softness | floor | packet failures | top hard live points | max packet norm | live Tkk fraction | live p_l fraction | max total ratio | max point peak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `max` | 1.0 | 1.0 | 0.60 | 0 | 0 | -5.236716 | 0.028567 | 0.006986 | 2.228077 | 43.889793 |

But many smoother/wider variants preserved the V5 gates and cut the point peak by about a factor of five.

Best gated rows by point peak:

| floor mode | beta width | edge softness | floor | packet failures | top hard live points | max packet norm | live Tkk fraction | live p_l fraction | max total ratio | max point peak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `blend` | 1.6 | 1.0 | 0.60 | 0 | 0 | -5.473217 | 0.023960 | 0.007027 | 2.037524 | 8.748470 |
| `blend` | 1.3 | 1.5 | 0.60 | 0 | 0 | -5.278531 | 0.024202 | 0.007184 | 2.030623 | 8.903916 |
| `blend` | 1.0 | 2.0 | 0.55 | 0 | 0 | -5.619104 | 0.023450 | 0.006903 | 2.047773 | 8.958024 |
| `add` | 1.6 | 2.0 | 0.60 | 0 | 0 | -3.442926 | 0.024274 | 0.007472 | 2.038626 | 8.990090 |
| `blend` | 1.6 | 1.5 | 0.60 | 0 | 0 | -5.409755 | 0.023172 | 0.007071 | 1.978410 | 9.080466 |

The important result is not that every smoothing survives. It does not. The `add` union is usually too aggressive and frequently burns packet margin. The important result is that the smoother `blend` union survives when paired with a wider trailing-edge sleeve.

## Higher-Resolution Check

The selected neighborhood was rerun at `81 x 109`.

| floor mode | beta width | edge softness | floor | packet failures | top hard live points | max packet norm | live Tkk fraction | live p_l fraction | max total ratio | max point peak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `blend` | 1.6 | 1.0 | 0.60 | 0 | 0 | -5.455516 | 0.024255 | 0.006986 | 2.035942 | 8.627056 |
| `blend` | 1.6 | 1.5 | 0.60 | 0 | 0 | -5.373688 | 0.023788 | 0.007022 | 1.976459 | 8.971424 |
| `blend` | 1.0 | 1.5 | 0.60 | 0 | 0 | -0.421576 | 0.025777 | 0.007224 | 2.119393 | 9.278222 |
| `max` | 1.6 | 1.5 | 0.60 | 0 | 0 | -5.507111 | 0.022362 | 0.006798 | 1.988207 | 9.690332 |
| `max` | 1.0 | 1.5 | 0.60 | 0 | 0 | -5.253305 | 0.025030 | 0.006981 | 2.078297 | 15.518113 |
| `max` | 1.6 | 1.0 | 0.60 | 0 | 0 | -5.507111 | 0.023628 | 0.006776 | 2.094995 | 32.560256 |
| `max` | 1.0 | 1.0 | 0.60 | 0 | 1 | -5.253305 | 0.029362 | 0.006934 | 2.286748 | 117.218036 |
| `blend` | 1.0 | 1.0 | 0.60 | 11 | 0 | 44.570625 | 0.025798 | 0.007137 | 2.257567 | 21.468399 |

This is the key artifact result:

```text
The exact hard-union refreeze does not survive refinement cleanly.
The smoother blend union alone does not survive refinement.
The smoother blend union plus a wider trailing-edge sleeve does survive refinement.
```

So the prior hard seam was partly a diagnostic crutch, but the underlying mechanism is not just a grid artifact. The packet-safety mechanism survives smoothing and grid refinement when the rematch layer is given enough radial thickness.

## Focused Point Ledger

The best higher-resolution smoother branch was:

```text
standing_support_packet_beta_rematch_floor_mode = blend
standing_support_packet_beta_rematch_width_multiplier = 1.6
standing_support_packet_beta_rematch_edge_softness = 1.0
standing_support_packet_beta_rematch_center_floor = 0.60
```

Focused ledger:

```text
grid = 81 x 109
rows = 8829
positive packet-norm live points = 0
max packet norm live = -5.455516
```

The top bad points remain outside the live packet:

```text
top channel: neg_Tkk_radial
top stages: catch_rematch
top regions: core_throat and support_edge
inside_packet_live: false for the listed top points
```

Derivative maxima:

| diagnostic | max value | stage | region | live packet |
|---|---:|---|---|---|
| `release_profile_slope_abs` | 10.415634 | `release_shift_fade` | `outer_quarantine_shell` | false |
| `standing_support_packet_carve_window_slope_abs` | 6.034293 | `catch_rematch` | `core_throat` | false |
| `standing_support_packet_lapse_window_slope_abs` | 5.613969 | `catch_rematch` | `core_throat` | false |
| `standing_support_packet_beta_rematch_window_slope_abs` | 5.545130 | `held_carry` | `core_throat` | false |

Compared with the previous refreeze ledger, the beta-rematch window derivative maximum fell from about `8.14` to about `5.55`. That is consistent with the point-peak improvement. The remaining derivative burden is now less dominated by the beta sleeve and more by the broader release/carve/lapse infrastructure.

## V10 Edge Smoke

The best smoother V5 branch was also run as a cheap V10 edge smoke at `53 x 73`.

| V | floor mode | beta width | edge softness | packet failures | top hard live points | max packet norm | live Tkk fraction | live p_l fraction | max total ratio | max point peak |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | `blend` | 1.6 | 1.0 | 16 | 2 | 571.583285 | 0.042804 | 0.016184 | 3.544930 | 63.765303 |

V10 remains out of reach for this fixed V5 law. The smoothing improves the V5 artifact story but does not make the current choreography a V10 architecture.

## Interpretation

The result is a qualified but real upgrade:

```text
The old hard-union refreeze should not be treated as the final candidate.
The release-choreography mechanism should not be dismissed as a grid artifact.
The serious V5 branch is the smoother blend-floor, wider trailing-edge sleeve family.
```

The mechanism is more specific than before:

```text
The packet needs a live trailing-edge beta rematch floor.
That floor should be smoothly blended, not hard-maxed, if point peaks matter.
But the smooth blend needs enough radial sleeve width; smoothing without width loses causal margin.
```

This is a useful separation:

```text
hard seam = artifact-prone implementation detail
live trailing-edge rematch with finite radial thickness = surviving mechanism
```

## Implications

For V5, the branch has become more serious. It now survives:

```text
zero packet-norm failures,
zero top hard-channel live packet points,
smoother floor union,
wider trailing-edge join,
higher grid resolution.
```

It is still not a final Stage I source target:

```text
max total source ratio remains near 2,
live radial-null fraction remains around 2.4 percent,
V10 edge smoke fails,
remaining top bad points remain in catch/rematch core-throat infrastructure.
```

Recommended next move:

```text
Refreeze the V5 candidate around blend + trailing-edge width 1.6.
Do not return to the hard max seam except as a diagnostic comparator.
Next optimize the infrastructure-side release/carve/lapse derivative structure,
especially catch/rematch core-throat and support-edge transitions.
Keep V10 as an edge smoke only after the V5 infrastructure burden is lower.
Use V2 only if a proposed timing law needs a mechanism microscope.
```

Stage II should remain paused. The V5 choreography is now less artifact-like, but the demanded-source burden is still too infrastructure-expensive to select a matter-source model.
