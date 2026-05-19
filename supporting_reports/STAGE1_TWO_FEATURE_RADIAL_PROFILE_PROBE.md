# Stage I Two-Feature Radial Profile Probe

## Purpose

The previous radial support refinement showed a clear tradeoff:

```text
ring radius 2.4 / width 2.4:
  cleaner live Tkk and pOmega behavior
  slightly higher live p_l / j_l than the wider comparator

ring radius 2.4 / width 3.2:
  slightly cleaner live p_l / j_l
  worse live Tkk and pOmega behavior
```

This probe tested whether those two jobs could be separated into a narrow main catch ring plus a weaker broad skirt. The question was not whether this would discover a new primary mechanism. The question was whether the remaining radial support profile could be smoothed without giving back the hard-won Tkk and pOmega improvements.

## Harness Update

The source harness now has an additional packet-local radial support feature:

```text
standing_support_packet_radial_skirt_log_gain
standing_support_packet_radial_skirt_mode
standing_support_packet_radial_skirt_inner_radius_multiplier
standing_support_packet_radial_skirt_radius_multiplier
standing_support_packet_radial_skirt_width_multiplier
standing_support_packet_radial_skirt_schedule
standing_support_packet_radial_skirt_temporal_profile
```

The skirt is multiplied into the same `gamma_ll` packet radial factor as the core and shoulder terms:

```text
gamma_ll *= exp(core_gain * core_window
              + shoulder_gain * shoulder_window
              + skirt_gain * skirt_window)
```

For annular skirts, the harness subtracts an independently sized inner packet window from an outer packet window and clips the result into `[0, 1]`. The ledger records both the skirt window and its temporal slope:

```text
standing_support_packet_radial_skirt_window
standing_support_packet_radial_skirt_window_slope_abs
```

The radial support screen runner also accepts skirt parameters in JSON spec files so this family can be reproduced without editing the script.

## Runs

Main local output directories:

```text
toolkit/adm_harness_cli/runs/stage1_v5_radial_skirt_quick_21x37/
toolkit/adm_harness_cli/runs/stage1_v5_radial_skirt_41x73/
toolkit/adm_harness_cli/runs/stage1_v5_radial_skirt_81x109/
```

The promoted skirt candidate was:

```text
core:
  gain     +0.05
  schedule entry_catch_release
  radius   1.3
  width    1.8

main annular ring:
  gain     +0.12
  schedule catch_only
  radius   2.4
  width    2.4

secondary annular skirt:
  gain         +0.05
  schedule     catch_only
  inner radius 2.4
  outer radius 2.6
  width        3.2
```

## Medium-Resolution Check

At `41 x 73`, the skirt comparison was:

```text
base:
  packet failures:      0
  max packet norm live: -23.127396
  live Tkk fraction:    0.020491046
  live p_l fraction:    0.006313959
  live j_l fraction:    0.126037460
  live pOmega fraction: 0.306013695
  Tkk point peak:       1.342257804
  pOmega point peak:    0.234728620

main ring only, 2.4 / 2.4:
  packet failures:      0
  max packet norm live: -23.127223
  live Tkk fraction:    0.020375007
  live p_l fraction:    0.006381376
  live j_l fraction:    0.125821247
  live pOmega fraction: 0.298089543
  Tkk point peak:       1.289831179
  pOmega point peak:    0.221513816

main ring plus skirt, gain +0.05, radius 2.6, width 3.2:
  packet failures:      0
  max packet norm live: -23.127222
  live Tkk fraction:    0.020374036
  live p_l fraction:    0.006373006
  live j_l fraction:    0.125822113
  live pOmega fraction: 0.298053993
  Tkk point peak:       1.289831179
  pOmega point peak:    0.221513816

main ring plus wider skirt, gain +0.05, radius 2.6, width 4.0:
  packet failures:      0
  max packet norm live: -23.127222
  live Tkk fraction:    0.020376724
  live p_l fraction:    0.006374075
  live j_l fraction:    0.125824022
  live pOmega fraction: 0.298027392
  Tkk point peak:       1.289831179
  pOmega point peak:    0.221513816
```

The width `3.2` skirt was the cleaner balanced option. The width `4.0` skirt gave slightly more pOmega relief but gave back more Tkk and current cleanliness.

## High-Resolution Comparison

Same-code `81 x 109` comparison against the prior high-resolution base and no-skirt main-ring candidate:

```text
base:
  packet failures:      0
  max packet norm live: -21.618963
  live Tkk fraction:    0.020241558
  live p_l fraction:    0.006372662
  live j_l fraction:    0.130283695
  live pOmega fraction: 0.309584956
  Tkk point peak:       1.337321950
  p_l point peak:       0.016756425
  pOmega point peak:    0.241848328

main ring only, 2.4 / 2.4:
  packet failures:      0
  max packet norm live: -21.612436
  live Tkk fraction:    0.020067871
  live p_l fraction:    0.006439339
  live j_l fraction:    0.129978357
  live pOmega fraction: 0.301588286
  Tkk point peak:       1.285178196
  p_l point peak:       0.016739262
  pOmega point peak:    0.228139190

main ring plus skirt, gain +0.05, radius 2.6, width 3.2:
  packet failures:      0
  max packet norm live: -21.612436
  live Tkk fraction:    0.020067589
  live p_l fraction:    0.006430887
  live j_l fraction:    0.129979244
  live pOmega fraction: 0.301551943
  Tkk point peak:       1.285178196
  p_l point peak:       0.016739197
  pOmega point peak:    0.228139190
```

Relative to the no-skirt main ring, the skirt gives:

```text
live Tkk fraction:    lower by 0.000000282
live p_l fraction:    lower by 0.000008452
live j_l fraction:    higher by 0.000000886
live pOmega fraction: lower by 0.000036343
Tkk point peak:       unchanged
p_l point peak:       lower by 0.000000065
pOmega point peak:    unchanged
packet failures:      unchanged at zero
```

Relative to base, the full two-feature profile gives:

```text
live Tkk fraction:    lower by 0.000173969
live p_l fraction:    higher by 0.000058225
live j_l fraction:    lower by 0.000304451
live pOmega fraction: lower by 0.008033014
Tkk point peak:       0.961009 x base
pOmega point peak:    0.943315 x base
packet failures:      unchanged at zero
```

## Interpretation

The two-feature profile works, but at fine-trim scale.

The secondary skirt does not disrupt the narrow ring's main benefit. Packet safety remains hard-bounded in the sampled live packet, and the Tkk/pOmega point-peak relief remains unchanged. It also recovers a small amount of live `p_l` and pOmega cleanliness. That validates the separation between a narrow null/angular localization ring and a weaker pressure/current smoothing skirt.

The size of the gain is the more important result. The skirt improves the candidate, but not enough to count as a new primary architecture knob. Most of the recent radial support gain came from identifying the positive `gamma_ll` direction and then moving the annular ring outward/narrower. The two-feature skirt is a polish layer on top of that geometry.

That means the current Stage I branch is not out of ideas, but it is probably near the local optimum of this radial profile family. More radial-width and skirt sweeps are likely to produce smaller tradeoffs unless a deeper term-level decomposition identifies a specific missed source channel.

## Current Candidate

Current best V5 radial support candidate:

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

standing_support_packet_radial_skirt_log_gain = +0.05
standing_support_packet_radial_skirt_mode = annular
standing_support_packet_radial_skirt_inner_radius_multiplier = 2.4
standing_support_packet_radial_skirt_radius_multiplier = 2.6
standing_support_packet_radial_skirt_width_multiplier = 3.2
standing_support_packet_radial_skirt_schedule = catch_only
```

This candidate should be treated as the current radial support refreeze unless the next algebraic ledger identifies a stronger, more specific missing knob.

## Stage I Implication

The recent progress is real:

```text
packet failures remain zero;
live packet norm remains strongly negative;
Tkk point peak is down by about 3.9 percent from base;
pOmega point peak is down by about 5.7 percent from base;
live pOmega burden is down by about 0.008 absolute fraction;
live Tkk burden is modestly lower;
live j_l burden is modestly lower.
```

The remaining caution is also real. The live `p_l` fraction is still slightly worse than base, and the incremental skirt gain is small. That points away from another broad geometry sweep and toward a more algebraic cause ledger.

The next decisive question is whether the remaining hard points are dominated by:

```text
lapse curvature;
shift/current coupling;
radial-metric curvature;
angular-capacity curvature;
extrinsic-curvature/time-derivative terms;
or cancellations among rho_H, p_l, and 2j_l.
```

If the top bad points all reduce to the already-controlled radial `gamma_ll` profile, then Stage I is close to optimized for this ansatz. If one of those term families stands out, there may still be a real design knob left: likely a local angular-capacity or extrinsic-curvature matching correction rather than another packet-wide radial sleeve.

## Recommended Next Work

Build a term-level algebraic ledger for the top bad points before adding another active design knob.

The minimum useful ledger should classify each top point by:

```text
stage and region;
inside live packet / packet geometry / support edge;
rho_H, p_l, j_l, rho_H + p_l, 2j_l, Tkk+ and Tkk-;
lapse derivative and curvature indicators;
shift derivative/current indicators;
radial metric derivative and curvature indicators;
angular metric derivative and curvature indicators;
time-derivative/extrinsic-curvature indicators;
cancellation ratios for radial-null contractions.
```

This is the right next step for deciding whether Stage I can honestly be called a robustly optimized, hard-bounded active-rail architecture, or whether the current architecture has simply reached the edge of its naive radial-support family.

## Verification

```text
python -m py_compile adm_harness/source_ledger.py scripts/run_source_ledger.py scripts/run_radial_support_screen.py
python -m unittest tests.test_validation_ladder_hardening
```

Result:

```text
Ran 18 tests
OK
```
