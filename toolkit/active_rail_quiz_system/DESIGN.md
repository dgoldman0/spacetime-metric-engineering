# Active-Rail Quiz System Design

This file is a design document, not an implementation roadmap. It defines what the full quiz system should become before we decide how to build it. Detailed implementation-facing notes live in companion documents:

- `INTERFACE_ARCHITECTURE.md` for screen structure, specialized activity surfaces, and math rendering.
- `ASSESSMENT_MODEL.md` for scoring, mastery, grading dimensions, and reports.

The original HTML prototype proves that a static active-rail quiz can work: it has a question bank, filters, explanations, KaTeX rendering, and mixed question types. The first infrastructure prototype in this folder proves local data separation and basic grading. The next system should now move to a lightweight dynamic frontend app so the interface can support specialized activity surfaces, richer state, proper math rendering, and grading profiles without turning into one oversized script file. It should teach established theory, published speculative-relativity context, and project-specific active-rail architecture while making the boundaries between those categories impossible to miss.

The guiding phrase:

> A future engineering program that knows exactly which parts are textbook, which parts are literature context, which parts are active-rail design language, and which parts are still open gates.

The system now has two related but distinct product layers:

- the qualification drill, which is an assessment and study surface backed by
  the question bank;
- operational learning services, which are scenario and trainer surfaces with
  their own domain data, state machines, procedures, and reports.

The question bank is not the product's universal content model. It is the right
model for quizzes, timed qualification, explanations, and assessment reporting.
An active-rail service trainer should instead feel like operating a line: the
learner works through readiness, command, hold, abort, recovery, and reset
decisions while the line state evolves.

## Product Intent

The quiz should feel like an engineering qualification from a future active-rail service academy, but it must remain honest by construction.

It should do four jobs at once:

1. Teach the established theory needed to reason about the design.
2. Teach the active-rail architecture as currently understood.
3. Train users to separate established understanding from project-specific ideas.
4. Help the project team study, audit, and sharpen the design itself.

The fictional framing is allowed to be fun. The physics boundary is not allowed to be fuzzy.

## Learning Modes

The app should support multiple session profiles over the same question bank.

Study mode is generous and explanation-forward. It can show feedback after each
answer, support resets, and prioritize learning over pressure.

Drill or qualification mode can delay grading until the workspace is checked and
can use stricter score reporting.

Timed quiz mode is a focused assessment session. It presents one question at a
time, keeps a running score, and runs against a selected time limit. The learner
answers, submits, and advances through the session until the question set or time
budget is exhausted.

Timed quiz mode should have an optional teaching setting:

- if explanation review is disabled, the session advances quickly and the timer
  continues to govern the attempt;
- if explanation review is enabled, the app shows the answer explanation after
  submission and pauses the timer while the learner reads it;
- the timer resumes when the learner moves to the next question.

This keeps timed mode honest as an assessment tool while still allowing it to
serve as a study tool when the learner chooses explanation review.

## Operational Learning Services

Some learning surfaces should not be quizzes at all. The active-rail service
trainer is the first such surface.

The service trainer is a qualitative architecture-logic simulator for a single
active-rail line. It does not compute a spacetime solution, solve field
equations, or claim physical plant realizability. It trains operational
reasoning inside the current active-rail architecture:

- bring a line from standby to armed service,
- precharge support and close the source ledger,
- synchronize endpoint catch conditions,
- carry a packet through the active interval,
- catch and rematch before fade,
- decompress and reset the rail,
- respond to support gaps, source debt, endpoint drift, reset residue,
  conservation or stability cautions, and abort states.

The operator interface should expose service requests, line states, readiness
gates, command buttons, meters, event logs, and recovery reports. It should not
ask the learner to type raw coefficients or enter a static parameter set for
grading. Hidden state variables are allowed inside the trainer, but the learner
interacts through operational choices: arm, hold, precharge, synchronize, carry,
catch, fade, decompress, reset, abort, and recover.

This surface should feel like a real training console in a future engineering
program. Its truth boundary remains explicit: it simulates the architecture's
procedural logic and predicted failure taxonomy, not validated spacetime
physics.

The trainer should use its own domain data:

- service profiles,
- rail phases,
- readiness actions,
- line state variables,
- qualitative thresholds,
- event templates,
- failure modes,
- recovery actions,
- run reports.

The question bank may be linked from the trainer for optional review prompts or
post-run study recommendations, but the trainer itself is not backed by quiz
questions.

## Non-Goals

- Do not present active-rail concepts as established physics unless they are actually established.
- Do not imply that a demanded-source ledger is a completed matter model.
- Do not let "engineering academy" styling hide unresolved physical gates.
- Do not require users to type LaTeX, equation syntax, or long symbolic answers.
- Do not make the service trainer feel like a static parameter form or graded
  quiz. It should be an evolving operator simulation.
- Do not make the first version a giant content dump with no epistemic structure.
- Do not add a backend, database, accounts, or server-side authoring system until the frontend learning model proves itself.
- Do not write learner-facing questions about "the quiz", "this quiz system", or the mechanics of the curriculum itself. Meta content belongs in authoring docs, not in the question bank.

## Core Design Principle: Claim Separation

Every question, explanation, module, and score report should expose the kind of claim being tested.

Suggested epistemic classes:

| Class | Meaning | Display Rule |
| --- | --- | --- |
| Established theory | Standard GR, differential geometry, stress-energy, ADM language, QFT-in-curved-spacetime basics, or broadly accepted mathematical machinery. | Show as "Established". Include references or canonical source notes. |
| Established constraint | Known limits, no-go pressures, energy-condition issues, quantum inequality constraints, topological censorship, backreaction concerns. | Show as "Established constraint". Explain what it limits and what it does not by itself rule out. |
| Published speculative model | Alcubierre-style warp metrics, traversable wormhole models, Natario-style metrics, or other published speculative-relativity constructs. | Show as "Published literature". Do not treat as demonstrated engineering. |
| Project definition | Active-rail vocabulary, decomposition, service chronology, support/carry/catch/fade/decompress/reset roles, demanded-source ledgers. | Show as "Active-rail model". State that this is project terminology or design structure. |
| Project hypothesis | A proposed active-rail design principle, burden-routing strategy, closure mechanism, or source-family conjecture. | Show as "Project hypothesis". Include what evidence would strengthen or falsify it. |
| Open physical gate | A required unresolved demonstration: matter closure, semiclassical response, stability, reset residue, repeated operation, causality, realizability. | Show as "Open gate". Score users on recognizing that it is not solved. |
| Fictional frame | Course names, certification titles, future institutional flavor. | Show in UI flavor only. Never use as evidence. |

The system should repeatedly ask users to classify claims. This should be a first-class skill, not an occasional warning.

Claim status is not the same thing as question context. The UI should expose both.

Suggested question contexts:

| Context | Meaning | Source Rule |
| --- | --- | --- |
| General theory | Textbook or broadly established theory questions that are not about a specific project design. | Use stable public source anchors where useful. |
| Paper theory | Questions about a paper's own theory, assumptions, results, implications, or limitations. | Use only papers with verified full public access, preferably arXiv or another actual public source page. Do not frame these as active-rail design lessons. |
| Project application | Questions that apply established theory or published literature to active-rail design reasoning. | Mark clearly as project application and attach project/source links when needed. |
| Project state | Questions about current repository evidence, run status, hypotheses, or open gates. | Flag as project-state or revision-sensitive and keep excludable. |

This distinction prevents a paper question from becoming an unmarked project question. For example, a general paper-theory item about Clark-Hiscock-Larson should ask what their null-geodesic analysis shows about Alcubierre causal access. A separate project-application item may ask how that result informs active-rail carrier audits, but it must be labeled as project application.

## Project-State Content Policy

Questions about project materials, project state, current work products, internal runs, active hypotheses, and open questions are allowed, but they must never be mixed into the general curriculum invisibly.

These questions should be treated as optional content bands that can be included or excluded selectively.

Project-state questions are not the same thing as quiz-meta questions. It is appropriate to ask whether a project claim is current, revision-sensitive, supported, unsupported, or still open. It is not appropriate to ask learners how the quiz system should label, score, or govern itself.

Required rules:

- Any item based on current project materials must be clearly marked.
- Any item about project state must be clearly marked as time-sensitive or revision-sensitive.
- Any item about open questions must be clearly marked as an open question, not as settled knowledge.
- Any item about a project hypothesis must identify what would count as supporting evidence, missing evidence, or falsifying pressure.
- No learner-facing item may ask about "the quiz", question-bank governance, scoring policy, or authoring policy.
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

- Mathematical modeling: units, dimensions, scaling, approximation regimes, stability, perturbations, and boundary conditions.
- Spacetime, metrics, signatures, and causal character.
- Stress-energy tensor and observer projections.
- Energy conditions: null, weak, dominant, strong.
- ADM split: lapse, shift, spatial metric, extrinsic curvature.
- Constraint equations and evolution language.
- Null contractions and source-channel diagnostics.
- Quantum mechanics basics: states, observables, uncertainty, spectra, ground states, and expectation values.
- Quantum vacuum basics: zero-point energy, vacuum fluctuations, mode structure, and why vacuum language is not a free-energy claim.
- Casimir-effect basics: boundary-conditioned vacuum modes, force/energy differences, experimental status, and limits of source interpretation.
- Basics of QFT in curved spacetime.
- Semiclassical stress tensor, RSET, and backreaction.
- Effective field theory: scale separation, cutoff sensitivity, matching, and why low-energy effective success is not unrestricted UV completion.
- Source-model literacy: scalar fields, electromagnetic fields, fluids, anisotropic stress, equations of state, and stability.
- String-theory context needed for source literacy: strings, branes, compactification, moduli, and effective descriptions, framed as background theory rather than an active-rail source solution.
- Causality protection, horizons, and chronology concerns.

Established foundations should not be treated as "mostly GR." The first release
needs a durable cross-domain spine: differential geometry and GR, quantum
mechanics, QFT and semiclassical gravity, effective field theory, source-model
basics, and carefully bounded string-theory context. These questions should be
mostly general theory, not paper trivia. Papers and lecture notes are source
anchors for concepts; they should not bias the bank into asking mainly "which
paper said this?"

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

Known public literature anchors in the current bank:

| Source | Public Access | Supports | Should Not Be Used For |
| --- | --- | --- | --- |
| Arnowitt, Deser, and Misner, "The Dynamics of General Relativity" | `https://arxiv.org/abs/gr-qc/0405109` | ADM split, lapse, shift, spatial metric, extrinsic curvature, Hamiltonian and momentum constraints. | Energy-condition taxonomy, quantum inequalities, global hyperbolicity, or active-rail source realization. |
| Carroll, "Lecture Notes on General Relativity" | `https://arxiv.org/abs/gr-qc/9712019` | Metric notation, curvature, Einstein's equation, geodesics, stress-energy tensor notation, Bianchi/conservation identities. | Primary support for energy-condition taxonomy, quantum inequalities, topological censorship, chronology protection, or global hyperbolicity. |
| OpenStax, "University Physics Volume 3" | `https://openstax.org/details/books/university-physics-volume-3` | Introductory quantum mechanics, spectra, expectation values, uncertainty, photons, matter waves, and modern-physics foundations. | Advanced QFT, curved-spacetime RSET, quantum inequalities, or string-theory source claims. |
| Tong, "Lectures on Quantum Field Theory" | `https://davidtong.org/teaching/quantum-field-theory/` | Field quantization, vacuum modes, particles as excitations, renormalization basics, and introductory Casimir-effect framing. | Engineering source construction, GR constraints, or active-rail validation. |
| Milton, "The Casimir Effect: Physical Manifestations of Zero Point Energy" | `https://arxiv.org/abs/hep-th/9901011` | Casimir-effect interpretation, zero-point-energy framing, boundary-conditioned vacuum effects, and limits of naive free-energy readings. | General proof that vacuum energy is an extractable source or that Casimir systems solve exotic-matter needs. |
| Burgess, "Introduction to Effective Field Theory" | `https://arxiv.org/abs/hep-th/0701053` | Scale separation, low-energy effective descriptions, matching, cutoff dependence, and EFT discipline. | Specific active-rail source realization or proof that any effective source has a UV completion. |
| Polchinski, "TASI Lectures on D-Branes" | `https://arxiv.org/abs/hep-th/9611050` | D-branes as open-string boundary-condition objects, worldvolume degrees of freedom, and source/coupling context in string theory. | Claims that branes provide a practical macroscopic source option. |
| Douglas and Kachru, "Flux Compactification" | `https://arxiv.org/abs/hep-th/0610102` | Flux compactification, moduli, string vacua, and why high-energy source ideas are embedded in strong consistency conditions. | Introductory QM/QFT basics or active-rail feasibility. |
| Curiel, "A Primer on Energy Conditions" | `https://arxiv.org/abs/1405.0403` | Definitions, interpretation, limits, and conceptual status of NEC/WEC/other standard energy conditions. | Quantum-inequality bounds, warp-specific source claims, or project source-family status. |
| Ford and Roman, "Quantum Field Theory Constrains Traversable Wormhole Geometries" | `https://arxiv.org/abs/gr-qc/9510071` | Quantum-inequality constraints on negative energy in exotic spacetime settings. | Generic NEC/WEC definitions, ADM constraints, or evidence that a source model exists. |
| Alcubierre, "The warp drive: hyper-fast travel within general relativity" | `https://arxiv.org/abs/gr-qc/0009013` | The published Alcubierre metric model and its stress-energy burden. | Engineering buildability, onboard controllability, quantum clearance, or active-rail validation. |
| Natario, "Warp Drive With Zero Expansion" | `https://arxiv.org/abs/gr-qc/0110086` | Zero-expansion warp-drive construction and its geometric scope. | Claims that zero expansion removes source, energy-condition, or causality review. |
| Clark, Hiscock, and Larson, "Null Geodesics in the Alcubierre Warp Drive Spacetime" | `https://arxiv.org/abs/gr-qc/9907019` | Null-geodesic reachability and horizon-like access cautions for Alcubierre spacetime. | Stress-energy source construction or physical feasibility proof. |
| Mueller and Weiskopf, "Detailed study of null and time-like geodesics in the Alcubierre Warp spacetime" | `https://arxiv.org/abs/1107.5650` | Null and timelike geodesic behavior inside the Alcubierre model. | Source realization, controllability, or broad physical feasibility. |
| Everett and Roman, "A Superluminal Subway: The Krasnikov Tube" | `https://arxiv.org/abs/gr-qc/9702049` | Krasnikov-tube network, chronology, and negative-energy lessons. | General proof that all shortcut networks are safe or impossible. |
| Shoshany and Snodgrass, "Warp Drives and Closed Timelike Curves" | `https://arxiv.org/abs/2309.10072` | Two-warp-drive CTC construction context and associated weak-energy-condition violation context. | General active-rail qualification or all-purpose chronology doctrine. |
| Garattini and Zatrimaylov, "On the Wormhole--Warp Drive Correspondence" | `https://arxiv.org/abs/2401.15136` | Warp/wormhole correspondence claims, intrinsic-curvature requirements, and traversability caveats. | Morris-Thorne full-paper replacement for every wormhole result or source realization proof. |
| Barcelo and Visser, "Scalar Fields, Energy Conditions, and Traversable Wormholes" | `https://arxiv.org/abs/gr-qc/0003025` | Non-minimally coupled scalar-field energy-condition behavior and caveats. | Generic clearance of arbitrary scalar-field source proposals. |
| Moghtaderi, Hull, Quintin, and Geshnizjani, "How Much NEC Breaking Can the Universe Endure?" | `https://arxiv.org/abs/2503.19955` | Smeared/semilocal NEC-breaking constraints in its stated quantum-motivated setting. | Replacement for classical pointwise energy-condition definitions. |
| Friedman, Schleich, and Witt, "Topological Censorship" | `https://arxiv.org/abs/gr-qc/9305017` | Global topological-censorship assumptions and shortcut-topology constraints. | Local throat inspection or source construction. |
| Visser, "The quantum physics of chronology protection" | `https://arxiv.org/abs/gr-qc/0204022` | Open-access chronology-protection review, closed causal curves, and quantum backreaction concerns. | Primary source for global hyperbolicity definitions or ADM constraints. |
| Minguzzi and Sanchez, "The causal hierarchy of spacetimes" | `https://arxiv.org/abs/gr-qc/0609119` | Causal hierarchy, chronology conditions, causality distinctions, and global causal-structure vocabulary. | Energy conditions, source realization, or ADM dynamics. |
| Miguel Sanchez, "Recent progress on the notion of global hyperbolicity" | `https://arxiv.org/abs/0712.1933` | Global hyperbolicity, Cauchy hypersurfaces, causal-curve criteria, and predictability framing. | Generic local light-cone notation, energy conditions, or source construction. |
| Bernal and Sanchez, "On smooth Cauchy hypersurfaces and Geroch's splitting theorem" | `https://arxiv.org/abs/gr-qc/0306108` | Smooth spacelike Cauchy hypersurfaces and splitting structure in globally hyperbolic spacetimes. | ADM constraint equations or energy-condition taxonomy. |

Known public project anchors in the current bank:

| Source | Public Access | Supports | Should Not Be Used For |
| --- | --- | --- | --- |
| Active-rail technical disclosure | Public GitHub `active_rail_technical_disclosure.tex` | Current active-rail architecture, component roles, source placement, and claim scope. | Established external theory or proof of physical source realization. |
| Repository status README | Public GitHub `README.md` | Current bounded project status and explicit non-claims. | Stable theory questions or paper-theory claims. |
| ADM harness README | Public GitHub `toolkit/adm_harness_cli/README.md` | Software parameter names and harness controls. | General ADM theory beyond the software vocabulary. |
| Supporting reports | Public GitHub `supporting_reports/*.md` | Current project evidence for service scheduling, source ledgers, reset ladder, source-family status, endpoint status, and V5/V10 diagnostic scope. | Stable general theory, complete matter-action closure, or deployment-independent claims. |

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

Use inside the qualification drill for ordering concepts, service-stage
vocabulary, and review procedures. The dedicated active-rail operation surface
is the Rail Run Trainer, not a sequence-question lane.

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
- source links,
- misconception targets,
- authoring status,
- review status,
- version.

Question data should remain canonical. It should not depend on answer order or
presentation order. Session state is responsible for randomizing display order
per attempt, while grading continues to compare stable IDs against the canonical
answer representation.

Per-attempt presentation state should include:

- choice order for multiple-choice, select-all, and true/false activities,
- token order for drag-fill word banks,
- prompt and option order for matching activities,
- statement order for claim-classification activities,
- item order for sequence activities.

Sequence activities should avoid starting in the canonical answer order when
there is more than one item. The point is ordering practice, not recognizing a
pre-solved list.

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
    kind: textbook
    supports: "Relation between Einstein tensor and stress-energy tensor."
    citation: "Standard GR text reference."
    url: null
source_links:
  - label: "Project source-ledger notes"
    kind: project_doc
    url: "relative/or/repo/path/when/available"
    supports: "Project-specific demanded-source terminology."
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
- **Source Links:** paper, textbook, project-document, or repository links that let a learner continue studying.

The shared explanation is the default and remains required. It is the stable
mini-lesson for the question: what the correct answer means, why it follows,
and what boundary it preserves. The system should also support optional
adaptive feedback when the question data provides it. Adaptive feedback is
choice-aware or action-aware text that responds to the learner's actual
selection: why a chosen option is supported, why a chosen distractor overclaims,
which correct option was missed, or which inversion in a sequence matters.

Adaptive feedback must be optional at the schema and renderer level. Existing
questions should continue to work with only `explanation.answer`,
`explanation.why`, and `explanation.boundary`. Adding adaptive feedback should
improve a question, not force every legacy item to be rewritten before the app
can build.

For example:

```text
Answer: The demanded-source ledger records G_mn/(8 pi).
Why: In units G = c = 1, Einstein's equation gives G_mn = 8 pi T_mn.
Boundary: This is established GR applied as project source accounting.
Project-Specific Meaning: The ledger identifies what the prescribed active-rail geometry demands.
Open Gate: It does not prove that a realizable matter sector exists.
```

References should be structured enough for UI rendering. A reference may point to a paper, arXiv page, textbook citation, project repository file, public project document, or run artifact. Paper-theory questions must point to actual public source locations for fully accessible papers, not local repo copies or unverified DOI-only landing pages. Project-material questions may point to public repository documents or local run records during internal use, but they must carry `project_material`, `project_state`, `open_question`, or `revision_sensitive` flags when appropriate.

Explanations should teach the learner after grading. A good explanation does not merely say which option was correct; it names the relevant principle, explains the distractor trap, identifies the claim boundary, and points to sources worth reading next.

Adaptive feedback patterns by activity:

- **Multiple choice and true/false:** each option may carry feedback explaining
  the specific reason it is supported or unsupported.
- **Select-all:** each choice may carry feedback so the review panel can
  distinguish selected-correct, selected-unsupported, and missed-supported
  choices. The feedback should teach the concept behind that choice rather than
  merely saying "right" or "wrong."
- **Drag-fill and symbol labs:** blanks and tokens may carry feedback for
  accepted tokens and common distractors. This is especially useful when a
  wrong token is mathematically related but plays the wrong role.
- **Sequence activities:** critical order relations may carry feedback, such as
  why catch/rematch must precede release fade or why source-demand accounting
  precedes physical source claims.
- **Matching and classification:** prompts or statements may carry feedback
  explaining the specific match or classification boundary.

Adaptive feedback should use positive, affirmative teaching language. It should
say what is true about the material and where the selected answer exceeds,
narrows, or misses that truth. It should not scold the learner, narrate the
author's rubric reasoning, or use difficulty-label language as explanation.

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

Session narrowing should use faceted multi-select controls for categories that naturally overlap. Users should be able to select one or more tracks, modules, difficulty levels, claim statuses, question contexts, and activity types where those controls are present. An empty facet selection should mean "all" for that facet. Count and optional-content policy can remain single-choice controls because they represent session behavior rather than content categories, but count should offer small, medium, and large review sizes plus all.

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

- No learner-facing question may reference "the quiz", "this quiz system", "question labeling", or scoring policy. Such material belongs in documentation or authoring validation, not curriculum.
- Every established-theory question needs at least one reference anchor.
- Every project-specific question needs a boundary note.
- Every project-material, project-state, open-question, or revision-sensitive question needs an explicit content flag.
- Project-specific content that could change as the architecture matures must use provisional language such as "could", "might", "appears", "seems", "current report suggests", or "current evidence indicates." Do not phrase revision-sensitive project state as final fact.
- Every speculative-literature question must distinguish metric construction from physical realizability.
- Every paper-theory question must identify the paper clearly in the stem, using a publication year plus author/title or an equivalent citation anchor. Vague stems like "the study" or "this result" are not acceptable.
- Every open-gate question should reward users for saying "not yet shown" when appropriate.
- Distractors should be plausible misunderstandings.
- Avoid trivia unless it supports conceptual fluency.
- Avoid "gotcha" wording.
- Equations should be rendered or tokenized, not typed by the learner.
- If a question combines established theory with active-rail vocabulary, the explanation must separate those parts.

## Question Quality Rubric

Each proposed question should be vetted before it enters the approved bank. Draft questions can exist locally, but the final bank should include only items that meet the rubric.

This rubric is an authoring scorecard, not just an automated validator. Automated checks can catch missing references, banned meta wording, or malformed data. They cannot judge whether a distractor is pedagogically useful, whether an advanced item really requires advanced reasoning, or whether an explanation teaches well. The author should score each question while writing and revising it.

### Required Passing Criteria

A question is acceptable only if it passes all of these checks:

- **Purpose:** it tests a real learning objective, not trivia or wording recall.
- **Claim status:** its epistemic class is correct and visible.
- **Difficulty fit:** the cognitive demand matches the assigned difficulty.
- **Source support:** established and literature claims have reference anchors; project claims have project-source or boundary anchors.
- **Paper anchor:** paper-theory stems identify the specific paper being tested; they do not rely on vague phrases such as "the study."
- **Explanation quality:** the explanation teaches why the answer is right and why tempting wrong answers fail.
- **Material-facing explanation:** explanations teach the subject matter, not why the author chose a difficulty label, question type, or rubric score.
- **Explanation depth:** explanation length and detail match difficulty; advanced items need enough reasoning detail to teach the boundary, not just reveal the answer.
- **Adaptive feedback quality:** when per-choice or per-action feedback is present, it must explain that specific answer relationship and remain consistent with the shared explanation.
- **Boundary clarity:** project-specific, speculative, unresolved, or revision-sensitive content is explicitly marked.
- **No meta leakage:** the item does not ask about the quiz system, authoring policy, scoring policy, or labeling policy.
- **Interaction fit:** the question type matches the task; symbolic items use rendered tokens rather than typed LaTeX.
- **Distractor quality:** wrong choices are plausible misconceptions, not jokes or throwaways.
- **Intermediate/advanced choice quality:** at intermediate and advanced levels,
  wrong choices must be credible misconceptions, nearby-but-wrong inferences,
  incomplete applications, or plausible overextensions. Obviously false
  absolutes are allowed only when the learning objective is basic recognition or
  when the option represents a common real-world overclaim that the explanation
  directly teaches against.
- **Difficulty-scaled discrimination:** intermediate and advanced questions must
  require discrimination among nearby ideas, not just elimination of choices no
  informed learner would take seriously. A wrong option may be false, but it
  should usually preserve a true surface feature, a common inference path, or an
  assumption that fails only after the learner applies the relevant distinction.
- **Select-all shape:** multi-select items do not follow a predictable fixed pattern. The number of choices and correct answers should vary with the concept being tested.
- **Reviewability:** references, tags, and misconception targets are specific enough for later audit.

### Difficulty Calibration

Difficulty should describe cognitive demand, not how obscure the wording is.

| Difficulty | Expected Learner Task | Multiple-Choice Standard |
| --- | --- | --- |
| Core | Recognize a definition, identify a direct relation, classify an obvious claim boundary, or apply one step of known theory. | A learner who studied the module should answer quickly without juggling several concepts. Distractors test common confusions. |
| Intermediate | Apply a concept in context, distinguish similar statuses, interpret a simple equation or chronology, or connect two ideas. | A learner should need to reason through at least one implication or reject a tempting overclaim. Wrong options should sound plausible until the relevant distinction is applied. |
| Advanced | Synthesize multiple constraints, evaluate evidence sufficiency, separate established theory from project use in a mixed prompt, or reason about open gates. | Even with choices supplied, the learner should need solid conceptual command and careful boundary discipline. Distractors should be expert-like partial truths, missing-assumption claims, scope errors, or plausible but unsupported synthesis moves. |

Advanced multiple choice is allowed, but it must be advanced because of
reasoning load, not because the source topic is difficult or because the answer
is hidden in obscure prose. An item is not advanced if the correct option is a
straight slogan and the wrong options are cartoon overclaims such as "ignore all
constraints" or "this proves the source." Those items should be downgraded or
rewritten with a real scenario, plausible distractors, and a reasoned tradeoff.

The same standard applies to intermediate items. If an intermediate prompt can
be answered by eliminating choices that no serious learner would consider, it
should be rewritten. Good intermediate distractors often preserve one true
surface feature while moving the wrong boundary: a local result treated as
global, a kinematic statement treated as a source statement, a consistency
condition treated as realization, or a paper result treated as deployment
evidence. At this level, the learner should often have to ask "what exactly
does this result support?" rather than merely spot an absurdity.

For advanced approval, the human reviewer should be able to name the advanced
move required. Examples:

- distinguish two related constraints that can fail independently,
- evaluate incomplete evidence without dismissing it or overpromoting it,
- transfer a paper result into a design review while preserving claim scope,
- identify which assumptions make a theorem applicable,
- separate consistency, source demand, physical realization, and operational
  qualification in one scenario.

That named move belongs in author notes or review logs, not in the
learner-facing explanation. A learner explanation should say something like
"For a type-I stress tensor, the NEC depends on density-plus-pressure
combinations" rather than "This is advanced because it uses a type-I tensor."

### Select-All Calibration

Select-all questions should not teach learners that there are always two right
answers and two wrong answers. Use the shape that fits the content:

- 4 choices with 1, 2, or 3 correct answers for compact checks;
- 5 choices when the learner needs to separate a primary principle from several
  nearby misconceptions;
- 6 choices when the task asks for a richer evidence review, source audit, or
  multi-constraint synthesis;
- 4 or more correct answers only when the item is explicitly about collecting a
  set of required conditions.

The correct-answer count should never be padded merely to create variety, but a
bank where every select-all item has the same answer shape fails review because
it lets test-taking pattern recognition replace subject understanding.

### Authoring Scorecard

Score each draft question before it is accepted into the learner-facing bank.

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Learning objective | No clear objective, trivia, or meta-policy content. | Objective exists but is vague or too small. | Tests a real module objective or misconception. |
| Difficulty fit | Difficulty label is misleading. | Difficulty is close but prompt or distractors distort it. | Cognitive demand clearly matches core, intermediate, or advanced. |
| Claim boundary | Status is missing, wrong, or overclaims evidence. | Status is present but explanation is thin. | Status and boundary are explicit and educational. |
| Source support | Unsupported established/literature/project claim. | Sources exist but are generic or weakly tied. | Sources directly support the claim being tested. |
| Paper anchor | Paper-theory item does not identify the paper or hides behind "the study." | Paper is named but incompletely anchored. | Stem gives author/title/year or an equivalent citation anchor. |
| Explanation quality | Merely reveals the answer or repeats the prompt. | Gives a reason but little teaching value. | Teaches answer, reasoning, boundary, and common trap. |
| Material-facing explanation | Explains authoring choices such as difficulty or rubric status. | Mostly teaches material but includes authoring-room phrasing. | Teaches the material only; no difficulty-label or rubric justification appears. |
| Explanation depth | Too short for the assigned difficulty. | Adequate but thin, especially for intermediate or advanced items. | Depth matches difficulty: concise for core, implication-focused for intermediate, reasoning-rich for advanced. |
| Adaptive feedback | Missing where the item clearly needs diagnostic feedback, or contradicts the answer. | Present but generic, such as "this is incorrect" without teaching the misconception. | Tailored to the learner's selected, missed, misplaced, or matched answer and consistent with the shared explanation. |
| Distractor quality | Throwaway, absurd, ambiguous, or obviously false options at intermediate/advanced level. | Some plausible distractors but uneven, or one option gives the answer away. | Distractors map to real misconceptions, partial truths, missing assumptions, scope errors, or plausible overclaims. |
| Difficulty-scaled discrimination | Intermediate/advanced item can be answered by dismissing unserious choices. | One plausible wrong choice exists, but the rest are giveaways. | Several options require applying the concept's boundary, assumptions, quantifiers, or evidence scope. |
| Select-all shape | Repeats the same number of options and correct answers by habit. | Shape varies but sometimes looks padded. | Choice count and answer count match the learning task and vary across the bank. |
| Interaction fit | Wrong activity type or asks for awkward typing. | Usable but not ideal for the skill. | Activity type supports the learning task naturally. |
| Content scope | Meta-policy, scoring, or authoring content appears in the learner-facing item. | Content is relevant but too broad or underspecified. | Content belongs in the curriculum and stays inside the intended module. |

Acceptance guide:

- `19-20`: approve if references and data validation also pass.
- `16-18`: revise or require reviewer approval.
- `11-15`: rewrite before inclusion.
- `0-8`: reject.

Any score of `0` in claim boundary, source support, explanation depth, adaptive feedback when required, or no-meta/content scope blocks approval regardless of total score.

## Curriculum Bank Scale

The learner-facing bank should be a rich curriculum bank, not a small demo set.
The current 128-item bank is a stronger seed after the first expansion and
advanced-question passes, but it is still below the intended curriculum scale.
A serious first release should
target roughly 150 to 250 approved items, with enough spread that filters still
leave useful sessions after excluding project-state or optional content.

Established general theory should be the durable core of the curriculum. The
paper-theory and active-rail layers should build on that foundation, not replace
it. Project-state and revision-sensitive questions should be a small, clearly
flagged layer because they can change as the project matures.

The bank should grow in reviewed passes:

- foundation pass: ADM, metric interpretation, stress-energy, energy
  conditions, causal structure, geodesics, curvature, constraints, basic GR
  vocabulary, quantum mechanics, quantum vacuum, Casimir effect, QFT,
  semiclassical gravity, effective field theory, source-model literacy, and
  bounded string-theory context;
- paper-theory pass: accessible literature on Alcubierre, Natario,
  Ford-Roman, Clark-Hiscock-Larson, Mueller-Weiskopf, Everett-Roman,
  Shoshany-Snodgrass, Garattini-Zatrimaylov, Barcelo-Visser, topological
  censorship, and chronology protection;
- active-rail architecture pass: packet/plant distinction, service stages,
  source ledger, support burden, endpoint handoff, reset, and failure modes;
- design-review pass: evidence sufficiency, claim boundaries, missing channels,
  and qualification decisions;
- symbol/activity pass: rendered math tokens, matching, sequencing, and
  classification surfaces so the experience is not dominated by ordinary
  multiple choice.

Each expansion pass should include a human rubric pass before acceptance. The
automated validator is a floor: it catches malformed data, unsupported links,
thin explanations, vague paper-theory stems, and meta leakage, but it does not
replace source reading or author judgment.

### Vetting Outcome

Each item should end in one of these states:

- `approved`: ready for the learner-facing bank.
- `needs_reference_review`: likely useful, but source anchors or citations are incomplete.
- `needs_project_review`: project-specific claim needs architecture review.
- `needs_rewrite`: learning objective is valid but prompt, distractors, or explanation are weak.
- `reject`: meta, misleading, unsupported, too trivial, or outside curriculum scope.

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
