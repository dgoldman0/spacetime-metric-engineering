import { getFailureMode, evaluateFailure } from "./failureModes.js";
import { getWorkOrder } from "./serviceProfiles.js";

export const telemetryDefs = [
  {
    id: "supportMargin",
    label: "Support Margin",
    direction: "low",
    caution: 54,
    red: 26,
    unit: "%",
    detail: "Available corridor support above the service floor."
  },
  {
    id: "sourceDebt",
    label: "Source Debt",
    direction: "high",
    caution: 58,
    red: 84,
    unit: "%",
    detail: "Unresolved demanded-source burden accumulated by the run."
  },
  {
    id: "endpointConfidence",
    label: "Endpoint Confidence",
    direction: "low",
    caution: 54,
    red: 26,
    unit: "%",
    detail: "Catch/rematch readiness at the receiving endpoint."
  },
  {
    id: "timingDrift",
    label: "Timing Drift",
    direction: "high",
    caution: 54,
    red: 82,
    unit: "%",
    detail: "Service-window drift relative to the active handoff."
  },
  {
    id: "resetResidue",
    label: "Reset Residue",
    direction: "high",
    caution: 56,
    red: 84,
    unit: "%",
    detail: "Residual line load that can contaminate reuse readiness."
  },
  {
    id: "stabilityPosture",
    label: "Stability Posture",
    direction: "low",
    caution: 52,
    red: 24,
    unit: "%",
    detail: "Qualitative perturbation and backreaction posture."
  },
  {
    id: "loadIndex",
    label: "Load Index",
    direction: "high",
    caution: 64,
    red: 88,
    unit: "%",
    detail: "Current operational burden on the line."
  }
];

export const controlDefs = [
  {
    id: "supportDrive",
    label: "Support Drive",
    shortLabel: "SUP",
    role: "Envelope",
    minLabel: "idle",
    maxLabel: "field",
    detail: "Raises the corridor support envelope; too much drive increases source and load burden."
  },
  {
    id: "ledgerClosure",
    label: "Ledger Closure",
    shortLabel: "SRC",
    role: "Source",
    minLabel: "open",
    maxLabel: "closed",
    detail: "Closes demanded-source accounting and reduces debt during service."
  },
  {
    id: "endpointSync",
    label: "Endpoint Sync",
    shortLabel: "SYN",
    role: "Endpoint",
    minLabel: "loose",
    maxLabel: "locked",
    detail: "Improves endpoint confidence and suppresses timing drift."
  },
  {
    id: "catchAperture",
    label: "Catch Aperture",
    shortLabel: "CTH",
    role: "Handoff",
    minLabel: "narrow",
    maxLabel: "wide",
    detail: "Opens the receiving aperture. It matters most once the packet enters the catch region."
  },
  {
    id: "carrierDrive",
    label: "Carrier Drive",
    shortLabel: "CAR",
    role: "Motion",
    minLabel: "hold",
    maxLabel: "carry",
    detail: "Moves the packet through the supported corridor when the line is armed."
  },
  {
    id: "releaseFade",
    label: "Release Fade",
    shortLabel: "FDE",
    role: "Release",
    minLabel: "latched",
    maxLabel: "fade",
    detail: "Withdraws the active carrier after catch/rematch has enough margin."
  },
  {
    id: "decompression",
    label: "Decompression",
    shortLabel: "DCP",
    role: "Unload",
    minLabel: "loaded",
    maxLabel: "unload",
    detail: "Unloads support and source channels after release is underway."
  },
  {
    id: "resetPurge",
    label: "Reset Purge",
    shortLabel: "RST",
    role: "Reuse",
    minLabel: "dirty",
    maxLabel: "clear",
    detail: "Clears residue and prepares the line for secure closeout."
  }
];

const defaultControls = {
  supportDrive: 28,
  ledgerClosure: 18,
  endpointSync: 25,
  catchAperture: 28,
  carrierDrive: 0,
  releaseFade: 0,
  decompression: 0,
  resetPurge: 0
};

const phaseBands = [
  { id: "standby", label: "Standby", range: [0, 4] },
  { id: "support", label: "Support", range: [4, 18] },
  { id: "carry", label: "Carry", range: [18, 70] },
  { id: "catch", label: "Catch", range: [70, 84] },
  { id: "release", label: "Release", range: [84, 94] },
  { id: "reset", label: "Reset", range: [94, 100] }
];

export function createInitialLine(profileId = "standard") {
  const workOrder = getWorkOrder(profileId);
  return {
    profileId: workOrder.id,
    workOrderId: workOrder.workOrderId,
    lineId: workOrder.lineId,
    clock: 0,
    runState: "standby",
    packetState: "staged",
    packetPosition: 0,
    packetVelocity: 0,
    authorityState: "work order",
    controls: { ...defaultControls },
    metrics: { ...workOrder.metrics },
    metricTrends: seedMetricTrends(workOrder.metrics),
    notices: {},
    events: [
      makeEvent(0, "system", "work order", `${workOrder.workOrderId} loaded for ${workOrder.callSign}.`)
    ],
    failure: null,
    completedAt: null
  };
}

export function updateLineControl(line, controlId, rawValue) {
  if (!Object.hasOwn(line.controls, controlId) || terminalClosed(line)) return line;
  const value = clamp(Number(rawValue));
  const controls = guardControls(line, { ...line.controls, [controlId]: value });
  return {
    ...line,
    controls,
    events: maybeAddControlEvent(line, controlId, value)
  };
}

export function applyLineAction(line, actionId) {
  if (actionId === "reset") return createInitialLine(line.profileId);

  if (actionId === "accept") {
    if (line.runState !== "standby") return line;
    return {
      ...line,
      runState: "readying",
      packetState: "accepted",
      authorityState: "operator",
      events: addEvent(line.events, makeEvent(line.clock, "operator", "intake", "Work order accepted. Line controls released to operator station."))
    };
  }

  if (actionId === "arm") {
    const constraints = getLineConstraints(line);
    if (line.runState !== "readying" || constraints.some((item) => item.blocksArm)) {
      return addOperatorNotice(line, "arm", "Arm guard held; readiness margins are not closed.");
    }
    return {
      ...line,
      runState: "armed",
      packetState: "accepted",
      authorityState: "armed",
      events: addEvent(line.events, makeEvent(line.clock, "operator", "authority", "Line armed. Carrier drive may move packet through the rail."))
    };
  }

  if (actionId === "hold") {
    if (!["readying", "armed", "service"].includes(line.runState)) return line;
    return {
      ...line,
      runState: "held",
      packetVelocity: 0,
      authorityState: "held",
      events: addEvent(line.events, makeEvent(line.clock, "operator", "authority", "Hold engaged. Packet motion and active evolution paused."))
    };
  }

  if (actionId === "releaseHold") {
    if (line.runState !== "held") return line;
    return {
      ...line,
      runState: line.packetPosition > 0 ? "service" : "readying",
      authorityState: "operator",
      events: addEvent(line.events, makeEvent(line.clock, "operator", "authority", "Hold released. Line evolution resumed."))
    };
  }

  if (actionId === "abort") {
    if (["recovery", "secured"].includes(line.runState)) return line;
    return enterRecovery(line, {
      ...getFailureMode("operator_abort"),
      id: "operator_abort",
      title: "Operator abort",
      subsystem: "operator",
      summary: "The operator stopped service before secure closeout.",
      recovery: "Stabilize the line, review the trace, and reset before another work order."
    });
  }

  if (actionId === "secure") {
    const constraints = getLineConstraints(line);
    if (secureBlocked(line, constraints)) {
      return addOperatorNotice(line, "secure", "Secure guard held; closeout margins are not stable.");
    }
    return {
      ...line,
      runState: "secured",
      packetState: "secured",
      packetVelocity: 0,
      completedAt: line.clock,
      authorityState: "secured",
      events: addEvent(line.events, makeEvent(line.clock, "complete", "closeout", "Line secured. Trace archived for debrief."))
    };
  }

  return line;
}

export function tickLine(line) {
  if (terminalClosed(line)) return line;
  const workOrder = getWorkOrder(line.profileId);
  const clock = line.clock + 1;
  const controls = guardControls(line, line.controls);
  const metrics = evolveMetrics(line, controls, workOrder);
  const packet = evolvePacket(line, controls, metrics, workOrder);
  const runState = deriveRunState(line, packet.position, metrics);
  const packetState = derivePacketState(runState, packet.position, controls);
  const metricTrends = updateMetricTrends(line.metricTrends, metrics);
  const withTick = {
    ...line,
    clock,
    controls,
    metrics,
    metricTrends,
    packetPosition: packet.position,
    packetVelocity: packet.velocity,
    runState,
    packetState,
    authorityState: deriveAuthorityState(runState),
    notices: { ...line.notices }
  };
  const failure = evaluateFailure(withTick);
  if (failure) return enterRecovery(withTick, failure);
  return addTelemetryNotices(withTick, metrics, clock);
}

export function getLineCondition(line) {
  if (line.runState === "recovery") return "red";
  if (line.runState === "secured") return "nominal";
  const statuses = telemetryDefs.map((def) => getTelemetryStatus(def, line.metrics[def.id]));
  if (statuses.includes("red")) return "red";
  if (statuses.includes("caution")) return "caution";
  return "nominal";
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

export function getLineConstraints(line) {
  const constraints = [];
  const { metrics, controls } = line;
  if (line.runState === "standby") {
    constraints.push({
      id: "workOrder",
      subsystem: "intake",
      level: "caution",
      title: "Work order staged",
      detail: "Accept the work order before line controls can drive service.",
      blocksArm: true
    });
  }
  if (metrics.supportMargin < 60) {
    constraints.push({
      id: "supportMargin",
      subsystem: "support",
      level: metrics.supportMargin < 35 ? "red" : "caution",
      title: "Support envelope below arm margin",
      detail: "Raise support drive until the corridor envelope is stable enough for armed service.",
      blocksArm: true,
      blocksSecure: true
    });
  }
  if (metrics.sourceDebt > 56) {
    constraints.push({
      id: "sourceDebt",
      subsystem: "source",
      level: metrics.sourceDebt > 78 ? "red" : "caution",
      title: "Source ledger carrying excess debt",
      detail: "Increase ledger closure or reduce carrier drive before source burden outruns the line.",
      blocksArm: metrics.sourceDebt > 66,
      blocksSecure: metrics.sourceDebt > 68
    });
  }
  if (metrics.endpointConfidence < 58) {
    constraints.push({
      id: "endpointConfidence",
      subsystem: "endpoint",
      level: metrics.endpointConfidence < 38 ? "red" : "caution",
      title: "Endpoint catch confidence below service margin",
      detail: "Increase endpoint sync and open the catch aperture before release.",
      blocksArm: metrics.endpointConfidence < 46
    });
  }
  if (metrics.timingDrift > 58) {
    constraints.push({
      id: "timingDrift",
      subsystem: "timing",
      level: metrics.timingDrift > 78 ? "red" : "caution",
      title: "Timing drift approaching catch tolerance",
      detail: "Endpoint sync should pull the handoff window back toward the packet.",
      blocksSecure: metrics.timingDrift > 72
    });
  }
  if (metrics.resetResidue > 56) {
    constraints.push({
      id: "resetResidue",
      subsystem: "reset",
      level: metrics.resetResidue > 78 ? "red" : "caution",
      title: "Reset path carries residue",
      detail: "Use reset purge and decompression before closeout.",
      blocksArm: metrics.resetResidue > 70,
      blocksSecure: true
    });
  }
  if (metrics.stabilityPosture < 52) {
    constraints.push({
      id: "stabilityPosture",
      subsystem: "stability",
      level: metrics.stabilityPosture < 32 ? "red" : "caution",
      title: "Stability posture below operating margin",
      detail: "Reduce load, improve closure, or hold the line before backreaction warning escalates.",
      blocksArm: metrics.stabilityPosture < 44,
      blocksSecure: metrics.stabilityPosture < 46
    });
  }
  if (metrics.loadIndex > 68) {
    constraints.push({
      id: "loadIndex",
      subsystem: "load",
      level: metrics.loadIndex > 88 ? "red" : "caution",
      title: "Line load still elevated",
      detail: "Reduce carrier drive and unload the line before secure closeout.",
      blocksSecure: metrics.loadIndex > 76
    });
  }
  if (controls.releaseFade > 28 && !releaseWindowOpen(line)) {
    constraints.push({
      id: "releaseGuard",
      subsystem: "release",
      level: "caution",
      title: "Release fade guarded",
      detail: "Carrier fade is resisted until packet position, endpoint confidence, and aperture agree."
    });
  }
  if (controls.decompression > 35 && controls.releaseFade < 45) {
    constraints.push({
      id: "decompressionGuard",
      subsystem: "release",
      level: "caution",
      title: "Decompression ahead of release",
      detail: "Unload gently; strong decompression before release increases stability stress."
    });
  }
  return constraints;
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
  const constraints = getLineConstraints(line);
  if (constraints.length) return constraints.slice(0, 4);
  return [{
    id: "nominal",
    level: "nominal",
    title: "Line nominal",
    detail: "No active subsystem is outside the current training margin."
  }];
}

export function getLineVisualState(line) {
  const workOrder = getWorkOrder(line.profileId);
  const constraints = getLineConstraints(line);
  const statusByMetric = Object.fromEntries(
    telemetryDefs.map((def) => [def.id, getTelemetryStatus(def, line.metrics[def.id])])
  );
  const condition = getLineCondition(line);
  const packetPosition = clamp(line.packetPosition);
  const sourceLoad = normalizeHigh(line.metrics.sourceDebt);
  const supportStrength = normalizeLow(line.metrics.supportMargin);
  const endpointAperture = Math.max(normalizeLow(line.metrics.endpointConfidence), line.controls.catchAperture / 100);
  const timingShear = normalizeHigh(line.metrics.timingDrift);
  const resetResidue = normalizeHigh(line.metrics.resetResidue);
  const stabilityField = normalizeLow(line.metrics.stabilityPosture);
  const opticsFocus = clamp01((line.metrics.endpointConfidence + line.controls.catchAperture - line.metrics.timingDrift * 0.55) / 145);
  const backreactionPosture = clamp01((100 - line.metrics.stabilityPosture + line.metrics.sourceDebt * 0.58 + line.metrics.loadIndex * 0.62) / 170);
  const causalRisk = clamp01((
    line.metrics.timingDrift
    + (100 - line.metrics.endpointConfidence) * 0.8
    + Math.max(0, line.packetPosition - 66) * 0.8
    + (workOrder.serviceWindow === "tight" ? 18 : 0)
  ) / 190);
  const horizonRisk = clamp01(causalRisk * (workOrder.causalProfile?.horizonRisk || 0.18));
  const chronologyRisk = clamp01(causalRisk * (workOrder.causalProfile?.chronologyRisk || 0));
  const supportRipple = clamp01((100 - line.metrics.supportMargin + line.metrics.loadIndex * 0.45 + backreactionPosture * 40) / 160);
  const sourceSaturation = clamp01((line.metrics.sourceDebt + line.metrics.loadIndex * 0.42) / 130);
  const residueDensity = clamp01((line.metrics.resetResidue + line.controls.decompression * 0.28 - line.controls.resetPurge * 0.18) / 105);
  const phase = getOperatingPhase(line);
  return {
    condition,
    phase,
    packetPosition,
    packetLabel: line.failure ? "REC" : line.runState === "secured" ? "SEC" : "PKT",
    packetPulse: line.runState === "service" && line.packetVelocity > 0,
    supportStrength,
    sourceLoad,
    endpointAperture,
    timingShear,
    resetResidue,
    stabilityField,
    opticsFocus,
    backreactionPosture,
    causalRisk,
    horizonRisk,
    chronologyRisk,
    supportRipple,
    sourceSaturation,
    residueDensity,
    statusByMetric,
    constraints,
    pins: constraints.map((item) => ({
      id: item.id,
      status: item.level,
      label: item.subsystem,
      position: visualPinPosition(item.id, packetPosition)
    })),
    styleVars: {
      "--packet-position": `${packetPosition}%`,
      "--support-strength": String(supportStrength),
      "--source-load": String(sourceLoad),
      "--endpoint-aperture": String(endpointAperture),
      "--timing-shear": String(timingShear),
      "--reset-residue": String(resetResidue),
      "--stability-field": String(stabilityField),
      "--optics-focus": String(opticsFocus),
      "--backreaction-posture": String(backreactionPosture),
      "--causal-risk": String(causalRisk),
      "--horizon-risk": String(horizonRisk),
      "--chronology-risk": String(chronologyRisk),
      "--support-ripple": String(supportRipple),
      "--source-saturation": String(sourceSaturation),
      "--residue-density": String(residueDensity)
    }
  };
}

export function getOperatingPhase(line) {
  if (line.runState === "standby") return phaseBands[0];
  if (line.runState === "readying" || line.runState === "armed") return phaseBands[1];
  if (line.runState === "held") return { id: "held", label: "Held", range: [line.packetPosition, line.packetPosition] };
  if (line.runState === "recovery") return { id: "recovery", label: "Recovery", range: [line.packetPosition, line.packetPosition] };
  if (line.runState === "secured") return phaseBands[5];
  return phaseBands.find((band) => line.packetPosition >= band.range[0] && line.packetPosition < band.range[1]) || phaseBands[5];
}

export function getControlState(line, controlId) {
  const constraints = getLineConstraints(line);
  const constraint = constraints.find((item) => constraintMatchesControl(item.id, controlId));
  const disabled = terminalClosed(line)
    || line.runState === "standby";
  return {
    disabled,
    level: constraint?.level || "nominal",
    note: constraint?.title || "nominal",
    constrained: Boolean(constraint)
  };
}

export function getActionState(line, actionId) {
  const constraints = getLineConstraints(line);
  if (actionId === "accept") {
    return {
      enabled: line.runState === "standby",
      label: line.runState === "standby" ? "Accept Work Order" : "Work Order Accepted",
      detail: "Release the staged line into operator control."
    };
  }
  if (actionId === "arm") {
    const blocked = line.runState !== "readying" || constraints.some((item) => item.blocksArm);
    return {
      enabled: !blocked,
      label: line.runState === "armed" || line.runState === "service" ? "Line Armed" : "Arm Line",
      detail: blocked ? "Close support, source, endpoint, reset, and stability margins." : "Line is inside readiness margins."
    };
  }
  if (actionId === "hold") {
    return {
      enabled: ["readying", "armed", "service"].includes(line.runState),
      label: "Hold",
      detail: "Freeze line evolution for correction."
    };
  }
  if (actionId === "releaseHold") {
    return {
      enabled: line.runState === "held",
      label: "Release Hold",
      detail: "Return authority to live operation."
    };
  }
  if (actionId === "abort") {
    return {
      enabled: !["standby", "recovery", "secured"].includes(line.runState),
      label: "Abort",
      detail: "Move the line into recovery authority."
    };
  }
  if (actionId === "secure") {
    const blocked = secureBlocked(line, constraints);
    return {
      enabled: !blocked && ["service", "held"].includes(line.runState),
      label: "Secure",
      detail: blocked ? "Closeout requires endpoint handoff, decompression, purge, and stable margins." : "Close the run and archive the trace."
    };
  }
  if (actionId === "reset") {
    return {
      enabled: true,
      label: "Reset Terminal",
      detail: "Reload the current work order."
    };
  }
  return { enabled: false, label: actionId, detail: "" };
}

export function getDebrief(line) {
  if (line.runState !== "secured" && line.runState !== "recovery") return null;
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
    summary: "The work order closed with service authority secured and no active recovery state.",
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

function evolveMetrics(line, controls, workOrder) {
  const next = { ...line.metrics };
  const { load, timing, residue, stability } = workOrder.stress;
  const accepted = line.runState !== "standby";
  const armed = line.runState === "armed" || line.runState === "service";
  const catchZone = line.packetPosition > 66;
  const releaseOpen = releaseWindowOpen({ ...line, controls });

  next.supportMargin += (controls.supportDrive - 44) / 13;
  next.supportMargin -= armed ? (controls.carrierDrive * load) / 56 : 0;
  next.supportMargin -= controls.releaseFade / 92;
  next.supportMargin += controls.decompression / 130;

  next.sourceDebt += accepted ? (controls.supportDrive * load) / 130 : -0.2;
  next.sourceDebt += armed ? (controls.carrierDrive * load) / 42 : 0;
  next.sourceDebt -= controls.ledgerClosure / 24;
  next.sourceDebt -= controls.decompression / 92;
  next.sourceDebt -= controls.resetPurge / 130;

  next.endpointConfidence += (controls.endpointSync - 38) / 13;
  next.endpointConfidence += controls.catchAperture / 90;
  next.endpointConfidence -= armed ? (controls.carrierDrive * timing) / 110 : 0;
  next.endpointConfidence -= catchZone && controls.catchAperture < 42 ? 2.8 * timing : 0;

  next.timingDrift += armed ? (controls.carrierDrive * timing) / 62 : -0.4;
  next.timingDrift -= controls.endpointSync / 34;
  next.timingDrift -= controls.catchAperture / 120;

  next.resetResidue += releaseOpen ? (controls.releaseFade * residue) / 82 : 0;
  next.resetResidue += controls.decompression > 45 ? (controls.decompression * residue) / 210 : 0;
  next.resetResidue -= controls.resetPurge / (workOrder.id === "reuse" ? 20 : 16);

  next.stabilityPosture += controls.ledgerClosure / 90;
  next.stabilityPosture += controls.endpointSync / 160;
  next.stabilityPosture -= armed ? (controls.carrierDrive * stability) / 120 : 0;
  next.stabilityPosture -= controls.releaseFade / 150;
  next.stabilityPosture -= next.sourceDebt > 70 ? 1.2 * stability : 0;
  next.stabilityPosture += line.runState === "held" ? 1.4 : 0;

  next.loadIndex += armed ? (controls.carrierDrive * load) / 42 : -0.45;
  next.loadIndex += controls.supportDrive / 140;
  next.loadIndex -= controls.decompression / 48;
  next.loadIndex -= controls.resetPurge / 95;

  return clampMetrics(next);
}

function evolvePacket(line, controls, metrics, workOrder) {
  if (!["armed", "service"].includes(line.runState)) {
    return { position: line.packetPosition, velocity: 0 };
  }
  const supportFactor = Math.max(0.1, metrics.supportMargin / 100);
  const confidenceFactor = line.packetPosition > 66 ? Math.max(0.2, metrics.endpointConfidence / 100) : 1;
  const drive = controls.carrierDrive / 100;
  const drag = line.packetPosition > 82 && controls.releaseFade < 28 ? 0.32 : 1;
  const velocity = drive * workOrder.pace * 0.085 * supportFactor * confidenceFactor * drag;
  const position = clamp(line.packetPosition + velocity, 0, 100);
  return { position, velocity };
}

function deriveRunState(line, packetPosition) {
  if (line.runState === "held" || line.runState === "recovery" || line.runState === "secured") return line.runState;
  if (line.runState === "standby" || line.runState === "readying") return line.runState;
  if (line.runState === "armed" && (packetPosition > 1 || line.controls.carrierDrive > 8)) return "service";
  return line.runState;
}

function derivePacketState(runState, packetPosition, controls) {
  if (runState === "standby") return "staged";
  if (runState === "readying" || runState === "armed") return "accepted";
  if (runState === "held") return "held";
  if (runState === "recovery") return "recovery";
  if (runState === "secured") return "secured";
  if (packetPosition > 96 && controls.resetPurge > 50) return "secured";
  if (packetPosition > 88 && controls.releaseFade > 40) return "released";
  if (packetPosition > 72) return "handoff pending";
  return "in service";
}

function deriveAuthorityState(runState) {
  const labels = {
    standby: "work order",
    readying: "readiness",
    armed: "armed",
    service: "operator",
    held: "held",
    recovery: "recovery",
    secured: "secured"
  };
  return labels[runState] || "operator";
}

function releaseWindowOpen(line) {
  return line.packetPosition >= 74
    && line.metrics.endpointConfidence >= 52
    && line.controls.catchAperture >= 48
    && line.metrics.timingDrift <= 74;
}

function secureBlocked(line, constraints = getLineConstraints(line)) {
  return constraints.some((item) => item.blocksSecure)
    || line.packetPosition < 92
    || line.controls.releaseFade < 54
    || line.controls.decompression < 42
    || line.controls.resetPurge < 46
    || line.runState === "recovery";
}

function guardControls(line, controls) {
  const guarded = { ...controls };
  if (line.runState === "standby") {
    guarded.carrierDrive = 0;
    guarded.releaseFade = 0;
    guarded.decompression = 0;
    guarded.resetPurge = Math.min(guarded.resetPurge, 28);
  }
  if (!["armed", "service"].includes(line.runState)) {
    guarded.carrierDrive = Math.min(guarded.carrierDrive, 12);
  }
  if (!releaseWindowOpen({ ...line, controls: guarded })) {
    guarded.releaseFade = Math.min(guarded.releaseFade, 34);
  }
  if (guarded.releaseFade < 36) {
    guarded.decompression = Math.min(guarded.decompression, 36);
  }
  if (line.packetPosition < 86) {
    guarded.resetPurge = Math.min(guarded.resetPurge, 40);
  }
  return Object.fromEntries(Object.entries(guarded).map(([key, value]) => [key, clamp(value)]));
}

function terminalClosed(line) {
  return line.runState === "recovery" || line.runState === "secured";
}

function enterRecovery(line, failure) {
  return {
    ...line,
    runState: "recovery",
    packetState: "recovery",
    packetVelocity: 0,
    authorityState: "recovery",
    failure,
    events: addEvent(line.events, makeEvent(line.clock, failure.id === "operator_abort" ? "abort" : "alarm", failure.subsystem, failure.title))
  };
}

function addTelemetryNotices(line, metrics, clock) {
  let events = line.events;
  const notices = { ...line.notices };
  telemetryDefs.forEach((def) => {
    const status = getTelemetryStatus(def, metrics[def.id]);
    const key = `${def.id}-${status}`;
    if (status !== "nominal" && !notices[key]) {
      notices[key] = true;
      events = addEvent(events, makeEvent(clock, status === "red" ? "alarm" : "advisory", def.label, `${def.label} entered ${status} band.`));
    }
  });
  return { ...line, notices, events };
}

function maybeAddControlEvent(line, controlId, value) {
  const control = controlDefs.find((item) => item.id === controlId);
  if (!control) return line.events;
  const previous = line.controls[controlId];
  if (Math.abs(previous - value) < 18) return line.events;
  return addEvent(line.events, makeEvent(line.clock, "operator", control.role, `${control.label} moved ${value > previous ? "up" : "down"}.`));
}

function addOperatorNotice(line, noticeId, message) {
  const key = `operator-${noticeId}-${line.clock}`;
  return {
    ...line,
    events: addEvent(line.events, makeEvent(line.clock, "advisory", "authority", message)),
    notices: { ...line.notices, [key]: true }
  };
}

function constraintMatchesControl(constraintId, controlId) {
  const map = {
    supportMargin: ["supportDrive", "carrierDrive"],
    sourceDebt: ["ledgerClosure", "carrierDrive", "decompression"],
    endpointConfidence: ["endpointSync", "catchAperture"],
    timingDrift: ["endpointSync", "catchAperture", "carrierDrive"],
    resetResidue: ["decompression", "resetPurge"],
    stabilityPosture: ["supportDrive", "ledgerClosure", "carrierDrive"],
    loadIndex: ["carrierDrive", "decompression", "resetPurge"],
    releaseGuard: ["releaseFade"],
    decompressionGuard: ["decompression"]
  };
  return (map[constraintId] || []).includes(controlId);
}

function visualPinPosition(metricId, packetPosition) {
  const positions = {
    supportMargin: Math.max(16, packetPosition - 8),
    sourceDebt: Math.max(22, packetPosition - 14),
    endpointConfidence: 84,
    timingDrift: Math.min(78, packetPosition + 11),
    resetResidue: 78,
    stabilityPosture: 52,
    loadIndex: packetPosition,
    releaseGuard: 82,
    decompressionGuard: 88
  };
  return positions[metricId] || packetPosition;
}

function seedMetricTrends(metrics) {
  return Object.fromEntries(
    Object.entries(metrics).map(([key, value]) => [key, Array(14).fill(clamp(value))])
  );
}

function updateMetricTrends(trends = {}, metrics) {
  return Object.fromEntries(
    Object.entries(metrics).map(([key, value]) => {
      const previous = Array.isArray(trends[key]) ? trends[key] : Array(13).fill(value);
      return [...previous.slice(-13), clamp(value)];
    })
  );
}

function clampMetrics(metrics) {
  return Object.fromEntries(
    Object.entries(metrics).map(([key, value]) => [key, clamp(value)])
  );
}

function normalizeHigh(value) {
  return clamp(value) / 100;
}

function normalizeLow(value) {
  return clamp(value) / 100;
}

function clamp01(value) {
  return Math.max(0, Math.min(1, Math.round(value * 1000) / 1000));
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
  return [keyedEvent, ...events].slice(0, 80);
}

function clamp(value, min = 0, max = 100) {
  return Math.max(min, Math.min(max, Math.round(value * 10) / 10));
}
