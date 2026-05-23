# Active-Rail Quiz Assessment Model

This document defines the intended scoring and reporting model. It is separate from the main design document so scoring can gain depth without unbalancing the product design.

The system should grade more than "right answer or wrong answer." It should help users see what kind of understanding they have.

## Assessment Goals

The system should answer:

1. Does the learner understand the concept?
2. Does the learner classify the claim correctly?
3. Can the learner apply the idea in a design-review context?
4. What should the learner study next?

## Score Dimensions

Useful dimensions:

- concept accuracy,
- claim-boundary accuracy,
- module accuracy,
- learning-objective accuracy,
- question-type accuracy,
- chronology/handoff accuracy,
- source-ledger interpretation,
- diagnostic reasoning,
- open-gate recognition,
- confidence calibration,
- hinted versus unaided performance.

Not every mode needs every dimension. The report should show the dimensions relevant to the session.

## Claim-Boundary Scoring

Claim-boundary scoring is special for this project.

Examples:

- A learner correctly defines lapse but marks it as active-rail-specific. Content is partly right; boundary is wrong.
- A learner recognizes the Alcubierre metric as published speculative literature. Boundary is right.
- A learner treats reset-residue closure as solved engineering. Boundary is wrong and should be called out.

The system should report boundary accuracy separately from total correctness.

## Per-Activity Grading

### Standard Quiz

Use for multiple choice, select all, and true/false.

Defaults:

- multiple choice: all-or-nothing,
- true/false: all-or-nothing,
- select all: correct selections add credit, incorrect selections subtract credit, floor at zero.

### Drag-Fill And Symbol Lab

Defaults:

- score per blank,
- allow all-or-nothing override,
- treat equivalent tokens as aliases when defined,
- do not rely on typed equation matching for ordinary learners.

### Sequencing

Possible scoring:

- exact position score,
- adjacent-pair score,
- critical-order score.

Critical-order score is useful for active-rail chronology. For example, catch before fade may matter more than exact placement of every surrounding review step.

### Matching And Classification

Defaults:

- score per matched pair,
- separately record claim-boundary errors,
- surface repeated category confusions.

### Ledger Interpretation

Possible scoring:

- correct channel identification,
- correct interpretation of standing versus active-service burden,
- correct evidence sufficiency judgment,
- correct boundary classification.

### Design-Review Case File

Possible scoring:

- final decision,
- evidence cited,
- risk channels identified,
- open gates recognized,
- overclaims rejected,
- missing evidence named.

The correct answer may be "needs evidence."

## Confidence And Hints

Confidence and hints are optional, but useful.

Confidence values:

- unsure,
- somewhat sure,
- confident.

Report categories:

- confident and correct,
- confident and wrong,
- unsure and correct,
- unsure and wrong.

Hints should be tracked:

- correct without hint,
- correct after hint,
- incorrect after hint,
- skipped.

Study mode can be generous. Qualification mode can be stricter.

## Mastery

Use simple labels:

- new,
- practicing,
- competent,
- strong,
- review needed.

Mastery should require repeated evidence. One correct answer should not make a topic "strong."

Mastery can be tracked by:

- module,
- claim status,
- question context,
- learning objective,
- symbol family,
- project component,
- theory dependency.

## Reports

A good report should say what happened and what to do next.

Include:

- total score,
- module breakdown,
- claim-status breakdown,
- question-context breakdown,
- weak learning objectives,
- repeated misconceptions,
- hinted versus unaided performance when available,
- missed questions,
- recommended review set.

Good report language:

- "Strong on ADM vocabulary, weak on source-ledger boundary."
- "Correct chronology, but overclassified project hypotheses as established."
- "Packet diagnostics were strong; plant burden channels need review."

Avoid reducing the session to only a percent.

## Qualification Profiles

Different modes can use different pass criteria.

General learner:

- no hard pass/fail required,
- emphasize review recommendations.

Boundary practice:

- claim-boundary accuracy is primary.

Project-internal review:

- require minimum total score,
- require minimum claim-boundary score,
- require no severe open-gate misclassification,
- include optional project-state content when explicitly selected.

Source-ledger lab:

- emphasize diagnostic interpretation over vocabulary recall.

Design-review cases:

- emphasize evidence sufficiency and risk-channel diagnosis.

## Data Implications

Questions should be able to declare:

- points or weight,
- partial-credit rule,
- learning objectives,
- misconception tags,
- claim-boundary target,
- question context,
- hint availability,
- qualification profile compatibility.

The first implementation can keep these fields optional. The data model should leave room for them before content population becomes large.
