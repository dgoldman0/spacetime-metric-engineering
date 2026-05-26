export const serviceProfiles = [
  {
    id: "inspection",
    manifestId: "AR-INS-014",
    lineId: "LINE-01",
    callSign: "Inspection Crawl",
    classLabel: "training",
    priority: "low",
    objective: "Verify the line with a low-load packet and wide catch tolerance.",
    constraints: ["wide catch window", "low source burden", "forgiving reset"],
    pace: 16,
    stress: {
      load: 0.66,
      timing: 0.72,
      residue: 0.72,
      stability: 0.76
    },
    metrics: {
      supportMargin: 82,
      sourceDebt: 18,
      endpointConfidence: 82,
      timingDrift: 14,
      resetResidue: 16,
      stabilityPosture: 82,
      loadIndex: 22
    }
  },
  {
    id: "standard",
    manifestId: "AR-STD-221",
    lineId: "LINE-01",
    callSign: "Standard Packet",
    classLabel: "nominal",
    priority: "ordinary",
    objective: "Run a normal packet with ordinary readiness burden.",
    constraints: ["standard support draw", "standard catch window", "ordinary reset"],
    pace: 14,
    stress: {
      load: 1,
      timing: 1,
      residue: 1,
      stability: 1
    },
    metrics: {
      supportMargin: 72,
      sourceDebt: 28,
      endpointConfidence: 70,
      timingDrift: 24,
      resetResidue: 24,
      stabilityPosture: 72,
      loadIndex: 38
    }
  },
  {
    id: "tight",
    manifestId: "AR-TWH-083",
    lineId: "LINE-01",
    callSign: "Tight-Window Handoff",
    classLabel: "timing",
    priority: "elevated",
    objective: "Keep endpoint timing disciplined through carry and catch.",
    constraints: ["narrow catch window", "drift-sensitive", "endpoint sync matters"],
    pace: 13,
    stress: {
      load: 0.96,
      timing: 1.55,
      residue: 1,
      stability: 1.08
    },
    metrics: {
      supportMargin: 68,
      sourceDebt: 32,
      endpointConfidence: 54,
      timingDrift: 42,
      resetResidue: 26,
      stabilityPosture: 68,
      loadIndex: 42
    }
  },
  {
    id: "heavy",
    manifestId: "AR-HVY-407",
    lineId: "LINE-02",
    callSign: "Heavy Packet",
    classLabel: "load",
    priority: "elevated",
    objective: "Carry a high-burden packet without exhausting support or source margin.",
    constraints: ["high support draw", "source debt grows quickly", "stability posture is stressed"],
    pace: 12,
    stress: {
      load: 1.48,
      timing: 1.08,
      residue: 1.16,
      stability: 1.34
    },
    metrics: {
      supportMargin: 60,
      sourceDebt: 42,
      endpointConfidence: 68,
      timingDrift: 28,
      resetResidue: 30,
      stabilityPosture: 60,
      loadIndex: 62
    }
  },
  {
    id: "reuse",
    manifestId: "AR-RSU-119",
    lineId: "LINE-03",
    callSign: "Post-Reset Reuse",
    classLabel: "reuse",
    priority: "caution",
    objective: "Prove reset clearance before accepting a new packet on a used line.",
    constraints: ["residue starts elevated", "reset gate is strict", "reuse readiness can be blocked"],
    pace: 13,
    stress: {
      load: 1.02,
      timing: 1.08,
      residue: 1.62,
      stability: 1.12
    },
    metrics: {
      supportMargin: 66,
      sourceDebt: 34,
      endpointConfidence: 64,
      timingDrift: 30,
      resetResidue: 62,
      stabilityPosture: 62,
      loadIndex: 46
    }
  },
  {
    id: "fault",
    manifestId: "AR-FLT-503",
    lineId: "LINE-04",
    callSign: "Fault-Injection Drill",
    classLabel: "fault",
    priority: "drill",
    objective: "Find the degraded subsystem and keep the run inside recovery authority.",
    constraints: ["hidden endpoint degradation", "faster drift", "abort discipline expected"],
    pace: 12,
    stress: {
      load: 1.1,
      timing: 1.42,
      residue: 1.12,
      stability: 1.28
    },
    metrics: {
      supportMargin: 64,
      sourceDebt: 38,
      endpointConfidence: 46,
      timingDrift: 46,
      resetResidue: 34,
      stabilityPosture: 58,
      loadIndex: 50
    }
  }
];

export function getServiceProfile(profileId) {
  return serviceProfiles.find((profile) => profile.id === profileId) || serviceProfiles[1];
}
