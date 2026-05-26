export const workOrders = [
  {
    id: "inspection",
    workOrderId: "AR-INS-014",
    lineId: "LINE-01",
    callSign: "Inspection Crawl",
    classLabel: "training",
    priority: "low",
    operationNotice: "Low-load inspection pass. Wide catch window authorized.",
    cautions: ["wide catch window", "low plant load", "forgiving reset"],
    serviceWindow: "wide",
    loadClass: "light",
    reuseStatus: "clean",
    seed: 14014,
    causalProfile: {
      horizonRisk: 0.08,
      chronologyRisk: 0
    },
    perturbation: {
      supportSag: 2,
      plantLoad: 2,
      receiverDrift: 2,
      leakage: 1,
      timing: 2,
      reservoir: 1
    },
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
      packetIsolation: 88,
      packetLeakage: 8,
      endpointConfidence: 82,
      timingDrift: 14,
      resetResidue: 16,
      reservoirCharge: 86,
      carrierRisk: 12,
      stabilityPosture: 82,
      loadIndex: 22
    }
  },
  {
    id: "standard",
    workOrderId: "AR-STD-221",
    lineId: "LINE-01",
    callSign: "Standard Packet",
    classLabel: "nominal",
    priority: "ordinary",
    operationNotice: "Nominal packet queued with ordinary readiness burden.",
    cautions: ["standard support draw", "standard catch window", "ordinary reset"],
    serviceWindow: "standard",
    loadClass: "ordinary",
    reuseStatus: "clean",
    seed: 32221,
    causalProfile: {
      horizonRisk: 0.16,
      chronologyRisk: 0
    },
    perturbation: {
      supportSag: 4,
      plantLoad: 4,
      receiverDrift: 4,
      leakage: 3,
      timing: 4,
      reservoir: 3
    },
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
      packetIsolation: 78,
      packetLeakage: 14,
      endpointConfidence: 70,
      timingDrift: 24,
      resetResidue: 24,
      reservoirCharge: 76,
      carrierRisk: 22,
      stabilityPosture: 72,
      loadIndex: 38
    }
  },
  {
    id: "tight",
    workOrderId: "AR-TWH-083",
    lineId: "LINE-01",
    callSign: "Tight-Window Handoff",
    classLabel: "timing",
    priority: "elevated",
    operationNotice: "Receiver timing window is narrow. Catch discipline required.",
    cautions: ["narrow catch window", "drift-sensitive", "receiver sync matters"],
    serviceWindow: "tight",
    loadClass: "ordinary",
    reuseStatus: "clean",
    seed: 83083,
    causalProfile: {
      horizonRisk: 0.34,
      chronologyRisk: 0.08
    },
    perturbation: {
      supportSag: 4,
      plantLoad: 5,
      receiverDrift: 9,
      leakage: 4,
      timing: 10,
      reservoir: 3
    },
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
      packetIsolation: 64,
      packetLeakage: 22,
      endpointConfidence: 54,
      timingDrift: 42,
      resetResidue: 26,
      reservoirCharge: 70,
      carrierRisk: 38,
      stabilityPosture: 68,
      loadIndex: 42
    }
  },
  {
    id: "heavy",
    workOrderId: "AR-HVY-407",
    lineId: "LINE-02",
    callSign: "Heavy Packet",
    classLabel: "load",
    priority: "elevated",
    operationNotice: "Heavy packet staged. Support-plant load expected above nominal.",
    cautions: ["high support draw", "plant load grows quickly", "stability posture is stressed"],
    serviceWindow: "standard",
    loadClass: "heavy",
    reuseStatus: "clean",
    seed: 74407,
    causalProfile: {
      horizonRisk: 0.22,
      chronologyRisk: 0
    },
    perturbation: {
      supportSag: 8,
      plantLoad: 10,
      receiverDrift: 4,
      leakage: 7,
      timing: 5,
      reservoir: 9
    },
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
      packetIsolation: 62,
      packetLeakage: 24,
      endpointConfidence: 68,
      timingDrift: 28,
      resetResidue: 30,
      reservoirCharge: 58,
      carrierRisk: 28,
      stabilityPosture: 60,
      loadIndex: 62
    }
  },
  {
    id: "reuse",
    workOrderId: "AR-RSU-119",
    lineId: "LINE-03",
    callSign: "Post-Reset Reuse",
    classLabel: "reuse",
    priority: "caution",
    operationNotice: "Reuse path carries residual from prior reset.",
    cautions: ["residue starts elevated", "reset gate is strict", "reuse readiness can be blocked"],
    serviceWindow: "standard",
    loadClass: "ordinary",
    reuseStatus: "residual",
    seed: 81119,
    causalProfile: {
      horizonRisk: 0.18,
      chronologyRisk: 0
    },
    perturbation: {
      supportSag: 5,
      plantLoad: 4,
      receiverDrift: 5,
      leakage: 5,
      timing: 5,
      reservoir: 5
    },
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
      packetIsolation: 66,
      packetLeakage: 20,
      endpointConfidence: 64,
      timingDrift: 30,
      resetResidue: 62,
      reservoirCharge: 54,
      carrierRisk: 26,
      stabilityPosture: 62,
      loadIndex: 46
    }
  },
  {
    id: "fault",
    workOrderId: "AR-FLT-503",
    lineId: "LINE-04",
    callSign: "Receiver Degradation Run",
    classLabel: "fault",
    priority: "training",
    operationNotice: "Receiver lock degraded at load. Monitor catch margin.",
    cautions: ["receiver lock low", "timing drift elevated", "abort authority armed"],
    serviceWindow: "tight",
    loadClass: "ordinary",
    reuseStatus: "clean",
    seed: 53503,
    causalProfile: {
      horizonRisk: 0.4,
      chronologyRisk: 0.12
    },
    perturbation: {
      supportSag: 6,
      plantLoad: 7,
      receiverDrift: 16,
      leakage: 7,
      timing: 14,
      reservoir: 5
    },
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
      packetIsolation: 58,
      packetLeakage: 30,
      endpointConfidence: 46,
      timingDrift: 46,
      resetResidue: 34,
      reservoirCharge: 64,
      carrierRisk: 48,
      stabilityPosture: 58,
      loadIndex: 50
    }
  }
];

export const serviceProfiles = workOrders;

export function getWorkOrder(workOrderId) {
  return workOrders.find((order) => order.id === workOrderId) || workOrders[1];
}

export function getServiceProfile(profileId) {
  return getWorkOrder(profileId);
}
