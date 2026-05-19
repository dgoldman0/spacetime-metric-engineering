# Stage I Topology/Support Scaling Discriminator

## Purpose

The shell-throat overlap proxy showed that the compact wide4 handoff reduces live angular/current mixed overlap, but leaves a non-live radial-null residual with a mixed shell/throat signature. This screen asks whether that residual is a fixed floor or whether it scales with broader support geometry.

The test is deliberately small. It is a discriminator before a freeze decision, not a new design campaign.

## Run

Topology/support scaling screen:

```text
toolkit/adm_harness_cli/runs/stage1_v5_topology_support_scaling_41x61/
```

Spec file:

```text
toolkit/adm_harness_cli/specs/topology_support_scaling_compact_wide4.json
```

Grid:

```text
41 x 61
s range: -0.96 to 1.65
l range: -2.80 to 2.80
top rows per channel: 15
```

The base case is the current compact candidate:

```text
compact7_wide4_edge160
entry_carve = 0.75
entry_width_multiplier = 4.8
catch_carve = 0.15
catch_width_multiplier = 3.4
edge_carve = 0.16
edge_width_multiplier = 7.2
null_cushion_log_gain = -0.07
```

The screen varied:

```text
support radius Rth / ROmega: 1.75 -> 1.90 -> 2.05
support width w_th:          0.569 -> 0.65 -> 0.75
angular jacket width wOmega: 1.40 -> 1.80 -> 2.20
selected combinations
```

All tested cases kept zero positive live packet-norm points on this grid.

## Radial-Null Mixed Score

The main discriminator is the top-row `neg_Tkk_radial` shell-throat mixed score.

| case | Rth | w_th | wOmega | mean Tkk badness | mean mixed score | mixed vs base | live pOmega burden | Tkk peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `wide4_base` | 1.75 | 0.569 | 1.40 | 0.1174 | 179.2 | 1.000 | 1.245 | 1.039 |
| `wide4_radius190` | 1.90 | 0.569 | 1.40 | 0.0939 | 173.4 | 0.968 | 1.435 | 0.878 |
| `wide4_radius205` | 2.05 | 0.569 | 1.40 | 0.0790 | 158.8 | 0.886 | 1.651 | 0.751 |
| `wide4_angw180` | 1.75 | 0.569 | 1.80 | 0.1219 | 179.9 | 1.004 | 1.221 | 1.051 |
| `wide4_angw220` | 1.75 | 0.569 | 2.20 | 0.1256 | 181.3 | 1.012 | 1.205 | 1.063 |
| `wide4_wth065` | 1.75 | 0.650 | 1.40 | 0.1219 | 280.9 | 1.568 | 1.262 | 1.048 |
| `wide4_wth075` | 1.75 | 0.750 | 1.40 | 0.1199 | 280.0 | 1.563 | 1.287 | 1.060 |
| `wide4_broad_mild` | 1.90 | 0.650 | 1.80 | 0.0970 | 174.0 | 0.971 | 1.423 | 0.893 |
| `wide4_radius205_wth075` | 2.05 | 0.750 | 1.40 | 0.0922 | 361.3 | 2.017 | 1.687 | 0.764 |

## Interpretation

The result is not a stuck-floor result.

Increasing the support radius lowers the top radial-null badness and lowers the shell-throat mixed score:

```text
Rth/ROmega 1.75 -> 2.05:
  mean Tkk badness: 0.1174 -> 0.0790
  mean mixed score: 179.2 -> 158.8
  Tkk point peak:   1.039 -> 0.751
```

That says the residual is support-geometry dependent. The universe is not obviously pinning this branch to a fixed smeared-null or mixed-null floor at the tested scale.

But the improvement is not free. The same radius broadening raises live angular burden:

```text
live pOmega burden: 1.245 -> 1.651
live p_l burden:    0.457 -> 0.491
```

So radius broadening helps the non-live radial-null infrastructure peak while charging the live angular-pressure ledger. It is an engineering trade, not a clean cure.

Support-width broadening alone is the wrong lever for this residual:

```text
w_th 0.569 -> 0.65 / 0.75:
  mean mixed score rises by about 56%;
  max point peaks also worsen.
```

Angular jacket width alone is nearly neutral for the radial-null mixed score. It trims live `pOmega` burden slightly but does not relieve the top `Tkk` shell-throat signature.

The mild combined broadening case (`Rth = 1.90`, `w_th = 0.65`, `wOmega = 1.80`) mostly preserves the radius benefit in Tkk badness, but does not improve the mixed score beyond the radius-only case. The support-width component appears to cancel much of the radius relief in the mixed derivative product.

## Freeze Implication

This shifts the freeze judgment.

Before this screen, the shell-throat proxy left open the possibility that the residual was an intrinsic fixed source requirement. After this screen, the residual looks at least partly geometry-scalable:

```text
broader support radius lowers the top non-live Tkk residual;
broader support width does not;
angular width is secondary.
```

That argues against being stuck in a fundamental sense. It also argues against freezing the current compact wide4 geometry as final, because a topology/support radius lever is real.

The cleanest next choice is:

```text
Do not launch a broad new Stage I campaign.
Promote compact wide4 as the provisional Stage II target,
but include one radius-broadened comparator, likely Rth/ROmega = 2.05,
so Stage II can tell whether the source family prefers compactness or broader support.
```

If one more Stage I validation is desired before Stage II, the highest-value check is not a wide sweep. It is a selected higher-resolution comparison:

```text
compact7_wide4_edge160 base
vs
wide4_radius205
```

on the same `61 x 83` or `81 x 109` grid, with the shell-throat proxy and smeared-null summaries carried along.
