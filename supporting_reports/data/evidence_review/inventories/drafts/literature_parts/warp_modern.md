## Part B. Warp-drive design literature, 2020–2026

Same labels (a)–(g) as Part A; project identity numbers I1–I26 refer to `knobs_one_space.md` §3.

### SantosPereiraAbreuRibeiro2020_2026 — Osvaldo L. Santos-Pereira, Everton M. C. Abreu, Marcelo B. Ribeiro (series), matter-sourced Alcubierre solutions
- **Citation (each verified via its arXiv abstract page, 2026-09-26):**
  - "Dust content solutions for the Alcubierre warp drive spacetime", Eur. Phys. J. C 80, 786 (2020), arXiv:2008.06560v1 (14 Aug 2020; only version).
  - "Fluid dynamics in the warp drive spacetime geometry", Eur. Phys. J. C 81, 133 (2021), arXiv:2101.11467v2 (9 Feb 2021; v1 27 Jan 2021).
  - "Perfect fluid warp drive solutions with the cosmological constant", Eur. Phys. J. Plus 136, 902 (2021), arXiv:2108.10960v1 (24 Aug 2021; only version).
  - "Warp drive dynamic solutions considering different fluid sources", Proc. MG16 (World Scientific 2023) pp. 840–855, arXiv:2111.01298v1.
  - "Matching the Alcubierre and Minkowski spacetimes", Eur. Phys. J. C 86, 46 (2026), arXiv:2512.12541v1 (14 Dec 2025).
  - "Shift vector sign reversal in the Alcubierre warp drive spacetime geometry and nonlinear Burgers-type dynamics", Eur. Phys. J. Plus 141, 921 (2026), arXiv:2510.11836v3 (10 Aug 2026; v1 13 Oct 2025, v2 11 Jul 2026).
  - Santos-Pereira PhD thesis, arXiv:2508.20348v1 (28 Aug 2025), collects the series.
- **Design parts and knobs:** prescribed matter model (dust, perfect fluid, parametrized perfect fluid, anisotropic fluid, charged dust, Λ); dependence of the shift on (t, x) only versus (t, x, y, z); junction to Minkowski.
- **Knob → physics relations:**
  - Dust source: every solution reduces to vacuum, and the shift then obeys the inviscid Burgers equation (plane shock-wave-like profiles) [derivation].
  - The shift along the motion couples off-diagonal Einstein components, so any source needs momentum/off-diagonal terms [derivation, 2108.10960].
  - Darmois matching to Minkowski requires a shift independent of y and z (the Burgers gauge), and the geometry is then not globally flat [derivation, 2512.12541].
  - Positive matter density is claimed possible for some perfect-fluid and PPF subcases, "at the cost of a complex solution for the warp drive regulating function" [claim].
  - The vacuum reductions require β = β(t, x) and therefore lose the spherical bubble dependence (explicit caveat in 2510.11836v3) [statement].
- **Method / verification standard:** analytic reduction of the Einstein equations under ansätze; energy conditions for the fluid frame.
- **Scope and caveats:** one-dimensional shift profiles; the positive-density subcases use complex-valued regulating functions.
- **Disputes:** none in print directly; the positive-density claims fall under the SSV 2022 NEC theorem for localized flat-slice drives.
- **Relation to active-rail results:** independent confirmation of (a) and of I3: a shift that depends only on (t, x) has zero transverse gradient, hence zero Eulerian energy, and it is exactly flat when it obeys the Burgers equation (a coordinate change of Minkowski). Energy enters only through transverse dependence.
- **Key quote:** "We found out that all Einstein equations solutions of this geometry containing pressureless dust lead to vacuum solutions." (2008.06560 abstract v1)

### Lentz2021 — Erik W. Lentz (2021), "Breaking the Warp Barrier: Hyper-Fast Solitons in Einstein–Maxwell-Plasma Theory"
- **Citation:** Class. Quantum Grav. 38, 075015 (2021), DOI 10.1088/1361-6382/abe692 (Crossref). arXiv:2006.07125v2 (10 Aug 2020); v1 12 Jun 2020 (abstract read; v2 text searched). Companion: "Hyper-Fast Positive Energy Warp Drives", MG16 proceedings (2023, pp. 779–786), arXiv:2201.00652v1. Verified 2026-09-26.
- **Design parts and knobs:** unit lapse, flat slices, multi-component shift obeying a hyperbolic (wave-like) relation among components; rhomboidal source elements; conducting plasma plus EM field as matter.
- **Knob → physics relations:**
  - Hyperbolic shift relation claimed to give everywhere non-negative Eulerian energy and superluminal motion [claim].
  - Plasma plus Maxwell source claimed consistent with the soliton [claim]; DEC stated to hold only for shift magnitudes below 1, with horizons forming at higher speed [claim].
- **Method / verification standard:** analytic ansatz and numerical example; Eulerian energy and momentum conditions only.
- **Scope and caveats:** Eulerian observers only; trace-free stress part of the Einstein equations left unsolved (per SSV 2022 App. C).
- **Disputes:** refuted on several fronts: Santiago–Schuster–Visser 2022 (NEC violated generically; Einstein equations only partly solved), Warp Factory 2024 (Lentz-inspired metric violates WEC for boosted observers at the rhomboid boundaries), Celmaster & Rubin 2025 (negative Eulerian energy regions and derivation errors), Barzegar–Buchert–Vigneron 2026 (Errors 3, 16, 17), Bobrick & Martire 2021 ("Our conclusions do not support the recent claim"). No rebuttal by Lentz found.
- **Relation to active-rail results:** conflicts with (a)'s integral form: on flat unit-lapse slices ∫ρ d³x = −(1/32π)∫ω² d³x ≤ 0 (SSV 2022), so an everywhere non-negative Eulerian energy requires zero vorticity and a vanishing divergence term.
- **Key quote:** "This paper overcomes this barrier by constructing a class of soliton solutions that are capable of superluminal motion and sourced by purely positive energy densities." (abstract v2)

### BobrickMartire2021 — Alexey Bobrick, Gianni Martire (2021), "Introducing Physical Warp Drives"
- **Citation:** Class. Quantum Grav. 38, 105009 (2021), DOI 10.1088/1361-6382/abdf6e (Crossref). arXiv:2102.06824v2 (17 Feb 2021); v1 12 Feb 2021. Read v2. Verified 2026-09-26.
- **Design parts and knobs:** the drive as a shell of material around a passenger region; lapse ("rate of time") inside; spatial "capacity"; shell mass; flattening factor α_X along the motion; shape function; four classes by causal character of the comoving observers.
- **Knob → physics relations:**
  - Spherically symmetric drives: flat exterior ("truncation") forces ∫4πw r² dr = 0, so any non-trivial truncated drive contains negative energy; with positive energy the exterior is Schwarzschild [derivation, §3.1].
  - Positive-energy spherical drives can only slow interior time relative to a remote comoving observer; faster interior time requires negative energy; an Earth-mass 10 m shell slows time by 4×10⁻⁴ [derivation + estimate].
  - Spherically symmetric drives cannot hold objects larger than the drive as seen from outside [derivation].
  - Flattening by a factor 10 lowers the Alcubierre energy proportionally; α_X = 1 + v² makes the total energy velocity-independent (E → E/(1+v²)) [derivation].
  - Extreme flattening lets a superluminal drive meet the QI while still violating ANEC [argument citing Visser et al. 2000, Graham & Olum 2007].
  - Variationally optimal Alcubierre profile f̄ = min(r₀/r_s, 1) cuts energy by about 3 [derivation].
  - Any warp drive is an inertially moving shell and needs propulsion obeying 4-momentum conservation [claim/interpretation].
- **Method / verification standard:** analytic; Eulerian energy density and volume integrals.
- **Scope and caveats:** spherical results only for the positive-energy statements; Eulerian energy only.
- **Disputes:** SSV 2022 (App. A, D) call the continuity-equation and coordinate-transformation claims false and the spherical implementation "not useful"; Barzegar–Buchert–Vigneron 2026 list several errors (Errors 4, 10, 11, 14). Le 2026 (steering) builds on the propulsion point.
- **Relation to active-rail results:** the interior-clock result bears on I16/I26 and (d): a raised interior lapse (clock faster than the exterior) needs negative energy in spherical positive-mass shells, matching the project's finding that a raised packet lapse comes with a negative-energy transverse layer. The ANEC remark supports (g) directly. The truncation argument is the spherical analogue of I10 (zero integrated energy with a flat exterior).
- **Key quote:** "the only type of modification to the internal spacetime that is achievable with purely positive energy for spherically symmetric warp drives is slowing down the rate of time inside the craft." (§5.2)

### FellHeisenberg2021 — Shaun D. B. Fell, Lavinia Heisenberg (2021), "Positive Energy Warp Drive from Hidden Geometric Structures"
- **Citation:** Class. Quantum Grav. 38, 155020 (2021), DOI 10.1088/1361-6382/ac0e47. arXiv:2104.06488v4 (9 Aug 2021); v1 13 Apr, v2 22 Apr, v3 5 Jul 2021. Verified 2026-09-26.
- **Design parts and knobs:** Helmholtz-type decomposition of the shift; irrotational (gradient) part; the Eulerian energy as a geometric (cofactor/Hessian) quantity of the potential.
- **Knob → physics relations:** relation between vanishing shift vorticity and vanishing Eulerian momentum [derivation, per Le 2026b and SSV 2022]; example configurations with positive semi-definite Eulerian energy and total energy four orders below a solar mass [numerical claim].
- **Method:** analytic decomposition; modest numerics; Eulerian observers only.
- **Scope and caveats:** Eulerian energy only.
- **Disputes:** SSV 2022 (the "hidden geometric structure" is the cofactor of K; NEC still violated for all members of the class); Barzegar–Buchert–Vigneron 2026 Remark IV.27.
- **Relation to active-rail results:** the vorticity–momentum link is the literature root of (c) for flat unit-lapse slices; zero vorticity gives zero Eulerian flux and hence Type I.
- **Key quote:** "Using this newfound interpretation, a superluminal solitonic spacetime is presented that possesses positive semi-definite energy." (abstract v4)

### MattinglyEtAl2021 — Brandon Mattingly, Abinash Kar, Matthew Gorban, William Julius, Cooper Watson, MD Ali, Andrew Baas, Caleb Elmore, Jeff Lee, Bahram Shakerin, Eric Davis, Gerald Cleaver (2021), "Curvature Invariants for the Alcubierre and Natário Warp Drives"
- **Citation:** Universe 7, 21 (2021), DOI 10.3390/universe7020021. arXiv:2010.13693v3 (14 Apr 2021); v1 26 Oct 2020, v2 20 Jan 2021. Verified via abstract page 2026-09-26 (abstract read).
- **Design parts and knobs:** speed, skin depth (wall), radius; constant versus accelerating Natário drive.
- **Knob → physics relations:** parameter sweeps of curvature-invariant maps; a "safe harbor" interior; the wake seen for accelerating Natário drives is absent at constant speed [numerical, visualization].
- **Disputes:** Rodal 2023 (GRG) and Rodal 2024 (IJTP) report that these plots underrepresent the invariants by 8 to 16 and 21 orders of magnitude respectively.
- **Relation to active-rail results:** none visible.
- **Key quote:** "The warp drive parameters of velocity, skin depth and radius are varied individually and then plotted to see each parameter's unique effect on the surrounding curvature." (abstract v3)

### Rodal2023_2024 — José Rodal (2023; 2024), curvature invariants of Alcubierre and Natário
- **Citation:** "Visualization and analysis of the curvature invariants in the Alcubierre warp-drive spacetime", Gen. Relativ. Gravit. 55, 134 (2023), DOI 10.1007/s10714-023-03182-9, arXiv:2512.20738v1 (23 Dec 2025). "A Closer Look at Natário's Zero-Expansion Warp Drive", Int. J. Theor. Phys. 63, 168 (2024), DOI 10.1007/s10773-024-05700-0, arXiv:2512.19837v1 (22 Dec 2025). Both posted to arXiv after journal publication. Verified via abstract pages 2026-09-26 (abstracts read).
- **Design parts and knobs:** choice of flow (Alcubierre vs zero-expansion Natário) at matched ρ, σ, v.
- **Knob → physics relations:** the Alcubierre bubble needs four distinct layers of anisotropic stress [numerical]; Natário's spacetime is Petrov type I and its curvature-invariant amplitudes are 35 times Alcubierre's at identical parameters [derivation + numerical]; momentum density, rather than volume change, governs the drive's orientation [claim].
- **Disputes:** with Mattingly et al. 2021 (orders-of-magnitude plotting error).
- **Relation to active-rail results:** consistent with (a): removing expansion (Natário) leaves or increases shear, so it does not lower the energy cost.
- **Key quote:** "We demonstrate that Natário's spacetime exhibits curvature invariant amplitudes 35 times greater than Alcubierre's, given identical warp-bubble parameters." (2512.19837 abstract v1)

### SSVTractor2021 — Jessica Santiago, Sebastian Schuster, Matt Visser (2021), "Tractor beams, pressor beams, and stressor beams in general relativity"
- **Citation:** Universe 7, 271 (2021), DOI 10.3390/universe7080271 (Crossref). arXiv:2106.05002v1 (9 Jun 2021; only version). Verified 2026-09-26.
- **Design parts and knobs:** Natário-type flow fields shaped to attract, repel or stress a target.
- **Knob → physics relations:** tractor, pressor and stressor beams are all attainable within the warp ansatz and all violate energy conditions [derivation].
- **Method:** analytic, reverse engineering.
- **Relation to active-rail results:** shows the flat-slice identity (a) constrains any flow-field device, not only transport.
- **Key quote:** "We show that all of these metrics would violate various energy conditions." (abstract v1)

### SSV2022 — Jessica Santiago, Sebastian Schuster, Matt Visser (2022), "Generic warp drives violate the null energy condition"
- **Citation:** Phys. Rev. D 105, 064038 (2022), DOI 10.1103/PhysRevD.105.064038. arXiv:2105.03079v2 (25 Feb 2022); v1 7 May 2021. Read v2. Verified 2026-09-26.
- **Design parts and knobs:** generic Natário flow v on flat slices with unit lapse; its divergence, shear and vorticity; fall-off at infinity; smoothness (C²⁻, thin shells allowed).
- **Knob → physics relations:**
  - ρ = (1/16π)[(v_{i,i})² − v_{(i,j)}v_{(i,j)}] = (1/16π)[∂_i(v_i v_{j,j} − v_j v_{i,j}) − ½ω·ω] [identity, eqs. 4.3–4.6].
  - ∫ρ d³x = −(1/32π)∫ω·ω d³x ≤ 0 for localized flows [theorem, eq. 7.17].
  - Eulerian flux f = (1/16π)∇×(∇×v); zero for gradient flows [identity, eqs. 4.7–4.8].
  - Zero-vorticity drives are Hawking–Ellis Type I (block-diagonal tensor), and for them WEC needs ρ ≥ 0 plus the NEC [derivation].
  - All physically reasonable Natário-class drives violate the NEC, hence WEC, SEC, DEC [theorem, with stated fall-off and smoothness hypotheses]: the NEC gives ρ + p̄ = (1/24π)(−2L_nK + K² − 3 tr K²) ≥ 0 (eq. 7.30), hence dK/dτ ≤ −(2/3) tr[K^tf]² ≤ 0 along Eulerian worldlines, which observers crossing the wall and returning to flat space must violate; the SEC is violated along the Eulerian congruence by a Raychaudhuri argument [theorem].
  - In modified gravity the null and timelike convergence conditions are still violated [claim/derivation].
- **Method / verification standard:** analytic, all-observer (NEC along all null vectors).
- **Scope and caveats:** unit lapse and flat slices (App. B names the N ≠ 1 and curved-slice generalizations as outside scope); "physically reasonable" is a localization hypothesis (Le 2026b note).
- **Disputes:** Huey 2024 evades it with non-compact thin membranes; Shoshany & Snodgrass 2024 extend the WEC part to non-unit lapse; Barzegar–Buchert–Vigneron 2026 restate it as Theorem IV.34 and record one minor error (Error 29) that leaves the result intact.
- **Relation to active-rail results:** (a) is the one-component, lapse-generalized case of eq. (4.5): for β = β(σ, z, r)ẑ the divergence term cancels and ρ = −ω²/32π pointwise. (c) is the Type I statement for zero flux; the project's zero-momentum condition is the general form (flux zero for any reason).
- **Key quote:** "That is, for the generic warp field, the Eulerian energy density is always the sum of a 3-divergence plus a quantity that is negative semi-definite." (§4.1)

### SSVADM2023 — Sebastian Schuster, Jessica Santiago, Matt Visser (2023), "ADM mass in warp drive spacetimes"
- **Citation:** Gen. Relativ. Gravit. 55, 14 (2023), DOI 10.1007/s10714-022-03061-9 (Crossref). arXiv:2205.15950v2 (4 Aug 2022); v1 31 May 2022. Read v2 (§2.3 and conclusions). Verified 2026-09-26.
- **Design parts and knobs:** where mass enters: payload, massive bubble, massive background; zero-vorticity flow fall-off v^i → v₀^i + √(2M/r) r̂.
- **Knob → physics relations:** Alcubierre and zero-expansion drives have identically zero ADM mass; zero-vorticity drives can carry non-zero ADM mass set by the flow fall-off, independent of interior masses; explicit NEC-violation locations for Schwarzschild-based and payload-carrying drives [derivation].
- **Method:** analytic, explicit stress-energy.
- **Scope and caveats:** Natário zero-vorticity class; Painlevé–Gullstrand-type foliations.
- **Disputes:** Barzegar–Buchert–Vigneron 2026 (Theorem IV.19; Remark IV.22–IV.24) state that every R-Warp model has vanishing ADM energy, that the Painlevé–Gullstrand foliation is not asymptotically flat in the ADM sense, and that the parameter M here is "at best ambiguous" — an open dispute.
- **Relation to active-rail results:** I10 (zero Komar mass for an exactly flat exterior) matches the zero-ADM-mass statement for truncated drives.
- **Key quote:** "both the Alcubierre and zero-expansion warp drives have identically zero ADM mass; whereas the zero-vorticity warp drive can, but need not, have a non-zero ADM mass." (§2.3)

### CarneiroEtAl2022 — F. L. Carneiro, S. C. Ulhoa, J. W. Maluf, J. F. da Rocha-Neto (2022), "On the total energy conservation of the Alcubierre spacetime"
- **Citation:** JCAP 07 (2022) 030, DOI 10.1088/1475-7516/2022/07/030. arXiv:2201.05684v2 (18 Aug 2022); v1 14 Jan 2022. Verified via abstract page 2026-09-26 (abstract read).
- **Design parts and knobs:** accelerating bubble; observer frame (static vs Eulerian); TEGR gravitational energy.
- **Knob → physics relations:** total (matter plus gravitational) energy is conserved during acceleration in TEGR; a static observer measures positive source energy where Eulerian observers measure negative [claim].
- **Disputes:** the "reference problem" reading conflicts with the frame-independent NEC violation (SSV 2022, Le 2026b); frame choice can hide negative energy from one observer family, never from all.
- **Relation to active-rail results:** a cautionary example for P01's all-observer rule.
- **Key quote:** "we find that a static observer measures positive energy of the source, while an Eulerian observer measures a negative one. Thus, we surmise that negative energy may be a reference problem." (abstract v2)

### BarceloEtAl2022 — Carlos Barceló, Valentin Boyanov, Luis J. Garay, Eduardo Martín-Martínez, Jose M. Sánchez Velázquez (2022), "Warp Drive Aerodynamics"
- **Citation:** JHEP 08 (2022) 288, DOI 10.1007/JHEP08(2022)288. arXiv:2207.06458v1 (13 Jul 2022; only version). Read v1. Verified 2026-09-26.
- **Design parts and knobs:** bubble shape (convexity, flatness of the front), trajectory (small zig-zags, alternating sub/superluminal intervals), dimension.
- **Knob → physics relations:**
  - On the boundary v = 1 of a stationary bubble, only points where the transverse derivative of the shape function vanishes (∂_y v = 0) can generate Cauchy horizons [derivation].
  - A smooth convex bubble has exactly two such points (front and back on the axis); one is future-unstable [derivation].
  - A flat or concave front (finite region with ∂_y v = 0) is less "aerodynamic" and accumulates more energy [derivation].
  - In 2+1 and higher dimensions the accumulation is limited to isolated points, so bubbles are "likely to be stable" [argument/estimate]; shape and trajectory can further disperse it [claim].
- **Method:** geodesic analysis near infinite-blueshift points; RSET estimated by analogy with 1+1, not computed.
- **Scope and caveats:** estimates; no 3+1 RSET.
- **Disputes:** qualifies Finazzi–Liberati–Barceló 2009 (same senior author) and Coutant et al. 2012.
- **Relation to active-rail results:** the transverse-gradient criterion is the literature counterpart of I13 (the surface α² = b² is null exactly where its transverse gradient vanishes). It explains why the project's flat front fall behaves as a white-hole disk and why a cone or rounded tip reduces the horizon to a point: the same design lever, front shape, controls (f).
- **Key quote:** "the only points on the boundary of the bubble v = 1 which have the possibility of generating Cauchy horizons are the ones where ∂_y v = ζ = 0, i.e. where the derivative of the shape function v in the direction perpendicular to that of motion is zero." (§III)

### AbellanBolivarVasilevSeries — Gabriel Abellán, Nelson Bolívar, Ivaylo Vasilev (2023–2026), matter-content warp studies
- **Citation (verified via arXiv abstract pages or Crossref, 2026-09-26):**
  - "Influence of anisotropic matter on the Alcubierre metric and other related metrics: revisiting the problem of negative energy", Gen. Relativ. Gravit. 55, 60 (2023), arXiv:2302.13826v3 (20 Apr 2023; v1 20 Feb, v2 19 Apr 2023). Read v3.
  - "Alcubierre warp drive in spherical coordinates with some matter configurations", Eur. Phys. J. C 83, 7 (2023), DOI 10.1140/epjc/s10052-022-11091-5 (Crossref); arXiv ID not identified (UNVERIFIED).
  - "Warp drive solutions in spherical coordinates with anisotropic matter configurations", arXiv:2305.03736v1 (4 May 2023), no journal reference.
  - "Spherical warp-based bubble with non-trivial lapse function and its consequences on matter content", Class. Quantum Grav. 41, 105011 (2024), DOI 10.1088/1361-6382/ad3ed9 (Crossref); arXiv ID not identified (UNVERIFIED).
  - Bolívar, Abellán, Vasilev, "Warp bubble geometries with anisotropic fluids: A piecewise analytical approach", Ann. Phys. 481, 170147 (2025), DOI 10.1016/j.aop.2025.170147 (Crossref); content from search-engine summary only (UNVERIFIED beyond title/journal).
  - "Gravitational Effects of Sources Inspired by ideal Electromagnetic Fields in Spherical Painlevé–Gullstrand Coordinates", Ann. Phys. 485, 170300 (2026), arXiv:2512.16109v1 (18 Dec 2025).
- **Design parts and knobs:** matter model (dust, isotropic, anisotropic fluid, heat flux, electrostatic-like fields); coordinate symmetry (Cartesian, cylindrical, spherical PG); lapse as an extra degree of freedom; piecewise density profiles.
- **Knob → physics relations:**
  - With the full Einstein equations and an anisotropic fluid, the Alcubierre energy density equals half the difference of tangential pressures, ρ = ½(p_z − p_y), and dust or isotropic fluids force ∂β/∂y = 0 and ρ = 0 [derivation, 2302.13826 eqs. 29–33].
  - A cosmological-constant term trades WEC against SEC; regions satisfying energy conditions exist in spherical PG-type bubbles; total mass can stay positive during evolution [numerical, 2305.03736].
  - A non-trivial lapse accommodates a heat-flux fluid [derivation, CQG 2024 via abstract].
  - Unit-lapse spherical PG with electrostatic-like sources: ρ tied to radial pressure by the field equations [derivation, 2512.16109].
- **Method:** analytic reductions and numerical ODE/PDE solutions; Eulerian or fluid-frame observers.
- **Scope and caveats:** the "not mandatory negative" conclusion rests on sources that force the transverse shift gradient to vanish, which removes the localized bubble.
- **Disputes:** Barzegar–Buchert–Vigneron 2026 (Error 20, Remark IV.27: unclear initial-value formulation); the headline claim is in tension with SSV 2022 for localized flat-slice drives.
- **Relation to active-rail results:** consistent with (a) once read correctly: forcing ∂⊥β = 0 sets ρ = 0, which is exactly (a). A positive Eulerian ρ for a one-component shift on flat slices contradicts (a) and SSV eq. (4.5), so the "sign depends on which tangential pressure dominates" statement is fixed by geometry to ρ ≤ 0.
- **Key quote:** "For matter such as dust or isotropic fluids we find that density and other related quantities become identically zero. This makes the negative energy problem spurious." (2302.13826 abstract v3)

### Pieri2023 — Lorenzo Pieri (2023), "Hyperwave: Hyper-Fast Communication within General Relativity"
- **Citation:** arXiv-only, arXiv:2311.12069v2 (16 May 2024); v1 19 Nov 2023. Verified via abstract page 2026-09-26 (abstract read).
- **Design parts and knobs:** bubble radius in the microscopic limit; tubular external negative-energy distribution; acceleration/deceleration mechanism.
- **Knob → physics relations:** small-radius bubbles need negative energy below that of a lightning bolt, "more than 70 orders of magnitude less than the original Alcubierre warp drive" [claim]; deceleration emits a ray of high-energy particles usable for signalling [claim, cf. McMonigal et al. 2012].
- **Scope:** unrefereed; energy estimates follow the E ∝ v²R²/Δ scaling.
- **Relation to active-rail results:** the proposed FTL signalling conflicts with the project's causality rule and with (g).
- **Key quote:** "In this regime the magnitude of the total negative energy requirements gets smaller than the energy contained in a lightning bolt, more than 70 orders of magnitude less than the original Alcubierre warp drive." (abstract v2)

### Huey2024 — Greg Huey (2024), "Membrane Models as a Means of Propulsion in General Relativity: Super-Luminal Warp-Drive that Satisfies the Weak Energy Condition"
- **Citation:** Class. Quantum Grav. 41, 135007 (2024), DOI 10.1088/1361-6382/ad4e00 (Crossref). arXiv:2311.07193v3 (6 May 2024); v1 13 Nov 2023, v2 16 Feb 2024. Verified via abstract page 2026-09-26.
- **Design parts and knobs:** chimeric bulk spacetimes joined by thin perfect-fluid membranes; per-side acceleration set by model parameters.
- **Knob → physics relations:** the Israel jump in extrinsic curvature produces apparent acceleration in each bulk; WEC satisfied everywhere in sub- and superluminal toy models [derivation]; the membrane jump can contribute positively to the Raychaudhuri equation, evading some no-go theorems [derivation, v3 addition].
- **Scope and caveats:** non-compact branes; quantum effects and stability not considered (author's statement).
- **Disputes:** sits outside the SSV 2022 hypotheses and the smooth-metric scope of Le 2026b (Le's note).
- **Relation to active-rail results:** a counterexample class to generalizing (a) and (g) beyond compact, smooth, asymptotically flat designs; (g) concerns quantum sources and compact support along a route, which the membranes do not have.
- **Key quote:** "Although the branes in these toy models are not compact, it is demonstrated that super-luminal warp-drive is possible that satisfies the WEC." (abstract v3)

### WarpFactory2024 — Christopher Helmerich, Jared Fuchs, Alexey Bobrick, Luke Sellers, Brandon Melcher, Gianni Martire (2024), "Analyzing warp drive spacetimes with Warp Factory"
- **Citation:** Class. Quantum Grav. 41, 095009 (2024), DOI 10.1088/1361-6382/ad2e42 (Crossref). arXiv:2404.03095v2 (10 Apr 2024); v1 3 Apr 2024. Read v2. Companion toolkit paper: "Warp Factory: A Numerical Toolkit for the Analysis and Optimization of Warp Drive Geometries", AIAA SciTech 2023 Forum, DOI 10.2514/6.2023-0553, arXiv:2404.10855v1. Verified 2026-09-26.
- **Design parts and knobs:** any metric on a grid; observer sampling density; lapse modification (Bobrick–Martire "modified time"); multi-component shifts (Lentz-inspired); perturbative optimizer (AIAA paper).
- **Knob → physics relations:**
  - Energy conditions evaluated as minima over sampled null and timelike observers (e.g. n_observers = 1000) at each point; fourth-order finite differences on a 1 m grid [method].
  - Alcubierre, Van Den Broeck, Modified Time (v_s = 0.1c, A_max = 2) and Lentz-inspired metrics all violate energy conditions [numerical].
  - The Lentz-inspired metric, with non-negative Eulerian energy, violates the WEC for boosted observers at the rhomboid interfaces, driven by pressure and momentum where the energy density vanishes [numerical].
- **Method / verification standard:** numerical; observer sampling (no certificate between samples or directions).
- **Scope and caveats:** sampled observers and sampled grid; no convergence ladder reported in the main text.
- **Disputes:** Barzegar–Buchert–Vigneron 2026 (Errors 19, 20) criticize the absence of a proper 3+1 initial-value formulation; Le 2026b adds certified bounds.
- **Relation to active-rail results:** the all-observer rule the project adopted (P01); momentum and pressure at shift boundaries are where violations sit, as in I5/I6.
- **Key quote:** "A notable finding in this work is a demonstration that metrics like the Lentz-inspired solution presented here, which may exhibit solely positive Eulerian energy density, can still violate the weak energy condition when examined across all timelike observers." (§6)

### Fuchs2024 — Jared Fuchs, Christopher Helmerich, Alexey Bobrick, Luke Sellers, Brandon Melcher, Gianni Martire (2024), "Constant Velocity Physical Warp Drive Solution"
- **Citation:** Class. Quantum Grav. 41, 095013 (2024), DOI 10.1088/1361-6382/ad26aa. arXiv:2405.02709v1 (4 May 2024; only version). Read v1. Verified 2026-09-26.
- **Design parts and knobs:** a stable anisotropic matter shell (R₁ = 10 m, R₂ = 20 m, M = 4.49×10²⁷ kg ≈ 2.365 Jupiter masses) solved with TOV plus smoothing; an interior shift β_warp added on top; non-unit lapse and curved spatial metric from the shell; positive ADM mass.
- **Knob → physics relations:**
  - Adding interior shift β_warp = 0.02 keeps NEC, WEC, DEC, SEC satisfied (not claimed as an upper limit) [numerical].
  - More shift adds momentum flux; physicality ends when flux exceeds energy density; shell mass is capped by R > 2GM/c² [claim/argument].
  - Round-trip light-time asymmetry δt ≈ 7.6 ns for the warp shell versus 0 for the bare shell (linear frame dragging), so the shift is not a coordinate artefact; comparison values at v_warp = 0.04c: Alcubierre 8.0 ns, Van Den Broeck 9.1 ns, Modified Time 6.7 ns [numerical].
  - With a lapse from positive ADM mass, light from B to A is still Shapiro-delayed; the Alcubierre metric shows an advance [numerical observation].
- **Method / verification standard:** numerical (Warp Factory), observer sampling (100 directions × 10 speeds); error analysis appendix.
- **Scope and caveats:** subluminal; constant velocity; modest shift; smoothing kernel choices.
- **Disputes:** Le 2026a finds Hawking–Ellis Type IV in 22 of 25 probes of the smoothing tail beyond R₂ (kernel-independent); Barzegar–Buchert–Vigneron 2026 (Error 18) state the construction does not solve the TOV equations and is not a solution of the Einstein equations; Le 2026a also finds prescribed and metric-implied sources disagree at O(10⁻¹).
- **Relation to active-rail results:** a positive-mass shell gives a Shapiro delay and no lead over light, consistent with (g) and I23; the flux-versus-density ceiling on the shift is the same trade as I5/I8 (flux linear in β, energy quadratic).
- **Key quote:** "This study demonstrates that classic warp drive spacetimes can be made to satisfy the energy conditions by adding a regular matter shell with a positive ADM mass." (abstract v1)

### CloughDietrichKhan2024 — Katy Clough, Tim Dietrich, Sebastian Khan (2024), "What no one has seen before: gravitational waveforms from warp drive collapse"
- **Citation:** Open J. Astrophys. 7 (2024), DOI 10.33232/001c.121868 (Crossref). arXiv:2406.02466v2 (24 Jul 2024); v1 4 Jun 2024. Read v2. Verified 2026-09-26.
- **Design parts and knobs:** Alcubierre initial data with fixed wall thickness; subluminal speed v (0.1–0.2, "related to the amplitude"); stiff-fluid equation of state for the warp matter; bubble size R.
- **Knob → physics relations:**
  - Containment failure produces a GW burst at frequency ~1/R; at v = 0.1, strain × extraction radius ~10⁻²R; a 1 km bubble at 1 Mpc gives strain ~10⁻²¹ at ~300 kHz [numerical].
  - Matter flux leaving the volume alternates in sign and exceeds the GW flux; the final quasi-local mass ends more positive than its initial zero; a positive-energy ring forms inside the negative shell and drives ejection [numerical].
  - Matter waves carry energy ~10⁻²R (≈1/100 solar mass for a 1 km bubble at v = 0.1) [numerical].
- **Method / verification standard:** full numerical relativity in GRChombo with shock-avoiding Bona–Massó slicing and a consistent fluid evolution; waves checked across resolutions, constraint convergence reported in an appendix.
- **Scope and caveats:** subluminal (0.1–0.2; up to 0.5 evolves stably but needs very high resolution); one equation of state; no ship.
- **Disputes:** Barzegar–Buchert–Vigneron 2026 call it "the only clear and sound work" in warp numerics while listing minor shortcomings.
- **Relation to active-rail results:** measures dynamics and radiation of a NEC-violating structure; relevant to the project's gaps on coupled dynamics; ADM mass stays zero at infinity while quasi-local mass rises.
- **Key quote:** "the true ADM mass should be conserved and remain at zero." (§2, footnote 2)

### GarattiniZatrimaylov2024_2025 — Remo Garattini, Kirill Zatrimaylov (2024; 2025), warp drives on curved backgrounds
- **Citation (verified via arXiv abstract pages and Crossref, 2026-09-26):**
  - "On the Wormhole–Warp Drive Correspondence", JCAP 08 (2024) 061, DOI 10.1088/1475-7516/2024/08/061; arXiv:2401.15136v2 (11 Apr 2024; v1 26 Jan 2024).
  - "Black Holes, Warp Drives, and Energy Conditions", Phys. Lett. B 856, 138910 (2024), DOI 10.1016/j.physletb.2024.138910; arXiv:2408.04495v4 (19 Dec 2024; v1 8 Aug, v2 24 Sep, v3 15 Oct 2024). Precursor "Black Holes and Warp Drive", arXiv:2311.06757v2.
  - "Warp Drive in a De Sitter Universe" (title of v4; Le 2026a cites it as "Positive-energy warp drive in a De Sitter universe", apparently an earlier version's title — which version carried it is UNVERIFIED), arXiv:2502.13153v4 (17 Jun 2026; v1 14 Feb 2025, v2 28 Feb 2025, v3 12 Jun 2026); no journal reference.
- **Design parts and knobs:** background geometry (Schwarzschild, Morris–Thorne wormhole, de Sitter); intrinsic curvature of slices; bubble speed relative to the background flow.
- **Knob → physics relations:**
  - A warp drive crossing a black-hole horizon subluminally sees no horizon inside the bubble; the black hole's field reduces WEC/NEC violation and the required negative energy [derivation].
  - Embedding a warp drive in a wormhole needs curved slices; a wormhole traversable by a warp drive must have a horizon ("humanly traversable wormholes cannot be traversed by a warp drive, and vice versa"), with stated loopholes [derivation/no-go claim].
  - In de Sitter, a bubble moving radially at the local expansion speed can have non-negative energy density, with WEC/NEC satisfied "up to a total divergence term that averages to zero" [derivation].
- **Scope and caveats:** the divergence identities do not establish pointwise energy-condition satisfaction (Le 2026b's note).
- **Relation to active-rail results:** background flows add to the shift; (a)'s divergence term is what the de Sitter construction exploits. The curved-background results show the energy of a flow field is measured against the background's own shift, consistent with I3 (a uniform flow costs nothing).
- **Key quote:** "we discover that the black hole's gravitational field can alleviate the violations of the weak energy condition (WEC) and the null energy condition (NEC) and therefore decrease the amount of negative energy required to sustain a warp drive" (2408.04495 abstract v4)

### ShoshanySnodgrass2024 — Barak Shoshany, Ben Snodgrass (2024), "Warp Drives and Closed Timelike Curves"
- **Citation:** Class. Quantum Grav. 41, 205005 (2024), DOI 10.1088/1361-6382/ad74d1. arXiv:2309.10072v3 (16 Sep 2024); v1 18 Sep 2023, v2 22 Apr 2024. Read v3. Verified 2026-09-26. (Causal-structure aspects are also covered in the QI/causality part.)
- **Design parts and knobs:** non-unit lapse N; compact support of the warp region; a frame-switching function; gluing two drives.
- **Knob → physics relations:**
  - The lapse lets a warp drive switch between inertial rest frames geometrically; two compact drives glued this way give a closed timelike geodesic [construction].
  - For flat slices with any lapse, ∫_Σ N²ρ d³x ≤ 0 (strict if β has curl) under C² smoothness and β = O(r^{-1/2}) fall-off; a non-unit lapse does not remove WEC violation [theorem, §4.1].
  - Relaxing the fall-off admits asymptotically flat gradient shifts with ρ ≥ 0 everywhere (explicit radial example) [construction].
  - Olum's 1998 theorem relies on the generic condition and a "fastest path" definition, which fail for drives with a Riemann-flat passenger region [argument].
  - Eulerian worldlines are geodesics iff ∂_iN = 0; drives with N = 1 or N = N(t) return passengers to the original rest frame, so geodesic rest-frame transitions need a spatially varying lapse (Sec. 2.1) [identity].
  - Flat slices with lapse N: ρ = (1/16πG)(1/N²)[(∂_iβ^i)² − ∂_(iβ_j)∂_(iβ_j)] (eq. 4.3) [identity]; E_tot = ∫ρ d³x "can however be made arbitrarily small simply by making N large where ∇β is large", at the cost that shell matter experiences the journey stretched by a factor of order N (Sec. 4.2) [claim].
  - With ρ = 0 = ∂_[iβ_j], the WEC forces ∂_t∫K d³x ≤ 0, which forbids drives that start from flat space and re-flatten unless T = 0 (Sec. 4.3) [derivation].
- **Method:** analytic.
- **Scope and caveats:** WEC (not NEC) for the lapse generalization.
- **Disputes:** Barzegar–Buchert–Vigneron 2026 accept the WEC result but criticize ADM usage (Error in Remark IV.22).
- **Relation to active-rail results:** for a pure shear shift β = β(x⊥)ẑ, eq. 4.3 gives ρ = −|∇⊥β|²/(32πN²), identical to (a) with N = α; the lapse-weighted integral is the literature form of (a) with a lapse: N²ρ carries the sign, and the lapse only reweights. It is also the literature precedent for (d): the lapse changes the frame the packet ends in, as the project's speed-scaling isometry I11 changes the carry speed. The Olum critique bears on (g): arguments from "superluminal ⇒ negative energy" need hypotheses that flat passenger regions violate; achronal-ANEC arguments must state theirs. Chronology: a rail network kept on one global foliation with positive lapse has a time function and forms no closed timelike curves; CTCs need drives (or rails) in two different rest frames, which is exactly what the lapse-driven frame switch provides.
- **Key quote:** "Put another way, Σ_t having zero intrinsic curvature coupled with it having non-zero extrinsic curvature leads to negative energy somewhere." (§4.2)

### Chowdhury2025 — Abhishek Chowdhury (2025), "Warp Drives and Martel–Poisson charts"
- **Citation:** accepted in Eur. Phys. J. C (per arXiv comments; volume not verified). arXiv:2404.15948v3 (29 Jan 2025); v1 24 Apr 2024, v2 28 Oct 2024. Verified via abstract page 2026-09-26 (abstract read).
- **Design parts and knobs:** background (Minkowski, AdS, dS) through Martel–Poisson charts; non-flat intrinsic metric; dimension.
- **Knob → physics relations:** non-flat slices introduce conical defects (3D) or non-zero spatial Ricci scalar (higher D) with "interesting scalings" of NEC violation; light-cone tilt and horizons discussed [derivation, abstract level].
- **Relation to active-rail results:** curved slices open the ³R energy channel outside (a)'s scope.
- **Key quote:** "We analyse the expansion/contraction of space and the (NEC) violations associated with these warp drives and find interesting scalings due to the global imprints of the conical defects." (abstract v3)

### SajeendranRalph2025 — Achintya Sajeendran, Timothy C. Ralph (2025), "Looping back to the past through free fall in a controlled warp drive spacetime"
- **Citation:** Phys. Rev. D 111, 124029 (2025), DOI 10.1103/1gmk-3zdq (Crossref). arXiv:2407.18993v2 (25 Mar 2025); v1 26 Jul 2024. Verified via abstract page 2026-09-26 (abstract read).
- **Design parts and knobs:** position-dependent effective rotation rate inside a "rotating" dynamical Alcubierre bubble.
- **Knob → physics relations:** making the rotation rate coordinate-dependent promotes a class of CTCs to spatially circular geodesics [derivation].
- **Relation to active-rail results:** a causal-structure hazard of shift fields with rotation; I19's single-rail time function excludes this within one rail.
- **Key quote:** "if the effective rotation rate is made dependent on the spacetime coordinates within the bubble, a class of closed timelike curves are promoted to spatially circular geodesics." (abstract v2)

### BarzegarBuchert2025 — Hamed Barzegar, Thomas Buchert (2025), "On restrictions of current warp drive spacetimes and immediate possibilities of improvement"
- **Citation:** Universe 11, 293 (2025), DOI 10.3390/universe11090293. arXiv:2407.00720v2 (1 Sep 2025; matches published version); v1 30 Jun 2024. Read v2. Verified 2026-09-26. (This is the Barzegar–Buchert paper; the three-author critique is arXiv:2602.16495.)
- **Design parts and knobs:** restrictions R1 flow-orthogonality (Eulerian = matter flow, irrotational), R2 lapse and shift choices, R3 flat slices; tilt of the matter 4-velocity; covariant vorticity and acceleration.
- **Knob → physics relations:**
  - For a one-component shift V^i = Vδ^i₁ on flat slices, 8πGε + Λ = −Ω² = −[(∂₂V)² + (∂₃V)²]/4 [derivation].
  - Vanishing coordinate vorticity gives ε = 0 (Λ = 0) or ε = −Λ/8πG [derivation].
  - Tilted flows (T-Warp) with covariant vorticity, acceleration and spatial curvature are proposed as the route to physical warp effects; "active generation of vorticity by the spaceship can produce acceleration" [claim/proposal].
- **Method:** covariant 3+1 kinematics.
- **Relation to active-rail results:** the one-component identity is exactly (a) at unit lapse: ε = −|∂⊥V|²/32π. The literature thus already holds (a); the project's contribution is the lapse factor α⁻² and its use as a design lever.
- **Key quote:** "We conclude that for irrotational Alcubierre warp drive, Ω = 0, (i) for Λ = 0, the energy density has to vanish" (§2.2)

### Rodal2025 — José Rodal (2025), "A warp drive with predominantly positive invariant energy density and global Hawking–Ellis Type I"
- **Citation:** Gen. Relativ. Gravit. 58, 1 (2026; published online 17 Dec 2025), DOI 10.1007/s10714-025-03495-x. arXiv:2512.18008v1 (19 Dec 2025; only version). Verified via abstract page 2026-09-26 (verbatim abstract read).
- **Design parts and knobs:** irrotational (scalar-potential) shift with closed-form potential; profile parameters ρ, σ, v/c; controlled vorticity ablation.
- **Knob → physics relations:**
  - Peak proper-energy deficit reduced ≈38× relative to Alcubierre and ≈2.6×10³× relative to Natário; peak NEC violation more than 60× smaller than Natário [numerical].
  - Global Hawking–Ellis Type I [derivation plus eigenanalysis].
  - Adding modest vorticity at fixed smoothing collapses the E₊/E₋ balance and raises the negative energy E₋ sharply: the gain is caused by irrotational kinematics, not profile shaping [numerical ablation].
  - Tail-corrected net proper energy |E₊ − E₋|/(E₊ + E₋) = 0.04% [numerical].
- **Method:** Cartan-tetrad analytic pipeline, high-precision eigenanalysis; slice-integrated proper energy.
- **Scope and caveats:** residual NEC/WEC violation remains (Rodal 2026 and Le 2026b); zero ADM mass (compact support).
- **Disputes:** Le 2026b: the Eulerian reading misses ≈73% of sampled wall WEC violations; Le 2026a: 9/50 probes violate NEC, 46/50 DEC; fails positive-ADM-mass criterion.
- **Relation to active-rail results:** confirms (c) (irrotational ⇒ zero momentum ⇒ Type I) and the integral form of (a) (∫ρ = −∫ω²/32π = 0 for ω = 0, hence the net zero proper energy). A one-component rail shift has vorticity wherever it has transverse gradient, so this route is closed to rail geometries of class C0.
- **Key quote:** "Crucially, the stress-energy is globally Hawking-Ellis Type I, with a well-defined timelike eigenvalue (proper energy density) everywhere." (abstract v1)

### CelmasterRubin2025 — Bill Celmaster, Steve Rubin (2025), "Violations of the Weak Energy Condition for Lentz Warp Drives"
- **Citation:** arXiv-only, arXiv:2511.18251v1 (23 Nov 2025; only version). Verified via abstract page 2026-09-26 (abstract read).
- **Knob → physics relations:** direct Eulerian-frame computation shows negative energy density regions in Lentz's geometry; several derivation errors identified; a corrected geometry still violates the WEC in the Eulerian frame [derivation/numerical].
- **Relation to active-rail results:** consistent with (a) integral form.
- **Key quote:** "We demonstrate that Lentz's claim is incorrect." (abstract v1)

### WhiteEtAl2025 — Harold White, Jerry Vera, Andre Sylvester, Leonard Dudzinski (2025), "Interior-flat cylindrical nacelle warp bubbles: derivation and comparison with Alcubierre model"
- **Citation:** Class. Quantum Grav. 42, 235022 (2025), DOI 10.1088/1361-6382/ae237a. No arXiv version identified. Verified via the IOP abstract page 2026-09-26 (abstract read).
- **Design parts and knobs:** number n = 2, 3, 4 of Gaussian cylindrical "nacelles" around the bubble; end-cap shaping; interior flatness.
- **Knob → physics relations:** segmentation localizes the exotic stress-energy into discrete cylindrical channels while keeping the interior flat and synchronized with external clocks [derivation/numerical maps].
- **Scope:** Eulerian quantities; all-observer character of the wall unchanged (Le 2026b's note).
- **Relation to active-rail results:** (a) applied to segmented shifts: energy follows the transverse shear wherever it is placed; segmentation relocates it.
- **Key quote:** "exotic matter localization, end-cap shaping, and interior flatness are tunable engineering parameters consistent with general relativity." (abstract)

### Rodal2025Metamaterial — José Rodal (2025), "On the Infeasibility of Low-Energy Warp Drive via Metamaterial Gravitational Coupling"
- **Citation:** arXiv-only, arXiv:2507.09724v2 (20 Jul 2025); v1 13 Jul 2025. Verified via abstract page 2026-09-26 (abstract read).
- **Knob → physics relations:** a prescribed spatially varying coupling κ(x) in G = κT violates ∇T = 0 through the Bianchi identity; a dynamical κ is a scalar–tensor theory excluded by |γ − 1| ≲ 10⁻⁵; interfaces need δ-function stress layers [derivation plus experimental bounds].
- **Relation to active-rail results:** none visible; relevant to the book's treatment of "coupling engineering" proposals.
- **Key quote:** "a non-dynamical scheme violates conservation laws, and its scalar-tensor completion is falsified by existing data." (abstract v2)

### BarzegarBuchertVigneron2026 — Hamed Barzegar, Thomas Buchert, Quentin Vigneron (2026), "General formalism, classification, and demystification of the current warp-drive spacetimes"
- **Citation:** arXiv-only, arXiv:2602.16495v1 (18 Feb 2026; only version). Theorem statements and the Errors list of v1 read. Verified 2026-09-26. This is the "source-consistency critique" Le 2026a answers.
- **Design parts and knobs:** R-Warp class (flow-orthogonal, unit lapse, flat slices, asymptotically flat); switching factor for turn-on; shear-free and harmonic-gradient shifts; ADM energy and momentum; DEC.
- **Knob → physics relations:**
  - Theorem III.15: coordinate-vorticity-free Alcubierre is Minkowski [theorem].
  - Theorem IV.7: a superluminal R-Warp model cannot be globally hyperbolic (turn-on from subluminal is excluded) [theorem].
  - Theorem IV.16: shear-free R-Warp models are Minkowski; Theorem IV.17: a harmonic-gradient shift gives Minkowski [theorems].
  - Theorem IV.19: R-Warp ADM energy vanishes; ADM momentum is generically non-zero; both vanish for Alcubierre [theorem].
  - Theorem IV.20: DEC plus the positive-energy theorem forces an R-Warp model to be Minkowski; Corollary IV.37: R-Warp models violate the DEC [theorem].
  - Theorem IV.33: a non-vacuum spacetime with a maximal (K = 0) foliation and R < 2Λ + |K|² violates the WEC [theorem].
  - 37 numbered "Errors" in the literature, including Fuchs et al. (not a TOV solution; Error 18), Bobrick–Martire, Lentz, Helmerich et al., Abellán et al.; Clough et al. called the only sound numerical work [critique].
- **Method:** covariant 3+1 analysis and proofs.
- **Scope and caveats:** theorems are for the R-Warp class; arXiv-only.
- **Disputes:** with SSV 2023 on ADM mass (see SSVADM2023); with Fuchs et al. 2024 and Bobrick–Martire 2021.
- **Relation to active-rail results:** Theorem IV.20 is the unit-lapse, flat-slice statement that DEC matter cannot support any non-trivial flow, consistent with (a). Theorem IV.7 needs comparison with I19 (the project's global time function σ on one rail): a time function gives stable causality, which is weaker than global hyperbolicity, so the two can coexist; this deserves a check in the book. Theorem IV.19 (ADM momentum non-zero in general) bears on the project's recoil accounting.
- **Key quote:** "Our analysis shows that when the principles of General Relativity are applied correctly, most claims regarding physical warp drives must be reassessed, and it becomes highly challenging to justify or support the viability of such models, not merely due to the violation of energy conditions." (abstract v1)

### BuchertFrackowiak2026 — Thomas Buchert, Antony Frackowiak (2026), "Novel Realizations of Warp Drive Spacetimes as Solutions of General Relativity"
- **Citation:** Universe 12, 132 (2026), DOI 10.3390/universe12050132. arXiv:2605.03653v1 (5 May 2026; only version). Verified via abstract page 2026-09-26 (abstract read).
- **Design parts and knobs:** Synge G-method realizations with one-component coordinate velocity; coordinate acceleration and vorticity; spatial curvature via relativistic Lagrangian perturbation theory and Szekeres class II solutions; tilted flows.
- **Knob → physics relations:** in Alcubierre's model changes of the velocity profile are suppressed apart from an external amplitude; a geodesically determined realization shows a generic instability of the warp field [derivation].
- **Relation to active-rail results:** none directly; supports treating dynamics and tilt as design dimensions.
- **Key quote:** "For the second we find an expected generic instability of the warp field." (abstract v1)

### Le2026b — An T. Le (2026), "Observer-robust energy condition verification for warp drive spacetimes"
- **Citation:** arXiv-only, arXiv:2602.18023v6 (24 Sep 2026); v1 20 Feb, v2 3 Mar, v3 27 Apr, v4 12 Jun, v5 1 Sep, v6 24 Sep 2026. Read v6. Toolkit "warpax" (JAX; Zenodo record). Verified 2026-09-26.
- **Design parts and knobs:** four drives at matched parameters (Alcubierre, Natário, Van Den Broeck, Rodal) across sub- and superluminal speeds; shift vorticity; speed-linear shifts.
- **Knob → physics relations:**
  - NEC, WEC, SEC as 4×4 linear matrix inequalities via the S-lemma; DEC needs two tests; no Hawking–Ellis classification and no rapidity cutoff needed [theorem, Theorem 1].
  - Interval evaluation of metric and curvature gives pointwise certificates and global bounds on the minimum over the wall [method].
  - On time-independent flat unit-lapse slices, 8π|j| = ½|∇×(∇×β)|; for smooth shifts with bounded vorticity on R³, j ≡ 0 exactly for a gradient plus rigid rotation [lemma, Lemma 2].
  - For shifts linear in speed, integrated negative Eulerian energy scales exactly quadratically on a fixed domain [lemma, Lemma 4].
  - Ideal Rodal profile is Type I at every speed [lemma, Lemma 3]; Alcubierre, Natário, Van Den Broeck walls are 81–99% Type IV at v_s = 0.5; Van Den Broeck's Type-IV fraction crosses 50% at v_s ≈ 0.38 [numerical].
  - The Eulerian reading misses ≈73% (WEC) and ≈74% (DEC) of sampled wall violations in the Rodal wall [numerical].
  - Global bounds establish NEC violation in all four walls at reference parameters [certified numerical].
  - Flat-space QI threshold for a static wall observer τ₀,th ≃ c_metric (ℓ_P R_b)^{1/2}, the geometric mean of the Planck length and bubble scale (eq. 36) [derivation].
  - ∫T(k,k)dλ scales by c under k ↦ ck: ANEC magnitudes depend on the affine normalization, their signs do not (Sec. 3.5) [identity].
- **Method / verification standard:** certified (interval) bounds plus sampled type labels; resolution ladder; symplectic null-geodesic integrator for finite-segment ANEC; flat-space QI estimates.
- **Scope and caveats:** flat unit-lapse slices for the lemmas; type labels are numerical and distinct from interval bounds (author's statement); "The null-geodesic integrals are finite-segment, basin-local diagnostics … they supply no complete-geodesic ANEC conclusion. The flat-space quantum-inequality estimates likewise supply no curved-spacetime bound." (Sec. 6)
- **Disputes:** none against it found; it adjudicates Rodal's positive-energy reading.
- **Relation to active-rail results:** the normalization identity applies to the project's ANEC magnitudes (−202, −2.2×10⁴), whose signs carry the physics. (c) appears here for flat unit-lapse slices; the project's I2 extends zero momentum to shift-free or uniform-shift regions with any lapse. The vorticity → Type IV mechanism matches the project's I6 (Type IV where a one-component shift begins to vary). The quadratic law is (a)'s scaling.
- **Key quote:** "On flat unit-lapse slices, the momentum constraint relates Eulerian momentum to shift vorticity. For smooth shifts on all of Euclidean space with bounded vorticity, momentum vanishes identically precisely for a gradient plus rigid rotation." (abstract v6)

### Rodal2026Birefringent — José Rodal (2026), "Weakly birefringent screening disfavors fast Hawking–Ellis Type I warp drives via low-velocity cubic tilt scaling" (v1–v2)
- **Citation:** arXiv:2603.21352v2 (24 Mar 2026); v1 22 Mar 2026. **Version hazard:** v3 (24 May 2026) replaces the paper with "Tamm–Rubilar branch diagnostics for Drummond–Hathrell photon propagation: Schwarzschild calibration and a Kerr weak-lensing benchmark", and the warp-screening claim is "removed as a main result and retained only as an appendix-level test" (v3 comments). Cite v2 for the warp content. Verified via abstract pages 2026-09-26 (abstracts read).
- **Design parts and knobs:** weakly birefringent area-metric deformation of the vacuum (SSSW framework) as a screening medium; wall speed v; polar angle θ.
- **Knob → physics relations:** the mixed-sector tilt needed to absorb the residual NEC deficit of an irrotational Type I wall scales approximately as v³ for v ≲ 1 at θ = π/4, follows an exact cubic at θ = π/2, and departs strongly at higher v; fast walls are disfavoured [numerical, exploratory, reduced model].
- **Relation to active-rail results:** none visible; the project uses standard vacuum.
- **Key quote:** "The resulting evidence disfavors fast walls within the reduced perturbative model, while indicating that smaller subluminal velocities are less strained by the reduced admissibility conditions." (abstract v2)

### Le2026a — An T. Le (2026), "On the boundary cost of source-consistent warp shells" (v1–v2)
- **Citation:** arXiv:2605.25417v2 (20 Jun 2026); v1 25 May 2026 has the same title and abstract. **Version hazard:** v3 (17 Sep 2026) is a different paper, "Relativistic elastic shells: material support and cavity geometry". Cite v2. Read v2 (abstract, admissibility standard, Fuchs verification, scan and ANEC sections). Verified 2026-09-26.
- **Design parts and knobs:** source-first shells: shift-free S-shell (lapse depression from TOV) and T-shell (shift from the momentum constraint for tilted matter, v₀); shell compactness C = M/R₂ ∈ [0.01, 0.20] and thickness ratio (20 × 15 = 600 configurations); smoothing kernels; five-criterion standard (regularity, constraint satisfaction, explicit matter model, frame-independent EC margins, global diagnostics).
- **Knob → physics relations:**
  - In all eight constructions graded (Alcubierre, Natário, Van Den Broeck, Rodal, Lentz, Fuchs, S-shell, T-shell), failures localize at the smooth source–vacuum transition; the matter bulk is Type I and compliant [numerical, certified margins].
  - The boundary failure splits into a Type I DEC deficit fixed by source-profile regularity and independent of v₀ (−4.42 to −4.55×10⁻⁴ across v₀ = 0–0.2; also in the static v₀ = 0 limit and in the shift-free S-shell), and a Type-IV onset whose imaginary eigenvalue grows linearly with tilt (log–log slope 1.01 ± 0.01) [numerical].
  - No admissible configuration in the 600-point compactness–thickness scan [numerical].
  - Fuchs shell: interior compliant (0/13 probes), 22/25 smoothing-tail probes Type IV, kernel-independent [numerical].
  - Geodesic-integrated null energy is positive for every source-prescribed shell (Fuchs ≈ +1.9×10⁻³, S ≈ +2.9×10⁻³, T ≈ +4.6×10⁻³ at v₀ = 0.1) across impact parameters [numerical, exploratory].
  - Null round-trip asymmetry δτ ≈ −0.795 at v₀ = 0.1 and −1.67 at 0.2 (near-linear in speed) [numerical].
- **Method / verification standard:** warpax certifier; constraint residuals; kernel robustness checks.
- **Scope and caveats:** spherical shells; quasi-static; ANEC along a representative ray is "an exploratory diagnostic rather than a proof".
- **Disputes:** challenges Fuchs et al. 2024; responds to Barzegar–Buchert–Vigneron 2026.
- **Relation to active-rail results:** the project's P01 findings (failures concentrate at transitions to vacuum; Type IV where shift varies) have their closest literature analogue here. Linear Type-IV onset in tilt parallels I5c (flux linear in β). Positive ANEC for positive-mass subluminal shells is consistent with (g): no lead over light, no achronal ANEC deficit required.
- **Key quote:** "The same boundary deficit appears in the shift-free S-shell and persists in the static v₀=0 limit, which ties it to the transition geometry rather than to the shift." (abstract v2)

### Le2026c — An T. Le (2026), "Radiative steering of warp shells" (v4); v1–v3 "Steering a warp drive without exotic matter"
- **Citation:** arXiv:2606.22531v4 (13 Sep 2026; "substantially revised and retitled"); v1 21 Jun, v2 30 Jun, v3 15 Jul 2026 carry the old title. Abstracts of v1–v4 read; v1 and v4 PDFs downloaded. Verified 2026-09-26.
- **Design parts and knobs:** compact flat cavity inside a thin timelike shell; exterior Kinnersley photon rocket; prescribed passenger worldtube; burn schedule and axis; compactness 2m/R; emission anisotropy.
- **Knob → physics relations:**
  - Bondi–Sachs balance as a propulsion law: an asymptotically flat drive with a confined DEC source changes its Bondi four-momentum only by radiating to null infinity [theorem-level argument, v1–v3].
  - Steering law −ṁ ≥ 3m|a| (v1–v3); burns joined at static spheres give m_f/m_i = e^{−3L} for exterior velocity-space path length L (v4) [derivation].
  - Static shell satisfies the surface DEC for 2m/R < 24/25; an acceleration–compactness frontier a_max R ≤ g(2m/R) with ceiling ½(1 − 2m/R) (v1) [derivation].
  - Minimum-radiation steering is the GW-silent Damour dipole, Tsiolkovsky constant 3 [derivation].
  - The radiating equilibrium is linearly unstable, growth bounded by the fuel budget over finite burns (v3); self-similar shells need anisotropic stress and have growing normal modes (v4) [derivation].
- **Method:** exact exterior solution, perturbative/numerical shell certification, stability analysis.
- **Scope and caveats:** thin-shell idealization; subluminal; self-gravitating settling after a turn open (v4).
- **Relation to active-rail results:** the literature form of the project's rule that recoil and boundary exchange must be accounted explicitly: every change of the carried momentum is paid by radiation or by exchange with external structure.
- **Key quote:** "any asymptotically flat, confined dominant-energy drive changes Bondi four-momentum only by radiating to null infinity, so it cannot steer without radiating." (abstract v3)

### BolivarAbellanVasilev2026 — Nelson Bolívar, Gabriel Abellán, Ivaylo Vasilev (2026), "Boundary Obstructions and Lapse Freedom in Static Spherical Hollow Cores"
- **Citation:** arXiv-only, arXiv:2608.15000v1 (15 Aug 2026; only version). Abstract and the quoted sections of v1 read. Verified 2026-09-26.
- **Design parts and knobs:** static hollow core (flat cavity plus positive-density wall); unit-lapse flat-slice radial PG class; unit-lapse curved slices; lapse released (incomplete-beta profile F_n with wall aspect ratio η and degree n).
- **Knob → physics relations:**
  - Unit-lapse, flat-slice radial PG: the Type I source obeys p_r = −ρ and p_⊥ = −ρ − rρ′/2, so a regular non-negative density rising out of the cavity violates the transverse NEC and WEC; quantified by an onset budget and a depth–width bound [theorem].
  - Unit lapse with curved slices (monotone areal radius, radial NEC both ways, flat inner boundary, asymptotic flatness) forces flat slices (Theorem 5) [theorem].
  - Releasing only the lapse gives regular hollow shells with flat cavities, Schwarzschild exteriors, no thin shells, satisfying NEC/WEC/SEC/DEC on an explicit compactness interval; a fixed-ADM-mass cavity-redshift benchmark [construction].
- **Method:** analytic proofs and explicit family.
- **Scope and caveats:** static; not a transport result (authors' statement).
- **Relation to active-rail results:** direct support for (b) and I2/I10: the lapse carries the stress balance that a positive wall needs; at unit lapse the boundary deficit is forced, as in Le 2026a. The rising-density obstruction is the radial-PG analogue of the project's boundary-layer findings.
- **Key quote:** "Finally, when only the lapse is released, an incomplete-beta family gives regular hollow shells with flat cavities, Schwarzschild exteriors, no thin shells, and NEC/WEC/SEC/DEC on an explicit compactness interval." (abstract v1)

### Gergely2026 — László Árpád Gergely (2026), "Fluid interpretation, Hawking–Ellis classification, and energy conditions of the proper kinetic gravity braiding stress tensor"
- **Citation:** accepted in Phys. Rev. D (per arXiv comments). arXiv:2608.15228v1 (15 Aug 2026; only version). Abstract read; v1 full text searched for the classification statements. Verified 2026-09-26.
- **Design parts and knobs:** scalar-gradient character (timelike, spacelike, null) of a kinetic-gravity-braiding scalar; discriminants of the effective fluid.
- **Knob → physics relations:** braiding generates heat fluxes and anisotropic stress; timelike sector Type I / II / IV for positive / zero / negative discriminant; the NEC excludes Types III and IV; admissible spacelike braiding is diagonal [theorem-level classification].
- **Relation to active-rail results:** matches the project's use of Hawking–Ellis type as a source-matching criterion (P01 §2g): braiding scalars can supply Type IV only where the NEC fails, which is where warp demands put their Type IV.
- **Key quote:** "The null energy condition excludes Types III and IV and, for spacelike gradients, every nonzero radial heat flux or mixed anisotropy." (abstract v1)

### MartinMorenoVisser2018_2021 — Prado Martín-Moruno, Matt Visser, Hawking–Ellis type papers
- **Citation:** "Essential core of the Hawking–Ellis types", Class. Quantum Grav. 35, 125003 (2018), arXiv:1802.00865v2 (11 May 2018; v1 2 Feb 2018). "Hawking–Ellis classification of stress-energy: test-fields versus back-reaction", Phys. Rev. D 103, 124003 (2021), arXiv:2102.13551v2 (5 Mar 2021; v1 26 Feb 2021). Verified via abstract pages 2026-09-26 (abstracts read).
- **Knob → physics relations:** types I and IV are stable under perturbation, II and III unstable; type IV arises semiclassically (e.g. Unruh state on Schwarzschild) [2018]; with Einstein back-reaction, any static spacetime has Type I stress-energy in the domain of outer communication and on horizons, and several stationary cases are Type I on horizons and axes [theorems, 2021].
- **Relation to active-rail results:** the 2021 static theorem is the published precedent for (c) and I2 in static slicing (zero Eulerian momentum ⇒ Type I).
- **Key quote:** "in any static spacetime the stress-energy is always type I in the domain of outer communication, and on any horizon that might be present" (2102.13551 abstract v2)

### JusufiLobo2026 — Kimet Jusufi, Francisco S. N. Lobo (2026), "Quantum-gravity-inspired Alcubierre warp-drive geometries"
- **Citation:** arXiv-only, arXiv:2609.05554v1 (3 Sep 2026; only version). Verified via abstract page 2026-09-26.
- **Design parts and knobs:** warp profile f(r_s) = 1 − r_s³/(r_s² + l²)^{3/2} with l² = R² + l₀² (T-duality zero-point length l₀).
- **Knob → physics relations:** closed-form total Eulerian energy E = −(15π/1024) v_s² l and |ρ_E| ≲ const × v_s²/l²; the R → 0 divergence at fixed speed is removed because l ≥ l₀ [derivation]; exotic matter still required.
- **Scope and caveats:** effective ansatz (authors' statement); no RSET computed.
- **Relation to active-rail results:** another instance of the v² energy law of (a) with the profile scale as the only length.
- **Key quote:** "In particular, $E=-(15\pi/1024)v_s^2 l$ in geometric units and $|\rho_E|$ is bounded by a constant times $v_s^2/l^2$." (abstract v1)
