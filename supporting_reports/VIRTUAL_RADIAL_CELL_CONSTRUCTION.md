# Driven radial support cells

A locally driven field pattern can vary the amount of radial prestress at a
rail location. The first construction test counts the condensate that controls
that variation. Adiabatic, spatially homogeneous amplitude control clears the
previous startup conflict at `x=-2`, while its complete local energy exceeds
the allowance elsewhere in both retained support histories. This locates a
specific distinction between changing a condensate's amplitude throughout a
cell and changing the volume occupied by its phases.

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
