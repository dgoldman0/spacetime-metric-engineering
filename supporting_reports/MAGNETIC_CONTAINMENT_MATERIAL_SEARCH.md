# Material candidates for the existing magnetic jacket

Literature search and numerical screen: 16 September 2026.

The surveyed literature supplies theoretical materials with stresses on the
required energy scale, while the demonstrated materials fall far below it.
The closest leads are anisotropic relativistic elastic membranes and
current-carrying scalar-field walls. A complete candidate satisfying the
existing containment cycle, including stability, electromagnetic currents,
and thermal operation, remains unidentified. This search holds the geometry
and registered heat histories fixed.

The [geometry comparison](MAGNETIC_GEOMETRY_COMPARISON.md) sets the reference:
the common jacket has internal magnetic pressure \(0.1p\), annular pressure
\(1.1p\), and outer-to-inner radius ratio 1.01. Its straight-section screen
includes both boundaries, current-carrier energy, and the mechanical hoop
reaction needed to turn the sheet carriers. The relevant material quantity is

\[
k=\frac{\text{allowable principal stress}}{\text{total proper energy density}},
\]

with rest energy included. For ordinary solids, a useful first comparison is
\(k\simeq(\sigma/\rho_m)/c^2\); for a membrane, surface stress and surface
energy replace their volume counterparts. Elastic strain energy alone and
frequency-dependent effective mass describe different quantities.

The thresholds below belong to the assigned sleeve and inventory model.
For a composite sleeve, each constituent retains its own stress law and
the assembly satisfies the summed tensor and mechanical loads. The
[ensemble audit](CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md) now supplies passing
pointwise allocations from the existing ideal field, membrane and string
families, with shared hoop load and opposing constituent normal stresses.
It also derives a broader closed-load material bound under those allowances.

| Retained requirement | First location | Second location |
| --- | ---: | ---: |
| Minimum sampled common-jacket strength fraction | 0.80655 | 0.65421 |
| Strength fraction used for the saved explicit allocations | 0.85 | 0.85 |
| Axial pressure / sleeve energy in those allocations | −0.64743 to +0.82486 | −0.60143 to +0.70427 |
| Maximum individual-boundary hoop tension / sleeve energy | 0.83500 | 0.83517 |
| Favorable energy-only lower bound within the closed-jacket family | 0.03227 | 0.13320 |

Positive axial pressure denotes compression; negative pressure denotes
tension. These axial and hoop ratios describe particular saved witnesses,
with independently adjustable axial stress. A material
law must generate an admissible history from its own state variables. The
underlying local hoop stress is \(-H\); cylindrical averaging gives the
recorded transverse component \(-H/2\). Material strength applies to the
local value. Coarse-to-fine changes in the threshold are approximately 0.0010
and 0.0115, respectively; the decimal values describe the sampled histories.

The energy-only bound grants freely changing sleeve energy and zero extra
field and carrier cost. It therefore offers a favorable comparison even for
materials whose energy evolves differently from the fixed inventories in the
current construction.

The demonstrated structural candidates give the following scale. The
conversions use each publication's reported loading mode; a compressive
strength measurement supplies a preliminary comparison, with tensile and
cyclic qualification remaining separate requirements.

| Demonstrated candidate | Published strength input | Converted stress / rest-energy density |
| --- | --- | ---: |
| Intrinsic monolayer graphene | Sheet breaking strength 42 N/m; pristine areal mass approximately \(7.6\times10^{-7}\) kg/m² | \(6.15\times10^{-10}\) |
| Carbon plate nanolattice, 2020 | Specific compressive strength 3.75 MJ/kg | \(4.17\times10^{-11}\) |
| Optimized carbon nanolattice, 2025 | Specific strength 2.03 MJ/kg | \(2.26\times10^{-11}\) |
| Continuous carbon-fiber lattice, 2026 | Specific compressive strength 0.782 MJ/kg | \(8.70\times10^{-12}\) |

Graphene's breaking strength comes from the indentation measurements of
[Lee et al., 2008](https://doi.org/10.1126/science.1157996); the areal-mass
value is also used in the experimental analysis of
[Shin et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9883292/).
Using these favorable pristine-sheet values places the current requirement
roughly a billion times above that example. Even the favorable closed-jacket
bounds exceed it by approximately 52 million and 217 million.

The plate lattices approach constituent and topology limits under the
reported compression tests. Their paper also identifies imperfections and
thin-feature fabrication as performance constraints.
[Crook et al., 2020](https://www.nature.com/articles/s41467-020-15434-2).
The optimized 2025 lattices improve stress distribution and demonstrate
millimeter-scale fabrication; their published specific strength remains on
the same nonrelativistic energy scale.
[Serles et al., 2025](https://www.aph.kit.edu/wegener/english/21_1191.php).
The 2026 carbon-fiber result addresses scale and load transfer through
continuous fibers, while retaining the specific-strength gap above.
[Mesoscale carbon fiber lattices, 2026](https://www.nature.com/articles/s41467-026-72105-4).
Thus architecture improves the use of chemical bonding strength, with these
examples already eliminated by the energy budget before thermal and current
requirements are imposed.

Resonant metamaterials address a different possibility. Yang and colleagues
demonstrated a membrane whose effective dynamic mass becomes negative near
an acoustic resonance. That response follows from the motion of its membrane
and attached mass under oscillatory forcing.
[Yang et al., 2008](https://doi.org/10.1103/PhysRevLett.101.204301).
For the present gravitational source ledger, those constituents retain their
rest energy. The effective dynamic parameter supplies neither the required
static sleeve stress nor a reduction of the counted proper energy. Auxetic
response and frequency-selective negative stiffness likewise require a
complete constituent stress-energy calculation before affecting this screen.

Superconductors are relevant to the current-host function. The SPARC model
coil demonstrated a 20.1 T peak field with REBCO conductors and a structural
case accommodating stresses approaching 1 GPa, together with a cryogenic
cooling system.
[Hartwig et al., 2023 preprint; 2024 publication](https://arxiv.org/abs/2308.12301).
REBCO tape's ceramic layer also imposes curvature and strain constraints in
coil design.
[Huslage et al., 2024](https://arxiv.org/abs/2409.01925).
These are useful precedents for conductivity and current management. Their
structural case, conductor substrate, and cooling equipment would all enter
the rail energy inventory. The jacket calculation currently specifies
normalized carrier coefficients, \(m/|q|=2.54415\times10^{-8}\) and
\(1.20001\times10^{-8}\), without a particle species or a complete SI
conversion. Its physical field, temperature, dimensions, current density,
and penetration-depth requirements remain to be assigned together.

Dense-matter candidates improve absolute rigidity substantially. The nuclear
pasta simulations of Caplan, Schneider, and Horowitz give a shear modulus
around \(10^{30}\) erg/cm³ and breaking strains above 0.1, at a simulated
nucleon density of 0.05 fm⁻³. That density corresponds to approximately
\(7.5\times10^{34}\) erg/cm³ of nucleon rest energy, giving a modulus-to-rest-
energy ratio near \(1.3\times10^{-5}\). A failure stress requires the actual
strain-dependent response; the modulus itself is already far below the
required stress scale. The simulated phase also depends on dense-matter
confinement and composition.
[Caplan et al., 2018](https://arxiv.org/abs/1807.02557).

Crystalline color-superconducting quark matter has a theoretical shear
modulus of
\(2.47\,\mathrm{MeV/fm^3}(\Delta/10\,\mathrm{MeV})^2
(\mu/400\,\mathrm{MeV})^2\), with a quoted parameter-range estimate of
0.47–24 MeV/fm³. This describes the response of particular dense quark
phases; it supplies neither a measured breaking stress nor a complete
freestanding enclosure with its total energy and thermal history.
[Mannarelli, Rajagopal, and Sharma, 2007](https://arxiv.org/abs/hep-ph/0702021).
Both dense-matter routes retain a surrounding-equilibrium problem in
addition to material selection.

The relativistic field and elastic candidates deserve a more specific
comparison:

| Theoretical candidate | Relevant capability | Present assessment |
| --- | --- | --- |
| Charged scalar wall with trapped fermions | Surface tension and a population of charge carriers | Its isotropic surface response couples the two in-plane stresses; an anisotropic extension and full electromagnetic accounting are required. |
| Bosonic current-carrying domain wall | Anisotropic tension and an explicit condensate current | A useful field-theory starting point; current stability and a gauged finite enclosure remain open. |
| Domain wall coupled to Abelian gauge fields | Self-consistent scalar, current, and magnetic profiles | Directly relevant to a magnetic interface; published planar fields extend to infinity and complete stability is unresolved. |
| Stiff ultrarigid elastic solid, SUREOS | Explicit relativistic elasticity with large causal wave speeds | Its zero-normal-stress sleeve specialization fails the joint-stress screen below. |
| Relativistic rigid elastic membrane | Explicit anisotropic stress law reaching the required ratios algebraically | Closest constitutive lead; compressed-direction stability and the full operating history remain open. |

For the charged fermionic skin, the surface model already discussed in
[the composite capacitor report](COMPOSITE_CAPACITOR_AND_RAIL_CONNECTIONS.md)
has energy \(U=\tau+e_F\) and equal tangential pressures
\(P=-\tau+e_F/2\). Increasing the fermion population changes tension into
pressure in both directions together. The underlying charged-bubble study
also includes Coulomb energy, carrier emission, and charge-screening effects.
[Morris, 1998](https://arxiv.org/abs/hep-ph/9810420).
The present sleeve needs distinct hoop and axial responses, including
simultaneous hoop tension and axial compression, so the isotropic skin alone
fails that requirement.

Peter's current-carrying wall gives a more useful anisotropic model. In its
spacelike-current rest frame, one in-plane tension equals the surface energy
\(U\), while the other follows a current-dependent equation of state.
The calculation includes current quenching and a longitudinal stability
condition \(-dT/dU>0\). Its carrier symmetry is global and long-range
electromagnetic interactions are omitted. A magnetic sleeve therefore needs
a gauged extension, with its admissible stress signs and stable current range
evaluated on the actual history.
[Peter, 1995 preprint; 1996 publication](https://arxiv.org/abs/hep-ph/9503408).

A concrete gauged example is the two-scalar, two-Abelian-field wall of
Rozowsky, Volkas, and Wali. It supports sheet currents and magnetic fields
parallel to the wall, with field exclusion on the appropriate side. Its
nonzero asymptotic magnetic fields carry infinite total energy, and its
reported surface energy subtracts that background. The authors leave a
complete stability analysis open. A finite jacket would instead count both
field domains, return currents, and outer reactions. This is a useful local
interface model whose finite enclosure remains to be constructed.
[Rozowsky et al., 2003](https://arxiv.org/abs/hep-th/0305232).

A new numerical screen clarifies the joint stress requirement. Let
\((A,B,C)\) be the three residual-support facets before adding the sleeve,
\(u\) its energy density, \(z\) its axial pressure, and \(H\) the summed local
hoop-tension contribution of the two boundaries. After adding the averaged
sleeve tensor \((u,z,-H/2)\), admissibility requires

\[
A+u-z+H\leq0,\quad B+u-z-H/2\leq0,\quad C+u+2z-H/2\leq0.
\]

Consequently, \(z\geq u+G\), where
\(G=\max(A+H,B-H/2)\). A material class obeying
\(z+H\leq u\) requires \(G+H\leq0\). This class includes separate ideal
hoop strings and axial particle/wave pressure carriers: their respective
energy costs add. The inequality also survives adding pressureless mass.
Its violation is independent of the chosen sleeve energy, even when that
energy is allowed to vary freely at each sample.

| Fine history | Samples violating \(G+H\leq0\) | Labels affected | Maximum \(D(G+H)\) |
| --- | ---: | ---: | ---: |
| First location, 4,113 times × 32 labels | 12 | 12 | 0.0183654 |
| Second location, 2,057 times × 32 labels | 176 | 32 | 0.0320066 |

The maxima occur at \((t,x)=(0.5,-1.9998046875)\) and approximately
\((1.1519824219,-1.9748515625)\), in the registered coordinates. Both coarse
histories also fail, with maximum gaps 0.0182464 and 0.0319083. Independent
linear programs confirm infeasibility at each history's worst sample.
Since a tensile sleeve also needs \(u\geq H\), a positive \(G+H\) forces
\(z>0\): axial compression at these samples is required by the residual
budget, even with a different allocation. Coupled fields and elastic laws
that permit larger joint stresses remain outside this excluded class.

SUREOS provides a specific application. Its constitutive law is
\(u=A\sum_{i<j}n_i^2n_j^2+B\), with
\(u=\sum_i p_i+4B\) and \(u-p_i-2B>0\).
Setting normal stress to zero and the other pressures to \(z,-H\) gives
\(z+H<u\). Thus a sleeve with that plane-stress specialization fails the
screen above. A finite layer with additional normal stress would require a
different, explicitly counted tensor.
[Karlovini and Samuelsson, 2004](https://arxiv.org/abs/gr-qc/0401115).

The rigid membrane of Mourão, Natário, and Vicente has a broader algebraic
response. Writing their equation (84) in principal inverse stretches gives

\[
U=\frac{U_0}{2}[(1-\epsilon)(1+n_z^2n_\phi^2)
                  +\epsilon(n_z^2+n_\phi^2)],
\]

with \(p_i=n_i\partial U/\partial n_i-U\).
Our substitution \(\epsilon=0.8\), \(n_z^2=6\), \(n_\phi^2=1/6\)
gives \(p_z/U=+0.875\) and \(p_\phi/U=-0.875\). This clears the magnitude
comparison and the excluded mixture inequality at a single algebraic state.
The paper establishes luminal longitudinal sound speed in isotropic states.
An isolated
membrane with zero bending stiffness has a compressed-direction transverse
mode \(\omega^2=-p_z k_z^2/U<0\), from its normal-displacement equation.
Finite thickness, confinement, or coupled fields must supply the stabilizing
response; anisotropic wave speeds and coupled stability remain to be checked.
[Mourão et al., 2024 preprint; 2025 publication](https://arxiv.org/html/2409.10602v1#S3.SS1).

Self-contained energy stores remain another category. Supersymmetric Q-ball
models admit stable charged condensates in thermal environments, with
finite-volume evaporation conditions depending on temperature and charge.
[Laine and Shaposhnikov, 1998](https://arxiv.org/abs/hep-ph/9804237).
Using one would require a replacement receiver model with heat capacity,
heat exchange, pressure, and confinement evaluated on the accepted receipts.
Experimentally observed self-bound ultracold droplets provide a laboratory
example of collective binding and a critical particle number for survival.
[Schmitt et al., 2016](https://www.nature.com/articles/nature20126).
Their demonstrated role is binding an ultracold quantum fluid; a relativistic
stress-bearing heat enclosure remains a separate requirement.

The material-focused next step is therefore a constitutive and stability
test at the existing geometry. The rigid membrane supplies a concrete
mechanical law to test; a gauged scalar wall supplies a concrete current-host
mechanism. Each needs a single set of material parameters and a connected
evolution through the prescribed stretches, currents, and thermal contacts.
The resulting test must include bend equilibrium, energy transfers, field
penetration, and perturbations that change shape. The current scalar
strength allowance of 0.85 remains an allocation parameter until such a
construction succeeds. A 50% strength target has no independent material
justification from this survey.

The [numerical evidence](data/magnetic_material_screen/summary.json) records
the unit conversions, boundary stress ranges, rejection samples, independent
linear-program statuses, and input hashes. Four parallel jobs read the
existing coarse and fine archives; all twelve direct input hashes match the
geometry manifest, and the saved tensor allocations reconstruct within
\(2.78\times10^{-17}\). The
[audit script](../toolkit/adm_harness_cli/scripts/audit_magnetic_material_candidates.py)
emits numerical evidence. This report is manually authored. Literature
coverage includes primary experimental, computational, and field-theory
papers, with recent structural examples through April 2026; it establishes
the outcomes for the surveyed candidates and the specified constitutive
class.

Reproduction from the repository root, choosing a fresh output directory:

```bash
PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_magnetic_material_candidates.py \
  --workers 4 --output /tmp/rail_material_screen_reproduction
```
