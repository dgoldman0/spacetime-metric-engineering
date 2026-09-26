# Synthesis of the evidence inventories, revision 2

Revision 2 (2026-09-26) applies the claim-by-claim audit (`audit_synthesis.md`)
and the independent identity verifications (`verification/v2_spherical_class.md`,
`verification/v3_moving_patterns.md`; the flat-slice and source-physics
verifications are pending and marked where they bear). Revision 1 is kept as
`02_SYNTHESIS_rev1.md`. Practice IDs from revision 1 keep their meaning; new
IDs extend each series.

**Inputs** (all in `inventory/`):
- incidents: `incidents_may_june.md` (20 incidents, 8 counter-evidence items)
  and `incidents_september.md` (72 incidents, 15 counter-evidence items, 24
  recurring lessons);
- knob maps: `knobs_one_space.md` (25 parts, 27 knobs, 26 identities) and
  `knobs_throat_era.md` (60 knobs, 28 class identities, 13 source identities,
  an invalidation register);
- literature, versions pinned:
  - `lit_design_strategy.md` (about 145 entries, several covering a series);
  - `lit_foundations.md` (135 numbered entries);
  - `lit_engineering_methods.md` (98 items, 10 of them unverified);
- `coverage_map.md` (evidence packets per section of `05_STRUCTURE.md`).

**Evidence codes:**
- **Th**: a theorem or identity, from the literature or derived and checked.
- **Lit**: verified published practice or result.
- **Inc(n)**: n incidents in the project record with a counterfactual. The
  incidents come from one project, and correlated counts are marked.
- **Adj**: established practice in an adjacent engineering field.

## 1. What the book is about

The inventories center on inverse design of spacetime geometry. A geometry is
prescribed and its demanded stress-energy computed. The demand is then matched
to source families and assemblies, under occupant, causal and verification
requirements.

The literature also works in the other direction:
- it builds geometries source-first (Le 2026a v2; Fuchs et al. 2024;
  matter-sourced Alcubierre solutions);
- it evolves them with matter (Clough, Dietrich and Khan 2024).

The book teaches both directions.

Alcubierre and Morris–Thorne work metric-first. Le's five-criterion standard
and the Barzegar–Buchert–Vigneron critique formalize source consistency, and
Warp Factory and Le 2026b give verification tooling. Transformation optics is
the mature engineering field with the same structure: prescribe a coordinate
map, demand a material.

The searches behind `lit_foundations.md` §7 found no textbook that combines:
- the 3+1 inverse problem;
- source typing;
- energy bounds with their exact scopes;
- semiclassical response;
- causal and topological theorems;
- NEC-violating source theories with their stability;
- numerical verification;
- occupant observables.

No book located covers the post-2016 results: the ANEC and QNEC proofs, SNEC
and DSNEC, the 2021–26 warp debate, and numerical warp evolution. The searches
were not exhaustive.

## 2. How the physics responds to design

For each class of metrics a design matrix records which design elements and
knobs move which physical channels, and whether an identity guarantees each
response or one design lineage measured it. The matrices draw on the
literature's parameter studies (`lit_design_strategy.md` E.1–E.3) and on the
project's knob maps.

### 2.1 Identity-backed responses (general for their class)

| # | Class and hypotheses | Response | Status | Literature |
|---|---|---|---|---|
| R1 | Flat slices; shift along one axis; any lapse | ρ = −(∂⊥β/α)²/32π. Only shift shear carries Eulerian energy density; the lapse divides it by α². The lapse-weighted density α²ρ is unchanged by the lapse. | Th (V1 pending) | Unit-lapse form: Alcubierre eq. 19, Lobo–Visser eq. 10, Barzegar–Buchert 2025. General-lapse form: Shoshany–Snodgrass eq. 4.3. The lever itself is published: Shoshany–Snodgrass §4.2 (a large lapse where ∇β is large shrinks the Eulerian energy, at a time-stretch of order N for the source matter); Loup–Waite–Halerewicz 2001 (unrefereed). |
| R2 | Flat slices, general shift | ∫ρ d³x = −∫ω² d³x/32π at unit lapse for localized flows. ∫N²ρ d³x ≤ 0 for any lapse, for a C² shift with β = O(r^−1/2), strict when β has curl. | Th | SSV 2022 eq. 7.17; Shoshany–Snodgrass §4.1. A relaxed fall-off admits gradient shifts with ρ ≥ 0 everywhere; the NEC at non-unit lapse is open (`lit_design_strategy.md` F.2.8). |
| R3 | Class C0: flat slices, axisymmetric shift along the axis, axisymmetric lapse | Complete orthonormal tensor. Fluxes are linear in β and O(1/α); the energy is quadratic and O(1/α²). The lapse enters the three axis-aligned null sums through its flat-space Hessian over α and through s = β_r/α. | Th (derived for the inventory; V1 re-derivation pending) | Not published in this form |
| R4 | K_ij = 0: a time-independent spatial metric with zero shift, or flat slices with a spatially uniform shift (in general, a shift that is a Killing field of the slice) | A pure lapse carries stress without energy or flux, Type I for any profile and history. On curved static slices the energy density ³R/16π comes from the slice; the lapse adds none. | Th | Morris–Thorne eqs. 17–18; Bolívar et al. 2026 |
| R5 | Flat slices; zero or uniform shift wherever the lapse varies; α → 1 outside, fall-off to be fixed by V1 | Every non-constant lapse violates the NEC somewhere (Komar-flux argument) | Th (analytic derivation, `lit_parts/lapse_only_nec.md`; V1 pending on the hypotheses) | No publication states it; closest are Bobrick–Martire §3.1 and BBV Thm IV.20 |
| R6 | Any spacetime | Zero Eulerian momentum ⇒ Type I. Two kinds of evaluation are blind to Type IV: evaluations in static slicing, and irrotational-shift evaluations on time-independent flat unit-lapse slices. With a varying lapse, a gradient shift carries momentum. | Th | SSV 2022; Le 2026b Lemmas 2–3; Martín-Moruno–Visser 2021 (static spacetimes) |
| R7 | Flat unit-lapse, time-independent slices; smooth shift with bounded vorticity on ℝ³ | j ≡ 0 iff the shift is a gradient plus a rigid rotation | Th | Le 2026b Lemma 2; SSV (flux = ∇×∇×v/16π) |
| R8 | Flat slices, α = A = 1 | 8πT(n±e_z, n±e_z) = −(β_r² ± Δ⊥β). The along-track null energies differ in sign wherever \|Δ⊥β\| > β_r², which happens at every edge of a shear layer. Where the (n, e_z) block decouples (T_n̂r̂ = T_ẑr̂ = 0, as for a steady shift window uniform along the track) the tensor is Type IV. Elsewhere the identity shows NEC violation along one of n ± e_z, and the type needs the full classification. | Th (identity); Type IV verified for the decoupled case | Le 2026b (numerical: walls 81–99% Type IV at v = 0.5) |
| R9 | A region where α(t) and β(t) depend on time only | The region is exactly flat, its normal observers are geodesic, and the occupant clock runs at α. The choice is free locally; globally the clock sets the depth of the lapse hole, and a 50-fold clock range moved peak stress 4× in one design (measured). | Th | Alcubierre eq. 13; Shoshany–Snodgrass §2.1 (Eulerian worldlines are geodesic iff ∂_iN = 0); Morris–Thorne 1988 for passenger quantities as design outputs |
| R10 | Steady lane; the lapse multiplied by c at every point of non-zero shift | (α, β, t) → (cα, cβ, t/c) is a local isometry: speed is a lapse contrast. The pure-lapse parts that return α to 1 change. | Th (reparametrization; V1 pending) | No precedent found. Related: Shoshany–Snodgrass (the lapse as frame switch); Loup et al. 2001. |
| R11 | Stationary pattern frame, b = β + v (V3) | See §2.1a. | Th with stated hypotheses; tip rate is an estimate | Natário §3 (Mach cone); Barceló et al. 2022; McMonigal et al. 2012; Finazzi et al. 2009 |
| R12 | Spherical warped products (V2) | See §2.1b. | Th with stated hypotheses | Morris–Thorne; Hochberg–Visser; Misner–Sharp and Hayward (anchors to acquire) |
| R13 | Any class, fixed shape | Stress ∝ 1/L²; integrated content ∝ L | Th | Pfenning–Ford eq. 28; Lobo–Visser M_warp ≈ −v²R²σ |

#### 2.1a Moving patterns (from `verification/v3_moving_patterns.md`; 75 of 75 checks)

In the book's convention b = β + v: the carried region (β = −v) has b = 0, and
shift-free regions have b = v. The Killing vector ξ = ∂_t + v∂_z is normalized
to exterior proper time, and k is the momentum Eulerian observers measure.

- **Killing energy** E = α√(m² + k²) − b k_ζ is conserved along geodesics.
  Verified, with drift at most 1.3×10⁻¹¹.
- **Rate law.** d ln|k|/dt = −k̂·∇α holds wherever the shift is locally
  uniform. The general law is
  Δ ln(α|k|) = ∫[−b ∂_ζ ln α + k̂_z k̂·∇β] dσ.
  The "kept gain" formula is exact only for paths that stay where the lab
  shift vanishes during a steady lane (counterexample: 6.1% off for an oblique
  ray through the shift region).
- **Exit-angle law.** The gain is (v − 1)/(v cos θ_f − 1), where θ_f is the
  final propagation angle to +z measured by static exterior observers. Exits
  must fall inside the steady lane and lie within arccos(1/v) of +z; the gain
  diverges at that edge.
- **Shelf law.** γ′ = (α_s² + v²)/(α_s² − v²). It needs three conditions:
  - reflection, i.e. the pattern's lapse reaching √(α_s² + v²) where the
    shift vanishes;
  - an exit along the axis;
  - a terminal that is static while it is crossed.
- **Horizon criterion.** The surface S: α² = b² is null exactly where its
  transverse gradient vanishes. It is a Killing horizon on open null portions;
  a cone tip is a single null point. The signed surface gravity is
  κ = ∂_ζ(α − |b|), negative for white-hole type and positive for black-hole
  type, and it reduces to |∂_ζα| where the lab shift vanishes.
  - Natário's Mach cone is a causal horizon built from the same criterion (a
    stationary surface is null iff |b·N| = α), and it meets S at S's null
    points.
  - Barceló et al. 2022 pick out the same points.
  - Lemma: light can come to rest in the pattern frame only at S's null
    points.
- **Tip shedding.** λ = ½(√(κ² + 4v(−∂_r²α)) − κ) is the exact linearized ray
  rate, and equals Barceló's η₋ with ξ = vA/2. The claim that energy density
  changes at 2(κ − λ) is an ESTIMATE. It is exact for geometric-optics ray
  bundles, and for fields it holds only in a paraxial window
  σ ≲ λ⁻¹ ln(ℓ⊥/w₀), after transients, with a lapse maximum on the axis. The
  step to quantum stress is heuristic.
- **Flank criterion.** Light rides the flank once v sin θ_c > 1. This needs a
  shift-free layer and α_in > v sin θ_c. It is exact for planar layers and
  local on a cone, and the threshold is the Mach angle.
- **Lapse cavity.** Light behaves as in a medium of refractive index 1/α.
  - This needs b = 0; a merely uniform shift is not enough.
  - Total reflection occurs only going from low to high lapse.
  - It is exact for planar layers and for rays crossing a cylinder's axis.
    Spherical walls need L/E ≤ min r/α.
- **Tolman reading.** κ/(2πN) with N = α_c; the ratio κ/N is invariant under
  rescaling ξ. The thermal input is the 1+1 result of Finazzi, Liberati and
  Barceló.
- **Causality.** g^{tt} = −1/α² makes t a time function, which gives stable
  causality.
  - With α > 0 and α + |β| bounded, every t-slice is a Cauchy surface, so
    bounded designs of the class are globally hyperbolic. This is the
    non-imprisonment argument, checked in this session.
  - A Killing horizon coexists with global hyperbolicity.
  - This conflicts with Barzegar–Buchert–Vigneron 2026 Thm IV.7, which is
    recorded as disputed (`lit_design_strategy.md` F.1.11).
- **Ray ordering** holds only on 2D reductions: on the symmetry axis and
  along radial lines. A lens makes 3D rays cross.

#### 2.1b Spherical warped products (from `verification/v2_spherical_class.md`; 170 of 170 checks)

- **Radial null energy.** 8πT(k,k) = −(2/R)∇_k∇_kR for radial null k.
- **Radial discriminant.** Δ_rad = T(k₊,k₊)T(k₋,k₋), so the radial block is
  Type IV exactly where the two radial null energies differ in sign. That
  requires time dependence acting where R varies. Every stationary region of
  the class is Type I.
- **Constant R** gives an exact string cloud with a boost-invariant radial
  block, ρ = −p_r = 1/(8πR²). The remaining dynamics move into
  p_Ω = −K/8π.
- **Static decomposition.** 8π(ρ, p_r, p_t) = W(1,−1,0) + Z(−2,0,1) +
  Y(0,2,1) + X(0,0,1), with:
  - W = 2m/R³, the Misner–Sharp compactness;
  - Z = R″/R, the opening;
  - Y = (N′/N)(R′/R), acceleration times areal expansion rate;
  - X = N″/N, the clock curvature.

  W is null-neutral only radially, since 8π(ρ + p_t) = W − Z + Y + X.
- **Flare-out** (static, proper-distance gauge, lapse N). The identity
  (R′/N)′ = −(4πR/N)(ρ + p_r) is exact. Opening from R′ = 0 to R′ → 1 at an
  end needs an integrated radial null deficit of at least 1, under three
  conditions:
  - the lapse is normalized to 1 at that end (in general the bound is
    1/N∞);
  - there is no horizon;
  - R′ → 1 at the end.

  Its time-dependent form, 4π∫R T(k,k) dλ = −Δ(dR/dλ) along any affine radial
  null geodesic, is new in this form and holds to 2×10⁻¹³ numerically.
- **Clock identity.** (R²N′)′ = 4πR²N(ρ + p_r + 2p_t), so a non-degenerate
  lapse maximum needs ρ + p_r + 2p_t < 0 there.
- **Throat tension.** At a minimal sphere p_r = −1/(8πR₀²) whatever the lapse
  (Morris–Thorne eq. 51). With a shift and a time-independent R this remains
  the principal radial stress where |β|√A < α, while the Eulerian component
  becomes −1/(8πR₀²) − β²R″/(4πα²R₀). A strict minimum need not have R″ > 0
  (counterexample R = R₀ + l⁴).
- **The shift enters undifferentiated** only through the normal derivative
  n = α⁻¹(∂_t − β∂_l); a uniform shift on the Ellis slice changes ρ.
- **Join regularity.** A d^p cusp gives stress of order d^{p−2} only when the
  affected second derivative appears in G. A kink (p = 1) gives a surface
  layer; the stress is integrable across the join iff p > 1.
- **Radial bundle focusing.** B drops out of the ray paths and their spreading,
  but the areal focusing θ = 2k(R)/R depends on B.
- **Uniform slowdown** at rate κ cannot remove Type IV at an enthalpy zero:
  Δ_κ = κ²(κ²h₂² − 4j₁²).
- **Canonical static condensates** supply no null deficit. This needs minimal
  coupling and a positive kinetic sign; where ∇φ is null the radial block is
  Type II.

### 2.2 Literature responses the project did not test, or tested only in part

- **Wall thickness against quantum inequalities:** Pfenning–Ford. The project
  tested the QI-versus-scale response in its own form.
- **Pocket geometry**, through curved slices and the ³R channel: Van Den
  Broeck.
- **Flattening along the motion:** Bobrick–Martire.
- **Positive-mass shells.** They are subluminal only, carry a Type IV tail
  (Fuchs 2024; Le 2026a), and are disputed (BBV Error 18).
- **Thin-shell equation of state as the stability knob:** Poisson–Visser.
- **Moving the NEC violation into scalar or curvature sectors.**
  - The Horndeski no-go results have specific settings; beyond-Horndeski
    theories escape them.
  - The project tested F(φ)R and non-minimally coupled scalars only.
- **Steering a confined dominant-energy drive needs radiation.** Le 2026c,
  arXiv:2606.22531: v1–v3 give −ṁ ≥ 3m|a|, and v4 gives m_f/m_i = e^{−3L}.
- **Long configurations against short.** Gao–Jafferis–Wall;
  Maldacena–Milekhin–Popov; Kontou 2024. The short-configuration exclusion
  inherits Graham–Olum's conjecture status.

### 2.3 Measured-only responses

These are marked DES in the maps: thresholds, shape effects and trade-off
curves measured on one design lineage. The book uses them only in labelled
"measured on one design" boxes, never as laws. Examples: plateau and convexity
thresholds, the clock-rate stress curve, cone-angle gains, and throat-era
radius scaling (not a similarity sweep).

### 2.4 Strategies and their price, by mechanism

Rows marked **(project)** are the project's design moves; their costs were
measured on one lineage.

| Mechanism | Strategy | Buys | Costs | Status |
|---|---|---|---|---|
| Reduce shear and vorticity | Zero-expansion shift (Natário) | No volume change | Energy remains in the shear | Lit |
| | Irrotational shift (Rodal 2025) | Type I on time-independent flat unit-lapse slices (Le 2026b Lemmas 2–3); peak deficit 38× below Alcubierre (numerical, abstract-level) | Still NEC-violating (Le 2026b certified bounds); unavailable to a one-component shift | Th / Lit |
| | Flattening along the motion (Bobrick–Martire) | Lower energy for a given interior | Shape constraints | Lit |
| Lapse against shear | Large lapse where ∇β is large (Shoshany–Snodgrass §4.2; Loup et al. 2001) | Eulerian energy suppressed as α⁻², flux as α⁻¹ | A time-stretch of order N for the source matter; α²ρ unchanged; NEC deficit where the lapse falls (R5) | Th / Lit |
| Spatial geometry | Pocket (Van Den Broeck) | Surface area decoupled from volume | Energy in the ³R channel; transition curvature radii near 10 ℓ_P; a few solar masses of each sign | Lit |
| | Constant areal radius | Exact string cloud in the radial block; no radial Type IV | Dynamics move into p_Ω = −K/8π, whose NEC fails where K > 1/R²; each open end needs an integrated radial deficit ≥ 1; with both ends open, a topology change | Th |
| Positive mass | Positive-mass shell with an interior shift (Fuchs 2024) | Energy conditions in the bulk | Subluminal only; Type IV tail (Le 2026a: 22 of 25 probes); disputed as a TOV solution (BBV Error 18); tested shift 0.02 | Lit (disputed) |
| Structure laid in advance | Krasnikov tube; superluminal subway (Everett–Roman) | A one-way trip beats light with structure built before | Construction at subluminal speed; two tubes can close timelike curves | Lit |
| Topology | Thin-shell, cut-and-paste wormholes (Visser 1989a); small ANEC violation (Visser–Kar–Dadhich) | Flat faces carry no stress; the exotic region is confined | Topology change to form; stability set by the equation of state | Lit |
| Give up the lead | Long configurations | Escapes achronal ANEC | No lead over exterior light; faces null QEIs (Kontou 2024) | Lit |
| Segmentation | Segmented nacelles (White et al. 2025) | Reported reduction | Abstract-level only | Lit (unverified content) |
| Change the source sector | Move the violation into a scalar or curvature sector | Classical supply scaling as 1/L² (the project's argument) | Horndeski no-go settings: stable static spherical asymptotically flat wormholes and flat nonsingular cosmologies; beyond-Horndeski tachyonic angular modes; superluminal perturbations | Lit |
| Time-varying lapse **(project)** | Lapse elements switched with the transit | Type I for any lapse history where the shift is uniform; flat standing geometry between transits | The lapse NEC deficit, present only during the transit; in one design the QI requirement fell 13× (measured) | Th (type) / M |
| Flat occupant region **(project)** | Uniform α, β around the occupants | Zero tides and acceleration; clock set by design | Stress at the region's boundary; no static frames when α_c < v | Th |
| Speed as lapse contrast **(project)** | Raise the lapse with the speed | Local geometry unchanged with speed | Contrast in NEC-violating falls; hotter rear horizon (κ 7.55 → 57.2, measured) | Th / M |
| Leading-edge shape **(project)** | Conical front, half-angle below arcsin(1/v) | Sheds overtaken matter; no front horizon off the axis | Peak negative-null content +68% (measured); peak stress unchanged | Th / M |
| Leading-edge shape **(project)** | Forward shelf | No light surface | Cost grows with route length (measured) | Th (law) / M |

### 2.5 Decomposition

Axiomatic design gives the vocabulary: uncoupled, decoupled and coupled design
matrices, and an adjustment order when the matrix is triangular. Independence
is a heuristic in that literature (Jones 2017; Olewnik–Lewis), and mature
designs are often coupled.

The flat-slice lapse–shift class has a partly triangular map, adjusted in
three steps:
1. Set the shift for the carry.
2. Set the lapse over the shift's region: α⁻² suppression, and a radially
   rising, convex profile that keeps the tensor Type I.
3. Set the lapse in shift-free regions, where it produces stress only.

Zoning separates the two lapse elements, and the region where they join
couples them again (`lit_engineering_methods.md` Area 4). The book presents
the matrix for each class, marks which entries are identities, and treats
decoupling as a heuristic.

## 3. Vetted practices

"Truism" means standard elsewhere: it gets one sentence, plus its domain
content if it has any.

### 3.1 Practices backed by physics or verified literature, with incidents that show the cost of neglect

| # | Practice (general form) | Evidence | Verdict |
|---|---|---|---|
| A1 | Evaluate the **complete** demanded tensor, for **all observers**, on the **time-dependent** geometry, through the transition to vacuum | Th (zero momentum ⇒ Type I). Lit: SSV 2022; Warp Factory; Le 2026a v2 and 2026b (the Eulerian reading misses ≈73% of WEC violations in the Rodal wall). Inc: the 22 May component classification (P01); I-10; the 9–17 Sep static surrogate (one episode); I-06. Better method: energy conditions as 4×4 LMIs with no classification, plus interval certificates (Le 2026b). | Evidence-backed |
| A2 | Treat algebraic type as a **matching criterion** between the demand and a source family | Th: braiding scalars can be Type IV only where the NEC fails (Gergely 2026); a Type IV tensor always violates the NEC. Lit: the quantum Type IV example is a test-field computation, and back-reaction forces Type I in static and some stationary settings, with the evaporating case open (Martín-Moruno–Visser 2021). Adj: match the transform to the available material (calcite, T10). | Evidence-backed; replaces "Type I required" |
| A3 | State the **global structure** first: topology, number of ends, the exterior, the causality class (stable causality, or global hyperbolicity under bounded fields), and the reference for any comparison | Th: Geroch; topological censorship; flare-out; the bounded-field Cauchy lemma. Inc: one root incident (I-01 = E5) with 5 missed checks. Adj: a topology choice removed singular demand in carpet cloaks (T7). | Evidence-backed |
| A4 | Define performance **inside one spacetime**: arrival against the earliest signal through the same background, one occupant worldline for every occupant audit, and a measure that responds to the quantity it names | Th: Krasnikov 1998 Prop. 1 (without structure laid along the route beforehand, a one-way trip cannot beat light); Everett–Roman 1997; Gao–Wald Thm 1 in Galloway's form for global leads. Inc: two related roots (I-02/E3 with four manifestations; I-03/E4). Adj: one measure of effectiveness with derived measures of performance (S2). | Evidence-backed |
| A5 | Apply **class-level exclusions and physically normalized magnitudes** before sign, placement or construction work, and fix the absolute scale | Inc: 12 incidents covering about 6 distinct facts in one workflow; I-19 independent. Adj: Bode–Fano and passivity bounds (T11); the Lawson criterion (S5). Keep each exclusion's exact scope (§4). | Evidence-backed |
| A6 | **Net supply.** NEC-satisfying components can only increase the null deficit the exotic sector must supply, so the supply hardware's own stress counts | Th: the sum of null energies. Inc: 2 incidents, 12 instances, one campaign. Lit: Morris–Thorne–Yurtsever 1988 plate constraints (the Costa–Matsas holding bound is cited in the repo, unverified). Adj: the fusion gain chain. Name the accounting boundary at each gain. | Evidence-backed |
| A7 | **The geometry fixes the demand.** A local source fix reallocates the deficit among components. Assigning a known tensor to components always succeeds, so it proves nothing. Track the worst residual after every fix. | Th: T = G/8π fixes the total. Inc: in the record each such fix moved the worst deficit elsewhere (n = 3 over three months); CE-3 and I-05 share the root. | Evidence-backed |
| A8 | Derive the class **identities, scalings and onset expansions** before numerics | Inc: 7 cases where numerics ran first and 5 where the identity came first, all in one workflow. The 23 Sep fix took about 2 h with a textbook identity. | Evidence-backed; the identities are book content |
| A9 | For moving structures, locate the α² = b² surfaces and classify them (null only where the transverse gradient vanishes). Keep front normal speeds below local light, and account for what is overtaken. | Th (V3); Lit: Natário; Barceló et al. 2022; McMonigal et al.; Finazzi et al. Inc: E11 and E12, one design and one day (correlated). | Evidence-backed |
| A10 | **Occupant quantities** with every crewed-transport design: clock rate against exterior time and against light's crossing time, tides, proper acceleration, radiation temperature, swept matter | Lit: Morris–Thorne 1988; Maldacena–Milekhin 2021. Inc: B14 and E13 (n = 2, four designs). Adj: measures of effectiveness. | Truism as practice; the domain list is content |
| A11 | Set the **smoothness class** by the highest derivative the analysis uses. A d^p cusp raises stress as d^{p−2} only where the affected second derivative appears in G, and the stress is integrable iff p > 1. Semiclassical stress contains fourth derivatives, so it needs at least C⁴. A curvature step gives a one-sided d⁻² vacuum energy, and ideal delta-mirror boundaries give d⁻³. | Th (V2 cusp rule). Inc(3). Adj: adiabatic transitions; smooth manufactured solutions. | Refined; replaces "C∞ joins" as a rule |
| A12 | Keep the **complete assembly ledger**: transport of work, reactions and heat; GR self-weight (the Tolman factor across a member in a lapse gradient); fit residuals; per-constituent principal stresses, never direction-averaged. A conservation equation fixes a tensor only up to divergence-free additions, so a fitted exchange current says nothing about its type. | Th (throat-era I15). Inc(5; `audit_synthesis.md` §3.1 item 1). | Evidence-backed |
| A13 | **Split bulk tension from the signed null deficit** before allocating sources. At a minimal sphere, tension and opening are separate duties. | Th (throat tension, flare-out); Lit (Morris–Thorne exoticity). Inc: B8 (n = 1). | Evidence-backed (physics) |
| A14 | **Superposition fails.** Component contributions are solved on one shared geometry; placement and overlap change local duties non-additively, and shared fields carry cross terms. | Th (non-linearity; the Q8 cross term). Inc: L24 and D6. | Evidence-backed (physics) |
| A15 | **Semiclassical constraints no tuning removes**: anomaly-fixed combinations (in 2D, ρ − p_r is fixed independently of state, length and multiplicity); the finite parts of the R² couplings (relabelling moves stress between the two sides of the field equation and supplies none); the species bound on multiplicity | Th / Lit (V4 pending on constants). Inc: D9, D10, D12 (n = 3, one workflow). | Evidence-backed |
| A16 | **Check a fitted source's principal part** before fitting its stress values. A matter model fitted to the principal part of G/8π cancels gravity's kinetic term and leaves a degenerate principal symbol. | Inc: B1 and B2 (n = 2). Th: well-posedness of the coupled system. | Evidence-backed; dynamics chapter |

### 3.2 Verification practice for numerical work

| # | Practice | Evidence | Verdict |
|---|---|---|---|
| B1 | Verify between samples: interval certificates first, then root-finding, then nodes | Inc(6, ≈14 instances); Lit: Le 2026b; Adj: validated numerics (V15) | Evidence-backed; the project's method is superseded by interval certification |
| B2 | Verify code with manufactured solutions judged by observed order of accuracy; report the grid convergence index. Agreement between two kernels is a low rung. | Adj: Salari–Knupp 2000 blind tests (of ten planted order-of-accuracy mistakes, the order criterion caught 10 and the consistency criterion 6). F1: tests passed while wrong. The repo reports convergence ratios of step ladders and applies no MMS order verification or GCI. | Superseded; the book teaches the adjacent method |
| B3 | Degenerate and near-vacuum tensors need exact evaluators and scale-aware tolerances | Inc: the legacy classifier failed 15 of 19 analytic fixtures, including vacuum, the string cloud and small-amplitude ordinary matter | Evidence-backed; brief |
| B4 | The domain contains the full service and ray extents, and truncated evaluations are flagged | Inc(6); E9 adds 2 | Near truism; brief |
| B5 | A surrogate or reduced model can forbid a failure mode, so a pass certifies only the model. A gate's control case is never the design case. | Th (static ⇒ Type I); Inc (3 distinct episodes) | Evidence-backed |
| B6 | Solver and stop statuses are not physics; use source-free controls and certificates | Inc(3, 8 instances) | Textbook numerics; brief |
| B7 | Aim refinement at quantities that could change a decision | F3; Adj: rigor commensurate with the decision's consequence (ASME V&V 40, V12; Samurai, N5) | Supported (imported) |
| B8 | Test fitted closures and fixes out of sample: at off-design service points, across the operating envelope and across mesh densities. A required basis that grows with mesh density signals a fit. | Inc: I-11 (n = 3) and E12. Adj: calibration is not validation (V9). | Evidence-backed |
| B9 | Causal claims from ray tracing need finite congruences and their expansion | I-14 (8 of 8 bundles compressed while the central rays escaped); Raychaudhuri | Evidence-backed; n = 1 |
| B10 | Averaged and smeared null conditions need affine parameters. Report the non-affinity of traces parametrized by lapse or coordinate. ANEC magnitudes carry the normalization; signs do not. | I-12; Le 2026b §3.5 | Textbook |
| B11 | Compare orthonormal or invariant quantities. Coordinate-normalized magnitudes carry lapse factors: T(k,k) with k^t = 1 carries α². | I-02 sub-note; throat-era I8 | Evidence-backed |
| B12 | Keep reductions that preserve the diagnostic. A minimum over null branches, or node sampling, hides it. | P01+ and E8 (n = 2); the radial-null count never separated Type I NEC violation from Type IV | Evidence-backed |
| B13 | Check conserved quantities in variables the integrator does not preserve trivially. In (p_t, p_i) form any Runge–Kutta step conserves the Killing energy exactly, so the check must use Eulerian variables. | V3 | Evidence-backed (numerical analysis) |
| B14 | Cap the integration step below the thinnest layer, so that no step jumps over it after a long flat stretch | V3 | Evidence-backed (numerical analysis) |
| B15 | A check guaranteed by symmetry carries no evidential weight | TE-§8.4; TE-M3 (J_⊥ = 0 forced by spherical symmetry) | Evidence-backed |

### 3.3 Design-study practice

| # | Practice | Evidence | Verdict |
|---|---|---|---|
| C1 | Use one-change controls for attribution at a base point. Map a design space with global sensitivity (Morris, Sobol'). Compare at matched effective strength. | Adj (D6–D8). Inc: I-15; matched strength in May; the ordering interaction (shift before stretch gives 525 Type IV points, the reverse gives 0). | Superseded for maps; supported for attribution |
| C2 | Run every branch of a fork through the same checks and record it | Adj: set-based concurrent engineering (D9), from case studies. E18 is a counter-instance: settle class-level choices first. | Supported (imported); a heuristic in this record |
| C3 | Record which knobs decouple and in what order to adjust them. Decoupling is a heuristic, and zoning must not hide phases. | Adj (axiomatic design, DSM); CE-7 (n = 1) | Refined, with a stated hazard |
| C4 | Optimizing to one gate distorts the others: carry margins, side effects, occupant and causal quantities in the same pass | Inc: I-08 (7 instances, one design family), E7 and E12. Designs chosen to pass the gate carried 450× excess energy, a 9,069× packet clock and a front horizon releasing matter at γ = 10²² (F11). Adj: coupled requirements under one objective (D1); constraints inside the optimizer (T13). | Evidence-backed hazard |
| C5 | Report absolute values beside fractions; a relative figure of merit needs an absolute threshold | Inc(7); F7 | Truism with a strong domain record |
| C6 | Spend design freedom on realizability: among geometries with the same service, choose the one easiest to source, state which burden rises, and forward-check the simplified source on every service observable | Adj: transformation optics (quasi-conformal maps; reduced parameters losing observables). Positive instances: the constant-R rule (E1: 13,587 → 0 Type IV, service reproduced); the amplitude pass (450× less energy, same service); the A ≡ 1 fork (standing energy 7.5×10⁴ → 0). | Supported; imported |
| C7 | Put passivity, the second law and regularity inside inverse source optimization; unbounded linear programs converge to distributions | L18: C13 and D14 (n = 2). Adj (T13, T14, established) | Evidence-backed |

### 3.4 Claims and program governance (a methods sidebar)

These practices are stated from Cooper, Millis, NASA-STD-7009 and the
validation literature, with project incidents as unnamed illustrations.

| # | Practice | Evidence | Verdict |
|---|---|---|---|
| D1 | Name each result by the check it passed. Rate credibility on several axes (PCMM; NASA-STD-7009 dimensions) beside maturity (validation tiers, V9). Separate kinematic claims, which analogue experiments can test, from sourcing claims, which they cannot. Place readiness honestly: analytic and computational work sits at or below TRL 2, and work whose enabling physics is unestablished belongs on Millis's Applied Science Readiness Levels, below TRL 1. | Inc(4, label inflation); Adj (V13–V14, S1, S6); Lit (analogue gravity) | Refined |
| D2 | A frame review is separate from a process review. Cover failure classes broadly before going deep in one. | CE-1 and CE-2 (one episode); F2 (a second); Adj (V9, V13, N2, V14) | Evidence-backed |
| D3 | Stopping rules at two levels, candidate and program, with binding authority and a recycle branch | Candidate stops worked; program rules were bypassed twice (F14). Adj: Cooper gates (S4). | Heuristic, labelled |
| D4 | Keep negative verdicts and relaxations in a live ledger | Inc: 7 cases mixing dropped verdicts with knowledge left unapplied; F8 (stacked relaxations with no ledger). Adj: Millis (publish results regardless of outcome, S6); input pedigree (V13). | Supported (governance); sidebar |
| D5 | Freezes stop tuning and carry no confidence; relax a failed criterion only by an explicit dated decision | CE-4; I-05 | Truism (governance) |

### 3.5 Truisms (one sentence each)

- **Process:**
  - stage-gate ordering;
  - interface contracts;
  - matched controls;
  - a supersession map;
  - measures of effectiveness.
- **Scaling:** dimensional analysis.
- **Verification:**
  - regression is not verification (established, N4);
  - nested parameterizations reproduce the reference exactly (I-16);
  - promote only after refinement and with margin (I-07);
  - cost-only objectives select the null design, and linear-response
    fractions say nothing about load-bearing (I-06);
  - pre-registered rules need a geometry-revision branch (CE-5).
- **Coordination:** clock-based coordination without signals (Lamport,
  supported). Its domain content is converting clock rates on a lapse profile
  to the chosen time function.

### 3.6 Dropped from the book as general practice

- **"Admissibility"** as a name. The check establishes algebraic
  compatibility with a source class.
- **"Type I required"**, replaced by A2.
- **The C1 build architecture as a rule.** The distinction between a function
  and its physical realization survives.
- **"Preserve specialized components".** In the record it made exclusions
  non-cumulative (F13).
- **"The central ordering principle"** (revision 1's A5 label). It is the
  project's workflow rule; the book's order follows the physics: global
  structure, demand, class exclusions, magnitudes, construction.
- **The project's claim-ladder vocabulary.** D1 uses validation tiers,
  credibility dimensions and readiness levels.
- **Commit discipline.** It has no spacetime content.

## 4. Corrections the book must carry

- **Achronal ANEC.**
  - Where it is proven:
    - in flat space (Faulkner et al. 2016; Hartman et al. 2017);
    - for a free scalar at first order in curvature on NEC backgrounds
      (Kontou–Olum 2015);
    - at first order in ħ given the generalized second law (Wall 2010).
  - Its self-consistent form is Graham–Olum's conjecture, and test-field
    versions fail (Urban–Olum 2010).
  - It excludes quantum sources only for a global lead that persists between
    distant endpoints, with null completeness and the generic condition, and
    within the semiclassical regime. Local advances are not excluded.
- **Topological censorship** assumes the ANEC; its abstract says NEC.
- **Chronology protection** is a conjecture. Hawking 1992 proves a violation
  of the averaged weak energy condition on compactly generated Cauchy
  horizons.
- **SNEC and DSNEC.** DSNEC is proven for free fields in Minkowski space, and a
  cutoff-dependent SNEC holds for free and super-renormalizable theories.
  Curved-space and interacting versions are open.
- **Null quantum inequalities.** A bound exists along timelike worldlines;
  along null geodesics in 4D there is none. Smearing in two null directions
  (DSNEC) or over strips (Fliss–Rolph 2025) restores finite bounds.
- **Type IV.** The quantum example (Unruh state on Schwarzschild; Type IV
  everywhere outside the horizon for the massless conformal scalar) is a
  test-field computation.
  - With back-reaction, Type I is forced in static spacetimes (outer domain
    and horizons), on horizons and axes of stationary axisymmetric
    spacetimes, on bifurcate Killing horizons and in some Bianchi
    cosmologies.
  - The back-reacted evaporating case is open.
  - Braiding scalars are the one classical Type IV source found, Type IV only
    where the NEC fails.
- **Horndeski no-go results** cover two settings:
  - stable static spherically symmetric asymptotically flat wormholes
    (Rubakov 2016; Evseev–Melichev 2018);
  - spatially flat nonsingular cosmologies over their whole history
    (Libanov–Mironov–Rubakov 2016; Kobayashi 2016).

  Beyond-Horndeski theories evade both, and slow tachyonic modes stay
  unconstrained in the wormhole examples.
- **Global hyperbolicity.**
  - A time function gives stable causality.
  - Bounded lapse and shift on flat slices give global hyperbolicity
    (bounded-field Cauchy lemma).
  - Barzegar–Buchert–Vigneron 2026 Thm IV.7 is disputed and is not stated in
    the book until its definitions and proof are read in full.
- **Krasnikov's theorem** carries its hypothesis: modifications are confined
  to the causal future of the launch event.

## 5. Identity verification status

| Verification | Scope | Result |
|---|---|---|
| `verification/v2_spherical_class.md` | Throat-era I1–I28, one-space I24 | 170 of 170 checks pass. All 28 identities are correct as mathematics. Eleven need a correction, hypothesis, scope or design label (I7, I11, I13, I16, I17, I18, I19, I23, I24, I25, I28). |
| `verification/v3_moving_patterns.md` | One-space I12–I17, I19, I20 | 75 of 75 checks pass. Nothing is false. Eight statements carry added hypotheses, and the tip energy-density rate is an estimate. |
| `verification/v1_flat_slice_class.md` | One-space I1–I11, I18, I26, §3.2, R5 lemma, general 3+1 lemmas | Pending |
| `verification/v4_source_physics.md` | One-space I21, I22, I25; throat-era Q1–Q13 | Pending |
