# Stage I-C V10 Selected-Candidate Edge Check

## Purpose

This edge check reran the selected V5 clock-lapse-only support-shell candidate at service factor `V = 10`. The goal was not to choose the V5 candidate again. It was to ask whether the selected architecture degrades gracefully when the carried-shift load is doubled.

Because Stage I-B already failed the strong minimal-traversability gate at V5, this V10 result should be read as diagnostic stress evidence, not as a rescue path.

## Candidate Checked

```text
variant:                  tuned_w0569_eta200
service factor:           V = 10
support-shell amplitude:  +0.5
sign:                     pos
catch lead:               1.55
temporal width:           0.30
clock-lapse ratio:        0.375
clock-lapse log gain:     0.1875
rail-stretch ratio:       0.0
throat-capacity ratio:    0.0
throat-capacity log gain: 0.0
grid:                     ns = 53, nl = 73
```

Run directories:

```text
toolkit/adm_harness_cli/runs/stage1_v10_selected_candidate_check/
toolkit/adm_harness_cli/runs/stage1_v10_selected_candidate_ledger/
toolkit/adm_harness_cli/runs/stage1_v10_minimal_traversability_report/
```

Repository commit at review time:

```text
f8bb7fe
```

## Overlay Sweep Readout

The one-case V10 overlay sweep completed without harness failures, but it found a packet-safety failure:

| readout | value |
|---|---:|
| positive_packet_norm_live | 3 |
| packet_norm_live_delta_max_abs | 0.105805 |
| max_total_burden_ratio | 1.054417 |
| neg_Tkk_radial_total_ratio | 1.017231 |
| abs_pOmega_total_ratio | 1.054417 |
| abs_j_l_total_ratio | 1.011784 |
| neg_rho_packet_total_ratio | 1.000000 |
| max_point_peak_ratio | 1.015240 |
| source_objective_score | 11.029344 |

The source-burden ratios themselves are not catastrophic; they remain in roughly the same aggregate band as V5. The hard stop is packet safety: `positive_packet_norm_live = 3`.

## Packet-Worldtube Readout

The V10 minimal-traversability report also failed:

```text
packet_norm_safe = false
positive_packet_norm_live = 3
max_packet_norm_live = 37140
live_packet_active_shell_points = 0
max_live_packet_fraction_any_channel = 0.307266
top hard-channel bad point lies in the live packet
```

Channel placement:

| channel | total burden | live packet fraction | main support fraction | top bad point region | top bad point in live packet? |
|---|---:|---:|---:|---|---|
| neg_Tkk_radial | 537.772192 | 0.307266 | 0.683872 | packet_in_support | true |
| abs_p_l | 87.356414 | 0.261007 | 0.730107 | core_throat | false |
| abs_pOmega | 3.928075 | 0.002728 | 0.184712 | support_edge | false |
| abs_j_l | 0.264407 | 0.008555 | 0.538304 | packet_in_support | false |
| neg_rho_euler | 0.454030 | 0.000000 | 0.012724 | outer_quarantine_shell | false |
| neg_rho_packet | 0.564644 | 0.000000 | 0.119685 | support_edge | false |

## Interpretation

The selected high-amplitude coupled support-shell candidate does not survive the V10 edge check. It keeps the active shell outside the live packet, but the live packet itself is no longer causally safe at all sampled points. The same standing packet/support overlap seen at V5 also worsens in the radial-null channel: the live packet carries about `30.7%` of the radial-null badness at V10.

This confirms that the earlier tiny support-shell target surviving V10 should not be generalized to the high-amplitude coupled candidate. The high-amplitude V5 candidate is a useful metric-side actuator at V5, but it is not a robust V10 architecture.

## Decision

Stage I-C status:

```text
fail
```

Reason:

```text
The selected V5 candidate has positive live packet-norm samples at V10 and carries a larger live radial-null burden. It does not degrade gracefully enough to support the current packet-service bypass claim.
```

## Recommended Next Move

Do not proceed to Stage II as though this selected metric candidate were architecture-clean. The next work should redesign Stage I first:

```text
separate the standing packet corridor from packet_in_support radial-null burden
recover V10 packet-norm safety before using high-amplitude support-shell coupling
consider lower-amplitude or V-aware support-shell scaling
revisit the support substrate placement relative to the live packet tube
```

The scalar-source compatibility screen remains valuable later, but this V10 edge check says the current metric-side candidate is not ready to be treated as the final source-family target.
