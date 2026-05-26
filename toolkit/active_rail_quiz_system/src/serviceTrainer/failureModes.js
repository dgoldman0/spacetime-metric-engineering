export const failureModes = [
  {
    id: "support_gap",
    title: "Support gap lockout",
    subsystem: "support",
    summary: "Support margin fell below the active service floor.",
    recovery: "Abort the pass, precharge support, close the ledger, and restart from a conservative manifest."
  },
  {
    id: "source_overdraw",
    title: "Source debt overdraw",
    subsystem: "source ledger",
    summary: "Demanded-source burden outran the closed source ledger.",
    recovery: "Hold or abort, close the ledger, and do not treat the demanded source as a physical source solution."
  },
  {
    id: "endpoint_mismatch",
    title: "Endpoint mismatch",
    subsystem: "endpoint",
    summary: "Endpoint confidence collapsed inside the catch window.",
    recovery: "Abort into endpoint recovery, synchronize the endpoint, and do not authorize fade until catch is restored."
  },
  {
    id: "timing_violation",
    title: "Timing window violation",
    subsystem: "timing",
    summary: "Service-window drift exceeded catch/rematch tolerance.",
    recovery: "Hold the line, rerun endpoint synchronization, and restart the pass with wider timing margin."
  },
  {
    id: "decompression_shock",
    title: "Decompression shock",
    subsystem: "release",
    summary: "Release unloading began while source debt or stability posture was outside the trainer gate.",
    recovery: "Abort release, stabilize the line, and close the ledger before another decompression attempt."
  },
  {
    id: "reset_contamination",
    title: "Reset contamination",
    subsystem: "reset",
    summary: "Residue remained above reuse threshold during reset.",
    recovery: "Secure the line as blocked for reuse, flush the reset path, and rerun reset clearance."
  },
  {
    id: "stability_lockout",
    title: "Stability review lockout",
    subsystem: "stability",
    summary: "Stability posture fell below the active trainer floor.",
    recovery: "Stop service and complete coupled-channel review before issuing new service authority."
  }
];

export function getFailureMode(id) {
  return failureModes.find((mode) => mode.id === id);
}

export function evaluateFailure(line) {
  const { metrics, phase } = line;
  const activePhases = ["supporting", "carrying", "catch_window", "fading", "decompressing", "resetting"];
  if (!activePhases.includes(phase) || line.awaitingCommand) return null;

  if (["supporting", "carrying", "fading"].includes(phase) && metrics.supportMargin < 22) {
    return getFailureMode("support_gap");
  }
  if (["supporting", "carrying", "catch_window", "fading"].includes(phase) && metrics.sourceDebt > 88) {
    return getFailureMode("source_overdraw");
  }
  if (phase === "catch_window" && metrics.endpointConfidence < 24) {
    return getFailureMode("endpoint_mismatch");
  }
  if (["carrying", "catch_window"].includes(phase) && metrics.timingDrift > 84) {
    return getFailureMode("timing_violation");
  }
  if (phase === "decompressing" && (metrics.sourceDebt > 82 || metrics.stabilityPosture < 30)) {
    return getFailureMode("decompression_shock");
  }
  if (phase === "resetting" && metrics.resetResidue > 88) {
    return getFailureMode("reset_contamination");
  }
  if (metrics.stabilityPosture < 20) {
    return getFailureMode("stability_lockout");
  }
  return null;
}
