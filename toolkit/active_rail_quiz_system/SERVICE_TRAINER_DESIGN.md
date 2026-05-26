# Rail Service Terminal Design

This document is the source of truth for the Rail Service Terminal. The
terminal is a first-class product in the active-rail training suite, not a quiz
mode and not a themed question workspace.

Target experience:

> The learner sits down as the assigned line engineer at a future active-rail
> service terminal. A single line is alive. The operator observes the geometry,
> authorizes service actions, watches subsystem state evolve, responds to
> limits, and secures, holds, recovers, or aborts the run. The controller does
> the low-level shaping; manual overrides are special access, not the default
> way to operate the line.

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

| Operator-Facing System | Technical Grounding | Visual Expression | Normal Operator Actions |
| --- | --- | --- | --- |
| Support Plant | Standing support substrate, radial backbone, support-shell actuator layer, and regulated medium/reservoir behavior. | A prepared shell that comes online around the service corridor, shows charge, sag, overload, and recovery, and never appears as a generic health bar. | Precharge line, authorize support, hold for support sag, request recovery, secure support. |
| Packet Bay And Gate | Live packet corridor, packet isolation, entry gate, packet sealing, and loss guards. | Packet staged at a bay, sealed before service, admitted into the corridor, isolated during carry, and flagged if leakage or packet-loss risk appears. | Accept work order, load/seal packet, admit packet when line authority permits, hold or abort on isolation loss. |
| Carrier Field | Carrying-flow actuator, clock-lapse cushion, rail-stretch/throat-capacity support, and carrier governance. | A carrier envelope forms around the packet, carries it through the live corridor, holds, fades, or destabilizes according to state. | Arm carrier, begin carry, hold, resume, fade after receiver capture, abort if carrier authority narrows. |
| Receiver Station | Endpoint receiver, catch/rematch collar, beta-memory/receiver posture, aperture, and timing lock. | Receiver acquisition rings and catch field show searching, tracking, locked, catch-ready, caught, mismatch, or missed capture. | Prepare receiver, authorize catch window, confirm catch/rematch, hold on receiver mismatch. |
| Reset Plant | Decompression path, reset cap, support-edge closure, wake-tail cleanup, and reuse readiness. | Residue, wake, decompression flow, and reset clearing are visible after release and before reuse. | Decompress, purge/reset, confirm residue clear, secure or block reuse. |
| Safety Interlocks | Packet isolation, support stability, receiver lock, timing window, carrier/chronology guards, and abort path availability. | Interlock gates attach to the subsystem they protect and tighten before alarms become terminal. | Read authority, honor holds, acknowledge alarms, choose abort/recovery/secure when the line requires it. |
| Autopilot/Supervisor | Controller policy using the same service state, guards, and access limits available to the terminal. | Supervisor highlights active concerns, moves authorized service controls when enabled, and leaves a trace in operating language. | Enable, pause, resume, hand back, or grant limited override access when justified. |

The terminal should also surface the four metric-service variables as component
channels where useful:

- carrying-flow field `beta`: service load and carry action;
- clock-lapse field `alpha`: causal/timing cushion;
- rail-stretch field `gamma_ll`: radial metric capacity;
- throat-capacity field `gamma_OmegaOmega`: angular/throat support.

These are not raw equation-entry controls. They are diagnostic actuator
families behind the service systems above. The main terminal should name the
operated equipment first and expose `beta`, `alpha`, `gamma_ll`, and
`gamma_OmegaOmega` only in engineering diagnostics or authorized override
views.

## Operator Vocabulary And Diagnostic Vocabulary

Default terminal language is service language. A line engineer should primarily
see:

- support plant charged, ramping, stable, sagging, overloaded, or recovering;
- packet bay staged, sealed, admitted, isolated, held, carried, caught, or
  released;
- carrier field idle, forming, carrying, holding, fading, or aborted;
- receiver station searching, tracking, locked, catch-ready, caught, mismatched,
  or missed;
- reset plant idle, decompression active, purge active, residue clear, or reuse
  blocked;
- safety interlocks open, satisfied, narrowing, locked, or tripped;
- line authority standby, ready, armed, carrying, held, recovering, aborting,
  resetting, or secured.

Analysis vocabulary is still useful, but it belongs in diagnostics, audits, and
engineering drawers:

- source-demand ledgers;
- source-family or matter-model notes;
- endpoint-confidence proxies;
- metric-variable details;
- constraint ledgers;
- causal-access, horizon-risk, and chronology-risk overlays;
- numerical run artifacts.

The primary operating surface should not use analysis terms as if they were
physical plant controls. `Endpoint confidence` becomes `receiver lock`,
`receiver acquisition`, or `catch margin` in the operator view. `Source family`
and `source-response` become `support plant`, `regulated medium`, `reservoir
headroom`, or `plant supply load` unless the user explicitly opens an expert
diagnostic view.

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
operational language such as:

- `Precharge Support`;
- `Authorize Carrier`;
- `Prepare Receiver`;
- `Open Catch Window`;
- `Decompress Line`;
- `Purge Reset Path`;
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

This is not a simplification target. The goal is a richer and more faithful
component visualization, not a toy diagram with fewer elements. If a current
visual layer is confusing or inaccurate, replace it with a better
state-derived representation. Do not remove important geometry, optics,
support, carrier, reset, or safety information just because the first attempt
rendered it poorly.

Required live layers:

- **service corridor:** protected route and active interval;
- **live packet:** packet body, packet isolation, packet leakage/loss warning,
  hold/carry/catch/release posture;
- **standing substrate:** quiet prepared railbed/readiness background;
- **support envelope:** active support-shell field whose thickness, continuity,
  brightness, and distortion change with support state;
- **metric actuator channels:** beta/carrying-flow, clock-lapse cushion,
  rail-stretch, and throat-capacity bands where the scenario calls for them;
- **plant supply channel:** regulated medium/reservoir headroom, saturation,
  support exchange, and overdraw as an operating burden, not a claim that matter
  closure is solved;
- **receiver station:** catch/rematch aperture, receiver phase, beta-memory
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

Text inside the graphic should be disciplined: station names, subsystem labels,
phase/status tags, and localized warning tags are useful when they clarify the
geometry. Labels should be anchored to features and should not become the main
content of the graphic.

The robust visual target includes:

- layered geometry for the protected corridor, support shell, carrier field,
  receiver/catch system, reset path, and packet isolation boundary;
- dense but meaningful field effects for support charging, medium/reservoir
  burden, carrier formation, receiver acquisition, leakage, residue, and
  overload;
- dynamic ray/probe bundles for receiver optics and carrier-audit posture,
  driven by receiver lock, timing drift, carry state, and scenario risk;
- visibly changing actuator-channel bands for carrying-flow, clock-lapse
  cushion, rail-stretch, and throat-capacity when those channels are relevant;
- localized deformation, shear, shimmer, aperture motion, residue clearing, and
  lock/catch transitions that match simulator state;
- alarm and guard overlays that attach to the subsystem that is actually
  degraded.

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
corridor, a packet service trace, plant supply load, receiver optics,
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
| Plant supply channel | Regulated medium, support exchange, reservoir draw, and overdraw. | plant supply load, medium coupling, reservoir headroom, service load | Side flow saturates, drains, leaves residual knots, or overheats. | Operating burden proxy, not proof of matter closure. |
| Receiver station | Catch/rematch, receiver phase, aperture, beta-memory receiver. | receiver lock, catch aperture, packet position, timing drift | Receiver rings align, widen, narrow, or miss; catch ring locks around packet edge. | Receiver operation proxy. |
| Optics/carrier probes | Access and branch-band audit posture. | receiver lock, timing drift, carrier governance, scenario flags | Ray/probe bundles converge, shear, defocus, or compress near risk boundaries. | Probe heuristic, not null-geodesic integration. |
| Timing shear | Packet/receiver phase mismatch. | timing drift, receiver lock, carrier field | Gridlines, probe bundles, or receiver rings shear relative to the packet trace. | Timing-risk proxy. |
| Backreaction/constraint posture | Stability, load coupling, and constraint stress. | stability, load index, plant supply load, support margin | Guard bands tighten, global envelope breathes unevenly, plant supply channel drags. | Review-burden warning, not backreaction calculation. |
| Horizon/causal-access risk | Horizon-like access concern in risky service regimes. | service factor, high-risk scenario, timing drift, receiver lock | One-way-looking veil or compressed reachability fan appears near catch/release. | Risk overlay, not horizon detection. |
| Chronology guard | Rail-time or closed-curve scheduling concern. | rail-time policy, network scenario, release/fade state | Guard band or loop-warning overlay appears only in relevant scenario mode. | Chronology training guard, not CTC detection. |
| Reset residue | Decompression and reuse readiness. | reset residue, decompression, reset purge, release fade | Haze trails the corridor and clears with purge; contamination clings to endpoint/support. | Operational residue proxy. |

These layers should be animated from the same simulator state. If the state does
not change, the geometry should settle rather than perform decorative motion.
When the design calls for a visual effect that cannot be honestly driven by the
current state model, the simulator model should be expanded instead of faking
the effect as static ornament.

### Visualization Accuracy Requirements

The visual simulation should preserve component meaning.

- The packet is a local object inside the service corridor, not a cursor dragged
  by an entry signal.
- The support envelope is the active support-shell condition around the
  corridor; it should change with support charge, sag, load, and stability.
- Carrier field visuals should show formation, carry, hold, fade, and
  instability as field behavior around the packet/corridor, not as a progress
  bar.
- Receiver visuals should distinguish acquisition, lock, catch aperture,
  rematch, catch, mismatch, and missed capture.
- Packet leakage/loss should be a direct visual phenomenon around packet and
  corridor isolation, not only an alarm row.
- Reset residue should occupy the reset/decompression path and clear according
  to reset-plant state.
- Backreaction, horizon-risk, chronology-risk, and carrier-audit visuals are
  cautious risk overlays. They should be rich enough to train recognition of
  the concern, but always labeled as heuristic architecture-logic indicators.
- Technical labels such as `source response`, `source family`, `endpoint
  confidence`, or `ledger` should not appear as ordinary plant labels. They may
  appear in expert overlays that explicitly say they are diagnostics.

## Instrumentation

Instrumentation supports the graphic. It does not replace it.

Required instruments:

- packet isolation / leakage margin;
- support margin;
- plant supply load / reservoir headroom;
- receiver lock / receiver acquisition / catch margin;
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

The terminal interaction model is live operation. The default controls are
service authorizations and supervised equipment actions, not raw parameter
knobs and not a next-action list.

Primary controls:

- accept work order;
- precharge support plant;
- load and seal packet bay;
- prepare receiver station;
- arm line authority;
- authorize carrier field;
- hold/resume;
- authorize receiver catch/rematch;
- confirm catch;
- fade carrier after receiver capture;
- decompress line;
- purge/reset plant;
- abort/recovery;
- secure line.

Controls may be guarded switches, levers, rotary controls, bounded sliders, or
compact buttons depending on the action. The key rule is that the operator is
directing a live line, not selecting the next command from a list.

### Access Levels And Manual Overrides

Manual knobs are special access. The normal operator should not need to tune raw
fields to complete a nominal run.

| Access | Surface | Purpose | Examples |
| --- | --- | --- | --- |
| Level 0: Supervised Operation | Default terminal | Service actions and authority management. | Accept work order, precharge support, arm carrier, authorize catch, hold, abort, secure. |
| Level 1: Authorized Trim | Guarded override drawer | Limited bounded trims when supervisor identifies a recoverable margin issue. | Support precharge target, receiver acquisition width, carrier ramp rate, purge intensity. |
| Level 2: Engineering Override | Explicit elevated access | Direct actuator-family adjustment for training, incident recovery, or expert diagnosis. | Clock-lapse cushion, rail-stretch trim, throat-capacity trim, medium/reservoir flow limits. |
| Level 3: Diagnostic/Research Access | Offline, instructor, or audit view | Raw model variables, ledgers, technical overlays, and run artifacts. | Source-demand ledger, constraint ledger, carrier audit, matter/source-family notes. |

The terminal should surface the lowest useful access level. If a manual
override is needed, the UI should say which subsystem needs it, what authority
is required, what guard limits apply, and how to return to supervised control.
Every override leaves a trace. Hold and abort remain available.

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
4. support plant, regulated medium, and reservoir brought inside operating
   headroom;
5. receiver station locked and catch/rematch aperture prepared;
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

Autopilot is an adaptive closed-loop controller, not a scripted next-action
runner:

- it uses the same service authority and access limits available to the
  operator;
- it completes a clean nominal run under nominal conditions;
- it observes changing state and adapts to bounded perturbations;
- it can pause, hold, recover, or request override access when margins narrow;
- it leaves an event trace;
- it can be paused or handed back to manual control;
- it should explain actions tersely in operational language;
- it must not hide failures or silently solve the run.

Supervisor mode is advisory:

- it highlights the next operational concern;
- it points to a subsystem, control, guard, or visual layer;
- it should not present a puzzle prompt or a single correct-answer button.

Randomness should be bounded and replayable:

- each work order has a seed and a perturbation envelope;
- set scenarios define baseline operating family and likely failure class;
- the random engine varies timing, subsystem margins, noise, disturbance
  onset, recovery tolerance, and warning thresholds inside that envelope;
- perturbations include support sag, plant supply load fluctuation, receiver
  drift, packet leakage, reservoir sag, reset residue, timing drift, and
  stability caution;
- the same seed should replay the same sequence for review;
- random faults should have observable precursors before or during alarm state.

Autopilot must respond to the same random perturbations. A successful autopilot
does not mean "perfect run"; it means the controller notices changing
conditions, keeps the line inside authority where possible, and chooses hold,
recovery, abort, or secure when the line state requires it.

## Work Orders And Scenarios

Work orders are operational assignments. They should be terse and terminal-like.

Good examples:

- `Receiver lock degraded at load. Monitor catch margin.`
- `Reuse path carries residual from prior reset.`
- `Heavy packet: support plant expected above nominal draw.`
- `Support plant sag likely under carry. Autopilot may request Level 1 trim.`

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
    acceptWorkOrder,
    prechargeSupport,
    loadSealPacket,
    prepareReceiver,
    armLine,
    authorizeCarrier,
    authorizeCatch,
    confirmCatch,
    fadeCarrier,
    decompressLine,
    purgeReset,
    secureLine,
    catchAperture,
    hold,
    abort,
    overrideAccess: {
      level,
      supportPrechargeTarget,
      receiverAcquisitionWidth,
      carrierRampRate,
      purgeIntensity,
      metricActuatorTrims,
      mediumReservoirLimits
    }
  },
  metrics: {
    packetIsolation,
    packetLeakage,
    supportMargin,
    plantSupplyLoad,
    reservoirHeadroom,
    receiverLock,
    catchMargin,
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
2. Apply seeded scenario perturbations and random faults inside the work
   order's envelope.
3. Evolve component metrics from work order, controls, run state, and faults.
4. Derive visual geometry from state, not static decoration.
5. Move packet position and posture according to carry, hold, catch, release,
   and reset conditions.
6. Track packet isolation, leakage, and loss warnings.
7. Emit warnings and alarms once per condition.
8. Apply guards and constraints to controls.
9. Enter hold, recovery, abort, secure, or reuse-blocked states.
10. Produce a replayable trace and debrief.

Additional visual-state responsibilities:

- derive support-shell contours, carrier envelope, actuator-channel bands, and
  receiver aperture geometry from component state;
- derive ray/probe bundles from receiver lock, timing drift, carrier posture,
  and risk overlays;
- derive particle/haze fields from leakage, reservoir load, residue, and reset
  clearing;
- derive randomized-but-replayable microvariation from the work-order seed so
  the line feels alive without becoming nondeterministic;
- expose enough component state for autopilot and the visualizer to agree about
  what is happening.

Operator timing should matter. Late catch should change receiver posture.
Overdriven support should increase plant supply load. Premature fade should
produce a release/catch conflict. Incomplete reset should leave visible
residue. Autopilot should be able to handle nominal variation and common
caution states, but it must hold, request access, abort, or block reuse when
conditions leave its authority envelope.

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
