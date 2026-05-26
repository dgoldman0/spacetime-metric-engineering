import { useEffect, useMemo, useRef, useState } from "react";
import { scaleLinear } from "d3-scale";
import { area as d3Area, curveBasis, curveCatmullRom, line as d3Line } from "d3-shape";
import { motion } from "framer-motion";
import { workOrders } from "../serviceTrainer/serviceProfiles.js";
import {
  applyLineAction,
  controlDefs,
  createInitialLine,
  formatClock,
  getActionState,
  getControlState,
  getDebrief,
  getLineCondition,
  getLineConstraints,
  getLineVisualState,
  getOperatingPhase,
  getTelemetryStatus,
  getTerminalAdvisories,
  telemetryDefs,
  tickLine,
  updateLineControl
} from "../serviceTrainer/lineSimulator.js";

const actionIds = ["accept", "arm", "hold", "releaseHold", "abort", "secure", "reset"];

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
    if (line.runState === "standby" || line.runState === "recovery" || line.runState === "secured") return undefined;
    const interval = window.setInterval(() => {
      setLine((current) => tickLine(current));
    }, line.runState === "service" ? 620 : 820);
    return () => window.clearInterval(interval);
  }, [line.runState]);

  function loadProfile(nextProfileId) {
    if (!["standby", "recovery", "secured"].includes(line.runState)) return;
    setProfileId(nextProfileId);
    setLine(createInitialLine(nextProfileId));
  }

  function moveControl(controlId, value) {
    setLine((current) => updateLineControl(current, controlId, value));
  }

  function runAction(actionId) {
    setLine((current) => applyLineAction(current, actionId));
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
            <div className="station-node origin">
              <span>Origin</span>
              <strong>{originLabel(line)}</strong>
              <small>support field</small>
            </div>

            <div className="rail-viewport">
              <FieldParticleLayer visualState={visualState} line={line} />
              <RailGraphic line={line} visualState={visualState} phase={phase} />
            </div>

            <div className="station-node endpoint">
              <span>Endpoint</span>
              <strong>{endpointLabel(line)}</strong>
              <small>catch aperture</small>
            </div>
          </div>
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
            </div>
          </section>
        </aside>

        <section className="terminal-panel control-console" aria-label="Operator controls">
          <PanelHead kicker="Operator Station" title="Line Controls" />
          <div className="control-surface">
            {controlDefs.map((control) => (
              <ControlSlider
                key={control.id}
                control={control}
                value={line.controls[control.id]}
                state={getControlState(line, control.id)}
                onChange={(value) => moveControl(control.id, value)}
              />
            ))}
          </div>
          <div className="authority-strip" aria-label="Authority controls">
            {actionIds.map((actionId) => {
              const action = getActionState(line, actionId);
              if (actionId === "releaseHold" && line.runState !== "held") return null;
              if (actionId === "hold" && line.runState === "held") return null;
              return (
                <button
                  type="button"
                  key={actionId}
                  className={`authority-button ${actionId}`}
                  disabled={!action.enabled}
                  onClick={() => runAction(actionId)}
                  title={action.detail}
                >
                  <span>{authorityGroup(actionId)}</span>
                  <strong>{action.label}</strong>
                </button>
              );
            })}
          </div>
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
        field.clear();
        particles.forEach((particle) => {
          const drift = particle.speed * (0.35 + source + residue + causal);
          particle.x = (particle.x + drift) % 1;
          const railBand = particle.band === 0;
          const yBase = railBand ? 0.46 : particle.band === 1 ? 0.3 : 0.64;
          const x = particle.x * width;
          const y = (yBase + Math.sin((particle.x + particle.id) * 6.283) * (0.015 + causal * 0.03)) * height;
          const alpha = 0.025 + residue * 0.1 + source * 0.08 + support * 0.025;
          const color = residue > 0.48 && particle.band === 2 ? 0xd6a23d : particle.band === 1 ? 0xd0bb68 : 0x9bc58b;
          field.circle(x, y, particle.radius + residue * 1.4 + source * 0.6).fill({ color, alpha });
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

function RailGraphic({ line, visualState, phase }) {
  const xScale = scaleLinear().domain([0, 100]).range([118, 1088]);
  const yCenter = 238;
  const packetX = xScale(visualState.packetPosition);
  const sourceWidth = Math.max(28, 650 * visualState.sourceLoad);
  const sourceResiduals = buildSourceResiduals(visualState);
  const apertureRx = 28 + visualState.endpointAperture * 102;
  const railTrailEnd = Math.max(132, Math.min(1088, packetX));
  const carrierGlow = Math.max(0.12, line.controls.carrierDrive / 100);
  const supportOpacity = 0.28 + visualState.supportStrength * 0.62;
  const supportStroke = 5 + visualState.supportStrength * 8 + visualState.backreactionPosture * 4;
  const supportEnvelope = buildSupportEnvelope(visualState);
  const supportRibs = buildSupportRibs(visualState);
  const worldline = buildWorldline(visualState, packetX, yCenter);
  const optics = buildOpticsBundle(visualState, packetX, yCenter, apertureRx);
  const shearLines = buildShearLines(visualState);
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
          <stop offset="0" stopColor="#e6c963" stopOpacity="0.22" />
          <stop offset="0.22" stopColor="#9ed18f" stopOpacity="0.46" />
          <stop offset="0.74" stopColor="#8bc488" stopOpacity="0.3" />
          <stop offset="1" stopColor="#d8b24c" stopOpacity="0.22" />
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

      <g className="source-flow-layer" aria-label="Demanded-source ledger channel">
        <text x="242" y="58">DEMANDED-SOURCE LEDGER</text>
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

      <g className="support-layer" opacity={supportOpacity} filter="url(#field-glow)">
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
      </g>

      <g className="optics-layer" aria-label="Endpoint optics">
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
          className="packet-worldline"
          d={worldline}
          animate={{ opacity: line.runState === "standby" ? 0.12 : 0.64 }}
          transition={{ duration: 0.35 }}
        />
      </g>

      <g className="endpoint-layer">
        <text x="920" y="154">CATCH / OPTICS APERTURE</text>
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
        <line className="endpoint-focus" x1="996" y1={yCenter} x2="1080" y2={yCenter} />
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
        <circle className="packet-wake" r={44 + line.controls.carrierDrive * 0.18} fill="url(#packet-glow)" />
        <line className="packet-tether" x1="-42" y1="0" x2="-7" y2="0" />
        <circle className="packet-body" r="35" />
        <text y="6" textAnchor="middle">{visualState.packetLabel}</text>
      </motion.g>
    </motion.svg>
  );
}

function buildSupportEnvelope(visualState) {
  const x = scaleLinear().domain([0, 1]).range([146, 1058]);
  const points = Array.from({ length: 18 }, (_, index) => {
    const t = index / 17;
    const edgeTaper = Math.sin(Math.PI * t);
    const ripple = Math.sin(t * Math.PI * 4 + visualState.timingShear * 2) * visualState.supportRipple * 18;
    const backreactionSag = Math.cos(t * Math.PI * 2) * visualState.backreactionPosture * 12;
    const halfHeight = 62 + visualState.supportStrength * 72 - visualState.backreactionPosture * 16 + edgeTaper * 22;
    return {
      x: x(t),
      y: 238 + ripple + backreactionSag,
      halfHeight
    };
  });
  return d3Area()
    .x((point) => point.x)
    .y0((point) => point.y - point.halfHeight)
    .y1((point) => point.y + point.halfHeight)
    .curve(curveCatmullRom.alpha(0.62))(points);
}

function buildSupportRibs(visualState) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  return Array.from({ length: 9 }, (_, index) => {
    const offset = -66 + index * 16.5;
    const points = Array.from({ length: 12 }, (_unused, pointIndex) => {
      const t = pointIndex / 11;
      return {
        x: 166 + t * 868,
        y: 238
          + offset
          + Math.sin(t * Math.PI * 2 + index * 0.7) * visualState.supportRipple * 18
          + Math.cos(t * Math.PI * 3) * visualState.backreactionPosture * 13
      };
    });
    return {
      id: `rib-${index}`,
      d: generator(points),
      opacity: 0.12 + visualState.supportStrength * 0.22 + visualState.backreactionPosture * 0.16
    };
  });
}

function buildWorldline(visualState, packetX, yCenter) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveCatmullRom.alpha(0.6));
  const startX = Math.max(128, packetX - 310);
  const points = Array.from({ length: 12 }, (_unused, index) => {
    const t = index / 11;
    return {
      x: startX + (packetX - startX) * t,
      y: yCenter
        + Math.sin(t * Math.PI * 2.4) * visualState.timingShear * 20
        + (1 - t) * visualState.backreactionPosture * 14
    };
  });
  return generator(points);
}

function buildOpticsBundle(visualState, packetX, yCenter, apertureRx) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  const spread = 8 + (1 - visualState.opticsFocus) * 68 + visualState.timingShear * 26;
  const endpointX = 1032;
  return Array.from({ length: 7 }, (_, index) => {
    const lane = index - 3;
    const startX = Math.max(150, packetX + 28);
    const startY = yCenter + lane * (8 + visualState.timingShear * 11);
    const endY = yCenter + lane * spread * 0.32 + visualState.timingShear * lane * 5;
    const midY = yCenter
      + lane * spread
      + Math.sin(index + visualState.causalRisk * 2) * visualState.backreactionPosture * 20;
    const points = [
      { x: startX, y: startY },
      { x: 610 + visualState.timingShear * 46, y: midY },
      { x: endpointX - apertureRx * 0.35, y: endY }
    ];
    return {
      id: `optics-${index}`,
      d: generator(points),
      focused: visualState.opticsFocus > 0.55,
      opacity: 0.16 + visualState.endpointAperture * 0.2 + (index === 3 ? 0.18 : 0)
    };
  });
}

function buildShearLines(visualState) {
  const generator = d3Line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(curveBasis);
  return Array.from({ length: 9 }, (_, index) => {
    const x = 250 + index * 91 + visualState.timingShear * 36;
    const lean = visualState.timingShear * 74 + visualState.causalRisk * 24;
    const points = [
      { x: x + lean * 0.3, y: 68 },
      { x, y: 238 },
      { x: x - lean, y: 406 }
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

function ControlSlider({ control, value, state, onChange }) {
  return (
    <label className={`control-slider ${state.level} ${state.constrained ? "constrained" : ""}`}>
      <span>
        <small>{control.shortLabel}</small>
        <strong>{control.label}</strong>
      </span>
      <input
        type="range"
        min="0"
        max="100"
        step="1"
        value={value}
        disabled={state.disabled}
        onChange={(event) => onChange(event.target.value)}
        aria-label={control.label}
      />
      <i aria-hidden="true">
        <span>{control.minLabel}</span>
        <span>{control.maxLabel}</span>
      </i>
      <em>{state.constrained ? state.note : control.detail}</em>
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
  return "Tuning";
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

function authorityGroup(actionId) {
  const groups = {
    accept: "intake",
    arm: "authority",
    hold: "control",
    releaseHold: "control",
    abort: "recovery",
    secure: "closeout",
    reset: "system"
  };
  return groups[actionId] || "control";
}

function pinGeometry(pinId) {
  const map = {
    supportMargin: { y: 142, label: "SUP" },
    sourceDebt: { y: 92, label: "SRC" },
    endpointConfidence: { y: 156, label: "CTH" },
    timingDrift: { y: 284, label: "DRF" },
    resetResidue: { y: 366, label: "RST" },
    stabilityPosture: { y: 214, label: "STB" },
    loadIndex: { y: 244, label: "LD" },
    releaseGuard: { y: 170, label: "FDE" },
    decompressionGuard: { y: 344, label: "DCP" }
  };
  return map[pinId] || { y: 232, label: "ALM" };
}
