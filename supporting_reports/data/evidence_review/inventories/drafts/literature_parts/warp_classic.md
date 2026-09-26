## Part A. Warp-drive design literature, 1994–2012

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
