# Stage I Refined Radial Support Law Progress

## Purpose

The channel-cause ledger indicated that the remaining V5 branch damage is dominated by radial-metric geometry rather than beta-gradient or broad lapse-release behavior. This pass tested whether a more explicit packet/support-local `gamma_ll` radial support law could improve the current V5 refreeze without abandoning the `blend + trailing-edge width 1.6` base.

The active target remains:

```text
V5 primary target
V2 diagnostic scale
V10 later stress target
```

This pass was not a report-grade final refreeze. It was a focused design iteration to see whether the radial support law has a real improvement surface.

## Harness Change

The harness now exposes packet/support-local radial metric factors on `gamma_ll`:

```text
standing_support_packet_radial_log_gain
standing_support_packet_radial_radius_multiplier
standing_support_packet_radial_width_multiplier
standing_support_packet_radial_schedule
standing_support_packet_radial_temporal_profile

standing_support_packet_radial_shoulder_log_gain
standing_support_packet_radial_shoulder_mode
standing_support_packet_radial_shoulder_radius_multiplier
standing_support_packet_radial_shoulder_width_multiplier
standing_support_packet_radial_shoulder_schedule
standing_support_packet_radial_shoulder_temporal_profile
```

The core window is a filled packet/support-local radial metric factor. The shoulder window can be `filled` or `annular`. The combined factor multiplies `gamma_ll`:

```text
gamma_ll = gamma_ll_base
         * support_shell_rail_stretch_factor
         * standing_support_packet_radial_factor
```

The ledger records:

```text
standing_support_packet_radial_window
standing_support_packet_radial_shoulder_window
standing_support_packet_radial_factor
standing_support_packet_delta_gamma_ll
standing_support_packet_radial_window_slope_abs
```

A `catch_only` temporal schedule was also added for packet-local windows. It restricts a window to the catch/rematch interval:

```text
x_catch_packet - 2 catch_width <= s <= x_catch_packet + 2 catch_width
```

The new focused runner is:

```text
toolkit/adm_harness_cli/scripts/run_radial_support_screen.py
```

It consumes an existing source-ledger run directory, writes each candidate row incrementally, and records top bad points for each candidate.

## Runs

Main local run outputs:

```text
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_quick_screen/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_quick_screen_shoulders/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_quick_screen_positive/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_candidate_41x73/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_candidate_81x109/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_ring_41x73/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_combo_41x73/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_combo_81x109/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_balance_41x73/
toolkit/adm_harness_cli/runs/stage1_v5_radial_support_law_balance_81x109/
```

The high-resolution comparison used `81 x 109` grids through the current code path.

## Design Findings

The first important sign result was directional:

```text
negative radial softening was not the right direction;
positive radial stretch was the useful direction.
```

Mild negative core/shoulder changes could slightly reduce one live fraction, but they worsened Tkk peak and angular burden. Positive core stretch reduced hard Tkk and angular pressure peaks while preserving packet-norm safety.

The second important result was compositional:

```text
filled positive radial core stretch gives peak relief;
catch-only outer annular radial stretch improves live-fraction behavior;
the two together are cleaner than either mechanism alone.
```

This is the first clear sign that the radial support law is acting like a design surface rather than another single blunt knob.

## High-Resolution Results

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

core +0.05:
  packet failures:      0
  max packet norm live: -21.612777
  live Tkk fraction:    0.020193426
  live p_l fraction:    0.006523472
  live j_l fraction:    0.129734682
  live pOmega fraction: 0.304114337
  Tkk point peak:       1.293786741
  pOmega point peak:    0.229600610

core +0.05, catch-only ring +0.08:
  packet failures:      0
  max packet norm live: -21.612436
  live Tkk fraction:    0.020143383
  live p_l fraction:    0.006484900
  live j_l fraction:    0.129939955
  live pOmega fraction: 0.302194949
  Tkk point peak:       1.285178196
  pOmega point peak:    0.228139190

core +0.05, catch-only ring +0.12:
  packet failures:      0
  max packet norm live: -21.612436
  live Tkk fraction:    0.020104230
  live p_l fraction:    0.006459793
  live j_l fraction:    0.129967672
  live pOmega fraction: 0.301790206
  Tkk point peak:       1.285178196
  pOmega point peak:    0.228139190

core +0.06, catch-only ring +0.12:
  packet failures:      0
  max packet norm live: -21.611110
  live Tkk fraction:    0.020097811
  live p_l fraction:    0.006492325
  live j_l fraction:    0.129887663
  live pOmega fraction: 0.300462196
  Tkk point peak:       1.274993859
  pOmega point peak:    0.225474065
```

Relative to base, the balanced candidate:

```text
core +0.05, catch-only ring +0.12
```

gives:

```text
live Tkk fraction:     lower by 0.000137329
live p_l fraction:     higher by 0.000087131
live j_l fraction:     lower by 0.000316023
live pOmega fraction:  lower by 0.007794751
Tkk point peak:        0.961009 x base
pOmega point peak:     0.943315 x base
packet failures:       0
```

The aggressive comparator:

```text
core +0.06, catch-only ring +0.12
```

gives stronger peak relief:

```text
Tkk point peak:        0.953393 x base
pOmega point peak:     0.932295 x base
```

but spends more live `p_l`, so it should remain a comparator rather than the balanced candidate.

## Interpretation

This is real progress, but not a final hard-bound solution.

The branch improved almost every active channel that motivated the radial support work:

```text
zero packet-norm failures preserved;
live radial-null fraction improved;
live radial current fraction improved;
live angular pressure fraction improved;
Tkk point peak improved;
pOmega point peak improved.
```

The remaining cost is a small increase in live `p_l` fraction. The catch-only annular ring reduced that cost compared with filled core-only stretch, which supports the design interpretation that the filled core and outer ring are doing different jobs.

The large `max_any_point_peak` remains dominated by an outer-quarantine `neg_rho_packet` artifact and is not yet addressed by this radial packet/support law. This report therefore does not claim that the whole point-peak landscape is solved. It claims that the previously identified radial-metric mechanism is now responding in the right direction.

The top bad-point regions remain structurally stable:

```text
neg_Tkk_radial: catch_rematch / core_throat
abs_p_l:        catch_rematch / core_throat
abs_j_l:        catch_rematch / packet_in_support
abs_pOmega:     catch_rematch / packet_in_support
```

That stability is useful: the refinement reduces magnitudes without merely moving the bad points into a new live region.

## Current Candidate

Balanced candidate for continued refinement:

```text
standing_support_packet_radial_log_gain = +0.05
standing_support_packet_radial_radius_multiplier = 1.3
standing_support_packet_radial_width_multiplier = 1.8
standing_support_packet_radial_schedule = entry_catch_release

standing_support_packet_radial_shoulder_log_gain = +0.12
standing_support_packet_radial_shoulder_mode = annular
standing_support_packet_radial_shoulder_radius_multiplier = 2.2
standing_support_packet_radial_shoulder_width_multiplier = 2.8
standing_support_packet_radial_shoulder_schedule = catch_only
```

Aggressive comparator:

```text
standing_support_packet_radial_log_gain = +0.06
standing_support_packet_radial_shoulder_log_gain = +0.12
```

with the same footprints and schedules.

## Recommended Next Work

Do not jump back to broad release/lapse sweeps.

Next refinement should tune geometry, not just gain:

```text
1. Tune ring radius and width around the balanced candidate.
2. Try to reduce live p_l cost while preserving Tkk and pOmega peak relief.
3. Compare balanced and aggressive candidates at V5 first.
4. Only after the V5 radial law stabilizes, run V10 as an edge/stress check.
5. Use lapse only as a small local null-channel trim after radial geometry is stable.
```

The most likely useful next axes are:

```text
ring radius multiplier: 2.0, 2.2, 2.4
ring width multiplier:  2.4, 2.8, 3.2
core gain:             0.04, 0.05, 0.06
ring gain:             0.10, 0.12, 0.14
```

The gate for the next pass should be:

```text
zero packet-norm failures;
Tkk point peak stays below the balanced candidate or close to it;
pOmega point peak stays below the balanced candidate or close to it;
live p_l fraction moves closer to base than the balanced candidate;
bad points do not migrate into a new live release/post-release region.
```

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
