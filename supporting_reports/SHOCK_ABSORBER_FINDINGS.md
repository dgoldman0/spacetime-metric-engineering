# Catch-Edge Shock Absorber Test

## Scope

This tests a geometry-side packet-edge shock absorber on the new active-rail freeze candidate. The absorber is a small, smooth lapse guard localized near the inner packet edge during catch/rematch. This is still a prescribed-geometry Einstein-source diagnostic, not a physical source construction.

## Result

The shock-absorber idea partially works, but not strongly enough to promote as a new freeze geometry yet. A mild/early inner-edge lapse guard reduces integrated live catch/rematch negative radial-null burden while preserving packet safety and leaving radial pressure unchanged. However, it raises local/global `Tkk` peaks, so it is better treated as a promising source-side catch component or a geometry-side idea needing a smoother implementation.

Best high-resolution geometry-side variant tested:

```text
early inner-edge lapse guard
edge_guard_kind = alpha
edge_guard_amp  = 0.30
edge_guard_x    = -0.30
edge_guard_w    = 0.28
edge_guard_sigma = 0.075
```

It gives:

```text
live catch Tkk burden: 97.2% of freeze
live total Tkk burden: 97.5% of freeze
live p_l burden: 100.0% of freeze
packet safety: 0 positive live packet-norm points
global Tkk peak: 111.3% of freeze
```

## High-resolution comparison

| case                | note                                                                      |   live_catch_Tkk_burden_ratio_vs_freeze |   live_total_Tkk_burden_ratio_vs_freeze |   live_total_p_l_burden_ratio_vs_freeze |   global_Tkk_peak_ratio_vs_freeze |   live_catch_Tkk_peak_ratio_vs_freeze |   max_live_packet_norm |   positive_live_packet_norm_points |
|:--------------------|:--------------------------------------------------------------------------|----------------------------------------:|----------------------------------------:|----------------------------------------:|----------------------------------:|--------------------------------------:|-----------------------:|-----------------------------------:|
| alpha_early030_w028 | early inner-edge lapse guard, amp=0.30, x=-0.30, w=0.28                   |                                  0.9721 |                                  0.9754 |                                       1 |                             1.113 |                                 1.052 |                 -198.9 |                                  0 |
| alpha_early030_w036 | early inner-edge lapse guard, amp=0.30, x=-0.30, w=0.36                   |                                  0.9726 |                                  0.9759 |                                       1 |                             1.117 |                                 1.05  |                 -198.9 |                                  0 |
| alpha_guard_250     | inner-edge lapse guard, amp=0.25, catch centered at x=0.0                 |                                  0.978  |                                  0.9806 |                                       1 |                             1.042 |                                 1.042 |                 -198.9 |                                  0 |
| alpha_guard_150     | inner-edge lapse guard, amp=0.15, catch centered at x=0.0                 |                                  0.983  |                                  0.985  |                                       1 |                             1.024 |                                 1.024 |                 -198.9 |                                  0 |
| freeze_candidate    | no shock absorber; current freeze                                         |                                  1      |                                  1      |                                       1 |                             1     |                                 1     |                 -198.9 |                                  0 |
| alpha_guard_080     | strong inner-edge lapse guard, amp=0.80; included as failure mode warning |                                  1.002  |                                  1.002  |                                       1 |                             1.843 |                                 1.145 |                 -198.9 |                                  0 |

## Interpretation

This confirms the residual diagnosis: the catch-edge layer is a real control location. But the simple lapse-only geometric guard is a blunt implementation. It reduces integrated live catch `Tkk` by only a few percent and pays for that by increasing local peaks. The source-proxy version of the shock absorber is cleaner than the current metric-guard version.

The useful design lesson is:

```text
catch-edge shock absorber = valid target
simple localized lapse guard = partial success, not freezeable yet
next implementation should smooth the edge guard more gently or treat it as a separate source component
```

## Implication

Do not replace the freeze candidate with this guard yet. Preserve the current freeze and add the shock absorber as a source-decomposition component. If we continue geometry tuning, test a smoother, lower-curvature guard rather than a sharper lapse bump.