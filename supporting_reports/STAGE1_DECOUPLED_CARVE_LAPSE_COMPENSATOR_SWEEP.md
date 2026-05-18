# Stage I Decoupled Carve/Lapse Compensator Sweep

## Purpose

The first carve-plus-lapse compensator used the same packet-local window for both operations:

```text
standing support carve:  W -> W * (1 - carve * packet_window)
packet lapse boost:      alpha -> alpha * exp(lapse_gain * packet_window)
```

That rescued V10 packet-norm safety, but it also partially restored radial-null burden in the live packet. This sweep decoupled the packet-lapse footprint from the standing-support carve footprint so the harness could test whether causal margin can be restored with a wider/softer lapse shoulder.

This remains a demanded-source placement screen, not a matter-source model.

## Harness Change

The working tree now exposes separate packet-lapse window controls:

```text
standing_support_packet_lapse_log_gain
standing_support_packet_lapse_radius_multiplier
standing_support_packet_lapse_width_multiplier
standing_support_packet_lapse_schedule
standing_support_packet_lapse_window
```

The carve controls remain separate:

```text
standing_support_packet_exclusion
standing_support_packet_exclusion_radius_multiplier
standing_support_packet_exclusion_width_multiplier
standing_support_packet_exclusion_schedule
```

The overlay sweep CLI now accepts:

```text
--standing-support-packet-lapse-log-gains
--standing-support-packet-lapse-radius-multipliers
--standing-support-packet-lapse-width-multipliers
--standing-support-packet-lapse-schedules
```

The focused ledger CLI accepts the singular forms of the same lapse controls.

## Validation

The existing targeted test set still passes:

```text
pytest -q tests/test_validation_ladder_hardening.py tests/test_service_synthesis_validation.py
25 passed
```

## V10 Shape Sweep

Run directories:

```text
toolkit/adm_harness_cli/runs/stage1_v10_decoupled_carve_lapse_smoke/
toolkit/adm_harness_cli/runs/stage1_v10_decoupled_carve_lapse_highres/
toolkit/adm_harness_cli/runs/stage1_v10_decoupled_carve_lapse_width_check/
```

High-resolution grid:

```text
variant:              tuned_w0569_eta200
service factor:       V = 10
support shell:        a_beta = +0.5, lead = 1.55, width = 0.30
clock-lapse ratio:    0.375
carve strengths:      0.12, 0.14, 0.16
carve radius/width:   1.0, 1.0
packet lapse gains:   0.55, 0.65, 0.75
lapse radii:          1.1, 1.2, 1.3, 1.4
lapse widths:         0.5, 0.8, 1.2
grid:                 ns = 53, nl = 73
```

The high-resolution V10 sweep found a real safe family: 103 of 108 cases had no positive live packet norm and no top hard-channel point in the live packet.

Best low-peak/high-placement candidate from the sweep:

| carve | lapse gain | lapse radius | lapse width | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.16 | 0.55 | 1.4 | 1.2 | 0 | 0.159660 | 0.144818 | 0 | 1.072897 | 1.015240 |

A width follow-up found that broadening the lapse transition to `1.6` preserved V10 safety and slightly improved global burden:

| V | carve | lapse gain | lapse radius | lapse width | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0.16 | 0.55 | 1.4 | 1.6 | 0 | 0.159615 | 0.144818 | 0 | 1.069684 | 1.015240 |

Widths `2.0` and `2.5` failed the V10 packet-norm gate, so the selected decoupled candidate uses width `1.6`.

## V5 Back-Check

Run directories:

```text
toolkit/adm_harness_cli/runs/stage1_v5_decoupled_carve_lapse_selected_check/
toolkit/adm_harness_cli/runs/stage1_v5_decoupled_carve_lapse_tradeoff/
toolkit/adm_harness_cli/runs/stage1_v5_decoupled_carve_lapse_width_check/
```

Selected decoupled candidate:

```text
standing_support_packet_exclusion = 0.16
standing_support_packet_lapse_log_gain = 0.55
standing_support_packet_lapse_radius_multiplier = 1.4
standing_support_packet_lapse_width_multiplier = 1.6
schedule = live_only for both carve and lapse
```

V5 selected-candidate check:

| V | packet failures | max packet norm live | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio | max point peak ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0 | -302.944082 | 0.140270 | 0.144818 | 0 | 1.070626 | 2.077538 |

The V5 point-peak cost is higher than V10, but the packet-worldtube placement is materially cleaner than the uncarved selected candidate.

## Focused Worldtube Reports

Focused ledgers:

```text
toolkit/adm_harness_cli/runs/stage1_v5_decoupled_carve_lapse_selected_ledger/
toolkit/adm_harness_cli/runs/stage1_v10_decoupled_carve_lapse_selected_ledger/
```

Focused minimal-traversability reports:

```text
toolkit/adm_harness_cli/runs/stage1_v5_decoupled_carve_lapse_minimal_traversability_report/
toolkit/adm_harness_cli/runs/stage1_v10_decoupled_carve_lapse_minimal_traversability_report/
```

V5 focused comparison:

| case | packet safe | max live packet fraction | top hard channels in live packet | live Tkk fraction | live p_l fraction | status |
|---|---|---:|---:|---:|---:|---|
| uncarved selected V5 | yes | 0.261006 | 1 | 0.221837 | 0.261006 | fail |
| decoupled carve/lapse V5 | yes | 0.144818 | 0 | 0.140270 | 0.144818 | fail |

V10 focused comparison:

| case | packet safe | max live packet fraction | top hard channels in live packet | live Tkk fraction | live p_l fraction | status |
|---|---|---:|---:|---:|---:|---|
| uncarved selected V10 | no | 0.307266 | 8 | 0.307266 | 0.261007 | fail |
| decoupled carve/lapse V10 | yes | 0.159615 | 0 | 0.159615 | 0.144818 | fail |

## Interpretation

This is a meaningful harness improvement and a meaningful architecture improvement, but not a strict Stage I-B pass.

The decoupled carve/lapse candidate achieves:

```text
V5 and V10 packet-norm safety
top hard-channel bad points moved out of the live packet
live radial-null exposure reduced at V5 and V10
live radial-pressure exposure reduced at V5 and V10
V10 max total burden ratio improved relative to the co-located compensator
```

It does not achieve:

```text
tiny live hard-channel fractions
strict minimal-traversability pass
full packet/source separation
```

The result changes the diagnosis. The earlier gate fail was not fatal in the sense of "the support shell must be abandoned." It was showing that the packet was sitting on the standing-support substrate. Carving the substrate and restoring lapse with a wider compensator can move the worst points infrastructure-side. The remaining problem is a residual percent-level radial-null/radial-pressure burden along the live packet tube.

## Recommended Next Step

Do not move to Stage II yet. The scalar-source screen would still be fitting a metric-side candidate that fails the strict packet/source separation target.

The next Stage I harness move should test whether the residual live-packet burden is mostly from the standing support floor or from gradients introduced by the carve/lapse transition:

```text
1. Add an offset or annular packet-lapse compensator option.
2. Add a two-zone standing-support carve: deeper center, softer shoulder.
3. Sweep carve strengths 0.14 to 0.20 with wider carve widths 1.2 to 2.0.
4. Keep the decoupled lapse family near gain 0.50 to 0.60, radius 1.3 to 1.5, width 1.4 to 1.8.
```

The best current branch is now a V5/V10-safe redesign candidate, not yet a minimal-traversability success.
