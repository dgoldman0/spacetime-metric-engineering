# Active Rail Tuned Candidate Robustness Check

This bundle tests the R1.75 shaped-catch, radial-softened, lapse-cushioned branch in a local parameter neighborhood. The computation is a point-level prescribed-geometry Einstein-source ledger; it is still a design diagnostic, not a matter model or constraint solve.

## Candidate under test

```text
Rth = 1.75
w_th = 0.569
eta_N = 2.00
w_pass = 0.06
support catch: x = -0.05, w = 0.32, minimum jerk
packet rematch: x = 0.00, w = 0.32, minimum jerk
```

## Main result

The tuned branch survives high-resolution recheck, but the basin is narrow. The system has a real functional knob set, not a wide robust plateau. Lowering `w_th` buys safety margin while sacrificing some source improvement. Increasing the lapse cushion helps, but does not reopen much room beyond the old `w_th ≈ 0.569` boundary. Timing perturbations are dangerous enough that the locked-lead catch should stay close to the discovered values until a separate timing study is done.

## High-resolution decision table

| case                     |     score |   pl_live_ratio |   tkk_live_ratio |   pl_peak_ratio |   tkk_peak_ratio |   infra_pressure_ratio |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |
|:-------------------------|----------:|----------------:|-----------------:|----------------:|-----------------:|-----------------------:|-----------------------:|----------------------------:|------------------------------:|-------------------------------------:|--------------------------------:|---------------------------------------:|
| w0569_eta180             |  0.802003 |        0.802003 |         0.73547  |        0.739359 |         0.902709 |               0.739688 |               -197.108 |                           0 |                       13.8318 |                              72.3099 |                        0.270559 |                               0.232693 |
| same_center_softer       |  0.802003 |        0.802003 |         0.734715 |        0.739359 |         0.882658 |               0.739697 |               -251.331 |                           0 |                       13.8318 |                              72.2356 |                        0.270556 |                               0.227746 |
| earlier_locked_same_lead |  0.802004 |        0.802004 |         0.727684 |        0.739359 |         0.890064 |               0.739697 |               -251.331 |                           0 |                       13.8318 |                              71.5443 |                        0.270556 |                               0.226204 |
| tuned_w0569_eta200       |  0.802004 |        0.802004 |         0.736178 |        0.739359 |         0.896165 |               0.739697 |               -198.925 |                           0 |                       13.8318 |                              72.3794 |                        0.270556 |                               0.228108 |
| tighter_packet_wpass055  |  0.802004 |        0.802004 |         0.740221 |        0.739359 |         0.963785 |               0.739697 |               -198.925 |                           0 |                       13.8318 |                              72.7769 |                        0.270556 |                               0.229106 |
| w0569_eta220             |  0.802004 |        0.802004 |         0.736896 |        0.739359 |         0.889341 |               0.739706 |               -200.743 |                           0 |                       13.8318 |                              72.45   |                        0.270553 |                               0.223503 |
| w0565_eta180             |  0.806134 |        0.806134 |         0.741076 |        0.740998 |         0.904973 |               0.743972 |               -248.535 |                           0 |                       13.9031 |                              72.861  |                        0.270387 |                               0.232635 |
| w0565_eta200             |  0.806134 |        0.806134 |         0.74178  |        0.740998 |         0.89838  |               0.743981 |               -254.03  |                           0 |                       13.9031 |                              72.9302 |                        0.270383 |                               0.228046 |
| w0560_eta180             |  0.8113   |        0.8113   |         0.748094 |        0.746793 |         0.907763 |               0.749364 |               -251.909 |                           0 |                       13.9922 |                              73.551  |                        0.270161 |                               0.232549 |
| w0560_eta200             |  0.8113   |        0.8113   |         0.748794 |        0.746793 |         0.901109 |               0.749373 |               -257.478 |                           0 |                       13.9922 |                              73.6198 |                        0.270158 |                               0.227956 |
| w0550_eta150_existing    |  0.821633 |        0.821633 |         0.761139 |        0.757921 |         0.922856 |               0.760255 |               -250.549 |                           0 |                       14.1704 |                              74.8335 |                        0.269683 |                               0.239192 |
| w0540_eta120_existing    |  0.831956 |        0.831956 |         0.774247 |        0.768317 |         0.937524 |               0.771305 |               -249.339 |                           0 |                       14.3484 |                              76.1223 |                        0.269159 |                               0.245738 |
| shaped_base              |  1        |        1        |         1        |        1        |         1        |               1        |               -467.882 |                           0 |                       17.2466 |                              98.3178 |                        0.249537 |                               0.231663 |
| w0580_eta200_existing    | 10.7907   |        0.790662 |         0.720827 |        0.734464 |         0.889933 |               0.728056 |               4422.9   |                           1 |                       13.6362 |                              70.8702 |                        0.270995 |                               0.228232 |
| w0570_eta200_existing    | 10.801    |        0.800971 |         0.734779 |        0.738968 |         0.895607 |               0.738631 |                228.109 |                           1 |                       13.814  |                              72.2419 |                        0.270598 |                               0.228122 |
| w0570_eta220             | 10.801    |        0.800972 |         0.735498 |        0.738968 |         0.888795 |               0.73864  |                226.296 |                           1 |                       13.814  |                              72.3125 |                        0.270595 |                               0.223518 |
| later_locked_same_lead   | 10.802    |        0.802004 |         0.744737 |        0.739359 |         0.901952 |               0.739697 |               2169.02  |                           1 |                       13.8318 |                              73.2209 |                        0.270556 |                               0.230015 |

## Safe candidates

| case                     |    score |   pl_live_ratio |   tkk_live_ratio |   pl_peak_ratio |   tkk_peak_ratio |   infra_pressure_ratio |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |
|:-------------------------|---------:|----------------:|-----------------:|----------------:|-----------------:|-----------------------:|-----------------------:|----------------------------:|------------------------------:|-------------------------------------:|--------------------------------:|---------------------------------------:|
| w0569_eta180             | 0.802003 |        0.802003 |         0.73547  |        0.739359 |         0.902709 |               0.739688 |               -197.108 |                           0 |                       13.8318 |                              72.3099 |                        0.270559 |                               0.232693 |
| same_center_softer       | 0.802003 |        0.802003 |         0.734715 |        0.739359 |         0.882658 |               0.739697 |               -251.331 |                           0 |                       13.8318 |                              72.2356 |                        0.270556 |                               0.227746 |
| earlier_locked_same_lead | 0.802004 |        0.802004 |         0.727684 |        0.739359 |         0.890064 |               0.739697 |               -251.331 |                           0 |                       13.8318 |                              71.5443 |                        0.270556 |                               0.226204 |
| tuned_w0569_eta200       | 0.802004 |        0.802004 |         0.736178 |        0.739359 |         0.896165 |               0.739697 |               -198.925 |                           0 |                       13.8318 |                              72.3794 |                        0.270556 |                               0.228108 |
| tighter_packet_wpass055  | 0.802004 |        0.802004 |         0.740221 |        0.739359 |         0.963785 |               0.739697 |               -198.925 |                           0 |                       13.8318 |                              72.7769 |                        0.270556 |                               0.229106 |
| w0569_eta220             | 0.802004 |        0.802004 |         0.736896 |        0.739359 |         0.889341 |               0.739706 |               -200.743 |                           0 |                       13.8318 |                              72.45   |                        0.270553 |                               0.223503 |
| w0565_eta180             | 0.806134 |        0.806134 |         0.741076 |        0.740998 |         0.904973 |               0.743972 |               -248.535 |                           0 |                       13.9031 |                              72.861  |                        0.270387 |                               0.232635 |
| w0565_eta200             | 0.806134 |        0.806134 |         0.74178  |        0.740998 |         0.89838  |               0.743981 |               -254.03  |                           0 |                       13.9031 |                              72.9302 |                        0.270383 |                               0.228046 |
| w0560_eta180             | 0.8113   |        0.8113   |         0.748094 |        0.746793 |         0.907763 |               0.749364 |               -251.909 |                           0 |                       13.9922 |                              73.551  |                        0.270161 |                               0.232549 |
| w0560_eta200             | 0.8113   |        0.8113   |         0.748794 |        0.746793 |         0.901109 |               0.749373 |               -257.478 |                           0 |                       13.9922 |                              73.6198 |                        0.270158 |                               0.227956 |
| w0550_eta150_existing    | 0.821633 |        0.821633 |         0.761139 |        0.757921 |         0.922856 |               0.760255 |               -250.549 |                           0 |                       14.1704 |                              74.8335 |                        0.269683 |                               0.239192 |
| w0540_eta120_existing    | 0.831956 |        0.831956 |         0.774247 |        0.768317 |         0.937524 |               0.771305 |               -249.339 |                           0 |                       14.3484 |                              76.1223 |                        0.269159 |                               0.245738 |
| shaped_base              | 1        |        1        |         1        |        1        |         1        |               1        |               -467.882 |                           0 |                       17.2466 |                              98.3178 |                        0.249537 |                               0.231663 |

## Unsafe candidates

| case                   |   score |   pl_live_ratio |   tkk_live_ratio |   pl_peak_ratio |   tkk_peak_ratio |   infra_pressure_ratio |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |
|:-----------------------|--------:|----------------:|-----------------:|----------------:|-----------------:|-----------------------:|-----------------------:|----------------------------:|------------------------------:|-------------------------------------:|--------------------------------:|---------------------------------------:|
| w0580_eta200_existing  | 10.7907 |        0.790662 |         0.720827 |        0.734464 |         0.889933 |               0.728056 |               4422.9   |                           1 |                       13.6362 |                              70.8702 |                        0.270995 |                               0.228232 |
| w0570_eta200_existing  | 10.801  |        0.800971 |         0.734779 |        0.738968 |         0.895607 |               0.738631 |                228.109 |                           1 |                       13.814  |                              72.2419 |                        0.270598 |                               0.228122 |
| w0570_eta220           | 10.801  |        0.800972 |         0.735498 |        0.738968 |         0.888795 |               0.73864  |                226.296 |                           1 |                       13.814  |                              72.3125 |                        0.270595 |                               0.223518 |
| later_locked_same_lead | 10.802  |        0.802004 |         0.744737 |        0.739359 |         0.901952 |               0.739697 |               2169.02  |                           1 |                       13.8318 |                              73.2209 |                        0.270556 |                               0.230015 |

## Convergence check for tuned candidate

| grid   |   pl_live_ratio |   tkk_live_ratio |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |
|:-------|----------------:|-----------------:|-----------------------:|----------------------------:|------------------------------:|-------------------------------------:|--------------------------------:|---------------------------------------:|
| 25x45  |               1 |                1 |               -198.925 |                           0 |                       13.8019 |                              71.4351 |                        0.264783 |                               0.221226 |
| 33x59  |               1 |                1 |               -198.925 |                           0 |                       13.988  |                              72.5353 |                        0.271614 |                               0.227126 |
| 41x73  |               1 |                1 |               -198.925 |                           0 |                       13.8318 |                              72.3794 |                        0.270556 |                               0.228108 |

## Read

The knob decomposition still holds: shaped catch controls radial-null exposure, radial support widening reduces `p_l`, and the lapse cushion protects packet safety. The robustness check adds one constraint: the useful branch is a thin tuned ridge. `w_th = 0.569, eta_N = 2.00` is usable on the tested grid, but it is close to a safety cliff. A conservative fallback around `w_th = 0.565, eta_N = 2.00` gives less improvement but more causal margin.

The timing perturbations did not reveal a broader escape route. Earlier/later locked timing changes move the exposure pattern but do not obviously make the branch more robust. The best next architectural improvement is therefore not more timing drift; it is a nonuniform radial support shape that preserves the pressure reduction of wide `w_th` while reducing inward causal leakage into the early live packet corridor.

## Updated design lesson

```text
Tkk wants shaped, locked-lead catch timing.
p_l wants radial support-edge widening.
packet safety wants a lapse cushion.
robustness wants nonuniform radial support, because uniform w_th has a cliff.
```