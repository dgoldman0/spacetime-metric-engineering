# Radial Pressure Boundary Push

Prescribed-geometry point-level source diagnostic. This is a source-ledger design screen, not a matter model, not a constraint solve, and not an RSET calculation.

## Track-record note

The previous shaped-catch lesson remains part of the design record: the support-side catch can lead slightly, but packet rematch must remain tightly locked to it. This boundary push keeps that shaped catch fixed and varies only the radial support edge.

## What was tested

Starting point: `R1.75 locked-lead shaped catch`.

Fixed catch/rematch:

```text
support/beta catch: x = -0.05, w = 0.32, minimum jerk
packet rematch:    x =  0.00, w = 0.32, minimum jerk
```

Variable tested:

```text
w_th = 0.54, 0.55, 0.56, 0.565, 0.566, 0.567, 0.568, 0.569, 0.570, 0.58, 0.59, 0.60
```

A few `w_pass = 0.08` packet-transition variants were also checked. They helped `Tkk` modestly but did not improve `p_l` enough to become the main branch.

## Main result

The safety boundary is very sharp. `w_th = 0.569` remains safe on the 21x37 fine-boundary grid, while `w_th = 0.570` produces a live packet-norm failure.

Recommended promoted candidate:

```text
R1.75 shaped catch radial-soft boundary v1
Rth    = 1.75
w_th   = 0.569   # promoted boundary value from this screen
w_pass = 0.06    # keep conservative; w_pass smoothing is optional later
```

Refined 21x37 comparison versus shaped-catch baseline:

| case         |   live p_l burden |   live Tkk burden |   p_l ratio |   Tkk ratio |   max live packet norm |   positive live norm points |
|:-------------|------------------:|------------------:|------------:|------------:|-----------------------:|----------------------------:|
| shaped_base  |           17.572  |           99.5082 |    1        |    1        |               -584.334 |                           0 |
| w_th = 0.569 |           14.0914 |           73.1568 |    0.801927 |    0.735184 |               -189.836 |                           0 |
| w_th = 0.570 |           14.0733 |           73.0174 |    0.800895 |    0.733783 |                237.172 |                           1 |

## Interpretation

This confirms the pressure channel has a genuine radial-support-edge control knob. Increasing `w_th` lowers live radial pressure and also keeps helping live radial-null burden. The improvement is nearly monotone until the packet-norm safety boundary is crossed.

The boundary is not gradual in the safety variable. The source burden improves smoothly from `0.565` to `0.569`, but the packet norm flips at `0.570` on this grid. That means the branch should be promoted with margin rather than sitting exactly at the failure edge. `0.569` is the best observed safe value here; `0.565` is the more conservative version if a higher-resolution check exposes interpolation sensitivity.

The result sharpens the design rule:

```text
Tkk wants shaped catch timing.
p_l wants radial support-edge widening.
packet safety sets a hard upper bound on w_th.
```

## Stage-level read

The remaining live burden is still mainly catch/rematch. Widening the support edge lowers the catch/rematch burden, but it does not relocate the problem into reset/decompression.

|                                   |   catch_rematch |   post_release_buffer |   release_shift_fade |   reset_decompression |
|:----------------------------------|----------------:|----------------------:|---------------------:|----------------------:|
| ('abs_p_l', 'shaped_base')        |         15.9141 |                     0 |              1.65789 |                     0 |
| ('abs_p_l', 'wth_0.569')          |         12.7995 |                     0 |              1.29193 |                     0 |
| ('abs_p_l', 'wth_0.570')          |         12.783  |                     0 |              1.2903  |                     0 |
| ('neg_Tkk_radial', 'shaped_base') |         87.142  |                     0 |             12.3661  |                     0 |
| ('neg_Tkk_radial', 'wth_0.569')   |         63.9671 |                     0 |              9.18972 |                     0 |
| ('neg_Tkk_radial', 'wth_0.570')   |         63.8421 |                     0 |              9.17528 |                     0 |

## Packet transition check

The `w_pass = 0.08` branch at `w_th = 0.56` slightly improves live `Tkk` compared with `w_pass = 0.06`, but its live `p_l` improvement is essentially identical. So packet-transition smoothing should remain a secondary `Tkk` refinement, not the main pressure fix.

## Next recommended test

Run a higher-resolution safety/convergence check on three cases only:

```text
shaped_base
w_th = 0.565
w_th = 0.569
w_th = 0.570
```

Pass condition for promoting `0.569`: no positive live packet-norm points and stable reductions in live `p_l` and live `Tkk`. If `0.569` becomes sensitive at higher resolution, promote `0.565` as the safer radial-soft branch.
