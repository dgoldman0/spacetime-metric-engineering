# Active-Rail Training System Roadmap

This roadmap keeps the system modest in implementation scope but honest about
product shape. The goal is no longer just a good quiz system. The goal is an
active-rail training suite with two first-class products:

- **Qualification Board:** the quiz/study/timed assessment product.
- **Rail Service Terminal:** the active-rail operator simulator.

The Qualification Board teaches and tests theory, references, claim boundaries,
and active-rail vocabulary. The Rail Service Terminal lets the learner act as a
line engineer inside a qualitative architecture-logic simulation.

The first three phases still describe the qualification/curriculum path:

1. Quiz infrastructure.
2. Curriculum design.
3. Content population.

Phase 4 defines the Rail Service Terminal simulation product:

4. Rail Service Terminal.

Design comes first for Phase 4. The terminal must have its own domain model,
visual simulation model, interface architecture, and simulator loop before code
changes.

Phase 5 now captures the suite-level product shell and the Service Terminal
visual-simulation rewrite needed to make the terminal feel like line operation,
not a themed quiz panel.

## Phase 1: Quiz Infrastructure

Build the system that can render, grade, review, and organize questions.

This phase should produce a usable quiz application with a small sample bank. It does not need the final curriculum or a huge question set yet, but it does need the right architecture: a lightweight dynamic frontend, real math rendering, specialized activity renderers, and an assessment model that can grow beyond one generic card layout.

### Core Features

- Load question data from structured files instead of inline JavaScript.
- Support question filtering by module, difficulty, type, claim status, and question context.
- Support study mode with immediate explanations.
- Support quiz mode with delayed grading.
- Support timed quiz mode with one-question-at-a-time pacing, a selected time
  limit, scorekeeping, and an optional explanation-review pause.
- Support review of missed questions.
- Show clear claim-status badges on every question.
- Show explanations with answer, reason, boundary, and references when present.
- Show structured source links to papers, textbooks, project docs, repository files, or run artifacts when present.
- Render math and symbolic tokens with a LaTeX rendering library.
- Work well on desktop, tablet, and mobile.

### Infrastructure Subphases

Phase 1 should be split into practical subphases.

1. Prototype checkpoint.
   - Static app.
   - Separate sample bank.
   - Basic filters.
   - Basic grading.
   - Basic question types.
2. Rendering and data foundation.
   - Convert the prototype into a small Vite/React app.
   - Add proper LaTeX rendering.
   - Add a renderer registry.
   - Normalize question data around render blocks, answers, explanations, references, source links, claim status, and optional content flags.
   - Add schema validation or a lightweight bank validation script.
3. Specialized activity surfaces.
   - Keep the standard quiz surface.
   - Add boundary classification surface.
   - Add symbol/equation lab surface.
   - Keep sequencing questions inside the qualification drill.
   - Prepare room for ledger and case-file surfaces.
4. Assessment and reports.
   - Separate concept accuracy from claim-boundary accuracy.
   - Track module, claim-status, and activity-type performance.
   - Report missed questions and recommended review sets.
   - Keep qualification rules configurable by mode.

### Question Types

Implement the types needed for a good first system, but do not force them all into the same UI:

- multiple choice,
- select all,
- true/false,
- drag-fill word bank,
- sequencing,
- matching.

The first renderer set should include:

- standard quiz renderer for multiple choice, select all, and true/false,
- symbol/equation renderer for drag-fill,
- ordering renderer for sequencing,
- matching renderer for pairs and small classifications,
- boundary-classification renderer for claim-status training.

Leave diagram labeling and full ledger labs for later unless they become easy
extensions. The Rail Service Terminal should be treated as a separate
operational surface, not as another question type.

### Drag-Fill Word Bank

This is the most important interaction upgrade from the prototype.

Requirements:

- Users place rendered word or equation tokens into blanks.
- Users can drag tokens.
- Users can also click/tap token then click/tap blank.
- Mobile interaction must feel natural.
- Keyboard use must be possible.
- Users should not need to type LaTeX.
- Tokens should support rendered text and rendered LaTeX math.

### Math Rendering

Add proper math rendering early, before content population.

Requirements:

- Use KaTeX or another real LaTeX rendering library.
- Store canonical math in question data as LaTeX.
- Render math in prompts, choices, tokens, blanks, explanations, references, and reports.
- Keep plain-text aliases for accessibility and validation only.

### Dynamic Frontend Target

Move from static-file prototype to a small local-first frontend app now.

Recommended scope:

- Vite + React.
- KaTeX dependency installed through the package manager.
- Local question-bank modules imported by the app.
- Componentized surfaces for standard quiz, symbol/equation work, sequencing,
  matching, and boundary classification.
- Local browser state for one session at a time.
- No backend.
- No database.
- No user accounts.

This is not a move to a large platform. It is a move to a healthier frontend structure before the UI becomes too rich for one static file.

### Grading

The grading system should be flexible but not overbuilt.

Track:

- total score,
- score by module,
- score by difficulty,
- score by question type,
- score by claim status,
- score by activity surface,
- missed-question list.

Also track claim-boundary mistakes separately. For this project, confusing "established theory" with "active-rail model" is a meaningful learning failure, not just another wrong answer.

Use `ASSESSMENT_MODEL.md` as the guide for richer scoring. The first implementation can be partial, but it should not block future grading dimensions.

### Data Model

Define a simple question schema with room to grow.

Minimum fields:

- `id`,
- `type`,
- `track`,
- `module`,
- `difficulty`,
- `claim_status`,
- `prompt`,
- render blocks or prompt parts,
- `choices` or `tokens`,
- `answer`,
- `explanation`,
- `boundary_note`,
- `references`,
- `source_links`,
- `tags`.

Do not make the schema perfect before building. It should be strict enough to prevent messy content and simple enough to author by hand.

The schema should also support richer explanation metadata:

- `explanation.answer`,
- `explanation.why`,
- `explanation.boundary`,
- `explanation.misconceptions`,
- `explanation.openGate`,
- optional adaptive feedback keyed to choices, blanks, tokens, sequence relations, matching prompts, or classification statements,
- `references[]` with citation/source-kind/support fields,
- `sourceLinks[]` with label/kind/url/support fields.

Adaptive feedback is not a required migration field. The infrastructure should
render it when present and fall back to the shared explanation when absent, so
the bank can improve incrementally without blocking builds.

### User Experience

The first screen should be the quiz/study tool itself.

Required surfaces:

- mode selector,
- timed duration selector when timed mode is active,
- explanation-review toggle for timed study-practice sessions,
- module multi-select facet,
- claim-status multi-select facet,
- track multi-select facet,
- difficulty multi-select facet,
- question count selector,
- active workspace,
- score/report area,
- missed-question review.

The design should feel like a polished engineering console: readable, calm, fast, and clear. It should look much better than the prototype, but the first implementation should avoid ornamental complexity.

The Qualification Board workspace should change by activity type. A
boundary-classification session, a symbol lab, and a design-review case should
not all be cramped into the same generic card. The Rail Service Terminal is a
separate top-level product surface with its own shell, not another
question-card workspace.

Timed mode should keep those specialized surfaces but show only the active item.
Its timer is a pacing constraint, not a separate scoring dimension in the first
implementation. If explanation review is enabled, the countdown pauses while the
learner reads feedback and resumes when the next item starts.

Filter controls should not force narrow single-choice paths. Tracks, modules, difficulties, activity types, claim statuses, and question contexts should allow selecting multiple values. Empty selection should mean "all." Count and optional-content policy can stay single-choice.

### Phase 1 Done When

- A user can run a mixed quiz from structured data.
- At least six question types work.
- Proper LaTeX rendering works.
- Drag-fill works without typing equations.
- A renderer registry or equivalent separation exists.
- At least one specialized surface exists beyond the standard quiz card.
- Grading reports module and claim-status performance.
- Timed quiz mode can run through a selected question set, stop on time expiry,
  and optionally pause for explanations after submitted answers.
- Explanations clearly separate answer, reason, and epistemic boundary.
- The interface is pleasant enough that content authors will want to use it.

## Phase 2: Curriculum Design

Design what the system teaches before filling it with lots of questions.

This phase should produce the curriculum map, module list, claim taxonomy, and authoring rules. It should prevent the later content phase from becoming a pile of isolated trivia.

It should also define the question quality rubric. The first serious curriculum pass should reject meta questions about the quiz system itself, shallow wording checks, unsupported theory claims, and advanced items whose difficulty comes from unclear prose rather than reasoning demand.

### Curriculum Tracks

Use three main teaching tracks plus one review/synthesis track.

1. Established foundations.
2. Published warp and wormhole context.
3. Active-rail architecture.
4. Design review and synthesis.

### Established Foundations

Define the real theory users need before they can reason well about active-rail ideas.

Likely modules:

- mathematical modeling, units, dimensional analysis, scaling, perturbations,
  approximation regimes, boundary conditions, and stability;
- spacetime and metric basics,
- causal character and packet norm,
- stress-energy tensor,
- observer projections,
- energy conditions,
- ADM lapse and shift,
- constraint and evolution language,
- null contractions,
- quantum mechanics basics: states, observables, spectra, uncertainty,
  expectation values, and ground states,
- quantum vacuum basics: zero-point energy, vacuum fluctuations, mode
  structure, and the limits of vacuum-energy language,
- Casimir effect: boundary-conditioned field modes, force/energy differences,
  experimental status, and why it is not a macroscopic free-energy source,
- semiclassical stress tensor,
- backreaction and quantum inequalities.
- effective field theory: scale separation, cutoff sensitivity, matching, and
  validity domains,
- source-model literacy: scalar fields, electromagnetic fields, fluids,
  anisotropic stress, equations of state, and stability,
- bounded string-theory context: strings, branes, compactification, moduli, and
  effective descriptions as background literacy rather than source-option
  endorsement.

### Published Warp And Wormhole Context

Define the literature background without pretending it is solved engineering.

Likely modules:

- Morris-Thorne wormholes,
- Alcubierre warp metric,
- Natario-style warp concepts,
- Lorentzian wormhole analysis,
- exotic matter requirements,
- Ford-Roman quantum inequality constraints,
- chronology and horizon issues,
- topological censorship.

### Active-Rail Architecture

Define the project-specific concepts.

Likely modules:

- packet-centered service,
- rail as operating plant,
- support/carry/catch/fade/decompress/reset chronology,
- support containment,
- reduced metric roles,
- angular jacket,
- packet diagnostics versus plant diagnostics,
- demanded-source ledger,
- standing support versus active-service excess,
- reset residue and repeated operation,
- open physical gates.

### Design Review And Synthesis

Define higher-level reasoning tasks.

Likely modules:

- handoff failure diagnosis,
- burden-channel diagnosis,
- source-ledger interpretation,
- evidence sufficiency,
- claim classification,
- pass/fail/needs-evidence reviews,
- design tradeoff analysis.

### Claim Status Taxonomy

Use the same statuses from the design document unless there is a strong reason to revise them:

- established theory,
- established constraint,
- published speculative model,
- active-rail model,
- project hypothesis,
- open physical gate,
- fictional frame.

Each module should say which statuses it is allowed to teach.

### Curriculum Outputs

This phase should create:

- a module map,
- learning objectives for each module,
- prerequisite relationships,
- reference anchors,
- claim-status rules,
- question-type recommendations per module,
- activity-surface recommendations per module,
- question quality rubric and authoring scorecard,
- difficulty calibration rules,
- source and reference requirements,
- a small set of example questions per module.

### Phase 2 Done When

- The full curriculum structure exists.
- Every module has learning objectives.
- Claim-status rules are clear enough for content authors.
- A quality rubric exists and can be used to score, accept, rewrite, or reject draft questions.
- Difficulty levels are calibrated by reasoning demand.
- Reference anchors are assigned to established and literature modules.
- Active-rail modules distinguish definitions, hypotheses, and open gates.
- There is enough structure to begin writing questions at scale.

## Phase 3: Content Population

Write, review, and refine the actual question bank.

This phase should start small and grow deliberately. The first target should be a useful release, not exhaustive coverage.

### Population Order

Populate in this order:

1. Established foundations across the full theory spine, not just GR.
2. Claim-status classification questions that separate general theory, paper
   theory, project application, and project state.
3. Core active-rail vocabulary and chronology.
4. Source-ledger and plant-diagnostic questions.
5. Published warp/wormhole context.
6. Design-review scenarios.
7. Advanced synthesis questions.

This order keeps the system useful while preventing the bank from becoming
project-heavy before learners have the broader theory needed to judge source,
vacuum, semiclassical, and high-energy claims.

### Initial Content Targets

A good first release should have:

- 150 to 250 total questions,
- at least 30 claim-classification questions,
- at least 40 non-ordinary activities across drag-fill, sequencing, matching, and classification,
- at least 90 established general-theory/foundation questions, distributed
  across GR/differential geometry, quantum mechanics, QFT/semiclassical gravity,
  Casimir/vacuum physics, effective field theory, source-model literacy, and
  bounded string-theory context,
- at least 40 paper-theory questions drawn only from fully accessible public papers,
- at least 35 active-rail architecture questions,
- at least 25 design-review questions,
- no more than roughly 15 to 25 project-state or revision-sensitive questions in the first release, all flagged so they can be excluded.

These numbers are targets, not sacred requirements.

Population should happen in numerous vetted passes, not one bulk dump. Each
pass should add a coherent slice, run the automated validator, then perform a
human rubric pass for prompt clarity, difficulty fit, source support, answer
quality, distractor quality, and explanation depth.

### Content Quality Rules

Each question should have:

- one clear learning purpose,
- one claim status,
- one question context: general theory, paper theory, project application, or project state,
- a teaching-quality explanation,
- explanation depth matched to difficulty: core items can be concise, intermediate items should explain the main implication or misconception, and advanced items should teach the reasoning path, boundary, and why attractive wrong answers fail,
- a boundary note when project-specific or speculative,
- reference support when established or literature-based,
- source links when project documents, repository files, papers, or run artifacts are relevant,
- provisional wording for project-specific claims that could change as the architecture matures,
- plausible distractors,
- tags that make review and filtering useful.

Avoid:

- learner-facing questions about the quiz system, scoring policy, label policy, or curriculum governance,
- trivia for its own sake,
- questions that only test wording memorization,
- overlong prompts,
- false certainty,
- unreviewed claims presented as facts,
- too many advanced questions before the core bank is strong.

### Review Process

Use a lightweight review flow:

- draft,
- content reviewed,
- physics/reference reviewed,
- project-model reviewed,
- approved.

Not every question needs every review type. Established-theory and literature questions need reference review. Project-specific questions need project-model review. Mixed questions need both.

### Phase 3 Done When

- The first substantial question bank exists.
- It is no longer just a seed bank: it is large enough that every major filter
  combination still has useful material.
- Questions cover all major tracks.
- The sample bank contains no quiz-meta questions.
- Claim-status classification is well represented.
- Drag-fill and sequencing are used where typing would be annoying.
- Explanations teach rather than merely reveal answers.
- The first release can function as both a study tool and an active-rail architecture review aid.

## Phase 4: Rail Service Terminal

Build the active-rail operator simulator as its own first-class product surface.
This phase is not an extension of the question-bank renderer. It should follow
`SERVICE_TRAINER_DESIGN.md`.

### Design Requirements

The design checkpoint must exist before implementation changes.

Required design artifacts:

- terminal information architecture,
- operational work-order model,
- line state model,
- visual simulation model,
- subsystem visual-state model,
- continuous control model,
- constraint/guard model,
- telemetry definitions,
- failure taxonomy,
- event/debrief model,
- visual direction for the operations terminal.

### Implementation Subphases

1. Remove quiz-shell dependency.
   - Selecting the service terminal should remove quiz filters, report panels,
     question counts, study/timed controls, and card-stack styling.
   - The terminal should have a separate shell and visual language.
2. Extract simulator data and logic.
   - Move work orders, line controls, failure rules, and update functions into
     dedicated service-trainer modules.
   - Keep the React component responsible for rendering and dispatching control
     changes, not for holding all simulator rules inline.
3. Build the terminal simulation surface.
   - Top status bar.
   - Live line simulation with rail corridor, packet, support envelope,
     source/ledger channel, endpoint/catch window, reset path, and localized
     subsystem warnings.
   - Instrumentation with bands and recent-change cues.
   - Persistent operator controls for support, source, endpoint, release,
     decompression, reset, hold, abort, and secure.
   - Secondary constraint, advisory, trace, and debrief inspection.
4. Make the run feel alive.
   - Advance clock during active states.
   - Evolve telemetry over time.
   - Evolve visual subsystem state over time.
   - Emit alarms once per condition.
   - Let operator timing matter.
   - Support hold, resume, abort, reset, and secure.
5. Add meaningful first failure modes.
   - Support gap.
   - Source overdraw.
   - Endpoint mismatch.
   - Timing violation.
   - Fade-before-catch refusal or alarm.
   - Reset contamination.
   - Stability lockout.

### First Acceptance Target

The first acceptable terminal should let the learner:

- accept a work order,
- bring support/source/endpoint/reset controls into operating margins,
- arm or hold the line from a persistent authority control,
- manage carry, catch, fade, decompression, and reset through control surfaces,
- monitor visible subsystem state,
- see controls constrained, guarded, or resisted by subsystem state,
- respond to warnings,
- trigger and recover from at least four failures,
- secure or abort the line,
- read a terse operational debrief.

It should not look like a quiz page. It should look like an active-rail service
station. Its central line view should not be only a progress bar.

### Phase 4 Done When

- Rail Service Terminal has a separate shell and style from the Qualification
  Board.
- Service trainer data and simulation logic live outside the React rendering
  component.
- The terminal uses work orders, live controls, constraints, telemetry, events, and
  failure rules instead of question-bank data.
- The terminal supports an evolving single-line run with visible subsystem
  state.
- The event log and debrief explain outcomes in operator language.
- Validation, smoke tests, and production build pass.

## Phase 5: Service Terminal Redesign

The shared suite shell exists and the Service Terminal has a separate prototype
shell, but the terminal still needs a real redesign pass. This phase replaces
the prototype's command-panel feel with a first-viewport operator station and a
state-derived graphic line readout.

Design gate: update `SERVICE_TRAINER_DESIGN.md`, `DESIGN.md`, and
`INTERFACE_ARCHITECTURE.md` before code changes. Do not implement another
terminal iteration by adding panels or renaming labels around the old command
model.

### Design Requirements

- Qualification Board remains a learning-board product.
- Rail Service Terminal remains an operations product.
- The simulator centers a live line graphic, not a button grid, prompt panel,
  work-order list, phase stepper, or themed progress bar.
- Work-order browsing and fault-injection setup are secondary drawers or setup
  surfaces, not the main driver of the run.
- The first viewport shows suite/status, line graphic, instrumentation, and core
  controls without requiring scrolling for ordinary operation.
- The line graphic shows packet, support envelope, source/ledger channel,
  endpoint/catch aperture, timing shear, reset residue, constraint posture, and
  localized subsystem warnings.
- The line graphic uses the spacetime visual grammar from
  `SERVICE_TRAINER_DESIGN.md`: packet worldline/wake, endpoint optics,
  causal-access risk, backreaction/constraint posture, horizon-risk guard,
  chronology guard, and reset residue all have explicit state drivers and truth
  boundaries.
- All graphic elements inside the line are state-derived. Static squiggles,
  decorative warning triangles, generic stickers, and duplicate telemetry cards
  are explicitly out of scope.
- Numeric telemetry stays in the instrumentation cluster. The line viewport
  encodes state through geometry, motion, opacity, thickness, aperture shape,
  source saturation, residue haze, shear, and localized deformation.
- Operator input uses persistent control surfaces: support drive/trim,
  source-ledger closure, endpoint sync, catch aperture, carry drive, fade,
  decompression, reset purge, hold/resume, abort/recovery, and secure.
- Constraints and guards attach to controls and affected subsystems through
  range clipping, resistance, warning lamps, or visual subsystem changes.
- Autopilot and supervisor modes are allowed as visible training aids. They
  manipulate or point to real controls and leave traces; they are not solve
  buttons or quiz prompts.
- Randomness is seeded, bounded, replayable, and visible through subsystem
  changes before or during alarm state.

### Implementation Subphases

1. Clean the primary layout.
   - Collapse work orders into compact assignment/setup controls.
   - Remove the left-rail list as the main driver of service.
   - Remove the command stack and phase-chip stepper from the primary
     interaction model.
   - Fit line graphic, telemetry, and core controls in the first viewport.
2. Rebuild the line graphic as state-derived SVG/CSS.
   - Keep packet and endpoint markers inside the viewport.
   - Replace static curves and triangles with derived support, source, timing,
     endpoint, reset, and constraint layers.
   - Add endpoint optics/ray-bundle behavior and packet worldline/wake before
     adding any purely decorative effects.
   - Add backreaction/constraint posture and causal-risk overlays as cautious
     risk readouts, not as solved physics.
   - Remove embedded numeric cards and duplicate text blocks from the line
     graphic.
   - Make standby, support, carry, catch, fade, reset, hold, abort, recovery,
     and secure visually distinct.
3. Rework operator controls.
   - Controls become persistent line instruments, not next-action buttons.
   - Controls visibly change the line and subsystem state.
   - Guards, clipped ranges, and warnings explain constraints without turning
     the UI into a disabled button grid.
4. Add supervised operation.
   - Add a visible autopilot/supervisor mode that moves or highlights the same
     controls available to the operator.
   - Add bounded seeded perturbations to source load, endpoint drift, support,
     reset residue, and stability.
   - Make faults visible before or during alarm state.
5. Tune and review.
   - Manually run ordinary, cautious, risky, hold, abort, and recovery paths.
   - Confirm the visual state explains the run without relying on paragraphs.
   - Confirm debrief and trace remain useful secondary surfaces.

### Phase 5 Done When

- The first screen has a coherent shared training-suite frame.
- Switching between Qualification Board and Rail Service Terminal feels like
  moving between sibling products.
- The Service Terminal's center area is an actual graphic simulation, not a
  progress strip, static schematic, duplicate telemetry cluster, or quiz prompt
  panel.
- The first viewport shows status, live line, telemetry, and core controls
  without forcing the operator to scroll for ordinary service.
- Secondary inspection surfaces are bounded, drawer-based, tabbed, or below the
  primary operating view.
- A learner can tell what to operate from the line viewport, instrumentation,
  controls, and supervisor hints without reading documentation.
- The terminal no longer uses a command stack, phase-chip progression, or
  work-order list as the core interaction model.
- The terminal viewport feels like a graphic readout of active-rail service
  evolution: packet motion, support field, source flow, catch aperture, timing
  shear, reset residue, constraints, and failure localization change with state.

## Keep It Simple Rules

- Prefer local imported question-bank files before adding a database.
- Prefer local progress storage before user accounts.
- Prefer clear reports before elaborate analytics.
- Prefer a few excellent question types before many shallow ones.
- Prefer readable design before visual spectacle.
- Prefer content quality over content volume.

## Prototype Checkpoint

The initial static prototype is now a checkpoint, not the target architecture. It proves:

- static-file operation,
- separated sample bank,
- basic filters,
- basic modes,
- basic activity types,
- basic scoring by module and claim status.

## Current Implementation State

The current Vite/React app provides the Qualification Board infrastructure and
an early Rail Service Terminal shell:

- Vite/React app shell exists.
- KaTeX is installed and renders math tokens.
- Local question-bank modules replaced inline browser globals.
- A renderer/grader registry exists.
- Standard quiz, symbol-fill, sequence, matching, and claim-classification
  renderers exist.
- Workspace rail and distinct Qualification Board workspaces exist for Mixed
  Quiz, Boundary Board, Symbol Lab, and Design Review.
- The Rail Service Terminal now opens as a separate top-level operator shell
  instead of a quiz workspace.
- Multi-select facets exist for tracks, modules, difficulty, and claim status.
- Question context exists as a separate facet from claim status, with general theory, paper theory, project application, and project state lanes.
- Paper-theory prompts now require publication-year/citation anchoring rather than vague "the study" wording.
- The bank has reached 200 validated questions after major expansion passes
  across broad foundations, advanced reasoning, explanation quality,
  distractor quality, and cross-domain theory.
- Established general theory has been promoted as the durable core layer; it now includes a broader foundation spine across GR, quantum basics, QFT/vacuum/Casimir physics, semiclassical gravity, effective field theory, source-model literacy, and bounded string-theory context. Project-state and revision-sensitive content should remain a smaller flagged layer.
- Difficulty calibration has had manual correction and follow-up passes: the bank now has a stronger advanced slice, but it still needs more reviewed depth before it should be called a full curriculum.
- Count controls now support small drills, medium reviews, large reviews, and all matching questions.
- Per-attempt presentation order is randomized for standard choices, drag-fill tokens, matching prompts/options, classification statements, and sequence items.
- Sequence activities now avoid starting in canonical answer order and use draggable rows with keyboard fallback.
- Workspace smoke test renders all current workspaces.
- Bank validation and production build commands work.
- The initial Rail Service Terminal has a separate shell, work-order selection,
  line state, telemetry, legacy authority-button controls, interlock reasons,
  inspection panels, event feed, debrief panel, and separate service-terminal
  data/simulator modules.
- The first Phase 5 pass adds a shared suite shell and moves the terminal away
  from the Qualification Board shell, but it is not yet an acceptable service
  simulation. The current implementation still reads too much like a
  command-stack trainer with a stylized progress rail. The latest design pass
  makes the required correction explicit: the next code pass must demote
  work-order selection, remove the command-stack interaction, fit ordinary
  operation into the first viewport, and replace static/ornamental visuals with
  state-derived active-rail subsystem graphics.

What is still missing:

- workspace-specific scoring panels,
- Service Terminal visual simulation rewrite: support/source/endpoint/reset
  subsystem visualization through real graphic layers, trend cues, localized
  subsystem warnings, and work-order language that reads like operations rather
  than puzzle prompts,
- Service Terminal interaction rewrite: replace next-action buttons and phase
  chips with persistent operator controls and constraint feedback,
- deeper Rail Service Terminal work orders, replay, incident review, and more
  richly tuned failure/recovery behavior,
- a fuller Ledger Reader workspace,
- stronger question validation for references, source links, difficulty fit, and meta-question bans,
- larger vetted curriculum banks with deeper coverage inside each broad
  foundation domain,
- richer answer/explanation writing, especially for intermediate and advanced questions,
- better mode separation between study, drill, qualification, and project-internal review.

The Qualification Board architecture and validation gates are good enough for
continued curriculum work. The Rail Service Terminal has an independent shell
and simulation model, but its visual/interaction design still needs a true
service-terminal rewrite before it should be treated as a complete simulator.

## Likely Next Infrastructure Milestone

The next milestone is Phase 5 service-terminal redesign:

- collapse work-order browsing into secondary setup instead of the main left
  rail;
- remove the command stack and phase-chip progression from the primary
  interaction model;
- fit the live line, telemetry, supervisor/autopilot affordance, and core
  controls in the first viewport;
- replace static squiggles, decorative warning triangles, and duplicate
  telemetry cards with state-derived graphic layers for support, source/ledger,
  endpoint/catch, timing shear, reset residue, constraint posture, and failure
  localization;
- add persistent line controls that directly affect subsystem state;
- add bounded seeded perturbations and visible autopilot/supervisor behavior;
- make hold, abort, recovery, secure, and reuse-blocked states visually
  distinct;
- keep secondary inspection panels subordinate to the live simulation;
- expand terminal-specific data without using quiz questions as the simulator
  content model;
- keep validation, smoke tests, and production builds healthy.

This milestone should prove the system can teach active-rail operation through
interactive practice, not merely render more content.

## Roadmap Summary

Phase 1 builds the quiz machine. Phase 2 designs the course. Phase 3 fills it
with high-quality questions. Phase 4 builds the Rail Service Terminal as a
separate operator simulator. Phase 5 makes the suite feel unified and makes the
terminal feel like an operator station.

The system should stay friendly and flexible, but each surface must behave like
what it claims to be. The Qualification Board teaches claim boundaries and
theory. The Rail Service Terminal trains active-rail operation through service
state, live controls, constraints, alarms, and consequences.
