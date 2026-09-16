# Literature comparison for storage and containment

Review date: 16 September 2026.

Published work supplies several close analogues to the rail's storage problem:
magnetic energy storage with limited structural mass, magnetically confined
relativistic radiation, and localized interacting fields with their own
confining stresses. These studies identify physical mechanisms worth testing.
The sources examined establish no complete thermal store satisfying the
current rail histories, their temperature ordering, and their remaining
material allowance simultaneously.

The comparison below distinguishes published results from their possible
application to the rail. It records a targeted literature search and introduces
no new numerical source solution.

The current [photon-contact comparison](VIRTUAL_RADIAL_CELL_PHOTON_CONTACT_DESIGN.md)
assigns the entire spare added rest inventory to the cold bank. Absorbing the
scheduled heat then requires specific-energy increments of
\(7.136\)–\(9.348\,c^2\) at the first location and
\(3.084\)–\(6.256\,c^2\) at the second. Existing heat and containment are already
counted. These ratios concern additional conserved material inventory at fixed
histories; they differ from the stored energy divided by the mass of the whole
assembly. A candidate can change this comparison by reallocating existing
components and solving their remaining duties together.

| Closely related problem | Published containment mechanism | Evidence and transfer requirement |
| --- | --- | --- |
| Superconducting magnetic energy storage | Shape the winding so centering and hoop forces balance more favorably. | Small superconducting prototypes support the force-balanced-coil concept. The rail would need its own complete current, field, material, and boundary-load solution. |
| Magnetar trapped fireballs | Closed magnetic fields confine an optically thick photon–electron–positron plasma. | An astrophysical model constrained by observed flare tails. Field energy, stellar anchoring, cooling, and pair dynamics belong to the system. |
| Self-bound scalar configurations | Conserved charge and scalar interactions produce a localized object with a resolved transition to vacuum. | Explicit classical field solutions exist in specified theories. A rail heat bank additionally needs a finite-temperature response and controlled exchange with the photon channels. |
| Self-gravitating radiation | Strong gravity confines the radiation through its contribution to the metric. | Mathematical photon-shell solutions exist at high compactness. A complete rail application would change the coupled geometry and require loading and stability calculations. |

**Magnetic storage and force balance.** Sato and collaborators fabricated a
small superconducting force-balanced coil and operated it close to its rated
current. Their winding uses opposing electromagnetic loads to reduce the
centering force and simplify support. This is an experimentally investigated
structural optimization.
[Sato et al., 1999, publisher abstract](https://onlinelibrary.wiley.com/doi/abs/10.1002/%28SICI%291520-6416%28199908%29128%3A3%3C82%3A%3AAID-EEJ10%3E3.0.CO%3B2-T).

The virial analysis in Ciceron, Badel, and Tixador relates magnetic storage
capacity to structural strength, density, and topology. The conductor also
has critical-current constraints depending on temperature, magnetic field,
and strain.
[Ciceron et al., 2017, sections 2.1–2.2](https://doi.org/10.1051/epjap/2017160452).

For the rail, the useful inference is to investigate whether existing field
and support components can share loads through an explicit geometry. Such a
construction must include its end reactions and response during the scheduled
cycle. The experiment supplies neither a thermal caloric law nor a measured
improvement for this rail. The earlier
[composite connection study](COMPOSITE_CAPACITOR_AND_RAIL_CONNECTIONS.md)
provides the appropriate starting accounting for shared components.

**Relativistic radiation in a magnetic trap.** Thompson and Duncan model
magnetar flare tails using a hot photon–pair plasma trapped on closed magnetic
field lines. Their confinement condition is
\(B^2/(8\pi)>P_\gamma+P_{e^\pm}\) in Gaussian units, or
\(B^2/(2\mu_0)>P_\gamma+P_{e^\pm}\) in SI. They also calculate neutrino losses
that become increasingly restrictive as the fireball is compressed and heated.
[Thompson and Duncan, 2001, sections 4.2 and 5.1](https://arxiv.org/abs/astro-ph/0110675).

This is a close analogue to storing heat with little baryonic inventory.
The transferable question is whether a counted field and its current carriers
can confine an interacting radiation reservoir while meeting the rail tensor.
The star's role in anchoring the field must have a specified counterpart.
Temperature normalization, pair opacity, and the thermal contact cycle must
be solved before using this as a candidate cold bank.

**A useful isolated-wall benchmark.** Bousso derives a thin-container energy
bound from pressure balance and the dominant energy condition. Specializing
his equations (6.4)–(6.9) to a static spherical radiation cavity in flat
spacetime gives

\[
p=\frac{E_\gamma}{3V},\qquad
\tau=\frac{pR}{2},\qquad
E_{\rm wall}\geq4\pi R^2\tau=\frac{E_\gamma}{2},
\quad V=\frac{4\pi R^3}{3}.
\]

Here \(\tau\) is membrane tension per unit length; the surface energy density
is at least \(\tau\). This specialization assumes isotropic radiation, a thin
wall, negligible gravity, and zero exterior pressure. The same paper discusses
interactions that form bound objects without a separate container.
[Bousso, 2003, sections 6–7](https://arxiv.org/abs/hep-th/0310148).

The rail's existing containment remains in its tensor accounting. Applying
this benchmark requires the complete candidate geometry and loads; adding
this wall cost again to already counted containment would double-count it.
An active connected assembly also has boundary momentum and time dependence
absent from this isolated benchmark.

**Self-bound fields and thermal response.** The Friedberg–Lee–Sirlin model
offers localized states of a complex scalar interacting with a real scalar
mediator. The mediator supplies binding, and the total energy contains both
fields' gradients and potential energy.
[Heeck and Sokhashvili, 2023, sections 2 and 5](https://link.springer.com/article/10.1140/epjc/s10052-023-11710-9).
Ishihara and Ogawa's related gauge–Higgs constructions include screened
homogeneous balls and shell configurations.
[Ishihara and Ogawa, 2019](https://arxiv.org/abs/1901.08799),
[2021](https://arxiv.org/abs/2103.13732).

This mechanism already overlaps the repository's condensate program.
The [joint continuation](CONDENSATE_JOINT_CONTINUATION.md) obtained regular
stationary material profiles after an earlier exterior attachment developed
inward scalar growth. Subsequent
[quantum-source work](CONDENSATE_SUPPLIED_QUANTUM_STRESS.md) identified separate
geometric and source-magnitude requirements. Those calculations studied rail
support; applying a condensate to the present heat bank requires an additional
thermal model.

Finite-temperature studies illustrate that additional requirement. Laine and
Shaposhnikov find volume-dependent evaporation temperatures for Q-balls in the
supersymmetric theories they examine.
[Laine and Shaposhnikov, 1998](https://arxiv.org/abs/hep-ph/9804237).
Their result is model-specific. It motivates computing the candidate's
energy, entropy, charge exchange, and stability over the required temperature
interval, alongside its mechanical containment.

**Gravity as the container.** Andréasson, Fajman, and Thaller prove existence
of static, spherical massless Einstein–Vlasov shells with
\(2Gm/(rc^2)\) close to \(8/9\). These are collisionless radiation solutions
with strong self-gravity.
[Andréasson et al., 2017](https://arxiv.org/abs/1511.01290).
In a different construction, Di Filippo and Rezzolla find that self-gravitating
photon light-rings around a black hole become unstable under photon addition
or removal.
[Di Filippo and Rezzolla, 2025](https://arxiv.org/abs/2407.13832).
That instability concerns their configurations; it supplies no general
stability verdict for every radiation shell.

Gravity therefore supplies a theoretical localization mechanism, with a
substantial change to the rail's geometry and operating problem. The source
and loading stability would need to be solved together.

The most direct next investigation suggested by this search is a bounded
comparison of magnetic containment with explicit shared supports, using the
existing heat and rest-inventory allocation. Its acceptance quantities are
the complete stress tensor, the absorbed heat and temperature interval,
channel momentum reactions, and the evolution through charging and release.
A condensate reservoir is a second direction if a specified finite-temperature
theory supplies those quantities. The literature supports both as research
questions while leaving their advantage over the present assembly to be
computed.

The subsequent [magnetic load-balancing test](MAGNETIC_LOAD_BALANCING_TEST.md)
evaluates a closed flux-tube cold reservoir on both accepted rail histories.
Its field and current accounting admits a conditional tensor allocation;
the selected straight sleeve requires stress-to-energy fractions of 0.7767
and 0.9746, with bend supports and the coupled material response still open.
