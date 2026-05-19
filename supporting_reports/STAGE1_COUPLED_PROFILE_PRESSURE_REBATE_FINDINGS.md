# Stage I Coupled Profile and Pressure-Rebate Findings

## Purpose

This pass tested whether the successful split-carve/null-cushion behavior could be consolidated into a more coherent coupled packet-support profile.

The motivating hypothesis was:

```text
The piecewise split family may be approximating a pressure-preserving coupled support law:
  soften/remove support where the packet edge creates point stress,
  keep enough support to avoid integrated Tkk / p_l tax,
  trim the exposed null channel locally,
  and avoid turning lapse into the main release driver.
```

The test was intentionally focused. It did not try to find a final smooth ansatz. It asked whether a first coupled edge profile, with and without an explicit support rebate, points toward the right conservation/redistribution structure.

## Harness Update

The source ledger now includes an optional coupled packet profile:

```text
standing_support_packet_coupled_profile_enabled
standing_support_packet_coupled_entry_carve
standing_support_packet_coupled_catch_carve
standing_support_packet_coupled_edge_carve
standing_support_packet_coupled_radius_multiplier
standing_support_packet_coupled_width_multiplier
standing_support_packet_coupled_entry_schedule
standing_support_packet_coupled_catch_schedule
standing_support_packet_coupled_temporal_profile
standing_support_packet_coupled_edge_inner_radius_multiplier
standing_support_packet_coupled_edge_outer_radius_multiplier
standing_support_packet_coupled_edge_width_multiplier
standing_support_packet_coupled_rebate_fraction
standing_support_packet_coupled_radial_log_gain
standing_support_packet_coupled_null_cushion_log_gain
```

The coupled profile records separate diagnostic windows and deltas:

```text
standing_support_packet_coupled_entry_window
standing_support_packet_coupled_catch_window
standing_support_packet_coupled_containment_window
standing_support_packet_coupled_edge_window
standing_support_packet_coupled_rebate_window
standing_support_packet_coupled_radial_window
standing_support_packet_coupled_null_cushion_window
standing_support_packet_raw_carve_contribution
standing_support_packet_coupled_rebate_contribution
standing_support_packet_coupled_null_cushion_delta_alpha
standing_support_packet_coupled_delta_gamma_ll
```

The important semantic distinction is:

```text
standing_support_packet_raw_carve_contribution
  pre-rebate carve amount

standing_support_packet_coupled_rebate_contribution
  bounded edge-local support restoration

standing_support_packet_carve_contribution
  effective carve actually applied to W
```

A new screen runner was added:

```text
toolkit/adm_harness_cli/scripts/run_coupled_profile_screen.py
```

It uses the shared source-screening infrastructure and compares current, split-piecewise, coupled-edge, and pressure-rebate candidates on the same source-channel summary metrics.

## V5 Focused Screen

Input context:

```text
toolkit/adm_harness_cli/runs/stage1_v5_two_feature_radial_current_ledger/
```

Primary output:

```text
toolkit/adm_harness_cli/runs/stage1_v5_pressure_preserving_profile_31x55/
```

Control output:

```text
toolkit/adm_harness_cli/runs/stage1_v5_pressure_preserving_controls_31x55/
```

Grid:

```text
31 x 55
```

The main comparison was:

```text
current
split_ref
coupled edge carve without rebate
coupled edge carve with 25% edge-local support rebate
coupled edge carve with 50% edge-local support rebate
```

Summary:

```text
current:
  packet failures:      0
  live Tkk burden:      10.149576
  live p_l burden:      0.410096
  live j_l burden:      0.123456
  live pOmega burden:   2.668905
  Tkk point peak:       1.227705
  pOmega point peak:    0.543241

split_ref:
  packet failures:      0
  live Tkk burden:      10.096127
  live p_l burden:      0.399238
  live j_l burden:      0.067590
  live pOmega burden:   1.920342
  Tkk point peak:       0.928407
  pOmega point peak:    0.218660

coupled_edgecarve024_keep_radial:
  packet failures:      0
  live Tkk burden:      11.284369
  live p_l burden:      0.610231
  live j_l burden:      0.039035
  live pOmega burden:   0.907949
  Tkk point peak:       0.822397
  pOmega point peak:    0.082385

pressure_edge018_rebate025_keep_radial:
  packet failures:      0
  live Tkk burden:      17.496011
  live p_l burden:      0.844502
  live j_l burden:      0.037408
  live pOmega burden:   0.936030
  Tkk point peak:       1.391364
  pOmega point peak:    0.102577

pressure_edge024_rebate025_keep_radial:
  packet failures:      0
  live Tkk burden:      16.388524
  live p_l burden:      0.816202
  live j_l burden:      0.037283
  live pOmega burden:   0.916201
  Tkk point peak:       0.963404
  pOmega point peak:    0.094963

pressure_edge024_rebate050_keep_radial:
  packet failures:      0
  live Tkk burden:      24.967464
  live p_l burden:      1.119394
  live j_l burden:      0.035218
  live pOmega burden:   0.916429
  Tkk point peak:       4.193088
  pOmega point peak:    0.118413
```

## Interpretation

The coupled edge profile has a real signal, but not a complete design.

Without rebate, the `edge 0.24` coupled profile strongly reduces the angular/current channels and point peaks:

```text
live j_l:      0.123456 -> 0.039035
live pOmega:   2.668905 -> 0.907949
Tkk peak:      1.227705 -> 0.822397
pOmega peak:   0.543241 -> 0.082385
```

But it pays a large live radial cost:

```text
live Tkk:      10.149576 -> 11.284369
live p_l:      0.410096 -> 0.610231
```

That trade-off is not a numerical accident. It repeated across the coupled-edge variants.

The pressure-preserving rebate tested here is not the missing principle. Restoring support in the same packet-edge region worsened the radial channels sharply. At 25% rebate, live `Tkk` rose into the `16-17` range. At 50% rebate, the point peak failed badly:

```text
Tkk point peak: 4.193088
```

This means the useful conservation structure is not:

```text
remove support at the edge, then add some of it back at the edge.
```

That operation preserves a local amount of support, but not the relevant derivative/cancellation structure. It appears to reintroduce support exactly where the edge handoff is most derivative-sensitive.

## What This Says About Direction

The last few rounds have enough signal to stop doing broad whack-a-mole screens.

The stable facts are:

```text
1. The split-carve/null-cushion family is not random luck.
   It preserves packet safety and gives major point-peak, current, and angular-pressure relief.

2. The coupled edge family identifies a real packet-edge lever.
   It can strongly reduce j_l, pOmega, and point peaks.

3. The naive pressure rebate is the wrong pressure-preservation idea.
   It restores support in a way that worsens Tkk / p_l and can destroy point-peak control.

4. The next law should preserve derivative/cancellation structure, not local support mass.
```

The next design should therefore be a smoothed ansatz built from the successful piecewise split family, rather than a new arbitrary coupled profile.

The target shape family should consolidate:

```text
soft early/live-entry containment,
separate softer catch/rematch containment,
trailing-edge annular sleeve only where it relieves point peaks,
small local null cushion as a trim,
smooth joins with derivative control,
no edge-local support rebate unless a channel-cause ledger proves that it belongs somewhere else.
```

In plain terms: the piecewise knobs have taught us a geometry. The next step is not to add more independent knobs. It is to turn that geometry into fewer, smoother, more coherent knobs that encode the same separation.

## Recommended Next Work

Build a smoothed split-family ansatz with a small number of structured controls:

```text
smooth_split_profile_enabled
smooth_split_entry_carve
smooth_split_catch_carve
smooth_split_edge_carve
smooth_split_edge_inner_radius_multiplier
smooth_split_edge_outer_radius_multiplier
smooth_split_edge_width_multiplier
smooth_split_null_cushion_log_gain
smooth_split_join_profile
smooth_split_join_width_multiplier
```

The first version should stay close to the successful split reference. It should replace abrupt piecewise composition with smooth-union and derivative-controlled transitions, but it should not change the conceptual placement yet.

Initial screen should compare:

```text
current
split_ref
coupled_edgecarve024_keep_radial
smooth_split_reference_like
smooth_split_edge_soft
smooth_split_join_wide
```

The decision criterion is not only whether the smooth ansatz beats `split_ref`; the first question is whether it preserves the split-family gains without the pressure-rebate failure mode. If it does, this branch becomes a serious Stage I consolidation path.

## Verification

Focused coupled-profile regression:

```text
python -m pytest toolkit/adm_harness_cli/tests/test_validation_ladder_hardening.py -k coupled_profile -q
1 passed, 19 deselected
```

Full harness test suite from the CLI package root:

```text
cd toolkit/adm_harness_cli
python -m pytest tests -q
30 passed
```
