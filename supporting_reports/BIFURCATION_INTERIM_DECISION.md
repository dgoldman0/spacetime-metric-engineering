# Catch/Rematch Bifurcation Interim Decision

## Status

The previous full point-level bundle was left untouched. This run is a separate bifurcation probe focused on the catch/rematch layer.

The tested question was whether the remaining live packet radial burden behaves like:

1. a one-component shaping problem, where smoothing/retiming the same catch field gradually improves the result, or
2. a two-component split problem, where separating the catch/rematch function into support-side and packet-side components gives a qualitative improvement.

## Main result

The current evidence points first toward **catch-shaping**, not a clean split win.

The best safe focused variant was:

```text
shape_early_minjerk_w32
```

That means the same catch/rematch component is moved earlier and changed to a wider minimum-jerk transition. In the focused 25x41 point run, it reduced live negative radial-null burden to about **85.9% of baseline** while preserving packet safety. Radial pressure barely changed.

The naive temporal split looked promising in the coarse screen, but the focused run found a packet-norm failure. That means decoupling the support-side beta catch from the packet-frame rematch can reduce radial-null burden while breaking the packet handoff. This is not a viable split as tested.

Spatial split variants reduced the live packet **fraction** of negative radial-null burden, but they did not reduce the absolute live radial burden as strongly as the early minimum-jerk shaping case, and they worsened the global radial-null peak in the focused run. That suggests the broad/local spatial split is mostly moving denominators and peak locations, not solving the handoff.

## Focused decision table

| case | decision score | live Tkk fraction | live p_l fraction | live Tkk burden vs base | live p_l burden vs base | Tkk peak vs base | p_l peak vs base | packet norm failure |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| shape_early_minjerk_w32 | 0.929 | 25.92% | 25.02% | 0.859 | 1.000 | 0.999 | 1.000 | no |
| split_spatial_broad100 | 0.965 | 20.31% | 25.02% | 0.930 | 1.000 | 1.423 | 1.000 | no |
| split_broad75_minjerk_w32 | 0.967 | 21.93% | 25.02% | 0.933 | 1.000 | 1.180 | 1.000 | no |
| base_R1p75 | 1.000 | 28.66% | 25.02% | 1.000 | 1.000 | 1.000 | 1.000 | no |
| split_temporal_beta_early | 100.908 | 25.01% | 25.02% | 0.816 | 1.000 | 0.983 | 1.000 | yes |

The huge score for the temporal split is the packet-norm penalty. Without that penalty it would have been the strongest Tkk reducer, which is useful information: the system wants beta/support catch to happen earlier, but packet-frame rematch cannot be left behind.

## Stage reading

The early minimum-jerk shaping variant removes the old entry/pre-catch burden by pulling the catch transition earlier, but the burden reappears inside the larger catch/rematch window. Its improvement comes from lowering the total live radial-null burden, not from merely relabeling the stage.

For negative radial Tkk live burden:

```text
base_R1p75:
  entry/pre-catch     61.53
  catch/rematch       66.67
  release/shift-fade  17.95

shape_early_minjerk_w32:
  entry/pre-catch      0.00
  catch/rematch      116.59
  release/shift-fade   8.94
```

For radial pressure live burden:

```text
base_R1p75:
  entry/pre-catch      6.52
  catch/rematch       10.19
  release/shift-fade   2.86

shape_early_minjerk_w32:
  entry/pre-catch      0.00
  catch/rematch       18.45
  release/shift-fade   1.12
```

The pressure result is especially important: it barely changes in total. That says the radial pressure channel is probably not being controlled by catch timing alone.

## Interpretation

The bifurcation is not yet “split the catch into two components.” The next model should first promote the catch curve itself:

```text
x_catch = 0.00
w_catch = 0.32
catch profile = minimum jerk
```

Then test a more constrained split where the support-side catch and packet-side rematch remain locked by a packet-norm constraint. The naive temporal split tells us that earlier support catch is attractive, but it also shows that the passenger packet cannot tolerate an unconstrained lag between beta catch and packet-frame rematch.

## Next test

Freeze a shaped-catch branch, then test a constrained split:

```text
support catch begins early
packet rematch follows smoothly
beta and packet frame are tied by a max packet-norm constraint
broad infrastructure component is allowed only if it does not raise global Tkk peak
```

The immediate engineering read is:

```text
negative radial-null exposure = mostly catch shaping / timing
radial pressure exposure      = likely a separate radial-geometry/support-channel issue
naive split                   = attractive but unsafe unless constrained
```
