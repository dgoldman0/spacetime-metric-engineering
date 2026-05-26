import { useEffect, useMemo, useState } from "react";
import { serviceProfiles } from "../serviceTrainer/serviceProfiles.js";
import {
  createInitialLine,
  dispatchLineCommand,
  formatClock,
  getDebrief,
  getLineCondition,
  getOperatorCommands,
  getTelemetryStatus,
  getTerminalAdvisories,
  phaseDefs,
  phaseSequence,
  telemetryDefs,
  tickLine
} from "../serviceTrainer/lineSimulator.js";
import { procedureSteps } from "../serviceTrainer/lineProcedures.js";

const commandGroupLabels = {
  intake: "Intake",
  readiness: "Readiness",
  authority: "Authority",
  service: "Line Service",
  closeout: "Closeout",
  control: "Control"
};

const packetLabels = {
  staged: "staged",
  accepted: "accepted",
  in_service: "in service",
  handoff_pending: "handoff pending",
  rematched: "rematched",
  released: "released",
  release_holding: "release holding",
  secured: "secured",
  recovery: "recovery"
};

export function RailServiceTerminal({ workspaces = [], onWorkspaceChange }) {
  const [profileId, setProfileId] = useState("standard");
  const [line, setLine] = useState(() => createInitialLine("standard"));
  const condition = getLineCondition(line);
  const commands = useMemo(() => getOperatorCommands(line), [line]);
  const advisories = useMemo(() => getTerminalAdvisories(line), [line]);
  const debrief = getDebrief(line);
  const activeProfile = serviceProfiles.find((profile) => profile.id === profileId) || serviceProfiles[1];
  const alarmCount = line.events.filter((event) => event.level === "alarm" || event.level === "abort").length;

  useEffect(() => {
    const active = ["supporting", "carrying", "catch_window", "fading", "decompressing", "resetting"].includes(line.phase);
    if (!active || line.awaitingCommand || line.failure) return undefined;
    const interval = window.setInterval(() => {
      setLine((current) => tickLine(current));
    }, 850);
    return () => window.clearInterval(interval);
  }, [line.phase, line.awaitingCommand, line.failure]);

  function loadProfile(nextProfileId) {
    setProfileId(nextProfileId);
    setLine(createInitialLine(nextProfileId));
  }

  function runCommand(commandId) {
    if (commandId === "RESET_TRAINER") {
      setLine(createInitialLine(profileId));
      return;
    }
    setLine((current) => dispatchLineCommand(current, commandId));
  }

  return (
    <div className="service-terminal-shell">
      <header className="terminal-topbar">
        <div className="terminal-brand">
          <span>ARS</span>
          <strong>Rail Service Terminal</strong>
          <small>SIM TRAINER / ARCHITECTURE LOGIC / NOT PHYSICS SOLVER</small>
        </div>
        <nav className="terminal-nav" aria-label="Training surfaces">
          {workspaces.map((workspace) => (
            <button
              type="button"
              key={workspace.id}
              className={workspace.serviceMode ? "active" : ""}
              onClick={() => onWorkspaceChange?.(workspace.id)}
            >
              {workspace.serviceMode ? "Service Terminal" : workspace.title}
            </button>
          ))}
        </nav>
      </header>

      <main className="terminal-grid">
        <section className={`terminal-status ${condition}`} aria-label="Line status">
          <StatusTile label="Line" value={line.lineId} />
          <StatusTile label="Manifest" value={line.manifestId} />
          <StatusTile label="Clock" value={`T+${formatClock(line.clock)}`} />
          <StatusTile label="State" value={stateLabel(line)} />
          <StatusTile label="Authority" value={line.authorityState} />
          <StatusTile label="Packet" value={packetLabels[line.packetState] || line.packetState} />
          <StatusTile label="Alarms" value={String(alarmCount)} />
        </section>

        <section className="terminal-panel manifest-console" aria-label="Service manifests">
          <PanelHead kicker="Manifest" title="Run Order" />
          <div className="manifest-table">
            {serviceProfiles.map((profile) => {
              const selected = profile.id === profileId;
              return (
                <button
                  type="button"
                  key={profile.id}
                  className={selected ? "selected" : ""}
                  onClick={() => loadProfile(profile.id)}
                  disabled={line.gates.manifestAccepted && !line.failure && line.phase !== "secured"}
                >
                  <span>{profile.manifestId}</span>
                  <strong>{profile.callSign}</strong>
                  <small>{profile.classLabel} / {profile.priority}</small>
                </button>
              );
            })}
          </div>
          <div className="manifest-brief">
            <strong>{activeProfile.objective}</strong>
            <span>{activeProfile.constraints.join(" / ")}</span>
          </div>
        </section>

        <section className="terminal-panel line-console" aria-label="Line schematic">
          <PanelHead kicker="Line" title="Single Rail Service" aside={line.awaitingCommand ? "AWAITING AUTHORITY" : stateLabel(line).toUpperCase()} />
          <div className="line-schematic">
            <div className="line-bus" aria-hidden="true">
              <span style={{ width: `${packetPosition(line)}%` }} />
            </div>
            <div className="phase-strip">
              {phaseDefs.map((phase) => (
                <div className={`phase-cell ${phaseClass(line, phase.id)}`} key={phase.id}>
                  <span>{phase.shortLabel}</span>
                  <strong>{phase.label}</strong>
                  <small>{phase.detail}</small>
                  {phase.id === effectivePhase(line) && activePhaseProgress(line) > 0 && (
                    <div className="phase-meter" aria-hidden="true">
                      <i style={{ width: `${activePhaseProgress(line)}%` }} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="terminal-panel telemetry-console" aria-label="Telemetry">
          <PanelHead kicker="Telemetry" title="Line State" />
          <div className="telemetry-grid">
            {telemetryDefs.map((def) => (
              <TelemetryMeter key={def.id} def={def} value={line.metrics[def.id]} />
            ))}
          </div>
        </section>

        <section className="terminal-panel command-stack" aria-label="Command stack">
          <PanelHead kicker="Command" title="Operator Authority" />
          {Object.entries(groupCommands(commands)).map(([group, items]) => (
            <div className="command-group" key={group}>
              <h3>{commandGroupLabels[group] || group}</h3>
              <div className="terminal-command-grid">
                {items.map((command) => (
                  <button
                    type="button"
                    key={command.id}
                    className={`${command.primary ? "primary" : ""} ${command.danger ? "danger" : ""}`}
                    onClick={() => runCommand(command.id)}
                    disabled={!command.enabled}
                  >
                    <strong>{command.label}</strong>
                    <span>{command.enabled ? "available" : command.reason}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </section>

        <section className="terminal-panel procedure-console" aria-label="Procedure checklist">
          <PanelHead kicker="Procedure" title="Gate Board" />
          <div className="procedure-ledger">
            {procedureSteps.map((step) => (
              <div className={line.gates[step.id] ? "complete" : "pending"} key={step.id}>
                <span>{line.gates[step.id] ? "set" : "open"}</span>
                <strong>{step.label}</strong>
                <small>{step.group}</small>
              </div>
            ))}
          </div>
        </section>

        <section className="terminal-panel advisory-console" aria-label="Advisories">
          <PanelHead kicker="Advisory" title={line.failure ? "Recovery" : "Watch Floor"} />
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

function TelemetryMeter({ def, value }) {
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
      <small>{Math.round(value)}{def.unit}</small>
    </div>
  );
}

function groupCommands(commands) {
  return commands.reduce((groups, command) => {
    if (!groups[command.group]) groups[command.group] = [];
    groups[command.group].push(command);
    return groups;
  }, {});
}

function stateLabel(line) {
  if (line.failure) return "Recovery";
  if (line.phase === "held") return "Held";
  if (line.awaitingCommand) return "Awaiting";
  return line.phase.replaceAll("_", " ");
}

function effectivePhase(line) {
  if (line.phase === "held") return line.previousPhase || "precheck";
  if (line.phase === "aborted") return line.previousPhase || "standby";
  return line.phase;
}

function activePhaseProgress(line) {
  if (line.phase === "held" || line.phase === "aborted") return line.phaseProgress;
  return line.phaseProgress;
}

function phaseClass(line, phaseId) {
  const effective = effectivePhase(line);
  if (line.phase === "aborted" && phaseId === effective) return "failed";
  if (line.phase === "held" && phaseId === effective) return "held";
  if (phaseId === effective) return line.awaitingCommand ? "waiting" : "active";
  if (phaseIsComplete(line, phaseId)) return "complete";
  return "pending";
}

function phaseIsComplete(line, phaseId) {
  if (phaseId === "standby") return line.gates.manifestAccepted;
  if (phaseId === "precheck") return line.gates.precheckClear;
  if (phaseId === "armed") return line.gates.lineArmed;
  const gateByPhase = {
    supporting: "supportEstablished",
    carrying: "carryComplete",
    catch_window: "catchConfirmed",
    fading: "fadeComplete",
    decompressing: "decompressed",
    resetting: "resetClear",
    secured: "secured"
  };
  return Boolean(line.gates[gateByPhase[phaseId]]);
}

function packetPosition(line) {
  const phase = effectivePhase(line);
  if (phase === "standby") return 2;
  if (phase === "precheck") return 8;
  if (phase === "armed") return 16;
  if (phase === "secured") return 100;
  const index = phaseSequence.indexOf(phase);
  if (index < 0) return 0;
  const start = 24;
  const usable = 72;
  return Math.min(100, start + ((index + line.phaseProgress / 100) / phaseSequence.length) * usable);
}
