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
    prompt: "An internal active-rail run ledger appears to report a candidate pass with clean packet safety but a thin support-closure margin. What is the safest status for that claim?",
    choices: [
      { id: "flagged", content: "Revision-sensitive project-state evidence that can guide review but should not be treated as established physics." },
      { id: "general", content: "A general result that can be applied to any active-rail geometry without qualification." },
      { id: "established", content: "An established theorem of general relativity because the ledger was computed from a metric." },
      { id: "complete", content: "A completed physical-source construction because packet safety was clean." }
    ],
    answer: ["flagged"],
    explanation: {
      answer: "It appears to be revision-sensitive project-state evidence.",
      why: "An apparently clean packet-safety result could be meaningful while support closure, source realization, or repeated-operation margins remain under review.",
      boundary: "This is provisional project-state interpretation, not an established physical theorem.",
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
    id: "foundation.extrinsic_curvature.002",
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
    prompt: "A current service-rating ladder appears to report that the V10 case fails live packet source safety. What is the safest interpretation?",
    choices: [
      { id: "boundary", content: "It appears to mark a high-service boundary for the current package and could motivate additional causal/source-margin work." },
      { id: "impossible", content: "It proves every possible high-service active-rail design is impossible." },
      { id: "solved", content: "It proves V10 is ready because failed diagnostics are only bookkeeping." },
      { id: "general_theorem", content: "It is an established theorem of GR independent of the project configuration." }
    ],
    answer: ["boundary"],
    explanation: {
      answer: "It appears to be a current-package high-service boundary, not a universal impossibility theorem.",
      why: "The reported failure could be meaningful project evidence about the present V10 ladder. The careful interpretation preserves that warning while avoiding an overclaim about all future high-service geometries or all possible source strategies.",
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
    prompt: "A report appears to describe the sealed beta075 V5 package as packet-safe with fixed-background endpoint/support and source-family evidence. Which scope statements are appropriate?",
    choices: [
      { id: "fixed_background", content: "It could be evidence at prescribed-metric or fixed-background effective-source level." },
      { id: "watches", content: "Thin margins and watch conditions should remain visible in the claim." },
      { id: "matter_action", content: "It proves a complete matter action for the service medium." },
      { id: "broad_family", content: "It proves broad service-family viability across V2.5, V5, and V10." }
    ],
    answer: ["fixed_background", "watches"],
    explanation: {
      answer: "The careful scope appears to be fixed-background evidence with visible watches.",
      why: "The current record appears to distinguish V5 prescribed-metric evidence from unproved matter-action, semiclassical, and broad-family claims. The right answer preserves the possible value of the evidence without letting it expand into unearned physical-realization language.",
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
    prompt: "A candidate appears to show clean live packet norm, improved source-family validation, and a passing local stress rung. Which missing items could still block a full physical-realization claim?",
    choices: [
      { id: "matter_action", content: "A matter action or microphysical model that produces the required stress-energy." },
      { id: "semiclassical", content: "A semiclassical/RSET analysis when quantum-field effects are relevant." },
      { id: "packet_trace", content: "A packet trace, because the prompt already says the live packet norm is clean." },
      { id: "duplicate_trace", content: "Another copy of the already-clean packet trace." }
    ],
    answer: ["matter_action", "semiclassical"],
    explanation: {
      answer: "Matter action and semiclassical/RSET work could remain missing for a full physical-realization claim.",
      why: "Packet-facing and fixed-background evidence can be strong while still falling short of physical source realization. The advanced move is to credit the apparently passed diagnostics while naming the missing source-sector and quantum-field evidence.",
      boundary: "This is design-review reasoning inside the active-rail project model, not an established external certification rule.",
      references: [],
      sourceLinks: [sources.projectReadme, sources.boundedSealReadiness, sources.endpointSourceFamilyRung],
      openGate: "Physical-source realization remains open until the source sector is derived or otherwise physically justified."
    }
  },
  {
    id: "foundation.metric_interval.002",
    type: "mc",
    track: "Established foundations",
    module: "Metric basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What does a spacetime metric primarily let you compute?",
    choices: [
      { id: "interval", content: "Intervals, causal character, and proper-time or proper-distance relations between nearby events." },
      { id: "matter_action", content: "A unique matter action that must physically realize any chosen geometry." },
      { id: "engineering_pass", content: "Whether a service plant has passed all endpoint reset checks." },
      { id: "publication_status", content: "Whether a speculative metric has become an engineering demonstration." }
    ],
    answer: ["interval"],
    explanation: {
      answer: "A metric encodes interval and causal-structure information.",
      why: "In GR the metric is the geometric field used to calculate line elements, causal character, proper time, and curvature. It does not by itself provide a matter model or an engineering qualification.",
      boundary: "This is established GR vocabulary; physical realization and service qualification are separate questions.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.causal_vectors.matching.002",
    type: "matching",
    track: "Established foundations",
    module: "Metric basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Match each causal class to the usual metric-signature statement for a nonzero vector in mostly-plus convention.",
    prompts: [
      { id: "timelike", content: "Timelike" },
      { id: "null", content: "Null" },
      { id: "spacelike", content: "Spacelike" }
    ],
    options: [
      { id: "negative_norm", label: "Negative squared norm" },
      { id: "zero_norm", label: "Zero squared norm" },
      { id: "positive_norm", label: "Positive squared norm" }
    ],
    answer: {
      timelike: "negative_norm",
      null: "zero_norm",
      spacelike: "positive_norm"
    },
    explanation: {
      answer: "Timelike is negative, null is zero, and spacelike is positive in mostly-plus convention.",
      why: "The sign convention must be stated, but once fixed it gives a compact way to separate causal directions. This distinction is basic machinery for later horizon, packet, and geodesic discussions.",
      boundary: "This is established notation practice, not a project-specific claim.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.stress_energy_observer.002",
    type: "multi",
    track: "Established foundations",
    module: "Stress-energy basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements correctly describe observer energy density in GR?",
    choices: [
      { id: "timelike_contraction", content: "For a timelike observer with four-velocity u, the measured energy density is represented by a contraction such as T_mn u^m u^n." },
      { id: "observer_dependent", content: "The measured density depends on the observer field as well as the stress-energy tensor." },
      { id: "trace_only", content: "It is always just the trace T^m_m." },
      { id: "geometry_alone", content: "It can be read from a metric name without computing stress-energy or an observer field." }
    ],
    answer: ["timelike_contraction", "observer_dependent"],
    explanation: {
      answer: "Observer density is a timelike contraction and depends on the observer field.",
      why: "The stress tensor contains more information than a single scalar. Energy density for an observer is obtained by contracting with that observer's timelike four-velocity, while traces and other components answer different questions.",
      boundary: "This is established stress-energy interpretation, not a service-specific diagnostic by itself.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.adm_hamiltonian.dragfill.001",
    type: "drag_fill",
    track: "Established foundations",
    module: "ADM constraints",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    promptParts: [
      "In standard ADM notation, the Hamiltonian constraint relates spatial curvature and extrinsic curvature to ",
      { type: "blank", id: "density" },
      "."
    ],
    tokens: [
      { id: "rho", content: [{ type: "math", latex: "\\rho", label: "rho" }] },
      { id: "beta", content: [{ type: "math", latex: "\\beta^i", label: "beta i" }] },
      { id: "alpha", content: [{ type: "math", latex: "\\alpha", label: "alpha" }] },
      { id: "trace_free", content: [{ type: "math", latex: "T^\\mu{}_{\\mu}=0", label: "trace equals zero" }] }
    ],
    blanks: [
      { id: "density", accepts: ["rho"] }
    ],
    explanation: {
      answer: [{ type: "math", latex: "\\rho", label: "rho" }],
      why: "In the ADM split, the Hamiltonian constraint is the normal-normal projection of Einstein's equation and contains the matter energy density seen by the slice normal.",
      boundary: "This is established ADM constraint structure; a project ledger may use it, but the vocabulary is not invented by the project.",
      references: [references.adm, references.carrollGrNotes]
    }
  },
  {
    id: "foundation.energy_condition.classification.002",
    type: "claim_classification",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "Classify each energy-condition and source-realization statement by the safest general status.",
    statuses: ["established_theory", "established_constraint", "literature_model", "open_gate"],
    statements: [
      { id: "nec_definition", content: "The null energy condition is formulated using stress-energy contracted with null vectors.", answer: "established_constraint" },
      { id: "warp_violation", content: "The Alcubierre 1994 warp model is associated with exotic stress-energy requirements.", answer: "literature_model" },
      { id: "einstein_equation", content: "Einstein's equation relates curvature to stress-energy.", answer: "established_theory" },
      { id: "realization", content: "A conventional matter sector realizes every prescribed exotic stress-energy tensor.", answer: "open_gate" }
    ],
    explanation: {
      answer: "NEC is an established constraint, Alcubierre exotic stress-energy is literature context, Einstein's equation is established theory, and universal exotic-source realization remains open.",
      why: "This classification prevents a common collapse: field equations, energy-condition constraints, speculative metric literature, and matter-realization claims are related but not the same kind of statement.",
      boundary: "This is general-theory claim-boundary training with no dependence on project state or architecture-specific vocabulary.",
      references: [references.carrollGrNotes, references.alcubierre]
    }
  },
  {
    id: "constraints.qi.duration.003",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Quantum inequalities",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Ford and Roman's 1996 paper \"Quantum Field Theory Constrains Traversable Wormhole Geometries,\" what is the key lesson for negative energy?",
    choices: [
      { id: "duration_magnitude", content: "Magnitude and duration of negative energy are constrained together, so sustained macroscopic violations are difficult." },
      { id: "unlimited", content: "Negative energy may be accumulated arbitrarily if the metric is smooth." },
      { id: "classical_only", content: "Quantum-field constraints are irrelevant to wormhole or warp discussions." },
      { id: "source_constructed", content: "The paper constructs an engineering-ready source for arbitrary traversable geometries." }
    ],
    answer: ["duration_magnitude"],
    explanation: {
      answer: "Ford-Roman constraints tie negative-energy magnitude to sampling duration.",
      why: "The qualitative lesson is not merely that negative energy appears, but that quantum inequalities restrict how much can persist for how long in the settings considered.",
      boundary: "This is constraint literature, not a proof that every speculative spacetime is impossible or buildable.",
      references: [references.fordRoman]
    }
  },
  {
    id: "constraints.qi.sampling.004",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Quantum inequalities",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "In the Ford-Roman 1996 quantum-inequality setting, which design cautions follow most directly?",
    choices: [
      { id: "sampling", content: "A local snapshot of negative energy is not enough; sampling time and accumulated exposure matter." },
      { id: "scale", content: "Macroscopic exotic geometries face stronger burden than a formal stress-tensor sign check alone suggests." },
      { id: "ignore", content: "Once a metric is named, quantum-field sampling restrictions disappear." },
      { id: "complete_source", content: "The inequality supplies the missing matter action for a chosen geometry." }
    ],
    answer: ["sampling", "scale"],
    explanation: {
      answer: "Sampling and scale cautions follow; source realization does not.",
      why: "The advanced point is that a negative-energy diagnosis must consider duration and scale, not only whether a pointwise algebraic condition can be written. The inequality constrains candidate sources; it does not construct them.",
      boundary: "This is a literature-backed constraint interpretation and should not be stretched into an all-purpose impossibility theorem.",
      references: [references.fordRoman]
    }
  },
  {
    id: "literature.alcubierre.local_global.003",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Alcubierre's 1994 paper \"The Warp Drive,\" what is the central contrast between the bubble interior and the global construction?",
    choices: [
      { id: "local_flat_global_exotic", content: "The passenger region can be locally mild while the global geometry requires exotic stress-energy in the wall." },
      { id: "flat_everywhere", content: "The whole spacetime is globally identical to Minkowski spacetime." },
      { id: "matter_action", content: "The paper derives a conventional matter action that realizes the bubble." },
      { id: "no_metric", content: "The paper does not propose a metric model." }
    ],
    answer: ["local_flat_global_exotic"],
    explanation: {
      answer: "The local passenger region and global source burden must be separated.",
      why: "Alcubierre's construction is famous partly because the bubble interior can be described gently while the surrounding geometry carries severe exotic-matter implications.",
      boundary: "This is published speculative metric analysis, not a demonstrated propulsion system.",
      references: [references.alcubierre]
    }
  },
  {
    id: "literature.alcubierre.exotic_matter.004",
    type: "tf",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "core",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "True or false: Alcubierre's 1994 warp-drive metric removes the need to examine stress-energy requirements.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["false"],
    explanation: {
      answer: "False.",
      why: "The stress-energy implications are central to interpreting the Alcubierre model. Naming the metric does not remove the source question.",
      boundary: "This is literature-model context and does not establish physical realizability.",
      references: [references.alcubierre]
    }
  },
  {
    id: "literature.natario.zero_expansion.003",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Natario's 2002 paper \"Warp Drive With Zero Expansion,\" what does the zero-expansion condition mainly show?",
    choices: [
      { id: "variant", content: "Warp-drive geometry can be reformulated so the expansion of the volume elements vanishes, while source concerns remain." },
      { id: "realized", content: "Zero expansion proves the source is ordinary laboratory matter." },
      { id: "flat", content: "Zero expansion makes the entire spacetime flat." },
      { id: "chronology_safe", content: "Zero expansion proves global chronology protection." }
    ],
    answer: ["variant"],
    explanation: {
      answer: "It shows an important geometric variant, not physical source realization.",
      why: "Natario's construction changes a geometric feature of the warp-drive class. The existence of a zero-expansion construction does not erase energy-condition or matter-sector questions.",
      boundary: "This is published metric-geometry context and must stay distinct from engineering feasibility.",
      references: [references.natario]
    }
  },
  {
    id: "literature.natario.lesson.004",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which lessons are appropriate to draw from Natario's 2002 zero-expansion warp-drive construction?",
    choices: [
      { id: "geometry_family", content: "There is more than one way to formulate warp-drive-like geometry." },
      { id: "source_still_matters", content: "Changing expansion properties does not by itself solve the source-realization problem." },
      { id: "ordinary_matter", content: "Zero expansion guarantees ordinary positive-energy matter everywhere." },
      { id: "no_causality", content: "It makes causal-structure analysis unnecessary." }
    ],
    answer: ["geometry_family", "source_still_matters"],
    explanation: {
      answer: "The construction broadens the geometry family while preserving the need for source and causal analysis.",
      why: "A strong reading notices both sides: Natario provides a meaningful alternative warp geometry, but the result is not a license to ignore stress-energy or global behavior.",
      boundary: "This is speculative literature interpretation, not a completed matter model or engineering feasibility claim.",
      references: [references.natario]
    }
  },
  {
    id: "literature.chl.horizon_cones.003",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Clark, Hiscock, and Larson's 1999 paper \"Null Geodesics in the Alcubierre Warp Drive Spacetime,\" what issue is highlighted for superluminal bubbles?",
    choices: [
      { id: "horizon", content: "Null rays reveal horizon-like access structures that affect signaling and control assumptions." },
      { id: "no_light", content: "Light rays cannot be discussed in the Alcubierre geometry." },
      { id: "ordinary_control", content: "A passenger at the center can always control the front wall by ordinary signals." },
      { id: "source_done", content: "Null geodesics construct the stress-energy source." }
    ],
    answer: ["horizon"],
    explanation: {
      answer: "The null-geodesic analysis exposes horizon-like signaling limitations.",
      why: "The paper is valuable because it turns a geometric model into a causal-access problem. Superluminal operation cannot assume that every part of the bubble is controllable by ordinary internal signaling.",
      boundary: "This is literature-model analysis of Alcubierre geometry, not a design-architecture result.",
      references: [references.clarkHiscockLarson]
    }
  },
  {
    id: "literature.chl.signal_reach.004",
    type: "tf",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "core",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "True or false: Clark, Hiscock, and Larson's 1999 null-geodesic analysis makes signal reachability a central concern for Alcubierre bubbles.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["true"],
    explanation: {
      answer: "True.",
      why: "Null geodesics are the natural tool for studying lightlike signal paths, so their behavior directly informs reachability and horizon-like limitations.",
      boundary: "This is a published analysis of a speculative metric, not proof of a controllable craft.",
      references: [references.clarkHiscockLarson]
    }
  },
  {
    id: "literature.muller_weiskopf.educational.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "core",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Mueller and Weiskopf's 2012 paper \"Detailed study of null and time-like geodesics in the Alcubierre Warp spacetime,\" why are geodesics useful?",
    choices: [
      { id: "probe_paths", content: "They probe possible lightlike and massive-particle paths through the modeled spacetime." },
      { id: "source_action", content: "They provide a matter action that realizes the warp bubble." },
      { id: "energy_condition", content: "They replace stress-energy and energy-condition analysis." },
      { id: "no_geometry", content: "They avoid using the metric." }
    ],
    answer: ["probe_paths"],
    explanation: {
      answer: "Geodesics probe trajectories in the modeled geometry.",
      why: "Null and timelike geodesics are diagnostic tools for how light and massive probes behave in a spacetime. They do not by themselves solve the source-realization problem.",
      boundary: "This is published model analysis and should be taught with physical-feasibility caveats.",
      references: [references.mullerWeiskopf]
    }
  },
  {
    id: "literature.muller_weiskopf.lensing.003",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "What should a careful reader take from Mueller and Weiskopf's 2012 geodesic study of the Alcubierre spacetime?",
    choices: [
      { id: "visual_diagnostic", content: "Geodesic behavior can reveal optical and observer-facing consequences of the geometry." },
      { id: "not_realization", content: "Trajectory analysis remains separate from matter-sector realization." },
      { id: "ordinary_source", content: "A detailed geodesic study proves ordinary matter can create the spacetime." },
      { id: "no_causal_limits", content: "If geodesics can be plotted, causal restrictions no longer matter." }
    ],
    answer: ["visual_diagnostic", "not_realization"],
    explanation: {
      answer: "The study is a diagnostic of paths and observations, not a realization proof.",
      why: "Advanced interpretation keeps the geodesic result in its lane: it enriches understanding of how the model behaves, but it does not certify sources, quantum stability, or engineering control.",
      boundary: "This is literature-model analysis with educational value and explicit feasibility and source-realization limits.",
      references: [references.mullerWeiskopf]
    }
  },
  {
    id: "literature.everett_roman.control.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Everett and Roman's 1997 paper \"A Superluminal Subway: The Krasnikov Tube,\" what is one reason the construction is relevant to chronology discussions?",
    choices: [
      { id: "two_tube", content: "Arrangements of superluminal tubes can raise closed-timelike-curve concerns." },
      { id: "no_negative", content: "It eliminates negative-energy concerns from superluminal travel." },
      { id: "ordinary_train", content: "It is an engineering design for an ordinary railway." },
      { id: "adm_constraint", content: "It replaces the ADM constraints with Newtonian mechanics." }
    ],
    answer: ["two_tube"],
    explanation: {
      answer: "Krasnikov-tube arrangements are relevant because they can raise CTC concerns.",
      why: "The paper connects superluminal travel geometries with causal-loop worries, while also keeping negative-energy and feasibility questions in view.",
      boundary: "This is published speculative-spacetime literature, not a demonstrated transportation system.",
      references: [references.everettRoman]
    }
  },
  {
    id: "literature.everett_roman.negative_energy.003",
    type: "tf",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "True or false: Everett and Roman's 1997 Krasnikov-tube analysis removes the need to worry about negative energy.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["false"],
    explanation: {
      answer: "False.",
      why: "The Krasnikov-tube context is tied to exotic stress-energy and quantum-inequality concerns. It is not a free pass around source constraints.",
      boundary: "This is a literature caution about speculative superluminal geometries, not a practical source construction.",
      references: [references.everettRoman, references.fordRoman]
    }
  },
  {
    id: "literature.shoshany_snodgrass.frame_switch.003",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Shoshany and Snodgrass's 2024 paper \"Warp Drives and Closed Timelike Curves,\" what is the central chronology lesson?",
    choices: [
      { id: "ctg", content: "Combinations of warp-drive regions can permit closed timelike geodesics in the model under the analyzed conditions." },
      { id: "safe", content: "Any single warp metric automatically forbids all closed causal curves in every arrangement." },
      { id: "ordinary_matter", content: "Closed timelike curves appear only after the weak energy condition is restored everywhere." },
      { id: "irrelevant", content: "Chronology is unrelated to superluminal metric constructions." }
    ],
    answer: ["ctg"],
    explanation: {
      answer: "The analyzed multi-warp arrangement can produce closed timelike geodesics.",
      why: "The advanced point is compositional: causal risk can arise from how superluminal regions are arranged, not just from reading one local metric patch in isolation.",
      boundary: "This is a published model result and chronology warning, not a project-specific service result.",
      references: [references.shoshanySnodgrass]
    }
  },
  {
    id: "literature.garattini_zatrimaylov.no_free_transfer.003",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp-wormhole correspondence",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "In Garattini and Zatrimaylov's 2024 paper \"On the Wormhole--Warp Drive Correspondence,\" which interpretations are careful?",
    choices: [
      { id: "correspondence", content: "The paper explores a formal correspondence between wormhole and warp-drive geometries." },
      { id: "caveats", content: "A correspondence does not automatically supply traversability, ordinary matter, or engineering control." },
      { id: "solved", content: "The correspondence proves warp drives can be built from ordinary matter." },
      { id: "no_geometry", content: "The correspondence makes intrinsic curvature irrelevant." }
    ],
    answer: ["correspondence", "caveats"],
    explanation: {
      answer: "The formal correspondence is useful but bounded by traversability and source caveats.",
      why: "The careful reading gains conceptual transfer between geometry families without treating that transfer as a proof of physical realization, traversability, stable sourcing, or operational control.",
      boundary: "This is recent literature-model context, not an established engineering result or source-realization proof.",
      references: [references.garattiniZatrimaylov]
    }
  },
  {
    id: "literature.barcelo_visser.scalar.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Scalar-source literature",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Barcelo and Visser's 2000 paper \"Scalar Fields, Energy Conditions, and Traversable Wormholes,\" what is the main source-sector lesson?",
    choices: [
      { id: "nonminimal", content: "Non-minimally coupled scalar fields can alter energy-condition behavior, but with important physical caveats." },
      { id: "universal", content: "Any scalar field automatically gives a safe traversable wormhole." },
      { id: "no_energy", content: "Energy conditions are irrelevant once a scalar field is named." },
      { id: "engineering_specific", content: "The paper analyzes a particular endpoint reset architecture." }
    ],
    answer: ["nonminimal"],
    explanation: {
      answer: "Non-minimal scalar coupling can change energy-condition behavior, but caveats matter.",
      why: "The paper is useful because it explores source-sector possibilities rather than merely prescribing a metric. The lesson is nuanced: altered energy conditions do not automatically equal practical or benign matter.",
      boundary: "This is scalar-field literature context and should not be confused with any architecture-specific source closure.",
      references: [references.barceloVisser]
    }
  },
  {
    id: "constraints.topological_censorship.curves.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Topological censorship",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Friedman, Schleich, and Witt's 1993 paper \"Topological Censorship,\" what is the broad lesson for visible nontrivial topology?",
    choices: [
      { id: "screened", content: "Under suitable assumptions, causal curves from infinity cannot probe nontrivial topology in the naive traversable way." },
      { id: "guaranteed", content: "All wormhole-like topology is automatically traversable by external observers." },
      { id: "no_assumptions", content: "The result needs no causal or energy assumptions." },
      { id: "warp_source", content: "It supplies stress-energy for warp-drive walls." }
    ],
    answer: ["screened"],
    explanation: {
      answer: "The theorem constrains externally visible traversal of nontrivial topology under its assumptions.",
      why: "The result is powerful because it ties global topology, causal structure, and energy conditions together. The assumptions matter, so the correct interpretation is constrained rather than slogan-like.",
      boundary: "This is established constraint literature under stated assumptions, not a project-specific geometry verdict.",
      references: [references.topologicalCensorship]
    }
  },
  {
    id: "constraints.visser_chronology.protection.003",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "In Visser's 2002 review \"The quantum physics of chronology protection,\" which cautions are appropriate?",
    choices: [
      { id: "backreaction", content: "Quantum-field backreaction near chronology horizons is a central concern." },
      { id: "open", content: "Chronology protection is a serious constraint topic, not a solved engineering recipe." },
      { id: "ignore", content: "Closed causal curves can be ignored if a metric is smooth." },
      { id: "complete", content: "The review provides a complete safe construction for time-machine operation." }
    ],
    answer: ["backreaction", "open"],
    explanation: {
      answer: "Backreaction and unresolved chronology-protection issues are the right cautions.",
      why: "The review frames chronology protection as a deep quantum-field and causal-structure problem. It does not license smooth metrics to bypass closed-curve concerns.",
      boundary: "This is constraint-review context, not a project qualification rule by itself.",
      references: [references.chronologyProtection]
    }
  },
  {
    id: "constraints.snec.scope.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Quantum inequalities",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Moghtaderi, Hull, Quintin, and Geshnizjani's 2025 smeared-NEC paper, what is the main constraint style?",
    choices: [
      { id: "semilocal", content: "It constrains accumulated NEC violation over a smeared region rather than only a pointwise sign." },
      { id: "unrestricted", content: "It allows arbitrary accumulated NEC breaking if each point is small." },
      { id: "matter_action", content: "It constructs a matter action for every warp or wormhole geometry." },
      { id: "project_reset", content: "It validates a specific engineering reset schedule." }
    ],
    answer: ["semilocal"],
    explanation: {
      answer: "The smeared NEC constrains accumulated violation over a finite sampling region.",
      why: "The important distinction is semilocal: pointwise energy-condition violation is not the whole story when a constraint integrates or smears exposure across a region and sampling scale.",
      boundary: "This is recent constraint literature and should be applied cautiously outside the assumptions of the paper.",
      references: [references.smearedNec]
    }
  },
  {
    id: "active_rail.packet_plant.matching.002",
    type: "matching",
    track: "Active-rail architecture",
    module: "Architecture overview",
    difficulty: "core",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "Match each active-rail term to its role in the service model.",
    prompts: [
      { id: "packet", content: "Packet" },
      { id: "rail", content: "Rail" },
      { id: "endpoint", content: "Endpoint" },
      { id: "reset", content: "Reset" }
    ],
    options: [
      { id: "served_region", label: "Passenger-facing served region" },
      { id: "prepared_infrastructure", label: "Prepared support/carry/handoff infrastructure" },
      { id: "handoff_region", label: "Region responsible for catch or rematch boundary work" },
      { id: "reuse_check", label: "Post-service residue and readiness process" }
    ],
    answer: {
      packet: "served_region",
      rail: "prepared_infrastructure",
      endpoint: "handoff_region",
      reset: "reuse_check"
    },
    explanation: {
      answer: "Packet is served region, rail is infrastructure, endpoint handles handoff, and reset handles post-service readiness.",
      why: "The terms are useful only if they keep responsibilities separated. Packet success, rail burden, endpoint handoff, and reset evidence are different surfaces.",
      boundary: "These are active-rail model roles, not established GR vocabulary.",
      references: [],
      sourceLinks: [sources.technicalDisclosure, sources.serviceAlignedSchedule]
    }
  },
  {
    id: "active_rail.source_demand.dragfill.002",
    type: "drag_fill",
    track: "Active-rail architecture",
    module: "Source ledger",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: [],
    promptParts: [
      "A demanded-source ledger is strongest when it is read as ",
      { type: "blank", id: "claim" },
      ", not as automatic matter realization."
    ],
    tokens: [
      { id: "source_accounting", content: "source-demand accounting" },
      { id: "matter_action", content: "a completed matter action" },
      { id: "causal_proof", content: "a global causal-safety proof" },
      { id: "chronology_solution", content: "a chronology-protection solution" }
    ],
    blanks: [
      { id: "claim", accepts: ["source_accounting"] }
    ],
    explanation: {
      answer: "source-demand accounting",
      why: "The ledger is a disciplined way to say what the prescribed metric asks the source sector to supply. It does not explain what matter dynamics produce that stress-energy.",
      boundary: "This is active-rail source bookkeeping with an explicit physical-realization boundary.",
      references: [references.carrollGrNotes],
      sourceLinks: [sources.componentSourceLedger],
      openGate: "A physical source model remains a separate gate."
    }
  },
  {
    id: "active_rail.service_chronology.sequence.004",
    type: "sequence",
    track: "Active-rail architecture",
    module: "Service chronology",
    difficulty: "core",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "Order the compact active-rail service verbs.",
    items: [
      { id: "support", content: "Support" },
      { id: "carry", content: "Carry" },
      { id: "catch", content: "Catch" },
      { id: "fade", content: "Fade" },
      { id: "reset", content: "Reset" }
    ],
    answer: ["support", "carry", "catch", "fade", "reset"],
    explanation: {
      answer: "Support, carry, catch, fade, reset.",
      why: "The compressed sequence keeps the same service logic: prepare support before transport, catch before fading active carry, and treat reset as post-service readiness work.",
      boundary: "This is active-rail operational vocabulary, not textbook GR chronology.",
      references: [],
      sourceLinks: [sources.serviceAlignedSchedule, sources.resetReleaseLadder]
    }
  },
  {
    id: "active_rail.evidence_stack.sequence.006",
    type: "sequence",
    track: "Design review and synthesis",
    module: "Evidence sufficiency",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    prompt: "Order these evidence layers from weakest to strongest for an active-rail physical-realization claim.",
    items: [
      { id: "metric", content: "Prescribed metric with intended service behavior" },
      { id: "ledger", content: "Demanded-source ledger for the prescribed metric" },
      { id: "diagnostics", content: "Packet, support, endpoint, and reset diagnostics" },
      { id: "source_family", content: "Candidate source-family validation with watch conditions" },
      { id: "matter_action", content: "Matter action or microphysical source model coupled to the geometry" }
    ],
    answer: ["metric", "ledger", "diagnostics", "source_family", "matter_action"],
    explanation: {
      answer: "Metric, ledger, diagnostics, source-family validation, matter action.",
      why: "The ordering separates design intent, source demand, operational diagnostics, candidate source organization, and stronger physical-source evidence. Later layers do not erase the need to preserve watches from earlier layers.",
      boundary: "This is active-rail design-review ordering, with matter-action or microphysical-source closure still treated as an open gate.",
      references: [references.carrollGrNotes],
      sourceLinks: [sources.technicalDisclosure, sources.componentSourceLedger, sources.sourceFamilyValidation],
      openGate: "A coupled source model remains the high bar for physical-realization claims."
    }
  },
  {
    id: "active_rail.endpoint_handoff.001",
    type: "multi",
    track: "Active-rail architecture",
    module: "Service chronology",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements correctly describe the endpoint handoff burden in the active-rail model?",
    choices: [
      { id: "before_fade", content: "Catch or rematch should be established before release/fade removes active support." },
      { id: "separate_surface", content: "Endpoint evidence is distinct from merely seeing the packet arrive." },
      { id: "irrelevant", content: "Endpoint behavior is irrelevant once the initial support condition is named." },
      { id: "textbook", content: "Endpoint handoff is an established ADM theorem." }
    ],
    answer: ["before_fade", "separate_surface"],
    explanation: {
      answer: "Endpoint handoff must precede fade and remains a separate evidence surface.",
      why: "A service pass can fail at the handoff even if the beginning looked well prepared. The review should ask whether support is transferred or released in the intended order.",
      boundary: "This is active-rail architecture and should not be described as established ADM theory.",
      references: [],
      sourceLinks: [sources.serviceAlignedSchedule, sources.resetReleaseLadder]
    }
  },
  {
    id: "design_review.missing_channels.003",
    type: "multi",
    track: "Design review and synthesis",
    module: "Failure analysis",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    scoring: "subtract_incorrect",
    prompt: "A candidate report shows a clean packet path but omits support-edge stress, angular-sector pressure, endpoint rematch, and reset history. Which review findings are justified?",
    choices: [
      { id: "partial", content: "The packet result is useful but only partial." },
      { id: "missing", content: "The omitted plant channels block a full service qualification." },
      { id: "full", content: "Clean packet path alone proves full plant readiness." },
      { id: "ignore", content: "Angular and reset channels are decorative once the packet path is clean." }
    ],
    answer: ["partial", "missing"],
    explanation: {
      answer: "The result is partial, and missing plant channels block full qualification.",
      why: "Design review must credit the clean packet evidence without letting it hide unexamined burden channels. Support edge, angular sector, endpoint rematch, and reset history are not interchangeable with final packet arrival.",
      boundary: "This is active-rail review logic with open project gates, not an external theorem.",
      references: [],
      sourceLinks: [sources.boundedSealReadiness, sources.serviceRatingLadder],
      openGate: "Plant-channel closure remains open until those diagnostics are supplied."
    }
  },
  {
    id: "design_review.packet_arrival.003",
    type: "mc",
    track: "Design review and synthesis",
    module: "Evidence sufficiency",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: [],
    prompt: "A packet arrives within tolerance, but no source ledger or reset audit is provided. What is the strongest justified conclusion?",
    choices: [
      { id: "packet_only", content: "Packet-facing behavior passed one check, while source and reset claims remain unsupported." },
      { id: "all_done", content: "The full active-rail plant is qualified." },
      { id: "source_done", content: "The demanded stress-energy has been physically realized." },
      { id: "chronology_safe", content: "Global chronology safety has been established." }
    ],
    answer: ["packet_only"],
    explanation: {
      answer: "Only the packet-facing check is supported.",
      why: "One successful observable can matter without carrying every other claim. Source accounting, physical realization, reset readiness, and global causal safety are different evidentiary layers.",
      boundary: "This is project-application review reasoning, not a general certification rule.",
      references: [],
      sourceLinks: [sources.technicalDisclosure, sources.resetReleaseLadder]
    }
  },
  {
    id: "project_state.v5_watch.002",
    type: "mc",
    track: "Design review and synthesis",
    module: "Project-state handling",
    difficulty: "advanced",
    claimStatus: "project_hypothesis",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    prompt: "A current V5 sealed package is described as appearing to pass bounded fixed-background checks with watch conditions. What is the most careful interpretation?",
    choices: [
      { id: "bounded", content: "It appears to be bounded project evidence for the current fixed-background package, with watches still part of the claim." },
      { id: "universal", content: "It proves broad physical realization for all active-rail families." },
      { id: "no_watches", content: "Passing checks erase watch conditions from the review record." },
      { id: "external_theorem", content: "It is now an established theorem independent of the project model." }
    ],
    answer: ["bounded"],
    explanation: {
      answer: "The careful interpretation is apparent bounded project evidence with visible watches.",
      why: "An apparent pass in the current package could be meaningful, but its strength depends on the tested scope. Treating watches as part of the claim protects against overpromoting fixed-background evidence.",
      boundary: "This is revision-sensitive project-state material and should stay excludable from stable theory sessions.",
      references: [],
      sourceLinks: [sources.boundedSealReadiness, sources.serviceRatingLadder],
      openGate: "Broader family robustness and matter-sector closure remain separate gates."
    }
  },
  {
    id: "project_state.v10_boundary.003",
    type: "tf",
    track: "Design review and synthesis",
    module: "Project-state handling",
    difficulty: "advanced",
    claimStatus: "project_hypothesis",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    prompt: "True or false: A current V10 source-safety failure appears best reported as a project-state boundary rather than hidden behind the apparently successful lower-service cases.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["true"],
    explanation: {
      answer: "True.",
      why: "A higher-service failure can be informative even when lower-service cases look better. Hiding that boundary would distort the service envelope and make later promotion decisions less trustworthy.",
      boundary: "This is current project-state interpretation with revision-sensitive scope, not established external theory.",
      references: [],
      sourceLinks: [sources.serviceRatingLadder, sources.projectReadme],
      openGate: "Additional source safety and causal-margin work would be needed before stronger V10 claims."
    }
  },
  {
    id: "active_rail.claim_boundary.classification.004",
    type: "claim_classification",
    track: "Design review and synthesis",
    module: "Claim classification",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    prompt: "Classify each service-readiness statement by safest status.",
    statuses: ["established_theory", "established_constraint", "literature_model", "active_rail_model", "project_hypothesis", "open_gate"],
    statements: [
      { id: "adm_split", content: "The ADM split distinguishes lapse, shift, spatial metric, and constraints.", answer: "established_theory" },
      { id: "qi_constraint", content: "Quantum-inequality literature constrains some negative-energy configurations.", answer: "established_constraint" },
      { id: "alcubierre_metric", content: "The Alcubierre metric is a published speculative warp-drive model.", answer: "literature_model" },
      { id: "service_stack", content: "Support, carry, catch, fade, decompression, and reset are active-rail service stages.", answer: "active_rail_model" },
      { id: "bounded_scope", content: "A fixed-background package could be a candidate bounded evidence point with watch conditions.", answer: "project_hypothesis" },
      { id: "matter_sector", content: "A complete repeated-service matter sector has been derived.", answer: "open_gate" }
    ],
    explanation: {
      answer: "The statements span established theory, established constraints, published models, active-rail architecture, provisional project hypothesis, and open gate.",
      why: "Advanced review often fails by promoting every useful statement to the same status. The correct classification keeps source constraints, metric literature, project architecture, and unresolved realization separate.",
      boundary: "This is a mixed project-application item and must remain selectable by claim/status context.",
      references: [references.adm, references.fordRoman, references.alcubierre],
      sourceLinks: [sources.technicalDisclosure, sources.boundedSealReadiness],
      openGate: "The matter-sector statement remains open unless separately demonstrated."
    }
  },
  {
    id: "foundation.metric_signature.003",
    type: "mc",
    track: "Established foundations",
    module: "Metric basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why does the metric signature matter when classifying vectors?",
    choices: [
      { id: "signs", content: "It fixes which sign corresponds to timelike, null, and spacelike squared norms." },
      { id: "matter", content: "It determines the unique matter action for any geometry." },
      { id: "coordinate", content: "It removes the need to state coordinates." },
      { id: "source", content: "It proves whether an exotic source is physically available." }
    ],
    answer: ["signs"],
    explanation: {
      answer: "The signature sets the sign convention for causal classification.",
      why: "A timelike vector has one sign in mostly-plus convention and the opposite sign in mostly-minus convention. The causal class is invariant, but the written inequality depends on convention.",
      boundary: "This is established differential-geometry vocabulary used in GR, not a project-specific diagnostic.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.line_element.dragfill.003",
    type: "drag_fill",
    track: "Established foundations",
    module: "Metric basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    promptParts: [
      "The line element is commonly written as ",
      { type: "blank", id: "line_element" },
      "."
    ],
    tokens: [
      { id: "metric_line", content: [{ type: "math", latex: "ds^2=g_{\\mu\\nu}dx^\\mu dx^\\nu", label: "ds squared equals g mu nu dx mu dx nu" }] },
      { id: "einstein_eq", content: [{ type: "math", latex: "G_{\\mu\\nu}=8\\pi T_{\\mu\\nu}", label: "Einstein equation" }] },
      { id: "nec", content: [{ type: "math", latex: "T_{\\mu\\nu}k^\\mu k^\\nu\\ge 0", label: "null energy condition" }] },
      { id: "trace", content: [{ type: "math", latex: "T^\\mu{}_{\\mu}", label: "stress tensor trace" }] }
    ],
    blanks: [
      { id: "line_element", accepts: ["metric_line"] }
    ],
    explanation: {
      answer: [{ type: "math", latex: "ds^2=g_{\\mu\\nu}dx^\\mu dx^\\nu", label: "line element" }],
      why: "The metric turns coordinate differentials into an invariant interval. The other tokens are related GR expressions, but they are not the line element.",
      boundary: "This is established GR notation and does not assert any particular source model.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.geodesic.principle.001",
    type: "mc",
    track: "Established foundations",
    module: "Geodesics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What is a geodesic in GR, at the basic conceptual level?",
    choices: [
      { id: "free_fall", content: "A path followed by an ideal freely falling test body or light ray, depending on causal type." },
      { id: "force", content: "A path that requires a continuous non-gravitational force by definition." },
      { id: "source", content: "A stress-energy tensor that realizes a metric." },
      { id: "coordinate", content: "A coordinate grid line in every coordinate system." }
    ],
    answer: ["free_fall"],
    explanation: {
      answer: "A geodesic is the free-fall or lightlike path determined by the geometry.",
      why: "Timelike geodesics model ideal massive test-particle free fall, while null geodesics model ideal light rays. Coordinate grid lines need not be geodesics.",
      boundary: "This is established GR kinematics, separate from whether a chosen geometry has a physical source.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.geodesic.nonforce.002",
    type: "multi",
    track: "Established foundations",
    module: "Geodesics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements about geodesics are careful?",
    choices: [
      { id: "test_body", content: "They are test-path diagnostics of a geometry." },
      { id: "not_source", content: "They do not by themselves construct the stress-energy source of the geometry." },
      { id: "always_safe", content: "If geodesics can be drawn, global causal safety is guaranteed." },
      { id: "coordinate_lines", content: "Every coordinate line is automatically a geodesic." }
    ],
    answer: ["test_body", "not_source"],
    explanation: {
      answer: "Geodesics diagnose motion in a geometry, but they are not source construction.",
      why: "A geodesic analysis can reveal important behavior of probes and light, yet it leaves stress-energy, energy conditions, and global causal structure as separate questions.",
      boundary: "This is established GR interpretation and should not be inflated into physical-realization evidence.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.curvature.matching.001",
    type: "matching",
    track: "Established foundations",
    module: "Metric basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Match each geometric object to its role.",
    prompts: [
      { id: "metric", content: [{ type: "math", latex: "g_{\\mu\\nu}", label: "metric" }] },
      { id: "connection", content: [{ type: "math", latex: "\\Gamma^\\rho{}_{\\mu\\nu}", label: "Christoffel symbol" }] },
      { id: "einstein", content: [{ type: "math", latex: "G_{\\mu\\nu}", label: "Einstein tensor" }] }
    ],
    options: [
      { id: "intervals", label: "Encodes intervals and causal structure" },
      { id: "derivative", label: "Connection coefficients used in covariant derivatives" },
      { id: "curvature_combo", label: "Curvature combination appearing in Einstein's equation" }
    ],
    answer: {
      metric: "intervals",
      connection: "derivative",
      einstein: "curvature_combo"
    },
    explanation: {
      answer: "The metric encodes intervals, the connection supports covariant differentiation, and the Einstein tensor is the curvature side of Einstein's equation.",
      why: "Keeping these roles separate prevents a common confusion between geometry, derivative machinery, and source-demand equations.",
      boundary: "This is established GR structure, not tied to any one speculative metric.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.curvature_to_source.sequence.001",
    type: "sequence",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Order the usual geometry-to-source calculation for a prescribed metric.",
    items: [
      { id: "metric", content: "Specify the metric components" },
      { id: "connection", content: "Compute connection coefficients" },
      { id: "curvature", content: "Compute curvature tensors" },
      { id: "einstein", content: "Form the Einstein tensor" },
      { id: "stress", content: "Infer the demanded stress-energy through Einstein's equation" }
    ],
    answer: ["metric", "connection", "curvature", "einstein", "stress"],
    explanation: {
      answer: "Metric, connection, curvature, Einstein tensor, demanded stress-energy.",
      why: "The sequence follows the mathematical dependency chain. It can identify what stress-energy a metric demands, while leaving physical matter realization as a further step.",
      boundary: "This is established GR calculation logic; demanded stress-energy is not automatically a source model.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.bianchi.conservation.001",
    type: "mc",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why does the contracted Bianchi identity matter for Einstein's equation?",
    choices: [
      { id: "conservation", content: "It is tied to covariant conservation of the stress-energy tensor when Einstein's equation holds." },
      { id: "source_anything", content: "It proves any arbitrary stress tensor can be supplied by ordinary matter." },
      { id: "coordinates", content: "It removes the need to choose coordinates for calculations." },
      { id: "energy_positive", content: "It guarantees positive energy density for all observers." }
    ],
    answer: ["conservation"],
    explanation: {
      answer: "The Bianchi identity underlies covariant stress-energy conservation in Einstein's equation.",
      why: "Because the Einstein tensor has vanishing covariant divergence, the source side must satisfy the corresponding conservation law. This is a consistency condition, not a guarantee of benign matter.",
      boundary: "This is established GR structure and does not solve source-realization or energy-condition questions.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.pressure_components.001",
    type: "mc",
    track: "Established foundations",
    module: "Stress-energy basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In a stress-energy tensor, why can pressure or stress components matter as much as energy density?",
    choices: [
      { id: "tensor", content: "Einstein's equation couples the geometry to the full tensor, not only to one scalar density." },
      { id: "ignore", content: "Pressure components are coordinate decoration with no gravitational role." },
      { id: "always_zero", content: "Pressure components vanish in every relativistic source." },
      { id: "packet_only", content: "Only the final trajectory of a test packet determines the source." }
    ],
    answer: ["tensor"],
    explanation: {
      answer: "The full stress-energy tensor matters.",
      why: "Energy density, flux, and stresses can all contribute to the source side of Einstein's equation. Reducing the source to one scalar can hide important burdens.",
      boundary: "This is established stress-energy reasoning, not a project-specific bookkeeping preference.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.energy_conditions.limits.003",
    type: "multi",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements correctly describe the role and limits of classical energy conditions?",
    choices: [
      { id: "diagnostic", content: "They diagnose whether a stress-energy tensor satisfies selected positivity-style constraints." },
      { id: "not_complete", content: "Passing one condition is not a complete proof of physical source realizability." },
      { id: "all_matter", content: "They classify all quantum and classical matter behavior without exceptions or assumptions." },
      { id: "metric_name", content: "They can be decided from a metric's nickname without evaluating stress-energy." }
    ],
    answer: ["diagnostic", "not_complete"],
    explanation: {
      answer: "Energy conditions are diagnostic constraints, not complete physical-source certification.",
      why: "They are powerful because they encode useful positivity assumptions, but different conditions test different contractions and can fail or require reinterpretation in quantum or effective settings.",
      boundary: "This is established constraint reasoning; it must be applied with assumptions visible.",
      references: [references.carrollGrNotes, references.fordRoman]
    }
  },
  {
    id: "foundation.nec_wec.relationship.001",
    type: "mc",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "What is a careful way to distinguish the NEC from the WEC?",
    choices: [
      { id: "vectors", content: "NEC tests null-vector contractions, while WEC tests timelike-observer energy density." },
      { id: "same", content: "They are the same condition with different names." },
      { id: "trace", content: "Both are only statements about the trace of the stress tensor." },
      { id: "metric_only", content: "Both can be checked without referring to stress-energy." }
    ],
    answer: ["vectors"],
    explanation: {
      answer: "NEC is null-contraction based; WEC is timelike-observer based.",
      why: "The difference matters because null and timelike probes test different aspects of the stress tensor. Confusing them can make source diagnostics look cleaner than they are.",
      boundary: "This is established energy-condition vocabulary and not tied to one project architecture.",
      references: [references.carrollGrNotes, references.fordRoman]
    }
  },
  {
    id: "foundation.adm_spatial_metric.002",
    type: "mc",
    track: "Established foundations",
    module: "ADM split",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In the ADM split, what does the spatial metric describe?",
    choices: [
      { id: "slice_geometry", content: "The intrinsic geometry of each spatial slice." },
      { id: "time_step", content: "Only the rate at which proper time advances between slices." },
      { id: "ordinary_matter", content: "A guarantee that the source is ordinary matter." },
      { id: "quantum_state", content: "The quantum state of fields on a chronology horizon." }
    ],
    answer: ["slice_geometry"],
    explanation: {
      answer: "The spatial metric describes intrinsic geometry on a slice.",
      why: "The ADM variables separate spatial geometry, time advance, and spatial drift. Lapse and shift do different work from the spatial metric.",
      boundary: "This is established ADM terminology, not active-rail-specific language.",
      references: [references.adm]
    }
  },
  {
    id: "foundation.adm_shift.002",
    type: "mc",
    track: "Established foundations",
    module: "ADM split",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In ADM language, what does the shift primarily describe?",
    choices: [
      { id: "spatial_drift", content: "How spatial coordinates drift from one slice to the next." },
      { id: "normal_time", content: "Only the normal proper-time separation between slices." },
      { id: "energy_density", content: "The observer energy density in every matter model." },
      { id: "topology", content: "The global topology of spacetime." }
    ],
    answer: ["spatial_drift"],
    explanation: {
      answer: "The shift describes spatial coordinate drift between slices.",
      why: "ADM lapse handles normal time advance, while shift handles how coordinates slide tangentially between neighboring slices.",
      boundary: "This is established ADM notation; later applied models must still respect that baseline meaning.",
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
    prompt: "What does extrinsic curvature describe in a 3+1 split?",
    choices: [
      { id: "embedding_change", content: "How a spatial slice is embedded in spacetime, related to the time evolution of spatial geometry." },
      { id: "intrinsic_only", content: "Only distances measured entirely inside the slice, with no embedding information." },
      { id: "matter_unique", content: "The unique matter action that realizes the geometry." },
      { id: "causal_complete", content: "A proof of global causal completeness." }
    ],
    answer: ["embedding_change"],
    explanation: {
      answer: "Extrinsic curvature describes embedding and time-change information for the slice.",
      why: "The spatial metric gives intrinsic slice geometry; extrinsic curvature records how that slice sits in the full spacetime and enters the ADM constraints.",
      boundary: "This is established 3+1 geometry, not an operational readiness claim.",
      references: [references.adm, references.carrollGrNotes]
    }
  },
  {
    id: "foundation.constraints_evolution.001",
    type: "multi",
    track: "Established foundations",
    module: "ADM constraints",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements about ADM constraints are careful?",
    choices: [
      { id: "initial_data", content: "They restrict admissible initial data on a spatial slice." },
      { id: "monitor", content: "They are useful diagnostics during evolution or numerical modeling." },
      { id: "optional", content: "They can be ignored once a desired metric behavior is named." },
      { id: "matter_action", content: "They automatically provide the matter action for any prescribed geometry." }
    ],
    answer: ["initial_data", "monitor"],
    explanation: {
      answer: "ADM constraints restrict initial data and provide important consistency diagnostics.",
      why: "Constraint satisfaction is not decorative: it is part of what makes the 3+1 data compatible with Einstein's equation. But constraints alone do not construct a physical source sector.",
      boundary: "This is established ADM theory and should be kept separate from application-specific qualification language.",
      references: [references.adm]
    }
  },
  {
    id: "foundation.initial_value.sequence.001",
    type: "sequence",
    track: "Established foundations",
    module: "ADM constraints",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Order a conservative 3+1 initial-value reasoning flow.",
    items: [
      { id: "choose_data", content: "Choose spatial metric and extrinsic-curvature data" },
      { id: "matter", content: "Specify compatible matter projections or vacuum conditions" },
      { id: "constraints", content: "Check Hamiltonian and momentum constraints" },
      { id: "evolve", content: "Evolve with chosen lapse and shift conditions" },
      { id: "monitor", content: "Monitor constraint preservation and interpretation" }
    ],
    answer: ["choose_data", "matter", "constraints", "evolve", "monitor"],
    explanation: {
      answer: "Choose data, specify matter projections, check constraints, evolve, monitor.",
      why: "The order keeps initial data and constraint consistency ahead of evolution claims. Monitoring matters because numerical or analytic evolution can expose inconsistency or gauge confusion.",
      boundary: "This is established 3+1 reasoning, not a project-specific service schedule.",
      references: [references.adm, references.carrollGrNotes]
    }
  },
  {
    id: "foundation.causal_cones.001",
    type: "mc",
    track: "Established foundations",
    module: "Causal structure",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What do light cones represent in a relativistic spacetime?",
    choices: [
      { id: "causal_directions", content: "The local null boundaries separating timelike, null, and spacelike directions." },
      { id: "matter_source", content: "The matter source required to realize a metric." },
      { id: "coordinate_grid", content: "A fixed coordinate grid independent of the metric." },
      { id: "energy_positive", content: "A guarantee that all observers measure positive energy." }
    ],
    answer: ["causal_directions"],
    explanation: {
      answer: "Light cones encode local causal directions.",
      why: "They separate directions that can be reached by timelike or lightlike motion from spacelike-separated directions. Their tilt or distortion can reveal important causal behavior.",
      boundary: "This is established causal-structure vocabulary, not a physical-source claim.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.horizon.local_global.001",
    type: "multi",
    track: "Established foundations",
    module: "Causal structure",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which horizon-related statements are careful in GR reasoning?",
    choices: [
      { id: "global", content: "Some horizons are global causal structures, not features a local observer can always identify from one small patch." },
      { id: "signals", content: "Horizon-like behavior is about signal reachability and causal access." },
      { id: "coordinate_only", content: "All horizons are merely bad coordinate choices." },
      { id: "source_done", content: "Finding a horizon constructs the matter source." }
    ],
    answer: ["global", "signals"],
    explanation: {
      answer: "Horizons require causal-access reasoning, often with global context.",
      why: "Some apparent singularities are coordinate artifacts, but horizons themselves can encode real causal boundaries. Their interpretation requires more than local component inspection or a single coordinate chart.",
      boundary: "This is established causal-structure reasoning and does not decide source realizability or matter viability.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.global_hyperbolicity.001",
    type: "mc",
    track: "Established foundations",
    module: "Causal structure",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why is global hyperbolicity important in GR?",
    choices: [
      { id: "well_posed", content: "It supports well-posed causal evolution from suitable initial data and rules out certain causal pathologies." },
      { id: "ordinary_matter", content: "It guarantees ordinary positive-energy matter for any metric." },
      { id: "local_only", content: "It is only a statement about one tangent space at one event." },
      { id: "no_constraints", content: "It removes the need for constraint equations." }
    ],
    answer: ["well_posed"],
    explanation: {
      answer: "Global hyperbolicity is tied to well-posed causal evolution.",
      why: "It is a global causal condition that helps make initial-value reasoning meaningful. It is not a substitute for stress-energy, energy-condition analysis, or source modeling.",
      boundary: "This is established causal-structure theory, not an engineering-readiness, source-realization, or matter-viability claim.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.ctc.definition.001",
    type: "tf",
    track: "Established foundations",
    module: "Causal structure",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "True or false: A closed timelike curve is a future-directed timelike path that returns to its starting event.",
    choices: [
      { id: "true", content: "True" },
      { id: "false", content: "False" }
    ],
    answer: ["true"],
    explanation: {
      answer: "True.",
      why: "That is the basic causal-structure idea: a timelike worldline loops back to the same event, creating chronology problems.",
      boundary: "This is established causal terminology; particular mechanisms or examples require separate analysis.",
      references: [references.carrollGrNotes, references.chronologyProtection]
    }
  },
  {
    id: "foundation.stress_components.matching.002",
    type: "matching",
    track: "Established foundations",
    module: "Stress-energy basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Match each stress-energy idea to the most direct interpretation.",
    prompts: [
      { id: "density", content: "Energy density" },
      { id: "flux", content: "Energy or momentum flux" },
      { id: "pressure", content: "Pressure or stress" }
    ],
    options: [
      { id: "observer_measure", label: "What a chosen observer measures locally as density" },
      { id: "flow", label: "Transport of energy or momentum across directions" },
      { id: "spatial_stress", label: "Spatial force-per-area style components" }
    ],
    answer: {
      density: "observer_measure",
      flux: "flow",
      pressure: "spatial_stress"
    },
    explanation: {
      answer: "Density, flux, and pressure/stress are distinct tensor roles.",
      why: "A source diagnostic can fail if it watches density but ignores fluxes or stresses. The tensor structure matters because Einstein's equation couples to the whole stress-energy tensor.",
      boundary: "This is established stress-energy interpretation, not an architecture-specific or project-only taxonomy.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.equation_units.dragfill.003",
    type: "drag_fill",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    promptParts: [
      "In units ",
      { type: "math", latex: "G=c=1", label: "G equals c equals one" },
      ", solving Einstein's equation for stress-energy gives ",
      { type: "blank", id: "stress" },
      "."
    ],
    tokens: [
      { id: "stress_from_g", content: [{ type: "math", latex: "T_{\\mu\\nu}=G_{\\mu\\nu}/(8\\pi)", label: "T equals Einstein tensor over eight pi" }] },
      { id: "metric_flat", content: [{ type: "math", latex: "g_{\\mu\\nu}=\\eta_{\\mu\\nu}", label: "metric equals eta" }] },
      { id: "null_norm", content: [{ type: "math", latex: "k^\\mu k_\\mu=0", label: "null norm" }] },
      { id: "lapse_positive", content: [{ type: "math", latex: "\\alpha>0", label: "alpha greater than zero" }] }
    ],
    blanks: [
      { id: "stress", accepts: ["stress_from_g"] }
    ],
    explanation: {
      answer: [{ type: "math", latex: "T_{\\mu\\nu}=G_{\\mu\\nu}/(8\\pi)", label: "stress energy from Einstein tensor" }],
      why: "Einstein's equation can be algebraically read this way for a prescribed geometry in these units. That computes source demand, not a matter action.",
      boundary: "This is established equation manipulation with a source-realization boundary.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.tensor_components.001",
    type: "mc",
    track: "Established foundations",
    module: "Stress-energy basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why should tensor component claims name the frame or basis being used?",
    choices: [
      { id: "basis", content: "Components depend on the chosen frame or coordinates, even though tensorial statements can be invariant." },
      { id: "absolute", content: "Each component has the same numerical value in every frame." },
      { id: "no_tensor", content: "Naming a basis makes the object stop being a tensor." },
      { id: "source", content: "The frame choice constructs the physical matter source." }
    ],
    answer: ["basis"],
    explanation: {
      answer: "Components are basis-dependent.",
      why: "Tensor equations can be coordinate-invariant while individual components change with the frame. Good interpretation keeps this distinction visible.",
      boundary: "This is established tensor reasoning and applies before any project-specific modeling.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.symmetry_reduction.001",
    type: "multi",
    track: "Established foundations",
    module: "Metric basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements about symmetry reduction are careful?",
    choices: [
      { id: "simplifies", content: "Symmetry can reduce equations and make diagnostics tractable." },
      { id: "misses_modes", content: "A reduced model may hide nonsymmetric perturbations or channels." },
      { id: "proves_full", content: "A symmetric calculation automatically proves every nonsymmetric case." },
      { id: "no_sources", content: "Symmetry removes the need to check stress-energy." }
    ],
    answer: ["simplifies", "misses_modes"],
    explanation: {
      answer: "Symmetry helps, but it narrows what has been tested.",
      why: "Reduction is a legitimate mathematical strategy, but claims should track the reduced scope. Missing modes or channels can matter outside the symmetry class.",
      boundary: "This is general modeling discipline, not a project-specific excuse or guarantee.",
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.model_solution.classification.001",
    type: "claim_classification",
    track: "Established foundations",
    module: "Metric basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Classify each modeling statement by the safest general status.",
    statuses: ["established_theory", "established_constraint", "literature_model", "open_gate"],
    statements: [
      { id: "field_equation", content: "Einstein's equation relates curvature to stress-energy.", answer: "established_theory" },
      { id: "energy_condition", content: "The NEC constrains stress-energy contractions with null vectors.", answer: "established_constraint" },
      { id: "metric_ansatz", content: "A named speculative metric is a model to be analyzed, not automatically a physical source.", answer: "literature_model" },
      { id: "source_realization", content: "A conventional matter sector realizes every prescribed exotic metric.", answer: "open_gate" }
    ],
    explanation: {
      answer: "The statements separate field equations, constraints, model status, and unresolved source realization.",
      why: "General theory work often mixes equations, assumptions, and model proposals. Classification keeps a calculation from becoming an overclaim.",
      boundary: "This is general claim-boundary training with no dependence on project state.",
      references: [references.carrollGrNotes, references.fordRoman]
    }
  },
  {
    id: "foundation.conservation_boundary.001",
    type: "multi",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements correctly distinguish conservation consistency from physical source realization?",
    choices: [
      { id: "necessary", content: "Covariant conservation is a necessary consistency condition for the source side of Einstein's equation." },
      { id: "not_sufficient", content: "Conservation alone is not sufficient to identify a viable microphysical matter model." },
      { id: "sufficient", content: "Any conserved stress tensor is automatically produced by ordinary matter." },
      { id: "irrelevant", content: "The Bianchi identity makes source interpretation irrelevant." }
    ],
    answer: ["necessary", "not_sufficient"],
    explanation: {
      answer: "Conservation is necessary but not sufficient for physical source realization.",
      why: "The Bianchi identity supplies a deep consistency relation, but viable matter also depends on dynamics, stability, energy behavior, coupling assumptions, and physical interpretation beyond conservation.",
      boundary: "This is established GR reasoning and is deliberately broader than any one architecture.",
      references: [references.carrollGrNotes]
    }
  }
];
