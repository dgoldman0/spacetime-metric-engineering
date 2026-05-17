# Active Rail Radial-Pressure Softening Probe

This bundle continues from the shaped-catch branch and keeps the earlier bundles untouched. The carried-forward design lesson is: support-side catch can lead slightly, but packet rematch must remain tightly locked to it. The present probe keeps that locked-lead shaped catch and asks how to reduce the remaining radial pressure `p_l` without losing packet safety.

## Executive result

The viable direction is radial support-edge widening, with a hard safety boundary. Widening `w_th` from `0.35` to about `0.55` lowered live radial-pressure burden by about 18% and live radial-null burden by about 24–25% in the refined check, while keeping all live packet norms negative. Pushing to `w_th = 0.60` lowered the burdens further, but produced a live packet-norm failure in both coarse and refined checks.

The best safe branch from this round is:

```text
R1.75 locked-lead shaped catch + radial-soft v1

beta/support catch:   x = -0.05, w = 0.32, minimum jerk
packet rematch:       x =  0.00, w = 0.32, minimum jerk
radial support:       Rth = 1.75, w_th = 0.55
packet transition:    Rpass = 0.35, w_pass = 0.06
angular jacket:       ROmega = 1.75, wOmega = 1.40, aOmega = 0.20
```

Adding modest packet smoothing (`w_pass = 0.08`) on top of `w_th = 0.55` gives a little extra `Tkk` improvement, but it does not reduce `p_l` further. The safe default should therefore stay conservative on `w_pass` unless the next target is specifically `Tkk` peak shaping.

## Refined decision table

Grid: `21 x 37`; finite-difference demanded-source diagnostic. Ratios are relative to the locked-lead shaped-catch baseline.

| case          |   score |   pl_live_ratio |   tkk_live_ratio |   pl_peak_ratio |   tkk_peak_ratio |   infra_pressure_ratio |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |
|:--------------|--------:|----------------:|-----------------:|----------------:|-----------------:|-----------------------:|-----------------------:|----------------------------:|------------------------------:|-------------------------------------:|--------------------------------:|---------------------------------------:|
| wth55_wpass08 |  0.8216 |          0.8216 |           0.7502 |          0.7445 |           0.7607 |                 0.7598 |                 -306.2 |                           0 |                         14.44 |                                74.65 |                          0.2669 |                                 0.2448 |
| wth_0.55      |  0.8216 |          0.8216 |           0.7619 |          0.7445 |           0.9081 |                 0.7598 |                 -306.2 |                           0 |                         14.44 |                                75.81 |                          0.2669 |                                 0.2479 |
| shaped_base   |  1      |          1      |           1      |          1      |           1      |                 1      |                 -584.3 |                           0 |                         17.57 |                                99.51 |                          0.2468 |                                 0.2286 |
| wth_0.60      | 10.77   |          0.7701 |           0.6921 |          0.7226 |           0.8741 |                 0.7069 |                12390   |                           1 |                         13.53 |                                68.87 |                          0.2689 |                                 0.2483 |

## Refined stage read

The improvement lands exactly where we wanted: catch/rematch and release/shift-fade. Reset/decompression remains excluded from live packet exposure.

### abs_p_l

| case          |   catch_rematch |   post_release_buffer |   release_shift_fade |   reset_decompression |
|:--------------|----------------:|----------------------:|---------------------:|----------------------:|
| shaped_base   |         15.9141 |                     0 |              1.65789 |                     0 |
| wth55_wpass08 |         13.1132 |                     0 |              1.3232  |                     0 |
| wth_0.55      |         13.1132 |                     0 |              1.3232  |                     0 |
| wth_0.60      |         12.2893 |                     0 |              1.24241 |                     0 |

### neg_Tkk_radial

| case          |   catch_rematch |   post_release_buffer |   release_shift_fade |   reset_decompression |
|:--------------|----------------:|----------------------:|---------------------:|----------------------:|
| shaped_base   |         87.142  |                     0 |             12.3661  |                     0 |
| wth55_wpass08 |         65.1835 |                     0 |              9.46318 |                     0 |
| wth_0.55      |         66.3463 |                     0 |              9.46734 |                     0 |
| wth_0.60      |         60.1223 |                     0 |              8.75089 |                     0 |

## What each option taught us

**1. Widening the radial support edge works.** In the coarse screen, `w_th = 0.40, 0.45, 0.50, 0.55` gave a monotonic reduction in absolute live `p_l` burden and absolute live `Tkk` burden, while remaining packet-safe through `w_th = 0.55`. The refined check preserved that result.

**2. There is a safety boundary near `w_th ≈ 0.60`.** The `w_th = 0.60` case looked better by raw burden, but the live packet norm became positive at one sampled point. That makes it a useful boundary marker, not a promotable candidate.

**3. Packet-transition smoothing is not the `p_l` cure.** Increasing `w_pass` from `0.06` to `0.08–0.12` barely changed live radial pressure. It did reduce `Tkk` somewhat, so it may be useful later as a secondary null-channel tweak.

**4. Moving `Rth` outward improves fractions and peaks, but not absolute live radial burden.** The `Rth = 1.80–2.00` screen made live fractions look better because more burden moved into infrastructure. Absolute live `p_l` and `Tkk` burden rose slightly. That is not the right first move for the pressure problem.

**5. The simple asymmetric shoulder did not beat ordinary widening.** The tested inner-soft/outer-firm variants mostly replicated the benefits of wider `w_th` while worsening pressure peak behavior. A more carefully designed asymmetric shoulder may still be possible, but the naive version is not the branch to promote.

## Implication

The radial-pressure problem is a radial wall/gradient problem, not a catch-timing problem. The shaped catch fixed part of the null-channel exposure; the radial-soft branch now shows that `p_l` responds to support-edge width. The system wants a coordinated temporal handoff plus a softer radial support edge, with packet safety setting the upper bound on how soft the edge can become.

## Next test

Promote `w_th = 0.55` as the next candidate and refine around the safety boundary:

```text
w_th = 0.52, 0.54, 0.56, 0.58
w_pass = 0.06 initially
check live packet norm at higher resolution
only then test w_pass = 0.08 as a secondary Tkk-shaping tweak
```

The pass condition is not just lower burden. The pass condition is lower live `p_l`, retained shaped-catch `Tkk` gains, and zero positive live packet-norm points at higher resolution.
