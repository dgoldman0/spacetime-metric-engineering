import { useEffect, useMemo, useRef, useState } from "react";
import { scaleLinear } from "d3-scale";
import { area as d3Area, curveBasis, curveCatmullRom, line as d3Line } from "d3-shape";
import { motion } from "framer-motion";
import { workOrders } from "../serviceTrainer/serviceProfiles.js";
import {
  applyAutopilotStep,
  applyServiceCommand,
  controlDefs,
  createInitialLine,
  formatClock,
  getControlState,
  getDebrief,
  getLineCondition,
  getLineConstraints,
  getLineVisualState,
  getOperatingPhase,
  getServiceCommandState,
  getTelemetryStatus,
  getTerminalAdvisories,
  serviceCommandDefs,
  telemetryDefs,
  tickLine,
  updateLineControl
} from "../serviceTrainer/lineSimulator.js";

const overrideLabels = ["locked", "operator trim", "engineering override"];

const packetLabels = {
  staged: "staged",
  accepted: "accepted",
  held: "held",
  recovery: "recovery",
  secured: "secured",
  released: "released",
  "handoff pending": "handoff",
  "in service": "in service"
};

export function RailServiceTerminal() {
  const [profileId, setProfileId] = useState("standard");
  const [line, setLine] = useState(() => createInitialLine("standard"));
  const [autopilot, setAutopilot] = useState(false);
  const [overrideLevel, setOverrideLevel] = useState(0);
  const visualState = useMemo(() => getLineVisualState(line), [line]);
  const condition = visualState.condition || getLineCondition(line);
  const constraints = useMemo(() => getLineConstraints(line), [line]);
  const advisories = useMemo(() => getTerminalAdvisories(line), [line]);
  const debrief = getDebrief(line);
  const activeWorkOrder = workOrders.find((order) => order.id === profileId) || workOrders[1];
  const phase = getOperatingPhase(line);
  const alarmCount = line.events.filter((event) => event.level === "alarm" || event.level === "abort").length;
  const primaryAdvisory = advisories[0];

  useEffect(() => {
    if (!autopilot && (line.runState === "standby" || line.runState === "recovery" || line.runState === "secured")) return undefined;
    const interval = window.setInterval(() => {
      setLine((current) => {
        const piloted = autopilot ? applyAutopilotStep(current) : current;
        if (piloted.runState === "standby" || piloted.runState === "recovery" || piloted.runState === "secured") return piloted;
        return tickLine(piloted);
      });
    }, line.runState === "service" ? 620 : 820);
    return () => window.clearInterval(interval);
  }, [line.runState, autopilot]);

  function loadProfile(nextProfileId) {
    if (!["standby", "recovery", "secured"].includes(line.runState)) return;
    setAutopilot(false);
    setOverrideLevel(0);
    setProfileId(nextProfileId);
    setLine(createInitialLine(nextProfileId));
  }

  function moveControl(controlId, value) {
    if (controlAccessLevel(controlId) > overrideLevel) return;
    setLine((current) => updateLineControl(current, controlId, value));
  }

  function runServiceCommand(commandId) {
    setLine((current) => applyServiceCommand(current, commandId));
  }

  function toggleAutopilot() {
    setAutopilot((enabled) => !enabled);
  }

  return (
    <div className="service-terminal-shell">
      <main className={`terminal-grid ${condition}`}>
        <section className={`terminal-status ${condition}`} aria-label="Line status">
          <StatusTile label="Line" value={line.lineId} />
          <StatusTile label="Work Order" value={line.workOrderId} />
          <StatusTile label="Clock" value={`T+${formatClock(line.clock)}`} />
          <StatusTile label="State" value={stateLabel(line.runState)} />
          <StatusTile label="Authority" value={line.authorityState} />
          <StatusTile label="Packet" value={packetLabels[line.packetState] || line.packetState} />
          <StatusTile label="Alarms" value={String(alarmCount)} />
        </section>

        <motion.section
          className="terminal-panel line-console"
          aria-label="Live line simulation"
          layout
          transition={{ type: "spring", stiffness: 180, damping: 24 }}
        >
          <PanelHead
            kicker="Line"
            title="Single Rail Service"
            aside={`${phase.label} / ${condition.toUpperCase()}`}
          />
          <div className="assignment-strip">
            <div>
              <span>Work order</span>
              <strong>{activeWorkOrder.workOrderId} / {activeWorkOrder.callSign}</strong>
              <small>{activeWorkOrder.operationNotice}</small>
            </div>
            <details className="assignment-drawer">
              <summary>Change assignment</summary>
              <div className="work-order-list">
                {workOrders.map((order) => {
                  const selected = order.id === profileId;
                  return (
                    <button
                      type="button"
                      key={order.id}
                      className={selected ? "selected" : ""}
                      onClick={() => loadProfile(order.id)}
                      disabled={!["standby", "recovery", "secured"].includes(line.runState)}
                    >
                      <span>{order.workOrderId}</span>
                      <strong>{order.callSign}</strong>
                      <small>{order.classLabel} / {order.priority}</small>
                    </button>
                  );
                })}
              </div>
            </details>
          </div>
          <div
            className={`live-line-view ${condition} ${line.runState}`}
            style={visualState.styleVars}
          >
            <div className="rail-viewport">
              <FieldParticleLayer visualState={visualState} line={line} />
              <RailGraphic line={line} visualState={visualState} phase={phase} />
            </div>
          </div>
          <VisualKey />
        </motion.section>

        <aside className="terminal-ops-stack" aria-label="Telemetry">
          <section className="terminal-panel telemetry-console" aria-label="Telemetry">
            <PanelHead kicker="Telemetry" title="Line State" />
            <div className="telemetry-grid">
              {telemetryDefs.map((def) => (
                <TelemetryMeter
                  key={def.id}
                  def={def}
                  value={line.metrics[def.id]}
                  trend={line.metricTrends?.[def.id] || []}
                />
              ))}
            </div>
          </section>
          <section className={`terminal-panel supervisor-console ${primaryAdvisory?.level || "nominal"}`} aria-label="Supervisor">
            <PanelHead kicker="Supervisor" title="Guidance" />
            <div>
              <strong>{primaryAdvisory?.title || "Line nominal"}</strong>
              <span>{primaryAdvisory?.detail || "No active subsystem requires intervention."}</span>
              <button
                type="button"
                className={`autopilot-toggle ${autopilot ? "active" : ""}`}
                onClick={toggleAutopilot}
              >
                {autopilot ? "Autopilot running" : "Run supervised autopilot"}
              </button>
            </div>
          </section>
        </aside>

        <section className="terminal-panel control-console" aria-label="Operator controls">
          <PanelHead kicker="Operator Station" title="Service Controls" />
          <div className="service-command-grid" aria-label="Service commands">
            {serviceCommandDefs.map((command) => {
              const state = getServiceCommandState(line, command.id);
              return (
                <ServiceCommandButton
                  key={command.id}
                  command={command}
                  state={state}
                  onRun={() => runServiceCommand(command.id)}
                />
              );
            })}
          </div>
          <details className="override-console">
            <summary>
              <span>Engineering access</span>
              <strong>{overrideLabels[overrideLevel]}</strong>
            </summary>
            <div className="override-access" role="group" aria-label="Manual override access">
              {[0, 1, 2].map((level) => (
                <button
                  type="button"
                  key={level}
                  className={overrideLevel === level ? "selected" : ""}
                  onClick={() => setOverrideLevel(level)}
                >
                  {overrideLabels[level]}
                </button>
              ))}
            </div>
            {overrideLevel === 0 ? (
              <div className="override-locked">
                Manual actuator trims are locked. Use service controls unless the training run explicitly calls for operator or engineering override.
              </div>
            ) : (
              <div className="control-surface override-controls">
                {controlDefs.map((control) => {
                  const accessLevel = controlAccessLevel(control.id);
                  const locked = accessLevel > overrideLevel;
                  return (
                    <ControlSlider
                      key={control.id}
                      control={control}
                      value={line.controls[control.id]}
                      state={getControlState(line, control.id)}
                      locked={locked}
                      accessLevel={accessLevel}
                      onChange={(value) => moveControl(control.id, value)}
                    />
                  );
                })}
              </div>
            )}
          </details>
        </section>

        <section className="terminal-secondary-console" aria-label="Inspection consoles">
          <section className="terminal-panel advisory-console" aria-label="Advisories">
            <PanelHead kicker="Watch Floor" title="Constraints" />
            <div className="terminal-advisories">
              {advisories.map((advisory) => (
                <div className={advisory.level} key={advisory.id}>
                  <strong>{advisory.title}</strong>
                  <span>{advisory.detail}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="terminal-panel event-console" aria-label="Event feed">
            <PanelHead kicker="Events" title="Service Trace" />
            <ol>
              {line.events.map((event) => (
                <li className={event.level} key={event.id}>
                  <time>T+{formatClock(event.clock)}</time>
                  <span>{event.subsystem}</span>
                  <strong>{event.message}</strong>
                </li>
              ))}
            </ol>
          </section>

          <section className="terminal-panel constraint-map" aria-label="Constraint map">
            <PanelHead kicker="Limits" title="Guard Map" />
            <div className="guard-map">
              {constraints.length ? constraints.map((constraint) => (
                <div className={constraint.level} key={constraint.id}>
                  <span>{constraint.subsystem}</span>
                  <strong>{constraint.title}</strong>
                </div>
              )) : (
                <div className="nominal">
                  <span>system</span>
                  <strong>No active guard limiting line operation.</strong>
                </div>
              )}
            </div>
          </section>
        </section>

        {debrief && (
          <section className={`terminal-panel debrief-console ${debrief.tone}`} aria-label="Run debrief">
            <PanelHead kicker="Debrief" title={debrief.outcome} />
            <p>{debrief.summary}</p>
            <p>{debrief.recovery}</p>
            <div className="debrief-stats">
              {debrief.stats.map(([label, value]) => (
                <div key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function FieldParticleLayer({ visualState, line }) {
  const hostRef = useRef(null);
  const appRef = useRef(null);
  const visualRef = useRef(visualState);

  useEffect(() => {
    visualRef.current = { ...visualState, clock: line.clock, runState: line.runState };
  }, [visualState, line.clock, line.runState]);

  useEffect(() => {
    let destroyed = false;
    let app;
    const host = hostRef.current;
    const particles = Array.from({ length: 110 }, (_, index) => ({
      id: index,
      x: (index * 0.61803398875) % 1,
      y: (index * 0.377 + 0.12) % 1,
      speed: 0.0018 + (index % 9) * 0.00045,
      radius: 0.9 + (index % 5) * 0.46,
      band: index % 3
    }));

    async function mount() {
      const PIXI = await import("pixi.js");
      app = new PIXI.Application();
      await app.init({
        backgroundAlpha: 0,
        antialias: true,
        autoDensity: true,
        resolution: Math.min(window.devicePixelRatio || 1, 2),
        resizeTo: host
      });
      if (destroyed || !host) {
        app.destroy(true);
        return;
      }
      host.appendChild(app.canvas);
      appRef.current = app;
      const field = new PIXI.Graphics();
      app.stage.addChild(field);
      app.ticker.add(() => {
        const state = visualRef.current;
        const width = app.screen.width || host.clientWidth || 900;
        const height = app.screen.height || host.clientHeight || 360;
        const residue = state.residueDensity || 0;
        const source = state.sourceSaturation || 0;
        const support = state.supportStrength || 0;
        const causal = state.causalRisk || 0;
        const leakage = state.packetLeakage || 0;
        const reservoirStress = 1 - (state.reservoirCharge || 0.75);
        field.clear();
        particles.forEach((particle) => {
          const drift = particle.speed * (0.35 + source + residue + causal + leakage * 0.8);
          particle.x = (particle.x + drift) % 1;
          const railBand = particle.band === 0;
          const yBase = railBand ? 0.46 : particle.band === 1 ? 0.3 + reservoirStress * 0.08 : 0.64;
          const x = particle.x * width;
          const wobble = 0.015 + causal * 0.03 + leakage * 0.05;
          const y = (yBase + Math.sin((particle.x + particle.id) * 6.283) * wobble) * height;
          const alpha = 0.025 + residue * 0.1 + source * 0.08 + support * 0.025 + leakage * 0.08;
          const color = leakage > 0.38 && railBand ? 0xd86f57 : residue > 0.48 && particle.band === 2 ? 0xd6a23d : particle.band === 1 ? 0xd0bb68 : 0x9bc58b;
          field.circle(x, y, particle.radius + residue * 1.4 + source * 0.6 + leakage * 1.2).fill({ color, alpha });
        });
      });
    }

    mount();

    return () => {
      destroyed = true;
      if (appRef.current) {
        appRef.current.destroy(true);
        appRef.current = null;
      }
    };
  }, []);

  return <div className="pixi-field-layer" ref={hostRef} aria-hidden="true" />;
}

function VisualKey() {
  return (
    <div className="visual-key" aria-label="Line graphic key">
      <span><i className="key-corridor" /> service corridor</span>
      <span><i className="key-support" /> support shell</span>
      <span><i className="key-source" /> plant load</span>
      <span><i className="key-optics" /> receiver optics</span>
      <span><i className="key-leakage" /> packet leakage</span>
      <span><i className="key-carrier" /> carrier probes</span>
      <span><i className="key-residue" /> reset residue</span>
    </div>
  );
}

function RailGraphic({ line, visualState, phase }) {
  const xScale = scaleLinear().domain([0, 100]).range([104, 1096]);
  const yCenter = 238;
  const packetX = xScale(visualState.packetPosition);
  const sourceWidth = Math.max(28, 650 * Math.max(visualState.sourceSaturation, visualState.plantSupplyPulse));
  const sourceResiduals = buildSourceResiduals(visualState);
  const apertureRx = 22 + visualState.endpointAperture * 86;
  const apertureHeight = 38 + visualState.endpointAperture * 146;
  const railTrailEnd = Math.max(132, Math.min(1088, packetX));
  const carrierGlow = Math.max(0.12, line.controls.carrierDrive / 100);
  const supportOpacity = 0.28 + visualState.supportStrength * 0.62;
  const supportStroke = 4 + visualState.supportStrength * 7 + visualState.backreactionPosture * 4 + visualState.supportSag * 5;
  const leakageRadius = 40 + visualState.packetLeakage * 58;
  const isolationStroke = 2.5 + visualState.packetIsolation * 5;
  const clockPhase = line.clock / 11 + (visualState.perturbation?.mediumNoise || 0);
  const corridorPath = buildServiceCorridor(visualState, clockPhase);
  const supportEnvelope = buildSupportEnvelope(visualState, clockPhase);
  const supportRibs = buildSupportRibs(visualState, clockPhase);
  const metricBands = buildMetricActuatorBands(visualState, clockPhase);
  const packetTrace = buildPacketTrace(visualState, packetX, yCenter, clockPhase);
  const optics = buildOpticsBundle(visualState, packetX, yCenter, apertureRx, apertureHeight, clockPhase);
  const carrierProbes = buildCarrierProbes(visualState, packetX, yCenter, clockPhase);
  const shearLines = buildShearLines(visualState, clockPhase);
  const causalFan = buildCausalFan(visualState, apertureRx);
  const chronologyLoop = buildChronologyLoop(visualState);
  const residuePath = buildResiduePath(visualState);
  const constraintBands = buildConstraintBands(visualState);
  const horizonOpacity = Math.max(0, visualState.horizonRisk - 0.08) * 1.45;
  const chronologyOpacity = Math.max(0, visualState.chronologyRisk - 0.04) * 1.8;

  return (
    <motion.svg
      className={`rail-graphic ${visualState.condition} ${line.runState}`}
      viewBox="0 0 1200 470"
      preserveAspectRatio="none"
      role="img"
      aria-label={`Single rail service line, packet ${packetLabels[line.packetState] || line.packetState}`}
      initial={false}
      animate={{ opacity: 1 }}
    >
      <defs>
        <pattern id="terminal-grid-pattern" width="40" height="30" patternUnits="userSpaceOnUse">
          <path d="M40 0H0V30" fill="none" stroke="rgba(218,228,199,0.055)" strokeWidth="1" />
        </pattern>
        <linearGradient id="support-gradient" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#e6c963" stopOpacity="0.12" />
          <stop offset="0.18" stopColor="#9ed18f" stopOpacity="0.24" />
          <stop offset="0.74" stopColor="#7fbf93" stopOpacity="0.16" />
          <stop offset="1" stopColor="#d8b24c" stopOpacity="0.12" />
        </linearGradient>
        <linearGradient id="corridor-gradient" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#c9db9a" stopOpacity="0.1" />
          <stop offset="0.35" stopColor="#6fb5a6" stopOpacity="0.16" />
          <stop offset="0.75" stopColor="#86c090" stopOpacity="0.12" />
          <stop offset="1" stopColor="#dbc45f" stopOpacity="0.1" />
        </linearGradient>
        <linearGradient id="source-gradient" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#e3d27c" stopOpacity="0.94" />
          <stop offset="0.52" stopColor="#bc8245" stopOpacity="0.9" />
          <stop offset="1" stopColor="#d1634e" stopOpacity="0.9" />
        </linearGradient>
        <linearGradient id="rail-live-gradient" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#d7c65f" />
          <stop offset="0.52" stopColor="#9fcb89" />
          <stop offset="1" stopColor="#d9c15f" />
        </linearGradient>
        <linearGradient id="metric-band-gradient" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#b7e1a5" stopOpacity="0.12" />
          <stop offset="0.5" stopColor="#9ed6ce" stopOpacity="0.24" />
          <stop offset="1" stopColor="#e2c15f" stopOpacity="0.12" />
        </linearGradient>
        <radialGradient id="leakage-glow" cx="50%" cy="50%" r="60%">
          <stop offset="0" stopColor="#f0d06d" stopOpacity="0.06" />
          <stop offset="0.56" stopColor="#da7058" stopOpacity="0.18" />
          <stop offset="1" stopColor="#da7058" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="packet-glow" cx="50%" cy="50%" r="58%">
          <stop offset="0" stopColor="#f1cc66" stopOpacity="0.92" />
          <stop offset="0.68" stopColor="#f1cc66" stopOpacity="0.28" />
          <stop offset="1" stopColor="#f1cc66" stopOpacity="0" />
        </radialGradient>
        <filter id="field-glow" x="-25%" y="-25%" width="150%" height="150%">
          <feGaussianBlur stdDeviation="9" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <rect className="rail-svg-backdrop" x="0" y="0" width="1200" height="470" />
      <rect className="rail-svg-grid" x="0" y="0" width="1200" height="470" fill="url(#terminal-grid-pattern)" />

      <g className="station-marker-layer">
        <g className="station-marker origin-marker">
          <line x1="88" y1="94" x2="88" y2="382" />
          <circle cx="104" cy={yCenter} r="11" />
          <text x="34" y="212">ORIGIN</text>
          <text x="34" y="236">{originLabel(line).toUpperCase()}</text>
        </g>
        <g className="station-marker endpoint-marker">
          <line x1="1112" y1="94" x2="1112" y2="382" />
          <circle cx="1096" cy={yCenter} r="11" />
          <text x="1130" y="212">RECEIVER</text>
          <text x="1130" y="236">{endpointLabel(line).toUpperCase()}</text>
        </g>
      </g>

      <g className="service-zones" aria-hidden="true">
        {constraintBands.map((band) => (
          <motion.rect
            key={band.id}
            x={band.x}
            y="24"
            width={band.width}
            height="420"
            animate={{ opacity: band.opacity }}
            transition={{ duration: 0.45 }}
          />
        ))}
      </g>

      <g className="source-response-layer" aria-label="Support-plant and regulated medium channel">
        <text x="242" y="58">SUPPORT PLANT / REGULATED MEDIUM</text>
        <rect className="source-shell" x="242" y="76" width="650" height="34" rx="17" />
        <motion.rect
          className="source-flow"
          x="242"
          y="76"
          height="34"
          rx="17"
          animate={{ width: sourceWidth }}
          transition={{ type: "spring", stiffness: 90, damping: 20 }}
        />
        {sourceResiduals.map((residual) => (
          <motion.circle
            className="source-residual-knot"
            key={residual.id}
            cx={residual.x}
            cy={residual.y}
            r={residual.r}
            animate={{ opacity: residual.opacity, scale: 1 + visualState.sourceSaturation * 0.18 }}
          />
        ))}
      </g>

      <g className="causal-risk-layer" opacity={horizonOpacity}>
        <path className="causal-fan" d={causalFan} />
        <text x="922" y="122">CAUSAL-ACCESS RISK</text>
      </g>

      <g className="chronology-guard-layer" opacity={chronologyOpacity}>
        <path d={chronologyLoop} />
        <text x="740" y="386">CHRONOLOGY GUARD</text>
      </g>

      <g className="metric-actuator-layer" aria-label="Metric actuator channels">
        {metricBands.map((band) => (
          <motion.path
            key={band.id}
            className={`metric-band ${band.id}`}
            d={band.d}
            animate={{ opacity: band.opacity }}
            transition={{ duration: 0.45 }}
          />
        ))}
        <text x="210" y="184">BETA CARRYING FLOW</text>
        <text x="214" y="214">ALPHA LAPSE CUSHION</text>
        <text x="214" y="266">GAMMA RAIL STRETCH</text>
        <text x="214" y="298">GAMMA THROAT CAPACITY</text>
      </g>

      <g className="support-layer" opacity={supportOpacity} filter="url(#field-glow)">
        <motion.path
          className="service-corridor-svg"
          d={corridorPath}
          animate={{ opacity: 0.42 + visualState.supportStrength * 0.26 }}
          transition={{ duration: 0.45 }}
        />
        <motion.path
          className="support-envelope-svg"
          d={supportEnvelope}
          strokeWidth={supportStroke}
          animate={{ opacity: supportOpacity }}
          transition={{ duration: 0.45 }}
        />
        {supportRibs.map((rib) => (
          <motion.path
            className="support-inner-rib"
            d={rib.d}
            key={rib.id}
            animate={{ opacity: rib.opacity }}
            transition={{ duration: 0.45 }}
          />
        ))}
        <text className="corridor-label" x="176" y="158">LIVE PACKET CORRIDOR</text>
        <text className="support-label" x="176" y="340">STANDING SUPPORT SHELL</text>
      </g>

      <g className="carrier-probe-layer" aria-label="Carrier governance probes">
        {carrierProbes.map((probe) => (
          <motion.path
            className={probe.focused ? "carrier-probe focused" : "carrier-probe"}
            d={probe.d}
            key={probe.id}
            animate={{ opacity: probe.opacity }}
            transition={{ duration: 0.45 }}
          />
        ))}
      </g>

      <g className="optics-layer" aria-label="Receiver station optics">
        {optics.map((ray) => (
          <motion.path
            className={ray.focused ? "optics-ray focused" : "optics-ray"}
            d={ray.d}
            key={ray.id}
            animate={{ opacity: ray.opacity }}
            transition={{ duration: 0.45 }}
          />
        ))}
      </g>

      <g className="timing-layer" opacity={Math.max(0.06, visualState.timingShear * 0.72)}>
        {shearLines.map((lineItem) => (
          <path key={lineItem.id} d={lineItem.d} opacity={lineItem.opacity} />
        ))}
      </g>

      <g className="reset-layer" opacity={visualState.residueDensity * 0.72}>
        <path className="reset-haze-path" d={residuePath} />
        <ellipse cx="890" cy="358" rx={80 + visualState.residueDensity * 260} ry={14 + visualState.residueDensity * 60} />
      </g>

      <g className="rail-path-layer">
        <line className="rail-base" x1="128" y1={yCenter} x2="1090" y2={yCenter} />
        <motion.line
          className="rail-live"
          x1="128"
          y1={yCenter}
          y2={yCenter}
          animate={{ x2: railTrailEnd, opacity: 0.32 + carrierGlow * 0.52 }}
          transition={{ type: "spring", stiffness: 90, damping: 19 }}
        />
        <motion.path
          className="packet-service-trace"
          d={packetTrace}
          animate={{ opacity: line.runState === "standby" ? 0.08 : 0.72 }}
          transition={{ duration: 0.35 }}
        />
        {visualState.packetPosition > 8 && (
          <text className="service-trace-label" x={Math.max(172, packetX - 188)} y={yCenter - 38}>PACKET SERVICE TRACE</text>
        )}
      </g>

      <g className="endpoint-layer">
        <text x="896" y="154">RECEIVER STATION / RESET PLANT</text>
        <motion.ellipse
          className="endpoint-field"
          cx="1032"
          cy={yCenter}
          ry="116"
          animate={{ rx: apertureRx, opacity: 0.24 + visualState.opticsFocus * 0.52 }}
          transition={{ type: "spring", stiffness: 85, damping: 18 }}
        />
        <motion.ellipse
          className="endpoint-lock"
          cx="1032"
          cy={yCenter}
          ry="66"
          animate={{ rx: Math.max(14, apertureRx * (0.32 + visualState.opticsFocus * 0.2)) }}
        />
        <motion.line
          className="endpoint-focus"
          x1="1070"
          x2="1070"
          animate={{
            y1: yCenter - apertureHeight / 2,
            y2: yCenter + apertureHeight / 2,
            opacity: 0.48 + visualState.endpointAperture * 0.42
          }}
          transition={{ type: "spring", stiffness: 90, damping: 18 }}
        />
        <text className="aperture-label" x="1084" y={yCenter - apertureHeight / 2 - 8}>CATCH APERTURE</text>
        <motion.path
          className="reset-plant-coil"
          d={buildResetPlantCoil(visualState, clockPhase)}
          animate={{ opacity: 0.16 + visualState.residueDensity * 0.6 }}
          transition={{ duration: 0.45 }}
        />
      </g>

      <g className="phase-band-label">
        <rect x="512" y="388" width="176" height="48" rx="10" />
        <text x="600" y="410" textAnchor="middle">{phase.label}</text>
        <text x="600" y="428" textAnchor="middle">T+{formatClock(line.clock)}</text>
      </g>

      <g className="alarm-pin-layer">
        {visualState.pins.slice(0, 5).map((pin) => {
          const pinX = xScale(pin.position);
          const pinY = pinGeometry(pin.id).y;
          return (
            <motion.g
              className={`svg-alarm-pin ${pin.status}`}
              animate={{ x: pinX, y: pinY, opacity: 1 }}
              initial={false}
              key={pin.id}
            >
              <circle r="8" />
              <text x="14" y="5">{pinGeometry(pin.id).label}</text>
            </motion.g>
          );
        })}
      </g>

      <motion.g
        className={`packet-layer ${visualState.packetPulse ? "moving" : ""}`}
        animate={{ x: packetX, y: yCenter }}
        transition={{ type: "spring", stiffness: 88, damping: 18 }}
      >
        <motion.circle
          className="packet-leakage-halo"
          r={leakageRadius}
          fill="url(#leakage-glow)"
          animate={{ opacity: visualState.packetLeakage * 0.95 }}
        />
        <circle className="packet-wake" r={44 + line.controls.carrierDrive * 0.18} fill="url(#packet-glow)" />
        <line className="packet-tether" x1="-42" y1="0" x2="-7" y2="0" />
        <circle className="packet-isolation-ring" r="43" strokeWidth={isolationStroke} />
        <circle className="packet-body" r="35" />
        <text y="6" textAnchor="middle">{visualState.packetLabel}</text>
      </motion.g>
    </motion.svg>
  );
}

function buildServiceCorridor(visualState, clockPhase) {
  return buildClosedTube({
    left: 154,
    right: 1046,
    centerY: 238,
    halfBase: 38 + visualState.supportStrength * 16 - visualState.supportSag * 8,
    flare: 12 + visualState.supportStrength * 8 + visualState.carrierStability * 6,
    ripple: visualState.timingShear * 5 + visualState.backreactionPosture * 8 + visualState.perturbation.mediumNoise * 6,
    phase: clockPhase * 0.32
  });
}

function buildSupportEnvelope(visualState, clockPhase) {
  return buildClosedTube({
    left: 126,
    right: 1076,
    centerY: 238,
    halfBase: 72 + visualState.supportStrength * 42 - visualState.backreactionPosture * 10 - visualState.supportSag * 18,
    flare: 24 + visualState.supportStrength * 18 + visualState.plantSupplyPulse * 10,
    ripple: visualState.supportRipple * 22 + visualState.backreactionPosture * 15 + visualState.supportSag * 18,
    phase: clockPhase * 0.48
  });
}

function buildClosedTube({ left, right, centerY, halfBase, flare, ripple, phase }) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveCatmullRom.alpha(0.7));
  const top = Array.from({ length: 18 }, (_, index) => {
    const t = index / 17;
    const taper = 0.62 + Math.sin(Math.PI * t) * 0.38;
    const curve = Math.sin(t * Math.PI * 2 + phase) * ripple;
    return {
      x: left + (right - left) * t,
      y: centerY - (halfBase + flare * taper) + curve
    };
  });
  const bottom = Array.from({ length: 18 }, (_, index) => {
    const t = 1 - index / 17;
    const taper = 0.62 + Math.sin(Math.PI * t) * 0.38;
    const curve = Math.cos(t * Math.PI * 2 + phase * 0.8) * ripple;
    return {
      x: left + (right - left) * t,
      y: centerY + (halfBase + flare * taper) + curve
    };
  });
  return `${generator([...top, ...bottom])}Z`;
}

function buildSupportRibs(visualState, clockPhase) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  return Array.from({ length: 7 }, (_, index) => {
    const offset = -56 + index * 18.6;
    const points = Array.from({ length: 12 }, (_unused, pointIndex) => {
      const t = pointIndex / 11;
      return {
        x: 168 + t * 864,
        y: 238
          + offset
          + Math.sin(t * Math.PI * 2 + index * 0.5 + clockPhase * 0.22) * visualState.supportRipple * 8
          + Math.cos(t * Math.PI * 3) * visualState.backreactionPosture * 13
      };
    });
    return {
      id: `rib-${index}`,
      d: generator(points),
      opacity: 0.08 + visualState.supportStrength * 0.18 + visualState.backreactionPosture * 0.14
    };
  });
}

function buildMetricActuatorBands(visualState, clockPhase) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  const specs = [
    {
      id: "beta",
      y: 184,
      amplitude: 14 + visualState.betaFlow * 24,
      opacity: 0.1 + visualState.betaFlow * 0.36 + visualState.carrierRisk * 0.12
    },
    {
      id: "lapse",
      y: 212,
      amplitude: 8 + (1 - visualState.lapseCushion) * 24 + visualState.timingShear * 20,
      opacity: 0.1 + visualState.lapseCushion * 0.24 + visualState.timingShear * 0.16
    },
    {
      id: "rail-stretch",
      y: 266,
      amplitude: 8 + visualState.railStretch * 18 + visualState.supportRipple * 16,
      opacity: 0.08 + visualState.railStretch * 0.24 + visualState.supportRipple * 0.18
    },
    {
      id: "throat-capacity",
      y: 298,
      amplitude: 8 + visualState.throatCapacity * 28,
      opacity: 0.08 + visualState.throatCapacity * 0.28 + visualState.endpointAperture * 0.12
    }
  ];
  return specs.map((spec, bandIndex) => {
    const points = Array.from({ length: 18 }, (_unused, index) => {
      const t = index / 17;
      const packetPull = Math.max(0, 1 - Math.abs(visualState.packetPosition / 100 - t) * 3.2);
      return {
        x: 160 + t * 850,
        y: spec.y
          + Math.sin(t * Math.PI * 2 + clockPhase * (0.16 + bandIndex * 0.03)) * spec.amplitude * 0.32
          + packetPull * visualState.packetLeakage * 24
          - packetPull * visualState.packetIsolation * 7
      };
    });
    return {
      id: spec.id,
      d: generator(points),
      opacity: spec.opacity
    };
  });
}

function buildPacketTrace(visualState, packetX, yCenter, clockPhase) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveCatmullRom.alpha(0.6));
  const traceLength = 165 + visualState.betaFlow * 190 + visualState.timingShear * 70;
  const startX = Math.max(128, packetX - traceLength);
  const points = Array.from({ length: 12 }, (_unused, index) => {
    const t = index / 11;
    return {
      x: startX + (packetX - startX) * t,
      y: yCenter
        + Math.sin(t * Math.PI * 2.2 + clockPhase * 0.2) * visualState.timingShear * 16
        + Math.sin(t * Math.PI * 4.4) * visualState.packetLeakage * 12
        + (1 - t) * visualState.backreactionPosture * 10
    };
  });
  return generator(points);
}

function buildCarrierProbes(visualState, packetX, yCenter, clockPhase) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  const startX = Math.max(150, packetX + 18);
  const endpointX = 1070;
  return Array.from({ length: 6 }, (_unused, index) => {
    const lane = index - 2.5;
    const shear = visualState.carrierRisk * 56 + visualState.timingShear * 34;
    const points = [
      { x: startX, y: yCenter + lane * 9 },
      { x: 710 + lane * 5 + shear * 0.35, y: yCenter + lane * (18 + shear * 0.08) },
      { x: endpointX - 24, y: yCenter + lane * (10 + visualState.endpointAperture * 6) + visualState.timingShear * lane * 8 }
    ];
    return {
      id: `carrier-probe-${index}`,
      d: generator(points),
      focused: visualState.railTimeGovernance > 0.55 && visualState.carrierRisk < 0.45,
      opacity: 0.1 + visualState.railTimeGovernance * 0.26 + visualState.carrierRisk * 0.16
    };
  });
}

function buildOpticsBundle(visualState, packetX, yCenter, apertureRx, apertureHeight, clockPhase) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  const spread = 12 + (1 - visualState.receiverAcquisition) * 86 + visualState.timingShear * 30;
  const endpointX = 1070;
  return Array.from({ length: 9 }, (_, index) => {
    const lane = index - 4;
    const reach = 240 + visualState.receiverAcquisition * 420 + visualState.packetPosition * 2.2;
    const startX = Math.max(150, endpointX - reach);
    const startY = yCenter + lane * (7 + visualState.timingShear * 8);
    const targetWindow = apertureHeight * 0.44;
    const miss = (1 - visualState.endpointAperture) * lane * 16 + visualState.timingShear * lane * 7;
    const endY = yCenter + lane * Math.min(18, targetWindow / 5) + miss;
    const midY = yCenter
      + lane * spread
      + Math.sin(index + visualState.causalRisk * 2 + clockPhase * 0.25) * visualState.backreactionPosture * 22;
    const points = [
      { x: startX, y: startY },
      { x: 760 + visualState.timingShear * 64, y: midY },
      { x: endpointX - apertureRx * 0.18, y: endY }
    ];
    return {
      id: `optics-${index}`,
      d: generator(points),
      focused: visualState.receiverAcquisition > 0.58,
      opacity: 0.1 + visualState.receiverAcquisition * 0.28 + (index === 4 ? 0.22 : 0)
    };
  });
}

function buildResetPlantCoil(visualState, clockPhase) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  const amplitude = 14 + visualState.residueDensity * 42;
  const points = Array.from({ length: 22 }, (_unused, index) => {
    const t = index / 21;
    return {
      x: 1010 + t * 82,
      y: 318 + Math.sin(t * Math.PI * 7 + clockPhase * 0.24) * amplitude
    };
  });
  return generator(points);
}

function buildShearLines(visualState, clockPhase) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  return Array.from({ length: 8 }, (_, index) => {
    const x = 250 + index * 96 + visualState.timingShear * 42;
    const lean = visualState.timingShear * 86 + visualState.causalRisk * 28;
    const points = [
      { x: x + lean * 0.28 + Math.sin(clockPhase + index) * visualState.timingShear * 8, y: 74 },
      { x, y: 238 },
      { x: x - lean, y: 402 }
    ];
    return {
      id: `shear-${index}`,
      d: generator(points),
      opacity: Math.max(0.06, visualState.timingShear * 0.58 - index * 0.025)
    };
  });
}

function buildCausalFan(visualState, apertureRx) {
  const generator = d3Area()
    .x((point) => point.x)
    .y0((point) => point.y0)
    .y1((point) => point.y1)
    .curve(curveBasis);
  const compression = visualState.horizonRisk * 68;
  const points = Array.from({ length: 8 }, (_, index) => {
    const t = index / 7;
    const x = 890 + t * 220;
    const height = 108 - t * (58 + compression) + visualState.causalRisk * 20;
    return {
      x,
      y0: 238 - Math.max(22, height),
      y1: 238 + Math.max(22, height)
    };
  });
  points[0].x = 1032 - apertureRx * 0.92;
  return generator(points);
}

function buildChronologyLoop(visualState) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  const radius = 54 + visualState.chronologyRisk * 92;
  const cx = 760 + visualState.timingShear * 80;
  const cy = 344;
  const points = Array.from({ length: 18 }, (_, index) => {
    const theta = (index / 17) * Math.PI * 2;
    return {
      x: cx + Math.cos(theta) * radius * 1.55,
      y: cy + Math.sin(theta) * radius * 0.38
    };
  });
  return generator(points);
}

function buildResiduePath(visualState) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  const points = Array.from({ length: 11 }, (_, index) => {
    const t = index / 10;
    return {
      x: 706 + t * 370,
      y: 365
        + Math.sin(t * Math.PI * 2) * (10 + visualState.residueDensity * 30)
        + visualState.backreactionPosture * 16
    };
  });
  return generator(points);
}

function buildConstraintBands(visualState) {
  return [
    { id: "origin", x: 112, width: 88, opacity: 0.04 + visualState.supportRipple * 0.18 },
    { id: "source", x: 330, width: 96, opacity: 0.04 + visualState.sourceSaturation * 0.18 },
    { id: "release", x: 754, width: 92, opacity: 0.04 + visualState.backreactionPosture * 0.16 },
    { id: "endpoint", x: 990, width: 92, opacity: 0.04 + visualState.causalRisk * 0.22 }
  ];
}

function buildSourceResiduals(visualState) {
  const count = Math.ceil(visualState.sourceSaturation * 5);
  return Array.from({ length: count }, (_, index) => ({
    id: `residual-${index}`,
    x: 286 + index * 92 + visualState.sourceSaturation * 28,
    y: 92 + Math.sin(index * 1.7) * 9,
    r: 4 + visualState.sourceSaturation * 7,
    opacity: 0.12 + visualState.sourceSaturation * 0.44
  }));
}

function ServiceCommandButton({ command, state, onRun }) {
  return (
    <button
      type="button"
      className={`service-command ${command.group}`}
      disabled={!state.enabled}
      onClick={onRun}
      title={state.detail || command.detail}
    >
      <span>{command.group}</span>
      <strong>{state.label || command.label}</strong>
      <em>{state.detail || command.detail}</em>
    </button>
  );
}

function ControlSlider({ control, value, state, locked, accessLevel, onChange }) {
  return (
    <label className={`control-slider ${state.level} ${state.constrained ? "constrained" : ""} ${locked ? "locked" : ""}`}>
      <span>
        <small>{control.shortLabel}</small>
        <strong>{control.label}</strong>
        <b>{accessLevel === 1 ? "trim" : "engineering"}</b>
      </span>
      <input
        type="range"
        min="0"
        max="100"
        step="1"
        value={value}
        disabled={state.disabled || locked}
        onChange={(event) => onChange(event.target.value)}
        aria-label={control.label}
      />
      <i aria-hidden="true">
        <span>{control.minLabel}</span>
        <span>{control.maxLabel}</span>
      </i>
      <em>{locked ? "Requires higher override access." : state.constrained ? state.note : control.detail}</em>
    </label>
  );
}

function TelemetryMeter({ def, value, trend }) {
  const status = getTelemetryStatus(def, value);
  const fill = def.direction === "low" ? value : Math.min(100, value);
  return (
    <div className={`telemetry-meter ${status}`}>
      <div>
        <strong>{def.label}</strong>
        <span>{status}</span>
      </div>
      <div className="telemetry-bar" aria-hidden="true">
        <i style={{ width: `${fill}%` }} />
      </div>
      <Sparkline values={trend} direction={def.direction} />
      <small>{Math.round(value)}{def.unit}</small>
    </div>
  );
}

function Sparkline({ values, direction }) {
  const points = values.length ? values : [50, 50];
  const max = 100;
  const polyline = points
    .map((value, index) => {
      const x = points.length === 1 ? 0 : (index / (points.length - 1)) * 100;
      const y = direction === "low" ? 28 - (value / max) * 24 : 4 + (value / max) * 24;
      return `${x},${y}`;
    })
    .join(" ");
  return (
    <svg className="telemetry-spark" viewBox="0 0 100 32" preserveAspectRatio="none" aria-hidden="true">
      <polyline points={polyline} />
    </svg>
  );
}

function StatusTile({ label, value }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function PanelHead({ kicker, title, aside }) {
  return (
    <div className="terminal-panel-head">
      <div>
        <span>{kicker}</span>
        <h2>{title}</h2>
      </div>
      {aside && <strong>{aside}</strong>}
    </div>
  );
}

function originLabel(line) {
  if (line.runState === "standby") return "Staged";
  if (line.runState === "readying") return "Readying";
  if (line.runState === "armed") return "Armed";
  if (line.runState === "recovery") return "Recovery";
  if (line.packetPosition > 12) return "Released";
  return "Support online";
}

function endpointLabel(line) {
  if (line.runState === "standby") return "Waiting";
  if (line.packetPosition > 96) return "Secured";
  if (line.packetPosition > 76) return "Catch active";
  if (line.metrics.endpointConfidence > 64) return "Synced";
  return "Acquiring";
}

function stateLabel(runState) {
  const labels = {
    standby: "Standby",
    readying: "Readying",
    armed: "Armed",
    service: "Service",
    held: "Held",
    recovery: "Recovery",
    secured: "Secured"
  };
  return labels[runState] || runState;
}

function controlAccessLevel(controlId) {
  const operatorTrim = new Set([
    "supportDrive",
    "endpointSync",
    "catchAperture",
    "matchedHold",
    "carrierDrive",
    "releaseFade",
    "decompression",
    "resetPurge"
  ]);
  return operatorTrim.has(controlId) ? 1 : 2;
}

function pinGeometry(pinId) {
  const map = {
    supportMargin: { y: 142, label: "SUP" },
    sourceDebt: { y: 92, label: "PLT" },
    packetIsolation: { y: 198, label: "PKT" },
    packetLeakage: { y: 236, label: "LEAK" },
    endpointConfidence: { y: 156, label: "RCV" },
    timingDrift: { y: 284, label: "DRF" },
    resetResidue: { y: 366, label: "RST" },
    reservoirCharge: { y: 110, label: "RSV" },
    carrierRisk: { y: 300, label: "CAR" },
    stabilityPosture: { y: 214, label: "STB" },
    loadIndex: { y: 244, label: "LD" },
    releaseGuard: { y: 170, label: "FDE" },
    decompressionGuard: { y: 344, label: "DCP" }
  };
  return map[pinId] || { y: 232, label: "ALM" };
}
