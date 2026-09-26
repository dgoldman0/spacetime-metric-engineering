# Book structure (revision of 03_STRUCTURE.md, 2026-09-26)

This file is the working structure for the scaffold. It keeps the discipline
that 03 derived from the evidence, inverse design of spacetime geometry. Four
changes follow from evaluating 03 against the inventories and the synthesis.

## Changes from 03 and their reasons

1. **Verification moves into Part II (Chapter 13).** Part III labels every
   design-matrix entry as an identity or a measurement. The reader needs the
   standard that a measurement meets before the first measured entry appears.
   The incident record says the same: verification habits are needed from
   the first numerical chapter onward (02 §3.2; B1–B7). Design-study practice
   and credibility stay in Part VI, because they concern running a program
   and assume the physics.
2. **The design-matrix framework opens Part III (Chapter 14).** In 03 it came
   last. Each design-element chapter fills in its part of the matrix, so the
   matrix concept comes first (C3; `lit_engineering_methods.md` D1–D5).
3. **Part III is organized by design element: lapse, shift, spatial
   geometry, then their coupling.** The identity-backed responses are
   attributed to metric functions:
   - on flat slices the shift alone carries energy density;
   - where the shift is uniform the lapse carries stress without energy;
   - the spatial geometry carries the ³R channel and the areal-radius
     Hessian.

   Organizing by element gives the general form of "how the physics responds
   to design". Metric families (warp, wormhole, shell) remain as the running
   examples, introduced in Chapter 1 and analysed in Chapter 8. Every
   identity states its class conditions, because each holds only within its
   class (for example, flat slices).
4. **Quantum sources get a chapter of their own (Chapter 24).** In 03 they
   were spread across Chapters 4, 6 and 19. The evidence base is large:
   - the QEI field count and species bound;
   - Casimir systems with their mirror cost;
   - laboratory negative-energy modalities;
   - the anomaly;
   - the scope of the achronal-ANEC exclusion.

   Chapter 22 now frames the supply problem (algebraic range of source
   families, class-level exclusions, absolute scale) before the family
   chapters.

Smaller changes: "Static slicing and the lapse" merges into the lapse
chapter; "Decomposition" becomes the framework chapter; the open problems
close the book (Chapter 32).

## Reader and layout (default, pending the user)

The default reader is at graduate level: GR at the level of a first graduate
course, with QFT prerequisites flagged where the quantum chapters need them.
The layout has two levels: core text, plus derivation boxes that an
engineering reader can skip. Physics-literate engineers read the core; GR
students read both.

## Claim-status tags used throughout

| Tag | Meaning |
|---|---|
| **T** | Theorem: proved, with assumptions stated |
| **D** | Derived in this book and symbolically checked |
| **L** | Established literature result (cite) |
| **C** | Conjecture |
| **M** | Measured on one design; carries a design label and scope, and never appears as a law |
| **H** | Heuristic |
| **P** | Vetted engineering practice, stated with scope and basis |

## Conventions

- Signature (−,+,+,+). Geometric units G = c = 1; ħ explicit in quantum
  chapters; ℓ_P = (ħG/c³)^{1/2}. SI conversion of a demand at unit length L:
  energy ×c⁴L/G, stress ×c⁴/(GL²).
- Greek indices for spacetime components, Latin i, j, k for spatial ones;
  hats for orthonormal-frame components.
- Riemann and Ricci tensors follow MTW; G_{μν} = 8πT_{μν}.
- 3+1 split: ds² = −α²dt² + γ_ij(dx^i + β^i dt)(dx^j + β^j dt).
  - Carriage at speed v in the Eulerian frame has β^z = −v.
  - K_ij = −(1/2α)(∂_tγ_ij − D_iβ_j − D_jβ_i), so K = −∇_μ n^μ.
  - ρ = T_{μν}n^μn^ν, j_i = −γ_i^μ T_{μν}n^ν, S_ij = γ_i^μγ_j^νT_{μν}.
- Hawking–Ellis types are written I–IV. The energy conditions are NEC, WEC,
  SEC and DEC; the averaged forms ANEC and AWEC; the quantum forms QEI,
  QNEC, SNEC and DSNEC.
- A null vector is normalized by u_μk^μ = −1 relative to a stated observer.
- Regions carry geometric names (service region, transverse boundary layer,
  exterior), never hardware names.
- Mechanisms are described on their own terms. A comparison names the
  shared trait and says where the mechanisms differ.

## Chapters and sections

File stems are given in brackets under `book/`.

### Front matter
- Preface: purpose, audience and prerequisites, organization, what is new.
- How to read this book: claim-status tags, boxes, running examples.
- Notation and conventions.

### Part I. Foundations  [part1-foundations/]
1. **Spacetime engineering: the inverse problem** [ch01-inverse-problem]
   1.1 Geometry as the engineered object · 1.2 A first tour of five canonical
   geometries (Morris–Thorne/Ellis wormhole; Alcubierre and Natário warp
   metrics; Krasnikov tube; a static lapse geometry; a positive-mass shell) ·
   1.3 The design loop (geometry → demand → tests → supply → verification) ·
   1.4 What makes it hard · 1.5 Performance inside one spacetime
2. **Lorentzian geometry for design** [ch02-lorentzian-geometry]
   2.1 Causal structure and proper time · 2.2 Observers, frames and tetrads ·
   2.3 Killing vectors, stationarity and conserved quantities · 2.4 Horizons
   and surface gravity · 2.5 Congruences, expansion and focusing ·
   2.6 Optical geometry of static metrics
3. **The 3+1 split** [ch03-three-plus-one]
   3.1 Foliations, lapse and shift · 3.2 Extrinsic curvature · 3.3 The
   constraints read as demand · 3.4 Evolution equations and stresses ·
   3.5 Worked examples (Morris–Thorne; Alcubierre and Natário; a lapse-only
   geometry) · 3.6 ADM and Komar masses
4. **Stress-energy and its algebra** [ch04-stress-energy-algebra]
   4.1 Components and observers · 4.2 Hawking–Ellis types and their scope ·
   4.3 Type from 3+1 data: zero momentum implies Type I · 4.4 Canonical matter
   models and their types (fluids, heat flux, electromagnetic fields, strings
   and sheets, scalars) · 4.5 Pointwise energy conditions; matrix-inequality
   form
5. **Energy conditions and quantum bounds** [ch05-energy-bounds]
   5.1 Quantum violation of pointwise conditions · 5.2 Worldline QEIs and
   quantum interest · 5.3 Null-contracted bounds: timelike worldlines versus
   null geodesics · 5.4 SNEC, DSNEC and QNEC · 5.5 ANEC: proofs, status in
   curved spacetime, achronality, counterexamples · 5.6 Exact scopes for
   design use
6. **Global structure: topology, causality, chronology** [ch06-global-structure]
   6.1 Topology change · 6.2 Topological censorship · 6.3 Causality
   conditions and time functions · 6.4 Faster-than-light theorems and their
   definitions · 6.5 Chronology and its protection conjecture
7. **Semiclassical response** [ch07-semiclassical]
   7.1 Renormalized stress and the trace anomaly · 7.2 Vacuum polarization and
   states · 7.3 Horizon temperatures · 7.4 The species bound · 7.5 Instability
   of superluminal fronts · 7.6 Validity limits
8. **The canonical engineered geometries** [ch08-canonical-geometries]
   8.1 Traversable wormholes · 8.2 Warp metrics · 8.3 Krasnikov tubes ·
   8.4 The positive-energy debate, 2021–26 · 8.5 The warp–wormhole
   correspondence · 8.6 Horizons, swept matter and control

### Part II. Specifying and testing a geometry  [part2-specifying/]
9. **From geometry to demand** [ch09-geometry-to-demand]
   9.1 The geometry fixes the demand (A7) · 9.2 The demand ledger: region,
   class, frame, measure · 9.3 Functional zoning · 9.4 Normalization and
   absolute scale
10. **Testing the demand** [ch10-testing-demand]
    10.1 Complete tensor, all observers (A1) · 10.2 Time dependence and the
    blindness of static checks · 10.3 Transitions to vacuum · 10.4 Matrix
    inequalities and certified bounds between samples (B1) · 10.5 Degenerate
    tensors (B3) · 10.6 Type as a match to source families (A2)
11. **Global structure and performance claims** [ch11-global-performance]
    11.1 Declaring topology, ends and exterior (A3) · 11.2 The causality class
    of a design · 11.3 Performance inside one spacetime; one occupant
    worldline (A4) · 11.4 Coordination without superluminal signals
12. **Occupants** [ch12-occupants]
    12.1 Occupant observables (A10) · 12.2 Flat compartments · 12.3 Choosing
    the occupant clock · 12.4 Occupants under single-gate optimization
13. **Computing and certifying the demand** [ch13-certifying-demand]
    13.1 Code verification: manufactured solutions and observed order (B2) ·
    13.2 Solution verification aimed at decisions (B7) · 13.3 Domains,
    surrogates and reduced models (B4, B5) · 13.4 Solver statuses (B6) ·
    13.5 Reference solutions for testing

### Part III. How the physics responds to design  [part3-design-response/]
14. **Design matrices** [ch14-design-matrices]
    14.1 Design elements and physical channels · 14.2 Identity-backed and
    measured entries · 14.3 Coupling, decoupling and adjustment order ·
    14.4 Identities before numerics (A8) · 14.5 Zoning and its hazard (C3)
15. **The lapse** [ch15-lapse]
    15.1 Clock, redshift and refractive index · 15.2 Stress without energy
    where the shift is uniform · 15.3 The lapse-only NEC lemma and the Komar
    balance; lapse maxima and the SEC · 15.4 The lapse in static spherical
    geometries (redshift function; lapse-supported NEC violation; hollow
    cores) · 15.5 Time staging · 15.6 Measured examples (M)
16. **The shift** [ch16-shift]
    16.1 Carriage · 16.2 Energy density from shear and vorticity; integral
    negativity; α⁻² suppression · 16.3 Momentum and vorticity; irrotational
    shifts · 16.4 Type IV at shear-layer edges · 16.5 Speed as a lapse contrast
    · 16.6 Energy scaling with speed
17. **The spatial geometry** [ch17-spatial-geometry]
    17.1 Curved slices and the ³R channel · 17.2 Stretch and conformal factors
    · 17.3 Spherical warped products: areal-radius Hessian, radial
    discriminant, string clouds · 17.4 Throats: flare-out cost, tension,
    topology · 17.5 Thin shells and junctions
18. **Coupling the elements** [ch18-coupling]
    18.1 The complete tensor of the flat-slice lapse–shift class · 18.2 Lapse
    under a varying shift: exact discriminants and the envelope heuristic ·
    18.3 Product regions · 18.4 Adjustment order · 18.5 The combined design
    matrix
19. **Moving structures** [ch19-moving-structures]
    19.1 The pattern frame and Killing energy · 19.2 Light surfaces and
    horizons · 19.3 Overtaken light and matter · 19.4 Front design: shelves,
    cones, the flank criterion · 19.5 Semiclassical response at fronts ·
    19.6 Momentum and steering
20. **Scaling laws** [ch20-scaling]
    20.1 Size · 20.2 Speed · 20.3 Wall thickness under QEIs · 20.4 Shape
21. **Strategies and their price** [ch21-strategies]
    21.1 The catalogue · 21.2 Where the NEC violation goes · 21.3 Class choices

### Part IV. Supplying the demand  [part4-supply/]
22. **The supply problem** [ch22-supply-problem]
    22.1 Algebraic range of source families · 22.2 Class-level exclusions
    first (A5) · 22.3 Absolute scale · 22.4 A screening sequence with exact
    scopes
23. **Ordinary matter under relativistic stress** [ch23-ordinary-matter]
    23.1 Strength-to-energy ratios · 23.2 Electromagnetic stresses and
    confinement · 23.3 Strings, sheets and oriented ensembles · 23.4 Junction
    stress and charged shells · 23.5 Storage limits
24. **Quantum sources** [ch24-quantum-sources]
    24.1 Casimir systems and the mirror's energy · 24.2 States with negative
    energy density · 24.3 Field counts and the species bound · 24.4 Vacuum
    polarization and the anomaly · 24.5 Scope of quantum exclusions
25. **Classical NEC-violating fields** [ch25-nec-violating-fields]
    25.1 Canonical fields and curvature couplings (bound-state test) ·
    25.2 Higher-derivative scalars · 25.3 Stability and no-go results with
    their scopes · 25.4 Superluminality and UV completion · 25.5 Algebraic
    range
26. **Net supply** [ch26-net-supply]
    26.1 NEC-satisfying parts only add to the deficit (A6) · 26.2 Accounting
    boundaries and gain chains · 26.3 Holding costs
27. **Assemblies** [ch27-assemblies]
    27.1 Component tensors on one shared geometry · 27.2 Interaction
    contracts and recoil · 27.3 Function and physical realization · 27.4
    Momentum exchange by radiation
28. **Realizability as a design objective** [ch28-realizability]
    28.1 Spending design freedom on sourceability (C6) · 28.2 Forward checks of
    simplified designs · 28.3 Realizability inside the design loop

### Part V. Dynamics  [part5-dynamics/]
29. **Dynamics, back-reaction and stability** [ch29-dynamics]
    29.1 Prescribed metrics and solutions · 29.2 Evolving warp spacetimes with
    matter · 29.3 Semiclassical back-reaction · 29.4 Stability of
    NEC-violating sources · 29.5 Fields on engineered backgrounds

### Part VI. Method and frontier  [part6-method/]
30. **Design studies** [ch30-design-studies]
    30.1 Attribution and sensitivity maps (C1) · 30.2 Matched comparisons ·
    30.3 Forks and set-based exploration (C2) · 30.4 Single-gate distortion
    (C4) · 30.5 Absolute and relative figures of merit (C5)
31. **Credibility and claim scope** [ch31-credibility]
    31.1 Naming results by the check passed (D1) · 31.2 Multi-axis
    credibility and readiness · 31.3 Kinematic and sourcing claims ·
    31.4 Program hazards (D2–D5)
32. **The frontier** [ch32-frontier]
    32.1 Open sourcing classes · 32.2 Dynamics and stability · 32.3 Quantum
    questions · 32.4 Global questions

### Appendices  [appendices/]
- A. Laboratory analogues and experiments [appA-laboratory]
- B. Computational companion [appB-computational]
- C. Units, scales and conversions [appC-units]
- D. Reference solutions and their stress tensors [appD-reference-solutions]

## Placement rules for project material

- Project identities appear in general form, with class conditions, as D-
  or T-tagged statements.
- Measured results appear only in "measured on one design" boxes, labelled
  and scoped.
- No chapter narrates the project, and no chapter is organized around it.
- Incidents inform practices; the book states the practice, its physical
  basis and its failure mode, without project history.
