# Stage I Smooth Split-Family Ansatz Progress

## Purpose

This pass consolidated the successful split-carve/null-cushion family into a smoother, structured harness family.

The goal was not to add another broad knob cloud. The goal was to preserve the useful piecewise split behavior while making the design easier to reason about:

```text
soft live-entry containment,
separate catch/rematch containment,
small trailing-edge annular sleeve,
local annular null cushion,
explicit composition rule,
and a shared screen runner for reference, bracket, and confirmation passes.
```

The key question was whether the recent gains were just moving burden around, or whether the split family had exposed a coherent design direction.

## Harness Update

The source ledger now includes an optional smooth split-family packet profile:

```text
standing_support_packet_smooth_split_enabled
standing_support_packet_smooth_split_entry_carve
standing_support_packet_smooth_split_catch_carve
standing_support_packet_smooth_split_edge_carve
standing_support_packet_smooth_split_entry_radius_multiplier
standing_support_packet_smooth_split_entry_width_multiplier
standing_support_packet_smooth_split_catch_radius_multiplier
standing_support_packet_smooth_split_catch_width_multiplier
standing_support_packet_smooth_split_edge_inner_radius_multiplier
standing_support_packet_smooth_split_edge_outer_radius_multiplier
standing_support_packet_smooth_split_edge_width_multiplier
standing_support_packet_smooth_split_entry_schedule
standing_support_packet_smooth_split_catch_schedule
standing_support_packet_smooth_split_edge_schedule
standing_support_packet_smooth_split_temporal_profile
standing_support_packet_smooth_split_temporal_width_multiplier
standing_support_packet_smooth_split_composition
standing_support_packet_smooth_split_null_cushion_log_gain
```

The profile records its diagnostic windows:

```text
standing_support_packet_smooth_split_entry_window
standing_support_packet_smooth_split_catch_window
standing_support_packet_smooth_split_edge_window
standing_support_packet_smooth_split_containment_window
standing_support_packet_smooth_split_null_cushion_window
standing_support_packet_smooth_split_null_cushion_factor
standing_support_packet_smooth_split_null_cushion_delta_alpha
standing_support_packet_smooth_split_containment_window_slope_abs
standing_support_packet_smooth_split_edge_window_slope_abs
standing_support_packet_smooth_split_null_cushion_window_slope_abs
```

The composition selector is important:

```text
smooth_union
additive
```

The first naive smooth-union consolidation was too blunt. It removed useful overlap between the entry/catch/shoulder pieces and raised the integrated live radial burden. The additive mode preserves the overlap/cancellation structure that the piecewise split family had discovered.

New screen runner:

```text
toolkit/adm_harness_cli/scripts/run_smooth_split_screen.py
```

It compares:

```text
current
split_ref
coupled-edge diagnostic cases
smooth split-family cases
edge-sleeve brackets
null-cushion brackets
```

## Wiring Correction

During the first smooth split pass, the `additive` composition selector was only applied at the outer packet-carve stack. The smooth split profile's internal entry/catch/edge composition was still using `smooth_union`.

That made the "additive" cases under-carve relative to the actual split reference and falsely suggested that the smooth family was intrinsically worse.

After the correction, the additive smooth reference exactly reproduces `split_ref` on the 31 x 55 screen:

```text
split_ref:
  live Tkk burden:      9.977489
  live p_l burden:      0.401310
  live j_l burden:      0.065932
  live pOmega burden:   1.908483
  Tkk point peak:       0.907802
  pOmega point peak:    0.216943

smooth_additive_ref:
  live Tkk burden:      9.977489
  live p_l burden:      0.401310
  live j_l burden:      0.065932
  live pOmega burden:   1.908483
  Tkk point peak:       0.907802
  pOmega point peak:    0.216943
```

This matters because the smooth split-family harness can now express the already-successful piecewise law without changing behavior. Future refinements can be made inside one coherent family rather than by adding more unrelated piecewise controls.

## Mechanism Readout

The focused comparison clarified why the stronger coupled-edge profile was attractive but not balanced.

The coupled edge profile improved:

```text
live Tkk
live j_l
live pOmega
Tkk point peak
pOmega point peak
```

but inflated integrated live `p_l`.

A live-row inspection showed that this was not primarily a `p_l` point-peak failure. It was an integrated `catch_rematch / packet_in_support` volume effect:

```text
split_ref catch_rematch / packet_in_support live p_l burden:
  0.200767

coupled_edge024 catch_rematch / packet_in_support live p_l burden:
  0.365156

smooth_additive_edge006 catch_rematch / packet_in_support live p_l burden:
  0.336188
```

So the failed behavior was not simply an edge derivative spike. It was a broader live support sleeve / packet-support overlap issue during catch/rematch. This explains why the pressure-rebate branch failed: restoring support in the same edge region preserves local support mass but worsens the wrong integrated structure.

## 31 x 55 Edge Bracket

Input context:

```text
toolkit/adm_harness_cli/runs/stage1_v5_two_feature_radial_current_ledger/
```

Output:

```text
toolkit/adm_harness_cli/runs/stage1_v5_smooth_split_edge_bracket_31x55/
```

The additive edge sleeve gives a clean one-parameter trade. Increasing the edge sleeve improves live `Tkk` and live `p_l`, while gradually giving back some `j_l`, `pOmega`, and pOmega point-peak relief.

```text
split_ref:
  packet failures:      0
  max packet norm live: -24.279848
  live Tkk burden:      9.977489
  live p_l burden:      0.401310
  live j_l burden:      0.065932
  live pOmega burden:   1.908483
  Tkk point peak:       0.907802
  pOmega point peak:    0.216943

smooth_additive_edge002:
  packet failures:      0
  max packet norm live: -24.002040
  live Tkk burden:      9.776282
  live p_l burden:      0.395442
  live j_l burden:      0.066501
  live pOmega burden:   1.922042
  Tkk point peak:       0.906940
  pOmega point peak:    0.226015

smooth_additive_edge004:
  packet failures:      0
  max packet norm live: -23.727410
  live Tkk burden:      9.585357
  live p_l burden:      0.389766
  live j_l burden:      0.067102
  live pOmega burden:   1.938318
  Tkk point peak:       0.905824
  pOmega point peak:    0.235464

smooth_additive_edge006:
  packet failures:      0
  max packet norm live: -23.455923
  live Tkk burden:      9.403277
  live p_l burden:      0.384276
  live j_l burden:      0.067730
  live pOmega burden:   1.958038
  Tkk point peak:       0.905116
  pOmega point peak:    0.245307

smooth_additive_edge008:
  packet failures:      0
  max packet norm live: -23.187542
  live Tkk burden:      9.227666
  live p_l burden:      0.378966
  live j_l burden:      0.068370
  live pOmega burden:   1.978972
  Tkk point peak:       0.905124
  pOmega point peak:    0.255559
```

This is a useful knob, not random burden motion. The trade is monotone and interpretable.

## 31 x 55 Null Bracket

Output:

```text
toolkit/adm_harness_cli/runs/stage1_v5_smooth_split_null_bracket_31x55/
```

The stronger local null cushion partly recovers pOmega at a fixed edge setting with very little radial penalty.

```text
smooth_additive_edge004_null_m003:
  live Tkk burden:      9.625510
  live p_l burden:      0.389676
  live j_l burden:      0.067021
  live pOmega burden:   1.949430
  Tkk point peak:       0.910331
  pOmega point peak:    0.236117

smooth_additive_edge004_null_m005:
  live Tkk burden:      9.585357
  live p_l burden:      0.389766
  live j_l burden:      0.067102
  live pOmega burden:   1.938318
  Tkk point peak:       0.905824
  pOmega point peak:    0.235464

smooth_additive_edge004_null_m007:
  live Tkk burden:      9.545529
  live p_l burden:      0.389857
  live j_l burden:      0.067183
  live pOmega burden:   1.927639
  Tkk point peak:       0.905093
  pOmega point peak:    0.234817
```

The conservative balanced candidate is:

```text
smooth_additive_edge002_null_m007
```

The more radial-relief-oriented candidate is:

```text
smooth_additive_edge004_null_m007
```

## 61 x 83 Confirmation

Output:

```text
toolkit/adm_harness_cli/runs/stage1_v5_smooth_split_selected_61x83/
```

The selected candidates were checked on a denser grid:

```text
split_ref:
  packet failures:      0
  max packet norm live: -24.273518
  live Tkk burden:      9.523620
  live p_l burden:      0.393498
  live j_l burden:      0.065130
  live pOmega burden:   1.914439
  Tkk point peak:       1.016302
  pOmega point peak:    0.216869

smooth_additive_edge002_null_m007:
  packet failures:      0
  max packet norm live: -23.941739
  live Tkk burden:      9.299443
  live p_l burden:      0.387771
  live j_l burden:      0.065796
  live pOmega burden:   1.916257
  Tkk point peak:       1.009476
  pOmega point peak:    0.224332

smooth_additive_edge004_null_m007:
  packet failures:      0
  max packet norm live: -23.666557
  live Tkk burden:      9.121695
  live p_l burden:      0.382413
  live j_l burden:      0.066402
  live pOmega burden:   1.930788
  Tkk point peak:       1.008351
  pOmega point peak:    0.232705
```

The confirmation preserves the 31 x 55 pattern:

```text
edge002_null_m007:
  smaller radial gain,
  almost no pOmega cost,
  cleaner balanced candidate.

edge004_null_m007:
  stronger live Tkk / p_l relief,
  modest pOmega and j_l cost,
  likely the better next high-resolution candidate.
```

## Interpretation

This is not just another whack-a-mole round.

The branch made three concrete gains:

```text
1. The successful piecewise split law can now be represented in a consolidated smooth-family interface.

2. The additive-overlap structure is confirmed as essential.
   Plain smooth-union loses the useful overlap/cancellation and raises live radial burden.

3. A small trailing-edge annular sleeve is a real one-parameter improvement direction.
   It lowers live Tkk and live p_l over split_ref while keeping packet safety and preserving point-peak control.
```

The remaining trade is also clear:

```text
more edge sleeve -> lower live Tkk / p_l
more edge sleeve -> slightly higher live j_l / pOmega and pOmega point peak
```

That is a usable engineering trade, not a random burden shuffle.

## Recommended Next Work

Use the smooth split family as the active branch for the next pass.

Recommended immediate checks:

```text
1. High-resolution V5 screen of:
   split_ref
   smooth_additive_edge002_null_m007
   smooth_additive_edge004_null_m007

2. Stage/region delta ledger for the selected smooth candidate versus split_ref,
   with special attention to catch_rematch / packet_in_support.

3. If the 81 x 109 pass holds, run a V2 diagnostic and a V5 cap/stress confirmation.
```

The likely active candidate is:

```text
smooth_additive_edge004_null_m007
```

The conservative fallback is:

```text
smooth_additive_edge002_null_m007
```

## Verification

Focused smooth/coupled regression:

```text
python -m pytest toolkit/adm_harness_cli/tests/test_validation_ladder_hardening.py -k "smooth_split or coupled_profile" -q
2 passed, 19 deselected
```

Full harness test suite from the CLI package root:

```text
cd toolkit/adm_harness_cli
python -m pytest tests -q
31 passed
```
