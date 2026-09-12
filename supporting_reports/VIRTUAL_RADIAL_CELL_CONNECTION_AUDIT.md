# Connections and reciprocal exchange for driven radial cells

Sharing the phase between opposed radial-cell feeds preserves the local
stress-budget pass at both tested locations, removes the central core
traction jump, and reduces peak net central beam recoil by 99.89% and
99.18%. Each arm continues to carry appreciable force. The remaining
construction question is the reciprocal energy exchange and transport of
the complementary radiation and its material partner. A passive completion
with zero material-frame power exchange fails for these prescribed controls.

The earlier locally confined reservoir failures concern different optimized
controls from the final externally powered cell comparison. The present
audit tests the retained work beams, complementary current, and component
tractions together, then separately relaxes the phase schedule itself.

The [joint thermal-exchange continuation](VIRTUAL_RADIAL_CELL_THERMAL_EXCHANGE.md)
adds a counted pressure-bearing state and optimizes it with the phase and
radial radiation. Its sampled local energy gate opens at both locations;
causal delivery and a physical reciprocal constitutive law determine the
remaining construction.

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

## Explicit port subledger on the accepted controls

An independent SSP RK2 replay accumulates each beam's port traffic at both
integration stages. The six streams share corrected-step observation times,
so the radial reaction compares their simultaneous values. Each case uses
96 spatial samples and 2057 saved times, with finer internal steps selected
by the same causal transport restriction as the accepted replay.

| Pair center | Incident work | Useful return | Heat return | Signed radial beam impulse | Peak proper beam reaction |
| --- | ---: | ---: | ---: | ---: | ---: |
| -2 | 0.05601246 | 0.05527565 | 0.00224866 | 0.01529292 | 0.89677449 |
| -1.975 | 0.07277549 | 0.06549560 | 0.00279258 | -0.00620367 | 0.18671659 |

Energies integrate material-frame photon energy per coordinate time; the
force is per common-port proper time. All entries include the spherical
`4 pi` factor. The signed radial quantity is the sphere-integrated local
radial component in the prescribed tetrad.

If the minimum counterstream crosses the same cut, the radiation energy
current cancels and its radial pressure adds to that of the work beams. The
resulting conditional radiation reactions peak at `1.575659` and `0.373433`.
The independent core traction steps peak at `4.603748` and `2.850815`.
Those component contributions retain their separate attachment and transport
requirements; the complete material traction follows from their shared
source construction.

The [port archive](data/virtual_cell_port_baseline/summary.json) retains each
arm's incident, useful-return, and thermal histories, initial and final wave
inventories, geometric work, conversion sources, and counterstream flux
requirements. Its physical-time ADM balances close within `2.39e-18`.
Replayed wave fields agree with the earlier accepted arrays within `5.01e-12`.
Thirteen analytic tests check transformed port flux, recoil signs, symmetric
cancellation, backward absorption bookkeeping, geometric work, and common
observation times.

The first optimized common-phase case separately passes independent
changing-geometry replay, with minimum density margin `0.000111923`. Its
[retained evidence](data/virtual_cell_matched_replay/summary.json) covers
the `x=-2` location. The deterministic averaged candidate provides the
two-location comparison described above.

## Reoptimizing the passive phase itself

The fixed-control interval result leaves a separate question about the
phase schedule. A final local relaxation optimizes that schedule together
with prepared balanced radial radiation at each tested position. It allows
perfect conversion, zero required travelling inventory, and arbitrary
initial radiation. The finite interface allowance remains in the target
budget; additional guide requirements are omitted in this favorable gate.

Let `U=(ell R)^2 W`. For a piecewise-linear phase amplitude, conservation
on a panel is

```
U_(i+1)-U_i + mean_panel(ell^2) (A_(i+1)-A_i) = 0.
```

Nonnegative `A,U` and the three remaining component-cone facets define a
linear program. Its objective is the smallest uniform extra density needed
by that local history. It uses the full archived target density and permits
independent phase histories at different positions. Spatial coherence,
photon transport, opacity, and the force exchange law remain additional
requirements.

| Position | Added density, 1029 times | Added density, 2057 times |
| --- | ---: | ---: |
| -2.00000260417 | 0 | 0 |
| -1.99999739583 | 0 | 0 |
| -1.97500260417 | 0.000380990 | 0.000380853 |
| -1.97499739583 | 0.000370185 | 0.000370049 |

The [passive-phase archive](data/virtual_cell_passive_phase/summary.json)
therefore contains an optimistic local energy/cone opening near `x=-2`
and a small remaining deficit near `x=-1.975`. The latter persists when
the phase controls change and the travelling inventory requirement is
removed. The fixed-control failures alone would have missed the opening
at the first location.

Each positive optimum has a separately reconstructed bounded-domain dual
lower bound within `9e-16` of the primal value. The finite variable bounds
follow from the explicit feasible competitor `A=U=0` with a sufficiently
large density allowance. The archive retains those bounds, multipliers,
controls, and residuals. An independent algebraic reconstruction of all eight
solutions finds maximum panel residual `1.58e-14`, facet violation
`1.12e-16`, and primal/dual discrepancy `6.40e-16`.

This certificate concerns the sampled local phase family and its stated
favorable component assumptions. The continuing construction requires joint
phase and constituent response, with energy exchange, transport, and the
full target solved together.

The backing target retains its registered continuum force residual of
approximately `0.3752%` and weighted power residual `1.33e-7`. The local
optimization certifies its finite input problem; those certificates do not
bound changes from further refinement or reoptimization of the backing
itself.

## Retained common-phase stress comparison

The deterministic averaged phases pass independent changing-geometry replay
at both locations. Minimum density margins are `0.0000831843` at `x=-2`
and `0.0000731197` at `x=-1.975`. Each replay uses 96 spatial samples and
2057 time samples with the original 98% conversion efficiency, thermal
return, guide comparison, and interface allowance. The exact common phase
removes the middle core traction jump.

The [averaged replay](data/virtual_cell_averaged_replay/summary.json) retains
the complete tested wave and stress histories. Source-identity checks compare
the replay and controls with their immutable manifests and follow verified
manifest links to the original active metric and medium data.

The [common-phase counterstream audit](data/virtual_cell_counterstream_averaged/summary.json)
still finds empty passive-energy intervals at all 96 sampled positions in
both pairs. Representative interior gaps are `26.049549` near `x=-2` and
`44.548457` near `x=-1.975`; temporal decimation changes them by `0.261`
and `0.124`, respectively. Quadrature differences stay below `5e-14`.

An additional relaxation removes the entire lower bound on radiation
inventory while holding the common phase fixed. Its required initial
constant becomes simply `max_t I`. Even this relaxation has empty intervals
at every sampled position, with maximum gaps `25.906096` and `44.427205`.
The fixed phase work and the available correlated stress already require
an energy-exchanging partner. Travelling peaks alone therefore do not
account for this remaining conflict.

The minimal-counterstream differential audit again resolves power exchange
of both signs. The largest resolved magnitudes are `2.21508` and `1.22055`
in the two pairs. Phase matching retains the useful local stress model and
removes the core discontinuity, while reciprocal material energy exchange
remains the limiting physical completion.

## Opposed-feed recoil comparison

The [common-phase port replay](data/virtual_cell_port_averaged/summary.json)
uses the same transport scheme and resolution as the original port replay.
Its shared phase balances most of the central recoil while retaining the
gross work delivery and heat-return duties.

| Pair center | Original peak net beam reaction | Common-phase peak net beam reaction | Reduction | Largest common-phase arm reaction |
| --- | ---: | ---: | ---: | ---: |
| -2 | 0.89677449 | 0.000971147 | 99.8917% | 0.450558 |
| -1.975 | 0.18671659 | 0.001538490 | 99.1760% | 0.647610 |

Forces use the common material frame, proper time, and spherical `4 pi`
normalization defined above. Opposite arm forces account for the small net
reaction; their individual connections still transmit the tabulated loads.
The central core traction jump is exactly zero in both cases. The different
metric paths leave a small residual beam asymmetry even with identical
phase histories.

| Pair center | Incident work | Useful return | Heat return | Signed beam energy entering cells | Signed radial beam impulse |
| --- | ---: | ---: | ---: | ---: | ---: |
| -2 | 0.05544427 | 0.05473690 | 0.00222630 | -0.00151893 | -0.000133258 |
| -1.975 | 0.07172822 | 0.06448985 | 0.00275110 | 0.00448727 | -0.000172295 |

If the allocated minimum counterstream crosses the same cut, its energy
current cancels the beam current and its pressure contributes to the
reaction. The conditional complete-radiation peaks are `0.001907653` and
`0.003017384`. This calculation supplies the kinematic port requirement;
the counterstream's transport, energy exchange, and material attachments
remain to be constructed.

The port wave fields agree with the independent common-phase stress replay
within `2.503e-12`. The resulting conservative density-budget perturbation
bound is `1.502e-11`, well below the retained margins. Physical-time ADM
wave balances, including the summed ledgers, close within `5e-18`. The two
cases take 5.80 and 6.01 minutes with two independent workers and retain
approximately 71 MB of evidence.

## Construction boundary and reproducibility

The retained result is a common-phase cell pair with a verified local
stress allowance and substantially balanced central recoil. Physical
completion requires a joint phase, radiation, and material exchange law
whose constituents supply opposite four-forces and whose stresses remain
within the complete allocation. The endpoint medium, pressure link, and
standing support already carry assigned duties; any participation in this
exchange must enter their existing budgets and evolution equations.

The passive fixed-control route reaches its energy/cone boundary in this
round. Allowing the phase itself to change opens the favorable local gate
near `x=-2`, while the second location retains a small sampled deficit.
These distinct outcomes support keeping the common-phase control and
reformulating the reciprocal constituent dynamics before extending the
material search. A complete active-rail source and sustained operation
remain open.

The focused control, transport, counterstream, passive-phase, and interface
suite passes 58 tests. The final port checks also cover linked model
identity, tampered inputs, and equivalence of interpolation on known time
panels. Library use preserves the initialized HiGHS thread configuration;
fresh audit workers explicitly request one solver thread. This avoids a
process-global scheduler conflict while preserving the archived numerical
problems.

Every calculation directory links its controls, target geometry, numerical
outputs, and source versions through SHA-256 manifests. Earlier source
versions remain recoverable from the staged commits. Verification of all
13 calculation manifests checks 698 file references, including nine
historical source versions. The port runner
accepts `--source`, `--output-name`, `--factor`, and `--workers`; the recorded
comparison uses factor 4 and two workers. The counterstream and passive-phase
audit scripts reproduce the separate source and energy/cone tests from the
registered histories.
