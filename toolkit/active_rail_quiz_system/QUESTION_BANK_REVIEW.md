# Question Bank Review

Date: 2026-05-23

This is a human acceptance log for the current seed bank. The script in
`scripts/validate-bank.mjs` is only a mechanical gate for schema, banned meta
text, and public source-card URLs. It is not a rubric scorer and must not be
treated as question-quality review.

## Current State

- Accepted items: 34.
- Paper-specific coverage is now useful for a seed bank, but not yet enough for
  a full curriculum. Most disclosure-bibliography papers have at least one
  manually reviewed item; deeper coverage should add more advanced items per
  paper.
- Paper-theory items have been rewritten to ask about the paper's own theory,
  results, assumptions, or implications rather than unmarked active-rail design
  lessons.
- The UI now separates claim status from question context: general theory,
  paper theory, project application, and project state.
- Project-state and open-gate items remain flagged so they can be included or
  excluded selectively.

## Source Hygiene

- Learner-facing paper links now point to actual public source locations, not to
  local repo copies.
- Current paper links are arXiv source pages with full paper access.
- The old Hawking chronology DOI card was replaced with Visser's open arXiv
  chronology-protection review because a fully accessible source for the full
  PRD paper was not verified.
- Generic no-URL textbook cards were replaced with Carroll's open arXiv general
  relativity notes for metrics, Einstein-equation context, and energy-condition
  notation.
- The Morris-Thorne OSTI record is not used as a learner-facing source because
  it is a bibliographic/abstract record rather than verified full paper access.
  Morris-Thorne correspondence content is currently sourced through the
  Garattini-Zatrimaylov arXiv paper.

## Public Paper Sources In Use

- ADM: `https://arxiv.org/abs/gr-qc/0405109`
- Alcubierre: `https://arxiv.org/abs/gr-qc/0009013`
- Ford-Roman: `https://arxiv.org/abs/gr-qc/9510071`
- Carroll GR notes: `https://arxiv.org/abs/gr-qc/9712019`
- Barcelo-Visser: `https://arxiv.org/abs/gr-qc/0003025`
- Natario: `https://arxiv.org/abs/gr-qc/0110086`
- Topological censorship: `https://arxiv.org/abs/gr-qc/9305017`
- Visser chronology protection: `https://arxiv.org/abs/gr-qc/0204022`
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
| `active_rail.packet_vs_plant.001` | accept | Core architecture item; public project sources support packet/plant separation. |
| `active_rail.source_ledger_boundary.002` | accept | Intermediate source-ledger boundary; explicitly separates source demand from source sector. |
| `active_rail.service_evidence.sequence.002` | accept | Intermediate service-review sequence; reset audit is correctly not assumed away. |
| `active_rail.channel_roles.matching.001` | accept with flags | Project-state diagnostic taxonomy; public source links verified and flags are present. |
| `claim_status.classification.002` | accept with flags | Strong mixed-status item; marked as project/open content because it includes current source-family scope. |
| `project_state.v5_scope.001` | accept with flags | Advanced V5 scope item; public sources support fixed-background/watch/non-claim boundaries. |
| `design_review.evidence_sufficiency.002` | accept with flags | Advanced evidence-sufficiency item; open physical-realization gates are explicit. |
