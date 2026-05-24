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
  energyConditionsPrimer: {
    id: "curiel_energy_conditions_primer",
    kind: "paper",
    label: "A Primer on Energy Conditions",
    citation: "Erik Curiel, arXiv:1405.0403 (2014).",
    url: "https://arxiv.org/abs/1405.0403",
    supports: "Definitions, interpretation, limits, and conceptual status of standard pointwise energy conditions."
  },
  causalHierarchy: {
    id: "minguzzi_sanchez_causal_hierarchy",
    kind: "paper",
    label: "The causal hierarchy of spacetimes",
    citation: "E. Minguzzi and M. Sanchez, arXiv:gr-qc/0609119 (2006).",
    url: "https://arxiv.org/abs/gr-qc/0609119",
    supports: "Causal hierarchy, chronology, causality conditions, and global causal-structure distinctions."
  },
  globalHyperbolicityReview: {
    id: "sanchez_global_hyperbolicity_review",
    kind: "paper",
    label: "Recent progress on the notion of global hyperbolicity",
    citation: "Miguel Sanchez, arXiv:0712.1933 (2007).",
    url: "https://arxiv.org/abs/0712.1933",
    supports: "Global hyperbolicity, Cauchy hypersurfaces, and causal-curve criteria."
  },
  cauchyHypersurfaces: {
    id: "bernal_sanchez_smooth_cauchy",
    kind: "paper",
    label: "On smooth Cauchy hypersurfaces and Geroch's splitting theorem",
    citation: "A. N. Bernal and M. Sanchez, arXiv:gr-qc/0306108 (2003).",
    url: "https://arxiv.org/abs/gr-qc/0306108",
    supports: "Existence of smooth spacelike Cauchy hypersurfaces and splitting structure in globally hyperbolic spacetimes."
  },
  carrollGrNotes: {
    id: "carroll_gr_notes",
    kind: "paper",
    label: "Lecture Notes on General Relativity",
    citation: "Sean M. Carroll, arXiv:gr-qc/9712019.",
    url: "https://arxiv.org/abs/gr-qc/9712019",
    supports: "Open-access general relativity reference for metric notation, curvature, Einstein's equation, geodesics, stress-energy tensors, and conservation identities; not the primary anchor for energy-condition taxonomy or global hyperbolicity."
  },
  openStaxQuantum: {
    id: "openstax_university_physics_3",
    kind: "textbook",
    label: "University Physics Volume 3",
    citation: "OpenStax, University Physics Volume 3.",
    url: "https://openstax.org/details/books/university-physics-volume-3",
    supports: "Open introductory reference for quantum states, observables, uncertainty, spectra, photons, matter waves, and modern-physics foundations."
  },
  tongQft: {
    id: "tong_quantum_field_theory",
    kind: "lecture_notes",
    label: "Lectures on Quantum Field Theory",
    citation: "David Tong, University of Cambridge lecture notes.",
    url: "https://davidtong.org/teaching/quantum-field-theory/",
    supports: "Open lecture notes for field quantization, vacuum modes, particle excitations, renormalization basics, and conceptual Casimir-effect framing."
  },
  miltonCasimir: {
    id: "milton_casimir_zero_point",
    kind: "paper",
    label: "The Casimir Effect: Physical Manifestations of Zero Point Energy",
    citation: "Kimball A. Milton, arXiv:hep-th/9901011.",
    url: "https://arxiv.org/abs/hep-th/9901011",
    supports: "Casimir-effect interpretation, zero-point-energy framing, boundary-conditioned vacuum effects, and limits of naive free-energy readings."
  },
  burgessEft: {
    id: "burgess_intro_eft",
    kind: "lecture_notes",
    label: "Introduction to Effective Field Theory",
    citation: "C. P. Burgess, arXiv:hep-th/0701053.",
    url: "https://arxiv.org/abs/hep-th/0701053",
    supports: "Scale separation, low-energy effective descriptions, matching, cutoff sensitivity, and validity-domain discipline."
  },
  polchinskiDBranes: {
    id: "polchinski_tasi_dbranes",
    kind: "lecture_notes",
    label: "TASI Lectures on D-Branes",
    citation: "Joseph Polchinski, arXiv:hep-th/9611050.",
    url: "https://arxiv.org/abs/hep-th/9611050",
    supports: "D-branes as open-string boundary-condition objects, worldvolume degrees of freedom, and source/coupling context in string theory."
  },
  douglasKachruFlux: {
    id: "douglas_kachru_flux_compactification",
    kind: "review",
    label: "Flux Compactification",
    citation: "Michael R. Douglas and Shamit Kachru, arXiv:hep-th/0610102.",
    url: "https://arxiv.org/abs/hep-th/0610102",
    supports: "Flux compactification, moduli, string vacua, and the consistency conditions around high-energy effective descriptions."
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
      adaptive: {
        choices: {
          local_time: {
            supported: "Lapse multiplies the normal time advance between spatial slices, so this choice names the direct ADM role."
          },
          angular_area: {
            unsupported: "Angular area belongs to the spatial metric sector, not to the lapse function."
          },
          source_model: {
            unsupported: "A lapse choice can enter a metric ansatz, but it does not by itself specify a matter model."
          },
          packet_release: {
            unsupported: "Release timing is active-rail service vocabulary. It is not the established ADM meaning of lapse."
          }
        }
      },
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
      adaptive: {
        choices: {
          plant: {
            supported: "The rail is the operating plant: the prepared support and handoff infrastructure that carries the service burden around the packet."
          },
          payload: {
            unsupported: "The payload is the packet side of the architecture. The rail is the infrastructure serving it."
          },
          constraint: {
            unsupported: "The rail is a project architecture term, not a theorem proving physical realizability."
          },
          rset: {
            unsupported: "A renormalized stress tensor is quantum-field source notation. It is not the active-rail infrastructure role."
          }
        }
      },
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
      adaptive: {
        choices: {
          true: {
            supported: "The 1994 paper introduces and analyzes a spacetime model; it does not demonstrate a realizable propulsion system."
          },
          false: {
            unsupported: "Calling the paper an engineering construction overstates what the publication supplies. The source and control problems remain outside that result."
          }
        }
      },
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
      { id: "boundary", content: "They can make a demanded stress tensor look compatible with a selected classical assumption, but only within that assumption's scope." },
      { id: "assumptions", content: "They make positivity, averaging, and observer assumptions explicit during review." },
      { id: "prove_build", content: "They are enough to promote a demanded stress tensor to a viable source when no stability problem is visible." },
      { id: "ignore", content: "They can be deferred until after the causal chronology is accepted, because chronology review is the stricter gate." },
      { id: "single_condition", content: "Passing one pointwise condition usually makes the remaining energy-condition checks redundant." }
    ],
    answer: ["diagnose", "assumptions"],
    explanation: {
      answer: "Energy-condition checks diagnose stress-energy constraints and make assumptions explicit.",
      why: "They are part of established relativistic analysis, but they do not by themselves produce or certify a realizable matter sector. Their value is clearest when the relevant observer, null direction, averaging, or positivity assumption is kept visible.",
      boundary: "This is established constraint material applied to design interpretation, not a proof of buildability.",
      adaptive: {
        choices: {
          diagnose: {
            supported: "Energy conditions are useful diagnostics because they expose what stress-energy behavior a proposed geometry demands."
          },
          boundary: {
            unsupported: "This is close to a useful diagnostic, but it overpromotes scope. Compatibility with one selected assumption is not completed physical realization."
          },
          assumptions: {
            supported: "The observer, null direction, averaging interval, and positivity assumptions are part of what the check actually means."
          },
          prove_build: {
            unsupported: "Even when stability concerns are not obvious, a viable source still needs dynamics, realization, and operational evidence beyond the inequality check."
          },
          ignore: {
            unsupported: "Chronology review and source-condition review answer different questions. Passing one gate does not justify deferring the other indefinitely."
          },
          single_condition: {
            unsupported: "Different energy conditions test different observers, contractions, and averaging assumptions, so one pointwise pass does not make the others redundant."
          }
        }
      },
      references: [references.energyConditionsPrimer]
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
      adaptive: {
        blanks: {
          source_term: {
            correct: "The ledger is recording the demanded stress-energy, so the Einstein tensor divided by eight pi is the right source-side quantity in these units.",
            tokens: {
              shift_over_lapse: "The shift-over-lapse ratio can describe coordinate or service kinematics, but it is not the stress-energy demanded by Einstein's equation.",
              packet_norm: "The packet norm is packet-facing data. It does not replace the tensor source demanded by the prescribed geometry.",
              angular_metric: "The angular metric component is part of the geometry. The ledger step asks for the source-side tensor inferred from that geometry."
            },
            missing: "This blank asks for the stress-energy quantity demanded by the prescribed metric."
          }
        }
      },
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
      adaptive: {
        sequence: [
          {
            id: "support-before-carry",
            before: "support",
            after: "carry",
            content: "Support comes before carry because the service channel must be prepared before the packet is transported."
          },
          {
            id: "catch-before-fade",
            before: "catch",
            after: "fade",
            content: "Catch/rematch comes before fade because endpoint support should be established before the carrying shift is removed."
          },
          {
            id: "decompress-before-reset",
            before: "decompress",
            after: "reset",
            content: "Decompression precedes reset because the support state has to unwind before reuse readiness can be assessed."
          }
        ]
      },
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
      boundary: "These statements mix statuses and should be read as epistemic classification rather than as one uniform claim type.",
      adaptive: {
        classifications: {
          adm: {
            correct: "ADM lapse and shift are established 3+1 decomposition vocabulary.",
            statuses: {
              literature_model: "ADM terminology is not merely a speculative warp-model convention; it is standard GR formalism.",
              active_rail_model: "Active-rail uses ADM vocabulary, but lapse and shift themselves are not project-specific inventions.",
              open_gate: "There is no unresolved project gate in the statement that ADM separates lapse and shift roles."
            }
          },
          alcubierre: {
            correct: "The Alcubierre metric belongs in published speculative-literature context.",
            statuses: {
              established_theory: "The paper is published literature, but the warp metric is not an established physical construction.",
              active_rail_model: "Active-rail may study or compare against the metric, but the metric predates the project.",
              open_gate: "The statement names a literature model, not a missing project demonstration."
            }
          },
          rail: {
            correct: "Packet and rail are active-rail architecture terms.",
            statuses: {
              established_theory: "The packet/rail split is not textbook GR terminology.",
              literature_model: "This is project architecture vocabulary rather than a published warp metric by itself.",
              open_gate: "The statement defines model language; it does not assert a completed unresolved demonstration."
            }
          },
          reset: {
            correct: "The reset statement is an open gate because source-history accumulation has not been closed as a general result.",
            statuses: {
              established_theory: "Established GR does not supply reusable rail reset without a source-history audit.",
              literature_model: "A speculative metric paper does not establish reusable active-rail reset behavior.",
              active_rail_model: "Reset is part of the model, but the statement claims no accumulation, which requires evidence beyond vocabulary."
            }
          }
        }
      },
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
      adaptive: {
        matches: {
          alpha: {
            correct: "Alpha is conventionally used for the lapse in ADM-style notation.",
            options: {
              radial_shift: "Radial shift is the beta role, not the alpha role.",
              angular_sector: "Angular-sector information belongs to a spatial metric component, not the lapse."
            }
          },
          beta: {
            correct: "Beta with a radial index denotes the radial shift component here.",
            options: {
              lapse: "The lapse is alpha; beta labels shift.",
              angular_sector: "The angular sector is represented by a gamma spatial metric component."
            }
          },
          gamma: {
            correct: "Gamma-Omega-Omega names an angular component of the spatial metric.",
            options: {
              lapse: "The lapse role is alpha, not a gamma spatial metric component.",
              radial_shift: "Radial shift is beta-ell; gamma-Omega-Omega belongs to the spatial angular sector."
            }
          }
        }
      },
      references: [references.adm],
      sourceLinks: [sources.cliSourceParams]
    }
  },
  {
    id: "design_review.burden.001",
    type: "multi",
    track: "Design review and synthesis",
    module: "Failure analysis",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    scoring: "subtract_incorrect",
    prompt: "A service case has clean packet arrival, but the plant report omits support-edge burden, angular pressure, and reset residue. Which review comments are appropriate?",
    choices: [
      { id: "arrival_not_enough", content: "Final packet arrival is not enough to qualify the service." },
      { id: "need_channels", content: "The missing plant channels should be reviewed before acceptance." },
      { id: "partial_packet", content: "The clean arrival can still be recorded as partial packet-facing evidence." },
      { id: "ignore_reset", content: "Reset residue can be moved to a later review if the claim is limited to a single first-use pass." },
      { id: "source_done", content: "The clean packet trace is strong indirect evidence that source closure is likely adequate." },
      { id: "endpoint_inferred", content: "Endpoint rematch quality can be treated as provisionally acceptable if final position and timing are both within tolerance." }
    ],
    answer: ["arrival_not_enough", "need_channels", "partial_packet"],
    explanation: {
      answer: "Arrival is useful packet evidence, but missing plant channels still matter.",
      why: "Active-rail qualification separates packet-facing success from plant burden, reset evidence, and source realization. A clean arrival can be a real success while still leaving the support edge, angular sector, and reset history unqualified.",
      boundary: "This is active-rail design-review logic, not a general theorem of GR or a substitute for physical source closure.",
      adaptive: {
        choices: {
          arrival_not_enough: {
            supported: "Packet arrival is one evidence surface. It does not automatically qualify support-edge, angular-pressure, reset, or source-realization channels."
          },
          need_channels: {
            supported: "The omitted plant channels are exactly the kind of missing evidence that should block a full service claim."
          },
          partial_packet: {
            supported: "The clean arrival should still be credited as partial packet-facing evidence rather than discarded."
          },
          ignore_reset: {
            unsupported: "A first-use claim can narrow the reset burden, but a service qualification that includes reuse or readiness still needs reset evidence."
          },
          source_done: {
            unsupported: "The packet trace is positive evidence, but source closure needs source-channel evidence rather than inference from packet behavior alone."
          },
          endpoint_inferred: {
            unsupported: "Position and timing help, but endpoint rematch is a channel claim about transfer/release quality and needs its own evidence."
          }
        }
      },
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
      adaptive: {
        choices: {
          flagged: {
            supported: "This choice credits the run ledger while keeping its project-state and revision-sensitive status visible."
          },
          general: {
            unsupported: "A single internal run ledger does not become a geometry-independent general result."
          },
          established: {
            unsupported: "Computation from a metric can use established equations, but the resulting project claim is not itself an established theorem."
          },
          complete: {
            unsupported: "Clean packet safety does not complete physical source construction or repeated-operation closure."
          }
        }
      },
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
      adaptive: {
        choices: {
          interval: {
            supported: "The metric directly evaluates intervals and inner products, which also determine local causal character."
          },
          matter: {
            unsupported: "Einstein's equation can infer demanded stress-energy from geometry, but the metric alone does not specify a unique physical matter model."
          },
          global: {
            unsupported: "Local metric data does not by itself fix the complete global topology."
          },
          coordinates: {
            unsupported: "A metric can be expressed in many coordinate systems; it does not choose one preferred coordinate frame for every observer."
          }
        }
      },
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
      adaptive: {
        choices: {
          spatial_drift: {
            supported: "The shift is the tangential part of the time-evolution vector, so it describes how spatial coordinates move between slices."
          },
          proper_time: {
            unsupported: "The lapse controls normal proper-time advance; the shift handles tangential coordinate drift."
          },
          matter_law: {
            unsupported: "A shift vector is part of the geometric decomposition, not a matter law."
          },
          quantum_state: {
            unsupported: "Quantum-state selection is a separate field-theory issue, not the ADM role of shift."
          }
        }
      },
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
      adaptive: {
        blanks: {
          nec_expression: {
            correct: "The NEC is the nonnegativity of the stress-energy tensor contracted with every null vector.",
            tokens: {
              trace_zero: "A vanishing trace is a different stress-tensor statement; it is not the NEC.",
              einstein_tensor_zero: "A zero Einstein tensor is a vacuum-curvature condition, not the null energy condition.",
              timelike_norm: "A null vector has zero norm, not timelike norm minus one, and the NEC is a stress-energy contraction."
            },
            missing: "The blank needs the stress-energy contraction evaluated on a null vector."
          }
        }
      },
      references: [references.energyConditionsPrimer]
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
      { id: "unique_solution", content: "It can be treated as the main source check once the momentum constraint is separately small." },
      { id: "no_matter", content: "It fixes the energy-density projection but leaves the detailed matter model for later." },
      { id: "coordinate_only", content: "It mostly tracks the chosen slicing, so its matter interpretation is secondary to evolution diagnostics." }
    ],
    answer: ["geometry_source_relation"],
    explanation: {
      answer: "It relates slice geometry to normal-observer energy density.",
      why: "The constraint connects spatial curvature and extrinsic curvature terms to the matter energy density projection.",
      boundary: "This is established ADM structure. Using it as a diagnostic ledger is an application, not a new theorem.",
      adaptive: {
        choices: {
          geometry_source_relation: {
            supported: "The Hamiltonian constraint links intrinsic and extrinsic slice geometry to the normal-observer energy-density projection."
          },
          unique_solution: {
            unsupported: "The Hamiltonian constraint is one essential source projection, but it does not absorb the momentum constraint or all later evolution checks."
          },
          no_matter: {
            unsupported: "The energy-density projection is not the same as a detailed matter model; the boundary between demand and realization remains."
          },
          coordinate_only: {
            unsupported: "Slicing matters in ADM, but the Hamiltonian constraint still carries a real geometry-to-source projection."
          }
        }
      },
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
      { id: "intrinsic_only", content: "The curvature of the spatial metric alone, before considering how the slice changes in time." },
      { id: "matter_choice", content: "The part of the initial data that selects which matter action can realize the geometry." },
      { id: "global_topology", content: "The global embedding class of the whole spacetime rather than the local embedding of one slice." }
    ],
    answer: ["embedding_change"],
    explanation: {
      answer: "Extrinsic curvature tracks how a spatial slice sits and evolves inside spacetime.",
      why: "It is not merely intrinsic spatial curvature; it records normal-direction change of the spatial geometry.",
      boundary: "This is established ADM geometry and should not be confused with a project-specific source channel.",
      adaptive: {
        choices: {
          embedding_change: {
            supported: "Extrinsic curvature records how the spatial metric changes as the slice is embedded and evolved through spacetime."
          },
          intrinsic_only: {
            unsupported: "Intrinsic curvature lives inside the slice. Extrinsic curvature records how the slice sits in spacetime and changes along the normal direction."
          },
          matter_choice: {
            unsupported: "Extrinsic curvature enters the geometric initial data and constraints, but it does not select a microscopic matter action."
          },
          global_topology: {
            unsupported: "The local embedding behavior of a slice is not the same as classifying the full spacetime topology."
          }
        }
      },
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
    prompt: [
      "For an observer with unit timelike four-velocity ",
      { type: "math", latex: "u^\\mu", label: "u mu" },
      ", which contraction gives the local energy density that observer measures?"
    ],
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
      adaptive: {
        choices: {
          tuu: {
            supported: "Projecting stress-energy twice onto the observer's timelike four-velocity gives that observer's measured energy density."
          },
          trace: {
            unsupported: "The trace contracts stress-energy with the metric; it is not the energy density measured by a specified observer."
          },
          einstein: {
            unsupported: "This uses the Einstein tensor and a null vector. It is not the observer energy-density projection of stress-energy."
          },
          metric_norm: {
            unsupported: "The metric norm verifies the four-velocity normalization; it is not the stress-energy density."
          }
        }
      },
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
      { id: "null_contraction", label: "Nonnegative stress-energy null contraction for every null vector" },
      { id: "timelike_density", label: "Nonnegative observer energy density for every timelike observer" },
      { id: "contracted_trace", label: "Stress-tensor trace, not itself an energy condition" }
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
      adaptive: {
        matches: {
          nec: {
            correct: "The NEC is stated using stress-energy contracted with every null vector.",
            options: {
              timelike_density: "Timelike-observer density is the WEC pattern, not the NEC.",
              contracted_trace: "The trace is a separate contraction and is not the NEC."
            }
          },
          wec: {
            correct: "The WEC asks for nonnegative energy density for every timelike observer.",
            options: {
              null_contraction: "Null contractions belong to the NEC, not the WEC.",
              contracted_trace: "The trace does not encode the observer-quantified WEC requirement."
            }
          },
          trace: {
            correct: "The trace is a contraction of the tensor, but it is not itself one of these energy conditions.",
            options: {
              null_contraction: "A null contraction tests the NEC rather than the trace.",
              timelike_density: "Timelike density is the WEC pattern rather than the tensor trace."
            }
          }
        }
      },
      references: [references.energyConditionsPrimer]
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
      adaptive: {
        blanks: {
          equation: {
            correct: "This is Einstein's equation in units with G equals c equals one.",
            tokens: {
              flat_metric: "A flat metric condition is a special geometry statement, not the general field equation.",
              null_norm: "The null norm condition identifies a null vector; it does not relate curvature to stress-energy.",
              trace: "A zero trace condition is a stress-tensor statement, not Einstein's equation."
            },
            missing: "The blank asks for the field equation relating curvature and stress-energy."
          }
        }
      },
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
      { id: "unique_global", content: "The spatial gauge choice to the shift-gradient part of the evolution." },
      { id: "vacuum_only", content: "Extrinsic-curvature balance in vacuum-like regions, with matter momentum treated as a separate source check." },
      { id: "quantum_state", content: "The semiclassical state choice to the renormalized momentum flux measured by an observer." }
    ],
    answer: ["momentum_projection"],
    explanation: {
      answer: "It relates extrinsic-curvature combinations to the momentum density projection of stress-energy.",
      why: "In ADM language the constraints split source diagnostics into normal energy-density and spatial momentum channels. That distinction matters before any project-specific source ledger or channel naming is introduced.",
      boundary: "This is established ADM structure and should not be mistaken for a physical source construction.",
      adaptive: {
        choices: {
          momentum_projection: {
            supported: "The momentum constraint ties spatial derivatives of extrinsic-curvature combinations to matter momentum density."
          },
          unique_global: {
            unsupported: "Gauge and shift behavior are related to the 3+1 description, but the momentum constraint is not merely a gauge-choice relation."
          },
          vacuum_only: {
            unsupported: "The vacuum limit is a useful special case, but the constraint's source-diagnostic role includes the matter momentum projection."
          },
          quantum_state: {
            unsupported: "Semiclassical momentum flux can be relevant elsewhere, but the ADM momentum constraint is the classical slice constraint relating geometry to momentum density."
          }
        }
      },
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
      { id: "ban_all", content: "They make sustained macroscopic negative energy so restricted that it can be treated as absent for design purposes." },
      { id: "construct_drive", content: "They identify the sampling scales a geometry would need to respect, which is close to a constructive source recipe." },
      { id: "ignore_geometry", content: "They let the source review focus on quantum bounds rather than the detailed geometric stress ledger." }
    ],
    answer: ["bound_negative_energy"],
    explanation: {
      answer: "Quantum inequalities constrain negative energy; they do not erase the subject or solve engineering.",
      why: "The key lesson is quantitative restriction, not a simplistic ban or a construction method. In this setting, magnitude, duration, and sampling scale have to be reviewed together, so a pointwise sign table is not enough.",
      boundary: "This is established constraint literature applied to speculative geometries, not a source recipe.",
      adaptive: {
        choices: {
          bound_negative_energy: {
            supported: "The constraint is quantitative: magnitude, duration, sampling, and distribution are tied together."
          },
          ban_all: {
            unsupported: "The constraints are severe, but the paper's lesson is quantitative limitation rather than treating all negative energy as absent."
          },
          construct_drive: {
            unsupported: "Sampling-scale restrictions help review a candidate, but a bound is not a constructive source model."
          },
          ignore_geometry: {
            unsupported: "Quantum bounds and geometric source accounting work together; the inequality does not replace the stress ledger."
          }
        }
      },
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
      { id: "coupling_specific", content: "The source-sector lesson depends on the coupling and physical regime, not merely on naming a scalar field." },
      { id: "formal_not_final", content: "A formal solution branch still needs physical-regime and semiclassical-trust review." },
      { id: "minimal_generic", content: "It shows minimally coupled scalar fields generically support macroscopic traversable wormholes without additional assumptions." },
      { id: "scaling_clearance", content: "Once a formal non-minimal scalar branch is found, semiclassical trust is mainly a regime-selection issue rather than a central caveat." },
      { id: "field_name", content: "The phrase scalar field is by itself enough to identify a usable macroscopic material source." }
    ],
    answer: ["scalar_violation", "trans_planckian", "coupling_specific", "formal_not_final"],
    explanation: {
      answer: "The paper shows a coupling-sensitive scalar-field route to energy-condition violation while keeping the trans-Planckian and physical-regime caveats visible.",
      why: "The result is not simply 'scalar fields solve wormholes'; the coupling, field scale, and physical interpretation remain central. The valuable lesson is that source models can evade classical energy conditions while still raising severe feasibility and semiclassical-trust questions.",
      boundary: "This is published literature about a theoretical source class, not demonstrated macroscopic engineering.",
      adaptive: {
        choices: {
          scalar_violation: {
            supported: "The paper's non-minimal coupling analysis is exactly about scalar-field energy-condition violation."
          },
          trans_planckian: {
            supported: "The trans-Planckian field-value caveat is part of why the result does not become easy macroscopic source engineering."
          },
          coupling_specific: {
            supported: "The coupling and regime matter; a scalar-field label alone is not enough to preserve the result."
          },
          formal_not_final: {
            supported: "A formal branch still needs physical-regime, stability, and semiclassical-trust interpretation."
          },
          minimal_generic: {
            unsupported: "The result is not a generic minimally coupled scalar-field solution for macroscopic traversable wormholes."
          },
          scaling_clearance: {
            unsupported: "Field scale and semiclassical trust stay central to the physical interpretation; they are not merely later regime-selection details."
          },
          field_name: {
            unsupported: "A field name does not identify a usable material source without coupling, regime, and physical interpretation."
          }
        }
      },
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
      { id: "no_energy", content: "It suggests the expansion part of the source burden is removed, so remaining stress components are secondary." },
      { id: "flat_everywhere", content: "It means the chosen flow is locally volume-preserving, so curvature effects can be treated as coordinate effects." },
      { id: "complete_engineering", content: "It supplies a cleaner warp kinematics that is close to an operational control prescription." }
    ],
    answer: ["congruence_property"],
    explanation: {
      answer: "Zero expansion is a kinematic property of the flow, not a source-free engineering result.",
      why: "A warp metric can have zero expansion while still carrying curvature and stress-energy issues. The result changes one geometric feature of the warp construction; it does not make the Einstein tensor vanish or provide a matter sector.",
      boundary: "This is published speculative metric context, not a physical construction or source model.",
      adaptive: {
        choices: {
          congruence_property: {
            supported: "Zero expansion characterizes the flow congruence; it does not erase curvature or source demand."
          },
          no_energy: {
            unsupported: "Zero expansion removes one kinematic feature; it does not remove the remaining stress-energy review."
          },
          flat_everywhere: {
            unsupported: "Volume-preserving flow is not the same as flat spacetime or pure coordinate behavior."
          },
          complete_engineering: {
            unsupported: "Cleaner kinematics are still metric-model information, not an operational control system."
          }
        }
      },
      references: [references.natario]
    }
  },
  {
    id: "constraints.topological_censorship.001",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Topological censorship",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "What is the disciplined use of Friedman, Schleich, and Witt's 1993 topological censorship result in traversable-wormhole discussions?",
    choices: [
      { id: "conditional_constraint", content: "It is a conditional theorem showing that, under suitable assumptions, nontrivial topology is hidden from causal observers." },
      { id: "local_escape", content: "A smooth local throat cross-section can keep the discussion inside differential geometry unless a global causal route is specified." },
      { id: "source_substitute", content: "It makes causal accessibility the decisive issue, with stress-energy details mostly entering only through theorem assumptions." },
      { id: "assumption_free", content: "It can be used as a broad warning before all energy, asymptotic, and predictability assumptions are fully checked." }
    ],
    answer: ["conditional_constraint"],
    explanation: {
      answer: "Topological censorship is a conditional constraint theorem.",
      why: "Its force comes from its assumptions: energy, causality, asymptotic structure, and predictability conditions matter. The theorem is powerful because it tells you which global structures are hidden under those assumptions, not because it forbids writing every wormhole metric.",
      boundary: "This is established constraint material. It should be used carefully, not as a slogan or an assumption-free ban.",
      adaptive: {
        choices: {
          conditional_constraint: {
            supported: "This keeps the theorem attached to its energy, causality, asymptotic, and predictability assumptions."
          },
          local_escape: {
            unsupported: "Local throat smoothness is relevant geometry, but theorem applicability turns on global causal routes and assumptions."
          },
          source_substitute: {
            unsupported: "Causal accessibility is central, but stress-energy and predictability assumptions are active parts of the theorem."
          },
          assumption_free: {
            unsupported: "The theorem can guide suspicion, but a disciplined application still checks its assumptions."
          }
        }
      },
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
      why: "Chronology-protection literature treats closed-causal-curve formation as a deep causality and quantum-field problem, not a construction method. The warning is about whether backreaction and global causal structure obstruct time-machine formation, not how to operate one.",
      boundary: "This is literature-backed constraint context, with conjectural status.",
      adaptive: {
        choices: {
          true: {
            supported: "The review frames chronology protection as a physical constraint problem involving causality, quantum fields, and backreaction."
          },
          false: {
            unsupported: "The review does not provide an operating recipe for chronology violation; it emphasizes obstructions and unresolved physics."
          }
        }
      },
      references: [references.chronologyProtection]
    }
  },
  {
    id: "literature.alcubierre_horizon.001",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which cautions are appropriate when interpreting Alcubierre's 1994 warp metric?",
    choices: [
      { id: "metric_not_engine", content: "A metric ansatz is not the same thing as a controlled physical engine." },
      { id: "source_demand", content: "The stress-energy demand and energy-condition behavior remain central." },
      { id: "control_open", content: "Control and causal-access questions remain separate from writing the line element." },
      { id: "automatic_control", content: "A smooth line element can make the passenger region look operationally simple, so control can be treated after source review." },
      { id: "established_transport", content: "Because it is an exact GR ansatz, it gives stronger evidence than a qualitative propulsion sketch." },
      { id: "source_later", content: "If the passenger-region metric is mild, source review can focus mainly on the wall after control questions are settled." }
    ],
    answer: ["metric_not_engine", "source_demand", "control_open"],
    explanation: {
      answer: "The metric is a valuable speculative model, but source demand, control, and causal access remain central.",
      why: "Writing a spacetime geometry does not supply matter realization, stability, causal control, or operational protocols. A smooth ansatz can still leave negative energy, horizon, and steering questions unresolved.",
      boundary: "This is published-literature interpretation with unresolved physical gates, not a physical-realization result.",
      adaptive: {
        choices: {
          metric_not_engine: {
            supported: "A line element is a mathematical model. It does not by itself create an engine or operating protocol."
          },
          source_demand: {
            supported: "The stress-energy demand and energy-condition behavior are central burdens of the Alcubierre metric."
          },
          control_open: {
            supported: "Causal access and control remain separate questions after the metric is written down."
          },
          automatic_control: {
            unsupported: "A smooth line element can make the model readable, but it does not supply causal control over creation, steering, or stopping."
          },
          established_transport: {
            unsupported: "An exact ansatz is stronger than a sketch, but it is still not established transportation physics."
          },
          source_later: {
            unsupported: "A mild passenger region does not postpone source review; the wall and full geometry carry central stress-energy burdens."
          }
        }
      },
      references: [references.alcubierre],
      openGate: "Physical realizability, controllability, and source construction remain outside the metric ansatz itself."
    }
  },
  {
    id: "literature.chl.null_geodesics.001",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Clark, Hiscock, and Larson's 1999 paper \"Null Geodesics in the Alcubierre Warp Drive Spacetime,\" what causal feature appears for effective superluminal motion?",
    choices: [
      { id: "causal_access", content: "Horizon-like conical regions appear, limiting which signals can reach or be sent from the bubble." },
      { id: "complete_control", content: "The central worldline remains easy to parametrize, so control limits are mainly an engineering timing problem." },
      { id: "no_quantum", content: "Because the analysis is classical null geodesics, it brackets quantum-vacuum questions and weakens their relevance to causal access." },
      { id: "flat_optics", content: "The central region can look locally mild, so optical differences are mostly boundary effects rather than access limits." }
    ],
    answer: ["causal_access"],
    explanation: {
      answer: "The paper identifies horizon-like conical access structures.",
      why: "For effective superluminal motion, the null-geodesic structure includes regions that block signals from reaching the bubble and regions the bubble cannot signal into. That makes causal access a geometric issue, not just a matter of passenger intent.",
      boundary: "This is a result about the Alcubierre spacetime's causal optics, not a construction method.",
      adaptive: {
        choices: {
          causal_access: {
            supported: "The null-geodesic analysis reveals horizon-like access restrictions for the superluminal case."
          },
          complete_control: {
            unsupported: "A well-parametrized central worldline does not show that the passenger can causally reach or control every relevant region."
          },
          no_quantum: {
            unsupported: "Classical null-geodesic analysis brackets quantum questions; it does not weaken the causal-access result or remove source concerns."
          },
          flat_optics: {
            unsupported: "Local mildness near the center does not remove horizon-like access limits in the full superluminal geometry."
          }
        }
      },
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
      { id: "build", content: "Use its observer-facing signatures as indirect evidence that the modeled geometry has a physically coherent generation path." },
      { id: "ignore_sources", content: "Use geodesic regularity as evidence that source and energy-condition problems are independent of observable path analysis." },
      { id: "no_curvature", content: "Read the smoothness of plotted paths as evidence that the optical behavior is close to flat-space propagation." }
    ],
    answer: ["playground"],
    explanation: {
      answer: "It treats Alcubierre spacetime as a detailed geodesic/lensing study while preserving feasibility caveats.",
      why: "The paper's educational value is in the geodesic and visual-effects analysis: it shows how light and test paths behave inside the model. That does not answer how to generate the metric, stabilize it, or provide acceptable stress-energy.",
      boundary: "This is published-literature study of a speculative spacetime, not demonstrated engineering.",
      adaptive: {
        choices: {
          playground: {
            supported: "This captures both sides: rich geodesic and lensing analysis inside the model, plus feasibility caveats."
          },
          build: {
            unsupported: "Observer-facing signatures are valuable model diagnostics, but they do not show how the metric is generated."
          },
          ignore_sources: {
            unsupported: "Path regularity and source viability are separate, but source and energy-condition burdens remain attached to the same proposed spacetime."
          },
          no_curvature: {
            unsupported: "Smooth-looking paths can still encode nontrivial curvature and lensing behavior."
          }
        }
      },
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
      { id: "composition", content: "Network composition matters; one shortcut in isolation is not the whole causal analysis." },
      { id: "return_path", content: "A return route or paired arrangement can change the chronology analysis relative to one isolated leg." },
      { id: "no_ctc", content: "The one-way character of each individual tube is the dominant fact, so paired-network chronology risk is secondary." },
      { id: "source_solution", content: "The analysis identifies the stress profile sharply enough that source construction is mostly an implementation problem." },
      { id: "energy_optional", content: "Once the chronology question is framed as a network problem, the negative-energy burden can be reviewed separately rather than jointly." }
    ],
    answer: ["two_tubes", "negative_energy", "composition", "return_path"],
    explanation: {
      answer: "Network composition, return paths, and negative-energy burden are central.",
      why: "Everett and Roman distinguish the single-tube case from paired arrangements that can produce time-machine behavior, while preserving severe source concerns. The point is that chronology risk depends on how superluminal links are composed, not only on each link in isolation.",
      boundary: "This is superluminal-spacetime literature, not demonstrated engineering or a practical ordinary-matter construction.",
      adaptive: {
        choices: {
          two_tubes: {
            supported: "The paper distinguishes a single tube from paired arrangements that change the chronology problem."
          },
          negative_energy: {
            supported: "The construction retains severe exotic-source and thin-layer burdens."
          },
          composition: {
            supported: "Chronology risk depends on network composition, not only one isolated shortcut."
          },
          return_path: {
            supported: "A return path or paired arrangement can supply the causal structure needed for time-machine behavior."
          },
          no_ctc: {
            unsupported: "Individual one-way behavior is not enough; paired or return-path arrangements can change the chronology question."
          },
          source_solution: {
            unsupported: "Identifying the stress profile is not the same as supplying a practical ordinary-matter source."
          },
          energy_optional: {
            unsupported: "Chronology and negative-energy burden stay coupled in review because the shortcut geometry still needs a source."
          }
        }
      },
      references: [references.everettRoman]
    }
  },
  {
    id: "literature.shoshany_snodgrass.ctc.001",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "What does Shoshany and Snodgrass's 2024 paper \"Warp Drives and Closed Timelike Curves\" demonstrate?",
    choices: [
      { id: "composition", content: "It gives a concrete GR model where composed warp-drive geometries yield a closed timelike geodesic." },
      { id: "safe", content: "It suggests single-leg smoothness is a weak but useful indicator of network chronology safety." },
      { id: "matter", content: "It treats the causal construction as the main issue, leaving matter-realization details outside the central result." },
      { id: "coordinates", content: "It frames the closed-curve issue as sensitive to global arrangement and frame choice rather than local stress structure." }
    ],
    answer: ["composition"],
    explanation: {
      answer: "It demonstrates that composed warp-drive geometries can create closed-timelike-curve structure.",
      why: "The paper supplies a concrete two-warp-drive model rather than leaving the timing issue as only a slogan. The important reasoning step is composition: multiple superluminal geometries can change the global causal story.",
      boundary: "This is a published chronology result about warp-drive geometries, not a physical-realization claim or an engineering recipe.",
      adaptive: {
        choices: {
          composition: {
            supported: "The result depends on composing warp-drive geometries into a causal structure with a closed timelike geodesic."
          },
          safe: {
            unsupported: "Smoothness of individual legs does not settle the composed network's global causal behavior."
          },
          matter: {
            unsupported: "Matter realization is not supplied by the causal construction; it remains a separate physical burden."
          },
          coordinates: {
            unsupported: "Global arrangement and frame choice matter, but the closed curve is not dismissed as a mere coordinate label."
          }
        }
      },
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
      { id: "flat_shift", content: "A flat-spatial-slice shift profile captures the relevant correspondence once the coordinate presentation is chosen carefully." },
      { id: "realization", content: "The correspondence narrows the source problem enough that physical realization can be treated as the next engineering step." },
      { id: "name_equivalence", content: "The correspondence transfers the main traversability intuition unless additional curvature caveats are introduced." }
    ],
    answer: ["curvature", "traversability_caveat"],
    explanation: {
      answer: "The useful takeaways are intrinsic-curvature dependence and a nontrivial traversability caveat.",
      why: "The result is a constrained correspondence, not a statement that ordinary traversable wormholes and warp drives are interchangeable. The need for intrinsic spatial curvature prevents the takeaway from collapsing into a simple flat-slice shift analogy.",
      boundary: "This is published correspondence context and must not be promoted to engineering completion or physical source realization.",
      adaptive: {
        choices: {
          curvature: {
            supported: "The correspondence requires nonzero intrinsic spatial curvature, so flat-slice intuition is not enough."
          },
          traversability_caveat: {
            supported: "The traversability caveat is part of the careful reading; the correspondence is not a simple comfort-preserving equivalence."
          },
          flat_shift: {
            unsupported: "The correspondence depends on allowing nonzero intrinsic spatial curvature, so flat-slice shift intuition is incomplete."
          },
          realization: {
            unsupported: "A correspondence between geometrical forms does not by itself solve the source-realization problem."
          },
          name_equivalence: {
            unsupported: "The traversability caveat prevents a simple transfer of intuition from one label to the other."
          }
        }
      },
      references: [references.garattiniZatrimaylov]
    }
  },
  {
    id: "constraints.snec.semiglobal.001",
    type: "mc",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "What does the 2025 paper \"How Much NEC Breaking Can the Universe Endure?\" add beyond a pointwise NEC check?",
    choices: [
      { id: "semilocal_bound", content: "It treats accumulated negative energy along smeared null probes as a semilocal constraint." },
      { id: "pointwise_only", content: "It keeps pointwise NEC sign as the primary criterion, with smearing mainly used to regularize the calculation." },
      { id: "construction", content: "It identifies how much NEC breaking can be tolerated, which is close to specifying an allowable source profile." },
      { id: "irrelevant", content: "It makes smeared bounds the stronger review layer, so pointwise checks mainly act as screening diagnostics." }
    ],
    answer: ["semilocal_bound"],
    explanation: {
      answer: "The added lesson is semilocal accumulation: not just pointwise sign.",
      why: "The smeared NEC is a quantum-motivated bound on accumulated NEC violation along null probes. It shifts the review toward finite-window exposure, not only whether one sampled stress-tensor contraction is negative.",
      boundary: "This is a constraint reference, not a construction recipe or a replacement for a full source model.",
      adaptive: {
        choices: {
          semilocal_bound: {
            supported: "The smeared NEC concerns accumulated exposure along null probes, so it goes beyond one pointwise sign check."
          },
          pointwise_only: {
            unsupported: "The smeared condition is not just a regularized pointwise sign test; finite-window accumulation is central."
          },
          construction: {
            unsupported: "Bounding tolerable NEC breaking is still a constraint result, not a source construction."
          },
          irrelevant: {
            unsupported: "Smeared bounds add a review layer; pointwise checks remain useful but incomplete local evidence."
          }
        }
      },
      references: [references.smearedNec]
    }
  },
  {
    id: "literature.alcubierre.stress_energy.002",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements are careful readings of Alcubierre's 1994 paper \"The Warp Drive\"?",
    choices: [
      { id: "metric_ansatz", content: "The paper gives a spacetime metric that contracts space ahead of a region and expands it behind." },
      { id: "negative_energy", content: "The stress-energy required by the metric includes exotic energy-condition behavior." },
      { id: "ordinary_matter", content: "The paper's stress-energy calculation is detailed enough to identify the source sector once an exotic medium is allowed." },
      { id: "no_causality", content: "The metric construction makes the central worldline well behaved, so control and causality concerns are secondary to source concerns." }
    ],
    answer: ["metric_ansatz", "negative_energy"],
    explanation: {
      answer: "The paper presents a metric ansatz and exposes exotic stress-energy behavior.",
      why: "A careful reading separates the geometric construction from the missing source mechanism. The model is famous because it shows what GR's equations allow as a geometry, while also revealing a severe stress-energy burden.",
      boundary: "This is published speculative-relativity literature, not demonstrated propulsion physics or an ordinary-matter construction.",
      adaptive: {
        choices: {
          metric_ansatz: {
            supported: "The paper's central object is a spacetime metric with contraction ahead and expansion behind the region."
          },
          negative_energy: {
            supported: "The stress-energy implied by the metric includes exotic energy-condition behavior."
          },
          ordinary_matter: {
            unsupported: "The stress-energy demand is identified, but a physical source sector is not supplied."
          },
          no_causality: {
            unsupported: "A mild central worldline does not settle causal-access and control behavior of the full superluminal geometry."
          }
        }
      },
      references: [references.alcubierre]
    }
  },
  {
    id: "constraints.ford_roman.sampling.002",
    type: "mc",
    track: "Established foundations",
    module: "Quantum inequalities",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Ford and Roman's 1996 paper \"Quantum Field Theory Constrains Traversable Wormhole Geometries,\" why does sampling time matter?",
    choices: [
      { id: "duration_bound", content: "Quantum inequalities constrain how much negative energy can be seen over a sampling interval, tying magnitude to duration and scale." },
      { id: "coordinate_choice", content: "Sampling time mainly reflects the chosen observer frame, so the invariant burden is carried by the local energy density." },
      { id: "permanent_negative", content: "Long-lived negative energy can be acceptable when its density is low enough compared with the geometry's scale." },
      { id: "construction", content: "The sampling bound gives target scales that could be used as the starting point for a source design." }
    ],
    answer: ["duration_bound"],
    explanation: {
      answer: "Sampling time matters because the bound couples negative-energy magnitude to duration and scale.",
      why: "The quantum inequality is not just a pointwise warning. It says sustained negative energy is quantitatively constrained, which is why macroscopic wormhole geometries become so difficult under the paper's assumptions.",
      boundary: "This is an established constraint result in the cited setting, not an all-purpose construction or a proof that every negative-energy effect is impossible.",
      adaptive: {
        choices: {
          duration_bound: {
            supported: "The sampling interval is part of the bound, so magnitude, duration, and scale have to be read together."
          },
          coordinate_choice: {
            unsupported: "Sampling time is part of the physical inequality setup; it is not reduced to a coordinate convention."
          },
          permanent_negative: {
            unsupported: "The bound ties density, duration, and scale; low density alone does not automatically clear a long-lived macroscopic profile."
          },
          construction: {
            unsupported: "Target scales from a bound guide review, but they do not provide a source construction."
          }
        }
      },
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
      adaptive: {
        choices: {
          false: {
            supported: "The null-geodesic result supports causal-access restrictions, not free central control."
          },
          true: {
            unsupported: "A central observer cannot be assumed to control all relevant bubble regions when the causal structure blocks signal access."
          }
        }
      },
      references: [references.clarkHiscockLarson]
    }
  },
  {
    id: "literature.shoshany_snodgrass.energy.002",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which conclusions are supported by Shoshany and Snodgrass's 2024 paper \"Warp Drives and Closed Timelike Curves\"?",
    choices: [
      { id: "ctg", content: "Two warp-drive geometries can be arranged so that a closed timelike geodesic exists." },
      { id: "wec_violation", content: "The construction remains tied to weak-energy-condition violation." },
      { id: "composition", content: "The chronology conclusion depends on composing geometries, not merely on inspecting one isolated smooth region." },
      { id: "ordinary_matter", content: "Because the paper foregrounds causal composition, the matter burden can be treated as separate from the chronology conclusion." },
      { id: "single_leg_safe", content: "A single isolated leg may look causally controlled, so network safety can be inferred from leg-by-leg checks." }
    ],
    answer: ["ctg", "wec_violation", "composition"],
    explanation: {
      answer: "The paper supports the composed closed-timelike-geodesic construction and keeps energy-condition violation in view.",
      why: "The point is not only that closed causal curves can be discussed abstractly. The paper gives a concrete two-drive arrangement and does not turn that arrangement into ordinary positive-energy engineering.",
      boundary: "This is a published chronology and energy-condition result about a theoretical construction, not a buildability claim.",
      adaptive: {
        choices: {
          ctg: {
            supported: "The paper gives a concrete composed geometry with a closed timelike geodesic."
          },
          wec_violation: {
            supported: "The construction remains tied to weak-energy-condition violation."
          },
          composition: {
            supported: "The chronology result comes from composing geometries, not from a single isolated smooth patch."
          },
          ordinary_matter: {
            unsupported: "The causal composition result does not separate away the energy-condition burden."
          },
          single_leg_safe: {
            unsupported: "Leg-by-leg checks do not settle the global chronology of a composed network."
          }
        }
      },
      references: [references.shoshanySnodgrass]
    }
  },
  {
    id: "literature.garattini_zatrimaylov.intrinsic_curvature.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Warp-wormhole correspondence",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Garattini and Zatrimaylov's 2024 paper \"On the Wormhole--Warp Drive Correspondence,\" what extra ingredient is central to relating Morris-Thorne wormholes to warp-drive form?",
    choices: [
      { id: "intrinsic_curvature", content: "Nonzero intrinsic spatial curvature in the warp-drive metric." },
      { id: "flat_space", content: "A flat-slice warp form supplemented by a careful coordinate transformation." },
      { id: "ordinary_fuel", content: "A source model that preserves the correspondence while keeping the wormhole throat static." },
      { id: "no_shift", content: "Eliminating the shift term so the remaining spatial curvature carries the correspondence." }
    ],
    answer: ["intrinsic_curvature"],
    explanation: {
      answer: "The key ingredient is nonzero intrinsic spatial curvature.",
      why: "That requirement makes the correspondence more subtle than a simple rebranding of a flat-slice warp shift. It also helps explain why the paper's traversability caveat matters for interpretation.",
      boundary: "This is a correspondence result inside published speculative geometry, not a source-realization theorem.",
      adaptive: {
        choices: {
          intrinsic_curvature: {
            supported: "The correspondence depends on allowing nonzero intrinsic spatial curvature in the warp-drive metric."
          },
          flat_space: {
            unsupported: "The paper's correspondence needs nonzero intrinsic spatial curvature; flat-slice form is not the extra ingredient."
          },
          ordinary_fuel: {
            unsupported: "The extra ingredient is geometric, not a specified source model."
          },
          no_shift: {
            unsupported: "The correspondence is not obtained by simply eliminating shift-like structure."
          }
        }
      },
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
      { id: "recipe", content: "They identify where a classical time-machine construction would need stabilization." },
      { id: "coordinate", content: "They show why distinguishing coordinates from causal structure is the main horizon issue." },
      { id: "irrelevant", content: "Once the classical horizon is located, the main quantum-field question is how strongly it backreacts rather than whether chronology is already suspect." }
    ],
    answer: ["backreaction"],
    explanation: {
      answer: "They are worrisome because quantum-field stress and backreaction can become central near chronology horizons.",
      why: "Chronology protection is not merely a naming convention for time travel. The review surveys why quantum effects near the onset of closed causal curves can threaten the classical spacetime picture.",
      boundary: "This is constraint and review literature, not a finished theorem that supplies engineering design rules.",
      adaptive: {
        choices: {
          backreaction: {
            supported: "Chronology horizons are physically serious because quantum stress and backreaction may destabilize the classical picture."
          },
          recipe: {
            unsupported: "The concern is not just stabilization of a classical design; quantum stress and backreaction are part of the horizon problem."
          },
          coordinate: {
            unsupported: "Coordinate care matters, but the physical worry is quantum stress near chronology-horizon formation."
          },
          irrelevant: {
            unsupported: "The classical horizon identifies the concern; quantum-field stress and backreaction are not merely a later severity estimate."
          }
        }
      },
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
      adaptive: {
        choices: {
          packet_facing: {
            supported: "A clean trace supports the packet-facing observable for that run while leaving plant-side burdens separate."
          },
          matter_action: {
            unsupported: "Packet arrival does not derive the matter action or source sector."
          },
          all_channels: {
            unsupported: "Plant channels such as support, endpoint rematch, and reset require their own evidence."
          },
          global_causality: {
            unsupported: "One packet trace does not prove global causal safety."
          }
        }
      },
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
      { id: "realized", content: "The ledger is strong evidence for realization if its channels match the intended source roles." },
      { id: "irrelevant", content: "The ledger is the primary source-accounting object, so energy conditions can be treated as secondary diagnostics." },
      { id: "global", content: "The ledger constrains the source side tightly enough that global causal review can be separated into a later stage." }
    ],
    answer: ["demand_not_realization"],
    explanation: {
      answer: "Demand accounting is not source realization.",
      why: "A ledger can identify what stress-energy a prescribed metric would require without deriving matter dynamics that supply it.",
      boundary: "This is one of the central active-rail claim boundaries, not established GR terminology.",
      adaptive: {
        choices: {
          demand_not_realization: {
            supported: "The ledger identifies the demanded stress-energy; realization needs a source sector that can supply it."
          },
          realized: {
            unsupported: "Matched source-demand channels are useful accounting, but they are not matter dynamics or physical construction."
          },
          irrelevant: {
            unsupported: "The ledger and energy conditions answer different source questions; neither replaces the other."
          },
          global: {
            unsupported: "Tight source accounting does not remove the need for global causal-structure review."
          }
        }
      },
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
      boundary: "These are project-application and open-gate claims, not stable general-theory statements.",
      adaptive: {
        classifications: {
          einstein: {
            correct: "Einstein's equation is established GR theory.",
            statuses: {
              literature_model: "This is not merely a cited speculative-model result; it is standard field-equation structure.",
              active_rail_model: "Active-rail uses the equation, but did not invent it.",
              project_hypothesis: "The equation is not provisional project evidence.",
              open_gate: "The relation itself is not an unresolved project gate."
            }
          },
          qi: {
            correct: "Ford-Roman quantum inequalities are published constraint literature in the relevant setting.",
            statuses: {
              established_theory: "The question is asking about a specific published constraint result, not just the field equations.",
              active_rail_model: "The result predates the project and is not active-rail vocabulary.",
              project_hypothesis: "The constraint is not a current project strategy.",
              open_gate: "The paper constrains sources; it is not the missing matter-action gate itself."
            }
          },
          ledger: {
            correct: "The demanded-source ledger is active-rail model language for organizing source demand.",
            statuses: {
              established_theory: "Einstein's equation is established, but the ledger convention is project model language.",
              literature_model: "This is not a named external warp metric paper.",
              project_hypothesis: "The ledger is a model/accounting surface, not a candidate physical source strategy by itself.",
              open_gate: "Recording source demand is not itself the unresolved realization claim."
            }
          },
          source_family: {
            correct: "The current source-family strategy is a project hypothesis because it is a candidate organizing route.",
            statuses: {
              established_theory: "A current source-family strategy is not textbook GR.",
              literature_model: "It may use literature constraints, but this statement is about project strategy.",
              active_rail_model: "The source family is more provisional than stable architecture vocabulary.",
              open_gate: "It is a candidate route, not the claim that realization has been completed."
            }
          },
          matter_action: {
            correct: "A completed repeated-service matter action remains an open gate.",
            statuses: {
              established_theory: "Established GR does not automatically derive this project-specific matter action.",
              literature_model: "A literature model does not complete active-rail repeated-service realization.",
              active_rail_model: "The statement asserts completion, not just architecture vocabulary.",
              project_hypothesis: "The safest status is stronger caution: the completion claim remains unshown."
            }
          }
        }
      },
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
      adaptive: {
        sequence: [
          {
            id: "pre-support-before-carry",
            before: "pre_support",
            after: "carry",
            content: "Corridor preparation comes before live carrying because the packet should enter an already supported channel."
          },
          {
            id: "catch-before-fade",
            before: "catch",
            after: "fade",
            content: "Catch/rematch precedes fade so endpoint support is established before active carrying support is removed."
          },
          {
            id: "decompress-before-reset-audit",
            before: "decompress",
            after: "reset_audit",
            content: "Reset residue is audited after decompression because the support state must unwind before reuse evidence is meaningful."
          }
        ]
      },
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
      adaptive: {
        sequence: [
          {
            id: "ready-before-support",
            before: "ready",
            after: "support",
            content: "Rail and endpoint readiness should be confirmed before standing support is treated as armed service infrastructure."
          },
          {
            id: "support-before-carry",
            before: "support",
            after: "carry",
            content: "Standing support precedes carrying because packet transport should not begin before the service corridor is established."
          },
          {
            id: "handoff-before-unwind",
            before: "handoff",
            after: "unwind",
            content: "Catch/rematch comes before support unwind so the endpoint is not inferred after the carrying support is gone."
          },
          {
            id: "unwind-before-residue",
            before: "unwind",
            after: "residue",
            content: "Residue checking follows support unwind because it is evidence about the post-service reset state."
          }
        ]
      },
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
      { id: "scope", content: "Keep the paper result as a causal-access caution, not as validation of source closure." },
      { id: "controller_region", content: "Ask whether the claimed controller can affect the region whose behavior it is supposed to manage." },
      { id: "central_ray_only", content: "Use a clean central ray as the primary branch-access proxy when side-ray spread is small in the sampled region." },
      { id: "arrival_clears", content: "Treat clean packet arrival as reachability evidence for that run if no wall-facing anomaly is observed." },
      { id: "stress_source", content: "Use the null-geodesic paper to localize where source analysis must support wall control." }
    ],
    answer: ["reachability", "bundle", "scope", "controller_region"],
    explanation: {
      answer: "Reachability, finite-bundle behavior, controller access, and claim scope are appropriate review moves.",
      why: "The paper supplies a warning about causal optics and access, while the active-rail audit must still produce its own evidence for branch access, packet behavior, and service safety. It also cannot substitute for source analysis.",
      boundary: "This applies published literature to active-rail review. It is not a claim that the literature validates the project design.",
      adaptive: {
        choices: {
          reachability: {
            supported: "CHL-style concerns directly motivate checking which regions can send or receive controlling signals."
          },
          bundle: {
            supported: "Finite-bundle behavior matters because one ideal ray can miss access or spread failures."
          },
          scope: {
            supported: "The paper transfers as a causal-access caution, not as a source-closure validation."
          },
          controller_region: {
            supported: "A controller claim must show the controller can affect the region it is supposed to manage."
          },
          central_ray_only: {
            unsupported: "A clean central ray is useful evidence, but it does not settle branch access or finite-bundle behavior."
          },
          arrival_clears: {
            unsupported: "Packet arrival is run evidence; wall reachability and control still need their own causal-access review."
          },
          stress_source: {
            unsupported: "Null-geodesic analysis can localize access concerns, but it does not supply the stress-energy source."
          }
        }
      },
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
      adaptive: {
        matches: {
          packet_norm: {
            correct: "The live packet norm ledger is packet-facing safety evidence.",
            options: {
              plant_exchange: "Plant exchange is a support/accounting layer, not the packet norm surface.",
              effective_source: "Source-family evidence is broader than packet norm behavior.",
              stress_response: "The local stress rung tests response behavior rather than the packet norm itself."
            }
          },
          support_closure: {
            correct: "Endpoint/support closure is plant exchange and support accounting evidence.",
            options: {
              packet_safety: "Packet safety can pass while support closure still needs evidence.",
              effective_source: "Effective-source evidence does not replace support closure accounting.",
              stress_response: "A stress rung is not the endpoint/support closure ledger."
            }
          },
          source_family: {
            correct: "Source-family validation is fixed-background effective-source evidence.",
            options: {
              packet_safety: "Packet safety is the trajectory/norm surface, not source-family validation.",
              plant_exchange: "Plant exchange is a separate support accounting surface.",
              stress_response: "The local stress rung is a response test, not the source-family validation surface."
            }
          },
          moderate_capstone: {
            correct: "The moderate local 3+1 stress rung is a local response stress test.",
            options: {
              packet_safety: "A stress response test is not the same as packet-facing norm evidence.",
              plant_exchange: "Plant exchange ledgers and local stress response answer different review questions.",
              effective_source: "Effective-source validation is not identical to the local 3+1 stress rung."
            }
          }
        }
      },
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
      adaptive: {
        classifications: {
          nec: {
            correct: "The NEC statement is established stress-energy constraint vocabulary.",
            statuses: {
              literature_model: "This is not just one speculative metric model; it is general constraint language.",
              project_hypothesis: "The NEC definition is not current project evidence.",
              open_gate: "The definition itself is not unresolved."
            }
          },
          qi: {
            correct: "Quantum inequalities are established constraint results in their stated settings.",
            statuses: {
              established_theory: "This is more specifically a constraint result than general field-equation vocabulary.",
              literature_model: "The cited papers are literature, but the safest class here is established constraint.",
              project_hypothesis: "The constraint is not a project hypothesis.",
              open_gate: "The constraint exists; what remains open is how a project source sector responds."
            }
          },
          natario: {
            correct: "Natario's zero-expansion warp drive is a published speculative metric model.",
            statuses: {
              established_theory: "The paper is not established physical transportation theory.",
              established_constraint: "Zero expansion is a model feature here, not a constraint theorem.",
              project_hypothesis: "The metric predates the project and is not current project-state evidence.",
              open_gate: "The statement identifies a published model rather than an unresolved project gate."
            }
          },
          source_family: {
            correct: "The source-family package is project-hypothesis evidence because it depends on current project reports.",
            statuses: {
              established_theory: "Fixed-background project evidence is not established GR.",
              established_constraint: "This is not a general constraint theorem.",
              literature_model: "It is project evidence, not a published speculative metric model.",
              open_gate: "The statement claims candidate evidence, not completed realization."
            }
          },
          matter_action: {
            correct: "A completed repeated-service matter action remains an open gate.",
            statuses: {
              established_theory: "Established theory does not supply this project-specific completion claim.",
              established_constraint: "This is a missing realization claim, not a constraint result.",
              literature_model: "No cited warp model completes the active-rail matter action.",
              project_hypothesis: "The statement asserts completion; the safer status is that this completion is still open."
            }
          }
        }
      },
      references: [references.energyConditionsPrimer, references.fordRoman, references.natario],
      sourceLinks: [sources.projectReadme, sources.sourceFamilyValidation],
      openGate: "Matter-action closure and repeated-service physical realization remain unresolved."
    }
  },
  {
    id: "project_state.v10_scope.002",
    type: "mc",
    track: "Design review and synthesis",
    module: "Project-state handling",
    difficulty: "intermediate",
    claimStatus: "project_hypothesis",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    prompt: "A current service-rating ladder appears to report that the V10 case fails live packet source safety. What is the safest interpretation?",
    choices: [
      { id: "boundary", content: "It appears to mark a high-service boundary for the current package and could motivate additional causal/source-margin work." },
      { id: "impossible", content: "It is strong evidence against this high-service strategy unless a substantially different source margin is introduced." },
      { id: "solved", content: "It can still support readiness if the failed diagnostic is outside the intended operating envelope." },
      { id: "general_theorem", content: "It should be interpreted as a general design constraint once the same failure appears in multiple package reports." }
    ],
    answer: ["boundary"],
    explanation: {
      answer: "It appears to be a current-package high-service boundary, not a universal impossibility theorem.",
      why: "The reported failure could be meaningful project evidence about the present V10 ladder. The careful interpretation preserves that warning while avoiding an overclaim about all future high-service geometries or all possible source strategies.",
      boundary: "This is revision-sensitive project-state content based on the current service-rating report, not established external theory.",
      adaptive: {
        choices: {
          boundary: {
            supported: "This keeps the V10 result tied to the current package and treats it as a review boundary rather than a universal theorem."
          },
          impossible: {
            unsupported: "The failure is important evidence about the current package, but it does not rule out substantially different strategies."
          },
          solved: {
            unsupported: "A failed live packet source-safety diagnostic cannot support readiness unless the claim is explicitly narrowed away from that envelope."
          },
          general_theorem: {
            unsupported: "Repeated project reports can strengthen a project pattern, but they do not become a configuration-independent GR theorem."
          }
        }
      },
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
    difficulty: "intermediate",
    claimStatus: "project_hypothesis",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    scoring: "subtract_incorrect",
    prompt: "A report appears to describe the sealed beta075 V5 package as packet-safe with fixed-background endpoint/support and source-family evidence. Which scope statements are appropriate?",
    choices: [
      { id: "fixed_background", content: "It could be evidence at prescribed-metric or fixed-background effective-source level." },
      { id: "watches", content: "Thin margins and watch conditions should remain visible in the claim." },
      { id: "revision_sensitive", content: "The claim should remain revision-sensitive because it depends on the current package and reports." },
      { id: "matter_action", content: "It supports matter-action closure if the source-family evidence already matches the required stress channels." },
      { id: "broad_family", content: "It gives evidence for broad service-family viability if V5 is the representative midrange package." },
      { id: "hide_watches", content: "Watch conditions can be moved into internal notes if the public claim is limited to packet-safe fixed-background behavior." }
    ],
    answer: ["fixed_background", "watches", "revision_sensitive"],
    explanation: {
      answer: "The careful scope appears to be fixed-background evidence with visible watches and revision-sensitive status.",
      why: "The current record appears to distinguish V5 prescribed-metric evidence from unproved matter-action, semiclassical, and broad-family claims. The right answer preserves the possible value of the evidence without letting it expand into unearned physical-realization language.",
      boundary: "This is revision-sensitive project-state content and must be excluded from stable general-theory or paper-theory sessions unless intentionally selected.",
      adaptive: {
        choices: {
          fixed_background: {
            supported: "This credits the package at the prescribed-metric or fixed-background effective-source level."
          },
          watches: {
            supported: "Visible watch conditions keep thin margins from being hidden by a pass label."
          },
          revision_sensitive: {
            supported: "The claim depends on current reports and should remain revision-sensitive."
          },
          matter_action: {
            unsupported: "Matching source-family evidence is not the same as a complete matter action."
          },
          broad_family: {
            unsupported: "A midrange package can be suggestive, but it does not prove broad viability across the full family."
          },
          hide_watches: {
            unsupported: "Visible watch conditions are part of the honest public scope, especially for thin-margin package claims."
          }
        }
      },
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
      { id: "coupled_evolution", content: "Evidence that the source remains controlled in a coupled or backreaction-aware setting." },
      { id: "reset_history", content: "A reset or repeated-use history audit if the claim includes service reuse." },
      { id: "repeat_rung", content: "Additional repetitions of the same fixed-background stress rung to show the local pass is robust." },
      { id: "local_to_global", content: "A mapping from the passing local stress rung to endpoint, reset, and history channels." }
    ],
    answer: ["matter_action", "semiclassical", "coupled_evolution", "reset_history"],
    explanation: {
      answer: "Matter action, semiclassical/RSET work, coupled-source behavior, and reuse history could remain missing for a full physical-realization claim.",
      why: "Packet-facing and fixed-background evidence can be strong while still falling short of physical source realization. A careful review credits useful diagnostics without promoting repeated fixed-background evidence into a matter sector or a repeated-service claim.",
      boundary: "This is design-review reasoning inside the active-rail project model, not an established external certification rule.",
      adaptive: {
        choices: {
          matter_action: {
            supported: "A matter action or microphysical model is central to physical source realization."
          },
          semiclassical: {
            supported: "When quantum-field effects are relevant, RSET or semiclassical response cannot be replaced by fixed-background packet evidence."
          },
          coupled_evolution: {
            supported: "Backreaction-aware or coupled behavior is a separate burden from a fixed-background pass."
          },
          reset_history: {
            supported: "Reuse claims need reset/history evidence, not only a single successful diagnostic."
          },
          repeat_rung: {
            unsupported: "Repeating the same local fixed-background rung can improve confidence in that rung, but it does not fill different missing evidence classes."
          },
          local_to_global: {
            unsupported: "A mapping from one rung to other channels would itself need evidence; it cannot be assumed from the local pass."
          }
        }
      },
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
      adaptive: {
        choices: {
          interval: {
            supported: "The metric is the field used to compute intervals, causal character, and proper-time/proper-distance relations."
          },
          matter_action: {
            unsupported: "A metric can imply source demand, but it does not select a unique matter action."
          },
          engineering_pass: {
            unsupported: "Endpoint reset checks are service-qualification evidence, not what a metric primarily computes."
          },
          publication_status: {
            unsupported: "A metric does not determine whether a speculative model has become an engineering demonstration."
          }
        }
      },
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
      adaptive: {
        matches: {
          timelike: {
            correct: "In mostly-plus convention, a timelike nonzero vector has negative squared norm.",
            options: {
              zero_norm: "Zero squared norm is the null case.",
              positive_norm: "Positive squared norm is the spacelike case."
            }
          },
          null: {
            correct: "A null vector has zero squared norm.",
            options: {
              negative_norm: "Negative squared norm is timelike in mostly-plus convention.",
              positive_norm: "Positive squared norm is spacelike in mostly-plus convention."
            }
          },
          spacelike: {
            correct: "A spacelike vector has positive squared norm in mostly-plus convention.",
            options: {
              negative_norm: "Negative squared norm is timelike.",
              zero_norm: "Zero squared norm is null."
            }
          }
        }
      },
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
      {
        id: "timelike_contraction",
        content: [
          "For a timelike observer with four-velocity ",
          { type: "math", latex: "u^\\mu", label: "u mu" },
          ", the measured energy density is represented by a contraction such as ",
          { type: "math", latex: "T_{\\mu\\nu}u^\\mu u^\\nu", label: "T mu nu u mu u nu" },
          "."
        ]
      },
      { id: "observer_dependent", content: "The measured density depends on the observer field as well as the stress-energy tensor." },
      { id: "normalized", content: "The observer four-velocity should be timelike and normalized before interpreting the contraction as measured density." },
      { id: "trace_only", content: "The trace is a useful observer-independent scalar, so it can substitute for measured density in many reviews." },
      { id: "geometry_alone", content: "A named metric often identifies the natural observer field, so the density can be read before doing a full projection." },
      { id: "component_absolute", content: "The time-time component in a convenient coordinate chart is a good proxy for measured density unless strong boosts are involved." }
    ],
    answer: ["timelike_contraction", "observer_dependent", "normalized"],
    explanation: {
      answer: "Observer density is a normalized timelike contraction and depends on the observer field.",
      why: "The stress tensor contains more information than a single scalar. Energy density for an observer is obtained by contracting with that observer's timelike four-velocity, while traces and other components answer different questions.",
      boundary: "This is established stress-energy interpretation, not a service-specific diagnostic by itself.",
      adaptive: {
        choices: {
          timelike_contraction: {
            supported: "The observer-measured density is obtained by contracting stress-energy with that observer's timelike four-velocity."
          },
          observer_dependent: {
            supported: "Different observer fields can measure different local densities from the same stress tensor."
          },
          normalized: {
            supported: "Normalization matters because the contraction is interpreted as a measured density for a unit timelike observer."
          },
          trace_only: {
            unsupported: "The trace is useful, but it does not substitute for the observer-specific timelike contraction."
          },
          geometry_alone: {
            unsupported: "A natural observer choice still has to be specified and used in a projection; the metric name is not enough."
          },
          component_absolute: {
            unsupported: "A convenient time-time component can be useful in a chosen frame, but it is not automatically observer-independent measured density."
          }
        }
      },
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
      adaptive: {
        blanks: {
          density: {
            correct: "Rho is the matter energy density seen by the slice normal in the ADM constraint.",
            tokens: {
              beta: "Beta is shift notation, not the matter density in the Hamiltonian constraint.",
              alpha: "Alpha is lapse notation, not the density source projection.",
              trace_free: "A trace-free condition is not the normal-observer density term."
            },
            missing: "This blank asks for the source density projection in the Hamiltonian constraint."
          }
        }
      },
      references: [references.adm]
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
      adaptive: {
        classifications: {
          nec_definition: {
            correct: "The NEC is an established stress-energy constraint.",
            statuses: {
              established_theory: "The NEC is general theory adjacent, but here the safest class is an established constraint.",
              literature_model: "The NEC is not just a specific speculative metric model.",
              open_gate: "The definition is not unresolved."
            }
          },
          warp_violation: {
            correct: "The Alcubierre exotic-stress statement belongs to published literature-model context.",
            statuses: {
              established_theory: "The model is published GR literature, not established physical engineering.",
              established_constraint: "The statement is about a speculative model's source burden, not a general constraint theorem itself.",
              open_gate: "The statement identifies literature context rather than an unresolved universal realization claim."
            }
          },
          einstein_equation: {
            correct: "Einstein's equation is established theory.",
            statuses: {
              established_constraint: "The field equation is broader than an energy-condition constraint.",
              literature_model: "It is not merely a specific speculative model.",
              open_gate: "The equation itself is not an unresolved matter-realization gate."
            }
          },
          realization: {
            correct: "Universal realization of arbitrary exotic stress-energy remains an open gate.",
            statuses: {
              established_theory: "Established field equations do not guarantee a conventional matter sector for every exotic tensor.",
              established_constraint: "This is a realization claim, not just a constraint statement.",
              literature_model: "No one named speculative metric supplies this universal matter-sector result."
            }
          }
        }
      },
      references: [references.energyConditionsPrimer, references.alcubierre]
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
      { id: "unlimited", content: "A smooth metric can make the negative-energy region controllable enough that accumulated exposure is a secondary issue." },
      { id: "classical_only", content: "The main burden remains classical stress-tensor sign; quantum-field sampling mostly refines that pointwise review." },
      { id: "source_constructed", content: "The paper identifies the allowable duration scale closely enough to guide a candidate source layer." }
    ],
    answer: ["duration_magnitude"],
    explanation: {
      answer: "Ford-Roman constraints tie negative-energy magnitude to sampling duration.",
      why: "The qualitative lesson is not merely that negative energy appears, but that quantum inequalities restrict how much can persist for how long in the settings considered.",
      boundary: "This is constraint literature, not a proof that every speculative spacetime is impossible or buildable.",
      adaptive: {
        choices: {
          duration_magnitude: {
            supported: "The key relationship is between negative-energy magnitude and how long it is sampled."
          },
          unlimited: {
            unsupported: "Smoothness does not make accumulated exposure secondary; sampling duration is part of the constraint."
          },
          classical_only: {
            unsupported: "Classical stress-tensor signs matter, but Ford-Roman bounds add quantum-field sampling constraints."
          },
          source_constructed: {
            unsupported: "The allowable duration scale is a constraint on candidates, not a source-layer construction."
          }
        }
      },
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
    prompt: "A proposed exotic geometry reports only a pointwise negative-energy peak but gives no sampling-time or macroscopic scale analysis. In the Ford-Roman 1996 quantum-inequality setting, which cautions follow most directly?",
    choices: [
      { id: "sampling", content: "A local snapshot of negative energy is not enough; sampling time and accumulated exposure matter." },
      { id: "scale", content: "Macroscopic exotic geometries face stronger burden than a formal stress-tensor sign check alone suggests." },
      { id: "not_construction", content: "The inequality constrains candidate negative-energy sources but does not construct one." },
      { id: "worldline", content: "The sampling setup and worldline used for the bound have to match the physical claim being reviewed." },
      { id: "pointwise_enough", content: "A sufficiently small pointwise peak may clear the concern if the sampling window is much wider than the pulse." },
      { id: "classical_enough", content: "A classical stress-tensor sign table gives the relevant negative-energy support, while quantum sampling refines the margin." },
      { id: "sampling_optional", content: "Sampling windows can be chosen after the geometry is fixed because macroscopic scale already sets the main burden." }
    ],
    answer: ["sampling", "scale", "not_construction", "worldline"],
    explanation: {
      answer: "Sampling, scale, source-construction, and worldline-matching cautions follow.",
      why: "A negative-energy diagnosis must consider duration, scale, and the sampling setup, not only whether a pointwise algebraic condition can be written. The inequality constrains candidate sources; it does not construct them.",
      boundary: "This is a literature-backed constraint interpretation and should not be stretched into an all-purpose impossibility theorem.",
      adaptive: {
        choices: {
          sampling: {
            supported: "A pointwise peak does not answer the sampling-duration or accumulated-exposure question."
          },
          scale: {
            supported: "Macroscopic exotic geometries make scale central rather than decorative."
          },
          not_construction: {
            supported: "A quantum inequality bounds candidate negative energy; it does not provide the matter source."
          },
          worldline: {
            supported: "The physical claim has to match the worldline and sampling setup used by the bound."
          },
          pointwise_enough: {
            unsupported: "The relationship between peak size and sampling window is the point; it cannot be assumed without specifying scale."
          },
          classical_enough: {
            unsupported: "The classical sign table identifies support, but the quantum inequality adds a duration and sampling burden."
          },
          sampling_optional: {
            unsupported: "Macroscopic scale makes sampling review more important, not optional after geometry selection."
          }
        }
      },
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
      { id: "flat_everywhere", content: "The interior's near-flat behavior can be extended to the full model except where the wall carries gradients." },
      { id: "matter_action", content: "The stress-energy calculation is close to a source recipe once an exotic sector is allowed." },
      { id: "no_metric", content: "The paper is better read as a qualitative possibility argument than as a specific metric target." }
    ],
    answer: ["local_flat_global_exotic"],
    explanation: {
      answer: "The local passenger region and global source burden must be separated.",
      why: "Alcubierre's construction is famous partly because the bubble interior can be described gently while the surrounding geometry carries severe exotic-matter implications.",
      boundary: "This is published speculative metric analysis, not a demonstrated propulsion system.",
      adaptive: {
        choices: {
          local_flat_global_exotic: {
            supported: "This separates the mild passenger-region description from the global wall/source burden."
          },
          flat_everywhere: {
            unsupported: "The mild interior does not extend to the full spacetime; the wall and global geometry carry the stress-energy burden."
          },
          matter_action: {
            unsupported: "The stress-energy demand is not a matter action or source recipe, even if an exotic sector is imagined."
          },
          no_metric: {
            unsupported: "The paper's central contribution is a specific metric ansatz, not only a qualitative possibility argument."
          }
        }
      },
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
      adaptive: {
        choices: {
          false: {
            supported: "Stress-energy requirements are central to the model's interpretation."
          },
          true: {
            unsupported: "The metric does not remove the need for source and energy-condition analysis."
          }
        }
      },
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
      { id: "realized", content: "Zero expansion reduces the source burden enough that ordinary-matter realization becomes the natural next inference." },
      { id: "flat", content: "Zero expansion makes the volume flow locally mild enough that curvature can be treated as a smaller correction." },
      { id: "chronology_safe", content: "Zero expansion weakens the horizon and causal-access concerns enough to leave source analysis as the main issue." }
    ],
    answer: ["variant"],
    explanation: {
      answer: "It shows an important geometric variant, not physical source realization.",
      why: "Natario's construction changes a geometric feature of the warp-drive class. The existence of a zero-expansion construction does not erase energy-condition or matter-sector questions.",
      boundary: "This is published metric-geometry context and must stay distinct from engineering feasibility.",
      adaptive: {
        choices: {
          variant: {
            supported: "Zero expansion is an important geometric reformulation while source concerns remain."
          },
          realized: {
            unsupported: "Reduced or changed kinematic burden does not imply ordinary-matter realization."
          },
          flat: {
            unsupported: "Local volume behavior is not the same as flat spacetime or negligible curvature."
          },
          chronology_safe: {
            unsupported: "Zero expansion does not by itself settle global causal access or horizon-like behavior."
          }
        }
      },
      references: [references.natario]
    }
  },
  {
    id: "literature.natario.lesson.004",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which lessons are appropriate to draw from Natario's 2002 zero-expansion warp-drive construction?",
    choices: [
      { id: "geometry_family", content: "There is more than one way to formulate warp-drive-like geometry." },
      { id: "source_still_matters", content: "Changing expansion properties does not by itself solve the source-realization problem." },
      { id: "specific_property", content: "Zero expansion is a specific kinematic property of the congruence, not a blanket feasibility result." },
      { id: "ordinary_matter", content: "Zero expansion lowers the apparent source burden enough that ordinary positive-energy sourcing becomes the natural next hypothesis." },
      { id: "no_causality", content: "It shifts the main review toward source terms, with causal-structure analysis becoming a follow-up concern." },
      { id: "all_warp_same", content: "Zero-expansion models can be grouped together for first-pass source and control review." }
    ],
    answer: ["geometry_family", "source_still_matters", "specific_property"],
    explanation: {
      answer: "The construction broadens the geometry family while preserving the need for source and causal analysis.",
      why: "A strong reading notices both sides: Natario provides a meaningful alternative warp geometry, but the result is not a license to ignore stress-energy or global behavior.",
      boundary: "This is speculative literature interpretation, not a completed matter model or engineering feasibility claim.",
      adaptive: {
        choices: {
          geometry_family: {
            supported: "Natario's construction shows warp-drive-like geometry is not limited to one expansion behavior."
          },
          source_still_matters: {
            supported: "Changing expansion properties does not construct the source sector."
          },
          specific_property: {
            supported: "Zero expansion is a particular congruence property, not a full feasibility certificate."
          },
          ordinary_matter: {
            unsupported: "Zero expansion changes one geometric property; it does not establish ordinary positive-energy sourcing."
          },
          no_causality: {
            unsupported: "Source review remains important, but causal access and control are not just follow-up details."
          },
          all_warp_same: {
            unsupported: "Zero expansion is a shared feature, not a guarantee of shared source and control behavior."
          }
        }
      },
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
      { id: "no_light", content: "The relevant light rays are mainly a visualization tool rather than a control limitation." },
      { id: "ordinary_control", content: "A central passenger may control the front wall if the metric is already smooth and superluminal only relative to external observers." },
      { id: "source_done", content: "Null geodesics locate where source support is needed, which is close to identifying the source burden." }
    ],
    answer: ["horizon"],
    explanation: {
      answer: "The null-geodesic analysis exposes horizon-like signaling limitations.",
      why: "The paper is valuable because it turns a geometric model into a causal-access problem. Superluminal operation cannot assume that every part of the bubble is controllable by ordinary internal signaling.",
      boundary: "This is literature-model analysis of Alcubierre geometry, not a design-architecture result.",
      adaptive: {
        choices: {
          horizon: {
            supported: "Null rays reveal horizon-like access structures relevant to signaling and control assumptions."
          },
          no_light: {
            unsupported: "The lightlike paths are not merely visual; their reachability behavior is the control caution."
          },
          ordinary_control: {
            unsupported: "Smoothness and observer relativity do not settle whether signals from the center reach the front wall."
          },
          source_done: {
            unsupported: "Null geodesics can localize access issues, but they do not identify a physical stress-energy source."
          }
        }
      },
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
      adaptive: {
        choices: {
          true: {
            supported: "The paper's null-geodesic analysis puts reachability and horizon-like limitations at the center."
          },
          false: {
            unsupported: "Signal reachability is one of the main lessons of studying null paths in the Alcubierre spacetime."
          }
        }
      },
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
      adaptive: {
        choices: {
          probe_paths: {
            supported: "Geodesics are the appropriate diagnostic for lightlike and massive-particle paths through the modeled spacetime."
          },
          source_action: {
            unsupported: "Trajectory analysis does not provide the matter action that would realize the geometry."
          },
          energy_condition: {
            unsupported: "Geodesic analysis complements, but does not replace, stress-energy and energy-condition analysis."
          },
          no_geometry: {
            unsupported: "Geodesics are defined from the metric geometry; they do not avoid it."
          }
        }
      },
      references: [references.mullerWeiskopf]
    }
  },
  {
    id: "literature.muller_weiskopf.lensing.003",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "What should a careful reader take from Mueller and Weiskopf's 2012 geodesic study of the Alcubierre spacetime?",
    choices: [
      { id: "visual_diagnostic", content: "Geodesic behavior can reveal optical and observer-facing consequences of the geometry." },
      { id: "not_realization", content: "Trajectory analysis gives enough internal consistency evidence to treat source realization as a separate later step." },
      { id: "causal_access", content: "Null and timelike path behavior can inform causal-access questions inside the modeled spacetime." },
      { id: "ordinary_source", content: "A detailed geodesic study constrains the source problem enough that ordinary-source questions can be separated from path analysis." },
      { id: "no_causal_limits", content: "If null and timelike paths can be charted cleanly, remaining causal restrictions are mostly boundary-condition details." },
      { id: "image_proof", content: "A visually smooth rendering is strong evidence that the modeled observable behavior is physically plausible." }
    ],
    answer: ["visual_diagnostic", "causal_access"],
    explanation: {
      answer: "The study is a diagnostic of paths, observations, and causal access.",
      why: "The geodesic result enriches understanding of how the model behaves, but it does not certify sources, quantum stability, or engineering control.",
      boundary: "This is literature-model analysis with educational value and explicit feasibility and source-realization limits.",
      adaptive: {
        choices: {
          visual_diagnostic: {
            supported: "Geodesic behavior is useful for optical and observer-facing consequences inside the model."
          },
          not_realization: {
            unsupported: "Internal path consistency is useful, but source realization cannot simply be deferred as a later bookkeeping step."
          },
          causal_access: {
            supported: "Null and timelike paths can inform causal-access questions in the modeled spacetime."
          },
          ordinary_source: {
            unsupported: "Geodesic detail constrains observables and access, not the ordinary-matter source problem."
          },
          no_causal_limits: {
            unsupported: "Cleanly charted geodesics are evidence for analysis, but boundary and reachability questions remain substantive."
          },
          image_proof: {
            unsupported: "Visual smoothness can aid interpretation, but it is not physical feasibility evidence by itself."
          }
        }
      },
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
      { id: "no_negative", content: "It makes chronology composition the main issue, with negative energy handled as a separate source burden." },
      { id: "ordinary_train", content: "It uses an engineering-style transport analogy strongly enough that operational routing is part of the interpretation." },
      { id: "adm_constraint", content: "It treats the shortcut geometry directly, so the usual 3+1 constraint split is not the main chronology lesson." }
    ],
    answer: ["two_tube"],
    explanation: {
      answer: "Krasnikov-tube arrangements are relevant because they can raise CTC concerns.",
      why: "The paper connects superluminal travel geometries with causal-loop worries, while also keeping negative-energy and feasibility questions in view.",
      boundary: "This is published speculative-spacetime literature, not a demonstrated transportation system.",
      adaptive: {
        choices: {
          two_tube: {
            supported: "Composed superluminal tube arrangements can raise closed-timelike-curve concerns."
          },
          no_negative: {
            unsupported: "Chronology composition is central, but it does not separate away negative-energy concerns."
          },
          ordinary_train: {
            unsupported: "The transport analogy helps intuition, but the paper is a spacetime model rather than an operational railway design."
          },
          adm_constraint: {
            unsupported: "The chronology lesson can be read without foregrounding ADM, but it does not replace relativistic constraints with Newtonian mechanics."
          }
        }
      },
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
      adaptive: {
        choices: {
          false: {
            supported: "Negative-energy and quantum-inequality concerns remain part of the Krasnikov-tube discussion."
          },
          true: {
            unsupported: "The analysis does not remove the exotic-source burden."
          }
        }
      },
      references: [references.everettRoman, references.fordRoman]
    }
  },
  {
    id: "literature.shoshany_snodgrass.frame_switch.003",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    prompt: "In Shoshany and Snodgrass's 2024 paper \"Warp Drives and Closed Timelike Curves,\" what is the central chronology lesson?",
    choices: [
      { id: "ctg", content: "Combinations of warp-drive regions can permit closed timelike geodesics in the model under the analyzed conditions." },
      { id: "safe", content: "A single warp metric can look causally controlled, so closed curves become a concern only after extra global identifications." },
      { id: "ordinary_matter", content: "The chronology construction can be analyzed separately from the weak-energy-condition violation." },
      { id: "irrelevant", content: "Chronology is a secondary issue compared with source feasibility in superluminal metric constructions." }
    ],
    answer: ["ctg"],
    explanation: {
      answer: "The analyzed multi-warp arrangement can produce closed timelike geodesics.",
      why: "Causal risk can be compositional: it can arise from how superluminal regions are arranged, not just from reading one local metric patch in isolation.",
      boundary: "This is a published model result and chronology warning, not a project-specific service result.",
      adaptive: {
        choices: {
          ctg: {
            supported: "The central result is a composed warp-drive arrangement admitting a closed timelike geodesic."
          },
          safe: {
            unsupported: "A single local metric picture does not settle the global causal behavior of composed arrangements."
          },
          ordinary_matter: {
            unsupported: "The chronology construction and weak-energy-condition violation remain linked in the paper's setting."
          },
          irrelevant: {
            unsupported: "Source feasibility matters, but chronology is not secondary in superluminal constructions."
          }
        }
      },
      references: [references.shoshanySnodgrass]
    }
  },
  {
    id: "literature.garattini_zatrimaylov.no_free_transfer.003",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp-wormhole correspondence",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "In Garattini and Zatrimaylov's 2024 paper \"On the Wormhole--Warp Drive Correspondence,\" which interpretations are careful?",
    choices: [
      { id: "correspondence", content: "The paper explores a formal correspondence between wormhole and warp-drive geometries." },
      { id: "caveats", content: "A correspondence does not automatically supply traversability, ordinary matter, or engineering control." },
      { id: "solved", content: "The correspondence narrows the realization problem enough that ordinary-matter questions become the next engineering layer." },
      { id: "no_geometry", content: "The correspondence lets one translate between forms, so intrinsic curvature can be treated as presentation-dependent." },
      { id: "comfort_transfer", content: "Traversability intuition can transfer when the correspondence preserves the relevant throat or bubble geometry." }
    ],
    answer: ["correspondence", "caveats"],
    explanation: {
      answer: "The formal correspondence is useful but bounded by traversability and source caveats.",
      why: "The careful reading gains conceptual transfer between geometry families without treating that transfer as a proof of physical realization, traversability, stable sourcing, or operational control.",
      boundary: "This is recent literature-model context, not an established engineering result or source-realization proof.",
      adaptive: {
        choices: {
          correspondence: {
            supported: "The paper explores a formal relationship between wormhole and warp-drive geometries."
          },
          caveats: {
            supported: "The correspondence does not automatically supply traversability, ordinary matter, or control."
          },
          solved: {
            unsupported: "A narrowed realization question is still not an ordinary-matter construction."
          },
          no_geometry: {
            unsupported: "Intrinsic curvature is part of the geometry being related, not a presentation detail to discard."
          },
          comfort_transfer: {
            unsupported: "A formal correspondence needs caveats before traversability or comfort intuition transfers."
          }
        }
      },
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
      { id: "universal", content: "Scalar fields form a broad enough source class that safety depends mainly on choosing a suitable coupling." },
      { id: "no_energy", content: "The scalar-field mechanism shifts attention from energy conditions to field stability and scale." },
      { id: "engineering_specific", content: "The paper is close to a source-design analysis because it studies a concrete field mechanism." }
    ],
    answer: ["nonminimal"],
    explanation: {
      answer: "Non-minimal scalar coupling can change energy-condition behavior, but caveats matter.",
      why: "The paper is useful because it explores source-sector possibilities rather than merely prescribing a metric. The lesson is nuanced: altered energy conditions do not automatically equal practical or benign matter.",
      boundary: "This is scalar-field literature context and should not be confused with any architecture-specific source closure.",
      adaptive: {
        choices: {
          nonminimal: {
            supported: "The paper's source-sector lesson is about non-minimal coupling and its caveats."
          },
          universal: {
            unsupported: "A suitable coupling is not enough by itself; regime, scale, and caveats remain."
          },
          no_energy: {
            unsupported: "Field stability and scale matter, but energy-condition behavior remains central to the paper."
          },
          engineering_specific: {
            unsupported: "A concrete field mechanism is still theoretical source literature, not architecture-specific source closure."
          }
        }
      },
      references: [references.barceloVisser]
    }
  },
  {
    id: "constraints.topological_censorship.curves.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Topological censorship",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Friedman, Schleich, and Witt's 1993 paper \"Topological Censorship,\" what is the broad lesson for visible nontrivial topology?",
    choices: [
      { id: "screened", content: "Under suitable assumptions, causal curves from infinity cannot probe nontrivial topology in the naive traversable way." },
      { id: "guaranteed", content: "A visible smooth throat can be treated as probe-access evidence if the relevant causal curves are drawn explicitly." },
      { id: "no_assumptions", content: "The result is best read as a topology constraint first, with causal and energy assumptions entering later." },
      { id: "warp_source", content: "It constrains shortcut topology closely enough to inform the source burden for warp-like walls." }
    ],
    answer: ["screened"],
    explanation: {
      answer: "The theorem constrains externally visible traversal of nontrivial topology under its assumptions.",
      why: "The result is powerful because it ties global topology, causal structure, and energy conditions together. The assumptions matter, so the correct interpretation is constrained rather than slogan-like.",
      boundary: "This is established constraint literature under stated assumptions, not a project-specific geometry verdict.",
      adaptive: {
        choices: {
          screened: {
            supported: "Under the theorem's assumptions, causal curves from infinity cannot probe topology in the naive traversable way."
          },
          guaranteed: {
            unsupported: "Drawn local access curves help visualization, but the theorem is about global causal behavior under assumptions."
          },
          no_assumptions: {
            unsupported: "The causal, energy, and asymptotic assumptions are part of the result, not later decoration."
          },
          warp_source: {
            unsupported: "Topological constraints can inform review, but they do not supply source stress-energy."
          }
        }
      },
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
      { id: "global_causal", content: "Closed-causal-curve questions require global causal analysis, not only local smoothness checks." },
      { id: "ignore", content: "Closed causal curves can be treated as a later global check if the local metric is smooth and source-supported." },
      { id: "complete", content: "The review identifies enough mechanisms to prioritize designs that avoid chronology-horizon formation." }
    ],
    answer: ["backreaction", "open", "global_causal"],
    explanation: {
      answer: "Backreaction, global causal analysis, and unresolved chronology-protection issues are the right cautions.",
      why: "The review frames chronology protection as a deep quantum-field and causal-structure problem. It does not license smooth metrics to bypass closed-curve concerns.",
      boundary: "This is constraint-review context, not a project qualification rule by itself.",
      adaptive: {
        choices: {
          backreaction: {
            supported: "Quantum-field backreaction near chronology horizons is one of the central concerns."
          },
          open: {
            supported: "The review frames chronology protection as a serious unresolved constraint topic, not an operating recipe."
          },
          global_causal: {
            supported: "Closed-causal-curve questions require global causal analysis beyond local smoothness."
          },
          ignore: {
            unsupported: "Local smoothness and source support do not move closed causal curves into a later-only check."
          },
          complete: {
            unsupported: "The mechanisms guide caution around chronology horizons; they do not define a safe construction program."
          }
        }
      },
      references: [references.chronologyProtection]
    }
  },
  {
    id: "constraints.snec.scope.002",
    type: "mc",
    track: "Published warp and wormhole context",
    module: "Quantum inequalities",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "In Moghtaderi, Hull, Quintin, and Geshnizjani's 2025 smeared-NEC paper, what is the main constraint style?",
    choices: [
      { id: "semilocal", content: "It constrains accumulated NEC violation over a smeared region rather than only a pointwise sign." },
      { id: "unrestricted", content: "It allows larger accumulated effects when each local contribution is small and broadly smeared." },
      { id: "matter_action", content: "It identifies tolerable NEC-breaking profiles closely enough to guide candidate matter actions." },
      { id: "project_reset", content: "It is relevant to reset-style audits whenever repeated sampling of negative energy is the concern." }
    ],
    answer: ["semilocal"],
    explanation: {
      answer: "The smeared NEC constrains accumulated violation over a finite sampling region.",
      why: "The important distinction is semilocal: pointwise energy-condition violation is not the whole story when a constraint integrates or smears exposure across a region and sampling scale.",
      boundary: "This is recent constraint literature and should be applied cautiously outside the assumptions of the paper.",
      adaptive: {
        choices: {
          semilocal: {
            supported: "The constraint style is smeared or semilocal rather than purely pointwise."
          },
          unrestricted: {
            unsupported: "Broad smearing does not by itself permit unlimited accumulated NEC breaking."
          },
          matter_action: {
            unsupported: "Tolerable profile constraints can guide review, but they do not construct matter actions."
          },
          project_reset: {
            unsupported: "Repeated sampling is conceptually relevant, but this paper does not validate a specific engineering reset schedule."
          }
        }
      },
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
      adaptive: {
        matches: {
          packet: {
            correct: "The packet is the passenger-facing served region.",
            options: {
              prepared_infrastructure: "Prepared infrastructure is the rail role.",
              handoff_region: "Handoff boundary work belongs to the endpoint role.",
              reuse_check: "Reuse readiness belongs to reset."
            }
          },
          rail: {
            correct: "The rail is the prepared support, carry, and handoff infrastructure.",
            options: {
              served_region: "The served region is the packet, not the rail.",
              handoff_region: "Endpoint handoff is one rail-adjacent surface, but the rail is the broader infrastructure.",
              reuse_check: "Reset is the post-service readiness process."
            }
          },
          endpoint: {
            correct: "The endpoint is responsible for catch or rematch boundary work.",
            options: {
              served_region: "The served region is the packet.",
              prepared_infrastructure: "The rail is the prepared infrastructure.",
              reuse_check: "Reset is post-service readiness, not endpoint handoff."
            }
          },
          reset: {
            correct: "Reset is the post-service residue and readiness process.",
            options: {
              served_region: "The packet is the served region.",
              prepared_infrastructure: "The rail is prepared infrastructure.",
              handoff_region: "Endpoint handles catch/rematch; reset handles reuse readiness."
            }
          }
        }
      },
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
      adaptive: {
        blanks: {
          claim: {
            correct: "The ledger is strongest as source-demand accounting: it states the burden before claiming realization.",
            tokens: {
              matter_action: "A demanded-source ledger is not a completed matter action.",
              causal_proof: "Source-demand accounting does not prove global causal safety.",
              chronology_solution: "The ledger does not solve chronology protection."
            },
            missing: "The blank asks for the bounded role of a demanded-source ledger."
          }
        }
      },
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
      adaptive: {
        sequence: [
          {
            id: "support-before-carry",
            before: "support",
            after: "carry",
            content: "Support comes before carry because the packet should move through a prepared service condition."
          },
          {
            id: "catch-before-fade",
            before: "catch",
            after: "fade",
            content: "Catch comes before fade so endpoint handoff is not inferred after carrying support is removed."
          },
          {
            id: "fade-before-reset",
            before: "fade",
            after: "reset",
            content: "Reset follows fade because it is a post-service readiness process."
          }
        ]
      },
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
      adaptive: {
        sequence: [
          {
            id: "metric-before-ledger",
            before: "metric",
            after: "ledger",
            content: "The prescribed metric comes before the ledger because the ledger records what that geometry demands."
          },
          {
            id: "ledger-before-diagnostics",
            before: "ledger",
            after: "diagnostics",
            content: "Source demand should be known before operational diagnostics are promoted into source claims."
          },
          {
            id: "diagnostics-before-source-family",
            before: "diagnostics",
            after: "source_family",
            content: "Packet, support, endpoint, and reset diagnostics are narrower than candidate source-family validation."
          },
          {
            id: "source-family-before-matter-action",
            before: "source_family",
            after: "matter_action",
            content: "A candidate source family is weaker than a matter action or microphysical model coupled to the geometry."
          }
        ]
      },
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
      { id: "criteria", content: "Endpoint labels can stand in for detailed criteria if the pass is only a high-level service chronology review." },
      { id: "irrelevant", content: "Endpoint behavior can be treated as downstream once the initial support and carry conditions are evidenced." },
      { id: "textbook", content: "Endpoint handoff can be treated as an application of standard evolution constraints rather than a separate project concept." }
    ],
    answer: ["before_fade", "separate_surface"],
    explanation: {
      answer: "Endpoint handoff must precede fade and remain a separate evidence surface.",
      why: "A service pass can fail at the handoff even if the beginning looked well prepared. The review should ask whether support is transferred or released in the intended order; labels alone are not enough.",
      boundary: "This is active-rail architecture and should not be described as established ADM theory.",
      adaptive: {
        choices: {
          before_fade: {
            supported: "Catch or rematch should be evidenced before fade removes the active carrying support."
          },
          separate_surface: {
            supported: "Packet arrival and endpoint handoff are related but distinct evidence surfaces."
          },
          criteria: {
            unsupported: "A high-level chronology label still needs rematch or handoff criteria when endpoint burden is being claimed."
          },
          irrelevant: {
            unsupported: "Initial support and carry evidence do not make endpoint behavior merely downstream."
          },
          textbook: {
            unsupported: "Standard evolution constraints matter, but endpoint handoff is an active-rail service concept with its own evidence surface."
          }
        }
      },
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
    prompt: "A candidate report shows a clean packet path and a plausible source-family fit, but omits support-edge stress, angular-sector pressure, endpoint rematch, and reset history. Which review findings are justified?",
    choices: [
      { id: "partial", content: "The packet and source-family evidence should be credited as partial evidence." },
      { id: "missing", content: "The omitted plant channels still block a full service qualification." },
      { id: "narrow_claim", content: "The conclusion should be narrowed to the channels actually tested." },
      { id: "separate_channels", content: "Support edge, angular pressure, endpoint rematch, and reset history need separate evidence rather than one pooled pass label." },
      { id: "family_enough", content: "A plausible source-family fit can provisionally cover omitted plant channels if they are part of the same source mechanism." },
      { id: "packet_enough", content: "Clean packet transport should dominate if omitted plant channels do not visibly perturb the packet path." },
      { id: "reset_inferred", content: "Reset history can be inferred when source-family behavior appears stable across the reported pass." }
    ],
    answer: ["partial", "missing", "narrow_claim", "separate_channels"],
    explanation: {
      answer: "The result is partial, the claim should be narrowed, and missing plant channels need separate evidence.",
      why: "Design review must credit the clean packet and source-family evidence without letting them hide unexamined burden channels. Support edge, angular sector, endpoint rematch, and reset history are not interchangeable with final packet arrival.",
      boundary: "This is active-rail review logic with open project gates, not an external theorem.",
      adaptive: {
        choices: {
          partial: {
            supported: "The clean packet path and plausible source-family fit are useful partial evidence."
          },
          missing: {
            supported: "Omitted plant channels block full qualification because they are separate burden surfaces."
          },
          narrow_claim: {
            supported: "The conclusion should track the channels actually tested."
          },
          separate_channels: {
            supported: "Support edge, angular pressure, endpoint rematch, and reset history cannot be collapsed into one pass label."
          },
          family_enough: {
            unsupported: "A shared source mechanism is a hypothesis; omitted plant channels still need direct evidence."
          },
          packet_enough: {
            unsupported: "A clean packet path can miss plant burdens that do not immediately perturb the packet observable."
          },
          reset_inferred: {
            unsupported: "Apparent source stability in one pass does not substitute for a reset-history audit."
          }
        }
      },
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
      { id: "all_done", content: "The plant can be provisionally accepted if the missing source and reset checks are outside the immediate packet-tolerance claim." },
      { id: "source_done", content: "The packet result is indirect evidence that the demanded stress-energy was functionally supplied for this pass." },
      { id: "chronology_safe", content: "Clean endpoint arrival gives practical evidence against causal problems in the tested service interval." }
    ],
    answer: ["packet_only"],
    explanation: {
      answer: "Only the packet-facing check is supported.",
      why: "One successful observable can matter without carrying every other claim. Source accounting, physical realization, reset readiness, and global causal safety are different evidentiary layers.",
      boundary: "This is project-application review reasoning, not a general certification rule.",
      adaptive: {
        choices: {
          packet_only: {
            supported: "This credits the packet observable while keeping source and reset claims unsupported."
          },
          all_done: {
            unsupported: "A narrow packet-tolerance claim can pass, but missing source and reset checks still block plant qualification."
          },
          source_done: {
            unsupported: "Packet behavior is indirect evidence at best; physical stress-energy realization needs source evidence."
          },
          chronology_safe: {
            unsupported: "Clean endpoint arrival is practical evidence for this run, but global chronology safety is a separate causal-structure claim."
          }
        }
      },
      references: [],
      sourceLinks: [sources.technicalDisclosure, sources.resetReleaseLadder]
    }
  },
  {
    id: "project_state.v5_watch.002",
    type: "mc",
    track: "Design review and synthesis",
    module: "Project-state handling",
    difficulty: "intermediate",
    claimStatus: "project_hypothesis",
    contentFlags: ["project_material", "project_state", "revision_sensitive"],
    prompt: "A current V5 sealed package is described as appearing to pass bounded fixed-background checks with watch conditions. What is the most careful interpretation?",
    choices: [
      { id: "bounded", content: "It appears to be bounded project evidence for the current fixed-background package, with watches still part of the claim." },
      { id: "universal", content: "It is evidence for broader family realization if the V5 package is the representative midrange case." },
      { id: "no_watches", content: "Passing checks can move watch conditions into supporting notes when the headline claim is narrow." },
      { id: "external_theorem", content: "It can be treated like a stable architecture rule if repeated package reports keep the same boundary." }
    ],
    answer: ["bounded"],
    explanation: {
      answer: "The careful interpretation is apparent bounded project evidence with visible watches.",
      why: "An apparent pass in the current package could be meaningful, but its strength depends on the tested scope. Treating watches as part of the claim protects against overpromoting fixed-background evidence.",
      boundary: "This is revision-sensitive project-state material and should stay excludable from stable theory sessions.",
      adaptive: {
        choices: {
          bounded: {
            supported: "This wording credits the current fixed-background evidence and keeps the watch conditions attached."
          },
          universal: {
            unsupported: "Representativeness has to be argued; a bounded V5 result alone does not establish broad realization."
          },
          no_watches: {
            unsupported: "A narrow headline still needs visible watch conditions when they affect the evidence scope."
          },
          external_theorem: {
            unsupported: "Repeated project patterns can guide architecture, but they do not become external theorem status."
          }
        }
      },
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
    difficulty: "intermediate",
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
      adaptive: {
        choices: {
          true: {
            supported: "Reporting the V10 failure as a boundary preserves the current service envelope honestly."
          },
          false: {
            unsupported: "Lower-service successes should not hide a higher-service source-safety boundary."
          }
        }
      },
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
      why: "Evidence review can fail by promoting every useful statement to the same status. The correct classification keeps source constraints, metric literature, project architecture, and unresolved realization separate.",
      boundary: "The active-rail statements are application-specific and should not be read as pure general theory.",
      adaptive: {
        classifications: {
          adm_split: {
            correct: "ADM split terminology is established GR theory.",
            statuses: {
              established_constraint: "ADM variables are broader theory structure, not just a constraint result.",
              literature_model: "ADM split is not a speculative metric model.",
              active_rail_model: "Active-rail uses ADM language but did not define it.",
              project_hypothesis: "This is not current project evidence.",
              open_gate: "The ADM split itself is not unresolved."
            }
          },
          qi_constraint: {
            correct: "Quantum inequalities are established constraint literature in their settings.",
            statuses: {
              established_theory: "The statement is more specifically a constraint result than general vocabulary.",
              literature_model: "The safest curriculum label here is constraint, not speculative metric model.",
              active_rail_model: "The constraint predates the architecture.",
              project_hypothesis: "This is not a project candidate claim.",
              open_gate: "The constraint exists; project source response remains separate."
            }
          },
          alcubierre_metric: {
            correct: "The Alcubierre metric is a published speculative literature model.",
            statuses: {
              established_theory: "It is published theory context, not established engineering reality.",
              established_constraint: "The metric is a model, not itself a constraint theorem.",
              active_rail_model: "The metric is external literature, not active-rail vocabulary.",
              project_hypothesis: "It is not current project evidence.",
              open_gate: "The statement identifies a model rather than the unresolved source realization."
            }
          },
          service_stack: {
            correct: "The service-stage stack is active-rail model vocabulary.",
            statuses: {
              established_theory: "These service stages are not textbook GR terms.",
              established_constraint: "They are not an energy or causal constraint theorem.",
              literature_model: "The stack is project architecture, not a published warp metric.",
              project_hypothesis: "The stage vocabulary is more stable model language than a current evidence hypothesis.",
              open_gate: "The stage list is not itself the unresolved matter-sector claim."
            }
          },
          bounded_scope: {
            correct: "A fixed-background package with watches is project-hypothesis evidence.",
            statuses: {
              established_theory: "Current package evidence is not established GR.",
              established_constraint: "The statement is not a general constraint theorem.",
              literature_model: "This is project evidence rather than external metric literature.",
              active_rail_model: "The watch-conditioned evidence is more provisional than architecture vocabulary.",
              open_gate: "It is candidate bounded evidence, not a completed missing demonstration."
            }
          },
          matter_sector: {
            correct: "The completed repeated-service matter-sector claim remains an open gate.",
            statuses: {
              established_theory: "Established GR does not supply the project-specific repeated-service matter sector.",
              established_constraint: "This is a missing realization claim rather than a constraint theorem.",
              literature_model: "A published metric model does not complete this matter sector.",
              active_rail_model: "The statement asserts completion, not just model vocabulary.",
              project_hypothesis: "The safer status is unresolved because completion has not been supplied."
            }
          }
        }
      },
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
      adaptive: {
        choices: {
          signs: {
            supported: "The signature tells you which sign corresponds to timelike, null, and spacelike norms."
          },
          matter: {
            unsupported: "Signature does not determine a unique matter action."
          },
          coordinate: {
            unsupported: "A signature convention does not remove the need to state coordinates when components are discussed."
          },
          source: {
            unsupported: "Signature does not prove that an exotic source is physically available."
          }
        }
      },
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
      adaptive: {
        blanks: {
          line_element: {
            correct: "The line element uses the metric to turn coordinate differentials into an interval.",
            tokens: {
              einstein_eq: "Einstein's equation relates curvature to stress-energy; it is not the line element.",
              nec: "The NEC is an energy-condition inequality, not the line element.",
              trace: "The stress-tensor trace is a source contraction, not interval notation."
            },
            missing: "The blank asks for the metric line element."
          }
        }
      },
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
      adaptive: {
        choices: {
          free_fall: {
            supported: "Geodesics describe ideal free-fall or lightlike paths determined by the connection."
          },
          force: {
            unsupported: "A geodesic is the no-non-gravitational-force path, not one requiring continuous force by definition."
          },
          source: {
            unsupported: "A geodesic is a path, not a stress-energy tensor."
          },
          coordinate: {
            unsupported: "Coordinate grid lines are not geodesics in every coordinate system."
          }
        }
      },
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
      { id: "null_reach", content: "Null geodesics can help diagnose signal reachability and horizon-like behavior." },
      { id: "always_safe", content: "If the relevant null and timelike geodesics are regular in the modeled region, global causal safety is strongly suggested." },
      { id: "coordinate_lines", content: "Coordinate lines adapted to the apparent motion are usually the right first proxy for geodesic behavior." }
    ],
    answer: ["test_body", "not_source", "null_reach"],
    explanation: {
      answer: "Geodesics diagnose motion and signal reachability in a geometry, but they are not source construction.",
      why: "A geodesic analysis can reveal important behavior of probes and light, yet it leaves stress-energy, energy conditions, and global causal structure as separate questions.",
      boundary: "This is established GR interpretation and should not be inflated into physical-realization evidence.",
      adaptive: {
        choices: {
          test_body: {
            supported: "Geodesics are test-path diagnostics for the geometry."
          },
          not_source: {
            supported: "A path calculation does not construct the stress-energy source."
          },
          null_reach: {
            supported: "Null geodesics are especially useful for signal reachability and horizon-like behavior."
          },
          always_safe: {
            unsupported: "Regular modeled geodesics are useful evidence, but global causal safety requires broader causal analysis."
          },
          coordinate_lines: {
            unsupported: "Adapted coordinates can guide intuition, but coordinate lines are not automatically geodesics."
          }
        }
      },
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
      adaptive: {
        matches: {
          metric: {
            correct: "The metric encodes intervals and causal structure.",
            options: {
              derivative: "Connection coefficients support covariant derivatives.",
              curvature_combo: "The Einstein tensor is the curvature combination in Einstein's equation."
            }
          },
          connection: {
            correct: "The Christoffel symbols are connection coefficients used for covariant differentiation.",
            options: {
              intervals: "Intervals are encoded by the metric.",
              curvature_combo: "The Einstein tensor is the curvature-side combination."
            }
          },
          einstein: {
            correct: "The Einstein tensor is the curvature combination appearing in Einstein's equation.",
            options: {
              intervals: "The metric, not the Einstein tensor, directly encodes intervals.",
              derivative: "Connection coefficients, not the Einstein tensor, are used directly in covariant derivatives."
            }
          }
        }
      },
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
      adaptive: {
        sequence: [
          {
            id: "metric-before-connection",
            before: "metric",
            after: "connection",
            content: "Metric components come first because the connection is computed from the metric."
          },
          {
            id: "connection-before-curvature",
            before: "connection",
            after: "curvature",
            content: "Curvature tensors are built from the connection and its derivatives."
          },
          {
            id: "curvature-before-einstein",
            before: "curvature",
            after: "einstein",
            content: "The Einstein tensor is formed from curvature quantities."
          },
          {
            id: "einstein-before-stress",
            before: "einstein",
            after: "stress",
            content: "Demanded stress-energy is inferred from the Einstein tensor through Einstein's equation."
          }
        ]
      },
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.bianchi.conservation.001",
    type: "mc",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why does the contracted Bianchi identity matter for Einstein's equation?",
    choices: [
      { id: "conservation", content: "It is tied to covariant conservation of the stress-energy tensor when Einstein's equation holds." },
      { id: "source_anything", content: "It makes a conserved demanded tensor a strong candidate for ordinary-matter realization." },
      { id: "coordinates", content: "It makes the conservation law coordinate-independent enough that coordinate choices are mainly computational." },
      { id: "energy_positive", content: "It supports positive-energy interpretation when the conserved tensor has a positive density component." }
    ],
    answer: ["conservation"],
    explanation: {
      answer: "The Bianchi identity underlies covariant stress-energy conservation in Einstein's equation.",
      why: "Because the Einstein tensor has vanishing covariant divergence, the source side must satisfy the corresponding conservation law. This is a consistency condition, not a guarantee of benign matter.",
      boundary: "This is established GR structure and does not solve source-realization or energy-condition questions.",
      adaptive: {
        choices: {
          conservation: {
            supported: "The contracted Bianchi identity is tied to covariant conservation of the stress-energy side of Einstein's equation."
          },
          source_anything: {
            unsupported: "Conservation consistency is necessary, but ordinary-matter realization needs dynamics and source modeling."
          },
          coordinates: {
            unsupported: "Coordinate-independent meaning does not remove the practical role of coordinates or frames."
          },
          energy_positive: {
            unsupported: "Conservation and one positive component do not establish observer-quantified positive energy."
          }
        }
      },
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
      { id: "ignore", content: "Pressure components are often frame-dependent enough that density should carry the main source interpretation." },
      { id: "always_zero", content: "Pressure components can be neglected in dust-like or weak-stress limits, so they are usually secondary." },
      { id: "packet_only", content: "A well-chosen test-packet trajectory can reveal the effective source burden more directly than individual tensor components." }
    ],
    answer: ["tensor"],
    explanation: {
      answer: "The full stress-energy tensor matters.",
      why: "Energy density, flux, and stresses can all contribute to the source side of Einstein's equation. Reducing the source to one scalar can hide important burdens.",
      boundary: "This is established stress-energy reasoning, not a project-specific bookkeeping preference.",
      adaptive: {
        choices: {
          tensor: {
            supported: "Einstein's equation couples to the tensor structure, so stresses and pressures can matter alongside density."
          },
          ignore: {
            unsupported: "Frame dependence has to be handled carefully, but stresses are still tensor components with gravitational significance."
          },
          always_zero: {
            unsupported: "Dust-like limits are special cases; pressure and stress cannot be treated as usually secondary."
          },
          packet_only: {
            unsupported: "A packet trajectory is a useful probe, but it does not replace the tensor source analysis."
          }
        }
      },
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.energy_conditions.limits.003",
    type: "multi",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements correctly describe the role and limits of classical energy conditions?",
    choices: [
      { id: "diagnostic", content: "They diagnose whether a stress-energy tensor satisfies selected positivity-style constraints." },
      { id: "not_complete", content: "Passing one condition is not a complete proof of physical source realizability." },
      { id: "assumption_sensitive", content: "Their interpretation depends on the relevant classical, quantum, pointwise, averaged, or observer assumptions." },
      { id: "all_matter", content: "They give a broad first-pass classification, with quantum exceptions handled as later refinements." },
      { id: "metric_name", content: "A metric family often signals the likely energy-condition burden before detailed stress-energy evaluation." },
      { id: "one_condition_all", content: "Passing the NEC is strong evidence for related pointwise conditions when the tensor has a simple type-I form." }
    ],
    answer: ["diagnostic", "not_complete", "assumption_sensitive"],
    explanation: {
      answer: "Energy conditions are assumption-sensitive diagnostic constraints, not complete physical-source certification.",
      why: "They are powerful because they encode useful positivity assumptions, but different conditions test different contractions and can fail or require reinterpretation in quantum or effective settings.",
      boundary: "This is established constraint reasoning; it must be applied with assumptions visible.",
      adaptive: {
        choices: {
          diagnostic: {
            supported: "Energy conditions diagnose selected positivity-style properties of a stress tensor."
          },
          not_complete: {
            supported: "Passing one condition does not identify a complete physical matter model."
          },
          assumption_sensitive: {
            supported: "Pointwise, averaged, classical, quantum, and observer assumptions change interpretation."
          },
          all_matter: {
            unsupported: "They are useful first-pass constraints, but quantum and effective settings are not just later refinements."
          },
          metric_name: {
            unsupported: "A metric family can warn you what to expect, but the stress-energy still has to be evaluated."
          },
          one_condition_all: {
            unsupported: "Simple type-I structure can relate conditions, but NEC passage is not a blanket clearance for WEC, DEC, or averaged conditions."
          }
        }
      },
      references: [references.energyConditionsPrimer, references.fordRoman]
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
      { id: "same", content: "They usually agree for simple diagonal examples once the relevant density and pressure sums are checked." },
      { id: "trace", content: "Both can be inferred from a compact scalar summary of the stress tensor in highly symmetric cases." },
      { id: "metric_only", content: "Both can be screened from the geometry once the Einstein tensor is known, before naming observer vectors." }
    ],
    answer: ["vectors"],
    explanation: {
      answer: "NEC is null-contraction based; WEC is timelike-observer based.",
      why: "The difference matters because null and timelike probes test different aspects of the stress tensor. Confusing them can make source diagnostics look cleaner than they are.",
      boundary: "This is established energy-condition vocabulary and not tied to one project architecture.",
      adaptive: {
        choices: {
          vectors: {
            supported: "The NEC quantifies over null vectors, while the WEC quantifies over timelike observers."
          },
          same: {
            unsupported: "The conditions can be related in simple cases, but their vector quantifiers are different."
          },
          trace: {
            unsupported: "Symmetry can simplify checks, but the conditions are contractions with null or timelike vectors, not only scalar summaries."
          },
          metric_only: {
            unsupported: "Geometry can imply a demanded stress tensor through Einstein's equation, but the condition itself still requires the appropriate contractions."
          }
        }
      },
      references: [references.energyConditionsPrimer]
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
      adaptive: {
        choices: {
          slice_geometry: {
            supported: "The spatial metric is the intrinsic geometry on each slice."
          },
          time_step: {
            unsupported: "Normal proper-time advance is the lapse role, not the spatial metric's role."
          },
          ordinary_matter: {
            unsupported: "The spatial metric does not guarantee ordinary matter."
          },
          quantum_state: {
            unsupported: "Quantum state selection is separate from the ADM spatial metric."
          }
        }
      },
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
      adaptive: {
        choices: {
          spatial_drift: {
            supported: "The shift describes tangential coordinate drift from one slice to the next."
          },
          normal_time: {
            unsupported: "Normal proper-time separation is the lapse role."
          },
          energy_density: {
            unsupported: "Energy density is a stress-energy projection, not the shift."
          },
          topology: {
            unsupported: "The shift does not determine global topology."
          }
        }
      },
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
      { id: "intrinsic_only", content: "The part of the slice geometry most directly visible to observers who measure distances within that slice." },
      { id: "matter_unique", content: "The geometric data needed to constrain matter projections once the spatial metric is fixed." },
      { id: "causal_complete", content: "A local foliation diagnostic that can support later causal analysis when evolved consistently." }
    ],
    answer: ["embedding_change"],
    explanation: {
      answer: "Extrinsic curvature describes embedding and time-change information for the slice.",
      why: "The spatial metric gives intrinsic slice geometry; extrinsic curvature records how that slice sits in the full spacetime and enters the ADM constraints.",
      boundary: "This is established 3+1 geometry, not an operational readiness claim.",
      adaptive: {
        choices: {
          embedding_change: {
            supported: "Extrinsic curvature records embedding and normal-time-change information for the spatial slice."
          },
          intrinsic_only: {
            unsupported: "Distance measurements inside the slice are intrinsic-metric information; extrinsic curvature adds embedding and time-change information."
          },
          matter_unique: {
            unsupported: "Extrinsic curvature enters constraint relations, but it does not identify a unique matter action."
          },
          causal_complete: {
            unsupported: "Consistent foliation data can inform causal review, but global causal completeness is a separate claim."
          }
        }
      },
      references: [references.adm]
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
    prompt: "A 3+1 candidate has a small Hamiltonian-constraint residual on the initial slice, but the momentum-constraint residual is large near a high-shift region during evolution. Which conclusions are justified?",
    choices: [
      { id: "momentum_matters", content: "A small Hamiltonian residual alone is not enough; the momentum-constraint residual is still a consistency problem." },
      { id: "diagnostic_not_source", content: "Constraint residuals diagnose compatibility with Einstein's equation but do not construct a matter action." },
      { id: "monitor_evolution", content: "Constraint behavior during evolution matters, not only the initial slice residual." },
      { id: "hamiltonian_enough", content: "The small Hamiltonian residual should carry more weight because high-shift regions often amplify momentum-residual noise." },
      { id: "observable_enough", content: "A clean packet or probe trajectory can justify treating the momentum residual as a numerical artifact if it does not affect observables." }
    ],
    answer: ["momentum_matters", "diagnostic_not_source", "monitor_evolution"],
    explanation: {
      answer: "The momentum residual and its evolution remain consistency problems, and constraint control is not matter-action construction.",
      why: "The Hamiltonian and momentum constraints test different projections of Einstein's equation. A good review does not let one small residual, or one clean observable, hide a separate constraint failure.",
      boundary: "This is established ADM theory and should be kept separate from application-specific qualification language.",
      adaptive: {
        choices: {
          momentum_matters: {
            supported: "The momentum constraint is a separate projection and remains a consistency problem when large."
          },
          diagnostic_not_source: {
            supported: "Constraint residuals diagnose equation compatibility; they do not construct a matter action."
          },
          monitor_evolution: {
            supported: "Constraint behavior during evolution can reveal failures not visible on one initial scalar residual."
          },
          hamiltonian_enough: {
            unsupported: "A small Hamiltonian residual is valuable, but high-shift context does not demote a large momentum residual without constraint evidence."
          },
          observable_enough: {
            unsupported: "A clean observable can coexist with a real constraint failure, so it cannot classify the momentum residual as numerical artifact by itself."
          }
        }
      },
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
      adaptive: {
        sequence: [
          {
            id: "data-before-matter",
            before: "choose_data",
            after: "matter",
            content: "Spatial metric and extrinsic-curvature data define the geometric initial-data side before compatible matter projections are assigned."
          },
          {
            id: "matter-before-constraints",
            before: "matter",
            after: "constraints",
            content: "Constraint checks compare the geometry with the matter or vacuum projections."
          },
          {
            id: "constraints-before-evolve",
            before: "constraints",
            after: "evolve",
            content: "Constraint consistency should be checked before evolution claims are trusted."
          },
          {
            id: "evolve-before-monitor",
            before: "evolve",
            after: "monitor",
            content: "Monitoring follows evolution because preservation and interpretation are ongoing checks."
          }
        ]
      },
      references: [references.adm]
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
      adaptive: {
        choices: {
          causal_directions: {
            supported: "Light cones are the local null boundaries that organize timelike, null, and spacelike directions."
          },
          matter_source: {
            unsupported: "Light cones describe causal directions, not the source required to realize a metric."
          },
          coordinate_grid: {
            unsupported: "Light cones depend on the metric, not a fixed coordinate grid independent of it."
          },
          energy_positive: {
            unsupported: "Causal cones do not guarantee positive energy for all observers."
          }
        }
      },
      references: [references.carrollGrNotes, references.causalHierarchy]
    }
  },
  {
    id: "foundation.horizon.local_global.001",
    type: "multi",
    track: "Established foundations",
    module: "Causal structure",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which horizon-related statements are careful in GR reasoning?",
    choices: [
      { id: "global", content: "Some horizons are global causal structures, not features a local observer can always identify from one small patch." },
      { id: "signals", content: "Horizon-like behavior is about signal reachability and causal access." },
      { id: "coordinate_caution", content: "Coordinate artifacts and genuine causal boundaries have to be distinguished carefully." },
      { id: "coordinate_only", content: "A horizon seen in one coordinate chart should first be treated as a coordinate effect until invariant or global checks say otherwise." },
      { id: "source_done", content: "Horizon identification helps classify the geometry enough that source review can be separated afterward." }
    ],
    answer: ["global", "signals", "coordinate_caution"],
    explanation: {
      answer: "Horizons require causal-access reasoning, coordinate care, and often global context.",
      why: "Some apparent singularities are coordinate artifacts, but horizons themselves can encode real causal boundaries. Their interpretation requires more than local component inspection or a single coordinate chart.",
      boundary: "This is established causal-structure reasoning and does not decide source realizability or matter viability.",
      adaptive: {
        choices: {
          global: {
            supported: "Some horizons are global causal structures and cannot be fully identified from one small patch."
          },
          signals: {
            supported: "Horizon-like behavior is about which signals can reach which regions."
          },
          coordinate_caution: {
            supported: "Coordinate artifacts have to be separated from genuine causal boundaries."
          },
          coordinate_only: {
            unsupported: "Coordinate caution is right, but genuine horizons are not dismissed before invariant and global causal checks."
          },
          source_done: {
            unsupported: "Horizon classification and matter-source construction remain separate review surfaces."
          }
        }
      },
      references: [references.causalHierarchy, references.globalHyperbolicityReview]
    }
  },
  {
    id: "foundation.global_hyperbolicity.001",
    type: "mc",
    track: "Established foundations",
    module: "Causal structure",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why is global hyperbolicity important in GR?",
    choices: [
      { id: "well_posed", content: "It supports well-posed causal evolution from suitable initial data and rules out certain causal pathologies." },
      { id: "ordinary_matter", content: "It supports a well-posed evolution, which strongly constrains admissible matter behavior." },
      { id: "local_only", content: "It can be checked locally by looking at causal cones on a representative slice." },
      { id: "no_constraints", content: "It makes the evolution problem well posed, so constraints are mainly initial-data bookkeeping." }
    ],
    answer: ["well_posed"],
    explanation: {
      answer: "Global hyperbolicity is tied to well-posed causal evolution.",
      why: "It is a global causal condition that helps make initial-value reasoning meaningful. It is not a substitute for stress-energy, energy-condition analysis, or source modeling.",
      boundary: "This is established causal-structure theory, not an engineering-readiness, source-realization, or matter-viability claim.",
      adaptive: {
        choices: {
          well_posed: {
            supported: "Global hyperbolicity supports well-posed causal evolution from suitable initial data."
          },
          ordinary_matter: {
            unsupported: "Global hyperbolicity supports predictability; it does not guarantee an ordinary positive-energy source."
          },
          local_only: {
            unsupported: "Local cone checks can inform the review, but global hyperbolicity is a global causal condition."
          },
          no_constraints: {
            unsupported: "Well-posed evolution still depends on compatible initial data and constraint control."
          }
        }
      },
      references: [references.globalHyperbolicityReview, references.cauchyHypersurfaces]
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
      adaptive: {
        choices: {
          true: {
            supported: "A closed timelike curve is timelike and returns to its starting event."
          },
          false: {
            unsupported: "The statement is the standard causal-structure definition."
          }
        }
      },
      references: [references.causalHierarchy, references.chronologyProtection]
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
      adaptive: {
        matches: {
          density: {
            correct: "Energy density is what a chosen observer measures locally as density.",
            options: {
              flow: "Energy or momentum flux is transport across directions.",
              spatial_stress: "Pressure or stress are spatial force-per-area style components."
            }
          },
          flux: {
            correct: "Flux represents transport of energy or momentum across directions.",
            options: {
              observer_measure: "Observer-measured density is the density role.",
              spatial_stress: "Spatial stress is pressure or force-per-area style behavior."
            }
          },
          pressure: {
            correct: "Pressure or stress corresponds to spatial stress components.",
            options: {
              observer_measure: "Observer-measured density is a different tensor role.",
              flow: "Flux is directional transport, not pressure or stress."
            }
          }
        }
      },
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
      adaptive: {
        blanks: {
          stress: {
            correct: "Solving Einstein's equation for stress-energy gives the Einstein tensor divided by eight pi in these units.",
            tokens: {
              metric_flat: "A flat metric condition is not the algebraic source-demand expression.",
              null_norm: "A null norm condition classifies a vector, not stress-energy.",
              lapse_positive: "A positive lapse condition is not the stress-energy side of Einstein's equation."
            },
            missing: "The blank asks for stress-energy solved from Einstein's equation."
          }
        }
      },
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
      adaptive: {
        choices: {
          basis: {
            supported: "Individual components depend on the selected frame or coordinate basis."
          },
          absolute: {
            unsupported: "Tensor components generally change between frames."
          },
          no_tensor: {
            unsupported: "Naming a basis gives components of the tensor; it does not make the object stop being a tensor."
          },
          source: {
            unsupported: "A frame choice does not construct a physical matter source."
          }
        }
      },
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
      { id: "proves_full", content: "A symmetric calculation can be treated as representative if it controls the dominant channels." },
      { id: "no_sources", content: "Symmetry can make stress-energy checks simpler enough that the reduced source components carry the burden." },
      { id: "averaging_magic", content: "A controlled reduced average can stand in for local components when the symmetry is physically motivated." }
    ],
    answer: ["simplifies", "misses_modes"],
    explanation: {
      answer: "Symmetry helps, but it narrows what has been tested.",
      why: "Reduction is a legitimate mathematical strategy, but claims should track the reduced scope. Missing modes or channels can matter outside the symmetry class.",
      boundary: "This is general modeling discipline, not a project-specific excuse or guarantee.",
      adaptive: {
        choices: {
          simplifies: {
            supported: "Symmetry can reduce equations and make diagnostics tractable."
          },
          misses_modes: {
            supported: "A reduced model can hide nonsymmetric perturbations or channels."
          },
          proves_full: {
            unsupported: "A symmetric calculation can be representative inside its assumptions, but it does not prove nonsymmetric cases by itself."
          },
          no_sources: {
            unsupported: "Reduced source components still have to be checked; symmetry simplifies rather than removes the burden."
          },
          averaging_magic: {
            unsupported: "A reduced average needs assumptions connecting it to local unsymmetrized behavior."
          }
        }
      },
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
      adaptive: {
        classifications: {
          field_equation: {
            correct: "Einstein's equation is established theory.",
            statuses: {
              established_constraint: "The field equation is broader than a positivity or causal constraint.",
              literature_model: "It is not merely a named speculative metric model.",
              open_gate: "The equation itself is not unresolved."
            }
          },
          energy_condition: {
            correct: "The NEC is an established constraint on stress-energy contractions.",
            statuses: {
              established_theory: "It is theory-adjacent, but the safer class here is established constraint.",
              literature_model: "The NEC is not just a specific speculative metric model.",
              open_gate: "The definition is not the unresolved source-realization claim."
            }
          },
          metric_ansatz: {
            correct: "A named speculative metric is literature-model material until physically realized.",
            statuses: {
              established_theory: "A speculative metric ansatz is not automatically established physical theory.",
              established_constraint: "A metric ansatz is not itself an energy-condition theorem.",
              open_gate: "The model is analyzable; the open gate is physical source realization."
            }
          },
          source_realization: {
            correct: "Universal conventional realization of arbitrary exotic metrics remains open.",
            statuses: {
              established_theory: "Established equations do not guarantee conventional matter for every exotic metric.",
              established_constraint: "This is a realization claim, not just a constraint.",
              literature_model: "No single named metric supplies universal source realization."
            }
          }
        }
      },
      references: [references.carrollGrNotes, references.energyConditionsPrimer, references.fordRoman]
    }
  },
  {
    id: "foundation.conservation_boundary.001",
    type: "multi",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements correctly distinguish conservation consistency from physical source realization?",
    choices: [
      { id: "necessary", content: "Covariant conservation is a necessary consistency condition for the source side of Einstein's equation." },
      { id: "not_sufficient", content: "Conservation alone is not sufficient to identify a viable microphysical matter model." },
      { id: "dynamics_needed", content: "For a conserved tensor, dynamics and coupling details are mostly choices of matter representation rather than separate consistency gates." },
      { id: "sufficient", content: "A conserved stress tensor is close to a source model when it has reasonable density and pressure components." },
      { id: "irrelevant", content: "The Bianchi identity moves the main review from conservation to interpretation of the chosen geometry." }
    ],
    answer: ["necessary", "not_sufficient"],
    explanation: {
      answer: "Conservation is necessary but not sufficient for source realization.",
      why: "The Bianchi identity supplies a deep consistency relation, but viable matter also depends on dynamics, stability, energy behavior, coupling assumptions, and physical interpretation beyond conservation.",
      boundary: "This is established GR reasoning and is deliberately broader than any one architecture.",
      adaptive: {
        choices: {
          necessary: {
            supported: "Covariant conservation is a necessary consistency condition for the source side of Einstein's equation."
          },
          not_sufficient: {
            supported: "A conserved tensor can still lack a viable microphysical matter model."
          },
          dynamics_needed: {
            unsupported: "Conservation is a consistency gate; dynamics, stability, and coupling assumptions remain separate source-realization questions."
          },
          sufficient: {
            unsupported: "Reasonable-looking components can help interpretation, but conservation plus component plausibility is not a microphysical matter model."
          },
          irrelevant: {
            unsupported: "The Bianchi identity constrains source interpretation; it does not move the main burden away from source realization."
          }
        }
      },
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.adm_constraint_residuals.002",
    type: "multi",
    track: "Established foundations",
    module: "ADM constraints",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A 3+1 evolution has a small Hamiltonian residual on the initial slice, a growing momentum residual near a strong shift-gradient region, and a stable-looking probe trajectory. Which review conclusions are justified?",
    choices: [
      { id: "momentum_failure", content: "The growing momentum residual remains a constraint-consistency problem even if the Hamiltonian residual is small." },
      { id: "probe_not_enough", content: "A stable-looking probe trajectory is not enough to clear the constraint failure." },
      { id: "initial_not_all", content: "An initially small residual does not settle constraint preservation during later evolution." },
      { id: "hamiltonian_dominates", content: "The small Hamiltonian residual should carry greater weight if the momentum residual is localized near a strong shift-gradient region." },
      { id: "probe_clears", content: "The stable-looking probe trajectory is evidence that the residual may be confined to an unobserved channel." }
    ],
    answer: ["momentum_failure", "probe_not_enough", "initial_not_all"],
    explanation: {
      answer: "The momentum residual remains a real consistency problem, later preservation matters, and the probe trajectory does not clear it.",
      why: "This requires separating two different ADM constraints from a downstream observable. The Hamiltonian and momentum constraints test different projections of Einstein's equation, and a good-looking trajectory can coexist with inconsistent field data.",
      boundary: "This is established 3+1 constraint reasoning; it does not depend on any project-specific service vocabulary.",
      adaptive: {
        choices: {
          momentum_failure: {
            supported: "A growing momentum residual is a separate constraint-consistency problem."
          },
          probe_not_enough: {
            supported: "A stable-looking probe trajectory does not clear inconsistent field data."
          },
          initial_not_all: {
            supported: "An initially small residual does not settle later constraint preservation."
          },
          hamiltonian_dominates: {
            unsupported: "A localized high-shift residual may suggest where to look, but it does not downgrade a growing momentum residual without further constraint evidence."
          },
          probe_clears: {
            unsupported: "A stable trajectory is useful downstream evidence, but it cannot by itself reclassify inconsistent field data as nonphysical."
          }
        }
      },
      references: [references.adm]
    }
  },
  {
    id: "foundation.energy_condition_synthesis.004",
    type: "multi",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A stress-energy candidate passes the NEC along one sampled null direction and has positive energy density for one observer, but it has untested null directions and large anisotropic stresses. Which conclusions are justified?",
    choices: [
      { id: "not_global_nec", content: "Passing one sampled null direction does not establish the NEC for all null vectors." },
      { id: "not_wec", content: "Positive density for one observer does not establish the WEC for every timelike observer." },
      { id: "anisotropic_review", content: "Large anisotropic stresses require checking the relevant tensor contractions, not only scalar density." },
      { id: "region_scope", content: "The region over which the condition is claimed has to be specified, not inferred from one event." },
      { id: "full_clear", content: "The tested null direction and one observer give a representative sample unless a symmetry argument says otherwise." },
      { id: "stress_irrelevant", content: "The anisotropic stresses matter mainly for material interpretation, while energy density carries the energy-condition check." }
    ],
    answer: ["not_global_nec", "not_wec", "anisotropic_review", "region_scope"],
    explanation: {
      answer: "The tested directions and region are insufficient for global NEC or WEC claims, and anisotropic stresses still need tensor review.",
      why: "Energy-condition review must track quantifiers over vectors, observers, and regions. NEC and WEC are not one-direction or one-observer checks, and anisotropic stresses can matter in the full stress tensor.",
      boundary: "This is established constraint reasoning about stress-energy, not a physical source-realization claim.",
      adaptive: {
        choices: {
          not_global_nec: {
            supported: "The NEC is quantified over null vectors, so one sampled null direction is not enough."
          },
          not_wec: {
            supported: "The WEC concerns every timelike observer, not one positive-density observer."
          },
          anisotropic_review: {
            supported: "Large anisotropic stresses can affect the relevant tensor contractions."
          },
          region_scope: {
            supported: "The spatial or spacetime region of the claim has to be stated rather than inferred from one event."
          },
          full_clear: {
            unsupported: "A sample becomes representative only with supporting symmetry or domain arguments; none are supplied here."
          },
          stress_irrelevant: {
            unsupported: "Anisotropic stresses enter the relevant tensor contractions, not only material interpretation."
          }
        }
      },
      references: [references.energyConditionsPrimer]
    }
  },
  {
    id: "foundation.causal_assumption_tracking.002",
    type: "multi",
    track: "Established foundations",
    module: "Causal structure",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A spacetime model is locally smooth and has no closed timelike curves in a small simulated patch, but the proposed use depends on global signal routing around a compact region. Which cautions are justified?",
    choices: [
      { id: "local_not_global", content: "Local smoothness and a patch-level CTC check do not establish global causal behavior." },
      { id: "routing", content: "Signal reachability and global hyperbolicity or horizon-like boundaries still need separate analysis." },
      { id: "domain_limits", content: "The simulated patch's domain of dependence and boundary assumptions matter for the claimed use." },
      { id: "extension_assumptions", content: "Assumptions about how the local patch is extended outside the simulated region affect the global claim." },
      { id: "smooth_enough", content: "Local smoothness and the absence of patch-level CTCs are strong evidence unless the extension introduces explicit identifications." },
      { id: "ctc_patch_enough", content: "A small-patch CTC search is the relevant test when the proposed signal routing stays near that patch." }
    ],
    answer: ["local_not_global", "routing", "domain_limits", "extension_assumptions"],
    explanation: {
      answer: "Local checks are not enough for global causal, routing, extension, or domain-of-dependence claims.",
      why: "Assumptions have to be tracked across scales: local regularity, absence of CTCs in one patch, extension beyond the patch, global hyperbolicity, horizon-like access, and signal reachability are distinct causal claims that can fail independently.",
      boundary: "This is established causal-structure reasoning and remains independent of any specific engineering architecture.",
      adaptive: {
        choices: {
          local_not_global: {
            supported: "Local smoothness and a small-patch CTC search do not establish global causal behavior."
          },
          routing: {
            supported: "Signal reachability, global hyperbolicity, and horizon-like boundaries need separate analysis."
          },
          domain_limits: {
            supported: "The domain of dependence and boundary assumptions define what the simulated patch can support."
          },
          extension_assumptions: {
            supported: "How the patch is extended outside the simulation can change the global claim."
          },
          smooth_enough: {
            unsupported: "The patch evidence is useful, but extension assumptions can introduce global causal structure not visible in the local check."
          },
          ctc_patch_enough: {
            unsupported: "Even nearby routing depends on boundary and domain-of-dependence assumptions, so the patch search is not the whole causal-access test."
          }
        }
      },
      references: [references.causalHierarchy, references.globalHyperbolicityReview, references.chronologyProtection]
    }
  },
  {
    id: "foundation.source_realization_layers.002",
    type: "sequence",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Order these claims from weakest to strongest when moving from a prescribed metric toward physical source realization.",
    items: [
      { id: "metric", content: "A metric ansatz is specified." },
      { id: "einstein_tensor", content: "The Einstein tensor is computed." },
      { id: "demand", content: "The demanded stress-energy tensor is inferred." },
      { id: "consistency", content: "Conservation and constraint consistency are checked." },
      { id: "matter", content: "A viable matter model or microphysical source is supplied." }
    ],
    answer: ["metric", "einstein_tensor", "demand", "consistency", "matter"],
    explanation: {
      answer: "Metric ansatz, Einstein tensor, demanded stress-energy, consistency checks, matter model.",
      why: "The sequence forces separation between mathematical source demand and physical source realization. Computing the demanded tensor is not the same as deriving a viable matter sector.",
      boundary: "This is general GR reasoning about claim strength, not a project-specific qualification ladder.",
      adaptive: {
        sequence: [
          {
            id: "metric-before-einstein-tensor",
            before: "metric",
            after: "einstein_tensor",
            content: "The metric ansatz is specified before its Einstein tensor can be computed."
          },
          {
            id: "einstein-tensor-before-demand",
            before: "einstein_tensor",
            after: "demand",
            content: "The demanded stress-energy is inferred from the Einstein tensor through Einstein's equation."
          },
          {
            id: "demand-before-consistency",
            before: "demand",
            after: "consistency",
            content: "Once demand is known, conservation and constraint consistency can be checked."
          },
          {
            id: "consistency-before-matter",
            before: "consistency",
            after: "matter",
            content: "Consistency checks are weaker than supplying a viable matter model or microphysical source."
          }
        ]
      },
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.topological_censorship_assumptions.003",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Topological censorship",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A proposed traversable shortcut claims to evade topological censorship because a local throat cross-section looks smooth. Which review objections are justified under Friedman, Schleich, and Witt's 1993 topological censorship framing?",
    choices: [
      { id: "global_theorem", content: "Topological censorship is a global causal theorem, so a local smooth throat picture is not enough to decide applicability." },
      { id: "assumptions", content: "The energy, asymptotic, and predictability assumptions must be checked before using or evading the theorem." },
      { id: "local_smooth", content: "A smooth local throat is strong evidence against singular obstruction, so the theorem's global assumptions become secondary." },
      { id: "no_energy", content: "The theorem is mainly a topology statement, so energy and asymptotic assumptions serve as background hypotheses rather than review gates." },
      { id: "topology_label", content: "If the proposed geometry is described as a traversable shortcut, that classification largely determines which censorship result applies." }
    ],
    answer: ["global_theorem", "assumptions"],
    explanation: {
      answer: "The theorem requires global assumption tracking; local smoothness is not enough.",
      why: "A careful use of the theorem avoids two opposite mistakes: treating it as an assumption-free slogan, or dismissing it merely because a local geometric picture looks smooth.",
      boundary: "This is established constraint literature with explicit assumptions, not a universal ban on writing shortcut metrics.",
      adaptive: {
        choices: {
          global_theorem: {
            supported: "Topological censorship is global, so a local smooth throat picture does not decide applicability."
          },
          assumptions: {
            supported: "Energy, asymptotic, causality, and predictability assumptions are part of applying or evading the theorem."
          },
          local_smooth: {
            unsupported: "Local smoothness helps rule out one kind of obstruction, but it does not decide a global theorem."
          },
          no_energy: {
            unsupported: "Energy, asymptotic, causal, and predictability assumptions are review gates for applying the theorem."
          },
          topology_label: {
            unsupported: "The label points to a concern, but theorem applicability depends on the geometry and assumptions."
          }
        }
      },
      references: [references.topologicalCensorship]
    }
  },
  {
    id: "literature.ford_roman_design_transfer.005",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Quantum inequalities",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A design note claims its negative-energy layer is acceptable because the peak violation is brief at each point, but the layer is macroscopic and repeatedly sampled by null probes. Which Ford and Roman 1996 quantum-inequality review moves are justified?",
    choices: [
      { id: "sampling_worldline", content: "Ask for sampling-time and accumulated-exposure analysis, not only a pointwise peak value." },
      { id: "macroscopic_scale", content: "Treat macroscopic scale and repeated exposure as part of the burden." },
      { id: "not_source_model", content: "Keep the constraint separate from a positive construction of the required source." },
      { id: "compare_scale", content: "Compare the claimed layer thickness and duration with the scales entering the quantum-inequality bound." },
      { id: "brief_peak_enough", content: "A brief pointwise peak can be adequate if each local observer samples only a narrow pulse." },
      { id: "metric_name_enough", content: "If the geometry is smooth and the layer is localized, the remaining burden is mostly classical stress accounting." }
    ],
    answer: ["sampling_worldline", "macroscopic_scale", "not_source_model", "compare_scale"],
    explanation: {
      answer: "Sampling duration, accumulated exposure, scale comparison, and source-construction boundaries remain central.",
      why: "The quantum-inequality lesson applies to the incomplete design claim through sampling duration, exposure, layer scale, and bound scale, while the inequality itself still does not supply a full matter model.",
      boundary: "This is a literature-backed constraint review, not a construction recipe or an all-purpose impossibility proof.",
      adaptive: {
        choices: {
          sampling_worldline: {
            supported: "The review needs sampling-time and exposure analysis, not just one peak value."
          },
          macroscopic_scale: {
            supported: "Macroscopic scale and repeated exposure are part of the Ford-Roman burden."
          },
          not_source_model: {
            supported: "The inequality constrains candidate sources but does not construct them."
          },
          compare_scale: {
            supported: "Layer thickness and duration have to be compared with the scales in the bound."
          },
          brief_peak_enough: {
            unsupported: "Local pulse width is not enough by itself; repeated exposure and macroscopic scale still enter the review."
          },
          metric_name_enough: {
            unsupported: "Smooth localized geometry still needs quantum-field review when the claim depends on negative energy."
          }
        }
      },
      references: [references.fordRoman]
    }
  },
  {
    id: "literature.chl_control_transfer.005",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A superluminal bubble proposal says an onboard controller will adjust the front wall after launch. Using Clark-Hiscock-Larson's 1999 null-geodesic lesson, which objections are justified?",
    choices: [
      { id: "signal_reach", content: "The proposal must show signal reachability to the wall region it claims to control." },
      { id: "horizon_like", content: "Horizon-like null structures can make onboard control assumptions nontrivial." },
      { id: "source_separate", content: "Null-geodesic reachability does not itself supply the stress-energy source." },
      { id: "smooth_control", content: "Smooth metric components plus local wall regularity are enough unless a horizon is explicitly present." },
      { id: "geodesics_source", content: "A null-geodesic plot can constrain the missing source problem by identifying where control influence must be applied." }
    ],
    answer: ["signal_reach", "horizon_like", "source_separate"],
    explanation: {
      answer: "Reachability and horizon-like causal structure must be checked, while source realization remains separate.",
      why: "The paper result becomes relevant to control because the issue is not just whether null rays exist, but whether the claimed controller can causally affect the relevant region.",
      boundary: "This is literature-model reasoning about Alcubierre-type geometry, not proof that any particular design succeeds or fails.",
      adaptive: {
        choices: {
          signal_reach: {
            supported: "The controller claim needs evidence that signals can reach the wall region being controlled."
          },
          horizon_like: {
            supported: "Horizon-like null structures make onboard control assumptions nontrivial."
          },
          source_separate: {
            supported: "Reachability analysis does not supply the stress-energy source."
          },
          smooth_control: {
            unsupported: "Smooth local components do not settle whether signals from the onboard controller can reach the wall region."
          },
          geodesics_source: {
            unsupported: "A null-geodesic plot can localize access issues, but it does not supply the stress-energy source."
          }
        }
      },
      references: [references.clarkHiscockLarson]
    }
  },
  {
    id: "design_review.conflicting_evidence.004",
    type: "multi",
    track: "Design review and synthesis",
    module: "Evidence sufficiency",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    scoring: "subtract_incorrect",
    prompt: "A candidate has clean packet transport, a moderate source-family fit, a growing endpoint residual, and no reset-history audit. Which review conclusions are appropriate?",
    choices: [
      { id: "credit_packet", content: "Credit the packet and source-family evidence as partial positive evidence." },
      { id: "block_full", content: "Block full service qualification until endpoint residual and reset-history evidence are resolved." },
      { id: "narrow_scope", content: "Narrow the claim to the channels actually supported by the evidence." },
      { id: "diagnose_conflict", content: "Treat the endpoint residual as conflicting channel evidence rather than averaging it away." },
      { id: "packet_dominates", content: "Clean packet transport should carry the final decision if the endpoint residual does not affect the packet observable." },
      { id: "source_dominates", content: "A moderate source-family fit can make endpoint and reset issues secondary if those channels are downstream effects." },
      { id: "reset_optional", content: "Reset history can be deferred when the immediate claim is one clean service pass rather than repeated operation." }
    ],
    answer: ["credit_packet", "block_full", "narrow_scope", "diagnose_conflict"],
    explanation: {
      answer: "Credit partial positives, diagnose the conflict, narrow the claim, and block full qualification on unresolved channels.",
      why: "Calibrated judgment matters: useful evidence should not be discarded, but it also should not be promoted beyond its scope. Conflicting channel evidence should narrow the claim rather than being averaged away.",
      boundary: "This is active-rail design-review reasoning with open gates, not established external certification doctrine.",
      adaptive: {
        choices: {
          credit_packet: {
            supported: "Clean packet transport and source-family fit are real partial positives."
          },
          block_full: {
            supported: "Endpoint residual and missing reset history block full service qualification."
          },
          narrow_scope: {
            supported: "The claim should be narrowed to the channels actually evidenced."
          },
          diagnose_conflict: {
            supported: "The endpoint residual is conflicting channel evidence and should not be averaged away."
          },
          packet_dominates: {
            unsupported: "A final packet observable is important, but endpoint residual and reset history are separate service channels rather than downstream noise."
          },
          source_dominates: {
            unsupported: "Source-family fit is positive evidence, but endpoint and reset behavior still need channel-specific support."
          },
          reset_optional: {
            unsupported: "A one-pass claim can be narrower, but this prompt asks about service qualification where reset history remains a live gate."
          }
        }
      },
      references: [],
      sourceLinks: [sources.boundedSealReadiness, sources.resetReleaseLadder, sources.endpointSourceFamilyRung],
      openGate: "Endpoint residual and reset-history closure remain unresolved in the scenario."
    }
  },
  {
    id: "design_review.claim_scope.classification.005",
    type: "claim_classification",
    track: "Design review and synthesis",
    module: "Claim classification",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    prompt: "Classify each statement in a mixed evidence review by safest status.",
    statuses: ["established_theory", "established_constraint", "literature_model", "active_rail_model", "project_hypothesis", "open_gate"],
    statements: [
      { id: "bianchi", content: "The Einstein tensor has vanishing covariant divergence.", answer: "established_theory" },
      { id: "qi", content: "Quantum inequalities constrain some sampled negative-energy configurations.", answer: "established_constraint" },
      { id: "chl", content: "Clark-Hiscock-Larson analyze null-geodesic reachability in the Alcubierre spacetime.", answer: "literature_model" },
      { id: "ledger", content: "A demanded-source ledger records source demand for a prescribed architecture metric.", answer: "active_rail_model" },
      { id: "candidate", content: "A current fixed-background source family could be a candidate organizing strategy.", answer: "project_hypothesis" },
      { id: "matter", content: "A repeated-service microphysical matter sector has been supplied.", answer: "open_gate" }
    ],
    explanation: {
      answer: "The statements span established theory, constraints, literature, architecture model, project hypothesis, and open gate.",
      why: "Cross-status review keeps mathematical identities, constraint literature, paper results, project bookkeeping, and unresolved source realization in separate bins. Without that separation, a useful partial result can be promoted into an unsupported physical claim.",
      boundary: "This is project-application review with explicit flags; it should not be read as pure general theory.",
      adaptive: {
        classifications: {
          bianchi: {
            correct: "The vanishing covariant divergence of the Einstein tensor is established theory.",
            statuses: {
              established_constraint: "This is a geometric identity tied to the field equations, not a positivity constraint.",
              literature_model: "It is not a speculative spacetime model.",
              active_rail_model: "Active-rail uses this structure but did not define it.",
              project_hypothesis: "It is not current project evidence.",
              open_gate: "The identity itself is not unresolved."
            }
          },
          qi: {
            correct: "Quantum inequalities are established constraint literature in their stated domains.",
            statuses: {
              established_theory: "This is more specifically a constraint result than general GR vocabulary.",
              literature_model: "The safest review status is constraint, not speculative metric model.",
              active_rail_model: "It is not active-rail architecture vocabulary.",
              project_hypothesis: "It is not a current project strategy.",
              open_gate: "The constraint exists; the open gate is how a source sector satisfies it."
            }
          },
          chl: {
            correct: "CHL is a published literature analysis of Alcubierre null geodesics.",
            statuses: {
              established_theory: "It is a paper result about a speculative model, not baseline GR vocabulary.",
              established_constraint: "It is causal-access literature rather than a general constraint theorem.",
              active_rail_model: "It predates the project and is not project architecture.",
              project_hypothesis: "It is not current project evidence.",
              open_gate: "The statement identifies what the paper analyzes, not a missing project proof."
            }
          },
          ledger: {
            correct: "A demanded-source ledger is active-rail model bookkeeping.",
            statuses: {
              established_theory: "The equations used are established, but the ledger is architecture bookkeeping.",
              established_constraint: "The ledger is not a constraint theorem.",
              literature_model: "It is not an external speculative metric paper.",
              project_hypothesis: "The ledger convention is model language, not a provisional source strategy by itself.",
              open_gate: "Recording demand is not the same as the unresolved realization claim."
            }
          },
          candidate: {
            correct: "A current fixed-background source family is project-hypothesis evidence.",
            statuses: {
              established_theory: "Current fixed-background evidence is not established GR.",
              established_constraint: "It is not a general constraint theorem.",
              literature_model: "It is not an external paper model.",
              active_rail_model: "It is more provisional than stable model vocabulary.",
              open_gate: "It is candidate evidence, not a completed missing demonstration."
            }
          },
          matter: {
            correct: "A repeated-service microphysical matter sector remains an open gate.",
            statuses: {
              established_theory: "Established GR does not supply this specific project matter sector.",
              established_constraint: "This is a missing realization claim rather than a constraint theorem.",
              literature_model: "A paper model does not supply this active-rail matter sector.",
              active_rail_model: "The statement asserts completion, not only architecture vocabulary.",
              project_hypothesis: "The safer status is open because the completed sector has not been supplied."
            }
          }
        }
      },
      references: [references.carrollGrNotes, references.fordRoman, references.clarkHiscockLarson],
      sourceLinks: [sources.componentSourceLedger, sources.sourceFamilyValidation],
      openGate: "The matter-sector statement remains open until separately demonstrated."
    }
  },
  {
    id: "active_rail.reset_reuse.sequence.007",
    type: "sequence",
    track: "Design review and synthesis",
    module: "Evidence sufficiency",
    difficulty: "advanced",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    prompt: "Order the evidence needed before promoting a one-pass service result into a repeated-use readiness claim.",
    items: [
      { id: "one_pass", content: "Document the one-pass packet and plant-channel result" },
      { id: "residue", content: "Measure post-pass source/support residue" },
      { id: "reset", content: "Apply and verify reset/decompression procedure" },
      { id: "repeat", content: "Repeat service after reset under comparable conditions" },
      { id: "drift", content: "Audit drift or accumulation across repeated cycles" }
    ],
    answer: ["one_pass", "residue", "reset", "repeat", "drift"],
    explanation: {
      answer: "One-pass result, residue measurement, reset verification, repeated service, drift audit.",
      why: "A repeated-use claim needs evidence about history dependence. A successful single pass and a service process that remains controlled after reset cycles are different claims.",
      boundary: "This is active-rail review logic with open reset and accumulation gates, not textbook GR terminology.",
      adaptive: {
        sequence: [
          {
            id: "one-pass-before-residue",
            before: "one_pass",
            after: "residue",
            content: "The one-pass result is documented before post-pass residue can be interpreted."
          },
          {
            id: "residue-before-reset",
            before: "residue",
            after: "reset",
            content: "Residue measurement comes before reset verification because reset is judged against the post-pass state."
          },
          {
            id: "reset-before-repeat",
            before: "reset",
            after: "repeat",
            content: "Repeated service should follow verified reset, not assume reset succeeded."
          },
          {
            id: "repeat-before-drift",
            before: "repeat",
            after: "drift",
            content: "Drift or accumulation is audited after repeated cycles reveal history dependence."
          }
        ]
      },
      references: [],
      sourceLinks: [sources.resetReleaseLadder, sources.boundedSealReadiness],
      openGate: "Longer-horizon reset accumulation remains a separate qualification surface."
    }
  },
  {
    id: "foundation.adm_gauge_constraint_interpretation.003",
    type: "multi",
    track: "Established foundations",
    module: "ADM split",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Two 3+1 evolutions describe the same geometric setup with different lapse and shift choices. One has cleaner coordinate-looking trajectories but a larger constraint residual on later slices. Which review conclusions are justified?",
    choices: [
      { id: "gauge_not_clear", content: "Cleaner coordinate trajectories do not by themselves clear a larger constraint residual." },
      { id: "separate_roles", content: "Gauge choices should be separated from constraint satisfaction and physical invariant claims." },
      { id: "invariants", content: "Physical interpretation should use invariant or constraint-aware checks, not coordinate appearance alone." },
      { id: "trajectory_wins", content: "Cleaner coordinate trajectories are strong evidence for the physically better evolution when the compared setups describe the same geometry." },
      { id: "lapse_shift_source", content: "Changing lapse and shift changes the foliation enough that the implied stress-energy interpretation should be recomputed from scratch." }
    ],
    answer: ["gauge_not_clear", "separate_roles", "invariants"],
    explanation: {
      answer: "Gauge appearance, constraint satisfaction, invariant checks, and physical interpretation must be reviewed separately.",
      why: "A coordinate improvement is not automatically a physical improvement. Lapse and shift affect how the foliation is described, while the Hamiltonian and momentum constraints still test whether the slice data remain compatible with Einstein's equation.",
      boundary: "This is established ADM and gauge reasoning, not an endorsement of any particular numerical gauge or engineering architecture.",
      adaptive: {
        choices: {
          gauge_not_clear: {
            supported: "Cleaner coordinate trajectories do not clear a larger constraint residual."
          },
          separate_roles: {
            supported: "Gauge choices, constraint satisfaction, and invariant physical claims have different roles."
          },
          invariants: {
            supported: "Physical interpretation should not rest on coordinate appearance alone."
          },
          trajectory_wins: {
            unsupported: "Cleaner coordinate trajectories are useful diagnostics, but they do not override constraint or invariant checks."
          },
          lapse_shift_source: {
            unsupported: "Changing lapse and shift changes the foliation description; it does not by itself supply a new physical source."
          }
        }
      },
      references: [references.adm]
    }
  },
  {
    id: "foundation.conserved_tensor_realization.003",
    type: "multi",
    track: "Established foundations",
    module: "Einstein equation",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A prescribed metric yields a demanded stress-energy tensor whose covariant divergence vanishes. The tensor also has unusual principal pressures and no proposed matter Lagrangian. Which conclusions are justified?",
    choices: [
      { id: "necessary", content: "Covariant conservation is a necessary consistency check for the demanded tensor." },
      { id: "not_realized", content: "Conservation does not by itself supply a viable matter model or stability analysis." },
      { id: "pressures_need_model", content: "Unusual principal pressures should be examined for dynamics, energy conditions, and physical interpretation." },
      { id: "lagrangian_unneeded", content: "A conserved tensor with coherent pressure structure can be treated as a strong proxy for ordinary-matter realizability." },
      { id: "pressures_irrelevant", content: "Principal pressures are mainly material-model details once conservation and energy density are under control." }
    ],
    answer: ["necessary", "not_realized", "pressures_need_model"],
    explanation: {
      answer: "Conservation is necessary but not sufficient, and unusual pressure structure still needs physical review.",
      why: "Bianchi consistency can be satisfied while the inferred stress tensor still lacks a microphysical model, equations of motion, stability behavior, or acceptable energy-condition profile. Those are separate burdens.",
      boundary: "This is general GR claim discipline, independent of project-specific source ledgers or service-readiness language.",
      adaptive: {
        choices: {
          necessary: {
            supported: "Covariant conservation is a necessary consistency check for the demanded tensor."
          },
          not_realized: {
            supported: "Conservation alone does not supply a viable matter model or stability analysis."
          },
          pressures_need_model: {
            supported: "Unusual principal pressures need dynamics, energy-condition, and interpretation review."
          },
          lagrangian_unneeded: {
            unsupported: "A coherent conserved tensor is useful, but ordinary-matter realization still needs matter dynamics and stability support."
          },
          pressures_irrelevant: {
            unsupported: "Principal pressures affect energy conditions, dynamics, and source interpretation."
          }
        }
      },
      references: [references.carrollGrNotes, references.energyConditionsPrimer]
    }
  },
  {
    id: "foundation.energy_condition_type_i.005",
    type: "multi",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "For a diagonal type-I stress tensor in an orthonormal frame, a review finds positive energy density but one principal pressure is strongly negative. Which cautions are justified before claiming classical energy-condition safety?",
    choices: [
      { id: "nec_combo", content: "The sums of density plus each principal pressure still matter for null-energy-condition checks." },
      { id: "wec_observers", content: "The weak energy condition concerns all timelike observers, not just the comoving density." },
      { id: "principal_directions", content: "Each principal direction can matter; one benign component does not clear every contraction." },
      { id: "density_enough", content: "Positive comoving density is the dominant check when the pressure anisotropy is confined to one principal direction." },
      { id: "pressure_no_gravity", content: "Principal pressures mainly affect material interpretation; the energy-condition decision is carried by observer-measured density." }
    ],
    answer: ["nec_combo", "wec_observers", "principal_directions"],
    explanation: {
      answer: "Positive density alone is not enough; pressure combinations, principal directions, and observer quantifiers remain essential.",
      why: "For a type-I tensor, energy-condition review depends on the tensor's pressure structure as well as its density. A large negative principal pressure can violate density-plus-pressure inequalities even when one observer measures positive density.",
      boundary: "This is established pointwise energy-condition reasoning; it does not assert that pointwise conditions are the only relevant quantum or averaged constraints.",
      adaptive: {
        choices: {
          nec_combo: {
            supported: "For type-I tensors, density-plus-principal-pressure combinations enter NEC checks."
          },
          wec_observers: {
            supported: "The WEC quantifies over all timelike observers, not only the comoving density."
          },
          principal_directions: {
            supported: "Each principal direction can expose a different contraction."
          },
          density_enough: {
            unsupported: "Even one strongly negative principal pressure can affect density-plus-pressure inequalities."
          },
          pressure_no_gravity: {
            unsupported: "Principal pressures are stress-energy components; they affect both material interpretation and energy-condition contractions."
          }
        }
      },
      references: [references.energyConditionsPrimer]
    }
  },
  {
    id: "foundation.cauchy_problem_global_patch.004",
    type: "multi",
    track: "Established foundations",
    module: "Causal structure",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A local metric patch is smooth and numerically well behaved, but the proposed spacetime extension may contain horizon-like boundaries and lacks a demonstrated Cauchy surface for the full region. Which conclusions are justified?",
    choices: [
      { id: "local_insufficient", content: "Local smoothness does not establish a well-posed global causal extension." },
      { id: "cauchy_needed", content: "A Cauchy-surface or global-hyperbolicity claim needs separate support." },
      { id: "boundary_data", content: "Boundary behavior can affect whether the local patch supports the proposed global claim." },
      { id: "domain_of_dependence", content: "The domain of dependence for the data used in the claim has to be identified or bounded." },
      { id: "patch_solves", content: "A smooth local patch can support a global-hyperbolicity claim when the intended extension is regular and numerically stable." },
      { id: "horizons_irrelevant", content: "Horizon-like boundaries affect signal routing, but predictability can often be reviewed after the local patch is validated." }
    ],
    answer: ["local_insufficient", "cauchy_needed", "boundary_data", "domain_of_dependence"],
    explanation: {
      answer: "The local patch is useful evidence, but global predictability, domain of dependence, and boundary behavior remain separate questions.",
      why: "Smooth local geometry matters, but it does not settle the causal domain, existence of Cauchy surfaces, boundary behavior, or whether data determine the full region used by the claim.",
      boundary: "This is established global-causality reasoning, not a project-state judgment about any specific simulated patch.",
      adaptive: {
        choices: {
          local_insufficient: {
            supported: "Local smoothness does not establish a well-posed global extension."
          },
          cauchy_needed: {
            supported: "A Cauchy-surface or global-hyperbolicity claim needs separate support."
          },
          boundary_data: {
            supported: "Boundary behavior can control whether the local patch supports the global claim."
          },
          domain_of_dependence: {
            supported: "The domain of dependence has to be identified or bounded for predictability claims."
          },
          patch_solves: {
            unsupported: "A regular local patch helps, but global hyperbolicity still requires support for the full extension."
          },
          horizons_irrelevant: {
            unsupported: "Horizon-like boundaries are part of predictability and signal-routing review, not a later cosmetic detail."
          }
        }
      },
      references: [references.globalHyperbolicityReview, references.cauchyHypersurfaces, references.causalHierarchy]
    }
  },
  {
    id: "literature.alcubierre_assumption_transfer.006",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Metric basics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A proposal cites Alcubierre's 1994 warp metric and then claims that choosing a smooth bubble profile is enough to make the model an engineering design. Which objections are justified?",
    choices: [
      { id: "metric_not_source", content: "A smooth prescribed metric does not by itself supply the required stress-energy source." },
      { id: "energy_burden", content: "Energy-condition and source-realization burdens remain after the metric ansatz is written." },
      { id: "control_open", content: "Controllability and causal access are separate from the existence of the metric ansatz." },
      { id: "smooth_sufficient", content: "Smoothness of the bubble profile is the main regularity condition, so source and control questions become secondary follow-up checks." },
      { id: "paper_demonstrates", content: "The 1994 metric demonstrates a consistent GR target, so buildability mainly depends on later engineering maturity." }
    ],
    answer: ["metric_not_source", "energy_burden", "control_open"],
    explanation: {
      answer: "The Alcubierre metric is a published speculative spacetime model, not a completed source, control, or engineering design.",
      why: "The paper supplies a mathematically clear metric ansatz, but that does not inflate into a source model. Stress-energy, energy-condition, stability, and control questions remain separate.",
      boundary: "This is literature-model framing for Alcubierre's 1994 result; it is not a claim about a current architecture succeeding or failing.",
      adaptive: {
        choices: {
          metric_not_source: {
            supported: "A metric ansatz fixes the geometry to analyze; it does not identify matter fields or a mechanism that produces the required Einstein tensor."
          },
          energy_burden: {
            supported: "The stress-energy implied by the metric remains part of the physical burden, including energy-condition and source-realization review."
          },
          control_open: {
            supported: "Existence of a formal spacetime is separate from whether signals, actuators, or boundary access could control it."
          },
          smooth_sufficient: {
            unsupported: "Smoothness helps the model be mathematically well behaved, but it does not demote source and control questions to secondary checks."
          },
          paper_demonstrates: {
            unsupported: "A consistent GR target remains distinct from buildability; the paper does not establish the engineering path."
          }
        }
      },
      references: [references.alcubierre]
    }
  },
  {
    id: "literature.natario_zero_expansion_limits.004",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A reviewer cites Natario's 2002 zero-expansion warp-drive construction and claims zero expansion removes the exotic-source problem. Which responses are justified?",
    choices: [
      { id: "expansion_not_all", content: "Zero expansion changes one geometric feature but does not automatically clear stress-energy or energy-condition issues." },
      { id: "check_shift", content: "The construction still requires careful review of the shift-driven geometry and inferred source demand." },
      { id: "causal_review", content: "Causal use and control assumptions still need review outside the zero-expansion statement." },
      { id: "zero_source", content: "Zero expansion removes the volume-change contribution, so any remaining Einstein-tensor terms are the secondary part of the model." },
      { id: "no_review_needed", content: "Once expansion is zero, source analysis can focus on the shift profile while causal review is largely unchanged." }
    ],
    answer: ["expansion_not_all", "check_shift", "causal_review"],
    explanation: {
      answer: "Zero expansion is an important geometric property, not a complete source, causal, or physical-realization result.",
      why: "A specific geometric improvement should not be collapsed into universal clearance. Expansion, inferred stress-energy, energy-condition behavior, and causal use are different review surfaces, so a zero-expansion construction still needs source and causality analysis.",
      boundary: "This is paper-specific literature interpretation of Natario's 2002 model, not a general theorem that all zero-expansion metrics are viable or impossible.",
      adaptive: {
        choices: {
          expansion_not_all: {
            supported: "Zero expansion constrains one kinematic feature of the congruence; it does not by itself settle the required stress-energy."
          },
          check_shift: {
            supported: "Natario-type constructions are shift-driven, so the geometry and source demand still have to be read through the field equations."
          },
          causal_review: {
            supported: "Causal use, access, and control assumptions are not erased by a zero-expansion condition."
          },
          zero_source: {
            unsupported: "Zero expansion constrains one geometric feature; it does not make the remaining Einstein-tensor terms secondary or absent."
          },
          no_review_needed: {
            unsupported: "The shift profile and causal behavior both remain active review surfaces, not a narrowed afterthought."
          }
        }
      },
      references: [references.natario]
    }
  },
  {
    id: "literature.muller_weiskopf_observable_limits.004",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp geodesics",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A visualization based on Mueller and Weiskopf's 2012 geodesic study shows plausible-looking photon paths through an Alcubierre bubble. Which conclusions are justified?",
    choices: [
      { id: "geodesic_value", content: "Geodesic behavior is valuable for understanding observables and causal access in the model." },
      { id: "not_source", content: "Plausible-looking geodesics do not supply the stress-energy source or prove physical feasibility." },
      { id: "fixed_model", content: "The conclusion is about paths inside the modeled spacetime, not about how to generate that spacetime." },
      { id: "visual_proves", content: "A convincing optical visualization is strong indirect evidence that the modeled spacetime has coherent physical behavior." },
      { id: "no_causal_questions", content: "Once geodesics are plotted, horizon and reachability questions can be read from the paths without separate causal analysis." }
    ],
    answer: ["geodesic_value", "not_source", "fixed_model"],
    explanation: {
      answer: "The geodesic analysis is informative inside the fixed model, but it does not close source or control questions.",
      why: "Observable behavior inside a fixed spacetime model is separate from the independent burden of generating that spacetime and controlling its causal boundaries. Geodesic plots can be physically informative while still leaving source, stability, and control claims unresolved.",
      boundary: "This is a literature-model reading of the 2012 Alcubierre geodesic study, not an engineering qualification claim.",
      adaptive: {
        choices: {
          geodesic_value: {
            supported: "Null and timelike paths are directly relevant to what observers could see and which regions can exchange signals within the modeled spacetime."
          },
          not_source: {
            supported: "Tracing geodesics assumes the spacetime model; it does not provide the stress-energy or construction mechanism for that model."
          },
          fixed_model: {
            supported: "The result is about behavior in a specified geometry, so generation and control remain different questions."
          },
          visual_proves: {
            unsupported: "A visualization can clarify model behavior, but coherent modeled behavior does not prove generation or control."
          },
          no_causal_questions: {
            unsupported: "Geodesic plots inform causal analysis, but they do not replace separate horizon and reachability interpretation."
          }
        }
      },
      references: [references.mullerWeiskopf]
    }
  },
  {
    id: "literature.everett_roman_network_causality.004",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Chronology concerns",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A shortcut-network concept cites Everett and Roman's 1997 Krasnikov-tube analysis but treats a one-way superluminal route as automatically safe in every network arrangement. Which cautions are justified?",
    choices: [
      { id: "network_matters", content: "Network composition and return paths matter for chronology and causality analysis." },
      { id: "energy_burden", content: "Negative-energy and quantum-inequality burdens remain relevant to the proposed shortcut structure." },
      { id: "one_way_limited", content: "A one-way description of one route does not settle the causal behavior of a larger network." },
      { id: "one_way_safe", content: "A one-way route is enough to control chronology risk unless a second route is explicitly added." },
      { id: "chronology_no_energy", content: "Chronology review can be separated from stress-energy review because it concerns network arrangement rather than source construction." }
    ],
    answer: ["network_matters", "energy_burden", "one_way_limited"],
    explanation: {
      answer: "The network arrangement, one-route limitation, and exotic-source burden all remain part of the review.",
      why: "Local shortcut behavior and global network composition interact. A route that is described one way in isolation can still participate in broader causal loops or require exotic stress-energy.",
      boundary: "This is paper-specific reasoning from the 1997 Krasnikov-tube literature, not a claim about any current project route.",
      adaptive: {
        choices: {
          network_matters: {
            supported: "Chronology analysis depends on how shortcut segments compose, especially when return paths or multiple tubes are available."
          },
          energy_burden: {
            supported: "The causal question does not remove the stress-energy and quantum-inequality issues associated with the shortcut structure."
          },
          one_way_limited: {
            supported: "A one-way description of a single route is a local constraint, not a proof about every larger network."
          },
          one_way_safe: {
            unsupported: "The risk lives in network composition; a one-way segment does not settle what paired or return routes can do."
          },
          chronology_no_energy: {
            unsupported: "Chronology and stress-energy are distinct, but both remain necessary review surfaces for the shortcut structure."
          }
        }
      },
      references: [references.everettRoman, references.fordRoman]
    }
  },
  {
    id: "literature.barcelo_visser_scalar_caveat.004",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Scalar-source literature",
    difficulty: "advanced",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A source proposal cites Barcelo and Visser's 2000 scalar-field wormhole work and concludes that non-minimal coupling makes exotic-source worries disappear. Which review responses are justified?",
    choices: [
      { id: "mechanism_specific", content: "Non-minimal coupling can change energy-condition behavior, but the mechanism and regime must be specified." },
      { id: "caveats_matter", content: "Trans-Planckian, stability, and model-dependence caveats remain relevant to physical interpretation." },
      { id: "not_generic", content: "A scalar-field label alone does not identify a realizable source for an arbitrary geometry." },
      { id: "coupling_equations", content: "The field equations and coupling assumptions matter, not only the sign of one stress-tensor component." },
      { id: "generic_clearance", content: "A non-minimally coupled scalar result gives enough mechanism detail to treat scalar-source proposals as a favored class by default." },
      { id: "no_boundary", content: "Because the proposal names a field theory rather than an algebraic tensor, mathematical solution and physical realization are much closer together." }
    ],
    answer: ["mechanism_specific", "caveats_matter", "not_generic", "coupling_equations"],
    explanation: {
      answer: "The scalar-field literature supplies a coupling-dependent mechanism to study, not a blanket or generic source clearance.",
      why: "Mechanism, field equations, coupling assumptions, and physical regime have to remain attached to the claim. Non-minimal coupling can alter energy-condition conclusions, but it does not erase stability, scale, or realization burdens.",
      boundary: "This is a bounded reading of Barcelo and Visser's 2000 paper, not a generic approval of scalar-field source models.",
      adaptive: {
        choices: {
          mechanism_specific: {
            supported: "The energy-condition result depends on the coupling and field configuration, so the mechanism has to be stated rather than inferred from the label."
          },
          caveats_matter: {
            supported: "The paper's physical interpretation includes scale, stability, and model-dependence cautions that stay attached to the result."
          },
          not_generic: {
            supported: "A scalar-field name does not specify the equations, boundary conditions, or regime needed for a particular geometry."
          },
          coupling_equations: {
            supported: "The relevant claim lives in the coupled field equations, not in one isolated sign or component."
          },
          generic_clearance: {
            unsupported: "Non-minimal scalar mechanisms are specific; they do not make every scalar-source proposal favored by default."
          },
          no_boundary: {
            unsupported: "A field-theory model narrows the gap, but physical regime, stability, and scale still separate solution from realization."
          }
        }
      },
      references: [references.barceloVisser]
    }
  },
  {
    id: "foundation.nec_single_direction_scope.006",
    type: "multi",
    track: "Established foundations",
    module: "Energy conditions",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: [
      "A calculation checks ",
      { type: "math", latex: "T_{\\mu\\nu}k^\\mu k^\\nu \\ge 0", label: "T mu nu k mu k nu greater than or equal to zero" },
      " for one named null vector at one event. Which conclusion is supported by that calculation alone?"
    ],
    choices: [
      { id: "one_direction", content: "That sampled null contraction passed at that event." },
      { id: "global_nec", content: "The result can be used as evidence for the NEC if symmetry or continuity makes nearby null directions representative." },
      { id: "wec", content: "The result supports weak-energy-condition safety when the sampled null vector is aligned with the dominant energy-flow direction." },
      { id: "source_model", content: "The result supports source viability if the sampled contraction is the channel expected to be most negative." }
    ],
    answer: ["one_direction"],
    explanation: {
      answer: "Only the sampled null contraction has been checked.",
      why: "The NEC is a quantified condition over null directions and regions. One positive contraction can be useful evidence, but it does not establish the full condition, the WEC, or a physical source model.",
      boundary: "This is established energy-condition scope control, not a statement about any particular architecture.",
      adaptive: {
        choices: {
          one_direction: {
            supported: "The calculation supports exactly the tested contraction at the tested event."
          },
          global_nec: {
            unsupported: "Symmetry or continuity would have to be shown; a single sampled direction alone does not establish the full NEC."
          },
          wec: {
            unsupported: "The WEC has different timelike-observer quantifiers, so alignment with one null direction is not enough."
          },
          source_model: {
            unsupported: "A worst-channel contraction can be useful evidence, but it still does not provide matter dynamics or a source mechanism."
          }
        }
      },
      references: [references.energyConditionsPrimer]
    }
  },
  {
    id: "literature.alcubierre_supported_claim.007",
    type: "multi",
    track: "Published warp and wormhole context",
    module: "Warp metrics",
    difficulty: "intermediate",
    claimStatus: "literature_model",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "From Alcubierre's 1994 paper \"The Warp Drive\" alone, which claim is safest?",
    choices: [
      { id: "metric_model", content: "It gives a speculative warp metric whose interpretation includes severe stress-energy concerns." },
      { id: "ordinary_engine", content: "It identifies the stress-energy target closely enough that ordinary-matter engineering becomes a later source-design question." },
      { id: "central_control", content: "It leaves the central observer in a locally mild region, which supports a limited onboard-control reading." },
      { id: "quantum_clear", content: "It is a classical GR model, so quantum-inequality and semiclassical questions are outside its claim rather than problems for the metric." },
      { id: "chronology_clear", content: "It analyzes a single warp metric, so broader chronology-network issues are outside the result rather than active cautions." }
    ],
    answer: ["metric_model"],
    explanation: {
      answer: "The safest claim is that Alcubierre provides a speculative metric model with severe source concerns.",
      why: "The paper is foundational because it writes a concrete spacetime ansatz for warp-like motion. That is not the same as deriving an ordinary source, proving onboard control, or resolving later quantum and chronology constraints.",
      boundary: "This is a bounded paper-theory claim about the 1994 metric, not physical realization.",
      adaptive: {
        choices: {
          metric_model: {
            supported: "The paper's durable contribution is the explicit metric model and the recognition that its implied stress-energy is severe."
          },
          ordinary_engine: {
            unsupported: "Identifying a stress-energy target is not the same as showing ordinary matter can generate it."
          },
          central_control: {
            unsupported: "A locally mild central region does not prove causal control over the wall during superluminal operation."
          },
          quantum_clear: {
            unsupported: "Being outside the paper's classical claim does not make quantum and semiclassical concerns disappear."
          },
          chronology_clear: {
            unsupported: "Network chronology issues are outside the paper's result, so they remain cautions rather than cleared claims."
          }
        }
      },
      references: [references.alcubierre]
    }
  },
  {
    id: "design_review.single_observable_scope.006",
    type: "multi",
    track: "Design review and synthesis",
    module: "Evidence sufficiency",
    difficulty: "intermediate",
    claimStatus: "active_rail_model",
    contentFlags: ["project_material", "open_question"],
    scoring: "subtract_incorrect",
    prompt: "A report provides only one clean final packet observable and no plant-channel, source, endpoint, or reset evidence. Which conclusion is justified?",
    choices: [
      { id: "packet_only", content: "Only the reported packet-facing observable is supported." },
      { id: "plant_full", content: "The plant can be provisionally accepted if the missing channels are downstream of the packet observable." },
      { id: "source_closed", content: "The clean observable is indirect evidence that the source sector is at least functionally realized for this pass." },
      { id: "repeat_ready", content: "Repeated-use readiness can be inferred if the final observable shows no visible residue." },
      { id: "general_theory", content: "The scope rule follows from general evidence discipline rather than project-specific architecture." }
    ],
    answer: ["packet_only"],
    explanation: {
      answer: "Only the packet-facing observable is supported by the stated evidence.",
      why: "A single clean observable can be valuable without carrying every adjacent claim. Plant burden, source realization, endpoint handoff, reset residue, and repeated-use readiness each need their own evidence.",
      boundary: "This is active-rail evidence-scope discipline with open gates, not established external certification doctrine.",
      adaptive: {
        choices: {
          packet_only: {
            supported: "The scenario gives evidence for the packet-facing observable and should be credited at that scope."
          },
          plant_full: {
            unsupported: "Missing plant channels cannot be accepted merely as downstream of the packet observable."
          },
          source_closed: {
            unsupported: "A clean observable is useful but does not identify or realize the source sector."
          },
          repeat_ready: {
            unsupported: "No visible final residue is not the same as reset and reuse evidence."
          },
          general_theory: {
            unsupported: "General evidence discipline helps, but the specific claim is about active-rail channel scope."
          }
        }
      },
      references: [],
      sourceLinks: [sources.technicalDisclosure, sources.resetReleaseLadder, sources.componentSourceLedger],
      openGate: "Plant, source, endpoint, reset, and repeatability evidence remain open in the scenario."
    }
  },
  {
    id: "foundation.dimensional_analysis.001",
    type: "mc",
    track: "Established foundations",
    module: "Dimensional analysis",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What is dimensional analysis mainly used for in physical modeling?",
    choices: [
      { id: "consistency", content: "Checking that equations compare like physical quantities and scale consistently." },
      { id: "proof", content: "Proving that a proposed source mechanism is dynamically stable." },
      { id: "coordinate", content: "Choosing the coordinate chart that makes the metric simplest." },
      { id: "quantization", content: "Turning a classical field into a quantum operator." }
    ],
    answer: ["consistency"],
    explanation: {
      answer: "Dimensional analysis checks physical consistency and scaling.",
      why: "An equation that adds or equates unlike dimensions cannot be a correct physical law. Dimensional analysis also exposes scale dependence before a detailed calculation is trusted.",
      boundary: "This is general modeling discipline; it does not prove stability, source realization, or coordinate validity by itself.",
      adaptive: {
        choices: {
          consistency: {
            supported: "The direct use is checking dimensions and scale consistency across a model."
          },
          proof: {
            unsupported: "Dimensional consistency is necessary but far short of a stability proof."
          },
          coordinate: {
            unsupported: "Coordinate choices can simplify equations, but dimensional analysis is about physical units and scales."
          },
          quantization: {
            unsupported: "Quantization is a separate step from checking dimensions."
          }
        }
      },
      references: [references.openStaxQuantum]
    }
  },
  {
    id: "foundation.scale_regime.001",
    type: "multi",
    track: "Established foundations",
    module: "Modeling discipline",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A calculation is valid only after assuming a small parameter, a smooth background, and wavelengths much larger than a cutoff scale. Which review statements are careful?",
    choices: [
      { id: "state_regime", content: "The validity regime should be stated with the result." },
      { id: "avoid_transfer", content: "The result should not be transferred to short wavelengths without a new argument." },
      { id: "scale_error", content: "Changing the scale can change which terms or effects are negligible." },
      { id: "exact_theory", content: "A controlled approximation can be treated as an exact theory when it is numerically accurate in one benchmark." },
      { id: "smooth_enough", content: "A smooth background usually makes cutoff sensitivity a bookkeeping issue rather than a physical limitation." }
    ],
    answer: ["state_regime", "avoid_transfer", "scale_error"],
    explanation: {
      answer: "The result should carry its validity regime, scale limits, and approximation assumptions.",
      why: "Approximation success is not portable without checking the assumptions that made terms small. Scale changes can move neglected physics into the leading-order behavior.",
      boundary: "This is general modeling practice and applies before interpreting any specific metric, source, or quantum calculation.",
      adaptive: {
        choices: {
          state_regime: {
            supported: "A result should say which small parameters, smoothness assumptions, and scales it uses."
          },
          avoid_transfer: {
            supported: "Short-wavelength behavior needs its own argument if the calculation assumed long wavelengths."
          },
          scale_error: {
            supported: "Terms can change importance when the relevant scale changes."
          },
          exact_theory: {
            unsupported: "A benchmark can support an approximation in one regime, but it does not make the approximation exact."
          },
          smooth_enough: {
            unsupported: "Smoothness helps, but cutoff sensitivity can remain a physical validity limitation."
          }
        }
      },
      references: [references.burgessEft]
    }
  },
  {
    id: "foundation.stability.001",
    type: "mc",
    track: "Established foundations",
    module: "Stability and perturbations",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What does linear stability analysis usually test?",
    choices: [
      { id: "small_growth", content: "Whether small perturbations around a background grow, decay, or oscillate within the linearized model." },
      { id: "global_realization", content: "Whether decaying modes make ordinary-matter sourcing plausible for the background." },
      { id: "nonlinear_complete", content: "Whether large disturbances are likely controlled once all linear modes decay." },
      { id: "coordinate_free", content: "Whether apparent growth has already been separated from gauge or coordinate behavior." }
    ],
    answer: ["small_growth"],
    explanation: {
      answer: "Linear stability tracks small perturbations around a background.",
      why: "The method expands around a background and studies the leading perturbation behavior. It can reveal growing modes, but it does not settle nonlinear stability or source realization.",
      boundary: "This is general perturbation theory, not a guarantee about full nonlinear dynamics or matter-sector feasibility.",
      adaptive: {
        choices: {
          small_growth: {
            supported: "Linear stability asks how small perturbations behave inside the linearized equations."
          },
          global_realization: {
            unsupported: "Decaying modes are useful evidence, but source realization is a different question from perturbation growth."
          },
          nonlinear_complete: {
            unsupported: "Linear decay supports local stability, but it does not automatically control large disturbances."
          },
          coordinate_free: {
            unsupported: "Gauge or coordinate separation may be part of the analysis, but it is not the main definition of linear stability."
          }
        }
      },
      references: [references.burgessEft, references.carrollGrNotes]
    }
  },
  {
    id: "foundation.boundary_conditions.sequence.001",
    type: "sequence",
    track: "Established foundations",
    module: "Boundary conditions",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Order a conservative boundary-condition review for a model calculation.",
    items: [
      { id: "domain", content: "State the domain being modeled" },
      { id: "fields", content: "Name the fields and equations on that domain" },
      { id: "boundary", content: "Specify boundary or asymptotic conditions" },
      { id: "solve", content: "Solve or approximate inside the stated setup" },
      { id: "interpret", content: "Interpret only within the domain and conditions used" }
    ],
    answer: ["domain", "fields", "boundary", "solve", "interpret"],
    explanation: {
      answer: "State domain, state fields/equations, specify boundaries, solve, then interpret within that setup.",
      why: "Boundary conditions are part of the problem, not decoration after the calculation. The same differential equation can support different physical conclusions under different domains or boundaries.",
      boundary: "This is general mathematical-physics practice and does not decide any particular source or spacetime claim.",
      adaptive: {
        sequence: [
          {
            id: "domain-before-fields",
            before: "domain",
            after: "fields",
            content: "The domain tells what region the fields and equations live on."
          },
          {
            id: "fields-before-boundary",
            before: "fields",
            after: "boundary",
            content: "Boundary conditions are attached to named equations and fields."
          },
          {
            id: "boundary-before-solve",
            before: "boundary",
            after: "solve",
            content: "The boundary setup is part of the mathematical problem being solved."
          },
          {
            id: "solve-before-interpret",
            before: "solve",
            after: "interpret",
            content: "Interpretation should stay inside the domain and assumptions actually solved."
          }
        ]
      },
      references: [references.burgessEft]
    }
  },
  {
    id: "foundation.qm_state_observable.001",
    type: "mc",
    track: "Established foundations",
    module: "Quantum basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In basic quantum mechanics, what is an observable?",
    choices: [
      { id: "operator", content: "A measurable quantity represented mathematically by an operator." },
      { id: "trajectory", content: "A definite classical path followed by a particle between measurements." },
      { id: "vacuum", content: "The lowest-energy state of a quantum field." },
      { id: "source", content: "The stress-energy tensor required by a spacetime metric." }
    ],
    answer: ["operator"],
    explanation: {
      answer: "An observable is a measurable quantity represented by an operator.",
      why: "Quantum theory separates state preparation from measurement. Observables such as energy, momentum, or position are represented by operators whose possible measurement results are tied to the operator spectrum.",
      boundary: "This is basic quantum mechanics and should not be promoted into a claim about field-theory vacuum sources.",
      adaptive: {
        choices: {
          operator: {
            supported: "The operator representation is the direct quantum-mechanics meaning."
          },
          trajectory: {
            unsupported: "A definite classical trajectory is not the general quantum observable concept."
          },
          vacuum: {
            unsupported: "A vacuum state is a state, not the definition of an observable."
          },
          source: {
            unsupported: "Stress-energy source demand is a relativistic field concept, not the basic definition of observable."
          }
        }
      },
      references: [references.openStaxQuantum]
    }
  },
  {
    id: "foundation.qm.expectation.001",
    type: "mc",
    track: "Established foundations",
    module: "Quantum basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What does an expectation value represent in quantum mechanics?",
    choices: [
      { id: "average", content: "The predicted average measurement result over many similarly prepared systems." },
      { id: "single", content: "The guaranteed result of the next individual measurement." },
      { id: "classical", content: "A hidden classical value that the system carried all along." },
      { id: "energy_source", content: "A directly extractable energy source." }
    ],
    answer: ["average"],
    explanation: {
      answer: "An expectation value is an ensemble average prediction.",
      why: "A quantum state can assign probabilities to measurement outcomes. The expectation value summarizes the average over repeated preparations, not a guarantee for one event.",
      boundary: "This is quantum-measurement vocabulary; it is not a source-realization or extractable-energy statement.",
      adaptive: {
        choices: {
          average: {
            supported: "Expectation values summarize repeated-measurement averages for a prepared state."
          },
          single: {
            unsupported: "A single measurement can differ from the expectation value."
          },
          classical: {
            unsupported: "The expectation value is not generally a hidden classical value."
          },
          energy_source: {
            unsupported: "A measured or expected energy value is not automatically an extractable source."
          }
        }
      },
      references: [references.openStaxQuantum]
    }
  },
  {
    id: "foundation.qm.uncertainty.001",
    type: "multi",
    track: "Established foundations",
    module: "Quantum basics",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements about the uncertainty principle are careful?",
    choices: [
      { id: "noncommuting", content: "It reflects limits associated with noncommuting observables." },
      { id: "preparation", content: "It constrains how sharply certain pairs of quantities can be prepared together." },
      { id: "not_sloppy", content: "It is not merely a statement about bad instruments or sloppy measurement." },
      { id: "energy_free", content: "It permits temporary energy imbalances that can be accumulated into a usable macroscopic source." },
      { id: "all_pairs", content: "It applies in the same way to every pair of measurable quantities." }
    ],
    answer: ["noncommuting", "preparation", "not_sloppy"],
    explanation: {
      answer: "Uncertainty is tied to noncommuting observables and state preparation, not just instrument quality.",
      why: "The principle is structural in quantum mechanics. It limits simultaneous sharpness for specific observable pairs, but it does not license arbitrary energy borrowing or apply identically to every pair of observables.",
      boundary: "This is established quantum theory; it should not be used as a shortcut to macroscopic source claims.",
      adaptive: {
        choices: {
          noncommuting: {
            supported: "Noncommutation is the mathematical source of many uncertainty relations."
          },
          preparation: {
            supported: "The relation constrains preparation sharpness for the relevant observable pair."
          },
          not_sloppy: {
            supported: "The principle is not merely about imperfect devices."
          },
          energy_free: {
            unsupported: "Uncertainty relations do not provide an accumulable macroscopic energy source."
          },
          all_pairs: {
            unsupported: "The specific relation depends on the observables and their commutator."
          }
        }
      },
      references: [references.openStaxQuantum]
    }
  },
  {
    id: "foundation.qm.ground_state.dragfill.001",
    type: "drag_fill",
    track: "Established foundations",
    module: "Quantum basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    promptParts: [
      "For a quantum harmonic oscillator, the ground-state energy is ",
      { type: "blank", id: "energy" },
      " rather than zero."
    ],
    tokens: [
      { id: "half_hbar_omega", content: [{ type: "math", latex: "\\frac{1}{2}\\hbar\\omega", label: "one half hbar omega" }] },
      { id: "hbar_omega", content: [{ type: "math", latex: "\\hbar\\omega", label: "hbar omega" }] },
      { id: "zero", content: [{ type: "math", latex: "0", label: "zero" }] },
      { id: "eight_pi", content: [{ type: "math", latex: "8\\pi G", label: "eight pi G" }] }
    ],
    blanks: [
      { id: "energy", accepts: ["half_hbar_omega"] }
    ],
    explanation: {
      answer: [{ type: "math", latex: "E_0=\\frac{1}{2}\\hbar\\omega", label: "ground energy equals one half hbar omega" }],
      why: "The harmonic oscillator ground state has nonzero energy because the quantum state cannot have both exactly zero displacement spread and zero momentum spread.",
      boundary: "This is elementary quantum mechanics. It motivates zero-point language but does not by itself create an extractable energy reservoir.",
      adaptive: {
        blanks: {
          energy: {
            correct: "The oscillator ground state has energy one half hbar omega.",
            tokens: {
              hbar_omega: "Hbar omega is the energy spacing between adjacent oscillator levels, not the ground-state value.",
              zero: "The quantum oscillator ground state is not zero energy.",
              eight_pi: "Eight pi G belongs to Einstein-equation normalization, not oscillator energy."
            },
            missing: "The blank asks for the oscillator ground-state energy."
          }
        }
      },
      references: [references.openStaxQuantum]
    }
  },
  {
    id: "foundation.qm.superposition.matching.001",
    type: "matching",
    track: "Established foundations",
    module: "Quantum basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Match each quantum term to the careful interpretation.",
    prompts: [
      { id: "superposition", content: "Superposition" },
      { id: "eigenstate", content: "Eigenstate of an observable" },
      { id: "measurement", content: "Measurement outcome" }
    ],
    options: [
      { id: "linear_combo", label: "A state expressed as a linear combination of basis states" },
      { id: "definite_value", label: "A state with a definite value for the chosen observable" },
      { id: "sampled_result", label: "A result sampled according to the state's probabilities" }
    ],
    answer: {
      superposition: "linear_combo",
      eigenstate: "definite_value",
      measurement: "sampled_result"
    },
    explanation: {
      answer: "Superposition, eigenstate, and measurement outcome are different roles.",
      why: "A state can be written as a combination in one basis, can be definite for a chosen observable, and can still produce individual sampled outcomes according to probabilities.",
      boundary: "This is basic quantum-state language and does not settle field-theory vacuum, source, or gravity questions.",
      adaptive: {
        matches: {
          superposition: {
            correct: "Superposition means a linear combination of basis states.",
            options: {
              definite_value: "An eigenstate is definite for the chosen observable.",
              sampled_result: "A measurement outcome is sampled; it is not the definition of superposition."
            }
          },
          eigenstate: {
            correct: "An eigenstate has a definite value for the chosen observable.",
            options: {
              linear_combo: "A superposition is a linear-combination description.",
              sampled_result: "The sampled result is the measurement event, not the state role."
            }
          },
          measurement: {
            correct: "A measurement outcome is sampled according to the state's probabilities.",
            options: {
              linear_combo: "A linear combination describes state representation, not the event outcome itself.",
              definite_value: "Definite value is the eigenstate relation for one observable."
            }
          }
        }
      },
      references: [references.openStaxQuantum]
    }
  },
  {
    id: "foundation.qft.field_quantization.001",
    type: "mc",
    track: "Established foundations",
    module: "QFT basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In basic quantum field theory, what is the usual meaning of a particle excitation?",
    choices: [
      { id: "field_mode", content: "An excitation of an underlying quantum field mode." },
      { id: "tiny_ball", content: "A small classical ball moving through an otherwise empty stage." },
      { id: "metric", content: "A choice of spacetime metric." },
      { id: "brane", content: "A compactified extra dimension." }
    ],
    answer: ["field_mode"],
    explanation: {
      answer: "A particle is treated as an excitation of a quantum field.",
      why: "QFT shifts the basic object from individual classical particles to fields whose modes can be excited. This matters for vacuum language because the vacuum is a field state, not a literal empty container.",
      boundary: "This is established QFT vocabulary and does not by itself provide a source mechanism for a spacetime geometry.",
      adaptive: {
        choices: {
          field_mode: {
            supported: "The field-mode excitation is the standard QFT interpretation."
          },
          tiny_ball: {
            unsupported: "QFT particles are not fundamental little classical balls in empty space."
          },
          metric: {
            unsupported: "A metric is geometric structure, not a particle excitation."
          },
          brane: {
            unsupported: "A brane is a string-theory object, not the basic QFT meaning of particle excitation."
          }
        }
      },
      references: [references.tongQft]
    }
  },
  {
    id: "foundation.qft.vacuum_modes.001",
    type: "multi",
    track: "Established foundations",
    module: "QFT basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements about the quantum-field vacuum are careful?",
    choices: [
      { id: "state", content: "It is a state of the field, not simply classical nothingness." },
      { id: "mode_dependent", content: "Its description can depend on the field, boundary conditions, and background setup." },
      { id: "renormalization", content: "Physical predictions often depend on differences or renormalized quantities rather than a naive infinite sum." },
      { id: "battery", content: "A regulated zero-point sum gives a direct estimate of vacuum energy available to a device." },
      { id: "unique_everywhere", content: "Once a mode basis is chosen, vacuum ambiguity is only a mathematical convention." }
    ],
    answer: ["state", "mode_dependent", "renormalization"],
    explanation: {
      answer: "The vacuum is a field state whose physical use depends on setup and renormalized observables.",
      why: "Vacuum language in QFT is subtle because mode structure, boundary conditions, and background geometry can matter. Naive zero-point sums are not automatically physical energy reservoirs.",
      boundary: "This is established QFT framing and should not be promoted into an extractable-energy or source-realization claim.",
      adaptive: {
        choices: {
          state: {
            supported: "The vacuum is a quantum state, not classical emptiness."
          },
          mode_dependent: {
            supported: "Field content, boundaries, and background setup can affect vacuum descriptions."
          },
          renormalization: {
            supported: "Observable quantities often involve differences or renormalized stress-energy."
          },
          battery: {
            unsupported: "A regulated sum is not by itself an extractable device energy; observables, boundaries, and dynamics still matter."
          },
          unique_everywhere: {
            unsupported: "Mode choices can encode real physical assumptions, especially in curved or time-dependent settings."
          }
        }
      },
      references: [references.tongQft]
    }
  },
  {
    id: "foundation.qft.renormalization_boundary.001",
    type: "multi",
    track: "Established foundations",
    module: "QFT basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements describe a careful role for renormalization in field theory?",
    choices: [
      { id: "finite_prediction", content: "It helps define finite physical predictions from quantities that can be formally divergent." },
      { id: "parameters", content: "It relates measured parameters to the scale and scheme used in the calculation." },
      { id: "not_magic", content: "It is not a license to assign any desired stress-energy to a model." },
      { id: "delete_physics", content: "It absorbs high-energy sensitivity into measured parameters so low-energy source claims need no further validity discussion." },
      { id: "source_done", content: "Once a stress tensor is renormalized, a physical source model has been constructed." }
    ],
    answer: ["finite_prediction", "parameters", "not_magic"],
    explanation: {
      answer: "Renormalization supports finite predictions and scale-aware parameter interpretation, but it is not arbitrary source construction.",
      why: "Renormalization is a disciplined framework for handling divergences and relating calculations to measured quantities. It does not erase validity limits or produce a matter sector on demand.",
      boundary: "This is QFT calculation discipline and remains distinct from source realization in a gravitational model.",
      adaptive: {
        choices: {
          finite_prediction: {
            supported: "Renormalization is used to extract finite physical predictions from divergent formal expressions."
          },
          parameters: {
            supported: "Measured parameters and calculation scale are part of the interpretation."
          },
          not_magic: {
            supported: "Renormalization is constrained, not arbitrary stress-energy assignment."
          },
          delete_physics: {
            unsupported: "Measured parameters help, but validity range and residual scale sensitivity still have to be tracked."
          },
          source_done: {
            unsupported: "A renormalized stress tensor is not automatically a constructed physical source model."
          }
        }
      },
      references: [references.tongQft, references.burgessEft]
    }
  },
  {
    id: "foundation.quantum_vacuum.zero_point.001",
    type: "mc",
    track: "Established foundations",
    module: "Quantum vacuum",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What does zero-point energy mean in quantum theory?",
    choices: [
      { id: "ground", content: "A nonzero ground-state energy associated with quantized modes." },
      { id: "free", content: "Energy that can be freely extracted because it is present in empty space." },
      { id: "classical", content: "The classical rest energy of a particle." },
      { id: "curvature", content: "The curvature required by Einstein's equation." }
    ],
    answer: ["ground"],
    explanation: {
      answer: "Zero-point energy is ground-state mode energy.",
      why: "Quantized systems can have nonzero ground-state energy. That fact is not the same as a technology for extracting arbitrary energy from the vacuum.",
      boundary: "This is quantum foundation vocabulary and must be kept separate from source-option claims.",
      adaptive: {
        choices: {
          ground: {
            supported: "Zero-point energy refers to nonzero ground-state energy in a quantized system."
          },
          free: {
            unsupported: "Nonzero ground-state energy is not a freely extractable reservoir."
          },
          classical: {
            unsupported: "Classical rest energy and quantum zero-point energy are different concepts."
          },
          curvature: {
            unsupported: "Curvature-source relations belong to gravitational field equations, not the definition of zero-point energy."
          }
        }
      },
      references: [references.openStaxQuantum, references.tongQft]
    }
  },
  {
    id: "foundation.quantum_vacuum.not_free_energy.002",
    type: "multi",
    track: "Established foundations",
    module: "Quantum vacuum",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which cautions apply when someone says vacuum fluctuations are a usable source of macroscopic energy?",
    choices: [
      { id: "state_not_battery", content: "A vacuum state is not automatically a battery-like energy reservoir." },
      { id: "observable_differences", content: "Physical effects often involve differences, boundary conditions, or renormalized quantities." },
      { id: "thermo", content: "Extraction claims still need ordinary energy accounting and dynamics." },
      { id: "more_modes", content: "Adding more field modes generally gives more extractable energy." },
      { id: "negative_easy", content: "Vacuum fluctuations make negative energy easy to sustain macroscopically." }
    ],
    answer: ["state_not_battery", "observable_differences", "thermo"],
    explanation: {
      answer: "Vacuum fluctuation language needs state, observable, and energy-accounting discipline.",
      why: "Vacuum effects can be real without becoming a macroscopic source technology. The physical claim has to identify the state, boundary setup, observable quantity, and extraction dynamics.",
      boundary: "This is established quantum-field caution and does not deny real vacuum effects such as Casimir forces.",
      adaptive: {
        choices: {
          state_not_battery: {
            supported: "A quantum vacuum state is not automatically a usable reservoir."
          },
          observable_differences: {
            supported: "Vacuum effects are usually interpreted through physical differences or renormalized observables."
          },
          thermo: {
            supported: "Energy extraction still needs a dynamical mechanism and accounting."
          },
          more_modes: {
            unsupported: "More formal modes do not directly mean more extractable energy."
          },
          negative_easy: {
            unsupported: "Vacuum effects can include negative-energy features, but sustained macroscopic use remains constrained."
          }
        }
      },
      references: [references.tongQft, references.miltonCasimir]
    }
  },
  {
    id: "foundation.casimir.boundary_modes.001",
    type: "mc",
    track: "Established foundations",
    module: "Casimir effect",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What is the Casimir effect most directly associated with?",
    choices: [
      { id: "boundary_modes", content: "Forces or energy differences caused by boundary-conditioned quantum field modes." },
      { id: "free_energy", content: "Unrestricted extraction of zero-point energy from empty space." },
      { id: "wormhole", content: "A proof that traversable wormholes have ordinary matter sources." },
      { id: "adm", content: "The Hamiltonian constraint in the ADM split." }
    ],
    answer: ["boundary_modes"],
    explanation: {
      answer: "The Casimir effect comes from boundary-conditioned quantum field modes.",
      why: "The classic setup compares vacuum mode structure under different boundary conditions, leading to measurable force or energy differences. It is not a general zero-point-energy extraction method.",
      boundary: "This is established quantum-field physics and should be separated from speculative macroscopic source claims.",
      adaptive: {
        choices: {
          boundary_modes: {
            supported: "Boundary-conditioned modes are the direct Casimir-effect idea."
          },
          free_energy: {
            unsupported: "The effect is not unrestricted zero-point-energy extraction."
          },
          wormhole: {
            unsupported: "Casimir systems do not prove ordinary matter can support traversable wormholes."
          },
          adm: {
            unsupported: "ADM constraints are GR initial-data equations, not Casimir physics."
          }
        }
      },
      references: [references.miltonCasimir, references.tongQft]
    }
  },
  {
    id: "foundation.casimir.interpretation.002",
    type: "multi",
    track: "Established foundations",
    module: "Casimir effect",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which interpretations of the Casimir effect are careful?",
    choices: [
      { id: "real_effect", content: "It is a real quantum-field effect with measurable force behavior." },
      { id: "setup_specific", content: "Its sign and magnitude depend on geometry, materials, and boundary conditions." },
      { id: "not_source_clearance", content: "It does not by itself clear macroscopic exotic-source requirements." },
      { id: "vacuum_tank", content: "It shows boundary motion can mine zero-point energy once a device cycle is engineered." },
      { id: "geometry_independent", content: "The effect is mostly geometry-independent once conductors are present." }
    ],
    answer: ["real_effect", "setup_specific", "not_source_clearance"],
    explanation: {
      answer: "Casimir forces are real and setup-dependent, but they do not automatically solve source requirements.",
      why: "The effect depends on boundary conditions, geometry, and material response. Its existence teaches caution about vacuum fields, not a blanket path to macroscopic exotic matter.",
      boundary: "This is established Casimir-effect interpretation and remains distinct from engineering-scale source realization.",
      adaptive: {
        choices: {
          real_effect: {
            supported: "Casimir forces are experimentally and theoretically real quantum-field effects."
          },
          setup_specific: {
            supported: "Geometry, boundaries, and material response affect the result."
          },
          not_source_clearance: {
            supported: "A real effect is not the same as clearing macroscopic exotic-source requirements."
          },
          vacuum_tank: {
            unsupported: "Casimir forces are real, but a device cycle still needs energy accounting and does not simply mine a vacuum reservoir."
          },
          geometry_independent: {
            unsupported: "The effect is strongly tied to setup and geometry."
          }
        }
      },
      references: [references.miltonCasimir]
    }
  },
  {
    id: "foundation.casimir.energy_conditions.003",
    type: "mc",
    track: "Established foundations",
    module: "Casimir effect",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "A design note points to negative energy density between idealized Casimir plates and claims that macroscopic exotic stress is therefore available. What is the careful response?",
    choices: [
      { id: "bounded_setup", content: "Casimir negative energy is setup-specific and does not by itself supply a scalable, controllable stress-energy source." },
      { id: "scale_up", content: "Smaller separations can raise the magnitude enough if material limits are engineered around the target stress." },
      { id: "ignore_materials", content: "Ideal boundary calculations can define the source target first, with material and geometry corrections added afterward." },
      { id: "all_negative", content: "The sign of local energy density is the main gravitational-source feature once the region is static." }
    ],
    answer: ["bounded_setup"],
    explanation: {
      answer: "Casimir negative energy is real but setup-specific and not a scalable source clearance.",
      why: "The gravitational source question concerns the full stress tensor, geometry, material limits, and control of the effect. A local negative-energy feature in an idealized setup does not become arbitrary macroscopic exotic stress.",
      boundary: "This is established quantum-field source caution, not a dismissal of the Casimir effect itself.",
      adaptive: {
        choices: {
          bounded_setup: {
            supported: "This keeps the real effect attached to setup, scale, materials, and stress-tensor context."
          },
          scale_up: {
            unsupported: "Changing separation runs into material, geometry, and full-stress constraints; magnitude alone is not the source claim."
          },
          ignore_materials: {
            unsupported: "Ideal boundaries are useful targets, but material and geometry limits are part of the physical source claim."
          },
          all_negative: {
            unsupported: "Local sign is not enough; the full stress tensor, geometry, and scale matter gravitationally."
          }
        }
      },
      references: [references.miltonCasimir, references.energyConditionsPrimer]
    }
  },
  {
    id: "foundation.semiclassical.rset.001",
    type: "mc",
    track: "Established foundations",
    module: "Semiclassical gravity",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In semiclassical gravity, what role does the renormalized stress-energy expectation value usually play?",
    choices: [
      { id: "source_expectation", content: "It is used as the quantum-field source side for a classical spacetime equation." },
      { id: "particle_path", content: "It gives the definite trajectory of one particle." },
      { id: "gauge_choice", content: "It chooses the ADM lapse and shift." },
      { id: "brane_count", content: "It counts compactified branes." }
    ],
    answer: ["source_expectation"],
    explanation: {
      answer: "The RSET is the quantum expectation value used as a semiclassical source.",
      why: "Semiclassical gravity commonly couples a classical geometry to a renormalized expectation value of the quantum stress-energy tensor. This is different from a classical matter tensor chosen by hand.",
      boundary: "This is semiclassical-gravity vocabulary and does not establish that a proposed geometry has a controlled quantum source.",
      adaptive: {
        choices: {
          source_expectation: {
            supported: "The renormalized expectation value supplies the source term in semiclassical treatments."
          },
          particle_path: {
            unsupported: "A stress-energy expectation value is not a single-particle trajectory."
          },
          gauge_choice: {
            unsupported: "Gauge choices such as lapse and shift are separate from the RSET."
          },
          brane_count: {
            unsupported: "Brane counting is string-theory context, not the RSET role."
          }
        }
      },
      references: [references.tongQft, references.chronologyProtection]
    }
  },
  {
    id: "foundation.semiclassical.backreaction.002",
    type: "multi",
    track: "Established foundations",
    module: "Semiclassical gravity",
    difficulty: "intermediate",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which cautions apply when a model uses quantum fields on a fixed background?",
    choices: [
      { id: "fixed_background", content: "The calculation may be informative while still neglecting geometry response." },
      { id: "rset_needed", content: "Backreaction review asks how the field stress-energy expectation affects the geometry." },
      { id: "state_choice", content: "The quantum state and boundary setup matter for the stress-energy being evaluated." },
      { id: "geometry_finished", content: "If the computed stress is small on the chosen background, the fixed-background treatment is enough for source interpretation." },
      { id: "classical_source", content: "A renormalized expectation value can be read as an effective classical source without specifying the field state further." }
    ],
    answer: ["fixed_background", "rset_needed", "state_choice"],
    explanation: {
      answer: "Fixed-background calculations are useful but leave backreaction, state choice, and source interpretation to review.",
      why: "Solving fields on a prescribed geometry can reveal important effects, but self-consistency requires asking whether the field stress changes the geometry and whether the state is physically appropriate.",
      boundary: "This is semiclassical-gravity discipline and should not be treated as automatic physical realization.",
      adaptive: {
        choices: {
          fixed_background: {
            supported: "A fixed-background result can be valuable while still omitting geometry response."
          },
          rset_needed: {
            supported: "Backreaction is about how the stress-energy expectation affects the geometry."
          },
          state_choice: {
            supported: "State and boundary setup can change the stress tensor being evaluated."
          },
          geometry_finished: {
            unsupported: "Small stress can support an approximation, but source interpretation still needs the state, regime, and backreaction assumptions."
          },
          classical_source: {
            unsupported: "A renormalized expectation is source-side data, but the state and quantum origin remain part of the interpretation."
          }
        }
      },
      references: [references.chronologyProtection, references.tongQft]
    }
  },
  {
    id: "foundation.eft.validity.001",
    type: "mc",
    track: "Established foundations",
    module: "Effective field theory",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What is the central discipline of effective field theory?",
    choices: [
      { id: "scale", content: "Describe physics within a stated range of energies or length scales." },
      { id: "everything", content: "Replace the need for a more complete high-energy theory." },
      { id: "geometry", content: "Choose the spacetime metric with the smallest curvature." },
      { id: "vacuum", content: "Extract zero-point energy from all field modes." }
    ],
    answer: ["scale"],
    explanation: {
      answer: "EFT is scale-bound theory building.",
      why: "An effective field theory can make reliable predictions inside its domain without claiming to be the final theory at every energy or length scale.",
      boundary: "This is general theory discipline and does not guarantee a UV completion or source realization.",
      adaptive: {
        choices: {
          scale: {
            supported: "EFT keeps validity domains and scale separation explicit."
          },
          everything: {
            unsupported: "An EFT can be powerful without replacing the need for a high-energy completion."
          },
          geometry: {
            unsupported: "Metric choice is a different modeling decision."
          },
          vacuum: {
            unsupported: "EFT is not a vacuum-energy extraction rule."
          }
        }
      },
      references: [references.burgessEft]
    }
  },
  {
    id: "foundation.eft.scale_matching.002",
    type: "multi",
    track: "Established foundations",
    module: "Effective field theory",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements are careful when applying an effective source model?",
    choices: [
      { id: "validity", content: "State the energy, length, and field-strength regime where the model is intended to hold." },
      { id: "operators", content: "Track which neglected operators or corrections could become important." },
      { id: "matching", content: "Identify how effective parameters are matched to measurements or a deeper model." },
      { id: "uv_done", content: "A successful low-energy fit makes the high-energy completion irrelevant for claims inside the fitted regime." },
      { id: "arbitrary_stress", content: "Enough allowed operators can fit the desired stress tensor while staying within EFT if the coefficients are measured." }
    ],
    answer: ["validity", "operators", "matching"],
    explanation: {
      answer: "Effective source claims should carry validity range, neglected corrections, and parameter matching.",
      why: "EFT strength comes from controlled approximation, not unrestricted fitting. A model that works at one scale can fail when neglected operators or high-energy physics becomes relevant.",
      boundary: "This is established EFT reasoning and does not by itself validate a proposed exotic source sector.",
      adaptive: {
        choices: {
          validity: {
            supported: "The regime of validity is part of the effective claim."
          },
          operators: {
            supported: "Neglected corrections can become important outside the intended regime."
          },
          matching: {
            supported: "Effective parameters need matching to data or to a deeper model."
          },
          uv_done: {
            unsupported: "Low-energy success can be enough for some predictions, but source claims still need validity and completion limits stated."
          },
          arbitrary_stress: {
            unsupported: "Measured coefficients help, but arbitrary stress fitting still faces consistency, stability, and validity constraints."
          }
        }
      },
      references: [references.burgessEft]
    }
  },
  {
    id: "foundation.eft.sequence.003",
    type: "sequence",
    track: "Established foundations",
    module: "Effective field theory",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Order a conservative EFT-style modeling claim.",
    items: [
      { id: "scales", content: "Identify the relevant low-energy or long-distance scales" },
      { id: "degrees", content: "Choose the active degrees of freedom" },
      { id: "operators", content: "Write allowed terms organized by importance" },
      { id: "match", content: "Match coefficients to data or a deeper calculation" },
      { id: "limits", content: "State the validity limits of the resulting model" }
    ],
    answer: ["scales", "degrees", "operators", "match", "limits"],
    explanation: {
      answer: "Scales, degrees of freedom, operator organization, matching, then validity limits.",
      why: "EFT reasoning starts by deciding which physics is active at the scale of interest. Coefficients and limits then keep the approximation from being overpromoted.",
      boundary: "This is general EFT practice, not evidence that any particular source option is physically realized.",
      adaptive: {
        sequence: [
          {
            id: "scales-before-degrees",
            before: "scales",
            after: "degrees",
            content: "The relevant scale guides which degrees of freedom should be active."
          },
          {
            id: "degrees-before-operators",
            before: "degrees",
            after: "operators",
            content: "Operators are written for the chosen degrees of freedom and symmetries."
          },
          {
            id: "operators-before-match",
            before: "operators",
            after: "match",
            content: "Coefficients are matched after the possible terms are organized."
          },
          {
            id: "match-before-limits",
            before: "match",
            after: "limits",
            content: "The final claim should state the limits of the matched effective model."
          }
        ]
      },
      references: [references.burgessEft]
    }
  },
  {
    id: "foundation.source.scalar_field.001",
    type: "mc",
    track: "Established foundations",
    module: "Source model basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why is naming a scalar field not enough to specify a physical source model?",
    choices: [
      { id: "dynamics", content: "The action, coupling, potential, state, stability, and regime still have to be specified." },
      { id: "tensor", content: "A scalar field's stress-energy is fixed once its field profile is named." },
      { id: "ordinary", content: "A minimally coupled scalar field is usually enough to keep source behavior ordinary." },
      { id: "geometry_only", content: "A scalar ansatz can determine the geometry after the desired energy density is matched." }
    ],
    answer: ["dynamics"],
    explanation: {
      answer: "A field label is not a full model.",
      why: "The stress-energy and physical behavior depend on the scalar action, couplings, potential, state, boundary conditions, and stability. The same field type can appear in different physical regimes.",
      boundary: "This is general source-model literacy and does not approve or reject any specific scalar-source proposal.",
      adaptive: {
        choices: {
          dynamics: {
            supported: "A physical field model needs dynamics, couplings, state, and regime information."
          },
          tensor: {
            unsupported: "The stress-energy depends on dynamics, couplings, potential, and state, not only the field profile label."
          },
          ordinary: {
            unsupported: "Scalar-field behavior depends on coupling and regime; the field label alone is not an ordinary-matter guarantee."
          },
          geometry_only: {
            unsupported: "Energy-density matching alone does not determine the full geometry or source dynamics."
          }
        }
      },
      references: [references.barceloVisser, references.burgessEft]
    }
  },
  {
    id: "foundation.source.equation_of_state.001",
    type: "matching",
    track: "Established foundations",
    module: "Source model basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Match each source-model term to the careful role it usually plays.",
    prompts: [
      { id: "equation_state", content: "Equation of state" },
      { id: "anisotropic_stress", content: "Anisotropic stress" },
      { id: "stability", content: "Stability analysis" }
    ],
    options: [
      { id: "pressure_density", label: "Relates pressure-like quantities to density or other state variables" },
      { id: "directional", label: "Allows stress behavior to differ by spatial direction" },
      { id: "perturb_response", label: "Checks response to disturbances around a background" }
    ],
    answer: {
      equation_state: "pressure_density",
      anisotropic_stress: "directional",
      stability: "perturb_response"
    },
    explanation: {
      answer: "Equation of state, anisotropic stress, and stability test different source-model surfaces.",
      why: "A source model is more than a density value. Pressure relations, directional stresses, and perturbation behavior all affect whether the model is physically meaningful.",
      boundary: "This is general source-model vocabulary, not a claim that any candidate matter sector has been found.",
      adaptive: {
        matches: {
          equation_state: {
            correct: "An equation of state relates pressure-like quantities to density or other state variables.",
            options: {
              directional: "Directional stress behavior is anisotropy.",
              perturb_response: "Perturbation response is stability analysis."
            }
          },
          anisotropic_stress: {
            correct: "Anisotropic stress means stress differs by direction.",
            options: {
              pressure_density: "Pressure-density relation is the equation-of-state role.",
              perturb_response: "Perturbation response is stability analysis."
            }
          },
          stability: {
            correct: "Stability analysis checks disturbance response.",
            options: {
              pressure_density: "Pressure-density relation is not by itself a perturbation check.",
              directional: "Directional stress is anisotropy, not the stability test itself."
            }
          }
        }
      },
      references: [references.carrollGrNotes, references.energyConditionsPrimer]
    }
  },
  {
    id: "foundation.source.stability.002",
    type: "multi",
    track: "Established foundations",
    module: "Source model basics",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A proposed effective source matches the required stress tensor at one background configuration but has no perturbation study, no equation of state, and no coupling description. Which cautions are justified?",
    choices: [
      { id: "matching_not_model", content: "Algebraic matching to one background is not a complete physical source model." },
      { id: "stability_missing", content: "Perturbative stability and response to disturbances remain open." },
      { id: "dynamics_missing", content: "Dynamics and couplings are needed to know whether the source can sustain the configuration." },
      { id: "eos_missing", content: "An equation-of-state or constitutive relation may be needed to interpret pressure and stress behavior." },
      { id: "match_enough", content: "A stress-tensor match is enough if the geometry is the intended target." },
      { id: "pressure_secondary", content: "Pressure details can be postponed if the energy density component is matched well." }
    ],
    answer: ["matching_not_model", "stability_missing", "dynamics_missing", "eos_missing"],
    explanation: {
      answer: "A single stress match is useful but incomplete without dynamics, stability, couplings, and constitutive behavior.",
      why: "Physical source realization requires more than reproducing tensor components at one background point or configuration. The model must explain how the source behaves, responds, and remains consistent.",
      boundary: "This is general source-realization discipline and does not depend on any project-specific ledger language.",
      adaptive: {
        choices: {
          matching_not_model: {
            supported: "A background match is an accounting success, not a full matter model."
          },
          stability_missing: {
            supported: "Perturbation response remains an independent burden."
          },
          dynamics_missing: {
            supported: "Couplings and equations of motion are needed for source behavior."
          },
          eos_missing: {
            supported: "Constitutive or equation-of-state information helps interpret stresses."
          },
          match_enough: {
            unsupported: "Target matching does not by itself show a source can physically sustain the target."
          },
          pressure_secondary: {
            unsupported: "Pressure and stress details are part of the source and energy-condition story."
          }
        }
      },
      references: [references.energyConditionsPrimer, references.burgessEft]
    }
  },
  {
    id: "foundation.string.brane_basic.001",
    type: "mc",
    track: "Established foundations",
    module: "String theory context",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "In string-theory language, what is a D-brane?",
    choices: [
      { id: "boundary", content: "An object on which open strings can end, carrying worldvolume degrees of freedom." },
      { id: "warp_engine", content: "A macroscopic propulsion source for arbitrary spacetime metrics." },
      { id: "observer", content: "A timelike observer used to measure local energy density." },
      { id: "constraint", content: "The Hamiltonian constraint in a 3+1 split." }
    ],
    answer: ["boundary"],
    explanation: {
      answer: "A D-brane is an object where open strings can end.",
      why: "D-branes carry worldvolume degrees of freedom and source/coupling roles inside string theory. That background does not make them practical macroscopic source devices.",
      boundary: "This is string-theory literacy, not an endorsement of branes as deployable source options.",
      adaptive: {
        choices: {
          boundary: {
            supported: "Open-string boundary conditions are central to the D-brane concept."
          },
          warp_engine: {
            unsupported: "D-branes are theoretical objects, not macroscopic propulsion sources by definition."
          },
          observer: {
            unsupported: "A timelike observer is GR measurement vocabulary, not a D-brane."
          },
          constraint: {
            unsupported: "ADM constraints are unrelated to the definition of D-brane."
          }
        }
      },
      references: [references.polchinskiDBranes]
    }
  },
  {
    id: "foundation.string.compactification.001",
    type: "mc",
    track: "Established foundations",
    module: "String theory context",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What is compactification meant to do in string-theory model building?",
    choices: [
      { id: "extra_dimensions", content: "Relate higher-dimensional theory to lower-dimensional effective physics by specifying small or hidden dimensions." },
      { id: "energy_source", content: "Package flux or vacuum energy into a lower-dimensional source term." },
      { id: "metric_free", content: "Summarize compact geometry by effective parameters so the detailed shape is secondary." },
      { id: "stability_done", content: "Make moduli stabilization a later correction once the compact dimensions are small." }
    ],
    answer: ["extra_dimensions"],
    explanation: {
      answer: "Compactification connects higher-dimensional theory to lower-dimensional effective physics.",
      why: "The shape, size, fluxes, and moduli of compact dimensions affect the low-energy effective theory. Stabilization and consistency are substantive problems, not automatic consequences.",
      boundary: "This is high-energy theory background and should not be treated as a direct source option.",
      adaptive: {
        choices: {
          extra_dimensions: {
            supported: "Compactification specifies how extra dimensions feed into lower-dimensional effective physics."
          },
          energy_source: {
            unsupported: "Flux or vacuum contributions require a consistent compactification and effective description; they are not simply usable local source terms."
          },
          metric_free: {
            unsupported: "Effective parameters summarize geometry only after assumptions are made; detailed compact geometry still matters."
          },
          stability_done: {
            unsupported: "Small compact dimensions do not make moduli stabilization a later cosmetic correction."
          }
        }
      },
      references: [references.douglasKachruFlux]
    }
  },
  {
    id: "foundation.string.effective_claims.002",
    type: "multi",
    track: "Established foundations",
    module: "String theory context",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A source proposal invokes branes, fluxes, and compactification but gives only a four-dimensional effective stress tensor. Which cautions are justified?",
    choices: [
      { id: "effective_scope", content: "The four-dimensional tensor should be treated as an effective description with stated validity limits." },
      { id: "moduli", content: "Compactification data and moduli stabilization can affect whether the setup is consistent." },
      { id: "couplings", content: "Couplings, scales, and backreaction need to be specified before the source claim is physical." },
      { id: "not_magic", content: "String-theory vocabulary does not by itself supply a macroscopic controllable source." },
      { id: "label_enough", content: "Naming branes and fluxes gives enough high-energy structure to trust the effective tensor." },
      { id: "four_d_complete", content: "A four-dimensional stress tensor makes the higher-dimensional construction optional once it matches the desired geometry." }
    ],
    answer: ["effective_scope", "moduli", "couplings", "not_magic"],
    explanation: {
      answer: "High-energy vocabulary must remain tied to effective scope, compactification consistency, couplings, scales, and backreaction.",
      why: "String-theory ingredients can be meaningful source context, but a physical claim needs the mechanism and validity domain. A four-dimensional effective tensor does not erase the higher-dimensional assumptions that produced it.",
      boundary: "This is bounded string-theory and EFT literacy, not a claim that string theory supplies an active source sector.",
      adaptive: {
        choices: {
          effective_scope: {
            supported: "The effective tensor should carry its domain of validity."
          },
          moduli: {
            supported: "Compactification and moduli behavior are part of the consistency story."
          },
          couplings: {
            supported: "Couplings, scales, and backreaction determine whether the source claim is physical."
          },
          not_magic: {
            supported: "Terminology alone does not make a controllable macroscopic source."
          },
          label_enough: {
            unsupported: "Brane and flux labels need concrete dynamics, scales, and consistency conditions."
          },
          four_d_complete: {
            unsupported: "The effective tensor depends on higher-dimensional assumptions rather than replacing them."
          }
        }
      },
      references: [references.polchinskiDBranes, references.douglasKachruFlux, references.burgessEft]
    }
  },
  {
    id: "foundation.cross_domain.classification.001",
    type: "claim_classification",
    track: "Established foundations",
    module: "Claim classification",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Classify each broad foundation statement by its safest status.",
    statuses: ["established_theory", "established_constraint", "literature_model", "open_gate"],
    statements: [
      { id: "observable", content: "Quantum observables are represented by operators.", answer: "established_theory" },
      { id: "casimir", content: "Casimir systems show setup-dependent vacuum forces, not unrestricted vacuum-energy extraction.", answer: "established_constraint" },
      { id: "alcubierre", content: "The Alcubierre metric is a published speculative spacetime model.", answer: "literature_model" },
      { id: "source", content: "A complete physical source sector for an arbitrary exotic metric has been demonstrated.", answer: "open_gate" }
    ],
    explanation: {
      answer: "The statements separate general theory, constraint caution, published model status, and unresolved source realization.",
      why: "Broad foundations mix stable theory, limiting principles, paper-specific models, and open physical gates. Classification prevents a real effect or model from being promoted into source realization.",
      boundary: "This is general claim-boundary training across foundation domains, not project-state content.",
      adaptive: {
        classifications: {
          observable: {
            correct: "Quantum-observable operator language is established quantum theory.",
            statuses: {
              established_constraint: "This is not a limiting theorem or no-go pressure.",
              literature_model: "It is broader than a single speculative model.",
              open_gate: "The observable formalism itself is not unresolved."
            }
          },
          casimir: {
            correct: "The statement is a constraint-style caution about what Casimir physics does and does not support.",
            statuses: {
              established_theory: "The effect is established, but this sentence is about its interpretive limit.",
              literature_model: "This is not a speculative spacetime model.",
              open_gate: "The cautious statement is supported; the open gate would be a scalable source mechanism."
            }
          },
          alcubierre: {
            correct: "The Alcubierre metric is published speculative literature.",
            statuses: {
              established_theory: "The metric is a model within GR, not established transportation physics.",
              established_constraint: "The sentence names model status rather than a constraint theorem.",
              open_gate: "The metric exists as literature; source realization remains an open gate."
            }
          },
          source: {
            correct: "Universal physical source realization for arbitrary exotic metrics remains an open gate.",
            statuses: {
              established_theory: "Established field equations do not supply universal exotic-source realization.",
              established_constraint: "This is a realization claim, not only a constraint.",
              literature_model: "No named literature model demonstrates the universal claim."
            }
          }
        }
      },
      references: [references.openStaxQuantum, references.miltonCasimir, references.alcubierre, references.energyConditionsPrimer]
    }
  },
  {
    id: "foundation.qm.mixed_state.001",
    type: "mc",
    track: "Established foundations",
    module: "Quantum basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What is the main difference between a pure quantum state and a mixed state?",
    choices: [
      { id: "statistical", content: "A mixed state represents statistical uncertainty or ensemble structure beyond a single state vector." },
      { id: "classical", content: "A mixed state can always be interpreted as ordinary ignorance over definite pure states in any basis." },
      { id: "energy", content: "A mixed state should have less usable energy because coherence has been lost." },
      { id: "source", content: "A mixed state is enough to specify the stress-energy once the field operator is known." }
    ],
    answer: ["statistical"],
    explanation: {
      answer: "A mixed state represents ensemble or statistical structure, not just one state vector.",
      why: "Pure and mixed states can give different descriptions of preparation and information. The distinction matters when interpreting expectation values and quantum fields, because averages can reflect state structure as well as measurement statistics.",
      boundary: "This is quantum-state vocabulary and does not by itself identify a gravitational source.",
      adaptive: {
        choices: {
          statistical: {
            supported: "A mixed state captures ensemble or statistical structure beyond one state vector."
          },
          classical: {
            unsupported: "A mixed state is still quantum, and its decomposition into pure states is not basis-independent in that simple way."
          },
          energy: {
            unsupported: "Loss of coherence does not define the energy ordering by itself."
          },
          source: {
            unsupported: "The state contributes to stress-energy expectations, but the operator, renormalization, and setup still matter."
          }
        }
      },
      references: [references.openStaxQuantum]
    }
  },
  {
    id: "foundation.qft.curved_vacuum.002",
    type: "multi",
    track: "Established foundations",
    module: "QFT basics",
    difficulty: "advanced",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "In a curved or time-dependent spacetime, which cautions apply to the phrase vacuum state?",
    choices: [
      { id: "observer_setup", content: "The vacuum notion can depend on observers, modes, boundary conditions, or asymptotic structure." },
      { id: "stress_state", content: "The chosen state affects the renormalized stress-energy expectation value." },
      { id: "not_empty", content: "Vacuum should not be read as classical empty space with no physical consequences." },
      { id: "unique", content: "A single preferred vacuum exists whenever the metric is smooth." },
      { id: "no_backreaction", content: "The vacuum choice is only interpretive and cannot affect backreaction questions." }
    ],
    answer: ["observer_setup", "stress_state", "not_empty"],
    explanation: {
      answer: "Vacuum choice can be setup-dependent and physically relevant through the stress-energy expectation.",
      why: "Curvature, time dependence, and boundary conditions can make the field-state choice nontrivial. The vacuum is a quantum state with possible observable and gravitational consequences, not a universal label for empty space.",
      boundary: "This is QFT-in-curved-spacetime background and should not be used as a source-clearance shortcut.",
      adaptive: {
        choices: {
          observer_setup: {
            supported: "Mode and observer structure can matter in curved or time-dependent settings."
          },
          stress_state: {
            supported: "The state affects the renormalized stress-energy expectation."
          },
          not_empty: {
            supported: "Vacuum is not simply classical nothingness."
          },
          unique: {
            unsupported: "Metric smoothness does not guarantee one preferred vacuum notion."
          },
          no_backreaction: {
            unsupported: "The stress expectation from a state can enter backreaction analysis."
          }
        }
      },
      references: [references.tongQft, references.chronologyProtection]
    }
  },
  {
    id: "foundation.casimir.material_limits.004",
    type: "multi",
    track: "Established foundations",
    module: "Casimir effect",
    difficulty: "advanced",
    claimStatus: "established_constraint",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "A calculation uses ideal perfectly conducting plates to estimate a Casimir stress, then applies it unchanged to a finite material device. Which cautions are justified?",
    choices: [
      { id: "material_response", content: "Real material response can change the effect relative to an ideal boundary calculation." },
      { id: "geometry", content: "Finite geometry and edge effects can matter outside the idealized setup." },
      { id: "scale", content: "Scaling the setup changes both the force scale and the engineering interpretation." },
      { id: "ideal_exact", content: "The ideal-plate result can be used directly if the material is a good conductor over the relevant frequencies." },
      { id: "stress_complete", content: "The attractive force determines the complete stress-energy tensor needed for a gravitational source claim." }
    ],
    answer: ["material_response", "geometry", "scale"],
    explanation: {
      answer: "Material response, finite geometry, and scaling all matter when moving away from ideal Casimir plates.",
      why: "Ideal calculations are valuable reference cases, but physical devices introduce material, frequency, geometry, and scale limits. A force estimate is not the complete stress-energy information needed for a source claim.",
      boundary: "This is Casimir-effect interpretation, not an argument against using ideal models as controlled starting points.",
      adaptive: {
        choices: {
          material_response: {
            supported: "Real materials can change the boundary-conditioned mode behavior."
          },
          geometry: {
            supported: "Finite size and edge effects can alter the idealized result."
          },
          scale: {
            supported: "Scale changes the magnitude and physical interpretation of the force."
          },
          ideal_exact: {
            unsupported: "Good conductivity helps but does not make the ideal result directly exact."
          },
          stress_complete: {
            unsupported: "A force estimate does not specify the full stress-energy tensor."
          }
        }
      },
      references: [references.miltonCasimir]
    }
  },
  {
    id: "foundation.eft.naturalness.004",
    type: "mc",
    track: "Established foundations",
    module: "Effective field theory",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "What does naturalness usually warn about in effective field theory?",
    choices: [
      { id: "sensitivity", content: "Low-energy parameters may be sensitive to high-energy physics or require unexplained tuning." },
      { id: "beauty", content: "Simpler-looking equations are more natural because fewer terms need to be tracked." },
      { id: "source", content: "A technically natural effective source is likely to become physical after adding compatible fields." },
      { id: "coordinate", content: "Small component values in a convenient frame indicate the model is natural." }
    ],
    answer: ["sensitivity"],
    explanation: {
      answer: "Naturalness warns about sensitivity and unexplained tuning.",
      why: "An EFT can be predictive while still raising questions about why its parameters take the values they do. Naturalness is a diagnostic of scale sensitivity, not a proof of failure.",
      boundary: "This is EFT interpretation and should not be used as a standalone verdict on source feasibility.",
      adaptive: {
        choices: {
          sensitivity: {
            supported: "Naturalness concerns sensitivity to high-energy physics and parameter tuning."
          },
          beauty: {
            unsupported: "Visual simplicity is not the technical question; sensitivity to scale and tuning is."
          },
          source: {
            unsupported: "Technical naturalness can help a model, but compatible fields still need dynamics, stability, and evidence."
          },
          coordinate: {
            unsupported: "Coordinate component size is not the same as parameter sensitivity or tuning."
          }
        }
      },
      references: [references.burgessEft]
    }
  },
  {
    id: "foundation.source.energy_condition_eos.003",
    type: "mc",
    track: "Established foundations",
    module: "Source model basics",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why is an energy-condition check not the same thing as an equation of state?",
    choices: [
      { id: "different_roles", content: "An energy condition constrains stress-energy contractions, while an equation of state relates source variables dynamically or constitutively." },
      { id: "same", content: "Both are just names for positivity of energy density." },
      { id: "eos_weaker", content: "An equation of state mainly refines source behavior after the main energy-condition contractions are checked." },
      { id: "ec_source", content: "An energy condition supplies the matter dynamics once the metric is chosen." }
    ],
    answer: ["different_roles"],
    explanation: {
      answer: "Energy conditions and equations of state play different roles.",
      why: "Energy conditions test tensor contractions under specified assumptions. An equation of state or constitutive law says how source variables relate and evolve, which is needed for physical source modeling.",
      boundary: "This is general source-model discipline and does not establish any particular matter sector.",
      adaptive: {
        choices: {
          different_roles: {
            supported: "The statement separates constraint checks from constitutive source modeling."
          },
          same: {
            unsupported: "Energy conditions and equations of state are not merely the same positivity statement."
          },
          eos_weaker: {
            unsupported: "Constitutive behavior is part of the source model, not just a later refinement after contraction checks."
          },
          ec_source: {
            unsupported: "An energy condition does not supply matter dynamics."
          }
        }
      },
      references: [references.energyConditionsPrimer, references.carrollGrNotes]
    }
  },
  {
    id: "foundation.classical_field.em_stress.001",
    type: "mc",
    track: "Established foundations",
    module: "Source model basics",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why can electromagnetic fields act as sources in general relativity?",
    choices: [
      { id: "stress", content: "They carry energy, momentum, and stress that enter the stress-energy tensor." },
      { id: "charge_only", content: "Only electric charge appears in Einstein's equation." },
      { id: "coordinate", content: "They choose the coordinate system for the metric." },
      { id: "vacuum", content: "They remove the need for boundary conditions." }
    ],
    answer: ["stress"],
    explanation: {
      answer: "Electromagnetic fields carry stress-energy.",
      why: "Classical fields can carry energy density, momentum flux, and stresses. In GR those contributions appear through the stress-energy tensor rather than only through particle-like matter.",
      boundary: "This is established field-source vocabulary and not a claim that electromagnetic fields can realize arbitrary exotic stress tensors.",
      adaptive: {
        choices: {
          stress: {
            supported: "Field energy, momentum, and stress are source-side quantities in GR."
          },
          charge_only: {
            unsupported: "Einstein's equation couples to stress-energy, not only charge."
          },
          coordinate: {
            unsupported: "Field sources do not choose coordinates by definition."
          },
          vacuum: {
            unsupported: "Electromagnetic fields still require equations and boundary conditions."
          }
        }
      },
      references: [references.carrollGrNotes]
    }
  },
  {
    id: "foundation.numerical.convergence.001",
    type: "multi",
    track: "Established foundations",
    module: "Modeling discipline",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    scoring: "subtract_incorrect",
    prompt: "Which statements about numerical convergence evidence are careful?",
    choices: [
      { id: "resolution", content: "A result should be checked against resolution or discretization changes when possible." },
      { id: "norms", content: "Residuals and error norms should be tied to the physical claim being made." },
      { id: "not_single", content: "One visually clean run is useful evidence but not a convergence study." },
      { id: "plot_enough", content: "A smooth plot is enough if it matches the expected qualitative behavior." },
      { id: "source_done", content: "Numerical convergence of a diagnostic establishes the physical source model." }
    ],
    answer: ["resolution", "norms", "not_single"],
    explanation: {
      answer: "Convergence evidence needs resolution checks, relevant norms, and more than visual smoothness.",
      why: "Numerical evidence is strongest when the measured error behavior supports the specific claim. Clean plots can be encouraging while still hiding discretization, residual, or channel failures.",
      boundary: "This is general computational-modeling discipline and does not replace physics or source review.",
      adaptive: {
        choices: {
          resolution: {
            supported: "Resolution changes are a standard way to test numerical robustness."
          },
          norms: {
            supported: "The chosen residuals and norms should correspond to the claim."
          },
          not_single: {
            supported: "A single clean run is evidence, but not full convergence evidence."
          },
          plot_enough: {
            unsupported: "Visual smoothness is not a substitute for convergence checks."
          },
          source_done: {
            unsupported: "Converged diagnostics do not construct the physical source model."
          }
        }
      },
      references: [references.burgessEft, references.adm]
    }
  },
  {
    id: "foundation.string.moduli_stabilization.003",
    type: "mc",
    track: "Established foundations",
    module: "String theory context",
    difficulty: "intermediate",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Why does moduli stabilization matter in compactification discussions?",
    choices: [
      { id: "parameters", content: "Unstabilized moduli can change the effective low-energy parameters and geometry." },
      { id: "optional", content: "Moduli can be summarized by fixed parameters once the compact dimensions are below accessible scales." },
      { id: "energy_free", content: "A stabilized compactification can be treated as a controlled reservoir for lower-dimensional vacuum energy." },
      { id: "adm", content: "Moduli stabilization is analogous to constraint preservation because both keep chosen background data fixed." }
    ],
    answer: ["parameters"],
    explanation: {
      answer: "Moduli stabilization matters because moduli affect the effective theory.",
      why: "Compactification data can appear as fields or parameters in the lower-dimensional description. If those quantities are not stabilized, the effective geometry and couplings may not stay fixed.",
      boundary: "This is string-compactification context and does not imply a practical source mechanism.",
      adaptive: {
        choices: {
          parameters: {
            supported: "Unstabilized moduli can change effective parameters and geometry."
          },
          optional: {
            unsupported: "Fixed effective parameters require stabilization assumptions; small size alone does not make moduli irrelevant."
          },
          energy_free: {
            unsupported: "Stabilization can affect vacuum energy, but it does not provide a controlled extractable reservoir by itself."
          },
          adm: {
            unsupported: "Both involve consistency, but ADM constraint preservation and moduli stabilization are different mechanisms."
          }
        }
      },
      references: [references.douglasKachruFlux]
    }
  },
  {
    id: "foundation.thermo.energy_accounting.001",
    type: "mc",
    track: "Established foundations",
    module: "Modeling discipline",
    difficulty: "core",
    claimStatus: "established_constraint",
    contentFlags: [],
    prompt: "Why does ordinary energy accounting still matter when a model uses quantum or vacuum effects?",
    choices: [
      { id: "accounting", content: "The model still needs a mechanism that respects conservation, work, heat, losses, and boundary changes." },
      { id: "quantum_exempt", content: "Quantum effects are exempt from ordinary bookkeeping because measurement changes the state." },
      { id: "vacuum_free", content: "Vacuum fluctuations provide energy without needing a cycle or external work." },
      { id: "geometry_only", content: "A geometric description replaces thermodynamic accounting." }
    ],
    answer: ["accounting"],
    explanation: {
      answer: "Quantum and vacuum effects still require energy accounting.",
      why: "Real quantum effects can exchange energy with apparatus, boundaries, fields, or reservoirs. A source claim must identify the cycle and accounting rather than rely on vocabulary alone.",
      boundary: "This is general physical discipline and does not deny quantum effects or vacuum forces.",
      adaptive: {
        choices: {
          accounting: {
            supported: "Conservation, work, losses, and boundary changes remain part of the physical claim."
          },
          quantum_exempt: {
            unsupported: "Measurement and state change do not exempt a model from energy accounting."
          },
          vacuum_free: {
            unsupported: "Vacuum fluctuations do not provide cycle-free energy by definition."
          },
          geometry_only: {
            unsupported: "Geometry does not replace energy accounting for a physical source claim."
          }
        }
      },
      references: [references.openStaxQuantum, references.miltonCasimir]
    }
  },
  {
    id: "foundation.foundation_domains.matching.001",
    type: "matching",
    track: "Established foundations",
    module: "Claim classification",
    difficulty: "core",
    claimStatus: "established_theory",
    contentFlags: [],
    prompt: "Match each foundation domain to a question it is best suited to answer.",
    prompts: [
      { id: "qm", content: "Quantum mechanics" },
      { id: "eft", content: "Effective field theory" },
      { id: "gr", content: "General relativity" },
      { id: "casimir", content: "Casimir physics" }
    ],
    options: [
      { id: "measurement", label: "How observables and state preparation are represented" },
      { id: "scale", label: "Where an approximate field model is valid" },
      { id: "curvature", label: "How spacetime geometry relates to stress-energy" },
      { id: "boundary_vacuum", label: "How boundaries modify vacuum-mode effects" }
    ],
    answer: {
      qm: "measurement",
      eft: "scale",
      gr: "curvature",
      casimir: "boundary_vacuum"
    },
    explanation: {
      answer: "The domains answer different foundation questions: state/measurement, validity scale, curvature/source relation, and boundary-conditioned vacuum effects.",
      why: "Keeping domains distinct prevents a real idea in one area from being overpromoted in another. A Casimir force, an EFT validity range, and Einstein's equation are all useful, but they answer different questions.",
      boundary: "This is broad foundation organization and does not make any project-specific claim.",
      adaptive: {
        matches: {
          qm: {
            correct: "Quantum mechanics is the foundation for state preparation and observables.",
            options: {
              scale: "Validity scale is the EFT role.",
              curvature: "Curvature and stress-energy belong to GR.",
              boundary_vacuum: "Boundary-conditioned vacuum effects are Casimir physics."
            }
          },
          eft: {
            correct: "EFT tracks validity domains for approximate field models.",
            options: {
              measurement: "State preparation and observables are quantum-mechanics basics.",
              curvature: "Curvature/source relation is GR.",
              boundary_vacuum: "Boundary-conditioned vacuum effects are Casimir physics."
            }
          },
          gr: {
            correct: "GR relates spacetime geometry to stress-energy.",
            options: {
              measurement: "Measurement formalism is quantum-mechanics territory.",
              scale: "Validity domains are EFT discipline.",
              boundary_vacuum: "Boundary-conditioned vacuum effects are Casimir physics."
            }
          },
          casimir: {
            correct: "Casimir physics concerns boundary-conditioned vacuum-mode effects.",
            options: {
              measurement: "Quantum measurement is not the specific Casimir focus.",
              scale: "EFT scale discipline is broader than Casimir physics.",
              curvature: "GR curvature/source relation is a different foundation domain."
            }
          }
        }
      },
      references: [references.openStaxQuantum, references.burgessEft, references.carrollGrNotes, references.miltonCasimir]
    }
  }
];
