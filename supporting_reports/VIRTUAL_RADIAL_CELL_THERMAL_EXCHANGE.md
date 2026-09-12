# Counted thermal exchange in the radial-cell assembly

A pressure-bearing reservoir, evolved jointly with the phase and balanced
radial radiation, clears the sampled local energy/cone gate at both tested
locations. The pressureless storage comparison retains the earlier small
deficit near `x=-1.975`. Keeping the previously accepted phase schedule
fixed instead requires substantial extra density for either reservoir.
The useful change is therefore coordinated pressure work and phase evolution.

This calculation continues the [connection audit](VIRTUAL_RADIAL_CELL_CONNECTION_AUDIT.md)
on the scheduled active-rail patch, with `f=0.99`, the protected packet's
existing exclusion, and the separate capacitor, pressure-link, endpoint,
and standing-support duties. The retained common-phase controls remain
the independently replayed transport comparison. The new local histories
are a necessary energy gate for constructing their coupled continuation.

## Reciprocal energy and the counted component budget

Let the phase carry `(s,-s,0)`, with `s=A/R^2`, and let the full balanced
radial radiation carry `(W,W,0)`. The original drive, useful return, and
heat waves are included in `W`; additional photons cancel their radial
current. A comoving reservoir has tensor `B(1,w,w)` and positive energy.

The two comparisons use `w=0` and `w=1/3`. Pressureless adjustable energy is
a favorable stored-excitation bound: conserved cold particle rest mass
alone cannot repeatedly convert into radiation. The pressure-bearing case
represents relativistic thermal energy. Its material carrier, confinement,
and microscopic exchange require separate accounting in a realization.

Define material measures

```
D = ell R^2,        M = (ell R)^2,
U = M W,           K = D^(1+w) B.
```

The phase and complete radial radiation have combined local power
`[U_t+ell^2 A_t]/(N M)`. The reservoir has power
`K_t/[N D^(1+w)]`. Requiring these powers to cancel gives

```
U_t + ell^2 A_t + (M/D^(1+w)) K_t = 0.
```

This assigns the counterstream's missing power to the counted reservoir.
The remaining auxiliary components retain the backing's original external
power duty. The test adds zero endpoint supply. Reassigning part of the
existing capacitor or support work to this exchange would define a different
joint construction with changed tensor and port histories.

The remaining positive field/radiation/membrane mixture gives three facets:

```
2s + B                  <= rho-p_r+p_t,
2s + (1-3w) B           <= rho-p_r-2p_t-3 rho_wall,
3W-s + (1+3w) B         <= rho+2p_r+p_t.
```

Thus the reservoir's energy and both pressures enter the original density
allowance. Its pressure changes the correlated stress requirement as well
as the geometric work. The finite interface allowance remains included;
extra carrier mass, confinement, and the guide floor are omitted in this
favorable local gate.

For piecewise-linear `A,K`, integration on each time panel is

```
Delta U + mean(ell^2) Delta A
        + mean(M/D^(1+w)) Delta K = 0.
```

Four- and eight-point Gauss rules evaluate the geometry means directly
from the registered metric. The linear program minimizes a uniform added
density while keeping `A,U,K` nonnegative. Prepared radiation and reservoir
inventories are free variables with their full local stress costs.

## Fixed and jointly evolving phase comparisons

The fixed-phase cases retain the averaged phase and the sampled physical
wave floor `W >= 2 max(u_absorbed,u_useful_return+u_heat_return)`. The
joint-phase cases optimize `A` independently at each position and allow
zero travelling inventory. This relaxation separates pressure/energy
compatibility from coherent phase control and causal work delivery.

The [32-case archive](data/virtual_cell_thermal_exchange/summary.json)
contains the two samples adjacent to each pair's central port, two equations
of state, both control choices, and 1029/2057 time samples. The finest
added-density results are:

| Pair center | Reservoir | Fixed phase, two adjacent samples | Joint phase, two adjacent samples |
| --- | --- | --- | --- |
| -2 | Pressureless stored excitation | 0.0106691 / 0.0107091 | 0 / 0 |
| -2 | Thermal pressure `w=1/3` | 0.0411613 / 0.0412047 | 0 / 0 |
| -1.975 | Pressureless stored excitation | 0.0216304 / 0.0216260 | 0.000380852 / 0.000370048 |
| -1.975 | Thermal pressure `w=1/3` | 0.0678047 / 0.0678017 | 0 / 0 |

The joint pressure-bearing cases also pass at 1029 times. The pressureless
deficits near the second port change by about `1.34e-7` and `1.33e-7`
under refinement. The fixed-control shortfalls vary more because their
wave floor resolves sharp traffic peaks; all remain positive on both grids.

Each archive retains primal histories, finite variable bounds, and dual
multipliers. An explicit constant-radiation competitor with sufficient
prepared reservoir energy bounds the required density allowance. The dual
evaluation includes both lower and upper variable bounds, including the
fixed phase and positive wave floors. Independent direct reconstruction
finds maximum panel residual `5.36e-13`, cone violation `3.61e-16`, zero
fixed-phase mismatch, and wave-floor violation below `8.7e-19`.

These finite input problems inherit the backing target's approximately
`0.3752%` continuum force residual and weighted power residual `1.33e-7`.
Their dual bounds certify the sampled optimization; background refinement
and changes to its work allocation have separate effects.

## Constitutive tests selected by the result

Conventional radiation hydrodynamics supplies reciprocal matter/radiation
four-forces. Its thermal power changes sign with the material temperature
relative to the radiation, while positive opacity damps the radiation
current. This structure appears in [Park's covariant formulation](https://arxiv.org/html/astro-ph/0601635v2#S2.SS3)
and [Sadowski and colleagues, equations 15–18](https://arxiv.org/html/1212.5050v2#S2.SS1).
For two radial directions, our specialization is

```
S_+ = kappa_a (c_eq(T)/2-c_+) + kappa_b (c_--c_+),
S_- = kappa_a (c_eq(T)/2-c_-) + kappa_b (c_+-c_-),
P_c = kappa_a (c_eq(T)-c),
F_c = -(kappa_a+2 kappa_b) j_c.
```

Nonnegative absorption and scattering require `j_c F_c <= 0`. Positive
emission or reversal populates an initially empty direction. The minimum
counterstream's resolved positive-power witnesses fail this passive damping
condition. The new energy gate permits additional photons, which therefore
have a physical purpose beyond smoothing the numerical controls.

A selective counterstream interaction also requires a physical frequency,
polarization, or spatial channel. Equal opacity acting on all balanced
photons has zero net thermal force, leaving the separately assigned phase
conversion and material attachments to satisfy momentum balance. Temperature,
opacity, and recoil must come from one evolving material model.

There is also an interpretation within the existing radiation components:
an isotropic energy `B` equals radial photons `B/3` plus angular photons
`2B/3`. The passing pressure response motivates a bounded check of angular
redistribution before introducing a new material reservoir. Its positive
scattering rates and its angular evolution impose constraints beyond the
arbitrary reciprocal exchange admitted by the local linear program.

The focused thermal-exchange, prior passive-phase, and counterstream suite
passes 18 tests. The numerical runner uses two independent workers with one
solver thread each. Input identities, source versions, and output hashes
are retained in the calculation manifest. The complete phase-front,
transport, force, and constitutive source construction remains open.

## Passive angular redistribution comparison

The simplest elastic angular-relaxation operator is
`C[I]=kappa[(W+B)/(4 pi)-I]`. Applied to opposed radial radiation plus
an isotropic distribution, its collision step transfers `kappa W` from
the radial population into the isotropic population. Its total local
power and force vanish. The operator and the distinction from the actual
Thomson angular kernel are discussed by [Achterberg and Norman](https://academic.oup.com/mnras/article/479/2/1783/5034957).

Treating the receiving population as exactly isotropic with zero flux
gives `K_t=N D^(4/3) kappa W >= 0`. The
[monotone-inventory comparison](data/virtual_cell_isotropization_gate/summary.json)
therefore adds `K_(i+1)>=K_i` to the joint pressure-bearing gate. It permits
arbitrary positive rates and prepared inventory, with zero travelling-wave
floor. A constant `K` and sufficiently prepared `U` supply the finite
feasible competitor used for its dual bounds.

| Position | Added density, 1029 times | Added density, 2057 times |
| --- | ---: | ---: |
| -2.00000260417 | 0 | 0 |
| -1.99999739583 | 0 | 0 |
| -1.97500260417 | 0.000300121 | 0.000299962 |
| -1.97499739583 | 0.000288798 | 0.000288640 |

The second port needs energy return beyond the geometric work allowed by
this perfect-isotropic receiving-population model. Maximum panel residual
is `6.76e-14`, cone violation `2.23e-16`, and primal/dual discrepancy
`1.78e-15`. The bidirectional thermal interpretation retains its separate
opening from the preceding comparison.

Finite scattering also requires angular dynamics. For an exactly isotropic
population, the radiation moment hierarchy generates a dipole from
`D_s B+4aB` and a quadrupole from shear. At vanishing flux, anisotropic
pressure, and higher multipoles, the quadrupole derivative is
`D_u pi^(ab)=-(8/15)B sigma^(ab)`. These follow from
[Maartens, Gebbie, and Ellis's covariant moment hierarchy](https://arxiv.org/html/astro-ph/9808163v2#S6).
Scattering relaxes a finite quadrupole; it leaves a shear-driven correction
to the perfect-fluid tensor.

Moreover, a tensor decomposition of one evolving angular distribution has
geometric exchange between its apparent radial and isotropic parts. In a
homogeneous anisotropic local check with `delta=theta_r-theta_t`, the
radial-plus-isotropic fourth moment gives
`D_u B+(4/3)Theta B=kappa W+(8/15)delta B`. Thus monotonic `K` tests the
separately maintained perfect-isotropic comparison. Full angular transport
has additional flux and shear-work terms and remains a distinct construction.

The selected continuation restores coherent paired phase and actual causal
drive/return/heat waves to the bidirectional pressure-bearing energy gate.
Its purpose is to determine whether the useful local opening survives the
work-delivery duties already present in the radial-cell architecture.

## Coherent thermal response with work-wave transport

The coupled finite-cell model gives each pair one phase history and each
spatial sample its counted `U,K` inventories. It restores 98% beam/phase
conversion, separate heat return, the guide comparison 0.5, interface
surface allowance `1e-7`, and a 0.2% numerical density reserve. Positive
exponential propagation supplies the drive and recovery waves. Whole-panel
wave ceilings constrain `W` at both ends and the midpoint of each panel.
Thermal exchange uses the midpoint geometry in its panel power balance.

The [12-cell, 132-time pilot](data/virtual_cell_thermal_transport_pilot/summary.json)
requires added density `0.00132490` at `x=-2` and `0.00312356` at
`x=-1.975`. Independent reconstruction of the complete component cone agrees
with these values to about `1e-9`. The retained controls have large phase
changes just after `t=0.5`, when thermal and radial-photon inventories
compete with the changing core and guide requirements.

Prepared or converted radiation contributes substantially to this conflict.
At the final time the total radial radiation peaks at `0.09844` and
`0.24432`, while the actual travelling-wave floors there are approximately
`0.000267` and `0.000291`. At one tight second-pair sample near `t=0.507`,
the envelope floor exceeds the instantaneous wave floor, so temporal
resolution also matters. These histories therefore motivate refinement
before assigning the pilot deficit to the continuous construction.

Reintegrating the fixed pilot `A,K` histories using eight-point Gauss geometry
changes the required radiation density by at most `6.56e-7` and `1.53e-6`.
The corresponding cone changes are much smaller than the pilot deficits.
This checks the energy-weight quadrature; the independent wave propagation
and optimized control resolution remain separate questions.

The [24-cell, 515-time comparison](data/virtual_cell_thermal_transport_refined/summary.json)
reaches the dual-simplex time limit at both locations, with no returned
primal state. Each primary optimization has a 300-second allowance. These
are unresolved refined cases. The archive preserves the numerical status
and exact inputs for a solver-method comparison on the same model.

The new `B` can also represent additional internal energy in the existing
pressure-link fluid, with `U_fluid,new=U_fluid,old+D B` and its already
counted particle inventory. That interpretation changes the fluid's pressure,
temperature, and reciprocal contact law together. Its entropy and force
equations still require a joint solution. The registered beam/phase
efficiency applies to that converter; a thermal-to-work conversion would
have its own entropy and receiving-temperature requirements.

The complete virtual-cell, driven-condensate, and surface-interface suite
passes 70 tests at this stage. Four new semigroup tests cover a static common
core, driven conversion with actual wave/counterstream/heat inventory, an
incompatible disappearing energy capacity, and model-option validation.
