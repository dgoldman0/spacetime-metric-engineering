# Stage I Annular Shoulder Shaping Probe

## Purpose

The two-zone packet carve reduced live packet hard-channel fractions, but it did not reduce them by an order of magnitude. This probe tested whether adjusted shoulder geometry could push the live fractions down further without reintroducing packet-norm failures.

The new tested shape was an annular shoulder: a wider support-floor carve around the packet tube rather than another filled carve centered on the packet.

## Harness Change

The standing-support packet shoulder now supports a shape mode:

```text
standing_support_packet_exclusion_shoulder_mode = filled | annular
```

`filled` preserves the previous two-zone behavior. `annular` computes:

```text
shoulder_window = clip(outer_packet_window - inner_packet_window, 0, 1)
```

This lets the core carve reduce the packet-center support floor while the shoulder softens the surrounding transition.

The focused ledger and overlay sweep CLIs expose:

```text
--standing-support-packet-exclusion-shoulder-mode
--standing-support-packet-exclusion-shoulder-modes
```

## Runs

Exploratory runs:

```text
toolkit/adm_harness_cli/runs/stage1_v5_annular_shoulder_smoke/
toolkit/adm_harness_cli/runs/stage1_v10_annular_shoulder_check/
toolkit/adm_harness_cli/runs/stage1_v5_annular_shoulder_selected_check/
toolkit/adm_harness_cli/runs/stage1_v10_annular_shoulder_selected_check/
toolkit/adm_harness_cli/runs/stage1_v5_deep_annular_probe/
toolkit/adm_harness_cli/runs/stage1_v10_deep_annular_probe_selected/
```

The broad V5 smoke was intentionally stopped after enough per-case outputs were available to identify the useful regime; it was too wide for an exploratory pass.

## Best Moderate Annular Candidate

Selected moderate annular check:

```text
standing_support_packet_exclusion = 0.32
standing_support_packet_exclusion_width_multiplier = 1.0
standing_support_packet_exclusion_shoulder = 0.08
standing_support_packet_exclusion_shoulder_mode = annular
standing_support_packet_exclusion_shoulder_radius_multiplier = 1.4
standing_support_packet_exclusion_shoulder_width_multiplier = 1.8
standing_support_packet_lapse_log_gain = 1.00
standing_support_packet_lapse_radius_multiplier = 1.7
standing_support_packet_lapse_width_multiplier = 2.0
```

Focused 53x73 result:

| V | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0 | 0.096545 | 0.075388 | 0 | 1.238714 | 7.595579 |
| 10 | 0 | 0.095680 | 0.075388 | 0 | 1.107752 | 4.100704 |

This improves live fractions compared with the balanced filled-shoulder candidate, but the point-peak and aggregate costs are much worse.

## Deep Annular Diagnostic

Deep diagnostic point:

```text
standing_support_packet_exclusion = 0.60
standing_support_packet_exclusion_width_multiplier = 1.4
standing_support_packet_exclusion_shoulder = 0.12
standing_support_packet_exclusion_shoulder_mode = annular
standing_support_packet_exclusion_shoulder_radius_multiplier = 1.5
standing_support_packet_exclusion_shoulder_width_multiplier = 2.0
standing_support_packet_lapse_log_gain = 1.00
```

V5 looked closer to the desired live-fraction target:

| V | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0 | 0.057229 | 0.023731 | 0 | 1.196173 | 11.098429 |

But the same branch fails the V10 edge gate:

| V | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 165 | 0.041852 | 0.023521 | 0 | 1.187070 | 6.143737 |

The deep carve can reduce live fractions further, especially radial pressure, but it consumes too much causal margin and introduces large point-peak cost.

## Interpretation

Annular shoulder shaping improves the live-packet burden, but it does not provide the hoped-for order-of-magnitude reduction in a V5/V10-safe branch.

Current readout:

```text
balanced filled shoulder:    V10 live Tkk/p_l = 0.130 / 0.114
moderate annular shoulder:   V10 live Tkk/p_l = 0.096 / 0.075
deep annular diagnostic:     V5 live Tkk/p_l = 0.057 / 0.024, but V10 packet norm fails
```

The remaining radial-null burden appears resistant to purely radial packet-support carving. Radial pressure can be pushed much lower, but radial-null exposure stalls unless the metric pays with V10 causal-margin failure and large peaks.

## Implication

This narrows the next design problem:

```text
Shoulder shaping alone is probably not enough for another order-of-magnitude live-fraction reduction.
The next useful knob should target the radial-null channel more directly.
```

Recommended next harness directions:

```text
1. Add a packet-local beta rematch or beta-gradient softening partner tied to the carve window.
2. Add an independent temporal shoulder/ramp for the carve, not just live_only, to reduce entry/catch transition peaks.
3. Add a radial-null-aware objective/ranking that explicitly penalizes V10 packet-norm margin loss and point peaks.
4. Treat the deep annular branch as a diagnostic boundary, not a selected architecture.
```

Stage II should remain paused. The best V5/V10-safe branches are better than before, but not clean enough to be a matter-source target.
