# P01 — "Admissibility before construction": vetting

Candidate as first stated (quick list, 2026-09-26): *Classify the complete
demanded tensor by Hawking–Ellis type on the active metric, under derivative
refinement, through the outermost boundary into the exterior, root-finding
crossings; begin source work only on a geometry that passes.*

The candidate bundles one ordering claim with six technical claims. Each part is
vetted separately below.

## 1. What the project record shows

The project did not follow this practice for most of its history. The rule
entered [SOURCE_FEASIBILITY_WORKFLOW.md] on 23 September, after four months of
source work. The practice is therefore generalized from the project's newest
rule; it was never tested as a long-standing habit. Timeline:

| Date | Event | Source |
|---|---|---|
| 22 May | The endpoint source *component* J is classified with the radial discriminant. About 25% of its burden is Type IV. The response adds a "regulator" to the source model so that the component becomes Type I. The geometry, and with it the complete demand, is unchanged. | `STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md` (commit ecb5a7e) |
| 24 May – 17 Sep | Source engineering on the beta075 geometry: containment, storage, thermal and optical transfer, joints, condensates, fermions, C1. | agent survey of `supporting_reports/` |
| 8 Sep | First classification on record of the complete demand G/8π. A refinement-stable Type IV layer is present in every operating phase (3,843 dense-grid points). The whole diagnostic took about 186 s. | `LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md` |
| 8 Sep | The legacy classifier fails 15 of 19 analytic fixtures. It labels vacuum and the string cloud ρ = −p_l as Type II. | `LE_BOUNDARY_GATE_PREFLIGHT.md`, `LE_CLASSIFIER_REPAIR.md` |
| 9–17 Sep | Source work continues on a static, zero-shift surrogate of phase 0.745, recorded as leaving "the current-driven Type IV demand untested". | `plan.md` §2026-09-17, `C1_FINITE_MODULE_PAIR_SCREEN.md` l.25 |
| 23 Sep | Standing gate adopted; geometry redesigned. The first one-space boundary layer carries 74,700 Type IV points, which the redesign removes before any source work begins on it. | `SOURCE_FEASIBILITY_WORKFLOW.md`, `ONE_SPACE_REVISION.md` |
| 23–24 Sep | A plateau of e³ leaves 232 Type IV nodes, so e⁴ is adopted. The packet clock then runs at 55× exterior time, with lethal tides, until the compartment redesign. | `LAPSE_AND_STAGING_PASS.md` l.94, l.188 |

The tools to detect the failure existed in May: the 22 May screen computed the
same discriminant, but on one component. The quantitative source work of
May–September was superseded with the geometry.

## 2. Claim-by-claim verdicts

### 2a. "Check cheap necessary conditions before expensive construction"

**Truism.** Generic stage-gate engineering. It earns a sentence, not a heading.
The domain-specific content is the *cost asymmetry*: the complete classification
took minutes (186 s), while the source work it would have redirected took
months. That asymmetry is the argument for the ordering.

### 2b. "Classify the complete demanded tensor, for all observers"

**Evidence-backed, and established in the literature.**
- Literature: claims of positive-energy warp drives that checked only the
  Eulerian energy density failed once all observers were considered (Santiago,
  Schuster & Visser 2022). Warp Factory samples about 10³ observers for this
  reason (Helmerich et al. 2024). Le's observer-robust verification finds that
  the Eulerian reading misses about 73% of the sampled weak-energy violations
  in the Rodal wall (Le 2026b).
- Project: the May component-level classification, followed by a
  component-level fix, left the complete demand unexamined for 3.5 months.
- General point for the book: the complete demand is fixed by the geometry.
  A component's type is a diagnostic of a bookkeeping split, and changing a
  component moves the problem to another component. The handoff document
  already states this (partial sums are diagnostic; the total gives the
  verdict).

### 2c. "On the active metric; static surrogates are insufficient"

**Derivable, and stronger than the project stated.**
- Derivation: if the Eulerian momentum density vanishes, j_i = 0, then the
  normal n is an eigenvector of T and the tensor is Type I. For a static
  metric in static slicing, K_ij = 0, so j_i = 0 identically. A static
  surrogate is therefore Type I everywhere the Killing vector is timelike;
  a static check *cannot* detect Type IV. More generally, Type IV requires
  8πj_i = D_jK^j_i − D_iK ≠ 0, which tells the designer where to look: where
  extrinsic curvature has a divergence, i.e. moving shift gradients and
  time-varying spatial metrics.
- Project: all 4,504 static control samples are Type I, while every one of
  the seven active phases carries a Type IV witness at the same points
  (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md`).
- Literature: Le (2026b, Lemma 2) reaches the same statement for
  time-independent flat unit-lapse slices with a smooth shift of bounded
  vorticity on ℝ³: momentum vanishes exactly for a gradient shift plus rigid
  rotation, and the irrotational Rodal profile is everywhere Type I (Rodal
  2025). The scope matters. With a varying lapse a gradient shift carries
  momentum: 8π|j_i| = |∂_iα ∇²φ − ∂_jα ∂_i∂_jφ|/α² for β = ∇φ
  (`audit_synthesis.md` §1.2 R6). "Irrotational ⇒ Type I" therefore holds
  only at unit lapse.
- Caveat: static controls still carry information about energy conditions.
  Le's static v₀ = 0 limit keeps a boundary deficit, and the project's static
  reset witness has NEC and DEC margins of −0.011. They are useful controls,
  and they can never be a gate for Type IV.

### 2d. "Through the outermost boundary into the exterior"

**Evidence-backed; failures concentrate at source–vacuum transitions.**
- Literature: Le (2026a) scans 600 configurations and finds none admissible.
  The failures sit at the smooth source–vacuum transition, and the Fuchs
  constant-velocity shell has Type IV in its smoothing tail beyond the
  nominal shell.
- Project: the first one-space transverse boundary layer carried 74,700
  Type IV points.
- Scope: this is well supported for shells and layers with smooth
  termination. Whether it holds for every design class is open.

### 2e. "Root-find crossings, because node sampling misses bands"

**Evidence-backed on the problem; the project's method is not the best
available.**
- Project: from e⁵ upward every node was Type I while resolved bands
  persisted to e^6.5 (`AMPLITUDE_PASS.md` l.74–76).
- Literature: interval evaluation of metric and curvature gives pointwise
  certificates *and global bounds between samples* (Le 2026b). That is
  stronger than root-finding along chosen lines. The book should teach the
  problem and present interval certification as the stronger remedy.

### 2f. "Certified classifier"

**Evidence-backed; engineered sources sit on degenerate cases.**
- Project: the legacy classifier failed 15 of 19 fixtures, including vacuum
  and the string cloud ρ = −p_l. That is exactly the tension-dominated case
  that engineered supports favour (`LE_BOUNDARY_GATE_PREFLIGHT.md`).
- Literature alternative: Le (2026b) writes the NEC, WEC and SEC as 4×4
  linear matrix inequalities via the S-lemma, with DEC needing two tests.
  This requires *no* Hawking–Ellis classification and no rapidity cutoff.
  For the energy conditions, the classification step can be bypassed; it
  remains necessary only when the type itself is the question (2g).

### 2g. "Type I is required" (the gate's pass criterion)

**Not generally true. It is a source-class choice.**
- Type IV means the two opposite null directions of a block carry null energy
  of opposite sign (`CONSTANT_RADIUS_TRACK.md`: Δ_rad = T(k₊,k₊)T(k₋,k₋)).
  A single material with a rest frame cannot produce that. Counter-directed
  fluxes can.
- Type IV arises in renormalized expectation values (Martín-Moruno & Visser
  2018). The standard example is a massless conformal scalar in the Unruh
  vacuum on Schwarzschild, which is Type IV everywhere outside the horizon.
  That example is a test-field computation. With back-reaction, Type I is
  forced in these settings (Martín-Moruno & Visser 2021, arXiv:2102.13551,
  checked against the saved full text by `audit_synthesis.md`):
  - static spacetimes (outer domain and horizons);
  - horizons and axes of stationary axisymmetric spacetimes;
  - bifurcate Killing horizons;
  - some Bianchi cosmologies.

  The back-reacted evaporating case is open; Roman 1986 argued for Type IV
  near the apparent horizon.
- Martín-Moruno & Visser 2021 also state that no known classical matter field
  gives a Type IV tensor. The one classical exception found since is
  proper kinetic-gravity-braiding scalars with a timelike gradient (Gergely
  2026, arXiv:2608.15228v1, read at abstract level plus a text search). They
  are Type IV for negative discriminant, and only where the NEC fails. That
  is compatible with a Type IV demand, since a Type IV tensor always violates
  the NEC.
- The book should therefore present the type as a *matching criterion
  between the demand and a source family's algebraic range*. Type I
  certifies compatibility with rest-frame materials. It does not define
  admissibility.
- Project consequence (for the user, not the book): the Type I gate was
  reinstated on 23 September (`9be57e0`, 11:50). About 37 hours later the
  higher-derivative scalars were named the open family (`d128547`, 25 Sep
  00:40). The gate's criterion has not yet been matched to that family's
  algebraic range.

### 2h. "Passing ⇒ proceed to sources"

**Necessary, not sufficient.** The one-space geometry passes the gate, and
every source family but one is then excluded on other grounds
(`SOURCE_SCALING_TEST.md`, `ANEC_MAP_PASS.md`). Caveat: the quantum
exclusion rests on achronal ANEC. That is proven in Minkowski space (Faulkner
et al.; Hartman et al.), for 2D, and for free fields in restricted curved
settings. In the self-consistent curved case it is a conjecture (Graham–Olum),
and test-field counterexamples exist (Urban–Olum; Ishibashi–Maeda–Mefford).
"At any size, in principle" is stronger than that evidence, as recorded in
`inventory/lit_foundations.md`. The word "admissibility"
overclaims; "algebraic compatibility with a source class" says what the
check establishes.

### 2i. "Run the gate alone"

**Observed hazard, one incident.** Designing to pass the gate chose the e⁴
plateau and produced a 55× occupant clock with lethal tides. Gates shape
designs, so they belong in the same pass as the occupant and causal
requirements. With one incident, the book states it as an observed hazard
with its mechanism, not as a law.

## 3. What goes in the book

Parts that survive vetting, in the form a textbook can state:

1. The demanded tensor is fixed by the geometry. Its algebraic structure and
   energy conditions are evaluated on the complete tensor, for all observers
   (2b).
2. **Theorem-level:** zero Eulerian momentum ⇒ Type I. Two kinds of
   evaluation are therefore structurally blind to Type IV: evaluations in
   static slicing, and irrotational-shift evaluations on time-independent
   flat unit-lapse slices. Type IV lives where the momentum constraint is
   sourced (2c).
3. Failures concentrate at transitions to vacuum. The evidence is strong for
   smooth shells and layers (2d).
4. Verification between samples, preferably interval-certified (2e), and
   robust treatment of degenerate tensors, or LMI tests that avoid the
   classification (2f).
5. The type as a matching criterion for source families. Type IV appears in
   test-field quantum states; with back-reaction it is removed in static and
   some stationary settings, and the evaporating case is open. Classically,
   braiding scalars are the one example found, Type IV only where the NEC
   fails (2g).
6. The cost asymmetry that justifies checking before construction (2a), and
   the hazard of optimizing to a single gate (2i).

Dropped: "admissibility" as the name; Type I as a universal requirement.

Placement: items 1–2 and 5 belong in the stress-energy chapter of the
foundations (physics). Items 3, 4 and 6 belong in a verification chapter
(method).

## 4. Findings for the project (outside the book)

- **Citation versioning.** arXiv:2605.25417 now resolves to Le's "Relativistic
  elastic shells: material support and cavity geometry" (v3, 17 Sep 2026). The
  boundary-cost paper the disclosure and the gate handoff cite is v1 (25 May)
  and v2 (20 Jun). The disclosure's `\bibitem{Le2026}` needs `v2` (or `v1`)
  pinned.
- **Gate criterion vs the open source family.** See 2g.
- **Scope of the quantum exclusion.** `ANEC_MAP_PASS.md` and the README
  state that no semiclassical quantum sector can supply the demand "at any
  size". That rests on achronal ANEC, which is conjectural for self-consistent
  curved spacetimes and has test-field counterexamples (see 2h).
- **Relevant 2025–26 literature not in the repo:** Le 2026b (observer-robust
  verification, Warpax), Rodal 2025, Gergely 2026, Bolívar–Abellán–Vasilev
  2026 (lapse freedom in static hollow cores), the Barzegar–Buchert–Vigneron
  source-consistency critique cited by Le 2026a, and "General formalism,
  classification, and demystification of the current warp-drive spacetimes"
  (arXiv:2602.16495). The last two are unread.

## References (verified 2026-09-26 against arXiv/ADS pages)

- Santiago, Schuster, Visser, *Generic warp drives violate the null energy
  condition*, PRD 105, 064038 (2022), arXiv:2105.03079.
- Helmerich, Fuchs, Bobrick, Sellers, Melcher, Martire, *Analyzing warp drive
  spacetimes with Warp Factory*, CQG 41, 095009 (2024), arXiv:2404.03095.
- Le (2026a), *On the boundary cost of source-consistent warp shells*,
  arXiv:2605.25417**v2** (title and content replaced in v3).
- Le (2026b), *Observer-robust energy condition verification for warp drive
  spacetimes*, arXiv:2602.18023 (final version 24 Sep 2026).
- Rodal, *A warp drive with predominantly positive invariant energy density
  and global Hawking–Ellis Type I*, arXiv:2512.18008 (2025).
- Martín-Moruno, Visser, *Essential core of the Hawking–Ellis types*, CQG 35,
  125003 (2018), arXiv:1802.00865.
- Gergely, *Fluid interpretation, Hawking–Ellis classification, and energy
  conditions of the proper kinetic gravity braiding stress tensor*,
  arXiv:2608.15228 (2026).
- Bolívar, Abellán, Vasilev, *Boundary obstructions and lapse freedom in
  static spherical hollow cores*, arXiv:2608.15000 (2026).
