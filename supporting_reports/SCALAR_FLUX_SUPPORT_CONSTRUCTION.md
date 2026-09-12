# Scalar potential and flux-tube support

Scalar potential energy supplies the correlated stress missing from the
previous electromagnetic/radiation/angular-membrane comparison. Its local
addition admits the retained active-rail backing target and a conservatively
blended target with a lower comparison peak. Permanent radial flux-tube
populations impose a stronger temporal restriction. Both a common population
and arbitrary time-independent spatial grading fail after reoptimizing the
registered support family. Stable causal elastic excitations about a fixed
tube ground state remain inside the same excluded stress envelope.

The calculation concerns the scheduled backing patch `-2.1 <= x <= -0.5`,
its pressure link, and its standing-support connections. It uses the active
geometry and counted electrode, fluid, work-route, and receiver loads from the
[joint construction review](JOINT_SUPPORT_CONSTRUCTION_REVIEW.md). The
capacitor keeps its electrical role, while the support carries the combined
mechanical reaction. The standing substrate's allocated tensor remains a
construction target with a separately required physical realization.

## Local stress supplied by the extra field sector

Write the rest-frame tensor as `(rho,p_r,p_t)`. Here `rho` is energy density,
including rest energy. The candidate basis contains radial Maxwell energy
`E`, scalar potential energy `V`, radial waves `W`, angular waves `H`, an
angular tensile membrane `M`, and rest inventory `I`:

| Energy | Tensor per positive unit energy |
| --- | --- |
| `E` | `(1,-1,1)` |
| `V` | `(1,-1,-1)` |
| `W` | `(1,1,0)` |
| `H` | `(1,0,1/2)` |
| `M` | `(1,0,-1)` |
| `I` | `(1,0,0)` |

Minimizing their summed energy at fixed pressures gives

```
rho_min = max(p_r+2p_t, p_r-p_t, -p_r, -p_t).
```

In particular, `E=V=1/2` supplies `(1,-1,0)`. The earlier Maxwell field plus
purely angular membrane needed energy 2 for the same unit radial tension.
The scalar potential contributes radial tension while supplying the
transverse reaction. This is the relevant change in stress correlation.

[Ishihara and Ogawa](https://arxiv.org/html/2103.13732v1) give a canonical
scalar/gauge model whose potential-dominated interior has positive energy
and equal negative pressures. Their full tensor also contains scalar kinetic
and gradient energies. A local allocation of `V` leaves those field
equations, gradients, and exchanges to the material construction.

For a general target, the allowed potential interval is

```
max(0,(-2p_r-rho-p_t)/2) <= V
V <= min((rho-p_r-2p_t)/4, rho-p_r+p_t).
```

At each allowed `V`, the field energy satisfies
`max(0,-p_r-V) <= E <= (rho-p_r+p_t-V)/3`. The remaining positive weights
then reconstruct the target tensor. Independent linear programs verify the
closed-form energy bound and the component reconstruction.

## Equilibrium tubes impose a conserved amplitude

An isolated straight static relativistic vortex has equal energy and tension
per unit length. For fixed tube count, a radial bundle therefore supplies

```
(rho_v,p_r_v,p_t_v) = (A/R^2,-A/R^2,0).
```

The amplitude `A` is constant along an uninterrupted bundle and through time.
This tensor is exactly conserved on the registered active metric. Its
equality of longitudinal energy and tension also holds for a resolved
equilibrium core; the expression uses the integrated transverse equilibrium
stress, with the usual small-core approximation relative to the rail scale.

Subtracting this tensor and requiring the remaining fields, radiation,
angular membrane, and rest inventory to carry positive energy gives

```
A >= max(0, R^2*(-2p_r-p_t-rho)),
A <= R^2*min((rho-p_r-2p_t)/2, (rho-p_r+p_t)/2).
```

The final `f=0.99` generic target admits this decomposition independently at
every original node. A common amplitude instead requires `A >= 2.02361`
near `(t,x)=(1.24986,-1.15)` and `A <= 0.00237834` near
`(0.0727832,-2.0)`. The two bounds differ by a factor of about 851. At
`x=-2.0` alone, the maximum lower bound through time exceeds the minimum
upper bound by a factor of about 119. Even independently grading the tube
population at each position leaves a temporal conflict in this target.

The upper-bound witness is a region of radial compression. Maintaining a
large permanent tension there consumes energy in both the tension carrier
and its opposing compressive load. The later tensile region needs much
more of the same permanent population. This explains the conflict in terms
of the assembly's changing load distribution.

## Reoptimizing the scheduled support

The comparison reuses the conservative response bases at 128 cells / 258
times and 256 cells / 515 times. All 27 material controls have unrestricted
amplitudes, both work-direction fractions range over `[0,1]`, and the
conserved bundle amplitude ranges over `[0,infinity)`. The bundle is
subtracted from the total backing response before testing the residual
component mixture. Thus its energy and stress belong to the same counted
backing tensor.

| Representation | Freely varying potential energy | Conserved bundle plus earlier components |
| --- | --- | --- |
| 128 cells | Nodal material null peak `0.663599` | Infeasible subset of 2601 constraints |
| 256 cells | Nodal material null peak `0.690092` | Infeasible subset of 2602 constraints |

The refined potential case satisfies all 1,455,905 original inequalities to
`1.25e-13` after replacing the sampled angular maximum with the analytic
maximum. Its initial support inventory is 10,133.7, final inventory 978.53,
and charging feed fraction from the left 0.25134. Recovery remains rightward.
For comparison, the earlier generic `f=0.99` target had material null peak
1.76512 and initial support inventory 7914.71. The lower peak therefore
coexists with increased prepared energy.

These peaks cover the backing and pressure medium in the existing comparison.
The changed route's full tensor, physical field dynamics, and complete quantum
source remain separate entries in the construction. The nodal potentials
provide an algebraic response target. Their independent work audit is
reported below.

The conserved-bundle result is a finite-family numerical infeasibility
result, obtained on both representations. The local interval contradiction
above independently excludes that realization of the retained target.

## Conservative audit and a retained scalar target

The dense audit evaluates 2057 times and 1025 positions on the refined
representation, including original knots, physical cuts, and three Gauss
points per panel. Energy comes from integrating the actual radial work,
angular work, and registered exchange. The original `f=0.99` target passes
the scalar/field component cone throughout this sample. Its weighted force
residual is 0.3752% and its weighted power residual is `1.33e-7`.

The unconstrained potential optima touch component-energy boundaries at their
nodes. Between nodes, the coarse and refined targets exceed their available
energy by `0.00066875` and `0.00084963`, respectively. These optima therefore
remain failed dense-admissibility controls.

A single deterministic continuation uses 90% of the refined potential target
and 10% of the already admissible `f=0.99` target. The material controls,
direction fractions, initial energy, and pressure histories are blended
together. Replaying the archived conservative response basis reproduces the
blend to `2.83e-12`; the total tensor has a common force and work history.

The blend passes the dense scalar/field energy gate. Its smallest sampled
energy margin is `5.72821e-5`, minimum density is 0.0370150, weighted force
residual is 0.3775%, and weighted power residual is `1.66e-7`. Its analytic
angular maximum at the original nodes is 0.797139, compared with 1.765117 for
the earlier target. The comparison peak falls by about 55%, while initial
support inventory rises about 25%, to 9911.83. This retains a useful stress
allocation improvement with positive sampled component energy. A constitutive
field evolution and continuum convergence remain separate requirements.

The end reactions remain substantial. The blend's left cut requires signed
load `-1.26754` at `t=0.5`, while every admissible positive-energy angular
jacket supplies force per unit energy in `[0.67506,0.84130]`. The right
adiabatic jacket requires initial inventory simultaneously above 5275.34 and
below 51.54. A continuing standing-support connection must carry those loads
and its accompanying work.

## Allowing arbitrary permanent spatial grading

The stronger test gives each spatial node its own amplitude `A(x)`, constant
only through time. Each amplitude is positive and unbounded. This allows
arbitrary grading with no imposed smoothness or spatial-amplitude budget.
A varying amplitude has radial divergence

```
F_v = -A_x/(ell R^2)
```

and vanishing material-frame power. The remaining backing receives the
opposite exchange. The total response still satisfies the registered
conservation equations. The medium that establishes this grading has an additional construction duty,
so the test grants an optimistic local stress envelope.

The direct program rejects the coarse representation. Its refined version
reaches the constraint-generation iteration limit. Eliminating the amplitudes
resolves that numerical uncertainty: at every position, a time-independent
amplitude exists exactly when the greatest lower bound through time lies
below the least upper bound, with all upper bounds nonnegative. Separating
those temporal inequality pairs leaves only the original 29 material and
route controls plus the comparison peak.

The eliminated programs are infeasible on both representations. Each
contradiction uses 30 nonnegative weighted inequalities. Their weighted
right-hand sides are `-0.000485543` and `-0.000571242`, with floating-point
coefficient cancellation errors below `3.0e-16`. Independent full-program
positive and negative controls verify that temporal elimination preserves
feasibility. The resulting obstruction covers the registered response family
even after granting arbitrary permanent grading.

Exact rational verification of the archived normalized eliminated matrices
retains nonnegative weights, unit weight sum, exact coefficient cancellation,
and strictly negative right-hand sides on both grids. Thus each archived
matrix requires `0 <=` a negative number. This exact statement applies to
those finite coefficient matrices; constructing them from discretized geometry
and floating-point elimination retains its numerical scope.

## Why ordinary elastic or current excitations stay within this gate

[Hartmann, Michel, and Peter](https://arxiv.org/pdf/1710.00738) relate the
longitudinal and transverse squared characteristic speeds of an elastic
string to `-dT/dU` and `T/U`. Consider an aligned equilibrium branch connected
to a common ground state `U=T=mu`, with `U>=mu`, `T>=0`, and causal stable
longitudinal response `0<=-dT/dU<=1`. Integrating this last inequality gives

```
T <= mu,              U+T >= 2mu.
```

Its diagonal stress has the exact positive decomposition

```
(U,-T,0) = mu*(1,-1,0)
         + (mu-T)*(1,1,0)
         + (U+T-2mu)*(1,0,0).
```

The last two terms already belong to the radial-wave and rest-inventory
basis used by the conserved-bundle test. Consequently those causal elastic
branches, including the transonic law `UT=mu^2`, fit inside its more generous
component envelope. A fixed spatial dependence in `mu` belongs to the
graded version of the same gate. Adding these excitations therefore preserves
the finite-family obstruction. This implication is derived here from the
characteristic-speed condition; the cited work studies microscopic string
models and also shows
that macroscopic stability can coexist with microscopic instability in excited
branches.

The implication assumes a fixed ground state, radial orientation, conserved
bundle count, and the stated equilibrium branch. A changing condensate phase,
resolved transverse dynamics, changing tube orientation or distribution, or
additional interaction stress introduces different material equations and counted exchanges.

## Changing the tube cross section

For a leading-volume magnetic bag population of one species, let `a` be the
common physical tube cross section at a given slice. Fixed tube count,
magnetic flux, and core potential give averaged energies
`E proportional to 1/(R^2 a)` and `V proportional to a/R^2`. Therefore

```
A0 = 2 R^2 sqrt(E V)
```

stays fixed even when the cross section changes. The exact local component
polytope above gives the minimum and maximum possible `E V`. At fixed `V`,
its minimum uses `E=max(0,-p_r-V)` and its maximum uses
`E=(rho-p_r+p_t-V)/3`. Endpoint evaluation gives the minimum product;
maximizing the latter concave quadratic gives the maximum.

On the densely audited original `f=0.99` target, the resulting interval
requires `A0 >= 2.03052` and `A0 <= 0.00274627`. At `x=-2.0` alone, its
temporal lower/upper conflict has a factor of about 132. The improved blended
target also fails this invariant, with global bounds 2.47300 and 0.000274627.
Thus changing the tube cross section alone preserves a large mismatch in
these two targets.

This product test uses the leading-volume, large-flux approximation. Finite
domain-wall energy, transverse inertia, and longitudinal gradients introduce
additional stress and dynamics. A resolved equilibrium wall remains covered
by the equilibrium-tube test; an appreciably driven wall requires its own
coupled equations. An ensemble with independently varying cross sections
also has extra state variables. Those broader bag models have a separate
scope from the tested common-cross-section family and the reoptimized
equilibrium/elastic-tube family.

## Literature and physical construction boundary

[Bolognesi and colleagues](https://arxiv.org/html/1408.1572v3) provide an
explicit large-flux vortex limit in which magnetic energy balances scalar
potential energy inside a tube. At fixed flux, increasing the cross section
reduces magnetic energy and increases potential energy. This gives a useful
finite-dimensional check before attempting a general field evolution.

These gauge/scalar actions supply theoretical constitutive candidates.
Their mapping to available matter remains a physical requirement. In
particular, the Standard Model embedding has its own stability problem:
[Forgacs and Lukacs](https://arxiv.org/abs/1909.07447) find their electroweak
strings with an added dark condensate become unstable as the mixing angle
approaches its physical value. A laboratory condensate analogue likewise
requires its host's rest energy and mechanical tensor in the gravitational
accounting.

The positive local result identifies a useful stress correlation. The
conserved-bundle, graded-support, elastic-envelope, and bag results identify
the response that this realization lacks. Within the radial tube realization,
the amount or type of ground-state prestress at a fixed rail label must be
able to change during the schedule, or a different interaction stress must
carry the changing demand. Ordinary excitations of a permanent equilibrium
bundle supply insufficient freedom
within the tested family.

The bounded investigation stops at that physical construction boundary.
A further field construction needs an independently specified mechanism for
changing the condensate state, orientation, or distribution, with its carrier
energy, reciprocal force, and continuing rail connections counted. The cited
literature supplies the relevant stress ingredients and their stability questions; it supplies
no completed active-rail implementation of that response. The improved tensor
allocation remains a numerical source target. The technical disclosure and
its PDF retain their established design content.

## Evidence and validation

The [response-family results](data/scalar_flux_response_family/summary.json),
[retained-target audit](data/scalar_flux_support_gate/summary.json),
[potential-optimum audit](data/scalar_flux_response_audit/summary.json),
[conservative blend](data/scalar_flux_support_blend/fraction0.9_summary.json),
and [blend audit](data/scalar_flux_blend_audit/summary.json) preserve the
allocation and work comparisons. The [direct grading test](data/graded_vortex_support_gate/summary.json)
records its refined iteration limit. The
[eliminated grading test](data/graded_vortex_eliminated_gate/summary.json)
resolves both cases and archives the short contradiction matrices and weights.
The [exact certificates](data/graded_vortex_exact_certificates/summary.json)
provide the rational verification of both archived representations.

Nine focused tests compare the local cone with independent component
programs, verify conserved expanding and squeezed tube controls, check product
bounds and elastic-envelope inclusion, and compare temporal elimination with
independent complete linear programs. Independent cases run in parallel with
a configurable worker count. Each completed calculation records input and
output hashes in its manifest. Final verification passes 825 hash comparisons
over 126 distinct files and independently multiplies both exact rational
certificates back into their archived matrices. The new numerical evidence
occupies approximately 48.4 MB.
