# V5 Throat-Capacity Screen and Gradient-Matching Note

This note records the first throat-capacity screen after the high-resolution V5 coupled timing result. The screen used the current support-shell candidate neighborhood:

```text
service factor:              V = 5
carrying-flow amplitude:      a_beta = +0.5
catch lead:                  1.45, 1.55
temporal width:              0.30
clock-lapse ratio:           0.375, 0.5
rail-stretch ratio:          0.0
throat-capacity ratio:       -0.5, -0.25, -0.10, -0.05, 0, 0.05, 0.10, 0.25, 0.5
```

The result is clear: same-window throat-capacity coupling can be set aside as a direct load-bearing knob for the current V5 support-shell design. The best source-objective and best practical tradeoff both occur at `throat_capacity_ratio = 0`. Negative throat-capacity can produce tiny aggregate or angular-pressure improvements in a few `clock = 0.5` cases, with a large point-peak and radial/current penalty. Positive throat-capacity is worse: even small positive ratios raise radial-null burden sharply, and larger positive ratios produce severe point-peak growth.

The best source-objective case remains:

| catch lead | temporal width | clock ratio | throat-capacity ratio | source objective | max burden | radial-null ratio | radial-current ratio | angular-pressure ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `1.55` | `0.30` | `0.375` | `0.0` | `1.097425` | `1.054489` | `1.019950` | `1.011789` | `1.054489` |

The best aggregate case also keeps throat-capacity off:

| catch lead | temporal width | clock ratio | throat-capacity ratio | max burden | radial-null ratio | radial-current ratio | angular-pressure ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `1.45` | `0.30` | `0.5` | `0.0` | `1.053076` | `1.024110` | `1.013124` | `1.053076` |

## Interpretation

The throat-capacity result reinforces the main control principle that has emerged across the V5 support-shell program: timing and gradient matching dominate amplitude tuning. The source ledger repeatedly penalizes components that are placed in the right architectural region but rise, fall, or overlap the intrinsic support/throat gradients in the wrong way. Carrying-flow alone was too one-sided. Mistimed support-shell cases concentrated burden in the shell-throat overlap band. Same-window throat-capacity now shows the same pattern: it adds intrinsic angular/throat response, but the added gradient couples into the mixed shell-throat layer faster than it relieves the angular-pressure ceiling.

The successful part of the architecture remains the clock-lapse-coupled carrying-flow shell. Narrow timing around `temporal_width = 0.30`, later support lead around `1.45` to `1.55`, and clock-lapse ratio around `0.375` to `0.5` gives stable packet safety and controlled source placement. That is the current reduced source-feasibility candidate.

## Next Direction

The next design question should be framed as gradient matching. Useful next probes are:

1. Shape/smoothness sweeps for the support-shell window itself.
2. Delayed, broadened, or lower-gradient companion windows for any intrinsic metric partner.
3. Mixed-term proxy diagnostics that correlate derivatives of the shell window, carrying-flow, clock-lapse, and support/throat metric gradients with the demanded-source deltas.
4. Source-family assignment for the residual angular-pressure burden if metric-side intrinsic partners keep charging the shell-throat overlap layer.

For this design branch, same-window throat-capacity should be set aside as a default load-bearing component. It may remain a useful architectural knob in variants with different throat timing, broader angular jackets, or separately shaped intrinsic windows.
