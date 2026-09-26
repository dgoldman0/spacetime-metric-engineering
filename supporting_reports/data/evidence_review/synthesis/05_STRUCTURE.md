# Book structure, revision 2 (2026-09-26)

This is the working structure for the scaffold. It keeps the discipline that
`03_STRUCTURE.md` derived from the evidence: the design of spacetime
geometry. Revision 1 reorganized 03. Revision 2 applies the coverage map
(`inventory/coverage_map.md`, Parts 2–4) and the synthesis audit
(`audit_synthesis.md`).

## Decisions and their reasons

### Kept from revision 1

1. **Verification sits in Part II (Chapter 13).** Part III labels every
   design-matrix entry as an identity or a measurement, so the verification
   standard comes first (02 §3.2, B1–B7).
2. **The design-matrix framework opens Part III (Chapter 14).**
3. **Part III is organized by design element: lapse, shift, spatial
   geometry.** This split is the ADM split, and the literature attributes
   responses the same way:
   - the Morris–Thorne shape and redshift functions;
   - Santiago–Schuster–Visser and Shoshany–Snodgrass for the shift's energy;
   - Van Den Broeck for the ³R channel.

   Every identity states its class conditions.
4. **Quantum sources get their own chapter (Chapter 23).**

### New in revision 2

5. **Quantum-field groundwork comes before the energy bounds.** The new
   Chapter 5 holds renormalized stress and the anomaly, states and vacuum
   polarization, horizon temperatures, the species bound and validity limits.
   The bounds (Chapter 6) use all of these (coverage §4.1).
6. **Causality conditions open the global-structure chapter (7.1).**
   Topology change and censorship use them.
7. **Each subject has one home.** The coverage map's ten duplications are
   merged:
   - fronts in 18.5;
   - zoning in 14.5;
   - adjustment order in 14.3 and 16.6;
   - speed in 19.2;
   - momentum by radiation in 18.6;
   - scale in 9.3 and Appendix C;
   - reference solutions in Appendix D;
   - single-gate distortion in 28.4.

   Chapter 1 keeps a short preview of performance claims (1.5), whose full
   treatment is 11.3.
8. **The coupling chapter dissolves.** Its general identities move to where
   their prerequisites are:
   - the complete tensor of the axisymmetric flat-slice class, and the shift
     under a varying lapse → 16.5;
   - the adjustment order → 16.6;
   - product geometries → 17.3.

   No chapter now rests mainly on one project's class identities.
9. **Occupants stay in Part II as requirements**: the observables and how to
   compute them from the metric. Designing a flat interior region belongs to
   the shift (16.1), and choosing the occupant clock to the lapse (15.1).
10. **The spherical lapse follows spherical geometry (17.4).** It uses the
    static spherical decomposition.
11. **Orphans are placed:**
    - Bondi mass and momentum → 3.6;
    - smoothness class of a prescription (A11) → 9.4;
    - curvature sectors of modified gravity → 24.6;
    - quantum-sourced wormholes → 23.5;
    - curvature invariants → 10.1;
    - nonlinear energy conditions → 4.5;
    - the exotic-matter measure → 9.2;
    - rest-frame switching by the lapse → 15.1;
    - coupling engineering → 21.2.
12. **Chapter 8 is relieved.** Stability moves to 27.4, modified gravity to
    24.6 and quantum-sourced wormholes to 23.5. The positive-energy debate
    (8.5) states its resolution with forward references to 10.1, 10.3 and
    16.2.
13. **Part IV is consolidated.**
    - Net supply and assemblies merge (Chapter 25).
    - The screening sequence moves to the end of Part IV (26.4), after the
      source-family physics it applies.
    - Ordinary matter stays a chapter (22) only if its missing literature is
      acquired; the list is below.
14. **Section titles name general constructs.** Examples: "flat interior
    regions", "scheduling lapse elements in time", "front shape and normal
    speed", "product and warped-product geometries".
15. **The strategy catalogue (20.1) leads with the literature's strategies.**
    The project's strategies enter as labelled rows.
16. **Appendix A is scoped to its evidence.** Analogue kinematics (Barceló,
    Liberati and Visser) is verified. The laboratory negative-energy
    literature exists in the repo only through the author's own review paper
    (`white_casimir_intersection/negative_energy_modalities_laboratory_qft_paper.tex`),
    whose references are unverified; it must be acquired and verified before
    A.2–A.4 and 23.2 are drafted. Revision 1 claimed this evidence for
    Chapter 24; that claim was wrong.

### Audit additions placed (`audit_synthesis.md` §3.1)

- Complete assembly ledger, including the identity that conservation fixes a
  tensor only up to divergence-free additions → 25.5.
- Semiclassical constraints that no tuning removes → 23.3.
- Principal-part check before fitting a source to G/8π → 27.1.
- Passivity and regularity inside inverse source optimization → 26.3.
- Splitting bulk tension from the signed null deficit → 9.2.
- Out-of-sample tests for fitted closures → 13.3.
- Superposition fails on a shared geometry → 25.4.
- Congruences, not single rays → 2.5 and 13.3.
- Affine parameters for averaged conditions → 6.5.
- Coordinate-normalized magnitudes carry lapse factors → 9.2.

## Reader and layout (default, pending the author)

- **Reader.** Graduate level: GR at the level of a first graduate course, and
  QFT flagged where Chapters 5, 6 and 23 need it.
- **Layout.** Two levels: the core text, plus derivation boxes. Physics-literate
  engineers read the core; GR students read both.

## Claim-status tags

| Tag | Meaning |
|---|---|
| **T** | Theorem: proved, with assumptions stated |
| **D** | Derived in this book and symbolically checked |
| **L** | Established literature result (cite at a pinned version) |
| **C** | Conjecture |
| **M** | Measured on one design: labelled, scoped, never a law |
| **H** | Heuristic |
| **P** | Vetted engineering practice, with scope and basis |

## Conventions

- **Units.** Signature (−,+,+,+). Geometric units G = c = 1, with ħ explicit
  in the quantum chapters; ℓ_P = (ħG/c³)^{1/2}. A demand at unit length L
  converts to SI by E ×c⁴L/G and S ×c⁴/(GL²).
- **Indices.** Greek for spacetime, Latin for space; hats mark
  orthonormal-frame components.
- **Curvature.** MTW Riemann and Ricci; G_{μν} = 8πT_{μν}.
- **3+1 split.** ds² = −α²dt² + γ_ij(dx^i + β^i dt)(dx^j + β^j dt).
  - Normal observers move at dx^i/dt = −β^i, so carriage at speed v along z
    has β^z = −v.
  - K_ij = −(1/2α)(∂_tγ_ij − D_iβ_j − D_jβ_i), and K = −∇_μ n^μ.
  - ρ = T_{μν}n^μn^ν, j_i = −γ_i^μ T_{μν}n^ν, S_ij = γ_i^μγ_j^νT_{μν}.
- **Energy conditions.** Hawking–Ellis types are written I–IV. The pointwise
  conditions are NEC, WEC, SEC and DEC; the averaged ones ANEC and AWEC; the
  quantum ones QEI, QNEC, SNEC and DSNEC.
- **Null vectors** are normalized by u_μk^μ = −1 relative to a stated
  observer.
- **Regions** carry geometric names, and sources carry separate names.
  Mechanisms are described on their own terms; a comparison names the shared
  trait and says where the mechanisms differ.

## Chapters and sections

File stems are given in brackets under `book/`.

### Part I. Foundations  [part1-foundations/]
1. **Spacetime Engineering: The Inverse Problem** [ch01-inverse-problem]
   1.1 Geometry as the engineered object · 1.2 A first tour of canonical
   geometries · 1.3 Two directions of design: geometry first and source first ·
   1.4 What makes it hard · 1.5 Performance inside one spacetime: a preview
2. **Lorentzian Geometry for Design** [ch02-lorentzian-geometry]
   2.1 Causal structure and proper time · 2.2 Observers, frames and tetrads ·
   2.3 Killing vectors, stationarity and conserved quantities · 2.4 Horizons
   and surface gravity · 2.5 Congruences, expansion and focusing
3. **The 3+1 Split** [ch03-three-plus-one]
   3.1 Foliations, lapse and shift · 3.2 Extrinsic curvature · 3.3 The
   constraints read as demand · 3.4 Evolution equations and stresses ·
   3.5 Worked examples · 3.6 ADM, Komar and Bondi masses
4. **Stress-Energy and Its Algebra** [ch04-stress-energy-algebra]
   4.1 Components and observers · 4.2 Hawking–Ellis types and their scope ·
   4.3 Type from 3+1 data · 4.4 Canonical matter models and their types ·
   4.5 Pointwise and nonlinear energy conditions
5. **Quantum Fields on Curved Backgrounds** [ch05-quantum-fields]
   5.1 Renormalized stress and the trace anomaly · 5.2 States and vacuum
   polarization · 5.3 Horizon temperatures · 5.4 The species bound ·
   5.5 Validity limits of semiclassical gravity
6. **Energy Conditions and Quantum Bounds** [ch06-energy-bounds]
   6.1 Quantum violation of pointwise conditions · 6.2 Worldline inequalities
   and quantum interest · 6.3 Null-contracted bounds · 6.4 Smeared and quantum
   null energy conditions · 6.5 Averaged null energy · 6.6 Exact scopes for
   design use
7. **Global Structure: Causality, Topology, Chronology** [ch07-global-structure]
   7.1 Causality conditions and time functions · 7.2 Topology change ·
   7.3 Topological censorship · 7.4 Faster-than-light theorems and their
   definitions · 7.5 Chronology and its protection
8. **The Canonical Engineered Geometries** [ch08-canonical-geometries]
   8.1 Static traversable wormholes · 8.2 Thin-shell and cut-and-paste
   wormholes · 8.3 Warp metrics · 8.4 Krasnikov tubes and superluminal subways ·
   8.5 The positive-energy debate, 2021–2026 · 8.6 The warp–wormhole
   correspondence

### Part II. Specifying and Testing a Geometry  [part2-specifying/]
9. **From Geometry to Demand** [ch09-geometry-to-demand]
   9.1 The geometry fixes the demand · 9.2 The demand ledger · 9.3
   Normalization and absolute scale · 9.4 Smoothness class of a prescription
10. **Testing the Demand** [ch10-testing-demand]
    10.1 Complete tensor, all observers · 10.2 Time dependence and the
    blindness of static checks · 10.3 Transitions to vacuum · 10.4 Matrix
    inequalities and certified bounds between samples · 10.5 Degenerate
    tensors · 10.6 Type as a match to source families
11. **Global Structure and Performance Claims** [ch11-global-performance]
    11.1 Declaring topology, ends and exterior · 11.2 The causality class of a
    design · 11.3 Performance inside one spacetime · 11.4 Coordination and
    control without superluminal signals
12. **Occupants** [ch12-occupants]
    12.1 Occupant observables · 12.2 Computing occupant observables from the
    metric · 12.3 Occupant requirements in crewed designs
13. **Computing and Certifying the Demand** [ch13-certifying-demand]
    13.1 Code verification: manufactured solutions and observed order ·
    13.2 Solution verification aimed at decisions · 13.3 Domains, surrogates,
    reduced models and fitted closures · 13.4 Solver statuses · 13.5 Reference
    solutions for testing

### Part III. How the Physics Responds to Design  [part3-design-response/]
14. **Design Matrices** [ch14-design-matrices]
    14.1 Design elements and physical channels · 14.2 Identity-backed and
    measured entries · 14.3 Coupling, decoupling and adjustment order ·
    14.4 Identities before numerics · 14.5 Zoning and its hazard
15. **The Lapse** [ch15-lapse]
    15.1 Clock, redshift, frames and refractive index · 15.2 Stress without
    energy where the shift is uniform · 15.3 The lapse-only NEC lemma and the
    Komar balance · 15.4 Scheduling lapse elements in time · 15.5 Measured
    examples
16. **The Shift** [ch16-shift]
    16.1 Carriage and flat interior regions · 16.2 Energy density from shear
    and vorticity · 16.3 Momentum and vorticity · 16.4 Null energies at
    shear-layer edges · 16.5 The shift under a varying lapse · 16.6 Adjustment
    order for lapse and shift
17. **The Spatial Geometry** [ch17-spatial-geometry]
    17.1 Curved slices and the three-curvature channel · 17.2 Stretch and
    conformal factors · 17.3 Product and warped-product geometries · 17.4 The
    lapse in static spherical geometries · 17.5 Throats: flare-out cost,
    tension and topology · 17.6 Thin shells and junctions
18. **Moving Structures** [ch18-moving-structures]
    18.1 The pattern frame and Killing energy · 18.2 Light surfaces and
    horizons · 18.3 Overtaken light and matter · 18.4 Front shape and normal
    speed · 18.5 Semiclassical response at fronts · 18.6 Momentum, steering and
    radiation
19. **Scaling Laws** [ch19-scaling]
    19.1 Size · 19.2 Speed and the steady-lane rescaling · 19.3 Wall thickness
    under quantum inequalities · 19.4 Shape
20. **Strategies and Their Price** [ch20-strategies]
    20.1 The catalogue · 20.2 Where the NEC violation goes · 20.3 Class
    choices

### Part IV. Supplying the Demand  [part4-supply/]
21. **The Supply Problem** [ch21-supply-problem]
    21.1 Algebraic range of source families · 21.2 Class-level exclusions
    first · 21.3 Absolute scale
22. **Ordinary Matter and Classical Fields** [ch22-ordinary-matter]
    22.1 Strength-to-energy ratios and the dominant energy condition ·
    22.2 Electromagnetic stresses and confinement · 22.3 Strings, sheets and
    oriented ensembles · 22.4 Junction stress and charged shells · 22.5 Storage
    limits
23. **Quantum Sources** [ch23-quantum-sources]
    23.1 Casimir systems and the mirror's energy · 23.2 States with negative
    energy density · 23.3 Field counts and constraints no tuning removes ·
    23.4 Vacuum polarization and the anomaly as sources · 23.5 Quantum-sourced
    wormholes: long and short · 23.6 Scope of quantum exclusions
24. **Classical NEC-Violating Fields and Modified Gravity** [ch24-nec-violating-fields]
    24.1 Canonical fields and curvature couplings · 24.2 Higher-derivative
    scalars · 24.3 Stability and no-go results · 24.4 Superluminality and
    ultraviolet completion · 24.5 Algebraic range · 24.6 Curvature sectors of
    modified gravity
25. **Net Supply and Assemblies** [ch25-net-supply-assemblies]
    25.1 NEC-satisfying parts only add to the deficit · 25.2 Accounting
    boundaries and gain chains · 25.3 Holding costs · 25.4 Component tensors on
    one shared geometry · 25.5 Interaction contracts, recoil and the complete
    ledger · 25.6 Function and physical realization
26. **Realizability and Screening** [ch26-realizability]
    26.1 Spending design freedom on sourceability · 26.2 Forward checks of
    simplified designs · 26.3 Realizability and passivity inside the design
    loop · 26.4 A screening sequence with exact scopes

### Part V. Dynamics  [part5-dynamics/]
27. **Dynamics, Back-Reaction and Stability** [ch27-dynamics]
    27.1 Prescribed metrics and solutions · 27.2 Evolving warp spacetimes with
    matter · 27.3 Semiclassical back-reaction · 27.4 Stability of NEC-violating
    sources and wormholes · 27.5 Fields on engineered backgrounds

### Part VI. Method and Frontier  [part6-method/]
28. **Design Studies** [ch28-design-studies]
    28.1 Attribution and sensitivity maps · 28.2 Matched comparisons ·
    28.3 Forks and set-based exploration · 28.4 Single-gate distortion ·
    28.5 Absolute and relative figures of merit
29. **Credibility and Claim Scope** [ch29-credibility]
    29.1 Naming results by the check passed · 29.2 Multi-axis credibility and
    readiness · 29.3 Kinematic and sourcing claims · 29.4 Program hazards
30. **The Frontier** [ch30-frontier]
    30.1 Open sourcing classes · 30.2 Dynamics and stability · 30.3 Quantum
    questions · 30.4 Global questions

### Appendices  [appendices/]
- A. Analogue Systems and Laboratory Negative Energy [appA-laboratory]
- B. Computational Companion [appB-computational]
- C. Units, Scales and Conversions [appC-units]
- D. Reference Solutions and Their Stress Tensors [appD-reference-solutions]

## Literature to acquire and verify before drafting the affected chapters

| For | Needed |
|---|---|
| 2, 3, 4 | Standard texts, read for the definitions the book relies on (MTW; Wald 1984; Hawking–Ellis 1973; Gourgoulhon 2012; Alcubierre 2008; Baumgarte–Shapiro 2010). They are metadata-only now. |
| 3.6, 18.6 | A Bondi–Sachs primary source (Bondi–van der Burg–Metzner 1962; Sachs 1962). |
| 17.6, 22.4 | Israel 1966 junction conditions. |
| 17.3, 22.3 | A string-cloud source (Letelier 1979). |
| 22.1–22.2 | Primary material-strength data; Maxwell-stress and confinement sources. |
| 23.1, 25.3 | QFT models of Casimir plates and their energy (Morris–Thorne–Yurtsever 1988 is verified; Graham–Olum 2005; Costa–Matsas, currently unverified). |
| 23.2, App. A | The laboratory negative-energy literature (squeezed states, Casimir measurements, QET experiments), starting from the author's modalities paper. |
| engineering survey | 19 arXiv identifiers without pinned versions (`coverage_map.md` §2.3). |

## Placement rules for project material

- Project identities appear in general form, with class conditions, as D-
  or T-tagged statements.
- Measured results appear only in "measured on one design" boxes, labelled
  and scoped.
  - Results on the beta075 geometry, and on its static surrogate, appear
    only as cautionary examples.
  - Gate-passing one-space designs (D-lap, D-cmp, D-fr, D-trim) are usable.
- No chapter narrates the project, and no chapter is organized around it.
- Incidents inform practices. The book states the practice, its physical
  basis and its failure mode, without project history.
