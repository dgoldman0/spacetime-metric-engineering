# Active-Rail Training System

This is the local frontend for the active-rail training system. It uses Vite,
React, local question-bank modules, KaTeX for math rendering, and a separate
service-terminal simulator model.

Run it locally:

```bash
npm install
npm run dev
```

Useful commands:

```bash
npm run validate:bank
npm run build
```

Current features:

- shared training suite with Qualification Board and Rail Service Terminal
  surfaces,
- study, quiz, and boundary modes,
- filters for track, module, difficulty, question type, claim status, question context, and optional flagged content,
- count controls for small drills, medium reviews, large reviews, or all matching questions,
- renderer registry for standard quiz, symbol-fill, chronology, matching, and boundary-classification activities,
- multiple choice, select all, true/false, rendered symbol-fill, sequencing, matching, and claim-classification questions,
- click/tap or drag word-bank placement for fill blanks,
- per-attempt randomization for answer choices, token banks, matching rows/options, classification statements, and sequence items,
- KaTeX rendering for math tokens and explanations,
- visible claim-status and optional-content badges,
- grading by module, claim status, question context, and activity type,
- explanations with answer, reason, boundary, and references.
- validation for source hygiene, paper-theory anchors, project-framing leakage, and minimal explanation depth.
- Rail Service Terminal prototype shell with work orders, telemetry,
  constraints, event trace, alarms, and debriefs. The current redesign target is
  a first-viewport operator simulator with state-derived active-rail graphics,
  persistent line controls, bounded seeded perturbations, and no command-stack
  workflow.

This is intentionally local-first. There is no backend, database, or user account system in this version.

Design documents:

- `DESIGN.md`
- `ROADMAP.md`
- `INTERFACE_ARCHITECTURE.md`
- `ASSESSMENT_MODEL.md`
- `SERVICE_TRAINER_DESIGN.md`
