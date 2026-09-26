# Incident inventory: block Sep 8 (after LE reports) through Sep 9, 2026

Repo: `/media/projectspace/active-rail-refined-design-base` (read-only mining).
Paths below are relative to that root; `SR/` = `supporting_reports/`. Line numbers
refer to the current working-tree files unless a commit is named.

Block scope: 56 commits, `cc5e253` (Sep 8 20:46) through `8492f8e` (Sep 9 21:21).
The LE reports end at `dab8549` (Sep 8 20:14). Roughly 16 source families were opened
and closed in about 25 wall-clock hours, with an overnight gap from Sep 8 22:12 to Sep 9 08:26.
37 commits (Sep 9 09:00 to 20:31) ran on the complete two-ended static background
introduced in `1069413`.

Timeline, one family per line:
- Sep 8: Comer quadratic startup (`cc5e253`, `0cc3f79`, `275edbc`); Comer two-current (`e656242`, `9a59e55`, `96f0459`); vacuum support rounds (`a91c04d`, `5cbbbf1`, `0e88247`, `1a4c988`); moving quantum boundary (`8987ffa`, `7a1aed0`, `8d1bb32`).
- Sep 9 morning: matched-mass boundaries (`26728fa`, `1edb374`); curved spherical boundaries on the static surrogate (`1069413`, `ea33ad8`, `e44a5e4`, `d2a7da6`); smooth mirror with trapped fermions (`05c5a4a`, `361d406`); screened wall (`3c1431e`, `2ef33bc`); gravitating atmosphere (`c04cc31`, `cdde39c`).
- Sep 9 midday: screened condensate (`d7e6cdd`, `7512231`); joint selection (`6fa75d7`, `b4bd0a9`); joint continuation (`4188ad3`); supplied quantum stress (`aa25081`, `b040588`); semiclassical joint (`868b938`, `b040b9b`, `d4512da`, `cf87a89`).
- Sep 9 afternoon and evening: longitudinal literature (`e3c17ae`); role audit (`ada8661`); component cross-reference (`0e66f43`); disclosure integration (`921e560`); reorientation (`ebe80b0`, `aa7408f`); geometry history (`83fe023`); archived geometry (`d9b93df`, `fe99e3f`); restart shortlist (`bce06d7`); confined fermion (`b4fe60d`, `56aa116`); cavity (`e2dc588`, `92b997b`); magnetic (`283a91e`, `f4227ff`); disclosure cleanup (`734156c`); scope review (`a1a8a65`); active endpoint transfer (`bad59e2`, `8492f8e`).

---

## Incident 1: Exact inverse stress fit cancels the gravitational kinetic term (Comer quadratic startup)

- **Date / commits:** Sep 8, `cc5e253` 20:46, `0cc3f79` 20:51, `275edbc` 20:54.
- **What happened:** A rate-quadratic action Q = ½[aΘ² + b B_ab B^ab] was fitted to reproduce the missing angular time-curvature stress. The fit forces (8πa, 8πb) = (1, −1), so the tensor kinetic ratio is K_TT = 1 + 8πb = 0. All 12 least-squares fits return (1, −1) with residual 8.48e-15 (`SR/COMER_ANDERSSON_SPHERICAL_STARTUP_ATTEMPT.md:214-220`), and all 72 registered evaluations fail (`:7`, `:240-241`). The near match (0.975, −0.95) keeps K_TT = 0.05 but leaves a stress mismatch of 8.99e-4 and negative entropy production of −2.32e-4 (`:233`). A second scale failure surfaced in the same round: the thermal preload needed to carry the current costs 6.16e6 to 6.45e8 in mass, which drives the minimum f to between −1.97e6 and −2.06e8 against a retained metric of order 1 (`:263-271`). The report attributes this to a lapse contrast of about 78 raised to the Tolman power α⁻⁴ (`:271-273`).
- **Detected by:** Analytic derivation in the same report. The fitted Q cancels the Einstein–Hilbert kinetic density (B_ab B^ab − Θ²)/16π (`:144-156`).
- **Tool available earlier?** Yes. The ADM kinetic term is textbook, and the report derives the cancellation before any numerics. The preload blow-up follows from 78⁴ ≈ 3.7e7 in one line.
- **Counterfactual:** Both failures were predictable on paper in minutes, so the 72-run grid and 216 curvature records were confirmation only.
- **Cost:** Low. 3 commits in about 8 minutes, with 65 MB of evidence (`:346`).
- **Candidate lesson:** Suppose an inverse-designed matter model reproduces the second-time-derivative (principal) part of the Einstein tensor. It then subtracts gravity's own kinetic term and leaves a degenerate or ill-posed principal symbol. Check a source's contribution to the principal part, and its mass and energy price, before fitting its stress values.
- **Generality:** General to inverse ("fit T to G/8π") constitutive design whenever the source depends on metric velocities. It is not a truism, but it is well known in modified-gravity well-posedness work.
- **Recurrence in block:** 2 cases of "an exact algebraic fit is not admissible dynamics": here, and the elastic-vacuum ghost in Incident 2.

## Incident 2: NEC-satisfying sectors cannot carry the negative-enthalpy demand, rediscovered family by family

- **Date / commits:** Sep 8 21:12 through Sep 9 20:23. Occurrences: `96f0459`, `1a4c988`, `1edb374`, `7512231`/`868b938`, `56aa116`, `92b997b`, `f4227ff`, `aa7408f`.
- **What happened:** Each family closed on the same sign fact. The demand has ρ + p_r < 0 at all 2,049 sampled radii (`SR/QUANTUM_MOVING_BOUNDARY_ATTEMPT.md:271-273`; `SR/VACUUM_SUPPORT_SELECTION_ROUNDS.md:18-19`), and every ordinary component adds nonnegative null stress. The occurrences:
  1. **Comer two-current** (`96f0459`). The reference radial enthalpy lies between −2.22e-2 and −1.34e-6. The support contributes 0 and the fluids contribute a positive amount. The normal-acceleration jumps are 0.01302 at the inner boundary and 0.01311 at the outer (`SR/COMER_TWO_CURRENT_EVOLUTION_ROUND.md:284-299`). The report states that this failure holds "already at zero preload" (`:192-193`), yet 12 evolutions and a 1,024-cell refinement were run before recording it.
  2. **Vacuum support, elastic round** (`0e88247`/`1a4c988`). The time kinetic coefficient is K_i = e + p_i (`SR/VACUUM_SUPPORT_SELECTION_ROUNDS.md:215-218`). K_r ranges from −0.022232 to −1.34e-6 and is negative at all 2,049 radii, so 72 of 72 cases fail (`:258-276`). The construction cites Dubovsky–Grégoire–Nicolis–Rattazzi (hep-th/0512260) at `:186`, a paper whose main result is that NEC violation in such media implies ghosts or instability.
  3. **Planar vacuum** (`1edb374`). E + P⊥ = 0 in the angular channel, while the rail needs ρ + p⊥ < 0 at 1,162 radii (`SR/RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md:253-260`).
  4. **Condensate** (`7512231`, `868b938`). The material has ρ + p_r = 2(K + D) ≥ 0 (`SR/SCREENED_SCALAR_CONDENSATE.md:42`; `SR/SEMICLASSICAL_JOINT_INVESTIGATION.md:92-95`).
  5. **Confined fermions** (`56aa116`). None of the 74, 302 or 1,222 multiplets helps. Filling every multiplet gives −0.0045, −0.070 and −1.10, against a required +2.0 (`SR/CONFINED_FERMION_EVALUATION.md:154-165`).
  6. **Cavity mirrors** (`92b997b`). The net contribution at g = 10 is −0.2015 (`SR/NARROW_CURVED_CAVITY_EVALUATION.md:143-148`).
  7. **Magnetic bends** (`f4227ff`). ρ_B + p_r,B = B²(1 − t_r²)/e² ≥ 0 (`SR/SHORT_MAGNETIC_CIRCUIT_EVALUATION.md:57`).
  8. **General gate** (`aa7408f`). H_rem ≥ 0 is stated as a general gate (`SR/COUPLED_REORIENTATION_INVESTIGATION.md:197-203`).
- **Detected by:** A short analytic sign argument inside each report.
- **Tool available earlier?** Yes, from the start of the block. The LE classification (Sep 8) plus the convex-cone property of NEC give it immediately: a sum of NEC-satisfying tensors satisfies NEC. The integrated opening identity (R′/A)′ = −4π(R/A)(ρ + p_r) first appears only at `b040b9b` (Sep 9 15:13; `SR/SEMICLASSICAL_JOINT_INVESTIGATION.md:77-100`).
- **Counterfactual:** A block-level "null budget" ledger at the outset would have turned each family into one question: does its NEC-violating part exceed its own positive supports and the O(1) opening demand? Families 1, 2, 5, 6 and 7 could each have been scored on paper first.
- **Cost:** Partly justified, because several rounds had other goals, such as dynamics or kinetic positivity. The repeated sign closures still recur across about 8 rounds, roughly 20 commits.
- **Candidate lesson:** The NEC deficit is a budget that only the exotic sector can pay. Every ordinary component, including the holders, mirrors, fields and confinement that the exotic sector needs, adds to the bill. Score candidates by their net weighted null contribution, their own supports included, before anything else.
- **Generality:** A truism once stated, and general to all exotic-matter metric engineering. The operational point, counting the exotic sector's own supports, is the non-trivial part.
- **Recurrence in block:** About 8 occurrences.

## Incident 3: Casimir cells with ordinary holders are net positive: known literature bound, then re-derived three times

- **Date / commits:** `a91c04d`/`5cbbbf1` Sep 8 21:34, then `8987ffa`/`8d1bb32` 22:05–22:12, `26728fa`/`1edb374` Sep 9 08:26–08:36, and `ebe80b0` 17:51.
- **What happened:** At 21:34 the vacuum round already applied Costa–Matsas (arXiv:2112.08881). A dominant-energy-condition (DEC) holder carries at least 3C of energy, so a complete cell has at least 2C per cavity volume (`SR/VACUUM_SUPPORT_SELECTION_ROUNDS.md:86-92`, `:158-164`). The same conclusion was then reached three more times:
  - The moving-boundary round ran 16 coupled evolutions and derived the exact bound H − E_g[0] ≥ 2σ + M_H + ½K(a − a_nat)² > 0. Its minimum complete energy was 8.498, while the rail needs negative energy at 1,651 of 2,049 radii (`SR/QUANTUM_MOVING_BOUNDARY_ATTEMPT.md:259-276`).
  - The matched-mass round derived E_held ≥ M₁ + M₂ + (af/e − 1)e > 0 with 1 < af/e < 3. Over 154 optical pairs, the holding/binding ratio ran from 1.0014 to 2.9994 (`SR/RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md:99-121`, `:139-146`).
  - The reorientation round found a "mechanical realization gate" failure with a maximum local deficit of 0.139277 (`SR/COUPLED_REORIENTATION_INVESTIGATION.md:137-151`).
- **Detected by:** Literature (Costa–Matsas) plus the DEC, then re-derived analytically.
- **Tool available earlier?** Yes. It was cited at the first occurrence, and the Casimir-energy-with-plates accounting is standard.
- **Counterfactual:** The rail verdict of the moving-boundary and matched-mass rounds was fixed at 21:34. Their genuinely new content was narrower: negative gap enthalpy coexists with positive primitive kinetic terms, and regulator and planar-angular facts. The later SOURCE_SCALING_TEST (Sep 25, `d128547`) generalizes the point. At every gap, the thinnest electron mirror carries about 10⁷ times the deficit it bounds (`SR/SOURCE_SCALING_TEST.md:24-29`).
- **Cost:** About 5 commits and 2 reports whose rail-level conclusion was already known. Moderate.
- **Candidate lesson:** Static Casimir negative energy cannot be net-negative once the structure that holds the plates apart is counted under the dominant energy condition. Treat "complete cell energy ≥ 0" as a prior gate for any Casimir-based source.
- **Generality:** General, with a textbook or literature basis. It applies to all static Casimir wall and cavity proposals.
- **Recurrence in block:** 4, plus the cavity-mirror variant in Incident 11, so 5.

## Incident 4: Idealized boundaries and joins give regulator-dependent or divergent local quantum stress

- **Date / commits:** (a) `8d1bb32`, Sep 8 22:12, cutoff dependence. (b) `1069413` through `d2a7da6`, Sep 9 09:00–09:37, ideal-sheet singularity. (c) `b040588`, Sep 9 14:31, curvature-step divergence.
- **What happened:**
  - **(a) Gaussian walls, free-subtracted stress.** Interaction energy and force converge, changing by 2.1 to 3.1%, but local densities do not. The one-wall dressing runs 5.10, 5.94, 7.18 at cutoff 8 and 11.08, 13.77 at cutoff 12. The center energy changes sign, from −0.1968 to +0.0538 (`SR/QUANTUM_MOVING_BOUNDARY_ATTEMPT.md:225-246`). The follow-up identified the missing overlap counterterm, −(log Λ/16π²)∫V₁V₂dz, with coefficient about −4.10e-5 (`SR/RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md:184-201`).
  - **(b) Ideal delta sheets.** The curved placement search used 159,705 radial nodes, 129 harmonics, 192 frequencies and about 536 s over 11 comparisons (`SR/CURVED_QUANTUM_BOUNDARY_SEARCH.md:169-172`, `:221-224`). The closure report then found C(d) ~ λ/(48π²d³) near the sheet. At coupling 8 and d = 1e-6 the exact pressure is 0.999996 times this asymptote. The search stops there (`SR/SPHERICAL_BOUNDARY_MATERIAL_CLOSURE.md:104-141`, `:149-156`).
  - **(c) Classical C¹ join.** The join (continuous metric and extrinsic curvature) has a curvature step with D_R = −0.00151861 and D_A = −0.00125080. This produces a one-sided d⁻² vacuum energy of η·(+3.59e-11, 0, −3.66e-11)/d², against a finite required −1.208e-4 (`SR/CONDENSATE_SUPPLIED_QUANTUM_STRESS.md:54-112`).
- **Detected by:** (a) the registered cutoff comparison, which was good practice. (b) and (c) local asymptotic analysis.
- **Tool available earlier?** Yes for all three. Deutsch–Candelas (1979) boundary divergences, Graham et al. (hep-th/0309130) and Milton et al. (1401.0784) are all cited in-block. Graham was cited at `1edb374`, 08:36, before the curved sheet search began at 09:00 (`SR/RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md:204-205`). The Fosco–Giraldo–Mazzitelli mirror-mass cutoff dependence is cited at `SR/QUANTUM_MOVING_BOUNDARY_ATTEMPT.md:124-126`.
- **Counterfactual:** Start pointwise source-closure work with resolved, finite-thickness material and C²/smooth joins, and use ideal sheets only for off-sheet placement. The placement result was still useful: the enclosing sheet gives both null signs at 37 of 37 witnesses (`SR/CURVED_QUANTUM_BOUNDARY_SEARCH.md:120-125`).
- **Cost:** About 7 commits across three episodes. The ideal-sheet closure and the classical-join background were each abandoned.
- **Candidate lesson:** ⟨T_ab⟩ is only as regular as the background and boundaries. Delta mirrors give a d⁻³ divergence, curvature steps give d⁻², and unrenormalized regulated walls give cutoff-dependent densities. Israel (C¹) matching is sufficient classically but insufficient semiclassically. Require renormalized stress on smooth (C² or better) backgrounds before inserting it into the Einstein equation.
- **Generality:** General and textbook for any semiclassical source construction.
- **Recurrence in block:** 3.

## Incident 5: The junction forces a compressed shell, which buckles; a three-step patch chain follows

- **Date / commits:** The requirement is visible at `d2a7da6` (09:37). It is detected at `361d406` (10:15). Patches follow at `3c1431e`/`2ef33bc` (10:41–10:53) and `c04cc31`/`cdde39c` (11:30–11:41).
- **What happened:** The enclosing R = 6.8 junction requires positive tangential surface pressure. At M = 1.5, σ = 0.002560 and P = +0.000447 (`SR/SPHERICAL_BOUNDARY_MATERIAL_CLOSURE.md:69-83`), and the report already remarks that "the required compression selects a different surface constitutive response" (`:80-83`). A trapped-fermion wall was then built to supply the compression. The leading extrinsic equation gives ω² = −(P/Σ)k², with −P/Σ = −0.1744, ω² = −0.5884 and an e-folding time of 1.30. Stiffness is negative in all 1,029 admissible rows, and P > 0 is proved for the whole branch (`SR/SMOOTH_QUANTUM_MATERIAL_ATTEMPT.md:149-153`, `:215-264`). Two patches followed:
  - **Screening cloud.** The cloud adds bending, but the benefit saturates at f(q) = q²/(q² + 3q + 3) < 1. The analytic ceiling is B_max = (2R − b)/(3b) = 2.257, which needs a/R ≥ 0.2999 and so lies outside the thin-cloud regime. All 1,040 cases are negative (`SR/SCREENED_CHARGED_WALL_RESPONSE.md:155-181`, `:227-236`).
  - **Gravitating atmosphere.** This makes the wall tensile (P = −1.356e-4), but relaxation of the exterior cloud exceeds the wall tension by at least 4.086×, negative in 37 of 37 cases. The confinement scale also pushes the collective Yukawa loop measure to 1.5 to 27 (`SR/GRAVITATING_SCREENING_ATMOSPHERE.md:124-143`, `:231-264`, `:292-297`).
- **Detected by:** The membrane and extrinsic-curvature perturbation equation. The report cites Emparan et al. 0910.1601, eqs. 8.6–8.11, and Mourão et al. 2409.10602, eq. 56.
- **Tool available earlier?** Yes. Compressed membranes buckling is textbook, and Israel thin-shell dynamics plus Lobo–Crawford were already cited at `d2a7da6` (`SR/SPHERICAL_BOUNDARY_MATERIAL_CLOSURE.md:52-53`).
- **Counterfactual:** Checking the shape-stability sign at `d2a7da6` would have caught this before building the smooth wall. The subsequent screening and atmosphere patches each also ended on analytic bounds that were cheap to derive first.
- **Cost:** About 6 commits, 3 reports and roughly 2 hours.
- **Candidate lesson:** Read the sign of the surface stress the Israel junction demands before choosing a shell material. A thin shell under tangential compression has ω² ∝ −P k² and needs an independently counted restoring (bending or bulk) response. Patches that add restoring response carry their own counted loads and saturate.
- **Generality:** General to thin-shell source constructions, including wormhole and gravastar shells. Textbook physics.
- **Recurrence in block:** 3, one shape gate per construction (smooth wall, screened wall, atmosphere).

## Incident 6: An exterior-first shooting blow-up was reported as a physical obstruction; the joint BVP removed it

- **Date / commits:** `d7e6cdd`/`7512231`, Sep 9 12:23–12:36, then `6fa75d7`/`b4bd0a9` at 12:47–12:56, then `4188ad3` at 14:05.
- **What happened:** Integrating the condensate inward from exterior data produces a pole near areal radius 4.2925. The limit estimates are 4.291666, 4.292530 and 4.292531. The singularity has the asymptote h ≈ √(2/μ)/(Bv(x* − x)), and the measured |u|/h of 0.801764 matches the predicted 0.80178 (`SR/SCREENED_SCALAR_CONDENSATE.md:156-187`). Robustness checks all reproduced it: 16 checks (two tolerances, two geometries, thresholds from 10 to 1,000, and the DOP853 and Radau integrators) plus a 9-point boundary neighborhood (`:187`). The report headline states that the result is "failing the regular stationary material continuation" (`:3`). The joint synthesis then noticed that the fixed p_r,R = −0.125 had forced K + D = 0.127 at the join (`SR/CONDENSATE_JOINT_SELECTION_DIRECTION.md:59-72`). A global boundary-value problem then found two regular branches (15 starts, 3 converged, 2 continued to the full metric). The preferred branch has p_r,R = −0.2436 and is potential-dominated with V = 0.25 (`SR/CONDENSATE_JOINT_CONTINUATION.md:53-85`). The exterior-first candidate also had ω/A₀ ≈ 1.28, above √μ = 1.183, so it failed far-end localization as well (`:40`).
- **Detected by:** Synthesis of boundary-condition counting, followed by the joint BVP.
- **Tool available earlier?** Yes. Finite-distance movable singularities of h″ ∼ c h³ under one-sided integration are textbook ODE behavior, and the soliton literature cited (Ogawa–Ishihara) uses global matching.
- **Counterfactual:** Formulate as a global BVP from the outset. The 16 robustness checks tested numerical stability of a formulation artifact.
- **Cost:** About 3 commits and roughly 1.5 hours. The superseded "obstruction" headline remains in the report; only a forward link was appended (`SR/SCREENED_SCALAR_CONDENSATE.md:199`).
- **Candidate lesson:** A finite-radius blow-up in one-sided integration of a nonlinear field equation is the generic signature of mis-specified boundary data. It is not a no-go result. Physical exclusion claims need a global boundary-value formulation, or an analytic argument, with all asymptotic and regularity conditions imposed.
- **Generality:** General numerical-method lesson for soliton, boson-star and wormhole matter matching.
- **Recurrence in block:** 1.

## Incident 7: Magnitude deferred behind sign-only screening; first normalized comparison is short by 10⁵ to 10⁸, and the implied rail is Planck-scale

- **Date / commits:** Sign-only work ran from `a91c04d` (Sep 8 21:34) through `d2a7da6` (09:37). The first magnitude number came at `b040588` (Sep 9 14:31), and the absolute deficit at `b040b9b`/`cf87a89` (15:13–15:36).
- **What happened:** Unit conversion was deferred explicitly. One report says "This comparison uses signs, independently of any conversion between the cavity units and the rail's curvature scale" (`SR/QUANTUM_MOVING_BOUNDARY_ATTEMPT.md:275-276`). Another says "relative quantum strength … is N ℓ_P²/L² … the sign comparison has no fitted strength parameter" (`SR/CURVED_QUANTUM_BOUNDARY_SEARCH.md:157-162`). The first magnitude results were:
  - The smooth optical response supplies 6.63e-9 to 8.11e-7 of the required radial magnitude (`SR/CONDENSATE_SUPPLIED_QUANTUM_STRESS.md:3`, `:34-38`).
  - The absolute renormalized vacuum supplies 5.01e-6 to 5.38e-6 of B_opening = 2.1766. The required-to-available ratio is 185,950 to 213,708, and the signed quantum balance opposes opening (`SR/SEMICLASSICAL_JOINT_INVESTIGATION.md:102-121`).

  η = Għ/L² was an output of material matching: 1.0456e-7 for the atmosphere (`SR/GRAVITATING_SCREENING_ATMOSPHERE.md:139`), 6.09e-6 for the condensate exterior (`SR/SCREENED_SCALAR_CONDENSATE.md:136`) and 2.41e-5 for the joint branch. By my arithmetic, η = 2.41e-5 means L = ℓ_P/√η ≈ 204 ℓ_P ≈ 3.3e-33 m. The record notes R₀/√η = 415.22 Planck lengths only in passing (`SR/LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md:232`). The deficit therefore exists even for a rail a few hundred Planck lengths across. Scaling roughly by η, a one-metre rail would be short by a further factor of about 10⁶⁵ (my extrapolation).
- **Detected by:** An absolute renormalized mode sum plus the integrated opening identity.
- **Tool available earlier?** Yes. The ℓ_P²/L² scaling is dimensional analysis and was written down at 09:36. Ford–Roman quantum inequalities (1996) and Pfenning–Ford for warp drives are standard. The repo deferred "quantum inequality / ANEC-style endpoint cost: not shown" in May (`SR/STAGE2_ENDPOINT_JUNCTION_SOURCE_MILESTONE.md:274`; `SR/STAGE2_AFFINE_REPARAM_SNEC_AUDIT.md:158-162`). The explicit scaling test arrived only on Sep 25 (`d128547`, `SR/SOURCE_SCALING_TEST.md:14-29`). It finds N ≥ Q(L/ℓ_P)² fields: about 560 at the recorded normalization and 5 × 10⁶⁷ at 1 m.
- **Counterfactual:** A cheap scaling estimate on Sep 8 evening would have closed or re-scoped the whole quantum-boundary, wall, condensate and semiclassical chain to "Planck-scale or large-N only". That estimate compares η times a loop factor of about 10⁻³ to 10⁻⁴ per field against an O(1) opening demand.
- **Cost:** The largest cost in the block: about 30 commits and 18 reports over roughly 24 hours, from Sep 8 21:34 to Sep 9 20:23.
- **Candidate lesson:** For any semiclassical source, compute the physically normalized magnitude first: (ℓ_P/L)² × loop factor × species count, against the geometric demand at the intended physical size. Only then work on signs, placement, regularity and stability. Sign agreement is necessary and carries no weight without magnitude.
- **Generality:** General and textbook (Ford–Roman, Pfenning–Ford, Visser). It applies to every exotic-matter metric-engineering proposal.
- **Recurrence in block:** About 5 magnitude gaps: optical (≤ 1e-6), absolute (5e-6), longitudinal (≤ 4.17% at c ≈ 65,000; 2.13e-7 at c = 1), cavity (g* ≈ 17,000), magnetic (N_f e²/16π² ≈ 18 against 0.1).

## Incident 8: Bulk tension assigned to the quantum sector, where the established architecture had a separate backbone

- **Date / commits:** The allocation happened implicitly from `4188ad3` to `cf87a89` (Sep 9 14:05–15:36). It was detected at `ada8661` (16:18) and restated at `0e66f43` (16:47).
- **What happened:** At the throat the demand is (ρ, p_r, p_t) = (9.564e-3, −9.565e-3, 3.26e-5). The relaxed condensate carries 0.612% of the tension, and the "quantum remainder" is assigned 99.388% (`SR/COUPLED_SOURCE_ROLE_AUDIT.md:7-12`, `:58-63`). The null part is tiny by comparison: ρ + p_r = −1.364e-6, or about 1.4e-4 of ρ (`SR/LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md:36-43`). The cross-reference records the self-correction: "The recent condensate-plus-neutral-scalar calculation restricted the allocation too far" (`SR/RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md:50-52`). In the reallocation, a backbone carries 95% of the throat tension and the ideal quantum radial weight becomes 3.41e-7 (`SR/COUPLED_REORIENTATION_INVESTIGATION.md:72-86`).
- **Detected by:** A role audit against the May component ledger (`SR/STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md`).
- **Tool available earlier?** Yes. The May architecture (S₀ backbone and others) and the Morris–Thorne tension/density/"exoticity" decomposition were both available.
- **Counterfactual:** Allocating tension explicitly before the semiclassical solve would have framed the quantum requirement as the null deficit only. The opening-deficit verdict does not change, because it is independent of the tension allocation (`SR/COUPLED_SOURCE_ROLE_AUDIT.md:65-68`).
- **Cost:** Mostly conceptual and framing, plus 3 or 4 commits of reallocation (`ada8661`, `0e66f43`, `ebe80b0`, `aa7408f`).
- **Candidate lesson:** Split the demand into bulk tension, ρ ≈ −p_r, which is NEC-neutral and can be carried by ordinary strings, flux or potential energy, and the signed null deficit ρ + p_r < 0, which is exotic. Allocate each to components before solving fields. Only the second requires the exotic sector.
- **Generality:** General to wormhole and warp source design (Morris–Thorne exoticity). A standard textbook decomposition.
- **Recurrence in block:** 1 explicit; implicit in the single-field semiclassical framing.

## Incident 9: The surrogate's exterior is an Ellis-type tail, so the NEC demand extends along the whole route

- **Date / commits:** `ada8661`, Sep 9 16:18. The underlying metric form is noted in `a1a8a65`.
- **What happened:** The static background's positive-side far tail is R = √(x² + 1.75²) with constant lapse (`SR/CURVED_QUANTUM_BOUNDARY_SEARCH.md:35-37`), and "That tail itself requires negative radial null stress" (`SR/COUPLED_SOURCE_ROLE_AUDIT.md:180-184`). Of the negative radial-null balance B₋ = 2.325, 96.69% lies outside |x| ≤ 2: 67.92% in 2 < |x| < 3 and 28.77% in 3 ≤ |x| ≤ 40 (`:160-176`). The metric's angular function contains ℓ² + R_th² (`SR/ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md:121-124`), which is the Ellis/Morris–Thorne throat form. The morning's source-localization work was effectively trying to terminate an ultrastatic wormhole tail. That work included the enclosing sheet at R = 6.8, the Schwarzschild exterior junction and the atmosphere.
- **Detected by:** Band-integrated null balance in the role audit.
- **Tool available earlier?** Yes, from textbooks. The Ellis (1973) and Morris–Thorne (1988) ultrastatic throat has ρ + p_r = −b²/(4π r⁴) < 0 at every radius. The repo later characterized "the earlier wormhole" on Sep 24 (`86a557f`, `db79203`).
- **Counterfactual:** One analytic Einstein-tensor evaluation of the chosen angular metric function at design time shows the route-long NEC demand.
- **Cost:** It shaped the whole static source program. The redesign came Sep 23–24, outside the block.
- **Candidate lesson:** Before sourcing, evaluate the null-energy demand of the chosen asymptotic and exterior geometry analytically. A throat-like areal function √(ℓ² + b²) with flat lapse demands exotic stress everywhere, so local sources cannot close it.
- **Generality:** General for wormhole-like or two-mouth spatial geometries. Textbook.
- **Recurrence in block:** 1 explicit.

## Incident 10: The zero-shift static surrogate is Type I by construction and cannot represent the Type IV layer; the first active-metric test finds a new shift-routing obstruction

- **Date / commits:** The complete static background dates from `1069413` (Sep 9 09:00; `SR/ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md:147-152`). The correction is `a1a8a65` (20:46). The active test is `bad59e2`/`8492f8e` (21:10–21:21).
- **What happened (fine grain):**
  - Static holding controls are diagonal in the static frame (j_r = 0). "Every holding control is Type I" (`SR/COMER_ANDERSSON_SPHERICAL_STARTUP_ATTEMPT.md:312`), and the disclosure text (diff in `734156c`) states "At j_r = 0 the diagonal tensor is Type I … A radial block with H² < 4j_r² is Type IV". The Type IV layer found on Sep 8 lives in the shift-generated flux, so the 37 static-background commits addressed a different, Type I problem.
  - The scope review names this "The scope error was promoting these conditional source results into necessary active-rail selection gates without demonstrating the state equivalence" (`SR/ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md:162-165`). It adds that local scope qualifications were already present (`:163-165`), and it withdraws the inferences (`:186-192`).
  - About 35 minutes of active-metric work produced two results. First, all 9 timing schedules retain 6 or 7 Type IV witnesses; the principal reset deficit falls from 0.03869 to 0.01134 while another rises from 0.00405 to 0.01322 (`SR/ACTIVE_ENDPOINT_TRANSFER_INVESTIGATION.md:127-135`). Second, a transfer-routing obstruction: the characteristic speeds v± = −β ± α/B carry the required reservoir radiation through the protected packet, with a required in-packet density ≥ 1.0754 (direct-metric value 1.07544665) (`:61-67`, `:153-192`).
- **Detected by:** An architecture and scope review against the pre-September disclosure `d44e923`. It was probably prompted by the user, but the record does not quote the user.
- **Tool available earlier?** Yes. The Hawking–Ellis classification (static diagonal tensor ⇒ Type I) and the ADM form K_ij ∋ D_(iβ_j) (`SR/ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md:92-100`) are both textbook.
- **Counterfactual:** At `1069413`, the question "which obstruction classes can this surrogate represent?" would have shown that it cannot test Type IV or shift-dependent routing.
- **Cost:** 37 commits in the block. Continuation to Sep 17 is documented elsewhere (for example `SR/C1_FINITE_MODULE_PAIR_SCREEN.md:25`, "static, zero-shift surrogate of the archived phase-0.745").
- **Candidate lesson:** A surrogate that zeroes the shift or flux removes the momentum-density channel that makes a stress Type IV, together with the transport routes set by the shift. Before adopting a simplified background, list the obstruction classes and constraints it can and cannot represent.
- **Generality:** General to shift-driven (warp or Natário-type) metrics. Textbook.
- **Recurrence in block:** 1. See counter-evidence C3.

## Incident 11: Useful and parasitic terms share the same size scaling, so shrinking or reshaping cannot help; analytic bounds predicted the scans

- **Date / commits:** `e3c17ae` (15:58), `aa7408f` (18:02), `e2dc588`/`92b997b` (20:05–20:13), `283a91e`/`f4227ff` (20:13–20:23).
- **What happened:**
  - **Long conformal loops.** A helpful sign needs L_opt < 2π/(A₀√a″₀) = 3.266, but a loop spanning [−2, 2] already has L_opt = 6.30 and the wrong sign (`SR/LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md:180-206`). With clock freedom, the best case supplies ≤ 4.17% at c ≈ 65,000; 78 of 88 cases are excluded (`SR/COUPLED_REORIENTATION_INVESTIGATION.md:242-258`).
  - **Cavities.** The interaction and the mirror gradient load both scale as η/a³. The crossing coupling is g* = 17,385 planar (11,467 for wider profiles) and 17,438 to 24,191 curved, against registered g ≤ 10 (`SR/NARROW_CURVED_CAVITY_EVALUATION.md:80-87`, `:119-153`). A sixteenfold gap reduction gains only a factor of 1.67 (`:156-162`).
  - **Magnetic loops.** For a flat circle, B_Q/|B_B| = P/(B r_b²) with B r_b² ≥ 2qγ², which requires P = N_f e²/16π² > 18. The curved minimum is 17.971, against a perturbative limit of 0.1, and 0 of 23,760 cases pass under both field prescriptions (`SR/SHORT_MAGNETIC_CIRCUIT_EVALUATION.md:143-196`).
- **Detected by:** In-report analytic scaling, confirmed by scans that took 0.16 to 107 s.
- **Tool available earlier?** Yes, dimensional analysis. The Sep 25 scaling test later generalizes the cavity case (`SR/SOURCE_SCALING_TEST.md:24-29`).
- **Counterfactual:** Deriving the dimensionless threshold first would have ended both families on paper.
- **Cost:** Low in compute; 4 to 6 commits and 3 reports.
- **Candidate lesson:** When the helpful quantum term and the confinement or holding term share the same length scaling, the verdict is a dimensionless coupling threshold. Compute that threshold before any geometric tuning; if it is non-perturbative, stop.
- **Generality:** A general rule of thumb for Casimir, flux-tube and mirror sources.
- **Recurrence in block:** 3 or 4, including the archived geometry transfers in Incident 12.

## Incident 12: A redundant recommendation was corrected, and a re-screen of archived geometry was predictably null

- **Date / commits:** `aa7408f` (18:02) wrote "Its operational and field constraints remain to be selected before a further joint field solve". `83fe023` (18:17) replaced it (see `git show 83fe023` on `SR/COUPLED_REORIENTATION_INVESTIGATION.md`). The re-screen followed in `d9b93df`/`fe99e3f` (18:35–18:49).
- **What happened:** The new history report states: "The previous recommendation to select the operational constraints before proceeding repeated work already established in the design record" (`SR/GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:17-20`). Thirteen archived controls were then transferred. The best change is +0.315% (core gain 0.06) and radius 2.05 gives −8.45%. No exclusion is removed; 1,133 of 1,287 cases are excluded, including all 819 through k/R₀² = 0.03 (`SR/ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:5-13`, `:132-162`). The report notes that this reproduces "the historical lesson that a smaller local peak can accompany a larger counted support requirement": radius 2.05 raises negative-density demand by 15.8% and angular pressure by 27.4% (`:185-194`).
- **Detected by:** Probably the user, given the 15-minute reversal and the "repeated work" wording; the record does not quote the user. The archive supplied the rest.
- **Tool available earlier?** Yes. The May design record, and an effect-size check: transfers of about 10% cannot close a 24× to 200× gap.
- **Counterfactual:** Consult the project's own prior sweeps before recommending new design-space selection, and compare the expected effect size with the gap before re-screening.
- **Cost:** 3 commits, about 50 minutes, 163 s of compute. No decision changed.
- **Candidate lesson:** Before proposing new exploration, search your own project archive. Before re-screening variants, compare their plausible effect size with the gap.
- **Generality:** A research-process near-truism, general.
- **Recurrence in block:** 1 correction, plus 1 "historical lesson reproduced".

## Incident 13: The technical disclosure was used as a running log for 3.5 hours, then stripped

- **Date / commits:** Additions in `921e560` (16:59; +179/−51 lines of .tex), `aa7408f` (+10), `fe99e3f` (+4), `56aa116` (+2) and `f4227ff` (+4). Removal in `734156c` (20:31; −41/+27).
- **What happened:** Trial-specific results were written into the disclosure and its PDF. These included 0.612%, 186,000–204,000, 4.17%, 0.315%, the 74/302/1,222 multiplets, 17,438–24,191 and 23,760 cases. `734156c` removed them and replaced them with requirement-style statements (`git show 734156c`). The PDF was rebuilt 6 times; the removal took it from 425,968 to 416,114 bytes.
- **Detected by:** Probably a user correction; the record does not quote the user. The rule "NEVER use the technical disclosure as a running log" was codified in AGENTS.md on Sep 16 (`e7a9951`). The user's memory file `disclosure-updates-need-explicit-go-ahead` (Sep 25) records the same failure recurring.
- **Tool available earlier?** A project convention; it is unclear whether it was written down by Sep 9.
- **Cost:** 6 disclosure and PDF commits.
- **Candidate lesson:** Keep the canonical design specification separate from the investigation log. Enter only locked design elements, and only on explicit request.
- **Generality:** A research-process lesson, general to any project with a canonical spec. It is not physics.
- **Recurrence:** At least 2, the block plus Sep 25 per memory.

## Incident 14: The rail's clock-enhancement lapse hill (A up to about 108) had two consequences flagged late: no free binding and passenger aging

- **Date / commits:** The numbers are present throughout Sep 9. They appear explicitly at `ada8661` (A₀ = 69.34), `fe99e3f` (throat lapse 81.66 to 88.47) and `bce06d7` (maximum lapse 108.07).
- **What happened:**
  - **(a) No free binding.** The restart shortlist reads the cache: minimum lapse 1, maximum 108.071, and 1 at both ends. Weinbaum's eq. (111) requires an attractive lapse well for freely bound massive states, so fermions need material confinement (`SR/SOURCE_CONSTRUCTION_RESTART_SHORTLIST.md:70-77`). The confined-fermion build that followed found that every occupied multiplet opposes opening (Incident 2). The same commit also qualified the Kain EDM benchmarks, which had been cited three hours earlier (`e3c17ae`) as comparable "hundreds of Planck lengths" examples. The 2026 critique (accepted in PRD on 31 Aug, so available before the block) was used to weaken "the earlier complete-source examples" (`SR/SOURCE_CONSTRUCTION_RESTART_SHORTLIST.md:58-68`; `SR/LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md:230-247`).
  - **(b) Passenger aging.** With dτ = A dt for a payload comoving at the throat, a lapse of 69 to 108 means a static or comoving payload at the center ages about 70 to 110 times faster than exterior clocks. Nothing in the block interprets this. My inference, from `SR/COUPLED_SOURCE_ROLE_AUDIT.md:58`, `SR/ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:178-180` and the shortlist line above, is that it was invisible as a passenger issue. The user's later memory (Sep 25) records that a design aging its packet 55× was judged a transit failure. The static-to-service mapping of the lapse is not established in the block.
- **Detected by:** (a) a literature read, 3 hours after the benchmark was first cited. (b) Not detected in the block; detected later by the user.
- **Tool available earlier?** Yes for both: dτ = α dt and the lapse-well condition for bound states are elementary.
- **Cost:** (a) 3 commits (`bce06d7`, `b4fe60d`, `56aa116`), about 40 minutes, six runs of up to 204 s. (b) A goal-level issue left to the later redesign.
- **Candidate lesson:** Report payload-facing quantities (proper-time rate, tides, acceleration) with every metric iteration. A lapse enhancement at the payload is passenger aging, and it also removes gravitational binding for massive fields.
- **Generality:** General for crewed metric engineering.
- **Recurrence:** Lapse values appear in 4 or more reports in the block without payload interpretation.

## Incident 15: Checks that caught method errors early (good practice) and numerical hygiene

- **(a) Coarse-resolution Type IV artifacts.** In the Comer two-current round, 138 raw complex-pair (Type IV) curvature records occur only at coarse settings. At a fixed witness the discriminant runs −6.91e-9, −1.70e-9, −2.56e-10 over the three coarse resolutions, then +2.10e-10 at 1,024 cells, against a source value of 3.4e-10. All 36 finest witnesses are Type I (`SR/COMER_TWO_CURRENT_EVOLUTION_ROUND.md:244-270`, `:344-347`; `9a59e55`). *Lesson:* Hawking–Ellis classification near a vanishing discriminant is resolution-sensitive, so refine or attach error bars before declaring Type IV. This is directly relevant to the project's headline Type IV claim, which the LE reports did test for refinement stability.
- **(b) Truncated gradient expansion.** Extrapolating the quartic bending term beyond ka ~ 1 would have produced 72 false passes among the 420 hierarchy-valid cases; the full saturating response gives 0 (`SR/SCREENED_CHARGED_WALL_RESPONSE.md:234-236`; `3c1431e`/`2ef33bc`). *Lesson:* never extrapolate a long-wavelength stabilizer outside its validity. General.
- **(c) Precision loss at release.** The direct force quotient lost precision at the second release step, a = 0.9999970828, and was replaced by an analytic sine/sinc divided difference (`SR/QUANTUM_MOVING_BOUNDARY_ATTEMPT.md:137-141`, `:309-312`; `7a1aed0`, 2 minutes after `8987ffa`).
- **(d) CSV round-trip precision.** A default CSV float converter broke near-cancellation audits in the outer tail and near-horizon controls. The fix was exact round-trip reading (`SR/VACUUM_SUPPORT_SELECTION_ROUNDS.md:330-336`; `SR/SCREENED_CHARGED_WALL_RESPONSE.md:253-254`; `SR/RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md:294-295`). Recurs 3 times.
- **(e) Unresolved quadrature kept out of the verdict.** The reservoir initial-energy quadrature is unresolved (coarse about 162, finer about 39,023) and was correctly excluded from the verdict (`SR/ACTIVE_ENDPOINT_TRANSFER_INVESTIGATION.md:218-226`).
- **(f) Finite-domain effect.** An end-distance change from 48 to 96 moved the weak inner response by 1.84%, and was extended to 384–1,536 (`SR/CURVED_QUANTUM_BOUNDARY_SEARCH.md:184-187`).
- **(g) Renormalization-condition correction.** `b040b9b` corrected a renormalization claim: the text had said "the Higgs mass and quartic coupling retain their registered values", and it now says only the potential's first two derivatives vanish (`SR/SEMICLASSICAL_JOINT_INVESTIGATION.md:17`).
- **Cost:** Minutes each. These are items where checking helped.

---

## Counter-evidence (practices followed that did not help or misled)

- **C1. Robustness audits certified an artifact.** The condensate inward runaway passed 16 checks (two integrators, tolerances, thresholds, two geometries) and a 9-point neighborhood (`SR/SCREENED_SCALAR_CONDENSATE.md:187`). It was a formulation artifact that the joint BVP removed 90 minutes later (Incident 6). Independent verification tested numerical stability, not the formulation.
- **C2. Refinement ladders that did not change a decision.**
  - Semiclassical: 5.01e-6, then 5.27e-6, then 5.38e-6 of requirement across three stages. That was 28.04 minutes of mode runs plus a 1,948-line commit (`cf87a89`) against a deficit of 2×10⁵ (`SR/SEMICLASSICAL_JOINT_INVESTIGATION.md:108-121`, `:160`).
  - Confined fermions: 6 runs of up to 203.8 s, where the first run already showed 0 helpful multiplets (`SR/CONFINED_FERMION_EVALUATION.md:184-191`).
  - Magnetic field spreading: 2842.3 to 2837.9.
  - Cavity wider profiles: 17,385 to 11,467, still about 3 orders away.
  - Archived transfers: at most 0.315%.
  - The 16 moving-wall evolutions, whose rail verdict followed from an exact sign bound.
- **C3. Scope qualifications did not prevent scope creep.**
  - The scope review found that "Local scope qualifications were already present in several reports. The later recommendations exceeded them" (`SR/ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md:162-165`). An example of such a qualification: "The stationary snapshot omits the rail's time derivatives, so the result applies to this proposed equilibrium attachment" (`SR/SCREENED_SCALAR_CONDENSATE.md:195`).
  - The Sep 9 20:46 correction itself did not stick. On Sep 17 the same surrogate is used as "the static, zero-shift surrogate of the archived phase-0.745" (`SR/C1_FINITE_MODULE_PAIR_SCREEN.md:25`).
- **C4. Per-round pre-registration worked locally but did not bound the program.** Each round registered stopping rules and did stop; for example, "No additional source layer … after a failed test" (`SR/COMER_ANDERSSON_SPHERICAL_STARTUP_ATTEMPT.md:208-210`). Yet about 16 families were opened in about 25 hours without a program-level magnitude or normalization gate. That gate was codified only on Sep 17 in the source-feasibility workflow (`1e9ac1d`), which prioritizes "physically normalized component contributions".
- **C5. Append-only reports kept superseded headlines.** Block reports have essentially zero deletions in git numstat; updates are appended forward links. A reader who stops at the top still sees superseded claims, for example:
  - the condensate "failing … continuation" headline (`SR/SCREENED_SCALAR_CONDENSATE.md:3`);
  - the cutoff-dependent local stresses (`SR/QUANTUM_MOVING_BOUNDARY_ATTEMPT.md:183-191`).
- **C6. High-precision verification of irrelevant premises.** Several verifications reached machine precision while the premises went unchecked: the static surrogate, the magnitude, and the Ellis tail. Examples:
  - 504 eigensystems to 1e-16 (`SR/COMER_ANDERSSON_SPHERICAL_STARTUP_ATTEMPT.md:308-311`);
  - 147,528 action matrices (`SR/VACUUM_SUPPORT_SELECTION_ROUNDS.md:281-282`);
  - Gauss-law checks to 8e-13 (`SR/CONDENSATE_JOINT_CONTINUATION.md:107`).
- **C7. Positive controls on other geometries validated code, not relevance.** Two examples: Weinbaum's negative-ANEC example reproduced (111.88352 / −3.59047), and the AdS2 control ratio of exactly 4. The confined-fermion report states that this distinction was handled correctly (`SR/CONFINED_FERMION_EVALUATION.md:212-221`; `SR/COUPLED_REORIENTATION_INVESTIGATION.md:304-307`). Neutral rather than misleading.
- **C8. The update-PDF-with-every-disclosure-edit rule amplified churn.** Six disclosure PDF rebuilds for content later removed (Incident 13).

## Cross-cutting summary

The dominant lesson, the costliest and most general, is Incident 7: gate on physically normalized magnitude first. Incidents 2, 3 and 11 express the same budget logic in sign and scaling form: every ordinary support adds to the null deficit, and when helpful and parasitic terms share their scaling, geometry cannot rescue the design. Incidents 9 and 10 are geometry- and surrogate-level premises that textbook checks, the Ellis NEC profile and Hawking–Ellis Type I for diagonal tensors, would have exposed at the moment the background was adopted. Incidents 4, 5 and 6 are method errors with textbook detectors: boundary divergences, compressed-shell buckling, and one-sided shooting blow-up.
