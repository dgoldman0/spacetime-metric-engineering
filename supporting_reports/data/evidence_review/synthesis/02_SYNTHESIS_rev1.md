# Synthesis of the evidence inventories

Inputs (all in `inventory/`):
- incidents: `incidents_may_june.md` (20 incidents, 8 counter-evidence items) and `incidents_september.md` (71 incidents, 15 counter-evidence items, 24 recurring lessons);
- knob maps: `knobs_one_space.md` (25 parts, 27 knobs, 26 identities) and `knobs_throat_era.md` (60 knobs, 28 class identities, 13 source identities, an invalidation register);
- literature, with versions pinned: `lit_design_strategy.md` (~170 papers), `lit_foundations.md` (~110 items) and `lit_engineering_methods.md` (98 items).

Evidence codes used below:
- **Th**: a theorem or identity, from the literature or derived and checked.
- **Lit**: verified published practice or result.
- **Inc(n)**: n incidents in the project record with a counterfactual. The n come from one project and are correlated.
- **Adj**: established practice in an adjacent engineering field.

## 1. What the book is about, as the evidence defines it

Every inventory converges on the same object: **inverse design of spacetime
geometry**. A geometry is prescribed and its demanded stress-energy computed.
That demand is then matched to source families and assemblies, under occupant,
causal and verification requirements. The literature reached this framing
independently:
- Alcubierre and Morris–Thorne work metric-first.
- Le's five-criterion standard and the Barzegar–Buchert–Vigneron critique
  formalize source consistency.
- Warp Factory and Le 2026b give verification tooling.

Transformation optics is a mature engineering field with the same structure:
prescribe a coordinate map, demand a material.

**The gap is confirmed** (`lit_foundations.md` §7). No textbook combines:
- the 3+1 inverse problem;
- source typing;
- energy bounds with their exact scopes;
- semiclassical response;
- causal and topological theorems;
- NEC-violating source theories with their stability;
- numerical verification;
- occupant observables.

No book covers the post-2016 results (ANEC and QNEC proofs, SNEC and
DSNEC, the 2021–26 warp debate).

## 2. How the physics responds to engineering strategy

This is the project's distinctive contribution, and the part the user asked
to see covered. The knob maps make it concrete. For each class of metrics
there is a design matrix: which parts and knobs move which physical channels,
and whether an identity guarantees the response or it was measured once.

### 2.1 Identity-backed responses (general for their class)

| Class | Response | Status | Literature |
|---|---|---|---|
| Flat slices, shift along one axis, any lapse | ρ = −(∂⊥β/α)²/32π. Only shift shear carries energy density; the lapse only suppresses it as α⁻². | Th | Unit-lapse form published (Alcubierre eq. 19; Lobo–Visser; Barzegar–Buchert). The general-lapse form follows from Shoshany–Snodgrass eq. 4.3. The α⁻² *design lever* is the project's. |
| Flat slices, general shift | ∫ρ = −∫ω²/32π; ∫N²ρ ≤ 0 | Th | SSV 2022; Shoshany–Snodgrass 2024 |
| Same class, full tensor | Complete orthonormal tensor. Fluxes are linear in β and O(1/α); energy is quadratic and O(1/α²); the lapse enters every null sum through its flat-space Hessian over α. | Th (derived for the inventory, symbolically checked) | Not published in this form |
| Static or uniform-shift regions | A pure lapse carries stress without energy or flux: Type I for any profile and history | Th | Morris–Thorne (redshift function enters stresses only); Bolívar et al. 2026 |
| Same, with flat slices and α → 1 | **Every non-constant lapse violates the NEC somewhere** (Komar-mass argument) | Th (derived for the inventory, symbolically checked) | Closest: Bobrick–Martire (faster interior clocks need negative energy); BBV Thm IV.20 |
| Any | Zero Eulerian momentum ⇒ Type I. Static and irrotational evaluations are therefore blind to Type IV. | Th | SSV §5; Le 2026b Lemmas 2–3; Martín-Moruno–Visser 2021 |
| Flat unit-lapse slices | j ≡ 0 iff the shift is a gradient plus a rigid rotation (vorticity drives momentum) | Th | Le 2026b; SSV |
| Flat slices, α = 1 | Shear identity: Type IV wherever \|Δ⊥β\| > β_r², at every edge of a shear layer | Th | Le 2026b (vorticity walls are Type-IV dominated) |
| Uniform α(σ), β(σ) region | Exactly flat: zero tides and acceleration, occupant clock = α, a free design choice | Th | MT 1988 made passenger metrics design outputs |
| Steady lane | Speed scaling (α, β) → (cα, cβ) is an isometry: **speed is a lapse contrast** | Th (reparametrization) | No precedent found. The lemma above gives its price: the contrast sits in NEC-violating falls. |
| Stationary pattern frame | Killing energy; blueshift d ln\|k\|/dσ = −k̂·∇α; exit-angle and shelf laws; a horizon only where the transverse lapse gradient vanishes; lapse = refractive index 1/α; flank subluminal iff v sin θ < 1 | Th | Natário (Mach cone); Barceló et al. 2022 (same horizon criterion); McMonigal et al.; Finazzi et al. |
| Spherical warped products | 8πT(k,k) = −(2/R)∇∇R; Δ_rad = T(k₊,k₊)T(k₋,k₋); constant R ⇒ exact string cloud; flare-out costs ≥ 1 per end; throat tension −1/(8πR₀²) independent of lapse, shift and stretch; a clock maximum needs ρ + p_r + 2p_t < 0 | Th | Morris–Thorne; Hochberg–Visser |
| Any, fixed shape | Stress ∝ 1/L²; content ∝ L | Th | Pfenning–Ford; Lobo–Visser E ∝ v²R²/Δ |

### 2.2 Literature responses the project never tested

- **Wall thickness and quantum inequalities:** Pfenning–Ford.
- **Pocket geometry, via curved slices and a ³R energy channel:** Van Den Broeck.
- **Flattening along the motion:** Bobrick–Martire.
- **Positive-mass shells:** subluminal, with a Type IV tail (Fuchs; Le 2026a).
- **Thin-shell equation of state as the stability knob:** Poisson–Visser.
- **Moving the NEC violation into scalar or curvature sectors:** Horndeski no-go results; beyond-Horndeski escapes.
- **Steering needs radiation, −ṁ ≥ 3m|a|:** Le 2026c.
- **Long-versus-short wormhole dichotomy:** Gao–Jafferis–Wall, Maldacena–Milekhin–Popov, Kontou.

### 2.3 Measured-only responses

These are marked DES in the maps: thresholds, shape effects and trade-off
curves measured on one design lineage. The book can use them as worked
examples with that label. It cannot state them as laws. Examples:
- plateau and convexity thresholds;
- the clock-rate stress curve;
- cone-angle gains;
- throat-era radius scaling (not a controlled similarity sweep).

### 2.4 Design strategies and their physical price

The chapter form the user's "how physics reacts to strategy" suggests: a
catalogue of strategies, each with what it buys, what it costs, and the
status of both.

| Strategy | Buys | Costs | Status |
|---|---|---|---|
| Put shear behind a high lapse | Energy suppressed as α⁻², flux as α⁻¹ | NEC deficit where the lapse falls (lemma); the clock, unless the occupant sits in a compartment | Th |
| Stage demand in time with the lapse | Admissible for any history where the shift is uniform | Same lapse NEC deficit, present only during the transit | Th |
| Irrotational or gradient shift | Type I, lower peak deficit | Still NEC-violating (Le certifies wall NEC violation) | Th / Lit |
| Flat compartment | Zero tides and acceleration, clock by design | Stress at the compartment boundary; no static frames when α_c < v | Th |
| Speed via lapse contrast | Local geometry unchanged with speed | Contrast placed in NEC-violating falls; hotter rear horizon | Th / measured |
| Curved slices (pocket) | Surface area decoupled from volume | Energy in the ³R channel; outside the flat-slice identity | Lit |
| Constant areal radius | Exact string cloud, no radial Type IV | With a throat, two ends and a topology change | Th |
| Conical front | Sheds overtaken matter; no front horizon off the axis | Peak demand +68% (measured); half-angle tied to 1/v | Th / measured |
| Forward shelf | No light surface | Cost grows with route length | Th (law) / measured (cost) |
| Positive-mass shell with interior shift | Energy conditions in the bulk | Subluminal only; Type IV tail at the boundary; Shapiro delay | Lit |
| Move the violation into a scalar sector | Classical supply scaling as 1/L² | Horndeski no-go; beyond-Horndeski tachyonic sector open; superluminal modes | Lit |

### 2.5 Decomposition as an engineering idea

Axiomatic design (Suh) gives the vocabulary: uncoupled, decoupled or coupled
design matrices, and an adjustment order when the matrix is triangular. The
flat-slice class has a partly triangular map: shift, then lapse, where zoning
keeps lapse variation off the shift's region. Independence is a heuristic in
that literature (`lit_engineering_methods.md` D2–D3), and mature designs are
often coupled. The book presents the matrix per class, marks which entries are
identities, and does not claim decoupling as a law.

## 3. Vetted practices

The verdicts combine the incident record, the adjacent-field literature and
the physics. "Truism" means standard elsewhere; it gets one sentence, plus
its domain content if it has any.

### 3.1 Physics-backed practices: a theorem makes them necessary, and incidents show the cost of neglect

| # | Practice (general form) | Evidence | Better method or refinement | Verdict |
|---|---|---|---|---|
| A1 | Evaluate the **complete** demanded tensor, for **all observers**, on the **time-dependent** geometry, through the transition to vacuum | Th (zero momentum ⇒ Type I); Lit (SSV; Warp Factory; Le 2026a/b); Inc(3+): the May component classification; I-10; 4,504 static samples all Type I while the active metric fails | Energy conditions as 4×4 LMIs, which need no classification; interval certificates (Le 2026b) | **Evidence-backed** |
| A2 | Treat algebraic type as a **matching criterion** between demand and source family, not as admissibility | Th (Gergely 2026: braiding scalars reach Type IV where the NEC fails); Lit (Unruh Type IV is a test-field effect; back-reaction forces Type I in symmetric settings); Adj (match the transform to the available material, calcite) | — | **Evidence-backed**; replaces "Type I required" |
| A3 | State the **global structure** first: topology, number of ends, the exterior, the causality class (stable causality vs global hyperbolicity), and the reference for any comparison | Th (Geroch; topological censorship; flare-out); Inc: I-01 (five missed checks; the metric form showed it on 17 May), E5; Adj (a topology choice removed singular demand in carpet cloaks) | Say which causality property a time function gives (`lit_design_strategy.md` F.1.11) | **Evidence-backed** |
| A4 | Define performance **inside one spacetime**: arrival against the earliest signal through the same background, and one occupant worldline for every occupant audit | Th (Krasnikov / Everett–Roman: one-way arrival cannot be hastened; the Gao–Wald chain for global leads); Inc(4+1): two packet readings, the service-time ratio built from V; Adj (one measure of effectiveness broken into measures of performance) | — | **Evidence-backed** |
| A5 | Apply **class-level exclusions and physically normalized magnitudes** before sign, placement or construction work, and fix the absolute scale | Inc(12, strength A): QI with the species bound, achronal ANEC, mirror energy, E/Mc², coupling thresholds; I-19; Adj (Bode–Fano, causality and passivity bounds redirected cloaking; the Lawson criterion) | Keep the exact scope of each exclusion (see §4: ANEC is conditional) | **Evidence-backed**. The central ordering principle. |
| A6 | **Net supply**: NEC-satisfying components only add to the null deficit, so the supply hardware's own stress counts | Th (sum of null energies); Inc(2, 12 instances): mirrors, holders, confinement, bulk motion; Lit (Casimir mirror cost); Adj (the fusion gain chain Q_fuel → Q_wp) | Name the accounting boundary at each gain | **Evidence-backed** |
| A7 | **The geometry fixes the demand.** A local source fix moves the deficit, and assigning a known tensor to components always succeeds. Track the worst residual after every fix. | Th (T = G/8π); Inc(3 + pervasive): the May regulator, A6, D11, CE-3 oracle partitions, "zero live residual" by construction | The edge-migration test in the gate handoff | **Evidence-backed** |
| A8 | Derive the class **identities, scalings and onset expansions** before numerics | Inc(12, strength A): numerics ran first where an identity decided; the 23 Sep fix took about 2 h with a textbook identity | — | **Evidence-backed**; the identities are book content |
| A9 | For moving structures, locate α² = b² surfaces, classify them (a horizon only where the transverse gradient vanishes), keep front normal speeds below local light, and account for what is overtaken | Th; Lit (Natário; Barceló et al. 2022; McMonigal et al.; Finazzi et al.); Inc(2) | — | **Evidence-backed** |
| A10 | **Occupant quantities** with every design: clock rate against exterior time and against light's crossing time, tides, proper acceleration, radiation temperature, swept matter | Lit (MT 1988 and MM 2021 treat them as design outputs); Inc: I-08 (n = 7), E13; Adj (measures of effectiveness) | — | Truism as practice; **the domain list is content** |
| A11 | Set smoothness by the highest derivative the analysis uses. C∞ is a convenient sufficient choice; semiclassical stress needs more (d⁻³ at sheets). | Th (a cusp d^p gives stress ~ d^{p−2}); Inc(3); Adj (adiabatic transitions; smooth manufactured solutions) | Replaces "C∞ joins" as a rule | **Refined** |

### 3.2 Verification practice for numerical work

| # | Practice | Evidence | Verdict |
|---|---|---|---|
| B1 | Verify between samples: interval certificates, then root-finding, then nodes | Inc(6, ≈14 instances); Lit (Le 2026b) | Evidence-backed; the project's method is superseded by interval certification |
| B2 | Code verification by manufactured solutions judged by observed order of accuracy; report the grid convergence index. Agreement between two kernels is a low rung. | Adj (Salari–Knupp: 10 of 10 errors caught vs 6 of 10); counter-evidence F1: tests passed while wrong; no observed-order reporting in the repo | Superseded; the book teaches the adjacent-field method |
| B3 | Degenerate and near-vacuum tensors need exact evaluators and scale-aware tolerances | Inc(3, 7 instances): the legacy classifier failed 15 of 19 fixtures at string clouds and vacuum | Evidence-backed; brief |
| B4 | The domain contains the full service and ray extents; truncated evaluations are flagged | Inc(6) | Near truism; brief |
| B5 | A surrogate or reduced model can forbid a failure mode, so a pass certifies only the model. A gate's control case is never the design case. | Th (static ⇒ Type I); Inc(5) | Evidence-backed |
| B6 | Solver and stop statuses are not physics; use source-free controls and certificates | Inc(3, 8 instances) | Textbook numerics; brief |
| B7 | Aim refinement at quantities that could change a decision | Counter-evidence F3: many ladders converged without changing any decision | Refinement of practice |

### 3.3 Design-study practice

| # | Practice | Evidence | Verdict |
|---|---|---|---|
| C1 | One-change controls for attribution at a base point; global sensitivity (Morris, Sobol') to map a design space; compare at matched effective strength | Adj (D6–D8); Inc: I-15, matched strength in May | Superseded for maps; supported for attribution |
| C2 | Run every branch of a fork through the same checks and record it | Adj (set-based concurrent engineering); user practice | Supported |
| C3 | Record which knobs decouple and in what order to adjust them; decoupling is a heuristic. Zoning must not hide phases. | Adj (axiomatic design, DSM); CE-7 (passenger-centred zoning hid reset, where the Type IV lived) | Refined, with a stated hazard |
| C4 | Optimizing to one gate distorts the others: carry margins, side effects, occupant and causal quantities in the same pass | Inc(7 + 3): burden reduction consumed causal margin; minimal passing amplitudes hid 450× energy, a 9,069× clock and γ = 10²²; Adj | Evidence-backed hazard |
| C5 | Report absolute values alongside fractions; relative figures of merit need an absolute threshold | Inc(7); F7 (a relative merit steered about 90 commits) | Truism with a strong domain record |
| C6 | Spend design freedom on realizability: among geometries with the same service, choose the one easiest to source, state which burden rises, then forward-check the simplified source on every service observable | Adj (transformation optics: quasi-conformal maps, reduced parameters losing observables) | Supported; imported |

### 3.4 Claims and program governance (a methods sidebar, not physics)

| # | Practice | Evidence | Verdict |
|---|---|---|---|
| D1 | Name each result by the check it passed. Rate credibility on several axes (PCMM, NASA-STD-7009). Separate kinematic claims, which analogue experiments can test, from sourcing claims, which they cannot. Place readiness honestly (analytic work sits below TRL 1). | Inc(4, label inflation); Adj (V13–V14, S1); Lit (analogue gravity) | Refined; the claim ladder is kept as one axis |
| D2 | A frame review is separate from a process review; cover failure classes broadly before going deep in one | CE-1 (the review rated the work "excellent" and never mentioned topology), CE-2 (15 gates within one frame) | Evidence-backed; one strong episode |
| D3 | Stopping rules at two levels, candidate and program, with binding authority and a recycle branch | Inc: candidate stops worked; program rules bypassed twice (F14); Adj (Cooper gates) | Heuristic, labelled |
| D4 | Keep negative verdicts and relaxations in a live ledger | Inc(7); F6 (a style rule erased a gate verdict); F8 (stacked relaxations with no ledger) | Governance; sidebar |
| D5 | Freezes stop tuning and carry no confidence; relax a failed criterion only by an explicit dated decision | CE-4; I-05 | Governance; sidebar |

### 3.5 Truisms: one sentence each

- Stage-gate ordering.
- Dimensional analysis.
- Interface contracts.
- Matched controls.
- Commit discipline.
- A supersession map.
- Regression is not verification.
- Measures of effectiveness.
- Clock-based coordination without signals: Lamport; the domain part is proper time.

### 3.6 Dropped from the book as general practice

- **"Admissibility"** as a name. The check establishes algebraic compatibility with a source class.
- **"Type I required"**, replaced by A2.
- **The C1 build architecture as a rule.** The distinction between a function and its physical realization survives as a general point. The architecture choice is the project's.
- **"Preserve specialized components" as a general principle.** In the record it made exclusions non-cumulative (F13).

## 4. Corrections the book must carry, found against the literature

- **Achronal ANEC** excludes quantum sources only for a *global* lead that
  persists between distant endpoints. It needs null completeness and the
  generic condition. It is proven perturbatively (Wall; Kontou–Olum) and
  conjectured non-perturbatively (Graham–Olum). "At any size" holds only
  within the semiclassical regime. Local advances are not excluded.
- **Topological censorship** assumes ANEC.
- **Chronology protection** is a conjecture; Hawking 1992 proves an
  averaged-WEC violation on compactly generated Cauchy horizons.
- **The SNEC** is a conjecture; DSNEC and a free-field SNEC with a cutoff
  are proven.
- **Null QEIs**: a bound exists along timelike worldlines; along null
  geodesics in 4D there is none.
- **Type IV** is a test-field effect in the Unruh state.
- **Horndeski no-go results** are specific to their settings.
- **A global time function** gives stable causality, which is weaker than
  global hyperbolicity.
