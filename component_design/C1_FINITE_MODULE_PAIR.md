# C1 finite assembly and neighboring overlap

17 September 2026.

The first C1 test article assigns a finite radial electric source to two
mechanically separate material assemblies. Their electric fields overlap on
one prescribed standing geometry. Each assembly carries its own charged
populations and internal radial and angular support. Mechanical traction
vanishes at each assembly's radial ends, while electromagnetic interaction
transfers momentum between the populations.

This construction follows the [topology decision](../supporting_reports/RAIL_BUILD_TOPOLOGY_DECISION.md)
and the [source-selection preference](../supporting_reports/SOURCE_CONSTRUCTION_SELECTION.md)
for specified fields and materials. It supplies an initial Maxwell source
and static support requirement. A complete module additionally contains the
remaining source sectors, finite hardware, and their evolving states.
The [standing screen](../supporting_reports/C1_FINITE_MODULE_PAIR_SCREEN.md)
records the numerical comparisons and their acceptance limits.

## Common geometry and boundaries

The standing comparison uses

\[
ds^2=-A(x)^2dt^2+B(x)^2dx^2+R(x)^2d\Omega^2.
\]

Its lapse and spatial metric are the archived phase-0.745 reference used by
the geometry/source reassessment. Setting the shift and time derivatives to
zero defines the same static surrogate used for that source comparison.
The archived active metric retains its own shift, time dependence and service
checks. A source-derived C1 trajectory will require those additional equations.

The [signed-source channel screen](../supporting_reports/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md)
retains this geometry, electric-source placement and both material-domain
brackets. Its added trial quantum channels have outer reflecting ends inset
by 0.05 coordinate units, giving quantum overlaps \([0.55,2.45]\) and
\([0.55,0.95]\). Internal optical compartments and their mode counts vary in
that source comparison. The physical quantum layout remains a construction
choice, with its radial and angular tensor and finite boundaries supplied jointly.

For an overlap interval \([a,b]\), module L occupies radial labels
\([-3,b]\), and module R occupies \([a,3]\). Source flux tapers smoothly to
zero at each module end. Each material support has zero density and radial
and angular pressure at its two ends. All distances and times retain the
reference's dimensionless geometric normalization:

\[
L_{\rm overlap}=\int_a^b B\,dx,\qquad
t_{\rm light}=\int_a^b B/A\,dx.
\]

These domains describe spherically averaged source populations. A physical
embedding must assign distinct material locations, angular coverage, clearances,
field penetration and load paths within their common radial band. The module
may be a coordinated cluster, consistent with the topology decision. Full
shell averages alone leave this three-dimensional packing requirement open.

## Finite electric source and interaction

Use \(c=\epsilon_0=G=1\), with flux per solid angle \(Q=R^2E\). A common
flux envelope is constant through \(|x|=1\), tapers with a quintic smoothstep,
and vanishes at \(|x|=3\). Its throat electric tension is 95% of the
reference throat radial-tension magnitude. This fraction supplies a comparison
load; electric angular pressure and the remaining source are counted separately.

Let \(h\) rise smoothly from zero to one through the overlap. The two fields
have fluxes

\[
Q_L=(1-h)Q,\qquad Q_R=hQ,\qquad
\rho_{q,i}=\frac{\partial_xQ_i}{BR^2}.
\]

Both modules have zero total charge because each flux vanishes at both ends.
Their positive and negative charge inventories remain present. The shared
Maxwell tensor and material Lorentz forces are

\[
u_E=\frac{(Q_L+Q_R)^2}{2R^4},\qquad
T_E=(u_E,-u_E,u_E),\qquad
F_i=\rho_{q,i}\frac{Q_L+Q_R}{R^2}.
\]

Tensor channels are \((\rho,p_r,p_t)\). The interaction energy
\(Q_LQ_R/R^4\) belongs to the shared field ledger. At equal field amplitudes
it supplies half the total local electric energy. A separated self-field sum
therefore requires this cross term. The force sum satisfies
\(\nabla_aT_E^{a\hat l}=-(F_L+F_R)\).

The static charge distributions establish finite field termination. Preparing,
changing and recovering them requires conserved finite currents, induction
fields, power conversion and charge binding. Those interfaces belong inside
the corresponding module or to explicitly counted electromagnetic exchange.

## Separate internal supports

Each module's material tensor obeys

\[
\partial_l p_{r,i}+(\partial_l\log A)(\rho_i+p_{r,i})
+2(\partial_l\log R)(p_{r,i}-p_{t,i})=F_i,
\qquad \rho_i\geq |p_{r,i}|,|p_{t,i}|.
\]

Radial stress can carry a local charge force to another location within that
module. The simpler angular-only contact has force interval
\([\partial_l\log A-2|\partial_l\log R|,
\partial_l\log A+2|\partial_l\log R|]\rho\); it supplies a useful necessary
screen for a local contact. A finite connected support inside one module
has the larger tensor freedom of the displayed equation.

The numerical comparison minimizes proper material energy. A bounded variant
also caps each material density at four times the reference throat electric
density and limits the proper gradients of density and angular pressure to
that cap per unit proper length. These are declared comparison envelopes.
An identified material must supply its own allowable stress, gradients,
response speeds, stored energy and stability. The zero mass-per-charge
coefficient grants the most favorable carrier-cost relaxation; absolute charge
inventories are recorded for subsequent physical normalization.

## Complete module responsibilities

| Responsibility | Location and interface in C1 | Current input |
|---|---|---|
| Bulk radial and angular source | Each module's fields, charged material and internal support; summed once in the overlap | Finite electrostatic field plus bounded static support comparison |
| Signed radial and angular source | Separately specified quantum components and their material boundaries through the occupied and overlap regions | Conditional radial-channel plus angular-target bulk allocation; reflector force requirements and a compatibility bound from the radial-only control |
| Endpoint current and support exchange | Medium and receiver within the finite assembly, with specified transfers to its stores | Archived fitted tensor and effective response evidence |
| Holding, conversion and heat | Finite stores, work routes, receiver and heat destination carried by each assembly or separately identified vehicles | Conditional local storage/interface results |
| Entry, handoff and release | Common geometric history supported by the overlapping source states | Service reference and causal preparation requirements |
| Motion and recovery | Assembly inertia, field momentum, external fluxes and station-keeping ports | Angular-resolved boundary and state model still required |

The six containment populations and six rotor copies retain their distinct
roles wherever that storage construction is selected. This first source
screen prices its added Maxwell and supporting tensors. Incorporating the
storage assembly requires its own physical cell measure and full tensor on
the same geometry; its earlier local capacities have a different measure.

## Motion, scheduling and advancement gates

The radial load integrals in the screen measure support duties. They are
scalar sums over solid angle. Translational recoil and torque require the
angular distribution and a declared frame for momentum balance. In particular,
the spherical average has discarded the directional information needed for
a free-flying vehicle trajectory.

A motion construction will retain initial and final position, orientation,
linear and angular momentum, internal energy and heat. It will integrate
material and electromagnetic boundary fluxes with background and tidal
forces at the chosen approximation order. Recovery includes displacement and
orientation as well as momentum: even in a local Newtonian control, successive
opposite constant-force pulses of duration \(\tau\) return the velocity while
leaving displacement \(F\tau^2/M\).

The first service cycle is preparation, standing hold, neighbor engagement,
packet handoff, release and reset. Each stage needs an actual state law and
causal communication paths; the static light time is an input to that schedule.
The earlier packet collar remains a service constraint and comparison case.

Advancement to that cycle requires a finite, physically separated source
assembly with supplied interactions and a viable remaining signed source on
the same geometry. The standing comparison identifies useful boundary
placements and support requirements. Constitutive evolution, quantum source
completion and three-dimensional embedding remain explicit gates before a
physical handoff claim. A later chain additionally needs collective response,
readiness propagation and chronology checks.
