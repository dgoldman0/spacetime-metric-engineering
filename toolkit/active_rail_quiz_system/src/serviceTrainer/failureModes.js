export const failureModes = [
  {
    id: "support_gap",
    title: "Support gap lockout",
    subsystem: "support",
    summary: "Support margin fell below the active service floor.",
    recovery: "Abort the pass, precharge support, close the ledger, and restart from a conservative work order."
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
    summary: "Release unloading began while source debt or stability posture was outside the service gate.",
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
    summary: "Stability posture fell below the active service floor.",
    recovery: "Stop service and complete coupled-channel review before issuing new service authority."
  },
  {
    id: "operator_abort",
    title: "Operator abort",
    subsystem: "operator",
    summary: "The operator stopped service before secure closeout.",
    recovery: "Stabilize the line, review the trace, and reset before another work order."
  }
];

export function getFailureMode(id) {
  return failureModes.find((mode) => mode.id === id);
}

export function evaluateFailure(line) {
  const { metrics, packetPosition, runState, controls } = line;
  if (!["armed", "service"].includes(runState)) return null;

  if (metrics.supportMargin < 18) {
    return getFailureMode("support_gap");
  }
  if (metrics.sourceDebt > 92) {
    return getFailureMode("source_overdraw");
  }
  if (packetPosition > 70 && metrics.endpointConfidence < 22) {
    return getFailureMode("endpoint_mismatch");
  }
  if (packetPosition > 50 && metrics.timingDrift > 90) {
    return getFailureMode("timing_violation");
  }
  if (controls.decompression > 72 && (metrics.sourceDebt > 82 || metrics.stabilityPosture < 30)) {
    return getFailureMode("decompression_shock");
  }
  if (packetPosition > 88 && metrics.resetResidue > 92) {
    return getFailureMode("reset_contamination");
  }
  if (metrics.stabilityPosture < 20) {
    return getFailureMode("stability_lockout");
  }
  return null;
}
