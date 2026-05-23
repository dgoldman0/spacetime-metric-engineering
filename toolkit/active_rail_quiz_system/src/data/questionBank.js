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
    prompt: "True or false: The Alcubierre warp metric is a published speculative spacetime model, not a demonstrated engineering construction.",
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
      boundary: "This is established constraint material applied to design interpretation.",
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
      why: "Active-rail qualification separates packet-facing success from plant burden, reset evidence, and source realization.",
      boundary: "This is active-rail design-review logic, not a general theorem of GR.",
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
    id: "constraints.qi_interpretation.001",
    type: "mc",
    track: "Established foundations",
    module: "Quantum inequalities",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "What is the safest interpretation of Ford-Roman quantum inequality constraints in warp or wormhole discussions?",
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
      boundary: "This is established constraint literature applied to speculative geometries.",
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
    prompt: "Which statements accurately describe the Barcelo-Visser result on non-minimally coupled scalar fields?",
    choices: [
      { id: "scalar_violation", content: "Non-minimally coupled scalar fields can violate standard energy conditions, including averaged null-energy conditions." },
      { id: "trans_planckian", content: "The traversable-wormhole branch carries a serious trans-Planckian field-value caveat." },
      { id: "plug_in", content: "It supplies an experimentally established material that can be inserted into any macroscopic wormhole geometry." },
      { id: "no_constraints", content: "It removes all energy-condition and quantum-gravity concerns." }
    ],
    answer: ["scalar_violation", "trans_planckian"],
    explanation: {
      answer: "The paper shows a scalar-field route to energy-condition violation while keeping the trans-Planckian caveat visible.",
      why: "The result is not simply 'scalar fields solve wormholes'; the field scale and physical interpretation remain central.",
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
    prompt: "What does the phrase zero expansion mean in Natario-style warp-drive literature?",
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
      boundary: "This is published speculative metric context.",
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
    prompt: "What is the disciplined use of topological censorship in traversable-wormhole discussions?",
    choices: [
      { id: "conditional_constraint", content: "It is a conditional theorem showing that, under suitable assumptions, nontrivial topology is hidden from causal observers." },
      { id: "algebraic_ban", content: "It is an algebraic ban on writing any wormhole metric." },
      { id: "all_sources_solved", content: "It proves every possible source-realization question is solved." },
      { id: "fictional", content: "It is only a narrative convention without mathematical content." }
    ],
    answer: ["conditional_constraint"],
    explanation: {
      answer: "Topological censorship is a conditional constraint theorem.",
      why: "Its force comes from its assumptions: energy, causality, asymptotic structure, and predictability conditions matter.",
      boundary: "This is established constraint material. It should be used carefully, not as a slogan.",
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
    prompt: "True or false: Chronology-protection arguments are best treated as serious causality constraints, not as completed engineering recipes.",
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
    prompt: "Which cautions are appropriate when interpreting an Alcubierre-style warp metric?",
    choices: [
      { id: "metric_not_engine", content: "A metric ansatz is not the same thing as a controlled physical engine." },
      { id: "source_demand", content: "The stress-energy demand and energy-condition behavior remain central." },
      { id: "automatic_control", content: "If the line element is smooth, a passenger can necessarily create, steer, and stop the bubble." },
      { id: "established_transport", content: "It is established transportation physics because it is a solution ansatz in GR." }
    ],
    answer: ["metric_not_engine", "source_demand"],
    explanation: {
      answer: "The metric is a valuable speculative model, but source demand and control questions remain central.",
      why: "Writing a spacetime geometry does not supply matter realization, stability, causal control, or operational protocols.",
      boundary: "This is published-literature interpretation with unresolved physical gates.",
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
    prompt: "In Clark-Hiscock-Larson's null-geodesic analysis, what causal feature appears for effective superluminal Alcubierre motion?",
    choices: [
      { id: "causal_access", content: "Horizon-like conical regions appear, limiting which signals can reach or be sent from the bubble." },
      { id: "complete_control", content: "A passenger at the bubble center can create, steer, and stop the bubble on demand." },
      { id: "no_quantum", content: "Null-geodesic behavior removes quantum-vacuum concerns." },
      { id: "flat_optics", content: "All photon paths remain indistinguishable from flat-space optics." }
    ],
    answer: ["causal_access"],
    explanation: {
      answer: "The paper identifies horizon-like conical access structures.",
      why: "For effective superluminal motion, the null-geodesic structure includes regions that block signals from reaching the bubble and regions the bubble cannot signal into.",
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
    prompt: "What does the Mueller-Weiskopf geodesic study emphasize about the Alcubierre spacetime?",
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
    prompt: "Which statements match Everett and Roman's analysis of Krasnikov tubes?",
    choices: [
      { id: "two_tubes", content: "A single directed tube is not the same chronology problem as a two-tube network arranged into a time-machine system." },
      { id: "negative_energy", content: "The construction still carries severe negative-energy and thin-layer concerns." },
      { id: "no_ctc", content: "Any number of superluminal tubes is chronology-safe once each tube is individually one-way." },
      { id: "source_solution", content: "The paper supplies a practical ordinary-matter source for constructing the tube." }
    ],
    answer: ["two_tubes", "negative_energy"],
    explanation: {
      answer: "Network composition and negative-energy burden are both central.",
      why: "Everett and Roman distinguish the single-tube case from a two-tube time-machine arrangement, while preserving severe source concerns.",
      boundary: "This is superluminal-spacetime literature, not demonstrated engineering.",
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
    prompt: "What does the Shoshany-Snodgrass two-warp construction demonstrate?",
    choices: [
      { id: "composition", content: "It gives a concrete GR model where composed warp-drive geometries yield a closed timelike geodesic." },
      { id: "safe", content: "It proves all warp-drive networks are chronology-safe when each leg is smooth." },
      { id: "matter", content: "It derives ordinary positive-energy matter that realizes the drives." },
      { id: "coordinates", content: "It shows closed timelike curves are only a coordinate-label issue." }
    ],
    answer: ["composition"],
    explanation: {
      answer: "It demonstrates that composed warp-drive geometries can create closed-timelike-curve structure.",
      why: "The paper supplies a concrete two-warp-drive model rather than leaving the timing issue as only a slogan.",
      boundary: "This is a published chronology result about warp-drive geometries, not a physical-realization claim.",
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
    prompt: "Which statements are careful takeaways from the Garattini-Zatrimaylov wormhole--warp-drive correspondence?",
    choices: [
      { id: "curvature", content: "The correspondence requires allowing nonzero intrinsic spatial curvature in the warp-drive metric." },
      { id: "traversability_caveat", content: "The paper reports a traversability caveat rather than a simple equivalence between comfortable wormholes and warp drives." },
      { id: "flat_shift", content: "Any flat-spatial-slice shift profile is automatically a Morris-Thorne wormhole." },
      { id: "realization", content: "The correspondence proves a physical matter source for a traversable warp-drive carrier." }
    ],
    answer: ["curvature", "traversability_caveat"],
    explanation: {
      answer: "The useful takeaways are intrinsic-curvature dependence and a nontrivial traversability caveat.",
      why: "The result is a constrained correspondence, not a statement that ordinary traversable wormholes and warp drives are interchangeable.",
      boundary: "This is published correspondence context and must not be promoted to engineering completion.",
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
    prompt: "What does the smeared-null-energy-condition literature add beyond a pointwise NEC check?",
    choices: [
      { id: "semilocal_bound", content: "It treats accumulated negative energy along smeared null probes as a semilocal constraint." },
      { id: "pointwise_only", content: "It says only the pointwise sign of one stress-tensor component matters." },
      { id: "construction", content: "It supplies a physical source construction for any prescribed negative-energy profile." },
      { id: "irrelevant", content: "It says pointwise energy-condition checks are the only relevant tests." }
    ],
    answer: ["semilocal_bound"],
    explanation: {
      answer: "The added lesson is semilocal accumulation: not just pointwise sign.",
      why: "The smeared NEC is a quantum-motivated bound on accumulated NEC violation along null probes.",
      boundary: "This is a constraint reference, not a construction recipe.",
      references: [references.smearedNec]
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
      boundary: "This is one of the core active-rail claim boundaries.",
      references: [references.carrollGrNotes],
      sourceLinks: [sources.componentSourceLedger, sources.technicalDisclosure],
      openGate: "A physical matter action, semiclassical stress tensor, or coupled Einstein-matter evolution remains a separate requirement."
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
      boundary: "This is active-rail service architecture, not established textbook terminology.",
      references: [],
      sourceLinks: [sources.serviceAlignedSchedule, sources.resetReleaseLadder]
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
      why: "Conflating these layers is how a narrow pass becomes an overclaim.",
      boundary: "This is project-state architecture and review taxonomy.",
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
      why: "The current record distinguishes V5 prescribed-metric evidence from unproved matter-action, semiclassical, and broad-family claims.",
      boundary: "This is revision-sensitive project-state content.",
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
      why: "Packet-facing and fixed-background evidence can be strong while still falling short of physical source realization.",
      boundary: "This is design-review reasoning inside the active-rail project model.",
      references: [],
      sourceLinks: [sources.projectReadme, sources.boundedSealReadiness, sources.endpointSourceFamilyRung],
      openGate: "Physical-source realization remains open until the source sector is derived or otherwise physically justified."
    }
  }
];
