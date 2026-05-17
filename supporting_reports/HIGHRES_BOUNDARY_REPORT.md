# High-Resolution Radial-Softening Boundary Check

Grid: `41 x 73` per case, 2,993 points per case. The original four-case validation was extended downward after the higher grid found packet-norm failures at the previously safe-looking boundary.

This is a prescribed-geometry point-level Einstein-source ledger. It is a numerical design diagnostic, not a matter model or constraint solve.

## Ordered decision extract
| case        |     score |   pl_live_ratio |   tkk_live_ratio |   pl_peak_ratio |   tkk_peak_ratio |   infra_pressure_ratio |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   total_burden__abs_p_l |   total_burden__neg_Tkk_radial |   point_peak__abs_p_l |   point_peak__neg_Tkk_radial |   live_packet_point_peak__abs_p_l |   live_packet_point_peak__neg_Tkk_radial |
|:------------|----------:|----------------:|-----------------:|----------------:|-----------------:|-----------------------:|-----------------------:|----------------------------:|--------------------------------:|---------------------------------------:|------------------------------:|-------------------------------------:|------------------------:|-------------------------------:|----------------------:|-----------------------------:|----------------------------------:|-----------------------------------------:|
| shaped_base |  1        |        1        |         1        |        1        |         1        |               1        |               -467.882 |                           0 |                        0.249537 |                               0.231663 |                       17.2466 |                              98.3178 |                 69.1145 |                        424.4   |             0.0156262 |                     0.159218 |                        0.00953056 |                                 0.159218 |
| wth_0.520   |  0.852505 |        0.852505 |         0.801765 |        0.786293 |         0.954187 |               0.793878 |               -258.474 |                           0 |                        0.267965 |                               0.24954  |                       14.7028 |                              78.8278 |                 54.8685 |                        315.893 |             0.0122868 |                     0.151924 |                        0.00953056 |                                 0.151924 |
| wth_0.540   | 10.832    |        0.831955 |         0.773605 |        0.768317 |         0.943368 |               0.771296 |               4276.14  |                           1 |                        0.269162 |                               0.250246 |                       14.3484 |                              76.0591 |                 53.3077 |                        303.938 |             0.0120059 |                     0.150201 |                        0.00953056 |                                 0.150201 |
| wth_0.550   | 10.8216   |        0.821632 |         0.759491 |        0.757921 |         0.937649 |               0.760232 |               8795.9   |                           1 |                        0.26969  |                               0.250494 |                       14.1704 |                              74.6715 |                 52.543  |                        298.097 |             0.0118434 |                     0.149291 |                        0.00953056 |                                 0.149291 |
| wth_0.565   | 10.8061   |        0.806132 |         0.738357 |        0.740997 |         0.928727 |               0.743935 |              15119.3   |                           1 |                        0.2704   |                               0.25074  |                       13.903  |                              72.5937 |                 51.4167 |                        289.518 |             0.011579  |                     0.14787  |                        0.00953056 |                                 0.14787  |
| wth_0.569   | 10.802    |        0.802002 |         0.732739 |        0.739359 |         0.926283 |               0.739651 |              16714.1   |                           1 |                        0.270572 |                               0.25078  |                       13.8318 |                              72.0413 |                 51.1206 |                        287.268 |             0.0115534 |                     0.147481 |                        0.00953056 |                                 0.147481 |
| wth_0.570   | 10.801    |        0.800969 |         0.731336 |        0.738968 |         0.925669 |               0.738584 |              17106.8   |                           2 |                        0.270614 |                               0.250789 |                       13.814  |                              71.9034 |                 51.0469 |                        286.709 |             0.0115472 |                     0.147383 |                        0.00953056 |                                 0.147383 |

## Best safe cases

| case        |    score |   pl_live_ratio |   tkk_live_ratio |   pl_peak_ratio |   tkk_peak_ratio |   infra_pressure_ratio |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   total_burden__abs_p_l |   total_burden__neg_Tkk_radial |   point_peak__abs_p_l |   point_peak__neg_Tkk_radial |   live_packet_point_peak__abs_p_l |   live_packet_point_peak__neg_Tkk_radial |
|:------------|---------:|----------------:|-----------------:|----------------:|-----------------:|-----------------------:|-----------------------:|----------------------------:|--------------------------------:|---------------------------------------:|------------------------------:|-------------------------------------:|------------------------:|-------------------------------:|----------------------:|-----------------------------:|----------------------------------:|-----------------------------------------:|
| wth_0.520   | 0.852505 |        0.852505 |         0.801765 |        0.786293 |         0.954187 |               0.793878 |               -258.474 |                           0 |                        0.267965 |                               0.24954  |                       14.7028 |                              78.8278 |                 54.8685 |                        315.893 |             0.0122868 |                     0.151924 |                        0.00953056 |                                 0.151924 |
| shaped_base | 1        |        1        |         1        |        1        |         1        |               1        |               -467.882 |                           0 |                        0.249537 |                               0.231663 |                       17.2466 |                              98.3178 |                 69.1145 |                        424.4   |             0.0156262 |                     0.159218 |                        0.00953056 |                                 0.159218 |

## Live radial-channel burden by stage
### abs_p_l

| case        |   entry_precatch |   catch_rematch |   held_carry |   release_shift_fade |   post_release_buffer |   reset_decompression |
|:------------|-----------------:|----------------:|-------------:|---------------------:|----------------------:|----------------------:|
| shaped_base |                0 |         15.8603 |            0 |              1.38635 |                     0 |                     0 |
| wth_0.520   |                0 |         13.5563 |            0 |              1.14654 |                     0 |                     0 |
| wth_0.540   |                0 |         13.2302 |            0 |              1.11818 |                     0 |                     0 |
| wth_0.550   |                0 |         13.0662 |            0 |              1.1042  |                     0 |                     0 |
| wth_0.565   |                0 |         12.8195 |            0 |              1.08351 |                     0 |                     0 |
| wth_0.569   |                0 |         12.7538 |            0 |              1.07805 |                     0 |                     0 |
| wth_0.570   |                0 |         12.7373 |            0 |              1.07669 |                     0 |                     0 |

### neg_Tkk_radial

| case        |   entry_precatch |   catch_rematch |   held_carry |   release_shift_fade |   post_release_buffer |   reset_decompression |
|:------------|-----------------:|----------------:|-------------:|---------------------:|----------------------:|----------------------:|
| shaped_base |                0 |         87.7455 |            0 |             10.5723  |                     0 |                     0 |
| wth_0.520   |                0 |         70.3554 |            0 |              8.47232 |                     0 |                     0 |
| wth_0.540   |                0 |         67.8429 |            0 |              8.21623 |                     0 |                     0 |
| wth_0.550   |                0 |         66.5816 |            0 |              8.08989 |                     0 |                     0 |
| wth_0.565   |                0 |         64.6908 |            0 |              7.9029  |                     0 |                     0 |
| wth_0.569   |                0 |         64.1877 |            0 |              7.85359 |                     0 |                     0 |
| wth_0.570   |                0 |         64.0621 |            0 |              7.8413  |                     0 |                     0 |

## Safety

| case        |   live_points |   max_packet_norm_live |   min_packet_norm_live |   positive_packet_norm_live |
|:------------|--------------:|-----------------------:|-----------------------:|----------------------------:|
| shaped_base |           260 |               -467.882 |                -323767 |                           0 |
| wth_0.520   |           260 |               -258.474 |                -212452 |                           0 |
| wth_0.540   |           260 |               4276.14  |                -197685 |                           1 |
| wth_0.550   |           260 |               8795.9   |                -190369 |                           1 |
| wth_0.565   |           260 |              15119.3   |                -179812 |                           1 |
| wth_0.569   |           260 |              16714.1   |                -177030 |                           1 |
| wth_0.570   |           260 |              17106.8   |                -176336 |                           2 |

## Top live packet norm points

| case      |     s |         l | stage              | region            |   packet_norm |
|:----------|------:|----------:|:-------------------|:------------------|--------------:|
| wth_0.570 | -0.35 | -0.7      | catch_rematch      | packet_in_support |     17106.8   |
| wth_0.569 | -0.35 | -0.7      | catch_rematch      | packet_in_support |     16714.1   |
| wth_0.565 | -0.35 | -0.7      | catch_rematch      | packet_in_support |     15119.3   |
| wth_0.550 | -0.35 | -0.7      | catch_rematch      | packet_in_support |      8795.9   |
| wth_0.540 | -0.35 | -0.7      | catch_rematch      | packet_in_support |      4276.14  |
| wth_0.570 | -0.35 |  0        | catch_rematch      | packet_in_support |       237.172 |
| wth_0.569 | -0.35 |  0        | catch_rematch      | packet_in_support |      -189.836 |
| wth_0.570 |  1.05 |  1.32222  | release_shift_fade | packet_in_support |      -224.647 |
| wth_0.569 |  1.05 |  1.32222  | release_shift_fade | packet_in_support |      -225.245 |
| wth_0.565 |  1.05 |  1.32222  | release_shift_fade | packet_in_support |      -227.668 |
| wth_0.550 |  1.05 |  1.32222  | release_shift_fade | packet_in_support |      -237.184 |
| wth_0.540 |  1.05 |  1.32222  | release_shift_fade | packet_in_support |      -243.929 |
| wth_0.520 |  1.05 |  1.32222  | release_shift_fade | packet_in_support |      -258.474 |
| wth_0.570 |  1.05 |  1.24444  | release_shift_fade | packet_in_support |      -289.755 |
| wth_0.569 |  1.05 |  1.24444  | release_shift_fade | packet_in_support |      -290.54  |
| wth_0.565 |  1.05 |  1.24444  | release_shift_fade | packet_in_support |      -293.719 |
| wth_0.550 |  1.05 |  1.24444  | release_shift_fade | packet_in_support |      -306.163 |
| wth_0.570 |  1    |  1.32222  | release_shift_fade | packet_in_support |      -310.831 |
| wth_0.569 |  1    |  1.32222  | release_shift_fade | packet_in_support |      -311.706 |
| wth_0.540 |  1.05 |  1.24444  | release_shift_fade | packet_in_support |      -314.943 |
| wth_0.565 |  1    |  1.32222  | release_shift_fade | packet_in_support |      -315.251 |
| wth_0.550 |  1    |  1.32222  | release_shift_fade | packet_in_support |      -329.197 |
| wth_0.520 |  1.05 |  1.24444  | release_shift_fade | packet_in_support |      -333.757 |
| wth_0.540 |  1    |  1.32222  | release_shift_fade | packet_in_support |      -339.102 |
| wth_0.570 |  1.05 |  1.16667  | release_shift_fade | packet_in_support |      -358.053 |
| wth_0.569 |  1.05 |  1.16667  | release_shift_fade | packet_in_support |      -359.014 |
| wth_0.520 |  1    |  1.32222  | release_shift_fade | packet_in_support |      -360.512 |
| wth_0.565 |  1.05 |  1.16667  | release_shift_fade | packet_in_support |      -362.899 |
| wth_0.550 |  1.05 |  1.16667  | release_shift_fade | packet_in_support |      -378.05  |
| wth_0.540 |  1.05 |  1.16667  | release_shift_fade | packet_in_support |      -388.681 |
| wth_0.570 |  1    |  1.24444  | release_shift_fade | packet_in_support |      -406.837 |
| wth_0.569 |  1    |  1.24444  | release_shift_fade | packet_in_support |      -408.004 |
| wth_0.520 |  1.05 |  1.16667  | release_shift_fade | packet_in_support |      -411.294 |
| wth_0.565 |  1    |  1.24444  | release_shift_fade | packet_in_support |      -412.724 |
| wth_0.570 |  1.05 |  1.08889  | release_shift_fade | packet_in_support |      -422.93  |
| wth_0.569 |  1.05 |  1.08889  | release_shift_fade | packet_in_support |      -424.033 |
| wth_0.565 |  1.05 |  1.08889  | release_shift_fade | packet_in_support |      -428.489 |
| wth_0.550 |  1    |  1.24444  | release_shift_fade | packet_in_support |      -431.234 |
| wth_0.540 |  1    |  1.24444  | release_shift_fade | packet_in_support |      -444.32  |
| wth_0.550 |  1.05 |  1.08889  | release_shift_fade | packet_in_support |      -445.788 |
| wth_0.540 |  1.05 |  1.08889  | release_shift_fade | packet_in_support |      -457.856 |
| wth_0.520 |  1    |  1.24444  | release_shift_fade | packet_in_support |      -472.431 |
| wth_0.570 |  1.05 |  1.01111  | release_shift_fade | packet_in_support |      -477.609 |
| wth_0.569 |  1.05 |  1.01111  | release_shift_fade | packet_in_support |      -478.806 |
| wth_0.520 |  1.05 |  1.08889  | release_shift_fade | packet_in_support |      -483.324 |
| wth_0.565 |  1.05 |  1.01111  | release_shift_fade | packet_in_support |      -483.632 |
| wth_0.550 |  1.05 |  1.01111  | release_shift_fade | packet_in_support |      -502.288 |
| wth_0.570 |  1    |  1.16667  | release_shift_fade | packet_in_support |      -508.823 |
| wth_0.569 |  1    |  1.16667  | release_shift_fade | packet_in_support |      -510.267 |
| wth_0.540 |  1.05 |  1.01111  | release_shift_fade | packet_in_support |      -515.224 |
| wth_0.565 |  1    |  1.16667  | release_shift_fade | packet_in_support |      -516.107 |
| wth_0.565 |  1.05 |  0.933333 | release_shift_fade | packet_in_support |      -524.246 |
| wth_0.550 |  1    |  1.16667  | release_shift_fade | packet_in_support |      -538.917 |
| wth_0.520 |  1.05 |  1.01111  | release_shift_fade | packet_in_support |      -542.31  |
| wth_0.550 |  1.05 |  0.933333 | release_shift_fade | packet_in_support |      -543.43  |
| wth_0.540 |  1    |  1.16667  | release_shift_fade | packet_in_support |      -554.954 |
| wth_0.540 |  1.05 |  0.933333 | release_shift_fade | packet_in_support |      -556.653 |
| wth_0.520 |  1.05 |  0.933333 | release_shift_fade | packet_in_support |      -584.132 |
| wth_0.520 |  1    |  1.16667  | release_shift_fade | packet_in_support |      -589.149 |
| wth_0.520 |  1.05 |  0.855556 | release_shift_fade | packet_in_support |      -609.7   |

## Interpretation

The high-resolution check did **not** validate the earlier `w_th = 0.569` near-boundary promotion. The finer grid found positive live packet-norm points not only at `0.570`, but also at `0.569`, `0.565`, `0.550`, and `0.540`. The previously reported safety cliff was therefore under-resolved and moved substantially downward once the live worldtube was sampled more densely.

The useful pressure trend still survives: larger `w_th` consistently lowers live radial pressure and live radial-null burden. The problem is that the same widening also pushes the packet toward packet-norm failure. On this grid, the best widened case that remains safe is `w_th = 0.520`. It reduces live `p_l` to about `85.4%` of shaped baseline and live radial `Tkk` to about `80.4%` of shaped baseline, while keeping zero positive live packet-norm points.

Implication: radial support-edge widening is still a valid `p_l` lever, but the usable window is narrower than the low-resolution run implied. The promotable branch should be revised from `w_th = 0.569` down to a conservative `w_th = 0.520`, and the next test should combine this conservative widening with a packet-safety compensator rather than pushing `w_th` alone.

The design lesson changes from “safety cliff near 0.570” to “uniform radial widening helps pressure but rapidly eats packet safety margin.”