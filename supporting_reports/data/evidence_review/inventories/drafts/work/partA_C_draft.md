## Part A. The Le boundary gate and its repair ladder (8 September)

Timeline of 8 September (commit times, local): `8f13bfe` 09:13 preflight;
`118c064` 09:18 classifier repair; `ed67c3d` 09:38 diagnostic (verdict);
`a6c96dc`/`30edf57` 14:10–14:15 receiver C2 repair; `bba91f2`/`322f51f`/`cbfb68e`
14:39–14:44 bounded metric repair and slowdown; `af814cd`/`468c742` 17:31–17:38
coupled reset source; `9387443`/`812cfee`/`dab8549` 19:43–20:14 inverse search;
then Comer–Andersson (20:46–20:54), Comer two-current (21:12–21:20), Casimir
support (21:34–21:42) and quantum moving boundary (22:05–22:12). Twenty-six
commits in one day. From `8d1bb32` to `42e6688` (9–17 September) follow 183
more commits; 100 reports were added between 8 and 17 September.

### A1. The legacy classifier had corrupted rest-frame quantities since May

*Adds detail to P01 §2f; P01 records only the fixture failure.*

- **Date / commit.** 8 Sep, `8f13bfe` (preflight), `118c064` (repair).
- **What happened.** Besides failing 15 of 19 analytic fixtures, the legacy
  classifier always took the positive square root for the rest energy. For
  negative radial enthalpy the correct branch is
  ρ_rest = [ρ − p_l + sgn(ρ+p_l)√((ρ+p_l)² − 4j²)]/2. The stored rest energy of
  the May endpoint artifacts disagreed with the correct branch on 6,810 baseline
  rows and 26,929 dense rows; largest discrepancy 0.0318; example: stored
  +0.00302, correct −0.02877 (a sign flip)
  (`LE_BOUNDARY_GATE_PREFLIGHT.md` l.64–87). The type test compared the squared
  discriminant with an absolute tolerance of 1e-12 and put the whole near-zero
  band into Type II (l.64–65), so vacuum and small-amplitude ordinary matter
  were labelled Type II.
- **Detected by.** An analytic fixture table (7 tensor families × 3 amplitudes
  = 19 fixtures) and a mixed-tensor eigensystem cross-check, built for the gate
  preflight.
- **Detector available since.** Always: the fixtures are closed-form tensors.
  The classifier entered on 22 May (`ecb5a7e`).
- **Counterfactual.** A fixture table at the classifier's introduction would
  have cost hours. It would have caught the error before the 22 May regulated
  medium admissibility audit (`c7bfa0d`,
  `STAGE2_BETA075_REGULATED_MEDIUM_ADMISSIBILITY_AUDIT.md`, "58 unit tests
  passed"), whose rest-frame margins use this assignment. The four existing
  focused tests passed throughout (preflight l.89–91).
- **Cost.** Every rest-frame-dependent admissibility quantity of the May
  endpoint medium "require[s] reevaluation" (l.80–82; `LE_CLASSIFIER_REPAIR.md`
  l.58–63). The reevaluation was never done, because the geometry itself
  failed the same day.
- **Candidate lesson.** Validate an energy-condition/type classifier on
  analytic fixtures that include the degenerate cases (vacuum, isotropic
  degeneracy, the string cloud ρ = −p), both enthalpy signs, null dust, and
  amplitudes over many decades, with scale-free tolerances.
- **Generality.** General. Engineered supports favour tension-dominated,
  degenerate tensors (ρ = −p_l is the exact radial block of every
  constant-radius design, `CONSTANT_RADIUS_TRACK.md` l.80–84), so the
  degenerate cases are the working cases. The software half of the lesson
  ("test edge cases") is a truism; the domain half (which cases are the edge
  cases, and that sign branches of eigenvalue formulas flip) is not.
- **Recurrence.** Numerical diagnostics failing at degenerate or near-vacuum
  tensors recur 5 times in the window: see E17.

### A2. A role ledger is not a source partition

- **Date / commit.** 8 Sep, `8f13bfe`.
- **What happened.** The component-assignment table repeated the full local
  demanded tensor once per assigned channel, up to four rows per point; the
  repeats agreed with the geometry ledger to 3.39e-21, so summing them as
  independent component stresses would multiply the same source
  (`LE_BOUNDARY_GATE_PREFLIGHT.md` l.104–109). The declared S0/J/R
  decomposition covered 34% of the grid (l.97–102). The fitted endpoint medium
  differed from the geometric J target by 48–50% of the J norm (l.115–119). The
  support audit supplied a fitted exchange current through
  ∇_μT^{μν} = J^ν, which leaves the support tensor undetermined up to any
  divergence-free addition, including its algebraic type (l.137–145).
- **Detected by.** Reconstruction checks during the preflight.
- **Available since.** May (the ledger and fits date from 20–24 May).
- **Counterfactual.** The same reconstruction check at ledger creation: cheap.
- **Cost.** The May "source-role ledger" language entered the technical
  disclosure. The 9 Sep scope review
  (`ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md` l.178–190) repeats that these
  rows "cannot be added as independent physical sources".
- **Candidate lesson.** Assigning demand to components by location and role
  is bookkeeping. A physical source model needs independent component
  tensors whose sum reproduces G/8π, including interaction terms and fit
  residuals. A conservation equation fixes a tensor only up to divergence-free
  additions, so a fitted exchange current says nothing about the tensor's type.
- **Generality.** The divergence-freedom point is an identity, valid for every
  design. The ledger point is general bookkeeping hygiene.
- **Recurrence.** n = 1 in this block (P01 §2b makes the related point that
  component types are diagnostics of a split). Check the source-plant blocks
  for more.

### A3. Non-smooth primitives in a prescribed metric

- **Date / commit.** Found 8 Sep (`ed67c3d`, `30edf57`, `bba91f2`); rule adopted
  23 Sep (`9be57e0`: "C∞ design rule … no clipped powers and no polynomial
  C2/C3 joins").
- **What happened.** Three primitives were non-smooth:
  1. The receiver's clipped square root, u^{1/2} with u = clip(...), gave a
     square-root cusp at ℓ = −0.875. The Eulerian density grew as d^{-3/2}
     (−0.064 → −107.6 as the step fell from 0.0025 to 1.95e-5), and the
     one-sided absolute stress integral grew without bound (0.0012 → 0.0038 →
     0.0120 as the excluded distance fell from 1e-3 to 1e-5)
     (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md` l.151–200). The outer clipping point
     had a slope jump, with density growing as h^{-1} (l.185–189).
  2. A lapse shoulder in |ℓ| had a first-derivative jump at the throat; the
     angular pressure grew 0.0019 → 0.0258 under refinement
     (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md` l.136–155).
  3. The support-shell Gaussian cap started at a nonzero slope; the shift
     derivative jumped by −4.705 (`LE_BOUNDED_METRIC_REPAIR.md` l.40–55).
  The receiver power primitive dates from 20 May (`beafedf`,
  `source_ledger.py` l.138, l.596).
- **Detected by.** Step-halving at the exact join locations, plus the analytic
  scaling of the cusp. A systematic primitive audit then followed (bounded
  repair l.63–97: every clip, cap, schedule and compact profile tabulated with
  its join order).
- **Available since.** Always. The audit is a code read plus finite-difference
  probes.
- **Counterfactual.** A primitive audit in May would have removed the
  singularities in hours. All sampled "absolute burden" budgets of the
  receiver region were resolution-dependent in the meantime ("Finite-grid
  whole-profile norms therefore provide sampled burdens, with their values
  depending on edge resolution", diagnostic l.199–200).
- **Cost.** Moderate. Burden numbers near the receiver from May to September
  depended on the grid. The C2 repair itself was cheap (169 s and 88 s
  runs). C2 joins still converge only at first order at the joins
  (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md` l.79–81), which motivated the C∞ rule.
- **Candidate lesson.** Build prescribed metrics from C∞ primitives (smooth
  steps built from exp(−1/t)), and audit every clip, abs, max and piecewise
  join. A kink in a metric function is a surface layer (Israel junction) and
  a cusp is a non-integrable stress. Neither belongs in a thick-source design
  unless it is modelled as such.
- **Generality.** General for any prescribed-metric design, because the
  Einstein tensor uses second derivatives. Relativists know this; the
  practice of auditing the primitives is worth a paragraph.
- **Recurrence.** Three primitives in one geometry; the C∞ rule held through
  all later designs with no recurrence.

### A4. A local repair cannot change a demand outside its support

- **Date / commit.** 8 Sep, `a6c96dc`/`30edf57`.
- **What happened.** The receiver C2 repair fixed the cusp. All 104 retained
  Type IV witnesses had bitwise-identical raw tensors afterward, because they
  lay outside the repair bands and their stencils
  (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md` l.98–104). Phase-profile Type IV samples
  went from 1,361 to 1,365.
- **Detected by.** A direct locality comparison.
- **Counterfactual.** Predictable before the run, since the Einstein tensor is
  local and the witnesses sat outside the repair's support. The repair was
  aimed at regularity, and it achieved that.
- **Cost.** Negligible (21,443 evaluations, 169 s).
- **Candidate lesson.** Before running a repair, check that its support
  overlaps the defect.
- **Generality.** Truism. It belongs in the book only as a one-line remark.
- **Recurrence.** n = 1.

### A5. Uniform slowdown: a scaling argument used as a stopping rule

- **Date / commit.** 8 Sep, `bba91f2`/`cbfb68e`.
- **What happened.** Slowing evolution and shift together (σ = κt) scales
  K_ij by κ, so j scales by κ and the diagonal channels as X_0 + κ²(X_1 − X_0).
  At a static enthalpy zero the discriminant is κ²(κ²h₂² − 4j₁²), negative for
  every κ < κ_c = 2|j₁|/|h₂|. The measured κ_c is 1.2948 at the clearest root,
  converged under three step halvings; all 28 static-enthalpy roots stay
  Type IV at rates 1/4 to 1/64 (`LE_BOUNDED_METRIC_REPAIR.md` l.99–171).
  The report then "stops further parameter patching" (l.238–253). It also
  records that the node grid at spacing 0.025 found all 321 points Type I at
  rates 1/32 and 1/64, while targeted profiles resolved 41 of 81 Type IV points;
  the layer had narrowed to widths of 0.0056 and 0.0027 (l.187–192).
- **Detected by.** An analytic scaling of the ADM constraints, confirmed
  numerically.
- **Available since.** Always (the ADM momentum and Hamiltonian constraints).
- **Counterfactual.** The scaling argument costs minutes and could have
  preceded any slowdown numerics. Here it came first, and the run confirmed it.
  This is a positive example.
- **Cost.** Small.
- **Candidate lesson.** Before sweeping a knob, derive how the obstruction
  scales with it. A knob that multiplies the obstruction's sign-determining
  expression by a positive factor cannot remove it. Uniform slowing cannot
  remove current-driven Type IV at enthalpy zeros. The same derivation shows
  that the static limit can be Type I while every evolving neighbour is not.
- **Generality.** The κ-scaling holds for every ADM metric under uniform time
  reparametrization with shift scaled alike, so it is a general identity. The
  node-grid blind spot is general (see E8).
- **Recurrence.** Analytic structural arguments that decided or stopped a
  branch: A5, A6 (enthalpy cancellation), A7 (onset expansion), E1 (null
  Hessian), E6 (shear/Hessian/flux identities), E12 (normal-speed
  condition), and the closure pass's speed-as-lapse-contrast identity:
  n ≈ 7. Node-grid miss: n = 3 (E8).

### A6. A pre-registered source candidate relocates the failure and overdraws the mass budget

- **Date / commit.** 8 Sep, `af814cd` (registered design committed before the
  run), `468c742`.
- **What happened.** A Le-inspired prescription (tangential material plus two
  null streams replacing part of the radial string support) had one density
  ratio, one pressure ratio and one handoff profile, "no outcome-driven
  tuning", and a stop rule: a refinement-stable failure of complete-source
  Type I or of the radial Einstein condition f > 0 stops it
  (`LE_COUPLED_RESET_SOURCE_ATTEMPT.md` l.37–50). The old principal witness
  became Type I (Δ −0.00206 → +0.00123). A converged Type IV witness then
  appeared farther out at ℓ = −2.133, and a new Type IV interval appeared at
  s = 2.6, where the reference had none (l.149–192): 2,030 of 8,253 samples
  Type IV. The Hamiltonian mass response gave f = −0.609. The source needed
  δm ≈ 1.433 against an allowance of 0.533 (l.194–206). The mechanism is
  algebraic: h_total = h_b + 3F, and the string release B cancels (l.226–247).
- **Detected by.** Complete-source classification plus the Misner–Sharp mass
  equation m = m_b + 4π∫(2F − B)r²dr.
- **Available since.** Always.
- **Counterfactual.** The algebraic cancellation and the mass integral could
  have been evaluated by hand before implementing the run; the whole run took
  76.6 s.
- **Cost.** Small in compute; about 3 hours wall.
- **Candidate lesson.** (i) When the geometry fixes the demand, a source that
  cures the discriminant at one witness moves the deficit elsewhere, because
  the complete tensor is still G/8π. (ii) In spherical symmetry the mass
  function gives a necessary budget, f = 1 − 2m/r > 0, that any added source
  energy must fit inside. Evaluate it before constructing dynamics.
- **Generality.** (ii) is general for spherically symmetric designs and has a
  quasi-local analogue elsewhere. (i) restates P01 §2b: the demand is fixed by
  the geometry.
- **Recurrence.** Relocation under local source fixes: the May regulator (P01
  table row 22 May), here, and the 17 Sep C1 edge migration (D11): n = 3. The
  user-supplied gate handoff named the test in advance: "does the composite
  source actually cure the edge, or merely move it outward one layer at a
  time?" (`active_rail_test1_le_boundary_gate_handoff.md` l.24, 103).

### A7. Onset analysis versus a bounded optimization

- **Date / commit.** 8 Sep, `9387443` (registered design), `812cfee` (onset
  audit), `dab8549`.
- **What happened.** The search ran 1,024 scrambled Sobol controls, 16 boundary
  seeds and 8 Powell solves. Every local solve hit its 240-evaluation cap. 780
  of the 1,024 exploration controls ended with the numerical lapse range
  exhausted and are "physically undecided" (`LE_RESET_INVERSE_SEARCH.md`
  l.257–276). No finalist was admissible: negative material density to
  −5.9e-5, radial margin −7.3e-4, angular mismatch 2.9e-3 (l.278–287). An
  asymptotic expansion at the outer boundary's startup then showed the
  failure for every member of the registered families. The geometry demands
  an angular stress at order u^{n−2}; the registered sources supply it only at
  u^{2n−2} (l.359–424). The search then stops "with the four registered
  families" (l.450–455).
- **Detected by.** A pencil-and-paper onset expansion, confirmed at 80 sample
  points (coefficient ratios 0.997–1.000 for the direct path).
- **Available since.** Always.
- **Counterfactual.** The expansion needs only the boundary data and the
  source laws. It could have preceded the search and would have made the
  search unnecessary for these families. The report itself draws the
  conclusion: "a source-and-boundary condition that a subsequent construction
  can confront before a larger run" (l.455–456).
- **Cost.** Low in compute (44 s run, 171 MB of output); roughly 2.5 hours of
  implementation.
- **Candidate lesson.** Before optimizing a source family against a
  time-dependent geometry, expand the field equations at switch-on and at the
  boundaries. The order at which the geometry demands each stress channel,
  against the order at which the source can supply it, often decides the whole
  family. Optimizer non-convergence is not infeasibility, and optimizer
  success is not existence.
- **Generality.** General for any switch-on, handoff or reset in
  time-dependent designs. The "order-matching at onset" check is standard in
  PDE initial-boundary problems (compatibility conditions); its use as a
  source-family screen is the domain content.
- **Recurrence.** Part of the n ≈ 7 analytic-argument cluster (A5).

### A8. The repair ladder as a whole: candidate-level stops held; the written program-level rule was not followed

- **Date / commits.** 8 Sep 09:13 – 17 Sep (`8f13bfe` … `42e6688`).
- **What happened.**
  - **Each rung stopped honestly.** Every rung had a registered acceptance
    test and stopped quickly:
    - receiver repair: "succeeds locally … continues to fail";
    - bounded repair: "stops further parameter patching";
    - coupled reset: "registered stopping point for the single candidate";
    - inverse search: "stops with the four registered families".
  - **The diagnosis named a geometric remedy.** Rung 5 said what was needed:
    "A successful further design would have to control the current at
    static enthalpy zeros, change the sign structure of that enthalpy, or
    alter the coupled evolution in another structural way"
    (`LE_BOUNDED_METRIC_REPAIR.md` l.241–245).
  - **A program-level rule already existed.** The user-supplied gate handoff,
    whose vocabulary the preflight and diagnostic use and whose verdict
    category the diagnostic returns, contains a decision rule:
    - "**INTERNAL CLOSURE FAILURE — redesign before Comer inversion**"
      (`active_rail_test1_le_boundary_gate_handoff.md` l.156);
    - "Only a PASS makes the Comer-style inverse constitutive tests the next
      priority" (l.162).
    The verdict at 09:38 was INTERNAL CLOSURE FAILURE.
  - **The ladder went on changing the source instead.** After the two
    geometric repairs, the rungs changed the source for the fixed geometry:
    coupled reset (17:31), inverse search (19:43), then the Comer–Andersson
    inverse construction itself at 20:46 (`cc5e253`), then Comer two-current,
    Casimir and quantum boundaries. From 9 September the work moved to
    source-plant engineering on a static surrogate. The handoff defines that
    surrogate as its *control* (l.119–126): "edge is Type I in holding but
    becomes Type IV only during active current → Le-like flux/tilt failure".
  - **The rule entered the repository late and as background.** It was
    committed only on 16 Sep, filed as "separate research context"
    (`e7a9951`). The 17 Sep workflow had no gate stage (`git show
    1e9ac1d:supporting_reports/SOURCE_FEASIBILITY_WORKFLOW.md`, investigation
    table).
  - **The remedy, once applied, was fast.** It was carried out on 23 Sep by
    holding the areal radius constant where the metric evolves (E1). The
    gate was reinstated at 11:50 and passed at 14:07 (13,587 Type IV points →
    0).
- **Detected by.** The standing-gate reinstatement (`9be57e0`, 23 Sep),
  user-agreed ("Agreed direction").
- **Available since.** 8 Sep 09:38: the verdict plus the handoff's rule. The
  identity that implements the redesign is textbook (E1).
- **Counterfactual.** Following the handoff's own rule on 8 Sep would have
  meant geometry redesign instead of inverse source construction. Measured on
  23 Sep, that redesign took about 2 h 17 min. It would have skipped most of
  the 183 commits of 9–17 Sep. Caveat: some of that work (classifier,
  evaluators, quantum-inequality machinery) was reused, so the saving is less
  than the full count.
- **Cost.** High: 9 working days, 183 commits, about 100 reports. Most of their
  conclusions are now scoped to a static phase-0.745 slice of a failed
  geometry (`plan.md` l.298–305).
- **Candidate lesson (stopping rules).** Stopping rules are needed at two
  levels, and both must be binding where work is planned.
  - **Candidate level:** pre-registered acceptance, no outcome tuning, and a
    stop on a refinement-stable failure of a necessary condition. This keeps
    each attempt honest and cheap, and this record supports it.
  - **Program level:** when the demand gate fails, redesign the geometry
    before constructing sources. The rule existed in writing, and it was
    bypassed because it lived in a handoff document outside the research-order
    document and the standing plan.
  - A second written stop rule was also bypassed the day it was written: the
    17 Sep workflow's "insufficient normalized strength … ends when it leaves
    that cause unchanged" was followed by three more population-refinement
    commits after the 5.8e7-field result (D-list, F).
- **Generality.** The two-level structure is plausibly general. "The demand
  gate precedes source construction" is P01's ordering. The new evidence here
  is that a written rule does not bind unless it sits in the document that
  orders the work. This is a governance heuristic, not physics.
- **Recurrence.** Written stop rules not applied: n = 2 (the handoff on 8 Sep;
  the workflow on 17 Sep). Program-level non-return to geometry: n = 1. The
  candidate-level stop worked 4 times on 8 Sep and many times in Parts B–D.

### A9. The failed-gate verdict dropped out of the status documents

- **Date / commits.** 9 Sep: `921e560` (16:59) put the Le results into the
  technical disclosure; `734156c` (20:31, "Remove source-trial narratives from
  the technical disclosure") took them out. 23 Sep: `9be57e0` restored them.
- **What happened.**
  - `921e560` wrote into the disclosure: "The regularized metric tests retain
    active Type IV demand near static enthalpy zeros. Current and diagonal
    stress must therefore evolve together where an ordinary material rest
    frame is required."
  - `734156c` replaced this with a conditional requirement: "Where a material
    description requires an ordinary energy frame, current and diagonal
    stress evolve together within the permitted tensor class." The statement
    that the reference geometry fails was gone.
  - `plan.md` still carried its 23 May handoff through 17 September. It never
    recorded the verdict (`git log -S'Type IV' -- plan.md` shows no change
    before 23 Sep). Nor did the README.
  - `9be57e0`'s message: "That verdict had dropped out of the current
    handoff, the source-feasibility workflow and the README, while later
    source work continued on a static surrogate."
- **Detected by.** Review on 23 Sep, apparently user-directed: the plan says
  "Agreed direction (2026-09-23)".
- **Available since.** 8 Sep.
- **Counterfactual.** One line in the handoff ("reference geometry: INTERNAL
  CLOSURE FAILURE, Type IV in every phase") costs nothing.
- **Cost.** A contributor to A8; the causal share cannot be separated.
- **Mechanism.** The repository's style rules demand affirmative language
  ("Avoid 'not'…", "Only use locked in recognized as solid design elements",
  "NEVER use the technical disclosure as a running log", `AGENTS.md`). The
  disclosure was also the only document then being updated. The rewrite
  complied with the rules and removed the negative verdict.
- **Candidate lesson.** A failed necessary condition on the reference design
  is status, not narrative. It belongs in the standing status document until
  the design changes. Writing rules that favour affirmative statements should
  not apply to status.
- **Generality.** Process and management, not physics. For the book this is
  at most a sentence in a methods chapter; it is a known engineering-management
  failure (lost open issues).
- **Recurrence.** Knowledge already in the record that was not applied when
  it mattered: this (verdict lost); the Casimir holding cost (E10, 8–9 Sep vs
  24 Sep); the wormhole framing since May vs the topology decision on 23 Sep
  (E5); the May 20 list of "not shown" quantum-inequality/ANEC gates vs 25 Sep
  (E15); the 9 Sep scope correction (B10); the handoff's decision rule (A8);
  the standing host rejection dropped from the 17 Sep summary (D5). n = 7.

## Part E. The redesign (23–25 September)

Scale: 30 commits and 16 reports took the design from the failed beta075
geometry to a closed, gate-passing prescribed geometry with a flat passenger
compartment and an in-principle narrowing of the source class.

### E1. The spherical null-Hessian identity turned the failure into a design rule

- **Date / commit.** 23 Sep, `9c1021a`.
- **What happened.** In spherical symmetry
  8πT(k,k) = −(2/R) k^a k^b ∇_a∇_b R for radial null k, so
  Δ_rad = T(k₊,k₊)T(k₋,k₋). The radial block is Type IV exactly where the two
  radial null energies have opposite signs (`CONSTANT_RADIUS_TRACK.md`
  l.27–49). An attribution run (features switched off, same classifier)
  assigned the failure: 842 Type IV points for the repaired geometry, 874 for
  support decompression alone, 19 for a static support with carrying flow
  (l.51–71). About 98% of the integrated burden came from decompression acting
  on a varying areal radius. Design rule: hold R constant wherever the metric
  evolves. The radial block is then an exact string cloud with zero current
  (l.73–95). Result: 13,587 → 0 Type IV points on the 141,661-point map, with
  the beta075 service reproduced (l.160–176, 231–243).
- **Detected by.** Derivation plus ablation.
- **Available since.** The identity follows from the warped-product form of
  the Einstein tensor; it has been standard since the Misner–Sharp era.
  Usable in May, and certainly on 8 Sep.
- **Counterfactual.** Applied on 8 Sep after the diagnostic, it would have
  given the geometric fix that A5 asked for within a day.
- **Cost of lateness.** See A8.
- **Candidate lesson.** For each symmetry class used in design, derive the
  null-energy identities that express T(k,k) through the metric functions
  (here, the Hessian of the areal radius). They convert a classification
  result into an explicit design rule, and they tell the designer which
  metric function to freeze.
- **Generality.** The identity holds for every spherically symmetric
  spacetime. The axial analogues (E6) confirm the pattern in a second class.
  The design rule ("keep the radius constant where the metric evolves") is
  specific to warped products but has analogues.
- **Recurrence.** Identities that produced design rules: spherical (E1), axial
  shear/Hessian/flux (E6), census ρ√γ = −(1/8π)∂_r(r∂_rA) (E2/E7), flat-slice
  ρ = −(Aβ_r/α)²/32π (`LAPSE_AND_STAGING_PASS.md` l.56–73), and the
  compartment flatness transformation (`COMPARTMENT_PASS.md` l.54–68): n = 5.

### E2. Inherited mechanism elements that the design did not need

- **Date / commits.** 23–24 Sep: `9c1021a`, `5abcc98`, `2a3f404`, `97a78ca`,
  `564e69f`.
- **What happened.** Three elements carried over from beta075 turned out to
  generate most of the demand and to be unnecessary:
  1. **Decompression overlapping service.** The support-stretch reset
     ("relax/decompress the throat support, reset the plant") overlapped
     catch, carry and release. It carried about 98% of the Type IV burden
     (E1). On the constant-radius track, 95% of the angular deficit integral
     lay after the live window. A reset moved after the window cut the
     deficit by 98% (`CONSTANT_RADIUS_TRACK.md` l.297–318;
     `RESET_SCHEDULE_OPTIONS.md` l.75–82).
  2. **The standing support stretch of about 600.** The axial report concluded
     that the one-space service "keeps its stretch as a standing structure"
     (`AXIAL_TRACK.md` l.265–268). The amplitude pass found "The support needs
     no stretch" (`AMPLITUDE_PASS.md` l.13–15): energy fell 450×. The static
     Hamiltonian constraint gives ρ√γ = −(1/8π)∂_r(r∂_rA), so the energy
     follows the stretch alone (`DEMAND_CENSUS.md` l.126–149).
  3. **The packet carve.** It carried the packet-coordinate speed advantage
     (0.352 without it, `ONE_SPACE_REVISION.md` l.154–155). It also produced
     the residual Type IV bands (l.29–35). The choreography pass then showed
     that a path-matched shift "carries the lane speed by itself" on a static
     support (`CHOREOGRAPHY_PASS.md` l.34–38).
- **Detected by.** Attribution runs and the census identity.
- **Available since.** The identity always; ablation at any time.
- **Counterfactual.** An ablation of each inherited element against the
  demand, done when the one-space embedding was first built (23 Sep
  afternoon), would have skipped the e⁸ pre-sheath stage (E7). Its cost was
  hours, not days.
- **Candidate lesson.** When a design is carried into a new model or
  embedding, re-derive the need for every inherited element. Ablate each
  against the demand, occupant and service metrics before tuning the rest.
- **Generality.** General design practice; ablation is a truism in
  engineering. The domain content is the identities that make it quick:
  energy density follows the spatial stretch, and a lapse carries no energy
  where the shift vanishes.
- **Recurrence.** Three elements in two days: n = 3.

### E3. Two kinematic readings of the packet's motion

- **Date / commit.** Found 23 Sep (`5abcc98`); resolved 23 Sep (`cb3008a`).
- **What happened.** The beta075 packet windows advanced along ℓ = σ at unit
  speed, while the shift carried the packet at U_packet/B: 0.625 before the
  catch and 0.0625 after. When the live window closed, the window centre stood
  at 1.645 while the velocity reading put the packet at 0.853. The windows led
  the packet by 0.8–0.9, more than twice the window radius of 0.35
  (`RESET_SCHEDULE_OPTIONS.md` l.92–111). The packet-safety audit evaluated
  the velocity field at the window points, and the probes followed the
  velocity field (l.104–108). The inconsistency dates from May and is item 4
  of the May paper's issues (`THROAT_GEOMETRY_CLARIFICATION.md` l.159–164).
- **Detected by.** Comparing delivery times across reset schedules. Delivery
  changed only under the velocity reading.
- **Available since.** May: a trajectory-consistency check needs no new tool.
- **Counterfactual.** One consistency test in May (does the packet's
  integrated worldline stay inside its windows?).
- **Cost.** The May paper's packet screen and the disclosure's service-time
  ratios inherited it; correction by addendum.
- **Candidate lesson.** Define the payload worldline once. Derive every
  payload-attached field (windows, carve, lapse plateau) and every payload
  audit from that one worldline, and test that the payload stays inside its
  own region.
- **Generality.** General for any design with a payload region moved by a
  shift. The consistency check is close to a truism, but the failure is
  easy to make because the shift and the region profiles are separate inputs.
- **Recurrence.** n = 1.

### E4. The advantage metric was ill-posed and insensitive

- **Date / commits.** Recognized 23–24 Sep (`2a3f404`, `cb3008a`, `db79203`,
  `9bdf376`).
- **What happened.** The disclosure's service-time ratios (2.569 schedule
  factor, 1.233 packet-coordinate proxy) compared the packet's service time
  with an exterior null signal between endpoints in separate asymptotic
  regions. That exterior path does not exist in a two-ended geometry
  (`THROAT_GEOMETRY_CLARIFICATION.md` l.165–175). The schedule-factor
  advantage also stayed at 2.569 across every variant, while the
  velocity-read arrival at ℓ = 5 moved from 10.1 to 23.4 to 39.8
  (`ONE_SPACE_REVISION.md` l.135–147). The first well-posed comparison (packet
  and light in one flat exterior, same coordinate distance) came with the
  choreography pass: lead 1.66, mean 1.35c (`CHOREOGRAPHY_PASS.md` l.17–20).
- **Detected by.** The topology decision (E5) and the kinematic reading
  (E3).
- **Available since.** May.
- **Counterfactual.** Define "faster than light" at the outset as the payload
  arriving before the earliest signal through the same background, with both
  in one spacetime.
- **Cost.** The headline figures of the May paper and the disclosure needed
  correction by addendum.
- **Candidate lesson.** The performance metric of a transport geometry must be
  defined within that geometry: arrival of the payload against the earliest
  causal signal between the same events through the unmodified background.
  Check that the metric responds to the quantity it names; a proxy that stays
  constant while arrival time quadruples is measuring the schedule.
- **Generality.** General. The literature uses the same criterion (a
  comparison with the fastest signal in the background is the standard
  definition of effective superluminality). Supporting citation to verify:
  Visser, Bassett & Liberati, "superluminal censorship" (recalled, not
  verified here).
- **Recurrence.** n = 2 (ill-posed reference; insensitive proxy).

### E5. The throat metric was a two-ended wormhole that needs a topology change

- **Date / commits.** Decided 23 Sep 17:39 (`2a3f404`); written up 24 Sep
  (`db79203`, `86a557f`, `9bdf376`), with an addendum to the May paper.
- **What happened.** The reduced metric had areal radius
  (ℓ² + R_th²)c_Ω², an Ellis throat with R → |ℓ| on both sides. Its spatial
  slices are R × S² with two ends: a Morris–Thorne wormhole
  (`THROAT_GEOMETRY_CLARIFICATION.md` l.44–83). Forming a two-ended space from
  ordinary space requires a change of spatial topology. In a compact region
  that brings closed timelike curves (Geroch 1967, cited l.136–141). The
  minimal sphere persisted through every service, so the "relax throat" step
  never closed it (l.123–135).
- **When it could have been known.**
  - 16–17 May: the metric form was in the disclosure (throat/core support,
    ℓ² + R_th²). The first `plan.md` framed the rail against "a conventional
    traversable wormhole … the ordinary Morris-Thorne passenger-traversability
    requirement" (plan at its first commit, l.27–32). The May paper's title
    is "From the Warp/Wormhole Interface to a Throat-Supported Shift Rail".
    The wormhole character was known. Its consequences (topology change for
    construction; no exterior path for the service-time comparison) were not
    drawn.
  - 8 Sep: the preflight identified the late-time exterior as the ultrastatic
    throat with a negative-energy |ℓ|^{-4} tail on both ends; "A region label
    such as far_exterior supplies a bookkeeping location; the stress tensor
    supplies the vacuum criterion" (`LE_BOUNDARY_GATE_PREFLIGHT.md` l.147–178;
    `LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md` l.233–257).
  - 9 Sep: the scope review noted that the exterior "is distinct from assuming
    an always-open two-mouth transport route"
    (`ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md` l.122–130).
  - 23 Sep 14:07: the constant-radius report attributes its end transitions to
    "the two-ended spherical model". Its flare-out identity
    (R'/A)' = −4πR(ρ+p_ℓ)/A requires at least one unit of radial null deficit
    per end (`CONSTANT_RADIUS_TRACK.md` l.320–342). The same minute, the
    disclosure was updated to this two-ended geometry (`2146526`).
  - 23 Sep 15:59: "The two-ended track remains the gate-passing geometry"
    (`6e1a1fb` plan diff).
  - 23 Sep 17:39: "a two-ended geometry is a wormhole whose ends would require
    a change of spatial topology" (`2a3f404`).
- **Detected by.** The termination decision on the constant-radius track,
  which made the ends explicit; the decision was labelled "(decided)", most
  likely by the user.
- **Counterfactual.** A global-structure statement at design start (count the
  asymptotic ends; check whether the intended construction from ordinary space
  is topologically possible) takes an hour. It uses textbook results
  (Geroch 1967; the Morris–Thorne flare-out condition).
- **Cost.**
  - The May paper's topology, source premise and headline ratios were
    corrected by a two-page addendum.
  - The disclosure was revised twice within 36 hours.
  - The "opening" and end-transition source work addressed a feature that the
    one-space rail removes: the semiclassical opening comparison supplying
    about 5e-6 of the requirement, the condensate matching "through the
    asymmetric rail throat" (commit `b4bd0a9`), and C1 modules on the throat.
    The Part B notes carry details.
- **Candidate lesson.** Record the global structure of a prescribed metric
  before any source work: topology of the slices, number of asymptotic ends,
  horizons, and which exterior any performance comparison uses. Check it
  against how the object is meant to come into being. A geometry that
  ordinary sources could hold open may still be one that no source can form.
- **Generality.** General and literature-backed (Geroch; topology-change
  theorems). It applies to any design with a minimal surface or a "throat".
- **Recurrence.** n = 1 major incident. Related: the bookkeeping label
  "far_exterior" (preflight), and E4.

### E6. A gate pass in one symmetry reduction did not survive a change of embedding

- **Date / commits.** 23 Sep, `0dfcf6e`/`6e1a1fb` (15:59).
- **What happened.** The constant-radius spherical track passed with zero
  Type IV points. The same service embedded in one flat space around an axis
  failed: 74,700 of 374,187 non-vacuum boundary-layer points were Type IV
  (20%), including all 217 live samples, and the count was stable under
  refinement (74,702) (`AXIAL_TRACK.md` l.33–40). Attribution: lapse alone 0,
  carry shift alone 120,363, stretch alone 53,576. The mechanism is the shear
  identity 8πT(n±e_z, n±e_z) = −(β_r² ± Δ_⊥β). It gives opposite signs
  wherever |Δ_⊥β| > β_r², a condition that holds at every edge of a shear
  layer. "The spherical track carries its shift uniformly over closed
  cross-sections and has no such layer" (l.191–204).
- **Detected by.** Exact modelling of the one-space embedding within hours.
- **Available since.** Same day. Caught early, so this is a check that
  worked.
- **Cost.** Small. The disclosure had been updated to the two-ended geometry
  two hours earlier (see E16).
- **Candidate lesson.** A symmetry reduction can forbid a failure mode
  outright: a spherical shift has no transverse shear, and a static slice
  has no momentum density (P01 §2c). A pass in a reduced model certifies that
  model only. Re-run the gate in the embedding the design will actually use.
- **Generality.** General; the shear identity and the static-momentum theorem
  are exact.
- **Recurrence.** Reduced models blind to a failure: static surrogate (P01),
  spherical → axial (here), radial-only escape audits → 3D lapse cavity
  (E14): n = 3.

### E7. A gate passed by raising an amplitude hid a large cost and side effects

*Extends P01 §2i, which records the e⁴ plateau and the 55× clock as a single
incident.*

- **Date / commits.** 23 Sep: `2a3f404` (one-space revision), `cb3008a`
  (choreography), `9ab01d4` (census), `97a78ca` (amplitude pass). 24 Sep:
  `564e69f`.
- **What happened.**
  - The one-space revision passed with a conformal pre-sheath of e⁸ and a
    lapse sheath of a further e⁸.
  - The census then found that the pre-sheath carried 99.98% of the energy:
    3.39e7 of each sign, Gμ/c² ≈ 2e4, 13 solar masses per metre. Energy grows
    as e^φ, and e⁶ already passed the node screen at 8× less energy
    (`DEMAND_CENSUS.md` l.23–29, 151–178).
  - The amplitude pass then cut the energy 450× with an unchanged service, by
    flattening the support and taking the band-free threshold e⁷.
  - The lapse-staged design brought standing energy to zero.
  - Side effects of the e¹⁶ lapse maximum:
    - clocks in the sheath ran at up to 9e6 times exterior time
      (`ONE_SPACE_REVISION.md` l.127–131);
    - the standing geometry became a superluminal signal channel: light
      reached ℓ = 5 at σ = 0.85, against 3.34 for the packet, and "two rails
      in relative motion can close causal curves"
      (`CHOREOGRAPHY_PASS.md` l.160–191);
    - the packet's peak clock rate was 9,069× in the census design and 140×
      after the amplitude pass. These were first tabulated a day later, in
      `LAPSE_AND_STAGING_PASS.md` l.178–192. The earlier passes do not report
      them.
- **Detected by.** Magnitude census and, later, the clock table.
- **Available since.** The census identity always. The clock is an integral
  along the packet path.
- **Counterfactual.** Running the census, clock and light-channel checks in
  the same pass as the gate. The census ran about 4 hours after the one-space
  revision.
- **Cost.** Hours. The expensive designs lived half a day, but they
  entered the handoff as the reference.
- **Candidate lesson.** When a gate is passed by increasing an amplitude, find
  the smallest passing value and report the cost scaling and the side effects
  in the same pass: demand magnitude, occupant clock and tides, causal
  channels. Gates are pass/fail; designs need magnitudes.
- **Generality.** Heuristic. The evidence is several incidents in one project
  within 48 h.
- **Recurrence.** Gate-first choices with hidden cost: the e⁸ pre-sheath
  (here), the e⁴ plateau and 55× clock (P01), the 15° cone chosen at one speed
  (E12): n = 3.

### E8. Node sampling missed Type IV bands (recurrence count for P01 §2e)

- **Instances.**
  1. 8 Sep slowdown. On the node grid (spacing 0.025) all 321 points were
     Type I at rates 1/32 and 1/64; targeted profiles resolved 41 of 81
     (`LE_BOUNDED_METRIC_REPAIR.md` l.187–192).
  2. 23 Sep one-space first-draft stack. 0 Type IV at 4,884,931 nodes, yet
     root-finding found bands at 60 of 60 samples, up to 2.0e-4 wide
     (`ONE_SPACE_REVISION.md` l.62–70).
  3. 23 Sep census. The e⁶ pre-sheath "passes the node-level gate screen";
     the amplitude pass moved the threshold to e⁷ (every node Type I from e⁵
     up, bands to e^6.5; `AMPLITUDE_PASS.md` l.74–77). Commit `97a78ca`
     corrected the census report accordingly.
- **Lesson.** As in P01 §2e: verify between nodes. n = 3.

### E9. Gate domains that stop short of the structure

- **Date / commits.** 8 Sep (preflight exterior); 23 Sep census (`9ab01d4`).
- **What happened.**
  - On 8 Sep, the "far_exterior" label covered a sourced |ℓ|^{-4} tail
    (E5).
  - On 23 Sep, the choreography gate had sampled σ ≥ −1.5 and |z| ≤ 4.9. The
    transit begins at σ ≈ −7, and the sheath tapers out to |z| = 6.5
    (`DEMAND_CENSUS.md` l.41–46). The extended domain passed.
  - Later passes moved to σ ∈ [−8, 10], |z| ≤ 8 and then ≤ 10.
- **Candidate lesson.** A gate's domain must cover the full space-time support
  of every non-vacuum field, including switch-on, switch-off and tapers, out
  to exact vacuum.
- **Generality.** General; close to a truism. P01 §2d covers the exterior
  half.
- **Recurrence.** n = 2 (one caught as a real failure, one clean).

### E10. The "Casimir sector plus positive mass" idea

- **Date / commits.** Proposed 24 Sep (`564e69f`,
  `LAPSE_AND_STAGING_PASS.md` l.256–258: "A tension with zero energy density
  can in principle combine a negative-energy, negative-pressure sector
  (Casimir-type) with ordinary positive mass"). Refuted 25 Sep (`d128547`,
  `SOURCE_SCALING_TEST.md` l.24–30, 197–232).
- **What happened.** Matching the demand's peak deficit needs a gap of
  0.58√(ℓ_P L): 2.3e-18 m, with modes at 530 GeV, at L = 1 m. One skin depth
  of electron mirror carries about 1.2e7 k³ times the deficit it bounds
  (ultra-relativistic regime) or more than 1.6e7 (non-relativistic). "The
  Casimir and positive-mass combination proposed in the staging pass has no
  working regime."
- **Detected by.** A back-of-envelope plasma-frequency and skin-depth estimate.
- **Available since.** The project's own record, 8–9 Sep:
  - `VACUUM_SUPPORT_SELECTION_ROUNDS.md` l.87–92 applied the Costa–Matsas
    bound: DEC holding matter carries at least 3C, "leaving a positive total
    energy of at least 2C per cavity volume before adding further plate
    mass".
  - `RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md` l.5–11: "The ordinary holding
    contribution exceeds the negative binding energy throughout … All 154
    sampled response pairs and the independent analytic bound give a positive
    complete held assembly".
- **Counterfactual.** A search of the record before proposing the idea.
- **Cost.** Negligible: one paragraph, refuted the next morning. It is
  recorded because it is a clean refuted idea.
- **Candidate lesson.** Charge a negative-energy source with its enabling
  hardware (plates, mirrors, holding matter) before counting its deficit. For
  Casimir sources the hardware dominates by orders of magnitude at every
  scale.
- **Generality.** General for boundary-induced vacuum sources;
  literature-backed through Costa–Matsas (cited in the repo) and the Sep 25
  estimate.
- **Recurrence.** Knowledge in the record not applied: n = 4 (A9).

### E11. The front light surface: the known warp-drive horizon problem

- **Date / commits.** Present from 23 Sep (`cb3008a`, the 2.1c lane) onward.
  The rear surface was noted 25 Sep 00:40 (`d128547`); the front was found
  25 Sep 09:45 (`f4ba1bb`).
- **What happened.** About 6.2 ahead of the packet, the log-lapse falls
  through the carry speed. Forward light and matter at rest within r ≈ 11
  gather there, gaining 9.6 e-folds per unit σ. Matter leaves the 12.6, 25.2
  and 37.8 trips at γ = 1e22, 1e47 and 1e72 (`FRONT_LIGHT_SURFACE_PASS.md`
  l.16–22, 159–170). The surface is a white-hole horizon disk with
  κ = 9.1–9.7 (`CONE_TIP_FIELD_PASS.md` l.16–21). Fixes: a forward shelf
  (2.1e27 kg of null deficit per metre, 1e13 M☉ per light-year) or a 15°
  conical front (peak content 198 → 333). All four fronts pass the Type I
  gate.
- **Detected by.** Tracing swept light and matter in the pattern's frame,
  with a conserved Killing energy.
- **Available since.**
  - Literature: Finazzi–Liberati–Barceló 2009; McMonigal–Lewis–O'Byrne 2012
    (both cited in the report).
  - The user's own earlier paper raised this concern (memory note
    `answer-user-comments-directly`).
  - The tool is a light-surface locator: solve α² = (β + v)² along the track,
    trivially computable from 23 Sep.
- **Counterfactual.** Locating the surface where the pattern's Killing vector
  turns null (α = b), and classifying it null or timelike (from the
  transverse gradient), costs minutes. It would have flagged the problem at
  the first superluminal choreography. Two passes (lapse staging,
  compartment) and the disclosure update were done without it.
- **Cost.** Small in time (about 2 days). The disclosure (`b53727b`) describes
  a design with this defect.
- **Candidate lesson.** For any pattern moving faster than exterior light,
  compute in the pattern's frame the surfaces where α² = b² before adopting
  the design. Each is a horizon only where its transverse gradient vanishes
  (`CONE_TIP_FIELD_PASS.md` l.61–70). Trace what the front sweeps, in
  energy, as a function of trip length.
- **Generality.** General for superluminal warp-type designs;
  literature-backed. The "transverse gradient makes the surface timelike"
  criterion is an exact identity with general use.
- **Recurrence.** n = 2 with E12 (the cone's flank trap at higher speed).

### E12. A fix tuned at one speed failed at higher speeds

- **Date / commit.** 25 Sep, `53c27fe`.
- **What happened.** "Every result so far was at a lane speed of 2.1"
  (`GEOMETRY_CLOSURE_PASS.md` l.4–5). A cone flank moves along its normal at
  v sin θ_c. Above 1/sin 15° = 3.9 light rides the flank: swept gains
  reached 3.7e6 at v = 5 and 8e11 at v = 10, and 7e19 from the compartment
  at 10 (l.29–36, 149–157, 271–273). Scaling sin θ_c = 0.54/v restores
  bounded gains (about 5v) up to v = 20.
- **Detected by.** A speed scan, the same day.
- **Counterfactual.** The normal-speed condition is a one-line derivation
  available when the cone was designed that morning. Caught within hours.
- **Candidate lesson.** Every moving surface of a pattern must advance along
  its own normal slower than local light. Test a fix across the operating
  envelope, not at the design point alone.
- **Generality.** General (kinematics of moving surfaces). Envelope testing
  is a truism; the normal-speed criterion is the domain content.
- **Recurrence.** n = 1, plus E11.

### E13. Occupant quantities were missing from the audit set

*Adds detail to P01 §2i.*

- **Date / commits.** 23–25 Sep. Compartment fix 25 Sep (`7c2a0fb`).
- **What happened.** Packet safety meant "timelike packet". Nobody checked
  the passenger clock rate, tides or proper acceleration. Peak clock rates
  were 9,069× (census design), 140× (amplitude pass) and 55× (lapse design)
  (`LAPSE_AND_STAGING_PASS.md` l.178–192). At L = 1 m, tides were
  3e16 m/s² per metre of body (`COMPARTMENT_PASS.md` l.3–8). The user called
  the 55× design a failure for crewed transit (memory
  `rail-goal-is-crewed-transit`). The fix is a region of uniform lapse and
  shift: flat by a coordinate change, with zero tides and a chosen clock
  (`COMPARTMENT_PASS.md` l.54–68).
- **Available since.** The flat interior with a free-falling passenger is a
  standard property of the Alcubierre-type bubble interior (recalled, not
  verified here). The coordinate change is two lines.
- **Counterfactual.** Adding clock rate, Riemann components across the body
  and proper acceleration to the standard audit set in May.
- **Candidate lesson.** For crewed designs, report proper-time rate, tidal
  tensor and proper acceleration of the payload with every geometry. Put the
  payload in a region where the lapse and shift are spatially uniform.
- **Generality.** General for crewed transport geometries. The compartment
  construction (uniform α and β give local Minkowski) is an identity.
- **Recurrence.** Two incidents across four designs: the 9 Sep throat lapse
  of 69–108 (B14) and the three redesign-era designs here. Peak packet clock
  rates across the window: about 108×, 9,069×, 140×, 55×, then 1× by design.

### E14. Reduced-dimension audits missed the lapse cavity

- **Date / commit.** 25 Sep, `53c27fe`.
- **What happened.** Three-dimensional ray tracing found that the compartment
  is a lapse cavity. Light escapes during the carry only within
  arcsin(α_c/α_max): 1.05° at 2.1c and 0.22° at 10c. About 98% of radiated
  heat stays inside until arrival (`GEOMETRY_CLOSURE_PASS.md` l.46–55,
  205–224). Earlier escape audits traced radial or axial rays on a 1D
  ledger and reported "radial escape complete".
- **Candidate lesson.** Run optical audits in full dimension. A refractive
  index 1/α with a large contrast traps light by total internal reflection,
  which radial or axial rays cannot see.
- **Generality.** The refractive-index reading of a static lapse in the
  pattern's frame is exact and general.
- **Recurrence.** Part of the reduced-model blind-spot cluster (E6): n = 3.

### E15. The in-principle exclusion of quantum sources came last

- **Date / commits.** 25 Sep 17:47 (`e744879`, `ANEC_MAP_PASS.md`). The
  deferred-gate list dates from 20 May.
- **What happened.** The first light from the departure is achronal and
  carries negative ANEC: −0.0012 on the test trip, −202 on a lane ending at
  σ = 30 (l.13–31). "Any lead over exterior light" requires this (l.41–42).
  Achronal ANEC holds for quantum fields in flat space (FLPW 2016, HKT 2017),
  in curved space for free fields at small curvature (Kontou–Olum 2015), and
  as the proposed self-consistent condition (Graham–Olum 2007). So "A
  semiclassical quantum sector therefore supplies none of this demand, at any
  size" (l.42–51). Eleven hours earlier, the scaling test's magnitude result
  (quantum fields up to L ≈ 0.45 mm) had been written into the disclosure
  (`b53727b`). It still reads "Quantum fields supply it at sub-millimetre
  unit lengths" (`active_rail_technical_disclosure.tex` l.573; also l.401,
  l.468).
- **When it could have been known.**
  - 20 May: `STAGE2_ENDPOINT_JUNCTION_SOURCE_MILESTONE.md` l.268–275 listed
    "quantum inequality / ANEC-style endpoint cost: not shown" and "curvature
    or trans-Planckian scale control: not shown" as unpassed physical-source
    gates. The Ford–Roman (1996) wormhole constraint is in the repo's
    references (`SOURCE_SCALING_TEST.md` l.361–362).
  - From 23 Sep (the first lead over exterior light), the achronal ANEC
    argument applied directly.
- **Counterfactual.** For the one-space FTL design, an hour of literature
  work on 23 Sep. For the throat design the case is weaker: a two-ended
  geometry without an exterior comparison path is not a "lead over exterior
  light", and quantum-supported traversable wormholes are discussed in the
  literature. Treat this counterfactual as strong only for designs claiming
  a lead over exterior light.
- **Cost.** Every quantum-source branch from 8–17 Sep targeted a sector
  that achronal ANEC (if it holds in the relevant regime) excludes for any
  FTL rail: Casimir supports, moving quantum boundaries, spherical quantum
  boundaries, condensate vacuum stress, the semiclassical opening, and the C1
  radial and angular quantum channels (about 58 million fields). Caveats:
  those branches were run on the two-ended throat, and achronal ANEC in
  strongly curved spacetime remains conjectural.
- **Candidate lesson.** Order source-family screening by the reach of the
  exclusion. First apply in-principle theorems that decide a whole class
  (achronal ANEC for any lead over exterior light; quantum inequalities with
  the species bound for scale). Then do magnitude estimates, then
  constructions. The May list had the right gates, and they came last.
- **Generality.** General for superluminal and shortcut designs. The
  literature supports it, with a regime caveat.
- **Recurrence.** Deferred decisive checks, from the May "not shown" list: QI
  scale (computed 25 Sep 00:40), ANEC (25 Sep 17:47), trans-Planckian or
  curvature coupling (25 Sep, F → 0 at r ≈ 10.65). n = 3 from one list. The
  species bound, which would have ended the C1 multiplicity route on 17 Sep
  (D9), belongs to the same deferred set.

### E16. Premature locking of the design record

- **Date / commits.**
  1. `921e560` (9 Sep 16:59), removed `734156c` (20:31).
  2. `2146526` (23 Sep 14:07): constant-radius two-ended track as "the
     representative disclosed geometry"; superseded by one space at 17:39.
  3. `b53727b` (25 Sep 00:41): one-space lapse-staged rail with quantum fields
     "below 0.45 mm". Superseded the same day by the compartment (07:10),
     the conical front (09:45) and the ANEC exclusion (17:47). The user had
     not authorized this update (memory `disclosure-updates-need-explicit-go-ahead`:
     "The user then asked where they had said to update the disclosure; they
     had not").
- **Candidate lesson.** Lock a design record only after the checks that can
  eliminate the design class have run: topology and global structure,
  in-principle source theorems, occupant quantities, swept-matter and horizon
  checks. Those checks were cheap here and came after each lock.
- **Generality.** Process. For the book, at most one sentence supporting the
  ordering in E15.
- **Recurrence.** n = 3.

### E17. Numerical diagnostics at degenerate or near-vacuum points

- **Instances.**
  1. The legacy classifier's absolute 1e-12 tolerance and branch error (A1).
  2. The 4D finite-difference kernel labelled 17 of 129 witnesses Type IV on
     a geometry whose radial block is exactly Type I. Truncation residuals of
     ρ + p_ℓ and j_ℓ carried the sign, while the discriminant fell 16× per
     halving (`CONSTANT_RADIUS_TRACK.md` l.199–207). An exact warped-product
     evaluator settled it.
  3. Caustic-like bundle flags came from an initial areal-radius spread of
     2.2e-16, one rounding unit on a constant radius
     (`CONSTANT_RADIUS_TRACK.md` l.258–263; `RESET_SCHEDULE_OPTIONS.md`
     l.136–141).
  4. Bundle "crossings" (193 and 202 samples) appeared at the default step,
     though rays of one family obey a first-order ODE and cannot cross; they
     vanished at 0.1 spacing (`CHOREOGRAPHY_PASS.md` l.152–158).
  5. Source rest-frame velocities were read at points below the
     classification noise floor (`f7edf6b`, 24 Sep).
  A positive counterpart: the quantum-estimates draft had dropped the Weyl
  term from the anomaly formula. It was replaced before the run and tested
  against the Christensen–Fulling Ricci-flat limit (`19a367a`;
  `QUANTUM_ESTIMATES_PASS.md` l.42–56).
- **Candidate lesson.** Engineered demands sit on degenerate tensors (string
  clouds, exact zeros, repeated eigenvalues). Classification and derived
  frames there need exact or analytic evaluators, scale-aware tolerances and
  a noise floor. Invariants (ordering of rays in one family, exact zeros)
  are free tests of numerical artifacts. Test every formula against its known
  limits before use.
- **Generality.** General.
- **Recurrence.** n = 5 artifacts plus 1 early catch.
