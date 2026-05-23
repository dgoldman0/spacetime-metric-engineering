const repoDoc = (path) => `https://github.com/dgoldman0/spacetime-metric-engineering/blob/main/${path}`;

export const questionBank = [
  {
    id: "foundation.adm_lapse.001",
    type: "mc",
    track: "Established foundations",
    module: "ADM split",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In ADM language, what does the lapse primarily control?",
    choices: [
      { id: "local_time", content: "The local advance of proper time between spatial slices." },
      { id: "angular_area", content: "The angular area assigned to a spherical section." },
      { id: "source_model", content: "The matter model required to realize a prescribed geometry." },
      { id: "packet_release", content: "The active-rail release handoff order." }
    ],
    answer: ["local_time"],
    explanation: {
      answer: "The lapse controls the local advance of time between slices.",
      why: "In a 3+1 split, lapse and shift separate time advance from spatial coordinate drift.",
      boundary: "This is established ADM terminology, not active-rail-specific vocabulary.",
      references: [
        {
          id: "adm_dynamics_gr",
          kind: "paper",
          label: "ADM, The Dynamics of General Relativity",
          citation: "Arnowitt, Deser, and Misner, in Gravitation: An Introduction to Current Research.",
          url: "https://arxiv.org/abs/gr-qc/0405109",
          supports: "Canonical 3+1 decomposition terminology including lapse and shift."
        }
      ]
    }
  },
  {
    id: "active_rail.packet_plant.001",
    type: "mc",
    track: "Active-rail architecture",
    module: "Architecture overview",
    difficulty: "core",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "In the active-rail service model, what is the rail?",
    choices: [
      { id: "plant", content: "The operating plant that supplies support, carry, handoff, decompression, and reset functions." },
      { id: "payload", content: "The passenger payload whose timing and release define service requirements." },
      { id: "constraint", content: "An established theorem proving physical realizability." },
      { id: "rset", content: "The renormalized stress tensor of a quantum field." }
    ],
    answer: ["plant"],
    explanation: {
      answer: "The rail is the operating plant.",
      why: "The active-rail architecture separates the serviced packet from the infrastructure that carries and resets the service geometry.",
      boundary: "This is project model language, not established GR terminology.",
      references: [],
      sourceLinks: [
        {
          label: "Project work analysis",
          kind: "project_doc",
          path: "PROJECT_WORK_ANALYSIS.md",
          url: repoDoc("PROJECT_WORK_ANALYSIS.md"),
          supports: "Current project-level distinction between packet-facing success, plant burden, and physical-source realization."
        }
      ]
    }
  },
  {
    id: "literature.alcubierre.001",
    type: "tf",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "core",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "True or false: The Alcubierre warp metric is a published speculative spacetime model, not a demonstrated engineering construction.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["true"],
    explanation: {
      answer: "True.",
      why: "The metric is a literature model for exploring relativistic geometry and energy-condition issues.",
      boundary: "Published speculative-relativity context should not be presented as solved engineering.",
      references: [
        {
          id: "alcubierre_warp_drive",
          kind: "paper",
          label: "The warp drive: hyper-fast travel within general relativity",
          citation: "Miguel Alcubierre, Classical and Quantum Gravity 11, L73-L77 (1994).",
          url: "https://arxiv.org/abs/gr-qc/0009013",
          supports: "Published speculative warp metric context."
        }
      ]
    }
  },
  {
    id: "constraints.energy_conditions.001",
    type: "multi",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements are appropriate uses of energy-condition checks in relativistic design analysis?",
    choices: [
      { id: "diagnose", content: "They diagnose constrained stress-energy channels in a proposed geometry." },
      { id: "boundary", content: "They help separate mathematical demand from physical source realization." },
      { id: "prove_build", content: "They prove an active-rail plant can be built if a packet arrives." },
      { id: "ignore", content: "They can be ignored once a service chronology is named." }
    ],
    answer: ["diagnose", "boundary"],
    explanation: {
      answer: "Energy-condition checks diagnose source constraints and help maintain claim boundaries.",
      why: "They are part of established relativistic analysis, but they do not by themselves produce a realizable matter sector.",
      boundary: "This is established constraint material applied to design interpretation.",
      references: [
        {
          id: "ford_roman_qi_wormholes",
          kind: "paper",
          label: "Quantum Field Theory Constrains Traversable Wormhole Geometries",
          citation: "L. H. Ford and Thomas A. Roman, Physical Review D 53, 5496 (1996).",
          url: "https://arxiv.org/abs/gr-qc/9510071",
          supports: "Example of quantum-field constraints on exotic spacetime geometries."
        }
      ]
    }
  },
  {
    id: "source_ledger.dragfill.001",
    type: "drag_fill",
    track: "Active-rail architecture",
    module: "Source ledger",
    difficulty: "core",
    claimStatus: "active_rail_model",
    contentFlags: [],
    promptParts: [
      "For a prescribed metric in units ",
      { type: "math", latex: "G=c=1", label: "G equals c equals 1" },
      ", the demanded-source ledger records ",
      { type: "blank", id: "source_term" },
      "."
    ],
    tokens: [
      { id: "einstein_over_8pi", content: [{ type: "math", latex: "G_{\\mu\\nu}/(8\\pi)", label: "Einstein tensor over eight pi" }] },
      { id: "shift_over_lapse", content: [{ type: "math", latex: "\\beta^{\\ell}/\\alpha", label: "beta ell over alpha" }] },
      { id: "packet_norm", content: [{ type: "math", latex: "n_{\\mathrm{pkt}}", label: "packet norm" }] },
      { id: "angular_metric", content: [{ type: "math", latex: "\\gamma_{\\Omega\\Omega}", label: "gamma omega omega" }] }
    ],
    blanks: [
      { id: "source_term", accepts: ["einstein_over_8pi"] }
    ],
    explanation: {
      answer: [{ type: "math", latex: "G_{\\mu\\nu}/(8\\pi)", label: "Einstein tensor over eight pi" }],
      why: ["In these units, Einstein's equation gives ", { type: "math", latex: "G_{\\mu\\nu}=8\\pi T_{\\mu\\nu}", label: "Einstein equation" }, "."],
      boundary: "The ledger records source demand for a prescribed geometry. It is not a completed physical matter model.",
      references: [
        {
          id: "einstein_equation_standard_gr",
          kind: "textbook",
          label: "Einstein equation in standard GR",
          citation: "Standard general relativity texts.",
          supports: "Relation between curvature and stress-energy in units where G=c=1."
        }
      ],
      sourceLinks: [
        {
          label: "Component source ledger promoted pair",
          kind: "project_doc",
          path: "supporting_reports/STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md",
          url: repoDoc("supporting_reports/STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md"),
          supports: "Project source-ledger terminology and demanded-source accounting."
        }
      ],
      openGate: "A demanded-source ledger does not by itself construct a physical matter model."
    }
  },
  {
    id: "chronology.sequence.001",
    type: "sequence",
    track: "Active-rail architecture",
    module: "Service chronology",
    difficulty: "core",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "Put the active-rail service stages in the intended order.",
    items: [
      { id: "support", content: "Support" },
      { id: "carry", content: "Carry" },
      { id: "catch", content: "Catch/rematch" },
      { id: "fade", content: "Fade" },
      { id: "decompress", content: "Decompress" },
      { id: "reset", content: "Reset" }
    ],
    answer: ["support", "carry", "catch", "fade", "decompress", "reset"],
    explanation: {
      answer: "Support, carry, catch/rematch, fade, decompress, reset.",
      why: "The packet needs a supported carrying channel, a handoff before shift fade, then a controlled support unwind before reuse.",
      boundary: "This is active-rail service architecture, not established textbook terminology.",
      references: [],
      sourceLinks: [
        {
          label: "Service aligned schedule",
          kind: "project_doc",
          path: "supporting_reports/STAGE2_BETA075_SERVICE_ALIGNED_SCHEDULE.md",
          url: repoDoc("supporting_reports/STAGE2_BETA075_SERVICE_ALIGNED_SCHEDULE.md"),
          supports: "Project service-order and timing language."
        },
        {
          label: "Endpoint reset release ladder",
          kind: "project_doc",
          path: "supporting_reports/STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md",
          url: repoDoc("supporting_reports/STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md"),
          supports: "Reset and release sequencing context."
        }
      ]
    }
  },
  {
    id: "claim_status.classification.001",
    type: "claim_classification",
    track: "Design review and synthesis",
    module: "Claim classification",
    difficulty: "core",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "Classify each statement by claim status.",
    statuses: ["established_theory", "literature_model", "active_rail_model", "open_gate"],
    statements: [
      { id: "adm", content: "ADM lapse and shift split time advance from spatial drift.", answer: "established_theory" },
      { id: "alcubierre", content: "The Alcubierre metric is a published speculative warp model.", answer: "literature_model" },
      { id: "rail", content: "The rail is the operating plant and the passenger is the packet.", answer: "active_rail_model" },
      { id: "reset", content: "Reusable rail reset has no source-history accumulation.", answer: "open_gate" }
    ],
    explanation: {
      answer: "ADM is established theory, Alcubierre is literature context, packet/rail is active-rail model language, and reset accumulation is an open gate.",
      why: "The statements mix textbook theory, published speculative geometry, project terminology, and unresolved project evidence.",
      boundary: "This item intentionally mixes statuses to test epistemic classification.",
      references: [
        {
          id: "adm_dynamics_gr",
          kind: "paper",
          label: "ADM, The Dynamics of General Relativity",
          citation: "Arnowitt, Deser, and Misner, in Gravitation: An Introduction to Current Research.",
          url: "https://arxiv.org/abs/gr-qc/0405109",
          supports: "Established ADM lapse and shift terminology."
        },
        {
          id: "alcubierre_warp_drive",
          kind: "paper",
          label: "The warp drive: hyper-fast travel within general relativity",
          citation: "Miguel Alcubierre, Classical and Quantum Gravity 11, L73-L77 (1994).",
          url: "https://arxiv.org/abs/gr-qc/0009013",
          supports: "Published speculative warp metric status."
        }
      ],
      sourceLinks: [
        {
          label: "Project work analysis",
          kind: "project_doc",
          path: "PROJECT_WORK_ANALYSIS.md",
          url: repoDoc("PROJECT_WORK_ANALYSIS.md"),
          supports: "Current project-state framing and unresolved evidence boundaries."
        }
      ]
    }
  },
  {
    id: "symbols.matching.001",
    type: "matching",
    track: "Established foundations",
    module: "Symbol roles",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Match each symbol to its role.",
    prompts: [
      { id: "alpha", content: [{ type: "math", latex: "\\alpha", label: "alpha" }] },
      { id: "beta", content: [{ type: "math", latex: "\\beta^{\\ell}", label: "beta ell" }] },
      { id: "gamma", content: [{ type: "math", latex: "\\gamma_{\\Omega\\Omega}", label: "gamma omega omega" }] }
    ],
    options: [
      { id: "lapse", label: "Lapse" },
      { id: "radial_shift", label: "Radial shift" },
      { id: "angular_sector", label: "Angular sector" }
    ],
    answer: {
      alpha: "lapse",
      beta: "radial_shift",
      gamma: "angular_sector"
    },
    explanation: {
      answer: "Alpha is lapse, beta-ell is radial shift, and gamma-Omega-Omega is the angular sector.",
      why: "These symbols map to different operational roles in the local 3+1-style split used by the design model.",
      boundary: "The ADM lapse/shift terms are established; the active-rail interpretation of the angular sector is project model language.",
      references: [
        {
          id: "adm_dynamics_gr",
          kind: "paper",
          label: "ADM, The Dynamics of General Relativity",
          citation: "Arnowitt, Deser, and Misner, in Gravitation: An Introduction to Current Research.",
          url: "https://arxiv.org/abs/gr-qc/0405109",
          supports: "Established lapse and shift roles."
        }
      ],
      sourceLinks: [
        {
          label: "Project work analysis",
          kind: "project_doc",
          path: "PROJECT_WORK_ANALYSIS.md",
          url: repoDoc("PROJECT_WORK_ANALYSIS.md"),
          supports: "Project-level use of reduced metric and ADM translation language."
        }
      ]
    }
  },
  {
    id: "design_review.burden.001",
    type: "multi",
    track: "Design review and synthesis",
    module: "Failure analysis",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A service case has clean packet arrival, but the plant report omits support-edge burden, angular pressure, and reset residue. Which review comments are appropriate?",
    choices: [
      { id: "arrival_not_enough", content: "Final packet arrival is not enough to qualify the service." },
      { id: "need_channels", content: "The missing plant channels should be reviewed before acceptance." },
      { id: "ignore_reset", content: "Reset residue can be ignored after one successful arrival." },
      { id: "source_done", content: "A clean packet trace proves source closure." }
    ],
    answer: ["arrival_not_enough", "need_channels"],
    explanation: {
      answer: "Arrival is not enough; missing plant channels matter.",
      why: "Active-rail qualification separates packet-facing success from plant burden and reuse evidence.",
      boundary: "This is active-rail design-review logic, not a general theorem of GR.",
      references: [],
      sourceLinks: [
        {
          label: "Project work analysis",
          kind: "project_doc",
          path: "PROJECT_WORK_ANALYSIS.md",
          url: repoDoc("PROJECT_WORK_ANALYSIS.md"),
          supports: "Current project distinction between packet safety, plant burden, and source realization."
        },
        {
          label: "Source family validation",
          kind: "project_doc",
          path: "supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_VALIDATION.md",
          url: repoDoc("supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_VALIDATION.md"),
          supports: "Example of project-state source-family validation and remaining watch items."
        }
      ]
    }
  },
  {
    id: "project_state.internal_ledger.001",
    type: "mc",
    track: "Design review and synthesis",
    module: "Project-state handling",
    difficulty: "core",
    claimStatus: "project_hypothesis",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    prompt: "An internal active-rail run ledger reports a candidate pass with clean packet safety but a thin support-closure margin. What is the safest status for that claim?",
    choices: [
      { id: "flagged", content: "Revision-sensitive project-state evidence that can guide review but should not be treated as established physics." },
      { id: "general", content: "A general result that can be applied to any active-rail geometry without qualification." },
      { id: "established", content: "An established theorem of general relativity because the ledger was computed from a metric." },
      { id: "complete", content: "A completed physical-source construction because packet safety was clean." }
    ],
    answer: ["flagged"],
    explanation: {
      answer: "It is revision-sensitive project-state evidence.",
      why: "A clean packet-safety result can be meaningful while support closure, source realization, or repeated-operation margins remain under review.",
      boundary: "This is project-state interpretation, not an established physical theorem.",
      references: [],
      sourceLinks: [
        {
          label: "Project work analysis",
          kind: "project_doc",
          path: "PROJECT_WORK_ANALYSIS.md",
          url: repoDoc("PROJECT_WORK_ANALYSIS.md"),
          supports: "Current project distinction between supported claims, watch items, and overclaims."
        },
        {
          label: "Source family validation",
          kind: "project_doc",
          path: "supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_VALIDATION.md",
          url: repoDoc("supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_VALIDATION.md"),
          supports: "Example of a passing project-state validation with explicit watch conditions."
        }
      ],
      openGate: "Passing a fixed-background or ledger-level screen does not prove matter-action closure, semiclassical consistency, or broad repeated-service viability."
    }
  }
];
