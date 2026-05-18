# Stage I Two-Zone Packet Carve Sweep

## Purpose

The decoupled carve/lapse sweep showed that separating the packet carve from the packet-lapse compensator can recover V10 packet safety and move top hard-channel points out of the live packet. The remaining problem was percent-level live radial-null and radial-pressure burden.

This sweep tested whether that residual burden is caused by the standing support floor under the packet or by sharp carve/lapse transition gradients. The new harness option adds a wider, softer standing-support shoulder carve on top of the existing packet-centered carve.

This is still demanded-source placement accounting only.

## Harness Change

The source ledger now supports a two-zone standing-support packet carve:

```text
core carve contribution     = standing_support_packet_exclusion * core_packet_window
shoulder carve contribution = standing_support_packet_exclusion_shoulder * shoulder_packet_window
W -> W_raw * (1 - clip(core + shoulder, 0, 1))
```

New parameters:

```text
standing_support_packet_exclusion_shoulder
standing_support_packet_exclusion_shoulder_radius_multiplier
standing_support_packet_exclusion_shoulder_width_multiplier
standing_support_packet_exclusion_shoulder_schedule
```

New point-ledger fields:

```text
standing_support_packet_carve_shoulder_window
standing_support_packet_carve_contribution
```

The focused ledger and overlay sweep CLIs expose the singular/plural forms of the new shoulder controls.

## Validation

```text
python -m py_compile adm_harness/source_ledger.py scripts/run_source_ledger.py scripts/run_source_overlay_sweep.py
pytest -q tests/test_validation_ladder_hardening.py tests/test_service_synthesis_validation.py
25 passed
```

## Sweeps

Smoke runs:

```text
toolkit/adm_harness_cli/runs/stage1_v5_two_zone_carve_smoke/
toolkit/adm_harness_cli/runs/stage1_v10_two_zone_carve_smoke/
toolkit/adm_harness_cli/runs/stage1_v10_two_zone_carve_lapse_gain_smoke/
```

High-resolution focused runs:

```text
toolkit/adm_harness_cli/runs/stage1_v10_two_zone_carve_highres/
toolkit/adm_harness_cli/runs/stage1_v5_two_zone_carve_tradeoff/
```

Focused selected ledgers and worldtube reports:

```text
toolkit/adm_harness_cli/runs/stage1_v5_two_zone_carve_balanced_ledger/
toolkit/adm_harness_cli/runs/stage1_v10_two_zone_carve_balanced_ledger/
toolkit/adm_harness_cli/runs/stage1_v5_two_zone_carve_minimal_traversability_report/
toolkit/adm_harness_cli/runs/stage1_v10_two_zone_carve_minimal_traversability_report/
```

## Selected Balanced Candidate

The best aggressive V10 point reduced live fractions further, but raised V5 point-peak cost. The selected balanced candidate keeps a lower V10 point peak while still improving live-packet exposure:

```text
standing_support_packet_exclusion = 0.17
standing_support_packet_exclusion_shoulder = 0.05
standing_support_packet_exclusion_shoulder_radius_multiplier = 1.3
standing_support_packet_exclusion_shoulder_width_multiplier = 1.6
standing_support_packet_lapse_log_gain = 0.70
standing_support_packet_lapse_radius_multiplier = 1.4
standing_support_packet_lapse_width_multiplier = 1.6
schedule = live_only for carve, shoulder, and lapse
```

Comparison with the previous decoupled carve/lapse candidate:

| V | candidate | packet safe | live Tkk fraction | live p_l fraction | top hard channels in live packet | max live packet fraction | status |
|---:|---|---|---:|---:|---:|---:|---|
| 5 | decoupled carve/lapse | yes | 0.140270 | 0.144818 | 0 | 0.144818 | fail |
| 5 | two-zone balanced | yes | 0.121145 | 0.114254 | 0 | 0.121145 | fail |
| 10 | decoupled carve/lapse | yes | 0.159615 | 0.144818 | 0 | 0.159615 | fail |
| 10 | two-zone balanced | yes | 0.129528 | 0.114254 | 0 | 0.129528 | fail |

The top radial-null and radial-pressure points remain outside the live packet. In the balanced two-zone reports, both hard-channel top points sit in `core_throat`, not `packet_in_support`.

## Interpretation

The two-zone carve is a real improvement over the one-zone decoupled carve/lapse branch:

```text
V5 live Tkk fraction improves from 0.140 to 0.121
V5 live p_l fraction improves from 0.145 to 0.114
V10 live Tkk fraction improves from 0.160 to 0.130
V10 live p_l fraction improves from 0.145 to 0.114
packet norm remains safe at V5 and V10
top hard-channel points remain outside the live packet
```

It still does not pass strict minimal traversability:

```text
live hard-channel fractions are still percent-level
V5 point-peak ratios rise in the stronger shoulder branches
the packet/support separation is improved but not clean enough for Stage II target selection
```

The data suggest that the residual live burden is partly the standing support floor: adding a wider shoulder lowers live radial-null and radial-pressure exposure. The rising V5 point peaks suggest that the transition geometry is now the limiting design problem.

## Recommended Next Step

The next harness improvement should make the shoulder smoother or less symmetric:

```text
add an annular carve shoulder that avoids carving the packet center twice
or add an offset/edge-only shoulder that softens the transition ahead of the packet
or add an independent shoulder schedule with a wider temporal ramp than live_only
```

The next sweep should hold the balanced branch as the baseline and test whether smoother shoulder timing can keep the live-fraction gain while reducing V5 point peaks.
