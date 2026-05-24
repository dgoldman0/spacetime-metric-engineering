# Question Bank Review

Date: 2026-05-24

This is a human acceptance log for the current seed bank. The script in
`scripts/validate-bank.mjs` is only a mechanical gate for schema, banned meta
text, and public source-card URLs. It is not a rubric scorer and must not be
treated as question-quality review.

## Current State

- Accepted items: 167.
- The bank is now inside the first-release size range, but still needs deeper
  domain coverage before it should be treated as a complete curriculum.
- Established general theory is now treated as the durable core layer. The bank
  includes GR/differential-geometry foundations plus a broader foundation spine
  for quantum mechanics, QFT/vacuum/Casimir physics, semiclassical gravity,
  effective field theory, source-model literacy, and bounded string-theory
  context.
- Paper-specific coverage remains useful, but not yet exhaustive. Most
  disclosure-bibliography papers have at least one manually reviewed item; deeper
  coverage should continue adding advanced items per paper.
- Paper-theory items have been rewritten to ask about the paper's own theory,
  results, assumptions, or implications rather than unmarked active-rail design
  lessons.
- Paper-theory stems now include a publication year and author/title anchor so
  learners know exactly which paper is being tested. Vague stems like "the
  study" are not accepted.
- The UI now separates claim status from question context: general theory,
  paper theory, project application, and project state.
- Explanation-depth validation now scales by difficulty so intermediate and
  advanced items cannot pass with ultra-thin `why` or boundary text.
- Project-state and open-gate items remain flagged so they can be included or
  excluded selectively.
- Revision-sensitive project-state items were manually reviewed for provisional
  wording such as "appears", "could", "current", or "candidate" so they do not
  read like final project facts.

## 2026-05-24 Manual Review Pass

The expansion pass was reviewed in three groups after mechanical validation:

- **Established foundations:** reviewed for pure general-theory scope, useful
  learning objective, plausible distractors, and separation between source demand
  and physical source realization. One mixed energy-condition item was rewritten
  to remove project-ledger vocabulary from the foundation track.
- **Paper theory:** reviewed for paper/year anchoring, public arXiv source cards,
  no project-specific framing, and explanations that distinguish model analysis
  from feasibility or source realization.
- **Project application and project state:** reviewed for flags, explicit
  boundary language, provisional wording where claims could change, and
  avoidance of treating current package behavior as established theory.

Mechanical validation remains a floor, not an approval substitute.

## 2026-05-24 Difficulty Calibration Audit

The difficulty audit found that several questions were incorrectly labeled
`advanced` because the topic was advanced, not because the question required
advanced reasoning. That is not acceptable.

Reviewer rule going forward:

- The human reviewer, not the validator, is the primary reviewer for every
  question.
- `advanced` must require an identifiable advanced move: synthesis, assumption
  tracking, evidence sufficiency, cross-status classification, or transfer from
  literature into a bounded review scenario.
- If the correct answer is a slogan and the wrong answers are obvious absolutes,
  the item is `core` or `intermediate`, even if the paper or theory behind it is
  hard.
- A difficult source does not make a shallow question difficult.

Actions taken in this audit:

- Downgraded recognition-level items that were mislabeled as `advanced`.
- Rewrote the ADM-constraints item into a residual-diagnosis scenario so its
  `advanced` label is earned.
- Rewrote selected design-review and quantum-inequality items so distractors are
  plausible review mistakes rather than throwaway overclaims.
- Left the bank intentionally advanced-light until more genuinely advanced
  questions were written.

Post-audit distribution:

- Core: 30.
- Intermediate: 65.
- Advanced: 11.

## 2026-05-24 Advanced Expansion Pass

The follow-up pass added genuinely advanced items and manually reviewed them for
the failure mode that prompted this audit: hard topic, easy question. The new
items emphasize scenario review, assumption tracking, source-realization
layering, gauge-vs-constraint separation, global-vs-local causal reasoning,
paper-result transfer, and calibrated evidence sufficiency.

Subsequent review found two bank-level quality failures that are now explicit
rubric blockers:

- Learner-facing explanations must explain the material, not the author's reason
  for assigning a difficulty level. Phrases such as "this is advanced because"
  or "the advanced move is" belong in review notes, not in the answer panel.
- Select-all items must not all have the same answer shape. A serious bank needs
  4 to 6 choices as appropriate, with 1, 2, 3, or more correct answers depending
  on the concept.

## 2026-05-24 Explanation And Select-All Audit

This pass reviewed every learner-facing question prompt, answer, and explanation
in the 128-item bank. The review focused on two concrete failures: explanations
that described authoring choices instead of the material, and select-all
questions that taught a predictable answer pattern.

Actions taken:

- Rewrote explanations that said or implied "this is advanced because..." so
  they now explain the physics, evidence boundary, or paper result directly.
- Removed learner-facing authoring-room phrases such as "this item" and
  "learner" from explanations and boundaries.
- Added a validator guard against difficulty/rubric language in explanations.
- Varied select-all choice counts and answer counts where the material justified
  it, including 5- and 6-choice evidence-review items.
- Added three one-correct select-all items where the point is scope discipline:
  one checked contraction, one supported paper claim, or one supported observable.
- Added a validator guard that prevents the multi-select bank from collapsing
  back to one answer shape.
- Re-reviewed the select-all bank after finding a second pattern collapse: most
  items had shifted from two-correct to three-correct. Several items were
  rewritten by hand so the correct-answer count follows the material rather
  than a template.
- Recalibrated difficulty after the rewrite: the topological-censorship
  recognition item is now intermediate, while advanced select-all items carry
  more assumption tracking, scale matching, domain-of-dependence review, and
  conflicting-evidence judgment.
- Expanded short explanations where the answer panel needed more subject-matter
  teaching, especially quantum-inequality, Natario, chronology-protection, and
  geodesic-study items.

Current select-all shape distribution:

- 14 items: 5 choices, 3 correct.
- 6 items: 7 choices, 4 correct.
- 6 items: 6 choices, 4 correct.
- 6 items: 6 choices, 3 correct.
- 6 items: 5 choices, 2 correct.
- 2 items: 6 choices, 2 correct.
- 2 items: 5 choices, 1 correct.
- 1 item: 4 choices, 1 correct.
- 1 item: 4 choices, 2 correct.

Remaining curriculum concern: future passes should continue varying answer shape
where the subject matter naturally supports it. Do not force answer-count variety
at the cost of truth.

Manual changes in this pass:

- Added advanced established-foundation items on ADM gauge interpretation,
  constraint residuals, stress-energy conservation, type-I energy-condition
  quantifiers, global causal patches, and source-realization layering.
- Added advanced paper-theory items for Alcubierre 1994, Natario 2002,
  Mueller-Weiskopf 2012, Everett-Roman 1997, Barcelo-Visser 2000,
  Ford-Roman 1996, Clark-Hiscock-Larson 1999, and topological censorship.
- Added advanced project-application items only where the prompt is explicitly
  flagged and bounded: conflicting evidence, claim-scope classification, and
  repeated-use reset evidence.
- Replaced several cartoon distractors with more realistic misconceptions:
  local smoothness vs global theorem scope, central-ray evidence vs
  finite-bundle access, repeated local rung vs physical-source closure, and
  formal scalar solution branch vs physical-regime caveats.

Current distribution after this pass:

- Core: 30.
- Intermediate: 69.
- Advanced: 29.

## 2026-05-24 Intermediate And Advanced Distractor Audit

This pass reviewed the intermediate and advanced standard-choice items for a
specific failure mode: questions that could be answered by eliminating answers
that no informed learner would take seriously. Mechanical scans were used only
to surface candidate items with words such as "all", "only", "automatically",
"irrelevant", and "secondary"; acceptance remained a manual judgment.

Rubric updates:

- Added difficulty-scaled discrimination as a required quality criterion.
- Required intermediate and advanced distractors to preserve a plausible surface
  feature, assumption, scope error, or common overextension.
- Clarified that obviously false absolutes belong only in basic-recognition
  checks or when the option represents a real-world overclaim that the
  explanation teaches against.

Manual review actions:

- Rewrote weak distractors across ADM constraints, causal structure,
  topological censorship, quantum inequalities, stress-energy, geodesic studies,
  chronology protection, active-rail source ledgers, endpoint handoff, and
  paper-to-design transfer.
- Replaced cartoon claims such as "the source is solved", "all paths are flat",
  or "constraints are irrelevant" with nearby but wrong claims: local-to-global
  promotion, metric-to-source promotion, clean-observable promotion,
  gauge-to-physics promotion, and source-demand-to-realization promotion.
- Rechecked the shared explanations and adaptive feedback wherever answer
  choices changed, so the answer panel teaches the material distinction rather
  than merely naming the right choice.

Current interpretation: the bank is still a seed curriculum, but intermediate
and advanced choice questions now require more boundary discrimination than the
earlier draft. Future expansion should preserve this standard from first draft
rather than relying on cleanup passes.

## 2026-05-24 Broad Foundations Expansion

This pass broadened the established-foundations track beyond GR-centered
material. It added 39 manually reviewed items across modeling discipline,
quantum mechanics, QFT basics, quantum vacuum interpretation, Casimir effect,
semiclassical gravity, effective field theory, source-model basics, numerical
evidence discipline, thermodynamic accounting, and bounded string-theory
context.

Review passes:

- First pass checked domain balance so the additions were not merely more warp
  literature or project-state questions.
- Second pass checked intermediate and advanced distractors for plausible
  misconceptions rather than obvious throwaways.
- Third pass checked explanations for material teaching, source boundaries, and
  no project-specific leakage in general-theory items.

Current distribution:

- Total: 167.
- Core: 43.
- Intermediate: 90.
- Advanced: 34.
- Established foundations: 92.
- Published warp and wormhole context: 43.
- Active-rail architecture: 13.
- Design review and synthesis: 19.

The bank now meets the first-release target for established-foundation count,
but several domains still need deeper follow-up: quantum measurement/state
formalism, QFT in curved spacetime, material Casimir systems, source-model
stability, and high-energy effective descriptions.

## Source Hygiene

- Learner-facing paper links now point to actual public source locations, not to
  local repo copies.
- Current paper links are arXiv source pages with full paper access. The source
  URLs used in the bank returned public pages during the current review run.
- The old Hawking chronology DOI card was replaced with Visser's open arXiv
  chronology-protection review because a fully accessible source for the full
  PRD paper was not verified.
- Generic no-URL textbook cards were replaced with Carroll's open arXiv general
  relativity notes for metrics, Einstein-equation context, geodesics,
  stress-energy tensor notation, and Bianchi/conservation identities. Carroll is
  no longer treated as the primary anchor for energy-condition taxonomy or
  global hyperbolicity.
- Energy-condition definition and interpretation items now use Curiel's open
  arXiv primer. Quantum-inequality items remain anchored to Ford and Roman.
- Causal-hierarchy and global-hyperbolicity items now use Minguzzi-Sanchez,
  Sanchez, and Bernal-Sanchez rather than a generic GR-notes citation.
- The Morris-Thorne OSTI record is not used as a learner-facing source because
  it is a bibliographic/abstract record rather than verified full paper access.
  Morris-Thorne correspondence content is currently sourced through the
  Garattini-Zatrimaylov arXiv paper.

## Public Sources In Use

- ADM: `https://arxiv.org/abs/gr-qc/0405109`
- Alcubierre: `https://arxiv.org/abs/gr-qc/0009013`
- Ford-Roman: `https://arxiv.org/abs/gr-qc/9510071`
- Carroll GR notes: `https://arxiv.org/abs/gr-qc/9712019`
- OpenStax University Physics Volume 3: `https://openstax.org/details/books/university-physics-volume-3`
- Tong QFT notes: `https://davidtong.org/teaching/quantum-field-theory/`
- Milton Casimir review: `https://arxiv.org/abs/hep-th/9901011`
- Burgess EFT notes: `https://arxiv.org/abs/hep-th/0701053`
- Polchinski D-brane notes: `https://arxiv.org/abs/hep-th/9611050`
- Douglas-Kachru flux compactification review: `https://arxiv.org/abs/hep-th/0610102`
- Curiel energy conditions primer: `https://arxiv.org/abs/1405.0403`
- Barcelo-Visser: `https://arxiv.org/abs/gr-qc/0003025`
- Natario: `https://arxiv.org/abs/gr-qc/0110086`
- Topological censorship: `https://arxiv.org/abs/gr-qc/9305017`
- Visser chronology protection: `https://arxiv.org/abs/gr-qc/0204022`
- Minguzzi-Sanchez causal hierarchy: `https://arxiv.org/abs/gr-qc/0609119`
- Sanchez global hyperbolicity review: `https://arxiv.org/abs/0712.1933`
- Bernal-Sanchez smooth Cauchy hypersurfaces: `https://arxiv.org/abs/gr-qc/0306108`
- Clark-Hiscock-Larson: `https://arxiv.org/abs/gr-qc/9907019`
- Mueller-Weiskopf: `https://arxiv.org/abs/1107.5650`
- Everett-Roman: `https://arxiv.org/abs/gr-qc/9702049`
- Shoshany-Snodgrass: `https://arxiv.org/abs/2309.10072`
- Garattini-Zatrimaylov: `https://arxiv.org/abs/2401.15136`
- Smeared NEC paper: `https://arxiv.org/abs/2503.19955`

## Cleanup Decisions

- Removed `PROJECT_WORK_ANALYSIS.md` and all learner-facing meta-analysis source
  cards.
- Replaced local project paths with verified public GitHub URLs for source
  cards.
- Marked project-state and open-gate items with content flags so they can be
  included or excluded selectively.
- Corrected the symbol-role item from `established_theory` to
  `active_rail_model` because the notation is taught in the project service
  context.
- Removed a throwaway distractor about a future certification title.
- Added a first manually reviewed disclosure-bibliography layer rather than
  relying only on generic foundation samples.
- Renamed the visible `literature_model` label to "Published literature" and
  added context filtering so paper study and project application can be selected
  independently.

## Accepted Items

| ID | Decision | Manual review note |
|---|---|---|
| `foundation.adm_lapse.001` | accept | Core ADM vocabulary; answer is unambiguous and sourced to ADM. |
| `active_rail.packet_plant.001` | accept | Basic active-rail architecture distinction; public project sources point to the disclosure and harness reference. |
| `literature.alcubierre.001` | accept | Core literature-status boundary; arXiv source verified. |
| `constraints.energy_conditions.001` | accept | Intermediate constraint interpretation; avoids claiming energy conditions prove buildability. |
| `source_ledger.dragfill.001` | accept | Good symbol-fill use; rendered token avoids typing LaTeX; boundary states demand is not realization. |
| `chronology.sequence.001` | accept | Core active-rail sequence item; useful for orientation, public schedule/reset sources verified. |
| `claim_status.classification.001` | accept with flags | Valid classification drill, but includes project/open-gate material, so it is flagged. |
| `symbols.matching.001` | accept after status fix | Useful symbol-role item; treated as active-rail model context rather than pure established theory. |
| `design_review.burden.001` | accept with flags | Advanced design-review item; answer requires separating packet success from plant burden. |
| `project_state.internal_ledger.001` | accept with flags | Project-state handling item; source links now public and current-scope caveat is explicit. |
| `foundation.metric_interval.001` | accept | Core metric concept; no project-specific language in the stem; open Carroll source used. |
| `foundation.adm_shift.001` | accept | Core ADM vocabulary; distractors are plausible enough for basic level. |
| `foundation.nec.dragfill.001` | accept | Core NEC fill item; rendered math token is appropriate and avoids LaTeX typing. |
| `foundation.hamiltonian_constraint.001` | accept | Intermediate ADM constraint item; tests source-diagnostic interpretation without overclaim. |
| `foundation.extrinsic_curvature.001` | accept | Intermediate ADM geometry item; clear distinction from intrinsic curvature and matter choice. |
| `foundation.observer_energy.001` | accept | Intermediate stress-energy projection item; distinguishes observer energy density from trace and null contractions. |
| `foundation.energy_conditions.matching.001` | accept | Matching item for NEC, WEC, and trace distinctions; useful for preventing later source-channel confusion. |
| `foundation.einstein_equation.dragfill.002` | accept | Core drag-fill equation item; rendered token avoids typed LaTeX and reinforces the curvature/source relation. |
| `foundation.adm_momentum_constraint.001` | accept | Intermediate ADM momentum-constraint item; distinguishes momentum projection from topology, vacuum, and quantum-state distractors. |
| `constraints.qi_interpretation.001` | accept | Intermediate Ford-Roman interpretation; rejects both simplistic bans and construction claims. |
| `literature.barcelo_visser.scalar.001` | accept after project-framing cleanup | Advanced source-literature item; includes both scalar energy-condition violation and trans-Planckian caveat. |
| `literature.natario.001` | accept | Literature-context item; zero expansion is correctly framed as kinematic, not source-free. |
| `constraints.topological_censorship.001` | accept | Advanced constraint item; answer depends on theorem assumptions rather than slogan recall. |
| `constraints.chronology_protection.001` | accept | Core/intermediate causality boundary; open Visser source replaces unverified DOI access. |
| `literature.alcubierre_horizon.001` | accept | Advanced Alcubierre interpretation; separates metric ansatz from controllable engine. |
| `literature.chl.null_geodesics.001` | accept after project-framing cleanup | Paper-specific CHL item; focuses on null access and horizon-like structures, not construction. |
| `literature.muller_weiskopf.geodesics.001` | accept after project-framing cleanup | Paper-specific geodesic/lensing item; keeps exotic-matter feasibility caveat visible. |
| `literature.everett_roman.krasnikov.001` | accept after project-framing cleanup | Paper-specific chronology-network item; distinguishes single tube from two-tube time-machine arrangement. |
| `literature.shoshany_snodgrass.ctc.001` | accept after project-framing cleanup | Paper-specific modern chronology item; concrete two-warp closed-timelike-geodesic construction is the tested lesson. |
| `literature.garattini_zatrimaylov.correspondence.001` | accept after project-framing cleanup | Paper-specific correspondence item; keeps intrinsic-curvature requirement and traversability caveat visible. |
| `constraints.snec.semiglobal.001` | accept | Advanced smeared-NEC item; tests semilocal accumulation rather than pointwise-only thinking. |
| `literature.alcubierre.stress_energy.002` | accept | Advanced Alcubierre item; separates metric ansatz from ordinary-matter construction and source burden. |
| `constraints.ford_roman.sampling.002` | accept | Advanced Ford-Roman item; focuses on sampling-time/magnitude-duration reasoning rather than slogan recall. |
| `literature.chl.control.002` | accept | Intermediate CHL item; rejects the passenger-control misconception using causal-access reasoning. |
| `literature.shoshany_snodgrass.energy.002` | accept | Advanced chronology/energy item; keeps CTG construction and WEC violation together. |
| `literature.garattini_zatrimaylov.intrinsic_curvature.002` | accept | Advanced correspondence item; tests the intrinsic-curvature ingredient explicitly. |
| `constraints.visser_chronology.horizon.002` | accept | Intermediate chronology-protection item; focuses on quantum/backreaction concern near chronology horizons. |
| `active_rail.packet_vs_plant.001` | accept | Core architecture item; public project sources support packet/plant separation. |
| `active_rail.source_ledger_boundary.002` | accept | Intermediate source-ledger boundary; explicitly separates source demand from source sector. |
| `active_rail.demand_realization.classification.003` | accept with flags | Mixed source-status classification item; project/open content is flagged and source links are public. |
| `active_rail.service_evidence.sequence.002` | accept | Intermediate service-review sequence; reset audit is correctly not assumed away. |
| `active_rail.service_readiness.sequence.003` | accept | Intermediate chronology item; adds readiness and reset-residue checkpoints without overclaiming reuse. |
| `active_rail.paper_application.chl.001` | accept with flags | Advanced paper-to-design transfer item; clearly marked as project application, not paper theory. |
| `active_rail.channel_roles.matching.001` | accept with flags | Project-state diagnostic taxonomy; public source links verified and flags are present. |
| `claim_status.classification.002` | accept with flags | Strong mixed-status item; marked as project/open content because it includes current source-family scope. |
| `project_state.v10_scope.002` | accept with flags | Advanced revision-sensitive status item; interprets V10 failure as current-package boundary, not universal impossibility. |
| `project_state.v5_scope.001` | accept with flags | Advanced V5 scope item; public sources support fixed-background/watch/non-claim boundaries. |
| `design_review.evidence_sufficiency.002` | accept with flags | Advanced evidence-sufficiency item; open physical-realization gates are explicit. |
