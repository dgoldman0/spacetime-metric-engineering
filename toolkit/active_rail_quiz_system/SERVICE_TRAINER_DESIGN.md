# Active-Rail Service Trainer Design

This document defines the Rail Service Terminal before implementation work. It
is intentionally separate from the quiz design because the service trainer is
not a quiz mode, not a question-bank view, and not a lightly restyled activity
card.

The target experience:

> A learner is dropped into the seat of an active-rail line engineer and asked
> to operate a single service line through a real-time training run.

The trainer is still honest about physics. It simulates current active-rail
architecture logic, procedural gates, and failure modes. It does not solve field
equations, simulate a validated plant, or claim physical realizability.

## Product Boundary

The training suite has two top-level products:

| Product | Purpose | Data Model | Interface |
| --- | --- | --- | --- |
| Qualification Board | Study, timed quiz, explanations, curriculum assessment. | Question bank, grading, explanations, references. | Learning board with filters, cards, reports. |
| Rail Service Terminal | Operate a line, manage readiness, respond to evolving state, recover from failures. | Service scenarios, line state, procedures, interlocks, events, failure rules. | Full operations terminal. |

The service trainer may link to quiz material after a run, but it must not rely
on quiz questions for its main interaction. Its primary loop is command, state
evolution, alarm, hold, recovery, and reset.

## User Role

The user is not answering questions. The user is acting as a line engineer.

The terminal should assume the user has an operator assignment:

- identify the active line,
- review the manifest and readiness gates,
- authorize or hold procedure steps,
- monitor telemetry,
- respond to alarms,
- decide when to abort,
- recover and reset the line,
- read the final service trace.

The trainer can still teach, but the teaching should happen through operational
consequence, terse advisories, event logs, and post-run debriefs. It should not
explain itself like an educational page while the run is active.

## Simulation Scope

The first trainer simulates one rail line. It is a qualitative state machine,
not a physics solver.

The trainer should model:

- line state: offline, standby, precheck, armed, supporting, carrying,
  catch-window, fading, decompressing, resetting, secured, held, aborted;
- packet state: staged, accepted, in service, handoff pending, rematched,
  released, secured;
- readiness gates: support permit, ledger closure, endpoint sync, reset clear,
  stability posture, operator authority;
- hidden state: support margin, source debt, endpoint confidence, timing drift,
  residue load, stability posture, thermal/control load;
- visible telemetry: operational bands and alarms rather than raw equations;
- event stream: timestamped procedure, advisory, warning, alarm, and lockout
  entries;
- failure rules: support gap, source overdraw, endpoint mismatch, timing
  violation, fade-before-catch, decompression shock, reset contamination,
  stability lockout, operator overrun.

The trainer should not model:

- real spacetime curvature,
- exact stress-energy tensors,
- physical source closure,
- actual hardware,
- real safety certification.

## Terminal Information Architecture

The service trainer should use a full operations terminal layout, not the quiz
workspace panel.

Required first-screen regions:

- **Top Status Bar:** line id, manifest id, simulation clock, current state,
  authority, alarm count.
- **Line Schematic:** dominant central strip showing rail phases, packet
  position, support envelope, endpoint status, and phase progress.
- **Telemetry Stack:** compact gauges or bars for support, ledger, endpoint,
  drift, residue, stability, and load.
- **Command Stack:** only currently relevant operator commands, with disabled
  controls shown as interlocked rather than hidden.
- **Procedure Checklist:** current operating procedure with satisfied, pending,
  bypassed, and failed gates.
- **Alarm/Event Log:** dense terminal-like feed with timestamps, severity, and
  subsystem.
- **Run Debrief:** appears after secure or abort, summarizing service outcome,
  triggered failures, recovery requirements, and optional study links.

Avoid:

- large explanatory hero panels,
- quiz-style cards,
- profile card galleries,
- right-rail quiz filters,
- ordinary score panels,
- language like "items ready" in the service terminal,
- static "set parameters and check" interaction.

## Operator Controls

Controls are procedural and authority-based.

Examples:

- accept manifest,
- run precheck,
- precharge support,
- close source ledger,
- synchronize endpoint,
- arm line,
- start support,
- begin carry,
- hold line,
- resume line,
- catch/rematch,
- authorize fade,
- decompress,
- flush reset path,
- reset line,
- secure service,
- abort.

Controls can be disabled by interlocks. Disabled controls should say why:

- support permit missing,
- endpoint sync stale,
- ledger closure below gate,
- catch not confirmed,
- residue above reuse threshold,
- line held,
- recovery required.

The interface should never ask the user to type hidden numeric state directly.
Preset service manifests are acceptable. Procedure choices are acceptable.
Manual override can exist later, but it must produce explicit trace and risk
entries.

## Service Manifests

The first version should include a small set of operator manifests. These are
not quiz cards; they are run presets loaded into the terminal.

Initial manifests:

- inspection crawl: low burden, wide catch window, forgiving training run;
- standard packet: nominal service burden;
- tight-window handoff: timing and endpoint sync are fragile;
- heavy packet: source debt and support margin are stressed;
- post-reset reuse: residue and reset gate are stressed;
- fault-injection drill: one hidden subsystem begins degraded.

Each manifest should define:

- manifest id,
- operator-facing description,
- initial line state,
- hidden state seeds,
- active fault biases,
- expected operating discipline,
- completion and abort conditions.

## Data Model

Use a separate service-trainer data model.

Suggested modules:

- `serviceProfiles.js`: manifests and initial conditions.
- `lineProcedures.js`: phase definitions, gates, commands, and interlocks.
- `failureModes.js`: failure rules, alarm text, recovery guidance.
- `lineSimulator.js`: reducer/state-machine functions.

Suggested state shape:

```js
{
  manifestId,
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
  gates: {
    supportPermit,
    ledgerClosed,
    endpointSynced,
    catchConfirmed,
    fadeAuthorized,
    resetClear
  },
  activeInterlocks,
  alarms,
  events,
  completedProcedures,
  failedProcedures
}
```

The reducer should handle all terminal commands. The component should render
state; it should not contain the simulation rules inline.

## Simulation Loop

The first loop can be deterministic with small bounded drift. It should still
feel alive.

Loop responsibilities:

1. Advance clock while the line is armed/running.
2. Degrade or recover hidden state according to phase and manifest.
3. Check interlocks and gates.
4. Emit alarms and event log entries once, not every tick.
5. Move packet/line phase only through operator commands.
6. Lock unsafe commands until required procedures complete.
7. Enter abort/recovery state when a red failure rule fires.
8. Produce a run debrief after secure or abort.

Operator timing should matter. If the operator waits too long during carry
without endpoint sync, drift should increase. If fade is authorized before catch
confirmation, the trainer should refuse or alarm depending on authority mode.
If reset is skipped after residue buildup, reuse should begin degraded.

## Visual Direction

The service terminal needs its own visual language.

Direction:

- dark operational console or high-contrast industrial terminal;
- compact typography;
- dense but readable panels;
- status lamps, strips, and meters;
- terminal-style event feed;
- subdued color with strong alarm colors;
- little to no explanatory body copy during operation;
- no marketing-card composition;
- no quiz badges except optional post-run study links.

The first glance should communicate:

- what line is active,
- whether it is safe,
- what phase it is in,
- what command is next,
- what subsystem is warning.

## Truth Boundary In UI

The terminal should include a boundary marker, but it should be operationally
styled, not a teaching paragraph.

Example:

`SIM TRAINER / ARCHITECTURE LOGIC / NOT PHYSICS SOLVER`

This marker can live in the top status bar or footer. Detailed caveats belong in
documentation and post-run debrief, not in the active command surface.

## MVP Acceptance Criteria

The first replacement is successful when:

- selecting Rail Service Terminal removes the quiz filter/report shell;
- the terminal fills the working area as an operations console;
- the user can load a manifest and run a single line through service phases;
- line state evolves over time;
- commands unlock and lock based on gates and state;
- telemetry changes during the run;
- at least four meaningful failure modes can occur from operator behavior or
  manifest stress;
- alarms and event logs explain what happened in operator language;
- completion and abort produce different debriefs;
- the UI does not look or feel like a quiz workspace.

## Later Expansion

Future versions can add:

- multiple lines,
- scheduled service windows,
- replay mode,
- operator authorization modes,
- incident investigation,
- richer line schematics,
- ledger/telemetry artifacts,
- post-run links into the qualification question bank,
- authored training missions.
