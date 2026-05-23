# Active-Rail Quiz System

This is the first dynamic frontend slice for the active-rail quiz system. It uses Vite, React, local question-bank modules, and KaTeX for math rendering.

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

- study, quiz, and boundary modes,
- filters for track, module, difficulty, question type, claim status, question context, and optional flagged content,
- renderer registry for standard quiz, symbol-fill, chronology, matching, and boundary-classification activities,
- multiple choice, select all, true/false, rendered symbol-fill, sequencing, matching, and claim-classification questions,
- click/tap or drag word-bank placement for fill blanks,
- KaTeX rendering for math tokens and explanations,
- visible claim-status and optional-content badges,
- grading by module, claim status, question context, and activity type,
- explanations with answer, reason, boundary, and references.

This is intentionally local-first. There is no backend, database, or user account system in this version.

Design documents:

- `DESIGN.md`
- `ROADMAP.md`
- `INTERFACE_ARCHITECTURE.md`
- `ASSESSMENT_MODEL.md`
