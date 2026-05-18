# Stage I Infrastructure Derivative-Smoothing Progress

## Purpose

This pass tested whether the V5 `blend` floor-union, trailing-edge width `1.6` candidate could be improved by smoothing or coordinating the infrastructure-side release/carve/lapse timing, without promoting the hard `max` floor union back into the main design.

Target hierarchy:

```text
V5 remains the active engineering target.
V2 remains a diagnostic scale.
V10 remains an edge/later hardening target.
```

## Harness Change

The harness now exposes temporal-edge profile controls for packet-local infrastructure windows:

```text
standing_support_packet_exclusion_temporal_profile
standing_support_packet_exclusion_shoulder_temporal_profile
standing_support_packet_lapse_temporal_profile
standing_support_packet_beta_rematch_temporal_profile
```

Allowed profile values are:

```text
tanh
minimum_jerk / minjerk / smoothstep5
smoothstep7
```

The default is still `tanh`, preserving existing behavior unless a profile is explicitly selected. The new controls are wired through:

```text
toolkit/adm_harness_cli/adm_harness/source_ledger.py
toolkit/adm_harness_cli/scripts/run_source_ledger.py
toolkit/adm_harness_cli/scripts/run_source_overlay_sweep.py
toolkit/adm_harness_cli/tests/test_validation_ladder_hardening.py
toolkit/adm_harness_cli/README.md
```

## Runs

Main local run outputs:

```text
toolkit/adm_harness_cli/runs/stage1_v5_infra_derivative_smoothing_screen/
toolkit/adm_harness_cli/runs/stage1_v5_infra_coordinated_release_screen/
toolkit/adm_harness_cli/runs/stage1_v5_blend_width16_highres_current_code/
toolkit/adm_harness_cli/runs/stage1_v5_infra_coordinated_lapse_highres/
```

The first screen held the current V5 candidate fixed and varied temporal-edge profiles and hard-`max` comparator rows.

```text
cases: 64
execution failures: 0
```

The second screen varied coordinated-release schedules for carve, shoulder, and lapse.

```text
cases: 72
execution failures: 0
```

## Screen Results

The plain temporal-edge smoothing screen did not improve the current candidate. All rows remained packet-safe, but the best rows were the existing `tanh` timing:

```text
floor mode = blend
release profile = minimum_jerk
carve schedule = live_only
shoulder schedule = live_only
lapse schedule = entry_catch_release
carve temporal profile = tanh
lapse temporal profile = tanh

positive packet-norm live points = 0
top hard-channel live packet points = 0
max packet norm live = -5.473217
live Tkk fraction = 0.023960
live p_l fraction = 0.007027
max total burden ratio = 2.037524
max point peak ratio = 8.748470
```

The hard-`max` comparator remained worse on point peak:

```text
best hard-max comparator point peak ratio = 32.652456
```

The coordinated-release screen was more informative. Coordinated carve release is not a good path. When carve and/or carve shoulder are coordinated with release, live source fractions worsen sharply even though packet-norm safety still holds. This suggests the carve field is part of the packet/support separation geometry, not merely a cleanup field to be faded with release.

Coordinated lapse release did produce a useful diagnostic signal. With carve and shoulder left `live_only`, and lapse switched to `coordinated_release`, the screen found:

```text
positive packet-norm live points = 0
top hard-channel live packet points = 0
max packet norm live = about -3.55 to -3.87
live Tkk fraction = about 0.0161 to 0.0165
live p_l fraction = about 0.00875
max total burden ratio = about 2.47 to 2.50
max point peak ratio = 8.234451
```

So coordinated lapse reduces live radial-null burden and point peak, but it does not give a cleaner overall V5 law because it raises live radial pressure and total burden.

## Higher-Resolution Check

A fresh high-resolution baseline and coordinated-lapse check were run at `81 x 109`.

Current `blend + trailing-edge width 1.6` baseline:

```text
positive packet-norm live points = 0
max packet norm live = -5.455516
live Tkk fraction = 0.024255
live p_l fraction = 0.006986
raw max point peak = 1.343064
max release_profile_slope_abs = 10.415634, release_shift_fade / outer_quarantine_shell / not live
max carve_window_slope_abs = 6.034293, catch_rematch / core_throat / not live
max lapse_window_slope_abs = 5.613969, catch_rematch / core_throat / not live
max beta_rematch_window_slope_abs = 5.545130, held_carry / core_throat / not live
```

Coordinated-lapse diagnostic, with lapse lag `0.5` and carve/shoulder still `live_only`:

```text
positive packet-norm live points = 0
max packet norm live = -3.860307
live Tkk fraction = 0.016849
live p_l fraction = 0.008749
raw max point peak = 1.146274
max release_profile_slope_abs = 10.415634, release_shift_fade / outer_quarantine_shell / not live
max carve_window_slope_abs = 6.034293, catch_rematch / core_throat / not live
max lapse_window_slope_abs = 10.211907, post_release_buffer / packet_in_support / live
max beta_rematch_window_slope_abs = 5.545130, held_carry / core_throat / not live
```

This confirms the screen-level interpretation. Coordinated lapse can reduce the radial-null channel, but it does so by introducing a live lapse-derivative burden and worsening live radial pressure.

## Interpretation

Do not refreeze around coordinated release.

Keep the current main V5 candidate:

```text
standing_support_packet_beta_rematch_floor_mode = blend
standing_support_packet_beta_rematch_shape = trailing_edge
standing_support_packet_beta_rematch_width_multiplier = 1.6
standing_support_packet_beta_rematch_schedule = live_only
standing_support_packet_exclusion_schedule = live_only
standing_support_packet_exclusion_shoulder_schedule = live_only
standing_support_packet_lapse_schedule = entry_catch_release
```

The coordinated carve failure is useful evidence: carve appears to preserve packet/support separation during transport and catch. Moving it into coordinated release damages the live sleeve.

The coordinated lapse result is also useful, but as a diagnostic. It shows that lapse can trim the radial-null channel, but the full coordinated-release implementation is too broad or too steep and must be constrained against live `p_l` and live lapse-window derivative spikes.

## Recommended Next Work

Build a focused channel-cause ledger rather than another broad sweep.

For each selected top bad point, record:

```text
rho_H
p_l
j_l
rho_H + p_l
2 j_l
Tkk plus/minus projections
```

and local derivative-origin diagnostics such as:

```text
d_s alpha
d_l alpha
d_l^2 alpha
d_s beta^l
d_l beta^l
d_l^2 beta^l
d_s gamma_ll
d_l gamma_ll
d_s gamma_Omega
d_l gamma_Omega
```

The goal is to classify top bad points as beta-gradient dominated, lapse-curvature dominated, radial-metric dominated, angular-capacity dominated, or cancellation dominated. After that, test a weaker local lapse/null-channel trim aimed at the offending catch/rematch infrastructure region, not a full lapse release driver.

## Verification

```text
python -m py_compile adm_harness/source_ledger.py scripts/run_source_ledger.py scripts/run_source_overlay_sweep.py
python -m unittest discover -s tests
```

Result:

```text
Ran 26 tests in 1.291s
OK
```
