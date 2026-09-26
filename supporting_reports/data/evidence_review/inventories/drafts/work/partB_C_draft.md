## Part B. Source families on the static background (8 September evening – 9 September)

Scope: 56 commits, `cc5e253` (8 Sep 20:46) to `8492f8e` (9 Sep 21:21). About 16
source families were opened and closed in about 25 wall-clock hours. From
`1069413` (9 Sep 09:00), 37 of these commits ran on a complete two-ended
*static* background at phase 0.745. Fuller notes with every citation are in
`work/block_sep08_09.md`; this part condenses them. I spot-checked the key
numbers against the reports.

### B1. An exact inverse stress fit cancels gravity's own kinetic term

- **Date / commits.** 8 Sep, `cc5e253`, `0cc3f79`, `275edbc`.
- **What happened.** A rate-quadratic Comer–Andersson action was fitted to
  supply the missing early angular stress. The fit forces
  (8πa, 8πb) = (1, −1), so the tensor kinetic ratio is K_TT = 1 + 8πb = 0. All
  12 least-squares fits land there, with residual 8.5e-15, and all 72
  registered evaluations fail. The thermal preload needed to carry the current
  costs 6.2e6–6.5e8 in mass, which drives the minimum f to between −2e6 and
  −2e8. The cause is a lapse contrast of about 78 raised to the Tolman power 4
  (`COMER_ANDERSSON_SPHERICAL_STARTUP_ATTEMPT.md` l.144–156, 214–241, 263–273).
- **Detected by / available since.** The report's own analytic derivation.
  Both failures follow on paper: the fitted Q cancels the ADM kinetic
  density, and 78⁴ ≈ 3.7e7.
- **Counterfactual.** Minutes on paper. The 72-run grid only confirmed it.
  Cost: 3 commits, about 8 minutes.
- **Candidate lesson.** A matter model fitted to reproduce the principal
  (second-time-derivative) part of G/8π subtracts gravity's kinetic term and
  leaves a degenerate principal symbol. Check a source's contribution to the
  principal part, and its mass price, before fitting its stress values.
- **Generality.** General for inverse ("fit T to G/8π") constitutive design
  with velocity-dependent sources. Known in modified-gravity well-posedness
  work.
- **Recurrence.** n = 2 in the block ("an exact algebraic fit is not
  admissible dynamics"; also the elastic-vacuum ghost in B2).

### B2. NEC-satisfying sectors cannot pay a negative-enthalpy demand: rediscovered family by family

- **Date / commits.** 8 Sep 21:12 to 9 Sep 20:23: `96f0459`, `1a4c988`,
  `1edb374`, `7512231`/`868b938`, `56aa116`, `92b997b`, `f4227ff`, `aa7408f`.
- **What happened.** The demand has ρ + p_r < 0 at all 2,049 sampled radii
  (`QUANTUM_MOVING_BOUNDARY_ATTEMPT.md` l.271–273). Eight families each closed
  on the same sign fact:
  - Comer two-current support contributes 0, and its fluids a positive amount
    (`COMER_TWO_CURRENT_EVOLUTION_ROUND.md` l.284–299). The report says this
    holds "already at zero preload", yet 12 evolutions and a 1,024-cell
    refinement ran first.
  - An elastic vacuum support has time kinetic coefficient K_r = e + p_r < 0 at
    every radius, a ghost. The construction cites Dubovsky et al., whose main
    result is exactly this (`VACUUM_SUPPORT_SELECTION_ROUNDS.md` l.186,
    215–218, 258–276).
  - The planar vacuum's angular E + P⊥ = 0.
  - The condensate has ρ + p_r = 2(K + D) ≥ 0.
  - Filling every confined-fermion multiplet gives −0.0045 to −1.10 against a
    required +2.0.
  - Cavity mirrors give a net −0.20 at g = 10.
  - Magnetic bends have ρ + p_r = B²(1 − t_r²)/e² ≥ 0.
- **Detected by.** A short sign argument inside each report.
- **Available since.** The start of the block. A sum of NEC-satisfying tensors
  satisfies NEC.
- **Counterfactual.** A block-level null-energy budget would have scored five
  of these families on paper. Cost: about 8 rounds, about 20 commits, partly
  justified by other aims.
- **Candidate lesson.** The null deficit is a budget that only the exotic
  sector can pay. Every ordinary component, including the holders, mirrors
  and confinement the exotic sector needs, adds to the bill. Score candidates
  by net null contribution, supports included, first.
- **Generality.** A truism once stated, and universal for NEC-violating
  designs. The operational content is counting the exotic sector's own
  supports.
- **Recurrence.** About 8 in this block. With C4 (four more on 10–12 Sep), the
  lesson recurs about 12 times in the window.

### B3. Casimir cells with ordinary holders are net positive: known, then re-derived

- **Date / commits.** `a91c04d`/`5cbbbf1` (8 Sep 21:34); `8987ffa`/`8d1bb32`
  (22:05–22:12); `26728fa`/`1edb374` (9 Sep 08:26–08:36); `ebe80b0` (17:51).
- **What happened.** At 21:34 the vacuum round already applied the
  Costa–Matsas bound. DEC holding matter carries at least 3C, so a complete
  cell has at least 2C per cavity volume (`VACUUM_SUPPORT_SELECTION_ROUNDS.md`
  l.86–92). The same conclusion was then re-derived three times:
  - a moving-boundary bound with minimum complete energy 8.498;
  - a matched-mass bound with holding/binding ratio 1.0014–2.9994 over 154
    pairs (`RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md` l.5–11, 99–146);
  - a reorientation "mechanical realization gate" failure.
- **Counterfactual.** The rail-level verdict was fixed at 21:34. Cost: about
  5 commits and 2 reports whose rail conclusion was already known.
- **Candidate lesson.** Treat "complete cell energy ≥ 0 under DEC holding" as a
  prior gate for any Casimir-based source.
- **Generality.** General, and literature-backed (Costa–Matsas, cited in the
  repo).
- **Recurrence.** Four derivations in the block, then the idea's return on
  24 Sep and its refutation on 25 Sep (E10): n = 5 derivations or encounters
  of the same fact.

### B4. Idealized boundaries and joins give regulator-dependent or divergent quantum stress

- **Date / commits.** `8d1bb32` (8 Sep 22:12); `1069413`–`d2a7da6` (9 Sep
  09:00–09:37); `b040588` (14:31).
- **What happened.**
  - (a) Gaussian walls: free-subtracted local densities do not converge. The
    one-wall dressing runs 5.10 → 13.77 as the cutoff rises, and the centre
    energy changes sign, −0.197 → +0.054 (`QUANTUM_MOVING_BOUNDARY_ATTEMPT.md`
    l.225–246). The missing overlap counterterm is identified later.
  - (b) Ideal delta sheets: a curved search with 159,705 radial nodes and 129
    harmonics was followed by the finding that the pressure diverges as
    λ/(48π²d³) at the sheet. The branch stopped (`CURVED_QUANTUM_BOUNDARY_SEARCH.md`
    l.169–172; `SPHERICAL_BOUNDARY_MATERIAL_CLOSURE.md` l.104–156).
  - (c) A classical C¹ join: its curvature step gives a one-sided d⁻² vacuum
    energy against a finite requirement (`CONDENSATE_SUPPLIED_QUANTUM_STRESS.md`
    l.54–112).
- **Available since.** All three were available, with Deutsch–Candelas,
  Graham et al. and Milton et al. cited in the block. Graham was cited at
  08:36, before the sheet search began at 09:00.
- **Cost.** About 7 commits; two backgrounds abandoned.
- **Candidate lesson.** ⟨T_ab⟩ is only as regular as the background and the
  boundaries:
  - delta mirrors diverge as d⁻³;
  - curvature steps diverge as d⁻²;
  - Israel (C¹) matching is sufficient classically and insufficient
    semiclassically.
  Use smooth backgrounds and finite-thickness boundaries before inserting
  ⟨T⟩ into the field equations.
- **Generality.** General and textbook. It pairs with A3 (C∞ primitives): the
  semiclassical case strengthens the smoothness requirement.
- **Recurrence.** n = 3 in the block; with A3, n = 4 smoothness incidents.

### B5. The Israel junction demanded a compressed shell, which buckles; a patch chain followed

- **Date / commits.** The requirement was visible at `d2a7da6` (09:37) and
  detected at `361d406` (10:15). Patches followed at `3c1431e`/`2ef33bc` and
  `c04cc31`/`cdde39c` (to 11:41).
- **What happened.** The enclosing junction needs positive tangential surface
  pressure (P = +4.5e-4). A trapped-fermion wall supplying it has ω² ∝ −(P/Σ)k²,
  with an e-folding time of 1.30. Stiffness is negative in all 1,029 rows, and
  P > 0 holds for the whole branch (`SMOOTH_QUANTUM_MATERIAL_ATTEMPT.md`
  l.149–153, 215–264).
  - The screening-cloud patch saturates, with an analytic ceiling outside the
    thin-cloud regime; all 1,040 cases are negative
    (`SCREENED_CHARGED_WALL_RESPONSE.md` l.155–181, 227–236).
  - The gravitating-atmosphere patch makes the wall tensile, but the cloud's
    relaxation exceeds the tension by at least 4.1×
    (`GRAVITATING_SCREENING_ATMOSPHERE.md` l.124–143, 231–264).
- **Available since.** Yes: membrane buckling under compression, and Israel
  thin-shell dynamics (cited at `d2a7da6`).
- **Cost.** About 6 commits, 3 reports and 2 hours.
- **Candidate lesson.** Read the sign of the surface stress the junction
  demands before choosing a shell material. Compression needs an independently
  counted restoring response, and patches that add one carry their own loads.
- **Generality.** General for thin-shell constructions (wormhole, gravastar
  and bubble shells). Textbook physics.
- **Recurrence.** n = 3 (smooth wall, screened wall, atmosphere).

### B6. A one-sided shooting blow-up was reported as a physical obstruction

- **Date / commits.** `d7e6cdd`/`7512231` (9 Sep 12:23–12:36), then
  `6fa75d7`/`b4bd0a9`, then `4188ad3` (14:05).
- **What happened.** Integrating the condensate inward from exterior data
  produced a pole near areal radius 4.2925, matching the asymptote
  h ≈ √(2/μ)/(Bv(x* − x)) to 0.02%. Sixteen robustness checks reproduced it:
  two integrators, tolerances, thresholds and geometries. The headline reads
  "failing the regular stationary material continuation"
  (`SCREENED_SCALAR_CONDENSATE.md` l.3, 156–187). Ninety minutes later, a
  global boundary-value problem found two regular branches
  (`CONDENSATE_JOINT_CONTINUATION.md` l.53–85). The fixed exterior value
  p_r,R = −0.125 had forced the singularity (`CONDENSATE_JOINT_SELECTION_DIRECTION.md`
  l.59–72).
- **Available since.** Yes. Movable singularities of h″ ~ ch³ under one-sided
  integration are textbook ODE behaviour.
- **Cost.** About 3 commits. The superseded headline stays at the top of the
  report, with only a forward link appended.
- **Candidate lesson.** A finite-radius blow-up in one-sided integration of a
  nonlinear field equation usually signals mis-specified boundary data. A
  no-go claim needs a global boundary-value formulation or an analytic
  argument.
- **Generality.** General for soliton, boson-star and shell matching.
- **Recurrence.** n = 1. It is also counter-evidence: 16 robustness checks
  certified a formulation artifact (F-list).

### B7. Magnitude was deferred behind sign-only screening; the first normalized comparison fell short by about 10⁵

- **Date / commits.** Sign-only work ran from `a91c04d` (8 Sep 21:34) to
  `d2a7da6` (9 Sep 09:37). The first magnitudes came at `b040588` (14:31) and
  `b040b9b`/`cf87a89` (15:13–15:36).
- **What happened.** Reports stated explicitly that the comparison "uses
  signs, independently of any conversion between the cavity units and the
  rail's curvature scale" (`QUANTUM_MOVING_BOUNDARY_ATTEMPT.md` l.275–276).
  - The first magnitude result: the absolute renormalized vacuum supplies
    5.0e-6 to 5.4e-6 of the required opening balance B = 2.1766. The final
    required-to-available ratios are 185,950 and 203,502, and the signed
    balance opposes opening (`SEMICLASSICAL_JOINT_INVESTIGATION.md` l.102–121).
  - The normalization η = 2.41e-5 came out of material matching. It sets one
    rail unit at about 204 ℓ_P and the throat at R₀/√η = 415 Planck lengths,
    noted only in passing (`LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md` l.232).
- **Available since.** Yes. The (ℓ_P/L)² scaling was written down at 09:36.
  Ford–Roman-type quantum-inequality bounds are standard. May's gate list had
  "quantum inequality / ANEC-style endpoint cost: not shown"
  (`STAGE2_ENDPOINT_JUNCTION_SOURCE_MILESTONE.md` l.274).
- **Counterfactual.** A one-line estimate on 8 Sep evening would have re-scoped
  the quantum chain to "Planck-scale or large-N only": η times a loop factor
  per field against an O(1) opening demand.
- **Cost.** The largest in the block: about 30 commits and 18 reports in about
  24 hours. The workflow gained a normalized-first rule only on 17 Sep
  (`1e9ac1d`; Part D).
- **Candidate lesson.** For any semiclassical source, compute the physically
  normalized magnitude first: (ℓ_P/L)² × loop factor × species count, against
  the demand at the intended size. Signs, placement and stability come after.
- **Generality.** General and textbook. It generalizes as the scaling test
  did on 25 Sep (E15).
- **Recurrence.** About 5 magnitude gaps in the block:
  - optical, ≤ 1e-6;
  - absolute vacuum, 5e-6;
  - longitudinal loops, ≤ 4.17%;
  - cavity crossing coupling g* ≈ 17,000;
  - magnetic loops, N_f e²/16π² ≈ 18 against 0.1.

### B8. Bulk tension was assigned to the quantum sector

- **Date / commits.** `4188ad3`–`cf87a89` (implicit), caught at `ada8661`
  (16:18) and `0e66f43`.
- **What happened.** At the throat the demand is (ρ, p_r, p_t) =
  (9.564e-3, −9.565e-3, 3.26e-5). The condensate carried 0.612% of the tension
  and the "quantum remainder" 99.388%, although the null part is only
  ρ + p_r = −1.36e-6 (`COUPLED_SOURCE_ROLE_AUDIT.md` l.7–12, 58–63). After
  reallocation, a backbone carries 95% of the tension and the quantum radial
  weight becomes 3.4e-7 (`COUPLED_REORIENTATION_INVESTIGATION.md` l.72–86).
  The opening-deficit verdict was independent of the allocation.
- **Candidate lesson.** Split the demand into bulk tension (ρ ≈ −p, NEC-neutral,
  carried by strings, flux or potential energy) and the signed null deficit
  (the exotic part). Allocate each before solving any fields.
- **Generality.** A standard decomposition (Morris–Thorne "exoticity"). It is
  general, and the constant-radius track later made the split exact (E1).
- **Recurrence.** n = 1.

### B9. The surrogate's exterior is an Ellis tail, so the null demand runs along the route

- **Date / commit.** `ada8661` (9 Sep 16:18).
- **What happened.** 96.69% of the negative radial-null balance B₋ = 2.325
  lies outside |x| ≤ 2, with 28.77% in 3 ≤ |x| ≤ 40. "That tail itself requires
  negative radial null stress" (`COUPLED_SOURCE_ROLE_AUDIT.md` l.160–184).
  The morning's source-localization work was trying to terminate an
  ultrastatic wormhole tail: the enclosing sheet at R = 6.8, the Schwarzschild
  exterior junction and the atmosphere.
- **Lesson and counterfactual.** See E5 (topology). This is its 9 Sep data
  point.

### B10. The zero-shift static surrogate: the scope error was recognized on 9 Sep and did not stick

*Fine grain for P01's "static-surrogate source work".*

- **Date / commits.** Background `1069413` (9 Sep 09:00); scope correction
  `a1a8a65` (20:46); first active-metric test `bad59e2`/`8492f8e` (21:10–21:21).
- **What happened.**
  - The scope review names the error: "The scope error was promoting these
    conditional source results into necessary active-rail selection gates
    without demonstrating the state equivalence. Local scope qualifications
    were already present in several reports. The later recommendations
    exceeded them" (`ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md` l.165–167).
  - About 35 minutes of active-metric work found the Type IV witnesses in all
    9 timing schedules, and a transfer-routing obstruction. The characteristic
    speeds v± = −β ± α/B carry the required reservoir radiation through the
    protected packet, with in-packet density ≥ 1.0754
    (`ACTIVE_ENDPOINT_TRANSFER_INVESTIGATION.md` l.61–67, 127–135, 153–192).
  - Sep 10–17 nevertheless returned to static slices. The 10–12 Sep endpoint
    patch reports keep the shift, but none cites the Type IV verdict (C-list
    overview). The C1 work used "the static, zero-shift surrogate of the
    archived phase-0.745" (`C1_FINITE_MODULE_PAIR_SCREEN.md` l.25).
- **Candidate lesson.** Before adopting a simplified background, list the
  obstruction classes it can and cannot represent. A correction recorded in a
  report does not constrain later work unless it enters the standing plan (A9).
- **Recurrence.** Correction not propagated: A9 and this: n = 2.

### B11. Helpful and parasitic terms share one length scaling, so reshaping cannot help

- **Date / commits.** `e3c17ae`, `aa7408f`, `e2dc588`/`92b997b`,
  `283a91e`/`f4227ff` (9 Sep 15:58–20:23).
- **What happened.**
  - Long conformal loops need L_opt < 3.27 for a helpful sign, but the loop has
    6.30. With clock freedom the best case reaches ≤ 4.17%.
  - For cavities, the interaction and the mirror gradient load both scale as
    η/a³. The crossing coupling is g* ≈ 11,000–24,000 against g ≤ 10, and a
    sixteenfold gap reduction gains only 1.67×
    (`NARROW_CURVED_CAVITY_EVALUATION.md` l.80–162).
  - Magnetic loops need N_f e²/16π² > 18 against a perturbative 0.1; 0 of
    23,760 cases pass (`SHORT_MAGNETIC_CIRCUIT_EVALUATION.md` l.143–196).
- **Candidate lesson.** When helpful and holding terms scale alike with size,
  the verdict is a dimensionless coupling threshold. Compute it first; if it
  is non-perturbative, stop.
- **Generality.** A general rule of thumb for Casimir, flux-tube and mirror
  sources.
- **Recurrence.** n = 3–4.

### B12. A redundant recommendation, corrected within 15 minutes; an archive re-screen that was predictably null

- **Date / commits.** `aa7408f` (18:02), replaced at `83fe023` (18:17);
  re-screen `d9b93df`/`fe99e3f`.
- **What happened.** The history report says: "The previous recommendation to
  select the operational constraints before proceeding repeated work already
  established in the design record" (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md`
  l.17–20). The 13 archived controls then moved the demand by at most
  +0.315% against a gap of 10⁵ (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md`
  l.5–13, 132–162). Probably a user correction; the record does not quote the
  user.
- **Candidate lesson.** Search the project archive before proposing
  exploration, and compare plausible effect size with the gap before
  re-screening.
- **Generality.** A research-process near-truism.
- **Recurrence.** Knowledge in the record not applied: n = 5 with A9.

### B13. The technical disclosure used as a running log for 3.5 hours, then stripped

- **Date / commits.** `921e560` (16:59, +179/−51 lines) plus four small
  additions; removed at `734156c` (20:31). The PDF was rebuilt 6 times.
- **Note.** The same removal also erased the Le verdict (A9). Premature locking
  recurs: E16.

### B14. The lapse hill at the packet (A up to about 108) was never read as passenger aging

- **Date / commits.** `ada8661` (A₀ = 69.34), `fe99e3f` (81.7–88.5), `bce06d7`
  (maximum 108.07).
- **What happened.**
  - (a) The lapse profile rules out free binding of massive fields, since
    Weinbaum's bound-state condition needs an attractive lapse well. Fermions
    therefore need material confinement (`SOURCE_CONSTRUCTION_RESTART_SHORTLIST.md`
    l.70–77). The same commit also qualified the Kain EDM benchmarks cited
    three hours earlier.
  - (b) A payload at a lapse of 69–108 ages 70–110× faster than exterior
    clocks. No report in the block interprets this.
- **Cross-reference.** Adds a fourth design to E13. Peak clock rates across the
  window: about 108× (throat, 9 Sep), 9,069× (census), 140× (amplitude), 55×
  (lapse design).

### B15. Checks that caught method errors early

- (a) Coarse-resolution Type IV artifacts: 138 raw complex-pair records
  appeared only at coarse settings. The discriminant ran −6.9e-9 → +2.1e-10 at
  1,024 cells, and all 36 finest witnesses are Type I
  (`COMER_TWO_CURRENT_EVOLUTION_ROUND.md` l.244–270). This is the mirror image
  of E8: coarse grids can create Type IV as well as miss it.
- (b) Truncated gradient expansion: extrapolating the quartic bending term
  beyond ka ~ 1 would have given 72 false passes of 420; the saturating law
  gives 0.
- (c) Precision loss at release was replaced by an analytic divided
  difference 2 minutes after introduction.
- (d) Default CSV float parsing broke near-cancellation audits; the fix was
  exact round-trip reading (recurs 3 times).
- (e) An unresolved quadrature (162 against 39,023) was kept out of the
  verdict.
- (f) A renormalization claim was corrected in the text (`b040b9b`).

## Part C. Endpoint storage, capacitors, joints and virtual radial cells (10 and 12 September)

Scope: 90 commits, `f562930` (10 Sep 05:10) to `75360cd` (12 Sep 21:15), 26
reports; there are no commits on 11 Sep. All 26 reports work on the late,
non-live endpoint patch x ∈ [−2.1, −0.5], s ∈ [0, 1.285], with the active
metric's shift kept. None mentions the Hawking–Ellis classification or Type
IV (0 grep hits). Ten defer the negative-null remainder to an unspecified
"independently supplied negative-stress sector" or "quantum source". Fuller
notes: `work/block_sep10_12.md`.

### C1. Numerical temperature floors misread as physical heat depletion

- **Date / commits.** 10 Sep: `f562930`/`38ea61b`, `9f1429c`/`a107821`/`56e6b8d`,
  `148b5eb`.
- **What happened.**
  - Zero-exchange elastic controls lost temperature although the adiabatic law
    conserves heat: "a numerical limitation"
    (`ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md` l.141–147).
  - In the EM storage runs, the ideal control drove an element to zero heat.
    "Global conservation of the combined tensor leaves that internal-energy
    error undetected". A stop time converging between 256 and 512 cells still
    carried a heat discrepancy of 0.141 against an initial 0.261: "Convergence
    of a stopping time alone would therefore give an incorrect impression of a
    physical limit" (`ELECTROMAGNETIC_ENDPOINT_STORAGE_INVESTIGATION.md`
    l.196–218).
  - Three of five conductor runs stopped at a primitive-inversion limit inside
    the analytic causal boundary (`ACTIVE_RESERVOIR_CAUSAL_TRANSPORT.md`
    l.259–266).
- **Detected by.** Source-free controls and independent heat audits, run in the
  first round. This is largely a check that caught a problem early.
- **Candidate lesson.** Run a source-free control that the continuum law says
  conserves the quantity at issue. Classify every stop as numerical or
  physical before interpreting it. A converging event time does not show that
  the event is physical.
- **Generality.** General for numerical source modelling. The dual-energy
  problem is textbook in computational fluid dynamics; the "converged stop
  time" trap is worth teaching.
- **Recurrence.** n = 3.

### C2. A conservation error normalized to the wrong budget

- **Date / commit.** `8880934`.
- **What happened.** The energy error was about 0.5 against a total of 34,700
  (1.4e-5 relative), while the decisive local heats are about 0.25. The
  material-wave CFL limit, not the step cap, was controlling: a Courant
  factor of 0.2 → 0.05 cut the error about 60×. Going from 64 to 128 cells
  changed density by 55.5% and stress by 47.6%, with 97.6–99.6% of the squared
  error in steepening end fronts (`ACTIVE_RESERVOIR_ENSEMBLE_REFINEMENT.md`
  l.183–205, 376–379).
- **Candidate lesson.** State conservation errors relative to the smallest
  budget that decides pass or fail, and check which step restriction is
  active.
- **Generality.** General numerics; textbook.
- **Recurrence.** n = 2.

### C3. Treating heat symptoms of a kinematic cause (γ ≈ 47); redirected by the user

- **Date / commits.** Chain `9f1429c` → `4f3eb03`; redirect `6b6433b`–`aa22156`.
- **What happened.** Three reports added heat supply to a depleting element:
  EM storage, strain relaxation and conduction. The element moved at
  v = −0.9995 with n_eff = 1.05e-3, and q̇ = αR²(−P + vF)/(A n_eff) made the
  1/n_eff factor explicit. Conversion replaced 0.91% of the withdrawal, and the
  best conductor kept 0.153% (`ACTIVE_RESERVOIR_ENSEMBLE_REFINEMENT.md`
  l.344–364; `ACTIVE_RESERVOIR_CAUSAL_TRANSPORT.md` l.7, 289–356). The
  prestressed study then recorded "the user's material-velocity concern" and
  a Lorentz factor "near 47". It found that the speed "depends strongly on the
  tested mechanical construction" (`PRESTRESSED_BUFFER_VELOCITY_INVESTIGATION.md`
  l.13–14, 174, 237, 340–342).
- **Counterfactual.** A γ and dilution column in the first run; speeds of 0.93
  and 0.97 were already tabulated.
- **Cost.** About 8–10 commits, 3 reports and 2.5 hours.
- **Candidate lesson.** When a demanded exchange tensor is forced one way onto
  trial matter, check the receiving matter's kinematics (γ, dilution, causal
  access) before adding stores or conductors.
- **Generality.** Any one-way forcing of a demanded tensor onto trial matter.
- **Recurrence.** n = 1 chain. The user correction is visible in the record.

### C4. The null-projection screen ran after the dynamics; the user set the reservoir aside

- **Date / commits.** `a60432b`/`21b98b9`, `2cd4244` (10 Sep 09:16–09:34).
- **What happened.** The required negative radial-null contribution was 14.21
  at startup, about 3,248× the geometric value, and 75.78 at fade. Optimizing
  the preload cut it only 23%. An exact identity ties it to buffer inertia and
  motion: max S_kk = w_b/(1 − c_f²)·(1 + |v|)/(1 − |v|)
  (`RESERVOIR_FEASIBILITY_ENVELOPE.md` l.139–148, 180–215). "The user has set
  this assembly aside from the active search" (l.257–260).
- **Counterfactual.** One null-projection evaluation of the proposed reservoir
  tensor before registering any dynamics. That was 20 commits and 4.3 hours
  earlier.
- **Cost.** Phase A: about 20 commits and 6 reports.
- **Candidate lesson.** Screen each support component by its null projections,
  including the Doppler weight (1 + |v|)/(1 − |v|) of its bulk motion, before
  designing its dynamics.
- **Recurrence.** n = 4 here. With B2, about 12 in the window. See H-list
  lesson L3.

### C5. Solver statuses read as physics: HiGHS dropped small metric coefficients

- **Date / commits.** `1b70929` (10 Sep); `c05aa05`, `5dc7ce4` (12 Sep).
- **What happened.** A heat-engine control was reported infeasible, although
  its feasible set contains an accepted history (residual 9.45e-9). "HiGHS
  deletes coefficients at or below 1e-9 by default", and small shift
  coefficients multiply large stores. With the threshold at 1e-12 the
  control became feasible (`PRESSURE_LINKED_STORAGE_COMPLETION.md` l.223–252).
  Later, a native state marked valid violated the original rows by 0.51 and
  7.91. The fix went forward only: `graded_electrothermal.py` l.142–145 still
  uses defaults, and the earlier GRADED runs were not repeated. Practice
  improved within the block, with exact rational Farkas certificates by
  12 Sep.
- **Candidate lesson.** Metric data are badly scaled: tiny lapse or shift
  derivatives multiply large stores. Never read solver statuses as physics.
  Check nested-relaxation consistency and the original rows, and require
  certificates for infeasibility.
- **Generality.** General for optimization-based source design.
- **Recurrence.** n = 4.

### C6. Stores must hold energy comparable to their own rest energy

- **Date / commits.** `64006ae`, `7416b33` (10 Sep); `5e59da3`, `75360cd`
  (12 Sep).
- **What happened.**
  - The capacitor benchmark carries 3.4e12 units of rest energy per unit
    stored, so its necessary negative null is 1.9e11 against 0.104.
    Break-even needs 0.6 c² per kilogram (`REGENERATIVE_CONVERTER_EVALUATION.md`
    l.8, 169–206).
  - Allowed added material needs 2.5 c² per kilogram, and charge layers need
    5.1 MV, above the pair threshold.
  - The radial-cell thermal bank needs 3–9 c² per kilogram, and the report says
    "a general material search [is] premature … Work pauses"
    (`VIRTUAL_RADIAL_CELL_PHOTON_CONTACT_DESIGN.md` l.12–20, 211–217, 271–274).
- **Counterfactual.** The ratio of duty to spare rest inventory was computable
  at `4d6af24`/`cc1c210`. The next 22–25 commits and 3 reports developed
  temperatures, contacts and photon turnover first.
- **Candidate lesson.** Support energy duties in metric engineering are of the
  order of the geometry's source scale, ρc² in geometric units. Screen every
  store by E_stored/(Mc²) against the density budget first.
- **Generality.** Very general for designs with O(ρc²) stresses. Only field- or
  radiation-dominated stores can pass, and those need containment (C7).
- **Recurrence.** n = 4.

### C7. An optimistic enclosure bound stayed the reference after a 3× tighter one was derived

- **Date / commits.** `64006ae` → `7416b33`, used through `0e07a9c`.
- **What happened.** The U/3 trace bound gave a fade requirement of 0.2628.
  Two hours later, the componentwise DEC gave wall energy ≥ U, "stronger than
  the U/3 trace bound", and 0.5338 with the absorbed work counted
  (`FINITE_WORK_INTERFACE.md` l.224–254). The old value remained the reference
  in three reports, and magnetic insulation at 0.254 looked "favorable" against
  it (`CHARGED_CAPACITOR_CONSTRUCTION.md` l.36–38, 204–206). It was demoted in
  `COMPOSITE_CAPACITOR_AND_RAIL_CONNECTIONS.md` l.158–159.
- **Candidate lesson.** Use the tightest cheap necessary bound (componentwise
  energy conditions; the von Laue/virial integral) as the selection
  reference, and re-baseline explicitly when a tighter one appears.
- **Generality.** General for containment of field-energy stores.
- **Recurrence.** One bound, reused in 4 reports.

### C8. Partial ledgers flattered candidates; counting the full route reversed them

- **Date / commits.** `5e59da3`/`371bdf9`, `0e07a9c`/`162f399`, `4d6af24` →
  `27f8f18`.
- **What happened.**
  - Magnetic insulation went from 0.254 to 8.6–43.5 once its work was routed
    through the receiver, because flux freezing raises B² under compression
    (`CHARGED_CAPACITOR_CONSTRUCTION.md` l.8–9, 230–262).
  - An internally balanced capacitor removed the stresses the pressure link
    relied on, leaving a 6.45× shortfall.
  - A relaxed local thermal LP cleared both locations; restoring coherent
    control reopened a deficit.
- **Candidate lesson.** Compare components by their complete assembly ledger,
  including the transport of their work, reactions and heat. A field that
  carries load cannot be repackaged as an isolated store without replacing its
  stress.
- **Generality.** General.
- **Recurrence.** n ≈ 5 (with C9).

### C9. GR self-weight: a local contact cost hid an exponential pressure column

- **Date / commits.** `13cbdd1`, `152e32e`.
- **What happened.** The local pieces cost 158 at startup. The connected column
  p_x + 4ΓB a_s p = ΓB F needs a peak pressure of 221,217 and slice energy
  3.1e7, about 2e5× more: "The integrating factor accumulates that self-weight
  across the large clock gradient" (`PRESSURE_LINKED_STORAGE_COMPLETION.md`
  l.113–173).
- **Available since.** Yes: Tolman/TOV hydrostatics, where pressure has weight.
- **Candidate lesson.** Estimate the self-weight integrating factor
  exp(∫(1 + κ)ΓB a dx) across any stress-transmitting member in a strong lapse
  gradient before sizing local pieces.
- **Generality.** General for static support in strong redshift gradients.
- **Recurrence.** n = 1. Related to B1: the Tolman factor 78⁴.

### C10. Explicit correction: the independent audit omitted the moving-frame EM force

*The `JOINT_SUPPORT_CONTINUUM_CORRECTION.md` erratum.*

- **Date / commit.** `9133810` (12 Sep 11:01), 20 minutes after `b368552`.
- **What happened.** The independent continuum audit
  (`scripts/audit_joint_support.py` at `b368552`, l.73) dropped the term
  −vH_t/(NR⁴) from F_rest = Γ(F_normal − vP_normal). The solver target
  already had it, so the auditor was wrong and the solver right
  (`JOINT_SUPPORT_CONTINUUM_CORRECTION.md` l.3–17). The original report
  claimed the audit passed an independent covariant-divergence test "on a
  metric with nonzero shift". That test set `flux_energy=zero`, so the term
  was never exercised (`JOINT_SUPPORT_STRESS_SCHEDULE.md` l.211–213). The
  effect was small: residuals 11.96 → 11.89%, 8.24 → 8.18%, 4.60 → 4.50%. No
  decision changed.
- **Detected by.** Not recorded. The fix adds a manufactured solution with a
  time-dependent field and nonzero material velocity.
- **Candidate lesson.** A manufactured test verifies only the couplings it
  switches on. Frame-projection cross terms (time dependence × velocity ×
  field) vanish in static tests.
- **Generality.** General (coverage of method-of-manufactured-solutions
  tests).
- **Recurrence.** n = 1 erratum. It is also counter-evidence: the independent
  code was the faulty component.

### C11. A selected support target was reversed by conservative evolution

- **Date / commits.** `b368552` (10:41) → `a986c28`/`9a5f0be`/`ad2e7f7` (13:31).
- **What happened.** The target was selected with a solver residual of 3.2e-12,
  while the continuum audit in the same commit showed an 8.24% force
  residual. Conservative implicit evolution made it inadmissible: "An
  admissible approximate tensor becomes inadmissible when its force balance is
  evolved more accurately". The final routed target's fade remainder of 3.18 is
  about 9.6× the selected 0.333 (`JOINT_SUPPORT_REFINEMENT_AND_END_LOADS.md`
  l.4–7, 72–79; `JOINT_SUPPORT_CONSTRUCTION_REVIEW.md` l.5–7, 156–160).
- **Candidate lesson.** A schedule enforced only at collocation points is not a
  continuum source, and a tiny discrete residual says nothing about it.
  Promote only after a dense conservation audit and an admissibility check
  between nodes.
- **Recurrence.** "Between samples" in this block: n ≈ 7 (with C12). Across the
  window, with E8 and B15a, this is the most frequent numerical lesson.

### C12. Clearances that existed only at samples or at a moved test point

- **Date / commits.** `79b92d1` → `183f925`; `ae538ae`; `9dbaf92`.
- **What happened.**
  - Narrow cell pairs placed "between the earlier startup witnesses" passed.
  - Explicit replay withdrew those clearances (deficits 0.0016 and 0.014). A
    48 × 1029 pass then failed at 96 × 2057, with overloads between samples.
  - Averaging the demanded tensor over panels hid errors of ±0.01–0.02.
  - A midpoint-only temperature check failed at a time knot
    (`VIRTUAL_RADIAL_CELL_CONSTRUCTION.md` l.170–252, 357–393;
    `VIRTUAL_RADIAL_CELL_PRESSURE_LINK_REALLOCATION.md` l.337–356).
- **Candidate lesson.** Enforce time-dependent budgets over whole intervals
  (supersolution envelopes), never average the demanded tensor over a panel,
  and keep known failing witnesses inside any narrowed test.
- **Recurrence.** See C11.

### C13. Optimizers exploited unphysical freedoms; passivity was checked afterwards

- **What happened.**
  - Force concentration doubled under refinement.
  - Heat schedules failed a passive contact test "at every sampled material
    label".
  - "Large simultaneous conversion cycles … use the converter losses to export
    heat".
  - A fluid went near-cold, needing α⁴ < 1.7e-16 and volume contrasts of
    4.7e21; a warm floor cut this by more than 13 orders.
  (`GRADED_ELECTROTHERMAL_ASSEMBLY.md` l.176–184;
  `JOINT_ELASTIC_BACKING_PRESSURE_SCREEN.md` l.149–156;
  `VIRTUAL_RADIAL_CELL_CONSTRUCTION.md` l.291–296;
  `VIRTUAL_RADIAL_CELL_PRESSURE_LINK_REALLOCATION.md` l.200–288.)
- **Candidate lesson.** Energy-momentum balance alone admits schedules no
  passive material can realize. Build the second law, passivity and regularity
  into inverse source design as constraints.
- **Recurrence.** n = 4–5.

### C14. A spatial march posed against the characteristic direction

- **Date / commit.** `a986c28`.
- **What happened.** The time-derivative coefficient has the sign of the
  material velocity (−0.20 to 0). Marching from the left blew up; data at the
  inflow cut fixed it (`JOINT_SUPPORT_CONSERVATION_AND_PASSIVITY.md` l.56–61).
- **Candidate lesson.** On a shifted metric, material drift and shift decide
  which boundary is inflow; prescribe data there.
- **Generality.** Textbook well-posedness.
- **Recurrence.** n = 1.

### C15. Cheap nodewise screens excluded passive and permanent prestress early (positive)

- **Date / commits.** `b368552`, `a986c28`, `15bb755`, `f6a3e88`.
- **What happened.**
  - 73.6% of the axial-force changes run opposite to passive-spring behaviour.
  - A permanent flux-tube bundle needs amplitudes 851× apart at different
    nodes.
  - End jackets need values outside their admissible range.
  All were proved infeasible with exact certificates, in the same commits that
  proposed them (`SCALAR_FLUX_SUPPORT_CONSTRUCTION.md` l.87–93, 185–236;
  `JOINT_SUPPORT_REFINEMENT_AND_END_LOADS.md` l.127–137).
- **Candidate lesson.** When the demanded support stress changes sign or
  magnitude over the cycle, permanent or passive prestress cannot supply it.
  Test the time intersection of nodewise bounds first.
- **Generality.** General for time-dependent metric schedules.
- **Recurrence.** n = 4 or more; a positive example.
