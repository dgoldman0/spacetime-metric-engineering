# Connections and reciprocal exchange for driven radial cells

The retained cell histories admit a sharper connection test when the work
beams, their complementary current, and the material traction are considered
together. The earlier locally confined reservoir failures concern different
optimized controls from the final externally powered cell comparison. The
remaining construction question is the reciprocal transport and material
response of the retained decomposition.

This investigation uses the scheduled active-rail patch
`-2.1 <= x <= -0.5`, `0 <= t <= 1.285`, and the retained `f=0.99` support
history. The capacitor, pressure link, endpoint heat/current medium, and
standing support retain their separate physical duties. The established
guide route lies outside the protected packet. Its existing electrical work,
thermal capacity, field allocation, and reaction loads remain assigned.

## Traction and current at the cell connections

The [previous construction](VIRTUAL_RADIAL_CELL_CONSTRUCTION.md) supplies
two accepted local phase-volume controls at pair centers `x=-2` and
`x=-1.975`. Their stress budget includes a balanced field/potential core,
incident and returning waves, conversion heat, an auxiliary positive-energy
component mixture, and a minimum complementary radial current.

For core amplitude `A`, density and radial pressure are `s=A/R^2` and `-s`.
Across an interior cut the core traction jump is therefore `-[A]/R^2`.
The remaining components carry the opposite jump when their sum reproduces
the continuous prescribed total pressure. An isolated core load is an
intercomponent attachment duty; the net force on the full assembly follows
from all component tractions and currents at the cut.

Let `d=-1` in the left feeding region and `d=+1` in the right. Write the
material-frame travelling energies as `u_a` for absorption, `u_w` for useful
return, and `u_h` for heat return. The local allocation uses

```
j_wave = d (u_a-u_w-u_h),
rho_counter = p_r_counter = |j_wave|,
j_counter = -j_wave,
p_t_counter = 0.
```

Consequently the whole allocated backing has zero current in this frame.
If the counterstream crosses the same physical port, its energy flux cancels
the beam energy flux. The work/return beam ledger is thus a component ledger
until the counterstream's own supply, transport, and receiving connections
are specified. Its assigned positive tensor supplies an energy allowance;
its covariant divergence determines the required reciprocal exchange.

This accounting follows the separation of material and radiation tensors
with opposite four-forces in [Park's covariant radiation formulation](https://arxiv.org/html/astro-ph/0601635v2#S2.SS3).
The equations here use the repository's scheduled metric and material frame.

At the middle port, let `a_L,a_R` be outgoing drive powers and `r_L,r_R`
be returning useful-plus-thermal powers, all in the same local rest frame.
The beam contribution to deposited power and radial force is

```
P_beam = r_L+r_R-a_L-a_R,
F_beam = a_L+r_L-a_R-r_R.
```

Equal traffic in the two arms cancels beam recoil while preserving the
power exchange. Energy returned from an arm adds to that arm's incident
momentum contribution. The counterstream, material attachments, and any
subsequent heat outlet have their own contributions.

## Common phase across opposed feeding regions

The accepted independent controls have sizeable phase differences between
their neighboring cells. The largest amplitude jumps are `0.366355` at
`x=-2` and `0.226861` at `x=-1.975`, compared with peak amplitudes
`0.417894` and `0.390295`. The optimization had permitted independent
amplitudes at the two sides of a pair of width `0.0005`.

A bounded continuation imposes a common amplitude and common conversion
increments on the two feeding regions. It retains the original density
target, 0.2% numerical reserve, 98% conversion efficiency, heat return,
guide drift comparison 0.5, finite interface allowance, and whole-panel
wave ceilings. This directly removes the core traction step at the middle
cut. Propagation on the two different metric paths still determines their
actual beam recoil.

The first equality-constrained implementation admits the `x=-2` case with
zero additional density. Its scaled equation residual is `1.05e-12`; the
secondary travelling-inventory minimization returns no solution. The
`x=-1.975` primary solve returns an unresolved HiGHS status, which leaves
that location undecided. The raw comparison is archived in
[the common-phase calculation](data/virtual_cell_matched_pair/summary.json).

Physical control reconstruction first verifies that spatial phase mismatch
is at roundoff level, then uses a common nonnegative amplitude. Its positive
and negative increments preserve the exact phase change and remove
simultaneous conversion cycles. Fresh interval bounds and independent wave
replay determine the retained numerical result.

The focused implementation checks include a symmetric constant-tension
control and an incompatible neighboring-tension control whose exact common
phase penalty is `2/3`. The latter verifies that the constraint introduces
a physical restriction. Reconstruction tests reject a finite unmatched
history. Eighteen control, exponential-transport, and shared-reservoir tests
pass at this stage.

Eliminating the duplicate equality variables preserves the common-phase
model and the successful first location. The second location again returns
an unresolved numerical status. An explicit alternative takes the arithmetic
mean of the two previously accepted phase histories and applies it to both
arms. This changes the controls deliberately, preserving a shared phase
without a further optimization. The
[averaged controls](data/virtual_cell_averaged_controls/summary.json) pass
[fresh whole-panel envelopes](data/virtual_cell_averaged_envelopes/summary.json)
at both locations, with density margins `0.0000848228` and `0.0000757241`.
Their changing-geometry replay supplies the separate refinement check.

## Reciprocal power required by the complementary current

The minimum counterstream has density `c=|j_wave|` and current
`j_c=-j_wave`. Define material derivatives and kinematic coefficients by

```
D_u = (1/N) partial_t,
D_s = (1/ell) partial_x + (v/N) partial_t,
theta_r = D_u ln ell,       theta_t = D_u ln R,
a = radial material acceleration,       k = D_s ln R.
```

The counterstream's required power and radial force are

```
P_c = D_u c + 2(theta_r+theta_t)c + D_s j_c + 2(a+k)j_c,
F_c = D_s c + 2(a+k)c + D_u j_c + 2(theta_r+theta_t)j_c.
```

Its partner receives `-P_c,-F_c`. A free counterstream has both quantities
zero. Material-frame elastic direction scattering permits a force exchange
with zero power. On a smooth region of the minimum allocation only one
null direction is populated, so `F_c=sign(j_c)P_c`; zero-power completion
there also requires vanishing force. Additional counterpropagating photons
provide a larger class with their own energy requirement.

The [differential audit](data/virtual_cell_counterstream_baseline/summary.json)
reconstructs this exchange in the material tetrad and independently through
the conservative directional ADM wave equations. It compares derivatives
on the retained replay with derivatives after time/space decimation. Firm
witnesses avoid current switches, control-knot crossings, and material cuts;
their exchange exceeds the measured numerical sensitivity by a factor of
ten. Both signs of reciprocal power are resolved at each location.

| Pair center | Resolved nonzero-exchange samples | Largest resolved `|P_c|` | Largest resolved `|F_c|` |
| --- | ---: | ---: | ---: |
| -2 | 9296 | 4.42379 | 4.42379 |
| -1.975 | 6765 | 1.52179 | 1.52179 |

These values use project stress per proper time/length. They describe the
required exchange between constituents of the retained decomposition. The
total backing tensor and its previously measured continuum residual remain
the prescribed target. The derivative comparison measures sensitivity of
the sampled replay; it supplies empirical witnesses rather than a continuum
error bound.

## Extra prepared radiation and the passive energy bound

A stronger comparison permits counterstream density above `|j_wave|` and
arbitrary prepared spatial grading. Let `u_r=u_w+u_h`, and let `W` be the
energy of all drive, return, heat, and counterstream photons. Their total
current is zero. The counted beam conversion obeys
`P_wave=-A_t/(N R^2)`. Requiring `P_c=0` therefore gives

```
partial_t[(ell R)^2 W] = -ell^2 A_t,
I(t,x) = integral_0^t ell^2 A_t dt,
(ell R)^2 W = C(x)-I(t,x).
```

Nonnegative photon populations require `W >= 2 max(u_a,u_r)`. The existing
component cone permits at most `W <= (rho+2p_r+p_t+s)/3`. Every prepared
constant must consequently satisfy

```
max_t[I+(ell R)^2 2 max(u_a,u_r)] <= C(x)
    <= min_t[I+(ell R)^2 (rho+2p_r+p_t+s)/3].
```

This interval uses the full available density, including the former
numerical reserve. It permits arbitrary extra balanced counterphotons and
imposes no additional material mass or guide requirement on them. Integrating
the known piecewise-linear phase controls avoids differentiation of the
current in this energy test.

All 96 positions in each retained pair have empty intervals. Representative
interior witnesses are:

| Pair center | Witness position | Required lower `C` | Permitted upper `C` | Gap |
| --- | ---: | ---: | ---: | ---: |
| -2 | -2.00002864583 | 25.234190 | -4.862000 | 30.096189 |
| -1.975 | -1.97497656250 | 54.379269 | 9.809304 | 44.569965 |

The first witness compares `t=0.0445483` with `t=0.547129`; the second
compares `t=0.0445483` with startup. Four- and eight-point Gauss quadrature
change the work integrals by less than `6e-14`. Decimating the sampled
histories changes these gaps by approximately `0.093` and `0.125`.
Propagation uncertainty remains inherited from the independent wave replay.

Thus a counterstream with zero local power exchange cannot complete these
prescribed controls within their allotted stress. The required continuation
is reciprocal energy exchange with another counted constituent, or revised
joint controls that satisfy that exchange. The isolated-store/jacket failures
and this counterstream result address different construction assumptions.

Five manufactured tests cover source-free propagation, explicitly sourced
opposing streams, independent ADM/tetrad agreement under refinement, and
compatible and incompatible prepared-radiation intervals. The archived
evidence records the controls, metric, source code, derivative witnesses,
and passive-energy intervals.
