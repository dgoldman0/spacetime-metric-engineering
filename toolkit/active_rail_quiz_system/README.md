# Active-Rail Quiz System Prototype

This is the first static infrastructure slice for the active-rail quiz system.

Open `index.html` directly in a browser:

```text
toolkit/active_rail_quiz_system/index.html
```

No build step or local server is required. The sample question bank lives in `question_banks/sample_bank.js` so the app can run from a local file while still keeping question data separate from the HTML.

Current features:

- study, quiz, and boundary modes,
- filters for track, module, difficulty, question type, claim status, and optional flagged content,
- multiple choice, select all, true/false, drag-fill, sequencing, and matching questions,
- click/tap or drag word-bank placement for fill blanks,
- visible claim-status and optional-content badges,
- grading by module and claim status,
- explanations with answer, reason, boundary, and references.

This is intentionally small. The next step is to refine the question data shape and replace the sample bank with real curriculum-backed banks.

Implementation direction:

- The static prototype is a checkpoint.
- The next build should be a lightweight Vite/React app.
- Question banks should remain local files for now.
- KaTeX should be used as a real math-rendering dependency.
- No backend, database, or user accounts are planned for the first dynamic version.

Design documents:

- `DESIGN.md`
- `ROADMAP.md`
- `INTERFACE_ARCHITECTURE.md`
- `ASSESSMENT_MODEL.md`
