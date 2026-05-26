import { useEffect, useMemo, useState } from "react";
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

        <section className="terminal-panel work-order-console" aria-label="Work orders">
          <PanelHead kicker="Work Orders" title="Line Queue" />
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
          <div className="work-order-brief">
            <strong>{activeWorkOrder.operationNotice}</strong>
            <span>{activeWorkOrder.cautions.join(" / ")}</span>
          </div>
        </section>

        <section className="terminal-panel line-console" aria-label="Live line simulation">
          <PanelHead
            kicker="Line"
            title="Single Rail Service"
            aside={`${phase.label} / ${condition.toUpperCase()}`}
          />
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
              <RailGraphic line={line} visualState={visualState} phase={phase} />
            </div>

            <div className="station-node endpoint">
              <span>Endpoint</span>
              <strong>{endpointLabel(line)}</strong>
              <small>catch aperture</small>
            </div>
          </div>
        </section>

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

function RailGraphic({ line, visualState, phase }) {
  const packetX = 120 + visualState.packetPosition * 9.58;
  const packetY = 238;
  const sourceWidth = Math.max(24, 650 * visualState.sourceLoad);
  const supportWidth = 760 + visualState.supportStrength * 160;
  const supportX = 600 - supportWidth / 2;
  const supportStroke = 3 + visualState.supportStrength * 9;
  const supportOpacity = 0.16 + visualState.supportStrength * 0.64;
  const apertureRx = 34 + visualState.endpointAperture * 92;
  const railTrailEnd = Math.max(132, Math.min(1088, packetX));
  const shearOpacity = visualState.timingShear * 0.62;
  const residueOpacity = visualState.resetResidue * 0.58;
  const stabilityOpacity = 0.08 + visualState.stabilityField * 0.3;
  const carrierGlow = Math.max(0.12, line.controls.carrierDrive / 100);
  const fieldLines = Array.from({ length: 14 }, (_, index) => ({
    id: `field-${index}`,
    y: 150 + index * 13,
    bend: (index - 6.5) * 5 * (1 - visualState.supportStrength)
  }));
  const shearLines = Array.from({ length: 8 }, (_, index) => ({
    id: `shear-${index}`,
    x: 245 + index * 96 + visualState.timingShear * 26,
    opacity: Math.max(0.08, shearOpacity - index * 0.03)
  }));

  return (
    <svg
      className={`rail-graphic ${visualState.condition} ${line.runState}`}
      viewBox="0 0 1200 470"
      preserveAspectRatio="none"
      role="img"
      aria-label={`Single rail service line, packet ${packetLabels[line.packetState] || line.packetState}`}
    >
      <defs>
        <pattern id="terminal-grid-pattern" width="40" height="30" patternUnits="userSpaceOnUse">
          <path d="M40 0H0V30" fill="none" stroke="rgba(218,228,199,0.055)" strokeWidth="1" />
        </pattern>
        <linearGradient id="support-gradient" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#e2c45c" stopOpacity="0.26" />
          <stop offset="0.25" stopColor="#94c98e" stopOpacity="0.42" />
          <stop offset="0.76" stopColor="#86b882" stopOpacity="0.26" />
          <stop offset="1" stopColor="#d8b24c" stopOpacity="0.2" />
        </linearGradient>
        <linearGradient id="source-gradient" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#dcc76b" stopOpacity="0.92" />
          <stop offset="0.56" stopColor="#bc7f3f" stopOpacity="0.88" />
          <stop offset="1" stopColor="#d1634e" stopOpacity="0.9" />
        </linearGradient>
        <linearGradient id="rail-live-gradient" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#d7c65f" />
          <stop offset="0.5" stopColor="#9fcb89" />
          <stop offset="1" stopColor="#d9c15f" />
        </linearGradient>
        <radialGradient id="packet-glow" cx="50%" cy="50%" r="58%">
          <stop offset="0" stopColor="#f1cc66" stopOpacity="0.9" />
          <stop offset="0.68" stopColor="#f1cc66" stopOpacity="0.28" />
          <stop offset="1" stopColor="#f1cc66" stopOpacity="0" />
        </radialGradient>
        <filter id="field-glow" x="-25%" y="-25%" width="150%" height="150%">
          <feGaussianBlur stdDeviation="8" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <rect className="rail-svg-backdrop" x="0" y="0" width="1200" height="470" />
      <rect className="rail-svg-grid" x="0" y="0" width="1200" height="470" fill="url(#terminal-grid-pattern)" />

      <g className="service-zones" aria-hidden="true">
        <rect x="112" y="24" width="88" height="420" />
        <rect x="330" y="24" width="96" height="420" />
        <rect x="754" y="24" width="92" height="420" />
        <rect x="990" y="24" width="92" height="420" />
      </g>

      <g className="source-flow-layer" aria-label="Source channel">
        <text x="242" y="58">SOURCE CHANNEL</text>
        <rect className="source-shell" x="242" y="76" width="650" height="32" rx="16" />
        <rect className="source-flow" x="242" y="76" width={sourceWidth} height="32" rx="16" />
      </g>

      <g className="stability-layer" opacity={stabilityOpacity}>
        <path d="M160 226 C320 96, 470 350, 622 224 S878 112, 1046 226" />
        <path d="M160 252 C338 156, 475 304, 628 252 S870 152, 1046 252" />
        <path d="M160 198 C328 154, 470 286, 628 198 S872 154, 1046 198" />
      </g>

      <g className="support-field-lines" opacity={supportOpacity}>
        {fieldLines.map((lineItem) => (
          <path
            key={lineItem.id}
            d={`M166 ${lineItem.y} C360 ${lineItem.y + lineItem.bend}, 830 ${lineItem.y - lineItem.bend}, 1034 ${lineItem.y}`}
          />
        ))}
      </g>

      <g className="support-layer" opacity={supportOpacity} filter="url(#field-glow)">
        <rect
          className="support-envelope-svg"
          x={supportX}
          y="138"
          width={supportWidth}
          height="202"
          rx="101"
          strokeWidth={supportStroke}
        />
        <path
          className="support-inner-rib"
          d="M234 178 C390 122, 812 122, 974 178 M234 298 C390 350, 812 350, 974 298"
        />
      </g>

      <g className="timing-layer" opacity={shearOpacity}>
        {shearLines.map((lineItem) => (
          <path
            key={lineItem.id}
            d={`M${lineItem.x} 88 L${lineItem.x - 44} 390`}
            opacity={lineItem.opacity}
          />
        ))}
      </g>

      <g className="reset-layer" opacity={residueOpacity}>
        <ellipse cx="882" cy="362" rx={118 + visualState.resetResidue * 230} ry={18 + visualState.resetResidue * 52} />
        <path d="M710 378 C830 334, 946 334, 1074 378" />
      </g>

      <g className="rail-path-layer">
        <line className="rail-base" x1="128" y1={packetY} x2="1090" y2={packetY} />
        <line className="rail-live" x1="128" y1={packetY} x2={railTrailEnd} y2={packetY} opacity={0.38 + carrierGlow * 0.42} />
      </g>

      <g className="endpoint-layer">
        <text x="922" y="152">CATCH APERTURE</text>
        <ellipse className="endpoint-field" cx="1032" cy={packetY} rx={apertureRx} ry="116" />
        <ellipse className="endpoint-lock" cx="1032" cy={packetY} rx={Math.max(14, apertureRx * 0.44)} ry="66" />
        <line className="endpoint-focus" x1="996" y1={packetY} x2="1080" y2={packetY} />
      </g>

      <g className="phase-band-label">
        <rect x="512" y="384" width="176" height="48" rx="10" />
        <text x="600" y="406" textAnchor="middle">{phase.label}</text>
        <text x="600" y="424" textAnchor="middle">T+{formatClock(line.clock)}</text>
      </g>

      <g className="alarm-pin-layer">
        {visualState.pins.slice(0, 5).map((pin) => {
          const pinX = 120 + pin.position * 9.58;
          const pinY = pinGeometry(pin.id).y;
          return (
            <g className={`svg-alarm-pin ${pin.status}`} transform={`translate(${pinX} ${pinY})`} key={pin.id}>
              <path d="M0 -9 L9 8 H-9 Z" />
              <text x="14" y="5">{pinGeometry(pin.id).label}</text>
            </g>
          );
        })}
      </g>

      <g className={`packet-layer ${visualState.packetPulse ? "moving" : ""}`} transform={`translate(${packetX} ${packetY})`}>
        <circle className="packet-wake" r={44 + line.controls.carrierDrive * 0.18} fill="url(#packet-glow)" />
        <line className="packet-tether" x1="-42" y1="0" x2="-7" y2="0" />
        <circle className="packet-body" r="35" />
        <text y="6" textAnchor="middle">{visualState.packetLabel}</text>
      </g>
    </svg>
  );
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
