# Active-Rail Quiz Interface Architecture

This document describes the intended interface shape for the full quiz system. It exists because the first infrastructure prototype is useful but too simple: it puts every activity into the same basic card flow. That is fine for proving the plumbing, but it will not support the richer teaching and assessment model.

The full system should use shared infrastructure with specialized learning surfaces. The next implementation should be a lightweight dynamic frontend app, not a larger server-backed platform.

## Core Principle

Use a shared shell, not a single shared question UI.

Shared shell:

- navigation,
- filters,
- mode selection,
- claim-status and optional-content controls,
- session state,
- scoring service,
- explanations,
- reference drawer,
- review queue.

Specialized surfaces:

- ordinary quiz cards,
- boundary classification workspace,
- symbol and equation token lab,
- service chronology timeline,
- matching matrix,
- source-ledger/table reader,
- design-review case file,
- mastery and remediation view.

This keeps the app coherent without flattening every kind of learning into multiple choice with badges.

## Screen Regions

### Command Bar

The command bar controls the active session:

- mode,
- curriculum track,
- module,
- question type or activity type,
- claim status,
- optional content flags,
- count or session length,
- build/start action.

It should stay compact. It is a cockpit control strip, not a settings page.

### Workspace

The workspace changes by activity type. It is the main learning surface.

Examples:

- a concise card stack for basic quiz items,
- a grid for claim classification,
- a horizontal or vertical timeline for service chronology,
- a table-plus-question layout for ledger interpretation,
- a dossier layout for design-review cases.

### Right Rail

The right rail should be context-sensitive.

Possible panels:

- score summary,
- claim-status legend,
- reference drawer,
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

Use for:

- support/carry/catch/fade/decompress/reset ordering,
- handoff timing,
- evidence-check ordering,
- release-before-catch failure diagnosis.

Better UI shape:

- reorderable timeline,
- stage cards,
- optional timing markers,
- stage-specific explanations.

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
- reference snippets,
- reports.

The UI should not expose raw LaTeX to learners unless they are in an authoring or expert mode.

## Renderer Architecture

The app should use a renderer registry. In React terms, this can be a mapping from activity type to component plus grader:

```text
question type -> activity renderer -> grading adapter -> explanation adapter
```

Examples:

- `mc` -> standard quiz renderer,
- `multi` -> standard quiz renderer,
- `drag_fill` -> symbol lab renderer,
- `sequence` -> chronology renderer,
- `claim_classification` -> boundary classification renderer,
- `ledger_interpretation` -> source-ledger reader,
- `case_review` -> design-review case file.

This keeps future question types from bloating one central render function.

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
- color plus text/icon for claim statuses,
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
