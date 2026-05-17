# Shaped Catch Branch Candidate

## Branch name

```text
R1.75 locked-lead shaped catch v1
```

## Why this branch

The bifurcation probe gave a useful rule: the support-side catch wants to begin earlier, while the packet rematch cannot lag freely. The shaped-catch design therefore keeps the handoff as one coordinated choreography, with only a small constrained lead for the support/beta catch.

This is not the earlier unsafe temporal split. The beta/support catch and packet rematch use the same smooth profile and nearly the same timing. The packet rematch follows by only `0.05` in schedule coordinate.

## Candidate parameters

```text
Base geometry:
  Rpass   = 0.35
  Rth     = 1.75
  ROmega  = 1.75
  w_th    = 0.35
  wOmega  = 1.40
  aOmega  = 0.20

Support decompression:
  q(s) = minimum-jerk down-ramp
  q_t0 = -0.40
  q_Tr = 3.00

Catch/rematch:
  beta/support catch profile  = minimum jerk
  beta/support x_catch        = -0.05
  beta/support w_catch        = 0.32
  packet rematch profile      = minimum jerk
  packet rematch x_catch      = 0.00
  packet rematch w_catch      = 0.32
  maximum tested lead         = 0.05
```

Fallback pure-shaped branch:

```text
shape_xm05_mj_w28:
  x_catch = -0.05
  w_catch = 0.28
  profile = minimum jerk
  beta/support and packet rematch fully locked
```

## Refine-3 result

The higher-grid three-case check compared baseline R1.75, the pure shaped fallback, and the locked-lead shaped branch.

| case | live Tkk fraction | live p_l fraction | live Tkk burden vs base | p_l burden vs base | Tkk peak vs base | packet-norm failure |
|---|---:|---:|---:|---:|---:|---:|
| locked_lead005_mj_w32 | 26.14% | 25.10% | 0.840 | 1.000 | 0.977 | 0 |
| shape_xm05_mj_w28 | 26.22% | 25.10% | 0.844 | 1.000 | 0.995 | 0 |
| base_R1p75 | 29.26% | 25.10% | 1.000 | 1.000 | 1.000 | 0 |

## Interpretation

The constrained lead survives refinement better than the pure one-component branch by a small margin. It reduces live negative radial-null burden to about `84%` of baseline without producing a packet-norm failure. The pure shaped fallback is close at about `84.4%` of baseline.

Radial pressure remains essentially unchanged in both branches. That means shaped catch helps the radial-null channel, while radial pressure likely needs a separate radial-geometry/support-channel modification.

## Current design decision

Promote `locked_lead005_mj_w32` as the next shaped-catch branch to test.

Keep `shape_xm05_mj_w28` as the conservative fallback if the tiny beta/packet lead fails at higher resolution or under off-axis packet tests.

## Next branch tests

1. Refine the candidate at a larger grid and check convergence of the live radial-null reduction.
2. Sweep constrained lead values in the narrow range `0.00` to `0.08`; do not allow freely lagging rematch.
3. Sweep catch width around `0.28` to `0.38`.
4. Keep packet-norm failure as a hard rejection.
5. Treat radial pressure as a separate problem after the shaped catch branch is stable.
