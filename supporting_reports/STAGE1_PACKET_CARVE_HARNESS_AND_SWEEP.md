# Stage I Packet-Carve Harness Improvement And First Sweep

## Purpose

After the Stage I-B gate failed, the next question was whether the harness could directly target the observed cause: hard-channel burden inside `packet_in_support`. The earlier overlay objective was mostly a source-delta ranking. It could improve the support-shell actuator while missing the live-packet burden that mattered for minimal traversability.

This update adds two harness capabilities:

```text
1. worldtube exposure metrics in source overlay sweeps
2. an experimental standing-support packet carve-out knob
```

The carve-out is not a final design. It is a diagnostic branch that tests whether reducing the standing support bump under the live packet tube actually moves the hard-channel burdens.

## Code Changes

Updated:

```text
toolkit/adm_harness_cli/adm_harness/source_ledger.py
toolkit/adm_harness_cli/scripts/run_source_ledger.py
toolkit/adm_harness_cli/scripts/run_source_overlay_sweep.py
```

New source-ledger fields:

```text
W_raw
standing_support_packet_carve_window
standing_support_packet_carve_factor
W
```

Here `W` is the effective support bump after carving, while `W_raw` preserves the original standing support bump.

New experimental parameters:

```text
standing_support_packet_exclusion
standing_support_packet_exclusion_radius_multiplier
standing_support_packet_exclusion_width_multiplier
standing_support_packet_exclusion_schedule
```

New overlay-sweep readouts include:

```text
worldtube_exposure_score
neg_Tkk_radial_live_packet_fraction_absolute
abs_p_l_live_packet_fraction_absolute
neg_Tkk_radial_packet_in_support_fraction
abs_p_l_packet_in_support_fraction
top_hard_channels_in_live_packet
live_packet_active_shell_points
```

The sweep now writes:

```text
source_overlay_sweep_worldtube_ranking.csv
```

## Validation

The existing tests pass:

```text
pytest -q tests/test_validation_ladder_hardening.py tests/test_service_synthesis_validation.py
25 passed
```

A tiny carved source-ledger smoke run also completed:

```text
toolkit/adm_harness_cli/runs/stage1_carve_tiny_smoke/
```

## First V5 Carve Sweep

Smoke sweep:

```text
toolkit/adm_harness_cli/runs/stage1_v5_packet_carve_smoke/
```

High-resolution focused slice:

```text
toolkit/adm_harness_cli/runs/stage1_v5_packet_carve_highres_slice/
```

Focused selected-carve point ledger and worldtube report:

```text
toolkit/adm_harness_cli/runs/stage1_v5_packet_carve_selected_ledger/
toolkit/adm_harness_cli/runs/stage1_v5_packet_carve_minimal_traversability_report/
```

The high-resolution V5 slice used:

```text
variant:          tuned_w0569_eta200
service factor:   V = 5
grid:             ns = 53, nl = 73
shell amplitude:  +0.5
catch lead:       1.55
temporal width:   0.30
clock ratio:      0.375
carve schedule:   live_only
carve radius:     1.0
carve width:      1.0
carve strengths:  0.0, 0.12, 0.16, 0.20, 0.24
```

Results:

| carve strength | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 0 | 0.221837 | 0.261006 | 1 | 1.054489 |
| 0.12 | 0 | 0.107606 | 0.169186 | 0 | 1.070796 |
| 0.16 | 0 | 0.087072 | 0.144818 | 0 | 1.079520 |
| 0.20 | 0 | 0.072283 | 0.123389 | 0 | 1.089866 |
| 0.24 | 1 | 0.061485 | 0.104700 | 0 | 1.102152 |

The `0.20` carve is the best V5 diagnostic point in this slice. It removes top hard-channel points from the live packet and cuts live hard-channel fractions substantially:

```text
neg_Tkk_radial live fraction: 0.221837 -> 0.072283
abs_p_l live fraction:       0.261006 -> 0.123389
```

But it still does not pass the strict minimal-traversability rule, because the max live packet fraction remains percent-level:

```text
minimal_traversability_status: fail
reason: live packet carries percent-level burden
```

## V10 Carve Check

Focused V10 slice:

```text
toolkit/adm_harness_cli/runs/stage1_v10_packet_carve_highres_slice/
```

Focused selected-carve point ledger and report:

```text
toolkit/adm_harness_cli/runs/stage1_v10_packet_carve_selected_ledger/
toolkit/adm_harness_cli/runs/stage1_v10_packet_carve_minimal_traversability_report/
```

Results:

| carve strength | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 3 | 0.307266 | 0.261007 | 1 | 1.054417 |
| 0.05 | 11 | 0.224027 | 0.219307 | 0 | 1.058839 |
| 0.08 | 20 | 0.182660 | 0.196642 | 0 | 1.063247 |
| 0.10 | 80 | 0.158769 | 0.182522 | 0 | 1.066677 |
| 0.12 | 135 | 0.137813 | 0.169187 | 0 | 1.070411 |
| 0.16 | 162 | 0.103780 | 0.144819 | 0 | 1.079049 |

The V10 interpretation is important: carving improves source placement but consumes causal margin. Every nonzero V10 carve tested here worsened packet-norm safety relative to the already-failing uncarved V10 candidate.

## Interpretation

This is a useful redesign signal.

The Stage I-B diagnosis was correct: the hard-channel packet burden was caused by standing packet/support substrate overlap, not by the support-shell overlay. The carve-out directly attacks that overlap and immediately moves the top hard-channel points out of the live packet at V5.

However, the carve-out also weakens the support/lapse structure under the packet. At V5 there is a useful but narrow band around `0.16` to `0.20`. At V10, the same idea worsens packet-norm safety. That means the next design cannot simply remove standing support under the packet. It needs compensation.

## Recommended Next Sweep

The next sweep should combine packet carving with a causal-margin compensator. Keep the V5/V10 split explicit.

Suggested V5 grid:

```text
standing_support_packet_exclusions: 0.12, 0.16, 0.20, 0.22
standing_support_packet_exclusion_radius_multipliers: 0.8, 1.0, 1.2
standing_support_packet_exclusion_width_multipliers: 0.75, 1.0, 1.5
standing_support_packet_exclusion_schedules: live_only
clock_lapse_ratios: 0.375, 0.5, 0.75
rail_stretch_ratios: 0.0
throat_capacity_ratios: 0.0
```

Then run V10 only on the V5-safe carve/clock candidates. The V10 goal should be:

```text
positive_packet_norm_live = 0
top_hard_channels_in_live_packet = 0
live Tkk fraction materially below the uncarved candidate
live p_l fraction materially below the uncarved candidate
```

Do not proceed to Stage II from the current carved candidate yet. It is a promising Stage I redesign direction, not a finished metric-side target.
