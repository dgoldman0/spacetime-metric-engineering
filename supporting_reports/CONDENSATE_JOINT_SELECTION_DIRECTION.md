# Joint selection of the condensate interior and exterior

Date: 9 September 2026.

The accumulated source trials support a joint boundary-value search within the Ishihara–Ogawa scalar–Higgs–gauge model. The preferred starting construction has a smooth enclosing material layer, an interior field state selected for regularity, and the quantum contribution required by the rail's negative null stresses. The existing condensate neighborhood supplies a local continuation direction. The model's potential-dominated interior supplies a complementary regular starting state. Together these give a more specific construction problem than an additional survey of material families.

## Constraints supplied by the earlier trials

| Retained finding | Consequence for joint selection |
| --- | --- |
| The reset's initially empty material sector supplies angular stress too late in the prescribed startup expansion. | Include the material state and its stress response in the initial data. |
| Independently evolving Comer currents and a responding geometry avoid the earlier forced gravitational kinetic cancellation. | Determine subsequent geometry from source dynamics, with the rail's matching and service conditions imposed as constraints. |
| The retained initial annulus requires negative radial enthalpy throughout and negative angular enthalpy over part of its extent. | Retain both null channels in the quantum-plus-material tensor comparison. |
| Ordinary preload adds positive null stress; local complete Casimir cells have a positive counted energy cost. | Account spatially for material energy and quantum stress, including the positive material contribution inside any candidate layer. |
| An enclosing spherical quantum boundary gives the useful radial and angular response signs at the registered witnesses. | Preserve the enclosing geometry as the optical starting arrangement and compute its response from the selected smooth material profile. |
| The atmosphere achieves static force balance but its local deformation response remains unfavorable. | Require the coupled angular response as well as equilibrium pressure balance. |
| The screened condensate achieves an exterior mass and radial-pressure match, then develops inward scalar growth. | Select the interior and exterior field values and normal derivatives in one boundary-value problem. |

These findings come from different controlled constructions. Their common role is to constrain the next source model. The calculated ideal-sheet quantum tensor and the atmosphere's local deformation kernel each retain their original material assumptions; the condensate requires its own optical response and coupled perturbations.

## The local condensate direction

The [retained nine-point neighborhood](data/condensate_rail/boundary_neighborhood.csv) fixes the couplings, material scale, geometric join, inner radial pressure, and zero inner electric derivative. At each of the three Higgs amplitudes, increasing the matter amplitude lowers the ADM mass and moves the amplitude-100 event inward. At each matter amplitude, reducing the Higgs amplitude produces the same two changes.

| Boundary amplitudes \((u_R,h_R)\) | ADM mass, rail units | Radius at amplitude 100 |
| --- | ---: | ---: |
| (0.9, 0.07) | 2.474068 | 4.409758 |
| (1.0, 0.05), selected exterior | 2.390302 | 4.296173 |
| (1.1, 0.03) | 2.316392 | 4.145892 |

The final row lowers the selected exterior mass by 3.09% and moves the event inward by 0.15028 rail units. All nine exteriors still reach the event before the core. The monotone trends therefore identify useful starting directions for continuation; acceptance requires a regular profile over the full specified interior and its asymptotic completion.

The relative phase condition also needs independent attention. The stationary combination \(\omega-ea_R\) increases from 0.130848 at the selected point to 0.135954 at the final row. Thus the favorable event-radius trend by itself does not approach the phase-locked interior described below. A joint solve must determine the frequency and gauge profile together with the scalar amplitudes.

## A regular inner state in the same action

The Ishihara–Ogawa potential-ball branch has a nearly constant inner region with small Higgs amplitude. Its limiting fields are

\[
h=0,\qquad ea=\omega,\qquad u=u_0,\qquad
u'=h'=a'=0.
\]

These constant fields solve the classical matter equations on a static metric: the matter phase is canceled by the gauge potential, the Higgs amplitude vanishes, and the covariant scalar gradients vanish. Their stress is

\[
\rho=V=\lambda/4,\qquad p_r=p_t=-V,\qquad
\rho+p_r=\rho+p_t=0
\]

in Higgs-vacuum units. The gravitational solutions in [Ogawa and Ishihara (2024), equations (33)–(36)](https://arxiv.org/html/2409.07818v3#S3.SS2) connect a nearly constant potential interior to an outer vacuum through a finite material layer. Those solutions have a de Sitter interior. For the rail, the potential-dominated fields provide an interior starting profile while the retained geometry and its required quantum stress remain separate constraints.

A finite connection to the outer Higgs vacuum requires small departures from this limiting state. Exact zero Higgs amplitude and exact zero derivative at a finite cut would keep that field identically zero under the smooth classical equations. A global solve must select the small departures and their gradients.

The alternative hollow branch of the same action has a vacuum interior and concentrated shell energy; it is a useful comparison for the cost of filling the interior with positive potential energy. The [published flat families](https://arxiv.org/html/2103.13732v1) distinguish that volume cost from the shell contribution. The quantum budget must count the potential-dominated interior's positive energy even though its null enthalpies vanish. The rail's negative enthalpies still require their quantum source.

## The loading condition that the previous grid held fixed

At the selected join, the electric gradient is zero and the complete tensor obeys

\[
p_r=K+D-V,\qquad \rho+p_r=2(K+D),
\]

where \(K\) is the gauge-covariant temporal kinetic energy and \(D\) the positive scalar gradient energy. The retained values are

\[
V_R=0.25225156,\qquad p_{r,R}=-0.125,\qquad
K_R+D_R=0.12725156.
\]

Hence the previous boundary conditions force substantial kinetic and gradient energy at the join. Throughout the nine-point grid, \(V_R\) remains near 0.25 and \(K_R+D_R\) remains near 0.125. Changing only the two amplitudes within that grid preserves this restriction. A potential-dominated join would instead satisfy \(p_{r,R}\simeq-V_R\), with a smaller kinetic and gradient contribution.

The physical radial load remains fixed by the matched geometry. The adjustable quantities are the material scale and the location of the join within the resolved profile, together with the frequency and global field data. For illustration, a potential-dominated join with \(\lambda=1\) obeys

\[
\eta v^4\frac{\lambda}{4}
\simeq 5.6991156\times10^{-5}
\]

for the retained geometric pressure. At the previous \(v=20/6.8\), this would give approximately half the previous \(g=\eta v^2\). This relation identifies a pressure-to-potential matching direction; a candidate must also satisfy its complete field equations and quantum normalization. The same \(\eta\) applies to material and quantum stresses.

## Bounded joint construction

The next calculation can retain the existing action and couplings while treating the frequency, material scale, and boundary field data as coupled unknowns. The numerical starting profiles are the loaded exterior and the potential-dominated inner branch, with the hollow branch as a comparison. Continuation should first seek a regular common profile whose field values and normal derivatives agree across the join. Conserved matter number can fix the branch while the frequency is solved, as in the successful flat reference refinement.

The rail contains a finite-radius throat. Interior completion therefore means regular continuation through that geometry and specified far-end field conditions. The origin conditions of a spherical star require a different topology. Likewise, the radius-6.8 surface is an interior cut through the proposed material: its electric derivative should follow from the global solution and Gauss's law. Zero total asymptotic charge can be enforced without independently prescribing zero electric flux at every internal cut.

The residuals should include scalar and gauge continuity, mass and lapse-gradient matching, and the prescribed asymptotic states. A profile that only postpones the runaway retains a finite regularity residual. Following a converged branch then permits assessment of its counted energy, both null-stress requirements, and the optical response of its actual smooth layer. The complete angular perturbations and time-dependent rail conditions provide the subsequent construction tests.

This direction uses the earlier trials to select the geometry, material organization, and matching conditions together. It supplies a concrete search within the current model, while the existence of a regular, stable source meeting the full rail tensor remains open.

The [joint-continuation calculation](CONDENSATE_JOINT_CONTINUATION.md) realizes the stationary material-regularity part of this search, with two resolved branches on the retained asymmetric geometry. Its measured quantum remainder and stability requirements define the remaining source tests.

## Evidence links

- [Reset startup and source-order obstruction](LE_RESET_INVERSE_SEARCH.md)
- [Comer current evolution and initial junction](COMER_TWO_CURRENT_EVOLUTION_ROUND.md)
- [Vacuum stress and local material realization](VACUUM_SUPPORT_SELECTION_ROUNDS.md)
- [Counted support energy and radial/angular requirements](RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md)
- [Enclosing curved quantum-boundary response](CURVED_QUANTUM_BOUNDARY_SEARCH.md)
- [Atmosphere equilibrium and deformation audit](GRAVITATING_SCREENING_ATMOSPHERE.md)
- [Condensate field equations, refinements, and interior obstruction](SCREENED_SCALAR_CONDENSATE.md)

The numerical comparisons above are direct evaluations of the existing retained profiles and neighborhood table. This synthesis introduces no new field solve.
