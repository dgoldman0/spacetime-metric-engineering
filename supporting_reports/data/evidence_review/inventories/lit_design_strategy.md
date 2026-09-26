# Design strategy in the spacetime-engineering literature: a verified inventory

> **Errata (audit 2026-09-26, `../audit_synthesis.md` §5).**
> - BarzegarBuchert2025 entry, E.1 row 1 and E.4 row (a): the claim that 'the α⁻² design lever is the project's own' is contradicted by this file's own Shoshany–Snodgrass entry and E.2 row. Shoshany–Snodgrass 2024 §4.2 publish the lever (a large lapse where ∇β is large shrinks the Eulerian energy, at a time-stretch of order N for the source matter); Loup–Waite–Halerewicz 2001 (unrefereed) proposed it earlier (audit §1.2 R1).


Working inventory for the textbook (not book text). Compiled 2026-09-26.

## Purpose and standard

This inventory records published results that relate design parts, parameters or construction choices of warp drives, shortcut corridors and traversable wormholes to physical quantities: energy requirements and their scaling, where energy conditions fail, Hawking–Ellis type, horizons and causal structure, swept matter and blueshift, semiclassical stability, topology, ADM mass and momentum, and matter-model consistency.

Every entry was checked against the paper itself:

- arXiv entries: the abstract page was fetched and parsed directly (title, authors, comments, journal reference, DOI and the full submission history), and the version read is pinned. Where the full text was needed, the pinned PDF was converted with pdftotext and read; quotes are verbatim from that text or from the abstract of the stated version.
- Pre-arXiv or journal-only entries: the publisher page, Crossref record or ADS/INSPIRE record, as stated in each entry.
- "Abstract read" marks entries whose content beyond the abstract was not checked.
- UNVERIFIED marks anything that could not be confirmed, with the reason.

Tags on each knob → physics relation: **[identity/theorem]** (proved in general within stated hypotheses), **[derivation]** (derived for the stated construction), **[numerical]** (computed), **[claim]** (asserted without a derivation shown, or not checked here).

Version hazards found during verification (cite the pinned version):

- arXiv:2605.25417 — v1 (25 May 2026) and v2 (20 Jun 2026) are Le, "On the boundary cost of source-consistent warp shells"; v3 (17 Sep 2026) is a different paper, "Relativistic elastic shells: material support and cavity geometry".
- arXiv:2603.21352 — v1–v2 are Rodal, "Weakly birefringent screening disfavors fast Hawking–Ellis Type I warp drives via low-velocity cubic tilt scaling"; v3 (24 May 2026) is a Tamm–Rubilar/Drummond–Hathrell paper with the warp claim demoted to an appendix.
- arXiv:2606.22531 — v1–v3 "Steering a warp drive without exotic matter"; v4 (13 Sep 2026) "Radiative steering of warp shells", substantially revised with narrowed scope.
- arXiv:gr-qc/9511068 (Krasnikov) — v1–v5 are withdrawn placeholders; v6 (9 Mar 1998) is the paper.
- arXiv:gr-qc/9702026 (Pfenning & Ford) — v2 is a withdrawn placeholder; v1 and v3 carry the paper.
- arXiv:2512.20738 and 2512.19837 (Rodal) are 2025 postings of papers published in 2023 (GRG) and 2024 (IJTP).
- arXiv:gr-qc/0009013 (Alcubierre) was posted in 2000 for the 1994 paper.
- The "Barzegar, Buchert & Vigneron source-consistency critique" is arXiv:2602.16495 (three authors); arXiv:2407.00720 is the two-author Barzegar & Buchert paper (Universe 11, 293, 2025).

Project results compared against (labels used throughout; identity numbers I1–I26 refer to `knobs_one_space.md` §3):

- (a) = I1: on flat slices with a one-component shift, ρ = −(∂⊥β/α)²/32π, so only shift shear carries Eulerian energy.
- (b) = I2, I10: the lapse carries stress without energy.
- (c) = I2, I5c: zero Eulerian momentum ⇒ Hawking–Ellis Type I.
- (d) = I11: speed as a lapse contrast (speed-scaling isometry).
- (e) = I15: a moving conical front needs half-angle sin θ < 1/v.
- (f) = I12, I13: a front light surface traps overtaken light (white-hole-like front).
- (g) = I23: achronal ANEC excludes quantum sources for any lead over light.

## Contents

- Part A. Warp drives and shortcut corridors, 1994–2012
- Part B. Warp drives, 2020–2026
- Part C. Quantum inequalities, averaged null energy, superluminal censorship and chronology
- Part D. Traversable wormholes
- Part E. Synthesis table: knob/part × physics relation × papers × status
- Part F. Open disputes
- Part G. UNVERIFIED items

# Part A. Warp drives and shortcut corridors, 1994–2012

Labels used in the "Relation to active-rail results" fields:
(a) flat-slice identity ρ = −(∂⊥β/α)²/32π, so only shift shear carries Eulerian energy;
(b) the lapse carries stress without energy;
(c) zero Eulerian momentum ⇒ Hawking–Ellis Type I;
(d) speed as a lapse contrast;
(e) a moving conical front needs half-angle sin θ < 1/v;
(f) a front light surface traps overtaken light;
(g) achronal ANEC excludes quantum sources for any lead over light.

Full texts were read from pdftotext conversions of the pinned arXiv PDFs; abstract pages were read directly (HTML parsed, not summarized).

### Alcubierre1994 — Miguel Alcubierre (1994), "The warp drive: hyper-fast travel within general relativity"
- **Citation:** Class. Quantum Grav. 11, L73–L77 (1994). arXiv:gr-qc/0009013v1 (5 Sep 2000; the only version, posted six years after publication). Verified via https://arxiv.org/abs/gr-qc/0009013 and the v1 PDF, 2026-09-26.
- **Design parts and knobs:** unit lapse; flat slices; one-component shift β^x = −v_s(t) f(r_s); top-hat shape function f with radius R and steepness σ; trajectory x_s(t).
- **Knob → physics relations:**
  - Eulerian energy density T^{αβ}n_α n_β = −(1/8π)(v_s²ρ²/4r_s²)(df/dr_s)², ρ = (y²+z²)^{1/2}; negative wherever f′ ≠ 0 off-axis [derivation, eq. 19].
  - Expansion θ = v_s (x_s/r_s) df/dr_s: expansion behind, contraction in front [derivation, eq. 12].
  - Ship worldline: dτ = dt and geodesic, so zero time dilation and zero proper acceleration for any v_s(t) [derivation, eq. 13].
  - Large σ gives small tidal forces near the ship; tidal forces are large at r_s ≈ R [claim, qualitative].
  - With 3+1 form and positive-definite γ_ij, the spacetime is globally hyperbolic and has no closed causal curves [claim, stated].
- **Method / verification standard:** analytic, reverse-engineered metric (metric first, Einstein tensor gives the demand); only Eulerian energy density evaluated.
- **Scope and caveats:** test-particle ship; the WEC/DEC/SEC violation is shown for Eulerian observers only; time-dependent v_s(t) is postulated.
- **Disputes, refutations, later corrections:** the time-dependent-velocity form was called an energy-conservation error by Bobrick & Martire 2021 §5.2; Santiago, Schuster & Visser 2022 (App. A) and Barzegar, Buchert & Vigneron 2026 (Error 14) reject that criticism because the Bianchi identity enforces conservation of the reverse-engineered tensor. Everett & Roman 1997 and Krasnikov 1998 show the ship cannot create or steer a superluminal bubble.
- **Relation to active-rail results:** eq. (19) is exactly (a) at α = 1: β^x = −v f gives |∂⊥β|² = v²f′²ρ²/r_s², and −|∂⊥β|²/32π reproduces eq. (19). The expansion θ drops out of ρ, as (a) states.
- **Key quote:** "The fact that this expression is everywhere negative implies that the weak and dominant energy conditions are violated." (v1, after eq. 19)

### Hiscock1997 — William A. Hiscock (1997), "Quantum effects in the Alcubierre warp drive spacetime"
- **Citation:** Class. Quantum Grav. 14, L183–L188 (1997). arXiv:gr-qc/9707024v1 (10 Jul 1997; only version). Verified via abstract page, 2026-09-26.
- **Design parts and knobs:** apparent (global) speed of the bubble relative to c; 1+1 reduction.
- **Knob → physics relations:** the expectation value of the stress tensor of a conformal scalar diverges once the apparent speed exceeds c (horizon formation) [derivation in 1+1].
- **Method / verification standard:** analytic, 1+1-dimensional, eternal constant-speed bubble.
- **Scope and caveats:** 2D reduction; four-dimensional behaviour conjectured.
- **Disputes:** extended by Clark–Hiscock–Larson 1999 (4D horizons) and Finazzi–Liberati–Barceló 2009 (dynamical creation); González-Díaz 2000 finds a non-divergent vacuum under a Misner-space extension; Barceló et al. 2022 argue the 2+1 and higher instability is confined to isolated points.
- **Relation to active-rail results:** supports (f): the divergence sits at the horizon that superluminal apparent speed creates; a design with no front horizon avoids this mechanism.
- **Key quote:** "The stress-energy is found to diverge if the apparent velocity of the spaceship exceeds the speed of light." (abstract v1)

### PfenningFord1997 — Michael J. Pfenning, L. H. Ford (1997), "The unphysical nature of 'Warp Drive'"
- **Citation:** Class. Quantum Grav. 14, 1743–1751 (1997). arXiv:gr-qc/9702026v3 (15 Mar 2001); history v1 13 Feb 1997, v2 20 Mar 1997 (withdrawn placeholder), v3 15 Mar 2001. Read v3. Verified 2026-09-26.
- **Design parts and knobs:** wall thickness Δ (Δ ≃ 2/σ), bubble radius R, speed v_b; QI sampling time t₀ = α(2Δ/√3 v_b), α ≪ 1.
- **Knob → physics relations:**
  - Flat-space Ford–Roman QI applied over sampling times below the local curvature radius r_min ~ 2Δ/(√3 v_b) gives Δ ≤ (3/4)√(3 v_b/π α²) (Planck units), i.e. Δ ≤ 10² v_b L_Planck for α = 1/10 [derivation, eqs. 20–23].
  - Total Eulerian energy E = −(1/12) v_b² (R²/Δ + Δ/12) [derivation, eq. 28]: E ∝ v²R²/Δ.
  - With the QI wall, E ≤ −6.2×10⁷⁰ v_b L_Planck ~ −6.2×10⁶⁵ v_b g for R = 100 m [numerical estimate, eq. 29]; a 1 m wall gives about a quarter solar mass; R = one electron Compton wavelength gives E ~ −400 M_sun [estimate].
  - Raising v_b allows a thicker wall but raises |E| by the same factor [derivation, §5].
  - Massive scalar QI is more restrictive; the electromagnetic field relaxes Δ by √2 [claim from cited QIs].
- **Method / verification standard:** analytic, flat-space QI for a massless scalar applied locally; order-of-magnitude integration with a piecewise-linear shape function.
- **Scope and caveats:** assumes the negative energy comes from a free quantum field obeying the flat-space QI; the curvature-radius argument is heuristic; Eulerian energy only.
- **Disputes:** Krasnikov 2003 ("The quantum inequalities do not forbid spacetime shortcuts", covered in the QI cluster) disputes the applicability; Van Den Broeck 1999 evades the energy estimate by decoupling surface area from interior volume; Bobrick & Martire 2021 construct flattened superluminal drives meeting the QI and note they still violate ANEC.
- **Relation to active-rail results:** E ∝ v²/Δ is the volume integral of (a) for a thin wall. The QI verdict concerns local magnitude; (g) is a global condition independent of wall thickness (Bobrick & Martire 2021 §4.2 make the same distinction).
- **Key quote:** "It will be shown that the bubble wall thickness is on the order of only a few hundred Planck lengths." (abstract v3)

### EverettRoman1997 — Allen E. Everett, Thomas A. Roman (1997), "A Superluminal Subway: The Krasnikov Tube"
- **Citation:** Phys. Rev. D 56, 2100 (1997). arXiv:gr-qc/9702049v1 (25 Feb 1997; only version). Verified 2026-09-26.
- **Design parts and knobs:** 4D Krasnikov tube: tube length D, radius ρ_max, wall thickness ε, light-cone opening η = 2 − δ (k = 1 − η inside), negative-energy band width Δρ = αε.
- **Knob → physics relations:**
  - The centre of an Alcubierre bubble is spacelike-separated from the outer front wall: a forward photon stalls where dx/dt = v inside the wall, so the crew can neither create nor control a superluminal bubble; the bubble must be arranged beforehand by an observer whose forward light cone contains the whole trajectory [derivation, §2].
  - One tube: no CTCs; two non-overlapping tubes: a time machine [derivation].
  - QI applied to static observers in the wall: ε ≲ 10⁴ l_P for σ ≈ 0.01 [derivation, eqs. 44–45].
  - Negative energy E ≈ −αρ_max D/ε; for D = ρ_max = 1 m, E ≈ −α 10¹⁸ M_galaxy; for D ≈ 4×10¹⁶ m, E ≈ −10³² M_galaxy [estimate, eqs. 51–52].
  - Trade-off: wall energy density ∝ η/ε²; the QI with τ₀ = ε ≈ 1 cm is met only for η ≈ l_P²ε²/τ₀⁴ ≈ 10⁻⁶⁶, and the backward light speed inside then exceeds 1 by one part in 10⁶⁶ [derivation, §6].
- **Method / verification standard:** analytic; QI on a static observer inside the wall; order-of-magnitude.
- **Scope and caveats:** thin-wall estimates; positive energy on the outer side of the wall is ignored in the total (they argue exact cancellation is implausible).
- **Further knob relations (from the QI/causality review):** a network of tubes avoids CTCs only if "there existed a preferred axis such that all the Krasnikov tubes were oriented so that the velocity components along that axis of objects in superluminal motion were always positive" (Sec. 4) [claim]; "The t = const slices of the Krasnikov spacetime are not everywhere spacelike" (Sec. 6); a thick tube needs ρ_max ≲ ℓ_P/σ² (eq. 46) [derivation]; the fractional lead a QI-limited wall can buy scales as η ~ (ℓ_P/ε)² [derivation in this inventory, from Sec. 6].
- **Disputes:** Krasnikov 2003 contests the QI argument (Part C, K03).
- **Relation to active-rail results:** the causal-disconnection argument is the literature form of the project's choreography rule (the carrying structure is laid down in advance along the route). The η–ε trade-off is a local-QI statement that leaves room for an arbitrarily small lead over light; (g), if achronal ANEC holds, removes even that room. This is the sharpest literature contrast for (g).
- **Key quote:** "Photons emitted in the forward direction by the spaceship never reach the outside edge of the bubble wall, which therefore lies outside the forward light cone of the spaceship." (§2)

### Krasnikov1998 — S. V. Krasnikov (1998), "Hyperfast Interstellar Travel in General Relativity"
- **Citation:** Phys. Rev. D 57, 4760–4766 (1998). arXiv:gr-qc/9511068v6 (9 Mar 1998); v1–v5 withdrawn placeholders (1995–1997). Read v6. Verified 2026-09-26.
- **Design parts and knobs:** the traveller's ability to alter the metric only within J⁺(S) ("utter causality"); one-way versus round trip; light-cone opening in a pre-built corridor (2D metric ds² = −(dt − dx)(dt + k dx)).
- **Knob → physics relations:**
  - Proposition 1: in globally hyperbolic spacetimes that differ only in the causal future of the launch event S, the traveller cannot reach the destination sooner than light would [theorem, proof in appendix].
  - The return leg can be made arbitrarily short by a corridor built on the outbound leg (the "Krasnikov tube") [construction].
  - Such "space machines" are square roots of time machines; two of them yield CTCs; those leading to compactly generated Cauchy horizons require WEC violation [claim citing Hawking's theorem].
- **Method / verification standard:** causal-structure theorems; explicit 2D examples.
- **Scope and caveats:** 2D examples; energy estimates deferred to Everett & Roman 1997.
- **Disputes:** Barzegar, Buchert & Vigneron 2026 (Remark IV.11) cite Krasnikov for the statement that a globally hyperbolic superluminal Natário-class drive must be superluminal from the start.
- **Relation to active-rail results:** Proposition 1 is the literature basis of the project's causality rule: any lead over light needs structure placed along the route in advance by subluminal means. It says nothing about energy conditions, which (g) addresses.
- **Key quote:** "It is argued that under some reasonable assumptions in globally hyperbolic spacetimes the traveller cannot hasten reaching the destination." (abstract v6)

### VanDenBroeck1999 — Chris Van Den Broeck (1999), "A 'warp drive' with more reasonable total energy requirements"
- **Citation:** Class. Quantum Grav. 16, 3973–3979 (1999). arXiv:gr-qc/9905084v5 (21 Sep 1999); v1 21 May, v2 1 Jun, v3 16 Jun, v4 17 Jun, v5 21 Sep 1999. Read v5. Verified 2026-09-26.
- **Design parts and knobs:** a conformal "pocket" factor B(r_s) on the spatial metric, ds² = −dt² + B²[(dx − v_s f dt)² + dy² + dz²]; expansion factor 1 + α; pocket radius R̃ and transition width Δ̃; outer bubble radius R and wall Δ; polynomial order n of B.
- **Knob → physics relations:**
  - Decoupling of external surface area from internal volume: outer radius 3×10⁻¹⁵ m, inner diameter 200 m with α = 10¹⁷ [construction, eq. 7].
  - Wall region IV keeps the Pfenning–Ford form: E_IV ≃ −6.3×10²⁹ v_s kg [derivation, eq. 9].
  - Pocket region II (uniform shift, f = 1, so shift-free in the bubble frame; curved slices): Eulerian density (1/8π)[(∂_rB)²/B⁴ − 2∂_r²B/B³ − 4∂_rB/(rB³)]; E_II,− = −1.4×10³⁰ kg and E_II,+ = +4.9×10³⁰ kg ("a few solar masses") [numerical, eqs. 11–16].
  - Choice n = 80 maximizes the minimum curvature radius (≈ 1.4×10⁻³⁴ m, ten Planck lengths); low-order B gives sub-Planck curvature radii [numerical].
  - QI satisfied for Eulerian observers with τ₀ = 0.1 r_c,min [numerical check].
- **Method / verification standard:** analytic plus 1D quadrature; Eulerian observers only.
- **Scope and caveats:** structures near the Planck scale; energy densities remain enormous (author's own caveat); stellar-mass energies.
- **Disputes:** Bobrick & Martire 2021 note spherically symmetric drives cannot enclose objects larger than the drive; Warp Factory 2024 and Le 2026b find WEC/NEC violations and Type IV in its wall (Le: Type-IV wall fraction crosses 50% at v_s ≈ 0.38).
- **Relation to active-rail results:** region IV is (a); region II carries energy through spatial curvature ³R under a uniform shift, which lies outside (a)'s flat-slice scope and illustrates that curved slices add a second energy channel.
- **Key quote:** "We will solve the problem of the large negative energy by keeping the surface area of the warp bubble itself microscopically small, while at the same time expanding the spatial volume inside the bubble." (§2)

### ClarkHiscockLarson1999 — Chad Clark, William A. Hiscock, Shane L. Larson (1999), "Null geodesics in the Alcubierre warp drive spacetime: the view from the bridge"
- **Citation:** Class. Quantum Grav. 16, 3965–3972 (1999). arXiv:gr-qc/9907019v1 (6 Jul 1999; only version). Verified 2026-09-26.
- **Design parts and knobs:** effective speed v_s; wall shape.
- **Knob → physics relations:** for v_s > 1, a conical region behind forms from which no signal reaches the ship, and a conical region in front that the ship cannot signal ("Mach cones"); forward stars appear aberrated toward the direction of motion [numerical, null-geodesic integration].
- **Method / verification standard:** numerical geodesic integration in 4D.
- **Scope and caveats:** eternal constant-speed bubble.
- **Disputes:** refined analytically by Natário 2002 (thin-wall refraction, sin α = 1/v).
- **Relation to active-rail results:** the front cone is the horizon that (e) avoids: a front whose normal speed stays below c forms no such cone.
- **Key quote:** "Behind the starship, a conical region forms from within which no signal can reach the starship, an effective 'horizon'." (abstract v1)

### GonzalezDiaz2000 — Pedro F. González-Díaz (2000), "On the warp drive space-time"
- **Citation:** Phys. Rev. D 62, 044005 (2000) (DOI 10.1103/PhysRevD.62.044005). arXiv:gr-qc/9907026v2 (10 Apr 2000); v1 7 Jul 1999. Verified via abstract page 2026-09-26.
- **Design parts and knobs:** maximal extension of the 2D superluminal warp spacetime (Misner-space embedding).
- **Knob → physics relations:** the extended interior is a nonchronal region with CTCs; in the chosen vacuum the RSET stays finite on the chronology horizon; CTCs are confined to near-Planck scales [claim, 2D].
- **Method:** analytic, 2D.
- **Scope and caveats:** depends on the chosen extension and vacuum; 2D.
- **Disputes:** stands against Hiscock 1997 on the divergence; later dynamical analysis (Finazzi et al. 2009) finds instability.
- **Relation to active-rail results:** none visible beyond the general point that the semiclassical verdict depends on the global extension and state.
- **Key quote:** "the most natural vacuum allows quantum fluctuations which do not induce any divergent behaviour of the re-normalized stress-energy tensor, even on the event (Cauchy) chronology horizon." (abstract v2)

### LoupWaiteHalerewicz2001 — F. Loup, D. Waite, E. Halerewicz Jr (2001), "Reduced Total Energy Requirements for a Modified Alcubierre Warp Drive Spacetime"
- **Citation:** arXiv-only preprint, arXiv:gr-qc/0107097v2 (3 Nov 2001); v1 30 Jul 2001. No journal reference found. Verified via abstract page 2026-09-26.
- **Design parts and knobs:** a lapse function A(ct, r_s) added to the Alcubierre metric.
- **Knob → physics relations:** the lapse is claimed to reduce the negative energy requirement "arbitrarily as a function of A" [claim, unrefereed].
- **Method:** analytic, Eulerian density.
- **Scope and caveats:** unrefereed; energy measured by Eulerian observers only; the proposed superluminal control scheme is called a "pseudo method" by the authors.
- **Disputes:** none found in print; the claim is superseded in structure by the lapse-weighted integral of Shoshany & Snodgrass 2024 (∫N²ρ d³x ≤ 0).
- **Relation to active-rail results:** consistent with (a): Eulerian ρ scales as 1/α² at fixed shift gradient, so a large lapse in the wall lowers |ρ|. The invariant content is α²ρ, which the lapse leaves unchanged; this is also the mechanism behind (d), where α and β scale together and the local tensor is unchanged.
- **Key quote:** "negative energy requirements within the Alcubierre spacetime can be greatly reduced when one introduces a lapse function into the Einstein tensor." (abstract v2)

### Natario2002 — José Natário (2002), "Warp Drive With Zero Expansion"
- **Citation:** Class. Quantum Grav. 19, 1157–1166 (2002). arXiv:gr-qc/0110086v3 (13 Mar 2002); v1 19 Oct 2001, v2 6 Nov 2001. Read v3. Verified 2026-09-26.
- **Design parts and knobs:** arbitrary shift vector field X on flat slices with unit lapse (the "Natário class"); divergence-free choice X ∝ curl of a potential; wall thickness in the thin-wall optics limit.
- **Knob → physics relations:**
  - K = ½(∂_iX_j + ∂_jX_i); expansion θ = ∇·X is a free design choice; zero expansion is achievable [derivation, Cor. 1.5, §2].
  - Eulerian energy ρ = (1/16π)(θ² − K_ijK^ij); Theorem 1.7: every non-flat warp spacetime of this class violates the WEC or the SEC [theorem].
  - Zero-expansion drive: ρ = −(v_s²/8π)[3(f′)²cos²θ + (f′ + r f″/2)² sin²θ] ≤ 0 [derivation].
  - Stationarity requires |v_s| < 1 because ⟨∂_t,∂_t⟩ = −1 + |X|² [derivation].
  - For v_s > 1 the surface through the point where |X| = 1 with angle sin α = 1/|X| to X is a horizon; far from the bubble sin α = 1/v_s, the Mach angle [derivation, §3].
  - Energy of a particle measured by Eulerian observers obeys E(1 + X·n) = E₀: forward light seen from the centre is blueshifted by 1 + v_s; light sent toward the horizon is blueshifted without bound [derivation].
- **Method / verification standard:** analytic.
- **Scope and caveats:** constant velocity for the optics; thin-wall refraction.
- **Disputes:** Rodal 2024 (IJTP) finds Natário curvature invariants 35 times larger than Alcubierre's at matched parameters and establishes Petrov type I; Barzegar, Buchert & Vigneron 2026 restate Theorem 1.7 as their Theorem IV.31.
- **Relation to active-rail results:** confirms (a) (θ cancels from ρ for one-component shifts) and supplies the geometry behind (e): the horizon is the Mach cone sin α = 1/v, so a moving front whose half-angle satisfies sin θ < 1/v advances along its normal slower than light and forms no horizon. The unbounded blueshift toward the horizon is the mechanism of (f).
- **Key quote:** "Notice that away from the warp bubble we have sin α = 1/v_s which is the familiar expression for the Mach cone angle." (§3)

### LoboVisser2004 — Francisco S. N. Lobo, Matt Visser (2004), "Fundamental limitations on 'warp drive' spacetimes"
- **Citation:** Class. Quantum Grav. 21, 5871–5892 (2004), DOI 10.1088/0264-9381/21/24/011. arXiv:gr-qc/0406083v2 (31 Oct 2004; "no physics changes"); v1 21 Jun 2004. Read v2. Verified 2026-09-26.
- **Design parts and knobs:** bubble speed v, radius R, wall steepness σ (Δ = 1/σ), ship mass M_ship and size R_ship, weak-field order.
- **Knob → physics relations:**
  - Exact: WEC and NEC violated at all speeds; Eulerian density −(v²/32π)[(∂_xf)² + (∂_yf)²] [derivation, eq. 10].
  - "Volume integral quantifier": M_warp = ∫ρ d³x ≈ −v²R²σ, "quadratically with bubble velocity, quadratically with bubble size, and inversely as the thickness of the bubble wall" [derivation plus estimate, eqs. 13–14].
  - NEC contains a term linear in v that dominates at low speed, so NEC fails at arbitrarily low speed; its volume integral vanishes and the net NEC violation is O(v²) [derivation, eqs. 15–20].
  - Linearized theory with a finite-mass ship: T₀ᵢ = O(v), Tᵢⱼ = O(v²); requiring positive integrated WEC gives v²R²σ ≲ M_ship, i.e. v² ≲ (M_ship/R_ship)(R_ship Δ/R²) [derivation, eqs. 94–95].
  - The ADM mass of the Alcubierre geometry is zero, so the warp-field energy must cancel the ship's mass [argument, §II].
  - The drive is a "reaction-less drive" in the weak-field regime [claim/interpretation].
- **Method / verification standard:** exact Einstein tensor; linearized gravity to first and second order in v.
- **Scope and caveats:** volume integrals of Eulerian quantities; ship modelled as a Newtonian source.
- **Disputes:** Barzegar, Buchert & Vigneron 2026 (Error 5) criticize the use of ADM-mass language descending from this paper.
- **Relation to active-rail results:** eq. (10) is (a) at α = 1. The O(v) NEC term comes from the Eulerian momentum flux, which is the quantity whose vanishing gives (c). The v² scaling of the energy is the scaling of (a) under β ∝ v.
- **Key quote:** "Note that the energy requirements for the warp bubble scale quadratically with bubble velocity, quadratically with bubble size, and inversely as the thickness of the bubble wall." (§II)

### Natario2006 — José Natário (2006), "Newtonian limits of warp drive spacetimes"
- **Citation:** Gen. Relativ. Gravit. 38, 475–484 (2006). arXiv:gr-qc/0408085v3 (7 Oct 2009); v1 25 Aug 2004, v2 28 Feb 2005 ("major changes"). Verified via abstract page 2026-09-26 (abstract only read).
- **Design parts and knobs:** a class of warp drives with Newtonian limits.
- **Knob → physics relations:** existence of a Newtonian limit for a subclass [claim, abstract level].
- **Scope:** abstract-level entry; content beyond the abstract UNVERIFIED.
- **Relation to active-rail results:** none visible at abstract level.
- **Key quote:** "We find a class of warp drive spacetimes possessing Newtonian limits, which we then determine." (abstract v3)

### FinazziLiberatiBarcelo2009 — Stefano Finazzi, Stefano Liberati, Carlos Barceló (2009), "Semiclassical instability of dynamical warp drives"
- **Citation:** Phys. Rev. D 79, 124017 (2009). arXiv:0904.0141v2 (14 Jul 2009); v1 1 Apr 2009. Read v2. Verified 2026-09-26.
- **Design parts and knobs:** superluminal speed (horizon formation), wall thickness Δ (sets the surface gravity κ ~ c/Δ), creation from flat space, duration of superluminal operation.
- **Knob → physics relations:**
  - A superluminal bubble created from flat space forms a black horizon at the rear wall and a white horizon at the front wall [derivation, 1+1].
  - Interior observers receive a Hawking flux at T_H ~ κ; with the QI wall (Δ ≲ 10² L_P), T_H ≳ 10⁻² T_P; with Δ ~ 1 m, T ~ 0.003 K [estimate].
  - The RSET grows exponentially on and near the front (white) horizon on a time scale 1/κ ≈ Δ/c; a 1 s time scale needs Δ ≈ 3×10⁸ m [derivation].
  - Subluminal bubbles form no horizons, no Hawking flux and no white-horizon instability [statement].
- **Method / verification standard:** RSET of a massless field in 1+1 (s-wave-like), geometric optics; analytic with a kinked dynamical profile.
- **Scope and caveats:** 1+1 dimensions; the 3+1 extension is argued for an open set around the axis.
- **Disputes:** Barceló, Boyanov, Garay, Martín-Martínez & Sánchez Velázquez 2022 ("Warp drive aerodynamics") argue that in 2+1 and higher dimensions the infinite-blueshift set shrinks to isolated points, which weakens the instability; Coutant et al. 2012 find the instability survives UV Lorentz violation.
- **Relation to active-rail results:** supports (f): overtaken light accumulating at the front surface is the white-horizon mechanism, and the front wall is where the semiclassical instability lives. It also supports the design value of (e), which removes the front horizon.
- **Key quote:** "Most of all, we find that the RSET will exponentially grow in time close to, and on, the front wall of the superluminal bubble." (abstract v2)

### BarceloFinazziLiberati2010 — Carlos Barceló, Stefano Finazzi, Stefano Liberati (2010), "On the impossibility of superluminal travel: the warp drive lesson"
- **Citation:** FQXi essay (second prize, 2009 contest); arXiv:1001.4960v1 (27 Jan 2010; only version); no journal reference. Verified via abstract page 2026-09-26.
- **Knob → physics relations:** restates the 2009 result for a general audience: back-reaction destabilizes bubbles "whenever superluminal speeds are attained" [claim, summary].
- **Relation to active-rail results:** as for Finazzi et al. 2009.
- **Key quote:** "the quantum back-reaction to warp-drive geometries, created out of an initially flat spacetime, inevitably lead to their destabilization whenever superluminal speeds are attained." (abstract v1)

### CoutantFinazziLiberatiParentani2012 — Antonin Coutant, Stefano Finazzi, Stefano Liberati, Renaud Parentani (2012), "Impossibility of superluminal travel in Lorentz violating theories"
- **Citation:** Phys. Rev. D 85, 064020 (2012). arXiv:1111.4356v2 (11 Apr 2012); v1 18 Nov 2011. Verified via abstract page 2026-09-26.
- **Design parts and knobs:** UV dispersion relation of the quantum field (subluminal or superluminal dispersion).
- **Knob → physics relations:** dispersion regulates the UV divergence yet the drive stays unstable: subluminal dispersion gives a black-hole-laser exponential amplification, superluminal dispersion a linear growth of the flux [derivation/numerical].
- **Method:** mode analysis on a 1+1 warp background.
- **Scope:** 1+1 dimensions.
- **Relation to active-rail results:** strengthens (f)-type concerns: the front-wall blueshift problem persists under modified dispersion.
- **Key quote:** "Interestingly, even though the ultraviolet divergence is now regulated, warp drives are still unstable." (abstract v2)

### McMonigalLewisOByrne2012 — Brendan McMonigal, Geraint F. Lewis, Philip O'Byrne (2012), "The Alcubierre Warp Drive: On the Matter of Matter"
- **Citation:** Phys. Rev. D 85, 064024 (2012). arXiv:1202.5708v1 (26 Feb 2012; only version). Read v1. Verified 2026-09-26.
- **Design parts and knobs:** ship speed v_s (sub- and superluminal), particle initial velocity v_p, bubble acceleration and deceleration history.
- **Knob → physics relations:**
  - Constant-velocity bubble: particles in regions N±, B+ are blueshifted by b = 1 − v_s v_p at the ship and exit with their original energy [numerical + analytic].
  - Particles overtaken from ahead (region P+, positive v_p, superluminal bubble) acquire extreme blueshift and become "time locked" in the bubble [numerical].
  - Acceleration boosts particles inside the bubble; boost magnitude scales with the acceleration; Eulerian matter is unaffected [numerical].
  - Deceleration from superluminal speed releases a concentrated beam of extremely high-energy particles ahead of the ship [numerical].
- **Method / verification standard:** numerical geodesic integration (Matlab ode23s/ode45) with 4-velocity normalization as an accuracy check.
- **Scope and caveats:** test particles; Alcubierre profile only; no back-reaction.
- **Disputes:** none found.
- **Relation to active-rail results:** direct literature support for (f) and for the project's accounting of what a moving structure overtakes: overtaken forward-moving matter is trapped at the front and released with large blueshift at stops.
- **Key quote:** "any ship using an Alcubierre warp drive carrying people would need shielding to protect them from potential dangerously blueshifted particles during the journey, and any people at the destination would be gamma ray and high energy particle blasted into oblivion due to the extreme blueshifts for P+ region particles." (§IV)

# Part B. Warp drives, 2020–2026

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

# Part C. Quantum inequalities, averaged null energy, superluminal censorship and chronology

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

## C.1 Quantum inequalities along timelike worldlines

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
- See Part D, FordRoman1996 (field-number scaling and the redshift escape route merged there).

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
- See Part A, EverettRoman1997 (QI and network-orientation details merged there).

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

## C.2 Superluminal travel, time delay and speed-limit theorems

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
- See Part D, FriedmanSchleichWitt1993 (full text read there: the theorem assumes ANEC).

## C.3 ANEC, achronal ANEC and their proofs

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

## C.4 Null-segment bounds (no-go, SNEC, DSNEC, QNEIs) and QEI reviews

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

## C.5 Chronology

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
- See Part B, ShoshanySnodgrass2024 (lapse identities and chronology details merged there).

## C.6 2018–2026 applications to warp drives and shortcuts, and older weak-field constraints

**Search record (2026-09-26).** WebSearch queries covered QI or SNEC bounds on warp drives, QI bounds on wall thickness, ANEC along bubble-crossing geodesics, and SNEC or DSNEC applied to warp drives or wormholes. No paper applying SNEC or DSNEC to a warp drive or rail was located. Located and verified: SNEC/DSNEC applied to the Maldacena–Milekhin–Popov long wormhole (FKK22, K24); flat-space QI estimates and finite-segment null integrals for four warp geometries (Le26); a Planck-regularized warp profile (JL26); an averaged-condition claim for a de Sitter-embedded bubble (GZ25).

### SSV22 — Jessica Santiago, Sebastian Schuster, Matt Visser (2022), "Generic warp drives violate the null energy condition"
- See Part B, SSV2022 (NEC monotonicity proof merged there).

### Le26 — An T. Le (2026), "Observer-robust energy condition verification for warp drive spacetimes"
- See Part B, Le2026b (QI threshold and ANEC normalization identity merged there).

### JL26 — Kimet Jusufi, Francisco S. N. Lobo (2026), "Quantum-gravity-inspired Alcubierre warp-drive geometries" (abstract-level)
- See Part B, JusufiLobo2026.

### GZ25 — Remo Garattini, Kirill Zatrimaylov (2025), "Warp Drive in a De Sitter Universe" (abstract-level)
- See Part B, GarattiniZatrimaylov2024_2025.

### LV04 — Francisco S. N. Lobo, Matt Visser (2004), "Fundamental limitations on 'warp drive' spacetimes"
- See Part A, LoboVisser2004.

## C.7 Assessment of project claim (g)

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

# Part D. Traversable wormholes


Cluster: traversable wormholes. Compiled 2026-09-26.

## Verification method and conventions

- **arXiv papers.** Each abstract page `https://arxiv.org/abs/<id>` was fetched directly over HTTP on 2026-09-26 and parsed from the page HTML (`citation_title`/`citation_author` meta tags, the abstract block, the "Journal reference" cell, the DOI meta tag, and the "Submission history" block). The full text was then downloaded at the pinned version from `https://arxiv.org/pdf/<id>v<N>` and converted with `pdftotext`; every full-text quote below is copied from that conversion. The pinned version is the latest version listed on 2026-09-26. Where the arXiv page carries no journal reference, the publication data come from the INSPIRE-HEP API record (`https://inspirehep.net/api/literature?q=arxiv:<id>`), fetched the same day and labelled as such.
- **Pre-arXiv papers.** Title, authors, publication data and abstract come from the INSPIRE-HEP API record looked up by DOI (abstract text supplied there by APS/AIP). Full text: Morris & Thorne 1988 from a scanned copy of the AJP PDF hosted at `https://materias.df.uba.ar/rga2019c2/files/2019/11/MT.pdf`; Morris, Thorne & Yurtsever 1988 from Caltech AUTHORS (`https://authors.library.caltech.edu/records/m644f-tbz27`, file `MORprl88.pdf`). Both are image scans, so their text was read through `tesseract` OCR. Prose quotes from them are reliable, while formulas are given in cleaned form and flagged "(OCR-cleaned)". Hawking 1992 and Kim & Thorne 1991 were checked at abstract level only.
- **Tags.** [identity/theorem] = holds as an identity or proven theorem inside the paper's assumptions; [derivation] = derived explicitly in the text; [numerical] = obtained numerically; [claim] = asserted without a full derivation in the paper, or not checked here.
- **Notation.** Static spherically symmetric (Morris–Thorne) form: ds² = −e^{2Φ(r)}dt² + dr²/(1 − b(r)/r) + r²dΩ². b = shape function, Φ = redshift function, so e^{Φ} is the lapse of the static slicing. The throat sits at r₀ = b(r₀). ρ = energy density, τ = radial tension = −p_r, p or p_t = lateral pressure. All components are measured by static observers in the static orthonormal frame, where the stress tensor is diagonal.

---

## D.1 Foundations: metric-first design of static wormholes

### MorrisThorne1988 — M. S. Morris, K. S. Thorne (1988), "Wormholes in spacetime and their use for interstellar travel: A tool for teaching general relativity"
- **Citation:** Am. J. Phys. 56, 395–412 (1988); DOI 10.1119/1.15620. Pre-arXiv. Verified via INSPIRE API (`q=doi:10.1119/1.15620`) and the full-text scan listed above (19 pages OCR'd) on 2026-09-26. INSPIRE lists the title as "…in space-time…"; the article page reads "Wormholes in spacetime…".
- **Design parts and knobs:** shape function b(r) and throat radius b₀; redshift function Φ(r), with Φ′ = 0 giving the "zero-tidal-force" class; the traveller's speed profile v(r) and the positions of the start and end stations ±l₁; an optional radial cutoff R_s of the source with a transition layer of thickness ΔR; the thickness a₀ of the exotic region; the power-law exponent η in b = b₀(r/b₀)^{1−η}.
- **Knob → physics relations:**
  - [derivation] The field equations are solved backwards, from geometry to source: ρ = b′/(8πGc⁻²r²), τ = [b/r − 2(r − b)Φ′]/(8πGc⁻⁴r²), and radial force balance τ′ = (ρc² − τ)Φ′ − 2(p + τ)/r (Eqs. 17, 18, 16; OCR-cleaned). The energy density depends on b alone; the redshift function (lapse) enters only the tension and the pressure.
  - [derivation] No horizon ⇔ Φ finite everywhere (Eq. 37).
  - [derivation] At the throat, τ₀ = 1/(8πGc⁻⁴b₀²) ≈ 5×10⁴¹ dyn cm⁻² (10 m/b₀)² (Eq. 51, OCR-cleaned). For b₀ ≈ 3 km this equals the pressure at the centre of the most massive neutron stars.
  - [derivation] Flare-out (d²r/dz² > 0 at the throat) plus the Einstein equations give ζ₀ = (τ₀ − ρ₀c²)/|ρ₀c²| > 0, i.e. τ₀ > ρ₀c² ("exotic"; Eqs. 54–56).
  - [derivation] A radial observer with Lorentz factor γ measures T₀′₀′ = γ²(ρ₀c² − τ₀) + τ₀, which is negative for large γ (Eq. 57). The throat therefore violates the weak energy condition (WEC) even when static observers see ρ₀ ≥ 0.
  - [derivation] The traveller's felt acceleration is |e^{−Φ} d(γe^{Φ})/dl| c² ≲ g⊕ (Eq. 44). The radial tide is set by Φ″, Φ′ and b (Eq. 49); the lateral tide is set by v, b′ − b/r and Φ′ (Eq. 50). Choosing Φ′ = 0 removes the radial tide, and the lateral constraint then limits the speed.
  - [derivation] Example b = (b₀r)^{1/2}, Φ = 0: v ≲ 60 m/s (b₀/10 m) at the throat, and "the total trip time through such a tunnel can be made a comfortable hour with maximum tidal force of 1 Earth gravity" (Appendix 1).
  - [derivation] Keeping the gravity at the end stations near g⊕ forces a finite-cutoff wormhole to have R_s ≳ 1×10¹¹ m (b₀/10 m)^{1/2} ≈ 0.6 AU and a trip time ≈ 7 days (R_s/10¹¹ m)^{1/2} (Eqs. A17–A27; the ½ exponents are read from a degraded scan, see UNVERIFIED list).
  - [derivation] If static observers may see ρ < 0, the exotic region can be made arbitrarily thin (a₀ → 0; Eqs. A28–A31, "absurdly benign wormhole"). With ρ ≥ 0 imposed, a significant flare-out needs Δr ≳ b₀ of exotic material (Eq. A33 argument).
  - [claim] Stability is not analysed. An advanced civilisation "might be able to monitor its structure and use feedback forces" (Sec. III G).
  - [claim] Note added in proof, crediting Page: exotic matter is required for "any traversible, nonspherical, and nonstatic wormhole", through the outer-trapped-surface argument.
- **Method / verification standard:** Exact analytic metric-first construction. Curvature is computed in the static orthonormal frame and Lorentz-transformed to the traveller's frame. Human-comfort limits (1 yr trip, g⊕ acceleration, g⊕ tidal over 2 m) are imposed explicitly. There is no numerics and no stability analysis.
- **Scope and caveats:** Static, spherical, general relativity (GR). The matter model is left open ("we must let the relationships between ρ, τ, and p dangle"). The traveller–matter coupling is flagged as an open problem, with suggested remedies: a vacuum tube through the wormhole, or weakly coupled exotic matter.
- **Disputes, refutations, later corrections:** The requirement of exotic matter is generalised by Hochberg & Visser (1997, 1998) and by topological censorship (Friedman, Schleich & Witt 1993). Quantum-field constraints on the geometry come from Ford & Roman (1996). The "absurdly benign" limit is the thin-shell class (Visser 1989b).
- **Relation to active-rail results:** (b) The structural fact is the same one: in static slicing (zero shift, K_ij = 0) the energy density is fixed by the spatial geometry b alone, and the lapse e^{Φ} contributes only tension and pressure. (c) The stress tensor is diagonal in the static orthonormal frame (Eq. 13), which makes it Hawking–Ellis Type I. (a) This is the complement of the rail result: on the wormhole's K = 0 slices ρ comes from intrinsic curvature, whereas on flat slices it comes only from shift shear. The station condition |Φ′c²| ≲ g⊕ (Eq. 40) is the static-observer form of "a lapse gradient is felt as acceleration", a passenger limit that transfers directly to rail lapse profiles.
- **Key quote:** "Tailor b(r) and Φ(r) to make a nice wormhole; Eq. (17) and our choice for b(r) will then give us ρ(r); Eq. (18) and our choices for both b(r) and Φ(r) will then yield τ(r); and, finally, Eq. (19) together with the above will determine p(r)." (Sec. III B 3; OCR-cleaned symbols). Abstract (INSPIRE): "In the wormhole’s throat that material must possess a radial tension τ0 with the enormous magnitude τ0∼ (pressure at the center of the most massive of neutron stars)×(20 km)2/(circumference of throat)2. Moreover, this tension must exceed the material’s density of mass‐energy, ρ0c2."

### MorrisThorneYurtsever1988 — M. S. Morris, K. S. Thorne, U. Yurtsever (1988), "Wormholes, Time Machines, and the Weak Energy Condition"
- **Citation:** Phys. Rev. Lett. 61, 1446–1449 (1988); DOI 10.1103/PhysRevLett.61.1446. Pre-arXiv. Verified via INSPIRE API (`q=doi:10.1103/PhysRevLett.61.1446`) and the Caltech AUTHORS scan (4 pages, OCR) on 2026-09-26.
- **Design parts and knobs:** throat radius r₀; a Casimir source made of two charged spherical conducting plates with separation s and charge Q; plate surface energy σ; the mouths' relative motion (right-mouth acceleration g(t), velocity v) and the mouth separation D.
- **Knob → physics relations:**
  - [identity/theorem] A sphere around one mouth, seen through the wormhole, is an outer trapped surface. The averaged weak energy condition (AWEC) must then be violated along null geodesics through the wormhole (via Hawking–Ellis Prop. 9.2.8, adapted).
  - [derivation] Casimir model: between the plates τ = 3p = −3ρ = (3π²/720)(ħ/s⁴) ≡ τ_C (OCR-cleaned; consistent with the Casimir stress ∝ diag(−1, 1, 1, −3)), and a Coulomb field outside. Force balance gives Q = (8πr₀²τ_C)^{1/2}. The Einstein equations then give s ~ (r₀ l_P)^{1/2} up to an O(1) factor, i.e. s ~ 10⁻¹⁰ cm for r₀ = 1 AU. The mass and charge seen from afar both equal r₀ (OCR-cleaned).
  - [derivation] If the plates' mass-to-charge ratio must exceed the electron's, the AWEC-violating plate energy requires s < 0.029 ħ/m (below the electron Compton wavelength).
  - [derivation] Moving one mouth there and back produces differential aging between the mouths, and traversal from right to left then travels backward in time. The throat acts as a diverging lens with focal length f = r₀/2. If (f/D)B < 1, where B is the Doppler factor per cycle, repeated traversals lose energy and the Cauchy-horizon instability of the Misner type is avoided.
  - [claim] The authors "suspect … that the Cauchy horizon is fully stable".
- **Method / verification standard:** Analytic order-of-magnitude construction with fractional errors O(s/r₀). Quantum-field models of the plates are not attempted.
- **Scope and caveats:** Whether σ < ½τ_C s is allowed needs "explicit study of quantum-field-theory models for the plates (a task we have not attempted)".
- **Disputes, refutations, later corrections:** Ford & Roman (1996) show the MTY Casimir wormhole satisfies their quantum inequality (QI) bound. The same paper shows it sits extremely close to a horizon, with |g_tt| ≈ δ²/M² at the plates, and blueshifts infalling radiation by ~10²³. On chronology, Kim & Thorne (1991), Hawking (1992) and Visser (1993, 1997) dispute whether vacuum polarisation stops closed timelike curves (CTCs).
- **Relation to active-rail results:** Among (a)–(g), none visible directly. At analogy level [claim]: time-machine conversion runs entirely on differential clock rates between two ends, which is the same bookkeeping as a rail's lapse contrast (d).
- **Key quote:** "Thus, if one could show that quantum field theory forbids violations of AWEC, one could rule out advanced civilizations maintaining traversible wormholes." (p. 1446, OCR).

### Visser1989a — M. Visser (1989), "Traversable wormholes: Some simple examples"
- **Citation:** Phys. Rev. D 39, 3182–3184 (1989); DOI 10.1103/PhysRevD.39.3182; arXiv:0809.0907v1 (read v1; pre-arXiv article uploaded 2008). Submission history: [v1] Thu, 4 Sep 2008 22:42:18 UTC. Verified via https://arxiv.org/abs/0809.0907 on 2026-09-26.
- **Design parts and knobs:** an ultrastatic geometry (g₀₀ ≡ 1) made by cut-and-paste of two Minkowski spaces along ∂Ω × ℝ; the shape of the compact region Ω, i.e. the throat's principal curvature radii ρ₁, ρ₂ (flat faces, edge bending angle φ, corner rounding radius r).
- **Knob → physics relations:**
  - [derivation] Surface stress S^i_j = −(1/4πG)(K^i_j − δ^i_j K). This gives σ = −(1/4πG)(1/ρ₁ + 1/ρ₂), ϑ₁ = −1/(4πGρ₂), ϑ₂ = −1/(4πGρ₁) (Eqs. 2.2–2.4). A convex throat carries negative surface energy.
  - [derivation] A flat face (ρ₁,₂ → ∞) carries zero stress. A traveller crossing it "will feel no tidal forces and see no matter, exotic or otherwise."
  - [derivation] Polyhedral throat: all stress collapses onto the edges as negative-tension strings with μ = T = −φ/(4πG) (bending angle φ). For a cube μ = −1/(8G) = −1.52×10⁴³ J/m. Corner energy → 0 as r → 0. The edge length does not enter.
  - [derivation] Via the focusing theorem, a convex portion of ∂Ω defocuses light and so violates the WEC and AWEC.
- **Method / verification standard:** Analytic Israel junction formalism.
- **Scope and caveats:** No stability analysis. Negative-tension strings have no known field-theoretic realisation ("Note however, that field theoretic models of strings lead to positive string tensions").
- **Disputes, refutations, later corrections:** The thin-shell stability programme follows (Visser 1989b; Poisson & Visser 1995; Garcia, Lobo & Visser 2012). Eiroa et al. (2025) identify the radial tide at thin shells as fixed by the jump in K_tt.
- **Relation to active-rail results:** (c) The static surface stress is diagonal, so Type I. With unit lapse and zero shift, the only source is the bending of the junction, and flat faces carry nothing. This is a clean example of a design where the energy sits only where a surface bends.
- **Key quote:** "In particular, it is possible for a traveller to traverse such a wormhole without passing through a region of exotic matter." (abstract v1)

### Visser1989b — M. Visser (1989), "Traversable wormholes from surgically modified Schwarzschild spacetimes"
- **Citation:** Nucl. Phys. B 328, 203–212 (1989); DOI 10.1016/0550-3213(89)90100-4; arXiv:0809.0927v1 (read v1; pre-arXiv article uploaded 2008). Submission history: [v1] Thu, 4 Sep 2008 22:35:09 UTC. Verified via https://arxiv.org/abs/0809.0927 on 2026-09-26.
- **Design parts and knobs:** shell radius a (required a > 2M), mass M (and charge Q in the Reissner–Nordström variant), and the shell equation of state ϑ(σ).
- **Knob → physics relations:**
  - [derivation] σ = −(1/2πa)√(1 − 2M/a) and ϑ = −(1/4πa)(1 − M/a)/√(1 − 2M/a) (Eq. 4.3). The energy density is always negative.
  - [derivation] Nambu–Goto membrane (σ = ϑ) forces a = 3M and is dynamically unstable. Traceless (massless/Casimir-like) shell stress admits no solution.
  - [derivation] Throat equation of motion ȧ² − 2M/a − (2πσa)² = −1, with σ̇ = −2(σ − ϑ)ȧ/a (Eq. 6.1). If M > 0, the potential near a = 0 is unbounded below.
  - [derivation] For ϑ = k²σ near σ = 0: stability against explosion needs k² ≤ ½. Full stability needs M = 0 and k ≥ 1/2, or M < 0 with k ∈ (1/2, 1/√2]. Hence "(global) stability of the wormhole against collapse requires that the gravitational mass … be non–positive."
- **Method / verification standard:** Analytic junction conditions plus a dynamical potential analysis restricted to spherical motion.
- **Scope and caveats:** Spherical perturbations only. The conclusions depend on a Taylor-expandable ϑ(σ) at σ = 0.
- **Disputes, refutations, later corrections:** Linearised around a static solution without fixing an equation of state (EOS) in Poisson & Visser 1995. Generalised in Garcia, Lobo & Visser 2012.
- **Relation to active-rail results:** (c) The static shell stress is diagonal (Type I). The throat's K^τ_τ equals the magnitude of the four-acceleration of the static shell (Eq. 5.4). From eq. (3.7), σ = −κ^θ_θ/4π and ϑ = −(κ^τ_τ + κ^θ_θ)/8π: the lapse-gradient jump κ^τ_τ enters the tension ϑ together with the areal jump, while the surface energy σ contains no lapse term — the thin-shell form of (b), the lapse carrying stress without energy. Eiroa et al. (2025) show this same jump fixes the radial tide on a crossing passenger.
- **Key quote:** "The stability analysis places constraints on the equation of state of the exotic matter that comprises the throat of the wormhole." (abstract v1)

---

## D.2 Thin-shell stability: equation of state as the stability knob

### PoissonVisser1995 — E. Poisson, M. Visser (1995), "Thin-shell wormholes: Linearization stability"
- **Citation:** Phys. Rev. D 52, 7318–7321 (1995); DOI 10.1103/PhysRevD.52.7318; arXiv:gr-qc/9506083v1 (read v1, 30 Jun 1995). Submission history: [v1] Fri, 30 Jun 1995 18:49:41 UTC. Verified via https://arxiv.org/abs/gr-qc/9506083 on 2026-09-26.
- **Design parts and knobs:** a₀/M, where a₀ is the static shell radius; β₀² ≡ ∂p/∂σ at the static solution.
- **Knob → physics relations:**
  - [derivation] Linearising V(a) = 1 − 2M/a − [2πσ(a)a]² gives stability iff 2M/a₀ + (M²/a₀²)/(1 − 2M/a₀) + (1 + 2β₀²)(1 − 3M/a₀) < 0 (Eq. 29).
  - [derivation] For a₀ > 3M: β₀² < −(1 − 3M/a₀ + 3(M/a₀)²)/[2(1 − 2M/a₀)(1 − 3M/a₀)] (Eq. 31). For a₀ < 3M the inequality reverses (Eq. 32). The stable regions are I: β₀² ≥ 3/2 + √3 with a₀⁻ < a₀ < a₀⁺, and II: β₀² ≤ −1/2 with a₀ > a₀⁻, where a₀^± are the roots of Eq. 34 (Eqs. 35–36). The band −1/2 < β₀² < 3/2 + √3 is unstable for all a₀.
  - [derivation] With β₀ ∈ (0, 1] (a sound-speed reading), spherical thin-shell wormholes are always unstable. "Large traversable wormhole (a₀ > 3M) are stable only for β₀² < 0!"
  - [derivation] The Casimir plates and false vacuum both have β² = −1.
- **Method / verification standard:** Analytic linearisation of the one-dimensional potential.
- **Scope and caveats:** The authors warn that β₀ need not be a sound speed without a microphysical model: "wormhole configurations with |β₀²| > 1 should not be ruled out a priori."
- **Disputes, refutations, later corrections:** Generalised to asymmetric bulks and to external flux terms by Garcia, Lobo & Visser 2012, who replace β with conditions on the shell mass m_s(a).
- **Relation to active-rail results:** (c) Type I static shell. None visible otherwise.
- **Key quote:** "This permits us to relate stability issues to the (linearized) equation of state of the exotic matter which is located at the wormhole throat." (abstract v1)

### GarciaLoboVisser2012 — N. Montelongo Garcia, F. S. N. Lobo, M. Visser (2012), "Generic spherically symmetric dynamic thin-shell traversable wormholes in standard general relativity"
- **Citation:** Phys. Rev. D 86, 044026 (2012); DOI 10.1103/PhysRevD.86.044026; arXiv:1112.2057v3 (read v3, 15 Aug 2012). Submission history: [v1] Fri, 9 Dec 2011; [v2] Thu, 15 Dec 2011 (fig. 4 corrected); [v3] Wed, 15 Aug 2012 (matches published). Verified via https://arxiv.org/abs/1112.2057 on 2026-09-26.
- **Design parts and knobs:** two independent bulk geometries M± with b±(r), Φ±(r), where g_tt = −e^{2Φ±}(1 − b±/r); the shell surface mass m_s(a) = 4πa²σ(a); the flux term Ξ.
- **Knob → physics relations:**
  - [derivation] In this parametrisation the bulk radial null energy condition (NEC) is ρ + p_r = (r − b)Φ′/(4πr²) (Eq. 5). Outside horizons it "reduces to Φ′(r) > 0", so the choice Φ± = 0 puts the bulk on the verge of NEC violation.
  - [derivation] The flux term Ξ is "the net discontinuity in the (bulk) momentum flux … physically interpreted as the work done by external forces on the thin shell". It vanishes automatically when Φ± = 0.
  - [derivation] Stability of a static solution at a₀ ⇔ V″(a₀) > 0. This is rewritten as explicit lower bounds on m_s″(a₀) (Eq. 70) or [m_s(a)/a]″ (Eq. 72) in terms of b±, b±′, b±″. With Φ± ≠ 0 there is a second inequality on Ξ (Eq. 74).
  - [numerical] Mapping stability regions for Schwarzschild, Reissner–Nordström, Ellis and dilaton bulks: "large stability regions exist for small values of x [= 2M₊/a₀] and of y [= M₋/M₊]". The regions shrink near the horizon.
- **Method / verification standard:** Analytic junction formalism; stability regions are plotted as surfaces.
- **Scope and caveats:** Spherical, linearised, radial perturbations. Integrability of σ(a) is assumed; a two-fluid model is given as a sufficient condition.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** (b)/(c) In this parametrisation the bulk NEC is controlled solely by the lapse factor's gradient Φ′. The shell's energy exchange with the bulk (Ξ) is present only when the lapse factor varies. This parallels the rail requirement to account explicitly for boundary exchange between components.
- **Key quote:** "We demonstrate in full generality that stability of the wormhole is equivalent to choosing suitable properties for the exotic material residing on the wormhole throat." (abstract v3)

---

## D.3 General theorems: where the NEC must fail

### HochbergVisser1997 — D. Hochberg, M. Visser (1997), "Geometric structure of the generic static traversable wormhole throat"
- **Citation:** Phys. Rev. D 56, 4745–4755 (1997); DOI 10.1103/PhysRevD.56.4745; arXiv:gr-qc/9704082v1 (read v1, 29 Apr 1997). Submission history: [v1] Tue, 29 Apr 1997 22:30:15 UTC. Verified via https://arxiv.org/abs/gr-qc/9704082 on 2026-09-26.
- **Design parts and knobs:** a static metric ds² = −e^{2φ}dt² + g_ij dx^i dx^j with no symmetry assumed; the throat as a minimal-area 2-surface in a t = const slice; the throat topology (Euler characteristic χ); flare-out conditions (simple, strong, weak, f-weighted, N-fold degenerate).
- **Knob → physics relations:**
  - [identity/theorem] At the throat ρ = (1/16πG)[⁽²⁾R + 2∂tr(K)/∂n − tr(K²)] ≤ ⁽²⁾R/(16πG) (Eqs. 70–71). This expression contains no φ.
  - [identity/theorem] Throat genus decides the energy-density sign: ∫√g ρ ≤ χ/(4G) < 0 for higher genus, and ∫√g ρ < 0 for a torus under strong or weak flare-out (Eqs. 73–76).
  - [identity/theorem] At maxima of φ on the throat, ρ − τ ≤ 0 (Eq. 78). The lapse-weighted transverse integral ∫√g e^{+φ}[ρ − τ] < 0 under strong (or weak e^φ-weighted) flare-out (Eq. 83). This is the NEC averaged over the throat, and it holds without geodesic averaging.
  - [identity/theorem] If the throat sits at a minimum of the gravitational redshift, the throat-averaged transverse pressure is positive (Eqs. 86–87).
- **Method / verification standard:** Analytic (Gauss–Codazzi decomposition of the static Einstein tensor at an extremal surface).
- **Scope and caveats:** Static spacetimes only (the authors call this "the major technical limitation").
- **Disputes, refutations, later corrections:** Extended to dynamic throats by Hochberg & Visser 1998 (PRL, PRD).
- **Relation to active-rail results:** (b) The theorem's structure matches the rail result: in static slicing the lapse e^{φ} is absent from the energy density and appears in stresses and as the weight in the averaged NEC statement. (c) The stress tensor at the throat is block-diagonal with G_t̂a = 0 (Eqs. 64–65), i.e. zero Eulerian momentum density.
- **Key quote:** "[For example: the null energy condition (NEC), when suitably weighted and integrated over the wormhole throat, must be violated.]" (abstract v1)

### HochbergVisser1998PRL — D. Hochberg, M. Visser (1998), "The null energy condition in dynamic wormholes"
- **Citation:** Phys. Rev. Lett. 81, 746–749 (1998); DOI 10.1103/PhysRevLett.81.746; arXiv:gr-qc/9802048v3 (read v3, 18 Jun 1998). Submission history: [v1] Wed, 18 Feb 1998; [v2] Tue, 24 Feb 1998; [v3] Thu, 18 Jun 1998. Verified via https://arxiv.org/abs/gr-qc/9802048 on 2026-09-26.
- **Design parts and knobs:** a throat defined per null direction as a marginally anti-trapped surface (θ± = 0, dθ±/du± ≥ 0); the time dependence of the geometry.
- **Knob → physics relations:**
  - [identity/theorem] Raychaudhuri at a throat gives R_ab l±^a l±^b ≤ 0 ⇒ T_ab l±^a l±^b ≤ 0 (Eqs. 7–8). A strict-minimum condition upgrades this to strict violation on an open neighbourhood near the throat (Eq. 13).
  - [identity/theorem] A time-dependent wormhole has two throats, one per direction of travel, and they coalesce only in the static case.
  - [claim] Relabelling the source as "exotic + normal" parts (Brans–Dicke, higher-derivative, dilaton, scalar-tensor) leaves the total stress-energy NEC-violating ("semantic games"). Temporary suspension of NEC violation through time dependence is "essentially an illusion" for anyone who actually passes through.
- **Method / verification standard:** Analytic, local geometry only; no asymptotic flatness assumed.
- **Scope and caveats:** Proof sketched; details are in the PRD companion.
- **Disputes, refutations, later corrections:** Consistent with topological censorship. Modified-gravity papers (Lobo & Oliveira 2009; Kanti, Kleihaus & Kunz 2011–12) adopt the "effective stress tensor" framing that this paper criticises as semantic.
- **Relation to active-rail results:** The same Raychaudhuri bookkeeping locates NEC demand in the rail: a surface where a null congruence turns from converging to diverging requires R_ab l^a l^b ≤ 0 there. The wormhole throat is marginally anti-trapped; the rail's front light surface (f) is a trapping structure for overtaken light. The two are opposite sides of one diagnostic [claim: analogy introduced in this inventory; neither paper states it].
- **Key quote:** "A key aspect of the analysis is the demonstration that time-dependent wormholes have two throats, one for each direction through the wormhole, and that the two throats coalesce only for the case of a static wormhole." (abstract v3)

### HochbergVisser1998PRD — D. Hochberg, M. Visser (1998), "Dynamic wormholes, anti-trapped surfaces, and energy conditions"
- **Citation:** Phys. Rev. D 58, 044021 (1998); DOI 10.1103/PhysRevD.58.044021; arXiv:gr-qc/9802046v2 (read v2, 18 Jun 1998). Submission history: [v1] Tue, 17 Feb 1998; [v2] Thu, 18 Jun 1998. Verified via https://arxiv.org/abs/gr-qc/9802046 on 2026-09-26.
- **Design parts and knobs:** a marginally anti-trapped throat; fully antisymmetric torsion; time dependence.
- **Knob → physics relations:**
  - [identity/theorem] NEC violation at or near each dynamic throat is generic (abstract).
  - [derivation] Torsion cannot absorb the violation: "the energy condition violations cannot be dumped into the torsion degrees of freedom" (abstract).
  - [derivation] "…even temporary suspension of energy-condition violations is incompatible with the flare-out property of dynamic throats" (abstract; shown by concrete example).
- **Method / verification standard:** Analytic. Checked at abstract level plus the PRL companion; the full text was downloaded but its derivations were not re-traced here.
- **Scope and caveats:** Local theorems; the Page-style anti-trapped-surface definition.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** As for HochbergVisser1998PRL.
- **Key quote:** "The divergence property of the null geodesics at the marginally anti-trapped surface generalizes the ``flare-out'' condition for an arbitrary wormhole." (abstract v2)

### FriedmanSchleichWitt1993 — J. L. Friedman, K. Schleich, D. M. Witt (1993), "Topological Censorship"
- **Citation:** Phys. Rev. Lett. 71, 1486–1489 (1993), DOI 10.1103/PhysRevLett.71.1486; Erratum Phys. Rev. Lett. 75, 1872 (1995), DOI 10.1103/PhysRevLett.75.1872 (both DOIs from INSPIRE; the arXiv page shows only the erratum DOI). arXiv:gr-qc/9305017v2 (read v2, 9 Jun 1995). Submission history: [v1] Sun, 23 May 1993 (withdrawn); [v2] Fri, 9 Jun 1995. Verified via https://arxiv.org/abs/gr-qc/9305017 on 2026-09-26.
- **Design parts and knobs:** global hyperbolicity, asymptotic flatness, and the energy condition assumed.
- **Knob → physics relations:**
  - [identity/theorem] Theorem 1 (full text): if an asymptotically flat, globally hyperbolic spacetime satisfies the averaged null energy condition (ANEC), every causal curve from 𝒥⁻ to 𝒥⁺ is deformable to a topologically trivial one. The abstract states the hypothesis as the NEC; the theorem in the text uses ANEC.
  - [claim] The v2 comment records that the erratum retracts a secondary "passive topological censorship" result. "The main topological censorship theorem is unaffected by the error".
- **Method / verification standard:** Rigorous global-causal-structure proof.
- **Scope and caveats:** Needs global hyperbolicity and asymptotic flatness. Wormholes connecting a region to itself need extra care (see GrahamOlum2007).
- **Disputes, refutations, later corrections:** Erratum as above. Graham & Olum 2007 re-prove it with self-consistent achronal ANEC for simply connected spacetimes.
- **Relation to active-rail results:** (g) Same family of statements: averaged null energy along the relevant (fastest) null curves decides whether any causal shortcut exists.
- **Key quote:** "We prove here the conjecture that general relativity does not allow an observer to probe the topology of spacetime: any topological structure collapses too quickly to allow light to traverse it." (abstract v2)

### GrahamOlum2007 — N. Graham, K. D. Olum (2007), "Achronal averaged null energy condition"
- See Part C, GO07. Wormhole-specific point from this cluster's reading:
  - [derivation] Counterexample showing the limit of the theorem: a static wormhole connecting a region to itself whose throat is longer than the exterior distance between the mouths. Its fastest paths through the wormhole are chronal, so the theorem does not exclude it.

### KontouOlum2015 — E.-A. Kontou, K. D. Olum (2015), "Proof of the averaged null energy condition in a classical curved spacetime using a null-projected quantum inequality"
- See Part C, KO15.

## D.4 How much exotic matter: volume quantifiers and their dispute

### VisserKarDadhich2003 — M. Visser, S. Kar, N. Dadhich (2003), "Traversable wormholes with arbitrarily small energy condition violations"
- **Citation:** Phys. Rev. Lett. 90, 201102 (2003); DOI 10.1103/PhysRevLett.90.201102; arXiv:gr-qc/0301003v2 (read v2, 23 Apr 2003). Submission history: [v1] Wed, 1 Jan 2003; [v2] Wed, 23 Apr 2003 ("no changes in physics conclusions"). Verified via https://arxiv.org/abs/gr-qc/0301003 on 2026-09-26.
- **Design parts and knobs:** b(r), φ(r), the outer radius a of the non-Schwarzschild region, and the lapse parameters ε and λ in e^{φ} = ε + λ√(1 − 2m/r).
- **Knob → physics relations:**
  - [derivation] The ANEC line integral along radial null geodesics is I = −(1/4π)∮ e^{−φ}√(1 − b/r) dr/r² < 0 (Eq. 7).
  - [derivation] Volume quantifier ∮[ρ + p_r]dV = −∫(1 − b′) ln[e^{2φ}/(1 − b/r)] dr (Eq. 13; measure 4πr²dr).
  - [derivation] "Spatial Schwarzschild" choice b = 2m = r₀: "ρ = 0 throughout the spacetime". All ANEC-violating stress then sits in p_r and is controlled by φ (Eq. 15).
  - [derivation] Confining the deviation to r < a gives ∮p_r dV → 0 as a → 2m, while the ANEC line integral stays below −1/(2πa) (Eqs. 17–21).
  - [derivation] Piecewise R = 0 example: ∮p_r dV and ∮p_t dV can both be taken to zero (Eqs. 34–37). The ANEC line integral stays finite and negative.
- **Method / verification standard:** Analytic, explicit examples.
- **Scope and caveats:** Spherical, static. The measure choice (4πr²dr) is a convention, which is exactly what NandiZhangKumar2004 dispute.
- **Disputes, refutations, later corrections:** Nandi, Zhang & Kumar 2004 dispute the measure. Fewster & Roman 2005 show QIs force VKD wormholes to be submicroscopic or to have large scale discrepancies.
- **Relation to active-rail results:** (b) Directly visible. In the spatially Schwarzschild VKD wormholes the energy density vanishes identically, and the whole NEC-violating source is lapse-supported radial stress. This is the wormhole instance of "the lapse carries stress without energy".
- **Key quote:** "…and demonstrate the existence of spacetime geometries containing traversable wormholes that are supported by arbitrarily small quantities of ``exotic matter''." (abstract v2)

### KarDadhichVisser2004 — S. Kar, N. Dadhich, M. Visser (2004), "Quantifying energy condition violations in traversable wormholes"
- **Citation:** Pramana 63, 859–864 (2004); DOI 10.1007/BF02705207; arXiv:gr-qc/0405103v1 (read v1, 19 May 2004). Submission history: [v1] Wed, 19 May 2004. Verified via https://arxiv.org/abs/gr-qc/0405103 on 2026-09-26.
- **Design parts and knobs:** the same as VKD2003 (b, φ, a).
- **Knob → physics relations:**
  - [derivation] Restates the VKD volume-integral theorem and the spatially-Schwarzschild construction (Eqs. 8–17): ∮p_r dV → 0 as a → 2m⁺ while "the ANEC integral does not go to zero".
  - [claim] That volume integrals are "the correct quantifiers" is left as "a task for the future".
- **Method / verification standard:** Analytic (conference proceedings).
- **Scope and caveats:** The authors state that "the local and averaged energy conditions still remain violated and that violation cannot be made to vanish!"
- **Disputes, refutations, later corrections:** As for VKD2003.
- **Relation to active-rail results:** (b) As for VKD2003.
- **Key quote:** "(ii) whether this `amount of violation' can be minimised for some specific cut--and--paste geometric constructions." (abstract v1)

### NandiZhangKumar2004 — K. K. Nandi, Y.-Z. Zhang, K. B. Vijaya Kumar (2004), "Volume Integral Theorem for Exotic Matter"
- **Citation:** Phys. Rev. D 70, 127503 (2004); DOI 10.1103/PhysRevD.70.127503; arXiv:gr-qc/0407079v5 (read v5, 17 Dec 2004). Submission history: [v1] Wed, 21 Jul 2004; [v2] Thu, 22 Jul 2004; [v3] Mon, 26 Jul 2004; [v4] Sat, 23 Oct 2004; [v5] Fri, 17 Dec 2004. Verified via https://arxiv.org/abs/gr-qc/0407079 on 2026-09-26.
- **Design parts and knobs:** the integration measure; ghost-scalar (Einstein minimally coupled, sign-reversed kinetic term) wormholes; mass M and Buchdahl β; the lapse offset ε in the R = 0 wormhole.
- **Knob → physics relations:**
  - [derivation] Proposed quantifier Ω_ANEC = ∫[T_μν k^μ k^ν]√(−g₄)d³x (Eq. 6). For the Yilmaz-type ghost-scalar wormhole it returns the scalar charge exactly (Ω^{p_r=0} = −M/2 = M_S; Ω = −M), independent of coordinates. The 4πR²dR measure gives M(2 − e) instead.
  - [derivation] Buchdahl class: Ω_ANEC → 0 as β → 1⁺, where the solution approaches Schwarzschild.
  - [derivation] R = 0 wormhole: Ω^{ρ=0} = −2mε ln(2a/m) (Eq. 13): "it is ε that controls the amount of ANEC violating matter".
- **Method / verification standard:** Analytic, checked on exact solutions.
- **Scope and caveats:** The authors "do not contend" VKD's qualitative conclusion; the dispute concerns the measure.
- **Disputes, refutations, later corrections:** None found beyond this exchange.
- **Relation to active-rail results:** (b) In the R = 0 example the amount of ANEC violation is set by the lapse parameter ε.
- **Key quote:** "The improved quantifier is consistent with the principle that traversable wormholes can be supported by arbitrarily small quantities of exotic matter." (abstract v5)

### FewsterRoman2005 — C. J. Fewster, T. A. Roman (2005), "On wormholes with arbitrarily small quantities of exotic matter"
- **Citation:** Phys. Rev. D 72, 044023 (2005); DOI 10.1103/PhysRevD.72.044023; arXiv:gr-qc/0507013v1 (read v1, 4 Jul 2005). Submission history: [v1] Mon, 4 Jul 2005. Verified via https://arxiv.org/abs/gr-qc/0507013 on 2026-09-26.
- **Design parts and knobs:** throat radius r₀; b′₀ = b′(r₀); the minimum local length scale ℓ_min; the sampling fraction f; VKD and Kuhfittig geometries.
- **Knob → physics relations:**
  - [derivation] For a static observer at the throat with k = e_t̂ + e_r̂: T_ab k^a k^b = (b′₀ − 1)/(8πr₀²l_p²) < 0 (Eq. 39). This is nonzero even when ρ = 0.
  - [derivation] A null-contracted QI along the static worldline gives (ℓ_min²/r₀)√(1 − b′₀) ≲ 10⁵ l_p (Eq. 42, f = 0.01).
  - [derivation] If ℓ_min = r₀, then r₀ ≲ 10⁵ l_p/√(1 − b′₀). Reaching r₀ ~ 10²⁰ l_p (1 fermi) "one needs 1 − b′₀ ≤ 10⁻³⁰" (Eq. 43).
  - [derivation] For the spatially Schwarzschild VKD wormhole, T_ab k^a k^b = −1/(8πr₀²) at the throat (Eq. 59). VKD models are "either submicroscopic or [have] a large discrepancy between throat size and curvature radius".
  - [derivation] Kuhfittig's model flares so slowly that light needs infinite affine parameter to reach the throat, so it is non-traversable.
- **Method / verification standard:** Analytic QI bounds for a free scalar in a Hadamard state; conservative order-of-magnitude choices.
- **Scope and caveats:** Free-field QI assumed valid on scales small compared with curvature radii.
- **Disputes, refutations, later corrections:** Reviewed and extended in Kontou 2024.
- **Relation to active-rail results:** (b)/(g) Stress-only (lapse-carried) NEC violation with ρ = 0 in the static frame is bounded by the usual energy-density QIs only after boosting to a radially moving geodesic observer (Sec. 6.1, citing Ford–Roman 1996); the null-contracted bound removes the need for the boost. A QI audit of a lapse-supported rail source therefore uses boosted observers or T_ab k^a k^b; the static-frame ρ alone misses it.
- **Key quote:** "One lesson to be drawn from our results is that simply concentrating the exotic matter, in a classical analysis, to an arbitrarily small region around the wormhole throat is, by itself, not sufficient to guarantee both traversability and consistency with (or evasion of) the quantum inequality bounds." (Sec. 9)

---

## D.5 Quantum-field constraints on geometry

### FordRoman1996 — L. H. Ford, T. A. Roman (1996), "Quantum Field Theory Constrains Traversable Wormhole Geometries"
- **Citation:** Phys. Rev. D 53, 5496–5507 (1996); DOI 10.1103/PhysRevD.53.5496; arXiv:gr-qc/9510071v1 (read v1, 31 Oct 1995). Submission history: [v1] Tue, 31 Oct 1995. Verified via https://arxiv.org/abs/gr-qc/9510071 on 2026-09-26.
- **Design parts and knobs:** throat radius r₀; the thickness a₀ of the negative-energy band; the sampling fraction f; MT example geometries; the MTY Casimir plates (separation s, offset δ of the plates from r₀).
- **Knob → physics relations:**
  - [derivation] QI for a static geodesic observer, ρ₀ ≳ −c/τ₀⁴ with c = 3/(32π²). With τ₀ = f r₀ this gives r₀ ≲ l_p/(2f²) ≈ 10⁴ l_p for f ≈ 0.01 (Eqs. 50–51, MT Box 2 wormhole).
  - [derivation] "Absurdly benign" band: a₀ ≲ (r₀/(8f⁴ l_p))^{1/3} l_p (Eq. 69). For r₀ ≈ 1 m this gives a₀ ≲ 10¹⁴ l_p ≈ 10⁻²¹ m. "So even with a throat radius the size of a galaxy, the negative energy must be distributed in a band no thicker than about 10 proton radii."
  - [derivation] MTY Casimir wormhole: r₀ ≳ f²s² (in Planck units; Eq. 88) is satisfied. The plates, however, sit where |g_tt| ≈ δ²/M², so infalling radiation is blueshifted by M/δ ≈ 10²³: "A static observer just outside the plates would likely be incinerated by infalling radiation."
  - N independent fields relax the bound only as √N; a 1 m throat needs about 10⁶² fields (Conclusions) [derivation].
  - Compliance is possible only with geometries involving "large redshifts (or blueshifts)" or extreme length-scale discrepancies (Conclusions) [claim].
- **Method / verification standard:** Analytic, flat-space QI applied locally.
- **Scope and caveats:** Assumes the flat-space QI holds on scales small compared with curvature radii and boundary distances (argued, not proven).
- **Disputes, refutations, later corrections:** Refined by Fewster & Roman 2005 (null-contracted QI). Reviewed in Kontou 2024.
- **Relation to active-rail results:** (d) A deep lapse contrast multiplies the energy of infalling radiation by the lapse ratio. This passenger hazard follows any design that places people or hardware at small lapse relative to the exterior.
- **Key quote:** "Our analysis implies that either the wormhole must be only a little larger than Planck size or that there is a large discrepancy in the length scales which characterize the wormhole. In the latter case, the negative energy must typically be concentrated in a thin band many orders of magnitude smaller than the throat size." (abstract v1)

### FreivogelKrommydas2018 — B. Freivogel, D. Krommydas (2018), "The Smeared Null Energy Condition"
- See Part C, FK18.

### Kontou2024 — E.-A. Kontou (2024), "Wormhole restrictions from quantum energy inequalities"
- See Part C, K24. Wormhole-specific point from this cluster's reading:
  - [derivation] New result: applying the DSNEC to the MMP long wormhole, violation requires q ≳ r_e/ℓ (Eq. 103). "As r_e ≪ ℓ, the DSNEC is easily violated." The schematic bounds are ⟨T₋₋⟩_SNEC ≥ −4B/(ℓ_pl²ℓ²) and ⟨T₋₋⟩_DSNEC ≥ −N/(ℓ³r_e) (Eq. 104).

## D.6 Self-consistent semiclassical construction

### HochbergPopovSushkov1997 — D. Hochberg, A. Popov, S. V. Sushkov (1997), "Self-consistent Wormhole Solutions of Semiclassical Gravity"
- **Citation:** Phys. Rev. Lett. 78, 2050–2053 (1997); DOI 10.1103/PhysRevLett.78.2050; arXiv:gr-qc/9701064v1 (read v1, 30 Jan 1997). Submission history: [v1] Thu, 30 Jan 1997. Verified via https://arxiv.org/abs/gr-qc/9701064 on 2026-09-26.
- **Design parts and knobs:** ds² = −f(l)dt² + dl² + r²(l)dΩ²; boundary data f(0), f″(0), r″(0); the scalar coupling ξ.
- **Knob → physics relations:**
  - [derivation] The ll-equation at the throat is an algebraic quartic for r(0) (Eq. 8). With f′(0) = f″(0) = r″(0) = 0 and ξ = 1/6, it gives r(0) = √(−16K² ln f(0)), K² = 1/(5760π) (Eq. 9). The throat radius is set by the lapse at the throat.
  - [numerical] f(0) = f″(0) = 1, r″(0) = 0, ξ = 1/6 gives r(0) ≈ 67 l_P. Other data give r(0) ≈ 200–300 l_P, with horizons far from the throat. The displayed solution has r(0) ≈ 0.02 l_P.
  - [numerical] Planck-scale ripples with frequencies ω₁² = 1/(16K²) and ω₂² = 1/(16K²(4 + 3 ln F)). The redshift function grows as F ≈ (a ln l − b)², "so the metric as a whole is not asymptotically flat."
- **Method / verification standard:** Runge–Kutta integration of fourth-order semiclassical equations, using the Anderson–Hiscock–Samuel analytic approximation to ⟨T_μν⟩ for a conformally coupled massless scalar.
- **Scope and caveats:** Approximate ⟨T_μν⟩. Throat sizes of order 10⁻²–10² l_P place the solutions where semiclassical gravity is questionable; this is an inference from the reported numbers, not the authors' statement. The solution is not asymptotically flat.
- **Disputes, refutations, later corrections:** None found in this search.
- **Relation to active-rail results:** (b) Here the lapse value at the throat fixes the throat size through the semiclassical constraint.
- **Key quote:** "In general, the diameter of the wormhole throat, in units of the Planck length, can be arbitrarily large, depending on the values of the scalar coupling $\xi$ and the boundary values for the shape and redshift functions." (abstract v1)

---

## D.7 Stability versus matter model (GR with phantom/ghost scalars; rotation)

### ShinkaiHayward2002 — H. Shinkai, S. A. Hayward (2002), "Fate of the first traversible wormhole: black-hole collapse or inflationary expansion"
- **Citation:** Phys. Rev. D 66, 044005 (2002); DOI 10.1103/PhysRevD.66.044005; arXiv:gr-qc/0205041v2 (read v2, 11 May 2002). Submission history: [v1] Fri, 10 May 2002; [v2] Sat, 11 May 2002. Verified via https://arxiv.org/abs/gr-qc/0205041 on 2026-09-26.
- **Design parts and knobs:** the Ellis wormhole with a massless ghost Klein–Gordon field; perturbation sign and energy (ghost or normal Gaussian pulses); added "balancing" ghost radiation.
- **Knob → physics relations:**
  - [numerical] Negative total input energy → inflationary explosion. Positive → collapse to a black hole. The collapse time relates to the input energy "with an apparently universal critical exponent".
  - [numerical] "For normal matter, such as a traveller traversing the wormhole, collapse to a black hole always results." Balanced extra ghost radiation maintains it "for a limited time".
- **Method / verification standard:** Dual-null spherically symmetric code covering both universes. Convergence checked with 801–9601 grid points against the exact static solution.
- **Scope and caveats:** Spherical symmetry, massless fields.
- **Disputes, refutations, later corrections:** Confirmed by the linear and nonlinear analyses of Gonzalez, Guzman & Sarbach 2009.
- **Relation to active-rail results:** None visible among (a)–(g). As a design lesson, the passenger's own positive energy is a destabilising perturbation that the source budget must absorb.
- **Key quote:** "For normal matter, such as a traveller traversing the wormhole, collapse to a black hole always results." (abstract v2)

### GonzalezGuzmanSarbach2009a — J. A. Gonzalez, F. S. Guzman, O. Sarbach (2009), "Instability of wormholes supported by a ghost scalar field. I. Linear stability analysis"
- **Citation:** Class. Quantum Grav. 26, 015010 (2009); DOI 10.1088/0264-9381/26/1/015010; arXiv:0806.0608v2 (read v2, 19 Nov 2008). Submission history: [v1] Tue, 3 Jun 2008; [v2] Wed, 19 Nov 2008. Verified via https://arxiv.org/abs/0806.0608 on 2026-09-26.
- **Design parts and knobs:** throat areal radius and the product of the asymptotic masses (parameter γ₁).
- **Knob → physics relations:**
  - [identity/theorem] All such solutions have exactly one exponentially growing linear mode (nodal-theorem argument).
  - [numerical] The growth time τ_unstable/r_throat runs from 0.846 (γ₁ = 0) and converges to 0.590 for large γ₁ (Table I). "…a wormhole whose throat has an areal radius smaller than 1km, say, decays in a few µs."
- **Method / verification standard:** Rigorous linear analysis plus numerical shooting.
- **Scope and caveats:** Massless ghost scalar, spherical perturbations.
- **Disputes, refutations, later corrections:** Simplified derivation in Cremona, Pirotta & Pizzocchero 2019.
- **Relation to active-rail results:** None visible.
- **Key quote:** "We prove that all these solutions are unstable with respect to linear fluctuations and possess precisely one unstable, exponentially in time growing mode. The associated time scale is shown to be of the order of the wormhole throat divided by the speed of light." (abstract v2)

### GonzalezGuzmanSarbach2009b — J. A. Gonzalez, F. S. Guzman, O. Sarbach (2009), "Instability of wormholes supported by a ghost scalar field. II. Nonlinear evolution"
- **Citation:** Class. Quantum Grav. 26, 015011 (2009); DOI 10.1088/0264-9381/26/1/015011; arXiv:0806.1370v2 (read v2, 19 Nov 2008). Submission history: [v1] Mon, 9 Jun 2008; [v2] Wed, 19 Nov 2008. Verified via https://arxiv.org/abs/0806.1370 on 2026-09-26.
- **Design parts and knobs:** amplitude and profile of the initial perturbation.
- **Knob → physics relations:**
  - [numerical] End states: expansion (exponential growth of the areal radius at the symmetry point) or collapse to Schwarzschild. Timescales agree with perturbation theory for small perturbations.
  - [numerical] "Despite the rapid collapse, we find that it is possible for a photon to travel from one universe to the other and back without falling into the black hole."
- **Method / verification standard:** Numerical relativity with constraint-convergence checks, second-order convergence of the timescale, and Richardson extrapolation.
- **Scope and caveats:** Spherical, massless ghost scalar.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "Here we show that depending on the initial perturbation the wormholes either expand or decay to a Schwarzschild black hole." (abstract v2)

### BronnikovFabrisZhidenko2011 — K. A. Bronnikov, J. C. Fabris, A. Zhidenko (2011), "On the stability of scalar-vacuum space-times"
- **Citation:** Eur. Phys. J. C 71, 1791 (2011); DOI 10.1140/epjc/s10052-011-1791-2; arXiv:1109.6576v2 (read v2, 22 Oct 2011). Submission history: [v1] Thu, 29 Sep 2011; [v2] Sat, 22 Oct 2011. Verified via https://arxiv.org/abs/1109.6576 on 2026-09-26.
- **Design parts and knobs:** scalar potential V(φ); phantom versus normal kinetic sign; conformal maps to scalar-tensor and f(R) theories.
- **Knob → physics relations:**
  - [derivation] At a throat the perturbation potential has a positive pole. Generically it is regularisable by the S-deformation method, yielding regular perturbations.
  - [derivation] All static solutions with V = 0 (normal and phantom) are unstable under spherical perturbations, including anti-Fisher wormholes and "cold black holes".
- **Method / verification standard:** Analytic plus numerical perturbation analysis (abstract-level check).
- **Scope and caveats:** Radial perturbations only.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "As a particular example, we prove the instability of all static solutions with both normal and phantom scalars and V(\phi) = 0 under spherical perturbations." (abstract v2)

### BronnikovKonoplyaZhidenko2012 — K. A. Bronnikov, R. A. Konoplya, A. Zhidenko (2012), "Instabilities of wormholes and regular black holes supported by a phantom scalar field"
- **Citation:** Phys. Rev. D 86, 024028 (2012); DOI 10.1103/PhysRevD.86.024028; arXiv:1205.2224v3 (read v3, 12 Jul 2013). Submission history: [v1] Thu, 10 May 2012; [v2] Tue, 24 Jul 2012; [v3] Fri, 12 Jul 2013 ("Eqs (29) and (30) corrected"). Verified via https://arxiv.org/abs/1205.2224 on 2026-09-26.
- **Design parts and knobs:** asymptotics (flat at one end, AdS at the other; "black universes").
- **Knob → physics relations:**
  - [numerical] All M-AdS wormholes and black universes studied are unstable under spherical perturbations. The only exception is black universes whose event horizon coincides with the minimum of the area function.
- **Method / verification standard:** Numerical regularisation of the throat wall in the effective potential (abstract-level check).
- **Scope and caveats:** Axial and monopole polar perturbations only.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "As a result, we have shown that all configurations under study are unstable under spherically symmetric perturbations, except for a special class of black universes where the event horizon coincides with the minimum of the area function." (abstract v3)

### CremonaPirottaPizzocchero2019 — F. Cremona, F. Pirotta, L. Pizzocchero (2019), "On the linear instability of the Ellis-Bronnikov-Morris-Thorne wormhole"
- **Citation:** Gen. Relativ. Gravit. 51, 19 (2019); DOI 10.1007/s10714-019-2501-x; arXiv:1805.02602v3 (read v3, 21 Jan 2019). Submission history: [v1] Mon, 7 May 2018; [v2] Mon, 6 Aug 2018; [v3] Mon, 21 Jan 2019. Verified via https://arxiv.org/abs/1805.02602 on 2026-09-26.
- **Design parts and knobs:** the EBMT wormhole with a phantom scalar.
- **Knob → physics relations:**
  - [derivation] A simplified derivation of the linear instability, compared with Gonzalez–Guzman–Sarbach and Bronnikov–Fabris–Zhidenko (abstract).
- **Method / verification standard:** Analytic (abstract-level check).
- **Scope and caveats:** Linear, spherical.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "In this paper we propose a simplified derivation of the linear instability of this system, making comparisons with previous works on this subject (and generalizations) by Gonzalez, Guzman, Sarbach, Bronnikov, Fabris and Zhidenko." (abstract v3)

### BronnikovStarobinsky2007 — K. A. Bronnikov, A. A. Starobinsky (2007), "No realistic wormholes from ghost-free scalar-tensor phantom dark energy"
- **Citation:** JETP Lett. 85, 1–5 (2007); Pisma Zh. Eksp. Teor. Fiz. 85, 3–8 (2007); DOI 10.1134/S0021364007010018; arXiv:gr-qc/0612032v1 (read v1, 5 Dec 2006). Submission history: [v1] Tue, 5 Dec 2006. Verified via https://arxiv.org/abs/gr-qc/0612032 on 2026-09-26.
- **Design parts and knobs:** the non-minimal coupling f(Φ) (its sign); whether the scalar is a ghost; electric or magnetic fields.
- **Knob → physics relations:**
  - [identity/theorem] With f(Φ) > 0 everywhere and a non-ghost scalar, no wormholes form, even with electromagnetic fields.
  - [claim] With f ≥ 0 reaching zero, wormholes need "severe fine tuning". With f < 0 somewhere, the graviton becomes a ghost and the solutions are "generically unstable".
- **Method / verification standard:** Analytic theorem plus argument (abstract-level check).
- **Scope and caveats:** Static, spherical, scalar-tensor.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "It is proved that no wormholes can be formed in viable scalar-tensor models of dark energy admitting its phantom-like ($w < -1$) behaviour in cosmology, even in the presence of electric or magnetic fields, if the non-minimal coupling function $f(\Phi)$ is everywhere positive and the scalar field $\Phi$ itself is not a ghost." (abstract v1)

### Azad2023 — B. Azad, J. L. Blázquez-Salcedo, F. S. Khoo, J. Kunz (2023), "Are slowly rotating Ellis-Bronnikov wormholes stable?"
- **Citation:** Phys. Lett. B 848, 138349 (2024) (journal from INSPIRE); DOI 10.1016/j.physletb.2023.138349; arXiv:2301.05243v2 (read v2, 23 Nov 2023). Submission history: [v1] Thu, 12 Jan 2023; [v2] Thu, 23 Nov 2023 ("results unchanged"). Verified via https://arxiv.org/abs/2301.05243 on 2026-09-26.
- **Design parts and knobs:** angular momentum J (scaled J/A, A = throat area); asymmetry parameter C.
- **Knob → physics relations:**
  - [numerical] The second-order spin correction to the unstable radial mode is positive for all C studied, e.g. C = 0: ω_I⁽⁰⁾ = −1.182, Δω_I⁽²⁾ = 16.358 (Table 1). There is a critical J_c where the mode vanishes. J_c/A is "around 50% of the limiting value" 1/(8π), and it decreases monotonically with C.
- **Method / verification standard:** Perturbation theory to second order in rotation plus a numerical eigenvalue search. The first-order correction was checked to be < 10⁻⁷.
- **Scope and caveats:** Slow-rotation expansion; radial-led (l = 0) modes only. The phrasing is "indications".
- **Disputes, refutations, later corrections:** Follow-ups: Khoo et al. 2024 (rapid rotation, M_z = 2, 3 sectors) and Azad et al. 2025 (quadrupole equations).
- **Relation to active-rail results:** None visible among (a)–(g). As a design point, rotation, a stationary-shift ingredient, acts here as a stabilising knob.
- **Key quote:** "We find indications that simple wormhole solutions such as Ellis-Bronnikov in General Relativity can be stabilized by rotation, thus favoring a viable traversable wormhole." (abstract v2)

### Khoo2024 — F. S. Khoo, B. Azad, J. L. Blázquez-Salcedo, L. M. González-Romero, B. Kleihaus, J. Kunz, F. Navarro-Lérida (2024), "Quasinormal modes of rapidly rotating Ellis-Bronnikov wormholes"
- **Citation:** Phys. Rev. D 109, 084013 (2024); DOI 10.1103/PhysRevD.109.084013; arXiv:2401.02898v2 (read v2, 8 Apr 2024). Submission history: [v1] Fri, 5 Jan 2024; [v2] Mon, 8 Apr 2024. Verified via https://arxiv.org/abs/2401.02898 on 2026-09-26.
- **Design parts and knobs:** rotation rate; perturbation sector M_z.
- **Knob → physics relations:**
  - [numerical] Rotation breaks the triple isospectrality of the static symmetric Ellis–Bronnikov wormhole. "We do not find any instabilities for $M_z=2,3$ perturbations."
- **Method / verification standard:** Spectral decomposition on numerical backgrounds (abstract-level check).
- **Scope and caveats:** Only M_z = 2, 3; the radial (M_z = 0) sector is not covered.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "We do not find any instabilities for $M_z=2,3$ perturbations." (abstract v2)

### Azad2025 — B. Azad, J. L. Blázquez-Salcedo, F. S. Khoo, J. Kunz, F. Navarro-Lérida (2025), "Quadrupole perturbations of slowly spinning Ellis-Bronnikov wormholes"
- **Citation:** Universe 11(10), 325 (2025); DOI 10.3390/universe11100325; arXiv:2509.22118v1 (read v1, 26 Sep 2025). Submission history: [v1] Fri, 26 Sep 2025. Verified via https://arxiv.org/abs/2509.22118 on 2026-09-26.
- **Design parts and knobs:** asymmetry parameter; l = 2, M_z = 2 sector.
- **Knob → physics relations:**
  - [derivation] Derives the axial and polar l = 2, M_z = 2 perturbation equations in a double expansion. These "may exhibit potential instabilities in the quadrupole sector" (abstract).
- **Method / verification standard:** Perturbative derivation (abstract-level check).
- **Scope and caveats:** Equations derived. Stability verdicts for this sector are not stated in the abstract.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "Moreover, calculation of these modes may exhibit potential instabilities in the quadrupole sector." (abstract v1)
---

## D.8 Modified gravity: moving the NEC violation into the gravitational sector

### LoboOliveira2009 — F. S. N. Lobo, M. A. Oliveira (2009), "Wormhole geometries in f(R) modified theories of gravity"
- **Citation:** Phys. Rev. D 80, 104012 (2009); DOI 10.1103/PhysRevD.80.104012; arXiv:0909.5539v2 (read v2, 20 Oct 2009). Submission history: [v1] Wed, 30 Sep 2009; [v2] Tue, 20 Oct 2009. Verified via https://arxiv.org/abs/0909.5539 on 2026-09-26.
- **Design parts and knobs:** the form of f(R); the shape function b(r); the matter equation of state, with the matter required to satisfy the energy conditions.
- **Knob → physics relations:**
  - [derivation] The matter stress tensor obeys the energy conditions, while the effective stress tensor built from higher-curvature terms (a "gravitational fluid") carries the NEC violation needed at the throat. Exact f(R) solutions follow for chosen b(r) and equations of state.
- **Method / verification standard:** Analytic reconstruction of f(R) from chosen geometry. A keyword search of the full text finds no stability analysis.
- **Scope and caveats:** Stability and ghost-freedom of the reconstructed f(R) are not established in the paper.
- **Disputes, refutations, later corrections:** Hochberg & Visser (1998 PRL) call the split into "exotic" and "normal" parts a relabelling, because the total effective source still violates the NEC. The later f(R)/f(R,T)/f(Q) literature follows the same template (not individually inventoried).
- **Relation to active-rail results:** None visible.
- **Key quote:** "We impose that the matter threading the wormhole satisfies the energy conditions, so that it is the effective stress-energy tensor containing higher order curvature derivatives that is responsible for the null energy condition violation." (abstract v2)

### KantiKleihausKunz2011 — P. Kanti, B. Kleihaus, J. Kunz (2011), "Wormholes in Dilatonic Einstein-Gauss-Bonnet Theory"
- **Citation:** Phys. Rev. Lett. 107, 271101 (2011); DOI 10.1103/PhysRevLett.107.271101; arXiv:1108.3003v2 (read v2, 14 Mar 2012). Submission history: [v1] Mon, 15 Aug 2011; [v2] Wed, 14 Mar 2012. Verified via https://arxiv.org/abs/1108.3003 on 2026-09-26.
- **Design parts and knobs:** Gauss–Bonnet coupling α (in units of r₀²); dilaton coupling; the throat parameter f₀.
- **Knob → physics relations:**
  - [numerical] 4D asymptotically flat wormholes exist "without needing any form of exotic matter". The domain of existence is mapped and a generalised Smarr relation holds.
  - [claim] Linear stability under radial perturbations holds for a subset (retracted in effect by CuyubambaKonoplyaZhidenko2018).
- **Method / verification standard:** Numerical solution of the field equations (abstract-level check; details in KKK 2012).
- **Scope and caveats:** See KantiKleihausKunz2012.
- **Disputes, refutations, later corrections:** Cuyubamba, Konoplya & Zhidenko 2018 find instability for all parameters.
- **Relation to active-rail results:** None visible.
- **Key quote:** "We demonstrate linear stability with respect to radial perturbations for a subset of these wormholes." (abstract v2)

### KantiKleihausKunz2012 — P. Kanti, B. Kleihaus, J. Kunz (2012), "Stable Lorentzian Wormholes in Dilatonic Einstein-Gauss-Bonnet Theory"
- **Citation:** Phys. Rev. D 85, 044007 (2012) (journal from INSPIRE); DOI 10.1103/PhysRevD.85.044007; arXiv:1111.4049v3 (read v3, 21 Mar 2012). Submission history: [v1] Thu, 17 Nov 2011; [v2] Tue, 6 Dec 2011; [v3] Wed, 21 Mar 2012. Verified via https://arxiv.org/abs/1111.4049 on 2026-09-26.
- **Design parts and knobs:** α/r₀²; f₀; dilaton charge D; a throat perfect-fluid shell required by the symmetric extension.
- **Knob → physics relations:**
  - [derivation] Near the throat, −G⁰₀ + G^l_l = −2/(f₀r₀²) < 0 whenever e^{2ν(0)} ≠ 0 (no horizon; Eq. 32). The NEC is violated near the throat for every solution, and the violation is carried by the effective Gauss–Bonnet stress tensor.
  - [derivation] Extending to the second asymptotic region "must be made in a symmetric way, since otherwise a singularity is encountered". This makes derivatives discontinuous at the throat and requires a perfect-fluid shell there, "whose energy density is positive for the subset of stable wormhole solutions" (Sec. VIII).
  - [derivation] The acceleration and tidal forces on a traveller are computed in the traveller frame (Sec. VII, Morris–Thorne formalism).
  - [claim] The stable subset lies near the border with linearly stable dilatonic black holes. The authors note that "the study of the standard equivalent Schrödinger equation cannot determine the stability for the full domain of existence".
- **Method / verification standard:** Numerical ODE solutions; radial perturbations with a Dirichlet condition on the dilaton perturbation at the throat.
- **Scope and caveats:** A stated method limit on the stability analysis; the throat shell is needed.
- **Disputes, refutations, later corrections:** CuyubambaKonoplyaZhidenko2018: the throat boundary condition fixed the throat size. With it relaxed, all solutions are unstable.
- **Relation to active-rail results:** None visible among (a)–(g). Passenger acceleration and tides are reported, in line with the crewed-transit standard.
- **Key quote:** "The violation of the energy conditions, that is essential for the existence of the wormhole solutions [43], is realized via the presence of an effective energy-momentum tensor generated by the quadratic-in-curvature Gauss-Bonnet term." (Sec. VIII, v3)

### CuyubambaKonoplyaZhidenko2018 — M. A. Cuyubamba, R. A. Konoplya, A. Zhidenko (2018), "No stable wormholes in Einstein-dilaton-Gauss-Bonnet theory"
- **Citation:** Phys. Rev. D 98, 044040 (2018); DOI 10.1103/PhysRevD.98.044040; arXiv:1804.11170v2 (read v2, 19 Aug 2018). Submission history: [v1] Mon, 30 Apr 2018; [v2] Sun, 19 Aug 2018. Verified via https://arxiv.org/abs/1804.11170 on 2026-09-26.
- **Design parts and knobs:** the boundary conditions of the perturbation problem at the throat and at both infinities; the Gauss–Bonnet coupling α.
- **Knob → physics relations:**
  - [numerical] With throat-size perturbations allowed and purely outgoing waves at both asymptotic regions, the KKK wormhole "is unstable against small perturbations for any values of its parameters". The growth appears after a long period of damped oscillations, driven by a purely imaginary mode "nonperturbative in the Gauss-Bonnet coupling α".
  - [claim] The KKK stability result rested on a Dirichlet condition on the dilaton perturbation at the throat, which "effectively disconnected the two regions to the left and right from the throat" and fixed the throat size.
- **Method / verification standard:** Time-domain integration plus mode analysis of regularised wave equations.
- **Scope and caveats:** Radial perturbations.
- **Disputes, refutations, later corrections:** This is itself the refutation of KKK's stability claim.
- **Relation to active-rail results:** None visible. Methodological lesson: stability conclusions depend on boundary conditions that allow the structure's defining scale (here the throat size) to move.
- **Key quote:** "Here, more detailed analysis of perturbations shows that the Kanti-Kleihaus-Kunz wormhole is unstable against small perturbations for any values of its parameters." (abstract v2)

### Rubakov2016a — V. A. Rubakov (2016), "Can Galileons support Lorentzian wormholes?"
- **Citation:** Theor. Math. Phys. 187, 743 (2016); Teor. Mat. Fiz. 187, 338 (journal from INSPIRE); DOI 10.1134/S004057791605010X; arXiv:1509.08808v3 (read v3, 18 Dec 2015). Submission history: [v1] Tue, 29 Sep 2015; [v2] Thu, 8 Oct 2015; [v3] Fri, 18 Dec 2015 ("Error corrected, results and conclusions unchanged"). Verified via https://arxiv.org/abs/1509.08808 on 2026-09-26.
- **Design parts and knobs:** Galileon Lagrangian L = −R/2κ + F(π, X) + K(π, X)□π with the Minkowski limit at ∂π = 0; spacetime dimension d + 2; the throat profile c(R) (areal radius against proper distance).
- **Knob → physics relations:**
  - [identity/theorem] In 3D spacetime (d = 1), ANEC violation and ghost/gradient stability contradict each other, so there are no stable wormholes, under a mild asymptotic assumption.
  - [derivation] In 4D, wormholes with |dc/dR| ≤ 1 everywhere, including monotonic dc/dR, are ruled out; so is monotonic c′(r) in Schwarzschild-type coordinates. "Galileon-supported wormholes, if any, must be quite tricky."
  - [derivation] "…adding conventional matter that does not violate the NEC would not help", because the ANEC inequalities hold for the total stress tensor.
- **Method / verification standard:** Analytic inequalities from the stability conditions for perturbations.
- **Scope and caveats:** 4D not closed in this paper (completed in Rubakov2016b).
- **Disputes, refutations, later corrections:** Extended to Horndeski (Evseev & Melichev 2018) and evaded beyond Horndeski (Mironov, Rubakov & Volkova; Franciolini et al.).
- **Relation to active-rail results:** None visible.
- **Key quote:** "…we find that there is tension between the properties of the energy-momentum tensor required to support a wormhole (violation of average null energy conditions) and stability of the Galileon perturbations about the putative solution (absence of ghosts and gradient instabilities)." (abstract v3)

### Rubakov2016b — V. A. Rubakov (2016), "More about wormholes in generalized Galileon theories"
- **Citation:** Theor. Math. Phys. 188, 1253 (2016); Teor. Mat. Fiz. 188, 337 (journal from INSPIRE); DOI 10.1134/S0040577916080080; arXiv:1601.06566v1 (read v1, 25 Jan 2016). Submission history: [v1] Mon, 25 Jan 2016. Verified via https://arxiv.org/abs/1601.06566 on 2026-09-26.
- **Design parts and knobs:** as Rubakov2016a, now for d ≥ 2, with no assumption on π(r) at infinity.
- **Knob → physics relations:**
  - [identity/theorem] Generalised Galileon theories of form (1) admit no stable, static, spherically symmetric, asymptotically flat, traversable wormholes in more than 3 spacetime dimensions.
- **Method / verification standard:** Analytic.
- **Scope and caveats:** The Lagrangian class of Eq. (1) only.
- **Disputes, refutations, later corrections:** Consistent with Evseev & Melichev 2018 (Horndeski).
- **Relation to active-rail results:** None visible.
- **Key quote:** "We show that these theories do not admit stable, static, spherically symmetric, asymptotically flat and traversable Lorentzian wormholes." (abstract v1)

### EvseevMelichev2018 — O. A. Evseev, O. I. Melichev (2018), "No static sphericaly symmetric wormholes in Horndeski theory"
- **Citation:** Phys. Rev. D 97, 124040 (2018); DOI 10.1103/PhysRevD.97.124040; arXiv:1711.04152v1 (read v1, 11 Nov 2017). Submission history: [v1] Sat, 11 Nov 2017. Title as on arXiv, including "sphericaly". Verified via https://arxiv.org/abs/1711.04152 on 2026-09-26.
- **Design parts and knobs:** the Horndeski functions K, G₃, G₄, G₅.
- **Knob → physics relations:**
  - [identity/theorem] In 4D Horndeski, stable, static, spherically symmetric, asymptotically flat Lorentzian wormholes do not exist (ghost/gradient conditions versus the throat requirements).
- **Method / verification standard:** Analytic stability conditions in terms of the Lagrangian functions.
- **Scope and caveats:** Parity-even perturbation stability conditions.
- **Disputes, refutations, later corrections:** Evaded beyond Horndeski (Franciolini et al. 2019; Mironov, Rubakov & Volkova 2019, 2023).
- **Relation to active-rail results:** None visible.
- **Key quote:** "We show that this theory does not admit stable, static, spherically symmetric, asymptotically flat, Lorentzian wormholes." (abstract v1)

### MironovRubakovVolkova2018 — S. Mironov, V. Rubakov, V. Volkova (2018), "Towards wormhole beyond Horndeski"
- **Citation:** EPJ Web Conf. 191, 07014 (2018); DOI 10.1051/epjconf/201819107014; arXiv:1811.05832v1 (read v1, 14 Nov 2018). Submission history: [v1] Wed, 14 Nov 2018. Verified via https://arxiv.org/abs/1811.05832 on 2026-09-26.
- **Design parts and knobs:** beyond-Horndeski Lagrangian functions.
- **Knob → physics relations:**
  - [derivation] The ghost instabilities behind the Horndeski no-go can be avoided.
  - [claim] The solutions are "strongly fine tuned". This conclusion was later traced by the same authors to a computational error (MironovRubakovVolkova2019).
- **Method / verification standard:** Analytic (proceedings).
- **Scope and caveats:** Gradient instabilities left open.
- **Disputes, refutations, later corrections:** Corrected in MRV 2019: "Ref. [33] had a computational error which lead to a wrong conclusion concerning fine-tuning. We correct the error in this paper." Franciolini et al. (note added) say the same.
- **Relation to active-rail results:** None visible.
- **Key quote:** "The wormhole solutions with the latter property are, however, strongly fine tuned, and hence it is likely that they are unstable." (abstract v1)

### MironovRubakovVolkova2019 — S. Mironov, V. Rubakov, V. Volkova (2019), "More about stable wormholes in beyond Horndeski theory"
- **Citation:** Class. Quantum Grav. 36, 135008 (2019) (journal from INSPIRE); DOI 10.1088/1361-6382/ab2574; arXiv:1812.07022v2 (read v2, 5 Jun 2019). Submission history: [v1] Mon, 17 Dec 2018; [v2] Wed, 5 Jun 2019. Verified via https://arxiv.org/abs/1812.07022 on 2026-09-26.
- **Design parts and knobs:** beyond-Horndeski Lagrangian functions; parity-even and parity-odd perturbation sectors.
- **Knob → physics relations:**
  - [derivation] The Horndeski no-go proof "does not go through beyond Horndeski". An explicit Lagrangian admits a wormhole obeying the no-ghost and no-gradient conditions derived for radial-propagating parity-even and all parity-odd modes.
- **Method / verification standard:** Analytic plus an explicit example.
- **Scope and caveats:** Incomplete: spherically symmetric parity-even modes, angular propagation and slow tachyonic modes are not covered.
- **Disputes, refutations, later corrections:** Corrects the fine-tuning claim of MRV 2018. Completed for high-energy modes in MRV 2023.
- **Relation to active-rail results:** None visible.
- **Key quote:** "…our findings indicate that beyond Horndeski theories may be viable candidates to support traversable wormholes." (abstract v2)

### FranciolinietAl2019 — G. Franciolini, L. Hui, R. Penco, L. Santoni, E. Trincherini (2019), "Stable wormholes in scalar-tensor theories"
- **Citation:** JHEP 01 (2019) 221 (journal from INSPIRE); DOI 10.1007/JHEP01(2019)221; arXiv:1811.05481v2 (read v2, 29 Jan 2019). Submission history: [v1] Tue, 13 Nov 2018; [v2] Tue, 29 Jan 2019. Verified via https://arxiv.org/abs/1811.05481 on 2026-09-26.
- **Design parts and knobs:** effective field theory (EFT) operators for perturbations around static spherical backgrounds in unitary gauge, in particular the coefficient M₁₃ of the beyond-Horndeski operator.
- **Knob → physics relations:**
  - [derivation] With M₁₃ = 0 (Horndeski class) the wormhole is "always affected by a ghost instability". With M₁₃ ≠ 0 "it is possible to avoid ghost and gradient instabilities alike".
  - [claim] Stable solutions are obtainable "without any fine-tuning".
  - [claim] Open question: whether such dynamics "can be UV completed in a Lorentz invariant theory with an S-matrix that satisfies the standard analyticity conditions".
- **Method / verification standard:** EFT-of-perturbations analysis.
- **Scope and caveats:** No explicit covariant Lagrangian with the needed operator in this paper. Additional matter fields do not change the result (footnote).
- **Disputes, refutations, later corrections:** Agrees with MRV 2019.
- **Relation to active-rail results:** None visible.
- **Key quote:** "…we show that scalar-tensor theories of "beyond Horndeski" type can have wormhole solutions that are free of ghost and gradient instabilities. Such solutions are instead forbidden within the more restrictive "Horndeski" class of theories." (abstract v2)

### MironovRubakovVolkova2023 — S. Mironov, V. Rubakov, V. Volkova (2023), "In hot pursuit of a stable wormhole in beyond Horndeski theory"
- **Citation:** Phys. Rev. D 107, 104061 (2023) (journal from INSPIRE); DOI 10.1103/PhysRevD.107.104061; arXiv:2212.05969v1 (read v1, 12 Dec 2022). Submission history: [v1] Mon, 12 Dec 2022. Verified via https://arxiv.org/abs/2212.05969 on 2026-09-26.
- **Design parts and knobs:** a beyond-Horndeski Lagrangian; kinetic and gradient matrices of both parity sectors; angular sound speeds.
- **Knob → physics relations:**
  - [derivation] A complete set of high-energy stability conditions (no ghosts; no radial or angular gradient instabilities) and an example Lagrangian that satisfies them.
  - [numerical] For the example, c²_{a1}·c²_{a2} > 1: "either of speeds c²_{a1} or c²_{a2} (or both) is greater than the speed of light. This is another troublesome drawback of our solution".
  - [claim] Slow tachyonic instabilities remain unconstrained.
- **Method / verification standard:** Analytic conditions plus a numerical check on the example.
- **Scope and caveats:** Tachyonic sector open; superluminal angular propagation in the example.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible among (a)–(g). Design lesson: in this example, stability of the source sector came with superluminal propagation in the source, which a design that forbids superluminal signalling must exclude.
- **Key quote:** "We give an example of beyond Horndeski Lagrangian admitting a wormhole solution which complies with all stability constraints for the high energy modes." (abstract v1)

### LiuEtAl2023 — P. Liu, C. Niu, W.-L. Qian, X. Wang, C.-Y. Zhang (2023), "Traversable Thin-shell Wormhole in the 4D Einstein-Gauss-Bonnet Theory"
- **Citation:** Chin. J. Phys. 83, 527–538 (2023); DOI 10.1016/j.cjph.2023.04.016; arXiv:2004.14267v4 (read v4, 24 May 2023). Submission history: [v1] Wed, 29 Apr 2020; [v2] Mon, 4 May 2020; [v3] Thu, 11 Nov 2021; [v4] Wed, 24 May 2023. Verified via https://arxiv.org/abs/2004.14267 on 2026-09-26.
- **Design parts and knobs:** the sign and magnitude of the Gauss–Bonnet coupling α; the asymptotics (flat, AdS, dS); charge; throat radius.
- **Knob → physics relations:**
  - [numerical] For α < 0 with large |α|, flat and AdS: stable neutral thin-shell wormholes sustained by ordinary matter, with finite throat radii. For dS: none with ordinary matter. For α > 0: stable only with exotic matter.
  - [numerical] Charged: stable with ordinary matter in flat, AdS and dS, and throat radii can be arbitrarily small. At larger charge, stable only with exotic matter.
- **Method / verification standard:** Israel junction conditions plus linear radial stability (abstract-level check; the text notes it uses the regularised scalar-tensor version).
- **Scope and caveats:** Rests on "4D EGB", whose status as a 4D theory is disputed (see GursesSismanTekin2020).
- **Disputes, refutations, later corrections:** See GursesSismanTekin2020.
- **Relation to active-rail results:** None visible.
- **Key quote:** "In asymptotically flat and AdS spacetimes with a negative Gauss-Bonnet coupling constant, stable neutral wormholes are encountered when the magnitude of the coupling constant becomes significant. The throats of such wormholes are sustained by ordinary matter and possess finite radii." (abstract v4)

### GursesSismanTekin2020 — M. Gurses, T. C. Sisman, B. Tekin (2020), "Is there a novel Einstein-Gauss-Bonnet theory in four dimensions?"
- **Citation:** Eur. Phys. J. C 80, 647 (2020); DOI 10.1140/epjc/s10052-020-8200-7; arXiv:2004.03390v3 (read v3 abstract, 11 May 2020). Submission history: [v1] Tue, 7 Apr 2020; [v2] Sun, 12 Apr 2020; [v3] Mon, 11 May 2020. Verified via https://arxiv.org/abs/2004.03390 on 2026-09-26 (abstract level).
- **Design parts and knobs:** the D → 4 limit of Gauss–Bonnet.
- **Knob → physics relations:**
  - [claim] (abstract) The EGB field equations split into parts that remain higher-dimensional, so there is no intrinsically 4D limit.
- **Method / verification standard:** Analytic (abstract level only).
- **Scope and caveats:** Concerns the unregularised proposal. Regularised scalar-tensor versions exist; LiuEtAl2023 invoke one.
- **Disputes, refutations, later corrections:** This paper is itself one side of the 4D-EGB dispute.
- **Relation to active-rail results:** None visible.
- **Key quote:** "No! We show that the field equations of Einstein-Gauss-Bonnet theory defined in generic $D>4$ dimensions split into two parts one of which always remains higher dimensional, and hence the theory does not have a non-trivial limit to $D=4$." (abstract v3)

### EiroaRubinDeCelisSimeone2025 — E. F. Eiroa, E. Rubín de Celis, C. Simeone (2025), "Tides and energy conditions in Einstein-Gauss-Bonnet thin-shell wormholes"
- **Citation:** Universe 11, 368 (2025); DOI 10.3390/universe11110368; arXiv:2511.15001v1 (read v1, 19 Nov 2025). Submission history: [v1] Wed, 19 Nov 2025. Verified via https://arxiv.org/abs/2511.15001 on 2026-09-26.
- **Design parts and knobs:** 5D EGB coupling (positive, non-GR branch of the Wiltshire solution); inner mass M; negative Λ in the inner region; outer mass m; outer normal-matter shells.
- **Knob → physics relations:**
  - [derivation] For an object crossing a thin shell, the relative radial acceleration is ΔA^r = −κ^t_t + (Δη̃/2)[R^{rt}₋ + R^{rt}₊ …] (Eq. 14). The κ^t_t term, the jump in extrinsic curvature, is finite and "does not vanish for infinitely close points at different sides of the throat".
  - [derivation] The radial tide "does not depend of the separation between these points, nor on the traversing speed of the body", unlike the transverse tide, which can be tuned by speed and shell thickness.
  - [derivation] Choosing parameters with no κ^t_t crossing tide and with shell matter obeying the WEC (σ ≥ 0, σ + p ≥ 0) is possible with Gauss–Bonnet terms. "…pure Einstein gravity forces compact wormholes to be threaded by exotic matter". In one construction "the total amount of exotic matter of the whole construction is zero".
- **Method / verification standard:** Analytic junction conditions in EGB.
- **Scope and caveats:** 5D; a secondary cut-and-paste is used to avoid ill-defined regions of the non-GR branch; stability not treated.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** (d)/(b) and crewed-transit standard. For static shells, κ^t_t is the jump in the normal derivative of ln(lapse): the four-acceleration of static observers (cf. Visser 1989b, Eq. 5.4). A discontinuous lapse gradient across any layer therefore imposes a speed-independent radial tide on an extended passenger, so lapse profiles must be smooth on the passenger scale.
- **Key quote:** "We show that configurations supported by non-exotic matter, that is matter satisfying the weak energy condition, are possible at the same time that traversability problems associated with strong radial tides at the throat can be avoided when suitable values of the parameters are adopted." (abstract v1)

---

## D.9 Quantum-sourced wormholes: long versus short

### GaoJafferisWall2017 — P. Gao, D. L. Jafferis, A. C. Wall (2017), "Traversable Wormholes via a Double Trace Deformation"
- **Citation:** JHEP 12 (2017) 151 (journal from INSPIRE); DOI 10.1007/JHEP12(2017)151; arXiv:1608.05687v3 (read v3, 24 Sep 2019). Submission history: [v1] Fri, 19 Aug 2016; [v2] Mon, 11 Sep 2017; [v3] Tue, 24 Sep 2019. Verified via https://arxiv.org/abs/1608.05687 on 2026-09-26.
- **Design parts and knobs:** a boundary–boundary double-trace coupling h(t, x) in eternal BTZ, with its sign, strength, turn-on time and operator dimension Δ.
- **Knob → physics relations:**
  - [derivation] For positive h, the null energy along the horizon is negative after the insertion. The ray V = 0 "becomes time-like after U₀ and a spaceship that enters early enough may escape the black hole!"
  - [derivation] The direct boundary coupling makes null geodesics through the wormhole "no longer achronal". The achronal-ANEC and generalised-second-law (GSL) obstructions therefore do not apply.
  - [claim] "…the traversable throat size depends on the strength of the coupling". The wormhole "is only open for a small proper time in the interior region". The coupling fixes relative boundary time, "excluding the possibility of having closed time-like curves".
- **Method / verification standard:** Perturbative semiclassical backreaction, with the one-loop stress tensor computed numerically.
- **Scope and caveats:** AdS₃, test-astronaut level. Astronaut backreaction is discussed separately.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** (g) Directly visible. The ANEC-violating null curves are made chronal by an explicit non-local coupling, so no lead over the exterior light path arises.
- **Key quote:** "There are reasonable arguments that the ANEC is always obeyed along infinite achronal geodesics … This is sufficient to rule out traversable wormholes joining two otherwise disconnected regions of spacetime" (Sec. 1, v3).

### FuGradoWhiteMarolf2019a — Z. Fu, B. Grado-White, D. Marolf (2019), "A perturbative perspective on self-supporting wormholes"
- **Citation:** Class. Quantum Grav. 36, 045006 (2019); DOI 10.1088/1361-6382/aafcea; arXiv:1807.07917v3 (read v3, 9 Aug 2019). Submission history: [v1] Fri, 20 Jul 2018; [v2] Sat, 18 Aug 2018; [v3] Fri, 9 Aug 2019 ("fixing a factor of 2 in several formulas/plots"). Verified via https://arxiv.org/abs/1807.07917 on 2026-09-26.
- **Design parts and knobs:** periodic or anti-periodic boundary conditions of linear quantum fields around a non-contractible cycle; proximity to extremality.
- **Knob → physics relations:**
  - [derivation] Back-reaction of such fields generically makes the wormhole traversable, without boundary interactions. Nearing a smooth extremal limit keeps it traversable at later and later times.
  - [claim] This suggests a non-perturbative self-supporting eternal traversable wormhole.
- **Method / verification standard:** Perturbative semiclassical (AdS₃ and AdS₃ × S¹ detailed).
- **Scope and caveats:** General case not analysed in detail.
- **Disputes, refutations, later corrections:** v3 corrects a factor of 2.
- **Relation to active-rail results:** None visible.
- **Key quote:** "When the examples admit a smooth extremal limit, our perturbative analysis indicates the back-reacted wormhole remains traversable at later and later times as this limit is approached." (abstract v3)

### FuGradoWhiteMarolf2019b — Z. Fu, B. Grado-White, D. Marolf (2019), "Traversable Asymptotically Flat Wormholes with Short Transit Times"
- **Citation:** Class. Quantum Grav. 36, 245018 (2019); DOI 10.1088/1361-6382/ab56e4; arXiv:1908.03273v2 (read v2, 12 Nov 2019). Submission history: [v1] Thu, 8 Aug 2019; [v2] Tue, 12 Nov 2019. Verified via https://arxiv.org/abs/1908.03273 on 2026-09-26.
- **Design parts and knobs:** a pair of oppositely charged black holes held apart by a cosmic string; a second string wrapping the wormhole cycle (its quantum fluctuations are the negative-energy source); non-extremality; signal timing; mouth separation d.
- **Knob → physics relations:**
  - [derivation] For non-extremal backgrounds the integrated null energy along the horizon is exponentially small, "and thus traversability to be exponentially fragile".
  - [derivation] With appropriate timing, t_min transit = d + logs. This is more than a factor 2 below MMP and "approaches the value that, at least in higher dimensions, would be the theoretical minimum".
  - [derivation] In the "cosmological wormhole" contrast case, negative quantum energy makes traversal harder.
- **Method / verification standard:** Perturbative back-reaction in Hartle–Hawking states.
- **Scope and caveats:** Traversable only at early times, and only absent larger perturbations.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** (g) The best quantum-sourced transit time approaches, but does not beat, the exterior light time d.
- **Key quote:** "…a wormhole with mouths separated by a distance $d$ becomes traversable with a minimum transit time $t_{\text{min transit}} = d + \text{logs}$." (abstract v2)

### MaldacenaMilekhinPopov2023 — J. Maldacena, A. Milekhin, F. Popov (2018 preprint; 2023 journal), "Traversable wormholes in four dimensions"
- **Citation:** Class. Quantum Grav. 40, 155016 (2023) (journal from INSPIRE; the arXiv page shows no journal reference); DOI 10.1088/1361-6382/acde30; arXiv:1807.04726v3 (read v3, 3 Nov 2020). Submission history: [v1] Thu, 12 Jul 2018; [v2] Wed, 29 Aug 2018 ("Further restriction on the regime of validity in section 5.5"); [v3] Tue, 3 Nov 2020. Verified via https://arxiv.org/abs/1807.04726 on 2026-09-26.
- **Design parts and knobs:** magnetic charge q (integer flux); U(1) coupling; massless charged fermions (lowest Landau level → q 2D fields); near-extremal radius r_e; mouth separation d; mouth rotation.
- **Knob → physics relations:**
  - [derivation] The negative Casimir-like energy of q 2D fermions on field-line circles violates ANEC along null lines "which are not achronal". The Einstein equations then fix the throat length ℓ, with ℓ ∝ q² l_p (Sec. 5.4).
  - [derivation] Validity requires ℓ ≪ q³ l_p (Eq. 5.43); Sec. 5.5 (added in v2, kept in v3) restricts the classical derivation further, after averaging throat fluctuations over a time of order d, to d ≪ q^{5/2} (Eq. 5.49), "which is smaller than our previous estimate q³ in (5.43)". The energy gap is ~1/(q² l_p) and the binding energy ~1/(q l_p).
  - [derivation] For d ≫ q² l_p, πℓ grows linearly with d "with a coefficient which is greater than one, and numerically of order 2.35", so "in all cases πℓ > d", i.e. the wormhole is long.
  - [derivation] "…these wormholes are not safe for human travelers, who will need r_e much larger than their Compton wavelength!" (Sec. 5.4).
  - [claim] Can be embedded in the Standard Model if the mouth separation is below the electroweak scale.
- **Method / verification standard:** Analytic matched-region construction (throat, mouths, exterior), with a controlled large-q expansion.
- **Scope and caveats:** A fragile configuration: enough energy creates horizons. Rotation leads to slow radiation-driven merger.
- **Disputes, refutations, later corrections:** Kontou 2024 applies SNEC and DSNEC. The DSNEC is "easily violated", with the caveats stated there. Kanai, Maeda & Yoshida 2025 show higher-derivative EFT corrections cannot replace the Casimir source.
- **Relation to active-rail results:** (g) Directly: "Traversable short wormholes that join very distant points in space, and would lead to causality violation, are not allowed by the Einstein equations combined with the achronal average null energy condition." (d) The throat is an AdS₂ region of very small g_tt, so traversal time is set by a deep redshift contrast.
- **Key quote:** "However, long traversable wormholes are in principle allowed. By “long” we mean that it takes longer to go through the wormhole than through the ambient space." (Sec. 1, v3)

### MaldacenaMilekhin2021 — J. Maldacena, A. Milekhin (2021), "Humanly traversable wormholes"
- **Citation:** Phys. Rev. D 103, 066007 (2021); DOI 10.1103/PhysRevD.103.066007; arXiv:2008.06618v2 (read v2, 3 Nov 2020). Submission history: [v1] Sat, 15 Aug 2020; [v2] Tue, 3 Nov 2020. Verified via https://arxiv.org/abs/2008.06618 on 2026-09-26.
- **Design parts and knobs:** a dark sector: a 4D CFT with gauged U(1), realised via Randall–Sundrum II (bulk radius R₅ ≤ 50 µm); magnetic charge q; mouth radius r_e; throat length ℓ; mouth separation d.
- **Knob → physics relations:**
  - [derivation] Tidal limit: a ~ (size)/r_e² < 20g with size 0.5 m gives r_e > 1.5×10⁷ m ~ 0.05 s. Proper traversal time is πr_e (Eq. 3.26).
  - [derivation] At minimal r_e and R₅ = 50 µm: ℓ ~ 3×10³ ly, γ = ℓ/r_e ~ 2×10¹², E_bin ~ −5×10⁹ kg (Eq. 3.27). "…one could travel in less than a second between distant points in our galaxy. A second for the observer that goes through the wormhole. It would be tens of thousands of years for somebody looking from the outside."
  - [derivation] Infalling CMB photons are enhanced by γ, and the traveller sees them "with the square of this factor". The dark sector must be colder than 1/ℓ ~ 10⁻²⁶ eV.
  - [claim] No formation mechanism is given ("they require topology change").
- **Method / verification standard:** Analytic scaling construction on the MMP template.
- **Scope and caveats:** Cold, empty, flat ambient space. The "science fiction" dark sector is stated as such.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** (d) and crewed-transit standard, directly visible. The passenger's clock and the exterior clock are separated by a redshift (lapse) ratio γ ~ 2×10¹². The same ratio multiplies infalling radiation energy (γ² in the traveller frame). This quantifies the aging, tide and radiation trade that any lapse-contrast design carries.
- **Key quote:** "Interestingly, they are allowed in the quantum theory, but with one catch, the time it takes to go through the wormhole should be longer than the time it takes to travel between the two mouths on the outside" (Sec. 1, v2).

### KanaiMaedaYoshida2025 — T. Kanai, K. Maeda, D. Yoshida (2025), "Wormholes as perturbations of near-horizon black hole geometries: no-go theorems within effective field theories"
- **Citation:** Phys. Rev. D 113, 064026 (2026) (journal from INSPIRE; the arXiv page shows no journal reference); DOI 10.1103/dsnv-gq47 (INSPIRE); arXiv:2511.21017v1 (read v1, 26 Nov 2025). Submission history: [v1] Wed, 26 Nov 2025. Verified via https://arxiv.org/abs/2511.21017 on 2026-09-26.
- **Design parts and knobs:** the source of the throat perturbation (Casimir energy versus higher-derivative EFT corrections); background symmetry (near-extremal Reissner–Nordström in 4D; equal-angular-momenta Myers–Perry in 5D).
- **Knob → physics relations:**
  - [identity/theorem] With Casimir energy as source, the framework reduces to MMP. With EFT higher-derivative corrections of any form, perturbative traversable wormholes cannot arise, because near-horizon symmetry constrains the effective stress tensor at the throat.
- **Method / verification standard:** Analytic perturbation theory (abstract-level check).
- **Scope and caveats:** Perturbative, EFT, specific symmetric backgrounds.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "Our analysis therefore establishes no-go theorems: traversable wormholes cannot arise perturbatively from Reissner-Nordström or Myers-Perry black holes in an effective field theory approach." (abstract v1)

### Garattini2019 — R. Garattini (2019), "Casimir Wormholes"
- **Citation:** Eur. Phys. J. C 79, 951 (2019) (journal from INSPIRE); DOI 10.1140/epjc/s10052-019-7468-y; arXiv:1907.03623v1 (read v1, 5 Jul 2019). Submission history: [v1] Fri, 5 Jul 2019. Verified via https://arxiv.org/abs/1907.03623 on 2026-09-26.
- **Design parts and knobs:** plate separation promoted to the radial coordinate; the equation of state p_r = ωρ (ω = 3 for Casimir); redshift choice; throat radius r₀.
- **Knob → physics relations:**
  - [derivation] Casimir energy density gives b(r) = r₀ − r₁²/r₀ + r₁²/r with r₁² = π³l_p²/90 (Eq. 26, OCR-limited). A traversable wormhole (no horizon, no singularity) requires ωr₁² = r₀² (Eq. 29). For ω = 3 the result is "a TW of Planckian size". ω = 1 gives a sub-Planckian Ellis–Bronnikov wormhole.
  - [claim] The quantum weak energy condition analysis gives traversability "only in principle but not in practice".
- **Method / verification standard:** Analytic.
- **Scope and caveats:** The flat-plate Casimir stress tensor is used with r replacing the plate separation. The author notes this "could make the stress-energy tensor … potentially not conserved".
- **Disputes, refutations, later corrections:** None found. Extensions (charged, Yukawa, GUP-corrected, EGB) are not inventoried.
- **Relation to active-rail results:** None visible.
- **Key quote:** "Nevertheless, despite of the traversability result, one finds once again that the traversability is only in principle but not in practice." (abstract v1)

---

## D.10 Einstein–Dirac–Maxwell wormholes and their dispute

### BlazquezSalcedoKnollRadu2021 — J. L. Blázquez-Salcedo, C. Knoll, E. Radu (2021), "Traversable wormholes in Einstein-Dirac-Maxwell theory"
- **Citation:** Phys. Rev. Lett. 126, 101102 (2021); DOI 10.1103/PhysRevLett.126.101102; arXiv:2010.07317v2 (read v2, 12 Mar 2021). Submission history: [v1] Wed, 14 Oct 2020; [v2] Fri, 12 Mar 2021 (same title both versions). Verified via https://arxiv.org/abs/2010.07317 on 2026-09-26.
- **Design parts and knobs:** two massive charged fermions in a singlet spinor state (treated as classical one-particle wave functions); fermion mass μ; gauge charge q; mirror (Z₂) symmetry about the throat.
- **Knob → physics relations:**
  - [numerical] Spherically symmetric, asymptotically flat, singularity-free solutions with finite M and Q_e, Q_e/M > 1. They satisfy a generalised Smarr relation and are connected to extremal Reissner–Nordström.
  - [derivation] An exact solution exists for ungauged massless fermions.
  - [claim] Requires no "exotic matter". NEC violation is needed and is supplied by the spinor stress tensor. The text itself states the need for "matter content violating the null energy condition".
- **Method / verification standard:** Numerical ODE boundary-value solutions.
- **Scope and caveats:** Z₂ symmetry creates non-smoothness at the throat (see disputes). Curvature at the throat is of Planck order (Bolokhov et al.).
- **Disputes, refutations, later corrections:** Bolokhov et al. 2021; Danielson et al. 2021 ("not solutions"); Konoplya & Zhidenko 2022 (smooth asymmetric solutions); Blázquez-Salcedo et al. 2022 (reply and details); Kain 2023a (not traversable dynamically).
- **Relation to active-rail results:** None visible.
- **Key quote:** "We construct a specific example of a class of traversable wormholes in Einstein-Dirac-Maxwell theory in four spacetime dimensions, without needing any form of exotic matter." (abstract v2)

### BolokhovEtAl2021 — S. Bolokhov, K. Bronnikov, S. Krasnikov, M. Skvortsova (2021), "A note on "Traversable wormholes in Einstein-Dirac-Maxwell theory""
- **Citation:** Grav. Cosmol. 27(4), 401 (2021); DOI 10.1134/S0202289321040034; arXiv:2104.10933v2 (read v2, 3 Sep 2021). Submission history: [v1] Thu, 22 Apr 2021; [v2] Fri, 3 Sep 2021. Verified via https://arxiv.org/abs/2104.10933 on 2026-09-26.
- **Design parts and knobs:** spinor normalisation; Z₂ symmetry; curvature scale at the throat.
- **Knob → physics relations:**
  - [claim] Throat curvature scalars are of order unity in Planck units (Ricci ≈ 0.1, Kretschmann ≈ 6). Vacuum-polarisation corrections would then be as large as the Einstein-tensor terms, "Thus the metric solving the Einstein equations generally does not solve the actual equations of motion."
  - [claim] ν′(0) ≠ 0 means asymmetry. A thin shell is required only if one "postulates an unnecessary Z₂ symmetry".
  - [claim] The "without … exotic matter" wording is "misleading", since "Dirac spinor fields become exotic matter under certain circumstances".
  - [claim] "…a direct n-particle generalization of the present solutions is impossible due to the Pauli exclusion principle".
- **Method / verification standard:** Critical comment.
- **Scope and caveats:** Two pages.
- **Disputes, refutations, later corrections:** Part of the EDM dispute.
- **Relation to active-rail results:** None visible.
- **Key quote:** "The main new feature of these solutions is that such Dirac spinor fields can possess exotic properties, necessary for the existence of static wormhole configurations in GR." (abstract v2)

### DanielsonEtAl2021 — D. L. Danielson, G. Satishchandran, R. M. Wald, R. J. Weinbaum (2021), "Blázquez-Salcedo-Knoll-Radu Wormholes Are Not Solutions to the Einstein-Dirac-Maxwell Equations"
- **Citation:** Phys. Rev. D 104, 124055 (2021); DOI 10.1103/PhysRevD.104.124055; arXiv:2108.13361v2 (read v2, 17 Dec 2021). Submission history: [v1] Mon, 30 Aug 2021; [v2] Fri, 17 Dec 2021. Verified via https://arxiv.org/abs/2108.13361 on 2026-09-26.
- **Design parts and knobs:** matching of metric, Maxwell and Dirac fields at r = 0.
- **Knob → physics relations:**
  - [identity/theorem] If metric, Dirac and Maxwell fields solve the EDM equations near r = 0, then all are smooth there in a suitable gauge. The BSKR metric fails to be C³ at the throat, so it is not a solution.
  - [derivation] The failure implies an extra shell of charged matter (Maxwell matching) and "a spurious source term for the Dirac field" (Dirac matching).
- **Method / verification standard:** Rigorous analytic proof.
- **Scope and caveats:** Addresses the Z₂-symmetric BSKR construction.
- **Disputes, refutations, later corrections:** Consistent with Konoplya & Zhidenko 2022, which provides smooth asymmetric solutions.
- **Relation to active-rail results:** None visible.
- **Key quote:** "However, it can be seen that the BSKR metric fails to be $C^3$ on the wormhole throat at $r=0$." (abstract v2)

### BlazquezSalcedoKnollRadu2022 — J. L. Blázquez-Salcedo, C. Knoll, E. Radu (2022), "Einstein-Dirac-Maxwell wormholes: ansatz, construction and properties of symmetric solutions"
- **Citation:** Eur. Phys. J. C 82, 533 (2022); DOI 10.1140/epjc/s10052-022-10488-6; arXiv:2108.12187v1 (read v1, 27 Aug 2021). Submission history: [v1] Fri, 27 Aug 2021. Verified via https://arxiv.org/abs/2108.12187 on 2026-09-26.
- **Design parts and knobs:** the ansatz; the junction conditions at the throat (thin mass shell; electric-charge shell); domain of existence.
- **Knob → physics relations:**
  - [derivation] Non-smooth symmetric configurations imply "the presence of a thin mass shell structure at the throat" and a thin shell of electric charge.
  - [numerical] T^r_r − T^t_t < 0 throughout: "the null energy condition is violated everywhere", maximal "slightly outside of the throat" where the spinor amplitude peaks.
  - [derivation] The jump of the electric field at the throat is sourced by a thin charge shell with density σ₀ (Eqs. 3.33–3.35).
  - [numerical] The "limit" configurations bounding the domain of existence "possess negative masses", relatively large negative for large μQ_e.
- **Method / verification standard:** Numerical, with the junction analysis made explicit.
- **Scope and caveats:** Z₂-symmetric only. "Possible issues and limitations of the approach are also discussed."
- **Disputes, refutations, later corrections:** Written in parallel with Danielson et al.
- **Relation to active-rail results:** None visible.
- **Key quote:** "In this study, we assume symmetry under interchange of the two asymptotically flat regions of a wormhole. Possible issues and limitations of the approach are also discussed." (abstract v1)

### KonoplyaZhidenko2022 — R. A. Konoplya, A. Zhidenko (2022), "Traversable Wormholes in General Relativity"
- **Citation:** Phys. Rev. Lett. 128, 091104 (2022); DOI 10.1103/PhysRevLett.128.091104; arXiv:2106.05034v4 (read v4, 4 Mar 2022). Submission history: [v1] Wed, 9 Jun 2021; [v2] Wed, 16 Jun 2021; [v3] Mon, 13 Sep 2021; [v4] Fri, 4 Mar 2022. The v1 title was "Traversable wormholes in General Relativity without exotic matter" (checked at https://arxiv.org/abs/2106.05034v1); the v4 comment reads "(title changed)". Verified via https://arxiv.org/abs/2106.05034 on 2026-09-26.
- **Design parts and knobs:** asymmetry of metric and matter about the throat; fermion charge and mass (e.g. qr₀, μr₀).
- **Knob → physics relations:**
  - [numerical] In ds² = −N(x)²dt² + dx² + r(x)²dΩ², asymmetric solutions with smooth gravitational and matter fields exist, with no throat shell and no sign flip of the charge density.
  - [claim] "…normal matter fields must anyway violate the null energy conditions".
- **Method / verification standard:** Numerical.
- **Scope and caveats:** Dynamical stability not addressed; Kain 2023a addresses it.
- **Disputes, refutations, later corrections:** Kain 2023a evolves these asymmetric solutions and finds black-hole formation.
- **Relation to active-rail results:** None visible.
- **Key quote:** "We show that there are wormhole solutions, which are asymmetric relative the throat and endowed by smooth gravitational and matter fields, thereby being free from all the above problems." (abstract v4)

### Kain2023a — B. Kain (2023), "Are Einstein-Dirac-Maxwell wormholes traversable?"
- **Citation:** Phys. Rev. D 108, 044019 (2023); DOI 10.1103/PhysRevD.108.044019; arXiv:2305.11217v2 (read v2, 8 Aug 2023). Submission history: [v1] Thu, 18 May 2023; [v2] Tue, 8 Aug 2023. Verified via https://arxiv.org/abs/2305.11217 on 2026-09-26.
- **Design parts and knobs:** asymmetric static EDM initial data.
- **Knob → physics relations:**
  - [numerical] "In all cases considered, our simulations indicate that black holes form that are connected by the wormhole." Null geodesics through the wormhole "are trapped inside a black hole". Example initial data: μ̄ = 0.2, ē/√(4π) = 0.03.
- **Method / verification standard:** Numerical time evolution of the static solutions (spherically symmetric code, reported as second-order convergent; apparent-horizon diagnostics).
- **Scope and caveats:** Spherical; the cases considered.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "We conclude that Einstein-Dirac-Maxwell wormholes are not traversable." (abstract v2)

### Kain2023b — B. Kain (2023), "Einstein-Dirac-Maxwell wormholes in quantum field theory"
- **Citation:** Phys. Rev. D 108, 084010 (2023); DOI 10.1103/PhysRevD.108.084010; arXiv:2308.00049v2 (read v2, 10 Oct 2023). Submission history: [v1] Mon, 31 Jul 2023; [v2] Tue, 10 Oct 2023. Verified via https://arxiv.org/abs/2308.00049 on 2026-09-26.
- **Design parts and knobs:** quantised Dirac field with semiclassical gravity and electromagnetism; mode quantum numbers.
- **Knob → physics relations:**
  - [numerical] Static spherically symmetric EDM wormholes built in a QFT framework, covering "a broader class of EDM wormholes than previously considered".
- **Method / verification standard:** Numerical, semiclassical (abstract-level check).
- **Scope and caveats:** Static; stability not addressed in the abstract.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** None visible.
- **Key quote:** "Our framework is able to describe a broader class of EDM wormholes than previously considered and, being constructed in quantum field theory, puts EDM wormholes on firmer theoretical ground." (abstract v2)

---

## D.11 One-parameter bridge between black hole and wormhole

### SimpsonVisser2019 — A. Simpson, M. Visser (2019), "Black-bounce to traversable wormhole"
- **Citation:** JCAP 02 (2019) 042; DOI 10.1088/1475-7516/2019/02/042; arXiv:1812.07114v3 (read v3, 3 Feb 2019). Submission history: [v1] Tue, 18 Dec 2018; [v2] Mon, 24 Dec 2018; [v3] Sun, 3 Feb 2019. Verified via https://arxiv.org/abs/1812.07114 on 2026-09-26.
- **Design parts and knobs:** ds² = −(1 − 2m/√(r² + a²))dt² + dr²/(1 − 2m/√(r² + a²)) + (r² + a²)dΩ²; the single parameter a relative to 2m.
- **Knob → physics relations:**
  - [derivation] a > 2m gives a two-way traversable wormhole with a timelike throat. a = 2m gives a one-way wormhole with an extremal null throat. 0 < a < 2m gives a regular "black bounce". a = 0 gives Schwarzschild.
  - [derivation] ρ + p_∥ = −a²|√(r² + a²) − 2m|/(4πG_N(r² + a²)^{5/2}) (Eq. 5.5), negative everywhere except on horizons. The NEC, and with it the WEC, SEC and DEC, is violated for all a > 0.
- **Method / verification standard:** Analytic.
- **Scope and caveats:** Geometry-first; no matter model; no stability analysis.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** In static slicing a horizon is a zero of the lapse (compare MT Eq. 37). One parameter moves the design across the horizon/no-horizon boundary without touching the NEC-violation sign.
- **Key quote:** "This spacetime neatly interpolates between the standard Schwarzschild black hole and the Morris-Thorne traversable wormhole; at intermediate stages passing through a black-bounce (into a future incarnation of the universe), an extremal null-bounce (into a future incarnation of the universe), and a traversable wormhole." (abstract v3)

---

## D.12 Chronology

### KimThorne1991 — S.-W. Kim, K. S. Thorne (1991), "Do vacuum fluctuations prevent the creation of closed timelike curves?"
- **Citation:** Phys. Rev. D 43, 3929–3947 (1991); DOI 10.1103/PhysRevD.43.3929. Pre-arXiv. Verified via INSPIRE API (`q=doi:10.1103/PhysRevD.43.3929`, abstract from APS) on 2026-09-26. Full text not read.
- **Design parts and knobs:** mouth separation D when the Cauchy horizon forms; proper time Δt to the horizon; the quantum-gravity cutoff.
- **Knob → physics relations:**
  - [derivation] (abstract) The renormalised stress tensor of a conformal scalar diverges at the Cauchy horizon, but weakly: δg^{VP}_{μν} ~ (l_P/D)(l_P/Δt). For D ~ 1 m it reaches only ~10⁻³⁵ within a Planck time of the horizon.
  - [claim] Kim–Thorne conjecture a quantum-gravity cutoff at Δt ~ l_P. Hawking conjectures the cutoff at DΔt ~ l_P², which gives δg ~ 1.
- **Method / verification standard:** Abstract-level only.
- **Scope and caveats:** Massless conformal scalar; other free fields argued to agree to O(1).
- **Disputes, refutations, later corrections:** Hawking 1992; Visser 1993, 1997.
- **Relation to active-rail results:** None visible among (a)–(g).
- **Key quote:** "The renormalized stress-energy tensor is found to diverge as one approaches the Cauchy horizon. However, the divergence is extremely weak" (abstract, INSPIRE).

### Hawking1992 — S. W. Hawking (1992), "The Chronology protection conjecture"
- See Part C, H92.

### Visser1993 — M. Visser (1993), "From wormhole to time machine: Comments on Hawking's Chronology Protection Conjecture"
- **Citation:** Phys. Rev. D 47, 554–565 (1993); DOI 10.1103/PhysRevD.47.554; arXiv:hep-th/9202090v2 (read v2, 8 Oct 1992). Submission history: [v1] Wed, 26 Feb 1992 (withdrawn); [v2] Thu, 8 Oct 1992 ("major revisions"). The arXiv author field reads "Visser, By Matt". Verified via https://arxiv.org/abs/hep-th/9202090 on 2026-09-26.
- **Design parts and knobs:** mouth configuration; the quantum-gravity cutoff.
- **Knob → physics relations:**
  - [claim] (abstract) Casimir effects, wormhole disruption and gravitational back-reaction act as a "defense in depth" against time travel. For the model problems, back-reaction becomes large before the Planck cutoff is reached.
- **Method / verification standard:** Analytic model problems (abstract-level check).
- **Scope and caveats:** Model problems.
- **Disputes, refutations, later corrections:** Visser 1997 (Roman ring) shows a configuration where the argument fails.
- **Relation to active-rail results:** None visible among (a)–(g).
- **Key quote:** "For the class of model problems considered it is shown that the gravitational back reaction becomes large before the Planck scale quantum gravity cutoff is reached, thus supporting Hawking's conjecture." (abstract v2)

### Visser1997 — M. Visser (1997), "Traversable wormholes: the Roman ring"
- **Citation:** Phys. Rev. D 55, 5212–5214 (1997); DOI 10.1103/PhysRevD.55.5212; arXiv:gr-qc/9702043v1 (read v1, 21 Feb 1997). Submission history: [v1] Fri, 21 Feb 1997. Verified via https://arxiv.org/abs/gr-qc/9702043 on 2026-09-26.
- **Design parts and knobs:** number N of wormholes in a ring; per-wormhole distance from chronology violation.
- **Knob → physics relations:**
  - [derivation] (abstract) With enough wormholes, no subset is near chronology violation while the whole ring is. Vacuum polarisation can be made arbitrarily small up to the "reliability horizon", so semiclassical gravity fails before back-reaction grows.
- **Method / verification standard:** Analytic (abstract-level check).
- **Scope and caveats:** Semiclassical reliability argument.
- **Disputes, refutations, later corrections:** None found in this search.
- **Relation to active-rail results:** None visible among (a)–(g).
- **Key quote:** "In particular the back-reaction can be kept arbitrarily small all the way to the ``reliability horizon''---so that semi-classical quantum gravity becomes unreliable before the gravitational back reaction becomes large." (abstract v1)

---

## D.13 Cross-paper design findings (summary of the verified record)

1. **Geometry-first design with lapse/shape separation.** In static slicing (zero shift, zero extrinsic curvature of the slices), the energy density is fixed by spatial geometry alone. For Morris–Thorne ρ = b′/(8πr²); for the generic static throat ρ has no φ (Hochberg–Visser 1997). The lapse enters stresses only. The spatially Schwarzschild wormholes of VKD 2003 have ρ ≡ 0, and all NEC-violating stress there is lapse-supported. Fewster–Roman 2005 bound such stress-only violation with a null-contracted quantum inequality; the usual energy-density QIs reach it only after a boost to a radially moving geodesic observer (their Sec. 6.1).
2. **The NEC violation is geometric and located by null expansions.** Flare-out forces NEC violation at or near every throat (static or dynamic; two throats when time-dependent). Moving the violation into a scalar, higher-curvature or spinor sector relabels which term of the total source violates it. Globally, averaged null energy along the fastest (achronal) curves decides whether any shortcut exists. Quantum-sourced wormholes exist only as "long" wormholes whose transit time is at least the exterior light time (GJW, MMP, FGWM, Kontou 2024).
3. **Stability is decided by the matter model and by the boundary conditions of the stability analysis.** Thin shells: stability needs β₀² < 0 for a₀ > 3M, or M ≤ 0 globally. Ghost scalars: exactly one unstable mode with growth time ≈ 0.6–0.85 r_throat/c. A passenger's positive energy collapses the Ellis wormhole. Galileon/Horndeski: no-go. Beyond-Horndeski: high-energy stability achieved, with the tachyonic sector open and superluminal angular speeds in the explicit example. Rotation reduces the Ellis–Bronnikov radial instability (perturbative indication). The KKK stability claim failed once the throat size was allowed to move.
4. **Passenger metrics are design outputs.** MT 1988: tidal ≤ g⊕ gives v ≲ 60 m/s (b₀/10 m), a 1-hour to 200-day trip, and station gravity −Φ′c² ≲ g⊕. MM 2021: a 20g tidal limit forces r_e > 1.5×10⁷ m and a redshift contrast γ ~ 2×10¹², i.e. <1 s proper time against ~10⁴ yr outside, with CMB photons boosted by γ². FR 1996: near-horizon plates blueshift infalling radiation by ~10²³. Eiroa et al. 2025: a jump in K^t_t at a thin layer produces a radial tide independent of speed and separation.

---

# Part E. Synthesis table: knob/part × physics relation × papers × status

Status vocabulary: identity/theorem, derivation, numerical, claim, conjecture, disputed. The last column of E.1 and the table E.4 compare with the project identities.

### E.1 Warp drives and shortcut corridors

| Knob / part | Physics relation | Papers | Status | Project |
|---|---|---|---|---|
| Shift, one component, flat slices | Eulerian ρ = −\|∂⊥β\|²/32π at unit lapse; the longitudinal gradient (expansion) contributes nothing | Alcubierre 1994 (eq. 19); Natário 2002; Lobo & Visser 2004 (eq. 10); Barzegar & Buchert 2025 (8πGε = −Ω²) | identity | I1/(a): agrees; the α⁻² factor is the project's addition |
| Shift depending only on (t, x) | ρ = 0; vacuum (flat) exactly when the inviscid Burgers equation holds; dust or isotropic sources force this case | Santos-Pereira et al. 2020–2026; Abellán et al. 2023 | derivation | I1, I3: agree |
| General shift, flat unit-lapse slices | ρ = (1/16π)[divergence − ½ω²]; ∫ρ = −(1/32π)∫ω² ≤ 0 under fall-off | SSV 2022 (eqs. 4.5, 7.17) | theorem | I1 is the one-component case |
| Lapse N on flat slices | ∫N²ρ d³x ≤ 0, strict unless curl-free: the lapse reweights, the sign stays | Shoshany & Snodgrass 2024 | theorem (WEC) | (a) with lapse: agrees |
| Lapse as energy reducer | Eulerian \|ρ\| lowered "arbitrarily" by a lapse function | Loup, Waite & Halerewicz 2001 | claim (unrefereed); invariant content is N²ρ | I1 α⁻² suppression; I11 |
| Shift vorticity ↔ Eulerian momentum | 8π\|j\| = ½\|∇×∇×β\|; j ≡ 0 iff gradient + rigid rotation (bounded vorticity, ℝ³) | SSV 2022 (f = ∇×∇×v/16π); Fell & Heisenberg 2021; Le 2026b (Lemma 2) | theorem | I5c |
| Zero Eulerian momentum | block-diagonal tensor ⇒ Hawking–Ellis Type I | SSV 2022 §5; Rodal 2025; Le 2026b (Lemma 3); Martín-Moruno & Visser 2021 (static spacetimes) | theorem | (c), I2: agrees |
| Vorticity-bearing walls | Type-IV dominated walls (81–99% at v = 0.5); Van Den Broeck wall Type IV > 50% from v ≈ 0.38 | Le 2026b | numerical | I6: agrees |
| Matter tilt v₀ of a source-first shell | Type-IV imaginary eigenvalue grows linearly in v₀, zero at v₀ = 0 | Le 2026a | numerical | I5c (flux linear in β) |
| Speed v (shift linear in v) | energy ∝ v²; integrated negative Eulerian energy exactly quadratic on a fixed domain | Lobo & Visser 2004; Le 2026b (Lemma 4); Jusufi & Lobo 2026 | theorem / derivation | I11 breaks the fixed-profile premise: co-scaling the lapse holds the local tensor fixed |
| Wall thickness Δ, radius R | E ≈ −(1/12)v²R²/Δ; M_warp ≈ −v²R²σ | Pfenning & Ford 1997; Lobo & Visser 2004 | derivation | I25 |
| Wall thickness under a QI | Δ ≲ 10² v L_P; E then ∝ v | Pfenning & Ford 1997; Everett & Roman 1997 (tube ε ≲ 10⁴ l_P) | derivation (heuristic QI transfer) | K27 |
| Ship mass in the weak field | positive integrated WEC needs v²R²σ ≲ M_ship | Lobo & Visser 2004 | derivation | — |
| Surface area vs interior volume | conformal pocket B decouples them: stellar-mass energies, Planck-near structure; curved slices add a ³R energy channel | Van Den Broeck 1999 | numerical | outside I1's flat-slice scope |
| Shape flattening along the motion | energy ∝ longitudinal extent; α_X = 1 + v² makes E velocity-independent; optimal f̄ = min(r₀/r, 1) saves ×3 | Bobrick & Martire 2021 | derivation | — |
| Segmented walls (nacelles) | exotic stress-energy localized into cylinders; interior clocks synchronized | White et al. 2025 | derivation | I1 (energy follows shear placement) |
| Irrotational shift | peak deficit 38× below Alcubierre, 2.6×10³× below Natário; net proper energy ≈ 0; vorticity ablation raises \|E₋\| | Rodal 2025 | numerical (causal ablation) | (c) and ∫-form of (a) |
| Removing expansion (Natário) | same or larger shear; invariants 35× Alcubierre | Natário 2002; Rodal 2024 | derivation / numerical | (a) |
| Superluminal speed | horizons are Mach cones, sin α = 1/v; the interior is causally cut from the front wall | Natário 2002; Clark, Hiscock & Larson 1999; Everett & Roman 1997 | derivation / numerical | I15/(e): agrees |
| Front wall, superluminal | white horizon; RSET grows as e^{2κt}, κ ~ c/Δ; interior Hawking flux at T ~ κ | Hiscock 1997; Finazzi et al. 2009; Coutant et al. 2012 | derivation (1+1) | I13, I17, (f) |
| Front shape (transverse gradient) | infinite-blueshift points only where ∂⊥v = 0 on the v = 1 surface; a convex bubble has two; flat fronts accumulate more | Barceló et al. 2022 | derivation | I13: same criterion |
| Overtaken matter and light | blueshift b = 1 − v_s v_p at the ship; P+ particles time-locked and released as a high-energy beam on deceleration; infinite blueshift toward the horizon | McMonigal et al. 2012; Natário 2002 | numerical / derivation | (f), I12: agrees |
| UV dispersion of the quantum field | regulates the divergence, instability persists (laser or linear growth) | Coutant et al. 2012 | derivation (1+1) | I13 |
| Placement of the carrying structure | ship cannot create or steer a superluminal bubble; one-way arrival not hastened in globally hyperbolic evolution; round trip can be shortened by a corridor built on the way out | Krasnikov 1998 (Prop. 1); Everett & Roman 1997; BBV 2026 (Thm IV.7) | theorem / derivation | choreography rule; I19 |
| Two corridors or two bubbles | CTCs (time machine) | Everett & Roman 1997; Krasnikov 1998; Shoshany & Snodgrass 2024; Sajeendran & Ralph 2025 | construction | I19 (one rail has a time function) |
| Light-cone opening η of a corridor | wall energy density ∝ η/ε²; QI met at cm walls for η ~ 10⁻⁶⁶ (lead one part in 10⁶⁶) | Everett & Roman 1997 | derivation | contrast with (g) |
| Interior lapse (clock rate) | positive-energy spherical drives only slow interior clocks; faster interior clocks need negative energy | Bobrick & Martire 2021 | derivation (spherical) | I16, I26, (d) |
| Lapse as frame switch | a non-unit lapse moves the drive between rest frames; two such drives close a timelike geodesic | Shoshany & Snodgrass 2024 | construction | I11 analogue |
| Positive-mass matter shell + interior shift | EC-compliant constant-velocity shift up to β ≈ 0.02 (2.365 M_J shell); shift bounded by momentum ≤ energy; Shapiro delay persists | Fuchs et al. 2024 | numerical; disputed | I5/I8; (g) |
| Source–vacuum transition of a shell | EC failures localize there; v-independent DEC deficit fixed by profile regularity | Le 2026a; Bolívar et al. 2026 (onset budget) | numerical / theorem (static PG) | P01 §2d |
| Shell compactness and thickness | no admissible shell in 600 configurations | Le 2026a | numerical | — |
| Released lapse, static hollow core | positive-energy flat cavities with Schwarzschild exterior satisfy all ECs on a compactness interval | Bolívar et al. 2026 | construction | (b), I2, I10: agrees |
| Unit-lapse radial PG class | p_r = −ρ, p_⊥ = −ρ − rρ′/2: a density rising out of a cavity violates the transverse NEC | Bolívar et al. 2026 | theorem | boundary-layer findings |
| Flat exterior (truncation) | zero integrated energy ⇒ negative energy somewhere (spherical) | Bobrick & Martire 2021 | derivation | I10 |
| ADM mass | Alcubierre and zero-expansion: M_ADM = 0; zero-vorticity can carry M via a √(2M/r) tail | SSV 2023 | derivation; disputed | I10 |
| ADM energy and momentum, R-Warp | E_ADM = 0; P_ADM generally ≠ 0; DEC ⇒ Minkowski | BBV 2026 (Thms IV.19, IV.20) | theorem | recoil accounting |
| Steering | Bondi four-momentum changes only by radiation; −ṁ ≥ 3m\|a\|; m_f/m_i = e^{−3L} | Le 2026c; Bobrick & Martire 2021 (propulsion needed) | theorem-level / derivation | recoil and boundary exchange |
| Containment failure | GW burst f ~ 1/R; matter flux dominates; quasi-local mass ends more positive | Clough, Dietrich & Khan 2024 | numerical (full NR) | coupled-dynamics gap |
| Background geometry | black-hole or de Sitter background flow lowers NEC/WEC violation; warp traversal of a wormhole needs a horizon | Garattini & Zatrimaylov 2024–2025 | derivation (Eulerian; divergence-averaged) | I3 |
| Non-compact thin membranes | superluminal WEC-satisfying toy drive | Huey 2024 | derivation (outside SSV scope) | limits of (a), (g) |
| Energy-condition test method | NEC/WEC/SEC as 4×4 LMIs; interval certificates; the Eulerian frame misses ≈73% of WEC violations (Rodal wall) | Le 2026b; Warp Factory 2024 (observer sampling) | theorem / numerical | P01 |
| Hawking–Ellis type as source match | braiding scalars reach Type IV only where the NEC fails; types I and IV stable, II and III unstable | Gergely 2026; Martín-Moruno & Visser 2018 | theorem | P01 §2g |
| Coupling engineering κ(x) | violates conservation (Bianchi) or is excluded by PPN bounds | Rodal 2025 (metamaterial) | derivation | — |
| Optimization method | variational shape optimum for the Alcubierre profile (×3); perturbative metric optimizer in Warp Factory (AIAA 2023 toolkit paper); "direct 1D optimization of the radial profiles" named as future work for the Fuchs shell. The 2026-09-26 search found no paper that optimizes a warp geometry against certified all-observer energy-condition margins. | Bobrick & Martire 2021; Helmerich et al. 2023/2024; Fuchs et al. 2024 | derivation / method; gap | — |

### E.2 Quantum inequalities, ANEC and causality

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

### E.3 Traversable wormholes

| Knob/part | Physics relation | Papers | Status |
|---|---|---|---|
| Shape function b(r), throat radius b₀ | ρ = b′/(8πGc⁻²r²); throat tension τ₀ = 1/(8πGc⁻⁴b₀²) ∝ b₀⁻² (≈5×10⁴¹ dyn cm⁻² at b₀ = 10 m) | MorrisThorne1988 | [derivation], exact GR |
| Redshift function Φ (lapse e^Φ) | Absent from ρ; sets τ, p; horizon ⇔ Φ → −∞; station gravity −Φ′c²; radial tide from Φ′, Φ″; Φ′ = 0 gives zero radial tide | MorrisThorne1988; HochbergVisser1997; VisserKarDadhich2003 | [derivation]/[identity/theorem] |
| Flare-out of throat (static) | τ₀ > ρ₀c² at throat; ∫√g e^φ(ρ − τ) < 0 over throat; NEC violated at maxima of φ | MorrisThorne1988; HochbergVisser1997 | [identity/theorem] |
| Throat topology (genus) | ∫√g ρ ≤ χ/4G < 0 for genus ≥ 2; torus ≤ 0 | HochbergVisser1997 | [identity/theorem] |
| Dynamic throat (marginally anti-trapped surface) | T_ab l^a l^b < 0 near each of two throats; temporary suspension incompatible with flare-out; torsion cannot absorb violation | HochbergVisser1998PRL; HochbergVisser1998PRD | [identity/theorem] |
| Achronality of through-going null curves | Achronal ANEC ⇒ no shortcut wormholes joining distinct asymptotic regions; "long" wormholes (chronal curves) allowed | FriedmanSchleichWitt1993; GrahamOlum2007; KontouOlum2015; GaoJafferisWall2017; MaldacenaMilekhinPopov2023; Kontou2024 | [identity/theorem] conditional on self-consistent achronal ANEC (conjecture; partial proof) |
| Exotic-region thickness a₀ | With ρ < 0 allowed: arbitrarily thin (MT); QI: a₀ ≲ (r₀/(8f⁴ l_p))^{1/3} l_p (≈10⁻²¹ m at r₀ = 1 m) | MorrisThorne1988; FordRoman1996 | [derivation]; QI assumed valid locally |
| Uniform-scale throat | QI: r₀ ≲ l_p/(2f²) ≈ 10⁴ l_p | FordRoman1996 | [derivation] |
| b′₀ and ℓ_min at throat | Null-contracted QI: (ℓ_min²/r₀)√(1 − b′₀) ≲ 10⁵ l_p; 1 fermi throat needs 1 − b′₀ ≤ 10⁻³⁰ | FewsterRoman2005 | [derivation] (free-field QI) |
| Volume "amount" of exotic matter | ∮(ρ + p_r)dV → 0 for b = 2m, a → 2m, while ANEC line integral < −1/(2πa) stays finite | VisserKarDadhich2003; KarDadhichVisser2004; NandiZhangKumar2004; FewsterRoman2005 | [derivation]; measure disputed; QI-constrained |
| Thin-shell surface shape (ultrastatic) | σ = −(1/4πG)(1/ρ₁ + 1/ρ₂); flat faces carry zero stress; edges = negative-tension strings μ = −φ/(4πG) | Visser1989a | [derivation] |
| Thin-shell EOS β₀² = ∂p/∂σ, radius a₀/M | a₀ > 3M stable only for β₀² < 0; global stability needs M ≤ 0 | Visser1989b; PoissonVisser1995 | [derivation] |
| Asymmetric bulks b±, Φ± and shell mass m_s(a) | Stability ⇔ inequality on m_s″(a₀); bulk NEC sign = sign of Φ′; shell–bulk energy flux Ξ ≠ 0 only when Φ± ≠ 0 | GarciaLoboVisser2012 | [derivation] |
| Jump of K^t_t at a thin layer (lapse-gradient jump) | Finite radial tide on extended crossing body, independent of speed and separation | EiroaRubinDeCelisSimeone2025; Visser1989b (K^τ_τ = throat 4-acceleration) | [derivation] |
| Traveller speed profile, Φ′ | Lateral tide limits v (≈60 m/s (b₀/10 m) for b = (b₀r)^{1/2}); trip ~1 h, ~7 d, ~200 d for the three MT solutions | MorrisThorne1988; KantiKleihausKunz2012 | [derivation] |
| Ghost/phantom scalar source | Exactly one unstable mode, τ ≈ 0.59–0.85 r_throat/c; end states: BH or inflationary expansion; traveller's positive energy triggers collapse | ShinkaiHayward2002; GonzalezGuzmanSarbach2009a,b; BronnikovFabrisZhidenko2011; BronnikovKonoplyaZhidenko2012; CremonaPirottaPizzocchero2019 | [identity/theorem] + [numerical] |
| Angular momentum J (Ellis–Bronnikov) | Unstable radial mode shrinks; vanishes at J_c/A ≈ 50% of 1/(8π) (second-order slow rotation); no instability found in M_z = 2, 3 at rapid rotation | Azad2023; Khoo2024; Azad2025 | [numerical]; perturbative indication, open |
| Galileon / Horndeski scalar | No stable static spherical asymptotically flat wormholes | Rubakov2016a,b; EvseevMelichev2018 | [identity/theorem] |
| Beyond-Horndeski operator (M₁₃ ≠ 0) | Ghost- and gradient-free wormholes possible without fine-tuning; example has superluminal angular speeds; tachyonic sector open; UV completion open | FranciolinietAl2019; MironovRubakovVolkova2018/2019/2023 | [derivation]; open |
| Scalar-tensor coupling f(Φ) > 0, non-ghost | No wormholes | BronnikovStarobinsky2007 | [identity/theorem] |
| Higher-curvature terms (f(R), EGB) | Effective (geometric) stress carries NEC violation; KKK EGB-dilaton wormholes unstable for all parameters; 4D-EGB thin shells with normal matter for α < 0 (theory status disputed); 5D EGB shells with WEC matter and no crossing radial tide | LoboOliveira2009; KantiKleihausKunz2011/2012; CuyubambaKonoplyaZhidenko2018; LiuEtAl2023; GursesSismanTekin2020; EiroaRubinDeCelisSimeone2025 | mixed: [derivation]/[numerical]; disputes open |
| Non-local boundary coupling h (AdS) | Negative ANEC for h > 0; throat opening grows with coupling; null curves made chronal, no CTCs | GaoJafferisWall2017 | [derivation] |
| Magnetic charge q with massless charged fermions | Casimir-like negative energy; throat length ℓ ∝ q² l_p; validity ℓ ≪ q³ l_p, tightened to d ≪ q^{5/2} by Sec. 5.5; πℓ > d always (coefficient ≈ 2.35 at large d); unsafe for humans | MaldacenaMilekhinPopov2023; Kontou2024 | [derivation] |
| Quantum string/field fluctuations on non-contractible cycle | Traversability exponentially fragile off extremality; minimum transit d + logs | FuGradoWhiteMarolf2019a,b | [derivation] (perturbative) |
| Mouth radius r_e, dark-sector (RS-II) | 20g tide ⇒ r_e > 1.5×10⁷ m; ℓ ~ 3×10³ ly; redshift contrast γ ~ 2×10¹²; <1 s proper vs ~10⁴ yr outside; dark sector colder than 10⁻²⁶ eV | MaldacenaMilekhin2021 | [derivation] under stated assumptions |
| Lapse at source location (near-horizon) | Infalling radiation blueshifted by lapse ratio (≈10²³ at MTY plates; γ, γ² in MM) | FordRoman1996; MaldacenaMilekhin2021 | [derivation] |
| Casimir EOS p_r = 3ρ as the only source | Planck-size throat; traversable "only in principle" | Garattini2019; MorrisThorneYurtsever1988 | [derivation] |
| Semiclassical self-consistency (conformal scalar) | Throat radius fixed by lapse at throat, r(0) = √(−16K² ln f(0)); Planck-scale ripples; not asymptotically flat | HochbergPopovSushkov1997 | [numerical], approximate ⟨T⟩ |
| Classical Dirac spinors + Maxwell | Symmetric solutions need throat shells (not EDM solutions); smooth asymmetric solutions exist; NEC violated; evolve to connected black holes | BlazquezSalcedoKnollRadu2021/2022; BolokhovEtAl2021; DanielsonEtAl2021; KonoplyaZhidenko2022; Kain2023a,b | disputed; numerics: not traversable |
| Higher-derivative EFT corrections near extremal RN/MP | Cannot perturbatively open a traversable throat | KanaiMaedaYoshida2025 | [identity/theorem] (perturbative EFT) |
| Single parameter a (black-bounce metric) | a > 2m wormhole, a = 2m null throat, a < 2m black bounce; NEC violated for all a > 0 | SimpsonVisser2019 | [derivation] |
| Mouth motion / differential aging | Time machine; Cauchy-horizon vacuum polarisation δg ~ (l_P/D)(l_P/Δt); protection disputed; Roman ring keeps back-reaction small to the reliability horizon | MorrisThorneYurtsever1988; KimThorne1991; Hawking1992; Visser1993; Visser1997 | disputed |

---

### E.4 The project's results against the literature

| Project result | Literature status | Key papers | Reading |
|---|---|---|---|
| (a) I1: ρ = −(∂⊥β/α)²/32π on flat slices, one-component shift | Unit-lapse form published repeatedly; the general-lapse form follows from Shoshany & Snodgrass eq. 4.3, which reduces to exactly −\|∇⊥β\|²/(32πN²) for a pure shear shift. The integral form ∫ρ = −∫ω²/32π (unit lapse) and ∫N²ρ ≤ 0 (any lapse) are theorems. | Alcubierre 1994 eq. 19; Natário 2002; Lobo & Visser 2004 eq. 10; Barzegar & Buchert 2025; SSV 2022 eqs. 4.5, 7.17; Shoshany & Snodgrass 2024 eqs. 4.3, 4.8; Santos-Pereira et al. (dust ⇒ vacuum) | Agrees. The identity is established physics; the project's use of α⁻² as a design lever is its own. Scope: flat slices; curved slices (Van Den Broeck pocket, wormholes, Fuchs shell, Bolívar lapse family) add the ³R channel. |
| (b) I2, I10: the lapse carries stress without energy | In static slicing the energy density follows the spatial geometry alone and the redshift function enters only stresses; releasing the lapse is what lets a positive wall support a flat cavity. | Morris & Thorne 1988 eqs. 17–19 (Part D); Bolívar, Abellán & Vasilev 2026; Shoshany & Snodgrass 2024 eq. 4.25 (ΔN/N in the stresses); Bobrick & Martire 2021 (interior clock rate) | Agrees. |
| (c) I2, I5c: zero Eulerian momentum ⇒ Type I | Stated for zero-vorticity Natário drives and proved for static spacetimes with back-reaction; momentum–vorticity lemma for flat unit-lapse slices. | SSV 2022 §5; Martín-Moruno & Visser 2021; Le 2026b Lemmas 2–3; Rodal 2025 | Agrees. The project's statement for any lapse and any cause of zero momentum is the algebraic core (n is then an eigenvector); the literature states special cases. |
| (d) I11: speed as a lapse contrast (speed-scaling isometry) | No paper states the isometry. Related results: a spatially varying lapse is required for geodesic frame transitions; Eulerian energy scales as 1/N²; large N suppresses total Eulerian energy at an N-fold time-stretch cost; positive-energy spherical shells can only slow interior clocks. | Shoshany & Snodgrass 2024; Loup et al. 2001 (unrefereed); Bobrick & Martire 2021 | Consistent; the isometry is a derivation (time reparametrization) with no literature precedent found. The clock cost the literature names is the project's 55× clock incident. |
| (e) I15: sin θ < 1/v for a moving front | The horizon of a superluminal drive is the Mach cone sin α = 1/v; a front surface moving slower than light along its normal is timelike. | Natário 2002 §3; Clark, Hiscock & Larson 1999; Low 1999 with the Part C derivation | Agrees. |
| (f) I12, I13: a front light surface traps overtaken light | Superluminal fronts are white horizons with exponential RSET growth; overtaken particles are time-locked and blueshifted; horizon points sit where the transverse gradient of the flow vanishes on the v = 1 surface. | Finazzi, Liberati & Barceló 2009; Natário 2002; McMonigal, Lewis & O'Byrne 2012; Barceló et al. 2022; Coutant et al. 2012 | Agrees; Barceló et al.'s criterion is the same statement as I13. The 3+1 renormalized stress tensor is open in both the literature and the project. |
| (g) I23: achronal ANEC excludes quantum sources for any lead over light | Supported as a conditional statement about a global lead (usable by arbitrarily distant endpoints): Gao–Wald Theorem 1 in Galloway's null-line form gives a null line, and Graham–Olum Lemma 1 gives negative ANEC on it, assuming null completeness and the generic condition. Quantum exclusion is proven perturbatively (Wall 2010; Kontou & Olum 2015) and conjectured in general (Graham & Olum 2007). Local (Olum-type) advances are not excluded by achronal ANEC. | Part C: GW00, GO07, W10, KO15, VBL98 (withdrawn v1 claim), O98; Bobrick & Martire 2021 §4.2; Fuchs et al. 2024 (positive mass ⇒ Shapiro delay); Le 2026a (positive null-energy integral for positive-mass shells) | Agrees with qualifications: "any lead" should read "any lead that persists for distant endpoints"; "at any size" holds within the semiclassical regime; the achronality of the complete ray and the transverse width of the deficit need to be shown. |
| I19: σ is a global time function on one rail | One tube or bubble has no CTCs; two in different frames do; a switched-on superluminal R-Warp model is not globally hyperbolic. | Everett & Roman 1997; Everett 1996 and Hawking 1992 (Part C); Shoshany & Snodgrass 2024; Barzegar, Buchert & Vigneron 2026 Thm IV.7 | Consistent. A time function gives stable causality, a weaker property than global hyperbolicity; the book should state which one a design has. |
| I6, I5c: Type IV where a one-component shift begins to vary; flux linear in β | Type-IV dominated walls; Type-IV onset linear in matter tilt; violations at shift boundaries. | Le 2026b; Le 2026a; Warp Factory 2024 | Agrees. |
| I10: zero Komar mass with an exactly flat exterior | Truncated drives have zero ADM mass and need negative energy somewhere. | Bobrick & Martire 2021 §3.1; SSV 2023; Lobo & Visser 2004; Barzegar, Buchert & Vigneron 2026 Thm IV.19; Gao & Wald 2000 (DEC + flat exterior ⇒ flat) | Agrees. |
| I25: stresses ∝ 1/L², energies ∝ L | E ∝ v²R²/Δ at fixed shape; E = −(15π/1024)v²l for a one-scale profile. | Pfenning & Ford 1997; Lobo & Visser 2004; Jusufi & Lobo 2026 | Agrees. |

### E.5 Derived here: the energy-condition cost of a lapse-only region on flat slices

Status: **derivation** made during this survey, with the Einstein tensor checked symbolically (sympy, metric −α(x)²dt² + δ_ij dx^i dx^j). No paper read for this inventory states it in this form; the closest published statements are Bobrick & Martire 2021 §3.1 (a positive-energy spherical shell can only slow interior clocks), Barzegar, Buchert & Vigneron 2026 Thm IV.20 (DEC forces an asymptotically flat R-Warp model to be Minkowski) and the static Type I theorem of Martín-Moruno & Visser 2021.

**Setting.** Flat spatial slices, a time-independent lapse α(x) → 1 at infinity, and zero shift (a spatially uniform, time-independent shift gives the same K_ij = 0 and the same result).

**Tensor.** G_00 = 0, so the Eulerian energy density vanishes identically; the Eulerian momentum vanishes (K_ij = 0), so the tensor is Hawking–Ellis Type I; the stresses are

  8π α S_ij = δ_ij ∇²α − ∂_i∂_j α,  with trace S = ∇²α / (4π α).

This is the precise content of project result (b): the lapse carries stress and no energy.

**Lemma.** Every non-constant such lapse violates the NEC somewhere.

- *Case 1: a 1/r tail, α = 1 − M/r + …, M ≠ 0.* Outside the source ∇²α = 0 and S_ij = −∂_i∂_jα/(8πα). The Hessian of −M/r has eigenvalues −2M/r³ (radial) and +M/r³ (twice, tangential). For M > 0 the tangential principal stress is −M/(8παr³) < 0 while ρ = 0, so ρ + p_⊥ < 0; for M < 0 the radial stress is negative.
- *Case 2: faster fall-off (M = 0).* ∫ α S d³x = (1/4π)∮ ∇α·dA → 0, so S = ∇²α/(4πα) changes sign unless ∇²α ≡ 0; a bounded harmonic α with α → 1 and no 1/r term is constant. Where S < 0 at least one principal stress is negative with ρ = 0, which violates the NEC.

**Reading.** The flux (1/4π)∮∇α·dA is the Komar mass of the lapse region, so Case 1 and Case 2 are the "positive Komar mass" and "zero Komar mass" branches. A lapse-only region on flat slices is therefore always Type I and always NEC-violating somewhere. Curved slices remove the obstruction: the Bolívar, Abellán & Vasilev 2026 lapse family and the Morris–Thorne redshift function both carry energy through the spatial curvature (mass function) while the lapse supplies the stress balance.

**Consequences for the project identities.**
- (b) holds as stated and gains a qualifier: the lapse's stress carries a mandatory NEC deficit somewhere whenever the slices are flat.
- (d) Speed as a lapse contrast places the whole contrast in regions where the lapse returns to one. On flat slices those regions are Type I, as the project states, and by the lemma each of them violates the NEC somewhere. This is the flat-slice counterpart of Bobrick & Martire's result that a faster interior clock needs negative energy.

# Part F. Open disputes

### F.1 Warp drives and shortcut corridors

1. **Positive-energy superluminal solitons (Lentz 2021; Fell & Heisenberg 2021).** Claimed non-negative Eulerian energy. Answered by Santiago–Schuster–Visser 2022 (NEC violated for every localized Natário-class drive; Eulerian energy alone decides nothing; Lentz solved only part of the Einstein equations), Warp Factory 2024 (boosted-observer WEC violation at the rhomboid interfaces), Celmaster & Rubin 2025 (negative Eulerian regions and derivation errors), Bobrick & Martire 2021 and Barzegar–Buchert–Vigneron 2026. No rebuttal from the original authors was found. Status: settled against the claim within the flat unit-lapse class.
2. **The Fuchs et al. 2024 constant-velocity shell.** Claimed to satisfy all energy conditions. Le 2026a finds a kernel-independent Type-IV tail in 22 of 25 exterior probes beyond the nominal shell and an O(10⁻¹) mismatch between the prescribed and metric-implied source; Barzegar–Buchert–Vigneron 2026 (Error 18) state the construction does not solve the TOV equations. Open: no reply from the authors found; whether an optimized profile removes the tail is untested.
3. **ADM mass of zero-vorticity drives.** Schuster–Santiago–Visser 2023 assign an ADM mass through the √(2M/r) fall-off of the flow. Barzegar–Buchert–Vigneron 2026 (Theorem IV.19, Remark IV.22) state every R-Warp model has zero ADM energy and that Painlevé–Gullstrand foliations are not asymptotically flat in the ADM sense. Open; the disagreement is over which foliation defines the ADM quantities.
4. **Time-dependent Alcubierre velocity and "continuity".** Bobrick & Martire 2021 call a time-dependent v_s an energy-conservation error; Santiago–Schuster–Visser 2022 (App. A) and Barzegar–Buchert–Vigneron 2026 (Error 14) answer that the Bianchi identity makes the reverse-engineered tensor conserved automatically. Settled against the Bobrick–Martire statement; the physical point that a drive needs an external momentum exchange to accelerate survives in Le 2026c (Bondi balance).
5. **Semiclassical stability of superluminal bubbles.** Hiscock 1997, Finazzi–Liberati–Barceló 2009 and Coutant et al. 2012 (1+1) find divergence or exponential growth at the front (white) horizon. González-Díaz 2000 finds a finite RSET in a Misner-extended 2D vacuum. Barceló et al. 2022 argue that in 2+1 and higher dimensions the accumulation is confined to isolated points and "aerodynamic" shapes and trajectories can tame it. Open: no 3+1 renormalized stress tensor has been computed.
6. **Applicability of Olum 1998 to warp drives.** Shoshany & Snodgrass 2024 argue its generic condition and "fastest path" definition fail for drives with Riemann-flat passenger regions; Graham & Olum 2007 state that achronal ANEC alone does not forbid Olum-type local superluminality. This bears on how claim (g) must be phrased (see Part C, assessment).
7. **Energy-condition violation as a frame effect.** Carneiro et al. 2022 (TEGR) suggest negative energy "may be a reference problem" because static observers measure positive source energy. The NEC is frame-independent and violated (SSV 2022; Le 2026b certified bounds). Settled: frame choice hides negative energy from one observer family only.
8. **"Negative energy is not mandatory" in matter-sourced Alcubierre metrics (Abellán, Bolívar & Vasilev 2023; Santos-Pereira et al. 2021).** The derivations force the transverse shift gradient to vanish (planar or Burgers profiles), which removes the localized bubble and gives ρ = 0, in agreement with identity (a). For localized one-component shifts on flat slices, ρ ≤ 0 is an identity. Status: resolved by the identity; the papers' headline wording overstates their results.
9. **Positive-energy reading of the irrotational Rodal drive.** Rodal 2025 reports global Type I and predominantly positive invariant energy; Le 2026b certifies NEC violation in its wall and finds the Eulerian frame misses ≈73% of sampled WEC violations; Le 2026a finds 9/50 NEC and 46/50 DEC probe violations. Consistent: the drive is Type I and energy-condition violating.
10. **Curvature-invariant magnitudes.** Rodal 2023 and 2024 report that Mattingly et al. 2021 underrepresent invariants by 8–16 and 21 orders of magnitude. No reply found.
11. **Global hyperbolicity of superluminal drives.** Alcubierre 1994 states that any 3+1 metric with positive-definite γ_ij is globally hyperbolic; Barzegar–Buchert–Vigneron 2026 (Theorem IV.7) state a superluminal R-Warp model switched on from rest cannot be globally hyperbolic; Finazzi et al. 2009 find Cauchy horizons in dynamical superluminal drives. The claims concern different constructions (eternal versus switched-on); the project's global time function (I19) establishes stable causality on one rail, a weaker property that should be stated as such. **Verification note (2026-09-26, `../verification/v3_moving_patterns.md`, I19):** for flat-slice lapse–shift metrics with α > 0 and α + |β| bounded, every t-slice is a Cauchy surface: t is a time function, so the spacetime is strongly causal; bounded coordinate light speed keeps a causal curve in a compact set over any finite t-interval; non-imprisonment then forces every inextendible causal curve across every slice. A switched-on superluminal pattern with bounded fields is therefore globally hyperbolic, and a Killing horizon coexists with global hyperbolicity (flat-front test pattern; Kruskal is the classic example). The verifier reports that BBV's proof of Thm IV.7 assumes 'globally hyperbolic ⇒ no horizons'. Status: **disputed**. Read BBV §IV (definitions of the R-Warp model and the proof) in full before citing Thm IV.7; the book states the bounded-field sufficient condition with its proof.
12. **Non-compact membrane drives (Huey 2024).** A WEC-satisfying superluminal toy model outside the smooth, compact, asymptotically flat hypotheses of the no-go theorems. Open as to physical realizability (quantum effects and stability not treated).
13. **Averaging identities on curved backgrounds (Garattini & Zatrimaylov 2025).** WEC and NEC hold "up to a total divergence term that averages to zero"; Le 2026b notes divergence identities do not give pointwise satisfaction. Open.
14. **Quantum inequalities and shortcuts.** Pfenning & Ford 1997 and Everett & Roman 1997 apply flat-space QIs locally; Krasnikov 2003 disputes that QIs forbid shortcuts (Part C).

### F.2 Quantum inequalities, ANEC and causality

1. **Non-perturbative superluminal censorship.** VBL98 v1 claimed "Superluminal travel requires violations of the averaged null energy condition (ANEC)" for asymptotically flat spacetimes. v2 abandoned the argument, which had "become bogged down in issues of considerable technical complexity". GW00 showed the perturbative light-cone comparison is gauge dependent. The rigorous replacement is GW00 Theorem 1 in Galloway's null-line form combined with GO07 Lemma 1.
2. **Olum's definition of superluminal travel.** SS24 (Sec. 4.2) argues that it misses Riemann-flat passenger regions (the generic condition fails), that neighbouring paths are equally fast, and that superluminal paths can be timelike. K03 notes that weak minima fail the definition. GO07 shows that achronal ANEC does not exclude Olum-type (local) superluminality.
3. **Does achronal ANEC rule out warp drives?** KS20 (Sec. 5): "By Olum's earlier proof [180], this theorem also prohibits warp drive spacetimes." GO07 (Sec. IV.D): "additional constraints are necessary to rule out superluminal communication." Resolution in this inventory: achronal ANEC excludes *global* leads (via GW00 and a null line) and compactly generated CTCs, and leaves *local* advances in place.
4. **QI-based unphysicality of shortcuts.** FR96, ER97 and Pfenning–Ford 1997 infer Planck-thin walls and huge E_tot. K03 disputes each step (Weyl dominance, periodic identifications, sub-Planckian layers).
5. **Status of achronal ANEC in curved spacetime.** Test-field violations exist (UO10; Visser's anomaly, discussed in GO07). The self-consistent version is a conjecture (GO07), proven at first order in ħ from the GSL (W10) and for a free scalar on NEC backgrounds (KO15). W10 flags failure once gravitons are quantized (shear-squared renormalization), and proposes a shear-inclusive ANEC.
6. **Universality of QIs.** Interacting domain-wall systems violate QIs (OG03); 2D CFTs obey null QEIs (FH05); 4D free fields have no null-segment QI (FR03).
7. **Averaged satisfaction by divergence terms.** GZ25 claims WEC and NEC hold "up to a total divergence term that averages to zero". Le26 states such identities do not establish pointwise satisfaction.
8. **Origin of WEC violation.** SS24 calls it likely an artefact of the metric class. SSV22 proves NEC violation for the entire Natário class. The non-unit-lapse NEC question remains open (SSV22 App. B; SS24 Sec. 4.1).

### F.3 Traversable wormholes

1. **Quantifying exotic matter.** The VKD volume integral (4πr²dr measure) goes to zero while the ANEC line integral stays finite. Nandi–Zhang–Kumar contest the measure and propose √(−g₄)d³x. Fewster–Roman show quantum inequalities confine VKD-type wormholes to submicroscopic size or extreme scale hierarchies. Which quantifier is physical is unresolved; Kar–Dadhich–Visser leave it as "a task for the future".
2. **Einstein–Dirac–Maxwell wormholes.** Existence of the symmetric BSKR solutions is refuted by Danielson et al. (non-C³ metric, spurious sources) and discussed by the authors (2022). The "no exotic matter" wording is contested by Bolokhov et al., and Konoplya–Zhidenko retitled their paper. Smooth asymmetric solutions exist (KZ 2022). Kain (2023a) finds them non-traversable dynamically, and semiclassical validity at Planck-order throat curvature is questioned (Bolokhov et al.). Open: whether any stable, traversable EDM configuration exists.
3. **Beyond-Horndeski stable wormholes.** Linear high-energy stability is achieved (Franciolini et al.; MRV 2019, 2023). The tachyonic sector is unconstrained, the explicit example propagates superluminally in the angular direction, and a UV completion with standard analyticity is open.
4. **Higher-curvature "no exotic matter" wormholes.** The KKK stability claim is refuted by Cuyubamba–Konoplya–Zhidenko, and no counter-rebuttal was found in this search. The interpretive dispute (Hochberg–Visser's "semantic games" against the effective-stress framing of Lobo–Oliveira and KKK) persists. The "4D EGB" constructions inherit the dispute over whether that theory exists in 4D (Gurses–Sisman–Tekin).
5. **Rotation as stabiliser.** Second-order slow-rotation results indicate stabilisation of the Ellis–Bronnikov radial mode. Full non-perturbative radial stability and the quadrupole sector are not yet settled. The full text of Azad et al. 2025 (arXiv:2509.22118v1) reports, from a cited 2024 follow-up (Phys. Rev. D 109, 124051; UNVERIFIED here), that J_c decreases with the asymmetry parameter only up to C ≈ 0.5 and grows beyond it, and that a second unstable branch emerges from a zero mode; "the radial instability is conjectured to disappear."
6. **Achronal ANEC.** It is a conjecture in its self-consistent form (Graham–Olum), proven for a free scalar to first order in curvature on NCC backgrounds (Kontou–Olum). SNEC and DSNEC restrictions on long wormholes (Freivogel–Krommydas; Kontou 2024) rest on free-field Minkowski bounds.
7. **Thin-shell equation of state.** Whether β₀² < 0 or |β₀| > 1 is physically admissible awaits a microphysical model of the shell (Poisson–Visser).
8. **Chronology protection.** Kim–Thorne versus Hawking on the quantum-gravity cutoff; Visser's "defense in depth" versus the Roman ring.

---

# Part G. UNVERIFIED items

### G.1 Warp drives and shortcut corridors

- Abellán, Bolívar & Vasilev, Eur. Phys. J. C 83, 7 (2023) and Class. Quantum Grav. 41, 105011 (2024): journal records verified through Crossref; arXiv identifiers not identified; content from abstracts and search summaries only.
- Bolívar, Abellán & Vasilev, Ann. Phys. 481, 170147 (2025): title and journal verified through Crossref; content from a search-engine summary only.
- Chowdhury, "Warp Drives and Martel–Poisson charts": EPJC acceptance per arXiv comments; volume and article number not verified.
- White, Vera, Sylvester & Dudzinski 2025: IOP abstract read; no arXiv version found; full text not read.
- Abstract-level entries (content beyond the abstract not checked): Hiscock 1997, Clark–Hiscock–Larson 1999, González-Díaz 2000, Loup et al. 2001, Natário 2006, Barceló–Finazzi–Liberati 2010, Coutant et al. 2012, Mattingly et al. 2021, Rodal 2023 and 2024, SSV tractor beams 2021, Carneiro et al. 2022, Pieri 2023, Huey 2024, Garattini & Zatrimaylov 2024–2025, Chowdhury 2025, Sajeendran & Ralph 2025, Rodal 2025 (read at abstract level plus Le's evaluation), Celmaster & Rubin 2025, Rodal 2025 (metamaterial), Buchert & Frackowiak 2026, Rodal 2026 (birefringent), Gergely 2026 (abstract plus a text search), Martín-Moruno & Visser 2018/2021, Jusufi & Lobo 2026.
- Le 2026c: abstracts of v1–v4 read; the v1 and v4 PDFs were downloaded, and results quoted come from the abstracts.
- "Santiago, Schuster & Visser ... ADM mass / momentum papers": the ADM-mass paper is verified; no separate SSV paper on warp-drive momentum was found. The Eulerian flux is treated in SSV 2022 §4.2 and ADM momentum in Barzegar, Buchert & Vigneron 2026 Thm IV.19.
- Garattini & Zatrimaylov, arXiv:2502.13153: Le 2026a cites it as "Positive-energy warp drive in a De Sitter universe"; the version that carried this title was not identified.
- Lentz 2021: the DEC statement and horizon onset are taken from a text search of v2; the energy estimates were not checked.
- Fell & Heisenberg 2021: abstract plus a text search; the decomposition details are taken from SSV 2022's reading.
- Harold White's earlier "warp field mechanics" reports (2003, 2011, 2013) were not surveyed.

### G.2 Quantum inequalities, ANEC and causality

- **Fewster & Roman erratum**, Phys. Rev. D 80, 069903 (2009): existence confirmed via Crossref; content not read.
- **Pfenning & Ford 1997** (gr-qc/9702026): covered by another cluster. Its wall figure ("a few hundred Planck lengths") is cited here only through KS20.
- **Krasnikov 1998** (construction-time result), **Borde 1987** (focusing theorem), **Galloway's null splitting theorem**, **Tipler 1976/77**, **Flanagan & Wald 1996**, **Wald & Yurtsever 1991**, **Visser 1995 (scale anomaly)**: cited only through the verified papers that quote them; originals not read.
- **Barzegar & Buchert**, **Barzegar, Buchert & Vigneron**, **Fell & Heisenberg**, **Rodal 2025** (2512.18008, abs page parsed but paper not read), **Garattini & Zatrimaylov 2024** (2408.04495, abs page parsed only): mentioned in Le26 or found in searches; outside this cluster's sections.
- **Everett 1996 and Hawking 1992**: no arXiv versions. The APS abstract pages returned only paraphrases through WebFetch (direct retrieval blocked by Cloudflare). Verbatim text comes from published-article PDFs hosted by third parties (if.ufrj.br; archive.org), whose text layers garble some mathematical symbols.
- **PF98 eq. (48)**: the coefficient and superscript placement of the g_tt term are reconstructed from the PDF text layer.
- **FKK22 "B ≪ 1"**: the relation symbol was lost in the text layer and is reconstructed from context.
- **"Fewster & Kontou" review**: the brief named "Fewster & Kontou / Kontou & Sanders 2020". The 2020 CQG review verified here is by Kontou & Sanders; no separate Fewster–Kontou review was searched.
- **Journal references** for FF21 and FFK21 come from Crossref; the arXiv pages show none.

### G.3 Traversable wormholes

1. **Hawking1992** and **KimThorne1991**: only the INSPIRE/APS abstracts were read. Every statement beyond the abstract (formulas, the precise boost/area quantities, the detailed spacetime example) is UNVERIFIED (full text not accessed).
2. **MorrisThorne1988, OCR-derived numerics.** The ½ exponents in R_s ≳ 1×10¹¹ m (b₀/10 m)^{1/2} and trip time ≈ 7 days (R_s/10¹¹ m)^{1/2} (Eqs. A18, A27), and the exact form of the traversal time in Eq. (A31), are read from a degraded scan. They are UNVERIFIED at the symbol level; prose statements and the equations quoted as legible are verified.
3. **MorrisThorneYurtsever1988, Casimir plate separation.** The exact numerical prefactor in s ≈ (…)^{1/4}(r₀ l_P)^{1/2} is garbled in the OCR, and only the scaling and the quoted s ~ 10⁻¹⁰ cm at r₀ = 1 AU are verified. Ford–Roman (1996, Sec. 4.5) independently state that "MTY calculate r₀ ≈ 1 A.U. for a plate separation of s ≈ 10⁻¹⁰ cm".
4. **MaldacenaMilekhinPopov2023, Eq. (5.40).** The exact prefactor of ℓ in terms of r_e, α, q, G_N is garbled in the text extraction. Only the scaling ℓ ∝ q² l_p (Sec. 5.4) is used.
5. **Garattini2019, Eq. (26).** The form r₁² = π³l_p²/90 is read from a layout-garbled extraction (UNVERIFIED at the prefactor level). The Planck-size conclusion is quoted verbatim.
6. **Abstract-level only** (full text downloaded but derivations not re-traced): HochbergVisser1998PRD, KontouOlum2015, BronnikovFabrisZhidenko2011, BronnikovKonoplyaZhidenko2012, CremonaPirottaPizzocchero2019, BronnikovStarobinsky2007, KantiKleihausKunz2011, Khoo2024, Azad2025, KanaiMaedaYoshida2025, Kain2023b, LiuEtAl2023, Visser1993, Visser1997. GursesSismanTekin2020 is abstract-only, with no full text downloaded.
7. **HochbergPopovSushkov1997, validity.** The statement that throat sizes of 10⁻²–10² l_P put the solutions outside the reliable semiclassical regime is my inference from the reported numbers, not a claim made in the paper.
8. **Regularised 4D EGB.** Whether the regularised scalar-tensor version used by LiuEtAl2023 escapes the Gurses–Sisman–Tekin objection is not verified here.
9. **2019–2026 f(R,T), f(Q), f(R,L_m) and non-commutative wormhole papers.** Seen only as search-result titles; none were read, and none are inventoried. Their design content is UNVERIFIED.
10. **Corrections to the task list.** Evseev & Melichev 2018 (arXiv:1711.04152) is a **Horndeski** no-go ("No static sphericaly symmetric wormholes in Horndeski theory"), not a beyond-Horndeski stability result. The beyond-Horndeski results are Mironov–Rubakov–Volkova and Franciolini et al. Rubakov's "Can Galileons support Lorentzian wormholes?" is arXiv:1509.08808 (Theor. Math. Phys. 187, 2016); arXiv:1601.06566 is the 4D follow-up "More about wormholes in generalized Galileon theories". Both Visser 1989 papers are confirmed as arXiv:0809.0907 (PRD 39, 3182) and arXiv:0809.0927 (NPB 328, 203), uploaded in 2008.

From the second, independent reading of the wormhole cluster: Hawking 1992 and Kim–Thorne 1991 beyond their abstracts; OCR-limited prefactors in Morris–Thorne and MTY; the volume and pages of Rubakov's Theor. Math. Phys. paper (seen only in a search snippet); the Azad et al. Phys. Rev. D 109, 124051 (2024) follow-up, known only through a citation in Azad et al. 2025; the Graham–Olum abstract wording differs between the arXiv abstract page ("sufficient to rule out wormholes and closed timelike curves") and the pinned v2 PDF ("sufficient to rule out closed timelike curves and wormholes connecting different asymptotically flat regions"); the PDF wording matches Theorem 1's simple-connectedness restriction.
