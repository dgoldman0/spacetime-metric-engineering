# Incident inventory, 8–25 September 2026

> **Errata (audit 2026-09-26, `../audit_synthesis.md` §5).**
> - A1: the preflight fixture set is vacuum plus six tensor families at three amplitudes (19 fixtures), not '7 × 3 = 19' (`LE_BOUNDARY_GATE_PREFLIGHT.md` l.43–53).
> - A9 'Mechanism': the affirmative-language and no-running-log rules entered AGENTS.md on 16 Sep (`e7a9951`), seven days after `734156c` (9 Sep). The removal fits their intent, but the causal link to written rules is an inference (audit §2 #13).


**Purpose.** This is evidence for vetting candidate practices for a textbook on
spacetime (metric) engineering. It is not a project history and not book
text. An *incident* is an event where a check, result or finding changed a
decision. Each entry records:
- date and commit;
- what happened, with numbers;
- what detected it;
- when the detector or the knowledge became available;
- the counterfactual;
- the cost;
- the candidate general lesson;
- its generality;
- recurrence.

**Relation to P01.** `../vetting/P01_classify_demand_before_sources.md` already
covers these incidents:
- the 8 Sep Type IV finding;
- the legacy classifier failures;
- 9–17 Sep static-surrogate source work in outline;
- node-sampling bands (amplitude pass);
- the 74,700 Type IV points of the first one-space boundary layer;
- the e⁴ plateau and 55× clock.
Entries here that touch those incidents add detail or recurrence counts and
say so.

**Sources and method.**
- **Repository.** `/media/projectspace/active-rail-refined-design-base`, read
  only. All citations refer to the committed state, HEAD `19a367a` (25 Sep
  21:02) or the named earlier commit. On 26 Sep, `git diff HEAD` is empty for
  every cited document (`supporting_reports/*.md`, `plan.md`, `README.md`,
  `AGENTS.md`, the gate handoff, the disclosure `.tex`), so their line numbers
  are HEAD line numbers. Another session's uncommitted work (a
  deficit-minimization pass; edits to `compartment_service.py`,
  `front_surface.py`) is outside the window and is not cited. Report paths are
  relative to `supporting_reports/` unless given in full. Commit times are
  local (−0400).
- **Who read what.** Parts A (the Le ladder, 8 Sep) and E (the redesign,
  23–25 Sep) are my own reading. Parts B, C and D condense three delegated
  read-only surveys: `work/block_sep08_09.md`, `work/block_sep10_12.md` and
  `work/block_sep16_17.md` hold the full notes with every citation. I
  spot-checked their decisive numbers and quotes against the reports, and
  all checks matched.
- **Arithmetic not in the record.** Marked "agent's arithmetic" or
  "derived". Two cases: the species-length check in D9, and the Schwinger
  field at the recorded normalization in D7.
- **Literature.** Cited only where the repository cites it, unless marked
  "recalled, not verified here".
- **User corrections.** Taken from the repository (R), inferred from reversals
  (I), or from the user's memory files outside the repository (M); see Part G.

**Scale of the window.**
- **8 Sep:** 26 commits (the ladder).
- **9–17 Sep:** 183 commits and about 100 new reports: source families,
  source plant and C1.
- **18–22 Sep:** no commits.
- **23–25 Sep:** 30 commits and 16 reports. The redesign took the design from
  the failed beta075 geometry to a closed, gate-passing prescribed geometry
  with a flat passenger compartment and a narrowed source class.

**How to read the parts.**
- A: the Le gate and its repair ladder (stopping-rule evidence).
- B–D: the source-plant period.
- E: the redesign.
- F: counter-evidence.
- G: user corrections.
- H: recurring lessons with counts.
- Closing table: one row per incident.

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
- **Recurrence.** Complete-ledger failures across the window: A2, C7, C8, C9,
  D3 (L14, n = 5). P01 §2b makes the related point that component types are
  diagnostics of a split.

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
    commits after the 5.8e7-field result (Part F, F14; `work/block_sep16_17.md`,
    counter-evidence F).
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

## Part B. Source families on the static background (8 September evening – 9 September)

Scope: 56 commits, `cc5e253` (8 Sep 20:46) to `8492f8e` (9 Sep 21:21). About 16
source families were opened and closed in about 25 wall-clock hours. From
`1069413` (9 Sep 09:00), 37 of these commits ran on a complete two-ended
*static* background at phase 0.745. Fuller notes with every citation are in
`work/block_sep08_09.md`; this part condenses them. I spot-checked the key
numbers against the reports.

### B1. An exact inverse stress fit cancels gravity's own kinetic term

- **Date / commits.** 8 Sep, `cc5e253`, `0cc3f79`, `275edbc`.
- **What happened.** A rate-quadratic Comer–Andersson action was fitted to
  supply the missing early angular stress. The fit forces
  (8πa, 8πb) = (1, −1), so the tensor kinetic ratio is K_TT = 1 + 8πb = 0. All
  12 least-squares fits land there, with residual 8.5e-15, and all 72
  registered evaluations fail. The thermal preload needed to carry the current
  costs 6.2e6–6.5e8 in mass, which drives the minimum f to between −2e6 and
  −2e8. The cause is a lapse contrast of about 78 raised to the Tolman power 4
  (`COMER_ANDERSSON_SPHERICAL_STARTUP_ATTEMPT.md` l.144–156, 214–241, 263–273).
- **Detected by / available since.** The report's own analytic derivation.
  Both failures follow on paper: the fitted Q cancels the ADM kinetic
  density, and 78⁴ ≈ 3.7e7.
- **Counterfactual.** Minutes on paper. The 72-run grid only confirmed it.
  Cost: 3 commits, about 8 minutes.
- **Candidate lesson.** A matter model fitted to reproduce the principal
  (second-time-derivative) part of G/8π subtracts gravity's kinetic term and
  leaves a degenerate principal symbol. Check a source's contribution to the
  principal part, and its mass price, before fitting its stress values.
- **Generality.** General for inverse ("fit T to G/8π") constitutive design
  with velocity-dependent sources. Known in modified-gravity well-posedness
  work.
- **Recurrence.** n = 2 in the block ("an exact algebraic fit is not
  admissible dynamics"; also the elastic-vacuum ghost in B2).

### B2. NEC-satisfying sectors cannot pay a negative-enthalpy demand: rediscovered family by family

- **Date / commits.** 8 Sep 21:12 to 9 Sep 20:23: `96f0459`, `1a4c988`,
  `1edb374`, `7512231`/`868b938`, `56aa116`, `92b997b`, `f4227ff`, `aa7408f`.
- **What happened.** The demand has ρ + p_r < 0 at all 2,049 sampled radii
  (`QUANTUM_MOVING_BOUNDARY_ATTEMPT.md` l.271–273). Eight families each closed
  on the same sign fact:
  - Comer two-current support contributes 0, and its fluids a positive amount
    (`COMER_TWO_CURRENT_EVOLUTION_ROUND.md` l.284–299). The report says this
    holds "already at zero preload", yet 12 evolutions and a 1,024-cell
    refinement ran first.
  - An elastic vacuum support has time kinetic coefficient K_r = e + p_r < 0 at
    every radius, a ghost. The construction cites Dubovsky et al., whose main
    result is exactly this (`VACUUM_SUPPORT_SELECTION_ROUNDS.md` l.186,
    215–218, 258–276).
  - The planar vacuum's angular E + P⊥ = 0.
  - The condensate has ρ + p_r = 2(K + D) ≥ 0.
  - Filling every confined-fermion multiplet gives −0.0045 to −1.10 against a
    required +2.0.
  - Cavity mirrors give a net −0.20 at g = 10.
  - Magnetic bends have ρ + p_r = B²(1 − t_r²)/e² ≥ 0.
- **Detected by.** A short sign argument inside each report.
- **Available since.** The start of the block. A sum of NEC-satisfying tensors
  satisfies NEC.
- **Counterfactual.** A block-level null-energy budget would have scored five
  of these families on paper. Cost: about 8 rounds, about 20 commits, partly
  justified by other aims.
- **Candidate lesson.** The null deficit is a budget that only the exotic
  sector can pay. Every ordinary component, including the holders, mirrors
  and confinement the exotic sector needs, adds to the bill. Score candidates
  by net null contribution, supports included, first.
- **Generality.** A truism once stated, and universal for NEC-violating
  designs. The operational content is counting the exotic sector's own
  supports.
- **Recurrence.** About 8 in this block. With C4 (four more on 10–12 Sep), the
  lesson recurs about 12 times in the window.

### B3. Casimir cells with ordinary holders are net positive: known, then re-derived

- **Date / commits.** `a91c04d`/`5cbbbf1` (8 Sep 21:34); `8987ffa`/`8d1bb32`
  (22:05–22:12); `26728fa`/`1edb374` (9 Sep 08:26–08:36); `ebe80b0` (17:51).
- **What happened.** At 21:34 the vacuum round already applied the
  Costa–Matsas bound. DEC holding matter carries at least 3C, so a complete
  cell has at least 2C per cavity volume (`VACUUM_SUPPORT_SELECTION_ROUNDS.md`
  l.86–92). The same conclusion was then re-derived three times:
  - a moving-boundary bound with minimum complete energy 8.498;
  - a matched-mass bound with holding/binding ratio 1.0014–2.9994 over 154
    pairs (`RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md` l.5–11, 99–146);
  - a reorientation "mechanical realization gate" failure.
- **Counterfactual.** The rail-level verdict was fixed at 21:34. Cost: about
  5 commits and 2 reports whose rail conclusion was already known.
- **Candidate lesson.** Treat "complete cell energy ≥ 0 under DEC holding" as a
  prior gate for any Casimir-based source.
- **Generality.** General, and literature-backed (Costa–Matsas, cited in the
  repo).
- **Recurrence.** Four derivations in the block, then the idea's return on
  24 Sep and its refutation on 25 Sep (E10): n = 5 derivations or encounters
  of the same fact.

### B4. Idealized boundaries and joins give regulator-dependent or divergent quantum stress

- **Date / commits.** `8d1bb32` (8 Sep 22:12); `1069413`–`d2a7da6` (9 Sep
  09:00–09:37); `b040588` (14:31).
- **What happened.**
  - (a) Gaussian walls: free-subtracted local densities do not converge. The
    one-wall dressing runs 5.10 → 13.77 as the cutoff rises, and the centre
    energy changes sign, −0.197 → +0.054 (`QUANTUM_MOVING_BOUNDARY_ATTEMPT.md`
    l.225–246). The missing overlap counterterm is identified later.
  - (b) Ideal delta sheets: a curved search with 159,705 radial nodes and 129
    harmonics was followed by the finding that the pressure diverges as
    λ/(48π²d³) at the sheet. The branch stopped (`CURVED_QUANTUM_BOUNDARY_SEARCH.md`
    l.169–172; `SPHERICAL_BOUNDARY_MATERIAL_CLOSURE.md` l.104–156).
  - (c) A classical C¹ join: its curvature step gives a one-sided d⁻² vacuum
    energy against a finite requirement (`CONDENSATE_SUPPLIED_QUANTUM_STRESS.md`
    l.54–112).
- **Available since.** All three were available, with Deutsch–Candelas,
  Graham et al. and Milton et al. cited in the block. Graham was cited at
  08:36, before the sheet search began at 09:00.
- **Cost.** About 7 commits; two backgrounds abandoned.
- **Candidate lesson.** ⟨T_ab⟩ is only as regular as the background and the
  boundaries:
  - delta mirrors diverge as d⁻³;
  - curvature steps diverge as d⁻²;
  - Israel (C¹) matching is sufficient classically and insufficient
    semiclassically.
  Use smooth backgrounds and finite-thickness boundaries before inserting
  ⟨T⟩ into the field equations.
- **Generality.** General and textbook. It pairs with A3 (C∞ primitives): the
  semiclassical case strengthens the smoothness requirement.
- **Recurrence.** n = 3 in the block; with A3, n = 4 smoothness incidents.

### B5. The Israel junction demanded a compressed shell, which buckles; a patch chain followed

- **Date / commits.** The requirement was visible at `d2a7da6` (09:37) and
  detected at `361d406` (10:15). Patches followed at `3c1431e`/`2ef33bc` and
  `c04cc31`/`cdde39c` (to 11:41).
- **What happened.** The enclosing junction needs positive tangential surface
  pressure (P = +4.5e-4). A trapped-fermion wall supplying it has ω² ∝ −(P/Σ)k²,
  with an e-folding time of 1.30. Stiffness is negative in all 1,029 rows, and
  P > 0 holds for the whole branch (`SMOOTH_QUANTUM_MATERIAL_ATTEMPT.md`
  l.149–153, 215–264).
  - The screening-cloud patch saturates, with an analytic ceiling outside the
    thin-cloud regime; all 1,040 cases are negative
    (`SCREENED_CHARGED_WALL_RESPONSE.md` l.155–181, 227–236).
  - The gravitating-atmosphere patch makes the wall tensile, but the cloud's
    relaxation exceeds the tension by at least 4.1×
    (`GRAVITATING_SCREENING_ATMOSPHERE.md` l.124–143, 231–264).
- **Available since.** Yes: membrane buckling under compression, and Israel
  thin-shell dynamics (cited at `d2a7da6`).
- **Cost.** About 6 commits, 3 reports and 2 hours.
- **Candidate lesson.** Read the sign of the surface stress the junction
  demands before choosing a shell material. Compression needs an independently
  counted restoring response, and patches that add one carry their own loads.
- **Generality.** General for thin-shell constructions (wormhole, gravastar
  and bubble shells). Textbook physics.
- **Recurrence.** n = 3 (smooth wall, screened wall, atmosphere).

### B6. A one-sided shooting blow-up was reported as a physical obstruction

- **Date / commits.** `d7e6cdd`/`7512231` (9 Sep 12:23–12:36), then
  `6fa75d7`/`b4bd0a9`, then `4188ad3` (14:05).
- **What happened.** Integrating the condensate inward from exterior data
  produced a pole near areal radius 4.2925, matching the asymptote
  h ≈ √(2/μ)/(Bv(x* − x)) to 0.02%. Sixteen robustness checks reproduced it:
  two integrators, tolerances, thresholds and geometries. The headline reads
  "failing the regular stationary material continuation"
  (`SCREENED_SCALAR_CONDENSATE.md` l.3, 156–187). Ninety minutes later, a
  global boundary-value problem found two regular branches
  (`CONDENSATE_JOINT_CONTINUATION.md` l.53–85). The fixed exterior value
  p_r,R = −0.125 had forced the singularity (`CONDENSATE_JOINT_SELECTION_DIRECTION.md`
  l.59–72).
- **Available since.** Yes. Movable singularities of h″ ~ ch³ under one-sided
  integration are textbook ODE behaviour.
- **Cost.** About 3 commits. The superseded headline stays at the top of the
  report, with only a forward link appended.
- **Candidate lesson.** A finite-radius blow-up in one-sided integration of a
  nonlinear field equation usually signals mis-specified boundary data. A
  no-go claim needs a global boundary-value formulation or an analytic
  argument.
- **Generality.** General for soliton, boson-star and shell matching.
- **Recurrence.** n = 1. It is also counter-evidence: 16 robustness checks
  certified a formulation artifact (F-list).

### B7. Magnitude was deferred behind sign-only screening; the first normalized comparison fell short by about 10⁵

- **Date / commits.** Sign-only work ran from `a91c04d` (8 Sep 21:34) to
  `d2a7da6` (9 Sep 09:37). The first magnitudes came at `b040588` (14:31) and
  `b040b9b`/`cf87a89` (15:13–15:36).
- **What happened.** Reports stated explicitly that the comparison "uses
  signs, independently of any conversion between the cavity units and the
  rail's curvature scale" (`QUANTUM_MOVING_BOUNDARY_ATTEMPT.md` l.275–276).
  - The first magnitude result: the absolute renormalized vacuum supplies
    5.0e-6 to 5.4e-6 of the required opening balance B = 2.1766. The final
    required-to-available ratios are 185,950 and 203,502, and the signed
    balance opposes opening (`SEMICLASSICAL_JOINT_INVESTIGATION.md` l.102–121).
  - The normalization η = 2.41e-5 came out of material matching. It sets one
    rail unit at about 204 ℓ_P and the throat at R₀/√η = 415 Planck lengths,
    noted only in passing (`LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md` l.232).
- **Available since.** Yes. The (ℓ_P/L)² scaling was written down at 09:36.
  Ford–Roman-type quantum-inequality bounds are standard. May's gate list had
  "quantum inequality / ANEC-style endpoint cost: not shown"
  (`STAGE2_ENDPOINT_JUNCTION_SOURCE_MILESTONE.md` l.274).
- **Counterfactual.** A one-line estimate on 8 Sep evening would have re-scoped
  the quantum chain to "Planck-scale or large-N only": η times a loop factor
  per field against an O(1) opening demand.
- **Cost.** The largest in the block: about 30 commits and 18 reports in about
  24 hours. The workflow gained a normalized-first rule only on 17 Sep
  (`1e9ac1d`; Part D).
- **Candidate lesson.** For any semiclassical source, compute the physically
  normalized magnitude first: (ℓ_P/L)² × loop factor × species count, against
  the demand at the intended size. Signs, placement and stability come after.
- **Generality.** General and textbook. It generalizes as the scaling test
  did on 25 Sep (E15).
- **Recurrence.** About 5 magnitude gaps in the block:
  - optical, ≤ 1e-6;
  - absolute vacuum, 5e-6;
  - longitudinal loops, ≤ 4.17%;
  - cavity crossing coupling g* ≈ 17,000;
  - magnetic loops, N_f e²/16π² ≈ 18 against 0.1.

### B8. Bulk tension was assigned to the quantum sector

- **Date / commits.** `4188ad3`–`cf87a89` (implicit), caught at `ada8661`
  (16:18) and `0e66f43`.
- **What happened.** At the throat the demand is (ρ, p_r, p_t) =
  (9.564e-3, −9.565e-3, 3.26e-5). The condensate carried 0.612% of the tension
  and the "quantum remainder" 99.388%, although the null part is only
  ρ + p_r = −1.36e-6 (`COUPLED_SOURCE_ROLE_AUDIT.md` l.7–12, 58–63). After
  reallocation, a backbone carries 95% of the tension and the quantum radial
  weight becomes 3.4e-7 (`COUPLED_REORIENTATION_INVESTIGATION.md` l.72–86).
  The opening-deficit verdict was independent of the allocation.
- **Candidate lesson.** Split the demand into bulk tension (ρ ≈ −p, NEC-neutral,
  carried by strings, flux or potential energy) and the signed null deficit
  (the exotic part). Allocate each before solving any fields.
- **Generality.** A standard decomposition (Morris–Thorne "exoticity"). It is
  general, and the constant-radius track later made the split exact (E1).
- **Recurrence.** n = 1.

### B9. The surrogate's exterior is an Ellis tail, so the null demand runs along the route

- **Date / commit.** `ada8661` (9 Sep 16:18).
- **What happened.** 96.69% of the negative radial-null balance B₋ = 2.325
  lies outside |x| ≤ 2, with 28.77% in 3 ≤ |x| ≤ 40. "That tail itself requires
  negative radial null stress" (`COUPLED_SOURCE_ROLE_AUDIT.md` l.160–184).
  The morning's source-localization work was trying to terminate an
  ultrastatic wormhole tail: the enclosing sheet at R = 6.8, the Schwarzschild
  exterior junction and the atmosphere.
- **Lesson and counterfactual.** See E5 (topology). This is its 9 Sep data
  point.

### B10. The zero-shift static surrogate: the scope error was recognized on 9 Sep and did not stick

*Fine grain for P01's "static-surrogate source work".*

- **Date / commits.** Background `1069413` (9 Sep 09:00); scope correction
  `a1a8a65` (20:46); first active-metric test `bad59e2`/`8492f8e` (21:10–21:21).
- **What happened.**
  - The scope review names the error: "The scope error was promoting these
    conditional source results into necessary active-rail selection gates
    without demonstrating the state equivalence. Local scope qualifications
    were already present in several reports. The later recommendations
    exceeded them" (`ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md` l.165–167).
  - About 35 minutes of active-metric work found the Type IV witnesses in all
    9 timing schedules, and a transfer-routing obstruction. The characteristic
    speeds v± = −β ± α/B carry the required reservoir radiation through the
    protected packet, with in-packet density ≥ 1.0754
    (`ACTIVE_ENDPOINT_TRANSFER_INVESTIGATION.md` l.61–67, 127–135, 153–192).
  - 10–17 Sep did not act on the verdict. The 10–12 Sep endpoint-patch reports
    keep the active metric's shift, but none cites the Type IV verdict (Part C
    overview). The 17 Sep C1 work used "the static, zero-shift surrogate of the
    archived phase-0.745" (`C1_FINITE_MODULE_PAIR_SCREEN.md` l.25).
- **Candidate lesson.** Before adopting a simplified background, list the
  obstruction classes it can and cannot represent. A correction recorded in a
  report does not constrain later work unless it enters the standing plan (A9).
- **Recurrence.** Correction not propagated: A9 and this: n = 2.

### B11. Helpful and parasitic terms share one length scaling, so reshaping cannot help

- **Date / commits.** `e3c17ae`, `aa7408f`, `e2dc588`/`92b997b`,
  `283a91e`/`f4227ff` (9 Sep 15:58–20:23).
- **What happened.**
  - Long conformal loops need L_opt < 3.27 for a helpful sign, but the loop has
    6.30. With clock freedom the best case reaches ≤ 4.17%.
  - For cavities, the interaction and the mirror gradient load both scale as
    η/a³. The crossing coupling is g* ≈ 11,000–24,000 against g ≤ 10, and a
    sixteenfold gap reduction gains only 1.67×
    (`NARROW_CURVED_CAVITY_EVALUATION.md` l.80–162).
  - Magnetic loops need N_f e²/16π² > 18 against a perturbative 0.1; 0 of
    23,760 cases pass (`SHORT_MAGNETIC_CIRCUIT_EVALUATION.md` l.143–196).
- **Candidate lesson.** When helpful and holding terms scale alike with size,
  the verdict is a dimensionless coupling threshold. Compute it first; if it
  is non-perturbative, stop.
- **Generality.** A general rule of thumb for Casimir, flux-tube and mirror
  sources.
- **Recurrence.** n = 3–4.

### B12. A redundant recommendation, corrected within 15 minutes; an archive re-screen that was predictably null

- **Date / commits.** `aa7408f` (18:02), replaced at `83fe023` (18:17);
  re-screen `d9b93df`/`fe99e3f`.
- **What happened.** The history report says: "The previous recommendation to
  select the operational constraints before proceeding repeated work already
  established in the design record" (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md`
  l.17–20). The 13 archived controls then moved the demand by at most
  +0.315% against a gap of 10⁵ (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md`
  l.5–13, 132–162). Probably a user correction; the record does not quote the
  user.
- **Candidate lesson.** Search the project archive before proposing
  exploration, and compare plausible effect size with the gap before
  re-screening.
- **Generality.** A research-process near-truism.
- **Recurrence.** Knowledge in the record not applied: n = 5 with A9.

### B13. The technical disclosure used as a running log for 3.5 hours, then stripped

- **Date / commits.** `921e560` (16:59, +179/−51 lines) plus four small
  additions; removed at `734156c` (20:31). The PDF was rebuilt 6 times.
- **Note.** The same removal also erased the Le verdict (A9). Premature locking
  recurs: E16.

### B14. The lapse hill at the packet (A up to about 108) was never read as passenger aging

- **Date / commits.** `ada8661` (A₀ = 69.34), `fe99e3f` (81.7–88.5), `bce06d7`
  (maximum 108.07).
- **What happened.**
  - (a) The lapse profile rules out free binding of massive fields, since
    Weinbaum's bound-state condition needs an attractive lapse well. Fermions
    therefore need material confinement (`SOURCE_CONSTRUCTION_RESTART_SHORTLIST.md`
    l.70–77). The same commit also qualified the Kain EDM benchmarks cited
    three hours earlier.
  - (b) A payload at a lapse of 69–108 ages 70–110× faster than exterior
    clocks. No report in the block interprets this.
- **Cross-reference.** Adds a fourth design to E13. Peak clock rates across the
  window: about 108× (throat, 9 Sep), 9,069× (census), 140× (amplitude), 55×
  (lapse design).

### B15. Checks that caught method errors early

- (a) Coarse-resolution Type IV artifacts: 138 raw complex-pair records
  appeared only at coarse settings. The discriminant ran −6.9e-9 → +2.1e-10 at
  1,024 cells, and all 36 finest witnesses are Type I
  (`COMER_TWO_CURRENT_EVOLUTION_ROUND.md` l.244–270). This is the mirror image
  of E8: coarse grids can create Type IV as well as miss it.
- (b) Truncated gradient expansion: extrapolating the quartic bending term
  beyond ka ~ 1 would have given 72 false passes of 420; the saturating law
  gives 0.
- (c) Precision loss at release was replaced by an analytic divided
  difference 2 minutes after introduction.
- (d) Default CSV float parsing broke near-cancellation audits; the fix was
  exact round-trip reading (recurs 3 times).
- (e) An unresolved quadrature (162 against 39,023) was kept out of the
  verdict.
- (f) A renormalization claim was corrected in the text (`b040b9b`).

## Part C. Endpoint storage, capacitors, joints and virtual radial cells (10 and 12 September)

Scope: 90 commits, `f562930` (10 Sep 05:10) to `75360cd` (12 Sep 21:15), 26
reports; there are no commits on 11 Sep. All 26 reports work on the late,
non-live endpoint patch x ∈ [−2.1, −0.5], s ∈ [0, 1.285], with the active
metric's shift kept. None mentions the Hawking–Ellis classification or Type
IV (0 grep hits). Ten defer the negative-null remainder to an unspecified
"independently supplied negative-stress sector" or "quantum source". Fuller
notes: `work/block_sep10_12.md`.

### C1. Numerical temperature floors misread as physical heat depletion

- **Date / commits.** 10 Sep: `f562930`/`38ea61b`, `9f1429c`/`a107821`/`56e6b8d`,
  `148b5eb`.
- **What happened.**
  - Zero-exchange elastic controls lost temperature although the adiabatic law
    conserves heat: "a numerical limitation"
    (`ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md` l.141–147).
  - In the EM storage runs, the ideal control drove an element to zero heat.
    "Global conservation of the combined tensor leaves that internal-energy
    error undetected". A stop time converging between 256 and 512 cells still
    carried a heat discrepancy of 0.141 against an initial 0.261: "Convergence
    of a stopping time alone would therefore give an incorrect impression of a
    physical limit" (`ELECTROMAGNETIC_ENDPOINT_STORAGE_INVESTIGATION.md`
    l.196–218).
  - Three of five conductor runs stopped at a primitive-inversion limit inside
    the analytic causal boundary (`ACTIVE_RESERVOIR_CAUSAL_TRANSPORT.md`
    l.259–266).
- **Detected by.** Source-free controls and independent heat audits, run in the
  first round. This is largely a check that caught a problem early.
- **Candidate lesson.** Run a source-free control that the continuum law says
  conserves the quantity at issue. Classify every stop as numerical or
  physical before interpreting it. A converging event time does not show that
  the event is physical.
- **Generality.** General for numerical source modelling. The dual-energy
  problem is textbook in computational fluid dynamics; the "converged stop
  time" trap is worth teaching.
- **Recurrence.** n = 3.

### C2. A conservation error normalized to the wrong budget

- **Date / commit.** `8880934`.
- **What happened.** The energy error was about 0.5 against a total of 34,700
  (1.4e-5 relative), while the decisive local heats are about 0.25. The
  material-wave CFL limit, not the step cap, was controlling: a Courant
  factor of 0.2 → 0.05 cut the error about 60×. Going from 64 to 128 cells
  changed density by 55.5% and stress by 47.6%, with 97.6–99.6% of the squared
  error in steepening end fronts (`ACTIVE_RESERVOIR_ENSEMBLE_REFINEMENT.md`
  l.183–205, 376–379).
- **Candidate lesson.** State conservation errors relative to the smallest
  budget that decides pass or fail, and check which step restriction is
  active.
- **Generality.** General numerics; textbook.
- **Recurrence.** n = 2.

### C3. Treating heat symptoms of a kinematic cause (γ ≈ 47); redirected by the user

- **Date / commits.** Chain `9f1429c` → `4f3eb03`; redirect `6b6433b`–`aa22156`.
- **What happened.** Three reports added heat supply to a depleting element:
  EM storage, strain relaxation and conduction. The element moved at
  v = −0.9995 with n_eff = 1.05e-3, and q̇ = αR²(−P + vF)/(A n_eff) made the
  1/n_eff factor explicit. Conversion replaced 0.91% of the withdrawal, and the
  best conductor kept 0.153% (`ACTIVE_RESERVOIR_ENSEMBLE_REFINEMENT.md`
  l.344–364; `ACTIVE_RESERVOIR_CAUSAL_TRANSPORT.md` l.7, 289–356). The
  prestressed study then recorded "the user's material-velocity concern" and
  a Lorentz factor "near 47". It found that the speed "depends strongly on the
  tested mechanical construction" (`PRESTRESSED_BUFFER_VELOCITY_INVESTIGATION.md`
  l.13–14, 174, 237, 340–342).
- **Counterfactual.** A γ and dilution column in the first run; speeds of 0.93
  and 0.97 were already tabulated.
- **Cost.** About 8–10 commits, 3 reports and 2.5 hours.
- **Candidate lesson.** When a demanded exchange tensor is forced one way onto
  trial matter, check the receiving matter's kinematics (γ, dilution, causal
  access) before adding stores or conductors.
- **Generality.** Any one-way forcing of a demanded tensor onto trial matter.
- **Recurrence.** n = 1 chain. The user correction is visible in the record.

### C4. The null-projection screen ran after the dynamics; the user set the reservoir aside

- **Date / commits.** `a60432b`/`21b98b9`, `2cd4244` (10 Sep 09:16–09:34).
- **What happened.** The required negative radial-null contribution was 14.21
  at startup, about 3,248× the geometric value, and 75.78 at fade. Optimizing
  the preload cut it only 23%. An exact identity ties it to buffer inertia and
  motion: max S_kk = w_b/(1 − c_f²)·(1 + |v|)/(1 − |v|)
  (`RESERVOIR_FEASIBILITY_ENVELOPE.md` l.139–148, 180–215). "The user has set
  this assembly aside from the active search" (l.257–260).
- **Counterfactual.** One null-projection evaluation of the proposed reservoir
  tensor before registering any dynamics. That was 20 commits and 4.3 hours
  earlier.
- **Cost.** Phase A: about 20 commits and 6 reports.
- **Candidate lesson.** Screen each support component by its null projections,
  including the Doppler weight (1 + |v|)/(1 − |v|) of its bulk motion, before
  designing its dynamics.
- **Recurrence.** n = 4 here. With B2, about 12 in the window. See H-list
  lesson L3.

### C5. Solver statuses read as physics: HiGHS dropped small metric coefficients

- **Date / commits.** `1b70929` (10 Sep); `c05aa05`, `5dc7ce4` (12 Sep).
- **What happened.** A heat-engine control was reported infeasible, although
  its feasible set contains an accepted history (residual 9.45e-9). "HiGHS
  deletes coefficients at or below 1e-9 by default", and small shift
  coefficients multiply large stores. With the threshold at 1e-12 the
  control became feasible (`PRESSURE_LINKED_STORAGE_COMPLETION.md` l.223–252).
  Later, a native state marked valid violated the original rows by 0.51 and
  7.91. The fix went forward only: `graded_electrothermal.py` l.142–145 still
  uses defaults, and the earlier GRADED runs were not repeated. Practice
  improved within the block, with exact rational Farkas certificates by
  12 Sep.
- **Candidate lesson.** Metric data are badly scaled: tiny lapse or shift
  derivatives multiply large stores. Never read solver statuses as physics.
  Check nested-relaxation consistency and the original rows, and require
  certificates for infeasibility.
- **Generality.** General for optimization-based source design.
- **Recurrence.** n = 4.

### C6. Stores must hold energy comparable to their own rest energy

- **Date / commits.** `64006ae`, `7416b33` (10 Sep); `5e59da3`, `75360cd`
  (12 Sep).
- **What happened.**
  - The capacitor benchmark carries 3.4e12 units of rest energy per unit
    stored, so its necessary negative null is 1.9e11 against 0.104.
    Break-even needs 0.6 c² per kilogram (`REGENERATIVE_CONVERTER_EVALUATION.md`
    l.8, 169–206).
  - Allowed added material needs 2.5 c² per kilogram, and charge layers need
    5.1 MV, above the pair threshold.
  - The radial-cell thermal bank needs 3–9 c² per kilogram, and the report says
    "a general material search [is] premature … Work pauses"
    (`VIRTUAL_RADIAL_CELL_PHOTON_CONTACT_DESIGN.md` l.12–20, 211–217, 271–274).
- **Counterfactual.** The ratio of duty to spare rest inventory was computable
  at `4d6af24`/`cc1c210`. The next 22–25 commits and 3 reports developed
  temperatures, contacts and photon turnover first.
- **Candidate lesson.** Support energy duties in metric engineering are of the
  order of the geometry's source scale, ρc² in geometric units. Screen every
  store by E_stored/(Mc²) against the density budget first.
- **Generality.** Very general for designs with O(ρc²) stresses. Only field- or
  radiation-dominated stores can pass, and those need containment (C7).
- **Recurrence.** n = 4.

### C7. An optimistic enclosure bound stayed the reference after a 3× tighter one was derived

- **Date / commits.** `64006ae` → `7416b33`, used through `0e07a9c`.
- **What happened.** The U/3 trace bound gave a fade requirement of 0.2628.
  Two hours later, the componentwise DEC gave wall energy ≥ U, "stronger than
  the U/3 trace bound", and 0.5338 with the absorbed work counted
  (`FINITE_WORK_INTERFACE.md` l.224–254). The old value remained the reference
  in three reports, and magnetic insulation at 0.254 looked "favorable" against
  it (`CHARGED_CAPACITOR_CONSTRUCTION.md` l.36–38, 204–206). It was demoted in
  `COMPOSITE_CAPACITOR_AND_RAIL_CONNECTIONS.md` l.158–159.
- **Candidate lesson.** Use the tightest cheap necessary bound (componentwise
  energy conditions; the von Laue/virial integral) as the selection
  reference, and re-baseline explicitly when a tighter one appears.
- **Generality.** General for containment of field-energy stores.
- **Recurrence.** One bound, reused in 4 reports.

### C8. Partial ledgers flattered candidates; counting the full route reversed them

- **Date / commits.** `5e59da3`/`371bdf9`, `0e07a9c`/`162f399`, `4d6af24` →
  `27f8f18`.
- **What happened.**
  - Magnetic insulation went from 0.254 to 8.6–43.5 once its work was routed
    through the receiver, because flux freezing raises B² under compression
    (`CHARGED_CAPACITOR_CONSTRUCTION.md` l.8–9, 230–262).
  - An internally balanced capacitor removed the stresses the pressure link
    relied on, leaving a 6.45× shortfall.
  - A relaxed local thermal LP cleared both locations; restoring coherent
    control reopened a deficit.
- **Candidate lesson.** Compare components by their complete assembly ledger,
  including the transport of their work, reactions and heat. A field that
  carries load cannot be repackaged as an isolated store without replacing its
  stress.
- **Generality.** General.
- **Recurrence.** n ≈ 5 (with C9).

### C9. GR self-weight: a local contact cost hid an exponential pressure column

- **Date / commits.** `13cbdd1`, `152e32e`.
- **What happened.** The local pieces cost 158 at startup. The connected column
  p_x + 4ΓB a_s p = ΓB F needs a peak pressure of 221,217 and slice energy
  3.1e7, about 2e5× more: "The integrating factor accumulates that self-weight
  across the large clock gradient" (`PRESSURE_LINKED_STORAGE_COMPLETION.md`
  l.113–173).
- **Available since.** Yes: Tolman/TOV hydrostatics, where pressure has weight.
- **Candidate lesson.** Estimate the self-weight integrating factor
  exp(∫(1 + κ)ΓB a dx) across any stress-transmitting member in a strong lapse
  gradient before sizing local pieces.
- **Generality.** General for static support in strong redshift gradients.
- **Recurrence.** n = 1. Related to B1: the Tolman factor 78⁴.

### C10. Explicit correction: the independent audit omitted the moving-frame EM force

*The `JOINT_SUPPORT_CONTINUUM_CORRECTION.md` erratum.*

- **Date / commit.** `9133810` (12 Sep 11:01), 20 minutes after `b368552`.
- **What happened.** The independent continuum audit
  (`scripts/audit_joint_support.py` at `b368552`, l.73) dropped the term
  −vH_t/(NR⁴) from F_rest = Γ(F_normal − vP_normal). The solver target
  already had it, so the auditor was wrong and the solver right
  (`JOINT_SUPPORT_CONTINUUM_CORRECTION.md` l.3–17). The original report
  claimed the audit passed an independent covariant-divergence test "on a
  metric with nonzero shift". That test set `flux_energy=zero`, so the term
  was never exercised (`JOINT_SUPPORT_STRESS_SCHEDULE.md` l.211–213). The
  effect was small: residuals 11.96 → 11.89%, 8.24 → 8.18%, 4.60 → 4.50%. No
  decision changed.
- **Detected by.** Not recorded. The fix adds a manufactured solution with a
  time-dependent field and nonzero material velocity.
- **Candidate lesson.** A manufactured test verifies only the couplings it
  switches on. Frame-projection cross terms (time dependence × velocity ×
  field) vanish in static tests.
- **Generality.** General (coverage of method-of-manufactured-solutions
  tests).
- **Recurrence.** n = 1 erratum. It is also counter-evidence: the independent
  code was the faulty component.

### C11. A selected support target was reversed by conservative evolution

- **Date / commits.** `b368552` (10:41) → `a986c28`/`9a5f0be`/`ad2e7f7` (13:31).
- **What happened.** The target was selected with a solver residual of 3.2e-12,
  while the continuum audit in the same commit showed an 8.24% force
  residual. Conservative implicit evolution made it inadmissible: "An
  admissible approximate tensor becomes inadmissible when its force balance is
  evolved more accurately". The final routed target's fade remainder of 3.18 is
  about 9.6× the selected 0.333 (`JOINT_SUPPORT_REFINEMENT_AND_END_LOADS.md`
  l.4–7, 72–79; `JOINT_SUPPORT_CONSTRUCTION_REVIEW.md` l.5–7, 156–160).
- **Candidate lesson.** A schedule enforced only at collocation points is not a
  continuum source, and a tiny discrete residual says nothing about it.
  Promote only after a dense conservation audit and an admissibility check
  between nodes.
- **Recurrence.** "Between samples" in this block: n ≈ 7 (with C12). Across the
  window, with E8 and B15a, this is the most frequent numerical lesson.

### C12. Clearances that existed only at samples or at a moved test point

- **Date / commits.** `79b92d1` → `183f925`; `ae538ae`; `9dbaf92`.
- **What happened.**
  - Narrow cell pairs placed "between the earlier startup witnesses" passed.
  - Explicit replay withdrew those clearances (deficits 0.0016 and 0.014). A
    48 × 1029 pass then failed at 96 × 2057, with overloads between samples.
  - Averaging the demanded tensor over panels hid errors of ±0.01–0.02.
  - A midpoint-only temperature check failed at a time knot
    (`VIRTUAL_RADIAL_CELL_CONSTRUCTION.md` l.170–252, 357–393;
    `VIRTUAL_RADIAL_CELL_PRESSURE_LINK_REALLOCATION.md` l.337–356).
- **Candidate lesson.** Enforce time-dependent budgets over whole intervals
  (supersolution envelopes), never average the demanded tensor over a panel,
  and keep known failing witnesses inside any narrowed test.
- **Recurrence.** See C11.

### C13. Optimizers exploited unphysical freedoms; passivity was checked afterwards

- **What happened.**
  - Force concentration doubled under refinement.
  - Heat schedules failed a passive contact test "at every sampled material
    label".
  - "Large simultaneous conversion cycles … use the converter losses to export
    heat".
  - A fluid went near-cold, needing α⁴ < 1.7e-16 and volume contrasts of
    4.7e21; a warm floor cut this by more than 13 orders.
  (`GRADED_ELECTROTHERMAL_ASSEMBLY.md` l.176–184;
  `JOINT_ELASTIC_BACKING_PRESSURE_SCREEN.md` l.149–156;
  `VIRTUAL_RADIAL_CELL_CONSTRUCTION.md` l.291–296;
  `VIRTUAL_RADIAL_CELL_PRESSURE_LINK_REALLOCATION.md` l.200–288.)
- **Candidate lesson.** Energy-momentum balance alone admits schedules no
  passive material can realize. Build the second law, passivity and regularity
  into inverse source design as constraints.
- **Recurrence.** n = 4–5.

### C14. A spatial march posed against the characteristic direction

- **Date / commit.** `a986c28`.
- **What happened.** The time-derivative coefficient has the sign of the
  material velocity (−0.20 to 0). Marching from the left blew up; data at the
  inflow cut fixed it (`JOINT_SUPPORT_CONSERVATION_AND_PASSIVITY.md` l.56–61).
- **Candidate lesson.** On a shifted metric, material drift and shift decide
  which boundary is inflow; prescribe data there.
- **Generality.** Textbook well-posedness.
- **Recurrence.** n = 1.

### C15. Cheap nodewise screens excluded passive and permanent prestress early (positive)

- **Date / commits.** `b368552`, `a986c28`, `15bb755`, `f6a3e88`.
- **What happened.**
  - 73.6% of the axial-force changes run opposite to passive-spring behaviour.
  - A permanent flux-tube bundle needs amplitudes 851× apart at different
    nodes.
  - End jackets need values outside their admissible range.
  All were proved infeasible with exact certificates, in the same commits that
  proposed them (`SCALAR_FLUX_SUPPORT_CONSTRUCTION.md` l.87–93, 185–236;
  `JOINT_SUPPORT_REFINEMENT_AND_END_LOADS.md` l.127–137).
- **Candidate lesson.** When the demanded support stress changes sign or
  magnitude over the cycle, permanent or passive prestress cannot supply it.
  Test the time intersection of nodewise bounds first.
- **Generality.** General for time-dependent metric schedules.
- **Recurrence.** n = 4 or more; a positive example.

## Part D. Containment, optical and thermal transfer, fermionic hosts, C1 modules (16–17 September)

**Scope.** 50 commits, 41 new reports and about 473k inserted lines.
- *Storage phase:* `e7a9951`..`4c576e0`, 39 commits (2 of them disk cleanups),
  16 Sep 18:18 to 17 Sep 09:36.
- *Pause:* the topology decision `ba93e0e` (17 Sep 09:44). `plan.md` at that
  commit reads "Numerical work is paused for discussion".
- *C1 phase:* `4c576e0`..`42e6688`, 10 commits, 17 Sep 12:27–19:49, all on the
  static phase-0.745 surrogate.

Fuller notes are in `work/block_sep16_17.md`. I spot-checked the key citations:
the handoff decision rule, the Schwinger scale, the 58,279,574-field
requirement, the LP envelope and the pause.

### D1. The gate's own control case became the design geometry

- **Date / commits.** `e7a9951` (16 Sep), all seven C1 reports (17 Sep).
- **What happened.** Beyond A8, the Le handoff treats the matched static,
  zero-current slice as the *control* that separates a termination cost from
  a current-driven failure (handoff l.119–126). Every C1 screen used exactly
  that slice as its *design* geometry, recorded as "Unchanged", in 7
  reports. Examples: `C1_FINITE_MODULE_PAIR_SCREEN.md` l.25–29 and
  `C1_POPULATION_BOUNDARY_AND_REFINEMENT.md` l.22.
- **Candidate lesson.** When working on a surrogate, check that it is not the
  gate's control case, which by construction cannot show the failure.
- **Generality.** A sharp special case of L5 (reduced models).
- **Recurrence.** 7 reports.

### D2. Batch commit of uncommitted work; a user rule on commit discipline

- **What happened.** Seven commits landed in 33 s (16 Sep 18:18:07–18:18:40),
  with about 52.7k lines and about 238 MB of arrays. They included the wall
  rejection and the report that reopens it (D3), in the same second. Fourteen
  minutes later `AGENTS.md` gained "Commit completed, validated milestones as
  work proceeds" (`9083031`).
- **Lesson.** Commit each decision-bearing result, so that reversals and
  their triggers can be audited.
- **Generality.** Process truism. User correction.

### D3. A direction-averaged stress basis over-scoped a rejection

- **Date / commits.** `96aa74c` → `86c6163` → `ebb606b` (16 Sep).
- **What happened.** The current-carrying scalar wall failed its stress
  allocation. The ensemble audit reopened it: "In the original averaged
  support basis, a transverse Maxwell field and opposed axial photons both
  have tensor (u,p_z,p_⊥)=(1,1,0) … Their hoop and normal stresses differ"
  (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md` l.13–18, 38–42). The required strength
  dropped from k = 0.78–0.97 to k ≥ 0.022–0.089. The finite construction then
  failed anyway: 32 of 32 labels were short by 0.097–0.171
  (`FINITE_CONTAINMENT_HOSTS_AND_EVOLUTION.md` l.5–12, 240–247).
- **Candidate lesson.** Never assign mechanical duties, or reject a material
  class, from direction-averaged tensors. Keep the principal stresses of each
  constituent.
- **Generality.** General for anisotropic sources.
- **Recurrence.** n = 2, counting the reframed exclusion in D10.

### D4. A virial bound predicted the containment result before six commits measured it

- **Date / commits.** `702caec`, `1a4d9d4`, `cc4c300`, `96aa74c`, `86c6163`,
  `ebb606b`.
- **What happened.** The cold bank must absorb 3–9 c² per unit of added rest
  inventory (`STORAGE_CONTAINMENT_LITERATURE_REVIEW.md` l.17–25). Six commits
  then measured a stress-to-energy ratio k = 0.65–0.99 for every magnetic
  geometry. "Every tested geometry fails the whole-history comparison at
  k=0.5" (`MAGNETIC_GEOMETRY_COMPARISON.md` l.133–146). Demonstrated materials
  reach about 1.3e-5 (nuclear pasta), and Kevlar-class solids about 3e-11. The
  program fell back on ideal k = 1 primitives. The same literature review
  already cited the von Laue/virial result and Bousso's wall bound
  E_wall ≥ E_γ/2 (l.41–45, 70–86).
- **Counterfactual.** One line. Any gravitationally significant stored energy
  needs container stress of the order of its energy density.
- **Cost.** 6 commits, about 238 MB of arrays. About 30 later commits
  continued on ideal primitives.
- **Candidate lesson.** Run the virial/von Laue/DEC bound on any energy store
  inside the source budget before sweeping its geometry or materials.
- **Generality.** General and textbook. Part of L1.
- **Recurrence.** With C6 (E/Mc², 4 cases) and C7 (U/3 bound): n = 3 incidents
  of one fact.

### D5. A standing rejection was carried as a caveat through eight reports, then dropped from the summary

- **Date / commits.** Origin `ebb606b`; carried through 8 reports; summary
  `4c576e0`.
- **What happened.** A Cauchy–Schwarz host bound rejected 10 samples. Its
  necessary ceiling is 1.31e-8 against a retained 2.54e-8
  (`FINITE_CONTAINMENT_HOSTS_AND_EVOLUTION.md` l.141–157). The "ten rejected
  samples" caveat recurs in 8 downstream reports, while optics (loss budgets of
  1.273 ppm and 18.300 ppm), joints and controllers were optimized. The pause
  summary leads with "Its strongest system result is a conditional holding
  and transfer budget" and omits the rejection
  (`RAIL_STORAGE_AND_INTERFACE_STATUS.md` l.5–11, 34).
- **Candidate lesson.** A failed necessary condition blocks the optimization
  that depends on it, and it stays in every summary until resolved.
- **Recurrence.** With A9 and B10: negative results not propagated to
  summaries or plans, n = 3.

### D6. Implementation-first detour, stopped by a user pause and a topology decision

- **Date / commits.** Storage phase (`702caec` … `4c576e0`); `ba93e0e`;
  `1e9ac1d`.
- **What happened.** For 37 technical commits the program optimized hardware
  on an implicit continuous backbone. The list runs to magnetic jackets,
  elastic joints, ppm optics, splitters, rotor stores, capacitor ports,
  thermal relays, coaxial leads and fermionic-vortex hosts. The user paused
  the work. The topology decision then found the continuous build "one
  possible realization … requiring its own justification", and said that
  storage results add "an architectural preference without adding a physical
  feasibility result" (`RAIL_BUILD_TOPOLOGY_DECISION.md` l.20–24, 109–114).
  The first C1 screen found that "placement, source overlap and the extent of
  each internal load path materially change those fixtures' duties"
  (`C1_FINITE_MODULE_PAIR_SCREEN.md` l.13–16).
- **Counterfactual.** A finite-pair placement screen (68 cases, four workers)
  on 16 Sep.
- **Cost.** 37 commits, about 29 reports and about 180k lines, now
  "conditional inputs".
- **Candidate lesson.** Do not optimize subsystem hardware until the source
  mechanism and the build topology that fix its duties are settled. In GR,
  source placement and overlap change local duties non-additively.
- **Generality.** A general engineering truism. The non-additivity is the
  domain content.
- **Recurrence.** Repeated "detailed fixture … follows the combined source
  balance" statements: n = 4.

### D7. Physical normalization came last, and it exposed incompatible scale windows

- **Date / commits.** Normalization at `4c576e0` (17 Sep 09:36). Scale facts
  date from 9 and 12 Sep. Acknowledged 23 Sep (`plan.md` l.302–305) and
  quantified 25 Sep.
- **What happened.**
  - **The scale was inherited, not chosen.** η = 2.41e-5 is an eigenparameter
    of the 9 Sep condensate matching (`CONDENSATE_JOINT_CONTINUATION.md`
    l.13, 60). That branch had already failed its own source test, at
    5e-6 of the requirement. η set one rail unit at 204 ℓ_P and the throat at
    415 ℓ_P.
  - **The storage ledgers ran in "inherited ledger units" until the pause.**
    The draft normalization had applied the volume factor twice
    (`RAIL_STORAGE_AND_INTERFACE_STATUS.md` l.99–135: "applying another factor
    of D would duplicate the volume weighting").
  - **The scale windows conflict.**
    - Electric sources reach the Schwinger field for L ≲ 4.4e8 m: "E_peak =
      (5.86e26 volt)/L" (`CHARGED_CAPACITOR_CONSTRUCTION.md` l.266–271,
      12 Sep).
    - Quantum sources need L ≲ 0.45 mm (E15).
    - The rotor host needs a node action of at least 9.2e32 ħ
      (`FINITE_RADIUS_CARRIER_REQUIREMENTS.md` l.122–127).
    - Crewed transit needs L ≳ 1 m.
    - No single L satisfies the C1 source mix (the agent's arithmetic; not
      re-derived here).
- **Available since.** 9–12 Sep inside the repo. The tools are textbook:
  (ℓ_P/L)² scaling, the Ford–Roman and Pfenning–Ford warp-wall thickness of
  order 100 ℓ_P, the Schwinger field, the species bound.
- **Counterfactual.** A one-page scale table on 9–12 Sep would plausibly have
  redirected both phases: choose L first, then source families that scale
  correctly at that L.
- **Candidate lesson.** Fix the physical scale, or an admissible window,
  before choosing source families. Each family carries its own power of ℓ_P/L
  and its own material or pair-production limit. A scale inherited from a
  solver eigenparameter is not a design choice.
- **Generality.** Fully general. Part of L1.
- **Recurrence.** 4 unanchored microscopic parameters in the storage phase; η
  inherited in 5 C1 reports.

### D8. Normalize-before-structure (`1e9ac1d`); the first normalized number changed a decision within 41 minutes

- **Date / commits.** `a9217d5` (13:59) → `1e9ac1d` (14:29, user-agreed
  workflow) → `a955302` (15:10).
- **What the correction targeted.** Un-normalized or "granted" source terms
  counted as progress. The angular source had been "granted" as a target, and
  mode counts were "continuous nonnegative values". A 574-comparison spectral
  screen selected "neither compartment count nor overlap bracket"
  (`C1_ANGULAR_SCALAR_INVESTIGATION.md` l.117–122). The workflow ranks claim
  scopes: an algebraic target, then a positive spectrum, then a supplied
  stress.
- **What the first normalized result showed.** One field supplies −1.47e-10
  against a duty of −0.00858, so 58,279,574 fields are needed. Internal
  reflection adds 0.6% useful response while the end loads rise from 9.03 to
  about 1.5e6, and the neighbour carries −7.4e7
  (`C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md` l.127–153, 171–172,
  213–225). Blanket reflection was dropped in favour of transparency.
- **Counterfactual.** N ≈ duty·2880π²R⁴/(η·|coefficient|) is one line. It was
  available on 9 Sep and could have preceded both the 80-case LP and the
  574-case spectral screen.
- **Candidate lesson.** Establish a contribution's normalized magnitude before
  validating its structure (signs, spectra, algebraic fits).
- **Recurrence.** Part of L1, with B7 (magnitude deferred on 8–9 Sep): n = 2
  explicit incidents plus E15.

### D9. Multiplicity treated as a free continuous knob; the species bound was not applied

- **Date / commits.** `a955302`, `247b988`, `3975f7b`, `42e6688`.
- **What happened.**
  - N was kept continuous (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md`
    l.230–233). Allocations used about 25 million scalars and radial central
    charges up to 8.1e8.
  - The same morning, species were counted for the rotor host (140 Dirac
    species) but not for the angular scalars.
  - The agent's check with the repo's own Sep 25 method: ℓ_* ≈ √N ℓ_P ≈
    3,400–7,600 ℓ_P, which is 8–18× the 415 ℓ_P throat. The throat would sit
    inside the strong-coupling length of its own field content.
- **Available since.** The Dvali species bound (2007–2010), applied in the repo
  only on 25 Sep (`SOURCE_SCALING_TEST.md` l.157–167).
- **Counterfactual.** One line at `a955302`, which would have ended the
  multiplicity route before 3 more commits.
- **Candidate lesson.** A large-N semiclassical source must satisfy
  √N ℓ_P < (smallest curvature radius of the demand). Multiplicity is not a
  free design knob.
- **Generality.** General and literature-backed (Dvali).
- **Recurrence.** 4 reports.

### D10. An anomaly identity excluded the radial channels; a reframing turned the exclusion into a requirement on another component

- **Date / commits.** `e968b01` (13:17) → `57aadf8` (13:31).
- **What happened.** The 2D anomaly fixes
  (ρ_Q − p_{r,Q}) = ηc(a″ + a′²)/(48π²R²), independently of state and cavity
  length. The geometry needs −0.00100 at the transition; the coefficient is
  +0.000358. Every nonnegative mix has the wrong sign, and 80 of 80 radial-only
  comparisons fail (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md` l.126–149). Fourteen
  minutes later, a user-directed rewrite ("Preserve component roles") led with
  the "conditional radial-plus-angular allocation". The exclusion became a
  lower bound on the angular target. That target then needed 25–58 million
  fields (D8, D9).
- **Available since.** 9 Sep (`LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md`
  l.155–162); the 2D trace anomaly is textbook.
- **Candidate lesson.** Anomaly-fixed stress combinations cannot be tuned by
  state, length or multiplicity. Derive such sign constraints first.
  Recasting an exclusion as a requirement on another component is legitimate
  only if that component is normalized promptly.
- **Recurrence.** The identity is reused as a certificate in 3 reports.

### D11. Sparse-probe passes reversed as probes were added; each fix moved the deficit to the boundary it created

- **Date / commits.** `247b988` → `3975f7b` → `42e6688` (16:03–19:49).
- **What happened.**
  - ℓ₀ = 4 passed at 2 probes, then failed at 4 and 6 probes.
  - Frozen witnesses failed at nearby points.
  - Six-coordinate allocations failed the expanded check (ρ − p_r = −0.386;
    84 of 84 fail).
  - After inserting walls, 16 of 72 passed at 11 samples. The dense check then
    found (ρ + p_t) = −0.00796 at x = 0.300001, the newly created angular
    endpoint (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md` l.85–100, 140–149,
    207–214).
  - The handoff had named this test in advance: "does the composite source
    actually cure the edge, or merely move it outward one layer at a time?"
    (handoff l.24, 103).
- **Candidate lesson.** Pointwise feasibility at sparse probes is not
  feasibility. After each fix, track where the worst residual goes,
  especially at the boundaries the fix introduces.
- **Generality.** General for inverse source allocation.
- **Recurrence.** Relocation under fixes of a fixed demand: the May regulator
  (P01), A6 and this: n = 3. The between-samples part belongs to L4.

### D12. Feasibility hinged on an unfixed renormalization coupling

- **Date / commit.** `247b988`, carried to `42e6688`.
- **What happened.** Only ℓ₀ = log(R₀/a₀) = 2 or 4 passed. The report itself
  says that a change of subtraction convention is compensated by the
  couplings α, β, that the total is invariant, and that "A material mechanism
  for adjusting the couplings has yet to be established"
  (`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md` l.133–150, 257–264). Work
  continued with ℓ₀ = 2.
- **Available since.** The Wald ambiguity (the local conserved terms ⁽¹⁾H and
  ⁽²⁾H) is textbook.
- **Candidate lesson.** A semiclassical source whose feasibility depends on
  the finite parts of R² couplings is not a source until those couplings are
  physically fixed. Relabelling moves stress between the two sides of the
  equation without creating any.
- **Generality.** General.
- **Recurrence.** 3 reports.

### D13. A C²-joined reference metric was used for fourth-derivative vacuum stress

- **Date / commits.** `247b988`, `3975f7b`. Resolved by the C∞ rule on 23 Sep.
- **What happened.** The absolute renormalized stress contains ⁽¹⁾H, ⁽²⁾H,
  which involve fourth derivatives. The reference had C² Hermite joins from the
  8 Sep repair. The reports sample "smooth portions" and defer the global
  ledger (`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md` l.203–207). The 9 Sep
  d⁻² curvature-step result (B4c) was already on record.
- **Candidate lesson.** Semiclassical work needs metrics smooth to at least
  fourth order, in practice C∞.
- **Recurrence.** Joins L9 (smoothness): A3, B4, D13 → n = 3 incidents.

### D14 (minor). An unbounded LP concentrated support material

- **What happened.** "The initial relaxation allowed arbitrarily concentrated
  supports. Its maximum density grew under refinement"
  (`C1_FINITE_MODULE_PAIR_SCREEN.md` l.88–96). An envelope of 0.0363 fixed it.
  The next screen relaxed the envelope, and its passes peak at 0.098 and 0.086
  (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md` l.58, 222–225).
- **Lesson.** Minimum-energy LPs without regularity bounds converge to
  distributions. Keep the bound, or record every pass that violates it.
- **Generality.** Textbook (bang-bang optima).

### D15 (minor). An illustrative cut forced a non-perturbative coupling

- **What happened.** β = 5.8e-11 and g = 3.97 gave a loop-to-tree ratio of
  2.7e10/e². It was replaced 33 minutes later
  (`FERMIONIC_STRING_MATERIAL_CANDIDATE.md` l.103–141;
  `FINITE_RADIUS_CARRIER_REQUIREMENTS.md` l.3–9).
- **Lesson.** Check perturbative control whenever a parameter is pushed to an
  extreme.
- **Generality.** Field-theory hygiene; caught early.

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
    (`ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md` l.122–130). The same day, the
    role audit found 96.69% of the negative radial-null balance outside
    |x| ≤ 2: an Ellis tail (B9).
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
  against how the object is meant to come into being. A geometry that some
  source could hold open may still be one that no source can form from
  ordinary space.
- **Generality.** General and literature-backed (Geroch; topology-change
  theorems). It applies to any design with a minimal surface or a "throat".
- **Recurrence.** n = 1 major incident. Related: B9 (the Ellis tail), the
  "far_exterior" bookkeeping label (preflight) and E4. Together, L6: n = 4
  with one root.

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
- **Recurrence.** Same fact: B3 derived it four times on 8–9 Sep, so n = 5
  encounters. Knowledge in the record not applied: L12, n = 7.

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
- **Amendment.** The closure report first gave 1.05° as the escape cone. The
  ANEC map pass, two hours later, found the forward cone narrower: 0.36° at
  2.1c, where the cone's lapse adds to the plateau. The closure report was
  amended in the same commit (`e744879` diff of `GEOMETRY_CLOSURE_PASS.md`
  l.51–52). One direction of one audit was refined by a different tool, so
  this is a small instance of E14 itself.
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

### E18. A schedule was optimized before the class-level termination decision

- **Date / commits.** 23 Sep: `5abcc98` (15:45), superseded by `6e1a1fb`
  (15:59), `2a3f404` (17:39) and `97a78ca` (22:15).
- **What happened.** The reset comparison ran 9 decompression schedules through
  the full audit suite, about 12 minutes on six workers. It recommended a
  half-rate trailing front: 80% less angular deficit, a delay of 4.1
  (`RESET_SCHEDULE_OPTIONS.md` l.6–21, 177–187). The termination decision was
  then still open (`plan.md` at `9c1021a`, "settle those two decisions").
  Within two hours the one-space revision held the support compressed with no
  decompression (`ONE_SPACE_REVISION.md` l.16–17, 81–85). Five hours later the
  amplitude pass removed the support stretch altogether
  (`AMPLITUDE_PASS.md` l.13–15). The recommended schedule never entered a
  design.
- **What survived.** The comparison confirmed that decompression dominates the
  deficit, and it first recorded the two kinematic readings (E3). The holding
  decision reused it ("the slow-reset comparison shows the same
  packet-coordinate advantage", `ONE_SPACE_REVISION.md` l.84–85).
- **Counterfactual.** Taking the termination decision first. It was already
  posed that morning, and its resolution rests on a topology fact (E5).
- **Cost.** Small: one report, a few hours.
- **Candidate lesson.** Settle class-level choices (topology, termination,
  which elements exist at all) before optimizing parameters within the class.
- **Generality.** A truism of design ordering. The same pattern at larger cost
  is D6.
- **Recurrence.** n = 2 (D6 and this).

## Part F. Counter-evidence: practices followed that did not help, or misled

Each item names a practice the project followed and the record showing it
failed to prevent, or actively caused, a problem. None of this shows that
the practice is bad. It shows the limits of what it certifies.

| # | Practice | What happened | Source |
|---|---|---|---|
| F1 | Passing tests and "independent" verification | The legacy classifier passed its 4 focused tests (and the May audit's 58) while failing 15/19 analytic fixtures and flipping rest-energy signs. The joint-support audit was "independent" code, but its test set `flux_energy=zero`, so the omitted term was never exercised. Sixteen robustness checks certified a one-sided shooting artifact. | A1, C10, B6 |
| F2 | Machine-precision verification and provenance hashing | Examples: 504 eigensystems to 1e-16, 147,528 action matrices, 6,507 references over 79 manifests, 264 hashes. In the C1 phase, the RSET agreed to 2.3e-9 and 222 manifest hashes were verified, and a 574-comparison spectral screen decided nothing (D8). None of these tested the premises that later failed: static surrogate, two-ended topology, magnitude, species bound. Their demonstrated value was operational, the recovery after an interruption (`3dbd12b`/`3759d2c`). | `work/block_*.md`; D8 |
| F3 | Refinement ladders | Many converged without changing any decision (semiclassical 5.01e-6 → 5.38e-6 against a 2×10⁵ gap; elastic depletion time refined four ways). The EM stop time converged although the stop was numerical. Node-level "refinement-stable" Type I verdicts missed bands (E8). The refinement that mattered, the Type IV witness converged to 0.001%, was cheap. | B7, C1, E8; `work/block_sep10_12.md` C2 |
| F4 | Per-candidate pre-registration and stop rules | Each candidate stopped honestly and fast. About 16 families were opened in about 25 hours on 8–9 Sep, and 183 commits followed to 17 Sep. The written program-level rule in the handoff was bypassed (A8, F14). | A8 |
| F5 | Local scope qualifications | They were present in the reports ("applies to this proposed equilibrium attachment"), yet later recommendations exceeded them. The 9 Sep scope correction did not constrain 10–17 Sep. | B10 |
| F6 | Affirmative-writing and no-running-log rules | They erased the negative gate verdict from the only document being updated (A9). The PDF-with-every-edit rule produced 6 rebuilds for content removed the same day. | A9, B13 |
| F7 | A relative figure of merit without an absolute threshold | Ranking by "required negative-null remainder" (75.78 → 0.104 → 3.18) steered about 90 commits and could not reveal that no remainder is acceptable. | Part C header |
| F8 | Gate relaxations declared as model tests | Guide drift 0.5 → 0.6 → 0.8, reserve 0.2% → 0.5%, crediting excluded inventories: the local pass came, and the branch still stopped at the mass barrier. In C1 the passes rested on stacked relaxations: arbitrary DEC material, continuous N, a granted angular target, field-selective transparency, zero m/q, free hosts, lossless photon control and chosen R² couplings. No ledger records which relaxations a pass depends on. | `work/block_sep10_12.md` C4; `work/block_sep16_17.md` D |
| F9 | "Reproduce the reference audits" as a success criterion | The constant-radius track reproduced beta075's 2.569/1.233 service ratios exactly (`CONSTANT_RADIUS_TRACK.md` l.242). That carried the kinematic mismatch and the missing exterior path forward. | E3, E4 |
| F10 | Append-only reports | Superseded headlines stay at the top of reports (for example `SCREENED_SCALAR_CONDENSATE.md` l.3). The disclosure still says quantum fields supply the rail below 0.45 mm (E15). | B6, E15 |
| F11 | A single pass/fail gate as the design driver | Designs chosen to pass carried 450× excess energy, 9,069× clocks and a front horizon (γ = 10²²). | E7, E11, E13; P01 §2h–i |
| F12 | Reproducibility evidence and the parallel-worker rule | One batch committed about 238 MB of arrays. Two mid-research cleanups followed (1.282 GiB and 5.511 GiB; 2 commits, 2 reports). Four-worker parallelism was applied to jobs of 2.5 s and 10.3 s. | `work/block_sep16_17.md` C |
| F13 | "Preserve specialized components" with narrowly scoped exclusions | Exclusions were re-expressed as duties on components not yet built (D3 reopening; D10 reframing). Negative results did not accumulate, and the softening sat in leads and summaries (D5; the `57aadf8` lead rewrite). Report bodies carry 106 fail/reject/exclude mentions. | D3, D5, D10 |
| F14 | Written stopping rules | The handoff rule ("redesign before Comer inversion", 8 Sep) and the workflow rule ("insufficient normalized strength … ends", 17 Sep) were each bypassed on the day they applied. | A8 |
| F15 | A provisional topology preference | C1 was adopted before any C1 number existed. The first measurements (77% more support energy, twice the charge inventory) did not reopen it. The decision record requires evidence to change the preference but not to keep it. Weak item. | `work/block_sep16_17.md` G |

## Part G. User corrections visible in the record

Source types:
- (R): stated in the repository.
- (I): inferred from the timing and wording of a reversal.
- (M): stated in the user's auto-memory files, which lie outside the repository.

| Date | Correction | Effect | Source |
|---|---|---|---|
| 9 Sep | Disclosure stripped of trial narratives. | The Le verdict was lost with them (A9). | `734156c` (I); the AGENTS.md rule was codified 16 Sep (R) |
| 9 Sep | "The previous recommendation … repeated work already established in the design record". | Archive re-screen. | `83fe023` (I/R) |
| 9 Sep | Scope correction: static background results are not rail selection gates. | Did not constrain 10–17 Sep. | `a1a8a65` (I/R) |
| 10 Sep | "the user's material-velocity concern" (γ ≈ 47). | Heat-supply chain redirected to the mechanics (C3). | `PRESTRESSED_BUFFER_VELOCITY_INVESTIGATION.md` l.237 (R) |
| 10 Sep | "The user has set this assembly aside"; string sources deferred. | Phase A closed (C4). | `RESERVOIR_FEASIBILITY_ENVELOPE.md` l.257–260 (R) |
| 12 Sep | "three-hour investigation authorized on 12 September". | Time-boxing. | `JOINT_SUPPORT_CONSTRUCTION_REVIEW.md` l.11–16 (R) |
| 16 Sep | The supplied gate handoff and Casimir handoff were committed as "separate research context", and `AGENTS.md` was created (report, disclosure and worker rules). | The handoff's decision rule was not wired into the plan (A8). | `e7a9951` (R) |
| 16 Sep | "Commit completed, validated milestones as work proceeds". | Followed the 33-second batch commit (D2). | `9083031` (R) |
| 17 Sep | "Numerical work is paused for discussion"; build topology C1 added to `AGENTS.md`. | Storage phase stopped (D6). | `ba93e0e` (R) |
| 17 Sep | "Preserve component roles": the radial-only exclusion was reframed. | D10. | `57aadf8` (I/R) |
| 17 Sep | Normalized-source workflow agreed; `AGENTS.md`: "Prioritize physically normalized component contributions". | The first normalized number changed a decision within 41 minutes (D8). | `1e9ac1d` (R) |
| 23 Sep | "Agreed direction": reinstate the gate, C∞ rule, redesign the geometry. | Redesign began. | `9be57e0`, plan l.27–36 (R/I) |
| 23 Sep | "Track termination: one space (decided)". | Axial track and one-space revision. | `2a3f404` (R/I) |
| 23 Sep | "tube"/"wall" renamed "service region"/"transverse boundary layer". The user had read the old names as a physical pipe. | Terminology. | `5aa0b49` (R); memory `geometry-region-terminology` (M) |
| 24–25 Sep | A 55× packet clock is a failure for crewed transit; report aging, tides and acceleration. | Compartment pass (E13). | memory `rail-goal-is-crewed-transit` (M) |
| 25 Sep | The disclosure update had not been authorized. | Process rule (E16). | memory `disclosure-updates-need-explicit-go-ahead` (M) |
| 25 Sep | Front trapping is the known warp-drive problem the user had raised in an earlier paper. | Framing (E11). | memory `answer-user-comments-directly` (M) |
| 25 Sep | Choreography may use planned timing and local fallback, never superluminal coordination signals. | Choreography columns in E11. | memory `rail-choreography-causality` (M) |
| 25 Sep | Investigate both branches of every fork. | Shelf recorded beside the cone. | memory `record-design-forks` (M) |
| 24 Sep | Cite the disclosure at a pinned commit in the addendum. | The addendum first cited the living disclosure without a commit. | `9bdf376` "pin the disclosure commit" (R); memory `pin-disclosure-citations` (M) |
| 25 Sep | Describe the shelf in the rail's own terms. The user rejected "the FTL result comes from the shelf's lapse" and the comparison to a wormhole or Krasnikov trade: the shift remains the carrier. | Framing of E11's fork. | memory `rail-mechanism-framing` (M) |
| 25 Sep | Report where and when NEC violation occurs, without restating that FTL needs it. | Reporting style. | memory `nec-violation-reminders` (M) |

## Part H. Recurring lessons across the window

Counts are distinct incidents; brackets give instances within an incident.
Strength codes:
- **A:** an identity, theorem or verified literature, plus at least one
  incident with a clear counterfactual.
- **B:** at least three incidents in this record with an understood
  mechanism, or a textbook numerical fact.
- **C:** one or two incidents; a heuristic.
- **T:** a truism.

The column "For the book" is a first sort, not a vetting verdict.

| # | Lesson (general form) | Incidents | n | Strength | For the book |
|---|---|---|---:|---|---|
| L1 | Apply class-level exclusions and physically normalized magnitudes before sign, placement or construction work. Covers: quantum inequality with the species bound; achronal ANEC for any lead over exterior light; the hardware energy of boundary-induced sources; E/Mc² and virial bounds on stores; dimensionless coupling thresholds; a fixed physical scale. | B3, B7, B11, C4, C6, C7, D4, D7, D8, D9, E10, E15 | 12 | A | Yes. The central ordering principle, and the costliest single pattern in the window. |
| L2 | NEC-satisfying components only add to the null bill. Count the exotic sector's own supports (holders, mirrors, confinement, bulk motion with its Doppler weight). | B2 [×8], C4 [×4] | 2 (12 instances) | A (identity) | Yes, as an identity with its operational corollary. |
| L3 | Derive the class identities, scalings and onset or asymptotic expansions of the metric family before numerics. Examples: null-Hessian, shear, flux, κ-scaling, onset order, Tolman factor, census, anomaly and speed-as-lapse identities. | Positive: A5, E1, E2, E6, E12. Numerics ran first where an identity decided: A6, A7, B1, B5, B11, C9, D10. | 12 | A | Yes. The identities are book content. |
| L4 | Verify between samples: bands between nodes, constraints over intervals, dense residuals after each fix. Coarse grids can also manufacture Type IV. | A5, E8 [×3], C11, C12 [×7], D11, B15a | 6 (≈14 instances) | A | Yes (verification chapter; P01 §2e). |
| L5 | A reduced model or surrogate can forbid a failure mode outright, so a pass there certifies only the model. Never use a gate's control case as the design case. | P01 static surrogate, B10, D1, E6, E14 | 5 | A (static ⇒ Type I is a theorem; the shear identity is exact) | Yes. |
| L6 | State the global structure first: topology, number of ends, the exterior, and the reference for any performance comparison. | E5, B9, E4, the "far_exterior" label (A-list) | 3–4 (one root) | A (Geroch; flare-out) | Yes. |
| L7 | Report occupant quantities (clock rate, tides, proper acceleration) with every geometry. | B14, E13 (4 designs) | 2 | B | Yes, for crewed designs. The flat compartment is an identity. |
| L8 | A pass/fail gate needs magnitudes and side effects beside it: the minimal passing amplitude, the cost scaling, causal channels. | E7 [×3], P01 §2i, E12 | 3 | B | Yes, as a hazard with its mechanism. |
| L9 | Use C∞ primitives. Semiclassical stress demands more smoothness than classical matching (d⁻³ at sheets, d⁻² at curvature steps, fourth derivatives in the RSET). | A3 [×3], B4 [×3], D13 | 3 | A (textbook) | Yes. |
| L10 | Diagnostics at degenerate or near-vacuum tensors need exact evaluators, scale-aware tolerances and noise floors. Invariants provide free artifact tests. | A1, E17 [×5], B15a | 3 (7 instances) | B | Yes, briefly. |
| L11 | Solver and stop statuses are not physics. Use source-free controls, original-row checks and certificates. | C1 [×3], C5 [×4], B6 | 3 (8 instances) | B (textbook numerics) | Yes, briefly (methods). |
| L12 | Keep negative verdicts, standing rejections and prior results live in the standing status and in every summary. | A9, B3/E10, B10, B12, D5, E5, E15 (the May list) | 7 | B (process) | Methods sidebar only. Governance, not physics. |
| L13 | Stopping rules at two levels, both binding where work is ordered. Candidate level: pre-registered acceptance, no tuning, stop on a stable necessary-condition failure. Program level: a failed demand gate means redesign the geometry before building sources. | A8; F14 (two written rules bypassed); positive candidate-level stops in A6, A7 and Parts B–D | 2 | C (heuristic; the candidate level is well supported) | Yes, labelled as a heuristic, with the Le ladder as evidence. |
| L14 | Count the complete ledger: assembly routes, reactions, GR self-weight, fit residuals, divergence-free freedom, per-constituent principal stresses. | A2, C7, C8 [×3], C9, D3 | 5 | B | Yes (bookkeeping chapter). |
| L15 | When a design moves to a new model, re-derive the need for every inherited element (ablate against demand, occupant and service metrics). | E2 [×3] | 1 (3 instances) | C | A heuristic. Ablation is a truism; the identities that make it fast are content. |
| L16 | For superluminal patterns, locate the surfaces where α² = b² and classify them (a horizon only where the transverse gradient vanishes). Keep every front's normal speed below local light. | E11, E12 | 2 | A (literature plus identity) | Yes. |
| L17 | Read the sign of the surface stress a junction demands before choosing a shell material. | B5 [×3] | 1 | A (textbook) | Yes, briefly. |
| L18 | Put the second law, passivity and regularity inside inverse source optimization. Unbounded LPs converge to distributions. | C13 [×4–5], D14 | 2 | B | Yes (inverse-design chapter). |
| L19 | Derive every payload-attached field and audit from one payload worldline. | E3 | 1 | C | A sentence. |
| L20 | Define the performance metric within the geometry: arrival against the earliest signal through the same background. Check that it responds to what it names. | E4 | 1 (2 aspects) | A (standard definition) | Yes. |
| L21 | Lock the design record only after the class-eliminating checks have run. | E16 [×3], B13 | 2 | C (process) | No (project governance). |
| L22 | Some semiclassical constraints cannot be tuned away: anomaly-fixed stress combinations, the Wald renormalization ambiguity (finite R² parts), the species bound on multiplicity. | D9, D10, D12 | 3 | A (textbook) | Yes. |
| L23 | When the geometry fixes the demand, a local source fix relocates the deficit. Track the worst residual after every fix (the edge-migration test). | P01 (22 May regulator), A6, D11 | 3 | B | Yes; a direct corollary of "the demand is G/8π". |
| L24 | Settle the source mechanism, build topology and class-level geometry choices before optimizing subsystems or parameters. | D6, E18 | 2 | T/C | A truism. The non-additivity of placement in GR is the domain content. |

**Demote to single sentences.** These pass vetting as statements but carry
little domain content:
- A4: a local repair cannot reach a remote defect;
- "test edge cases" in L10;
- ablation in L15;
- envelope testing in E12;
- D2: commit discipline;
- L24.

## Closing table

**n** is the recurrence count of the lesson across the window, taken from
each entry and Part H. **Strength** uses the Part H codes:
- **A:** an identity, theorem or literature, plus an incident with a
  counterfactual;
- **B:** multiple incidents or textbook numerics;
- **C:** a heuristic from one or two incidents;
- **T:** a truism.

| Incident | Lesson | n | Generality | Strength |
|---|---|---:|---|---|
| A1 Legacy classifier: sign branch and absolute tolerance corrupted May rest-frame data | Validate type/EC classifiers on degenerate analytic fixtures across amplitudes, with scale-free tolerances | 7 (L10) | General | B |
| A2 Role ledger repeated tensors; fitted exchange current left the support tensor free | A ledger is not a partition; conservation fixes a tensor only up to divergence-free terms | 5 (L14) | General (identity) | A |
| A3 Receiver cusp, lapse kink, cap slope | C∞ primitives; audit every clip, abs and join | 3 (L9) | General | A |
| A4 C2 repair could not touch remote Type IV | Check that a repair's support overlaps the defect | 1 | Truism | T |
| A5 Uniform slowdown: κ²(κ²h₂² − 4j₁²) | Derive how the obstruction scales with a knob before sweeping it | 12 (L3) | General identity | A |
| A6 Coupled reset: Type IV moved outward; mass overdraft f = −0.61 | Local source fixes relocate a fixed demand; check the Misner–Sharp budget first | 3 (L23) | General (mass budget: spherical) | B |
| A7 1,024-point search, 780 undecided; onset expansion excluded every family | Order-match switch-on and boundary expansions before optimizing | 12 (L3) | General | A |
| A8 The handoff's "redesign before Comer inversion" rule was bypassed; 183 commits followed | Two-level stopping rules, binding where work is ordered | 2 | Heuristic | C |
| A9 Le verdict erased from disclosure; never entered the plan | Negative verdicts are status and stay in it | 7 (L12) | Process | B |
| B1 Inverse fit forced K_TT = 0; Tolman 78⁴ preload | Check a source's principal-part contribution and mass price before fitting | 2 | General | A |
| B2 Eight NEC-satisfying families failed on one sign fact | Null budget, including the exotic sector's own supports | 12 inst. (L2) | Universal | A |
| B3 Casimir holding cost re-derived four times | Hardware energy gate for boundary-induced sources | 5 | General | A |
| B4 Delta sheets d⁻³, curvature steps d⁻², cutoff-dependent walls | Smooth backgrounds and finite boundaries before ⟨T⟩ | 3 (L9) | General, textbook | A |
| B5 Junction demanded compression; shell buckles; patches saturate | Read the junction stress sign before choosing the shell material | 3 | Thin shells | A |
| B6 One-sided shooting blow-up reported as an obstruction | Global BVP or analytic argument before a no-go claim | 1 | General numerics | B |
| B7 Sign-only screening; first magnitude 5e-6 of the requirement | Normalized magnitude first | 12 (L1) | General | A |
| B8 Bulk tension assigned to the quantum sector | Split bulk tension from null deficit before allocating | 1 | General, standard | A |
| B9 Ellis tail: 96.7% of the null demand outside the throat | Global structure first (see E5) | 4 (L6) | General | A |
| B10 Scope error recognized 9 Sep, did not stick | List what a surrogate can represent; propagate corrections to the plan | 5 (L5) / 7 (L12) | General | B |
| B11 Helpful and holding terms scale alike (g* ≈ 1.7e4, N_f e²/16π² > 18) | Compute the dimensionless threshold first | 3–4 | General rule of thumb | B |
| B12 Redundant recommendation; archive re-screen at most 0.3% | Search the archive; compare effect size with the gap | 1 | Near-truism | T |
| B13 Disclosure used as a running log for 3.5 h | Keep specification and log separate | 2 (L21) | Process | C |
| B14 Throat lapse 69–108 never read as aging | Report occupant quantities | 2 (L7) | Crewed designs | B |
| B15 Early catches: coarse-grid Type IV, truncated expansion, CSV precision | Resolution-sensitive classification; validity ranges; exact I/O | 6 | General | B |
| C1 Numerical temperature floors read as physical depletion | Source-free controls; classify stops before interpreting | 3 (L11) | General | B |
| C2 Energy error normalized to the total, not the deciding budget | Normalize to the deciding budget; find the active step limit | 2 | General, textbook | B |
| C3 Heat add-ons for a γ ≈ 47 kinematic cause (user redirect) | Check the receiving matter's kinematics first | 1 | One-way forcing designs | C |
| C4 Null projection computed after dynamics (3,248× burden) | k·T·k screen, with Doppler weight, before dynamics | 4 (12 with B2) | Universal | A |
| C5 HiGHS dropped coefficients; "valid" states violated rows | Solver status is not physics; certificates | 4 (L11) | General | B |
| C6 Stores need 0.6–9 c² per kilogram | E/Mc² screen first | 4 | Very general | A |
| C7 U/3 trace bound kept as reference after the ≥U bound | Tightest cheap bound; re-baseline | 1 (4 reports) | General | B |
| C8 Partial ledgers flattered (insulation 0.25 → 8.6–43.5) | Complete assembly ledger | ~5 (L14) | General | B |
| C9 Pressure column self-weight about 2e5× local cost | Tolman integrating factor before sizing | 1 | General | A |
| C10 Erratum: audit omitted −vH_t/(NR⁴); its test had the field off | Manufactured tests must activate every coupling | 1 | General | B |
| C11 Selected target reversed; burden 9.6× | Dense conservation audit before promotion | ~14 inst. (L4) | General | A |
| C12 Clearances only at samples or a moved point | Enforce budgets over intervals; keep failing witnesses | (C11) | General | A |
| C13 Optimizers used non-passive freedoms (α⁴ < 1.7e-16) | Passivity and second law inside the optimization | 2 (L18) | General | B |
| C14 March posed against the characteristic direction | Data on the inflow boundary set by drift and shift | 1 | Textbook | T |
| C15 Nodewise screens excluded passive prestress early (positive) | Time intersection of nodewise bounds first | 4 | General | B |
| D1 The gate's control slice used as the C1 design geometry | Never design on the gate's control case | 5 (L5) | General | A |
| D2 33-second batch commit; commit rule | Commit per decision-bearing result | 1 | Truism | T |
| D3 Direction-averaged stresses over-scoped a rejection | Per-constituent principal stresses | 2 | General | B |
| D4 Virial bound predicted containment (k = 0.65–0.99 needed) | Virial/DEC bound on stores before sweeps | 3 | General, textbook | A |
| D5 Standing host rejection dropped from the pause summary | Failed necessary conditions block and persist | 7 (L12) | Process | B |
| D6 37 hardware commits before topology and mechanism (user pause) | Mechanism and topology before subsystem optimization | 1 | Truism plus GR non-additivity | T/C |
| D7 Scale inherited from an eigenparameter; windows conflict | Fix the physical scale window first | 12 (L1) | General | A |
| D8 58,279,574 fields; decision changed in 41 minutes | Magnitude before structure | 12 (L1) | General | A |
| D9 Multiplicity as a knob; √N ℓ_P exceeds the throat | Species bound on large-N sources | 3 (L22) | General | A |
| D10 Anomaly-fixed ρ − p_r excluded radial channels, then reframed | Anomaly-fixed combinations cannot be tuned; normalize any reassigned duty | 3 (L22) | General | A |
| D11 Sparse-probe passes reversed; deficit moved to the new wall | Dense residual tracking after each fix | 3 (L23) | General | B |
| D12 Feasibility needed a chosen finite R² coupling | The Wald ambiguity moves stress; it does not supply it | 3 (L22) | General | A |
| D13 C² reference metric for fourth-derivative RSET | C∞ (at least C⁴) for semiclassical work | 3 (L9) | General | A |
| D14 Unbounded LP concentrated material | Regularity bounds in LPs | 2 (L18) | Textbook | B |
| D15 Illustrative cut forced loop/tree 2.7e10 | Check perturbative control at extremes | 1 | Hygiene | T |
| E1 Null-Hessian identity: 13,587 → 0 Type IV | Derive the class null-energy identities; they become design rules | 5 | General (spherical identity; axial analogue) | A |
| E2 Decompression overlap, 600× stretch and carve were unnecessary | Ablate inherited elements in a new model | 1 (3) | Heuristic | C |
| E3 Windows at unit speed, packet at U/B | One payload worldline for all fields and audits | 1 | General | C |
| E4 Service ratios against an absent exterior path; 2.569 insensitive | Define advantage within the geometry; check responsiveness | 2 | General | A |
| E5 Two-ended wormhole needing topology change, knowable in May | State topology, ends and exterior before sourcing | 4 (L6) | General | A |
| E6 Spherical pass → 74,700 Type IV in one-space embedding | Re-gate in the real embedding; reductions forbid modes | 5 (L5) | General | A |
| E7 e⁸ pre-sheath: 450× excess energy, FTL channel, 9,069× clock | Minimal passing amplitude plus census in the gate pass | 3 (L8) | Heuristic | B |
| E8 Node grids missed bands (8 Sep, 23 Sep ×2) | Verify between nodes | 14 inst. (L4) | General | A |
| E9 Gate domain stopped short of switch-on and tapers | Cover the full support to exact vacuum | 2 | Near-truism | T |
| E10 Casimir-plus-positive-mass proposed 24 Sep, refuted 25 Sep | Charge enabling hardware (mirrors carry ~10⁷× the deficit) | 5 (with B3) | General | A |
| E11 Front light surface: γ = 10²²–10⁷² | Locate α² = b² surfaces and trace what is swept | 2 (L16) | Superluminal designs | A |
| E12 15° cone traps light above 3.9c | Front normal speed below light; test the envelope | 2 (L16) | General | A |
| E13 Clocks 108× to 9,069×; tides 3e16 m/s²/m unreported | Occupant quantities in every audit; flat compartment | 2 (L7) | Crewed designs | B |
| E14 3D audit: lapse cavity, 1.05° escape cones | Full-dimension optical audits | 5 (L5) | General | B |
| E15 Achronal-ANEC exclusion of quantum sources came last | Class-level theorems before magnitudes and constructions | 3 (May list) / 12 (L1) | Superluminal and shortcut designs | A (regime caveat) |
| E16 Disclosure locked three times before class-eliminating checks | Lock after the checks that can kill the class | 3 | Process | C |
| E17 False Type IV from truncation, one-ulp flags, step-size crossings, sub-noise velocities | Exact evaluators, noise floors, invariant tests, known-limit tests | 7 (L10) | General | B |
| E18 Reset schedule optimized before the termination decision; moot within hours | Class-level choices before in-class optimization | 2 (L24) | Truism | T |
