# Active Rail Tuned Candidate V-Sweep Findings

Scope: V-sweep for the shaped-catch + radial-soft + lapse-cushion branch. This remains a prescribed-geometry finite-difference Einstein-source ledger plus fast packet-norm scans; it is not a matter model or constraint solve.

## Cases

- shaped baseline: locked-lead minimum-jerk catch, `w_th = 0.35`, `eta_N = 1.00`
- conservative fallback: `w_th = 0.565`, `eta_N = 2.00`
- tuned candidate: `w_th = 0.569`, `eta_N = 2.00`
- cliff comparator: `w_th = 0.570`, `eta_N = 2.00`

## High-resolution source-ledger results

|   V | variant                   | case                          |   live_packet_burden__abs_p_l_ratio_vs_V_base |   live_packet_burden__neg_Tkk_radial_ratio_vs_V_base |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |   point_peak__abs_p_l |   point_peak__neg_Tkk_radial |
|----:|:--------------------------|:------------------------------|----------------------------------------------:|-----------------------------------------------------:|-----------------------:|----------------------------:|------------------------------:|-------------------------------------:|--------------------------------:|---------------------------------------:|----------------------:|-----------------------------:|
|   2 | cliff_w0570_eta200        | V2_cliff_w0570_eta200         |                                      0.800971 |                                             0.772064 |               -250.665 |                           0 |                       13.814  |                              42.1452 |                        0.270597 |                               0.150088 |             0.0115472 |                     0.100088 |
|   2 | shaped_base               | V2_shaped_base                |                                      1        |                                             1        |               -467.882 |                           0 |                       17.2466 |                              54.5877 |                        0.249536 |                               0.146768 |             0.0156262 |                     0.101415 |
|   2 | tuned_w0569_eta200        | V2_tuned_w0569_eta200         |                                      0.802003 |                                             0.773331 |               -251.331 |                           0 |                       13.8318 |                              42.2143 |                        0.270555 |                               0.150045 |             0.0115534 |                     0.100128 |
|   5 | cliff_w0570_eta200        | V5_cliff_w0570_eta200         |                                      0.800971 |                                             0.755191 |               -250.665 |                           0 |                       13.814  |                              51.9656 |                        0.270597 |                               0.177553 |             0.0115472 |                     0.100088 |
|   5 | shaped_base               | V5_shaped_base                |                                      1        |                                             1        |               -467.882 |                           0 |                       17.2466 |                              68.8112 |                        0.249536 |                               0.176776 |             0.0156262 |                     0.101415 |
|   5 | tuned_w0569_eta200        | V5_tuned_w0569_eta200         |                                      0.802003 |                                             0.756517 |               -251.331 |                           0 |                       13.8318 |                              52.0568 |                        0.270555 |                               0.17752  |             0.0115534 |                     0.100128 |
|  10 | cliff_w0570_eta200        | V10_cliff_w0570_eta200        |                                      0.800971 |                                             0.734779 |                228.109 |                           1 |                       13.814  |                              72.2419 |                        0.270598 |                               0.228122 |             0.0115472 |                     0.142597 |
|  10 | conservative_w0565_eta200 | V10_conservative_w0565_eta200 |                                      0.806134 |                                             0.74178  |               -254.03  |                           0 |                       13.9031 |                              72.9302 |                        0.270383 |                               0.228046 |             0.011579  |                     0.143039 |
|  10 | shaped_base               | V10_shaped_base               |                                      1        |                                             1        |               -467.882 |                           0 |                       17.2466 |                              98.3178 |                        0.249537 |                               0.231663 |             0.0156262 |                     0.159218 |
|  10 | tuned_w0569_eta200        | V10_tuned_w0569_eta200        |                                      0.802004 |                                             0.736178 |               -198.925 |                           0 |                       13.8318 |                              72.3794 |                        0.270556 |                               0.228108 |             0.0115534 |                     0.142686 |
|  11 | tuned_w0569_eta200        | V11_tuned_w0569_eta200        |                                    nan        |                                           nan        |              42605.3   |                           2 |                       13.8318 |                              76.9481 |                        0.270556 |                               0.238476 |             0.0115534 |                     0.155578 |
|  12 | tuned_w0569_eta200        | V12_tuned_w0569_eta200        |                                    nan        |                                           nan        |              89475.7   |                           3 |                       13.8319 |                              81.6724 |                        0.270556 |                               0.248848 |             0.0115534 |                     0.168254 |
|  13 | tuned_w0569_eta200        | V13_tuned_w0569_eta200        |                                    nan        |                                           nan        |             140412     |                           3 |                       13.8319 |                              86.5502 |                        0.270556 |                               0.259208 |             0.0115534 |                     0.180655 |
|  14 | tuned_w0569_eta200        | V14_tuned_w0569_eta200        |                                    nan        |                                           nan        |             195415     |                           5 |                       13.8319 |                              91.5794 |                        0.270556 |                               0.269537 |             0.0115534 |                     0.192717 |
|  15 | cliff_w0570_eta200        | V15_cliff_w0570_eta200        |                                      0.800972 |                                             0.721757 |             254699     |                           5 |                       13.8141 |                              96.564  |                        0.270598 |                               0.279817 |             0.0115472 |                     0.20426  |
|  15 | shaped_base               | V15_shaped_base               |                                      1        |                                             1        |             182340     |                           3 |                       17.2467 |                             133.79   |                        0.249537 |                               0.287038 |             0.0156262 |                     0.222329 |
|  15 | tuned_w0569_eta200        | V15_tuned_w0569_eta200        |                                      0.802004 |                                             0.723205 |             254483     |                           5 |                       13.8319 |                              96.7577 |                        0.270556 |                               0.27982  |             0.0115534 |                     0.204374 |

## High-resolution safety

|   V | variant                   | case                          |   live_points |   max_packet_norm_live |   min_packet_norm_live |   positive_packet_norm_live |
|----:|:--------------------------|:------------------------------|--------------:|-----------------------:|-----------------------:|----------------------------:|
|   2 | cliff_w0570_eta200        | V2_cliff_w0570_eta200         |           260 |               -250.665 |                -201720 |                           0 |
|   2 | shaped_base               | V2_shaped_base                |           260 |               -467.882 |                -331511 |                           0 |
|   2 | tuned_w0569_eta200        | V2_tuned_w0569_eta200         |           260 |               -251.331 |                -202322 |                           0 |
|   5 | cliff_w0570_eta200        | V5_cliff_w0570_eta200         |           260 |               -250.665 |                -195592 |                           0 |
|   5 | shaped_base               | V5_shaped_base                |           260 |               -467.882 |                -327959 |                           0 |
|   5 | tuned_w0569_eta200        | V5_tuned_w0569_eta200         |           260 |               -251.331 |                -196216 |                           0 |
|  10 | cliff_w0570_eta200        | V10_cliff_w0570_eta200        |           260 |                228.109 |                -176368 |                           1 |
|  10 | conservative_w0565_eta200 | V10_conservative_w0565_eta200 |           260 |               -254.03  |                -179844 |                           0 |
|  10 | shaped_base               | V10_shaped_base               |           260 |               -467.882 |                -323767 |                           0 |
|  10 | tuned_w0569_eta200        | V10_tuned_w0569_eta200        |           260 |               -198.925 |                -177062 |                           0 |
|  11 | tuned_w0569_eta200        | V11_tuned_w0569_eta200        |           260 |              42605.3   |                -171964 |                           2 |
|  12 | tuned_w0569_eta200        | V12_tuned_w0569_eta200        |           260 |              89475.7   |                -166379 |                           3 |
|  13 | tuned_w0569_eta200        | V13_tuned_w0569_eta200        |           260 |             140412     |                -160446 |                           3 |
|  14 | tuned_w0569_eta200        | V14_tuned_w0569_eta200        |           260 |             195415     |                -154504 |                           5 |
|  15 | cliff_w0570_eta200        | V15_cliff_w0570_eta200        |           260 |             254699     |                -147341 |                           5 |
|  15 | shaped_base               | V15_shaped_base               |           260 |             182340     |                -318078 |                           3 |
|  15 | tuned_w0569_eta200        | V15_tuned_w0569_eta200        |           260 |             254483     |                -148121 |                           5 |

## Fast packet-norm threshold scans

Fine scan near `V = 10` on a `101 x 181` packet-norm grid:

| variant                   |   last_safe_V |   first_unsafe_V |   max_norm_at_10 |
|:--------------------------|--------------:|-----------------:|-----------------:|
| conservative_w0565_eta200 |         10.04 |            10.05 |         -209.127 |
| safe_w0520_eta100         |         10.21 |           nan    |         -216.839 |
| shaped_base               |         10.21 |           nan    |         -396.474 |
| tuned_eta220              |         10    |            10.01 |         -200.743 |
| tuned_w0569_eta200        |         10    |            10.01 |         -198.925 |

Coarser upper-range scan from `V = 10` to `V = 15` in `0.1` steps:

| variant                   |   last_safe_V_step01 |   first_unsafe_V_step01 |
|:--------------------------|---------------------:|------------------------:|
| conservative_w0565_eta200 |                 10   |                    10.1 |
| safe_w0520_eta100         |                 10.5 |                    10.6 |
| shaped_base               |                 12   |                    12.1 |
| tuned_w0569_eta200        |                 10   |                    10.1 |

## Read

The tuned branch is good at `V = 2`, `V = 5`, and the stressed design point `V = 10`. It reduces live `p_l` by about 20% relative to the shaped baseline at the same V, and reduces live negative radial `Tkk` by about 23-28% depending on V.

The upward headroom is extremely thin. The fast packet-norm scan finds the tuned `w_th = 0.569, eta_N = 2.00` candidate safe at exactly `V = 10` but already unsafe by about `V = 10.01` on the finer packet-norm grid. The high-resolution source-ledger checks agree with the pattern: tuned cases at `V = 11`, `12`, `13`, `14`, and `15` show positive live packet-norm points.

The `w_th = 0.570` cliff is not a universal cliff at lower V. It is safe at `V = 2` and `V = 5`, unsafe at `V = 10`, and deeply unsafe by `V = 15`. That means the safety cliff is stress-dependent, not purely a static radial-width artifact.

The shaped baseline has more upward packet-safety headroom than the tuned radial-soft branch, but worse source burden. In the fast scan it remains safe to roughly `V = 12.0` and becomes unsafe around `V = 12.1`. So radial softening and lapse cushioning improved source burden but spent a lot of V headroom.

## Design implication

This branch is a strong `V <= 10` tuned candidate, not a general high-V branch. The knobs work, but they use almost all causal margin at `V = 10`. The next design move should not be more uniform `w_th` pushing. It should be a V-aware or nonuniform radial support shape that preserves the `p_l` reduction while restoring the lost V headroom.

Promotable framing:

```text
R1.75 shaped catch radial-soft lapse-cushion v1
valid as a tuned V=10 candidate
good below V=10
not robust above V=10 without a new safety/headroom mechanism
```