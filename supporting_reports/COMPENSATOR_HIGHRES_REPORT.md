# Packet-Safety Compensator High-Resolution Check

Grid: `41 x 73` per case. This is a finite-difference prescribed-geometry source ledger, not a matter model or constraint solve.

## Main result

A lapse cushion works as a packet-safety compensator. It does not directly make the radial-pressure source cheaper; instead it buys causal margin so the stronger radial support-edge widening can be used safely.

The best safe tested branch is:

```text
R1.75 shaped catch + radial-soft + lapse-cushion v1
w_th = 0.569
eta_N = 2.00
w_pass = 0.06
support catch: x = -0.05, w = 0.32, minimum jerk
packet rematch: x = 0.00, w = 0.32, minimum jerk
```

It remains packet-safe on this grid, with max live packet norm `-198.925`, and gives live `p_l` burden at `80.2%` of shaped baseline and live radial `Tkk` burden at `73.6%` of shaped baseline.

## Decision table

| case           |   score |   pl_live_ratio |   tkk_live_ratio |   pl_peak_ratio |   tkk_peak_ratio |   infra_pressure_ratio |   max_packet_norm_live |   positive_packet_norm_live |   live_packet_burden__abs_p_l |   live_packet_burden__neg_Tkk_radial |   live_packet_fraction__abs_p_l |   live_packet_fraction__neg_Tkk_radial |
|:---------------|--------:|----------------:|-----------------:|----------------:|-----------------:|-----------------------:|-----------------------:|----------------------------:|------------------------------:|-------------------------------------:|--------------------------------:|---------------------------------------:|
| shaped_base    |  1      |          1      |           1      |          1      |           1      |                 1      |                 -467.9 |                           0 |                         17.25 |                                98.32 |                          0.2495 |                                 0.2317 |
| wth_0.520      |  0.8525 |          0.8525 |           0.8018 |          0.7863 |           0.9542 |                 0.7939 |                 -258.5 |                           0 |                         14.7  |                                78.83 |                          0.268  |                                 0.2495 |
| wth_0.540      | 10.83   |          0.832  |           0.7736 |          0.7683 |           0.9434 |                 0.7713 |                 4276   |                           1 |                         14.35 |                                76.06 |                          0.2692 |                                 0.2502 |
| wth_0540_eta12 |  0.832  |          0.832  |           0.7742 |          0.7683 |           0.9375 |                 0.7713 |                 -249.3 |                           0 |                         14.35 |                                76.12 |                          0.2692 |                                 0.2457 |
| wth_0.550      | 10.82   |          0.8216 |           0.7595 |          0.7579 |           0.9376 |                 0.7602 |                 8796   |                           1 |                         14.17 |                                74.67 |                          0.2697 |                                 0.2505 |
| wth_0550_eta15 |  0.8216 |          0.8216 |           0.7611 |          0.7579 |           0.9229 |                 0.7603 |                 -250.5 |                           0 |                         14.17 |                                74.83 |                          0.2697 |                                 0.2392 |
| wth_0.565      | 10.81   |          0.8061 |           0.7384 |          0.741  |           0.9287 |                 0.7439 |                15120   |                           1 |                         13.9  |                                72.59 |                          0.2704 |                                 0.2507 |
| wth_0565_eta20 |  0.8061 |          0.8061 |           0.7418 |          0.741  |           0.8984 |                 0.744  |                 -254   |                           0 |                         13.9  |                                72.93 |                          0.2704 |                                 0.228  |
| wth_0.569      | 10.8    |          0.802  |           0.7327 |          0.7394 |           0.9263 |                 0.7397 |                16710   |                           1 |                         13.83 |                                72.04 |                          0.2706 |                                 0.2508 |
| wth_0569_eta20 |  0.802  |          0.802  |           0.7362 |          0.7394 |           0.8962 |                 0.7397 |                 -198.9 |                           0 |                         13.83 |                                72.38 |                          0.2706 |                                 0.2281 |
| wth_0.570      | 10.8    |          0.801  |           0.7313 |          0.739  |           0.9257 |                 0.7386 |                17110   |                           2 |                         13.81 |                                71.9  |                          0.2706 |                                 0.2508 |
| wth_0570_eta20 | 10.8    |          0.801  |           0.7348 |          0.739  |           0.8956 |                 0.7386 |                  228.1 |                           1 |                         13.81 |                                72.24 |                          0.2706 |                                 0.2281 |
| wth_0580_eta20 | 10.79   |          0.7907 |           0.7208 |          0.7345 |           0.8899 |                 0.7281 |                 4423   |                           1 |                         13.64 |                                70.87 |                          0.271  |                                 0.2282 |

## Safety boundary

Raw radial widening failed already at `w_th = 0.540` on the prior high-resolution check. With `eta_N = 2.00`, the safe boundary moves to about `w_th = 0.569`; `w_th = 0.570` still fails, and `w_th = 0.580` fails clearly.

This means the compensator is real, but the design remains close to a cliff. The lapse cushion buys margin, not unlimited room.

## Interpretation

The result strengthens the design decomposition:

```text
Tkk burden: helped by shaped, locked-lead catch timing
p_l burden: helped by radial support-edge widening
packet safety: protected by lapse cushion
```

The important subtlety is that increasing `eta_N` barely changes the live `p_l` burden at a fixed `w_th`. For example, raw `w_th = 0.565` and `w_th = 0.565, eta_N = 2.00` have almost the same `p_l` burden; the latter is safe while the former fails. The lapse cushion is therefore a safety compensator, not the source-reduction knob itself.

## Stage burden for radial channels

### abs_p_l

| case           |   entry_precatch |   catch_rematch |   held_carry |   release_shift_fade |   post_release_buffer |   reset_decompression |
|:---------------|-----------------:|----------------:|-------------:|---------------------:|----------------------:|----------------------:|
| shaped_base    |                0 |         15.8603 |            0 |              1.38635 |                     0 |                     0 |
| wth_0.520      |                0 |         13.5563 |            0 |              1.14654 |                     0 |                     0 |
| wth_0.540      |                0 |         13.2302 |            0 |              1.11818 |                     0 |                     0 |
| wth_0540_eta12 |                0 |         13.2302 |            0 |              1.11819 |                     0 |                     0 |
| wth_0.550      |                0 |         13.0662 |            0 |              1.1042  |                     0 |                     0 |
| wth_0550_eta15 |                0 |         13.0662 |            0 |              1.10422 |                     0 |                     0 |
| wth_0.565      |                0 |         12.8195 |            0 |              1.08351 |                     0 |                     0 |
| wth_0565_eta20 |                0 |         12.8195 |            0 |              1.08355 |                     0 |                     0 |
| wth_0.569      |                0 |         12.7538 |            0 |              1.07805 |                     0 |                     0 |
| wth_0569_eta20 |                0 |         12.7537 |            0 |              1.0781  |                     0 |                     0 |
| wth_0.570      |                0 |         12.7373 |            0 |              1.07669 |                     0 |                     0 |
| wth_0570_eta20 |                0 |         12.7373 |            0 |              1.07674 |                     0 |                     0 |
| wth_0580_eta20 |                0 |         12.573  |            0 |              1.06323 |                     0 |                     0 |

### neg_Tkk_radial

| case           |   entry_precatch |   catch_rematch |   held_carry |   release_shift_fade |   post_release_buffer |   reset_decompression |
|:---------------|-----------------:|----------------:|-------------:|---------------------:|----------------------:|----------------------:|
| shaped_base    |                0 |         87.7455 |            0 |             10.5723  |                     0 |                     0 |
| wth_0.520      |                0 |         70.3554 |            0 |              8.47232 |                     0 |                     0 |
| wth_0.540      |                0 |         67.8429 |            0 |              8.21623 |                     0 |                     0 |
| wth_0540_eta12 |                0 |         67.7699 |            0 |              8.35235 |                     0 |                     0 |
| wth_0.550      |                0 |         66.5816 |            0 |              8.08989 |                     0 |                     0 |
| wth_0550_eta15 |                0 |         66.4032 |            0 |              8.43029 |                     0 |                     0 |
| wth_0.565      |                0 |         64.6908 |            0 |              7.9029  |                     0 |                     0 |
| wth_0565_eta20 |                0 |         64.3444 |            0 |              8.58584 |                     0 |                     0 |
| wth_0.569      |                0 |         64.1877 |            0 |              7.85359 |                     0 |                     0 |
| wth_0569_eta20 |                0 |         63.8469 |            0 |              8.53251 |                     0 |                     0 |
| wth_0.570      |                0 |         64.0621 |            0 |              7.8413  |                     0 |                     0 |
| wth_0570_eta20 |                0 |         63.7227 |            0 |              8.51922 |                     0 |                     0 |
| wth_0580_eta20 |                0 |         62.483  |            0 |              8.38723 |                     0 |                     0 |

## Files

- `compensator_highres_point_ledger.csv`
- `compensator_highres_decision_table.csv`
- `compensator_key_decision_table.csv`
- `compensator_key_stage_extract.csv`
- `compensator_top_packet_norm_points.csv`