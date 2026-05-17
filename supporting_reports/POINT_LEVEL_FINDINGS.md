# Point-level lifecycle result

Main run: V=10, 41x61 grid for freeze-like, R1.75, and R2.0 comparison. Refined R1.75 check: 61x91 grid.

## Key global comparison, 41x61 volume-weighted

| case                | channel        |   total_burden |   live_packet_burden | live_fraction   |   live_peak |   global_peak |
|:--------------------|:---------------|---------------:|---------------------:|:----------------|------------:|--------------:|
| freeze_like_minjerk | neg_Tkk_radial |      342.6     |          140.6       | 41.0%           |   0.1757    |      0.2619   |
| freeze_like_minjerk | abs_p_l        |       58.98    |           17.9       | 30.3%           |   0.02723   |      0.02928  |
| freeze_like_minjerk | abs_pOmega     |        5.865   |            0.07499   | 1.3%            |   0.9807    |      1.003    |
| freeze_like_minjerk | abs_j_l        |        0.07086 |            0.00146   | 2.1%            |   0.001019  |      0.01036  |
| freeze_like_minjerk | neg_rho_euler  |        0.475   |            0.0008782 | 0.2%            |   0.02381   |      0.02405  |
| freeze_like_minjerk | neg_rho_packet |        0.5004  |            0.001762  | 0.4%            |   0.03802   |      0.1502   |
| R1p75_quarantine    | neg_Tkk_radial |      458       |          122.5       | 26.7%           |   0.1164    |      0.1647   |
| R1p75_quarantine    | abs_p_l        |       69.12    |           17.21      | 24.9%           |   0.009531  |      0.01565  |
| R1p75_quarantine    | abs_pOmega     |        4.092   |            0.007595  | 0.2%            |   9.428e-05 |      0.1682   |
| R1p75_quarantine    | abs_j_l        |        0.2006  |            0.001936  | 1.0%            |   8.9e-05   |      0.007957 |
| R1p75_quarantine    | neg_rho_euler  |        0.39    |            0         | 0.0%            |   0         |      0.01621  |
| R1p75_quarantine    | neg_rho_packet |        0.6095  |            0         | 0.0%            |   0         |      0.7239   |
| R2p0_quarantine     | neg_Tkk_radial |      558.9     |          126         | 22.5%           |   0.08918   |      0.1313   |
| R2p0_quarantine     | abs_p_l        |       83.04    |           17.65      | 21.3%           |   0.007297  |      0.01303  |
| R2p0_quarantine     | abs_pOmega     |        4.972   |            0.01039   | 0.2%            |   9.479e-05 |      0.163    |
| R2p0_quarantine     | abs_j_l        |        0.2337  |            0.001851  | 0.8%            |   4.673e-05 |      0.006664 |
| R2p0_quarantine     | neg_rho_euler  |        0.3732  |            0         | 0.0%            |   0         |      0.01398  |
| R2p0_quarantine     | neg_rho_packet |        0.4375  |            0         | 0.0%            |   0         |      0.08951  |

## R1.75 refined 61x91 reading

| channel        |   total_burden |   live_packet_burden | live_fraction   |   live_peak |   global_peak |
|:---------------|---------------:|---------------------:|:----------------|------------:|--------------:|
| neg_Tkk_radial |       454.1    |           122.6      | 27.0%           |   0.1484    |       0.1682  |
| abs_p_l        |        68.42   |            17.1      | 25.0%           |   0.009532  |       0.01565 |
| abs_pOmega     |         4.049  |             0.007479 | 0.2%            |   9.428e-05 |       0.1682  |
| abs_j_l        |         0.1969 |             0.001785 | 0.9%            |   8.086e-05 |       0.00802 |
| neg_rho_euler  |         0.3831 |             0        | 0.0%            |   0         |       0.01621 |
| neg_rho_packet |         0.6289 |             0        | 0.0%            |   0         |       0.7239  |

## R1.75 refined stage breakdown

### neg_Tkk_radial

| stage               |   total_burden |   live_packet_burden | live_packet_fraction   |   point_peak |   live_packet_point_peak |
|:--------------------|---------------:|---------------------:|:-----------------------|-------------:|-------------------------:|
| entry_precatch      |        97.89   |                40.34 | 41.2%                  |      0.1682  |                  0.1484  |
| catch_rematch       |       267.7    |                65.06 | 24.3%                  |      0.1324  |                  0.1324  |
| release_shift_fade  |        80.79   |                17.16 | 21.2%                  |      0.1009  |                  0.08461 |
| post_release_buffer |         6.717  |                 0    | 0.0%                   |      0.08696 |                  0       |
| reset_decompression |         0.9582 |                 0    | 0.0%                   |      0.07084 |                  0       |

### abs_p_l

| stage               |   total_burden |   live_packet_burden | live_packet_fraction   |   point_peak |   live_packet_point_peak |
|:--------------------|---------------:|---------------------:|:-----------------------|-------------:|-------------------------:|
| entry_precatch      |        16.34   |                4.326 | 26.5%                  |      0.01565 |                 0.009523 |
| catch_rematch       |        39.63   |               10.2   | 25.7%                  |      0.01563 |                 0.009532 |
| release_shift_fade  |        11.01   |                2.572 | 23.4%                  |      0.01552 |                 0.009443 |
| post_release_buffer |         1.224  |                0     | 0.0%                   |      0.01373 |                 0        |
| reset_decompression |         0.2186 |                0     | 0.0%                   |      0.01044 |                 0        |

### abs_pOmega

| stage               |   total_burden |   live_packet_burden | live_packet_fraction   |   point_peak |   live_packet_point_peak |
|:--------------------|---------------:|---------------------:|:-----------------------|-------------:|-------------------------:|
| entry_precatch      |         0.4393 |            0.0009298 | 0.2%                   |       0.167  |                1.432e-05 |
| catch_rematch       |         1.408  |            0.002395  | 0.2%                   |       0.1682 |                1.662e-05 |
| release_shift_fade  |         1.165  |            0.004154  | 0.4%                   |       0.1652 |                9.428e-05 |
| post_release_buffer |         0.5756 |            0         | 0.0%                   |       0.1375 |                0         |
| reset_decompression |         0.4616 |            0         | 0.0%                   |       0.1034 |                0         |

### abs_j_l

| stage               |   total_burden |   live_packet_burden | live_packet_fraction   |   point_peak |   live_packet_point_peak |
|:--------------------|---------------:|---------------------:|:-----------------------|-------------:|-------------------------:|
| entry_precatch      |      0.0002995 |            2.532e-05 | 8.5%                   |    0.0001429 |                6.647e-08 |
| catch_rematch       |      0.01101   |            9.941e-05 | 0.9%                   |    0.00156   |                4.28e-07  |
| release_shift_fade  |      0.04126   |            0.001661  | 4.0%                   |    0.003659  |                8.086e-05 |
| post_release_buffer |      0.06614   |            0         | 0.0%                   |    0.005622  |                0         |
| reset_decompression |      0.07819   |            0         | 0.0%                   |    0.00802   |                0         |

### neg_rho_euler

| stage               |   total_burden |   live_packet_burden | live_packet_fraction   |   point_peak |   live_packet_point_peak |
|:--------------------|---------------:|---------------------:|:-----------------------|-------------:|-------------------------:|
| entry_precatch      |        0.04084 |                    0 | 0.0%                   |      0.01621 |                        0 |
| catch_rematch       |        0.1283  |                    0 | 0.0%                   |      0.01621 |                        0 |
| release_shift_fade  |        0.1171  |                    0 | 0.0%                   |      0.01599 |                        0 |
| post_release_buffer |        0.06385 |                    0 | 0.0%                   |      0.01469 |                        0 |
| reset_decompression |        0.03305 |                    0 | 0.0%                   |      0.01278 |                        0 |

### neg_rho_packet

| stage               |   total_burden |   live_packet_burden | live_packet_fraction   |   point_peak |   live_packet_point_peak |
|:--------------------|---------------:|---------------------:|:-----------------------|-------------:|-------------------------:|
| entry_precatch      |        0       |                    0 | nan                    |      0       |                        0 |
| catch_rematch       |        0.2825  |                    0 | 0.0%                   |      0.7239  |                        0 |
| release_shift_fade  |        0.1951  |                    0 | 0.0%                   |      0.03702 |                        0 |
| post_release_buffer |        0.09949 |                    0 | 0.0%                   |      0.02698 |                        0 |
| reset_decompression |        0.05172 |                    0 | 0.0%                   |      0.02602 |                        0 |

## Interpretation

- R1.75 preserves the quarantine improvement seen in the earlier summary table: live radial null fraction is about 27%, and live radial pressure fraction is about 25%.
- The remaining live radial-null burden is not a reset/decompression artifact. It is concentrated in entry/pre-catch and catch/rematch, with a smaller contribution during shift fade/release.
- Eulerian and packet-comoving negative density are successfully kept out of the live packet in the R1.75 run at this resolution.
- Angular pressure is strongly quarantined away from the live packet; the live fraction is below 0.2%.
- R2.0 improves the radial-null and radial-pressure fractions, but by making a larger infrastructure ledger. This reproduces the design tradeoff from the report.
