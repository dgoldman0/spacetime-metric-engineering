window.ACTIVE_RAIL_QUESTION_BANK = [
  {
    id: "foundation.adm_lapse.001",
    type: "mc",
    track: "Established foundations",
    module: "ADM split",
    difficulty: "core",
    claim_status: "established_theory",
    content_flags: [],
    prompt: "In ADM language, what does the lapse primarily control?",
    choices: [
      { id: "local_time", text: "The local advance of proper time between spatial slices." },
      { id: "angular_area", text: "The angular area assigned to a spherical section." },
      { id: "source_model", text: "The matter model required to realize a prescribed geometry." },
      { id: "packet_release", text: "The active-rail release handoff order." }
    ],
    answer: ["local_time"],
    explanation: {
      answer: "The lapse controls the local advance of time between slices.",
      why: "In a 3+1 split, lapse and shift separate time advance from spatial coordinate drift.",
      boundary: "This is established ADM terminology, not active-rail-specific vocabulary.",
      references: ["ADM formulation; standard GR texts."]
    }
  },
  {
    id: "active_rail.packet_plant.001",
    type: "mc",
    track: "Active-rail architecture",
    module: "Architecture overview",
    difficulty: "core",
    claim_status: "active_rail_model",
    content_flags: [],
    prompt: "In the active-rail service model, what is the rail?",
    choices: [
      { id: "plant", text: "The operating plant that supplies support, carry, handoff, decompression, and reset functions." },
      { id: "payload", text: "The passenger payload whose timing and release define service requirements." },
      { id: "constraint", text: "An established theorem proving physical realizability." },
      { id: "rset", text: "The renormalized stress tensor of a quantum field." }
    ],
    answer: ["plant"],
    explanation: {
      answer: "The rail is the operating plant.",
      why: "The active-rail architecture separates the serviced packet from the infrastructure that carries and resets the service geometry.",
      boundary: "This is project model language, not established GR terminology.",
      references: []
    }
  },
  {
    id: "literature.alcubierre.001",
    type: "tf",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "core",
    claim_status: "literature_model",
    content_flags: [],
    prompt: "True or false: The Alcubierre warp metric is a published speculative spacetime model, not a demonstrated engineering construction.",
    choices: [
      { id: "true", text: "True" },
      { id: "false", text: "False" }
    ],
    answer: ["true"],
    explanation: {
      answer: "True.",
      why: "The metric is a literature model for exploring relativistic geometry and energy-condition issues.",
      boundary: "Published speculative-relativity context should not be presented as solved engineering.",
      references: ["Alcubierre 1994 and subsequent warp-metric literature."]
    }
  },
  {
    id: "constraints.energy_conditions.001",
    type: "multi",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "intermediate",
    claim_status: "established_constraint",
    content_flags: [],
    prompt: "Which statements are appropriate uses of energy-condition checks in this quiz system?",
    choices: [
      { id: "diagnose", text: "They diagnose constrained stress-energy channels in a proposed geometry." },
      { id: "boundary", text: "They help separate mathematical demand from physical source realization." },
      { id: "prove_build", text: "They prove an active-rail plant can be built if a packet arrives." },
      { id: "ignore", text: "They can be ignored once a service chronology is named." }
    ],
    answer: ["diagnose", "boundary"],
    explanation: {
      answer: "Energy-condition checks diagnose source constraints and help maintain claim boundaries.",
      why: "They are part of established relativistic analysis, but they do not by themselves produce a realizable matter sector.",
      boundary: "This is established constraint material applied to design interpretation.",
      references: ["Standard GR and quantum inequality discussions."]
    }
  },
  {
    id: "source_ledger.dragfill.001",
    type: "drag_fill",
    track: "Active-rail architecture",
    module: "Source ledger",
    difficulty: "core",
    claim_status: "active_rail_model",
    content_flags: [],
    prompt: "For a prescribed metric in units G = c = 1, the demanded-source ledger records {source_term}.",
    tokens: [
      { id: "einstein_over_8pi", text: "G_mn/(8*pi)", render_kind: "math" },
      { id: "shift_over_lapse", text: "beta^ell/alpha", render_kind: "math" },
      { id: "packet_norm", text: "n_pkt", render_kind: "math" },
      { id: "angular_metric", text: "gamma_OmegaOmega", render_kind: "math" }
    ],
    blanks: [
      { id: "source_term", accepts: ["einstein_over_8pi"] }
    ],
    explanation: {
      answer: "The demanded source is G_mn/(8*pi).",
      why: "In these units, Einstein's equation gives G_mn = 8*pi*T_mn.",
      boundary: "The ledger records source demand for a prescribed geometry. It is not a completed physical matter model.",
      references: ["Einstein equation in standard GR."]
    }
  },
  {
    id: "chronology.sequence.001",
    type: "sequence",
    track: "Active-rail architecture",
    module: "Service chronology",
    difficulty: "core",
    claim_status: "active_rail_model",
    content_flags: [],
    prompt: "Put the active-rail service stages in the intended order.",
    items: [
      { id: "support", text: "Support" },
      { id: "carry", text: "Carry" },
      { id: "catch", text: "Catch/rematch" },
      { id: "fade", text: "Fade" },
      { id: "decompress", text: "Decompress" },
      { id: "reset", text: "Reset" }
    ],
    answer: ["support", "carry", "catch", "fade", "decompress", "reset"],
    explanation: {
      answer: "Support -> carry -> catch/rematch -> fade -> decompress -> reset.",
      why: "The packet needs a supported carrying channel, a handoff before shift fade, then a controlled support unwind before reuse.",
      boundary: "This is active-rail service architecture, not established textbook terminology.",
      references: []
    }
  },
  {
    id: "claim_status.matching.001",
    type: "matching",
    track: "Design review and synthesis",
    module: "Claim classification",
    difficulty: "core",
    claim_status: "active_rail_model",
    content_flags: [],
    prompt: "Match each statement to the most appropriate claim status.",
    prompts: [
      { id: "adm", text: "ADM lapse and shift split time advance from spatial drift." },
      { id: "alcubierre", text: "The Alcubierre metric is a published speculative warp model." },
      { id: "rail", text: "The rail is the operating plant and the passenger is the packet." },
      { id: "reset", text: "Reusable rail reset has no source-history accumulation." }
    ],
    options: [
      { id: "established_theory", text: "Established theory" },
      { id: "literature_model", text: "Published speculative model" },
      { id: "active_rail_model", text: "Active-rail model" },
      { id: "open_gate", text: "Open physical gate" }
    ],
    answer: {
      adm: "established_theory",
      alcubierre: "literature_model",
      rail: "active_rail_model",
      reset: "open_gate"
    },
    explanation: {
      answer: "ADM is established theory, Alcubierre is literature context, packet/rail is active-rail model language, and reset accumulation is an open gate.",
      why: "The quiz should train the category boundary as much as the content itself.",
      boundary: "This item intentionally mixes statuses to test epistemic classification.",
      references: ["ADM formulation; Alcubierre 1994; active-rail design documents."]
    }
  },
  {
    id: "design_review.burden.001",
    type: "multi",
    track: "Design review and synthesis",
    module: "Failure analysis",
    difficulty: "advanced",
    claim_status: "active_rail_model",
    content_flags: [],
    prompt: "A service case has clean packet arrival, but the plant report omits support-edge burden, angular pressure, and reset residue. Which review comments are appropriate?",
    choices: [
      { id: "arrival_not_enough", text: "Final packet arrival is not enough to qualify the service." },
      { id: "need_channels", text: "The missing plant channels should be reviewed before acceptance." },
      { id: "ignore_reset", text: "Reset residue can be ignored after one successful arrival." },
      { id: "source_done", text: "A clean packet trace proves source closure." }
    ],
    answer: ["arrival_not_enough", "need_channels"],
    explanation: {
      answer: "Arrival is not enough; missing plant channels matter.",
      why: "Active-rail qualification separates packet-facing success from plant burden and reuse evidence.",
      boundary: "This is active-rail design-review logic, not a general theorem of GR.",
      references: []
    }
  },
  {
    id: "project_state.flagged.001",
    type: "mc",
    track: "Design review and synthesis",
    module: "Project-state handling",
    difficulty: "core",
    claim_status: "project_hypothesis",
    content_flags: ["project_material", "project_state", "revision_sensitive"],
    prompt: "A question based on a current internal run ledger should be treated how in the quiz system?",
    choices: [
      { id: "flagged", text: "Clearly flagged and excludable from stable/general quizzes." },
      { id: "general", text: "Mixed into the general curriculum without any special label." },
      { id: "established", text: "Marked as established theory because it came from a project artifact." },
      { id: "hidden", text: "Hidden from scoring reports so the fiction feels cleaner." }
    ],
    answer: ["flagged"],
    explanation: {
      answer: "It should be flagged and excludable.",
      why: "Project-state content can be useful, but it is revision-sensitive and should not masquerade as stable curriculum.",
      boundary: "This is a quiz-system governance rule, not physics content.",
      references: []
    }
  }
];
