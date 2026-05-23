# Active-Rail Quiz System Roadmap

This roadmap keeps the system modest in machinery but strong in usefulness. The goal is not to build a giant learning platform. The goal is to build a good, flexible quiz system that can teach active-rail architecture honestly, separate established theory from project-specific ideas, and make content authoring manageable.

The three main phases are:

1. Quiz infrastructure.
2. Curriculum design.
3. Content population.

## Phase 1: Quiz Infrastructure

Build the system that can render, grade, review, and organize questions.

This phase should produce a usable quiz application with a small sample bank. It does not need the final curriculum or a huge question set yet.

### Core Features

- Load question data from structured files instead of inline JavaScript.
- Support question filtering by module, difficulty, type, and claim status.
- Support study mode with immediate explanations.
- Support quiz mode with delayed grading.
- Support review of missed questions.
- Show clear claim-status badges on every question.
- Show explanations with answer, reason, boundary, and references when present.
- Render math and symbolic tokens cleanly.
- Work well on desktop, tablet, and mobile.

### Question Types

Implement only the types needed for a good first system:

- multiple choice,
- select all,
- true/false,
- drag-fill word bank,
- sequencing,
- matching.

Leave diagram labeling, case-file simulations, and ledger labs for later unless they become easy extensions.

### Drag-Fill Word Bank

This is the most important interaction upgrade from the prototype.

Requirements:

- Users place rendered word or equation tokens into blanks.
- Users can drag tokens.
- Users can also click/tap token then click/tap blank.
- Mobile interaction must feel natural.
- Keyboard use must be possible.
- Users should not need to type LaTeX.
- Tokens should support rendered text and rendered math.

### Grading

The grading system should be flexible but not overbuilt.

Track:

- total score,
- score by module,
- score by difficulty,
- score by question type,
- score by claim status,
- missed-question list.

Also track claim-boundary mistakes separately. For this project, confusing "established theory" with "active-rail model" is a meaningful learning failure, not just another wrong answer.

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
- `choices` or `tokens`,
- `answer`,
- `explanation`,
- `boundary_note`,
- `references`,
- `tags`.

Do not make the schema perfect before building. It should be strict enough to prevent messy content and simple enough to author by hand.

### User Experience

The first screen should be the quiz/study tool itself.

Required surfaces:

- mode selector,
- module selector,
- claim-status selector,
- question count selector,
- active quiz area,
- score/report area,
- missed-question review.

The design should feel like a polished engineering console: readable, calm, fast, and clear. It should look much better than the prototype, but the first implementation should avoid ornamental complexity.

### Phase 1 Done When

- A user can run a mixed quiz from structured data.
- At least six question types work.
- Drag-fill works without typing equations.
- Grading reports module and claim-status performance.
- Explanations clearly separate answer, reason, and epistemic boundary.
- The interface is pleasant enough that content authors will want to use it.

## Phase 2: Curriculum Design

Design what the system teaches before filling it with lots of questions.

This phase should produce the curriculum map, module list, claim taxonomy, and authoring rules. It should prevent the later content phase from becoming a pile of isolated trivia.

### Curriculum Tracks

Use three main teaching tracks plus one review/synthesis track.

1. Established foundations.
2. Published warp and wormhole context.
3. Active-rail architecture.
4. Design review and synthesis.

### Established Foundations

Define the real theory users need before they can reason well about active-rail ideas.

Likely modules:

- spacetime and metric basics,
- causal character and packet norm,
- stress-energy tensor,
- observer projections,
- energy conditions,
- ADM lapse and shift,
- constraint and evolution language,
- null contractions,
- semiclassical stress tensor,
- backreaction and quantum inequalities.

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
- a small set of example questions per module.

### Phase 2 Done When

- The full curriculum structure exists.
- Every module has learning objectives.
- Claim-status rules are clear enough for content authors.
- Reference anchors are assigned to established and literature modules.
- Active-rail modules distinguish definitions, hypotheses, and open gates.
- There is enough structure to begin writing questions at scale.

## Phase 3: Content Population

Write, review, and refine the actual question bank.

This phase should start small and grow deliberately. The first target should be a useful release, not exhaustive coverage.

### Population Order

Populate in this order:

1. Core active-rail vocabulary and chronology.
2. Claim-status classification questions.
3. Established foundations needed by the active-rail modules.
4. Source-ledger and plant-diagnostic questions.
5. Published warp/wormhole context.
6. Design-review scenarios.
7. Advanced synthesis questions.

This order lets the system become useful early while still building toward a serious curriculum.

### Initial Content Targets

A good first release could have:

- 150 to 250 total questions,
- at least 30 claim-classification questions,
- at least 30 drag-fill or sequencing questions,
- at least 20 established-foundation questions,
- at least 20 active-rail architecture questions,
- at least 10 literature-context questions,
- at least 10 design-review questions.

These numbers are targets, not sacred requirements.

### Content Quality Rules

Each question should have:

- one clear learning purpose,
- one claim status,
- a concise explanation,
- a boundary note when project-specific or speculative,
- reference support when established or literature-based,
- plausible distractors,
- tags that make review and filtering useful.

Avoid:

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
- Questions cover all major tracks.
- Claim-status classification is well represented.
- Drag-fill and sequencing are used where typing would be annoying.
- Explanations teach rather than merely reveal answers.
- The first release can function as both a study tool and an active-rail architecture review aid.

## Keep It Simple Rules

- Prefer structured JSON or YAML files before adding a database.
- Prefer local progress storage before user accounts.
- Prefer clear reports before elaborate analytics.
- Prefer a few excellent question types before many shallow ones.
- Prefer readable design before visual spectacle.
- Prefer content quality over content volume.

## Likely First Milestone

The first milestone should be a small but complete vertical slice:

- polished quiz interface,
- structured question loading,
- multiple choice,
- select all,
- drag-fill,
- sequencing,
- claim-status badges,
- grading by module and claim status,
- 20 to 30 sample questions,
- clear explanations with boundary notes.

This milestone should prove the system feels good before the project invests in large-scale content.

## Roadmap Summary

Phase 1 builds the quiz machine. Phase 2 designs the course. Phase 3 fills it with high-quality questions.

The system should stay friendly and flexible. Its special strength should be that it teaches active-rail ideas while constantly training the user to ask: is this established theory, literature context, project model, hypothesis, or open gate?
