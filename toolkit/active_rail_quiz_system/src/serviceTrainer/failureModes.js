export const failureModes = [
  {
    id: "support_gap",
    title: "Support gap lockout",
    subsystem: "support",
    summary: "Support margin fell below the active service floor.",
    recovery: "Abort the pass, precharge support, reduce carrying-flow demand, and restart from a conservative work order."
  },
  {
    id: "source_overdraw",
    title: "Source response overdraw",
    subsystem: "source response",
    summary: "Demanded-source burden outran the qualitative source-response and medium headroom.",
    recovery: "Hold or abort, reduce support and carrying-flow demand, increase regulated medium support, and keep the source ledger as a diagnostic artifact."
  },
  {
    id: "packet_leakage",
    title: "Packet isolation breach",
    subsystem: "packet corridor",
    summary: "Packet leakage exceeded the training floor for protected live-packet carriage.",
    recovery: "Hold or abort, restore the support shell and handoff collar, then review packet-safe margins before another carry attempt."
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
    summary: "Release unloading began while source burden or stability posture was outside the service gate.",
    recovery: "Abort release, stabilize the line, and restore source-response and medium headroom before another decompression attempt."
  },
  {
    id: "reservoir_sag",
    title: "Reservoir headroom collapse",
    subsystem: "reservoir",
    summary: "Support-reservoir headroom fell below the active-service floor.",
    recovery: "Hold the line, unload the medium, reduce support draw, and do not resume until reservoir headroom recovers."
  },
  {
    id: "carrier_guard_lockout",
    title: "Carrier governance lockout",
    subsystem: "carrier",
    summary: "Carrier timing and reachability risk exceeded the rail-time guard.",
    recovery: "Hold or abort, increase rail-time governance and endpoint synchronization, then restart from a lower carrying-flow authority."
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
  if (metrics.packetLeakage > 72 || metrics.packetIsolation < 18) {
    return getFailureMode("packet_leakage");
  }
  if (packetPosition > 70 && metrics.endpointConfidence < 22) {
    return getFailureMode("endpoint_mismatch");
  }
  if (packetPosition > 50 && metrics.timingDrift > 90) {
    return getFailureMode("timing_violation");
  }
  if (metrics.reservoirCharge < 12) {
    return getFailureMode("reservoir_sag");
  }
  if (packetPosition > 44 && metrics.carrierRisk > 92) {
    return getFailureMode("carrier_guard_lockout");
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
