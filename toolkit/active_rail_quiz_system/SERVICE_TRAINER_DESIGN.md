# Rail Service Terminal Design

This document is the source of truth for the Rail Service Terminal. The terminal
is a first-class product in the active-rail training suite, not a quiz mode and
not a themed question workspace.

Target experience:

> The learner sits down as the assigned line engineer at a future active-rail
> service terminal. A single line is already alive. The operator observes the
> line, works the controls, responds to changing subsystem state, and secures,
> holds, recovers, or aborts the run.

The terminal remains honest about physics. It is an architecture-logic and
operations simulator. It does not solve the Einstein equation, validate a matter
model, certify an active-rail plant, or claim physical realizability.

## Product Boundary

The training suite has two sibling products:

| Product | Primary Job | Data Model | Interface |
| --- | --- | --- | --- |
| Qualification Board | Teach and assess theory, references, claim boundaries, and active-rail vocabulary. | Question bank, grading, explanations, references. | Learning board. |
| Rail Service Terminal | Simulate operation of one active-rail line. | Line state, work orders, controls, subsystem models, visual state, alarms, traces, debriefs. | Operations terminal. |

The question bank can recommend study after a terminal run. It cannot drive the
terminal's main loop. The terminal loop is:

1. observe the live line;
2. manipulate operational controls;
3. watch subsystem state evolve;
4. respond to limits, warnings, and failures;
5. secure, hold, recover, or abort.

## Primary Operating Surface

The primary operating surface presents a working line terminal. Its structure is
defined by live service state, direct controls, and graphic subsystem feedback.

The primary operating surface excludes these patterns:

- a work-order list that drives the whole experience;
- "drill" or puzzle-prompt language as the main framing;
- a visible command stack or next-action button sequence;
- phase chips used as the operator's main interaction;
- big origin/endpoint text boxes that occupy space without doing visual work;
- static decorative curves that do not reflect state;
- generic triangles or stickers presented as "visualization";
- duplicate percentage cards inside the line graphic;
- tall layouts where the operator must scroll to find core controls;
- any wording that makes the active run feel like a graded question attempt.

Scenario setup, guided practice, and instructor challenges are allowed as
secondary modes. They must not be the default operating surface.

## Active-Rail Architecture Mapping

The terminal should be grounded in the active-rail architecture as currently
understood. It abstracts that architecture, but it should not collapse it into
generic "health bars."

Use these mappings:

| Architecture Idea | Terminal Abstraction | Visual/Control Expression |
| --- | --- | --- |
| Prescribed service geometry | Service corridor and active interval | Rail corridor shape, active service envelope, packet path. |
| Packet-centered service | Packet body and carry state | Moving packet marker, handoff/hold/recovery posture. |
| Support plant | Support envelope and containment | Envelope thickness, continuity, glow, fracture, support drive. |
| Demanded-source ledger | Source channel and source debt | Source-flow band, saturation, ledger closure control, residual markers. |
| ADM/constraint posture | Constraint guard layer | Constraint bands, interlocks, stability posture, guard map. |
| Endpoint catch/rematch | Catch aperture and endpoint phase | Aperture shape, lock rings, endpoint sync/catch controls. |
| Fade/release | Carrier withdrawal | Release fade control, visible fade front, caught-before-release guard. |
| Decompression/reset | Reset path and residue | Residue haze, purge/decompression controls, reuse readiness. |
| Stability/backreaction concern | Global posture and caution layer | Envelope vibration/shear, warning tone, lockout posture. |
| Component-source handoff | Closure/readiness channels | Inspector overlays and debrief traces, not raw equations. |

The visual language should repeatedly teach the distinction between:

- geometry requested by the service;
- source demand recorded by the ledger;
- physical source realization, which remains an open gate;
- operating qualification inside this simulator.

## Operator Role

The user is a line operator, not a quiz taker. The operator should be able to
understand the current situation from the terminal without reading a paragraph
of instructions.

The operator acts through:

- support drive and support-shaping controls;
- source/ledger closure controls;
- endpoint sync and catch aperture controls;
- carry authority and hold authority;
- release/fade, decompression, and reset controls;
- secure, recovery, and abort controls.

The operator should not type raw hidden variables, coefficients, equations, or
state numbers. Expert override can be a later diagnostic mode, but it must be
separate from ordinary line operation.

## First-Viewport Layout

The ordinary desktop first viewport must include all core operation:

1. shared suite/product header;
2. compact line status strip;
3. dominant live line graphic;
4. compact instrumentation adjacent to the graphic;
5. persistent operator controls;
6. concise advisory/trace area or drawer affordance.

The operator should not scroll to perform ordinary service. Scrolling is
acceptable for debrief, trace history, scenario library, and detailed
inspection. It is not acceptable for core controls.

Work-order selection is a compact setup affordance, not a left-rail content
deck. During a run, the work order should collapse to a small assignment card or
status chip. Scenario browser, fault library, and instructor mode can live in a
drawer.

Origin and endpoint should be visual stations integrated into the line graphic.
They should not be large empty panels whose main function is to show text.

## Live Graphic Readout

The line graphic is the primary simulation surface. It should feel like an
aesthetically finished instrument that shows geometry and service evolution.

Required live layers:

- **service corridor:** bounded route, active interval, geometry frame;
- **support envelope:** field around the corridor whose thickness, continuity,
  brightness, and distortion change with support state;
- **packet:** moving body with hold, carry, catch, fade, recovery, and secure
  visual states;
- **source channel:** side channel showing source load, debt, closure, residual,
  and overdraw through shape and saturation;
- **endpoint aperture:** receiving/catch region with phase alignment, aperture
  width, and rematch lock;
- **timing shear:** state-derived phase offset or shear bands, not static
  ornament;
- **reset residue:** haze/debris/decay along the reset path that visibly clears
  or contaminates reuse;
- **constraint posture:** guard or boundary layer that tightens when constraints
  or stability limits narrow authority;
- **alarm localization:** warnings attached to the subsystem that is actually
  degraded.

The graphic must avoid:

- static squiggles that never change;
- arbitrary triangles or shapes that are not tied to a subsystem state;
- overlaying dashboard cards inside the line;
- repeating the same percentage values already shown in instrumentation;
- labels that cover the geometry they claim to explain.

Text inside the graphic should be sparse: station names, subsystem labels,
phase/status tags, and short localized warning tags. The learner should feel the
support field, source burden, catch aperture, timing drift, and residue state
from the graphic before reading a number.

Implementation preference:

- Use SVG for corridor geometry, packet motion, envelopes, apertures, masks,
  gradients, traces, and localized warnings.
- Use CSS transitions/animations for continuous motion and state changes.
- Add canvas later only for dense particles, field noise, heatmaps, or other
  raster effects that SVG cannot handle cleanly.
- Keep all visual layers state-derived from the simulator model.

## Instrumentation

Instrumentation supports the graphic. It does not replace it.

Required instruments:

- support margin;
- source debt/source load;
- endpoint confidence;
- timing drift;
- reset residue;
- stability posture;
- load index;
- alarm count/severity;
- operating authority.

At least some instruments should show trend, band, and direction: rising,
falling, steady, recovering, caution, or lockout. Numeric percentages are useful
only when paired with recent motion or threshold context.

## Control Model

The terminal interaction model is live operation. Controls are persistent
instruments, not answers.

Primary controls:

- support drive;
- support trim or containment shaping;
- ledger closure/source channel;
- endpoint sync;
- catch aperture;
- carry drive;
- release fade;
- decompression;
- reset purge;
- hold/resume;
- abort/recovery;
- secure line.

Controls may be sliders, guarded switches, levers, dials, toggles, or compact
button controls depending on the action. The key rule is that the operator is
manipulating a live line, not selecting the next command from a list.

Constraints should appear as:

- guarded controls;
- clipped control ranges;
- warning lamps on the relevant control;
- control resistance or delayed response;
- visible changes in the affected subsystem.

A detail drawer may explain why a guard is active. The main UI should not become
a grid of disabled buttons.

## Autopilot, Supervisor, And Randomness

The terminal should support a supervised learning mode without becoming a quiz.

Autopilot is a visible control-law demonstration:

- it manipulates the same controls available to the operator;
- it leaves an event trace;
- it can be paused or handed back to manual control;
- it should explain actions tersely in operational language;
- it must not hide failures or silently solve the run.

Supervisor mode is advisory:

- it highlights the next operational concern;
- it points to a subsystem, control, or guard;
- it should not present a puzzle prompt or single "correct answer" button.

Randomness should be bounded and replayable:

- each work order has a seed;
- perturbations include source-load fluctuation, endpoint timing drift, support
  disturbance, reset residue, hidden degradation, and stability caution;
- the same seed should replay the same sequence for review;
- random faults should manifest visually before or during alarm state.

## Work Orders And Scenarios

Work orders are operational assignments. They should be terse and terminal-like.

Good examples:

- `Endpoint confidence degraded at load. Monitor catch margin.`
- `Reuse path carries residual from prior reset.`
- `Heavy packet: source load expected above nominal.`

Avoid:

- `Find the degraded subsystem.`
- `Keep the run inside recovery authority.`
- `Which action is correct?`
- `Fault-Injection Drill` as the normal operating language.

The scenario/fault library can remain as a secondary instructor component. It
may include guided drills, incident replays, and specific fault injections, but
the main terminal should open as a live assigned line, not as a drill list.

## Data Model

Use a separate service-terminal model.

Suggested modules:

- `workOrders.js`: assignment metadata, seeds, starting states, known cautions.
- `lineControls.js`: control definitions, authority rules, guard behavior.
- `failureModes.js`: failure conditions, alarm templates, recovery guidance.
- `lineSimulator.js`: time evolution, control response, state transitions.
- `visualState.js`: derived geometry, field layers, warning localization,
  trends, and viewport state.

Suggested state shape:

```js
{
  workOrderId,
  seed,
  lineId,
  clock,
  runState,
  packetState,
  authorityState,
  controls: {
    supportDrive,
    supportTrim,
    ledgerClosure,
    endpointSync,
    catchAperture,
    carryDrive,
    releaseFade,
    decompression,
    resetPurge,
    hold,
    abort,
    secure
  },
  metrics: {
    supportMargin,
    sourceDebt,
    endpointConfidence,
    timingDrift,
    resetResidue,
    stabilityPosture,
    loadIndex
  },
  trends,
  constraints,
  guards,
  alarms,
  visualState,
  events,
  debrief
}
```

The React component renders state and dispatches control changes. Simulator
rules belong in service-terminal modules, not inside JSX.

## Simulation Loop

The first loop can be qualitative, but it must feel alive.

Loop responsibilities:

1. Advance the clock while the line is powered or active.
2. Apply seeded perturbations and scenario faults.
3. Evolve subsystem metrics from work order, controls, run state, and faults.
4. Derive visual geometry from state, not static decoration.
5. Move packet position and posture according to carry, hold, catch, release,
   and reset conditions.
6. Emit warnings and alarms once per condition.
7. Apply guards and constraints to controls.
8. Enter hold, recovery, abort, secure, or reuse-blocked states.
9. Produce a replayable trace and debrief.

Operator timing should matter. Late catch should change endpoint posture.
Overdriven support should increase source burden. Premature fade should produce
a release/catch conflict. Incomplete reset should leave visible residue.

## Outcomes

Terminal outcomes are operational, not quiz scores:

- secured nominal;
- secured with cautions;
- held;
- recovered;
- aborted;
- reuse blocked;
- lockout.

Debriefs should summarize the operational trace, limiting subsystems, alarms,
operator interventions, and recommended study links. They should not grade the
run like a multiple-choice attempt.

## Acceptance Criteria

The terminal redesign is acceptable when:

- the first viewport contains the live line, instrumentation, and core controls;
- ordinary operation does not require scrolling;
- work-order browsing is secondary rather than the main driver;
- no command stack, next-action button list, or phase-chip stepper drives the
  run;
- the central viewport is an active graphic readout, not a progress bar;
- support, source, endpoint, timing, reset, stability, packet, and authority
  are visible in the graphic or instrumentation;
- visual elements change because simulator state changes;
- there are no decorative triangles, static squiggles, or duplicate telemetry
  cards inside the line view;
- at least four failure modes produce visible subsystem changes before or during
  alarm state;
- autopilot/supervisor mode manipulates or points to real controls rather than
  posing quiz prompts;
- hold, recovery, abort, secure, and reuse-blocked states have distinct visual
  postures;
- service trace and debrief use operator language;
- the truth boundary is visible as `SIM / ARCHITECTURE LOGIC / NOT PHYSICS SOLVER`;
- no score, question count, quiz filter, or quiz-report language appears in the
  active terminal.

## Later Expansion

Future versions can add:

- multiple lines;
- scheduled service windows;
- richer seeded scenario libraries;
- incident replay;
- canvas field/particle layers;
- imported ledger/telemetry artifacts;
- instructor overlay mode;
- post-run Qualification Board recommendations;
- separate deployment route or package for the terminal.
