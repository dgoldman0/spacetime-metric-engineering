# Stage I Radial Support Geometry Refinement

## Purpose

This follow-up refined the radial support-law geometry around the previous balanced candidate:

```text
core +0.05 on entry_catch_release
annular ring +0.12 on catch_only
ring radius multiplier = 2.2
ring width multiplier = 2.8
```

The goal was to determine whether the remaining live `p_l` cost could be reduced while preserving the Tkk and pOmega peak relief.

## Harness Update

The radial support screen runner now supports JSON spec files:

```text
toolkit/adm_harness_cli/scripts/run_radial_support_screen.py --spec-file ...
```

It also records the actual footprint parameters in each summary row:

```text
core_radius_multiplier
core_width_multiplier
shoulder_radius_multiplier
shoulder_width_multiplier
core_temporal_profile
shoulder_temporal_profile
```

This makes geometry probes reproducible without hardcoding every candidate into the script.

## Runs

Main local output directories:

```text
toolkit/adm_harness_cli/runs/stage1_v5_radial_geometry_quick_21x37/
toolkit/adm_harness_cli/runs/stage1_v5_radial_geometry_r24_41x73/
toolkit/adm_harness_cli/runs/stage1_v5_radial_geometry_r24_81x109/
```

The quick screen swept:

```text
ring radius multiplier: 2.0, 2.2, 2.4
ring width multiplier:  2.4, 2.8, 3.2
ring gain:              +0.12
core gain:              +0.05
```

The best family moved the catch-only annular ring outward to radius multiplier `2.4`. Width was a smaller tradeoff, so `2.4` and `3.2` were promoted to high-resolution comparison.

## High-Resolution Comparison

Same-code `81 x 109` comparison:

```text
base:
  packet failures:      0
  max packet norm live: -21.618963
  live Tkk fraction:    0.020241558
  live p_l fraction:    0.006372662
  live j_l fraction:    0.130283695
  live pOmega fraction: 0.309584956
  Tkk point peak:       1.337321950
  pOmega point peak:    0.241848328

previous balanced candidate, ring 2.2 / 2.8:
  packet failures:      0
  max packet norm live: -21.612436
  live Tkk fraction:    0.020104230
  live p_l fraction:    0.006459793
  live j_l fraction:    0.129967672
  live pOmega fraction: 0.301790206
  Tkk point peak:       1.285178196
  pOmega point peak:    0.228139190

new geometry, ring 2.4 / 2.4:
  packet failures:      0
  max packet norm live: -21.612436
  live Tkk fraction:    0.020067871
  live p_l fraction:    0.006439339
  live j_l fraction:    0.129978357
  live pOmega fraction: 0.301588286
  Tkk point peak:       1.285178196
  pOmega point peak:    0.228139190

nearby tradeoff, ring 2.4 / 3.2:
  packet failures:      0
  max packet norm live: -21.612436
  live Tkk fraction:    0.020087258
  live p_l fraction:    0.006436868
  live j_l fraction:    0.129961944
  live pOmega fraction: 0.301808816
  Tkk point peak:       1.285178196
  pOmega point peak:    0.228139190
```

Relative to base, the new `2.4 / 2.4` geometry gives:

```text
live Tkk fraction:     lower by 0.000173687
live p_l fraction:     higher by 0.000066677
live j_l fraction:     lower by 0.000305337
live pOmega fraction:  lower by 0.007996670
Tkk point peak:        0.961009 x base
pOmega point peak:     0.943315 x base
packet failures:       0
```

Relative to the previous balanced candidate, the `2.4 / 2.4` ring:

```text
lowers live Tkk further;
reduces the live p_l cost;
lowers live pOmega slightly;
preserves the same Tkk and pOmega peak relief;
keeps zero packet failures.
```

## Interpretation

The ring geometry is telling us that radial support is separating into at least two jobs.

The `2.4 / 2.4` ring behaves like a targeted outer catch ring. It sits far enough out to act on the radial-metric hard zone, but remains narrow enough not to smear too much correction back into the packet/support volume. That improves Tkk and pOmega while also reducing the live `p_l` cost relative to the previous `2.2 / 2.8` ring.

The `2.4 / 3.2` ring is broader. It slightly improves live `p_l` and live `j_l`, but worsens live Tkk and pOmega. This suggests that a wider ring smooths radial pressure/current distribution but couples more strongly into the angular/null channels.

The tradeoff is therefore:

```text
narrower outer ring:
  better channel localization
  better Tkk / pOmega behavior
  slightly worse p_l / j_l than a wider skirt

wider outer ring:
  smoother p_l / j_l behavior
  worse Tkk / pOmega localization
```

This points toward a two-feature radial profile rather than a single wider ring:

```text
1. a narrow outer catch ring for Tkk / pOmega peak and live-fraction control;
2. a weaker broader skirt for p_l / j_l smoothing.
```

The next design should keep the main ring narrow and add a weaker secondary shoulder only if it can recover `p_l` / `j_l` without giving back the Tkk and pOmega gains.

## Current Candidate

Updated balanced candidate:

```text
standing_support_packet_radial_log_gain = +0.05
standing_support_packet_radial_radius_multiplier = 1.3
standing_support_packet_radial_width_multiplier = 1.8
standing_support_packet_radial_schedule = entry_catch_release

standing_support_packet_radial_shoulder_log_gain = +0.12
standing_support_packet_radial_shoulder_mode = annular
standing_support_packet_radial_shoulder_radius_multiplier = 2.4
standing_support_packet_radial_shoulder_width_multiplier = 2.4
standing_support_packet_radial_shoulder_schedule = catch_only
```

Nearby smoothing comparator:

```text
same core and ring gain
ring radius multiplier = 2.4
ring width multiplier = 3.2
```

## Recommended Next Work

Build a two-feature radial profile instead of widening the main ring:

```text
main narrow ring:
  gain around +0.12
  radius around 2.4
  width around 2.4
  schedule catch_only

secondary broad skirt:
  weaker gain, likely +0.02 to +0.05
  radius around 2.4 to 2.6
  width around 3.2 to 4.0
  schedule catch_only or entry_catch_release
```

Gate for the next pass:

```text
preserve zero packet failures;
preserve Tkk and pOmega peak ratios from the 2.4 / 2.4 candidate;
move live p_l and live j_l toward the 2.4 / 3.2 comparator;
do not worsen live Tkk or live pOmega toward the wider-ring tradeoff.
```

## Verification

```text
python -m py_compile scripts/run_radial_support_screen.py
python -m unittest tests.test_validation_ladder_hardening
```

Result:

```text
Ran 18 tests
OK
```
