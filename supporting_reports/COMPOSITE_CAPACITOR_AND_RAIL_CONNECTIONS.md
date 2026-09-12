# Composite capacitor and rail connections

The capacitor candidate consists of charged tensile skins, a separate radial
backing, the existing pressure medium, and bidirectional electrical contacts.
Its mechanical connections determine whether electrode loads are balanced
inside each cell or transmitted to the standing rail support. This study
evaluates those alternatives on the scheduled active-rail patch, including
credit for the pressure medium already present.

The first calculation identifies a distinction between storing charge and
supporting the charged assembly through the prescribed deformation. A passive
skin and directional backing covering the electric tractions require about
171.53 units of initial material energy and reach 1,864.41 at fade. Allowing
controlled unloading greatly reduces the instantaneous material inventory;
the resulting electrical and mechanical exchange must then be supplied through
the assembly's connections. The continuation below evaluates that exchange.

## Architecture and material basis

The controlling geometry is the prepared, scheduled carrying flow with its
protected packet, collars, and release interval. The capacitor occupies the
existing endpoint support patch, x in [-2.1,-0.5], over s in [0,1.285]. The
standing radial support, angular jacket, endpoint heat/current medium, delivery
guides, and thermal receiver retain distinct roles. The
[architecture scope review](ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md) and
[finite work interface](FINITE_WORK_INTERFACE.md) specify that decomposition.

The charged-skin material basis is a phase boundary carrying trapped charged
fermions. Its leading surface thermodynamics are

    Sigma = tau + C n_s^(3/2),
    P = -tau + (C/2) n_s^(3/2).

Consequently a tension-dominated skin supplies P/Sigma near -1, while its
positive pressure approaches Sigma/2. The slope dP/dSigma at fixed tau is
1/2. Charge injection changes the carrier energy as well as the electric
field energy. For skin area A and carrier number N, the required additional
chemical port follows from U=tau A+C N^(3/2)/sqrt(A). This relation is
implemented and checked independently against area variation. The model's
trapping phase and couplings remain material hypotheses.
[Morris, *Charged Vacuum Bubble Stability*](https://arxiv.org/abs/hep-ph/9810420)
provides the charged-wall construction underlying this surface model.

A related constitutive lead is Peter's
[surface current-carrying domain wall](https://arxiv.org/abs/hep-ph/9503408).
It computes surface energy and tension from a scalar-wall/condensate model,
with a carrier localization threshold. That calculation treats the current
symmetry as global and omits long-range electromagnetic interactions. A rail
electrode would require the gauged finite-layer problem, its confinement
energy, and the electrical contacts. These models therefore identify
constitutive building blocks for the tensile skin; the separate backing
and rail connections carry the remaining construction duties.

For the backing, the numerical screen includes directional pressure, an
isotropic causal stiff-fluid limit, and a radiation-pressure fluid. The
tensile skins remain separate in each case. A general anisotropic material
saturating the dominant energy condition supplies an optimistic comparison.
Its energy inequality alone supplies no finite material realization.

## Existing pressure receives an explicit credit

Write u for electric energy density and p_* = min(p_fluid,u) for the existing
isotropic pressure allocated to the cell. New material must then supply

    delta p_r = u-p_*,       delta p_t = -u-p_*.

The pressure credit reduces the radial backing requirement and increases
the skins' tangential load. The following minimum added densities include
both effects:

| Added material family | Minimum added energy density |
| --- | ---: |
| General anisotropic DEC floor | u+p_* |
| Directional compression backing plus tensile skins | 2u |
| Isotropic stiff-fluid backing plus tensile skins | 3u-p_* |
| Radiation-fluid backing plus tensile skins | 5u-3p_* |

In the directional composite, the backing costs u-p_* and the skins cost
u+p_*. Thus reusing the existing pressure leaves the minimum added density
at 2u. For isotropic backing, the skins supply tension 2u, including the
backing's angular pressure. Existing fluid energy stays in the source ledger.
The remaining macroscopic pressure of electric field, allocated fluid, and
new support is the pressure of the unallocated fluid. All comparisons use
the complete boosted tensor.

At full recovery, the existing pressure supplies about 10.75% of the electric
load under an electric-energy/proper-duration weighting. This quantity is
a load-allocation diagnostic. A physical arrangement must implement the
subcell pressure distribution and its connections.

## Passive preparation and controlled unloading

Let ell=Gamma B, D=ell R^2, H_e=H-S, and U_E=H_e ell/R^2, per coordinate
material label and solid angle. The elementary electric cell has

    q=sqrt(2 H_e),       1/C=ell/R^2,
    Delta U_E = W_electrical + W_mechanical,E.

Endpoint product averages give an exact discrete work identity. Across the
full-recovery history, ell at fade is between 0.0380 and 0.3658 of its initial
value. R changes by about one percent. This deformation acts very differently
on a tensile skin and a compressed radial backing.

The least prepared passive coefficients covering the field tractions are

    U_skin = tau(x) R^2,       tau=max_s(U_E/R^2),
    U_back = K(x)/ell,         K=max_s(U_E ell).

These laws grant zero charge-carrier energy and a maximally stiff directional
backing. The skin stores little area work; the backing accumulates radial
compression work. Their 1024-cell total rises from 171.53 to 1,864.41. Their
fade required negative-null remainder is 6.27767. Traction coverage also
leaves excess pressure and tension, so this configuration is a material
capacity control with unresolved force balance.

The more favorable controls prescribe the balancing stresses exactly. Let
W_* = -average(p_*) Delta D denote the credited fluid's compression work.
The support's mechanical work is

    W_support = -W_mechanical,E - W_*.

Two inventories then bracket the required handling of that work. A retained
inventory has U_support=U_initial+prefix(W_support), with the smallest initial
value keeping it above the material energy floor throughout the interval.
A controlled inventory follows that floor and exchanges
Delta U_support-W_support through an additional work port. These histories
grant arbitrary constitutive adjustment consistent with the specified
stress and energy accounting.

At full recovery and 1024 cells:

| Family | Retained: initial material energy | Retained: fade material energy | Controlled: fade material energy | Controlled: joint work export |
| --- | ---: | ---: | ---: | ---: |
| General anisotropic floor | 96.57 | 194.98 | 8.88 | 151.45 |
| Directional backing and skins | 165.87 | 264.29 | 16.88 | 217.60 |
| Stiff-fluid backing and skins | 235.60 | 334.01 | 24.89 | 283.91 |
| Radiation-fluid backing and skins | 375.57 | 473.98 | 40.89 | 416.70 |

The retained fade source remainders are respectively 0.51732, 0.65312,
0.78931, and 1.06208. The controlled instantaneous values are 0.20377,
0.21633, 0.22889, and 0.25400 before transport of the added work. The preceding
zero-added-material interface gives 0.20375. The older 0.262788 formal-store
value is an assembly comparison, with no universal feasibility status.

## Mechanical connection accounting

For the electric cells, the signed deformation work is -105.18847, with
111.90093 delivered and 6.71246 absorbed across individual label intervals.
The existing fluid has 7.96944 of positive compression work and -1.12778
of expansion work. Granting instantaneous local reuse of opposite work leaves
103.99898 of electric/fluid mechanical export and 5.65217 of input across
the interval. This credit preserves the fluid's prescribed energy history;
it specifies the ideal coupling that would transfer the work.

The paired radial guide also changes energy under the prescribed deformation:
its constant G gives U_G=G ell/R^2 and Delta U_G=G Delta(ell/R^2).
For this history the signed change is -523.69715. This is a deformation term
on the time-dependent metric. A source-free radial guide can have zero local
four-divergence while its energy changes this way. Consequently the guide
figure is a geometry/support accounting diagnostic, and a physical port duty
requires the actual guide-end and support boundary conditions. Assigning
all of it to electrical return or receiver heat would add an unsupported
assumption.

The physical distinction is therefore between a closed cell, whose internal
backing takes the opposite field work, and an attached cell, whose residual
tractions enter the wider support equations. The second case requires the
standing support's reciprocal forces, work, and constitutive response.

## Evidence and continuation

Producer:
`toolkit/adm_harness_cli/scripts/evaluate_composite_capacitor.py`.
Material/work controls:
`toolkit/adm_harness_cli/adm_harness/composite_capacitor.py`.
Evidence: [`data/composite_capacitor`](data/composite_capacitor).
Four independent cases use 512/1024 cells and 90%/100% recovery. Eight new
unit tests cover charged-skin thermodynamics, chemical work, preparation,
boosted stress cancellation, pressure credit, and retained/controlled energy
identities; the eight preceding charged-capacitor tests also pass.

The next bounded calculation sends partial and full unloading through the
existing delivery route and checks the remaining material-frame holding
force. Charge confinement, finite skin thickness, carrier costs, material
stability, and contact losses remain explicit physical construction duties.
