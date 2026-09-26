# Theorems and constraints that bind superluminal and shortcut designs

Quantum inequalities (QIs), averaged null energy conditions (ANEC, achronal ANEC), smeared null bounds (SNEC, DSNEC), superluminal censorship, time-delay theorems, speed limits and chronology. Inventory part for the metric-engineering textbook, compiled 2026-09-26.

## Verification protocol

- Every arXiv record was checked on 2026-09-26 in two ways: WebFetch of `https://arxiv.org/abs/<id>` (title, authors, submission history, journal reference) and direct retrieval of the same abs page, from which title, authors, submission history, journal reference, DOI and abstract were extracted verbatim. The two agreed in every case.
- Full-text statements come from the text layer (pdftotext) of the pinned PDF `https://arxiv.org/pdf/<id>v<N>`. The pinned version is the latest version on 2026-09-26 unless stated. Abstract quotes are verbatim from the abs page, which carries the latest version's abstract.
- Entries marked **abstract-level** rest on the abstract alone.
- Journal references marked "(Crossref)" come from `api.crossref.org`, because the arXiv page shows only the DOI.
- Two papers have no arXiv version (Hawking 1992, Everett 1996). They were verified from APS metadata (WebFetch of the APS abstract page, which returned a paraphrase), Crossref metadata and the text of the published article; each entry names its sources.
- Equations quoted from PDF text layers keep the paper's notation. Where the text layer lost typeset symbols, the entry says so.

**Tags.** [identity/theorem] a proved statement within its stated hypotheses; [derivation] follows from an explicit calculation in the paper, or, when marked *(this inventory)*, from quoted statements combined here; [numerical] a number from evaluation or simulation; [claim] asserted, conjectured or argued without proof.

**Project results used in the "Relation" fields** (from `supporting_reports/ANEC_MAP_PASS.md` and the caller's brief). (a) On flat spatial slices the Eulerian energy density is ρ = −(∂⊥β/α)²/32π, so only shift shear carries energy density. (b) The lapse carries stress without energy. (c) Zero Eulerian momentum ⇒ Hawking–Ellis Type I. (d) Speed appears as a lapse contrast. (e) A moving conical front needs half-angle sin θ < 1/v. (f) A front light surface traps overtaken light. (g) Achronal ANEC excludes quantum sources for any lead over light, i.e. any configuration in which a carried packet arrives before a light signal through the exterior. The project text reads: "The design needs negative ANEC along achronal light rays, as any lead over exterior light does … A semiclassical quantum sector therefore supplies none of this demand, at any size."

**Cross-reference.** Pfenning & Ford 1997, "The unphysical nature of 'Warp Drive'" (gr-qc/9702026), is covered by the warp-drive cluster and gets no section here. Its bubble-wall result (a wall of a few hundred Planck lengths, per Kontou & Sanders 2020, Sec. 5) is cited below only through verified secondary statements.

---

## A. Quantum inequalities along timelike worldlines

### FR95 — L. H. Ford, Thomas A. Roman (1995), "Averaged Energy Conditions and Quantum Inequalities"
- **Citation:** Phys. Rev. D 51, 4277–4286 (1995); DOI 10.1103/PhysRevD.51.4277; report TUTP-94-16. arXiv:gr-qc/9410043v1 (read; v1 only). Submission history: v1 Sat, 29 Oct 1994 01:33:00 UTC. Verified via https://arxiv.org/abs/gr-qc/9410043 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9410043v1.
- **Design parts and knobs:** the sampling time τ0 of a geodesic observer crossing a negative-energy region; the magnitude and duration of negative energy density; the field content.
- **Knob → physics relations:**
  - [identity/theorem] For a free, massless, minimally coupled scalar in 4D Minkowski space and any quantum state, the Lorentzian-weighted energy density on any timelike geodesic obeys ρ̂ = (τ0/π)∫⟨T_μν u^μ u^ν⟩ dτ/(τ²+τ0²) ≥ −3/(32π² τ0⁴) for all τ0 (Sec. 4, eqs. 64–65). A negative density of magnitude |ρ| therefore persists for at most a proper time of order |ρ|^(−1/4) (ħ = c = 1).
  - [derivation] τ0 → ∞ gives AWEC along every timelike geodesic. The null limit gives ANEC in 4D Minkowski space (eqs. 66–67).
  - [claim] A 4D null-geodesic QI with a λ0^(−4) right-hand side "would not be invariant under rescaling of the affine parameter and hence does not seem to be meaningful" (Sec. 4). FR03 later proved that no such inequality exists.
  - [claim] Assembling warp-scale negative energy from flat space is self-limiting, because compensating positive energy arrives before enough negative energy has been collected (Sec. 5).
- **Method / verification standard:** analytic spherical-wave mode sum evaluated at r = 0; Lorentz covariance extends the result to every inertial observer. Peer-reviewed.
- **Scope and caveats:** covers a free massless minimally coupled scalar with one specific (Lorentzian) sampling function in flat space without boundaries. The 2D compactified results are difference inequalities relative to the Casimir vacuum.
- **Disputes, refutations, later corrections:** FE98 generalized the result to other sampling functions, PF98 and F00 to curved spacetimes. Interacting fields can violate QIs (OG03). K03 disputes the use of QIs to infer that shortcuts are unphysical.
- **Relation to active-rail results:** (a) *(this inventory, [derivation])* Take a shear layer with shift jump Δβ across width w. Result (a) gives |ρ| ≈ (Δβ/(αw))²/32π, and the curvature radius is r_c ≈ αw/Δβ. The flat-space QI with τ0 = f r_c and ħ = ℓ_P² (G = c = 1) then requires αw/Δβ ≲ (3/π)^(1/2) ℓ_P/f². This is the same form as the Krasnikov-tube wall bound in ER97. The QI therefore limits the layer's curvature radius, and the lapse in the layer rescales the allowed width linearly (w ≲ (Δβ/α) ℓ_P/f²). The estimate assumes that curved-space QIs take the flat form on the scale f r_c (PF98) and that Ricci and Weyl curvature are comparable (K03). Eulerian observers are non-geodesic wherever the lapse varies, so F00-type corrections apply. (g): none directly.
- **Key quote:** "The bound implies that any inertial observer in flat spacetime cannot see an arbitrarily large negative energy density which lasts for an arbitrarily long period of time." (abstract, v1)

### FR96 — L. H. Ford, Thomas A. Roman (1996), "Quantum Field Theory Constrains Traversable Wormhole Geometries"
- **Citation:** Phys. Rev. D 53, 5496–5507 (1996); DOI 10.1103/PhysRevD.53.5496; report TUTP-95-4. arXiv:gr-qc/9510071v1 (read; v1 only). Submission history: v1 Tue, 31 Oct 1995 23:42:50 UTC. Verified via https://arxiv.org/abs/gr-qc/9510071 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9510071v1.
- **Design parts and knobs:** the throat radius r0; the thickness a0 of the negative-energy band; the redshift function; the sampling fraction f (τ0 = f × smallest local length scale); the number of fields N.
- **Knob → physics relations:**
  - [claim] The flat-space QI holds in curved space for sampling times small compared with the smallest local curvature radius and the distance to any boundary (Sec. 2). PF98 later derived this for static spacetimes.
  - [derivation] For a0 < r0 with τ0 = f a0: a0 ≲ (r0/(8 f⁴ ℓ_P))^(1/3) ℓ_P (eq. 69, as read from the text layer).
  - [numerical] With f ≈ 0.01: r0 ≈ 1 m gives a0 ≲ 10¹⁴ ℓ_P ≈ 10⁻²¹ m. Even a galaxy-sized throat confines the band to about 10 proton radii (Sec. 4).
  - [derivation] N fields relax the bound only as √N. A 1 m throat needs about 10⁶² fields (Conclusions).
  - [claim] Compliance is possible only with geometries that involve "large redshifts (or blueshifts)" or extreme length-scale discrepancies (Conclusions).
- **Method / verification standard:** the flat-space QI of FR95 applied to static Morris–Thorne geometries, with a static observer at the throat. Analytic.
- **Scope and caveats:** static, spherically symmetric wormholes; massless minimally coupled scalar; curved-space applicability assumed.
- **Disputes, refutations, later corrections:** K03 argues that the QI need not imply Planck-scale densities, citing Weyl-dominated regions and Casimir-like periodic identifications.
- **Relation to active-rail results:** (b)/(d) The lapse is the rail's redshift function. FR96 names large redshifts as the geometric escape route from the band bound, which ties lapse contrast to QI compliance. The cost of large redshifts is passenger-relevant tides and blueshifts (Conclusions). (g): none.
- **Key quote:** "Our analysis implies that either the wormhole must be only a little larger than Planck size or that there is a large discrepancy in the length scales which characterize the wormhole. In the latter case, the negative energy must typically be concentrated in a thin band many orders of magnitude smaller than the throat size." (abstract, v1)

### FR97 — L. H. Ford, Thomas A. Roman (1997), "Restrictions on Negative Energy Density in Flat Spacetime"
- **Citation:** Phys. Rev. D 55, 2082–2089 (1997); DOI 10.1103/PhysRevD.55.2082; report TUTP-96-2. arXiv:gr-qc/9607003v2 (read; 24 Jan 1997). Submission history: v1 Mon, 1 Jul 1996 17:17:18 UTC; v2 Fri, 24 Jan 1997 22:48:00 UTC ("minor revisions in the Introduction, conclusions unchanged"). Verified via https://arxiv.org/abs/gr-qc/9607003 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9607003v2.
- **Design parts and knobs:** the sampling time t0; field species (massless scalar, massive scalar, electromagnetic); mass m.
- **Knob → physics relations:**
  - [identity/theorem] Massless scalar in 4D: ρ̂ ≥ −3/(32π² t0⁴) (eq. 1). Electromagnetic field: ρ̂ ≥ −3/(16π² t0⁴) (eq. 48), a factor 2 weaker, one factor per polarization.
  - [derivation] A mass m tightens the bound, because negative energy must overcome the rest mass (Sec. 4).
  - [claim] With restricted sampling time, the bounds should hold in curved space and near boundaries (Sec. 4).
- **Method / verification standard:** plane-wave mode expansion with two operator lemmas (Appendix A). Analytic.
- **Scope and caveats:** free fields, Minkowski space, Lorentzian sampling.
- **Disputes, refutations, later corrections:** generalized by FE98 and F00.
- **Relation to active-rail results:** fixes the species factor in any QI budget for (a). (g): none.
- **Key quote:** "Recently we argued that such bounds should also hold in a curved spacetime and/or one with boundaries, if the sampling time is restricted to be much smaller than the smallest local radius of curvature and/or the distance to any boundaries in the spacetime" (Sec. 4, Conclusions, v2)

### PF98 — Michael J. Pfenning, L. H. Ford (1998), "Scalar Field Quantum Inequalities in Static Spacetimes"
- **Citation:** Phys. Rev. D 57, 3489 (1998); DOI 10.1103/PhysRevD.57.3489; report TUTP-97-10. arXiv:gr-qc/9710055v1 (read; v1 only). Submission history: v1 Thu, 9 Oct 1997 22:47:29 UTC. Verified via https://arxiv.org/abs/gr-qc/9710055 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9710055v1.
- **Design parts and knobs:** the static observer's sampling time; the metric component g_tt (the lapse squared for a static observer); scalar curvature R; field mass; distance to a horizon.
- **Knob → physics relations:**
  - [derivation] For short sampling times the static-spacetime QI equals the flat-space form times a scale function f(t0), with f → 1 as t0 → 0 (eqs. 46–47, 145).
  - [derivation] The flat form applies when τ0 is small compared with an inverse square root of three terms (eq. 48): a g_tt-gradient term (read from the text layer as ½ g_tt ∇^i∇_i g_tt⁻¹), R/6 and m². Superscript placement in eq. 48 is reconstructed from the text layer. "Typically, this term dominates when the spacetime contains a horizon, and the observer is at rest near the horizon" (Sec. IV).
  - [identity/theorem] Quantum AWEC: the energy density averaged over the entire worldline of a static observer is bounded below by the vacuum energy of the spacetime, for example the Boulware value near a black hole (abstract; eq. 21).
- **Method / verification standard:** exact Euclidean two-point functions for mirrors, Rindler space, static de Sitter and 2D black holes; a Hadamard short-time expansion in general. Analytic.
- **Scope and caveats:** minimally coupled scalar; static spacetimes and static observers only.
- **Disputes, refutations, later corrections:** F00 extends worldline QIs to arbitrary globally hyperbolic spacetimes and trajectories.
- **Relation to active-rail results:** (b)/(d) For static observers the lapse enters the validity scale through g_tt = −α², so gradients and curvature of the lapse shorten the sampling time on which a flat-space QI budget applies. (f) Near a front light surface the g_tt term plays the role of the "distance to the boundary". (g): none.
- **Key quote:** "In a short sampling time limit, the quantum inequality can be written as the flat space form plus subdominant correction terms dependent upon the geometric properties of the spacetime. This supports the use of flat space quantum inequalities to constrain negative energy effects in curved spacetime." (abstract, v1)

### FE98 — C. J. Fewster, S. P. Eveson (1998), "Bounds on negative energy densities in flat spacetime" (abstract-level)
- **Citation:** Phys. Rev. D 58, 084010 (1998); DOI 10.1103/PhysRevD.58.084010. arXiv:gr-qc/9805024v2 (pinned; 8 Jul 1998). Submission history: v1 Thu, 7 May 1998 17:28:57 UTC; v2 Wed, 8 Jul 1998 14:52:49 UTC. Verified via https://arxiv.org/abs/gr-qc/9805024 on 2026-09-26.
- **Design parts and knobs:** the shape of the sampling function (compact support, smooth, even); dimension d; mass m.
- **Knob → physics relations:** [identity/theorem] QIs hold for a class of smooth, even, non-negative sampling functions, compactly supported or rapidly decaying, for the free real scalar of mass m ≥ 0 in d ≥ 2 Minkowski dimensions. In 2D the bound is weaker than Flanagan's optimal bound by a factor 3/2 (abstract).
- **Method / verification standard:** rigorous functional-analytic bounds.
- **Scope and caveats:** free scalar, flat space.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** allows compactly supported sampling windows matched to a finite passage through a rail component. (g): none.
- **Key quote:** "we use a different argument to obtain quantum inequalities for a class of smooth, even and non-negative sampling functions which are either compactly supported or decay rapidly at infinity." (abstract, v2)

### F00 — C. J. Fewster (2000), "A general worldline quantum inequality" (abstract-level)
- **Citation:** Class. Quantum Grav. 17, 1897–1911 (2000); DOI 10.1088/0264-9381/17/9/302. arXiv:gr-qc/9910060v2 (pinned; 21 Feb 2000). Submission history: v1 Mon, 18 Oct 1999 14:32:49 UTC; v2 Mon, 21 Feb 2000 14:43:42 UTC ("The statement of the main result is changed slightly"). Verified via https://arxiv.org/abs/gr-qc/9910060 on 2026-09-26.
- **Design parts and knobs:** an arbitrary smooth timelike trajectory (passenger, Eulerian or static worldlines); the weight function; the Hadamard reference state.
- **Knob → physics relations:** [identity/theorem] A worldline QI on the normal-ordered energy density holds for a real linear scalar on any globally hyperbolic spacetime, for arbitrary smooth timelike trajectories, smooth compactly supported weights and Hadamard states (abstract).
- **Method / verification standard:** microlocal analysis.
- **Scope and caveats:** bounds the normal-ordered density relative to a reference state, and the bound has no closed form in general. K03 notes that such difference-type bounds do not directly give absolute Planck-scale restrictions.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** covers the accelerated (non-geodesic) Eulerian observers of a rail with spatially varying lapse (see SS24 on the geodesic condition). (g): none.
- **Key quote:** "we establish a worldline quantum inequality on the normal ordered energy density, valid for arbitrary smooth timelike trajectories of the observer, arbitrary smooth compactly supported weight functions and arbitrary Hadamard quantum states." (abstract, v2)

### OG03 — Ken D. Olum, Noah Graham (2003), "Static Negative Energies Near a Domain Wall" (abstract-level)
- **Citation:** Phys. Lett. B 554, 175–179 (2003); DOI 10.1016/S0370-2693(03)00011-X; report UCLA/02/TEP/10. arXiv:gr-qc/0205134v3 (pinned; 7 Dec 2002). Submission history: v1 Fri, 31 May 2002 01:18:02 UTC; v2 Mon, 3 Jun 2002 20:53:55 UTC; v3 Sat, 7 Dec 2002 17:25:31 UTC. Verified via https://arxiv.org/abs/gr-qc/0205134 on 2026-09-26.
- **Design parts and knobs:** interacting fields; domain-wall backgrounds; distance from the wall.
- **Knob → physics relations:** [derivation] A domain wall coupled to a scalar produces static negative energy density at certain distances. This violates AWEC and the QIs for interacting fields, with the background energy included self-consistently (abstract).
- **Method / verification standard:** renormalized QFT calculation.
- **Scope and caveats:** a specific interacting model.
- **Disputes, refutations, later corrections:** K03 uses this as evidence that QIs are non-universal. GO07 cites a domain wall as a system where flat-space ANEC still holds.
- **Relation to active-rail results:** limits the reach of free-field QI budgets. Interacting sectors can hold static negative energy, while achronal ANEC remains the global constraint relevant to (g).
- **Key quote:** "This system provides a simple, explicit example of violation of the averaged weak energy condition and the quantum inequalities by interacting quantum fields." (abstract, v3)

### FH05 — Christopher J. Fewster, Stefan Hollands (2005), "Quantum Energy Inequalities in two-dimensional conformal field theory" (abstract-level)
- **Citation:** Rev. Math. Phys. 17, 577 (2005); DOI 10.1142/S0129055X05002406; report ESI Preprint 1559. arXiv:math-ph/0412028v2 (pinned; 29 Apr 2005). Submission history: v1 Thu, 9 Dec 2004 14:38:11 UTC; v2 Fri, 29 Apr 2005 16:42:14 UTC. Verified via https://arxiv.org/abs/math-ph/0412028 on 2026-09-26.
- **Design parts and knobs:** the averaging curve (timelike, null, spacelike) or volume; the central charge.
- **Knob → physics relations:** [identity/theorem] State-independent QEIs for unitary positive-energy 2D CFTs, including null-curve averages, with bounds set by the weight and the central charge (abstract).
- **Method / verification standard:** rigorous, axiomatic.
- **Scope and caveats:** two dimensions only. In 4D, null-segment averages have no lower bound (FR03).
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** 2D reductions of a rail (axis-only light rays) carry null QEIs that the 4D rail lacks, so 1+1 toy models overstate null-segment protection. (g): none.
- **Key quote:** "We give bounds for various situations: averaging along timelike, null and spacelike curves, as well as over a spacetime volume." (abstract, v2)

### ER97 — Allen E. Everett, Thomas A. Roman (1997), "A Superluminal Subway: The Krasnikov Tube"
- **Citation:** Phys. Rev. D 56, 2100 (1997); DOI 10.1103/PhysRevD.56.2100; report TUTP-97-06. arXiv:gr-qc/9702049v1 (read; v1 only). Submission history: v1 Tue, 25 Feb 1997 00:22:54 UTC. Verified via https://arxiv.org/abs/gr-qc/9702049 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9702049v1.
- **Design parts and knobs:** tube length D; tube radius ρmax; wall and end-cap thickness ε; light-cone opening η = 2 − δ; the orientation of tubes in a network; the lateral separation of opposite tubes.
- **Knob → physics relations:**
  - [derivation] One tube produces no CTCs. Two non-overlapping, oppositely directed tubes form a time machine (Sec. 4).
  - [claim] A network avoids CTCs only if "there existed a preferred axis such that all the Krasnikov tubes were oriented so that the velocity components along that axis of objects in superluminal motion were always positive" (Sec. 4).
  - [derivation] Wall energy density T_t̂t̂ ≈ −1/(8πε²) and curvature radius r_c ≈ ε. With the QI, ε ≲ ℓ_P/σ² (eq. 44), i.e. ε ≲ 10⁴ ℓ_P ≈ 10⁻³¹ m for σ ≈ 0.01 (eq. 45). A thick tube needs ρmax ≲ ℓ_P/σ² (eq. 46).
  - [numerical] Band energy E ≈ −α ρmax D/ε (eq. 51). A 1 m × 1 m tube needs about −10¹⁶ galactic masses at α = 0.01 (eq. 52).
  - [derivation] Lead versus wall trade-off: T_tt scales as η/ε². With τ0 = ε ≈ 1 cm the QI holds "only by taking η ≈ ℓ_P² ε²/τ0⁴ ≈ 10⁻⁶⁶", so light inside the tube beats exterior light by about one part in 10⁶⁶ (Sec. 6).
- **Method / verification standard:** analytic stress tensor of the 4D Krasnikov metric; flat-space QI applied at sampling times below r_c.
- **Scope and caveats:** QI applicability in curved space is assumed; the metric is static long after formation. "The t = const slices of the Krasnikov spacetime are not everywhere spacelike" (Sec. 6).
- **Disputes, refutations, later corrections:** K03 disputes the step from the QI to large E_tot.
- **Relation to active-rail results:** (g) *(this inventory, [derivation])* The fractional lead a QI-limited quantum wall can buy scales as η ~ (ℓ_P/ε)². A macroscopic lead requires a non-QI source, which is consistent with the project's conclusion. Chronology: an active-rail network that keeps every rail in one global time orientation meets ER97's stated CTC-avoidance condition (compare SS24, E96). (e) The tube is laid during the outbound trip, inside the launch point's causal future, which matches the project's pre-laid route demand.
- **Key quote:** "We show that, although a single Krasnikov tube does not involve closed timelike curves, a time machine can be constructed with a system of two non-overlapping tubes. Furthermore, it is demonstrated that Krasnikov tubes, like warp bubbles and traversable wormholes, also involve unphysically thin layers of negative energy density, as well as large total negative energies" (abstract, v1)

### K03 — S. Krasnikov (2003), "The quantum inequalities do not forbid spacetime shortcuts"
- **Citation:** Phys. Rev. D 67, 104013 (2003); DOI 10.1103/PhysRevD.67.104013. arXiv:gr-qc/0207057v3 (read; 19 May 2003). Submission history: v1 Mon, 15 Jul 2002 22:25:04 UTC; v2 Fri, 29 Nov 2002 21:25:08 UTC; v3 Mon, 19 May 2003 13:14:26 UTC ("Minor corrections and additions"). Verified via https://arxiv.org/abs/gr-qc/0207057 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/0207057v3.
- **Design parts and knobs:** the ratio of Weyl to Ricci curvature in the exotic region; periodic identifications (Casimir-like lengths L); the thickness of the WEC-violating layer relative to the Planck length; construction time.
- **Knob → physics relations:**
  - [identity/theorem] Definition: M is a *shortcut* if it is globally hyperbolic and is Minkowski space with a cylinder C replaced, such that some pair of points spacelike-separated in L⁴ becomes causally connected in M (Sec. I).
  - [derivation] The QI-to-Planck-density chain uses ℓ⁻⁴ ~ ρ², which "one expects … to be true only when max|C_αβγδ|/max|R_αβ| ≲ 1, … a condition that breaks down more often than not" (Sec. III.A). Weyl-dominated designs escape the inferred Planck-scale ρ.
  - [derivation] A wormhole built from two cylinders identified with time shift T has a section that is a cylinder of length L = (X² − T²)^(1/2). The QI condition Δ ≲ L can then be met for any ρ by making L small, while the throat and mouth separation stay macroscopic (Sec. III.A).
  - [claim] When the WEC-violating layers are thinner than the Planck length, semiclassical E_tot is meaningless (Sec. III.B).
  - [claim] Construction time: "If a Da = 100 light years, then a shortcut that would allow one to reach the star in 1 yr, cannot be built in less than 99 yr" (Sec. I, citing Krasnikov 1998).
- **Method / verification standard:** explicit counterexamples to the steps of the QI argument. Analytic.
- **Scope and caveats:** addresses only the QI route; the ANEC and achronal-ANEC routes lie outside the paper.
- **Disputes, refutations, later corrections:** contests FR96, ER97 and Pfenning–Ford 1997. The K03 definition of a shortcut matches the premise of project claim (g).
- **Relation to active-rail results:** (g) K03's shortcut is the project's "lead over exterior light". K03 undercuts only QI-magnitude arguments, while (g) rests on achronal ANEC, which K03 leaves standing. (a)/(b) Weyl-dominated lapse structures fall in the regime where local QIs give weak magnitude limits. (e) The construction-time remark matches the project's rule that demand extends along the route ahead of use.
- **Key quote:** "By explicit examples I prove that: 1) the relevant quantum inequality does not (always) imply large energy densities; 2) large densities may not lead to large values of E_tot; 3) large E_tot, being physically meaningless in some relevant situations, does not necessarily exclude shortcuts." (abstract, v3)

---

## B. Superluminal travel, time delay and speed-limit theorems

### O98 — Ken D. Olum (1998), "Superluminal travel requires negative energies"
- **Citation:** Phys. Rev. Lett. 81, 3567–3570 (1998); DOI 10.1103/PhysRevLett.81.3567. arXiv:gr-qc/9805003v2 (read; 14 Oct 1998). Submission history: v1 Fri, 1 May 1998 19:39:39 UTC; v2 Wed, 14 Oct 1998 18:55:32 UTC (merges gr-qc/9806091). Verified via https://arxiv.org/abs/gr-qc/9805003 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9805003v2.
- **Design parts and knobs:** the fastest path P from origin A to destination B; flat 2-surfaces Σ_A and Σ_B made of spacelike geodesics; shear and tidal content along P (the generic condition).
- **Knob → physics relations:**
  - [identity/theorem] Condition 1: P is superluminal only if q ∈ J⁺(p) for p ∈ Σ_A, q ∈ Σ_B holds only for (p, q) = (A, B). Then P is a null geodesic normal to both surfaces. If the generic condition holds on P, the WEC is violated at some point of P.
  - [derivation] *(this inventory, from eqs. 3–8)* The proof starts from θ̂ = 0 at A and requires θ̂ ≥ 0 at B with vanishing vorticity. Integrating Raychaudhuri gives ∫_A^B R_ab K^a K^b dv ≤ −∫_A^B (2σ̂² + θ̂²/2) dv ≤ 0. The fastest segment therefore needs negative integrated null curvature (negative null energy), and shear along the fastest ray raises the demand.
  - [derivation] The theorem forbids the existence of superluminal travel, and "the WEC violation must occur along the path to be traveled" (text after eq. 8).
  - [derivation] For a flat-exterior modification of Minkowski space, identifying boundaries converts P into a closed causal curve, and Tipler–Hawking theorems then force WEC violation (Fig. 2 argument).
  - [derivation] Casimir plates satisfy Condition 1: negative T_zz defocuses the congruence (eqs. 9–11).
- **Method / verification standard:** a global-causal-structure proof with a Raychaudhuri argument; peer-reviewed.
- **Scope and caveats:** the definition is local ("earlier than any neighboring path"). "It is possible that while P arrives earlier than any nearby path, it is still slower than a path some larger distance away." The generic condition is required.
- **Disputes, refutations, later corrections:** SS24 (Sec. 4.2) argues that the definition misses warp drives with Riemann-flat passenger regions, where the generic condition fails and neighbouring paths are equally fast. K03 notes that a weak minimum of arrival time fails the definition. GO07 (Sec. IV.D) shows that achronal ANEC alone does not forbid Condition-1 superluminality, because the Casimir example satisfies it.
- **Relation to active-rail results:** (g) O98 establishes negative null energy on a *finite* segment of the fastest ray. This is a segment statement, weaker than negative ANEC on a complete ray. The project's axis ray, which rides the cone tip, is the O98 path P. The derived shear inequality ties passenger tidal comfort (low shear on the fastest ray) to a smaller null-energy demand. (a) The theorem constrains null energy, so it applies whether the negative energy sits in shift shear or in lapse curvature (compare the project's T(k,k) = α_rr/(4πα) on the axis).
- **Key quote:** "I propose a definition of superluminal travel which requires that the path to be traveled reach a destination surface at an earlier time than any neighboring path. With this definition (and assuming the generic condition) I prove that superluminal travel requires weak-energy-condition violation." (abstract, v2)

### VBL98 — Matt Visser, Bruce Bassett, Stefano Liberati (2000), "Superluminal censorship"
- **Citation:** Nucl. Phys. Proc. Suppl. 88, 267–270 (2000); DOI 10.1016/S0920-5632(00)00782-9. arXiv:gr-qc/9810026v2 (read; 15 Dec 1999); v1 also read, for the record of the withdrawn claim. Submission history: v1 Wed, 7 Oct 1998 23:24:13 UTC; v2 Wed, 15 Dec 1999 19:54:38 UTC. v2 comment: "Significant revisions: (1) the perturbative analysis is extended; (2) the non-perturbative analysis in terms of null infinity is abandoned". Verified via https://arxiv.org/abs/gr-qc/9810026 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9810026v2 and https://arxiv.org/pdf/gr-qc/9810026v1.
- **Design parts and knobs:** a weak field h_μν around Minkowski space; the retarded source distribution; the gauge choice (Hilbert–Lorentz); the absence of incoming gravitational radiation.
- **Knob → physics relations:**
  - [derivation] In Hilbert–Lorentz gauge, h_μν k^μ k^ν = 16πG ∫d³y T_μν(y, t̃) k^μ k^ν/|x − y| over the retarded past cone (eqs. 8–10). If the NEC holds throughout the source, then g_μν k^μ k^ν > 0 for every Minkowski-null k: the light cones narrow everywhere and the Shapiro effect is always a delay.
  - [derivation] Any light-cone opening, anywhere, requires NEC violation somewhere on the retarded past cone of that point, weighted by 1/|x − y|.
  - [claim] v1 (withdrawn): in asymptotically flat spacetimes, a null curve from I⁻ that reaches I⁺ before the Minkowski geodesic implies a fastest null geodesic without conjugate points, hence ANEC violation ("Superluminal travel requires violations of the averaged null energy condition (ANEC)", v1 abstract). v2 abandons this and states "we do not yet have a fully convincing argument that applies in a non-perturbative setting" (v2, Sec. 4).
- **Method / verification standard:** linearized gravity with gravitational Liénard–Wiechert potentials.
- **Scope and caveats:** weak fields; global Hilbert–Lorentz gauge; asymptotic flatness; no incoming radiation.
- **Disputes, refutations, later corrections:** GW00 shows the perturbative light-cone comparison is gauge dependent: "we can reverse the conclusions of [3] in any compact region of spacetime" (GW00, Sec. 1). The authors abandoned the non-perturbative theorem (v2).
- **Relation to active-rail results:** (g) v1 of this paper claimed exactly the project's statement (a lead over the Minkowski arrival ⇒ ANEC violation on a fastest null geodesic), and the authors withdrew that claim. The logical content is recovered in GW00 (Galloway's footnote) combined with GO07 Lemma 1; see the assessment at the end. (d) A lapse contrast that widens coordinate light cones is, in weak field and this gauge, an NEC-violating source.
- **Key quote:** "Given the NEC, the Shapiro time delay in any weak gravitational field is always a delay relative to the Minkowski background, and never an advance." (abstract, v2)

### VBL99 — Matt Visser, Bruce Bassett, Stefano Liberati (1999), "Perturbative superluminal censorship and the null energy condition"
- **Citation:** AIP Conf. Proc. 493, 301–305 (1999); DOI 10.1063/1.1301601. arXiv:gr-qc/9908023v1 (read; v1 only). Submission history: v1 Fri, 6 Aug 1999 22:58:15 UTC. Verified via https://arxiv.org/abs/gr-qc/9908023 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9908023v1.
- **Design parts and knobs:** as VBL98, plus voids in FRW backgrounds.
- **Knob → physics relations:** [derivation] Same linearized light-cone narrowing under the NEC. Voids relative to FRW can give a Shapiro advance without NEC violation, because the comparison background is FRW (Sec. "Strong field gravity").
- **Method / verification standard:** proceedings summary of VBL98.
- **Scope and caveats:** weak field. The text refers to "a non-perturbative theorem regarding superluminal censorship" in [1] = gr-qc/9810026, whose v2 later abandoned it.
- **Disputes, refutations, later corrections:** as VBL98.
- **Relation to active-rail results:** (g) the "lead" is always measured against a chosen background. The project's comparison is exterior light in the flat exterior, which is the well-defined case (compare GW00 on Olum's world-tube setting).
- **Key quote:** "Furthermore, any object travelling within the lightcones of the weak gravitational field is similarly delayed with respect to the minimum traversal time possible in the background Minkowski geometry." (abstract, v1)

### L99 — Robert J. Low (1999), "Speed Limits in General Relativity"
- **Citation:** Class. Quantum Grav. 16, 543–549 (1999); DOI 10.1088/0264-9381/16/2/016. arXiv:gr-qc/9812067v1 (read; v1 only). Submission history: v1 Fri, 18 Dec 1998 14:06:01 UTC. Verified via https://arxiv.org/abs/gr-qc/9812067 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9812067v1.
- **Design parts and knobs:** the decision event p; the region K = J⁺(p) ∩ Σ where initial data may change; the destination worldline L; the matter's hyperbolicity and energy condition.
- **Knob → physics relations:**
  - [identity/theorem] With symmetric hyperbolic matter whose ray cones lie inside the light cones, D(Σ∖K) is isometric between the original and altered developments (Corollary 4.1). A decision at p therefore cannot let anyone reach an earlier point on L than the boundary of D⁺(Σ∖K) allows.
  - [identity/theorem] Theorem 4.2: "In the absence of exotic matter, it is impossible to construct a warpdrive", where exotic means non-hyperbolic or DEC-violating (Definition 2.3).
  - [claim] Travel with less elapsed proper time, and short return trips in Krasnikov's sense, remain possible (Sec. 4).
- **Method / verification standard:** Cauchy-problem uniqueness and domain-of-dependence arguments.
- **Scope and caveats:** the energy condition used is the DEC, stronger than the NEC; the conclusion is about *construction on demand*.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (e) A front apex moving at v > 1 is compatible with L99 only when the rail's demand is laid along the route inside the causal future of the preparation events. The condition sin θ < 1/v makes the lateral front surface's normal speed v sin θ subluminal *(this inventory, [derivation])*, so the surface is timelike. The apex's motion is then a scheduled intersection, not a propagating signal. This matches the project rule that choreography uses planned timing and local evolution. (g): none.
- **Key quote:** "These results are applied first to show that in a well defined sense, finite perturbations in the gravitational field travel no faster than light, and second to show that it is impossible to construct a warp drive as considered by Alcubierre (1994) in the absence of exotic matter." (abstract, v1)

### GW00 — Sijie Gao, Robert M. Wald (2000), "Theorems on gravitational time delay and related issues"
- **Citation:** Class. Quantum Grav. 17, 4999–5008 (2000); DOI 10.1088/0264-9381/17/24/305. arXiv:gr-qc/0007021v2 (read; 28 Jul 2000). Submission history: v1 Tue, 11 Jul 2000 15:12:16 UTC; v2 Fri, 28 Jul 2000 22:10:54 UTC ("Example of gauge perturbation changed/corrected. Two footnotes added and one footnote removed"). Verified via https://arxiv.org/abs/gr-qc/0007021 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/0007021v2.
- **Design parts and knobs:** a compact region K holding the modification; the endpoint pair (p, q) outside a larger compact set K′; fastest null geodesics (q ∈ J⁺(p) ∖ I⁺(p)); null completeness; the NEC; the null generic condition; the existence of null lines.
- **Knob → physics relations:**
  - [identity/theorem] Theorem 1: in a null-geodesically complete spacetime with the NEC and the null generic condition, for every compact K there is a compact K′ ⊇ K such that no causal curve from p to q with q ∈ J⁺(p) ∖ I⁺(p) and p, q ∉ K′ meets K.
  - [identity/theorem] Footnote 1 (Galloway): the conclusion holds whenever the spacetime contains no null line (inextendible achronal null geodesic). When the conclusion fails, the proof constructs a null line.
  - [derivation] Theorem 2: in asymptotically AdS-type spacetimes with a timelike conformal boundary, fastest boundary-to-boundary null geodesics lie in the boundary, so generic perturbations give a time delay.
  - [claim] A spacetime Minkowskian outside a world tube with the DEC has zero ADM mass and therefore contradicts the positive mass theorem unless flat (Sec. 1).
  - [derivation] VBL's perturbative result is gauge dependent: a pure-gauge h_ab opens light cones everywhere (eqs. 6–8).
- **Method / verification standard:** conjugate-point continuity (Lemma 1) and global causal structure.
- **Scope and caveats:** "the theorem gives little control over the size of the region K′". Theorem 1 speaks about sufficiently distant endpoints.
- **Disputes, refutations, later corrections:** corrects the gauge example in v2; critiques VBL98.
- **Relation to active-rail results:** (g) *(this inventory, [derivation])* Suppose a compact rail with a flat exterior delivers a lead L > 0 from departure event D to arrival event A. Take p_n on the route line a distance n behind D, at the time its light reaches D, and q_n a distance n beyond A. Then q_n ∈ J⁺(p_n) through the rail, while exterior light from p_n arrives L later. The fastest p_n → q_n curves enter K for every n, so Theorem 1's conclusion fails and Galloway's footnote supplies a null line. A lead over exterior light usable by arbitrarily distant endpoints therefore implies a null line. Combined with GO07 Lemma 1 (generic condition), that null line violates ANEC. This is the rigorous route to the project's statement (g); it needs null completeness and the generic condition. The DEC remark implies that exterior-flat rail components need DEC violation, consistent with (a).
- **Key quote:** "G. Galloway (private communication) has pointed out to us that the conclusions of Theorem 1 remain valid if the hypothesis of Theorem 1 is replaced by the condition that (M, g_ab) fails to contain a null line." (footnote 1, v2)

### PSW93 — R. Penrose, R. D. Sorkin, E. Woolgar (1993), "A Positive Mass Theorem Based on the Focusing and Retardation of Null Geodesics"
- **Citation:** no journal reference or DOI on arXiv. arXiv:gr-qc/9301015v2 (read; 15 Jan 1993). Submission history: v1 Thu, 14 Jan 1993 20:00:57 UTC (withdrawn); v2 Fri, 15 Jan 1993 21:00:19 UTC. Verified via https://arxiv.org/abs/gr-qc/9301015 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/9301015v2.
- **Design parts and knobs:** ADM mass; conjugate points on null geodesics in the domain of outer communication D; asymptotic flatness; global hyperbolicity of D ∪ I.
- **Knob → physics relations:**
  - [identity/theorem] If every infinite null geodesic in D has a pair of conjugate points, and D ∪ I is globally hyperbolic, the 4-momentum is future-causal (Theorem II.1.1). "This condition can be weakened to one pertaining only to achronal null geodesics."
  - [derivation] Negative total mass advances null geodesics, while positive energy focuses and retards them (abstract).
- **Method / verification standard:** global causal-structure proof.
- **Scope and caveats:** asymptotically flat; one asymptotic region.
- **Disputes, refutations, later corrections:** none visible. GO07 and W10 carry it over to achronal ANEC.
- **Relation to active-rail results:** (g) A lead over exterior light is a time advance of the PSW kind. Under achronal ANEC plus genericity, a rail assembly with ADM mass ≥ 0 cannot produce an asymptotic advance through focusing alone. (a) An exterior-flat rail has zero ADM mass and therefore sits at the boundary of this theorem.
- **Key quote:** "the basic idea being that positive energy-density focuses null geodesics, and correspondingly retards them, whereas a negative total mass would advance them." (abstract, v2)

### FSW93 — John L. Friedman, Kristin Schleich, Donald M. Witt (1993), "Topological Censorship" (abstract-level)
- **Citation:** Phys. Rev. Lett. 71, 1486–1489 (1993); Erratum 75, 1872 (1995); DOI 10.1103/PhysRevLett.75.1872 (as shown on arXiv). arXiv:gr-qc/9305017v2 (pinned; 9 Jun 1995). Submission history: v1 Sun, 23 May 1993 21:09:00 UTC (withdrawn); v2 Fri, 9 Jun 1995 05:21:58 UTC. Verified via https://arxiv.org/abs/gr-qc/9305017 on 2026-09-26.
- **Design parts and knobs:** spatial topology; causal curves from I⁻ to I⁺; the energy condition.
- **Knob → physics relations:** [identity/theorem] In a globally hyperbolic, asymptotically flat spacetime with the NEC, every causal curve from I⁻ to I⁺ is homotopic to a topologically trivial one (abstract). GO07 replaces the NEC with self-consistent achronal ANEC for simply connected spacetimes.
- **Method / verification standard:** global analysis.
- **Scope and caveats:** the arXiv comment records that the secondary "passive topological censorship" result in the PRL version is false, while the main theorem is unaffected.
- **Disputes, refutations, later corrections:** erratum (PRL 75, 1872).
- **Relation to active-rail results:** the C1 multicomponent rail keeps trivial topology, so topological censorship leaves it alone, and (g) rests on the time-advance route (GW00, PSW93).
- **Key quote:** "any topological structure collapses too quickly to allow light to traverse it." (abstract, v2)

---

## C. ANEC, achronal ANEC and their proofs

### GO07 — Noah Graham, Ken D. Olum (2007), "Achronal averaged null energy condition"
- **Citation:** Phys. Rev. D 76, 064001 (2007); DOI 10.1103/PhysRevD.76.064001. arXiv:0705.3193v2 (read; 27 Aug 2007). Submission history: v1 Tue, 22 May 2007 15:24:36 UTC; v2 Mon, 27 Aug 2007 18:54:45 UTC ("qualify conditions on theorem 1, fix typos"). Verified via https://arxiv.org/abs/0705.3193 on 2026-09-26; full text https://arxiv.org/pdf/0705.3193v2.
- **Design parts and knobs:** the achronality of complete null geodesics; self-consistency of the semiclassical solution; the null generic condition; asymptotic flatness; simple connectedness; curvature relative to the Planck scale.
- **Knob → physics relations:**
  - [claim] Condition 1 (self-consistent achronal ANEC): "There is no self-consistent solution in semiclassical gravity in which ANEC is violated on a complete, achronal null geodesic." It is stated as a conjecture ("We conjecture that all semiclassical systems obey self-consistent achronal ANEC.").
  - [identity/theorem] Lemma 1: in a generic spacetime obeying Condition 1 there are no complete achronal null geodesics, because an ANEC-obeying complete null geodesic under the generic condition has conjugate points (Borde).
  - [identity/theorem] Condition 1 plus genericity rules out simply connected topological-censorship violations (Theorem 1), Tipler-type time machines (Theorem 2) and compactly generated Cauchy horizons (Theorem 3), and yields positive mass through PSW (Sec. IV.C).
  - [derivation] Olum-type superluminality needs ANEC only on achronal *partial* geodesics, and that "half achronal ANEC" fails in flat space. Example: T_ab k^a k^b = −1/(16π² z⁴) near a Dirichlet plane (Sec. IV.D).
  - [claim] Anomalous (Visser) rescaling violations leave the semiclassical self-consistent regime (Sec. III).
- **Method / verification standard:** proofs of the theorems from Condition 1; a survey of known violations (all on chronal geodesics or outside the self-consistent regime).
- **Scope and caveats:** "Condition 1 should be expected to hold only in cases where the curvature is well below the Planck scale". Theorem 1 needs simple connectedness. The null generic condition is assumed throughout.
- **Disputes, refutations, later corrections:** UO10 violates the non-self-consistent version. W10 proves a perturbative version. KS20 (Sec. 5) states that the theorem "also prohibits warp drive spacetimes" via O98, while GO07 itself says superluminal communication needs additional constraints (see Open disputes).
- **Relation to active-rail results:** (g) GO07 supplies the self-consistent condition the project cites and Lemma 1, the step from "null line" to "negative ANEC". GO07 also states that achronal ANEC alone does not exclude *local* (Olum) superluminality. The project's "any lead over light" holds as a *global* lead statement, one that produces a complete achronal geodesic through GW00/Galloway. It fails as a local one. The "at any size" wording exceeds GO07's scope, which stops at Planck-scale curvature. Condition 1 is a conjecture; the proven cases are W10 and KO15.
- **Key quote:** "So, as with singularity theorems, self-consistent achronal ANEC is an adequate substitute for ordinary ANEC, but additional constraints are necessary to rule out superluminal communication." (Sec. IV.D, v2)

### W10 — Aron C. Wall (2010), "Proving the Achronal Averaged Null Energy Condition from the Generalized Second Law"
- **Citation:** Phys. Rev. D 81, 024038 (2010); DOI 10.1103/PhysRevD.81.024038. arXiv:0910.5751v2 (read; 16 Feb 2010). Submission history: v1 Thu, 29 Oct 2009 23:43:08 UTC; v2 Tue, 16 Feb 2010 01:57:35 UTC ("Added 2 paragraphs to end of section 2"). Verified via https://arxiv.org/abs/0910.5751 on 2026-09-26; full text https://arxiv.org/pdf/0910.5751v2.
- **Design parts and knobs:** a null line N in a classical NEC-obeying background; perturbation order in ħ; minimal coupling; quantization of gravitons (shear).
- **Knob → physics relations:**
  - [identity/theorem] If the GSL holds on causal horizons (plus CPT or the anti-GSL, and a suitable renormalization of generalized entropy), then quantum fields minimally coupled to semiclassical Einstein gravity satisfy ANEC on null lines at first order in ħ (Secs. 4–5).
  - [derivation] The background obeys the Einstein equation with classical matter satisfying the NEC (eq. 6). Galloway's null splitting theorem places N on an achronal horizon with θ = σ = 0.
  - [claim] Once gravitons are quantized, the renormalized σ_ab σ^ab can be negative and the ANEC-based theorems fail. A shear-inclusive ANEC is proposed and proven under an extra horizon assumption (Sec. 7).
  - [derivation] In pp-wave (including Minkowski) backgrounds, a separation of past and future horizons would violate O98's and VBL's no-superluminal-communication results (Sec. 7).
- **Method / verification standard:** GSL plus perturbation theory in ħ, with an argument about renormalization.
- **Scope and caveats:** "The present result is weaker insofar as it is restricted to the case in which the gravitational perturbation to the background metric is small". It covers minimal coupling only and assumes a version of cosmic censorship (Sec. 3, footnote 6).
- **Disputes, refutations, later corrections:** none visible on the core result. The graviton-shear caveat is the author's own.
- **Relation to active-rail results:** (g) W10 proves the project's statement *perturbatively*: quantum fields that perturb an NEC-obeying background cannot create a lead. A quantum sector that supplies an O(1) geometry change, which is what "supplies … this demand at any size" would require, lies outside W10.
- **Key quote:** "It is proven that for any quantum fields minimally coupled to semiclassical Einstein gravity, the averaged null energy condition (ANEC) on null lines is a consequence of the generalized second law of thermodynamics for causal horizons." (abstract, v2)

### UO10 — Douglas Urban, Ken D. Olum (2010), "Averaged null energy condition violation in a conformally flat spacetime"
- **Citation:** Phys. Rev. D 81, 024039 (2010); DOI 10.1103/PhysRevD.81.024039. arXiv:0910.5925v2 (read; 28 Jan 2010). Submission history: v1 Fri, 30 Oct 2009 19:59:16 UTC; v2 Thu, 28 Jan 2010 05:24:05 UTC. Verified via https://arxiv.org/abs/0910.5925 on 2026-09-26; full text https://arxiv.org/pdf/0910.5925v2.
- **Design parts and knobs:** the conformal factor, in particular the width r of the deviation from flatness; the quantum state; conformal coupling; transverse averaging.
- **Knob → physics relations:**
  - [derivation] A conformal map that enhances the NEC-violating parts of a Minkowski state violates ANEC by an arbitrary amount on achronal geodesics of a conformally and asymptotically flat spacetime (Secs. II, V).
  - [derivation] An anomaly-driven violation exists even in the vacuum and "grows as r → 0" (Sec. V).
  - [claim] Transverse averaging over distances greater than r, or imposing self-consistency, could remove both violations (Sec. V).
- **Method / verification standard:** explicit test-field calculation.
- **Scope and caveats:** the background is fixed and is not a solution sourced by the field ("we have computed the stress tensor in a given background without attempting to impose self-consistency").
- **Disputes, refutations, later corrections:** consistent with GO07's self-consistent formulation; KS20 notes that all such violations are test-field ones.
- **Relation to active-rail results:** (g) Test-field achronal ANEC fails in curved spacetime. The project's phrase "holds in curved space" is correct only for the self-consistent (GO07) or perturbative (W10, KO15) versions. Design knob: sharply localized conformal (lapse-like) structure of width r drives anomaly-induced negative ANEC.
- **Key quote:** "Since all geodesics in conformally flat spacetimes are achronal, the achronal averaged null energy condition is likewise violated." (abstract, v2)

### FOP07 — Christopher J. Fewster, Ken D. Olum, Michael J. Pfenning (2007), "Averaged null energy condition in spacetimes with boundaries" (abstract-level)
- **Citation:** Phys. Rev. D 75, 025007 (2007); DOI 10.1103/PhysRevD.75.025007. arXiv:gr-qc/0609007v3 (pinned; 10 Sep 2007). Submission history: v1 Fri, 1 Sep 2006 15:52:23 UTC; v2 Mon, 11 Dec 2006 18:45:21 UTC; v3 Mon, 10 Sep 2007 19:29:46 UTC. Verified via https://arxiv.org/abs/gr-qc/0609007 on 2026-09-26.
- **Design parts and knobs:** a flat tubular neighbourhood around the geodesic; exterior curvature or boundaries that leave the tube's causal structure intact.
- **Knob → physics relations:** [identity/theorem] A free minimally coupled scalar cannot violate ANEC on a complete null geodesic inside a flat tube whose intrinsic causal structure matches that induced from the full spacetime. This includes Casimir boundaries a finite distance away (abstract).
- **Method / verification standard:** null limit of a worldline QI.
- **Scope and caveats:** free scalar; flat tube.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (g) The causal-structure condition is the achronality condition in disguise. A rail ray whose neighbourhood is flat but whose exterior provides a lead would violate the causal-structure hypothesis, which is where (g) bites.
- **Key quote:** "the ANEC holds in flat space with boundaries, as in the Casimir effect, for geodesics which stay a finite distance away from the boundary" (abstract, v3)

### GO05 — Noah Graham, Ken D. Olum (2005), "Plate with a hole obeys the averaged null energy condition" (abstract-level)
- **Citation:** Phys. Rev. D 72, 025013 (2005); DOI 10.1103/PhysRevD.72.025013. arXiv:hep-th/0506136v2 (pinned; 7 Nov 2005). Submission history: v1 Thu, 16 Jun 2005 18:07:15 UTC; v2 Mon, 7 Nov 2005 15:17:36 UTC. Verified via https://arxiv.org/abs/hep-th/0506136 on 2026-09-26.
- **Design parts and knobs:** hole radius; boundary condition (Dirichlet or Neumann).
- **Knob → physics relations:** [derivation] For Dirichlet plates, the positive correction from the hole overwhelms the plate's negative contribution; for Neumann plates, ANEC is also obeyed (abstract).
- **Method / verification standard:** scattering theory in spheroidal coordinates.
- **Scope and caveats:** idealized boundaries.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (g) O98's Casimir time advance is local. The complete ray through the Casimir system still obeys ANEC, which shows how local advances fail to add up to a global lead.
- **Key quote:** "This system thus provides another example of a situation where ANEC turns out to be obeyed when one might expect it to be violated." (abstract, v2)

### KO13 — Eleni-Alexandra Kontou, Ken D. Olum (2013), "Averaged null energy condition in a classical curved background" (abstract-level)
- **Citation:** Phys. Rev. D 87, 064009 (2013) (Crossref); DOI 10.1103/PhysRevD.87.064009. arXiv:1212.2290v1 (pinned; v1 only). Submission history: v1 Tue, 11 Dec 2012 03:30:34 UTC. Verified via https://arxiv.org/abs/1212.2290 on 2026-09-26.
- **Design parts and knobs:** a classical source for the curvature around the geodesic; tubular neighbourhood.
- **Knob → physics relations:** [derivation] Assuming a curved-space QI conjecture, ANEC holds for a free minimally coupled scalar on achronal geodesics whose surrounding curvature comes from a classical source (abstract). KO15 removes the conjecture.
- **Method / verification standard:** conditional proof.
- **Scope and caveats:** conditional on the conjectured QI.
- **Disputes, refutations, later corrections:** superseded by KO15.
- **Relation to active-rail results:** see KO15.
- **Key quote:** "Exotic spacetimes, such as those allow wormholes or the construction of time machines are possible in general relativity only if ANEC is violated along achronal geodesics." (abstract, v1)

### KO15 — Eleni-Alexandra Kontou, Ken D. Olum (2015), "Proof of the averaged null energy condition in a classical curved spacetime using a null-projected quantum inequality"
- **Citation:** Phys. Rev. D 92, 124009 (2015); DOI 10.1103/PhysRevD.92.124009. arXiv:1507.00297v2 (read; 27 Oct 2015). Submission history: v1 Wed, 1 Jul 2015 17:45:19 UTC; v2 Tue, 27 Oct 2015 02:27:20 UTC ("references added"). Verified via https://arxiv.org/abs/1507.00297 on 2026-09-26; full text https://arxiv.org/pdf/1507.00297v2.
- **Design parts and knobs:** the null convergence condition of the background in a tubular neighbourhood M′; bounded curvature and its derivatives; minimal coupling; uniformity of the ANEC integral across the neighbourhood.
- **Knob → physics relations:**
  - [identity/theorem] Theorem 1: for an achronal null geodesic γ with a tubular neighbourhood of bounded curvature obeying the null convergence condition, and causal structure unaffected by the exterior, the ANEC integral of a minimally coupled scalar in a Hadamard state "cannot converge uniformly to negative values on all geodesics Γ(λ) in M′" (Sec. II.B).
  - [derivation] The null-projected QI used equals Fewster–Roman's flat form plus corrections that vanish in the highly boosted short-time limit (Sec. VIII).
  - [claim] "Thus we have shown that no spacetime that obeys NEC can be perturbed by a minimally-coupled quantum scalar field into one which violates achronal ANEC. Thus no such perturbation of a classical spacetime would allow wormholes, superluminal travel, or construction of time machines" (Sec. VIII).
  - [claim] Open: a quantum field that "generates enough NEC violation to permit itself to violate ANEC", or a three-step chain in which an ANEC-obeying NEC violator sources a background for an ANEC violator (Sec. VIII).
- **Method / verification standard:** the Fewster–Smith general QI, first order in curvature. Rigorous within its assumptions.
- **Scope and caveats:** massless minimally coupled free scalar; first order in the Riemann tensor; a background obeying the null convergence condition. The curvature bounds R_max are finite "but not necessarily small". The conclusion is transverse-uniform.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (g) Supports the project for perturbations of NEC-obeying backgrounds. It leaves open exactly the regime of a large quantum-supplied violation, which KO15 lists as an open possibility. The project's summary "free fields at small curvature" matches the first-order-in-curvature scope. KO15's conclusion forbids *uniform* negative ANEC across a tube, so the project should test the transversely displaced family of parallel rays, not only the angular fan from one event.
- **Key quote:** "We then use this inequality to prove ANEC on achronal geodesics in a curved background that obeys the null convergence condition." (abstract, v2)

### FLPW16 — Thomas Faulkner, Robert G. Leigh, Onkar Parrikar, Huajia Wang (2016), "Modular Hamiltonians for Deformed Half-Spaces and the Averaged Null Energy Condition" (abstract-level)
- **Citation:** JHEP 09 (2016) 038 (Crossref); DOI 10.1007/JHEP09(2016)038. arXiv:1605.08072v1 (pinned; v1 only). Submission history: v1 Wed, 25 May 2016 21:02:28 UTC. Verified via https://arxiv.org/abs/1605.08072 on 2026-09-26.
- **Design parts and knobs:** none on the geometry side; this is flat-space QFT.
- **Knob → physics relations:** [identity/theorem] Shape deformations of the half-space modular Hamiltonian bring in ∫T_uu along the Rindler horizon, and relative-entropy monotonicity then proves ANEC in Minkowski space (abstract).
- **Method / verification standard:** modular theory with perturbative entanglement methods.
- **Scope and caveats:** Minkowski space without gravity; relativistic QFTs.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (g) supports the flat-space leg of the project's citation chain. It contains no curved or self-consistent statement.
- **Key quote:** "We use this fact along with monotonicity of relative entropy to prove the averaged null energy condition in Minkowski space-time." (abstract, v1)

### HKT17 — Thomas Hartman, Sandipan Kundu, Amirhossein Tajdini (2017), "Averaged Null Energy Condition from Causality" (abstract-level)
- **Citation:** JHEP 07 (2017) 066 (Crossref); DOI 10.1007/JHEP07(2017)066. arXiv:1610.05308v1 (pinned; v1 only). Submission history: v1 Mon, 17 Oct 2016 20:00:02 UTC. Verified via https://arxiv.org/abs/1610.05308 on 2026-09-26.
- **Design parts and knobs:** none on the geometry side.
- **Knob → physics relations:** [identity/theorem] Microcausality in unitary, Lorentz-invariant interacting QFTs in d > 2 implies ∫du T_uu ≥ 0, with higher-spin analogues (abstract).
- **Method / verification standard:** lightcone OPE sum rule.
- **Scope and caveats:** flat spacetime; interacting theories in more than two dimensions.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (g) as FLPW16.
- **Key quote:** "For interacting theories in more than two dimensions, we show that this implies that the averaged null energy, ∫du T_uu, must be positive." (abstract, v1)

### R20 — Felipe Rosso (2020), "Achronal averaged null energy condition for extremal horizons and (A)dS" (abstract-level)
- **Citation:** JHEP 07 (2020) 023; DOI 10.1007/JHEP07(2020)023. arXiv:2005.06476v3 (pinned; 23 Dec 2020). Submission history: v1 Wed, 13 May 2020 18:00:01 UTC; v2 Wed, 12 Aug 2020 17:24:37 UTC; v3 Wed, 23 Dec 2020 22:32:31 UTC. Verified via https://arxiv.org/abs/2005.06476 on 2026-09-26.
- **Design parts and knobs:** background symmetry (AdS₂ × S^(d−2), dS, AdS).
- **Knob → physics relations:** [identity/theorem] Achronal ANEC holds for general QFTs on these backgrounds, proven by relative entropy (abstract).
- **Method / verification standard:** modular Hamiltonians of null-deformed regions.
- **Scope and caveats:** highly symmetric fixed backgrounds.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** extends the curved-space evidence base for (g) to symmetric backgrounds, a class the rail geometry lies outside.
- **Key quote:** "We prove the achronal averaged null energy condition for general quantum field theories in the near horizon geometry of spherical extremal black holes (i.e. AdS₂×S^{d−2}), de Sitter and anti-de Sitter." (abstract, v3)

### KS20 — Eleni-Alexandra Kontou, Ko Sanders (2020), "Energy conditions in general relativity and quantum field theory"
- **Citation:** Class. Quantum Grav. 37 (19), 193001 (2020) (Crossref); DOI 10.1088/1361-6382/ab8fcf. arXiv:2003.01815v2 (read; 5 Jun 2020). Submission history: v1 Tue, 3 Mar 2020 22:30:02 UTC; v2 Fri, 5 Jun 2020 02:22:16 UTC. Verified via https://arxiv.org/abs/2003.01815 on 2026-09-26; full text https://arxiv.org/pdf/2003.01815v2 (Secs. 4.3 and 5 read).
- **Design parts and knobs:** the transverse extent of any ANEC violation; self-consistency; asymptotic flatness; compact generation of Cauchy horizons.
- **Knob → physics relations:**
  - [claim] Formulation (ii): "On-shell configurations can violate the AANEC only over Planck scale distances in directions transversal to the null geodesic" (Sec. 4.3).
  - [claim] AANEC "has the best chance of being valid under all physically reasonable circumstances … and it has no known physically reasonable counter-examples" (Sec. 4.3). Known violations involve Planck lengths or are test-field only.
  - [identity/theorem] Restates GO07 (Theorem 5.9): no compactly generated Cauchy horizon under on-shell AANEC and genericity.
  - [claim] "By Olum's earlier proof [180], this theorem also prohibits warp drive spacetimes." (Sec. 5)
  - [numerical] Quoted secondary figures: Krasnikov-tube walls of a few thousand Planck lengths; Alcubierre walls of "a few hundred Planck lengths" (Sec. 5, citing ER97 and Pfenning–Ford 1997).
  - [claim] Time machines that evade GO07 are either non-asymptotically-flat (Gödel, Mallett's infinite cylinder, Gott's strings) or not compactly generated (Ori) (Sec. 5).
- **Method / verification standard:** topical review with new derivations.
- **Scope and caveats:** review; formulation (ii) is a proposal.
- **Disputes, refutations, later corrections:** the warp-drive sentence conflicts with GO07 Sec. IV.D (see Open disputes).
- **Relation to active-rail results:** (g) Formulation (ii) sets a transverse-width criterion. A rail ANEC deficit confined to a Planck-width bundle would be permitted, and a deficit carried by a macroscopic bundle of achronal rays would be forbidden. The project's departure fan shows negative ANEC only on the 0° ray (positive at 0.5°), so the transverse width of the negative-ANEC bundle is the quantity that decides the claim. It is measured by displacing rays in parallel, not by rotating them about one event. (c) The review's Hawking–Ellis type discussion supports using Type I as the setting for pointwise conditions.
- **Key quote:** "One of these conditions, the achronal averaged null energy condition, has recently received increased attention. It is expected to be a universal property of the dynamics of all gravitating physical matter, even in the context of semiclassical or quantum gravity." (abstract, v2)

### BV00 — Carlos Barceló, Matt Visser (2000), "Scalar fields, energy conditions, and traversable wormholes" (abstract-level)
- **Citation:** Class. Quantum Grav. 17, 3843–3864 (2000); DOI 10.1088/0264-9381/17/18/318. arXiv:gr-qc/0003025v2 (pinned; 14 Jul 2000). Submission history: v1 Wed, 8 Mar 2000 03:14:11 UTC; v2 Fri, 14 Jul 2000 23:29:14 UTC. Verified via https://arxiv.org/abs/gr-qc/0003025 on 2026-09-26.
- **Design parts and knobs:** the curvature coupling ξ > 0; the field amplitude relative to the Planck scale.
- **Knob → physics relations:** [derivation] Classical non-minimally coupled scalars violate every standard energy condition, including ANEC, and support traversable wormholes for every ξ > 0, provided the field reaches trans-Planckian values somewhere (abstract).
- **Method / verification standard:** exact static spherically symmetric solutions.
- **Scope and caveats:** requires trans-Planckian field values. GO07, KO15 and KS20 note that the effective Newton constant diverges and changes sign.
- **Disputes, refutations, later corrections:** physical admissibility is disputed (GO07 Sec. I; KO15 Sec. VIII; KS20 Sec. 4.3).
- **Relation to active-rail results:** (g) This is the classical ANEC-violating class the project keeps open ("classical fields that violate ANEC, of which the higher-derivative scalars are the open family"). The literature's standing objection to this class is the Planck-scale amplitude and G_eff sign change.
- **Key quote:** "We demonstrate that a non-minimally coupled scalar field with a positive curvature coupling xi>0 can easily violate all the standard energy conditions, up to and including the averaged null energy condition (ANEC)." (abstract, v2)

---

## D. Null-segment bounds (no-go, SNEC, DSNEC, QNEIs) and QEI reviews

### FR03 — C. J. Fewster, T. A. Roman (2003), "Null energy conditions in quantum field theory"
- **Citation:** Phys. Rev. D 67, 044003 (2003); DOI 10.1103/PhysRevD.67.044003; report ESI 1205. Erratum: Phys. Rev. D 80, 069903 (2009) (Crossref; erratum content not read). arXiv:gr-qc/0209036v2 (pinned; 26 Nov 2002). Submission history: v1 Wed, 11 Sep 2002 14:38:12 UTC; v2 Tue, 26 Nov 2002 10:24:53 UTC. Verified via https://arxiv.org/abs/gr-qc/0209036 on 2026-09-26; abstract-level with PDF downloaded.
- **Design parts and knobs:** the averaging curve (a finite null segment versus a timelike worldline); the state class (Hadamard).
- **Knob → physics relations:**
  - [identity/theorem] For the massless minimally coupled scalar in 4D Minkowski space, weighted null-segment averages of T_ab k^a k^b are unbounded below on Hadamard states (explicit construction).
  - [identity/theorem] The same states obey ANEC. In any globally hyperbolic spacetime, the null-contracted stress averaged over a *timelike worldline* obeys a QI (abstract).
- **Method / verification standard:** rigorous construction.
- **Scope and caveats:** free scalar; the 2D analogue has null QIs.
- **Disputes, refutations, later corrections:** the 2009 erratum exists (Crossref), and its content is UNVERIFIED here. FK18 and FF21 evade the no-go with a UV cutoff; FFK21 with double smearing.
- **Relation to active-rail results:** (g) A finite segment of a rail light ray carries no state-independent QFT floor on null energy. Constraints come from complete achronal rays (ANEC), timelike-worldline averages of T_kk, or cutoff-dependent SNEC. This is why the project's ANEC map integrates complete rays.
- **Key quote:** "Thus there are no quantum inequalities along null geodesics in four-dimensional Minkowski spacetime." (abstract, v2)

### FK18 — Ben Freivogel, Dimitrios Krommydas (2018), "The Smeared Null Energy Condition"
- **Citation:** JHEP 12 (2018) 067 (Crossref); DOI 10.1007/JHEP12(2018)067. arXiv:1807.03808v4 (read; 19 Apr 2021). Submission history: v1 Tue, 10 Jul 2018 18:19:33 UTC; v2 Thu, 12 Jul 2018 08:08:16 UTC; v3 Thu, 18 Apr 2019 03:53:19 UTC; v4 Mon, 19 Apr 2021 09:54:21 UTC. Verified via https://arxiv.org/abs/1807.03808 on 2026-09-26; full text https://arxiv.org/pdf/1807.03808v4.
- **Design parts and knobs:** the null smearing length τ (affine); Newton's constant G_N (or UV cutoff ℓ_UV and field number N); the defocusing of null congruences.
- **Knob → physics relations:**
  - [claim] SNEC: ⟨T_kk⟩ smeared over affine length τ ≥ −B/(G_N τ²) (eq. 4), with B of order one, valid for τ below the curvature scale. Equivalent forms: R_kk ≥ −#/τ² (eq. 6); T_kk ≥ −Bħ N/(ℓ_UV^(D−2) τ²) (eq. 8).
  - [derivation] Fractional area change ΔA/A = −λ² G_N⟨T_kk⟩ ≥ −B (eq. 41): negative null energy defocuses only within the linear-gravity regime.
  - [derivation] An isolated NEC-violating region of fixed negative energy per unit transverse area b gives ⟨T_kk⟩ ∝ −b/τ, which violates the τ⁻² bound for large τ. Isolated negative null energy is forbidden (Sec. 1).
- **Method / verification standard:** proposal backed by examples and the induced-gravity argument.
- **Scope and caveats:** a conjecture; regime of perturbative quantum gravity.
- **Disputes, refutations, later corrections:** FF21 proves a version for free and super-renormalizable theories with a UV cutoff and shows light-sheet smearing alone cannot improve it; FFK21 proposes DSNEC.
- **Relation to active-rail results:** (g) Complementary to ANEC. Any quantum contribution to the rail's null-energy deficit is limited to O(B) defocusing per smearing length, so a quantum sector cannot produce the order-one focusing reversal a macroscopic lead needs. (a)/(b) The bound constrains R_kk, which receives contributions from both shift shear and lapse curvature.
- **Key quote:** "If correct, our bound implies that regions of negative energy density are never strongly gravitating, and that isolated regions of negative energy are forbidden." (abstract, v4)

### FF21 — Jackson R. Fliss, Ben Freivogel (2022), "Semi-local Bounds on Null Energy in QFT" (abstract-level)
- **Citation:** SciPost Phys. 12, 084 (2022) (Crossref; not shown on arXiv); DOI 10.21468/SciPostPhys.12.3.084 (Crossref). arXiv:2108.06068v1 (pinned; v1 only). Submission history: v1 Fri, 13 Aug 2021 05:29:48 UTC. Verified via https://arxiv.org/abs/2108.06068 on 2026-09-26.
- **Design parts and knobs:** smearing on a light sheet versus two null directions; UV cutoff; correlation length.
- **Knob → physics relations:** [identity/theorem] A version of SNEC is proven for free and super-renormalizable QFTs with a UV cutoff (light-sheet quantization). Squeezed states show light-sheet smearing alone cannot improve it. [claim] DSNEC is cutoff-independent and changes behaviour when the smearing lengths reach the correlation length (abstract).
- **Method / verification standard:** light-sheet quantization with explicit states.
- **Scope and caveats:** free or super-renormalizable theories.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** a UV-cutoff-dependent floor on finite null segments of rail rays. (g): complementary.
- **Key quote:** "we use light-sheet quantization to prove a version of the 'Smeared Null Energy Condition' (SNEC) proposed in [1], applicable for free and super-renormalizable QFT's equipped with a UV cutoff." (abstract, v1)

### FFK21 — Jackson R. Fliss, Ben Freivogel, Eleni-Alexandra Kontou (2023), "The double smeared null energy condition" (abstract-level)
- **Citation:** SciPost Phys. 14, 024 (2023) (Crossref; not shown on arXiv); DOI 10.21468/SciPostPhys.14.2.024 (Crossref). arXiv:2111.05772v1 (pinned; v1 only). Submission history: v1 Wed, 10 Nov 2021 16:24:47 UTC. Verified via https://arxiv.org/abs/2111.05772 on 2026-09-26.
- **Design parts and knobs:** smearing over two null directions.
- **Knob → physics relations:** [identity/theorem] DSNEC, a finite lower bound on null energy smeared over two null directions, is derived rigorously for free fields in Minkowski space from worldvolume bounds (abstract).
- **Method / verification standard:** rigorous worldvolume QEIs.
- **Scope and caveats:** free fields, flat space; curvature corrections left for later work.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** a spacetime-smeared floor applicable to a rail's null-energy deficit over a finite region; relevant for configurations with no lead (see K24). (g): complementary.
- **Key quote:** "Here, we propose an alternative, the double smeared null energy condition (DSNEC), stating that the null energy smeared over two null directions has a finite lower bound." (abstract, v1)

### FKK22 — Ben Freivogel, Eleni-Alexandra Kontou, Dimitrios Krommydas (2022), "The Return of the Singularities: Applications of the Smeared Null Energy Condition"
- **Citation:** SciPost Phys. 13, 001 (2022); DOI 10.21468/SciPostPhys.13.1.001. arXiv:2012.11569v2 (read; 15 Nov 2021). Submission history: v1 Mon, 21 Dec 2020 18:46:37 UTC; v2 Mon, 15 Nov 2021 17:17:02 UTC. Verified via https://arxiv.org/abs/2012.11569 on 2026-09-26; full text https://arxiv.org/pdf/2012.11569v2 (Secs. 1–2 read).
- **Design parts and knobs:** the SNEC constant B; the ratio of UV cutoff to Planck length; the number of fields.
- **Knob → physics relations:**
  - [derivation] Induced gravity gives B = 1/32π. The authors argue that "when semi-classical gravity is well under control, B ≪ 1" (Sec. 2.2; the relation symbol was lost in the text layer and is reconstructed from context).
  - [identity/theorem] A Penrose-type semiclassical singularity theorem follows with SNEC as the assumption (abstract).
  - [claim] "It was shown [29] that achronal ANEC is sufficient to rule out so called 'short' wormholes. In those it takes longer to travel through the ambient space than the wormhole, creating a shortcut in spacetime" (Sec. 1).
- **Method / verification standard:** proof of a singularity theorem under a conjectured bound.
- **Scope and caveats:** SNEC is assumed.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (g) The short/long classification stated here maps directly onto "lead over exterior light" versus "no lead". The rail with a lead is a "short" configuration in their sense.
- **Key quote:** "Here, we provide motivation for an energy condition obeyed by semiclassical gravity: the smeared null energy condition (SNEC), a proposed bound on the weighted average of the null energy along a finite portion of a null geodesic." (abstract, v2)

### K24 — Eleni-Alexandra Kontou (2024), "Wormhole restrictions from quantum energy inequalities"
- **Citation:** Universe 10 (7), 291 (2024) (Crossref); DOI 10.3390/universe10070291. arXiv:2405.05963v2 (read; 8 Jul 2024). Submission history: v1 Thu, 9 May 2024 17:58:40 UTC; v2 Mon, 8 Jul 2024 11:50:33 UTC. Verified via https://arxiv.org/abs/2405.05963 on 2026-09-26; full text https://arxiv.org/pdf/2405.05963v2.
- **Design parts and knobs:** "short" versus "long" (whether passage beats the ambient route); asymptotic flatness; genericity; achronal segment length inside a long wormhole.
- **Knob → physics relations:**
  - [identity/theorem] Definitions: "A 'short' wormhole is one where the proper time of the observer travelling through it is shorter that the travel in ambient space … In a 'long' wormhole, travelling between the mouths on the outside is shorter in proper time." (Sec. 4.1)
  - [claim] Short wormholes are ruled out by self-consistent achronal ANEC (via GO07). Long wormholes escape because "there are no complete achronal null geodesics passing through them", and null QEIs (SNEC, DSNEC) restrict them instead (Secs. 1, 5.3, 6).
  - [derivation] New DSNEC constraint on the length of the Maldacena–Milekhin–Popov long wormhole (Sec. 6).
  - [claim] Remaining options for short wormholes: loss of asymptotic flatness, non-semiclassical regimes, or chronal geodesics (Sec. 7).
- **Method / verification standard:** review plus one new calculation.
- **Scope and caveats:** wormhole-specific; the short-wormhole exclusion inherits GO07's conjecture status.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (g) This is the closest literature statement of the project's dichotomy. A rail that delivers a lead is "short" and falls under achronal ANEC. A rail that trades the lead for other benefits (passenger proper time, tides) is "long" and faces only null QEIs. This splits design strategy into two families with different source classes.
- **Key quote:** "'Long' wormholes circumvent the problem of the achronal ANEC, as there are no complete achronal null geodesics passing through them. In this case, null QEIs could provide restrictions." (Sec. 1, v2)

### FRo25 — Jackson R. Fliss, Andrew Rolph (2025), "Curious QNEIs from QNEC: New Bounds on Null Energy in Quantum Field Theory" (abstract-level)
- **Citation:** no journal reference on arXiv. arXiv:2510.26247v2 (pinned; 16 Apr 2026). Submission history: v1 Thu, 30 Oct 2025 08:31:26 UTC; v2 Thu, 16 Apr 2026 14:26:30 UTC ("simplified the higher-dimensional energy inequality and clarified its state-dependence"). Verified via https://arxiv.org/abs/2510.26247 on 2026-09-26.
- **Design parts and knobs:** semi-local integrals of T_vv over null intervals and strips.
- **Knob → physics relations:** [identity/theorem] State-independent lower bounds on semi-local integrals of ⟨T_vv⟩, including for interacting theories in higher dimensions, from QNEC, strong subadditivity and modular Hamiltonians (abstract). The v2 comment adds a clarification of state dependence for the higher-dimensional inequality.
- **Method / verification standard:** entropic methods.
- **Scope and caveats:** flat-space QFT.
- **Disputes, refutations, later corrections:** v2 revises the higher-dimensional statement.
- **Relation to active-rail results:** newer null-segment floors applicable to finite rail ray segments. (g): complementary.
- **Key quote:** "These are universal, state-independent lower bounds on semi-local integrals of ⟨T_vv⟩, the energy-momentum flux in a null direction, and the first of this kind for interacting theories in higher dimensions." (abstract, v2)

### P26 — Andrea Palessandro (2026), "Quantum Inequalities from the Second Law" (abstract-level)
- **Citation:** Int. J. Theor. Phys. 65, 233 (2026); DOI 10.1007/s10773-026-06434-x. arXiv:2608.11817v1 (pinned; v1 only). Submission history: v1 Wed, 12 Aug 2026 08:58:51 UTC. Verified via https://arxiv.org/abs/2608.11817 on 2026-09-26.
- **Design parts and knobs:** a thermal detector coupled to the field.
- **Knob → physics relations:** [derivation] Ford–Roman QIs follow operationally from the second law, through non-negative detector–field entanglement entropy (abstract).
- **Method / verification standard:** operational model.
- **Scope and caveats:** new paper; independent checks not yet visible.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** a thermodynamic basis for QIs parallel to W10's GSL basis for achronal ANEC. (g): indirect.
- **Key quote:** "by the non-negativity of the entanglement entropy between the two systems, one can show that its heat loss is bounded from below by a state-independent quantity." (abstract, v1)

---

## E. Chronology

### H92 — S. W. Hawking (1992), "Chronology protection conjecture"
- **Citation:** Phys. Rev. D 46, 603–611 (1992) (Crossref); DOI 10.1103/PhysRevD.46.603; received 23 Sep 1991, published 15 Jul 1992. No arXiv version. Verified 2026-09-26 via WebFetch of https://journals.aps.org/prd/abstract/10.1103/PhysRevD.46.603 (metadata; paraphrased abstract), Crossref metadata, and the text layer of the published article (archive.org item `pdfy-rUc2KLIygUZjXGDb`, a mirror of the APS PDF). Quotes come from that text layer.
- **Design parts and knobs:** a finite causality-violating region without curvature singularities; a compactly generated Cauchy horizon; closed null generators with boost and area-increase factors; the frame of the return trip.
- **Knob → physics relations:**
  - [identity/theorem] If causality violation develops from a non-compact initial surface, AWEC must be violated on the Cauchy horizon (abstract).
  - [claim] Vacuum polarization grows large as timelike curves become almost closed, and back-reaction prevents CTCs (abstract; Sec. I).
  - [claim] Faster-than-light travel converts to time travel by returning "again faster than light, but in a different Lorentz frame" (Sec. I).
- **Method / verification standard:** global analysis plus semiclassical estimates.
- **Scope and caveats:** chronology protection is a conjecture. GO07 later upgraded the energy-condition part to self-consistent achronal ANEC.
- **Disputes, refutations, later corrections:** KS20 lists non-compactly-generated proposals (Ori) and non-asymptotically-flat ones that evade the theorem.
- **Relation to active-rail results:** a rail network approaching a closed causal loop would meet diverging vacuum polarization, so choreography should keep a margin from any chronology horizon. The "different Lorentz frame" clause names the design lever. Every rail should share one global rest frame and time orientation (see SS24, E96).
- **Key quote:** "Even if violations of the weak energy condition are allowed by quantum theory, the expectation value of the energy-momentum tensor would get very large if timelike curves become almost closed. It seems the back reaction would prevent closed timelike curves from appearing." (abstract, published text)

### E96 — Allen E. Everett (1996), "Warp drive and causality"
- **Citation:** Phys. Rev. D 53, 7365–7368 (1996) (Crossref); DOI 10.1103/PhysRevD.53.7365; received 14 Sep 1995, published 15 Jun 1996. No arXiv version located. Verified 2026-09-26 via WebFetch of https://journals.aps.org/prd/abstract/10.1103/PhysRevD.53.7365 (paraphrased abstract), Crossref metadata, and the text layer of the published article hosted at https://www.if.ufrj.br/~mbr/warp/etc/prd53_7365.pdf. Quotes come from that text; mathematical symbols are garbled in the text layer, so inequalities below are transcribed from context.
- **Design parts and knobs:** bubble acceleration a over route length D; lateral offset y0 ≫ R between outbound and return lines; the relative boost β between the two bubbles' rest frames; wall thickness σ.
- **Knob → physics relations:**
  - [derivation] A bubble accelerating uniformly over the first half and decelerating over the second beats light when a > 4/D (eq. 5).
  - [derivation] The arrival event has negative time order in a frame boosted by β when a > 4/(Dβ²) (eq. 7).
  - [derivation] A second bubble defined in the boosted frame, on a laterally offset line, returns the traveller at t ≈ −βD in the high-acceleration limit (eq. 9). The two bubbles give CTCs, and their overlap can be made negligible by y0 ≫ R (eq. 10).
  - [identity/theorem] A single-frame family admits no causal loops: "the forward light cone of an event at t = t0 includes only events with t > t0; signals can only be sent in one direction in t" (text before eq. 10).
- **Method / verification standard:** explicit metric superposition; analytic.
- **Scope and caveats:** thin-wall Alcubierre metric; the overlap is only approximately negligible (SS24 makes the construction exact).
- **Disputes, refutations, later corrections:** SS24 refines it (non-unit lapse for frame transitions, compact support).
- **Relation to active-rail results:** chronology. *(this inventory, [derivation])* Any metric of the form −N²dt² + γ_ij(dx^i − β^i dt)(dx^j − β^j dt) with N > 0 and γ positive definite on a single global slicing has g^tt = −1/N² < 0, so t increases along every future causal curve and no closed causal curve exists. The active rail with (b)/(d) on one global foliation is chronology-safe. CTC risk arises only when rails are defined on different foliations (moving stations, boosted rail frames), which is E96's second bubble. (g) E96's lead over light is the project's lead.
- **Key quote:** "The spaceship beats the light signal to S2 not because its motion is spacelike but because, in effect, the bubble acts like a wormhole and provides a shortcut from S1 to S2." (p. 7366)

### SS24 — Barak Shoshany, Ben Snodgrass (2024), "Warp Drives and Closed Timelike Curves"
- **Citation:** Class. Quantum Grav. 41, 205005 (2024); DOI 10.1088/1361-6382/ad74d1. arXiv:2309.10072v3 (read; 16 Sep 2024). Submission history: v1 Mon, 18 Sep 2023 18:37:30 UTC; v2 Mon, 22 Apr 2024 18:03:01 UTC; v3 Mon, 16 Sep 2024 20:36:28 UTC ("version published in Classical and Quantum Gravity"). Verified via https://arxiv.org/abs/2309.10072 on 2026-09-26; full text https://arxiv.org/pdf/2309.10072v3.
- **Design parts and knobs:** a spatially varying lapse N; the shift β = a(t) v(t, x); compact support of each drive; the relative frame velocity u; drive speed v.
- **Knob → physics relations:**
  - [identity/theorem] Eulerian worldlines are geodesics iff ∂_i N = 0 (from eq. 2.4). Natário-class drives (N = 1, flat slices), and drives with N = N(t), return passengers to the original rest frame, so "we have no choice but to introduce spatial dependence into the lapse" for geodesic rest-frame transitions (Sec. 2.1).
  - [derivation] Two compactly supported, non-overlapping drives that begin and end in different rest frames produce an explicit closed timelike geodesic (eq. 3.5; Sec. 3).
  - [identity/theorem] For flat slices with lapse N: ρ = (1/16πG)(1/N²)((∂_iβ^i)² − ∂_(iβ_j)∂_(iβ_j)) (eq. 4.3). With β = O(r^(−1/2)), ∫N²ρ d³x ≤ 0, strictly when β has curl (eq. 4.8).
  - [claim] E_tot = ∫ρ d³x "can however be made arbitrarily small simply by making N large where ∇β is large", at the cost that shell matter experiences the journey stretched by a factor of order N (Sec. 4.2).
  - [derivation] For ρ = 0 = ∂_[iβ_j], p̄ = −K² − L_nK + ΔN/N (eq. 4.25), and the WEC forces ∂_t∫K d³x ≤ 0, which forbids re-flattening drives that start from flat space unless T = 0 (Sec. 4.3).
- **Method / verification standard:** explicit metrics with symbolic computation (OGRe/OGRePy).
- **Scope and caveats:** the WEC analysis assumes C² fields, the decay condition and asymptotic flatness. NEC violation with N ≠ 1 is left unproved.
- **Disputes, refutations, later corrections:** SS24 disputes O98's definition (Sec. 4.2) and calls the WEC violations "likely nothing more than an artefact of the particular class of metrics".
- **Relation to active-rail results:** (a) *(this inventory, [derivation])* For a pure shear shift β = β(x⊥) ẑ, eq. 4.3 gives ρ = −|∇⊥β|²/(32πN²), identical to project result (a) with N = α. (b) N enters ρ only through 1/N², and enters stresses through ΔN/N (eq. 4.25), consistent with "stress without energy". (d) The spatially varying lapse that sets the rail speed is exactly the ingredient SS24 shows enables geodesic frame transitions, and hence CTC constructions. Chronology safety therefore needs every rail on one global foliation (see E96). E_tot suppression by lapse is a design knob, and its null-energy cost appears in the project's axis result T(k,k) = α_rr/(4πα).
- **Key quote:** "By generalizing the usual warp drive metric to allow for a non-unit lapse function, we allow the warp drive to switch between reference frames in a purely geometric way. With an additional modification allowing the warp drive to have compact support, this permits us to glue two warp drives together to construct a closed timelike geodesic" (abstract, v3)

(ER97, the two-tube time machine, appears in Part A.)

---

## F. 2018–2026 applications to warp drives and shortcuts, and older weak-field constraints

**Search record (2026-09-26).** WebSearch queries covered QI or SNEC bounds on warp drives, QI bounds on wall thickness, ANEC along bubble-crossing geodesics, and SNEC or DSNEC applied to warp drives or wormholes. No paper applying SNEC or DSNEC to a warp drive or rail was located. Located and verified: SNEC/DSNEC applied to the Maldacena–Milekhin–Popov long wormhole (FKK22, K24); flat-space QI estimates and finite-segment null integrals for four warp geometries (Le26); a Planck-regularized warp profile (JL26); an averaged-condition claim for a de Sitter-embedded bubble (GZ25).

### SSV22 — Jessica Santiago, Sebastian Schuster, Matt Visser (2022), "Generic warp drives violate the null energy condition"
- **Citation:** Phys. Rev. D 105, 064038 (2022); DOI 10.1103/PhysRevD.105.064038. arXiv:2105.03079v2 (read; 25 Feb 2022). Submission history: v1 Fri, 7 May 2021 06:25:26 UTC; v2 Fri, 25 Feb 2022 23:32:51 UTC ("Arguments clarified and made more precise; no significant change in physics conclusions"). Verified via https://arxiv.org/abs/2105.03079 on 2026-09-26; full text https://arxiv.org/pdf/2105.03079v2.
- **Design parts and knobs:** unit lapse; flat slices (Natário class); flow-field gradients at infinity; vorticity; Eulerian worldlines crossing the wall.
- **Knob → physics relations:**
  - [identity/theorem] The NEC implies ρ + p̄ ≥ 0, with ρ + p̄ = (1/24π)(−2L_nK + K² − 3 tr K²) (eq. 7.30), hence dK/dτ ≤ −(2/3) tr[K^tf]² ≤ 0 along Eulerian worldlines. Eulerian observers that cross the wall and return to flat space violate this monotonicity, so every Natário-class drive violates the NEC (Sec. 7).
  - [derivation] Zero vorticity ⇒ zero Eulerian flux ⇒ block-diagonal stress, i.e. Hawking–Ellis Type I (Sec. 5).
  - [claim] Non-unit-lapse and Van den Broeck geometries "must be directly addressed using different techniques" (Appendix B).
- **Method / verification standard:** analytic.
- **Scope and caveats:** unit lapse and flat slices; sufficiently localized flow.
- **Disputes, refutations, later corrections:** SS24 extends the WEC analysis to N ≠ 1 and leaves the NEC open there. Le26 confirms NEC violation numerically for four walls.
- **Relation to active-rail results:** (c) Project result (c) (zero momentum ⇒ Type I) parallels SSV22's zero-vorticity Type I statement. The rail's non-unit lapse places it outside SSV22's NEC theorem, and the project's own ANEC map supplies the NEC-violation evidence directly. (g): the NEC violation is pointwise, while (g) is global.
- **Key quote:** "all physically reasonable warp drives will violate the null energy condition, and so also automatically violate the WEC, and both the strong and dominant energy conditions." (abstract, v2)

### Le26 — An T. Le (2026), "Observer-robust energy condition verification for warp drive spacetimes"
- **Citation:** no journal reference. arXiv:2602.18023v6 (read; 24 Sep 2026). Submission history: v1 Fri, 20 Feb 2026 06:37:44 UTC; v2 Tue, 3 Mar 2026 15:26:27 UTC; v3 Mon, 27 Apr 2026 02:12:02 UTC; v4 Fri, 12 Jun 2026 11:49:05 UTC; v5 Tue, 1 Sep 2026 03:44:20 UTC; v6 Thu, 24 Sep 2026 05:50:28 UTC. Verified via https://arxiv.org/abs/2602.18023 on 2026-09-26; full text https://arxiv.org/pdf/2602.18023v6. The paper was revised six times in seven months, so the pin matters.
- **Design parts and knobs:** shift vorticity; speed v_s; bubble radius R_b; wall thickness; affine normalization of null rays; the sampling time of static wall observers.
- **Knob → physics relations:**
  - [identity/theorem] On flat unit-lapse slices, the momentum constraint relates Eulerian momentum to shift vorticity. For smooth shifts on ℝ³ with bounded vorticity, momentum vanishes identically exactly for a gradient plus rigid rotation (abstract; Lemma 2).
  - [identity/theorem] For speed-linear shifts, integrated negative Eulerian energy scales exactly as v_s² when finite (abstract).
  - [derivation] Flat-space QI threshold for a static wall observer: τ0_th ≃ c_metric (ℓ_P R_b)^(1/2), the geometric mean of the Planck length and bubble scale (eq. 36). "Their zero crossings cannot be rescaled to macroscopic R_b by equation (36)".
  - [identity/theorem] ∫T(k,k)dλ scales by c under k ↦ ck, so ANEC magnitudes depend on the chosen normalization, and signs do not (Sec. 3.5).
  - [numerical] Global interval bounds establish NEC violation in all four benchmark walls. The Eulerian reading misses about 73% of sampled wall WEC violations for the Type I Rodal profile (abstract).
- **Method / verification standard:** S-lemma linear matrix inequalities with interval arithmetic (the JAX toolkit "Warpax").
- **Scope and caveats:** "The null-geodesic integrals are finite-segment, basin-local diagnostics … they supply no complete-geodesic ANEC conclusion. The flat-space quantum-inequality estimates likewise supply no curved-spacetime bound." (Sec. 6)
- **Disputes, refutations, later corrections:** notes that Garattini–Zatrimaylov's divergence identities "do not establish pointwise energy-condition satisfaction" (Sec. 1).
- **Relation to active-rail results:** (c) The momentum–vorticity lemma is stated for unit lapse. The rail's zero-momentum Type I result with a lapse lies outside its stated scope. (a) v_s² scaling of integrated negative Eulerian energy matches the quadratic shear form of (a). (g) The normalization identity matters for the project's ANEC magnitudes (−202, −2.2×10⁴), which carry the chosen affine normalization, while their signs carry the physics. Le26's warning that finite segments give no ANEC conclusion supports the project's use of complete rays.
- **Key quote:** "For smooth shifts on all of Euclidean space with bounded vorticity, momentum vanishes identically precisely for a gradient plus rigid rotation." (abstract, v6)

### JL26 — Kimet Jusufi, Francisco S. N. Lobo (2026), "Quantum-gravity-inspired Alcubierre warp-drive geometries" (abstract-level)
- **Citation:** no journal reference. arXiv:2609.05554v1 (pinned; v1 only). Submission history: v1 Thu, 3 Sep 2026 15:34:50 UTC. Verified via https://arxiv.org/abs/2609.05554 on 2026-09-26.
- **Design parts and knobs:** the effective profile scale l with l² = R² + l0² (zero-point length l0); speed v_s.
- **Knob → physics relations:** [derivation] E = −(15π/1024) v_s² l, with |ρ_E| bounded by a constant times v_s²/l² (abstract). The R → 0 divergence at fixed speed is removed, but the thin-wall limit at fixed macroscopic R remains.
- **Method / verification standard:** closed-form effective ansatz.
- **Scope and caveats:** "Exotic matter remains necessary, and neither semiclassical stability nor a modified quantum energy inequality is claimed" (abstract).
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (a) the same v² energy scaling. (g): none.
- **Key quote:** "In particular, E=−(15π/1024)v_s² l in geometric units and |ρ_E| is bounded by a constant times v_s²/l²." (abstract, v1)

### GZ25 — Remo Garattini, Kirill Zatrimaylov (2025), "Warp Drive in a De Sitter Universe" (abstract-level)
- **Citation:** no journal reference. arXiv:2502.13153v4 (pinned; 17 Jun 2026). Submission history: v1 Fri, 14 Feb 2025 08:19:04 UTC; v2 Fri, 28 Feb 2025 14:18:06 UTC; v3 Fri, 12 Jun 2026 05:58:43 UTC; v4 Wed, 17 Jun 2026 12:46:42 UTC. Verified via https://arxiv.org/abs/2502.13153 on 2026-09-26.
- **Design parts and knobs:** bubble speed equal to the local expansion speed; the de Sitter background.
- **Knob → physics relations:** [claim] Non-negative energy density, with WEC and NEC "satisfied up to a total divergence term that averages to zero" (abstract).
- **Method / verification standard:** analytic.
- **Scope and caveats:** the background is not asymptotically flat, so the bubble is carried by cosmic expansion.
- **Disputes, refutations, later corrections:** Le26: divergence identities "do not establish pointwise energy-condition satisfaction".
- **Relation to active-rail results:** (g) Non-asymptotically-flat backgrounds are one of the exits K24 and KS20 list from the achronal-ANEC theorems. A rail relies on an asymptotically flat exterior and does not use this exit.
- **Key quote:** "it is possible for the bubble to have strictly non--negative energy density, with the weak and null energy satisfied up to a total divergence term that averages to zero." (abstract, v4)

### LV04 — Francisco S. N. Lobo, Matt Visser (2004), "Fundamental limitations on 'warp drive' spacetimes"
- **Citation:** Class. Quantum Grav. 21, 5871–5892 (2004); DOI 10.1088/0264-9381/21/24/011. arXiv:gr-qc/0406083v2 (read; 31 Oct 2004). Submission history: v1 Mon, 21 Jun 2004 11:07:42 UTC; v2 Sun, 31 Oct 2004 13:32:19 UTC ("no physics changes"). Verified via https://arxiv.org/abs/gr-qc/0406083 on 2026-09-26; full text https://arxiv.org/pdf/gr-qc/0406083v2.
- **Design parts and knobs:** bubble speed v ≪ 1; radius R; wall thickness Δ = 1/σ; ship mass M_ship and size R_ship.
- **Knob → physics relations:**
  - [derivation] M_warp ≈ −v²R²σ. "The energy requirements for the warp bubble scale quadratically with bubble velocity, quadratically with bubble size, and inversely as the thickness of the bubble wall" (eq. 14).
  - [derivation] A positive volume-averaged WEC requires v²R²σ ≲ M_ship, i.e. v² ≲ (M_ship/R_ship)(R_ship Δ/R²) (eqs. 94–95).
  - [derivation] Localized NEC violations persist even with a finite-mass ship inside (Sec. 5).
- **Method / verification standard:** exact and linearized gravity.
- **Scope and caveats:** non-relativistic speeds; Alcubierre and Natário forms.
- **Disputes, refutations, later corrections:** none visible.
- **Relation to active-rail results:** (a) the same v² and inverse-thickness scaling. The ship-mass bound links cabin mass budgets to allowed speed for self-sourced designs, and does not apply to externally sourced rails. (g): none.
- **Key quote:** "For both the Alcubierre and Natario warp drives we find that the occurrence of significant energy condition violations is not just a high-speed effect, but that the violations persist even at arbitrarily low speeds." (abstract, v2)

---

## 1. Synthesis table

| Knob / part | Physics relation | Papers | Status |
|---|---|---|---|
| Sampling time τ0 vs negative density ρ | ρ̂ ≥ −3/(32π²τ0⁴) scalar, −3/(16π²τ0⁴) EM (flat) | FR95, FR97, FE98 | theorem (free fields, flat) |
| Curved-space QI validity scale | flat form holds for τ0 ≪ curvature radius, boundary distance and the g_tt-gradient scale | PF98, FR96, FR97, F00 | derivation (static); claim (general) |
| Lapse (g_tt) near horizons | shortens the validity scale of flat QIs for static observers | PF98 | derivation |
| Wall or layer thickness ε, curvature radius | QI ⇒ ε ≲ ℓ_P/σ² ~ 10²–10⁴ ℓ_P; shear-layer form αw/Δβ ≲ ℓ_P/f² | ER97, FR96, KS20 (citing Pfenning–Ford 1997); this inventory | derivation (QI-in-curved-space assumed) |
| Light-cone opening η vs ε | η ≲ (ℓ_P/ε)² for QI-sourced walls; lead fraction ~ 10⁻⁶⁶ at 1 cm | ER97 | derivation |
| Throat r0 vs band a0 | a0 ≲ (r0/(8f⁴ℓ_P))^(1/3) ℓ_P; large redshift as escape | FR96 | derivation |
| Field number N | bounds relax as √N; ~10⁶² fields for 1 m | FR96, FR97 | derivation |
| Weyl/Ricci ratio, periodic identification | QI ⇏ Planck densities when Weyl dominates or L is small | K03 | claim/derivation (disputed) |
| Interacting fields | static negative energy violating QIs (domain wall) | OG03 | derivation |
| Fastest ray segment (local lead) | negative null energy on the segment; shear adds to demand | O98 (+ this inventory) | theorem (generic condition) |
| Weak-field light-cone opening | needs NEC violation on the retarded past cone (Lorentz gauge) | VBL98, VBL99 | derivation; gauge-dependent (GW00) |
| Global lead over exterior light | implies a null line; with genericity, ANEC < 0 on it | GW00 (Galloway fn.) + GO07 Lemma 1 | theorem chain (completeness, genericity) |
| Quantum source of a global lead | excluded under self-consistent achronal ANEC | GO07 (conjecture), W10 (1st order ħ, GSL), KO15 (free scalar, NEC background) | conjecture; proven perturbatively |
| Flat-space ANEC | holds for general QFTs | FLPW16, HKT17 | theorem |
| Test-field achronal ANEC in curved space | violated arbitrarily (conformal factor width r) | UO10 | derivation |
| Transverse width of ANEC deficit | violations only over Planck transverse widths; uniform tube negativity forbidden | KS20 (ii), KO15, UO10 | claim / theorem (free scalar) |
| Finite null segment | unbounded below (4D); SNEC ≥ −B/(G_N τ²); DSNEC | FR03, FK18, FF21, FFK21, FRo25 | theorem / conjecture |
| Defocusing magnitude | ΔA/A ≥ −B (B ≤ 1/32π or ≪ 1) | FK18, FKK22 | conjecture |
| Short vs long shortcut | short ⇒ achronal-ANEC bound; long ⇒ null QEIs | K24, FKK22, GO07 | claim (inherits conjecture) |
| Exterior flatness / compact support | DEC + flat outside world tube ⇒ flat; zero mass ⇒ negative energy | GW00, K03, PSW93 | theorem / derivation |
| Decision-to-arrival | no earlier arrival than ∂D⁺(Σ∖K) with DEC hyperbolic matter | L99 | theorem |
| Construction time | shortcut to a 100 ly star usable in 1 yr takes ≥ 99 yr to build | K03 (citing Krasnikov 1998) | claim |
| Front half-angle | sin θ < 1/v ⇔ subluminal normal speed of the front (timelike front) | this inventory, with L99 | derivation |
| Two shortcuts in different frames | CTCs (bubbles, tubes); a single foliation with N > 0 has none | E96, ER97, SS24, H92; this inventory | derivation |
| Spatially varying lapse | required for geodesic rest-frame transitions | SS24 | theorem (within the stated class) |
| Lapse vs Eulerian energy | ρ ∝ 1/N²; E_tot suppressed by large N in shear regions at an N-fold time-dilation cost | SS24 | identity / claim |
| Zero vorticity / zero momentum | Type I stress (unit lapse) | SSV22, Le26 | derivation / theorem |
| Speed and size scaling | M_warp ≈ −v²R²σ; integrated negative Eulerian energy ∝ v² | LV04, Le26, JL26 | derivation / theorem |
| ANEC normalization | magnitude scales with k-normalization; sign invariant | Le26 | identity |
| Near-closed timelike curves | vacuum polarization diverges | H92 | claim/conjecture |

## 2. Open disputes

1. **Non-perturbative superluminal censorship.** VBL98 v1 claimed "Superluminal travel requires violations of the averaged null energy condition (ANEC)" for asymptotically flat spacetimes. v2 abandoned the argument, which had "become bogged down in issues of considerable technical complexity". GW00 showed the perturbative light-cone comparison is gauge dependent. The rigorous replacement is GW00 Theorem 1 in Galloway's null-line form combined with GO07 Lemma 1.
2. **Olum's definition of superluminal travel.** SS24 (Sec. 4.2) argues that it misses Riemann-flat passenger regions (the generic condition fails), that neighbouring paths are equally fast, and that superluminal paths can be timelike. K03 notes that weak minima fail the definition. GO07 shows that achronal ANEC does not exclude Olum-type (local) superluminality.
3. **Does achronal ANEC rule out warp drives?** KS20 (Sec. 5): "By Olum's earlier proof [180], this theorem also prohibits warp drive spacetimes." GO07 (Sec. IV.D): "additional constraints are necessary to rule out superluminal communication." Resolution in this inventory: achronal ANEC excludes *global* leads (via GW00 and a null line) and compactly generated CTCs, and leaves *local* advances in place.
4. **QI-based unphysicality of shortcuts.** FR96, ER97 and Pfenning–Ford 1997 infer Planck-thin walls and huge E_tot. K03 disputes each step (Weyl dominance, periodic identifications, sub-Planckian layers).
5. **Status of achronal ANEC in curved spacetime.** Test-field violations exist (UO10; Visser's anomaly, discussed in GO07). The self-consistent version is a conjecture (GO07), proven at first order in ħ from the GSL (W10) and for a free scalar on NEC backgrounds (KO15). W10 flags failure once gravitons are quantized (shear-squared renormalization), and proposes a shear-inclusive ANEC.
6. **Universality of QIs.** Interacting domain-wall systems violate QIs (OG03); 2D CFTs obey null QEIs (FH05); 4D free fields have no null-segment QI (FR03).
7. **Averaged satisfaction by divergence terms.** GZ25 claims WEC and NEC hold "up to a total divergence term that averages to zero". Le26 states such identities do not establish pointwise satisfaction.
8. **Origin of WEC violation.** SS24 calls it likely an artefact of the metric class. SSV22 proves NEC violation for the entire Natário class. The non-unit-lapse NEC question remains open (SSV22 App. B; SS24 Sec. 4.1).

## 3. UNVERIFIED items

- **Fewster & Roman erratum**, Phys. Rev. D 80, 069903 (2009): existence confirmed via Crossref; content not read.
- **Pfenning & Ford 1997** (gr-qc/9702026): covered by another cluster. Its wall figure ("a few hundred Planck lengths") is cited here only through KS20.
- **Krasnikov 1998** (construction-time result), **Borde 1987** (focusing theorem), **Galloway's null splitting theorem**, **Tipler 1976/77**, **Flanagan & Wald 1996**, **Wald & Yurtsever 1991**, **Visser 1995 (scale anomaly)**: cited only through the verified papers that quote them; originals not read.
- **Barzegar & Buchert**, **Barzegar, Buchert & Vigneron**, **Fell & Heisenberg**, **Rodal 2025** (2512.18008, abs page parsed but paper not read), **Garattini & Zatrimaylov 2024** (2408.04495, abs page parsed only): mentioned in Le26 or found in searches; outside this cluster's sections.
- **Everett 1996 and Hawking 1992**: no arXiv versions. The APS abstract pages returned only paraphrases through WebFetch (direct retrieval blocked by Cloudflare). Verbatim text comes from published-article PDFs hosted by third parties (if.ufrj.br; archive.org), whose text layers garble some mathematical symbols.
- **PF98 eq. (48)**: the coefficient and superscript placement of the g_tt term are reconstructed from the PDF text layer.
- **FKK22 "B ≪ 1"**: the relation symbol was lost in the text layer and is reconstructed from context.
- **"Fewster & Kontou" review**: the brief named "Fewster & Kontou / Kontou & Sanders 2020". The 2020 CQG review verified here is by Kontou & Sanders; no separate Fewster–Kontou review was searched.
- **Journal references** for FF21 and FFK21 come from Crossref; the arXiv pages show none.

## 4. Assessment of project claim (g)

**The claim.** "The design needs negative ANEC along achronal light rays, as any lead over exterior light does … A semiclassical quantum sector therefore supplies none of this demand, at any size." The literature supports this as a conditional statement about global leads, and qualifies three of its parts.

**First part: a global lead needs negative ANEC on a null line.** This is established by a theorem chain.
- Take a compact modification of an asymptotically flat or exterior-flat spacetime that delivers a lead over exterior light, usable between arbitrarily distant endpoints on the route line.
- Gao–Wald's Theorem 1, in Galloway's form (GW00 footnote 1), then implies a null line: a complete achronal null geodesic.
- Graham–Olum's Lemma 1 (with Borde's focusing theorem and the null generic condition) then forces ANEC < 0 on that line.
- Visser–Bassett–Liberati claimed this directly (VBL98 v1) and withdrew the non-perturbative proof. Kontou (K24) and Freivogel–Kontou–Krommydas (FKK22) state the same short/long dichotomy for wormholes.

The chain needs:
- null geodesic completeness;
- the null generic condition;
- a lead that persists for asymptotically distant endpoints.

Olum 1998 gives only a finite-segment result for *local* leads. Graham–Olum state explicitly that achronal ANEC "is an adequate substitute for ordinary ANEC, but additional constraints are necessary to rule out superluminal communication" in that local sense.

**Second part: quantum sources supply none of the demand.** The condition is proven in these cases:
- flat-space QFT (FLPW16, HKT17);
- a free scalar perturbing an NEC-obeying background at first order in curvature (KO15);
- minimally coupled fields perturbing an NEC background at first order in ħ, given the GSL, CPT and a renormalization scheme (W10).

The self-consistent, non-perturbative case is Graham–Olum's *conjecture*: a quantum sector that itself supplies an O(1) geometry change, which is what "at any size" requires. Kontou–Olum list it explicitly as an open possibility. Test-field achronal ANEC is violated arbitrarily (UO10). Wall notes that the theorems fail once gravitons are quantized unless a shear-inclusive ANEC holds.

**Qualifications the project should carry.**
1. "At any size" holds only within the semiclassical regime. Kontou–Sanders' formulation (ii) permits violations over Planck-scale transverse widths.
2. The ray the project integrates lies on the departure event's causal boundary, which proves achronality of the segment from departure onward. The complete ray must also be shown achronal: it is the null line obtained as the limit of fastest paths between the distant endpoints p_n and q_n.
3. The transverse width of the negative-ANEC bundle should be measured with parallel-displaced rays. Kontou–Olum forbid uniform negativity across a tube, and formulation (ii) turns on transverse width.
4. The ANEC magnitudes (−202, −2.2×10⁴) carry the affine normalization; only their sign is invariant (Le26).
5. The "classical ANEC-violating scalar" exit (BV00) carries the literature's standing objection of trans-Planckian amplitudes and a sign-changing effective Newton constant.

With these qualifiers, (g) is consistent with the literature and matches its strongest current formulation.
---

## E. Chronology: which shortcut choreography produces closed timelike curves

### H92 — S. W. Hawking (1992), "Chronology protection conjecture"
- **Citation:** Phys. Rev. D 46, 603–611 (1992), received 23 Sep 1991, published 15 Jul 1992; DOI 10.1103/PhysRevD.46.603 (metadata confirmed via Crossref and the APS abstract page). Not on arXiv (no arXiv version located). Verified on 2026-09-26 via https://journals.aps.org/prd/abstract/10.1103/PhysRevD.46.603 (WebFetch returned a paraphrase only) and via the text layer of the published article as mirrored at https://archive.org/details/pdfy-rUc2KLIygUZjXGDb; quotes below are from that published text.
- **Design parts and knobs:** compactly generated Cauchy horizon; closed null geodesics on the horizon and their boost/area factors; initial surface (compact or non-compact); proximity of timelike curves to closure.
- **Knob → physics relations:**
  - [identity/theorem] Causality violation developing from a non-compact initial surface in a finite region without curvature singularities requires AWEC violation on the Cauchy horizon (abstract).
  - [derivation] Finite lengths of cosmic string cannot create CTCs (abstract).
  - [claim] Vacuum polarisation grows without bound as timelike curves approach closure; back-reaction prevents CTCs (abstract; Sec. I). The conjecture itself is a [claim].
  - [claim] Two-leg recipe: "You just have to travel from A to B faster than light would normally take. You then travel back, again faster than light, but in a different Lorentz frame. You can arrive back before you left." (Sec. I)
- **Method / verification standard:** global causal structure of compactly generated horizons; semiclassical stress-tensor estimates.
- **Scope and caveats:** compactly generated horizons; semiclassical estimates near the horizon; the chronology protection statement is conjectural.
- **Disputes, refutations, later corrections:** GO07 Theorem 3 replaces WEC/AWEC by self-consistent achronal ANEC; KO15 footnote cites Ori's non-compactly generated construction as an escape (not verified here).
- **Relation to active-rail results (where visible):** the "different Lorentz frame" clause is the design-relevant condition: a network whose superluminal legs all move forward in one frame's time does not satisfy it (see SS24 and the single-foliation derivation there).
- **Key quote:** "Even if violations of the weak energy condition are allowed by quantum theory, the expectation value of the energy-momentum tensor would get very large if timelike curves become almost closed. It seems the back reaction would prevent closed timelike curves from appearing." (abstract, published text)

### E96 — Allen E. Everett (1996), "Warp drive and causality"
- **Citation:** Phys. Rev. D 53, 7365–7368 (1996), received 14 Sep 1995, published 15 Jun 1996; DOI 10.1103/PhysRevD.53.7365 (Crossref). No arXiv version located. Verified on 2026-09-26 via https://journals.aps.org/prd/abstract/10.1103/PhysRevD.53.7365 (WebFetch, paraphrase) and via the text layer of the published article (PDF linked from https://www.if.ufrj.br/~mbr/warp/); quotes are from that text, with symbols garbled by the text layer rewritten.
- **Design parts and knobs:** bubble acceleration profile (uniform a over the first half of the trip, −a over the second); trip length D; boost parameter b between the two bubbles' rest frames; lateral separation y0 ≫ R between the two bubble paths.
- **Knob → physics relations:**
  - [derivation] Arrival time T = 2√(D/a); the ship beats light along the axis when a > 4/D (eq. 5).
  - [derivation] In a frame boosted by b, the arrival precedes departure (T′ < 0) when a > 4/(D b²) (eq. 7).
  - [derivation] A second bubble defined in the boosted frame, on a parallel path at lateral offset 2y0, returns the traveller at T1 ≈ −bD in the large-acceleration limit (eq. 9): a closed causal loop. Overlap of the two bubbles can be made arbitrarily small since y0 ≫ R.
  - [identity] A single bubble family in one frame has no loops: "for that space the forward light cone of an event at t = t0 includes only events with t > t0; signals can only be sent in one direction in t."
- **Method / verification standard:** explicit construction from Alcubierre's metric and Lorentz invariance of the exterior.
- **Scope and caveats:** assumes Alcubierre bubbles are realisable in every frame; superposes two metrics with negligible overlap.
- **Disputes, refutations, later corrections:** SS24 makes the construction explicit with compact, non-overlapping drives and a geodesic frame transition.
- **Relation to active-rail results (where visible):** loops need two shortcuts built in different rest frames. A rail network defined in one route frame, with both directions of travel moving forward in that frame's time, stays in the loop-free case the paper identifies.
- **Key quote:** "The spaceship beats the light signal to S2 not because its motion is spacelike but because, in effect, the bubble acts like a wormhole and provides a shortcut from S1 to S2." (text, p. 7366)

### SS24 — Barak Shoshany, Ben Snodgrass (2024), "Warp Drives and Closed Timelike Curves"
- **Citation:** Class. Quantum Grav. 41, 205005 (2024); DOI 10.1088/1361-6382/ad74d1; arXiv:2309.10072v3 (read version, 16 Sep 2024, "version published in Classical and Quantum Gravity"); submission history: v1 Mon, 18 Sep 2023 18:37:30 UTC; v2 Mon, 22 Apr 2024 18:03:01 UTC; v3 Mon, 16 Sep 2024 20:36:28 UTC. Verified via https://arxiv.org/abs/2309.10072 on 2026-09-26; full text read (Secs. 1–2.2, 4).
- **Design parts and knobs:** lapse N (spatially varying versus N(t)); shift β; compact support of each drive; relative velocity u of the two frames; drive speed v; shell where ∇β is large.
- **Knob → physics relations:**
  - [identity/theorem] With N = 1 (or N = N(t)) and flat (or any positive-definite) slices, Eulerian observers are geodesics and end at rest in the original frame: no geodesic rest-frame transition. "in order to find a metric allowing for a rest frame transition, we have no choice but to introduce spatial dependence into the lapse." (Sec. 2.1)
  - [derivation] Two compact, non-overlapping drives with a non-unit lapse, beginning and ending in different rest frames, give an explicit closed timelike geodesic (metric 3.5); illustrative values u ≈ 0.66, v ≈ 4 (Fig. 1 caption).
  - [identity] On flat slices with lapse N: ρ = (1/16πG)(1/N²)((∂_iβ^i)² − ∂_(iβ_j)∂^(iβ^j)) (eq. 4.3), and ∫N²ρ d³x ≤ 0 with strict inequality if β has curl, for β = O(r^{−1/2}) (eq. 4.8).
  - [claim] E_tot = ∫ρ d³x "can however be made arbitrarily small simply by making N large where ∇β is large", with the trade-off that matter in the shell experiences the journey longer by a factor of order N (Sec. 4.2).
  - [derivation] Case ρ = 0 with curl-free β: WEC ⇒ ∂_t∫K d³x ≤ 0 (eq. 4.29); a drive arising from flat space cannot re-flatten without violating WEC unless T_μν = 0 (Sec. 4.3).
  - [claim] Negative energy in these metrics is "a symptom of the choice of metric", not of superluminal travel (Sec. 4.2).
- **Method / verification standard:** ADM analysis; explicit metric; symbolic computation (OGRe, OGRePy).
- **Scope and caveats:** pointwise WEC only ("We do not prove violation of the pointwise null energy condition (NEC) as was done in [6], as the arguments therein do not readily extend to the case with N ≠ 1"); decay assumptions on β.
- **Disputes, refutations, later corrections:** disputes O98's definition (generic condition fails in Riemann-flat passenger regions; neighbouring paths equally fast; the definition makes all superluminal paths null).
- **Relation to active-rail results (where visible):**
  - (a) [derivation from eq. 4.3] For a pure shear shift β = β(x⊥)ẑ, ∂_iβ^i = 0 and ∂_(iβ_j)∂^(iβ^j) = ½|∇⊥β|², so ρ = −|∇⊥β|²/(32πN²): the project's result (a) with N = α. SS24's eq. 4.8 then gives ∫α²ρ d³x < 0.
  - (b) The lapse enters ρ only through 1/N² and enters the isotropic stress through ΔN/N (eq. 4.25): consistent with "stress without energy".
  - (d) The spatially varying lapse that sets the project's speed is exactly the ingredient SS24 identify as enabling geodesic frame transitions, hence CTC construction.
  - Chronology [derivation assembled here]: for any metric −N²dt² + γ_ij(dx^i − β^i dt)(dx^j − β^j dt) with N > 0 and γ positive definite on one global chart, g^{tt} = −1/N² < 0, so ∇t is timelike and t increases strictly along every future-directed causal curve; no closed causal curve exists. Loops need legs defined in different foliations (E96, ER97, SS24), or regions where t = const slices fail to be spacelike (ER97 Sec. 6). A rail network kept inside one global foliation with positive lapse is chronology-safe by construction; this is the design rule the chronology literature implies.
- **Key quote:** "that if they stayed in the reference frame of S, they must still move towards the future of S (i.e. towards increasing values of t), so time travel would be impossible." (Sec. 1.3)

---

## F. Recent applications to warp drives and older linearised constraints

### SSV22 — Jessica Santiago, Sebastian Schuster, Matt Visser (2022), "Generic warp drives violate the null energy condition"
- **Citation:** Phys. Rev. D 105, 064038 (2022); DOI 10.1103/PhysRevD.105.064038; arXiv:2105.03079v2 (read version, 25 Feb 2022, "closely resembles the final version accepted and in press at PRD"); submission history: v1 Fri, 7 May 2021 06:25:26 UTC; v2 Fri, 25 Feb 2022 23:32:51 UTC. Verified via https://arxiv.org/abs/2105.03079 on 2026-09-26; full text read (Secs. 2, 5, 7–8, App. B).
- **Design parts and knobs:** Natário class (unit lapse, flat slices, flow vector); decay of flow-field gradients at infinity; Eulerian observers crossing the wall; shift vorticity.
- **Knob → physics relations:**
  - [identity/theorem] NEC along Eulerian worldlines implies (3/2) dK/dτ ≤ −tr[K^tf]² ≤ 0 (eq. 7.33); an Eulerian observer that starts and ends in flat space while crossing a wall with nonzero trace-free extrinsic curvature forces NEC violation somewhere on its worldline (Sec. 7).
  - [identity] Zero-vorticity drives: Eulerian observers see zero flux, so the stress tensor is block diagonal and Hawking–Ellis Type I (Sec. 5).
  - [claim] Non-unit-lapse and non-flat-slice drives "cannot simply be dismissed out of hand" and "must be directly addressed using different techniques" (App. B).
- **Method / verification standard:** extrinsic-curvature monotonicity along Eulerian flow.
- **Scope and caveats:** unit lapse and flat slices; smooth, sufficiently localised flow (thin shells allowed).
- **Disputes, refutations, later corrections:** SS24 extends the WEC part to non-unit lapse; LE26 checks NEC violation numerically for four drives.
- **Relation to active-rail results (where visible):** (c) agrees with the zero-flux ⇒ Type I statement. The project's non-unit lapse places it outside this theorem's hypotheses; its own ANEC map supplies the NEC-violation location directly (on the axis ray inside the cone).
- **Key quote:** "all physically reasonable warp drives will violate the null energy condition, and so also automatically violate the WEC, and both the strong and dominant energy conditions." (abstract v2)

### LE26 — An T. Le (2026), "Observer-robust energy condition verification for warp drive spacetimes"
- **Citation:** no journal reference; arXiv:2602.18023v6 (read version, 24 Sep 2026); submission history: v1 Fri, 20 Feb 2026 06:37:44 UTC; v2 Tue, 3 Mar 2026 15:26:27 UTC; v3 Mon, 27 Apr 2026 02:12:02 UTC; v4 Fri, 12 Jun 2026 11:49:05 UTC; v5 Tue, 1 Sep 2026 03:44:20 UTC; v6 Thu, 24 Sep 2026 05:50:28 UTC. Six versions in seven months: content may still change. Verified via https://arxiv.org/abs/2602.18023 on 2026-09-26; full text read (abstract, Secs. 1, 3.5, 5–6).
- **Design parts and knobs:** bubble radius R_b; wall parameter σ; speed v_s; shift vorticity; QI sampling time τ0; null-vector normalisation.
- **Knob → physics relations:**
  - [identity/theorem] NEC, WEC, SEC as 4×4 linear matrix inequalities (S-lemma); DEC needs two such tests; no Hawking–Ellis type assumption or rapidity cap (abstract).
  - [identity/theorem] Unit lapse, flat slices, bounded vorticity: Eulerian momentum vanishes identically exactly for a gradient plus rigid rotation (abstract; Lemma 2).
  - [identity] For shifts linear in speed on fixed Euclidean slices, integrated negative Eulerian energy scales exactly as v_s² when finite (abstract).
  - [derivation] Flat-space Ford–Roman estimate on a coordinate-static wall worldline gives a threshold sampling time τ0^th ≃ c_metric √(ℓ_P R_b) (eq. 36); the author states the zero crossings "cannot be rescaled to macroscopic R_b".
  - [numerical] Global interval bounds establish NEC violation in all four benchmark walls (Alcubierre, Natário, Van den Broeck, Rodal); for Rodal "the Eulerian reading misses about 73% of the sampled wall weak-energy violations" (abstract).
  - [identity] ∫T(k,k)dλ scales by c under k → ck: the ANEC magnitude depends on the affine normalisation, its sign does not (Sec. 3.5).
- **Method / verification standard:** interval arithmetic certificates; JAX toolkit (Warpax); finite-segment ray integrals.
- **Scope and caveats:** the author's own limits: finite-segment integrals "supply no complete-geodesic ANEC conclusion", and "The flat-space quantum-inequality estimates likewise supply no curved-spacetime bound" (Sec. 6). Unit lapse, flat slices.
- **Disputes, refutations, later corrections:** questions GZ25's averaged satisfaction ("These divergence identities do not establish pointwise energy-condition satisfaction").
- **Relation to active-rail results (where visible):** (c) matches its momentum–Type I link for unit lapse; with a non-unit lapse the momentum constraint is weighted by 1/α [derivation from SS24's ADM expressions], so the project's zero-momentum statement lies outside Lemma 2's stated scope. The normalisation identity applies to the project's ANEC magnitudes (−202, −2.2×10⁴): the sign is invariant, the magnitude is set by the chosen affine normalisation.
- **Key quote:** "For shifts linear in speed, integrated negative Eulerian energy scales exactly quadratically when finite, with a fixed profile and integration domain on these slices." (abstract v6)

### JL26 — Kimet Jusufi, Francisco S. N. Lobo (2026), "Quantum-gravity-inspired Alcubierre warp-drive geometries"
- **Citation:** no journal reference; arXiv:2609.05554v1 (read version, 3 Sep 2026; abstract-level); submission history: v1 Thu, 3 Sep 2026 15:34:50 UTC (only version). Verified via https://arxiv.org/abs/2609.05554 on 2026-09-26.
- **Design parts and knobs:** profile scale l with l² = R² + l0² (zero-point length l0 = 2π√α′); speed v_s.
- **Knob → physics relations:** [derivation] E = −(15π/1024) v_s² l and |ρ_E| ≲ const·v_s²/l² (abstract): total negative energy linear in the profile scale, quadratic in speed; the R → 0 divergence at fixed speed is removed because l ≥ l0.
- **Method / verification standard:** closed-form ansatz (abstract-level).
- **Scope and caveats:** the abstract states "the construction is an effective ansatz rather than a derivation from string-corrected field equations" and "neither semiclassical stability nor a modified quantum energy inequality is claimed"; the thin-wall limit at fixed macroscopic radius is not regularised.
- **Disputes, refutations, later corrections:** none (single recent paper).
- **Relation to active-rail results (where visible):** the v_s² scaling agrees with LE26's exact v² law for speed-linear shifts; none visible for (g).
- **Key quote:** "Exotic matter remains necessary, and neither semiclassical stability nor a modified quantum energy inequality is claimed without an explicit renormalized stress-tensor calculation." (abstract v1)

### GZ25 — Remo Garattini, Kirill Zatrimaylov (2025), "Warp Drive in a De Sitter Universe"
- **Citation:** no journal reference; arXiv:2502.13153v4 (read version, 17 Jun 2026; abstract-level); submission history: v1 Fri, 14 Feb 2025 08:19:04 UTC; v2 Fri, 28 Feb 2025 14:18:06 UTC; v3 Fri, 12 Jun 2026 05:58:43 UTC; v4 Wed, 17 Jun 2026 12:46:42 UTC. The title on the abstract page is "Warp Drive in a De Sitter Universe" (search engines index it under an earlier title with "Positive–Energy"). Verified via https://arxiv.org/abs/2502.13153 on 2026-09-26.
- **Design parts and knobs:** background expansion rate; bubble radial velocity equal to the expansion speed.
- **Knob → physics relations:** [claim] under that velocity matching the bubble has non-negative energy density, with WEC and NEC "satisfied up to a total divergence term that averages to zero" (abstract).
- **Method / verification standard:** analytic (abstract-level).
- **Scope and caveats:** de Sitter background (not asymptotically flat); averaged statement only.
- **Disputes, refutations, later corrections:** LE26: divergence identities do not establish pointwise satisfaction.
- **Relation to active-rail results (where visible):** a non-asymptotically-flat background is one of the escape routes K24 lists for achronal-ANEC arguments; none visible otherwise.
- **Key quote:** "it is possible for the bubble to have strictly non--negative energy density, with the weak and null energy satisfied up to a total divergence term that averages to zero." (abstract v4)

### LV04 — Francisco S. N. Lobo, Matt Visser (2004), "Fundamental limitations on \"warp drive\" spacetimes"
- **Citation:** Class. Quantum Grav. 21, 5871–5892 (2004); DOI 10.1088/0264-9381/21/24/011; arXiv:gr-qc/0406083v2 (read version, 31 Oct 2004); submission history: v1 Mon, 21 Jun 2004 11:07:42 UTC; v2 Sun, 31 Oct 2004 13:32:19 UTC ("no physics changes"). Verified via https://arxiv.org/abs/gr-qc/0406083 on 2026-09-26; full text read (Secs. 2, 4).
- **Design parts and knobs:** bubble speed v; bubble radius R; wall inverse thickness σ (Δ = 1/σ); ship mass M_ship and size R_ship.
- **Knob → physics relations:**
  - [derivation] M_warp ≈ −v²R²σ (eq. 14): "the energy requirements for the warp bubble scale quadratically with bubble velocity, quadratically with bubble size, and inversely as the thickness of the bubble wall."
  - [derivation] Positive volume-integrated WEC with a finite-mass ship requires v² ≲ (M_ship/R_ship)(R_ship Δ/R²) (eq. 95).
  - [derivation] Localised NEC violations in the wall persist at arbitrarily low speed, independent of ship mass (Sec. 4).
- **Method / verification standard:** exact energy-condition evaluation plus linearised gravity to O(v²).
- **Scope and caveats:** unit-lapse Alcubierre and Natário forms; non-relativistic speeds.
- **Disputes, refutations, later corrections:** none found.
- **Relation to active-rail results (where visible):** the v² scaling is the weak-field counterpart of the project's shear-squared energy density (a); none visible for (g).
- **Key quote:** "For both the Alcubierre and Natario warp drives we find that the occurrence of significant energy condition violations is not just a high-speed effect, but that the violations persist even at arbitrarily low speeds." (abstract v2)

