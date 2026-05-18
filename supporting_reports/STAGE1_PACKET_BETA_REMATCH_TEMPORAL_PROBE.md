# Stage I Packet Beta Rematch and Temporal-Lapse Probe

## Purpose

The annular shoulder probe showed that spatial packet-support carving alone is unlikely to deliver another order-of-magnitude reduction in live packet hard-channel burden. This probe tested the next recommended harness direction:

```text
add a packet-local beta rematch / beta-gradient softening partner
test it both alone and in combination with a temporal lapse ramp
rank candidates with explicit packet-norm and point-peak penalties
```

This remains demanded-source placement accounting only.

## Harness Change

The source ledger now exposes a packet-local beta rematch control:

```text
standing_support_packet_beta_rematch_gain
standing_support_packet_beta_rematch_radius_multiplier
standing_support_packet_beta_rematch_width_multiplier
standing_support_packet_beta_rematch_schedule
```

The rematch window uses the same packet-window schedule families as carve and lapse. Positive gain applies:

```text
delta_beta_packet = -gain * packet_beta_rematch_window * (vcoord + beta_pre_rematch)
```

So positive gain nudges the local shift toward cancelling the modeled packet coordinate velocity. The point ledger records:

```text
standing_support_packet_beta_rematch_window
standing_support_packet_delta_beta
beta_pre_packet_rematch
```

The focused ledger and overlay sweep CLIs expose singular/plural forms of the new controls.

The worldtube ranking now also penalizes positive packet-norm count, near-zero packet-norm margin, and point-peak excess. This prevents boundary branches with good live fractions but bad V10 margin from ranking too highly.

## Runs

Exploratory and focused runs:

```text
toolkit/adm_harness_cli/runs/stage1_v5_beta_rematch_smoke/
toolkit/adm_harness_cli/runs/stage1_v10_beta_rematch_smoke/
toolkit/adm_harness_cli/runs/stage1_v5_beta_rematch_focused/
toolkit/adm_harness_cli/runs/stage1_v10_beta_rematch_focused/
toolkit/adm_harness_cli/runs/stage1_v5_temporal_ramp_check/
toolkit/adm_harness_cli/runs/stage1_v5_temporal_beta_combo/
toolkit/adm_harness_cli/runs/stage1_v10_temporal_beta_combo/
toolkit/adm_harness_cli/runs/stage1_v10_temporal_beta_highgain/
toolkit/adm_harness_cli/runs/stage1_v10_temporal_beta_gain_tradeoff/
toolkit/adm_harness_cli/runs/stage1_v8_annular_and_temporal_beta_check/
```

All focused checks used the moderate annular branch as the baseline geometry:

```text
standing_support_packet_exclusion = 0.32
standing_support_packet_exclusion_shoulder = 0.08
standing_support_packet_exclusion_shoulder_mode = annular
standing_support_packet_lapse_log_gain = 1.00
```

## Beta Rematch Alone

At report grid, beta rematch alone is a useful point-peak shaper but not a radial-null solution.

V5 focused result:

| beta gain | packet failures | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 0 | 0.096545 | 0.075388 | 1.238714 | 7.595579 |
| 0.10 | 0 | 0.096139 | 0.075388 | 1.237637 | 7.071307 |
| 0.20 | 0 | 0.096200 | 0.075389 | 1.237481 | 6.564166 |

V10 focused result:

| beta gain | packet failures | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 0 | 0.095680 | 0.075388 | 1.107752 | 4.100704 |
| 0.10 | 0 | 0.098485 | 0.075389 | 1.108878 | 3.534678 |
| 0.20 | 0 | 0.106604 | 0.075389 | 1.109913 | 3.648101 |

Interpretation:

```text
positive beta rematch has the right sign for peak reduction
it does not lower V10 live radial-null exposure
large beta rematch becomes a radial-null cost
```

## Temporal Lapse Ramp

Using `entry_catch_release` for the packet-lapse schedule exposed a more interesting tradeoff. With carve and shoulder still `live_only`, V5 live radial-null dropped, but packet norm failed:

| carve schedule | shoulder schedule | lapse schedule | packet failures | live Tkk fraction | live p_l fraction | max point peak ratio |
|---|---|---|---:|---:|---:|---:|
| live_only | live_only | live_only | 0 | 0.096545 | 0.075388 | 7.595579 |
| live_only | live_only | entry_catch_release | 43 | 0.072203 | 0.075391 | 3.434036 |
| live_only | entry_catch_release | entry_catch_release | 41 | 0.074642 | 0.075253 | 3.397077 |

This is a real diagnostic: temporal lapse gating can reduce radial-null and peak cost, but it consumes too much causal margin by itself.

## Temporal Lapse Plus Beta Rematch

Combining `entry_catch_release` packet lapse with positive beta rematch rescued V5 packet safety:

| V | lapse gain | beta gain | packet failures | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 1.00 | 0.20 | 0 | 0.073763 | 0.075393 | 1.107766 | 3.362681 |
| 5 | 1.00 | 0.30 | 0 | 0.075340 | 0.075394 | 1.108778 | 3.327277 |
| 5 | 1.00 | 0.40 | 0 | 0.077722 | 0.075395 | 1.110173 | 3.292056 |

But the same branch does not survive V10 at comparable gains:

| V | lapse gain | beta gain | packet failures | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 1.00 | 0.20 | 67 | 0.084977 | 0.075396 | 1.109218 | 2.110783 |
| 10 | 1.00 | 0.30 | 62 | 0.092901 | 0.075399 | 1.111537 | 2.088560 |
| 10 | 1.00 | 0.40 | 55 | 0.102039 | 0.075402 | 1.113525 | 2.066451 |

Higher beta gains recover V10 safety, but they erase the radial-null improvement:

| V | lapse gain | beta gain | packet failures | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 1.00 | 0.60 | 0 | 0.120067 | 0.075408 | 1.116397 | 2.201465 |
| 10 | 1.00 | 0.80 | 0 | 0.138675 | 0.075416 | 1.118671 | 2.804231 |
| 10 | 1.00 | 1.00 | 0 | 0.157160 | 0.075425 | 1.189598 | 3.557998 |

Lowering the temporal-lapse gain did not find a V10-safe branch below the moderate annular V10 radial-null fraction:

| V | lapse gain | beta gain | packet failures | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0.50 | 0.60 | 0 | 0.099771 | 0.075410 | 1.106389 | 1.580073 |
| 10 | 0.70 | 0.60 | 0 | 0.106162 | 0.075409 | 1.109598 | 1.580584 |
| 10 | 0.85 | 0.60 | 0 | 0.112680 | 0.075409 | 1.113020 | 1.850511 |

The lower-`Tkk` V10 cases in this tradeoff sweep remained packet-unsafe.

## V8 Service-Class Check

A V8 check was added without changing the harness to see whether the project should stop treating V10 as the hard optimization target. The moderate annular branch survives V8 cleanly:

| V | lapse schedule | beta gain | packet failures | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|---:|
| 8 | live_only | 0.00 | 0 | 0.095756 | 0.075388 | 1.132136 | 5.123597 |

The lower-radial-null temporal-lapse branches still consume too much causal margin at V8:

| V | lapse schedule | beta gain | packet failures | live Tkk fraction | live p_l fraction | max total ratio | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|---:|
| 8 | entry_catch_release | 0.00 | 67 | 0.072726 | 0.075391 | 1.106500 | 2.541883 |
| 8 | entry_catch_release | 0.20 | 59 | 0.078872 | 0.075395 | 1.108444 | 2.489066 |
| 8 | entry_catch_release | 0.60 | 0 | 0.105505 | 0.075403 | 1.115691 | 2.385052 |

Interpretation:

```text
V8 supports the moderate annular branch as an operational service-class candidate.
It does not turn the temporal/beta low-Tkk branch into a packet-safe pass.
Restoring V8 packet safety with high beta again raises live radial-null burden.
```

## Interpretation

The combined beta/timing harness answered the immediate question:

```text
beta rematch is useful, but it is not the missing order-of-magnitude radial-null lever
temporal lapse gating can lower radial-null exposure, but it spends V10 causal margin
high beta rematch can restore V10 safety, but it restores radial-null burden too
```

The best new V5 diagnostic branch is much better than the previous moderate annular candidate:

```text
moderate annular V5:        live Tkk/p_l = 0.096545 / 0.075388, peak = 7.595579
temporal+beta V5:           live Tkk/p_l = 0.073763 / 0.075393, peak = 3.362681
```

But the V10-safe branch is not better on radial-null:

```text
moderate annular V10:       live Tkk/p_l = 0.095680 / 0.075388, peak = 4.100704
best safe tradeoff V10:     live Tkk/p_l = 0.099771 / 0.075410, peak = 1.580073
moderate annular V8:        live Tkk/p_l = 0.095756 / 0.075388, peak = 5.123597
```

So the new control is valuable for peak management and for diagnosing the causal-margin/radial-null tradeoff. It should not replace the moderate annular branch as the selected Stage I architecture.

## Implication

The next harness improvement should not simply add more local packet beta or lapse amplitude. The evidence now points to a deeper coupling:

```text
V5 can trade temporal lapse gating plus beta rematch into lower radial-null exposure.
V8 and V10 require so much rematch to keep the low-Tkk temporal branch causal-safe that the radial-null gain disappears.
```

Recommended next directions:

```text
1. Add a V-aware or service-factor-scaled temporal/beta control law instead of one fixed V5/V10 gain.
2. Add an independent temporal ramp-width parameter for packet lapse and beta rematch, not just schedule choice.
3. Test nonuniform beta rematch shapes that avoid steep packet-edge gradients.
4. Keep the moderate annular branch as the selected V5-V8 operational architecture, with V10 treated as a warning-grade edge check until a deeper timing/control law beats its live radial-null fraction.
```

Stage II should remain paused. The probe improved the diagnosis and supports a V5-V8 operational service-class framing, but it did not produce a clean strict minimal-traversability source-placement target.
