Sources in this section were verified by a delegated search (26 items; extracts in
`inventory/work/dd_*.txt`); two load-bearing quotes (Suh on decoupled designs, Saltelli
et al. 2019 on OAT) were re-fetched and confirmed for this survey.

### 4.1 Suh: axiomatic design, the design matrix and the independence axiom

1. **Citations.** N. P. Suh, *The Principles of Design*, Oxford University Press, 1990,
   ISBN 0-19-504345-6. **PARTIAL** (bibliographic). N. P. Suh, *Axiomatic Design: Advances
   and Applications*, Oxford University Press, 2001, ISBN 0-19-513466-4. **PARTIAL**
   (bibliographic; content via MIT OCW 2.800 slides drawn from it). N. P. Suh, "Axiomatic
   design theory for systems", *Res. Eng. Des.* 10, 189–209 (1998), DOI
   10.1007/s001639870001. **PARTIAL** (abstract). N. P. Suh, "Chapter 1: Introduction to
   Axiomatic Design", MIT course text, 1996, web.mit.edu/2.882/www/chapter1/chapter1.htm.
   **VERIFIED** (re-fetched).
2. **Practice.** "Axiom 1: The Independence Axiom. Maintain the independence of the
   functional requirements (FRs). Axiom 2: The Information Axiom. Minimize the information
   content of the design." Design equation {FR} = [A]{DP}, A_ij = ∂FR_i/∂DP_j. "When the
   design matrix [A] is diagonal, each of the FRs can be satisfied independently by means of
   one DP. Such a design is called an uncoupled design. When the matrix is triangular, the
   independence of FRs can be guaranteed if and only if the DPs are changed in a proper
   sequence. Such a design is called a decoupled or quasi-coupled design." All other
   matrices are coupled. Decomposition zigzags between the "what" domain (FRs) and the
   "how" domain (DPs) level by level. Theorem 1: "to satisfy the independence of a given set
   of FRs, the number of DPs must be at least equal to the number of FRs."
3. **Rationale.** Axiomatic: "Self-evident truth or fundamental truth for which there are
   no counter examples or exceptions." The support is argument and case examples, not a
   controlled study (see 4.2).
4. **Bearing.** P03 (functional zoning): *supports and formalizes*. P11 (geometric vs
   mechanical continuity): *refines*; continuous rail geometry is an FR-level statement
   about service, mechanical independence of modules is a DP-level choice, so the
   distinction is architectural (a design decision) rather than a result.
   Knob map, derived for this survey *(inference, derivation below)*: on flat, stationary
   slices the Eulerian energy density depends on the shift and on the lapse only as a
   factor 1/α² where the shift is nonzero, while the stress depends on both. The design
   matrix for (FR₁ = energy density, FR₂ = stress; DP₁ = shift, DP₂ = lapse) is therefore
   triangular wherever α is constant across the shift's support, and Suh's rule gives the
   adjustment order: set the shift for the energy-density requirement, then the lapse for
   stress. Functional zoning that keeps lapse variation off the shift's support is what
   makes the matrix triangular.
5. **Transfer.** The design matrix transfers with an advantage over mechanical design: its
   entries are exact derivatives of demand functionals with respect to profile parameters
   and can be computed rather than estimated. Non-transfer: the information axiom's
   success probabilities have no clear counterpart; the matrix depends on the operating
   point (a nonlinear design in Suh's terms), so triangularity must be checked across the
   operating envelope.

**Derivation for the knob map.** With γ_ij = δ_ij and ∂_tγ_ij = 0, the extrinsic curvature
is K_ij = (∂_iβ_j + ∂_jβ_i)/(2α) (sign conventions differ; only quadratic forms enter
below). The Hamiltonian constraint with R⁽³⁾ = 0 gives
16πρ = K² − K_ijK^ij = α⁻²[(∂_kβ^k)² − ¼(∂_iβ_j + ∂_jβ_i)(∂^iβ^j + ∂^jβ^i)].
Hence ρ = 0 when β = 0 for any lapse, and ρ scales as α⁻² where β ≠ 0. For β = 0 and a
static lapse, the evolution equation with K_ij = 0 and R_ij = 0 reduces to
S_ij − ½δ_ij S = −(8πα)⁻¹ ∂_i∂_jα: stress without Eulerian energy density. The momentum
density 8πj_i = ∂_jK^j_i − ∂_iK vanishes for β = 0, consistent with P01 (2c). These are
Eulerian quantities; the complete-tensor, all-observer statement of P01 still governs
admissibility.

### 4.2 Critiques and assessments of axiomatic design

1. **Citations.** A. T. Olewnik and K. Lewis, "On validating engineering design decision support
   tools", *Concurrent Engineering* 13(2), 111–122 (2005),
   DOI 10.1177/1063293X05053796 (the requested attribution to *Research in Engineering
   Design* is incorrect). **VERIFIED** (abstract; full text of the 2003 DETC precursor).
   D. D. Frey, E. Jahangir, F. Engelhardt, "Computing the information content of decoupled
   designs", *Res. Eng. Des.* 12, 90–102 (2000), DOI 10.1007/s001630050025. **VERIFIED**
   (abstract). D. D. Frey and C. L. Dym, "Validation of design methods: lessons from
   medicine", *Res. Eng. Des.* 17, 45–57 (2006), DOI 10.1007/s00163-006-0016-4. **VERIFIED**
   (abstract).
2. **Findings.** Olewnik & Lewis: both House of Quality and Axiomatic Design "are shown to
   violate some portion of the proposed definition of validity"; their own caveat: "The
   empirical results in this paper should not be thought of as analytical proofs." Frey et
   al.: "information cannot be summed for decoupled designs," and "decoupled designs can
   have lower information content than uncoupled systems." Frey & Dym propose validation
   of design methods on the model of clinical studies.
3. **Rationale.** Design methods themselves need validation evidence.
4. **Bearing.** P03: *limits the support*; the independence axiom is a well-argued
   heuristic without controlled validation, and the book should present decoupling as a
   design aid whose value in spacetime engineering is shown by the derived knob map, not by
   the axiom's authority.
5. **Transfer.** The caution transfers.

### 4.3 The design structure matrix

1. **Citations.** D. V. Steward, "The design structure system: a method for managing the
   design of complex systems", *IEEE Trans. Eng. Manage.* EM-28(3), 71–74 (1981), DOI
   10.1109/TEM.1981.6448589. **VERIFIED** (abstract). T. R. Browning, "Applying the design
   structure matrix to system decomposition and integration problems: a review and new
   directions", *IEEE Trans. Eng. Manage.* 48(3), 292–306 (2001), DOI 10.1109/17.946528.
   **VERIFIED** (full text). S. D. Eppinger, D. E. Whitney, R. P. Smith, D. A. Gebala, "A
   model-based method for organizing tasks in product development", *Res. Eng. Des.* 6(1),
   1–13 (1994), DOI 10.1007/BF01588087. **VERIFIED** (abstract). S. D. Eppinger and T. R.
   Browning, *Design Structure Matrix Methods and Applications*, MIT Press, 2012, DOI
   10.7551/mitpress/8896.001.0001. **PARTIAL** (description).
2. **Practice.** Steward: "Systems design involves the determination of interdependent
   variables. Thus precedence ordering for tasks determining these variables involves
   circuits. Circuits require planning decisions about how to iterate and where use
   estimates." Browning: partitioning ("to minimize feedbacks and their scope by
   restructuring … by resequencing the rows and columns"); tearing ("choosing certain
   dependencies about which to make assumptions … The least-damaging assumptions are made
   first, and their marks are temporarily removed or 'torn'"); clustering ("maximize
   interactions between elements within clusters … while minimizing interactions between
   clusters"; "No single clustering approach is a panacea").
3. **Rationale.** "When activities begin work without the necessary information, the
   arrival or change of that information causes rework" (Browning). Evidence is field
   modelling in several organizations (Eppinger et al.).
4. **Bearing.** P01 (2a) and P02: *supports with a mechanism*. *(inference)* The May–September
   source work depended on the geometry through a feedback mark (the complete-demand
   classification); the frozen reference geometry was a tear, an assumption made to let
   source work proceed. DSM practice makes such tears explicit and orders the least
   damaging first, which is the formal version of "classify the complete demand before
   source work." P10 and P03: *supports*; C1 modules correspond to DSM clusters, and the
   overlap interfaces are the inter-cluster marks that the interaction contract governs.
5. **Transfer.** Directly, for research tasks and for component coupling. The book can
   show the rail's task DSM with its tears labelled.

### 4.4 Global sensitivity analysis

1. **Citations.** A. Saltelli et al., *Global Sensitivity Analysis: The Primer*, Wiley,
   2008, DOI 10.1002/9780470725184. **PARTIAL** (description). I. M. Sobol', "Global
   sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates",
   *Math. Comput. Simul.* 55(1–3), 271–280 (2001), DOI 10.1016/S0378-4754(00)00270-6.
   **PARTIAL** (bibliographic). A. Saltelli and P. Annoni, "How to avoid a perfunctory
   sensitivity analysis", *Environ. Model. Softw.* 25(12), 1508–1517 (2010), DOI
   10.1016/j.envsoft.2010.04.012. **PARTIAL** (bibliographic). A. Saltelli et al., "Why so
   many published sensitivity analyses are false: a systematic review of sensitivity
   analysis practices", *Environ. Model. Softw.* 114, 29–39 (2019), DOI
   10.1016/j.envsoft.2019.01.012, arXiv:1711.11359. **VERIFIED** (re-fetched). Lo Piano, Ferretti, Puy, Albrecht and Saltelli, *Reliab. Eng. Syst. Saf.* 206, 107300 (2021), arXiv:2203.00639 (index
   definitions). **VERIFIED**. M. D. Morris, "Factorial sampling plans for preliminary
   computational experiments", *Technometrics* 33(2), 161–174 (1991), DOI
   10.1080/00401706.1991.10484804. **VERIFIED** (full text).
2. **Practice.** First-order index S_j = V(E(Y|X_j))/V(Y) and total-effect index
   T_j = E(V(Y|X_~j))/V(Y); S_j = T_j marks an additive factor, S_j < T_j an interacting
   one. Critique of one-at-a-time (OAT): "moving factors OAT in ten dimensions leaves over
   99.75% of the input space unexplored … the reason why an OAT SA is perfunctory, unless
   the model is proven to be linear"; "If all models were linear, an OAT or derivative based
   approach would be adequate." Morris screening: "individually randomized
   one-factor-at-a-time designs," with elementary effects classified as negligible,
   linear and additive, nonlinear, or interacting, at cost n = 2rk runs.
3. **Evidence.** Review of 280 papers: 65% use flawed methods if unclear linearity counts
   as a flaw, "over 20% (57/280)" at the most generous reading.
4. **Bearing.** P17 (matched controls and attribution): *refines, and supersedes for
   design-space mapping*. The project already scopes its controls ("Fixed-placement controls
   identify the effect of one change. Their result applies to that arrangement."). That
   scoping is correct and local; mapping a knob's effect across a design class needs
   randomized-base OAT (Morris) at minimum, and S_j/T_j where runs are cheap. The
   design-response maps in `00_METHOD.md` item 4 ("record the couplings and the separations
   between knobs") have their standard quantitative form in S_j versus T_j.
5. **Transfer.** Fully: demand functionals are deterministic and cheap to evaluate for
   analytic metric families, which is the regime where Sobol' indices are affordable.

### 4.5 Design of experiments, including deterministic computer experiments

1. **Citations.** R. A. Fisher, *The Design of Experiments*, Oliver and Boyd, 1935.
   **VERIFIED** (archive.org text). Box, Hunter and Hunter, *Statistics
   for Experimenters*, 2nd ed., Wiley, 2005, ISBN 978-0-471-71813-0. **PARTIAL** (Chapter 1
   excerpt). J. Sacks, W. J. Welch, T. J. Mitchell, H. P. Wynn, "Design and analysis of
   computer experiments", *Statist. Sci.* 4(4), 409–423 (1989), DOI 10.1214/ss/1177012413.
   **VERIFIED** (OCR of Project Euclid scan). V. Czitrom, "One-factor-at-a-time versus
   designed experiments", *Am. Stat.* 53(2), 126–131 (1999), DOI
   10.1080/00031305.1999.10474445. **VERIFIED**. D. D. Frey, F. Engelhardt, E. M. Greitzer,
   "A role for 'one-factor-at-a-time' experimentation in parameter design", *Res. Eng. Des.*
   14, 65–74 (2003), DOI 10.1007/s00163-002-0026-9. **VERIFIED** (abstract; title confirmed by Crossref).
2. **Practice.** Fisher: randomization guarantees "the validity of the test of
   significance"; replication supplies "an estimate of error"; blocking adds "greatly to the
   precision"; against "an excessive stress laid on the importance of varying the essential
   conditions only one at a time," because modifications "must always be considered as
   potentially interacting"; a conclusion "has a wider inductive basis when inferred from an
   experiment in which the quantities of other ingredients have been varied." Czitrom:
   "Interactions are not estimable from OFAT experiments." Sacks et al.: for deterministic
   codes, "Classical notions of experimental unit, blocking, replication and randomization
   are irrelevant," yet "The selection of inputs at which to run a computer code is still an
   experimental design problem"; the output is modelled as a random function and fitted by
   kriging, with designs chosen by IMSE, maximum-MSE or entropy criteria (the paper does not
   use the term "space-filling"). Frey et al. (2003): "When experimental error is small …
   or the interactions among control factors are large …, an adaptive one-at-a-time strategy
   tends to achieve greater gains than those provided by orthogonal arrays," where the goal
   is improvement rather than parameter estimation.
3. **Evidence.** Fisher's agricultural designs; Frey et al. analysed 66 responses from 27
   published full factorials.
4. **Bearing.** P17: *refines*. For attribution of a single change at a base point,
   matched OAT controls are sound; for claims about a knob across a class, factorial or
   randomized designs are required. For improvement (searching for a better design),
   adaptive OAT is defensible. Replication does not apply to deterministic kernels; the
   remaining design problem is where to evaluate.
5. **Transfer.** Directly. The distinction between attribution, mapping and improvement
   should be explicit in every control the book prescribes.

### 4.6 Set-based concurrent engineering and the value of carrying alternatives

1. **Citations.** Sobek, Ward and Liker, "Toyota's principles of
   set-based concurrent engineering", *Sloan Manage. Rev.* 40(2), 67–83 (1999). **PARTIAL**
   (publisher preview; principles quoted in B. Toche, R. Pellerin, C. Fortin, "Set-based design: a review and new
   directions", *Design Science* 6, e18 (2020), DOI 10.1017/dsj.2020.16). Ward, Liker, Cristiano and Sobek, "The second Toyota paradox: how delaying decisions can make better cars
   faster", *Sloan Manage. Rev.* 36(3), 43–61 (1995). **PARTIAL**. D. N. Ford and D. K.
   Sobek, "Adapting real options to new product development by modeling the second
   Toyota paradox", *IEEE Trans. Eng. Manage.* 52(2), 175–185 (2005), DOI
   10.1109/TEM.2005.844466. **VERIFIED** (abstract). R. de Neufville and S. Scholtes,
   *Flexibility in Engineering Design*, MIT Press, 2011, DOI 10.7551/mitpress/8292.001.0001.
   **PARTIAL** (description).
2. **Practice.** "Map the design space: (i) Define feasible regions (ii) Explore trade-offs
   by designing multiple alternatives (iii) Communicate sets of possibilities. Integrate by
   intersection … Establish feasibility before commitment: (i) Narrow sets gradually while
   increasing detail (ii) Stay within sets once committed (iii) Control by managing
   uncertainty at process gates." Ford & Sobek: "converging too quickly or too slowly
   degrades project value," explained by real options.
3. **Evidence and limits.** Interviews at Toyota and comparison with Chrysler; Toche et
   al. note that carrying alternatives costs money and that SBCE "as described, was the
   result of their perception of a system that is not explicitly documented."
4. **Bearing.** P19 (forks and stopping rules): *supports*, including the practice of
   investigating alternatives after one succeeds, with a stated cost and an explicit
   narrowing rule. P01/P02: *supports* "establish feasibility before commitment."
5. **Transfer.** Directly for research forks; the book should pair each fork with its
   narrowing criterion and the cost of carrying it.
