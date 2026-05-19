# Stage I Split-Carve and Local Null-Cushion Progress

## Purpose

This pass tested a design separation suggested by the channel-cause ledger:

```text
Do not treat packet carve as one blunt packet-local containment knob.
Split it into:
  softer early/live-entry containment,
  stronger catch/rematch containment,
  and only a small local null cushion where reduced carve exposes Tkk.
```

The goal was not to add another independent packet patch permanently. The goal was to see whether the algebraic separation is real enough to consolidate into a more coherent coupled support law.

## Harness Update

The source harness now separates the standing-support packet carve into two additive containment terms:

```text
standing_support_packet_exclusion
standing_support_packet_exclusion_catch
```

The original packet carve remains the entry/live containment field. The new catch carve has its own radius, width, schedule, and temporal profile:

```text
standing_support_packet_exclusion_catch_radius_multiplier
standing_support_packet_exclusion_catch_width_multiplier
standing_support_packet_exclusion_catch_schedule
standing_support_packet_exclusion_catch_temporal_profile
```

The harness also adds a weak packet-local lapse/null cushion:

```text
standing_support_packet_null_cushion_log_gain
standing_support_packet_null_cushion_mode
standing_support_packet_null_cushion_inner_radius_multiplier
standing_support_packet_null_cushion_radius_multiplier
standing_support_packet_null_cushion_width_multiplier
standing_support_packet_null_cushion_schedule
standing_support_packet_null_cushion_temporal_profile
```

This cushion multiplies `alpha` through a packet-window factor and is recorded separately from the broader packet-lapse factor:

```text
standing_support_packet_null_cushion_window
standing_support_packet_null_cushion_factor
standing_support_packet_null_cushion_delta_alpha
standing_support_packet_null_cushion_window_slope_abs
```

The purpose is narrow: trim the exposed radial-null region without turning lapse into the main release driver.

## Shared Screen Infrastructure

The split-carve screen initially duplicated the radial-support screen plumbing. That was refactored into:

```text
toolkit/adm_harness_cli/adm_harness/source_screening.py
```

The shared module now handles:

```text
source-ledger manifest loading
SourceParams / grid reconstruction
spec-file loading and label filtering
common source-channel summary rows
top-bad-point output
screen manifest writing and hashes
service-factor-aware case labels
```

Both screen runners now use this shared infrastructure:

```text
toolkit/adm_harness_cli/scripts/run_split_carve_screen.py
toolkit/adm_harness_cli/scripts/run_radial_support_screen.py
```

This keeps later screens from becoming a pile of one-off CSV runners while preserving screen-specific spec mapping.

## Main V5 High-Resolution Check

The main high-resolution check used the current two-feature radial candidate as context and compared:

```text
current
entry075_catch015
entry075_catch015_null_ann_m005
```

Output directory:

```text
toolkit/adm_harness_cli/runs/stage1_v5_split_carve_highres_81x109/
```

Grid:

```text
81 x 109
s range: -0.96 to 1.65
l range: -2.80 to 2.80
```

The tested split-carve/null-cushion candidate was:

```text
entry carve:      0.75, live_only
catch carve:      0.15, catch_only
null cushion:    -0.05 log gain
null mode:        annular
null inner/r/w:   1.0 / 1.7 / 2.2
null schedule:    catch_only
```

High-resolution V5 summary:

```text
current:
  packet failures:      0
  max packet norm live: -5.455491
  live Tkk burden:      9.714007
  live p_l burden:      0.396128
  live j_l burden:      0.119451
  live pOmega burden:   2.746906
  Tkk point peak:       1.289256
  p_l point peak:       0.070877
  j_l point peak:       0.031188
  pOmega point peak:    0.570530

entry075_catch015:
  packet failures:      0
  max packet norm live: -23.766801
  live Tkk burden:      10.016699
  live p_l burden:      0.402683
  live j_l burden:      0.065546
  live pOmega burden:   1.952462
  Tkk point peak:       1.067814
  p_l point peak:       0.018968
  j_l point peak:       0.011476
  pOmega point peak:    0.220166

entry075_catch015_null_ann_m005:
  packet failures:      0
  max packet norm live: -23.635666
  live Tkk burden:      9.917827
  live p_l burden:      0.402858
  live j_l burden:      0.065737
  live pOmega burden:   1.922939
  Tkk point peak:       1.052742
  p_l point peak:       0.018997
  j_l point peak:       0.011497
  pOmega point peak:    0.218683
```

Relative to current, the split-carve plus annular null cushion gives:

```text
live Tkk burden:      1.020982 x current
live p_l burden:      1.016989 x current
live j_l burden:      0.550326 x current
live pOmega burden:   0.700038 x current
Tkk point peak:       0.816550 x current
pOmega point peak:    0.383298 x current
```

So the candidate survives V5 and produces major current/angular/peak relief, but it does not yet beat the current architecture on integrated live `Tkk` or `p_l`.

## V2 Drop-Back Check

A V2 diagnostic was run to test whether the remaining gap is simply that V5 is too demanding for this architecture. To keep the comparison fair, the current V5 architecture parameters were retained and only `V` was changed to `2`.

Input context:

```text
toolkit/adm_harness_cli/runs/stage1_v2_two_feature_radial_current_context/
```

Output directory:

```text
toolkit/adm_harness_cli/runs/stage1_v2_split_carve_highres_81x109/
```

High-resolution V2 summary:

```text
current:
  packet failures:      0
  max packet norm live: -5.615541
  live Tkk burden:      5.352058
  live p_l burden:      0.303496
  live j_l burden:      0.047056
  live pOmega burden:   2.203718
  Tkk point peak:       1.289256
  p_l point peak:       0.019612
  j_l point peak:       0.009123
  pOmega point peak:    0.229194

entry075_catch015_null_ann_m005:
  packet failures:      0
  max packet norm live: -23.636530
  live Tkk burden:      5.549517
  live p_l burden:      0.392682
  live j_l burden:      0.031275
  live pOmega burden:   1.703449
  Tkk point peak:       0.962345
  p_l point peak:       0.011633
  j_l point peak:       0.009097
  pOmega point peak:    0.205843
```

Relative to V2 current:

```text
live Tkk burden:      1.0369 x current
live p_l burden:      1.2939 x current
live j_l burden:      0.6646 x current
live pOmega burden:   0.7730 x current
Tkk point peak:       0.7464 x current
pOmega point peak:    0.8981 x current
```

Dropping to V2 does not make the split-carve/null-cushion branch an all-around solution. The same tradeoff remains: point peaks, `j_l`, and pOmega improve, while integrated live `Tkk` and especially `p_l` worsen.

This is an important diagnostic result. The gap is not just that V5 is too high for an otherwise clean architecture. The remaining cost is structural in the packet/support containment and radial-pressure balance.

## Interpretation

The split-carve/null-cushion branch is useful, but not yet a sealed Stage I candidate.

The useful part is the separation:

```text
softer early/live-entry carve:
  reduces live angular/current exposure and hard point peaks;

catch/rematch carve add-back:
  recovers much of the live Tkk/p_l burden that reduced entry carve exposes;

small annular null cushion:
  trims Tkk burden and peak modestly without acting as a broad lapse driver.
```

The problematic part is that the improvement is not globally dominant. The branch improves several important hard surfaces, but leaves an integrated `Tkk/p_l` tax. That tax persists at V2, so it is not simply a high-load artifact.

The current collection of `standing_support_packet_*` variables is therefore better understood as a diagnostic basis than as the final design surface. The piecewise knobs have revealed which algebraic jobs need to be coupled:

```text
contain packet/support separation;
avoid early live angular/current exposure;
protect catch/rematch radial-null margins;
avoid increasing integrated radial pressure cost;
keep lapse as a weak local cushion, not a release driver.
```

## Next Design Direction

The next design move should reduce degrees of freedom rather than add more independent packet knobs.

Instead of continuing with independent piecewise controls, build a coupled packet containment/support profile with a smaller conceptual surface:

```text
one containment profile with entry and catch amplitudes;
one radial support profile tied to that containment profile;
one optional weak annular null cushion tied to the exposed radial-null region;
smooth or minimum-jerk temporal joins;
explicit derivative limits or boundary conditions at packet-edge joins;
then V5 as primary target, V2 as diagnostic, V10 as stress check.
```

The individual `standing_support_packet_*` controls should remain in the harness as diagnostics and future fine-tuning handles. But the design should be promoted to a more holistic ansatz, where carve, radial support, and the weak null cushion are generated from one smoother coupled shape family.

The viability read is mixed but not discouraging:

```text
not solved:
  integrated live Tkk/p_l still do not cleanly improve;

real progress:
  packet safety survives;
  hard point peaks drop;
  live j_l and pOmega improve strongly;
  V2 confirms the remaining issue is structural, not just excessive V;

best next question:
  can a coupled smooth profile preserve the peak/current/angular gains while removing the p_l/Tkk tax?
```

If the coupled profile still carries the same `p_l` tax after high-resolution checks, then Stage I may have found a durable bound for this architecture family. If the coupled profile removes that tax, this branch becomes a serious path toward a robust hard-bounded active-rail Stage I closure.
