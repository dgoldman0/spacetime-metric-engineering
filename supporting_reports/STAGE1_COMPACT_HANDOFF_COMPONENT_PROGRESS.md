# Stage I Compact Handoff Component Progress

## Purpose

Recent smooth-split and paired-compensator probes showed a structured trade surface: radial/edge support could lower live `Tkk` and `p_l`, but the cost reappeared in live `j_l` and `pOmega`; angular-capacity partners steered the trade but did not break it. That made another ordinary amplitude or timing sleeve unattractive.

This pass tested a different kind of component: a compact, endpoint-limited packet/support handoff primitive for the smooth-split layer. Instead of adding another local metric factor, this changes the transition law used by the smooth-split packet windows. The intent is to reduce the underlying derivative concentration at the packet/support handoff.

## Harness Addition

The smooth-split packet windows now accept:

```text
standing_support_packet_smooth_split_radial_profile
```

Supported values are:

```text
tanh
compact_minjerk
compact_smoothstep7
```

The default remains `tanh`, so existing smooth-split cases retain their prior behavior unless the compact radial profile is explicitly selected.

The compact profiles replace the tanh packet boundary with a finite-width smoothstep transition in packet radius. `compact_minjerk` is the fifth-order profile, while `compact_smoothstep7` has higher endpoint smoothness. This is a handoff-law component, not a new source sleeve.

## Runs

Initial compact handoff screen:

```text
toolkit/adm_harness_cli/runs/stage1_v5_smooth_split_compact_handoff_41x61/
```

Wide compact handoff follow-up:

```text
toolkit/adm_harness_cli/runs/stage1_v5_smooth_split_compact_handoff_wide_31x45/
```

The grids were kept modest because the goal was direction finding before a full channel-cause and high-resolution pass.

## Initial Result

Narrow compact profiles failed badly. At the old widths, the compact transition was too steep inside the active grid despite having zero endpoint derivatives.

At V5 `41 x 61`:

| case | live Tkk | live p_l | live j_l | live pOmega | Tkk peak | pOmega peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `smooth_additive_edge004_null_m007` | 9.7451 | 0.3971 | 0.0682 | 1.9572 | 0.9579 | 0.2337 |
| `compact5` | 21.7315 | 0.3705 | 0.1436 | 6.9452 | 7.2383 | 4.1381 |
| `compact7` | 30.4550 | 0.3781 | 0.1674 | 8.0913 | 12.7277 | 5.6783 |

That ruled out a narrow compact handoff. Endpoint smoothness alone is not enough; the transition must be broad enough that the active packet does not see a new compact edge cliff.

## Wide Compact Signal

The very wide compact C7 handoff was qualitatively different.

At V5 `31 x 45`:

| case | live Tkk | live p_l | live j_l | live pOmega | Tkk peak | pOmega peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `split_ref` | 8.4248 | 0.3952 | 0.0660 | 1.9728 | 0.9685 | 0.2022 |
| `smooth_edge004_tanh` | 8.0917 | 0.3831 | 0.0673 | 1.9873 | 0.9700 | 0.2162 |
| `compact7_edge004_wide3` | 8.6223 | 0.4412 | 0.0638 | 1.4713 | 1.0410 | 0.1770 |

The wide compact handoff gave back some radial performance, especially `p_l`, but it substantially reduced live `j_l` and `pOmega`.

The channel-cause read on the wide compact `edge004` case is the important part:

| measure | split_ref | tanh edge004 | compact7 wide3 edge004 |
| --- | ---: | ---: | ---: |
| live cause badness mean | 0.1135 | 0.1234 | 0.0882 |
| radial metric score mean | 80.95 | 78.48 | 55.17 |
| `rel_abs_d_l_gamma_ll` mean | 25.05 | 24.21 | 17.16 |
| `rel_abs_d2_l_gamma_ll` mean | 1093.93 | 1045.98 | 509.19 |

This is the first recent component that reduced the derivative concentration itself rather than merely steering the same burden between projections.

## Recovery Sweep

Since the wide compact handoff reduced derivative concentration but gave back radial performance, a small recovery sweep varied edge carve within the same wide compact component:

| case | edge carve | live Tkk | live p_l | live j_l | live pOmega | Tkk peak | pOmega peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compact7_wide3_edge004` | 0.04 | 8.6223 | 0.4412 | 0.0638 | 1.4713 | 1.0410 | 0.1770 |
| `compact7_wide3_edge008` | 0.08 | 8.3724 | 0.4262 | 0.0655 | 1.5003 | 1.0487 | 0.1902 |
| `compact7_wide3_edge012` | 0.12 | 8.1323 | 0.4122 | 0.0673 | 1.5302 | 1.0561 | 0.2044 |
| `compact7_wide3_edge016` | 0.16 | 7.8999 | 0.3992 | 0.0692 | 1.5622 | 1.0629 | 0.2196 |

This is not yet clean, but it is encouraging. Stronger edge carve recovers live `Tkk` and `p_l` while keeping live `pOmega` far below both `split_ref` and the tanh smooth split. The cost is a rising `j_l` and point-peak burden.

## Interpretation

This result gives the project breathing room. The compact handoff component is not a final Stage I candidate, but it is also not the exact old whack-a-mole trade. The wide compact profile reduced the derivative-origin scores in the live catch/rematch packet-support region and opened a new balance surface:

```text
wide compact handoff -> lower pOmega and lower derivative concentration
edge-carve recovery  -> restores Tkk/p_l at some current/point-peak cost
```

That means the next question is no longer whether any new component can move the underlying derivative concentration. It can. The question is whether the recovery branch can be made to keep `Tkk`, `p_l`, `j_l`, and point peaks jointly acceptable at higher resolution.

## Next Checks Before TeX Alignment

Before updating the TeX document, this branch needs:

1. A focused channel-cause pass on the recovery cases, especially `compact7_wide3_edge012` and `compact7_wide3_edge016`.
2. A higher-resolution V5 selected check once the best recovery point is chosen.
3. A V2 sanity check only after the V5 candidate is informative.
4. A V8 or V10 edge check only after V5 is stable.

The TeX file should not be aligned to this component yet as a settled design. It should wait until the channel-cause and higher-resolution checks tell us whether the compact handoff branch is a genuine new design direction or only a promising diagnostic.

