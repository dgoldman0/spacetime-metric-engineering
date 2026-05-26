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
architecture logic, operator procedure, subsystem state, and predicted failure
modes. It does not solve field equations, validate a physical plant, or claim
that active-rail service is physically realizable.

## Product Boundary

The training suite has two sibling products:

| Product | Primary Job | Data Model | Interface |
| --- | --- | --- | --- |
| Qualification Board | Teach and assess theory, references, claim boundaries, and active-rail vocabulary. | Question bank, grading, explanations, references. | Learning board. |
| Rail Service Terminal | Simulate operation of a single active-rail service line. | Work orders, line state, subsystem models, interlocks, alarms, event traces. | Operations terminal. |

The question bank can recommend study after a run. It cannot be the terminal's
main content model. The terminal's main loop is:

1. observe line state,
2. issue or hold authority,
3. watch subsystems evolve,
4. respond to warnings and interlocks,
5. secure or recover the line.

## Design Correction

The terminal must not be implemented as a quiz-like trainer panel.

Avoid these shapes:

- scenario cards that read like prompts or challenges;
- prose such as "find the degraded subsystem" in the main operating surface;
- big static panels where the learner presses the next authorized button;
- a line graphic that is only a fancy progress bar;
- work-order descriptions written as learning objectives;
- procedure lists that dominate the visual hierarchy;
- button catalogs, score language, "items ready", or quiz/report terminology.

Panel-based trainer aids are allowed only as secondary surfaces: tutorial
overlays, instructor mode, debrief review, or optional guided practice. The
default terminal should read as an operating system, not as a worksheet.

## Operator Role

The user is acting as a line engineer, not answering questions.

The operator should:

- read the active work order;
- inspect line readiness from visible instruments;
- bring support, source, endpoint, and reset subsystems into service;
- authorize or hold procedure transitions;
- monitor packet motion, support envelope, source load, endpoint state,
  timing drift, residue, and stability;
- respond to warnings before they become lockouts;
- abort when recovery authority is the correct operational choice;
- read the final trace after secure or abort.

The terminal can teach, but it teaches through instruments, alarms, interlocks,
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
- authority subsystem: operator clearance, interlocks, holds, abort authority;
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

Commands should be controls over the line, not answers to a prompt.

The command system should:

- show current authority clearly;
- make the next available authority visible;
- expose hold, abort, and reset where operationally appropriate;
- attach locked actions to the interlock or subsystem that blocks them;
- let the learner inspect why a command is unavailable;
- avoid showing every possible command as a large grid.

Commands may appear in an authority rail, subsystem controls, or a compact
command console. They should be visually subordinate to the live line and
instrumentation.

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
5. current authority controls.

Secondary inspection surfaces:

- work-order drawer;
- gate/interlock inspection;
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
- `lineProcedures.js`: phases, authority rules, gates, and interlocks.
- `failureModes.js`: failure rules, alarm text, recovery guidance.
- `lineSimulator.js`: reducer/state-machine functions.
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
  gates,
  activeInterlocks,
  alarms,
  eventPins,
  visualOverlays,
  events,
  debrief
}
```

The React component should render state and dispatch commands. Simulation rules
belong in the service-terminal model.

## Simulation Loop

The first loop can be deterministic with bounded drift, but it must feel alive.

Loop responsibilities:

1. Advance clock while the line is powered or active.
2. Evolve subsystem metrics according to phase, work order, and faults.
3. Update trend history and visual overlays.
4. Move packet state through operator-authorized phases.
5. Emit warnings and alarms once per condition.
6. Lock unsafe authority until gates clear.
7. Enter hold, abort, or recovery state when rules require it.
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
- live schematic layers;
- trend strips and subsystem markers;
- alarm colors with text labels;
- minimal explanatory prose during operation.

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
- a button-selection exercise.

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
- support, source, endpoint, reset, stability, packet, and authority states all
  have visible representations;
- at least four failure modes produce visible subsystem changes before or during
  alarm state;
- current authority is contextual but not the main visual object;
- secondary gates/events/debriefs do not dominate the first screen;
- a learner can infer the state of the line from the viewport and instruments;
- completion, hold, abort, and recovery have distinct visual postures;
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
