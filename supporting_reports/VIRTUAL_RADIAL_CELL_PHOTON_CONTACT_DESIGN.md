# Passive photon contacts and material thermal storage

The two selected radial-cell histories fit a favorable passive photon-flux
budget. Their largest shared transmission requirements are approximately
4% and 24% of the existing channel capacity. A reciprocal three-line
junction supplies an explicit instantaneous scattering matrix for those
transmissions. Its direct hot-to-cold leakage fits the bank ratings in a
frozen-temperature projection. These results identify a concrete contact
framework and separate its physical flux capacity from the earlier chosen
turnover comparison of 10.

Material storage remains the stronger construction constraint. Replacing
the radiation-bank caloric law with constant heat capacities reduces the
required cold/hot capacity contrast to approximately 21 and 232 at the
archived channel normalization. However, the spare density budget permits
so little additional cold-bank rest mass that its absorbed heat would
require a specific-energy increase of roughly 3–9 times rest-mass energy.
A material construction therefore needs a counted redistribution of the
existing allocation, or a storage law and containment system that satisfy
this energetic requirement.

This calculation continues the
[passive exchange investigation](VIRTUAL_RADIAL_CELL_PASSIVE_PHOTON_CLOSURE.md).
It concerns the backing cells of the scheduled active rail, with a moving
protected packet and distinct capacitor, endpoint delivery, pressure-link,
and standing-support duties. The calculation uses the selected first
location at `x=-2` and the refined second location at `x=-1.975`.

## Contact integration

The actual-fluid heat partition takes positive and negative parts of a
smooth net heat rate. Its sign changes introduce integration kinks. The
new optional adaptive contact integrator bisects common intervals for all
energy components, compares Gauss orders four and eight, and checks
one-sided endpoint signs. It sums absolute leaf estimates per original
panel, with internal target `1e-11` and maximum depth 20. Unresolved
panels remain explicit failures. The existing overall integrity tolerance
stays `1e-9`.

| Second-location replay | Factor 2 | Factor 4 |
|---|---:|---:|
| Previous Gauss 4/8 panel difference | `1.39737e-9` | `9.76284e-10` |
| Adaptive Gauss 4/8 panel difference | `3.43158e-13` | `1.04829e-13` |
| Summed absolute panel estimate | `9.50692e-12` | `7.97553e-12` |
| Additional interval bisections | 20 | 39 |
| Unresolved panels | 0 | 0 |
| Minimum full density margin | `0.000190115` | `0.000159306` |
| Full sampled and integrity gates | Pass | Pass |

The [adaptive replay archive](data/virtual_cell_bank_fluid_donor_guide08_second_n8_guarded_replay_adaptive_contacts/summary.json)
preserves the parent and applied controls exactly. The full density
margins remain unchanged; the radiation inventory changes by at most
`3.55e-15` relative to the preceding integration. Bank directions,
ratings, and counted donor comparisons pass, with zero additional
prepared inventory. The separate 0.5% reserve is partly consumed.
These are sampled checks with numerical error estimates; continuous
spatial acceptance and a complete constitutive evolution retain their
own requirements.

## A passive circuit basis

The circuit treatment of photonic heat transport expresses heat flow as

\[
Q=\int_0^\infty\frac{d\omega}{2\pi}\,
\hbar\omega\,\tau(\omega)
[n(\omega,T_h)-n(\omega,T_c)],\qquad 0\leq\tau\leq1.
\]

For real resistive terminals connected through a reactive network,
impedance matching controls transmission. A fully transmitted mode gives
`Q=pi k_B^2 (T_h^2-T_c^2)/(12 hbar)`. These relations supply the
passive flux normalization used here.
[Pascal, Courtois and Hekking, *Circuit approach to photonic heat transport*](https://arxiv.org/pdf/1003.3217).

Three-terminal superconducting circuits provide a laboratory example of
separate thermal reservoirs joined through a tunable electromagnetic
coupler. The experiment supplies a useful component arrangement for
coupled heat ports. Its cryogenic device parameters require a separate
translation to the rail's temperatures, stress budget, and mode structure.
[Gubaydullin et al., *Photonic heat transport in three terminal superconducting circuit*](https://www.nature.com/articles/s41467-022-29078-x).

## Available channel flux

Write `c_gamma` for the existing counterstream photon energy density and
`j_gamma` for its current, in units with the speed of light equal to one.
Each equilibrium direction carries flux `c_eq/2`. With symmetric thermal
access at both ends of a physical cell of proper length `l_cell`, the
effective grey contact coefficient satisfies

\[
\kappa_j=\tau_j/l_{\rm cell},\qquad
l_{\rm cell}(\kappa_h+\kappa_c)\leq1.
\]

The hot and cold ports share the original channels. The local proper
length is `ell` times the physical half-cell coordinate width `0.00025`;
refined numerical grid spacing supplies no additional physical flux.
The comparison assumes favorable access at both ends and a local cell
description. A curved-space propagation solution would determine its
spatial corrections and transit response.

For each archived panel, divide its hot and cold photon branch heats by
the proper duration and sampled `D(c_eq,h-c_gamma)` or
`D(c_gamma-c_eq,c)`. This gives the effective coefficients required at
the five registered sample locations: midpoint, endpoints, and quarter
points. The calculation compares panel-average powers with those local
temperature gaps; a time-dependent material contact must reproduce the
underlying heat history.

| Passive comparison | First location | Second location |
|---|---:|---:|
| Maximum shared transmission requirement | `0.03958` | `0.23605` |
| Maximum grey contact recoil contribution | `8.38e-5` | `1.77e-4` |
| Maximum directional fraction `abs(j_gamma)/c_gamma` | `0.4062` | `0.4208` |
| Shared passive flux budget | Pass | Pass |

The [verified contact archive](data/virtual_cell_photon_passive_port_capacity_verified/summary.json)
uses the first-location factor-eight temperature audit and the refreshed
second-location factor-four audit after adaptive integration. The
[initial comparison](data/virtual_cell_photon_passive_port_capacity/summary.json)
retains the preceding integration for provenance. Both comparisons give
the values above at the displayed precision.

The recoil follows from absorption of the directional current and
isotropic emission in the material frame:
`f_material=(kappa_h+kappa_c) j_gamma`. It identifies the absorption
and emission contribution. The explicit boundary junction below also
reflects photons, with cell-line reflection probability
`1-tau_h-tau_c`; reflection and termination forces add mechanical
loads even at zero bank heat transfer. Their mechanical paths,
associated work, and influence on the material evolution remain to be
included in a coupled construction.
The largest directional fraction also shows why a balanced-population
approximation would require a local check.

## An instantaneous reciprocal junction

Three real-impedance lines with normalized admittances
`p_0+p_h+p_c=1` have the real symmetric scattering matrix

\[
S=2vv^{\mathsf T}-I,\qquad
v=(\sqrt{p_0},\sqrt{p_h},\sqrt{p_c})^{\mathsf T}.
\]

It is unitary and has transmission `tau_ij=4 p_i p_j`. Given the
cell-to-bank transmissions `tau_h,tau_c`, choose

\[
p_0=\frac{1+\sqrt{1-\tau_h-\tau_c}}{2},\qquad
p_h=\frac{\tau_h}{4p_0},\qquad
p_c=\frac{\tau_c}{4p_0}.
\]

The larger root minimizes direct bank-to-bank transmission within this
junction family:

\[
\tau_{hc}=\frac{\tau_h\tau_c}{4p_0^2}.
\]

Both archived histories admit this matrix at every evaluated sample;
the maximum unitarity residual is `8.88e-16`. The additional direct
hot-to-cold heat is evaluated using the same thermal populations and
the same two-ended flux convention.

| Frozen-junction comparison | First location | Second location |
|---|---:|---:|
| Maximum direct bank transmission | `1.98e-9` | `3.74e-9` |
| Largest cumulative bypass over the five sample estimates | `7.17e-7` | `1.66e-6` |
| Midpoint cumulative bypass maximum | `6.86e-7` | `8.24e-7` |
| Original minimum separate-rating margin | `0.00041071` | `0.00073844` |
| Projected minimum separate-rating margin | `0.00041015` | `0.00073780` |

The projection transfers accumulated bypass from `H` to `C`, preserving
their sum to roundoff and keeping both individual rating requirements
within their shared capacity. It holds the fitted temperatures and
couplings fixed. Updating `H,C` changes those temperatures and requires
a new joint evolution. The matrix establishes an instantaneous passive
junction; a physical network still needs its spectrum, tunability,
switching work, bandwidth, work-channel isolation, and material inventory.

## Storage calorics and additional rest mass

The earlier common radiation-bank caloric law gives volume-contrast
infima of `8.36587e6` and `6.58211e7`. To test their dependence on that
law, consider constant heat-capacity banks `E_j=B_j Theta_j` and define
`b_j=1/B_j`. Temperature ordering at every active contact gives

\[
b_h>\max(L_f,L_g/\sqrt{a_2}),\qquad
b_c<1/\max(B_f,B_g\sqrt{a_2}),
\]

where the bounds use the active-sample extrema
`L_f=max(Theta_f/H)`, `B_f=max(C/Theta_f)`,
`L_g=max(R sqrt(c_gamma)/H)`, and
`B_g=max(C/(R sqrt(c_gamma)))`.
Consequently the capacity-ratio infimum at fixed `a_2` is

\[
\inf\frac{B_c}{B_h}
=\max(L_f,L_g/\sqrt{a_2})\max(B_f,B_g\sqrt{a_2}).
\]

Allowing the modal normalization `a_2` to change reduces that infimum to
`max(L_f B_f,L_g B_g)`. This latter comparison changes a physical
normalization of the photon channels.

| Constant-capacity comparison | First location | Second location |
|---|---:|---:|
| Capacity-ratio infimum, archived `a_2` | `20.8384` | `232.2381` |
| Capacity-ratio infimum, adjustable `a_2` | `20.8384` | `44.9184` |
| Spare added rest inventory per material label | `0.01133–0.01438` | `0.01544–0.03527` |
| Cold heat absorbed per label | `0.09775–0.11440` | `0.08912–0.10876` |
| Required specific-energy increment divided by `c_light^2` | `7.136–9.348` | `3.084–6.256` |

The [verified material-bank archive](data/virtual_cell_material_bank_fixed_history_verified/summary.json)
uses the same refreshed temperature inputs. The
[initial material comparison](data/virtual_cell_material_bank_fixed_history/summary.json)
preserves the preceding input version.

Capacity contrasts become volume contrasts only after a volumetric heat
capacity is specified. Furthermore, these are ordering infima; finite
heat transfer requires strict temperature gaps and corresponding
coefficient margins.

The final three rows charge additional cold-bank material to the spare
full density budget while retaining the existing heat and containment.
For a conserved rest inventory `M` per material label, dust adds `M/D`
to density. Thus

\[
M_{\rm spare}(x)=\min_t[D(t,x)\,\Delta\rho_{\rm spare}(t,x)],\qquad
\Delta\epsilon_c\geq\frac{\Delta C}{M_{\rm spare}},\qquad
\epsilon_c=u_{\rm specific}/c_{\rm light}^2.
\]

This favorable additive comparison gives the entire remaining allowance
to cold-bank material. Hot-bank rest mass, its preparation, additional
containment, and pressure stresses add further requirements. Ordinary
thermal matter with specific-energy changes small compared with
`c_light^2` therefore exceeds this allocation's added mass allowance.
For any proposed material, the direct comparison is
`M_physical >= Q_absorbed/[u(T_max)-u(T_initial)]`, using its caloric law
and allowed operating interval.

As a conditional comparison, the registered law `E=3 M Theta` requires
added cold rest inventory exceeding the corresponding spare allowance
by factors `10.65–24.48` at the first location and `1.88–22.21` at the
second, at archived `a_2`. At the second location, the fluid-cold contact
alone requires cold material inventory as large as `0.34295`, comparable
with the `0.4` already assigned to the pressure-link fluid. Reusing that
existing inventory would require a conserved allocation that continues
to supply its pressure, heat, and momentum duties.

Absolute packing also depends on the rail length scale, the temperature
normalization, and the material density. The present specific-energy
comparison survives a change of the overall length scale because both
absorbed heat and spare rest inventory scale together. It supplies a
target for a material model while keeping the original component duties
explicit.

## Checkpoint

The final bounded calculation supports a passive electromagnetic contact
basis and resolves the contact-quadrature issue at the two tested
refinement levels. It leaves a concrete coupled requirement: thermal
storage, its counted material mass, photon momentum reaction, and the
network response must share a consistent evolution. The constant-capacity
comparison makes a general material search premature; an ordinary thermal
store would first need a justified reassignment of existing inventory.
Work pauses at this checkpoint.

## Verification and execution records

The focused transport, thermal, solver, capacity, and support suite passes
217 tests. Adaptive-contact regressions cover sign-change kinks,
Gauss-node blind spots, cancellation, and unresolved-depth failures.
Passive-port tests cover shared capacity, closed temperature gaps,
directional populations, reciprocal unitarity, direct bypass, and the
unit-transmission boundary. Material-bank tests cover the caloric
ordering and added-rest-inventory bounds. The final port guard uses the
same unit-transmission limit as the junction and requires both to pass.

All numerical jobs retain input and output SHA-256 records. The completed
provenance check covers 79 manifests and 6,507 references, with zero
errors, five matched execution snapshots, and 52 matched historical
source versions. Commit `41a074a` preserves the initial execution sources;
the verified contact rerun includes the consistent boundary guard and
explicit reflection-force scope. Independent cases used two workers per
diagnostic. Narrative analysis is recorded in this manually authored
report.
