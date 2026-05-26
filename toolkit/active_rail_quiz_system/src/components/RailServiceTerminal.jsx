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

export function RailServiceTerminal() {
  const [profileId, setProfileId] = useState("standard");
  const [line, setLine] = useState(() => createInitialLine("standard"));
  const condition = getLineCondition(line);
  const commands = useMemo(() => getOperatorCommands(line), [line]);
  const advisories = useMemo(() => getTerminalAdvisories(line), [line]);
  const debrief = getDebrief(line);
  const activeProfile = serviceProfiles.find((profile) => profile.id === profileId) || serviceProfiles[1];
  const alarmCount = line.events.filter((event) => event.level === "alarm" || event.level === "abort").length;
  const commandModel = buildCommandModel(commands, line);

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
          <div
            className={`live-line-view ${condition} ${line.phase}`}
            style={{
              "--packet-position": `${packetPosition(line)}%`,
              "--support-alpha": String(0.3 + line.metrics.supportMargin / 160),
              "--support-glow": `${12 + line.metrics.supportMargin * 0.25}px`,
              "--drift-alpha": String(Math.min(0.7, line.metrics.timingDrift / 115)),
              "--residue-alpha": String(Math.min(0.72, line.metrics.resetResidue / 120))
            }}
          >
            <div className="station-node origin">
              <span>Origin</span>
              <strong>{line.gates.supportEstablished ? "Support online" : line.gates.lineArmed ? "Armed" : "Staged"}</strong>
              <small>support {Math.round(line.metrics.supportMargin)}%</small>
            </div>

            <div className="rail-viewport">
              <div className="support-envelope" aria-hidden="true" />
              <div className="drift-band" aria-hidden="true" />
              <div className="rail-core" aria-hidden="true">
                <i />
              </div>
              <div className="packet-marker" aria-label={`Packet ${packetLabels[line.packetState] || line.packetState}`}>
                <span>{packetLabel(line)}</span>
              </div>
              <div className="phase-readout">
                <span>{activePhaseCode(line)}</span>
                <strong>{getPhaseLabel(line)}</strong>
                <small>{phaseInstruction(line)}</small>
              </div>
              {advisories.filter((item) => item.level !== "nominal").slice(0, 3).map((advisory, index) => (
                <div
                  className={`line-alarm ${advisory.level}`}
                  style={{ left: `${24 + index * 24}%` }}
                  key={advisory.id}
                >
                  {advisory.title}
                </div>
              ))}
            </div>

            <div className="station-node endpoint">
              <span>Endpoint</span>
              <strong>{line.gates.catchConfirmed ? "Rematched" : line.gates.endpointSynced ? "Synced" : "Waiting"}</strong>
              <small>confidence {Math.round(line.metrics.endpointConfidence)}%</small>
            </div>
          </div>

          <div className="phase-timeline" aria-label="Service phase timeline">
            {phaseDefs.map((phase) => (
              <div className={`phase-chip ${phaseClass(line, phase.id)}`} key={phase.id}>
                <span>{phase.shortLabel}</span>
                <strong>{phase.label}</strong>
              </div>
            ))}
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

        <section className="terminal-panel action-console" aria-label="Operator authority">
          <PanelHead kicker="Authority" title="Current Control" />
          <div className="primary-action-card">
            <span>{commandModel.primary ? "Next authorized action" : "No primary authority"}</span>
            <strong>{commandModel.primary?.label || "Hold for diagnostics"}</strong>
            <p>{primaryActionDetail(line, commandModel.primary)}</p>
            <button
              type="button"
              onClick={() => commandModel.primary && runCommand(commandModel.primary.id)}
              disabled={!commandModel.primary}
            >
              {commandModel.primary?.label || "No Action"}
            </button>
          </div>

          <div className="context-actions">
            {commandModel.contextual.map((command) => (
              <button
                type="button"
                key={command.id}
                className={command.danger ? "danger" : ""}
                onClick={() => runCommand(command.id)}
              >
                <strong>{command.label}</strong>
                <span>{commandGroupLabels[command.group] || command.group}</span>
              </button>
            ))}
          </div>

          <details className="interlock-drawer">
            <summary>
              <span>Interlocks</span>
              <strong>{commandModel.locked.length} locked</strong>
            </summary>
            <div>
              {commandModel.locked.map((command) => (
                <button
                  type="button"
                  key={command.id}
                  onClick={() => runCommand(command.id)}
                  disabled
                >
                  <strong>{command.label}</strong>
                  <span>{command.reason}</span>
                </button>
              ))}
            </div>
          </details>
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

function buildCommandModel(commands, line) {
  const persistentIds = line.phase === "held"
    ? ["RESUME", "ABORT", "RESET_TRAINER"]
    : ["HOLD", "ABORT", "RESET_TRAINER"];
  const primary = commands.find((command) => command.primary && command.enabled)
    || commands.find((command) => command.enabled && command.id !== "RESET_TRAINER")
    || null;
  const contextual = commands
    .filter((command) => command.enabled)
    .filter((command) => command.id !== primary?.id)
    .filter((command) => persistentIds.includes(command.id) || command.group === "readiness")
    .slice(0, 5);
  const locked = commands
    .filter((command) => !command.enabled)
    .filter((command) => command.id !== "RESET_TRAINER");
  return { primary, contextual, locked };
}

function primaryActionDetail(line, command) {
  if (!command) {
    if (line.failure) return "Recovery authority is active. Inspect the debrief and reset when ready.";
    return "The line has no authorized command in this state.";
  }
  const details = {
    ACCEPT_MANIFEST: "Open the run order and move the line into readiness.",
    RUN_PRECHECK: "Check support, stability, and reset gates before arming.",
    PRECHARGE_SUPPORT: "Raise support margin before active service draws on it.",
    CLOSE_LEDGER: "Reduce source debt before the demanded-source burden rises.",
    SYNC_ENDPOINT: "Improve catch confidence and reduce timing drift.",
    STABILITY_SWEEP: "Strengthen stability posture before continuing.",
    FLUSH_RESET_PATH: "Clear residue so reset and reuse gates can close.",
    ARM_LINE: "Issue line authority once readiness gates are set.",
    START_SUPPORT: "Bring the corridor support envelope online.",
    BEGIN_CARRY: "Move the accepted packet through the active service interval.",
    CATCH_REMATCH: "Confirm endpoint catch before release fade.",
    AUTHORIZE_FADE: "Withdraw the carrier after catch/rematch is secured.",
    DECOMPRESS: "Unload support and source channels in controlled order.",
    RESET_LINE: "Clear the rail after decompression.",
    SECURE: "Close the run and open the debrief.",
    HOLD: "Freeze active evolution while you recover margins.",
    RESUME: "Release the held line back into active evolution.",
    ABORT: "Stop the run and enter recovery authority.",
    RESET_TRAINER: "Return the terminal to a fresh manifest state."
  };
  return details[command.id] || "Authorized by current line state.";
}

function getPhaseLabel(line) {
  const phase = phaseDefs.find((item) => item.id === effectivePhase(line));
  return phase?.label || stateLabel(line);
}

function activePhaseCode(line) {
  const phase = phaseDefs.find((item) => item.id === effectivePhase(line));
  return phase?.shortLabel || "SYS";
}

function phaseInstruction(line) {
  if (line.failure) return "Recovery authority active.";
  if (line.phase === "held") return "Line motion held for intervention.";
  if (line.awaitingCommand) return "Phase complete; issue next authority.";
  if (line.phase === "standby") return "Manifest staged for operator acceptance.";
  if (line.phase === "precheck") return "Bring readiness gates online.";
  if (line.phase === "armed") return "Support authority available.";
  if (line.phase === "secured") return "Run closed; debrief available.";
  return "Active service evolution in progress.";
}

function packetLabel(line) {
  if (line.failure) return "REC";
  if (line.phase === "secured") return "SEC";
  if (line.phase === "standby") return "PKT";
  if (line.phase === "held") return "HLD";
  return "PKT";
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
