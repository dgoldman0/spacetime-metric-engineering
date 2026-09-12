# Conserved backing and end-load continuation

The joint backing calculation now resolves a persistent material deficit in
the retained loading history. An admissible approximate tensor becomes
inadmissible when its force balance is evolved more accurately: radial
compression exceeds the energy assigned to the separate load-bearing
members. Meanwhile, isolated angular jackets fail the registered end-load
conditions. These results locate the remaining construction problem in the
backing and its mechanical connections, alongside the capacitor's established
electrical duties.

The calculation uses the scheduled active-rail collar patch, its moving
material labels, and its existing heat receiver and guided work route. The
protected packet remains outside the patch. All numbers use the archived
dimensionless normalization; the physical length remains a design parameter.
The technical disclosure and its PDF retain their design content.

## Smooth field sharing and an approximate admissible backing

The first continuation imposed force equations at two temporal Gauss points
per interpolation panel. Three shared-field cases were infeasible in that
low-order representation, and the native-time case reached its solver limit.
A maximum-residual linear program also gave poor independent residuals or
reached its time limit. These are finite numerical-model outcomes.

A sparse quadratic program instead minimizes squared force and power
residuals while retaining the integrated work equation and the separate-member
condition

```
|P| + max(-Q, 2Q) <= f M,
```

where `M`, `P`, and `Q` are energy, radial stress, and angular stress per
material label. A signed correction that lifted a coarse field-sharing
representation to the original smooth field failed this material condition.
Consequently the accepted comparison changes the actual static allocation
profile, using a shape-preserving cubic through the registered safe values.
Its continuous first derivative supplies a regular force without a singular
layer.

At 64 spatial cells and all 258 time nodes, the smooth-allocation case with
`f=0.9` and material null comparison cap 0.2 solves and passes its independent
member-cost check. Its weighted force and power residuals are 3.909% and
3.020%. The electric allocation exceeds its cap by zero, retains at least
0.118 of the reference electric field, and reaches a maximum normalized
average rate of 1.00000000000053. The three archived source-remainder peaks
are 0.22500, 0.20158, and 0.40038.

Those source remainders compare the assigned total tensor with geometric
demand. A quantum field supplying them remains a separate requirement.
Likewise, the member inequality counts constituent energy and stress; an
equation of state and its characteristic speeds require additional material
information. The finer quadratic programs reached their time limit with
failed constraint checks, so their trajectories supply numerical diagnostics.

## Stable evolution of the conserved stress

Preserving the smooth candidate's angular history, prepared energy, and
incoming right-end pressure gives a direct test of its radial support.
The initial radial pressure is equilibrated spatially using the prescribed
initial pressure rate. Each later step evolves momentum implicitly from the
incoming cut while integrating the radial and angular work. This treatment
also handles zero carrying velocity through its algebraic force equation.
Manufactured negative-shift and zero-shift controls test both regimes.

Every fixed fluid, electric field, wave, and receiver divergence enters the
evolution. In particular, the electric force retains the temporal term
`-v H_t/(N R^4)`. Independent quadrature subdivides at every original source
and allocation knot and measures the divergence of the resulting interpolated
tensor.

| Spatial cells | Time nodes | Weighted force residual | Weighted power residual | Maximum member density deficit |
| --- | ---: | ---: | ---: | ---: |
| 128 | 258 | 0.7262% | 3.0579% | 0.57481 |
| 256 | 258 | 0.4525% | 2.9731% | 0.57779 |
| 128 | 515 | 0.6965% | 1.6753% | 0.57456 |
| 256 | 515 | 0.4171% | 1.5812% | 0.57755 |

Both refinements reduce their principal residual, while the material deficit
persists. At a representative worst node of the finest history, near
`t=1.024, x=-2.1`, the rest-frame density is 0.59549, radial pressure 1.17282,
and angular pressure 0.00172. The load is chiefly radial compression. The
necessary separate-member energy exceeds the available density by about
0.581 at that node. The table measures interior quadrature points and
therefore has a slightly different maximum.

The earlier whole-history spatial projections are retained as failed
numerical controls. Their temporal amplification motivated the initial
equilibration and implicit evolution used here. Further temporal refinement
would improve the remaining power interpolation error; the observed
material deficit is already large and insensitive to these refinements.

## Coupled changes of preparation, angular stress, and incoming pressure

A bounded linear response family evolves 27 changes through the same
conservation solver: six prepared-energy profiles, eighteen coupled
space/time angular-stress profiles, and three incoming-pressure histories.
The spatial controls use cubic splines; the temporal controls use quadratic
Bernstein functions. Their amplitudes lie between -5 and 5 relative to the
registered scales. This amplitude range is a computational search bound.

All four family screens are infeasible: member fractions 0.9 and 0.75, each
with exposed end reactions or with adiabatic angular termination jackets.
Thus this particular smooth response span and amplitude range provide no
admissible repair. The stored response basis allows the amplitude restriction
and additional physically motivated controls to be tested separately.

## The end reactions require a continuing load path

For a thin jacket at a material cut, let `Y=R^2 sigma` denote positive surface
energy and `Z=R^2 tau` angular stress per steradian. The radial acceleration
`a` and angular gradient `k` use the same increasing-label material frame as
the bulk equations. The force and adiabatic work equations are

```
a Y - 2 k Z = epsilon R^2 jump,
dY = -2 Z d(ln R),
|Z| <= f Y.
```

Here `epsilon` is -1 at the left cut and +1 at the right. The jump includes
the fluid, electric store, and backing. The magnetic guide continues across
the cut with matched traction, and the wave route retains its own work port.
These assumptions define an isolated angular termination of the remaining
load.

At the left cut, every admissible positive-energy jacket supplies a force
per unit energy between `a-2f|k|` and `a+2f|k|`. For the original composite
schedule at fade, even `f=1` permits only `[0.57369, 0.94360]`, while the
required load is -0.30436. The force signs conflict at every sampled time.
The newer 64-cell midpoint history has the same sign obstruction.

The right cut passes that instantaneous force-sign gate, but its integrated
adiabatic history requires incompatible prepared energies. At `f=1`, the
original history needs `Y(0)>=725.57` and `Y(0)<=4.84`; the newer midpoint
history needs `Y(0)>=890.51` and `Y(0)<=5.75`. Fraction 0.9 also gives empty
intervals. Static Laplace-pressure and expanding-surface controls verify the
sign convention and work integration.

These end results require a continuing mechanical reaction, a jointly changed
bulk pressure history, or a powered end response for the tested schedules.
A connection to the standing rail must supply its own stress and exchanged
work. The calculation grants no unused capacity to that standing support.

## Evidence and reproducibility

The independent cases use up to four workers. The optional quadratic solver
is OSQP 1.0.5, installed in a temporary dependency directory for this session;
`requirements-joint-support.txt` records the dependency. Every completed
evidence directory includes input and output hashes. Rejected and timed-out
optimizer states retain their failed acceptance flags.

Evidence: [two-point force equations](data/joint_gauss_support),
[maximum-residual programs](data/joint_support_residual),
[quadratic programs and field lifts](data/joint_support_least_squares),
[smooth physical allocation](data/joint_support_smooth_allocation),
[whole-history controls](data/joint_projected_candidate),
[implicit evolution and refinement](data/joint_time_projected_candidate),
[conservative response family](data/joint_response_family), and
[termination jackets](data/surface_support_termination).

This milestone continues the
[conservation and passivity analysis](JOINT_SUPPORT_CONSERVATION_AND_PASSIVITY.md).
The remaining session checks the momentum freedom of the existing work route
and the distinction between missing response amplitude and missing physical
load paths.
