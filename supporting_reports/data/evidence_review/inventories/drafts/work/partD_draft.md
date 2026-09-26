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
