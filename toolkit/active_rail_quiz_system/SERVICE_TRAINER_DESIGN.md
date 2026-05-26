# Rail Service Terminal Simulation Design

This document defines the Rail Service Terminal as a first-class simulation
surface. It is not a quiz mode, not a question-bank activity, and not a set of
training cards with a rail-themed skin.

Target experience:

> The learner sits down at an active-rail service terminal as the assigned line
> engineer. A single rail line is alive on screen. The operator monitors the
> line, authorizes service, reacts to subsystem state, and either secures the
> run or enters recovery.

The terminal remains honest about physics. It simulates current active-rail
architecture logic, operator controls, subsystem state, and predicted failure
modes. It does not solve field equations, validate a physical plant, or claim
that active-rail service is physically realizable.

## Product Boundary

The training suite has two sibling products:

| Product | Primary Job | Data Model | Interface |
| --- | --- | --- | --- |
| Qualification Board | Teach and assess theory, references, claim boundaries, and active-rail vocabulary. | Question bank, grading, explanations, references. | Learning board. |
| Rail Service Terminal | Simulate operation of a single active-rail service line. | Work orders, line state, live controls, subsystem models, constraints, alarms, event traces. | Operations terminal. |

The question bank can recommend study after a run. It cannot be the terminal's
main content model. The terminal's main loop is:

1. observe line state,
2. adjust live controls,
3. watch subsystems evolve,
4. respond to warnings, constraints, and degraded margins,
5. secure, hold, abort, or recover the line.

## Design Correction

The terminal must not be implemented as a quiz-like trainer panel.

Avoid these shapes:

- scenario cards that read like prompts or challenges;
- prose such as "find the degraded subsystem" in the main operating surface;
- big static panels where the learner presses the next authorized button;
- a line graphic that is only a fancy progress bar;
- work-order descriptions written as learning objectives;
- procedure lists that dominate the visual hierarchy;
- phase chips that act like quiz progress steps;
- command stacks where the user repeatedly clicks the next enabled action;
- button catalogs, score language, "items ready", or quiz/report terminology.

Panel-based trainer aids are allowed only as secondary surfaces: tutorial
overlays, instructor mode, debrief review, or optional guided practice. The
default terminal should read as an operating system, not as a worksheet.

## Operator Role

The user is acting as a line engineer, not answering questions.

The operator should:

- read the active work order;
- inspect line readiness from visible instruments;
- manipulate support, source, endpoint, release, decompression, and reset
  controls;
- monitor packet motion, support envelope, source load, endpoint state,
  timing drift, residue, and stability;
- use hold, abort, recovery, and secure authority when the line state demands
  it;
- respond to warnings before they become lockouts;
- read the final trace after secure or abort.

The terminal can teach, but it teaches through instruments, alarms, constraints,
trace entries, and debriefs. During a run, explanatory paragraphs should give
way to operational labels and subsystem state.

## Simulation Scope

The first terminal simulates one rail line. It is a qualitative architecture
simulation, not a physics solver.

It should model:

- line state: offline, standby, precheck, armed, supporting, carrying,
  catch-window, fading, decompressing, resetting, secured, held, aborted;
- packet state: staged, accepted, in-service, handoff pending, rematched,
  released, secured, recovery;
- support subsystem: support envelope strength, margin, gaps, containment;
- source subsystem: source debt, ledger closure, overdraw, conservation
  residual;
- endpoint subsystem: catch window, rematch confidence, timing drift;
- reset subsystem: decompression order, residue, reuse readiness;
- stability subsystem: posture, backreaction warning, lockout;
- authority subsystem: operating clearance, live-control limits, holds, abort
  authority, secure authority;
- event stream: timestamped operational events, warnings, alarms, and recovery
  notes.

It should not model:

- exact spacetime curvature;
- exact stress-energy tensors;
- physical source closure;
- actual hardware;
- certified safety.

## Visual Simulation Model

The central viewport is the simulation. It should look like an active line, not
a decorative progress bar.

The viewport should read as an aesthetically finished graphic instrument. It
should let the learner feel the corridor geometry and service evolution:
envelope shape, packet motion, source loading, catch aperture, drift shear,
residue haze, warning pins, and recovery posture. It must not become another
numeric dashboard.

Numbers belong in the instrumentation cluster. The central viewport should use
graphic layers first and text only where it labels a geometric feature. Avoid
placing duplicate telemetry cards, percentage blocks, explanatory text boxes,
or large UI panels on top of the line. A short phase tag or alarm pin is fine;
six boxed readouts inside the rail view are not.

Required visible objects:

- **Rail corridor:** a bounded spatial route from origin to endpoint, with
  service-zone markers and active phase regions.
- **Packet:** a moving body with position, motion state, handoff state, and
  hold/recovery visual state.
- **Support envelope:** a visible field around the service corridor. It changes
  thickness, brightness, fracture, or continuity as support margin changes.
- **Source/ledger channel:** a visible burden stream or side channel. It should
  show debt, overdraw, and closure state without exposing raw equations.
- **Endpoint/catch window:** a receiving region with sync confidence, catch
  aperture, rematch lock, and timing drift.
- **Reset path:** residue and decompression state that appears after fade and
  controls reuse readiness.
- **Alarm pins:** warnings attached to the subsystem they affect, not generic
  messages floating over the line.
- **Telemetry traces:** small live trends or sparkline bands for key subsystem
  values, so the operator can see state changing rather than only reading
  percentage bars.

Implementation preference:

- Use SVG for the first rich schematic: rails, envelopes, apertures, packet
  motion, pins, masks, gradients, and state-driven geometry.
- Use CSS animation for simple motion and state transitions.
- Add canvas later if particles, field noise, heat maps, or denser transient
  effects need a raster layer.
- Do not approximate the graphic readout by adding more HTML cards inside the
  viewport.

The viewport must show useful state even before work-order acceptance:

- line powered or offline state;
- staged packet at origin;
- endpoint waiting state;
- initial support/source/reset condition;
- current authority marker.

During active service:

- packet motion is visible;
- support envelope evolves continuously;
- drift, source load, and residue leave visual traces;
- warnings attach to the affected subsystem;
- hold freezes motion and marks the held subsystem;
- abort changes the whole line into recovery posture.

## Instrumentation

Telemetry should feel like instrumentation, not grading feedback.

Visible instrumentation should include:

- support margin;
- source debt or source load;
- endpoint confidence;
- timing drift;
- reset residue;
- stability posture;
- load index;
- alarm count and severity;
- current authority state.

Percentages are acceptable as supporting data, but they are not enough. At least
some instruments should show direction or recent history: rising, falling,
steady, recovering, or crossing a caution band.

Instrumentation should stay outside or adjacent to the central viewport. If a
metric is already shown in the telemetry cluster, it should not be repeated as a
large numeric card inside the line graphic. The viewport may encode that metric
through shape, color, opacity, motion, thickness, deformation, or pin location.

## Work Orders

Service manifests should be treated as operational work orders, not quiz prompts.

A work order may include:

- work-order id;
- line id;
- packet class;
- service window;
- load class;
- reuse status;
- known cautions;
- hidden fault seeds for training runs;
- operator authority level;
- completion and abort conditions.

The operator-facing language should be terse and terminal-like.

Good:

- `Endpoint confidence degraded at load. Monitor catch margin.`
- `Reuse path carries residual from prior reset.`
- `Heavy packet: source load expected above nominal.`

Avoid:

- `Find the degraded subsystem.`
- `Keep the run inside recovery authority.`
- `Which action is correct?`
- anything that sounds like a puzzle prompt or exam instruction.

## Operator Interaction

The terminal interaction model is live operation, not command selection.

The operator should manipulate a small set of persistent controls whose meaning
stays visible throughout the run:

- support envelope drive or stabilizer control;
- source/ledger closure or source-load control;
- endpoint sync and catch-aperture control;
- carry/release authority tied to line readiness;
- fade and decompression control;
- reset purge and residue-clearance control;
- hold, abort, and secure controls.

These controls are not quiz answers and they are not a step-by-step command
stack. They should look and behave like line controls: sliders, guarded
switches, levers, rotary/segmented controls, status lamps, hold toggles, and
emergency authority controls. The operator should adjust the line, then watch
the simulator respond.

Interlocks are system constraints, not disabled answer choices. A constraint
should attach to the subsystem or control it limits: for example, the endpoint
catch aperture may refuse to open, the release control may stay guarded, or the
reset path may remain contaminated. The learner can inspect why a constraint is
active, but the main surface should not be a grid of locked buttons.

The visible model should avoid "next authorized action" as the primary pattern.
The terminal may indicate current authority, but authority should narrow or
expand available controls rather than present a single button to click next.

The terminal should not ask the operator to type raw hidden-state values. Manual
override may be added later, but it must leave an event trace and explicit risk
record.

## Information Architecture

The first screen should be a working terminal.

Primary operating view:

1. suite/product status strip;
2. line status strip;
3. central live line simulation;
4. right or lower instrumentation cluster;
5. persistent operator-control deck.

Secondary inspection surfaces:

- work-order drawer;
- constraint/interlock inspection;
- event trace;
- advisory/watch floor;
- debrief/replay.

Secondary surfaces may be drawers, tabs, or bounded consoles. They should not
stretch the terminal into a tall wall of panels. Scrolling should reveal
inspection detail, not the missing core simulation.

## Data Model

Use a separate service-terminal model.

Suggested modules:

- `workOrders.js`: operational work orders and initial conditions.
- `lineControls.js`: live controls, authority rules, guards, and constraints.
- `failureModes.js`: failure rules, alarm text, recovery guidance.
- `lineSimulator.js`: continuous line-state update functions.
- later `visualState.js`: derived viewport geometry, alarm pins, trends, and
  subsystem overlays.

Suggested state shape:

```js
{
  workOrderId,
  lineId,
  clock,
  runState,
  phase,
  packetState,
  authorityState,
  metrics: {
    supportMargin,
    sourceDebt,
    endpointConfidence,
    timingDrift,
    resetResidue,
    stabilityPosture,
    loadIndex
  },
  trends: {
    supportMargin,
    sourceDebt,
    endpointConfidence,
    timingDrift,
    resetResidue,
    stabilityPosture,
    loadIndex
  },
  controls: {
    supportDrive,
    ledgerClosure,
    endpointSync,
    catchAperture,
    releaseFade,
    decompression,
    resetPurge,
    hold,
    abort,
    secure
  },
  constraints,
  guards,
  alarms,
  eventPins,
  visualOverlays,
  events,
  debrief
}
```

The React component should render state and dispatch control changes.
Simulation rules belong in the service-terminal model.

## Simulation Loop

The first loop can be deterministic with bounded drift, but it must feel alive.

Loop responsibilities:

1. Advance clock while the line is powered or active.
2. Evolve subsystem metrics according to work order, control inputs, operating
   state, and faults.
3. Update trend history and visual overlays.
4. Move packet state according to support, source, endpoint, and release
   conditions rather than a fixed button sequence.
5. Emit warnings and alarms once per condition.
6. Apply guards and constraints to risky controls.
7. Enter hold, abort, recovery, or secure state when rules require it.
8. Produce a debrief and replayable trace after secure or abort.

Operator timing should matter. Waiting too long in carry can increase drift.
Failing to recover support can fracture the envelope. Skipping reset cleanup can
make reuse visibly degraded.

## Failure Visualization

Failures must be visible in the simulation, not only listed in text.

Examples:

- support gap: envelope thins, breaks, or opens around the corridor;
- source overdraw: source channel saturates and turns caution/red;
- endpoint mismatch: catch aperture narrows or loses lock;
- timing violation: packet and endpoint markers drift out of phase;
- fade before catch: release path warns or locks;
- decompression shock: support unload trace spikes;
- reset contamination: residue remains on the reset path;
- stability lockout: global terminal posture changes and authority narrows;
- conservation residual: source/ledger channel flags a residual marker.

The event trace should explain the operational consequence, but the viewport
should show where the problem is.

## Visual Direction

The terminal should use an industrial operations style:

- dark or high-contrast working background;
- compact, legible typography;
- status lamps and caution bands;
- live schematic layers with polished graphic geometry;
- trend strips and subsystem markers;
- alarm colors with text labels;
- minimal explanatory prose during operation.

The line view should feel more like a beautiful technical readout than a web
dashboard. It should prefer drawn paths, fields, masks, glows, traces, apertures,
and moving bodies over stacked boxes. Text labels are subordinate to geometry.

The first glance should communicate:

- which line is active;
- what phase it is in;
- where the packet is;
- whether support/source/endpoint/reset/stability are nominal;
- what authority is currently available;
- which subsystem is warning.

The first glance should not communicate:

- a quiz page;
- a settings panel;
- a deck of training cards;
- a button-selection exercise;
- a phase-progress strip.

## Truth Boundary In UI

The terminal should include a compact boundary marker:

`SIM / ARCHITECTURE LOGIC / NOT PHYSICS SOLVER`

Detailed caveats belong in documentation and post-run debriefs, not in the
active operating surface.

## Acceptance Criteria

The terminal design is acceptable when:

- selecting Rail Service Terminal removes the quiz filter/report shell;
- work orders do not read like quiz prompts;
- the central viewport is a true live schematic with multiple visible
  subsystems, not only a packet progress bar;
- the central viewport does not duplicate side telemetry as embedded numeric
  cards or text-box clusters;
- support/source/endpoint/reset/timing/stability are expressed graphically
  through geometry, fields, overlays, traces, pins, or motion;
- support, source, endpoint, reset, stability, packet, and authority states all
  have visible representations;
- at least four failure modes produce visible subsystem changes before or during
  alarm state;
- persistent operator controls drive the simulator instead of a visible command
  stack or next-action button sequence;
- secondary constraint/event/debrief inspection does not dominate the first
  screen;
- a learner can infer the state of the line from the viewport and instruments;
- completion, hold, abort, and recovery have distinct visual postures;
- controls, constraints, and visual feedback fit in the primary viewport without
  forcing the operator to scroll to operate the line;
- no score, question, or quiz-language appears in the active terminal.

## Later Expansion

Future versions can add:

- multiple lines;
- scheduled service windows;
- replay mode;
- incident investigation;
- richer schematic layers;
- instructor overlays;
- ledger/telemetry artifact import;
- post-run links into Qualification Board study sets;
- authored missions.
