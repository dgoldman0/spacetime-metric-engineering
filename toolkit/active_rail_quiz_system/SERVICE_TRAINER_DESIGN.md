# Rail Service Terminal Design

This document is the source of truth for the Rail Service Terminal. The
terminal is a first-class product in the active-rail training suite, not a quiz
mode and not a themed question workspace.

Target experience:

> The learner sits down as the assigned line engineer at a future active-rail
> service terminal. A single line is alive. The operator observes the geometry,
> moves persistent controls, watches subsystem state evolve, responds to
> limits, and secures, holds, recovers, or aborts the run.

The terminal remains honest about physics. It is a qualitative
architecture-logic and operations simulator. It does not solve the Einstein
equation, validate a matter action, certify a physical plant, compute true null
geodesics, detect actual horizons, or identify CTCs. It can, however, represent
the current active-rail component architecture much more honestly than a quiz
panel or progress strip.

## Product Boundary

The training suite has two sibling products:

| Product | Primary Job | Data Model | Interface |
| --- | --- | --- | --- |
| Qualification Board | Teach and assess theory, references, claim boundaries, and active-rail vocabulary. | Question bank, grading, explanations, references. | Learning board. |
| Rail Service Terminal | Simulate operation of one active-rail line. | Line state, work orders, component controls, subsystem models, visual state, alarms, traces, debriefs. | Operations terminal. |

The question bank can recommend study after a terminal run. It cannot drive the
terminal's main loop. The terminal loop is:

1. observe the live line and active component state;
2. manipulate persistent operational controls;
3. watch subsystem state evolve;
4. respond to limits, warnings, and failures;
5. secure, hold, recover, or abort.

## Technical Truth Boundary

The terminal should aim for a high-fidelity service representation and a
low-fidelity physics representation.

Reasonable target:

- 75-85% faithful to the current active-rail architecture as an operator
  terminal: components, staging, diagnostics, failure modes, and qualitative
  feedback.
- 0% faithful as a numerical spacetime solver: no actual coupled
  Einstein-matter evolution, no validated semiclassical response, no real
  geodesic integration, no physical CTC/horizon detection.

The UI must expose this boundary. Labels should say `architecture logic`,
`carrier audit risk`, `packet isolation proxy`, `causal-access risk`, or
`chronology guard`, not `physics solved`, `horizon detected`, or `CTC detected`.

## Architecture Grounding

The terminal is grounded in the current disclosure and component-design track.
Its visible systems should map to the active-rail component stack rather than to
generic health bars.

| Active-Rail Component | Terminal Role | Visual Expression | Operator Controls |
| --- | --- | --- | --- |
| Live packet corridor | Protected passenger/payload bore inside the service plant. | Quiet inner corridor, packet body, packet isolation/leakage margin, packet loss warnings. | Hold, abort, isolation guard, packet monitor override in later diagnostic mode. |
| Standing support substrate / radial backbone | Prepared railbed carrying baseline throat, radial, angular, and lapse support. | Baseline support field behind the active envelope; readiness bands at origin/endpoint. | Substrate readiness and support precharge controls. |
| Support-shell metric actuator layer | Annular programmable shell for carrying-flow, clock-lapse cushion, rail-stretch, and throat-capacity scheduling. | Active support envelope, flow-front, lapse/rail/throat bands, deformation under load. | Support drive, clock-lapse cushion, rail-stretch trim, throat-capacity trim. |
| Handoff, rematch, and carrier collar | Entry/catch/hold/release impedance-transformer around packet edge. | Entry gate, beta-collar/rematch sleeve, catch ring, packet-edge trim, matched-hold state. | Entry gate, carrier drive, rematch/collar trim, matched hold, release fade. |
| Endpoint receiver and reset plant | Station-end receiver, beta-memory store, reset cap, support-edge closure, decompression plant. | Endpoint receiver body, catch aperture, reset/decompression path, residue haze, wake-tail monitor. | Endpoint sync, catch aperture, decompression, reset purge, secure. |
| Regulated heat/current medium and support reservoir | Endpoint/support source plant with bounded heat/current exchange and reservoir behavior. | Medium flow, reservoir charge, limiter state, heat/current routing, support exchange closure. | Medium coupling, reservoir draw, limiter guard, source-response trim. |
| Carrier governance and diagnostics | Supervisory timing, carrier, reachability, chronology, and rail-time safety system. | Rail-time ruler, branch-band probe fan, causal-access overlay, chronology guard, alarms. | Arm, rail-time governor, supervisor/autopilot, hold/resume, abort/recovery. |

The terminal should also surface the four metric-service variables as component
channels where useful:

- carrying-flow field `beta`: service load and carry action;
- clock-lapse field `alpha`: causal/timing cushion;
- rail-stretch field `gamma_ll`: radial metric capacity;
- throat-capacity field `gamma_OmegaOmega`: angular/throat support.

These are not raw equation-entry controls. They are operator-facing actuator
families with readable names and diagnostic details available in drawers.

## Ledger Semantics

The active-rail disclosure uses ledgers, but ledgers are diagnostics and
accounting artifacts. They are not physical knobs.

Terminal rule:

- A demanded-source ledger is an audit/readout of source demand for a
  prescribed architecture.
- A constraint ledger is a diagnostic surface for consistency and margin.
- A service-time ledger is an operational comparison record.
- A carrier ledger is an audit of reachability, branch behavior, probes, and
  wake-tail restoration.

Do not put `Ledger Closure` in the primary operator controls. Use physical or
operational controls such as:

- `Source Response Trim`;
- `Medium Coupling`;
- `Support Exchange`;
- `Reservoir Draw`;
- `Endpoint Current Limit`;
- `Closure Audit` as an inspection/readout, not a live actuator.

Ledger material belongs in:

- diagnostics drawers;
- debrief/audit trails;
- source-demand overlays;
- reference links from the Qualification Board.

## Primary Operating Surface

The primary operating surface presents a working line terminal. Its structure is
defined by live service state, direct controls, and graphic subsystem feedback.

The primary operating surface excludes these patterns:

- a work-order list that drives the whole experience;
- `drill`, puzzle, or quiz-prompt language as the main framing;
- a visible command stack or next-action button sequence;
- phase chips used as the operator's main interaction;
- big origin/endpoint text boxes that occupy space without doing visual work;
- static decorative curves that do not reflect state;
- generic triangles or stickers presented as visualization;
- duplicate percentage cards inside the line graphic;
- tall layouts where the operator must scroll to find core controls;
- any wording that makes the active run feel like a graded question attempt.

Scenario setup, guided practice, incident replay, and instructor challenges are
allowed as secondary modes. They must not be the default operating surface.

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
aesthetically finished instrument that shows service geometry and component
evolution. The graphic should make the operator feel the corridor, support
field, endpoint receiver, and reset plant before reading a number.

Required live layers:

- **service corridor:** protected route and active interval;
- **live packet:** packet body, packet isolation, packet leakage/loss warning,
  hold/carry/catch/release posture;
- **standing substrate:** quiet prepared railbed/readiness background;
- **support envelope:** active support-shell field whose thickness, continuity,
  brightness, and distortion change with support state;
- **metric actuator channels:** beta/carrying-flow, clock-lapse cushion,
  rail-stretch, and throat-capacity bands where the scenario calls for them;
- **source-response channel:** side channel showing demanded-source burden,
  saturation, support exchange, reservoir draw, and overdraw;
- **endpoint receiver:** catch/rematch aperture, endpoint phase, beta-memory
  receiver, current-limit/medium state;
- **carrier/collar layer:** entry gate, rematch sleeve, catch ring, matched
  hold, release fade;
- **timing shear:** state-derived phase offset or shear bands, not static
  ornament;
- **reset residue:** haze/debris/decay along the reset/decompression path that
  visibly clears or contaminates reuse;
- **constraint/backreaction posture:** guard or boundary layer that tightens
  when constraints, load, or stability limits narrow authority;
- **carrier/chronology overlays:** branch-band probe fan, causal-access risk,
  rail-time guard, and chronology guard when relevant;
- **alarm localization:** warnings attached to the subsystem that is actually
  degraded.

The graphic must avoid:

- static squiggles that never change;
- arbitrary triangles or shapes that are not tied to a subsystem state;
- overlaying dashboard cards inside the line;
- repeating the same percentage values already shown in instrumentation;
- labels that cover the geometry they claim to explain;
- any line that implies a command signal from the entry station to the packet.

Text inside the graphic should be sparse: station names, subsystem labels,
phase/status tags, and short localized warning tags.

## Packet Trace And Causal Honesty

The active rail is not a traversable wormhole, and the visual model must not
imply that an entrance signal reaches out and drags the packet forward.

Use these rules:

- A line behind the packet is a **packet service trace**, **carry history**, or
  **wake-tail trace**, not a singular control signal.
- If a `worldline` label appears, it must mean a schematic service-coordinate
  history of the packet, not a computed geodesic and not an information channel.
- Optics/ray-bundle visuals are diagnostic probes or carrier-audit heuristics.
  They are not actual null geodesics unless a future solver exists and the UI
  says so.
- Entry, catch, rematch, release, and reset behavior should be represented as
  local component interactions at the relevant stations/collars.
- Packet loss and leakage should be explicit visual risks: isolation fade,
  packet-center coupling, bore leakage, packet norm margin, or abort threshold
  indicators.

## Spacetime Visual Simulation Grammar

The viewport should feel like a spacetime-engineering instrument, not a
mechanical conveyor diagram. It shows a qualitative geometry: an active
corridor, a packet service trace, source-response burden, endpoint optics,
support-shell posture, and carrier/constraint risk.

The visual grammar is heuristic and diagnostic. It represents architecture logic
and known concern classes; it does not numerically solve curvature, geodesics,
semiclassical backreaction, horizons, or chronology formation.

| Layer | What It Shows | State Drivers | Animation Shape | Boundary |
| --- | --- | --- | --- | --- |
| Service corridor | Protected route and active interval. | work order, support shell, packet isolation, service state | Corridor opens from a thin standby spine into a supported bore; leakage or loss narrows/desaturates the packet-safe region. | Schematic service geometry, not a solved metric. |
| Packet service trace | Packet position, carry history, hold, catch, release, recovery. | packet position, carry drive, hold/recovery, timing drift | Packet moves with a short trace; hold freezes it; recovery kinks or quarantines it. | Service-coordinate trace, not a command signal or geodesic solve. |
| Standing substrate | Prepared baseline support. | work order, readiness, support precharge | Quiet background railbed or station-to-station frame brightens as readiness improves. | Prepared plant proxy. |
| Support envelope | Active support-shell adequacy. | support drive, support margin, load index, stability | Envelope thickens, thins, breathes, fractures, or ripples under stress. | Support adequacy proxy, not a material solution. |
| Metric actuator channels | Beta, lapse, rail-stretch, throat-capacity role separation. | actuator controls, service state, constraints | Separated bands or flow fronts shift, cushion, stretch, or ring the corridor. | Operator abstraction of ADM channels. |
| Source-response channel | Source demand, support exchange, reservoir draw, overdraw. | source debt, medium coupling, reservoir, load | Side flow saturates, drains, leaves residual knots, or overheats. | Demanded-source/source-family proxy, not proof of matter closure. |
| Endpoint receiver | Catch/rematch, endpoint phase, aperture, beta-memory receiver. | endpoint sync, catch aperture, packet position, timing drift | Receiver rings align, widen, narrow, or miss; catch ring locks around packet edge. | Endpoint operation proxy. |
| Optics/carrier probes | Access and branch-band audit posture. | endpoint confidence, timing drift, carrier governance, scenario flags | Ray/probe bundles converge, shear, defocus, or compress near risk boundaries. | Probe heuristic, not null-geodesic integration. |
| Timing shear | Packet/endpoint phase mismatch. | timing drift, endpoint sync, carrier drive | Gridlines, probe bundles, or receiver rings shear relative to the packet trace. | Timing-risk proxy. |
| Backreaction/constraint posture | Stability, load coupling, and constraint stress. | stability, load index, source burden, support margin | Guard bands tighten, global envelope breathes unevenly, source channel drags. | Review-burden warning, not backreaction calculation. |
| Horizon/causal-access risk | Horizon-like access concern in risky service regimes. | service factor, high-risk scenario, timing drift, endpoint confidence | One-way-looking veil or compressed reachability fan appears near catch/release. | Risk overlay, not horizon detection. |
| Chronology guard | Rail-time or closed-curve scheduling concern. | rail-time policy, network scenario, release/fade state | Guard band or loop-warning overlay appears only in relevant scenario mode. | Chronology training guard, not CTC detection. |
| Reset residue | Decompression and reuse readiness. | reset residue, decompression, reset purge, release fade | Haze trails the corridor and clears with purge; contamination clings to endpoint/support. | Operational residue proxy. |

These layers should be animated from the same simulator state. If the state does
not change, the geometry should settle rather than perform decorative motion.

## Instrumentation

Instrumentation supports the graphic. It does not replace it.

Required instruments:

- packet isolation / leakage margin;
- support margin;
- source-response burden / source debt;
- endpoint confidence;
- timing drift;
- reset residue;
- stability posture;
- load index;
- reservoir charge or medium headroom;
- causal/carrier risk;
- alarm count/severity;
- operating authority.

At least some instruments should show trend, band, and direction: rising,
falling, steady, recovering, caution, lockout.

## Control Model

The terminal interaction model is live operation. Controls are persistent
instruments, not answers and not a next-action list.

Primary controls:

- support precharge / support drive;
- clock-lapse cushion;
- rail-stretch trim;
- throat-capacity trim;
- source-response trim or medium coupling;
- support reservoir draw / exchange;
- endpoint sync;
- catch/rematch aperture;
- carrier drive;
- matched hold;
- release fade;
- decompression;
- reset purge;
- rail-time governor / arm;
- hold/resume;
- abort/recovery;
- secure line.

Controls may be sliders, guarded switches, levers, rotary controls, toggles, or
compact button controls depending on the action. The key rule is that the
operator is manipulating a live line, not selecting the next command from a
list.

Constraints should appear as:

- guarded controls;
- clipped control ranges;
- warning lamps on the relevant control;
- control resistance or delayed response;
- visible changes in the affected subsystem;
- inspection drawers that explain why a guard is active.

The main UI should not become a grid of disabled buttons.

## Service Operation

A complete nominal service should be discoverable from the terminal itself.

Nominal service stages:

1. assignment received and work order accepted;
2. standing substrate/support shell brought into readiness;
3. metric actuator channels shaped for the service rating;
4. source-response/medium/reservoir posture brought inside operating headroom;
5. endpoint receiver synchronized and catch/rematch aperture prepared;
6. rail-time governor arms the line;
7. entry gate admits live service;
8. carrier drive carries the packet through the supported corridor;
9. catch/rematch collar secures packet edge at the endpoint;
10. matched hold and release fade withdraw the carrier;
11. decompression and reset plant clear support-edge and wake-tail residue;
12. secure or block reuse based on residue, leakage, and debrief state.

The operator should be able to run this manually. Autopilot should demonstrate
the same operations without hiding controls.

## Autopilot, Supervisor, And Randomness

Autopilot is a visible control-law demonstration:

- it manipulates the same controls available to the operator;
- it leaves an event trace;
- it can be paused or handed back to manual control;
- it should explain actions tersely in operational language;
- it must not hide failures or silently solve the run.

Supervisor mode is advisory:

- it highlights the next operational concern;
- it points to a subsystem, control, guard, or visual layer;
- it should not present a puzzle prompt or a single correct-answer button.

Randomness should be bounded and replayable:

- each work order has a seed;
- perturbations include source-load fluctuation, endpoint timing drift, support
  disturbance, reset residue, packet leakage, reservoir sag, and stability
  caution;
- the same seed should replay the same sequence for review;
- random faults should manifest visually before or during alarm state.

## Work Orders And Scenarios

Work orders are operational assignments. They should be terse and terminal-like.

Good examples:

- `Endpoint confidence degraded at load. Monitor catch margin.`
- `Reuse path carries residual from prior reset.`
- `Heavy packet: source response expected above nominal.`

Avoid:

- `Find the degraded subsystem.`
- `Keep the run inside recovery authority.`
- `Which action is correct?`
- `Fault-Injection Drill` as the normal operating language.

The scenario/fault library can remain as a secondary instructor component. It
may include guided drills, incident replays, and specific fault injections, but
the main terminal should open as a live assigned line, not as a drill list.

## Data Model

Use a separate service-terminal model. Suggested modules:

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
  serviceFactor,
  runState,
  packetState,
  authorityState,
  components: {
    livePacketCorridor,
    standingSubstrate,
    supportShell,
    metricActuators,
    handoffCollar,
    endpointReceiver,
    resetPlant,
    heatCurrentMedium,
    supportReservoir,
    carrierGovernance
  },
  controls: {
    supportDrive,
    clockLapseCushion,
    railStretchTrim,
    throatCapacityTrim,
    sourceResponseTrim,
    mediumCoupling,
    reservoirDraw,
    endpointSync,
    catchAperture,
    carrierDrive,
    matchedHold,
    releaseFade,
    decompression,
    resetPurge,
    railTimeGovernor,
    hold,
    abort,
    secure
  },
  metrics: {
    packetIsolation,
    packetLeakage,
    supportMargin,
    sourceBurden,
    endpointConfidence,
    timingDrift,
    resetResidue,
    stabilityPosture,
    loadIndex,
    reservoirCharge,
    causalRisk
  },
  trends,
  guards,
  alarms,
  visualState,
  diagnosticLedgers,
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
3. Evolve component metrics from work order, controls, run state, and faults.
4. Derive visual geometry from state, not static decoration.
5. Move packet position and posture according to carry, hold, catch, release,
   and reset conditions.
6. Track packet isolation, leakage, and loss warnings.
7. Emit warnings and alarms once per condition.
8. Apply guards and constraints to controls.
9. Enter hold, recovery, abort, secure, or reuse-blocked states.
10. Produce a replayable trace and debrief.

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
- packet-loss lockout;
- carrier/chronology lockout.

Debriefs should summarize the operational trace, limiting subsystems, alarms,
operator interventions, diagnostic ledgers produced, and recommended study
links. They should not grade the run like a multiple-choice attempt.
