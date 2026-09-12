# Joint elastic backing, pressure link, and rail support

The joint elastic screen places the capacitor's electrode loads, a prepared
radial frame, angular rings, the pressure fluid, and a warm backing store in
one force-and-energy calculation. A finite elastic continuation exists, but
its optimized trajectories require large prepared inventories, substantial
end reactions, and heat exchange incompatible with the tested passive contact
law. This particular prepared frame supplies a poor completion of the
capacitor's rail connection.

The failure directs the next comparison toward the support's constitutive
response. An independently scheduled radial and angular stress envelope can
separate restrictions imposed by this elastic law from restrictions imposed
by joint conservation. The standing support and its actuator retain their
separate construction roles in that comparison.

## Operating patch and component accounting

The calculation uses the scheduled active-rail patch x in [-2.1,-0.5],
s in [0,1.285], with the carrying-flow shift and metric time derivatives.
The protected packet, |x-s|<0.35, remains outside this patch. The physical
length scale remains free. Energies, stresses, and forces below use the
existing dimensionless source normalization.

The inputs are the retained-coefficient pressure-fluid/electric history and
the full-recovery work interface. The paired radial guide, propagating work
waves, and existing heat receiver retain their preceding trajectories. The
new material's stresses, energy, and end reactions are added explicitly. The
original endpoint tensor supplies the exchange target; each constructed
component replaces part of that target.

Write ell=Gamma B, D=ell R^2, N=alpha/Gamma, and v=B beta/alpha. The pressure
fluid has conserved number per label N_m, density n+3p, and thermal energy
U=3Dp. Its original trajectory is U_0. The surviving electric store has
H_e=H-S, u_E=H_e/R^4, charge q=sqrt(2H_e), and inverse capacitance ell/R^2.
Its radial and angular stresses are -u_E and +u_E. The additional constant
guide flux is G; the combined radial-field density is (H+G-S)/R^4.

For the right-side delivery route, the material-frame force still required
from the replacement support is

    F_* = Gamma(F_endpoint-v P_endpoint)
          - [max(J,0)/eta + eta max(-J,0)]
          - rho_receiver a - S_x/(ell R^4),
    J = H_s/(N R^4),       eta = 0.98.

The receiver includes the pressure medium's original heat exchange and the
converter losses. The converter identity makes the work-wave and receiver
power equal to the original endpoint power. Thus the added backing and the
change in pressure fluid exchange energy locally, with zero additional net
power port in this registered screen. A different electrical return schedule
would define an additional joint construction.

## Prepared elastic response

The cold frame has five nonnegative coefficients fixed in material labels:

    U_cold = A(x) ell + B_c(x)/ell + C(x) R + D_c(x)/R + T(x) R^2.

The first pair describes radial tension and compression. The next pair
describes equally populated circumferential members, and the last term
describes a tensile skin. The material stresses follow the energy variation:

| Contribution | Radial pressure / density | Angular pressure / density |
| --- | ---: | ---: |
| A ell | -1 | 0 |
| B_c/ell | +1 | 0 |
| C R | 0 | -1/2 |
| D_c/R | 0 | +1/2 |
| T R^2 | 0 | -1 |

The radial pair has the one-dimensional causal rigid-rod form. Here rigidity
means a longitudinal characteristic speed equal to c. A pressure-free thermal
store attached to that member adds inertia and reduces this characteristic
speed. This is a constitutive comparison at relativistic stress levels.
[Natário, *Relativistic elasticity of rigid rods and strings*](https://arxiv.org/abs/1406.0634).

For the cold radial pair, the relaxed length is sqrt(B_c/A). To keep a finite
compression response throughout the prescribed deformation, the screen imposes

    B_c >= delta A max_s(ell^2),
    D_c >= delta C max_s(R^2).

The parameter delta compares finite prestretch choices. At the largest length,
the limiting radial ratio is p_r/rho=(-1+delta)/(1+delta). Delta=0 admits the
degenerate pure-tension limit; positive delta gives a finite relaxed length
where A is present. Full three-dimensional shear and buckling stability need
a corresponding solid constitutive law. The available relativistic framework
distinguishes longitudinal and transverse elastic parameters.
[Natário, *Rigid elastic solids in relativity*](https://arxiv.org/abs/1912.08221).

The warm store has nonnegative energy Z and zero averaged pressure. Its local
exchange with the pressure fluid obeys

    partial_s(U-U_0+Z) + (U-U_0) partial_s(ln D)/3 = 0.

Each cold contribution independently obeys

    partial_s U_cold = -D[p_r partial_s(ln ell)
                          + 2 p_t partial_s(ln R)].

Consequently the calculation counts strain work and retained energy together.
Stress obtained by varying stored energy also organizes the relativistic
hyperelastic action formulation.
[Brown, *Elasticity Theory in General Relativity*](https://arxiv.org/abs/2004.03641).

The radial force of any co-moving diagonal material is

    F = (rho+p_r)a + d_r(p_r) + 2(p_r-p_t) k,
    d_r = (v/N) partial_s + (1/ell) partial_x,
    k = d_r(ln R).

The new cold/warm force plus the change in fluid force must equal F_*.
This admits a distributed longitudinal stress gradient, which the earlier
locally balanced capacitor lacked.

## Joint results

The objective minimizes the peak null projection of the complete new
fluid/frame/warm tensor over the sampled history and all null directions.
The table reports the geometry replacement remainder at fade separately.
It includes the fixed electric field, guide, work waves, and heat receiver.

| Spatial cells / time stride | Delta | Solver result | Fade negative-null remainder | Initial cold energy |
| --- | ---: | --- | ---: | ---: |
| 32 / 8 | 0 | Feasible | 19.7130 | 54,389.2 |
| 32 / 8 | 0.000001 | Feasible | 19.8236 | 54,726.3 |
| 32 / 8 | 0.0001 | Feasible | 34.3318 | 55,799.4 |
| 32 / 8 | 0.001 | Infeasible | — | — |
| 32 / 8 | 0.01 | Infeasible | — | — |
| 32 / 8 | 0.1 | Infeasible | — | — |
| 64 / 4 | 0 | Feasible | 18.3563 | 49,455.7 |

The original history has 257 intervals. The 32/8 screen retains 35 time nodes,
including the three archived source phases. The 64/4 comparison refines space
and time together. Its fade value differs by 6.9%, so these values establish
the large cost of the sampled family without claiming a converged optimum.
The preceding zero-added-backing interface has a fade remainder of 0.203752.
These are assembly comparisons; they carry no universal engineering ceiling.

The successful delta=0.0001 case also begins with about 8,179.4 units of fluid
thermal energy and 526.1 units of warm backing energy. The original fluid's
thermal inventory on this grid is about 36.6. Thus finite prestretch alone
does little to resolve the cost. During release, the radial material length
falls to roughly 4–37% of its initial value while the angular radius changes
by about one percent. The inverse-length compression term increases its
stress while the required support load is changing.

The optimized heat histories fail a simple passive contact test at every
sampled material label. Let T_fluid=U/(3N_m) and
T_warm=Z/(3N_m c_Z), with a fixed positive local heat-capacity ratio c_Z.
Warm-to-fluid exchange requires c_Z <= Z/U; reverse exchange requires
c_Z >= Z/U. Across the computed cycles these intervals have empty
intersection. The algebraic energy balance permits a heat schedule that this
passive thermal law cannot realize. More general thermal laws or heat engines
would have their own material and work requirements.

Keeping the fluid exactly at U_0 is infeasible for both delta=0 and 0.01.
Requiring zero combined nonwave traction at both ends is also infeasible for
those two values. With exposed ends, the delta=0.0001 trajectory reaches
reaction magnitudes of about 1,195.2 and 137.2 at the left and right cuts.
The neighboring rail would have to supply the opposite tractions through
counted attachment material.

## Evidence and use in selection

The result identifies a restriction of the prepared energy law together with
the retained delivery route. It leaves independently regulated stress response
as a distinct possibility. An endpoint traction record specifies a required
connection; a complete attachment additionally supplies its stress tensor,
work exchange, and stability.

The subsequent [joint support stress schedule](JOINT_SUPPORT_STRESS_SCHEDULE.md)
tests that freedom with independently counted radial and angular members,
records the mechanical work at both ends, and audits the resulting continuum
interpolation.

The cold strain-energy identities and an independently manufactured
accelerated, expanding metric verify the frame equations. Static force
controls verify that a transmitted load appears at the ends and that setting
both reactions to zero rejects an unpaid net load. The thermal control checks
compatible and incompatible temperature orderings. Five focused tests pass.

The largest original-matrix equality residual among the successful elastic
cases is 4.43e-8. Force quadrature is split at every original field-allocation
knot, since sampling only the knots would miss the quintic allocation's
interior derivatives. All computations use four independent workers and
small state archives.

Producers: `adm_harness/joint_backing_link.py`,
`scripts/run_joint_backing_link.py`, and `scripts/refine_joint_backing_link.py`
under `toolkit/adm_harness_cli`. The numerical evidence and input/output hashes
are in [`data/joint_backing_link`](data/joint_backing_link) and
[`data/joint_backing_link_continuation`](data/joint_backing_link_continuation).
The preceding load-allocation result is in
[Composite capacitor and rail connections](COMPOSITE_CAPACITOR_AND_RAIL_CONNECTIONS.md).
