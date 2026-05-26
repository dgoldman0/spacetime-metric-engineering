# Active-Rail Training Interface Architecture

This document describes the intended interface shape for the full training
suite. It exists because the first infrastructure prototype is useful but too
simple: it puts every activity into the same learning-board shell. That is fine
for proving quiz plumbing, but it does not support an operator simulator that
should feel like a rail engineer's terminal.

The full system has two top-level surfaces:

- **Qualification Board:** the quiz/study/assessment app.
- **Rail Service Terminal:** the active-rail line operations trainer.

Both can live in the same local React app for now. They should not share the
same visual shell.

## Core Principle

Use shared infrastructure, not one shared interface.

Shared infrastructure:

- local app runtime,
- top-level product switcher,
- common typography baseline,
- reusable low-level buttons where appropriate,
- validation/build tooling,
- source/reference infrastructure where useful.

Qualification Board owns:

- ordinary quiz cards,
- boundary classification workspace,
- symbol and equation token lab,
- matching matrix,
- source-ledger/table reader,
- design-review case file,
- filters,
- scoring,
- explanations,
- reference drawer,
- mastery and remediation view.

Rail Service Terminal owns:

- operations status bar,
- service manifest loader,
- line schematic,
- telemetry panels,
- command stack,
- procedure checklist,
- interlock display,
- alarm/event feed,
- run debrief.

This keeps the app coherent without flattening the service simulator into a quiz
workspace with badges.

## Qualification Board Screen Regions

### Command Bar

The command bar controls the active session:

- mode,
- timed-mode duration when relevant,
- explanation-review toggle when relevant,
- curriculum track,
- module,
- question type or activity type,
- claim status,
- optional content flags,
- count or session length,
- build/start action.

It should stay compact. It is a cockpit control strip, not a settings page.

Content filters should behave like facets, not single-choice dropdowns. Track, module, difficulty, claim status, question context, and activity type should support multiple selections. Empty selection means the facet is unrestricted. Use checkbox chips, compact tag groups, or checklist popovers rather than native single-select boxes for these controls. Count, workspace, and optional-content policy may remain single-choice because they control session shape rather than content inclusion. Count choices should cover small drills and larger review sets, not just one or two fixed sizes.

Timed quiz mode adds pacing controls without changing the content filters. The
command bar should expose a compact duration selector and an explanation-review
toggle. The timer should be visible in the workspace header, with a clear paused
state while explanations are open.

### Workspace

The workspace changes by activity type. It is the main learning surface.

Examples:

- a concise card stack for basic quiz items,
- a grid for claim classification,
- a table-plus-question layout for ledger interpretation,
- a dossier layout for design-review cases.

Timed quiz mode uses the same specialized renderers, but presents one activity
at a time. The active question should have a clear submit/review/next flow, a
visible item counter, and a timer state. If explanation review is enabled, the
workspace should show the explanation after submission and pause the timer until
the learner advances.

### Right Rail

The right rail should be context-sensitive.

Possible panels:

- score summary,
- claim-status legend,
- source and reference drawer,
- hint panel,
- current module objectives,
- missed-question queue,
- explanation panel after review.

On mobile, this should collapse under the workspace or become tabs.

### Review And Mastery Area

Review should feel like part of the tool, not a separate afterthought.

It should show:

- weak modules,
- weak claim statuses,
- repeated misconceptions,
- missed questions,
- recommended study sets.

## Rail Service Terminal Screen Regions

The Rail Service Terminal should not show the qualification filters, score
report, question count, or study-mode controls. It should use a terminal shell.

Required regions:

- **Status Bar:** `LINE`, `MANIFEST`, `STATE`, `CLOCK`, `AUTHORITY`, `ALARMS`,
  and a compact truth-boundary marker such as `SIM / ARCHITECTURE LOGIC`.
- **Line Board:** the dominant area. Shows service phases, packet position,
  support envelope, endpoint readiness, and phase progress.
- **Telemetry:** dense meters for support margin, source debt, endpoint
  confidence, timing drift, reset residue, stability posture, and load.
- **Command Stack:** current operator commands, with visible interlocks on
  disabled actions.
- **Procedure Panel:** checklist of gates and phase procedures.
- **Alarm/Event Feed:** timestamped stream with subsystem, severity, and terse
  event text.
- **Debrief Drawer:** appears after secure or abort.

The terminal should minimize explanatory prose while the line is active. The
operator learns through state, alarms, command availability, and the service
trace.

## Activity Surfaces

### Standard Quiz Surface

Use for:

- multiple choice,
- select all,
- true/false,
- short conceptual checks.

Features:

- compact prompt,
- claim-status badge,
- optional-content badge,
- answer controls,
- explanation after review,
- report contribution.

### Boundary Classification Surface

Use for distinguishing:

- established theory,
- established constraint,
- published speculative model,
- active-rail model,
- project hypothesis,
- open physical gate,
- project-state or revision-sensitive content.

Better UI shape:

- statements in rows,
- claim statuses as columns or drop targets,
- quick feedback on overclassification,
- summary of repeated boundary mistakes.

This surface should not feel like ordinary trivia. It is the honesty-training part of the system.

### Symbol And Equation Lab

Use for:

- rendered equation tokens,
- symbol-to-role matching,
- drag-fill blanks,
- expression interpretation.

Requirements:

- render LaTeX with KaTeX or equivalent,
- support tap/click placement,
- support drag placement,
- support keyboard placement,
- expose accessible labels,
- never require ordinary learners to type LaTeX.

### Service Chronology Surface

The old service chronology quiz surface is not enough for active-rail operator
training. Sequencing questions can remain inside the qualification drill, but
the dedicated operator product should become the Rail Service Terminal.

### Rail Service Terminal

Use for:

- single-line active-rail service operation in a terminal shell,
- readiness gates,
- support/carry/catch/fade/decompress/reset command flow,
- hold, abort, and recovery decisions,
- qualitative failure-mode training,
- post-run operator debriefs.

Required UI shape:

- full-width operations terminal, not a card inside the quiz workspace;
- dark or high-contrast console styling that clearly differs from the
  Qualification Board;
- compact top status bar with line id, state, manifest, clock, authority, and
  alarm count;
- dominant line schematic with live phase and packet state;
- telemetry stack with status bands and subsystem labels;
- command stack with currently available commands and locked commands;
- procedure checklist with gate state;
- terminal event feed;
- run debrief after completion or abort.

Interaction rules:

- The learner should not type raw source coefficients, timing constants, or
  synthetic score parameters.
- Service manifests should be loaded as operator work orders, not selected from
  friendly marketing cards.
- The trainer may use hidden numeric state to drive meters and outcomes, but the
  displayed controls should be procedural: precharge support, close ledger,
  synchronize endpoint, carry packet, catch/rematch, fade, decompress, reset,
  hold, abort, and secure.
- The trainer should not use question-bank scoring. Its outcomes are line
  states, event logs, cautions, abort reports, readiness summaries, and recovery
  notes.
- The interface must clearly label the trainer as architecture-logic simulation,
  but the label should look like a terminal status marker rather than a teaching
  paragraph.
- The terminal should keep disabled controls visible with interlock reasons.
- The terminal should make time matter: waiting too long in the wrong phase can
  increase drift, source debt, residue, or alarm severity.

### Matching Matrix

Use for:

- symbol-to-role,
- concept-to-claim-status,
- diagnostic-to-risk-channel,
- reference-to-claim.

Better UI shape:

- two-column matching for small sets,
- matrix/grid for multi-class classification,
- immediate visibility of unpaired or conflicting matches.

### Source-Ledger Reader

Use for:

- source-channel interpretation,
- standing support versus active-service excess,
- packet diagnostic versus plant diagnostic,
- burden migration.

Better UI shape:

- table or plot on one side,
- questions and interpretation controls on the other,
- highlighted row/column references,
- explanations tied to selected channels.

The first implementation can use static tables. Later versions can load real ledger artifacts.

### Design-Review Case File

Use for:

- multi-artifact review,
- pass/fail/needs-evidence decisions,
- open-gate recognition,
- evidence sufficiency,
- architecture review.

Better UI shape:

- dossier header,
- tabs for timeline, packet trace, ledger, notes, references,
- decision panel,
- evidence checklist,
- final review summary.

This is where the future-engineering-program framing can be strongest, as long as claim boundaries remain explicit.

## Math Rendering

Math should be rendered with a real LaTeX library.

Preferred dynamic-frontend approach:

- KaTeX installed as a package dependency.
- A small math-rendering component used consistently across the app.
- Store math as LaTeX strings in question data.
- Render after each workspace update.
- Keep text aliases for accessibility, search, and validation.

Rendering locations:

- prompts,
- choices,
- drag-fill tokens,
- blanks,
- matching options,
- explanations,
- reference snippets and source links,
- reports.

The UI should not expose raw LaTeX to learners unless they are in an authoring or expert mode.

## Explanation And Source UI

Explanations are part of the teaching surface, not just grading feedback.

After review, each item should be able to show:

- direct answer,
- technical reason,
- claim-boundary note,
- misconception note when useful,
- public paper or textbook anchors for established and literature claims,
- project-document or repository anchors for project-specific claims,
- open-gate notes for unresolved claims.

Reference links should be rendered as compact source cards or a drawer section with:

- title or label,
- source kind: paper, textbook, project doc, repo file, run artifact, or design note,
- citation or path,
- URL when available,
- short note explaining what the source supports.

The source drawer should never make an unsupported claim look stronger. A project document link supports "this is the current project model" or "this is the current project state"; it does not turn the claim into established physics.

## Renderer Architecture

The app should use a renderer registry. In React terms, this can be a mapping from activity type to component plus grader:

```text
question type -> activity renderer -> grading adapter -> explanation adapter
```

Examples:

- `mc` -> standard quiz renderer,
- `multi` -> standard quiz renderer,
- `drag_fill` -> symbol lab renderer,
- `sequence` -> ordering renderer inside qualification/study sessions,
- `claim_classification` -> boundary classification renderer,
- `rail_run` -> stateful service trainer, not a question-bank renderer,
- `ledger_interpretation` -> source-ledger reader,
- `case_review` -> design-review case file.

This keeps future question types from bloating one central render function.

## Presentation Order

Question-bank order is authoring order, not learner order. A session should
randomize display order at attempt creation and keep that order stable until the
workspace is rebuilt or reset.

Randomized presentation state should cover:

- standard choices for multiple choice, select all, and true/false,
- drag-fill token banks,
- matching prompts and matching options,
- claim-classification statements,
- sequence items.

Renderers should read these ordered ID lists from response/session state and
fall back to bank order only when old or malformed state is missing an order.
Graders should continue using stable IDs, so randomization never changes the
answer key.

## Frontend Stack

Recommended stack for the next build:

- Vite for local development and static build output.
- React for componentized activity surfaces.
- KaTeX for math rendering.
- Plain CSS modules or a small app stylesheet at first.
- Local data modules for question banks.

Avoid for now:

- backend API,
- database,
- accounts,
- server-side authoring workflow,
- heavy state-management libraries.

The app needs component boundaries and build tooling, not institutional software.

## Accessibility

The richer interface must remain usable.

Requirements:

- keyboard path for all interactions,
- tap-first fallback for drag operations,
- accessible labels for rendered math,
- color plus text/icon for claim statuses and question contexts,
- responsive layouts that do not hide report content,
- clear focus states,
- no essential information conveyed by color alone.

## Prototype Implication

The current static prototype should be treated as a vertical slice of infrastructure:

- data separation,
- filters,
- basic modes,
- basic renderers,
- basic scoring.

The next interface iteration should convert that slice into the dynamic frontend architecture, then introduce the renderer registry and proper LaTeX rendering before adding much more content.
