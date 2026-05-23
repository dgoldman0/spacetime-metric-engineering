# Active-Rail Quiz System Design

This file is a design document, not an implementation roadmap. It defines what the full quiz system should become before we decide how to build it. Detailed implementation-facing notes live in companion documents:

- `INTERFACE_ARCHITECTURE.md` for screen structure, specialized activity surfaces, and math rendering.
- `ASSESSMENT_MODEL.md` for scoring, mastery, grading dimensions, and reports.

The original HTML prototype proves that a static active-rail quiz can work: it has a question bank, filters, explanations, KaTeX rendering, and mixed question types. The first infrastructure prototype in this folder proves local data separation and basic grading. The next system should now move to a lightweight dynamic frontend app so the interface can support specialized activity surfaces, richer state, proper math rendering, and grading profiles without turning into one oversized script file. It should teach established theory, published speculative-relativity context, and project-specific active-rail architecture while making the boundaries between those categories impossible to miss.

The guiding phrase:

> A future engineering program that knows exactly which parts are textbook, which parts are literature context, which parts are active-rail design language, and which parts are still open gates.

## Product Intent

The quiz should feel like an engineering qualification from a future active-rail service academy, but it must remain honest by construction.

It should do four jobs at once:

1. Teach the established theory needed to reason about the design.
2. Teach the active-rail architecture as currently understood.
3. Train users to separate established understanding from project-specific ideas.
4. Help the project team study, audit, and sharpen the design itself.

The fictional framing is allowed to be fun. The physics boundary is not allowed to be fuzzy.

## Non-Goals

- Do not present active-rail concepts as established physics unless they are actually established.
- Do not imply that a demanded-source ledger is a completed matter model.
- Do not let "engineering academy" styling hide unresolved physical gates.
- Do not require users to type LaTeX, equation syntax, or long symbolic answers.
- Do not make the first version a giant content dump with no epistemic structure.
- Do not add a backend, database, accounts, or server-side authoring system until the frontend learning model proves itself.

## Core Design Principle: Claim Separation

Every question, explanation, module, and score report should expose the kind of claim being tested.

Suggested epistemic classes:

| Class | Meaning | Display Rule |
| --- | --- | --- |
| Established theory | Standard GR, differential geometry, stress-energy, ADM language, QFT-in-curved-spacetime basics, or broadly accepted mathematical machinery. | Show as "Established". Include references or canonical source notes. |
| Established constraint | Known limits, no-go pressures, energy-condition issues, quantum inequality constraints, topological censorship, backreaction concerns. | Show as "Established constraint". Explain what it limits and what it does not by itself rule out. |
| Published speculative model | Alcubierre-style warp metrics, traversable wormhole models, Natario-style metrics, or other published speculative-relativity constructs. | Show as "Literature model". Do not treat as demonstrated engineering. |
| Project definition | Active-rail vocabulary, decomposition, service chronology, support/carry/catch/fade/decompress/reset roles, demanded-source ledgers. | Show as "Active-rail model". State that this is project terminology or design structure. |
| Project hypothesis | A proposed active-rail design principle, burden-routing strategy, closure mechanism, or source-family conjecture. | Show as "Project hypothesis". Include what evidence would strengthen or falsify it. |
| Open physical gate | A required unresolved demonstration: matter closure, semiclassical response, stability, reset residue, repeated operation, causality, realizability. | Show as "Open gate". Score users on recognizing that it is not solved. |
| Fictional frame | Course names, certification titles, future institutional flavor. | Show in UI flavor only. Never use as evidence. |

The system should repeatedly ask users to classify claims. This should be a first-class skill, not an occasional warning.

## Project-State Content Policy

Questions about project materials, project state, current work products, internal runs, active hypotheses, and open questions are allowed, but they must never be mixed into the general curriculum invisibly.

These questions should be treated as optional content bands that can be included or excluded selectively.

Required rules:

- Any item based on current project materials must be clearly marked.
- Any item about project state must be clearly marked as time-sensitive or revision-sensitive.
- Any item about open questions must be clearly marked as an open question, not as settled knowledge.
- Any item about a project hypothesis must identify what would count as supporting evidence, missing evidence, or falsifying pressure.
- Study and quiz modes must allow users to exclude project-state, project-materials, and open-question items.
- Qualification modes should default to excluding revision-sensitive project-state items unless the qualification is explicitly a project-internal review.
- Established-theory and literature-context modules should not depend on project-state questions.

Suggested optional content flags:

| Flag | Meaning | Default Treatment |
| --- | --- | --- |
| `project_material` | Based on project documents, harness outputs, ledgers, reports, or repository artifacts. | Excludable. Off by default for general learners. |
| `project_state` | Describes what the project currently thinks, has implemented, has tested, or has not yet tested. | Excludable. Off by default for stable quizzes. |
| `open_question` | Tests recognition of unresolved questions, missing evidence, or future work. | Excludable, but useful in design-review mode. |
| `revision_sensitive` | Likely to change as the architecture or evidence changes. | Off by default outside project-internal review. |

This does not mean those questions are bad. They are valuable for project-internal study and architecture review. The rule is that they must be visible, filterable, and never allowed to masquerade as stable curriculum.

## Voice And Frame

The experience can be playful and immersive:

- "Active-Rail Service Engineering Board"
- "Plant Qualification Review"
- "Packet Safety Practicum"
- "Source Ledger Lab"
- "Release Handoff Simulator"
- "Reset Debt Audit"

But every immersive element should be paired with disciplined language. The tone should be:

- confident about definitions,
- careful about physics status,
- precise about evidence,
- warm enough to make study feel alive,
- never falsely triumphant.

A good tone model:

> You are in a future training simulator, but the simulator has a very strict footnote department.

## Application Architecture

The next implementation target should be a small client-side app, not a larger platform.

Recommended shape:

- Vite + React for the dynamic frontend.
- Local question-bank modules for now.
- KaTeX as an installed dependency for math rendering.
- Componentized activity surfaces.
- A renderer/grader registry by question or activity type.
- Local browser state for session progress.
- No backend, database, user accounts, or network-required data flow in the first dynamic version.

This is a pivot from "open one HTML file" to "run a lightweight local frontend app." The tradeoff is worthwhile because the system needs richer interfaces than a static file should carry.

The dynamic app should still remain local-first. It should be easy to run, easy to inspect, and easy to replace question banks without deploying infrastructure.

## Curriculum Architecture

The content should be organized as a curriculum rather than one large bag of trivia.

### Track A: Established Foundations

Purpose: give users the real theory needed to understand what active-rail claims are borrowing from.

Candidate modules:

- Spacetime, metrics, signatures, and causal character.
- Stress-energy tensor and observer projections.
- Energy conditions: null, weak, dominant, strong.
- ADM split: lapse, shift, spatial metric, extrinsic curvature.
- Constraint equations and evolution language.
- Null contractions and source-channel diagnostics.
- Basics of QFT in curved spacetime.
- Semiclassical stress tensor, RSET, and backreaction.
- Causality protection, horizons, and chronology concerns.

### Track B: Published Warp And Wormhole Context

Purpose: situate the project in the known speculative-relativity landscape.

Candidate modules:

- Morris-Thorne traversable wormholes.
- Alcubierre warp metric.
- Natario-style warp concepts.
- Visser-style Lorentzian wormhole analysis.
- Ford-Roman quantum inequality constraints.
- Topological censorship and global causal constraints.
- Energy-condition violations in warp and wormhole settings.
- Known issues with horizons, signals, control, and backreaction.

These modules should not be written as "how to build a warp drive." They should be written as "what the literature explored, what it showed, and what remained physically problematic."

### Track C: Active-Rail Architecture

Purpose: teach the project-specific architecture as a coherent engineering language.

Candidate modules:

- Packet-centered service model.
- Rail as operating plant rather than passenger-owned field.
- Service chronology: support, carry, catch/rematch, fade, decompress, reset.
- Reduced metric roles: service coordinate, radial coordinate, lapse, radial shift, radial metric support, angular sector.
- Support containment: carrying flow inside support envelope.
- Packet norm versus plant burden.
- Angular jacket and pressure/tension bookkeeping.
- Demanded-source ledger: what it identifies and what it does not prove.
- Standing support versus active-service excess.
- Source roles: support, edge shaping, actuation, reset.
- Reset residue and multi-cycle accumulation.

### Track D: Design Review And Failure Analysis

Purpose: turn the quiz into an engineering study tool.

Candidate modules:

- Handoff order failures.
- Clean packet result with dirty plant channels.
- Burden migration from packet to support edge.
- Angular pressure hiding behind good timing.
- Source-ledger interpretation errors.
- Reset debt and repeated-operation failure.
- Misclassified claims: project vocabulary mistaken for established theory.
- Incomplete evidence packages.

### Track E: Synthesis And Qualification

Purpose: simulate higher-level review.

Candidate modules:

- Service case files.
- Ledger table interpretation.
- "Pass, fail, or needs evidence" reviews.
- Evidence sufficiency.
- Design tradeoff diagnosis.
- Claim-boundary defense.
- Oral-exam style justification.

## Important Reference Anchors

The content system should maintain a reference library. Each reference should be attached to specific claims, not just listed globally.

Candidate reference anchors to verify and formalize during content authoring:

- ADM formulation: Arnowitt, Deser, Misner.
- Standard GR texts: Misner, Thorne, Wheeler; Wald.
- Traversable wormholes: Morris and Thorne.
- Lorentzian wormholes and exotic matter analysis: Visser.
- Warp metric literature: Alcubierre; Natario.
- Quantum inequality constraints: Ford and Roman; later Fewster-style treatments.
- QFT in curved spacetime: Birrell and Davies; Wald.
- Chronology protection: Hawking.
- Topological censorship: Friedman, Schleich, Witt; related later work.
- Numerical relativity and ADM/BSSN learning references where useful.

Design rule: a reference entry should say which exact claim it supports. A source should never be used as a decorative bibliography item.

## Question Types

The old prototype has multiple choice, select-all, true/false, and typed fill-in-the-blank. The full system should keep those where useful, but add richer formats.

Question types should not all be forced into the same generic card interface. A shared question shell is useful for metadata, claim-status display, explanations, and review controls, but the main work area should be specialized by activity type. Boundary classification, source-ledger interpretation, sequencing, symbol practice, case-file review, and ordinary multiple choice have different educational shapes.

### Multiple Choice

Use for precise concepts, definitions, and contrastive misconceptions.

Good use:

- "Which statement is established ADM language?"
- "Which interpretation overclaims what the demanded-source ledger proves?"

### Select All

Use for multi-channel diagnostics and evidence packages.

Good use:

- "Which monitors are needed before accepting this service schedule?"
- "Which claims are project-specific rather than established theory?"

### Drag-Fill Word Bank

This should replace typed fill-in-the-blank as the default fill mode.

Requirements:

- Users drag rendered text or equation tokens into blanks.
- Users can also tap/click a token and then tap/click a blank.
- Equations render through a real LaTeX rendering library, preferably KaTeX for the dynamic frontend.
- Visual examples should appear as rendered expressions, not pseudo-plain-text strings such as `gamma_OmegaOmega`, `T_mn k^m k^n`, or `G_mn/(8 pi)`.
- Users never need to type LaTeX.
- Tokens can have aliases internally, but the visible task is token placement.
- On mobile, the interaction must work without precision dragging.
- Keyboard users need a non-drag path: focus token, choose blank, place token.
- Each blank can declare whether tokens are reusable.
- Distractor tokens should represent real misconceptions, not random noise.

This mode is especially important for symbolic expressions and active-rail vocabulary.

### Sequencing

Use for service chronology.

Examples:

- Arrange support, carry, catch/rematch, fade, decompress, reset.
- Place catch before shift fade and support relaxation.
- Order evidence checks in a design review.

### Matching

Use for concept-to-status and symbol-to-role practice.

Examples:

- Match `alpha` to lapse.
- Match "quantum inequality" to established constraint.
- Match "angular jacket" to project model.

### Diagram Labeling

Use visual schematics for active-rail structure.

Examples:

- Label packet, support envelope, radial shift region, angular sector.
- Identify where a support-containment violation occurs.
- Mark the catch/rematch region on a service profile.

### Ledger Interpretation

Use tables or plots from source diagnostics.

Examples:

- Identify which channel carries negative Eulerian density.
- Distinguish standing burden from active-service excess.
- Decide whether a clean packet norm is enough evidence.

### Design Review Case File

Use a compact scenario with multiple artifacts.

Artifacts might include:

- service timeline,
- packet norm trace,
- support envelope plot,
- source ledger summary,
- reset residue measure,
- claim-status notes.

The user answers:

- pass/fail/needs evidence,
- which risk channel dominates,
- which claim is overclassified,
- what evidence is missing.

### Claim Classification

This should appear everywhere.

Examples:

- "Classify this statement: The radial shift supplies support-contained carrying flow."
- "Classify this statement: The null energy condition constrains `T_mn k^m k^n`."
- "Classify this statement: The rail can be reset without source-history accumulation."

The correct answer may be "project hypothesis" or "open gate", not just true or false.

## Math Rendering

Mathematical notation is central to this system and should be treated as first-class content.

Requirements:

- Use a real LaTeX rendering library for displayed and inline math. KaTeX is the preferred default for the dynamic frontend; MathJax is acceptable if later needs require it.
- Store canonical math as LaTeX in the question data, for example `G_{\mu\nu}/(8\pi)`.
- Render equations consistently in prompts, choices, drag-fill tokens, explanations, references, reports, and review material.
- Keep plain-text aliases only for search, accessibility labels, validation, and internal matching.
- Do not ask learners to type LaTeX unless an advanced authoring or expert mode explicitly calls for it.
- Provide accessible text labels for rendered math tokens.

The current infrastructure prototype uses simple text-like math tokens. That is acceptable only as a first-pass placeholder, not as the intended design.

## Question Data Model

The question bank should move out of inline JavaScript into structured data.

Every question should include:

- stable id,
- title or short label,
- question type,
- module,
- curriculum track,
- difficulty,
- epistemic class,
- project component tags,
- established-theory dependency tags,
- optional content flags,
- prompt,
- prompt parts or render blocks,
- answer representation,
- distractors,
- explanation,
- claim-boundary explanation,
- references,
- misconception targets,
- authoring status,
- review status,
- version.

Example shape:

```yaml
id: arq.dragfill.source_ledger.001
type: drag_fill
track: active_rail_architecture
module: source_ledger
difficulty: core
epistemic_class: project_definition
component_tags:
  - demanded_source_ledger
  - source_accounting
theory_dependencies:
  - einstein_equation
  - stress_energy_tensor
content_flags: []
prompt: "For a prescribed metric in units G = c = 1, the demanded-source ledger records {source_term}."
tokens:
  - id: einstein_tensor_over_8pi
    render_kind: latex
    render: "G_{\\mu\\nu}/(8\\pi)"
  - id: beta_over_alpha
    render_kind: latex
    render: "\\beta^\\ell/\\alpha"
  - id: packet_norm
    render_kind: latex
    render: "n_{\\mathrm{pkt}}"
blanks:
  - id: source_term
    accepts:
      - einstein_tensor_over_8pi
answer:
  source_term: einstein_tensor_over_8pi
explanation:
  correct: "Einstein's equation gives G_mn = 8 pi T_mn in these units, so the demanded source is G_mn/(8 pi)."
  boundary: "This is source accounting for a prescribed geometry. It is not a completed matter model."
references:
  - id: einstein_equation_standard_gr
    supports: "Relation between Einstein tensor and stress-energy tensor."
misconception_targets:
  - ledger_as_physical_source
  - packet_diagnostic_as_source_diagnostic
status: draft
review_status: needs_physics_review
```

## Explanation Design

Every explanation should have a predictable structure.

Recommended fields:

- **Answer:** what was correct.
- **Why:** concise technical reason.
- **Boundary:** what kind of claim this is.
- **Related Established Theory:** if applicable.
- **Project-Specific Meaning:** if applicable.
- **Open Gate:** if the question touches unresolved physics.
- **References:** source anchors for established or literature claims.

For example:

```text
Answer: The demanded-source ledger records G_mn/(8 pi).
Why: In units G = c = 1, Einstein's equation gives G_mn = 8 pi T_mn.
Boundary: This is established GR applied as project source accounting.
Project-Specific Meaning: The ledger identifies what the prescribed active-rail geometry demands.
Open Gate: It does not prove that a realizable matter sector exists.
```

## Visual And Interaction Design

The current prototype looks like a useful dark demo. The full system should look more like a refined engineering console than a novelty quiz page.

The first infrastructure prototype is intentionally too simple. It proves data loading, filters, a few interactions, and basic grading. It should not become the final interaction model by accretion. The full system needs richer activity surfaces and mode-specific layouts.

Design direction:

- cleaner layout,
- better typography,
- less gradient-heavy styling,
- more readable contrast,
- clearer module navigation,
- compact but polished cards,
- visible claim-status badges,
- schematic visuals where they teach something,
- responsive layout that works on tablet and mobile.

Suggested aesthetic:

- institutional future lab,
- quiet technical confidence,
- instrument-panel clarity,
- color used for meaning rather than decoration.

Avoid:

- one-note blue/purple sci-fi styling,
- giant decorative hero pages,
- overly rounded toy-like cards,
- long paragraphs inside cramped cards,
- badges that look fun but do not communicate status,
- hiding important epistemic caveats in small text.

Claim class should be visible through a combination of label, color, and icon or shape. Color alone is not enough.

Possible visual language:

- Established theory: cool neutral or deep green.
- Established constraint: amber.
- Published speculative model: blue.
- Active-rail model: cyan or teal.
- Project hypothesis: violet or magenta, used sparingly.
- Open gate: red/orange warning style.
- Fictional frame: subtle neutral styling, never source-like.

See `INTERFACE_ARCHITECTURE.md` for the intended multi-surface interface model.

## Main User Experience

The first screen should be the learning tool, not a marketing page.

Core surfaces:

- module browser,
- active quiz pane,
- claim-status filter,
- optional-content filter,
- learning mode selector,
- progress and mastery view,
- review queue,
- reference drawer,
- design-review simulator.

The system should support both casual and serious use:

- quick drill,
- focused module study,
- mixed qualification exam,
- claim-boundary practice,
- source-ledger lab,
- design review simulation,
- missed-question review,
- print/export for offline study.

The interface should support several classes of learning activity:

- ordinary question answering,
- claim-boundary classification,
- symbolic/token practice,
- service chronology and timeline work,
- source-ledger/table interpretation,
- design-review case files,
- review and remediation.

These can share navigation, metadata, filters, and scoring services, but they should not all share one cramped card layout.

## Learning Modes

### Study Mode

Immediate explanations after each answer. Designed for learning.

### Drill Mode

Short randomized sets. Fast feedback. Good for vocabulary, equations, and claim classification.

### Qualification Mode

Exam-like session. Feedback delayed until submission. Scores by module and epistemic class.

### Design Review Mode

Scenario-based. Users inspect a service case and decide what passes, what fails, and what evidence is missing.

### Boundary Mode

Focused on separating established theory, literature context, project model, project hypothesis, and open gates.

### Source Ledger Lab

Questions revolve around tables, plots, projections, burden channels, standing support, and active-service excess.

## Scoring Model

The score should not be a single percent only.

Useful score dimensions:

- concept accuracy,
- claim-boundary accuracy,
- diagnostic reasoning,
- source-ledger interpretation,
- chronology/handoff accuracy,
- open-gate recognition,
- confidence calibration.

Qualification reports should say things like:

- "Strong on ADM vocabulary, weak on source-ledger boundary."
- "Correct active-rail chronology, but overclassified project hypotheses as established."
- "Good packet diagnostics, missed plant burden channels."

That is more valuable than "82%".

See `ASSESSMENT_MODEL.md` for the fuller assessment model. This design document intentionally keeps scoring principles short while the companion file defines dimensions, per-activity grading, reports, and qualification profiles.

## Authoring Standards

Question authors should follow these rules:

- Every established-theory question needs at least one reference anchor.
- Every project-specific question needs a boundary note.
- Every project-material, project-state, open-question, or revision-sensitive question needs an explicit content flag.
- Every speculative-literature question must distinguish metric construction from physical realizability.
- Every open-gate question should reward users for saying "not yet shown" when appropriate.
- Distractors should be plausible misunderstandings.
- Avoid trivia unless it supports conceptual fluency.
- Avoid "gotcha" wording.
- Equations should be rendered or tokenized, not typed by the learner.
- If a question combines established theory with active-rail vocabulary, the explanation must separate those parts.

## Content Review Workflow

Suggested authoring states:

- draft,
- internally reviewed,
- physics/reference reviewed,
- project-model reviewed,
- approved,
- deprecated.

Suggested review roles:

- content author,
- physics reviewer,
- project architecture reviewer,
- UX reviewer.

Review should check:

- correctness,
- claim classification,
- references,
- explanation quality,
- accessibility,
- whether the item teaches a real distinction.

## Relationship To The Existing Prototype

Keep:

- static prototype spirit,
- module filtering,
- difficulty filtering,
- mixed quiz generation,
- KaTeX rendering,
- explanations,
- print/export concept.

Replace or redesign:

- static-file architecture as the main implementation target,
- inline JavaScript question bank,
- typed fill-in-the-blank as the main symbolic-answer mode,
- single undifferentiated question voice,
- limited claim provenance,
- prototype visual style,
- single score percentage,
- lack of references,
- lack of scenario-based review.

The existing questions can seed the first active-rail model bank, but many need epistemic labels, boundary explanations, and reference metadata before they belong in the full system.

## Initial Folder Concept

This folder can eventually grow into:

```text
toolkit/active_rail_quiz_system/
  DESIGN.md
  ROADMAP.md
  INTERFACE_ARCHITECTURE.md
  ASSESSMENT_MODEL.md
  AUTHORING_GUIDE.md
  STYLE_GUIDE.md
  schemas/
    question.schema.json
    module.schema.json
    reference.schema.json
  question_banks/
    established_foundations/
    warp_wormhole_literature/
    active_rail_architecture/
    design_review_cases/
  prototypes/
  references/
  package.json
  vite.config.*
  src/
```

The static prototype can remain as a reference checkpoint or be retired once the dynamic app covers the same behavior.

## Open Design Questions

- What should the official product name be: Active-Rail Engineering Academy, Active-Rail Service Engineering Board, or something else?
- How strong should the future-program fiction be in the UI?
- Should qualification mode require claim-boundary accuracy to pass, even when concept answers are correct?
- Which references should be treated as mandatory anchors for the first content release?
- Which framework conventions should the dynamic frontend standardize on as it grows?
- Should project-internal run outputs and ledgers become quiz artifacts later?
- How should the system mark active-rail ideas that are later revised or retired?

## Design Summary

The full quiz system should be fun because it feels like training inside a real future engineering program. It should be useful because it teaches active-rail architecture as a system, not as loose vocabulary. It should be honest because every item exposes whether it is established theory, published speculative context, project-specific design language, a hypothesis, or an open physical gate.

The most important design requirement is not more questions. It is better epistemic architecture.
