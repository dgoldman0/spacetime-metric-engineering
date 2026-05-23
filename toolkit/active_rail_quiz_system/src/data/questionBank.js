const references = {
  adm: {
    id: "adm_dynamics_gr",
    kind: "paper",
    label: "ADM, The Dynamics of General Relativity",
    citation: "Arnowitt, Deser, and Misner, Gravitation: An Introduction to Current Research, chapter 7.",
    url: "https://arxiv.org/abs/gr-qc/0405109",
    supports: "Canonical 3+1 decomposition terminology including lapse, shift, spatial metric, and constraints."
  },
  alcubierre: {
    id: "alcubierre_warp_drive",
    kind: "paper",
    label: "The warp drive: hyper-fast travel within general relativity",
    citation: "Miguel Alcubierre, Classical and Quantum Gravity 11, L73-L77 (1994).",
    url: "https://arxiv.org/abs/gr-qc/0009013",
    supports: "Published speculative warp metric context."
  },
  fordRoman: {
    id: "ford_roman_qi_wormholes",
    kind: "paper",
    label: "Quantum Field Theory Constrains Traversable Wormhole Geometries",
    citation: "L. H. Ford and Thomas A. Roman, Physical Review D 53, 5496-5507 (1996).",
    url: "https://arxiv.org/abs/gr-qc/9510071",
    supports: "Quantum inequality constraints on exotic spacetime geometries."
  },
  clarkHiscockLarson: {
    id: "clark_hiscock_larson_null_geodesics",
    kind: "paper",
    label: "Null Geodesics in the Alcubierre Warp Drive Spacetime",
    citation: "C. Clark, W. A. Hiscock, and S. L. Larson, Classical and Quantum Gravity 16, 3965-3972 (1999).",
    url: "https://arxiv.org/abs/gr-qc/9907019",
    supports: "Null-geodesic access, horizon-like cone structures, and quantum-vacuum cautions for superluminal Alcubierre operation."
  },
  mullerWeiskopf: {
    id: "muller_weiskopf_alcubierre_geodesics",
    kind: "paper",
    label: "Detailed study of null and time-like geodesics in the Alcubierre Warp spacetime",
    citation: "T. Mueller and D. Weiskopf, General Relativity and Gravitation 44, 509-533 (2012).",
    url: "https://arxiv.org/abs/1107.5650",
    supports: "Detailed null and timelike geodesic study for Alcubierre spacetime as an educational model, with physical feasibility caveats."
  },
  everettRoman: {
    id: "everett_roman_krasnikov_tube",
    kind: "paper",
    label: "A Superluminal Subway: The Krasnikov Tube",
    citation: "A. E. Everett and T. A. Roman, Physical Review D 56, 2100-2108 (1997).",
    url: "https://arxiv.org/abs/gr-qc/9702049",
    supports: "Krasnikov-tube chronology, control, and negative-energy lessons for superluminal networks."
  },
  shoshanySnodgrass: {
    id: "shoshany_snodgrass_warp_ctc",
    kind: "paper",
    label: "Warp Drives and Closed Timelike Curves",
    citation: "B. Shoshany and B. Snodgrass, Classical and Quantum Gravity 41, 205005 (2024).",
    url: "https://arxiv.org/abs/2309.10072",
    supports: "Concrete two-warp-drive closed-timelike-geodesic construction and weak-energy-condition violation context."
  },
  garattiniZatrimaylov: {
    id: "garattini_zatrimaylov_wormhole_warp_correspondence",
    kind: "paper",
    label: "On the Wormhole--Warp Drive Correspondence",
    citation: "R. Garattini and K. Zatrimaylov, arXiv:2401.15136.",
    url: "https://arxiv.org/abs/2401.15136",
    supports: "Warp/wormhole correspondence requiring nonzero intrinsic curvature and its traversability caveats."
  },
  barceloVisser: {
    id: "barcelo_visser_scalar_energy_conditions",
    kind: "paper",
    label: "Scalar Fields, Energy Conditions, and Traversable Wormholes",
    citation: "C. Barcelo and M. Visser, Classical and Quantum Gravity 17, 3843-3864 (2000).",
    url: "https://arxiv.org/abs/gr-qc/0003025",
    supports: "Non-minimally coupled scalar-field energy-condition violation, traversable-wormhole branches, and trans-Planckian caveats."
  },
  smearedNec: {
    id: "moghtaderi_hull_quintin_geshnizjani_snec",
    kind: "paper",
    label: "How Much NEC Breaking Can the Universe Endure?",
    citation: "E. Moghtaderi, B. R. Hull, J. Quintin, and G. Geshnizjani, Physical Review D 111, 123552 (2025).",
    url: "https://arxiv.org/abs/2503.19955",
    supports: "Quantum-motivated smeared null energy condition as a semilocal constraint on accumulated NEC violation."
  },
  natario: {
    id: "natario_zero_expansion",
    kind: "paper",
    label: "Warp Drive With Zero Expansion",
    citation: "Jose Natario, Classical and Quantum Gravity 19, 1157-1166 (2002).",
    url: "https://arxiv.org/abs/gr-qc/0110086",
    supports: "Published zero-expansion warp-drive construction."
  },
  topologicalCensorship: {
    id: "topological_censorship",
    kind: "paper",
    label: "Topological Censorship",
    citation: "Friedman, Schleich, and Witt, Physical Review Letters 71, 1486-1489 (1993).",
    url: "https://arxiv.org/abs/gr-qc/9305017",
    supports: "Constraint on visible nontrivial topology under suitable assumptions."
  },
  chronologyProtection: {
    id: "visser_chronology_protection",
    kind: "paper",
    label: "The quantum physics of chronology protection",
    citation: "Matt Visser, arXiv:gr-qc/0204022.",
    url: "https://arxiv.org/abs/gr-qc/0204022",
    supports: "Open-access review context for chronology protection, closed causal curves, and quantum-field backreaction concerns."
  },
  carrollGrNotes: {
    id: "carroll_gr_notes",
    kind: "paper",
    label: "Lecture Notes on General Relativity",
    citation: "Sean M. Carroll, arXiv:gr-qc/9712019.",
    url: "https://arxiv.org/abs/gr-qc/9712019",
    supports: "Open-access general relativity reference for metrics, Einstein's equation, and energy-condition notation."
  }
};

const publicProjectDocBase = "https://github.com/dgoldman0/spacetime-metric-engineering/blob/main/";

const projectSource = (label, publicPath, supports) => ({
  label,
  kind: "project_doc",
  citation: "Public project repository document.",
  url: `${publicProjectDocBase}${publicPath}`,
  supports
});

const sources = {
  technicalDisclosure: projectSource(
    "Active-rail technical disclosure",
    "active_rail_technical_disclosure.tex",
    "Current primary project disclosure for active-rail architecture, service components, source placement, and claim scope."
  ),
  projectReadme: projectSource(
    "Repository status README",
    "README.md",
    "Current bounded project status and explicit non-claims."
  ),
  cliSourceParams: projectSource(
    "ADM harness SourceParams reference",
    "toolkit/adm_harness_cli/README.md",
    "Durable software reference for alpha, beta, gamma_ll, gamma_omega, packet, support, release, and reset controls."
  ),
  entryServiceGate: projectSource(
    "Stage II entry service gate memo",
    "supporting_reports/STAGE2_ENTRY_SERVICE_GATE_MEMO.md",
    "Service-boundary evidence separating setup support from live packet accounting."
  ),
  componentSourceLedger: projectSource(
    "Component source ledger promoted pair",
    "supporting_reports/STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md",
    "Project demanded-source ledger terminology and component source accounting."
  ),
  serviceAlignedSchedule: projectSource(
    "Service aligned schedule",
    "supporting_reports/STAGE2_BETA075_SERVICE_ALIGNED_SCHEDULE.md",
    "Project service-order and timing context."
  ),
  resetReleaseLadder: projectSource(
    "Endpoint reset release ladder",
    "supporting_reports/STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md",
    "Reset and release sequencing context."
  ),
  sourceFamilyValidation: projectSource(
    "Source family validation",
    "supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_VALIDATION.md",
    "Fixed-background source-family validation status and watch conditions."
  ),
  boundedSealReadiness: projectSource(
    "Bounded seal readiness",
    "supporting_reports/STAGE2_BETA075_BOUNDED_SEAL_READINESS.md",
    "Sealed V5 prescribed-metric/effective-source scope with explicit non-claims and watch obligations."
  ),
  serviceRatingLadder: projectSource(
    "Service rating ladder diagnostic",
    "supporting_reports/STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md",
    "Current V2.5 and V10 service-rating diagnostic interpretation."
  ),
  endpointSourceFamilyRung: projectSource(
    "Endpoint J source family rung",
    "supporting_reports/STAGE2_BETA075_ENDPOINT_J_SOURCE_FAMILY_RUNG.md",
    "Endpoint source-family status and physical-source non-claims."
  ),
  moderate3p1Capstone: projectSource(
    "Moderate 3+1 V5 capstone",
    "supporting_reports/STAGE2_BETA075_MODERATE_3P1_V5_CAPSTONE.md",
    "Current local 3+1/backreaction capstone watch-pass scope for the sealed V5 target."
  )
};

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
      { id: "packet_release", content: "The timing of a release handoff in a particular service architecture." }
    ],
    answer: ["local_time"],
    explanation: {
      answer: "The lapse controls the local advance of time between slices.",
      why: "In a 3+1 split, lapse and shift separate normal time advance from spatial coordinate drift.",
      boundary: "This is established ADM terminology, not active-rail-specific vocabulary.",
      references: [references.adm]
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
      { id: "plant", content: "The prepared infrastructure that supplies support, carry, handoff, decompression, and reset functions." },
      { id: "payload", content: "The passenger-facing packet whose protection is one service requirement." },
      { id: "constraint", content: "An established theorem proving physical realizability." },
      { id: "rset", content: "The renormalized stress tensor of a quantum field." }
    ],
    answer: ["plant"],
    explanation: {
      answer: "The rail is the prepared operating infrastructure.",
      why: "The active-rail architecture separates the serviced packet from the support, carrying, handoff, endpoint, and reset infrastructure that bears much of the geometric burden.",
      boundary: "This is project model language, not established GR terminology.",
      references: [],
      sourceLinks: [sources.technicalDisclosure, sources.cliSourceParams]
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
    prompt: "True or false: Alcubierre's 1994 paper \"The Warp Drive\" presents a speculative spacetime model, not a demonstrated engineering construction.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["true"],
    explanation: {
      answer: "True.",
      why: "The metric is a published model for exploring relativistic geometry and energy-condition issues.",
      boundary: "Published speculative-relativity context should not be presented as solved engineering.",
      references: [references.alcubierre]
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
      { id: "prove_build", content: "They prove a service plant can be built if a packet trace arrives." },
      { id: "ignore", content: "They can be ignored once a service chronology is named." }
    ],
    answer: ["diagnose", "boundary"],
    explanation: {
      answer: "Energy-condition checks diagnose source constraints and help maintain claim boundaries.",
      why: "They are part of established relativistic analysis, but they do not by themselves produce a realizable matter sector.",
      boundary: "This is established constraint material applied to design interpretation, not a proof of buildability.",
      references: [references.fordRoman]
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
      references: [references.carrollGrNotes],
      sourceLinks: [sources.componentSourceLedger],
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
      sourceLinks: [sources.serviceAlignedSchedule, sources.resetReleaseLadder]
    }
  },
  {
    id: "claim_status.classification.001",
    type: "claim_classification",
    track: "Design review and synthesis",
    module: "Claim classification",
    difficulty: "core",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    prompt: "Classify each statement by claim status.",
    statuses: ["established_theory", "literature_model", "active_rail_model", "open_gate"],
    statements: [
      { id: "adm", content: "ADM lapse and shift split time advance from spatial drift.", answer: "established_theory" },
      { id: "alcubierre", content: "The Alcubierre metric is a published speculative warp model.", answer: "literature_model" },
      { id: "rail", content: "The rail is prepared infrastructure and the passenger-facing region is the packet.", answer: "active_rail_model" },
      { id: "reset", content: "Reusable rail reset has no source-history accumulation.", answer: "open_gate" }
    ],
    explanation: {
      answer: "ADM is established theory, Alcubierre is literature context, packet/rail is active-rail model language, and reset accumulation is an open gate.",
      why: "The statements mix textbook theory, published speculative geometry, project terminology, and unresolved project evidence.",
      boundary: "This item intentionally mixes statuses to test epistemic classification.",
      references: [references.adm, references.alcubierre],
      sourceLinks: [sources.technicalDisclosure]
    }
  },
  {
    id: "symbols.matching.001",
    type: "matching",
    track: "Active-rail architecture",
    module: "Symbol roles",
    difficulty: "core",
    claimStatus: "active_rail_model",
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
      why: "Alpha and beta are standard lapse/shift notation in ADM language; gamma components denote spatial metric sectors.",
      boundary: "The ADM lapse/shift terms are established. A particular service interpretation of the angular sector is project model language.",
      references: [references.adm],
      sourceLinks: [sources.cliSourceParams]
    }
  },
  {
    id: "design_review.burden.001",
    type: "multi",
    track: "Design review and synthesis",
    module: "Failure analysis",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
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
      why: "Active-rail qualification separates packet-facing success from plant burden, reset evidence, and source realization. A clean arrival can be a real success while still leaving the support edge, angular sector, and reset history unqualified.",
      boundary: "This is active-rail design-review logic, not a general theorem of GR or a substitute for physical source closure.",
      references: [],
      sourceLinks: [sources.boundedSealReadiness, sources.sourceFamilyValidation]
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
      sourceLinks: [sources.projectReadme, sources.sourceFamilyValidation, sources.boundedSealReadiness],
      openGate: "Passing a prescribed-metric or fixed-background screen does not prove matter-action closure, semiclassical consistency, or broad repeated-service viability."
    }
  },
  {
    id: "foundation.metric_interval.001",
    type: "mc",
    track: "Established foundations",
    module: "Metric basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What does a spacetime metric determine locally?",
    choices: [
      { id: "interval", content: "The interval, causal character, and inner products of nearby tangent vectors." },
      { id: "matter", content: "A unique matter model that must realize the geometry." },
      { id: "global", content: "The complete global topology without additional information." },
      { id: "coordinates", content: "A preferred coordinate system for all observers." }
    ],
    answer: ["interval"],
    explanation: {
      answer: "A metric determines local intervals and inner products.",
      why: "The metric is the tensor field used to evaluate lengths, times, angles, null directions, and causal character locally.",
      boundary: "This is established differential-geometric GR machinery, not active-rail terminology.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.adm_shift.001",
    type: "mc",
    track: "Established foundations",
    module: "ADM split",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In a 3+1 split, what is the basic role of the shift vector?",
    choices: [
      { id: "spatial_drift", content: "It describes how spatial coordinates drift from one slice to the next." },
      { id: "proper_time", content: "It alone sets the proper-time separation between slices." },
      { id: "matter_law", content: "It supplies a physical stress-energy law." },
      { id: "quantum_state", content: "It selects the quantum vacuum state." }
    ],
    answer: ["spatial_drift"],
    explanation: {
      answer: "The shift describes spatial coordinate drift between slices.",
      why: "ADM lapse and shift separate normal time advance from tangential coordinate motion.",
      boundary: "This is established ADM language. Later active-rail use of shift-like carrying-flow terms is project interpretation.",
      references: [references.adm]
    }
  },
  {
    id: "foundation.nec.dragfill.001",
    type: "drag_fill",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "core",
    claimStatus: "established_constraint",
    contentFlags: [],
    promptParts: [
      "For every null vector ",
      { type: "math", latex: "k^\\mu", label: "k mu" },
      ", the null energy condition requires ",
      { type: "blank", id: "nec_expression" },
      "."
    ],
    tokens: [
      { id: "tkk_nonnegative", content: [{ type: "math", latex: "T_{\\mu\\nu}k^\\mu k^\\nu \\ge 0", label: "T mu nu k mu k nu greater than or equal to zero" }] },
      { id: "trace_zero", content: [{ type: "math", latex: "T^\\mu{}_{\\mu}=0", label: "trace of T equals zero" }] },
      { id: "einstein_tensor_zero", content: [{ type: "math", latex: "G_{\\mu\\nu}=0", label: "Einstein tensor equals zero" }] },
      { id: "timelike_norm", content: [{ type: "math", latex: "k^\\mu k_\\mu=-1", label: "k mu k mu equals minus one" }] }
    ],
    blanks: [
      { id: "nec_expression", accepts: ["tkk_nonnegative"] }
    ],
    explanation: {
      answer: [{ type: "math", latex: "T_{\\mu\\nu}k^\\mu k^\\nu \\ge 0", label: "null energy condition expression" }],
      why: "The NEC is a condition on stress-energy contracted twice with any null vector.",
      boundary: "This is an established constraint. Violating it is a diagnostic pressure, not by itself a full impossibility proof.",
      references: [references.carrollGrNotes, references.fordRoman]
    }
  },
  {
    id: "foundation.hamiltonian_constraint.001",
    type: "mc",
    track: "Established foundations",
    module: "ADM constraints",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What makes the ADM Hamiltonian constraint useful for source diagnostics?",
    choices: [
      { id: "geometry_source_relation", content: "It ties intrinsic/extrinsic slice geometry to the energy density seen by the normal observer." },
      { id: "unique_solution", content: "It uniquely determines the global spacetime from one scalar equation." },
      { id: "no_matter", content: "It removes the need to discuss stress-energy." },
      { id: "coordinate_only", content: "It is only a coordinate convention with no relation to matter content." }
    ],
    answer: ["geometry_source_relation"],
    explanation: {
      answer: "It relates slice geometry to normal-observer energy density.",
      why: "The constraint connects spatial curvature and extrinsic curvature terms to the matter energy density projection.",
      boundary: "This is established ADM structure. Using it as a diagnostic ledger is an application, not a new theorem.",
      references: [references.adm]
    }
  },
  {
    id: "foundation.extrinsic_curvature.001",
    type: "mc",
    track: "Established foundations",
    module: "ADM split",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What does extrinsic curvature measure in the ADM setting?",
    choices: [
      { id: "embedding_change", content: "How the spatial slice is embedded in spacetime, equivalently how its spatial metric changes along the normal direction." },
      { id: "intrinsic_only", content: "Only the intrinsic two-dimensional curvature of an angular sphere." },
      { id: "matter_choice", content: "Which microscopic matter action realizes a prescribed metric." },
      { id: "global_topology", content: "Whether spacetime has nontrivial global topology." }
    ],
    answer: ["embedding_change"],
    explanation: {
      answer: "Extrinsic curvature tracks how a spatial slice sits and evolves inside spacetime.",
      why: "It is not merely intrinsic spatial curvature; it records normal-direction change of the spatial geometry.",
      boundary: "This is established ADM geometry and should not be confused with a project-specific source channel.",
      references: [references.adm]
    }
  },
  {
    id: "foundation.observer_energy.001",
    type: "mc",
    track: "Established foundations",
    module: "Stress-energy basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "For an observer with unit timelike four-velocity u^mu, which contraction gives the local energy density that observer measures?",
    choices: [
      { id: "tuu", content: [{ type: "math", latex: "T_{\\mu\\nu}u^\\mu u^\\nu", label: "T mu nu u mu u nu" }] },
      { id: "trace", content: [{ type: "math", latex: "T^\\mu{}_{\\mu}", label: "trace of T" }] },
      { id: "einstein", content: [{ type: "math", latex: "G_{\\mu\\nu}k^\\mu k^\\nu", label: "Einstein tensor contracted with null vector" }] },
      { id: "metric_norm", content: [{ type: "math", latex: "g_{\\mu\\nu}u^\\mu u^\\nu", label: "metric norm of u" }] }
    ],
    answer: ["tuu"],
    explanation: {
      answer: [{ type: "math", latex: "T_{\\mu\\nu}u^\\mu u^\\nu", label: "observer energy density" }],
      why: "Stress-energy becomes observer-measured energy density when projected twice onto the observer's timelike four-velocity. The trace, metric norm, and null contractions answer different geometric or source questions.",
      boundary: "This is standard GR stress-energy machinery and is independent of any active-rail source-ledger convention.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.energy_conditions.matching.001",
    type: "matching",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "Match each energy-condition phrase to the contraction or observer statement it most directly tests.",
    prompts: [
      { id: "nec", content: "Null energy condition" },
      { id: "wec", content: "Weak energy condition" },
      { id: "trace", content: "Stress-tensor trace" }
    ],
    options: [
      { id: "null_contraction", label: "Nonnegative T_mn k^m k^n for every null k" },
      { id: "timelike_density", label: "Nonnegative T_mn u^m u^n for every timelike observer u" },
      { id: "contracted_trace", label: "T^m_m, not itself an energy condition" }
    ],
    answer: {
      nec: "null_contraction",
      wec: "timelike_density",
      trace: "contracted_trace"
    },
    explanation: {
      answer: "NEC tests null contractions, WEC tests timelike-observer energy density, and the trace is a separate contraction.",
      why: "Energy conditions are not interchangeable slogans. Matching each phrase to the correct contraction keeps later source diagnostics from confusing null exposure, observer energy density, and trace behavior.",
      boundary: "This is established stress-energy vocabulary; it does not by itself decide whether a proposed geometry is physically realizable.",
      references: [references.carrollGrNotes, references.fordRoman]
    }
  },
  {
    id: "foundation.einstein_equation.dragfill.002",
    type: "drag_fill",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    promptParts: [
      "In units ",
      { type: "math", latex: "G=c=1", label: "G equals c equals one" },
      ", Einstein's equation can be written as ",
      { type: "blank", id: "equation" },
      "."
    ],
    tokens: [
      { id: "einstein_eq", content: [{ type: "math", latex: "G_{\\mu\\nu}=8\\pi T_{\\mu\\nu}", label: "G mu nu equals eight pi T mu nu" }] },
      { id: "flat_metric", content: [{ type: "math", latex: "g_{\\mu\\nu}=\\eta_{\\mu\\nu}", label: "metric equals eta" }] },
      { id: "null_norm", content: [{ type: "math", latex: "k^\\mu k_\\mu=0", label: "null norm equals zero" }] },
      { id: "trace", content: [{ type: "math", latex: "T^\\mu{}_{\\mu}=0", label: "trace of T equals zero" }] }
    ],
    blanks: [
      { id: "equation", accepts: ["einstein_eq"] }
    ],
    explanation: {
      answer: [{ type: "math", latex: "G_{\\mu\\nu}=8\\pi T_{\\mu\\nu}", label: "Einstein equation" }],
      why: "The equation relates spacetime curvature to stress-energy in the chosen units. The other tokens are useful statements in other contexts, but they are not Einstein's field equation.",
      boundary: "This is established GR machinery; computing a demanded source from it is still not a physical matter model.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.adm_momentum_constraint.001",
    type: "mc",
    track: "Established foundations",
    module: "ADM constraints",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What does the ADM momentum constraint primarily relate?",
    choices: [
      { id: "momentum_projection", content: "Spatial variation of extrinsic curvature to the matter momentum density seen by the slice normal." },
      { id: "unique_global", content: "A unique global spacetime topology to one local lapse value." },
      { id: "vacuum_only", content: "Only vacuum curvature, with no matter projection involved." },
      { id: "quantum_state", content: "The renormalized quantum state to the observer's detector response." }
    ],
    answer: ["momentum_projection"],
    explanation: {
      answer: "It relates extrinsic-curvature combinations to the momentum density projection of stress-energy.",
      why: "In ADM language the constraints split source diagnostics into normal energy-density and spatial momentum channels. That distinction matters before any project-specific source ledger or channel naming is introduced.",
      boundary: "This is established ADM structure and should not be mistaken for a physical source construction.",
      references: [references.adm]
    }
  },
  {
    id: "constraints.qi_interpretation.001",
    type: "mc",
    track: "Established foundations",
    module: "Quantum inequalities",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Ford and Roman's 1996 paper \"Quantum Field Theory Constrains Traversable Wormhole Geometries,\" what is the safest interpretation of the quantum inequality constraints?",
    choices: [
      { id: "bound_negative_energy", content: "They bound the magnitude, duration, and distribution of negative-energy effects in relevant quantum-field settings." },
      { id: "ban_all", content: "They prove that no negative energy density can ever occur in quantum field theory." },
      { id: "construct_drive", content: "They provide a recipe for building a warp bubble if the geometry is smooth." },
      { id: "ignore_geometry", content: "They make geometric source ledgers irrelevant." }
    ],
    answer: ["bound_negative_energy"],
    explanation: {
      answer: "Quantum inequalities constrain negative energy; they do not erase the subject or solve engineering.",
      why: "The key lesson is quantitative restriction, not a simplistic ban or a construction method.",
      boundary: "This is established constraint literature applied to speculative geometries, not a source recipe.",
      references: [references.fordRoman]
    }
  },
  {
    id: "literature.barcelo_visser.scalar.001",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Scalar-source literature",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements accurately describe Barcelo and Visser's 2000 paper \"Scalar Fields, Energy Conditions, and Traversable Wormholes\"?",
    choices: [
      { id: "scalar_violation", content: "Non-minimally coupled scalar fields can violate standard energy conditions, including averaged null-energy conditions." },
      { id: "trans_planckian", content: "The traversable-wormhole branch carries a serious trans-Planckian field-value caveat." },
      { id: "plug_in", content: "It supplies an experimentally established material that can be inserted into any macroscopic wormhole geometry." },
      { id: "no_constraints", content: "It removes all energy-condition and quantum-gravity concerns." }
    ],
    answer: ["scalar_violation", "trans_planckian"],
    explanation: {
      answer: "The paper shows a scalar-field route to energy-condition violation while keeping the trans-Planckian caveat visible.",
      why: "The result is not simply 'scalar fields solve wormholes'; the field scale and physical interpretation remain central. The valuable lesson is that source models can evade classical energy conditions while still raising severe feasibility and semiclassical-trust questions.",
      boundary: "This is published literature about a theoretical source class, not demonstrated macroscopic engineering.",
      references: [references.barceloVisser]
    }
  },
  {
    id: "literature.natario.001",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Natario's 2002 paper \"Warp Drive With Zero Expansion,\" what does zero expansion mean?",
    choices: [
      { id: "congruence_property", content: "It describes a property of the chosen flow congruence, not the absence of curvature or source demands." },
      { id: "no_energy", content: "It means the spacetime needs no stress-energy." },
      { id: "flat_everywhere", content: "It means the metric is flat everywhere." },
      { id: "complete_engineering", content: "It converts the warp model into an engineered propulsion system." }
    ],
    answer: ["congruence_property"],
    explanation: {
      answer: "Zero expansion is a kinematic property of the flow, not a source-free engineering result.",
      why: "A warp metric can have zero expansion while still carrying curvature and stress-energy issues.",
      boundary: "This is published speculative metric context, not a physical construction or source model.",
      references: [references.natario]
    }
  },
  {
    id: "constraints.topological_censorship.001",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Topological censorship",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "What is the disciplined use of Friedman, Schleich, and Witt's 1993 topological censorship result in traversable-wormhole discussions?",
    choices: [
      { id: "conditional_constraint", content: "It is a conditional theorem showing that, under suitable assumptions, nontrivial topology is hidden from causal observers." },
      { id: "algebraic_ban", content: "It is an algebraic ban on writing any wormhole metric." },
      { id: "all_sources_solved", content: "It proves every possible source-realization question is solved." },
      { id: "fictional", content: "It is only a narrative convention without mathematical content." }
    ],
    answer: ["conditional_constraint"],
    explanation: {
      answer: "Topological censorship is a conditional constraint theorem.",
      why: "Its force comes from its assumptions: energy, causality, asymptotic structure, and predictability conditions matter. The theorem is powerful because it tells you which global structures are hidden under those assumptions, not because it forbids writing every wormhole metric.",
      boundary: "This is established constraint material. It should be used carefully, not as a slogan or an assumption-free ban.",
      references: [references.topologicalCensorship]
    }
  },
  {
    id: "constraints.chronology_protection.001",
    type: "tf",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "core",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "True or false: Visser's 2002 review \"The Quantum Physics of Chronology Protection\" treats chronology-protection arguments as serious causality constraints, not completed engineering recipes.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["true"],
    explanation: {
      answer: "True.",
      why: "Chronology-protection literature treats closed-causal-curve formation as a deep causality and quantum-field problem, not a construction method.",
      boundary: "This is literature-backed constraint context, with conjectural status.",
      references: [references.chronologyProtection]
    }
  },
  {
    id: "literature.alcubierre_horizon.001",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which cautions are appropriate when interpreting Alcubierre's 1994 warp metric?",
    choices: [
      { id: "metric_not_engine", content: "A metric ansatz is not the same thing as a controlled physical engine." },
      { id: "source_demand", content: "The stress-energy demand and energy-condition behavior remain central." },
      { id: "automatic_control", content: "If the line element is smooth, a passenger can necessarily create, steer, and stop the bubble." },
      { id: "established_transport", content: "It is established transportation physics because it is a solution ansatz in GR." }
    ],
    answer: ["metric_not_engine", "source_demand"],
    explanation: {
      answer: "The metric is a valuable speculative model, but source demand and control questions remain central.",
      why: "Writing a spacetime geometry does not supply matter realization, stability, causal control, or operational protocols. The advanced skill is recognizing that a smooth ansatz can still leave negative energy, horizon, and steering questions unresolved.",
      boundary: "This is published-literature interpretation with unresolved physical gates, not a physical-realization result.",
      references: [references.alcubierre],
      openGate: "Physical realizability, controllability, and source construction remain outside the metric ansatz itself."
    }
  },
  {
    id: "literature.chl.null_geodesics.001",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Clark, Hiscock, and Larson's 1999 paper \"Null Geodesics in the Alcubierre Warp Drive Spacetime,\" what causal feature appears for effective superluminal motion?",
    choices: [
      { id: "causal_access", content: "Horizon-like conical regions appear, limiting which signals can reach or be sent from the bubble." },
      { id: "complete_control", content: "A passenger at the bubble center can create, steer, and stop the bubble on demand." },
      { id: "no_quantum", content: "Null-geodesic behavior removes quantum-vacuum concerns." },
      { id: "flat_optics", content: "All photon paths remain indistinguishable from flat-space optics." }
    ],
    answer: ["causal_access"],
    explanation: {
      answer: "The paper identifies horizon-like conical access structures.",
      why: "For effective superluminal motion, the null-geodesic structure includes regions that block signals from reaching the bubble and regions the bubble cannot signal into. That makes causal access a geometric issue, not just a matter of passenger intent.",
      boundary: "This is a result about the Alcubierre spacetime's causal optics, not a construction method.",
      references: [references.clarkHiscockLarson]
    }
  },
  {
    id: "literature.muller_weiskopf.geodesics.001",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "What does Mueller and Weiskopf's 2012 paper \"Detailed Study of Null and Time-Like Geodesics in the Alcubierre Warp Spacetime\" emphasize?",
    choices: [
      { id: "playground", content: "It is a rich setting for null and timelike geodesic/lensing calculations, while remaining far from physical feasibility because of exotic matter." },
      { id: "build", content: "Treat it as a construction plan for a physically feasible warp engine." },
      { id: "ignore_sources", content: "Use it to avoid source and energy-condition analysis." },
      { id: "no_curvature", content: "Use it to show the Alcubierre spacetime is optically flat." }
    ],
    answer: ["playground"],
    explanation: {
      answer: "It treats Alcubierre spacetime as a detailed geodesic/lensing study while preserving feasibility caveats.",
      why: "The paper's educational value is in the geodesic and visual-effects analysis, not in claiming physical construction.",
      boundary: "This is published-literature study of a speculative spacetime, not demonstrated engineering.",
      references: [references.mullerWeiskopf]
    }
  },
  {
    id: "literature.everett_roman.krasnikov.001",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements match Everett and Roman's 1997 paper \"A Superluminal Subway: The Krasnikov Tube\"?",
    choices: [
      { id: "two_tubes", content: "A single directed tube is not the same chronology problem as a two-tube network arranged into a time-machine system." },
      { id: "negative_energy", content: "The construction still carries severe negative-energy and thin-layer concerns." },
      { id: "no_ctc", content: "Any number of superluminal tubes is chronology-safe once each tube is individually one-way." },
      { id: "source_solution", content: "The paper supplies a practical ordinary-matter source for constructing the tube." }
    ],
    answer: ["two_tubes", "negative_energy"],
    explanation: {
      answer: "Network composition and negative-energy burden are both central.",
      why: "Everett and Roman distinguish the single-tube case from a two-tube time-machine arrangement, while preserving severe source concerns. The point is that chronology risk depends on how superluminal links are composed, not only on each link in isolation.",
      boundary: "This is superluminal-spacetime literature, not demonstrated engineering or a practical ordinary-matter construction.",
      references: [references.everettRoman]
    }
  },
  {
    id: "literature.shoshany_snodgrass.ctc.001",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "What does Shoshany and Snodgrass's 2024 paper \"Warp Drives and Closed Timelike Curves\" demonstrate?",
    choices: [
      { id: "composition", content: "It gives a concrete GR model where composed warp-drive geometries yield a closed timelike geodesic." },
      { id: "safe", content: "It proves all warp-drive networks are chronology-safe when each leg is smooth." },
      { id: "matter", content: "It derives ordinary positive-energy matter that realizes the drives." },
      { id: "coordinates", content: "It shows closed timelike curves are only a coordinate-label issue." }
    ],
    answer: ["composition"],
    explanation: {
      answer: "It demonstrates that composed warp-drive geometries can create closed-timelike-curve structure.",
      why: "The paper supplies a concrete two-warp-drive model rather than leaving the timing issue as only a slogan. The important reasoning step is composition: multiple superluminal geometries can change the global causal story.",
      boundary: "This is a published chronology result about warp-drive geometries, not a physical-realization claim or an engineering recipe.",
      references: [references.shoshanySnodgrass]
    }
  },
  {
    id: "literature.garattini_zatrimaylov.correspondence.001",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp-wormhole correspondence",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements are careful takeaways from Garattini and Zatrimaylov's 2024 paper \"On the Wormhole--Warp Drive Correspondence\"?",
    choices: [
      { id: "curvature", content: "The correspondence requires allowing nonzero intrinsic spatial curvature in the warp-drive metric." },
      { id: "traversability_caveat", content: "The paper reports a traversability caveat rather than a simple equivalence between comfortable wormholes and warp drives." },
      { id: "flat_shift", content: "Any flat-spatial-slice shift profile is automatically a Morris-Thorne wormhole." },
      { id: "realization", content: "The correspondence proves a physical matter source for a traversable warp-drive carrier." }
    ],
    answer: ["curvature", "traversability_caveat"],
    explanation: {
      answer: "The useful takeaways are intrinsic-curvature dependence and a nontrivial traversability caveat.",
      why: "The result is a constrained correspondence, not a statement that ordinary traversable wormholes and warp drives are interchangeable. The need for intrinsic spatial curvature prevents the takeaway from collapsing into a simple flat-slice shift analogy.",
      boundary: "This is published correspondence context and must not be promoted to engineering completion or physical source realization.",
      references: [references.garattiniZatrimaylov]
    }
  },
  {
    id: "constraints.snec.semiglobal.001",
    type: "mc",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "What does the 2025 paper \"How Much NEC Breaking Can the Universe Endure?\" add beyond a pointwise NEC check?",
    choices: [
      { id: "semilocal_bound", content: "It treats accumulated negative energy along smeared null probes as a semilocal constraint." },
      { id: "pointwise_only", content: "It says only the pointwise sign of one stress-tensor component matters." },
      { id: "construction", content: "It supplies a physical source construction for any prescribed negative-energy profile." },
      { id: "irrelevant", content: "It says pointwise energy-condition checks are the only relevant tests." }
    ],
    answer: ["semilocal_bound"],
    explanation: {
      answer: "The added lesson is semilocal accumulation: not just pointwise sign.",
      why: "The smeared NEC is a quantum-motivated bound on accumulated NEC violation along null probes. It trains the learner to ask about finite-window exposure, not only whether one sampled stress-tensor contraction is negative.",
      boundary: "This is a constraint reference, not a construction recipe or a replacement for a full source model.",
      references: [references.smearedNec]
    }
  },
  {
    id: "literature.alcubierre.stress_energy.002",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements are careful readings of Alcubierre's 1994 paper \"The Warp Drive\"?",
    choices: [
      { id: "metric_ansatz", content: "The paper gives a spacetime metric that contracts space ahead of a region and expands it behind." },
      { id: "negative_energy", content: "The stress-energy required by the metric includes exotic energy-condition behavior." },
      { id: "ordinary_matter", content: "The paper derives an ordinary-matter engine that creates the geometry." },
      { id: "no_causality", content: "The paper removes all causality and control concerns for superluminal travel." }
    ],
    answer: ["metric_ansatz", "negative_energy"],
    explanation: {
      answer: "The paper presents a metric ansatz and exposes exotic stress-energy behavior.",
      why: "A careful reading separates the geometric construction from the missing source mechanism. The model is famous because it shows what GR's equations allow as a geometry, while also revealing a severe stress-energy burden.",
      boundary: "This is published speculative-relativity literature, not demonstrated propulsion physics or an ordinary-matter construction.",
      references: [references.alcubierre]
    }
  },
  {
    id: "constraints.ford_roman.sampling.002",
    type: "mc",
    track: "Established foundations",
    module: "Quantum inequalities",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Ford and Roman's 1996 paper \"Quantum Field Theory Constrains Traversable Wormhole Geometries,\" why does sampling time matter?",
    choices: [
      { id: "duration_bound", content: "Quantum inequalities constrain how much negative energy can be seen over a sampling interval, tying magnitude to duration and scale." },
      { id: "coordinate_choice", content: "Sampling time is only a coordinate convention and has no physical role." },
      { id: "permanent_negative", content: "Long-lived macroscopic negative energy can be made arbitrarily large if it is smooth." },
      { id: "construction", content: "The sampling bound supplies a recipe for building a traversable wormhole." }
    ],
    answer: ["duration_bound"],
    explanation: {
      answer: "Sampling time matters because the bound couples negative-energy magnitude to duration and scale.",
      why: "The quantum inequality is not just a pointwise warning. It says sustained negative energy is quantitatively constrained, which is why macroscopic wormhole geometries become so difficult under the paper's assumptions.",
      boundary: "This is an established constraint result in the cited setting, not an all-purpose construction or a proof that every negative-energy effect is impossible.",
      references: [references.fordRoman]
    }
  },
  {
    id: "literature.chl.control.002",
    type: "tf",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "True or false: Clark, Hiscock, and Larson's 1999 paper \"Null Geodesics in the Alcubierre Warp Drive Spacetime\" supports the idea that a central observer can freely control a superluminal bubble after it forms.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["false"],
    explanation: {
      answer: "False.",
      why: "The paper's null-geodesic analysis identifies causal-access restrictions for the superluminal case. That is the opposite of a simple passenger-control story, because signals do not freely connect all relevant regions.",
      boundary: "This is a causal-structure lesson about the Alcubierre spacetime, not a complete analysis of every possible warp-drive variant.",
      references: [references.clarkHiscockLarson]
    }
  },
  {
    id: "literature.shoshany_snodgrass.energy.002",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which conclusions are supported by Shoshany and Snodgrass's 2024 paper \"Warp Drives and Closed Timelike Curves\"?",
    choices: [
      { id: "ctg", content: "Two warp-drive geometries can be arranged so that a closed timelike geodesic exists." },
      { id: "wec_violation", content: "The construction remains tied to weak-energy-condition violation." },
      { id: "ordinary_matter", content: "The construction shows ordinary positive-energy matter is enough to build the drives." },
      { id: "single_leg_safe", content: "It proves every individual superluminal leg is globally chronology-safe in all networks." }
    ],
    answer: ["ctg", "wec_violation"],
    explanation: {
      answer: "The paper supports the closed-timelike-geodesic construction and keeps energy-condition violation in view.",
      why: "The point is not only that closed causal curves can be discussed abstractly. The paper gives a concrete two-drive arrangement and does not turn that arrangement into ordinary positive-energy engineering.",
      boundary: "This is a published chronology and energy-condition result about a theoretical construction, not a buildability claim.",
      references: [references.shoshanySnodgrass]
    }
  },
  {
    id: "literature.garattini_zatrimaylov.intrinsic_curvature.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp-wormhole correspondence",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Garattini and Zatrimaylov's 2024 paper \"On the Wormhole--Warp Drive Correspondence,\" what extra ingredient is central to relating Morris-Thorne wormholes to warp-drive form?",
    choices: [
      { id: "intrinsic_curvature", content: "Nonzero intrinsic spatial curvature in the warp-drive metric." },
      { id: "flat_space", content: "Strictly flat spatial slices everywhere." },
      { id: "ordinary_fuel", content: "A specified ordinary-matter fuel model." },
      { id: "no_shift", content: "Removing all shift-like structure from the metric." }
    ],
    answer: ["intrinsic_curvature"],
    explanation: {
      answer: "The key ingredient is nonzero intrinsic spatial curvature.",
      why: "That requirement makes the correspondence more subtle than a simple rebranding of a flat-slice warp shift. It also helps explain why the paper's traversability caveat matters for interpretation.",
      boundary: "This is a correspondence result inside published speculative geometry, not a source-realization theorem.",
      references: [references.garattiniZatrimaylov]
    }
  },
  {
    id: "constraints.visser_chronology.horizon.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Visser's 2002 review \"The Quantum Physics of Chronology Protection,\" why are chronology horizons physically worrisome?",
    choices: [
      { id: "backreaction", content: "They are places where quantum-field stress and backreaction concerns may become central." },
      { id: "recipe", content: "They provide a stable recipe for constructing closed timelike curves." },
      { id: "coordinate", content: "They show chronology violation is always only a coordinate artifact." },
      { id: "irrelevant", content: "They remove the need for quantum-field analysis." }
    ],
    answer: ["backreaction"],
    explanation: {
      answer: "They are worrisome because quantum-field stress and backreaction can become central near chronology horizons.",
      why: "Chronology protection is not merely a naming convention for time travel. The review surveys why quantum effects near the onset of closed causal curves can threaten the classical spacetime picture.",
      boundary: "This is constraint and review literature, not a finished theorem that supplies engineering design rules.",
      references: [references.chronologyProtection]
    }
  },
  {
    id: "active_rail.packet_vs_plant.001",
    type: "mc",
    track: "Active-rail architecture",
    module: "Packet versus plant",
    difficulty: "core",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "A packet trace arrives cleanly at the target endpoint. What does that show by itself?",
    choices: [
      { id: "packet_facing", content: "A packet-facing success signal for that trace, not complete plant qualification." },
      { id: "matter_action", content: "A completed matter action for the whole service infrastructure." },
      { id: "all_channels", content: "All plant burden channels are automatically closed." },
      { id: "global_causality", content: "Global causal structure has been proven safe." }
    ],
    answer: ["packet_facing"],
    explanation: {
      answer: "It is packet-facing evidence, not full plant qualification.",
      why: "Active-rail review separates packet trajectory outcomes from plant burden, support closure, reset residue, and source realization.",
      boundary: "This is project architecture language and should be read as an internal design distinction.",
      references: [],
      sourceLinks: [sources.technicalDisclosure, sources.entryServiceGate]
    }
  },
  {
    id: "active_rail.source_ledger_boundary.002",
    type: "mc",
    track: "Active-rail architecture",
    module: "Source ledger",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "A demanded-source ledger has been computed for a prescribed geometry. What is the next claim boundary?",
    choices: [
      { id: "demand_not_realization", content: "The ledger identifies source demand; it does not yet supply a physical source sector." },
      { id: "realized", content: "The geometry is physically realized because the ledger has entries." },
      { id: "irrelevant", content: "The ledger makes energy conditions irrelevant." },
      { id: "global", content: "The ledger proves global causal safety." }
    ],
    answer: ["demand_not_realization"],
    explanation: {
      answer: "Demand accounting is not source realization.",
      why: "A ledger can identify what stress-energy a prescribed metric would require without deriving matter dynamics that supply it.",
      boundary: "This is one of the core active-rail claim boundaries, not established GR terminology.",
      references: [references.carrollGrNotes],
      sourceLinks: [sources.componentSourceLedger, sources.technicalDisclosure],
      openGate: "A physical matter action, semiclassical stress tensor, or coupled Einstein-matter evolution remains a separate requirement."
    }
  },
  {
    id: "active_rail.demand_realization.classification.003",
    type: "claim_classification",
    track: "Design review and synthesis",
    module: "Claim classification",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    prompt: "Classify each source-related claim by the safest status.",
    statuses: ["established_theory", "literature_model", "active_rail_model", "project_hypothesis", "open_gate"],
    statements: [
      { id: "einstein", content: "Einstein's equation relates curvature to stress-energy.", answer: "established_theory" },
      { id: "qi", content: "Ford-Roman quantum inequalities constrain sustained negative-energy distributions in their setting.", answer: "literature_model" },
      { id: "ledger", content: "A demanded-source ledger records the stress-energy required by a prescribed active-rail metric.", answer: "active_rail_model" },
      { id: "source_family", content: "The current source-family strategy is a candidate route for organizing active-rail source burden.", answer: "project_hypothesis" },
      { id: "matter_action", content: "A complete matter action realizing repeated service has been derived.", answer: "open_gate" }
    ],
    explanation: {
      answer: "The claims split into established theory, published constraint literature, project model language, project hypothesis, and open gate.",
      why: "The classification matters because the same source conversation can contain textbook equations, paper constraints, internal ledger vocabulary, candidate strategies, and unresolved physical realization at once.",
      boundary: "This item is project application with open-gate content, so it should remain excludable from stable general-theory sessions.",
      references: [references.carrollGrNotes, references.fordRoman],
      sourceLinks: [sources.componentSourceLedger, sources.sourceFamilyValidation],
      openGate: "Matter-action and repeated-service source realization remain separate from demanded-source accounting."
    }
  },
  {
    id: "active_rail.service_evidence.sequence.002",
    type: "sequence",
    track: "Active-rail architecture",
    module: "Service chronology",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "Order these review checkpoints for a single active-rail service pass.",
    items: [
      { id: "pre_support", content: "Verify standing support and packet corridor preparation" },
      { id: "carry", content: "Carry packet through the supported service interval" },
      { id: "catch", content: "Catch/rematch before release fade" },
      { id: "fade", content: "Fade active carrying support" },
      { id: "decompress", content: "Decompress support and source load" },
      { id: "reset_audit", content: "Audit reset residue before reuse" }
    ],
    answer: ["pre_support", "carry", "catch", "fade", "decompress", "reset_audit"],
    explanation: {
      answer: "Preparation, carry, catch/rematch, fade, decompression, reset audit.",
      why: "The review order preserves packet support before handoff and treats reset as evidence before reuse, not as an assumption.",
      boundary: "This is active-rail service architecture, not established textbook terminology or external physics doctrine.",
      references: [],
      sourceLinks: [sources.serviceAlignedSchedule, sources.resetReleaseLadder]
    }
  },
  {
    id: "active_rail.service_readiness.sequence.003",
    type: "sequence",
    track: "Active-rail architecture",
    module: "Service chronology",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "Order these service-readiness checkpoints for a conservative active-rail pass.",
    items: [
      { id: "ready", content: "Confirm rail and endpoint readiness before arming" },
      { id: "support", content: "Establish standing support/corridor conditions" },
      { id: "carry", content: "Carry the packet through the service interval" },
      { id: "handoff", content: "Catch/rematch before release fade" },
      { id: "unwind", content: "Decompress support and source load" },
      { id: "residue", content: "Check reset residue before declaring reuse readiness" }
    ],
    answer: ["ready", "support", "carry", "handoff", "unwind", "residue"],
    explanation: {
      answer: "Readiness, support, carry, handoff, unwind, reset-residue check.",
      why: "The ordering keeps support ahead of live service and treats reset as evidence after the pass, not as a label applied automatically because the packet arrived.",
      boundary: "This is active-rail service architecture, not established GR chronology terminology.",
      references: [],
      sourceLinks: [sources.serviceAlignedSchedule, sources.resetReleaseLadder]
    }
  },
  {
    id: "active_rail.paper_application.chl.001",
    type: "multi",
    track: "Design review and synthesis",
    module: "Paper-to-design transfer",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    scoring: "subtract_incorrect",
    prompt: "When applying Clark-Hiscock-Larson-style null-geodesic concerns to an active-rail carrier audit, which review moves are appropriate?",
    choices: [
      { id: "reachability", content: "Check signal reachability and branch access rather than assuming a smooth metric is controllable." },
      { id: "bundle", content: "Treat finite-bundle behavior as a diagnostic surface, not only one ideal ray." },
      { id: "proof", content: "Claim the CHL paper proves the active-rail carrier is safe." },
      { id: "ignore", content: "Ignore causal access because packet arrival was clean." }
    ],
    answer: ["reachability", "bundle"],
    explanation: {
      answer: "Reachability and finite-bundle behavior are appropriate review moves; claiming proof or ignoring access is not.",
      why: "This is a project-application question: the paper supplies a warning about causal optics, while the active-rail audit must still produce its own evidence for branch access, packet behavior, and service safety.",
      boundary: "This applies published literature to active-rail review. It is not a claim that the literature validates the project design.",
      references: [references.clarkHiscockLarson],
      sourceLinks: [sources.technicalDisclosure]
    }
  },
  {
    id: "active_rail.channel_roles.matching.001",
    type: "matching",
    track: "Active-rail architecture",
    module: "Plant diagnostics",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    prompt: "Match each diagnostic surface to its review role.",
    prompts: [
      { id: "packet_norm", content: "Live packet norm ledger" },
      { id: "support_closure", content: "Endpoint/support closure ledger" },
      { id: "source_family", content: "Source-family validation" },
      { id: "moderate_capstone", content: "Moderate local 3+1 stress rung" }
    ],
    options: [
      { id: "packet_safety", label: "Packet-facing safety screen" },
      { id: "plant_exchange", label: "Plant exchange and support accounting" },
      { id: "effective_source", label: "Fixed-background effective-source evidence" },
      { id: "stress_response", label: "Local response stress test" }
    ],
    answer: {
      packet_norm: "packet_safety",
      support_closure: "plant_exchange",
      source_family: "effective_source",
      moderate_capstone: "stress_response"
    },
    explanation: {
      answer: "Each surface reviews a different layer: packet safety, plant exchange, effective source family, and local stress response.",
      why: "Conflating these layers is how a narrow pass becomes an overclaim, because packet-facing safety, plant exchange, effective-source evidence, and local stress response answer different review questions.",
      boundary: "This is project-state architecture and review taxonomy, so it remains revision-sensitive.",
      references: [],
      sourceLinks: [sources.technicalDisclosure, sources.sourceFamilyValidation, sources.moderate3p1Capstone]
    }
  },
  {
    id: "claim_status.classification.002",
    type: "claim_classification",
    track: "Design review and synthesis",
    module: "Claim classification",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "project_state", "open_question"],
    prompt: "Classify each claim by the safest status.",
    statuses: ["established_theory", "established_constraint", "literature_model", "project_hypothesis", "open_gate"],
    statements: [
      { id: "nec", content: "The NEC tests contractions of stress-energy with null vectors.", answer: "established_theory" },
      { id: "qi", content: "Quantum inequality results constrain sustained negative-energy distributions.", answer: "established_constraint" },
      { id: "natario", content: "Natario's zero-expansion warp drive is a published speculative metric model.", answer: "literature_model" },
      { id: "source_family", content: "The current source-family package is fixed-background evidence for an active-rail source strategy.", answer: "project_hypothesis" },
      { id: "matter_action", content: "A complete matter action realizing repeated active-rail service has been derived.", answer: "open_gate" }
    ],
    explanation: {
      answer: "The statuses split established theory, established constraints, published literature, project evidence, and open gates.",
      why: "A strong architecture review keeps these categories separate even when the same design conversation uses all of them.",
      boundary: "The project-state statements are revision-sensitive and should remain explicitly flagged.",
      references: [references.carrollGrNotes, references.fordRoman, references.natario],
      sourceLinks: [sources.projectReadme, sources.sourceFamilyValidation],
      openGate: "Matter-action closure and repeated-service physical realization remain unresolved."
    }
  },
  {
    id: "project_state.v10_scope.002",
    type: "mc",
    track: "Design review and synthesis",
    module: "Project-state handling",
    difficulty: "advanced",
    claimStatus: "project_hypothesis",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    prompt: "A current service-rating ladder reports that the V10 case fails live packet source safety. What is the safest interpretation?",
    choices: [
      { id: "boundary", content: "It marks a high-service boundary for the current package and motivates additional causal/source-margin work." },
      { id: "impossible", content: "It proves every possible high-service active-rail design is impossible." },
      { id: "solved", content: "It proves V10 is ready because failed diagnostics are only bookkeeping." },
      { id: "general_theorem", content: "It is an established theorem of GR independent of the project configuration." }
    ],
    answer: ["boundary"],
    explanation: {
      answer: "It is a current-package high-service boundary, not a universal impossibility theorem.",
      why: "The reported failure is meaningful project evidence about the present V10 ladder. The careful interpretation preserves that warning while avoiding an overclaim about all future high-service geometries or all possible source strategies.",
      boundary: "This is revision-sensitive project-state content based on the current service-rating report, not established external theory.",
      references: [],
      sourceLinks: [sources.serviceRatingLadder, sources.projectReadme],
      openGate: "Additional causal-margin engineering and source-family work would be needed before a high-service promotion claim."
    }
  },
  {
    id: "project_state.v5_scope.001",
    type: "multi",
    track: "Design review and synthesis",
    module: "Project-state handling",
    difficulty: "advanced",
    claimStatus: "project_hypothesis",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    scoring: "subtract_incorrect",
    prompt: "A report describes the sealed beta075 V5 package as packet-safe with fixed-background endpoint/support and source-family evidence. Which scope statements are appropriate?",
    choices: [
      { id: "fixed_background", content: "It is evidence at prescribed-metric or fixed-background effective-source level." },
      { id: "watches", content: "Thin margins and watch conditions should remain visible in the claim." },
      { id: "matter_action", content: "It proves a complete matter action for the service medium." },
      { id: "broad_family", content: "It proves broad service-family viability across V2.5, V5, and V10." }
    ],
    answer: ["fixed_background", "watches"],
    explanation: {
      answer: "The careful scope is fixed-background evidence with visible watches.",
      why: "The current record distinguishes V5 prescribed-metric evidence from unproved matter-action, semiclassical, and broad-family claims. The right answer preserves the value of the evidence without letting it expand into unearned physical-realization language.",
      boundary: "This is revision-sensitive project-state content and must be excluded from stable general-theory or paper-theory sessions unless intentionally selected.",
      references: [],
      sourceLinks: [sources.projectReadme, sources.boundedSealReadiness, sources.serviceRatingLadder],
      openGate: "Matter-action closure, semiclassical response, and broad repeated-service robustness remain separate gates."
    }
  },
  {
    id: "design_review.evidence_sufficiency.002",
    type: "multi",
    track: "Design review and synthesis",
    module: "Evidence sufficiency",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    scoring: "subtract_incorrect",
    prompt: "A candidate shows clean live packet norm, improved source-family validation, and a passing local stress rung. Which missing items still block a full physical-realization claim?",
    choices: [
      { id: "matter_action", content: "A matter action or microphysical model that produces the required stress-energy." },
      { id: "semiclassical", content: "A semiclassical/RSET analysis when quantum-field effects are relevant." },
      { id: "packet_trace", content: "A packet trace, because the prompt already says the live packet norm is clean." },
      { id: "duplicate_trace", content: "Another copy of the already-clean packet trace." }
    ],
    answer: ["matter_action", "semiclassical"],
    explanation: {
      answer: "Matter action and semiclassical/RSET work remain missing for a full physical-realization claim.",
      why: "Packet-facing and fixed-background evidence can be strong while still falling short of physical source realization. The advanced move is to credit the passed diagnostics while naming the missing source-sector and quantum-field evidence.",
      boundary: "This is design-review reasoning inside the active-rail project model, not an established external certification rule.",
      references: [],
      sourceLinks: [sources.projectReadme, sources.boundedSealReadiness, sources.endpointSourceFamilyRung],
      openGate: "Physical-source realization remains open until the source sector is derived or otherwise physically justified."
    }
  }
];
