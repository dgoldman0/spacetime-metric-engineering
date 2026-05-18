# Stage I Carve-Plus-Lapse Compensator Sweep

## Purpose

The packet carve-out sweep showed that reducing the standing support bump under the packet tube moves hard-channel burden out of `packet_in_support`, but it consumes causal margin. This sweep tested a packet-local lapse compensator on the same carve window:

```text
alpha -> alpha * exp(packet_lapse_log_gain * carve_window)
```

The goal was to find whether modest standing-support carving plus local lapse compensation can:

```text
preserve packet norm safety
remove top hard-channel points from the live packet
reduce live radial-null and radial-pressure exposure
survive V10 better than the uncarved selected candidate
```

## Code Added

The current working tree adds:

```text
standing_support_packet_lapse_log_gain
standing_support_packet_lapse_factor
standing_support_packet_delta_alpha
```

to the source-ledger path and exposes the parameter through:

```text
toolkit/adm_harness_cli/scripts/run_source_ledger.py
toolkit/adm_harness_cli/scripts/run_source_overlay_sweep.py
```

No commit has been made for this sweep.

## Validation

The existing test set still passes:

```text
pytest -q tests/test_validation_ladder_hardening.py tests/test_service_synthesis_validation.py
25 passed
```

## V5 Sweep

Run directory:

```text
toolkit/adm_harness_cli/runs/stage1_v5_carve_lapse_compensator/
```

Grid:

```text
V = 5
carve strengths: 0.12, 0.16, 0.20, 0.22
packet-lapse log gains: 0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30
ns = 53, nl = 73
```

Result:

```text
For V5 alone, the lapse compensator is not needed.
The best worldtube exposure score remains near zero packet-lapse gain.
Increasing packet-lapse gain buys extra causal margin but raises live radial-null exposure.
```

Best V5 exposure case in the tested band:

| carve | packet lapse gain | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 0.22 | 0.00 | 0 | 0.066475 | 0.113716 | 0 | 1.095747 |

This remains a strict minimal-traversability fail because the live fractions are still percent-level.

## V10 Sweep

Run directories:

```text
toolkit/adm_harness_cli/runs/stage1_v10_carve_lapse_compensator/
toolkit/adm_harness_cli/runs/stage1_v10_lowcarve_lapse_compensator/
```

The broad V10 carve/lapse sweep found only one initially safe case:

| carve | packet lapse gain | packet failures | live Tkk fraction | live p_l fraction | top hard channels in live packet | max total ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 0.12 | 0.75 | 0 | 0.282501 | 0.169190 | 0 | 1.075107 |

The lower-carve/high-lapse follow-up found the same case as the best V10-safe point. Lower carve strengths with high lapse can be packet-safe, but they leave more radial-null exposure or keep a top hard-channel point in the live packet.

## Focused Candidate Report

Focused ledgers:

```text
toolkit/adm_harness_cli/runs/stage1_v5_carve_lapse_selected_ledger/
toolkit/adm_harness_cli/runs/stage1_v10_carve_lapse_selected_ledger/
```

Focused minimal-traversability reports:

```text
toolkit/adm_harness_cli/runs/stage1_v5_carve_lapse_minimal_traversability_report/
toolkit/adm_harness_cli/runs/stage1_v10_carve_lapse_minimal_traversability_report/
```

Selected carve/lapse candidate:

```text
standing_support_packet_exclusion = 0.12
standing_support_packet_lapse_log_gain = 0.75
schedule = live_only
radius multiplier = 1.0
width multiplier = 1.0
```

Focused V5 comparison:

| case | packet safe | live Tkk fraction | live p_l fraction | top hard point in live packet? | status |
|---|---|---:|---:|---|---|
| uncarved V5 | yes | 0.221837 | 0.261006 | yes | fail |
| carve+lapse V5 | yes | 0.251622 | 0.169190 | no | fail |

Focused V10 comparison:

| case | packet safe | live Tkk fraction | live p_l fraction | top hard point in live packet? | status |
|---|---|---:|---:|---|---|
| uncarved V10 | no | 0.307266 | 0.261007 | yes | fail |
| carve+lapse V10 | yes | 0.282501 | 0.169190 | no | fail |

## Interpretation

The carve-plus-lapse branch is a real V10 stabilization improvement, but it is not the minimal-traversability solution.

It achieves:

```text
V10 packet norm safety recovered
top hard-channel bad points moved out of the live packet
radial-pressure live fraction reduced materially
```

It does not achieve:

```text
tiny live hard-channel fractions
clean live radial-null exposure
strict Stage I-B pass
```

The lesson is sharp: packet-local lapse can buy back causal margin, but it partially reintroduces radial-null burden. The next design should decouple causal-margin restoration from radial-null recontamination.

## Recommended Next Step

The next sweep should vary the compensator shape, not just its amplitude:

```text
carve strengths: 0.10, 0.12, 0.14, 0.16
packet lapse gains: 0.55, 0.65, 0.75, 0.85
carve radius multipliers: 0.8, 1.0, 1.2
lapse radius multipliers: separate from carve if added
lapse width multipliers: separate from carve if added
```

The likely needed harness improvement is separate packet-carve and packet-lapse windows. The current compensator is co-located with the carve, which is probably why restoring causal margin also restores radial-null exposure in the packet corridor.
