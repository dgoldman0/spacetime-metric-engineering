# Driven radial support cells

A phase-volume model of locally driven radial support cells admits the two
tested startup histories after counting causal drive and return waves,
conversion heat, guide-field energy, and a finite interface allowance.
Reconstructed controls pass both interval-envelope checks and independent
wave replay on the active geometry. This retains a useful local control
candidate, with phase-front dynamics, complementary current transport, and
material attachments still requiring construction.

The shared local store supplies the limiting continuation. Negligible-pressure
and isotropic-radiation stores exceed the prescribed budget. Directed
radiation gives a favorable pressure response, while its counted axial
restraint again exceeds the budget; the selected histories also conflict
with the existing angular jackets. A connected power and axial-support
implementation remains the required broader construction.

The calculation uses the scheduled active-rail backing, pressure link, and
standing-support connections from the
[scalar/flux construction](SCALAR_FLUX_SUPPORT_CONSTRUCTION.md). The
capacitor, endpoint heat/current medium, power delivery, and mechanical
support retain their separate roles. The two-cell proposal is a candidate
physical realization of the backing response. Its relevant background is the
active schedule on `-2.1 <= x <= -0.5`, `0 <= t <= 1.285`.

## Counted homogeneous controller

[Ishihara and Ogawa](https://arxiv.org/html/2103.13732v1) specify a canonical
matter scalar, Higgs scalar, gauge field, and positive interaction between the
two scalar amplitudes. Their equations and tensor provide a concrete
adiabatic controller test. Let `f` be the Higgs amplitude, `u` the matter
amplitude, and

```
V0 = lambda eta^4 / 4,
z = f^2 / eta^2,
V = V0 (1-z)^2,
I = g f^2 u^2.
```

On the suppressed-Higgs branch `0 <= z <= 1`, homogeneous stationary matter
motion gives `K_u=I`. The Higgs amplitude equation gives
`I=2 V0 z(1-z)+K_f`, where `K_f` is its nonnegative covariant temporal kinetic
energy. Consequently the scalar and controller together supply

```
(rho_s,p_r_s,p_t_s)
    = (4 sqrt(V V0)-3V, -V, -V) + K_f (3,1,1).
```

The last term belongs to the already admitted radiation basis. Setting it
to zero and relaxing charge-screening constraints gives the most favorable
local controller budget used here. Scalar gradients, interfaces, and driven
departures from the homogeneous stationary equations have separate tensors
and equations. The result therefore bounds this adiabatic amplitude branch;
it does not exclude general time-dependent field evolution.

The additional controller cost is `4(sqrt(V V0)-V)`. It vanishes at the two
end phases and is positive at intermediate amplitudes. A controller that
holds the entire cell at an intermediate field amplitude therefore changes
the energy requirement of the earlier potential-only allocation.

## Exact local and temporal test

After subtracting the complete scalar tensor, the remaining positive-energy
components are radial electromagnetic fields, radial and angular radiation,
angular membranes, and rest inventory. Their minimum energy gives

```
rho_needed(V;V0) = max(
    p_r+2p_t + 4 sqrt(V V0),
    p_r-p_t + 4 sqrt(V V0)-3V,
    -2p_r-p_t + 4 sqrt(V V0)-6V).
```

The minimum over `0 <= V <= V0` occurs at an endpoint or at one of the
pressure-basis crossings `V=-p_t`, `V=-p_r`, `V=-(p_r+p_t)/2`. Between these
crossings each active expression is concave. Thus five candidate evaluations
resolve the continuous amplitude problem.

An independent calculation obtains the complete interval of permitted
`V0` at every sample. If the auxiliary fields alone carry the target, this
interval is unrestricted above. Otherwise, for the previously derived
ideal potential interval `[V_l,V_h]`, define

```
B(V) = min(rho-p_r-2p_t,
           rho-p_r+p_t+3V,
           rho+2p_r+p_t+6V).
```

The permitted core heights are
`V_l <= V0 <= max_[V_l,V_h] B(V)^2/(16V)`. The same crossings and interval
endpoints suffice for this maximization. Intersecting these intervals through
time tests one fixed field potential at each position. Allowing an arbitrary
different `V0(x)` at every spatial sample makes the test more permissive than
two cells sharing one material potential.

The independent dense audit uses 2057 times and 1025 positions, including
the physical cuts and all source knots.

| Target | Worst location | Required `V0` | Permitted `V0` | Incompatible positions |
| --- | --- | ---: | ---: | ---: |
| Retained `f=0.99` | `x=-1.15` | 0.177190 | 0.146365 | 312 / 1025 |
| Improved scalar blend | `x=-1.5` | 0.207310 | 0.080261 | 851 / 1025 |

At `x=-2`, the intervals are now nonempty: `[0.017105,0.029191]` for the
retained target and `[0.014855,0.021709]` for the improved target. Thus this
controller removes the particular startup restriction that rejected the
permanent tube at that location. The whole backing still has incompatible
temporal requirements. Replaying the smallest core height required at each
position produces maximum density deficits 0.058806 and 0.372080,
respectively. These are fixed-target results; the material-response controls
have yet to be reoptimized for this controller.

## Direction supplied by the controller result

The two end phases carry the favorable scalar stress without the homogeneous
intermediate-amplitude penalty. Changing their occupied volume replaces that
bulk cost with phase-boundary energy, motion, currents, and conversion work.
An average potential `V=F V0`, with phase fraction `0 <= F <= 1`, makes this
distinction explicit. The boundaries and the shared power/reservoir connection
then determine whether the apparent bulk saving survives.

There is a concrete condensed-matter analogue for that control architecture.
[Berdiyorov and colleagues](https://www.nature.com/articles/s41598-017-11659-2)
simulate injection, storage, merger, and splitting of magnetic flux domains
in type-I superconductors using applied currents and engineered pinning
regions. Their flux domains exchange individual flux quanta and dissipate
energy. This supplies an example of configurable domains and a reservoir;
the gravitational energy accounting of a physical superconductor additionally
includes its host material. Its condensation free energy alone supplies no
rail-scale stress-to-total-energy demonstration.

## Two cells with a common power port

The phase-volume comparison uses the retained `f=0.99` schedule. An adjustable
balanced field/potential contribution has
`(rho_s,p_r_s,p_t_s)=(A/R^2,-A/R^2,0)`. Its required material-frame power and
radial force are

```
P_s = A_t/(N R^2),
F_s = -(A_x/ell + v A_t/N)/R^2.
```

Two finite feeding regions share a middle power port. Absorbed radial waves
travel outward from that port, while recovered waves travel back to it. A
positive backward transport solve supplies the minimum prepared absorption
inventory; forward transport evolves recovery. The two streams, the phase
amplitude, conversion heat, and complementary material budget are optimized
together. The remaining radial current is balanced by a separately counted
counterstream. The optimization includes the full auxiliary component cone.

This first comparison allows distributed actuation inside each feeding
region, ideal conversion efficiency, and zero interface energy. It therefore
tests a favorable transport limit. The source-free propagation coefficients
come from the prescribed active metric, and the local conversion exchanges
cancel algebraically. The registered support target retains its previous
continuum force residual.

| Pair width in rail coordinates | Pair center | Additional density required |
| ---: | ---: | ---: |
| 1.6 | -1.3 | 0.0143110 |
| 0.05 | -1.9875 | 0.00368280 |
| 0.005 | -1.9875 | 0 within `2e-7` |
| 0.0005 | -1.9875 | 0 within `2e-7` |

Each comparison uses 24 spatial cells and 132 temporal samples. For width
0.005, the maximum travelling rest density is 0.009095. The two individual
feeding regions have proper lengths between 0.00745 and 0.02806 in the
project's length unit during the schedule. Their common port receives
0.10114 units of incident work and returns 0.21720 units over the sampled
interval. The minimum initially stored energy for an isolated pressureless
buffer is 0.10059. That particular optimized schedule leaves insufficient
spare energy for the isolated buffer through the whole interval. The port
therefore remains an external supply and recovery interface in the passing
transport comparison.

The narrowing comparison also changes the sampled neighbourhood: the narrow
pairs sit between the earlier startup witnesses. A follow-up must test those
witness locations directly, resolve the temporal and spatial transport,
restrict each cell to a coherent amplitude, and include conversion loss and
heat return. Interface and guide stresses remain additional requirements.

## Coherent cells and independent wave replay

The next comparison places pairs directly around `x=-2` and `x=-1.975`.
Each physical cell has one amplitude through its whole radial extent.
Conversion efficiency is 0.98; conversion losses travel back to the common
port in a separately tracked thermal stream. Two end membranes per cell have
surface energy `sigma=1e-7` in project units, represented by their volume
average `rho_wall=2 sigma/(ell cell_width)` and angular tension
`p_t_wall=-rho_wall`. This is a finite energy allowance for interfaces; their
resolved profiles and mechanical attachment remain construction requirements.

The implicit transport optimization initially admits widths 0.005 and
0.0005 at both locations with 24 spatial cells, 260 time nodes, and a 0.1%
reserved density margin. Replaying its fixed controls with the independent
limited finite-volume SSP RK2 solver changes that assessment. At width
0.005, the maximum density deficits are 0.001617 at `x=-2` and 0.014184 at
`x=-1.975`. The latter needs density 0.063002 where the target provides
0.048818, near `t=0.05521`. Both explicit wave ledgers close to better than
`1.1e-18` in their finite-volume balance. The unresolved issue is transient
inventory under the selected controls, rather than an energy-ledger leak.

The width-0.0005 replay at `x=-1.975` also fails, by 0.001451. At `x=-2`,
the secondary inventory optimization fails numerically; its retained primary
solution contains large simultaneous conversion cycles and small negative
increments at solver tolerance. Explicit evolution rejects that candidate
on positivity. It therefore supplies no accepted narrower-cell result.

These replays withdraw the preliminary transport clearances. A revised
discretization uses a positive matrix exponential for each time panel and
tests stresses at panel midpoints as well as at nodes. Its source amplitude
and conversion increments are shared by each complete physical cell. A
separate guide check allocates guiding magnetic energy from the field already
present in the core and auxiliary mixture. These changes address the
identified numerical and component-accounting gaps directly.

## Exponential transport and temporal refinement

The exponential calculation uses all 515 original time nodes, a 0.2%
reserved density margin, and pair width 0.0005 at both startup locations.
Each run has 24 spatial samples. It includes 98% conversion efficiency,
thermal return, and the same finite membrane allowance. A guide requirement
corresponding to a drift bound of 0.5 is supplied from existing core and
auxiliary radial field energy. This bounds the electromagnetic guide
contribution for the explicit transport streams; current-carrier inertia
and the complete guide geometry remain separate construction requirements.

Both optimized controls pass independent replay at 48 spatial samples and
1029 time samples. The smallest remaining density margins are 0.00010765
at `x=-2` and 0.00007134 at `x=-1.975`. The largest travelling densities are
0.0015582 and 0.0021441. The wave ledgers close within `1.2e-19`; conversion
increments remain positive and contain zero simultaneous forward/reverse
cycling. This supplies a positive result at that resolution. The further
replay at 96 spatial samples and 2057 time samples resolves brief overloads
between the previous sample times: 0.0011494 at `x=-2` and 0.0010623 at
`x=-1.975`. The local clearance therefore fails temporal refinement. A
positive supersolution for each wave operator can bound the inventory
throughout a control interval and directly address this sampling failure.

The common power port still connects to an external supply and recovery
system. A post-processing comparison of these schedules finds insufficient
space in their stress budget for an isolated pressureless shared buffer.
The controls were selected by minimizing travelling inventory, so that
comparison supplies a reason to optimize the store and cells together.
The source target remains the retained `f=0.99` history; the lower-null-load
scalar blend has a different angular-stress requirement.

## Joint shared-reservoir comparison

The next calculation optimizes the two coherent amplitudes, travelling waves,
and shared stored energy together. A reservoir has
`(rho_b,p_r_b,p_t_b)=(b,w_r b,w_t b)`. Its energy is distributed with fixed
material-volume weights over the pair, granting perfect internal mixing.
The common-port flux is integrated with an augmented matrix exponential on
each panel. Useful return work recharges the store; conversion heat leaves
through the existing thermal-return channel. Reservoir energy obeys

```
dE_b/dt = P_return,useful - P_incident
          - integral(b [w_r d(log ell)/dt + 2 w_t d(log R)/dt] dVolume).
```

The calculation charges this energy and pressure against the same support
target. It leaves the store's redistribution stresses, confinement, and host
mass open. The geometric-work integral uses midpoint time quadrature.
Flat-space tests independently conserve the combined core, wave, store,
and exported-heat energies. The rail reservoir ledgers close within
`2.1e-12` in project energy units.

| Reservoir pressure ratios `(w_r,w_t)` | Density deficit at `x=-2` | Density deficit at `x=-1.975` |
| --- | ---: | ---: |
| Negligible pressure `(0,0)` | 0.0133824 | 0.0165346 |
| Isotropic radiation `(1/3,1/3)` | 0.0133931 | 0.0159377 |
| Directed counterpropagating radiation `(1,0)` | 0 | 0.00002822 |

Deficits refer to the target with its 0.2% numerical reserve. The directed
store at the second location misses that reserve by less than its full
amount. These are allocation comparisons; both directed cases require a
separate confinement check. Their optimized histories also contain large
simultaneous conversion cycles, which use the converter losses to export
heat. This grants a favorable dissipative control channel whose physical
phase-front realization remains open.

The directed case at `x=-2` begins with reservoir energy 0.0023283 and exports
0.0148129 as heat. Near `t=0.0727832`, even the maximum radial tension
available from its core and auxiliary field falls below the stored axial
radiation pressure. Integrated over the pair, the deficit is 0.0152582 in
project energy units. Thus the initial directed-storage allocation requires
an external axial reaction. The next comparison places the confinement
requirement inside the optimization and permits use of the radial field
already present in the support mixture.

## Axial restraint for the local directed store

For directed stored radiation, let its density be `b` and the balanced core
density be `s`. The auxiliary radial field can occupy at most

```
E_aux,max = (rho-p_r+p_t-2s-b)/3.
```

A locally contained, quasistatic store needs radial tension to balance its
axial radiation pressure. Granting the store every radial tensile field in
the pair gives the generous integrated condition

```
integral(s + E_aux,max - b) dVolume >= 0,
equivalently integral(rho-p_r+p_t+s-3b) dVolume >= 0.
```

This comparison reuses the core and auxiliary field already counted in the
tensor. It adds zero host or attachment mass, and permits restraint to be
shared across the complete pair. Reoptimizing with this condition requires
additional density 0.0123869 at `x=-2` and 0.0147331 at `x=-1.975`. Both
deficits greatly exceed the 0.2% numerical reserve. Reservoir energy ledgers
close within `9.7e-14`. The local confined-storage realization therefore
exceeds the prescribed support budget even under these favorable allowances.

The confinement comparison concerns a locally contained quasistatic module.
[Giulini's treatment of Laue's theorem](https://arxiv.org/abs/1808.09320)
identifies the conservation, stationarity, and boundary assumptions behind
integrated stress cancellation for an isolated system. The active rail has
time-dependent fields and continuing support connections; those connections
can transmit an external axial reaction, with their own energy, stress, and
work requirements. Thus the confined-module failure selects a system-level
load-transfer problem for an externally supported implementation.

The existing spherical angular jackets provide a separate closure option.
A cross-check grants the two selected directed-store histories their maximum
available radial-field restraint, then asks a jacket to carry the remaining
end pressure. At `t=0.0727832`, the left cuts require signed loads
`-0.239294` at the `x=-2` pair and `-0.298548` at the `x=-1.975` pair.
Every positive-energy jacket with `|angular stress| <= surface energy`
instead supplies force per unit surface inventory in `[0.455273,0.535885]`
and `[0.409016,0.479476]`, respectively. Their signs conflict regardless of
prepared surface energy. The right adiabatic jackets have empty allowed
initial-energy intervals. This cross-check covers those two selected
histories; it preserves the continuing-support alternative and its separate
load-transfer requirements.

## Bounding the full control interval

For a frozen-panel positive wave generator `G` and source rate `S`, a
nonnegative ceiling `z` satisfying `z >= y_initial` and `G z + S <= 0`
bounds the wave throughout the panel. Applying this condition to forward
recovery and backward absorption covers the transit peaks that the earlier
time samples missed. Stress gates use the ceiling at both panel ends and
at the midpoint, with the phase amplitude shared by each physical cell.

Both width-0.0005 locations admit zero added density in this stronger
optimization. The primary controls close the scaled equality constraints
within `2.9e-11`. Their secondary inventory minimizations fail, leaving
primary controls with simultaneous conversion and negative roundoff at
approximately `1e-9`. These raw controls therefore require an explicit
physical control reconstruction and a fresh wave replay. The source and
propagator comparisons remain available for verification.

The physical reconstruction sets phase amplitude to its nonnegative value,
changing it by at most `9.96e-10`. Each panel then uses the positive and
negative parts of the exact amplitude increment as its forward and reverse
conversion. This removes simultaneous cycling and preserves phase work.
The new control archive contains zero previously computed wave histories.

Fresh exponential evolution and a triangular upwind obstacle solve rebuild
the least positive wave ceiling for each panel. The resulting minimum
density margins are `0.000112148` at `x=-2` and `0.0000971534` at `x=-1.975`.
The ceiling inequalities close within `1.14e-12`, and the actual target and
boost factors are evaluated at five times per panel. These bounds cover
continuous wave evolution for the frozen-panel transport coefficients. The
separate explicit replay tests evolution on the changing active geometry.

That replay evolves the reconstructed controls at 96 spatial samples and
2057 time samples per pair, using the independently implemented limited
finite-volume SSP RK2 solver. Both cases pass. The minimum density margins
are `0.0000974998` at `x=-2` and `0.0000624104` at `x=-1.975`; maximum
travelling densities are 0.00861794 and 0.00624494. Wave-energy balances
close within `3.46e-19`, and the reconstructed controls contain zero
simultaneous conversion cycles. This retains the local stress and
work-transport result after the earlier sampling failures have been resolved.

## Construction requirements retained by the comparison

The local allocation includes phase/potential energy, drive and recovery
waves, transported conversion heat, a complementary counterstream, radial
guide energy, angular support, and the stated interface allowance. The
counterstream has an assigned positive stress tensor; its transport and
exchange law remain part of the required material construction. The phase
fronts, current-carrier rest energy, and resolved mechanical attachments
also retain their own equations and loads.

The reservoir comparison distinguishes the useful pressure response from
the force needed to contain it. Directed radiation supplies compression
efficiently when the schedule reduces radial prestress. Housing that energy
inside a self-contained module requires a compensating axial reaction, which
exceeds the tested local budget. The selected histories also conflict with
the existing angular-jacket response. A connected implementation therefore
needs coordinated power delivery, heat return, and axial load transfer
through the continuing support. This is the construction limit reached by
the two-cell/shared-reservoir investigation; the capacitor retains its
electrical storage role throughout.

## Reproduction

The [controller gate](data/virtual_cell_controller_gate/summary.json) contains
the two node and two dense runs. Each spatial temporal interval and its
witness times is retained in compressed arrays. Four focused tests compare
the exact energy minimum with independent global optimization, check the
height intervals against independently minimized costs, reconstruct the
controller energy directly, and check shared-buffer conversion bookkeeping.
Independent histories run with four worker processes. The manifest hashes
the archived inputs, source code, tests, and outputs. The disclosure and its
PDF retain their design content.

The [first transport comparison](data/virtual_cell_transport/summary.json)
retains the optimized amplitudes, both wave histories, heat, required
reaction forces, and common-port energy histories. Four further tests check
the finite-volume boundary balance, a constant-tension control, the cost of
changing pure tension, and conversion heat with finite membrane energy.

The [coherent heat-return runs](data/virtual_cell_coherent_heat_return/summary.json)
and [independent wider-cell replay](data/virtual_cell_independent_replay/summary.json)
retain the controls and transient failures. The
[narrower replay](data/virtual_cell_narrow_replay/summary.json) records its
completed `x=-1.975` case and the numerical positivity failure at `x=-2`.

The [exponential transport cases](data/virtual_cell_semigroup/summary.json)
and their [independent replay](data/virtual_cell_semigroup_replay/summary.json)
retain the short-cell controls, finite wave histories, guide comparison,
and original sampled margins. Their
[finer replay](data/virtual_cell_semigroup_replay_refined/summary.json)
records the subsequent transient failures. Four additional tests check the exact
single-cell propagator, positivity at large transit Courant number, a
constant-tension control, and the monotonic cost of adding a guide bound.

The [joint reservoir cases](data/virtual_cell_joint_reservoir/summary.json)
contain the three pressure laws at both startup locations. Four additional
tests compare the integrated port flux with analytic decay, conserve the
full flat-space inventory with ideal and lossy conversion, and verify the
additional restriction imposed by closing an unrestricted external port.

The [confined reservoir comparison](data/virtual_cell_confined_reservoir/summary.json)
adds the integrated axial-restraint gate. An additional test checks that
confinement tightens the directed-store allocation and independently
reconstructs its integrated tension allowance.

The [interval-envelope cases](data/virtual_cell_wave_envelope/summary.json)
preserve the raw controls and wave ceilings. Two additional tests verify
positive-supersolution bounds between samples and the stronger restriction
imposed by the full-panel wave ceiling.

The [reconstructed controls](data/virtual_cell_reconstructed_controls/summary.json)
record every amplitude correction and remove the previous wave solution.
Their [rebuilt interval envelopes](data/virtual_cell_reconstructed_envelopes/summary.json)
use fresh propagation and a triangular obstacle solve, independently checked
against linear optimization. Three control tests check phase-work balance,
the reduction in conversion heat after cycle removal, and rejection of
substantial negative phases.

The [final independent replay](data/virtual_cell_reconstructed_replay/summary.json)
contains the retained margins, actual travelling and thermal densities,
and complete sampled histories. The focused suite has 24 passing tests;
three existing surface-termination tests also pass. Archived manifests
retain the source version used by each calculation. Earlier source hashes
resolve to their staged commits as the implementation evolves.

The [angular-jacket cross-check](data/virtual_cell_jacket_crosscheck/summary.json)
retains the left-cut sign witnesses and right-cut surface-work conflicts.
