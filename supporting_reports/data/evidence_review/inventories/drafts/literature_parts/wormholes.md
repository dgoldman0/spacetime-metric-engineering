# Traversable wormholes — design-strategy literature inventory

Cluster: traversable wormholes. Compiled 2026-09-26.

## Verification method and conventions

- **arXiv papers.** Each abstract page `https://arxiv.org/abs/<id>` was fetched directly over HTTP on 2026-09-26 and parsed from the page HTML (`citation_title`/`citation_author` meta tags, the abstract block, the "Journal reference" cell, the DOI meta tag, and the "Submission history" block). The full text was then downloaded at the pinned version from `https://arxiv.org/pdf/<id>v<N>` and converted with `pdftotext`; every full-text quote below is copied from that conversion. The pinned version is the latest version listed on 2026-09-26. Where the arXiv page carries no journal reference, the publication data come from the INSPIRE-HEP API record (`https://inspirehep.net/api/literature?q=arxiv:<id>`), fetched the same day and labelled as such.
- **Pre-arXiv papers.** Title, authors, publication data and abstract come from the INSPIRE-HEP API record looked up by DOI (abstract text supplied there by APS/AIP). Full text: Morris & Thorne 1988 from a scanned copy of the AJP PDF hosted at `https://materias.df.uba.ar/rga2019c2/files/2019/11/MT.pdf`; Morris, Thorne & Yurtsever 1988 from Caltech AUTHORS (`https://authors.library.caltech.edu/records/m644f-tbz27`, file `MORprl88.pdf`). Both are image scans, so their text was read through `tesseract` OCR. Prose quotes from them are reliable, while formulas are given in cleaned form and flagged "(OCR-cleaned)". Hawking 1992 and Kim & Thorne 1991 were checked at abstract level only.
- **Tags.** [identity/theorem] = holds as an identity or proven theorem inside the paper's assumptions; [derivation] = derived explicitly in the text; [numerical] = obtained numerically; [claim] = asserted without a full derivation in the paper, or not checked here.
- **Notation.** Static spherically symmetric (Morris–Thorne) form: ds² = −e^{2Φ(r)}dt² + dr²/(1 − b(r)/r) + r²dΩ². b = shape function, Φ = redshift function, so e^{Φ} is the lapse of the static slicing. The throat sits at r₀ = b(r₀). ρ = energy density, τ = radial tension = −p_r, p or p_t = lateral pressure. All components are measured by static observers in the static orthonormal frame, where the stress tensor is diagonal.

---

## A. Foundations: metric-first design of static wormholes

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
- **Relation to active-rail results:** (c) The static shell stress is diagonal (Type I). The throat's K^τ_τ equals the magnitude of the four-acceleration of the static shell (Eq. 5.4). The jump in the lapse gradient across the shell is thus what sources ϑ. Eiroa et al. (2025) show this same jump fixes the radial tide on a crossing passenger.
- **Key quote:** "The stability analysis places constraints on the equation of state of the exotic matter that comprises the throat of the wormhole." (abstract v1)

---

## B. Thin-shell stability: equation of state as the stability knob

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

## C. General theorems: where the NEC must fail

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
- **Relation to active-rail results:** The same Raychaudhuri bookkeeping locates NEC demand in the rail: a surface where a null congruence turns from converging to diverging requires R_ab l^a l^b ≤ 0 there. The wormhole throat is marginally anti-trapped; the rail's front light surface (f) is a trapping structure for overtaken light. The two are opposite sides of one diagnostic.
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
- **Citation:** Phys. Rev. D 76, 064001 (2007); DOI 10.1103/PhysRevD.76.064001; arXiv:0705.3193v2 (read v2, 27 Aug 2007). Submission history: [v1] Tue, 22 May 2007; [v2] Mon, 27 Aug 2007 ("qualify conditions on theorem 1"). Verified via https://arxiv.org/abs/0705.3193 on 2026-09-26.
- **Design parts and knobs:** whether the null geodesics through the wormhole are achronal; simple connectedness.
- **Knob → physics relations:**
  - [claim] Condition 1 (self-consistent achronal ANEC) is conjectured to hold in all semiclassical systems.
  - [identity/theorem] Given Condition 1 and the generic condition, topological censorship holds in simply connected, asymptotically flat, globally hyperbolic spacetimes (Theorem 1). This rules out wormholes joining two asymptotic regions. Tipler-type no-time-machine results follow as well (Theorem 2).
  - [derivation] Counterexample showing the limit of the theorem: a static wormhole connecting a region to itself whose throat is longer than the exterior distance between the mouths. Its fastest paths through the wormhole are chronal, so the theorem does not exclude it.
- **Method / verification standard:** Analytic, conditional on Condition 1.
- **Scope and caveats:** Condition 1 is a conjecture, supported by the absence of known violations.
- **Disputes, refutations, later corrections:** Proven in curved backgrounds obeying the null convergence condition (NCC), for a free scalar to first order in curvature, by Kontou & Olum 2015.
- **Relation to active-rail results:** (g) Directly. The project's result that achronal ANEC excludes quantum sources for any lead over light is the rail version of this "long wormhole only" boundary.
- **Key quote:** "…requiring only that there is no self-consistent space-time in semiclassical gravity in which ANEC is violated on a complete, {\em achronal} null geodesic. We indicate why such a condition might be expected to hold and show that it is sufficient to rule out wormholes and closed timelike curves." (abstract v2)

### KontouOlum2015 — E.-A. Kontou, K. D. Olum (2015), "Proof of the averaged null energy condition in a classical curved spacetime using a null-projected quantum inequality"
- **Citation:** Phys. Rev. D 92, 124009 (2015); DOI 10.1103/PhysRevD.92.124009; arXiv:1507.00297v2 (read v2, 27 Oct 2015). Submission history: [v1] Wed, 1 Jul 2015; [v2] Tue, 27 Oct 2015. Verified via https://arxiv.org/abs/1507.00297 on 2026-09-26.
- **Design parts and knobs:** a massless minimally coupled scalar; a background obeying the NCC; first order in the Riemann tensor.
- **Knob → physics relations:**
  - [identity/theorem] A null-projected QI implies ANEC on achronal geodesics in such backgrounds (abstract).
- **Method / verification standard:** Analytic proof (abstract-level check; full text downloaded but not re-traced).
- **Scope and caveats:** Free scalar only, first order in curvature, background obeying the NCC. The self-consistent case is not covered.
- **Disputes, refutations, later corrections:** None found.
- **Relation to active-rail results:** (g) Supplies the proven piece behind achronal ANEC.
- **Key quote:** "A null-projected quantum inequality can be used to prove the averaged null energy condition (ANEC), which would then rule out exotic phenomena such as wormholes and time machines." (abstract v2)

---

## D. How much exotic matter: volume quantifiers and their dispute

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
- **Relation to active-rail results:** (b)/(g) Stress-only (lapse-carried) NEC violation with ρ = 0 escapes energy-density QIs. It is caught only by null-contracted bounds. Any QI audit of a lapse-supported rail source therefore has to use T_ab k^a k^b, not ρ.
- **Key quote:** "One lesson to be drawn from our results is that simply concentrating the exotic matter, in a classical analysis, to an arbitrarily small region around the wormhole throat is, by itself, not sufficient to guarantee both traversability and consistency with (or evasion of) the quantum inequality bounds." (Sec. 9)

---

## E. Quantum-field constraints on geometry

### FordRoman1996 — L. H. Ford, T. A. Roman (1996), "Quantum Field Theory Constrains Traversable Wormhole Geometries"
- **Citation:** Phys. Rev. D 53, 5496–5507 (1996); DOI 10.1103/PhysRevD.53.5496; arXiv:gr-qc/9510071v1 (read v1, 31 Oct 1995). Submission history: [v1] Tue, 31 Oct 1995. Verified via https://arxiv.org/abs/gr-qc/9510071 on 2026-09-26.
- **Design parts and knobs:** throat radius r₀; the thickness a₀ of the negative-energy band; the sampling fraction f; MT example geometries; the MTY Casimir plates (separation s, offset δ of the plates from r₀).
- **Knob → physics relations:**
  - [derivation] QI for a static geodesic observer, ρ₀ ≳ −c/τ₀⁴ with c = 3/(32π²). With τ₀ = f r₀ this gives r₀ ≲ l_p/(2f²) ≈ 10⁴ l_p for f ≈ 0.01 (Eqs. 50–51, MT Box 2 wormhole).
  - [derivation] "Absurdly benign" band: a₀ ≲ 8f⁴(r₀/l_p)^{1/3} l_p (Eq. 69). For r₀ ≈ 1 m this gives a₀ ≲ 10¹⁴ l_p ≈ 10⁻²¹ m. "So even with a throat radius the size of a galaxy, the negative energy must be distributed in a band no thicker than about 10 proton radii."
  - [derivation] MTY Casimir wormhole: r₀ ≳ f²s² (in Planck units; Eq. 88) is satisfied. The plates, however, sit where |g_tt| ≈ δ²/M², so infalling radiation is blueshifted by M/δ ≈ 10²³: "A static observer just outside the plates would likely be incinerated by infalling radiation."
- **Method / verification standard:** Analytic, flat-space QI applied locally.
- **Scope and caveats:** Assumes the flat-space QI holds on scales small compared with curvature radii and boundary distances (argued, not proven).
- **Disputes, refutations, later corrections:** Refined by Fewster & Roman 2005 (null-contracted QI). Reviewed in Kontou 2024.
- **Relation to active-rail results:** (d) A deep lapse contrast multiplies the energy of infalling radiation by the lapse ratio. This passenger hazard follows any design that places people or hardware at small lapse relative to the exterior.
- **Key quote:** "Our analysis implies that either the wormhole must be only a little larger than Planck size or that there is a large discrepancy in the length scales which characterize the wormhole. In the latter case, the negative energy must typically be concentrated in a thin band many orders of magnitude smaller than the throat size." (abstract v1)

### FreivogelKrommydas2018 — B. Freivogel, D. Krommydas (2018), "The Smeared Null Energy Condition"
- **Citation:** JHEP 12 (2018) 067 (journal from INSPIRE); DOI 10.1007/JHEP12(2018)067; arXiv:1807.03808v4 (read v4, 19 Apr 2021). Submission history: [v1] Tue, 10 Jul 2018; [v2] Thu, 12 Jul 2018; [v3] Thu, 18 Apr 2019; [v4] Mon, 19 Apr 2021. Verified via https://arxiv.org/abs/1807.03808 on 2026-09-26.
- **Design parts and knobs:** smearing length τ along a null geodesic; G_N; an O(1) constant B.
- **Knob → physics relations:**
  - [claim] Proposed bound ⟨T_kk⟩ ≥ −B/(G_N τ²) (Eq. 4), valid where perturbative quantum gravity holds.
  - [claim] Consequences: "regions of negative energy density are never strongly gravitating, and … isolated regions of negative energy are forbidden."
  - [claim] ANEC "cannot be used to exclude wormholes in the same universe", which motivates a local bound.
- **Method / verification standard:** Proposal checked on examples. It is a conjecture, not a theorem.
- **Scope and caveats:** Free fields in the examples. Curved-space validity is assumed.
- **Disputes, refutations, later corrections:** The double-smeared version (DSNEC) is discussed in Kontou 2024.
- **Relation to active-rail results:** (g) A candidate finite-segment complement to achronal ANEC, relevant where rail null segments are not complete.
- **Key quote:** "If correct, our bound implies that regions of negative energy density are never strongly gravitating, and that isolated regions of negative energy are forbidden." (abstract v4)

### Kontou2024 — E.-A. Kontou (2024), "Wormhole restrictions from quantum energy inequalities"
- **Citation:** Universe 10, 291 (2024) (journal from INSPIRE); DOI 10.3390/universe10070291; arXiv:2405.05963v2 (read v2, 8 Jul 2024). Submission history: [v1] Thu, 9 May 2024; [v2] Mon, 8 Jul 2024. Verified via https://arxiv.org/abs/2405.05963 on 2026-09-26.
- **Design parts and knobs:** "short" versus "long" wormholes; the throat length ℓ; the AdS₂ radius r_e; the number of fields N (flux q).
- **Knob → physics relations:**
  - [claim] (review) Achronal ANEC prohibits wormholes as "shortcuts". "'Long' wormholes circumvent the problem of the achronal ANEC, as there are no complete achronal null geodesics passing through them."
  - [derivation] New result: applying the DSNEC to the MMP long wormhole, violation requires q ≳ r_e/ℓ (Eq. 103). "As r_e ≪ ℓ, the DSNEC is easily violated." The schematic bounds are ⟨T₋₋⟩_SNEC ≥ −4B/(ℓ_pl²ℓ²) and ⟨T₋₋⟩_DSNEC ≥ −N/(ℓ³r_e) (Eq. 104).
  - [claim] The author cautions that "the SNEC and DSNEC bounds are for free massless scalars on Minkowski".
- **Method / verification standard:** Review plus an order-of-magnitude application.
- **Scope and caveats:** No QEIs exist for self-interacting fields in 4D; a curved-space DSNEC has not been derived.
- **Disputes, refutations, later corrections:** An open question: whether DSNEC-type bounds constrain the MMP length.
- **Relation to active-rail results:** (g) Directly. It states the short/long dichotomy the rail result reproduces: quantum sources are allowed only when the route through the structure is slower than the exterior light path.
- **Key quote:** "While the achronal ANEC seems to prohibit wormholes as “shortcuts”, a different kind of wormhole still seems possible: the ‘long’ wormhole. This is a wormhole where it takes longer for an observer to travel through the throat than the outside spacetime." (Sec. 1, v2)

---

## F. Self-consistent semiclassical construction

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

## G. Stability versus matter model (GR with phantom/ghost scalars; rotation)

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

## H. Modified gravity: moving the NEC violation into the gravitational sector

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

## I. Quantum-sourced wormholes: long versus short

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
  - [derivation] Validity requires ℓ ≪ q³ l_p (Eq. 5.43). The energy gap is ~1/(q² l_p) and the binding energy ~1/(q l_p).
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

## J. Einstein–Dirac–Maxwell wormholes and their dispute

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

## K. One-parameter bridge between black hole and wormhole

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

## L. Chronology

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
- **Citation:** Phys. Rev. D 46, 603–611 (1992); DOI 10.1103/PhysRevD.46.603. Pre-arXiv. Verified via INSPIRE API (`q=doi:10.1103/PhysRevD.46.603`, abstract from APS) on 2026-09-26. Full text not read. INSPIRE capitalises the title as "The Chronology protection conjecture".
- **Design parts and knobs:** a compactly generated Cauchy horizon; the boost and area increase around closed null geodesics.
- **Knob → physics relations:**
  - [identity/theorem] (abstract) If causality violation develops from a noncompact initial surface, the averaged weak energy condition must be violated on the Cauchy horizon, so finite lengths of cosmic string cannot create CTCs.
  - [claim] (abstract) The stress tensor "would get very large if timelike curves become almost closed", and back-reaction would prevent CTCs.
- **Method / verification standard:** Abstract-level only.
- **Scope and caveats:** Finite causality-violating region without curvature singularities.
- **Disputes, refutations, later corrections:** Kim & Thorne 1991 (cutoff); Visser 1997 (Roman ring evades the semiclassical argument).
- **Relation to active-rail results:** None visible among (a)–(g).
- **Key quote:** "These results strongly support the chronology protection conjecture: The laws of physics do not allow the appearance of closed timelike curves." (abstract, INSPIRE)

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

## Cross-paper design findings (summary of the verified record)

1. **Geometry-first design with lapse/shape separation.** In static slicing (zero shift, zero extrinsic curvature of the slices), the energy density is fixed by spatial geometry alone. For Morris–Thorne ρ = b′/(8πr²); for the generic static throat ρ has no φ (Hochberg–Visser 1997). The lapse enters stresses only. The spatially Schwarzschild wormholes of VKD 2003 have ρ ≡ 0, and all NEC-violating stress there is lapse-supported. Fewster–Roman 2005 show that such stress-only violation is caught by null-contracted quantum inequalities, not by energy-density ones.
2. **The NEC violation is geometric and located by null expansions.** Flare-out forces NEC violation at or near every throat (static or dynamic; two throats when time-dependent). Moving the violation into a scalar, higher-curvature or spinor sector relabels which term of the total source violates it. Globally, averaged null energy along the fastest (achronal) curves decides whether any shortcut exists. Quantum-sourced wormholes exist only as "long" wormholes whose transit time is at least the exterior light time (GJW, MMP, FGWM, Kontou 2024).
3. **Stability is decided by the matter model and by the boundary conditions of the stability analysis.** Thin shells: stability needs β₀² < 0 for a₀ > 3M, or M ≤ 0 globally. Ghost scalars: exactly one unstable mode with growth time ≈ 0.6–0.85 r_throat/c. A passenger's positive energy collapses the Ellis wormhole. Galileon/Horndeski: no-go. Beyond-Horndeski: high-energy stability achieved, with the tachyonic sector open and superluminal angular speeds in the explicit example. Rotation reduces the Ellis–Bronnikov radial instability (perturbative indication). The KKK stability claim failed once the throat size was allowed to move.
4. **Passenger metrics are design outputs.** MT 1988: tidal ≤ g⊕ gives v ≲ 60 m/s (b₀/10 m), a 1-hour to 200-day trip, and station gravity −Φ′c² ≲ g⊕. MM 2021: a 20g tidal limit forces r_e > 1.5×10⁷ m and a redshift contrast γ ~ 2×10¹², i.e. <1 s proper time against ~10⁴ yr outside, with CMB photons boosted by γ². FR 1996: near-horizon plates blueshift infalling radiation by ~10²³. Eiroa et al. 2025: a jump in K^t_t at a thin layer produces a radial tide independent of speed and separation.

---

## Synthesis table

| Knob/part | Physics relation | Papers | Status |
|---|---|---|---|
| Shape function b(r), throat radius b₀ | ρ = b′/(8πGc⁻²r²); throat tension τ₀ = 1/(8πGc⁻⁴b₀²) ∝ b₀⁻² (≈5×10⁴¹ dyn cm⁻² at b₀ = 10 m) | MorrisThorne1988 | [derivation], exact GR |
| Redshift function Φ (lapse e^Φ) | Absent from ρ; sets τ, p; horizon ⇔ Φ → −∞; station gravity −Φ′c²; radial tide from Φ′, Φ″; Φ′ = 0 gives zero radial tide | MorrisThorne1988; HochbergVisser1997; VisserKarDadhich2003 | [derivation]/[identity/theorem] |
| Flare-out of throat (static) | τ₀ > ρ₀c² at throat; ∫√g e^φ(ρ − τ) < 0 over throat; NEC violated at maxima of φ | MorrisThorne1988; HochbergVisser1997 | [identity/theorem] |
| Throat topology (genus) | ∫√g ρ ≤ χ/4G < 0 for genus ≥ 2; torus ≤ 0 | HochbergVisser1997 | [identity/theorem] |
| Dynamic throat (marginally anti-trapped surface) | T_ab l^a l^b < 0 near each of two throats; temporary suspension incompatible with flare-out; torsion cannot absorb violation | HochbergVisser1998PRL; HochbergVisser1998PRD | [identity/theorem] |
| Achronality of through-going null curves | Achronal ANEC ⇒ no shortcut wormholes joining distinct asymptotic regions; "long" wormholes (chronal curves) allowed | FriedmanSchleichWitt1993; GrahamOlum2007; KontouOlum2015; GaoJafferisWall2017; MaldacenaMilekhinPopov2023; Kontou2024 | [identity/theorem] conditional on self-consistent achronal ANEC (conjecture; partial proof) |
| Exotic-region thickness a₀ | With ρ < 0 allowed: arbitrarily thin (MT); QI: a₀ ≲ 8f⁴(r₀/l_p)^{1/3} l_p (≈10⁻²¹ m at r₀ = 1 m) | MorrisThorne1988; FordRoman1996 | [derivation]; QI assumed valid locally |
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
| Magnetic charge q with massless charged fermions | Casimir-like negative energy; throat length ℓ ∝ q² l_p; validity ℓ ≪ q³ l_p; πℓ > d always (coefficient ≈ 2.35 at large d); unsafe for humans | MaldacenaMilekhinPopov2023; Kontou2024 | [derivation] |
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

## Open disputes in this cluster

1. **Quantifying exotic matter.** The VKD volume integral (4πr²dr measure) goes to zero while the ANEC line integral stays finite. Nandi–Zhang–Kumar contest the measure and propose √(−g₄)d³x. Fewster–Roman show quantum inequalities confine VKD-type wormholes to submicroscopic size or extreme scale hierarchies. Which quantifier is physical is unresolved; Kar–Dadhich–Visser leave it as "a task for the future".
2. **Einstein–Dirac–Maxwell wormholes.** Existence of the symmetric BSKR solutions is refuted by Danielson et al. (non-C³ metric, spurious sources) and discussed by the authors (2022). The "no exotic matter" wording is contested by Bolokhov et al., and Konoplya–Zhidenko retitled their paper. Smooth asymmetric solutions exist (KZ 2022). Kain (2023a) finds them non-traversable dynamically, and semiclassical validity at Planck-order throat curvature is questioned (Bolokhov et al.). Open: whether any stable, traversable EDM configuration exists.
3. **Beyond-Horndeski stable wormholes.** Linear high-energy stability is achieved (Franciolini et al.; MRV 2019, 2023). The tachyonic sector is unconstrained, the explicit example propagates superluminally in the angular direction, and a UV completion with standard analyticity is open.
4. **Higher-curvature "no exotic matter" wormholes.** The KKK stability claim is refuted by Cuyubamba–Konoplya–Zhidenko, and no counter-rebuttal was found in this search. The interpretive dispute (Hochberg–Visser's "semantic games" against the effective-stress framing of Lobo–Oliveira and KKK) persists. The "4D EGB" constructions inherit the dispute over whether that theory exists in 4D (Gurses–Sisman–Tekin).
5. **Rotation as stabiliser.** Second-order slow-rotation results indicate stabilisation of the Ellis–Bronnikov radial mode. Full non-perturbative radial stability and the quadrupole sector are not yet settled.
6. **Achronal ANEC.** It is a conjecture in its self-consistent form (Graham–Olum), proven for a free scalar to first order in curvature on NCC backgrounds (Kontou–Olum). SNEC and DSNEC restrictions on long wormholes (Freivogel–Krommydas; Kontou 2024) rest on free-field Minkowski bounds.
7. **Thin-shell equation of state.** Whether β₀² < 0 or |β₀| > 1 is physically admissible awaits a microphysical model of the shell (Poisson–Visser).
8. **Chronology protection.** Kim–Thorne versus Hawking on the quantum-gravity cutoff; Visser's "defense in depth" versus the Roman ring.

---

## UNVERIFIED items

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
