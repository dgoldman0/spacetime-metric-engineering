import { getFailureMode, evaluateFailure } from "./failureModes.js";
import {
  getPhase,
  phaseCommandLabel,
  phaseCompletionGate,
  phaseDefs,
  phaseSequence,
  telemetryDefs
} from "./lineProcedures.js";
import { getServiceProfile } from "./serviceProfiles.js";

const activePhases = new Set(["supporting", "carrying", "catch_window", "fading", "decompressing", "resetting"]);
const procedureCommands = new Set([
  "RUN_PRECHECK",
  "PRECHARGE_SUPPORT",
  "CLOSE_LEDGER",
  "SYNC_ENDPOINT",
  "STABILITY_SWEEP",
  "FLUSH_RESET_PATH"
]);

export function createInitialLine(profileId = "standard") {
  const profile = getServiceProfile(profileId);
  return {
    profileId: profile.id,
    manifestId: profile.manifestId,
    lineId: profile.lineId,
    clock: 0,
    phase: "standby",
    previousPhase: null,
    phaseProgress: 0,
    awaitingCommand: false,
    packetState: "staged",
    authorityState: "manifest",
    metrics: { ...profile.metrics },
    gates: {
      manifestAccepted: false,
      precheckClear: false,
      supportPermit: false,
      ledgerClosed: false,
      endpointSynced: false,
      lineArmed: false,
      supportEstablished: false,
      carryComplete: false,
      catchConfirmed: false,
      fadeComplete: false,
      decompressed: false,
      resetClear: false,
      secured: false
    },
    notices: {},
    events: [
      makeEvent(0, "system", "manifest", `${profile.manifestId} loaded for ${profile.callSign}.`)
    ],
    failure: null,
    completedAt: null
  };
}

export function tickLine(line) {
  if (!activePhases.has(line.phase) || line.awaitingCommand || line.failure) return line;
  const profile = getServiceProfile(line.profileId);
  const clock = line.clock + 1;
  const metrics = evolveMetrics(line.metrics, line.phase, profile);
  const phaseProgress = Math.min(100, line.phaseProgress + profile.pace);
  const failure = evaluateFailure({ ...line, clock, metrics, phaseProgress });

  if (failure) {
    return {
      ...line,
      clock,
      metrics,
      phaseProgress,
      phase: "aborted",
      authorityState: "recovery",
      packetState: "recovery",
      failure,
      events: addEvent(line.events, makeEvent(clock, "alarm", failure.subsystem, failure.title))
    };
  }

  const noticeResult = addTelemetryNotices(line, metrics, clock);
  if (phaseProgress >= 100) {
    return completePhase({
      ...line,
      clock,
      metrics,
      phaseProgress: 100,
      notices: noticeResult.notices,
      events: noticeResult.events
    });
  }

  return {
    ...line,
    clock,
    metrics,
    phaseProgress,
    notices: noticeResult.notices,
    events: noticeResult.events
  };
}

export function dispatchLineCommand(line, commandId) {
  const locked = getInterlockReason(line, commandId);
  if (locked) {
    return {
      ...line,
      events: addEvent(line.events, makeEvent(line.clock, "interlock", "authority", `${commandLabel(commandId)} locked: ${locked}`))
    };
  }

  switch (commandId) {
    case "ACCEPT_MANIFEST":
      return {
        ...line,
        phase: "precheck",
        packetState: "accepted",
        authorityState: "readiness",
        gates: { ...line.gates, manifestAccepted: true },
        events: addEvent(line.events, makeEvent(line.clock, "procedure", "manifest", "Manifest accepted. Readiness precheck opened."))
      };
    case "RUN_PRECHECK":
      return runPrecheck(line);
    case "PRECHARGE_SUPPORT":
      return applyProcedure(line, {
        message: "Support precharge complete.",
        metrics: {
          supportMargin: 18,
          sourceDebt: 4,
          stabilityPosture: 3,
          loadIndex: 4,
          timingDrift: 2
        }
      });
    case "CLOSE_LEDGER":
      return applyProcedure(line, {
        message: "Source ledger closure accepted.",
        gates: { ledgerClosed: true },
        metrics: {
          sourceDebt: -28,
          stabilityPosture: 2,
          loadIndex: -3
        }
      });
    case "SYNC_ENDPOINT":
      return applyProcedure(line, {
        message: "Endpoint synchronization accepted.",
        gates: { endpointSynced: true },
        metrics: {
          endpointConfidence: 26,
          timingDrift: -22,
          loadIndex: 2
        }
      });
    case "STABILITY_SWEEP":
      return applyProcedure(line, {
        message: "Stability sweep complete.",
        metrics: {
          stabilityPosture: 20,
          timingDrift: 3,
          sourceDebt: 2,
          loadIndex: -2
        }
      });
    case "FLUSH_RESET_PATH":
      return applyProcedure(line, {
        message: "Reset path flush complete.",
        setResetClear: true,
        metrics: {
          resetResidue: -36,
          stabilityPosture: 3,
          loadIndex: -4
        }
      });
    case "ARM_LINE":
      return {
        ...line,
        phase: "armed",
        authorityState: "armed",
        phaseProgress: 0,
        gates: { ...line.gates, lineArmed: true },
        events: addEvent(line.events, makeEvent(line.clock, "command", "authority", "Line armed. Support command available."))
      };
    case "START_SUPPORT":
      return startPhase(line, "supporting", "Support envelope establishment started.");
    case "BEGIN_CARRY":
      return startPhase(line, "carrying", "Packet carry started.");
    case "CATCH_REMATCH":
      return startPhase(line, "catch_window", "Catch/rematch window opened.");
    case "AUTHORIZE_FADE":
      return startPhase(line, "fading", "Release fade authorized after catch confirmation.");
    case "DECOMPRESS":
      return startPhase(line, "decompressing", "Controlled decompression started.");
    case "RESET_LINE":
      return startPhase(line, "resetting", "Reset sequence started.");
    case "SECURE":
      return {
        ...line,
        phase: "secured",
        authorityState: "closed",
        packetState: "secured",
        completedAt: line.clock,
        gates: { ...line.gates, secured: true },
        events: addEvent(line.events, makeEvent(line.clock, "complete", "closeout", "Line secured. Run debrief available."))
      };
    case "HOLD":
      return {
        ...line,
        previousPhase: line.phase,
        phase: "held",
        authorityState: "held",
        events: addEvent(line.events, makeEvent(line.clock, "advisory", "operator", "Line held. Active evolution paused for intervention."))
      };
    case "RESUME":
      return {
        ...line,
        phase: line.previousPhase || "precheck",
        previousPhase: null,
        authorityState: "operator",
        events: addEvent(line.events, makeEvent(line.clock, "command", "operator", "Hold released. Active line evolution resumed."))
      };
    case "ABORT":
      return {
        ...line,
        phase: "aborted",
        authorityState: "recovery",
        packetState: "recovery",
        failure: {
          ...getFailureMode("stability_lockout"),
          id: "operator_abort",
          title: "Operator abort",
          subsystem: "operator",
          summary: "The service pass was stopped by operator authority before closeout.",
          recovery: "Inspect the active trace, complete recovery checks, then reset before another service attempt."
        },
        events: addEvent(line.events, makeEvent(line.clock, "abort", "operator", "Operator abort accepted. Line is in recovery."))
      };
    case "RESET_TRAINER":
      return createInitialLine(line.profileId);
    default:
      return line;
  }
}

export function getOperatorCommands(line) {
  const definitions = [
    ["ACCEPT_MANIFEST", "Accept Manifest", "intake"],
    ["RUN_PRECHECK", "Run Precheck", "readiness"],
    ["PRECHARGE_SUPPORT", "Precharge Support", "readiness"],
    ["CLOSE_LEDGER", "Close Source Ledger", "readiness"],
    ["SYNC_ENDPOINT", "Sync Endpoint", "readiness"],
    ["STABILITY_SWEEP", "Stability Sweep", "readiness"],
    ["FLUSH_RESET_PATH", "Flush Reset Path", "readiness"],
    ["ARM_LINE", "Arm Line", "authority"],
    ["START_SUPPORT", "Start Support", "service"],
    ["BEGIN_CARRY", "Begin Carry", "service"],
    ["CATCH_REMATCH", "Catch / Rematch", "service"],
    ["AUTHORIZE_FADE", "Authorize Fade", "service"],
    ["DECOMPRESS", "Decompress", "service"],
    ["RESET_LINE", "Reset Line", "service"],
    ["SECURE", "Secure", "closeout"],
    ["HOLD", "Hold", "control"],
    ["RESUME", "Release Hold", "control"],
    ["ABORT", "Abort", "control"],
    ["RESET_TRAINER", "Reset Terminal", "control"]
  ];

  return definitions.map(([id, label, group]) => {
    const reason = getInterlockReason(line, id);
    return {
      id,
      label,
      group,
      enabled: !reason,
      reason,
      primary: isPrimaryCommand(line, id),
      danger: id === "ABORT"
    };
  });
}

export function getInterlockReason(line, commandId) {
  if (commandId === "RESET_TRAINER") return null;
  if (line.failure && commandId !== "ABORT") return "recovery state active";
  if (line.phase === "secured") return "line already secured";
  if (line.phase === "aborted") return "line in recovery";

  if (commandId === "ACCEPT_MANIFEST") {
    if (line.gates.manifestAccepted) return "manifest already accepted";
    return null;
  }

  if (!line.gates.manifestAccepted) return "manifest not accepted";

  if (procedureCommands.has(commandId)) {
    if (activePhases.has(line.phase) && !line.awaitingCommand) return "active phase running; hold first";
    if (line.phase === "held" || line.phase === "precheck" || line.phase === "armed" || line.awaitingCommand) return null;
    return "procedure window not open";
  }

  if (commandId === "ARM_LINE") {
    if (line.phase !== "precheck" && line.phase !== "armed") return "readiness precheck not active";
    if (!line.gates.precheckClear) return "precheck not clear";
    if (!line.gates.supportPermit) return "support permit missing";
    if (!line.gates.ledgerClosed) return "source ledger not closed";
    if (!line.gates.endpointSynced) return "endpoint sync missing";
    if (line.metrics.resetResidue > 60 && !line.gates.resetClear) return "reset residue above reuse gate";
    if (line.metrics.stabilityPosture < 52) return "stability posture below arm gate";
    return null;
  }

  if (commandId === "START_SUPPORT") return line.phase === "armed" ? null : "line not armed";
  if (commandId === "BEGIN_CARRY") return phaseReady(line, "supporting", "supportEstablished") ? null : "support not established";
  if (commandId === "CATCH_REMATCH") return phaseReady(line, "carrying", "carryComplete") ? null : "carry not complete";
  if (commandId === "AUTHORIZE_FADE") return phaseReady(line, "catch_window", "catchConfirmed") ? null : "catch not confirmed";
  if (commandId === "DECOMPRESS") return phaseReady(line, "fading", "fadeComplete") ? null : "fade not complete";
  if (commandId === "RESET_LINE") return phaseReady(line, "decompressing", "decompressed") ? null : "decompression not complete";
  if (commandId === "SECURE") {
    if (!phaseReady(line, "resetting", "resetClear")) return "reset clear missing";
    if (line.metrics.resetResidue > 62) return "reset residue above secure gate";
    return null;
  }

  if (commandId === "HOLD") {
    if (!activePhases.has(line.phase) || line.awaitingCommand) return "no active phase to hold";
    return null;
  }
  if (commandId === "RESUME") return line.phase === "held" ? null : "line is not held";
  if (commandId === "ABORT") {
    if (line.phase === "standby" || line.phase === "precheck") return "service not active";
    return null;
  }

  return "command unavailable";
}

export function getTelemetryStatus(def, value) {
  if (def.direction === "low") {
    if (value <= def.red) return "red";
    if (value <= def.caution) return "caution";
    return "nominal";
  }
  if (value >= def.red) return "red";
  if (value >= def.caution) return "caution";
  return "nominal";
}

export function getLineCondition(line) {
  if (line.phase === "aborted") return "red";
  if (line.phase === "secured") return "nominal";
  const statuses = telemetryDefs.map((def) => getTelemetryStatus(def, line.metrics[def.id]));
  if (statuses.includes("red")) return "red";
  if (statuses.includes("caution")) return "caution";
  return "nominal";
}

export function getTerminalAdvisories(line) {
  if (line.failure) {
    return [{
      id: "failure",
      level: "red",
      title: line.failure.title,
      detail: line.failure.recovery
    }];
  }

  const advisories = telemetryDefs
    .map((def) => {
      const status = getTelemetryStatus(def, line.metrics[def.id]);
      if (status === "nominal") return null;
      return {
        id: def.id,
        level: status,
        title: `${def.label} ${status === "red" ? "red" : "caution"}`,
        detail: def.detail
      };
    })
    .filter(Boolean);

  if (line.awaitingCommand) {
    advisories.unshift({
      id: "awaiting",
      level: "nominal",
      title: "Awaiting operator command",
      detail: `${getPhase(line.phase).label} is complete. Next authority is available in the command stack.`
    });
  }

  if (!advisories.length) {
    return [{
      id: "nominal",
      level: "nominal",
      title: "Line nominal",
      detail: "No active telemetry band is outside the nominal trainer gate."
    }];
  }
  return advisories.slice(0, 5);
}

export function getDebrief(line) {
  if (line.phase !== "secured" && line.phase !== "aborted") return null;
  const alarmCount = line.events.filter((event) => event.level === "alarm" || event.level === "abort").length;
  const cautionCount = line.events.filter((event) => event.level === "advisory").length;
  if (line.failure) {
    return {
      outcome: "Recovery Required",
      tone: "red",
      summary: line.failure.summary,
      recovery: line.failure.recovery,
      stats: [
        ["Clock", formatClock(line.clock)],
        ["Alarms", String(alarmCount)],
        ["Cautions", String(cautionCount)]
      ]
    };
  }
  return {
    outcome: "Line Secured",
    tone: alarmCount ? "caution" : "nominal",
    summary: "The manifest closed with service authority secured and no active recovery state.",
    recovery: "Archive the service trace and release the line for the next training assignment.",
    stats: [
      ["Clock", formatClock(line.clock)],
      ["Alarms", String(alarmCount)],
      ["Cautions", String(cautionCount)]
    ]
  };
}

export function formatClock(value) {
  const minutes = Math.floor(value / 60);
  const seconds = value % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function runPrecheck(line) {
  const supportPermit = line.metrics.supportMargin >= 54 && line.metrics.stabilityPosture >= 50;
  const resetClear = line.metrics.resetResidue <= 42 || line.gates.resetClear;
  const events = [
    makeEvent(line.clock, "procedure", "readiness", supportPermit ? "Precheck clear. Support permit available." : "Precheck found support or stability below permit gate.")
  ];
  if (!resetClear) {
    events.push(makeEvent(line.clock, "advisory", "reset", "Reset residue remains above reuse gate. Flush reset path before arming."));
  }
  return {
    ...line,
    authorityState: "readiness",
    gates: {
      ...line.gates,
      precheckClear: supportPermit,
      supportPermit,
      resetClear
    },
    events: addEvents(line.events, events)
  };
}

function applyProcedure(line, patch) {
  const metrics = clampMetrics({ ...line.metrics, ...applyMetricPatch(line.metrics, patch.metrics || {}) });
  const gates = { ...line.gates, ...(patch.gates || {}) };
  if (patch.setResetClear) gates.resetClear = metrics.resetResidue <= 62;
  return {
    ...line,
    metrics,
    gates,
    events: addEvent(line.events, makeEvent(line.clock, "procedure", "readiness", patch.message))
  };
}

function applyMetricPatch(metrics, patch) {
  return Object.fromEntries(
    Object.entries(patch).map(([key, delta]) => [key, (metrics[key] || 0) + delta])
  );
}

function startPhase(line, phase, message) {
  return {
    ...line,
    phase,
    phaseProgress: 0,
    awaitingCommand: false,
    authorityState: "operator",
    packetState: packetStateForPhase(phase),
    events: addEvent(line.events, makeEvent(line.clock, "command", "line", message))
  };
}

function completePhase(line) {
  const gate = phaseCompletionGate[line.phase];
  const gates = { ...line.gates, [gate]: true };
  let packetState = line.packetState;
  if (line.phase === "catch_window") packetState = "rematched";
  if (line.phase === "fading") packetState = "released";
  if (line.phase === "resetting") {
    gates.resetClear = line.metrics.resetResidue <= 62;
    packetState = gates.resetClear ? "secured" : "release_holding";
  }
  const phase = getPhase(line.phase);
  const message = line.phase === "resetting" && !gates.resetClear
    ? "Reset sequence complete, but residue remains above secure gate."
    : `${phase.label} phase complete.`;
  return {
    ...line,
    gates,
    packetState,
    awaitingCommand: true,
    authorityState: "operator",
    events: addEvent(line.events, makeEvent(line.clock, gates.resetClear === false ? "advisory" : "complete", phase.shortLabel, message))
  };
}

function evolveMetrics(metrics, phase, profile) {
  const next = { ...metrics };
  const { load, timing, residue, stability } = profile.stress;

  if (phase === "supporting") {
    next.supportMargin += 1.1;
    next.sourceDebt += 1.15 * load;
    next.loadIndex += 0.9 * load;
    next.timingDrift += 0.18 * timing;
  }
  if (phase === "carrying") {
    next.supportMargin -= 2.5 * load;
    next.sourceDebt += 2.7 * load;
    next.endpointConfidence -= 0.6 * timing;
    next.timingDrift += 1.85 * timing;
    next.stabilityPosture -= 1.15 * stability;
    next.loadIndex += 1.1 * load;
  }
  if (phase === "catch_window") {
    next.endpointConfidence -= 2.15 * timing;
    next.timingDrift += 1.5 * timing;
    next.supportMargin -= 1.05 * load;
    next.sourceDebt += 1.1 * load;
    next.stabilityPosture -= 0.65 * stability;
    next.loadIndex += 0.25 * load;
  }
  if (phase === "fading") {
    next.supportMargin -= 1.45 * load;
    next.sourceDebt += 1.2 * load;
    next.stabilityPosture -= 1.65 * stability;
    next.resetResidue += 1.55 * residue;
    next.loadIndex -= 0.35;
  }
  if (phase === "decompressing") {
    next.supportMargin -= 0.82 * load;
    next.sourceDebt -= 1.55;
    next.stabilityPosture -= 0.85 * stability;
    next.resetResidue += 1.8 * residue;
    next.timingDrift -= 0.65;
    next.loadIndex -= 1.2;
  }
  if (phase === "resetting") {
    next.resetResidue -= profile.id === "reuse" ? 2.45 : 4.4;
    next.endpointConfidence += 0.6;
    next.supportMargin += 0.35;
    next.sourceDebt -= 1.35;
    next.stabilityPosture += 0.55;
    next.timingDrift -= 0.85;
    next.loadIndex -= 1.7;
  }
  return clampMetrics(next);
}

function addTelemetryNotices(line, metrics, clock) {
  let events = line.events;
  const notices = { ...line.notices };
  telemetryDefs.forEach((def) => {
    const status = getTelemetryStatus(def, metrics[def.id]);
    const key = `${def.id}-${status}-${line.phase}`;
    if (status !== "nominal" && !notices[key]) {
      notices[key] = true;
      events = addEvent(events, makeEvent(clock, status === "red" ? "alarm" : "advisory", def.label, `${def.label} entered ${status} band.`));
    }
  });
  return { notices, events };
}

function phaseReady(line, phase, gate) {
  return line.phase === phase && line.awaitingCommand && line.gates[gate];
}

function isPrimaryCommand(line, commandId) {
  if (!line.gates.manifestAccepted) return commandId === "ACCEPT_MANIFEST";
  if (line.phase === "precheck") {
    if (!line.gates.precheckClear) return commandId === "RUN_PRECHECK";
    return commandId === "ARM_LINE";
  }
  if (line.phase === "armed") return commandId === "START_SUPPORT";
  if (line.phase === "supporting" && line.awaitingCommand) return commandId === "BEGIN_CARRY";
  if (line.phase === "carrying" && line.awaitingCommand) return commandId === "CATCH_REMATCH";
  if (line.phase === "catch_window" && line.awaitingCommand) return commandId === "AUTHORIZE_FADE";
  if (line.phase === "fading" && line.awaitingCommand) return commandId === "DECOMPRESS";
  if (line.phase === "decompressing" && line.awaitingCommand) return commandId === "RESET_LINE";
  if (line.phase === "resetting" && line.awaitingCommand) return commandId === "SECURE";
  if (line.phase === "held") return commandId === "RESUME";
  return false;
}

function packetStateForPhase(phase) {
  const states = {
    supporting: "accepted",
    carrying: "in_service",
    catch_window: "handoff_pending",
    fading: "rematched",
    decompressing: "released",
    resetting: "release_holding"
  };
  return states[phase] || "accepted";
}

function commandLabel(commandId) {
  const phaseMatch = Object.entries({
    START_SUPPORT: "supporting",
    BEGIN_CARRY: "carrying",
    CATCH_REMATCH: "catch_window",
    AUTHORIZE_FADE: "fading",
    DECOMPRESS: "decompressing",
    RESET_LINE: "resetting"
  }).find(([id]) => id === commandId);
  if (phaseMatch) return phaseCommandLabel[phaseMatch[1]];
  return commandId.toLowerCase().replaceAll("_", " ");
}

function makeEvent(clock, level, subsystem, message) {
  return {
    id: `${clock}-${level}-${subsystem}-${message}`,
    clock,
    level,
    subsystem,
    message
  };
}

function addEvent(events, event) {
  const keyedEvent = {
    ...event,
    id: `event-${event.clock}-${events.length}-${event.level}-${event.subsystem}`
  };
  return [keyedEvent, ...events].slice(0, 60);
}

function addEvents(events, nextEvents) {
  return nextEvents.reduce((current, event) => addEvent(current, event), events);
}

function clampMetrics(metrics) {
  return Object.fromEntries(
    Object.entries(metrics).map(([key, value]) => [key, clamp(value)])
  );
}

function clamp(value) {
  return Math.max(0, Math.min(100, Math.round(value * 10) / 10));
}

export { phaseDefs, phaseSequence, telemetryDefs };
