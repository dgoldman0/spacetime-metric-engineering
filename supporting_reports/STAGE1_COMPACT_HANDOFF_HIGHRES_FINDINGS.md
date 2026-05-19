# Stage I Compact Handoff High-Resolution Findings

## Purpose

The compact handoff component was introduced to test whether the packet/support transition could reduce the derivative concentration itself, rather than only moving burden between `Tkk`, `p_l`, `j_l`, and `pOmega`.

The earlier direction-finding memo showed a promising low-resolution signal: very wide compact profiles reduced live `j_l`, live `pOmega`, and channel-cause derivative scores, while charging live `p_l`. This follow-up asks whether that signal survives a stricter V5 grid and whether the pressure cost can be separated by tuning the early entry containment profile.

## Runs

Selected V5 high-resolution compact handoff screen:

```text
toolkit/adm_harness_cli/runs/stage1_v5_compact_handoff_selected_61x83/
```

Selected V5 high-resolution entry-balance screen:

```text
toolkit/adm_harness_cli/runs/stage1_v5_compact_entry_balance_selected_61x83/
```

V5 channel-cause comparison:

```text
toolkit/adm_harness_cli/runs/stage1_v5_compact_handoff_channel_cause_61x83/
```

Low-resolution entry decomposition, used only to choose the high-resolution balance checks:

```text
toolkit/adm_harness_cli/runs/stage1_v5_compact_entry_decomposition_31x45/
```

All V5 selected checks here used `61 x 83` unless otherwise stated. The compact branch used the smooth-split harness with:

```text
standing_support_packet_smooth_split_radial_profile = compact_smoothstep7
standing_support_packet_smooth_split_composition = additive
standing_support_packet_smooth_split_null_cushion_log_gain = -0.07
```

## Main High-Resolution Results

The core comparison is:

| case | live Tkk | live p_l | live j_l | live pOmega | Tkk peak | pOmega peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `split_ref` | 9.5236 | 0.3935 | 0.0651 | 1.9144 | 1.0163 | 0.2169 |
| `smooth_edge004_tanh` | 9.1217 | 0.3824 | 0.0664 | 1.9308 | 1.0084 | 0.2327 |
| `compact7_wide3_edge100` | 8.7360 | 0.4159 | 0.0659 | 1.4801 | 1.1591 | 0.2033 |
| `compact7_wide3_edge120` | 8.6093 | 0.4093 | 0.0668 | 1.4946 | 1.1656 | 0.2122 |
| `compact7_wide4_edge160` | 8.4975 | 0.4416 | 0.0585 | 1.2278 | 1.0672 | 0.1463 |

Relative to `split_ref`, `compact7_wide4_edge160` gives:

| channel | change |
| --- | ---: |
| live Tkk | -10.8% |
| live p_l | +12.2% |
| live j_l | -10.2% |
| live pOmega | -35.9% |
| Tkk point peak | +5.0% |
| pOmega point peak | -32.5% |

This is the important high-resolution result. The wide compact handoff does not merely hide cost in the point peaks. It improves live `Tkk`, live `j_l`, live `pOmega`, and point `pOmega` at the same time. The cost is concentrated in live `p_l`, plus a modest `Tkk` point-peak increase.

## Entry-Balance Decomposition

The low-resolution decomposition suggested that reducing early entry strength or entry width might separate the live `p_l` cost from the angular/current relief. The high-resolution check narrowed that interpretation.

| case | entry carve | entry width | live Tkk | live p_l | live j_l | live pOmega | Tkk peak | pOmega peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compact7_wide4_edge160` | 0.75 | 4.8 | 8.4975 | 0.4416 | 0.0585 | 1.2278 | 1.0672 | 0.1463 |
| `wide4_e075_w42` | 0.75 | 4.2 | 8.4326 | 0.4005 | 0.0692 | 1.5203 | 1.2179 | 0.2328 |
| `wide4_e070_w42` | 0.70 | 4.2 | 9.0049 | 0.5067 | 0.0453 | 1.0840 | 0.8758 | 0.1088 |
| `wide4_e070_w48` | 0.70 | 4.8 | 9.0808 | 0.5583 | 0.0389 | 0.8813 | 0.7957 | 0.0864 |

The separation is real but not immediately usable as a final candidate:

- Full-strength entry with narrower width (`0.75 / 4.2`) brings `p_l` near the reference value, but loses much of the angular/current relief and introduces the worst `Tkk` point peak in the selected set.
- Weakened entry (`0.70`) gives excellent `j_l`, `pOmega`, and point-peak relief, but live `p_l` rises too much and live `Tkk` gives back most of the compact branch's gain.
- Full-strength wide entry (`0.75 / 4.8`) remains the best serious compact candidate because it gives the strongest combined improvement in live `Tkk`, live `j_l`, live `pOmega`, and point `pOmega`.

This means the `p_l` cost is not simply caused by "too much early entry containment." Weakening entry actually worsens live `p_l`. The early entry layer is carrying radial pressure balance. The broad catch/handoff sleeve is carrying angular/current relief. The two roles are coupled but distinguishable.

## Channel-Cause Confirmation

The high-resolution channel-cause pass compared `split_ref`, `smooth_edge004_tanh`, and `compact7_wide4_edge160`.

| case | live cause rows | live badness mean | radial metric score | lapse curvature score | beta gradient score | `rel_abs_d2_l_gamma_ll` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `split_ref` | 28 | 0.0611 | 92.48 | 46.36 | 30.44 | 1297.40 |
| `smooth_edge004_tanh` | 29 | 0.0761 | 90.63 | 44.92 | 30.87 | 1262.45 |
| `compact7_wide4_edge160` | 21 | 0.0404 | 48.15 | 24.50 | 15.53 | 394.93 |

This is the strongest evidence that the compact handoff component is buying something structural. At the stricter grid, the compact wide4 branch reduces:

| measure | reduction vs `split_ref` |
| --- | ---: |
| live cause badness mean | -33.9% |
| radial metric score mean | -47.9% |
| lapse curvature score mean | -47.2% |
| beta gradient score mean | -49.0% |
| `rel_abs_d2_l_gamma_ll` mean | -69.6% |

The dominant derivative family remains mostly radial-metric dominated across the top channel rows. That matters: the compact handoff does not change the algebraic origin into a new mysterious failure. It reduces the same radial metric derivative concentration that the channel-cause ledger has been identifying.

## Interpretation

The compact handoff is a real Stage I component candidate, but not yet a final Stage I closure.

It buys:

- a substantial reduction in live `pOmega`;
- a real reduction in live `j_l`;
- a meaningful live `Tkk` improvement;
- lower point `pOmega`;
- sharply lower derivative-origin scores in the live channel-cause ledger.

It costs:

- higher live `p_l`;
- a modest `Tkk` point-peak increase in the best balanced wide4 branch;
- a sensitive entry/catch trade surface where weakening entry improves angular/current channels but makes pressure balance worse.

That pattern is not random whack-a-mole. It is structured. The broad compact handoff reduces the packet/support derivative concentration, especially in the radial metric sector. The remaining problem is that the same broad relief changes radial pressure balance. The entry layer and catch/handoff layer are serving different physical roles:

```text
entry containment        -> radial pressure balance / live p_l control
broad compact handoff    -> angular-current relief / derivative concentration control
edge carve recovery      -> live Tkk recovery with peak/current cost
```

The most useful current candidate is therefore not a single scalar "more compact" setting. It is a two-role profile:

```text
strong enough early entry containment
plus broad compact catch/handoff smoothing
plus constrained edge recovery
```

The high-resolution checks say that full-strength entry with wide compact support is closer to this than weakened entry. Reducing early entry strength is not a clean pressure fix; it is an angular/current relief mode that sacrifices pressure balance.

## Implications For Viability

This result improves the viability picture for Stage I. The branch is still outside a clean hard-bounded final gate, but it has crossed an important diagnostic threshold: it lowered the underlying derivative concentration at V5 on a stricter grid.

That matters because the recent paired-compensator and smooth split screens often showed channel steering without enough evidence that the root concentration had been reduced. The compact handoff branch gives that evidence.

The design is not yet ready to freeze because live `p_l` is still too high in the strongest derivative-relief branch, and narrower entry control produces unacceptable point-peak or angular/current regressions. But this is now a focused design problem, not a broad search problem:

```text
preserve wide compact catch/handoff relief
while adding pressure-aware entry containment or local radial-pressure balancing
without reintroducing the old derivative cliff
```

## Recommended Next Step

Do not add another free fine-tuning sleeve first. The next component should be a pressure-aware compact entry/catch profile that encodes the separation found here.

The next law should probably expose fewer, more coherent controls:

```text
entry_pressure_hold_strength
entry_pressure_hold_width
compact_handoff_width
edge_recovery_strength
```

but internally it should enforce a smooth relation between them, so that the entry layer cannot be weakened enough to dump cost into `p_l` while the handoff layer remains broad enough to suppress `j_l/pOmega`.

In practical harness terms, the next focused test should start from `compact7_wide4_edge160` and try one pressure-control modification at a time:

1. Preserve `entry_carve = 0.75`.
2. Keep the broad compact catch/edge support near `catch_width = 3.4`, `edge_width = 7.2`.
3. Add a pressure-aware entry profile or radial-pressure balancing factor that is strongest in the entry/core-throat region but derivative-limited at the packet boundary.
4. Reject candidates that regain `p_l` by losing the wide4 improvements in live `j_l`, live `pOmega`, or channel-cause derivative scores.

The current best diagnostic candidate remains:

```text
compact_smoothstep7
entry_carve = 0.75
entry_width_multiplier = 4.8
catch_carve = 0.15
catch_width_multiplier = 3.4
edge_carve = 0.16
edge_width_multiplier = 7.2
null_cushion_log_gain = -0.07
```

It should not be treated as a final refreeze. It should be treated as the first compact handoff candidate with high-resolution evidence of real derivative concentration reduction.
