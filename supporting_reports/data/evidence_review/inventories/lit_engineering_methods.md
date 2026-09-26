# Adjacent engineering methods: literature survey for the spacetime-engineering textbook

> **Errata (audit 2026-09-26, `../audit_synthesis.md` §5).**
> - V6 (Salari–Knupp 2000): the primary text (`work/pdf/sk.txt` l.2812–2823) reports that of ten planted order-of-accuracy mistakes, the order-of-accuracy criterion caught 10 and the consistency criterion 6; MMS missed the efficiency mistake and all seven formal mistakes (audit §1.6 B2).


Evidence inventory for vetting candidates P01–P19 and N01
(`01_CANDIDATES.md`). Nothing here is book text. Compiled 26 September 2026.

## How the items were checked

Every source below was fetched during this session from a DOI resolver,
Crossref/OpenAlex/Semantic Scholar/Europe PMC metadata, arXiv, OSTI, NASA
(NTRS, standards.nasa.gov, nasa.gov), GAO, ASME, a publisher page, or an open
full text. Content claims come only from text that was read. Status codes:

- **VERIFIED**: bibliographic data confirmed and the quoted content read in the
  fetched text (abstract or full text, as stated).
- **PARTIAL**: bibliographic data confirmed; content is taken from a named
  secondary source that was read, or only a publisher summary was available.
- **UNVERIFIED**: no confirming page could be fetched; the item carries no
  weight in any verdict.

Local copies of the full texts read (PDF and extracted text) are in
`inventory/work/pdf/` (areas 1, 2, 3, 5, 6) and `inventory/work/dd_*`
(area 4). Quotes are verbatim except for ligatures and line breaks.

Each source record gives: (1) citation; (2) practice or method; (3) evidence
or rationale in its own field; (4) bearing on candidates, with the verdict
type (truism / supports / refines / supersedes / contradicts); (5) what
transfers to spacetime engineering and what does not. Two incident
inventories (`incidents_may_june.md`, `incidents_september.md`) are cited by
incident code (I-xx, CE-x, F-x, L-x) where an adjacent field already names
the lesson.

## Principal findings

1. **Verification practice in computational science is more developed than the
   project's.** The rigor hierarchy is explicit: trend tests < code-to-code
   comparison < exact-solution tests < manufactured solutions with an
   observed-order criterion (Salari & Knupp 2000). "Independent kernels" and
   "refinement-stable" verdicts sit on the lower rungs. For prescribed metrics
   the top rung is cheap, because any analytic metric has an analytic Einstein
   tensor.
2. **Metric-first design is the method of manufactured solutions run in
   reverse.** In both, a solution is prescribed and the source term it needs
   is computed; the computation guarantees nothing about the source's
   physical existence. The incidents where "assigning a known tensor always
   succeeds" (CE-3, I-11) are the calibration-versus-validation distinction of
   Oberkampf & Trucano (2002).
3. **Transformation optics is the closest mature analogue of
   demand-first design.** Its twenty-year record gives six transferable lessons
   (area 3 synthesis): spend the design freedom on realizability; "hard" is
   relative to the source technology; every simplification is a new design
   that needs a forward check; physical bounds come before construction;
   realizability constraints belong inside the optimizer; and the analogy is
   kinematic only.
4. **Axiomatic design formalizes the separation of parts and knobs, and
   corrects it.** On the project's own identities, carry, energy density and
   shift-free stress are three requirements on two parameters (shift, lapse),
   which Suh's Theorem 1 makes coupled. Functional zoning splits the lapse into
   separate elements and turns the design into a *decoupled* (triangular) one
   with a required adjustment order. It is *uncoupled* only region by region.
5. **One-change-at-a-time controls are superseded as an attribution method
   across a design space.** Fisher, Box–Hunter–Hunter, Czitrom and Saltelli
   agree; Morris (1991) elementary effects are the natural upgrade of the
   project's matched controls, and the project's ordering interactions
   (shift-before-stretch 525 Type IV points against 0) show the need.
6. **The claim ladder has close relatives with better structure.** Its rungs
   parallel the V&V validation hierarchy and the fusion gain chain
   (Q_fuel → Q_sci → Q_eng → Q_wp). Every rung is analytic or computational, so
   in NASA terms the whole ladder lies at or below TRL 2; Millis's Applied
   Science Readiness Levels are the adjacent field's scale for exactly this
   regime. PCMM and NASA-STD-7009 add what a single ladder lacks: independent
   credibility dimensions and a fixed reporting template.
7. **Several candidates are truisms elsewhere**: stage-gate ordering (P01 2a),
   dimensional normalization (P04), interface control (P10 practice half),
   stakeholder measures (P12), complete force accounting (P09), and
   convergence testing (P16 core). Their domain content survives; their
   slogans earn a sentence each.

---

## Area 1. Verification and validation in computational science

### V1. Roache, *Verification and Validation in Computational Science and Engineering* (1998)

1. P. J. Roache, *Verification and Validation in Computational Science and
   Engineering*, Hermosa Publishers, Albuquerque, 1998; ISBN 0913478083.
   **PARTIAL** (Open Library record; content via V5, V6, which build on it).
2. Separates verification of codes from verification of calculations and
   develops the grid-refinement machinery (V2) and manufactured solutions
   (V5).
3. Rationale as stated by V5: "Verification of Calculations involves error
   estimation, whereas Verification of Codes involves error evaluation, from
   known benchmark solutions."
4. P16 — refines (see V5–V6).
5. Transfers fully; the terminology is field-neutral.

### V2. Roache 1994, the Grid Convergence Index

1. P. J. Roache, "Perspective: A Method for Uniform Reporting of Grid
   Refinement Studies", *J. Fluids Eng.* **116**(3), 405–413 (1994),
   DOI 10.1115/1.2910291. **VERIFIED** (Crossref abstract). Formulas
   **VERIFIED** from NASA Glenn's NPARC tutorial "Examining Spatial (Grid)
   Convergence" (grc.nasa.gov/www/wind/valid/tutorial/spatconv.html), which
   attributes the GCI to Roache (1994).
2. From three grids with ratio r: observed order
   p = ln[(f₃ − f₂)/(f₂ − f₁)]/ln r; Richardson estimate
   f_{h=0} ≈ f₁ + (f₁ − f₂)/(r^p − 1); fine-grid index
   GCI₁₂ = F_s |ε|/(r^p − 1), with ε the relative difference. Safety factor
   "Fs=3.0 for comparisons of two grids and Fs=1.25 for comparisons over three
   or more grids." Asymptotic-range check: GCI₂₃/(r^p GCI₁₂) ≈ 1.
3. Abstract: the GCI gives "an objective asymptotic strategy for quantifying
   grid convergence uncertainty through generalized Richardson Extrapolation
   theory". The ASME Fluids Engineering Division adopted it as a reporting
   standard (V3).
4. P16 (refinement ladders) — **supersedes** "refinement-stable" as a verdict
   with a reported observed order, error band and asymptotic check. P01 2e
   and I-07 (sign boundaries between samples) — refines: the GCI applies to
   smooth scalar outputs.
5. Transfers for smooth functionals: signed extremal null energy, integrated
   deficits, band widths, clock ratios. Counts of sampled points in a sign set
   (for example "3,843 Type IV points") are discontinuous in resolution and
   have no observed order; they need the between-sample methods of V15.
   *(Inference, mine.)*

### V3. Celik et al. 2008, ASME reporting procedure

1. I. B. Celik, U. Ghia, P. J. Roache, C. J. Freitas, et al., "Procedure for
   Estimation and Reporting of Uncertainty Due to Discretization in CFD
   Applications", *J. Fluids Eng.* **130**(7), 078001 (2008),
   DOI 10.1115/1.2960953. **PARTIAL** (Crossref/OpenAlex; abstract only;
   first four authors confirmed by Semantic Scholar, the full author list was
   not confirmed).
2. The journal's mandatory procedure for estimating and reporting
   discretization error with the GCI (V2).
3. Abstract: "specific guidelines for prospective authors for calculation and
   reporting of discretization error estimates in CFD simulations where
   experimental data may or may not be available for comparison."
4. P16 — refines: a journal-level reporting standard exists.
5. Transfers as a reporting template.

### V4. Richardson 1911; Richardson & Gaunt 1927

1. L. F. Richardson, "The approximate arithmetical solution by finite
   differences of physical problems involving differential equations, with an
   application to the stresses in a masonry dam", *Phil. Trans. R. Soc. A*
   **210**, 307–357 (1911), DOI 10.1098/rsta.1911.0009. L. F. Richardson &
   J. A. Gaunt, "The deferred approach to the limit", *Phil. Trans. R. Soc. A*
   **226**, 299–361 (1927), DOI 10.1098/rsta.1927.0008. **PARTIAL**
   (Crossref); the use of Richardson's observation in numerical relativity is
   **VERIFIED** through N1.
2. Extrapolation of a discretized result to zero step size from results at
   several step sizes.
3. The foundation of V2 and of convergence testing in numerical relativity
   (N1, N2).
4. P16 — truism in its basic form.
5. Transfers directly.

### V5. Roache 2002, code verification by manufactured solutions

1. P. J. Roache, "Code Verification by the Method of Manufactured Solutions",
   *J. Fluids Eng.* **124**(1), 4–10 (2002), DOI 10.1115/1.1436090.
   **VERIFIED** (Crossref abstract).
2. Choose an analytic solution, apply the differential operator to obtain the
   source term that makes it exact, run the code with that source, and confirm
   the theoretical order of accuracy under refinement.
3. Abstract: the method "utilizes symbolic manipulation with grid refinement
   studies to produce strong code verifications with well-defined completion
   criteria."
4. P16 — supersedes code-to-code agreement as the verification criterion.
   P02 — see the observation under the area synthesis.
5. Transfers with unusual ease; see the synthesis.

### V6. Salari & Knupp 2000 (Sandia)

1. K. Salari & P. Knupp, *Code Verification by the Method of Manufactured
   Solutions*, Sandia report SAND2000-1444 (June 2000), OSTI 759450,
   DOI 10.2172/759450. **VERIFIED** (full text read).
2. Four dynamic testing approaches (trend, symmetry, comparison, exact
   solution) plus MMS, and four acceptance criteria "in order of increasing
   rigor": expert judgement, percent error, consistency, order of accuracy.
   MMS with the order-of-accuracy criterion is "the most comprehensive and
   rigorous of all code Verification methods." Manufactured coefficient
   functions "should be non-trivial and fully general" so that every term is
   exercised. Code verification precedes solution accuracy assessment and is
   performed separately from it.
3. Twenty-one blind tests show which planted coding mistakes MMS detects. On
   the weaker approaches: the trend method "sets a very low bar … Most
   unverified codes would pass the physical trend test"; for comparisons,
   "A successful comparison test does not rule out the possibility that both
   codes contain the same mistake." Stated limits: MMS "does not address the
   issues of code robustness, performance, or formal correctness"; "One cannot
   apply the order-of-accuracy criterion to solutions containing
   singularities."
4. - P16 (independent kernels): **superseded** as the verification criterion;
     two kernels agreeing is the comparison approach, the second-lowest rung.
   - P16 (conserved quantities): conservation checks are consistency-level
     evidence; refines.
   - P09 and incident C10/F1 (an "independent" audit whose test switched the
     omitted term off): the fully-general-coefficients rule is the established
     remedy. Supports.
   - CE-8 (200,000 SNEC windows on a permissive benchmark): the trend-test
     warning. Supports the lesson.
   - P05: smooth manufactured solutions are required for order-of-accuracy
     tests. Supports a regularity rule for verification geometries.
5. Transfers directly to every kernel that maps a metric to a stress tensor,
   null energies, classifiers or geodesics. The blind-test protocol (plant
   mistakes, check detection) transfers to classifier fixtures (A1 in the
   September inventory).

### V7. Oberkampf & Roy, *Verification and Validation in Scientific Computing*

1. W. L. Oberkampf & C. J. Roy, *Verification and Validation in Scientific
   Computing*, Cambridge University Press, 2010, DOI 10.1017/CBO9780511760396.
   Second edition: *Verification, Validation, and Uncertainty Quantification
   in Scientific Computing*, CUP, 22 March 2025, DOI 10.1017/9781009031004.
   **PARTIAL** (Crossref description and chapter list).
2. Chapter structure confirms the separation the field uses: "Code
   verification" (pp. 170–207), "Exact solutions" (208–248), "Solution
   verification" (250–285), "Discretization error" (286–342), "Model
   validation fundamentals" (371–408), "Predictive capability" (555–670),
   "Maturity assessment of modeling and simulation" (696–727).
3. The standard graduate text; its content on rigor rankings is confirmed here
   through V6 and V9, which it extends.
4. P16, P18 — refines.
5. The book to cite for the verification chapter; the 2025 edition is current.

### V8. Roy 2005 review

1. C. J. Roy, "Review of code and solution verification procedures for
   computational simulation", *J. Comput. Phys.* **205**(1), 131–156 (2005),
   DOI 10.1016/j.jcp.2004.10.036. **PARTIAL** (Crossref only; abstract
   withheld). Its ranking of code-verification methods is not relied on here;
   V6 supplies the ranking.

### V9. Oberkampf & Trucano 2002; AIAA G-077-1998

1. W. L. Oberkampf & T. G. Trucano, "Verification and validation in
   computational fluid dynamics", *Prog. Aerosp. Sci.* **38**, 209–272 (2002),
   DOI 10.1016/S0376-0421(02)00005-2; open copy OSTI 793406 (SAND2002-0529).
   **VERIFIED** (full text). AIAA, *Guide for the Verification and Validation
   of Computational Fluid Dynamics Simulations*, AIAA G-077-1998(2002),
   DOI 10.2514/4.472855. **PARTIAL** (Crossref); its definitions are quoted
   from V9's full text.
2. Definitions (AIAA, quoted in V9): verification is "The process of
   determining that a model implementation accurately represents the
   developer's conceptual description of the model and the solution to the
   model"; validation is "The process of determining the degree to which a
   model is an accurate representation of the real world from the perspective
   of the intended uses of the model." The **validation hierarchy**: complete
   system → subsystem cases → benchmark cases → unit problems, with coupling
   between physics reduced at each lower tier. **Calibration is distinct from
   validation**: adjusting parameters "so that improved agreement with the
   experimental data is obtained … is expedient in certain engineering
   situations, but it is weakly defensible", and "the term calibration more
   appropriately describes the process than does validation".
3. The tiered approach is recommended "Because of the infeasibility and
   impracticality of conducting true validation experiments on most complex
   systems"; unit problems isolate "One element of complex physics".
4. - P18 — refines: the claim ladder's rungs (component source → finite pair
     → coupled system) parallel the tiers, and the tier concept supplies the
     rule that each tier reduces coupling on purpose and a complete-system
     tier remains necessary.
   - I-11, CE-3 (closure fits, oracle partitions): the calibration/validation
     distinction names the error exactly. A source basis fitted to a known
     demand is calibration.
   - CE-1, CE-6 (frame-blind review): verification checks implementation
     against the conceptual model; it cannot detect a wrong conceptual model.
     Topology, the passenger worldline and the complete-tensor type are
     conceptual-model questions. Supports a separate frame review.
5. Transfers: definitions, tiers, calibration warning. Does not transfer:
   validation against experiment. For a prescribed spacetime with no
   laboratory counterpart, only verification and physical-consistency checks
   are available; the book must say that claims stop at verified
   consequences of stated physics.

### V10. ASME V&V 20-2009

1. ASME V&V 20-2009, *Standard for Verification and Validation in
   Computational Fluid Dynamics and Heat Transfer*. **PARTIAL**: content
   **VERIFIED** from K. Dowding, "Overview of ASME V&V 20-2009 Standard",
   Sandia SAND2016-5342C (OSTI 1368927, full slides read); the standard's own
   text was not fetched.
2. Comparison error E = S − D; simulation error δ_S = δ_model + δ_num +
   δ_input; validation uncertainty u_val = √(u_num² + u_input² + u_D²) for
   independent errors; the model error lies in [E − u_val, E + u_val]. u_num
   comes from the GCI; "Code verification does not directly contribute to
   unum"; u_input by mean-value propagation or Latin hypercube sampling.
3. Built to be consistent with experimental uncertainty practice (ASME PTC
   19.1, ISO GUM).
4. P16, P18 — refines: separates numerical and input uncertainty and states
   them in the same units as the claim.
5. u_num and u_input transfer; u_D and E have no counterpart without data.
   The transferable content is "report numerical and input uncertainty on each
   decision quantity".

### V11. ASME V&V 10-2019

1. ASME V&V 10-2019 (reaffirmed 2025), *Standard for Verification and
   Validation in Computational Solid Mechanics*. **PARTIAL** (ASME product
   page). The 2006 edition was titled a *Guide*; that history comes from a
   search snippet and is **UNVERIFIED**.
2. "a common language, a conceptual framework, and general guidance for
   implementing the processes of computational model VVUQ."
4. P16, P18 — supports (terminology).

### V12. ASME V&V 40-2018 (risk-informed credibility)

1. ASME V&V 40-2018, *Assessing Credibility of Computational Modeling through
   Verification and Validation: Application to Medical Devices*.
   **VERIFIED** (ASME product description).
2. Credibility "should be commensurate with the degree to which the
   computational model is relied on as evidence" and with the "consequences of
   that decision being incorrect."
3. Developed with the US FDA for regulatory submissions; "Not a quantitative
   methodology or step-by-step guide."
4. P16 and incident F3/C2 (refinement ladders that decided nothing; errors
   normalized to the wrong budget) — **refines**: verification effort is sized
   to the decision it supports. P18 — refines.
5. Transfers as a principle; the medical risk categories do not.

### V13. NASA-STD-7009B (2024)

1. NASA, *Standard for Models and Simulations*, NASA-STD-7009B, approved
   5 March 2024 (standards.nasa.gov). **VERIFIED** (full text read).
2. M&S results reporting shall include "(1) the best estimate of the results,
   (2) a statement on the uncertainty in the results, (3) objective,
   credibility supporting, assessments of the M&S capabilities and M&S results
   …, (4) explicit caveats accompanying the results (e.g., the use of the M&S
   in violation of its assumptions or M&S limits), and (5) the risks
   associated with accepting the results". Results assessment uses six
   factors: use assessment, input pedigree, uncertainty characterization,
   results robustness, technical review (with reviewer independence), and
   process management, each with level definitions.
3. Purpose: "to reduce the risks associated with M&S-influenced decisions."
4. - P18 — **refines**: a fixed reporting template for each claim, with
     caveats naming violated assumptions.
   - I-17 (labels ahead of evidence) and F8 (stacked relaxations with no
     ledger) — the caveats and input-pedigree factors are the established
     remedy. Supports.
   - CE-1 — the technical-review factor asks "how independent were the
     reviewers". Supports.
5. Transfers nearly whole. The "use history" factor has little content in a
   new field.

### V14. Predictive Capability Maturity Model (PCMM)

1. W. L. Oberkampf, T. G. Trucano & M. M. Pilch, *Predictive Capability
   Maturity Model for Computational Modeling and Simulation*, Sandia
   SAND2007-5948 (October 2007), OSTI 976951, DOI 10.2172/976951.
   **VERIFIED** (OSTI abstract).
2. Six elements, each rated at four maturity levels: representation and
   geometric fidelity; physics and material model fidelity; code verification;
   solution verification; model validation; uncertainty quantification and
   sensitivity analysis. It draws on CMMI and NASA/DoD TRLs.
3. Built for engineering M&S at Sandia; it "does not determine whether results
   meet specified performance requirements."
4. P18 — **refines**. A single linear ladder lets depth on one rung mask gaps
   elsewhere (CE-2: 15 gates and machine-precision certificates on a two-ended
   geometry with the passenger off its worldline). A matrix of independent
   dimensions exposes that pattern.
5. Transfers as a structure; the element list needs domain entries
   (topology and global structure, algebraic type, occupant quantities,
   source normalization).

### V15. Validated numerics (interval enclosures)

1. W. Tucker, *Validated Numerics: A Short Introduction to Rigorous
   Computations*, Princeton University Press, 2011, ISBN 9780691147819
   (**PARTIAL**, publisher description). R. E. Moore, R. B. Kearfott &
   M. J. Cloud, *Introduction to Interval Analysis*, SIAM, 2009,
   DOI 10.1137/1.9780898717716 (**PARTIAL**, Crossref).
2. Set-valued arithmetic that returns guaranteed enclosures: per the
   publisher, computations "that can find all possible solutions to a problem
   while taking into account all possible sources of error".
4. P01 2e, I-07, L4 (sign boundaries and bands between samples) —
   **supersedes** node sampling and line root-finding when a certificate over
   a region is needed. Consistent with the P01 vetting, which found Le (2026b)
   using interval evaluation for energy conditions.
5. Transfers: metric components and curvature are closed-form or smooth, so
   interval extensions are available.

### V16. Oreskes, Shrader-Frechette & Belitz 1994

1. N. Oreskes, K. Shrader-Frechette & K. Belitz, "Verification, Validation,
   and Confirmation of Numerical Models in the Earth Sciences", *Science*
   **263**, 641–646 (1994), DOI 10.1126/science.263.5147.641. **VERIFIED**
   (abstract).
2. "Verification and validation of numerical models of natural systems is
   impossible … Models can be confirmed by the demonstration of agreement
   between observation and prediction, but confirmation is inherently
   partial … The primary value of models is heuristic."
4. P18, I-17 — supports naming results by the check passed and avoiding
   words that imply coverage ("seal", "certificate", "capstone").
5. Transfers as a caution on claim wording.

### Area 1 synthesis

**Metric-first design and MMS share one computation.** MMS prescribes u,
computes the source f = L[u], and uses f only to test a code. Metric-first
design prescribes g, computes T = G[g]/8π, and treats T as an engineering
demand. The computation certifies that the source is *consistent with* the
prescribed field; it certifies nothing about the source's *physical
existence*. The incidents where fitted source bases always "closed" (I-11,
CE-3) follow directly: with the demand known, any sufficiently flexible basis
reproduces it. *(Observation, mine; the MMS description is V5–V6.)*

**The transfer is cheap.** Any analytic metric has an analytic Einstein tensor
by computer algebra, so MMS for the curvature and stress kernels needs no
invented source term. A verification suite should use manufactured metrics
with every coupling switched on (lapse gradients, shift gradients, time
dependence, off-diagonal spatial metric, non-flat slices) and report observed
order on each output, including null energies and the classifier's
discriminants. For solution verification, a second independent residual
exists at no cost: the contracted Bianchi identity makes ∇_μT^{μν} = 0 an
identity, so a separately discretized divergence of the computed T must
converge to zero at the scheme's order (Choptuik's independent residual, N1).
*(Inference, mine, from V5, V6, N1.)*

---

## Area 2. Numerical-relativity verification practice

### N1. Choptuik 1991

1. M. W. Choptuik, "Consistency of finite-difference solutions of Einstein's
   equations", *Phys. Rev. D* **44**, 3124–3135 (1991),
   DOI 10.1103/PhysRevD.44.3124. **VERIFIED** (abstract via OpenAlex).
2. Freely evolved constraints converge at the scheme's order, using "the key
   observation, originally due to Richardson, that numerical differentiation
   need not produce an O(h^{p−1}) quantity from an O(h^p) one". Alcubierre et
   al. (N2) attribute to Choptuik the practice of checking consistency by
   "'independent residual evaluation' using an alternative discretization of
   the equations obtained by symbolic algebra techniques".
3. "These results show that expected convergence of various residual
   quantities can be achieved in practice."
4. P16 — refines: an independent residual is a specific, stronger form of
   "independent kernels": the second discretization tests the first solution
   against the equations themselves.
5. Transfers (see area 1 synthesis).

### N2. Alcubierre et al. 2004, "Apples with Apples"

1. M. Alcubierre, G. Allen, C. Bona, … J. Winicour (21 authors), "Toward
   standard testbeds for numerical relativity", *Class. Quantum Grav.* **21**,
   589 (2004), arXiv:gr-qc/0305023. **VERIFIED** (full text).
2. Standardized tests that "separate out different effects, and their causes";
   each test specifies gauge, grids, resolutions for convergence testing and
   minimum output. Criteria: broadly applicable, unambiguous data, specified
   free quantities, model-independent outputs.
3. Rationale in the text:
   - "it is important not to examine the constraints in isolation"; a code that
     enforces the constraints "might suffer other losses of accuracy which
     produce a numerically generated spacetime that is unphysical";
   - run length before a crash is no quality criterion without accuracy;
   - exact solutions "are the most unambiguous tests and the most important for
     debugging";
   - on agreement between codes: "a common error could lead to acceptance of an
     incorrect numerical solution"; "systematic problems can lead a code to
     converge to a physically irrelevant solution";
   - boundary inconsistencies give growing modes "that may not appear in tests
     run at low resolutions or short time scales".
4. - P16 — refines and partly supersedes (code agreement is weaker than exact
     tests; convergence is necessary and insufficient).
   - CE-2, F2, F3 (convergence confirming quantities that answered the wrong
     questions) — the sentence on converging to a physically irrelevant
     solution is the field's own statement of the lesson. Supports.
   - I-13 (domain truncation) — supports.
5. Transfers: testbed design, the warning on code agreement, the refusal to
   read constraint satisfaction alone as correctness.

### N3. Babiuc et al. 2008

1. M. C. Babiuc, S. Husa, D. Alic, I. Hinder, … J. Winicour (11 authors),
   "Implementation of standard testbeds for numerical relativity",
   *Class. Quantum Grav.* **25**, 125012 (2008), arXiv:0709.3559.
   **VERIFIED** (full text).
2. Benchmarks run across codes and formulations; results archived in a shared
   repository.
3. "Useful benchmarks have been established for the linear wave, gauge wave,
   and Gowdy wave tests, which have revealed clear deficiencies in various
   codes. Such deficiencies raise a clear alert that it is necessary to apply
   or recheck other verification techniques, such as convergence tests." On
   adoption: "In order for code verification to be attractive, the tests have
   to be useful and the investment in time has to be minimal." The authors
   quote Post & Votta on defect rates of about seven faults per 1000 lines of
   Fortran (the Post & Votta source was **not** fetched; **UNVERIFIED**).
4. P16 — supports (shared benchmarks find real faults); CE-2 — supports.
5. Transfers: a warp-and-rail benchmark set (analytic metrics with known
   demand, type and energy-condition verdicts) would serve the field the same
   way.

### N4. Einstein Toolkit and Cactus test suites

1. F. Löffler, J. Faber, E. Bentivegna, … P. Laguna, "The Einstein Toolkit: A
   Community Computational Infrastructure for Relativistic Astrophysics",
   *Class. Quantum Grav.* **29**, 115001 (2012), arXiv:1111.3344.
   **VERIFIED** (full text). Cactus *Users' Guide* §B2.6 and §C1.8.5
   (einsteintoolkit.org/usersguide), **VERIFIED**.
2. Test suites store parameter files and their output; runs compare new
   output against stored output within per-file ABSTOL/RELTOL tolerances. The
   Users' Guide states their purpose: "Regression testing i.e. making sure that
   changes to the thorn or the flesh don't affect the output from a known
   parameter file" and "Portability testing". Löffler et al.: "nightly builds
   are checked against a set of benchmarks to ensure that consistent results
   are generated with the inclusion of all new commits".
3. Community practice for a large shared code base.
4. P16 — refines by distinction: regression tests certify *consistency with a
   stored answer*, which verification must certify first. Incident F9
   ("reproduce the reference audits" carried the 2.569 service ratio forward)
   and I-16 (the nested-reproduction check that saved a design family) are the
   two faces of this: reproduction guards refactoring and propagates stored
   errors.
5. Transfers directly; the book should present regression and verification as
   two separate test types.

### N5. Hannam et al. 2009, the Samurai project

1. M. Hannam, S. Husa, J. G. Baker, M. Boyle, … (19 authors), "The Samurai
   Project: verifying the consistency of black-hole-binary waveforms for
   gravitational-wave detection", *Phys. Rev. D* **79**, 084025 (2009),
   arXiv:0901.2437. **VERIFIED** (abstract).
2. Code comparison judged against each code's own error estimate and against
   the downstream use: phase and amplitude "agree within each code's
   uncertainty estimates"; mismatch below 10⁻³ for stated mass ranges; the
   waveforms "would be indistinguishable … if detected with a signal-to-noise
   ratio of less than ≈14".
3. Accuracy standard set by the detector's ability to tell waveforms apart.
4. P16 — refines: a comparison carries weight when each side reports its own
   error bar. P15/P18 — supports defining accuracy by the decision it serves
   (compare V12).
5. Transfers: accuracy requirements stated against the decision threshold
   (for example, a null-energy margin against the quantum-inequality bound).

### N6. Hinder et al. 2014, NRAR

1. I. Hinder, A. Buonanno, M. Boyle, … (84 authors), "Error-analysis and
   comparison to analytical models of numerical waveforms produced by the NRAR
   Collaboration", *Class. Quantum Grav.* **31**, 025012 (2014),
   arXiv:1307.5307. **VERIFIED** (abstract).
2. All waveforms "analysed in a uniform and consistent manner, with numerical
   errors evaluated using an analysis code created by members of the NRAR
   collaboration."
4. P16 — supports: a shared, independent error-analysis pipeline.
5. Transfers as practice for multi-group work.

### N7. Helmerich et al. 2024, Warp Factory

1. C. Helmerich, J. Fuchs, A. Bobrick, L. Sellers, B. Melcher, G. Martire,
   "Analyzing warp drive spacetimes with Warp Factory", *Class. Quantum Grav.*
   **41**, 095009 (2024), arXiv:2404.03095v2. **VERIFIED** (full text,
   Appendix B).
2. Metric derivatives by "a fourth-order central finite difference method
   … with a 1-meter grid spacing." Error discussion uses Schwarzschild, whose
   exterior T⁰⁰ must vanish, at two resolutions (20 m and 1 m) and two stencil
   orders; it classifies edge-of-grid, discretization, round-off and
   truncation errors, and recommends excluding two boundary points. "Metrics
   with sharp transitions can lead to these finite difference edge effects and
   may give energy/violation that wouldn't actually exist at those
   boundaries."
3. The field's public tool verifies by an exact vacuum benchmark (exact-
   solution approach, percent-error or consistency criterion in V6 terms); no
   observed-order test is reported.
4. P16 — the field's current practice sits below the V6 top rung, so the book
   teaches the stronger method. P05 — supports: sharp transitions produce
   spurious violations numerically as well as physically.
5. Transfers as a baseline to improve on.

### Area 2 synthesis

Numerical relativity already practises the core of P16: convergence testing,
Richardson extrapolation, independent residuals, shared testbeds and
regression suites. The core is therefore a **truism** for the book, stated once
with citations. The domain content that survives: the prescribed-metric
setting makes exact tests cheap (area 1 synthesis); the Bianchi identity
gives a free residual; and energy-condition verdicts on sign sets need
between-sample certification, which convergence testing of smooth outputs
cannot supply. Constraint monitoring in the NR sense applies only in the
coupled-dynamics rung, where fields evolve on or with the geometry.

---

## Area 3. Inverse design and demanded-material design

### T1. Pendry, Schurig & Smith 2006

1. J. B. Pendry, D. Schurig & D. R. Smith, "Controlling Electromagnetic
   Fields", *Science* **312**, 1780–1782 (2006),
   DOI 10.1126/science.1125907. **VERIFIED** (abstract via Semantic Scholar).
2. Prescribe the desired field geometry by a coordinate transformation; the
   material tensors (ε, μ) follow from the Jacobian. "Using the freedom of
   design that metamaterials provide, we show how electromagnetic fields can be
   redirected at will and propose a design strategy."
3. The cloak example excludes "all electromagnetic fields" from a volume.
4. P02 — the adjacent field's founding instance of demand-first design;
   supports metric-first as a general design paradigm.
5. See synthesis.

### T2. Leonhardt 2006

1. U. Leonhardt, "Optical Conformal Mapping", *Science* **312**, 1777 (2006);
   arXiv:physics/0602092 (title there: "Optical Conformal Mapping and
   Dielectric Invisibility Devices"). **VERIFIED** (arXiv abstract).
2. Conformal maps give isotropic index profiles.
3. "Ideal invisibility devices are impossible due to the wave nature of light
   … perfect invisibility within the accuracy of geometrical optics … the
   imperfections of invisibility can be made arbitrarily small to hide objects
   that are much larger than the wavelength."
4. P02, P07 — supports: the prescription's validity regime (geometrical
   optics) is stated up front.
5. Transfers as a habit: state the regime in which the prescription is exact.

### T3. Schurig et al. 2006 (first cloak, reduced parameters)

1. D. Schurig, J. J. Mock, B. J. Justice, S. A. Cummer, J. B. Pendry,
   A. F. Starr, D. R. Smith, "Metamaterial Electromagnetic Cloak at Microwave
   Frequencies", *Science* **314**, 977–980 (2006),
   DOI 10.1126/science.1133628. **VERIFIED** (abstract via Europe PMC).
2. Built "according to the previous theoretical prescription" with
   metamaterials "designed for operation over a band of microwave
   frequencies"; the parameters were simplified (T6 quotes them).
3. "The cloak decreased scattering from the hidden object while at the same
   time reducing its shadow, so that the cloak and object combined began to
   resemble empty space." The theory is described as possible "at least over
   a narrow frequency band."
4. P02 — supports the demand-first route to hardware; see T6 for its cost.

### T4. Cummer et al. 2006

1. S. A. Cummer, B.-I. Popa, D. Schurig, D. R. Smith, J. Pendry, "Full-wave
   simulations of electromagnetic cloaking structures", *Phys. Rev. E* **74**,
   036621 (2006), DOI 10.1103/PhysRevE.74.036621. **VERIFIED** (abstract).
2. Full-wave simulation of ideal and "nonideal (but physically realizable)"
   parameters.
3. "Neither the coordinate transformation-based analytical formulation nor
   the supporting ray-tracing simulation indicate how material perturbations and
   full-wave effects might affect the solution." Findings: low reflection and
   power-flow bending "are not especially sensitive to modest permittivity and
   permeability variations"; performance "degrades smoothly with increasing
   loss"; an "eight- (homogeneous) layer approximation" works; "An imperfect but
   simpler version of the cloaking material is derived."
4. P16, P02 — supports: forward full-physics simulation of the realizable
   approximation is the verification step between demand and hardware.
5. Transfers: after replacing the demanded tensor with a realizable source,
   evaluate what that source actually produces.

### T5. Cai, Chettiar, Kildishev & Shalaev 2007

1. W. Cai, U. K. Chettiar, A. V. Kildishev, V. M. Shalaev, "Optical cloaking
   with metamaterials", *Nature Photonics* **1**(4), 224–227 (April 2007),
   DOI 10.1038/nphoton.2007.28. **VERIFIED** (abstract).
2. A non-magnetic reduced-parameter design, because the microwave design
   "cannot be implemented for an optical cloak".
4. P02 — supports: the realizable parameter set depends on the regime.

### T6. Yan, Ruan & Qiu 2007: simplified cloaks are inherently visible

1. M. Yan, Z. Ruan, M. Qiu, "Cylindrical Invisibility Cloak with Simplified
   Material Parameters is Inherently Visible", *Phys. Rev. Lett.* **99**,
   233901 (2007), arXiv:0706.0655. **VERIFIED** (full text).
2. Analysis of the reduced parameters μ_r = ((r − a)/r)², μ_θ = 1,
   ε_z = (b/(b − a))².
3. Findings:
   - the reduction's derivation "has assumed beforehand that μθ is a constant",
     which changes the wave operator;
   - the zeroth-order cylindrical wave sees "a homogeneous isotropic medium"
     with n_eff = b/(b − a); its scattering coefficient converges to 0.867 with
     thickness, and objects inside are exposed to it;
   - higher orders scatter less but "do not converge to zero even when the
     cloak wall is very thick";
   - "the penalty of using the simplified cloak is more than just nonzero
     reflectance at the cloak boundary";
   - the ideal cloak is "extremely sensitive to the position of the cloak's
     inner surface": moving it from 0.100 to 0.101 m lets field of norm 0.5466
     leak inside.
4. - P02 — **refines**: a simplified source is a different design and its
     penalty must be computed forward; the original paper's stated penalty
     (reflectance) understated it.
   - F8 (C1 passes resting on stacked relaxations) — the same pattern; supports
     a relaxation ledger plus forward check.
   - P05 — supports: regularizing a singular demand at an inner boundary has
     large effects.
5. Transfers fully as a process lesson.

### T7. Li & Pendry 2008: the carpet cloak

1. J. Li & J. B. Pendry, "Hiding under the Carpet: A New Strategy for
   Cloaking", *Phys. Rev. Lett.* **101**, 203901 (2008),
   DOI 10.1103/PhysRevLett.101.203901, arXiv:0806.4396. **VERIFIED** (full
   text).
2. Method, in four moves:
   - **Topology choice removes singular demand.** "there are three distinct
     topological possibilities: the cloaked object can be crushed to a point,
     to a line, or to a sheet"; crushing to a sheet gives parameters that
     "need not be singular". "It is the result of crushing the object to a
     conducting plane instead of a line so that there is no singular point in
     the coordinate transform."
   - **Spend the map freedom on the hard component.** A quasi-conformal map,
     found by minimizing the Modified-Liao functional ∫(Tr g)²/det g with
     sliding boundaries, "minimizes not only the average but also the maximum"
     anisotropy; the anisotropy factor becomes a constant 1.042.
   - **Trade ranges.** "we sacrifice n to a larger range at the same time
     anisotropy is minimized" (n² from 0.68 to 1.96 against 1.0–1.153 for the
     naive map).
   - **Drop the residual and test.** "If the anisotropy is small enough, we can
     simply drop this part (by assigning α = 1) and only keep the refractive
     index n." FDTD beam and pulse tests follow.
3. Stated limit: "if a thinner cloak or bigger object is used, it is expected
   that the distortion will become larger. It is due to a larger anisotropy
   neglected in our cloak profile."
4. - P06 — **supports**: the topological choice decided whether the demand was
     finite.
   - P02 — **refines**: within the family of maps that deliver the same
     exterior function, choose the one that minimizes the demand component the
     source technology finds hardest. The project's geometry revisions that
     removed Type IV layers are this move (E1 in the September inventory).
   - P01 2g — supports type-as-matching.
5. Transfers as the central design move of the book's inverse-design chapter.

### T8. Carpet cloak experiments

1. R. Liu, C. Ji, J. J. Mock, J. Y. Chin, T. J. Cui, D. R. Smith, "Broadband
   Ground-Plane Cloak", *Science* **323**, 366–369 (2009),
   DOI 10.1126/science.1166949. J. Valentine, J. Li, T. Zentgraf, G. Bartal,
   X. Zhang, "An optical cloak made of dielectrics", *Nature Materials* **8**,
   568–571 (2009), DOI 10.1038/nmat2461. **VERIFIED** (abstracts).
2. Liu et al.: "a metamaterial consisting of thousands of elements, the
   geometry of each element determined by an automated design process";
   non-resonant elements give "a broad operational bandwidth (covering the
   range of 13 to 16 gigahertz …) and … extremely low loss". Valentine et al.:
   "The cloak consists only of isotropic dielectric materials, which enables
   broadband and low-loss invisibility at a wavelength range of 1,400-1,800
   nm."
4. P02 — supports: the reduced-demand design reached hardware within a year
   in two bands.

### T9. Zhang, Chan & Wu 2010: the lateral shift

1. B. Zhang, T. Chan, B.-I. Wu, "Lateral Shift Makes a Ground-Plane Cloak
   Detectable", *Phys. Rev. Lett.* **104**, 233903 (2010), arXiv:1004.2551.
   **VERIFIED** (abstract).
2. "This cloak without anisotropy will generally lead to a lateral shift of the
   scattered wave, whose value is comparable to the height of the cloaked
   object … the corresponding virtual space is thinner and wider than it should
   be." For a bump of height 0.2, a 45° ray shifts about 0.15.
4. P02 — **refines** (with T6): dropping a "small" demanded component changed
   the delivered geometry itself. The forward check must compare the delivered
   service against the specified service. P12, P15 — supports measuring the
   service quantity directly.
5. Transfers: after trimming a demand component, recompute the effective
   geometry the occupant or signal actually experiences.

### T10. Calcite cloaks: matching the transformation to a natural material

1. B. Zhang, Y. Luo, X. Liu, G. Barbastathis, "Macroscopic Invisibility Cloak
   for Visible Light", *Phys. Rev. Lett.* **106**, 033901 (2011),
   arXiv:1012.2238 (**VERIFIED**, full text). X. Chen, Y. Luo, J. Zhang,
   K. Jiang, J. B. Pendry, S. Zhang, "Macroscopic invisibility cloaking of
   visible light", *Nature Communications* **2**, 176 (2011),
   DOI 10.1038/ncomms1176 (**VERIFIED**, abstract).
2. A uniform squeeze of space gives a *homogeneous* uniaxial cloak realizable
   in natural calcite. Zhang et al.: the difficulties "boil down to two
   difficulties in the fabrication of cloak materials—anisotropy and
   inhomogeneity. The previously proposed quasiconformal mapping strategy
   attempted to solve anisotropy … However, in conventional optical lens
   fabrication, the inhomogeneity is more difficult to implement than
   anisotropy."
3. Result: a cloak hiding an object "larger than 3500 free-space-wavelength"
   across red, green and blue light. Stated limits: "it can only work in a 2D
   geometry … and for only one polarization"; in a liquid of n ≈ 1.53 "it is
   not subject to the limitations of delay-bandwidth and delay-loss for
   cloaking in air". Chen et al.: earlier cloaks' composite materials "limit
   the size of the cloaked region to a few wavelengths".
4. - P01 2g and P02 — **supports and sharpens**: which demand component is
     "hard" depends on the source technology, so the geometry family should be
     chosen so its demand lies in an available source's range.
   - P19 — supports forks: the quasi-conformal and linear-map branches each
     won in a different technology.
5. Transfers: map each candidate source family's algebraic and spatial range
   (Hawking–Ellis type, sign pattern, homogeneity, anisotropy), then restrict
   the geometry family to demands inside it.

### T11. Physical limits on cloaking

1. Sources:
   - H. Hashemi, B. Zhang, J. D. Joannopoulos, S. G. Johnson, "Delay-Bandwidth
     and Delay-Loss Limitations for Cloaking of Large Objects", *Phys. Rev.
     Lett.* **104**, 253903 (2010), arXiv:1003.5934 (**VERIFIED**, full text).
   - F. Monticone & A. Alù, "Do Cloaked Objects Really Scatter Less?",
     *Phys. Rev. X* **3**, 041005 (2013), arXiv:1307.3996 (**VERIFIED**, full
     text).
   - F. Monticone & A. Alù, "Invisibility exposed: physical bounds on passive
     cloaking", *Optica* **3**, 718–724 (2016), DOI 10.1364/OPTICA.3.000718
     (**VERIFIED**, abstract).
   - D. A. B. Miller, "On perfect cloaking", *Opt. Express* **14**,
     12457–12466 (2006), DOI 10.1364/OE.14.012457 (**VERIFIED**, abstract).
   - P.-Y. Chen, C. Argyropoulos, A. Alù, "Broadening the Cloaking Bandwidth
     with Non-Foster Metasurfaces", *Phys. Rev. Lett.* **111**, 233001 (2013),
     arXiv:1306.5835 (**VERIFIED**, abstract).
   - R. M. Fano, "Theoretical limitations on the broadband matching of
     arbitrary impedances", *J. Franklin Inst.* **249**, 57–83 (1950),
     DOI 10.1016/0016-0032(50)90006-8 (**PARTIAL**, Crossref; used here through
     Monticone & Alù 2016).
   - "Chen, Liang & Alù" on cloaking limits: **UNVERIFIED** — no paper by these
     authors was found; the verified Chen–Alù paper is the 2013 PRL above.
2. The bounds:
   - Hashemi et al.: perfect cloaking in vacuum "is impossible over nonzero
     bandwidth, because rays traveling around the object must have velocity
     > c to mimic empty space"; even ground-plane cloaks meet "delay–bandwidth
     and delay–loss limitations that worsen as the size of the object to be
     cloaked increases relative to the wavelength"; minimum thickness
     d ≳ h/(n − 1) without slow light; loss tolerance
     Im n/Re n ≪ λ/[4π(h + d)]. Passive linear delay is bounded, "unlike
     time-varying active devices".
   - Monticone & Alù 2013: "the total extinction and scattering, integrated over
     all wavelengths, of any linear, passive, causal and non-diamagnetic cloak
     necessarily increases compared to the uncloaked case."
   - Monticone & Alù 2016: bounds from the Bode–Fano theory of broadband
     matching; "fundamentally new directions, involving nonlinearities and
     active metamaterials, become necessary to realize broadband cloaking".
   - Miller 2006 is an **active** construction, with no passive bound: sensors
     and sources "could operate over broad bandwidths", and "any active scheme
     should [be] detectable by a quantum probe".
   - Chen et al. 2013: active non-Foster metasurfaces give bandwidth "orders of
     magnitude broader than any available passive cloaking technology".
3. Derived from causality, passivity, linearity and energy conservation
   (Kramers–Kronig sum rules) — the optical counterparts of energy conditions
   and quantum inequalities.
4. - P07 — **supports** as established practice: engineering electromagnetics
     derives fundamental bounds (Bode–Fano, sum rules) before and alongside
     device design. L1 of the September inventory (class-level exclusions first)
     has direct precedent.
   - L23 (a local source fix relocates a fixed deficit) — Monticone & Alù
     2013 is the optical analogue: suppressing scattering in one band raises it
     elsewhere.
5. Transfer: bounds first; identify which assumption (passivity, linearity,
   time-independence) an escape route drops. Non-transfer: the optical bounds
   themselves; spacetime's bounds come from energy conditions, quantum
   inequalities and ANEC (foundations survey).

### T12. Optical metrics: lapse as refractive index

1. U. Leonhardt & T. G. Philbin, "General relativity in electrical
   engineering", *New J. Phys.* **8**, 247 (2006), arXiv:cond-mat/0607418
   (**VERIFIED**, full text). W. Gordon, "Zur Lichtfortpflanzung nach der
   Relativitätstheorie", *Ann. Phys.* **377**(22), 421–456 (1923),
   DOI 10.1002/andp.19233772202 (**PARTIAL**). J. Plebański, "Electromagnetic
   Waves in Gravitational Fields", *Phys. Rev.* **118**, 1396–1408 (1960),
   DOI 10.1103/PhysRev.118.1396 (**PARTIAL**; content via Leonhardt & Philbin).
2. Plebański's constitutive relations as given by Leonhardt & Philbin (their
   Eq. 5, signature +−−−): ε^{ij} = μ^{ij} = −√(−g) g^{ij}/g₀₀,
   w_i = g₀ᵢ/g₀₀. "Empty space appears as an impedance-matched anisotropic
   magneto-electric or moving medium." Their programme: "Given a desired
   device function, the theory describes the electromagnetic properties that
   turn this function into fact."
3. Rooted in Fermat's principle; Gordon first noticed that "moving isotropic
   media appear to electromagnetic fields as certain effective spacetime
   geometries". Footnote 1: "we use the kinematic aspects of general
   relativity, not the dynamic ones."
4. Derivation (mine, from Eq. 5): for ds² = α²dt² − ψ²δ_ij dx^i dx^j,
   g₀₀ = α², g^{ij} = −ψ⁻²δ^{ij}, √(−g) = αψ³, so ε = μ = (ψ/α)δ and the
   index is n = ψ/α; on flat slices n = 1/α. The shift enters only through
   w ∝ g₀ᵢ, the constitutive form of a moving medium. Lapse elements
   therefore act as graded index (low lapse = high index: slow light, focusing
   and trapping), and the shift acts as medium flow. This matches the
   analogue-gravity reading (A1: sound speed as lapse, flow as shift).
   Bears on P03 and the knob maps — supports an optics vocabulary for design
   intuition (ray bending toward low lapse, drag by shift).
5. Transfers for null-ray kinematics (horizons, trapping, arrival times,
   optical audits). Does not transfer: the medium is a source the designer
   chooses freely; in GR the "medium" is fixed by the Einstein equations.

### T13. Topology optimization

1. Sources:
   - M. P. Bendsøe & N. Kikuchi, "Generating optimal topologies in structural
     design using a homogenization method", *Comput. Methods Appl. Mech. Eng.*
     **71**(2), 197–224 (1988), DOI 10.1016/0045-7825(88)90086-2
     (**PARTIAL**).
   - M. P. Bendsøe & O. Sigmund, *Topology Optimization: Theory, Methods and
     Applications*, 2nd ed., Springer, 2003 (ISBN 3540429921; eBook DOI
     10.1007/978-3-662-05086-6, dated 2004 by Crossref) (**PARTIAL**,
     publisher description).
   - O. Sigmund, "A 99 line topology optimization code written in Matlab",
     *Struct. Multidisc. Optim.* **21**, 120–127 (2001) (**VERIFIED**, full
     text).
   - O. Sigmund & J. Petersson, "Numerical instabilities in topology
     optimization …", *Struct. Optim.* **16**, 68–75 (1998),
     DOI 10.1007/BF01214002 (**PARTIAL**).
   - F. Wang, B. S. Lazarov & O. Sigmund, "On projection methods, convergence
     and robust formulations in topology optimization", *Struct. Multidisc.
     Optim.* **43**(6), 767–784 (2011), DOI 10.1007/s00158-010-0602-y
     (**VERIFIED**, abstract via DTU Orbit; correction 2022).
   - A. Olason & D. Tidman, *Methodology for Topology and Shape Optimization in
     the Design Process*, Master's thesis 2010:11, Chalmers (**VERIFIED**,
     full text).
   - M. Zhou et al., "An integrated approach to topology, sizing, and shape
     optimization", *Struct. Multidisc. Optim.* **26**, 308–317 (2004),
     DOI 10.1007/s00158-003-0351-2 (**PARTIAL**; content not read).
2. The methods:
   - distribute material to optimize a function under resource constraints;
   - relaxed (homogenized) designs bound performance and are unbuildable:
     homogenization designs "cannot be built since no definite length-scale is
     associated with the microstructures. However, the homogenization approach …
     can provide bounds on the theoretical performance";
   - realizability is imposed by penalization and length-scale control: "To
     ensure existence of solutions, the power-law approach must be combined
     with a perimeter constraint, a gradient constraint or with filtering
     techniques";
   - robust formulations optimize eroded, intermediate and dilated designs at
     once for manufacturing tolerance and mesh convergence (Wang et al.);
   - staging: "In the early stage of concept generation, topology optimization
     should be used … In the later stage, shape and size optimization should be
     used to fine-tune" (Olason & Tidman).
3. The book description reports that designs from these methods "are in
   production on a daily basis".
4. - L18 and C13/D14 in the September inventory (unbounded LPs concentrated
     material; optimizers used non-passive freedoms) — **supports**: the field
     learned that realizability constraints (penalization, filters, length
     scales, physical admissibility) must sit inside the optimization.
   - P06, L24 — supports: topology is decided at concept stage.
   - I-06 (cost-only objective selected a null component) — supports: the
     standard formulation optimizes delivered function under a resource
     constraint.
   - P05 — supports a length-scale requirement; the regularity order is set
     by the physics.
5. Transfers: relaxed-demand bounds, in-loop realizability, robust
   formulations. The density-interpolation machinery does not transfer
   directly: a stress-energy source has no scalar "material fraction".

### T14. Inverse design in nanophotonics

1. S. Molesky, Z. Lin, A. Y. Piggott, W. Jin, J. Vučković, A. W. Rodriguez,
   "Inverse design in nanophotonics", *Nature Photonics* **12**(11), 659–670
   (2018), DOI 10.1038/s41566-018-0246-9, arXiv:1801.06715 (arXiv title
   "Outlook for inverse design in nanophotonics"). **VERIFIED** (full text).
2. "the strengths of inverse design and transformation optics are highly
   complementary. Coordinate transformations often lead to a clear
   understanding of the boundary behavior that must be achieved … natural
   transformations … tend to produce material profiles that are difficult to
   fabricate, (unrealistic permittivities, anisotropy, etc). On the other hand,
   this second problem is well suited for inverse design." Fabrication
   constraints go "directly into the optimization problem" (filters, erosion
   and dilation, minimum radius of curvature). On bounds: "what is the maximum
   theoretical performance of an optical device? … Establishing such
   theoretical bounds … would help guide future work in all of photonics."
3. Experimental devices (wavelength splitters) validate the approach.
4. - P02 — **refines toward a hybrid**: the transformation (metric) fixes the
     function; optimization over realizable sources fills in the rest. This is
     a better method than choosing between "metric-first" and "source-first"
     (Le 2026a); both halves have roles.
   - P07 — supports bounds research.
5. Transfers: metric-first specification of the service and exterior,
   followed by optimization over physically admissible source parameters with
   the metric's service requirements as constraints.

### T15. Review

H. Chen, C. T. Chan & P. Sheng, "Transformation optics and
metamaterials", *Nature Materials* **9**, 387–396 (2010),
DOI 10.1038/nmat2743. **PARTIAL** (abstract only; not used for any verdict).

### Area 3 synthesis: what transformation optics learned

Transformation optics faced the problem the project faces: the prescription
returns a demanded material that is exact, often singular, anisotropic and
dispersive. Its twenty-year record gives six lessons.

1. **Spend the design freedom on realizability.** Many maps deliver the same
   exterior function. The field chose the map that minimizes the hardest
   demand component (quasi-conformal, T7) and chose the topology that removes
   singular demand (crush to a sheet, T7).
2. **"Hard" is relative to the source technology.** Metamaterials made
   anisotropy hard; lens fabrication made inhomogeneity hard, so the linear-map
   family matched natural calcite (T10). The geometry family should be matched
   to a source family's range.
3. **Every simplification is a new design and needs a forward check.** Reduced
   parameters kept ray paths and leaked the monopole (T6); dropping residual
   anisotropy produced a lateral shift of the object's height (T9); full-wave
   simulation of the realizable approximation became standard (T4).
4. **Bounds first.** Causality, passivity and linearity bound bandwidth, delay
   and loss, and the bounds tighten with size (T11). Escapes drop an
   assumption explicitly: active or time-varying media.
5. **Realizability belongs inside the optimizer.** Relaxed designs bound
   performance; buildable designs need penalization and length scales in the
   loop (T13, T14).
6. **The analogy is kinematic.** Transformation optics uses the geometry of
   light rays and none of Einstein's equations (T12). A medium can realize any
   constitutive tensor up to material limits, so its gap is a fabrication gap.
   In spacetime engineering the demanded stress must come from matter obeying
   field equations and energy conditions, so the gap is a physics gap. The
   process lessons transfer; the optimism about material freedom does not.

---

## Area 4. Design decomposition and the mapping from knobs to physics

### D1. Suh, axiomatic design

1. N. P. Suh, *The Principles of Design*, Oxford University Press, 1990
   (ISBN 0195043456) and *Axiomatic Design: Advances and Applications*, OUP,
   2001 (ISBN 0195134664). **PARTIAL** (Open Library records); content
   **VERIFIED** from MIT OpenCourseWare lecture notes "Chapter 10 Introduction
   to Axiomatic Design", which "draws extensively on materials from
   [Suh 2001]" (`work/dd_suh_ocw.txt`), and from Jones 2017 (D2). Suh 1998,
   *Res. Eng. Des.* **10**, 189: **UNVERIFIED** (not fetched).
2. Two axioms: "Maintain the independence of the functional requirements
   (FRs)" and "Minimize the information content of the design." Design
   equation {FR} = [A]{DP}, differential form {dFR} = [A]{dDP},
   A_ij = ∂FR_i/∂DP_j. Diagonal A: **uncoupled**. Triangular A: **decoupled**
   ("DP1 can be designed independently to satisfy FR1 and then DP2 can be
   designed to satisfy FR2 while also considering the effect of DP1", Jones).
   All other matrices: **coupled**. Theorem 1: "When the number of design
   parameters is less than the number of functional requirements, we always
   have a coupled design." Decomposition by zigzagging between functional and
   physical domains. Listed designer mistakes include "Not Recognizing a
   Decoupled Design" and "Concentrating on Symptoms rather than Cause".
3. Presented as axioms, justified by the claim that they are common to good
   designs (D2 quotes Suh 2005).
4. P03, P11, N01 — **refines** (see synthesis). I-08 (burden reduction
   repeatedly consumed causal margin, n = 7) is a coupled FR pair: the packet
   norm −α² + γ_ll(v + β)² and the demanded stress depend on the same fields.
   The lapse cushion, introduced as "a pure causal-margin compensator", is an
   added DP that decouples them.
5. Transfers as a representation. The information axiom (probability of
   meeting tolerances) has little use before any source exists.

### D2. Jones 2017 (NASA Ames): a balanced assessment

1. H. W. Jones, "Axiomatic Design of Space Life Support Systems", 47th
   International Conference on Environmental Systems, ICES-2017-82,
   Charleston, 16–20 July 2017. **VERIFIED** (full text,
   `work/dd_nasa_ad.txt`).
2. Restates the design-matrix classes and "A good design must be either
   uncoupled or decoupled".
3. Assessment: "Designers are asked to accept the algorithmic approach on
   faith. There is no counter proof that the independence axiom does not
   produce better designs, but most designs are usually coupled to some
   extent. Many mature and evolved designs are strongly coupled and are
   considered good designs by engineers and operators."
4. P03 — scope: independence is a heuristic with broad plausibility, weakly
   evidenced.
5. Transfers with that label.

### D3. Olewnik & Lewis 2003: validity critique

1. A. T. Olewnik & K. E. Lewis, "On Validating Design Decision
   Methodologies", ASME DETC2003/DTM-48669, pp. 747–756,
   DOI 10.1115/DETC2003/DTM-48669. **VERIFIED** (Crossref; full text).
   The later journal version (*Res. Eng. Des.* 2005) is **UNVERIFIED**.
2. Proposes validity criteria for design methods (logical, uses meaningful
   information, does not bias the designer).
3. Finding: axiomatic design "forces the designer to conform to a particular
   preference structure … it also determines the importance (weights) of those
   attributes"; a hair-dryer case shows the bias.
4. P03 — refines: use the design matrix as a map of couplings; keep the
   ranking of designs to explicit requirements.
5. Transfers as a caution.

### D4. Weber, Kößler & Paetzold 2015

1. J. Weber, J. Kößler, K. Paetzold, "An approach for industrial application
   of Axiomatic Design", ICED15, Milan, 27–30 July 2015. **VERIFIED** (full
   text, `work/dd_iced15.txt`).
2. A shortened procedure "applying Suh's independence axiom on the most
   abstract levels during decomposition", "as a kind of approximation in early
   design phases."
4. P03 — supports using the independence check at concept level only.

### D5. Design structure matrix (DSM)

1. D. V. Steward, "The design structure system: A method for managing the
   design of complex systems", *IEEE Trans. Eng. Manage.* **EM-28**(3), 71–74
   (1981), DOI 10.1109/TEM.1981.6448589 (**PARTIAL**). T. R. Browning,
   "Applying the design structure matrix to system decomposition and
   integration problems: a review and new directions", *IEEE Trans. Eng.
   Manage.* **48**(3), 292–306 (2001), DOI 10.1109/17.946528 (**VERIFIED**,
   full text). S. D. Eppinger & T. R. Browning, *Design Structure Matrix
   Methods and Applications*, MIT Press, 2012 (**PARTIAL**).
2. A square matrix of dependencies. Static (component) DSMs are clustered to
   "maximize interactions between elements within clusters … while minimizing
   interactions between clusters"; "any interactions exogenous to the clusters
   should be noticed as interfaces where special attention and verification may
   be required." Time-based (activity) DSMs are sequenced toward a "maximally-
   feed-forward process flow"; "rework results from information arriving at the
   wrong time".
3. Industrial case studies reviewed in Browning; "No single clustering
   approach is a panacea."
4. - P03 — supports (modules as clusters). P10 — supports: cross-cluster
     interactions are the interfaces to verify.
   - P01 ordering and L24 — **refines**: the activity DSM turns "classify
     before sourcing" into a general rule, sequencing activities so the
     information each needs exists before it starts. The four months of source
     work on an unclassified demand is rework from information arriving late.
5. Transfers fully.

### D6. Global sensitivity analysis

1. A. Saltelli, K. Aleksankina, W. Becker, P. Fennell, F. Ferretti, N. Holst,
   S. Li, Q. Wu, "Why so many published sensitivity analyses are false: A
   systematic review of sensitivity analysis practices", *Environ. Model.
   Softw.* **114**, 29–39 (2019), DOI 10.1016/j.envsoft.2019.01.012
   (**VERIFIED**, full text). Also, **PARTIAL** (Crossref only):
   - A. Saltelli et al., *Global Sensitivity Analysis: The Primer*, Wiley,
     2008 (online 2007), DOI 10.1002/9780470725184;
   - I. M. Sobol′, "Global sensitivity indices for nonlinear mathematical
     models and their Monte Carlo estimates", *Math. Comput. Simul.* **55**,
     271–280 (2001);
   - A. Saltelli & P. Annoni, "How to avoid a perfunctory sensitivity
     analysis", *Environ. Model. Softw.* **25**, 1508–1517 (2010);
   - S. Lo Piano et al., "Variance-based sensitivity analysis: The quest for
     better estimators and designs between explorativity and economy",
     *Reliab. Eng. Syst. Saf.* **206**, 107300 (2021).
2. A global method evaluates "the effect of a factor while all others are also
   varying" and must capture interactions, which "arise when the effect of
   changing two factors is different from the sum of their individual
   effects."
3. Bibliometric review; geometric argument: "moving factors OAT in ten
   dimensions leaves over 99.75% of the input space unexplored"; "If all models
   were linear, an OAT or derivative based approach would be adequate." Also:
   "a global SA is a good instrument of model verification", because it tends
   to expose model errors.
4. P17 — **supersedes** one-at-a-time attribution beyond a local derivative.
   The knob map records strong ordering interactions ("shift before stretch
   525 Type IV; stretch before shift 0", `knobs_one_space.md` l.289), exactly
   the non-additivity that OAT cannot see.
5. Transfers. Rail evaluations take seconds to minutes, so variance-based
   designs over a handful of knobs are affordable.

### D7. Morris 1991 elementary effects

1. M. D. Morris, "Factorial Sampling Plans for Preliminary Computational
   Experiments", *Technometrics* **33**(2), 161–174 (1991),
   DOI 10.1080/00401706.1991.10484804. **VERIFIED** (full text).
2. "individually randomized one-factor-at-a-time designs"; the sample of
   "elementary effects" per input classifies inputs as "(a) negligible,
   (b) linear and additive, (c) nonlinear, or (d) involved in interactions".
3. Built for deterministic computational models with many inputs; it avoids
   assumptions of sparsity, monotonicity or low-order polynomial adequacy.
4. P17 — **refines, as the natural upgrade**: repeat each matched one-change
   control from several randomized base designs; the mean gives the effect,
   the spread flags interactions.
5. Transfers directly and cheaply.

### D8. Design of experiments

1. Sources:
   - R. A. Fisher, *The Design of Experiments*, Oliver and Boyd, Edinburgh,
     1935 (**VERIFIED**, Internet Archive full text, §37 "The Single Factor").
   - G. E. P. Box, J. S. Hunter, W. G. Hunter, *Statistics for Experimenters*,
     2nd ed., Wiley, 2005, ISBN 0471718130 (**VERIFIED**, chapter 1 read).
   - V. Czitrom, "One-Factor-at-a-Time versus Designed Experiments", *Am.
     Stat.* **53**(2), 126–131 (1999), DOI 10.1080/00031305.1999.10474445
     (**VERIFIED**, full text).
   - J. Sacks, W. J. Welch, T. J. Mitchell, H. P. Wynn, "Design and Analysis of
     Computer Experiments", *Stat. Sci.* **4**(4), 409–435 (1989),
     DOI 10.1214/ss/1177012413 (**VERIFIED**, full text via OCR).
2. What each says:
   - Fisher: "excessive stress laid on the importance of varying the essential
     conditions only one at a time … We have usually no knowledge that any one
     factor will exert its effects independently of all others";
   - Box–Hunter–Hunter: the "'change one factor at a time' philosophy … is
     unlikely to produce a good result quickly and economically";
   - Czitrom: "Interactions are not estimable from OFAT experiments"; factorial
     designs use all observations for every effect;
   - Sacks et al.: in deterministic computer experiments "Classical notions of
     experimental unit, blocking, replication and randomization are
     irrelevant", and fitted-model adequacy "is determined solely by
     systematic bias."
3. Classical statistical design theory and industrial case studies.
4. - P17 — **truism** for the principle of controls. **Superseded** for
     attribution across factors by factorial or space-filling designs.
   - **Refined** by Sacks for deterministic codes: noise-driven devices
     (randomization, replication) drop out, and discretization bias becomes the
     uncertainty to control. A matched control must therefore match resolution
     and domain as well as design (I-13).
5. Transfers with Sacks' modification.

### D9. Set-based concurrent engineering

1. D. K. Sobek II, A. C. Ward, J. K. Liker, "Toyota's Principles of Set-Based
   Concurrent Engineering", *Sloan Management Review* **40**(2), 67–84 (Winter
   1999) (**PARTIAL**, MIT SMR summary). B. Toche, R. Pellerin, C. Fortin,
   "Set-based design: a review and new directions", *Design Science* **6**, e18
   (2020), DOI 10.1017/dsj.2020.16 (**VERIFIED**, full text).
2. Principles as quoted by Toche et al. from Sobek et al.: "(1) Map the design
   space: define feasible regions; explore trade-offs by designing multiple
   alternatives; communicate sets of possibilities. (2) Integrate by
   intersection … (3) Establish feasibility before commitment: narrow sets
   gradually while increasing detail; stay within sets once committed; control
   by managing uncertainty at process gates." SMR summary: Toyota "delays
   certain decisions longer than other automotive companies do, yet has what
   may be the fastest" development.
3. Evidence is mostly case studies of automakers; the review finds "SBD has a
   relatively low theoretical development", with empirical support cited from
   Camburn et al. for pursuing several alternatives early.
4. P19 (forks) — **supports**: investigating alternatives after one succeeds is
   established practice. F15 (a provisional topology preference requiring
   evidence to change it and none to keep it) — SBCE's "establish feasibility
   before commitment" is the counter-rule.
5. Transfers as a principle; its evidence base is moderate.

### Area 4 synthesis: the rail's knob map as a design matrix

Take the one-space identities from `knobs_one_space.md` (class C0: flat
static slices, A = 1, shift along the track):
- I1: ρ = −(β_r/α)²/32π, with β_r the radial gradient of the shift. The
  shift is the only source of energy density; the lapse enters only as the
  α⁻² suppression of the radial shear;
- I2: where the shift is uniform or zero, K_ij = 0, so ρ = j_i = 0 and
  8πT_ij = (δ_ij D²α − D_iD_jα)/α: the lapse produces stress only, and the
  tensor is Type I;
- P2 of the part list: the packet's speed is set by the shift at its centre.

Take FR₁ = carry speed, FR₂ = energy density in the shift transition,
FR₃ = stress pattern in the shift-free regions. With one global lapse the
design matrix is

| | shift | lapse |
|---|---|---|
| FR₁ carry | X | 0 |
| FR₂ energy density (shift transition) | X | X |
| FR₃ stress (shift-free regions) | 0 | X |

Three FRs on two DPs is coupled by Theorem 1: any lapse change made for FR₃
also moves FR₂. Functional zoning splits the lapse into spatially separate
elements, lapse_T in the shift transition and lapse_F in the shift-free
regions, and the matrix becomes lower triangular:

| | shift | lapse_T | lapse_F |
|---|---|---|---|
| FR₁ carry | X | 0 | 0 |
| FR₂ energy density | X | X | 0 |
| FR₃ stress (shift-free) | 0 | 0 | X |

The zero in the lower-right block holds to the extent that the two lapse
elements do not overlap; their joining region couples them again.

Three consequences follow:
1. The statement "the lapse controls stress without energy; the shift alone
   carries energy density" is exact region by region. Across the whole design
   it describes a **decoupled design with an adjustment order**: fix the shift
   for the carry first, then set lapse_T for energy suppression, and shape the
   shift-free stress with lapse_F.
2. **Functional zoning is the decoupling device** (P03): it raises the DP count
   so that Theorem 1 no longer forces coupling. Axiomatic design also names
   zoning's failure mode, a joining region where two elements overlap. CE-7
   (scrutiny moved off infrastructure phases) is a separate hazard.
3. **N01 (optimizing to a single gate distorts other requirements) is coupling
   plus a single objective.** The remedy is an added DP (the lapse cushion in
   I-08) or a joint objective.

*(Application, mine; the identities are the inventory's, the classification
D1–D2's.)*

---

## Area 5. Stage-gates, readiness and claim scope

### S1. Technology Readiness Levels

1. J. C. Mankins, *Technology Readiness Levels: A White Paper*, NASA Office
   of Space Access and Technology, Advanced Concepts Office, 6 April 1995
   (**VERIFIED**, full text). J. C. Mankins, "Technology readiness
   assessments: A retrospective", *Acta Astronaut.* **65**(9–10), 1216–1223
   (2009), DOI 10.1016/j.actaastro.2009.03.058 (**PARTIAL**, bibliographic).
2. The levels relevant here:
   - TRL 1, "Basic principles observed and reported";
   - TRL 2, "Technology concept and/or application formulated": "the
     application is still speculative: there is not experimental proof or
     detailed analysis to support the conjecture";
   - TRL 3, "Analytical and experimental critical function and/or
     characteristic proof-of-concept", which "must include both analytical
     studies … and laboratory-based studies to physically validate that the
     analytical predictions are correct";
   - TRL 4, "Component and/or breadboard validation in laboratory
     environment".
   Each level lists a cost to achieve, rising by "several factors" per level.
3. Per Mankins, used "on-and-off in NASA space technology planning for many
   years" and "recently incorporated in the NASA Management Instruction
   (NMI 7100)".
4. P18 — comparison below; P01 2a — the cost escalation per level is the
   stage-gate rationale.
5. See comparison.

### S2. NASA Systems Engineering Handbook (2016)

1. NASA, *NASA Systems Engineering Handbook*, NASA/SP-2016-6105 Rev2 (2016;
   supersedes Rev1, 2007), nasa.gov. **VERIFIED** (full text).
2. Content used:
   - **MOE**: "A measure by which a stakeholder's expectations are judged in
     assessing satisfaction with products or systems … critical to not only
     the acceptability of the product … but also critical to operational/mission
     usage."
   - **MOP**: "A quantitative measure that, when met by the design solution,
     helps ensure that a MOE … will be satisfied … There are generally two or
     more measures of performance for each MOE."
   - **TPM**: "monitored by comparing the current actual achievement of the
     parameters with that anticipated at the current time and on future
     dates."
   - **TRL**: "at its most basic, a description of the performance history of
     a given system, subsystem, or component".
   - **AD2** (Advancement Degree of Difficulty): "The process to develop an
     understanding of what is required to advance the level of system
     maturity."
   - **Interface management**, with interface requirements documents and ICDs.
3. Agency standard practice.
4. - P12 — **truism** in systems engineering: occupant quantities are the MOEs
     of a crewed transport. Its domain content is the list (clock rate, tides,
     proper acceleration) and the reason the list was needed (the 55× clock).
   - P15 — **refines**: define one MOE from the passenger's and operator's
     viewpoint, then its MOPs within the geometry (arrival against light through
     the same exterior, L20). "Single operational measure" becomes "one MOE,
     several MOPs, each defined once" (I-02, I-03).
   - P10 — **truism** for the practice half (interface control).
   - P18 — TRL measures maturity, AD2 measures difficulty; the claim ladder
     conflates the two.
5. Transfers.

### S3. GAO Technology Readiness Assessment Guide

1. U.S. GAO, *Technology Readiness Assessment Guide: Best Practices for
   Evaluating the Readiness of Technology for Use in Acquisition Programs and
   Projects*, GAO-20-48G, January 2020 (reissued with revisions 11 February
   2020). **VERIFIED** (GAO summary page).
2. Best practices for credible, objective, reliable and useful assessments
   of critical technologies.
3. "Technologies that are not adequately mature have led to program delays and
   cost increases."
4. P18 — supports readiness assessment as standard practice.

### S4. Cooper 1990, stage-gate systems

1. R. G. Cooper, "Stage-gate systems: A new tool for managing new products",
   *Business Horizons* **33**(3), 44–54 (1990),
   DOI 10.1016/0007-6813(90)90040-I. **VERIFIED** (full text, OCR of pages
   1–5 of the author's upload).
2. "Each gate is characterized by a set of deliverables or inputs, a set of exit
   criteria, and an output … typically a Go/Kill/Hold/Recycle decision";
   gates are "manned by senior managers who act as 'gatekeepers'" with
   authority over resources. "Each stage is usually more expensive than the
   preceding one. Concurrently, information becomes better and better, so risk
   is managed."
3. Evidence cited: a Booz, Allen & Hamilton (1982) study found firms with a
   formal process "did better". The evidence is correlational.
4. - P01 2a (check cheap necessary conditions first) — **truism**.
   - P19 and F4/F14/A8 (written stopping rules bypassed on the day they
     applied) — **refines**: a gate needs named exit criteria, a "Recycle"
     branch (compare CE-5: pre-registered branches that offered only
     source-side remedies), and a gatekeeper with authority over the next stage.
5. Transfers as process design; the book gives it a paragraph.

### S5. Fusion's evidence ladder

1. Sources:
   - J. D. Lawson, "Some Criteria for a Power Producing Thermonuclear Reactor",
     *Proc. Phys. Soc. B* **70**(1), 6–10 (1957),
     DOI 10.1088/0370-1301/70/1/303 (**PARTIAL**).
   - S. E. Wurzel & S. C. Hsu, "Progress toward fusion energy breakeven and
     gain as measured against the Lawson criterion", *Phys. Plasmas* **29**,
     062103 (2022), DOI 10.1063/5.0083990, arXiv:2105.10954 (**VERIFIED**,
     full text).
   - H. Abu-Shawareb et al. (Indirect Drive ICF Collaboration), "Achievement
     of Target Gain Larger than Unity in an Inertial Fusion Experiment",
     *Phys. Rev. Lett.* **132**, 065102 (2024) (**VERIFIED**, abstract).
   - M. S. Tillack et al. (ARIES Team), "An Evaluation of Fusion Energy R&D Gaps
     Using Technology Readiness Levels", *Fusion Sci. Technol.* **56**(2),
     949–956 (2009), DOI 10.13182/FST09-A9033 (**PARTIAL**, bibliographic);
     content from Tillack's Fusion Power Associates presentation of 4 December
     2008 (fire.pppl.gov, **VERIFIED**).
2. A nested gain chain, each level charging more of the supply chain:
   - Q_fuel, "Ratio of fusion power to power absorbed by the fuel";
   - Q_sci, "Ratio of fusion power to externally applied heating power";
   - Q_eng, "Ratio of electrical power to the grid to recirculating power",
     with Q_eng = η_elec η_E(Q_sci + 1) − 1;
   - Q_wp, "Ratio of fusion power to input electrical power from the grid".
   Representative efficiencies differ by class; for laser ICF η_E ≈ 0.1.
   "Q_sci is the better metric for assessing remaining physics risk";
   "Scientific breakeven … signifies that very significant (but not all)
   plasma-physics challenges have been retired"; "We regard the eventual
   demonstration of Q_wp = 1 (not Q_fuel or Q_sci = 1) as the so-called 'Kitty
   Hawk moment'". The Lawson criterion "is only one of many equally important
   factors". NIF: "target gain G_target of 1.5 … 2.05 MJ of 351 nm laser light
   produced 3.1 MJ of total fusion yield", labelled "scientific breakeven". The
   facility's wall-plug energy per shot was not fetched (**UNVERIFIED**; no
   figure is used here). Tillack: TRLs "express increasing levels of
   integration and environmental relevance, terms which must be defined for
   each technology application", with issue-specific level definitions per
   subsystem.
3. Six decades of fusion programmes; the gain definitions are standard.
4. - P08 (net supply) — **supports with a better method**: define nested
     supply ratios, one per accounting boundary, and name which one a claim
     reaches. The Casimir-mirror incidents (mirror hardware carrying about 10⁷
     times its deficit; L2, E10) are Q_sci-versus-Q_wp confusions.
   - P15 — supports explicit gain definitions to prevent conflation.
   - P18 — **refines**: the chain is a ladder of accounting boundaries, the
     closest analogue of "supplied stress → finite closure"; Tillack shows
     generic levels must be rewritten per subsystem.
   - P07 — the Lawson criterion is a magnitude screen applied before device
     design. Supports.
5. Transfers as structure. Fusion has experiments at every rung; the rail has
   none.

### S6. Millis, NASA Breakthrough Propulsion Physics

1. M. G. Millis, *Assessing Potential Propulsion Breakthroughs*,
   NASA/TM—2005-213998, Glenn Research Center, December 2005 (NTRS
   20060000022). **VERIFIED** (full text). Companion items **PARTIAL** (search
   metadata only): Millis, *Breakthrough Propulsion Physics Project: Project
   Management Methods*, NASA/TM—2004-213406; Millis, *Ann. N.Y. Acad. Sci.*
   **1065**, 441 (2005), DOI 10.1196/annals.1370.023. Hord (1985), cited by
   Millis for the readiness adaptation: **UNVERIFIED**.
2. Methods:
   - **Applied Science Readiness Levels**: "the Scientific Method can be
     adapted as a readiness scale"; three stages (General Physics, Critical
     Issues, Desired Effect) each repeat "Problem formulated / Data collected /
     Hypothesis proposed / Hypothesis tested & results reported", giving "15
     levels of relative maturity, with the most advanced level being equivalent
     to Technology Readiness Level 1";
   - scope each task to "the minimum level of effort needed to resolve an
     immediate 'go/no-go' decision", in one to three years;
   - diversify the portfolio;
   - review for credibility rather than feasibility: "judging credibility
     rather than pre-judging feasibility";
   - "Success is defined as acquiring reliable knowledge, rather than as
     achieving a breakthrough";
   - publish results "regardless of outcome";
   - on metrics: "When using the metrics of an incumbent technology to assess
     the potential of a new technology, results can be misleading"
     (infinite specific impulse for a propellantless drive "has no real
     meaning").
3. Lessons from the BPP project's solicitations and reviews, 1996–2002.
4. - P18 — **refines**: the adjacent field's evidence scale for exactly this
     regime; see the comparison below.
   - P19 — supports go/no-go increments and portfolio diversity.
   - L12, F13 (negative verdicts dropped from summaries) — supports publishing
     null results.
   - P15, I-03, L20 — supports: performance metrics must be defined for the
     new mechanism.
5. Transfers nearly whole.

### S7. False positives in propulsion anomaly testing

1. M. Tajmar, O. Neunzig, M. Weikert, "High-accuracy thrust measurements of
   the EMDrive and elimination of false-positive effects", *CEAS Space J.*
   **14**(1), 31–44 (2022; online 2021), DOI 10.1007/s12567-021-00385-1.
   **VERIFIED** (full text). The 2019 *Acta Astronautica* SpaceDrive paper is
   **UNVERIFIED** (not fetched).
2. A thruster with "significant thermal and mechanical load as well as high
   electric currents … can create numerous artefacts that produce false-
   positive thrust values." Controls: an inverted counterbalanced double
   pendulum "to eliminate most thermal drift effects" and battery power "to
   remove undesired interactions due to feedthroughs."
3. Result: no thrust; limits "rule out previous test results by at least two
   orders of magnitude."
4. P17 — supports: attribution in a speculative field requires controls
   designed against named artefacts. The computational analogues are
   numerical artefacts read as physics (C1, L11, E17 in the September
   inventory).
5. Transfers as the principle "name the artefact, design the control".

### S8. Lamport 1978: coordination under relativistic causality

1. L. Lamport, "Time, Clocks, and the Ordering of Events in a Distributed
   System", *Commun. ACM* **21**(7), 558–565 (1978),
   DOI 10.1145/359545.359563. **VERIFIED** (full text).
2. The happened-before partial order; "In relativity, the ordering of events is
   defined in terms of messages that could be sent." Physical clocks "running
   quite independently of one another" can satisfy the Strong Clock Condition
   with bounded drift and synchronization error, where the minimum
   inter-process delay μ can be "the shortest distance between processes
   divided by the speed of light."
3. The foundation of distributed-systems ordering.
4. P14 (causal operations; coordination by planned timing and local fallback)
   — **supports**: pre-synchronized clocks with bounded drift are the
   established way to coordinate separated hardware without signals faster
   than the causal bound.
5. Transfers for the choreography's timing layer. Clock rates on a lapse
   profile must be converted to the chosen time function, as Lamport's own
   footnote requires "if the relative motion of the clocks or gravitational
   effects are not negligible".

### Comparison: the project's claim ladder against adjacent ladders

The project's ladder (SOURCE_FEASIBILITY_WORKFLOW.md): **algebraic target**
(allocation of the demanded G/8π) → **positive spectrum** (a field theory's
modes are well behaved) → **supplied stress** (a normalized source delivers
the demand) → **finite closure** (a finite assembly closes the budget with
interfaces and exchanges) → **coupled dynamics** (preparation, handoff and
recovery evolve consistently). The mapping below is mine.

| Claim-ladder rung | V&V tier (V9) | Fusion (S5) | Readiness (S1, S6) | Credibility dimension missing from the rung |
|---|---|---|---|---|
| Algebraic target | code verification of the demand kernel | Lawson requirement stated | SRL 2.0–2.2 (critical issue formulated) | global structure, type, occupant MOEs (PCMM representation fidelity) |
| Positive spectrum | model well-posedness | stability of a confined plasma | SRL 2.3 | solution verification |
| Supplied stress | unit problem | Q_fuel / Q_sci | SRL 2.4 (tested analytically) | input pedigree: every relaxation listed (F8) |
| Finite closure | benchmark / subsystem tiers | Q_eng | SRL 3.x; TRL 2 | complete-ledger accounting (L14) |
| Coupled dynamics | complete system (simulated) | burn dynamics, Q_wp | TRL 2, short of TRL 3 (no laboratory test) | robustness and sensitivity (V13, D6) |

Findings from the comparison:
1. **Every rung is analytic or computational.** Mankins places laboratory
   validation at TRL 3, so the whole ladder lies at or below TRL 2, and inside
   Millis's SRL scale (below TRL 1 for new physics). The book should say so
   and adopt an SRL-like scale for its claim language.
2. **The ladder is a validation hierarchy without validation.** Its structure
   (component → pair → assembly → coupled system) matches V9's tiers, which
   supports it. It also inherits V9's warning: lower tiers reduce coupling, so
   passes there say little about the coupled system.
3. **A single ladder hides breadth failures.** PCMM and NASA-STD-7009 rate
   several independent dimensions at each maturity level. CE-2 (depth on one
   rung, breadth missing) is the failure a matrix exposes. Better method: keep
   the ladder as the maturity axis and add credibility columns (global
   structure, type, occupant MOEs, numerical uncertainty, relaxations,
   independent review).
4. **Report each claim with the 7009 template**: best estimate, uncertainty,
   credibility assessment, caveats (violated assumptions), risk of acting on
   it.
5. **Name accounting boundaries as fusion does.** "Supplied stress" and
   "finite closure" correspond to Q_sci and Q_eng; naming the boundary each
   claim reaches prevents the P08 and P15 conflations.
6. **Maturity and difficulty are separate axes (AD2).** The ladder records
   how far a candidate has come; a separate estimate should record what the
   next rung costs.

---

## Area 6. Analogue gravity as a laboratory-engineering neighbour

### A1. Barceló, Liberati & Visser, *Analogue Gravity*

1. C. Barceló, S. Liberati, M. Visser, "Analogue Gravity", *Living Rev.
   Relativ.* **8**, 12 (2005), DOI 10.12942/lrr-2005-12; **14**, 3 (2011),
   DOI 10.12942/lrr-2011-3; revised edition **29**, 2 (30 June 2026),
   DOI 10.1007/s41114-026-00064-9. Text read: arXiv:gr-qc/0505065v4
   (29 November 2024, "Major revision, updated and expanded"). **VERIFIED**
   (full text of v4; Crossref for all three editions; the identity of v4 with
   the 2026 edition was not checked).
2. Content used:
   - the acoustic metric is an ADM-form metric whose lapse is set by the sound
     speed c_s and whose shift is the flow velocity (the covariant metric has
     g₀₀ ∝ −(c_s² − v²) and g₀ⱼ ∝ −v_j);
   - it has "at most, 3 degrees of freedom per point", reduced to 2 by
     continuity, so it "can, at best, reproduce some subset of the generic
     metrics of interest in general relativity";
   - "in Einstein gravity the spacetime metric is related to the distribution
     of matter by the nonlinear Einstein–Hilbert differential equations. In
     contrast, in the present context, the acoustic metric is related to the
     distribution of matter in a simple algebraic fashion";
   - Hawking emission "is a kinematic effect that does not rely on Einstein's
     equations"; laboratory Hawking experiments "are purely kinematic
     experiments that do not probe the dynamics of the effective spacetime";
   - modified dispersion (breakdown of the analogy at short scales) leaves the
     Hawking spectrum approximately intact for dispersion scales well above the
     surface gravity (§5.1.2).
3. The standard review of the field, now in its third edition.
4. - P02, P18 — supports the kinematic/dynamic distinction as a claim
     boundary: horizon kinematics, ray trapping and mode conversion can be
     studied in any medium; the demand (G/8π) cannot.
   - L5 (a reduced model forbids failure modes) — supports: an analogue
     realizes a restricted subset of metrics, so a result there certifies only
     that subset.
   - Knob vocabulary — supports reading the shift as flow and the lapse as
     signal speed (with T12).
5. Transfers: a laboratory route to *kinematic* checks of rail features
   (horizon formation at α² = b² surfaces, front trapping, blue-shifting at a
   white-hole front). Does not transfer: any test of source feasibility.

### A2. Unruh 1981

W. G. Unruh, "Experimental Black-Hole Evaporation?", *Phys. Rev. Lett.* **46**,
1351–1353 (1981), DOI 10.1103/PhysRevLett.46.1351. **PARTIAL**
(bibliographic). The founding proposal cited throughout A1.

### A3. Laboratory analogues

1. S. Weinfurtner, E. W. Tedford, M. C. J. Penrice, W. G. Unruh,
   G. A. Lawrence, "Measurement of stimulated Hawking emission in an analogue
   system", *Phys. Rev. Lett.* **106**, 021302 (2011), arXiv:1008.1911.
   J. Steinhauer, "Observation of quantum Hawking radiation and its
   entanglement in an analogue black hole", *Nat. Phys.* **12**, 959 (2016),
   arXiv:1510.00621. T. G. Philbin, C. Kuklewicz, S. Robertson, S. Hill,
   F. König, U. Leonhardt, "Fiber-Optical Analog of the Event Horizon",
   *Science* **319**, 1367–1370 (2008), arXiv:0711.4796. **VERIFIED**
   (abstracts).
2. Water waves: long waves blocked and converted at a white-hole horizon, with
   "the thermal nature of the conversion process". BEC: spontaneous Hawking
   pairs, entangled at high energy; results "consistent with a driven
   oscillation experiment and a numerical simulation". Fibre: "the
   blue-shifting of light at a white-hole horizon".
3. Laboratory measurements with stated controls and simulations.
4. P18 — these are the only experiments that test consequences of
   horizon-bearing effective metrics; a rail feature with a white-hole-like
   front (E11 in the September inventory) has laboratory precedent for its
   kinematics.
5. Transfers as validation of kinematic predictions only.

### Area 6 synthesis

Analogue gravity is the neighbour field that already engineers effective
metrics in the laboratory. It supplies the claim boundary the book needs:
kinematic predictions can be tested in media; dynamic claims (source
feasibility, back-reaction) cannot. It also confirms the design vocabulary of
T12, sound speed as lapse and flow as shift.

---

## Incident lessons that adjacent fields already name

| Incident lesson (inventory code) | Adjacent practice | Source | Verdict for the lesson |
|---|---|---|---|
| Fitted closures and oracle partitions always "close" (I-11, CE-3) | Calibration ≠ validation; MMS source terms are manufactured | V9, V5 | Established; cite |
| "Independent" audit with the omitted term switched off (C10, F1) | Manufactured tests with fully general coefficients | V6 | Established; cite |
| Reproducing reference audits carried errors forward (F9) | Regression tests certify consistency, verification certifies correctness | N4, V6 | Established; cite |
| Convergence and precision on the wrong questions (CE-2, F2, F3) | "converge to a physically irrelevant solution"; constraints not in isolation; breadth over depth | N2, V14 | Established; cite |
| Refinement effort unrelated to the decision (F3, C2) | Rigor commensurate with decision consequence | V12, N5 | Established; cite |
| Stacked relaxations with no ledger (F8) | Caveats and input pedigree; simplified designs re-verified | V13, T6, T9 | Established; cite |
| Label inflation (I-17) | Name results by the check passed; confirmation is partial | V16, V13 | Truism with citations |
| Frame-blind internal review (CE-1, CE-6) | Verification cannot detect conceptual-model error; reviewer independence | V9, V13 | Established; cite |
| Sign boundaries between samples (I-07, L4) | Interval enclosures | V15 | Better method |
| Local fix relocates a fixed deficit (L23) | Passive-cloak sum rule | T11 | Analogy only |
| Realizability inside inverse optimization (L18) | Penalization, filters, robust formulations | T13, T14 | Established; cite |
| Class-level bounds before construction (L1) | Bode–Fano and causality bounds; Lawson criterion | T11, S5 | Established; cite |
| Hardware cost of the supply (L2, E10) | Nested gains Q_sci / Q_eng / Q_wp | S5 | Better method |
| Burden reduction consumed causal margin (I-08, N01) | Coupled FRs; decouple by added DP or joint objective | D1 | Established framing |
| Ordering interactions between knobs (knob map (c)) | Interaction effects; OAT blind to them | D6–D8 | Better method |
| Written stopping rules bypassed (A8, F14) | Gatekeepers with authority; Go/Kill/Hold/Recycle | S4 | Established; cite |
| Negative verdicts dropped from summaries (L12, F13) | Publish results regardless of outcome | S6 | Established; cite |
| Incumbent metrics mislead (I-03, L20) | MOE/MOP definitions; metrics fit to the new mechanism | S2, S6 | Established; cite |
| Artefacts read as physics (C1, L11, E17) | Controls designed against named artefacts | S7, V6 | Established; cite |

---

## Unverified and partial items

**UNVERIFIED** (carry no weight):
- "Chen, Liang & Alù" on cloaking limits (no such paper found);
- Post & Votta (2005), defect rates (quoted by N3 only);
- ASME V&V 10-2006 *Guide* history (search snippet only);
- Olewnik & Lewis (2005) journal version;
- Suh (1998) *Res. Eng. Des.*;
- Ward et al. (1995), "The second Toyota paradox";
- de Neufville & Scholtes (2011);
- NPR 7123.1;
- Hord (1985);
- Tajmar et al. SpaceDrive (2019) *Acta Astronautica*;
- Leonhardt & Philbin (2009) *Prog. Opt.*;
- Kildishev et al. (2008) *NJP*;
- Jensen & Sigmund (2011);
- Cassier & Milton (2017);
- Gundlach et al. (2005) constraint damping;
- the NIF facility's wall-plug energy per shot.

**PARTIAL** (bibliographic data confirmed; content from a named secondary
source or a summary):
- area 1: Roache 1998; Celik et al. 2008; Richardson 1911 and 1927; Oberkampf
  & Roy 2010/2025; Roy 2005; AIAA G-077; ASME V&V 20 (through the Sandia
  overview); ASME V&V 10-2019; Tucker 2011; Moore et al. 2009;
- area 3: Gordon 1923; Plebański 1960; Fano 1950; Bendsøe & Kikuchi 1988;
  Bendsøe & Sigmund 2003; Sigmund & Petersson 1998; Zhou et al. 2004; Chen,
  Chan & Sheng 2010;
- area 4: Suh 1990 and 2001 (content through the MIT OCW notes); Steward 1981;
  Eppinger & Browning 2012; Saltelli et al. 2008; Sobol′ 2001; Saltelli &
  Annoni 2010; Lo Piano et al. 2021; Sobek, Ward & Liker 1999;
- area 5: Mankins 2009; Lawson 1957; Tillack et al. 2009 (content through the
  2008 presentation); Millis 2004 and the 2005 NYAS paper;
- other: Unruh 1981; Buckingham 1914 (below).

E. Buckingham, "On Physically Similar Systems; Illustrations of the Use of
Dimensional Equations", *Phys. Rev.* **4**, 345–376 (1914),
DOI 10.1103/PhysRev.4.345 (**PARTIAL**), is the citation for P04's
dimensional-analysis core.

---

## Closing table: candidate × adjacent-field practice × verdict

Verdicts: **truism** (standard practice elsewhere; one sentence in the book);
**supported** (established backing for the candidate as stated);
**refined** (backing with a sharper or narrower statement);
**superseded** (a better method exists and should be taught);
**contradicted**. A candidate can carry several rows.

| Candidate | Adjacent-field practice (source) | Verdict |
|---|---|---|
| P01 ordering: cheap necessary checks before costly construction | Stage-gates, rising stage cost (S4); TRL cost escalation (S1) | Truism |
| P01 ordering as information flow | Activity DSM sequencing; rework from late information (D5) | Refined |
| P01 2e between-sample verification | Interval enclosures (V15) | Superseded (root-finding along lines → interval certification) |
| P01 2g type as matching criterion | Transformation family matched to available material: calcite (T10); map chosen to minimize the hard component (T7) | Supported |
| P01 2i / N01 single-gate optimization distorts | Coupled FRs under one objective (D1); passive sum rule (T11, analogy) | Supported |
| P02 metric-first specification | Transformation optics (T1, T12); MMS computes the same source term (V5) | Supported |
| P02 metric-first as sufficient method | TO + inverse design hybrid (T14); in-loop realizability (T13); simplification needs forward check (T4, T6, T9) | Refined |
| P03 functional zoning | Axiomatic design: zoning as block-decoupling; adjustment order (D1, D2); DSM clustering (D5) | Refined |
| P03 zoning hazard (CE-7) | Validation hierarchy keeps a complete-system tier (V9) | Supported (as hazard) |
| P04 scale-free normalization | Dimensional analysis (Buckingham 1914) | Truism |
| P04 fix the absolute scale before magnitude comparison | Lawson criterion as absolute threshold (S5); delay–bandwidth scaling with size (T11) | Supported |
| P05 C∞ joins | Adiabatic transitions remove reflection (T11); boundary sensitivity (T6); length scales for existence (T13); smooth manufactured solutions for order tests (V6); sharp transitions give spurious violations (N7) | Refined (smoothness order set by the analysis' highest derivative; C∞ a convenient sufficient choice) |
| P06 topology accounting early | Topology at concept stage, shape and size later (T13); topology choice removed singular demand (T7) | Supported |
| P07 in-principle exclusions before magnitudes | Bode–Fano, causality and passivity bounds (T11); bounds guide inverse design (T14); go/no-go increments (S6) | Supported |
| P08 net supply counts supply hardware | Nested gains Q_fuel → Q_sci → Q_eng → Q_wp (S5) | Supported; refined by named accounting boundaries |
| P09 complete component tensors | Complete force accounting (general practice); fully general manufactured tests (V6) | Truism (accounting); supported (testing) |
| P10 interaction contract | Interface management, ICDs (S2); cross-cluster interfaces need verification (D5) | Truism (practice half); physics half out of scope |
| P10 one shared geometry for overlaps | Validation tiers: coupled tier required beyond components (V9) | Supported |
| P11 geometric vs mechanical continuity | Functional vs physical domains (D1) | Supported (as FR/DP distinction; the architecture choice stays project-specific) |
| P12 occupant quantities as primary outputs | Measures of effectiveness (S2) | Truism (practice); domain list is content |
| P13 accounting for what a moving structure overtakes | No adjacent-method source; physics literature | Not assessed here |
| P14 causal operations, coordination without FTL signals | Happened-before order; independently running synchronized clocks (S8) | Supported |
| P15 single operational performance measure | One MOE with derived MOPs (S2); gain definitions (S5); incumbent metrics mislead (S6); accuracy tied to use (N5) | Refined |
| P16 convergence and refinement ladders | Richardson, GCI, observed order (V2–V4); NR convergence testing (N1–N3) | Truism (core); superseded ("refinement-stable" → observed order + GCI + asymptotic check) |
| P16 independent kernels | Comparison tests are a low rung; common errors pass (V6, N2) | Superseded (→ MMS with order-of-accuracy; independent residuals, N1) |
| P16 conserved quantities | Consistency-level evidence (V6); Bianchi residual (area 1 synthesis) | Refined |
| P16 regression reproduction | Regression ≠ verification (N4) | Refined |
| P17 matched controls | Controls as principle (D8) | Truism |
| P17 one-change attribution across a design space | Factorial designs (D8); variance-based GSA (D6); Morris elementary effects (D7); deterministic-code design (D8, Sacks) | Superseded |
| P17 attribution against artefacts | Controls against named artefacts (S7) | Supported |
| P18 claim ladder | Validation hierarchy (V9); TRL (S1); SRL (S6); fusion gain chain (S5) | Supported (structure) |
| P18 claim ladder as sole credibility structure | PCMM matrix (V14); 7009 factors and reporting template (V13); risk-commensurate rigor (V12); maturity vs difficulty (S2, AD2) | Refined |
| P18 kinematic vs dynamic claim scope | Analogue gravity (A1); TO kinematic only (T12) | Supported |
| P19 forks | Set-based concurrent engineering (D9); portfolio diversity (S6) | Supported |
| P19 stopping rules | Go/Kill/Hold/Recycle with gatekeepers (S4); minimal go/no-go tasks (S6) | Supported; refined (gatekeeper authority, recycle branch) |
| N01 optimizing to a single gate | Coupled design under one objective (D1); in-loop constraints (T13) | Supported |

No adjacent-field source **contradicts** a candidate. The closest to a
contradiction is D2–D3: independence is a heuristic, and mature good designs
are often coupled, so P03 cannot be stated as a law.
