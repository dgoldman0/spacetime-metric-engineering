export const phaseDefs = [
  {
    id: "standby",
    label: "Standby",
    shortLabel: "STBY",
    detail: "Manifest loaded; line awaits operator acceptance."
  },
  {
    id: "precheck",
    label: "Precheck",
    shortLabel: "PRE",
    detail: "Readiness gates and service burden are being checked."
  },
  {
    id: "armed",
    label: "Armed",
    shortLabel: "ARM",
    detail: "Line authority is armed and ready for support."
  },
  {
    id: "supporting",
    label: "Support",
    shortLabel: "SUP",
    detail: "Corridor support envelope is being established."
  },
  {
    id: "carrying",
    label: "Carry",
    shortLabel: "CAR",
    detail: "Packet is inside the active service interval."
  },
  {
    id: "catch_window",
    label: "Catch",
    shortLabel: "CTH",
    detail: "Endpoint catch/rematch must be completed before release fade."
  },
  {
    id: "fading",
    label: "Fade",
    shortLabel: "FDE",
    detail: "Carrier is being withdrawn while support remains controlled."
  },
  {
    id: "decompressing",
    label: "Decompress",
    shortLabel: "DCP",
    detail: "Support and source channels are being unloaded."
  },
  {
    id: "resetting",
    label: "Reset",
    shortLabel: "RST",
    detail: "Residue is being cleared before the line is secured."
  },
  {
    id: "secured",
    label: "Secured",
    shortLabel: "SEC",
    detail: "Run is closed and line is available for debrief."
  }
];

export const telemetryDefs = [
  {
    id: "supportMargin",
    label: "Support Margin",
    direction: "low",
    caution: 54,
    red: 26,
    unit: "%",
    detail: "Available corridor support above the trainer floor."
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

export const procedureSteps = [
  {
    id: "manifestAccepted",
    label: "Accept manifest",
    group: "intake"
  },
  {
    id: "precheckClear",
    label: "Precheck clear",
    group: "readiness"
  },
  {
    id: "supportPermit",
    label: "Support permit",
    group: "readiness"
  },
  {
    id: "ledgerClosed",
    label: "Source ledger closed",
    group: "readiness"
  },
  {
    id: "endpointSynced",
    label: "Endpoint synchronized",
    group: "readiness"
  },
  {
    id: "lineArmed",
    label: "Line armed",
    group: "authority"
  },
  {
    id: "supportEstablished",
    label: "Support established",
    group: "service"
  },
  {
    id: "carryComplete",
    label: "Carry complete",
    group: "service"
  },
  {
    id: "catchConfirmed",
    label: "Catch/rematch confirmed",
    group: "service"
  },
  {
    id: "fadeComplete",
    label: "Fade complete",
    group: "release"
  },
  {
    id: "decompressed",
    label: "Decompressed",
    group: "release"
  },
  {
    id: "resetClear",
    label: "Reset clear",
    group: "reset"
  },
  {
    id: "secured",
    label: "Line secured",
    group: "closeout"
  }
];

export const phaseSequence = [
  "supporting",
  "carrying",
  "catch_window",
  "fading",
  "decompressing",
  "resetting"
];

export const phaseCompletionGate = {
  supporting: "supportEstablished",
  carrying: "carryComplete",
  catch_window: "catchConfirmed",
  fading: "fadeComplete",
  decompressing: "decompressed",
  resetting: "resetClear"
};

export const phaseCommandLabel = {
  supporting: "Start Support",
  carrying: "Begin Carry",
  catch_window: "Catch / Rematch",
  fading: "Authorize Fade",
  decompressing: "Decompress",
  resetting: "Reset Line"
};

export function getPhase(phaseId) {
  return phaseDefs.find((phase) => phase.id === phaseId) || phaseDefs[0];
}
